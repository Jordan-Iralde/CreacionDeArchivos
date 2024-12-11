import json
import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from typing import List, Dict, Union, Optional
import logging
from datetime import datetime
import shutil
import threading

class ProjectTemplate:
    """Clase para manejar plantillas de proyectos."""
    
    def __init__(self, name: str, description: str, structure: List[Dict]):
        self.name = name
        self.description = description
        self.structure = structure

class ProjectStructureManager:
    """Administrador de estructura de proyectos con capacidades para JARVIS."""
    
    def __init__(self):
        self.setup_logging()
        self.templates_dir = Path("templates")
        self.history_file = Path("structure_history.json")
        self.history = []
        self.templates: Dict[str, ProjectTemplate] = {}
        self.load_templates()
        self.load_history()

    def setup_logging(self):
        """Configura el sistema de logging avanzado."""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            filename=log_dir / f'structure_manager_{datetime.now().strftime("%Y%m%d")}.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - [%(threadName)s] - %(message)s'
        )

    def load_templates(self):
        """Carga las plantillas predefinidas."""
        self.templates_dir.mkdir(exist_ok=True)
        for template_file in self.templates_dir.glob("*.json"):
            try:
                data = json.loads(template_file.read_text())
                self.templates[template_file.stem] = ProjectTemplate(
                    name=data.get("name", template_file.stem),
                    description=data.get("description", ""),
                    structure=data.get("structure", [])
                )
            except Exception as e:
                logging.error(f"Error al cargar plantilla {template_file}: {e}")

    def save_template(self, template: ProjectTemplate) -> bool:
        """Guarda una nueva plantilla."""
        try:
            template_path = self.templates_dir / f"{template.name}.json"
            template_data = {
                "name": template.name,
                "description": template.description,
                "structure": template.structure
            }
            template_path.write_text(json.dumps(template_data, indent=2))
            self.templates[template.name] = template
            return True
        except Exception as e:
            logging.error(f"Error al guardar plantilla: {e}")
            return False

    def create_structure_async(self, base_dir: Path, items: List[Dict], callback: callable):
        """Crea la estructura de forma asíncrona."""
        def _create():
            success = self.create_structure(base_dir, items)
            callback(success)
        
        thread = threading.Thread(target=_create)
        thread.start()

    def create_structure(self, base_dir: Path, items: List[Dict]) -> bool:
        """Versión mejorada de create_structure con validación y backup."""
        # Crear backup si el directorio existe y tiene contenido
        if base_dir.exists() and any(base_dir.iterdir()):
            backup_dir = base_dir.parent / f"{base_dir.name}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            try:
                shutil.copytree(base_dir, backup_dir)
                logging.info(f"Backup creado en: {backup_dir}")
            except Exception as e:
                logging.error(f"Error al crear backup: {e}")
                return False

        try:
            for item in items:
                path = base_dir / item['path']
                logging.info(f"Procesando: {path}")
                
                if item['type'] == 'directory':
                    path.mkdir(parents=True, exist_ok=True)
                    if permissions := item.get('permissions'):
                        os.chmod(path, permissions)
                    logging.info(f"Directorio creado: {path}")
                
                elif item['type'] == 'file':
                    path.parent.mkdir(parents=True, exist_ok=True)
                    content = item.get('content', "")
                    path.write_text(content)
                    if permissions := item.get('permissions'):
                        os.chmod(path, permissions)
                    logging.info(f"Archivo creado: {path}")
                
                elif item['type'] == 'symlink':
                    target = item.get('target')
                    if target:
                        path.symlink_to(target)
                        logging.info(f"Symlink creado: {path} -> {target}")
                
                else:
                    logging.warning(f"Tipo desconocido ignorado: {path}")
            
            return True
        except Exception as e:
            logging.error(f"Error al crear estructura: {str(e)}")
            return False

    def analyze_history(self) -> Dict:
        """Analiza el historial para encontrar patrones de uso."""
        if not self.history:
            return {}
        
        analysis = {
            "total_structures": len(self.history),
            "templates_usage": {},
            "most_used_template": None,
            "last_used": self.history[-1],
            "usage_by_month": {}
        }
        
        for entry in self.history:
            template = entry["template"]
            date = datetime.fromisoformat(entry["date"])
            month_key = date.strftime("%Y-%m")
            
            analysis["templates_usage"][template] = analysis["templates_usage"].get(template, 0) + 1
            analysis["usage_by_month"][month_key] = analysis["usage_by_month"].get(month_key, 0) + 1
        
        if analysis["templates_usage"]:
            analysis["most_used_template"] = max(
                analysis["templates_usage"].items(),
                key=lambda x: x[1]
            )[0]
        
        return analysis

    def load_history(self):
        """Carga el historial de estructuras creadas."""
        try:
            if self.history_file.exists():
                with open(self.history_file, 'r') as f:
                    self.history = json.load(f)
            else:
                self.history = []
                # Crear el archivo si no existe
                with open(self.history_file, 'w') as f:
                    json.dump(self.history, f)
            logging.info(f"Historial cargado: {len(self.history)} entradas")
        except Exception as e:
            logging.error(f"Error al cargar historial: {e}")
            self.history = []

    def save_history_entry(self, template_name: str, base_dir: Path):
        """Guarda una nueva entrada en el historial."""
        try:
            entry = {
                "date": datetime.now().isoformat(),
                "template": template_name,
                "base_dir": str(base_dir)
            }
            self.history.append(entry)
            with open(self.history_file, 'w') as f:
                json.dump(self.history, f, indent=2)
            logging.info(f"Nueva entrada guardada en historial: {entry}")
        except Exception as e:
            logging.error(f"Error al guardar entrada en historial: {e}")

