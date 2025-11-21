# Cursor Memory Bank 🧠

Un système de workflow autonome avancé pour Cursor avec gestion de tâches intelligente et système de roadmap centralisée.

## Table des Matières - Ordre de Révision

*Les fichiers sont listés du plus récent au moins récent. Le dernier fichier sera vérifié à la prochaine exécution.*

1. [Scripts](./scripts/scripts.md) - *Dernière vérification : 2025-01-20*

## Architecture du dépôt & emplacement des fichiers

Le projet Cursor Memory Bank est organisé selon une architecture modulaire permettant une installation flexible et une maintenance aisée :

```
root/
├─ .cursor/              # Configuration Cursor et règles d'agent
│  ├─ rules/            # Règles d'agent (.mdc) - comportement de l'IA
│  ├─ commands/         # Commandes personnalisées (.md)
├─ documentation/        # Guides détaillés et documentation longue
├─ install.sh           # Script d'installation automatisé
├─ tomd.py              # Utilitaire Python pour conversion markdown
└─ package.json         # Métadonnées du projet et scripts npm
```

### Structure détaillée des dossiers

- **`.cursor/commands/`** : Commandes personnalisées pour l'agent
  - *Contient* : `prompt.md`, `enqueteur.md`, `agent.md`, `architecte.md`, `janitor.md` - Commandes de transition, enquête, roadmap, supervision et maintenance
  - *Structure* : Fichiers `.md` définissant des commandes slash personnalisées
  - *Usage* : Permet aux agents de générer des prompts de transition avec `/prompt`, lancer une enquête avec `/enqueteur`, sélectionner une tâche avec `/agent`, superviser avec `/architecte`, et analyser le repository avec `/janitor`

- **`.cursor/rules/`** : Règles d'agent définissant le comportement de l'IA
  - *Contient* : `agent.mdc`, `debug.mdc`, `start.mdc`, `README.mdc` (exemples)
  - *Structure* : Fichiers `.mdc` avec métadonnées YAML et instructions markdown
  - *Usage* : Définissent comment l'agent doit réagir dans différents contextes. Note : la procédure d'enquête auparavant répartie dans `.cursor/rules/enqueteur/` a été consolidée en une commande unique `.cursor/commands/enqueteur.md`.
