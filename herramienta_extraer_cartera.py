"""
Herramienta de extracción: convierte el reporte de cartera en PDF
(formato ERP, tipo "reporte_cartera_erp_v2.pdf") en datos estructurados.

Genera dos tablas:
  - clientes: un renglón por cliente con sus totales por rango de mora.
  - detalles: un renglón por documento/factura, ligado al NIT del cliente.

El formato del reporte es de ancho fijo pero pdfplumber a veces pega el
NIT con el nombre del cliente (ej: "1000085253GUISAO ESCOBAR"), por eso
se hace un pequeño arreglo de espacios antes de aplicar las expresiones
regulares.

"""

import re
import json
import pdfplumber
import pandas as pd

from my_helper import limpiar_numero

# --- Patrones de las dos clases de renglón del reporte -----------------

NUM = r"(-?[\d,]+)"

# TR  DOCUMENTO  FECHA  VENCE  EDAD  DOC_REF  AL_DIA 0A30 30A60 60A90 90A120 >180 SALDO
DETALLE_RE = re.compile(
    r"^(\d{2})\s+(\d+)\s+(\d{2}-\d{2}-\d{2})\s+(\d{2}-\d{2}-\d{2})\s+(\d+)\s+"
    r"(SALDO A FAV|\d+)\s+" + r"\s+".join([NUM] * 7) + r"\s*$"
)

# NIT  NOMBRE...  AL_DIA 0A30 30A60 60A90 90A120 >180 SALDO  (fila de totales del cliente)
CLIENTE_RE = re.compile(
    r"^(\d{6,12})\s+(.+?)\s+" + r"\s+".join([NUM] * 7) + r"\s*$"
)

COLUMNAS_RANGO = ["al_dia", "d0_30", "d30_60", "d60_90", "d90_120", "mas_180", "saldo"]


def _extraer_texto(pdf_path: str) -> str:
    partes = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            partes.append(page.extract_text() or "")
    texto = "\n".join(partes)
    # Arregla el pegado NIT+NOMBRE que a veces produce pdfplumber
    texto = re.sub(r"(\d)([A-ZÁÉÍÓÚÑ])", r"\1 \2", texto)
    return texto


def extraer_cartera(pdf_path: str):
    """
    Parsea el PDF y devuelve (df_clientes, df_detalles) como DataFrames
    de pandas, con las columnas de saldo ya convertidas a números.
    """
    texto = _extraer_texto(pdf_path)

    clientes = []
    detalles = []
    nit_actual = None
    nombre_actual = None

    for linea in texto.split("\n"):
        linea = linea.strip()
        if not linea or linea.startswith("PERIODO") or linea.startswith("TR ") or linea.startswith("Página"):
            continue

        m = DETALLE_RE.match(linea)
        if m:
            detalles.append({
                "nit": nit_actual,
                "cliente": nombre_actual,
                "tr": m.group(1),
                "documento": m.group(2),
                "fecha": m.group(3),
                "vence": m.group(4),
                "edad": int(m.group(5)),
                "doc_ref": m.group(6),
                "al_dia": limpiar_numero(m.group(7)),
                "d0_30": limpiar_numero(m.group(8)),
                "d30_60": limpiar_numero(m.group(9)),
                "d60_90": limpiar_numero(m.group(10)),
                "d90_120": limpiar_numero(m.group(11)),
                "mas_180": limpiar_numero(m.group(12)),
                "saldo": limpiar_numero(m.group(13)),
            })
            continue

        m = CLIENTE_RE.match(linea)
        if m:
            nit_actual = m.group(1)
            nombre_actual = m.group(2).strip()
            clientes.append({
                "nit": nit_actual,
                "cliente": nombre_actual,
                "al_dia": limpiar_numero(m.group(3)),
                "d0_30": limpiar_numero(m.group(4)),
                "d30_60": limpiar_numero(m.group(5)),
                "d60_90": limpiar_numero(m.group(6)),
                "d90_120": limpiar_numero(m.group(7)),
                "mas_180": limpiar_numero(m.group(8)),
                "saldo": limpiar_numero(m.group(9)),
            })
            continue

        # Si una línea no calza con ningún patrón, se ignora en silencio
        # (encabezados repetidos, líneas en blanco, pies de página, etc.)

    df_clientes = pd.DataFrame(clientes)
    df_detalles = pd.DataFrame(detalles)
    return df_clientes, df_detalles


def guardar_como_csv_json(df_clientes: pd.DataFrame, df_detalles: pd.DataFrame, carpeta_salida: str = "salida"):
    df_clientes.to_csv(f"{carpeta_salida}/clientes.csv", index=False)
    df_detalles.to_csv(f"{carpeta_salida}/detalles.csv", index=False)
    with open(f"{carpeta_salida}/clientes.json", "w", encoding="utf-8") as f:
        json.dump(df_clientes.to_dict(orient="records"), f, ensure_ascii=False, indent=2)
    with open(f"{carpeta_salida}/detalles.json", "w", encoding="utf-8") as f:
        json.dump(df_detalles.to_dict(orient="records"), f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    import sys

    ruta = sys.argv[1] if len(sys.argv) > 1 else "datos/reporte_cartera_erp_v2.pdf"
    df_clientes, df_detalles = extraer_cartera(ruta)
    guardar_como_csv_json(df_clientes, df_detalles)
    print(f"Clientes: {len(df_clientes)} | Documentos: {len(df_detalles)}")
    print(f"Archivos guardados en salida/")
