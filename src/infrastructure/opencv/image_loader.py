"""Adaptador OpenCV para cargar imágenes."""
from pathlib import Path

import cv2
import numpy as np

from src.entities.image import Image
from src.use_cases.load_images import ImageLoaderPort


class OpenCVImageLoader:
    """Implementación del puerto ImageLoader usando OpenCV."""
    
    def load(self, path: Path) -> Image:
        """
        Carga una imagen usando OpenCV.
        
        Args:
            path: Ruta al archivo de imagen.
            
        Returns:
            Entidad Image con los datos cargados.
            
        Raises:
            ValueError: Si no se puede cargar la imagen.
        """
        # OpenCV usa BGR por defecto, convertimos a RGB
        data = cv2.imread(str(path), cv2.IMREAD_UNCHANGED)
        
        if data is None:
            raise ValueError(f"No se pudo cargar la imagen: {path}")
        
        # Convertir BGR a RGB si es una imagen a color
        if len(data.shape) == 3 and data.shape[2] >= 3:
            data = cv2.cvtColor(data, cv2.COLOR_BGR2RGB)
        
        return Image(
            name=path.name,
            data=data,
            path=str(path)
        )
