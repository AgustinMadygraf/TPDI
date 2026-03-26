"""
Path: src/infrastructure/cli/app.py
"""

from pathlib import Path
import math
import sys
import time
from types import SimpleNamespace
from typing import List

from src.entities.image import Image
from src.infrastructure.cli.analysis_reporter import ColorAnalysisConsoleReporter
from src.infrastructure.opencv.cv2_image_loader import CV2ImageLoader
from src.infrastructure.opencv.cv2_video_loader import (
    CV2VideoLoader,
    CameraUnavailableError,
)
from src.infrastructure.settings.path_validator import PathValidator
from src.infrastructure.settings.logger import setup_logging, get_logger
from src.interface_adapters.presenters.analysis_grid_presenter import AnalysisGridPresenter
from src.use_cases.color_analysis import (
    ColorAnalysisResult,
    ColorChannelAnalyzer,
    ColorMode,
)
from src.use_cases.color_separation import GenericCmykSeparationPolicy
from src.use_cases.display_image import ImageDisplayPort
from src.use_cases.load_images import ImageLoaderPort, LoadImagesFromDirectory

from src.interface_adapters.gateways.image_gateway import ImageGateway
from src.infrastructure.settings.config import AppConfig, parse_cli_args

DEFAULT_INPUT_DIR = Path("data/input")


