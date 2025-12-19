import streamlit as st
import pandas as pd
from io import BytesIO

# =========================
# CONFIG
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
3. Definir tipo (Producción / Levante)  
4. Definir lotes y montos  
5. Ingresar participación y faltas  
6. Descargar archivo final  
""")

# =========================
# REGLAS POR CARGO
# =========================
REGLAS_CARGO = {
    "GALPONERO": 1.00,
    "AYUDANTE GALPONERO": 0.125,
    "VOLANTE DESCANSERO": 0.125,
    "VOLANTE ALIMENTO": 0.125,
    "BIOSEGURIDAD": 0.0625,
    "GUARDIANES": 0.0625,
    "CAPORAL": 0.125,
    "SUPERVISOR": 1.00,
    "MANTENIMIENTO": 0.0,
    "GRADING": 0.08,
    "VACUNADORES": 0.07
}

# =========================
# CARGA ARCHIVOS
# =========================
archivo_dni = st.file_uploader("📄 Excel con lista de DNI", type=["xlsx"])
archivo_base = st.file_uploader("📊 Base de trabajadores", type=["xlsx"])

if archivo_dni and archivo_base:

    df_dni = pd.read_excel(archivo_dni, dtype=str)
    df_base = pd.read_excel(archivo_base, dtype=str)

    df_dni.columns = df_dni.columns.str.strip().str.upper()
    df_base.columns = df_base.columns.str.strip().str.upper()

    if "DNI" not in df_dni.columns:
        st.error("❌ El archivo de DNIs debe tener columna DNI")
        st.stop()

    if not {"DNI", "NOMBRE COMPLETO", "CARGO"}.issubset(df_base.columns):
        st.error("❌ La base debe tener: DNI, NOMBRE COMPLETO y CARGO")
        st.stop()

    def limpiar_dni(s):
        return (
            s.astype(str)
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
    # TIPO DE PROCESO
    # =========================
    st.subheader("🏷️ Tipo de proceso")
    tipo = st.radio("Seleccione uno", ["PRODUCCIÓN", "LEVANTE"], horizontal=True)

    # =========================
    # LOTES
    # =========================
    st.subheader("🔢 Definir lotes")
    lotes_txt = st.text_input("Ejemplo: 211-212-213", value="211-212-213")
    lotes = [l.strip() for l in lotes_txt.split("-") if l.strip()]

    if not lotes:
        st.stop()

    # =========================
    # CONFIG POR LOTE
    # =========================
    st.subheader("🧬 Configuración por lote")

    config_lotes = {}
    cols = st.columns(len(lotes))

    for i, lote in enumerate(lotes):
        with cols[i]:
            genetica = st.text_input(f"Genética {lote}", value="ROSS")
            monto = st.number_input(f"Monto S/ {lote}", min_value=0.0, value=1000.0)
            config_lotes[lote] = {"genetica": genetica, "monto": monto}

    # =========================
    # COLUMNAS PARTICIPACIÓN
    # =========================
    for lote in lotes:
        df[f"%_{lote}"] = 0.0

    for lote in lotes:
        df[f"F_{lote}"] = 0

    st.subheader("✍️ Registro por trabajador y lote")
    df_edit = st.data_editor(df, use_container_width=True, num_rows="fixed")

    # =========================
    # CÁLCULO FINAL
    # =========================
    df_final = df_edit.copy()
    total_cols = []

    for lote in lotes:
        def calcular_pago(row):
            cargo = str(row["CARGO"]).upper()
            base_pct = REGLAS_CARGO.get(cargo, 0)
            monto = config_lotes[lote]["monto"]
            participacion = row[f"%_{lote}"] / 100
            faltas = row[f"F_{lote}"]

            pago = monto * participacion * base_pct
            pago = max(pago - (faltas * 5), 0)  # regla simple de descuento
            return round(pago, 2)

        df_final[f"PAGO_{lote}"] = df_final.apply(calcular_pago, axis=1)
        total_cols.append(f"PAGO_{lote}")

    df_final["TOTAL S/"] = df_final[total_cols].sum(axis=1)

    st.subheader("💰 Resultado final")
    st.dataframe(df_final, use_container_width=True)

    # =========================
    # EXPORT
    # =========================
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df_final.to_excel(writer, index=False)

    output.seek(0)

    st.download_button(
        "📥 Descargar archivo final",
        data=output,
        file_name="bono_reproductoras_final.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