- *Règle critique* : `README.mdc` impose un README atomique, autosuffisant et mis à jour à chaque session (aucune référence à d'anciennes versions).
- *Nouveau* : `communication.mdc` — règle de communication imposant clarté, emojis pertinents, sections structurées, usage réfléchi des tableaux et des synthèses 100 % textuelles (sans code).

- **`documentation/`** : Guides approfondis et procédures détaillées
  - *Contient* : Documentation technique, guides d'utilisation, architecture détaillée
  - *Structure* : Fichiers markdown organisés par domaine fonctionnel
  - *Usage* : Référence pour les utilisateurs avancés et la maintenance

- **`install.sh`** : Script d'installation unifié (mode unique)
  - *Rôle* : Installation automatisée avec détection de branche et fallback curl
  - *Fonctionnalités* : Mode unique — règles, commandes et configuration `.gitignore`
  - *Usage* : `bash install.sh`

- **`tomd.py`** : Utilitaire Python pour la conversion et le traitement markdown
  - *Rôle* : Conversion de formats, traitement de fichiers markdown
  - *Usage* : Outil de ligne de commande pour les tâches de formatage

## Installation 🚀

A single installer is provided: `install.sh`. It installs agent rules, custom commands, and configures `.gitignore`. Clone is preferred; a curl fallback may be used when necessary.

Recommended (download then run — reviewable):
```bash
curl -fsSL https://raw.githubusercontent.com/hjamet/cursor-memory-bank/master/install.sh | bash
```

Examples:
```bash
# Default installation (rules + commands)
bash install.sh

# Install to a specific directory
bash install.sh --dir /path/to/install

# Show help information
bash install.sh --help
```

Available options (summary):
- `--dir <path>` : Install to a specific directory (default: current directory)
- `--force` : Force overwrite existing files
- `--help` : Show help information
- `--version` : Show version information

### Required files and fail-fast policy

Certain files are considered required by the installer and a missing download will stop the installation immediately (fail-fast). This ensures the installer does not continue in a partially-installed state.

- **Required files (examples)**:
  - `.cursor/rules/agent.mdc` (agent behavior rules)
  - `.cursor/commands/prompt.md` (agent handoff command)

- **Diagnosis**: On failure the installer will print diagnostic info including HTTP status codes and curl exit codes (e.g. `http_code=404 curl_exit_code=22`). Re-run the installer after fixing network or URL issues.

### Comportement des téléchargements

Le script utilise une fonction interne `download_file(url, dest, [required])` pour récupérer des fichiers via `curl`.
- **Paramètre `required`**: si la 3ᵉ valeur passée est `required`, le fichier est **considéré critique**; toute erreur HTTP (404, 403, 5xx) ou un fichier vide provoquera une erreur fatale et interrompra l'installation (fail‑fast).
- **Fichiers optionnels**: si le paramètre n'est pas fourni, les erreurs réseau/HTTP **ne feront pas échouer** l'installation. Le script affichera un **warning** et continuera (retourne 0) pour préserver la compatibilité avec `set -e` et éviter des régressions quand des ressources facultatives manquent.
- **Diagnostics**: sur erreurs ou comportements inattendus, le script affiche `http_code` et `curl_exit_code` (ex. `http_code=404 curl_exit_code=22`) pour faciliter le diagnostic réseau/URL.

Exemples d'utilisation dans le script:

```bash
# Fichier critique — installation échoue si absent
download_file "$RAW_URL_BASE/.cursor/commands/prompt.md" "$target_dir/.cursor/commands/prompt.md" "required"
```


### Method 2: Using git clone

If you prefer, you can also install Cursor Memory Bank by cloning the repository:

```bash
git clone https://github.com/hjamet/cursor-memory-bank.git
cd cursor-memory-bank
bash install.sh [options]
```

## Installation Mode 🎯

The installer now provides a single mode: it installs essential rules (`agent.mdc`, `debug.mdc`), custom commands, and updates `.gitignore`. Existing custom rules are preserved. No Streamlit UI or ML artifacts are installed.

## What is Cursor Memory Bank? 🤔

Cursor Memory Bank is an advanced autonomous workflow system that revolutionizes how you work with Cursor. It provides intelligent task management, persistent memory, and automated quality assurance through a sophisticated rule-based architecture.

### Core Features ✨

#### 🧠 **Autonomous Workflow System**
- **Self-Managing**: Operates in continuous autonomous loops with intelligent decision-making
- **Quality Assurance**: Mandatory testing cycle with automatic `implementation → experience-execution` transitions
- **Safety Mechanisms**: Anti-infinite-loop protection, emergency brakes, and transition monitoring
- **Intelligent Routing**: Context-aware task routing based on complexity and requirements

#### 🚀 **Workflow Automation**
- **Automatic Testing**: Mandatory validation after every implementation
- **Smart Transitions**: Context-aware workflow step recommendations
- **Memory Persistence**: Long-term and working memory with automatic cleanup
- **Git Integration**: Automated commit messages with standardized formatting

## Custom Commands

### `/prompt` - Transition entre agents

La commande `/prompt` permet aux agents de créer un plan de transition pour passer le contexte à un nouvel agent. Le plan est automatiquement enregistré dans le repository et supprimé par le successeur.

### `/enqueteur` - Enquête méthodologique des bugs

La commande `/enqueteur` exécute la procédure d'enquête pas à pas (exploration, hypothèses, logs, exécution, analyse, validation critique, rapport) définie dans `.cursor/commands/enqueteur.md`.

### `/janitor` - Reviewer exhaustif du repository

La commande `/janitor` conduit une analyse critique exhaustive du repository pour identifier TOUS les problèmes de maintenance, incohérences, et lacunes organisationnelles.

### `/agent` - Sélection et traitement de tâche 🚀

La commande `/agent` consulte la roadmap directement dans le README, sélectionne la tâche la plus prioritaire, et engage sa réalisation en collaboration avec l'utilisateur.

### `/architecte` - Supervision stratégique 🏗️

La commande `/architecte` permet de gérer la roadmap dans le README (ajout, réorganisation, visualisation) sans modifier le code source.

## Technical Architecture 🏗️

### **Workflow Safety Systems**
- **Transition Monitoring**: Real-time tracking of workflow steps
- **Loop Detection**: Automatic identification of problematic patterns
- **Emergency Brakes**: Fail-safe mechanisms for system stability
- **Performance Metrics**: Comprehensive monitoring and reporting

### **Memory Management**
- **Working Memory**: Short-term context for active tasks
- **Long-term Memory**: Persistent storage of important decisions
- **Automatic Cleanup**: Intelligent memory optimization
- **Context Preservation**: Seamless session continuity

### **Quality Assurance**
- **Mandatory Testing**: Automatic validation after every implementation
- **Code Quality Checks**: Integrated linting and validation
- **Regression Prevention**: Systematic testing of changes
- **Performance Monitoring**: Real-time system health tracking

## Contributing 🤝

While this is primarily a personal project, contributions are welcome! The system is designed to be extensible and maintainable. Most documentation and rules are in French, but English translations and general-purpose improvements are especially appreciated.

### **Development Guidelines**
- Follow the established workflow patterns
- Test all changes through the experience-execution cycle
- Document architectural decisions in long-term memory

## License 📄

This project is open source and available for personal and educational use. Please refer to the repository for the most current license information.

## Troubleshooting 🔧

### **Windows Emoji Encoding Issues** 🐛

If you encounter `UnicodeEncodeError` when running commands with emojis on Windows:

**Problem**: Windows uses `cp1252` encoding by default, causing errors with Unicode characters and emojis.

**Solution**: Set the following environment variables for all processes:
- `PYTHONIOENCODING=utf-8`: Forces Python to use UTF-8 for I/O operations
- `PYTHONLEGACYWINDOWSSTDIO=0`: Enables UTF-8 mode on Windows
- `LC_ALL=C.UTF-8` and `LANG=C.UTF-8`: Sets locale to UTF-8

### **Workflow Issues**

If the autonomous workflow seems stuck or behaving unexpectedly:

1. **Check Safety Systems**: Look for emergency brake activation
2. **Monitor Transitions**: Verify workflow step transitions are completing
3. **Review Memory**: Check working memory for error patterns
4. **Restart Workflow**: Use `start-workflow` to reset system state

## Automatic Task Creation System 🔧

The system automatically creates refactoring tasks for oversized files (>500 lines) integrated directly into the commit workflow.

### How It Works

**Automatic Detection**: Every time you commit, the system:
1. **Scans all files** in the project with supported extensions (`.py`, `.js`, `.tex`, `.html`, `.css`, `.sh`)
2. **Detects files** exceeding 500 lines
3. **Creates refactoring tasks** automatically with appropriate priorities

### Supported File Types
- Python (`.py`)
- JavaScript (`.js`) 
- LaTeX (`.tex`)
- HTML (`.html`)
- CSS (`.css`)
- Shell scripts (`.sh`)

### Priority Assignment
- **1500+ lines**: Priority 5 (Critical)
- **1000+ lines**: Priority 5 (Critical)
- **500+ lines**: Priority 4 (High)

### Testing the System

To verify automatic task creation works:

1. Create a test file with >500 lines: `seq 600 > test_file.py`
2. Commit the changes
3. Check the commit output for "Automatic Task Creation" section
 
5. Clean up: `rm test_file.py`

### Configuration Notes

**Important**: If you see git hook configuration pointing to `.githooks`, this is obsolete and can be removed:
```bash
git config --unset core.hooksPath
```

The functionality is now **100% integrated** into the commit workflow - no separate hooks needed.

### **Windows: git diff encoding fix**

If `python tomd.py` raises a `UnicodeDecodeError` when writing the git diff (Windows CP1252 decoding issue), update `tomd.py` to write the raw `git diff` bytes to the `diff` file. The script now writes the diff as binary to preserve arbitrary bytes and avoid platform-specific decoding errors. No user action is required for the fix bundled in the repository.

# Roadmap

| Tâche | Objectif | État | Dépendances |
|-------|----------|------|-------------|
| **Nettoyer dossier agents** | Supprimer le dossier obsolète `.cursor/agents/` et son contenu (roadmap.yaml, fichiers tâches) maintenant que le système est migré vers le README. Vérifier qu'aucun fichier important n'y est resté avant suppression. | 📅 À faire | - |
