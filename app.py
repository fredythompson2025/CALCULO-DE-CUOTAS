
 
  import streamlit as st
import pandas as pd
from io import BytesIO
import base64
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
import locale

locale.setlocale(locale.LC_ALL, '')

# ----------------------------
# Función para formatear con separador de millar
# ----------------------------
def formato_miles(valor):
    try:
        valor_float = float(valor.replace(",", ""))
        return f"{valor_float:,.2f}"
    except:
        return valor

# ----------------------------
# Función para calcular la cuota
# ----------------------------
def calcular_cuota(monto, tasa_anual, plazo_meses):
    tasa_mensual = tasa_anual / 12 / 100
    if tasa_mensual == 0:
        return monto / plazo_meses
    cuota = monto * (tasa_mensual * (1 + tasa_mensual)**plazo_meses) / ((1 + tasa_mensual)**plazo_meses - 1)
    return cuota

# ----------------------------
# Función para generar tabla de amortización
# ----------------------------
def generar_tabla_amortizacion(monto, tasa_anual, plazo_meses):
    tasa_mensual = tasa_anual / 12 / 100
    cuota = calcular_cuota(monto, tasa_anual, plazo_meses)

    saldo = monto
    data = []

    for i in range(1, plazo_meses + 1):
        interes = saldo * tasa_mensual
        capital = cuota - interes
        saldo -= capital
        data.append({
            "Cuota": i,
            "Pago": round(cuota, 2),
            "Interés": round(interes, 2),
            "Capital": round(capital, 2),
            "Saldo": round(max(saldo, 0), 2)
        })

    return pd.DataFrame(data)

# ----------------------------
# Función para convertir DataFrame a Excel
# ----------------------------
def convertir_a_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Amortización')
    return output.getvalue()

# ----------------------------
# Función para generar link de descarga
# ----------------------------
def generar_link_descarga_excel(df):
    excel_data = convertir_a_excel(df)
    b64 = base64.b64encode(excel_data).decode()
    return f'<a href="data:application/octet-stream;base64,{b64}" download="amortizacion.xlsx">📥 Descargar Excel</a>'

# ----------------------------
# Interfaz Streamlit
# ----------------------------
st.title("Calculadora de Préstamos")

monto_input = st.text_input("Monto del préstamo", value="0", key="monto_prestamo")
monto_input = formato_miles(monto_input)
st.session_state.monto_prestamo = monto_input

tasa = st.number_input("Tasa de interés anual (%)", value=6.0, step=0.1)
plazo = st.number_input("Plazo (meses)", value=12, step=1)

# Checkbox para decidir si mostrar tabla
mostrar_tabla = st.checkbox("Mostrar tabla de amortización", value=True)

# Botón para calcular
if st.button("Calcular"):
    try:
        monto = float(monto_input.replace(",", ""))
        cuota = calcular_cuota(monto, tasa, plazo)
        st.success(f"Cuota mensual: {cuota:,.2f}")

        if mostrar_tabla:
            df_resultado = generar_tabla_amortizacion(monto, tasa, plazo)
            st.dataframe(df_resultado)
            st.markdown(generar_link_descarga_excel(df_resultado), unsafe_allow_html=True)

    except ValueError:
        st.error("Por favor, ingresa valores numéricos válidos.")
