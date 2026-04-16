import streamlit as st
import pandas as pd

# --- 1. CONFIGURACIÓN DE SEGURIDAD ---
PASSWORD_CORRECTA = "ovalle2026"

def check_password():
    if "password_ok" not in st.session_state:
        st.session_state["password_ok"] = False
    if not st.session_state["password_ok"]:
        st.markdown("<h2 style='text-align: center;'>🔐 Acceso Sistema Ferretería Ovalle</h2>", unsafe_allow_html=True)
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

# --- 2. LÓGICA DE BÚSQUEDA TIPO ACCESS ---
def buscar_coincidencias(df, term):
    if not term:
        return df
    palabras = term.lower().split()
    mask = df['DESCRIPCIÓN'].str.lower().apply(lambda x: all(p in str(x) for p in palabras))
    return df[mask]

# --- 3. INTERFAZ PRINCIPAL ---
if check_password():
    st.set_page_config(page_title="Búsqueda Ferretería Ovalle", layout="wide")

    st.markdown("""
        <style>
        .main { background-color: #1e1e1e; }
        .stTextInput > div > div > input { background-color: #ffffff !important; color: black !important; font-size: 20px; font-weight: bold; }
        .info-box { border: 2px solid #5bc0de; padding: 25px; border-radius: 10px; background-color: #262730; color: white; }
        .label-blue { color: #5bc0de; font-weight: bold; margin-bottom: 5px; }
        </style>
        """, unsafe_allow_html=True)

    # TU ENLACE DE GOOGLE SHEETS
    GSHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSS8fd7ccGW_AoCZzYCU0idkGpzDQqsb77NyF1lH7MT6DonkUKQNc3Uu-71Nfe-6w/pub?output=csv"

    @st.cache_data(ttl=60)
    def cargar_datos():
        try:
            df_raw = pd.read_csv(GSHEET_CSV_URL)
            df_raw.columns = [str(c).strip().upper() for c in df_raw.columns]
            df_raw = df_raw.rename(columns={'DESCRIPCION': 'DESCRIPCIÓN', 'PUBLICO': 'PÚBLICO'})
            df_raw['DESCRIPCIÓN'] = df_raw['DESCRIPCIÓN'].astype(str)
            return df_raw
        except Exception as e:
            st.error(f"Error: {e}")
            return None

    df = cargar_datos()

    if df is not None:
        st.markdown("<h1 style='color: white; font-size: 28px;'>BUSCAR PRODUCTO:</h1>", unsafe_allow_html=True)
        busqueda = st.text_input("", placeholder="Escriba palabras (ej: mezcladora cromo)...")

        df_filtrado = buscar_coincidencias(df, busqueda)

        col_tabla, col_info = st.columns([3, 2])

        with col_tabla:
            # Mostramos la tabla normal (sin selección para evitar el error de API)
            st.dataframe(
                df_filtrado[['ID', 'DESCRIPCIÓN', 'PÚBLICO', 'DISTRIBUIDOR']], 
                use_container_width=True, 
                height=450,
                hide_index=True
            )
            
            # Selector manual debajo de la tabla (Esto sustituye el clic en la fila)
            # Permite elegir el producto exacto de los resultados filtrados
            opciones = df_filtrado['DESCRIPCIÓN'].tolist()
            if opciones:
                seleccionado = st.selectbox("🎯 Seleccione un producto para ver detalle completo:", opciones)
                item = df_filtrado[df_filtrado['DESCRIPCIÓN'] == seleccionado].iloc[0]
            else:
                item = None

        with col_info:
            st.markdown("<h2 style='background-color: #103f54; color: white; padding: 10px;'>DETALLES</h2>", unsafe_allow_html=True)
            
            if item is not None:
                st.markdown(f"""
                <div class="info-box">
                    <p class="label-blue">DESCRIPCIÓN</p>
                    <p style="font-size: 20px;">{item.get('DESCRIPCIÓN', 'N/A')}</p>
                    <hr style="border-color: #5bc0de;">
                    
                    <p class="label-blue">PRECIO PÚBLICO</p>
                    <p style="font-size: 45px; font-weight: bold; color: #00ff00; margin-top: -10px;">
                        ${item.get('PÚBLICO', 0)}
                    </p>
                    
                    <br>
                    <details>
                        <summary style="color: #888; cursor: pointer;">Ver Precio Distribuidor</summary>
                        <div style="margin-top: 15px;">
                            <p class="label-blue" style="color: #ff4b4b;">COSTO DISTRIBUIDOR</p>
                            <p style="font-size: 28px; font-weight: bold;">
                                ${item.get('DISTRIBUIDOR', 0)}
                            </p>
                        </div>
                    </details>
                    
                    <div style="margin-top: 30px; border-top: 1px solid #444; padding-top: 10px; font-size: 11px; color: #777;">
                        ID: {item.get('ID', 'N/A')} | Libro: {item.get('LIBRO', 'N/A')} <br>
                        Actualizado: {item.get('FECHA ACTUALIZACION', 'N/A')}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.info("Escriba en el buscador para filtrar y elija un producto.")

        st.caption("Ferretería Ovalle v2.3 - Versión Estable")
