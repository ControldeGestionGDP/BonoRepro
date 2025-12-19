import streamlit as st
import pandas as pd
from io import BytesIO

# =========================
# CONFIGURACIÓN
# =========================
st.set_page_config(
    page_title="Cruce de DNIs – Bono",
    layout="centered"
)

st.title("📥 Cruce masivo de DNIs – Base de Trabajadores")

st.markdown("""
**Flujo del sistema**
1. Subes un Excel SOLO con la columna **DNI**
2. Subes la base maestra de trabajadores
3. El sistema cruza y devuelve **Nombre y Cargo**
✔ Conserva ceros iniciales  
✔ Limpia basura invisible  
✔ Diagnóstico incluido
""")

# =========================
# FUNCIÓN CLAVE
# =========================
def limpiar_dni(col):
    return (
        col.astype(str)
        .str.normalize("NFKD")
        .str.replace(r"[^\d]", "", regex=True)
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
    "📊 Base maestra de trabajadores",
    type=["xlsx"],
    key="base"
)

if archivo_dni and archivo_base:

    # =========================
    # LECTURA SEGURA
    # =========================
    df_dni = pd.read_excel(archivo_dni, dtype=str)
    df_base = pd.read_excel(archivo_base, dtype=str)

    # Normalizar encabezados
    df_dni.columns = df_dni.columns.str.strip()
    df_base.columns = df_base.columns.str.strip()

    # =========================
    # VALIDACIONES
    # =========================
    if "DNI" not in df_dni.columns:
        st.error("❌ El archivo de DNIs debe tener una columna llamada 'DNI'")
        st.stop()

    columnas_base = {"DNI", "Nombre", "Cargo"}
    if not columnas_base.issubset(df_base.columns):
        st.error("❌ La base debe contener las columnas: DNI, Nombre y Cargo")
        st.stop()

    # =========================
    # LIMPIEZA DNI (CRÍTICO)
    # =========================
    df_dni["DNI"] = limpiar_dni(df_dni["DNI"])
    df_base["DNI"] = limpiar_dni(df_base["DNI"])

    # =========================
    # DIAGNÓSTICO (CLAVE)
    # =========================
    st.subheader("🔍 Diagnóstico de coincidencias")

    col1, col2 = st.columns(2)
    with col1:
        st.write("Ejemplo DNIs archivo:")
        st.write(df_dni["DNI"].head(10))

    with col2:
        st.write("Ejemplo DNIs base:")
        st.write(df_base["DNI"].head(10))

    st.write("Coincidencias encontradas:")
    st.write(
        df_dni["DNI"].isin(df_base["DNI"]).value_counts()
    )

    # =========================
    # CRUCE
    # =========================
    df_resultado = df_dni.merge(
        df_base[["DNI", "Nombre", "Cargo"]],
        on="DNI",
        how="left",
        validate="m:1"
    )

    df_resultado["Estado"] = df_resultado["Nombre"].apply(
        lambda x: "OK" if pd.notna(x) else "NO ENCONTRADO"
    )

    # =========================
    # RESULTADO
    # =========================
    st.success("✅ Cruce ejecutado correctamente")
    st.subheader("📋 Resultado")
    st.dataframe(df_resultado.head(20))

    # DNIs no encontrados
    no_encontrados = df_resultado[df_resultado["Estado"] == "NO ENCONTRADO"]
    if not no_encontrados.empty:
        st.warning(f"⚠️ {len(no_encontrados)} DNIs no encontrados")
        st.write(no_encontrados[["DNI"]].head(10))

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
        file_name="cruce_dni_resultado.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
