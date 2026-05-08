# Fase 3: Segregación de Interfaces (ISP)

## Objetivo
Dividir `BaseRepository` en Mixins granulares. Evitar exponer métodos innecesarios en repositorios especializados.

## Archivos Afectados
*   **Modificado:** `src/repositories/base.py`, `src/repositories/user.py`, `src/repositories/movie.py`, `src/repositories/audit.py`, `src/repositories/action.py`

## Pasos de Implementación

### 1. Refactorizar `src/repositories/base.py`
*   Crear `ReadRepositoryMixin`, `CreateRepositoryMixin`, `UpdateRepositoryMixin`, `DeleteRepositoryMixin`.
*   `BaseRepository` hereda de todos (Full CRUD).

### 2. Actualizar Repositorios Específicos
*   `UserRepository`, `MovieRepository`: mantienen `BaseRepository`.
*   `AuditRepository`: hereda de `Read` + `Create`. Sin `update`/`delete`.
*   `ActionRepository`: hereda de `Read`. Solo lectura.

## Verificación & Testing
1.  Tests `pytest tests/unit/` pasaron 100%.
2.  Contratos de interfaz ahora restringen operaciones inválidas por diseño.
