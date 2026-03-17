"""
Path: src/infrastructure/cli/app.py
"""

from pathlib import Path
from typing import List, Tuple
from src.infrastructure.shared.logger import setup_logging, get_logger
from src.interface_adapters.controllers.main_controller import MainController
from src.use_cases.load_images import ImageLoaderPort, LoadImagesFromDirectory
from src.use_cases.display_image import ImageDisplayPort
from src.use_cases.image_processing import (
    apply_grayscale,
    extract_red_channel,
    extract_green_channel,
    extract_blue_channel,
    red_to_grayscale,
    green_to_grayscale,
    blue_to_grayscale,
)
from src.entities.image import Image


class CLIApp:
    "Aplicación de línea de comandos para TPDI."

    def __init__(
        self,
        loader: ImageLoaderPort,
        displayer: ImageDisplayPort,
        base_path: Path = None,
    ):
        setup_logging(name="tpdi")
        self._logger = get_logger(__name__)
        self._displayer = displayer
        self._loader = loader
        self._base_path = base_path or MainController.DEFAULT_INPUT_DIR

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
        variants = self._process_color_variants(original)

        # Mostrar grid 2x4
        print()
        self._display_grid_2x4(original, variants)

        print()
        print("=" * 60)
        print("Aplicacion finalizada.")
        print("=" * 60)
        return True

    def _analyze_pixel(self, image: Image, x: int, y: int) -> tuple:
        "Analiza el valor RGB de un pixel específico en la imagen."
        idx = (y * image.width + x) * image.channels
        if image.channels == 3:
            return (image.data[idx], image.data[idx + 1], image.data[idx + 2])
        else:
            return (image.data[idx],)

    def _process_color_variants(self, original: Image) -> List[Tuple[str, Image]]:
        "Procesa la imagen original para extraer canales y aplicar escala de grises, con depuración."
        print()
        print("=" * 60)
        print("DEPURACION DE CANALES RGB")
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
            r, g, b = self._analyze_pixel(original, x, y)
            print(f"  ({x:4d},{y:4d}) {desc:30s} -> R={r:3d}, G={g:3d}, B={b:3d}")

        print()
        print("ESTADISTICAS GLOBALES DE LA ORIGINAL:")
        print("-" * 60)

        # Calcular estadísticas por canal
        r_values = [original.data[i] for i in range(0, len(original.data), 3)]
        g_values = [original.data[i + 1] for i in range(0, len(original.data), 3)]
        b_values = [original.data[i + 2] for i in range(0, len(original.data), 3)]

        print(
            f"  Canal Rojo   -> Min: {min(r_values):3d}, Max: {max(r_values):3d}, Promedio: {sum(r_values)/len(r_values):6.2f}"
        )
        print(
            f"  Canal Verde  -> Min: {min(g_values):3d}, Max: {max(g_values):3d}, Promedio: {sum(g_values)/len(g_values):6.2f}"
        )
        print(
            f"  Canal Azul   -> Min: {min(b_values):3d}, Max: {max(b_values):3d}, Promedio: {sum(b_values)/len(b_values):6.2f}"
        )
        print()

        # Extraer canales directamente de la imagen ORIGINAL
        print("EXTRAYENDO CANALES DE LA IMAGEN ORIGINAL...")
        print("-" * 60)
        red_channel = extract_red_channel(original)
        green_channel = extract_green_channel(original)
        blue_channel = extract_blue_channel(original)
        full_grayscale = apply_grayscale(original)
        red_grayscale = red_to_grayscale(original)
        green_grayscale = green_to_grayscale(original)
        blue_grayscale = blue_to_grayscale(original)

        # Verificar que los canales se extrajeron correctamente
        print("VERIFICACION DE EXTRACCION:")
        print("-" * 60)

        # Verificar canal rojo (debe tener R original, G=0, B=0)
        r_red = red_channel.data[0]
        g_red = red_channel.data[1]
        b_red = red_channel.data[2]
        r_orig = original.data[0]
        print(
            f"  Canal Rojo: Pixel 0 -> R={r_red:3d}, G={g_red:3d}, B={b_red:3d} | R original era: {r_orig:3d} | OK: {r_red == r_orig and g_red == 0 and b_red == 0}"
        )

        # Verificar canal verde (debe tener R=0, G original, B=0)
        r_green = green_channel.data[0]
        g_green = green_channel.data[1]
        b_green = green_channel.data[2]
        g_orig = original.data[1]
        print(
            f"  Canal Verde: Pixel 0 -> R={r_green:3d}, G={g_green:3d}, B={b_green:3d} | G original era: {g_orig:3d} | OK: {r_green == 0 and g_green == g_orig and b_green == 0}"
        )

        # Verificar canal azul (debe tener R=0, G=0, B original)
        r_blue = blue_channel.data[0]
        g_blue = blue_channel.data[1]
        b_blue = blue_channel.data[2]
        b_orig = original.data[2]
        print(
            f"  Canal Azul: Pixel 0 -> R={r_blue:3d}, G={g_blue:3d}, B={b_blue:3d} | B original era: {b_orig:3d} | OK: {r_blue == 0 and g_blue == 0 and b_blue == b_orig}"
        )

        # Verificar escala de grises
        r_gray = full_grayscale.data[0]
        g_gray = full_grayscale.data[1]
        b_gray = full_grayscale.data[2]
        expected_gray = int((r_orig + g_orig + b_orig) / 3)
        print(
            f"  Escala Gris: Pixel 0 -> R={r_gray:3d}, G={g_gray:3d}, B={b_gray:3d} | Esperado: {expected_gray:3d} | OK: {r_gray == expected_gray and g_gray == expected_gray and b_gray == expected_gray}"
        )

        print()
        print("=" * 60)

        return [
            ("Canal Rojo (R,0,0)", red_channel),
            ("Canal Verde (0,G,0)", green_channel),
            ("Canal Azul (0,0,B)", blue_channel),
            ("Escala de grises", full_grayscale),
            ("Rojo -> Gris", red_grayscale),
            ("Verde -> Gris", green_grayscale),
            ("Azul -> Gris", blue_grayscale),
        ]

    def _display_grid_2x4(
        self, original: Image, variants: List[Tuple[str, Image]]
    ) -> None:
        """Muestra el grid 2x4 con la imagen original y variantes RGB.

        Args:
            original: Imagen original.
            variants: Lista de variantes procesadas.
        """
        print("Mostrando grid de analisis 2x4:")
        print("  [FILA 1] ORIGINAL | ROJO (R,0,0) | VERDE (0,G,0) | AZUL (0,0,B)")
        print(
            "  [FILA 2] GRIS (promedio) | R->GRIS (R,R,R) | V->GRIS (G,G,G) | A->GRIS (B,B,B)"
        )
        print()
        print("Presiona cualquier tecla en la ventana para cerrar...")
        print()

        # Grid 2x4: 2 filas, 4 columnas
        red_channel = variants[0][1]
        green_channel = variants[1][1]
        blue_channel = variants[2][1]
        full_grayscale = variants[3][1]
        red_grayscale = variants[4][1]
        green_grayscale = variants[5][1]
        blue_grayscale = variants[6][1]

        grid_images = [
            # Fila 1
            (original, "ORIGINAL"),
            (red_channel, "CANAL ROJO"),
            (green_channel, "CANAL VERDE"),
            (blue_channel, "CANAL AZUL"),
            # Fila 2
            (full_grayscale, "ESCALA DE GRISES"),
            (red_grayscale, "ROJO -> GRIS"),
            (green_grayscale, "VERDE -> GRIS"),
            (blue_grayscale, "AZUL -> GRIS"),
        ]

        self._displayer.display_grid(
            images=grid_images, grid_size=(2, 4), title=f"Analisis RGB: {original.name}"
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
