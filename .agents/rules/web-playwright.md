---
description: "Doctrine d'usage du MCP Playwright : distinction statique vs dynamique, outils natifs, furtivité d'arrière-plan et garde-fous de soumission."
trigger: always_on
---

# 🌐 Navigation Web & MCP Playwright (Statique vs Dynamique & Garde-Fous)

## 🧭 Quel outil pour quel besoin ?

| Besoin | Outils | Acteur |
|---|---|---|
| **Contenu statique** (docs, articles, pages publiques figées) | `search_web`, `read_url_content` (zéro navigateur lourd) | Sous-agent (`eclaireur` / `research`) |
| **Contenu dynamique, interactif ou recette UI** (horaires CFF, Maps, simulateurs, démarches, test visuel d'application locale) | MCP Playwright (`call_mcp_tool ServerName='playwright'`) | Sous-agent `eclaireur`, `executant` ou `auditeur-alignement`, jamais le superviseur (`Model: 'inherit'` si formulaire/démarche à risque irréversible, cf. [sous-agents.md](file:///c:/Users/Jamet/Documents/VoiceNotes/_agents/rules/sous-agents.md)) |

## 🛠️ Interaction avec les pages & Furtivité stricte (Chrome actif d'Henri)

- **Outils natifs d'abord & Preuve visuelle** : utiliser `browser_snapshot`, `browser_fill_form` / `browser_type`, `browser_click`, `browser_hover`, `browser_drag`, `browser_select_option` et consigner au fil de l'eau les extraits et captures horodatées (`browser_take_screenshot`) dans `sources_*.md`. Aucun script Python/shell interrogeant des API privées à la place de Playwright ; `browser_evaluate` / `browser_run_code_unsafe` uniquement en dernier recours face à un obstacle DOM.
- **Un seul agent Playwright à la fois (Sérialisation obligatoire)** : la page courante étant partagée dans le navigateur, ne jamais lancer deux sous-agents Playwright en parallèle (*ex. réel 13/10/2026, DLLP : `browser_fill_form` d'un agent exécuté dans l'onglet d'un autre*).
- **Onglets isolés et 100 % furtifs — INTERDICTION ABSOLUE DE VOLER LE FOCUS** :
  1. **Ouverture unique** : ouvrir **un seul** onglet dédié au début de la mission via `browser_tabs(action="new"[, url="..."])`, puis naviguer dedans avec `browser_navigate`.
  2. **Zéro mise au premier plan (`bringToFront` / `select` bannis)** : interdiction formelle d'appeler `browser_tabs(action="select")`, `page.bringToFront()` dans `browser_run_code_unsafe` ou `window.focus()` dans `browser_evaluate`. Cibler l'onglet en arrière-plan via `const target = page.context().pages().find(p => p.url().includes('...'))` sans jamais appeler `target.bringToFront()` (*ex. réel 14/10/2026, AIB A4 : onglets Dify/Wooclap surgissant au premier plan en continu pendant qu'Henri travaillait*).
  3. **Fermeture sécurisée (jamais le dernier onglet ni `browser_close`)** : en fin de mission, vérifier `browser_tabs(action="list")` et n'appeler `browser_tabs(action="close")` que s'il reste `> 1` onglet connecté au relai MCP (fermer le dernier onglet coupe définitivement l'extension Chrome — *ex. réel 14/10/2026, DLLP*). `browser_close` est strictement interdit.

## 🔒 Garde-fous financiers et administratifs

> [!CAUTION]
> 1. **Zéro achat** : aucun billet, ticket ni transaction financière.
> 2. **Zéro soumission finale sans accord** : pré-remplir avec les outils natifs ➔ capture nette (`browser_take_screenshot`) ➔ résumé télégraphique + capture à Henri ➔ attendre sa validation formelle avant tout clic d'envoi définitif.
