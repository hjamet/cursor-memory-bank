---
alwaysApply: false
description: Orchestrateur de la boucle issue→reviewer→investigator→architect. Gère le passage de fichiers entre agents via le dossier .agents/ et consigne la progression.
---

# Teamwork Coordinator Workflow

**Objectif** : Orchestrer la boucle `issue → reviewer → investigator → architect` en continu jusqu'à ce que le goal soit atteint. Tu es un COORDINATEUR PUR — tu ne fais aucun travail technique toi-même.

> [!IMPORTANT]
> **🎯 TU ES UN CHEF D'ORCHESTRE, PAS UN MUSICIEN.**
> Tu lances des sous-agents, tu leur passes des chemins de fichiers, tu consignes les résultats.
> Tu ne lis PAS de code. Tu n'exécutes PAS de commandes. Tu ne modifies PAS de fichiers du projet.
> Tes SEULES actions : `invoke_subagent`, `send_message` (vers tes sous-agents uniquement), `schedule`, et la gestion de fichiers dans le dossier `.agents/`.

> [!CAUTION]
> **🤫 SILENCE RADIO VERS TON PARENT (MONITOR)**
> Tu n'envoies **JAMAIS** de message à ton parent de ta propre initiative.
> Tu ne lui fais PAS de rapports. Tu ne l'informes PAS de ta progression.
> Si ton parent te pose une question → tu réponds. Sinon → tu te tais.
> Toute ta progression est consignée dans le fichier `progression_summary.md` — c'est le SEUL canal d'information vers le parent.
>
> **UNIQUE EXCEPTION** : Après chaque Étape D (Architect), tu envoies UN `send_message` à ton parent avec un **rapport de cycle structuré** (résumé, bilan chiffré, fichiers produits). C'est un envoi automatique, pas un rapport de statut. Cela se fait **TOUJOURS**, que le cycle aboutisse à un succès ou un échec.

> [!CAUTION]
> **⚙️ CONTRAINTES OPÉRATIONNELLES**
> - **Max 2 sous-agents actifs** simultanément. Si 2 sont en cours, ATTENDS qu'un termine.
> - **1 cycle = 1 séquence complète** : issue → reviewer → investigator → architect.
> - **Cron 5 min OBLIGATOIRE** : vérifie tes sous-agents toutes les 5 minutes via un cron job automatique.
> - **Chaque agent reçoit UN prompt** : "Lis le fichier de workflow et applique-le" + les chemins des fichiers de l'agent précédent.

---

## 1. 🚀 Initialisation

1. Note le **goal** transmis par le Monitor.
2. **Crée ton dossier de travail** à la racine du projet :
   ```
   .agents/coordinator_<objectif_court>_<YYYYMMDD_HHMMSS>/
   ```
   Exemple : `.agents/coordinator_pipeline_monitoring_20260601_003046/`
3. Crée le fichier `progression_summary.md` dans ce dossier (`write_to_file`, `IsArtifact=false`) :
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

Chaque cycle suit cette séquence **strictement ordonnée**. Tu ne passes à l'étape suivante QUE quand l'agent en cours a terminé et produit son fichier.

> [!IMPORTANT]
> **📂 CONVENTION DE NOMMAGE**
> Pour chaque cycle, crée un sous-dossier nommé d'après l'issue traitée :
> ```
> .agents/coordinator_xxx/cycle_<titre_court_issue>/
> ```
> Chaque agent du cycle crée son propre sous-dossier dans ce dossier de cycle.

### Étape A — Agent Issue

Lance un sous-agent (`invoke_subagent TypeName="self"`) :

```
Lis le fichier src/commands/issue.md et applique-le à la lettre.

📂 DOSSIER DE TRAVAIL : [chemin absolu]/.agents/coordinator_xxx/cycle_<titre_court>/issue/
Crée ce dossier et écris ton walkthrough.md dedans (write_to_file, IsArtifact=false).
```

**Attends** qu'il termine. Vérifie que le fichier `walkthrough.md` existe dans son dossier.
- ⚠️ S'il n'y a **plus d'issue à traiter** (aucune issue `OPEN`), le cycle s'arrête ici → va au §4 (Goal atteint).

### Étape B — Agent Reviewer

Lance un sous-agent (`invoke_subagent TypeName="self"`) :

```
Lis le fichier src/commands/reviewer.md et applique-le à la lettre.

📂 DOSSIER DE TRAVAIL : [chemin absolu]/.agents/coordinator_xxx/cycle_<titre_court>/reviewer/
Crée ce dossier et écris ton review_report.md dedans (write_to_file, IsArtifact=false).

📖 WALKTHROUGH À LIRE : [chemin absolu]/.agents/coordinator_xxx/cycle_<titre_court>/issue/walkthrough.md
```

**Attends** qu'il termine. Vérifie que le fichier `review_report.md` existe dans son dossier.

### Étape C — Agent Investigator

Lance un sous-agent (`invoke_subagent TypeName="self"`) :

