---
description: "Doctrine d'usage du MCP Playwright : distinction statique vs dynamique, outils natifs, furtivité d'arrière-plan et garde-fous de soumission."
trigger: always_on
---

# 🌐 Navigation Web & MCP Playwright (Statique vs Dynamique & Garde-Fous)

## 🧭 Quel outil pour quel besoin ?

| Besoin | Outils |
|---|---|
| **Contenu statique** (docs, articles, pages publiques figées) | `search_web`, `read_url_content` (zéro navigateur lourd) |
| **Contenu dynamique, interactif ou recette UI** (horaires CFF, Maps, simulateurs, démarches, test visuel d'application locale) | MCP Playwright (`call_mcp_tool ServerName='playwright'`) |

## 🛠️ Interaction avec les pages & Furtivité stricte (Chrome actif d'Henri)

- **Outils natifs d'abord & Preuve visuelle** : utiliser `browser_snapshot`, `browser_fill_form` / `browser_type`, `browser_click`, `browser_hover`, `browser_drag`, `browser_select_option` et prendre des captures (`browser_take_screenshot`) pour contrôler visuellement le rendu. Aucun script Python/shell interrogeant des API privées à la place de Playwright ; `browser_evaluate` / `browser_run_code_unsafe` uniquement en dernier recours face à un obstacle DOM.
- **Onglets isolés & 100 % furtifs — INTERDICTION ABSOLUE DE VOLER LE FOCUS** : opérer dans un onglet dédié en arrière-plan sans jamais modifier le focus de Windows :
  1. **Ouverture dédiée** : ouvrir un onglet propre à la mission via `browser_tabs(action="new"[, url="..."])`, puis naviguer dedans avec `browser_navigate`.
  2. **Zéro mise au premier plan (`bringToFront` / `select` bannis)** : interdiction formelle d'appeler `browser_tabs(action="select")`, `page.bringToFront()` dans `browser_run_code_unsafe` ou `window.focus()` dans `browser_evaluate`. Cibler son onglet en arrière-plan via `const target = page.context().pages().find(p => p.url().includes('...'))` sans jamais appeler `target.bringToFront()` (*ex. réel 14/10/2026, AIB A4 : onglets Dify/Wooclap surgissant au premier plan en continu pendant qu'Henri travaillait*).
  3. **Fermeture sécurisée (jamais le dernier onglet ni `browser_close`)** : en fin de mission, vérifier `browser_tabs(action="list")` et n'appeler `browser_tabs(action="close")` que s'il reste `> 1` onglet connecté au relai MCP (fermer le dernier onglet coupe définitivement l'extension Chrome — *ex. réel 14/10/2026, DLLP*). `browser_close` est strictement interdit.

## 🔒 Garde-fous financiers et administratifs

> [!CAUTION]
> 1. **Zéro achat** : aucun billet, ticket ni transaction financière.
> 2. **Zéro soumission finale sans accord** : pré-remplir avec les outils natifs ➔ capture nette (`browser_take_screenshot`) ➔ résumé télégraphique + capture à Henri ➔ attendre sa validation formelle avant tout clic d'envoi définitif.
