.PHONY: install dev test build deploy clean

# Variables
POETRY = poetry
ALEMBIC = $(POETRY) run alembic

# Installation des dépendances
install:
	$(POETRY) install

# Lancement en développement
dev:
	$(POETRY) run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Exécution des tests
test:
	$(POETRY) run pytest tests/ -v

# Construction pour la production
build:
	$(POETRY) install --no-dev
	$(ALEMBIC) upgrade head

# Déploiement sur le serveur UNIL
deploy: build
	@echo "Déploiement sur le serveur UNIL..."
	# Commandes de déploiement à définir

# Nettoyage
clean:
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -r {} +
	find . -type d -name "*.egg" -exec rm -r {} +
	find . -type d -name ".pytest_cache" -exec rm -r {} +
	find . -type d -name ".coverage" -exec rm -r {} +
	find . -type d -name "htmlcov" -exec rm -r {} +
	$(POETRY) env remove --all 