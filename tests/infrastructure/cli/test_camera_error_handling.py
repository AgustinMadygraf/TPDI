"""Tests for camera error handling in CLIApp."""

from pathlib import Path
from unittest.mock import MagicMock, patch

from src.infrastructure.cli.app import CLIApp
from src.infrastructure.opencv.cv2_video_loader import CameraUnavailableError
from src.infrastructure.settings.config import AppConfig
from src.entities.image import Image


def _build_app(
    image_source: str = "camera", camera_index: int = 0
) -> tuple[CLIApp, MagicMock, MagicMock]:
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
            logger = MagicMock()
            get_logger.return_value = logger
            app = CLIApp(
                loader=loader,
                displayer=displayer,
                gateway=gateway,
                config=config,
                base_path=Path("data/input"),
                color_mode="RGB",
            )

    return app, gateway, logger


def test_run_color_channel_analysis_handles_camera_unavailable_error():
    app, gateway, logger = _build_app(image_source="camera", camera_index=1)
    gateway.get_frame.side_effect = CameraUnavailableError("camara ocupada")

    result = app.run_color_channel_analysis()

    assert result is False
    logger.error.assert_any_call("No se pudo iniciar la camara.")
    logger.error.assert_any_call("Detalle: %s", "camara ocupada")
    logger.warning.assert_any_call(
        "  2. Prueba otro indice: --image_source=camera --camera_index=1"
    )


def test_run_color_channel_analysis_handles_runtime_error_from_camera():
    app, gateway, logger = _build_app(image_source="camera", camera_index=2)
    gateway.get_frame.side_effect = RuntimeError("fallo de backend de video")

    result = app.run_color_channel_analysis()

    assert result is False
    logger.error.assert_any_call("No se pudo iniciar la camara.")
    logger.error.assert_any_call("Detalle: %s", "fallo de backend de video")
    logger.warning.assert_any_call(
        "  3. Usa archivos: --image_source=file --input_dir=data/input"
    )


def test_run_color_channel_analysis_stream_uses_video_stream():
    app, gateway, _logger = _build_app(image_source="camera", camera_index=0)
    app._config = AppConfig.from_overrides(
        image_source="camera",
        camera_mode="stream",
        fps=20,
        color_mode="RGB",
    )
    frame = Image(
        name="frame",
        width=2,
        height=2,
        channels=3,
        data=[0] * 12,
        path=None,
    )
    gateway.get_video_stream.return_value = iter([frame])

    result = app.run_color_channel_analysis()

    assert result is True
    gateway.get_video_stream.assert_called_once_with(frame_interval=0.05)
    gateway.get_frame.assert_not_called()
