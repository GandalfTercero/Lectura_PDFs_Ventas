# Agente de Cartera (LangChain + Gemini)

Agente conversacional que lee un reporte de cartera en PDF (formato ERP, ej. `reporte_cartera_erp_v2.pdf`) y responde preguntas en lenguaje natural sobre saldos, moras y alertas de riesgo.

## ¿Qué hace?

1. **Extrae** los datos del PDF (cliente, documentos, fechas, edad de mora, saldos por rango) y los estructura en tablas (`herramienta_extraer_cartera.py`).
2. **Calcula** estadísticas: saldo total, totales por rango de mora, top de clientes (`herramienta_estadisticas.py`).
3. **Consulta** clientes puntuales por nombre o NIT, y filtra por días de mora (`herramienta_consultas.py`).
4. **Genera alertas** clasificando cada cliente en un nivel de riesgo: CRÍTICO / ALTO / MEDIO / BAJO (`herramienta_alertas.py`).
5. Expone todo lo anterior como **tools de LangChain** que un agente con Gemini usa para responder tus preguntas (`orquestador.py`, `main.py`).

## Estructura del proyecto

```
cartera-agente-langchain/
├── .gitignore            # (paso 1)
├── .venv/                # (paso 2, gris/ignorado)
├── .env                  # tus claves reales (paso 3. NO se sube, está en .gitignore)
├── requirements.txt      # (paso 4)
├── my_models.py           # constantes con los nombres de modelos (paso 5)
├── my_keys.py             # lee las claves desde .env (paso 5)
├── my_helper.py           # funciones de apoyo generales (paso 5)
├── datos/                  # PDFs de cartera a procesar (paso 5)
└── salida/                 # CSV/JSON generados (paso 5. No se sube, ver .gitignore)
├── herramienta_extraer_cartera.py   # PDF -> DataFrames / CSV / JSON (paso 6)
└── __pycache__/             (aparece solo, gris/ignorado, al correr cualquier .py)
├── herramienta_estadisticas.py      # totales y resúmenes (paso 6)
├── herramienta_consultas.py         # búsqueda de clientes y filtros de mora (paso 6)
├── herramienta_alertas.py           # niveles de riesgo (paso 6)
├── orquestador.py          # arma el agente con las tools (paso 7)
├── main.py                 # punto de entrada (chat en terminal) (paso 7)

```

## Instalación

```bash
# 1. Clona el repo y entra a la carpeta
git clone https://github.com/tu_usuario/cartera-agente-langchain.git
cd cartera-agente-langchain

# 2. Crea y activa el entorno virtual
python -m venv .venv
# Windows: .\.venv\Scripts\activate
# Mac/Linux: source .venv/bin/activate

# 3. Instala dependencias
pip install -r requirements.txt

# 4. Crea tu .env a partir de la plantilla y pon tus claves reales
cp .env.example .env
# Edita .env y coloca tu GEMINI_API_KEY (Google AI Studio)
```

## Uso

Coloca tu PDF de cartera en `datos/` (ya incluye uno de ejemplo) y ejecuta:

```bash
python main.py datos/reporte_cartera_erp_v2.pdf
```

Esto abre un chat en la terminal. Ejemplos de preguntas:

- "Dame un resumen general de la cartera"
- "¿Quién tiene el saldo más alto?"
- "¿Qué clientes tienen documentos vencidos hace más de 90 días?"
- "Dame las alertas de riesgo crítico"
- "Busca al cliente Cardona"

Escribe `salir` para terminar.

### Solo extraer los datos (sin el agente)

Si únicamente quieres los datos estructurados en CSV/JSON:

```bash
python herramienta_extraer_cartera.py datos/reporte_cartera_erp_v2.pdf
```

Esto genera `salida/clientes.csv`, `salida/detalles.csv` y sus equivalentes `.json`.

## Notas sobre el formato del PDF

El parser (`herramienta_extraer_cartera.py`) está hecho a la medida del layout de este reporte ERP:

- Una fila de **totales por cliente**: `NIT  NOMBRE  AL_DIA  0A30  30A60  60A90  90A120  >180  SALDO`
- Varias filas de **detalle por documento** debajo de cada cliente: `TR  DOCUMENTO  FECHA  VENCE  EDAD  DOC_REF  AL_DIA  0A30  30A60  60A90  90A120  >180  SALDO`

Si cambias de proveedor de ERP o el formato del reporte varía, ajusta las expresiones regulares `DETALLE_RE` y `CLIENTE_RE` en `herramienta_extraer_cartera.py`.

## Subir cambios a GitHub

```bash
git add .
git commit -m "mensaje descriptivo"
git push
```

Gracias al `.gitignore`, `.venv/`, `.env` y los CSV/JSON generados en `salida/` nunca se suben por accidente.

## Página y URL
En la siguiente imagen encontrarás el perfil de la página.
(Esta herramienta se hizo principalmente con el archivo base que está en la carpeta Datos).

### URL:
https://lecturapdfsventas-krcfxlnzizgsgeyqfszirl.streamlit.app/

<img width="792" height="350" alt="image" src="https://github.com/user-attachments/assets/727a32f1-2dd3-4105-88ba-80af29780785" />
