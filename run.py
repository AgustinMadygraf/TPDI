#!/usr/bin/env python3
"""
TPDI - Técnicas de Procesamiento Digital de Imágenes
Punto de entrada CLI de la aplicación.
"""
from pathlib import Path

from src.infrastructure.opencv import CV2ImageAdapter
from src.use_cases.load_images import LoadImagesFromDirectory


def main():
    """Carga y visualiza las imágenes en data/input/."""
    input_dir = Path("data/input")
    
    print("=" * 50)
    print("TPDI - Procesamiento Digital de Imágenes")
    print("=" * 50)
    print(f"\nCargando imágenes desde: {input_dir}")
    
    adapter = CV2ImageAdapter()
    use_case = LoadImagesFromDirectory(adapter)
    images = use_case.execute(input_dir)
    
    if not images:
        print("\n[!] No se encontraron imágenes.")
        print(f"   Coloca imágenes en: {input_dir.absolute()}")
        return
    
    print(f"\n[OK] Cargadas {len(images)} imagen(es):\n")
    
    for i, img in enumerate(images, 1):
        print(f"  [{i}] {img.name}")
        print(f"      Tamaño: {img.width} x {img.height} px")
        print(f"      Canales: {img.channels}")
    
    print("\n" + "=" * 50)
    
    # Mostrar primera imagen
    if images:
        adapter.display(images[0])
    
    print("\nVisor cerrado.")


if __name__ == "__main__":
    main()
