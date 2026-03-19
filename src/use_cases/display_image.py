"""
Path: src/use_cases/display_image.py
"""

from typing import List, Optional, Protocol, Tuple
from src.entities.image import Image


class ImageDisplayPort(Protocol):
    "Puerto para mostrar imagenes en pantalla."

    def display(
        self,
        image: Image,
        comparison: Optional[Image] = None,
        layout: str = "vertical",
        comparison_labels: Optional[Tuple[str, str]] = None,
    ) -> None:
        "Muestra una imagen, opcionalmente comparandola con otra."
        raise NotImplementedError

    def display_grid(
        self,
        images: List[Tuple[Image, str]],
        grid_size: Tuple[int, int] = (2, 2),
        title: str = "Grid",
        wait_ms: int = 0,
        close_on_exit: bool = True,
        quit_key: str | None = None,
    ) -> bool:
        "Muestra una cuadricula de imagenes con sus etiquetas."
        raise NotImplementedError
