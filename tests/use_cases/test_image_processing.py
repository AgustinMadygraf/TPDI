"""
Tests for image processing use cases.
Path: tests/use_cases/test_image_processing.py
"""

import pytest

from src.entities.image import Image
from src.use_cases.image_processing import (
    apply_grayscale,
    extract_red_channel,
    extract_green_channel,
    extract_blue_channel,
    red_to_grayscale,
    green_to_grayscale,
    blue_to_grayscale
)


class TestApplyGrayscale:
    """Test suite for apply_grayscale function."""

    def test_apply_grayscale_returns_new_image(self):
        """Test that apply_grayscale returns a new Image instance."""
        image = Image(
            name="test.png",
            width=2,
            height=2,
            channels=3,
            data=[255, 0, 0, 0, 255, 0, 0, 0, 255, 128, 128, 128],
            path="/tmp/test.png"
        )
        
        result = apply_grayscale(image)
        
        assert isinstance(result, Image)
        assert result is not image
        assert result.name == "test.png_grayscale"

    def test_apply_grayscale_calculates_average(self):
        """Test that grayscale is calculated as average of RGB."""
        # Pure red: (255 + 0 + 0) / 3 = 85
        image = Image(
            name="test.png",
            width=1,
            height=1,
            channels=3,
            data=[255, 0, 0],
            path="/tmp/test.png"
        )
        
        result = apply_grayscale(image)
        
        expected_gray = 85  # (255 + 0 + 0) // 3
        assert result.data == [expected_gray, expected_gray, expected_gray]

    def test_apply_grayscale_preserves_dimensions(self):
        """Test that grayscale image preserves original dimensions."""
        image = Image(
            name="test.png",
            width=100,
            height=50,
            channels=3,
            data=[128] * 15000,
            path="/tmp/test.png"
        )
        
        result = apply_grayscale(image)
        
        assert result.width == 100
        assert result.height == 50
        assert result.channels == 3  # Still RGB format

    def test_apply_grayscale_multiple_pixels(self):
        """Test grayscale conversion with multiple pixels."""
        image = Image(
            name="test.png",
            width=2,
            height=1,
            channels=3,
            data=[255, 0, 0, 0, 255, 0],  # Red, Green
            path="/tmp/test.png"
        )
        
        result = apply_grayscale(image)
        
        # Red pixel: (255 + 0 + 0) / 3 = 85
        # Green pixel: (0 + 255 + 0) / 3 = 85
        assert result.data[0:3] == [85, 85, 85]
        assert result.data[3:6] == [85, 85, 85]

    def test_apply_grayscale_already_grayscale_returns_same(self):
        """Test that grayscale image returns itself."""
        image = Image(
            name="test.png",
            width=2,
            height=2,
            channels=1,
            data=[128, 64, 32, 16],
            path="/tmp/test.png"
        )
        
        result = apply_grayscale(image)
        
        assert result is image


class TestExtractRedChannel:
    """Test suite for extract_red_channel function."""

    def test_extract_red_channel_returns_new_image(self):
        """Test that extract_red_channel returns a new Image instance."""
        image = Image(
            name="test.png",
            width=2,
            height=2,
            channels=3,
            data=[255, 128, 64, 32, 16, 8, 100, 50, 25, 10, 5, 2],
            path="/tmp/test.png"
        )
        
        result = extract_red_channel(image)
        
        assert isinstance(result, Image)
        assert result is not image
        assert result.name == "test.png_red_channel"

    def test_extract_red_channel_removes_green_blue(self):
        """Test that green and blue channels are set to zero."""
        image = Image(
            name="test.png",
            width=1,
            height=1,
            channels=3,
            data=[255, 128, 64],
            path="/tmp/test.png"
        )
        
        result = extract_red_channel(image)
        
        assert result.data == [255, 0, 0]

    def test_extract_red_channel_multiple_pixels(self):
        """Test red channel extraction with multiple pixels."""
        image = Image(
            name="test.png",
            width=2,
            height=1,
            channels=3,
            data=[255, 100, 50, 128, 64, 32],
            path="/tmp/test.png"
        )
        
        result = extract_red_channel(image)
        
        # Pixel 1: [255, 100, 50] -> [255, 0, 0]
        # Pixel 2: [128, 64, 32] -> [128, 0, 0]
        assert result.data[0:3] == [255, 0, 0]
        assert result.data[3:6] == [128, 0, 0]

    def test_extract_red_channel_preserves_dimensions(self):
        """Test that red channel image preserves original dimensions."""
        image = Image(
            name="test.png",
            width=100,
            height=50,
            channels=3,
            data=[128] * 15000,
            path="/tmp/test.png"
        )
        
        result = extract_red_channel(image)
        
        assert result.width == 100
        assert result.height == 50
        assert result.channels == 3

    def test_extract_red_channel_grayscale_returns_same(self):
        """Test that grayscale image returns itself."""
        image = Image(
            name="test.png",
            width=2,
            height=2,
            channels=1,
            data=[128, 64, 32, 16],
            path="/tmp/test.png"
        )
        
        result = extract_red_channel(image)
        
        assert result is image


