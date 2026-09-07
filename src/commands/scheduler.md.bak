---
alwaysApply: false
description: Orchestrateur cron crash-resilient. Invoqué périodiquement via /schedule, consulte un fichier d'état central, détecte les agents crashés via heartbeat, et exécute le workflow approprié (issue → reviewer → investigator → architect).
---

# Scheduler Workflow

**Objectif** : Orchestrer de manière autonome et crash-resilient la boucle `issue → reviewer → investigator → architect` via un système d'état persistant et de heartbeat, invoqué périodiquement par un cron Antigravity.

> [!IMPORTANT]
> **⏰ TU ES UN AGENT ÉPHÉMÈRE INVOQUÉ PAR UN CRON.**
> Tu es créé toutes les ~15 minutes par un cron Antigravity (`/schedule`).
> Tu consultes l'état, tu décides quoi faire, et tu travailles ou tu t'arrêtes.
> Tu NE restes PAS en vie entre les invocations — c'est le CRON qui te relance.
> **Si un agent est déjà actif (heartbeat frais), tu t'arrêtes IMMÉDIATEMENT sans rien faire.**

> [!CAUTION]
> **🔐 PERMISSIONS**
>
> | Action | Autorisé ? |
> |--------|:-:|
> | `view_file` / `grep_search` / `list_dir` | ✅ |
> | `write_to_file` | ✅ (state, heartbeat, artefacts) |
> | `run_command` | ✅ (heartbeat timestamp, Git) |
> | `invoke_subagent` | ✅ (1 seul actif à la fois) |
> | `schedule` | ✅ (heartbeat cron interne uniquement) |

---

## 📋 Utilisation

Pour lancer le système, l'utilisateur configure un cron Antigravity via `/schedule` :

```
Cron : */15 * * * *
Prompt : Lis le fichier src/commands/scheduler.md et applique-le à la lettre. GOAL : [objectif]
```

Le Scheduler crée automatiquement les fichiers d'état au premier lancement. Aucune configuration manuelle requise.

---

## 1. 📖 Lecture de l'État

1. Vérifie si le fichier `.agents/scheduler/state.json` existe (via `view_file`).
   - **S'il existe** → lis-le, puis lis `.agents/scheduler/heartbeat`.
   - **S'il n'existe pas** → c'est la **première exécution**. Passe à §1.1.

2. Obtiens l'heure actuelle :
   ```powershell
   Get-Date -Format "o"
   ```

3. Si un heartbeat existe, calcule son âge :
   ```powershell
   $hb = Get-Content ".agents\scheduler\heartbeat"; $diff = (Get-Date) - [DateTime]::Parse($hb); Write-Output "Heartbeat age: $([math]::Round($diff.TotalMinutes, 1)) minutes"
   ```

4. Passe à §2 (Décision).

### 1.1 Première Exécution (Initialisation)

1. Extrais le **GOAL** de ton prompt d'invocation (la phrase après `GOAL :`).
2. Obtiens l'heure actuelle via `run_command("Get-Date -Format 'o'")`.
3. Crée le fichier `.agents/scheduler/state.json` :

```json
{
  "goal": "[GOAL extrait du prompt]",
  "status": "active",
  "created_at": "[TIMESTAMP ACTUEL]",
  "config": {
    "heartbeat_timeout_minutes": 12,
    "step_timeout_minutes": 90,
    "pipeline": ["issue", "reviewer", "investigator", "architect"]
  },
  "current_cycle": null,
  "completed_cycles": []
}
```

4. Passe à §2 (Décision).

---

## 2. 🧠 Décision

Lis l'état et applique la **PREMIÈRE** règle qui correspond, dans l'ordre :

