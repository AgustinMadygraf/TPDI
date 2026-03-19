"""
Path: src/infrastructure/shared/config.py
"""

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar

from src.use_cases.display_image import ImageDisplayPort

COLOR_MODE_CHOICES: tuple[str, str, str] = ("RGB", "CMY", "CMYK")
GUI_BACKEND_CHOICES: tuple[str, str] = ("cv2", "matplotlib")
LOG_LEVEL_CHOICES: tuple[str, str, str, str, str] = (
    "DEBUG",
    "INFO",
    "WARNING",
    "ERROR",
    "CRITICAL",
)
IMAGE_SOURCE_CHOICES: tuple[str, str] = ("file", "camera")
GRID_CHOICES: tuple[str, str] = ("2x2", "2x3")
CAMERA_MODE_CHOICES: tuple[str, str] = ("snapshot", "stream")

@dataclass(frozen=True)
class AppConfigDefaults:
    gui_backend: str = GUI_BACKEND_CHOICES[0]  # "cv2"
    color_mode: str = COLOR_MODE_CHOICES[2]  # "CMYK"
    input_dir: Path = Path("data/input")
    log_level: str = LOG_LEVEL_CHOICES[0]  # "DEBUG"
    image_source: str = IMAGE_SOURCE_CHOICES[0]  # "file"
    camera_index: int = 0
    fps: float = 10.0
    grid: str = GRID_CHOICES[0]  # "2x2"
    camera_mode: str = CAMERA_MODE_CHOICES[0]  # "snapshot"
    frame_width: int | None = None
    frame_height: int | None = None
    perf_debug: bool = False
    perf_every: int = 30

APP_CONFIG_DEFAULTS = AppConfigDefaults()

DisplayerRegistry = dict[str, type[ImageDisplayPort]]

def parse_cli_args(argv: list[str] | None = None) -> argparse.Namespace:
    normalized_argv = list(argv) if argv is not None else None
    if normalized_argv is not None:
        has_camera_mode = any(
            token == "--camera_mode" or token.startswith("--camera_mode=")
            for token in normalized_argv
        )
        for idx, token in enumerate(normalized_argv):
            if token == "--image_source" and idx + 1 < len(normalized_argv):
                if normalized_argv[idx + 1] == "stream":
                    normalized_argv[idx + 1] = "camera"
                    if not has_camera_mode:
                        normalized_argv.extend(["--camera_mode", "stream"])
                    break
            elif token == "--image_source=stream":
                normalized_argv[idx] = "--image_source=camera"
                if not has_camera_mode:
                    normalized_argv.append("--camera_mode=stream")
                break

    parser = argparse.ArgumentParser(description="TPDI - Analisis de canales de color")
    parser.add_argument(
        "--mode",
        choices=list(COLOR_MODE_CHOICES),
        help="Modo de color para el analisis (si se omite usa el default de config)",
    )
    parser.add_argument(
        "--log_level",
        choices=list(LOG_LEVEL_CHOICES),
        help="Nivel de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
    )
    parser.add_argument(
        "--gui_backend",
        choices=list(GUI_BACKEND_CHOICES),
        help="Backend de GUI para mostrar imagenes (cv2, matplotlib)",
    )
    parser.add_argument(
        "--input_dir",
        type=str,
        help="Directorio de entrada de imagenes",
    )
    parser.add_argument(
        "--image_source",
        choices=list(IMAGE_SOURCE_CHOICES),
        help=(
            "Fuente de imagen: 'file' o 'camera' "
            f"(por defecto: {APP_CONFIG_DEFAULTS.image_source})"
        ),
    )
    parser.add_argument(
        "--camera_index",
        type=int,
        help=(
            "Indice de camara para OpenCV (solo aplica a --image_source=camera, "
            f"por defecto: {APP_CONFIG_DEFAULTS.camera_index})"
        ),
    )
    parser.add_argument(
        "--fps",
        type=float,
        help=(
            "Frames por segundo para captura de camara "
            f"(por defecto: {APP_CONFIG_DEFAULTS.fps})"
        ),
    )
    parser.add_argument(
        "--camera_mode",
        choices=list(CAMERA_MODE_CHOICES),
        help=(
            "Modo de camara: 'snapshot' (1 frame) o 'stream' (continuo) "
            f"(por defecto: {APP_CONFIG_DEFAULTS.camera_mode})"
        ),
    )
    parser.add_argument(
        "--frame_width",
        type=int,
        help="Ancho solicitado para captura de camara en pixeles.",
    )
    parser.add_argument(
        "--frame_height",
        type=int,
        help="Alto solicitado para captura de camara en pixeles.",
    )
    parser.add_argument(
        "--grid",
        choices=list(GRID_CHOICES),
        help=(
            "Layout de grilla para analisis CMYK "
            f"(por defecto: {APP_CONFIG_DEFAULTS.grid})"
        ),
    )
    parser.add_argument(
        "--perf_debug",
        action="store_true",
        help="Habilita metricas de rendimiento en modo stream.",
    )
    parser.add_argument(
        "--perf_every",
        type=int,
        help=(
            "Cantidad de frames entre reportes de rendimiento "
            f"(por defecto: {APP_CONFIG_DEFAULTS.perf_every})"
        ),
    )
    return parser.parse_args(normalized_argv)


