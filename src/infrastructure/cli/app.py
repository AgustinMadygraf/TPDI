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
from src.infrastructure.opencv.cv2_image_loader import CV2ImageLoader
from src.infrastructure.opencv.cv2_video_loader import (
    CV2VideoLoader,
    CameraUnavailableError,
)
from src.infrastructure.settings.path_validator import PathValidator
from src.infrastructure.settings.logger import setup_logging, get_logger
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
        self._logger = get_logger(__name__)
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
        self._cmyk_policy = GenericCmykSeparationPolicy()
        self._color_analyzer = ColorChannelAnalyzer(
            cmyk_policy=self._cmyk_policy
        )

    def _on_load_error(self, path: Path, exc: Exception) -> None:
        "Callback para manejar errores de carga de imágenes."
        self._logger.warning("No se pudo cargar imagen %s: %s", path, exc)

    def load_images(self) -> List[Image]:
        "Carga todas las imágenes del directorio base."
        use_case = LoadImagesFromDirectory(self._loader, on_error=self._on_load_error)
        return use_case.execute(self._base_path)

    def run_color_channel_analysis(self) -> bool:
        "Ejecuta analisis de canales de color con layout segun modo."
        print("=" * 60)
        print("TPDI - Analisis de Canales de Color")
        print("=" * 60)
        print()

        if self._config.image_source == "camera":
            if self._config.camera_mode == "stream":
                return self._run_camera_stream_analysis()
            print(
                "Capturando imagen desde camara... "
                f"(indice: {self._config.camera_index})"
            )
            try:
                original = self._gateway.get_frame()
            except CameraUnavailableError as exc:
                self._print_camera_unavailable_help(exc)
                return False
            except RuntimeError as exc:
                self._print_camera_unavailable_help(exc)
                return False
            if original is None:
                print("ERROR: No se pudo capturar imagen de la camara.")
                return False
            print(f"Imagen capturada: {original.name}")
            print(f"  Dimensiones: {original.width}x{original.height}")
            print(f"  Canales: {original.channels}")
        else:
            # Cargar imagenes desde archivos
            print(f"Cargando imagenes desde: {self._base_path}")
            images = self.load_images()
            if not images:
                print(f"ERROR: No se encontraron imagenes en: {self._base_path}")
                print("Agrega imagenes PNG/JPG a la carpeta data/input/")
                print()
                return False
            print(f"Cargadas {len(images)} imagen(es)")
            original = images[0]
            print(f"Imagen seleccionada: {original.name}")
            print(f"  Dimensiones: {original.width}x{original.height}")
            print(f"  Canales: {original.channels}")

        print()
        analysis = self._process_color_variants(original)

        print()
        self._display_grid_2x4(original, analysis)

        print()
        print("=" * 60)
        print("Aplicacion finalizada.")
        print("=" * 60)
        return True

    def _run_camera_stream_analysis(self) -> bool:
        """Ejecuta analisis continuo desde camara hasta que el usuario presione 'q'."""
        frame_interval = 1.0 / self._config.fps
        print(
            "Iniciando stream de camara... "
            f"(indice: {self._config.camera_index}, fps_objetivo: {self._config.fps:.2f})"
        )
        print("Presiona 'q' en la ventana para salir del stream.")
        print()

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
                analysis = self._color_analyzer.execute(original, self._color_mode)
                analysis_ms = (time.perf_counter() - analysis_start) * 1000.0

                render_start = time.perf_counter()
                should_continue = self._display_grid_2x4(
                    original,
                    analysis,
                    show_console_output=False,
                    wait_ms=1,
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
        except CameraUnavailableError as exc:
            self._print_camera_unavailable_help(exc)
            return False
        except RuntimeError as exc:
            self._print_camera_unavailable_help(exc)
            return False
        finally:
            close_windows = getattr(self._displayer, "close_windows", None)
            if callable(close_windows):
                close_windows()

        if processed_frames == 0:
            print("ERROR: No se pudo capturar imagen de la camara.")
            return False

        print(f"Stream finalizado. Frames procesados: {processed_frames}")
        print()
        print("=" * 60)
        print("Aplicacion finalizada.")
        print("=" * 60)
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

        print(
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
        self._logger.error("Error de camara: %s", exc)
        print("ERROR: No se pudo iniciar la camara.")
        print(f"Detalle: {exc}")
        print("Sugerencias:")
        print("  1. Verifica que la camara este conectada y libre.")
        print("  2. Prueba otro indice: --image_source=camera --camera_index=1")
        print("  3. Usa archivos: --image_source=file --input_dir=data/input")
        print()

    def _analyze_pixel(self, image: Image, x: int, y: int) -> tuple:
        "Analiza el valor del pixel específico en la imagen."
        idx = (y * image.width + x) * image.channels
        return tuple(image.data[idx : idx + image.channels])

    def _process_color_variants(self, original: Image) -> ColorAnalysisResult:
        "Construye el analisis configurable y muestra depuracion en consola."
        analysis = self._color_analyzer.execute(original, self._color_mode)

        print()
        print("=" * 60)
        print(analysis.debug_title)
        print("=" * 60)
        print(f"Imagen: {original.name}")
        print(
            f"Dimensiones: {original.width}x{original.height}, Canales: {original.channels}"
        )
        print(f"Total de bytes en data: {len(original.data)}")
        print(f"Total de pixeles: {len(original.data) // original.channels}")
        print()

        # Muestreo de pixeles de la imagen original (esquinas y centro)
        print("MUESTRA DE PIXELES DE LA IMAGEN ORIGINAL:")
        print("-" * 60)
        sample_positions = [
            (0, 0, "Esquina superior izquierda"),
            (original.width // 2, original.height // 2, "Centro"),
            (original.width - 1, original.height - 1, "Esquina inferior derecha"),
            (original.width // 4, original.height // 4, "Cuarto superior izquierdo"),
            (
                3 * original.width // 4,
                3 * original.height // 4,
                "Tres cuartos inferior derecho",
            ),
        ]

        for x, y, desc in sample_positions:
            values = self._analyze_pixel(original, x, y)
            converted_values = self._convert_pixel_for_mode(values)
            labels = analysis.channel_pixel_labels
            values_text = ", ".join(
                f"{label}={value:3d}"
                for label, value in zip(labels, converted_values, strict=False)
            )
            print(f"  ({x:4d},{y:4d}) {desc:30s} -> {values_text}")

        print()
        print("ESTADISTICAS GLOBALES DE LA ORIGINAL:")
        print("-" * 60)

        channel_values = self._extract_channel_values_for_mode(original)
        channel_labels = analysis.channel_labels

        for label, values in zip(channel_labels, channel_values, strict=False):
            print(
                f"  {label:15s} -> Min: {min(values):3d}, Max: {max(values):3d}, "
                f"Promedio: {sum(values)/len(values):6.2f}"
            )
        print()

        print("EXTRAYENDO CANALES DE LA IMAGEN ORIGINAL...")
        print("-" * 60)

        print("VERIFICACION DE EXTRACCION:")
        print("-" * 60)

        channel_variant_count = len(analysis.channel_labels)
        for variant in analysis.variants[:channel_variant_count]:
            print(
                self._build_channel_verification_message(
                    original, variant.label, variant.image
                )
            )

        grayscale_variant = next(
            (
                variant
                for variant in analysis.variants
                if variant.label == "ESCALA DE GRISES"
            ),
            None,
        )
        if grayscale_variant is not None:
            grayscale_image = grayscale_variant.image
            original_values = self._convert_pixel_for_mode(tuple(original.data[:3]))
            expected_gray = int(sum(original_values) / len(original_values))
            if self._color_mode == "CMYK":
                expected_gray = 255 - expected_gray
            gray_values = tuple(grayscale_image.data[:3])
            print(
                f"  Escala Gris: Pixel 0 -> "
                f"R={gray_values[0]:3d}, G={gray_values[1]:3d}, B={gray_values[2]:3d} | "
                f"Esperado: {expected_gray:3d} | "
                f"OK: {gray_values == (expected_gray, expected_gray, expected_gray)}"
            )

        print()
        print("=" * 60)

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
        if analysis.mode == "CMYK":
            variant_by_label = {variant.label: variant for variant in analysis.variants}
            if self._config.grid == "2x3":
                if show_console_output:
                    print("Mostrando grid de analisis 2x3:")
                rows, cols = (3, 2)
                ordered_labels = [
                    "ORIGINAL",
                    "ESCALA DE GRISES",
                    "CANAL CIAN",
                    "CANAL MAGENTA",
                    "CANAL AMARILLO",
                    "CANAL NEGRO",
                ]

                grid_images = [(original, "ORIGINAL")]
                grid_images.extend(
                    (variant_by_label[label].image, label)
                    for label in ordered_labels[1:]
                    if label in variant_by_label
                )
            else:
                if show_console_output:
                    print("Mostrando grid de analisis 2x2 (CMYK):")
                rows, cols = (2, 2)
                ordered_labels = [
                    "CANAL CIAN",
                    "CANAL MAGENTA",
                    "CANAL AMARILLO",
                    "CANAL NEGRO",
                ]
                grid_images = [
                    (variant_by_label[label].image, label)
                    for label in ordered_labels
                    if label in variant_by_label
                ]

            for row in range(rows):
                start = row * cols
                end = start + cols
                row_items = ordered_labels[start:end]
                if show_console_output:
                    print(f"  [FILA {row + 1}] " + " | ".join(row_items))
        else:
            if show_console_output:
                print("Mostrando grid de analisis 2x4:")
            grid_labels = [variant.label for variant in analysis.variants]
            total_images = 1 + len(grid_labels)
            cols = 4
            rows = max(2, math.ceil(total_images / cols))

            for row in range(rows):
                start = row * cols
                end = start + cols
                if row == 0:
                    row_items = ["ORIGINAL", *grid_labels[: cols - 1]]
                else:
                    row_items = grid_labels[start - 1 : end - 1]
                if row_items and show_console_output:
                    print(f"  [FILA {row + 1}] " + " | ".join(row_items))

            grid_images = [
                (original, "ORIGINAL"),
                *[(variant.image, variant.label) for variant in analysis.variants],
            ]

        if show_console_output:
            print()
            print("Presiona cualquier tecla en la ventana para cerrar...")
            print()

        display_result = self._displayer.display_grid(
            images=grid_images,
            grid_size=(rows, cols),
            title=analysis.analysis_title,
            wait_ms=wait_ms,
            close_on_exit=close_on_exit,
            quit_key="q",
        )
        return True if display_result is None else bool(display_result)

    def _convert_pixel_for_mode(self, values: tuple[int, ...]) -> tuple[int, ...]:
        """Convierte un pixel RGB al modo de color activo para depuracion."""
        if self._color_mode == "CMY":
            return tuple(255 - value for value in values)
        if self._color_mode == "CMYK":
            return self._cmyk_policy.rgb_to_cmyk(
                values[0], values[1], values[2]
            )
        return values

    def _extract_channel_values_for_mode(self, image: Image) -> tuple[List[int], ...]:
        """Retorna los valores por canal segun el modo de color activo."""
        first_channel = [image.data[i] for i in range(0, len(image.data), 3)]
        second_channel = [image.data[i + 1] for i in range(0, len(image.data), 3)]
        third_channel = [image.data[i + 2] for i in range(0, len(image.data), 3)]

        if self._color_mode == "CMY":
            return (
                [255 - value for value in first_channel],
                [255 - value for value in second_channel],
                [255 - value for value in third_channel],
            )

        if self._color_mode == "CMYK":
            cyan_values: List[int] = []
            magenta_values: List[int] = []
            yellow_values: List[int] = []
            black_values: List[int] = []
            for red, green, blue in zip(
                first_channel, second_channel, third_channel, strict=False
            ):
                cyan, magenta, yellow, black = self._cmyk_policy.rgb_to_cmyk(
                    red, green, blue
                )
                cyan_values.append(cyan)
                magenta_values.append(magenta)
                yellow_values.append(yellow)
                black_values.append(black)
            return (cyan_values, magenta_values, yellow_values, black_values)

        return (first_channel, second_channel, third_channel)

    def _build_channel_verification_message(
        self, original: Image, label: str, variant: Image
    ) -> str:
        """Construye un mensaje de verificacion para el primer pixel de una variante."""
        source_values = self._convert_pixel_for_mode(tuple(original.data[:3]))
        variant_values = tuple(variant.data[:3])

        is_cmyk_mode = self._color_mode == "CMYK" and len(source_values) >= 4

        if label == "CANAL ROJO":
            expected = (source_values[0], 0, 0)
        elif label == "CANAL VERDE":
            expected = (0, source_values[1], 0)
        elif label == "CANAL AZUL":
            expected = (0, 0, source_values[2])
        elif label == "CANAL CIAN":
            expected = (
                (255 - source_values[0], 255, 255)
                if is_cmyk_mode
                else (0, source_values[0], source_values[0])
            )
        elif label == "CANAL MAGENTA":
            expected = (
                (255, 255 - source_values[1], 255)
                if is_cmyk_mode
                else (source_values[1], 0, source_values[1])
            )
        elif label == "CANAL AMARILLO":
            expected = (
                (255, 255, 255 - source_values[2])
                if is_cmyk_mode
                else (source_values[2], source_values[2], 0)
            )
        elif label == "CANAL NEGRO" and len(source_values) >= 4:
            value = 255 - source_values[3]
            expected = (value, value, value)
        else:
            expected = variant_values

        return (
            f"  {label}: Pixel 0 -> R={variant_values[0]:3d}, G={variant_values[1]:3d}, "
            f"B={variant_values[2]:3d} | Esperado: {expected} | OK: {variant_values == expected}"
        )

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

    print()
    print("Selecciona la fuente de imagen:")
    print("  1) Imagen estatica (archivo)")
    print("  2) Camara web")
    while True:
        choice = input("Opcion [1/2, Enter=1]: ").strip()
        if choice in {"", "1"}:
            return "file"
        if choice == "2":
            return "camera"
        print("Entrada invalida. Escribe 1 o 2.")


def main() -> None:
    """Punto de entrada principal de la aplicacion TPDI."""
    args = parse_cli_args()
    image_source = _resolve_image_source(args.image_source)
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
            camera_mode=args.camera_mode,
            frame_width=args.frame_width,
            frame_height=args.frame_height,
            perf_debug=args.perf_debug,
            perf_every=args.perf_every,
        )
    except KeyboardInterrupt as exc:
        print()
        print("Interrumpido por usuario.")
        raise SystemExit(130) from exc
    raise SystemExit(0 if success else 1)