| # | Condition | Action |
|---|-----------|--------|
| 1 | `status` ≠ `"active"` | → **STOP**. Le système est en pause, terminé, ou en erreur. Arrête-toi. |
| 2 | `current_cycle` a `step_status = "running"` ET heartbeat **frais** (âge < `heartbeat_timeout_minutes`) | → **STOP**. Un agent travaille déjà. Ne fais RIEN. |
| 3 | `current_cycle` a `step_status = "running"` ET heartbeat **périmé** (âge ≥ `heartbeat_timeout_minutes`) | → **§2.1 Reprise après crash**. |
| 4 | `current_cycle` est `null` OU `step_status = "completed"` | → **§3 Exécution**. Un step attend d'être lancé. |

> [!CAUTION]
> **RÈGLE #2 EST SACRÉE.** Si un heartbeat frais existe, un autre agent est en train de travailler.
> Tu ne dois EN AUCUN CAS interférer. Arrête-toi proprement, sans rien écrire dans les fichiers d'état.

### 2.1 Reprise après Crash

L'agent précédent est mort (heartbeat périmé). Procédure de récupération :

1. **Log** dans ta sortie : `"⚠️ Crash détecté — Dernier heartbeat : [timestamp] ([N] minutes ago). Step en cours : [step]. Reprise…"`
2. **Nettoyage de l'état** :
   - Mets `step_status` à `"idle"` dans `state.json`.
   - Si le step crashé était `"issue"` :
     - Vérifie si l'issue a été fermée par l'agent Issue (via GitHub API : `issue_read`).
     - Si l'issue est fermée avec le label `in-progress` → **rouvre-la** (retire `in-progress`). L'agent Issue la reprendra.
3. **Passe à §3** pour relancer le step.

---

## 3. 🚀 Exécution

### 3.0 Détermination du Step

Applique la première règle qui correspond :

| Condition | Action |
|-----------|--------|
| `current_cycle` est `null` | → **Nouveau cycle**. Crée `current_cycle` avec `number = len(completed_cycles) + 1`, `step = "issue"`, `step_status = "idle"`. |
| `step_status` est `"idle"` | → **Reprendre** le step courant (`current_cycle.step`). |
| `step_status` est `"completed"` | → **Avancer** au step suivant dans le pipeline (voir table ci-dessous). |

**Transitions du pipeline :**

| Step terminé | Step suivant | Condition spéciale |
|-------------|-------------|-------------------|
| `issue` | `reviewer` | — |
| `reviewer` | `investigator` | — |
| `investigator` | `architect` | — |
| `architect` | *(fin de cycle)* | Enregistre le cycle dans `completed_cycles`. Mets `current_cycle = null`. Retourne à §3.0 pour un nouveau cycle ou un arrêt. |

> [!IMPORTANT]
> **Fin de pipeline (après architect)** : quand un cycle se termine, le Scheduler vérifie s'il reste des issues GitHub ouvertes (P1→P5). Si **oui** → nouveau cycle. Si **non** → `status = "completed"`, STOP.

### 3.1 Préparation

1. Crée le **répertoire de travail** du cycle si nécessaire :
   ```
   .agents/scheduler/cycle_[N]/[step]/
   ```
   Par exemple : `.agents/scheduler/cycle_1/issue/`, `.agents/scheduler/cycle_1/reviewer/`, etc.

2. Mets à jour `state.json` :
   - `step_status` → `"running"`
   - `step_started_at` → timestamp actuel

3. **Initialise le heartbeat** :
   ```powershell
   Get-Date -Format "o" | Set-Content ".agents\scheduler\heartbeat" -NoNewline
   ```

4. **Lance le heartbeat cron interne** :
   ```
   schedule(CronExpression="*/3 * * * *", Prompt="HEARTBEAT")
   ```
   Ce cron se déclenche automatiquement toutes les 3 minutes. Tu n'as PAS besoin de le relancer.

5. Passe à §3.2.

### 3.2 Lancement du Sous-Agent

Lance **UN** sous-agent (`invoke_subagent TypeName="self"`) avec le prompt correspondant au step.

> [!CAUTION]
> **UN SEUL sous-agent actif à la fois.** Attends qu'il termine avant de passer au step suivant.

---

#### Step `issue`

