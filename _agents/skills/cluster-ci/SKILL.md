---
name: cluster-ci
description: "Orchestration DVC, GitOps et pipelines d'entraînement sur cluster GPU."
---
# Skill cluster-ci — Orchestrateur GitOps & Pipeline GPU Cluster

## 1. Vision Générale et Architecture Matérielle

**Cluster-CI** est un orchestrateur minimaliste et décentralisé basé sur GitOps pour le traitement de jeux de données et l'entraînement de modèles Deep Learning sur un cluster de GPU hétérogènes. Il remplace Slurm/Ray par un modèle pull-based utilisant des exécuteurs GitHub Actions (GHA) auto-hébergés, Docker et DVC.

> [!IMPORTANT]
> **AUCUN VPN UNIL NI `eduroam` N'EST REQUIS POUR LANCER DES CALCULS SUR LE CLUSTER GPU.**
> Le déclenchement passe exclusivement par GitHub (`git tag -f cluster-run && git push -f origin cluster-run` en Mode A, ou `cluster-run` en Mode B) : **lancer et surveiller des jobs fonctionne depuis n'importe quelle connexion Internet (domicile, 4G, etc.)**. Seul l'affichage de l'interface web Dashboard (`http://130.223.73.209:5000/`) requiert le VPN UNIL ou `eduroam` — ne jamais prétendre qu'un calcul GPU est bloqué faute de VPN ou d'`eduroam`.

### Topologie Matérielle
* **Workers (ARM64 Executors)** : Nœuds NVIDIA GB10 (Grace Blackwell), 128 Go de mémoire unifiée, Ubuntu 24.04 LTS. Image Docker : `nvcr.io/nvidia/pytorch:26.05-py3` (Python 3.12, PyTorch 2.12, CUDA 13.2).
* **Headnode (AMD x86_64 Dual-Mode)** : 2x GPU NVIDIA RTX 3090 (48 Go VRAM), 125 Go RAM, AMD Ryzen 9 3900X, Ubuntu 20.04. Sert de **Serveur Scheduler API & Dashboard** et d'**Exécuteur** (mode dual).

---

## 2. Quelles sont les Règles Critiques et la Syntaxe du Fichier `.cluster-ci` & `meta.cluster` ?

### Mode local et confidentialité

> [!IMPORTANT]
> "Ensure the local mode is always implemented and respected in new features. The only exceptions are 1) the console logs and other general metrics that are made available on the local network for the dashboard and 2) the files that are available on the local network but protected by the cluster token. In no case should a job submitted with the --local flag or its associated data be uploaded to a third-party server, including GitHub, or served publicly."

### Structure de `.cluster-ci` (Minimaliste) et Spécifications par Nœud (`meta.cluster` dans `dvc.yaml`)

