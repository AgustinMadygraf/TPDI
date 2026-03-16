"""
Path: src/infrastructure/opencv/cv2_image_adapter.py
"""

from pathlib import Path
import cv2
from src.infrastructure.settings.logger import get_logger
from src.use_cases.load_images import ImageLoaderPort
from src.entities.image import Image

class CV2ImageAdapter(ImageLoaderPort):
    "Implementación del puerto ImageLoader usando OpenCV."
    def __init__(self):
        self._logger = get_logger(__name__)

    def load(self, path: Path) -> Image:
        data = cv2.imread(str(path), cv2.IMREAD_UNCHANGED)

        if data is None:
            raise ValueError(f"No se pudo cargar la imagen: {path}")

        if len(data.shape) == 3 and data.shape[2] >= 3:
            data = cv2.cvtColor(data, cv2.COLOR_BGR2RGB)

        return Image(
            name=path.name,
            data=data,
            path=str(path)
        )

    def display(self, image: Image) -> None:
        if len(image.data.shape) == 3 and image.data.shape[2] == 3:
            display_data = cv2.cvtColor(image.data, cv2.COLOR_RGB2BGR)
        else:
            display_data = image.data

        cv2.imshow(image.name, display_data)
        self._logger.info("Mostrando: %s", image.name)
        self._logger.info("Presiona cualquier tecla para cerrar...")
        cv2.waitKey(0)
        cv2.destroyAllWindows()
