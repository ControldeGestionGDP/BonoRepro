import streamlit as st
import pandas as pd
from io import BytesIO

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
DESCUENTO_FALTAS = {
    0: 1.00,
    1: 0.90,
    2: 0.80,
    3: 0.70,
    4: 0.60
}

def factor_faltas(f):
    try:
        f = int(f)
    except:
        return 0.50
    return DESCUENTO_FALTAS.get(f, 0.50)

# =========================
# APP PRINCIPAL
# =========================
st.title("🐔 BONO REPRODUCTORAS GDP")
st.markdown("""
**Flujo**
1. Subir DNIs  
2. Subir base de trabajadores  
3. Definir lotes y montos  
4. Registrar participación y faltas  
5. Obtener cálculo final del bono  
""")

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
    lotes_txt = st.text_input("Lotes (ej: 211-212-213)","211-212-213")
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
        # Inicializar columnas P y F
        for lote in lotes:
            st.session_state.tabla[f"P_{lote}"] = 0.0
            st.session_state.tabla[f"F_{lote}"] = 0
    else:
        # Agregar nuevas columnas si aparecen nuevos lotes
        for lote in lotes:
            if f"P_{lote}" not in st.session_state.tabla.columns:
                st.session_state.tabla[f"P_{lote}"] = 0.0
            if f"F_{lote}" not in st.session_state.tabla.columns:
                st.session_state.tabla[f"F_{lote}"] = 0
        # Eliminar columnas de lotes que ya no existan
        for col in list(st.session_state.tabla.columns):
            if col.startswith("P_") or col.startswith("F_"):
                lote_col = col.split("_")[1]
                if lote_col not in lotes:
                    st.session_state.tabla.drop(columns=[col], inplace=True)

    # =========================
    # ORDENAR COLUMNAS
    # =========================
    base_cols = ["DNI","NOMBRE COMPLETO","CARGO"]
    pct_cols = [f"P_{l}" for l in lotes if f"P_{l}" in st.session_state.tabla.columns]
    faltas_cols = [f"F_{l}" for l in lotes if f"F_{l}" in st.session_state.tabla.columns]
    otras_cols = [c for c in st.session_state.tabla.columns if c not in base_cols + pct_cols + faltas_cols]
    st.session_state.tabla = st.session_state.tabla[base_cols + pct_cols + faltas_cols + otras_cols]

    # =========================
    # AGREGAR / ELIMINAR TRABAJADOR
    # =========================
    st.subheader("➕ Agregar / ➖ Eliminar trabajador")

    with st.form("agregar_trabajador", clear_on_submit=True):
        dni_new = st.text_input("DNI")
        # PREVISUALIZAR DATOS AL INGRESAR DNI
        nombre_new = ""
        cargo_new = ""
        if dni_new.strip().zfill(8) in df_base["DNI"].values:
            fila = df_base[df_base["DNI"]==dni_new.strip().zfill(8)].iloc[0]
            nombre_new = fila["NOMBRE COMPLETO"]
            cargo_new = fila["CARGO"]
            st.info(f"Nombre: {nombre_new} | Cargo: {cargo_new}")
        nombre_input = st.text_input("Nombre completo", value=nombre_new)
        cargo_input = st.text_input("Cargo", value=cargo_new)
        submitted = st.form_submit_button("Agregar trabajador")
        if submitted:
            dni_new = dni_new.strip().zfill(8)
            if dni_new not in st.session_state.tabla["DNI"].values:
                nuevo = {"DNI":dni_new,"NOMBRE COMPLETO":nombre_input,"CARGO":cargo_input}
                for lote in lotes:
                    nuevo[f"P_{lote}"] = 0.0
                    nuevo[f"F_{lote}"] = 0
                st.session_state.tabla = pd.concat([st.session_state.tabla,pd.DataFrame([nuevo])],ignore_index=True)
                st.success("✅ Trabajador agregado")

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

    # Función para actualizar session_state al cambiar el Data Editor
    def actualizar_tabla():
        st.session_state.tabla = st.session_state.df_edit.copy()

    # Copiar la tabla a una variable de session_state para editar
    if "df_edit" not in st.session_state:
        st.session_state.df_edit = st.session_state.tabla.copy()

    # Data editor con on_change para guardar cambios al instante
    st.data_editor(
        st.session_state.df_edit,
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
            participacion = float(row[f"P_{lote}"])/100
            faltas = row[f"F_{lote}"]
            if participacion<=0: return 0.0
            return round(pct_cargo*monto*participacion*factor_faltas(faltas),2)
        col_pago = f"PAGO_{lote}"
        df_final[col_pago] = df_final.apply(pago_lote,axis=1)
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
        df_final.to_excel(writer, index=False)
    output.seek(0)

    st.download_button(
        "📥 Descargar archivo final",
        data=output,
        file_name="bono_reproductoras_final.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
