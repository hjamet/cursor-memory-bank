---
alwaysApply: false
description: Rétablissement et reprise générale du travail suite à une interruption inattendue.
---

# Workflow de Reprise du Travail (Continue)

**Objectif** : Restaurer l'environnement et relancer toutes les tâches, agents, superviseurs et programmations temporelles suite à une interruption inattendue (crash d'IDE, redémarrage du serveur, etc.).

> [!IMPORTANT]
> **🚨 EFFET D'UNE INTERRUPTION :**
> En cas d'interruption ou de plantage de la plateforme de développement :
> 1. Les agents et sous-agents en cours d'exécution ont pu être annulés.
> 2. Les tâches d'arrière-plan, les timers et les tâches planifiées (`schedule` / cron jobs) ont été supprimés.
> 3. Ce workflow permet de tout rétablir de manière cohérente pour reprendre le travail.

---

## 1. 🔍 Étape 1 : Diagnostic de l'État du Projet

1. **Recherche de l'état** :
   Consulte le dossier `.agents/` à la racine pour identifier le dossier de coordination ou de travail le plus récent.
2. **Identifier les tâches interrompues** :
   Lis le dernier fichier de progression (`progression_summary.md` ou similaire) et inspecte les sous-dossiers actifs pour déterminer exactement quel agent et quelle tâche étaient en cours d'exécution avant l'interruption.

---

## 2. ⚙️ Étape 2 : Rétablissement et Relance

Puisque toute l'infrastructure agentique et temporelle a été arrêtée, rétablis le flux de travail de manière ordonnée :

1. **Relancer les agents superviseurs et coordinateurs** :
   Instancie à nouveau le ou les agents principaux annulés (comme le Coordinator ou le Monitor) avec leur prompt initial et l'état de reprise.
2. **Rétablir les tâches de supervision (Schedules)** :
   Demande à chaque niveau de supervision de réenregistrer ses tâches planifiées (cron jobs de check, timers) qui ont été effacés lors de l'arrêt.
3. **Restaurer les sous-agents et les commandes en cours** :
   Chaque superviseur doit à son tour relancer ses propres sous-agents et réactiver les tâches ou commandes en cours qui ont été annulées.

---

## 3. 🧠 Étape 3 : Arbitrage Intelligent de Reprise (Validation / Review)

Si le travail a été interrompu en pleine phase de **validation ou de review** (Reviewer, Reviewer Final) :

- **Arbitrage** : S'il y a déjà suffisamment d'anomalies avérées et de bugs importants identifiés à corriger, ne perds pas de temps à faire tourner à nouveau l'étape de validation. **Enchaîne immédiatement sur l'Investigateur** pour analyser et corriger directement les bugs et itérer plus rapidement.
- **Sinon** (ex: processus de validation live critique ou benchmark en cours avec logs intéressants), relance l'étape de validation pour finaliser l'analyse.

---

## 4. 🧹 Étape 4 : Nettoyage Rapide
- Supprime les verrous orphelins (ex: `.git/index.lock` ou `.dvc/tmp/lock`) qui pourraient bloquer la reprise des commandes.
- Enregistre une note mémoire AIVC (`remember`) pour marquer le point de relance et la reprise effective de l'activité.
