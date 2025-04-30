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
cotizacion_dolar_comercio = st.number_input("💵 Cotización del DÓLAR que ofrece el comercio (CLP/USD)", min_value=1.0, step=1.0)
cotizacion_ars_comercio = st.number_input("🇦🇷 Cotización del PESO ARG. que ofrece el comercio (CLP/ARS)", min_value=0.1, step=0.1)

# === Obtener cotización oficial USD/ARS desde dolarhoy.com ===
def get_dolar_oficial():
    try:
        url = "https://dolarhoy.com/cotizaciondolaroficial"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        precio = soup.find_all("div", class_="val")[0].text.strip().replace("$", "").replace(".", "").replace(",", ".")
        return float(precio)
    except Exception as e:
        st.warning("No se pudo obtener la cotización del dólar oficial en Argentina.")
        return None

# Simulación de cotización dólar oficial en Chile (USD/CLP)
def get_dolar_chile():
    try:
        response = requests.get("https://mindicador.cl/api/dolar")
        data = response.json()
        return data["serie"][0]["valor"]
    except:
        return 950  # valor estimado si falla

dolar_ars = get_dolar_oficial()
dolar_clp = get_dolar_chile()

if dolar_ars and precio_clp > 0:
    st.subheader("🔎 Resultados del análisis")

    # Cálculos
    precio_usd = precio_clp / cotizacion_dolar_comercio
    precio_ars = precio_clp / cotizacion_ars_comercio

    precio_en_ars_usd = precio_usd * dolar_ars

    st.write(f"💸 Precio en **USD**: {precio_usd:.2f} → equivale a **ARS {precio_en_ars_usd:.2f}** (oficial)")
    st.write(f"💸 Precio en **ARS directo**: ARS {precio_ars:.2f}")
    st.write(f"💸 Precio en **CLP**: {precio_clp:.2f}")

    # Comparación
    mejor_opcion = min(precio_en_ars_usd, precio_ars)
    if mejor_opcion == precio_en_ars_usd:
        st.success("✅ Te conviene pagar en **DÓLARES**")
    elif mejor_opcion == precio_ars:
        st.success("✅ Te conviene pagar en **PESOS ARGENTINOS**")
    else:
        st.success("✅ Te conviene pagar en **PESOS CHILENOS**")

    # Mostrar cotizaciones
    st.markdown("---")
    st.markdown(f"📊 Cotización oficial del dólar en Argentina (USD → ARS): **{dolar_ars}**")
    st.markdown(f"📊 Cotización oficial del dólar en Chile (USD → CLP): **{dolar_clp}**")

else:
    st.info("Esperando ingreso de datos o cotizaciones...")

