"""Console reporting helpers for color analysis debug output."""

from typing import List

from src.entities.image import Image
from src.infrastructure.settings.logger import get_logger
from src.use_cases.color_analysis import ColorAnalysisResult, ColorMode
from src.use_cases.color_separation import GenericCmykSeparationPolicy


class ColorAnalysisConsoleReporter:
    """Renderiza en consola el diagnostico de analisis de color."""

    def __init__(
        self,
        color_mode: ColorMode,
        cmyk_policy: GenericCmykSeparationPolicy | None = None,
    ) -> None:
        self._color_mode = color_mode
        self._cmyk_policy = cmyk_policy or GenericCmykSeparationPolicy()
        self._logger = get_logger("tpdi.cli.analysis")

    def report(self, original: Image, analysis: ColorAnalysisResult) -> None:
        self._logger.info("=" * 60)
        self._logger.info(analysis.debug_title)
        self._logger.info("=" * 60)
        self._logger.info("Imagen: %s", original.name)
        self._logger.info(
            "Dimensiones: %dx%d, Canales: %d", original.width, original.height, original.channels
        )
        self._logger.info("Total de bytes en data: %d", len(original.data))
        self._logger.info("Total de pixeles: %d", len(original.data) // original.channels)

        self._logger.info("MUESTRA DE PIXELES DE LA IMAGEN ORIGINAL:")
        self._logger.info("-" * 60)
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
            values_text = ", ".join(
                f"{label}={value:3d}"
                for label, value in zip(
                    analysis.channel_pixel_labels, converted_values, strict=False
                )
            )
            self._logger.info("  (%4d,%4d) %-30s -> %s", x, y, desc, values_text)

        self._logger.info("ESTADISTICAS GLOBALES DE LA ORIGINAL:")
        self._logger.info("-" * 60)
        channel_values = self._extract_channel_values_for_mode(original)
        for label, values in zip(analysis.channel_labels, channel_values, strict=False):
            self._logger.info(
                "  %15s -> Min: %3d, Max: %3d, Promedio: %6.2f",
                label,
                min(values),
                max(values),
                sum(values) / len(values),
            )

        self._logger.info("EXTRAYENDO CANALES DE LA IMAGEN ORIGINAL...")
        self._logger.info("-" * 60)
        self._logger.info("VERIFICACION DE EXTRACCION:")
        self._logger.info("-" * 60)
        channel_variant_count = len(analysis.channel_labels)
        for variant in analysis.variants[:channel_variant_count]:
            self._logger.info(
                self._build_channel_verification_message(
                    original, variant.label, variant.image
                )
            )

        grayscale_variant = next(
            (variant for variant in analysis.variants if variant.label == "ESCALA DE GRISES"),
            None,
        )
        if grayscale_variant is not None:
            gray_values = tuple(grayscale_variant.image.data[:3])
            original_values = self._convert_pixel_for_mode(tuple(original.data[:3]))
            expected_gray = int(sum(original_values) / len(original_values))
            if self._color_mode == "CMYK":
                expected_gray = 255 - expected_gray
            self._logger.info(
                "  Escala Gris: Pixel 0 -> R=%3d, G=%3d, B=%3d | Esperado: %3d | OK: %s",
                gray_values[0],
                gray_values[1],
                gray_values[2],
                expected_gray,
                gray_values == (expected_gray, expected_gray, expected_gray),
            )

        self._logger.info("=" * 60)

    def _analyze_pixel(self, image: Image, x: int, y: int) -> tuple[int, ...]:
        idx = (y * image.width + x) * image.channels
        return tuple(image.data[idx : idx + image.channels])

    def _convert_pixel_for_mode(self, values: tuple[int, ...]) -> tuple[int, ...]:
        if self._color_mode == "CMY":
            return tuple(255 - value for value in values)
        if self._color_mode == "CMYK":
            return self._cmyk_policy.rgb_to_cmyk(values[0], values[1], values[2])
        return values

    def _extract_channel_values_for_mode(self, image: Image) -> tuple[List[int], ...]:
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
                cyan, magenta, yellow, black = self._cmyk_policy.rgb_to_cmyk(red, green, blue)
                cyan_values.append(cyan)
                magenta_values.append(magenta)
                yellow_values.append(yellow)
                black_values.append(black)
            return (cyan_values, magenta_values, yellow_values, black_values)

        return (first_channel, second_channel, third_channel)

    def _build_channel_verification_message(
        self, original: Image, label: str, variant: Image
    ) -> str:
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
