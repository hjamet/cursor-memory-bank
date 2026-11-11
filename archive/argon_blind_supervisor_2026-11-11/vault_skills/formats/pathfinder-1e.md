# ⚔️ Comment Structurer la Fiche Harpy en Texte Pur pour Pathfinder 1e ?

Cette note définit le **gabarit textuel canonique du Bloc 5** (fiche d'entité Harpy) pour le système **Pathfinder 1ère Édition**. 

Harpy ne gérant pas le formatage Markdown, cette fiche est rédigée en **texte pur strict**, enrichie d'émojis repères, optimisée pour un repérage visuel instantané en cours de combat sur écran ou smartphone.

---

## 🎯 Quels sont les principes d'affichage en texte pur pour Harpy ?

- **Ordre d'usage tactique en combat** :
  1. Identité & FP
  2. Défense (CA, contact, dépourvu, PV, JS, immunités)
  3. Tactique & Initiative (Init, Vitesse, Sens)
  4. Attaques & Capacités spéciales (toucher, dégâts, sous-ligne explicative)
  5. Sorts & Pouvoirs (NLS, DD, sorts préparés avec détails opérationnels)
  6. Compétences clés & Langues
  7. Caractéristiques principales, BBA, BMO, DMD
  8. Dons
  9. Équipement de combat & Richesse
- **Lignes courtes** : Maximum ~60 caractères par ligne (plafond strict : 70 caractères).
- **Émojis visuels en tête de bloc** : Un émoji thématique distinctif en début de chaque rubrique majeure.
- **Descriptions opérationnelles en sous-lignes (« ↳ »)** :
  Pour chaque attaque spéciale, capacité ou sort important, ajouter immédiatement sous la ligne principale une sous-ligne débutant par « ↳ » précisant en texte concis :
  * Type d'action (1 action simple, complexe, rapide, etc.)
  * Portée ou zone d'effet (contact, 7,5 m, cône 4,5 m, etc.)
  * Durée (instantané, 1 round, etc.)
  * Jet de sauvegarde et DD (Vol annule DD 13, Réf demi DD 13, etc.)
  * Effet concret opérationnel compréhensible d'un coup d'œil par le MJ.
- **Bannissement formel du balisage Markdown** :
  - Zéro tableau Markdown (`|`) — illisibles et inexploitables sur Harpy.
  - Zéro gras (`**` ou `__`).
  - Zéro titre (`#`).
  - Zéro balise de code ou backtick (`` ` ``).
  - Zéro lien Markdown ou Wikilink (`[[...]]` ou `[...]`).
  - Zéro chevron de citation (`>`).
  - Zéro case à cocher (`- [ ]`).
  - Apostrophes et tirets simples pleinement autorisés.

---

## 📋 Quel est le gabarit canonique en texte pur pour Pathfinder 1e ?

```text
👤 IDENTITÉ
[Nom] / FP [FP] ([XP] px)
[Race/Peuple] [Classe] [Niveau] / [Alignement]

🛡️ DÉFENSE
CA [Total] (contact [Contact], dépourvu [Dépourvu])
Détail CA : +[X] armure, +[X] bouclier, +[X] Dex
PV [Total] ([DV] dés de vie)
Sauvegardes : Vig +[X], Réf +[X], Vol +[X]
Immunités / RD : [Détails ou Aucune]

⚡ TACTIQUE
Initiative : +[X]
Vitesse : [X] m
Sens : Perception +[X], [Vision]

⚔️ ATTAQUES
Corps à corps : [Arme] +[X] ([Dégâts] / [Crit])
Distance : [Arme] +[X] ([Dégâts] / [Crit], portée [X] m)
Attaque spéciale : [Nom] ([Dégâts/Effet], DD [X], [X]/j)
↳ [Action], [portée/zone], [durée]. [Effet concret / condition].

🔮 SORTS & POUVOIRS
NLS [X], DD base [X] + niveau
Niv 1 ([X]/j, DD [X]) :
- [Sort 1] (DD [X])
  ↳ [Action], [portée], [durée], [JS]. [Effet opérationnel].
- [Sort 2]
  ↳ [Action], [portée], [durée]. [Effet opérationnel].
Niv 0 ([X] à volonté) :
- [Sort 0-1] : [Action], [portée]. [Effet opérationnel court].
- [Sort 0-2] : [Action], [portée]. [Effet opérationnel court].
Pouvoirs magiques / domaine :
- [Pouvoir 1] ([X]/j)
  ↳ [Action], [portée]. [Effet opérationnel].

🎯 COMPÉTENCES
[Compétence 1] +[X], [Compétence 2] +[X]
Perception +[X], Premiers secours +[X]
Langues : [Langue 1], [Langue 2]

📊 CARACTÉRISTIQUES
FOR [Val] (+[Mod]) / DEX [Val] (+[Mod]) / CON [Val] (+[Mod])
INT [Val] (+[Mod]) / SAG [Val] (+[Mod]) / CHA [Val] (+[Mod])
BBA +[X] / BMO +[X] / DMD [X]

🎖️ DONS
[Don 1], [Don 2], [Don 3]

🎒 ÉQUIPEMENT DE COMBAT
Armes : [Arme 1, Arme 2 avec munitions]
Protections : [Armure, Bouclier]
Consommables : [Potions, parchemins]
Divers : [Clés, missives, bourse [X] po]
```

---

## 🛡️ Quel est un exemple complet prêt à l'emploi (Shanwen, FP 1/2) ?

```text
👤 IDENTITÉ
Shanwen / FP 1/2 (200 px)
Humain (Chélaxien) prêtre d'Asmodéus 1 / Loyal Mauvais

🛡️ DÉFENSE
CA 18 (contact 9, pris au dépourvu 18)
Détail CA : +9 harnois de plates, -1 Dex
PV 14 (1d8+6 Con et Robustesse)
Sauvegardes : Vig +4, Réf -1, Vol +4
Immunités : Aucune

⚡ TACTIQUE
Initiative : -1
Vitesse : 6 m (encombré par harnois)
Sens : Perception +3, vision normale

⚔️ ATTAQUES
Masse d'armes lourde : +1 (1d8+1 / x2)
Arbalète lourde de toit taille G : -3 (2d6 / 19-20, 36 m)
↳ Fixée au chariot. Arme à 2 mains (-2 attaque). Action complexe recharg.
Trait de feu : contact distance -1 (1d6 feu, 9 m, 5/j)
↳ 1 action simple, rayon ardent d'énergie infernale (domaine Feu).
Canalisation d'énergie négative : 1d6 négatif (Vol DD 10 demi, 3/j)
↳ 1 action simple, explosion 9 m. Blesse vivants ou soigne morts-vivants.
Toucher de la Loi : contact +1 (5/j)
↳ 1 action simple, 1 rd. Cible traite tous ses d20 comme un résultat 11.

🔮 SORTS (NLS 1, DD base 12 + niveau)
Niv 1 (2+1/j) :
- Injonction (DD 13)
  ↳ 1 action simple, 7,5 m, 1 rd, Vol annule. Cible obéit à 1 ordre :
    approche, lâche, tombe, fuis ou arrête-toi.
- Mains brûlantes (DD 13, domaine Feu)
  ↳ 1 action simple, cône 4,5 m, instantané, Réf demi. 1d4 dégâts feu.
- Soins légers
  ↳ 1 action simple, contact, instantané. Rend 1d8+1 pv à 1 vivant.
Niv 0 (3 à volonté) :
- Lumière : 1 action simple, contact, 10 min. Objet brille (torche 6 m).
- Réparation : 10 min, contact. Répare 1d4 pv d'objet brisé < 0,5 kg.
- Stabilisation : 1 action simple, 7,5 m. Stabilise 1 mourant à 0 pv.
Domaines : Feu (Flammes infernales), Loi (Tyrannie)

🎯 COMPÉTENCES
Connaissances (plans) +5, Connaissances (religion) +5
Perception +3, Premiers secours +6
Langues : commun, infernal

📊 CARACTÉRISTIQUES
FOR 12 (+1) / DEX 8 (-1) / CON 14 (+2)
INT 13 (+1) / SAG 15 (+2) / CHA 10 (+0)
BBA +0 / BMO +1 / DMD 10

🎖️ DONS
Port des armures lourdes (prêtre), Robustesse

🎒 ÉQUIPEMENT DE COMBAT
Masse d'armes lourde, arbalète de toit (10 carreaux)
Harnois complet de plates, symbole sacré en bois
Clés du chariot de transport et des menottes
Lettre scellée du maire Arvanxi
```
