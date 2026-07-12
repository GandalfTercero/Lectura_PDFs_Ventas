"""
Herramienta de estadísticas: totales y resúmenes generales de la cartera.
"""

import pandas as pd

from herramienta_extraer_cartera import COLUMNAS_RANGO

RANGOS_LEGIBLES = {
    "al_dia": "Al día",
    "d0_30": "0 a 30 días",
    "d30_60": "30 a 60 días",
    "d60_90": "60 a 90 días",
    "d90_120": "90 a 120 días",
    "mas_180": "Más de 180 días",
}


def totales_por_rango(df_clientes: pd.DataFrame) -> dict:
    """Suma el saldo total de la cartera por cada rango de mora."""
    return {
        RANGOS_LEGIBLES[col]: round(float(df_clientes[col].sum()), 2)
        for col in RANGOS_LEGIBLES
    }


def saldo_total(df_clientes: pd.DataFrame) -> float:
    return round(float(df_clientes["saldo"].sum()), 2)


def top_clientes_por_saldo(df_clientes: pd.DataFrame, n: int = 5) -> list:
    top = df_clientes.sort_values("saldo", ascending=False).head(n)
    return top[["nit", "cliente", "saldo"]].to_dict(orient="records")


def resumen_general(df_clientes: pd.DataFrame) -> dict:
    return {
        "numero_clientes": int(len(df_clientes)),
        "saldo_total_cartera": saldo_total(df_clientes),
        "totales_por_rango": totales_por_rango(df_clientes),
        "top_5_clientes": top_clientes_por_saldo(df_clientes, 5),
    }