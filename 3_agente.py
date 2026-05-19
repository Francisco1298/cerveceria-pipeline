# 3_agente.py
# Cervecería Pipeline — Paso 3: Agente de IA
# Responde preguntas sobre ventas en lenguaje natural usando SQL

import json
import sqlite3
import os
from groq import Groq
from dotenv import load_dotenv
from datetime import datetime

# ─── CONFIGURACIÓN ────────────────────────────────────────────────────────────
load_dotenv()
API_KEY       = os.getenv("GROQ_API_KEY")
BASE_DE_DATOS = "cerveceria.db"
# ──────────────────────────────────────────────────────────────────────────────

# ─── HERRAMIENTA: ejecutar SQL ─────────────────────────────────────────────────
def ejecutar_sql(consulta):
    """Ejecuta una consulta SQL y devuelve los resultados como texto"""
    try:
        conexion  = sqlite3.connect(BASE_DE_DATOS)
        cursor    = conexion.cursor()
        cursor.execute(consulta)
        resultados = cursor.fetchall()
        columnas   = [desc[0] for desc in cursor.description]
        conexion.close()

        if not resultados:
            return "No se encontraron resultados para esta consulta."

        lineas = []
        for fila in resultados:
            linea = " | ".join(f"{columnas[i]}: {fila[i]}" for i in range(len(fila)))
            lineas.append(linea)
        return "\n".join(lineas)

    except Exception as e:
        return f"Error en la consulta SQL: {str(e)}"

# ─── HERRAMIENTA: resumen general ─────────────────────────────────────────────
def resumen_general():
    """Devuelve un resumen rápido de las ventas totales"""
    try:
        conexion = sqlite3.connect(BASE_DE_DATOS)
        cursor   = conexion.cursor()

        cursor.execute("SELECT COUNT(*) FROM ventas")
        total_registros = cursor.fetchone()[0]

        cursor.execute("SELECT SUM(total_venta) FROM ventas")
        ingresos = cursor.fetchone()[0] or 0

        cursor.execute("SELECT SUM(cantidad_litros) FROM ventas")
        litros = cursor.fetchone()[0] or 0

        cursor.execute("SELECT MIN(fecha), MAX(fecha) FROM ventas")
        fechas = cursor.fetchone()

        conexion.close()
        return (
            f"Total registros: {total_registros} | "
            f"Ingresos totales: ${ingresos:.2f} | "
            f"Litros totales: {litros:.1f} | "
            f"Período: {fechas[0]} al {fechas[1]}"
        )
    except Exception as e:
        return f"Error: {str(e)}"

