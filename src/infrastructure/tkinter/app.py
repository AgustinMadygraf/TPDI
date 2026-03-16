"""Aplicación GUI con Tkinter."""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Optional

import numpy as np
from PIL import Image as PILImage, ImageTk

from src.entities.image import Image
from src.interface_adapters.controllers.main_controller import MainController


class TPDIApp:
    """Aplicación principal de Técnicas de Procesamiento Digital de Imágenes."""
    
    WINDOW_TITLE = "TPDI - Procesamiento Digital de Imágenes"
    WINDOW_WIDTH = 1200
    WINDOW_HEIGHT = 800
    PREVIEW_SIZE = (400, 400)
    THUMBNAIL_SIZE = (120, 120)
    
    def __init__(self):
        self._controller = MainController()
        self._root: Optional[tk.Tk] = None
        self._current_image_tk: Optional[ImageTk.PhotoImage] = None
        self._thumbnail_refs: List[ImageTk.PhotoImage] = []
        
    def run(self) -> None:
        """Inicia la aplicación."""
        self._root = tk.Tk()
        self._root.title(self.WINDOW_TITLE)
        self._root.geometry(f"{self.WINDOW_WIDTH}x{self.WINDOW_HEIGHT}")
        self._root.minsize(800, 600)
        
        self._build_ui()
        self._load_default_images()
        
        self._root.mainloop()
    
    def _build_ui(self) -> None:
        """Construye la interfaz de usuario."""
        # Frame principal
        main_frame = ttk.Frame(self._root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")
        
        # Configurar grid
        self._root.columnconfigure(0, weight=1)
        self._root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Header
        header = ttk.Label(
            main_frame,
            text="TPDI - Procesamiento Digital de Imágenes",
            font=("Helvetica", 16, "bold")
        )
        header.grid(row=0, column=0, columnspan=2, pady=(0, 10), sticky="w")
        
        # Panel lateral (thumbnails)
        sidebar = ttk.LabelFrame(main_frame, text="Imágenes cargadas", padding="5")
        sidebar.grid(row=1, column=0, sticky="ns", padx=(0, 10))
        
        self._thumbnails_canvas = tk.Canvas(sidebar, width=150, highlightthickness=0)
        self._thumbnails_canvas.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(sidebar, orient=tk.VERTICAL, command=self._thumbnails_canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self._thumbnails_canvas.configure(yscrollcommand=scrollbar.set)
        
        self._thumbnails_frame = ttk.Frame(self._thumbnails_canvas)
        self._thumbnails_canvas.create_window((0, 0), window=self._thumbnails_frame, anchor="nw")
        
        # Panel principal (preview)
        preview_frame = ttk.LabelFrame(main_frame, text="Vista previa", padding="5")
        preview_frame.grid(row=1, column=1, sticky="nsew")
        preview_frame.columnconfigure(0, weight=1)
        preview_frame.rowconfigure(0, weight=1)
        
        self._preview_label = ttk.Label(preview_frame, text="No hay imagen seleccionada")
        self._preview_label.grid(row=0, column=0)
        
        # Info panel
        self._info_label = ttk.Label(main_frame, text="")
        self._info_label.grid(row=2, column=0, columnspan=2, pady=(10, 0), sticky="w")
        
        # Botón recargar
        reload_btn = ttk.Button(
            main_frame,
            text="Recargar imágenes",
            command=self._load_default_images
        )
        reload_btn.grid(row=3, column=0, columnspan=2, pady=(10, 0))
    
    def _load_default_images(self) -> None:
        """Carga las imágenes por defecto."""
        summary = self._controller.load_default_images()
        
        if summary["count"] == 0:
            self._preview_label.configure(text="No se encontraron imágenes en data/input/")
            self._info_label.configure(text="Coloca imágenes en la carpeta data/input/")
        else:
            self._info_label.configure(
                text=f"Cargadas {summary['count']} imágenes desde data/input/"
            )
            self._display_thumbnails(summary["images"])
            # Mostrar la primera imagen
            self._show_image(0)
    
    def _display_thumbnails(self, image_infos: List[dict]) -> None:
        """Muestra thumbnails de las imágenes cargadas."""
        # Limpiar thumbnails anteriores
        for widget in self._thumbnails_frame.winfo_children():
            widget.destroy()
        self._thumbnail_refs.clear()
        
        for i, info in enumerate(image_infos):
            image = self._controller.get_image(i)
            if image:
                thumb = self._create_thumbnail(image.data)
                if thumb:
                    self._thumbnail_refs.append(thumb)
                    
                    btn = tk.Button(
                        self._thumbnails_frame,
                        image=thumb,
                        text=info["name"],
                        compound=tk.BOTTOM,
                        command=lambda idx=i: self._show_image(idx)
                    )
                    btn.pack(pady=5)
        
        self._thumbnails_frame.update_idletasks()
        self._thumbnails_canvas.configure(scrollregion=self._thumbnails_canvas.bbox("all"))
    
    def _create_thumbnail(self, image_data: np.ndarray) -> Optional[ImageTk.PhotoImage]:
        """Crea un thumbnail de la imagen."""
        try:
            pil_image = self._numpy_to_pil(image_data)
            pil_image.thumbnail(self.THUMBNAIL_SIZE)
            return ImageTk.PhotoImage(pil_image)
        except Exception:
            return None
    
    def _show_image(self, index: int) -> None:
        """Muestra la imagen seleccionada en el preview."""
        image = self._controller.get_image(index)
        if not image:
            return
        
        try:
            pil_image = self._numpy_to_pil(image.data)
            
            # Redimensionar para el preview manteniendo aspecto
            pil_image.thumbnail(self.PREVIEW_SIZE)
            
            self._current_image_tk = ImageTk.PhotoImage(pil_image)
            self._preview_label.configure(image=self._current_image_tk, text="")
            
            # Actualizar info
            self._info_label.configure(
                text=f"{image.name} | {image.width}x{image.height} | {image.channels} canal(es)"
            )
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo mostrar la imagen: {e}")
    
    def _numpy_to_pil(self, data: np.ndarray) -> PILImage.Image:
        """Convierte array numpy a PIL Image."""
        if len(data.shape) == 2:
            # Escala de grises
            return PILImage.fromarray(data.astype(np.uint8), mode='L')
        elif data.shape[2] == 3:
            # RGB
            return PILImage.fromarray(data.astype(np.uint8), mode='RGB')
        elif data.shape[2] == 4:
            # RGBA
            return PILImage.fromarray(data.astype(np.uint8), mode='RGBA')
        else:
            # Fallback
            return PILImage.fromarray(data.astype(np.uint8))


def main():
    """Punto de entrada de la aplicación GUI."""
    app = TPDIApp()
    app.run()
