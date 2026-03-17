# Preguntas de Arquitectura Pendientes

> Fecha de registro: 2026-03-16  
> Origen: Escalado desde `docs/todo.md` (code-audit)

---

## [2026-03-16] ¿Cómo reestructurar las interfaces de Image Gateway?

### Contexto
El `ImageGateway` actual tiene responsabilidades mezcladas: implementa `load` (definido en `ImageLoaderPort`) y `display` (no definido en ningún protocolo). Además, `CV2ImageAdapter` también implementa ambas operaciones.

### Pregunta
¿Cómo deberíamos separar las responsabilidades de carga vs visualización?

### Opciones consideradas

**Opción A: Separar en dos Protocols distintos**
- `ImageLoaderPort` (existente) → solo `load()`
- `ImageDisplayPort` (nuevo) → `display()`
- `CV2ImageLoader` y `CV2ImageDisplayer` como implementaciones separadas
- Pros: SRP claro, testeable, puede reusar display con otro loader
- Contras: Más clases, más wiring

**Opción B: Un solo Adapter con ambas capacidades, pero gateway separados**
- Mantener `CV2ImageAdapter` con ambos métodos
- Crear `ImageDisplayGateway` separado del `ImageGateway`
- Pros: Menos cambio en adapter existente
- Contras: El adapter sigue teniendo múltiples responsabilidades

**Opción C: Mover display a capa de presentación/UI**
- Eliminar `display()` de infrastructure
- La UI/CLI usa OpenCV directamente para visualización
- Pros: Simplifica capa de infrastructure
- Contras: Acopla UI a OpenCV

### Decisión
Pendiente - requiere análisis de trade-offs

### ADR resultante
Pendiente

---

## [2026-03-16] ¿Dónde debe vivir la lógica de validación de paths?

### Contexto
Actualmente la validación de path traversal está tanto en `CV2ImageAdapter` como en `ImageGateway`. Hay duplicación potencial.

### Pregunta
¿Debería la validación de paths estar centralizada? ¿En qué capa?

### Opciones consideradas
- **Opción A**: Validar solo en Gateway (interface_adapters) - una sola vez
- **Opción B**: Validar en cada Adapter (defensa en profundidad)
- **Opción C**: Extraer a un `PathValidator` reusable

### Decisión
Pendiente

### ADR resultante
Pendiente
