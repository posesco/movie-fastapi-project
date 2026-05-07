# FastAPI Project (Movie API)

Proyecto exploratorio con **FastAPI** para construir APIs modernas y de alto rendimiento. El proyecto utiliza una arquitectura **Clean Architecture** y está completamente **asincronizado**.

## Características

- **FastAPI**: Marco web moderno y rápido para construir APIs basado en estándares abiertos (OpenAPI y JSON Schema). Actualizado a la versión **0.135.3**.
- **Python 3.12+**: Proyecto optimizado para las versiones más recientes de Python.
- **Clean Architecture**: Separación de responsabilidades en capas (API, Services, Repositories, Core, Models, Schemas).
- **Asincronía Completa**: Operaciones de base de datos y endpoints asíncronos para mayor rendimiento.
- **SQLModel**: Combinación de **SQLAlchemy** y **Pydantic** para modelos de datos elegantes y seguros.
- **Auth (OAuth2 + JWT)**: Implementación de **OAuth2 (Password Flow)** con tokens **JWT** (PyJWT) para una autenticación segura y estándar.
- **Escalado Horizontal y Sesiones**: Balanceo de carga mediante **Nginx** (Round Robin) y gestión de estado (Blacklisting de tokens, Rate Limiting y Refresh Tokens) mediante **Redis**.
- **Base de Datos**: Soporte para **PostgreSQL**, **MariaDB** (v11.4 LTS) y **SQLite** mediante drivers asíncronos.
- **Docker Stack**: Configuración moderna con **PostgreSQL**, **Prometheus v3.11**, **Grafana 13.0**, **Loki 3.6**, **Tempo 2.10** y **Grafana Alloy v1.16**.
- **Observabilidad Unificada (OpenTelemetry)**: Implementación de **Logs**, **Métricas** y **Trazabilidad Distribuida**. *Nota: Desactivado por defecto. Activar con `OTEL_ENABLED=True`.*
- **Almacenamiento de Objetos**: **MinIO** como almacenamiento S3-compatible para archivos y assets.
- **Análisis Estático**: **SonarQube Community** con quality gates, historial de issues y cobertura integrada. Complementado con **Ruff**, **Bandit** y **Safety** en CI.
- **Dbgate**: Interfaz web moderna integrada para la administración de bases de datos.

## Librerías utilizadas

- **FastAPI**: [FastAPI documentation](https://fastapi.tiangolo.com/)
- **SQLModel**: Para modelos de datos y ORM asíncrono.
- **Alembic**: Herramienta de migraciones para SQLAlchemy/SQLModel.
- **OpenTelemetry**: SDKs para instrumentación nativa de logs, trazas y métricas.
- **Redis**: Integración para cache, rate limiting y seguridad.
- **Monitoring**: Grafana Alloy (agente unificado), Prometheus, Grafana, Loki y Tempo.
- **MinIO**: Almacenamiento de objetos compatible con S3.

## Arquitectura Docker-First y Alta Disponibilidad

Este proyecto está diseñado bajo una filosofía **Docker-First**. Toda la infraestructura está estandarizada mediante contenedores, configurando la aplicación con **4 réplicas** balanceadas por Nginx para garantizar:
- **Alta Disponibilidad**: Resiliencia ante fallos de instancias individuales.
- **Consistencia**: El mismo entorno en desarrollo, staging y producción.
- **Aislamiento**: Dependencias del sistema (drivers de DB, librerías OTel) encapsuladas.

Se recomienda **no ejecutar la aplicación directamente en el host** para evitar conflictos de versiones y asegurar que las integraciones de red (como el exportador de OTel a Alloy) funcionen correctamente.

### Requisitos previos

Asegúrate de tener instalado:

- **Docker** y **Docker Compose** (Indispensable).
- **Python 3.12+** (Opcional, solo para soporte de IDE local).

### Guía de Inicio Rápido (Docker)

1. Clona el repositorio:

    ```bash
    git clone https://github.com/posesco/fastapi-project.git
    cd fastapi-project
    ```

2. Configura tu entorno:

    ```bash
    cp .env.example .env
    ```

3. Levanta el stack completo:

    ```bash
    docker compose up -d --build
    ```

   La API estará disponible en `http://localhost`.
   La documentación estará disponible en `http://localhost/docs` o `http://localhost/redoc`.


> El archivo `compose.yml` actúa como punto de entrada unificado e incluye automáticamente `compose.app.yml` y `compose.required.yml`. Para activar el stack de monitoreo y las herramientas opcionales, descomenta la línea correspondiente en `compose.yml`.

## Estructura del Proyecto (Clean Architecture)

```
src/
├── api/             # Capa de entrada (Controladores/Endpoints)
│   ├── deps.py      # Dependencias compartidas (Auth, DB)
│   └── v1/          # Versionado de API
├── core/            # Configuración global y seguridad (Settings, DB Engine)
├── models/          # Entidades de Base de Datos (SQLModel)
├── repositories/    # Capa de Acceso a Datos (Patrón Repository)
├── schemas/         # Modelos Pydantic para validación y DTOs
├── services/        # Lógica de Negocio, Orquestación y Métricas Custom
├── middlewares/     # Middlewares de FastAPI (Error handler)
└── main.py          # Punto de entrada de la aplicación e init de OTel
```

## Licencia

Este proyecto está licenciado bajo los términos de la [GNU General Public License v3.0](./LICENSE).

---

¡Gracias por revisar mi proyecto! Estoy aprendiendo y abierto a sugerencias y contribuciones.
