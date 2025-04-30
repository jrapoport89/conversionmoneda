import streamlit as st
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="Comparador de monedas", layout="centered")

st.title("💱 Comparador de opciones de pago en Chile")

st.markdown("""
Ingresá el precio del producto en pesos chilenos (CLP) y las cotizaciones que ofrece el comercio.  
La app te dirá qué opción te conviene: pagar en CLP, dólares o pesos argentinos.
""")

# === Inputs del usuario ===
precio_clp = st.number_input("💰 Precio del producto en CLP", min_value=1.0, step=1.0)
cotizacion_dolar_comercio = st.number_input("💵 Cotización del DÓLAR ofrecida por el comercio (CLP/USD)", min_value=1.0, step=1.0)
cotizacion_ars_comercio = st.number_input("🇦🇷 Cotización del PESO ARG. ofrecida por el comercio (CLP/ARS)", min_value=0.1, step=0.1)

# === API de Bluelytics para el dólar oficial ARS ===
def get_dolar_oficial_ars():
    try:
        response = requests.get("https://api.bluelytics.com.ar/v2/latest")
        data = response.json()
        return data["oficial"]["value_buy"], data["oficial"]["value_sell"]
    except:
        st.warning("No se pudo obtener la cotización oficial del dólar en Argentina.")
        return None, None

# === API de mindicador.cl para el dólar CLP ===
def get_dolar_chile():
    try:
        response = requests.get("https://mindicador.cl/api/dolar")
        data = response.json()
        return data["serie"][0]["valor"]
    except:
        st.warning("No se pudo obtener la cotización del dólar oficial en Chile.")
        return None

# === Obtener cotizaciones ===
dolar_ars_compra, dolar_ars_venta = get_dolar_oficial_ars()
dolar_clp = get_dolar_chile()

if all([dolar_ars_compra, dolar_ars_venta, dolar_clp]) and precio_clp > 0:

    st.subheader("🔎 Resultados del análisis")

    # Cálculos
    precio_usd = precio_clp / cotizacion_dolar_comercio
    precio_ars_directo = precio_clp / cotizacion_ars_comercio

    precio_en_ars_usd = precio_usd * dolar_ars_venta

    # Mostrar conversiones
    st.write(f"💸 Precio en **USD**: {precio_usd:.2f} → equivale a **ARS {precio_en_ars_usd:.2f}** (usando dólar oficial venta)")
    st.write(f"💸 Precio en **ARS directo** (según cotización del comercio): ARS {precio_ars_directo:.2f}")
    st.write(f"💸 Precio en **CLP**: CLP {precio_clp:.2f}")

    # Comparación
    min_valor = min(precio_en_ars_usd, precio_ars_directo)
    if min_valor == precio_en_ars_usd:
        st.success("✅ Te conviene pagar en **DÓLARES**")
    elif min_valor == precio_ars_directo:
        st.success("✅ Te conviene pagar en **PESOS ARGENTINOS**")
    else:
        st.success("✅ Te conviene pagar en **PESOS CHILENOS**")

    # Mostrar cotizaciones oficiales
    st.markdown("---")
    st.markdown(f"📊 Cotización oficial del dólar en Argentina (Compra: **ARS {dolar_ars_compra}**, Venta: **ARS {dolar_ars_venta}**)")
    st.markdown(f"📊 Cotización oficial del dólar en Chile: **CLP {dolar_clp}**")

else:
    st.info("Esperando ingreso de datos o carga de cotizaciones...")

