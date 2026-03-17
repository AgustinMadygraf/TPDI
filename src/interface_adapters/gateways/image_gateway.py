"""
Path: src/interface_adapters/gateways/image_gateway.py
"""

from pathlib import Path
from typing import Optional

from src.entities.image import Image
from src.use_cases.load_images import ImageLoaderPort, LoadImagesFromDirectory


class ImageGateway:
    def __init__(
        self,
        adapter: ImageLoaderPort,
        base_path: Optional[Path] = None
    ):
        self._adapter = adapter
        self._base_path = base_path or Path("data/input")

    def load(self, path: Path) -> Image:
        if not path.is_absolute():
            try:
                path.relative_to(self._base_path)
            except ValueError:
                path = self._base_path / path

        return self._adapter.load(path)

    def load_all(self) -> list[Image]:
        use_case = LoadImagesFromDirectory(self._adapter)
        return use_case.execute(self._base_path)

    def display(self, image: Image) -> None:
        self._adapter.display(image)
