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
  - `src/core/`: Global settings, database engine, security, and **observability setup**.
  - `src/models/`: Database entities using SQLModel.
  - `src/repositories/`: Data access logic (Repository pattern).
  - `src/schemas/`: Pydantic models for request/response validation.
  - `src/services/`: Core business logic and service orchestration.
  - `src/middlewares/`: **Idiomatic exception handlers** (replacing legacy BaseHTTPMiddleware).

- **Observability:** 
  - Centralized setup in `src/core/observability.py`.
  - All telemetry is exported via **OTLP (gRPC)** to Alloy.
  - Metrics: Custom metrics defined in `src/services/metrics.py` (OTel Meter).
  - Logs: Standard Python logging redirected to OTel LoggingHandler.
  - Traces: Automatic FastAPI instrumentation via `FastAPIInstrumentor`.

- **Database & Migrations:**
  - **Alembic** is used for schema versioning (async support).
  - Schema creation is decoupled from API startup.
  - Migrations live in `migrations/`.

- **Quality & Security:** 
  - `ruff` for linting and formatting. 
  - **Bandit** and **Safety** integrated into CI for security auditing.
  - `pytest` with `pytest-asyncio` and **coverage reporting**.

## Git & Release Management

This project strictly follows the **GitFlow** development strategy and **SemVer** semantic versioning.

- **Workflow:** Always refer to `conductor/workflow.md` for branch management (`feat/*`, `release/*`, `hotfix/*`).
- **Main Branches:** `master` for production and `develop` for integration.
- **Versioning:** Versions are tagged on `master` following the `vMAJOR.MINOR.PATCH` format.
- **Commits:** The use of *Conventional Commits* (`feat:`, `fix:`, `docs:`, etc.) is mandatory.