> [!IMPORTANT]
> **Cluster-CI v3 — Spécifications par Nœud dans `dvc.yaml` & Parallélisme DAG Automatique** :
> 1. **Ressources au niveau des nœuds (`stages.<stage>.meta.cluster`)** : déclarer `cpus`, `gpus`, `ram_gb`, `vram_gb`, `storage_gb`, `image`, `image_arm64`, `image_amd64`, `workers` et `priority` directement dans `dvc.yaml` plutôt que globalement dans `.cluster-ci`. Clés strictement validées en Fail-Fast ; `vram_gb > 0` exige `gpus >= 1`.
> 2. **Mémoire Unifiée GB10 (`ram_gb + vram_gb <= 120 GB`)** : sur les nœuds Grace Blackwell `GB10` (128 Go de mémoire unifiée, dont 8 Go de marge OS), le scheduler additionne `ram_gb + vram_gb` pour l'admission et la limite Docker `--memory`. Ne jamais demander `100 + 100 = 200 GB` (irréalisable sur aucune machine).
> 3. **Parallélisme DAG actif par défaut** : dès qu'un dépôt contient `dvc.yaml`, l'exécution DAG parallèle multi-workers est activée automatiquement par défaut (`PARALLEL_STAGES=false` permet uniquement un repli manuel vers l'ancien mode séquentiel). L'agent est autorisé à créer/mettre à jour `.cluster-ci` selon la documentation officielle du dépôt `UNIL-DESI/cluster-ci`.

Situé à la racine du projet de recherche (version minimaliste lorsque chaque stage déclare son propre `meta.cluster` dans `dvc.yaml`) :
```ini
# Durée maximale obligatoire (1 à 24 heures)
MAX_RUNTIME_HOURS=24

# Optionnel : priorité globale (high | normal | low | extra_low), whitelist globale ou ciblage d'étapes
# PRIORITY=normal
# ALLOWED_WORKERS=HEC45801,HEC45803
# STAGES=step_a,step_b

# Optionnel : Web App personnalisée (Streamlit/Gradio)
# EXPOSED_PORT=8501
# CUSTOM_WEB_APP=true
```

---

## 3. Architecture Duale : Choisir le Bon Mode d'Exécution (MANDATOIRE)

Cluster-CI opère selon deux modes d'exécution distincts. Le choix du mode est critique pour la résilience des calculs.

### 🖥️ Mode B : Synchrone Interactif (`cluster-run` CLI) — DÉFAUT EN DÉVELOPPEMENT ACTIF & SESSIONS SURVEILLÉES

> [!IMPORTANT]
> **Quand l'utiliser (DÉFAUT)** : Pour **tout développement actif, itération expérimentale ou session surveillée par l'agent** (y compris runs longs tant que le PC/agent reste actif). Permet d'obtenir les logs en direct (`ppng.io` + `.cluster-ci-logs/`), de voir l'attribution des nœuds en temps réel, de rapatrier immédiatement les résultats et d'itérer sans délai.

- **Fonctionnement interne** : La commande locale `cluster-run` crée un shadow commit sur une branche temporaire `cluster-draft/<user>`, enregistre le **PID local** dans `.cluster-ci-run.json` et streame les logs en direct. Lancée en tâche de fond dans le terminal de l'agent (`$env:PYTHONUNBUFFERED="1"`), elle reste vivante tant que la session/le PC reste actif.
- **Rapatriement 100 % automatique (zéro `git pull`)** : `cluster-run` (Shadow Push comme `--local`) synchronise automatiquement `metrics`, `plots` et `dvc.lock` localement toutes les `10 s`, à chaque push `[DVC-Git-Helper]`, et systématiquement en fin de run (même sur échec). Ne jamais demander de `git pull` après un `cluster-run` (`cluster-run sync` suffit en cas de coupure réseau).
- **Attention en cas d'extinction PC** : Si le processus local est tué brutalement (arrêt machine, veille), `recover_orphaned_run()` annule le job distant. Dans ce seul cas (PC qui va être éteint / `/advance` hors présence), basculer sur le **Mode A**.
- **Drapeau halluciné éliminé** : Le flag `--background` N'EXISTE PAS dans la CLI `cluster-run`.

### 🚀 Mode A : Asynchrone Déconnecté (Tag Git `cluster-run`) — UNIQUEMENT SI PC ÉTEINT / `/advance` HORS PRÉSENCE

> [!WARNING]
> **À éviter en développement actif** : le tag Git seul prive l'agent des logs en direct et de la synchro temps réel. Réserver le Mode A **exclusivement** aux runs lancés juste avant d'éteindre le PC ou en session autonome `/advance` sans terminal persistant.

1. **Commit & Push sur la branche de travail** :
   ```bash
   git add .
   git commit -m "feat(pipeline): description des changements"
   git push origin <branche_active>
   ```
2. **Déclenchement du Tag Technique `cluster-run`** :
   ```bash
   git tag -f cluster-run
   git push -f origin cluster-run
   ```
3. **Comportement Système & Rapatriement** :
   - **ZÉRO processus local** & **immunité à l'extinction du PC** : le démon distant `dvc_git_helper.py` committe et pousse les métriques, figures et `dvc.lock` sur `origin/<branche_active>`.
   - **Rapatriement des résultats (Mode A uniquement)** : Comme aucun processus local `cluster-run` ne tourne en Mode A, les résultats poussés sur `origin/<branche_active>` sont rapatriés par `git pull origin <branche_active>` — **exécuté automatiquement par la vigie `schedule` de l'agent à la fin du run** (ne jamais déléguer cette corvée dans la task list manuelle d'Henri).

