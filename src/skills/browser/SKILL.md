---
name: browser
description: Lis absolument ce skill lorsque l'utilisateur invoque le workflow /browser pour piloter son navigateur Chrome de bureau.
---

# Skill Browser : Observation Passive, Contrôle Manuel par Lots & Sous-Agent Persistant

Ce skill définit le protocole officiel, l'architecture et les règles opérationnelles pour l'accompagnement sur Google Chrome via la passerelle MCP `chrome_devtools` dans l'écosystème Antigravity.

Conformément à la doctrine établie par Henri Jamet, ce skill repose sur trois principes cardinaux :
1. **L'agent browser est les « yeux » passifs du système, jamais les « mains » d'écriture** : toutes les saisies et soumissions sont opérées manuellement par l'utilisateur (Henri), assisté par l'agent principal.
2. **Plafond strict de 5 actions maximum par round** : découpage en lots ultra-digestes (1 à 5 actions) garantissant une vigilance maximale, un audit chirurgical pas à pas et zéro surcharge cognitive.
3. **Boucle d'exploration en profondeur et conformité académique** : observation exhaustive du DOM, cohérence multi-onglets (ex: Prolific vs formulaire LOOP vs notes Obsidian), audit console, et respect strict des règles de `scientific-writing-style` (0 tiret cadratin, 0 cliché IA, ton sobre de chercheur senior).

---

## 1. Architecture, Déclenchement & Persistance Absolue

### 1.1 Condition d'Activation des Outils (`/browser`) & Invariance Absolue du Type (`TypeName: 'browser'`)
> [!IMPORTANT]
> **Mécanisme d'Injection des Outils dans Antigravity** :
> Dans Google Antigravity, les outils d'automatisation et de contrôle du navigateur (`chrome_devtools` : `list_pages`, `new_page`, `select_page`, `click`, `fill`, `type_text`, `evaluate_script`, `take_screenshot`, etc.) **ne sont jamais injectés par défaut** dans l'environnement.
> Ils ne sont injectés et mis à la disposition du superviseur et des sous-agents **QUE SI l'utilisateur (Henri) invoque explicitement la commande slash `/browser` dans son message**.
> - **Si `/browser` est présent dans le message** : Antigravity arme et injecte dynamiquement la passerelle MCP `chrome_devtools` reliée à l'instance Chrome active d'Henri.
> - **Si `/browser` est absent du message** : Même si la tâche porte sur la navigation web, les outils `chrome_devtools` n'existent pas dans l'environnement d'exécution. Ni le superviseur ni le sous-agent ne peuvent s'auto-octroyer ces outils.

> [!CAUTION]
> **Interdiction Formelle de `TypeName: 'self'` pour le Browser** :
> - Le sous-agent dédié au navigateur DOIT ÊTRE INVOQUÉ STRICTEMENT avec `TypeName: 'browser'`.
> - L'utilisation de `TypeName: 'self'` pour tenter de piloter le navigateur est une **ANOMALIE CRITIQUE MAJEURE** car elle prive le worker des outils `chrome_devtools`.

### 1.2 Règle Fondamentale de Persistance Absolue du Sous-Agent Browser
> [!IMPORTANT]
> **Invocation Unique & Maintien en Vie Permanent** :
> L'agent principal ne doit **JAMAIS** exécuter directement les outils du navigateur dans son fil de discussion principal, et doit impérativement déléguer à un sous-agent browser (`TypeName: 'browser'`).
> Cependant, une règle stricte régit son cycle de vie :
> 1. **Invocation Unique** : Invoquer le sous-agent browser **UNE SEULE FOIS** au moment où Henri tape `/browser`.
> 2. **Persistance Totale pour Toute la Session** : **INTERDICTION FORMELLE DE TUER ET RÉ-INVOQUER** un nouveau sous-agent browser en cours de route.
>    * *Pourquoi ?* Tuer et recréer le sous-agent fait perdre l'historique d'exploration, le contexte d'inspection DOM et l'accès dynamique aux outils injectés.
> 3. **Communication Exclusif via `send_message`** : L'agent principal réveille et pilote le sous-agent browser **EXCLUSIVEMENT via `send_message`** à chaque cycle d'audit et de vérification.

