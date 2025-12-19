import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(
    page_title="Carga masiva por DNI",
    layout="centered"
)

st.title("📥 Carga masiva de colaboradores por DNI")

st.markdown("""
**Flujo:**
1. Subir archivo con DNIs
2. Subir base maestra
3. El sistema conserva ceros iniciales y cruza correctamente
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

    # 🔑 LEER COMO TEXTO (CLAVE)
    df_dni = pd.read_excel(archivo_dni, dtype={"DNI": str})
    df_base = pd.read_excel(archivo_base, dtype={"DNI": str})

    # Normalizar columnas
    df_dni.columns = df_dni.columns.str.strip()
    df_base.columns = df_base.columns.str.strip()

    # Validaciones
    if "DNI" not in df_dni.columns:
        st.error("❌ El archivo de DNIs debe tener una columna 'DNI'")
        st.stop()

    if not {"DNI", "Nombre", "Cargo"}.issubset(df_base.columns):
        st.error("❌ La base debe contener: DNI, Nombre, Cargo")
        st.stop()

    # =========================
    # LIMPIEZA Y NORMALIZACIÓN
    # =========================
    df_dni["DNI"] = (
        df_dni["DNI"]
        .astype(str)
        .str.replace(".0", "", regex=False)
        .str.strip()
        .str.zfill(8)
    )

    df_base["DNI"] = (
        df_base["DNI"]
        .astype(str)
        .str.replace(".0", "", regex=False)
        .str.strip()
        .str.zfill(8)
    )

    # =========================
    # CRUCE
    # =========================
    df_resultado = df_dni.merge(
        df_base[["DNI", "Nombre", "Cargo"]],
        on="DNI",
        how="left"
    )

    df_resultado["Estado"] = df_resultado["Nombre"].apply(
        lambda x: "OK" if pd.notna(x) else "NO ENCONTRADO"
    )

    st.success("✅ Cruce realizado correctamente")
    st.subheader("Vista previa")
    st.dataframe(df_resultado.head(20))

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
