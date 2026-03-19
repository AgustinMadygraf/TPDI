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
        grid: str | None = None,
        camera_mode: str | None = None,
        frame_width: int | None = None,
        frame_height: int | None = None,
        perf_debug: bool | None = None,
        perf_every: int | None = None,
    ):
        self._mode = mode
        self._log_level = log_level
        self._gui_backend = gui_backend
        self._input_dir = input_dir
        self._image_source = image_source
        self._camera_index = camera_index
        self._fps = fps
        self._grid = grid
        self._camera_mode = camera_mode
        self._frame_width = frame_width
        self._frame_height = frame_height
        self._perf_debug = perf_debug
        self._perf_every = perf_every

    def run(self) -> bool:
        config = AppConfig.from_overrides(
            color_mode=self._mode,
            log_level=self._log_level,
            gui_backend=self._gui_backend,
            input_dir=self._input_dir,
            image_source=self._image_source,
            camera_index=self._camera_index,
            fps=self._fps,
            grid=self._grid,
            camera_mode=self._camera_mode,
            frame_width=self._frame_width,
            frame_height=self._frame_height,
            perf_debug=self._perf_debug,
            perf_every=self._perf_every,
        )

        # Crear dependencias
        path_validator = PathValidator(base_path=config.input_dir)
        loader = CV2ImageLoader(path_validator=path_validator)
        displayer = config.create_displayer()

        # Inicializar gateway con ambos loaders
        video_loader = CV2VideoLoader(
            camera_index=config.camera_index,
            frame_width=config.frame_width,
            frame_height=config.frame_height,
        )
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
    try:
        success = AppBootstrap(
            mode=args.mode,
            log_level=args.log_level,
            gui_backend=args.gui_backend,
            input_dir=args.input_dir,
            image_source=args.image_source,
            camera_index=args.camera_index,
            fps=args.fps,
            grid=args.grid,
            camera_mode=args.camera_mode,
            frame_width=args.frame_width,
            frame_height=args.frame_height,
            perf_debug=args.perf_debug,
            perf_every=args.perf_every,
        ).run()
    except KeyboardInterrupt:
        print()
        print("Interrumpido por usuario.")
        raise SystemExit(130)
    raise SystemExit(0 if success else 1)

if __name__ == "__main__":
    main()
