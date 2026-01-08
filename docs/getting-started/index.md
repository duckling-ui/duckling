# Getting Started

Welcome to Duckling! This section will help you get up and running quickly.

!!! tip "Fastest Way to Start"
    **Using Docker?** Run this single command and you're done:
    ```bash
    curl -O https://raw.githubusercontent.com/davidgs/duckling/main/docker-compose.prebuilt.yml && docker-compose -f docker-compose.prebuilt.yml up -d
    ```
    Then open [http://localhost:3000](http://localhost:3000) in your browser.

## Prerequisites

=== "Docker (Recommended)"

    - **Docker 20.10+**
    - **Docker Compose 2.0+**

    That's it! No Python or Node.js required.

=== "Local Development"

    - **Python 3.10+** (3.13 recommended)
    - **Node.js 18+**
    - **npm or yarn**
    - **Git**

## Installation Options

Choose the installation method that works best for you:

<div class="grid cards" markdown>

-   :material-docker:{ .lg .middle } __Docker (Recommended)__

    ---

    The fastest way to get started. One command deployment with pre-built images.

    [:octicons-arrow-right-24: Docker Guide](docker.md)

-   :material-rocket-launch:{ .lg .middle } __Quick Start__

    ---

    Get started in 5 minutes with the essentials

    [:octicons-arrow-right-24: Quick Start](quickstart.md)

-   :material-code-braces:{ .lg .middle } __Local Development__

    ---

    Set up a local development environment for customization and contribution

    [:octicons-arrow-right-24: Installation Guide](installation.md)

</div>

## What's Next?

After installation, explore:

1. **[Features](../user-guide/features.md)** - Learn about all the capabilities
2. **[Configuration](../user-guide/configuration.md)** - Customize settings for your needs
3. **[API Reference](../api/index.md)** - Integrate with your applications

