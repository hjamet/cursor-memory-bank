# Cursor Memory Bank 🧠

Cursor Memory Bank est un système de **workflow autonome avancé** conçu pour transformer Cursor (et bientôt tout environnement compatible Antigravity) en un développeur IA proactif. Il combine une gestion de tâches intelligente, une mémoire persistante et une architecture modulaire pour assurer qualité et cohérence sur le long terme.

## Installation

```bash
# Installation rapide (Linux/macOS/WSL)
curl -fsSL https://raw.githubusercontent.com/hjamet/cursor-memory-bank/multi-agent/install.sh | bash
```

*Pré-requis : `git`, `curl`.*  
*Pour une installation locale (développement), voir `documentation/dev_install.md` (à venir).*

## Description détaillée

### Coeur du Système
Cursor Memory Bank agit comme le "cerveau" persistant de votre projet. Contrairement à une session de chat standard qui "oublie", ce système maintient :
- Une **Roadmap** centralisée des tâches.
- Une **Mémoire** des décisions architecturales et techniques.
- Des **Règles** strictes (linting, tests obligatoires) appliquées à chaque étape.

### Flux de Travail
L'agent opère selon des cycles autonomes définis par des **Workflows** (`.agent/workflows/` ou `.cursor/commands/`) :
1. **Planification** : Analyse de la demande, décomposition en tâches.
2. **Implémentation** : Modification du code.
3. **Vérification** : Test obligatoire (cycle `experience-execution`) avant validation.
4. **Mémorisation** : Mise à jour de la mémoire du projet.

### Rôle de l'Architecte
Le workflow `/architect` introduit un partenaire stratégique. L'Architecte ne code pas les fonctionnalités métiers mais :
- Structure le projet et la roadmap.
- Challenge vos décisions techniques.
- Maintient la documentation (`README.md`) et les règles (`.agent/rules`).
- Garantit que le projet reste propre et maintenable sur le long terme.

### Direction Actuelle
Le projet est en pleine **Refonte Architecturale (2026)** :
- **Transition vers `.agent`** : Standardisation de la configuration pour être agnostique (support Antigravity).
- **Refactoring `src/`** : Déplacement de tout le code source (Serveur MCP, UI Streamlit) dans un dossier `src/` structuré.
- **Simplification** : Suppression des outils redondants au profit d'outils spécialisés (`memory-bank-mcp`).

## Principaux résultats

*Statut actuel du projet : En cours de refonte majeure.*

| Métrique | État |
|----------|------|
| **Architecture** | 🚧 Transition `.cursor` → `.agent` en cours |
| **Compatibilité** | ✅ Cursor, 🚧 Antigravity (Partielle) |
| **Stabilité** | 🟢 Core stable, 🟠 UI en refactoring |

## Plan du repo

```
root/
├─ .agent/               # [NOUVEAU] Configuration Runtime (Workflows, Rules)
│  ├─ rules/             # Règles système (.md)
│  └─ workflows/         # Définitions des workflows (.md)
├─ .cursor/              # [LEGACY] Configuration spécifique IDE & Backwards compat
├─ src/                  # [NOUVEAU] Code Source du projet
│  ├─ server/            # Serveur MCP (Mémoire)
│  ├─ ui/                # Interface Streamlit
│  └─ scripts/           # Scripts d'installation et maintenance
├─ documentation/        # Documentation technique et troubleshooting
├─ install.sh            # Script d'installation principal
└─ implementation_plan.md # Plan de travail courant (Architecte)
```

## Scripts d'entrée principaux

Les principales commandes accessibles pour piloter l'agent.

| Commande/Script | Description détaillée | Usage / Exemple |
|-----------------|-----------------------|-----------------|
| `/architect` | Lance le mode Architecte pour planification stratégique et update roadmap. | `@src/commands/architect` ou `/architect` |
| `/agent` | Lance l'agent autonome pour exécuter une tâche de la roadmap. | `/agent` |
| `/enqueteur` | Lance une procédure d'investigation de bug step-by-step. | `/enqueteur` (Suivre les instructions) |
| `/janitor` | Analyse exhaustive du repo pour nettoyage et maintenance. | `/janitor` |
| `install.sh` | Installe ou met à jour le système Memory Bank. | `bash install.sh` |

## Scripts exécutables secondaires & Utilitaires

Outils internes utilisés par le système.

| Script | Rôle technique | Contexte d'exécution |
|--------|----------------|----------------------|
| `tomd.py` | Utilitaire de conversion et formatage Markdown. | Utilisé par les hooks et scripts internes. |
| `src/scripts/install_dev.sh` | (Prévu) Installation en mode lien symbolique pour le développement du repo. | Dev only. |

## Roadmap 2026 🛣️

Cette section détaille les chantiers techniques pour transformer ce dépôt d'une configuration Cursor spécifique vers une plateforme d'agents autonome et agnostique.

### 🚧 Phase 1 : Architecture & Migration (`src/` + `.agent/`)
*Objectif : Séparer proprement le code source (build) de la configuration runtime (run).*

- **Refactoring Structurel**
  - [ ] **Création de `src/`** : Centraliser tout le code exécutable (`src/server`, `src/ui`, `src/scripts`, `src/core`).
  - [ ] **Standard `.agent/`** : Adopter `.agent/rules` et `.agent/workflows` comme source de vérité unique (remplace `.cursor/rules` et `.cursor/commands` progressivement).
  - [ ] **Nettoyage Legacy** : Supprimer `mcp-commit-server` (déprécié) et archiver les anciennes commandes non portées.

- **Migration des Composants**
  - [ ] **Memory Bank MCP** : Déménager `memory-bank-mcp` (Node.js) vers `src/server/memory-bank`.
  - [ ] **Streamlit UI** : Déménager l'application `.cursor/streamlit_app` vers `src/ui`.
  - [ ] **Scripts** : Déplacer `install.sh` et utilitaires dans `src/scripts`.

### ⏳ Phase 2 : Déploiement & Expérience Développeur
*Objectif : Faciliter le test et le déploiement du système, pour les utilisateurs ET les développeurs du repo.*

- **Scripts d'Installation**
  - [ ] **`install_dev.sh`** : Nouveau script pour "monter" le repository courant en tant qu'agent actif (via symlinks) sans devoir push/pull. Permet d'itérer rapidement.
  - [ ] **`install.sh`** (Update) : Mettre à jour le script de production pour cloner `src/`, builder si nécessaire, et installer dans le dossier cible `.agent`.
  
- **Configuration MCP Universelle**
  - [ ] **`mcp_config.json`** : Générer une configuration MCP standard compatible avec Antigravity et Claude Desktop (plus seulement `.cursor/mcp.json`).

### 🔮 Phase 3 : Interface de Configuration (Agent Editor)
*Objectif : Permettre la modification des agents sans toucher aux fichiers Markdown/YAML à la main.*

- **Streamlit Agent Editor**
  - [ ] Créer une page "Configurateur" dans l'UI Streamlit.
  - [ ] Permettre l'édition des Prompts Système (`.agent/rules`).
  - [ ] Permettre l'édition des Transitions de Workflow (Graphe d'état).

---
*Note pour les Agents : Pour travailler sur ces tâches, référez-vous au fichier `implementation_plan.md` si disponible, ou créez-en un via `/architect` avant de commencer.*
