"""Tests for camera error handling in CLIApp."""

from pathlib import Path
from unittest.mock import MagicMock, patch

from src.infrastructure.cli.app import CLIApp
from src.infrastructure.opencv.cv2_video_loader import CameraUnavailableError
from src.infrastructure.shared.config import AppConfig


def _build_app(
    image_source: str = "camera", camera_index: int = 0
) -> tuple[CLIApp, MagicMock]:
    loader = MagicMock()
    displayer = MagicMock()
    gateway = MagicMock()
    config = AppConfig.from_overrides(
        image_source=image_source,
        camera_index=camera_index,
        color_mode="RGB",
    )

    with patch("src.infrastructure.cli.app.setup_logging"):
        with patch("src.infrastructure.cli.app.get_logger") as get_logger:
            get_logger.return_value = MagicMock()
            app = CLIApp(
                loader=loader,
                displayer=displayer,
                gateway=gateway,
                config=config,
                base_path=Path("data/input"),
                color_mode="RGB",
            )

    return app, gateway


def test_run_color_channel_analysis_handles_camera_unavailable_error(capsys):
    app, gateway = _build_app(image_source="camera", camera_index=1)

    def _failing_stream():
        raise CameraUnavailableError("camara ocupada")
        yield  # pragma: no cover

    gateway.get_video_stream.return_value = _failing_stream()

    result = app.run_color_channel_analysis()
    captured = capsys.readouterr()

    assert result is False
    assert "ERROR: No se pudo iniciar la camara." in captured.out
    assert "camara ocupada" in captured.out
    assert "--camera_index=1" in captured.out


def test_run_color_channel_analysis_handles_runtime_error_from_camera(capsys):
    app, gateway = _build_app(image_source="camera", camera_index=2)

    def _runtime_error_stream():
        raise RuntimeError("fallo de backend de video")
        yield  # pragma: no cover

    gateway.get_video_stream.return_value = _runtime_error_stream()

    result = app.run_color_channel_analysis()
    captured = capsys.readouterr()

    assert result is False
    assert "ERROR: No se pudo iniciar la camara." in captured.out
    assert "fallo de backend de video" in captured.out
    assert "--image_source=file" in captured.out
