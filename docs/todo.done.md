# Tareas Completadas - TPDI

> Fecha de procesamiento: 2026-03-16  
> Skill: todo-workflow

---

## CERTEZAS Ejecutadas (Automático)

### [COMPLETADO] Path Traversal en CV2ImageAdapter
- **Archivo**: `src/infrastructure/opencv/cv2_image_adapter.py`
- **Cambio**: Agregado parámetro `base_path` al constructor y método `_validate_path()`
- **Validación**: Todos los paths se resuelven y validan contra el directorio base
- **Fix adicional**: Corregido path resolution en `LoadImagesFromDirectory` para usar paths absolutos
- **Fecha**: 2026-03-16

### [COMPLETADO] Bypass de validación en ImageGateway
- **Archivo**: `src/interface_adapters/gateways/image_gateway.py`
- **Cambio**: Reescrita la lógica de `load()` para SIEMPRE validar paths (absolutos y relativos)
- **Método agregado**: `_validate_path()` que resuelve y valida contra `base_path`
- **Fecha**: 2026-03-16

### [COMPLETADO] Silenciamiento de errores en LoadImagesFromDirectory
- **Archivo**: `src/use_cases/load_images.py`
- **Cambio**: Reemplazado `pass` por `logging.getLogger(__name__).warning(...)`
- **Beneficio**: Los errores de carga ahora son visibles en logs para diagnóstico
- **Fecha**: 2026-03-16

---

## DUDAS BAJO NIVEL Ejecutadas (Decisión del Agente)

### [COMPLETADO] Acoplamiento en CLIApp - Decisión: Inyección desde run.py
| Opción | Pros | Contras | Decisión |
|--------|------|---------|----------|
| A. Inyectar desde run.py | Máxima flexibilidad, testeable | Cambio en entry point | ✅ ELEGIDA |
| B. Factory pattern | Encapsula creación | Más complejo | ❌ |
| C. Mantener como está | Sin cambios | Difícil de testear | ❌ |

**Justificación**: La inyección desde `run.py` es el patrón más simple y consistente con Clean Architecture. El entry point es responsable del wiring.

**Cambios**:
- `run.py`: Crea adapter y lo pasa a `CLIApp`
- `src/infrastructure/cli/app.py`: Acepta `adapter: ImageLoaderPort` en constructor

**Fecha**: 2026-03-16

### [COMPLETADO] SUPPORTED_EXTENSIONS hardcodeado - Decisión: Constructor configurable
| Opción | Pros | Contras | Decisión |
|--------|------|---------|----------|
| A. Constructor con extensión opcional | Flexible, OCP, retrocompatible | Ligeramente más complejo | ✅ ELEGIDA |
| B. Constante de clase sobrescribible | Simple | Menos flexible | ❌ |
| C. Config global | Compartido | Acoplamiento a config | ❌ |

**Justificación**: Constructor con parámetro opcional mantiene retrocompatibilidad y permite extensibilidad sin modificar la clase (Open/Closed Principle).

**Cambios**:
- Renombrado `SUPPORTED_EXTENSIONS` → `DEFAULT_EXTENSIONS`
- Agregado parámetro `supported_extensions: Optional[Set[str]] = None` al constructor
- Usa `self._extensions` en lugar de la constante de clase

**Fecha**: 2026-03-16

---

## DUDAS ALTO NIVEL Escaladas

Las siguientes decisiones fueron escaladas a `docs/decisions/preguntas-arquitectura.md`:

1. **¿Cómo reestructurar las interfaces de Image Gateway?** - Separación de `load` vs `display`
2. **¿Dónde debe vivir la lógica de validación de paths?** - Centralización de validación

Estas requieren decisión del usuario debido a su impacto cross-cutting en la arquitectura.

---

## Estadísticas del Procesamiento

| Tipo | Cantidad | Acción |
|------|----------|--------|
| CERTEZAS | 3 | Ejecutadas |
| DUDAS BAJO NIVEL | 2 | Evaluadas y ejecutadas |
| DUDAS ALTO NIVEL | 2 | Escaladas a preguntas-arquitectura.md |
| **Total** | **7** | Procesadas |
