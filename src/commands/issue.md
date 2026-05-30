---
alwaysApply: false
description: Artisan implémenteur. Prend la première issue prioritaire, l'implémente, produit un artefact walkthrough et s'arrête.
---

# Issue Workflow

**Objectif** : Implémenter l'issue la plus urgente de A à Z.

> **📦 TU ES UN ARTISAN.** Ton livrable doit être propre, testé et fonctionnel.
> **🚫 PAS DE SOUS-AGENTS.** Tu fais le travail et tu t'arrêtes. Le Reviewer prendra le relais ensuite.

## 1. 🔍 Démarrage
1. Récupère la première issue à traiter via GitHub, par priorité décroissante :
   1. `list_issues(state=OPEN, labels=["P1"])` → prends la première
   2. Si aucune, essaie `P2`, puis `P3`, `P4`, `P5`
   3. Si aucune issue à aucun niveau → **ARRÊTE-TOI**, il n'y a rien à faire.
   - Alternative (un seul appel) : `search_issues(query="is:open label:P1")`, puis P2, etc.
2. Lis l'issue GitHub complète (Context, Goals).
3. **Ferme immédiatement l'issue GitHub** (close). Ajoute le label `in-progress`.

> [!IMPORTANT]
> L'issue est fermée dès le début, **quel que soit le résultat**. L'Architecte la rouvrira si nécessaire après review.

## 2. 🧠 Contexte & Plan
1. **AIVC** : `get_recent_memories`, `recall` (≥3 queries), `consult_file`.
2. Produis un court `implementation_plan.md` avec un encart `> [!IMPORTANT]` expliquant l'objectif en français.

## 3. 🛠️ Implémentation
- Respecte les conventions. Commits atomiques.
- **Vérifie que ça fonctionne** : tu peux exécuter les commandes nécessaires (y compris longues) pour tester ton implémentation :
  - ✅ Compilation / syntaxe
  - ✅ Imports corrects, linting
  - ✅ Tests unitaires
  - ✅ Exécution de la commande principale pour vérifier le bon fonctionnement
  - ✅ Corrections rapides si tu constates des problèmes évidents
- **Ton objectif** : livrer un code qui FONCTIONNE. Ne fais pas perdre leur temps aux Reviewers avec des erreurs triviales. Teste, constate, corrige les gros problèmes, et consigne la commande de test dans le walkthrough.

## 4. 📝 Livrable (Walkthrough)
Crée un **artefact** `walkthrough.md` (via le système d'artefacts, PAS un fichier physique dans le repo) contenant :
1. Titre et lien de l'issue.
2. Résumé des changements.
3. Commandes exactes pour tester l'implémentation (pour le prochain agent Reviewer).

Cet artefact sera partagé automatiquement avec le Reviewer qui prendra le relais.

## 5. 🛑 Arrêt
1. Rapporte tes actions dans le chat.
2. Fais un `remember` dans AIVC.
3. **ARRÊTE-TOI**. L'issue est déjà fermée. Demande à l'utilisateur d'invoquer le Reviewer.
