"""
Path: src/infrastructure/opencv/cv2_video_loader.py
"""

from typing import Iterator

import cv2

from src.entities.image import Image
from src.use_cases.video_stream import VideoStreamPort


class CameraUnavailableError(RuntimeError):
    """Error cuando la fuente de camara no esta disponible."""


class CV2VideoLoader(VideoStreamPort):
    def __init__(
        self,
        camera_index: int = 0,
        frame_width: int | None = None,
        frame_height: int | None = None,
    ):
        self._camera_index = camera_index
        self._frame_width = frame_width
        self._frame_height = frame_height

    def get_video_stream(self, frame_interval: float = 0.1) -> Iterator[Image]:
        _ = frame_interval  # Mantiene compatibilidad del contrato del puerto.
        cap = cv2.VideoCapture(self._camera_index)
        if not cap.isOpened():
            cap.release()
            raise CameraUnavailableError(
                f"No se pudo abrir la camara en indice {self._camera_index}. "
                "Verifica que exista un dispositivo disponible, permisos de acceso "
                "y prueba con --camera_index=1 (u otro). "
                "Tambien puedes usar --image_source=file."
            )
        self._configure_capture(cap)
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = self._build_image(frame_rgb)
                yield img
        finally:
            cap.release()

    def get_frame(self) -> Image:
        cap = cv2.VideoCapture(self._camera_index)
        if not cap.isOpened():
            cap.release()
            raise CameraUnavailableError(
                f"No se pudo abrir la camara en indice {self._camera_index}. "
                "Verifica que exista un dispositivo disponible, permisos de acceso "
                "y prueba con --camera_index=1 (u otro). "
                "Tambien puedes usar --image_source=file."
            )
        self._configure_capture(cap)
        try:
            ret, frame = cap.read()
            if not ret:
                raise RuntimeError("No se pudo capturar un frame desde la camara.")
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            return self._build_image(frame_rgb)
        finally:
            cap.release()

    def _build_image(self, frame_rgb) -> Image:
        height, width, channels = frame_rgb.shape
        data = frame_rgb.flatten().tolist()
        return Image(
            name="webcam_frame",
            width=width,
            height=height,
            channels=channels,
            data=data,
            path=None,
        )

    def _configure_capture(self, cap) -> None:
        if self._frame_width is not None:
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, self._frame_width)
        if self._frame_height is not None:
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self._frame_height)
