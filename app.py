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
3. El sistema normaliza DNIs y cruza correctamente
""")

# =========================
# FUNCIÓN CLAVE
# =========================
def limpiar_dni(col):
    return (
        col.astype(str)
        .str.replace(r"\.0$", "", regex=True)
        .str.replace(r"\D", "", regex=True)
        .str.strip()
        .str.zfill(8)
    )

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

    df_dni = pd.read_excel(archivo_dni)
    df_base = pd.read_excel(archivo_base)

    df_dni.columns = df_dni.columns.str.strip()
    df_base.columns = df_base.columns.str.strip()

    if "DNI" not in df_dni.columns:
        st.error("❌ El archivo de DNIs debe tener una columna 'DNI'")
        st.stop()

    if not {"DNI", "Nombre", "Cargo"}.issubset(df_base.columns):
        st.error("❌ La base debe contener: DNI, Nombre, Cargo")
        st.stop()

    # =========================
    # NORMALIZACIÓN (CLAVE)
    # =========================
    df_dni["DNI"] = limpiar_dni(df_dni["DNI"])
    df_base["DNI"] = limpiar_dni(df_base["DNI"])

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
    # EXPORTAR
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
