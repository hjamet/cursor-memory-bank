# Scripts Directory 📁

## Description
Ce dossier contient les scripts utilitaires et de maintenance du projet Cursor Memory Bank. Il centralise tous les outils Python pour la gestion et l'analyse du repository.

## Fichiers Principaux
- **`tomd.py`** : *Utilitaire Python pour la génération de snapshots de repository en Markdown*
- **`scripts.md`** : *Documentation complète du dossier et guide d'utilisation*

## Scripts Principaux
- **`tomd.py`** : *Génère un snapshot complet du repository avec arborescence et contenu des fichiers*

## Commandes Principales
```bash
# Générer un snapshot complet du repository
python scripts/tomd.py
```
*Crée les fichiers `repo.md` (snapshot) et `diff` (diff git) à la racine du projet*

```bash
# Vérifier la syntaxe du script
python -m py_compile scripts/tomd.py
```
*Valide la syntaxe Python du script sans l'exécuter*

## Résultats Principaux
| Résultat | Description | Fichier |
|----|----|---|
| Snapshot Repository | Arborescence et contenu des fichiers | `repo.md` |
| Diff Git | Modifications non commitées | `diff` |
| Documentation | Guide d'utilisation et configuration | `scripts.md` |

## Configuration

Le script `tomd.py` utilise une configuration flexible :

- **Extensions incluses** : `.py`, `.md`, `.tex`, `.css`, `.js`, `.tsx`, `.ipynb`, `.sh`
- **Extensions tronquées** : `.csv`, `.json`, `.log`, `.tsv`, `.yml`, `.yaml`
- **Fichiers spéciaux** : `Dockerfile`, `docker-compose.yml`, `Makefile`, `README.md`
- **Taille maximale** : 512 KiB par fichier
- **Dossiers exclus** : `node_modules`, `venv`, `.venv`, `env`, `.env`

## Architecture

```
scripts/
├── tomd.py              # Utilitaire de snapshot repository (325 lignes)
└── scripts.md           # Documentation du dossier (ce fichier)
```

## Maintenance

Ce dossier suit le principe "Fail-Fast" :
- Aucun fallback silencieux
- Erreurs explicites et immédiates
- Validation stricte des entrées
- Documentation claire des fonctionnalités

---

*Dernière mise à jour : 2025-01-20*