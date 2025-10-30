# Cursor Memory Bank 🧠

Un système de workflow autonome avancé pour Cursor avec gestion de tâches intelligente, système de roadmap centralisée et interface utilisateur Streamlit.

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
│  └─ agents/           # Système de roadmap centralisée
│     ├─ roadmap.yaml   # Roadmap centralisée avec toutes les tâches
│     └─ *.md            # Fichiers de tâches et rapports
├─ documentation/        # Guides détaillés et documentation longue
├─ install.sh           # Script d'installation automatisé
├─ tomd.py              # Utilitaire Python pour conversion markdown
└─ package.json         # Métadonnées du projet et scripts npm
```

### Structure détaillée des dossiers

- **`.cursor/commands/`** : Commandes personnalisées pour l'agent
  - *Contient* : `prompt.md`, `enqueteur.md`, `agent.md`, `task.md`, `janitor.md` - Commandes de transition, enquête, roadmap et maintenance
  - *Structure* : Fichiers `.md` définissant des commandes slash personnalisées
  - *Usage* : Permet aux agents de générer des prompts de transition avec `/prompt`, lancer une enquête avec `/enqueteur`, sélectionner une tâche avec `/agent`, ajouter une tâche avec `/task`, et analyser le repository avec `/janitor`

- **`.cursor/agents/`** : Système de roadmap centralisée pour coordination multi-agents
  - *Contient* : `roadmap.yaml` (roadmap centralisée), fichiers de tâches (`{titre-kebab-case}.md`), fichiers de résultats (`rapport-{titre-kebab-case}.md`)
  - *Structure* : Fichier YAML pour la roadmap, fichiers markdown pour les tâches et rapports
  - *Usage* : Permet à plusieurs agents Cursor de travailler en parallèle, chaque agent peut consulter la roadmap, sélectionner une tâche, et consulter les résultats des autres agents
  
- **`.cursor/rules/`** : Règles d'agent définissant le comportement de l'IA
  - *Contient* : `agent.mdc`, `debug.mdc`, `start.mdc`, `README.mdc` (exemples)
  - *Structure* : Fichiers `.mdc` avec métadonnées YAML et instructions markdown
  - *Usage* : Définissent comment l'agent doit réagir dans différents contextes. Note : la procédure d'enquête auparavant répartie dans `.cursor/rules/enqueteur/` a été consolidée en une commande unique `.cursor/commands/enqueteur.md`.

- **`documentation/`** : Guides approfondis et procédures détaillées
  - *Contient* : Documentation technique, guides d'utilisation, architecture détaillée
  - *Structure* : Fichiers markdown organisés par domaine fonctionnel
  - *Usage* : Référence pour les utilisateurs avancés et la maintenance

- **`install.sh`** : Script d'installation unifié avec stratégie de téléchargement intelligente
  - *Rôle* : Installation automatisée avec détection de branche et fallback curl
  - *Fonctionnalités* : Installation basique vs complète
  - *Usage* : `bash install.sh` ou `bash install.sh --full-install`

- **`tomd.py`** : Utilitaire Python pour la conversion et le traitement markdown
  - *Rôle* : Conversion de formats, traitement de fichiers markdown
  - *Usage* : Outil de ligne de commande pour les tâches de formatage

## Installation 🚀

A single, robust installer is provided: `install.sh`. It now uses a unified strategy: **prefer `git clone` when available, then verify all required rule files and automatically fall back to raw downloads** when files are missing in the clone. The installer also detects the repository default branch via the GitHub API (fallback: `master`) to avoid raw URL 404s.

Recommended (download then run — reviewable):
```bash
curl -fsSL https://raw.githubusercontent.com/hjamet/cursor-memory-bank/master/install.sh | bash
```

Quick one-liners (the script auto-detects the default branch; use `--use-curl` to force curl-only mode):

```bash
# Basic installation (rules only - fast)
curl -fsSL https://raw.githubusercontent.com/hjamet/cursor-memory-bank/$(curl -s https://api.github.com/repos/hjamet/cursor-memory-bank | grep -o '"default_branch": *"[^"]*"' | sed 's/.*: *"\(.*\)"/\1/' || echo master)/install.sh | tr -d '\r' | bash -s --

