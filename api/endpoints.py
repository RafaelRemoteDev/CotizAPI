from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta
from managers.assets_manager import obtener_precio_actual, obtener_precio_por_fecha
from managers.alerts_managers import obtener_alertas_recientes

router = APIRouter()

# Constante para los activos
ACTIVOS = ["GC=F", "SI=F", "BTC-USD", "ZW=F", "CL=F"]


def calcular_variaciones(activos: list, dias: int) -> list:
    """
    Calcula las variaciones porcentuales de precios de los activos en los últimos 'dias' días.
    """
    variaciones = []
    for simbolo in activos:
        precio_actual = obtener_precio_actual(simbolo)
        if precio_actual:
            fecha_pasada = (datetime.now() - timedelta(days=dias)).strftime('%Y-%m-%d')
            precio_pasado = obtener_precio_por_fecha(simbolo, fecha_pasada)
            if precio_pasado:
                variacion = ((precio_actual - precio_pasado) / precio_pasado) * 100
                variaciones.append({"symbol": simbolo, "variation": variacion})
            else:
                variaciones.append({"symbol": simbolo, "variation": None})
        else:
            variaciones.append({"symbol": simbolo, "variation": None})
    return variaciones


@router.get("/")
def endpoint_start():
    """
    Endpoint para mostrar los comandos disponibles en la API.
    """
    return {
        "message": "Bienvenido a CotizAPI! 🤖💸🐂",
        "endpoints": {
            "/assets": "Obtener precios actuales de los activos.",
            "/daily": "Ver variaciones diarias.",
            "/weekly": "Ver variaciones semanales.",
            "/alerts": "Ver alertas recientes generadas.",
        }
    }


@router.get("/assets")
def endpoint_assets():
    """
    Endpoint para obtener precios actuales de los activos.
    """
    precios = []
    for simbolo in ACTIVOS:
        precio = obtener_precio_actual(simbolo)
        precios.append({"symbol": simbolo, "price": precio or None})
    return {"assets": precios}


@router.get("/daily")
def endpoint_daily():
    """
    Endpoint para obtener variaciones diarias de los activos.
    """
    variaciones = calcular_variaciones(ACTIVOS, 1)
    return {"daily_variations": variaciones}


@router.get("/weekly")
def endpoint_weekly():
    """
    Endpoint para obtener variaciones semanales de los activos.
    """
    variaciones = calcular_variaciones(ACTIVOS, 7)
    return {"weekly_variations": variaciones}


@router.get("/alerts")
def endpoint_alerts():
    """
    Endpoint para obtener alertas recientes (últimas 24 horas).
    """
    alertas = obtener_alertas_recientes()
    if not alertas:
        raise HTTPException(status_code=404, detail="No se han registrado alertas en las últimas 24 horas.")

    formatted_alerts = [{"symbol": alerta[0], "date": alerta[1], "message": alerta[2]} for alerta in alertas]
    return {"alerts": formatted_alerts}

