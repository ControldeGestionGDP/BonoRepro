import streamlit as st
import pandas as pd
from io import BytesIO

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="Bono Reproductoras GDP", layout="wide")
st.title("🐔 BONO REPRODUCTORAS GDP")

# =========================
# TABLAS DE % POR CARGO
# =========================
REGLAS_PRODUCCION = {
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

REGLAS_LEVANTE = REGLAS_PRODUCCION.copy()  # hoy iguales, mañana ajustables

DESCUENTO_FALTA = 5  # S/ por falta

# =========================
# CARGA ARCHIVOS
# =========================
archivo_dni = st.file_uploader("📄 Excel con DNIs", type=["xlsx"])
archivo_base = st.file_uploader("📊 Base de trabajadores", type=["xlsx"])

if archivo_dni and archivo_base:

    df_dni = pd.read_excel(archivo_dni, dtype=str)
    df_base = pd.read_excel(archivo_base, dtype=str)

    df_dni.columns = df_dni.columns.str.strip().str.upper()
    df_base.columns = df_base.columns.str.strip().str.upper()

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

    df_base = df_base.drop_duplicates("DNI")

    df = df_dni.merge(
        df_base[["DNI", "NOMBRE COMPLETO", "CARGO"]],
        on="DNI",
        how="left"
    )

    st.success("✅ Cruce realizado")

    # =========================
    # TIPO
    # =========================
    tipo = st.radio("Tipo de proceso", ["PRODUCCIÓN", "LEVANTE"], horizontal=True)
    reglas = REGLAS_PRODUCCION if tipo == "PRODUCCIÓN" else REGLAS_LEVANTE

    # =========================
    # LOTES
    # =========================
    lotes_txt = st.text_input("Lotes (ej: 211-212-213)", "211-212-213")
    lotes = [l.strip() for l in lotes_txt.split("-") if l.strip()]

    config_lotes = {}
    st.subheader("🧬 Configuración por lote")
    cols = st.columns(len(lotes))

    for i, lote in enumerate(lotes):
        with cols[i]:
            genetica = st.text_input(f"Genética {lote}", "ROSS")
            monto = st.number_input(f"Monto S/ {lote}", min_value=0.0, value=1000.0)
            config_lotes[lote] = monto

    # =========================
    # COLUMNAS PARTICIPACIÓN Y FALTAS
    # =========================
    for lote in lotes:
        df[f"%_{lote}"] = 0.0
    for lote in lotes:
        df[f"F_{lote}"] = 0

    st.subheader("✍️ Registro por trabajador y lote")
    df_edit = st.data_editor(df, use_container_width=True, num_rows="fixed")

    # =========================
    # CÁLCULO DE PAGOS
    # =========================
    df_final = df_edit.copy()

    pagos = []
    for lote in lotes:

        def pago_lote(row):
            cargo = str(row["CARGO"]).upper()
            pct_cargo = reglas.get(cargo, 0)
            monto = config_lotes[lote]
            participacion = row[f"%_{lote}"] / 100
            faltas = row[f"F_{lote}"]

            pago = monto * participacion * pct_cargo
            pago -= faltas * DESCUENTO_FALTA
            return round(max(pago, 0), 2)

        df_final[f"PAGO_{lote}"] = df_final.apply(pago_lote, axis=1)
        pagos.append(f"PAGO_{lote}")

    df_final["TOTAL S/"] = df_final[pagos].sum(axis=1)

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
