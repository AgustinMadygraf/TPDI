"""
Path: src/use_cases/load_images.py
"""

from pathlib import Path
from typing import Callable, List, Optional, Protocol, Set
from src.entities.image import Image


class ImageLoaderPort(Protocol):
    "Puerto para cargar imágenes desde el sistema de archivos."

    def load(self, path: Path) -> Image:
        "Carga una imagen desde la ruta especificada."
        raise NotImplementedError


class LoadImagesFromDirectory:
    "Caso de uso: Cargar todas las imágenes de un directorio."

    DEFAULT_EXTENSIONS = {
        ".png",
        ".jpg",
        ".jpeg",
        ".bmp",
        ".tiff",
        ".tif",
        ".gif",
        ".webp",
    }

    def __init__(
        self,
        image_loader: ImageLoaderPort,
        supported_extensions: Optional[Set[str]] = None,
        on_error: Optional[Callable[[Path, Exception], None]] = None,
    ):
        self._loader = image_loader
        self._extensions = supported_extensions or self.DEFAULT_EXTENSIONS
        self._on_error = on_error

    def execute(self, directory: Path) -> List[Image]:
        images = []

        resolved_dir = directory.resolve()
        if not resolved_dir.exists():
            return images

        for file_path in sorted(resolved_dir.iterdir()):
            if file_path.is_file() and file_path.suffix.lower() in self._extensions:
                try:
                    image = self._loader.load(file_path)
                    images.append(image)
                except (ValueError, OSError) as exc:
                    if self._on_error:
                        self._on_error(file_path, exc)
        return images
