---
name: cluster-ci
description: Guide complet, architecture, commandes CLI, règles de configuration DVC/GitOps et protocole d'exécution de cluster-run avec auto-recovery et suivi par métriques/plots pour l'orchestrateur cluster-ci.
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
Located à la racine du projet de recherche.
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

## 3. Configuration `dvc.yaml` & Traçabilité Métriques / Plots (MANDATOIRE)

> [!IMPORTANT]
> **Chaque étape (`stage`) du pipeline dans `dvc.yaml` DOIT OBLIGATOIREMENT comporter des métriques (`metrics:`) ou des plots (`plots:`) configurés avec `{cache: false}`.**
> Cela permet :
> 1. Le suivi direct et continu de l'exécution sur le Dashboard Web.
> 2. L'exportation visuelle automatique des courbes d'apprentissage et tableaux d'évaluation.
> 3. Le commit automatique par le bot `cluster-ci-bot` à la fin de chaque étape.

### Exemple Standard de `dvc.yaml`
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

### 2.4 Doctrine de Connectivité Stricte du DAG (Zéro Nœuds Orphelins) (MANDATOIRE)

1. **Un Pipeline Doit Être un Arbre Strictement Connecté** :
   - Toute étape déclarée dans `dvc.yaml` DOIT impérativement posséder au moins une dépendance (`deps`) la reliant directement au flux de données amont (données brutes, modèles ou prédictions générées par une étape précédente).
   - Toute étape intermédiaire DOIT voir ses sorties (`outs`, `metrics` ou `plots`) consommées par au moins une étape aval (ex: étape finale d'agrégation, calcul global de métriques ou génération de figures).
2. **Interdiction Formelle des Étapes Éphémères Flottantes** :
   - Les scripts de vérification technique ponctuelle (ex: `check_together.py`, tests de ping API ou de credentials, étape flottante `step_check_together`) NE DOIVENT JAMAIS être enregistrés comme des étapes permanentes dans `dvc.yaml`.
   - Les vérifications d'environnement font partie intégrante des pré-requis du pipeline ou des scripts d'initialisation, pas du graphe de dépendances DVC.
3. **Audit de Connectivité Avant Tout Tag** :
   - Avant tout tag Git ou déclenchement de `cluster-run`, la commande `dvc dag` doit être inspectée : le graphe ne doit contenir STRICTEMENT AUCUN nœud déconnecté de la racine (`step_download_data` / `step_data_processing`) ou de la feuille finale (`step_global_compare_metrics`).

---

## 4. Commandes CLI Client (`cluster-run`)

| Commande | Description |
|---|---|
| `cluster-run` | Soumet un shadow commit, pousse la branche draft, suit les logs en direct et extrait les résultats une fois terminé |
| `cluster-run --background` | Soumet le job et rend immédiatement la main au terminal |
| `cluster-run list` | Affiche l'historique récent des runs avec ID, statut et timestamps |
| `cluster-run view [run_id]` | Affiche les logs d'un run spécifique (dernier run par défaut) |
| `cluster-run cancel [run_id]` | Demande l'annulation distante d'un run et nettoie le tracking local |
| `cluster-run sync` | Synchronise manuellement les métriques, plots et `dvc.lock` locaux depuis la branche distante |

---

## 5. Protocole de Gestion de `cluster-run` par l'Agent

> [!IMPORTANT]
> **Instructions d'exécution lors d'une demande de `cluster-run` par l'utilisateur :**
>
> 1. **Exécution au premier plan (Foreground)** :
>    - Lancer la commande `cluster-run` directement.
> 2. **Suivi continu par minuteur de 15 minutes** :
>    - Planifier un timer/cron de 15 minutes (`schedule` avec DurationSeconds=900 ou recurring cron) pour vérifier l'état de l'exécution.
>    - Consulter les logs via `cluster-run view` ou le Dashboard Web (`http://130.223.73.209:5000/`) à chaque intervalle.
> 3. **Auto-Recovery & Resolution en cas de crash** :
>    - Si `cluster-run` échoue ou crash :
>      a. Analyser les logs pour identifier la cause exacte (erreur de code, mémoire CUDA OOM, dépendance manquante, erreur DVC, etc.).
>      b. Résoudre la cause racine dans le code/les scripts (sans modifier `.cluster-ci` sans accord).
>      c. Relancer immédiatement `cluster-run` au premier plan.
>      d. Répéter jusqu'à l'achèvement complet et réussi du pipeline.

---

## 6. Dashboard Web & Télémétrie

* **URL d'accès** : `http://130.223.73.209:5000/` (Nécessite le VPN UNIL).
* **Fonctionnalités clés** :
  * **Télémétrie en direct** : Visualisation RAM/VRAM par nœud et causes d'attente (`branch_exclusivity`, `no_free_workers`, `insufficient_ram`).
  * **Logs segmentés** : Découpage par étape DVC avec indicateur de statut `☠️` et bouton "Last Error".
  * **MD5 Clustering & Slider temporel** : Regroupement des artefacts par hash MD5 et inspection chronologique.
  * **Hydra Inspector** : Visualisation de l'arborescence des paramètres Hydra YAML.

---

## 7. Résilience & Sécurité Anti-Zombie

1. **Single Instance Lock** : Verrou `/tmp/cluster-worker.lock` pour empêcher les exécutions concurrentes sur un même worker.
2. **PID Host SIGKILL (<5s)** : Récupération du PID hôte (`docker inspect`) et envoi d'un `SIGKILL` direct au noyau pour libérer les contextes CUDA gelés avant `docker rm -f`.
3. **Host Ollama VRAM Release** : Libération forcée de la VRAM d'Ollama via `POST http://127.0.0.1:11434/api/generate` avec `keep_alive: 0`.
4. **Auto-Cancellation** : 1 seul run actif par chercheur sur les branches draft (`cluster-draft/*`).
