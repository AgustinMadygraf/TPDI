"""Tests for CMYK and flexo spot separation policies."""

from src.use_cases.color_separation import (
    BasicFlexoTwoSpotSeparationPolicy,
    FlexoSpotPalette,
    GenericCmykSeparationPolicy,
    SpotInk,
    default_flexo_spot_palettes,
)


class TestGenericCmykSeparationPolicy:
    """Validate configurable CMYK print parameters."""

    def test_rgb_to_cmyk_default_matches_baseline_conversion(self):
        policy = GenericCmykSeparationPolicy()

        assert policy.rgb_to_cmyk(10, 20, 30) == (170, 85, 0, 225)

    def test_rgb_to_cmyk_applies_dot_gain(self):
        policy = GenericCmykSeparationPolicy(dot_gain=0.1)

        c, m, y, k = policy.rgb_to_cmyk(128, 128, 128)

        assert (c, m, y, k) == (0, 0, 0, 140)

    def test_rgb_to_cmyk_respects_total_ink_limit(self):
        policy = GenericCmykSeparationPolicy(total_ink_limit=300)

        c, m, y, k = policy.rgb_to_cmyk(10, 20, 30)

        assert c + m + y + k <= 300


class TestFlexoTwoSpotModelAndPolicy:
    """Validate spot ink model and baseline flexo two-channel separation."""

    def test_default_palettes_include_expected_entries(self):
        palettes = default_flexo_spot_palettes()

        assert "CYAN_MAGENTA" in palettes
        assert "BLACK_YELLOW" in palettes
        assert palettes["CYAN_MAGENTA"].first_ink.name == "CYAN"

    def test_rgb_to_spot_channels_returns_two_channel_values(self):
        policy = BasicFlexoTwoSpotSeparationPolicy()
        palette = FlexoSpotPalette(
            name="TEST",
            first_ink=SpotInk(name="BLUE_SPOT", rgb=(0, 80, 220)),
            second_ink=SpotInk(name="ORANGE_SPOT", rgb=(255, 120, 0)),
        )

        first, second = policy.rgb_to_spot_channels(120, 130, 140, palette)

        assert 0 <= first <= 255
        assert 0 <= second <= 255

    def test_channels_to_display_rgb_returns_valid_triplet(self):
        policy = BasicFlexoTwoSpotSeparationPolicy()
        palette = default_flexo_spot_palettes()["CYAN_MAGENTA"]

        rgb = policy.channels_to_display_rgb(200, 100, palette)

        assert len(rgb) == 3
        assert all(0 <= value <= 255 for value in rgb)
