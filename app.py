import streamlit as st
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="Comparador de monedas", layout="centered")

st.title("💱 Comparador de opciones de pago en Chile")

st.markdown("""
Ingresá el precio del producto en pesos chilenos (CLP) y las cotizaciones que ofrece el comercio.  
También podés ingresar cotizaciones de una casa de cambio donde hayas cambiado USD o ARS por CLP.  
La app te dirá qué opción te conviene más.
""")

# === Inputs del usuario ===
precio_clp = st.number_input("💰 Precio del producto en CLP", min_value=1.0, step=1.0)
cotizacion_dolar_comercio = st.number_input("💵 Cotización del DÓLAR ofrecida por el comercio (CLP/USD)", min_value=1.0, step=1.0)
cotizacion_ars_comercio = st.number_input("🇦🇷 Cotización del PESO ARG. ofrecida por el comercio (CLP/ARS)", min_value=0.1, step=0.1)

st.markdown("### 🏦 Cotización en casa de cambio")
cotizacion_clp_por_usd = st.number_input("CLP recibidos por cada USD cambiado", min_value=0.0, step=1.0)
cotizacion_clp_por_ars = st.number_input("CLP recibidos por cada ARS cambiado", min_value=0.0, step=0.1)

# === Scraping de Ámbito —
def get_dolar_oficial_ambito():
    try:
        url = "https://www.ambito.com/contenidos/dolar.html"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        tabla = soup.find("div", {"class": "table-responsive"})
        if tabla:
            filas = tabla.find_all("tr")
            for fila in filas:
                cols = fila.find_all("td")
                if len(cols) >= 3 and "oficial" in cols[0].text.lower():
                    compra = cols[1].text.strip().replace("$", "").replace(",", ".")
                    venta = cols[2].text.strip().replace("$", "").replace(",", ".")
                    return float(compra), float(venta)
    except:
        pass
    return None, None

# === Bluelytics como alternativa —
def get_dolar_oficial_bluelytics():
    try:
        response = requests.get("https://api.bluelytics.com.ar/v2/latest")
        data = response.json()
        return data["oficial"]["value_buy"], data["oficial"]["value_sell"]
    except:
        return None, None

# === Dólar en Chile —
def get_dolar_chile():
    try:
        response = requests.get("https://mindicador.cl/api/dolar")
        data = response.json()
        return data["serie"][0]["valor"]
    except:
        return None

# === Obtener cotizaciones ===
dolar_ars_compra, dolar_ars_venta = get_dolar_oficial_ambito()
if not (dolar_ars_compra and dolar_ars_venta):
    st.warning("❗ No se pudo obtener datos de Ámbito, intentando con Bluelytics...")
    dolar_ars_compra, dolar_ars_venta = get_dolar_oficial_bluelytics()

dolar_clp = get_dolar_chile()

# === Procesar si todo está cargado ===
if all([dolar_ars_compra, dolar_ars_venta, dolar_clp]) and precio_clp > 0:

    st.subheader("🔎 Resultados del análisis")

    # Opción 1: pagar en dólares
    precio_usd = precio_clp / cotizacion_dolar_comercio
    precio_en_ars_usd = precio_usd * dolar_ars_venta

    # Opción 2: pagar en pesos argentinos
    precio_ars_directo = precio_clp / cotizacion_ars_comercio

    # Opción 3: usar CLP comprados con USD
    precio_ars_cambio_usd = None
    if cotizacion_clp_por_usd > 0:
        usd_necesarios = precio_clp / cotizacion_clp_por_usd
        precio_ars_cambio_usd = usd_necesarios * dolar_ars_venta

    # Opción 4: usar CLP comprados con ARS
    precio_ars_cambio_ars = None
    if cotizacion_clp_por_ars > 0:
        precio_ars_cambio_ars = precio_clp / cotizacion_clp_por_ars

    # Mostrar conversiones
    st.write(f"💸 Precio en **USD**: {precio_usd:.2f} → equivale a **ARS {precio_en_ars_usd:.2f}** (dólar oficial venta)")
    st.write(f"💸 Precio en **ARS directo** (cotización del comercio): ARS {precio_ars_directo:.2f}")
    if precio_ars_cambio_usd:
        st.write(f"💸 Precio en **ARS usando CLP comprados con USD**: ARS {precio_ars_cambio_usd:.2f}")
    if precio_ars_cambio_ars:
        st.write(f"💸 Precio en **ARS usando CLP comprados con ARS**: ARS {precio_ars_cambio_ars:.2f}")
    st.write(f"💸 Precio en **CLP**: CLP {precio_clp:.2f}")

    # Comparación
    opciones = {
        "DÓLARES": precio_en_ars_usd,
        "PESOS ARGENTINOS": precio_ars_directo,
    }
    if precio_ars_cambio_usd:
        opciones["CLP comprados con USD"] = precio_ars_cambio_usd
    if precio_ars_cambio_ars:
        opciones["CLP comprados con ARS"] = precio_ars_cambio_ars

    mejor_opcion = min(opciones, key=opciones.get)
    st.success(f"✅ Te conviene pagar usando **{mejor_opcion}**")

    # Mostrar cotizaciones oficiales
    st.markdown("---")
    st.markdown(f"📊 Cotización oficial del dólar en Argentina (Compra: **ARS {dolar_ars_compra}**, Venta: **ARS {dolar_ars_venta}**) (fuente: Ámbito/Bluelytics)")
    st.markdown(f"📊 Cotización oficial del dólar en Chile: **CLP {dolar_clp}** (fuente: mindicador.cl)")

else:
    st.info("Esperando ingreso de datos o carga de cotizaciones...")
