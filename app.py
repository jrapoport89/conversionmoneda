import streamlit as st
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="Comparador de monedas", layout="centered")

st.title("💱 Comparador de opciones de pago en Chile")

st.markdown("""
Seleccioná los medios de pago disponibles en el comercio y luego completá los valores correspondientes.  
La app calculará cuál te conviene más.
""")

# === Paso 1: Selección de medios disponibles ===
st.sidebar.markdown("### Seleccioná los medios de pago aceptados por el comercio:")
usa_clp = st.sidebar.checkbox("💸 Pagar en CLP", value=True)
usa_usd = st.sidebar.checkbox("💵 Pagar en USD", value=False)
usa_ars = st.sidebar.checkbox("🇦🇷 Pagar en ARS", value=False)
usa_debito = st.sidebar.checkbox("💳 Débito automático", value=False)
usa_credito = st.sidebar.checkbox("💳 Tarjeta de crédito", value=False)
usa_cambio = st.sidebar.checkbox("🏦 Cambiar USD o ARS por CLP", value=False)

# === Paso 2: Ingreso de datos ===
precio_clp = st.number_input("💰 Precio del producto en CLP", min_value=1.0, step=1.0)

if usa_usd:
    cotizacion_dolar_comercio = st.number_input("💵 Cotización del DÓLAR ofrecida por el comercio (CLP/USD)", min_value=1.0, step=1.0)

if usa_ars:
    cotizacion_ars_comercio = st.number_input("🇦🇷 Cotización del PESO ARG. ofrecida por el comercio (CLP/ARS)", min_value=0.1, step=0.1)

if usa_cambio:
    st.markdown("### 🏦 Cotización en casa de cambio")
    cotizacion_clp_por_usd = st.number_input("CLP recibidos por cada USD cambiado", min_value=0.0, step=1.0)
    cotizacion_clp_por_ars = st.number_input("CLP recibidos por cada ARS cambiado", min_value=0.0, step=0.1)

# === Scraping de cotizaciones oficiales
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

def get_dolar_oficial_bluelytics():
    try:
        response = requests.get("https://api.bluelytics.com.ar/v2/latest")
        data = response.json()
        return data["oficial"]["value_buy"], data["oficial"]["value_sell"]
    except:
        return None, None

def get_dolar_chile():
    try:
        response = requests.get("https://mindicador.cl/api/dolar")
        data = response.json()
        return data["serie"][0]["valor"]
    except:
        return None

dolar_ars_compra, dolar_ars_venta = get_dolar_oficial_ambito()
if not (dolar_ars_compra and dolar_ars_venta):
    st.warning("❗ No se pudo obtener datos de Ámbito, intentando con Bluelytics...")
    dolar_ars_compra, dolar_ars_venta = get_dolar_oficial_bluelytics()

dolar_clp = get_dolar_chile()

# === Procesar si todo está listo ===
if all([dolar_ars_compra, dolar_ars_venta, dolar_clp]) and precio_clp > 0:

    st.subheader("🔎 Resultados del análisis")

    opciones = {}

    if usa_usd:
        precio_usd = precio_clp / cotizacion_dolar_comercio
        precio_en_ars_usd = precio_usd * dolar_ars_venta
        opciones["DÓLARES"] = precio_en_ars_usd
        st.write(f"💵 Pagando en **USD**: ARS {precio_en_ars_usd:.2f} (USD {precio_usd:.2f})")

    if usa_ars:
        precio_ars_directo = precio_clp / cotizacion_ars_comercio
        opciones["PESOS ARGENTINOS"] = precio_ars_directo
        st.write(f"🇦🇷 Pagando en **ARS directo**: ARS {precio_ars_directo:.2f}")

    if usa_cambio:
        if cotizacion_clp_por_usd > 0:
            usd_necesarios = precio_clp / cotizacion_clp_por_usd
            precio_ars_cambio_usd = usd_necesarios * dolar_ars_venta
            opciones["CLP comprados con USD"] = precio_ars_cambio_usd
            st.write(f"💱 CLP comprados con **USD**: ARS {precio_ars_cambio_usd:.2f}")

        if cotizacion_clp_por_ars > 0:
            precio_ars_cambio_ars = precio_clp / cotizacion_clp_por_ars
            opciones["CLP comprados con ARS"] = precio_ars_cambio_ars
            st.write(f"💱 CLP comprados con **ARS**: ARS {precio_ars_cambio_ars:.2f}")

    if usa_debito:
        precio_usd_debito = precio_clp / dolar_clp
        precio_ars_debito = precio_usd_debito * dolar_ars_venta
        opciones["DÉBITO AUTOMÁTICO"] = precio_ars_debito
        st.write(f"💳 Pagando con **débito automático** (dólar oficial): ARS {precio_ars_debito:.2f} / USD {precio_usd_debito:.2f} a descontar de tu cuenta")

    if usa_credito:
        precio_usd_credito = precio_clp / dolar_clp
        precio_ars_credito = precio_usd_credito * dolar_ars_venta * 1.6
        opciones["CRÉDITO (dólar tarjeta)"] = precio_ars_credito
        st.write(f"💳 Pagando con **tarjeta de crédito** (dólar tarjeta): ARS {precio_ars_credito:.2f} / USD {precio_usd_credito:.2f} a descontar de tu cuenta")

    # Comparación final
    if opciones:
        mejor_opcion = min(opciones, key=opciones.get)
        st.success(f"✅ Te conviene pagar usando **{mejor_opcion}**")

    st.markdown("---")
    st.markdown(f"📊 Cotización oficial del dólar en Argentina: Compra ARS {dolar_ars_compra}, Venta ARS {dolar_ars_venta}")
    st.markdown(f"📊 Cotización oficial del dólar en Chile: CLP {dolar_clp}")

else:
    st.info("Esperando ingreso de datos o carga de cotizaciones...")
