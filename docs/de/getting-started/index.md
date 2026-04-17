# Erste Schritte

Willkommen bei Duckling! In diesem Abschnitt bringen Sie das Projekt schnell zum Laufen.

!!! tip "Schnellster Start"
    **Mit Docker?** Ein einziger Befehl genügt:
    ```bash
    curl -O https://raw.githubusercontent.com/duckling-ui/duckling/main/docker-compose.prebuilt.yml && docker-compose -f docker-compose.prebuilt.yml up -d
    ```
    Öffnen Sie anschließend [http://localhost:3000](http://localhost:3000) im Browser.

## Voraussetzungen

=== "Docker (empfohlen)"

    - **Docker 20.10+**
    - **Docker Compose 2.0+**

    Das war’s! Weder Python noch Node.js nötig.

=== "Lokale Entwicklung"

    - **Python 3.10+** (3.13 empfohlen)
    - **Node.js 18+**
    - **npm oder yarn**
    - **Git**

## Installationsoptionen

Wählen Sie die für Sie passende Methode:

<div class="grid cards" markdown>

-   :material-docker:{ .lg .middle } __Docker (empfohlen)__

    ---

    Der schnellste Einstieg. Ein Befehl mit vorgefertigten Images.

    [:octicons-arrow-right-24: Docker-Anleitung](docker.md)

-   :material-rocket-launch:{ .lg .middle } __Schnellstart__

    ---

    In 5 Minuten mit dem Wesentlichen starten

    [:octicons-arrow-right-24: Schnellstart](quickstart.md)

-   :material-code-braces:{ .lg .middle } __Lokale Entwicklung__

    ---

    Lokale Entwicklungsumgebung für Anpassungen und Beiträge einrichten

    [:octicons-arrow-right-24: Installationsanleitung](installation.md)

</div>

## Wie geht es weiter?

Nach der Installation können Sie folgendes vertiefen:

1. **[Funktionen](../user-guide/features.md)** – Alle Möglichkeiten kennenlernen
2. **[Konfiguration](../user-guide/configuration.md)** – Einstellungen an Ihre Bedürfnisse anpassen
3. **[API-Referenz](../api/index.md)** – In Ihre Anwendungen integrieren

