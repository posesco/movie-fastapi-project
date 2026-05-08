# Fase 1: Inversión de Dependencias (DIP)

## Objetivo
Eliminar Singletons globales. Implementar Inyección de Dependencias en Servicio + API usando FastAPI `Depends`. Permitir acoplamiento suelto, facilitar unit tests + intercambio impls.

## Archivos Clave & Contexto
*   **Servicios (`src/services/*.py`)**: Importan instancias globales repos/servicios.
*   **Repositorios (`src/repositories/*.py`)**: Instancian variables globales fin archivo (ej. `user_repository = UserRepository(User)`).
*   **Dependencias (`src/api/deps.py`)**: Centralizar creación/provisión servicios + repositorios.
*   **Controladores (`src/api/v1/endpoints/*.py`)**: Usan servicios globales.

## Pasos de Implementación

### 1. Refactorizar Capa de Servicios
Modificar servicios para recibir dependencias vía constructor (`__init__`).

*   **`AuditService`**: 
    *   Constructor: `def __init__(self, action_repo: ActionRepository, audit_repo: AuditRepository)`
*   **`UserService`**:
    *   Constructor: `def __init__(self, user_repo: UserRepository, audit_service: AuditService)`
*   **`MovieService`**:
    *   Constructor: `def __init__(self, movie_repo: MovieRepository, audit_service: AuditService)`
*   **`StorageService`**:
    *   `src/services/storage/__init__.py` no instanciar servicio globalmente. 

### 2. Configurar Contenedor Dependencias (`src/api/deps.py`)
Crear funciones proveedoras ("providers") para FastAPI `Depends()`.

```python
# Ejemplo de provider
def get_user_repository() -> UserRepository:
    return UserRepository(User)

def get_audit_service(
    action_repo: ActionRepository = Depends(get_action_repository),
    # ...
) -> AuditService:
    return AuditService(action_repo, ...)
```
*Nota: Reevaluar usar fns que devuelven instancias o reutilizar singletons inyectados para facilitar mockeo.*

### 3. Refactorizar Controladores (Endpoints)
Actualizar rutas `src/api/v1/endpoints/`. Inyectar servicios en fns. No importar de módulos servicio.

*   Rutas de **movies**: Inyectar `MovieService`.
*   Rutas de **users**: Inyectar `UserService`.
*   Rutas de **upload**: Inyectar `StorageProvider`.

### 4. Limpieza
Eliminar instancias globales (`user_service = UserService()`, etc.) huérfanas fin archivos `src/services/`.

## Verificación & Testing
1.  Verificar app levante sin errores importación circular.
2.  Ejecutar `pytest tests/unit/`. Asegurar pasen. Actualizar mocks si usaban `patch`.
3.  Comprobar funcionalidad flujo básico (registro, login, crear película).
