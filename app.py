import streamlit as st
import requests
from bs4 import BeautifulSoup
from datetime import datetime

st.set_page_config(page_title="Comparador de Medios de Pago en Chile", layout="centered")
st.title("Comparador de Medios de Pago en Chile")

# --- Sidebar: Medios de pago ---
st.sidebar.subheader("Seleccioná los medios de pago que acepta el comercio")
medios_pago = {
    "CLP en casa de cambio": st.sidebar.checkbox("CLP en casa de cambio"),
    "USD en comercio": st.sidebar.checkbox("USD en comercio"),
    "ARS en comercio": st.sidebar.checkbox("ARS en comercio"),
    "Débito (USD oficial)": st.sidebar.checkbox("Débito (USD oficial)"),
    "Crédito (USD tarjeta)": st.sidebar.checkbox("Crédito (USD tarjeta)")
}

# --- Funciones ---
def obtener_dolar_oficial_arg():
    try:
        response = requests.get("https://dolarapi.com/v1/dolares/oficial")
        data = response.json()
        return data['venta']
    except:
        return None

def obtener_dolar_oficial_cl():
    try:
        response = requests.get("https://dolarapi.com/v1/dolares/clp")
        data = response.json()
        return data['venta']
    except:
        return None

# --- Ingreso de datos ---
st.subheader("Ingresá el valor del producto en pesos chilenos (CLP)")
precio_clp = st.number_input("Precio del producto (CLP):", min_value=0.0, format="%.2f")

st.subheader("Cotizaciones que te ofrece el comercio")
cotizacion_clp_ars = st.number_input("Cotización ARS/CLP (cuántos CLP por 1 ARS):", min_value=0.0, format="%.2f")
cotizacion_clp_usd = st.number_input("Cotización USD/CLP (cuántos CLP por 1 USD):", min_value=0.0, format="%.2f")

st.subheader("Cotización obtenida en casa de cambio")
cotizacion_casa_cambio = st.number_input("Cotización USD/CLP en casa de cambio:", min_value=0.0, format="%.2f")

# --- Obtener cotizaciones oficiales ---
dolar_oficial_arg = obtener_dolar_oficial_arg()
dolar_oficial_cl = obtener_dolar_oficial_cl()
dolar_tarjeta = dolar_oficial_arg * 1.75 if dolar_oficial_arg else None

# --- Cálculos ---
opciones = []

if medios_pago["CLP en casa de cambio"] and cotizacion_casa_cambio > 0 and dolar_oficial_arg:
    ars_total = (precio_clp / cotizacion_casa_cambio) * dolar_oficial_arg
    opciones.append(("CLP en casa de cambio", ars_total, precio_clp / cotizacion_casa_cambio))

if medios_pago["USD en comercio"] and cotizacion_clp_usd > 0 and dolar_oficial_arg:
    ars_total = (precio_clp / cotizacion_clp_usd) * dolar_oficial_arg
    opciones.append(("USD en comercio", ars_total, precio_clp / cotizacion_clp_usd))

if medios_pago["ARS en comercio"] and cotizacion_clp_ars > 0:
    ars_total = precio_clp / cotizacion_clp_ars
    opciones.append(("ARS en comercio", ars_total, None))

if medios_pago["Débito (USD oficial)"] and dolar_oficial_arg and cotizacion_clp_usd > 0:
    ars_total = (precio_clp / cotizacion_clp_usd) * dolar_oficial_arg
    opciones.append(("Débito (USD oficial)", ars_total, precio_clp / cotizacion_clp_usd))

if medios_pago["Crédito (USD tarjeta)"] and dolar_tarjeta and cotizacion_clp_usd > 0:
    ars_total = (precio_clp / cotizacion_clp_usd) * dolar_tarjeta
    opciones.append(("Crédito (USD tarjeta)", ars_total, precio_clp / cotizacion_clp_usd))

# --- Resultados ---
if opciones:
    st.subheader("Resultados")
    opciones.sort(key=lambda x: x[1])
    for medio, ars, usd_usado in opciones:
        if usd_usado:
            st.write(f"💳 {medio}: ARS {ars:.2f} / USD {usd_usado:.2f}")
        else:
            st.write(f"💳 {medio}: ARS {ars:.2f}")
    mejor_opcion = opciones[0][0]
    st.success(f"Conviene pagar con: {mejor_opcion}")
else:
    st.info("Seleccioná al menos un medio de pago e ingresá las cotizaciones para ver resultados.")

