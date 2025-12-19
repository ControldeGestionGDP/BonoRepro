import streamlit as st
import pandas as pd
from io import BytesIO

# =========================
# CONFIGURACIÓN GLOBAL
# =========================
st.set_page_config(page_title="Bono Reproductoras GDP", layout="wide")

# =========================
# PORTADA
# =========================
if "ingresar" not in st.session_state:
    st.session_state.ingresar = False

if not st.session_state.ingresar:
    st.markdown(
        """
        <div style='text-align:center; padding-top:100px'>
            <h1>🐔 BONO REPRODUCTORAS GDP</h1>
            <h3>Sistema de cálculo y distribución de bonos</h3>
            <p style="color:gray;">Desarrollado por Gerencia de Control de Gestión</p>
        </div>
        """,
        unsafe_allow_html=True
    )
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
    "GALPONERO": 1.00, "AYUDANTE GALPONERO": 0.125, "VOLANTE DESCANSERO": 0.125,
    "VOLANTE ALIMENTO": 0.125, "BIOSEGURIDAD": 0.0625, "GUARDIANES": 0.0625,
    "CAPORAL": 0.125, "SUPERVISOR": 1.00, "MANTENIMIENTO": 0.0,
    "GRADING": 0.08, "VACUNADORES": 0.07
}
REGLAS_LEVANTE = REGLAS_PRODUCCION.copy()

# =========================
# DESCUENTO POR FALTAS
# =========================
DESCUENTO_FALTAS = {0:1.0, 1:0.9, 2:0.8, 3:0.7, 4:0.6}
def factor_faltas(f):
    try: f=int(f)
    except: return 0.5
    return DESCUENTO_FALTAS.get(f,0.5)

# =========================
# CARGA DE ARCHIVOS
# =========================
archivo_dni = st.file_uploader("📄 Excel con DNIs", type=["xlsx"])
archivo_base = st.file_uploader("📊 Base de trabajadores", type=["xlsx"])

if archivo_dni and archivo_base:

    df_dni = pd.read_excel(archivo_dni,dtype=str)
    df_base = pd.read_excel(archivo_base,dtype=str)
    df_dni.columns = df_dni.columns.str.strip().str.upper()
    df_base.columns = df_base.columns.str.strip().str.upper()

    def limpiar_dni(s):
        return s.astype(str).str.replace("'", "", regex=False).str.replace(".0","",regex=False).str.strip().str.zfill(8)

    df_dni["DNI"] = limpiar_dni(df_dni["DNI"])
    df_base["DNI"] = limpiar_dni(df_base["DNI"])
    df_base = df_base.drop_duplicates("DNI")

    df = df_dni.merge(df_base[["DNI","NOMBRE COMPLETO","CARGO"]], on="DNI", how="left")

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
    # INICIALIZAR SESSION_STATE
    # =========================
    if "tabla" not in st.session_state:
        st.session_state.tabla = df.copy()
        for lote in lotes:
            st.session_state.tabla[f"%_{lote}"] = 0.0
            st.session_state.tabla[f"F_{lote}"] = 0

    # =========================
    # AGREGAR / ELIMINAR TRABAJADOR
    # =========================
    st.subheader("➕ Agregar / ➖ Eliminar trabajador")
    with st.form("form_agregar", clear_on_submit=True):
        dni_new = st.text_input("DNI")
        if dni_new.strip().zfill(8) in df_base["DNI"].values:
            fila = df_base[df_base["DNI"]==dni_new.strip().zfill(8)].iloc[0]
            st.info(f"Nombre: {fila['NOMBRE COMPLETO']} | Cargo: {fila['CARGO']}")
        submitted = st.form_submit_button("Agregar trabajador")
        if submitted:
            dni_new = dni_new.strip().zfill(8)
            if dni_new not in st.session_state.tabla["DNI"].values:
                fila = df_base[df_base["DNI"]==dni_new].iloc[0]
                nuevo = {"DNI":dni_new,"NOMBRE COMPLETO":fila["NOMBRE COMPLETO"],"CARGO":fila["CARGO"]}
                for lote in lotes:
                    nuevo[f"%_{lote}"] = 0.0
                    nuevo[f"F_{lote}"] = 0
                st.session_state.tabla = pd.concat([st.session_state.tabla,pd.DataFrame([nuevo])], ignore_index=True)

    eliminar_dni = st.text_input("DNI a eliminar")
    if st.button("Eliminar trabajador"):
        eliminar_dni = eliminar_dni.strip().zfill(8)
        if eliminar_dni in st.session_state.tabla["DNI"].values:
            st.session_state.tabla = st.session_state.tabla[st.session_state.tabla["DNI"]!=eliminar_dni]
            st.success("✅ Trabajador eliminado")

    # =========================
    # EDITAR PARTICIPACIÓN Y FALTAS
    # =========================
    st.subheader("✍️ Registro por trabajador y lote")
    def actualizar_tabla():
        st.session_state.tabla = df_edit.copy()

    df_edit = st.data_editor(
        st.session_state.tabla,
        use_container_width=True,
        num_rows="fixed",
        key="data_editor_tabla",
        on_change=actualizar_tabla
    )

    # =========================
    # CÁLCULO DE PAGOS
    # =========================
    df_final = st.session_state.tabla.copy()
    columnas_pago = []
    for lote in lotes:
        def pago_lote(row):
            cargo = str(row["CARGO"]).upper()
            pct_cargo = reglas.get(cargo,0)
            monto = config_lotes[lote]["MONTO"]
            participacion = float(row[f"%_{lote}"])/100
            faltas = row[f"F_{lote}"]
            if participacion <= 0: return 0.0
            return round(pct_cargo*monto*participacion*factor_faltas(faltas),2)
        col_pago = f"PAGO_{lote}"
        df_final[col_pago] = df_final.apply(pago_lote, axis=1)
        columnas_pago.append(col_pago)

    df_final["TOTAL S/"] = df_final[columnas_pago].sum(axis=1)

    # =========================
    # RESULTADO FINAL
    # =========================
    st.subheader("💰 Resultado final")
    st.dataframe(df_final,use_container_width=True)

    # =========================
    # EXPORTACIÓN
    # =========================
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df_final.to_excel(writer,index=False)
    output.seek(0)
    st.download_button(
        "📥 Descargar archivo final",
        data=output,
        file_name="bono_reproductoras_final.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