# Full installation (all components - Streamlit UI, ML model)
curl -fsSL https://raw.githubusercontent.com/hjamet/cursor-memory-bank/$(curl -s https://api.github.com/repos/hjamet/cursor-memory-bank | grep -o '"default_branch": *"[^"]*"' | sed 's/.*: *"\(.*\)"/\1/' || echo master)/install.sh | tr -d '\r' | bash -s -- --full-install
```

Note for MINGW64/Git Bash users on Windows: If you encounter `: command not found` errors during piping, strip CR characters with `tr -d '\r'` as shown above.

Available options (summary):
- `--dir <path>` : Install to a specific directory (default: current directory)
- `--force` : Force overwrite existing files
- `--use-curl` : Force curl-only downloads instead of `git clone` (useful when git is unavailable)
- `--full-install` : Install all components (Streamlit UI, ML model, workflow system)
- `--help` : Show help information
- `--version` : Show version information

Important: the installer now installs rule files more flexibly. By default it will attempt to download and install **all files** under `.cursor/rules/` from the repository into the target, except for files marked as "full-only" which are only deployed when using `--full-install`.

- Example: `.cursor/rules/agent.mdc` is provided in this repository and will be installed by default.
- Full-only example: `.cursor/rules/README.mdc` (installed only with `--full-install`).
- Critical rules that cause installation to fail if missing: `.cursor/rules/maitre-d-oeuvre.mdc`, `.cursor/rules/ouvrier.mdc`.

Note: repository-local files such as `.cursor/rules/mcp.mdc` remain in-repo and are NOT distributed by the installer.

Examples:
```bash
# Basic installation (rules only - fast)
bash install.sh

# Full installation with all components (Streamlit UI, ML model)
bash install.sh --full-install

# Install to a specific directory with all components
bash install.sh --dir /path/to/install --full-install

# Force curl-only (no git)
bash install.sh --use-curl

# Show help information
bash install.sh --help
```

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

# Fichier optionnel — log warning si absent mais installation continue
download_file "$RAW_URL_BASE/.cursor/streamlit_app/app.py" "$streamlit_dir/app.py"
```


### Method 2: Using git clone

If you prefer, you can also install Cursor Memory Bank by cloning the repository:

```bash
git clone https://github.com/hjamet/cursor-memory-bank.git
cd cursor-memory-bank
bash install.sh [options]
```

## Installation Modes 🎯

Cursor Memory Bank offers two installation modes to suit different needs:

### Basic Mode (Default) - Fast Installation ⚡
- **What's included:** Essential rules, tomd.py utility, and .gitignore configuration
- **Best for:** Users who want to quickly set up Cursor with basic rules and utilities
- **Features:** Core agent rules, debug tools, start workflow, Python utility script
- **Size:** Minimal installation footprint (no npm install)
- **Speed:** Very fast (downloads only essential files via curl)
- **Command:** `bash install.sh` (default)

### Full Mode (`--full-install`) - Complete System 🚀
- **What's included:** Streamlit UI, ML model, complete workflow system
- **Best for:** Users who want the complete autonomous workflow experience
- **Features:** Task management, persistent memory, autonomous workflow, visual interface, semantic search
- **Size:** Larger installation with ML dependencies and npm packages
- **Speed:** Slower (clones repository, installs npm dependencies)
- **Command:** `bash install.sh --full-install`

### Choosing Your Mode
- **Start with Basic:** If you're new to the system or want to quickly set up Cursor with essential rules
- **Upgrade to Full:** You can always re-run with `--full-install` to add workflow system later
- **Development Work:** Full mode recommended for complex projects requiring autonomous workflow

