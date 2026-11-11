---
tags:
  - sem
  - design
  - web
created_at: 2026-11-09
updated_at: 2026-11-09
Image: "[[design affiche culturelle sem.jpg]]"
---

# 🎨 Quelle Charte Graphique et Cinétique « Anti-IA » Gouverne le Site de l'Association SEM ?

![[design affiche culturelle sem.jpg]]
*Figure 1 : Charte éditoriale « Affiche Culturelle Engagée & Fil Conducteur » de l'Association SEM (Succès Égalité Mixité).*

> [!NOTE] 📑 Rattachement Projet & Révision Interactive
> - Note maîtresse : [[notes/Refonte du site WordPress de SEM|Refonte du site WordPress de SEM]]
> - Artéfact commentable : [[_agents/project_diffs/🤖 Design et Identite Visuelle SEM|🤖 Diff Design et Identité Visuelle SEM]]

---

## 🏛️ Pourquoi bannir les codes visuels génériques des IA au profit d'une affiche culturelle suisse ?

Pour éviter l'esthétique standardisée des sites générés par IA et offrir une lecture limpide au corps enseignant, aux directions d'écoles (3H-11H HarmoS) et aux partenaires institutionnels, le site adopte les codes de l'affiche culturelle engagée romande : grands aplats francs, contrastes typographiques marqués, filets de `1 px` en couleur courante et grille asymétrique à 12 colonnes façon revue. Toute carte blanche arrondie (`rounded-2xl` / `rounded-3xl`), ombre portée diffuse (`box-shadow`), pilule décorative, icône superflue ou emoji dans l'interface publique est formellement proscrite (rayon maximal de `0` à `2 px` sur les champs de saisie).

Source : `Prompt d'Henri Jamet (Chat 09/11/2026)`
> Annabelle m'a souvent fait remarquer que les sites générés par IA sont très reconnaissables en tant que telle : Tu peux me créer un DESIGN vraiment original et pertinent, sortir des sentiers battus, favoriser la lecture pour le public cible tout en étant aussi original, moderne et clair que possible ! [...] Style Affiche Culturelle Engagée : contrastes encore plus marqués (aplats vifs inspirés des affiches suisses du 14 juin / festivals culturels), filets typographiques fins et mise en page asymétrique façon magazine.

---

## 🎨 Quelles couleurs franches et quels couples typographiques rythment chaque section ?

Chaque chapitre de la page unique occupe un aplat plein-écran doté de ses propres variables CSS (`--bg`, `--ink`, `--ink-2`, `--rule`, `--accent`) garantissant un contraste de lecture élevé (WCAG AA/AAA), tandis que le logo officiel original `Logo_SEM.png` est affiché seul, sans jamais lui accoler de texte HTML. Les titres d'affiche utilisent la police variable **Archivo** (`wdth 75`, `wght 800`, interligne serré `0.92`, et surtitres capitales `wdth 112` espacés à `0.28em` en écho au logo SEM) associée à **Atkinson Hyperlegible Next** (`1.125rem`, interligne `1.6`, `62–68` caractères par ligne) pour un confort de lecture optimal.

Source : `https://sem-association.ch/wp-content/uploads/Logo_SEM.png` & `[PublicSiteView.tsx](file:///C:/Users/Jamet/Documents/code/sem-association/src/components/public/PublicSiteView.tsx)`
```text
S1 Ouverture & Logo officiel : fond #EB6A39 (orange SEM) | encre #1A1310 | accent fil #FFF4E8
S2 Mission officielle : fond #F4EEE3 (papier craie) | encre #1A1310 | accent #9A3412 (contraste 15.89:1)
S3 Comprendre & Valeurs (sélecteur gauche/droite) : fond #16324F (bleu outremer) | encre #F7F1E6 | accent #F2B33D (11.65:1)
S4 École obligatoire 3H-11H : fond #F2B33D (ocre solaire) | encre #1A1310 | accent #16324F (9.86:1)
S5 Réserver un atelier scolaire : fond #0B4F42 (vert sapin profond) | encre #F7F1E6 | accent #F2B33D (8.45:1)
S6 Équipe & Co-fondatrices : fond #4B2470 (prune engagé) | encre #F7F1E6 | accent #F2B33D (10.46:1)
S7 Événements culturels & 14 Partenaires : fond #E9E1CE (sable éditorial) | encre #1A1310 | accent #0B4F42 (14.09:1)
S8 Soutenir SEM & Adhérer : fond #8E1B30 (carmin affiche) | encre #FFF7EE | accent #F2B33D (8.42:1)
S9 Contact & Pied de page : fond #1A1310 (encre noire) | encre #F7F1E6 | accent #EB6A39 (16.32:1)
```

---

## 🌊 Comment fonctionnent le Fil Conducteur réactif à la souris et le Ruban TOC latéral gauche ?

Le site supprime toute barre d'en-tête horizontale au profit d'un unique bouton discret `Connexion` en haut à droite (menant à la page de login unifiée des trois portails privés) et d'un **ruban vertical de navigation (TOC)** fixé sur le bord gauche, qui s'élargit avec fluidité au survol pour révéler les chapitres numérotés (`01` à `09`) et fait défiler la page vers la section choisie ou ouvre les tiroirs détaillés des cycles `3-4H`, `7-8H` et `10-11H`. En arrière-plan (`<canvas>` 2D dédié respectant `prefers-reduced-motion`), une trame subtile d'ondes horizontales et un **Fil Conducteur** vectoriel continu (courbe de Catmull-Rom amortie par ressort) traversent toutes les sections colorées, ondulent délicatement à l'approche du curseur de la souris et déclenchent par dévoilement franc l'ouverture typographique des blocs — notamment le sélecteur interactif à deux colonnes inspiré d'`obsidian.md/sync` (liste à gauche, détail animé à droite).

Source : `Prompt d'Henri Jamet (Chat 09/11/2026)` & `https://obsidian.md/sync`
> Thème « Ondes & Fil Conducteur » : un fil/ruban vectoriel continu qui traverse verticalement toutes les sections colorées, ondule subtilement à l'approche du curseur et relie visuellement les animations d'ouverture de chaque bloc. [...] Quid de ne pas avoir d'en-tête, si ce n'est le bouton de login et d'utiliser un ruban de navigation élégant sur le côté gauche, comme une TOC qui fait défiler la page au clic avec une agréable animation ?
