import json
import os
import subprocess
import sys
import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path
from tqdm import tqdm
import logging
from dotenv import load_dotenv

# Cargar configuración desde .env
load_dotenv()
VS_CODE_PATH = os.getenv('VS_CODE_PATH', 'code')

# Configuración de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def check_vscode_installed() -> bool:
    """Verifica si Visual Studio Code está instalado y accesible en la línea de comandos."""
    try:
        subprocess.run([VS_CODE_PATH, "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return True
    except FileNotFoundError:
        return False

def create_file(file_path: Path, content: str) -> str:
    """Crea un archivo con el contenido especificado."""
    try:
        file_path.write_text(content)
        logging.info(f"Archivo creado: {file_path.resolve()}")
        return f"Archivo creado: {file_path.resolve()}"
    except Exception as e:
        logging.error(f"Error al crear el archivo {file_path}: {e}")
        return f"Error al crear el archivo {file_path}: {e}"

def create_structure(base_dir: Path, items: list) -> list:
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

def load_config(file_path: Path) -> list:
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
        logging.error(f"Error al leer el archivo de configuración: {e}")
        raise RuntimeError(f"Error al leer el archivo de configuración: {e}")

def open_vscode(directory: Path):
    """Abre Visual Studio Code en el directorio especificado."""
    vscode_command = [VS_CODE_PATH, str(directory)]
    if sys.platform == "win32":
        vscode_command = [r'C:\Program Files\Microsoft VS Code\Code.exe', str(directory)]

    if check_vscode_installed():
        try:
            subprocess.run(vscode_command, check=True)
            logging.info(f"Visual Studio Code abierto en {directory.resolve()}.")
        except subprocess.CalledProcessError as e:
            logging.error(f"Error al abrir Visual Studio Code: {e}")
            messagebox.showerror("Error", f"No se pudo abrir Visual Studio Code: {e}")
        except Exception as e:
            logging.error(f"Error inesperado al abrir Visual Studio Code: {e}")
            messagebox.showerror("Error", f"Error inesperado: {e}")
    else:
        messagebox.showwarning("Advertencia", "Visual Studio Code no está instalado o el comando 'code' no está en el PATH. Por favor, instala Visual Studio Code y asegúrate de que el comando 'code' esté disponible en la línea de comandos.")

def open_file_explorer(directory: Path):
    """Abre el explorador de archivos en el directorio especificado."""
    try:
        if sys.platform == "win32":
            os.startfile(directory)
        elif sys.platform == "darwin":
            os.system(f"open {directory}")
        else:
            os.system(f"xdg-open {directory}")
        logging.info(f"Explorador de archivos abierto en {directory.resolve()}.")
    except Exception as e:
        logging.error(f"No se pudo abrir el explorador de archivos: {e}")
        messagebox.showerror("Error", f"No se pudo abrir el explorador de archivos: {e}")

def gui_setup():
    """Configura y ejecuta la interfaz gráfica."""
    root = tk.Tk()
    root.title("Creador de Estructura de Proyecto")
    root.geometry("600x400")

    def select_base_dir():
        directory = filedialog.askdirectory(title="Seleccionar Directorio Base")
        if directory:
            base_dir.set(directory)
    
    def select_config_file():
        file = filedialog.askopenfilename(title="Seleccionar Archivo de Configuración", filetypes=[("Archivos JSON", "*.json")])
        if file:
            config_file.set(file)

    def run_process():
        base_path = Path(base_dir.get())
        config_path = Path(config_file.get())
        if not base_path or not config_path:
            messagebox.showerror("Error", "Directorio base o archivo de configuración no seleccionados.")
            return
        try:
            run_script(base_path, config_path)
            open_vscode(base_path)  # Intentar abrir Visual Studio Code en el directorio base
            open_file_explorer(base_path)  # Intentar abrir el explorador de archivos en el directorio base
        except Exception as e:
            messagebox.showerror("Error", str(e))

    base_dir = tk.StringVar()
    config_file = tk.StringVar()

    tk.Label(root, text="Directorio Base:").pack(pady=5)
    tk.Entry(root, textvariable=base_dir, width=70).pack(pady=5)
    tk.Button(root, text="Seleccionar Directorio Base", command=select_base_dir).pack(pady=5)

    tk.Label(root, text="Archivo de Configuración:").pack(pady=5)
    tk.Entry(root, textvariable=config_file, width=70).pack(pady=5)
    tk.Button(root, text="Seleccionar Archivo de Configuración", command=select_config_file).pack(pady=5)

    tk.Button(root, text="Crear Estructura", command=run_process).pack(pady=20)

    root.mainloop()

def run_script(base_dir: Path, config_file: Path):
    """Ejecuta el script para crear la estructura de directorios y archivos."""
    if not base_dir.exists():
        raise FileNotFoundError(f"El directorio base no existe: {base_dir.resolve()}")
    
    items = load_config(config_file)
    log_entries = create_structure(base_dir, items)
    
    # Mostrar resultados en la interfaz gráfica
    messagebox.showinfo("Éxito", f"Estructura de proyecto creada exitosamente.\nRuta de acceso: {base_dir.resolve()}")
    
    # Abrir el directorio base en el explorador de archivos
    open_file_explorer(base_dir)

def main():
    """Función principal para ejecutar el script con la interfaz gráfica."""
    gui_setup()

if __name__ == "__main__":
    main()
