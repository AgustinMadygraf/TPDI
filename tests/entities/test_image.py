"""
Unit tests for Image entity.
Path: tests/entities/test_image.py
"""

import pytest

from src.entities.image import Image


class TestImage:
    """Test suite for Image entity."""

    def test_image_creation(self):
        """Test basic image creation."""
        image = Image(
            name="test.jpg",
            width=100,
            height=200,
            channels=3,
            data=[0] * 60000,
            path="/tmp/test.jpg"
        )
        
        assert image.name == "test.jpg"
        assert image.width == 100
        assert image.height == 200
        assert image.channels == 3
        assert image.path == "/tmp/test.jpg"

    def test_image_size_property(self):
        """Test size property calculation."""
        image = Image(
            name="test.jpg",
            width=10,
            height=20,
            channels=3,
            data=[0] * 600,
            path="/tmp/test.jpg"
        )
        
        assert image.size == 600  # 10 * 20 * 3

    def test_image_size_property_grayscale(self):
        """Test size property for grayscale image."""
        image = Image(
            name="test.jpg",
            width=10,
            height=20,
            channels=1,
            data=[0] * 200,
            path="/tmp/test.jpg"
        )
        
        assert image.size == 200  # 10 * 20 * 1

    def test_get_pixel_valid(self):
        """Test getting a valid pixel."""
        data = [255, 0, 0] * 4  # 2x2 RGB image, red pixels
        image = Image(
            name="test.jpg",
            width=2,
            height=2,
            channels=3,
            data=data,
            path="/tmp/test.jpg"
        )
        
        pixel = image.get_pixel(0, 0)
        assert pixel == (255, 0, 0)

    def test_get_pixel_different_positions(self):
        """Test getting pixels at different positions."""
        # Create 2x2 image with different colors
        data = [
            255, 0, 0,    # (0,0) - Red
            0, 255, 0,    # (1,0) - Green
            0, 0, 255,    # (0,1) - Blue
            255, 255, 0   # (1,1) - Yellow
        ]
        image = Image(
            name="test.jpg",
            width=2,
            height=2,
            channels=3,
            data=data,
            path="/tmp/test.jpg"
        )
        
        assert image.get_pixel(0, 0) == (255, 0, 0)
        assert image.get_pixel(1, 0) == (0, 255, 0)
        assert image.get_pixel(0, 1) == (0, 0, 255)
        assert image.get_pixel(1, 1) == (255, 255, 0)

    def test_get_pixel_out_of_bounds_x_negative(self):
        """Test getting pixel with negative x coordinate."""
        image = Image(
            name="test.jpg",
            width=10,
            height=10,
            channels=3,
            data=[0] * 300,
            path="/tmp/test.jpg"
        )
        
        with pytest.raises(ValueError, match="Coordenadas fuera de rango"):
            image.get_pixel(-1, 5)

    def test_get_pixel_out_of_bounds_x_too_large(self):
        """Test getting pixel with x >= width."""
        image = Image(
            name="test.jpg",
            width=10,
            height=10,
            channels=3,
            data=[0] * 300,
            path="/tmp/test.jpg"
        )
        
        with pytest.raises(ValueError, match="Coordenadas fuera de rango"):
            image.get_pixel(10, 5)

    def test_get_pixel_out_of_bounds_y_negative(self):
        """Test getting pixel with negative y coordinate."""
        image = Image(
            name="test.jpg",
            width=10,
            height=10,
            channels=3,
            data=[0] * 300,
            path="/tmp/test.jpg"
        )
        
        with pytest.raises(ValueError, match="Coordenadas fuera de rango"):
            image.get_pixel(5, -1)

    def test_get_pixel_out_of_bounds_y_too_large(self):
        """Test getting pixel with y >= height."""
        image = Image(
            name="test.jpg",
            width=10,
            height=10,
            channels=3,
            data=[0] * 300,
            path="/tmp/test.jpg"
        )
        
        with pytest.raises(ValueError, match="Coordenadas fuera de rango"):
            image.get_pixel(5, 10)

    def test_image_optional_path(self):
        """Test image creation without optional path."""
        image = Image(
            name="test.jpg",
            width=10,
            height=10,
            channels=3,
            data=[0] * 300
        )
        
        assert image.path is None
