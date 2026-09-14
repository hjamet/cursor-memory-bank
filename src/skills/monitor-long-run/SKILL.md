---
name: monitor-long-run
description: "Surveillance d'expériences longues durée et overnight runs sans saturer le contexte."
---
# 🌙 Comment Surveiller Efficacement une Tâche Longue Durée (Overnight Run) ?

Ce workflow définit comment surveiller une tâche longue (ex: Optimisation Optuna, pipeline DVC, fine-tuning) sans saturer le contexte ni polluer le chat.

## 📋 Quels Sont les Pré-requis Avant le Lancement ?

*   **Lancement asynchrone** : Exécuter la commande via `run_command` standard (sans `&` ni `nohup`) avec `WaitMsBeforeAsync` adapté pour basculer en arrière-plan.
*   **Identifiant de tâche** : Récupérer le `TaskId` retourné par `run_command` pour piloter la surveillance.
*   **Contrôle initial** : Vérifier que le processus démarre correctement (`manage_task(Action="status")` et présence des premières lignes de log).

## ⏱️ Comment S'Articule le Double Palier de Surveillance Temporelle ?

### ⚡ Comment Détecter les Défaillances Immédiates (Palier 1 : Fail-Fast) ?

1.  **T+30s (Early Check)** :
    *   Armer un premier timer rapide via `schedule(DurationSeconds=30, TimerCondition="<task-id>", Prompt="Check Fail-Fast T+30s")`.
    *   Objectif : Intercepter immédiatement les erreurs de démarrage (imports manquants, mauvaise syntaxe CLI, crash précoce, CUDA OOM instantané).
2.  **T+90s (+60s, Confirmation)** :
    *   Armer le second check via `schedule(DurationSeconds=60, TimerCondition="<task-id>", Prompt="Check Fail-Fast T+90s")`.
    *   Objectif : Confirmer la stabilité de la phase de warm-up, le chargement effectif des checkpoints et la génération des premiers pas d'entraînement.

### 🚢 Comment Fonctionne le Régime de Croisière Silencieux (Palier 2 : 20 Minutes) ?

1.  **Bascule en croisière silencieuse** :
    *   Après validation du palier Fail-Fast, basculer sur des cycles de **20 minutes (1200 secondes)**.
    *   Armer l'attente via `schedule(DurationSeconds=1200, TimerCondition="<task-id>", Prompt="Check croisière 20m")`.
2.  **Attente passive absolue** :
    *   Ne JAMAIS utiliser de boucle d'attente active, `time.sleep()`, ou polling répétitif.
    *   L'agent s'endort immédiatement et laisse le système réactif le réveiller (expiration du timer ou message de terminaison du task).
3.  **Réarmement nominal** :
    *   À chaque réveil, si le processus est toujours actif et sain, réarmer un cycle de 20 minutes (`schedule(DurationSeconds=1200, TimerCondition="<task-id>")`).

## 🔍 Quelles Actions Exécuter à Chaque Réveil ?

1.  **Interroger l'état du processus** :
    *   Appeler `manage_task(Action="status", TaskId="<task-id>")`.
2.  **Analyser les logs d'exécution** :
    *   Lire les dernières lignes du fichier log associé.
    *   Traquer les motifs d'erreurs (`Traceback`, `CUDA out of memory`, `Error`, `Segmentation fault`).
    *   Relever la progression (`Epoch X/Y`, `Trial N/M`, `step`, loss, métriques de validation).
3.  **Surveiller l'activité matérielle et la fraîcheur des logs** :
    *   Vérifier le timestamp du dernier log émis.
    *   Si aucun log n'a été produit depuis plus de 20 minutes alors que le process est actif, suspecter un gel matériel ou un deadlock.

## 🤫 Quelles Sont les Règles de Silence et les Critères de Réveil du Chat ?

### 🔇 Comment Respecter la Règle de Silence Strict en Régime Nominal ?

*   **Silence absolu** : **0 message** dans le chat si l'exécution suit son cours normal.
*   **Interdiction des statuts de routine** : Proscription formelle d'envoyer des notifications du type "Check 20 min OK", "Tourne toujours", etc.

### 🚨 Quels Événements Déclenchent une Notification dans le Chat ?

Notifier l'utilisateur **exclusivement** lors des événements suivants :
*   **Transitions d'étapes DVC** : Passage validé d'une étape à la suivante dans le pipeline.
*   **Commits de résultats ou plots** : Publication de nouvelles courbes ou métriques par le bot distant / worker.
*   **Gel matériel ou blocage (> 20 min)** : Processus bloqué sans émission de logs depuis plus de 20 minutes nécessitant un arbitrage.
*   **Échec critique ou crash** : Processus arrêté sur erreur, extraction du traceback et proposition d'action corrective.
*   **Succès final** : Terminaison réussie de l'expérience, résumé chiffré des métriques et localisation des artefacts produits.
