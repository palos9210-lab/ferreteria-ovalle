import streamlit as st
import pandas as pd
import requests
from io import BytesIO

# --- 1. CONFIGURACIÓN DE SEGURIDAD ---
# Clave para entrar al sistema en las sucursales
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

# --- 2. LÓGICA PRINCIPAL ---
if check_password():
    st.set_page_config(page_title="Búsqueda Ferretería Ovalle", layout="wide")

    # Estilo visual oscuro y profesional
    st.markdown("""
        <style>
        .main { background-color: #1e1e1e; }
        .stTextInput > div > div > input { background-color: #ffffff !important; color: black !important; font-size: 22px; font-weight: bold; }
        .info-box { border: 2px solid #5bc0de; padding: 25px; border-radius: 10px; background-color: #262730; color: white; }
        .label-blue { color: #5bc0de; font-weight: bold; margin-bottom: 0px; }
        </style>
        """, unsafe_allow_html=True)

    # TRANSFORMACIÓN DEL LINK:
    # Tu link original: https://1drv.ms/x/c/c0d8e1e31398ed93/IQAoxcm-TFyiSI10iie0BXszAVfjm5UJhorCr5yaxRntqkY?e=cgx4qc
    # El siguiente formato fuerza la descarga directa del archivo Excel:
    EXCEL_URL = "https://onedrive.live.com/download?resid=C0D8E1E31398ED93&authkey=!ACjFyb5MXKJIjXQ&em=2"

    @st.cache_data(ttl=300) # Se actualiza cada 5 minutos
    def cargar_datos():
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/110.0.0.0 Safari/537.36'}
        try:
            response = requests.get(EXCEL_URL, headers=headers, timeout=20)
            if response.status_code == 200:
                # Leemos el archivo usando BytesIO y el motor openpyxl
                df_raw = pd.read_excel(BytesIO(response.content), engine='openpyxl')
                
                # Normalizamos nombres de columnas (Sin espacios y en Mayúsculas)
                df_raw.columns = [str(c).strip().upper() for c in df_raw.columns]
                
                # Manejo de tildes para las columnas que usa el sistema
                df_raw = df_raw.rename(columns={'DESCRIPCION': 'DESCRIPCIÓN', 'PUBLICO': 'PÚBLICO'})
                return df_raw
            else:
                st.error(f"Error {response.status_code}: No se pudo conectar con el archivo de OneDrive.")
                return None
        except Exception as e:
            st.error(f"Error de conexión: {e}")
            return None

    df = cargar_datos()

    if df is not None:
        st.markdown("<h1 style='color: white; font-size: 28px;'>BUSCAR PRODUCTO:</h1>", unsafe_allow_html=True)
        busqueda = st.text_input("", placeholder="Escriba descripción, ID o palabra clave...")

        # Filtrado inteligente
        if busqueda:
            mask = df.astype(str).apply(lambda x: x.str.contains(busqueda, case=False)).any(axis=1)
            df_filtrado = df[mask]
        else:
            df_filtrado = df

        col_tabla, col_info = st.columns([3, 2])

        with col_tabla:
            # Columnas indicadas: Id, DESCRIPCIÓN, DISTRIBUIDOR y PÚBLICO
            cols_ver = [c for c in ['ID', 'DESCRIPCIÓN', 'DISTRIBUIDOR', 'PÚBLICO'] if c in df_filtrado.columns]
            st.dataframe(
                df_filtrado[cols_ver], 
                use_container_width=True, 
                height=600,
                hide_index=True
            )

        with col_info:
            st.markdown("<h2 style='background-color: #103f54; color: white; padding: 10px;'>INFORMACIÓN</h2>", unsafe_allow_html=True)
            
            if not df_filtrado.empty and busqueda:
                item = df_filtrado.iloc[0]
                
                st.markdown(f"""
                <div class="info-box">
                    <p class="label-blue">DESCRIPCIÓN</p>
                    <p style="font-size: 20px;">{item.get('DESCRIPCIÓN', 'N/A')}</p>
                    <hr style="border-color: #5bc0de;">
                    
                    <p class="label-blue">PRECIO PÚBLICO</p>
                    <p style="font-size: 40px; font-weight: bold; color: #00ff00; margin-top: -10px;">
                        ${item.get('PÚBLICO', 0):,.2f}
                    </p>
                    
                    <br>
                    <details>
                        <summary style="color: #888; cursor: pointer;">Ver Precio Distribuidor (Costo)</summary>
                        <div style="margin-top: 10px;">
                            <p class="label-blue" style="color: #ff4b4b;">COSTO DISTRIBUIDOR</p>
                            <p style="font-size: 28px; font-weight: bold; color: white;">
                                ${item.get('DISTRIBUIDOR', 0):,.2f}
                            </p>
                        </div>
                    </details>
                    
                    <div style="margin-top: 30px; border-top: 1px solid #444; padding-top: 10px; font-size: 11px; color: #777;">
                        Libro: {item.get('LIBRO', 'N/A')} <br>
                        Fecha de actualización: {item.get('FECHA ACTUALIZACION', 'N/A')}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.info("Escriba en el buscador superior para ver el detalle de un producto.")

        st.caption("Ferretería Ovalle v1.3 - Sistema de Consulta Web")
