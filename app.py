import streamlit as st
import pandas as pd
from io import BytesIO
import base64
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet

# Configure the Streamlit page
st.set_page_config(page_title="Cuotas de Préstamo", layout="wide")

# Enhanced CSS for beautiful design
st.markdown("""
    <style>
    /* Global app styling */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 3rem 2rem;
        border-radius: 20px;
        text-align: center;
        margin-bottom: 2.5rem;
        box-shadow: 0 15px 35px rgba(102, 126, 234, 0.3);
        position: relative;
        overflow: hidden;
    }
    .main-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: url("data:image/svg+xml,%3Csvg width='40' height='40' viewBox='0 0 40 40' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='%23ffffff' fill-opacity='0.05'%3E%3Cpath d='M20 20c0 11.046-8.954 20-20 20v20h40V20H20z'/%3E%3C/g%3E%3C/svg%3E") repeat;
    }
    .main-title {
        color: white;
        font-size: 3rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 8px rgba(0,0,0,0.3);
        position: relative;
        z-index: 1;
    }
    .subtitle {
        color: #e0e6ff;
        font-size: 1.2rem;
        margin: 0;
        font-weight: 300;
        position: relative;
        z-index: 1;
    }
    
    /* Form container styling */
    .form-container {
        background: rgba(255, 255, 255, 0.95);
        padding: 2.5rem;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        margin-bottom: 2rem;
        border: 1px solid rgba(255, 255, 255, 0.8);
        backdrop-filter: blur(10px);
    }
    
    /* Input sections */
    .input-section {
        background: linear-gradient(135deg, #f8f9ff 0%, #e6f2ff 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 1.5rem;
        border: 1px solid #e1e8ff;
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.08);
        transition: all 0.3s ease;
    }
    .input-section:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.15);
    }
    
    /* Result boxes with enhanced animations */
    .result-box {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 20px;
        text-align: center;
        margin: 0.5rem 0;
        box-shadow: 0 10px 30px rgba(17, 153, 142, 0.3);
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        border: 1px solid rgba(255, 255, 255, 0.2);
        position: relative;
        overflow: hidden;
    }
    .result-box:hover {
        transform: translateY(-5px) scale(1.02);
        box-shadow: 0 15px 40px rgba(17, 153, 142, 0.4);
    }
    .result-box::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
        transition: left 0.6s;
    }
    .result-box:hover::before {
        left: 100%;
    }
    .result-amount {
        font-size: 2rem;
        font-weight: 800;
        margin: 0.5rem 0;
        text-shadow: 2px 2px 8px rgba(0,0,0,0.3);
        position: relative;
        z-index: 1;
    }
    .result-box h4 {
        margin: 0 0 0.8rem 0;
        font-size: 1rem;
        opacity: 0.95;
        font-weight: 600;
        position: relative;
        z-index: 1;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .result-box p {
        margin: 0.5rem 0 0 0;
        font-size: 0.9rem;
        opacity: 0.9;
        position: relative;
        z-index: 1;
    }
    
    /* Loan information card */
    .loan-info {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9ff 100%);
        padding: 2rem;
        border-radius: 20px;
        border: 1px solid #e1e8ff;
        margin: 1.5rem 0;
        box-shadow: 0 8px 25px rgba(0,0,0,0.08);
        position: relative;
        overflow: hidden;
    }
    .loan-info::before {
        content: '';
        position: absolute;
        left: 0;
        top: 0;
        bottom: 0;
        width: 5px;
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
        border-radius: 0 5px 5px 0;
    }
    .loan-info h4 {
        color: #2c3e50;
        margin: 0 0 1.5rem 0;
        font-weight: 700;
        font-size: 1.3rem;
        display: flex;
        align-items: center;
        gap: 0.8rem;
    }
    
    /* Info grid enhanced */
    .info-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 1.2rem;
        margin-top: 1.5rem;
    }
    .info-item {
        background: rgba(255, 255, 255, 0.9);
        padding: 1.2rem;
        border-radius: 12px;
        border: 1px solid rgba(102, 126, 234, 0.1);
        transition: all 0.3s ease;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    .info-item:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.15);
        border-color: rgba(102, 126, 234, 0.3);
    }
    .info-item strong {
        color: #2c3e50;
        display: block;
        margin-bottom: 0.5rem;
        font-size: 0.9rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .info-item span {
        color: #667eea;
        font-size: 1.1rem;
        font-weight: 700;
    }
    
    /* Enhanced buttons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 30px;
        padding: 1rem 2.5rem;
        font-weight: 700;
        font-size: 1.1rem;
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.3);
        transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 25px rgba(102, 126, 234, 0.4);
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    }
    
    /* Download section */
    .download-section {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        padding: 3rem 2rem;
        border-radius: 20px;
        text-align: center;
        margin-top: 3rem;
        border: 2px dashed #dee2e6;
        box-shadow: 0 8px 25px rgba(0,0,0,0.08);
    }
    .download-section h3 {
        color: #2c3e50;
        margin-bottom: 1rem;
        font-weight: 700;
    }
    .download-button {
        display: inline-block;
        padding: 15px 30px;
        margin: 0.5rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        text-decoration: none;
        border-radius: 30px;
        font-weight: 700;
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.3);
        transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        text-transform: uppercase;
        letter-spacing: 1px;
        font-size: 0.9rem;
    }
    .download-button:hover {
        transform: translateY(-3px);
        text-decoration: none;
        color: white;
        box-shadow: 0 10px 25px rgba(102, 126, 234, 0.4);
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    }
    
    /* Results container */
    .results-container {
        margin: 2.5rem 0;
    }
    .results-title {
        color: #2c3e50;
        font-size: 2.2rem;
        font-weight: 700;
        margin-bottom: 2rem;
        text-align: center;
        position: relative;
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    .results-title::after {
        content: '';
        position: absolute;
        bottom: -10px;
        left: 50%;
        transform: translateX(-50%);
        width: 80px;
        height: 4px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 2px;
    }
    
    /* Enhanced grid */
    .compact-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 1.5rem;
        margin: 2rem 0;
    }
    
    /* Custom scrollbar */
    .stDataFrame {
        border-radius: 15px;
        overflow: hidden;
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
    }
    
    /* Enhanced selectbox and inputs */
    .stSelectbox > div > div {
        border-radius: 10px;
        border: 2px solid #e1e8ff;
        transition: all 0.3s ease;
    }
    .stSelectbox > div > div:focus-within {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    .stNumberInput > div > div > input {
        border-radius: 10px;
        border: 2px solid #e1e8ff;
        transition: all 0.3s ease;
    }
    .stNumberInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    .stTextInput > div > div > input {
        border-radius: 10px;
        border: 2px solid #e1e8ff;
        transition: all 0.3s ease;
    }
    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Section headers */
    h3 {
        color: #2c3e50;
        font-weight: 700;
        margin-bottom: 1.5rem;
        font-size: 1.4rem;
    }
    
    /* Footer styling */
    .footer {
        background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
        color: white;
        text-align: center;
        padding: 2rem;
        border-radius: 15px;
        margin-top: 3rem;
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .main-title {
            font-size: 2.2rem;
        }
        .compact-grid {
            grid-template-columns: 1fr;
        }
        .info-grid {
            grid-template-columns: 1fr;
        }
    }
    </style>
""",
            unsafe_allow_html=True)

