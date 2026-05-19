# 🍺 Pipeline de Ventas — Cervecería Artesanal

Sistema de automatización completo que extrae ventas desde Google Sheets,
las almacena en una base de datos SQLite y permite consultarlas mediante
un agente de inteligencia artificial en lenguaje natural.

---

## ¿Qué problema resuelve?

Antes: el dueño revisaba manualmente las ventas en Excel al final del mes.
Después: un agente responde cualquier pregunta sobre ventas en segundos,
con datos actualizados automáticamente.

---

## Arquitectura del pipeline

```
Google Sheets (ventas del mes)
        ↓  [2_cargar_ventas.py]
SQLite (cerveceria.db)
        ↓  [3_agente.py]
Agente IA responde preguntas
        ↑
Make lo ejecuta automáticamente cada día
        ↑
Flask (4_app.py) expone el endpoint
```

---

## Archivos

| Archivo | Descripción |
|---|---|
| `1_crear_base_de_datos.py` | Inicializa la BD — ejecutar una sola vez |
| `2_cargar_ventas.py` | ETL: Google Sheets → SQLite |
| `3_agente.py` | Agente IA para consultar ventas |
| `4_app.py` | API Flask para automatización con Make |
| `.env.example` | Plantilla de variables de entorno |

---

## Instalación

**1. Clonar el repositorio:**
```bash
git clone https://github.com/TU_USUARIO/cerveceria-pipeline.git
cd cerveceria-pipeline
```

**2. Instalar dependencias:**
```bash
pip install requests gspread google-auth flask groq python-dotenv
```

**3. Configurar credenciales:**
```bash
cp .env.example .env
# Editar .env con tus API keys
```

**4. Agregar credenciales de Google Cloud:**
- Descarga el archivo JSON de tu cuenta de servicio
- Renómbralo a `credenciales.json`
- Comparte tu Google Sheet con el email de la cuenta de servicio

**5. Configurar Google Sheets:**
Tu hoja debe tener estos encabezados en la fila 1:
```
fecha | producto | categoria | cantidad_litros | precio_unitario | canal
```

**6. Ejecutar el sistema:**
```bash
# Solo la primera vez
python 1_crear_base_de_datos.py

# Cargar ventas desde Google Sheets
python 2_cargar_ventas.py

# Iniciar el agente
python 3_agente.py
```

---

## Ejemplo de uso del agente

```
Tú: ¿Cuál fue la cerveza más vendida este mes?
Asistente: La IPA Tropical lideró con 340 litros vendidos,
           representando el 28% del volumen total.

Tú: ¿Qué canal generó más ingresos?
Asistente: El canal Bar generó $1,240 en ingresos, seguido
           por Distribución con $890.

Tú: Compara IPA vs Stout
Asistente: IPA Tropical: 340L / $1,428 | Stout Oscura: 210L / $1,008.
           La IPA lidera en volumen pero la Stout tiene mejor
           precio unitario.

Tú: ¿Cuál es la cerveza más rentable?
Asistente: La Stout Oscura tiene el mayor ingreso por litro
           con $4.80, seguida por la Porter Robusta con $4.50.
```

---

## Automatización con Make

1. Subir `2_cargar_ventas.py` y `4_app.py` a PythonAnywhere
2. Configurar la web app apuntando a `4_app.py`
3. En Make: Schedule → HTTP GET → tu URL:
```
https://TU_USUARIO.pythonanywhere.com/ejecutar/cerveceria-clave-2026
```

---

## Stack tecnológico

- **Python 3.12** — lenguaje principal
- **gspread** — extracción desde Google Sheets
- **sqlite3** — base de datos local
- **Flask** — endpoint para automatización
- **Groq + LLaMA 3.3** — agente de IA con function calling
- **Make** — automatización del flujo mensual
- **PythonAnywhere** — deploy en la nube
- **Git + GitHub** — control de versiones

---

## Conceptos aplicados

- ETL (Extract, Transform, Load)
- SQL: SELECT, INSERT, GROUP BY, ORDER BY, SUM
- Agentes de IA con function calling
- Prompt engineering
- Deploy en la nube
- Automatización con iPaaS
- Variables de entorno y seguridad
