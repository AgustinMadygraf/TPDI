"""
Path: src/infrastructure/shared/path_validator.py
"""

from pathlib import Path
from typing import Optional


class PathValidator:
    "Valida que los paths estén dentro de un directorio base permitido."
    def __init__(self, base_path: Optional[Path] = None):
        "Inicializa el validador con un directorio base. Si no se proporciona, se usa 'data/input'."
        self._base_path = (base_path or Path("data/input")).resolve()

    def validate(self, path: Path) -> Path:
        "Valida que el path esté dentro del directorio base permitido. Devuelve el path resuelto si es válido."
        resolved = (self._base_path / path).resolve()
        try:
            resolved.relative_to(self._base_path)
        except ValueError as exc:
            raise PermissionError(f"Path no permitido: {path}") from exc

        return resolved
