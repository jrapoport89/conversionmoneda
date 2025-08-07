# app.py
import streamlit as st
import requests
import pandas as pd
from bs4 import BeautifulSoup

# Títulos
st.title("Comparador de Medios de Pago en Chile")
st.markdown("Ingrese los valores para comparar el costo en ARS según el medio de pago disponible en el comercio.")

# Entradas del usuario en la barra lateral
st.sidebar.header("Ingresar información del comercio")

valor_producto_clp = st.sidebar.number_input("Precio del producto en CLP", min_value=0.0, step=100.0)

st.sidebar.subheader("Cotizaciones del comercio")
clp_usd_comercio = st.sidebar.number_input("CLP por 1 USD (comercio)", min_value=0.0, step=10.0)
clp_ars_comercio = st.sidebar.number_input("CLP por 1 ARS (comercio)", min_value=0.0, step=1.0)

st.sidebar.subheader("Cotización en casa de cambio")
usd_ars_casadecambio = st.sidebar.number_input("USD por 1 ARS (casa de cambio)", min_value=0.0, step=0.01)
clp_usd_casadecambio = st.sidebar.number_input("CLP por 1 USD (casa de cambio)", min_value=0.0, step=10.0)
clp_ars_casadecambio = st.sidebar.number_input("CLP por 1 ARS (casa de cambio)", min_value=0.0, step=1.0)

st.sidebar.subheader("Opciones de pago aceptadas")
opciones = {
    "CLP (casa de cambio)": st.sidebar.checkbox("Pago en CLP (cambio previo)"),
    "USD": st.sidebar.checkbox("Pago en USD"),
    "ARS": st.sidebar.checkbox("Pago en ARS"),
    "Débito": st.sidebar.checkbox("Pago con Débito"),
    "Crédito": st.sidebar.checkbox("Pago con Crédito")
}

# Funciones para obtener cotizaciones oficiales
@st.cache_data

def obtener_dolar_oficial():
    try:
        response = requests.get("https://dolarapi.com/v1/dolares/oficial")
        return float(response.json()['venta'])
    except:
        return None

@st.cache_data

def obtener_dolar_tarjeta():
    try:
        response = requests.get("https://dolarapi.com/v1/dolares/tarjeta")
        return float(response.json()['venta'])
    except:
        return None

@st.cache_data

def obtener_dolar_chile():
    try:
        soup = BeautifulSoup(requests.get("https://si3.bcentral.cl/Indicadoressiete/secure/Indicadoresdiarios.aspx").text, 'html.parser')
        valor = soup.find('span', id='lblValorDolar').text.strip().replace("$", "").replace(".", "").replace(",", ".")
        return float(valor)
    except:
        return None

# Obtener cotizaciones
usd_ars_oficial = obtener_dolar_oficial()
usd_ars_tarjeta = obtener_dolar_tarjeta()
clp_usd_oficial = obtener_dolar_chile()

# Cálculo de opciones
opciones_pago = []

if opciones["CLP (casa de cambio)"] and clp_ars_casadecambio:
    ars_total = valor_producto_clp / clp_ars_casadecambio
    opciones_pago.append(["Pago en CLP (cambio previo)", f"CLP/ARS casa de cambio = {clp_ars_casadecambio}", round(ars_total, 2)])

if opciones["USD"] and clp_usd_comercio and usd_ars_oficial:
    usd = valor_producto_clp / clp_usd_comercio
    ars_total = usd * usd_ars_oficial
    opciones_pago.append(["Pago en USD", f"CLP/USD comercio = {clp_usd_comercio}, USD/ARS oficial = {usd_ars_oficial}", round(ars_total, 2)])

if opciones["ARS"] and clp_ars_comercio:
    ars_total = valor_producto_clp / clp_ars_comercio
    opciones_pago.append(["Pago en ARS", f"CLP/ARS comercio = {clp_ars_comercio}", round(ars_total, 2)])

if opciones["Débito"] and clp_usd_oficial and usd_ars_oficial:
    usd = valor_producto_clp / clp_usd_oficial
    ars_total = usd * usd_ars_oficial
    opciones_pago.append(["Pago con Débito", f"CLP/USD Chile API = {clp_usd_oficial}, USD/ARS oficial = {usd_ars_oficial}", round(ars_total, 2)])

if opciones["Crédito"] and clp_usd_oficial and usd_ars_tarjeta:
    usd = valor_producto_clp / clp_usd_oficial
    ars_total = usd * usd_ars_tarjeta
    opciones_pago.append(["Pago con Crédito", f"CLP/USD Chile API = {clp_usd_oficial}, USD/ARS tarjeta = {usd_ars_tarjeta}", round(ars_total, 2)])

# Mostrar resultados
if opciones_pago:
    df = pd.DataFrame(opciones_pago, columns=["Opción", "Cotizaciones usadas", "Costo en ARS"])
    df = df.sort_values("Costo en ARS")
    st.subheader("Comparativa de Opciones de Pago")
    st.dataframe(df, use_container_width=True)
    mejor = df.iloc[0]
    st.success(f"Conviene pagar con: **{mejor['Opción']}** (≈ {mejor['Costo en ARS']} ARS)")
else:
    st.info("Seleccione al menos una opción de pago y complete los datos necesarios para calcular.")