@dataclass(frozen=True)
class AppConfig:
    _displayers: ClassVar[dict[str, type[ImageDisplayPort]]] = {}

    gui_backend: str = APP_CONFIG_DEFAULTS.gui_backend
    color_mode: str = APP_CONFIG_DEFAULTS.color_mode
    input_dir: Path = APP_CONFIG_DEFAULTS.input_dir
    log_level: str = APP_CONFIG_DEFAULTS.log_level
    image_source: str = APP_CONFIG_DEFAULTS.image_source
    camera_index: int = APP_CONFIG_DEFAULTS.camera_index
    fps: float = APP_CONFIG_DEFAULTS.fps
    grid: str = APP_CONFIG_DEFAULTS.grid
    camera_mode: str = APP_CONFIG_DEFAULTS.camera_mode
    frame_width: int | None = APP_CONFIG_DEFAULTS.frame_width
    frame_height: int | None = APP_CONFIG_DEFAULTS.frame_height
    perf_debug: bool = APP_CONFIG_DEFAULTS.perf_debug
    perf_every: int = APP_CONFIG_DEFAULTS.perf_every

    def __post_init__(self):
        # Validar que input_dir sea un Path valido.
        if isinstance(self.input_dir, str):
            object.__setattr__(self, "input_dir", Path(self.input_dir))

        # Permite recibir strings (CLI/tests) y normaliza a enum tipado.
        if self.color_mode not in COLOR_MODE_CHOICES:
            valid_modes = ", ".join(COLOR_MODE_CHOICES)
            raise ValueError(
                f"color_mode invalido: '{self.color_mode}'. "
                f"Valores permitidos: {valid_modes}"
            )
        if self.image_source not in IMAGE_SOURCE_CHOICES:
            valid_sources = ", ".join(IMAGE_SOURCE_CHOICES)
            raise ValueError(
                f"image_source invalido: '{self.image_source}'. "
                f"Valores permitidos: {valid_sources}"
            )
        if not isinstance(self.camera_index, int):
            raise ValueError("camera_index invalido: debe ser un entero.")
        if self.camera_index < 0:
            raise ValueError("camera_index invalido: debe ser >= 0.")
        if isinstance(self.fps, bool) or not isinstance(
            self.fps, (int, float)
        ):
            raise ValueError("fps invalido: debe ser un numero.")
        if self.fps <= 0:
            raise ValueError("fps invalido: debe ser > 0.")
        object.__setattr__(self, "fps", float(self.fps))
        if self.grid not in GRID_CHOICES:
            valid_grids = ", ".join(GRID_CHOICES)
            raise ValueError(
                f"grid invalido: '{self.grid}'. Valores permitidos: {valid_grids}"
            )
        if self.camera_mode not in CAMERA_MODE_CHOICES:
            valid_camera_modes = ", ".join(CAMERA_MODE_CHOICES)
            raise ValueError(
                f"camera_mode invalido: '{self.camera_mode}'. "
                f"Valores permitidos: {valid_camera_modes}"
            )
        if self.frame_width is not None and self.frame_width <= 0:
            raise ValueError("frame_width invalido: debe ser > 0.")
        if self.frame_height is not None and self.frame_height <= 0:
            raise ValueError("frame_height invalido: debe ser > 0.")
        if self.perf_every <= 0:
            raise ValueError("perf_every invalido: debe ser > 0.")

    @classmethod
    def register_displayer(
        cls, backend: str, displayer_class: type[ImageDisplayPort]
    ) -> None:
        cls._displayers[backend] = displayer_class

    @classmethod
    def register_displayers(cls, displayers: DisplayerRegistry) -> None:
        for backend, displayer_class in displayers.items():
            cls.register_displayer(backend, displayer_class)

    @classmethod
    def available_backends(cls) -> list[str]:
        # Asegurar que cv2 este registrado para exponer al menos un backend.
        if "cv2" not in cls._displayers:
            try:
                from src.infrastructure.opencv.cv2_image_displayer import CV2ImageDisplayer
                cls.register_displayer("cv2", CV2ImageDisplayer)
            except ImportError:
                pass
        return list(cls._displayers.keys())

    def create_displayer(self) -> ImageDisplayPort:
        backend = self.gui_backend

        if backend not in self._displayers:
            # Lazy loading de displayers built-in.
            if backend == "cv2":
                from src.infrastructure.opencv.cv2_image_displayer import CV2ImageDisplayer
                self.register_displayer("cv2", CV2ImageDisplayer)
            elif backend == "matplotlib":
                raise NotImplementedError(
                    f"Backend '{backend}' no implementado aun. "
                    f"Disponibles: {list(self._displayers.keys()) or ['cv2']}"
                )
            else:
                raise ValueError(
                    f"Backend de GUI desconocido: '{backend}'. "
                    f"Disponibles: {list(self._displayers.keys())}"
                )

        displayer_class = self._displayers[backend]
        return displayer_class()

    @classmethod
    def from_overrides(
        cls,
        gui_backend: str = None,
        color_mode: str = None,
        gui_displayers: DisplayerRegistry = None,
        input_dir: str | Path = None,
        log_level: str = None,
        image_source: str = None,
        camera_index: int = None,
        fps: float = None,
        grid: str = None,
        camera_mode: str = None,
        frame_width: int | None = None,
        frame_height: int | None = None,
        perf_debug: bool | None = None,
        perf_every: int | None = None,
    ) -> "AppConfig":
        kwargs = {}
        if gui_backend is not None:
            kwargs["gui_backend"] = gui_backend
        if color_mode is not None:
            kwargs["color_mode"] = color_mode
        if input_dir is not None:
            kwargs["input_dir"] = input_dir
        if log_level is not None:
            kwargs["log_level"] = log_level
        if image_source is not None:
            kwargs["image_source"] = image_source
        if camera_index is not None:
            kwargs["camera_index"] = camera_index
        if fps is not None:
            kwargs["fps"] = fps
        if grid is not None:
            kwargs["grid"] = grid
        if camera_mode is not None:
            kwargs["camera_mode"] = camera_mode
        if frame_width is not None:
            kwargs["frame_width"] = frame_width
        if frame_height is not None:
            kwargs["frame_height"] = frame_height
        if perf_debug is not None:
            kwargs["perf_debug"] = perf_debug
        if perf_every is not None:
            kwargs["perf_every"] = perf_every

        config = cls(**kwargs)
        if gui_displayers:
            cls.register_displayers(gui_displayers)

        return config
