# FastAPI Review Project (Movie API)

Proyecto con **FastAPI**, en el que exploro y aprendo sobre esta potente herramienta para construir APIs modernas y de alto rendimiento. El proyecto utiliza una arquitectura **Clean Architecture** y está completamente **asincronizado**.

## Características

- **FastAPI**: Marco web moderno y rápido para construir APIs basado en estándares abiertos (OpenAPI y JSON Schema). Actualizado a la versión **0.135.3**.
- **Python 3.12+**: Proyecto optimizado para las versiones más recientes de Python.
- **Clean Architecture**: Separación de responsabilidades en capas (API, Services, Repositories, Core, Models, Schemas).
- **Asincronía Completa**: Operaciones de base de datos y endpoints asíncronos para mayor rendimiento.
- **SQLModel**: Combinación de **SQLAlchemy** y **Pydantic** para modelos de datos elegantes y seguros.
- **JWT Authentication**: Autenticación basada en JSON Web Tokens (JWT) con **PyJWT**.
- **Base de Datos**: Soporte para **PostgreSQL**, **MariaDB** (v11.4 LTS) y **SQLite** mediante drivers asíncronos (`asyncpg`, `aiomysql`, `aiosqlite`).
- **Docker Stack**: Configuración moderna con **PostgreSQL**, **Prometheus v3**, **Grafana 13**, **Loki 3.5**, **Tempo 2.10** y **Grafana Alloy v1.15**.
- **Observabilidad Unificada (OpenTelemetry)**: Implementación de **Logs**, **Métricas** y **Trazabilidad Distribuida**. *Nota: Desactivado por defecto. Activar con `OTEL_ENABLED=True`.*
- **Pgweb**: Interfaz web integrada para la administración de bases de datos en el entorno Docker.

## Librerías utilizadas

- **FastAPI**: [FastAPI documentation](https://fastapi.tiangolo.com/)
- **SQLModel**: Para modelos de datos y ORM asíncrono.
- **Alembic**: Herramienta de migraciones para SQLAlchemy/SQLModel.
- **OpenTelemetry**: SDKs para instrumentación nativa de logs, trazas y métricas.
- **python-dotenv**: Gestión de variables de entorno.
- **Async Drivers**: `asyncpg`, `aiomysql`, `aiosqlite` para bases de datos asíncronas.
- **Monitoring**: Grafana Alloy (agente unificado), Prometheus (Remote Write), Grafana, Loki y Tempo.

## Instalación y Ejecución

## Arquitectura Docker-First

Este proyecto está diseñado bajo una filosofía **Docker-First**. Toda la infraestructura, dependencias y el entorno de ejecución están estandarizados mediante contenedores para garantizar:
- **Consistencia**: El mismo entorno en desarrollo, staging y producción.
- **Aislamiento**: Dependencias del sistema (drivers de DB, librerías OTel) encapsuladas.
- **Simplicidad**: Un solo comando para levantar todo el stack de observabilidad y persistencia.

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

### Instalación del entorno local (Solo para desarrollo de código)

1. Crea un entorno virtual:

    ```bash
    python -m venv .venv
    source .venv/bin/activate  # En Linux/macOS
    .venv\Scripts\activate     # En Windows
    ```

3. Instala las dependencias del proyecto:

    ```bash
    pip install -r requirements.txt
    ```

### Ejecución en entorno local

1. Crea un archivo `.env` en la raíz del proyecto para configurar las variables de entorno (como claves JWT, base de datos, etc.).

2. Inicia el servidor de desarrollo utilizando la CLI oficial de FastAPI:

    ```bash
    fastapi dev src/main.py --port 8000 --host 0.0.0.0
    ```

   La API estará disponible en `http://localhost:8000`.
   La documentación estará disponible en `http://localhost:8000/docs` o `http://localhost:8000/redoc`.

### Ejecución con Docker

El proyecto está completamente preparado para ser ejecutado en contenedores Docker con **PostgreSQL** como base de datos por defecto y un stack de monitoreo completo.

1. Asegúrate de tener Docker y Docker Compose instalados.
2. Modifica el archivo `.env` con las configuraciones necesarias.
3. Construye y levanta los contenedores:

    ```bash
    docker compose -f compose.yml -f docker-compose.app.yml -f docker-compose.monitoring.yml up -d --build
    ```

## Estructura del Proyecto (Clean Architecture)

    ```bash
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
 abierto a sugerencias y contribuciones.
