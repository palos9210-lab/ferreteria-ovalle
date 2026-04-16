import streamlit as st
import pandas as pd
import requests
from io import BytesIO
import base64

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

# --- 2. LÓGICA DE DATOS ---
if check_password():
    st.set_page_config(page_title="Búsqueda Ferretería Ovalle", layout="wide")

    # URL base de compartir (la que me pasaste anteriormente)
    url_compartir = "https://1drv.ms/x/c/c0d8e1e31398ed93/IQAoxcm-TFyiSI10iie0BXszAVfjm5UJhorCr5yaxRntqkY?e=cgx4qc"

    def crear_url_directa(url):
        # Este método convierte el link de compartir en un link de descarga directa "limpio"
        base64_enqueue = base64.b64encode(url.encode("utf-8")).decode("utf-8")
        final_share_url = "https://api.onedrive.com/v1.0/shares/u!" + base64_enqueue.rstrip("=").replace("/", "_").replace("+", "-") + "/root/content"
        return final_share_url

    @st.cache_data(ttl=300)
    def cargar_datos():
        url_final = crear_url_directa(url_compartir)
        headers = {'User-Agent': 'Mozilla/5.0'}
        try:
            response = requests.get(url_final, headers=headers, timeout=20)
            if response.status_code == 200:
                df_raw = pd.read_excel(BytesIO(response.content), engine='openpyxl')
                df_raw.columns = [str(c).strip().upper() for c in df_raw.columns]
                df_raw = df_raw.rename(columns={'DESCRIPCION': 'DESCRIPCIÓN', 'PUBLICO': 'PÚBLICO'})
                return df_raw
            else:
                return f"ERROR_{response.status_code}"
        except Exception as e:
            return str(e)

    datos = cargar_datos()

    if isinstance(datos, str):
        st.error(f"⚠️ Error de servidor (Microsoft 500/401).")
        st.write("OneDrive está limitando la conexión. Intentando método alternativo...")
        # Botón de emergencia para limpiar caché
        if st.button("🔄 Forzar Reconexión"):
            st.cache_data.clear()
            st.rerun()
    else:
        df = datos
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
            st.markdown("<h2 style='background-color: #103f54; color: white; padding: 10px;'>INFORMACIÓN</h2>", unsafe_allow_html=True)
            if not df_filtrado.empty and busqueda:
                item = df_filtrado.iloc[0]
                st.markdown(f"""
                <div style="border: 2px solid #5bc0de; padding: 20px; border-radius: 10px; background-color: #262730; color: white;">
                    <p style="color: #5bc0de; font-weight: bold;">DESCRIPCIÓN</p>
                    <p style="font-size: 19px;">{item.get('DESCRIPCIÓN', 'N/A')}</p>
                    <hr>
                    <p style="color: #5bc0de; font-weight: bold;">PRECIO PÚBLICO</p>
                    <p style="font-size: 40px; font-weight: bold; color: #00ff00;">${item.get('PÚBLICO', 0):,.2f}</p>
                    <br>
                    <details>
                        <summary style="color: #888; cursor: pointer;">Ver Precio Distribuidor</summary>
                        <p style="font-size: 24px; color: #ff4b4b;">${item.get('DISTRIBUIDOR', 0):,.2f}</p>
                    </details>
                </div>
                """, unsafe_allow_html=True)
