"""
Path: src/infrastructure/numpy/image_adapter.py
"""

from typing import List, Tuple
import numpy as np
from src.entities.image import Image

class NumPyImageAdapter:
    " Adapter to convert between Image and NumPy array formats."
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

    @staticmethod
    def vstack(arrays: List[np.ndarray]) -> np.ndarray:
        return np.vstack(arrays)

    @staticmethod
    def hstack(arrays: List[np.ndarray]) -> np.ndarray:
        return np.hstack(arrays)

    @staticmethod
    def zeros(shape: Tuple[int, ...], dtype: np.dtype = np.uint8) -> np.ndarray:
        return np.zeros(shape, dtype=dtype)

    @staticmethod
    def resize(data: np.ndarray, size: Tuple[int, int]) -> np.ndarray:
        " Resize an image by cropping or padding to fit the target size."
        target_width, target_height = size
        current_height, current_width = data.shape[:2]
        channels = 1 if len(data.shape) == 2 else data.shape[2]
        if channels == 1:
            result = np.zeros((target_height, target_width), dtype=data.dtype)
        else:
            result = np.zeros((target_height, target_width, channels), dtype=data.dtype)
        y_start = max(0, (target_height - current_height) // 2)
        x_start = max(0, (target_width - current_width) // 2)

        y_src_start = max(0, (current_height - target_height) // 2)
        x_src_start = max(0, (current_width - target_width) // 2)

        copy_height = min(current_height, target_height)
        copy_width = min(current_width, target_width)

        if channels == 1:
            result[y_start:y_start+copy_height, x_start:x_start+copy_width] = \
                data[y_src_start:y_src_start+copy_height, x_src_start:x_src_start+copy_width]
        else:
            result[y_start:y_start+copy_height, x_start:x_start+copy_width, :] = \
                data[y_src_start:y_src_start+copy_height, x_src_start:x_src_start+copy_width, :]

        return result
