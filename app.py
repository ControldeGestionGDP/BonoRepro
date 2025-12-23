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

if "ver_manual" not in st.session_state:
    st.session_state.ver_manual = False

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if "ver_powerbi" not in st.session_state:
    st.session_state.ver_powerbi = False

# 🔑 ROL DEL USUARIO (MUY IMPORTANTE)
if "rol" not in st.session_state:
    st.session_state.rol = None

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
# AUTENTICACIÓN BÁSICA
# =========================
if st.session_state.ingresar and not st.session_state.autenticado:

    st.markdown("""
    <style>
    .login-card {
        max-width: 420px;
        margin: auto;
        margin-top: 80px;
        padding: 35px;
        border-radius: 12px;
        background-color: #ffffff;
        box-shadow: 0px 8px 25px rgba(0,0,0,0.12);
        text-align: center;
    }
    .login-title {
        font-size: 26px;
        font-weight: 700;
        margin-bottom: 10px;
    }
    .login-subtitle {
        font-size: 14px;
        color: #6b7280;
        margin-bottom: 25px;
    }
    </style>

    <div class="login-card">
        <div class="login-title">🔐 Iniciar sesión</div>
        <div class="login-subtitle">
            Acceso exclusivo para personal autorizado
        </div>
    </div>
    """, unsafe_allow_html=True)

    with st.container():
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            user = st.text_input("👤 Usuario")
            pwd = st.text_input("🔑 Contraseña", type="password")

            if st.button("➡️ Ingresar", use_container_width=True):

                rol_usuario = None

                # ---- CONTROL DE GESTIÓN ----
                if (
                    user == st.secrets["control"]["usuario"]
                    and pwd == st.secrets["control"]["password"]
                ):
                    rol_usuario = st.secrets["control"]["rol"]

                # ---- USUARIO NORMAL ----
                elif (
                    user == st.secrets["auth"]["usuario"]
                    and pwd == st.secrets["auth"]["password"]
                ):
                    rol_usuario = st.secrets["auth"]["rol"]

                # ---- VALIDACIÓN FINAL ----
                if rol_usuario:
                    st.session_state.autenticado = True
                    st.session_state.rol = rol_usuario
                    st.session_state.ver_manual = True
                    st.success("✅ Acceso autorizado")
                    st.rerun()
                else:
                    st.error("❌ Usuario o contraseña incorrectos")

    st.stop()


# =========================
# MANUAL DE INSTRUCCIONES
# =========================
if st.session_state.ingresar and st.session_state.ver_manual:

    st.markdown("## 📘 Manual de Uso – Bono Reproductoras GDP")

    # 🔴 REQUISITO PREVIO OBLIGATORIO
    st.warning(
        "⚠️ **REQUISITO PREVIO OBLIGATORIO**\n\n"
        "**Antes de iniciar en el sistema:**\n"
        "Al cerrar una granja, comuníquese con el equipo de **Control de Gestión**.\n\n"
        "**Ellos deben realizar previamente:**\n"
        "• El ingreso de los **Huevos Bomba**\n"
        "• La definición de los **montos base por granja y lote**\n\n"
        "Solo después de este paso se debe proceder con el cálculo individual."
    )

    st.markdown("""
    ---

    ### 🚀 Guía de Uso del Sistema

    #### 1️⃣ Acceso e Inicio
    Al ingresar a la aplicación encontrará dos opciones:

    - **➕ Iniciar desde cero**  
      Use esta opción si es la primera vez que procesa el bono del periodo.

    - **📂 Cargar Excel previamente generado**  
      Ideal para continuar un trabajo guardado o corregir un archivo descargado.

    #### 2️⃣ Carga de Datos (inicio desde cero)
    Deberá subir dos archivos Excel obligatorios:

    - **Excel con DNIs:** listado del personal participante  
    - **Base de trabajadores:** maestro general de personal  

    👉 El sistema realiza un **cruce automático** para validar nombres y cargos.

    #### 3️⃣ Configuración de Granja y Lotes
    - Seleccione la **Granja**
    - Defina el **Tipo de Proceso** (PRODUCCIÓN o LEVANTE)
    - Ingrese los **Lotes** (ejemplo: 211-212-213)
    - Confirme los datos para desbloquear el sistema

    #### 4️⃣ Configuración Económica y Genética
    Para cada lote:
    - **Genética:** por defecto ROSS
    - **Monto S/:** monto total asignado (habilitado por Control de Gestión)

    #### 5️⃣ Gestión de Personal
    - Agregar o eliminar trabajadores por DNI
    - Registrar:
        - **P_[Lote]:** porcentaje de participación
        - **F_[Lote]:** faltas (con descuento automático)

    💡 **Importante:** siempre presione **💾 Actualizar tabla** luego de editar.

    #### 6️⃣ Resultados y Exportación
    - Tabla final de pagos
    - Gráficos de distribución
    - Descarga de Excel con formato oficial
    - Envío automático por correo corporativo
    ---
    """)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("✅ Entendido, continuar al sistema", use_container_width=True):
            st.session_state.ver_manual = False
            st.rerun()

    st.stop()

