---
name: cluster-ci
description: "Orchestration DVC, GitOps et pipelines d'entraînement sur cluster GPU."
---
# Skill cluster-ci — Orchestrateur GitOps & Pipeline GPU Cluster

## 1. Quelle est l'Architecture Matérielle et la Topologie du Cluster ?

**Cluster-CI** est un orchestrateur minimaliste et décentralisé basé sur GitOps pour le traitement de jeux de données et l'entraînement de modèles Deep Learning sur un cluster de GPU hétérogènes. Il remplace Slurm/Ray par un modèle pull-based utilisant des exécuteurs GitHub Actions (GHA) auto-hébergés, Docker et DVC.

### Topologie Matérielle & Règle d'Allocation
* **Workers (ARM64 Executors)** : 2 nœuds physiques dédiés NVIDIA GB10 (Grace Blackwell — ex: `HEC45801`, `HEC45803`), 128 Go de mémoire unifiée, Ubuntu 24.04 LTS. Image Docker unifiée : `nvcr.io/nvidia/pytorch:26.05-py3` (Python 3.12, PyTorch 2.12, CUDA 13.2).
* **Headnode (AMD x86_64 Dual-Mode)** : 2x GPU NVIDIA RTX 3090 (48 Go VRAM), 125 Go RAM, AMD Ryzen 9 3900X, Ubuntu 20.04. Sert de **Serveur Scheduler API & Dashboard** et d'**Exécuteur** (mode dual avec malus de placement `-1` pour prioriser les workers dédiés).
* **Règle Fondamentale : 1 Job = 1 Seule Machine au Maximum** : L'agent worker distant est mono-tâche (`single-threaded worker agent`, verrou `/tmp/cluster-worker.lock`). Un job DVC ne peut JAMAIS réserver plus d'une machine à la fois. Le scheduler alloue chaque job à un seul worker selon un algorithme First-Fit Bin-Packing avec Data Locality (P2P cache hits) et 8 Go de marge OS réservée (`OS_HEADROOM_GB = 8.0`).

---

## 2. Quelles sont les Règles Critiques et la Syntaxe du Fichier `.cluster-ci` ?

### Mode local et confidentialité

> [!IMPORTANT]
> "Ensure the local mode is always implemented and respected in new features. The only exceptions are 1) the console logs and other general metrics that are made available on the local network for the dashboard and 2) the files that are available on the local network but protected by the cluster token. In no case should a job submitted with the --local flag or its associated data be uploaded to a third-party server, including GitHub, or served publicly. The threat model to use for this is the following: everyone on the cluster (GitHub org access to the cluster token) is fully trusted (e.g., containers are considered a convenience and not a security feature, and container isolation features can be ignored), the local network is trusted for console outputs and job metadata, and public web access or third-party servers are completely off limits."
>
> Toute nouvelle fonctionnalité doit être vérifiée contre cette règle (uploads GitHub du bot, streaming de logs vers des services tiers comme ppng.io, endpoints HTTP CAS des workers, dashboard).

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
* **Ciblage d'un Dataset Unique (Syntaxe Foreach DVC)** :
  Pour les étapes utilisant `foreach: ${datasets}` dans `dvc.yaml`, DVC instancie des nœuds nommés `<nom_étape>@<nom_dataset>`. Pour cibler un dataset unique, renseigner l'étape terminale souhaitée :
  ```ini
  STAGES=step_compare_metrics@amazon-video-games
  ```
