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
        .stTextInput > div > div > input { background-color: #ffffff; color: black; font-size: 22px; }
        .info-box { border: 2px solid #5bc0de; padding: 20px; border-radius: 10px; background-color: #262730; color: white; }
        </style>
        """, unsafe_allow_html=True)

    # ESTA ES LA URL CORRECTA (Direct Download)
    # Usamos tu ID de archivo: c0d8e1e31398ed93
    EXCEL_URL = "https://onedrive.live.com/download?resid=C0D8E1E31398ED93&authkey=!ANP_9uNqh76zPHY&em=2"

    @st.cache_data(ttl=300)
    def cargar_datos():
        # Fingimos ser un navegador para evitar el error 401
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124'}
        try:
            response = requests.get(EXCEL_URL, headers=headers)
            if response.status_code == 200:
                df_raw = pd.read_excel(BytesIO(response.content), engine='openpyxl')
                # Normalizar nombres de columnas
                df_raw.columns = [str(c).strip().upper() for c in df_raw.columns]
                # Corregir tildes comunes para que el buscador no falle
                df_raw = df_raw.rename(columns={'DESCRIPCION': 'DESCRIPCIÓN', 'PUBLICO': 'PÚBLICO'})
                return df_raw
            else:
                st.error(f"Error 401: OneDrive rechazó la conexión. Código: {response.status_code}")
                return None
        except Exception as e:
            st.error(f"Error técnico: {e}")
            return None

    df = cargar_datos()

    if df is not None:
        st.markdown("<h1 style='color: white;'>BUSCAR:</h1>", unsafe_allow_html=True)
        busqueda = st.text_input("", placeholder="Escriba descripción o ID...")

        if busqueda:
            mask = df.astype(str).apply(lambda x: x.str.contains(busqueda, case=False)).any(axis=1)
            df_filtrado = df[mask]
        else:
            df_filtrado = df

        col_tabla, col_info = st.columns([3, 2])

        with col_tabla:
            # Seleccionamos solo las columnas que necesitas ver
            cols_a_ver = [c for c in ['ID', 'DESCRIPCIÓN', 'DISTRIBUIDOR', 'PÚBLICO'] if c in df_filtrado.columns]
            st.dataframe(df_filtrado[cols_a_ver], use_container_width=True, height=550, hide_index=True)

        with col_info:
            st.markdown("<h2 style='background-color: #103f54; color: white; padding: 5px;'>INFORMACIÓN</h2>", unsafe_allow_html=True)
            if not df_filtrado.empty and busqueda:
                item = df_filtrado.iloc[0]
                st.markdown(f"""
                <div class="info-box">
                    <h3 style='color: #5bc0de;'>DESCRIPCIÓN</h3>
                    <p style="font-size: 18px;">{item.get('DESCRIPCIÓN', 'N/A')}</p>
                    <hr>
                    <p style="color: #5bc0de;">PRECIO PÚBLICO</p>
                    <p style="font-size: 32px; font-weight: bold; color: #00ff00;">${item.get('PÚBLICO', 0):,.2f}</p>
                    <br>
                    <details>
                        <summary style="color: #888; cursor: pointer;">Ver Precio Distribuidor</summary>
                        <p style="font-size: 24px; color: #ff4b4b;">${item.get('DISTRIBUIDOR', 0):,.2f}</p>
                    </details>
                    <p style="font-size: 12px; color: #555; margin-top: 15px;">
                        Actualizado: {item.get('FECHA ACTUALIZACION', 'N/A')}
                    </p>
                </div>
                """, unsafe_allow_html=True)

        st.caption("Ferretería Ovalle v1.1 - Sistema Multi-sucursal")
