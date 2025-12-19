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
        f = int(f)
    except:
        return 0.50
    return DESCUENTO_FALTAS.get(f,0.50)

# =========================
# APP PRINCIPAL
# =========================
st.title("🐔 BONO REPRODUCTORAS GDP")

# =========================
# CARGA DE ARCHIVOS
# =========================
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

    # =========================
    # TIPO DE PROCESO
    # =========================
    tipo = st.radio("Tipo de proceso", ["PRODUCCIÓN","LEVANTE"], horizontal=True)
    reglas = REGLAS_PRODUCCION if tipo=="PRODUCCIÓN" else REGLAS_LEVANTE

    # =========================
    # LOTES
    # =========================
    lotes_txt = st.text_input("Lotes (ej: 211-212-213)", "211-212-213")
    lotes = [l.strip() for l in lotes_txt.split("-") if l.strip()]

    st.subheader("🧬 Configuración por lote")
    config_lotes = {}
    cols = st.columns(len(lotes))

    for i,lote in enumerate(lotes):
        with cols[i]:
            genetica = st.text_input(f"Genética {lote}", "ROSS")
            monto = st.number_input(f"Monto S/ {lote}", min_value=0.0, value=1000.0, step=50.0)
            config_lotes[lote] = {"GENETICA":genetica.upper(),"MONTO":monto}

    # =========================
    # SESSION STATE TABLA
    # =========================
    if "tabla" not in st.session_state:
        st.session_state.tabla = df.copy()
        for lote in lotes:
            st.session_state.tabla[f"P_{lote}"] = 0.0
            st.session_state.tabla[f"F_{lote}"] = 0
    else:
        for lote in lotes:
            if f"P_{lote}" not in st.session_state.tabla.columns:
                st.session_state.tabla[f"P_{lote}"] = 0.0
            if f"F_{lote}" not in st.session_state.tabla.columns:
                st.session_state.tabla[f"F_{lote}"] = 0
        for col in list(st.session_state.tabla.columns):
            if col.startswith("P_") or col.startswith("F_"):
                if col.split("_")[1] not in lotes:
                    st.session_state.tabla.drop(columns=[col], inplace=True)

    # =========================
    # ORDENAR COLUMNAS
    # =========================
    base_cols = ["DNI","NOMBRE COMPLETO","CARGO"]
    pct_cols = [f"P_{l}" for l in lotes]
    faltas_cols = [f"F_{l}" for l in lotes]
    st.session_state.tabla = st.session_state.tabla[base_cols + pct_cols + faltas_cols]

    # =========================
    # SINCRONIZAR df_edit (FIX KEYERROR)
    # =========================
    if "df_edit" not in st.session_state:
        st.session_state.df_edit = st.session_state.tabla.copy()
    else:
        for col in st.session_state.tabla.columns:
            if col not in st.session_state.df_edit.columns:
                st.session_state.df_edit[col] = st.session_state.tabla[col]
        for col in list(st.session_state.df_edit.columns):
            if col not in st.session_state.tabla.columns:
                st.session_state.df_edit.drop(columns=[col], inplace=True)
        st.session_state.df_edit = st.session_state.df_edit[st.session_state.tabla.columns]

    # =========================
    # REGISTRO
    # =========================
    st.subheader("✍️ Registro por trabajador y lote")
    with st.form("form_edicion"):
        df_edit = st.data_editor(
            st.session_state.df_edit,
            use_container_width=True,
            num_rows="fixed"
        )
        guardar = st.form_submit_button("💾 Actualizar tabla")

        if guardar:
            st.session_state.df_edit = df_edit.copy()
            st.session_state.tabla = df_edit.copy()
            st.success("✅ Tabla actualizada")

    # =========================
    # CÁLCULO
    # =========================
    df_final = st.session_state.tabla.copy()
    pagos = []

    for lote in lotes:
        def pago(row):
            cargo = str(row["CARGO"]).upper()
            pct = reglas.get(cargo,0)
            part = float(row[f"P_{lote}"])/100
            faltas = row[f"F_{lote}"]
            if part<=0:
                return 0.0
            return round(pct * config_lotes[lote]["MONTO"] * part * factor_faltas(faltas),2)

        col = f"PAGO_{lote}"
        df_final[col] = df_final.apply(pago, axis=1)
        pagos.append(col)

    df_final["TOTAL S/"] = df_final[pagos].sum(axis=1)

    # =========================
    # RESULTADO FINAL
    # =========================
    st.subheader("💰 Resultado final")
    st.dataframe(df_final, use_container_width=True)

    # =========================
    # GRÁFICO BONOS
    # =========================
    fig = px.bar(
        df_final,
        x="NOMBRE COMPLETO",
        y="TOTAL S/",
        text_auto=".2f",
        title="Bono total por trabajador (S/)"
    )

    fig.update_traces(textposition="outside", cliponaxis=False)
    fig.update_layout(
        height=550,
        xaxis_tickangle=-45,
        margin=dict(t=80,b=140)
    )

    st.plotly_chart(fig, use_container_width=True)

    # =========================
    # GRÁFICO FALTAS
    # =========================
    faltas_cols = [c for c in df_final.columns if c.startswith("F_")]
    df_final["TOTAL_FALTAS"] = df_final[faltas_cols].sum(axis=1)

    fig2 = px.bar(
        df_final,
        x="NOMBRE COMPLETO",
        y="TOTAL_FALTAS",
        text_auto=True,
        title="Total de faltas por trabajador"
    )

    fig2.update_traces(textposition="outside", cliponaxis=False)
    fig2.update_layout(
        height=450,
        xaxis_tickangle=-45,
        margin=dict(t=80,b=140),
        yaxis=dict(dtick=1)
    )

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
