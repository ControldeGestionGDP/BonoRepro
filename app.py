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

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Ingresar al sistema", use_container_width=True):
            st.session_state.ingresar = True
            st.rerun()

    st.stop()

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
# DESCUENTO POR FALTAS (EXACTO A EXCEL)
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
    return DESCUENTO_FALTAS.get(f, 0.50)  # 5 o más

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
        df_base[["DNI", "NOMBRE COMPLETO", "CARGO"]],
        on="DNI",
        how="left"
    )

    st.success("✅ Cruce de trabajadores realizado")

    # =========================
    # TIPO DE PROCESO
    # =========================
    tipo = st.radio(
        "Tipo de proceso",
        ["PRODUCCIÓN", "LEVANTE"],
        horizontal=True
    )

    reglas = REGLAS_PRODUCCION if tipo == "PRODUCCIÓN" else REGLAS_LEVANTE

    # =========================
    # LOTES
    # =========================
    lotes_txt = st.text_input(
        "Lotes (ejemplo: 211-212-213)",
        "211-212-213"
    )

    lotes = [l.strip() for l in lotes_txt.split("-") if l.strip()]

    st.subheader("🧬 Configuración por lote")

    config_lotes = {}
    cols = st.columns(len(lotes))

    for i, lote in enumerate(lotes):
        with cols[i]:
            genetica = st.text_input(f"Genética {lote}", "ROSS")
            monto = st.number_input(
                f"Monto S/ {lote}",
                min_value=0.0,
                value=1000.0,
                step=50.0
            )
            config_lotes[lote] = {
                "GENETICA": genetica.upper(),
                "MONTO": monto
            }

    # =========================
    # COLUMNAS PARTICIPACIÓN Y FALTAS
    # =========================
    for lote in lotes:
        df[f"%_{lote}"] = 0.0
    for lote in lotes:
        df[f"F_{lote}"] = 0

    # =========================
    # INICIALIZAR SESSION_STATE PARA TABLA
    # =========================
    if "tabla" not in st.session_state:
        st.session_state.tabla = df.copy()

    st.subheader("✍️ Registro por trabajador y lote")
    df_edit = st.data_editor(
        st.session_state.tabla,
        use_container_width=True,
        num_rows="fixed"
    )
    st.session_state.tabla = df_edit.copy()

    # =========================
    # ELIMINAR TRABAJADOR
    # =========================
    st.subheader("✂️ Eliminar trabajador (opcional)")
    dni_eliminar = st.text_input("Ingrese DNI a eliminar", key="eliminar")
    if st.button("Eliminar trabajador"):
        if dni_eliminar.strip():
            dni_eliminar = dni_eliminar.zfill(8)
            if dni_eliminar in st.session_state.tabla["DNI"].values:
                st.session_state.tabla = st.session_state.tabla[st.session_state.tabla["DNI"] != dni_eliminar]
                st.success(f"✅ Trabajador con DNI {dni_eliminar} eliminado")
            else:
                st.warning("⚠️ DNI no encontrado en la tabla")

    # =========================
    # BUSCAR Y AGREGAR TRABAJADOR
    # =========================
    st.subheader("🔍 Buscar trabajador por DNI")
    dni_buscar = st.text_input("Ingrese DNI para buscar", key="buscar")
    if st.button("Buscar trabajador"):
        if dni_buscar.strip():
            dni_buscar = dni_buscar.zfill(8)
            encontrado = df_base[df_base["DNI"] == dni_buscar]
            if not encontrado.empty:
                st.dataframe(encontrado, use_container_width=True)
                if st.button(f"💾 Agregar trabajador {dni_buscar} a registro"):
                    if dni_buscar not in st.session_state.tabla["DNI"].values:
                        nuevo = encontrado.copy()
                        for lote in lotes:
                            if f"%_{lote}" not in nuevo.columns:
                                nuevo[f"%_{lote}"] = 0.0
                            if f"F_{lote}" not in nuevo.columns:
                                nuevo[f"F_{lote}"] = 0
                        st.session_state.tabla = pd.concat([st.session_state.tabla, nuevo], ignore_index=True)
                        st.success(f"✅ Trabajador {dni_buscar} agregado al registro")
                    else:
                        st.warning("⚠️ Este trabajador ya está en el registro")
            else:
                st.warning("⚠️ DNI no encontrado en la base de trabajadores")

    # =========================
    # CÁLCULO DE PAGOS
    # =========================
    df_final = st.session_state.tabla.copy()
    columnas_pago = []

    for lote in lotes:

        def pago_lote(row):
            cargo = str(row["CARGO"]).upper()
            pct_cargo = reglas.get(cargo, 0)

            monto = config_lotes[lote]["MONTO"]
            participacion = float(row[f"%_{lote}"]) / 100
            faltas = row[f"F_{lote}"]

            if participacion <= 0:
                return 0.0

            pago = (
                pct_cargo *
                monto *
                participacion *
                factor_faltas(faltas)
            )

            return round(pago, 2)

        col_pago = f"PAGO_{lote}"
        df_final[col_pago] = df_final.apply(pago_lote, axis=1)
        columnas_pago.append(col_pago)

    df_final["TOTAL S/"] = df_final[columnas_pago].sum(axis=1)

    # =========================
    # RESULTADO FINAL
    # =========================
    st.subheader("💰 Resultado final")
    st.dataframe(df_final, use_container_width=True)

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
