---
name: browser
description: "Assistance interactive sur formulaires web ou inspection de pages précises à la demande d'Henri."
---
# Skill Browser : Serveur MCP Playwright Permanent & Navigation Sémantique

Ce skill définit l'architecture, la matrice d'outils et les protocoles opérationnels pour la navigation, l'exploration web et l'assistance interactive via le **serveur officiel Microsoft Playwright MCP (`@playwright/mcp`)** dans l'écosystème Antigravity.

---

## 1. Architecture, Disponibilité Permanente & Arbre d'Accessibilité

### 1.1 Rôle & Déclenchement Exclusif à la Demande d'Henri
- **Usage Ciblé & Non-Autonome** : Ce skill ne doit pas être auto-invoqué par l'agent pour des explorations générales. Il est réservé aux situations où Henri demande expressément une assistance pour inspecter une page web précise ou interagir avec un formulaire web.
- **Primauté des Outils Directs** : Pour toute recherche ou collecte de données, l'agent utilise en priorité les outils CLI, les commandes système, les fichiers locaux et les MCP dédiés. Le navigateur n'intervient que pour les informations ou interactions inaccessibles autrement.

### 1.2 Paradigme SOTA : Arbre d'Accessibilité (`browser_snapshot`) & Références Stables (`ref`)
- **Élimination des Dumps HTML Lourds** : Fini les injections de pages HTML massives qui saturent la fenêtre de contexte.
- **Arbre d'Accessibilité Sémantique** : L'outil `browser_snapshot` capture la structure accessible de la page (rôles ARIA, libellés, valeurs, états actif/coché/sélectionné).
- **Identifiants Uniques Stables (`ref`)** : Chaque élément interactif est indexé par un identifiant court et stable (`ref`, ex: `ref="12"`), utilisable directement comme cible dans les outils d'interaction (`browser_click(ref="12")`, `browser_type(ref="12", text="...")`, etc.).
- **Recherche Ciblée Économe (`browser_find`)** : Pour localiser un élément sans recharger tout l'arbre, `browser_find` recherche par texte ou regex et renvoie uniquement le fragment hiérarchique pertinent avec son `ref`.

---

## 2. Matrice Canonique des 24 Outils Playwright MCP

Le serveur `@playwright/mcp` expose 24 outils spécialisés couvrant l'intégralité du cycle de navigation, d'inspection et d'action :

| Outil | Description & Rôle | Usage Type |
| :--- | :--- | :--- |
| `browser_navigate` | Navigue vers l'URL spécifiée. | Chargement initial d'une page ou changement d'adresse. |
| `browser_navigate_back` | Revient à la page précédente dans l'historique de navigation. | Retour arrière dans le flux. |
| `browser_snapshot` | Capture l'arbre d'accessibilité sémantique de la page avec les identifiants `ref`. | **Outil primaire d'observation** : analyse d'état, repérage des cibles. |
| `browser_find` | Recherche de texte ou regex dans l'arbre d'accessibilité. | Repérage rapide d'un élément précis et de son `ref` sans snapshot complet. |
| `browser_click` | Effectue un clic sur un élément via son `ref` ou sélecteur. | Activation de boutons, liens, cases à cocher, onglets. |
| `browser_hover` | Survole un élément interactif via son `ref`. | Déclenchement de menus flottants, infobulles (*tooltips*). |
| `browser_type` | Saisit du texte dans un champ éditable via son `ref`. | Saisie progressive de contenu texte. |
| `browser_fill_form` | Remplit en masse plusieurs champs d'un formulaire. | Remplissage groupé et atomique de formulaires. |
| `browser_select_option` | Sélectionne une ou plusieurs options dans un menu déroulant (`<select>`). | Choix dans des listes déroulantes standard. |
| `browser_press_key` | Émet une frappe clavier spécifique (`Enter`, `Tab`, `Escape`, flèches). | Validation clavier, navigation accessible, raccourcis. |
| `browser_drag` | Réalise un glisser-déposer (*drag and drop*) entre deux éléments. | Réorganisation de listes, interactions kanban. |
| `browser_drop` | Dépose des fichiers ou données MIME sur un élément cible. | Simulation de drop externe sur une zone de dépôt. |
| `browser_file_upload` | Téléverse un ou plusieurs fichiers locaux sur un champ d'upload. | Dépôt de documents, justificatifs, pièces jointes. |
| `browser_handle_dialog` | Répond ou rejette une boîte de dialogue native (`alert`, `confirm`, `prompt`). | Clôture des popups système bloquantes. |
| `browser_tabs` | Liste, crée, ferme ou sélectionne les onglets ouverts. | Gestion multi-onglets et bascule de contexte. |
| `browser_wait_for` | Attend l'apparition/disparition d'un texte ou l'écoulement d'un délai. | Synchronisation sur chargements asynchrones ou transitions UI. |
| `browser_evaluate` | Évalue une expression JavaScript dans la page ou sur un élément. | Extraction avancée de propriétés DOM en lecture seule. |
| `browser_console_messages` | Récupère l'historique des messages et erreurs console. | Diagnostic d'erreurs JavaScript ou avertissements front. |
| `browser_network_requests` | Liste numérotée des requêtes réseau depuis le chargement. | Surveillance des appels XHR / Fetch asynchrones. |
| `browser_network_request` | Fournit les détails complets (en-têtes, corps) d'une requête réseau précise. | Diagnostic de payload d'API ou d'échec de réponse HTTP. |
| `browser_take_screenshot` | Capture une image PNG de la page ou d'un élément spécifique. | Preuve visuelle, contrôle de rendu graphique. |
| `browser_resize` | Redimensionne la fenêtre du navigateur (dimensions viewport). | Tests de responsive design et adaptation mobile/desktop. |
| `browser_close` | Ferme la page courante du navigateur. | Nettoyage des pages de travail temporaires. |
| `browser_run_code_unsafe` | Exécute un snippet de code Playwright arbitraire dans le serveur. | Scripting complexe bas niveau (réservé aux cas spécifiques). |