The installation script will:
- **Basic mode (default)**: Install essential rules (`agent.mdc`, `debug.mdc`), `tomd.py` utility, and update `.gitignore`
- **Full mode (`--full-install`)**: Install complete workflow system (`start.mdc` rule included), Streamlit UI, and ML model
- Always preserve any existing custom rules
- Update only the core rules that need updating
- Preserve any unrelated files that might be in the .cursor directory
- Work even if the .cursor directory already exists
- Validate Node.js requirements and generated JSON configurations
- `.cursor/rules/mcp.mdc` is repository-local and will not be installed or distributed by the installer

## Système de Roadmap Centralisée 📋

Le système utilise maintenant une roadmap centralisée (`.cursor/agents/roadmap.yaml`) pour coordonner plusieurs agents Cursor en parallèle. Ce système simple et léger remplace les anciens serveurs MCP qui sont désormais obsolètes.

**Note historique** : L'historique git contient les anciens systèmes basés sur les serveurs MCP (ToolsMCP, MemoryBankMCP). Ces systèmes ont été remplacés par le système de roadmap centralisée qui est plus simple, plus léger et plus flexible.

### Comment ça fonctionne

- **Roadmap centralisée** : `.cursor/agents/roadmap.yaml` contient toutes les tâches à faire
- **Fichiers de tâches** : `.cursor/agents/{titre}.md` décrivent chaque tâche avec contexte, objectif et instructions
- **Commandes** : `/agent` pour sélectionner une tâche, `/task` pour en ajouter une nouvelle
- **Coordination** : Plusieurs agents peuvent travailler en parallèle en consultant la roadmap

Pour plus d'informations, consultez les commandes `/agent` et `/task` dans la section "Custom Commands" ci-dessous.

## What is Cursor Memory Bank? 🤔

Cursor Memory Bank is an advanced autonomous workflow system that revolutionizes how you work with Cursor. It provides intelligent task management, persistent memory, and automated quality assurance through a sophisticated rule-based architecture.

### Core Features ✨

#### 🧠 **Autonomous Workflow System**
- **Self-Managing**: Operates in continuous autonomous loops with intelligent decision-making
- **Quality Assurance**: Mandatory testing cycle with automatic `implementation → experience-execution` transitions
- **Safety Mechanisms**: Anti-infinite-loop protection, emergency brakes, and transition monitoring
- **Intelligent Routing**: Context-aware task routing based on complexity and requirements

#### 📋 **Advanced Task Management**
- **Hierarchical Tasks**: Support for parent-child task relationships and dependencies
- **Multi-Task Decomposition**: Intelligent breaking down of complex requests into manageable subtasks
- **Priority System**: 5-level priority system (1=lowest, 5=critical) with automatic prioritization
- **Status Tracking**: Comprehensive task lifecycle management (TODO, IN_PROGRESS, BLOCKED, REVIEW, DONE)

#### 🎨 **Modern Streamlit Interface**
- **Enhanced Notifications**: Custom toast notification system with configurable duration (5-15s)
- **Markdown Support**: Full markdown rendering with line breaks, bold, italic, code blocks
- **Visual Improvements**: Modern CSS styling with gradients, animations, and responsive design
- **Multi-Page Integration**: Consistent notification experience across all interface pages

#### 🚀 **Workflow Automation**
- **Automatic Testing**: Mandatory validation after every implementation
- **Smart Transitions**: Context-aware workflow step recommendations
- **Memory Persistence**: Long-term and working memory with automatic cleanup
- **Git Integration**: Automated commit messages with standardized formatting

### Recent Major Improvements 🆕

#### **Enhanced Notification System (v2.0)**
- **Custom Duration**: Configurable 5-15 second display time (vs 4s fixed in st.toast())
- **Markdown Support**: Full markdown rendering with safe HTML sanitization
- **Visual Progress**: Animated progress bars showing remaining time
- **Manual Control**: User-controlled dismissal and hover-pause functionality
- **Type System**: Distinct styling for info, success, warning, error, and memory notifications

