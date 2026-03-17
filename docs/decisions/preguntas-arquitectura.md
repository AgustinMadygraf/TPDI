# Preguntas de Arquitectura Pendientes

> Fecha de registro: 2026-03-16  
> Origen: Escalado desde `docs/todo.md` (code-audit)

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
**Resuelta como parte de ADR-001**

Se implementará `PathValidator` en `infrastructure/shared/` como parte de la refactorización de separación de interfaces.

### ADR resultante
`docs/decisions/ADR-001-separar-interfaces-image-gateway.md`

---

## [2026-03-16] ¿Cómo reestructurar las interfaces de Image Gateway?

### Contexto
El `ImageGateway` actual tiene responsabilidades mezcladas: implementa `load` (definido en `ImageLoaderPort`) y `display` (no definido en ningún protocolo). Además, `CV2ImageAdapter` también implementa ambas operaciones.

### Pregunta
¿Cómo deberíamos separar las responsabilidades de carga vs visualización?

### Decisión
**Resuelta en ADR-001**

Separar en dos Protocols distintos (`ImageLoaderPort` y `ImageDisplayPort`) con implementaciones separadas (`CV2ImageLoader` y `CV2ImageDisplayer`).

### ADR resultante
`docs/decisions/ADR-001-separar-interfaces-image-gateway.md`
