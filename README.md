# Cursor Memory Bank 🧠

Cursor Memory Bank est un système de gestion de projet autonome et structuré pour Cursor. Il remplace les systèmes de tâches complexes par une approche centrée sur le `README.md`, utilisé comme unique source de vérité pour la roadmap, l'installation et la documentation technique. L'agent Cursor utilise une règle dédiée pour maintenir ce fichier en permanence à jour, assurant une synchronisation parfaite entre le code et sa documentation.

# Installation

**Linux / macOS :**
```bash
curl -fsSL https://raw.githubusercontent.com/hjamet/cursor-memory-bank/master/install.sh | bash
```

**Windows (PowerShell) :**
```powershell
# Nécessite Git Bash (inclus avec Git for Windows)
& 'C:\Program Files\Git\bin\bash.exe' -c "curl -fsSL https://raw.githubusercontent.com/hjamet/cursor-memory-bank/master/install.sh | bash"
```


# Description détaillée

### Cœur du Système : La Memory Bank
Ce dépôt implémente le pattern "Memory Bank", une approche où la mémoire du projet n'est plus dispersée dans des contextes éphémères mais cristallisée dans des fichiers markdown structurés. Le **README.md** agit comme le "Master Record", la source de vérité absolue.

### Flux de Travail Agentique
L'agent (Cursor/Antigravity) ne se contente pas de répondre aux questions ; il **gère** le projet.
1. **Lecture** : À chaque début de session, l'agent lit les règles (`src/rules/*.md`) pour comprendre son rôle.
2. **Action** : Il exécute les tâches définies dans la Roadmap du README.
3. **Mise à jour** : Il met à jour le README en temps réel pour refléter les progrès, garantissant qu'aucun contexte n'est perdu entre les sessions.

### Le Rôle de l'Architecte
Une commande spécifique (`/architect`) active un mode de réflexion stratégique. L'Architecte ne code pas immédiatement ; il planifie, remet en question les besoins, et conçoit des solutions robustes avant de passer à l'exécution. C'est un partenaire de "Pair Programming" de haut niveau.

### Direction Actuelle
Le projet se concentre actuellement sur :
- **Refonte de la documentation** : Migration vers des formats plus simples (`.md`) pour faciliter la maintenance.
- **Rigueur linguistique** : Imposition stricte du Français pour toutes les interactions et artefacts.
- **Standardisation** : Amélioration des scripts d'installation pour supporter ces nouveaux standards.

# Principaux résultats

| Métrique | Valeur | État |
|----------|--------|------|
| Statut du projet | Opérationnel (v1.0.1) | ✅ stable |
| Automatisation Roadmap | 100% via README.md | ✅ actif |
| Commandes Slash | Supprimées (Transition README) | 🗑️ fait |
| Support Multi-OS | Linux / macOS / Windows (via WSL) | ✅ supporté |

# Documentation Index

| Titre (Lien) | Description |
|--------------|-------------|
| [Template Index](docs/index_template.md) | Modèle pour les index de documentation |
| [Index Tâches](docs/index_tasks.md) | Spécifications des tâches Roadmap |

# Plan du repo

```
root/
├─ .cursor/              # Configuration Cursor (Règles MDC installées)
├─ src/                  # Code source
│  ├─ rules/            # Définitions des règles (Sources .md)
│  └─ commands/         # Workflows & commandes (.md)
│     ├─ scout.md       # 🔭 Exploration & plan préliminaire
│     ├─ refine.md      # 🧠 Validation critique du plan
│     ├─ build.md       # 🏗️ Implémentation du plan
│     └─ audit.md       # 🔎 Vérification de l'implémentation
├─ install.sh           # Script d'installation
└─ README.md            # Source unique de vérité
```

### Rôles des dossiers
- **`src/rules/`** : Contient les règles sources en format Markdown standard (`.md`).
- **`.cursor/rules/`** : Destination des règles installées (converties en `.mdc` pour Cursor).
- **`src/commands/`** : Définit les workflows spécifiques (Architecte, Enquêteur...).

# Scripts d'entrée principaux

| Script / Commande | Description détaillée | Usage / Exemple |
|-------------------|-----------------------|-----------------|
| `install.sh` | **Installateur Universel**. Clone le repo (si nécessaire), convertit les règles `.md` en `.mdc`, configure l'environnement `.cursor`, et déploie les workflows globaux Windows (monitor) dans les répertoires d'antigravity et de config globale (`.gemini/config/global_workflows`). | `bash install.sh` |
| `monitor` | **Superviseur de Boucle pour cluster-run**. Commande globale Windows lancée dans un projet pour exécuter en arrière-plan la commande `cluster-run`, envoyer périodiquement ses logs à l'agent en mode non-interactif pour vérification, et réveiller l'agent en cas d'erreur de crash pour correction automatique du code source. Permet également le réveil manuel de l'agent à tout moment via la touche `Entrée` avec possibilité de fournir un message personnalisé. L'agent dispose de l'historique complet des actions via `.monitor.log` et peut déclencher de lui-même le redémarrage de la commande s'il estime qu'une erreur critique nécessite le rechargement de la pipeline via le mot clé `RESTART CLUSTER RUN`. | `monitor` (depuis un projet avec cluster-run) |

