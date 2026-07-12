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
├── .gitignore
├── .env                  # tus claves reales (NO se sube, está en .gitignore)
├── requirements.txt
├── my_models.py           # constantes con los nombres de modelos
├── my_keys.py             # lee las claves desde .env
├── my_helper.py           # funciones de apoyo generales
├── herramienta_extraer_cartera.py   # PDF -> DataFrames / CSV / JSON
├── herramienta_estadisticas.py      # totales y resúmenes
├── herramienta_consultas.py         # búsqueda de clientes y filtros de mora
├── herramienta_alertas.py           # niveles de riesgo
├── orquestador.py          # arma el agente con las tools
├── main.py                 # punto de entrada (chat en terminal)
├── datos/                  # PDFs de cartera a procesar
└── salida/                 # CSV/JSON generados (no se sube, ver .gitignore)
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