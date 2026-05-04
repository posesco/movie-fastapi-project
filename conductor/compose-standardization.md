# Status: Standardized and Isolated Compose Stack (Implemented)

## Objective
The Docker Compose stack is standardized to ensure consistency across services, property ordering, and network isolation. All services are connected through a dedicated bridge network (`fastapi_net`).

## Key Files & Context
- `compose.yml`: Main entry point with `fastapi_net` network declaration and service inclusion.
- `docker-compose.app.yml`: Application core services (App replicas, Postgres, Redis, Dbgate).
- `docker-compose.monitoring.yml`: Full observability stack (Prometheus, Grafana, Loki, Tempo, Alloy, Alertmanager, Exporters).

## Standardized Structure (Strict Property Order)
Each service follows this mandatory property sequence:
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

## Current Service Inventory
- **Core:** `app` (4 replicas), `postgres`, `redis`, `dbgate`.
- **Ingress:** `nginx` (Load Balancer).
- **Monitoring:** `prometheus`, `grafana`, `loki`, `tempo`, `alloy`, `alertmanager`, `vulture`.
- **Exporters:** `nginx_exporter`, `redis_exporter`.

## Verification
- Syntax validated via `docker compose config`.
- Network isolation verified: All inter-service communication occurs within `fastapi_net`.
- Load balancing confirmed via `X-Backend-Server` response headers.
