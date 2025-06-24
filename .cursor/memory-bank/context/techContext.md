# Technical Context

## Project Overview
This project is an autonomous AI agent operating within the Cursor IDE. Its primary goal is to manage software development tasks, interact with the user via a Streamlit interface, and maintain a persistent memory of its operations.

## Core Technologies
- **AI Agent**: Custom-built agent running within Cursor.
- **Workflow Engine**: A rule-based system (`.mdc` files) that dictates the agent's behavior.
- **Memory System**: A custom "Memory Bank" to persist state, tasks, and knowledge.
- **Tooling**: A suite of custom Model Context Protocol (MCP) servers for actions like file system operations, git commits, and task management.
- **Frontend**: A Streamlit application for user interaction, task monitoring, and communication.
- **Development**: Node.js (for MCP servers), Python (for Streamlit).

## Streamlit Application
The Streamlit application serves as the primary user interface for the agent.

- **UI Framework**: Streamlit
- **Application Structure**: A modular, component-based architecture.
    - `app.py`: Main entry point. It handles user request submission and the task review process. It uses a session-state controlled `st.radio` to manage navigation between "Add Request" and "Review" views.
    - `components/sidebar.py`: A centralized sidebar component displayed on all pages. It features an auto-refresh mechanism, a "Work Queue" counter (remaining tasks + unprocessed requests), and an estimated project completion time.
    - `components/task_utils.py`: Helper functions for task and user brief manipulation.
- **Pages**:
    - `pages/task_status.py`: A dashboard to view and track the status of all tasks.
    - `pages/memory.py`: An interface to inspect the agent's recent memories.
- **Data Models**:
    - `tasks.json`: Stores all development tasks. Each task includes a `status_history` array to accurately track time spent.
    - `userbrief.json`: Stores all user requests, decoupled from the task management system until they are explicitly converted into tasks.

## MemoryBankMCP Server (`mcp_MemoryBankMCP_*`)
This is the core server for managing the agent's state and workflow.
- **`read_userbrief` / `update_userbrief`**: Manages the lifecycle of user requests in `userbrief.json`.
- **`create_task` / `update_task` / `get_all_tasks` / `get_next_tasks`**: Full CRUD and queuing operations for tasks in `tasks.json`.
- **`commit`**: Performs standardized Git commits.
- **`remember`**: Records the agent's state (past, present, future) to its memory.
- **`next_rule`**: Fetches instructions for the next step in the workflow.

## ToolsMCP Server (`mcp_ToolsMCP_*`)
This server provides the agent with tools to interact with the system environment.
- **`execute_command` / `get_terminal_status` / `get_terminal_output` / `stop_terminal_command`**: A complete suite for asynchronous terminal command execution.
- **`consult_image` / `take_webpage_screenshot`**: Tools for processing and capturing visual information.

## Known Issues & Workarounds
- **`edit_file` Instability**: The `edit_file` tool can be unreliable. Prefer more specific tools like `mcp_ToolsMCP_regex_edit` or make very small, targeted edits.
- **MCP Tool Discovery**: New tools added to a running MCP server may not be immediately available in Cursor. A full restart of the IDE is required to clear the tool cache.
- **MCP Server Logging**: Any non-JSON output (like `console.log`) from an MCP server will break the communication with the Cursor client. All debug logs must be removed from production code.
- **MDC File Editing**: To reliably edit `.mdc` rule files and have the changes tracked by Git, it's sometimes necessary to rename them to `.md`, make the edits, and then rename them back to `.mdc`.

## Technology Stack

### Backend
- **Runtime**: Node.js 18+
- **Language**: TypeScript 5.0+
- **Framework**: Express.js
- **Database**: PostgreSQL 15+
- **ORM**: Prisma
- **Authentication**: JWT (jsonwebtoken)
- **Password Hashing**: bcrypt
- **Validation**: Joi or Zod