class TestExtractGreenChannel:
    """Test suite for extract_green_channel function."""

    def test_extract_green_channel_returns_new_image(self):
        """Test that extract_green_channel returns a new Image instance."""
        image = Image(
            name="test.png",
            width=2,
            height=2,
            channels=3,
            data=[255, 128, 64, 32, 16, 8, 100, 50, 25, 10, 5, 2],
            path="/tmp/test.png"
        )
        
        result = extract_green_channel(image)
        
        assert isinstance(result, Image)
        assert result is not image
        assert result.name == "test.png_green_channel"

    def test_extract_green_channel_removes_red_blue(self):
        """Test that red and blue channels are set to zero."""
        image = Image(
            name="test.png",
            width=1,
            height=1,
            channels=3,
            data=[255, 128, 64],
            path="/tmp/test.png"
        )
        
        result = extract_green_channel(image)
        
        assert result.data == [0, 128, 0]

    def test_extract_green_channel_multiple_pixels(self):
        """Test green channel extraction with multiple pixels."""
        image = Image(
            name="test.png",
            width=2,
            height=1,
            channels=3,
            data=[255, 100, 50, 128, 200, 32],
            path="/tmp/test.png"
        )
        
        result = extract_green_channel(image)
        
        # Pixel 1: [255, 100, 50] -> [0, 100, 0]
        # Pixel 2: [128, 200, 32] -> [0, 200, 0]
        assert result.data[0:3] == [0, 100, 0]
        assert result.data[3:6] == [0, 200, 0]

    def test_extract_green_channel_preserves_dimensions(self):
        """Test that green channel image preserves original dimensions."""
        image = Image(
            name="test.png",
            width=100,
            height=50,
            channels=3,
            data=[128] * 15000,
            path="/tmp/test.png"
        )
        
        result = extract_green_channel(image)
        
        assert result.width == 100
        assert result.height == 50
        assert result.channels == 3

    def test_extract_green_channel_grayscale_returns_same(self):
        """Test that grayscale image returns itself."""
        image = Image(
            name="test.png",
            width=2,
            height=2,
            channels=1,
            data=[128, 64, 32, 16],
            path="/tmp/test.png"
        )
        
        result = extract_green_channel(image)
        
        assert result is image


