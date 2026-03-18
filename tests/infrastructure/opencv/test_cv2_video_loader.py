"""Unit tests for CV2VideoLoader camera handling."""

from unittest.mock import MagicMock, patch

import pytest

from src.infrastructure.opencv.cv2_video_loader import (
    CV2VideoLoader,
    CameraUnavailableError,
)


def test_get_video_stream_raises_camera_unavailable_with_index():
    video_capture = MagicMock()
    video_capture.isOpened.return_value = False

    with patch(
        "src.infrastructure.opencv.cv2_video_loader.cv2.VideoCapture",
        return_value=video_capture,
    ):
        loader = CV2VideoLoader(camera_index=3)
        stream = loader.get_video_stream()

        with pytest.raises(CameraUnavailableError, match="indice 3"):
            next(stream)

    video_capture.release.assert_called_once()


def test_get_video_stream_stops_when_no_frame_is_read():
    video_capture = MagicMock()
    video_capture.isOpened.return_value = True
    video_capture.read.return_value = (False, None)

    with patch(
        "src.infrastructure.opencv.cv2_video_loader.cv2.VideoCapture",
        return_value=video_capture,
    ):
        loader = CV2VideoLoader(camera_index=0)
        stream = loader.get_video_stream()

        with pytest.raises(StopIteration):
            next(stream)

    video_capture.release.assert_called_once()
