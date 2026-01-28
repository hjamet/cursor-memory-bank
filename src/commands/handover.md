---
description: Générer un prompt de passation (Handover) narratif pour maintenir le contexte.
---

# Workflow: Context Handover

Ce workflow sert à générer un **"Prompt de Passation"** à la fin d'une conversation. L'objectif est de transmettre l'histoire de la session de manière naturelle, comme si tu expliquais la situation à un collègue oralement.

## Philosophie
*   **PAS DE LISTES À PUCES**.
*   **PAS DE PLANS DÉTAILLÉS MICRO-MANAGÉS**.
*   **PAS D'INJONCTIONS**.

On veut du **contexte**, de la **narrative**, et un résumé de la **discussion**. Le prochain agent doit comprendre *l'esprit* de ce qui se passe, pas juste recevoir une check-list aveugle.

## Structure du Prompt
Le prompt doit être généré dans un bloc de code Markdown.

### 1. 👋 Relai : [Titre de l'Action]
Un titre accrocheur résumant la mission immédiate.

### 2. Le Contexte & La Discussion (Narratif)
Rédige un **grand paragraphe (ou deux)** en langage naturel.
*   **Raconte l'histoire** : "On a commencé par regarder ça, puis on se rend compte que..."
*   **Intègre les fichiers** : Cite les noms des fichiers concernés (juste le nom, pas le chemin complet) directement dans tes phrases. Ex: "J'ai modifié `server.py` pour régler le bug, mais ça a cassé `utils.py`."
*   **Résume la discussion** : "L'utilisateur voulait absolument éviter telle méthode, on s'est donc mis d'accord pour partir sur..."
*   **État des lieux** : Dis clairement ce qui marche et ce qui ne marche pas.

### 3. La Mission (Synthétique)
Une phrase ou deux pour donner le cap.
**IMPORTANT** : Invite explicitement le nouvel agent à **lancer une discussion** avec l'utilisateur pour valider ses intentions et lever les doutes avant de foncer.
Ex: "L'objectif est de stabiliser le fix. Demande à l'utilisateur s'il préfère l'option A ou B avant de commencer."

## Exemple de Sortie
```markdown
# 👋 Relai : Stabilisation des Logs

### Contexte & Discussion
On est en train de bosser sur le système de logging. Au début, on pensait que le problème venait de la config dans `logging_config.py`, mais après analyse avec l'utilisateur, on a vu que `main.py` écrasait les handlers au démarrage. J'ai commencé à nettoyer ça, mais attention, l'utilisateur a insisté pour qu'on ne touche pas à la lib standard `custom_logger.py` pour l'instant. Là, le backend tourne mais n'écrit plus rien dans la console, surement un souci de niveau de verbosité que j'ai pas eu le temps de check.

### Mission
Il faut finir de rétablir l'affichage console sans casser le fichier de log, en respectant la contrainte sur `custom_logger.py`.
```
