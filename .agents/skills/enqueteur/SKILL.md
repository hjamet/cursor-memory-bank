---
name: enqueteur
description: "Diagnostic méthodique de bugs par traçage d'hypothèses et instrumentation sans rush."
---
# 🔎 Comment l'Enquêteur Identifie-t-il Méthodiquement l'Origine d'un Bug ?

## Principe fondamental (rappel strict)

Cette commande guide l'agent **étape par étape** pour identifier précisément l'origine d'un bug. **Interdiction absolue** : NE PAS modifier le code, NE PAS proposer ni appliquer de correction. L'objectif est d'identifier, pas de corriger.

Respectez le principe "Fail-Fast" : si une condition attendue est manquante, échouez explicitement et documentez.

---

## Vue d'ensemble (processus linéaire)

Suivre la séquence suivante dans l'ordre, sans appeler d'autres règles :

- Étape 1 — Exploration des fichiers de code
- Étape 2 — Formulation d'hypothèses (3–5)
- Étape 3 — Placement de logs avant/après pour chaque hypothèse
- Étape 4 — Exécution & collecte des logs
- Étape 5 — Analyse des logs
- Étape 6 — Validation critique (rôle de relecture approfondie)
- Étape 7 — Rapport final d'identification

À la fin de chaque étape, documenter la sortie attendue indiquée ci‑dessous, puis passer à l'étape suivante.

---

## ÉTAPE 1 — Exploration des fichiers de code 🔍

Objectif : cartographier les fichiers impliqués, tracer le flux d'exécution et repérer les points critiques.

Actions obligatoires :

1. Rechercher les points d'entrée pertinents (routes, handlers, main).  
2. Identifier les fonctions appelées et la séquence d'exécution jusqu'au point de défaillance.  
3. Noter dépendances externes (DB, services).  
4. Localiser les lignes/instructions candidates.

Sortie attendue (obligatoire) :

```
Fichiers identifiés :
- path/to/fileA (lignes X–Y)
- path/to/fileB (fonction foo)

Flux d'exécution : fileA:fn → fileB:fn → fileC:fn

Points critiques : liste de lignes/instructions suspectes
```

Exemple : `main.py:25 -> auth.py:validate_token -> models.py:get_user`

---

## ÉTAPE 2 — Formulation d'hypothèses 🎯

Objectif : produire 3–5 hypothèses précises et testables, localisées jusqu'à la ligne.

Règles : chaque hypothèse doit suivre ce format :

`Hypothèse N : [variable/fonction] [comportement attendu vs observé] car [cause supposée] — ligne [num] dans [fichier]`

Actions obligatoires :

1. Synthétiser l'exploration (étape 1).  
2. Rédiger 3–5 hypothèses localisées.  
3. Prioriser par probabilité et impact.

Sortie attendue (obligatoire) : liste de 3–5 hypothèses avec fichier + ligne.

Exemple : `Hypothèse 1 : user_id est None car extract_user_id_from_token() retourne None — ligne 23 dans src/utils/auth.py`

---

## ÉTAPE 3 — Placement de logs de débogage 📝

Objectif : insérer logs AVANT/APRÈS chaque instruction ciblée pour vérifier les hypothèses.

Règles strictes pour les logs :

- Format dictionnaire/JSON-like (ex : `print({"BEFORE_line_23":"true", "user_id": str(user_id)[:50]})`).  
- Limiter la taille des valeurs (tronquer) pour éviter sorties trop longues.  
- Ajouter `exit(1)` après la série de logs pour forcer l'arrêt et préserver l'état.

Actions obligatoires :

1. Pour chaque hypothèse, placer un `BEFORE` et un `AFTER` autour de la ligne ciblée.  
2. Utiliser identifiants clairs (`BEFORE_line_X`, `AFTER_line_X`).  
3. Documenter précisément où les logs ont été ajoutés.

Sortie attendue : liste des emplacements de logs ajoutés par hypothèse.

Exemple de sortie : `Logs ajoutés : src/auth.py lignes 22-24 (BEFORE) et 26-28 (AFTER)`

---

## ÉTAPE 4 — Exécution et collecte des logs 🚀

Objectif : exécuter le scénario reproduisant le bug et collecter stdout/stderr et code de sortie.

Actions obligatoires :

1. Reproduire les conditions exactes (env vars, arguments, état initial).  
2. Exécuter la commande exacte (documenter la commande).  
3. Collecter STDOUT, STDERR et code de sortie.  
4. Si le programme ne s'arrête pas, arrêter manuellement après avoir récupéré les logs et noter cette action.

