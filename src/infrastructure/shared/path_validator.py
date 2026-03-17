"""
Path: src/infrastructure/shared/path_validator.py

Validador de paths para seguridad (path traversal prevention).
Agnóstico al dominio, reutilizable.
"""

from pathlib import Path
from typing import Optional


class PathValidator:
    """Valida que los paths estén dentro de un directorio base permitido."""

    def __init__(self, base_path: Optional[Path] = None):
        """Inicializa el validador con un directorio base.

        Args:
            base_path: Directorio base permitido. Si es None, usa "data/input".
        """
        self._base_path = (base_path or Path("data/input")).resolve()

    def validate(self, path: Path) -> Path:
        """Valida que el path resuelto esté dentro del directorio base.

        Args:
            path: El path a validar (relativo o absoluto).

        Returns:
            El path resuelto y validado.

        Raises:
            PermissionError: Si el path resuelto está fuera del directorio base.
        """
        # Resolver el path contra base_path para normalizar
        resolved = (self._base_path / path).resolve()

        # Validar que esté dentro de base_path
        try:
            resolved.relative_to(self._base_path)
        except ValueError as exc:
            raise PermissionError(f"Path no permitido: {path}") from exc

        return resolved