class CLIApp:
    "Aplicación de línea de comandos para TPDI."

    def __init__(
        self,
        loader: ImageLoaderPort,
        displayer: ImageDisplayPort,
        gateway: ImageGateway | None = None,
        config: AppConfig | None = None,
        base_path: Path = None,
        color_mode: ColorMode = "RGB",
    ):
        setup_logging(name="tpdi")
        self._logger = get_logger("tpdi.cli")
        self._displayer = displayer
        self._loader = loader
        self._gateway = gateway or SimpleNamespace(
            get_video_stream=lambda frame_interval: iter(()),
            get_frame=lambda: None,
        )
        self._config = config or AppConfig.from_overrides(
            color_mode=color_mode
        )
        self._base_path = base_path or DEFAULT_INPUT_DIR
        self._color_mode = color_mode
        cmyk_policy = GenericCmykSeparationPolicy()
        self._color_analyzer = ColorChannelAnalyzer(
            cmyk_policy=cmyk_policy
        )
        self._analysis_reporter = ColorAnalysisConsoleReporter(
            color_mode=self._color_mode,
            cmyk_policy=cmyk_policy,
        )
        self._grid_presenter = AnalysisGridPresenter()

    def _on_load_error(self, path: Path, exc: Exception) -> None:
        "Callback para manejar errores de carga de imágenes."
        self._logger.warning("No se pudo cargar imagen %s: %s", path, exc)

    def load_images(self) -> List[Image]:
        "Carga todas las imágenes del directorio base."
        use_case = LoadImagesFromDirectory(self._loader, on_error=self._on_load_error)
        return use_case.execute(self._base_path)

    def run_color_channel_analysis(self) -> bool:
        "Ejecuta analisis de canales de color con layout segun modo."
        self._print_analysis_header()
        self._logger.info("Fuente de imagen activa: %s", self._config.image_source)
        if self._config.image_source == "camera":
            self._logger.info("Modo de camara activo: %s", self._config.camera_mode)

        if self._config.image_source == "camera" and self._config.camera_mode == "stream":
            return self._run_camera_stream_analysis()

        original = self._load_original_image_for_analysis()
        if original is None:
            return False

        analysis = self._process_color_variants(original)

        self._display_grid_2x4(original, analysis)

        self._print_app_finished()
        return True

    def _print_analysis_header(self) -> None:
        self._logger.info("=" * 60)
        self._logger.info("TPDI - Analisis de Canales de Color")
        self._logger.info("=" * 60)

    def _print_app_finished(self) -> None:
        self._logger.info("=" * 60)
        self._logger.info("Aplicacion finalizada.")
        self._logger.info("=" * 60)

    def _load_original_image_for_analysis(self) -> Image | None:
        if self._config.image_source == "camera":
            return self._load_original_from_camera()
        return self._load_original_from_files()

    def _load_original_from_camera(self) -> Image | None:
        self._logger.info(
            "Capturando imagen desde camara... "
            f"(indice: {self._config.camera_index})"
        )
        try:
            original = self._gateway.get_frame()
        except (CameraUnavailableError, RuntimeError) as exc:
            self._print_camera_unavailable_help(exc)
            return None

        if original is None:
            self._logger.error("No se pudo capturar imagen de la camara.")
            return None

        self._logger.info("Imagen capturada: %s", original.name)
        self._logger.info("  Dimensiones: %dx%d", original.width, original.height)
        self._logger.info("  Canales: %d", original.channels)
        return original

    def _load_original_from_files(self) -> Image | None:
        self._logger.info("Cargando imagenes desde: %s", self._base_path)
        images = self.load_images()
        if not images:
            self._logger.error("No se encontraron imagenes en: %s", self._base_path)
            self._logger.warning("Agrega imagenes PNG/JPG a la carpeta data/input/")
            return None

        self._logger.info("Cargadas %d imagen(es)", len(images))
        original = images[0]
        self._logger.info("Imagen seleccionada: %s", original.name)
        self._logger.info("  Dimensiones: %dx%d", original.width, original.height)
        self._logger.info("  Canales: %d", original.channels)
        return original

    def _run_camera_stream_analysis(self) -> bool:
        """Ejecuta analisis continuo desde camara hasta que el usuario presione 'q'."""
        frame_interval = 1.0 / self._config.fps
        self._logger.info(
            "Iniciando stream de camara... "
            f"(indice: {self._config.camera_index}, fps_objetivo: {self._config.fps:.2f})"
        )
        self._logger.info("Presiona 'q' en la ventana para salir del stream.")

        processed_frames = 0
        capture_ms_acc = 0.0
        analysis_ms_acc = 0.0
        render_ms_acc = 0.0
        loop_ms_acc = 0.0
        loop_window: list[float] = []
        try:
            stream = iter(self._gateway.get_video_stream(frame_interval=frame_interval))
            while True:
                loop_start = time.perf_counter()
                capture_start = time.perf_counter()
                try:
                    original = next(stream)
                except StopIteration:
                    break
                capture_ms = (time.perf_counter() - capture_start) * 1000.0

                analysis_start = time.perf_counter()
                include_grayscale_variant = not (
                    self._color_mode == "CMYK" and self._config.grid == "2x2"
                )
                analysis = self._color_analyzer.execute(
                    original,
                    self._color_mode,
                    include_grayscale_variant=include_grayscale_variant,
                )
                analysis_ms = (time.perf_counter() - analysis_start) * 1000.0

                render_start = time.perf_counter()
                should_continue = self._display_grid_2x4(
                    original,
                    analysis,
                    show_console_output=False,
                    wait_ms=10,
                    close_on_exit=False,
                )
                render_ms = (time.perf_counter() - render_start) * 1000.0

                loop_ms = (time.perf_counter() - loop_start) * 1000.0
                processed_frames += 1
                capture_ms_acc += capture_ms
                analysis_ms_acc += analysis_ms
                render_ms_acc += render_ms
                loop_ms_acc += loop_ms
                loop_window.append(loop_ms)

                if self._config.perf_debug and processed_frames % self._config.perf_every == 0:
                    self._print_perf_report(
                        processed_frames=processed_frames,
                        capture_ms_acc=capture_ms_acc,
                        analysis_ms_acc=analysis_ms_acc,
                        render_ms_acc=render_ms_acc,
                        loop_ms_acc=loop_ms_acc,
                        loop_window=loop_window,
                    )
                    loop_window.clear()

                if not should_continue:
                    break
        except (CameraUnavailableError, RuntimeError) as exc:
            self._print_camera_unavailable_help(exc)
            return False
        finally:
            close_windows = getattr(self._displayer, "close_windows", None)
            if callable(close_windows):
                close_windows()

        if processed_frames == 0:
            self._logger.error("No se pudo capturar imagen de la camara.")
            return False

        self._logger.info("Stream finalizado. Frames procesados: %d", processed_frames)
        self._print_app_finished()
        return True

    def _print_perf_report(
        self,
        processed_frames: int,
        capture_ms_acc: float,
        analysis_ms_acc: float,
        render_ms_acc: float,
        loop_ms_acc: float,
        loop_window: list[float],
    ) -> None:
        """Imprime metricas agregadas de rendimiento para stream."""
        if processed_frames <= 0:
            return
        avg_capture_ms = capture_ms_acc / processed_frames
        avg_analysis_ms = analysis_ms_acc / processed_frames
        avg_render_ms = render_ms_acc / processed_frames
        avg_loop_ms = loop_ms_acc / processed_frames
        effective_fps = 1000.0 / avg_loop_ms if avg_loop_ms > 0 else 0.0

        p95_loop_ms = avg_loop_ms
        if loop_window:
            sorted_window = sorted(loop_window)
            idx = max(0, math.ceil(len(sorted_window) * 0.95) - 1)
            p95_loop_ms = sorted_window[idx]

        self._logger.info(
            "[PERF] "
            f"frames={processed_frames} "
            f"avg_capture={avg_capture_ms:.2f}ms "
            f"avg_analysis={avg_analysis_ms:.2f}ms "
            f"avg_render={avg_render_ms:.2f}ms "
            f"avg_loop={avg_loop_ms:.2f}ms "
            f"p95_loop={p95_loop_ms:.2f}ms "
            f"fps_efectivo={effective_fps:.2f}"
        )

    def _print_camera_unavailable_help(self, exc: Exception) -> None:
        "Muestra un error de camara con pasos concretos para recuperarse."
        self._logger.error("No se pudo iniciar la camara.")
        self._logger.error("Detalle: %s", str(exc))
        self._logger.warning("Sugerencias:")
        self._logger.warning("  1. Verifica que la camara este conectada y libre.")
        self._logger.warning("  2. Prueba otro indice: --image_source=camera --camera_index=1")
        self._logger.warning("  3. Usa archivos: --image_source=file --input_dir=data/input")
    def _process_color_variants(self, original: Image) -> ColorAnalysisResult:
        "Construye el analisis configurable y muestra depuracion en consola."
        analysis = self._color_analyzer.execute(original, self._color_mode)
        self._analysis_reporter.report(original, analysis)
        return analysis

    def _display_grid_2x4(
        self,
        original: Image,
        analysis: ColorAnalysisResult,
        show_console_output: bool = True,
        wait_ms: int = 0,
        close_on_exit: bool = True,
    ) -> bool:
        """Muestra un grid de analisis con tamano dinamico segun variantes."""
        presentation = self._grid_presenter.present(
            original=original,
            analysis=analysis,
            grid=self._config.grid,
        )

        if show_console_output:
            self._logger.info("Mostrando grid de analisis %s:", presentation.layout_label)
            for idx, row_items in enumerate(presentation.row_labels):
                if row_items:
                    self._logger.info("  [FILA %d] %s", idx + 1, " | ".join(row_items))

        if show_console_output:
            self._logger.info("Presiona cualquier tecla en la ventana para cerrar...")

        display_result = self._displayer.display_grid(
            images=presentation.images,
            grid_size=presentation.grid_size,
            title=presentation.title,
            wait_ms=wait_ms,
            close_on_exit=close_on_exit,
            quit_key="q",
        )
        return True if display_result is None else bool(display_result)
    def run(self) -> None:
        """Ejecuta la aplicación CLI estándar (carga y muestra imágenes)."""
        self._logger.info("=" * 50)
        self._logger.info("TPDI - Procesamiento Digital de Imagenes")
        self._logger.info("=" * 50)

        self._logger.info("Cargando imagenes desde: %s", self._base_path)
        images = self.load_images()

        if not images:
            self._logger.warning("No se encontraron imagenes en: %s", self._base_path)
            return

        self._logger.info("Cargadas %d imagen(es)", len(images))

        for img in images:
            self._logger.info(
                "  [%s] %dx%d px, %d canal(es)",
                img.name,
                img.width,
                img.height,
                img.channels,
            )

        # Mostrar primera imagen
        if images:
            self._display_image(images[0])

        self._logger.info("Visor cerrado. Aplicacion finalizada.")

    def _display_image(self, image: Image) -> None:
        """Muestra una imagen usando el displayer."""
        self._logger.info("Mostrando imagen: %s", image.name)
        self._displayer.display(image)


