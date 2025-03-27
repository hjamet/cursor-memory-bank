# Contexte Technique

## Pile Technologique
- **Langages**: Bash
- **Outils**: curl, git
- **Tests**: Tests unitaires bash

## Architecture
Le projet est structuré en plusieurs composants:
- Script d'installation (`install.sh`):
  - Gestion des arguments
  - Création de répertoires
  - Sauvegarde des règles existantes
  - Nettoyage automatique
- Suite de tests (`tests/test_install.sh`)
- Documentation (`README.md`)

## Environnement de Développement
- **Configuration requise**:
  - Système Unix/Linux
  - Bash
  - curl
  - git
- **Installation**: Via curl ou clone git

## Conventions de Code
- Scripts bash avec shebang `#!/bin/bash`
- Utilisation de `set -e` et `set -u` pour la sécurité
- Documentation des fonctions et sections importantes
- Tests unitaires pour chaque fonctionnalité
- Gestion des erreurs avec trap et cleanup

## Dépendances Externes
- curl: Dernière version - Téléchargement des fichiers
- git: Dernière version - Gestion du code source

## Intégrations
- GitHub: Hébergement du code et distribution
- Cursor: Intégration avec l'IDE via les règles 

## Download Functionality
- Download mechanism now supports both local and remote files
- Uses `curl` for HTTP downloads and direct file access for local files
- Implements robust checksum verification using SHA256
- Handles both test and production environments through URL configuration
- Provides clear error messages and proper cleanup on failure

## Test Environment
- Supports isolated test environment with temporary directories
- Automatically creates and manages test files
- Handles both local and remote file testing scenarios
- Provides comprehensive test coverage for download functionality

## URL Management
- Production URLs use GitHub releases format
- Test URLs use local file:// protocol
- Proper URL construction with path joining
- Environment-aware URL selection 