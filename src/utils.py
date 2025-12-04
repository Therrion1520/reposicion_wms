"""
utils.py – Utilidades generales del sistema
Autor: Eduardo Hernández
"""

import os
import sys
import unicodedata


# =========================================
#  Manejo de rutas
# =========================================

def base_path() -> str:
    """
    Devuelve la ruta base del ejecutable:
    - Si está empaquetado (.exe), usa sys.executable
    - Si es .py, usa __file__
    """
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))


def data_path(filename: str) -> str:
    """
    Construye ruta absoluta hacia /data/<filename>
    """
    base = base_path()
    return os.path.join(os.path.dirname(base), "data", filename)


# =========================================
#  Normalización de texto
# =========================================

def normalizar_texto(s: str) -> str:
    """
    Normaliza texto para comparaciones:
    - NFKD
    - ASCII
    - minúsculas
    - strip
    """
    return (
        unicodedata.normalize("NFKD", str(s))
        .encode("ascii", "ignore")
        .decode("ascii")
        .strip()
        .lower()
    )
