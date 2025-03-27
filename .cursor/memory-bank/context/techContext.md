# Contexte Technique

## Pile Technologique
- **Langages**: Python, JavaScript, HTML, CSS
- **Frameworks**: FastAPI, TailwindCSS
- **Bibliothèques**: DaisyUI, WebSocket
- **Outils**: Redis, SQLite, Poetry, Pyenv

## Architecture
Architecture moderne basée sur FastAPI avec WebSocket pour les communications en temps réel, utilisant une base de données SQLite pour la simplicité et Redis pour le cache. Structure modulaire avec séparation claire entre frontend et backend.

## Environnement de Développement
- **Gestion Python**: Pyenv pour la version Python, Poetry pour la gestion des dépendances
- **Configuration requise**: Python 3.11+, Node.js, Redis
- **Installation**: Via Poetry (poetry install)
- **Développement**: poetry run uvicorn src.main:app --reload
- **Tests**: poetry run pytest
- **Production**: poetry install --no-dev, poetry run alembic upgrade head

## Conventions de Code
- Structure modulaire avec séparation backend/frontend
- Routes API RESTful
- Communication temps réel via WebSocket
- Utilisation de TailwindCSS pour le styling
- Tests unitaires requis

## Dépendances Externes
- FastAPI: Framework backend principal
- TailwindCSS: Framework CSS utilitaire
- DaisyUI: Composants UI préfabriqués
- Redis: Système de cache
- SQLite: Base de données
- WebSocket: Communication temps réel

## Intégrations
- Système de file d'attente intelligent
- Modération automatique des contenus
- Monitoring en temps réel
- Interface d'administration
- Système de sauvegarde automatique 