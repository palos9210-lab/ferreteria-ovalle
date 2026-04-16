with col_info:
            st.markdown("<h2 style='background-color: #103f54; color: white; padding: 10px;'>DETALLES</h2>", unsafe_allow_html=True)
            
            if item is not None:
                # Extraemos los valores para evitar errores de formato
                desc = item.get('DESCRIPCIÓN', 'N/A')
                precio_pub = item.get('PÚBLICO', 0)
                precio_dist = item.get('DISTRIBUIDOR', 0)
                id_prod = item.get('ID', 'N/A')
                libro = item.get('LIBRO', 'N/A')
                fecha = item.get('FECHA ACTUALIZACION', 'N/A')

                # Renderizamos el HTML correctamente
                st.markdown(f"""
                <div class="info-box">
                    <p class="label-blue" style="color: #5bc0de; font-weight: bold;">DESCRIPCIÓN</p>
                    <p style="font-size: 18px; color: white;">{desc}</p>
                    <hr style="border-color: #5bc0de;">
                    
                    <p class="label-blue" style="color: #5bc0de; font-weight: bold;">PRECIO PÚBLICO</p>
                    <p style="font-size: 45px; font-weight: bold; color: #00ff00; margin-top: -10px;">
                        $ {precio_pub:,.2f}
                    </p>
                    
                    <br>
                    <details style="color: #888; cursor: pointer;">
                        <summary>Ver Precio Distribuidor</summary>
                        <div style="margin-top: 15px; background-color: #1e1e1e; padding: 10px; border-radius: 5px;">
                            <p style="color: #ff4b4b; font-weight: bold; margin-bottom: 0;">COSTO DISTRIBUIDOR</p>
                            <p style="font-size: 28px; font-weight: bold; color: white; margin-top: 0;">
                                $ {precio_dist:,.2f}
                            </p>
                        </div>
                    </details>
                    
                    <div style="margin-top: 30px; border-top: 1px solid #444; padding-top: 10px; font-size: 11px; color: #777;">
                        ID: {id_prod} | Libro: {libro} <br>
                        Actualizado: {fecha}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.info("💡 Selecciona un producto del menú desplegable debajo de la tabla.")
