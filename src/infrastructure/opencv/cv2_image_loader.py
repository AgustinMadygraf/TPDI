"""
Path: src/infrastructure/opencv/cv2_image_loader.py
"""

from pathlib import Path
import cv2
from src.infrastructure.numpy.image_adapter import NumPyImageAdapter
from src.infrastructure.settings.path_validator import PathValidator
from src.use_cases.load_images import ImageLoaderPort
from src.entities.image import Image


class CV2ImageLoader(ImageLoaderPort):
    "Carga imágenes usando OpenCV."

    def __init__(self, path_validator: PathValidator):
        self._path_validator = path_validator
        self._numpy_adapter = NumPyImageAdapter()

    def load(self, path: Path) -> Image:
        "Carga una imagen desde el sistema de archivos."
        validated_path = self._path_validator.validate(path)
        data = cv2.imread(str(validated_path), cv2.IMREAD_UNCHANGED)

        if data is None:
            raise ValueError(f"No se pudo cargar la imagen: {validated_path}")

        if len(data.shape) == 3 and data.shape[2] == 4:
            # Normalizar BGRA a RGB para mantener contrato interno de 3 canales.
            data = cv2.cvtColor(data, cv2.COLOR_BGRA2RGB)
        elif len(data.shape) == 3 and data.shape[2] == 3:
            data = cv2.cvtColor(data, cv2.COLOR_BGR2RGB)

        return self._numpy_adapter.from_numpy(
            name=validated_path.name, data=data, path=str(validated_path)
        )
