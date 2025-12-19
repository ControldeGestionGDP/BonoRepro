import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Liquidación por DNI", layout="wide")
st.title("📊 Liquidación de Participación por DNI")

st.markdown("""
**Flujo**
1. Subir Excel con lista de DNI
2. Subir base maestra de trabajadores
3. El sistema cruza y genera estructura lista para cálculo
""")

# =========================
# SUBIDA DE ARCHIVOS
# =========================
archivo_dni = st.file_uploader("📄 Excel con lista de DNI", type=["xlsx"])
archivo_base = st.file_uploader("📊 Base de trabajadores", type=["xlsx"])

if archivo_dni and archivo_base:

    # =========================
    # LECTURA SEGURA (DNI TEXTO)
    # =========================
    df_dni = pd.read_excel(archivo_dni, dtype=str)
    df_base = pd.read_excel(archivo_base, dtype=str)

    df_dni.columns = df_dni.columns.str.strip()
    df_base.columns = df_base.columns.str.strip()

    # =========================
    # VALIDACIONES
    # =========================
    if "DNI" not in df_dni.columns:
        st.error("❌ El archivo de DNI debe tener la columna DNI")
        st.stop()

    if not {"DNI", "Nombre Completo", "Cargo"}.issubset(df_base.columns):
        st.error("❌ La base debe tener: DNI, Nombre Completo y Cargo")
        st.stop()

    # =========================
    # NORMALIZACIÓN DNI
    # =========================
    def limpiar_dni(x):
        if pd.isna(x):
            return None
        x = str(x).replace(".0", "").replace("'", "").strip()
        return x.zfill(8)

    df_dni["DNI"] = df_dni["DNI"].apply(limpiar_dni)
    df_base["DNI"] = df_base["DNI"].apply(limpiar_dni)

    # =========================
    # ELIMINAR DUPLICADOS BASE
    # =========================
    duplicados = df_base["DNI"].duplicated().sum()
    if duplicados > 0:
        st.warning(f"⚠️ Se encontraron {duplicados} DNIs duplicados. Se usará el primer registro.")
        df_base = df_base.drop_duplicates("DNI", keep="first")

    # =========================
    # CRUCE
    # =========================
    df = df_dni.merge(
        df_base[["DNI", "Nombre Completo", "Cargo"]],
        on="DNI",
        how="left"
    )

    # =========================
    # COLUMNAS BASE
    # =========================
    df.insert(0, "Estado", "En Proceso")

    # =========================
    # COLUMNAS PARTICIPACIÓN (%)
    # =========================
    for col in ["211", "212", "213"]:
        df[col] = ""

    # =========================
    # COLUMNAS FALTAS
    # =========================
    for col in ["F_211", "F_212", "F_213"]:
        df[col] = ""

    # =========================
    # COLUMNAS LIQUIDACIÓN
    # =========================
    for col in ["L_211", "L_212", "L_213"]:
        df[col] = ""

    # =========================
    # TOTAL
    # =========================
    df["TOTAL S/."] = ""

    st.success("✅ Estructura generada correctamente")
    st.subheader("Vista previa")
    st.dataframe(df, use_container_width=True)

    # =========================
    # EXPORTAR
    # =========================
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)
    output.seek(0)

    st.download_button(
        "📥 Descargar archivo base",
        data=output,
        file_name="liquidacion_base.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