# =========================
# BARRA LATERAL – POWER BI
# =========================
with st.sidebar:

    st.markdown("## 📊 Validación de Bonos")

    # 🔐 SOLO CONTROL DE GESTIÓN
    if st.session_state.get("rol") == "control":

        st.caption("Acceso exclusivo – Control de Gestión")

        if not st.session_state.ver_powerbi:
            if st.button("📈 Abrir Power BI", use_container_width=True):
                st.session_state.ver_powerbi = True
                st.rerun()
        else:
            if st.button("❌ Cerrar Power BI", use_container_width=True):
                st.session_state.ver_powerbi = False
                st.rerun()

        st.markdown("---")
        st.markdown(
            "🔎 Use este tablero para **validar huevos bomba, "
            "montos y coherencia con reportes oficiales**."
        )

    # 👤 USUARIOS NORMALES
    else:
        st.info(
            "🔒 El tablero Power BI es de uso exclusivo "
            "del equipo de Control de Gestión."
        )


# =========================
# ELECCIÓN DE OPCIÓN DE INICIO
# =========================
st.subheader("Seleccione cómo desea iniciar")
opcion_inicio = st.selectbox(
    "Opciones",
    ["➕ Iniciar desde cero", "📂 Cargar Excel previamente generado"]
)


# =========================
# VISUALIZACIÓN POWER BI
# =========================
if st.session_state.ver_powerbi:

    st.markdown("## 📊 Power BI – Histórico de Bonos")
    st.info(
        "📌 Este tablero es una referencia visual oficial. "
        "Los cálculos y validaciones se realizan en el sistema."
    )

    st.components.v1.iframe(
        src="https://app.powerbi.com/reportEmbed?reportId=07ff7776-f12c-4192-be31-08cc522358d1&autoAuth=true&ctid=42fc96b3-c018-482d-8ada-cab81720489e",
        height=650,
        scrolling=True
    )

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

DESCUENTO_FALTAS = {0:1.0, 1:0.90, 2:0.80, 3:0.70, 4:0.60}
def factor_faltas(f):
    try:
        f = int(f)
    except:
        return 0.50
    return DESCUENTO_FALTAS.get(f, 0.50)

# =========================
# CARGA DE ARCHIVOS SEGÚN OPCIÓN
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
            df_base[["DNI","NOMBRE COMPLETO","CARGO"]],
            on="DNI",
            how="left"
        )
        st.success("✅ Cruce de trabajadores realizado")

elif opcion_inicio == "📂 Cargar Excel previamente generado":
    archivo_prev = st.file_uploader("📂 Subir Excel previamente generado", type=["xlsx"])
    if archivo_prev:
        raw = pd.read_excel(archivo_prev, sheet_name="BONO_REPRODUCTORAS", header=None)

        # ---------- 1️⃣ Encabezado ----------
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

        # ---------- 2️⃣ Configuración de lotes ----------
        fila_lotes = raw[raw.iloc[:,0] == "Lote"].index[0]
        df_lotes = pd.read_excel(
            archivo_prev,
            sheet_name="BONO_REPRODUCTORAS",
            header=fila_lotes
        )
                # ---------- 2️⃣ Configuración de lotes ----------
        fila_lotes = raw[raw.iloc[:,0] == "Lote"].index[0]
        df_lotes = pd.read_excel(
            archivo_prev,
            sheet_name="BONO_REPRODUCTORAS",
            header=fila_lotes
        )

        config_lotes = {}
        for _, r in df_lotes.iterrows():

            if pd.isna(r["Lote"]):
                continue  # salta filas vacías

            monto_limpio = (
                str(r["Monto S/"])
                .replace(",", "")
                .strip()
            )

            try:
                monto = float(monto_limpio)
            except:
                monto = 0.0

            config_lotes[str(r["Lote"]).strip()] = {
                "GENETICA": str(r["Genética"]).upper().strip(),
                "MONTO": monto
            }

        # ---------- 3️⃣ Tabla trabajadores ----------
        fila_tabla = raw[raw.iloc[:,0] == "DNI"].index[0]
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
            .str.replace(".0","",regex=False)
            .str.zfill(8)
        )

        # Guardar en session_state
        st.session_state.tabla = df.copy()
        st.session_state.df_edit = df.copy()
        st.session_state.config_lotes = config_lotes
        st.session_state.lotes = lotes
        st.session_state.tipo = tipo

        st.success("✅ Excel cargado y reconstruido correctamente")

