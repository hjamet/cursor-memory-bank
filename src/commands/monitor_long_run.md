---
description: Stratégie de monitoring pour les expériences longue durée (Overnight Runs)
---

# Long Run Monitoring Workflow

Ce workflow définit comment l'agent doit surveiller une tâche longue (ex: Optimisation Optuna > 1h) sans saturer le contexte ni perdre le contrôle.

## 1. Pré-requis
*   La commande doit être lancée en background (via  et son ID récupéré).
*   L'agent doit avoir vérifié que le processus a démarré correctement (Status  + premiers logs valides).

## 2. Boucle de Monitoring (The "Check-In" Loop)
L'agent doit entrer dans une boucle de vérification périodique.

### Fréquence
*   **Optuna / Training** : Toutes les 5 à 10 minutes (300s - 600s).
*   **Compilation / Build** : Toutes les 1 à 2 minutes (60s - 120s).

### Actions à chaque Check-In
1.  **Vérifier le Status** : Utiliser  avec un  long.
2.  **Analyser les Logs** :
    *   Regarder les dernières lignes ().
    *   Chercher des erreurs (, , ).
    *   Vérifier la progression (ex: "Trial 5/100 completed", "Epoch 3/10").
3.  **Décision** :
    *   **Tout va bien** : Mettre à jour le  (Status: "Monitoring Trial X/N...") et relancer .
    *   **Problème détecté** : Interrompre (), analyser la cause, corriger, et relancer (ou notifier l'utilisateur).
    *   **Terminé** : Analyser les résultats finaux, mettre à jour les artefacts (README, Walkthrough), et notifier l'utilisateur.

## 3. Communication
*   Ne pas notifier l'utilisateur à chaque check-in si tout va bien.
*   Notifier uniquement en cas de :
    *   Succès final (avec résumé des résultats).
    *   Échec critique nécessitant une décision humaine.
    *   Découverte intermédiaire majeure (ex: "Nouveau record battu à Trial 50 !").

## 4. Timeout Strategy
*   Utiliser l'argument  de  pour "dormir" efficacement.
*   Ne JAMAIS faire de boucle active (). Laisser l'outil gérer l'attente.
