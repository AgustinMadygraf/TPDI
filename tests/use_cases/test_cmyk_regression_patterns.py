"""Regression patterns for CMYK separations under default print policy."""

from src.entities.image import Image
from src.use_cases.color_analysis import ColorChannelAnalyzer


class TestCmykRegressionPatterns:
    """Locks expected channel outputs for representative CMYK pattern image."""

    def test_reference_pattern_white_black_red_blue(self):
        analyzer = ColorChannelAnalyzer()
        image = Image(
            name="pattern_wbrb.png",
            width=2,
            height=2,
            channels=3,
            data=[
                255,
                255,
                255,  # white
                0,
                0,
                0,  # black
                255,
                0,
                0,  # red
                0,
                0,
                255,  # blue
            ],
            path="/tmp/pattern_wbrb.png",
        )

        result = analyzer.execute(image, "CMYK")

        assert [variant.label for variant in result.variants] == [
            "CANAL CIAN",
            "CANAL MAGENTA",
            "CANAL AMARILLO",
            "CANAL NEGRO",
            "ESCALA DE GRISES",
        ]

        cyan = result.variants[0].image.data
        magenta = result.variants[1].image.data
        yellow = result.variants[2].image.data
        black = result.variants[3].image.data
        grayscale = result.variants[4].image.data

        assert cyan == [
            255,
            255,
            255,
            255,
            255,
            255,
            255,
            255,
            255,
            0,
            255,
            255,
        ]
        assert magenta == [
            255,
            255,
            255,
            255,
            255,
            255,
            255,
            0,
            255,
            255,
            0,
            255,
        ]
        assert yellow == [
            255,
            255,
            255,
            255,
            255,
            255,
            255,
            255,
            0,
            255,
            255,
            255,
        ]
        assert black == [
            255,
            255,
            255,
            0,
            0,
            0,
            255,
            255,
            255,
            255,
            255,
            255,
        ]
        assert grayscale == [
            255,
            255,
            255,
            192,
            192,
            192,
            128,
            128,
            128,
            128,
            128,
            128,
        ]
