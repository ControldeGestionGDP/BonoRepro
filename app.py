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
DESCUENTO_FALTAS = {0:1.00,1:0.90,2:0.80,3:0.70,4:0.60}

def factor_faltas(f):
    try:
        return DESCUENTO_FALTAS.get(int(f),0.50)
    except:
        return 0.50

# =========================
# APP PRINCIPAL
# =========================
st.title("🐔 BONO REPRODUCTORAS GDP")

archivo_dni = st.file_uploader("📄 Excel con DNIs", type=["xlsx"])
archivo_base = st.file_uploader("📊 Base de trabajadores", type=["xlsx"])

if archivo_dni and archivo_base:
    df_dni = pd.read_excel(archivo_dni, dtype=str)
    df_base = pd.read_excel(archivo_base, dtype=str)

    df_dni.columns = df_dni.columns.str.strip().str.upper()
    df_base.columns = df_base.columns.str.strip().str.upper()

    def limpiar_dni(s):
        return (
            s.astype(str)
            .str.replace("'", "", regex=False)
            .str.replace(".0", "", regex=False)
            .str.strip()
            .str.zfill(8)
        )

    df_dni["DNI"] = limpiar_dni(df_dni["DNI"])
    df_base["DNI"] = limpiar_dni(df_base["DNI"])
    df_base = df_base.drop_duplicates("DNI")

    df = df_dni.merge(
        df_base[["DNI","NOMBRE COMPLETO","CARGO"]],
        on="DNI",
        how="left"
    )

    st.success("✅ Cruce de trabajadores realizado")

    tipo = st.radio("Tipo de proceso", ["PRODUCCIÓN","LEVANTE"], horizontal=True)
    reglas = REGLAS_PRODUCCION if tipo=="PRODUCCIÓN" else REGLAS_LEVANTE

    lotes_txt = st.text_input("Lotes (ej: 211-212-213)", "211-212-213")
    lotes = [l.strip() for l in lotes_txt.split("-") if l.strip()]

    st.subheader("🧬 Configuración por lote")
    config_lotes = {}
    cols = st.columns(len(lotes))
    for i,lote in enumerate(lotes):
        with cols[i]:
            config_lotes[lote] = {
                "GENETICA": st.text_input(f"Genética {lote}", "ROSS").upper(),
                "MONTO": st.number_input(f"Monto S/ {lote}", value=1000.0, step=50.0)
            }

    # =========================
    # SESSION STATE TABLA
    # =========================
    if "tabla" not in st.session_state:
        st.session_state.tabla = df.copy()
        for l in lotes:
            st.session_state.tabla[f"P_{l}"] = 0.0
            st.session_state.tabla[f"F_{l}"] = 0

    # =========================
    # AGREGAR TRABAJADOR
    # =========================
    st.subheader("➕ Agregar trabajador")
    with st.form("form_agregar"):
        dni_new = st.text_input("DNI")
        submit_add = st.form_submit_button("Agregar trabajador")

        if submit_add:
            dni_new = dni_new.strip().zfill(8)
            if dni_new in df_base["DNI"].values and dni_new not in st.session_state.tabla["DNI"].values:
                fila = df_base[df_base["DNI"]==dni_new].iloc[0]
                nuevo = {
                    "DNI": dni_new,
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
                st.success("✅ Trabajador agregado")
                st.rerun()

    # =========================
    # ELIMINAR TRABAJADOR
    # =========================
    st.subheader("➖ Eliminar trabajador")
    dni_del = st.text_input("DNI a eliminar").strip().zfill(8)
    if st.button("Eliminar"):
        st.session_state.tabla = st.session_state.tabla[
            st.session_state.tabla["DNI"] != dni_del
        ]
        st.success("✅ Trabajador eliminado")

    # =========================
    # REGISTRO EDITABLE (1 GUARDADO)
    # =========================
    st.subheader("✍️ Registro por trabajador y lote")
    with st.form("form_edicion"):
        df_edit = st.data_editor(
            st.session_state.tabla,
            use_container_width=True,
            num_rows="fixed"
        )
        guardar = st.form_submit_button("💾 Actualizar tabla")

        if guardar:
            st.session_state.tabla = df_edit.copy()
            st.success("✅ Tabla actualizada")

    # =========================
    # CÁLCULO
    # =========================
    df_final = st.session_state.tabla.copy()
    pagos = []

    for l in lotes:
        col = f"PAGO_{l}"
        df_final[col] = df_final.apply(
            lambda r: round(
                reglas.get(str(r["CARGO"]).upper(),0)
                * config_lotes[l]["MONTO"]
                * (float(r[f"P_{l}"])/100)
                * factor_faltas(r[f"F_{l}"]), 2
            ) if r[f"P_{l}"]>0 else 0,
            axis=1
        )
        pagos.append(col)

    df_final["TOTAL S/"] = df_final[pagos].sum(axis=1)

    # =========================
    # RESULTADO FINAL
    # =========================
    st.subheader("💰 Resultado final")
    st.dataframe(df_final, use_container_width=True)

    # =========================
    # GRÁFICOS
    # =========================
    fig = px.bar(
        df_final,
        x="NOMBRE COMPLETO",
        y="TOTAL S/",
        text_auto=".2f",
        title="Bono total por trabajador"
    )
    fig.update_traces(textposition="outside", cliponaxis=False)
    fig.update_layout(height=550, xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)

    df_final["TOTAL_FALTAS"] = df_final[[c for c in df_final.columns if c.startswith("F_")]].sum(axis=1)
    fig2 = px.bar(
        df_final,
        x="NOMBRE COMPLETO",
        y="TOTAL_FALTAS",
        text_auto=True,
        title="Total de faltas por trabajador"
    )
    fig2.update_traces(textposition="outside", cliponaxis=False)
    fig2.update_layout(height=450, xaxis_tickangle=-45, yaxis=dict(dtick=1))
    st.plotly_chart(fig2, use_container_width=True)

    # =========================
    # EXPORTAR
    # =========================
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df_final.to_excel(writer, index=False)
    output.seek(0)

    st.download_button(
        "📥 Descargar archivo final",
        data=output,
        file_name="bono_reproductoras_final.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
