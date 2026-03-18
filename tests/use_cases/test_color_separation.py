"""Tests for CMYK separation policy behavior."""

from src.use_cases.color_separation import GenericCmykSeparationPolicy


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
