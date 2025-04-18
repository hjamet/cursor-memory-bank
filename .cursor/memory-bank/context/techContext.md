# Technical Context

**Core Technologies:**
- Cursor AI Agent
- Markdown (`.md`, `.mdc` for rules)
- MCP Servers (specifically `mcp_servers_*` tools for knowledge graph/memory)

**Dependencies:**
- Access to `mcp_servers_create_entities`, `mcp_servers_create_relations`, `mcp_servers_add_observations`, `mcp_servers_search_nodes`, etc. (Used for agent's knowledge graph memory within workflow rules)
- Underlying Cursor infrastructure for rule execution and tool calls.

## Pile Technologique
- **Langages**: Bash, Markdown
- **Frameworks**: N/A
- **Bibliothèques**: N/A
- **Outils**: Cursor, Git, Curl

## Architecture
Le projet est organisé en une structure de fichiers cohérente avec des règles spécifiques pour Cursor et un script d'installation bash.

## Environnement de Développement
- **Configuration requise**: Cursor, Bash, Git (optionnel), Curl (recommandé)
- **Installation**: Via le script install.sh avec diverses options (--dir, --backup, --force)

## Conventions de Code
- Utilisation de fichiers .mdc pour les règles de Cursor
- Structure spécifique pour les fichiers de mémoire dans .cursor/memory-bank/
- Documentation en français
- Gestion explicite des protocoles file:// pour les téléchargements
- Traitement amélioré des codes HTTP non standards

## Dépendances Externes
- Cursor: Dernière version - Environnement d'exécution principal
- Git: Dernière version - Pour l'installation par clonage (optionnel)
- Curl: Dernière version - Pour l'installation sans Git (recommandé)
- API GitHub: Pour récupérer la liste des fichiers et la date du dernier commit

## Intégrations
- GitHub: Pour l'hébergement du dépôt, la distribution et l'API
- Cursor: Intégration avec l'éditeur Cursor pour la contextualisation

## Fonctionnalités du script d'installation
- Téléchargement direct des fichiers via l'API GitHub (pour curl)
- Clonage du dépôt Git (si Git est disponible et --use-curl n'est pas spécifié)
- Gestion intelligente des backups (désactivée par défaut, activable avec --backup)
- Compatibilité avec les protocoles standard et file://
- Gestion robuste des erreurs HTTP
- Récupération de la date du dernier commit pour indiquer la fraîcheur des règles
- Vérification et restauration des règles personnalisées 