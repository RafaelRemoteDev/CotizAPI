from db.database import get_connection
from datetime import datetime
from services.yahoo_finance import obtener_precio_actual

# Insertar un precio en la base de datos
def insertar_precio(simbolo, precio, fecha):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO activos (simbolo, fecha, precio)
        VALUES (?, ?, ?)
    ''', (simbolo.upper(), fecha, precio))
    conn.commit()
    conn.close()

# Obtener el precio más reciente de un activo
def obtener_precio_reciente(simbolo):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT precio, fecha FROM activos
        WHERE simbolo = ?
        ORDER BY fecha DESC LIMIT 1
    ''', (simbolo.upper(),))
    resultado = cursor.fetchone()
    conn.close()
    return resultado  # Devuelve una tupla (precio, fecha)

# Obtener el precio de un activo por una fecha específica
def obtener_precio_por_fecha(simbolo, fecha):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT precio FROM activos
        WHERE simbolo = ? AND fecha = ?
    ''', (simbolo.upper(), fecha))
    resultado = cursor.fetchone()
    conn.close()
    return resultado[0] if resultado else None

# Actualizar el precio de un activo en la base de datos
def actualizar_precio_en_bd(simbolo):
    precio = obtener_precio_actual(simbolo)  # Llama al servicio de Yahoo Finance
    if precio:
        fecha = datetime.now().strftime('%Y-%m-%d')
        insertar_precio(simbolo, precio, fecha)  # Usa la función insertar_precio
        return precio
    else:
        print(f"No se pudo obtener el precio para {simbolo}.")
        return None

# Obtener precios externos sin insertarlos (fetch de datos externos)
def fetch_external_prices():
    """
    Obtiene precios de activos desde una fuente externa (como Yahoo Finance).
    Devuelve un diccionario con los símbolos como claves y los precios como valores.
    """
    activos = ["GC=F", "SI=F", "BTC-USD", "ZW=F", "CL=F"]  # Oro, Plata, Bitcoin, Trigo, Petróleo
    precios = {}
    for simbolo in activos:
        precio = obtener_precio_actual(simbolo)
        if precio:
            precios[simbolo] = precio
        else:
            print(f"Error al obtener precio para {simbolo}")
            precios[simbolo] = None
    return precios  # Devuelve un diccionario con los precios obtenidos

# Actualizar todos los precios de los activos en la base de datos
def actualizar_todos_los_precios():
    activos = ["GC=F", "SI=F", "BTC-USD", "ZW=F", "CL=F"]  # Oro, Plata, Bitcoin, Trigo, Petróleo
    precios_actualizados = {}
    for simbolo in activos:
        precio = actualizar_precio_en_bd(simbolo)
        if precio:
            precios_actualizados[simbolo] = precio
            print(f"Actualizado: {simbolo} - Precio: {precio}")
        else:
            print(f"Error al actualizar {simbolo}.")
    return precios_actualizados  # Devuelve un diccionario con los precios actualizados
