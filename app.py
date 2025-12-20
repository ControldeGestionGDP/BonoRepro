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
# OPCIONES INICIO
# =========================
st.subheader("Seleccione una opción para continuar")
opcion_inicio = st.selectbox(
    "Opciones",
    ["➕ Iniciar desde cero", "📂 Cargar Excel previamente generado"]
)

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

DESCUENTO_FALTAS = {0:1.00,1:0.90,2:0.80,3:0.70,4:0.60}
def factor_faltas(f):
    try:
        f = int(f)
    except:
        return 0.50
    return DESCUENTO_FALTAS.get(f,0.50)

# =========================
# INICIAR DESDE CERO
# =========================
if opcion_inicio == "➕ Iniciar desde cero":
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

        st.session_state.tabla = df.copy()
        st.session_state.df_base = df_base.copy()
        st.success("✅ Cruce de trabajadores realizado")

# =========================
# CARGAR EXCEL PREVIO
# =========================
elif opcion_inicio == "📂 Cargar Excel previamente generado":
    archivo_prev = st.file_uploader("Subir Excel previamente generado", type=["xlsx"])
    if archivo_prev:
        df_prev_raw = pd.read_excel(archivo_prev, sheet_name="BONO_REPRODUCTORAS", dtype=str, header=None)
        fila_inicio = None
        for i, row in df_prev_raw.iterrows():
            if "DNI" in row.values:
                fila_inicio = i
                break
        if fila_inicio is None:
            st.error("❌ No se encontró la tabla de trabajadores en el Excel")
        else:
            df = pd.read_excel(archivo_prev, sheet_name="BONO_REPRODUCTORAS", dtype=str, header=fila_inicio)
            df.columns = df.columns.str.strip().str.upper()
            if "DNI" in df.columns:
                df["DNI"] = df["DNI"].astype(str).str.replace("'", "").str.replace(".0","",regex=False).str.zfill(8)
            else:
                st.error("❌ La columna DNI no existe en el bloque de trabajadores")
            st.session_state.tabla = df.copy()
            st.success("✅ Excel previamente cargado")

# =========================
# SEGUIMOS SI HAY DATOS
# =========================
if "tabla" not in st.session_state:
    st.warning("Sube un archivo de DNIs + Base de trabajadores o un Excel previamente generado")
    st.stop()

# =========================
# AQUÍ SIGUE EL RESTO DEL FLUJO ORIGINAL
# Granjas, lotes, agregar/eliminar trabajador, edición, cálculo y exportación
# =========================

st.write("Aquí continua el flujo original de granjas, lotes, edición y cálculo...")

# =========================
# 🏡 GRANJA
# =========================
st.subheader("🏡 Granja")
if "granjas_base" not in st.session_state:
    st.session_state.granjas_base = ["Chilco I", "Chilco II", "Chilco III", "Chilco IV"]
if "granjas" not in st.session_state:
    st.session_state.granjas = st.session_state.granjas_base.copy()

opcion_granja = st.selectbox("Seleccione la granja", st.session_state.granjas + ["➕ Agregar"])
if opcion_granja == "➕ Agregar":
    nueva_granja = st.text_input("Ingrese nueva granja")
    if nueva_granja and st.button("Agregar granja"):
        st.session_state.granjas.append(nueva_granja)
        st.success("✅ Granja agregada")
        st.rerun()
else:
    st.session_state.granja_seleccionada = opcion_granja
    if opcion_granja not in st.session_state.granjas_base:
        if st.button("🗑️ Eliminar granja"):
            st.session_state.granjas.remove(opcion_granja)
            st.success("✅ Granja eliminada")
            st.rerun()

# =========================
# TIPO DE PROCESO
# =========================
tipo = st.radio("Tipo de proceso", ["PRODUCCIÓN","LEVANTE"], horizontal=True)
reglas = REGLAS_PRODUCCION if tipo == "PRODUCCIÓN" else REGLAS_LEVANTE

# =========================
# LOTES
# =========================
lotes_txt = st.text_input("Lotes (ej: 211-212-213)", "211-212-213")
lotes = [l.strip() for l in lotes_txt.split("-") if l.strip()]
st.subheader("🧬 Configuración por lote")
config_lotes = {}
cols = st.columns(len(lotes))
for i, lote in enumerate(lotes):
    with cols[i]:
        genetica = st.text_input(f"Genética {lote}", "ROSS")
        monto = st.number_input(f"Monto S/ {lote}", min_value=0.0, value=1000.0, step=50.0)
        config_lotes[lote] = {"GENETICA": genetica.upper(), "MONTO": monto}

# =========================
# SESSION STATE TABLA
# =========================
for lote in lotes:
    if f"P_{lote}" not in st.session_state.tabla.columns:
        st.session_state.tabla[f"P_{lote}"] = 0.0
    if f"F_{lote}" not in st.session_state.tabla.columns:
        st.session_state.tabla[f"F_{lote}"] = 0

# =========================
# ORDENAR COLUMNAS
# =========================
base_cols = ["DNI","NOMBRE COMPLETO","CARGO"]
pct_cols = [f"P_{l}" for l in lotes]
faltas_cols = [f"F_{l}" for l in lotes]
st.session_state.tabla = st.session_state.tabla[base_cols + pct_cols + faltas_cols]

# =========================
# SINCRONIZAR df_edit
# =========================
if "df_edit" not in st.session_state:
    st.session_state.df_edit = st.session_state.tabla.copy()
