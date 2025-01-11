import json
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from datetime import datetime
import threading

class ProjectStructureManager:
    def create_structure_async(self, base_dir, items, callback):
        def _create():
            success = self.create_structure(base_dir, items)
            callback(success)
        threading.Thread(target=_create).start()

    def create_structure(self, base_dir, items):
        try:
            for item in items:
                path = Path(base_dir) / item['path']
                if item['type'] == 'directory':
                    path.mkdir(parents=True, exist_ok=True)
                    if 'files' in item:
                        self.create_structure(path, item['files'])
                elif item['type'] == 'file':
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.touch(exist_ok=True)
                    path.write_text(item.get('content', ''))
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False

    def load_config_from_file(self, file_path):
        with open(file_path, 'r') as f:
            data = json.load(f)
            return data

def create_gui():
    root = tk.Tk()
    root.title("Gestor de Estructuras de Proyecto")
    root.geometry("600x400")

    manager = ProjectStructureManager()

    base_dir = tk.StringVar()
    config_file_path = tk.StringVar()

    ttk.Label(root, text="Seleccionar Directorio Base:").pack(pady=5)
    ttk.Entry(root, textvariable=base_dir).pack(fill=tk.X, padx=10)
    ttk.Button(root, text="Seleccionar", command=lambda: base_dir.set(filedialog.askdirectory())).pack(pady=5)

    ttk.Label(root, text="Seleccionar Archivo config.json:").pack(pady=5)
    ttk.Entry(root, textvariable=config_file_path).pack(fill=tk.X, padx=10)
    ttk.Button(root, text="Seleccionar", command=lambda: config_file_path.set(filedialog.askopenfilename(filetypes=[("JSON files", "*.json")]))).pack(pady=5)

    progress = ttk.Progressbar(root, mode='indeterminate')

    def on_create():
        if not base_dir.get():
            messagebox.showerror("Error", "Por favor seleccione un directorio base")
            return

        if not config_file_path.get():
            messagebox.showerror("Error", "Por favor seleccione un archivo config.json")
            return

        progress.pack(fill=tk.X, pady=5)
        progress.start()

        template = manager.load_config_from_file(Path(config_file_path.get()))

        if not template:
            messagebox.showerror("Error", "Archivo config.json inválido")
            return

        def on_complete(success):
            progress.stop()
            progress.pack_forget()
            if success:
                messagebox.showinfo("Éxito", "Estructura creada correctamente")
            else:
                messagebox.showerror("Error", "Hubo un problema al crear la estructura")

        manager.create_structure_async(Path(base_dir.get()), template, on_complete)

    ttk.Button(root, text="Crear Estructura", command=on_create).pack(pady=10)

    return root

if __name__ == "__main__":
    root = create_gui()
    root.mainloop()
