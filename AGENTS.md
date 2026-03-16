# AGENTS.md - TPDI Project Guide

> **TPDI** - Técnicas de Procesamiento Digital de Imágenes  
> Digital Image Processing Techniques - A Python desktop application following Clean Architecture principles.

---

## Project Overview

TPDI is an educational/professional desktop application for digital image processing, built with Python. It provides an interactive GUI for applying various image processing techniques using industry-standard libraries.

### Key Characteristics

- **Type**: Desktop GUI application for image processing
- **Language**: Python 3.x
- **Architecture**: Clean Architecture (Robert C. Martin / Uncle Bob)
- **Domain**: Digital Image Processing (Procesamiento Digital de Imágenes)
- **Status**: Initial project structure created, awaiting implementation

---

## Technology Stack

### Core Dependencies

| Library | Purpose | Location in Project |
|---------|---------|---------------------|
| **OpenCV** (`opencv-python`) | Image processing operations (filters, transformations, computer vision) | `src/infrastructure/opencv/` |
| **NumPy** | Numerical arrays and matrix operations for image data | `src/infrastructure/numpy/` |
| **Tkinter** | Native Python GUI framework for desktop interface | `src/infrastructure/tkinter/` |

### Development Tools (Recommended)

- **pytest** - Unit and integration testing
- **mypy** - Static type checking
- **black** / **ruff** - Code formatting and linting
- **pip** / **uv** - Dependency management

---

## Project Structure

This project follows **Clean Architecture** with a clear separation of concerns across four layers:

```
TPDI/
├── run.py                          # Application entry point
├── .gitignore                      # Git ignore patterns
├── docs/                           # Documentation directory
├── tests/                          # Test suite (mirror src structure)
└── src/
    ├── entities/                   # Domain Layer - Core business entities
    │   └── .gitkeep
    ├── use_cases/                  # Application Layer - Business logic, workflows
    │   └── .gitkeep
    ├── interface_adapters/         # Interface Adapters Layer
    │   ├── controllers/            # Input handling, use case invocation
    │   ├── gateways/               # Data mapping between domain and external
    │   └── presenters/             # Output formatting for UI
    └── infrastructure/             # Frameworks & Drivers Layer
        ├── numpy/                  # NumPy array operations adapter
        ├── opencv/                 # OpenCV image processing adapter
        ├── settings/               # Configuration and logging
        │   ├── config.py/          # Configuration management
        │   └── logger.py           # Logging infrastructure
        └── tkinter/                # Tkinter GUI adapter
```

### Clean Architecture Dependency Rule

```
┌─────────────────────────────────────────────┐
│  Frameworks & Drivers (Infrastructure)      │  ← Outer layer - Most volatile
│  (OpenCV, Tkinter, NumPy, Filesystem)       │
├─────────────────────────────────────────────┤
│  Interface Adapters                         │
│  (Controllers, Presenters, Gateways)        │
├─────────────────────────────────────────────┤
│  Use Cases (Application)                    │  ← Business logic
│  (ApplyFilter, SaveImage, LoadImage, etc.)  │
├─────────────────────────────────────────────┤
│  Entities (Domain)                          │  ← Core - Most stable
│  (Image, Pixel, Filter, Histogram, etc.)    │
└─────────────────────────────────────────────┘
```

**Critical Rule**: Dependencies only point INWARD. Inner layers know nothing about outer layers.

---

## Build and Run Commands

### Environment Setup

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux/Mac)
source venv/bin/activate

# Install dependencies (when requirements.txt or pyproject.toml exists)
pip install -r requirements.txt
# or
pip install -e .
```

### Running the Application

```bash
# Run the application
python run.py
```

### Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test module
pytest tests/test_entities.py
```

---

## Code Style Guidelines

### Python Style

- Follow **PEP 8** style guide
- Use **type hints** for all function signatures
- Maximum line length: 100 characters
- Use **docstrings** (Google style or NumPy style) for all public modules, classes, and functions

### Clean Architecture Conventions

1. **Entities Layer** (`src/entities/`)
   - Pure Python classes with no external dependencies
   - Define core business rules (e.g., `Image`, `Filter`, `Region`)
   - Must be testable without any framework

2. **Use Cases Layer** (`src/use_cases/`)
   - Orchestrate flow between entities
   - Define interfaces (ports) for dependencies
   - One use case per file (e.g., `apply_filter.py`, `save_image.py`)

3. **Interface Adapters** (`src/interface_adapters/`)
   - **Controllers**: Handle user input, validate data, call use cases
   - **Presenters**: Format data for display
   - **Gateways**: Abstract data sources (filesystem, camera, etc.)

4. **Infrastructure** (`src/infrastructure/`)
   - Contains all framework-specific code
   - Implements interfaces defined in inner layers
   - OpenCV operations, Tkinter widgets, NumPy arrays here

### Naming Conventions