def bootstrap_and_run_color_channel_analysis(
    *,
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
) -> bool:
    """Construye dependencias y ejecuta el flujo principal de analisis."""
    config = AppConfig.from_overrides(
        color_mode=mode,
        log_level=log_level,
        gui_backend=gui_backend,
        input_dir=input_dir,
        image_source=image_source,
        camera_index=camera_index,
        fps=fps,
        grid=grid,
        camera_mode=camera_mode,
        frame_width=frame_width,
        frame_height=frame_height,
        perf_debug=perf_debug,
        perf_every=perf_every,
    )

    path_validator = PathValidator(base_path=config.input_dir)
    loader = CV2ImageLoader(path_validator=path_validator)
    displayer = config.create_displayer()
    frame_width = config.frame_width
    frame_height = config.frame_height
    if config.image_source == "camera" and config.camera_mode == "stream":
        if frame_width is None and frame_height is None:
            frame_width = 320
            frame_height = 240
            get_logger("tpdi.cli").info(
                "Stream sin resolucion explicita; usando 320x240 para mejorar FPS. "
                "Override: --frame_width --frame_height"
            )
    video_loader = CV2VideoLoader(
        camera_index=config.camera_index,
        frame_width=frame_width,
        frame_height=frame_height,
    )
    gateway = ImageGateway(
        loader=loader,
        video_streamer=video_loader,
        base_path=config.input_dir,
    )

    app = CLIApp(
        loader=loader,
        displayer=displayer,
        gateway=gateway,
        config=config,
        base_path=config.input_dir,
        color_mode=config.color_mode,
    )
    return app.run_color_channel_analysis()


