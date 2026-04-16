import streamlit as st
import pandas as pd
import requests
from io import BytesIO
import time

# --- 1. CONFIGURACIÓN DE SEGURIDAD ---
PASSWORD_CORRECTA = "ovalle2026"

def check_password():
    if "password_ok" not in st.session_state:
        st.session_state["password_ok"] = False

    if not st.session_state["password_ok"]:
        st.markdown("<h2 style='text-align: center; color: white;'>🔐 Acceso Sistema Ferretería Ovalle</h2>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            pwd = st.text_input("Introduce la clave de sucursal:", type="password")
            if st.button("Entrar al Sistema"):
                if pwd == PASSWORD_CORRECTA:
                    st.session_state["password_ok"] = True
                    st.rerun()
                else:
                    st.error("❌ Contraseña incorrecta")
        return False
    return True

# --- 2. LÓGICA DE CARGA Y SISTEMA ---
if check_password():
    st.set_page_config(page_title="Búsqueda Ferretería Ovalle", layout="wide")

    # Estilo CSS optimizado
    st.markdown("""
        <style>
        .main { background-color: #1e1e1e; }
        .stTextInput > div > div > input { background-color: #ffffff !important; color: black !important; font-size: 20px; font-weight: bold; }
        .info-box { border: 2px solid #5bc0de; padding: 20px; border-radius: 10px; background-color: #262730; color: white; }
        .label-blue { color: #5bc0de; font-weight: bold; }
        </style>
        """, unsafe_allow_html=True)

    # URL RECONSTRUIDA PARA EVITAR BLOQUEOS
    # Extraída de tu último vínculo compartido
    EXCEL_URL = "https://onedrive.live.com/download?resid=C0D8E1E31398ED93&authkey=!ACjFyb5MXKJIjXQ&em=2"

    @st.cache_data(ttl=300)
    def cargar_datos():
        # Usamos una sesión para mantener persistencia y evitar el Error 401
        session = requests.Session()
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8'
        }
        
        try:
            # Realizamos la petición
            response = session.get(EXCEL_URL, headers=headers, timeout=20)
            
            if response.status_code == 200:
                # Leemos el Excel desde los bytes descargados
                df_raw = pd.read_excel(BytesIO(response.content), engine='openpyxl')
                
                # Limpieza de nombres de columnas
                df_raw.columns = [str(c).strip().upper() for c in df_raw.columns]
                # Homologamos nombres con y sin tilde
                df_raw = df_raw.rename(columns={'DESCRIPCION': 'DESCRIPCIÓN', 'PUBLICO': 'PÚBLICO'})
                return df_raw
            else:
                return f"ERROR_{response.status_code}"
        except Exception as e:
            return str(e)

    # Intentar cargar
    datos = cargar_datos()

    # Manejo de errores visual
    if isinstance(datos, str):
        st.error(f"⚠️ Error de conexión: {datos}")
        st.info("OneDrive rechazó la conexión automática. Intenta refrescar la página o verifica que el archivo esté compartido públicamente.")
        if st.button("🔄 Reintentar"):
            st.cache_data.clear()
            st.rerun()
    else:
        df = datos
        st.markdown("<h1 style='color: white; font-size: 26px;'>BUSCAR PRODUCTO:</h1>", unsafe_allow_html=True)
        busqueda = st.text_input("", placeholder="Escriba descripción o ID del producto...")

        if busqueda:
            # Búsqueda en todo el documento
            mask = df.astype(str).apply(lambda x: x.str.contains(busqueda, case=False)).
