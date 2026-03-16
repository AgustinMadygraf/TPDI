"""Presentador para formatear imágenes para la UI."""
from typing import Dict, List

from src.entities.image import Image


class ImagePresenter:
    """Formatea datos de imagen para presentación."""
    
    def present_summary(self, images: List[Image]) -> Dict:
        """Genera un resumen de las imágenes cargadas."""
        return {
            "count": len(images),
            "images": [
                {
                    "name": img.name,
                    "path": img.path,
                    "width": img.width,
                    "height": img.height,
                    "channels": img.channels,
                }
                for img in images
            ]
        }
    
    def present_for_display(self, image: Image) -> Dict:
        """Prepara una imagen para mostrar en la UI."""
        return {
            "name": image.name,
            "width": image.width,
            "height": image.height,
            "data": image.data,
        }
