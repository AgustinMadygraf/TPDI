"""
Path: src/entities/image.py
"""

from dataclasses import dataclass
from typing import List, Optional, Tuple


@dataclass
class Image:
    name: str
    width: int
    height: int
    channels: int
    data: List[int]
    path: Optional[str] = None

    @property
    def size(self) -> int:
        return self.width * self.height * self.channels

    def get_pixel(self, x: int, y: int) -> Tuple[int, ...]:
        if not (0 <= x < self.width and 0 <= y < self.height):
            raise ValueError(f"Coordenadas fuera de rango: ({x}, {y})")

        idx = (y * self.width + x) * self.channels
        return tuple(self.data[idx : idx + self.channels])
