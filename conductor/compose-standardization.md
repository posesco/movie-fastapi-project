# Plan: Standardize and Isolate Compose Files

## Objective
Dar consistencia a los archivos Docker Compose (`docker-compose.app.yml` y `docker-compose.monitoring.yml`) unificando el orden de las propiedades de cada servicio y agregando una red aislada para el proyecto.

## Key Files & Context
- `compose.yml`: Se le añadirá la declaración de la red aislada (`fastapi_net`).
- `docker-compose.app.yml`: Se reordenarán las propiedades y se conectarán a `fastapi_net`.
- `docker-compose.monitoring.yml`: Se reordenarán las propiedades y se conectarán a `fastapi_net`.

## Proposed Structure (Standard Order)
Para cada servicio, se seguirá estrictamente el siguiente orden de propiedades:
1. `container_name`
2. `image` / `build`
3. `command`
4. `restart`
5. `ports`
6. `environment`
7. `env_file`
8. `volumes`
9. `depends_on`
10. `healthcheck`
11. `networks`

## Implementation Steps
1. **Definir la Red:**
   Añadir la red personalizada en `compose.yml`:
   ```yaml
   include:
     - docker-compose.app.yml
     - docker-compose.monitoring.yml

   networks:
     fastapi_net:
       driver: bridge
   ```
2. **Refactorizar `docker-compose.app.yml`:**
   Aplicar el orden estándar a los servicios `app`, `postgres`, `pgweb` y añadir `networks: [fastapi_net]` a todos. Declarar la red al final.
3. **Refactorizar `docker-compose.monitoring.yml`:**
   Aplicar el orden estándar a `prometheus`, `grafana`, `loki`, `tempo`, `alloy`, `vulture` y añadir `networks: [fastapi_net]`. Declarar la red al final.

## Verification
- Ejecutar `docker compose config` para validar que la sintaxis es correcta y que todos los servicios están en la red `fastapi_net`.