### 1.3 Environnement & Sessions Actives d'Henri
- Le serveur MCP `chrome_devtools` se connecte directement à l'instance Google Chrome de bureau active de l'utilisateur (**Henri**).
- **Accès complet aux sessions authentifiées** : L'agent bénéficie automatiquement de toutes les sessions connectées et des cookies existants d'Henri (ex. **Dify, Moodle, GitHub, Webmail, Drive, portails éthiques, consoles cloud, intranets et applications locales**).
- **Zéro ré-authentification manuelle** : Si l'utilisateur est déjà connecté à un service sur son Chrome, aucune étape de reconnexion ou de transmission de mots de passe n'est requise.

### 1.4 Doctrine Fail-Stop sur Indisponibilité des Outils, Règle Anti-Bricolage & Demande d'Accès
> [!CAUTION]
> **Arrêt Immédiat (Fail-Stop), Interdiction Absolue de Contournement & Demande d'Accès** :
> Si le sous-agent `browser` est invoqué mais constate que les outils `chrome_devtools` (`list_pages`, `new_page`, etc.) ne sont pas disponibles dans son environnement (l'utilisateur n'a pas tapé `/browser` dans son message, session expirée ou réinitialisée) :
> 1. **ARRÊT IMMÉDIAT & INCONDITIONNEL (FAIL-STOP)** : Le sous-agent et l'agent appelant DOIVENT S'ARRÊTER IMMÉDIATEMENT.
> 2. **INTERDICTION ABSOLUE DE CONTOURNEMENT OU BRICOLAGE** : Ne JAMAIS fabriquer d'outils maison (scripts Python, CDP direct, sockets). **INTERDICTION FORMELLE ET ABSOLUE** de basculer sur des recherches de fichiers locaux (OneDrive, documents locaux) ou d'extrapoler pour meubler ou simuler une navigation web. Tout contournement ou simulation est qualifié d'anomalie critique majeure.
> 3. **MESSAGE CANONIQUE OBLIGATOIRE & DEMANDE D'ACCÈS À HENRI** : Le sous-agent renvoie mot pour mot à l'agent appelant, et l'agent appelant demande explicitement à Henri d'invoquer le skill `/browser` dans son prochain message pour débloquer l'accès aux outils :
>    « *Les outils du navigateur ne sont pas disponibles dans cette session. Pour m'y donner accès, veuillez simplement inclure la commande `/browser` dans votre prochain message.* »

---

## 2. Le Nouveau Paradigme : Observation & Exploration Passive

### 2.1 Rôle Exclusif : Les « Yeux » du Système
L'agent browser opère comme un observateur expert et passif :
- **Identification de l'état** : Il observe la page active, repère où en est Henri dans son formulaire ou sa navigation, et cartographie les sections visibles et masquées.
- **Inspection structurelle du DOM** : Il extrait les sélecteurs, inspecte les champs, étudie les contraintes de validation (champs requis, formats attendus, options de listes déroulantes).
- **Exploration non-destructive** : Il peut cliquer pour déplier un menu, explorer des sous-sections ou dérouler un accordéon à seule fin d'inspecter ce qui manque.
- **Diagnostic technique** : Il inspecte la console JavaScript et les requêtes réseau (XHR/Fetch) via `list_network_requests` pour détecter les erreurs asynchrones ou blocages techniques.

### 2.2 Zéro Écriture Automatique (Contrôle Manuel Exclusif par Henri)
> [!CAUTION]
> **Interdiction Formelle et Absolue d'Écriture Automatique** :
> - L'agent browser ne doit **JAMAIS modifier, remplir (`fill`, `type_text`) ou cliquer pour soumettre des données sur la page web**.
> - C'est **TOUJOURS l'utilisateur (Henri)** qui effectue physiquement les saisies de texte, les coches de cases, les sélections de menus et les clics de soumission.
> - **Raison fondamentale** : Intégrité des données, conformité éthique et administrative, souveraineté totale de l'utilisateur, et élimination de tout risque d'hallucination ou de soumission intempestive.

### 2.3 Classification Rigoureuse des Outils `chrome_devtools`

