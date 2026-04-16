import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN DE SEGURIDAD
# Cambia 'admin123' por la contraseña que quieras para tus sucursales
PASSWORD_CORRECTA = "ovalle2026"

def check_password():
    if "password_ok" not in st.session_state:
        st.session_state["password_ok"] = False

    if not st.session_state["password_ok"]:
        st.title("🔐 Acceso Sistema Ferretería")
        pwd = st.text_input("Introduce la clave de sucursal:", type="password")
        if st.button("Entrar"):
            if pwd == PASSWORD_CORRECTA:
                st.session_state["password_ok"] = True
                st.rerun()
            else:
                st.error("Contraseña incorrecta")
        return False
    return True

# Solo si la contraseña es correcta, ejecutamos el resto
if check_password():
    st.set_page_config(page_title="Búsqueda Ferretería Ovalle", layout="wide")

    # URL de tu Excel en OneDrive (Asegúrate que termine en &download=1)
    EXCEL_URL = "TU_LINK_DE_ONEDRIVE_AQUI"

    @st.cache_data(ttl=300) # Actualiza cada 5 minutos
    def cargar_datos():
        return pd.read_excel("https://1drv.ms/x/c/c0d8e1e31398ed93/ESjFyb5MXKJIjXSKJ7QFezMBAD3_9uNqh76zPHYfiaq4-g?e=0XJ5Nz&download=1")

    try:
        df = cargar_datos()
        
        # Interfaz de búsqueda
        st.markdown("<h1 style='text-align: center; color: #5bc0de;'>BUSCAR PRODUCTO</h1>", unsafe_allow_html=True)
        busqueda = st.text_input("", placeholder="Escribe descripción o ID...")

        col1, col2 = st.columns([2, 1])

        # Filtrado
        if busqueda:
            mask = df.astype(str).apply(lambda x: x.str.contains(busqueda, case=False)).any(axis=1)
            resultado = df[mask]
        else:
            resultado = df

        with col1:
            st.dataframe(resultado[['Id', 'DESCRIPCIÓN', 'PÚBLICO']], use_container_width=True, height=500)

        with col2:
            st.markdown("### DETALLES")
            if not resultado.empty and busqueda:
                item = resultado.iloc[0]
                st.markdown(f"""
                <div style="background-color: #262730; padding: 20px; border-radius: 10px; border: 1px solid #5bc0de">
                    <h4 style="color: #5bc0de">DESCRIPCIÓN</h4>
                    <p style="font-size: 18px;">{item['DESCRIPCIÓN']}</p>
                    <hr>
                    <h4 style="color: #5bc0de">PRECIO PÚBLICO</h4>
                    <p style="font-size: 35px; font-weight: bold; color: #00ff00;">${item['PÚBLICO']:,.2f}</p>
                    <hr>
                    <details>
                        <summary style="color: gray; cursor: pointer;">Ver Precio Distribuidor (Costo)</summary>
                        <p style="font-size: 20px; color: #ff4b4b;">${item['DISTRIBUIDOR']:,.2f}</p>
                    </details>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.info("Ingresa una búsqueda para ver detalles.")

    except Exception as e:
        st.error("Error al conectar con la base de datos de OneDrive. Verifica el link.")
        st.write(e)
