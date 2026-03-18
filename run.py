"""
Path: run.py
"""

from src.infrastructure.cli.app import CLIApp
from src.infrastructure.opencv.cv2_image_loader import CV2ImageLoader
from src.infrastructure.shared.config import AppConfig, parse_cli_args
from src.infrastructure.shared.path_validator import PathValidator


class AppBootstrap:
    def __init__(self, mode: str | None = None, log_level: str | None = None, gui_backend: str | None = None, input_dir: str | None = None):
        self._mode = mode
        self._log_level = log_level
        self._gui_backend = gui_backend
        self._input_dir = input_dir

    def run(self) -> None:
        config = AppConfig.from_overrides(
            color_mode=self._mode,
            log_level=self._log_level,
            gui_backend=self._gui_backend,
            input_dir=self._input_dir,
        )

        # Crear dependencias
        path_validator = PathValidator(base_path=config.input_dir)
        loader = CV2ImageLoader(path_validator=path_validator)
        displayer = config.create_displayer()

        # Inicializar y ejecutar aplicacion
        app = CLIApp(
            loader,
            displayer,
            None,
            config.color_mode,
        )
        app.run_color_channel_analysis()



def main() -> None:
    "Punto de entrada principal de la aplicacion TPDI."
    args = parse_cli_args()
    AppBootstrap(
        mode=args.mode,
        log_level=args.log_level,
        gui_backend=args.gui_backend,
        input_dir=args.input_dir,
    ).run()


if __name__ == "__main__":
    main()
