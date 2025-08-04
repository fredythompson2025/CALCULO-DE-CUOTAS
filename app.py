import streamlit as st

try:
    st.title("Cálculo de Cuotas")
    capital = st.number_input("Capital:", min_value=0.0)
    tasa = st.number_input("Tasa de interés anual (%):", min_value=0.0)
    plazo = st.number_input("Plazo en meses:", min_value=1)

    if st.button("Calcular"):
        cuota = (capital * (tasa / 100)) / plazo
        st.success(f"Cuota mensual: {cuota:.2f}")
except Exception as e:
    st.error(f"Ocurrió un error: {e}")