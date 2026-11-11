---
created: 2026-11-04
updated: 2026-11-04
type: skill
tags:
  - skill
  - image
  - illustration
  - visual
---

# 🎨 Comment Générer et Intégrer des Visuels 16:9 dans le Coffre Obsidian et les Projets d'Henri ?

Ce skill régit la conception, l'orchestration et l'intégration de toute image ou illustration générée pour les notes du coffre Obsidian et les différents projets d'Henri Jamet.

## 📐 Quels Sont les Invariants de Format et de Stockage dans le Coffre Obsidian ?

Toute génération d'image s'exécute via l'outil natif `generate_image` au format paysage strict **16:9** (`AspectRatio: "16:9"`), avec enregistrement physique dans le dossier `_attachments/` (nom de fichier avec espaces uniquement, sans caractères spéciaux superflus).
Source : `c:\Users\Jamet\Documents\VoiceNotes\_agents\rules\coffre-obsidian.md:L30-L37`
```text
Chaque note ou sous-note pérenne reçoit sa propre illustration originale (generate_image) dans _attachments/ (espaces uniquement, nom de fichier seul sans chemin), déclarée en YAML (Image: "[[Nom Image.jpg]]") et sous le H1 (![[Nom Image.jpg]]) avec légende en italique dessous. Deux notes ne partagent jamais la même image.
```

- **Déclaration Frontmatter** : `Image: "[[Nom Image.png]]"`.
- **Intégration sous le H1** : `![[Nom Image.png]]` suivi de la légende en italique sur la ligne immédiatement suivante (`*Légende du visuel...*`).
- **Unicité Stricte** : Deux notes ne partagent jamais la même image. Une note créée ou scindée reçoit obligatoirement son visuel dédié.

## 🎯 Quels Sont les Trois Modes Visuels Canoniques selon le Type de Projet ?

### 🖌️ Comment Générer une Illustration Artistique ou un Portrait JDR ?
Pour les personnages, monstres, scènes narratives ou ambiances de jeu de rôle (Asharde, Le Conseil des Voleurs, Vampire V5), le prompt mobilise une esthétique de peinture à l'huile traditionnelle ultra-réaliste avec touches de pinceau dynamiques visibles et éclairage contrasté au chiaroscuro. Pour l'univers d'Asharde en particulier, appliquer la Master Formula en 7 points définie dans [[skills/asharde_illustration|Illustrations Artistiques Asharde]].
Source : `c:\Users\Jamet\Documents\VoiceNotes\skills\asharde_illustration.md`
```text
A masterful traditional oil painting of [SUBJECT], with extreme grounded realism. The medium is defined by distinct, visible, and dynamic directional brushstrokes that define form and atmosphere. Masterful chiaroscuro lighting.
```

### 🗺️ Comment Générer une Battlemap Tactique JDR ?
Pour les lieux d'affrontement, décors tactiques et bâtiments explorables, l'image est générée en vue strictement zénithale à 90° (perspective orthogonale du dessus sans ligne d'horizon), plein cadre bord-à-bord, sans grille artificielle et sans jetons ou personnages figés. Pour l'univers d'Asharde, appliquer la Cartography Formula en 5 points définie dans [[skills/asharde_battlemap|Battlemaps Zénithales Asharde]].
Source : `c:\Users\Jamet\Documents\VoiceNotes\skills\asharde_battlemap.md`
```text
A Tabletop RPG battle map of [LOCATION], viewed from a strict, perfect top-down bird's-eye perspective (90 degrees looking directly down). Orthographic projection. This is a functional floor plan. Absolutely no grids, measuring markers, or UI elements.
```

### 📊 Comment Générer une Infographie Technique ou Scientifique (Formule S.S.V.D.) ?
Pour les projets académiques, techniques ou d'outillage (CLIMB, ORBIT, DLLP, JDR Planner, architectures logicielles), le prompt mobilise la formule **S.S.V.D.** (Schéma Sobre Vectoriel Déterministe) en 2D épurée : aplats de couleurs maîtrisés, contrastes forts, formes géométriques nettes, aucun faux texte ou typo floue générée par l'IA, axée sur la lisibilité des flux, composants ou blocs conceptuels.
Source : `C:\Users\Public\aivc\dream_inbox_archive\Directive_Dream_2026-11-04_Skills_Intra_Projet_et_Inspections_Recurrentes.md:L18-L20`
```text
A clean 2D vector infographic illustrating [CONCEPT / ARCHITECTURE]. Minimalist modern design, sharp geometric contours, flat aesthetic with elegant soft gradients, high contrast on neutral light background, zero pseudo-text or illegible gibberish, technical schematic precision.
```

## 🔄 Comment Appliquer la Boucle d'Auto-Évolution /learn à Taille Constante (Rasoir d'Ockham) ?

Chaque fois qu'Henri émet une critique, un rejet ou un affinement sur un visuel généré (composition, saturation, cadrage, détail superflu), l'agent déclenche immédiatement une passe `/learn` sur la présente note : il identifie l'ajustement requis et fusionne ou condense les directives existantes sans gonfler la taille du fichier ($\le 120$ lignes).
Source : `C:\Users\Public\aivc\dream_inbox_archive\Directive_Dream_2026-11-04_Skills_Intra_Projet_et_Inspections_Recurrentes.md:L20-L22`
```text
Chaque fois qu'Henri émet un commentaire, une critique ou un rejet lors de la validation d'une tâche ayant utilisé un skill [...], l'agent doit déclencher une passe réflexive de type /learn sur la note du skill concerné. Modifier et affiner le skill sans inflation de taille (Rasoir d'Ockham).
```
