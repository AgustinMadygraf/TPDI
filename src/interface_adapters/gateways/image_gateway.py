"""
Path: src/interface_adapters/gateways/image_gateway.py
"""

from pathlib import Path
from typing import Callable, Optional

from src.use_cases.load_images import ImageLoaderPort, LoadImagesFromDirectory
from src.entities.image import Image


class ImageGateway:
    """Gateway para operaciones de carga de imágenes."""

    def __init__(
        self,
        loader: ImageLoaderPort,
        base_path: Optional[Path] = None,
        on_load_error: Optional[Callable[[Path, Exception], None]] = None
    ):
        """Inicializa el gateway.

        Args:
            loader: Adaptador para cargar imágenes.
            base_path: Directorio base para carga de imágenes.
            on_load_error: Callback opcional para errores de carga.
        """
        self._loader = loader
        self._base_path = (base_path or Path("data/input")).resolve()
        self._on_load_error = on_load_error

    def load(self, path: Path) -> Image:
        """Carga una imagen desde el path especificado.

        Args:
            path: Ruta de la imagen.

        Returns:
            La imagen cargada.
        """
        return self._loader.load(path)

    def load_all(self) -> list[Image]:
        """Carga todas las imágenes del directorio base.

        Returns:
            Lista de imágenes cargadas.
        """
        use_case = LoadImagesFromDirectory(
            self._loader,
            on_error=self._on_load_error
        )
        return use_case.execute(self._base_path)
