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
1. Subir archivo con **solo DNI**
2. Subir base maestra de trabajadores
3. El sistema cruza y devuelve archivo completo
""")

# =========================
# SUBIR ARCHIVO DE DNIs
# =========================
archivo_dni = st.file_uploader(
    "📄 Excel con lista de DNI",
    type=["xlsx"],
    key="dni"
)

# =========================
# SUBIR BASE MAESTRA
# =========================
archivo_base = st.file_uploader(
    "📊 Base de trabajadores (SharePoint)",
    type=["xlsx"],
    key="base"
)

if archivo_dni and archivo_base:

    # Leer archivos
    df_dni = pd.read_excel(archivo_dni)
    df_base = pd.read_excel(archivo_base)

    # Normalizar nombres de columnas
    df_dni.columns = df_dni.columns.str.strip()
    df_base.columns = df_base.columns.str.strip()

    # Validación mínima
    if "DNI" not in df_dni.columns:
        st.error("❌ El archivo de DNIs debe tener una columna llamada 'DNI'")
        st.stop()

    if not {"DNI", "Nombre", "Cargo"}.issubset(df_base.columns):
        st.error("❌ La base debe contener: DNI, Nombre, Cargo")
        st.stop()

    # Limpieza de DNI
    df_dni["DNI"] = df_dni["DNI"].astype(str).str.strip()
    df_base["DNI"] = df_base["DNI"].astype(str).str.strip()

    # Cruce
    df_resultado = df_dni.merge(
        df_base[["DNI", "Nombre", "Cargo"]],
        on="DNI",
        how="left"
    )

    # Marcar no encontrados
    df_resultado["Estado"] = df_resultado["Nombre"].apply(
        lambda x: "OK" if pd.notna(x) else "NO ENCONTRADO"
    )

    st.success("✅ Proceso completado")
    st.subheader("Vista previa del resultado")
    st.dataframe(df_resultado.head(20))

    # Exportar
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
