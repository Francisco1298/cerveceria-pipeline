# 1_crear_base_de_datos.py
# Cervecería Pipeline — Paso 1: Crear la base de datos
# Ejecutar UNA SOLA VEZ para inicializar el sistema

import sqlite3

BASE_DE_DATOS = "cerveceria.db"

conexion = sqlite3.connect(BASE_DE_DATOS)
cursor = conexion.cursor()

# Tabla de ventas
cursor.execute("""
    CREATE TABLE IF NOT EXISTS ventas (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha           TEXT NOT NULL,
        producto        TEXT NOT NULL,
        categoria       TEXT NOT NULL,
        cantidad_litros REAL NOT NULL,
        precio_unitario REAL NOT NULL,
        total_venta     REAL NOT NULL,
        canal           TEXT NOT NULL,
        registrado_en   TEXT NOT NULL
    )
""")

# Tabla de productos
cursor.execute("""
    CREATE TABLE IF NOT EXISTS productos (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre      TEXT NOT NULL UNIQUE,
        categoria   TEXT NOT NULL,
        precio      REAL NOT NULL,
        activo      INTEGER DEFAULT 1
    )
""")

# Insertar productos de ejemplo de la cervecería
productos = [
    ("Lager Dorada",     "Lager",   3.50, 1),
    ("IPA Tropical",     "IPA",     4.20, 1),
    ("Stout Oscura",     "Stout",   4.80, 1),
    ("Trigo Suave",      "Trigo",   3.80, 1),
    ("Pale Ale Clásica", "Pale Ale",3.90, 1),
    ("Porter Robusta",   "Porter",  4.50, 1),
]

cursor.executemany("""
    INSERT OR IGNORE INTO productos (nombre, categoria, precio, activo)
    VALUES (?, ?, ?, ?)
""", productos)

conexion.commit()
conexion.close()

print("✓ Base de datos creada: cerveceria.db")
print("✓ Tabla 'ventas' lista")
print("✓ Tabla 'productos' lista")
print(f"✓ {len(productos)} productos registrados")
print("\nSiguiente paso: ejecuta 2_cargar_ventas.py")
