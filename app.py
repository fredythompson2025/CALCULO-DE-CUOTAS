import streamlit as st
import pandas as pd
from io import BytesIO
import base64
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
import os

# Configure the Streamlit page
st.set_page_config(page_title="Cuotas de Préstamo", layout="centered")

# Header with icon and title
st.markdown("""
    <div style='text-align: center;'>
        <img src='https://cdn-icons-png.flaticon.com/512/2910/2910768.png' width='80'/>
        <h1 style='color: #003366;'>Cuotas de Préstamo</h1>
    </div>
""", unsafe_allow_html=True)
st.markdown("##")

def calcular_cuotas_df(monto, tasa_anual, plazo_meses, frecuencia, tipo_cuota, incluir_seguro, porcentaje_seguro):
    """
    Calculate loan amortization schedule with different payment frequencies and types.
    
    Args:
        monto: Loan amount
        tasa_anual: Annual interest rate (percentage)
        plazo_meses: Loan term in months
        frecuencia: Payment frequency
        tipo_cuota: Payment type (Nivelada or Saldos Insolutos)
        incluir_seguro: Whether to include insurance
        porcentaje_seguro: Insurance percentage per 1000
    
    Returns:
        DataFrame with amortization schedule
    """
    # Dictionary mapping payment frequencies to payments per year
    freq_dict = {
        'Diario': 360, 'Semanal': 52, 'Quincenal': 24, 'Mensual': 12,
        'Bimensual': 6, 'Trimestral': 4, 'Cuatrimestral': 3,
        'Semestral': 2, 'Anual': 1, 'Al vencimiento': 0
    }

    pagos_por_año = freq_dict[frecuencia]
    
    # Handle "At maturity" payment
    if pagos_por_año == 0:
        tasa_total = tasa_anual / 100 * (plazo_meses / 12)
        interes = monto * tasa_total
        abono = monto
        seguro = 0
        cuota_total = interes + abono
        return pd.DataFrame([{
            "Pago": 1, "Cuota": cuota_total, "Interés": interes,
            "Abono": abono, "Seguro": seguro, "Saldo": 0
        }])

    # Calculate number of payments and interest rate per period
    n_pagos = int(plazo_meses * pagos_por_año / 12)
    tasa_periodo = tasa_anual / 100 / pagos_por_año
    saldo = monto

    # Calculate reference values for insurance calculation
    ref_cuota_dict = {
        'Diario': 360, 'Semanal': 52, 'Quincenal': 24, 'Mensual': 12,
        'Bimensual': 6, 'Trimestral': 4, 'Cuatrimestral': 3,
        'Semestral': 2, 'Anual': 1
    }
    ref_cuota = min(ref_cuota_dict.get(frecuencia, 1), n_pagos)
    saldo_referencia = monto

    # Calculate base payment amount and reference balance for insurance
    if tipo_cuota == 'Nivelada':
        # Level payment calculation using PMT formula
        cuota_base = monto * (tasa_periodo * (1 + tasa_periodo) ** n_pagos) / ((1 + tasa_periodo) ** n_pagos - 1)
        # Simulate payments to get reference balance
        for _ in range(ref_cuota):
            interes = saldo_referencia * tasa_periodo
            abono = cuota_base - interes
            saldo_referencia -= abono
    else:
        # Declining balance payment - fixed principal payment
        abono_fijo = monto / n_pagos
        for _ in range(ref_cuota):
            interes = saldo_referencia * tasa_periodo
            saldo_referencia -= abono_fijo

    # Calculate insurance amount per payment
    seguro_unitario = 0
    if incluir_seguro == 'Sí':
        divisor = freq_dict[frecuencia]
        seguro_unitario = (saldo_referencia / 1000) * porcentaje_seguro * 12 / divisor

    # Calculate number of payments that include insurance
    cuotas_con_seguro = n_pagos - pagos_por_año
    saldo = monto
    datos = []

    # Generate amortization schedule
    if tipo_cuota == 'Nivelada':
        # Level payments - same payment amount each period
        for i in range(1, n_pagos + 1):
            interes = saldo * tasa_periodo
            abono = cuota_base - interes
            saldo -= abono
            saldo = max(saldo, 0)  # Prevent negative balance
            
            # Apply insurance for specified number of payments
            seguro_aplicado = seguro_unitario if incluir_seguro == 'Sí' and i <= cuotas_con_seguro else 0
            cuota_total = cuota_base + seguro_aplicado
            
            datos.append({
                "Pago": i, "Cuota": cuota_total, "Interés": interes,
                "Abono": abono, "Seguro": seguro_aplicado, "Saldo": saldo
            })
    else:
        # Declining balance - fixed principal, varying interest
        abono_fijo = monto / n_pagos
        for i in range(1, n_pagos + 1):
            interes = saldo * tasa_periodo
            cuota_base = abono_fijo + interes
            saldo -= abono_fijo
            saldo = max(saldo, 0)  # Prevent negative balance
            
            # Apply insurance for specified number of payments
            seguro_aplicado = seguro_unitario if incluir_seguro == 'Sí' and i <= cuotas_con_seguro else 0
            cuota_total = cuota_base + seguro_aplicado
            
            datos.append({
                "Pago": i, "Cuota": cuota_total, "Interés": interes,
                "Abono": abono_fijo, "Seguro": seguro_aplicado, "Saldo": saldo
            })

    df = pd.DataFrame(datos)
    return df

