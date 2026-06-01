---
alwaysApply: false
description: Workflow simple de reprise après un crash de l'IDE.
---

# Workflow de Reprise Après Crash (IDE / LS)

**Objectif** : Restaurer l'environnement et relancer le travail suite à un arrêt inattendu de l'IDE.

> [!IMPORTANT]
> **🚨 REPRISE APRÈS CRASH :**
> Si l'IDE ou le Language Server s'est arrêté inopinément :
> 1. Les sous-agents (Coordinator, etc.) et les tâches en arrière-plan (cronjobs, timers, `schedule`) ont tous été annulés.
> 2. Il faut immédiatement réinitialiser et relancer le travail.

---

## 1. 🚀 Relance de la Supervision (Crons et Coordinateur)

1. **Rétablir le Cron Horaire du Monitor** :
   Enregistre à nouveau le timer de supervision passive :
   - `schedule` (CronExpression="0 * * * *", Prompt="Check horaire : vérifier que le Teamwork Coordinator avance")

2. **Relancer le Teamwork Coordinator** :
   Lance un nouveau sous-agent Coordinator (`invoke_subagent TypeName="self"`) en lui fournissant le prompt de reprise avec son but initial.

3. **Rétablir le Cron du Coordinator** :
   Le nouveau Coordinator doit réactiver son cron de 5 minutes :
   - `schedule` (CronExpression="*/5 * * * *", Prompt="Check supervision : vérifier l'état des sous-agents")

---

## 2. 🧠 Arbitrage et Reprise du Cycle

Identifie où en était le dernier cycle actif via le dossier `.agents/` :

- **Si le cycle était en phase de Review (Reviewer ou Reviewer Final)** :
  - **Arbitrage** : S'il y a déjà suffisamment d'anomalies ou de gros bugs identifiés à régler, ne perds pas de temps à relancer le Reviewer. **Passe immédiatement à l'Investigator (Étape C)** pour itérer plus rapidement.
  - Sinon (ex: run critique en cours d'intérêt majeur), relance le Reviewer pour finaliser la validation.

- **Dans tous les autres cas** (Issue, Investigator, Architect) :
  - Relance simplement l'agent à l'étape où il s'était arrêté.

---

## 3. 🧹 Nettoyage Rapide
- Supprime les verrous orphelins éventuels qui bloqueraient les exécutions (ex: `.git/index.lock` ou `.dvc/tmp/lock`).
- Fais un `remember` AIVC rapide pour marquer la relance.
