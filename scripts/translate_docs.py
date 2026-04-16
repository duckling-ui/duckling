#!/usr/bin/env python3
"""
Translate documentation from English to target locales (de, es, fr).

Reads English source files from docs/, applies phrase-based translation
using a dictionary, preserves code blocks and technical terms, and writes
to docs/{locale}/.

Usage:
    python scripts/translate_docs.py                    # All files, all locales
    python scripts/translate_docs.py --file quickstart  # Single file
    python scripts/translate_docs.py --locale de        # Single locale
"""

import argparse
import re
from pathlib import Path
from typing import List, Optional

# Base path for docs
DOCS_ROOT = Path(__file__).resolve().parent.parent / "docs"

# Files to translate (relative to docs/)
FILES_TO_TRANSLATE = [
    "getting-started/quickstart.md",
    "getting-started/docker.md",
    "deployment/index.md",
    "deployment/production.md",
    "deployment/scaling.md",
    "architecture/index.md",
    "architecture/overview.md",
    "architecture/components.md",
    "architecture/diagrams.md",
    "api/index.md",
    "api/conversion.md",
    "user-guide/index.md",
    "user-guide/features.md",
    "user-guide/screenshots.md",
    "user-guide/formats.md",
    "user-guide/configuration.md",
]

LOCALES = ["de", "es", "fr"]

