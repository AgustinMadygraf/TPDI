"""
Path: src/use_cases/color_separation.py
"""

from typing import Protocol


class CmykSeparationPolicy(Protocol):
    """Contrato para conversion y visualizacion de canales CMYK."""

    def rgb_to_cmyk(self, red: int, green: int, blue: int) -> tuple[int, int, int, int]:
        ...

    def channel_to_display_rgb(self, channel_index: int, intensity: int) -> tuple[int, int, int]:
        ...

    def cmyk_to_display_gray(self, cyan: int, magenta: int, yellow: int, black: int) -> int:
        ...


class GenericCmykSeparationPolicy:
    "Politica CMYK generica para analisis y simulacion de impresion."
    def __init__(
        self,
        dot_gain: float = 0.0,
        total_ink_limit: int = 1020,
    ) -> None:
        self._dot_gain = dot_gain
        self._total_ink_limit = total_ink_limit

    def rgb_to_cmyk(self, red: int, green: int, blue: int) -> tuple[int, int, int, int]:
        red_norm = red / 255.0
        green_norm = green / 255.0
        blue_norm = blue / 255.0

        key = 1.0 - max(red_norm, green_norm, blue_norm)
        if key >= 1.0:
            return (0, 0, 0, 255)

        cyan = (1.0 - red_norm - key) / (1.0 - key)
        magenta = (1.0 - green_norm - key) / (1.0 - key)
        yellow = (1.0 - blue_norm - key) / (1.0 - key)

        channels = [
            int(round(cyan * 255)),
            int(round(magenta * 255)),
            int(round(yellow * 255)),
            int(round(key * 255)),
        ]

        if self._dot_gain > 0:
            channels = [
                min(255, int(round(value * (1.0 + self._dot_gain))))
                for value in channels
            ]

        total_ink = sum(channels)
        if total_ink > self._total_ink_limit:
            scale = self._total_ink_limit / total_ink
            channels = [int(round(value * scale)) for value in channels]

        return (channels[0], channels[1], channels[2], channels[3])

    def channel_to_display_rgb(self, channel_index: int, intensity: int) -> tuple[int, int, int]:
        if channel_index == 0:
            return (255 - intensity, 255, 255)
        if channel_index == 1:
            return (255, 255 - intensity, 255)
        if channel_index == 2:
            return (255, 255, 255 - intensity)

        value = 255 - intensity
        return (value, value, value)

    def cmyk_to_display_gray(self, cyan: int, magenta: int, yellow: int, black: int) -> int:
        return 255 - int((cyan + magenta + yellow + black) / 4)

