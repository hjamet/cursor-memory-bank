---
name: asharde-battlemap
description: "Génération de battlemaps JDR 16:9 vue zénithale 90° sans grille pour Asharde."
---
# 🗺️ Asharde Battlemap — The Cartographer (Vue Zénithale 90° Sans Grille)

Ce skill permet à Antigravity d'orchestrer et de générer des battlemaps ultra-détaillées, sans grille, sans personnages et en vue strictement zénithale à 90° au format **paysage (16:9)** pour les lieux et décors de jeu de rôle (univers d'Asharde ou univers médiéval fantastique réaliste), à intégrer directement dans les notes Obsidian.

> [!IMPORTANT]
> **EXÉCUTION DU PROCESSUS CARTOGRAPHIQUE** :
> Toute génération de battlemap est réalisée via l'outil natif `generate_image`.
> 
> **Format obligatoire** : `AspectRatio: "16:9"`. L'image est enregistrée dans `_attachments/` et intégrée sous la forme `![[DossierCampagne/_attachments/nom_battlemap.png]]` dans la note Obsidian et `![Description](file:///...)` dans le chat.

---

## 📐 Directives de Format & Rendu

1. **Format Paysage Systématique** : Format paysage **`16:9`** (`AspectRatio: "16:9"`).
2. **Vue Zénithale Strictement à 90° & Sans Grille** : Perspective orthogonale stricte du dessus, sans ligne d'horizon, sans grille et sans créatures ou personnages.
3. **Plein Cadre & Netteté Bord-à-Bord** : Le terrain est jouable et net jusqu'aux quatre coins de l'image.

---

## ⚙️ The Cartography Formula (5 Points)

Chaque prompt envoyé au modèle de génération doit strictement respecter l'architecture suivante en anglais :

### 1. Core Structure & Perspective (CRITICAL)
> "A Tabletop RPG battle map of [LOCATION], viewed from a **strict, perfect top-down bird's-eye perspective (90 degrees looking directly down)**. Orthographic projection. This is a functional floor plan. We are looking directly down at the ground, roofs, floors, or terrain. There is absolutely no visible horizon."

### 2. Extreme Detail, Variety & Originality
> "The environment must be densely packed with intricate, high-resolution details and varied textures. Avoid generic, repetitive layouts. Introduce unique architectural quirks, original environmental storytelling elements, and a rich diversity of props (scattered debris, specific localized tools, distinctive vegetation, uneven terrain) that make the location feel uniquely lived-in, organic, and incredibly real."

### 3. Playability & Layout
> "The layout provides clear, readable spaces where game tokens can be seamlessly placed. The geometry of the walls, floors, and environmental obstacles is perfectly defined from above. Absolutely no grids, measuring markers, or UI elements."

### 4. Medium & Lighting
> "Rendered in the style of a traditional oil painting with gritty realism. Masterful top-down lighting emphasizes depth by casting stark, realistic drop shadows from walls, trees, or ruins, visually separating heights while keeping the ground textures highly readable."

### 5. Full Canvas Cohesion
> "The map extends cleanly and sharply to the very borders of the image. The entire frame is filled with actionable, playable terrain. Every square inch of the map must feature distinct textures and purposeful details."

---

## 🛠️ Protocole Opérationnel

1. Réception du lieu (sanctuaire, pont, auberge fortifiée, catacombes, clairière rituelle).
2. Définition des zones tactiques (Zone A, Zone B, Zone C, Zone D).
3. Assemblage du prompt selon les 5 points de la Cartography Formula.
4. Génération de l'image via `generate_image` avec `AspectRatio: "16:9"`.
5. Sauvegarde dans `_attachments/` et intégration dans la note de lieu Obsidian couplée au schéma Mermaid.
