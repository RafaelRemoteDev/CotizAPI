from fastapi import APIRouter
from datetime import datetime, timedelta  # Para manejar fechas y cálculos de tiempo
from managers.assets_manager import obtener_precio_actual, obtener_precio_por_fecha  # Para datos de precios
from managers.alerts_managers import obtener_alertas_recientes  # Para alertas recientes


router = APIRouter()

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
    activos = ["GC=F", "SI=F", "BTC-USD", "ZW=F", "CL=F"]
    precios = []

    for simbolo in activos:
        precio = obtener_precio_actual(simbolo)
        if precio:
            precios.append({"symbol": simbolo, "price": precio})
        else:
            precios.append({"symbol": simbolo, "price": None})

    return {"assets": precios}


@router.get("/daily")
def endpoint_daily():
    """
    Endpoint para obtener variaciones diarias de los activos.
    """
    activos = ["GC=F", "SI=F", "BTC-USD", "ZW=F", "CL=F"]
    variaciones = []

    for simbolo in activos:
        precio_actual = obtener_precio_actual(simbolo)
        if precio_actual:
            fecha_ayer = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
            precio_ayer = obtener_precio_por_fecha(simbolo, fecha_ayer)
            if precio_ayer:
                variacion = ((precio_actual - precio_ayer) / precio_ayer) * 100
                variaciones.append({"symbol": simbolo, "daily_variation": variacion})
            else:
                variaciones.append({"symbol": simbolo, "daily_variation": None})
        else:
            variaciones.append({"symbol": simbolo, "daily_variation": None})

    return {"daily_variations": variaciones}

@router.get("/weekly")
def endpoint_weekly():
    """
    Endpoint para obtener variaciones semanales de los activos.
    """
    activos = ["GC=F", "SI=F", "BTC-USD", "ZW=F", "CL=F"]
    variaciones = []

    for simbolo in activos:
        precio_actual = obtener_precio_actual(simbolo)
        if precio_actual:
            fecha_hace_una_semana = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
            precio_semana_pasada = obtener_precio_por_fecha(simbolo, fecha_hace_una_semana)
            if precio_semana_pasada:
                variacion = ((precio_actual - precio_semana_pasada) / precio_semana_pasada) * 100
                variaciones.append({"symbol": simbolo, "weekly_variation": variacion})
            else:
                variaciones.append({"symbol": simbolo, "weekly_variation": None})
        else:
            variaciones.append({"symbol": simbolo, "weekly_variation": None})

    return {"weekly_variations": variaciones}

@router.get("/alerts")
def endpoint_alerts():
    """
    Endpoint para obtener alertas recientes (últimas 24 horas).
    """
    alertas = obtener_alertas_recientes()
    if not alertas:
        return {"alerts": [], "message": "No se han registrado alertas en las últimas 24 horas."}

    formatted_alerts = [{"symbol": alerta[0], "date": alerta[1], "message": alerta[2]} for alerta in alertas]
    return {"alerts": formatted_alerts}

