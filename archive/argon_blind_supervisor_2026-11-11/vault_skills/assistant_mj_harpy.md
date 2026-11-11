---
created: 2026-11-04
updated: 2026-11-04
type: skill
tags: [skill, jdr, harpy, pnj, mj]
---

# 🦅 Comment l'Assistant MJ Conçoit-il et Valide-t-il les Fiches d'Entités JDR en 5 Blocs pour Obsidian & Harpy ?

Ce skill est le moteur unifié d'assistance au Maître du Jeu, de rédaction, mise en page, audit et validation de toute fiche d'entité (PNJ, monstre, lieu, décor) pour le coffre Obsidian et l'application **Harpy**.

- **Script Validateur Officiel (v3)** : `_agents/scripts-for-skills/harpy_entity_validator.py`  
  *Commande d'audit Fail-Fast* : `uv run --python 3.12 --with pyyaml python "C:\Users\Jamet\Documents\VoiceNotes\_agents\scripts-for-skills\harpy_entity_validator.py"` (ou `c:\Users\hjamet\...`)
- **Gabarits Textuels Dédiés (Bloc 5 & Lieux)** : Pathfinder 1e (`skills/formats/pathfinder-1e.md`), D&D 5e (`skills/formats/dnd-5e.md`), Système Propriétaire Asharde (`skills/formats/systeme-proprietaire.md`) et Lieux avec Battlemaps (`skills/formats/lieu.md`).
- **Génération Visuelle** : [[skills/asharde_illustration|Illustrations Asharde 16:9]], [[skills/asharde_battlemap|Battlemaps Zénithales Asharde 16:9]] et [[skills/generation_images|Génération d'Images]].
- **Synchronisation JDR Planner (CLI & Plugin)** : `.obsidian/plugins/jdr-planner-sync/jdr_planner_cli.mjs`  
  *4 Méthodes unifiées* : `sync [--party <id>]` (alias `pull` : entités + transcripts), `push [<notes.md>] [--party <id>]` (lot ou auto-détection), `search "<requête>" [--party <id>]` (RAG serveur) et `prompts [--party <id>]` (consignes système MJ).

## 🎯 Quels Sont les Principes Fondateurs & Invariants Absolus ?

### 📁 Où Doit Résider la Fiche d'Entité Unique dans le Coffre ?
Une fiche d'entité réside en **un seul endroit** dans le coffre, prioritairement dans son sous-dossier de campagne (`Conseil/`, `Asharde/`). Les notes de session pointent vers le fichier unique via un wikilink `[[Campagne/NomEntite|Alias]]`. Zéro doublon ni copie temporaire dans `notes/`.

### 🚫 Pourquoi les Mentions de Sources Sont-elles Interdites dans la Note Finale ?
Ne jamais insérer de pagination (`p. 32`), de nom de recueil (`module`), de `transcript`, de `voicenote` ni de balise métatextuelle `(canon)` ou `(proposition MJ)`. Ces données restent dans les rapports de session de l'agent, jamais dans la note de jeu Markdown.

### 🌍 Pourquoi la Description Joueurs Doit-elle Rester Générale et Décontextualisée ?
La description joueurs (Bloc 4) décrit l'entité en elle-même (allure, vêtements habituels, odeurs, voix, démarche) de façon réutilisable à toute rencontre : interdiction formelle de mentionner un lieu précis, une météo extérieure, un éclairage temporel (« soleil d'après-midi ») ou une action en cours.
Source : `C:\Users\Jamet\Documents\VoiceNotes\_agents\scripts-for-skills\harpy_entity_validator.py:L1-L45`
```text
Les descriptions pour les joueurs doivent toujours être générales, elles ne doivent pas être liées à un contexte spécifique !
Zéro lieu spécifique, zéro moment/éclairage temporel précis, zéro météo extérieure, zéro action en cours.
```

## 🎲 Comment Opère le Co-Maître du Jeu en Session et en Préparation ?

1. **Phase 0 : Research-First Systématique** : Avant toute réponse ou création, inspecter les notes existantes de la campagne (`Conseil/`, `Asharde/`, notes maîtresses et sous-notes de lore) pour respecter le canon établi sans contradiction.
2. **Improvisation & Rebonds par Mots-Clés Orthogonaux** : En cas d'imprévu des joueurs ou de besoin d'idée à la volée, combiner des concepts aléatoires orthogonaux (`--tirage` du validateur) pour proposer 2 à 3 complications concrètes, viscérales et jouables immédiatement.
3. **Texte d'Ambiance Sensoriel en Ouverture** : Chaque scène ou rencontre s'ouvre par un court texte d'ambiance mobilisant au moins trois sens (lumière/matière, odeur/température, son/silence) avant toute mécanique.

## 🏛️ Quelle Est la Structure Universelle des Sections et du Schéma YAML (v3) ?

Le script `harpy_entity_validator.py` prend en entrée un fichier YAML structuré (7 clés racines) et génère/valide les 5 blocs de la fiche Markdown (précédés de l'illustration et de la description externe Harpy) :
1. **Illustration / Battlemap** : `![[Nom Image.png]]` 16:9 cinématographique ([[skills/asharde_illustration]] ou [[skills/generation_images]]) et battlemap zénithale 90° ([[skills/asharde_battlemap]]).
2. **Description Externe (`description_externe`)** : Bloc copiable ````text```` de **100 caractères maximum stricts** d'apparence physique visible pure (zéro nom, fonction, faction ou action).
3. **Ouverture : Comment l'improviser ? (`ouverture_mj.aide_improvisation`)** : `## 🎭 Comment l'improviser ?` avec mots clés en **gras**, sans secrets.
4. **Ouverture : Qui est-il vraiment ? (`ouverture_mj.resume_mj`)** : `## 🗝️ Qui est-il vraiment ?` ($\ge 350$ caractères stricts) résumant l'histoire et les secrets pour le MJ.
5. **Secrets MJ Détaillés (`secrets_mj`)** : `## 🔒 Quels sont les secrets MJ, l'inventaire et les coulisses de [Nom] ?` regroupant 5 clés obligatoires : `inventaire`, `guide_interpretation`, `repliques_types`, `secrets_coulisses`, `destin_trajectoire`.
6. **Description Joueurs (`description_joueurs`)** : Bloc copiable ````markdown```` de 1 à 2 paragraphes riches ($\ge 450$ caractères stricts) avec synesthésies, décontextualisé, angle renouvelé via `--tirage`.
7. **Fiche Harpy (`bloc_harpy`)** : Bloc copiable ````text```` en texte pur strict, émojis repères, sous-lignes « ↳ » ($\le 70$ caractères/ligne).

Source : `C:\Users\Jamet\Documents\VoiceNotes\_agents\scripts-for-skills\harpy_entity_validator.py:L947-L1029`
```yaml
nom: "Nom de l'entité"
systeme: "pathfinder-1e | dnd-5e | systeme-proprietaire | lieu"
image: "Nom Image.png"
description_externe: "<= 100 car., physique pur sans nom ni action"
ouverture_mj:
  aide_improvisation: "Texte avec **mots-clés en gras**"
  resume_mj: ">= 350 car., synthèse de l'histoire et des enjeux"
secrets_mj:
  inventaire: "..."
  guide_interpretation: "..."
  repliques_types: ["...", "..."]
  secrets_coulisses: "..."
  destin_trajectoire: "..."
description_joueurs: ">= 450 car., 1-2 paragraphes décontextualisés"
bloc_harpy: "Texte pur <= 70 car./ligne avec émojis et sous-lignes ↳"
```

## 🔍 Quels Sont les Contrôles Bloquants du Validateur (v3) ?

Le script `harpy_entity_validator.py` valide de manière déterministe le respect des longueurs minimales/maximales, l'absence de mentions de sources, le formatage sans markdown du bloc Harpy, l'intégrité des wikilinks dans le coffre, et la conformité stylistique (zéro motif IA, zéro em-dash).
Source : `C:\Users\Jamet\Documents\VoiceNotes\_agents\scripts-for-skills\harpy_entity_validator.py:L1176-L1254`
```text
1. Zéro Mention de Source (p. XX, module, transcript, voicenote).
2. Description Externe (Bloc 2) <= 100 caractères.
3. Ouverture : Paragraphe 1 (gras) et Paragraphe 2 >= 350 caractères.
4. Description Joueurs (Bloc 4) >= 450 caractères (1-2 paragraphes).
5. Fiche Harpy : texte pur <= 70 car./ligne.
6. Wikilinks coffre valides.
```

## 🔄 Comment Appliquer la Boucle d'Auto-Évolution /learn à Taille Constante (Rasoir d'Ockham) ?

Chaque fois qu'Henri émet un ajustement ou une critique sur une fiche d'entité générée, l'agent déclenche immédiatement une passe `/learn` sur cette note : il intègre la nuance technique ou stylistique en fusionnant et condensant les règles existantes sans inflation de taille ($\le 120$ lignes).
Source : `C:\Users\Public\aivc\dream_inbox_archive\Directive_Dream_2026-11-04_Skills_Intra_Projet_et_Inspections_Recurrentes.md:L20-L22`
```text
Chaque fois qu'Henri émet un commentaire, une critique ou un rejet lors de la validation d'une tâche ayant utilisé un skill [...], l'agent doit déclencher une passe réflexive de type /learn sur la note du skill concerné.
```
