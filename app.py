import streamlit as st
import pandas as pd
from io import BytesIO

# =========================
# CONFIGURACIÓN
# =========================
st.set_page_config(
    page_title="Carga masiva por DNI",
    layout="centered"
)

st.title("📥 Carga masiva de colaboradores por DNI")

st.markdown("""
**Flujo:**
1. Subir Excel con lista de DNIs  
2. Subir base maestra de trabajadores  
3. El sistema cruza, conserva ceros y devuelve el archivo listo
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

# =========================
# PROCESAMIENTO
# =========================
if archivo_dni and archivo_base:

    # Leer SIEMPRE como texto
    df_dni = pd.read_excel(archivo_dni, dtype=str)
    df_base = pd.read_excel(archivo_base, dtype=str)

    # Normalizar nombres de columnas
    df_dni.columns = df_dni.columns.str.strip()
    df_base.columns = df_base.columns.str.strip()

    # Validaciones
    if "DNI" not in df_dni.columns:
        st.error("❌ El archivo de DNIs debe contener una columna llamada 'DNI'")
        st.stop()

    if not {"DNI", "Nombre", "Cargo"}.issubset(df_base.columns):
        st.error("❌ La base debe contener las columnas: DNI, Nombre, Cargo")
        st.stop()

    # =========================
    # LIMPIEZA DE DNI
    # =========================
    def limpiar_dni(col):
        return (
            col.astype(str)
            .str.replace("'", "", regex=False)   # elimina '
            .str.replace(".0", "", regex=False)  # elimina .0 de Excel
            .str.strip()
            .str.zfill(8)                        # asegura 8 dígitos
        )

    df_dni["DNI"] = limpiar_dni(df_dni["DNI"])
    df_base["DNI"] = limpiar_dni(df_base["DNI"])

    # =========================
    # CONTROL DE DUPLICADOS
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
        df_base[["DNI", "Nombre", "Cargo"]],
        on="DNI",
        how="left"
    )

    df_resultado["Estado"] = df_resultado["Nombre"].apply(
        lambda x: "OK" if pd.notna(x) else "NO ENCONTRADO"
    )

    # =========================
    # RESULTADO
    # =========================
    st.success("✅ Cruce realizado correctamente")
    st.subheader("Vista previa")
    st.dataframe(df_resultado.head(20))

    # =========================
    # EXPORTAR EXCEL
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