class TestExtractBlueChannel:
    """Test suite for extract_blue_channel function."""

    def test_extract_blue_channel_returns_new_image(self):
        """Test that extract_blue_channel returns a new Image instance."""
        image = Image(
            name="test.png",
            width=2,
            height=2,
            channels=3,
            data=[255, 128, 64, 32, 16, 8, 100, 50, 25, 10, 5, 2],
            path="/tmp/test.png"
        )
        
        result = extract_blue_channel(image)
        
        assert isinstance(result, Image)
        assert result is not image
        assert result.name == "test.png_blue_channel"

    def test_extract_blue_channel_removes_red_green(self):
        """Test that red and green channels are set to zero."""
        image = Image(
            name="test.png",
            width=1,
            height=1,
            channels=3,
            data=[255, 128, 200],
            path="/tmp/test.png"
        )
        
        result = extract_blue_channel(image)
        
        assert result.data == [0, 0, 200]

    def test_extract_blue_channel_multiple_pixels(self):
        """Test blue channel extraction with multiple pixels."""
        image = Image(
            name="test.png",
            width=2,
            height=1,
            channels=3,
            data=[255, 100, 50, 128, 200, 255],
            path="/tmp/test.png"
        )
        
        result = extract_blue_channel(image)
        
        # Pixel 1: [255, 100, 50] -> [0, 0, 50]
        # Pixel 2: [128, 200, 255] -> [0, 0, 255]
        assert result.data[0:3] == [0, 0, 50]
        assert result.data[3:6] == [0, 0, 255]

    def test_extract_blue_channel_preserves_dimensions(self):
        """Test that blue channel image preserves original dimensions."""
        image = Image(
            name="test.png",
            width=100,
            height=50,
            channels=3,
            data=[128] * 15000,
            path="/tmp/test.png"
        )
        
        result = extract_blue_channel(image)
        
        assert result.width == 100
        assert result.height == 50
        assert result.channels == 3

    def test_extract_blue_channel_grayscale_returns_same(self):
        """Test that grayscale image returns itself."""
        image = Image(
            name="test.png",
            width=2,
            height=2,
            channels=1,
            data=[128, 64, 32, 16],
            path="/tmp/test.png"
        )
        
        result = extract_blue_channel(image)
        
        assert result is image


class TestRedToGrayscale:
    """Test suite for red_to_grayscale function."""

    def test_red_to_grayscale_returns_new_image(self):
        """Test that red_to_grayscale returns a new Image instance."""
        image = Image(
            name="test.png",
            width=2,
            height=2,
            channels=3,
            data=[255, 128, 64, 32, 16, 8, 100, 50, 25, 10, 5, 2],
            path="/tmp/test.png"
        )
        
        result = red_to_grayscale(image)
        
        assert isinstance(result, Image)
        assert result is not image
        assert result.name == "test.png_red_grayscale"

    def test_red_to_grayscale_replicates_red_channel(self):
        """Test that red value is replicated to all channels."""
        image = Image(
            name="test.png",
            width=1,
            height=1,
            channels=3,
            data=[200, 100, 50],
            path="/tmp/test.png"
        )
        
        result = red_to_grayscale(image)
        
        # Red value 200 replicated to R, G, B
        assert result.data == [200, 200, 200]

    def test_red_to_grayscale_multiple_pixels(self):
        """Test red to grayscale with multiple pixels."""
        image = Image(
            name="test.png",
            width=2,
            height=1,
            channels=3,
            data=[255, 0, 0, 128, 255, 0],
            path="/tmp/test.png"
        )
        
        result = red_to_grayscale(image)
        
        # Pixel 1: red=255 -> [255, 255, 255] (white)
        # Pixel 2: red=128 -> [128, 128, 128] (gray)
        assert result.data[0:3] == [255, 255, 255]
        assert result.data[3:6] == [128, 128, 128]

    def test_red_to_grayscale_preserves_dimensions(self):
        """Test that red grayscale image preserves original dimensions."""
        image = Image(
            name="test.png",
            width=100,
            height=50,
            channels=3,
            data=[128] * 15000,
            path="/tmp/test.png"
        )
        
        result = red_to_grayscale(image)
        
        assert result.width == 100
        assert result.height == 50
        assert result.channels == 3

    def test_red_to_grayscale_grayscale_returns_same(self):
        """Test that grayscale image returns itself."""
        image = Image(
            name="test.png",
            width=2,
            height=2,
            channels=1,
            data=[128, 64, 32, 16],
            path="/tmp/test.png"
        )
        
        result = red_to_grayscale(image)
        
        assert result is image


