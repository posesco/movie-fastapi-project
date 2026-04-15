# FastAPI Starter Project (Movie API)

Este es mi proyecto inicial con **FastAPI**, en el que exploro y aprendo sobre esta potente herramienta para construir APIs modernas y de alto rendimiento. El objetivo de este proyecto es ir implementando características paso a paso, comenzando con una API básica y avanzando a una arquitectura más robusta con MariaDB y contenedores.

## Características

- **FastAPI**: Marco web moderno y rápido para construir APIs basado en estándares abiertos (OpenAPI y JSON Schema). Actualizado a la versión **0.135.3**.
- **Python 3.12+**: Proyecto actualizado para utilizar las versiones más recientes y optimizadas de Python.
- **Pydantic**: Para validación de datos a través de modelos eficientes.
- **SQLAlchemy**: ORM utilizado para interactuar con la base de datos.
- **JWT Authentication**: Implementación de autenticación basada en JSON Web Tokens (JWT) con **PyJWT**.
- **Base de Datos**: Utiliza SQLite para el desarrollo inicial rápido, y una integración completa con **MariaDB (v11.4 LTS)** en el entorno de contenedores Docker.
- **Docker y Docker Compose**: Configuración lista para la implementación en entornos de contenedores, con buenas prácticas de seguridad (usuario no root) y monitoreo.

## Librerías utilizadas

- **FastAPI**: [FastAPI documentation](https://fastapi.tiangolo.com/)
- **FastAPI CLI**: Herramienta de línea de comandos oficial para ejecutar la aplicación.
- **Pydantic**: Para la validación de modelos de datos.
- **PyJWT**: Manejo de autenticación basada en tokens JWT.
- **python-dotenv**: Para gestionar variables de entorno.
- **SQLAlchemy**: ORM para la interacción con la base de datos.

## Instalación y Ejecución

### Requisitos previos

Asegúrate de tener instalado:

- **Python 3.10+** (Recomendado 3.12)
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
    python3 -m venv venv
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
   La documentacion estará disponible en `http://127.0.0.1:8000/docs` o `http://127.0.0.1:8000/redoc`.

### Ejecución con Docker

El proyecto está completamente preparado para ser ejecutado en contenedores Docker con **MariaDB** como base de datos y un stack de monitoreo completo (Prometheus, Grafana, Loki).

1. Asegúrate de tener Docker y Docker Compose instalados.

2. Modifica el archivo `.env` con las configuraciones necesarias para MariaDB (revisa `compose.yml` para ver las variables esperadas).

3. Construye y levanta los contenedores en segundo plano:

    ```bash
    docker compose up -d --build
    ```

### Próximos pasos

- Implementar una configuración más robusta para producción en Kubernetes.
- Mejorar el sistema de autenticación y autorización.
- Crear más rutas y añadir funcionalidad adicional a la API.

## Estructura del Proyecto

    ```bash
    .
    ├── compose.yml
    ├── Dockerfile
    ├── LICENSE
    ├── movie_api_db.sqlite
    ├── movies.json
    ├── pytest.ini
    ├── README.md
    ├── requirements.txt
    └── src
        ├── config
        │   ├── db.py
        │   ├── __init__.py
        │   └── security.py
        ├── main.py
        ├── middlewares
        │   ├── error_handler.py
        │   ├── __init__.py
        │   └── jwt_bearer.py
        ├── models
        │   ├── __init__.py
        │   ├── movie.py
        │   └── user.py
        ├── requirements.txt
        ├── routers
        │   ├── __init__.py
        │   ├── movie.py
        │   └── user.py
        ├── schemas
        │   ├── __init__.py
        │   ├── movie.py
        │   └── user.py
        ├── services
        │   ├── __init__.py
        │   ├── movie.py
        │   └── user.py
        └── tests
            ├── __init__.py
            ├── routers
            │   ├── __init__.py
            │   ├── movie.py
            │   └── test_user.py
            └── test_main.py
    ```

## Licencia

Este proyecto está licenciado bajo los términos de la [GNU General Public License v3.0](./LICENSE).

---

¡Gracias por revisar mi proyecto! Estoy aprendiendo y abierto a sugerencias y contribuciones.
