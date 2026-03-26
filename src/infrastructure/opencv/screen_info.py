"""Utilities for querying screen information."""

from __future__ import annotations

import ctypes
import sys


def get_screen_size() -> tuple[int, int]:
    """Return screen size as (width, height) with a safe fallback."""
    if sys.platform.startswith("win"):
        try:
            user32 = ctypes.windll.user32
            width = int(user32.GetSystemMetrics(0))
            height = int(user32.GetSystemMetrics(1))
            if width > 0 and height > 0:
                return width, height
        except (AttributeError, OSError, ValueError):
            pass

    return (1920, 1080)

