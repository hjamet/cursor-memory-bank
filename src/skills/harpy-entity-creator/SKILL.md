---
name: harpy-entity-creator
description: Générateur universel de fiches d'entités JDR pour Obsidian et Harpy, rigoureusement calibré sur la Fiche de Style d'univers, notes/Modèle Fiche Entité Pathfinder 1e.md et notes/Shanwen.md. Structure canonique en 5 blocs sans description dans le YAML, courte citation sensorielle sous l'image avant la Vue Joueurs, maillage dense de wikilinks dans les secrets MJ, profils mécaniques compacts et copier-coller Harpy en 30 secondes.
---

# Harpy Entity Creator — Générateur Universel d'Entités JDR pour Obsidian & Harpy

> **Aliases & Invocations** : `/harpy-entity-creator` | `/rpg-entity-creator` | `/jdr-entity-creator`
> **Fiche Étalon Canonique** : [`notes/Shanwen.md`](file:///c:/Users/Jamet/Documents/VoiceNotes/notes/Shanwen.md)
> **Note Modèle de Référence** : [`notes/Modèle Fiche Entité Pathfinder 1e.md`](file:///c:/Users/Jamet/Documents/VoiceNotes/notes/Mod%C3%A8le%20Fiche%20Entit%C3%A9%20Pathfinder%201e.md)

Ce skill est le **moteur unifié de rédaction, mise en page et illustration** de toute fiche d'entité de jeu de rôle (PNJ, Monstre, Lieu, Donjon, Bâtiment, Objet magique, Sortilège, Faction ou Scène) pour le coffre Obsidian d'Henri Jamet et l'application **Harpy**.

---

## 1. Principes Fondateurs & Exigences Absolues

1. **Ancrage Obligatoire dans la Fiche de Style d'Univers / Campagne (MANDATOIRE)** :
   Avant de poser la moindre ligne, l'agent doit consulter la **Fiche de Style** de la campagne (ex: `[[Conseil/Fiche de Style Le Conseil des Voleurs|Fiche de Style Le Conseil des Voleurs]]` ou `[[Asharde/Fiche de Style Asharde]]`) pour adopter le système de règles idoine (Pathfinder 1e, D&D 5e, système maison), le barème de FP/niveaux, le lexique francophone canonique et l'ambiance attendue.
2. **Étincelle Créative par Mot-Clé Aléatoire** :
   Pour éviter les fiches stéréotypées, utiliser une amorce sous forme de **mot-clé aléatoire** (concept, objet insolite, paradoxe) afin d'insuffler une singularité marquante à l'entité (manie, accessoire fétiche, secret inavouable).
3. **Calibrage Strict sur la Fiche Étalon (`notes/Shanwen.md`)** :
   Toute fiche générée doit refléter fidèlement l'élégance, la densité technique et l'ergonomie de `Shanwen.md`.
4. **Suppression Formelle de `description:` dans le YAML** :
   Le champ `description:` est strictement banni du frontmatter YAML pour éliminer toute redondance et alléger les métadonnées Obsidian.
5. **Courte Description Sensorielle Placée Sous l'Image** :
   La courte vue sensorielle (1 à 2 phrases percutantes, max 120 caractères) se place directement sous l'illustration 16:9 sous forme d'une citation Markdown `> ...`, juste avant le callout `> [!quote] 👤 Vue Joueurs`.
6. **Obligation d'Interconnexion Dense dans les Secrets MJ (`> [!warning]`) (MANDATOIRE)** :
   Dans le callout `> [!warning] 🔒 Secrets MJ / Coulisses` et les sections privées MJ, insérer sans hésiter de **multiples liens Obsidian `[[...]]`** vers les factions (`[[Conseil/Ordre du Chevalet|Ordre du Chevalet]]`), les PNJ alliés ou rivaux (`[[notes/Herb le Soufré|Herb le Soufré]]`), les lieux canoniques (`[[Conseil/Pont sur l Athua Site de l Embuscade|Pont sur l'Athua]]`), le lore (`[[Culte d'Asmodéus]]`) et la Fiche de Style. Chaque fiche devient ainsi un hub d'exploration instantané pour le MJ en partie.
7. **Liaison Proactive aux Notes Maîtresses & Sessions (MANDATOIRE)** :
   Chaque entité doit être explicitement liée à la campagne maîtresse et à la session active :
   - `[[notes/Le Conseil des Voleurs|Le Conseil des Voleurs]]`
   - `[[notes/Session JDR Le Conseil des Voleurs 9 septembre 2026|Session Active]]`
8. **Tag Dynamique de Session (MANDATOIRE)** :
   Dans le frontmatter YAML, le premier tag doit obligatoirement être le tag de session de préparation sans zéro initial : `session-5` (ou `session-1`, `session-4`, etc.).
9. **Illustration 16:9 Dédiée & Zéro Placeholder** :
   - PNJ, Monstres, Objets : Génération 16:9 via `/asharde-visual-architect` (Master Formula).
   - Donjons, Plans, Battlemaps : Génération 16:9 vue 90° sans grille via `/asharde-cartographer` (The Cartographer Formula).
   - Lieux & Bâtiments : **Deux images 16:9 minimum** (1 vue d'ambiance immersive + 1 battlemap zénithale).
   - L'illustration doit exister physiquement dans `_attachments/`. Zéro placeholder toléré.
10. **Copier-Coller Manuel Ultra-Fluide vers Harpy (< 30 secondes)** :
    Henri copie directement les sections de la note Markdown vers les champs de Harpy. La balise de pagination Harpy `<!-- harpy:page {"displayName":"Secrets MJ & Coulisses"} -->` isole automatiquement les secrets des joueurs lors de la manipulation.
11. **Immersion 100% en Français Soigné & Bannissement des Anglicismes** :
    Zéro terme ou doublon anglais entre parenthèses. Utilisation exclusive des sigles mécaniques francophones officiels : `CA`, `PV`, `BBA`, `BMO`, `DMD`, `RD`, `RM`, `FP`, `DD`, `AdO`, `DV`.

---

## 2. Structure Universelle en 5 Blocs Canoniques Révisée

Chaque note d'entité créée doit respecter rigoureusement l'enchaînement des 5 blocs suivants :

```
┌────────────────────────────────────────────────────────────────────────┐
│ BLOC 1 : FRONTMATTER YAML STANDARDISÉ (Obsidian + Harpy)               │
│ - displayName, type, category, Image (SANS champ description:)         │
│ - tags : session-N, date, PNJ/Monstre, Système, Campagne               │
│ - variables compactes pour Harpy : Classe, PV, CA, FP, BBA...          │
├────────────────────────────────────────────────────────────────────────┤
│ BLOC 2 : MAXIME DE L'ENTITÉ (DIRECTEMENT SOUS LE YAML)                 │
│ - > *« Citation percutante incarnant la voix et l'éthique »*          │
│ - STRICTEMENT AUCUN TITRE H1 `# [Nom]` (évite le doublon avec le nom) │
├────────────────────────────────────────────────────────────────────────┤
│ BLOC 3 : ILLUSTRATION 16:9 DÉDIÉE & CITATION SENSORIELLE               │
│ - ![[Dossier/_attachments/nom_image_16_9.png]]                         │
│ - > Courte vue extérieure sensorielle (≤ 120 car., sans spoiler)       │
├────────────────────────────────────────────────────────────────────────┤
│ BLOC 4 : LES DEUX CALLOUTS ÉTANCHES AVEC MAILLAGE DENSE MJ & ACTIONS   │
│ - > [!quote] 👤 Vue Joueurs / Directement visible                      │
│   (Allure, démarche, voix, posture, adjectifs en GRAS)                 │
│ - > [!warning] 🔒 Secrets MJ / Coulisses (DENSE EN WIKILINKS [[...]])  │
│   (Allégeances [[Factions]], rivaux [[PNJ]], lieux [[Lieux]], peurs)   │
│   (Fiche technique, Puissance, Source, Liaisons [[Campagne]]/[[Session]])│
│ - Puces d'actions réflexes : ⚔️ Attaque, 🏹 Pouvoir, 🔮 Magie, 🎲 Réflexe│
├────────────────────────────────────────────────────────────────────────┤
│ BLOC 5 : PROFIL MÉCANIQUE COMPLET & SECRETS ÉTENDUS HARPY              │
│ - ## ⚔️ Profil Mécanique & Statblock Complet (Tableaux compacts)       │
│   * Stats Principales (Init, Vitesse, CA, PV, Sauvegardes, BMO/DMD)    │
│   * Attaques & Capacités (Attaques, Aptitudes Ext/Sur/Mag, Sorts)      │
│   * Équipement & Trésor (Combat, Divers, Richesse)                     │
│   * Statistiques & Compétences (BBA, Sens, Langues, Dons, Compétences) │
│   * Attributs Principaux (For, Dex, Con, Int, Sag, Cha)                │
│ - <!-- harpy:page {"displayName":"Secrets MJ & Coulisses"} -->         │
│ - # Secrets MJ & Coulisses                                             │
│   * ### 💬 Répliques Types & Interactions Clés (3 répliques)           │
│   * ### ⏳ Destin & Trajectoire Narrative (Moments clés & 3 Phases)    │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Matrice de Correspondance pour le Copier-Coller dans Harpy

| Section de la Note Obsidian | Destination dans Harpy | Usage en Partie |
| :--- | :--- | :--- |
| **Frontmatter YAML** (`displayName`, `category`, `tags`) | **Nom de la carte**, **Dossier**, **Tags** | Tri immédiat par filtre `session-5` dans Harpy. |
| **Bloc 2 (Maxime)** + **Citation sensorielle** + **Bloc 4 (`Vue Joueurs`)** | Champ **Description** (Face publique) | Affiché aux joueurs lors d'un partage de fiche. |
| **Bloc 3 (`_attachments/...png`)** | **Avatar / Illustration de carte** | Visuel 16:9 plein écran de la carte Harpy. |
| **Bloc 4 (`Secrets MJ` maillés [[...]])** + **Bloc 5 (`Destin`)** | Champ **Notes Privées / Secrets MJ** | Révélations, factions et intrigue sous les yeux du MJ seul. |
| **Bloc 4 (Puces Réflexes)** + **Bloc 5 (Statblock)** | Section **Actions / Stats Rapides** | Lancer les attaques et sauvegardes sans latence. |

---

## 4. Modèle Canonique Complet Prêt à l'Emploi (Template Étalon Révisé)

```markdown
---
displayName: "[Nom de l'Entité]"
harpy-last-sync: "2026-09-09T18:00:00.000Z"
lastSync: "2026-09-09T18:00:00.000Z"
type: character
category: PNJ
tags:
  - session-5
  - 2026-09-09
  - PNJ
  - Pathfinder-1e
  - [Campagne-Cible]
variables:
  Classe: "[Classe et Niveau]"
  PV: [PV]
  CA: [CA]
  FP: "[FP]"
  BBA: [BBA]
  PerceptionPassif: [10 + Mod Perception]
Image: "[[Conseil/_attachments/nom_image_16_9.png]]"
---

> *« [Maxime / Citation percutante incarnant la voix et l'éthique de l'entité] »*

![[Conseil/_attachments/nom_image_16_9.png]]
> [Courte description sensorielle extérieure, max 120 caractères, zéro spoiler.]

> [!quote] 👤 Vue Joueurs / Directement visible
> [Physique, allure, démarche, voix et vêtements distinctifs avec adjectifs clés en **gras**.]

> [!warning] 🔒 Secrets MJ / Coulisses
> [Origines, allégeances secrètes à la faction [[Conseil/Ordre du Chevalet|Ordre du Chevalet]], rivalités avec [[notes/Herb le Soufré|Herb]], motivations profondes et peurs intimes.]
>
> **Fiche technique :** [Race] ([Genre]) [Classe] [Niveau]. [Type (Sous-type)] de taille [Taille], d'alignement [Alignement].  
> **Puissance :** FP [FP] ([XP] px).  
> **Source :** *[Ouvrage de référence]*, p. [XX].  
> **Liaisons Campagne :** [[Conseil/Fiche de Style Le Conseil des Voleurs|Fiche de Style]] • [[notes/Le Conseil des Voleurs|Cockpit Campagne]] • [[notes/Session JDR Le Conseil des Voleurs 9 septembre 2026|Session Active]] • [[Conseil/Pont sur l Athua Site de l Embuscade|Lieu d'Intervention]]

- ⚔️ **Attaque principale ([Arme])** : +[X] au toucher ([Dégâts] / [Critique], Portée [X] m). [Effet additionnel].
- 🏹 **Pouvoir clé ([Capacité majeure])** : [Fonctionnement direct, DD de sauvegarde, cadence].
- 🔮 **Pouvoir magique direct ([Sort/Don])** : [Portée, effet, utilisations par jour].
- 🎲 **Mécanique / Réflexe ([Interaction clé])** : [Bonus contextuel ou jet d'opposition].

---

## ⚔️ Profil Mécanique & Statblock Complet

### 🛡️ Stats Principales
| Initiative & Vitesse | CA | PV | Sauvegardes | BMO & DMD | RD, RM & Immunités |
| :--- | :--- | :---: | :--- | :--- | :--- |
| Init +[X], Vitesse [X] m | **[Total]**, contact [X], pris au dépourvu [X] (+[X] armure, +[X] Dex) | **[Total]** ([DV]) | **Vigueur** +[X], **Réflexes** +[X], **Volonté** +[X] | BMO +[X], DMD [X] | [RD, RM, Immunités] |

### ⚔️ Attaques & Capacités
* 🔮 **[Capacité Magique]** (`Mag`) : [Description de l'effet, portée, utilisations].
* ✨ **[Capacité Surnaturelle]** (`Sur`) : [Description, DD de sauvegarde].
* 📜 **Sortilèges préparés / connus** (`Sort`, NLS [X], DD [X] + niveau) :
  * **Niveau 1** ([X]/jour, DD [X]) : *[Sort 1]*, *[Sort 2]*.
  * **Niveau 0** ([X] à volonté) : *[Sort de base]*.

### 🎒 Équipement & Trésor
| Catégorie | Éléments & Détails |
| :--- | :--- |
| ⚔️ **Équipement de combat** | [Armes équipées, munitions, potions de soins] |
| 🎒 **Équipement divers** | [Armures, vêtements de fonction, clés maîtresses, missives scellées vers [[Citadelle de Rivad]]] |
| 💰 **Richesse** | [Bourse de pièces d'or (PO), bijoux, titres] |

### 🎲 Statistiques & Compétences
| Caractéristique | Valeur / Détail |
| :--- | :--- |
| 🎯 **BBA** | +[X] |
| 👁️ **Sens** | Perception +[X], [Vision dans le noir / normale] |
| 🗣️ **Langues** | [Langues parlées] |
| 🎖️ **Dons** | [Liste des dons] |
| 📚 **Compétences principales** | [Compétence 1] +[X] ([N] rgs), [Compétence 2] +[X] ([N] rgs) |

### 📊 Attributs Principaux
| Force | Dextérité | Constitution | Intelligence | Sagesse | Charisme |
| :---: | :---: | :---: | :---: | :---: | :---: |
| [10 (+0)] | [10 (+0)] | [10 (+0)] | [10 (+0)] | [10 (+0)] | [10 (+0)] |

<!-- harpy:page {"displayName":"Secrets MJ & Coulisses"} -->
# Secrets MJ & Coulisses

### 💬 Répliques Types & Interactions Clés
* *« [Réplique d'accueil ou de négociation marquant le ton habituel] »*
* *« [Réplique en situation de tension, de crise ou de combat] »*
* *« [Dernière parole ou sentence rituelle] »*

### ⏳ Destin & Trajectoire Narrative
* 🌟 **Le plus beau moment de sa vie** : [Événement fondateur ayant forgé sa vision du monde].
* ⚡ **Le pire moment de sa vie** : [Traumatisme originel ou pire défaite le hantant encore face à [[Conseil/Les Bâtards de l'Érèbe|la rébellion]]].
* 💀 **Comment il devrait mourir** : [Mort spectaculaire ou tragique prévue s'il n'est pas sauvé].
* **Phase 1 ([Ancrage initial])** : [Point de rencontre avec les PJ lors de la session].
* **Phase 2 ([Destin autonome])** : [Comportement si les PJ fuient ou le laissent agir dans [[Couronne d'Ouest]]].
* **Phase 3 ([Climax / Dépouille])** : [Conséquences de sa chute et révélations vers [[notes/Durotas Marcus Valerius|Marcus Valerius]]].
