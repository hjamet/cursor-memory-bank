# Contexte Technique

## Pile Technologique
- **Langages**: Bash, Markdown
- **Frameworks**: N/A
- **Bibliothèques**: N/A
- **Outils**: Cursor, Git, Curl

## Architecture
Le projet est organisé en une structure de fichiers cohérente avec des règles spécifiques pour Cursor et un script d'installation bash.

## Environnement de Développement
- **Configuration requise**: Cursor, Bash, Git (optionnel), Curl (optionnel)
- **Installation**: Via le script install.sh avec diverses options (--dir, --backup, --force, --use-curl)

## Conventions de Code
- Utilisation de fichiers .mdc pour les règles de Cursor
- Structure spécifique pour les fichiers de mémoire dans .cursor/memory-bank/
- Documentation en français
- Gestion explicite des protocoles file:// pour les téléchargements
- Traitement amélioré des codes HTTP non standards

## Dépendances Externes
- Cursor: Dernière version - Environnement d'exécution principal
- Git: Dernière version - Pour l'installation par clonage (optionnel)
- Curl: Dernière version - Pour l'installation sans Git (optionnel)

## Intégrations
- GitHub: Pour l'hébergement du dépôt et la distribution
- Cursor: Intégration avec l'éditeur Cursor pour la contextualisation

## Fonctionnalités du script d'installation
- Téléchargement d'archives et de fichiers individuels
- Gestion intelligente des backups (désactivée par défaut, activable avec --backup)
- Compatibilité avec les protocoles standard et file://
- Gestion robuste des erreurs HTTP
- Vérification et restauration des règles personnalisées 