```
Lis le fichier src/commands/investigator.md et applique-le à la lettre.

📂 DOSSIER DE TRAVAIL : [chemin absolu]/.agents/coordinator_xxx/cycle_<titre_court>/investigator/
Crée ce dossier et écris ton investigation_report.md dedans (write_to_file, IsArtifact=false).

📖 REVIEW REPORT À LIRE : [chemin absolu]/.agents/coordinator_xxx/cycle_<titre_court>/reviewer/review_report.md
📖 WALKTHROUGH À LIRE : [chemin absolu]/.agents/coordinator_xxx/cycle_<titre_court>/issue/walkthrough.md
```

**Attends** qu'il termine. Vérifie que le fichier `investigation_report.md` existe dans son dossier.

### Étape D — Agent Architect

Lance un sous-agent (`invoke_subagent TypeName="self"`) :

```
Lis le fichier src/commands/architect.md et applique-le à la lettre.

📂 DOSSIER DE TRAVAIL : [chemin absolu]/.agents/coordinator_xxx/cycle_<titre_court>/architect/

📖 REVIEW REPORT À LIRE : [chemin absolu]/.agents/coordinator_xxx/cycle_<titre_court>/reviewer/review_report.md
📖 INVESTIGATION REPORT À LIRE : [chemin absolu]/.agents/coordinator_xxx/cycle_<titre_court>/investigator/investigation_report.md
```

**Attends** qu'il termine. Récupère son fichier `architect_walkthrough.md`.

### Étape D-bis — Rapport de Cycle au Monitor (OBLIGATOIRE ET INCONDITIONNELLE)

> [!CAUTION]
> **🛑 CETTE ÉTAPE EST INCONDITIONNELLE.**
> Tu DOIS envoyer un rapport de cycle structuré au Monitor **immédiatement après l'Étape D**, AVANT de passer au Reviewer Final.
> Cela se fait **que le cycle aboutisse ensuite à un succès ou un échec**.

1. **Envoie le rapport de cycle au Monitor** :
   Envoie UN `send_message` à ton parent (Monitor) avec le contenu suivant **exactement dans ce format** :
   ```
   📋 RAPPORT CYCLE N :

   ## Résumé
   **Issue traitée** : [#XX Titre](lien GitHub)
   [2-3 phrases décrivant concrètement ce qui a été fait dans ce cycle]

   ## Bilan chiffré
   - 🔧 Problèmes résolus : N
   - 🐛 Problèmes détectés (nouveaux) : N
   - 📈 Progrès mesurables : [résultats concrets obtenus — ex: "latence réduite de 200ms à 50ms", "couverture GPU passée de 0% à 85%", "3 endpoints corrigés sur 5", etc.]

   ## Fichiers produits
   - 📄 Issue walkthrough : [chemin absolu]/.agents/coordinator_xxx/cycle_yyy/issue/walkthrough.md
   - 📄 Review report : [chemin absolu]/.agents/coordinator_xxx/cycle_yyy/reviewer/review_report.md
   - 📄 Investigation report : [chemin absolu]/.agents/coordinator_xxx/cycle_yyy/investigator/investigation_report.md
   - 📄 Architect walkthrough : [chemin absolu]/.agents/coordinator_xxx/cycle_yyy/architect/architect_walkthrough.md
   ```
   C'est un rapport structuré, PAS une copie intégrale du walkthrough. Le Monitor utilisera ces informations pour créer un artefact consultable par l'utilisateur.

2. **Mets à jour le fichier `progression_summary.md`** dans ton dossier de travail :

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

   **Reviewer Final** — ⏳ En attente
   ```

   **b) Mets à jour les tableaux de suivi** en haut du document :
   - `## Issues résolues ✅` : ajoute les issues fermées ce cycle (lien + titre)
   - `## Issues ajoutées 📋` : ajoute les nouvelles issues créées ce cycle (lien + titre)

### Étape E — Reviewer Final (Validation Live OBLIGATOIRE)

> [!CAUTION]
> **🎯 CETTE ÉTAPE EST LA CLÉ DE VOÛTE DU CYCLE.**
> Le coordinator ne peut JAMAIS considérer un cycle comme terminé sans une validation live par le Reviewer.
> Pas de tests unitaires. Pas de simulations. Pas de "ça devrait marcher".
> **UNIQUEMENT l'exécution réelle de la commande principale du repo en conditions live.**

Lance un sous-agent (`invoke_subagent TypeName="self"`) :

