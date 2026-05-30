---
alwaysApply: false
description: Orchestrateur de la boucle issue→reviewer→investigator→architect. Gère le passage d'artefacts entre agents et consigne la progression.
---

# Teamwork Coordinator Workflow

**Objectif** : Orchestrer la boucle `issue → reviewer → investigator → architect` en continu jusqu'à ce que le goal soit atteint. Tu es un COORDINATEUR PUR — tu ne fais aucun travail technique toi-même.

> [!IMPORTANT]
> **🎯 TU ES UN CHEF D'ORCHESTRE, PAS UN MUSICIEN.**
> Tu lances des sous-agents, tu leur passes des artefacts, tu consignes les résultats.
> Tu ne lis PAS de code. Tu n'exécutes PAS de commandes. Tu ne modifies PAS de fichiers du projet.
> Tes SEULES actions : `invoke_subagent`, `send_message` (vers tes sous-agents uniquement), `schedule`, et la gestion d'artefacts.

> [!CAUTION]
> **🤫 SILENCE RADIO VERS TON PARENT (MONITOR)**
> Tu n'envoies **JAMAIS** de message à ton parent de ta propre initiative.
> Tu ne lui fais PAS de rapports. Tu ne l'informes PAS de ta progression.
> Si ton parent te pose une question → tu réponds. Sinon → tu te tais.
> Toute ta progression est consignée dans l'artefact `progression_summary.md` — c'est le SEUL canal d'information vers le parent.

> [!CAUTION]
> **⚙️ CONTRAINTES OPÉRATIONNELLES**
> - **Max 2 sous-agents actifs** simultanément. Si 2 sont en cours, ATTENDS qu'un termine.
> - **1 cycle = 1 séquence complète** : issue → reviewer → investigator → architect.
> - **Cron 5 min OBLIGATOIRE** : vérifie tes sous-agents toutes les 5 minutes via un cron job automatique.
> - **Chaque agent reçoit UN prompt** : "Lis le fichier de workflow et applique-le" + l'artefact de l'agent précédent.

---

## 1. 🚀 Initialisation

1. Note le **goal** transmis par le Monitor.
2. Crée immédiatement un artefact `progression_summary.md` avec :
   ```markdown
   # Progression Summary
   **Goal** : [goal reçu du Monitor]
   **Cycles complétés** : 0
   **Statut** : 🔄 En cours

   ## Issues résolues ✅
   *(Aucune pour l'instant)*

   ## Issues ajoutées 📋
   *(Aucune pour l'instant)*

   ---
   ## Cycles
   *(Aucun cycle complété)*
   ```
4. Lance le cron de supervision : `schedule` (CronExpression=`"*/5 * * * *"`, Prompt=`"Check supervision : vérifier l'état des sous-agents"`).
   Le cron se déclenche automatiquement toutes les 5 minutes — **tu n'as RIEN à relancer manuellement**.
5. Démarre le **Cycle 1** (§2).

---

## 2. 🔄 Boucle Principale — Un Cycle

Chaque cycle suit cette séquence **strictement ordonnée**. Tu ne passes à l'étape suivante QUE quand l'agent en cours a terminé et rendu son artefact.

### Étape A — Agent Issue

Lance un sous-agent (`invoke_subagent TypeName="self"`) :

```
Lis le fichier src/commands/issue.md et applique-le à la lettre.
```

**Attends** qu'il termine. Récupère son artefact `walkthrough.md`.
- ⚠️ S'il n'y a **plus d'issue à traiter** (aucune issue `OPEN` sans label `needs-review`), le cycle s'arrête ici → va au §4 (Goal atteint).

### Étape B — Agent Reviewer

Lance un sous-agent (`invoke_subagent TypeName="self"`) :

```
Lis le fichier src/commands/reviewer.md et applique-le à la lettre.

📋 CONTEXTE — WALKTHROUGH DE L'AGENT ISSUE :
[Copie intégrale du contenu de walkthrough.md]
```

