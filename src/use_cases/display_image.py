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
        layout: str = "vertical"
    ) -> None:
        """Muestra la imagen en pantalla.

        Args:
            image: Imagen principal a mostrar.
            comparison: Imagen opcional para comparación lado a lado.
            layout: "vertical" (una sobre otra) o "horizontal" (lado a lado).
        """
        raise NotImplementedError

    def display_grid(
        self,
        images: List[Tuple[Image, str]],
        grid_size: Tuple[int, int] = (2, 2),
        title: str = "Grid"
    ) -> None:
        """Muestra múltiples imágenes en una cuadrícula.

        Args:
            images: Lista de tuplas (imagen, etiqueta).
            grid_size: Tupla (filas, columnas) para el grid.
            title: Título de la ventana.
        """
        raise NotImplementedError