# Translation dictionary: English phrase -> {locale: translated phrase}
# Order matters: longer phrases should come first to avoid partial replacements
TRANSLATIONS = {
    # Headers and titles
    "Quick Start": {"de": "Schnellstart", "es": "Inicio rápido", "fr": "Démarrage rapide"},
    "Starting the Application": {"de": "Anwendung starten", "es": "Iniciar la aplicación", "fr": "Démarrer l'application"},
    "Your First Conversion": {"de": "Ihre erste Konvertierung", "es": "Tu primera conversión", "fr": "Votre première conversion"},
    "Basic Configuration": {"de": "Grundkonfiguration", "es": "Configuración básica", "fr": "Configuration de base"},
    "Batch Processing": {"de": "Stapelverarbeitung", "es": "Procesamiento por lotes", "fr": "Traitement par lots"},
    "Using the API": {"de": "API verwenden", "es": "Usar la API", "fr": "Utiliser l'API"},
    "Next Steps": {"de": "Nächste Schritte", "es": "Próximos pasos", "fr": "Prochaines étapes"},
    "Docker Deployment": {"de": "Docker-Bereitstellung", "es": "Despliegue con Docker", "fr": "Déploiement Docker"},
    "Deployment": {"de": "Bereitstellung", "es": "Despliegue", "fr": "Déploiement"},
    "Architecture": {"de": "Architektur", "es": "Arquitectura", "fr": "Architecture"},
    "Overview": {"de": "Übersicht", "es": "Resumen", "fr": "Vue d'ensemble"},
    "API Reference": {"de": "API-Referenz", "es": "Referencia de la API", "fr": "Référence API"},
    "Configuration": {"de": "Konfiguration", "es": "Configuración", "fr": "Configuration"},
    "Features": {"de": "Funktionen", "es": "Características", "fr": "Fonctionnalités"},
    "Settings": {"de": "Einstellungen", "es": "Configuración", "fr": "Paramètres"},
    "OCR Settings": {"de": "OCR-Einstellungen", "es": "Configuración OCR", "fr": "Paramètres OCR"},
    "Table Settings": {"de": "Tabelleneinstellungen", "es": "Configuración de tablas", "fr": "Paramètres des tableaux"},
    "Image Settings": {"de": "Bildeinstellungen", "es": "Configuración de imágenes", "fr": "Paramètres des images"},
    "Prerequisites": {"de": "Voraussetzungen", "es": "Requisitos previos", "fr": "Prérequis"},
    "Docker Compose Files": {"de": "Docker Compose-Dateien", "es": "Archivos Docker Compose", "fr": "Fichiers Docker Compose"},
    "Building Docker Images": {"de": "Docker-Images erstellen", "es": "Construir imágenes Docker", "fr": "Construire les images Docker"},
    "Environment Variables": {"de": "Umgebungsvariablen", "es": "Variables de entorno", "fr": "Variables d'environnement"},
    "Managing Containers": {"de": "Container verwalten", "es": "Gestionar contenedores", "fr": "Gérer les conteneurs"},
    "Health Checks": {"de": "Health-Checks", "es": "Comprobaciones de estado", "fr": "Contrôles de santé"},
    "Troubleshooting": {"de": "Fehlerbehebung", "es": "Solución de problemas", "fr": "Dépannage"},
    "Security": {"de": "Sicherheit", "es": "Seguridad", "fr": "Sécurité"},
    "Production": {"de": "Produktion", "es": "Producción", "fr": "Production"},
    "Scaling": {"de": "Skalierung", "es": "Escalado", "fr": "Mise à l'échelle"},
    "User Guide": {"de": "Benutzerhandbuch", "es": "Guía del usuario", "fr": "Guide utilisateur"},
    "Deployment Options": {"de": "Bereitstellungsoptionen", "es": "Opciones de despliegue", "fr": "Options de déploiement"},
    "Quick Reference": {"de": "Kurzreferenz", "es": "Referencia rápida", "fr": "Référence rapide"},
    "Environment Checklist": {"de": "Umgebungs-Checkliste", "es": "Lista de comprobación del entorno", "fr": "Liste de contrôle de l'environnement"},
    "Key Design Decisions": {"de": "Wichtige Designentscheidungen", "es": "Decisiones de diseño clave", "fr": "Décisions de conception clés"},
    "Components": {"de": "Komponenten", "es": "Componentes", "fr": "Composants"},
    "Diagrams": {"de": "Diagramme", "es": "Diagramas", "fr": "Diagrammes"},
    "Sections": {"de": "Abschnitte", "es": "Secciones", "fr": "Sections"},
    "System Overview": {"de": "Systemübersicht", "es": "Resumen del sistema", "fr": "Vue d'ensemble du système"},
    "Separation of Concerns": {"de": "Trennung der Belange", "es": "Separación de responsabilidades", "fr": "Séparation des préoccupations"},
    "Supported Formats": {"de": "Unterstützte Formate", "es": "Formatos compatibles", "fr": "Formats pris en charge"},
    "Screenshots": {"de": "Screenshots", "es": "Capturas de pantalla", "fr": "Captures d'écran"},
    "Formats": {"de": "Formate", "es": "Formatos", "fr": "Formats"},
    "Conversion": {"de": "Konvertierung", "es": "Conversión", "fr": "Conversion"},
    "Description": {"de": "Beschreibung", "es": "Descripción", "fr": "Description"},
    "Default": {"de": "Standard", "es": "Predeterminado", "fr": "Par défaut"},
    "Setting": {"de": "Einstellung", "es": "Configuración", "fr": "Paramètre"},
    "Enabled": {"de": "Aktiviert", "es": "Habilitado", "fr": "Activé"},
    "Backend": {"de": "Backend", "es": "Backend", "fr": "Backend"},
    "Language": {"de": "Sprache", "es": "Idioma", "fr": "Langue"},
    "Mode": {"de": "Modus", "es": "Modo", "fr": "Mode"},
    "Extract": {"de": "Extrahieren", "es": "Extraer", "fr": "Extraire"},
    "Scale": {"de": "Skalierung", "es": "Escala", "fr": "Échelle"},
    "Purpose": {"de": "Zweck", "es": "Propósito", "fr": "Objectif"},
    "Method": {"de": "Methode", "es": "Método", "fr": "Méthode"},
    "Best For": {"de": "Am besten für", "es": "Mejor para", "fr": "Idéal pour"},
    "Complexity": {"de": "Komplexität", "es": "Complejidad", "fr": "Complexité"},
    "Secret": {"de": "Geheimnis", "es": "Secreto", "fr": "Secret"},
    "File": {"de": "Datei", "es": "Archivo", "fr": "Fichier"},
    "Development": {"de": "Entwicklung", "es": "Desarrollo", "fr": "Développement"},
    "Manual Setup": {"de": "Manuelle Einrichtung", "es": "Configuración manual", "fr": "Configuration manuelle"},
    "Manual Deployment": {"de": "Manuelle Bereitstellung", "es": "Despliegue manual", "fr": "Déploiement manuel"},
    "Manual Build": {"de": "Manueller Build", "es": "Construcción manual", "fr": "Construction manuelle"},
    "View Status": {"de": "Status anzeigen", "es": "Ver estado", "fr": "Voir le statut"},
    "View Logs": {"de": "Protokolle anzeigen", "es": "Ver registros", "fr": "Voir les journaux"},
    "Stop Services": {"de": "Dienste stoppen", "es": "Detener servicios", "fr": "Arrêter les services"},
    "Restart Services": {"de": "Dienste neu starten", "es": "Reiniciar servicios", "fr": "Redémarrer les services"},
    "GPU Support": {"de": "GPU-Unterstützung", "es": "Soporte GPU", "fr": "Support GPU"},
    "Persistent Storage": {"de": "Persistenter Speicher", "es": "Almacenamiento persistente", "fr": "Stockage persistant"},
    "Resource Limits": {"de": "Ressourcenlimits", "es": "Límites de recursos", "fr": "Limites de ressources"},
    "Networking": {"de": "Netzwerk", "es": "Red", "fr": "Réseau"},
    "Resource usage": {"de": "Ressourcenverbrauch", "es": "Uso de recursos", "fr": "Utilisation des ressources"},
    "Container status": {"de": "Container-Status", "es": "Estado del contenedor", "fr": "État du conteneur"},
    "Container Won't Start": {"de": "Container startet nicht", "es": "El contenedor no inicia", "fr": "Le conteneur ne démarre pas"},
    "Port Conflicts": {"de": "Portkonflikte", "es": "Conflictos de puertos", "fr": "Conflits de ports"},
    "Build Failures": {"de": "Build-Fehler", "es": "Fallos de construcción", "fr": "Échecs de construction"},
    "Memory Issues": {"de": "Speicherprobleme", "es": "Problemas de memoria", "fr": "Problèmes de mémoire"},
    "Network Issues": {"de": "Netzwerkprobleme", "es": "Problemas de red", "fr": "Problèmes de réseau"},
    "Performance": {"de": "Leistung", "es": "Rendimiento", "fr": "Performances"},
    "First Run": {"de": "Erster Start", "es": "Primera ejecución", "fr": "Premier démarrage"},
    "Documentation Build": {"de": "Dokumentations-Build", "es": "Construcción de documentación", "fr": "Construction de la documentation"},
    "Automatic Publishing (CI/CD)": {"de": "Automatische Veröffentlichung (CI/CD)", "es": "Publicación automática (CI/CD)", "fr": "Publication automatique (CI/CD)"},
    "Build Script": {"de": "Build-Skript", "es": "Script de construcción", "fr": "Script de construction"},
    "Required repository secrets": {"de": "Erforderliche Repository-Geheimnisse", "es": "Secretos de repositorio requeridos", "fr": "Secrets de dépôt requis"},
    "Backup Data": {"de": "Daten sichern", "es": "Respaldar datos", "fr": "Sauvegarder les données"},
    "Default (Bind Mounts)": {"de": "Standard (Bind Mounts)", "es": "Predeterminado (Bind Mounts)", "fr": "Par défaut (Bind Mounts)"},
    "Named Volumes (Recommended for Production)": {"de": "Benannte Volumes (empfohlen für Produktion)", "es": "Volúmenes con nombre (recomendado para producción)", "fr": "Volumes nommés (recommandé pour la production)"},
    "TL;DR - One Command Start": {"de": "TL;DR - Ein-Befehl-Start", "es": "TL;DR - Inicio con un comando", "fr": "TL;DR - Démarrage en une commande"},
    "Documentation": {"de": "Dokumentation", "es": "Documentación", "fr": "Documentation"},
    "Guides for deploying Duckling in various environments.": {"de": "Anleitungen zur Bereitstellung von Duckling in verschiedenen Umgebungen.", "es": "Guías para desplegar Duckling en diversos entornos.", "fr": "Guides pour déployer Duckling dans différents environnements."},
    "Technical architecture documentation for Duckling.": {"de": "Technische Architektur-Dokumentation für Duckling.", "es": "Documentación técnica de la arquitectura de Duckling.", "fr": "Documentation technique de l'architecture de Duckling."},
    "Deploy Duckling using Docker for quick setup and isolation.": {"de": "Stellen Sie Duckling mit Docker für schnelle Einrichtung und Isolation bereit.", "es": "Despliega Duckling con Docker para una configuración rápida y aislamiento.", "fr": "Déployez Duckling avec Docker pour une configuration rapide et une isolation."},
    "Get started with Duckling in 5 minutes.": {"de": "Starten Sie in 5 Minuten mit Duckling.", "es": "Comienza con Duckling en 5 minutos.", "fr": "Démarrez avec Duckling en 5 minutes."},
    "Choose your preferred method:": {"de": "Wählen Sie Ihre bevorzugte Methode:", "es": "Elige tu método preferido:", "fr": "Choisissez votre méthode préférée :"},
    "Docker (Recommended)": {"de": "Docker (empfohlen)", "es": "Docker (recomendado)", "fr": "Docker (recommandé)"},
    "The fastest way to get started - no dependencies to install!": {"de": "Der schnellste Weg zum Start - keine Abhängigkeiten zu installieren!", "es": "¡La forma más rápida de empezar - sin dependencias que instalar!", "fr": "Le moyen le plus rapide de démarrer - aucune dépendance à installer !"},
    "Option 1: Pre-built Images (Fastest)": {"de": "Option 1: Vorgefertigte Images (am schnellsten)", "es": "Opción 1: Imágenes preconstruidas (más rápido)", "fr": "Option 1 : Images préconstruites (le plus rapide)"},
    "Option 2: Build Locally": {"de": "Option 2: Lokal erstellen", "es": "Opción 2: Construir localmente", "fr": "Option 2 : Construire localement"},
    "The UI will be available at": {"de": "Die Benutzeroberfläche ist verfügbar unter", "es": "La interfaz estará disponible en", "fr": "L'interface sera disponible à"},
    "The API will be available at": {"de": "Die API ist verfügbar unter", "es": "La API estará disponible en", "fr": "L'API sera disponible à"},
    "The first startup may take a few minutes as Docker downloads/builds the images.": {"de": "Der erste Start kann einige Minuten dauern, da Docker die Images herunterlädt/erstellt.", "es": "El primer inicio puede tardar unos minutos mientras Docker descarga/construye las imágenes.", "fr": "Le premier démarrage peut prendre quelques minutes pendant que Docker télécharge/construit les images."},
    "Terminal 1: Backend": {"de": "Terminal 1: Backend", "es": "Terminal 1: Backend", "fr": "Terminal 1 : Backend"},
    "Terminal 2: Frontend": {"de": "Terminal 2: Frontend", "es": "Terminal 2: Frontend", "fr": "Terminal 2 : Frontend"},
    "1. Open the Application": {"de": "1. Anwendung öffnen", "es": "1. Abrir la aplicación", "fr": "1. Ouvrir l'application"},
    "2. Upload a Document": {"de": "2. Dokument hochladen", "es": "2. Subir un documento", "fr": "2. Télécharger un document"},
    "3. Watch the Progress": {"de": "3. Fortschritt beobachten", "es": "3. Ver el progreso", "fr": "3. Suivre la progression"},
    "4. Download Results": {"de": "4. Ergebnisse herunterladen", "es": "4. Descargar resultados", "fr": "4. Télécharger les résultats"},
    "Navigate to": {"de": "Navigieren Sie zu", "es": "Navega a", "fr": "Accédez à"},
    "in your browser.": {"de": "in Ihrem Browser.", "es": "en tu navegador.", "fr": "dans votre navigateur."},
    "The main Duckling interface": {"de": "Die Hauptoberfläche von Duckling", "es": "La interfaz principal de Duckling", "fr": "L'interface principale de Duckling"},
    "Drag and drop a PDF, Word document, or image onto the drop zone, or click to browse.": {"de": "Ziehen Sie eine PDF-, Word-Datei oder ein Bild in die Ablagezone oder klicken Sie zum Durchsuchen.", "es": "Arrastra y suelta un PDF, documento Word o imagen en la zona de soltar, o haz clic para explorar.", "fr": "Glissez-déposez un PDF, document Word ou image dans la zone de dépôt, ou cliquez pour parcourir."},
    "Upload progress indicator": {"de": "Fortschrittsanzeige beim Hochladen", "es": "Indicador de progreso de carga", "fr": "Indicateur de progression du téléchargement"},
    "The conversion progress will be displayed in real-time.": {"de": "Der Konvertierungsfortschritt wird in Echtzeit angezeigt.", "es": "El progreso de conversión se mostrará en tiempo real.", "fr": "La progression de la conversion sera affichée en temps réel."},
    "Real-time conversion progress": {"de": "Echtzeit-Konvertierungsfortschritt", "es": "Progreso de conversión en tiempo real", "fr": "Progression de conversion en temps réel"},
    "Once complete, choose your export format:": {"de": "Wählen Sie nach Abschluss Ihr Exportformat:", "es": "Una vez completado, elige tu formato de exportación:", "fr": "Une fois terminé, choisissez votre format d'exportation :"},
    "Conversion complete with export options": {"de": "Konvertierung abgeschlossen mit Exportoptionen", "es": "Conversión completa con opciones de exportación", "fr": "Conversion terminée avec options d'export"},
    "Great for documentation": {"de": "Ideal für Dokumentation", "es": "Ideal para documentación", "fr": "Idéal pour la documentation"},
    "Web-ready output": {"de": "Webfertige Ausgabe", "es": "Salida lista para web", "fr": "Sortie prête pour le web"},
    "Full document structure": {"de": "Vollständige Dokumentstruktur", "es": "Estructura completa del documento", "fr": "Structure complète du document"},
    "Simple text extraction": {"de": "Einfache Textextraktion", "es": "Extracción de texto simple", "fr": "Extraction de texte simple"},
    "Click the": {"de": "Klicken Sie auf", "es": "Haz clic en", "fr": "Cliquez sur"},
    "button to configure:": {"de": "Schaltfläche zum Konfigurieren:", "es": "botón para configurar:", "fr": "bouton pour configurer :"},
    "Enable OCR for scanned documents": {"de": "OCR für gescannte Dokumente aktivieren", "es": "Habilitar OCR para documentos escaneados", "fr": "Activer l'OCR pour les documents numérisés"},
    "OCR engine to use": {"de": "Zu verwendende OCR-Engine", "es": "Motor OCR a utilizar", "fr": "Moteur OCR à utiliser"},
    "Primary language": {"de": "Hauptsprache", "es": "Idioma principal", "fr": "Langue principale"},
    "Extract tables from documents": {"de": "Tabellen aus Dokumenten extrahieren", "es": "Extraer tablas de documentos", "fr": "Extraire les tableaux des documents"},
    "Detection accuracy level": {"de": "Erkennungsgenauigkeitsstufe", "es": "Nivel de precisión de detección", "fr": "Niveau de précision de détection"},
    "Extract embedded images": {"de": "Eingebettete Bilder extrahieren", "es": "Extraer imágenes incrustadas", "fr": "Extraire les images intégrées"},
    "Image output scale": {"de": "Bildausgabeskalierung", "es": "Escala de salida de imagen", "fr": "Échelle de sortie des images"},
    "To convert multiple files at once:": {"de": "Um mehrere Dateien gleichzeitig zu konvertieren:", "es": "Para convertir varios archivos a la vez:", "fr": "Pour convertir plusieurs fichiers à la fois :"},
    "Toggle": {"de": "Aktivieren", "es": "Activar", "fr": "Activer"},
    "Batch Mode": {"de": "Stapelmodus", "es": "Modo por lotes", "fr": "Mode lot"},
    "in the header": {"de": "in der Kopfzeile", "es": "en el encabezado", "fr": "dans l'en-tête"},
    "Drag multiple files onto the drop zone": {"de": "Ziehen Sie mehrere Dateien in die Ablagezone", "es": "Arrastra varios archivos a la zona de soltar", "fr": "Glissez plusieurs fichiers dans la zone de dépôt"},
    "All files will be processed simultaneously": {"de": "Alle Dateien werden gleichzeitig verarbeitet", "es": "Todos los archivos se procesarán simultáneamente", "fr": "Tous les fichiers seront traités simultanément"},
    "Batch mode with multiple files": {"de": "Stapelmodus mit mehreren Dateien", "es": "Modo por lotes con varios archivos", "fr": "Mode lot avec plusieurs fichiers"},
    "Batch processing uses a job queue with a maximum of 2 concurrent conversions to prevent memory exhaustion.": {"de": "Die Stapelverarbeitung verwendet eine Job-Warteschlange mit maximal 2 gleichzeitigen Konvertierungen, um Speichererschöpfung zu vermeiden.", "es": "El procesamiento por lotes usa una cola de trabajos con un máximo de 2 conversiones simultáneas para evitar el agotamiento de memoria.", "fr": "Le traitement par lots utilise une file d'attente de tâches avec un maximum de 2 conversions simultanées pour éviter l'épuisement de la mémoire."},
    "For programmatic access, use the REST API:": {"de": "Für programmatischen Zugriff verwenden Sie die REST-API:", "es": "Para acceso programático, usa la API REST:", "fr": "Pour un accès programmatique, utilisez l'API REST :"},
    "Check the": {"de": "Siehe die", "es": "Consulta la", "fr": "Consultez la"},
    "for complete documentation.": {"de": "für vollständige Dokumentation.", "es": "para documentación completa.", "fr": "pour la documentation complète."},
    "Explore all capabilities": {"de": "Alle Funktionen erkunden", "es": "Explorar todas las capacidades", "fr": "Explorer toutes les fonctionnalités"},
    "Advanced settings": {"de": "Erweiterte Einstellungen", "es": "Configuración avanzada", "fr": "Paramètres avancés"},
    "Integrate with your apps": {"de": "In Ihre Apps integrieren", "es": "Integrar con tus aplicaciones", "fr": "Intégrer à vos applications"},
    "Download the compose file": {"de": "Compose-Datei herunterladen", "es": "Descargar el archivo compose", "fr": "Télécharger le fichier compose"},
    "Start Duckling": {"de": "Duckling starten", "es": "Iniciar Duckling", "fr": "Démarrer Duckling"},
    "Clone and start": {"de": "Klonen und starten", "es": "Clonar e iniciar", "fr": "Cloner et démarrer"},
    "Upload and convert a document": {"de": "Dokument hochladen und konvertieren", "es": "Subir y convertir un documento", "fr": "Télécharger et convertir un document"},
    "Response": {"de": "Antwort", "es": "Respuesta", "fr": "Réponse"},
    "Processing": {"de": "Verarbeitung", "es": "Procesando", "fr": "Traitement"},
    "accurate": {"de": "genau", "es": "preciso", "fr": "précis"},
    "Markdown": {"de": "Markdown", "es": "Markdown", "fr": "Markdown"},
    "HTML": {"de": "HTML", "es": "HTML", "fr": "HTML"},
    "JSON": {"de": "JSON", "es": "JSON", "fr": "JSON"},
    "Plain Text": {"de": "Klartext", "es": "Texto plano", "fr": "Texte brut"},
    "Docker (Simplest)": {"de": "Docker (am einfachsten)", "es": "Docker (más simple)", "fr": "Docker (le plus simple)"},
    "Quick deployment, testing": {"de": "Schnelle Bereitstellung, Tests", "es": "Despliegue rápido, pruebas", "fr": "Déploiement rapide, tests"},
    "Full control, customization": {"de": "Volle Kontrolle, Anpassung", "es": "Control total, personalización", "fr": "Contrôle total, personnalisation"},
    "Large scale, cloud-native": {"de": "Großer Maßstab, Cloud-nativ", "es": "Gran escala, nativo de la nube", "fr": "Grande échelle, cloud-native"},
    "Low": {"de": "Niedrig", "es": "Bajo", "fr": "Faible"},
    "Medium": {"de": "Mittel", "es": "Medio", "fr": "Moyen"},
    "High": {"de": "Hoch", "es": "Alto", "fr": "Élevé"},
    "Deploy with Gunicorn, Nginx, and systemd": {"de": "Bereitstellung mit Gunicorn, Nginx und systemd", "es": "Desplegar con Gunicorn, Nginx y systemd", "fr": "Déployer avec Gunicorn, Nginx et systemd"},
    "Production Guide": {"de": "Produktionsanleitung", "es": "Guía de producción", "fr": "Guide de production"},
    "Scale for high traffic with load balancing": {"de": "Skalierung für hohen Verkehr mit Lastausgleich", "es": "Escalar para alto tráfico con balanceo de carga", "fr": "Mettre à l'échelle pour un trafic élevé avec équilibrage de charge"},
    "Scaling Guide": {"de": "Skalierungsanleitung", "es": "Guía de escalado", "fr": "Guide de mise à l'échelle"},
    "Security best practices and hardening": {"de": "Sicherheitsbest Practices und Härtung", "es": "Mejores prácticas de seguridad y endurecimiento", "fr": "Bonnes pratiques de sécurité et durcissement"},
    "Security Guide": {"de": "Sicherheitsanleitung", "es": "Guía de seguridad", "fr": "Guide de sécurité"},
    "Before deploying to production:": {"de": "Vor der Bereitstellung in der Produktion:", "es": "Antes de desplegar en producción:", "fr": "Avant de déployer en production :"},
    "Set strong": {"de": "Setzen Sie einen starken", "es": "Establece una", "fr": "Définissez une"},
    "Set": {"de": "Setzen", "es": "Establecer", "fr": "Définir"},
    "Configure CORS for your domain": {"de": "CORS für Ihre Domain konfigurieren", "es": "Configurar CORS para tu dominio", "fr": "Configurer CORS pour votre domaine"},
    "Enable HTTPS": {"de": "HTTPS aktivieren", "es": "Habilitar HTTPS", "fr": "Activer HTTPS"},
    "Set appropriate file size limits": {"de": "Angemessene Dateigrößenlimits setzen", "es": "Establecer límites de tamaño de archivo apropiados", "fr": "Définir des limites de taille de fichier appropriées"},
    "Configure reverse proxy": {"de": "Reverse-Proxy konfigurieren", "es": "Configurar proxy inverso", "fr": "Configurer le proxy inverse"},
    "Set up monitoring and logging": {"de": "Überwachung und Protokollierung einrichten", "es": "Configurar monitoreo y registro", "fr": "Configurer la surveillance et la journalisation"},
    "High-level architecture and data flow": {"de": "Architektur auf hoher Ebene und Datenfluss", "es": "Arquitectura de alto nivel y flujo de datos", "fr": "Architecture de haut niveau et flux de données"},
    "Frontend and backend component details": {"de": "Details zu Frontend- und Backend-Komponenten", "es": "Detalles de componentes frontend y backend", "fr": "Détails des composants frontend et backend"},
    "Architecture diagrams and flowcharts": {"de": "Architekturdiagramme und Flussdiagramme", "es": "Diagramas de arquitectura y flujos", "fr": "Diagrammes d'architecture et organigrammes"},
    "Frontend": {"de": "Frontend", "es": "Frontend", "fr": "Frontend"},
    "Backend": {"de": "Backend", "es": "Backend", "fr": "Backend"},
    "Engine": {"de": "Engine", "es": "Motor", "fr": "Moteur"},
    "React with TypeScript for type safety and modern UI": {"de": "React mit TypeScript für Typsicherheit und moderne UI", "es": "React con TypeScript para seguridad de tipos y UI moderna", "fr": "React avec TypeScript pour la sécurité des types et une UI moderne"},
    "Flask for simplicity and Python ecosystem access": {"de": "Flask für Einfachheit und Python-Ökosystem-Zugang", "es": "Flask por simplicidad y acceso al ecosistema Python", "fr": "Flask pour la simplicité et l'accès à l'écosystème Python"},
    "Docling for document conversion (IBM's library)": {"de": "Docling für Dokumentkonvertierung (IBMs Bibliothek)", "es": "Docling para conversión de documentos (biblioteca de IBM)", "fr": "Docling pour la conversion de documents (bibliothèque IBM)"},
    "Access the application at": {"de": "Greifen Sie auf die Anwendung unter zu", "es": "Accede a la aplicación en", "fr": "Accédez à l'application à"},
    "Then open": {"de": "Dann öffnen Sie", "es": "Luego abre", "fr": "Puis ouvrez"},
    "Use the provided build script for easy image building.": {"de": "Verwenden Sie das bereitgestellte Build-Skript für einfaches Image-Building.", "es": "Usa el script de construcción proporcionado para una fácil construcción de imágenes.", "fr": "Utilisez le script de construction fourni pour une construction d'images facile."},
    "The script automatically builds the MkDocs documentation before building Docker images:": {"de": "Das Skript erstellt automatisch die MkDocs-Dokumentation vor dem Erstellen der Docker-Images:", "es": "El script construye automáticamente la documentación MkDocs antes de construir las imágenes Docker:", "fr": "Le script construit automatiquement la documentation MkDocs avant de construire les images Docker :"},
    "Always set a strong": {"de": "Setzen Sie immer einen starken", "es": "Siempre establece una", "fr": "Définissez toujours une"},
    "in production.": {"de": "in der Produktion.", "es": "en producción.", "fr": "en production."},
    "Generate one with:": {"de": "Erzeugen Sie einen mit:", "es": "Genera uno con:", "fr": "Générez-en un avec :"},
    "For GPU-accelerated OCR with NVIDIA GPUs:": {"de": "Für GPU-beschleunigtes OCR mit NVIDIA-GPUs:", "es": "Para OCR acelerado por GPU con GPUs NVIDIA:", "fr": "Pour l'OCR accéléré par GPU avec des GPU NVIDIA :"},
    "GPU support requires the": {"de": "GPU-Unterstützung erfordert das", "es": "El soporte GPU requiere el", "fr": "Le support GPU nécessite le"},
    "Both containers include health checks:": {"de": "Beide Container enthalten Health-Checks:", "es": "Ambos contenedores incluyen comprobaciones de estado:", "fr": "Les deux conteneurs incluent des contrôles de santé :"},
    "Check backend health": {"de": "Backend-Gesundheit prüfen", "es": "Comprobar estado del backend", "fr": "Vérifier la santé du backend"},
    "Check frontend (returns HTML)": {"de": "Frontend prüfen (gibt HTML zurück)", "es": "Comprobar frontend (devuelve HTML)", "fr": "Vérifier le frontend (retourne HTML)"},
    "Docker Compose waits for health checks:": {"de": "Docker Compose wartet auf Health-Checks:", "es": "Docker Compose espera las comprobaciones de estado:", "fr": "Docker Compose attend les contrôles de santé :"},
    "Production configuration includes resource limits:": {"de": "Die Produktionskonfiguration enthält Ressourcenlimits:", "es": "La configuración de producción incluye límites de recursos:", "fr": "La configuration de production inclut des limites de ressources :"},
    "Services communicate over a bridge network:": {"de": "Dienste kommunizieren über ein Bridge-Netzwerk:", "es": "Los servicios se comunican a través de una red puente:", "fr": "Les services communiquent via un réseau bridge :"},
    "The frontend proxies API requests to the backend:": {"de": "Das Frontend leitet API-Anfragen an das Backend weiter:", "es": "El frontend hace proxy de las solicitudes API al backend:", "fr": "Le frontend fait proxy des requêtes API vers le backend :"},
    "Check logs": {"de": "Protokolle prüfen", "es": "Comprobar registros", "fr": "Vérifier les journaux"},
    "Check container status": {"de": "Container-Status prüfen", "es": "Comprobar estado del contenedor", "fr": "Vérifier l'état du conteneur"},
    "Inspect container": {"de": "Container untersuchen", "es": "Inspeccionar contenedor", "fr": "Inspecter le conteneur"},
    "Change ports in": {"de": "Ports ändern in", "es": "Cambiar puertos en", "fr": "Changer les ports dans"},
    "Change external port": {"de": "Externen Port ändern", "es": "Cambiar puerto externo", "fr": "Changer le port externe"},
    "Clean build cache": {"de": "Build-Cache bereinigen", "es": "Limpiar caché de construcción", "fr": "Nettoyer le cache de construction"},
    "Rebuild without cache": {"de": "Ohne Cache neu erstellen", "es": "Reconstruir sin caché", "fr": "Reconstruire sans cache"},
    "Check memory usage": {"de": "Speicherverbrauch prüfen", "es": "Comprobar uso de memoria", "fr": "Vérifier l'utilisation de la mémoire"},
    "Increase Docker memory limit (Docker Desktop)": {"de": "Docker-Speicherlimit erhöhen (Docker Desktop)", "es": "Aumentar límite de memoria de Docker (Docker Desktop)", "fr": "Augmenter la limite de mémoire Docker (Docker Desktop)"},
    "List networks": {"de": "Netzwerke auflisten", "es": "Listar redes", "fr": "Lister les réseaux"},
    "Inspect network": {"de": "Netzwerk untersuchen", "es": "Inspeccionar red", "fr": "Inspecter le réseau"},
    "Recreate network": {"de": "Netzwerk neu erstellen", "es": "Recrear red", "fr": "Recréer le réseau"},
    "All services": {"de": "Alle Dienste", "es": "Todos los servicios", "fr": "Tous les services"},
    "Specific service": {"de": "Bestimmter Dienst", "es": "Servicio específico", "fr": "Service spécifique"},
    "Last 100 lines": {"de": "Letzte 100 Zeilen", "es": "Últimas 100 líneas", "fr": "100 dernières lignes"},
    "Stop containers": {"de": "Container stoppen", "es": "Detener contenedores", "fr": "Arrêter les conteneurs"},
    "Stop and remove volumes": {"de": "Container stoppen und Volumes entfernen", "es": "Detener y eliminar volúmenes", "fr": "Arrêter et supprimer les volumes"},
    "Stop and remove images": {"de": "Container stoppen und Images entfernen", "es": "Detener y eliminar imágenes", "fr": "Arrêter et supprimer les images"},
    "Restart all": {"de": "Alle neu starten", "es": "Reiniciar todo", "fr": "Redémarrer tout"},
    "Restart specific service": {"de": "Bestimmten Dienst neu starten", "es": "Reiniciar servicio específico", "fr": "Redémarrer le service spécifique"},
    "Development with local builds": {"de": "Entwicklung mit lokalen Builds", "es": "Desarrollo con construcciones locales", "fr": "Développement avec builds locaux"},
    "Production overrides": {"de": "Produktionsüberschreibungen", "es": "Anulaciones de producción", "fr": "Surcharges de production"},
    "Pre-built images from registry": {"de": "Vorgefertigte Images aus der Registry", "es": "Imágenes preconstruidas del registro", "fr": "Images préconstruites du registre"},
    "Or run in background": {"de": "Oder im Hintergrund ausführen", "es": "O ejecutar en segundo plano", "fr": "Ou exécuter en arrière-plan"},
    "Download": {"de": "Herunterladen", "es": "Descargar", "fr": "Télécharger"},
    "Start with pre-built images": {"de": "Mit vorgefertigten Images starten", "es": "Iniciar con imágenes preconstruidas", "fr": "Démarrer avec les images préconstruites"},
    "Using default registry (duckling-ui)": {"de": "Standard-Registry verwenden (duckling-ui)", "es": "Usando registro predeterminado (duckling-ui)", "fr": "Utilisation du registre par défaut (duckling-ui)"},
    "Using custom registry": {"de": "Benutzerdefinierte Registry verwenden", "es": "Usando registro personalizado", "fr": "Utilisation d'un registre personnalisé"},
    "Using specific version": {"de": "Bestimmte Version verwenden", "es": "Usando versión específica", "fr": "Utilisation d'une version spécifique"},
    "Build images locally (includes documentation build)": {"de": "Images lokal erstellen (inkl. Dokumentations-Build)", "es": "Construir imágenes localmente (incluye construcción de documentación)", "fr": "Construire les images localement (inclut la construction de la documentation)"},
    "Build and push to Docker Hub": {"de": "Erstellen und zu Docker Hub pushen", "es": "Construir y subir a Docker Hub", "fr": "Construire et pousser vers Docker Hub"},
    "Build with specific version": {"de": "Mit bestimmter Version erstellen", "es": "Construir con versión específica", "fr": "Construire avec une version spécifique"},
    "Build for multiple platforms (requires buildx)": {"de": "Für mehrere Plattformen erstellen (erfordert buildx)", "es": "Construir para múltiples plataformas (requiere buildx)", "fr": "Construire pour plusieurs plateformes (nécessite buildx)"},
    "Push to custom registry": {"de": "Zu benutzerdefinierter Registry pushen", "es": "Subir a registro personalizado", "fr": "Pousser vers un registre personnalisé"},
    "Skip documentation build (use existing site/)": {"de": "Dokumentations-Build überspringen (vorhandenes site/ verwenden)", "es": "Omitir construcción de documentación (usar site/ existente)", "fr": "Ignorer la construction de la documentation (utiliser site/ existant)"},
    "The build script automatically runs": {"de": "Das Build-Skript führt automatisch aus", "es": "El script de construcción ejecuta automáticamente", "fr": "Le script de construction exécute automatiquement"},
    "to ensure documentation is available in the Docker containers.": {"de": "um sicherzustellen, dass die Dokumentation in den Docker-Containern verfügbar ist.", "es": "para asegurar que la documentación esté disponible en los contenedores Docker.", "fr": "pour s'assurer que la documentation est disponible dans les conteneurs Docker."},
    "If MkDocs is not installed, it will attempt to install it from": {"de": "Wenn MkDocs nicht installiert ist, wird versucht, es aus zu installieren", "es": "Si MkDocs no está instalado, intentará instalarlo desde", "fr": "Si MkDocs n'est pas installé, il tentera de l'installer depuis"},
    "When a pull request is merged to": {"de": "Wenn ein Pull Request in", "es": "Cuando una solicitud de extracción se fusiona en", "fr": "Lorsqu'une pull request est fusionnée dans"},
    "the workflow automatically:": {"de": "wird der Workflow automatisch:", "es": "el flujo de trabajo automáticamente:", "fr": "le workflow automatiquement :"},
    "Builds multi-platform images (linux/amd64, linux/arm64)": {"de": "Erstellt Multi-Platform-Images (linux/amd64, linux/arm64)", "es": "Construye imágenes multiplataforma (linux/amd64, linux/arm64)", "fr": "Construit des images multi-plateformes (linux/amd64, linux/arm64)"},
    "Pushes to **Docker Hub** as": {"de": "Pusht zu **Docker Hub** als", "es": "Sube a **Docker Hub** como", "fr": "Pousse vers **Docker Hub** comme"},
    "Pushes to **GitHub Container Registry** as": {"de": "Pusht zu **GitHub Container Registry** als", "es": "Sube a **GitHub Container Registry** como", "fr": "Pousse vers **GitHub Container Registry** comme"},
    "Images are tagged with the version from": {"de": "Images werden mit der Version aus getaggt", "es": "Las imágenes se etiquetan con la versión de", "fr": "Les images sont étiquetées avec la version de"},
    "and": {"de": "und", "es": "y", "fr": "et"},
    "Docker Hub username": {"de": "Docker Hub-Benutzername", "es": "Nombre de usuario de Docker Hub", "fr": "Nom d'utilisateur Docker Hub"},
    "Docker Hub access token (or password)": {"de": "Docker Hub-Zugriffstoken (oder Passwort)", "es": "Token de acceso de Docker Hub (o contraseña)", "fr": "Jeton d'accès Docker Hub (ou mot de passe)"},
    "GHCR authentication uses": {"de": "GHCR-Authentifizierung verwendet", "es": "La autenticación GHCR usa", "fr": "L'authentification GHCR utilise"},
    "which GitHub Actions provides automatically.": {"de": "das GitHub Actions automatisch bereitstellt.", "es": "que GitHub Actions proporciona automáticamente.", "fr": "que GitHub Actions fournit automatiquement."},
    "Create a": {"de": "Erstellen Sie eine", "es": "Crea un", "fr": "Créez un"},
    "file in the project root:": {"de": "Datei im Projektstamm:", "es": "archivo en la raíz del proyecto:", "fr": "fichier à la racine du projet :"},
    "Security (required for production)": {"de": "Sicherheit (erforderlich für Produktion)", "es": "Seguridad (requerido para producción)", "fr": "Sécurité (requis pour la production)"},
    "Flask configuration": {"de": "Flask-Konfiguration", "es": "Configuración de Flask", "fr": "Configuration Flask"},
    "Optional: Custom registry for pre-built images": {"de": "Optional: Benutzerdefinierte Registry für vorgefertigte Images", "es": "Opcional: Registro personalizado para imágenes preconstruidas", "fr": "Optionnel : Registre personnalisé pour les images préconstruites"},
    "Backup volumes": {"de": "Volumes sichern", "es": "Respaldar volúmenes", "fr": "Sauvegarder les volumes"},
    "Restore volumes": {"de": "Volumes wiederherstellen", "es": "Restaurar volúmenes", "fr": "Restaurer les volumes"},
}


