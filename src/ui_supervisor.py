# -*- coding: utf-8 -*-
"""
ui_supervisor.py – Interfaz de Supervisor (Industrial Light v1.0)
Autor: Eduardo Hernández
"""

import json
import tkinter as tk
from tkinter import messagebox

from core import (
    obtener_df_stock,
    obtener_historial_por_producto,
    PEND_FILE,
    clave_orden_picking,
)
from ui_role import clear_screen
from logger import log_info, log_error

# Variables globales
root = None
reposicion_list = []
check_vars = {}
obs_entries = {}
entry_codigo = None


# ============================================================
# HISTORIAL
# ============================================================

def mostrar_historial(producto_original: str):
    df = obtener_historial_por_producto(producto_original)

    if df.empty:
        messagebox.showinfo("Historial", "Este producto no tiene historial de ventas.")
        return

    top = tk.Toplevel(root)
    top.title(f"Historial de ventas: {producto_original}")
    top.geometry("850x400")

    txt = tk.Text(top, wrap="none", font=("Consolas", 10), bg="#FFFFFF", fg="#333333")
    txt.pack(fill="both", expand=True)

    txt.insert("end", f"{'Comprobante':<20} {'Fecha':<12} {'Cliente':<35} {'Cant':<5} {'Estado':<25}\n")
    txt.insert("end", "-" * 100 + "\n")

    for _, fila in df.iterrows():
        fecha_dt = fila.get("fecha_dt")
        fecha_str = "" if fecha_dt is None else fecha_dt.strftime("%Y-%m-%d")

        linea = (
            f"{str(fila['comprobante']):<20}"
            f"{fecha_str:<12}"
            f"{str(fila.get('cliente', ''))[:34]:<35}"
            f"{str(fila.get('cantidad', '')):<5}"
            f"{str(fila.get('estado de preparacion', ''))[:24]:<25}\n"
        )
        txt.insert("end", linea)

    txt.config(state="disabled")


# ============================================================
# BÚSQUEDA + TABLA (Industrial Light)
# ============================================================

def buscar_producto(frame_resultados, event=None):
    """Tabla con celdas completas + columnas expansibles + diseño Industrial Light."""
    global check_vars, obs_entries

    try:
        df_stock = obtener_df_stock()
    except Exception as e:
        messagebox.showerror("Error", f"No se pudieron cargar los datos.\n{e}")
        log_error(f"Error al cargar df_stock: {e}")
        return

    codigo = entry_codigo.get().strip()

    for widget in frame_resultados.winfo_children():
        widget.destroy()
    check_vars = {}
    obs_entries = {}

    if codigo == "":
        messagebox.showwarning("Atención", "Ingrese un código o fragmento.")
        return

    try:
        resultados = df_stock[df_stock["codigo"].str.contains(codigo, case=False, na=False)]
    except Exception as e:
        messagebox.showerror("Error", "Error procesando búsqueda.")
        log_error(f"Error filtrando productos: {e}")
        return

    if resultados.empty:
        messagebox.showerror("Sin resultados", f"No hubo coincidencias con '{codigo}'.")
        return

    log_info(f"Supervisor buscó '{codigo}' – {len(resultados)} resultados")

    header_font = ("Segoe UI", 10, "bold")
    cell_font = ("Segoe UI", 10)

    headers = [
        ("Código", 14),
        ("Producto", 45),
        ("Stock", 8),
        ("Picking", 12),
        ("Reposición", 12),
        ("Observaciones", 25),
        ("Historial", 10),
        ("Sel.", 6),
    ]

    # Encabezados
    for col_idx, (text, width) in enumerate(headers):
        tk.Label(
            frame_resultados,
            text=text,
            width=width,
            anchor="w",
            font=header_font,
            bg="#E6E6E6",
            fg="#333333"
        ).grid(row=0, column=col_idx, padx=3, pady=2, sticky="nsew")

    # Expandir columnas
    for col_idx in range(len(headers)):
        frame_resultados.grid_columnconfigure(col_idx, weight=1)

    # Filas con intercalado
    for i, (idx, fila) in enumerate(resultados.iterrows(), start=1):
        bg = "#FFFFFF" if i % 2 == 1 else "#F2F2F2"

        cod = str(fila["codigo"])
        prod = str(fila.get("producto", ""))
        stock = str(fila.get("stock", ""))
        picking = str(fila.get("picking", ""))
        repos = str(fila.get("reposicion", ""))

        # Código
        tk.Label(frame_resultados, text=cod, font=cell_font,
                 bg=bg, fg="#333333", anchor="w") \
            .grid(row=i, column=0, padx=3, pady=1, sticky="nsew")

        # Producto
        tk.Label(frame_resultados, text=prod, font=cell_font,
                 bg=bg, fg="#333333", anchor="w") \
            .grid(row=i, column=1, padx=3, pady=1, sticky="nsew")

        # Stock
        tk.Label(frame_resultados, text=stock, font=cell_font,
                 bg=bg, fg="#333333", anchor="center") \
            .grid(row=i, column=2, padx=3, pady=1, sticky="nsew")

        # Picking
        tk.Label(frame_resultados, text=picking, font=cell_font,
                 bg=bg, fg="#333333", anchor="center") \
            .grid(row=i, column=3, padx=3, pady=1, sticky="nsew")

        # Reposición
        tk.Label(frame_resultados, text=repos, font=cell_font,
                 bg=bg, fg="#333333", anchor="center") \
            .grid(row=i, column=4, padx=3, pady=1, sticky="nsew")

        # Observaciones (Entry)
        clave = f"{cod}_{i}"
        entry_obs = tk.Entry(frame_resultados, width=25, font=cell_font, bg="#FFFFFF")
        entry_obs.grid(row=i, column=5, padx=3, pady=1, sticky="nsew")
        obs_entries[clave] = entry_obs

        # Botón historial
        tk.Button(
            frame_resultados,
            text="Ver",
            font=("Segoe UI", 9),
            command=lambda p=prod: mostrar_historial(p),
            bg="#E1E1E1",
            fg="#333333",
            relief="raised",
            bd=1
        ).grid(row=i, column=6, padx=3, pady=1, sticky="nsew")

        # Checkbox
        var = tk.BooleanVar()
        chk = tk.Checkbutton(frame_resultados, variable=var, bg=bg, activebackground=bg)
        chk.grid(row=i, column=7, padx=3, pady=1, sticky="nsew")
        check_vars[clave] = (var, idx)


