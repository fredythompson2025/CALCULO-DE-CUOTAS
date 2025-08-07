import streamlit as st
import pandas as pd
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from streamlit_js_eval import streamlit_js_eval

# Configuración inicial
st.set_page_config(page_title="Calculadora de Cuotas Avanzada", layout="centered")

st.title("💸 Calculadora de Cuotas de Préstamo")

# Campo con separador de millares usando JavaScript
st.markdown("💰 **Monto del préstamo**")
monto_formateado = streamlit_js_eval(
    js_expressions="formattedValue = new Intl.NumberFormat('en-US', {minimumFractionDigits:2, maximumFractionDigits:2}).format(parseFloat(value.replace(/,/g, '')) || 0);",
    key="monto_prestamo",
    args={"value": "10000.00"},
    debounce=300,
    return_values=["formattedValue"],
    want_output=True
)

try:
    monto = float(monto_formateado.replace(",", ""))
except:
    st.error("❌ Ingrese un monto válido.")
    st.stop()

# Entradas adicionales
tasa_interes = st.number_input("📈 Tasa de interés anual (%)", min_value=0.0, step=0.01, format="%.2f")
plazo = st.number_input("📅 Plazo (meses)", min_value=1, step=1)
frecuencia = st.selectbox("⏱ Frecuencia de pago", ["Mensual", "Bimestral", "Trimestral", "Semestral", "Anual", "Al vencimiento"])
tipo_cuota = st.selectbox("🔄 Tipo de cuota", ["Nivelada", "Saldos Insolutos"])
incluir_seguro = st.selectbox("🛡️ Incluir seguro sobre saldo en cuota 12", ["No", "Sí"])

# Función para calcular cuotas
def calcular_cuotas(monto, tasa, plazo, frecuencia, tipo, incluir_seguro):
    frecuencia_map = {
        "Mensual": 1,
        "Bimestral": 2,
        "Trimestral": 3,
        "Semestral": 6,
        "Anual": 12,
        "Al vencimiento": plazo
    }

    periodo = frecuencia_map[frecuencia]
    tasa_periodica = tasa / 100 / (12 / periodo)
    n = plazo // periodo

    datos = []
    saldo = monto

    for i in range(1, n + 1):
        if tipo == "Nivelada":
            if tasa_periodica > 0:
                cuota = monto * (tasa_periodica * (1 + tasa_periodica) ** n) / ((1 + tasa_periodica) ** n - 1)
            else:
                cuota = monto / n
            interes = saldo * tasa_periodica
            abono = cuota - interes
        else:  # Saldos Insolutos
            interes = saldo * tasa_periodica
            abono = monto / n
            cuota = interes + abono

        saldo -= abono

        seguro = 0
        if incluir_seguro == "Sí" and i == 12 // periodo:
            seguro = saldo * 0.02

        datos.append({
            "Periodo": i,
            "Cuota": round(cuota + seguro, 2),
            "Interés": round(interes, 2),
            "Abono": round(abono, 2),
            "Saldo": round(max(saldo, 0), 2),
            "Seguro": round(seguro, 2)
        })

    return pd.DataFrame(datos)

# Botón de cálculo
if st.button("📊 Calcular cuotas"):
    df_resultado = calcular_cuotas(monto, tasa_interes, plazo, frecuencia, tipo_cuota, incluir_seguro)

    # Formato del DataFrame para visualización
    df_format = df_resultado.copy()
    for col in ["Cuota", "Interés", "Abono", "Saldo", "Seguro"]:
        df_format[col] = df_format[col].map(lambda x: f"Lps. {x:,.2f}")

    st.subheader("🧾 Tabla de amortización:")

    # Ocultar columna de seguro si no se aplica
    if incluir_seguro == 'No':
        df_format = df_format.drop(columns=["Seguro"])

    st.dataframe(df_format, use_container_width=True)

    # Mostrar cuota promedio
    cuota_promedio = df_resultado["Cuota"].mean()
    st.info(f"💵 **Cuota promedio a pagar:** Lps. {cuota_promedio:,.2f}")

    # Exportación a Excel
    def convertir_a_excel(df):
        output = BytesIO()
        df.to_excel(output, index=False, sheet_name='Amortización', engine='openpyxl')
        output.seek(0)
        return output

    def generar_link_descarga_excel(df):
        excel_data = convertir_a_excel(df)
        st.download_button(
            label="📥 Descargar Excel",
            data=excel_data,
            file_name="tabla_amortizacion.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    generar_link_descarga_excel(df_resultado)

    # Exportación a PDF
    def convertir_a_pdf(df):
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter
        y = height - 40
        p.setFont("Helvetica", 10)

        columnas = list(df.columns)
        col_width = width / len(columnas)

        for i, col in enumerate(columnas):
            p.drawString(i * col_width + 10, y, col)

        y -= 20
        for index, row in df.iterrows():
            for i, item in enumerate(row):
                p.drawString(i * col_width + 10, y, str(round(item, 2)))
            y -= 20
            if y < 50:
                p.showPage()
                y = height - 40
                p.setFont("Helvetica", 10)

        p.save()
        buffer.seek(0)
        return buffer

    st.download_button(
        label="📄 Descargar PDF",
        data=convertir_a_pdf(df_resultado),
        file_name="tabla_amortizacion.pdf",
        mime="application/pdf"
    )

