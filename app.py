import streamlit as st
import pandas as pd

st.set_page_config(page_title="Cruce de DNI", layout="wide")

st.title("🐔BONO REPRODUCTORAS GDP")

st.markdown("""
**Pasos:**
1. Subir Excel con lista de DNI  
2. Subir base maestra de trabajadores  
3. El sistema cruza, conserva ceros y devuelve el archivo listo  
""")

# ---------- FUNCION LIMPIAR DNI ----------
def limpiar_dni(col):
    return (
        col.astype(str)
        .str.replace(".0", "", regex=False)
        .str.replace("'", "", regex=False)
        .str.strip()
        .str.zfill(8)
    )

# ---------- SUBIR ARCHIVOS ----------
archivo_dni = st.file_uploader(
    "📄 Excel con lista de DNI",
    type=["xlsx"]
)

archivo_trabajadores = st.file_uploader(
    "👥 Base de trabajadores",
    type=["xlsx"]
)

if archivo_dni and archivo_trabajadores:

    df_dni = pd.read_excel(archivo_dni)
    df_trab = pd.read_excel(archivo_trabajadores)

    # ---------- NORMALIZAR DNI ----------
    df_dni["DNI"] = limpiar_dni(df_dni["DNI"])
    df_trab["DNI"] = limpiar_dni(df_trab["DNI"])

    # ---------- VALIDACIONES ----------
    duplicados = df_trab["DNI"].duplicated().sum()
    if duplicados > 0:
        st.warning(
            f"⚠️ Se encontraron {duplicados} DNIs duplicados en la base. "
            "Se usará el primer registro por DNI."
        )
        df_trab = df_trab.drop_duplicates(subset="DNI", keep="first")

    # ---------- CRUCE ----------
    resultado = df_dni.merge(
        df_trab,
        on="DNI",
        how="left"
    )

    st.success("✅ Cruce realizado correctamente")

    # ---------- VISTA PREVIA ----------
    st.subheader("👀 Vista previa")
    st.dataframe(resultado.head(10))

    # ---------- DESCARGA ----------
    archivo_salida = "resultado_cruce.xlsx"
    resultado.to_excel(archivo_salida, index=False)

    with open(archivo_salida, "rb") as f:
        st.download_button(
            label="⬇️ Descargar archivo final",
            data=f,
            file_name=archivo_salida,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )




