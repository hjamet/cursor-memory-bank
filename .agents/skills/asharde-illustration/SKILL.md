---
name: asharde-illustration
description: "Génération d'illustrations artistiques immersives 16:9 pour l'univers de JDR Asharde selon la Master Formula."
---
# 🎨 Asharde Illustration — The Visual Architect (Master Formula 16:9)

Ce skill permet à Antigravity d'orchestrer et de générer des illustrations réalistes et sombres au format **paysage (16:9)** pour l'univers du jeu de rôle Asharde, à intégrer directement dans les notes Obsidian (dossiers de campagne, fiches créatures, PNJ, lieux).

> [!IMPORTANT]
> **EXÉCUTION DU PROCESSUS GÉNÉRATIF** :
> Toute génération d'image dans le cadre d'Asharde est réalisée via l'outil natif `generate_image`.
> 
> **Format obligatoire** : `AspectRatio: "16:9"`. L'image est enregistrée dans `_attachments/` et intégrée sous la forme `![[DossierCampagne/_attachments/nom_image.png]]` dans la note Obsidian et `![Description](file:///...)` dans le chat.

---

## 📐 Directives de Format & Rendu

1. **Format Paysage Systématique** : Format paysage **`16:9`** (`AspectRatio: "16:9"`).
2. **Présentation dans les Notes & Chat** : L'agent incorpore le lien Markdown ou Wikilink valide directement dans la note Obsidian cible et dans la restitution au fil de l'eau.

---

## ⚙️ The Asharde Master Formula (7 Points)

Chaque prompt envoyé au modèle de génération doit strictement respecter l'architecture stylistique suivante en anglais :

### 1. Medium & Style
> "A masterful traditional oil painting of [SUBJECT], with extreme grounded realism. The medium is defined by **distinct, visible, and dynamic directional brushstrokes** that define form and atmosphere. There is minimal emphasis on raw canvas texture or excessively thick impasto; the focus is on the action of the paint application itself. Masterful chiaroscuro lighting."

### 2. Diversity in Entities & Appearance (CRITICAL)
> "Characters should vary significantly in age, gender, body type (lean, athletic, stout, etc.), and cleanliness. A character's appearance should be a direct result of their role and history (e.g., a seasoned ranger might be grimy, but a city priest would be clean-shaven in well-kept robes). Do not default to a single, repetitive type. Avoid clichés of unkempt and gaunt figures unless specified by the role."

### 3. Emotional Resonance
> "The image must convey a powerful, visceral emotion specific to the grim world of Asharde (e.g., profound dread, heavy melancholy, paranoia, abandonment, sorrow, or manic fanatic zeal). Every brushstroke, shadow, and facial expression must amplify this specific feeling."

### 4. Dynamic Framing & Camera
> "Captured in a tight, dynamic close-up from a dramatic [CHOOSE ONE: low angle / high angle / slightly tilted angle]. The composition is claustrophobic and asymmetrical, cropping out the lower body to create intense tension."

### 5. Internal Depth & Absolute Focus (CRITICAL)
> "The subject's face/eyes AND their primary interacting element (e.g., weapon, hands, artifact) MUST BOTH remain tack-sharp and highly detailed in the focal plane. DO NOT blur the main character's face, head, or core body. Show extreme wear, soot, and realistic textures on these sharp elements where applicable. The outer extremities (legs, trailing edges of clothing) soften and dissolve into the colorful background void."

### 6. The Background (The Void)
> "The background is a complex, turbulent atmospheric void of rich, non-descript colors, formed by **sweeping, masterful brushstrokes**. The dominant color palette should be **varied from image to image**, drawing from colors such as: [SELECT 3-4 DISTINCT AND VARIED COLORS e.g., deep verdigris, royal violet, rusty sienna, cold cerulean]. It is completely devoid of detailed scenery, landscapes, or recognizable environments."

### 7. The Foreground (Depth Push)
> "In the extreme foreground, heavily blurred, dark masses of **distinctly painted shadows** and suggestions of indistinct textures frame the composition, pushing the sharp subject deeper into the colorful chaos."

---

## 🛠️ Protocole Opérationnel

1. Réception du sujet (PNJ, monstre, artefact, lieu en gros plan).
2. Sélection aléatoire des couleurs dominantes et de l'émotion viscérale.
3. Assemblage du prompt selon les 7 points de la Master Formula.
4. Génération de l'image via `generate_image` avec `AspectRatio: "16:9"`.
5. Sauvegarde dans `_attachments/` et référencement propre dans la fiche.
