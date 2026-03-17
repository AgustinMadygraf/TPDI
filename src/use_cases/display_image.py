"""
Path: src/use_cases/display_image.py
"""

from typing import Protocol

from src.entities.image import Image


class ImageDisplayPort(Protocol):
    """Puerto para mostrar imágenes en pantalla."""

    def display(self, image: Image) -> None:
        """Muestra la imagen en pantalla.

        Args:
            image: La imagen a mostrar.
        """
        raise NotImplementedError
