# Fase 4: Principios OCP y LSP (Almacenamiento)

## Objetivo
Demostrar el cumplimiento de los principios Open/Closed (OCP) y Liskov Substitution (LSP) implementando un nuevo proveedor de almacenamiento local (`LocalStorageProvider`). Esto permitirá al sistema extender sus capacidades de almacenamiento sin modificar el código del controlador (`/upload`) ni las reglas de negocio (OCP), y asegurar que la nueva implementación pueda sustituir a la existente (`S3StorageProvider`) sin romper el comportamiento esperado (LSP).

## Archivos Afectados
*   **Modificado:** `src/core/config.py` (Añadir `storage_backend` para elegir S3 o Local).
*   **Nuevo:** `src/services/storage/local.py` (Implementar `LocalStorageProvider`).
*   **Modificado:** `src/services/storage/__init__.py` (Actualizar exportaciones).
*   **Modificado:** `src/api/deps.py` (Lógica para inyectar S3 o Local en base a la configuración).
*   **Modificado:** `src/main.py` (Montar un directorio estático para servir archivos locales si se usa el backend local).

## Pasos de Implementación

### 1. Actualizar Configuración (`src/core/config.py`)
Añadir una nueva variable de entorno:
*   `storage_backend: str = Field(default="local", validation_alias="STORAGE_BACKEND")`

### 2. Implementar `LocalStorageProvider` (`src/services/storage/local.py`)
Crear una clase que herede de `StorageProvider`:
*   `__init__`: Crear la carpeta base `uploads` si no existe.
*   `upload_file`: Guardar los bytes en disco y retornar la URL (ej. `/static/{key}`).
*   `delete_file`: Borrar el archivo del disco usando `os.remove` o `Path.unlink`.

### 3. Ajustar Proveedor de Dependencias (`src/api/deps.py`)
En `get_storage_provider()`, utilizar el patrón Factory:
```python
def get_storage_provider() -> StorageProvider:
    if settings.storage_backend == "s3":
        from src.services.storage.s3 import S3StorageProvider
        return S3StorageProvider()
    else:
        from src.services.storage.local import LocalStorageProvider
        return LocalStorageProvider()
```

### 4. Servir Archivos Locales (`src/main.py`)
Si el backend es `local`, montar un directorio de archivos estáticos en FastAPI para que las URLs retornadas funcionen y las imágenes se puedan visualizar.
```python
from fastapi.staticfiles import StaticFiles
# En la inicialización:
app.mount("/static", StaticFiles(directory="uploads"), name="static")
```

## Verificación & Testing
1.  Comprobar que los tests existentes no se rompen. (Es posible que sea necesario crear la carpeta `uploads` para pruebas, o inyectar un mock si los tests de uploads lo requieren).
2.  Probar subiendo un archivo con `STORAGE_BACKEND=local` y verificar que el archivo aparece en disco y es accesible vía URL.