class TestGreenToGrayscale:
    """Test suite for green_to_grayscale function."""

    def test_green_to_grayscale_returns_new_image(self):
        """Test that green_to_grayscale returns a new Image instance."""
        image = Image(
            name="test.png",
            width=2,
            height=2,
            channels=3,
            data=[255, 128, 64, 32, 16, 8, 100, 50, 25, 10, 5, 2],
            path="/tmp/test.png"
        )
        
        result = green_to_grayscale(image)
        
        assert isinstance(result, Image)
        assert result is not image
        assert result.name == "test.png_green_grayscale"

    def test_green_to_grayscale_replicates_green_channel(self):
        """Test that green value is replicated to all channels."""
        image = Image(
            name="test.png",
            width=1,
            height=1,
            channels=3,
            data=[200, 150, 50],
            path="/tmp/test.png"
        )
        
        result = green_to_grayscale(image)
        
        # Green value 150 replicated to R, G, B
        assert result.data == [150, 150, 150]

    def test_green_to_grayscale_multiple_pixels(self):
        """Test green to grayscale with multiple pixels."""
        image = Image(
            name="test.png",
            width=2,
            height=1,
            channels=3,
            data=[255, 255, 0, 0, 128, 0],
            path="/tmp/test.png"
        )
        
        result = green_to_grayscale(image)
        
        # Pixel 1: green=255 -> [255, 255, 255] (white)
        # Pixel 2: green=128 -> [128, 128, 128] (gray)
        assert result.data[0:3] == [255, 255, 255]
        assert result.data[3:6] == [128, 128, 128]

    def test_green_to_grayscale_preserves_dimensions(self):
        """Test that green grayscale image preserves original dimensions."""
        image = Image(
            name="test.png",
            width=100,
            height=50,
            channels=3,
            data=[128] * 15000,
            path="/tmp/test.png"
        )
        
        result = green_to_grayscale(image)
        
        assert result.width == 100
        assert result.height == 50
        assert result.channels == 3

    def test_green_to_grayscale_grayscale_returns_same(self):
        """Test that grayscale image returns itself."""
        image = Image(
            name="test.png",
            width=2,
            height=2,
            channels=1,
            data=[128, 64, 32, 16],
            path="/tmp/test.png"
        )
        
        result = green_to_grayscale(image)
        
        assert result is image


class TestBlueToGrayscale:
    """Test suite for blue_to_grayscale function."""

    def test_blue_to_grayscale_returns_new_image(self):
        """Test that blue_to_grayscale returns a new Image instance."""
        image = Image(
            name="test.png",
            width=2,
            height=2,
            channels=3,
            data=[255, 128, 64, 32, 16, 8, 100, 50, 25, 10, 5, 2],
            path="/tmp/test.png"
        )
        
        result = blue_to_grayscale(image)
        
        assert isinstance(result, Image)
        assert result is not image
        assert result.name == "test.png_blue_grayscale"

    def test_blue_to_grayscale_replicates_blue_channel(self):
        """Test that blue value is replicated to all channels."""
        image = Image(
            name="test.png",
            width=1,
            height=1,
            channels=3,
            data=[200, 100, 150],
            path="/tmp/test.png"
        )
        
        result = blue_to_grayscale(image)
        
        # Blue value 150 replicated to R, G, B
        assert result.data == [150, 150, 150]

    def test_blue_to_grayscale_multiple_pixels(self):
        """Test blue to grayscale with multiple pixels."""
        image = Image(
            name="test.png",
            width=2,
            height=1,
            channels=3,
            data=[255, 0, 255, 0, 0, 128],
            path="/tmp/test.png"
        )
        
        result = blue_to_grayscale(image)
        
        # Pixel 1: blue=255 -> [255, 255, 255] (white)
        # Pixel 2: blue=128 -> [128, 128, 128] (gray)
        assert result.data[0:3] == [255, 255, 255]
        assert result.data[3:6] == [128, 128, 128]

    def test_blue_to_grayscale_preserves_dimensions(self):
        """Test that blue grayscale image preserves original dimensions."""
        image = Image(
            name="test.png",
            width=100,
            height=50,
            channels=3,
            data=[128] * 15000,
            path="/tmp/test.png"
        )
        
        result = blue_to_grayscale(image)
        
        assert result.width == 100
        assert result.height == 50
        assert result.channels == 3

    def test_blue_to_grayscale_grayscale_returns_same(self):
        """Test that grayscale image returns itself."""
        image = Image(
            name="test.png",
            width=2,
            height=2,
            channels=1,
            data=[128, 64, 32, 16],
            path="/tmp/test.png"
        )
        
        result = blue_to_grayscale(image)
        
        assert result is image