def convertir_a_excel(df):
    """
    Convert DataFrame to Excel format in memory.
    
    Args:
        df: DataFrame to convert
        
    Returns:
        BytesIO object containing Excel data
    """
    output = BytesIO()

    # Try to use xlsxwriter, fallback to openpyxl
    try:
        import xlsxwriter
        engine = 'xlsxwriter'
    except ImportError:
        engine = 'openpyxl'

    with pd.ExcelWriter(output, engine=engine) as writer:
        df.to_excel(writer, index=False, sheet_name='Amortización')

    output.seek(0)
    return output

def generar_link_descarga_excel(df):
    """
    Generate download link for Excel file.
    
    Args:
        df: DataFrame to export
        
    Returns:
        HTML string with download link
    """
    excel_data = convertir_a_excel(df)
    b64 = base64.b64encode(excel_data.read()).decode()
    return f'<a href="data:application/octet-stream;base64,{b64}" download="tabla_amortizacion.xlsx">📅 Descargar Excel</a>'

def convertir_a_pdf(df):
    """
    Convert DataFrame to PDF format in memory.
    
    Args:
        df: DataFrame to convert
        
    Returns:
        BytesIO object containing PDF data
    """
    output = BytesIO()
    doc = SimpleDocTemplate(output, pagesize=letter)
    styles = getSampleStyleSheet()
    
    # Create document elements
    elements = [
        Paragraph("Tabla de Amortización", styles['Heading1']), 
        Spacer(1, 12)
    ]
    
    # Prepare table data with headers
    data = [list(df.columns)] + df.values.tolist()

    # Format numeric values in the data
    for i in range(1, len(data)):
        data[i] = [f"{x:,.2f}" if isinstance(x, (int, float)) else str(x) for x in data[i]]

    # Create and style the table
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#003366")),  # Header background
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),  # Header text color
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),  # Grid lines
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Header font
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Center alignment
        ('FONTSIZE', (0, 0), (-1, -1), 8),  # Font size
    ]))
    
    elements.append(table)
    doc.build(elements)
    output.seek(0)
    return output

def generar_link_descarga_pdf(df):
    """
    Generate download link for PDF file.
    
    Args:
        df: DataFrame to export
        
    Returns:
        HTML string with download link
    """
    pdf_data = convertir_a_pdf(df)
    b64 = base64.b64encode(pdf_data.read()).decode()
    return f'<a href="data:application/pdf;base64,{b64}" download="tabla_amortizacion.pdf">📄 Descargar PDF</a>'

