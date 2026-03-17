"""
Path: src/use_cases/display_image.py
"""

from typing import Optional, Protocol
from src.entities.image import Image

class ImageDisplayPort(Protocol):
    "Puerto para mostrar imágenes en pantalla."
    def display(
        self,
        image: Image,
        comparison: Optional[Image] = None,
        layout: str = "vertical"
    ) -> None:
        "Muestra una imagen en pantalla, opcionalmente comparándola con otra imagen."
        raise NotImplementedError
