# Fase 4: Principios OCP y LSP (Almacenamiento)

## Objetivo
Cumplir OCP/LSP implementando `LocalStorageProvider`. Extender almacenamiento sin modificar `/upload` (OCP). Nueva impl sustituye a S3 (LSP).

## Archivos Afectados
*   `src/core/config.py`, `src/services/storage/local.py`, `src/api/deps.py`, `src/main.py`

## Pasos de Implementación
1.  Config: añadir `storage_backend` (s3/local).
2.  `LocalStorageProvider`: hereda `StorageProvider`. Guarda en disco.
3.  `deps.py`: inyectar S3 o Local según config.
4.  `main.py`: montar `/static` si backend local.

## Verificación
Subida local retorna URL `/static/...`. Archivo accesible. Tests pasan.
