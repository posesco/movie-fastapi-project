# Fase 3: Segregación de Interfaces (ISP)

## Objetivo
Dividir `BaseRepository` Mixins granulares. Repositorios solo implementan interfaces necesarias. Evitar métodos innecesarios (ej: borrar auditoría).

## Archivos Afectados
*   `src/repositories/base.py`, `src/repositories/user.py`, `src/repositories/movie.py`, `src/repositories/audit.py`, `src/repositories/action.py`

## Pasos de Implementación
1.  Refactor `base.py`: Mixins `Read`, `Create`, `Update`, `Delete`. `BaseRepository` hereda todos.
2.  Update `audit.py`: `Read` + `Create`. No `update`/`delete`.
3.  Update `action.py`: `Read` solo. Master table.

## Verificación
Tests `pytest` 100%. Interfaces restringen ops inválidas.
