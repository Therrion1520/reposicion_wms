"""
core.py – Lógica central de datos para Reposición & Picking PRO
Autor: Eduardo Hernández

Responsabilidades:
- Rutas de archivos (dentro de /data)
- Carga y validación de CSV
- Normalización y merges
- Estructuras base de datos en memoria
- Utilidades de ordenamiento por picking
"""

import os
import sys
import json
from datetime import datetime

import pandas as pd

from utils import data_path, normalizar_texto


# =========================================
#  Rutas de archivos (carpeta /data)
# =========================================

ARCH_STOCK = data_path("stock.csv")
ARCH_ALMACEN = data_path("almacen.csv")
ARCH_PEDIDOS = data_path("TodoslosPedidos.csv")
ARCH_VENTAS = data_path("ventas.csv")

PEND_FILE = data_path("reposicion_pendiente.json")
HIST_FILE = data_path("historico_reposiciones.csv")


# =========================================
#  Carga y validación de datos
# =========================================

# Estos dataframes quedan disponibles para el resto del sistema
stock = None
almacen = None
ventas = None
pedidos = None
df_stock = None
ventas_detalle = None


def _validar_columnas(df: pd.DataFrame, requeridas, nombre_archivo: str):
    faltantes = [c for c in requeridas if c not in df.columns]
    if faltantes:
        raise RuntimeError(
            f"Error en {nombre_archivo}: faltan columnas requeridas: {', '.join(faltantes)}"
        )


def cargar_datos():
    """
    Carga todos los CSV desde /data, normaliza nombres de columnas,
    valida estructura y construye df_stock y ventas_detalle.
    Manejo de errores profesional:
        - captura FileNotFound
        - captura CSV corruptos
        - loggeo
        - mensajes claros
    """
    global stock, almacen, ventas, pedidos, df_stock, ventas_detalle

    if df_stock is not None and ventas_detalle is not None:
        return

    from logger import log_error, log_warning

    try:
        stock_local = pd.read_csv(ARCH_STOCK, dtype=str, encoding="latin1", sep=";")
        almacen_local = pd.read_csv(ARCH_ALMACEN, dtype=str, encoding="latin1", sep=";")
        ventas_local = pd.read_csv(ARCH_VENTAS, dtype=str, encoding="latin1", sep=";")
        pedidos_local = pd.read_csv(
            ARCH_PEDIDOS,
            dtype=str,
            encoding="latin1",
            sep=None,
            engine="python"
        )

    except FileNotFoundError as e:
        log_error(f"Archivo faltante: {e.filename}")
        raise RuntimeError(
            f"Falta el archivo requerido: {e.filename}\n"
            f"Debe colocarse dentro de la carpeta /data"
        ) from e

    except Exception as e:
        log_error(f"Error leyendo CSV: {e}")
        raise RuntimeError(
            "Uno de los archivos CSV está corrupto o mal formateado.\n"
            "Revisar separadores, encoding o columnas."
        ) from e

    # Normalizar columnas
    for df in [stock_local, almacen_local, pedidos_local, ventas_local]:
        df.columns = [c.strip().lower() for c in df.columns]

    # Validaciones
    try:
        _validar_columnas(stock_local, ["codigo", "producto", "stock"], "stock.csv")
        _validar_columnas(almacen_local, ["codigo"], "almacen.csv")
        _validar_columnas(
            ventas_local,
            ["comprobante", "producto", "cantidad", "codigo", "fecha"],
            "ventas.csv",
        )
        _validar_columnas(
            pedidos_local,
            ["numero de pedido dux", "estado de preparacion"],
            "TodoslosPedidos.csv",
        )
    except RuntimeError as e:
        log_error(str(e))
        raise

    # Normalización de texto
    try:
        stock_local["producto_norm"] = stock_local["producto"].apply(normalizar_texto)
        ventas_local["producto_norm"] = ventas_local["producto"].apply(normalizar_texto)
    except Exception as e:
        log_error(f"Error normalizando texto: {e}")
        raise RuntimeError("Error normalizando textos de producto.") from e

    # Merge stock + ubicaciones
    try:
        df_stock_local = stock_local.merge(
            almacen_local.drop(columns=["producto"], errors="ignore"),
            on="codigo",
            how="left"
        )
    except Exception as e:
        log_error(f"Error merge stock-almacen: {e}")
        raise RuntimeError("Error al unir stock.csv con almacen.csv.") from e

    # Estado del pedido en ventas
    try:
        pedidos_local["numero de pedido dux"] = pedidos_local["numero de pedido dux"].astype(str).str.strip()
        pedidos_local["estado de preparacion"] = pedidos_local["estado de preparacion"].astype(str).str.strip()
        ventas_local["comprobante"] = ventas_local["comprobante"].astype(str).str.strip()

        ventas_detalle_local = ventas_local.merge(
            pedidos_local[["numero de pedido dux", "estado de preparacion"]],
            left_on="comprobante",
            right_on="numero de pedido dux",
            how="left"
        )
    except Exception as e:
        log_error(f"Error merge ventas-pedidos: {e}")
        raise RuntimeError("Error al unir ventas.csv con TodoslosPedidos.csv.") from e

    # Asignar si todo salió bien
    stock = stock_local
    almacen = almacen_local
    ventas = ventas_local
    pedidos = pedidos_local
    df_stock = df_stock_local
    ventas_detalle = ventas_detalle_local


# Cargar datos al importar el módulo
cargar_datos()


# =========================================
#  Utilidades de negocio
# =========================================

def clave_orden_picking(item: dict):
    """
    Clave de orden para el campo 'picking':
    - Primero ubicaciones con número inicial (orden numérico)
    - Luego las alfanuméricas/solo letras.
    """
    import re
    pk = str(item.get("picking", "")).strip()
    m = re.match(r"(\d+)", pk)
    if m:
        return (0, int(m.group(1)), pk)
    else:
        return (1, pk)


def obtener_df_stock() -> pd.DataFrame:
    """Devuelve el dataframe de stock+almacen ya procesado."""
    if df_stock is None:
        cargar_datos()
    return df_stock


def obtener_ventas_detalle() -> pd.DataFrame:
    """Devuelve el dataframe de ventas con estado de pedido."""
    if ventas_detalle is None:
        cargar_datos()
    return ventas_detalle


def obtener_historial_por_producto(producto_original: str) -> pd.DataFrame:
    """
    Devuelve un dataframe filtrado con el historial de ventas
    para un producto dado, usando producto_norm.
    """
    df_v = obtener_ventas_detalle()
    prod_norm = normalizar_texto(producto_original)
    df = df_v[df_v["producto_norm"] == prod_norm].copy()

    if df.empty:
        return df

    # Convertir fechas y ordenar (más reciente primero)
    df["fecha_dt"] = pd.to_datetime(df["fecha"], format="%d/%m/%Y", errors="coerce")
    df = df.sort_values("fecha_dt", ascending=False)
    return df


def registrar_historico_reposiciones(data_rows, rol: str = "repositor"):
    """
    Recibe una lista de dicts (data_rows) ya validados
    y los almacena en historico_reposiciones.csv agregando fecha y rol.
    """
    df_hist = pd.DataFrame(data_rows)
    ahora = datetime.now()
    df_hist["fecha_registro"] = ahora.strftime("%Y-%m-%d")
    df_hist["rol"] = rol

    header = not os.path.exists(HIST_FILE)
    df_hist.to_csv(HIST_FILE, mode="a", index=False, encoding="utf-8-sig", header=header)