# ─── DEFINICIÓN DE HERRAMIENTAS PARA EL MODELO ────────────────────────────────
herramientas = [
    {
        "type": "function",
        "function": {
            "name": "ejecutar_sql",
            "description": """Ejecuta consultas SQL sobre la base de datos de ventas de la cervecería.
            La tabla principal se llama 'ventas' con estas columnas:
            - id: número único
            - fecha: fecha de la venta (TEXT, formato YYYY-MM-DD)
            - producto: nombre de la cerveza (TEXT) ej: 'IPA Tropical', 'Lager Dorada'
            - categoria: tipo de cerveza (TEXT) ej: 'IPA', 'Lager', 'Stout'
            - cantidad_litros: litros vendidos (REAL)
            - precio_unitario: precio por litro (REAL)
            - total_venta: ingresos de esa venta (REAL)
            - canal: donde se vendió (TEXT) ej: 'Bar', 'Tienda', 'Distribución'
            Solo usa SELECT. Nunca uses INSERT, UPDATE ni DELETE.""",
            "parameters": {
                "type": "object",
                "properties": {
                    "consulta": {
                        "type": "string",
                        "description": "La consulta SQL a ejecutar"
                    }
                },
                "required": ["consulta"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "resumen_general",
            "description": "Devuelve un resumen rápido con totales generales de ventas",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    }
]

# ─── EJECUTAR HERRAMIENTA ──────────────────────────────────────────────────────
def ejecutar_herramienta(nombre, argumentos):
    if nombre == "ejecutar_sql":
        return ejecutar_sql(argumentos["consulta"])
    elif nombre == "resumen_general":
        return resumen_general()
    return "Herramienta no encontrada"

# ─── AGENTE PRINCIPAL ──────────────────────────────────────────────────────────
cliente = Groq(api_key=API_KEY)

messages = [
    {
        "role": "system",
        "content": f"""Eres el asistente de análisis de ventas de una cervecería artesanal.
            La fecha actual es {datetime.now().strftime('%Y-%m-%d')}.
            El mes actual es {datetime.now().strftime('%Y-%m')}.
            Tienes acceso a una base de datos SQLite con la tabla 'ventas'.

            COLUMNAS DISPONIBLES:
            - fecha (TEXT, formato YYYY-MM-DD)
            - producto (TEXT): 'Ipa Tropical', 'Lager Dorada', 'Stout Oscura', 'Trigo Suave', 'Pale Ale Clásica', 'Porter Robusta'
            - categoria (TEXT): 'Ipa', 'Lager', 'Stout', 'Trigo', 'Pale Ale', 'Porter'
            - cantidad_litros (REAL): litros vendidos
            - precio_unitario (REAL): precio por litro
            - total_venta (REAL): ingresos de esa venta
            - canal (TEXT): 'Bar', 'Tienda', 'Distribución'

            REGLAS PARA GENERAR SQL:
            - Siempre usa SELECT con columnas específicas, nunca SELECT *
            - Para ventas por producto: GROUP BY producto, SUM(cantidad_litros), SUM(total_venta)
            - Para el más vendido: ORDER BY SUM(cantidad_litros) DESC LIMIT 1
            - Para el más rentable: ORDER BY SUM(total_venta) DESC LIMIT 1
            - Para comparar dos productos: WHERE producto IN ('Producto1', 'Producto2')
            - Para canales: GROUP BY canal, SUM(total_venta)
            - Siempre usa la herramienta ejecutar_sql para obtener datos reales

            REGLAS para interpretar resultados:
            - Mayor cantidad_litros = más vendido en volumen
            - Mayor total_venta = más rentable en ingresos
            - Responde en español claro para el dueño del negocio

            Solo usa SELECT. Nunca uses INSERT, UPDATE ni DELETE."""
    }
]

print("=" * 55)
print("  🍺 Asistente de Ventas — Cervecería Artesanal")
print("=" * 55)
print("Ejemplos de preguntas:")
print("  • ¿Cuál fue la cerveza más vendida este mes?")
print("  • ¿Qué canal de venta generó más ingresos?")
print("  • ¿Cuántos litros se vendieron en total?")
print("  • Compara las ventas de IPA vs Stout")
print("  • ¿Cuál es la cerveza más rentable?")
print("  • Dame un resumen general de ventas")
print("  • Escribe 'salir' para terminar")
print("=" * 55)

# ─── BUCLE DE CONVERSACIÓN ────────────────────────────────────────────────────
while True:
    try:
        pregunta = input("\nTú: ").strip()
    except EOFError:
        break

    if pregunta.lower() == "salir":
        print("\nAsistente: ¡Hasta luego! 🍺")
        break

    if not pregunta:
        continue

    # reiniciar historial en cada pregunta — evita errores de Groq
    messages_turno = [messages[0], {"role": "user", "content": pregunta}]

    # primera llamada al modelo
    respuesta = cliente.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages_turno,
        tools=herramientas,
        tool_choice="auto"
    )

    mensaje = respuesta.choices[0].message

    if mensaje.tool_calls:
        messages_turno.append({"role": "assistant", "tool_calls": mensaje.tool_calls})

        for tool_call in mensaje.tool_calls:
            nombre     = tool_call.function.name
            argumentos = json.loads(tool_call.function.arguments)

            if nombre == "ejecutar_sql":
                print(f"\n  [SQL] {argumentos.get('consulta', '')}")

            resultado = ejecutar_herramienta(nombre, argumentos)

            messages_turno.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": resultado
            })

        respuesta_final = cliente.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages_turno,
            tools=herramientas
        )
        respuesta_texto = respuesta_final.choices[0].message.content
        if not respuesta_texto:
            respuesta_texto = "No encontré datos para responder esa pregunta."

    else:
        respuesta_texto = mensaje.content
        if not respuesta_texto:
            respuesta_texto = "No encontré datos para responder esa pregunta."

    print(f"\nAsistente: {respuesta_texto}")