def create_modern_gui():
    """Interfaz gráfica moderna con más funcionalidades."""
    root = tk.Tk()
    root.title("JARVIS - Gestor Avanzado de Estructuras de Proyecto")
    root.geometry("800x600")
    
    style = ttk.Style()
    style.theme_use('clam')
    
    manager = ProjectStructureManager()
    
    # Crear frames principales
    main_frame = ttk.Frame(root, padding="10")
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    # Variables
    base_dir = tk.StringVar()
    selected_template = tk.StringVar()
    
    # Widgets
    ttk.Label(main_frame, text="Gestor de Estructuras de Proyecto", 
              font=("Helvetica", 16)).pack(pady=10)
    
    # Frame para selección de directorio y plantilla
    input_frame = ttk.LabelFrame(main_frame, text="Configuración", padding="5")
    input_frame.pack(fill=tk.X, pady=5)
    
    ttk.Button(input_frame, text="Seleccionar Directorio Base",
               command=lambda: base_dir.set(filedialog.askdirectory())).pack(fill=tk.X)
    ttk.Entry(input_frame, textvariable=base_dir).pack(fill=tk.X, pady=5)
    
    # Combobox para plantillas
    ttk.Label(input_frame, text="Seleccionar Plantilla:").pack()
    template_combo = ttk.Combobox(input_frame, textvariable=selected_template)
    template_combo['values'] = list(manager.templates.keys())
    template_combo.pack(fill=tk.X, pady=5)
    
    # Botón de creación con barra de progreso
    progress = ttk.Progressbar(main_frame, mode='indeterminate')
    
    def on_create():
        if not base_dir.get():
            messagebox.showerror("Error", "Por favor seleccione un directorio base")
            return
            
        if not selected_template.get():
            messagebox.showerror("Error", "Por favor seleccione una plantilla")
            return
            
        progress.pack(fill=tk.X, pady=5)
        progress.start()
        
        template = manager.templates.get(selected_template.get())
        if not template:
            messagebox.showerror("Error", "Plantilla no encontrada")
            return
            
        def on_complete(success):
            progress.stop()
            progress.pack_forget()
            
            if success:
                messagebox.showinfo("Éxito", "Estructura creada correctamente")
                open_file_explorer(Path(base_dir.get()))
            else:
                messagebox.showerror("Error", "Hubo un problema al crear la estructura")
        
        manager.create_structure_async(Path(base_dir.get()), template.structure, on_complete)
    
    ttk.Button(main_frame, text="Crear Estructura", command=on_create).pack(pady=10)
    
    # Frame para estadísticas
    stats_frame = ttk.LabelFrame(main_frame, text="Estadísticas", padding="5")
    stats_frame.pack(fill=tk.BOTH, expand=True, pady=5)
    
    def update_stats():
        analysis = manager.analyze_history()
        stats_text = (
            f"Total de estructuras creadas: {analysis.get('total_structures', 0)}\n"
            f"Plantilla más usada: {analysis.get('most_used_template', 'N/A')}\n"
            f"Último uso: {analysis.get('last_used', {}).get('date', 'N/A')}"
        )
        stats_label.config(text=stats_text)
    
    stats_label = ttk.Label(stats_frame, text="")
    stats_label.pack(pady=5)
    update_stats()
    
    return root

if __name__ == "__main__":
    root = create_modern_gui()
    root.mainloop()