### Frontend
- **Framework**: React 18+
- **Language**: TypeScript
- **State Management**: Redux Toolkit
- **Styling**: Tailwind CSS
- **Build Tool**: Vite
- **Testing**: Jest + React Testing Library

### Development Tools
- **Linting**: ESLint
- **Formatting**: Prettier
- **Version Control**: Git
- **Package Manager**: npm
- **API Documentation**: Swagger/OpenAPI

## Architecture Patterns

### Backend Architecture
- **Pattern**: Layered Architecture (Controller → Service → Repository)
- **Error Handling**: Centralized error middleware
- **Logging**: Winston or similar structured logging
- **Rate Limiting**: express-rate-limit
- **CORS**: Configured for frontend domain

### Database Design
- **Schema**: Normalized relational design
- **Migrations**: Prisma migrations
- **Indexing**: Proper indexing on frequently queried fields
- **Constraints**: Foreign key constraints and validation

### Security Considerations
- **Authentication**: JWT with refresh tokens
- **Authorization**: Role-based access control (RBAC)
- **Input Validation**: Validate all inputs
- **SQL Injection**: Use parameterized queries (Prisma ORM)
- **XSS Protection**: Sanitize outputs
- **HTTPS**: Enforce HTTPS in production

## Development Standards

### Code Quality
- **TypeScript**: Strict mode enabled
- **ESLint**: Airbnb configuration with TypeScript
- **Prettier**: Consistent code formatting
- **Husky**: Pre-commit hooks for linting
- **Testing**: Minimum 80% code coverage

### API Design
- **REST**: RESTful API design principles
- **Versioning**: API versioning strategy (v1, v2, etc.)
- **Status Codes**: Proper HTTP status codes
- **Error Responses**: Consistent error response format
- **Documentation**: OpenAPI/Swagger documentation

### Performance
- **Caching**: Redis for session storage and caching
- **Database**: Query optimization and indexing
- **Pagination**: Implement pagination for large datasets
- **Compression**: Gzip compression for responses

## Deployment & Infrastructure

### Environment Configuration
- **Development**: Local development with hot reload
- **Testing**: Automated testing environment
- **Staging**: Pre-production environment
- **Production**: Production environment with monitoring

### CI/CD Pipeline
- **Source Control**: Git with feature branch workflow
- **Testing**: Automated tests on every commit
- **Deployment**: Automated deployment to staging/production
- **Monitoring**: Application and infrastructure monitoring

**Core Technologies:**
- Cursor AI Agent
- Markdown (`.md`, `.mdc` for rules)
- MCP Servers (specifically `mcp_memory_*` tools for knowledge graph/memory, `mcp_ToolsMCP_*` for terminal operations, `mcp_MemoryBankMCP_*` for userbrief management and commit operations)
- Node.js with ESM (for MCP servers)
- Access to `mcp_debug_*` tools for interactive debugging.
- Underlying Cursor infrastructure for rule execution and tool calls.
- For MCP commit server: `@modelcontextprotocol/sdk`, `zod`, `puppeteer`, `sharp`
- For Memory Bank MCP server: `@modelcontextprotocol/sdk`, `express`, `cors`, `express-rate-limit`, `zod`