else:
    for col in st.session_state.tabla.columns:
        if col not in st.session_state.df_edit.columns:
            st.session_state.df_edit[col] = st.session_state.tabla[col]
    st.session_state.df_edit = st.session_state.df_edit[st.session_state.tabla.columns]

# =========================
# AGREGAR / ELIMINAR TRABAJADOR
# =========================
st.subheader("➕ Agregar trabajador")
dni_new = st.text_input("DNI", key="dni_preview", placeholder="Ingrese DNI y luego haga click en Agregar")
dni_limpio = dni_new.strip().zfill(8) if dni_new else ""
if dni_limpio:
    if dni_limpio in st.session_state.tabla["DNI"].values:
        st.warning("⚠️ El trabajador ya existe en la tabla")
    elif "df_base" in st.session_state:
        fila_prev = st.session_state.df_base[st.session_state.df_base["DNI"]==dni_limpio]
        if not fila_prev.empty:
            st.markdown(f"<span style='color:#1f77b4; font-weight:bold;'>👤 {fila_prev.iloc[0]['NOMBRE COMPLETO']}</span>", unsafe_allow_html=True)
        else:
            st.error("❌ DNI no encontrado en la base de trabajadores")

if st.button("Agregar trabajador"):
    if not dni_limpio:
        st.warning("⚠️ Ingrese un DNI")
    elif dni_limpio in st.session_state.tabla["DNI"].values:
        st.warning("⚠️ El trabajador ya existe en la tabla")
    elif "df_base" in st.session_state:
        fila = st.session_state.df_base[st.session_state.df_base["DNI"]==dni_limpio]
        if fila.empty:
            st.error("❌ DNI no encontrado en la base de trabajadores")
        else:
            fila = fila.iloc[0]
            nuevo = {"DNI": dni_limpio, "NOMBRE COMPLETO": fila["NOMBRE COMPLETO"], "CARGO": fila["CARGO"]}
            for lote in lotes:
                nuevo[f"P_{lote}"] = 0.0
                nuevo[f"F_{lote}"] = 0
            st.session_state.tabla = pd.concat([st.session_state.tabla, pd.DataFrame([nuevo])], ignore_index=True)
            st.session_state.df_edit = st.session_state.tabla.copy()
            st.success("✅ Trabajador agregado")
            st.rerun()

st.subheader("➖ Eliminar trabajador")
eliminar_dni = st.text_input("DNI a eliminar").strip().zfill(8)
if st.button("Eliminar trabajador"):
    st.session_state.tabla = st.session_state.tabla[st.session_state.tabla["DNI"]!=eliminar_dni]
    st.session_state.df_edit = st.session_state.tabla.copy()
    st.success("✅ Trabajador eliminado")

# =========================
# EDITAR TABLA
# =========================
st.subheader("✍️ Registro por trabajador y lote")
with st.form("form_edicion"):
    df_edit = st.data_editor(st.session_state.df_edit, use_container_width=True)
    if st.form_submit_button("💾 Actualizar tabla"):
        st.session_state.tabla = df_edit.copy()
        st.session_state.df_edit = df_edit.copy()
        st.success("✅ Tabla actualizada")

# =========================
# CÁLCULO FINAL
# =========================
df_final = st.session_state.tabla.copy()
pagos = []
for lote in lotes:
    col = f"PAGO_{lote}"
    df_final[col] = df_final.apply(
        lambda r: round(
            reglas.get(str(r["CARGO"]).upper(),0)
            * config_lotes[lote]["MONTO"]
            * (float(r[f"P_{lote}"])/100)
            * factor_faltas(r[f"F_{lote}"]),
            2
        ),
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
# GRÁFICO
# =========================
st.subheader("📊 Distribución de bonos por trabajador")
fig = px.bar(df_final, x="NOMBRE COMPLETO", y="TOTAL S/", text="TOTAL S/", title="Bono total por trabajador")
fig.update_traces(texttemplate="S/ %{text:,.2f}", textposition="outside", cliponaxis=False)
fig.update_layout(xaxis_tickangle=-45, height=550, margin=dict(t=100), yaxis=dict(rangemode="tozero"))
st.plotly_chart(fig, use_container_width=True)

# =========================
# EXPORTAR EXCEL
# =========================
output = BytesIO()
with pd.ExcelWriter(output, engine="openpyxl") as writer:
    sheet_name = "BONO_REPRODUCTORAS"
    fila_actual = 0

    # Encabezado
    encabezado = pd.DataFrame({
        "Campo":["Granja","Tipo de Proceso","Lotes","Fecha de Generación"],
        "Valor":[st.session_state.get("granja_seleccionada",""),tipo,",".join(lotes),pd.Timestamp.now().strftime("%Y-%m-%d %H:%M")]
    })
    encabezado.to_excel(writer, sheet_name=sheet_name, index=False, startrow=fila_actual)
    fila_actual += len(encabezado)+2

    # Configuración de lotes
    df_lotes = pd.DataFrame([{"Lote": l, "Genética": config_lotes[l]["GENETICA"], "Monto S/": config_lotes[l]["MONTO"]} for l in lotes])
    df_lotes.to_excel(writer, sheet_name=sheet_name, index=False, startrow=fila_actual)
    fila_actual += len(df_lotes)+3

    # Detalle trabajadores
    df_final.to_excel(writer, sheet_name=sheet_name, index=False, startrow=fila_actual)

st.download_button("📥 Descargar archivo final", data=output.getvalue(), file_name="bono_reproductoras_final.xlsx")

