"""
Path: src/interface_adapters/gateways/image_gateway.py
"""

from pathlib import Path
from typing import Callable, Optional, Iterator
from src.use_cases.load_images import ImageLoaderPort, LoadImagesFromDirectory
from src.use_cases.video_stream import VideoStreamPort
from src.entities.image import Image

class ImageGateway:
    """Gateway para operaciones de carga de imágenes y streaming de video (abstracción)."""

    def __init__(
        self,
        loader: ImageLoaderPort,
        video_streamer: VideoStreamPort,
        base_path: Optional[Path] = None,
        on_load_error: Optional[Callable[[Path, Exception], None]] = None,
    ):
        self._loader = loader
        self._video_streamer = video_streamer
        self._base_path = (base_path or Path("data/input")).resolve()
        self._on_load_error = on_load_error

    def load(self, path: Path) -> Image:
        """Carga una imagen desde el path especificado."""
        # ...existing code...

    def get_video_stream(self, frame_interval: float = 0.1) -> Iterator[Image]:
        """Devuelve un generador de frames desde la fuente de video configurada."""
        return self._video_streamer.get_video_stream(frame_interval=frame_interval)

    def load_all(self) -> list[Image]:
        """Carga todas las imágenes del directorio base.

        Returns:
            Lista de imágenes cargadas.
        """
        use_case = LoadImagesFromDirectory(self._loader, on_error=self._on_load_error)
        return use_case.execute(self._base_path)
