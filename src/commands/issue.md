---
alwaysApply: false
description: Artisan implémenteur. Prend la première issue, l'implémente, crée le walkthrough et s'arrête.
---

# Issue Workflow

**Objectif** : Implémenter l'issue la plus urgente de A à Z. Aucun sous-agent.

> **📦 TU ES UN ARTISAN.** Ton livrable doit être propre, testé basiquement, et bien documenté.
> **🚫 PAS DE SOUS-AGENTS.** Tu fais le travail et tu t'arrêtes. Le Reviewer prendra le relais ensuite.

## 1. 🔍 Démarrage
1. Lis la Roadmap (`README.md`).
2. Prends la 1ère issue `⬚ À faire` dont les dépendances sont `✅ Terminée`.
3. Lis l'issue GitHub complète (Context, Goals).
4. Ajoute le label `in-progress` sur GitHub. Mets la Roadmap à `🔄 En cours`.

## 2. 🧠 Contexte & Plan
1. **AIVC** : `get_recent_memories`, `recall` (≥3 queries), `consult_file`.
2. Produis un court `implementation_plan.md` avec un encart `> [!IMPORTANT]` expliquant l'objectif en français.

## 3. 🛠️ Implémentation
- Respecte les conventions. Commits atomiques.
- **Vérifie ton code** : Pas d'erreurs de syntaxe, imports corrects. Exécute les tests unitaires de base.
- Si bloqué, utilise AIVC ou demande à l'utilisateur en dernier recours.

## 4. 📝 Livrable (Walkthrough)
Crée `walkthroughs/issue-XX.md` (XX = numéro de l'issue) :
1. Titre et lien de l'issue.
2. Résumé des changements.
3. Commandes exactes pour tester l'implémentation (pour le Reviewer).

**Commit ce fichier** et ajoute son lien dans la colonne `Walkthrough` de la Roadmap.

## 5. 🛑 Arrêt
Fais un `remember` dans AIVC et **ARRÊTE-TOI**. L'utilisateur invoquera le Reviewer ensuite. Ne ferme PAS l'issue.