---

## 3. Les Deux Modes d'Usage Opérationnels

Le skill opère selon deux modes d'action rigoureusement étanches selon la nature de la mission :

### 3.1 Mode 1 : Assistance Interactive & Formulaires Éthiques / Académiques d'Henri
Ce mode s'applique aux saisies sensibles sur des portails institutionnels (ex: formulaires éthiques CER-UNIL, administration des cours Moodle, configurations de plateformes scientifiques comme Prolific) :

- **Rôle d'Observateur & Guide Passif** : L'agent observe l'état du formulaire via `browser_snapshot` et prépare des propositions précises, mais **ne soumet pas de formulaire sensible unilatéralement**. C'est Henri qui applique manuellement les saisies et clique sur les validations critiques.
- **Plafond Strict de 5 Actions par Lot (≤ 5 actions)** :
  * Les actions sont découpées en paquets digestes de 1 à 5 actions maximum dans `<appDataDir>\brain\<conversation-id>\lot_actions_browser_XX.md` (`RequestFeedback: true`).
  * Chaque action comporte : localisation précise, libellé exact du champ, texte à copier prêt à l'emploi (fenced code block), et justification réglementaire/méthodologique.
  * Zéro texte barré (`line-through`) ni souligné (`underline`) dans les présentations de diffs.
- **Conformité Déterministe à `scientific-writing-style`** :
  * 0 Tiret Cadratin (Zero Em-Dash : proscription absolue de `—`, `---` ou `--`).
  * Proscription déterministe des clichés IA (avoid-ai-writing).
  * Posture et sobriété de chercheur senior (ton direct, factuel, zéro réchauffement).
- **Règle de l'Élagage au Fil de l'Eau (Pruning & Clean Artifact)** :
  * Dès qu'Henri applique une action et que la vérification `browser_snapshot` certifie sa présence conforme dans le DOM, l'action validée est **immédiatement purgée de l'artéfact**.
  * L'artéfact ne contient en permanence **que les actions restant réellement à accomplir**, et se termine propre et vide (ou message de validation totale).

### 3.2 Mode 2 : Automatisation Autonome (Scouts, Builders & Tests d'UI)
Ce mode s'applique à tous les agents d'exploration, de test et d'implémentation (ex: `hotel-scout`, cartographies Google Maps, prospection de documentation web, vérification d'interfaces graphiques développées par les builders) :

- **Autonomie Opérationnelle Complète** :
  * L'agent navigue librement (`browser_navigate`, `browser_navigate_back`, `browser_tabs`).
  * Il explore et interagit avec la page (`browser_snapshot`, `browser_click`, `browser_fill_form`, `browser_hover`, `browser_select_option`).
  * Il vérifie la stabilité des interfaces (`browser_wait_for`, `browser_take_screenshot`).
- **Zéro Blocage ni Cérémonie** : Les agents ne demandent aucune autorisation superflue pour naviguer, cliquer ou inspecter lors des missions de scoutisme ou de test.

---

## 4. Preuve Matérielle Obligatoire & Doctrine Zero-Trust

Conformément aux principes Zero-Trust régissant Antigravity :

1. **Zéro Simulation & Zéro Extrapolation** :
   - INTERDICTION STRICTE d'extrapoler ou d'inventer le contenu d'une page web sans appel d'outil réel.
   - Ne jamais prétendre avoir inspecté un site, un formulaire ou une cartographie sans avoir exécuté les outils Playwright.
2. **Preuves Brutes Obligatoires** :
   - Toute affirmation relative à l'état d'une page doit être appuyée par des données factuelles vérifiables :
     * Extrait textuel du nœud d'accessibilité issu de `browser_snapshot` ou `browser_find` avec son `ref` et ses attributs réels.
     * Ou capture d'écran horodatée issue de `browser_take_screenshot`.
3. **Rejet Systématique des Rapports Non Sourcés** :
   - Tout retour de sous-agent prétendant avoir validé une page web sans citation textuelle mot à mot issue de `browser_snapshot` ou preuve visuelle est rejeté comme complaisance ou simulation trompeuse.
