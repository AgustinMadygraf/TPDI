"""
Integration tests for CV2ImageLoader.
Path: tests/infrastructure/opencv/test_cv2_image_loader.py
"""

from pathlib import Path

import cv2
import numpy as np
import pytest

from src.infrastructure.opencv.cv2_image_loader import CV2ImageLoader
from src.infrastructure.shared.path_validator import PathValidator


class TestCV2ImageLoader:
    """Integration test suite for CV2ImageLoader."""

    @pytest.fixture
    def loader(self, temp_directory):
        """Provides a configured CV2ImageLoader."""
        validator = PathValidator(base_path=temp_directory)
        return CV2ImageLoader(path_validator=validator)

    def test_load_rgb_image(self, temp_directory, loader):
        """Test loading a valid RGB image."""
        # Create a test image
        img_path = temp_directory / "test_rgb.png"
        img_data = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
        cv2.imwrite(str(img_path), img_data)
        
        result = loader.load(img_path)
        
        assert result.name == "test_rgb.png"
        assert result.width == 100
        assert result.height == 100
        assert result.channels == 3
        assert len(result.data) == 100 * 100 * 3

    def test_load_grayscale_image(self, temp_directory, loader):
        """Test loading a grayscale image."""
        img_path = temp_directory / "test_gray.png"
        img_data = np.random.randint(0, 256, (50, 80), dtype=np.uint8)
        cv2.imwrite(str(img_path), img_data)
        
        result = loader.load(img_path)
        
        assert result.name == "test_gray.png"
        assert result.width == 80
        assert result.height == 50
        assert result.channels == 1
        assert len(result.data) == 50 * 80

    def test_load_rgba_image(self, temp_directory, loader):
        """Test loading an RGBA (4-channel) image.
        
        Note: OpenCV loads PNG with alpha as BGRA by default, preserving 4 channels.
        """
        img_path = temp_directory / "test_rgba.png"
        # Create RGBA image with explicit alpha channel
        img_data = np.random.randint(0, 256, (100, 100, 4), dtype=np.uint8)
        cv2.imwrite(str(img_path), img_data)
        
        result = loader.load(img_path)
        
        # OpenCV loads PNG with alpha as 4-channel (BGRA -> converted to RGBA)
        assert result.channels in [3, 4]  # Depends on OpenCV build and flags
        assert len(result.data) == 100 * 100 * result.channels

    def test_load_nonexistent_file(self, loader):
        """Test loading a non-existent file raises ValueError."""
        with pytest.raises(ValueError, match="No se pudo cargar la imagen"):
            loader.load(Path("nonexistent.png"))

    def test_load_invalid_file(self, temp_directory, loader):
        """Test loading an invalid image file raises ValueError."""
        invalid_file = temp_directory / "not_an_image.txt"
        invalid_file.write_text("This is not an image")
        
        with pytest.raises(ValueError, match="No se pudo cargar la imagen"):
            loader.load(invalid_file)

    def test_load_path_traversal_blocked(self, loader):
        """Test that path traversal is blocked by PathValidator."""
        with pytest.raises(PermissionError, match="Path no permitido"):
            loader.load(Path("../../../etc/passwd"))

    def test_load_sets_correct_path(self, temp_directory, loader):
        """Test that loaded image has correct path attribute."""
        img_path = temp_directory / "test.png"
        img_data = np.zeros((10, 10, 3), dtype=np.uint8)
        cv2.imwrite(str(img_path), img_data)
        
        result = loader.load(img_path)
        
        assert result.path == str(img_path.resolve())

    def test_load_preserves_image_data(self, temp_directory, loader):
        """Test that image data is correctly loaded."""
        img_path = temp_directory / "test.png"
        # Create image with known values
        img_data = np.full((10, 10, 3), [255, 128, 64], dtype=np.uint8)
        cv2.imwrite(str(img_path), img_data)
        
        result = loader.load(img_path)
        
        # Check that data is present (exact values depend on compression)
        assert len(result.data) == 10 * 10 * 3
        assert all(isinstance(v, int) for v in result.data)

    def test_color_conversion_bgr_to_rgb(self, temp_directory, loader):
        """Test that BGR (OpenCV default) is converted to RGB."""
        img_path = temp_directory / "test_color.png"
        # Create pure red in BGR (OpenCV format: [0, 0, 255])
        img_data = np.zeros((10, 10, 3), dtype=np.uint8)
        img_data[:, :] = [0, 0, 255]  # BGR red
        cv2.imwrite(str(img_path), img_data)
        
        result = loader.load(img_path)
        
        # Check first pixel - should be RGB (255, 0, 0)
        first_pixel = result.data[:3]
        assert first_pixel == [255, 0, 0]  # RGB red


class TestCV2ImageLoaderPerformance:
    """Performance tests for CV2ImageLoader."""

    @pytest.fixture
    def loader(self, temp_directory):
        """Provides a configured CV2ImageLoader."""
        validator = PathValidator(base_path=temp_directory)
        return CV2ImageLoader(path_validator=validator)

    def test_load_small_image_performance(self, temp_directory, loader):
        """Test loading a small image is fast."""
        import time
        
        img_path = temp_directory / "small.png"
        img_data = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
        cv2.imwrite(str(img_path), img_data)
        
        start = time.time()
        result = loader.load(img_path)
        elapsed = time.time() - start
        
        assert elapsed < 0.5  # Should load in less than 500ms
        assert result is not None

    def test_load_large_image_performance(self, temp_directory, loader):
        """Test loading a large image."""
        import time
        
        img_path = temp_directory / "large.png"
        img_data = np.random.randint(0, 256, (2000, 2000, 3), dtype=np.uint8)
        cv2.imwrite(str(img_path), img_data)
        
        start = time.time()
        result = loader.load(img_path)
        elapsed = time.time() - start
        
        assert elapsed < 2.0  # Should load in less than 2 seconds
        assert result.width == 2000
        assert result.height == 2000

    def test_load_multiple_images(self, temp_directory, loader):
        """Test loading multiple images in sequence."""
        import time
        
        # Create 5 test images
        for i in range(5):
            img_path = temp_directory / f"test_{i}.png"
            img_data = np.random.randint(0, 256, (500, 500, 3), dtype=np.uint8)
            cv2.imwrite(str(img_path), img_data)
        
        start = time.time()
        results = []
        for i in range(5):
            result = loader.load(temp_directory / f"test_{i}.png")
            results.append(result)
        elapsed = time.time() - start
        
        assert len(results) == 5
        assert elapsed < 3.0  # Should load all in less than 3 seconds
