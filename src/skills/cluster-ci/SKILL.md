---
name: cluster-ci
description: "Orchestration DVC, GitOps et pipelines d'entraînement sur cluster GPU."
---
# Skill cluster-ci — Orchestrateur GitOps & Pipeline GPU Cluster

## 1. Quelle est l'Architecture Matérielle et la Topologie du Cluster ?

**Cluster-CI** est un orchestrateur minimaliste et décentralisé basé sur GitOps pour le traitement de jeux de données et l'entraînement de modèles Deep Learning sur un cluster de GPU hétérogènes. Il remplace Slurm/Ray par un modèle pull-based utilisant des exécuteurs GitHub Actions (GHA) auto-hébergés, Docker et DVC.

### Topologie Matérielle & Règle d'Allocation
* **Workers (ARM64 Executors)** : 2 nœuds physiques dédiés NVIDIA GB10 (Grace Blackwell, ex: `HEC45801`, `HEC45803`), 128 Go de mémoire unifiée, Ubuntu 24.04 LTS. Image Docker unifiée : `nvcr.io/nvidia/pytorch:26.05-py3` (Python 3.12, PyTorch 2.12, CUDA 13.2).
* **Headnode (AMD x86_64 Dual-Mode)** : 2x GPU NVIDIA RTX 3090 (48 Go VRAM), 125 Go RAM, AMD Ryzen 9 3900X, Ubuntu 20.04. Sert de **Serveur Scheduler API & Dashboard** et d'**Exécuteur** (mode dual avec malus de placement `-1` pour prioriser les workers dédiés).
* **Règle Fondamentale : 1 Job = 1 Seule Machine au Maximum** : L'agent worker distant est mono-tâche (`single-threaded worker agent`, verrou `/tmp/cluster-worker.lock`). Un job DVC ne peut JAMAIS réserver plus d'une machine à la fois. Le scheduler alloue chaque job à un seul worker selon un algorithme First-Fit Bin-Packing avec Data Locality (P2P cache hits) et 8 Go de marge OS réservée (`OS_HEADROOM_GB = 8.0`).

---

## 2. Quelles sont les Règles Critiques et la Syntaxe du Fichier `.cluster-ci` ?

### Mode local et confidentialité

> [!IMPORTANT]
> "Ensure the local mode is always implemented and respected in new features. The only exceptions are 1) the console logs and other general metrics that are made available on the local network for the dashboard and 2) the files that are available on the local network but protected by the cluster token. In no case should a job submitted with the --local flag or its associated data be uploaded to a third-party server, including GitHub, or served publicly."

> [!CAUTION]
> **INTERDICTION ABSOLUE DE MODIFIER LE FICHIER `.cluster-ci` SANS L'AUTORISATION EXPLICITE DE L'UTILISATEUR.**
> Antigravity et les sous-agents ne doivent sous AUCUN PRÉTEXTE modifier, altérer ou écraser `.cluster-ci` de leur propre initiative.

### Structure de `.cluster-ci`
Situé à la racine du projet de recherche.
```ini
# Resource Requirements
REQUIRED_RAM=16GB       # RAM minimale requise (le Headnode réserve 8GB de marge OS par nœud)
REQUIRED_VRAM=24GB      # VRAM minimale requise (0 = éligible CPU seul ; contrainte par GPU physique)
MAX_RUNTIME_HOURS=24    # Limite absolue d'exécution (1 à 24 heures)

# Execution Control
ALLOWED_WORKERS=HEC45801,HEC45803 # Whitelist de nœuds optionnelle
STAGES=train             # Sous-ensemble d'étapes DVC (par défaut 'dvc repro' complet si absent ou 'all')

# Web App Support
EXPOSED_PORT=8501       # Redirection de port Streamlit/Gradio
CUSTOM_WEB_APP=true     # Redirige vers une web app personnalisée au lieu de DVC-Viewer

# Overrides Docker (Supports _ARM64 et _AMD64)
DOCKER_IMAGE_ARM64=nvcr.io/nvidia/pytorch:26.05-py3
DOCKER_IMAGE_AMD64=custom-registry/image:latest
DOCKER_FLAGS=--cap-add=SYS_NICE
```

### 🎯 Ciblage Fin d'Étapes ou d'un Dataset Unique via `STAGES`
* **Ciblage d'un Dataset Unique (Syntaxe Foreach DVC)** : `STAGES=step_compare_metrics@amazon-video-games`
* **Résolution Automatique du Sous-DAG** : `dvc_iterative_repro.py` parse le graphe via `dvc dag --dot` et extrait récursivement **la cible et tous ses ancêtres amont**.
* **Multi-cibles** : Séparer par une virgule ou un espace (`STAGES=step_a,step_b`).

---

## 3. Quel Mode de Lancement Choisir Selon le Contexte Opérationnel ?

> [!CAUTION]
> **RÈGLE D'OR EN DÉVELOPPEMENT ACTIF — TOUJOURS UTILISER LA COMMANDE `cluster-run` DANS LE TERMINAL (BOUCLE SYNCHRONE DE LOGS EN DIRECT SANS VPN UNIL) :**
> 1. **En développement actif / session interactive avec Henri (quelle que soit la durée du run)** : Utiliser **TOUJOURS** la commande CLI **`cluster-run`** dans le terminal. Elle lance une **boucle synchrone qui redirige et affiche les logs en direct via `ppng.io` (et dans `.cluster-ci-logs/`) même lorsque le PC n'est PAS connecté au VPN de l'UNIL**.
> 2. **Interdiction d'invoquer l'absence de VPN UNIL** : Ne jamais dire « comme ton PC n'est pas connecté au VPN de l'UNIL, je n'ai pas les logs en direct ». La commande `cluster-run` fournit le flux de logs en direct sans VPN.
> 3. **Mode Background sans logs en direct (`git tag cluster-run` / `gh workflow run`)** : Un simple commit + push du tag `cluster-run` (ou `gh workflow run`) fait tourner le job en background sur le cluster **sans redirection de logs en direct** (seuls les commits de fin d'étape de `cluster-ci-bot` remontent sur Git). Ne l'utiliser que si le PC doit être éteint (`/shutdown-pc`), en session autonome `/advance`, ou pour occuper un 2e worker en parallèle d'un `cluster-run` actif.

### 🧭 Matrice de Décision : Quel Mode de Lancement Choisir ?

| Contexte / Objectif | Mode Recommandé | Logs & Visibilité (SANS VPN UNIL) | Concurrence & File | Comportement Terminal |
|---|---|---|---|---|
| **Développement actif / Session interactive (DÉFAUT OBLIGATOIRE)** | **Mode B (`cluster-run` CLI dans le terminal)** | **Boucle synchrone affichant les logs en DIRECT (`ppng.io` + `.cluster-ci-logs/`, fonctionne 100 % SANS VPN UNIL)** | **1 seul run actif à la fois** par chercheur (cross-repo) ; itératif | ⚠️ **La boucle synchrone doit rester ouverte** pendant tout le job |
| **PC bientôt éteint (`/shutdown-pc`) ou `/advance` autonome** | **Mode A (Tag `cluster-run` / `gh workflow run`)** | **Tourne en background sans logs en direct** ; métriques, plots et `dvc.lock` poussés à chaque fin de stage par `cluster-ci-bot` | **Au plus 1 en exécution + 1 en file d'attente par branche** | ✅ **Ordinateur peut être éteint** immédiatement |
| **Parallélisme 2 machines immédiat** | **Hybride (Mode A + Mode B)** | 1 job en direct (Mode B `cluster-run`) + 1 job en background (Mode A) | 2 workers occupés simultanément sans créer de branches manuelles | Variable selon le job |

### 🖥️ Mode B : Boucle Synchrone en Direct (`cluster-run` CLI) — DÉFAUT EN DÉVELOPPEMENT ACTIF

> [!IMPORTANT]
> **Quand l'utiliser** : **Systématiquement en développement actif et session interactive**, même pour des entraînements longs, dès lors que le PC reste allumé et qu'on veut suivre les logs en direct sans VPN UNIL.

- **Déclenchement** : Lancer `cluster-run` à la racine du dépôt dans le terminal (en tâche de fond locale maintenue ouverte sous Antigravity, `WaitMsBeforeAsync=5000`).
- **Fonctionnement interne & Redirection des logs sans VPN** : La commande locale `cluster-run` crée un shadow commit poussé sur la branche temporaire `cluster-draft/<user>` et sur le tag `cluster-run`. Elle enregistre son **PID local** dans `.cluster-ci-run.json` et **lance une boucle synchrone qui streame les logs en direct dans le terminal et dans `.cluster-ci-logs/` via `ppng.io` (sans nécessiter le VPN UNIL)**.
- **Retour des résultats** : À la fin du run, la CLI extrait automatiquement les métriques, plots et `dvc.lock` depuis la branche draft vers l'espace de travail local via `fetch_cluster_results` (checkout direct des fichiers modifiés).
- **Obligation de maintien ouvert** : **La commande `cluster-run` DOIT impérativement rester ouverte pendant tout le job**. Si le processus local est interrompu ou tué, `cleanup()` déclenche `cancel_and_cleanup_run()` et arrête le job distant.
- **Règle stricte d'auto-cancellation** : Politique `draft:same_user_cross_repo` (1 seul run draft actif par chercheur tous dépôts confondus). Le flag `--background` n'existe pas.

### 🚀 Mode A : Background Pur sans Logs en Direct (Git Tag / Workflow Dispatch) — NUIT PC ÉTEINT OU `/advance`

> [!WARNING]
> **Quand l'utiliser** : Uniquement quand l'ordinateur va être éteint, en session autonome `/advance`, ou pour lancer un 2e job en parallèle sur le second worker. **En Mode A, le job tourne en background sans flux de logs en direct hors VPN.**

1. **Commit, Push & Déclenchement** :
   ```bash
   git add . && git commit -m "feat(pipeline): description" && git push origin <branche_active>
   git tag -f cluster-run && git push -f origin cluster-run
   # OU alternative sans collision de tag :
   gh workflow run cluster-ci.yml --ref <branche_active>
   ```
2. **Comportement Système** :
   - **Immunité à l'extinction du PC** : Le PC peut être éteint immédiatement.
   - **Publication continue après chaque étape (`dvc.lock` & cache DVC)** : À chaque complétion de stage DVC, `dvc_iterative_repro.py` pousse les sorties déclarées dans `outs:` vers le cache DVC partagé du cluster et `cluster-ci-bot` committe/pousse immédiatement les métriques, plots et `dvc.lock` sur `<branche_active>` (`chore(ci): auto-sync metrics and dvc.lock [skip ci]`). Les étapes déjà validées dont les entrées n'ont pas changé ne sont donc jamais réexécutées.
   - **Rapatriement des résultats** : `git pull origin <branche_active>`.

### 🏠 Mode C : Exécution Directe sur Données Sensibles (`cluster-run --local`)
Pour les jeux de données sous embargo ou confidentiels ne devant pas transiter par GitHub, `cluster-run --local` transfère directement le dossier de travail vers le Headnode via l'API locale (zéro push Git/GitHub).

### 🚦 Quelles Sont les Règles Exactes de File d'Attente et de Concurrence ?
1. **Règle 1 Actif + 1 en File** : Sur une branche donnée, au plus 1 job en exécution (`running`/`assigned`) et 1 job en file d'attente (`pending`).
2. **Parallélisme Multi-Branches (`workflow_dispatch`)** : Pour lancer 2 jobs en parallèle sur 2 branches en Mode A, utiliser `gh workflow run cluster-ci.yml --ref <branche>`.

---

## 4. Comment Configurer dvc.yaml et Garantir la Connectivité du DAG ?

> [!IMPORTANT]
> **Chaque étape (`stage`) du pipeline dans `dvc.yaml` DOIT OBLIGATOIREMENT comporter des métriques (`metrics:`) ou des plots (`plots:`) configurés avec `{cache: false}`**, tandis que les artefacts lourds (datasets générés, paires inversées, poids de modèles) vont dans **`outs:`** (mis en cache automatiquement par DVC pour éviter toute réexécution lors des runs suivants).

### 4.1 Exemple Standard de `dvc.yaml`
```yaml
stages:
  preprocess:
    cmd: python scripts/preprocess.py
    deps:
      - data/raw/
    outs:
      - data/processed/
    metrics:
      - metrics/data_stats.json:
          cache: false

  train:
    cmd: python scripts/train.py
    deps:
      - data/processed/
      - scripts/train.py
    outs:
      - models/model.pt
    metrics:
      - metrics/train_metrics.json:
          cache: false
    plots:
      - plots/learning_curves.csv:
          cache: false
          x: epoch
          y: val_loss
```

### 4.2 Doctrine de Connectivité Stricte du DAG (Zéro Nœuds Orphelins) (MANDATOIRE)
1. **Arbre Strictement Connecté** : Toute étape doit avoir au moins une `deps` amont et voir ses sorties consommées en aval.
2. **Interdiction des Étapes Éphémères Flottantes** : Aucun script de test/ping ne doit figurer dans `dvc.yaml`.
3. **Audit de Connectivité Avant Lancement** : Vérifier `dvc dag` avant tout run.

---

## 5. Quelles Sont les Commandes CLI Client et Comment Inspecter l'État du Cluster ?

| Commande | Action & Rôle Opérationnel |
|---|---|
| `cluster-run` | **Défaut en développement actif** : soumet un shadow commit sur `cluster-draft/<user>`, lance la **boucle synchrone de logs en direct via `ppng.io` (sans VPN)** et extrait les résultats à la fin |
| `cluster-run --local` | Soumission directe au Headnode sans transit Git/GitHub pour données sensibles |
| `cluster-run list` | Affiche l'historique et le statut des runs récents (`gh run list --workflow "Cluster-CI Execution"`) |
| `cluster-run view [run_id]` | Affiche les logs d'un run spécifique |
| `cluster-run cancel [run_id]` | Arrête le conteneur sur le Headnode, annule le workflow GHA et purge l'état local |
| `cluster-run sync` | Synchronisation manuelle des métriques, plots et `dvc.lock` depuis la branche distante |

---

## 6. Quel est le Protocole de Gestion par l'Agent & Auto-Recovery ?

> [!IMPORTANT]
> 1. **Sélection du Mode** :
>    - **En développement actif / session interactive (DÉFAUT)** : Toujours lancer `cluster-run` dans le terminal (boucle synchrone maintenue ouverte) pour disposer des logs en direct via `ppng.io` et `.cluster-ci-logs/` sans VPN UNIL.
>    - **En autonomie nocturne PC éteint ou `/advance`** : Utiliser le Mode A (`git tag -f cluster-run && git push -f origin cluster-run` ou `gh workflow run`), qui tourne en background sans logs en direct.
> 2. **Auto-Recovery en cas d'échec** : Lire l'erreur exacte dans les logs de `cluster-run` (`.cluster-ci-logs/`), corriger la cause racine (sans toucher à `.cluster-ci` sans accord), et relancer `cluster-run`.
> 3. **Audit Critique Manuel des Sorties Intermédiaires (Zéro test unitaire, Zéro confiance aveugle dans les moyennes)** : À chaque étape d'un pipeline DVC (extraction, génération synthétique, entraînement, évaluation), **ne jamais se contenter d'un code retour `0` ni d'une métrique agrégée** : ouvrir et lire manuellement un échantillon réel des données intermédiaires produites à chaque étape (ex. vérifier qu'un corpus dit « humain » ne contient pas de listes à puces IA, qu'une reformulation ne boucle pas ou ne recopie pas l'entrée à 95 %, que la loss converge réellement, et valider les sorties finales sur le vrai canal externe comme `gptzero.me` via Playwright plutôt que sur un seul proxy local).

---

## 7. Comment Exploiter Simultanément les 2 Machines GB10 en Parallèle ?

* **Approche 1 (Recommandée, sans branches manuelles)** : 1 job en background sur `main` (Mode A : `gh workflow run cluster-ci.yml --ref main`) sur le 1er worker + 1 job en direct via `cluster-run` (`cluster-draft/<user>`) sur le 2e worker.
* **Approche 2 (Branches dédiées en urgence uniquement)** : Créer 2 branches, lancer `gh workflow run cluster-ci.yml --ref <branche>` sur chacune, puis fusionner et **supprimer immédiatement les branches temporaires** (`git branch -d` + `git push origin --delete`).

---

## 8. Dashboard Web & Sécurité Anti-Zombie

* **Dashboard Web (sous VPN UNIL)** : `http://130.223.73.209:5000/` (`scheduler_status`, `workers`, logs segmentés, MD5 clustering).
* **Mécanismes Anti-Zombie** : Verrou `/tmp/cluster-worker.lock`, `SIGKILL` hôte sur PID Docker avant `docker rm -f`, libération VRAM Ollama (`keep_alive: 0`), et auto-cancellation des runs draft du même chercheur.
