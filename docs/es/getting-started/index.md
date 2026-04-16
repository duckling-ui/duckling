# Primeros pasos

¡Bienvenido a Duckling! Esta sección le ayudará a poner el proyecto en marcha rápidamente.

!!! tip "Forma más rápida de empezar"
    **¿Usa Docker?** Ejecute este único comando y listo:
    ```bash
    curl -O https://raw.githubusercontent.com/duckling-ui/duckling/main/docker-compose.prebuilt.yml && docker-compose -f docker-compose.prebuilt.yml up -d
    ```
    Luego abra [http://localhost:3000](http://localhost:3000) en el navegador.

## Requisitos previos

=== "Docker (recomendado)"

    - **Docker 20.10+**
    - **Docker Compose 2.0+**

    ¡Eso es todo! No necesita Python ni Node.js.

=== "Desarrollo local"

    - **Python 3.10+** (se recomienda 3.13)
    - **Node.js 18+**
    - **npm o yarn**
    - **Git**

## Opciones de instalación

Elija el método que mejor le convenga:

<div class="grid cards" markdown>

-   :material-docker:{ .lg .middle } __Docker (recomendado)__

    ---

    La forma más rápida de empezar. Despliegue con un solo comando usando imágenes precompiladas.

    [:octicons-arrow-right-24: Guía de Docker](docker.md)

-   :material-rocket-launch:{ .lg .middle } __Inicio rápido__

    ---

    Póngase en marcha en 5 minutos con lo esencial

    [:octicons-arrow-right-24: Inicio rápido](quickstart.md)

-   :material-code-braces:{ .lg .middle } __Desarrollo local__

    ---

    Configure un entorno de desarrollo local para personalizar y contribuir

    [:octicons-arrow-right-24: Guía de instalación](installation.md)

</div>

## ¿Qué sigue?

Después de instalar, explore:

1. **[Funciones](../user-guide/features.md)** – Conozca todas las capacidades
2. **[Configuración](../user-guide/configuration.md)** – Adapte la configuración a sus necesidades
3. **[Referencia de la API](../api/index.md)** – Integre con sus aplicaciones

