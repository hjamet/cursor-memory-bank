# Contexte Technique

## Pile Technologique
- **Langages**: Markdown (.md, .mdc)
- **Frameworks**: Système de règles Cursor
- **Bibliothèques**: N/A
- **Outils**: Cursor AI Assistant

## Architecture
Memory Bank est basé sur une structure de fichiers organisée en dossiers thématiques. Le système fonctionne comme une machine à états où chaque règle représente un état avec des actions spécifiques à effectuer.

## Environnement de Développement
- **Configuration requise**: Cursor IDE
- **Installation**: Structure de dossiers dans le projet utilisateur

## Conventions de Code
- Les fichiers de règles (.mdc) suivent une structure standardisée avec des sections TLDR, Instructions, Précisions et Next Rules
- Les fichiers de contexte (.md) utilisent des titres et sous-titres pour une organisation claire
- Indication de l'état actuel dans le workflow avec un format spécifique: "# [Nom de la règle] : [numéro d'instruction] - [titre de l'instruction]"

## Dépendances Externes
- Cursor AI: Version actuelle - Assistant IA utilisé pour exécuter les règles

## Intégrations
- Système de fichiers: Stockage persistant des informations de contexte
- Cursor Rules: Système de règles personnalisées pour structurer le workflow 