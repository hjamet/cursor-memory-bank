# Technical Context

**Core Technologies:**
- Cursor AI Agent
- Markdown (`.md`, `.mdc` for rules)
- MCP Servers (specifically `mcp_memory_*` tools for knowledge graph/memory, `mcp_MyMCP_*` for terminal operations, `mcp_MemoryBank_*` for userbrief management and commit operations)
- Node.js with ESM (for MCP servers)
- Access to `mcp_debug_*` tools for interactive debugging.
- Underlying Cursor infrastructure for rule execution and tool calls.
- For MCP commit server: `@modelcontextprotocol/sdk`, `zod`, `puppeteer`, `sharp`
- For Memory Bank MCP server: `@modelcontextprotocol/sdk`, `express`, `cors`, `express-rate-limit`, `zod`

**Dependencies:**
- Access to `mcp_memory_create_entities`, `mcp_memory_create_relations`, `mcp_memory_add_observations`, `mcp_memory_search_nodes`, etc. (Used for agent's knowledge graph memory within workflow rules)
- Access to `mcp_context7_*` tools for library documentation lookup.
- Access to `mcp_debug_*` tools for interactive debugging.
- Access to `mcp_MemoryBank_*` tools for userbrief management and commit operations
- Underlying Cursor infrastructure for rule execution and tool calls.
- For MCP commit server: `@modelcontextprotocol/sdk`, `zod`, `puppeteer`, `sharp`
- For Memory Bank MCP server: `@modelcontextprotocol/sdk`, `express`, `cors`, `express-rate-limit`, `zod`

## Pile Technologique
- **Langages**: Bash, Markdown
- **Frameworks**: N/A
- **Bibliothèques**: N/A
- **Outils**: Cursor, Git, Curl

## Architecture
Le projet est organisé en une structure de fichiers cohérente avec des règles spécifiques pour Cursor et un script d'installation bash.

Le projet comprend deux serveurs MCP principaux :
1. **MyMCP Server** : Serveur pour les opérations de terminal et manipulation d'images/captures d'écran
2. **MemoryBank MCP Server** : Serveur consolidé pour la gestion des tâches, userbrief et opérations de commit

Ces serveurs se connectent via le protocole StdioTransport et doivent être correctement installés dans le répertoire d'installation de Cursor pour fonctionner.

Un hook pre-commit est également fourni dans `.githooks/pre-commit` et installé par `install.sh` pour vérifier la longueur des fichiers de code avant le commit.

## Environnement de Développement
- **Configuration requise**: Cursor, Bash, Git (optionnel), Curl (recommandé)
- **Installation**: Via le script `install.sh` avec diverses options (`--dir`, `--backup`, `--force`, `--use-curl`)
- **Post-installation Git**: Le script `install.sh` tente désormais de configurer automatiquement `core.hooksPath` si l'installation se fait dans un dépôt Git.

## Conventions de Code
- Utilisation de fichiers .mdc pour les règles de Cursor
- Structure spécifique pour les fichiers de mémoire dans .cursor/memory-bank/
- Documentation en français
- Gestion explicite des protocoles file:// pour les téléchargements
- Traitement amélioré des codes HTTP non standards
- **Utilisation systématique des outils MCP (`mcp_MyMCP_*` pour terminal, `mcp_MemoryBank_*` pour tâches/commits) pour l'exécution de commandes externes dans les règles**
- **WORKAROUND:** Pour modifier de manière fiable les fichiers `.mdc` (règles), renommer temporairement en `.md`, éditer, puis renommer en `.mdc` pour assurer la détection par Git.
- **Pre-commit Hook**: Warns (but does not block) if code files (.py, .js, .ts, .java, .go, .rb, .php, .sh) exceed 500 lines.

## Dépendances Externes
- Cursor: Dernière version - Environnement d'exécution principal
- Git: Dernière version - Pour l'installation par clonage (optionnel) et pour les fonctionnalités de commit
- Curl: Dernière version - Pour l'installation sans Git (recommandé)
- API GitHub: Pour récupérer la liste des fichiers et la date du dernier commit
- Node.js: Pour exécuter les serveurs MCP (v22.14.0 ou supérieur recommandé)

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
- Installation du hook pre-commit dans `.githooks/` et tentative de configuration automatique de `core.hooksPath`.
- Installation des dépendances des serveurs MCP si Node.js et npm sont disponibles
- Fusion du fichier mcp.json pour configurer les serveurs MCP 
- **jq (Optionnel mais recommandé)**: `jq` est nécessaire pour modifier le `mcp.json` afin d'utiliser un chemin absolu pour les serveurs MCP et pour fusionner la configuration avec un `mcp.json` existant. Si `jq` n'est pas trouvé, le script utilise un chemin relatif et ne fusionne pas, ce qui peut entraîner des problèmes si le script d'installation n'est pas exécuté depuis le répertoire racine de Cursor. 

## Notes sur les Serveurs MCP

### MyMCP Server (`mcp_MyMCP_*`)
Le serveur MyMCP (nommé `InternalAsyncTerminal` dans son code) fournit les outils suivants :
- `execute_command`: Pour exécuter des commandes shell de manière asynchrone.
- `get_terminal_status`: Pour vérifier l'état des commandes en cours.
- `get_terminal_output`: Pour récupérer la sortie d'une commande.
- `stop_terminal_command`: Pour arrêter une commande en cours.
- `consult_image`: Pour lire un fichier image et le retourner en base64 (utilise `sharp` pour redimensionnement/compression).
- `take_webpage_screenshot`: Pour prendre une capture d'écran d'une page web et la retourner en base64 (utilise `puppeteer` pour la capture et `sharp` pour redimensionnement/compression).

### MemoryBank MCP Server (`mcp_MemoryBank_*`)
Le serveur MemoryBank MCP (nommé `MemoryBank` dans sa configuration) fournit les outils suivants :
- `read-userbrief`: Reads the `userbrief.json` file and returns the current request ('in_progress' or 'new'), plus a configurable number of archived entries. (optional, default: 3)
- `update-userbrief`: Updates a request's status in `userbrief.json` using its unique ID. Supports status changes and adding comments to a request's history. Action is required. ID is optional (targets active request if omitted). Comment is optional.
- `create_task`: Creates a new task. Requires title, short_description, and detailed_description. Other fields like dependencies, status, etc., are optional.
- `update-task`: Updates an existing task by its ID. Requires task_id. All other fields are optional.
- `get_next_tasks`: Returns available tasks (whose dependencies are met). All parameters are optional filters.
- `get_all_tasks`: Returns all tasks, with optional filters.
- `commit`: Performs a standardized Git commit. Requires emoji, type, title, and description.
- `read_memory`: Reads the full content of a specified context file (activeContext, projectBrief, techContext). Requires context_file.
- `edit_memory`: Completely replaces the content of a specified context file. Requires context_file and content.
- `remember`: Records a memory of the agent's state (past, present, future). Replaces `activeContext.md`.
- `next_rule`: Fetches the instructions for the next rule to be executed.

## Problèmes Connus et Solutions MCP

### Client Discovery Issues
- **Problème**: Les nouveaux outils ajoutés aux serveurs MCP existants peuvent ne pas apparaître dans l'interface Cursor
- **Cause**: Cursor cache la liste des outils pour les performances et ne rafraîchit pas automatiquement le cache
- **Solution**: Redémarrer complètement l'application Cursor pour forcer le rafraîchissement du cache
- **Prévention**: Ajouter les nouveaux outils avant le déploiement initial du serveur quand possible
- **Documentation**: Guide de dépannage complet disponible dans `results/mcp_client_discovery_issue_resolution_20250106/`

### General MCP Issues
- Sensibilité à la configuration `cwd` (Current Working Directory) lors de l'exécution de commandes via `spawn`, en particulier avec `shell: false`. CWD is auto-detected based on server startup args (`--cwd`), `CURSOR_WORKSPACE_ROOT` env var, or the server process's CWD.
- Toute sortie `console.log` ou `console.warn` non JSON du serveur MCP peut interrompre la communication avec le client Cursor, entraînant des erreurs "Unexpected token". Les logs de débogage doivent être commentés ou supprimés en production.
- L'outil `mcp_MyMCP_execute_command` rencontrait des difficultés à capturer `stdout`/`stderr` pour `tests/test_mcp_async_terminal.js`. L'ajout de logging fichier dans le script de test semble avoir résolu le problème (test passe désormais).
- Le retour d'images volumineuses en base64 (`type: \"image\"`) via MCP peut entraîner des erreurs `Maximum call stack size exceeded` ou des interruptions. La solution consiste à traiter l'image côté serveur (ex: avec `sharp`) pour réduire sa taille (e.g., redimensionner à 1024px de large, compresser en JPEG) avant l'encodage base64.

## Architecture des Serveurs MCP
- **Format de Registration**: Tous les outils utilisent le format 3-paramètres `server.tool(name, schema, handler)` avec objets Zod inline
- **Validation**: Validation des paramètres avec Zod schemas et descriptions intégrées
- **Gestion d'Erreur**: Gestion d'erreur complète avec codes de retour appropriés
- **Modularité**: Architecture modulaire avec séparation des responsabilités
- **Status**: ✅ Les deux serveurs sont entièrement fonctionnels et validés