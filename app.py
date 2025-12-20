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
# TABLAS DE % POR CARGO
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
REGLAS_LEVANTE = REGLAS_PRODUCCION.copy()

# =========================
# DESCUENTO POR FALTAS
# =========================
DESCUENTO_FALTAS = {0:1.0,1:0.9,2:0.8,3:0.7,4:0.6}
def factor_faltas(f):
    try:
        return DESCUENTO_FALTAS.get(int(f), 0.5)
    except:
        return 0.5

# =========================
# APP PRINCIPAL
# =========================
st.title("🐔 BONO REPRODUCTORAS GDP")

archivo_dni = st.file_uploader("📄 Excel con DNIs", type=["xlsx"])
archivo_base = st.file_uploader("📊 Base de trabajadores", type=["xlsx"])

if archivo_dni and archivo_base:
    df_dni = pd.read_excel(archivo_dni, dtype=str)
    df_base = pd.read_excel(archivo_base, dtype=str)

    df_dni.columns = df_dni.columns.str.upper().str.strip()
    df_base.columns = df_base.columns.str.upper().str.strip()

    def limpiar_dni(s):
        return s.astype(str).str.replace(".0","",regex=False).str.strip().str.zfill(8)

    df_dni["DNI"] = limpiar_dni(df_dni["DNI"])
    df_base["DNI"] = limpiar_dni(df_base["DNI"])
    df_base = df_base.drop_duplicates("DNI")

    df = df_dni.merge(df_base[["DNI","NOMBRE COMPLETO","CARGO"]], on="DNI", how="left")

    st.success("✅ Cruce de trabajadores realizado")

    # =========================
    # TIPO PROCESO
    # =========================
    tipo = st.radio("Tipo de proceso", ["PRODUCCIÓN","LEVANTE"], horizontal=True)
    reglas = REGLAS_PRODUCCION if tipo=="PRODUCCIÓN" else REGLAS_LEVANTE

    # =========================
    # LOTES
    # =========================
    lotes = [l.strip() for l in st.text_input("Lotes (211-212-213)", "211-212-213").split("-") if l.strip()]
    config_lotes = {}

    cols = st.columns(len(lotes))
    for i,l in enumerate(lotes):
        with cols[i]:
            config_lotes[l] = {
                "GENETICA": st.text_input(f"Genética {l}", "ROSS"),
                "MONTO": st.number_input(f"Monto S/ {l}", value=1000.0)
            }

    # =========================
    # TABLA BASE
    # =========================
    if "tabla" not in st.session_state:
        st.session_state.tabla = df.copy()
        for l in lotes:
            st.session_state.tabla[f"P_{l}"] = 0.0
            st.session_state.tabla[f"F_{l}"] = 0

    if "df_edit" not in st.session_state:
        st.session_state.df_edit = st.session_state.tabla.copy()

    # =========================
    # ➕ AGREGAR TRABAJADOR (PRO)
    # =========================
    st.subheader("➕ Agregar trabajador")

    dni_input = st.text_input("Ingrese DNI")
    dni_clean = dni_input.strip().zfill(8)

    fila_preview = df_base[df_base["DNI"] == dni_clean]

    if dni_input:
        if not fila_preview.empty:
            fila = fila_preview.iloc[0]
            st.markdown(
                f"""
                <div style="background:#E8F2FF;padding:10px;border-radius:6px;">
                <b>👤 {fila['NOMBRE COMPLETO']}</b><br>
                <span style="color:gray;">{fila['CARGO']}</span>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.error("❌ DNI no encontrado en la base")

    if st.button("Agregar trabajador"):
        if dni_clean in st.session_state.tabla["DNI"].values:
            st.warning("⚠️ El trabajador ya existe")
        elif fila_preview.empty:
            st.error("❌ No se puede agregar: DNI inválido")
        else:
            fila = fila_preview.iloc[0]
            nuevo = {
                "DNI": dni_clean,
                "NOMBRE COMPLETO": fila["NOMBRE COMPLETO"],
                "CARGO": fila["CARGO"]
            }
            for l in lotes:
                nuevo[f"P_{l}"] = 0.0
                nuevo[f"F_{l}"] = 0

            st.session_state.tabla = pd.concat(
                [st.session_state.tabla, pd.DataFrame([nuevo])],
                ignore_index=True
            )
            st.session_state.df_edit = st.session_state.tabla.copy()
            st.success("✅ Trabajador agregado")
            st.rerun()

    # =========================
    # EDICIÓN
    # =========================
    st.subheader("✍️ Registro por trabajador y lote")
    with st.form("editar"):
        df_edit = st.data_editor(st.session_state.df_edit, use_container_width=True)
        if st.form_submit_button("💾 Guardar cambios"):
            st.session_state.tabla = df_edit.copy()
            st.session_state.df_edit = df_edit.copy()
            st.success("✅ Tabla actualizada")

    # =========================
    # CÁLCULO FINAL
    # =========================
    df_final = st.session_state.tabla.copy()
    pagos = []

    for l in lotes:
        col = f"PAGO_{l}"
        df_final[col] = df_final.apply(
            lambda r: round(
                reglas.get(r["CARGO"].upper(),0)
                * config_lotes[l]["MONTO"]
                * (float(r[f"P_{l}"]) / 100)
                * factor_faltas(r[f"F_{l}"]),
                2
            ), axis=1
        )
        pagos.append(col)

    df_final["TOTAL S/"] = df_final[pagos].sum(axis=1)

    st.subheader("💰 Resultado final")
    st.dataframe(df_final, use_container_width=True)

    fig = px.bar(
        df_final,
        x="NOMBRE COMPLETO",
        y="TOTAL S/",
        text="TOTAL S/"
    )
    fig.update_traces(texttemplate="S/ %{text:,.2f}", textposition="outside")
    st.plotly_chart(fig, use_container_width=True)

    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df_final.to_excel(writer, index=False)

    st.download_button("📥 Descargar Excel", output.getvalue(), "bono_final.xlsx")
