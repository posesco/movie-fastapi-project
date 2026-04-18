# Project Overview

This is a **FastAPI** starter project designed for building high-performance, modern REST APIs using **Clean Architecture** and **Asynchronous** patterns.

**Key Technologies:**
- **Framework:** FastAPI (0.135.3)
- **Language:** Python 3.12 (Standardized via Dockerfile)
- **Data Validation & ORM:** SQLModel (SQLAlchemy + Pydantic)
- **Database:** Support for MariaDB (v11.4 LTS), PostgreSQL, and SQLite via async drivers.
- **Authentication:** JSON Web Tokens (JWT) using PyJWT.
- **Containerization:** Docker and Docker Compose (Rootless setups enabled in Dockerfile).
- **Full Observability (OTel):** Unified implementation of **Logs**, **Metrics**, and **Tracing** using **OpenTelemetry SDK**.
- **Monitoring Stack:** Prometheus v3, Grafana 13, Loki 3.5, Tempo 2.10, and **Grafana Alloy v1.15** as the OTLP collector.
- **Tools:** pgweb for database administration.

## Building and Running

### Local Development
1. **Environment Setup:**
   Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```
2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the Server:**
   ```bash
   fastapi dev src/main.py --port 8000 --host 0.0.0.0
   ```

### Docker
```bash
docker compose up -d --build
```

## Development Conventions

- **Architecture:** Clean Architecture with separate layers:
  - `src/api/`: Controllers and endpoint definitions (versioned).
  - `src/core/`: Global settings, database engine, and security.
  - `src/models/`: Database entities using SQLModel.
  - `src/repositories/`: Data access logic (Repository pattern).
  - `src/schemas/`: Pydantic models for request/response validation.
  - `src/services/`: Core business logic and service orchestration.
  - `src/middlewares/`: Global exception handling and logging.

- **Observability:** 
  - All telemetry is exported via **OTLP (gRPC)** to Alloy.
  - Metrics: Custom metrics defined in `src/services/metrics.py` (OTel Meter).
  - Logs: Standard Python logging redirected to OTel LoggingHandler.
  - Traces: Automatic FastAPI instrumentation via `FastAPIInstrumentor`.

- **Quality:** `ruff` for linting and formatting. Async execution for all I/O operations.
- **Testing:** `pytest` with `pytest-asyncio`. Coverage for both unit and integration tests.

## Git & Release Management

Este proyecto sigue estrictamente la estrategia de desarrollo **GitFlow** y el versionado semántico **SemVer**.

- **Workflow:** Consultar siempre `conductor/workflow.md` para la gestión de ramas (`feat/*`, `release/*`, `hotfix/*`).
- **Ramas Principales:** `master` para producción y `develop` para integración.
- **Versionado:** Las versiones se etiquetan en `master` siguiendo el formato `vMAJOR.MINOR.PATCH`.
- **Commits:** Obligatorio el uso de *Conventional Commits* (`feat:`, `fix:`, `docs:`, etc.).