# =========================
# SI NO HAY DATOS, DETENER
# =========================
if df is None:
    st.warning("Suba un archivo para continuar")
    st.stop()

# =========================
# =========================
# FLUJO ORIGINAL COMPLETO
# =========================
# =========================

# 🏡 Granja
st.subheader("🏡 Granja")
st.warning(
    "⚠️ Una vez confirmado, no se recomienda cambiar Granja, Tipo de proceso y Lotes "
    "porque afectaría los registros ingresados."
)
if "granjas_base" not in st.session_state:
    st.session_state.granjas_base = ["Chilco I", "Chilco II", "Chilco III", "Chilco IV"]

if "granjas" not in st.session_state:
    st.session_state.granjas = st.session_state.granjas_base.copy()

# 🔑 SI VIENE UNA GRANJA DEL EXCEL Y NO EXISTE, SE AGREGA
if "granja_seleccionada" in st.session_state:
    granja_excel = st.session_state.granja_seleccionada
    if granja_excel not in st.session_state.granjas:
        st.session_state.granjas.append(granja_excel)

granjas_opciones = st.session_state.granjas + ["➕ Agregar"]

if "granja_seleccionada" in st.session_state and st.session_state.granja_seleccionada in granjas_opciones:
    index_granja = granjas_opciones.index(st.session_state.granja_seleccionada)
else:
    index_granja = 0

