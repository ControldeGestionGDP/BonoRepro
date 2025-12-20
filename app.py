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
# ELECCIÓN DE OPCIÓN DE INICIO
# =========================
st.subheader("Seleccione cómo desea iniciar")
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

DESCUENTO_FALTAS = {0:1.0, 1:0.90, 2:0.80, 3:0.70, 4:0.60}
def factor_faltas(f):
    try:
        f = int(f)
    except:
        return 0.50
    return DESCUENTO_FALTAS.get(f, 0.50)

# =========================
# CARGA DE ARCHIVOS
# =========================
df = None
df_base = None
lotes_detectados = "211-212-213"  # valor por defecto

def limpiar_dni_col(df):
    df["DNI"] = (
        df["DNI"].astype(str)
        .str.replace("'", "", regex=False)
        .str.replace(".0", "", regex=False)
        .str.strip()
        .str.zfill(8)
    )
    return df

if opcion_inicio == "➕ Iniciar desde cero":
    archivo_dni = st.file_uploader("📄 Excel con DNIs", type=["xlsx"])
    archivo_base = st.file_uploader("📊 Base de trabajadores", type=["xlsx"])

    if archivo_dni and archivo_base:
        df_dni = pd.read_excel(archivo_dni, dtype=str)
        df_base = pd.read_excel(archivo_base, dtype=str)

        df_dni.columns = df_dni.columns.str.strip().str.upper()
        df_base.columns = df_base.columns.str.strip().str.upper()

        df_dni = limpiar_dni_col(df_dni)
        df_base = limpiar_dni_col(df_base)
        df_base = df_base.drop_duplicates("DNI")

        df = df_dni.merge(
            df_base[["DNI", "NOMBRE COMPLETO", "CARGO"]],
            on="DNI",
            how="left"
        )

        st.success("✅ Cruce de trabajadores realizado")

elif opcion_inicio == "📂 Cargar Excel previamente generado":
    archivo_prev = st.file_uploader("📂 Subir Excel previamente generado", type=["xlsx"])
    if archivo_prev:
        df_prev_raw = pd.read_excel(
            archivo_prev,
            sheet_name="BONO_REPRODUCTORAS",
            header=None,
            dtype=str
        )

        fila_inicio = None
        for i, row in df_prev_raw.iterrows():
            if row.astype(str).str.contains("DNI", na=False).any():
                fila_inicio = i
                break

        if fila_inicio is None:
            st.error("❌ No se encontró la tabla de trabajadores en el Excel")
        else:
            df_cargado = pd.read_excel(
                archivo_prev,
                sheet_name="BONO_REPRODUCTORAS",
                header=fila_inicio,
                dtype=str
            )
            df_cargado.columns = df_cargado.columns.str.strip().str.upper()
            df_cargado = limpiar_dni_col(df_cargado)

            # Quitar columnas calculadas
            columnas_validas = [
                c for c in df_cargado.columns
                if not (c.startswith("PAGO_") or c == "TOTAL S/")
            ]
            df = df_cargado[columnas_validas].copy()

            # Detectar lotes
            lotes_list = sorted([c.replace("P_", "") for c in df.columns if c.startswith("P_")])
            if lotes_list:
                lotes_detectados = "-".join(lotes_list)

            st.success(f"✅ Excel cargado. Lotes detectados: {lotes_detectados}")

# =========================
# VALIDACIÓN
# =========================
if df is None:
    st.warning("Suba un archivo para continuar")
    st.stop()

# =========================
# GRANJA
# =========================
st.subheader("🏡 Granja")
if "granjas_base" not in st.session_state:
    st.session_state.granjas_base = ["Chilco I", "Chilco II", "Chilco III", "Chilco IV"]

if "granjas" not in st.session_state:
    st.session_state.granjas = st.session_state.granjas_base.copy()

opcion_granja = st.selectbox(
    "Seleccione la granja",
    st.session_state.granjas + ["➕ Agregar"]
)

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
# CONFIGURACIÓN DE PROCESO Y LOTES
# =========================
tipo = st.radio("Tipo de proceso", ["PRODUCCIÓN", "LEVANTE"], horizontal=True)
reglas = REGLAS_PRODUCCION if tipo == "PRODUCCIÓN" else REGLAS_LEVANTE

lotes_txt = st.text_input("Lotes (ej: 211-212-213)", lotes_detectados)
lotes = [l.strip() for l in lotes_txt.split("-") if l.strip()]

# =========================
# CONFIGURACIÓN POR LOTE
# =========================
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
if "tabla" not in st.session_state or opcion_inicio == "📂 Cargar Excel previamente generado":
    st.session_state.tabla = df.copy()

for lote in lotes:
    if f"P_{lote}" not in st.session_state.tabla.columns:
        st.session_state.tabla[f"P_{lote}"] = 0.0
    if f"F_{lote}" not in st.session_state.tabla.columns:
        st.session_state.tabla[f"F_{lote}"] = 0

base_cols = ["DNI", "NOMBRE COMPLETO", "CARGO"]
pct_cols = [f"P_{l}" for l in lotes]
faltas_cols = [f"F_{l}" for l in lotes]
st.session_state.tabla = st.session_state.tabla[base_cols + pct_cols + faltas_cols]

# =========================
# EDICIÓN
# =========================
st.subheader("✍️ Registro por trabajador y lote")
df_edit = st.data_editor(st.session_state.tabla, use_container_width=True)
st.session_state.tabla = df_edit.copy()

# =========================
# CÁLCULO FINAL
# =========================
df_final = st.session_state.tabla.copy()
pagos = []

for lote in lotes:
    col = f"PAGO_{lote}"
    df_final[col] = df_final.apply(
        lambda r: round(
            reglas.get(str(r["CARGO"]).upper(), 0)
            * config_lotes[lote]["MONTO"]
            * (float(r[f"P_{lote}"]) / 100)
            * factor_faltas(r[f"F_{lote}"]),
            2
        ),
        axis=1
    )
    pagos.append(col)

df_final["TOTAL S/"] = df_final[pagos].sum(axis=1)

st.subheader("💰 Resultado final")
st.dataframe(df_final, use_container_width=True)

# =========================
# EXPORTAR
# =========================
output = BytesIO()
with pd.ExcelWriter(output, engine="openpyxl") as writer:
    sheet = "BONO_REPRODUCTORAS"
    fila = 0

    encabezado = pd.DataFrame({
        "Campo": ["Granja", "Tipo de Proceso", "Lotes", "Fecha de Generación"],
        "Valor": [
            st.session_state.get("granja_seleccionada", ""),
            tipo,
            ", ".join(lotes),
            pd.Timestamp.now().strftime("%Y-%m-%d %H:%M")
        ]
    })
    encabezado.to_excel(writer, sheet_name=sheet, index=False, startrow=fila)
    fila += len(encabezado) + 2

    df_lotes = pd.DataFrame([
        {"Lote": l, "Genética": config_lotes[l]["GENETICA"], "Monto S/": config_lotes[l]["MONTO"]}
        for l in lotes
    ])
    df_lotes.to_excel(writer, sheet_name=sheet, index=False, startrow=fila)
    fila += len(df_lotes) + 3

    df_final.to_excel(writer, sheet_name=sheet, index=False, startrow=fila)

st.download_button(
    "📥 Descargar archivo final",
    data=output.getvalue(),
    file_name="bono_reproductoras_final.xlsx"
)
