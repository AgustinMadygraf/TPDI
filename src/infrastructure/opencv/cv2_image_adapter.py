"""
Path: src/infrastructure/opencv/cv2_image_adapter.py
"""

from pathlib import Path
import cv2
from src.infrastructure.numpy.image_adapter import NumPyImageAdapter
from src.infrastructure.settings.logger import get_logger
from src.use_cases.load_images import ImageLoaderPort
from src.entities.image import Image


class CV2ImageAdapter(ImageLoaderPort):
    def __init__(self):
        self._logger = get_logger(__name__)
        self._numpy_adapter = NumPyImageAdapter()

    def load(self, path: Path) -> Image:
        data = cv2.imread(str(path), cv2.IMREAD_UNCHANGED)

        if data is None:
            raise ValueError(f"No se pudo cargar la imagen: {path}")
        if len(data.shape) == 3 and data.shape[2] >= 3:
            data = cv2.cvtColor(data, cv2.COLOR_BGR2RGB)
        return self._numpy_adapter.from_numpy(
            name=path.name,
            data=data,
            path=str(path)
        )

    def display(self, image: Image) -> None:
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
