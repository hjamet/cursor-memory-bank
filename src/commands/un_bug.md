---
alwaysApply: false
description: Protocole de reprise résiliente après un crash de l'IDE Antigravity ou du Language Server.
---

# Workflow de Reprise Après Bug (Crash IDE / LS)

**Objectif** : Restaurer l'environnement de travail, relancer les structures de supervision agentiques annulées, et reprendre le cycle de développement là où il s'était arrêté de la manière la plus rapide et résiliente possible.

> [!IMPORTANT]
> **🚨 EFFET D'UN CRASH DE L'IDE/LS :**
> Lors d'un crash ou d'un redémarrage forcé de l'IDE :
> 1. **Tous les sous-agents** (Coordinator, Issue, Reviewer, Investigator, Architect) sont instantanément annulés.
> 2. **Toutes les tâches planifiées** (les timers et crons `schedule` du Monitor et du Coordinator) sont supprimées.
> 3. **Toutes les commandes asynchrones** en arrière-plan (comme `cluster-run`) sont interrompues.
>
> Ce workflow doit être exécuté par le Monitor pour reconstruire l'arbre de supervision et reprendre le travail sans perte de contexte.

---

## 1. 🔍 Étape 1 : Diagnostic de l'État du Dépôt

L'agent Monitor doit examiner l'état dans lequel se trouvait le projet juste avant l'interruption :

1. **Trouver le Coordinateur Actif** :
   Scanne le dossier `.agents/` à la racine du projet pour identifier le dossier de coordination le plus récent :
   ```
   .agents/coordinator_<objectif>_<YYYYMMDD_HHMMSS>/
   ```
2. **Lire la progression** :
   Consulte le fichier `.agents/coordinator_xxx/progression_summary.md` pour récupérer :
   - Le **Goal** initial fixé par l'utilisateur.
   - Les cycles complétés et l'état général.
3. **Identifier le Cycle Actif** :
   Scanne les sous-dossiers du coordinateur pour trouver le dossier de cycle en cours :
   ```
   .agents/coordinator_xxx/cycle_<titre_issue>/
   ```
4. **Déterminer l'étape interrompue** :
   Regarde quels sous-dossiers (`issue/`, `reviewer/`, `investigator/`, `architect/`, `reviewer_final/`) contiennent des livrables partiels pour savoir quel agent était en train de travailler.

---

## 2. ⚙️ Étape 2 : Nettoyage et Préparation (Résilience)

Avant de relancer les agents, nettoie le dépôt de tout effet de bord causé par l'arrêt brutal :

1. **Supprimer les verrous orphelins** :
   Si le crash a eu lieu pendant une opération Git ou DVC, supprime les fichiers de verrouillage qui bloqueraient les exécutions futures :
   - `.git/index.lock` (si présent)
   - `.dvc/tmp/lock` ou verrous similaires (si présents)
2. **Vérifier les services** :
   Si des serveurs locaux (comme Ollama) ou des connexions SSH vers le cluster étaient actifs, vérifie leur disponibilité et relance-les si nécessaire.

---

## 3. 🧠 Étape 3 : Arbitrage Intelligent de Reprise (Optimisation Reviewer)

Si le crash est survenu alors que le cycle était au milieu d'une étape de **Reviewer (Étape B — Reviewer Intermédiaire)** ou de **Reviewer Final (Étape E)**, applique cet arbitrage :

### Option A : Reprendre le Reviewer
* **Condition** : Le Reviewer était au milieu d'une tâche de validation complexe, critique ou particulièrement intéressante (ex: un long benchmark `cluster-run` sur Tomplay/Blackwell avec des sorties de logs en cours d'analyse que l'on veut absolument récupérer).
* **Action** : Relaunce l'agent Reviewer à l'étape correspondante en lui demandant de reprendre ses analyses.

### Option B : Enchaîner Directement sur l'Investigator (Recommandé pour la Vitesse)
* **Condition** : Le Reviewer effectuait des vérifications standards OU il y a déjà un volume d'anomalies confirmées et de gros bugs connus à régler sur le cluster, rendant inutile le fait de perdre du temps à refaire tourner le Reviewer.
* **Action** : Saute la fin de la phase Reviewer. Génère un `review_report.md` de transition résumant les bugs déjà connus ou partiellement identifiés, et **lance immédiatement l'Investigator (Étape C)**. Cela permet de profiter de l'interruption pour itérer plus rapidement et corriger les bugs sans attendre.

*Dans tous les autres cas (Issue, Investigator, Architect interrompus), relance simplement le sous-agent correspondant à l'étape interrompue avec les prompts et livrables adéquats.*

---

## 4. 🚀 Étape 4 : Rétablissement des Crons et Relance des Agents

Puisque le crash a supprimé toute l'infrastructure temporelle de supervision, rétablis-la de manière ordonnée :

1. **Rétablir le Cron Horaire du Monitor** :
   Enregistre à nouveau le timer de supervision passive :
   - `schedule` (CronExpression=`"0 * * * *"`, Prompt=`"Check horaire : vérifier que le Teamwork Coordinator avance"`)
2. **Instancier le nouveau Teamwork Coordinator** :
   Lance un sous-agent Coordinator tout propre (`invoke_subagent TypeName="self"`) avec le prompt de reprise :
   ```
   Lis le fichier src/commands/teamwork-coordinator.md.
   
   🎯 GOAL INITIAL : [Recopier le Goal du progression_summary.md]
   
   ⚠️ CONTEXTE DE REPRISE APRÈS CRASH :
   L'IDE a subi un arrêt inattendu. Nous étions au cycle <cycle_actif> à l'étape <etape_interrompue>.
   
   Instructions de reprise :
   - Recrée ton dossier de travail à l'emplacement existant : [chemin du dossier coordinator_xxx]
   - Rétablis ton cron de 5 minutes : schedule (CronExpression="*/5 * * * *", Prompt="Check supervision : vérifier l'état des sous-agents")
   - Applique la décision d'arbitrage intelligent pour reprendre le travail : [Indiquer si reprise de l'agent interrompu ou saut vers l'Investigator]
   ```
3. **Informer l'utilisateur** :
   Confirme à l'utilisateur que l'environnement est restauré, que les crons sont réactivés et que le cycle de développement a repris son cours.

---

## 5. 💾 Étape 5 : Mémoire à Long Terme (AIVC)

Termine l'opération en consignant l'événement dans le journal de version AIVC :
- Appelle l'outil `remember` pour enregistrer un résumé de la reprise :
  - **Titre** : "Reprise après crash IDE/LS — Restauration du cycle de développement"
  - **Description** : Détails du diagnostic, décision d'arbitrage prise, et relance des processus de supervision avec succès.
