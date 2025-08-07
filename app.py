import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Comparador de Medios de Pago", layout="wide")

st.title("🧮 Comparador de Medios de Pago para Compras en Chile")

# ---------- INPUTS PRINCIPALES ----------------

st.markdown("### Ingresar el valor del producto en el comercio")
precio_clp = st.number_input("💰 Precio en CLP (Pesos chilenos)", min_value=0.0, format="%.2f")

# Opciones de medios disponibles en el comercio
st.sidebar.markdown("### Opciones disponibles en el comercio")
uso_clp = st.sidebar.checkbox("Pago en CLP (Pesos chilenos)", value=True)
uso_usd = st.sidebar.checkbox("Pago en USD (Dólares)", value=True)
uso_ars = st.sidebar.checkbox("Pago en ARS (Pesos argentinos)", value=True)
uso_debito = st.sidebar.checkbox("Pago con débito automático", value=True)
uso_credito = st.sidebar.checkbox("Pago con tarjeta de crédito", value=True)
uso_casa_cambio = st.sidebar.checkbox("Cambio en casa de cambio", value=True)

# ---------- COTIZACIONES ----------------

@st.cache_data(show_spinner=False)
def obtener_cotizaciones():
    try:
        bluelytics = requests.get("https://api.bluelytics.com.ar/v2/latest").json()
        dolar_oficial_ars = bluelytics["oficial"]["value_sell"]
    except:
        try:
            oficial = requests.get("https://dolarapi.com/v1/dolares/oficial").json()
            dolar_oficial_ars = oficial["venta"]
        except:
            dolar_oficial_ars = None

    try:
        tarjeta = requests.get("https://dolarapi.com/v1/dolares/tarjeta").json()
        dolar_tarjeta_ars = tarjeta["venta"]
    except:
        dolar_tarjeta_ars = None

    try:
        dolar_clp = requests.get("https://mindicador.cl/api/dolar").json()
        valor_dolar_clp = dolar_clp["serie"][0]["valor"]
    except:
        valor_dolar_clp = None

    return dolar_oficial_ars, dolar_tarjeta_ars, valor_dolar_clp


dolar_oficial_ars, dolar_tarjeta_ars, valor_dolar_clp = obtener_cotizaciones()

# ---------- CONVERSIÓN Y RESULTADOS ----------------

resultados = []

if precio_clp > 0:

    if uso_clp:
        resultados.append(("Pago en CLP directo", precio_clp, "CLP"))

    if uso_usd and valor_dolar_clp:
        precio_usd = precio_clp / valor_dolar_clp
        resultados.append(("Pago en USD", precio_usd, "USD"))

    if uso_ars and valor_dolar_clp and dolar_oficial_ars:
        precio_ars_directo = (precio_clp / valor_dolar_clp) * dolar_oficial_ars
        resultados.append(("Pago en ARS (conversión directa)", precio_ars_directo, "ARS"))

    if uso_debito and valor_dolar_clp and dolar_oficial_ars:
        precio_usd = precio_clp / valor_dolar_clp
        precio_ars_debito = precio_usd * dolar_oficial_ars
        resultados.append(("💳 Pagando con débito automático (dólar oficial)", precio_ars_debito, f"ARS / {precio_usd:.2f} USD"))

    if uso_credito and valor_dolar_clp and dolar_tarjeta_ars:
        precio_usd = precio_clp / valor_dolar_clp
        precio_ars_credito = precio_usd * dolar_tarjeta_ars
        resultados.append(("💳 Pagando con tarjeta de crédito (dólar tarjeta)", precio_ars_credito, f"ARS / {precio_usd:.2f} USD"))

    if uso_casa_cambio:
        tasa_cambio_personal = st.sidebar.number_input("💱 Tasa ofrecida en casa de cambio (CLP por ARS)", min_value=0.01, format="%.2f")
        if tasa_cambio_personal > 0:
            precio_ars_cambio = precio_clp / tasa_cambio_personal
            resultados.append(("Cambio en casa de cambio", precio_ars_cambio, "ARS"))

    if resultados:
        st.markdown("### Resultados de conversión")
        df = pd.DataFrame(resultados, columns=["Opción", "Costo en moneda local", "Moneda"])
        df["Costo en moneda local"] = df["Costo en moneda local"].apply(lambda x: f"{x:,.2f}")
        st.table(df)

        # Elegir el mínimo costo
        min_valor = min([float(x[1]) for x in resultados if "ARS" in x[2]])
        mejor_opcion = [x for x in resultados if ("ARS" in x[2]) and float(x[1]) == min_valor]

        if mejor_opcion:
            st.markdown(f"## ✅ Conviene pagar con: **{mejor_opcion[0][0]}**")

# ---------- PANEL DE COTIZACIONES ----------------

with st.sidebar:
    st.markdown("---")
    st.markdown("### Cotizaciones utilizadas")
    if valor_dolar_clp:
        st.markdown(f"**Dólar Chile (CLP/USD)**: {valor_dolar_clp:.2f}")
    else:
        st.markdown("Dólar Chile no disponible")

    if dolar_oficial_ars:
        st.markdown(f"**Dólar oficial Argentina (ARS/USD)**: {dolar_oficial_ars:.2f}")
    else:
        st.markdown("Dólar oficial no disponible")

    if dolar_tarjeta_ars:
        st.markdown(f"**Dólar tarjeta (ARS/USD)**: {dolar_tarjeta_ars:.2f}")
    else:
        st.markdown("Dólar tarjeta no disponible")

# ---------- MENSAJE DE ERROR SI FALTAN DATOS ----------------

if not all([valor_dolar_clp, dolar_oficial_ars, dolar_tarjeta_ars]):
    with st.expander("ℹ️ Aviso sobre disponibilidad de datos"):
        if not valor_dolar_clp:
            st.warning("❗ No se pudo obtener el valor del dólar en Chile")
        if not dolar_oficial_ars:
            st.warning("❗ No se pudo obtener el dólar oficial en Argentina")
        if not dolar_tarjeta_ars:
            st.warning("❗ No se pudo obtener el dólar tarjeta en Argentina")

