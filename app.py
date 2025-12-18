import streamlit as st
import pandas as pd
from io import BytesIO

# Configuración de la página
st.set_page_config(
    page_title="Carga de Excel - Bono",
    layout="centered"
)

st.title("📥 Carga de Base de Datos")
st.write("Sube un archivo Excel para validar el flujo de carga.")

# Subir archivo
archivo = st.file_uploader(
    "Sube tu archivo Excel",
    type=["xlsx"]
)

if archivo is not None:
    try:
        # Leer el Excel
        df = pd.read_excel(archivo)

        st.success("✅ Archivo cargado correctamente")

        # Vista previa
        st.subheader("Vista previa de los datos")
        st.dataframe(df.head())

        # Preparar archivo para descarga
        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False)
        output.seek(0)

        # Botón de descarga
        st.download_button(
            label="📤 Descargar archivo procesado",
            data=output,
            file_name="archivo_procesado.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:
        st.error("❌ Ocurrió un error al procesar el archivo")
        st.exception(e)
