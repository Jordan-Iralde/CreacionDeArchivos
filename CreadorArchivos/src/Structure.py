import json
import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path

def create_file(file_path: Path, content: str):
    """Crea un archivo con contenido."""
    try:
        file_path.write_text(content)
        return f"Archivo creado: {file_path.resolve()}"
    except Exception as e:
        return f"Error al crear el archivo {file_path}: {e}"

def create_structure(base_dir: Path, items: list):
    """Crea la estructura de directorios y archivos."""
    for item in items:
        path = base_dir / item['path']
        if item['type'] == 'directory':
            path.mkdir(parents=True, exist_ok=True)
        elif item['type'] == 'file':
            path.parent.mkdir(parents=True, exist_ok=True)
            create_file(path, item.get('content', ""))
        else:
            print(f"Tipo desconocido: {path}") #Nada

def load_config(file_path: Path) -> list:
    """Carga la configuración del archivo JSON."""
    with open(file_path, 'r') as f:
        return json.load(f)

def open_file_explorer(directory: Path):
    """Abre el explorador de archivos en el directorio."""
    if sys.platform == "win32": #para abrir el explorador de archivos
        os.startfile(directory)
    elif sys.platform == "darwin":
        os.system(f"open {directory}")
    else:
        os.system(f"xdg-open {directory}")

def gui_setup():
    """Interfaz gráfica simple."""
    root = tk.Tk()
    root.title("Creador de Estructura de Proyecto")
    
    def select_base_dir(): #Elegir la carpeta para hacer la estructura
        base_dir.set(filedialog.askdirectory())
    
    def select_config_file():
        config_file.set(filedialog.askopenfilename(filetypes=[("Archivos JSON", "*.json")]))
    
    def run_process():
        base_path = Path(base_dir.get())
        config_path = Path(config_file.get())
        items = load_config(config_path)
        create_structure(base_path, items)
        open_file_explorer(base_path)
    
    base_dir = tk.StringVar() #Entradas
    config_file = tk.StringVar()
    
    tk.Button(root, text="Seleccionar Directorio Base", command=select_base_dir).pack()
    tk.Entry(root, textvariable=base_dir, width=50).pack()
    
    tk.Button(root, text="Seleccionar Archivo de Configuración", command=select_config_file).pack()
    tk.Entry(root, textvariable=config_file, width=50).pack()
    
    tk.Button(root, text="Crear Estructura", command=run_process).pack()

    root.mainloop()

if __name__ == "__main__":
    gui_setup()
