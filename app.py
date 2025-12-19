import streamlit as st
import pandas as pd
from io import BytesIO

# =========================
# CONFIGURACIÓN
# =========================
st.set_page_config(
    page_title="Carga masiva por DNI",
    layout="wide"
)

st.title("🐔 BONO REPRODUCTORAS GDP")

st.markdown("""
**Flujo:**
1. Subir Excel con DNIs
2. Subir base maestra de trabajadores
3. El sistema cruza, conserva ceros iniciales y devuelve el archivo listo
""")

# =========================
# CARGA DE ARCHIVOS
# =========================
archivo_dni = st.file_uploader(
    "📄 Excel con lista de DNI",
    type=["xlsx"],
    key="dni"
)

archivo_base = st.file_uploader(
    "📊 Base de trabajadores",
    type=["xlsx"],
    key="base"
)

if archivo_dni and archivo_base:

    # =========================
    # LECTURA (DNI COMO TEXTO)
    # =========================
    df_dni = pd.read_excel(archivo_dni, dtype=str)
    df_base = pd.read_excel(archivo_base, dtype=str)

    # =========================
    # NORMALIZAR COLUMNAS
    # =========================
    df_dni.columns = (
        df_dni.columns
        .str.strip()
        .str.upper()
    )

    df_base.columns = (
        df_base.columns
        .str.strip()
        .str.upper()
    )

    # =========================
    # VALIDACIONES
    # =========================
    if "DNI" not in df_dni.columns:
        st.error("❌ El archivo de DNIs debe tener una columna llamada DNI")
        st.stop()

    if not {"DNI", "NOMBRE COMPLETO", "CARGO"}.issubset(df_base.columns):
        st.error("❌ La base debe tener las columnas: DNI, NOMBRE COMPLETO y CARGO")
        st.stop()

    # =========================
    # LIMPIEZA DE DNI
    # =========================
    def limpiar_dni(serie):
        return (
            serie
            .astype(str)
            .str.replace("'", "", regex=False)
            .str.replace(".0", "", regex=False)
            .str.strip()
            .str.zfill(8)
        )

    df_dni["DNI"] = limpiar_dni(df_dni["DNI"])
    df_base["DNI"] = limpiar_dni(df_base["DNI"])

    # =========================
    # QUITAR DUPLICADOS EN BASE
    # =========================
    duplicados = df_base["DNI"].duplicated().sum()

    if duplicados > 0:
        st.warning(
            f"⚠️ Se encontraron {duplicados} DNIs duplicados en la base. "
            "Se usará el primer registro por DNI."
        )

    df_base = df_base.drop_duplicates(subset="DNI", keep="first")

    # =========================
    # CRUCE
    # =========================
    df_resultado = df_dni.merge(
        df_base[["DNI", "NOMBRE COMPLETO", "CARGO"]],
        on="DNI",
        how="left"
    )

    # =========================
    # ESTADO
    # =========================
    df_resultado["ESTADO"] = df_resultado["NOMBRE COMPLETO"].apply(
        lambda x: "OK" if pd.notna(x) else "NO ENCONTRADO"
    )

    # =========================
    # RESULTADO
    # =========================
    st.success("✅ Cruce realizado correctamente")
    st.subheader("Vista previa")
    st.dataframe(df_resultado.head(20), use_container_width=True)

    # =========================
    # EXPORTACIÓN
    # =========================
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df_resultado.to_excel(writer, index=False)

    output.seek(0)

    st.download_button(
        label="📤 Descargar archivo final",
        data=output,
        file_name="resultado_cruce_dni.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

