---
name: autoresearch
description: "Protocole scientifique d'expérimentation autonome en 4 étapes inspiré d'Andrej Karpathy et du Rasoir d'Ockham : (1) diagnostic rationnel de la cause racine d'un problème dans les résultats, (2) conception de la solution la plus simple possible selon Ockham, (3) test ceteris paribus strictement comparable aux résultats antérieurs en isolant uniquement le critère modifié, (4) décision Keep/Discard selon le rapport complexité/performance, avec documentation systématique dans la Note Maîtresse du projet et détails complets dans une sous-note dédiée. Trigger sur /autoresearch."
aliases:
  - autoresearch
  - auto-research
---

# 🪒 Skill Autoresearch — Expérimentation Scientifique *Ceteris Paribus* & Rasoir d'Ockham

> [!IMPORTANT]
> **Philosophie & Règle d'Or** :
> Face à un problème empirique ou une piste d'amélioration, les modèles de langage ont un biais d'addition : ils empilent des heuristiques, des hyperparamètres et des conditions `if/else` tout en modifiant plusieurs facteurs à la fois (ex. changer de modèle d'embeddings *et* ajouter une surcouche géométrique dans une même expérience), ce qui rend impossible d'identifier la source réelle d'un gain.
> Le skill `/autoresearch` impose une méthode expérimentale stricte en **4 étapes séquentielles** suivies d'une **documentation systématique à deux niveaux (Note Maîtresse + Sous-Note)**, **que l'idée testée soit conservée (`keep`) ou rejetée (`discard`)**.

---

## 🔬 Les 4 Étapes Obligatoires d'une Passe `/autoresearch`

### Étape 1 — Diagnostic Rationnel de la Cause Racine dans les Résultats
1. Inspecter les résultats bruts, les logs d'erreurs et les cas d'échec par segment ou par dataset (sans se fier à une moyenne globale trompeuse).
2. Identifier la **cause rationnelle et mécaniste** du problème observé (ex. effondrement vers des hubs, troncature de contexte, sur-pondération de la loss de justification, fuite de split, ou gain attribué à tort à une surcouche alors que la baseline a changé).
3. Formuler explicitement ce diagnostic sous forme d'hypothèse falsifiable avant d'écrire la moindre ligne de code.

### Étape 2 — Conception de la Solution Minimale selon le Critère d'Ockham
1. Imaginer la solution **la plus simple et épurée possible** répondant directement à la cause identifiée à l'Étape 1 ($\le 1$ opérateur ou paramètre réglé exclusivement sur `DEV`/`VAL`, zéro usine à gaz).
2. Définir simultanément le **contrôle négatif minimal sans surcouche** (ex. l'interpolation linéaire ou le modèle de base nu au même budget de calcul) que la solution devra battre pour prouver son utilité propre.

### Étape 3 — Test *Ceteris Paribus* Strictement Comparable (Un Seul Critère Modifié)
1. **Sanctuarisation de l'évaluation (`prepare.py` / banc de test immuable)** : utiliser exactement les mêmes jeux de données, les mêmes splits, les mêmes métriques et la même graine aléatoire que les résultats antérieurs.
2. **Isolation stricte d'une seule variable (*Ceteris Paribus*)** : ne modifier **QU'UN SEUL critère par expérience** afin d'avoir la certitude absolue que l'écart mesuré provient uniquement de ce critère. Si deux facteurs doivent être étudiés (ex. taille du modèle et méthode de reranking), exécuter la grille factorielle complète des ablations élémentaires.
3. Consigner chaque run dans un registre tabulaire reproductible (`results.tsv` : identifiant d'expérience, description, métriques par benchmark, moyenne, latence/coût et test statistique apparié face à la baseline).

### Étape 4 — Décision Keep / Discard selon le Rapport Complexité / Performance
Appliquer froidement le **Critère de Simplicité d'Andrej Karpathy** ([`zero-trust.md`](file:///c:/Users/hjamet/Documents/VoiceNotes/_agents/rules/zero-trust.md)) :
- **Supprimer du code ou une surcouche** en obtenant un résultat égal ou supérieur est une victoire majeure (`keep` — *simplification win*).
- **Ajouter de la complexité** pour un gain marginal, statistiquement non significatif ($p \ge 0.05$) ou battu par un contrôle trivial plus rapide doit être **rejeté** (`discard` + `git reset` du code complexe sur la branche de travail, tout en conservant la trace dans `results.tsv`).
- Ne conserver (`keep`) une addition que si le gain net est substantiel, statistiquement prouvé sur le facteur isolé et largement supérieur au coût de complexité et de latence introduit.

---

## 📓 Traçabilité Obligatoire dans le Coffre Obsidian (Dans Tous les Cas : `Keep` comme `Discard`)

Qu'une idée testée soit **conservée (`keep`) ou écartée (`discard`)**, un résultat négatif ou d'ablation propre a autant de valeur scientifique qu'un résultat positif et empêche de retester deux fois la même impasse :
1. **Dans la Sous-Note Dédiée (`notes/<Sous-Note Autoresearch Projet>.md`)** :
   - Documenter en détail l'état actuel des expérimentations : la question de recherche, la cause rationnelle testée, la formulation exacte de chaque variante, le protocole *ceteris paribus*, le tableau/extrait complet des métriques (`Source : <chemin results.tsv ou commande>`) et l'analyse du compromis complexité/performance.
2. **Dans la Note Maîtresse du Projet (`notes/<Titre>.md` $\to$ `_agents/project_diffs/🤖 <Titre>.md`)** :
   - Placer le wikilink `[[notes/<Sous-Note>|Titre]]` sous la section correspondante.
   - Expliquer en **1 à 2 phrases synthétiques** l'idée testée, la raison pour laquelle elle a été conservée ou rejetée selon le Critère d'Ockham, et le résultat chiffré clé suivi de son bloc `Source :`, puis régénérer l'artéfact de diff `_agents/project_diffs/🤖 <Titre>.md` via `doc-version` (`get_diff_artifact`).
   - En session autonome `/advance` (où l'écriture directe dans `VoiceNotes/` est interdite par l'Invariant 1), consigner cette synthèse et le brouillon de sous-note dans `<appDataDir>/brain/<id>/` + `task_commit` AIVC afin qu'ils soient intégrés à la Note Maîtresse et à sa sous-note dès la passe de synchronisation suivante.
