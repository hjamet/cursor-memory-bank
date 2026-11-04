---
name: watch-inbox
description: Boucle événementielle de surveillance de Dream_Inbox sur Google Drive et d'avancement autonome borné en mode /one-shot (1 projet = 1 tâche new ou Rasoir d'Ockham) lorsque Dream_Inbox est vide. Permet à un agent ou à Henri de lancer, vérifier ou arrêter manuellement watch-inbox. Trigger sur /watch-inbox.
aliases:
  - watch-inbox
---

# 📡 Skill Watch-Inbox — Surveillance Événementielle `Dream_Inbox` & Autonomie Bornée `/one-shot`

Ce skill documente et pilote le script canonique [`watch_inbox_cli.py`](file:///c:/Users/Jamet/Documents/VoiceNotes/_agents/scripts-for-skills/watch_inbox_cli.py), situé dans `_agents/scripts-for-skills/` afin d'être synchronisé automatiquement entre tous les ordinateurs d'Henri via Obsidian Sync tout en gardant le serveur MCP `aivc` strictement agnostique.

---

## 📍 Chemins Canoniques & Interprète Python

- **Script CLI Python (Source Unique de Vérité)** : `c:\Users\Jamet\Documents\VoiceNotes\_agents\scripts-for-skills\watch_inbox_cli.py` (résolu dynamiquement multi-PC via `"$env:USERPROFILE\Documents\VoiceNotes\_agents\scripts-for-skills\watch_inbox_cli.py"`)
- **Interprète Python Canonique (avec dépendances Google Drive & OAuth AIVC)** : `"$env:USERPROFILE\.aivc\venv\Scripts\python.exe"`
- **Archive Locale des Documents `Dream_Inbox`** : `C:\Users\Public\aivc\dream_inbox_archive\`
- **Registre Anti-Doublon Synchronisé** : `%USERPROFILE%\.aivc\dream_inbox_processed.json`
- **Lanceurs Shell Utilisateur** :
  - Fonction PowerShell `watch-inbox` dans `Microsoft.PowerShell_profile.ps1` (PowerShell 7 & WindowsPowerShell 5.1)
  - Wrappers CLI `%USERPROFILE%\.local\bin\watch-inbox.cmd` et `%USERPROFILE%\.local\bin\watch-inbox`

---

## ⚙️ Architecture à Deux Volets de `watch_inbox_cli.py`

1. **Volet 1 — Réception Temps Réel `Dream_Inbox` (Priorité Absolue)** :
   - Interroge en direct l'API REST Google Drive v3 (`/drive/v3/files` et `/drive/v3/changes`) avec backoff progressif `(5, 10, 20, 30)` s couvrant la fenêtre de 60 s de rate-limit Google Drive.
   - Dès qu'un document est détecté dans l'un des dossiers `Dream_Inbox` surveillés :
     1. **Sauvegarde locale immédiate** du texte intégral dans `C:\Users\Public\aivc\dream_inbox_archive\<nom>.md` ;
     2. **Verrouillage multi-clés** (`doc_id`, nom avec et sans extension) dans `~/.aivc/dream_inbox_processed.json` ;
     3. **Mise à la corbeille Google Drive dès la première seconde** (avant même d'invoquer `agy.exe`), garantissant zéro double exécution en cas d'interruption ;
     4. **Invocation d'`agy.exe --mode auto --model gemini-4-argon-high`** qui délègue directement le chemin du fichier local à un sous-agent `superviseur-projet` distinct par projet ciblé, sans jamais reformuler le propos d'Henri.
   - **Auto-rechargement à chaud (`os.execv`)** : à chaque cycle de veille, le script vérifie le `st_mtime` de `watch_inbox_cli.py` et se recharge automatiquement en mémoire vive dès que le fichier est mis à jour sur le disque (par exemple via Obsidian Sync).

2. **Volet 2 — Autonomie Bornée `/one-shot` lorsque `Dream_Inbox` est vide** :
   - Si aucun document n'est présent dans `Dream_Inbox` (et sauf si `--no-autonomous` est passé), `watch_inbox_cli.py` appelle :
     `python project_memory_cli.py next-autonomous --json`
   - Sélectionne le **premier projet actif le plus urgent** (selon le score effectif $S_{\text{eff}}$ avec malus de récence $M_{\text{temporal}}(K)$, **sans seuil de priorité minimum**) qui ne possède **aucune tâche au statut `await_validation`**.
   - Lance un unique agent `agy.exe --mode auto --model gemini-4-argon-high` en mode `/one-shot` qui :
     1. Lit la note maîtresse et `C:\Users\Public\aivc\advance_tldr\🤖 <Titre>.md` ;
     2. Identifie **la seule et unique tâche `new`** la plus urgente immédiatement réalisable (ou, à défaut, la tâche récurrente **Rasoir d'Ockham** `[ockham-<slug>]`) ;
     3. Consulte l'historique complet de la tâche via `mcp-cli call aivc get_task_history '{"task_id": "<id>"}'` ;
     4. Exécute cette unique tâche sur la branche principale (avec `/draft` obligatoire pour toute modification substantielle de note ou de texte destiné à publication, et zéro action irréversible), dépose son livrable en `await_validation` via `task_commit` et clôture la session avec `project_memory_cli.py feedback "<Projet>" ok --agent`.

---

## 🚀 Comment un Agent (ou Henri) Lance, Vérifie ou Arrête `watch-inbox` Manuellement ?

Lorsqu'Henri invoque `/watch-inbox` ou demande à l'agent de lancer, vérifier, relancer ou arrêter `watch-inbox` :
- Conformément à [`superviseur-aveugle.md`](file:///c:/Users/Jamet/Documents/VoiceNotes/_agents/rules/superviseur-aveugle.md), le Superviseur ($P=0$) délègue l'exécution shell à un sous-agent `executant` (`Model: 'flash'`) en Régime A Fast-Track, qui applique les commandes ci-dessous.

### 1. Répertoire des Sous-Commandes de `watch_inbox_cli.py`

```powershell
# Lancer la boucle de surveillance continue au premier plan (mode par défaut si appelé sans sous-commande)
& "$env:USERPROFILE\.aivc\venv\Scripts\python.exe" "$env:USERPROFILE\Documents\VoiceNotes\_agents\scripts-for-skills\watch_inbox_cli.py" watch [--interval 15] [--no-autonomous] [--model gemini-4-argon-high]

# Exécuter une seule passe (vérifie Dream_Inbox une fois + 1 passe autonome si vide, puis quitte)
& "$env:USERPROFILE\.aivc\venv\Scripts\python.exe" "$env:USERPROFILE\Documents\VoiceNotes\_agents\scripts-for-skills\watch_inbox_cli.py" watch --once [--dry-run] [--no-autonomous]

# Vérifier si un processus watch-inbox tourne déjà en arrière-plan (PID, heure de démarrage, ligne de commande)
& "$env:USERPROFILE\.aivc\venv\Scripts\python.exe" "$env:USERPROFILE\Documents\VoiceNotes\_agents\scripts-for-skills\watch_inbox_cli.py" status

# Arrêter proprement toute instance watch-inbox en cours d'exécution
& "$env:USERPROFILE\.aivc\venv\Scripts\python.exe" "$env:USERPROFILE\Documents\VoiceNotes\_agents\scripts-for-skills\watch_inbox_cli.py" stop

# Lister les documents actuellement présents dans Dream_Inbox sur Google Drive
& "$env:USERPROFILE\.aivc\venv\Scripts\python.exe" "$env:USERPROFILE\Documents\VoiceNotes\_agents\scripts-for-skills\watch_inbox_cli.py" list [--all]

# Lire le contenu d'un document Dream_Inbox par ID ou sous-chaîne du nom
& "$env:USERPROFILE\.aivc\venv\Scripts\python.exe" "$env:USERPROFILE\Documents\VoiceNotes\_agents\scripts-for-skills\watch_inbox_cli.py" read "<id_ou_nom>"

# Mettre à la corbeille un document Dream_Inbox par ID ou sous-chaîne du nom
& "$env:USERPROFILE\.aivc\venv\Scripts\python.exe" "$env:USERPROFILE\Documents\VoiceNotes\_agents\scripts-for-skills\watch_inbox_cli.py" trash "<id_ou_nom>"
```

### 2. Lancement Manuel par un Sous-Agent en Processus Détaché (Survivant à la Fermeture du Sous-Agent)

Conformément à la Règle d'Or n°9 de [`sous-agents.md`](file:///c:/Users/Jamet/Documents/VoiceNotes/_agents/rules/sous-agents.md), lorsqu'un sous-agent `executant` démarre `watch-inbox` en tâche de fond permanente, il **DOIT** le lancer hors de son Job Object via WMI (`Win32_Process.Create`) — ou via la sous-commande dédiée `start` du script qui encapsule l'appel WMI — afin que `manage_subagents kill` ne tue pas le démon `watch-inbox` :

```powershell
# Démarrer (ou redémarrer proprement) watch-inbox en arrière-plan détaché WMI avec logs dans C:\Users\Public\aivc\watch_inbox.log
& "$env:USERPROFILE\.aivc\venv\Scripts\python.exe" "$env:USERPROFILE\Documents\VoiceNotes\_agents\scripts-for-skills\watch_inbox_cli.py" start [--no-autonomous]
```

Après le lancement, le sous-agent vérifie systématiquement avec `status` que le nouveau PID est actif et consigne la sortie exacte dans `scratch/sources_executant.md`.
