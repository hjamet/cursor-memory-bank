---
description: "Doctrine d'usage du MCP Playwright : distinction statique vs dynamique, outils natifs et garde-fous de soumission."
trigger: always_on
---

# 🌐 Navigation Web & MCP Playwright (Statique vs Dynamique & Garde-Fous)

## 🧭 Quel outil pour quel besoin ?

| Besoin | Outils | Acteur |
|---|---|---|
| **Contenu statique** (documentation, articles, définitions, informations publiques figées) | `search_web`, `read_url_content` ; pas de navigateur lourd | Sous-agent de recherche |
| **Contenu dynamique ou interactif** (horaires en direct CFF/sbb.ch, Google Maps, simulateurs, démarches en ligne) | MCP Playwright uniquement (`call_mcp_tool ServerName='playwright'`) | Sous-agent `eclaireur` ou `executant`, jamais le superviseur (`Model: 'inherit'` pour toute manipulation de formulaire ou démarche à risque irréversible, cf. [sous-agents.md](file:///c:/Users/hjamet/Documents/VoiceNotes/_agents/rules/sous-agents.md)) |

## 🛑 Quel cycle de preuve et d'audit s'applique ?
- Le superviseur ne manipule jamais Playwright lui-même (cf. [superviseur-aveugle.md](file:///c:/Users/hjamet/Documents/VoiceNotes/_agents/rules/superviseur-aveugle.md)).
- Le sous-agent consigne au fil de l'eau ses extraits et ses captures horodatées (`browser_take_screenshot`) dans son artefact de sources, puis renvoie `ARTEFACT: <chemin>`.
- Le superviseur applique aussitôt l'audit contradictoire (`auditeur-alignement`) et restitue avec le paragraphe `🔎 Audit <Rôle>`.

## 🛠️ Comment interagir avec les pages ?
- **Outils natifs d'abord** : `browser_snapshot` (arborescence, sélecteurs), `browser_fill_form` / `browser_type` (formulaires), `browser_click`, `browser_hover`, `browser_drag`, `browser_select_option`, `browser_take_screenshot` (preuve obligatoire).
- **Pas de contournement** : pas de script Python ou shell interrogeant des API privées à la place de Playwright. `browser_evaluate` et l'exécution de code ne servent qu'en dernier recours, face à un obstacle DOM que les outils natifs ne franchissent pas.
- **Un seul agent Playwright à la fois** : la « page courante » est globale au navigateur partagé ; tout `browser_tabs(action="new")` d'un agent déplace la cible des outils de tous les autres. Jamais deux sous-agents Playwright en parallèle : les sérialiser. *Ex. réel (13/10/2026, DLLP) : 2 enseignants simulés + 1 exécutant Prolific lancés ensemble ; `browser_fill_form` de l'un exécuté dans l'onglet de l'autre, simulation E arrêtée.*
- **Onglets isolés et furtifs — INTERDICTION ABSOLUE DE METTRE AU PREMIER PLAN** (le navigateur est le Chrome actif d'Henri) :
  - **Ouverture unique** : ouvrir **un seul** onglet dédié au début de la mission via `browser_tabs(action="new"[, url="..."])`, puis naviguer dedans avec `browser_navigate`. Ne jamais ouvrir des onglets en boucle.
  - **Zéro vol de focus (`bringToFront` / `select` bannis)** : il est **strictement interdit** d'appeler `browser_tabs(action="select")`, d'appeler `page.bringToFront()` dans `browser_run_code_unsafe`, ou d'exécuter `window.focus()` dans `browser_evaluate`. Dans `browser_run_code_unsafe`, cibler un onglet en arrière-plan via `const target = page.context().pages().find(p => p.url().includes('...'))` et agir directement sur `target` (`target.goto()`, `target.locator()`, `target.evaluate()`, `target.screenshot()`) **sans jamais appeler `target.bringToFront()`**. *Ex. réel (14/10/2026, AIB A4) : un exécutant alternant entre Dify et Wooclap via `browser_run_code_unsafe` appelait `targetPage.bringToFront()` à chaque étape, faisant surgir les onglets Chrome au premier plan en continu pendant qu'Henri travaillait.*
  - **Fermeture (sauf dernier onglet du relai MCP)** : à la fin de la mission, vérifier le nombre d'onglets via `browser_tabs(action="list")` et n'appeler `browser_tabs(action="close")` que s'il reste au moins un autre onglet connecté au relai (`> 1` onglet). Il est **strictement interdit** de fermer le dernier onglet connecté à l'extension Playwright MCP, sous peine de déconnecter définitivement le pont MCP du navigateur. *Ex. réel (14/10/2026, DLLP) : un exécutant a appelé `browser_tabs(action="close")` sur l'unique onglet attaché au relai MCP, coupant la connexion de l'extension Chrome avant une supervision `/goal` nocturne.*
  - **`browser_close` interdit pour fermer un onglet** : il tente de détruire le contexte partagé et lève une exception bloquante en mode extension.

## 🔒 Quels garde-fous financiers et administratifs ?

> [!CAUTION]
> 1. **Zéro achat** : aucun billet, ticket ni transaction financière.
> 2. **Zéro soumission finale** : pré-remplir est permis ; cliquer sur le bouton d'envoi ou de soumission définitive est interdit sans accord explicite d'Henri.
> 3. **Procédure** : remplir les champs avec les outils natifs ➔ capture nette (`browser_take_screenshot`) ➔ résumé télégraphique des champs renseignés + capture à Henri ➔ attendre sa validation formelle.
