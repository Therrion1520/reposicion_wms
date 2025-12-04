# -*- coding: utf-8 -*-
"""
ui_repositor.py – Interfaz de Repositor (Industrial Light v1.0)
Autor: Eduardo Hernández

Características:
- Tabla centrada horizontalmente.
- Scroll horizontal funcional sin contenedores innecesarios.
- Filas intercaladas.
- Tipografía Segoe UI.
"""

import os
import json
import tkinter as tk
from tkinter import messagebox, filedialog

from logger import log_info, log_error
from core import PEND_FILE, HIST_FILE
from ui_role import clear_screen


# ============================================================
# VARIABLES GLOBALES
# ============================================================

root = None
qty_entries = []
current_frames = []


# ============================================================
# EXPORTAR A EXCEL
# ============================================================

def exportar_excel_repositor():
    """Exporta reposición pendiente a Excel con columna vacía para cantidades."""
    if not os.path.exists(PEND_FILE):
        messagebox.showinfo("Reposición", "No hay reposición pendiente.")
        return

    try:
        with open(PEND_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        log_error(f"JSON corrupto al exportar: {e}")
        messagebox.showerror("Error", "reposicion_pendiente.json está dañado.")
        return

    if not isinstance(data, list) or len(data) == 0:
        messagebox.showinfo("Reposición", "La reposición pendiente está vacía.")
        return

    import pandas as pd

    df = pd.DataFrame(data)
    df["cantidad_reponer"] = ""

    archivo_salida = filedialog.asksaveasfilename(
        defaultextension=".xlsx",
        filetypes=[("Excel files", "*.xlsx")],
        title="Guardar archivo Excel"
    )

    if not archivo_salida:
        return

    try:
        df.to_excel(archivo_salida, index=False)
    except Exception as e:
        log_error(f"Error guardando Excel: {e}")
        messagebox.showerror("Error", f"No se pudo guardar el archivo Excel:\n{e}")
        return

    messagebox.showinfo("Exportación", "Archivo exportado con éxito.")
    log_info("Repositor exportó Excel correctamente")


# ============================================================
# FINALIZAR PROCESO DEL REPOSITOR
# ============================================================

def finalizar_repositor():
    """Valida cantidades, guarda histórico y elimina el JSON pendiente."""
    global qty_entries

    from ui_role import show_role_selection
    from datetime import datetime
    import pandas as pd

    if not os.path.exists(PEND_FILE):
        messagebox.showerror("Error", "No existe reposición pendiente.")
        show_role_selection()
        return

    try:
        with open(PEND_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        log_error(f"Error leyendo JSON: {e}")
        messagebox.showerror("Error", "reposicion_pendiente.json está dañado.")
        show_role_selection()
        return

    if not isinstance(data, list) or len(data) == 0:
        messagebox.showerror("Error", "La reposición pendiente está vacía.")
        show_role_selection()
        return

    # validar cantidades
    for i, row in enumerate(data):
        val = qty_entries[i].get().strip()

        if val == "":
            messagebox.showerror("Error", "Hay cantidades vacías (pueden ser 0, pero no vacías).")
            return

        try:
            n = int(val)
        except ValueError:
            messagebox.showerror("Error", f"Cantidad inválida en la fila {i+1}: '{val}'.")
            return

        if n < 0:
            messagebox.showerror("Error", f"Cantidad negativa en la fila {i+1}.")
            return

        row["cantidad_reponer"] = n

    df_hist = pd.DataFrame(data)
    df_hist["fecha_registro"] = datetime.now().strftime("%Y-%m-%d")
    df_hist["rol"] = "repositor"

    header = not os.path.exists(HIST_FILE)

    try:
        df_hist.to_csv(HIST_FILE, mode="a", index=False, encoding="utf-8-sig", header=header)
    except Exception as e:
        log_error(f"Error guardando histórico: {e}")
        messagebox.showerror("Error", "No se pudo guardar el histórico.")
        return

    try:
        os.remove(PEND_FILE)
    except:
        pass

    messagebox.showinfo("Éxito", "Proceso finalizado con éxito.")
    log_info("Repositor finalizó el proceso.")
    show_role_selection()


# ============================================================
# UI – REPOSITOR (Industrial Light)
# ============================================================

def show_repositor_ui():
    """UI del repositor con tabla centrada y scroll horizontal."""
    global qty_entries, current_frames

    from ui_role import show_role_selection

    qty_entries = []
    clear_screen()

    root.configure(bg="#F2F2F2")

    # cargar pendiente
    if not os.path.exists(PEND_FILE):
        messagebox.showinfo("Reposición", "No hay reposición pendiente.")
        show_role_selection()
        return

    try:
        with open(PEND_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        log_error(f"JSON corrupto: {e}")
        messagebox.showerror("Error", "reposicion_pendiente.json está dañado.")
        show_role_selection()
        return

    if not isinstance(data, list) or len(data) == 0:
        messagebox.showinfo("Reposición", "La reposición pendiente está vacía.")
        show_role_selection()
        return

    # ========= TÍTULO =========
    lbl_title = tk.Label(
        root,
        text="Reposición pendiente",
        font=("Segoe UI", 14, "bold"),
        fg="#333333",
        bg="#F2F2F2"
    )
    lbl_title.pack(pady=(10, 5))

    # ========= CANVAS (TABLA CENTRADA) =========
    canvas = tk.Canvas(root, bg="#F2F2F2", highlightthickness=0)
    canvas.pack(pady=(0, 0), fill="both", expand=True)

    scroll_x = tk.Scrollbar(root, orient="horizontal", command=canvas.xview)
    scroll_x.pack(fill="x")

    canvas.configure(xscrollcommand=scroll_x.set)

    # frame interno donde vive la tabla
    frame_inner = tk.Frame(canvas, bg="#F2F2F2")
    canvas.create_window((0, 0), window=frame_inner, anchor="n")

    def update_scroll(event=None):
        canvas.configure(scrollregion=canvas.bbox("all"))

    frame_inner.bind("<Configure>", update_scroll)
    canvas.bind("<Configure>", update_scroll)

    # ========= TABLA =========
    headers = [
        ("Código", 10),
        ("Producto", 40),
        ("Stock", 8),
        ("Picking", 12),
        ("Reposición", 12),
        ("Observaciones", 25),
        ("Cant. a reponer", 14),
    ]

    header_font = ("Segoe UI", 10, "bold")
    cell_font = ("Segoe UI", 10)

    for col, (text, width) in enumerate(headers):
        tk.Label(
            frame_inner,
            text=text,
            width=width,
            anchor="w",
            font=header_font,
            bg="#E6E6E6",
            fg="#333333"
        ).grid(row=0, column=col, padx=3, pady=2, sticky="nsew")

    # filas
    for i, fila in enumerate(data, start=1):
        bg = "#FFFFFF" if i % 2 == 1 else "#F2F2F2"

        tk.Label(frame_inner, text=fila["codigo"], font=cell_font,
                 bg=bg, fg="#333333", width=10, anchor="w") \
            .grid(row=i, column=0, padx=3, pady=1, sticky="nsew")

        tk.Label(frame_inner, text=fila["producto"], font=cell_font,
                 bg=bg, fg="#333333", width=40, anchor="w") \
            .grid(row=i, column=1, padx=3, pady=1, sticky="nsew")

        tk.Label(frame_inner, text=fila["stock"], font=cell_font,
                 bg=bg, fg="#333333", width=8, anchor="center") \
            .grid(row=i, column=2, padx=3, pady=1, sticky="nsew")

        tk.Label(frame_inner, text=fila["picking"], font=cell_font,
                 bg=bg, fg="#333333", width=12, anchor="center") \
            .grid(row=i, column=3, padx=3, pady=1, sticky="nsew")

        tk.Label(frame_inner, text=fila["reposicion"], font=cell_font,
                 bg=bg, fg="#333333", width=12, anchor="center") \
            .grid(row=i, column=4, padx=3, pady=1, sticky="nsew")

        tk.Label(frame_inner, text=fila["observaciones"], font=cell_font,
                 bg=bg, fg="#333333", width=25, anchor="w") \
            .grid(row=i, column=5, padx=3, pady=1, sticky="nsew")

        entry_qty = tk.Entry(frame_inner, width=10, font=cell_font, bg="#FFFFFF")
        entry_qty.grid(row=i, column=6, padx=3, pady=1, sticky="nsew")
        qty_entries.append(entry_qty)

    # ============================================================
    # BOTONES FINALES
    # ============================================================

    frame_btn = tk.Frame(root, bg="#F2F2F2")
    frame_btn.pack(pady=(10, 20))

    tk.Button(
        frame_btn,
        text="Exportar a Excel",
        command=exportar_excel_repositor,
        width=20,
        font=("Segoe UI", 11),
        bg="#E1E1E1",
        fg="#333333",
        relief="raised",
        bd=2,
        activebackground="#CFCFCF"
    ).pack(side="left", padx=10)

    tk.Button(
        frame_btn,
        text="Proceso finalizado con éxito",
        command=finalizar_repositor,
        width=28,
        font=("Segoe UI", 11, "bold"),
        bg="#E1E1E1",
        fg="#333333",
        relief="raised",
        bd=2,
        activebackground="#CFCFCF"
    ).pack(side="left", padx=10)

    log_info("Mostrando interfaz de Repositor")
