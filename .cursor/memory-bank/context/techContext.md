# Technical Context

**Core Technologies:**
- Cursor AI Agent
- Markdown (`.md`, `.mdc` for rules)
- MCP Servers (specifically `mcp_memory_*` tools for knowledge graph/memory)
- Node.js with ESM (for MCP commit server)

**Dependencies:**
- Access to `mcp_memory_create_entities`, `mcp_memory_create_relations`, `mcp_memory_add_observations`, `mcp_memory_search_nodes`, etc. (Used for agent's knowledge graph memory within workflow rules)
- Access to `mcp_context7_*` tools for library documentation lookup.
- Access to `mcp_debug_*` tools for interactive debugging.
- Underlying Cursor infrastructure for rule execution and tool calls.
- For MCP commit server: `@modelcontextprotocol/sdk`, `zod`

## Pile Technologique
- **Langages**: Bash, Markdown
- **Frameworks**: N/A
- **Bibliothèques**: N/A
- **Outils**: Cursor, Git, Curl

## Architecture
Le projet est organisé en une structure de fichiers cohérente avec des règles spécifiques pour Cursor et un script d'installation bash.

Le projet comprend aussi un serveur MCP Commit qui doit être correctement installé dans le répertoire d'installation de Cursor pour fonctionner. Ce serveur se connecte via le protocole StdioTransport et permet d'effectuer des commits Git standardisés depuis l'interface de Cursor.

## Environnement de Développement
- **Configuration requise**: Cursor, Bash, Git (optionnel), Curl (recommandé)
- **Installation**: Via le script install.sh avec diverses options (--dir, --backup, --force)

## Conventions de Code
- Utilisation de fichiers .mdc pour les règles de Cursor
- Structure spécifique pour les fichiers de mémoire dans .cursor/memory-bank/
- Documentation en français
- Gestion explicite des protocoles file:// pour les téléchargements
- Traitement amélioré des codes HTTP non standards
- **Utilisation systématique des outils MCP (`mcp_MyMCP_*`) pour l'exécution de commandes externes dans les règles**

## Dépendances Externes
- Cursor: Dernière version - Environnement d'exécution principal
- Git: Dernière version - Pour l'installation par clonage (optionnel) et pour les fonctionnalités de commit
- Curl: Dernière version - Pour l'installation sans Git (recommandé)
- API GitHub: Pour récupérer la liste des fichiers et la date du dernier commit
- Node.js: Pour exécuter le serveur MCP commit (v22.14.0 ou supérieur recommandé)

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
- Installation des dépendances du serveur MCP commit si Node.js et npm sont disponibles
- Fusion du fichier mcp.json pour configurer le serveur MCP commit 
- **jq (Optionnel mais recommandé)**: `jq` est nécessaire pour modifier le `mcp.json` afin d'utiliser un chemin absolu pour le serveur MCP commit et pour fusionner la configuration avec un `mcp.json` existant. Si `jq` n'est pas trouvé, le script utilise un chemin relatif et ne fusionne pas, ce qui peut entraîner des problèmes si le script d'installation n'est pas exécuté depuis le répertoire racine de Cursor. 

## Notes sur les Serveurs MCP
- Le serveur MCP Commit (`mcp_MyMCP_*`) est sensible à la configuration `cwd` (Current Working Directory) lors de l'exécution de commandes via `spawn`, en particulier avec `shell: false`. Assurez-vous que `projectRoot` est correctement calculé.
- Toute sortie `console.log` ou `console.warn` non JSON du serveur MCP peut interrompre la communication avec le client Cursor, entraînant des erreurs "Unexpected token". Les logs de débogage doivent être commentés ou supprimés en production.
- L'outil `mcp_MyMCP_execute_command` peut avoir des difficultés à capturer la sortie `stdout`/`stderr` des processus Python très courts avant leur achèvement. 
- **Process Tree Killing**: L'outil `mcp_MyMCP_stop_terminal_command` utilise maintenant le paquet `fkill` pour tenter de terminer l'arbre de processus entier (parent et enfants) associé à un PID donné, afin de mieux gérer les processus enfants laissés par les commandes terminées. 