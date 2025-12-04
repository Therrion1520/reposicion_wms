"""
main.py – Launcher principal del sistema
Versión: 3.4B (estructurada)
Autor: Eduardo Hernández
"""

import tkinter as tk

# Importar módulos internos
from ui_role import show_role_selection
from logger import init_logger



def launch_app():
    """Punto de entrada principal."""
    # Iniciar logger
    init_logger()
    

    # Crear ventana Tk
    root = tk.Tk()
    root.title("Reposición & Picking PRO")
    root.iconbitmap("favicon.ico")  
    root.geometry("980x620")


    # Mantener root accesible a otros módulos
    # Técnicamente simple: lo pasamos como global
    import ui_role, ui_supervisor, ui_repositor
    ui_role.root = root
    ui_supervisor.root = root
    ui_repositor.root = root

    # Pantalla inicial
    show_role_selection()

    root.mainloop()


if __name__ == "__main__":
    launch_app()
