# 🐉 Comment Structurer la Fiche Harpy en Texte Pur pour D&D 5e ?

Cette note définit le **gabarit textuel canonique du Bloc 5** (fiche d'entité Harpy) pour le système **Donjons & Dragons 5ème Édition (D&D 5e)**.

Harpy ne gérant pas le formatage Markdown, cette fiche est rédigée en **texte pur strict**, enrichie d'émojis repères, optimisée pour un repérage visuel instantané en cours de combat sur écran ou smartphone.

---

## 🎯 Quels sont les principes d'affichage en texte pur pour D&D 5e ?

- **Ordre d'usage tactique en combat** :
  1. Identité & FP / Facteur de Puissance
  2. Défense (CA, PV, Dés de vie, Sauvegardes, Résistances/Immunités)
  3. Tactique & Initiative (Init, Vitesse, Sens & Perception passive)
  4. Actions d'attaque (Toucher, portée, dégâts et sous-lignes explicatives)
  5. Sorts & Capacités magiques (DD sauvegarde, bonus d'attaque, sorts avec détails)
  6. Compétences clés & Langues
  7. Caractéristiques principales & Bonus de maîtrise
  8. Traits & Dons tactiques
  9. Équipement de combat & Butin
- **Lignes courtes** : Maximum ~60 caractères par ligne (plafond strict : 70 caractères).
- **Émojis visuels en tête de bloc** : Repérage instantané sans lecture intégrale.
- **Descriptions opérationnelles en sous-lignes (« ↳ »)** :
  Pour chaque attaque spéciale, action bonus, réaction ou sort important, ajouter immédiatement une sous-ligne « ↳ » précisant :
  * Type d'action (1 action, action bonus, réaction)
  * Portée ou zone (contact, 18 m, sphère 6 m)
  * Durée et concentration (1 min conc., instantané)
  * Jet de sauvegarde et DD (Dex DD 14 demi, etc.)
  * Effet opérationnel immédiat en jeu.
- **Bannissement formel du balisage Markdown** :
  - Zéro tableau Markdown (`|`).
  - Zéro gras (`**` ou `__`).
  - Zéro titre (`#`).
  - Zéro balise de code ou backtick (`` ` ``).
  - Zéro lien Markdown ou Wikilink (`[[...]]` ou `[...]`).
  - Zéro chevron de citation (`>`).
  - Zéro case à cocher (`- [ ]`).

---

## 📋 Quel est le gabarit canonique en texte pur pour D&D 5e ?

```text
👤 IDENTITÉ
[Nom] / FP [FP] ([XP] px)
[Type de créature/Race] [Classe/Niveau] / [Alignement]

🛡️ DÉFENSE
CA [Total] ([Type d armure ou naturelle])
PV [Total] ([DV] dés de vie)
Sauvegardes : [Carac 1] +[X], [Carac 2] +[X]
Résistances / Immunités : [Détails ou Aucune]

⚡ TACTIQUE
Initiative : +[X]
Vitesse : [X] m
Sens : Perception passive [X], [Vision dans le noir]

⚔️ ACTIONS DE COMBAT
Attaque 1 : [Arme/Attaque] +[X] (dégâts [Dégâts] [Type])
Attaque 2 : [Arme distance] +[X] ([Dégâts], portée [X] m)
Action spéciale : [Nom]
↳ [Type action], [portée], [durée], [JS/DD]. [Effet tactique].
Action bonus : [Capacité / Réflexe]
↳ [Déclencheur / Coût]. [Effet tactique concret].
Réaction : [Parade / Riposte]
↳ [Condition de déclenchement]. [Effet concret].

🔮 SORTS & CAPACITÉS
DD sauvegarde [X], Attaque de sort +[X]
Sorts mineurs (à volonté) :
- [Sort 0] : [Action], [portée]. [Effet opérationnel court].
Niv 1 ([X] emplacements) :
- [Sort 1]
  ↳ [Action], [portée], [durée conc.], [JS/DD]. [Effet concret].
Capacités rechargeables :
- [Pouvoir] (Recharge [X])
  ↳ [Action], [zone/portée], [JS/DD]. [Dégâts et effet].

🎯 COMPÉTENCES
[Compétence 1] +[X], [Compétence 2] +[X]
Langues : [Langue 1], [Langue 2]

📊 CARACTÉRISTIQUES
FOR [Val] (+[Mod]) / DEX [Val] (+[Mod]) / CON [Val] (+[Mod])
INT [Val] (+[Mod]) / SAG [Val] (+[Mod]) / CHA [Val] (+[Mod])
Bonus de maîtrise : +[X]

🎖️ TRAITS SPÉCIAUX
[Trait 1] : [Effet court]
[Trait 2] : [Effet court]

🎒 ÉQUIPEMENT & BUTIN
Armes : [Arme principale, arme secondaire]
Protection : [Armure, écu]
Divers : [Composantes, clés, bourse [X] po]
```

---

## 🛡️ Quel est un exemple complet prêt à l'emploi (Capitaine Valerius, FP 3) ?

```text
👤 IDENTITÉ
Capitaine Valerius / FP 3 (700 px)
Humain Guerrier 5 / Loyal Neutre

🛡️ DÉFENSE
CA 18 (harnois de plates)
PV 52 (8d8+16)
Sauvegardes : For +5, Con +4
Résistances : Aucune

⚡ TACTIQUE
Initiative : +0
Vitesse : 9 m
Sens : Perception passive 12, vision normale

⚔️ ACTIONS DE COMBAT
Attaques multiples : 2 attaques de corps à corps
Épée bâtarde : +5 au toucher (1d10+3 tranchant à 2 mains)
Arbalète lourde : +2 au toucher (1d10 perforant, 30/120 m)
Action bonus : Second souffle (1/repos court)
↳ 1 action bonus. Récupère 1d10+5 PV immédiatement.
Réaction : Parade martiale
↳ Réaction quand touché au contact. Ajoute +2 à la CA.

🔮 CAPACITÉS SPÉCIALES
Sursaut d'activité : 1/repos court
↳ Gratuit lors de son tour. Effectue 1 action supplémentaire.

🎯 COMPÉTENCES
Athlétisme +5, Intimidation +4, Perception +2
Langues : commun

📊 CARACTÉRISTIQUES
FOR 16 (+3) / DEX 10 (+0) / CON 14 (+2)
INT 11 (+0) / SAG 12 (+1) / CHA 12 (+1)
Bonus de maîtrise : +2

🎖️ TRAITS SPÉCIAUX
Commandement tactique (3/jour)
↳ 1 action bonus. Ajoute +1d4 à l'attaque ou sauvegarde d'1 allié (9 m).

🎒 ÉQUIPEMENT & BUTIN
Épée bâtarde en acier trempé, arbalète et 20 carreaux
Harnois de plates de la cité, insigne officiel
Clés du poste de garde, mandat d'arrêt, 25 pièces d'or
```
