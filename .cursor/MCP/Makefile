# Makefile simplifié pour le serveur MCP de Cursor  

# Couleurs pour les messages  
GREEN := \033[0;32m  
YELLOW := \033[0;33m  
RED := \033[0;31m  
NC := \033[0m  

# Fichiers avec chemins absolus  
PID_FILE = ./.mcp_server.pid  
LOG_FILE = ./mcp_server.log  

.PHONY: install start stop status uninstall debug help  

# Cible par défaut  
help:  
	@echo "$(GREEN)Makefile pour le serveur MCP de Cursor$(NC)"  
	@echo ""  
	@echo "$(YELLOW)Commandes disponibles:$(NC)"  
	@echo "  $(GREEN)make install$(NC)   - Configure l'environnement Poetry et installe les dépendances"  
	@echo "  $(GREEN)make start$(NC)     - Démarre le serveur MCP en arrière-plan"  
	@echo "  $(GREEN)make stop$(NC)      - Arrête le serveur MCP"  
	@echo "  $(GREEN)make status$(NC)    - Affiche l'état du serveur MCP"  
	@echo "  $(GREEN)make uninstall$(NC) - Supprime l'environnement virtuel et les fichiers temporaires"  
	@echo "  $(GREEN)make debug$(NC)     - Affiche les informations de débogage"  

# Débogage  
debug:  
	@echo "$(YELLOW)Répertoire actuel:$(NC) $$(pwd)"  
	@echo "$(YELLOW)Contenu du répertoire:$(NC)"  
	@ls -la  

# Configure l'environnement et installe les dépendances  
install:  
	@echo "$(YELLOW)Utilisation de Python pour le projet...$(NC)"  
	@echo "$(GREEN)Python $(shell python3 --version) sera utilisé.$(NC)"  
	  
	@echo "$(YELLOW)Configuration de l'environnement Poetry...$(NC)"  
	@poetry config virtualenvs.in-project true --local  
	  
	@echo "$(YELLOW)Installation des dépendances...$(NC)"  
	@poetry install --no-root  
	@echo "$(GREEN)Environnement configuré avec succès!$(NC)"  

# Démarre le serveur MCP  
start: install  
	@echo "$(YELLOW)Vérification si le serveur MCP est déjà en cours d'exécution...$(NC)"  
	@if [ -f $(PID_FILE) ]; then \
		pid=$$(cat $(PID_FILE)); \
		if ps -p $$pid > /dev/null; then \
			echo "$(GREEN)Le serveur MCP est déjà en cours d'exécution (PID: $$pid).$(NC)"; \
			exit 0; \
		else \
			echo "$(YELLOW)Le fichier PID existe mais le processus ne tourne pas. Nettoyage...$(NC)"; \
			rm -f $(PID_FILE); \
		fi; \
	fi  
	  
	@echo "$(YELLOW)Vérification du fichier serveur...$(NC)"  
	@if [ ! -f ./mcp_server.py ]; then \
		echo "$(RED)Le fichier serveur MCP n'existe pas. Veuillez créer mcp_server.py dans ce répertoire.$(NC)"; \
		exit 1; \
	fi  
	  
	@echo "$(GREEN)Démarrage du serveur MCP en arrière-plan...$(NC)"  
	@nohup poetry run python ./mcp_server.py > $(LOG_FILE) 2>&1 & echo $$! > $(PID_FILE)  
	@sleep 1  
	@if [ -f $(PID_FILE) ]; then \
		echo "$(GREEN)Serveur MCP démarré avec succès (PID: $$(cat $(PID_FILE))).$(NC)"; \
		echo "$(GREEN)Les logs sont disponibles dans: $(LOG_FILE)$(NC)"; \
	else \
		echo "$(RED)Échec du démarrage du serveur MCP. Vérifiez les logs pour plus d'informations.$(NC)"; \
	fi  

# Arrête le serveur MCP  
stop:  
	@if [ -f $(PID_FILE) ]; then \
		pid=$$(cat $(PID_FILE)); \
		if ps -p $$pid > /dev/null; then \
			echo "$(YELLOW)Arrêt du serveur MCP (PID: $$pid)...$(NC)"; \
			kill $$pid; \
			rm -f $(PID_FILE); \
			echo "$(GREEN)Serveur MCP arrêté.$(NC)"; \
		else \
			echo "$(YELLOW)Le serveur MCP n'est pas en cours d'exécution (PID: $$pid invalide).$(NC)"; \
			rm -f $(PID_FILE); \
		fi; \
	else \
		echo "$(YELLOW)Aucun fichier PID trouvé. Le serveur MCP n'est probablement pas en cours d'exécution.$(NC)"; \
	fi  

# Affiche l'état du serveur MCP  
status:  
	@if [ -f $(PID_FILE) ]; then \
		pid=$$(cat $(PID_FILE)); \
		if ps -p $$pid > /dev/null; then \
			echo "$(GREEN)Le serveur MCP est en cours d'exécution (PID: $$pid).$(NC)"; \
			echo "$(GREEN)Les logs sont disponibles dans: $(LOG_FILE)$(NC)"; \
		else \
			echo "$(YELLOW)Le serveur MCP n'est pas en cours d'exécution (PID: $$pid invalide).$(NC)"; \
		fi; \
	else \
		echo "$(YELLOW)Le serveur MCP n'est pas en cours d'exécution.$(NC)"; \
	fi  

# Désinstalle l'environnement  
uninstall: stop  
	@echo "$(YELLOW)Suppression de l'environnement virtuel...$(NC)"  
	@if [ -d "./.venv" ]; then \
		rm -rf ./.venv; \
		echo "$(GREEN)Environnement virtuel supprimé.$(NC)"; \
	else \
		echo "$(YELLOW)Aucun environnement virtuel trouvé.$(NC)"; \
	fi  
	  
	@echo "$(YELLOW)Suppression des fichiers temporaires...$(NC)"  
	@rm -f $(PID_FILE) $(LOG_FILE)  
	@rm -f ./poetry.lock  
	@echo "$(GREEN)Fichiers temporaires supprimés.$(NC)"  
	@echo "$(GREEN)Désinstallation terminée.$(NC)"  