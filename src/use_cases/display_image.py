"""
Path: src/use_cases/display_image.py
"""

from typing import List, Optional, Protocol, Tuple
from src.entities.image import Image


class ImageDisplayPort(Protocol):
    "Puerto para mostrar imágenes en pantalla."
    def display(
        self,
        image: Image,
        comparison: Optional[Image] = None,
        layout: str = "vertical",
        comparison_labels: Optional[Tuple[str, str]] = None,
    ) -> None:
        "Muestra una imagen, opcionalmente comparándola con otra."
        raise NotImplementedError

    def display_grid(
        self,
        images: List[Tuple[Image, str]],
        grid_size: Tuple[int, int] = (2, 2),
        title: str = "Grid",
    ) -> None:
        "Muestra una cuadrícula de imágenes con sus etiquetas."
        raise NotImplementedError
