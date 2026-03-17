# Preguntas de Arquitectura Pendientes

> Archivo de inbox para decisiones arquitectónicas pendientes.
> El historial de decisiones resueltas vive en `docs/decisions/ADR-*.md`.

---

## 2026-03-17 - Preparación para CMYK futuro

### Pregunta

Cuando se habilite `CMYK`, ¿el modelo de color debe seguir siendo una política externa de análisis/configuración o debe promoverse a un concepto explícito del dominio, por ejemplo dentro de la entidad `Image` o en una abstracción de color dedicada?

### Contexto

- Para el alcance actual (`RGB` y `CMY`) alcanza con mantener la imagen cargada en RGB canónico y decidir el modo de análisis desde configuración.
- Para `CMYK`, esa estrategia puede empezar a quedarse corta porque ya no alcanza con distinguir solo por cantidad de canales ni con asumir una única representación canónica trivial para todo el flujo.

### Estado

- Pendiente
- No bloquea la implementación actual de `RGB`/`CMY`

---

## Últimas Decisiones Resueltas

- **2026-03-16**: ADR-001 - Separar Interfaces de Image Gateway
  - Ver: `docs/decisions/ADR-001-separar-interfaces-image-gateway.md`
  - Estado: ✅ Implementado
