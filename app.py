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
        "Antes de iniciar el cálculo del bono, se debe coordinar previamente con el "
        "**equipo de Control de Gestión (CDG)**.\n\n"
        "**Paso obligatorio:**\n"
        "• Completar todos los campos del sistema y **enviar la información al equipo CDG para su validación**.\n"
        "• CDG validará los datos productivos (Huevos Bomba, % de Cumplimiento, entre otros indicadores).\n\n"
        "• Asimismo, se valida la **definición de los montos base por granja y por lote**.\n\n"
        "**Correo de validación:**\n"
        "📧 humbertoatoche@donpollo.pe\n"
        "📧 galapi@donpollo.pe\n\n"
        "El sistema asume que esta información ya fue revisada y validada oficialmente por CDG."
    )

    st.markdown("""
    ---

    ## 🚀 Guía de Uso del Sistema

    ### 1️⃣ Ingreso al sistema
    Una vez autenticado, podrá elegir cómo iniciar el proceso:

    - **➕ Iniciar desde cero**  
      Utilice esta opción cuando el bono del periodo aún no ha sido trabajado.

    - **📂 Cargar Excel previamente generado**  
      Ideal para continuar, corregir o validar un archivo descargado anteriormente desde el sistema.

    ---

    ### 2️⃣ Carga de información base
    Dependiendo de la opción elegida:

    **Si inicia desde cero**, deberá cargar:
    - 📄 **Excel con DNIs** del personal participante  
    - 📊 **Base de trabajadores** (maestro oficial)

    El sistema realiza automáticamente:
    - Normalización de DNIs  
    - Cruce de nombres y cargos  
    - Validación de duplicados  

    ---

    ### 3️⃣ Configuración inicial del proceso
    En esta etapa deberá definir:

    - 🏡 **Granja**
    - 🔀 **Tipo de proceso**:  
        - **PRODUCCIÓN** → indicadores productivos  
        - **LEVANTE** → indicadores por Hembras y Machos
    - 🏷️ **Lotes** (ejemplo: 211-212-213)

    ⚠️ Una vez confirmados estos datos, no se recomienda modificarlos.

    ---

    ### 4️⃣ Ingreso de datos productivos
    Según el tipo de proceso seleccionado:

    #### 🏭 PRODUCCIÓN
    - Etapa  
    - Edad  
    - Huevos  
    - % Cumplimiento  
    - % Huevos bomba  

    #### 🐔 LEVANTE
    - ♀️ Hembras  
    - ♂️ Machos  
    (edad, uniformidad, peso y cumplimiento)

    💾 Siempre presione **Guardar** luego de modificar datos.

    ---

    ### 5️⃣ Configuración económica por lote
    - 🧬 Genética  
    - 💰 Monto base por lote  

    ---

    ### 6️⃣ Gestión de trabajadores
    - ➕ Agregar por DNI  
    - ➖ Eliminar trabajadores  
    - **P_[Lote]** porcentaje  
    - **F_[Lote]** faltas  

    💾 Presione **Actualizar tabla** al finalizar.

    ---

    ### 7️⃣ Resultados
    - Resultado final por trabajador  
    - Resumen por lote  
    - Gráficas de distribución  

    ---

    ### 8️⃣ Exportación y envío
    - 📥 Descargar Excel oficial  
    - 📧 Enviar correo corporativo con validación  

    ✔️ Flujo validado y alineado con Control de Gestión.
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

# =========================
# LISTA OFICIAL DE CARGOS
# =========================
CARGOS_VALIDOS = sorted(REGLAS_PRODUCCION.keys())

DESCUENTO_FALTAS = {0:1.0, 1:0.90, 2:0.80, 3:0.70, 4:0.60}
def factor_faltas(f):
    try:
        f = int(f)
    except:
        return 0.50
    return DESCUENTO_FALTAS.get(f, 0.50)

# =========================
# HELPER – LECTURA DE TABLAS INVERTIDAS (LEVANTE)
# =========================
def leer_bloque_invertido(raw, fila_inicio, n_filas):
    """
    raw        : dataframe completo sin header
    fila_inicio: fila donde está 'Edad'
    n_filas    : número de filas del bloque
    """

    # encabezados (lotes) están UNA FILA ARRIBA
    lotes = (
        raw.iloc[fila_inicio - 1, 1:]
        .astype(str)
        .str.replace(".0", "", regex=False)
        .str.strip()
    )

    bloque = raw.iloc[fila_inicio:fila_inicio + n_filas].copy()

    data = bloque.iloc[:, 1:]
    data.columns = lotes

    data.index = (
        bloque.iloc[:, 0]
        .astype(str)
        .str.strip()
    )

    return data


def get_valor(df, fila_idx, col, default=0.0):
    try:
        v = df.iloc[fila_idx][col]
        return float(v) if pd.notna(v) else default
    except:
        return default


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
            df_base[["DNI", "NOMBRE COMPLETO", "CARGO"]],
            on="DNI",
            how="left"
        )

        st.success("✅ Cruce de trabajadores realizado")
elif opcion_inicio == "📂 Cargar Excel previamente generado":
    archivo_prev = st.file_uploader(
        "📂 Subir Excel previamente generado",
        type=["xlsx"]
    )

    if archivo_prev:

        # =========================
        # LECTURA RAW
        # =========================
        raw = pd.read_excel(
            archivo_prev,
            sheet_name="BONO_REPRODUCTORAS",
            header=None
        )

        # =========================
        # 1️⃣ ENCABEZADO
        # =========================
        encabezado = raw.iloc[0:5, 0:2].copy()
        encabezado.columns = ["CAMPO", "VALOR"]
        encabezado["CAMPO"] = encabezado["CAMPO"].astype(str).str.upper().str.strip()

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

        # =========================
        # 2️⃣ CONFIGURACIÓN POR LOTE (ROBUSTA, SOLO A–C)
        # =========================
        fila_lotes = raw[
            raw.iloc[:, 0].astype(str).str.strip().str.upper() == "LOTE"
        ].index[0]

        # Leer SOLO columnas A, B y C
        df_lotes_raw = raw.iloc[fila_lotes + 1:, 0:3].copy()
        df_lotes_raw.columns = ["LOTE", "GENETICA", "MONTO"]

        # Limpieza fuerte
        df_lotes_raw["LOTE"] = df_lotes_raw["LOTE"].astype(str).str.strip()
        df_lotes_raw["GENETICA"] = (
            df_lotes_raw["GENETICA"]
            .astype(str)
            .str.strip()
            .str.upper()
        )

        df_lotes_raw["MONTO"] = (
            df_lotes_raw["MONTO"]
            .astype(str)
            .str.replace(",", "", regex=False)
        )
        df_lotes_raw["MONTO"] = pd.to_numeric(
            df_lotes_raw["MONTO"], errors="coerce"
        )

        # Cortar al primer vacío (evita Hembras/Machos)
        df_lotes_raw = df_lotes_raw[
            df_lotes_raw["LOTE"].notna() & (df_lotes_raw["LOTE"] != "")
        ]

        # Construir config_lotes LIMPIO
        config_lotes = {}
        for _, r in df_lotes_raw.iterrows():
            lote = str(r["LOTE"]).strip()
            config_lotes[lote] = {
                "GENETICA": r["GENETICA"] if r["GENETICA"] else "ROSS",
                "MONTO": float(r["MONTO"]) if pd.notna(r["MONTO"]) else 0.0
            }

        # =========================
        # 3️⃣ TABLA DE TRABAJADORES
        # =========================
        fila_tabla = raw[
            raw.iloc[:, 0].astype(str).str.strip().str.upper() == "DNI"
        ].index[0]

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

        # =========================
        # 4️⃣ DATOS PRODUCTIVOS – LEVANTE
        # =========================
        if tipo == "LEVANTE":

            st.session_state.datos_productivos = {}

            idx_edades = raw[
                raw.iloc[:, 0].astype(str).str.strip().str.upper() == "EDAD"
            ].index.tolist()

            if len(idx_edades) < 2:
                st.error("❌ No se detectaron bloques de Hembras y Machos")
                st.stop()

            inicio_h = idx_edades[0]   # Hembras
            inicio_m = idx_edades[1]   # Machos

            df_h = leer_bloque_invertido(raw, inicio_h, 8)
            df_m = leer_bloque_invertido(raw, inicio_m, 7)

            for lote in df_h.columns:
                st.session_state.datos_productivos.setdefault(lote, {})

                st.session_state.datos_productivos[lote]["HEMBRAS"] = {
                    "EDAD": get_valor(df_h, 0, lote),
                    "UNIFORMIDAD": get_valor(df_h, 1, lote),
                    "AVES_ENTREGADAS": get_valor(df_h, 2, lote),
                    "POBLACION_INICIAL": get_valor(df_h, 3, lote),
                    "PCT_CUMP_AVES": get_valor(df_h, 4, lote),
                    "PESO": get_valor(df_h, 5, lote),
                    "PESO_STD": get_valor(df_h, 6, lote),
                    "PCT_CUMP_PESO": get_valor(df_h, 7, lote),
                }

                st.session_state.datos_productivos[lote]["MACHOS"] = {
                    "EDAD": get_valor(df_m, 0, lote),
                    "UNIFORMIDAD": get_valor(df_m, 1, lote),
                    "AVES_ENTREGADAS": get_valor(df_m, 2, lote),
                    "POBLACION_INICIAL": get_valor(df_m, 3, lote),
                    "PESO": get_valor(df_m, 4, lote),
                    "PESO_STD": get_valor(df_m, 5, lote),
                    "PCT_CUMP_PESO": get_valor(df_m, 6, lote),
                }

        # =========================
        # 5️⃣ SESSION STATE FINAL
        # =========================
        st.session_state.tabla = df.copy()
        st.session_state.df_edit = df.copy()
        st.session_state.config_lotes = config_lotes
        st.session_state.lotes = lotes
        st.session_state.tipo = tipo

        # 🔑 FLAG CRÍTICO PARA LA UI
        st.session_state.cargado_desde_excel = True

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
# ETAPA Y DATOS PRODUCTIVOS (PRODUCCIÓN - TABLA INVERTIDA)
# =========================
if tipo == "PRODUCCIÓN":

    st.subheader("🏭 Información productiva – Producción")

    campos_prod = {
        "Etapa": "ETAPA",
        "Edad (sem)": "EDAD_AVE",
        "Huevos sem 41": "HUEVOS_SEM_41",
        "Población inicial": "POBLACION_INICIAL",
        "Huevos / AA": "HUEVOS_POR_AA",
        "Huevos STD 41": "HUEVOS_STD_41",
        "% Cumplimiento": "PCT_CUMPLIMIENTO",
        "% Huevos bomba": "PCT_HUEVOS_BOMBA",
    }

    data = {
        campo: [
            st.session_state.datos_productivos
            .get(lote, {})
            .get(key, "Primera Etapa" if key == "ETAPA" else 0)
            for lote in lotes
        ]
        for campo, key in campos_prod.items()
    }

    df_prod = pd.DataFrame(data, index=lotes).T

    # ===== FORMULARIO =====
    with st.form("form_produccion_tabla"):

        df_edit = st.data_editor(
            df_prod,
            use_container_width=True,
            num_rows="fixed",
            column_config={
                lote: (
                    st.column_config.SelectboxColumn(
                        "Etapa",
                        options=["Primera Etapa", "Segunda Etapa"]
                    )
                    if "Etapa" in df_prod.index
                    else st.column_config.NumberColumn()
                )
                for lote in lotes
            }
        )

        guardar = st.form_submit_button("💾 Guardar Producción")

    # ===== GUARDADO =====
    if guardar:
        for lote in lotes:
            st.session_state.datos_productivos.setdefault(lote, {})
            for campo, key in campos_prod.items():
                valor = df_edit.loc[campo, lote]
                st.session_state.datos_productivos[lote][key] = (
                    valor if key == "ETAPA" else float(valor)
                )

            st.session_state.datos_productivos[lote]["VALIDACION"] = "CERRADO"

        st.success("✅ Datos de PRODUCCIÓN guardados correctamente")

# =========================
# DATOS PRODUCTIVOS – LEVANTE (TABLAS INVERTIDAS)
# =========================
if tipo == "LEVANTE":

    st.subheader("🐔 Información productiva – Levante")

    # =====================================================
    # ♀️ HEMBRAS
    # =====================================================
    st.markdown("### ♀️ Hembras")

    campos_h = {
        "Edad": "EDAD",
        "Uniformidad (%)": "UNIFORMIDAD",
        "Aves entregadas": "AVES_ENTREGADAS",
        "Población inicial": "POBLACION_INICIAL",
        "% Cumpl. aves": "PCT_CUMP_AVES",
        "Peso": "PESO",
        "Peso STD": "PESO_STD",
        "% Cumpl. peso": "PCT_CUMP_PESO",
    }

    data_h = {
        campo: [
            st.session_state.datos_productivos
            .get(lote, {})
            .get("HEMBRAS", {})
            .get(key, 2.53 if key == "PESO_STD" else 0)
            for lote in lotes
        ]
        for campo, key in campos_h.items()
    }

    df_h = pd.DataFrame(data_h, index=lotes).T

    # (opcional) redondeo lógico
    df_h.loc["Peso STD"] = df_h.loc["Peso STD"].astype(float).round(2)

    with st.form("form_levante_hembras"):
        df_h_edit = st.data_editor(
            df_h,
            use_container_width=True,
            num_rows="fixed",
            column_config={
                lote: st.column_config.NumberColumn()
                for lote in lotes
            }
        )

        guardar_h = st.form_submit_button("💾 Guardar Hembras")

    if guardar_h:
        for lote in lotes:
            st.session_state.datos_productivos.setdefault(lote, {})
            st.session_state.datos_productivos[lote]["HEMBRAS"] = {
                key: float(df_h_edit.loc[campo, lote])
                for campo, key in campos_h.items()
            }

        st.success("✅ Datos de HEMBRAS guardados correctamente")

    # =====================================================
    # ♂️ MACHOS
    # =====================================================
    st.markdown("### ♂️ Machos")

    campos_m = {
        "Edad": "EDAD",
        "Uniformidad (%)": "UNIFORMIDAD",
        "Aves entregadas": "AVES_ENTREGADAS",
        "Población inicial": "POBLACION_INICIAL",
        "Peso": "PESO",
        "Peso STD": "PESO_STD",
        "% Cumpl. peso": "PCT_CUMP_PESO",
    }

    data_m = {
        campo: [
            st.session_state.datos_productivos
            .get(lote, {})
            .get("MACHOS", {})
            .get(key, 2.955 if key == "PESO_STD" else 0)
            for lote in lotes
        ]
        for campo, key in campos_m.items()
    }

    df_m = pd.DataFrame(data_m, index=lotes).T

    # 🔒 PESO STD MACHOS → SIEMPRE 3 DECIMALES
    df_m.loc["Peso STD"] = df_m.loc["Peso STD"].astype(float).round(3)

    with st.form("form_levante_machos"):
        df_m_edit = st.data_editor(
            df_m,
            use_container_width=True,
            num_rows="fixed",
            column_config={
                lote: st.column_config.NumberColumn()
                for lote in lotes
            }
        )

        guardar_m = st.form_submit_button("💾 Guardar Machos")

    if guardar_m:
        for lote in lotes:
            st.session_state.datos_productivos.setdefault(lote, {})
            st.session_state.datos_productivos[lote]["MACHOS"] = {
                key: float(df_m_edit.loc[campo, lote])
                for campo, key in campos_m.items()
            }

        st.success("✅ Datos de MACHOS guardados correctamente")

# =========================
# 🧬 CONFIGURACIÓN POR LOTE (CORREGIDO DEFINITIVO)
# =========================
st.subheader("🧬 Configuración por lote")

# 🔒 Blindaje
if "config_lotes" not in st.session_state:
    st.session_state.config_lotes = {}

config_lotes = st.session_state.config_lotes
cols = st.columns(len(lotes))

for i, lote in enumerate(lotes):
    with cols[i]:

        # 🔑 Lectura SEGURA
        data_lote = config_lotes.get(lote, {})
        valor_gen = data_lote.get("GENETICA", "ROSS")
        valor_monto = data_lote.get("MONTO", 0.0)

        genetica = st.text_input(
            f"Genética - Lote {lote}",
            value=str(valor_gen),
            key=f"gen_{lote}"
        )

        monto = st.number_input(
            f"Monto S/ - Lote {lote}",
            min_value=0.0,
            step=50.0,
            value=float(valor_monto),
            key=f"monto_{lote}"
        )

        # 💾 Guardado
        config_lotes[lote] = {
            "GENETICA": genetica.strip().upper(),
            "MONTO": float(monto)
        }

# Persistir
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
    df_edit = st.data_editor(
        st.session_state.df_edit,
        use_container_width=True,
        column_config={
            "CARGO": st.column_config.SelectboxColumn(
                "CARGO",
                options=CARGOS_VALIDOS,
                required=True
            )
        }
    )

    if st.form_submit_button("💾 Actualizar tabla"):
        # Normalización defensiva
        df_edit["CARGO"] = df_edit["CARGO"].str.upper().str.strip()

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

# =========================
# 📤 EXPORTAR EXCEL COMPLETO
# =========================
output = BytesIO()

with pd.ExcelWriter(output, engine="openpyxl") as writer:
    sheet_name = "BONO_REPRODUCTORAS"
    fila_actual = 0

    # =========================
    # 1️⃣ ENCABEZADO
    # =========================
    encabezado = pd.DataFrame({
        "Campo": ["Granja", "Tipo de Proceso", "Lotes", "Fecha de Generación"],
        "Valor": [
            st.session_state.get("granja_seleccionada", ""),
            tipo,
            ", ".join(lotes),
            pd.Timestamp.now().strftime("%Y-%m-%d %H:%M")
        ]
    })
    encabezado.to_excel(
        writer,
        sheet_name=sheet_name,
        index=False,
        startrow=fila_actual
    )
    fila_actual += len(encabezado) + 2

    # =========================
    # 2️⃣ CONFIGURACIÓN DE LOTES
    # =========================
    df_lotes = pd.DataFrame([
        {
            "Lote": l,
            "Genética": config_lotes[l]["GENETICA"],
            "Monto S/": config_lotes[l]["MONTO"]
        }
        for l in lotes
    ])
    df_lotes.to_excel(
        writer,
        sheet_name=sheet_name,
        index=False,
        startrow=fila_actual
    )
    fila_actual += len(df_lotes) + 3

    # =========================
    # 3️⃣ DATOS PRODUCTIVOS
    # =========================
    if tipo == "PRODUCCIÓN":
        df_prod_excel = pd.DataFrame(data_prod, index=lotes).T
        df_prod_excel.to_excel(
            writer,
            sheet_name=sheet_name,
            index=True,
            startrow=fila_actual
        )
        fila_actual += len(df_prod_excel) + 3

    else:  # LEVANTE
        df_h.to_excel(
            writer,
            sheet_name=sheet_name,
            index=True,
            startrow=fila_actual
        )
        fila_actual += len(df_h) + 3

        df_m.to_excel(
            writer,
            sheet_name=sheet_name,
            index=True,
            startrow=fila_actual
        )
        fila_actual += len(df_m) + 3

    # =========================
    # 4️⃣ RESUMEN POR LOTE (RECALCULADO AQUÍ)
    # =========================
    pagos_cols = [c for c in df_final.columns if c.startswith("PAGO_")]

    resumen_lote_excel = (
        df_final[pagos_cols]
        .sum()
        .reset_index()
        .rename(columns={"index": "Lote", 0: "Total S/"})
    )

    resumen_lote_excel["Lote"] = resumen_lote_excel["Lote"].str.replace("PAGO_", "")
    total_general = resumen_lote_excel["Total S/"].sum()

    resumen_lote_excel["% del total"] = (
        resumen_lote_excel["Total S/"] / total_general * 100
    ).round(2)

    resumen_lote_excel.to_excel(
        writer,
        sheet_name=sheet_name,
        index=False,
        startrow=fila_actual
    )
    fila_actual += len(resumen_lote_excel) + 2

    # =========================
    # 5️⃣ RESULTADO FINAL POR TRABAJADOR
    # =========================
    df_final.to_excel(
        writer,
        sheet_name=sheet_name,
        index=False,
        startrow=fila_actual
    )

# =========================
# 🏷️ NOMBRE DEL ARCHIVO
# =========================
nombre_archivo = (
    f"Bono_Reproductoras_"
    f"{st.session_state.get('granja_seleccionada','NA').replace(' ','')}_"
    f"{tipo}_"
    f"{pd.Timestamp.now():%Y%m%d_%H%M}.xlsx"
)

# =========================
# 📥 BOTÓN DE DESCARGA
# =========================
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

# -------- TAB 1: PREVISUALIZAR --------
with tab1:

    st.markdown("## 📊 Previsualización integral del proceso")

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
    # DATOS PRODUCTIVOS
    # =========================
    st.markdown("### 🧬 Datos productivos")

    if tipo == "PRODUCCIÓN":

        campos_prod = {
            "Etapa": "ETAPA",
            "Edad (sem)": "EDAD_AVE",
            "Huevos sem 41": "HUEVOS_SEM_41",
            "Población inicial": "POBLACION_INICIAL",
            "Huevos / AA": "HUEVOS_POR_AA",
            "Huevos STD 41": "HUEVOS_STD_41",
            "% Cumplimiento": "PCT_CUMPLIMIENTO",
            "% Huevos bomba": "PCT_HUEVOS_BOMBA",
        }

        data_prod = {
            campo: [
                st.session_state.datos_productivos
                .get(lote, {})
                .get(key, "")
                for lote in lotes
            ]
            for campo, key in campos_prod.items()
        }

        df_prod_prev = pd.DataFrame(data_prod, index=lotes).T
        st.dataframe(df_prod_prev, use_container_width=True)

    else:

        # ---------- HEMBRAS ----------
        st.markdown("#### ♀️ Levante – Hembras")

        campos_h = {
            "Edad": "EDAD",
            "Uniformidad (%)": "UNIFORMIDAD",
            "Aves entregadas": "AVES_ENTREGADAS",
            "Población inicial": "POBLACION_INICIAL",
            "% Cumpl. aves": "PCT_CUMP_AVES",
            "Peso": "PESO",
            "Peso STD": "PESO_STD",
            "% Cumpl. peso": "PCT_CUMP_PESO",
        }

        data_h = {
            campo: [
                st.session_state.datos_productivos
                .get(lote, {})
                .get("HEMBRAS", {})
                .get(key, "")
                for lote in lotes
            ]
            for campo, key in campos_h.items()
        }

        df_h_prev = pd.DataFrame(data_h, index=lotes).T
        st.dataframe(df_h_prev, use_container_width=True)

        # ---------- MACHOS ----------
        st.markdown("#### ♂️ Levante – Machos")

        campos_m = {
            "Edad": "EDAD",
            "Uniformidad (%)": "UNIFORMIDAD",
            "Aves entregadas": "AVES_ENTREGADAS",
            "Población inicial": "POBLACION_INICIAL",
            "Peso": "PESO",
            "Peso STD": "PESO_STD",
            "% Cumpl. peso": "PCT_CUMP_PESO",
        }

        data_m = {
            campo: [
                st.session_state.datos_productivos
                .get(lote, {})
                .get("MACHOS", {})
                .get(key, "")
                for lote in lotes
            ]
            for campo, key in campos_m.items()
        }

        df_m_prev = pd.DataFrame(data_m, index=lotes).T
        st.dataframe(df_m_prev, use_container_width=True)

    # =========================
    # RESULTADO FINAL
    # =========================
    st.markdown("### 💰 Resultado final por trabajador")
    st.dataframe(df_final, use_container_width=True)

    # =========================
    # RESUMEN POR LOTE (SE CREA AQUÍ)
    # =========================
    resumen_lote = (
        df_final[pagos]
        .sum()
        .reset_index()
        .rename(columns={"index": "Lote", 0: "Total S/"})
    )

    resumen_lote["Lote"] = resumen_lote["Lote"].str.replace("PAGO_", "")
    resumen_lote["% del total"] = (
        resumen_lote["Total S/"] / resumen_lote["Total S/"].sum() * 100
    ).round(2)

    st.markdown("### 📦 Resumen por lote")
    st.dataframe(resumen_lote, use_container_width=True)

    # =========================
    # GRÁFICA: DISTRIBUCIÓN DE PAGO POR LOTE
    # =========================
    st.markdown("### 📊 Distribución de pago por lote")

    import plotly.express as px

    fig = px.bar(
        resumen_lote,
        x="Lote",
        y="Total S/",
        text="Total S/",
        labels={"Total S/": "Total S/"},
    )

    fig.update_traces(
        texttemplate="S/ %{text:.2f}",
        textposition="outside"
    )

    fig.update_layout(
        yaxis_title="Total S/",
        xaxis_title="Lote",
        uniformtext_minsize=8,
        uniformtext_mode="hide",
    )

    st.plotly_chart(fig, use_container_width=True)


# -------- TAB 2: ENVIAR POR CORREO --------
with tab2:
    st.markdown("### 📧 Enviar resultado por correo corporativo")

    # ==================================================
    # Helper: HTML compacto y limpio (Outlook-safe)
    # ==================================================
    def _estilizar_tabla_html(html: str, align_td: str = "right") -> str:
        html = html.replace(
            "<table",
            "<table style='border-collapse:collapse; width:auto; max-width:760px; "
            "font-family:Arial, sans-serif; font-size:12px;'"
        )
        html = html.replace(
            "<th>",
            "<th style='border:1px solid #d1d5db; background:#f3f4f6; "
            "padding:6px 8px; text-align:left; white-space:nowrap;'>"
        )
        html = html.replace(
            "<td>",
            f"<td style='border:1px solid #d1d5db; padding:6px 8px; "
            f"text-align:{align_td}; white-space:nowrap;'>"
        )
        return html

    # ==================================================
    # Helper: tabla invertida (filas=campos)
    # ==================================================
    def tabla_html_limpia_invertida(df, decimales_por_fila=None):
        df_fmt = df.copy()

        for fila in df_fmt.index:
            serie = pd.to_numeric(df_fmt.loc[fila], errors="coerce")
            if serie.notna().any():
                if decimales_por_fila and fila in decimales_por_fila:
                    dec = int(decimales_por_fila[fila])
                    df_fmt.loc[fila] = serie.apply(
                        lambda x: f"{x:.{dec}f}" if pd.notna(x) else ""
                    )
                else:
                    df_fmt.loc[fila] = serie.apply(
                        lambda x: f"{int(x)}" if pd.notna(x) else ""
                    )

        html = df_fmt.to_html(index=True, border=1)
        return _estilizar_tabla_html(html, align_td="right")

    # ==================================================
    # Helper: tabla normal (filas = registros)
    # ==================================================
    def tabla_html_limpia_normal(df, decimales_por_col=None, alineacion="left"):
        df_fmt = df.copy()

        if decimales_por_col:
            for c, dec in decimales_por_col.items():
                if c in df_fmt.columns:
                    df_fmt[c] = pd.to_numeric(df_fmt[c], errors="coerce").apply(
                        lambda x: f"{x:.{int(dec)}f}" if pd.notna(x) else ""
                    )

        html = df_fmt.to_html(index=False, border=1)
        return _estilizar_tabla_html(html, align_td=alineacion)

    # ==================================================
    # Inputs
    # ==================================================
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

                # =========================
                # 📦 Resumen por lote (correo)
                # =========================
                tabla_lote_html = tabla_html_limpia_normal(
                    resumen_lote,
                    decimales_por_col={"Total S/": 2, "% del total": 2},
                    alineacion="left"
                )

                # =========================
                # 💰 Resultado final (correo)
                # =========================
                cols_pago = [c for c in df_final.columns if c.startswith("PAGO_")]
                if "TOTAL S/" in df_final.columns:
                    cols_pago.append("TOTAL S/")

                tabla_resultado_html = tabla_html_limpia_normal(
                    df_final,
                    decimales_por_col={c: 2 for c in cols_pago},
                    alineacion="left"
                )

                # =========================
                # 🧬 Datos productivos
                # =========================
                if tipo == "PRODUCCIÓN":
                    campos_prod = {
                        "Etapa": "ETAPA",
                        "Edad (sem)": "EDAD_AVE",
                        "Huevos sem 41": "HUEVOS_SEM_41",
                        "Población inicial": "POBLACION_INICIAL",
                        "Huevos / AA": "HUEVOS_POR_AA",
                        "Huevos STD 41": "HUEVOS_STD_41",
                        "% Cumplimiento": "PCT_CUMPLIMIENTO",
                        "% Huevos bomba": "PCT_HUEVOS_BOMBA",
                    }

                    data_prod = {
                        campo: [
                            st.session_state.datos_productivos
                            .get(lote, {})
                            .get(key, "Primera etapa" if key == "ETAPA" else 0)
                            for lote in lotes
                        ]
                        for campo, key in campos_prod.items()
                    }

                    df_prod_mail = pd.DataFrame(data_prod, index=lotes).T

                    df_etapa = df_prod_mail.loc[["Etapa"]]
                    df_num = df_prod_mail.drop(index=["Etapa"])

                    bloque_productivo_html = f"""
                    <h3>🏭 Datos productivos – Producción</h3>
                    {_estilizar_tabla_html(df_etapa.to_html(index=True, border=1), align_td="left")}
                    {tabla_html_limpia_invertida(df_num, {
                        "Huevos / AA": 2,
                        "% Cumplimiento": 2,
                        "% Huevos bomba": 2
                    })}
                    """
                else:
                    # Hembras
                    df_h_mail = pd.DataFrame({
                        campo: [
                            st.session_state.datos_productivos
                            .get(l, {}).get("HEMBRAS", {}).get(key, 0)
                            for l in lotes
                        ]
                        for campo, key in {
                            "Edad": "EDAD",
                            "Uniformidad (%)": "UNIFORMIDAD",
                            "Aves entregadas": "AVES_ENTREGADAS",
                            "Población inicial": "POBLACION_INICIAL",
                            "% Cumpl. aves": "PCT_CUMP_AVES",
                            "Peso": "PESO",
                            "Peso STD": "PESO_STD",
                            "% Cumpl. peso": "PCT_CUMP_PESO",
                        }.items()
                    }, index=lotes).T

                    # Machos
                    df_m_mail = pd.DataFrame({
                        campo: [
                            st.session_state.datos_productivos
                            .get(l, {}).get("MACHOS", {}).get(key, 0)
                            for l in lotes
                        ]
                        for campo, key in {
                            "Edad": "EDAD",
                            "Uniformidad (%)": "UNIFORMIDAD",
                            "Aves entregadas": "AVES_ENTREGADAS",
                            "Población inicial": "POBLACION_INICIAL",
                            "Peso": "PESO",
                            "Peso STD": "PESO_STD",
                            "% Cumpl. peso": "PCT_CUMP_PESO",
                        }.items()
                    }, index=lotes).T

                    bloque_productivo_html = f"""
                    <h3>🐔 Datos productivos – Levante (Hembras)</h3>
                    {tabla_html_limpia_invertida(df_h_mail, {
                        "Uniformidad (%)": 2,
                        "% Cumpl. aves": 2,
                        "% Cumpl. peso": 2,
                        "Peso": 3,
                        "Peso STD": 2
                    })}
                    <h3>🐔 Datos productivos – Levante (Machos)</h3>
                    {tabla_html_limpia_invertida(df_m_mail, {
                        "Uniformidad (%)": 2,
                        "% Cumpl. peso": 2,
                        "Peso": 3,
                        "Peso STD": 3
                    })}
                    """

                # =========================
                # CUERPO DEL CORREO
                # =========================
                cuerpo_html = f"""
                <html>
                <body style="font-family:Arial, sans-serif; font-size:12px;">
                    <h2>Bono Reproductoras GDP</h2>
                    <p><b>Granja:</b> {st.session_state.get("granja_seleccionada","")}</p>
                    <p><b>Tipo de proceso:</b> {tipo}</p>
                    <p><b>Lotes:</b> {", ".join(lotes)}</p>
                    <p><b>Fecha:</b> {pd.Timestamp.now().strftime("%Y-%m-%d %H:%M")}</p>

                    {bloque_productivo_html}

                    <h3>📦 Resumen por lote</h3>
                    {tabla_lote_html}

                    <h3>💰 Resultado final por trabajador</h3>
                    {tabla_resultado_html}

                    <p>{mensaje}</p>
                    <p><b>Equipo de Control de Gestión</b></p>
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
                st.error(f"❌ Error al enviar el correo: {e}")

















