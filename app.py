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

# --- 2. LÓGICA DE BÚSQUEDA TIPO ACCESS ---
def buscar_coincidencias(df, term):
    if not term:
        return df
    # Separamos la búsqueda por palabras (ej: "mezcla cromo" busca ambas palabras en cualquier orden)
    palabras = term.lower().split()
    # Filtramos: Todas las palabras deben estar presentes en la columna DESCRIPCIÓN
    mask = df['DESCRIPCIÓN'].str.lower().apply(lambda x: all(p in str(x) for p in palabras))
    return df[mask]

# --- 3. INTERFAZ PRINCIPAL ---
if check_password():
    st.set_page_config(page_title="Búsqueda Ferretería Ovalle", layout="wide")

    # Estilo visual que imita tu sistema original
    st.markdown("""
        <style>
        .main { background-color: #1e1e1e; }
        .stTextInput > div > div > input { background-color: #ffffff !important; color: black !important; font-size: 20px; font-weight: bold; }
        .info-box { border: 2px solid #5bc0de; padding: 25px; border-radius: 10px; background-color: #262730; color: white; }
        .label-blue { color: #5bc0de; font-weight: bold; margin-bottom: 5px; }
        </style>
        """, unsafe_allow_html=True)

    # ENLACE DE GOOGLE SHEETS PROPORCIONADO
    GSHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSS8fd7ccGW_AoCZzYCU0idkGpzDQqsb77NyF1lH7MT6DonkUKQNc3Uu-71Nfe-6w/pub?output=csv"

    @st.cache_data(ttl=60) # Sincroniza cambios cada 60 segundos
    def cargar_datos():
        try:
            # Lectura directa desde Google Drive (Sheets)
            df_raw = pd.read_csv(GSHEET_CSV_URL)
            # Normalización de nombres de columnas (Mayúsculas y sin espacios)
            df_raw.columns = [str(c).strip().upper() for c in df_raw.columns]
            # Homologamos nombres comunes
            df_raw = df_raw.rename(columns={'DESCRIPCION': 'DESCRIPCIÓN', 'PUBLICO': 'PÚBLICO'})
            # Aseguramos que la descripción sea texto para evitar errores de búsqueda
            df_raw['DESCRIPCIÓN'] = df_raw['DESCRIPCIÓN'].astype(str)
            return df_raw
        except Exception as e:
            st.error(f"Error al conectar con la base de datos de Google: {e}")
            return None

    df = cargar_datos()

    if df is not None:
        st.markdown("<h1 style='color: white; font-size: 28px;'>BUSCAR PRODUCTO:</h1>", unsafe_allow_html=True)
        busqueda = st.text_input("", placeholder="Escriba palabras del producto (ej: mezcladora fregadero)...")

        # 1. Aplicamos búsqueda flexible (Punto 1: palabras desordenadas)
        df_filtrado = buscar_coincidencias(df, busqueda)

        col_tabla, col_info = st.columns([3, 2])

        with col_tabla:
            # 2. Tabla Interactiva (Punto 2: clic para ver info instantánea)
            seleccion = st.dataframe(
                df_filtrado[['ID', 'DESCRIPCIÓN', 'PÚBLICO', 'DISTRIBUIDOR']], 
                use_container_width=True, 
                height=600,
                hide_index=True,
                on_select="rerun", # Esto permite que al tocar una fila se actualice el panel derecho
                selection_mode="single"
            )

        with col_info:
            st.markdown("<h2 style='background-color: #103f54; color: white; padding: 10px;'>INFORMACIÓN</h2>", unsafe_allow_html=True)
            
            item = None
            # Prioridad 1: Fila seleccionada por el usuario con el mouse
            if len(seleccion.selection.rows) > 0:
                idx = seleccion.selection.rows[0]
                item = df_filtrado.iloc[idx]
            # Prioridad 2: Si hay búsqueda pero no selección, mostrar el primer resultado
            elif not df_filtrado.empty and busqueda:
                item = df_filtrado.iloc[0]

            if item is not None:
                st.markdown(f"""
                <div class="info-box">
                    <p class="label-blue">DESCRIPCIÓN</p>
                    <p style="font-size: 20px; font-weight: 500;">{item.get('DESCRIPCIÓN', 'N/A')}</p>
                    <hr style="border-color: #5bc0de;">
                    
                    <p class="label-blue">PRECIO PÚBLICO</p>
                    <p style="font-size: 45px; font-weight: bold; color: #00ff00; margin-top: -10px;">
                        ${item.get('PÚBLICO', 0):,.2f}
                    </p>
                    
                    <br>
                    <details>
                        <summary style="color: #888; cursor: pointer;">Ver Precio Distribuidor (Costo)</summary>
                        <div style="margin-top: 15px;">
                            <p class="label-blue" style="color: #ff4b4b;">COSTO DISTRIBUIDOR</p>
                            <p style="font-size: 28px; font-weight: bold;">
                                ${item.get('DISTRIBUIDOR', 0):,.2f}
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
                st.info("💡 Haz clic en cualquier producto de la tabla para ver su detalle.")

        st.caption("Ferretería Ovalle v2.2 - Sistema Web Multi-sucursal (Google Drive)")

        st.caption("Ferretería Ovalle v1.7 - Búsqueda Flexible e Interactiva")