#### **Workflow Architecture Overhaul**
- **Automatic Experience-Execution**: Mandatory testing after every implementation
- **Safety Systems**: Comprehensive anti-loop protection with cooldown mechanisms
- **Performance Monitoring**: Real-time workflow performance tracking
- **Simplified Task Decomposition**: Streamlined approach balancing efficiency and simplicity

#### **Interface Modernization**
- **Responsive Design**: Mobile-friendly interface with breakpoint optimization
- **Enhanced Styling**: Modern gradients, shadows, and animations
- **Improved UX**: Better contrast, larger notification areas, and intuitive navigation
- **Cross-Page Consistency**: Unified notification experience across all Streamlit pages

### Known Issues & Active Development 🚧

#### **Auto-Refresh System Status**
✅ **RESOLVED**: The auto-refresh issue has been addressed with a hybrid solution that provides both reliability and user control (as of 2025-07-21).

**Solution Implemented:**
- **Primary Mode**: Manual refresh system with prominent "🔄 Actualiser les données" button in sidebar
- **Optional Auto-Refresh**: Experimental auto-refresh for users who want to try it (5-second intervals)
- **Clean Interface**: All informational refresh indicators removed from main interface for streamlined UX
- **Smart UX**: Clear instructions and visual feedback when data is refreshed

**Technical Implementation:**
- `streamlit-autorefresh` library available as optional experimental feature
- Robust manual refresh with cache clearing and forced rerun
- Error handling and fallback for environments where auto-refresh fails
- **Interface Streamlined (July 2025)**: Removed data freshness timestamps, counters, and mini refresh buttons from main interface per user feedback

**User Impact**: **POSITIVE** - Users have reliable control over data refresh with clean, distraction-free interface
**Status**: **OPERATIONAL** - Manual refresh system with experimental auto-refresh option

The system now provides a better user experience with guaranteed refresh functionality.

## Agent Workflow Logic 🧠⚙️

The autonomous agent operates on a sophisticated, rule-based workflow designed for robustness and intelligent decision-making. The system features **automatic testing integration** with mandatory `implementation → experience-execution` transitions to ensure code quality.

### Workflow Architecture

```mermaid
graph TD
    subgraph Legend
        direction LR
        Dev[Dev Task]:::devStyle
        Exec[Execution Task]:::execStyle
        Fix[Fix Task]:::fixStyle
        Decomp[Decomposition]:::decompStyle
    end

    subgraph "Main Loop"
        direction TB
        A(Start) --> B{Get Next Task}
        B -- No Tasks --> Z[Context Update / Idle]
        B -- Task Available --> C{Evaluate Task Type}
        C -- Development Req. --> D[1. Implementation]
        C -- Execution Only --> E[2. Experience Execution]
        
        D -- Code Complete --> F[Remember]
        F --> E
        
        E -- Testing Complete --> G[Remember]
        G --> H{Test Passed?}
        H -- Yes --> I[3. Context Update / Commit]
        H -- No --> D
        
        I --> B
    end

    subgraph "Interrupts"
        direction TB
        J[New User Request] --> K[4. Task Decomposition]
        K --> D
        L[Blocked Task Detected] --> M[5. Fix]
        M --> D
    end

    subgraph "Safety Systems"
        direction TB
        N[Transition Monitor] --> O{Excessive Loops?}
        O -- Yes --> P[Emergency Brake]
        O -- No --> Q[Continue]
    end

    classDef devStyle fill:#cde4ff,stroke:#333,stroke-width:2px
    classDef execStyle fill:#d5e8d4,stroke:#333,stroke-width:2px
    classDef fixStyle fill:#f8cecc,stroke:#333,stroke-width:2px
    classDef decompStyle fill:#dae8fc,stroke:#333,stroke-width:2px

    class Dev,D devStyle
    class Exec,E execStyle
    class Fix,M fixStyle
    class Decomp,K decompStyle
```