```
Lis le fichier src/commands/reviewer.md et applique-le à la lettre.

📂 DOSSIER DE TRAVAIL : [chemin absolu]/.agents/coordinator_xxx/cycle_<titre_court>/reviewer_final/
Crée ce dossier et écris ton review_report.md dedans (write_to_file, IsArtifact=false).

📋 CONTEXTE — VALIDATION FINALE DU CYCLE :
Tu es invoqué en MODE B (supervision live). Ta mission est d'exécuter la COMMANDE PRINCIPALE du repo en conditions réelles.

🔍 COMMENT TROUVER LA COMMANDE PRINCIPALE :
1. Lis le README.md du repo.
2. Identifie la commande d'exécution principale (pipeline de recherche, démarrage d'application, etc.).
3. Exécute-la telle quelle, SANS modification, SANS simplification.

📖 WALKTHROUGH À LIRE : [chemin absolu]/.agents/coordinator_xxx/cycle_<titre_court>/issue/walkthrough.md
📖 REVIEW REPORT INTERMÉDIAIRE À LIRE : [chemin absolu]/.agents/coordinator_xxx/cycle_<titre_court>/reviewer/review_report.md
📖 INVESTIGATION REPORT À LIRE : [chemin absolu]/.agents/coordinator_xxx/cycle_<titre_court>/investigator/investigation_report.md
```

**Attends** qu'il termine. Lis son fichier `review_report.md` (rapport final).

**Analyse le verdict du Reviewer Final :**
- **✅ APPROUVÉ** → Le cycle est validé. Passe à la section "Fin de cycle" ci-dessous.
- **❌ REJETÉ** → Les problèmes trouvés doivent être corrigés. Crée de nouvelles issues à partir des bugs remontés, puis relance un mini-cycle :
  1. Lance l'**Agent Issue** pour traiter les bugs du Reviewer Final.
  2. Lance l'**Agent Investigator** pour vérifier les corrections.
  3. **Relance l'Étape E** (nouveau Reviewer Final) pour re-valider.
  4. Répète jusqu'à obtenir ✅ APPROUVÉ.

### Fin de cycle

> [!IMPORTANT]
> **Tu arrives ici après que le Reviewer Final a rendu son verdict (✅ ou ❌).**
> La transmission du walkthrough et la mise à jour de progression_summary.md ont déjà été faites à l'Étape D-bis.

1. **Mets à jour `progression_summary.md`** avec le verdict du Reviewer Final :
   - Complète la section `**Reviewer Final**` du cycle en cours :
   ```markdown
   **Reviewer Final** — Verdict : ✅ APPROUVÉ / ❌ REJETÉ
   Commande testée : [commande principale]
   Tentatives de validation : N
   ```

2. **Recommence un nouveau cycle** (retour à l'Étape A).

---

## 3. ⏰ Cron de Supervision (5 min)

Le cron de 5 min est ton **battement de cœur**. Il tourne automatiquement — tu n'as PAS besoin de le relancer.

À chaque réveil :
1. **Vérifie tes sous-agents actifs** : Envoie un `send_message` pour demander leur statut.
2. **Si un agent est bloqué** (pas de réponse depuis 2+ checks) : relance-le ou tue-le et relance-en un nouveau.
3. **Si un agent a terminé** : vérifie que son fichier de livrable existe dans son dossier de travail, puis passe à l'étape suivante du cycle.

> [!CAUTION]
> **🚨 LE CRON EST TON BATTEMENT DE CŒUR.**
> Il tourne automatiquement — pas besoin de le relancer. Pour l'arrêter : `manage_task` avec son task ID.

---

## 4. 🛑 Conditions d'Arrêt

> [!CAUTION]
> **🎯 CONDITION D'ARRÊT UNIQUE ET NON NÉGOCIABLE :**
> Le Teamwork Coordinator ne peut s'arrêter **QUE** lorsque :
> 1. Il n'y a plus d'issues `OPEN` sur GitHub, **ET**
> 2. Le **Reviewer Final** a validé (✅ APPROUVÉ) l'exécution de la commande principale du repo en conditions réelles.
>
> **Sans validation live du Reviewer Final = PAS D'ARRÊT.** Même s'il n'y a plus d'issues, tu DOIS lancer un Reviewer Final pour confirmer que tout fonctionne.

1. **Plus d'issues à traiter + Reviewer Final ✅ APPROUVÉ** :
   - Toutes les issues sont fermées.
   - Le dernier Reviewer Final a rendu un verdict ✅ APPROUVÉ sur la commande principale.
   - Mets à jour `progression_summary.md` avec le statut `✅ Goal atteint — Validé en conditions réelles`.
   - **ARRÊTE-TOI.** (Le Monitor le découvrira à son prochain check horaire via le fichier.)

2. **Plus d'issues à traiter MAIS Reviewer Final ❌ REJETÉ** :
   - Le Reviewer Final a trouvé des problèmes → ce sont de NOUVELLES issues.
   - Lance l'**Agent Architect** pour créer les issues correspondantes.
   - **Recommence un cycle** (retour à l'Étape A). Tu ne peux PAS t'arrêter.

3. **Le Monitor te demande d'arrêter** :
   - Finalise le `progression_summary.md`.
   - **ARRÊTE-TOI.** (Seule exception à la règle du Reviewer Final.)

4. **Blocage irrésoluble** (3 cycles consécutifs sans progression ET 3 échecs consécutifs du Reviewer Final) :
   - Mets à jour `progression_summary.md` avec le statut `🛑 Bloqué` et les détails.
   - **ARRÊTE-TOI.** (Le Monitor le découvrira à son prochain check.)

Dans tous les autres cas : **continue la boucle indéfiniment.**