---

## 4. Configuration `dvc.yaml` & Traçabilité Métriques / Plots (MANDATOIRE)

> [!IMPORTANT]
> **Chaque étape (`stage`) du pipeline dans `dvc.yaml` DOIT OBLIGATOIREMENT comporter des métriques (`metrics:`) ou des plots (`plots:`) configurés avec `{cache: false}`.**
> Cela permet :
> 1. Le suivi direct et continu de l'exécution sur le Dashboard Web.
> 2. L'exportation visuelle automatique des courbes d'apprentissage et tableaux d'évaluation.
> 3. Le commit automatique par le bot `cluster-ci-bot` à la fin de chaque étape.

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
      - plots/confusion_matrix.csv:
          cache: false
```

### 4.2 Doctrine de Connectivité Stricte du DAG (Zéro Nœuds Orphelins) (MANDATOIRE)

1. **Un Pipeline Doit Être un Arbre Strictement Connecté** :
   - Toute étape déclarée dans `dvc.yaml` DOIT impérativement posséder au moins une dépendance (`deps`) la reliant directement au flux de données amont (données brutes, modèles ou prédictions générées par une étape précédente).
   - Toute étape intermédiaire DOIT voir ses sorties (`outs`, `metrics` ou `plots`) consommées par au moins une étape aval (ex: étape finale d'agrégation, calcul global de métriques ou génération de figures).
2. **Interdiction Formelle des Étapes Éphémères Flottantes** :
   - Les scripts de vérification technique ponctuelle (ex: `check_together.py`, tests de ping API ou de credentials, étape flottante `step_check_together`) NE DOIVENT JAMAIS être enregistrés comme des étapes permanentes dans `dvc.yaml`.
   - Les vérifications d'environnement font partie intégrante des pré-requis du pipeline ou des scripts d'initialisation, pas du graphe de dépendances DVC.
3. **Audit de Connectivité Avant Tout Tag** :
   - Avant tout tag Git ou déclenchement de `cluster-run`, la commande `dvc dag` doit être inspectée : le graphe ne doit contenir STRICTEMENT AUCUN nœud déconnecté de la racine (`step_download_data` / `step_data_processing`) ou de la feuille finale (`step_global_compare_metrics`).

---

## 5. Commandes CLI Client (`cluster-run`) — Réservées au Mode B

| Commande | Description |
|---|---|
| `cluster-run` | Soumet un shadow commit, pousse la branche draft, suit les logs en direct et extrait les résultats une fois terminé (Mode B interactif) |
| `cluster-run queue` | Affiche en direct l'état des workers (GPU/RAM/jobs actifs) et la file d'attente ordonnée avec les préfixes `job_id` |
| `cluster-run list` | Affiche l'historique récent des runs avec ID, statut et timestamps |
| `cluster-run view [run_id]` | Affiche les logs d'un run spécifique (dernier run par défaut) |
| `cluster-run cancel [run_id \| --job-id <id>]` | Stoppe un job sur le Headnode (y compris `main` / `--local` via préfixe `job_id`) et annule le run GHA associé |
| `cluster-run sync` | Synchronise manuellement les métriques, plots et `dvc.lock` locaux depuis la branche distante |
| `cluster-update --hot` | Déploie `UNIL-DESI/cluster-ci` à chaud sur Headnode + workers **sans annuler aucun job en cours** (redémarrage control plane ~2 s + ré-adoption live des exécuteurs) |

> [!CAUTION]
> **Élimination formelle du drapeau `--background`** : L'option `cluster-run --background` est une hallucination et n'existe pas. Pour tout travail en arrière-plan ou déconnecté, utiliser le **Mode A : Git tag `cluster-run`**.

---

## 6. Protocole de Gestion par l'Agent & Auto-Recovery

> [!IMPORTANT]
> **Instructions d'exécution lors d'une demande de lancement de calculs :**
>
> 1. **Sélection du Mode** :
>    - **En développement actif / session surveillée (DÉFAUT)** : Toujours lancer `cluster-run` dans le terminal en tâche de fond (`$env:PYTHONUNBUFFERED="1"`) pour disposer des logs en direct via `ppng.io` et `.cluster-ci-logs/`, suivre l'attribution des nœuds en temps réel, bénéficier du rapatriement automatique (`metrics`/`plots`/`dvc.lock` sans `git pull`) et itérer immédiatement.
>    - **Exclusivement si le PC va être éteint ou en `/advance` hors présence** : Utiliser le Mode A (`git tag -f cluster-run && git push -f origin cluster-run`).
> 2. **Vigie Autonome Obligatoire (`schedule`) — Zéro Job Abandonné, Zéro Corvée Manuelle** : Dès qu'un job Cluster-CI est lancé (`cluster-run` en arrière-plan ou Mode A) ou en file d'attente derrière un autre chercheur, l'agent arme immédiatement un réveil périodique via `schedule` (ex. horaire `CronExpression: "0 * * * *"`, `MaxIterations: 24` en file/long run, ou double palier `monitor-command` dès démarrage) pour : (a) vérifier que le job ne reste jamais bloqué/zombie (logs de la tâche `cluster-run`, `/job_status/<id>`, `/scheduler_status`), (b) auto-diagnostiquer, corriger chirurgicalement et relancer en cas d'échec ou de gel (`> 20 min` sans log une fois actif), et (c) auditer les résultats dès la fin (`cluster-run` les rapatrie déjà automatiquement ; exécuter `git pull origin <branche>` soi-même uniquement en Mode A) puis mettre à jour la note projet. **Interdiction de déléguer la surveillance d'un job ou son rapatriement dans la task list d'Henri.**
> 3. **Auto-Recovery en cas d'échec** : Lire l'erreur exacte dans les logs (`cluster-run` `.cluster-ci-logs/` ou `/job_logs/<job_id>`), corriger la cause racine (y compris dans `dvc.yaml` `meta.cluster`, `.cluster-ci` ou le dépôt `cluster-ci` lui-même après `git pull`), et relancer `cluster-run`.
> 4. **Audit Critique Manuel des Sorties Intermédiaires (Zéro test unitaire, Zéro confiance aveugle dans les moyennes)** : À chaque étape d'un pipeline DVC (extraction, génération synthétique, entraînement, évaluation), **ne jamais se contenter d'un code retour `0` ni d'une métrique agrégée** : ouvrir et lire manuellement un échantillon réel des données intermédiaires produites à chaque étape (ex. vérifier qu'un corpus dit « humain » ne contient pas de listes à puces IA, qu'une reformulation ne boucle pas ou ne recopie pas l'entrée à 95 %, que la loss converge réellement, et valider les sorties finales sur le vrai canal externe comme `gptzero.me` via Playwright plutôt que sur un seul proxy local).

---

## 7. Dashboard Web & Télémétrie

* **URL d'accès** : `http://130.223.73.209:5000/` (Nécessite le VPN UNIL).
* **Fonctionnalités clés** :
  * **Télémétrie en direct** : Visualisation RAM/VRAM par nœud et causes d'attente (`branch_exclusivity`, `no_free_workers`, `insufficient_ram`).
  * **Logs segmentés** : Découpage par étape DVC avec indicateur de statut `☠️` et bouton "Last Error".
  * **MD5 Clustering & Slider temporel** : Regroupement des artefacts par hash MD5 et inspection chronologique.
  * **Hydra Inspector** : Visualisation de l'arborescence des paramètres Hydra YAML.

---

## 8. Résilience & Sécurité Anti-Zombie

1. **Single Instance Lock** : Verrou `/tmp/cluster-worker.lock` pour empêcher les exécutions concurrentes sur un même worker.
2. **PID Host SIGKILL (<5s)** : Récupération du PID hôte (`docker inspect`) et envoi d'un `SIGKILL` direct au noyau pour libérer les contextes CUDA gelés avant `docker rm -f`.
3. **Host Ollama VRAM Release** : Libération forcée de la VRAM d'Ollama via `POST http://127.0.0.1:11434/api/generate` avec `keep_alive: 0`.
4. **Auto-Cancellation** : 1 seul run actif par chercheur sur les branches draft (`cluster-draft/*`).
