---
created: 2026-11-04
updated: 2026-11-04
type: skill
tags:
  - skill
  - jdr
  - asharde
  - battlemap
  - cartographie
---

# 🗺️ Comment Générer des Battlemaps Tactiques Zénithales 16:9 pour l'Univers d'Asharde ?

Ce skill régit la génération de cartes de combat tactiques ultra-détaillées, sans grille, sans personnages et en vue strictement zénithale à 90° au format **paysage (16:9)** pour les lieux et décors d'Asharde et de médiéval-fantastique réaliste.

## 📐 Quels Sont les Invariants Cartographiques Obligatoires ?

Toute battlemap est générée via l'outil natif `generate_image` au format paysage strict **16:9** (`AspectRatio: "16:9"`), enregistrée dans `_attachments/` et intégrée sous la forme `![[Nom Battlemap.png]]` avec sa légende en italique sur la ligne suivante.
Source : `Prompt d'Henri Jamet (Charte Cartographique Asharde Top-Down 90° 16:9)`
```text
Toute génération de battlemap est réalisée via l'outil natif generate_image.
Format obligatoire : AspectRatio: "16:9". L'image est enregistrée dans _attachments/.
Vue Zénithale Strictement à 90° & Sans Grille : Perspective orthogonale stricte du dessus, sans ligne d'horizon, sans grille et sans créatures ou personnages.
Plein Cadre & Netteté Bord-à-Bord : Le terrain est jouable et net jusqu'aux quatre coins de l'image.
```

- **Règle de Simplicité** : Garder autant que possible une seule carte par simplicité. Ne générer de cartes secondaires que si des étages nettement séparés et indispensables le justifient.

## ⚙️ Quels Sont les 5 Piliers de la Cartography Formula ?

Chaque prompt envoyé au modèle de génération doit strictement respecter l'architecture en cinq points en anglais :
- **1. Core Structure & Perspective (CRITICAL)** : *"A Tabletop RPG battle map of [LOCATION], viewed from a **strict, perfect top-down bird's-eye perspective (90 degrees looking directly down)**. Orthographic projection. This is a functional floor plan. We are looking directly down at the ground, roofs, floors, or terrain. There is absolutely no visible horizon."*
- **2. Extreme Detail, Variety & Originality** : *"The environment must be densely packed with intricate, high-resolution details and varied textures. Avoid generic, repetitive layouts. Introduce unique architectural quirks, original environmental storytelling elements, and a rich diversity of props (scattered debris, specific localized tools, distinctive vegetation, uneven terrain) that make the location feel uniquely lived-in, organic, and incredibly real."*
- **3. Playability & Layout** : *"The layout provides clear, readable spaces where game tokens can be seamlessly placed. The geometry of the walls, floors, and environmental obstacles is perfectly defined from above. Absolutely no grids, measuring markers, or UI elements."*
- **4. Medium & Lighting** : *"Rendered in the style of a traditional oil painting with gritty realism. Masterful top-down lighting emphasizes depth by casting stark, realistic drop shadows from walls, trees, or ruins, visually separating heights while keeping the ground textures highly readable."*
- **5. Full Canvas Cohesion** : *"The map extends cleanly and sharply to the very borders of the image. The entire frame is filled with actionable, playable terrain. Every square inch of the map must feature distinct textures and purposeful details."*

## 🛠️ Quel Est le Protocole Opérationnel d'Exécution ?

L'agent analyse le site (sanctuaire, pont, auberge fortifiée, catacombes, clairière), découpe les zones tactiques majeures (Zones A, B, C, D), formule le prompt selon les 5 points de la Cartography Formula, exécute `generate_image` (`AspectRatio: "16:9"`), et insère la carte dans la fiche de lieu Obsidian couplée au schéma Mermaid de circulation.
Source : `Prompt d'Henri Jamet (Charte Cartographique Asharde Top-Down 90° 16:9)`
```text
1. Réception du lieu (sanctuaire, pont, auberge fortifiée, catacombes, clairière rituelle).
2. Définition des zones tactiques (Zone A, Zone B, Zone C, Zone D).
3. Assemblage du prompt selon les 5 points de la Cartography Formula.
4. Génération de l'image via generate_image avec AspectRatio: "16:9".
5. Sauvegarde dans _attachments/ et intégration dans la note de lieu Obsidian couplée au schéma Mermaid.
```

## 🔄 Comment Appliquer la Boucle d'Auto-Évolution /learn à Taille Constante (Rasoir d'Ockham) ?

À chaque retour, critique ou rejet d'Henri sur une battlemap (proportions tactiques, lisibilité des obstacles, ombres portées), l'agent déclenche immédiatement une passe `/learn` sur cette note pour condenser ou affiner les règles sans inflation de taille ($\le 100$ lignes).
Source : `C:\Users\Public\aivc\dream_inbox_archive\Directive_Dream_2026-11-04_Skills_Intra_Projet_et_Inspections_Recurrentes.md:L20-L22`
```text
Chaque fois qu'Henri émet un commentaire, une critique ou un rejet lors de la validation d'une tâche ayant utilisé un skill [...], l'agent doit déclencher une passe réflexive de type /learn sur la note du skill concerné : identifier la règle manquante, modifier et affiner sans inflation de taille.
```
