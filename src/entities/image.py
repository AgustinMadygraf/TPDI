"""Entidad de dominio para imágenes."""
from dataclasses import dataclass
from typing import Optional
import numpy as np


@dataclass
class Image:
    """Representa una imagen en el dominio."""
    
    name: str
    data: np.ndarray
    path: Optional[str] = None
    
    @property
    def width(self) -> int:
        """Ancho de la imagen en píxeles."""
        return self.data.shape[1]
    
    @property
    def height(self) -> int:
        """Alto de la imagen en píxeles."""
        return self.data.shape[0]
    
    @property
    def channels(self) -> int:
        """Número de canales de color."""
        return 1 if len(self.data.shape) == 2 else self.data.shape[2]
