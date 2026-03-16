"""
Path: run.py
"""

from src.infrastructure.cli.app import CLIApp

def main() -> None:
    "Punto de entrada principal."
    app = CLIApp()
    app.run()

if __name__ == "__main__":
    main()
