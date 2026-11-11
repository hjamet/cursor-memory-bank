# 🎲 Comment Structurer la Fiche Harpy en Texte Pur pour Système Propriétaire (Asharde) ?

Cette note définit le **gabarit textuel canonique du Bloc 5** (fiche d'entité Harpy) pour les **systèmes propriétaires ou univers sur-mesure (ex: Asharde)**.

Harpy ne gérant pas le formatage Markdown, cette fiche est rédigée en **texte pur strict**, enrichie d'émojis repères, optimisée pour un repérage visuel instantané en cours de combat sur écran ou smartphone.

---

## 🎯 Quels sont les principes d'adaptation pour les systèmes personnalisés ?

- **Ordre d'usage tactique en combat** :
  1. Identité, Rang / Échelon & Archétype
  2. Défense (Protection/Blindage, Vitalité/Blessures, Résistance mentale)
  3. Tactique & Réactivité (Initiative, Déplacement, Vigilance)
  4. Actions martiales (Attaques principales, manoeuvres, ripostes avec détails)
  5. Pouvoirs, Flux ou Magie (Réserves de ressources, capacités d'impact détaillées)
  6. Talents, Maîtrises & Savoirs
  7. Attributs fondamentaux
  8. Particularités & Traits singuliers
  9. Matériel actif, Ressources & Clés
- **Lignes courtes** : Maximum ~60 caractères par ligne (plafond strict : 70 caractères).
- **Émojis visuels en tête de bloc** : Repérage immédiat.
- **Descriptions opérationnelles en sous-lignes (« ↳ »)** :
  Pour chaque manoeuvre martiale, riposte réflexe, flux ou pouvoir majeur, insérer une sous-ligne « ↳ » spécifiant :
  * Déclenchement / Type d'action (action standard, réaction réflexe, coût en ressource)
  * Portée, zone d'impact ou condition
  * Difficulté ou seuil d'opposition (DD / test opposé)
  * Conséquence directe sur le champ de bataille (dégâts nets, état, malus).
- **Bannissement formel du balisage Markdown** :
  - Zéro tableau Markdown (`|`).
  - Zéro gras (`**` ou `__`).
  - Zéro titre (`#`).
  - Zéro balise de code ou backtick (`` ` ``).
  - Zéro lien Markdown ou Wikilink (`[[...]]` ou `[...]`).
  - Zéro chevron de citation (`>`).
  - Zéro case à cocher (`- [ ]`).

---

## 📋 Quel est le gabarit canonique en texte pur pour Système Propriétaire ?

```text
👤 IDENTITÉ
[Nom] / Rang [Rang/Niveau]
[Origine/Peuple] [Archétype/Rôle] / [Faction/Allégeance]

🛡️ DÉFENSE
Blindage / Protection : [Valeur] ([Détail armure])
Vitalité / Seuil de blessure : [Total] PV ([Seuils])
Sang-froid / Résistance mentale : [Valeur]
Vulnérabilités / Défenses : [Détails ou Aucune]

⚡ TACTIQUE
Réactivité / Initiative : [Valeur]
Déplacement : [Valeur] m par tour
Vigilance / Instinct : [Valeur]

⚔️ ACTIONS MARTIALES
Frappe principale : [Arme] ([Impact/Dégâts], précision [Bonus])
Tir / Distance : [Arme distance] ([Dégâts], portée [X] m)
Manoeuvre réflexe : [Nom]
↳ [Coût/Action], [portée]. [Effet tactique / test requis].
Riposte tactique : [Condition]
↳ [Déclencheur]. [Conséquence mécanique].

🔮 FLUX & POUVOIRS
Réserve d énergie / Éther : [Total] points
Pouvoir majeur : [Nom]
↳ Coût [X] pts, portée [X], DD [X]. [Effet concret en jeu].
Pouvoir mineur : [Nom]
↳ Coût [X] pts. [Effet concret court].

🎯 TALENTS & SAVOIRS
[Talent 1] (Rang [X]), [Talent 2] (Rang [X])
Connaissances : [Domaine 1], [Domaine 2]
Langages : [Langue 1], [Langue 2]

📊 ATTRIBUTS CLÉS
Corps [Val] / Esprit [Val] / Instinct [Val] / Aura [Val]
Puissance motrice : [Valeur]

🎖️ PARTICULARITÉS
[Anomalie / Trait singulier 1]
[Manie / Particularité tactique 2]

🎒 MATÉRIEL ACTIF
Armes en main : [Armes équipées et munitions]
Accessoires utiles : [Outils de terrain, alchimie]
Ressources : [Jetons de faction, clés scellées, monnaies]
```

---

## 🛡️ Quel est un exemple complet prêt à l'emploi (Sentinelle Varek, Rang 2) ?

```text
👤 IDENTITÉ
Sentinelle Varek / Rang 2 (Élite)
Né-de-Roche Gardien / Ligue du Bastion

🛡️ DÉFENSE
Blindage lourd : 4 (cuirasse rivetée et bouclier pavois)
Vitalité : 28 PV (Seuil de blessure grave à 14 PV)
Sang-froid : 3 (inébranlable face à la panique)
Résistances : Résiste aux impacts contondants (-1 dégât)

⚡ TACTIQUE
Réactivité : 2
Déplacement : 5 m (ralenti par le pavois)
Vigilance : 3 (instinct du guetteur)

⚔️ ACTIONS MARTIALES
Masse à ailettes : Précision +3 (Impact 2d6+2 brut)
Pavois d'arrêt : Blocage réflexe
↳ Réaction face à 1 frappe au contact. Confère +2 Blindage.
Charge lourde : Renversement
↳ Action de déplacement + frappe. Cible renversée si échec test Corps.

🔮 FLUX & POUVOIRS
Réserve de Vigueur : 4 points
Frappe tellurique
↳ Coût 1 vig, onde de choc 3 m, DD 12. Renverse et inflige 1d6 brut.

🎯 TALENTS & SAVOIRS
Bouclier d équipe (Rang 2), Intimidation (Rang 2)
Topographie des faubourgs (Rang 1)
Langages : chélois, dialecte des mines

📊 ATTRIBUTS CLÉS
Corps 4 / Esprit 2 / Instinct 3 / Aura 1

🎖️ PARTICULARITÉS
Discipline d'acier : ne rompt jamais sa formation sans ordre
Marque du serment : cicatrice rituelle sur l'avant-bras

🎒 MATÉRIEL ACTIF
Masse à ailettes d'acier noir, pavois aux armes du Bastion
Fiole d'huile anti-rouille, corde de chanvre 15 m
Plaque matricule en laiton, clé du dépôt de garnison
```
