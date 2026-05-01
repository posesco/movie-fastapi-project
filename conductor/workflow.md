# Estrategia de Flujo de Trabajo: GitFlow + SemVer

Este proyecto sigue estrictamente el modelo **GitFlow** para la gestión de ramas y **Semantic Versioning (SemVer)** para el control de versiones.

## 1. Ramas Principales

| Rama | Propósito | Estado |
| :--- | :--- | :--- |
| `master` | Producción. Solo contiene código estable y listo para el usuario final. | Siempre estable. |
| `develop` | Integración. Rama principal para el desarrollo diario. | Últimos cambios integrados. |

## 2. Ramas de Apoyo

### Feature branches (`feat/*`)
- **Propósito:** Desarrollar nuevas funcionalidades.
- **Rama de origen:** `develop`.
- **Rama de destino:** `develop`.
- **Convención:** `feat/nombre-de-la-tarea`.

### Release branches (`release/*`)
- **Propósito:** Preparar un nuevo lanzamiento a producción (limpieza de código, documentación, versionado).
- **Rama de origen:** `develop`.
- **Rama de destino:** `master` y `develop`.
- **Convención:** `release/vX.Y.Z`.

### Hotfix branches (`hotfix/*`)
- **Propósito:** Corregir errores críticos detectados en producción (`master`).
- **Rama de origen:** `master`.
- **Rama de destino:** `master` y `develop`.
- **Convención:** `hotfix/vX.Y.Z`.

## 3. Semantic Versioning (SemVer 2.0.0)

El formato de versión es **vMAJOR.MINOR.PATCH**:
1.  **MAJOR:** Cambios incompatibles con versiones anteriores (breaking changes).
2.  **MINOR:** Nuevas funcionalidades compatibles con versiones anteriores.
3.  **PATCH:** Corrección de errores (bug fixes) compatibles con versiones anteriores.

### Etiquetas (Tags)
Cada fusión a `master` debe generar una etiqueta anotada con la versión correspondiente:
```bash
git tag -a v1.0.0 -m "Release v1.0.0"
```

## 4. Convención de Commits (Conventional Commits)

Todos los mensajes de commit deben seguir el estándar:
- `feat:` Nueva funcionalidad.
- `fix:` Corrección de error.
- `docs:` Cambios en documentación.
- `style:` Cambios estéticos (formato, espacios, etc.).
- `refactor:` Refactorización de código sin cambio funcional.
- `test:` Añadir o corregir pruebas.
- `chore:` Tareas de mantenimiento (dependencias, configuración).

---
*Nota: El agente Gemini CLI debe validar siempre que se encuentra en la rama correcta antes de realizar cualquier cambio.*