# Enhanced header with icon and title
st.markdown("""
    <div class='main-header'>
        <h1 class='main-title'>💰 Calculadora de Préstamos</h1>
        <p class='subtitle'>Calcula tu tabla de amortización con diferentes frecuencias de pago</p>
    </div>
""",
            unsafe_allow_html=True)


def calcular_seguro_danos(monto_asegurar, porcentaje_seguro_danos,
                          impuesto_danos, bomberos_danos, papeleria_danos):
    """
    Calculate damage insurance based on the correct formula.
    
    Args:
        monto_asegurar: Amount to insure
        porcentaje_seguro_danos: Insurance percentage
        impuesto_danos: Tax percentage
        bomberos_danos: Firefighters percentage
        papeleria_danos: Fixed paperwork expense
        
    Returns:
        Monthly payment amount
    """
    if monto_asegurar <= 0:
        return 0

    # Fórmula: cantidad_asegurar / 1000 * porcentaje
    seguro_base = (monto_asegurar / 1000) * porcentaje_seguro_danos
    impuesto = seguro_base * (impuesto_danos / 100)
    bomberos = seguro_base * (bomberos_danos / 100)

    total_anual = seguro_base + impuesto + bomberos + papeleria_danos
    pago_mensual = total_anual / 12

    return pago_mensual


