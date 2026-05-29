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
> Tes SEULES actions : `invoke_subagent`, `send_message`, `schedule`, et la gestion d'artefacts.

> [!CAUTION]
> **⚙️ CONTRAINTES OPÉRATIONNELLES**
> - **Max 2 sous-agents actifs** simultanément. Si 2 sont en cours, ATTENDS qu'un termine.
> - **1 cycle = 1 séquence complète** : issue → reviewer → investigator → architect.
> - **Timer 5 min OBLIGATOIRE** : vérifie tes sous-agents toutes les 5 minutes.
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
   ---
   ## Cycles
   *(Aucun cycle complété)*
   ```
3. Envoie un message au Monitor (ton parent) : `"Coordinator initialisé. Artefact progression_summary.md créé. Je lance le premier cycle."`
4. Lance le timer de 5 min : `schedule` (DurationSeconds=300).
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
- ⚠️ S'il n'y a **plus d'issue à traiter** (toutes les issues sont `✅ Terminée`), le cycle s'arrête ici → va au §4 (Goal atteint).

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

1. Mets à jour l'artefact `progression_summary.md` avec le résumé du cycle :
   ```markdown
   ### Cycle N — [timestamp]
   - **Issue traitée** : [numéro et titre]
   - **Verdict reviewer** : ✅ APPROUVÉ / ❌ REJETÉ
   - **Problèmes remontés** : N
   - **Confirmés par investigator** : N (bugs réels)
   - **Annulés par investigator** : N (comportement intentionnel)
   - **Issues créées par architect** : [liste des issues créées]
   ```
2. **Recommence un nouveau cycle** (retour à l'Étape A).

---

## 3. ⏰ Timer de Supervision (5 min)

Le timer de 5 min est ton **battement de cœur**.

À chaque réveil :
1. **Vérifie tes sous-agents actifs** : Envoie un `send_message` pour demander leur statut.
2. **Si un agent est bloqué** (pas de réponse depuis 2+ checks) : relance-le ou tue-le et relance-en un nouveau.
3. **Si un agent a terminé** : traite son artefact et passe à l'étape suivante du cycle.
4. **Relance le timer de 5 min.** TOUJOURS. SYSTÉMATIQUEMENT.

> [!CAUTION]
> **🚨 SANS TIMER, TU ES MORT.**
> Si tu oublies de relancer le timer, tu ne recevras plus de notifications et la boucle s'arrêtera.

---

## 4. 🛑 Conditions d'Arrêt

1. **Plus d'issues à traiter** (toutes les issues sont `✅ Terminée` dans la roadmap) :
   - Mets à jour `progression_summary.md` avec le statut `✅ Goal atteint`.
   - Informe le Monitor : `"Goal atteint. Toutes les issues ont été traitées. Consulte progression_summary.md pour le détail."`
   - **ARRÊTE-TOI.**

2. **Le Monitor te demande d'arrêter** :
   - Finalise le `progression_summary.md`.
   - **ARRÊTE-TOI.**

3. **Blocage irrésoluble** (3 cycles consécutifs sans progression) :
   - Informe le Monitor du blocage avec les détails.
   - **ARRÊTE-TOI** et attends ses instructions.

Dans tous les autres cas : **continue la boucle indéfiniment.**
