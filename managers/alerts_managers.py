from db.database import get_connection
from datetime import datetime, timedelta
from managers.assets_manager import obtener_precio_reciente, obtener_precio_por_fecha

# Insertar una alerta en la base de datos
def insertar_alerta(mensaje):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO alertas (mensaje, fecha)
        VALUES (?, ?)
    ''', (mensaje, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    conn.commit()
    conn.close()

# Generar alertas basadas en variaciones significativas de precios
def generar_alertas():
    activos = ["GC=F", "SI=F", "BTC-USD", "ZW=F", "CL=F"]  # Oro, Plata, Bitcoin, Trigo, Petróleo
    for simbolo in activos:
        precio_actual = obtener_precio_reciente(simbolo)
        if precio_actual:
            fecha_ayer = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
            precio_ayer = obtener_precio_por_fecha(simbolo, fecha_ayer)

            if precio_ayer:
                variacion_diaria = ((precio_actual[0] - precio_ayer) / precio_ayer) * 100
                if abs(variacion_diaria) > 5:  # Umbral de variación significativa diaria
                    mensaje = f"{simbolo}: Variación diaria significativa del {variacion_diaria:.2f}% respecto a ayer."
                    insertar_alerta(mensaje)

            fecha_semana_pasada = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
            precio_semana_pasada = obtener_precio_por_fecha(simbolo, fecha_semana_pasada)

            if precio_semana_pasada:
                variacion_semanal = ((precio_actual[0] - precio_semana_pasada) / precio_semana_pasada) * 100
                if abs(variacion_semanal) > 10:  # Umbral de variación significativa semanal
                    mensaje = f"{simbolo}: Variación semanal significativa del {variacion_semanal:.2f}%."
                    insertar_alerta(mensaje)

# Generar alertas diarias y semanales en un único flujo
def generar_alertas_diarias_y_semanales():
    print("[INFO] Generando alertas...")
    generar_alertas()
    print("[INFO] Alertas generadas correctamente.")
