# Architecture et aspects techniques

## Installation
- Installation via git clone
- Options disponibles :
  - `--no-backup` : Désactive la sauvegarde des règles existantes
  - `--dir` : Spécifie le répertoire d'installation
  - `--use-curl` : Force l'utilisation de curl au lieu de git clone
- Préservation des règles personnalisées via backup/restore
- Préservation automatique des fichiers existants non liés à l'installation
- Installation sans effacement des fichiers existants qui ne sont pas dans le dépôt
- Gestion robuste des erreurs :
  - Détection des erreurs dans les pipes (set -o pipefail)
  - Messages d'erreur descriptifs sur stderr
  - Capture des codes de sortie
  - Vérification des permissions
  - Vérification des dépendances (git)
  - Nettoyage des fichiers temporaires

## Structure du projet
- `.cursor/rules/` : Répertoire des règles
- `scripts/` : Scripts d'installation et utilitaires
- `tests/` : Tests unitaires et d'intégration

## Dépendances
- git (obligatoire)
- bash 4.0+ (obligatoire)
- curl (optionnel)

## Tests
- Tests d'installation
  - Installation de base
  - Préservation des règles
  - Options --force et --no-backup
  - Gestion des erreurs
- Tests de fonctionnalités
  - Vérification des règles
  - Validation des options

## Environnement de développement
- OS supportés : Linux, macOS
- Outils requis : git, bash 4.0+

## Bonnes pratiques
- Utiliser git clone pour l'installation
- Préserver les règles personnalisées
- Gérer les erreurs de manière robuste
- Nettoyer les fichiers temporaires
- Documenter les changements

## Pile Technologique
- **Langages**: Bash
- **Outils**:
  - git: Pour le clonage du dépôt
  - curl: Pour l'installation via curl
  - GitHub: Pour l'hébergement et la distribution
- **Environnement**: Unix/Linux (WSL/Ubuntu pour Windows)

## Versions
- Version actuelle: 1.0.0
- Format de version: Semantic Versioning (MAJOR.MINOR.PATCH)

## Notes Techniques
- Git est utilisé pour garantir l'intégrité des fichiers
- La vérification de checksum a été supprimée car Git garantit l'intégrité
- Le déplacement des fichiers tient compte de la structure du dépôt Git

## Dépendances
- git: Pour le clonage du dépôt
- curl: Pour l'installation via curl
- bash: Pour l'exécution des scripts

## Environnement de Développement
- **Configuration requise**: 
  - Système Unix/Linux ou WSL
  - git installé
  - curl installé
  - Cursor IDE
- **Installation**: Via curl avec la commande `curl -fsSL URL | bash`

## Conventions de Code
- Scripts bash avec extension .sh
- Documentation en français (principal) et anglais
- Permissions d'exécution appropriées pour les scripts
- Utilisation de la branche `main` comme branche principale

## Dépendances Externes
- git: Dernière version stable - Clonage du dépôt
- curl: Dernière version stable - Installation via curl
- GitHub: Hébergement et distribution du script

## Intégrations
- GitHub: 
  - Hébergement du dépôt
  - Distribution du script d'installation via raw.githubusercontent.com
  - Configuration requise:
    - Dépôt public pour l'accès aux fichiers raw
    - Branche main comme branche par défaut
    - Permissions appropriées pour l'accès aux fichiers 