import streamlit as st
import pandas as pd
from io import BytesIO
import plotly.express as px
import smtplib
from email.message import EmailMessage

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

    col1, col2, col3 = st.columns([1, 2, 1])
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

DESCUENTO_FALTAS = {0: 1.0, 1: 0.90, 2: 0.80, 3: 0.70, 4: 0.60}

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
            df_base[["DNI", "NOMBRE COMPLETO", "CARGO"]],
            on="DNI",
            how="left"
        )

        st.success("✅ Cruce de trabajadores realizado")

elif opcion_inicio == "📂 Cargar Excel previamente generado":
    archivo_prev = st.file_uploader("📂 Subir Excel previamente generado", type=["xlsx"])

    if archivo_prev:
        raw = pd.read_excel(archivo_prev, sheet_name="BONO_REPRODUCTORAS", header=None)

        encabezado = raw.iloc[0:4, 0:2]
        encabezado.columns = ["CAMPO", "VALOR"]
        encabezado["CAMPO"] = encabezado["CAMPO"].str.upper()

        st.session_state.granja_seleccionada = encabezado.loc[
            encabezado["CAMPO"] == "GRANJA", "VALOR"
        ].values[0]

        tipo = encabezado.loc[
            encabezado["CAMPO"] == "TIPO DE PROCESO", "VALOR"
        ].values[0]

        lotes_txt = encabezado.loc[
            encabezado["CAMPO"] == "LOTES", "VALOR"
        ].values[0]

        lotes = [l.strip() for l in lotes_txt.split(",")]

        fila_lotes = raw[raw.iloc[:, 0] == "Lote"].index[0]
        df_lotes = pd.read_excel(
            archivo_prev,
            sheet_name="BONO_REPRODUCTORAS",
            header=fila_lotes
        )

        config_lotes = {}
        for _, r in df_lotes.iterrows():
            if pd.isna(r["Lote"]):
                continue

            monto_limpio = str(r["Monto S/"]).replace(",", "").strip()
            try:
                monto = float(monto_limpio)
            except:
                monto = 0.0

            config_lotes[str(r["Lote"]).strip()] = {
                "GENETICA": str(r["Genética"]).upper().strip(),
                "MONTO": monto
            }

        fila_tabla = raw[raw.iloc[:, 0] == "DNI"].index[0]
        df = pd.read_excel(
            archivo_prev,
            sheet_name="BONO_REPRODUCTORAS",
            header=fila_tabla,
            dtype=str
        )

        df.columns = df.columns.str.strip().str.upper()
        df["DNI"] = (
            df["DNI"]
            .str.replace("'", "")
            .str.replace(".0", "", regex=False)
            .str.zfill(8)
        )

        st.session_state.tabla = df.copy()
        st.session_state.df_edit = df.copy()
        st.session_state.config_lotes = config_lotes
        st.session_state.lotes = lotes
        st.session_state.tipo = tipo

        st.success("✅ Excel cargado y reconstruido correctamente")

# =========================
# SI NO HAY DATOS
# =========================
if df is None:
    st.warning("Suba un archivo para continuar")
    st.stop()

# =========================
# CONTROL DE RESULTADOS
# =========================
if "mostrar_resultados" not in st.session_state:
    st.session_state.mostrar_resultados = False

# =========================
# EDICIÓN
# =========================
st.subheader("✍️ Registro por trabajador y lote")

with st.form("form_edicion"):
    df_edit = st.data_editor(st.session_state.df_edit, use_container_width=True)
    if st.form_submit_button("💾 Actualizar tabla"):
        st.session_state.tabla = df_edit.copy()
        st.session_state.df_edit = df_edit.copy()
        st.session_state.mostrar_resultados = True
        st.success("✅ Tabla actualizada")

# =========================
# RESULTADOS
# =========================
if st.session_state.mostrar_resultados:

    df_final = st.session_state.tabla.copy()
    pagos = []

    for lote in st.session_state.lotes:
        col = f"PAGO_{lote}"
        df_final[col] = df_final.apply(
            lambda r: round(
                REGLAS_PRODUCCION.get(str(r["CARGO"]).upper(), 0)
                * st.session_state.config_lotes[lote]["MONTO"]
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
        df_final.to_excel(writer, sheet_name="BONO_REPRODUCTORAS", index=False)

    st.download_button(
        "📥 Descargar archivo final",
        data=output.getvalue(),
        file_name="Bono_Reproductoras_Final.xlsx"
    )

    # =========================
    # ENVÍO DE CORREO
    # =========================
    st.subheader("📧 Enviar por correo")

    correo_destino = st.text_input("Correo destino")
    asunto = st.text_input("Asunto", "Resultado Bono Reproductoras GDP")
    mensaje = st.text_area("Mensaje", "Adjunto encontrará el resultado del bono generado.")

    if st.button("📨 Enviar correo"):
        msg = EmailMessage()
        msg["From"] = st.secrets["EMAIL_USER"]
        msg["To"] = correo_destino
        msg["Subject"] = asunto
        msg.set_content(mensaje)

        msg.add_attachment(
            output.getvalue(),
            maintype="application",
            subtype="vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            filename="bono_reproductoras.xlsx"
        )

        with smtplib.SMTP("smtp.office365.com", 587) as smtp:
            smtp.starttls()
            smtp.login(
                st.secrets["EMAIL_USER"],
                st.secrets["EMAIL_PASS"]
            )
            smtp.send_message(msg)

        st.success("✅ Correo enviado correctamente")
