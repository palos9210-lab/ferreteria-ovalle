import streamlit as st
import pandas as pd
import requests
from io import BytesIO

# --- 1. SEGURIDAD ---
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

    # CSS para imitar tu interfaz oscura
    st.markdown("""
        <style>
        .main { background-color: #1e1e1e; }
        .stTextInput > div > div > input { background-color: #ffffff !important; color: black !important; font-size: 22px; }
        .info-box { border: 2px solid #5bc0de; padding: 20px; border-radius: 10px; background-color: #262730; color: white; }
        </style>
        """, unsafe_allow_html=True)

    # LINK DIRECTO (Evita el error 401 de los links 1drv.ms)
    EXCEL_URL = "https://onedrive.live.com/download?resid=C0D8E1E31398ED93&authkey=!ANP_9uNqh76zPHY&em=2"

    @st.cache_data(ttl=300)
    def cargar_datos():
        # Fingimos ser un navegador para que OneDrive no nos rechace
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        try:
            response = requests.get(EXCEL_URL, headers=headers)
            if response.status_code == 200:
                # Leemos el archivo desde la memoria (BytesIO)
                df_raw = pd.read_excel(BytesIO(response.content), engine='openpyxl')
                # Limpiamos nombres de columnas (Mayúsculas y sin espacios)
                df_raw.columns = [str(c).strip().upper() for c in df_raw.columns]
                # Aseguramos nombres con tildes para la interfaz
                df_raw = df_raw.rename(columns={'DESCRIPCION': 'DESCRIPCIÓN', 'PUBLICO': 'PÚBLICO'})
                return df_raw
            else:
                st.error(f"Error {response.status_code}: No se pudo acceder al archivo en la nube.")
                return None
        except Exception as e:
            st.error(f"Error de conexión: {e}")
            return None

    df = cargar_datos()

    if df is not None:
        st.markdown("<h1 style='color: white;'>BUSCAR:</h1>", unsafe_allow_html=True)
        busqueda = st.text_input("", placeholder="Escriba descripción o código del producto...")

        if busqueda:
            # Buscador inteligente en todas las columnas
            mask = df.astype(str).apply(lambda x: x.str.contains(busqueda, case=False)).any(axis=1)
            df_filtrado = df[mask]
        else:
            df_filtrado = df

        col_tabla, col_info = st.columns([3, 2])

        with col_tabla:
            # Columnas requeridas
            cols_ver = [c for c in ['ID', 'DESCRIPCIÓN', 'DISTRIBUIDOR', 'PÚBLICO'] if c in df_filtrado.columns]
            st.dataframe(df_filtrado[cols_ver], use_container_width=True, height=550, hide_index=True)

        with col_info:
            st.markdown("<h2 style='background-color: #103f54; color: white; padding: 5px 15px;'>INFORMACIÓN</h2>", unsafe_allow_html=True)
            if not df_filtrado.empty and busqueda:
                item = df_filtrado.iloc[0]
                st.markdown(f"""
                <div class="info-box">
                    <h3 style='color: #5bc0de; margin-top:0;'>DESCRIPCIÓN</h3>
                    <p style="font-size: 18px;">{item.get('DESCRIPCIÓN', 'N/A')}</p>
                    <hr style="border-color: #5bc0de;">
                    <p style="color: #5bc0de; margin-bottom:0;">PRECIO PÚBLICO</p>
                    <p style="font-size: 35px; font-weight: bold; color: #00ff00; margin-top:0;">${item.get('PÚBLICO', 0):,.2f}</p>
                    <br>
                    <details>
                        <summary style="color: #888; cursor: pointer;">Ver Precio Distribuidor (Costo)</summary>
                        <p style="font-size: 24px; color: #ff4b4b; font-weight: bold;">${item.get('DISTRIBUIDOR', 0):,.2f}</p>
                    </details>
                    <p style="font-size: 11px; color: #666; margin-top: 20px;">
                        Libro: {item.get('LIBRO', 'N/A')} | Actualizado: {item.get('FECHA ACTUALIZACION', 'N/A')}
                    </p>
                </div>
                """, unsafe_allow_html=True)

        st.caption("Ferretería Ovalle - Sistema de Consulta Multi-sucursal")
