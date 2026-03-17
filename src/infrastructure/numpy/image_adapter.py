"""
Path: src/infrastructure/numpy/image_adapter.py
"""

import numpy as np
from src.entities.image import Image

class NumPyImageAdapter:
    @staticmethod
    def to_numpy(image: "Image") -> np.ndarray:
        if image.channels == 1:
            shape = (image.height, image.width)
        else:
            shape = (image.height, image.width, image.channels)

        return np.array(image.data, dtype=np.uint8).reshape(shape)

    @staticmethod
    def from_numpy(name: str, data: np.ndarray, path: str = None) -> "Image":

        height, width = data.shape[:2]
        channels = 1 if len(data.shape) == 2 else data.shape[2]

        flat_data = data.flatten().tolist()

        return Image(
            name=name,
            width=width,
            height=height,
            channels=channels,
            data=flat_data,
            path=path
        )