```text
Lis et suis le fichier src/commands/issue.md à la lettre.

Ton dossier de travail pour les artefacts (walkthrough.md, etc.) est :
.agents/scheduler/cycle_[N]/issue/

Travaille normalement selon les instructions du fichier issue.md.
Quand tu as terminé, envoie-moi via send_message le chemin complet de ton walkthrough.md.
```

**Après complétion** : Note le chemin du `walkthrough.md` dans `state.json` → `artifacts.walkthrough`. Note aussi l'issue traitée dans `issue_context`.

---

#### Step `reviewer`

```text
Lis et suis le fichier src/commands/reviewer.md à la lettre.
Tu es en Mode A (suite d'un agent Issue).

📄 Walkthrough à consulter : [chemin du walkthrough depuis state.json]

Ton dossier de travail pour les artefacts (review_report.md, etc.) est :
.agents/scheduler/cycle_[N]/reviewer/

Travaille normalement selon les instructions du fichier reviewer.md.
Quand tu as terminé (commande crashée ou fin naturelle), envoie-moi via send_message le chemin complet de ton review_report.md.
```

> [!WARNING]
> **Le Reviewer peut tourner longtemps** (il observe une commande en live). Surveille le timeout :
> si `step_timeout_minutes` est atteint, envoie un `send_message` au sous-agent :
> `"⏰ Timeout atteint. Rédige ton verdict final et ton review_report.md MAINTENANT, puis arrête-toi."`
> Attends encore 10 minutes max. Si toujours pas de réponse → tue le sous-agent et passe au step suivant avec ce que tu as.

**Après complétion** : Note le chemin du `review_report.md` dans `state.json` → `artifacts.review_report`.

---

#### Step `investigator`

```text
Lis et suis le fichier src/commands/investigator.md à la lettre.

📄 Walkthrough : [chemin]
📄 Review report : [chemin]

Ton dossier de travail pour les artefacts (investigation_report.md, etc.) est :
.agents/scheduler/cycle_[N]/investigator/

Travaille normalement selon les instructions du fichier investigator.md.
Quand tu as terminé, envoie-moi via send_message le chemin complet de ton investigation_report.md.
```

**Après complétion** : Note le chemin du `investigation_report.md` dans `state.json` → `artifacts.investigation_report`.

---

#### Step `architect`

```text
Lis et suis le fichier src/commands/architect.md à la lettre.

📄 Walkthrough : [chemin]
📄 Review report : [chemin]
📄 Investigation report : [chemin]

Ton dossier de travail pour les artefacts (architect_walkthrough.md, etc.) est :
.agents/scheduler/cycle_[N]/architect/

Travaille normalement selon les instructions du fichier architect.md.
Quand tu as terminé, envoie-moi via send_message le chemin complet de ton architect_walkthrough.md.
```

**Après complétion** : Note le chemin du `architect_walkthrough.md` dans `state.json` → `artifacts.architect_walkthrough`. Le cycle est **terminé**.

---

### 3.3 Supervision (Boucle de Messages)

Après le lancement du sous-agent, tu entres en **mode superviseur passif**. Tu ne fais QUE réagir aux messages reçus :

#### Message "HEARTBEAT" (du cron interne)

1. Mets à jour le fichier heartbeat :
   ```powershell
   Get-Date -Format "o" | Set-Content ".agents\scheduler\heartbeat" -NoNewline
   ```
2. **Vérifie le timeout du step** : si le temps écoulé depuis `step_started_at` dépasse `step_timeout_minutes`, envoie un message de timeout au sous-agent (voir §3.2, encart WARNING du Reviewer).
3. C'est tout. Continue d'attendre.

#### Message du sous-agent (step terminé)

1. Le sous-agent a fini son travail et t'envoie le chemin de son artefact.
2. **Arrête le heartbeat cron** : `manage_task(Action="kill", TaskId=[ID du cron heartbeat])`.
3. Mets à jour `state.json` :
   - Note le chemin de l'artefact produit dans `artifacts`.
   - `step_status` → `"completed"`.
   - Avance `step` au step suivant dans le pipeline.
