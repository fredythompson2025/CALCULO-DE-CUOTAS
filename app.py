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
st.set_page_config(page_title="Cuotas de Préstamo", layout="wide")

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 20px rgba(0,0,0,0.1);
    }
    .main-title {
        color: white;
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    .subtitle {
        color: #e0e6ff;
        font-size: 1.1rem;
        margin: 0;
    }
    .form-container {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.08);
        margin-bottom: 1.5rem;
        border: 1px solid #e1e8ed;
    }
    .result-box {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        margin: 1rem 0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    .result-amount {
        font-size: 2rem;
        font-weight: bold;
        margin: 0.5rem 0;
        text-shadow: 1px 1px 3px rgba(0,0,0,0.3);
    }
    .loan-info {
        background: #f8f9ff;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        margin: 1rem 0;
    }
    .download-section {
        background: #f8f9fa;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin-top: 2rem;
        border: 2px dashed #dee2e6;
    }
    .download-button {
        display: inline-block;
        padding: 12px 24px;
        margin: 0 10px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        text-decoration: none;
        border-radius: 25px;
        font-weight: bold;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        transition: transform 0.2s;
    }
    .download-button:hover {
        transform: translateY(-2px);
        text-decoration: none;
        color: white;
    }
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.75rem 2rem;
        font-weight: bold;
        font-size: 1.1rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(0,0,0,0.2);
    }
    .input-section {
        background: #f8f9ff;
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 1rem;
        border: 1px solid #e1e8ff;
    }
    </style>
""", unsafe_allow_html=True)

# Enhanced header with icon and title
st.markdown("""
    <div class='main-header'>
        <img src='https://cdn-icons-png.flaticon.com/512/2910/2910768.png' width='100' style='margin-bottom: 1rem;'/>
        <h1 class='main-title'>💰 Calculadora de Préstamos</h1>
        <p class='subtitle'>Calcula tu tabla de amortización con diferentes frecuencias de pago</p>
    </div>
