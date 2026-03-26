"""Console reporting helpers for color analysis debug output."""

from typing import List

from src.entities.image import Image
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

    def report(self, original: Image, analysis: ColorAnalysisResult) -> None:
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
            values_text = ", ".join(
                f"{label}={value:3d}"
                for label, value in zip(
                    analysis.channel_pixel_labels, converted_values, strict=False
                )
            )
            print(f"  ({x:4d},{y:4d}) {desc:30s} -> {values_text}")

        print()
        print("ESTADISTICAS GLOBALES DE LA ORIGINAL:")
        print("-" * 60)
        channel_values = self._extract_channel_values_for_mode(original)
        for label, values in zip(analysis.channel_labels, channel_values, strict=False):
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
            (variant for variant in analysis.variants if variant.label == "ESCALA DE GRISES"),
            None,
        )
        if grayscale_variant is not None:
            gray_values = tuple(grayscale_variant.image.data[:3])
            original_values = self._convert_pixel_for_mode(tuple(original.data[:3]))
            expected_gray = int(sum(original_values) / len(original_values))
            if self._color_mode == "CMYK":
                expected_gray = 255 - expected_gray
            print(
                f"  Escala Gris: Pixel 0 -> "
                f"R={gray_values[0]:3d}, G={gray_values[1]:3d}, B={gray_values[2]:3d} | "
                f"Esperado: {expected_gray:3d} | "
                f"OK: {gray_values == (expected_gray, expected_gray, expected_gray)}"
            )

        print()
        print("=" * 60)

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
