import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
import base64
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet

st.set_page_config(page_title="Calculadora de Cuotas", layout="centered")

# --- Funciones auxiliares ---
def calcular_cuotas(monto, tasa_anual, plazo_meses, frecuencia_pago, tipo_cuota):
    tasa_periodica = (tasa_anual / 100) / frecuencia_pago
    numero_cuotas = plazo_meses * frecuencia_pago / 12

    if tipo_cuota == "Cuota Nivelada":
        cuota = monto * (tasa_periodica * (1 + tasa_periodica) ** numero_cuotas) / ((1 + tasa_periodica) ** numero_cuotas - 1)
        saldo = monto
        tabla = []
        for i in range(1, int(numero_cuotas) + 1):
            interes = saldo * tasa_periodica
            abono_capital = cuota - interes
            saldo -= abono_capital
            tabla.append([i, cuota, interes, abono_capital, saldo if saldo > 0 else 0])
    else:
        saldo = monto
        tabla = []
        abono_capital = monto / numero_cuotas
        for i in range(1, int(numero_cuotas) + 1):
            interes = saldo * tasa_periodica
            cuota = interes + abono_capital
            saldo -= abono_capital
            tabla.append([i, cuota, interes, abono_capital, saldo if saldo > 0 else 0])

    df = pd.DataFrame(tabla, columns=["N° Cuota", "Cuota", "Interés", "Abono a Capital", "Saldo"])
    return df

def convertir_a_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Amortización')
    writer.close()
    output.seek(0)
    return output

def generar_link_descarga_excel(df):
    excel_data = convertir_a_excel(df)
    b64 = base64.b64encode(excel_data.read()).decode()
    href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="tabla_amortizacion.xlsx">📊 Descargar Excel</a>'
    return href

def convertir_a_pdf(df):
    output = BytesIO()
    doc = SimpleDocTemplate(output, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("Tabla de Amortización", styles['Heading1']))
    elements.append(Spacer(1, 12))

    data = [list(df.columns)] + df.values.tolist()

    for i in range(1, len(data)):
        data[i] = [
            f"{x:,.2f}" if isinstance(x, (int, float)) else str(x)
            for x in data[i]
        ]

    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#003366")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
    ]))

    elements.append(table)
    doc.build(elements)
    output.seek(0)
    return output

def generar_link_descarga_pdf(df):
    pdf_data = convertir_a_pdf(df)
    b64 = base64.b64encode(pdf_data.read()).decode()
    href = f'<a href="data:application/pdf;base64,{b64}" download="tabla_amortizacion.pdf">📄 Descargar PDF</a>'
    return href

# --- UI Streamlit ---
st.title("📈 Calculadora de Cuotas de Préstamo")

monto_prestamo = st.number_input("💰 Monto del préstamo", min_value=0.0, step=100.0, format="%.2f")
tasa_interes = st.number_input("📉 Tasa de interés anual (%)", min_value=0.0, step=0.1, format="%.2f")
plazo_meses = st.number_input("⏳ Plazo del préstamo (en meses)", min_value=1, step=1)
frecuencia = st.selectbox("📆 Frecuencia de pago", ["Mensual", "Bimestral", "Trimestral", "Semestral"])
tipo_cuota = st.selectbox("⚙️ Tipo de cuota", ["Cuota Nivelada", "Cuota con Saldos Insolutos"])

frecuencias_dict = {
    "Mensual": 12,
    "Bimestral": 6,
    "Trimestral": 4,
    "Semestral": 2
}

frecuencia_pago = frecuencias_dict[frecuencia]

if st.button("📊 Calcular Cuotas"):
    if monto_prestamo > 0 and tasa_interes >= 0 and plazo_meses > 0:
        df_resultado = calcular_cuotas(monto_prestamo, tasa_interes, plazo_meses, frecuencia_pago, tipo_cuota)
        st.success("✅ Cálculo completado.")
        st.dataframe(df_resultado.style.format({
            "Cuota": "{:,.2f}",
            "Interés": "{:,.2f}",
            "Abono a Capital": "{:,.2f}",
            "Saldo": "{:,.2f}"
        }), use_container_width=True)

        st.markdown(generar_link_descarga_excel(df_resultado), unsafe_allow_html=True)
        st.markdown(generar_link_descarga_pdf(df_resultado), unsafe_allow_html=True)
    else:
        st.error("❌ Por favor, completa todos los campos con valores válidos.")
     
