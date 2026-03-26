"""
Integration and security tests for PathValidator.
Path: tests/infrastructure/shared/test_path_validator.py
"""

from pathlib import Path

import pytest

from src.infrastructure.settings.path_validator import PathValidator


class TestPathValidator:
    """Test suite for PathValidator."""

    def test_validate_relative_path(self, temp_directory):
        """Test validating a relative path."""
        validator = PathValidator(base_path=temp_directory)
        (temp_directory / "subdir").mkdir()
        (temp_directory / "subdir" / "file.txt").touch()
        
        result = validator.validate(Path("subdir/file.txt"))
        
        assert result == (temp_directory / "subdir/file.txt").resolve()

    def test_validate_absolute_path_within_base(self, temp_directory):
        """Test validating an absolute path within base."""
        validator = PathValidator(base_path=temp_directory)
        (temp_directory / "file.txt").touch()
        
        absolute_path = temp_directory / "file.txt"
        result = validator.validate(absolute_path)
        
        assert result == absolute_path.resolve()

    def test_validate_resolves_to_absolute(self, temp_directory):
        """Test that validate returns absolute path."""
        validator = PathValidator(base_path=temp_directory)
        (temp_directory / "file.txt").touch()
        
        result = validator.validate(Path("file.txt"))
        
        assert result.is_absolute()


class TestPathValidatorSecurity:
    """Security tests for PathValidator - Path Traversal prevention."""

    def test_path_traversal_parent_directory(self, temp_directory):
        """Test that '../' traversal is blocked."""
        validator = PathValidator(base_path=temp_directory)
        
        with pytest.raises(PermissionError, match="Path no permitido"):
            validator.validate(Path("../secret.txt"))

    def test_path_traversal_multiple_parents(self, temp_directory):
        """Test that multiple '../' traversal is blocked."""
        validator = PathValidator(base_path=temp_directory)
        
        with pytest.raises(PermissionError, match="Path no permitido"):
            validator.validate(Path("../../../etc/passwd"))

    def test_path_traversal_mixed_valid_and_invalid(self, temp_directory):
        """Test traversal with mixed valid and invalid components."""
        validator = PathValidator(base_path=temp_directory)
        (temp_directory / "subdir").mkdir()
        
        with pytest.raises(PermissionError, match="Path no permitido"):
            validator.validate(Path("subdir/../../../etc/passwd"))

    def test_path_traversal_absolute_outside_base(self, temp_directory):
        """Test that absolute path outside base is blocked."""
        validator = PathValidator(base_path=temp_directory)
        outside_path = Path("/etc/passwd")
        
        with pytest.raises(PermissionError, match="Path no permitido"):
            validator.validate(outside_path)

    def test_path_traversal_dot_slash(self, temp_directory):
        """Test that './' prefix doesn't bypass validation."""
        validator = PathValidator(base_path=temp_directory)
        (temp_directory / "file.txt").touch()
        
        result = validator.validate(Path("./file.txt"))
        
        assert result.is_absolute()
        assert result.name == "file.txt"

    def test_path_traversal_double_slash(self, temp_directory):
        """Test that '//' doesn't bypass validation."""
        validator = PathValidator(base_path=temp_directory)
        (temp_directory / "file.txt").touch()
        
        result = validator.validate(Path("subdir//../file.txt"))
        
        assert result.is_absolute()
        assert result.name == "file.txt"

    def test_path_traversal_symlink_attempt(self, temp_directory):
        """Test handling of potential symlink traversal."""
        validator = PathValidator(base_path=temp_directory)
        
        # Even if the path looks like it might be a symlink target,
        # the validation should check the resolved path
        with pytest.raises(PermissionError, match="Path no permitido"):
            validator.validate(Path("/tmp/../etc/passwd"))

    def test_null_bytes_not_allowed(self, temp_directory):
        """Test that null bytes are handled (if relevant to OS)."""
        validator = PathValidator(base_path=temp_directory)
        
        # Pathlib should handle this, but we verify behavior
        with pytest.raises((PermissionError, ValueError)):
            validator.validate(Path("file.txt\x00"))

    def test_very_long_path(self, temp_directory):
        """Test handling of very long paths."""
        validator = PathValidator(base_path=temp_directory)
        (temp_directory / "file.txt").touch()
        
        # Create a valid but long path
        long_path = Path("a" * 100) / "file.txt"
        (temp_directory / long_path.parent).mkdir(parents=True, exist_ok=True)
        (temp_directory / long_path).touch()
        
        result = validator.validate(long_path)
        
        assert result.is_absolute()


class TestPathValidatorEdgeCases:
    """Edge case tests for PathValidator."""

    def test_default_base_path(self):
        """Test that default base path is data/input."""
        validator = PathValidator()
        
        assert validator._base_path == Path("data/input").resolve()

    def test_custom_base_path(self, temp_directory):
        """Test setting custom base path."""
        custom_path = temp_directory / "custom"
        custom_path.mkdir()
        
        validator = PathValidator(base_path=custom_path)
        
        assert validator._base_path == custom_path.resolve()

    def test_empty_path(self, temp_directory):
        """Test validating empty/current directory path."""
        validator = PathValidator(base_path=temp_directory)
        (temp_directory / "file.txt").touch()
        
        result = validator.validate(Path("."))
        
        assert result == temp_directory.resolve()

    def test_path_with_spaces(self, temp_directory):
        """Test path with spaces."""
        validator = PathValidator(base_path=temp_directory)
        (temp_directory / "file with spaces.txt").touch()
        
        result = validator.validate(Path("file with spaces.txt"))
        
        assert result.name == "file with spaces.txt"

    def test_path_with_unicode(self, temp_directory):
        """Test path with unicode characters."""
        validator = PathValidator(base_path=temp_directory)
        (temp_directory / "imagen_ñáéíóú.png").touch()
        
        result = validator.validate(Path("imagen_ñáéíóú.png"))
        
        assert "ñáéíóú" in result.name

    def test_base_path_is_resolved(self, temp_directory):
        """Test that base path is resolved to absolute."""
        relative_path = temp_directory / "subdir_for_resolve"
        relative_path.mkdir()
        
        validator = PathValidator(base_path=relative_path)
        
        assert validator._base_path.is_absolute()
