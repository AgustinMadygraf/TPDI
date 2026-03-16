"""
Path: src/entities/image.py
"""

from dataclasses import dataclass
from typing import Optional
import numpy as np


@dataclass
class Image:
    "Entidad que representa una imagen cargada en memoria."
    name: str
    data: np.ndarray
    path: Optional[str] = None

    @property
    def width(self) -> int:
        "Ancho de la imagen en píxeles."
        return self.data.shape[1]

    @property
    def height(self) -> int:
        "Alto de la imagen en píxeles."
        return self.data.shape[0]

    @property
    def channels(self) -> int:
        "Número de canales de color."
        return 1 if len(self.data.shape) == 2 else self.data.shape[2]
