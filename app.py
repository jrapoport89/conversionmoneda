import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup

# Funciones para obtener cotizaciones automáticas desde DolarAppi
def obtener_dolar_oficial():
    try:
        response = requests.get("https://dolarapi.com/v1/dolares/oficial")
        if response.status_code == 200:
            return response.json()['venta']
    except:
        pass
    return None

def obtener_dolar_tarjeta():
    try:
        response = requests.get("https://dolarapi.com/v1/dolares/tarjeta")
        if response.status_code == 200:
            return response.json()['venta']
    except:
        pass
    return None

def obtener_dolar_chile():
    try:
        url = "https://www.bcentral.cl/"
        page = requests.get(url)
        soup = BeautifulSoup(page.content, "html.parser")
        valor = soup.find("span", class_="num-circle").text.strip().replace("$", "").replace(".", "").replace(",", ".")
        return float(valor)
    except:
        return None

# Título
st.title("Comparador de Medios de Pago en Chile")

# Sección lateral con cotizaciones automáticas
st.sidebar.header("Cotizaciones automáticas")
dolar_oficial = obtener_dolar_oficial()
dolar_tarjeta = obtener_dolar_tarjeta()
dolar_chile = obtener_dolar_chile()

st.sidebar.write(f"💵 Dólar oficial AR: ${dolar_oficial if dolar_oficial else 'No disponible'}")
st.sidebar.write(f"💳 Dólar tarjeta: ${dolar_tarjeta if dolar_tarjeta else 'No disponible'}")
st.sidebar.write(f"🇨🇱 Dólar oficial CL: ${dolar_chile if dolar_chile else 'No disponible'}")

# Selección de medios de pago
st.subheader("Seleccioná los medios de pago que acepta el comercio")
medios_pago = {
    "CLP en casa de cambio": st.checkbox("CLP en casa de cambio"),
    "USD en comercio": st.checkbox("USD en comercio"),
    "ARS en comercio": st.checkbox("ARS en comercio"),
    "Débito (USD oficial)": st.checkbox("Débito (USD oficial)"),
    "Crédito (USD tarjeta)": st.checkbox("Crédito (USD tarjeta)")
}

# Ingreso de precios en CLP
st.subheader("Precios de los productos en CLP")
num_productos = st.number_input("Cantidad de productos a comparar", min_value=1, step=1)
precios = []
for i in range(num_productos):
    precio = st.number_input(f"Precio producto {i+1} (CLP)", min_value=0.0, step=1.0)
    precios.append(precio)

# Ingreso de cotizaciones manuales
st.subheader("Cotizaciones ingresadas por el usuario")
cotizaciones = {}
if medios_pago["CLP en casa de cambio"]:
    cotizaciones['clp_ars_cambio'] = st.number_input("CAMBIO ARS A CLP (casa de cambio)", min_value=0.01, step=0.01)
    cotizaciones['clp_usd_cambio'] = st.number_input("CAMBIO USD A CLP (casa de cambio)", min_value=0.01, step=0.01)
if medios_pago["USD en comercio"]:
    cotizaciones['clp_usd_comercio'] = st.number_input("COTIZACIÓN DÓLAR DEL COMERCIO (CLP/USD)", min_value=0.01, step=0.01)
if medios_pago["ARS en comercio"]:
    cotizaciones['clp_ars_comercio'] = st.number_input("COTIZACIÓN DE ARS DEL COMERCIO (CLP/ARS)", min_value=0.01, step=0.01)

# Función para convertir precios
resultados = []
for clp in precios:
    fila = {"Precio CLP": clp}
    if medios_pago["CLP en casa de cambio"] and cotizaciones.get('clp_ars_cambio'):
        fila["CLP → ARS (casa de cambio)"] = clp / cotizaciones['clp_ars_cambio']
    if medios_pago["USD en comercio"] and cotizaciones.get('clp_usd_comercio') and dolar_oficial:
        fila["USD en comercio"] = clp / (cotizaciones['clp_usd_comercio'] * dolar_oficial)
    if medios_pago["ARS en comercio"] and cotizaciones.get('clp_ars_comercio'):
        fila["ARS en comercio"] = clp / cotizaciones['clp_ars_comercio']
    if medios_pago["Débito (USD oficial)"] and dolar_chile and dolar_oficial:
        fila["Débito (USD oficial)"] = clp / dolar_chile * dolar_oficial
    if medios_pago["Crédito (USD tarjeta)"] and dolar_chile and dolar_tarjeta:
        fila["Crédito (USD tarjeta)"] = clp / dolar_chile * dolar_tarjeta
    resultados.append(fila)

# Mostrar resultados
if resultados:
    df_resultados = pd.DataFrame(resultados)
    st.subheader("Comparación de precios en ARS")
    st.dataframe(df_resultados.style.format("{:.2f}"))

