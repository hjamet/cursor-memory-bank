# Rapport : Suppression des outils MCP obsolètes

## Objectif

Supprimer complètement tous les serveurs MCP obsolètes (ToolsMCP, MemoryBankMCP, mcp-commit-server) du projet, ainsi que toutes leurs références dans le code et la documentation, car ils ont été remplacés par le système de roadmap centralisée.

## Travail effectué

### 1. Suppression des fichiers et dossiers MCP

- ✅ Supprimé le dossier `.cursor/mcp/` et tous ses sous-dossiers (memory-bank-mcp, tools-mcp, mcp-commit-server)
- ✅ Supprimé le fichier `.cursor/mcp.json`
- ✅ Tenté de supprimer `.gemini/settings.json` (fichier non trouvé, probablement non créé lors d'une installation précédente)

### 2. Modification de `install.sh`

- ✅ Supprimé la fonction `install_mcp_server_dependencies()` complètement
- ✅ Supprimé toutes les références aux serveurs MCP dans les variables et listes
- ✅ Supprimé les blocs de téléchargement des serveurs MCP (memory-bank-mcp, tools-mcp)
- ✅ Supprimé les fonctions `merge_mcp_json()` et `configure_gemini_cli_mcp()` complètement
- ✅ Supprimé les appels à ces fonctions dans le script principal
- ✅ Supprimé le bloc d'installation des dépendances npm pour les serveurs MCP
- ✅ Supprimé les références à `mcp.json` dans la partie git clone
- ✅ Modifié les commentaires et descriptions pour retirer les mentions de serveurs MCP
- ✅ Renommé et simplifié la fonction `create_mcp_tasks_file()` pour retirer les références "MCP" dans les commentaires (fonction conservée car elle crée juste un tasks.json simple)
- ✅ Corrigé l'indentation incorrecte dans la section principale d'installation

### 3. Modification de `README.md`

- ✅ Supprimé la section `.cursor/mcp/` de l'architecture du dépôt
- ✅ Supprimé la section complète "Gemini CLI Integration 🤖" avec toutes les références aux serveurs MCP
- ✅ Supprimé la section "MCP Server Integration" dans Core Features
- ✅ Supprimé la section complète "Available MCP Tools 🛠️" avec toutes les descriptions des outils MCP
- ✅ Supprimé la section "MCP Rule: `mcp`" avec toutes les directives
- ✅ Supprimé la section "MCP Server Issues" dans Troubleshooting
- ✅ Supprimé la section "CRITICAL: MCP Server Restart Requirement" dans Troubleshooting
- ✅ Supprimé toutes les références fonctionnelles aux serveurs MCP dans les descriptions des modes d'installation
- ✅ Supprimé les références aux serveurs MCP dans la section "Required files"
- ✅ Ajouté une nouvelle section "Système de Roadmap Centralisée 📋" avec note historique expliquant que les anciens systèmes MCP sont dans l'historique git
- ✅ Modifié la description principale pour retirer la mention "intégration MCP"
- ✅ Conservé uniquement les mentions historiques acceptables (note historique sur les anciens systèmes, mention de `.cursor/rules/mcp.mdc` comme fichier repository-local)

### 4. Points d'attention

- Les références dans `.gitignore` (`.cursor/mcp` et `.cursor/mcp.json`) ont été conservées car elles servent à ignorer ces fichiers s'ils sont créés par erreur dans le futur
- La fonction `create_mcp_tasks_file()` a été conservée mais renommée pour retirer les références "MCP" dans les commentaires, car elle crée simplement un fichier `tasks.json` qui peut être utile pour Streamlit
- La mention de `.cursor/rules/mcp.mdc` dans le README a été conservée car c'est juste une note technique sur un fichier qui existe toujours dans le repository (fichier repository-local)

## Résultat

Tous les serveurs MCP obsolètes ont été complètement supprimés du projet. Le système utilise maintenant uniquement la roadmap centralisée (`.cursor/agents/roadmap.yaml`) pour coordonner plusieurs agents Cursor en parallèle. Les références historiques ont été conservées de manière appropriée dans le README pour documenter l'évolution du système.

## Fichiers modifiés

- `install.sh` : Suppression complète de toutes les références et fonctions MCP
- `README.md` : Suppression des sections MCP et ajout d'une note historique sur le système de roadmap

## Fichiers supprimés

- `.cursor/mcp/` (dossier complet avec tous ses sous-dossiers)
- `.cursor/mcp.json`

## Validation

- ✅ Aucune erreur de linter détectée
- ✅ Toutes les références fonctionnelles aux serveurs MCP ont été supprimées
- ✅ Le système de roadmap centralisée est maintenant documenté comme solution de remplacement
- ✅ Les notes historiques sont présentes et appropriées

