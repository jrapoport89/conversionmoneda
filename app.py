iimport streamlit as st
import requests
from datetime import datetime

st.set_page_config(page_title="Comparador de Medios de Pago en Chile", layout="wide")

# ---- Funciones auxiliares ----
def obtener_cotizaciones():
    cotizaciones = {}

    try:
        # Argentina - Dólar Oficial
        r = requests.get("https://dolarapi.com/v1/dolares/oficial")
        data = r.json()
        cotizaciones["usd_oficial"] = data["venta"]
        cotizaciones["fecha_usd_oficial"] = data["fechaActualizacion"]

        # Argentina - Dólar Tarjeta
        r = requests.get("https://dolarapi.com/v1/dolares/tarjeta")
        data = r.json()
        cotizaciones["usd_tarjeta"] = data["venta"]
        cotizaciones["fecha_usd_tarjeta"] = data["fechaActualizacion"]

        # Chile - Dólar
        r = requests.get("https://cl.dolarapi.com/v1/cotizaciones/usd")
        data = r.json()
        cotizaciones["usd_chile"] = data["venta"]
        cotizaciones["fecha_usd_chile"] = data["fechaActualizacion"]

    except Exception as e:
        st.error("Error al obtener cotizaciones. Verificá tu conexión.")
        st.stop()

    return cotizaciones

def formatear_fecha(fecha_str):
    return datetime.fromisoformat(fecha_str).strftime('%d/%m/%Y %H:%M')

# ---- Sidebar ----
st.sidebar.header("Ingresá los datos del producto")

# Precio del producto
precio_clp_str = st.sidebar.text_input("Precio del producto en CLP", value="")
try:
    precio_clp = float(precio_clp_str.replace(",", "."))
    if precio_clp <= 0:
        st.sidebar.error("El valor debe ser mayor que cero.")
        st.stop()
except ValueError:
    if precio_clp_str != "":
        st.sidebar.error("Ingresá un número válido.")
    st.stop()

# Selección de medios de pago
st.sidebar.subheader("Seleccioná los medios de pago aceptados por el comercio")
pago_ars = st.sidebar.checkbox("ARS cotizados por el comercio")
pago_usd = st.sidebar.checkbox("USD cotizados por el comercio")
pago_clp_cambio = st.sidebar.checkbox("CLP de casa de cambio")
pago_debito = st.sidebar.checkbox("Débito (USD oficial)")
pago_credito = st.sidebar.checkbox("Crédito (USD tarjeta)")

# Obtener cotizaciones
cotizaciones = obtener_cotizaciones()

st.sidebar.markdown("---")
st.sidebar.markdown("### Cotizaciones actuales")
st.sidebar.markdown(f"- **Dólar Oficial Argentina**: ${cotizaciones['usd_oficial']} (Actualizado: {formatear_fecha(cotizaciones['fecha_usd_oficial'])})")
st.sidebar.markdown(f"- **Dólar Tarjeta**: ${cotizaciones['usd_tarjeta']} (Actualizado: {formatear_fecha(cotizaciones['fecha_usd_tarjeta'])})")
st.sidebar.markdown(f"- **Dólar Chile**: ${cotizaciones['usd_chile']} (Actualizado: {formatear_fecha(cotizaciones['fecha_usd_chile'])})")

# ---- Página principal ----
st.title("Comparador de medios de pago para compras en Chile")

datos = {}

# Ingresos adicionales según selección
if pago_ars:
    ars_cotizado = st.number_input("CLP por cada ARS tomados por el comercio", min_value=0.0001, format="%.4f")
    datos["ARS cotizados por el comercio"] = precio_clp / ars_cotizado if ars_cotizado else None

if pago_usd:
    usd_cotizado = st.number_input("CLP por cada USD tomados por el comercio", min_value=0.0001, format="%.4f")
    datos["USD cotizados por el comercio"] = (precio_clp / usd_cotizado) * cotizaciones["usd_oficial"] if usd_cotizado else None

if pago_clp_cambio:
    st.markdown("### CLP de casa de cambio")
    col1, col2 = st.columns(2)
    with col1:
        clp_por_ars = st.number_input("CLP por cada ARS recibido en casa de cambio", min_value=0.0001, format="%.4f")
        if clp_por_ars:
            datos["CLP desde ARS en casa de cambio"] = precio_clp / clp_por_ars
    with col2:
        clp_por_usd = st.number_input("CLP por cada USD recibido en casa de cambio", min_value=0.0001, format="%.4f")
        if clp_por_usd:
            datos["CLP desde USD en casa de cambio"] = (precio_clp / clp_por_usd) * cotizaciones["usd_oficial"]

if pago_debito:
    datos["Débito (USD oficial)"] = (precio_clp / cotizaciones["usd_chile"]) * cotizaciones["usd_oficial"]

if pago_credito:
    datos["Crédito (USD tarjeta)"] = (precio_clp / cotizaciones["usd_chile"]) * cotizaciones["usd_tarjeta"]

# ---- Tabla de resultados ----
if datos:
    st.markdown("### Comparación de medios de pago")
    import pandas as pd

    df_resultados = pd.DataFrame({
        "Forma de pago": list(datos.keys()),
        "Monto en ARS": [round(v, 2) if v is not None else None for v in datos.values()]
    }).dropna()

    st.table(df_resultados)

    # Recomendación
    if not df_resultados.empty:
        forma_min = df_resultados.loc[df_resultados["Monto en ARS"].idxmin()]
        st.markdown("## 🟩 **CONVIENE PAGAR CON:**")
        st.success(f"**{forma_min['Forma de pago']}**, pagando aproximadamente **ARS {forma_min['Monto en ARS']:.2f}**")
else:
    st.info("Seleccioná al menos un medio de pago y completá los valores para ver los resultados.")

