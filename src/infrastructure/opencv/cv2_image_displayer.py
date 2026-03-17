"""
Path: src/infrastructure/opencv/cv2_image_displayer.py
"""

import cv2

from src.infrastructure.numpy.image_adapter import NumPyImageAdapter
from src.infrastructure.settings.logger import get_logger
from src.use_cases.display_image import ImageDisplayPort
from src.entities.image import Image


class CV2ImageDisplayer(ImageDisplayPort):
    """Muestra imágenes usando OpenCV."""

    def __init__(self):
        """Inicializa el displayer."""
        self._logger = get_logger(__name__)
        self._numpy_adapter = NumPyImageAdapter()

    def display(self, image: Image) -> None:
        """Muestra la imagen en pantalla.

        Args:
            image: La imagen a mostrar.
        """
        data = self._numpy_adapter.to_numpy(image)

        if len(data.shape) == 3 and data.shape[2] == 3:
            display_data = cv2.cvtColor(data, cv2.COLOR_RGB2BGR)
        else:
            display_data = data

        cv2.imshow(image.name, display_data)
        self._logger.info("Mostrando: %s", image.name)
        self._logger.info("Presiona cualquier tecla para cerrar...")
        cv2.waitKey(0)
        cv2.destroyAllWindows()
