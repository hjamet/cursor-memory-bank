---
name: composio-mcp
description: "Intégration MCP distant pour scanner Slack, Notion, GitHub et Google Drive."
---
# 🔗 Skill Composio MCP Remote (`https://connect.composio.dev/mcp`)

Ce skill fournit le protocole exact validé pour interroger les canaux de messagerie et documents (Slack, Notion, GitHub, Google Drive) via le serveur MCP officiel Composio avec `mcp-cli`.

---

## 📌 Configuration dans `C:\Users\hjamet\.config\mcp\mcp_servers.json`

```json
{
  "mcpServers": {
    "composio": {
      "url": "https://connect.composio.dev/mcp",
      "headers": {
        "Authorization": "Bearer ck_2ralaLnwLn4lz9J2q8z0"
      }
    }
  }
}
```

---

## 🚀 Protocole d'Exécution Validé

### Étape 1 : Découverte des outils via `COMPOSIO_SEARCH_TOOLS`
```bash
mcp-cli call composio COMPOSIO_SEARCH_TOOLS '{"queries": [{"use_case": "slack search messages"}, {"use_case": "notion search pages"}], "session": {"generate_id": true}}'
```

### Étape 2 : Exécution ciblée via `COMPOSIO_MULTI_EXECUTE_TOOL`
*Note multi-comptes & PowerShell Windows* : Spécifier le compte cible (`slack_micky-kay` ou `slack_curr-anyway`). Sous PowerShell 5.1, les guillemets internes d'un littéral `'...'` passé à un binaire natif étant dépouillés (`Invalid JSON in --args`), appeler `mcp-cli` depuis Python via `subprocess.run(["mcp-cli", "call", "composio", "COMPOSIO_MULTI_EXECUTE_TOOL", json.dumps(payload)])`.

```bash
mcp-cli call composio COMPOSIO_MULTI_EXECUTE_TOOL '{"tools": [{"tool_slug": "SLACK_SEARCH_ALL", "account": "slack_micky-kay", "arguments": {"query": "after:2026-08-07"}}], "sync_response_to_workbench": true}'
```

---

## 🔒 Règles de Sécurité
- **Authentification** : `Authorization: Bearer <API_KEY>`.
- **Lecture seule** : Masquage des outils d'envoi/suppression de messages.
