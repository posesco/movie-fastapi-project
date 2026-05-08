# Fase 2: Principio de Responsabilidad Única (SRP)

## Objetivo
Desacoplar la lógica de autenticación (generación de tokens y validación de credenciales) del `UserService`. Actualmente, este servicio hace demasiado (CRUD de usuarios, roles, auditoría y autenticación). Extraeremos las responsabilidades de identidad a un nuevo `AuthService`.

## Archivos Afectados
*   **Nuevo:** `src/services/auth.py`
*   **Modificado:** `src/services/user.py`
*   **Modificado:** `src/api/deps.py`
*   **Modificado:** `src/api/v1/endpoints/user.py`

## Pasos de Implementación

### 1. Crear `AuthService` (`src/services/auth.py`)
*   Recibirá inyectado `UserRepository` (para buscar el usuario a autenticar).
*   Se moverán los métodos `get_tokens(self, user_data: dict) -> dict` y `authenticate(self, db, username, password) -> Optional[User]` desde `UserService`.
*   Las importaciones de `pwd_context`, `create_token` y `create_refresh_token` se moverán aquí.

### 2. Actualizar `UserService` (`src/services/user.py`)
*   Eliminar los métodos `get_tokens` y `authenticate`.
*   Eliminar las importaciones innecesarias de `src.core.security`.
*   Nota: `create_user` y `update_user` seguirán usando `pwd_context` para hashear la contraseña. Quizás `AuthService` también exponga un método para hashear contraseñas, o es válido que `UserService` dependa directamente de `src.core.security.pwd_context` para crear la entidad. Lo mantendremos dependiendo de `pwd_context` por simplicidad, o usaremos `AuthService` si tiene sentido.

### 3. Actualizar Dependencias (`src/api/deps.py`)
*   Añadir un proveedor: `def get_auth_service(user_repo: UserRepository = Depends(get_user_repository)) -> AuthService`
*   Añadir tipo inyectable: `AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]`

### 4. Refactorizar Controladores (`src/api/v1/endpoints/user.py`)
*   En los endpoints `/login` y `/refresh`, inyectar `AuthServiceDep` en lugar de / además de `UserServiceDep`.
*   Utilizar `auth_service.authenticate()` y `auth_service.get_tokens()`.

## Verificación & Testing
1.  Asegurar que no hay errores de tipo o referencias perdidas.
2.  Ejecutar la suite de tests (`pytest tests/unit/`). Los tests de login (`test_user_me.py`, `test_movie.py`) y creación de usuarios validarán que nada se haya roto en el flujo de identidad.