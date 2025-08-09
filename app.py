# Checkbox para decidir si se muestra la tabla
mostrar_tabla = st.checkbox("Mostrar tabla de amortización", value=True)

# Cálculo de cuota y tabla
if monto and tasa and plazo:
    cuota = calcular_cuota(monto, tasa, plazo)  # tu función existente
    st.write(f"**Cuota mensual:** {cuota:,.2f}")

    if mostrar_tabla:
        df_resultado = generar_tabla_amortizacion(monto, tasa, plazo)  # tu función existente
        st.dataframe(df_resultado)

        # Botón de descarga
        df_exportar = df_resultado.copy()
        st.markdown(generar_link_descarga_excel(df_exportar), unsafe_allow_html=True)

