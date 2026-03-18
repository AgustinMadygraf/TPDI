"""
Path: src/infrastructure/cli/app.py
"""

from pathlib import Path
import math
from typing import List

from src.entities.image import Image
from src.infrastructure.opencv.cv2_video_loader import CameraUnavailableError
from src.infrastructure.shared.logger import setup_logging, get_logger
from src.use_cases.color_analysis import (
    ColorAnalysisResult,
    ColorChannelAnalyzer,
    ColorMode,
)
from src.use_cases.color_separation import GenericCmykSeparationPolicy
from src.interface_adapters.controllers.main_controller import MainController
from src.use_cases.display_image import ImageDisplayPort
from src.use_cases.load_images import ImageLoaderPort, LoadImagesFromDirectory

from src.interface_adapters.gateways.image_gateway import ImageGateway
from src.infrastructure.shared.config import AppConfig


class CLIApp:
    "Aplicación de línea de comandos para TPDI."

    def __init__(
        self,
        loader: ImageLoaderPort,
        displayer: ImageDisplayPort,
        gateway: ImageGateway,
        config: AppConfig,
        base_path: Path = None,
        color_mode: ColorMode = "RGB",
    ):
        setup_logging(name="tpdi")
        self._logger = get_logger(__name__)
        self._displayer = displayer
        self._loader = loader
        self._gateway = gateway
        self._config = config
        self._base_path = base_path or MainController.DEFAULT_INPUT_DIR
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
        "Ejecuta análisis de canales de color en grid 2x4."
        print("=" * 60)
        print("TPDI - Analisis de Canales de Color")
        print("=" * 60)
        print()

        if self._config.image_source == "camera":
            frame_interval = 1.0 / self._config.fps
            print(
                "Capturando imagen desde camara... "
                f"(indice: {self._config.camera_index}, "
                f"fps: {self._config.fps:.2f}, "
                f"intervalo: {frame_interval:.3f}s)"
            )
            try:
                stream = self._gateway.get_video_stream(
                    frame_interval=frame_interval
                )
                original = next(stream)
            except CameraUnavailableError as exc:
                self._print_camera_unavailable_help(exc)
                return False
            except RuntimeError as exc:
                self._print_camera_unavailable_help(exc)
                return False
            except StopIteration:
                print("ERROR: No se pudo capturar imagen de la camara.")
                return False
            print(f"Imagen capturada: {original.name}")
            print(f"  Dimensiones: {original.width}x{original.height}")
            print(f"  Canales: {original.channels}")
        else:
            # Cargar imágenes desde archivos
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
        # Procesar variantes (con depuración incluida)
        analysis = self._process_color_variants(original)

        # Mostrar grid 2x4
        print()
        self._display_grid_2x4(original, analysis)

        print()
        print("=" * 60)
        print("Aplicacion finalizada.")
        print("=" * 60)
        return True

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

    def _display_grid_2x4(self, original: Image, analysis: ColorAnalysisResult) -> None:
        """Muestra un grid de analisis con tamaño dinamico segun variantes.

        Args:
            original: Imagen original.
            analysis: Resultado procesado para display.
        """
        if analysis.mode == "CMYK":
            print("Mostrando grid de analisis 2x3:")
            rows, cols = (3, 2)
            variant_by_label = {variant.label: variant for variant in analysis.variants}
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

            for row in range(rows):
                start = row * cols
                end = start + cols
                row_items = ordered_labels[start:end]
                print(f"  [FILA {row + 1}] " + " | ".join(row_items))
        else:
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
                if row_items:
                    print(f"  [FILA {row + 1}] " + " | ".join(row_items))

            grid_images = [
                (original, "ORIGINAL"),
                *[(variant.image, variant.label) for variant in analysis.variants],
            ]
        print()
        print("Presiona cualquier tecla en la ventana para cerrar...")
        print()

        self._displayer.display_grid(
            images=grid_images, grid_size=(rows, cols), title=analysis.analysis_title
        )

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

    def _display_comparison(self, original: Image, modified: Image) -> None:
        """Muestra comparación lado a lado de dos imágenes."""
        self._logger.info("Mostrando comparacion: %s", original.name)
        self._displayer.display(original, modified)
