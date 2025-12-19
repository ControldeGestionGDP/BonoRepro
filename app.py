import streamlit as st
import pandas as pd
from io import BytesIO
import plotly.express as px

# =========================
# CONFIGURACIÓN GLOBAL
# =========================
st.set_page_config(
    page_title="Bono Reproductoras GDP",
    layout="wide"
)

# =========================
# PORTADA
# =========================
if "ingresar" not in st.session_state:
    st.session_state.ingresar = False

if not st.session_state.ingresar:
    st.markdown("""
        <div style='text-align:center; padding-top:100px'>
            <h1>🐔 BONO REPRODUCTORAS GDP</h1>
            <h3>Sistema de cálculo y distribución de bonos</h3>
            <p style="color:gray;">Desarrollado por Gerencia de Control de Gestión</p>
        </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        if st.button("🚀 Ingresar al sistema", use_container_width=True):
            st.session_state.ingresar = True
            st.rerun()
    st.stop()

# =========================
# REGLAS
# =========================
REGLAS_PRODUCCION = {
    "GALPONERO": 1.00,
    "AYUDANTE GALPONERO": 0.125,
    "VOLANTE DESCANSERO": 0.125,
    "VOLANTE ALIMENTO": 0.125,
    "BIOSEGURIDAD": 0.0625,
    "GUARDIANES": 0.0625,
    "CAPORAL": 0.125,
    "SUPERVISOR": 1.00,
    "MANTENIMIENTO": 0.0,
    "GRADING": 0.08,
    "VACUNADORES": 0.07
}

DESCUENTO_FALTAS = {0:1,1:0.9,2:0.8,3:0.7,4:0.6}

def factor_faltas(f):
    try:
        return DESCUENTO_FALTAS.get(int(f),0.5)
    except:
        return 0.5

# =========================
# APP
# =========================
st.title("🐔 BONO REPRODUCTORAS GDP")

archivo_dni = st.file_uploader("📄 Excel DNIs", type="xlsx")
archivo_base = st.file_uploader("📊 Base trabajadores", type="xlsx")

if archivo_dni and archivo_base:
    df_dni = pd.read_excel(archivo_dni, dtype=str)
    df_base = pd.read_excel(archivo_base, dtype=str)

    for df_ in [df_dni, df_base]:
        df_.columns = df_.columns.str.upper().str.strip()

    def limpiar_dni(s):
        return s.astype(str).str.replace("'", "", regex=False).str.replace(".0","",regex=False).str.zfill(8)

    df_dni["DNI"] = limpiar_dni(df_dni["DNI"])
    df_base["DNI"] = limpiar_dni(df_base["DNI"])

    df = df_dni.merge(
        df_base[["DNI","NOMBRE COMPLETO","CARGO"]],
        on="DNI",
        how="left"
    )

    st.success("✅ Cruce realizado")

    lotes = st.text_input("Lotes (211-212)", "211-212").split("-")
    config = {}
    cols = st.columns(len(lotes))
    for i,l in enumerate(lotes):
        with cols[i]:
            config[l] = st.number_input(f"Monto {l}", value=1000.0)

    if "tabla" not in st.session_state:
        st.session_state.tabla = df.copy()
        for l in lotes:
            st.session_state.tabla[f"P_{l}"] = 0.0
            st.session_state.tabla[f"F_{l}"] = 0

    # =========================
    # FORM DE EDICIÓN (FIX DEFINITIVO)
    # =========================
    st.subheader("✍️ Registro por trabajador y lote")

    with st.form("form_edicion"):
        df_edit = st.data_editor(
            st.session_state.tabla,
            use_container_width=True,
            num_rows="fixed"
        )

        guardar = st.form_submit_button("💾 Guardar cambios")

        if guardar:
            st.session_state.tabla = df_edit.copy()
            st.success("✅ Datos guardados correctamente")

    # =========================
    # CÁLCULO
    # =========================
    df_final = st.session_state.tabla.copy()
    pagos = []

    for l in lotes:
        col = f"PAGO_{l}"
        df_final[col] = df_final.apply(
            lambda r: round(
                REGLAS_PRODUCCION.get(str(r["CARGO"]).upper(),0)
                * config[l]
                * (r[f"P_{l}"]/100)
                * factor_faltas(r[f"F_{l}"]),
                2
            ), axis=1
        )
        pagos.append(col)

    df_final["TOTAL S/"] = df_final[pagos].sum(axis=1)

    # =========================
    # RESULTADO
    # =========================
    st.subheader("💰 Resultado final")
    st.dataframe(df_final, use_container_width=True)

    fig = px.bar(
        df_final,
        x="NOMBRE COMPLETO",
        y="TOTAL S/",
        text="TOTAL S/",
        title="Distribución de bonos"
    )
    fig.update_traces(texttemplate="S/ %{text:.2f}", textposition="outside")
    st.plotly_chart(fig, use_container_width=True)

    # =========================
    # EXPORTAR
    # =========================
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df_final.to_excel(writer, index=False)
    output.seek(0)

    st.download_button(
        "📥 Descargar Excel",
        data=output,
        file_name="bono_reproductoras_final.xlsx"
    )
