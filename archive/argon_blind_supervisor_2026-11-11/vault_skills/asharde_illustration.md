---
created: 2026-11-04
updated: 2026-11-04
type: skill
tags:
  - skill
  - jdr
  - asharde
  - illustration
  - image
---

# 🎨 Comment Générer des Illustrations Artistiques pour l'Univers d'Asharde selon la Master Formula 16:9 ?

Ce skill régit la génération d'illustrations réalistes, sombres et immersives au format **paysage (16:9)** pour l'univers du jeu de rôle Asharde (personnages, PNJ, créatures, artefacts et scènes narratives), à intégrer directement dans les notes Obsidian et fiches Harpy.

## 📐 Quels Sont les Invariants de Rendu et de Cadrage pour Asharde ?

Toute illustration pour Asharde est générée via l'outil natif `generate_image` au format paysage strict **16:9** (`AspectRatio: "16:9"`), enregistrée dans `_attachments/` et référencée sous la forme `![[Nom Image.png]]` avec sa légende en italique sur la ligne suivante.
Source : `Prompt d'Henri Jamet (Charte Graphique Asharde Master Formula 16:9)`
```text
Toute génération d'image dans le cadre d'Asharde est réalisée via l'outil natif generate_image.
Format obligatoire : AspectRatio: "16:9". L'image est enregistrée dans _attachments/ et intégrée sous la forme ![[nom_image.png]] dans la note Obsidian.
```

## ⚙️ Quels Sont les 7 Piliers de l'Asharde Master Formula ?

Chaque prompt envoyé au modèle de génération doit strictement intégrer les sept blocs stylistiques en anglais :
- **1. Medium & Style** : *"A masterful traditional oil painting of [SUBJECT], with extreme grounded realism. The medium is defined by **distinct, visible, and dynamic directional brushstrokes** that define form and atmosphere. There is minimal emphasis on raw canvas texture or excessively thick impasto; the focus is on the action of the paint application itself. Masterful chiaroscuro lighting."*
- **2. Diversity in Entities & Appearance (CRITICAL — True 50/50 Random Roll)** : *"Before composing the portrait, if gender, age, or facial traits are not fixed by the entity's lore (e.g., generic class archetype or unnamed NPC), perform an explicit random roll enforcing strict 50/50 female/male parity, varied age brackets (young, prime, middle-aged, elderly), diverse body builds (lean, athletic, stout, stocky, heavy-set), and distinct facial bone structures, hair textures, and grooming tied to their role. Never default to a repetitive gaunt, stubbled thirty-something brown-haired man."*
- **3. Emotional Resonance** : *"The image must convey a powerful, visceral emotion specific to the grim world of Asharde (e.g., profound dread, heavy melancholy, paranoia, abandonment, sorrow, or manic fanatic zeal). Every brushstroke, shadow, and facial expression must amplify this specific feeling."*
- **4. Dynamic Framing & Camera** : *"Captured in a tight, dynamic close-up from a dramatic [CHOOSE ONE: low angle / high angle / slightly tilted angle]. The composition is claustrophobic and asymmetrical, cropping out the lower body to create intense tension."*
- **5. Internal Depth & Absolute Focus (CRITICAL)** : *"The subject's face/eyes AND their primary interacting element (e.g., weapon, hands, artifact) MUST BOTH remain tack-sharp and highly detailed in the focal plane. DO NOT blur the main character's face, head, or core body. Show extreme wear, soot, and realistic textures on these sharp elements where applicable. The outer extremities (legs, trailing edges of clothing) soften and dissolve into the colorful background void."*
- **6. The Background (The Void)** : *"The background is a complex, turbulent atmospheric void of rich, non-descript colors, formed by **sweeping, masterful brushstrokes**. The dominant color palette should be **varied from image to image**, drawing from colors such as: [SELECT 3-4 DISTINCT AND VARIED COLORS e.g., deep verdigris, royal violet, rusty sienna, cold cerulean]. It is completely devoid of detailed scenery, landscapes, or recognizable environments."*
- **7. The Foreground (Depth Push)** : *"In the extreme foreground, heavily blurred, dark masses of **distinctly painted shadows** and suggestions of indistinct textures frame the composition, pushing the sharp subject deeper into the colorful chaos."*

## 🛠️ Quel Est le Protocole Opérationnel d'Exécution ?

L'agent reçoit le sujet (PNJ, monstre, artefact), sélectionne aléatoirement la palette de 3 à 4 couleurs contrastées du vide et l'émotion viscérale du monde d'Asharde, assemble le prompt selon les 7 points de la Master Formula, exécute `generate_image` (`AspectRatio: "16:9"`), puis insère le wikilink canonique dans la note Obsidian ou la fiche Harpy.
Source : `Prompt d'Henri Jamet (Charte Graphique Asharde Master Formula 16:9)`
```text
1. Réception du sujet (PNJ, monstre, artefact, lieu en gros plan).
2. Sélection aléatoire des couleurs dominantes et de l'émotion viscérale.
3. Assemblage du prompt selon les 7 points de la Master Formula.
4. Génération de l'image via generate_image avec AspectRatio: "16:9".
5. Sauvegarde dans _attachments/ et référencement propre dans la fiche.
```

## 🔄 Comment Appliquer la Boucle d'Auto-Évolution /learn à Taille Constante (Rasoir d'Ockham) ?

À chaque retour, critique ou rejet d'Henri sur une illustration générée pour Asharde (sur le rendu des visages, le contraste du chiaroscuro ou la gestion du vide atmosphérique), l'agent déclenche immédiatement une passe `/learn` sur cette note pour fusionner et condenser les directives sans inflation de taille ($\le 110$ lignes).
Source : `C:\Users\Public\aivc\dream_inbox_archive\Directive_Dream_2026-11-04_Skills_Intra_Projet_et_Inspections_Recurrentes.md:L20-L22`
```text
Chaque fois qu'Henri émet un commentaire, une critique ou un rejet lors de la validation d'une tâche ayant utilisé un skill [...], l'agent doit déclencher une passe réflexive de type /learn sur la note du skill concerné : identifier la règle manquante, modifier et affiner sans inflation de taille.
```
