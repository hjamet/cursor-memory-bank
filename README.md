# Memory Bank

## Vue d'ensemble

Memory Bank est un système de mémoire persistante pour les agents IA, permettant de maintenir le contexte entre les sessions utilisateur en stockant et organisant les informations dans une structure de fichiers cohérente.

## Fonctionnalités principales

- **Persistance du contexte** entre les sessions utilisateur
- **Organisation structurée** de l'information dans des fichiers dédiés
- **Machine à états** basée sur des règles pour guider le workflow de l'agent
- **Suivi des tâches** et de la progression du projet
- **Prévention des boucles infinies** et des erreurs courantes

## Structure des fichiers

```
.cursor/memory-bank/
├── context/                 # Contexte du projet
│   ├── projectbrief.md      # Vision globale du projet
│   ├── activeContext.md     # Contexte de travail actuel
│   └── techContext.md       # Technologies et dépendances
└── workflow/                # Gestion du flux de travail
    ├── progress.md          # Suivi de la progression
    └── tasks.md             # Liste des tâches à accomplir

.cursor/rules/               # Règles du système
    ├── system.mdc           # Configuration générale du système
    ├── context-loading.mdc  # Chargement du contexte
    ├── request-analysis.mdc # Analyse des requêtes
    ├── task-decomposition.mdc # Décomposition des tâches
    └── ...                  # Autres règles du workflow
    └── custom/              # Règles personnalisées créées par l'agent
        ├── errors/          # Règles documentant les erreurs spécifiques
        └── preferences/     # Règles sur les préférences de l'utilisateur
```

## Installation

### Installation rapide

```bash
curl -fsSL https://raw.githubusercontent.com/votreusername/cursor-memory-bank/master/install.sh | bash
```

### Installation manuelle

1. Clonez ce dépôt dans un emplacement temporaire
2. Copiez le dossier `.cursor` dans la racine de votre projet
3. Commencez à utiliser Cursor avec la Memory Bank

## Workflow

Memory Bank implémente une machine à états où chaque règle représente un état avec des opérations spécifiques:

1. **Context-Loading**: Chargement du contexte du projet
2. **Request-Analysis**: Analyse approfondie de la requête utilisateur
3. **Task-Decomposition**: Décomposition de la requête en tâches spécifiques
4. **Implementation**: Implémentation des tâches définies
5. **Tests**: Création et exécution des tests
6. **Fix**: Correction des erreurs détectées
7. **Context-Update**: Mise à jour du contexte et préparation du commit

L'agent indique son état actuel dans le workflow avec un format standardisé:

```
# [Nom de la règle] : [numéro d'instruction] - [titre de l'instruction]
```

## Utilisation

1. Intégrez Memory Bank à votre projet en copiant le dossier `.cursor`
2. Ouvrez votre projet dans Cursor IDE
3. Interagissez normalement avec l'agent - il utilisera automatiquement Memory Bank pour maintenir le contexte

## Règles personnalisées

Memory Bank permet de créer des règles personnalisées pour:

- Documenter des erreurs courantes spécifiques à certaines bibliothèques
- Stocker les préférences utilisateur pour adapter le comportement de l'agent

## Contribution

Les contributions sont les bienvenues! N'hésitez pas à ouvrir une issue ou soumettre une pull request.

## Licence

MIT 