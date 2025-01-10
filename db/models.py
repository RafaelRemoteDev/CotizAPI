import sqlite3

# Conexión global
conn = sqlite3.connect("cotizapi.db")
cursor = conn.cursor()

# Modelo de Activos
def create_tables():
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS activos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            simbolo TEXT NOT NULL,
            fecha TEXT NOT NULL,
            precio REAL NOT NULL
        )
    ''')
    conn.commit()

