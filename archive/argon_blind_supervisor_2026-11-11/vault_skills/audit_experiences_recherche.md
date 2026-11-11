---
tags:
  - skill
  - recherche
  - ml
---

# 🔬 Comment Auditer Manuellement et Critiquement Chaque Étape Intermédiaire d'une Expérience de Recherche ?

- Projets rattachés : [[notes/Obfuscation Stylistique Personnelle par VoiceNotes et GRPO]] · [[notes/Projet Orbit]] · [[notes/Cluster CI]]
- Skill d'orchestration associé : [[_agents/skills/cluster-ci/SKILL|Skill cluster-ci]]

## 🎯 Pourquoi les métriques agrégées et les proxys locaux trompent-ils l'expérimentateur ?

### 🕵️ Quels sont les quatre pièges classiques observés sur nos pipelines d'entraînement ?
Un pipeline DVC peut terminer avec un code retour `0` et afficher des moyennes flatteuses tout en étant scientifiquement invalide d'un bout à l'autre. L'inspection manuelle d'échantillons réels à chaque étape intermédiaire est le seul rempart contre quatre dérives récurrentes :
1. **Conservation du formatage intentionnel (Étape 1 — Extraction)** : vérifier que les courriels et transcriptions extraits sont propres (sans en-têtes techniques ni signatures parasites), tout en **conservant le formatage Markdown ou les listes à puces** afin que le modèle n'apprenne pas à détruire la mise en forme des textes soumis.
2. **Dégénérescence de la génération synthétique (Étape 2 — Auto-Inversion / Prétraitement)** : un petit modèle générateur recopie 95 % du texte original en altérant un chiffre (`14h00` $\to$ `14h10`) ou boucle sur un fragment (`: am I to be that way?`), rendant les paires d'entraînement contre-productives malgré le passage des filtres numériques.
3. **Sous-convergence masquée (Étape 3 — Entraînement)** : l'entraînement s'arrête après un nombre fixe de pas trop faible lorsque la longueur de séquence augmente (`loss` bloquée à `2.05` au lieu de `< 0.70`), produisant un modèle moins bon que la baseline zero-shot.
4. **Absence de détecteur local fiable — Évaluation directe sur GPTZero (Étape 4 — Évaluation)** : aucun détecteur local (heuristique ou classifieur DeBERTa) ne restant à jour face aux détecteurs commerciaux, supprimer tout score de détection local trompeur et soumettre directement les sorties générées à `gptzero.me` via MCP Playwright.
Source : `Prompt d'Henri Jamet (Chat 05/11/2026)` & `https://app.gptzero.me/` (Scan Playwright 05/11/2026)
> « Attends, ne fais pas confiance à notre modèle de détection locale, utilise GPTZero (`gptzero.me`) et utilise ton MCP Playwright pour soumettre des textes et regarder quels sont les pourcentages de détection. [...] Manuellement, pas de tests unitaires, vérifie ce qui est produit de manière intermédiaire et analyse-le de manière critique. C'est vraiment un point important ça à faire pour la recherche, peut-être que même il faudrait le sauvegarder dans un skill pour les expériences. »

## 📋 Quel est le protocole obligatoire d'inspection manuelle étape par étape (Zéro test unitaire) ?

### 🔍 Que faut-il lire et vérifier concrètement à la sortie de chaque brique du pipeline ?
Conformément à la règle d'interdiction absolue des tests unitaires (`pytest`), l'agent superviseur ou l'auditeur contrôle manuellement la réalité des artefacts produits à la fin de chaque étape :
1. **Après l'extraction du corpus (`data/extracted/`)** : tirer au sort et lire intégralement au moins 10 échantillons FR et 10 échantillons EN ; vérifier que 100 % des textes sont réellement produits par l'auteur cible (ex. dans VoiceNotes : exclure `duration: 0s` qui correspond à des notes écrites/mails reçus collés, ainsi que les enregistrements `> 10m` qui sont des réunions, cours d'autres professeurs ou JDR parfois non diarizés sans `Speaker X:`), que les signatures/citations sont purgées tout en préservant les listes à puces et le Markdown intentionnel, et tester 2 échantillons sur `gptzero.me`.
2. **Après la génération des paires ou exemples d'entraînement (`data/pairs/`)** : lire côte à côte 5 couples `(entrée -> cible)` ; vérifier visuellement que l'entrée reformule réellement la syntaxe dans un style neutre sans recopier la cible, sans corrompre les nombres/heures et sans aucune répétition dégénérée en fin de bloc.
3. **Après l'entraînement (`metrics/train_metrics.json` & `plots/`)** : vérifier que la courbe de `train_loss` et `val_loss` a réellement convergé jusqu'au plateau attendu et comparer systématiquement le modèle entraîné à la baseline sans fine-tuning.
4. **Après l'évaluation (`metrics/benchmark_metrics.json`)** : lire les textes complets générés sur le jeu de test et soumettre un sous-ensemble représentatif au juge externe réel via MCP Playwright (`gptzero.me`) avant de tirer la moindre conclusion.