def extract_code_blocks(content: str) -> tuple:
    """
    Extract code blocks from content, return (non_code_parts, code_blocks).
    Non-code parts and code blocks alternate; we preserve order via indices.
    """
    # Match ```...``` including optional language identifier
    pattern = r"```[\w]*\n.*?```"
    parts = []
    code_blocks = []
    last_end = 0

    for match in re.finditer(pattern, content, re.DOTALL):
        # Non-code part before this block
        parts.append(content[last_end : match.start()])
        code_blocks.append(match.group(0))
        last_end = match.end()

    parts.append(content[last_end:])
    return parts, code_blocks


def reassemble_content(parts: list[str], code_blocks: list[str]) -> str:
    """Reassemble content from non-code parts and code blocks."""
    result = []
    for i, part in enumerate(parts):
        result.append(part)
        if i < len(code_blocks):
            result.append(code_blocks[i])
    return "".join(result)


def translate_text(text: str, locale: str) -> str:
    """Apply phrase-based translation to text. Longest phrases first."""
    if locale not in LOCALES:
        return text

    result = text
    # Sort by phrase length descending to replace longest first
    sorted_phrases = sorted(
        TRANSLATIONS.keys(),
        key=lambda p: len(p),
        reverse=True,
    )

    for phrase in sorted_phrases:
        if phrase in result and locale in TRANSLATIONS[phrase]:
            result = result.replace(phrase, TRANSLATIONS[phrase][locale])

    return result


