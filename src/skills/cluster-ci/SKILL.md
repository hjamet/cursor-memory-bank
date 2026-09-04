---
name: cluster-ci
description: Guide complet, architecture matérielle, commandes CLI, architecture duale (Mode A Asynchrone GitOps pur vs Mode B Synchrone CLI), règles de configuration DVC/GitOps et protocole d'auto-recovery pour l'orchestrateur cluster-ci.
---

# Skill cluster-ci — Orchestrateur GitOps & Pipeline GPU Cluster

## 1. Vision Générale et Architecture Matérielle

**Cluster-CI** est un orchestrateur minimaliste et décentralisé basé sur GitOps pour le traitement de jeux de données et l'entraînement de modèles Deep Learning sur un cluster de GPU hétérogènes. Il remplace Slurm/Ray par un modèle pull-based utilisant des exécuteurs GitHub Actions (GHA) auto-hébergés, Docker et DVC.

### Topologie Matérielle
* **Workers (ARM64 Executors)** : Nœuds NVIDIA GB10 (Grace Blackwell), 128 Go de mémoire unifiée, Ubuntu 24.04 LTS. Image Docker : `nvcr.io/nvidia/pytorch:26.05-py3` (Python 3.12, PyTorch 2.12, CUDA 13.2).
* **Headnode (AMD x86_64 Dual-Mode)** : 2x GPU NVIDIA RTX 3090 (48 Go VRAM), 125 Go RAM, AMD Ryzen 9 3900X, Ubuntu 20.04. Sert de **Serveur Scheduler API & Dashboard** et d'**Exécuteur** (mode dual).

---

## 2. Règle Critique & Sécurité : Fichier `.cluster-ci`

> [!CAUTION]
> **INTERDICTION ABSOLUE DE MODIFIER LE FICHIER `.cluster-ci` SANS L'AUTORISATION EXPLICITE DE L'UTILISATEUR.**
> Antigravity et les sous-agents ne doivent sous AUCUN PRÉTEXTE modifier, altérer ou écraser `.cluster-ci` de leur propre initiative.

### Structure de `.cluster-ci`
Situé à la racine du projet de recherche.
```ini
# Resource Requirements
REQUIRED_RAM=16GB       # RAM minimale requise (le Headnode réserve 8GB de marge OS par nœud)
REQUIRED_VRAM=24GB      # VRAM minimale requise (0 = éligible CPU seul)
MAX_RUNTIME_HOURS=24    # Limite absolue d'exécution (1 à 24 heures)

# Execution Control
ALLOWED_WORKERS=gb10-node1,gb10-node2 # Whitelist de nœuds optionnelle
STAGES=train             # Sous-ensemble d'étapes DVC (par défaut 'dvc repro')

# Web App Support
EXPOSED_PORT=8501       # Redirection de port Streamlit/Gradio
CUSTOM_WEB_APP=true     # Redirige vers une web app personnalisée au lieu de DVC-Viewer

# Overrides Docker (Supports _ARM64 et _AMD64)
DOCKER_IMAGE_ARM64=nvcr.io/nvidia/pytorch:26.05-py3
DOCKER_IMAGE_AMD64=custom-registry/image:latest
DOCKER_FLAGS=--cap-add=SYS_NICE
```

---

## 3. Architecture Duale : Choisir le Bon Mode d'Exécution (MANDATOIRE)

Cluster-CI opère selon deux modes d'exécution distincts. Le choix du mode est critique pour la résilience des calculs.

### 🚀 Mode A : Asynchrone Autonome (GitOps Pur) — RECOMMANDÉ PAR DÉFAUT

> [!IMPORTANT]
> **Quand l'utiliser** : Pour TOUT entraînement long, expérience de nuit, week-end, ou dès que l'utilisateur risque d'éteindre sa machine, fermer son terminal ou perdre sa connexion réseau.

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
3. **Comportement Système & Immunité Totale** :
   - **ZÉRO processus local** : Interdiction d'appeler `cluster-run` en CLI locale. Aucun PID n'est surveillé localement.
   - **Immunité à l'extinction du PC** : Le PC de développement peut être éteint dans la seconde qui suit le push du tag. Le conteneur Docker et le job GitHub Actions continuent de tourner sur le cluster sans interruption.
   - **Publication automatique des résultats** : Le script distant `run_research_pipeline.sh` résout dynamiquement la branche via `git branch -r --contains HEAD`. À la fin du calcul, le démon distant `dvc_git_helper.py` committe et pousse automatiquement les métriques, figures et `dvc.lock` sur `<branche_active>`.
   - **Rapatriement des résultats** : L'utilisateur ou l'agent récupère les artefacts au réveil via un simple :
     ```bash
     git pull origin <branche_active>
     ```

### 🖥️ Mode B : Synchrone Interactif (`cluster-run` CLI)

> [!WARNING]
> **Quand l'utiliser** : EXCLUSIVEMENT pour du débogage interactif court (≤ 15 min) lorsque l'utilisateur reste physiquement devant son écran pour observer le streaming des logs en direct.

- **Fonctionnement interne** : La commande locale `cluster-run` crée un shadow commit sur une branche temporaire `cluster-draft/<user>`, enregistre le **PID local** dans `.cluster-ci-run.json` et streame les logs dans le terminal.
- **Comportement destructeur en cas d'extinction** : Si le processus local est interrompu (fermeture de fenêtre, arrêt machine, veille), la fonction `recover_orphaned_run()` détecte la disparition du PID local, conclut à un abandon et **déclenche l'annulation immédiate du job (`cancel_and_cleanup_run()`)**, tuant le conteneur Docker sur le cluster.
- **Interdiction formelle** : Ne JAMAIS utiliser ce mode pour des exécutions longues ou de nuit.
- **Drapeau halluciné éliminé** : Le flag `--background` N'EXISTE PAS dans la CLI `cluster-run`. Tout besoin d'exécution en arrière-plan relève obligatoirement du **Mode A (GitOps Pur)**.

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
| `cluster-run list` | Affiche l'historique récent des runs avec ID, statut et timestamps |
| `cluster-run view [run_id]` | Affiche les logs d'un run spécifique (dernier run par défaut) |
| `cluster-run cancel [run_id]` | Demande l'annulation distante d'un run et nettoie le tracking local |
| `cluster-run sync` | Synchronise manuellement les métriques, plots et `dvc.lock` locaux depuis la branche distante |

> [!CAUTION]
> **Élimination formelle du drapeau `--background`** : L'option `cluster-run --background` est une hallucination et n'existe pas. Pour tout travail en arrière-plan ou déconnecté, utiliser le **Mode A : Git tag `cluster-run`**.

---

## 6. Protocole de Gestion par l'Agent & Auto-Recovery

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
