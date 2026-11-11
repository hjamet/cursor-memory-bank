# 🗺️ Comment Structurer la Fiche Harpy en 5 Blocs pour un Lieu ou Décor ?

Cette note définit le **gabarit textuel canonique en 5 blocs** pour la création d'un **lieu, décor, bâtiment ou site d'affrontement** dans le coffre Obsidian et l'application **Harpy**.

---

## 🎯 Quels Sont les Principes Spécifiques aux Lieux ?

| Dimension | Règle Stricte | Outil & Protocole |
|---|---|---|
| **Illustration & Ambiance** | Visuel cinématographique 16:9 du site ou de sa façade. | [[skills/asharde_illustration|Illustrations Artistiques Asharde]] (Master Formula 16:9). |
| **Cartographie & Battlemap** | Vue zénithale 90° sans grille, pleine page 16:9. | [[skills/asharde_battlemap|Battlemaps Zénithales Asharde]] (Cartography Formula 16:9). |
| **Simplicité Cartographique** | **Garder autant que possible une seule carte par simplicité** ; ne créer plusieurs cartes que si des étages distincts et indispensables le justifient. | Intégration en tête de la note ou dans la rubrique dédiée des secrets MJ. |
| **Description Externe (Bloc 2)** | Plafond strict de **100 caractères** dans un bloc ````text````. Apparence physique visible extérieure pure (architecture, matériaux, état, lumière). Zéro fonction secrète, zéro nom de faction. | Validation automatique par `harpy_entity_validator.py`. |
| **Ouverture : Improvisation & Vérité MJ** | **Deux sections H2 distinctes en tête** :<br/>1. `## 🎭 Comment l'improviser ?` : Aide immédiate dévoilable avec mots en **gras**.<br/>2. `## 🗝️ Qu'est-ce que ce lieu vraiment ?` : Résumé de l'histoire et secrets de fond ($\ge 350$ car.). | Suivi du H2 des secrets détaillés (accès, pièges, PNJ, butin, destin). |
| **Description Joueurs (Bloc 6)** | **1 ou 2 paragraphes riches ($\ge 450$ car.)** dans un bloc ````markdown````. Évocation de l'ambiance, matières, textures, lumières intrinsèques et synesthésies (odeur de suie, écho de pas, fraîcheur des dalles). Zéro spoil. Description générale et intemporelle du décor (visitable à toute heure, zéro météo éphémère ou action figée). Angle renouvelé via `--tirage`. | Validation automatique par `harpy_entity_validator.py`. |
| **Fiche Harpy (Bloc 7)** | Texte pur strict, max 70 car./ligne, sous-lignes « ↳ » pour chaque piège, porte verrouillée ou effet magique permanent. | Lisible immédiatement en jeu pour l'arbitrage tactique. |

---

## 📋 Quel Est le Gabarit d'Entrée Structuré pour un Lieu ?

