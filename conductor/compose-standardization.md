# Plan: Standardize and Isolate Compose Files

## Objective
Provide consistency to the Docker Compose files (`docker-compose.app.yml` and `docker-compose.monitoring.yml`) by unifying the order of properties for each service and adding an isolated network for the project.

## Key Files & Context
- `compose.yml`: The isolated network declaration (`fastapi_net`) will be added.
- `docker-compose.app.yml`: Properties will be reordered and connected to `fastapi_net`.
- `docker-compose.monitoring.yml`: Properties will be reordered and connected to `fastapi_net`.

## Proposed Structure (Standard Order)
For each service, the following property order will be strictly followed:
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
1. **Define the Network:**
   Add the custom network in `compose.yml`:
   ```yaml
   include:
     - docker-compose.app.yml
     - docker-compose.monitoring.yml

   networks:
     fastapi_net:
       driver: bridge
   ```
2. **Refactor `docker-compose.app.yml`:**
   Apply the standard order to the `app`, `postgres`, and `pgweb` services and add `networks: [fastapi_net]` to all. Declare the network at the end.
3. **Refactor `docker-compose.monitoring.yml`:**
   Apply the standard order to `prometheus`, `grafana`, `loki`, `tempo`, `alloy`, and `vulture` and add `networks: [fastapi_net]`. Declare the network at the end.

## Verification
- Run `docker compose config` to validate that the syntax is correct and that all services are on the `fastapi_net` network.
