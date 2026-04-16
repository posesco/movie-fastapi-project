# FastAPI Starter Project (Movie API)

Este es mi proyecto inicial con **FastAPI**, en el que exploro y aprendo sobre esta potente herramienta para construir APIs modernas y de alto rendimiento. El proyecto utiliza una arquitectura **Clean Architecture** y está completamente **asincronizado**.

## Características

- **FastAPI**: Marco web moderno y rápido para construir APIs basado en estándares abiertos (OpenAPI y JSON Schema). Actualizado a la versión **0.135.3**.
- **Python 3.12+**: Proyecto optimizado para las versiones más recientes de Python.
- **Clean Architecture**: Separación de responsabilidades en capas (API, Services, Repositories, Core, Models, Schemas).
- **Asincronía Completa**: Operaciones de base de datos y endpoints asíncronos para mayor rendimiento.
- **SQLModel**: Combinación de **SQLAlchemy** y **Pydantic** para modelos de datos elegantes y seguros.
- **JWT Authentication**: Autenticación basada en JSON Web Tokens (JWT) con **PyJWT**.
- **Base de Datos**: Soporte para **PostgreSQL**, **MariaDB** (v11.4 LTS) y **SQLite** mediante drivers asíncronos (`asyncpg`, `aiomysql`, `aiosqlite`).
- **Docker Stack**: Configuración con **MariaDB**, **Prometheus v3**, **Grafana 13** y **Loki 3.5**.
- **Pgweb**: Interfaz web integrada para la administración de bases de datos en el entorno Docker.

## Librerías utilizadas

- **FastAPI**: [FastAPI documentation](https://fastapi.tiangolo.com/)
- **SQLModel**: Para modelos de datos y ORM asíncrono.
- **PyJWT**: Manejo de autenticación basada en tokens JWT.
- **python-dotenv**: Gestión de variables de entorno.
- **Async Drivers**: `asyncpg`, `aiomysql`, `aiosqlite` para bases de datos asíncronas.
- **Monitoring**: Prometheus, Grafana, Loki y cAdvisor.

## Instalación y Ejecución

### Requisitos previos

Asegúrate de tener instalado:

- **Python 3.12+**
- **pip** para la gestión de paquetes de Python
- **Docker** y **Docker Compose** para la ejecución del stack completo

### Instalación del entorno local

1. Clona el repositorio:

    ```bash
    git clone https://github.com/posesco/fastapi-project.git
    cd fastapi-project
    ```

2. Crea un entorno virtual (opcional pero recomendado):

    ```bash
    python -m venv venv
    source venv/bin/activate  # En Linux/macOS
    venv\Scripts\activate     # En Windows
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

   La API estará disponible en `http://127.0.0.1:8000`.
   La documentación estará disponible en `http://127.0.0.1:8000/docs` o `http://127.0.0.1:8000/redoc`.

### Ejecución con Docker

El proyecto está completamente preparado para ser ejecutado en contenedores Docker con **MariaDB** como base de datos y un stack de monitoreo completo.

1. Asegúrate de tener Docker y Docker Compose instalados.
2. Modifica el archivo `.env` con las configuraciones necesarias.
3. Construye y levanta los contenedores:

    ```bash
    docker compose up -d --build
    ```

## Estructura del Proyecto (Clean Architecture)

    ```bash
    src/
    ├── api/             # Capa de entrada (Controladores/Endpoints)
    │   ├── deps.py      # Dependencias compartidas (Auth, DB)
    │   └── v1/          # Versionado de API
    │       └── endpoints/
    ├── core/            # Configuración global y seguridad
    ├── models/          # Entidades de Base de Datos (SQLModel)
    ├── repositories/    # Capa de Acceso a Datos (Patrón Repository)
    ├── schemas/         # Modelos Pydantic para validación y DTOs
    ├── services/        # Lógica de Negocio y Orquestación
    ├── middlewares/     # Middlewares de FastAPI (Error handler)
    └── main.py          # Punto de entrada de la aplicación
    ```

## Licencia

Este proyecto está licenciado bajo los términos de la [GNU General Public License v3.0](./LICENSE).

---

¡Gracias por revisar mi proyecto! Estoy aprendiendo y abierto a sugerencias y contribuciones.
