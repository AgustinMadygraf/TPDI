"""
Unit tests for NumPyImageAdapter.
Path: tests/infrastructure/numpy/test_image_adapter.py
"""

import numpy as np
import pytest

from src.entities.image import Image
from src.infrastructure.numpy.image_adapter import NumPyImageAdapter


class TestNumPyImageAdapter:
    """Test suite for NumPyImageAdapter."""

    def test_to_numpy_rgb(self):
        """Test converting RGB Image to numpy array."""
        adapter = NumPyImageAdapter()
        image = Image(
            name="test.png",
            width=10,
            height=10,
            channels=3,
            data=[255] * 300,  # All white
            path="/tmp/test.png"
        )
        
        result = adapter.to_numpy(image)
        
        assert isinstance(result, np.ndarray)
        assert result.shape == (10, 10, 3)
        assert result.dtype == np.uint8
        assert result[0, 0, 0] == 255

    def test_to_numpy_grayscale(self):
        """Test converting grayscale Image to numpy array."""
        adapter = NumPyImageAdapter()
        image = Image(
            name="test.png",
            width=5,
            height=5,
            channels=1,
            data=[128] * 25,
            path="/tmp/test.png"
        )
        
        result = adapter.to_numpy(image)
        
        assert result.shape == (5, 5)
        assert result.dtype == np.uint8
        assert result[0, 0] == 128

    def test_to_numpy_preserves_values(self):
        """Test that pixel values are preserved in conversion."""
        adapter = NumPyImageAdapter()
        data = list(range(27))  # 0-26 for 3x3x3 image
        image = Image(
            name="test.png",
            width=3,
            height=3,
            channels=3,
            data=data,
            path="/tmp/test.png"
        )
        
        result = adapter.to_numpy(image)
        
        assert result[0, 0, 0] == 0
        assert result[0, 0, 1] == 1
        assert result[0, 0, 2] == 2
        assert result[1, 1, 0] == 12  # Middle pixel

    def test_from_numpy_rgb(self):
        """Test converting RGB numpy array to Image."""
        adapter = NumPyImageAdapter()
        data = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
        
        result = adapter.from_numpy(name="test.png", data=data, path="/tmp/test.png")
        
        assert result.name == "test.png"
        assert result.width == 100
        assert result.height == 100
        assert result.channels == 3
        assert len(result.data) == 100 * 100 * 3
        assert result.path == "/tmp/test.png"

    def test_from_numpy_grayscale(self):
        """Test converting grayscale numpy array to Image."""
        adapter = NumPyImageAdapter()
        data = np.random.randint(0, 256, (50, 80), dtype=np.uint8)
        
        result = adapter.from_numpy(name="test.png", data=data, path="/tmp/test.png")
        
        assert result.width == 80
        assert result.height == 50
        assert result.channels == 1
        assert len(result.data) == 50 * 80

    def test_from_numpy_default_path(self):
        """Test from_numpy with default (None) path."""
        adapter = NumPyImageAdapter()
        data = np.zeros((10, 10, 3), dtype=np.uint8)
        
        result = adapter.from_numpy(name="test.png", data=data)
        
        assert result.path is None

    def test_roundtrip_conversion(self):
        """Test that to_numpy and from_numpy are inverse operations."""
        adapter = NumPyImageAdapter()
        original_data = np.random.randint(0, 256, (10, 10, 3), dtype=np.uint8)
        
        # Convert to Image
        image = adapter.from_numpy(name="test.png", data=original_data)
        
        # Convert back to numpy
        result_data = adapter.to_numpy(image)
        
        np.testing.assert_array_equal(original_data, result_data)

    def test_from_numpy_preserves_dtype(self):
        """Test that from_numpy preserves uint8 dtype."""
        adapter = NumPyImageAdapter()
        data = np.array([[0, 255], [128, 64]], dtype=np.uint8)
        
        result = adapter.from_numpy(name="test.png", data=data)
        
        # Values should be preserved exactly
        assert result.data[0] == 0
        assert result.data[1] == 255
        assert result.data[2] == 128
        assert result.data[3] == 64
