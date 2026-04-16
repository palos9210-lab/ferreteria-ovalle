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

# --- 2. LÓGICA DEL SISTEMA ---
if check_password():
    st.set_page_config(page_title="Búsqueda Ferretería Ovalle", layout="wide")

    # Estilo visual oscuro
    st.markdown("""
        <style>
        .main { background-color: #1e1e1e; }
        .stTextInput > div > div > input { background-color: #ffffff !important; color: black !important; font-size: 22px; }
        .info-box { border: 2px solid #5bc0de; padding: 25px; border-radius: 10px; background-color: #262730; color: white; }
        .label-blue { color: #5bc0de; font-weight: bold; }
        </style>
        """, unsafe_allow_html=True)

    # URL DIRECTA RECONSTRUIDA (Usando el ID c0d8e1e31398ed93)
    EXCEL_URL = "https://onedrive.live.com/download?resid=C0D8E1E31398ED93&authkey=!ANP_9uNqh76zPHY"

    @st.cache_data(ttl=300)
    def cargar_datos():
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        try:
            # Intentamos la descarga con la librería requests que es más flexible
            response = requests.get(EXCEL_URL, headers=headers, timeout=15)
            
            if response.status_code == 200:
                # Si la descarga es exitosa (Código 200)
                df_raw = pd.read_excel(BytesIO(response.content), engine='openpyxl')
                
                # Normalizar nombres de columnas (Quitar espacios y pasar a MAYÚSCULAS)
                df_raw.columns = [str(c).strip().upper() for c in df_raw.columns]
                
                # Asegurar que las columnas clave existan (con o sin tilde)
                df_raw = df_raw.rename(columns={'DESCRIPCION': 'DESCRIPCIÓN', 'PUBLICO': 'PÚBLICO'})
                return df_raw
            else:
                st.error(f"Error {response.status_code}: OneDrive no autorizó la descarga.")
                st.info("Sugerencia: Abre el Excel en OneDrive y verifica que esté compartido para 'Cualquier persona con el vínculo'.")
                return None
        except Exception as e:
            st.error(f"Error de conexión: {e}")
            return None

    df = cargar_datos()

    if df is not None:
        st.markdown("<h1 style='color: white;'>BUSCAR PRODUCTO:</h1>", unsafe_allow_html=True)
        busqueda = st.text_input("", placeholder="Escriba descripción, ID o palabra clave...")

        # Filtrado de datos
        if busqueda:
            # Buscamos en todas las columnas para facilitar el trabajo en sucursal
            mask = df.astype(str).apply(lambda x: x.str.contains(busqueda, case=False)).any(axis=1)
            df_filtrado = df[mask]
        else:
            df_filtrado = df

        col_tabla, col_info = st.columns([3, 2])

        with col_tabla:
            # Mostramos las columnas solicitadas
            columnas_a_mostrar = [c for c in ['ID', 'DESCRIPCIÓN', 'DISTRIBUIDOR', 'PÚBLICO'] if c in df_filtrado.columns]
            st.dataframe(
                df_filtrado[columnas_a_mostrar], 
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
                    
                    <div style="margin-top: 30px; border-top: 1px solid #444; padding-top: 10px; font-size: 12px; color: #777;">
                        Libro: {item.get('LIBRO', 'N/A')} <br>
                        Última actualización: {item.get('FECHA ACTUALIZACION', 'N/A')}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.info("Ingrese un término de búsqueda para ver el detalle.")

        st.caption("Ferretería Ovalle v1.2 - Sistema de Consulta Multi-sucursal")