### Key Workflow Features

#### **Mandatory Testing Cycle**
- **CRITICAL RULE**: `implementation → experience-execution` (AUTOMATIC)
- **ARCHITECTURAL INTEGRITY GUARANTEED**: Complete elimination of `implementation → implementation` violations (2025-07-23)
- Every code change is automatically tested before completion
- Prevents regressions and ensures quality
- Built-in safety mechanisms prevent infinite loops

#### **Intelligent Task Routing**
- **Development Tasks**: Full implementation → testing → commit cycle
- **Execution Tasks**: Direct routing to experience-execution for commands/scripts
- **Fix Tasks**: High-priority interrupt handling for blocked tasks
- **Decomposition**: Multi-request analysis and task creation

#### **Safety Systems**
- **Transition Limits**: Maximum 10 consecutive transitions before emergency brake
- **Cooldown Periods**: 1-minute minimum between experience-execution cycles
- **Cycle Detection**: Automatic identification of implementation → fix loops
- **Emergency Brakes**: Automatic activation on excessive transitions

### Workflow Steps Explained

1. **Implementation (`implementation`)**
   - Core development step for code changes
   - Automatic marking of tasks as IN_PROGRESS
   - Intelligent routing based on task complexity
   - **Mandatory transition** to Experience Execution

2. **Experience Execution (`experience-execution`)**
   - Automatic testing and validation
   - Manual testing for complex features
   - Quality assurance checks
   - **Exclusive responsibility** for task completion

3. **Task Decomposition (`task-decomposition`)**
   - Multi-request analysis capability
   - Intelligent task creation with dependencies
   - Priority assignment and scheduling
   - **Simplified approach** balancing efficiency and thoroughness

4. **Fix (`fix`)**
   - High-priority interrupt handling
   - Blocked task resolution
   - Error diagnosis and correction
   - **Immediate routing** to implementation

## Custom Commands

### `/prompt` - Transition entre agents

La commande `/prompt` permet aux agents de créer un plan de transition pour passer le contexte à un nouvel agent. Le plan est automatiquement enregistré dans le repository et supprimé par le successeur.

**Usage:**
- `/prompt il faudrait maintenant optimiser les performances` : Avec instructions
- `/prompt` : Sans instructions

**Format de sortie:** Plan de transition avec 4 sections (Contexte, Objectif, Fichiers Concernés, Instructions de Collaboration) + todos incomplets + todo de nettoyage

**Mécanique:**
- Le plan de transition est créé via l'outil `create_plan` et sauvegardé automatiquement dans le repository
- Si l'agent courant a des todos non terminés, ils sont inclus dans le plan de transition
- Le premier todo du plan est toujours de supprimer le fichier de plan de transition
- Le nouveau plan permet au successeur de reprendre là où le prédécesseur s'est arrêté ou de démarrer une nouvelle direction

### `/enqueteur` - Enquête méthodologique des bugs

La commande `/enqueteur` exécute la procédure d'enquête pas à pas (exploration, hypothèses, logs, exécution, analyse, validation critique, rapport) définie dans `.cursor/commands/enqueteur.md`.

**Usage:**
- `/enqueteur` : Démarre l'enquête étape par étape. L'agent doit suivre les instructions du fichier et produire le rapport final d'identification (aucune correction proposée).

**Format de sortie:** Rapport d'identification du bug avec fichier/fonction/ligne/instruction et preuves BEFORE/AFTER.

### `/janitor` - Reviewer exhaustif du repository

La commande `/janitor` conduit une analyse critique exhaustive du repository pour identifier TOUS les problèmes de maintenance, incohérences, et lacunes organisationnelles.

**Usage:**
- `/janitor` : Exploration exhaustive générale du repository (trouve au moins 1 problème)
- `/janitor scripts/` : Analyse ciblée d'un dossier spécifique

