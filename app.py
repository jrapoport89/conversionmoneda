import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="Comparador de Cotizaciones", layout="wide")
st.title("Comparador de formas de pago en Chile")

# ----------- ENTRADAS DEL USUARIO ----------- #

st.sidebar.header("Datos del producto")
clp_price = st.sidebar.number_input("Precio en CLP (pesos chilenos)", min_value=0.0, step=1.0)
usd_price = st.sidebar.number_input("Precio en USD", min_value=0.0, step=1.0)
ars_price = st.sidebar.number_input("Precio en ARS (pesos argentinos)", min_value=0.0, step=1.0)

st.sidebar.header("Opciones de pago aceptadas por el comercio")
show_clp = st.sidebar.checkbox("Acepta CLP", value=True)
show_usd = st.sidebar.checkbox("Acepta USD", value=True)
show_ars = st.sidebar.checkbox("Acepta ARS", value=True)
show_debito = st.sidebar.checkbox("Acepta Débito", value=True)
show_credito = st.sidebar.checkbox("Acepta Crédito", value=True)

st.sidebar.markdown("---")
st.sidebar.subheader("Cotizaciones")

# ----------- SCRAPING OBTENCIÓN DE COTIZACIONES ----------- #
def get_exchange_rates():
    try:
        bluelytics = requests.get("https://api.bluelytics.com.ar/v2/latest").json()
        oficial = bluelytics['oficial']['value_sell']
        tarjeta = oficial * 1.75
        blue = bluelytics['blue']['value_sell']
    except:
        try:
            oficial = requests.get("https://dolarapi.com/v1/dolares/oficial").json()['venta']
            tarjeta = requests.get("https://dolarapi.com/v1/dolares/tarjeta").json()['venta']
            blue = oficial * 1.95
        except:
            st.session_state.fetch_error = True
            oficial = tarjeta = blue = None
    return oficial, tarjeta, blue

def get_usd_to_clp():
    try:
        r = requests.get("https://mindicador.cl/api/dolar")
        return r.json()['serie'][0]['valor']
    except:
        return None

# ----------- LLAMADO A FUNCIONES ----------- #
usd_to_ars_oficial, usd_to_ars_tarjeta, usd_to_ars_blue = get_exchange_rates()
usd_to_clp = get_usd_to_clp()

# ----------- MOSTRAR COTIZACIONES ----------- #
st.sidebar.markdown(f"Dólar Chile (CLP/USD): {usd_to_clp if usd_to_clp else 'Error'}")
st.sidebar.markdown(f"Dólar Oficial (ARS/USD): {usd_to_ars_oficial if usd_to_ars_oficial else 'Error'}")
st.sidebar.markdown(f"Dólar Tarjeta (ARS/USD): {usd_to_ars_tarjeta if usd_to_ars_tarjeta else 'Error'}")

# ----------- CÁLCULOS ----------- #
st.markdown("## Opciones de pago")

if show_clp and usd_to_clp:
    st.subheader("💰 Pagando con CLP")
    st.write(f"USD estimado: {round(clp_price / usd_to_clp, 2)}")

if show_usd:
    st.subheader("💵 Pagando con USD")
    st.write(f"USD a pagar: {usd_price}")

if show_ars:
    st.subheader("💸 Pagando con ARS")
    st.write(f"ARS a pagar: {ars_price}")

if show_debito and usd_to_clp and usd_to_ars_oficial:
    usd_value = clp_price / usd_to_clp
    ars_equivalent = usd_value * usd_to_ars_oficial
    st.subheader("💳 Pagando con débito automático (dólar oficial)")
    st.write(f"ARS {round(ars_equivalent, 2)} / USD {round(usd_value, 2)} descontados de tu cuenta")

if show_credito and usd_to_clp and usd_to_ars_tarjeta:
    usd_value = clp_price / usd_to_clp
    ars_equivalent = usd_value * usd_to_ars_tarjeta
    st.subheader("💳 Pagando con crédito (dólar tarjeta)")
    st.write(f"ARS {round(ars_equivalent, 2)} / USD {round(usd_value, 2)} descontados de tu cuenta")

# ----------- MENSAJE DE ERROR ----------- #
if 'fetch_error' in st.session_state and st.session_state.fetch_error:
    st.markdown("---")
    st.warning("❗ No se pudo obtener los datos desde Bluelytics ni DolarAPI. Algunas funciones pueden no estar disponibles.")
