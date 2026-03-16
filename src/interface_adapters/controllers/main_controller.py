"""Controlador principal de la aplicación."""
from pathlib import Path
from typing import Callable, Dict, List, Optional

from src.entities.image import Image
from src.infrastructure.opencv import CV2ImageAdapter
from src.interface_adapters.presenters.image_presenter import ImagePresenter
from src.use_cases.load_images import LoadImagesFromDirectory


class MainController:
    """Controlador principal que coordina la carga inicial de imágenes."""
    
    DEFAULT_INPUT_DIR = Path("data/input")
    
    def __init__(self):
        self._loader = CV2ImageAdapter()
        self._use_case = LoadImagesFromDirectory(self._loader)
        self._presenter = ImagePresenter()
        self._images: List[Image] = []
        self._on_images_loaded: Optional[Callable[[List[Image]], None]] = None
    
    def set_on_images_loaded_callback(self, callback: Callable[[List[Image]], None]) -> None:
        """Registra callback para cuando se carguen imágenes."""
        self._on_images_loaded = callback
    
    def load_default_images(self) -> Dict:
        """
        Carga las imágenes del directorio por defecto.
        
        Returns:
            Resumen de las imágenes cargadas.
        """
        self._images = self._use_case.execute(self.DEFAULT_INPUT_DIR)
        
        if self._on_images_loaded:
            self._on_images_loaded(self._images)
        
        return self._presenter.present_summary(self._images)
    
    def get_images(self) -> List[Image]:
        """Retorna las imágenes cargadas."""
        return self._images
    
    def get_image(self, index: int) -> Optional[Image]:
        """Obtiene una imagen por índice."""
        if 0 <= index < len(self._images):
            return self._images[index]
        return None