* **Résolution Automatique du Sous-DAG** :
  Le moteur distant `dvc_iterative_repro.py` parse le graphe via `dvc dag --dot`. Dès qu'une cible est spécifiée dans `STAGES`, il extrait récursivement **la cible et tous ses ancêtres amont** dans le DAG, garantissant l'exécution complète et étanche de la chaîne de calcul pour ce dataset précis (du prétraitement à l'évaluation), sans toucher aux autres datasets.
* **Multi-cibles** : Plusieurs étapes peuvent être spécifiées séparées par une virgule ou un espace (ex: `STAGES=step_compare_metrics@amazon-video-games,step_compare_metrics@amazon-books`).

---

## 3. Quel Mode de Lancement Choisir Selon le Contexte Opérationnel ?

Cluster-CI propose deux modes d'exécution principaux (et un mode local sécurisé). Le tag technique unique écouté par GitHub Actions (`.github/workflows/cluster-ci.yml`) est **`cluster-run`**.

### 🧭 Matrice de Décision : Quel Mode de Lancement Choisir ?

| Contexte / Objectif | Mode Recommandé | Logs & Visibilité | Concurrence & File | Comportement Terminal |
|---|---|---|---|---|
| **Tests & Débogage rapide** | **Mode B (`cluster-run` CLI)** | Logs en DIRECT dans le terminal (`ppng.io` + `.cluster-ci-logs/`) | **1 seul run actif à la fois** par chercheur (cross-repo) ; itératif | ⚠️ **Doit rester ouvert** pendant tout le job (sinon auto-annulation) |
| **Nuit, Absence & Longs runs** | **Mode A (GitOps / Tag)** | Logs GHA à la fin ; métriques & plots au fil de l'eau par le bot | **Au plus 1 en exécution + 1 en file d'attente par branche** | ✅ **Ordinateur peut être éteint** immédiatement |
| **Parallélisme 2 machines immédiat** | **Hybride (Mode A + Mode B)** | 1 job en direct (Mode B) + 1 job en arrière-plan (Mode A) | 2 workers occupés simultanément sans créer de branches manuelles | Variable selon le job |
| **Parallélisme multi-branches** | **Branches temporaires dédiées (urgence uniquement, suppression immédiate après usage)** | Suivi via Dashboard Web (`:5000`) ou GHA | 1 job par branche en parallèle ; branches purgées post-merge | ✅ Ordinateur peut être éteint |

### 🚀 Mode A : Asynchrone Autonome (GitOps Pur) — RECOMMANDÉ POUR LA NUIT & RUNS LONGS

> [!IMPORTANT]
> **Quand l'utiliser** : Pour TOUT entraînement long (> 15 min), expérience de nuit, week-end, ou dès que l'utilisateur risque d'éteindre sa machine, fermer son terminal ou perdre sa connexion réseau.

1. **Commit & Push sur la branche de travail** :
   ```bash
   git add .
   git commit -m "feat(pipeline): description des changements"
   git push origin <branche_active>
   ```
2. **Déclenchement via Tag Technique Unique `cluster-run` ou Workflow Dispatch** :
   ```bash
   git tag -f cluster-run && git push -f origin cluster-run
   # OU alternative propre sans collision de tag :
   gh workflow run cluster-ci.yml --ref <branche_active>
   ```
3. **Comportement Système & Immunité Totale** :
   - **ZÉRO processus local** : Interdiction d'appeler `cluster-run` en CLI locale. Aucun PID n'est surveillé localement.
   - **Immunité à l'extinction du PC** : Le PC de développement peut être éteint dans la seconde qui suit le push du tag. Le conteneur Docker et le job GitHub Actions continuent de tourner sur le cluster sans interruption.
   - **Résolution automatique de la branche** : Le script distant `run_research_pipeline.sh` résout dynamiquement la vraie branche cible via `git branch -r --contains HEAD` (priorité 1 aux branches non-draft).
   - **Publication continue au fil de l'eau (après chaque étape réussie)** : À chaque complétion de stage, `dvc_iterative_repro.py` appelle `dvc_git_helper.py sync`. Le bot `cluster-ci-bot` committe (`chore(ci): auto-sync metrics and dvc.lock [skip ci]`) et pousse **immédiatement** les métriques, plots et `dvc.lock` sur `<branche_active>`. Les résultats sont ainsi sécurisés en direct sur GitHub même en cas d'interruption ultérieure.
   - **Rapatriement des résultats** : L'utilisateur ou l'agent récupère les artefacts au réveil ou au fil de l'eau via un simple :
     ```bash
     git pull origin <branche_active>
     ```
   - **Logs et Suivi** : Télémétrie en temps réel via le Dashboard Web (`http://130.223.73.209:5000/`) sous VPN UNIL. Les logs intégraux de la console sont archivés sur GitHub Actions à la complétion du run (`gh run view --log`).

### 🖥️ Mode B : Synchrone Interactif (`cluster-run` CLI) — RECOMMANDÉ POUR TESTS & DÉBOGAGE

> [!WARNING]
> **Quand l'utiliser** : Pour du débogage interactif court (≤ 15 min), des tests de configuration, ou une supervision active sous le skill [`monitor-command`](file:///c:/Users/hjamet/Documents/VoiceNotes/_agents/skills/monitor-command/SKILL.md) (contrôle Fail-Fast T+30s/T+90s et fraîcheur).

- **Déclenchement** : Commande `cluster-run` à la racine du dépôt (installée dans `$HOME/.local/bin/cluster-run` ou environnement Python local).
- **Fonctionnement interne** : La commande locale `cluster-run` crée un shadow commit (incluant fichiers modifiés et untracked) poussé sur la branche temporaire `cluster-draft/<user>` et sur le tag `cluster-run`. Elle enregistre son **PID local** dans `.cluster-ci-run.json` et streame les logs dans le terminal en direct via `ppng.io`.
- **Retour des résultats** : À la fin du run, la CLI extrait automatiquement les métriques, plots et `dvc.lock` depuis la branche draft vers l'espace de travail local via `fetch_cluster_results` (checkout direct des fichiers modifiés, sans fusion git dans l'historique).
- **Obligation de maintien ouvert** : **La commande DOIT impérativement rester ouverte pendant tout le job**. Si le processus local est interrompu (Ctrl+C, SIGINT, fermeture terminal), `cleanup()` déclenche `cancel_and_cleanup_run()`, arrêtant le conteneur sur le Headnode (`_headnode_stop_job`) et annulant le job GHA (`gh run cancel`). Si le processus est tué brutalement (SIGKILL), `recover_orphaned_run()` détecte la perte du PID au prochain lancement et purge le run orphelin.
- **Règle stricte d'auto-cancellation** : Le scheduler applique la règle `draft:same_user_cross_repo` : **1 seul run draft actif par chercheur** tous dépôts confondus. Tout nouveau draft annule immédiatement le précédent.
- **Drapeau halluciné éliminé** : Le flag `--background` N'EXISTE PAS dans la CLI `cluster-run`. Tout besoin d'arrière-plan relève du **Mode A**.

