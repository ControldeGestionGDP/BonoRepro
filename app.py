import streamlit as st
import pandas as pd
from io import BytesIO

# =========================
# CONFIG GENERAL
# =========================
st.set_page_config(
    page_title="Bono Reproductoras GDP",
    layout="wide"
)

# =========================
# PORTADA FULL SCREEN
# =========================
if "ingresar" not in st.session_state:
    st.session_state.ingresar = False

if not st.session_state.ingresar:

    st.markdown(
        """
        <style>
        html, body, [class*="css"] {
            height: 100%;
            overflow: hidden;
        }

        .portada {
            height: 100vh;
            background-color: #2a3c7c;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            text-align: center;
            color: white;
        }

        .portada img {
            width: 150px;
            margin-bottom: 25px;
        }

        .portada h1 {
            font-size: 42px;
            margin-bottom: 10px;
        }

        .portada h3 {
            font-weight: 300;
            margin-bottom: 40px;
        }

        .btn-ingresar button {
            background-color: #ef933d !important;
            color: white !important;
            font-size: 18px !important;
            padding: 12px 36px !important;
            border-radius: 10px !important;
            border: none !important;
        }
        </style>

        <div class="portada">
            <img src="logo_empresa.png">
            <h1>🐔 BONO REPRODUCTORAS GDP</h1>
            <h3>Sistema de cálculo y distribución de bonos</h3>
            <p style="font-size:14px; color:#dddddd;">
                Desarrollado por <br>
                <strong>Gerencia de Control de Gestión</strong>
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns([4, 2, 4])
    with col2:
        if st.button("🚀 Ingresar al sistema", key="ingresar"):
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
# REGLAS POR CARGO
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
# DESCUENTO POR FALTAS (EXCEL)
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
    # TIPO
    # =========================
    tipo = st.radio("Tipo de proceso", ["PRODUCCIÓN", "LEVANTE"], horizontal=True)
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
    # PARTICIPACIÓN Y FALTAS
    # =========================
    for lote in lotes:
        df[f"%_{lote}"] = 0.0
        df[f"F_{lote}"] = 0

    st.subheader("✍️ Registro por trabajador y lote")
    df_edit = st.data_editor(df, use_container_width=True, num_rows="fixed")

    # =========================
    # CÁLCULO FINAL
    # =========================
    df_final = df_edit.copy()
    pagos = []

    for lote in lotes:

        def pago_lote(row):
            cargo = str(row["CARGO"]).upper()
            pct_cargo = reglas.get(cargo, 0)
            monto = config_lotes[lote]["MONTO"]
            participacion = float(row[f"%_{lote}"]) / 100
            faltas = row[f"F_{lote}"]

            if participacion <= 0:
                return 0.0

            return round(
                pct_cargo * monto * participacion * factor_faltas(faltas),
                2
            )

        col = f"PAGO_{lote}"
        df_final[col] = df_final.apply(pago_lote, axis=1)
        pagos.append(col)

    df_final["TOTAL S/"] = df_final[pagos].sum(axis=1)

    st.subheader("💰 Resultado final")
    st.dataframe(df_final, use_container_width=True)

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
