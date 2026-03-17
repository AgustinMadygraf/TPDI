"""
Path: src/interface_adapters/gateways/image_gateway.py
"""

from pathlib import Path
from typing import Callable, Optional
from src.use_cases.load_images import ImageLoaderPort, LoadImagesFromDirectory
from src.entities.image import Image

class ImageGateway:
    def __init__(
        self,
        adapter: ImageLoaderPort,
        base_path: Optional[Path] = None,
        on_load_error: Optional[Callable[[Path, Exception], None]] = None
    ):
        self._adapter = adapter
        self._base_path = (base_path or Path("data/input")).resolve()
        self._on_load_error = on_load_error

    def _validate_path(self, path: Path) -> Path:
        "Valida que el path resuelto esté dentro del directorio base permitido."
        resolved = (self._base_path / path).resolve()
        try:
            resolved.relative_to(self._base_path)
        except ValueError as exc:
            raise PermissionError(f"Path no permitido: {path}") from exc
        return resolved

    def load(self, path: Path) -> Image:
        validated_path = self._validate_path(path)
        return self._adapter.load(validated_path)

    def load_all(self) -> list[Image]:
        use_case = LoadImagesFromDirectory(self._adapter, on_error=self._on_load_error)
        return use_case.execute(self._base_path)

    def display(self, image: Image) -> None:
        self._adapter.display(image)
