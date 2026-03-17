"""
Pytest configuration and shared fixtures.
Path: tests/conftest.py
"""

import tempfile
from pathlib import Path

import numpy as np
import pytest

from src.entities.image import Image
from src.infrastructure.numpy.image_adapter import NumPyImageAdapter


@pytest.fixture
def temp_directory():
    """Provides a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)


@pytest.fixture
def sample_image() -> Image:
    """Provides a sample Image entity."""
    return Image(
        name="test.png",
        width=100,
        height=100,
        channels=3,
        data=[0] * (100 * 100 * 3),
        path="/tmp/test.png"
    )


@pytest.fixture
def sample_grayscale_image() -> Image:
    """Provides a sample grayscale Image entity."""
    return Image(
        name="test_gray.png",
        width=50,
        height=50,
        channels=1,
        data=[128] * (50 * 50),
        path="/tmp/test_gray.png"
    )


@pytest.fixture
def numpy_adapter() -> NumPyImageAdapter:
    """Provides a NumPyImageAdapter instance."""
    return NumPyImageAdapter()


@pytest.fixture
def create_test_image_file(temp_directory):
    """Factory fixture to create test image files."""
    import cv2
    
    def _create(filename: str, width: int = 100, height: int = 100, channels: int = 3):
        filepath = temp_directory / filename
        if channels == 1:
            img = np.random.randint(0, 256, (height, width), dtype=np.uint8)
        else:
            img = np.random.randint(0, 256, (height, width, channels), dtype=np.uint8)
        cv2.imwrite(str(filepath), img)
        return filepath
    
    return _create


@pytest.fixture
def base_test_dir() -> Path:
    """Provides a base test directory path."""
    return Path("data/input").resolve()