def translate_content(content: str, locale: str) -> str:
    """Translate content, preserving code blocks."""
    parts, code_blocks = extract_code_blocks(content)
    translated_parts = [translate_text(p, locale) for p in parts]
    return reassemble_content(translated_parts, code_blocks)


def translate_file(source_path: Path, locale: str, files_filter: Optional[List[str]]) -> bool:
    """Translate a single file to the given locale."""
    rel = source_path.relative_to(DOCS_ROOT)
    rel_str = str(rel).replace("\\", "/")

    if files_filter and rel_str not in files_filter:
        # Also allow partial match (e.g. "quickstart" matches quickstart.md)
        if not any(f in rel_str for f in files_filter):
            return False

    if not source_path.exists():
        print(f"  Skip (not found): {rel_str}")
        return False

    content = source_path.read_text(encoding="utf-8")
    translated = translate_content(content, locale)

    out_path = DOCS_ROOT / locale / rel
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(translated, encoding="utf-8")
    print(f"  Wrote: {locale}/{rel_str}")
    return True


def main():
    parser = argparse.ArgumentParser(description="Translate docs from English to target locales")
    parser.add_argument(
        "--file",
        action="append",
        dest="files",
        help="Translate only these files (e.g. quickstart, docker). Can be repeated.",
    )
    parser.add_argument(
        "--locale",
        action="append",
        dest="locales",
        help="Translate only these locales (de, es, fr). Can be repeated.",
    )
    args = parser.parse_args()

    files_filter = args.files
    locales_to_use = args.locales or LOCALES

    for locale in locales_to_use:
        if locale not in LOCALES:
            print(f"Unknown locale: {locale}. Skipping.")
            continue
        print(f"\nLocale: {locale}")
        for rel_path in FILES_TO_TRANSLATE:
            source = DOCS_ROOT / rel_path
            translate_file(source, locale, files_filter)


if __name__ == "__main__":
    main()
