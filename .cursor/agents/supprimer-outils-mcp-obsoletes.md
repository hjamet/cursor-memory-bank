## Contexte

Je viens de terminer l'implémentation du système de roadmap centralisée avec les commandes `/agent` et `/task`, ainsi que la règle `agent.mdc`. Ce nouveau système permet de coordonner plusieurs agents Cursor en parallèle sans avoir besoin de serveurs MCP complexes.

Lors de cette implémentation, il est apparu que les serveurs MCP ToolsMCP et MemoryBankMCP ne sont plus nécessaires. Le système de roadmap centralisée avec fichiers markdown et YAML est plus simple, plus léger et plus flexible. Ces serveurs MCP ajoutent de la complexité inutile et doivent être supprimés pour simplifier l'architecture.

De plus, le script `install.sh` doit être adapté pour ne plus installer ces serveurs MCP obsolètes, ni les référencer dans la configuration MCP.

## Objectif

Supprimer complètement les serveurs MCP ToolsMCP et MemoryBankMCP du projet, et adapter le script `install.sh` pour ne plus les installer ni les configurer.

## Fichiers Concernés

### Du travail effectué précédemment :
- `.cursor/agents/roadmap.yaml` : Roadmap centralisée créée - système simple qui remplace les MCP
- `.cursor/commands/agent.md` : Commande pour sélectionner des tâches depuis la roadmap
- `.cursor/commands/task.md` : Commande pour ajouter des tâches à la roadmap
- `.cursor/rules/agent.mdc` : Règle pour créer des tâches dans la roadmap

### Fichiers à modifier/supprimer :
- `install.sh` : Script d'installation qui référence ToolsMCP et MemoryBankMCP
  - Ligne 988 : Liste des serveurs MCP à installer (`mcp_servers=("mcp-commit-server" "memory-bank-mcp" "tools-mcp")`)
  - Lignes 1138-1151 : Bloc de téléchargement de `memory-bank-mcp`
  - Lignes 1152-1161 : Bloc de téléchargement de `tools-mcp`
  - Lignes 1486-1496 : Configuration de `memory-bank-mcp` dans MCP JSON
  - Lignes 1503-1518 : Configuration `ToolsMCP` et `MemoryBankMCP` dans MCP JSON
  - Lignes 1530-1545 : Configuration `ToolsMCP` dans installation basique
  - Lignes 1582-1684 : Configuration Gemini CLI avec ToolsMCP et MemoryBankMCP
  - Ligne 1989 : Documentation mentionnant ToolsMCP et MemoryBankMCP
  - Lignes 2105-2106 : Installation des dépendances npm pour ToolsMCP et MemoryBankMCP
- `.cursor/mcp/memory-bank-mcp/` : Dossier entier à supprimer (si présent)
- `.cursor/mcp/tools-mcp/` : Dossier entier à supprimer (si présent)
- `.cursor/mcp/mcp-commit-server/` : Vérifier si ce serveur est encore utilisé ou doit aussi être supprimé

### Recherches à effectuer :
- Recherche sémantique : "Où sont référencés ToolsMCP et MemoryBankMCP dans le codebase ?"
- Recherche sémantique : "Quels fichiers utilisent encore les outils MCP ToolsMCP ou MemoryBankMCP ?"
- Documentation : Lire `README.md` pour vérifier les sections mentionnant ces serveurs MCP

### Fichiers de résultats d'autres agents (si pertinents) :
- Aucun pour le moment

**Fichier output pour le rapport final :**
- `.cursor/agents/rapport-supprimer-outils-mcp-obsoletes_30-10-2025.md`

## Instructions de Collaboration

Tu es **INTERDIT** de commencer à implémenter quoi que ce soit immédiatement. Ta première et UNIQUE tâche est l'exploration et la compréhension :

1. **LIS EXHAUSTIVEMENT** tous les fichiers listés ci-dessus dans "Fichiers Concernés" - tu dois comprendre ce qui a été fait, ce qui doit être supprimé, et ce qui doit être adapté
2. **EFFECTUE les recherches sémantiques** mentionnées pour identifier toutes les références à ToolsMCP et MemoryBankMCP dans le codebase
3. **LIS le README.md** et identifie toutes les sections/documentations qui mentionnent ces serveurs MCP
4. **VÉRIFIE** si `.cursor/mcp/mcp-commit-server/` est encore utilisé ou doit aussi être supprimé
5. **IDÉNTIFIE** toutes les références dans `install.sh` qui doivent être supprimées ou adaptées
6. **ATTEINS une compréhension approfondie** de l'impact de la suppression de ces serveurs MCP
7. **DISCUTE avec l'utilisateur** pour clarifier :
   - Est-ce que `mcp-commit-server` doit aussi être supprimé ou est-il encore utilisé ?
   - Faut-il garder Context7 dans la configuration MCP ?
   - Y a-t-il d'autres fichiers à adapter en plus de `install.sh` et `README.md` ?
8. **ÉTABLIS un plan d'action détaillé** avec l'utilisateur avant toute modification
9. **DOIT** écrire le rapport final dans le fichier output mentionné après avoir terminé

Seulement APRÈS avoir complété cette exploration exhaustive et cette planification collaborative, tu peux commencer à considérer tout travail de suppression et d'adaptation. L'exploration est OBLIGATOIRE, pas optionnelle.

