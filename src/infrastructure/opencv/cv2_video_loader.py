"""
Path: src/infrastructure/opencv/cv2_video_loader.py
"""

import time
import cv2
from typing import Iterator
from src.use_cases.video_stream import VideoStreamPort
from src.entities.image import Image

class CV2VideoLoader(VideoStreamPort):
    def get_video_stream(self, frame_interval: float = 0.1) -> Iterator[Image]:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            raise RuntimeError("No se pudo abrir la cámara predeterminada.")
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                height, width, channels = frame_rgb.shape
                data = frame_rgb.flatten().tolist()
                img = Image(
                    name="webcam_frame",
                    width=width,
                    height=height,
                    channels=channels,
                    data=data,
                    path=None,
                )
                yield img
                time.sleep(frame_interval)
        finally:
            cap.release()
