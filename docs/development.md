# Guide de développement

## 🏗️ Architecture

Le projet suit une architecture modulaire avec séparation claire des responsabilités :

```
src/
├── backend/
│   ├── api/          # Routes API FastAPI
│   ├── models/       # Modèles SQLAlchemy
│   ├── services/     # Services métier
│   └── websockets/   # Gestionnaires WebSocket
├── frontend/
│   ├── static/       # Assets statiques
│   └── templates/    # Templates Jinja2
└── utils/           # Utilitaires communs
```

## 🔧 Configuration

### Variables d'environnement

Créer un fichier `.env` à la racine du projet :

```env
DATABASE_URL=sqlite:///./app.db
REDIS_URL=redis://localhost:6379
SECRET_KEY=your-secret-key
ENVIRONMENT=development
```

### Base de données

Les migrations sont gérées avec Alembic :

```bash
# Créer une nouvelle migration
poetry run alembic revision --autogenerate -m "description"

# Appliquer les migrations
poetry run alembic upgrade head

# Revenir en arrière
poetry run alembic downgrade -1
```

## 🧪 Tests

### Tests unitaires

```bash
# Exécuter tous les tests
make test

# Exécuter un test spécifique
poetry run pytest tests/backend/test_api.py -v

# Avec couverture de code
poetry run pytest --cov=src tests/
```

### Tests de charge

```bash
# Lancer les tests de charge
poetry run locust -f tests/load/locustfile.py
```

## 📝 Conventions de code

- PEP 8 pour le style Python
- Type hints obligatoires
- Docstrings pour toutes les fonctions publiques
- Tests unitaires pour chaque nouvelle fonctionnalité
- Messages de commit clairs et descriptifs

## 🔄 Workflow Git

1. Créer une branche pour chaque fonctionnalité
2. Commits atomiques et descriptifs
3. Pull request avec revue de code
4. Merge uniquement après validation des tests

## 🐛 Débogage

### Logging

```python
import logging

logger = logging.getLogger(__name__)
logger.debug("Message de debug")
logger.info("Information")
logger.warning("Avertissement")
logger.error("Erreur")
```

### Débogage WebSocket

Utiliser l'inspecteur de navigateur pour :
- Surveiller les connexions WebSocket
- Analyser les messages échangés
- Détecter les erreurs de connexion

## 🚀 Bonnes pratiques

- Validation des données avec Pydantic
- Cache Redis pour les données fréquemment accédées
- Rate limiting pour protéger l'API
- Gestion appropriée des erreurs
- Documentation à jour
- Code commenté et lisible 