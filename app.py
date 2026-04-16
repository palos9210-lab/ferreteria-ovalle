import streamlit as st
import pandas as pd
import requests
from io import BytesIO

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

    # Estilo CSS para imitar tu interfaz oscura
    st.markdown("""
        <style>
        .main { background-color: #1e1e1e; }
        .stTextInput > div > div > input { background-color: #ffffff !important; color: black !important; font-size: 20px; font-weight: bold; }
        .info-box { border: 2px solid #5bc0de; padding: 20px; border-radius: 10px; background-color: #262730; color: white; }
        .label-blue { color: #5bc0de; font-weight: bold; }
        </style>
        """, unsafe_allow_html=True)

    # URL DIRECTA RECONSTRUIDA
    EXCEL_URL = "https://onedrive.live.com/download?resid=C0D8E1E31398ED93&authkey=!ACjFyb5MXKJIjXQ&em=2"

    @st.cache_data(ttl=300)
    def cargar_datos():
        session = requests.Session()
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36'
        }
        try:
            response = session.get(EXCEL_URL, headers=headers, timeout=20)
            if response.status_code == 200:
                df_raw = pd.read_excel(BytesIO(response.content), engine='openpyxl')
                # Normalización de columnas
                df_raw.columns = [str(c).strip().upper() for c in df_raw.columns]
                df_raw = df_raw.rename(columns={'DESCRIPCION': 'DESCRIPCIÓN', 'PUBLICO': 'PÚBLICO'})
                return df_raw
            else:
                return f"ERROR_{response.status_code}"
        except Exception as e:
            return str(e)

    datos = cargar_datos()

    if isinstance(datos, str):
        st.error(f"⚠️ Error de conexión: {datos}")
        if st.button("🔄 Reintentar"):
            st.cache_data.clear()
            st.rerun()
    else:
        df = datos
        st.markdown("<h1 style='color: white; font-size: 26px;'>BUSCAR PRODUCTO:</h1>", unsafe_allow_html=True)
        busqueda = st.text_input("", placeholder="Escriba descripción o ID del producto...")

        if busqueda:
            # Línea corregida (sin el punto final erróneo)
            mask = df.astype(str).apply(lambda x: x.str.contains(busqueda, case=False)).any(axis=1)
            df_filtrado = df[mask]
        else:
            df_filtrado = df

        col_tabla, col_info = st.columns([3, 2])

        with col_tabla:
            cols_ver = [c for c in ['ID', 'DESCRIPCIÓN', 'DISTRIBUIDOR', 'PÚBLICO'] if c in df_filtrado.columns]
            st.dataframe(
                df_filtrado[cols_ver], 
                use_container_width=True, 
                height=550,
                hide_index=True
            )

        with col_info:
            st.markdown("<h2 style='background-color: #103f54; color: white; padding: 10px;'>INFORMACIÓN</h2>", unsafe_allow_html=True)
            
            if not df_filtrado.empty and busqueda:
                item = df_filtrado.iloc[0]
                st.markdown(f"""
                <div class="info-box">
                    <p class="label-blue">DESCRIPCIÓN</p>
                    <p style="font-size: 19px;">{item.get('DESCRIPCIÓN', 'N/A')}</p>
                    <hr style="border-color: #5bc0de;">
                    
                    <p class="label-blue">PRECIO PÚBLICO</p>
                    <p style="font-size: 42px; font-weight: bold; color: #00ff00; margin-top: -10px;">
                        ${item.get('PÚBLICO', 0):,.2f}
                    </p>
                    
                    <br>
                    <details>
                        <summary style="color: #888; cursor: pointer;">Ver Precio Distribuidor</summary>
                        <div style="margin-top: 10px;">
                            <p class="label-blue" style="color: #ff4b4b;">COSTO DISTRIBUIDOR</p>
                            <p style="font-size: 28px; font-weight: bold;">
                                ${item.get('DISTRIBUIDOR', 0):,.2f}
                            </p>
                        </div>
                    </details>
                    
                    <div style="margin-top: 30px; border-top: 1px solid #444; padding-top: 10px; font-size: 11px; color: #666;">
                        Libro: {item.get('LIBRO', 'N/A')} | Actualización: {item.get('FECHA ACTUALIZACION', 'N/A')}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.info("Utilice el buscador para ver los detalles.")

        st.caption("Ferretería Ovalle v1.6 - Consulta Web")
