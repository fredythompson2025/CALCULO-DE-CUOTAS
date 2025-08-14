import streamlit as st
import pandas as pd
from io import BytesIO
import base64
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet

st.set_page_config(page_title="Cuotas de Préstamo", layout="centered")

# ==== Funciones de cálculo ====
def calcular_seguro_prestamo(monto, porcentaje):
    return monto * (porcentaje / 100) if monto > 0 and porcentaje > 0 else 0

def calcular_seguro_danos(monto_asegurar, porcentaje_seguro_danos):
    if monto_asegurar <= 0 or porcentaje_seguro_danos <= 0:
        return 0
    prima = monto_asegurar * (porcentaje_seguro_danos / 100)
    recargo = prima * 0.15
    gastos = 250
    total_seguro = prima + recargo + gastos
    return total_seguro

def calcular_seguro_vehiculo(monto_vehiculo, porcentaje_seguro_vehiculo):
    return monto_vehiculo * (porcentaje_seguro_vehiculo / 100) if monto_vehiculo > 0 and porcentaje_seguro_vehiculo > 0 else 0

def calcular_cuotas_df(monto, plazo_meses, tasa_anual, frecuencia, incluir_seguro, incluir_seguro_danos, incluir_seguro_vehiculo, 
                       monto_asegurar, porcentaje_seguro_danos, monto_vehiculo, porcentaje_seguro_vehiculo):
    
    # Frecuencia de pagos
    frecuencias = {
        "Mensual": 12,
        "Quincenal": 24,
        "Semanal": 52,
        "Diario": 360,
        "Cuatrimestral": 3,
        "Al vencimiento": 0
    }
    pagos_por_año = frecuencias[frecuencia]

    # Calcular seguros anuales
    seguro_anual_prestamo = calcular_seguro_prestamo(monto, incluir_seguro if incluir_seguro != "No" else 0)
    seguro_anual_danos = calcular_seguro_danos(monto_asegurar, porcentaje_seguro_danos) if incluir_seguro_danos == "Sí" else 0
    seguro_anual_vehiculo = calcular_seguro_vehiculo(monto_vehiculo, porcentaje_seguro_vehiculo) if incluir_seguro_vehiculo == "Sí" else 0

    if pagos_por_año == 0:  # Al vencimiento
        tasa_total = tasa_anual / 100 * (plazo_meses / 12)
        interes = monto * tasa_total
        abono = monto
        seguro_prestamo = seguro_anual_prestamo
        seguro_danos = seguro_anual_danos
        seguro_vehiculo = seguro_anual_vehiculo
        cuota_total = interes + abono + seguro_prestamo + seguro_danos + seguro_vehiculo
        return pd.DataFrame([{
            "Pago": 1,
            "Cuota": cuota_total,
            "Interés": interes,
            "Abono": abono,
            "Seguro de Préstamo": seguro_prestamo,
            "Seguro Daños": seguro_danos,
            "Seguro Vehículo": seguro_vehiculo,
            "Saldo": 0
        }])

    # Tasa por periodo
    tasa_periodo = tasa_anual / 100 / pagos_por_año
    numero_pagos = plazo_meses / 12 * pagos_por_año

    # Prorrateo de seguros por periodo
    seguro_prestamo_periodo = seguro_anual_prestamo / pagos_por_año
    seguro_danos_periodo = seguro_anual_danos / pagos_por_año
    seguro_vehiculo_periodo = seguro_anual_vehiculo / pagos_por_año

    # Calcular cuota base
    cuota_base = monto * (tasa_periodo / (1 - (1 + tasa_periodo) ** -numero_pagos))

    saldo = monto
    data = []
    for i in range(1, int(numero_pagos) + 1):
        interes = saldo * tasa_periodo
        abono = cuota_base - interes
        saldo -= abono
        data.append({
            "Pago": i,
            "Cuota": cuota_base + seguro_prestamo_periodo + seguro_danos_periodo + seguro_vehiculo_periodo,
            "Interés": interes,
            "Abono": abono,
            "Seguro de Préstamo": seguro_prestamo_periodo,
            "Seguro Daños": seguro_danos_periodo,
            "Seguro Vehículo": seguro_vehiculo_periodo,
            "Saldo": max(saldo, 0)
        })
    return pd.DataFrame(data)

# ==== Interfaz ====
st.title("Calculadora de Cuotas de Préstamo")

monto = st.number_input("Monto del préstamo", min_value=0.0, format="%.2f")
plazo_meses = st.number_input("Plazo (meses)", min_value=1)
tasa_anual = st.number_input("Tasa anual (%)", min_value=0.0, format="%.2f")
frecuencia = st.selectbox("Frecuencia de pago", ["Mensual", "Quincenal", "Semanal", "Diario", "Cuatrimestral", "Al vencimiento"])
incluir_seguro = st.number_input("Porcentaje seguro de préstamo (%)", min_value=0.0, format="%.2f")
incluir_seguro_danos = st.radio("¿Incluir seguro de daños?", ["Sí", "No"])
porcentaje_seguro_danos = st.number_input("Porcentaje seguro de daños (%)", min_value=0.0, format="%.2f") if incluir_seguro_danos == "Sí" else 0
monto_asegurar = st.number_input("Monto a asegurar (Daños)", min_value=0.0, format="%.2f") if incluir_seguro_danos == "Sí" else 0
incluir_seguro_vehiculo = st.radio("¿Incluir seguro de vehículo?", ["Sí", "No"])
porcentaje_seguro_vehiculo = st.number_input("Porcentaje seguro de vehículo (%)", min_value=0.0, format="%.2f") if incluir_seguro_vehiculo == "Sí" else 0
monto_vehiculo = st.number_input("Monto a asegurar (Vehículo)", min_value=0.0, format="%.2f") if incluir_seguro_vehiculo == "Sí" else 0

if st.button("Calcular"):
    df = calcular_cuotas_df(monto, plazo_meses, tasa_anual, frecuencia, incluir_seguro, incluir_seguro_danos, incluir_seguro_vehiculo,
                            monto_asegurar, porcentaje_seguro_danos, monto_vehiculo, porcentaje_seguro_vehiculo)
    st.dataframe(df, use_container_width=True)

