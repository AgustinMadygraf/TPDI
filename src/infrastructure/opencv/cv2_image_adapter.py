"""
Path: src/infrastructure/opencv/cv2_image_adapter.py
"""

from pathlib import Path
from typing import Optional
import cv2
from src.infrastructure.numpy.image_adapter import NumPyImageAdapter
from src.infrastructure.settings.logger import get_logger
from src.use_cases.load_images import ImageLoaderPort
from src.entities.image import Image


class CV2ImageAdapter(ImageLoaderPort):
    def __init__(self, base_path: Optional[Path] = None):
        self._logger = get_logger(__name__)
        self._numpy_adapter = NumPyImageAdapter()
        self._base_path = base_path.resolve() if base_path else Path("data/input").resolve()

    def _validate_path(self, path: Path) -> Path:
        "Valida que el path resuelto esté dentro del directorio base permitido."
        resolved = (self._base_path / path).resolve() if not path.is_absolute() else path.resolve()
        try:
            resolved.relative_to(self._base_path)
        except ValueError as exc:
            raise PermissionError(f"Path no permitido: {path}") from exc
        return resolved

    def load(self, path: Path) -> Image:
        validated_path = self._validate_path(path)
        data = cv2.imread(str(validated_path), cv2.IMREAD_UNCHANGED)

        if data is None:
            raise ValueError(f"No se pudo cargar la imagen: {validated_path}")
        if len(data.shape) == 3 and data.shape[2] >= 3:
            data = cv2.cvtColor(data, cv2.COLOR_BGR2RGB)
        return self._numpy_adapter.from_numpy(
            name=validated_path.name,
            data=data,
            path=str(validated_path)
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
