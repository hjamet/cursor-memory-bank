---
description: "Doctrine d'usage du MCP Playwright : interdiction du navigateur intégré Antigravity, distinction statique vs dynamique, outils natifs, furtivité d'arrière-plan et garde-fous de soumission."
trigger: always_on
---

# 🌐 Navigation Web & MCP Playwright (Statique vs Dynamique & Garde-Fous)

## 🧭 Quel outil pour quel besoin ? (Navigateur Intégré Antigravity Strictement Banni)

| Besoin | Outils |
|---|---|
| **Contenu statique** (docs, articles, pages publiques figées) | `search_web`, `read_url_content` (zéro navigateur lourd) |
| **Contenu dynamique, interactif, authentifié ou recette UI** (portails UNIL/Switch edu-ID, Prolific, Moodle, CFF, Maps, démarches, test visuel d'app locale) | **Exclusivement MCP Playwright** (`call_mcp_tool ServerName='playwright'`). **Interdiction formelle d'invoquer le sous-agent `browser` intégré d'Antigravity (`invoke_subagent(TypeName="browser")`)**, dont le webview isolé n'a aucune des sessions actives du navigateur principal d'Henri (*ex. réel 17/11/2026, CER-HEC*). |

## 🛠️ Interaction avec les pages, Stabilité JSON-RPC & Furtivité stricte (Chrome actif d'Henri)

- **Outils natifs d'abord, Preuve visuelle, Chemins relatifs nus & Protection JSON-RPC** : utiliser `browser_snapshot`, `browser_fill_form` / `browser_type`, `browser_click`, `browser_hover`, `browser_drag`, `browser_select_option` et prendre des captures (`browser_take_screenshot`) pour contrôler visuellement le rendu. Aucun script Python/shell interrogeant des API privées à la place de Playwright ; `browser_evaluate` / `browser_run_code_unsafe` uniquement en dernier recours face à un obstacle DOM. **Toujours passer un `filename` relatif nu (ex. `capture.png`, `body.txt`, enregistré dans `.playwright-mcp/`) à `browser_take_screenshot` et `browser_network_request`** — jamais de chemin absolu vers `brain/.../scratch/` (rejeté en `File access denied: outside allowed roots`, *ex. réels 20–21/11/2026 sur `e0ac0eed` et `eMush`*) — et **ne jamais appeler `browser_network_request` sans `filename` sur un corps volumineux** (`> 1 Mo` en sortie brute coupe le pipe JSON-RPC du serveur MCP `playwright`).
- **Onglets isolés, zéro groupe orphelin & 100 % furtifs — INTERDICTION ABSOLUE DE VOLER LE FOCUS** : `mcp_config.json` lance `@playwright/mcp@latest --extension --no-tab-group --background` (`Playwright Extension >= 0.6.0`), ce qui empêche nativement la création de groupes d'onglets colorés/gris orphelins, ouvre les onglets en arrière-plan (`--open-in-background`) et neutralise `Page.bringToFront` / `Target.activateTarget` côté protocole. Chaque session respecte strictement ce cycle de vie :
  1. **Réutilisation de l'onglet dédié `0: about:blank`** : vérifier `browser_tabs(action="list")`. Si la session démarre sur un onglet dédié `0: about:blank` (alloué automatiquement par `connect.html` avec `PLAYWRIGHT_MCP_EXTENSION_TOKEN`), naviguer directement dedans via `browser_navigate` au lieu d'empiler un 2e onglet superflu via `browser_tabs(action="new")`. N'ouvrir un onglet supplémentaire (`browser_tabs(action="new")`) que si `0` est déjà une page personnelle d'Henri ou si la mission nécessite un second onglet.
  2. **Zéro mise au premier plan (`bringToFront` / `select` bannis)** : interdiction formelle d'appeler `browser_tabs(action="select")`, `page.bringToFront()` dans `browser_run_code_unsafe` ou `window.focus()` dans `browser_evaluate`. Cibler son onglet en arrière-plan via `const target = page.context().pages().find(p => p.url().includes('...'))` sans jamais appeler `target.bringToFront()` (*ex. réel 14/10/2026, AIB A4 : onglets Dify/Wooclap surgissant au premier plan en continu pendant qu'Henri travaillait*).
  3. **Fermeture systématique de tous les onglets de la mission (y compris `0: about:blank`)** : contrairement à l'ancienne extension `<= 0.5.0`, l'extension `0.6.0` ne casse plus à la fermeture du dernier onglet et **abandonne tout onglet non fermé en `about:blank` / groupe gris orphelin à la fin de la session** (*audit 23/11/2026 : `background.mjs:L405-L454`*). En fin de mission, inspecter `browser_tabs(action="list")` et fermer via `browser_tabs(action="close", index=...)` **chaque onglet ouvert ou utilisé par la mission, y compris le dernier (`index=0` si c'est `about:blank` ou l'onglet dédié de la mission)** — ne jamais fermer un onglet personnel préexistant d'Henri. Éviter `browser_close` seul (qui coupe le WebSocket sans fermer les onglets ouverts dans Chrome).

## 🔒 Garde-fous financiers et administratifs

> [!CAUTION]
> 1. **Zéro achat** : aucun billet, ticket ni transaction financière.
> 2. **Zéro soumission finale sans accord** : pré-remplir avec les outils natifs ➔ capture nette (`browser_take_screenshot`) ➔ résumé télégraphique + capture à Henri ➔ attendre sa validation formelle avant tout clic d'envoi définitif.
