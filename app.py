import streamlit as st
import pandas as pd

# --- 1. CONFIGURACIÓN DE SEGURIDAD ---
PASSWORD_CORRECTA = "ovalle2026"

def check_password():
    if "password_ok" not in st.session_state:
        st.session_state["password_ok"] = False
    if not st.session_state["password_ok"]:
        st.markdown("<h2 style='text-align: center;'>🔐 Acceso Ferretería Ovalle</h2>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            pwd = st.text_input("Clave de sucursal:", type="password")
            if st.button("Entrar"):
                if pwd == PASSWORD_CORRECTA:
                    st.session_state["password_ok"] = True
                    st.rerun()
                else:
                    st.error("❌ Clave incorrecta")
        return False
    return True

if check_password():
    st.set_page_config(page_title="Búsqueda Ferretería Ovalle", layout="wide")

    # Estilo visual
    st.markdown("""
        <style>
        .main { background-color: #1e1e1e; }
        .stTextInput > div > div > input { background-color: #ffffff !important; color: black !important; font-size: 20px; }
        .info-box { border: 2px solid #5bc0de; padding: 20px; border-radius: 10px; background-color: #262730; color: white; }
        </style>
        """, unsafe_allow_html=True)

    # REEMPLAZA ESTE LINK por el que obtuviste al "Publicar en la web" (CSV)
    # Ejemplo: https://docs.google.com/spreadsheets/d/e/2PACX-1v.../pub?output=csv
    GSHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSS8fd7ccGW_AoCZzYCU0idkGpzDQqsb77NyF1lH7MT6DonkUKQNc3Uu-71Nfe-6w/pub?output=csv"

    @st.cache_data(ttl=60) # Se actualiza cada minuto
    def cargar_datos():
        try:
            # Google Sheets entrega el CSV al instante sin pedir contraseñas raras
            df = pd.read_csv(GSHEET_CSV_URL)
            df.columns = [str(c).strip().upper() for c in df.columns]
            df = df.rename(columns={'DESCRIPCION': 'DESCRIPCIÓN', 'PUBLICO': 'PÚBLICO'})
            return df
        except Exception as e:
            return f"Error: {e}"

    df = cargar_datos()

    if isinstance(df, str):
        st.error(f"Error al cargar datos: {df}")
        st.info("Asegúrate de haber 'Publicado en la web' como CSV.")
    else:
        st.markdown("<h1 style='color: white;'>BUSCAR PRODUCTO:</h1>", unsafe_allow_html=True)
        busqueda = st.text_input("", placeholder="Escriba descripción o código...")

        if busqueda:
            mask = df.astype(str).apply(lambda x: x.str.contains(busqueda, case=False)).any(axis=1)
            df_filtrado = df[mask]
        else:
            df_filtrado = df

        col1, col2 = st.columns([3, 2])
        with col1:
            cols_ver = [c for c in ['ID', 'DESCRIPCIÓN', 'DISTRIBUIDOR', 'PÚBLICO'] if c in df_filtrado.columns]
            st.dataframe(df_filtrado[cols_ver], use_container_width=True, height=550, hide_index=True)
        
        with col2:
            st.markdown("<h2 style='background-color: #103f54; color: white; padding: 10px;'>DETALLES</h2>", unsafe_allow_html=True)
            if not df_filtrado.empty and busqueda:
                item = df_filtrado.iloc[0]
                st.markdown(f"""
                <div class="info-box">
                    <p style="color: #5bc0de; font-weight: bold;">DESCRIPCIÓN</p>
                    <p style="font-size: 19px;">{item.get('DESCRIPCIÓN', 'N/A')}</p>
                    <hr>
                    <p style="color: #5bc0de; font-weight: bold;">PRECIO PÚBLICO</p>
                    <p style="font-size: 40px; font-weight: bold; color: #00ff00;">${item.get('PÚBLICO', 0)}</p>
                    <br>
                    <details>
                        <summary style="color: #888; cursor: pointer;">Ver Precio Distribuidor</summary>
                        <p style="font-size: 24px; color: #ff4b4b;">${item.get('DISTRIBUIDOR', 0)}</p>
                    </details>
                </div>
                """, unsafe_allow_html=True)

    st.caption("Ferretería Ovalle v2.0 - Sistema Estable")
