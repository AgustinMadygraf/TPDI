"""
Path: src/infrastructure/cli/app.py
"""

from pathlib import Path
from typing import List

from src.entities.image import Image
from src.infrastructure.shared.logger import setup_logging, get_logger
from src.use_cases.color_analysis import (
    ColorAnalysisResult,
    ColorChannelAnalyzer,
    ColorMode,
)
from src.interface_adapters.controllers.main_controller import MainController
from src.use_cases.display_image import ImageDisplayPort
from src.use_cases.load_images import ImageLoaderPort, LoadImagesFromDirectory


class CLIApp:
    "Aplicación de línea de comandos para TPDI."

    def __init__(
        self,
        loader: ImageLoaderPort,
        displayer: ImageDisplayPort,
        base_path: Path = None,
        color_mode: ColorMode = "RGB",
    ):
        setup_logging(name="tpdi")
        self._logger = get_logger(__name__)
        self._displayer = displayer
        self._loader = loader
        self._base_path = base_path or MainController.DEFAULT_INPUT_DIR
        self._color_mode = color_mode
        self._color_analyzer = ColorChannelAnalyzer()

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

        # Cargar imágenes
        print(f"Cargando imagenes desde: {self._base_path}")
        images = self.load_images()

        if not images:
            print(f"ERROR: No se encontraron imagenes en: {self._base_path}")
            print("Agrega imagenes PNG/JPG a la carpeta data/input/")
            print()
            return False

        print(f"Cargadas {len(images)} imagen(es)")
        print()

        # Tomar la primera imagen
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

    def _analyze_pixel(self, image: Image, x: int, y: int) -> tuple:
        "Analiza el valor del pixel específico en la imagen."
        idx = (y * image.width + x) * image.channels
        if image.channels == 3:
            return (image.data[idx], image.data[idx + 1], image.data[idx + 2])
        else:
            return (image.data[idx],)

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
            print(
                f"  ({x:4d},{y:4d}) {desc:30s} -> "
                f"{labels[0]}={converted_values[0]:3d}, "
                f"{labels[1]}={converted_values[1]:3d}, "
                f"{labels[2]}={converted_values[2]:3d}"
            )

        print()
        print("ESTADISTICAS GLOBALES DE LA ORIGINAL:")
        print("-" * 60)

        channel_values = self._extract_channel_values_for_mode(original)
        channel_labels = analysis.channel_labels

        print(
            f"  {channel_labels[0]:15s} -> Min: {min(channel_values[0]):3d}, Max: {max(channel_values[0]):3d}, Promedio: {sum(channel_values[0])/len(channel_values[0]):6.2f}"
        )
        print(
            f"  {channel_labels[1]:15s} -> Min: {min(channel_values[1]):3d}, Max: {max(channel_values[1]):3d}, Promedio: {sum(channel_values[1])/len(channel_values[1]):6.2f}"
        )
        print(
            f"  {channel_labels[2]:15s} -> Min: {min(channel_values[2]):3d}, Max: {max(channel_values[2]):3d}, Promedio: {sum(channel_values[2])/len(channel_values[2]):6.2f}"
        )
        print()

        print("EXTRAYENDO CANALES DE LA IMAGEN ORIGINAL...")
        print("-" * 60)

        print("VERIFICACION DE EXTRACCION:")
        print("-" * 60)

        for variant in analysis.variants[:3]:
            print(
                self._build_channel_verification_message(
                    original, variant.label, variant.image
                )
            )

        grayscale_image = analysis.variants[3].image
        original_values = self._convert_pixel_for_mode(tuple(original.data[:3]))
        expected_gray = int(sum(original_values) / 3)
        gray_values = tuple(grayscale_image.data[:3])
        print(
            f"  Escala Gris: Pixel 0 -> "
            f"R={gray_values[0]:3d}, G={gray_values[1]:3d}, B={gray_values[2]:3d} | "
            f"Esperado: {expected_gray:3d} | OK: {gray_values == (expected_gray, expected_gray, expected_gray)}"
        )

        print()
        print("=" * 60)

        return analysis

    def _display_grid_2x4(self, original: Image, analysis: ColorAnalysisResult) -> None:
        """Muestra el grid 2x4 con la imagen original y variantes del modo activo.

        Args:
            original: Imagen original.
            analysis: Resultado procesado para display.
        """
        print("Mostrando grid de analisis 2x4:")
        grid_labels = [variant.label for variant in analysis.variants]
        print(
            f"  [FILA 1] ORIGINAL | {grid_labels[0]} | {grid_labels[1]} | {grid_labels[2]}"
        )
        print(
            f"  [FILA 2] {grid_labels[3]} | {grid_labels[4]} | "
            f"{grid_labels[5]} | {grid_labels[6]}"
        )
        print()
        print("Presiona cualquier tecla en la ventana para cerrar...")
        print()

        grid_images = [
            (original, "ORIGINAL"),
            *[(variant.image, variant.label) for variant in analysis.variants],
        ]

        self._displayer.display_grid(
            images=grid_images, grid_size=(2, 4), title=analysis.analysis_title
        )

    def _convert_pixel_for_mode(
        self, values: tuple[int, int, int]
    ) -> tuple[int, int, int]:
        """Convierte un pixel RGB al modo de color activo para depuracion."""
        if self._color_mode == "CMY":
            return tuple(255 - value for value in values)
        return values

    def _extract_channel_values_for_mode(
        self, image: Image
    ) -> tuple[List[int], List[int], List[int]]:
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

        return (first_channel, second_channel, third_channel)

    def _build_channel_verification_message(
        self, original: Image, label: str, variant: Image
    ) -> str:
        """Construye un mensaje de verificacion para el primer pixel de una variante."""
        source_values = self._convert_pixel_for_mode(tuple(original.data[:3]))
        variant_values = tuple(variant.data[:3])

        expected_by_label = {
            "CANAL ROJO": (source_values[0], 0, 0),
            "CANAL VERDE": (0, source_values[1], 0),
            "CANAL AZUL": (0, 0, source_values[2]),
            "CANAL CIAN": (0, source_values[0], source_values[0]),
            "CANAL MAGENTA": (source_values[1], 0, source_values[1]),
            "CANAL AMARILLO": (source_values[2], source_values[2], 0),
        }
        expected = expected_by_label[label]
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
