import streamlit as st
import pandas as pd
from io import BytesIO

# =========================
# CONFIGURACIÓN
# =========================
st.set_page_config(
    page_title="Bono Reproductoras",
    layout="wide"
)

st.title("🐔 BONO REPRODUCTORAS GDP")

st.markdown("""
**Flujo:**
1. Subir Excel con DNIs  
2. Subir base de trabajadores  
3. Ingresar lotes, participación y faltas  
4. Descargar archivo final  
""")

# =========================
# CARGA DE ARCHIVOS
# =========================
archivo_dni = st.file_uploader(
    "📄 Excel con lista de DNI",
    type=["xlsx"]
)

archivo_base = st.file_uploader(
    "📊 Base de trabajadores",
    type=["xlsx"]
)

if archivo_dni and archivo_base:

    # =========================
    # LECTURA
    # =========================
    df_dni = pd.read_excel(archivo_dni, dtype=str)
    df_base = pd.read_excel(archivo_base, dtype=str)

    df_dni.columns = df_dni.columns.str.strip().str.upper()
    df_base.columns = df_base.columns.str.strip().str.upper()

    # =========================
    # VALIDACIONES
    # =========================
    if "DNI" not in df_dni.columns:
        st.error("❌ El archivo de DNIs debe tener columna DNI")
        st.stop()

    if not {"DNI", "NOMBRE COMPLETO", "CARGO"}.issubset(df_base.columns):
        st.error("❌ La base debe tener: DNI, NOMBRE COMPLETO y CARGO")
        st.stop()

    # =========================
    # LIMPIEZA DNI
    # =========================
    def limpiar_dni(serie):
        return (
            serie.astype(str)
            .str.replace("'", "", regex=False)
            .str.replace(".0", "", regex=False)
            .str.strip()
            .str.zfill(8)
        )

    df_dni["DNI"] = limpiar_dni(df_dni["DNI"])
    df_base["DNI"] = limpiar_dni(df_base["DNI"])

    df_base = df_base.drop_duplicates(subset="DNI")

    # =========================
    # CRUCE
    # =========================
    df_base_persona = df_dni.merge(
        df_base[["DNI", "NOMBRE COMPLETO", "CARGO"]],
        on="DNI",
        how="left"
    )

    df_base_persona["ESTADO"] = df_base_persona["NOMBRE COMPLETO"].apply(
        lambda x: "OK" if pd.notna(x) else "NO ENCONTRADO"
    )

    # =========================
    # EXPANDIR A 4 LOTES
    # =========================
    filas = []
    for _, row in df_base_persona.iterrows():
        for _ in range(4):  # 4 lotes por persona
            filas.append({
                "DNI": row["DNI"],
                "NOMBRE COMPLETO": row["NOMBRE COMPLETO"],
                "CARGO": row["CARGO"],
                "ESTADO": row["ESTADO"],
                "LOTE": "",
                "PARTICIPACIÓN (%)": "",
                "FALTAS": ""
            })

    df_lotes = pd.DataFrame(filas)

    st.success("✅ Cruce realizado – ingrese información por lote")

    st.subheader("✍️ Registro por persona y lote")

    df_editado = st.data_editor(
        df_lotes,
        use_container_width=True,
        num_rows="fixed"
    )

    # =========================
    # EXPORTACIÓN
    # =========================
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df_editado.to_excel(writer, index=False)

    output.seek(0)

    st.download_button(
        "📤 Descargar archivo final",
        data=output,
        file_name="bono_reproductoras_por_lote.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
