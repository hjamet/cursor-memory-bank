---
name: mcp-manager
description: "Gestion et exécution en ligne de commande de serveurs et outils MCP."
---
# MCP Manager Skill

Ce skill fournit les instructions et standards pour configurer, gérer et utiliser des serveurs MCP (Model Context Protocol) via l'outil en ligne de commande `mcp-cli`.

## 1. Emplacement du fichier de configuration

Le fichier de configuration centralisé des serveurs MCP est situé à :
`$HOME\.config\mcp\mcp_servers.json` (`C:\Users\Jamet\.config\mcp\mcp_servers.json` sur PC perso, `C:\Users\hjamet\.config\mcp\mcp_servers.json` sur PC UNIL).

Pour s'assurer que `mcp-cli` trouve toujours la bonne configuration dans n'importe quel environnement shell, la variable d'environnement `$env:MCP_CONFIG_PATH` ou `MCP_CONFIG_PATH` peut être définie :
```powershell
$env:MCP_CONFIG_PATH = "$HOME\.config\mcp\mcp_servers.json"
```

---

## 2. Configuration des Serveurs MCP (`mcp_servers.json`)

Le fichier `mcp_servers.json` utilise la structure standard `mcpServers` :

```json
{
  "mcpServers": {
    "aivc": {
      "command": "C:\\Users\\Jamet\\.aivc\\venv\\Scripts\\python.exe",
      "args": ["-m", "aivc.proxy"],
      "env": {
        "AIVC_STORAGE_ROOT": "C:\\Users\\Jamet\\.aivc\\storage"
      }
    },
    "remote_service": {
      "url": "https://api.example.com/sse",
      "headers": {
        "Authorization": "Bearer YOUR_TOKEN"
      }
    }
  }
}
```

### Types de transport supportés :
1. **Stdio (Local)** : Spécifier `"command"` (ex: `npx`, `node`, `bunx`, `python`) et la liste d'arguments `"args"`. Optionnellement `"env"` pour les variables d'environnement.
2. **SSE / Streamable HTTP (Remote)** : Spécifier `"url"` (et optionnellement `"headers"`).

---

## 3. Filtrage des outils (`allowedTools` / `disabledTools`)

Pour réduire le bruit et protéger le contexte LLM, `mcp-cli` permet de restreindre ou masquer certains outils au niveau de chaque serveur :

### Autoriser uniquement certains outils (`allowedTools`)
```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": { "GITHUB_PERSONAL_ACCESS_TOKEN": "ghp_..." },
      "allowedTools": ["search_repositories", "get_file_contents"]
    }
  }
}
```

### Masquer des outils spécifiques (`disabledTools`)
```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "C:\\Users\\hjamet"],
      "disabledTools": ["delete_file", "move_file"]
    }
  }
}
```

---

## 4. Utilisation de `mcp-cli`

`mcp-cli` permet d'explorer et d'exécuter des outils MCP directement en ligne de commande sans charger dynamiquement l'intégralité des schémas JSON dans le contexte de l'assistant.

### Commandes principales

1. **Lister les serveurs configurés**
   ```bash
   mcp-cli
   # Ou avec descriptions d'outils
   mcp-cli -d
   ```

2. **Inspecter un serveur ou un outil**
   ```bash
   # Lister les outils exposés par un serveur
   mcp-cli info <server_name>
   
   # Afficher le schéma d'arguments et la description d'un outil spécifique
   mcp-cli info <server_name> <tool_name>
   # Syntaxe alternative par slash :
   mcp-cli info <server_name>/<tool_name>
   ```

3. **Rechercher des outils par filtre glob (`grep`)**
   ```bash
   mcp-cli grep "*file*"
   mcp-cli grep "*search*"
   ```

4. **Appeler un outil (`call`)**
   ```bash
   # Transmission directe des arguments JSON sous forme de chaîne
   mcp-cli call <server_name> <tool_name> '{"path": "C:\\Users\\hjamet\\Documents\\example.txt"}'

   # Transmission par fichier payload.json via stdin avec séquences Unicode \uXXXX (recommandé pour les objets JSON contenant des accents sous Windows PowerShell 5.1, car @payload.json n'est pas supporté par @wong2/mcp-cli et le pipe PowerShell 5.1 remplace les accents UTF-8 bruts par '?')
   Get-Content -Raw payload.json | mcp-cli call <server_name> <tool_name>
   ```

---

## 5. Bonnes Pratiques & Gestion du Contexte LLM

- **Ne pas surcharger le contexte** : Au lieu d'enregistrer de nombreux serveurs MCP lourds directement en MCP eager/lazy dans la session d'agent (seul `playwright` reste monté dans `.gemini/antigravity/mcp_config.json`), utiliser `mcp-cli` pour exécuter ponctuellement des outils à la demande (`aivc`, `composio`, `doc-version`).
- **Validation** : Toujours exécuter `mcp-cli info <server>` après l'ajout d'un serveur dans `mcp_servers.json` pour s'assurer que la connexion s'établit et que les outils répondent correctement.
- **Démon AIVC Persistant (`aivc.proxy` / `aivc.daemon`)** : `@wong2/mcp-cli` (v2.0.0) fermant le processus stdio après chaque appel, `aivc` utilise le pont léger `python -m aivc.proxy` (bibliothèque standard pure, démarrage ~25 ms) qui démarre automatiquement en arrière-plan hors du Job Object Windows (via WMI `Win32_Process.Create`) le démon `aivc.daemon` (`127.0.0.1:18765`). Ce démon conserve en RAM le modèle ONNX FastEmbed, ChromaDB et le thread de synchronisation Google Drive (`AIVC_Sync/files/`), réduisant le temps d'appel de ~3,5 s à **< 80 ms**. Commandes de contrôle direct : `aivc daemon status`, `aivc daemon start`, `aivc daemon stop`.
