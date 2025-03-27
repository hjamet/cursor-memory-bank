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