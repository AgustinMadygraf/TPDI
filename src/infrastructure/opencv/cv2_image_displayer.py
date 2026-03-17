"""
Path: src/infrastructure/opencv/cv2_image_displayer.py
"""

import cv2
from src.infrastructure.numpy.image_adapter import NumPyImageAdapter
from src.infrastructure.settings.logger import get_logger
from src.use_cases.display_image import ImageDisplayPort
from src.entities.image import Image

class CV2ImageDisplayer(ImageDisplayPort):
    "Muestra imágenes usando OpenCV."
    def __init__(self):
        "Inicializa el displayer."
        self._logger = get_logger(__name__)
        self._numpy_adapter = NumPyImageAdapter()

    def _prepare_for_display(self, data):
        if len(data.shape) == 2:
            data = cv2.cvtColor(data, cv2.COLOR_GRAY2BGR)
        elif len(data.shape) == 3 and data.shape[2] == 3:
            data = cv2.cvtColor(data, cv2.COLOR_RGB2BGR)
        return data

    def display(self, image: Image, comparison: Image = None, layout: str = "vertical") -> None:
        data = self._numpy_adapter.to_numpy(image)

        if comparison:
            comp_data = self._numpy_adapter.to_numpy(comparison)
            if data.shape[:2] != comp_data.shape[:2]:
                comp_data = self._numpy_adapter.resize(comp_data, (data.shape[1], data.shape[0]))
            data_display = self._prepare_for_display(data)
            comp_display = self._prepare_for_display(comp_data)
            _height = data_display.shape[0]
            width = data_display.shape[1]
            label_height = 30
            label_original = self._numpy_adapter.zeros((label_height, width, 3))
            label_modified = self._numpy_adapter.zeros((label_height, width, 3))

            cv2.putText(label_original, "ORIGINAL", (10, 20),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
            cv2.putText(label_modified, "ESCALA DE GRISES", (10, 20),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
            if layout == "vertical":
                top = self._numpy_adapter.vstack([label_original, data_display])
                bottom = self._numpy_adapter.vstack([label_modified, comp_display])
                display_data = self._numpy_adapter.vstack([top, bottom])
            else:
                left = self._numpy_adapter.vstack([label_original, data_display])
                right = self._numpy_adapter.vstack([label_modified, comp_display])
                display_data = self._numpy_adapter.hstack([left, right])

            cv2.imshow(f"Comparacion: {image.name}", display_data)
            self._logger.info("Mostrando comparacion: %s (%s)", image.name, layout)
        else:
            display_data = self._prepare_for_display(data)
            cv2.imshow(image.name, display_data)
            self._logger.info("Mostrando: %s", image.name)

        self._logger.info("Presiona cualquier tecla para cerrar...")
        cv2.waitKey(0)
        cv2.destroyAllWindows()
