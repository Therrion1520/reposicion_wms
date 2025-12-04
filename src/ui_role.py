# -*- coding: utf-8 -*-
"""
ui_role.py — Pantalla inicial de selección de rol con estética Industrial Light
Autor: Eduardo Hernández
"""

import os
import tkinter as tk
from tkinter import messagebox

from core import cargar_datos, PEND_FILE
from logger import log_info, log_error


# ============================================================
# VARIABLES GLOBALES COMPARTIDAS
# ============================================================

root = None
current_frames = []


# ============================================================
# LIMPIEZA TOTAL DE PANTALLA
# ============================================================

def clear_screen():
    """Destruye absolutamente todos los widgets en pantalla."""
    global current_frames

    # destruir frames registrados
    for fr in current_frames:
        try:
            fr.destroy()
        except:
            pass

    # destruir cualquier otro widget suelto (failsafe)
    for widget in root.winfo_children():
        try:
            widget.destroy()
        except:
            pass

    current_frames = []


# ============================================================
# PANTALLA PRINCIPAL DE SELECCIÓN DE ROL
# ============================================================

def show_role_selection():
    """Pantalla inicial de selección de rol, centrada y con estilo industrial."""
    from ui_supervisor import show_supervisor_ui
    from ui_repositor import show_repositor_ui

    clear_screen()
    root.unbind("<Return>")

    # intentar cargar datos
    try:
        cargar_datos()
    except Exception as e:
        log_error(f"Error cargando datos: {e}")
        messagebox.showerror("Error", f"No se pudieron cargar los archivos necesarios:\n{e}")
        return

    # ===== ESTÉTICA INDUSTRIAL LIGHT =====
    root.configure(bg="#F2F2F2")

    # ===== CONTENEDOR CENTRADO =====
    container = tk.Frame(root, bg="#F2F2F2")
    container.pack(expand=True)        # <-- Esto centra vertical y horizontalmente

    current_frames.append(container)

    # ===== TÍTULO =====
    lbl_title = tk.Label(
        container,
        text="Seleccione rol de trabajo",
        font=("Segoe UI", 14, "bold"),
        fg="#333333",
        bg="#F2F2F2"
    )
    lbl_title.pack(pady=10)

    # ===== BOTONES =====
    btn_frame = tk.Frame(container, bg="#F2F2F2")
    btn_frame.pack(pady=10)

    current_frames.append(btn_frame)

    btn_style = {
        "width": 18,
        "font": ("Segoe UI", 11, "bold"),
        "bg": "#E1E1E1",
        "fg": "#333333",
        "relief": "raised",
        "bd": 2,
        "activebackground": "#CFCFCF"
    }

    btn_sup = tk.Button(
        btn_frame,
        text="Supervisor",
        command=show_supervisor_ui,
        **btn_style
    )
    btn_sup.pack(side="left", padx=15)

    btn_rep = tk.Button(
        btn_frame,
        text="Repositor",
        command=show_repositor_ui,
        **btn_style
    )
    btn_rep.pack(side="left", padx=15)

    # ===== ESTADO DE REPOSICIÓN PENDIENTE =====
    if os.path.exists(PEND_FILE):
        txt_estado = "Reposición pendiente ENCONTRADA."
        color = "#444444"
    else:
        txt_estado = "No hay reposición pendiente."
        color = "#777777"

    lbl_estado = tk.Label(
        container,
        text=txt_estado,
        font=("Segoe UI", 10),
        fg=color,
        bg="#F2F2F2"
    )
    lbl_estado.pack(pady=10)

    log_info("Se muestra la pantalla de selección de rol.")
