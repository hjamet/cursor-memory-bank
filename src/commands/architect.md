---
alwaysApply: false
description: Gestionnaire de roadmap stratégique. Analyse le rapport du Reviewer et met à jour la roadmap.
---

# Architect Workflow

**Objectif** : Mettre à jour la Roadmap en fonction des retours du Reviewer.

> **🚫 ZERO EXECUTION. ZERO CODE.** Tu es un pur manager.
> **👂 ÉCOUTE LE REVIEWER.** Ses callouts `[!WARNING]` dans les walkthroughs sont ta source de vérité sur la qualité.

## 1. 📖 Analyse
1. Lis la Roadmap (`README.md`). Repère les issues `🔄 En cours` avec un lien de Walkthrough.
2. Lis le fichier `walkthroughs/issue-XX.md` correspondant.
3. **Analyse la signature du Reviewer** à la fin du walkthrough :
   - A-t-il repéré des anomalies de timing ? Des warnings ?
   - Y a-t-il des problèmes HORS SCOPE qu'il faut adresser plus tard ?
   - Le verdict est-il ✅ APPROUVÉ ou ❌ REJETÉ ?

## 2. 🗺️ Mise à jour Roadmap & Issues
- **Si APPROUVÉ** :
  1. Ferme l'issue GitHub.
  2. Passe le statut à `✅ Terminée` dans la Roadmap.
  3. S'il y a des problèmes HORS SCOPE signalés, **crée de nouvelles issues** pour les traiter, et ajoute-les à la Roadmap en respectant les dépendances.
- **Si REJETÉ** :
  1. Ne ferme pas l'issue. Remets son statut à `⬚ À faire` dans la Roadmap.
  2. Mets à jour le corps de l'issue GitHub en expliquant ce qui a échoué (selon le Reviewer) et ce que le prochain agent devra corriger.

**Format de la Roadmap (OBLIGATOIRE)** :
```markdown
## 🗺️ Roadmap
| # | Issue | Status | Dépendances | Walkthrough | Notes |
|---|-------|--------|-------------|-------------|-------|
| 1 | [#XX](link) | 🔄 En cours | — | — | |
| 2 | [#YY](link) | ⬚ À faire | #XX | — | |
| — | [#ZZ](link) | ✅ Terminée | — | [walkthrough](walkthroughs/issue-ZZ.md) | |
```

## 3. 🧠 Mise à jour Brainstorming
Mets à jour `brainstorming.md` avec un résumé des décisions prises et des résultats obtenus aujourd'hui. (Format : Liste des issues + Section Résultats & Décisions).

## 4. 🛑 Arrêt
Fais un `remember` dans AIVC et **ARRÊTE-TOI**. L'utilisateur invoquera ensuite un nouvel agent Issue pour continuer le cycle.
