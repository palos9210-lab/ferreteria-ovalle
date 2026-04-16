import streamlit as st
import pandas as pd
import requests
from io import BytesIO

# --- SEGURIDAD ---
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

    # CSS Interfaz
    st.markdown("""
        <style>
        .main { background-color: #1e1e1e; }
        .stTextInput > div > div > input { background-color: #ffffff !important; color: black !important; font-size: 20px; }
        .info-box { border: 2px solid #5bc0de; padding: 20px; border-radius: 10px; background-color: #262730; color: white; }
        </style>
        """, unsafe_allow_html=True)

    # NUEVO ENLACE API ONEDRIVE
    EXCEL_URL = "https://api.onedrive.com/v1.0/shares/u!aHR0cHM6Ly8xZHJ2Lm1zL3gvYy9jMGQ4ZTFlMzEzOThlZDkzL0lRQW94Y20tVEZ5aVNJMTBpaWUwQlhzekFWZmptNVVKaG9yQ3I1eWF4Um50cWtZP2U9Y2d4NHFj/root/content"

    @st.cache_data(ttl=300)
    def cargar_datos():
        try:
            # Usamos un tiempo de espera (timeout) corto para detectar fallos rápido
            response = requests.get(EXCEL_URL, timeout=10)
            if response.status_code == 200:
                # Cargamos con motor openpyxl
                df_raw = pd.read_excel(BytesIO(response.content), engine='openpyxl')
                # Normalizar columnas
                df_raw.columns = [str(c).strip().upper() for c in df_raw.columns]
                df_raw = df_raw.rename(columns={'DESCRIPCION': 'DESCRIPCIÓN', 'PUBLICO': 'PÚBLICO'})
                return df_raw
            else:
                return f"Error {response.status_code}"
        except Exception as e:
            return str(e)

    resultado = cargar_datos()

    # Si el resultado es un String, significa que hubo un error
    if isinstance(resultado, str):
        st.error(f"⚠️ No se pudo conectar con OneDrive: {resultado}")
        st.info("Recomendación: Verifica que el archivo no esté abierto y bloqueado por otro usuario en la web.")
        if st.button("🔄 Reintentar Conexión"):
            st.cache_data.clear()
            st.rerun()
    else:
        df = resultado
        st.markdown("<h1 style='color: white;'>BUSCAR:</h1>", unsafe_allow_html=True)
        busqueda = st.text_input("", placeholder="Escriba descripción o código...")

        if busqueda:
            mask = df.astype(str).apply(lambda x: x.str.contains(busqueda, case=False)).any(axis=1)
            df_filtrado = df[mask]
        else:
            df_filtrado = df

        c1, c2 = st.columns([3, 2])

        with c1:
            cols = [c for c in ['ID', 'DESCRIPCIÓN', 'DISTRIBUIDOR', 'PÚBLICO'] if c in df_filtrado.columns]
            st.dataframe(df_filtrado[cols], use_container_width=True, height=500, hide_index=True)

        with c2:
            st.markdown("<h2 style='background-color: #103f54; color: white; padding: 5px;'>DETALLES</h2>", unsafe_allow_html=True)
            if not df_filtrado.empty and busqueda:
                item = df_filtrado.iloc[0]
                st.markdown(f"""
                <div class="info-box">
                    <p style="color: #5bc0de; margin-bottom:0;">DESCRIPCIÓN</p>
                    <p style="font-size: 18px;">{item.get('DESCRIPCIÓN', 'N/A')}</p>
                    <hr>
                    <p style="color: #5bc0de; margin-bottom:0;">PRECIO PÚBLICO</p>
                    <p style="font-size: 35px; font-weight: bold; color: #00ff00;">${item.get('PÚBLICO', 0):,.2f}</p>
                    <br>
                    <details>
                        <summary style="color: #888; cursor: pointer;">Ver Precio Distribuidor</summary>
                        <p style="font-size: 24px; color: #ff4b4b;">${item.get('DISTRIBUIDOR', 0):,.2f}</p>
                    </details>
                </div>
                """, unsafe_allow_html=True)

        st.caption("Ferretería Ovalle v1.4")