opcion_granja = st.selectbox(
    "Seleccione la granja",
    granjas_opciones,
    index=index_granja
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
        if st.button("🗑️ Eliminar granja", key="btn_eliminar_granja"):
            st.session_state.granjas.remove(opcion_granja)

            # 🔑 limpiar selección actual
            st.session_state.granja_seleccionada = st.session_state.granjas_base[0]

            st.success(f"✅ Granja '{opcion_granja}' eliminada correctamente")
            st.rerun()

st.markdown("""
<div style="
    border: 2px solid #2563eb;
    border-radius: 12px;
    padding: 18px;
    background-color: #eff6ff;
    margin-bottom: 15px;
">
    <h3 style="color:#1e3a8a; margin-bottom:5px;">
        🔀 Tipo de proceso (DECISIÓN CLAVE)
    </h3>
    <p style="color:#334155; margin-top:0;">
        Esta selección define los módulos, campos y cálculos que se habilitarán.
    </p>
</div>
""", unsafe_allow_html=True)

tipo_opciones = ["PRODUCCIÓN", "LEVANTE"]

if "tipo" in st.session_state and st.session_state.tipo in tipo_opciones:
    index_tipo = tipo_opciones.index(st.session_state.tipo)
else:
    index_tipo = 0

tipo = st.radio(
    "",
    tipo_opciones,
    index=index_tipo,
    horizontal=True
)

reglas = REGLAS_PRODUCCION if tipo == "PRODUCCIÓN" else REGLAS_LEVANTE

if tipo == "PRODUCCIÓN":
    st.success(
        "🏭 **Modo PRODUCCIÓN activo**. "
        "Se habilitan indicadores de huevos, huevos bomba y cumplimiento productivo."
    )
else:
    st.warning(
        "🐔 **Modo LEVANTE activo**. "
        "Se habilitan indicadores por HEMBRAS y MACHOS "
        "(edad, uniformidad, peso y cumplimiento)."
    )
if "tipo_confirmado" not in st.session_state:
    st.session_state.tipo_confirmado = False

st.session_state.tipo_confirmado = st.checkbox(
    f"✅ Confirmo que el proceso seleccionado es **{tipo}**"
)

if not st.session_state.tipo_confirmado:
    st.info("🔒 Confirme el tipo de proceso para continuar.")
    st.stop()

# Lotes
if "lotes" in st.session_state:
    lotes = st.session_state.lotes
    st.text_input("Lotes", ", ".join(lotes), disabled=True)
else:
    lotes_txt = st.text_input("Lotes (ej: 211-212-213)", "211-212-213")
    lotes = [l.strip() for l in lotes_txt.split("-") if l.strip()]

# Confirmación de datos iniciales
confirmar_inicio = st.checkbox(
     "✅ Confirmo que Granja, Tipo de proceso y Lotes son correctos"
)

if "datos_productivos" not in st.session_state:
    st.session_state.datos_productivos = {}

# =========================
# ETAPA Y DATOS PRODUCTIVOS (PRODUCCIÓN POR LOTE)
# =========================
if tipo == "PRODUCCIÓN":

    st.subheader("🏭 Información productiva – Producción (por lote)")

    for lote in lotes:
        st.markdown(f"### 🧬 Lote {lote}")

        datos = st.session_state.datos_productivos.get(lote, {})

        etapa = st.radio(
            "Etapa de Producción",
            ["Primera etapa", "Segunda etapa"],
            horizontal=True,
            key=f"etapa_{lote}",
            index=0 if datos.get("ETAPA") != "Segunda etapa" else 1
        )

        col1, col2, col3 = st.columns(3)

        with col1:
            edad_ave = st.number_input(
                "Edad del ave (semanas)",
                min_value=0,
                step=1,
                key=f"edad_{lote}",
                value=datos.get("EDAD_AVE", 0)
            )

            huevos_sem_41 = st.number_input(
                "Huevos hasta sem. 41",
                min_value=0,
                step=1,
                key=f"h41_{lote}",
                value=datos.get("HUEVOS_SEM_41", 0)
            )

            poblacion_inicial = st.number_input(
                "Población Inicial Prod",
                min_value=0,
                step=1,
                key=f"pob_{lote}",
                value=datos.get("POBLACION_INICIAL", 0)
            )

        with col2:
            huevos_por_aa = st.number_input(
                "H. Prod / AA",
                min_value=0.0,
                step=0.01,
                key=f"haa_{lote}",
                value=datos.get("HUEVOS_POR_AA", 0.0)
            )

            huevos_std_41 = st.number_input(
                "Huevos STD (41 sem)",
                min_value=0,
                step=1,
                key=f"std41_{lote}",
                value=datos.get("HUEVOS_STD_41", 0)
            )

            pct_cumplimiento = st.number_input(
                "% Cumplimiento",
                min_value=0.0,
                max_value=100.0,
                step=0.1,
                key=f"cumpl_{lote}",
                value=datos.get("PCT_CUMPLIMIENTO", 0.0),
                format="%.2f"
            )

        with col3:
            pct_huevos_bomba = st.number_input(
                "% Huevos Bomba",
                min_value=0.0,
                max_value=100.0,
                step=0.1,
                key=f"bomba_{lote}",
                value=datos.get("PCT_HUEVOS_BOMBA", 0.0),
                format="%.2f"
            )

            st.text_input("Validación", value="CERRADO", disabled=True, key=f"val_{lote}")

        # ✅ Guardar POR LOTE
        st.session_state.datos_productivos[lote] = {
            "ETAPA": etapa,
            "EDAD_AVE": edad_ave,
            "HUEVOS_SEM_41": huevos_sem_41,
            "POBLACION_INICIAL": poblacion_inicial,
            "HUEVOS_POR_AA": huevos_por_aa,
            "HUEVOS_STD_41": huevos_std_41,
            "PCT_CUMPLIMIENTO": pct_cumplimiento,
            "PCT_HUEVOS_BOMBA": pct_huevos_bomba,
            "VALIDACION": "CERRADO"
        }

# =========================
# DATOS PRODUCTIVOS – LEVANTE (POR LOTE)
# =========================
if tipo == "LEVANTE":

    st.subheader("🐔 Información productiva – Levante (por lote)")

    for lote in lotes:
        st.markdown(f"## 🧬 Lote {lote}")

        datos = st.session_state.datos_productivos.get(lote, {})

        # =========================
        # HEMBRAS
        # =========================
        st.markdown("### ♀️ Hembras")

        col1, col2, col3 = st.columns(3)

        with col1:
            edad_hembra = st.number_input(
                "Edad ave al entregar a Prod (Hembras)",
                min_value=0,
                step=1,
                key=f"edad_h_{lote}",
                value=datos.get("HEMBRAS", {}).get("EDAD", 0)
            )

            uniformidad_hembras = st.number_input(
                "Uniformidad Hembras (%)",
                min_value=0.0,
                max_value=100.0,
                step=0.1,
                format="%.2f",
                key=f"unif_h_{lote}",
                value=datos.get("HEMBRAS", {}).get("UNIFORMIDAD", 0.0)
            )

            nro_aves_entregadas_h = st.number_input(
                "Nro Aves Entregadas a Prod (Hembras)",
                min_value=0,
                step=1,
                key=f"aves_h_{lote}",
                value=datos.get("HEMBRAS", {}).get("AVES_ENTREGADAS", 0)
            )

        with col2:
            poblacion_inicial_h = st.number_input(
                "Población Inicial (Hembras)",
                min_value=0,
                step=1,
                key=f"pob_h_{lote}",
                value=datos.get("HEMBRAS", {}).get("POBLACION_INICIAL", 0)
            )

            pct_cumpl_aves_h = st.number_input(
                "% CUMP. Aves Entregadas (Hembras)",
                step=0.1,
                format="%.2f",
                key=f"cump_aves_h_{lote}",
                value=datos.get("HEMBRAS", {}).get("PCT_CUMP_AVES", 0.0)
            )

        with col3:
            peso_entrega_h = st.number_input(
                "Peso Ave al entregar a Prod (Hembras)",
                min_value=0.0,
                step=0.001,
                format="%.3f",
                key=f"peso_h_{lote}",
                value=datos.get("HEMBRAS", {}).get("PESO", 0.0)
            )

            peso_std_h = st.number_input(
                "Peso Ave al entregar a Prod STD (Hembras)",
                value=2.53,
                step=0.001,
                format="%.3f",
                key=f"peso_std_h_{lote}"
            )

            pct_cumpl_peso_h = st.number_input(
                "% CUMP. PESO (Hembras)",
                step=0.1,
                format="%.2f",
                key=f"cump_peso_h_{lote}",
                value=datos.get("HEMBRAS", {}).get("PCT_CUMP_PESO", 0.0)
            )

        # =========================
        # MACHOS
        # =========================
        st.markdown("### ♂️ Machos")

        col4, col5, col6 = st.columns(3)

        with col4:
            edad_macho = st.number_input(
                "Edad ave al entregar a Prod (Machos)",
                min_value=0,
                step=1,
                key=f"edad_m_{lote}",
                value=datos.get("MACHOS", {}).get("EDAD", 0)
            )

            uniformidad_machos = st.number_input(
                "Uniformidad Machos (%)",
                min_value=0.0,
                max_value=100.0,
                step=0.1,
                format="%.2f",
                key=f"unif_m_{lote}",
                value=datos.get("MACHOS", {}).get("UNIFORMIDAD", 0.0)
            )

            nro_aves_entregadas_m = st.number_input(
                "Nro Aves Entregadas a Prod (Machos)",
                min_value=0,
                step=1,
                key=f"aves_m_{lote}",
                value=datos.get("MACHOS", {}).get("AVES_ENTREGADAS", 0)
            )

        with col5:
            poblacion_inicial_m = st.number_input(
                "Población Inicial (Machos)",
                min_value=0,
                step=1,
                key=f"pob_m_{lote}",
                value=datos.get("MACHOS", {}).get("POBLACION_INICIAL", 0)
            )

        with col6:
            peso_entrega_m = st.number_input(
                "Peso Ave al entregar a Prod (Machos)",
                min_value=0.0,
                step=0.001,
                format="%.3f",
                key=f"peso_m_{lote}",
                value=datos.get("MACHOS", {}).get("PESO", 0.0)
            )

            peso_std_m = st.number_input(
                "Peso Ave al entregar a Prod STD (Machos)",
                value=2.955,
                step=0.001,
                format="%.3f",
                key=f"peso_std_m_{lote}"
            )

            pct_cumpl_peso_m = st.number_input(
                "% CUMP. PESO (Machos)",
                step=0.1,
                format="%.2f",
                key=f"cump_peso_m_{lote}",
                value=datos.get("MACHOS", {}).get("PCT_CUMP_PESO", 0.0)
            )

        # =========================
        # GUARDAR POR LOTE
        # =========================
        st.session_state.datos_productivos[lote] = {
            "HEMBRAS": {
                "EDAD": edad_hembra,
                "UNIFORMIDAD": uniformidad_hembras,
                "AVES_ENTREGADAS": nro_aves_entregadas_h,
                "POBLACION_INICIAL": poblacion_inicial_h,
                "PCT_CUMP_AVES": pct_cumpl_aves_h,
                "PESO": peso_entrega_h,
                "PESO_STD": peso_std_h,
                "PCT_CUMP_PESO": pct_cumpl_peso_h
            },
            "MACHOS": {
                "EDAD": edad_macho,
                "UNIFORMIDAD": uniformidad_machos,
                "AVES_ENTREGADAS": nro_aves_entregadas_m,
                "POBLACION_INICIAL": poblacion_inicial_m,
                "PESO": peso_entrega_m,
                "PESO_STD": peso_std_m,
                "PCT_CUMP_PESO": pct_cumpl_peso_m
            }
        }



# Configuración por lote
if not confirmar_inicio:
    st.info(
        "🔒 Confirme Granja, Tipo de proceso y Lotes para continuar."
    )
    st.stop()
st.subheader("🧬 Configuración por lote")

if "config_lotes" not in st.session_state:
    st.session_state.config_lotes = {}

config_lotes = st.session_state.config_lotes
cols = st.columns(len(lotes))

for i, lote in enumerate(lotes):
    with cols[i]:
        valor_gen = config_lotes.get(lote, {}).get("GENETICA", "ROSS")
        valor_monto = float(config_lotes.get(lote, {}).get("MONTO", 1000.0))

        genetica = st.text_input(
            f"Genética - Lote {lote}",
            value=valor_gen,
            key=f"gen_{lote}_v2"
        )

        monto = st.number_input(
            f"Monto S/ - Lote {lote}",
            min_value=0.0,
            value=valor_monto,
            step=50.0,
            key=f"monto_{lote}_v2"
        )

        config_lotes[lote] = {
            "GENETICA": genetica.upper(),
            "MONTO": monto
        }

st.session_state.config_lotes = config_lotes

# SESSION STATE tabla
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

# Ordenar columnas
base_cols = ["DNI","NOMBRE COMPLETO","CARGO"]
pct_cols = [f"P_{l}" for l in lotes]
faltas_cols = [f"F_{l}" for l in lotes]
st.session_state.tabla = st.session_state.tabla[base_cols + pct_cols + faltas_cols]

# Sincronizar df_edit
if "df_edit" not in st.session_state:
    st.session_state.df_edit = st.session_state.tabla.copy()
else:
    for col in st.session_state.tabla.columns:
        if col not in st.session_state.df_edit.columns:
            st.session_state.df_edit[col] = st.session_state.tabla[col]
    st.session_state.df_edit = st.session_state.df_edit[st.session_state.tabla.columns]

# Agregar trabajador
st.subheader("➕ Agregar trabajador")
dni_new = st.text_input("DNI", key="dni_preview", placeholder="Ingrese DNI y luego haga click en Agregar")
dni_limpio = dni_new.strip().zfill(8) if dni_new else ""
if dni_limpio:
    if dni_limpio in st.session_state.tabla["DNI"].values:
        st.warning("⚠️ El trabajador ya existe en la tabla")
    else:
        fila_prev = df_base[df_base["DNI"]==dni_limpio]
        if not fila_prev.empty:
            st.markdown(f"<span style='color:#1f77b4; font-weight:bold;'>👤 {fila_prev.iloc[0]['NOMBRE COMPLETO']}</span>", unsafe_allow_html=True)
        else:
            st.error("❌ DNI no encontrado en la base de trabajadores")

if st.button("Agregar trabajador"):
    if not dni_limpio:
        st.warning("⚠️ Ingrese un DNI")
    elif dni_limpio in st.session_state.tabla["DNI"].values:
        st.warning("⚠️ El trabajador ya existe en la tabla")
    else:
        fila = df_base[df_base["DNI"]==dni_limpio]
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

# Eliminar trabajador
st.subheader("➖ Eliminar trabajador")
eliminar_dni = st.text_input("DNI a eliminar").strip().zfill(8)
if st.button("Eliminar trabajador"):
    st.session_state.tabla = st.session_state.tabla[st.session_state.tabla["DNI"] != eliminar_dni]
    st.session_state.df_edit = st.session_state.tabla.copy()
    st.success("✅ Trabajador eliminado")

# Editar tabla
st.subheader("✍️ Registro por trabajador y lote")
st.info(
    "📌 **Leyenda de columnas**\n\n"
    "**P:** Porcentaje de Participación.\n\n"
    "**F:** Faltas Injustificadas."
)
with st.form("form_edicion"):
    df_edit = st.data_editor(st.session_state.df_edit, use_container_width=True)
    if st.form_submit_button("💾 Actualizar tabla"):
        st.session_state.tabla = df_edit.copy()
        st.session_state.df_edit = df_edit.copy()
        st.success("✅ Tabla actualizada")

# Cálculo final
df_final = st.session_state.tabla.copy()
pagos = []
for lote in lotes:
    col = f"PAGO_{lote}"
    df_final[col] = df_final.apply(lambda r: round(
        reglas.get(str(r["CARGO"]).upper(),0) * config_lotes[lote]["MONTO"] * (float(r[f"P_{lote}"])/100) * factor_faltas(r[f"F_{lote}"]),
        2
    ), axis=1)
    pagos.append(col)

df_final["TOTAL S/"] = df_final[pagos].sum(axis=1)

# Resultado final
st.subheader("💰 Resultado final")
st.dataframe(df_final, use_container_width=True)

# Gráfico
st.subheader("📊 Distribución de bonos por trabajador")
fig = px.bar(df_final, x="NOMBRE COMPLETO", y="TOTAL S/", text="TOTAL S/", title="Bono total por trabajador")
fig.update_traces(texttemplate="S/ %{text:,.2f}", textposition="outside", cliponaxis=False)
fig.update_layout(xaxis_tickangle=-45, height=550, margin=dict(t=100), yaxis=dict(rangemode="tozero"))
st.plotly_chart(fig, use_container_width=True)

# Exportar
output = BytesIO()
with pd.ExcelWriter(output, engine="openpyxl") as writer:
    sheet_name = "BONO_REPRODUCTORAS"
    fila_actual = 0

    # Encabezado
    encabezado = pd.DataFrame({
        "Campo":["Granja","Tipo de Proceso","Lotes","Fecha de Generación"],
        "Valor":[st.session_state.get("granja_seleccionada",""), tipo, ", ".join(lotes), pd.Timestamp.now().strftime("%Y-%m-%d %H:%M")]
    })
    encabezado.to_excel(writer, sheet_name=sheet_name, index=False, startrow=fila_actual)
    fila_actual += len(encabezado)+2

    # Configuración de lotes
    df_lotes = pd.DataFrame([{"Lote":l,"Genética":config_lotes[l]["GENETICA"],"Monto S/":config_lotes[l]["MONTO"]} for l in lotes])
    df_lotes.to_excel(writer, sheet_name=sheet_name, index=False, startrow=fila_actual)
    fila_actual += len(df_lotes)+3

    # Detalle trabajadores
    df_final.to_excel(writer, sheet_name=sheet_name, index=False, startrow=fila_actual)

nombre_archivo = (
    f"Bono_Reproductoras_"
    f"{st.session_state.get('granja_seleccionada','NA').replace(' ','')}_"
    f"{tipo}_"
    f"{pd.Timestamp.now():%Y%m%d_%H%M}.xlsx"
)

st.download_button(
    "📥 Descargar archivo final",
    data=output.getvalue(),
    file_name=nombre_archivo
)

# =========================
# PREVISUALIZAR Y ENVIAR POR CORREO (MICROSOFT 365)
# =========================
import smtplib
from email.message import EmailMessage

st.subheader("📬 Opciones finales")

tab1, tab2 = st.tabs(["📊 Previsualizar resultado", "📧 Enviar por correo"])

# =========================
# RESUMEN EJECUTIVO
# =========================
total_general = df_final["TOTAL S/"].sum()
num_trabajadores = df_final.shape[0]
lote_mayor = (
    df_final[pagos]
    .sum()
    .idxmax()
    .replace("PAGO_", "")
)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("💰 Total general (S/)", f"{total_general:,.2f}")

with col2:
    st.metric("👥 N° de trabajadores", num_trabajadores)

with col3:
    st.metric("🏷️ Lote con mayor pago", lote_mayor)

# =========================
# RESUMEN POR LOTE
# =========================
resumen_lote = (
    df_final[pagos]
    .sum()
    .reset_index()
    .rename(columns={"index": "Lote", 0: "Total S/"})
)

resumen_lote["Lote"] = resumen_lote["Lote"].str.replace("PAGO_", "")
resumen_lote["% del total"] = (
    resumen_lote["Total S/"] / total_general * 100
).round(2)

st.subheader("📦 Resumen por lote")
st.dataframe(resumen_lote, use_container_width=True)

fig_lote = px.bar(
    resumen_lote,
    x="Lote",
    y="Total S/",
    text="Total S/",
    title="Distribución de pago por lote"
)

fig_lote.update_traces(
    texttemplate="S/ %{text:,.2f}",
    textposition="outside"
)

fig_lote.update_layout(
    yaxis=dict(
        rangemode="tozero",
        automargin=True
    ),
    height=450,
    margin=dict(t=120, b=50)
)

fig_lote.update_traces(
    texttemplate="S/ %{text:,.2f}",
    textposition="outside",
    cliponaxis=False
)

st.plotly_chart(fig_lote, use_container_width=True)

# -------- TAB 1: PREVISUALIZAR --------
with tab1:
    st.markdown("### 💰 Resultado final completo")
    st.dataframe(df_final, use_container_width=True)

# -------- TAB 2: ENVIAR POR CORREO --------
with tab2:
    st.markdown("### 📧 Enviar resultado por correo corporativo")

    correo_destino = st.text_input("Correo destino", key="correo_destino")
    asunto = st.text_input(
        "Asunto",
        value="Resultado Bono Reproductoras GDP",
        key="asunto_correo"
    )
    mensaje = st.text_area(
        "Mensaje",
        value="Adjunto encontrará el resultado del bono generado.",
        key="mensaje_correo"
    )

    if st.button("📨 Enviar correo", key="btn_enviar_correo"):
        if not correo_destino:
            st.warning("Ingrese un correo destino")
        else:
            try:
                msg = EmailMessage()
                msg["From"] = st.secrets["EMAIL_USER"]
                msg["To"] = correo_destino
                msg["Subject"] = asunto

                tabla_lote_html = resumen_lote.to_html(
                    index=False,
                    border=1,
                    justify="center"
                )

                tabla_html = df_final.to_html(
                    index=False,
                    border=1,
                    justify="center"
                )

                cuerpo_html = f"""
                <html>
                    <body>
                        <h2>Bono Reproductoras GDP</h2>
                        <p><strong>Granja:</strong> {st.session_state.get("granja_seleccionada","")}</p>
                        <p><strong>Tipo de proceso:</strong> {tipo}</p>
                        <p><strong>Lotes:</strong> {", ".join(lotes)}</p>
                        <p><strong>Fecha:</strong> {pd.Timestamp.now().strftime("%Y-%m-%d %H:%M")}</p>

                        <h3>📦 Resumen por lote</h3>
                        {tabla_lote_html}

                        <h3>💰 Resultado final por trabajador</h3>
                        {tabla_html}

                        <p>Adjunto se envía el archivo Excel.</p>
                        <p><strong>Equipo de Control de Gestión</strong></p>
                    </body>
                </html>
                """

                msg.add_alternative(cuerpo_html, subtype="html")

                msg.add_attachment(
                    output.getvalue(),
                    maintype="application",
                    subtype="vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    filename="bono_reproductoras_final.xlsx"
                )

                with smtplib.SMTP("smtp.office365.com", 587) as smtp:
                    smtp.starttls()
                    smtp.login(
                        st.secrets["EMAIL_USER"],
                        st.secrets["EMAIL_PASS"]
                    )
                    smtp.send_message(msg)

                st.success("✅ Correo enviado correctamente")

            except Exception as e:
                st.error("❌ Error al enviar el correo")














