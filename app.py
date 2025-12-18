import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Carga de Excel", layout="centered")

st.title("Carga de Base de Datos")
st.write("Sube un archivo Excel para validar el flujo")

archivo = st.file_uploader("Sube tu archivo Excel", type=["xlsx"])

if archivo is not None:
    df = pd.read_excel(archivo)

    st.success("Archivo cargado correctamente")
    st.write("Vista previa:")
    st.dataframe(df.head())

    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)
    output.seek(0)

    st.download_button(
        label="Descargar archivo",
        data=output,
        file_name="archivo_procesado.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )