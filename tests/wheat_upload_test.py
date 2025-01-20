import yfinance as yf
trigo = yf.Ticker("ZW=F")
print(trigo.history(period="1d"))  # Verifica si devuelve datos
