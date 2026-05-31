---
alwaysApply: true
description: Règle de communication — réponses claires, structurées et agréables à lire
---

# Communication Protocol

## Language Rules 🇫🇷/🇬🇧
1. **Chat & Artifacts**: IMMÉDIATEMENT et OBLIGATOIREMENT en **Français**. C'est une règle absolue. (User interaction, task lists, walkthroughs, Implementation Plan, brainstorming.md etc.).
2. **Code & Documentation Technique (in-code)**: ALWAYS in **English**. (Variable names, comments, commit messages).

## Style
- **Concise**: Short sentences, bullet points.
- **Visual**: Use tables for comparisons. Use bold for key terms.
- **Professional**: Direct, no fluff, no excessive emojis.

## Structure
- **Objectif**: Target.
- **Contexte**: Why.
- **Action**: What.
- **Impact Envisagé**: Result.

*No jargon. No long blocks of text. Clarity is king.*

## Partage Inter-Agents — Dossier `.agents/`

Les agents partagent leurs livrables via des **fichiers Markdown classiques** dans `.agents/` à la racine du projet :

- **Hiérarchie** : Chaque agent crée un dossier à son nom. Ses sous-agents créent des sous-dossiers.
- **Racine unique** : L'agent originel crée un dossier `<rôle>_<objectif>_<YYYYMMDD_HHMMSS>/` pour garantir l'unicité entre runs.
- **Écriture** : `write_to_file(IsArtifact=false)` ou `replace_file_content`.
- **Lecture** : `view_file`.
- **1 fichier = 1 propriétaire.** Les documents vivants (mises à jour en continu) sont autorisés.
- **Historique** : Le dossier `.agents/` est tracké par git et AIVC. Pas de nettoyage automatique.
- Ne **jamais** utiliser `IsArtifact=true` pour les documents destinés à d'autres agents.