| Element | Convention | Example |
|---------|------------|---------|
| Modules | snake_case | `image_processor.py` |
| Classes | PascalCase | `ImageProcessor` |
| Functions | snake_case | `apply_filter()` |
| Constants | UPPER_SNAKE_CASE | `MAX_IMAGE_SIZE` |
| Private | _leading_underscore | `_internal_helper()` |
| Abstract classes | PascalCase + "Port" suffix | `ImageRepositoryPort` |
| Implementations | PascalCase + impl suffix | `OpenCVImageProcessor` |

---

## Testing Strategy

### Test Organization

Mirror the `src/` structure in `tests/`:

```
tests/
├── entities/
├── use_cases/
├── interface_adapters/
└── infrastructure/
```

### Test Types

1. **Unit Tests** - Test entities and use cases in isolation
   - Mock all external dependencies
   - Fast execution (< 100ms per test)

2. **Integration Tests** - Test interface adapters with real implementations
   - Test actual OpenCV operations
   - Test file I/O with temporary directories

3. **E2E Tests** (if applicable) - Test complete workflows
   - GUI testing with pytest-tkinter or similar

### Testing Conventions

- Use `pytest` fixtures for common setup
- Name tests descriptively: `test_apply_grayscale_filter_to_rgb_image()`
- One assertion concept per test
- Use `given-when-then` comments for clarity

---

## Security Considerations

### File Handling

- **Always validate** image file formats before processing
- **Sanitize file paths** to prevent directory traversal attacks
- **Limit file sizes** to prevent memory exhaustion
- Use temporary directories for intermediate processing

### Image Processing Security

- Validate image dimensions before processing (prevent decompression bombs)
- Handle malformed images gracefully (try/except around OpenCV calls)
- Be cautious with user-provided filter parameters

### Dependencies

- Keep OpenCV and NumPy updated for security patches
- Pin dependency versions in `requirements.txt` or `pyproject.toml`
- Use `pip-audit` to check for known vulnerabilities

---

## Development Workflow

### Adding a New Feature

1. **Start from the center**: Define entities in `src/entities/`
2. **Define use case**: Implement business logic in `src/use_cases/`
3. **Create interfaces**: Define ports (abstract classes) in use cases
4. **Implement adapters**: Create concrete implementations in `src/infrastructure/`
5. **Wire it up**: Connect through controllers in `src/interface_adapters/controllers/`

### Example: Adding a Blur Filter

```
1. src/entities/filter.py          → Define Filter entity
2. src/use_cases/apply_blur.py     → Define ApplyBlur use case
3. src/infrastructure/opencv/blur_adapter.py  → Implement with OpenCV
4. src/interface_adapters/controllers/blur_controller.py  → UI integration
```

---

## Documentation

### Project Documentation (`docs/`)

- `docs/todo.md` - Current tasks and backlog (managed by skills)
- `docs/todo.done.md` - Completed tasks
- `docs/decisions/` - Architecture Decision Records (ADRs)
- `docs/decisions/preguntas-arquitectura.md` - Pending architectural questions

### Code Documentation

- All public APIs must have docstrings
- Complex algorithms should have inline comments
- README files in each layer explaining its purpose

---

## Available Skills

This project has several specialized skills available:

| Skill | Purpose |
|-------|---------|
| `code-audit` | Security, Clean Architecture, SOLID analysis |
| `skill-backend-code-audit` | Python/FastAPI specific security/performance |
| `todo-workflow` | Automated task processing |
| `docs-maintainer` | Documentation synchronization |

---

## Common Commands Reference

```bash
# Development
python run.py                           # Run application
python -m pytest                        # Run tests
python -m pytest -xvs                   # Run tests verbose, stop on first failure
python -m mypy src/                     # Type checking
python -m black src/ tests/             # Format code
python -m ruff check src/               # Lint code

# Dependencies
pip freeze > requirements.txt           # Save current dependencies
pip install -r requirements.txt         # Install dependencies
pip list --outdated                     # Check for updates

# Git
git log --oneline -10                   # View recent commits
git status                              # Check working tree
```

---

## Notes for AI Agents

1. **This is a new project** - All source files are currently empty (`.gitkeep` placeholders only)
2. **Follow Clean Architecture strictly** - Never let inner layers depend on outer layers
3. **Use type hints** - All functions should have proper type annotations
4. **Write tests** - Every new feature should include corresponding tests
5. **Document decisions** - If you make architectural choices, document them in `docs/decisions/`
6. **Spanish context** - Project name suggests Spanish-language educational/professional context

---

## Resources

- **Clean Architecture Book**: Robert C. Martin - Clean Architecture: A Craftsman's Guide
- **OpenCV Docs**: https://docs.opencv.org/
- **Tkinter Docs**: https://docs.python.org/3/library/tkinter.html
- **NumPy Docs**: https://numpy.org/doc/

---

*Last updated: 2026-03-16*
*Project initialized: 2026-03-16*
