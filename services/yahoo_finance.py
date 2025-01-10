import yfinance as yf

def obtener_precio_actual(simbolo):
    try:
        activo = yf.Ticker(simbolo)
        datos = activo.history(period="1d")
        if not datos.empty:
            precio = datos['Close'].iloc[-1]
            return round(precio, 2)
        else:
            return None
    except Exception as e:
        print(f"Error al obtener el precio de {simbolo}: {e}")
        return None
    