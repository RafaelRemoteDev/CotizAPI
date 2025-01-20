import yfinance as yf
from datetime import datetime

def es_fin_de_semana():
    """
    Verifica si el día actual es sábado o domingo.
    :return: True si es fin de semana, False en caso contrario.
    """
    hoy = datetime.now().weekday()  # Lunes=0, Domingo=6
    return hoy >= 5  # Sábado (5) o Domingo (6)

def obtener_precio_actual(simbolo):
    """
    Obtiene el precio actual del activo usando Yahoo Finance.
    Maneja casos en los que el mercado está cerrado durante el fin de semana.

    :param simbolo: El símbolo del activo en Yahoo Finance.
    :return: Precio actual (float) o None si no se encuentra.
    """
    try:
        # Evitar obtener precios de activos tradicionales en fin de semana
        if es_fin_de_semana() and simbolo != "BTC-USD":
            print(f"El mercado está cerrado para {simbolo}.")
            return None

        activo = yf.Ticker(simbolo)
        datos = activo.history(period="1d")

        if not datos.empty:
            precio = datos['Close'].iloc[-1]  # Último precio de cierre
            return round(precio, 2)
        else:
            print(f"No se encontraron datos para {simbolo}.")
            return None
    except Exception as e:
        print(f"Error al obtener el precio de {simbolo}: {e}")
        return None

def actualizar_precios(activos):
    """
    Actualiza los precios de una lista de activos.

    :param activos: Lista de símbolos de activos.
    :return: Diccionario con los resultados de los precios actualizados.
    """
    resultados = {}

    for simbolo in activos:
        print(f"Actualizando precio para {simbolo}...")
        precio = obtener_precio_actual(simbolo)

        if precio is not None:
            resultados[simbolo] = precio
            print(f"{simbolo}: Último precio actualizado: {precio}")
        else:
            print(f"No se pudo actualizar el precio de {simbolo}.")
            resultados[simbolo] = None

    return resultados

# Ejemplo de uso:
if __name__ == "__main__":
    activos = ["GC=F", "SI=F", "BTC-USD", "ZW=F", "CL=F"]
    precios_actualizados = actualizar_precios(activos)
    print("\nResultados finales:")
    for simbolo, precio in precios_actualizados.items():
        print(f"{simbolo}: {precio}")