# -------------------- USER INTERFACE --------------------

# Create form for loan parameters input
with st.form("formulario"):
    col1, col2 = st.columns(2)

    with col1:
        # Loan amount input with formatting
        default_monto = st.session_state.get("monto_str", "10,000.00")
        monto_str = st.text_input("💰 Monto del préstamo", value=default_monto)

        # Validate and parse loan amount
        try:
            monto = float(monto_str.replace(",", "").replace("Lps.", "").strip())
            st.session_state["monto_str"] = f"{monto:,.2f}"
        except ValueError:
            st.error("❌ Ingrese un monto válido.")
            st.stop()

        # Interest rate and term inputs
        tasa = st.number_input("📈 Tasa de interés anual (%)", value=12.0, step=0.1)
        plazo = st.number_input("📅 Plazo (meses)", value=36, step=1)

    with col2:
        # Payment frequency selection
        frecuencia = st.selectbox(
            "📆 Frecuencia de pago",
            ['Diario', 'Semanal', 'Quincenal', 'Mensual', 'Bimensual',
             'Trimestral', 'Cuatrimestral', 'Semestral', 'Anual', 'Al vencimiento']
        )
        
        # Payment type selection
        tipo_cuota = st.selectbox("🔁 Tipo de cuota", ['Nivelada', 'Saldos Insolutos'])
        
        # Insurance options
        incluir_seguro = st.selectbox("🛡️ ¿Incluir seguro Prestamo?", ['No', 'Sí'])
        porcentaje_seguro = st.number_input("📌 % Seguro por cada Lps. 1,000", value=0.50, step=0.01)

    # Option to show/hide amortization table
    mostrar_tabla = st.checkbox("📋 Mostrar tabla de amortización", value=True)

    st.markdown("---")
    calcular = st.form_submit_button("🔍 Calcular cuotas")

# Process calculation when form is submitted
if calcular:
    st.subheader("📊 Resultados:")
    st.markdown(f"**Monto del préstamo:** Lps. {monto:,.2f}  \n**Tasa anual:** {tasa:.2f}%  \n**Plazo:** {plazo} meses")

    # Calculate amortization schedule
    df_resultado = calcular_cuotas_df(monto, tasa, plazo, frecuencia, tipo_cuota, incluir_seguro, porcentaje_seguro)

    # Display payment information
    if len(df_resultado) == 1:
        # Single payment (at maturity)
        cuota_final = df_resultado["Cuota"].iloc[0]
        st.info(f"💵 **Cuota a pagar:** Lps. {cuota_final:,.2f}")
    else:
        # Multiple payments - show average
        cuota_promedio = df_resultado["Cuota"].mean()
        st.info(f"💵 **Cuota promedio:** Lps. {cuota_promedio:,.2f}")

    # Format DataFrame for display
    df_format = df_resultado.copy()
    for col in ["Cuota", "Interés", "Abono", "Seguro", "Saldo"]:
        if col in df_format.columns:
            df_format[col] = df_format[col].apply(lambda x: f"Lps. {x:,.2f}")

    st.subheader("🧾 Tabla de amortización:")
    
    if mostrar_tabla:
        # Show table with or without insurance column
        if incluir_seguro == 'No' and "Seguro" in df_format.columns:
            st.dataframe(df_format.drop(columns=["Seguro"]), use_container_width=True)
            df_exportar = df_resultado.drop(columns=["Seguro"])
        else:
            st.dataframe(df_format, use_container_width=True)
            df_exportar = df_resultado

        # Download section
        st.markdown("---")
        st.markdown("### 📂 DESCARGA, creado por Fredy Thompson")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(generar_link_descarga_excel(df_exportar), unsafe_allow_html=True)
        with col2:
            st.markdown(generar_link_descarga_pdf(df_exportar), unsafe_allow_html=True)
    else:
        st.info("📋 Tabla de amortización oculta.")
