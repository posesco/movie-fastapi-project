# Fase 1: Inversión de Dependencias (DIP)

## Objetivo
Eliminar el uso de Singletons globales e implementar la Inyección de Dependencias en las capas de Servicio y API, utilizando el sistema nativo de FastAPI (`Depends`). Esto permitirá un acoplamiento suelto, facilitando el testing unitario y la intercambiabilidad de implementaciones.

## Archivos Clave & Contexto
*   **Servicios (`src/services/*.py`)**: Actualmente importan instancias globales de los repositorios y otros servicios.
*   **Repositorios (`src/repositories/*.py`)**: Instancian variables globales al final del archivo (ej. `user_repository = UserRepository(User)`).
*   **Dependencias (`src/api/deps.py`)**: Aquí centralizaremos la creación y provisión de servicios y repositorios.
*   **Controladores (`src/api/v1/endpoints/*.py`)**: Usan directamente los servicios globales.

## Pasos de Implementación

### 1. Refactorizar Capa de Servicios
Modificar los servicios para recibir sus dependencias a través del constructor (`__init__`).

*   **`AuditService`**: 
    *   Constructor: `def __init__(self, action_repo: ActionRepository, audit_repo: AuditRepository)`
*   **`UserService`**:
    *   Constructor: `def __init__(self, user_repo: UserRepository, audit_service: AuditService)`
*   **`MovieService`**:
    *   Constructor: `def __init__(self, movie_repo: MovieRepository, audit_service: AuditService)`
*   **`StorageService`**:
    *   El módulo `__init__.py` no debería instanciar el servicio globalmente. 

### 2. Configurar el Contenedor de Dependencias (`src/api/deps.py`)
Crear funciones proveedoras ("providers") que FastAPI usará con `Depends()`.

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
*Nota: Reevaluaremos si usar funciones que devuelven instancias o si se reutilizan los singletons instanciados, pero inyectándolos para facilitar mockeo.*

### 3. Refactorizar Controladores (Endpoints)
Actualizar las rutas en `src/api/v1/endpoints/` para inyectar los servicios en las funciones en lugar de importarlos de los módulos de servicio.

*   Rutas de **movies**: Inyectar `MovieService`.
*   Rutas de **users**: Inyectar `UserService`.
*   Rutas de **upload**: Inyectar `StorageProvider`.

### 4. Limpieza
Eliminar las instancias globales (`user_service = UserService()`, etc.) que quedaron huérfanas al final de los archivos en `src/services/`.

## Verificación & Testing
1.  Verificar que la aplicación levante sin errores de importación circular.
2.  Ejecutar la suite de tests (`pytest tests/unit/`) y asegurar que pasen. Si los tests mockeaban importaciones (`patch`), habrá que actualizarlos para que mockeen la dependencia o pasen un mock al inicializar el controlador.
3.  Comprobar funcionalidad con un flujo básico (registrar usuario, login, crear película).