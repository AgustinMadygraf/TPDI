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
            name="test.jpg",
            width=10,
            height=10,
            channels=3,
            data=[0] * 300,
            path="/tmp/test.jpg"
        )
        
        result = adapter.to_numpy(image)
        
        assert isinstance(result, np.ndarray)
        assert result.shape == (10, 10, 3)
        assert result.dtype == np.uint8

    def test_to_numpy_grayscale(self):
        """Test converting grayscale Image to numpy array."""
        adapter = NumPyImageAdapter()
        image = Image(
            name="test.jpg",
            width=5,
            height=5,
            channels=1,
            data=[128] * 25,
            path="/tmp/test.jpg"
        )
        
        result = adapter.to_numpy(image)
        
        assert result.shape == (5, 5)
        assert result.dtype == np.uint8

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

    def test_from_numpy_grayscale(self):
        """Test converting grayscale numpy array to Image."""
        adapter = NumPyImageAdapter()
        data = np.random.randint(0, 256, (50, 80), dtype=np.uint8)
        
        result = adapter.from_numpy(name="test.png", data=data, path="/tmp/test.png")
        
        assert result.width == 80
        assert result.height == 50
        assert result.channels == 1

    def test_roundtrip_conversion(self):
        """Test that to_numpy and from_numpy are inverse operations."""
        adapter = NumPyImageAdapter()
        original_data = np.random.randint(0, 256, (10, 10, 3), dtype=np.uint8)
        
        image = adapter.from_numpy(name="test.png", data=original_data)
        result_data = adapter.to_numpy(image)
        
        np.testing.assert_array_equal(original_data, result_data)


class TestNumPyImageAdapterOperations:
    """Test suite for array operations."""

    def test_vstack(self):
        """Test vertical stacking of arrays."""
        adapter = NumPyImageAdapter()
        arr1 = np.array([[1, 2], [3, 4]])
        arr2 = np.array([[5, 6], [7, 8]])
        
        result = adapter.vstack([arr1, arr2])
        
        expected = np.array([[1, 2], [3, 4], [5, 6], [7, 8]])
        np.testing.assert_array_equal(result, expected)

    def test_hstack(self):
        """Test horizontal stacking of arrays."""
        adapter = NumPyImageAdapter()
        arr1 = np.array([[1, 2], [3, 4]])
        arr2 = np.array([[5, 6], [7, 8]])
        
        result = adapter.hstack([arr1, arr2])
        
        expected = np.array([[1, 2, 5, 6], [3, 4, 7, 8]])
        np.testing.assert_array_equal(result, expected)

    def test_zeros_2d(self):
        """Test creating 2D zeros array."""
        adapter = NumPyImageAdapter()
        
        result = adapter.zeros((10, 10))
        
        assert result.shape == (10, 10)
        assert result.dtype == np.uint8
        assert np.all(result == 0)

    def test_zeros_3d(self):
        """Test creating 3D zeros array."""
        adapter = NumPyImageAdapter()
        
        result = adapter.zeros((30, 100, 3))
        
        assert result.shape == (30, 100, 3)
        assert result.dtype == np.uint8
        assert np.all(result == 0)

    def test_resize_2d(self):
        """Test resizing 2D array."""
        adapter = NumPyImageAdapter()
        data = np.zeros((50, 50), dtype=np.uint8)
        
        result = adapter.resize(data, (100, 100))
        
        assert result.shape == (100, 100)

    def test_resize_3d(self):
        """Test resizing 3D array."""
        adapter = NumPyImageAdapter()
        data = np.zeros((50, 50, 3), dtype=np.uint8)
        
        result = adapter.resize(data, (100, 100))
        
        assert result.shape == (100, 100, 3)

    def test_resize_preserves_dtype(self):
        """Test that resize preserves dtype."""
        adapter = NumPyImageAdapter()
        data = np.zeros((50, 50, 3), dtype=np.uint8)
        
        result = adapter.resize(data, (100, 100))
        
        assert result.dtype == np.uint8

    def test_vstack_multiple_arrays(self):
        """Test vertical stacking of multiple arrays."""
        adapter = NumPyImageAdapter()
        arrays = [
            np.zeros((10, 10, 3), dtype=np.uint8),
            np.zeros((20, 10, 3), dtype=np.uint8),
            np.zeros((15, 10, 3), dtype=np.uint8),
        ]
        
        result = adapter.vstack(arrays)
        
        assert result.shape == (45, 10, 3)

    def test_hstack_multiple_arrays(self):
        """Test horizontal stacking of multiple arrays."""
        adapter = NumPyImageAdapter()
        arrays = [
            np.zeros((10, 10, 3), dtype=np.uint8),
            np.zeros((10, 20, 3), dtype=np.uint8),
            np.zeros((10, 15, 3), dtype=np.uint8),
        ]
        
        result = adapter.hstack(arrays)
        
        assert result.shape == (10, 45, 3)
