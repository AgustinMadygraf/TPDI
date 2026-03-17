"""
Path: src/interface_adapters/controllers/main_controller.py
"""

from pathlib import Path
from typing import Callable, Dict, List, Optional
from src.interface_adapters.presenters.image_presenter import ImagePresenter
from src.use_cases.load_images import ImageLoaderPort, LoadImagesFromDirectory
from src.entities.image import Image


class MainController:
    "Controlador principal que coordina la carga inicial de imágenes."

    DEFAULT_INPUT_DIR = Path("data/input")

    def __init__(
        self,
        image_loader: ImageLoaderPort,
        on_load_error: Optional[Callable[[Path, Exception], None]] = None,
    ):
        "Inicializa el controlador con el puerto de carga de imágenes."
        self._loader = image_loader
        self._use_case = LoadImagesFromDirectory(self._loader, on_error=on_load_error)
        self._presenter = ImagePresenter()
        self._images: List[Image] = []
        self._on_images_loaded: Optional[Callable[[List[Image]], None]] = None

    def set_on_images_loaded_callback(
        self, callback: Callable[[List[Image]], None]
    ) -> None:
        "Registra callback para cuando se carguen imágenes."
        self._on_images_loaded = callback

    def load_default_images(self) -> Dict:
        "Carga las imágenes del directorio por defecto y retorna un resumen para la vista."
        self._images = self._use_case.execute(self.DEFAULT_INPUT_DIR)

        if self._on_images_loaded:
            self._on_images_loaded(self._images)

        return self._presenter.present_summary(self._images)

    def get_images(self) -> List[Image]:
        "Retorna las imágenes cargadas."
        return self._images

    def get_image(self, index: int) -> Optional[Image]:
        "Obtiene una imagen por índice."
        if 0 <= index < len(self._images):
            return self._images[index]
        return None