| Statut | Outils | Usage Autorisé / Proscrit |
| :--- | :--- | :--- |
| **Observation & Inspection** | `list_pages`, `select_page`, `evaluate_script` *(lecture seule)*, `take_screenshot`, `list_network_requests` | **✅ PLEINEMENT AUTORISÉ** : inspection du DOM, extraction d'arborescences, repérage de sélecteurs, diagnostic réseau et console. |
| **Exploration Passive** | `click` *(sur éléments non-mutatifs uniquement)*, `navigate_page` *(si navigation demandée)* | **✅ AUTORISÉ SOUS RÉSERVE** : ouvrir un menu déroulant, déplier un accordéon pour en lire le contenu. **INTERDIT** sur tout bouton de soumission ou de validation. |
| **Écriture & Mutation** | `fill`, `type_text`, `click` *(soumission)*, `evaluate_script` *(injection de valeurs DOM)* | **❌ STRICTEMENT INTERDIT** : aucune frappe clavier automatique, aucun remplissage de formulaire, aucun clic d'envoi. |

---

### 2.4 Rôle d'Observateur-Scout Complet & Exploration en Profondeur (Anti-Récursion)
> [!IMPORTANT]
> **Anti-Récursion Canonique & Autonomie d'Exploration de l'Agent Browser** :
> - Conformément à la règle anti-récursion d'Antigravity (les sous-agents sont des exécutants et ne créent jamais de sous-sous-agents), l'agent browser ne délègue à aucun tiers.
> - **Il conduit lui-même l'exploration minutieuse en profondeur** :
>   1. **Audit DOM chirurgical** : analyse de l'arborescence, détection des balises d'état, des champs conditionnels et des contraintes de validation côté client.
>   2. **Audit multi-onglets & cohérence croisée** : bascule (`select_page`) pour examiner les onglets connexes (ex: tableau de bord Prolific vs formulaire d'évaluation LOOP vs portail éthique) afin de certifier l'alignement des IDs, des redirections et des paramètres de l'étude.
>   3. **Contrôle console & réseau** : surveillance proactive des exceptions JavaScript et des requêtes réseau défaillantes pour prévenir tout blocage silencieux.

---

## 3. Batching par Lots de 5 Actions Maximum

### 3.1 Plafond de Lot Strict (≤ 5 actions)
Pour prévenir toute surcharge cognitive et assurer une exécution manuelle rapide, sécurisée et fluide par Henri :
- Les actions nécessaires identifiées par l'observation de la page sont découpées en **paquets digestes de 5 actions maximum à la fois** (actions 1 à 5).
- Chaque action est atomique, non ambiguë et directement actionnable (ex: « Copier la valeur X dans le champ Y », « Sélectionner l'option Z »).
- **Interdiction formelle de dépasser 5 actions par round** : ce format resserré garantit une concentration maximale, une vérification immédiate et un contrôle total à chaque étape.

### 3.2 Artéfact Dédié dans la Brain de Session
L'agent principal consigne et présente chaque lot dans un artéfact temporaire dédié situé dans `<appDataDir>\brain\<conversation-id>\lot_actions_browser_XX.md` avec `RequestFeedback: true` :
- **Structure ultra-lisible** : Tableau clair ou liste numérotée (1 à 5 maximum).
- **Contenu directement copiable** : Blocs de texte prêts à copier en un clic, intitulés exacts des champs et boutons cibles.
- **Charte de lisibilité sans texte barré** : Si des diffs ou ajustements sont présentés, respecter scrupuleusement la charte d'Henri :
  * Ajout / Nouvelle valeur : `<ins style="color:#116329; background-color:#dafbe1; text-decoration:none; display:block; padding:8px; border-radius:4px; font-family:monospace; font-size:12px;">...</ins>` (fond vert doux, texte vert, **sans soulignement**).
  * Suppression / Remplacement : `<del style="color:#cf222e; background-color:#ffeef0; text-decoration:none; display:block; padding:8px; border-radius:4px; font-family:monospace; font-size:12px;">...</del>` (fond rouge doux, texte rouge, **sans texte barré**).
  * **Strictement aucun texte barré (`line-through`) ni souligné (`underline`)**.
- **File de travail dynamique** : L'artéfact n'est pas un compte-rendu statique mais une file d'attente vivante soumise au principe d'élagage progressif au fil de l'eau.

### 3.3 Conformité Stricte à `scientific-writing-style` (Textes Proposés)
> [!IMPORTANT]
> **Barrières Déterministes Anti-IA pour Tout Texte Proposé** :
> Lorsque les actions préparent du texte destiné à être injecté dans un formulaire académique, scientifique ou institutionnel (ex: formulaires LOOP, interfaces Prolific, comités d'éthique CER-UNIL, déclarations méthodologiques) :
> 1. **0 Tiret Cadratin (Zero Em-Dash)** : Interdiction stricte de `—`, `---` ou `--` dans les textes proposés. Utiliser des virgules, des parenthèses, deux-points ou des phrases distinctes.
> 2. **Proscription Déterministe des Clichés IA** : Purge systématique des termes de la table avoid-ai-writing (ex: proscrire *foster*, *seamless*, *comprehensive*, *robust*, *leverage*, *crucial*, *pivotal*, *delve*, *showcase*, *intricate*, *testament to*, *tapestry*, *landscape*).
> 3. **Posture & Sobriété de Chercheur Senior** : Ton direct, sobre et purement factuel. Zéro superlatif non quantifié, zéro phrase de réchauffement (*padding*), vocabulaire technique précis.

### 3.4 Règle de l'Élagage au Fil de l'Eau (Pruning & Clean Artifact)
> [!IMPORTANT]
> **Règle de l'Élagage au Fil de l'Eau (Pruning & Clean Artifact)** :
> - **Suppression progressive des actions validées** : Dès qu'une action d'un lot est appliquée manuellement par Henri et certifiée conforme par l'audit DOM de l'agent browser, l'action validée **DOIT ÊTRE SUPPRIMÉE** de l'artéfact de lot.
> - **Contenu résiduel strict** : L'artéfact ne contient en permanence **QUE les actions restant réellement à faire**. Il ne conserve aucun élément déjà validé.
> - **Artéfact propre et vide à terme** : À la fin du lot, lorsque toutes les actions sont validées, l'artéfact devient vide (ou affiche un simple message de clôture 100% propre).

### 3.5 Format Canonique Obligatoire des Artéfacts de Consignes par Lot
Pour éliminer toute friction cognitive et guider pas à pas Henri lors de la saisie manuelle dans Chrome :

- **Attaque Directe & Zéro Boilerplate** :
  * Strictement **zéro note boilerplate / zéro encadré didactique** en tête d'artéfact.
  * Attaque directe et immédiate par le titre H1 du lot (ex: `# Lot 1 : Déclarations Éthiques & Affiliations`).
- **Plafond Strict de 5 Actions par Lot** : Tout artéfact de consignes est strictement plafonné à 5 actions maximum (actions 1 à 5).
- **Élagage au Fil de l'Eau** : Chaque action auditée et validée par l'agent browser est immédiatement purgée de l'artéfact.
- **Gabarit Normalisé pour Chaque Action (1 à 5)** :
  Chaque action dans l'artéfact doit impérativement respecter la structure canonique suivante :

````markdown
### [ ] Action X : <Titre explicite de l'action>

- **Où** : Localisation fluide en langage naturel et repères par rapport aux questions voisines.
- **Quoi faire** : Action directe (clic, sélection, remplacement de texte).
- **Texte à copier** (si champ de saisie) : Fenced code block ```text propre (strictement conforme à `scientific-writing-style` : 0 tiret cadratin, 0 cliché IA, ton sobre).
- **Callout de justification** :
  > [!NOTE]
  > **Justification (Source / d'après moi)** : Explication pédagogique, réglementaire (LRH, nLPD, CER-UNIL) ou méthodologique du choix.
````

- **Clôture de Lot (Artéfact Épuré)** :
  Lorsque la dernière action du lot est validée, l'artéfact devient vide ou affiche :
```markdown
# Lot X : Validé

🎉 Toutes les actions de ce lot ont été appliquées et certifiées conformes par l'audit DOM.
```

---

## 4. Cycle de Validation Interactif en 5 Temps & Boucle d'Audit Exhaustif

Le travail collaboratif entre Henri, l'agent principal et l'agent browser suit rigoureusement un cycle découpé en 5 temps intégrant une exploration en amont et un audit exhaustif en aval :

```mermaid
sequenceDiagram
    autonumber
    participant B as Agent Browser (Persistant / Scout)
    participant P as Agent Principal (Superviseur)
    participant H as Henri (Utilisateur)

    Note over B: Exploration minutieuse en profondeur<br/>(DOM, onglets connexes Prolific/LOOP, console)
    B->>P: Rapport d'état DOM, cohérence multi-sources & éléments manquants
    Note over P: Temps 1 : Découpage par lots (≤ 5 actions)<br/>Conformité scientific-writing-style
    P->>H: Présente l'artéfact de session (lot de 5 actions max)
    
    alt Temps 2 : Henri demande des ajustements
        H->>P: Commentaires / ajustements sur l'artéfact
        Note over P: L'agent principal ajuste l'artéfact (sous-agent recherche si besoin) SANS déranger l'agent browser
        P->>H: Artéfact mis à jour
    end

    Note over H: Temps 3 : Henri applique manuellement les 5 actions dans Chrome
    H->>P: Temps 4 : Validation (« Done », « Ok, c'est bon »)
    
    Note over P,B: Temps 5 : Réveil & Audit Exhaustif en Profondeur
    P->>B: send_message (audit chirurgical des 5 actions + cohérence globale)
    Note over B: Inspecte le DOM (valeurs réelles),<br/>vérifie console/réseau & onglets connexes
    B->>P: Rapport exhaustif (validation confirmée ou écarts détectés)
    Note over P: Planification du lot suivant de 5 actions (Temps 1)
```

### Temps 1 : Exploration en Profondeur Préalable & Présentation du Lot (≤ 5 actions)
- **Exploration préalable par l'agent browser** : avant toute formulation de lot, l'agent browser conduit lui-même (en respect de la règle anti-récursion) un diagnostic approfondi de la page active, de la console et des onglets connexes (ex: concordance Prolific vs LOOP).
- **Synthèse par l'agent principal** : l'agent principal formule un lot restreint de **5 actions au maximum** (actions 1 à 5).
- **Validation stylistique** : tous les textes proposés respectent strictement `scientific-writing-style` (0 tiret cadratin, 0 cliché IA, ton chercheur senior).
- **Mise à disposition** : génération ou mise à jour de l'artéfact temporaire de session dédié (`RequestFeedback: true`).

### Temps 2 : Revue & Ajustements par Henri (Sans Déranger le Browser)
- Henri lit l'artéfact et peut poser des questions ou demander des modifications de fond.
- **Règle d'Isolation** : L'agent principal effectue les ajustements de l'artéfact (en déployant au besoin des sous-agents de recherche documentaire dans le coffre) **SANS SOLLICITER L'AGENT BROWSER**.
- Le sous-agent browser reste au repos, préservant son contexte.

### Temps 3 : Application Manuelle par Henri
- Henri applique manuellement les 5 actions sur sa page web dans Google Chrome (copier-coller des textes préparés, sélection des boutons radio/checkboxes, saisies).
- Henri dispose de son propre rythme et d'un contrôle visuel total sur son navigateur.

### Temps 4 : Signal de Clôture d'Henri
- Une fois les modifications complétées, Henri envoie un message simple dans le chat :
  * **« Done »** (ou équivalent : « Ok, c'est bon », « Fait », « C'est bon pour ce lot »).

### Temps 5 : Boucle d'Audit Exhaustif & Vérification en Profondeur par l'Agent Browser Persistant
- L'agent principal réveille l'agent browser persistant via `send_message` en lui transmettant la liste exacte des 5 actions à vérifier ainsi que les contrôles de cohérence associés.
- L'agent browser exécute une inspection approfondie et autonome (anti-récursion) :
  1. **Vérification chirurgicale du DOM** : lecture des attributs `value`, `innerText`, statut des cases `checked` via `evaluate_script` en lecture seule.
  2. **Audit console et réseau** : contrôle des messages d'erreur, avertissements ou échecs de requêtes Fetch/XHR déclenchés lors de la saisie.
  3. **Cohérence multi-onglets** : bascule éventuelle (`select_page`) pour confirmer que les paramètres saisis concordent rigoureusement avec les onglets connexes (ex: ID d'étude, taux horaire, redirection d'URL).
- L'agent browser remonte son compte-rendu d'audit à l'agent principal via `send_message` :
  * Si validé : pour chaque action confirmée conforme dans le DOM, l'agent principal met à jour l'artéfact en supprimant immédiatement l'action validée (**règle de l'élagage au fil de l'eau**). L'artéfact ne conserve que le reliquat et devient vide (ou affiche un message de clôture 100% propre) dès validation intégrale du lot. L'agent principal prépare ensuite le lot suivant de 5 actions (retour au Temps 1).
  * Si un oubli ou une anomalie est détecté : l'action concernée reste consignée dans l'artéfact, et l'agent principal le signale immédiatement avec bienveillance pour correction ciblée.

---

## 5. Inventaire, Matrice d'Usage & Directives Doctrinales

### 5.1 Matrice d'Usage des Outils `chrome_devtools`

| Outil | Description & Rôle | Statut & Directives |
| :--- | :--- | :--- |
| `list_pages` | Cartographie tous les onglets ouverts (IDs, URLs, titres). | **Obligatoire au démarrage** pour cibler l'onglet de travail existant d'Henri et cartographier les onglets connexes sans ouvrir de doublons. |
| `select_page` | Bascule le focus d'inspection sur un onglet précis. | **Autorisé** pour cibler la page active d'Henri et auditer les onglets liés lors de l'exploration multi-sources. |
| `new_page` | Ouvre un nouvel onglet avec l'URL cible. | **Autorisé** uniquement si la page demandée n'est pas déjà ouverte dans un onglet existant. |
| `close_page` | Ferme un onglet spécifique. | **Strictement restreint** aux onglets temporaires créés par l'agent. **INTERDIT** de fermer les onglets d'Henri. |
| `navigate_page` | Charge une URL dans l'onglet actif. | **Autorisé** sur demande explicite de navigation. |
| `evaluate_script` | Exécute du JavaScript dans la page. | **AUTORISÉ EN LECTURE SEULE** : extraction du DOM, vérification d'état, inspection de valeurs, lecture console. **STRICTEMENT INTERDIT** pour modifier le DOM ou injecter des valeurs. |
| `take_screenshot` | Capture une image de la page ou d'un élément. | **Autorisé** pour contrôle visuel passif ou aide au repérage. |
| `list_network_requests` | Inspecte les requêtes XHR/Fetch et logs réseau. | **Autorisé** pour diagnostic technique (chargements asynchrones, erreurs HTTP). |
| `click` | Simule un clic sur un élément. | **Exploration passive uniquement** (déplier un menu, ouvrir un onglet de navigation). **INTERDIT** pour soumettre un formulaire ou valider définitivement. |
| `fill` | Remplit la valeur d'un champ (`input`, `textarea`). | **STRICTEMENT INTERDIT** : la saisie est réservée à Henri manuellement. |
| `type_text` | Simule la frappe clavier. | **STRICTEMENT INTERDIT** : la frappe est réservée à Henri manuellement. |

### 5.2 Directives Doctrinales : Règle de l'Élagage au Fil de l'Eau (Pruning & Clean Artifact)
> [!IMPORTANT]
> **Règle Doctrinale de l'Élagage au Fil de l'Eau (Pruning & Clean Artifact)** :
> - **Suppression progressive immédiate** : Dès qu'une action d'un lot est appliquée par l'utilisateur et certifiée conforme par l'audit DOM de l'agent browser, l'action validée **DOIT ÊTRE SUPPRIMÉE** de l'artéfact de lot.
> - **File d'attente résiduelle exclusive** : L'artéfact ne contient en permanence **QUE les actions restant réellement à faire**.
> - **Artéfact vide en fin de lot** : À la fin du lot, lorsque toutes les actions sont validées, l'artéfact devient vide (ou affiche un simple message de clôture 100% propre).

---

## 6. Règles de Sécurité, Recherche Documentaire & Bonnes Pratiques

### 6.1 Délégation Systématique de la Recherche Documentaire
- L'agent browser est spécialisé dans l'inspection Chrome. Il n'a pas accès et ne doit jamais chercher dans les fichiers locaux ou les notes du coffre Obsidian.
- **Délégation à l'Agent Principal** : Dès qu'une valeur de fond manque (détail d'un projet, numéro d'éthique, affiliations, formulations méthodologiques), l'agent principal orchestre cette recherche documentaire via des sous-agents dédiés (`self` ou `research`) dans le coffre Obsidian ou la mémoire AIVC, sans déranger le sous-agent browser.

### 6.2 Préservation de l'Espace de Travail d'Henri
- Ne jamais fermer les onglets préexistants ouverts par Henri.
- Ne jamais effacer le stockage local, les cookies ou les sessions de navigation.
- Ne pas divulguer de mots de passe, tokens ou informations confidentielles dans les synthèses de chat.

### 6.3 Sanctuarisation Doctrinale
- `GEMINI.md` demeure la source canonique suprême et reste intact.
- En cas de contradiction sur la manipulation Chrome, les directives d'observation passive, de batching de 5 actions et d'élagage au fil de l'eau (pruning) de ce présent skill priment rigoureusement.
