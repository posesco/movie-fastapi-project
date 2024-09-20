# FastAPI Starter Project (Movie API)

Este es mi proyecto inicial con **FastAPI**, en el que exploro y aprendo sobre esta potente herramienta para construir APIs modernas y de alto rendimiento. El objetivo de este proyecto es ir implementando características paso a paso, comenzando con una API básica y, en el futuro, avanzando a una arquitectura más robusta con MariaDB y contenedores.

## Características

- **FastAPI**: Marco web moderno y rápido para construir APIs con Python 3.7+ basado en estándares abiertos (OpenAPI y JSON Schema).
- **Pydantic**: Para validación de datos a través de modelos eficientes.
- **SQLAlchemy**: ORM utilizado para interactuar con la base de datos.
- **JWT Authentication**: Implementación de autenticación basada en JSON Web Tokens (JWT) con **PyJWT**.
- **SQLite**: Base de datos local para el desarrollo inicial, con planes de migración a **MariaDB** usando contenedores Docker.
- **Docker y Docker Compose**: Preparado para la implementación en entornos de contenedores utilizando **MariaDB** en futuras fases.

## Librerías utilizadas

- **FastAPI**: [FastAPI documentation](https://fastapi.tiangolo.com/)
- **Pydantic**: Para la validación de modelos de datos.
- **PyJWT**: Manejo de autenticación basada en tokens JWT.
- **Uvicorn**: Servidor ASGI para ejecutar la aplicación FastAPI.
- **python-dotenv**: Para gestionar variables de entorno.
- **SQLAlchemy**: ORM para la interacción con la base de datos.
- **SQLite**: Base de datos utilizada para desarrollo local (con planes de migración a MariaDB en producción).

## Instalación y Ejecución

### Requisitos previos

Asegúrate de tener instalado:

- **Python 3.7+**
- **pip** para la gestión de paquetes de Python
- **Docker** (opcional, para la configuración de contenedores y bases de datos)

### Instalación del entorno

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
    cd app
    pip install -r requirements.txt
    ```

### Ejecución en entorno local

1. Crea un archivo `.env` en la raíz del proyecto para configurar las variables de entorno (como claves JWT, base de datos, etc.).

2. Inicia el servidor de desarrollo:

    ```bash
    uvicorn main:app --reload --port 5000 --host 0.0.0.0
    ```

   La API estará disponible en `http://127.0.0.1:5000`.
   La documentacion estará disponible en `http://127.0.0.1:5000/docs` o `http://127.0.0.1:5000/redoc` .

### Uso de Docker (próximos pasos)

El proyecto está preparado para ser ejecutado en contenedores Docker con **MariaDB** como base de datos en lugar de SQLite. Estos son los pasos para el próximo despliegue:

1. Asegúrate de tener Docker y Docker Compose instalados.

2. Modifica el archivo `docker-compose.yml` con las configuraciones necesarias para MariaDB.

3. Construye y levanta los contenedores:

    ```bash
    docker-compose up --build
    ```

### Próximos pasos

- Migrar de **SQLite** a **MariaDB** utilizando Docker.
- Implementar una configuración más robusta para producción.
- Mejorar el sistema de autenticación y autorización.
- Crear más rutas y añadir funcionalidad adicional a la API.

## Estructura del Proyecto

    ```bash
    .
    ├── app
    │   ├── config
    │   │   ├── database.py
    │   │   └── __init__.py
    │   ├── database.sqlite
    │   ├── jwt_manager.py
    │   ├── main.py
    │   ├── middlewares
    │   │   ├── error_handler.py
    │   │   ├── __init__.py
    │   │   └── jwt_bearer.py
    │   ├── models
    │   │   ├── __init__.py
    │   │   └── movie.py
    │   ├── requirements.txt
    │   ├── routers
    │   │   ├── __init__.py
    │   │   ├── movie.py
    │   │   └── user.py
    │   ├── schemas
    │   │   ├── __init__.py
    │   │   ├── movie.py
    │   │   └── user.py
    │   └── services
    │       ├── __init__.py
    │       └── movie.py
    ├── compose.yml
    ├── Dockerfile
    ├── LICENSE
    ├── movies.json
    ├── README.md
    └── requirements.txt

    ```

## Licencia

Este proyecto está licenciado bajo los términos de la [GNU General Public License v3.0](./LICENSE).

---

¡Gracias por revisar mi proyecto! Estoy aprendiendo y abierto a sugerencias y contribuciones.