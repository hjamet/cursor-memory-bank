# Mystères de l'UNIL 2025 - Déjouez l'IA

Plateforme interactive d'expérimentation avec l'intelligence artificielle permettant aux participants des Mystères de l'UNIL 2025 de comprendre intuitivement les capacités et limites de l'IA moderne à travers un Test de Turing inversé ludique et éducatif.

## 🎯 Objectifs

- Permettre aux classes (9-13 ans) de créer leurs propres chatbots pendant des ateliers guidés
- Offrir une expérience de jeu engageante pour le grand public testant ces chatbots
- Fournir une plateforme robuste capable de gérer des pics d'utilisation
- Maintenir une disponibilité 24h/24 pendant l'événement

## 🛠️ Technologies

- **Backend**: FastAPI, WebSocket, SQLite, Redis
- **Frontend**: TailwindCSS, DaisyUI
- **Outils**: Poetry, Pyenv, Alembic

## 📋 Prérequis

- Python 3.11.8 (géré via pyenv)
- Poetry pour la gestion des dépendances
- Redis pour la gestion du cache

## 🚀 Installation

1. Cloner le dépôt :
```bash
git clone [URL_DU_REPO]
cd mysteres-unil
```

2. Installer Python 3.11.8 avec pyenv :
```bash
pyenv install 3.11.8
pyenv local 3.11.8
```

3. Installer les dépendances avec Poetry :
```bash
make install
```

## 🔧 Développement

1. Lancer le serveur de développement :
```bash
make dev
```

2. Exécuter les tests :
```bash
make test
```

## 📦 Déploiement

1. Construire pour la production :
```bash
make build
```

2. Déployer sur le serveur UNIL :
```bash
make deploy
```

## 🧪 Tests

- Tests unitaires avec pytest
- Tests de charge avec Locust
- Tests d'intégration avec httpx

## 📚 Documentation

- [Documentation de l'API](docs/api.md)
- [Guide de développement](docs/development.md)
- [Guide de déploiement](docs/deployment.md)

## 🤝 Contribution

1. Créer une branche pour votre fonctionnalité
2. Commiter vos changements
3. Pousser vers la branche
4. Créer une Pull Request

## 📄 Licence

Ce projet est la propriété de l'Université de Lausanne. Tous droits réservés. 