**Fonctionnalités:**
- **Cohérence structurelle** : Vérifie que la documentation (README) correspond à la structure réelle
- **Qualité de documentation** : Valide toutes les sections obligatoires du README contre réalité
- **Code legacy** : Identifie fichiers obsolètes, checkpoints anciens, logs non nettoyés
- **Organisation** : Détecte fichiers mal placés, duplications, structure incohérente
- **Qualité du code** : Imports cassés, chemins relatifs incorrects, dépendances manquantes
- **Complétude** : Variables d'environnement non documentées, commandes obsolètes

**Système de sévérité:**
- 🔴 **Critique** : Problèmes bloquants (architecture cassée, imports broken)
- 🟠 **Majeur** : Problèmes significatifs (documentation obsolète, incohérences majeures)
- 🟡 **Mineur** : Améliorations (clarté, organisation, conventions)

**Output:** Tableau complet avec 5 colonnes (Sévérité, Catégorie, Fichier/Section, Description du Problème, Action Suggérée) + Résumé + Évaluation de santé du repository

**Focus README:** Validation MANDATOIRE de toutes les sections du README contre l'état réel du repository à chaque exécution.

**Sécurité:** Jamais d'exécution automatique - identification exhaustive des problèmes uniquement

### `/agent` - Sélection et traitement de tâche depuis la roadmap centralisée 🚀

La commande `/agent` permet de lancer un agent qui consulte la roadmap centralisée, sélectionne automatiquement la tâche la plus intéressante disponible, charge tout son contexte, puis présente la tâche à l'utilisateur pour discussion collaborative avant implémentation.

**Usage:**
- `/agent` : Lance un agent qui sélectionne et traite une tâche de la roadmap

**Fonctionnalités:**
- **Sélection intelligente** : Choisit automatiquement la tâche la plus pertinente selon les dépendances, la priorité et l'ancienneté
- **Chargement de contexte** : Lit exhaustivement tous les fichiers mentionnés dans la tâche
- **Recherches** : Effectue les recherches sémantiques et web mentionnées
- **Présentation** : Présente la tâche sélectionnée avec contexte complet en français
- **Discussion collaborative** : Attend la planification avec l'utilisateur avant toute implémentation

**Système de roadmap:**
- Fichier centralisé : `.cursor/agents/roadmap.yaml`
- Fichiers de tâches : `.cursor/agents/{titre-kebab-case}.md`
- Fichiers de résultats : `.cursor/agents/rapport-{titre-kebab-case}.md`

**Critères de sélection:**
- Dépendances résolues (toutes les tâches dépendantes sont DONE)
- Priorité (5 = plus haute priorité)
- Ancienneté (tâches plus anciennes en priorité)
- Timeout (tâches IN_PROGRESS > 24h peuvent être reprises)

**Workflow:**
1. Lecture de la roadmap
2. Sélection de la tâche la plus intéressante
3. Marquage de la tâche comme IN_PROGRESS
4. Chargement du fichier de tâche et de tous les fichiers mentionnés
5. Recherches sémantiques et web
6. Présentation à l'utilisateur avec contexte complet
7. Discussion collaborative pour planification
8. Implémentation après validation

**Règle associée:** `.cursor/rules/agent.mdc` explique quand et comment créer des tâches dans la roadmap lorsque des travaux futurs sont identifiés.

### `/task` - Ajout non-bloquant de tâche à la roadmap 📝

La commande `/task` permet d'ajouter une nouvelle tâche à la roadmap centralisée **SANS INTERROMPRE** le travail en cours de l'agent. L'agent crée la tâche avec tout le contexte nécessaire, puis reprend immédiatement son travail précédent.

**Usage:**
- `/task il faudrait optimiser les performances plus tard` : Ajoute une tâche future à la roadmap

**Fonctionnalités:**
- **Création complète** : Génère le fichier de tâche avec les 4 sections obligatoires (Contexte, Objectif, Fichiers Concernés, Instructions)
- **Ajout à la roadmap** : Enregistre la tâche dans `roadmap.yaml` avec ID unique
- **Contexte préservé** : Mentionne les fichiers du travail actuel dans "Fichiers Concernés"
- **Non-bloquant** : Ne change pas le focus de l'agent, reprend le travail immédiatement après

