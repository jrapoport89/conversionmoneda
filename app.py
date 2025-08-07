import streamlit as st
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="Comparador de Medios de Pago en Chile", layout="centered")

st.title("💱 Comparador de Medios de Pago en Chile")
st.markdown("""
Esta herramienta te ayuda a decidir con qué medio conviene pagar al comprar en un comercio chileno.
Seleccioná las opciones que acepta el comercio y completá las cotizaciones si aplica. El resultado mostrará el costo en pesos argentinos (ARS) según cada alternativa.
""")

# --- Funciones para obtener cotizaciones oficiales ---
def obtener_dolar_oficial():
    try:
        r = requests.get("https://dolarapi.com/v1/dolares/oficial")
        return float(r.json()['venta'])
    except:
        return None

def obtener_dolar_tarjeta():
    try:
        r = requests.get("https://dolarapi.com/v1/dolares/tarjeta")
        return float(r.json()['venta'])
    except:
        return None

def obtener_clp_usd_mecon():
    try:
        url = "https://si3.bcentral.cl/Indicadoressiete/secure/Indicadoresdiarios.aspx"
        r = requests.get(url)
        soup = BeautifulSoup(r.content, 'html.parser')
        clp_usd = soup.find("span", id="lblValorDolar").text.replace("$", "").replace(".", "").replace(",", ".")
        return float(clp_usd)
    except:
        return None

# --- Inputs del usuario ---
precio_producto = st.number_input("💰 Precio del producto (en moneda del comercio)", min_value=0.0, step=0.01, format="%.2f")

st.subheader("💳 Medios de pago aceptados por el comercio")
opciones = {
    "Pago en CLP (efectivo o transferencia)": st.checkbox("CLP"),
    "Pago en USD (efectivo o tarjeta)": st.checkbox("USD"),
    "Pago en ARS (efectivo o transferencia)": st.checkbox("ARS"),
    "Pago con débito": st.checkbox("Débito"),
    "Pago con crédito": st.checkbox("Crédito"),
}

st.markdown("---")
st.subheader("🔧 Cotizaciones requeridas")

# Variables de cotización ingresadas por usuario
tasa_cambio_clp_ars_usuario = None
tasa_cambio_clp_usd_usuario = None
tasa_cambio_clp_ars_comercio = None
tasa_cambio_clp_usd_comercio = None

if opciones["Pago en CLP (efectivo o transferencia)"]:
    tasa_cambio_clp_ars_usuario = st.number_input("Cotización CLP/ARS de casa de cambio (por cada CLP, cuántos ARS)", min_value=0.0001, step=0.0001, format="%.4f")

if opciones["Pago en USD (efectivo o tarjeta)"]:
    tasa_cambio_clp_usd_comercio = st.number_input("Cotización CLP/USD del comercio", min_value=0.01, step=0.01, format="%.2f")

if opciones["Pago en ARS (efectivo o transferencia)"]:
    tasa_cambio_clp_ars_comercio = st.number_input("Cotización CLP/ARS del comercio", min_value=0.0001, step=0.0001, format="%.4f")

# --- Cotizaciones externas ---
dolar_oficial_ars = obtener_dolar_oficial()
dolar_tarjeta_ars = obtener_dolar_tarjeta()
clp_usd_mecon = obtener_clp_usd_mecon()

# --- Cálculos de cada opción ---
resultados = []

if opciones["Pago en CLP (efectivo o transferencia)"] and tasa_cambio_clp_ars_usuario:
    costo_ars = precio_producto * tasa_cambio_clp_ars_usuario
    resultados.append(("Pago en CLP", costo_ars, f"CLP/ARS ingresado: {tasa_cambio_clp_ars_usuario:.4f}"))

if opciones["Pago en USD (efectivo o tarjeta)"] and tasa_cambio_clp_usd_comercio and dolar_oficial_ars:
    valor_usd = precio_producto / tasa_cambio_clp_usd_comercio
    costo_ars = valor_usd * dolar_oficial_ars
    resultados.append(("Pago en USD", costo_ars, f"CLP/USD comercio: {tasa_cambio_clp_usd_comercio:.2f}, USD a ARS oficial: {dolar_oficial_ars:.2f}"))

if opciones["Pago en ARS (efectivo o transferencia)"] and tasa_cambio_clp_ars_comercio:
    costo_ars = precio_producto * tasa_cambio_clp_ars_comercio
    resultados.append(("Pago en ARS", costo_ars, f"CLP/ARS comercio: {tasa_cambio_clp_ars_comercio:.4f}"))

if opciones["Pago con débito"] and clp_usd_mecon and dolar_oficial_ars:
    valor_usd = precio_producto / clp_usd_mecon
    costo_ars = valor_usd * dolar_oficial_ars
    resultados.append(("Débito", costo_ars, f"CLP/USD MEcon: {clp_usd_mecon:.2f}, USD a ARS oficial: {dolar_oficial_ars:.2f}"))

if opciones["Pago con crédito"] and clp_usd_mecon and dolar_tarjeta_ars:
    valor_usd = precio_producto / clp_usd_mecon
    costo_ars = valor_usd * dolar_tarjeta_ars
    resultados.append(("Crédito", costo_ars, f"CLP/USD MEcon: {clp_usd_mecon:.2f}, USD a ARS tarjeta: {dolar_tarjeta_ars:.2f}"))

# --- Mostrar resultados ---
if resultados:
    st.markdown("---")
    st.subheader("📊 Comparación de costos en ARS")

    for medio, costo, detalle in resultados:
        st.write(f"**{medio}**: {costo:.2f} ARS")
        st.caption(detalle)

    # Recomendación
    medio_mas_barato = min(resultados, key=lambda x: x[1])
    st.markdown(f"### ✅ Conviene pagar con: **{medio_mas_barato[0]}**")
else:
    st.warning("Seleccioná al menos una opción y completá las cotizaciones necesarias.")

