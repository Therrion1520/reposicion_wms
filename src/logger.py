"""
logger.py – Sistema de logging profesional
Autor: Eduardo Hernández

Características:
- Archivo de log diario en /data/logs/
- Registra inicio, errores y acciones clave
"""

import os
import logging
from datetime import datetime

from utils import base_path


def _logs_dir():
    """Devuelve ruta absoluta a /data/logs, creándola si no existe."""
    base = os.path.dirname(base_path())
    path = os.path.join(base, "data", "logs")
    os.makedirs(path, exist_ok=True)
    return path


def init_logger():
    """
    Inicializa un logger profesional para toda la aplicación.
    Crea un archivo diario: logs/2025-01-01.log
    """
    logs_path = _logs_dir()
    fecha = datetime.now().strftime("%Y-%m-%d")
    logfile = os.path.join(logs_path, f"{fecha}.log")

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        handlers=[
            logging.FileHandler(logfile, encoding="utf-8"),
            logging.StreamHandler()
        ]
    )

    logging.info("=== Inicio de aplicación Reposición & Picking PRO ===")


def log_info(msg: str):
    logging.info(msg)


def log_error(msg: str):
    logging.error(msg)


def log_warning(msg: str):
    logging.warning(msg)
