import streamlit as st
import requests

st.set_page_config(page_title="Comparador de pagos", layout="wide")

# ---------- FUNCIONES PARA COTIZACIONES ----------

def obtener_dolar_bluelytics():
    try:
        response = requests.get("https://api.bluelytics.com.ar/v2/latest")
        data = response.json()
        oficial = data["oficial"]["value_avg"]
        tarjeta = oficial * 1.3
        return oficial, tarjeta, "Bluelytics"
    except:
        try:
            oficial = requests.get("https://dolarapi.com/v1/dolares/oficial").json()["venta"]
            tarjeta = requests.get("https://dolarapi.com/v1/dolares/tarjeta").json()["venta"]
            return oficial, tarjeta, "DolarAPI"
        except:
            return None, None, "No disponible"

def obtener_clp_usd():
    try:
        response = requests.get("https://dolarapi.com/v1/cotizaciones/clp")
        data = response.json()
        return data["venta"]
    except:
        return None

# ---------- INTERFAZ ----------

st.title("💱 Comparador de opciones de pago en Chile")

with st.sidebar:
    st.header("Opciones de pago disponibles")
    pago_clp = st.checkbox("Pago en CLP (Pesos Chilenos)")
    pago_usd = st.checkbox("Pago en USD (dólares)")
    pago_ars = st.checkbox("Pago en ARS (pesos argentinos)")
    pago_debito = st.checkbox("Pago con débito automático (dólar oficial)")

    st.markdown("---")
    st.subheader("Cotizaciones utilizadas")
    oficial, tarjeta, fuente_usd = obtener_dolar_bluelytics()
    clp_usd_auto = obtener_clp_usd()
    st.write(f"🔹 Dólar oficial: {oficial} ARS/USD ({fuente_usd})")
    st.write(f"🔹 Dólar tarjeta: {tarjeta} ARS/USD ({fuente_usd})")
    st.write(f"🔹 CLP/USD (automática): {clp_usd_auto} (DolarAPI)")

# ---------- ENTRADA PRINCIPAL ----------

st.markdown("## 🛒 Ingresá el precio del producto")
precio_clp = st.number_input("💰 Precio en CLP (Pesos chilenos)", min_value=0.0, format="%.2f")

# Opciones condicionales de cotización
clp_ars_manual = None
clp_usd_manual = None
usd_clp_comercio = None
ars_clp_comercio = None

if pago_clp:
    clp_ars_manual = st.number_input("🔸 Cotización CLP/ARS ofrecida por casa de cambio", min_value=0.0, format="%.4f")
    clp_usd_manual = st.number_input("🔸 Cotización CLP/USD ofrecida por casa de cambio", min_value=0.0, format="%.4f")

if pago_usd:
    usd_clp_comercio = st.number_input("🔸 Cotización CLP/USD ofrecida por el comercio", min_value=0.0, format="%.4f")
    ars_clp_comercio = st.number_input("🔸 Cotización CLP/ARS ofrecida por el comercio", min_value=0.0, format="%.4f")

# ---------- CÁLCULOS ----------
opciones = []

if pago_clp and clp_ars_manual:
    total_ars_clp = precio_clp * clp_ars_manual
    opciones.append(("CLP → ARS (cambio)", total_ars_clp, "ARS"))

if pago_clp and clp_usd_manual:
    total_usd_clp = precio_clp * clp_usd_manual
    opciones.append(("CLP → USD (cambio)", total_usd_clp, "USD"))

if pago_usd and usd_clp_comercio:
    precio_usd = precio_clp / usd_clp_comercio
    opciones.append(("USD directo (CLP/USD comercio)", precio_usd, "USD"))

if pago_usd and ars_clp_comercio and oficial:
    precio_usd = precio_clp / ars_clp_comercio
    total_ars = precio_usd * oficial
    opciones.append(("USD → ARS (via comercio)", total_ars, "ARS"))

if pago_ars and oficial:
    precio_ars = precio_clp * (1 / clp_usd_auto) * oficial
    opciones.append(("ARS directo (auto)", precio_ars, "ARS"))

if pago_debito and tarjeta:
    precio_usd = precio_clp / clp_usd_auto
    total_ars_tarjeta = precio_usd * tarjeta
    opciones.append(("Débito automático", total_ars_tarjeta, "ARS"))

# ---------- RESULTADOS ----------

if opciones:
    st.markdown("## 🧮 Comparación de costos")
    st.write("Los siguientes valores son aproximados y se calculan en base a las cotizaciones ingresadas y automáticas:")

    opciones.sort(key=lambda x: x[1])

    st.table({
        "Opción": [x[0] for x in opciones],
        "Costo": [f"{x[1]:,.2f}" for x in opciones],
        "Moneda": [x[2] for x in opciones]
    })

    mejor_opcion = opciones[0]
    st.markdown(f"### ✅ Conviene pagar con: **{mejor_opcion[0]}** → {mejor_opcion[1]:,.2f} {mejor_opcion[2]}")
else:
    st.info("Seleccioná al menos una opción y completá los datos para ver la comparación.")

