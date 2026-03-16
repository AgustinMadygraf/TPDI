"""
Path: src/use_cases/load_images.py
"""

from pathlib import Path
from typing import List, Protocol

from src.entities.image import Image

class ImageLoaderPort(Protocol):
    "Puerto para cargar imágenes desde el sistema de archivos."    
    def load(self, path: Path) -> Image:
        """Carga una imagen desde la ruta especificada."""
        raise NotImplementedError

class LoadImagesFromDirectory:
    "Caso de uso: Cargar todas las imágenes de un directorio."
    SUPPORTED_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.tif', '.gif', '.webp'}

    def __init__(self, image_loader: ImageLoaderPort):
        self._loader = image_loader

    def execute(self, directory: Path) -> List[Image]:
        images = []

        if not directory.exists():
            return images

        for file_path in sorted(directory.iterdir()):
            if file_path.is_file() and file_path.suffix.lower() in self.SUPPORTED_EXTENSIONS:
                try:
                    image = self._loader.load(file_path)
                    images.append(image)
                except (ValueError, OSError):
                    # Ignorar archivos que no se puedan cargar
                    pass

        return images
