# 2_cargar_ventas_limpio.py
# Cervecería Pipeline — ETL con limpieza de datos
# Extrae de Google Sheets → limpia → carga en SQLite

import sqlite3
import gspread
import re
from datetime import datetime
from google.oauth2.service_account import Credentials

# ─── CONFIGURACIÓN ────────────────────────────────────────────────────────────
ARCHIVO_CREDENCIALES = "credenciales.json"
NOMBRE_HOJA          = "Ventas Cervecería"
BASE_DE_DATOS        = "cerveceria.db"
# ──────────────────────────────────────────────────────────────────────────────

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# ─── FUNCIONES DE LIMPIEZA ────────────────────────────────────────────────────

def limpiar_fecha(valor):
    """Convierte cualquier formato de fecha a YYYY-MM-DD"""
    valor = str(valor).strip()
    formatos = [
        "%Y-%m-%d",   # 2026-05-01
        "%d/%m/%Y",   # 01/05/2026
        "%d-%m-%Y",   # 01-05-2026
        "%Y/%m/%d",   # 2026/05/01
    ]
    for fmt in formatos:
        try:
            return datetime.strptime(valor, fmt).strftime("%Y-%m-%d")
        except:
            continue
    return None  # fecha inválida

def limpiar_texto(valor):
    """Elimina espacios extra y convierte a Title Case"""
    if not valor:
        return None
    return str(valor).strip().title()

def limpiar_canal(valor):
    """Normaliza el canal de venta"""
    if not valor:
        return None
    canales = {
        "bar":          "Bar",
        "tienda":       "Tienda",
        "distribución": "Distribución",
        "distribucion": "Distribución",
    }
    return canales.get(str(valor).strip().lower(), str(valor).strip().title())

def limpiar_numero(valor):
    """Convierte texto con símbolos o comas a número"""
    if valor is None or valor == "":
        return None
    valor = str(valor).strip()
    valor = valor.replace("$", "").replace(" ", "")
    
    # detectar si la coma es decimal (ej: 4,80) o separador de miles (ej: 1,200)
    if re.search(r",\d{1,2}$", valor):
        # coma al final con 1 o 2 dígitos = separador decimal
        valor = valor.replace(".", "").replace(",", ".")
    else:
        # coma como separador de miles
        valor = valor.replace(",", "")
    
    # eliminar letras y unidades como "lt"
    valor = re.sub(r"[a-zA-ZáéíóúÁÉÍÓÚ]+", "", valor).strip()
    
    try:
        return float(valor)
    except:
        return None

# ─── CONECTAR CON GOOGLE SHEETS ───────────────────────────────────────────────
print("Conectando con Google Sheets...")
credenciales = Credentials.from_service_account_file(
    ARCHIVO_CREDENCIALES, scopes=SCOPES
)
cliente = gspread.authorize(credenciales)
hoja    = cliente.open(NOMBRE_HOJA).sheet1
print("✓ Conexión exitosa\n")

# ─── EXTRAER ──────────────────────────────────────────────────────────────────
print("Extrayendo datos...")
registros_raw = hoja.get_all_values()
encabezados   = registros_raw[0]
registros     = [dict(zip(encabezados, fila)) for fila in registros_raw[1:]]
print(f"✓ {len(registros)} registros extraídos\n")

# ─── TRANSFORMAR Y LIMPIAR ────────────────────────────────────────────────────
print("Limpiando datos...")
ahora     = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
filas_ok  = []
filas_err = []

for i, r in enumerate(registros, start=2):
    errores = []

    fecha    = limpiar_fecha(r.get("fecha", ""))
    producto = limpiar_texto(r.get("producto", ""))
    categoria= limpiar_texto(r.get("categoria", ""))
    cantidad = limpiar_numero(r.get("cantidad_litros", ""))
    precio   = limpiar_numero(r.get("precio_unitario", ""))
    canal    = limpiar_canal(r.get("canal", ""))

    # validar campos obligatorios
    if not fecha:
        errores.append("fecha inválida")
    if not producto:
        errores.append("producto vacío")
    if cantidad is None:
        errores.append(f"cantidad inválida: '{r.get('cantidad_litros')}'")
    if precio is None:
        errores.append(f"precio inválido: '{r.get('precio_unitario')}'")
    if not canal:
        errores.append("canal vacío")

    if errores:
        filas_err.append(f"Fila {i}: {' | '.join(errores)}")
        continue

    total = round(cantidad * precio, 2)
    filas_ok.append((
        fecha, producto, categoria,
        cantidad, precio, total,
        canal, ahora
    ))

# ─── MOSTRAR REPORTE DE LIMPIEZA ──────────────────────────────────────────────
print(f"✓ Filas limpias:    {len(filas_ok)}")
print(f"⚠ Filas con error: {len(filas_err)}")

if filas_err:
    print("\nRegistros descartados:")
    for err in filas_err:
        print(f"  {err}")

# ─── CARGAR EN SQLITE ─────────────────────────────────────────────────────────
print("\nCargando en la base de datos...")
conexion = sqlite3.connect(BASE_DE_DATOS)
cursor   = conexion.cursor()

cursor.execute("DELETE FROM ventas")
cursor.executemany("""
    INSERT INTO ventas
        (fecha, producto, categoria, cantidad_litros,
         precio_unitario, total_venta, canal, registrado_en)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
""", filas_ok)

conexion.commit()

# ─── RESUMEN FINAL ────────────────────────────────────────────────────────────
cursor.execute("""
    SELECT producto, SUM(cantidad_litros) as litros, SUM(total_venta) as ingresos
    FROM ventas
    GROUP BY producto
    ORDER BY litros DESC
""")
resumen = cursor.fetchall()
conexion.close()

print(f"✓ {len(filas_ok)} registros cargados\n")
print(f"{'PRODUCTO':<20} {'LITROS':>10} {'INGRESOS':>12}")
print("-" * 45)
for fila in resumen:
    print(f"{fila[0]:<20} {fila[1]:>10.1f} ${fila[2]:>11.2f}")

print(f"\n✓ ETL completado: {ahora}")