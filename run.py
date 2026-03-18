"""
Path: run.py
"""

from src.infrastructure.cli.app import CLIApp
from src.infrastructure.opencv.cv2_image_loader import CV2ImageLoader
from src.infrastructure.opencv.cv2_video_loader import CV2VideoLoader
from src.infrastructure.shared.config import AppConfig, parse_cli_args
from src.infrastructure.shared.path_validator import PathValidator
from src.interface_adapters.gateways.image_gateway import ImageGateway


class AppBootstrap:
    def __init__(
        self,
        mode: str | None = None,
        log_level: str | None = None,
        gui_backend: str | None = None,
        input_dir: str | None = None,
        image_source: str | None = None,
        camera_index: int | None = None,
        fps: float | None = None,
    ):
        self._mode = mode
        self._log_level = log_level
        self._gui_backend = gui_backend
        self._input_dir = input_dir
        self._image_source = image_source
        self._camera_index = camera_index
        self._fps = fps

    def run(self) -> bool:
        config = AppConfig.from_overrides(
            color_mode=self._mode,
            log_level=self._log_level,
            gui_backend=self._gui_backend,
            input_dir=self._input_dir,
            image_source=self._image_source,
            camera_index=self._camera_index,
            fps=self._fps,
        )

        # Crear dependencias
        path_validator = PathValidator(base_path=config.input_dir)
        loader = CV2ImageLoader(path_validator=path_validator)
        displayer = config.create_displayer()

        # Inicializar gateway con ambos loaders
        video_loader = CV2VideoLoader(camera_index=config.camera_index)
        gateway = ImageGateway(
            loader=loader,
            video_streamer=video_loader,
            base_path=config.input_dir,
        )

        # Inicializar y ejecutar aplicacion
        app = CLIApp(
            loader=loader,
            displayer=displayer,
            gateway=gateway,
            config=config,
            base_path=config.input_dir,
            color_mode=config.color_mode,
        )
        return app.run_color_channel_analysis()



def main() -> None:
    """Punto de entrada principal de la aplicacion TPDI."""
    args = parse_cli_args()
    success = AppBootstrap(
        mode=args.mode,
        log_level=args.log_level,
        gui_backend=args.gui_backend,
        input_dir=args.input_dir,
        image_source=args.image_source,
        camera_index=args.camera_index,
        fps=args.fps,
    ).run()
    raise SystemExit(0 if success else 1)

if __name__ == "__main__":
    main()