Format de rapport d'exécution :

```
Commande exécutée : [commande]

STDOUT :
{BEFORE_line_23:..., AFTER_line_23:...}

STDERR : [erreurs éventuelles]

Code de sortie : [valeur]
Conditions reproduites : [env, args]
```

---

## ÉTAPE 5 — Analyse des logs 🔎

Objectif : comparer logs BEFORE/AFTER, valider/invalider les hypothèses et extraire symptômes précis.

Actions obligatoires :

1. Pour chaque hypothèse, indiquer : VALIDÉE / INVALIDÉE / PARTIELLEMENT avec preuves (citations des logs).  
2. Extraire symptômes concrets (valeurs inattendues, transitions d'état).  
3. Préparer la synthèse pour l'étape de validation critique (étape 6).

Format d'analyse attendu (obligatoire) :

```
Hypothèse 1 : ...
Status : ✅ VALIDÉE / ❌ INVALIDÉE / ⚠️ PARTIELLEMENT
Preuve : BEFORE = {...}, AFTER = {...}
Symptôme : description précise
```

---

## ÉTAPE 6 — Validation critique (relecture approfondie) 🕵️‍♂️

Objectif : produire une analyse critique qui questionne la précision de l'investigation et vérifie que l'on a atteint la cause racine (pas seulement les symptômes).

Principes :

- Questionner la précision (ligne exacte, instruction primitive).  
- Vérifier présence de preuves BEFORE & AFTER irréfutables.  
- Évaluer si une fonction locale pointée nécessiterait une exploration plus approfondie de ses instructions.

Actions obligatoires :

1. Produire une analyse critique de l'investigation menée aux étapes précédentes.  
2. Documenter les points de vigilance identifiés (précision de la ligne, qualité des preuves, mécanisme identifié).  
3. Préparer cette analyse pour inclusion dans le rapport final de l'étape 7.

Sortie attendue (obligatoire) : analyse critique structurée identifiant les points de vérification et l'évaluation de la cause racine identifiée.

---

## ÉTAPE 7 — Rapport final 📋

Objectif : fournir un rapport concis et chirurgical identifiant l'origine exacte du bug, en intégrant l'analyse critique de l'étape 6.

Format obligatoire du rapport final :

```
=== RAPPORT FINAL D'IDENTIFICATION DE BUG ===

Bug identifié : [description courte]
Impact : [conséquence]
Comportement attendu : [ce qui devrait se passer]

Origine précise :
Fichier : [chemin]
Fonction : [nom]
Ligne : [numéro]
Instruction : [code exact]

Cause racine : [explication mécanique]
Conditions de reproduction : [env, données, séquence]

Hypothèses validées : [liste avec preuves]
Hypothèses invalidées : [liste avec preuves]

Preuves décisives : Log BEFORE, Log AFTER

Analyse critique (étape 6) : [synthèse de l'analyse critique avec points de vigilance identifiés]

Conclusion (1-2 phrases) : origine identifiée, aucune correction proposée

Note : Si cette conclusion n'est pas suffisante ou nécessite une investigation plus approfondie, relancer la commande `/enqueteur` avec une question plus précise pour un nouveau cycle d'enquête.
```

Après rapport, l'agent doit noter explicitement que tous les logs ajoutés doivent être retirés par l'auteur de la correction (ne pas retirer les logs ici).

---

## Bonnes pratiques & règles opérationnelles

- Toujours documenter commandes, environnements et étapes précises.  
- Ne pas utiliser try/except pour masquer erreurs (principe Fail-Fast).  
- Éviter modifications de code sauf pour placer/supprimer logs; toute modification doit être explicite et justifiée dans le rapport.  
- L'étape de validation critique (étape 6) produit une analyse pour enrichir le rapport final, elle n'est pas une étape de décision de routing.

---

## Utilisation

1. Lancer la commande `/enqueteur` (ou lire intégralement ce fichier) avant toute action.  
2. Suivre les étapes dans l'ordre (1 à 7) et produire les sorties demandées pour chaque étape.  
3. Mettre à jour le reporting à chaque étape et ne jamais avancer sans la sortie attendue.
4. Si la conclusion du rapport final (étape 7) n'est pas suffisante, relancer la commande `/enqueteur` avec une question plus précise pour un nouveau cycle d'enquête itératif.

---

Fin de la commande.
