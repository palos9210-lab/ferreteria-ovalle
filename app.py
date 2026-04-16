import streamlit as st
import pandas as pd

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

# --- 2. LÓGICA DE BÚSQUEDA ---
def buscar_coincidencias(df, term):
    if not term:
        return df
    palabras = term.lower().split()
    mask = df['DESCRIPCIÓN'].str.lower().apply(lambda x: all(p in str(x) for p in palabras))
    return df[mask]

# --- 3. INTERFAZ PRINCIPAL ---
if check_password():
    st.set_page_config(page_title="Búsqueda Ferretería Ovalle", layout="wide")

    # Estilo CSS ADAPTABLE y limpieza de diseño
    st.markdown("""
        <style>
        .main { background-color: #1e1e1e; }
        .stTextInput > div > div > input, .stSelectbox > div > div > div { 
            background-color: #ffffff !important; color: black !important; font-size: 18px !important; font-weight: bold !important; 
        }
        .info-box { border: 2px solid #5bc0de; padding: 25px; border-radius: 10px; background-color: #262730; color: white; }
        .label-blue { color: #5bc0de; font-weight: bold; margin-bottom: 5px; font-size: 0.9em; }
        .desc-text { font-size: clamp(16px, 2vw, 20px); color: white; line-height: 1.4; }
        .precio-publico { font-size: clamp(35px, 5vw, 50px); font-weight: bold; color: #00ff00; margin-top: -10px; }
        .precio-dist { font-size: clamp(22px, 4vw, 28px); font-weight: bold; color: white; }
        </style>
        """, unsafe_allow_html=True)

    # ENLACE DE GOOGLE SHEETS
    GSHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSS8fd7ccGW_AoCZzYCU0idkGpzDQqsb77NyF1lH7MT6DonkUKQNc3Uu-71Nfe-6w/pub?output=csv"

    @st.cache_data(ttl=60)
    def cargar_datos():
        try:
            df_raw = pd.read_csv(GSHEET_CSV_URL)
            df_raw.columns = [str(c).strip().upper() for c in df_raw.columns]
            df_raw = df_raw.rename(columns={'DESCRIPCION': 'DESCRIPCIÓN', 'PUBLICO': 'PÚBLICO'})
            df_raw['DESCRIPCIÓN'] = df_raw['DESCRIPCIÓN'].astype(str)
            for col in ['PÚBLICO', 'DISTRIBUIDOR']:
                if col in df_raw.columns:
                    df_raw[col] = pd.to_numeric(df_raw[col].astype(str).str.replace('[$,]', '', regex=True), errors='coerce').fillna(0)
            return df_raw
        except Exception as e:
            st.error(f"Error: {e}")
            return None

    df = cargar_datos()

    if df is not None:
        st.markdown("<h1 style='color: white; font-size: clamp(20px, 3vw, 28px);'>BUSCAR:</h1>", unsafe_allow_html=True)
        busqueda = st.text_input("", placeholder="1. Escriba para filtrar la lista...")

        df_filtrado = buscar_coincidencias(df, busqueda)

        col_tabla, col_info = st.columns([3, 2])

        with col_tabla:
            # Mostramos la tabla solo como referencia visual (sin selección para evitar errores)
            st.dataframe(
                df_filtrado[['ID', 'DESCRIPCIÓN', 'PÚBLICO', 'DISTRIBUIDOR']], 
                use_container_width=True, 
                height=400,
                hide_index=True
            )
            
            # EL SELECTOR MÁGICO (Punto clave para el Enter)
            # Este componente responde perfectamente a Flechas y Enter
            opciones = df_filtrado['DESCRIPCIÓN'].tolist()
            if opciones:
                seleccionado = st.selectbox(
                    "🎯 2. Use FLECHAS y presione ENTER para seleccionar el producto:", 
                    opciones,
                    index=0 # Por defecto selecciona el primero de la búsqueda
                )
                item = df_filtrado[df_filtrado['DESCRIPCIÓN'] == seleccionado].iloc[0]
            else:
                item = None

        with col_info:
            st.markdown("<h2 style='background-color: #103f54; color: white; padding: 10px; font-size: clamp(18px, 2.5vw, 24px);'>DETALLES</h2>", unsafe_allow_html=True)
            
            if item is not None:
                desc = item.get('DESCRIPCIÓN', 'N/A')
                precio_pub = item.get('PÚBLICO', 0)
                precio_dist = item.get('DISTRIBUIDOR', 0)
                id_prod = item.get('ID', 'N/A')
                libro = item.get('LIBRO', 'N/A')
                fecha = item.get('FECHA ACTUALIZACION', 'N/A')

                html_card = f"""
<div class="info-box">
<p class="label-blue">DESCRIPCIÓN</p>
<p class="desc-text">{desc}</p>
<hr style="border-color: #5bc0de;">
<p class="label-blue">PRECIO PÚBLICO</p>
<p class="precio-publico">$ {precio_pub:,.2f}</p>
<br>
<details style="color: #888; cursor: pointer;">
<summary>Ver Precio Distribuidor</summary>
<div style="margin-top: 15px; background-color: #1e1e1e; padding: 15px; border-radius: 5px; border: 1px solid #ff4b4b;">
<p style="color: #ff4b4b; font-weight: bold; margin-bottom: 0;">COSTO DISTRIBUIDOR</p>
<p class="precio-dist">$ {precio_dist:,.2f}</p>
</div>
</details>
<div style="margin-top: 30px; border-top: 1px solid #444; padding-top: 10px; font-size: 0.8em; color: #777;">
ID: {id_prod} | Libro: {libro} <br>
Actualizado: {fecha}
</div>
</div>
"""
                st.markdown(html_card, unsafe_allow_html=True)
            else:
                st.info("💡 Escriba en el buscador para filtrar.")

        st.caption("Ferretería Ovalle v3.0 - Control Total por Teclado")
