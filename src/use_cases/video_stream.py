"""
Path: src/use_cases/video_stream.py
"""

from typing import Iterator, Protocol
from src.entities.image import Image

class VideoStreamPort(Protocol):
    def get_video_stream(self, frame_interval: float = 0.1) -> Iterator[Image]:
        "Devuelve un generador de objetos Image capturados desde una fuente de video (e.g., webcam)."

    def get_frame(self) -> Image:
        "Captura un unico frame y lo devuelve como Image."