class TestImageProcessingIntegration:
    """Integration tests for image processing functions."""

    def test_processing_pipeline(self):
        """Test that multiple processing operations can be chained."""
        image = Image(
            name="test.png",
            width=2,
            height=2,
            channels=3,
            data=[
                255, 128, 64,   # Pixel 1: orange-ish
                128, 255, 64,   # Pixel 2: green-ish
                64, 128, 255,   # Pixel 3: blue-ish
                200, 100, 50    # Pixel 4: brown-ish
            ],
            path="/tmp/test.png"
        )
        
        # Apply all transformations
        grayscale = apply_grayscale(image)
        red_channel = extract_red_channel(image)
        green_channel = extract_green_channel(image)
        blue_channel = extract_blue_channel(image)
        red_gray = red_to_grayscale(image)
        green_gray = green_to_grayscale(image)
        blue_gray = blue_to_grayscale(image)
        
        # Verify all results are independent
        assert grayscale is not image
        assert red_channel is not image
        assert green_channel is not image
        assert blue_channel is not image
        assert red_gray is not image
        assert green_gray is not image
        assert blue_gray is not image
        
        # Verify original is unchanged
        assert image.data[0] == 255
        assert image.data[1] == 128
        assert image.data[2] == 64

    def test_all_channel_extractions_different(self):
        """Test that all channel extractions produce different results."""
        image = Image(
            name="test.png",
            width=3,
            height=1,
            channels=3,
            data=[
                255, 0, 0,      # Pure red
                0, 255, 0,      # Pure green
                0, 0, 255       # Pure blue
            ],
            path="/tmp/test.png"
        )
        
        red_channel = extract_red_channel(image)
        green_channel = extract_green_channel(image)
        blue_channel = extract_blue_channel(image)
        
        # First pixel (pure red): red=255, green=0, blue=0
        assert red_channel.data[0:3] == [255, 0, 0]    # Red channel keeps R
        assert green_channel.data[0:3] == [0, 0, 0]    # Green channel is 0
        assert blue_channel.data[0:3] == [0, 0, 0]     # Blue channel is 0
        
        # Second pixel (pure green): red=0, green=255, blue=0
        assert red_channel.data[3:6] == [0, 0, 0]      # Red channel is 0
        assert green_channel.data[3:6] == [0, 255, 0]  # Green channel keeps G
        assert blue_channel.data[3:6] == [0, 0, 0]     # Blue channel is 0
        
        # Third pixel (pure blue): red=0, green=0, blue=255
        assert red_channel.data[6:9] == [0, 0, 0]      # Red channel is 0
        assert green_channel.data[6:9] == [0, 0, 0]    # Green channel is 0
        assert blue_channel.data[6:9] == [0, 0, 255]   # Blue channel keeps B

    def test_all_grayscale_conversions_different(self):
        """Test that all channel grayscale conversions produce different results."""
        image = Image(
            name="test.png",
            width=3,
            height=1,
            channels=3,
            data=[
                255, 128, 64,   # Red > Green > Blue
                64, 192, 128,   # Green > Blue > Red
                128, 64, 255    # Blue > Red > Green
            ],
            path="/tmp/test.png"
        )
        
        red_gray = red_to_grayscale(image)
        green_gray = green_to_grayscale(image)
        blue_gray = blue_to_grayscale(image)
        
        # First pixel: red=255, green=128, blue=64
        assert red_gray.data[0:3] == [255, 255, 255]    # Based on red
        assert green_gray.data[0:3] == [128, 128, 128]  # Based on green
        assert blue_gray.data[0:3] == [64, 64, 64]      # Based on blue
        
        # Second pixel: red=64, green=192, blue=128
        assert red_gray.data[3:6] == [64, 64, 64]       # Based on red
        assert green_gray.data[3:6] == [192, 192, 192]  # Based on green
        assert blue_gray.data[3:6] == [128, 128, 128]   # Based on blue
        
        # Third pixel: red=128, green=64, blue=255
        assert red_gray.data[6:9] == [128, 128, 128]    # Based on red
        assert green_gray.data[6:9] == [64, 64, 64]     # Based on green
        assert blue_gray.data[6:9] == [255, 255, 255]   # Based on blue
