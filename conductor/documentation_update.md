# Plan de Actualización de Documentación

## Objetivo
Reflejar los cambios de la refactorización SOLID en la documentación principal del proyecto para asegurar que los desarrolladores y el agente (Marco) mantengan el contexto correcto.

## Cambios Propuestos

### 1. `GEMINI.md`
*   Actualizar la sección de **Key Technologies** para incluir el almacenamiento híbrido.
*   Añadir **Design Principles: SOLID** a las características principales.
*   Actualizar la sección de **Architecture** para mencionar la inyección de dependencias (DIP) y la separación de `AuthService` (SRP).
*   Mencionar el uso de Mixins en repositorios (ISP).

### 2. `README.md`
*   Añadir una mención a los principios SOLID en la introducción/características.
*   Actualizar la descripción de la arquitectura.
*   Añadir el soporte para almacenamiento local en la sección de características.

### 3. `.env.example`
*   Añadir las nuevas variables `STORAGE_BACKEND` y `LOCAL_STORAGE_PATH` con valores por defecto.

## Verificación
*   Revisar que la renderización de Markdown sea correcta.
*   Validar que las instrucciones para el agente en `GEMINI.md` sean claras y consistentes con el nuevo código.
