"""
Path: src/interface_adapters/gateways/image_gateway.py
"""

from pathlib import Path
from typing import Callable, Optional, Iterator
from src.use_cases.load_images import ImageLoaderPort, LoadImagesFromDirectory
from src.use_cases.video_stream import VideoStreamPort
from src.entities.image import Image


class _NullVideoStream(VideoStreamPort):
    """Implementacion por defecto para mantener compatibilidad en tests de carga."""

    def get_video_stream(self, frame_interval: float = 0.1) -> Iterator[Image]:
        return iter(())

    def get_frame(self) -> Image:
        raise RuntimeError("Video stream no configurado en ImageGateway.")


class ImageGateway:
    """Gateway para operaciones de carga de imágenes y streaming de video (abstracción)."""

    def __init__(
        self,
        loader: ImageLoaderPort,
        video_streamer: VideoStreamPort | None = None,
        base_path: Optional[Path] = None,
        on_load_error: Optional[Callable[[Path, Exception], None]] = None,
    ):
        self._loader = loader
        self._video_streamer = video_streamer or _NullVideoStream()
        self._base_path = (base_path or Path("data/input")).resolve()
        self._on_load_error = on_load_error

    def load(self, path: Path) -> Image:
        """Carga una imagen desde el path especificado."""
        resolved_path = path if path.is_absolute() else self._base_path / path
        return self._loader.load(resolved_path)

    def get_video_stream(self, frame_interval: float = 0.1) -> Iterator[Image]:
        """Devuelve un generador de frames desde la fuente de video configurada."""
        return self._video_streamer.get_video_stream(frame_interval=frame_interval)

    def get_frame(self) -> Image:
        """Captura un unico frame desde la fuente de video configurada."""
        return self._video_streamer.get_frame()

    def load_all(self) -> list[Image]:
        """Carga todas las imágenes del directorio base.

        Returns:
            Lista de imágenes cargadas.
        """
        use_case = LoadImagesFromDirectory(self._loader, on_error=self._on_load_error)
        return use_case.execute(self._base_path)
