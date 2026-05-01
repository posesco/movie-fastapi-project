# Plan: Split Compose File

## Objective
Dividir el archivo monolítico `compose.yml` en archivos lógicos más pequeños (`docker-compose.app.yml` y `docker-compose.monitoring.yml`) mediante la directiva `include`.

## Key Files & Context
- `compose.yml`: Se dividirá.
- `docker-compose.app.yml` (Nuevo): Servicios `app`, `postgres`, `pgweb`.
- `docker-compose.monitoring.yml` (Nuevo): Servicios de observabilidad.

## Implementation Steps
1. Mover los servicios y volúmenes principales a `docker-compose.app.yml`.
2. Mover la monitorización a `docker-compose.monitoring.yml`.
3. Modificar `compose.yml` para incluir los nuevos archivos.

## Verification
- Validar configuración con `docker compose config`.
- Opcionalmente probar el arranque con `docker compose up -d`.