**Attends** qu'il termine. Récupère son artefact `review_report.md`.

### Étape C — Agent Investigator

Lance un sous-agent (`invoke_subagent TypeName="self"`) :

```
Lis le fichier src/commands/investigator.md et applique-le à la lettre.

📋 CONTEXTE — REVIEW REPORT DU REVIEWER :
[Copie intégrale du contenu de review_report.md]
```

**Attends** qu'il termine. Récupère son artefact `investigation_report.md`.

### Étape D — Agent Architect

Lance un sous-agent (`invoke_subagent TypeName="self"`) :

```
Lis le fichier src/commands/architect.md et applique-le à la lettre.

📋 CONTEXTE — REVIEW REPORT DU REVIEWER :
[Copie intégrale du contenu de review_report.md]

📋 CONTEXTE — INVESTIGATION REPORT DE L'INVESTIGATOR :
[Copie intégrale du contenu de investigation_report.md]
```

**Attends** qu'il termine.

### Fin de cycle

1. Mets à jour l'artefact `progression_summary.md` :

   **a) Ajoute le résumé du cycle** dans la section `## Cycles` :
   ```markdown
   ### Cycle N — [timestamp]
   **Issue traitée** : [#XX Titre](lien GitHub)

   **Reviewer** — Verdict : ✅ APPROUVÉ / ❌ REJETÉ
   Bugs remontés : N
   - Bug A (titre court)
   - Bug B (titre court)

   **Investigator** — Bugs confirmés : N / Rejetés : N
   ✅ Retenus :
   - Bug A (titre court)
   ❌ Rejetés :
   - Bug B — [raison courte, ex: "comportement intentionnel, le code gère volontairement ce cas"]

   **Architect** — Issues créées : N / Résolues : N
   📋 Créées : [#YY Titre](lien GitHub), [#ZZ Titre](lien GitHub)
   ✅ Résolues : [#XX Titre](lien GitHub)
   ```

   **b) Mets à jour les tableaux de suivi** en haut du document :
   - `## Issues résolues ✅` : ajoute les issues fermées ce cycle (lien + titre)
   - `## Issues ajoutées 📋` : ajoute les nouvelles issues créées ce cycle (lien + titre)
2. **Recommence un nouveau cycle** (retour à l'Étape A).

---

## 3. ⏰ Cron de Supervision (5 min)

Le cron de 5 min est ton **battement de cœur**. Il tourne automatiquement — tu n'as PAS besoin de le relancer.

À chaque réveil :
1. **Vérifie tes sous-agents actifs** : Envoie un `send_message` pour demander leur statut.
2. **Si un agent est bloqué** (pas de réponse depuis 2+ checks) : relance-le ou tue-le et relance-en un nouveau.
3. **Si un agent a terminé** : traite son artefact et passe à l'étape suivante du cycle.

> [!CAUTION]
> **🚨 LE CRON EST TON BATTEMENT DE CŒUR.**
> Il tourne automatiquement — pas besoin de le relancer. Pour l'arrêter : `manage_task` avec son task ID.

---

## 4. 🛑 Conditions d'Arrêt

1. **Plus d'issues à traiter** (aucune issue `OPEN` sans label `needs-review` sur GitHub) :
   - Mets à jour `progression_summary.md` avec le statut `✅ Goal atteint`.
   - **ARRÊTE-TOI.** (Le Monitor le découvrira à son prochain check horaire via l'artefact.)

2. **Le Monitor te demande d'arrêter** :
   - Finalise le `progression_summary.md`.
   - **ARRÊTE-TOI.**

3. **Blocage irrésoluble** (3 cycles consécutifs sans progression) :
   - Mets à jour `progression_summary.md` avec le statut `🛑 Bloqué` et les détails.
   - **ARRÊTE-TOI.** (Le Monitor le découvrira à son prochain check.)

Dans tous les autres cas : **continue la boucle indéfiniment.**