### 🏠 Mode C : Exécution Directe sur Données Sensibles (`cluster-run --local`)
Pour les jeux de données sous embargo, confidentiels ou volumineux ne devant pas transiter par GitHub, la commande `cluster-run --local` transfère directement le dossier de travail vers le Headnode via l'API locale (`HTTP 400 fail-fast`, zéro push Git/GitHub).

### 🚦 Quelles Sont les Règles Exactes de File d'Attente et de Concurrence ?
1. **Règle 1 Actif + 1 en File** : Sur une branche donnée, il y a **au plus 1 job en exécution (`running` ou `assigned`) et 1 job en file d'attente (`pending`)**. Un 3e job remplace automatiquement celui en file d'attente.
2. **Portée PAR BRANCHE** :
   - Côté GitHub Actions : `concurrency: group: ${{ github.workflow }}-${{ github.actor }}-${{ github.ref_name }}` avec `cancel-in-progress: false` garantit qu'au plus 1 run est actif et 1 en attente par groupe.
   - Côté Headnode : La politique `branch:replace_pending` exécute `WHERE repo = ? AND branch = ? AND status = 'pending'`, annulant le pending précédent pour insérer le nouveau.
3. **Parallélisme Multi-Branches (`workflow_dispatch`)** : Pour lancer 2 jobs en parallèle sur 2 branches, utiliser obligatoirement `gh workflow run cluster-ci.yml --ref <branche>` et non le tag `cluster-run`. En mode tag, `ref_name` vaut « cluster-run » pour toutes les branches, regroupant les runs dans un groupe GHA unique (mise en file d'attente) ; avec `workflow_dispatch`, chaque branche possède son propre groupe GHA (`ref_name = <branche>`).

---

## 4. Comment Configurer dvc.yaml et Garantir la Connectivité du DAG ?

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

## 5. Quelles Sont les Commandes CLI Client et Comment Inspecter l'État du Cluster ?

### Commandes CLI Client (`cluster-run`)
| Commande | Action & Rôle Opérationnel |
|---|---|
| `cluster-run` | Soumet un shadow commit sur `cluster-draft/<user>`, streame les logs en direct et extrait les résultats à la fin (Mode B interactif) |
| `cluster-run --local` | Soumission directe au Headnode sans transit Git/GitHub pour données sensibles sous embargo |
| `cluster-run list` | Affiche l'historique et le statut des runs récents (`gh run list --workflow "Cluster-CI Execution"`) |
| `cluster-run view [run_id]` | Affiche les logs d'un run spécifique (stream direct si actif, ou logs historiques GHA) |
| `cluster-run cancel [run_id]` | Arrête le conteneur sur le Headnode (`/api/jobs/<id>/stop`), annule le workflow GHA (`gh run cancel`) et purge l'état local |
| `cluster-run sync` | Synchronisation manuelle des métriques, plots et `dvc.lock` depuis la branche distante |

### 🖥️ Panneau Dynamique de File d'Attente dans le Terminal
Lorsqu'un job `cluster-run` est en attente d'une machine libre, la CLI rafraîchit automatiquement toutes les 15s le bloc `⏳ FILE D'ATTENTE CLUSTER-CI` (`display_clean_queue_status`) :
* **Position dans la file** : Position exacte (`X / Y`) et temps d'attente maximum estimé.
* **Diagnostics de ressources** : Alerte immédiate si `REQUIRED_RAM` dépasse la capacité physique maximale du cluster.
* **État des machines** : Statut de chaque worker (`HEC45801`, `HEC45803`), nom du job en cours, utilisateur et durée écoulée.

### 🔍 Inspection d'État des Machines & Résolution des Auto-Blocages
1. **API Headnode directe (VPN UNIL)** :
   ```bash
   # État global du scheduler : workers actifs + file d'attente
   curl -s http://130.223.73.209:5000/scheduler_status
   # Caractéristiques matérielles et RAM/VRAM disponible par worker
   curl -s http://130.223.73.209:5000/workers
   ```
2. **Inspection via GitHub CLI** :
   ```bash
   gh run list --workflow cluster-ci.yml --limit 5
   gh run view <run_id>
   ```
3. **Comment vérifier et lever un auto-blocage ?**
   - **En Mode Draft (`cluster-draft/*`)** : Zéro blocage résiduel — tout nouveau `cluster-run` annule automatiquement le run précédent du chercheur (`draft:same_user_cross_repo`).
   - **En Mode Branche Standard (`main`, `feat/*`)** : Si un run antérieur tourne encore sur la même branche, la règle `branch_exclusivity` bloque tout nouveau job sur cette branche. Pour débloquer : annuler le run précédent via `cluster-run cancel <run_id>`, `gh run cancel <run_id>` ou le bouton **Stop** du Dashboard Web (`http://130.223.73.209:5000/`).

> [!CAUTION]
> **Élimination formelle du drapeau `--background`** : L'option `cluster-run --background` est une hallucination et n'existe pas. Pour tout travail en arrière-plan ou déconnecté, utiliser le **Mode A : Git tag `cluster-run`** ou `gh workflow run`.

---

## 6. Quel est le Protocole de Gestion par l'Agent & Auto-Recovery ?

> [!IMPORTANT]
> **Instructions d'exécution lors d'une demande de lancement de calculs :**
>
> 1. **Sélection du Mode** :
>    - **Par défaut / Runs longs (> 15 min) / Travail autonome** : Appliquer systématiquement le **Mode A (GitOps Pur)**. Committer, pusher la branche, puis taguer et pusher le tag `cluster-run`. Aucun process local ne doit tourner.
>    - **Débogage immédiat court (≤ 15 min)** : Si l'utilisateur demande explicitement un test direct interactif en séance, lancer `cluster-run` en foreground.
> 2. **Suivi périodique (si session active)** :
>    - Consulter l'état via le Dashboard Web (`http://130.223.73.209:5000/`) ou `cluster-run view`.
> 3. **Auto-Recovery & Résolution en cas d'échec** :
>    - Si le run échoue sur le cluster :
>      a. Analyser les logs pour identifier la cause exacte (code, mémoire CUDA OOM, dépendance manquante, syntaxe DVC, etc.).
>      b. Résoudre la cause racine dans le code ou les scripts (sans modifier `.cluster-ci` sans accord).
>      c. Committer et pusher le correctif.
>      d. Reposer et repousser le tag `cluster-run` (`git tag -f cluster-run && git push -f origin cluster-run`).
>      e. Répéter jusqu'à l'achèvement complet et réussi du pipeline.

## 7. Comment Exploiter Simultanément les 2 Machines GB10 en Parallèle ?

### ⚠️ Verrous et Contraintes du Scheduler
1. **1 Job = 1 Machine Maximum** : L'ordonnanceur (`scheduler_loop.py`) alloue chaque job à un seul worker. Un job unique ne peut pas distribuer ses calculs sur plusieurs machines.
2. **Exclusivité de Branche (`Branch-level exclusivity`)** : Le scheduler bloque (`branch_exclusivity`) tout second job soumis sur la **même branche** d'un dépôt tant que le premier est `running` ou `assigned`. Lancer deux jobs sur `main` ne les parallélisera jamais : le second attendra la fin du premier.
3. **Collision de Git Sync sur une Même Branche** : Deux jobs s'exécutant en parallèle sur la même branche génèrent des conflits de push Git et de rebase (`git rebase --abort`) lors des commits automatiques intermédiaires de `dvc.lock`.
4. **Collision des Runs Draft** : Deux commandes `cluster-run` CLI draft s'auto-annulent mutuellement via la politique `draft:same_user_cross_repo`.

### ⚡ Approche 1 : Parallélisme Immédiat Sans Branches (1 Run par Commit + 1 `cluster-run`)
Le moyen le plus direct et propre d'occuper simultanément les deux machines sans créer de branches Git manuelles :
* **Job 1 en tâche de fond (Mode A)** : Pousser un commit sur la branche de travail (`main` ou `feat/*`) et déclencher le run via `gh workflow run cluster-ci.yml --ref <branche>` (ou tag `cluster-run`). Le job s'exécute sur le premier worker libre (ex: `HEC45801`).
* **Job 2 interactif en direct (Mode B)** : Lancer localement `cluster-run` pour tester ou itérer. La CLI crée automatiquement la branche `cluster-draft/<user>`.
* **Isolation totale** : Comme `cluster-draft/<user>` est disjointe de la branche de travail, la contrainte `branch_exclusivity` ne s'applique pas. Le scheduler place immédiatement le second job sur le second worker libre (`HEC45803`). Les deux jobs tournent en parallèle sans aucune interférence.

### 🛠️ Approche 2 : Branches Dédiées Multi-Datasets (Tolérées Uniquement en Cas d'Urgence)
Pour paralléliser deux sous-pipelines de fond lourds (ex: dataset `amazon-video-games` et dataset `amazon-books` dans `llm-as-recommender`) :

> [!CAUTION]
> **Règle d'Hygiène Git & Roadmap** :
> 1. **Toléré en urgence uniquement** : La multiplication de branches Git manuelles est un pis-aller.
> 2. **Suppression systématique obligatoire** : Dès la fusion des résultats sur la branche principale, **supprimer impérativement les branches temporaires** (`git branch -d` et `git push origin --delete`).
> 3. **Roadmap Cluster-CI** : Inscrire dans la roadmap du projet le support natif de la distribution multi-stage/multi-dataset par l'orchestrateur sans nécessiter de branches Git éphémères.

1. **Création de Deux Branches Git Distinctes** :
   ```bash
   # Branche pour le premier dataset
   git checkout -b feat/cluster-dataset-vg
   # Configurer .cluster-ci : STAGES=step_compare_metrics@amazon-video-games
   git commit -am "ci: target amazon-video-games pipeline" && git push -u origin feat/cluster-dataset-vg

   # Branche pour le second dataset
   git checkout -b feat/cluster-dataset-books
   # Configurer .cluster-ci : STAGES=step_compare_metrics@amazon-books
   git commit -am "ci: target amazon-books pipeline" && git push -u origin feat/cluster-dataset-books
   ```

2. **Déclenchement Échelonné (Privilégier `workflow_dispatch`)** :
   ```bash
   # Job 1 sur première branche (isole le groupe de concurrence GHA) :
   gh workflow run cluster-ci.yml --ref feat/cluster-dataset-vg
   # Attendre le statut assigned/running sur le Dashboard Web, puis Job 2 :
   gh workflow run cluster-ci.yml --ref feat/cluster-dataset-books
   ```

3. **Réconciliation Sûre & Purge Immédiate des Branches** :
   ```bash
   # Rapatriement des résultats
   git fetch origin feat/cluster-dataset-vg feat/cluster-dataset-books
   git checkout main
   git merge origin/feat/cluster-dataset-vg -m "merge: results amazon-video-games"
   git merge origin/feat/cluster-dataset-books -m "merge: results amazon-books"
   # PURGE SYSTÉMATIQUE DES BRANCHES TEMPORAIRES (MANDATOIRE) :
   git branch -d feat/cluster-dataset-vg feat/cluster-dataset-books
   git push origin --delete feat/cluster-dataset-vg feat/cluster-dataset-books
   ```

---

## 8. Comment Accéder et Exploiter le Dashboard Web et la Télémétrie ?

* **URL d'accès** : `http://130.223.73.209:5000/` (Nécessite le VPN UNIL).
* **Fonctionnalités clés** :
  * **Télémétrie en direct** : Visualisation RAM/VRAM par nœud et causes d'attente (`branch_exclusivity`, `no_free_workers`, `insufficient_ram`).
  * **Logs segmentés** : Découpage par étape DVC avec indicateur de statut `☠️` et bouton "Last Error".
  * **MD5 Clustering & Slider temporel** : Regroupement des artefacts par hash MD5 et inspection chronologique.
  * **Hydra Inspector** : Visualisation de l'arborescence des paramètres Hydra YAML.

---

## 9. Quels sont les Mécanismes de Résilience et de Sécurité Anti-Zombie ?

1. **Single Instance Lock** : Verrou `/tmp/cluster-worker.lock` pour empêcher les exécutions concurrentes sur un même worker.
2. **PID Host SIGKILL (<5s)** : Récupération du PID hôte (`docker inspect`) et envoi d'un `SIGKILL` direct au noyau pour libérer les contextes CUDA gelés avant `docker rm -f`.
3. **Host Ollama VRAM Release** : Libération forcée de la VRAM d'Ollama via `POST http://127.0.0.1:11434/api/generate` avec `keep_alive: 0`.
4. **Auto-Cancellation** : 1 seul run actif par chercheur sur les branches draft (`cluster-draft/*`).
