# Fase 2: Principio de Responsabilidad Única (SRP)

## Objetivo
Desacoplar autenticación (tokens + credenciales) de `UserService`. Extraer responsabilidades identidad a `AuthService`.

## Archivos Afectados
*   **Nuevo:** `src/services/auth.py`
*   **Modificado:** `src/services/user.py`, `src/api/deps.py`, `src/api/v1/endpoints/user.py`

## Pasos de Implementación

### 1. Crear `AuthService` (`src/services/auth.py`)
*   Inyectar `UserRepository`.
*   Mover `get_tokens()` y `authenticate()` de `UserService`.
*   Mover imports `pwd_context`, `create_token`, `create_refresh_token`.

### 2. Actualizar `UserService` (`src/services/user.py`)
*   Eliminar `get_tokens()`, `authenticate()`.
*   Eliminar imports `src.core.security` innecesarios.
*   Mantener `pwd_context` para CRUD si necesario.

### 3. Actualizar Dependencias (`src/api/deps.py`)
*   Provider: `def get_auth_service(user_repo: UserRepository = Depends(get_user_repository)) -> AuthService`
*   Tipo: `AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]`

### 4. Refactorizar Controladores (`src/api/v1/endpoints/user.py`)
*   Endpoints `/login`, `/refresh`: inyectar `AuthServiceDep`.
*   Usar `auth_service.authenticate()`, `auth_service.get_tokens()`.

## Verificación & Testing
1.  Asegurar no errores tipo/referencias.
2.  Ejecutar `pytest tests/unit/`. Validar login (`test_user_me.py`, `test_movie.py`) + registro.