4. **Si un step suivant existe** → retourne à §3.1 (Préparation) pour le lancer.
5. **Si le cycle est terminé** (architect done) :
   - Enregistre le cycle dans `completed_cycles` :
     ```json
     {
       "number": N,
       "issue_number": [numéro],
       "issue_title": "[titre]",
       "result": "completed",
       "completed_at": "[TIMESTAMP]"
     }
     ```
   - Mets `current_cycle` → `null`.
   - Retourne à §3.0 pour vérifier s'il reste des issues (nouveau cycle ou arrêt).

---

## 4. 🛑 Conditions d'Arrêt

| Condition | Action |
|-----------|--------|
| `status` ≠ `"active"` | STOP immédiat. Ne rien écrire. |
| Heartbeat frais (agent actif) | STOP immédiat. Ne rien écrire dans les fichiers d'état. |
| Plus aucune issue GitHub ouverte (P1→P5) | Mets `status = "completed"`. STOP. |
| Erreur irrécupérable | Log l'erreur, mets `status = "error"` dans `state.json`. STOP. |
| 3 cycles consécutifs sans progrès | Mets `status = "stalled"` dans `state.json`. STOP. |

> [!IMPORTANT]
> **Quand tu t'arrêtes après avoir travaillé** (pas un simple "rien à faire"), fais un commit Git :
> ```powershell
> git add .agents/scheduler/
> git commit -m "🤖 scheduler: [résumé court de ce qui a été fait]"
> ```
> Ne fais PAS de `git push` — les pushs sont réservés aux fins de grosses features.

---

## 5. 📊 Référence : Format de `state.json`

```json
{
  "goal": "string — objectif de l'utilisateur",
  "status": "active | paused | completed | error | stalled",
  "created_at": "ISO 8601",
  "config": {
    "heartbeat_timeout_minutes": 12,
    "step_timeout_minutes": 90,
    "pipeline": ["issue", "reviewer", "investigator", "architect"]
  },
  "current_cycle": {
    "number": 1,
    "step": "issue | reviewer | investigator | architect",
    "step_status": "idle | running | completed",
    "step_started_at": "ISO 8601",
    "issue_context": {
      "number": 42,
      "title": "Fix GPU allocation"
    },
    "working_dir": ".agents/scheduler/cycle_1/",
    "artifacts": {
      "walkthrough": ".agents/scheduler/cycle_1/issue/walkthrough.md | null",
      "review_report": ".agents/scheduler/cycle_1/reviewer/review_report.md | null",
      "investigation_report": ".agents/scheduler/cycle_1/investigator/investigation_report.md | null",
      "architect_walkthrough": ".agents/scheduler/cycle_1/architect/architect_walkthrough.md | null"
    }
  },
  "completed_cycles": [
    {
      "number": 1,
      "issue_number": 41,
      "issue_title": "Initialize model",
      "result": "completed",
      "completed_at": "ISO 8601"
    }
  ]
}
```

---

## 6. 🔧 Contrôle Manuel

L'utilisateur peut interagir avec le Scheduler en modifiant directement `state.json` :

| Action souhaitée | Modification |
|-----------------|-------------|
| **Pause** | `"status": "paused"` |
| **Reprise** | `"status": "active"` |
| **Arrêt définitif** | `"status": "completed"` |
| **Forcer un restart du step** | `"step_status": "idle"` |
| **Changer le timeout** | `"config.step_timeout_minutes": [valeur]` |
| **Changer le pipeline** | `"config.pipeline": [...]` |

> [!NOTE]
> **📊 Suivi de progression** : consultez `state.json` et les artefacts dans `.agents/scheduler/cycle_N/` à tout moment pour voir l'avancement. Chaque cycle produit un ensemble complet d'artefacts (walkthrough, review_report, investigation_report, architect_walkthrough).
