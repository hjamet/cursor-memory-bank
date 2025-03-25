# Contexte Technique

## Pile Technologique
- **Langages**: Markdown (.md, .mdc), Shell (.sh)
- **Frameworks**: Système de règles Cursor
- **Outils**: Cursor AI Assistant

## Architecture
Memory Bank utilise une structure de fichiers organisée et fonctionne comme une machine à états où chaque règle représente un état avec des actions spécifiques.

## Organisation des Fichiers
- **src/**: Scripts sources du projet (install.sh)
- **tests/**: Tests unitaires et d'intégration (test_*.sh)
- **.cursor/memory-bank/**: Stockage du contexte et du workflow
- **.cursor/rules/**: Règles de la machine à états

## Environnement
- **Configuration requise**: Cursor IDE
- **Installation**: Script curl ou copie manuelle du dossier .cursor

## Conventions
- Règles (.mdc): Structure TLDR, Instructions, Précisions, Next Rules
- Fichiers contexte (.md): Titres et sous-titres hiérarchisés
- Affichage workflow: Format "# [Règle] : [numéro] - [instruction]"
- Scripts: Placés dans src/ avec tests correspondants dans tests/

## Workflow
- Appel obligatoire de la règle suivante après chaque règle
- Syntaxe explicite: @cursor-rules [nom-de-la-règle]
- Exception unique: finalisation par context-update

## Dépendances
- Curl: Téléchargement du script d'installation
- Bash: Exécution des scripts shell 