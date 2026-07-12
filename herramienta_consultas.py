"""
Herramienta de consultas: búsqueda de clientes y filtros por mora,
pensada para que el agente pueda responder preguntas puntuales
sobre la cartera.
"""

import pandas as pd


def buscar_cliente(df_clientes: pd.DataFrame, df_detalles: pd.DataFrame, texto: str) -> dict:
    """
    Busca un cliente por NIT o por (parte del) nombre, sin distinguir
    mayúsculas/minúsculas ni tildes exactas.
    """
    texto = texto.strip().lower()
    coincidencias = df_clientes[
        df_clientes["nit"].astype(str).str.lower().str.contains(texto)
        | df_clientes["cliente"].str.lower().str.contains(texto)
    ]

    if coincidencias.empty:
        return {"encontrado": False, "mensaje": f"No se encontró ningún cliente que coincida con '{texto}'."}

    resultado = []
    for _, fila in coincidencias.iterrows():
        documentos = df_detalles[df_detalles["nit"] == fila["nit"]][
            ["documento", "fecha", "vence", "edad", "saldo"]
        ].to_dict(orient="records")
        resultado.append({
            "nit": fila["nit"],
            "cliente": fila["cliente"],
            "saldo_total": float(fila["saldo"]),
            "documentos": documentos,
        })

    return {"encontrado": True, "clientes": resultado}


def clientes_por_rango_mora(df_clientes: pd.DataFrame, columna_rango: str, minimo: float = 1) -> list:
    """
    Devuelve los clientes que tienen saldo mayor o igual a `minimo`
    en un rango de mora específico (ej: 'd90_120', 'mas_180').
    """
    if columna_rango not in df_clientes.columns:
        raise ValueError(f"Rango inválido: {columna_rango}")

    filtrados = df_clientes[df_clientes[columna_rango] >= minimo]
    return filtrados[["nit", "cliente", columna_rango, "saldo"]].to_dict(orient="records")


def clientes_en_mora_mayor_a(df_detalles: pd.DataFrame, dias: int) -> list:
    """
    Devuelve los documentos individuales cuya 'edad' (días de mora)
    supera el umbral dado, agrupados por cliente.
    """
    vencidos = df_detalles[df_detalles["edad"] > dias]
    if vencidos.empty:
        return []
    return (
        vencidos.groupby(["nit", "cliente"])
        .agg(documentos_vencidos=("documento", "count"), saldo_vencido=("saldo", "sum"))
        .reset_index()
        .sort_values("saldo_vencido", ascending=False)
        .to_dict(orient="records")
    )

"""

Para verificar que funciona correctamente, se puede ejecutar el siguiente comando en la terminal:

python -c "from herramienta_extraer_cartera import extraer_cartera; 
from herramienta_consultas import buscar_cliente, clientes_por_rango_mora; 
df_c, df_d = extraer_cartera('datos/reporte_cartera_erp_v2.pdf'); 
print('--- Búsqueda que SÍ existe ---'); print(buscar_cliente(df_c, df_d, 'cardona')); 
print(); print('--- Búsqueda que NO existe (caso borde) ---'); 
print(buscar_cliente(df_c, df_d, '999999999')); print(); 
print('--- Clientes con saldo en 90-120 días ---'); print(clientes_por_rango_mora(df_c, 'd90_120'))"
"""