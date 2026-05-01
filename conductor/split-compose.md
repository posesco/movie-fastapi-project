# Plan: Split Compose File

## Objective
Split the monolithic `compose.yml` file into smaller logical files (`docker-compose.app.yml` and `docker-compose.monitoring.yml`) using the `include` directive.

## Key Files & Context
- `compose.yml`: To be split.
- `docker-compose.app.yml` (New): `app`, `postgres`, `pgweb` services.
- `docker-compose.monitoring.yml` (New): Observability services.

## Implementation Steps
1. Move the main services and volumes to `docker-compose.app.yml`.
2. Move monitoring to `docker-compose.monitoring.yml`.
3. Modify `compose.yml` to include the new files.

## Verification
- Validate configuration with `docker compose config`.
- Optionally test startup with `docker compose up -d`.