def _resolve_image_source(cli_value: str | None) -> str | None:
    """Resuelve la fuente de imagen desde CLI o con selector interactivo."""
    if cli_value in {"file", "camera"}:
        return cli_value

    if not sys.stdin.isatty():
        return None

    logger = get_logger("tpdi.cli")
    logger.info("Selecciona la fuente de imagen:")
    logger.info("  1) Imagen estatica (archivo)")
    logger.info("  2) Camara web")
    while True:
        choice = input("Opcion [1/2, Enter=1]: ").strip()
        if choice in {"", "1"}:
            return "file"
        if choice == "2":
            return "camera"
        logger.warning("Entrada invalida. Escribe 1 o 2.")


def _resolve_camera_mode(
    image_source: str | None, cli_value: str | None
) -> str | None:
    """Resuelve el modo de camara desde CLI o selector interactivo."""
    if image_source != "camera":
        return cli_value

    if cli_value in {"snapshot", "stream"}:
        return cli_value

    if not sys.stdin.isatty():
        return None

    logger = get_logger("tpdi.cli")
    logger.info("Selecciona el modo de camara:")
    logger.info("  1) Captura unica (snapshot)")
    logger.info("  2) Stream continuo")
    while True:
        choice = input("Modo [1/2, Enter=1]: ").strip()
        if choice in {"", "1"}:
            return "snapshot"
        if choice == "2":
            return "stream"
        logger.warning("Entrada invalida. Escribe 1 o 2.")


def main() -> None:
    """Punto de entrada principal de la aplicacion TPDI."""
    setup_logging(name="tpdi")
    args = parse_cli_args()
    image_source = _resolve_image_source(args.image_source)
    camera_mode = _resolve_camera_mode(image_source, args.camera_mode)
    try:
        success = bootstrap_and_run_color_channel_analysis(
            mode=args.mode,
            log_level=args.log_level,
            gui_backend=args.gui_backend,
            input_dir=args.input_dir,
            image_source=image_source,
            camera_index=args.camera_index,
            fps=args.fps,
            grid=args.grid,
            camera_mode=camera_mode,
            frame_width=args.frame_width,
            frame_height=args.frame_height,
            perf_debug=args.perf_debug,
            perf_every=args.perf_every,
        )
    except KeyboardInterrupt as exc:
        get_logger("tpdi.cli").warning("Interrumpido por usuario.")
        raise SystemExit(130) from exc
    raise SystemExit(0 if success else 1)
