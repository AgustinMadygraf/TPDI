"""
Path: src/infrastructure/shared/config.py
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import ClassVar, Literal

from src.use_cases.display_image import ImageDisplayPort
from src.use_cases.color_separation import (
    FlexoSpotPalette,
    default_flexo_spot_palettes,
)


ColorMode = Literal["RGB", "CMY", "CMYK"]
DisplayerRegistry = dict[str, type[ImageDisplayPort]]


@dataclass(frozen=True)
class AppConfig:
    _displayers: ClassVar[dict[str, type[ImageDisplayPort]]] = {}

    GUI_BACKEND: str = "cv2"
    COLOR_MODE: ColorMode = "RGB"
    CMYK_DOT_GAIN: float = 0.0
    CMYK_TOTAL_INK_LIMIT: int = 1020
    FLEXO_ACTIVE_PALETTE: str = "CYAN_MAGENTA"
    FLEXO_SPOT_PALETTES: dict[str, FlexoSpotPalette] = field(
        default_factory=default_flexo_spot_palettes
    )
    INPUT_DIR: Path = field(default_factory=lambda: Path("data/input"))
    LOG_LEVEL: str = "INFO"

    def __post_init__(self):
        # Validar que INPUT_DIR sea un Path válido
        if isinstance(self.INPUT_DIR, str):
            object.__setattr__(self, "INPUT_DIR", Path(self.INPUT_DIR))

        if not (0.0 <= self.CMYK_DOT_GAIN <= 1.0):
            raise ValueError("CMYK_DOT_GAIN debe estar entre 0.0 y 1.0")

        if not (0 < self.CMYK_TOTAL_INK_LIMIT <= 1020):
            raise ValueError(
                "CMYK_TOTAL_INK_LIMIT debe estar entre 1 y 1020"
            )

        if not self.FLEXO_SPOT_PALETTES:
            raise ValueError("FLEXO_SPOT_PALETTES no puede estar vacio")

        if self.FLEXO_ACTIVE_PALETTE not in self.FLEXO_SPOT_PALETTES:
            raise ValueError(
                "FLEXO_ACTIVE_PALETTE debe existir en FLEXO_SPOT_PALETTES"
            )

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
                from src.infrastructure.opencv.cv2_image_displayer import (
                    CV2ImageDisplayer,
                )

                cls.register_displayer("cv2", CV2ImageDisplayer)
            except ImportError:
                pass
        return list(cls._displayers.keys())

    def create_displayer(self) -> ImageDisplayPort:
        backend = self.GUI_BACKEND

        if backend not in self._displayers:
            # Lazy loading de displayers built-in.
            if backend == "cv2":
                from src.infrastructure.opencv.cv2_image_displayer import (
                    CV2ImageDisplayer,
                )

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


def load_config(
    gui_backend: str = None,
    color_mode: ColorMode = None,
    cmyk_dot_gain: float = None,
    cmyk_total_ink_limit: int = None,
    flexo_active_palette: str = None,
    flexo_spot_palettes: dict[str, FlexoSpotPalette] = None,
    gui_displayers: DisplayerRegistry = None,
    input_dir: str | Path = None,
    log_level: str = None,
) -> AppConfig:
    kwargs = {}
    if gui_backend is not None:
        kwargs["GUI_BACKEND"] = gui_backend
    if color_mode is not None:
        kwargs["COLOR_MODE"] = color_mode
    if cmyk_dot_gain is not None:
        kwargs["CMYK_DOT_GAIN"] = cmyk_dot_gain
    if cmyk_total_ink_limit is not None:
        kwargs["CMYK_TOTAL_INK_LIMIT"] = cmyk_total_ink_limit
    if flexo_active_palette is not None:
        kwargs["FLEXO_ACTIVE_PALETTE"] = flexo_active_palette
    if flexo_spot_palettes is not None:
        kwargs["FLEXO_SPOT_PALETTES"] = flexo_spot_palettes
    if input_dir is not None:
        kwargs["INPUT_DIR"] = input_dir
    if log_level is not None:
        kwargs["LOG_LEVEL"] = log_level

    config = AppConfig(**kwargs)
    if gui_displayers:
        AppConfig.register_displayers(gui_displayers)

    return config