def calcular_seguro_vehiculo(monto_vehiculo, porcentaje_seguro_vehiculo,
                             impuesto_vehiculo, gasto_vehiculo):
    """
    Calculate vehicle insurance based on amount, percentage, tax and expenses.
    
    Args:
        monto_vehiculo: Vehicle value
        porcentaje_seguro_vehiculo: Insurance percentage
        impuesto_vehiculo: Tax percentage (e.g., 15%)
        gasto_vehiculo: Fixed expense amount
        
    Returns:
        Monthly payment amount
    """
    if monto_vehiculo <= 0:
        return 0

    # Fórmula: valor_vehiculo * porcentaje / 100
    seguro_base = monto_vehiculo * (porcentaje_seguro_vehiculo / 100)
    impuesto = seguro_base * (impuesto_vehiculo / 100)

    total_anual = seguro_base + impuesto + gasto_vehiculo
    pago_mensual = total_anual / 12

    return pago_mensual


def calcular_cuotas_df(monto, tasa_anual, plazo_meses, frecuencia, tipo_cuota,
                       incluir_seguro, porcentaje_seguro, incluir_seguro_danos,
                       monto_asegurar, porcentaje_seguro_danos, impuesto_danos,
                       bomberos_danos, papeleria_danos,
                       incluir_seguro_vehiculo, monto_vehiculo,
                       porcentaje_seguro_vehiculo, impuesto_vehiculo,
                       gasto_vehiculo):
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
        'Diario': 360,
        'Semanal': 52,
        'Quincenal': 24,
        'Mensual': 12,
        'Bimensual': 6,
        'Trimestral': 4,
        'Cuatrimestral': 3,
        'Semestral': 2,
        'Anual': 1,
        'Al vencimiento': 0
    }

    pagos_por_año = freq_dict[frecuencia]

    # Calculate damage insurance per payment
    pago_mensual_seguro_danos = calcular_seguro_danos(
        monto_asegurar if incluir_seguro_danos == 'Sí' else 0,
        porcentaje_seguro_danos if incluir_seguro_danos == 'Sí' else 0,
        impuesto_danos if incluir_seguro_danos == 'Sí' else 0,
        bomberos_danos if incluir_seguro_danos == 'Sí' else 0,
        papeleria_danos if incluir_seguro_danos == 'Sí' else 0)

    # Calculate vehicle insurance per payment
    pago_mensual_seguro_vehiculo = calcular_seguro_vehiculo(
        monto_vehiculo if incluir_seguro_vehiculo == 'Sí' else 0,
        porcentaje_seguro_vehiculo if incluir_seguro_vehiculo == 'Sí' else 0,
        impuesto_vehiculo if incluir_seguro_vehiculo == 'Sí' else 0,
        gasto_vehiculo if incluir_seguro_vehiculo == 'Sí' else 0)

    # Handle "At maturity" payment
    if pagos_por_año == 0:
        tasa_total = tasa_anual / 100 * (plazo_meses / 12)
        interes = monto * tasa_total
        abono = monto
        seguro = 0
        cuota_total = interes + abono
        seguro_danos = pago_mensual_seguro_danos * plazo_meses if incluir_seguro_danos == 'Sí' else 0
        seguro_vehiculo = pago_mensual_seguro_vehiculo * plazo_meses if incluir_seguro_vehiculo == 'Sí' else 0
        return pd.DataFrame([{
            "Pago": 1,
            "Cuota": cuota_total + seguro_danos + seguro_vehiculo,
            "Interés": interes,
            "Abono": abono,
            "Seguro de Préstamo": seguro,
            "Seguro Daños": seguro_danos,
            "Seguro Vehículo": seguro_vehiculo,
            "Saldo": 0
        }])

    # Calculate number of payments and interest rate per period
    n_pagos = int(plazo_meses * pagos_por_año / 12)
    tasa_periodo = tasa_anual / 100 / pagos_por_año
    saldo = monto

    # Calculate reference values for insurance calculation
    ref_cuota_dict = {
        'Diario': 360,
        'Semanal': 52,
        'Quincenal': 24,
        'Mensual': 12,
        'Bimensual': 6,
        'Trimestral': 4,
        'Cuatrimestral': 3,
        'Semestral': 2,
        'Anual': 1
    }
    ref_cuota = min(ref_cuota_dict.get(frecuencia, 1), n_pagos)
    saldo_referencia = monto

    # Calculate base payment amount and reference balance for insurance
    cuota_base = 0  # Initialize to avoid unbound variable
    if tipo_cuota == 'Nivelada':
        # Level payment calculation using PMT formula
        cuota_base = monto * (tasa_periodo * (1 + tasa_periodo)**n_pagos) / (
            (1 + tasa_periodo)**n_pagos - 1)
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
        seguro_unitario = (saldo_referencia /
                           1000) * porcentaje_seguro * 12 / divisor

    # Calculate damage and vehicle insurance per payment based on frequency
    seguro_danos_por_pago = 0
    seguro_vehiculo_por_pago = 0

    if incluir_seguro_danos == 'Sí':
        if frecuencia == 'Mensual':
            seguro_danos_por_pago = pago_mensual_seguro_danos
        elif frecuencia == 'Quincenal':
            seguro_danos_por_pago = pago_mensual_seguro_danos / 2
        elif frecuencia == 'Semanal':
            seguro_danos_por_pago = pago_mensual_seguro_danos / 4.33
        elif frecuencia == 'Diario':
            seguro_danos_por_pago = pago_mensual_seguro_danos / 30
        else:
            # For other frequencies, calculate proportionally
            pagos_mensuales = freq_dict[frecuencia] / 12 if freq_dict[
                frecuencia] > 0 else 0
            seguro_danos_por_pago = pago_mensual_seguro_danos / pagos_mensuales if pagos_mensuales > 0 else 0

    if incluir_seguro_vehiculo == 'Sí':
        if frecuencia == 'Mensual':
            seguro_vehiculo_por_pago = pago_mensual_seguro_vehiculo
        elif frecuencia == 'Quincenal':
            seguro_vehiculo_por_pago = pago_mensual_seguro_vehiculo / 2
        elif frecuencia == 'Semanal':
            seguro_vehiculo_por_pago = pago_mensual_seguro_vehiculo / 4.33
        elif frecuencia == 'Diario':
            seguro_vehiculo_por_pago = pago_mensual_seguro_vehiculo / 30
        else:
            # For other frequencies, calculate proportionally
            pagos_mensuales = freq_dict[frecuencia] / 12 if freq_dict[
                frecuencia] > 0 else 0
            seguro_vehiculo_por_pago = pago_mensual_seguro_vehiculo / pagos_mensuales if pagos_mensuales > 0 else 0

    # Calculate number of payments that include insurance (not last year)
    cuotas_con_seguro = max(0, n_pagos -
                            pagos_por_año) if pagos_por_año > 0 else n_pagos
    cuotas_con_seguro_danos = max(
        0, n_pagos - pagos_por_año) if pagos_por_año > 0 else n_pagos
    cuotas_con_seguro_vehiculo = max(
        0, n_pagos - pagos_por_año) if pagos_por_año > 0 else n_pagos

    # Generate amortization schedule
    datos = []
    saldo = monto

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
            seguro_danos_aplicado = seguro_danos_por_pago if incluir_seguro_danos == 'Sí' and i <= cuotas_con_seguro_danos else 0
            seguro_vehiculo_aplicado = seguro_vehiculo_por_pago if incluir_seguro_vehiculo == 'Sí' and i <= cuotas_con_seguro_vehiculo else 0
            cuota_total = cuota_base + seguro_aplicado + seguro_danos_aplicado + seguro_vehiculo_aplicado

            datos.append({
                "Pago": i,
                "Cuota": cuota_total,
                "Interés": interes,
                "Abono": abono,
                "Seguro de Préstamo": seguro_aplicado,
                "Seguro Daños": seguro_danos_aplicado,
                "Seguro Vehículo": seguro_vehiculo_aplicado,
                "Saldo": saldo
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
            seguro_danos_aplicado = seguro_danos_por_pago if incluir_seguro_danos == 'Sí' and i <= cuotas_con_seguro_danos else 0
            seguro_vehiculo_aplicado = seguro_vehiculo_por_pago if incluir_seguro_vehiculo == 'Sí' and i <= cuotas_con_seguro_vehiculo else 0
            cuota_total = cuota_base + seguro_aplicado + seguro_danos_aplicado + seguro_vehiculo_aplicado

            datos.append({
                "Pago": i,
                "Cuota": cuota_total,
                "Interés": interes,
                "Abono": abono_fijo,
                "Seguro de Préstamo": seguro_aplicado,
                "Seguro Daños": seguro_danos_aplicado,
                "Seguro Vehículo": seguro_vehiculo_aplicado,
                "Saldo": saldo
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
    from io import BytesIO
    output = BytesIO()

    # Use openpyxl engine with explicit type specification
    try:
        with pd.ExcelWriter(output, engine='openpyxl', mode='w') as writer:
            df.to_excel(writer, index=False, sheet_name='Amortización')
    except Exception as e:
        # Fallback: use a temporary file approach
        import tempfile
        import os
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp:
            df.to_excel(tmp.name,
                        index=False,
                        sheet_name='Amortización',
                        engine='openpyxl')
            tmp.seek(0)
            with open(tmp.name, 'rb') as f:
                output.write(f.read())
            os.unlink(tmp.name)

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
        data[i] = [
            f"{x:,.2f}" if isinstance(x, (int, float)) else str(x)
            for x in data[i]
        ]

    # Create and style the table
    table = Table(data)
    table.setStyle(
        TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0),
             colors.HexColor("#003366")),  # Header background
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
        monto_str = st.text_input("Monto del préstamo (Lempiras)",
                                  value=default_monto)

        # Validate and parse loan amount
        try:
            monto = float(
                monto_str.replace(",", "").replace("Lempiras", "").replace(
                    "L.", "").replace("Lps.", "").strip())
            st.session_state["monto_str"] = f"{monto:,.2f}"
        except ValueError:
            st.error("❌ Ingrese un monto válido.")
            st.stop()

        # Interest rate and term inputs
        tasa = st.number_input("📈 Tasa de interés anual (%)",
                               value=12.0,
                               step=0.1,
                               format="%.2f")
        plazo = st.number_input("📅 Plazo (meses)",
                                value=36,
                                step=1,
                                min_value=1)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="input-section">', unsafe_allow_html=True)
        st.markdown("**⚙️ Configuración de Pagos**")
        # Payment frequency selection
        frecuencia = st.selectbox("📆 Frecuencia de pago", [
            'Mensual', 'Quincenal', 'Semanal', 'Diario', 'Bimensual',
            'Trimestral', 'Cuatrimestral', 'Semestral', 'Anual',
            'Al vencimiento'
        ])

        # Payment type selection
        tipo_cuota = st.selectbox("🔁 Tipo de cuota",
                                  ['Nivelada', 'Saldos Insolutos'])

        # Insurance options section
        st.markdown("**🛡️ Opciones de Seguros**")

        # Seguro de préstamo
        incluir_seguro = st.selectbox("Seguro de Préstamo", ['No', 'Sí'])
        if incluir_seguro == 'Sí':
            porcentaje_seguro = st.number_input("📌 % Seguro por cada L. 1,000",
                                                value=0.50,
                                                step=0.01,
                                                format="%.2f")
        else:
            porcentaje_seguro = 0.0

        # Seguro de daños
        incluir_seguro_danos = st.selectbox("Seguro de Daños", ['No', 'Sí'])
        if incluir_seguro_danos == 'Sí':
            col_a, col_b = st.columns(2)
            with col_a:
                monto_asegurar = st.number_input("💼 Monto a asegurar",
                                                 value=350000.00,
                                                 step=1000.0,
                                                 format="%.0f")
                porcentaje_seguro_danos = st.number_input(
                    "📊 % por cada L. 1,000",
                    value=3.5,
                    step=0.1,
                    format="%.1f")
            with col_b:
                impuesto_danos = st.number_input("🏛️ % de impuesto",
                                                 value=15.0,
                                                 step=0.5,
                                                 format="%.1f")
                bomberos_danos = st.number_input("🚒 % bomberos",
                                                 value=5.0,
                                                 step=0.5,
                                                 format="%.1f")
            papeleria_danos = st.number_input("📄 Gasto papelería",
                                              value=50.0,
                                              step=5.0,
                                              format="%.0f")
        else:
            monto_asegurar = 0.0
            porcentaje_seguro_danos = 0.0
            impuesto_danos = 0.0
            bomberos_danos = 0.0
            papeleria_danos = 0.0

        # Seguro de vehículo
        incluir_seguro_vehiculo = st.selectbox("Seguro de Vehículo",
                                               ['No', 'Sí'])
        if incluir_seguro_vehiculo == 'Sí':
            col_c, col_d = st.columns(2)
            with col_c:
                monto_vehiculo = st.number_input("🚗 Valor del vehículo",
                                                 value=500000.00,
                                                 step=5000.0,
                                                 format="%.0f")
                impuesto_vehiculo = st.number_input("📋 % de impuesto",
                                                    value=15.0,
                                                    step=0.5,
                                                    format="%.1f")
            with col_d:
                porcentaje_seguro_vehiculo = st.number_input(
                    "🏎️ % anual del valor",
                    value=12.0,
                    step=0.5,
                    format="%.1f")
                gasto_vehiculo = st.number_input("💰 Gasto fijo",
                                                 value=250.0,
                                                 step=10.0,
                                                 format="%.0f")
        else:
            monto_vehiculo = 0.0
            porcentaje_seguro_vehiculo = 0.0
            impuesto_vehiculo = 0.0
            gasto_vehiculo = 0.0
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")

    col_check, col_button = st.columns([3, 1])
    with col_check:
        # Option to show/hide amortization table
        mostrar_tabla = st.checkbox("📋 Mostrar tabla de amortización completa",
                                    value=True)

    with col_button:
        calcular = st.form_submit_button("🔍 Calcular Cuotas",
                                         use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)

# Process calculation when form is submitted
if calcular:
    # Calculate amortization schedule
    df_resultado = calcular_cuotas_df(
        monto, tasa, plazo, frecuencia, tipo_cuota, incluir_seguro,
        porcentaje_seguro, incluir_seguro_danos, monto_asegurar,
        porcentaje_seguro_danos, impuesto_danos, bomberos_danos,
        papeleria_danos, incluir_seguro_vehiculo, monto_vehiculo,
        porcentaje_seguro_vehiculo, impuesto_vehiculo, gasto_vehiculo)

    # Enhanced results section
    st.markdown("""
        <div class='results-container'>
            <div class='results-title'>🎯 Resultados del Cálculo</div>
        </div>
    """,
                unsafe_allow_html=True)

    # Enhanced loan information display
    st.markdown(f"""
        <div class='loan-info'>
            <h4>📋 Información del Préstamo</h4>
            <div class='info-grid'>
                <div class='info-item'>
                    <strong>💰 Monto del Préstamo</strong>
                    <span>L. {monto:,.2f}</span>
                </div>
                <div class='info-item'>
                    <strong>📈 Tasa de Interés</strong>
                    <span>{tasa:.2f}% anual</span>
                </div>
                <div class='info-item'>
                    <strong>📅 Plazo</strong>
                    <span>{plazo} meses</span>
                </div>
                <div class='info-item'>
                    <strong>📆 Frecuencia de Pago</strong>
                    <span>{frecuencia}</span>
                </div>
                <div class='info-item'>
                    <strong>🔁 Tipo de Cuota</strong>
                    <span>{tipo_cuota}</span>
                </div>
                <div class='info-item'>
                    <strong>🛡️ Seguros Incluidos</strong>
                    <span>Préstamo: {incluir_seguro}<br>Daños: {incluir_seguro_danos}<br>Vehículo: {incluir_seguro_vehiculo}</span>
                </div>
            </div>
        </div>
    """,
                unsafe_allow_html=True)

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
        """,
                    unsafe_allow_html=True)
    else:
        # Multiple payments - show first payment amount
        primera_cuota = df_resultado["Cuota"].iloc[0]
        total_cuotas = len(df_resultado)
        total_pago = df_resultado["Cuota"].sum()
        total_intereses = df_resultado["Interés"].sum()

        st.markdown(f"""
            <div class='compact-grid'>
                <div class='result-box'>
                    <h4>💵 Cuota a Pagar</h4>
                    <div class='result-amount'>L. {primera_cuota:,.2f}</div>
                    <p>{tipo_cuota.lower()}</p>
                </div>
                <div class='result-box' style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);'>
                    <h4>📊 Total a Pagar</h4>
                    <div class='result-amount'>L. {total_pago:,.2f}</div>
                    <p>En {total_cuotas} cuotas</p>
                </div>
                <div class='result-box' style='background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);'>
                    <h4>📈 Total Intereses</h4>
                    <div class='result-amount'>L. {total_intereses:,.2f}</div>
                    <p>Durante el préstamo</p>
                </div>
            </div>
        """,
                    unsafe_allow_html=True)

    # Format DataFrame for display
    df_format = df_resultado.copy()
    for col in [
            "Cuota", "Interés", "Abono", "Seguro de Préstamo", "Seguro Daños",
            "Seguro Vehículo", "Saldo"
    ]:
        if col in df_format.columns:
            df_format[col] = df_format[col].apply(lambda x: f"L. {x:,.2f}")

    st.markdown("---")
    st.markdown("## 🧾 Tabla de Amortización")

    if mostrar_tabla:
        # Show table with or without insurance columns
        columns_to_drop = []
        if incluir_seguro == 'No' and "Seguro de Préstamo" in df_format.columns:
            columns_to_drop.append("Seguro de Préstamo")
        if incluir_seguro_danos == 'No' and "Seguro Daños" in df_format.columns:
            columns_to_drop.append("Seguro Daños")
        if incluir_seguro_vehiculo == 'No' and "Seguro Vehículo" in df_format.columns:
            columns_to_drop.append("Seguro Vehículo")

        if columns_to_drop:
            st.dataframe(df_format.drop(columns=columns_to_drop),
                         use_container_width=True,
                         height=400)
            df_exportar = df_resultado.drop(columns=columns_to_drop)
        else:
            st.dataframe(df_format, use_container_width=True, height=400)
            df_exportar = df_resultado

        # Enhanced download section
        st.markdown("""
            <div class='download-section'>
                <h3>📂 Descargar Tabla de Amortización</h3>
                <p style='margin-bottom: 1.5rem; color: #666;'>Obtén tu tabla de amortización en formato Excel o PDF</p>
            </div>
        """,
                    unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            excel_link = generar_link_descarga_excel(df_exportar)
            # Style the download link with custom class
            excel_link = excel_link.replace(
                '<a href=', '<a class="download-button" href=')
            st.markdown(f'<div style="text-align: center;">{excel_link}</div>',
                        unsafe_allow_html=True)

        with col2:
            pdf_link = generar_link_descarga_pdf(df_exportar)
            # Style the download link with custom class
            pdf_link = pdf_link.replace('<a href=',
                                        '<a class="download-button" href=')
            st.markdown(f'<div style="text-align: center;">{pdf_link}</div>',
                        unsafe_allow_html=True)

        # Enhanced Footer
        st.markdown("""
            <div class='footer'>
                <h3 style='color: white; margin-bottom: 1rem;'>💰 Calculadora de Préstamos Profesional</h3>
                <p style='margin: 0; font-size: 1.1rem;'><strong>Creado por Fredy Thompson</strong></p>
                <p style='margin: 0.5rem 0 0 0; opacity: 0.8;'>Herramienta completa para cálculo de amortizaciones con múltiples opciones de seguro</p>
            </div>
        """,
                    unsafe_allow_html=True)
    else:
        st.info(
            "📋 Marque la casilla arriba para mostrar la tabla de amortización completa."
        )