```yaml
nom: "Poste de Garde du Pont sur l'Athua"
systeme: "Pathfinder 1e"
image: "pont_athua_vue_ambiance.png"
battlemap: "pont_athua_battlemap_zenithale.png"
description_externe: "Bâtisse basse en pierre de taille grise, flanquée d'une arche voûtée et de meurtrières étroites."

ouverture_mj:
  aide_improvisation: |
    **Maçonnerie austère** battue par les embruns de la rivière. Les dalles de granit sont **humides et glissantes** près du parapet. Deux lanternes à huile en fer forgé diffusent une **lueur jaunâtre** à travers les fentes des volets de chêne bardés de fer.
  resume_mj: |
    Avant-poste avancé contrôlé officieusement par l'Ordre du Chevalet pour surveiller le trafic fluvial et intercepter les fuyards de Couronne d'Ouest. Le sous-sol dissimule une geôle exiguë où transitent les prisonniers avant leur transfert vers la Citadelle de Rivad.

secrets_mj:
  cartographie_tactique: |
    - **Zone A (Tablier du pont)** : Arche pavée de 4 mètres de large, parapets bas (hauteur 90 cm, abri partiel). Risque de chute dans le courant rapide en contrebas (test d'Athlétisme DD 15).
    - **Zone B (Salle de garde)** : Espace clos de 6 × 4 mètres, sol en tomettes, table de chêne massif servant d'abri (+4 CA).
    - **Zone C (Geôle basse)** : Cellule aveugle voûtée sous l'arche, accessible par une trappe métallique verrouillée.
  acces_pieges_obstacles: |
    - **Porte principale** : Chêne ferré renforcé (Solidité 5, 20 pv, crochetage Sabotage DD 20).
    - **Trappe de la geôle** : Grille de fer forgé cadenassée (Solidité 10, 30 pv, clé portée par le sergent, crochetage DD 25).
    - **Meurtrières** : Fentes de tir offrant un abri supérieur (+8 CA, +4 aux réflexes) aux défenseurs intérieurs.
  factions_pnj_presents: |
    - 4 gardes en patrouille tournante armés d'arbalètes et de vouges.
    - 1 sergent instructeur supervisant les relèves de faction.
  tresors_documents: |
    - Registre des passages des chariots civils et réquisitions militaires.
    - Coffret de paie ferré contenant 40 pièces d'argent et les clés de rechange du pont.
  destin_evolution: |
    - En cas d'alerte ou d'embuscade sur la route, la garnison barricade la herse pour couper la traversée.

description_joueurs: |
  L'air frais de la rivière transporte une odeur piquante de limon humide et de feu de tourbe mal éteint. Dressée au coude de la chaussée, la silhouette massive du poste de garde découpe son granit sombre contre la brume du crépuscule. Le clapotis sourd du ruisseau contre les piles du pont se mêle au raclement régulier d'une lame aiguisée derrière les fentes des meurtrières.

  La lueur blafarde d'une lanterne de fer projette des reflets d'huile sur les dalles disjointes du tablier. Rien ne bouge à l'extérieur, mais la tension est palpable : les ferrures massives de la double porte de chêne sont verrouillées de l'intérieur, et l'architecture militaire ne laisse aucun angle mort à qui s'aventure sur le pavé.

bloc_harpy: |
  🏛️ LIEU & LOCALISATION
  Poste de Garde du Pont sur l'Athua / Campagne du Conseil
  Bâtiment fortifié en pierre / Contrôle routier et fluvial
  
  🛡️ DÉFENSES & ACCÈS
  Murs : Pierre de taille 60 cm (Solidité 8, 180 pv, Escalade DD 20)
  Porte principale : Chêne renforcé (Solidité 5, 20 pv, Sabotage DD 20)
  Trappe sous-sol : Fer forgé scellé (Solidité 10, 30 pv, Sabotage DD 25)
  Meurtrières : Abri supérieur (+8 CA, +4 Réflexes, +4 Discrétion)
  
  ⚡ TACTIQUE & TERRAIN
  Dimensions : Bâtisse 6 × 4 m, tablier de pont 4 × 12 m
  Éclairage : Pénombre extérieure, 2 lanternes (lumière 9 m)
  Terrain difficile : Berges boueuses et dalles mouillées (vitesse demi)
  Courant d'eau : Profondeur 1,2 m, emportement 6 m/rd (Athlétisme DD 15)
  
  ⚔️ DANGERS & PIÈGES
  Herse d'arrêt : Déclenchement manuel par levier (1 action simple)
  ↳ Chute de la herse sur 3 m. Inflige 3d6 perforant (Réf DD 15 évite).
  Chute du pont : Hauteur 3 m dans l'eau rapide
  ↳ 1d6 dégâts non-létaux si saut volontaire (Acrobaties DD 15 annule).
  
  🔮 MAGIE & DÉTECTION
  Aura magique : Aucune aura active permanente
  Résonance : Écho acoustique amplifié sous la voûte du pont
  
  🎒 BUTIN & DOCUMENTS
  Registre officiel des transferts cellulaires
  Clés de l'arche et de la geôle sous-fluviale
  Coffre de service scellé : 40 pièces d'argent, 1 potion de soins
```

---

## 🛡️ Quel Est l'Ordre de Rendu dans la Note Finale (v3) ?

1. **Bloc 1** : `![[pont_athua_vue_ambiance.png]]` (ambiance 16:9 `/asharde-illustration`) et `![[pont_athua_battlemap_zenithale.png]]` (battlemap zénithale 90° `/asharde-battlemap`).
2. **Bloc 2** : Bloc ````text```` de description externe visible $\le 100$ caractères.
3. **Bloc 3** : Titre H2 `## 🎭 Comment l'improviser ?` s'ouvrant par le P1 d'aide à l'improvisation avec mots en **gras**.
4. **Bloc 4** : Titre H2 `## 🗝️ Qu'est-ce que ce lieu vraiment ?` s'ouvrant par le P2 ($\ge 350$ caractères) de résumé de fond pour le MJ (histoire, secrets profonds).
5. **Bloc 5** : Titre H2 `## 🔒 Quels sont les secrets MJ...` avec sous-sections H3 (cartographie, accès/pièges, factions, butin, destin).
6. **Bloc 6** : Bloc ````markdown```` de description joueurs (1 ou 2 paragraphes $\ge 450$ caractères, synesthésies, description générale du décor sans scène éphémère).
7. **Bloc 7** : Bloc ````text```` de fiche mécanique Harpy sans balisage Markdown.
