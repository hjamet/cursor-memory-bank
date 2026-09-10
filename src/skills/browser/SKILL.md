---
name: browser
description: Lis absolument ce skill lorsque l'utilisateur invoque le workflow /browser pour piloter son navigateur Chrome de bureau.
---

# Skill Browser — Automatisation & Pilotage Avancé de Chrome

Ce skill définit le protocole officiel, l'architecture et les règles opérationnelles pour le pilotage de Google Chrome via la passerelle MCP `chrome_devtools` dans l'écosystème Antigravity.

---

## 1. Architecture & Déclenchement

### 1.1 Déclenchement Automatique
- **Commandes utilisateur** : `/browser` ou toute demande nécessitant l'interaction avec le web, le scraping dynamique, le remplissage de formulaires ou la manipulation d'applications web.
- **Activation MCP** : Dès l'invocation, Antigravity arme et connecte dynamiquement la passerelle MCP `chrome_devtools`.

### 1.2 Délégation Obligatoire au Sous-Agent (`TypeName: 'browser'`)
> [!IMPORTANT]
> **Règle Fondamentale de Délégation** :
> L'agent principal **NE DOIT PAS** exécuter directement les boucles d'interactions Chrome dans son contexte principal.
> Il **DOIT IMPÉRATIVEMENT** déléguer la mission à un sous-agent spécialisé en spécifiant :
> ```json
> {
>   "TypeName": "browser"
> }
> ```
> **Pourquoi cette isolation ?**
> - Préserve la fenêtre de contexte de l'agent principal.
> - Isole les payloads volumineux (captures d'écran, logs DOM, réponses réseau XHR).
> - Permet une boucle d'itération rapide (navigate -> click -> inspect -> evaluate) sans saturer l'historique conversationnel de haut niveau.

### 1.3 Environnement & Sessions Actives d'Henri
- Le serveur MCP `chrome_devtools` se connecte directement à l'instance Google Chrome de bureau active de l'utilisateur (**Henri**).
- **Accès complet aux sessions authentifiées** : L'agent bénéficie automatiquement de toutes les sessions connectées et des cookies existants d'Henri (ex. **Dify, Moodle, GitHub, Webmail, Drive, consoles cloud, applications intranet et locales**).
- **Pas de ré-authentification manuelle** : Si l'utilisateur est déjà connecté à un service sur son Chrome, aucune étape de reconnexion ou d'échange de mots de passe n'est requise.

---

## 2. Inventaire des Outils `chrome_devtools`

La passerelle `chrome_devtools` met à disposition une suite complète d'outils d'automatisation et d'inspection :

| Outil | Catégorie | Description & Rôle |
| :--- | :--- | :--- |
| `list_pages` | Gestion d'onglets | Liste l'ensemble des cibles/onglets ouverts avec leurs IDs, titres et URLs. |
| `new_page` | Gestion d'onglets | Crée un nouvel onglet et navigue vers l'URL spécifiée. |
| `select_page` | Gestion d'onglets | Sélectionne la page active sur laquelle les commandes suivantes s'appliqueront. |
| `close_page` | Gestion d'onglets | Ferme un onglet spécifique via son identifiant de page. |
| `navigate_page` | Navigation | Charge une URL dans la page active en cours. |
| `click` | Interaction DOM | Déclenche un clic sur un élément identifié (sélecteur CSS, XPath ou coordonnées). |
| `fill` | Interaction DOM | Remplit la valeur d'un champ de saisie (`input`, `textarea`). |
| `type_text` | Interaction DOM | Simule la frappe clavier au niveau caractère ou raccourcis système. |
| `take_screenshot` | Inspection visuelle | Capture une image de la page ou d'un élément spécifique pour vérification. |
| `evaluate_script` | Exécution JS | Exécute du code JavaScript dans le contexte de la page pour extraire du contenu ou manipuler le DOM. |
| `list_network_requests` | Réseau & Logs | Inspecte les requêtes réseau (XHR/Fetch), statuts HTTP et en-têtes pour déboguer les API. |

---

## 3. Protocole Opérationnel d'Automatisation

Pour garantir une exécution robuste, prévisible et sans erreur, tout sous-agent `browser` applique le cycle d'exécution en 6 étapes :

```mermaid
flowchart TD
    A[1. list_pages] --> B{Onglet cible déjà ouvert ?}
    B -- Oui --> C[2. select_page]
    B -- Non --> D[2. new_page avec URL cible]
    C --> E[3. evaluate_script ou inspection DOM]
    D --> E
    E --> F[4. Actions ciblées : click / fill / type_text]
    F --> G[5. Vérification : screenshot ou evaluate_script]
    G --> H{Objectif atteint ?}
    H -- Non --> E
    H -- Oui --> I[6. Rapport structuré & Nettoyage]
```

### Étape 1 : Cartographie des Onglets (`list_pages`)
Toujours exécuter `list_pages` en premier. Cela permet de vérifier si l'application visée (ex. un canvas Dify ou un cours Moodle) est déjà ouverte dans un onglet existant pour éviter d'ouvrir des doublons et réutiliser la session ouverte.

### Étape 2 : Ciblage / Ouverture (`select_page` ou `new_page`)
- Si l'onglet existe déjà : exécuter `select_page` avec le `pageId` correspondant.
- Si l'onglet n'existe pas : exécuter `new_page` avec l'URL souhaitée.

### Étape 3 : Attente & Analyse de l'État DOM
- Utiliser `evaluate_script` pour inspecter la présence d'éléments clés ou vérifier la complétion des requêtes asynchrones.
- Privilégier les sélecteurs stables : `data-testid`, `aria-label`, IDs explicites ou sélecteurs CSS uniques.

### Étape 4 : Interactions Structurées
- Enchaîner les commandes `fill`, `click`, ou `type_text` de manière ciblée.
- Prévoir de courts délais de transition si l'interface déclenche des animations ou des requêtes réseau en arrière-plan.

### Étape 5 : Validation & Feedback Visuel
- Valider le résultat de chaque action critique :
  - Soit par extraction de texte / validation d'état via `evaluate_script`.
  - Soit par capture visuelle via `take_screenshot` (particulièrement utile pour les interfaces complexes, canvas, éditeurs graphiques ou diagnostics d'erreurs).

### Étape 6 : Synthèse & Clôture
- Si des onglets éphémères de travail ont été créés, fermer uniquement ceux qui ont été initiés par la tâche (`close_page`).
- Remonter un rapport concis et documenté à l'agent principal via `send_message`.

---

## 4. Règles de Sécurité et Bonnes Pratiques

> [!CAUTION]
> **Préservation de l'espace de travail d'Henri** :
> - Ne jamais fermer un onglet préexistant ouvert par l'utilisateur sans instruction explicite.
> - Ne jamais modifier ou écraser des données de session ou profils utilisateurs critiques sans validation.
> - Ne pas divulguer de tokens, cookies d'authentification ou données d'identification personnelles dans les logs de compte-rendu.

---

## 5. Directives Doctrinales d'Exécution, de Sécurité & de Restitution (MANDATOIRE)

### 5.1 Exécution Réelle Préalable & Zéro Simulation (Action-First)
- Le sous-agent browser doit **TOUJOURS exécuter physiquement l'action** (`click`, `fill`, `type_text`, `evaluate_script`) dans le navigateur et vérifier l'état du DOM résultant **AVANT** de formuler son rapport.
- **Interdiction formelle de prétendre qu'une case est cochée, qu'un champ est rempli ou qu'une action est accomplie** tant que l'opération n'a pas été matériellement constatée et vérifiée dans la page web.

### 5.2 Règle Absolue de Sécurité : Interdiction Formelle des Actions Définitives
> [!CAUTION]
> **Validation et Soumission Finale Réservées Exclusivement à l'Utilisateur** :
> - **Interdiction formelle et absolue de soumettre ou de cliquer sur des boutons d'action définitive ou irréversible** : boutons d'envoi (`Submit`, `Send`, `Soumettre`), boutons de suppression définitive (`Delete`, `Purger`), boutons de validation finale (`Finaliser`, `Valider définitivement`, `Complete application`).
> - **C'est TOUJOURS à Henri (l'utilisateur) de procéder à la vérification finale et au clic de soumission ultime**. L'agent prépare, remplit, coche et inspecte, mais s'arrête impérativement avant le point de non-retour pour laisser la main à Henri.

### 5.3 Délégation Systématique de la Recherche Documentaire
- L'agent browser a pour rôle exclusif l'interaction, le remplissage et l'inspection de la page web.
- **Interdiction de chercher soi-même dans les notes ou fichiers du coffre** : Dès qu'une valeur, un texte, un chiffre, une décision éthique ou un contexte documentaire manque pour compléter un champ, l'agent browser doit impérativement déléguer cette recherche à un sous-agent dédié (`research` ou `self`) via `invoke_subagent` et attendre sa réponse.

### 5.4 Progression Incrémentale par Page / Bloc Logique
- **Plafond de lot strict** : Remplir une quantité raisonnable d'éléments à la fois — **strictement limitée à une seule page ou un seul bloc logique cohérent** (environ 3 à 5 champs maximum).
- **Arrêt et rapport systématique** après chaque page ou bloc logique pour permettre à Henri de valider, commenter ou ajuster avant de poursuivre sur les champs suivants.
- Ne jamais tenter de remplir un formulaire entier d'un coup sans validation intermédiaire.

### 5.5 Restitution par l'Agent Principal via Artéfact de Suivi & Diffs HTML Propres
- L'agent principal centralise et présente les modifications dans un **artéfact de session dédié** (`RequestFeedback: true`) pour permettre une revue claire, structurée et commentable.
- Pour tout diff visuel en HTML, respecter scrupuleusement la charte de lisibilité d'Henri :
  * **Suppression / Remplacement** : `<del style="color:#cf222e; background-color:#ffeef0; text-decoration:none; display:block; padding:8px; border-radius:4px; font-family:monospace; font-size:12px;">...</del>` (texte rouge, fond rouge doux, **SANS texte barré**).
  * **Ajout / Nouvelle valeur** : `<ins style="color:#116329; background-color:#dafbe1; text-decoration:none; display:block; padding:8px; border-radius:4px; font-family:monospace; font-size:12px;">...</ins>` (texte vert, fond vert doux, **SANS texte souligné**).
  * **Strictement aucun texte barré (`line-through`) ni souligné (`underline`)** : la lisibilité doit rester optimale pour les textes longs et les documents administratifs ou d'éthique.
