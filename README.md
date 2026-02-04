# Cursor Memory Bank 🧠

Cursor Memory Bank est un système de gestion de projet autonome et structuré pour Cursor. Il remplace les systèmes de tâches complexes par une approche centrée sur le `README.md`, utilisé comme unique source de vérité pour la roadmap, l'installation et la documentation technique. L'agent Cursor utilise une règle dédiée pour maintenir ce fichier en permanence à jour, assurant une synchronisation parfaite entre le code et sa documentation.

# Installation

```bash
# Installation et mise à jour
curl -fsSL https://raw.githubusercontent.com/hjamet/cursor-memory-bank/master/install.sh | bash
```
*Script universel pour Linux/macOS. Installe les règles `.mdc` dans `.cursor/rules`.*

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
| Statut du projet | Opérationnel (v1.0.0) | ✅ stable |
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
│  └─ commands/         # Commandes utilitaires (.md)
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
| `install.sh` | **Installateur Universel**. Clone le repo (si nécessaire), convertit les règles `.md` en `.mdc`, et configure l'environnement `.cursor`. | `bash install.sh` |

### Commandes Agent (Virtuelles)
Ces commandes sont définies par les règles installées :

| Commande | Description détaillée | Usage |
|----------|-----------------------|-------|
| `/architect` | **Stratège du projet**. Analyse la demande, vérifie le `task.md`, et propose un plan d'action structuré. À utiliser pour les nouvelles fonctionnalités complexes. | Taper `/architect` dans le chat. |
| `/janitor` | **Maintenance et Nettoyage**. Scanne le code pour trouver du code mort, des TODOs oubliés ou des incohérences. Génère un rapport de maintenance. | Taper `/janitor` en fin de sprint. |
| `/enqueteur` | **Débuggage Profond**. Suit une procédure rigoureuse pour isoler la cause racine d'un bug avant de proposer un fix. | Taper `/enqueteur` face à un bug tenace. |
| `/context` | **Agent de Contexte**. Prépare le terrain. **Préserve la prompt** et **force la lecture des sources**. | Taper `/context` pour préparer une tâche. |
| `/handover` | **Passation de Service**. Génère un résumé structuré et narratif pour le prochain agent, avec décisions clés et plan d'action. | Taper `/handover` en fin de session. |

# Scripts exécutables secondaires & Utilitaires

| Script | Rôle technique | Contexte d'exécution |
|--------|----------------|----------------------|
| *Aucun* | *Pas d'utilitaires autonomes actuellement.* | - |

# Roadmap

| Tâche | Objectif | État | Dépendances |
|-------|----------|------|-------------|
| **Validation du flux** | Vérifier que le nouveau `install.sh` déploie correctement les règles `.mdc` et que le README suit la nouvelle structure. | 📅 À faire | - |
| **Optimisation Context** | Interdire la reformulation des prompts par l'agent de contexte. | ✅ Fait | - |
| **Refonte Handover** | Rendre le protocole de passation plus rigoureux (planning obligatoire, décisions explicites). | ✅ Fait | - |
