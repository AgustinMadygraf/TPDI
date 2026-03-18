"""
Path: tests/use_cases/test_color_separation.py
"""

from src.use_cases.color_separation import GenericCmykSeparationPolicy


def test_rgb_to_cmyk_black():
    policy = GenericCmykSeparationPolicy()
    cmyk = policy.rgb_to_cmyk(0, 0, 0)
    assert cmyk == (0, 0, 0, 255)
