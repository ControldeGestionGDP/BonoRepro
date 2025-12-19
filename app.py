import streamlit as st
import pandas as pd
from io import BytesIO

# =========================
# CONFIGURACIÓN
# =========================
st.set_page_config(
    page_title="Bono Reproductoras GDP",
    layout="wide"
)

st.title("🐔 BONO REPRODUCTORAS GDP")

st.markdown("""
**Flujo**
1. Subir DNIs  
2. Subir base de trabajadores  
3. Definir lotes  
4. Configurar genética y monto  
5. Ingresar participación y faltas  
6. Descargar archivo final  
""")

DESCUENTO_FALTA = 50  # S/ por falta (editable)

# =========================
# CARGA DE ARCHIVOS
# =========================
archivo_dni = st.file_uploader("📄 Excel con lista de DNI", type=["xlsx"])
archivo_base = st.file_uploader("📊 Base de trabajadores", type=["xlsx"])

if archivo_dni and archivo_base:

    # =========================
    # LECTURA
    # =========================
    df_dni = pd.read_excel(archivo_dni, dtype=str)
    df_base = pd.read_excel(archivo_base, dtype=str)

    df_dni.columns = df_dni.columns.str.strip().str.upper()
    df_base.columns = df_base.columns.str.strip().str.upper()

    # =========================
    # VALIDACIONES
    # =========================
    if "DNI" not in df_dni.columns:
        st.error("❌ El archivo de DNIs debe tener columna DNI")
        st.stop()

    if not {"DNI", "NOMBRE COMPLETO", "CARGO"}.issubset(df_base.columns):
        st.error("❌ La base debe tener: DNI, NOMBRE COMPLETO y CARGO")
        st.stop()

    # =========================
    # LIMPIEZA DNI
    # =========================
    def limpiar_dni(serie):
        return (
            serie.astype(str)
            .str.replace("'", "", regex=False)
            .str.replace(".0", "", regex=False)
            .str.strip()
            .str.zfill(8)
        )

    df_dni["DNI"] = limpiar_dni(df_dni["DNI"])
    df_base["DNI"] = limpiar_dni(df_base["DNI"])

    df_base = df_base.drop_duplicates(subset="DNI")

    # =========================
    # CRUCE
    # =========================
    df = df_dni.merge(
        df_base[["DNI", "NOMBRE COMPLETO", "CARGO"]],
        on="DNI",
        how="left"
    )

    st.success("✅ Cruce realizado")

    # =========================
    # DEFINICIÓN DE LOTES
    # =========================
    st.subheader("🔢 Definir lotes")

    lotes_txt = st.text_input(
        "Ingrese los lotes separados por guion (ej: 211-212-213)",
        value="211-212-213"
    )

    lotes = [l.strip() for l in lotes_txt.split("-") if l.strip()]

    if len(lotes) == 0:
        st.warning("Ingrese al menos un lote")
        st.stop()

    # =========================
    # PANEL GENÉTICA Y MONTO
    # =========================
    st.subheader("🧬 Configuración por lote")

    config_lotes = {}
    cols = st.columns(len(lotes))

    for i, lote in enumerate(lotes):
        with cols[i]:
            genetica = st.text_input(f"Genética {lote}", "ROSS")
            monto = st.number_input(f"Monto S/ {lote}", min_value=0.0, value=1000.0)
            config_lotes[lote] = {
                "GENETICA": genetica,
                "MONTO": monto
            }

    # =========================
    # CREAR COLUMNAS DINÁMICAS
    # =========================
    for lote in lotes:
        df[f"%_{lote}"] = 0.0
        df[f"F_{lote}"] = 0
        df[f"PAGO_{lote}"] = 0.0

    st.subheader("✍️ Registro por trabajador y lote")

    df_editado = st.data_editor(
        df,
        use_container_width=True,
        num_rows="fixed"
    )

    # =========================
    # CÁLCULO DE PAGOS
    # =========================
    for lote in lotes:
        monto = config_lotes[lote]["MONTO"]

        df_editado[f"PAGO_{lote}"] = (
            df_editado[f"%_{lote}"].astype(float) / 100 * monto
            - df_editado[f"F_{lote}"].astype(float) * DESCUENTO_FALTA
        )

        df_editado[f"PAGO_{lote}"] = df_editado[f"PAGO_{lote}"].clip(lower=0)

    pago_cols = [f"PAGO_{lote}" for lote in lotes]
    df_editado["TOTAL S/"] = df_editado[pago_cols].sum(axis=1)

    st.subheader("💰 Resultado final")
    st.dataframe(df_editado, use_container_width=True)

    # =========================
    # EXPORTACIÓN
    # =========================
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df_editado.to_excel(writer, index=False, sheet_name="Detalle")
        pd.DataFrame(config_lotes).T.to_excel(writer, sheet_name="Configuracion_Lotes")

    output.seek(0)

    st.download_button(
        "📤 Descargar archivo final",
        data=output,
        file_name="bono_reproductoras_final.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