# ============================================================
# GUARDAR SELECCIÓN
# ============================================================

def guardar_seleccion(frame_resultados):
    global reposicion_list
    try:
        df_stock = obtener_df_stock()
    except:
        messagebox.showerror("Error", "No se pudo acceder a stock.")
        return

    existentes = set((item["codigo"], item["producto"]) for item in reposicion_list)
    agregados = 0

    for clave, (var, fila_idx) in check_vars.items():
        if not var.get():
            continue

        fila = df_stock.loc[fila_idx]
        cod = str(fila["codigo"])
        prod = str(fila["producto"])

        if (cod, prod) in existentes:
            continue

        obs = obs_entries.get(clave).get().strip()

        reposicion_list.append({
            "codigo": cod,
            "producto": prod,
            "stock": str(fila.get("stock", "")),
            "picking": str(fila.get("picking", "")),
            "reposicion": str(fila.get("reposicion", "")),
            "observaciones": obs
        })

        existentes.add((cod, prod))
        agregados += 1

    if agregados == 0:
        messagebox.showinfo("Sin selección", "No se marcó ningún producto.")
    else:
        messagebox.showinfo("Guardado", f"Se agregaron {agregados} productos.")

        # limpiar tabla
        for w in frame_resultados.winfo_children():
            w.destroy()


# ============================================================
# FINALIZAR SUPERVISOR
# ============================================================

def finalizar_supervisor():
    from ui_role import show_role_selection

    if len(reposicion_list) == 0:
        messagebox.showinfo("Reposición", "No hay productos seleccionados.")
        return

    try:
        ordenada = sorted(reposicion_list, key=clave_orden_picking)
        with open(PEND_FILE, "w", encoding="utf-8") as f:
            json.dump(ordenada, f, ensure_ascii=False, indent=2)
    except Exception as e:
        log_error(f"Error guardando JSON: {e}")
        messagebox.showerror("Error", "No se pudo guardar reposición pendiente.")
        return

    messagebox.showinfo("Reposición pendiente", "Lista guardada correctamente.")
    show_role_selection()


# ============================================================
# UI SUPERVISOR
# ============================================================

def show_supervisor_ui():
    global entry_codigo, reposicion_list, check_vars, obs_entries

    reposicion_list = []
    check_vars = {}
    obs_entries = {}

    clear_screen()
    root.configure(bg="#F2F2F2")

    # Título
    frame_top = tk.Frame(root, bg="#F2F2F2")
    frame_top.pack(pady=15)

    tk.Label(
        frame_top,
        text="Reposición (Supervisor)",
        font=("Segoe UI", 13, "bold"),
        fg="#333333",
        bg="#F2F2F2"
    ).grid(row=0, column=0, columnspan=3, pady=(0, 10))

    tk.Label(
        frame_top,
        text="Código de producto:",
        font=("Segoe UI", 11),
        fg="#333333",
        bg="#F2F2F2"
    ).grid(row=1, column=0, padx=5, sticky="e")

    entry_codigo = tk.Entry(frame_top, width=25, font=("Segoe UI", 11))
    entry_codigo.grid(row=1, column=1, padx=5)

    btn_buscar = tk.Button(
        frame_top,
        text="Buscar",
        command=lambda: buscar_producto(frame_resultados),
        font=("Segoe UI", 11),
        width=10,
        bg="#E1E1E1",
        fg="#333333",
        relief="raised",
        bd=2
    )
    btn_buscar.grid(row=1, column=2, padx=5)

    root.bind("<Return>", lambda event: buscar_producto(frame_resultados))

    # Canvas para scroll horizontal
    canvas = tk.Canvas(root, bg="#F2F2F2", highlightthickness=0)
    canvas.pack(fill="both", expand=True, pady=10)

    scroll_x = tk.Scrollbar(root, orient="horizontal", command=canvas.xview)
    scroll_x.pack(fill="x")
    canvas.configure(xscrollcommand=scroll_x.set)

    frame_resultados = tk.Frame(canvas, bg="#FFFFFF")
    canvas.create_window((0, 0), window=frame_resultados, anchor="nw")

    frame_resultados.bind("<Configure>", lambda event: canvas.configure(scrollregion=canvas.bbox("all")))

    # Botones inferiores
    frame_bot = tk.Frame(root, bg="#F2F2F2")
    frame_bot.pack(pady=(5, 20))

    tk.Button(
        frame_bot,
        text="Guardar selección",
        command=lambda: guardar_seleccion(frame_resultados),
        width=18,
        font=("Segoe UI", 11, "bold"),
        bg="#E1E1E1",
        fg="#333333",
        relief="raised",
        bd=2
    ).grid(row=0, column=0, padx=10)

    tk.Button(
        frame_bot,
        text="Finalizar",
        command=finalizar_supervisor,
        width=18,
        font=("Segoe UI", 11, "bold"),
        bg="#E1E1E1",
        fg="#333333",
        relief="raised",
        bd=2
    ).grid(row=0, column=1, padx=10)

    log_info("Mostrando interfaz de Supervisor")