**Principe fondamental:**
- **Interruption non-bloquante** : L'agent continue exactement là où il s'était arrêté
- **Délégation** : La tâche est créée pour être traitée par un autre agent (via `/agent`)
- **Format cohérent** : Suit exactement le même format que les autres fichiers de tâches

**Workflow:**
1. Analyser la demande de l'utilisateur
2. Générer les noms de fichiers (tâche + rapport)
3. Créer le fichier de tâche avec les 4 sections
4. Ajouter l'entrée dans `roadmap.yaml`
5. Confirmer la création (message court)
6. Reprendre immédiatement le travail précédent

**Exemple:** Pendant l'implémentation de l'authentification, l'utilisateur tape `/task optimiser les performances`. L'agent crée la tâche avec contexte, confirme, puis continue l'implémentation de l'authentification.

## Streamlit Interface Features 🎨

### **Enhanced Notification System**
- **Custom Duration**: 5-15 second configurable display time
- **Markdown Support**: Full formatting with line breaks, bold, italic
- **Visual Progress**: Animated countdown bars
- **Manual Control**: User dismissal and hover-pause
- **Type System**: Distinct styling for different notification types
- **Security**: HTML sanitization against XSS attacks

### **Modern UI Design**
- **Responsive Layout**: Mobile-friendly with breakpoint optimization
- **Modern Styling**: Gradients, shadows, and smooth animations
- **Enhanced Contrast**: Improved readability and accessibility
- **Intuitive Navigation**: Streamlined interface with clear visual hierarchy

### **Cross-Page Integration**
- **Consistent Experience**: Unified notifications across all pages
- **Session Management**: Persistent state across page navigation
- **Performance Optimized**: Efficient memory usage and cleanup

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

### **Notification Issues**

If toast notifications are not appearing or functioning correctly:

1. **Check Session State**: Verify Streamlit session state initialization
2. **Clear Cache**: Use Streamlit's cache clearing functionality
3. **Verify Integration**: Ensure notification functions are called on all pages
4. **Test Manually**: Use the enhanced notification system directly

### **Performance Issues**

If the system is running slowly or consuming excessive resources:

1. **Memory Cleanup**: Use context-update to optimize memory usage
2. **Task Optimization**: Review task dependencies and priorities
3. **Transition Monitoring**: Check for excessive workflow transitions
4. **System Resources**: Monitor CPU and memory usage

For more detailed troubleshooting, consult the system's working memory and long-term memory for specific error patterns and solutions.

## Automatic Task Creation System 🔧

The system automatically creates refactoring tasks for oversized files (>500 lines) integrated directly into the commit workflow.

### How It Works

**Automatic Detection**: Every time you commit, the system:
1. **Scans all files** in the project with supported extensions (`.py`, `.js`, `.tex`, `.html`, `.css`, `.sh`)
2. **Detects files** exceeding 500 lines
3. **Creates refactoring tasks** automatically with appropriate priorities
4. **Stores tasks** in `.cursor/memory-bank/workflow/tasks.json`

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
4. Verify the task appears in Streamlit interface
5. Clean up: `rm test_file.py`

### Configuration Notes

**Important**: If you see git hook configuration pointing to `.githooks`, this is obsolete and can be removed:
```bash
git config --unset core.hooksPath
```

The functionality is now **100% integrated** into the commit workflow - no separate hooks needed.

### **Windows: git diff encoding fix**

If `python tomd.py` raises a `UnicodeDecodeError` when writing the git diff (Windows CP1252 decoding issue), update `tomd.py` to write the raw `git diff` bytes to the `diff` file. The script now writes the diff as binary to preserve arbitrary bytes and avoid platform-specific decoding errors. No user action is required for the fix bundled in the repository.
