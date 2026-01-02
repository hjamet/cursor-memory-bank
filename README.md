# Cursor Memory Bank 🧠

Cursor Memory Bank est un système de gestion de projet autonome et structuré pour Cursor. Il remplace les systèmes de tâches complexes par une approche centrée sur le `README.md`, utilisé comme unique source de vérité pour la roadmap, l'installation et la documentation technique. L'agent Cursor utilise une règle dédiée pour maintenir ce fichier en permanence à jour, assurant une synchronisation parfaite entre le code et sa documentation.

# Installation

### Pré-requis
- **Bash** : *requis pour exécuter le script d'installation sur Linux/macOS.*
- **Git** : *nécessaire pour le clonage et la gestion des versions.*
- **Node.js (>=14.0.0)** : *requis pour certaines fonctionnalités avancées d'agent.*

### Étapes d'installation
```bash
curl -fsSL https://raw.githubusercontent.com/hjamet/cursor-memory-bank/master/install.sh | bash
```
*Téléchargement et exécution automatique du script d'installation unifié.*

```bash
bash install.sh --dir /chemin/vers/installation
```
*Installation dans un répertoire spécifique via les options du script.*

# Principaux résultats

| Métrique | Valeur | État |
|----------|--------|------|
| Statut du projet | Opérationnel (v1.0.0) | ✅ stable |
| Automatisation Roadmap | 100% via README.md | ✅ actif |
| Commandes Slash | Supprimées (Transition README) | 🗑️ fait |
| Support Multi-OS | Linux / macOS / Windows (via WSL) | ✅ supporté |

# Plan du repo

```
root/
├─ .cursor/              # Configuration Cursor (Règles MDC installées)
│  ├─ rules/            # Comportement de l'IA
├─ documentation/        # Guides approfondis et procédures détaillées
├─ src/                  # Code source des règles et commandes
│  ├─ rules/            # Fichiers sources des règles MDC
│  ├─ commands/         # Commandes utilitaires (enqueteur, janitor)
├─ install.sh           # Script d'installation automatisé
└─ README.md            # Source unique de vérité
```

- **`.cursor/rules/`** : *comportement de l'IA via des fichiers `.mdc` définissant les priorités et protocoles.*
- **`src/rules/`** : *fichiers sources originaux des règles pour faciliter la maintenance et les versions.*
- **`src/commands/`** : *fichiers sources des commandes utilitaires pour l'agent Cursor.*
- **`install.sh`** : *utilitaire central pour déployer proprement les règles et configurer `.gitignore`.*

# Scripts d'entrée principaux (scripts/)

| Chemin | Description | Exemple de commande |
|--------|-------------|---------------------|
| `install.sh` | Installateur universel du système Cursor Memory Bank. | `bash install.sh` *Installe les règles et configure le repo.* |

# Commandes d'Agent (via .cursor/commands/)

| Commande | Description | Usage |
|----------|-------------|-------|
| `/enqueteur` | Procédure d'enquête pas à pas pour le déverminage de bugs complexes. | `/enqueteur` *Lance l'analyse méthodique d'un problème.* |
| `/janitor` | Analyse critique du repository pour identifier les dettes techniques. | `/janitor` *Génère un rapport de maintenance.* |
| `/architect` | Planification de la roadmap, organisation du repo et gestion des règles. | `/architect` *Lance le flux de planification et d'architecture.* |

# Scripts exécutables secondaires (scripts/utils/)

*Aucun script utilitaire secondaire pour le moment.*

# Roadmap

| Tâche | Objectif | État | Dépendances |
|-------|----------|------|-------------|
| **Optimisation des règles** | Affiner les règles de communication et de démarrage pour mieux intégrer le flux centré sur le README uniquement. | 📅 À faire | - |
