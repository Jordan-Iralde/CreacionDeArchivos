import json
from pathlib import Path
from tqdm import tqdm
import tkinter as tk
from tkinter import filedialog, messagebox
import os
import subprocess
import sys
import time

def find_config_file(base_path: Path, filename: str = "config.json"):
    """Busca el archivo config.json en el directorio base y subdirectorios."""
    config_file = base_path / filename
    if config_file.exists():
        return config_file
    for root, dirs, files in os.walk(base_path):
        if filename in files:
            return Path(root) / filename
    raise FileNotFoundError(f"No se encontró el archivo {filename} en {base_path.resolve()} o sus subdirectorios.")

def create_file(file_path: Path, content: str):
    """Crea un archivo con el contenido especificado."""
    try:
        file_path.write_text(content)
        return f"Archivo creado: {file_path.resolve()}"
    except Exception as e:
        return f"Error al crear el archivo {file_path}: {e}"

def create_structure(base_dir: Path, items):
    """Crea la estructura de directorios y archivos según la configuración."""
    log = []
    for item in tqdm(items, desc="Creando estructura", unit="item"):
        path = base_dir / item['path']
        if item['type'] == 'directory':
            path.mkdir(parents=True, exist_ok=True)
            log.append(f"Directorio creado: {path.resolve()}")
        elif item['type'] == 'file':
            path.parent.mkdir(parents=True, exist_ok=True)
            content = item.get('content', f"# Contenido inicial para {path.name}")
            log.append(create_file(path, content))
        else:
            log.append(f"Error: Tipo desconocido para {path}")
    return log

def load_config(file_path: Path):
    """Carga y valida la configuración del archivo JSON."""
    try:
        with open(file_path, 'r') as f:
            items = json.load(f)
            if not isinstance(items, list):
                raise ValueError("La configuración debe ser una lista en el archivo JSON.")
            for item in items:
                if not isinstance(item, dict) or 'type' not in item or 'path' not in item:
                    raise ValueError("Cada elemento debe ser un diccionario con 'type' y 'path'.")
                if item['type'] not in ['directory', 'file']:
                    raise ValueError("El valor de 'type' debe ser 'directory' o 'file'.")
            return items
    except (json.JSONDecodeError, ValueError, FileNotFoundError) as e:
        raise RuntimeError(f"Error al leer el archivo de configuración: {e}")

def open_vscode(directory: Path):
    """Intenta abrir Visual Studio Code en el directorio especificado."""
    try:
        subprocess.run(["code", str(directory)], check=True)
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"No se pudo abrir Visual Studio Code: {e}")
    except FileNotFoundError:
        messagebox.showwarning("Advertencia", "Visual Studio Code no está instalado o el comando 'code' no está en el PATH.")

def open_file_explorer(directory: Path):
    """Abre el explorador de archivos en el directorio especificado."""
    try:
        if sys.platform == "win32":
            os.startfile(directory)
        elif sys.platform == "darwin":
            os.system(f"open {directory}")
        else:
            os.system(f"xdg-open {directory}")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo abrir el explorador de archivos: {e}")

def gui_setup():
    """Configura y ejecuta la interfaz gráfica."""
    root = tk.Tk()
    root.title("Creador de Estructura de Proyecto")

    def select_base_dir():
        base_dir.set(filedialog.askdirectory(title="Seleccionar Directorio Base"))

    def run_process():
        base_path = Path(base_dir.get())
        if not base_path:
            messagebox.showerror("Error", "Directorio base no seleccionado.")
            return
        try:
            config_path = find_config_file(base_path)
            items = load_config(config_path)
            log_entries = create_structure(base_path, items)
            for entry in log_entries:
                print(f"\033[92m{entry}\033[0m")
            messagebox.showinfo("Éxito", f"Estructura de proyecto creada exitosamente.\nRuta de acceso: {base_path.resolve()}")
            if open_vscode_var.get():
                open_vscode(base_path)
            if open_explorer_var.get():
                open_file_explorer(base_path)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    base_dir = tk.StringVar()
    open_vscode_var = tk.BooleanVar(value=True)  # Opción para abrir VSCode
    open_explorer_var = tk.BooleanVar(value=False)  # Opción para abrir explorador de archivos

    tk.Label(root, text="Directorio Base:").pack(pady=5)
    tk.Entry(root, textvariable=base_dir, width=50).pack(pady=5)
    tk.Button(root, text="Seleccionar Directorio Base", command=select_base_dir).pack(pady=5)

    tk.Label(root, text="Abrir Visual Studio Code:").pack(pady=5)
    tk.Checkbutton(root, variable=open_vscode_var).pack(pady=5)

    tk.Label(root, text="Abrir Explorador de Archivos:").pack(pady=5)
    tk.Checkbutton(root, variable=open_explorer_var).pack(pady=5)

    tk.Button(root, text="Crear Estructura", command=run_process).pack(pady=20)

    root.mainloop()

def main():
    """Función principal para ejecutar el script con la interfaz gráfica."""
    gui_setup()

if __name__ == "__main__":
    main()