**Dependencies:**
- Access to `mcp_memory_create_entities`, `mcp_memory_create_relations`, `mcp_memory_add_observations`, `mcp_memory_search_nodes`, etc. (Used for agent's knowledge graph memory within workflow rules)
- Access to `mcp_context7_*` tools for library documentation lookup.
- Access to `mcp_debug_*` tools for interactive debugging.
- Access to `mcp_MemoryBankMCP_*` tools for userbrief management and commit operations
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
1. **ToolsMCP Server** : Serveur pour les opérations de terminal et manipulation d'images/captures d'écran
2. **MemoryBankMCP Server** : Serveur consolidé pour la gestion des tâches, userbrief et opérations de commit

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
- **Utilisation systématique des outils MCP (`mcp_ToolsMCP_*` pour terminal, `mcp_MemoryBankMCP_*` pour tâches/commits) pour l'exécution de commandes externes dans les règles**
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

### ToolsMCP Server (`mcp_ToolsMCP_*`)
Le serveur ToolsMCP (nommé `ToolsMCP` dans son code) fournit les outils suivants :
- `execute_command`: Pour exécuter des commandes shell de manière asynchrone.
- `get_terminal_status`: Pour vérifier l'état des commandes en cours.
- `get_terminal_output`: Pour récupérer la sortie d'une commande.
- `stop_terminal_command`: Pour arrêter une commande en cours.
- `consult_image`: Pour lire un fichier image et le retourner en base64 (utilise `sharp` pour redimensionnement/compression).
- `take_webpage_screenshot`: Pour prendre une capture d'écran d'une page web et la retourner en base64 (utilise `puppeteer` pour la capture et `sharp` pour redimensionnement/compression).

### MemoryBankMCP Server (`mcp_MemoryBankMCP_*`)
Le serveur MemoryBankMCP (nommé `MemoryBankMCP` dans sa configuration) fournit les outils suivants :
- `read-userbrief`: Reads the `userbrief.json` file and returns the current request ('in_progress' or 'new'), plus a configurable number of archived entries. (optional, default: 3)
- `update-userbrief`: Updates a request's status in `userbrief.json` using its unique ID. Supports status changes and adding comments to a request's history. Action is required. ID is optional (targets active request if omitted). Comment is optional.
- `create_task`: Creates a new task. Requires title, short_description, and detailed_description. Other fields like dependencies, status, etc., are optional.
- `update-task`: Updates an existing task by its ID. Requires task_id. All other fields are optional.
- `get_next_tasks`: Returns available tasks (whose dependencies are met). All parameters are optional filters.
- `get_all_tasks`: Returns all tasks, with optional filters.
- `commit`: Performs a standardized Git commit. Requires emoji, type, title, and description.
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
- L'outil `mcp_ToolsMCP_execute_command` rencontrait des difficultés à capturer `stdout`/`stderr` pour `tests/test_mcp_async_terminal.js`. L'ajout de logging fichier dans le script de test semble avoir résolu le problème (test passe désormais).
- Le retour d'images volumineuses en base64 (`type: \"image\"`) via MCP peut entraîner des erreurs `Maximum call stack size exceeded` ou des interruptions. La solution consiste à traiter l'image côté serveur (ex: avec `sharp`) pour réduire sa taille (e.g., redimensionner à 1024px de large, compresser en JPEG) avant l'encodage base64.

### Known Issues/Solutions
- **`@modelcontextprotocol/sdk` Error**: The SDK can throw `ERR_PACKAGE_PATH_NOT_EXPORTED` on certain imports. The correct import for the client seems to be `import { McpClient } from '@modelcontextprotocol/sdk/client/mcp.js';`, but this can also fail. There appears to be an underlying issue with the SDK's package exports that makes imports unstable.
- **`edit_file` Tool Instability**: The `edit_file` tool is currently highly unstable, especially for `.js` and `.md` files. It often fails to apply changes, applies them partially, or makes destructive, unintended changes. Using more direct tools like `mcp_ToolsMCP_regex_edit` or breaking down changes into very small, targeted edits may be a necessary workaround.

## Architecture des Serveurs MCP
- **Format de Registration**: Tous les outils utilisent le format 3-paramètres `server.tool(name, schema, handler)` avec objets Zod inline
- **Validation**: Validation des paramètres avec Zod schemas et descriptions intégrées
- **Gestion d'Erreur**: Gestion d'erreur complète avec codes de retour appropriés
- **Modularité**: Architecture modulaire avec séparation des responsabilités
- **Status**: ✅ Les deux serveurs sont entièrement fonctionnels et validés