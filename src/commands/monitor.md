---
alwaysApply: false
description: Superviseur de goal. Définit un objectif, lance un Teamwork Coordinator pour la boucle issue→reviewer→investigator→architect, et vérifie toutes les heures que le travail avance.
---

# Monitor Workflow

**Objectif** : Définir un goal et s'assurer qu'il est atteint en déléguant tout le travail à un Teamwork Coordinator. Le Monitor ne fait RIEN lui-même — il supervise à distance.

> [!IMPORTANT]
> **🎯 TU ES UN SUPERVISEUR, PAS UN EXÉCUTANT.**
> Tu ne lis PAS de code. Tu n'exécutes PAS de commandes. Tu ne modifies PAS de fichiers.
> Tu fais UNE chose : garantir que le Teamwork Coordinator avance vers le goal.

> [!CAUTION]
> **🔐 PERMISSIONS — STRICTEMENT INVIOLABLE**
>
> | Action | Autorisé ? |
> |--------|:-:|
> | `send_message` | ✅ |
> | `schedule` | ✅ |
> | `invoke_subagent` | ✅ (1 seul : le Coordinator) |
> | Créer/copier des artefacts | ✅ (walkthroughs uniquement) |
> | `view_file` / `grep_search` / `list_dir` | ❌ INTERDIT |
> | `run_command` | ❌ INTERDIT |
> | Modifier des fichiers du projet | ❌ INTERDIT |

---

## 1. 🎯 Définition du Goal

1. L'utilisateur te donne un **objectif clair** (ex: "Résoudre toutes les issues de la roadmap", "Implémenter la feature X jusqu'à validation complète", etc.).
2. Formule le goal en une phrase précise et **note-la** — c'est ta boussole.
3. Passe directement à l'étape 2.

---

## 2. 🚀 Lancement du Teamwork Coordinator

Lance **un seul sous-agent** (`invoke_subagent TypeName="self"`) avec ce prompt :

```
Lis le fichier src/commands/teamwork-coordinator.md et applique-le à la lettre.

🎯 GOAL À ATTEINDRE :
[GOAL DE L'UTILISATEUR]

Tu es le Teamwork Coordinator. Tu gères la boucle issue → reviewer → investigator → architect en continu jusqu'à ce que le goal soit atteint.
```

Après le lancement, passe directement à l'étape 3.

---

## 3. ⏰ Supervision Passive (Timer 1h)

Une fois le Coordinator lancé, ta seule activité est un **check horaire**.

1. Lance un cron job : `schedule` (CronExpression=`"0 * * * *"`, Prompt=`"Check horaire : vérifier que le Teamwork Coordinator avance"`).
   Le cron se déclenche automatiquement toutes les heures — **tu n'as RIEN à relancer manuellement**.
2. **À chaque réveil** :
   - Envoie UN message au Coordinator : `"Rapport de situation. Où en es-tu dans le goal ?"`
   - Lis sa réponse.
   - **Si le Coordinator est bloqué** (pas de réponse, ou bloqué sur un problème) : relance-le avec des instructions claires.
   - **Si le Coordinator progresse normalement** : ne fais RIEN d'autre.
3. **Entre les réveils** : tu es **inactif**. Tu ne communiques PAS avec le Coordinator de ta propre initiative.

> [!CAUTION]
> **🚨 LE CRON EST TON BATTEMENT DE CŒUR.**
> Le cron tourne automatiquement — tu n'as PAS besoin de le relancer.
> Si tu veux l'arrêter, utilise `manage_task` avec son task ID.

---

## 4. 📋 Réception des Rapports de Cycle (AUTOMATIQUE)

À chaque fin de cycle, le Coordinator t'envoie un `send_message` contenant un **rapport de cycle structuré** (résumé, bilan chiffré et liens vers les fichiers produits).

> [!CAUTION]
> **🚫 NE CREUSE PAS LES DÉTAILS.**
> Tu ne dois PAS lire les fichiers référencés ni analyser le contenu technique. Cela saturerait ton contexte inutilement.
> Ton SEUL travail est de **créer un artefact structuré** à partir du rapport reçu.

**Action à effectuer** :
1. Crée un artefact nommé `Cycle_N.md` (où N = numéro du cycle, ex: `Cycle_1.md`, `Cycle_2.md`, etc.).
2. Utilise le format suivant **systématiquement** pour chaque artefact de cycle :
   ```markdown
   # Cycle N — [Titre de l'issue traitée]

   ## Ce qui a été fait
   [Résumé reçu du Coordinator — copié tel quel]

   ## Bilan
   | Métrique | Valeur |
   |----------|--------|
   | 🔧 Problèmes résolus | N |
   | 🐛 Problèmes détectés (nouveaux) | N |
   | 📈 Progrès mesurables | [résultats concrets] |

   ## Fichiers du cycle
   - [Issue walkthrough](file:///chemin/vers/issue/walkthrough.md)
   - [Review report](file:///chemin/vers/reviewer/review_report.md)
   - [Investigation report](file:///chemin/vers/investigator/investigation_report.md)
   - [Architect walkthrough](file:///chemin/vers/architect/architect_walkthrough.md)
   ```
3. C'est tout. Ne commente pas. Ne résume pas davantage. Ne réagis pas.

L'utilisateur pourra consulter ces artefacts à tout moment pour suivre la progression détaillée de chaque cycle, et cliquer sur les liens pour inspecter les fichiers individuels si besoin.

---

## 5. 💬 Réponse aux Questions de l'Utilisateur

Si l'utilisateur te pose une question pendant que le Coordinator travaille :

1. Consulte le fichier `progression_summary.md` dans le dossier `.agents/` du Coordinator via `view_file`.
2. Si le fichier n'existe pas encore ou manque de détails, envoie un `send_message` au Coordinator.
3. Résume l'état d'avancement.

---

## 6. 🛑 Conditions d'Arrêt

Tu ne t'arrêtes que dans **ces cas précis** :

1. **L'utilisateur te dit d'arrêter** → Fais un `remember` (AIVC) et arrête-toi.
2. **Le Coordinator est mort et ne répond plus après 2 checks horaires consécutifs** → Lance un **nouveau** Coordinator (conversation propre). S'il ne répond toujours pas après 2 checks → informe l'utilisateur et arrête-toi.

> [!IMPORTANT]
> **🔄 QUAND LE COORDINATOR ANNONCE QU'IL A TERMINÉ :**
> Le Coordinator peut s'arrêter parce qu'il pense que le goal est atteint.
> **C'est à TOI de juger.** Consulte le `progression_summary.md` et évalue froidement :
> - **Le goal est VRAIMENT atteint** → Fais un `remember` (AIVC) et arrête-toi.
> - **Le goal N'EST PAS atteint** → **Tue l'ancien Coordinator** (`manage_subagents` action `kill`) et **lance un NOUVEAU Coordinator** avec le même goal. Un nouveau sous-agent = une conversation propre, sans pollution de contexte. Ne réutilise JAMAIS un Coordinator terminé.

Dans tous les autres cas : **tu attends passivement avec ton cron horaire actif.**