### Commandes Agent (Virtuelles)
Ces commandes sont définies par les règles installées :

| Commande | Description détaillée | Usage |
|----------|-----------------------|-------|
| `/architect` | **Stratège du projet**. Analyse la demande, vérifie le `task.md`, et propose un plan d'action structuré. À utiliser pour les nouvelles fonctionnalités complexes. | Taper `/architect` dans le chat. |
| `/janitor` | **Maintenance et Nettoyage**. Scanne le code pour trouver du code mort, des TODOs oubliés ou des incohérences. Génère un rapport de maintenance. | Taper `/janitor` en fin de sprint. |
| `/enqueteur` | **Débuggage Profond**. Suit une procédure rigoureuse pour isoler la cause racine d'un bug avant de proposer un fix. | Taper `/enqueteur` face à un bug tenace. |
| `/context` | **Agent de Contexte**. Prépare le terrain. **Préserve la prompt** et **force la lecture des sources**. | Taper `/context` pour préparer une tâche. |
| `/handover` | **Passation de Service**. Génère un résumé structuré et narratif pour le prochain agent, avec décisions clés et plan d'action. | Taper `/handover` en fin de session. |
| `/research` | **Recherche Approfondie (Deep Research)**. Conduit une recherche structurée multi-axes avec vagues de recherches parallèles, suivi des sources, et produit un rapport détaillé avec citations footnote. | Taper `/research [sujet]` pour lancer une investigation. |
| `/pull` | **Merge des PRs & Validation**. Inventorie toutes les PRs ouvertes, les merge séquentiellement en résolvant les conflits, met à jour les issues liées, installe l'environnement de validation, et génère un walkthrough détaillé. | Taper `/pull` pour merger les PRs ouvertes. |
| `/continue` | **Reprise du Travail**. Rétablit l'ensemble de la supervision agentique et temporelle (crons, agents, sous-agents, timers) après une interruption, avec arbitrage intelligent pour la phase de validation. | Taper `/continue` pour reprendre et restaurer le travail suite à une interruption inattendue. |
| `/scheduler` | **Orchestrateur Cron Crash-Resilient**. Remplace le Monitor pour les workflows nocturnes/longs. Invoqué périodiquement via `/schedule` (cron Antigravity), consulte un fichier d'état central (`state.json`) et un heartbeat pour détecter les agents crashés. Exécute automatiquement le pipeline `issue → reviewer → investigator → architect` avec reprise après crash. | Configurer via `/schedule` : cron `*/15 * * * *`, prompt `Lis le fichier src/commands/scheduler.md et applique-le à la lettre. GOAL : [objectif]`. Contrôle via `.agents/scheduler/state.json`. |
| `/scout` | **Éclaireur de Code**. Explore en profondeur le codebase, la documentation et le web. Délègue à des sous-agents pour maximiser la couverture. Produit un `exploration_report.md` avec diagnostic, fichiers concernés et plan d'implémentation préliminaire. | Taper `/scout` pour lancer une exploration approfondie avant implémentation. |
| `/refine` | **Critique Stratégique du Plan**. Valide le plan du Scout avec une vision haut niveau. Traque les erreurs silencieuses, fallbacks cachés et incohérences. Annote le rapport d'exploration avec des callouts de review et produit un verdict (APPROUVÉ / RÉSERVES / À REVOIR). | Taper `/refine` après `/scout` pour valider et renforcer le plan. |
| `/build` | **Artisan Implémenteur**. Exécute méthodiquement le plan validé par le Refine, étape par étape. Commits atomiques, vérifications continues, respect des points de vigilance. Produit un `walkthrough.md` détaillé. | Taper `/build` après `/refine` pour implémenter le plan validé. |
| `/audit` | **Auditeur Critique**. Inspecte le code du Build, traque les erreurs silencieuses dans le code réel, analyse la cohérence des résultats. Peut corriger les problèmes triviaux et superviser l'exécution si demandé. Annote le walkthrough avec des callouts. | Taper `/audit` après `/build` pour valider l'implémentation. |

# Scripts exécutables secondaires & Utilitaires

| Script | Rôle technique | Contexte d'exécution |
|--------|----------------|----------------------|
| *Aucun* | *Pas d'utilitaires autonomes actuellement.* | - |

# Roadmap

| Tâche | Objectif | État | Dépendances |
|-------|----------|------|-------------|
| **Validation du flux** | Vérifier que le nouveau `install.sh` déploie correctement les règles `.mdc` et les workflows globaux. | ✅ Fait | - |
| **Optimisation Context** | Interdire la reformulation des prompts par l'agent de contexte. | ✅ Fait | - |
| **Refonte Handover** | Rendre le protocole de passation plus rigoureux (planning obligatoire, décisions explicites). | ✅ Fait | - |