""", unsafe_allow_html=True)

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

# Create enhanced form for loan parameters input
st.markdown('<div class="form-container">', unsafe_allow_html=True)

with st.form("formulario"):
    st.markdown("### 📝 Datos del Préstamo")
    
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="input-section">', unsafe_allow_html=True)
        st.markdown("**💰 Información del Monto**")
        # Loan amount input with formatting
        default_monto = st.session_state.get("monto_str", "10,000.00")
        monto_str = st.text_input("Monto del préstamo (Lempiras)", value=default_monto)

        # Validate and parse loan amount
        try:
            monto = float(monto_str.replace(",", "").replace("Lempiras", "").replace("L.", "").replace("Lps.", "").strip())
            st.session_state["monto_str"] = f"{monto:,.2f}"
        except ValueError:
            st.error("❌ Ingrese un monto válido.")
            st.stop()

        # Interest rate and term inputs
        tasa = st.number_input("📈 Tasa de interés anual (%)", value=12.0, step=0.1, format="%.2f")
        plazo = st.number_input("📅 Plazo (meses)", value=36, step=1, min_value=1)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="input-section">', unsafe_allow_html=True)
        st.markdown("**⚙️ Configuración de Pagos**")
        # Payment frequency selection
        frecuencia = st.selectbox(
            "📆 Frecuencia de pago",
            ['Mensual', 'Quincenal', 'Semanal', 'Diario', 'Bimensual',
             'Trimestral', 'Cuatrimestral', 'Semestral', 'Anual', 'Al vencimiento']
        )
        
        # Payment type selection
        tipo_cuota = st.selectbox("🔁 Tipo de cuota", ['Nivelada', 'Saldos Insolutos'])
        
        # Insurance options
        incluir_seguro = st.selectbox("🛡️ ¿Incluir seguro Prestamo?", ['No', 'Sí'])
        if incluir_seguro == 'Sí':
            porcentaje_seguro = st.number_input("📌 % Seguro por cada L. 1,000", value=0.50, step=0.01, format="%.2f")
        else:
            porcentaje_seguro = 0.0
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")
    
    col_check, col_button = st.columns([3, 1])
    with col_check:
        # Option to show/hide amortization table
        mostrar_tabla = st.checkbox("📋 Mostrar tabla de amortización completa", value=True)
    
    with col_button:
        calcular = st.form_submit_button("🔍 Calcular Cuotas", use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)

# Process calculation when form is submitted
if calcular:
    # Calculate amortization schedule
    df_resultado = calcular_cuotas_df(monto, tasa, plazo, frecuencia, tipo_cuota, incluir_seguro, porcentaje_seguro)
    
    # Enhanced results section
    st.markdown("## 🎯 Resultados del Cálculo")
    
    # Loan information in styled box
    st.markdown(f"""
        <div class='loan-info'>
            <h4>📋 Información del Préstamo</h4>
            <div style='display: flex; justify-content: space-between; flex-wrap: wrap;'>
                <div><strong>💰 Monto:</strong> L. {monto:,.2f}</div>
                <div><strong>📈 Tasa Anual:</strong> {tasa:.2f}%</div>
                <div><strong>📅 Plazo:</strong> {plazo} meses</div>
            </div>
            <div style='display: flex; justify-content: space-between; flex-wrap: wrap; margin-top: 1rem;'>
                <div><strong>📆 Frecuencia:</strong> {frecuencia}</div>
                <div><strong>🔁 Tipo:</strong> {tipo_cuota}</div>
                <div><strong>🛡️ Seguro:</strong> {incluir_seguro}</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Display payment information in attractive box
    if len(df_resultado) == 1:
        # Single payment (at maturity)
        cuota_final = df_resultado["Cuota"].iloc[0]
        st.markdown(f"""
            <div class='result-box'>
                <h3>💵 Cuota a Pagar</h3>
                <div class='result-amount'>L. {cuota_final:,.2f}</div>
                <p>Pago único al vencimiento</p>
            </div>
        """, unsafe_allow_html=True)
    else:
        # Multiple payments - show first payment amount
        primera_cuota = df_resultado["Cuota"].iloc[0]
        total_cuotas = len(df_resultado)
        total_pago = df_resultado["Cuota"].sum()
        total_intereses = df_resultado["Interés"].sum()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
                <div class='result-box'>
                    <h4>💵 Cuota a Pagar</h4>
                    <div class='result-amount'>L. {primera_cuota:,.2f}</div>
                    <p>{tipo_cuota.lower()}</p>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
                <div class='result-box' style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);'>
                    <h4>📊 Total a Pagar</h4>
                    <div class='result-amount'>L. {total_pago:,.2f}</div>
                    <p>En {total_cuotas} cuotas</p>
                </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
                <div class='result-box' style='background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);'>
                    <h4>📈 Total Intereses</h4>
                    <div class='result-amount'>L. {total_intereses:,.2f}</div>
                    <p>Durante el préstamo</p>
                </div>
            """, unsafe_allow_html=True)

    # Format DataFrame for display
    df_format = df_resultado.copy()
    for col in ["Cuota", "Interés", "Abono", "Seguro", "Saldo"]:
        if col in df_format.columns:
            df_format[col] = df_format[col].apply(lambda x: f"L. {x:,.2f}")

    st.markdown("---")
    st.markdown("## 🧾 Tabla de Amortización")
    
    if mostrar_tabla:
        # Show table with or without insurance column
        if incluir_seguro == 'No' and "Seguro" in df_format.columns:
            st.dataframe(df_format.drop(columns=["Seguro"]), use_container_width=True, height=400)
            df_exportar = df_resultado.drop(columns=["Seguro"])
        else:
            st.dataframe(df_format, use_container_width=True, height=400)
            df_exportar = df_resultado

        # Enhanced download section
        st.markdown("""
            <div class='download-section'>
                <h3>📂 Descargar Tabla de Amortización</h3>
                <p style='margin-bottom: 1.5rem; color: #666;'>Obtén tu tabla de amortización en formato Excel o PDF</p>
            </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            excel_link = generar_link_descarga_excel(df_exportar)
            # Style the download link with custom class
            excel_link = excel_link.replace('<a href=', '<a class="download-button" href=')
            st.markdown(f'<div style="text-align: center;">{excel_link}</div>', unsafe_allow_html=True)
        
        with col2:
            pdf_link = generar_link_descarga_pdf(df_exportar)
            # Style the download link with custom class
            pdf_link = pdf_link.replace('<a href=', '<a class="download-button" href=')
            st.markdown(f'<div style="text-align: center;">{pdf_link}</div>', unsafe_allow_html=True)
            
        # Footer
        st.markdown("""
            <div style='text-align: center; margin-top: 2rem; padding: 1rem; color: #666; border-top: 1px solid #eee;'>
                <p><strong>Creado por Fredy Thompson</strong> | Calculadora de Préstamos Profesional</p>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.info("📋 Marque la casilla arriba para mostrar la tabla de amortización completa.")
