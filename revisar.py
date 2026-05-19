# revisar.py
import sqlite3

conexion = sqlite3.connect("cerveceria.db")
cursor = conexion.cursor()

cursor.execute("""
    SELECT fecha, producto, cantidad_litros, precio_unitario, total_venta
    FROM ventas
    WHERE producto IN ('Lager Dorada', 'Stout Oscura')
    ORDER BY producto, fecha
""")

filas = cursor.fetchall()
conexion.close()

print(f"{'FECHA':<12} {'PRODUCTO':<15} {'LITROS':>8} {'PRECIO':>8} {'TOTAL':>10}")
print("-" * 58)
for f in filas:
    print(f"{f[0]:<12} {f[1]:<15} {f[2]:>8.1f} {f[3]:>8.2f} {f[4]:>10.2f}")