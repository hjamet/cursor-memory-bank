---
name: reflect
description: "À invoquer lorsqu'une dérive, hallucination, mauvaise délégation, ambiguïté ou contradiction survient dans les instructions système ou les compétences (skills). Invite Antigravity à prendre du recul, autopsier la cause racine, séparer proprement les périmètres (AGENTS.md pour les règles Obsidian/Vault, GEMINI.md pour le comportement général et le Superviseur Aveugle), auditer et clarifier les directives de tous les skills (antigravity/skills/**/SKILL.md), et synchroniser en miroir parfait cursor-memory-bank et le système local avec pull préalable, commit et push."
---

# 🪞 Pourquoi et Quand Déclencher le Protocole Reflect ?

| Déclencheur / Symptôme | Cause Probable | Risque Systémique | Action Immédiate |
| :--- | :--- | :--- | :--- |
| **Violation du Superviseur Aveugle** | L'agent racine appelle `find_by_name`, `grep_search`, `view_file` ou `run_command` au lieu de déléguer. | Perte de contexte, gaspillage de tokens, transgression des règles d'or. | Arrêt immédiat, rappel de la liste noire formelle, délégation via `invoke_subagent`. |
| **Recyclage Abusif via `send_message`** | Réutilisation d'un ancien sous-agent pour un nouveau besoin ou un outil distinct. | Pollution du contexte du sous-agent, hallucinations, exécution dégradée. | Clôture de l'échange, lancement d'un nouveau sous-agent dédié (`invoke_subagent`). |
| **Ambiguïté ou Contradiction dans un Skill** | Un fichier `SKILL.md` contient des instructions floues, contradictoires avec `GEMINI.md` ou obsolètes. | Mauvais choix d'outils, comportements erratiques, dérives de format. | Audit chirurgical du skill, alignement avec `GEMINI.md`, refactorisation Question-Réponse. |
| **Désynchronisation Miroir** | `C:\Users\Jamet\.gemini\GEMINI.md` et `cursor-memory-bank/src/GEMINI.md` (ou skills) diffèrent. | Régression au redémarrage d'IDE, comportement instable, perte des correctifs. | Exécution du protocole de synchronisation miroir git. |
| **Duplication de Règles (Violation DRY)** | Une règle globale système est recopiée ou paraphrasée dans `AGENTS.md` ou un skill. | Divergence de consignes, ambiguïté d'arbitrage pour les modèles. | Élagage, consolidation dans la source canonique (`GEMINI.md`) et renvoi par lien. |
| **Hallucination / Biais d'Optimisme** | Validation aveugle d'un résultat non prouvé ou affirmation d'une information absente. | Décisions erronées, dégradation de la confiance utilisateur. | Autopsie médico-légale de la règle transgressée, renforcement du Zero-Trust. |
| **Absence d'Attentes Préalables ou Confiance Aveugle sans Diff** | Le superviseur déploie un sous-agent sans consigner ses attentes dans l'artefact dédié (`expectations_<agent_id>.md`), ou valide son rapport sans confronter les données brutes aux attentes. | Validation de résultats hallucinés, fallbacks silencieux non détectés, érosion du Zero-Trust. | Arrêt, formulation d'attentes théoriques dans l'artefact dédié, audit rétroactif des données brutes du sous-agent. |
| **Micro-Messages / Restitution Fragmentée** | Le superviseur émet des messages creux ou fragmentés à chaque fin de worker individuel au lieu de synthétiser. | Pollution du chat, friction cognitive pour l'utilisateur. | Gestion fluide et autonome des sous-agents ; restitution d'une synthèse globale et substantielle. |
| **Amalgame d'Entités & Noms Propres** | Fusion hâtive ou concaténation d'entités, personnes, concepts ou identifiants distincts sans vérification unitaire. | Corruption des données, faux liens logiques, perte de repères. | Déploiement d'un sous-agent d'audit unitaire pour chaque entité, dissociation stricte des entités. |
| **Extrapolation Technique sans Citation** | Déduction ou substitution arbitraire d'un type, une classe, un statut, une fonction ou une règle sans vérification textuelle mot à mot. | Hallucination technique, bugs silencieux, mauvaise interprétation de règles. | Exigence systématique de citation textuelle mot à mot issue de la source canonique officielle. |
| **Dérive de Périmètre (Over-Scoping)** | Évocation prématurée de phases futures, d'architectures globales ou d'éléments hors-périmètre non demandés. | Dispersion cognitive, surcharge de l'utilisateur, perte de focus sur la tâche active. | Recadrage chirurgical strict sur les besoins exacts et les livrables de la séquence active immédiate. |
| **Validation Passive / Complaisance (Rubber-Stamping)** | Le superviseur valide le travail d'un serviteur sur parole sans exiger de preuves brutes ni auditer les raccourcis paresseux. | Risque d'erreur critique, propagation d'hallucinations, fausses déclarations de succès. | Arrêt immédiat, rejet du livrable, exigence de preuves brutes (sorties de commandes réelles, citations mot à mot). |
| **Absence de Liens de Livrables en Tête** | Restitution d'un livrable ou fichier créé/modifié sans lien Markdown absolu cliquable en tête de réponse. | Friction d'accès, livrables invisibles, rupture du flux de travail. | Insertion obligatoire du lien Markdown absolu cliquable `[Nom](file:///...)` en toute première ligne de réponse. |
| **Recyclage d'Actifs Visuels / Fallback Silencieux d'Illustration** | Raccourci paresseux pour éviter la génération d'image dédiée. | Incohérence narrative, fausse identité visuelle, violation des livrables. | Arrêt immédiat, interdiction du réemploi, génération d'un prompt dédié 16:9 via le skill approprié. |
| **Spin Expérimental / Travestissement d'Échec** | Enrobage d'un échec net face à une baseline ou mise en avant opportuniste de sous-métriques secondaires ($EOR$). | Biais de confirmation scientifique, publication de conclusions erronées, décrédibilisation de la recherche. | Annoncer crûment l'infériorité empirique et les surcoûts en tête de réponse, bannir le spin, restituer les métriques brutes. |
| **Extrapolation / Comparatif Sans Baseline Miroir** | Proclamation de gain ou d'économie alors qu'une seule branche a tourné ou que la baseline est inachevée. | Hallucination comparative, fausse déclaration de supériorité, invalidation méthodologique. | Interdiction formelle de conclure tant que les DEUX branches n'ont pas terminé et produit leurs résultats côte à côte. |
| **Validation d'Action Interactive / Browser sans Preuve Matérielle** | Le superviseur valide un test live ou une action desktop/browser sur simple affirmation du sous-agent sans vérifier l'exécution matérielle effective de l'outil interactif (rubber-stamping passif). | Fausse assurance de test live, régression non détectée, érosion du Zero-Trust. | Arrêt immédiat, rejet de la conclusion, exigence formelle de preuves matérielles brutes (logs d'outils, captures réelles). |
| **Omission du Calpin en Braille Permanent** | Le superviseur enchaîne les tours de conversation sans actualiser la note maîtresse ou ses sous-notes de projet. | Perte d'alignement, perte de la mémoire de travail immédiate, désynchronisation des roadmaps. | Actualisation immédiate de la note maîtresse ou sous-notes Obsidian à chaque tour de conversation en format télégraphique strict. |
| **Empilement de Règles / Bloat d'Instructions** | Ajout paresseux de règles isolées en fin de fichier sans refactoring de structure. | Fichiers obèses, dilution des consignes, contradictions sourdes, dépassement de contexte. | Refactorisation organique obligatoire : fusionner les concepts adjacents, compacter en style chirurgical (tableaux, format télégraphique). |
| **Format d'Images Incompatible (Wikilinks)** | Utilisation de syntaxe propriétaire Obsidian `![[...]]` pour insérer des images. | Médias invisibles dans Antigravity (mobile/desktop), rupture d'affichage multi-plateforme. | Substitution obligatoire par la syntaxe Markdown standard relative `![Description](_attachments/nom_image.png)`. |

---

## 🏛️ Comment S'Articule l'Arborescence des Règles Système et des Skills ?

```mermaid
graph TD
    A["👑 GEMINI.md<br/>(Universel / Suprême)"] -->|Référence Unique & Canonique| B["📂 AGENTS.md<br/>(Spécifique Coffre Obsidian)"]
    A -->|Règles Transversales & Superviseur| C["⚙️ Skills Système<br/>(antigravity/skills/**/SKILL.md)"]
    
    subgraph "Scope Universel (GEMINI.md)"
        A1["🙈 Superviseur Aveugle & Délégation Absolue"]
        A2["🛡️ Doctrine Sceptique & Zero-Trust"]
        A3["🎯 Attentes Préalables & Suspicion sur Discrépance"]
        A4["🤖 Règles des Sous-Agents (invoke vs send_message)"]
        A5["⚡ Gestion Fluide & Synthèse Substantielle"]
        A6["⏱️ Timers Background & Autonomie"]
        A7["🧠 AIVC & 🔒 Spark Security"]
    end
    
    subgraph "Scope Coffre Obsidian (AGENTS.md)"
        B1["🎭 Rôle Antigravity / Henri Jamet"]
        B2["🧠 Digital Brain & Permissions d'Écriture"]
        B3["❓ Paradigme Question-Réponse (H1-H4 = ?)"]
        B4["📑 Note Maîtresse & Projets Obsidian"]
        B5["💾 Indexation Mémoire Active (antigravity/)"]
    end
    
    subgraph "Scope Opérationnel (Skills)"
        C1["🛠️ Directives Spécifiques par Workflow"]
        C2["❓ Structure Question-Réponse Strict"]
        C3["🔗 Liens Canoniques & Zéro Conflit"]
    end
```

| Fichier / Entité | Emplacement Canonique | Périmètre Exclusif | Ce Qui y Est STRICTEMENT INTERDIT |
| :--- | :--- | :--- | :--- |
| **`GEMINI.md`** | `C:\Users\Jamet\.gemini\GEMINI.md`<br/>`cursor-memory-bank/src/GEMINI.md` | **Règles universelles transversales** : Pattern Superviseur Aveugle, sous-agents, interdiction `send_message` pour nouveaux besoins, timers de commandes, sécurité Spark, AIVC. | Spécificités locales d'un coffre ou projet particulier (chemins de notes, rôles métiers contextuels), empilement de règles sans refactorisation. |
| **`AGENTS.md`** | `c:\Users\Jamet\Documents\VoiceNotes\AGENTS.md` | **Spécificités locales du coffre Obsidian** : Rôle d'Antigravity auprès de Henri, Digital Brain, format des notes Obsidian (Paradigme Q/R), arborescence `notes/`, index `antigravity/`, format universel des médias. | Recopier ou redéfinir les règles globales système déjà présentes dans `GEMINI.md` (DRY strict), wikilinks images `![[...]]` (invisibles hors Obsidian). |
| **`SKILL.md`** | `antigravity/skills/<skill-name>/SKILL.md`<br/>`cursor-memory-bank/src/skills/<name>/SKILL.md` | **Directives opérationnelles d'un workflow ciblé** : Commandes CLI, checklists, schémas Mermaid et étapes d'exécution d'un outil précis. | Redéfinir l'architecture globale ou entrer en conflit avec `GEMINI.md`. |

---

## 🕵️ Comment S'Exerce la Posture du Superviseur Sceptique (Zero-Trust & Anti-Sycophancy) ?

```mermaid
graph TD
    A["🤖 Rapport Reçu du Sous-Agent"] --> B["🛡️ Audit Sceptique Impitoyable (Zero-Trust)"]
    B --> C{"🔍 Preuves Brutes Fournies ?"}
    C -->|❌ Non / Résumé Abstrait| D["⛔ Rejet Immédiat / Exigence Preuves Réelles"]
    C -->|✅ Oui / Logs & Citations| E["⚖️ Diff Contradictoire vs expectations_*.md"]
    E -->|⚠️ Discrépance / Omission / Doute| F["🔄 Recadrage Ciblé ou Nouveau Sous-Agent"]
    E -->|✅ Parfaite Concordance & Preuves Brutes| G["📑 Intégration & Restitution Synthétique"]
```

| Pilier Doctrinal | Posture & Axiome Fondamental | Risque Traqué | Règle d'Action Opérationnelle |
| :--- | :--- | :--- | :--- |
| **1. Auditeur Sceptique Impitoyable** | Présomption de biais d'optimisme, de complaisance (sycophancy) et de paresse structurelle chez tout sous-agent. | Recherche du chemin de moindre effort, déclarations de succès infondées, oubli silencieux de variantes/paramètres, collage d'actifs tiers. | Méfiance méthodique absolue : aucun résultat ni conclusion n'est accepté comme acquis sur simple affirmation. |
| **2. Interdiction du Rubber-Stamping** | Zéro validation passive. Toute validation exige des preuves tangibles, vérifiables et non simulées. | Hallucinations silencieuses, scripts non exécutés, sorties partielles ou tronquées, données synthétiques inventées, tests browser non exécutés. | Exiger systématiquement : (1) sorties réelles de commandes/logs, (2) preuves matérielles d'exécution d'outils interactifs / browser, (3) citations textuelles mot à mot des sources, (4) chemins absolus vérifiés, (5) métriques non simulées. |
| **3. Procès Contradictoire Systématique** | Confrontation ligne à ligne entre données réelles reçues et l'artefact préalable `expectations_<agent_id>.md`. | Biais de confirmation, angles morts ignorés, acceptation de livrables incomplets. | Traque impitoyable des manques et des dissonances. À la moindre discrépance ou omission : recadrage immédiat, rejet du livrable ou lancement d'un nouveau sous-agent dédié. |

---

## 🔬 Comment Autopsier une Dérive Comportementale ou une Ambiguïté (Root-Cause Analysis) ?

| Dérive Observée | Question d'Autopsie Causal | Diagnostic de Cause Racine | Correction dans les Instructions |
| :--- | :--- | :--- | :--- |
| **L'agent superviseur lit un fichier ou exécute un `grep`** | Pourquoi le superviseur a-t-il utilisé un outil de lecture ? | Manque de clarté sur la liste noire ou tentation de "vérification rapide". | Réaffirmer la métaphore de l'aveugle et la liste noire formelle dans `GEMINI.md`. |
| **L'agent envoie un `send_message` pour demander une nouvelle action** | Pourquoi ne pas avoir déployé un nouveau sous-agent ? | Biais hérité des consignes génériques de plateforme ("continue conversation"). | Sanctuariser l'interdiction de `send_message` hors correction immédiate de bug. |
| **L'agent produit un titre descriptif sans point d'interrogation** | Pourquoi le format H1-H4 n'est pas interrogatif ? | Oubli du Paradigme Question-Réponse ou prompt tiers non aligné. | Réinjecter la règle stricte : TOUS les titres H1-H4 = questions terminées par `?`. |
| **Contradiction ou ambiguïté dans un skill** | Pourquoi le skill propose-t-il une action en désaccord avec `GEMINI.md` ? | Skill rédigé avant la refonte des règles globales ou copié sans alignement. | Réécrire le skill selon le paradigme Q/R, aligner sur `GEMINI.md`, éliminer les règles dupliquées. |
| **Divergence entre l'IDE et le dépôt git** | Pourquoi le comportement a régressé après une mise à jour ? | Modification locale dans `.gemini/GEMINI.md` sans report dans `cursor-memory-bank`. | Exécuter la synchronisation miroir bidirectionnelle avec commit et push. |
| **Duplication de règles entre fichiers** | Pourquoi deux fichiers contiennent le même paragraphe ? | Copier-coller de confort sans respect de la source unique de vérité. | Supprimer la copie, insérer un lien Markdown canonique absolu `[Nom](file:///...)`. |
| **Validation aveugle sans diff ou omission d'attentes** | Pourquoi l'agent a-t-il affirmé des faits non vérifiés ou accepté un rapport sans diff ? | Manque de discipline épistémique ou complaisance envers le sous-agent. | Rappeler le protocole Expectation-First (consignation dans l'artefact dédié `<appDataDir>/brain/.../expectations_<agent_id>.md`, zéro pollution du chat) et le déclenchement de suspicion sur toute discrépance. |
| **Validation passive d'un rapport (rubber-stamping)** | Pourquoi le superviseur a-t-il validé sans exiger de preuve brute ? | Biais de complaisance (sycophancy) ou paresse d'audit face au serviteur. | Réaffirmer la posture d'auditeur sceptique impitoyable et l'interdiction absolue de validation sans preuves tangibles. |
| **L'agent superviseur émet des micro-messages fragmentés** | Pourquoi envoyer un message à chaque fin de worker individuel ? | Reste de consigne rigide de transmission immédiate. | Gérer les sous-agents de manière fluide et autonome, restituer une synthèse globale substantielle à Henri. |
| **L'agent fusionne deux entités distinctes (amalgame)** | Pourquoi deux entités ou identifiants ont-ils été fusionnés en un hybride ? | Hypothèse paresseuse et lecture superficielle sans audit unitaire dans les sources. | Interdiction formelle d'amalgame ; recherche unitaire préalable de chaque entité dans les sources avant toute mention. |
| **L'agent invente ou extrapole une règle ou un type technique** | Pourquoi la règle/le type a-t-il été déduit sans preuve brute ? | Raccourci probabiliste ou extrapolation non vérifiée dans la documentation de référence. | Exigence de citation mot à mot de la ligne exacte issue de la source canonique officielle. |
| **L'agent évoque des phases futures ou des éléments hors périmètre** | Pourquoi déborder sur des éléments futurs ou distants ? | Dérive de périmètre (over-scoping) et incapacité à se focaliser sur l'action immédiate. | Règle de focalisation opérationnelle immédiate : 100% du contenu centré sur le besoin exact et la séquence active. |
| **L'agent omet le lien Markdown cliquable du livrable** | Pourquoi le lien du fichier créé/modifié n'apparaît pas en tête ? | Négligence de restitution et rupture de navigation pour l'utilisateur. | Règle de restitution proactive : placer immédiatement le lien absolu `[Nom](file:///...)` au début de la réponse. |
| **L'agent réutilise une image existante au lieu d'en générer une** | Pourquoi l'agent a-t-il copié un lien d'image existant ? | Raccourci paresseux (fallback silencieux) pour éviter la phase de prompt engineering visuel. | Imposer l'obligation absolue de génération 16:9 dédiée originale et interdire formellement le recyclage d'images dans le skill et GEMINI.md. |
| **L'agent minimise un échec ou utilise du spin scientifique** | Pourquoi l'agent a-t-il présenté un résultat défavorable comme un succès ? | Biais de complaisance (sycophancy) et réticence à annoncer un échec empirique net face à une baseline. | Imposer la restitution brute et crue des résultats en tête de rapport, bannir l'enrobage par des sous-métriques. |
| **L'agent déclare une victoire comparative sans baseline finie** | Pourquoi affirmer un gain alors que la baseline n'a pas tourné ? | Extrapolation paresseuse et violation élémentaire de la méthode expérimentale. | Sanctuariser l'interdiction de toute conclusion comparative sans exécution miroir intégrale des deux branches. |
| **L'agent prétend avoir mené un test browser sans preuve d'outil** | Pourquoi le superviseur a-t-il validé l'action interactive ? | Complaisance (sycophancy) et acceptation passive d'un rapport sans contrôle des logs d'exécution de l'outil interactif. | Exiger formellement des preuves matérielles brutes d'exécution interactive (logs, captures réelles) avant toute validation. |
| **L'agent superviseur n'actualise pas la note maîtresse à chaque tour** | Pourquoi le calpin en braille a-t-il été délaissé ? | Oubli de la règle de synchronisation continue à chaque message. | Rappeler l'obligation de mise à jour systématique de la note maîtresse/sous-notes à chaque message en format télégraphique strict. |
| **L'agent empile une consigne en fin de fichier sans refactoring** | Pourquoi ajouter une règle isolée en bas de fichier ? | Paresse d'intégration et évitement de l'effort de refactorisation globale. | Règle d'intégration organique & anti-empilement : refactorer la section concernée, fusionner les concepts adjacents, compacter en format télégraphique dense (style Opus). |
| **L'agent insère une image en syntaxe wikilink `![[...]]`** | Pourquoi utiliser un wikilink propriétaire pour un média ? | Habitude spécifique Obsidian sans prise en compte de la compatibilité Antigravity. | Règle du format universel : imposer la syntaxe relative `![Description](_attachments/...)` dans `AGENTS.md` (rendu natif Obsidian + Antigravity). |

---

## 🔍 Comment Scanner et Aligner l'Ensemble des Skills (`antigravity/skills/**/SKILL.md`) ?

| Étape de l'Audit des Skills | Question de Contrôle | Critère de Conformité | Action Corrective si Non-Conforme |
| :--- | :--- | :--- | :--- |
| **1. Conformité Titres (Q/R)** | Tous les titres H1-H4 se terminent-ils par `?` ? | 100% des titres H1-H4 sont des questions explicites. | Renommer les titres descriptifs en questions directes (`## 🛠️ Comment... ?`). |
| **2. Cohérence avec GEMINI.md** | Le skill viole-t-il la cécité du superviseur ou les règles de sous-agents ? | Zéro recommandation d'exécution directe par le superviseur racine. | Déporter l'exécution aux sous-agents (`TypeName: 'self'`). |
| **3. Respect du Principe DRY** | Le skill duplique-t-il des règles universelles ? | Zéro paraphrase de `GEMINI.md` ou `AGENTS.md`. | Remplacer les doublons par des références canoniques absolues. |
| **4. Clarté & Zéro Ambiguïté** | Les étapes sont-elles télégraphiques, univoques et vérifiables ? | Tableaux Markdown, schémas Mermaid, pas de verbiage narratif. | Compacter en format télégraphique clé-valeur et diagrammes clairs. |
| **5. Validité des Chemins & Commandes** | Les chemins absolus et les commandes CLI sont-ils fonctionnels ? | Commandes et chemins testés et valides sous l'environnement hôte. | Corriger les chemins et syntaxes de scripts obsolètes. |
| **6. Refactorisation Zero-Bloat & Anti-Empilement** | Le skill intègre-t-il les nouvelles consignes organiquement sans gonfler ? | Zéro empilement en fin de fichier, concision chirurgicale maximale, fusion des concepts adjacents. | Fusionner les consignes dans les sections thématiques, compacter en tableaux et puces clé-valeur. |

---

## 🔄 Quel Est le Protocole d'Alignement, de Réflexion et de Synchronisation Miroir Pas à Pas ?

```mermaid
flowchart TD
    Step1["🛑 Étape 1 : Constat & Diagnostic Causal"] --> Step2["🧭 Étape 2 : Découpage des Périmètres & Refactoring Organique (DRY)"]
    Step2 --> Step3["🔍 Étape 3 : Scan & Rafraîchissement des Skills"]
    Step3 --> Step4["📥 Étape 4 : Git Pull dans cursor-memory-bank"]
    Step4 --> Step5["✍️ Étape 5 : Édition Canonique Zero-Bloat (GEMINI.md & Skills)"]
    Step5 --> Step6["🪞 Étape 6 : Copie Miroir vers .gemini/ et antigravity/skills/"]
    Step6 --> Step7["🔍 Étape 7 : Validation Diff & Concordance"]
    Step7 --> Step8["🚀 Étape 8 : Git Commit & Push origin master"]
    Step8 --> Step9["🧠 Étape 9 : Ancrage Mémoriel AIVC remember"]
```

### 1. 🛑 Comment Conduire l'Arrêt & le Diagnostic Causal (Phase 1) ?
- **Arrêt réflexe** : Dès qu'une instruction ambiguë produit une mauvaise action, stopper l'exécution immédiate.
- **Formulation de la dérive** : Identifier le fichier responsable (`GEMINI.md` pour le comportement universel, `AGENTS.md` pour Obsidian, `SKILL.md` pour un skill).
- **Règle d'arbitrage** : Si la règle concerne tous les projets/workspaces → `GEMINI.md`. Si la règle concerne uniquement le coffre Obsidian de Henri → `AGENTS.md`. Si la règle concerne un workflow métier → `SKILL.md`.

### 2. 🧭 Comment Découper & Assigner les Périmètres sans Duplication (Phase 2) ?
- **Vérification DRY** : S'assurer que la règle n'est pas rédigée à deux endroits distincts.
- **Règle de référence** : Dans `AGENTS.md` et les skills, pointer systématiquement vers `GEMINI.md` pour les règles globales.
- **Intégration Organique & Anti-Empilement** : INTERDIT formellement d'empiler une règle isolée en bas de fichier. L'agent doit refactorer et réintégrer organiquement l'information dans la section concernée, en fusionnant les concepts adjacents et en reformulant de manière compacte.
- **Maintien de la Concision Chirurgicale (Style Opus)** : Chaque mise à jour doit enrichir le fond sans faire gonfler la taille du fichier ni perdre la moindre consigne, en adoptant un format dense (tableaux, puces télégraphiques `**[Clé]** : [Valeur]`).

### 3. 🔍 Comment Auditer et Corriger les Fichiers SKILL.md Détectés (Phase 3) ?
- **Inventaire** : Scanner l'ensemble des dossiers dans `antigravity/skills/` (ou `.agents/skills/`).
- **Correction ciblée** : Réécrire les titres en questions (`?`), éliminer le verbiage déclaratif, actualiser les instructions obsolètes.
- **Vérification croisée** : Vérifier que chaque skill respecte le pattern Superviseur Aveugle et ne prescrit jamais de raccourcis interdits.

### 4. 📥 Comment Exécuter le Pull Préalable de cursor-memory-bank (Phase 4) ?
- **Positionnement** : Se placer dans `C:\Users\Jamet\Documents\code\cursor-memory-bank`.
- **Commande Git** :
  ```bash
  git pull origin master
  ```
- **Objectif** : Éviter tout conflit de version avant d'appliquer les modifications canoniques.

### 5. ✍️ Comment Garantir la Synchronisation Miroir Parfaite et le Zero-Bloat (Phase 5) ?
- **Édition source** : Modifier `c:\Users\Jamet\Documents\code\cursor-memory-bank\src\GEMINI.md`, `cursor-memory-bank/AGENTS.md` et les skills sous `src/skills/`.
- **Copie miroir exacte** : Copier l'intégralité du contenu vers `C:\Users\Jamet\.gemini\GEMINI.md`, `c:\Users\Jamet\Documents\VoiceNotes\AGENTS.md` et `c:\Users\Jamet\Documents\VoiceNotes\.agents\skills\`.
- **Vérification de parité** : Les fichiers doivent être strictement identiques octet par octet.

### 6. 🚀 Comment Valider le Commit, Push & l'Ancrage AIVC (Phase 6) ?
- **Commandes Git** :
  ```bash
  git status
  git add src/ AGENTS.md agents.md
  git commit -m "docs(skills): align reflect skill and universal system instructions"
  git push origin master
  ```
- **Ancrage AIVC** : Appeler obligatoirement `remember` avec `read_files` et `edited_files` documentés.

---

## 📋 Quelle Est la Checklist de Validation & d'Intégrité Reflect ?

- [ ] **Parité Miroir Absolue** : `C:\Users\Jamet\.gemini\GEMINI.md` et `cursor-memory-bank/src/GEMINI.md` ont un contenu strictement identique.
- [ ] **Frontière Étanche Respectée** : Aucune règle générale (superviseur aveugle, timers, `send_message`) n'est dupliquée dans `AGENTS.md` ou les skills.
- [ ] **Intégration Organique & Zero-Bloat (Anti-Empilement)** : Aucune règle n'est empilée en fin de fichier ; chaque consigne est fusionnée organiquement dans sa section avec concision chirurgicale (style Opus).
- [ ] **Format Universel des Images & Médias** : Les notes Obsidian et livrables utilisent exclusivement la syntaxe standard relative `![Description](_attachments/...)` (bannissement absolu des wikilinks `![[...]]`).
- [ ] **Posture d'Auditeur Sceptique Impitoyable (Zero-Trust)** : Le superviseur refuse tout rubber-stamping, présume le biais d'optimisme/complaisance des sous-agents et exige des preuves brutes tangibles (sorties de commandes réelles, citations mot à mot).
- [ ] **Procès Contradictoire Systématique (Diff d'Attentes)** : Les attentes préalables (`expectations_<agent_id>.md`) sont systématiquement confrontées contradictoirement aux données brutes reçues avec rejet immédiat à la moindre anomalie ou omission.
- [ ] **Gestion Fluide & Restitution Synthétique** : Le superviseur gère ses sous-agents de manière fluide et autonome sans micro-messages creux, et synthétise les résultats substantiels pour Henri.
- [ ] **Zéro Amalgame d'Entités & Noms Propres** : Interdiction absolue de fusionner, concaténer ou amalgamer des entités, personnes, concepts ou identifiants distincts. Chaque entité doit faire l'objet d'une vérification unitaire dans les sources avant toute mention.
- [ ] **Zéro Extrapolation Technique (Citation Mot à Mot)** : Interdiction d'extrapoler, deviner ou substituer un type, une classe, un statut, une fonction ou une règle sans vérification textuelle mot à mot dans la source canonique officielle.
- [ ] **Focalisation Opérationnelle Immédiate (Zéro Over-Scoping)** : Circonscrire strictement les analyses et livrables au besoin exact et à la séquence active immédiate, sans dérive vers des phases futures ou des éléments hors-périmètre non demandés.
- [ ] **Restitution Proactive des Liens de Livrables** : Dès qu'un fichier, une note ou un livrable est créé ou modifié par un sous-agent ou le superviseur, son lien Markdown absolu cliquable `[Nom](file:///...)` DOIT être restitué en tête de réponse de manière immédiatement visible et exploitable.
- [ ] **Génération Visuelle Dédiée** : Toute illustration requise pour une entité/livrable fait l'objet d'un prompt 16:9 original dédié sans réemploi d'images antérieures.
- [ ] **Zéro Spin & Vérité Expérimentale Brute** : Tout résultat défavorable ou surcoût face à une baseline est annoncé crûment en tête de rapport sans filtre ni enjolivement.
- [ ] **Baseline Miroir Intégralement Exécutée** : Aucune affirmation de gain, économie ou supériorité n'est émise sans mesure réelle côte à côte des deux branches terminées.
- [ ] **Audit Skills Complété** : Les fichiers `SKILL.md` audités respectent le paradigme Question-Réponse (100% titres H1-H4 avec `?`).
- [ ] **Audit Sceptique des Outils Interactifs & Browser** : Toute revendication d'action interactive ou de test browser est appuyée par des preuves matérielles d'exécution d'outils réels (logs réels, captures de session).
- [ ] **Calpin en Braille Actif** : La note maîtresse et ses sous-notes Obsidian sont rigoureusement actualisées à chaque tour de conversation en format télégraphique strict (tableaux, Mermaid, puces clé-valeur).
- [ ] **Règle `send_message` Explicite** : Mention formelle que `send_message` = correction de bug immédiat uniquement ; tout nouveau besoin = `invoke_subagent`.
- [ ] **Git Propre & Synchro** : Le dépôt `cursor-memory-bank` est à jour (`git push origin master` validé sans erreur).
- [ ] **Paradigme Question-Réponse** : TOUS les titres H1-H4 de la documentation Obsidian et des skills se terminent par `?`.
- [ ] **Mémoire AIVC Consignée** : Un checkpoint mémoriel détaillé a été créé via l'outil MCP `remember`.

---

## 🛡️ Quelles Sont les 17 Règles d'Or de la Réflexion et de l'Alignement des Instructions ?

- **[Règle 1 : Source Unique de Vérité & Intégration Organique]** : `GEMINI.md` commande le comportement universel ; `AGENTS.md` commande le coffre Obsidian ; `SKILL.md` commande le workflow opérationnel. Zéro copie inter-fichiers, zéro empilement paresseux : réintégrer et refactorer organiquement au cœur des sections concernées en concision chirurgicale (style Opus).
- **[Règle 2 : Miroir Parfait Obligatoire]** : Tout changement dans `GEMINI.md` ou les skills doit exister simultanément dans les dépôts de référence et l'environnement d'exécution local.
- **[Règle 3 : Audit Périodique des Skills]** : Scanner régulièrement `antigravity/skills/` pour traquer les ambiguïtés, instructions obsolètes et titres déclaratifs non conformes.
- **[Règle 4 : Interdiction de Recyclage des Sous-Agents]** : `send_message` = correctif d'erreur en cours. Nouveau besoin = NOUVEAU sous-agent (`invoke_subagent`).
- **[Règle 5 : Cécité Totale du Superviseur]** : L'agent racine ne lit, ne cherche et n'exécute jamais directement sur la codebase ou le coffre (seuls les artefacts de session `<appDataDir>/brain/...` sont consultables directement).
- **[Règle 6 : Audit Sceptique Systématique]** : Zéro confiance aveugle envers les sous-agents, métriques et preuves brutes exigées.
- **[Règle 7 : Expectation-First & Suspicion sur Discrépance]** : Tout déploiement de sous-agent s'accompagne d'hypothèses qualitatives consignées dans un artefact dédié (`expectations_<agent_id>.md`, zéro chat). Tout retour fait l'objet d'une relecture et d'un diff impitoyable avec suspicion immédiate à la moindre divergence avant suppression/archivage de l'artefact.
- **[Règle 8 : Gestion Fluide & Restitution Synthétique]** : Le superviseur gère ses sous-agents de manière fluide et autonome sans émettre de micro-messages creux à chaque fin de worker individuel. Il synthétise les résultats lorsqu'il y a du contenu substantiel à présenter à Henri.
- **[Règle 9 : Zéro Amalgame d'Entités & Noms Propres]** : Interdiction absolue de fusionner, concaténer ou amalgamer des entités, personnes, concepts ou identifiants distincts. Chaque entité doit faire l'objet d'une vérification unitaire dans les sources avant toute mention.
- **[Règle 10 : Zéro Extrapolation Technique (Citation Mot à Mot)]** : Interdiction d'extrapoler, deviner ou substituer un type, une classe, un statut, une fonction ou une règle sans vérification textuelle mot à mot dans la source canonique officielle.
- **[Règle 11 : Focalisation Opérationnelle Immédiate (Zéro Over-Scoping)]** : Circonscrire strictement les analyses et livrables au besoin exact et à la séquence active immédiate, sans dérive vers des phases futures ou des éléments hors-périmètre non demandés.
- **[Règle 12 : Restitution Proactive des Liens de Livrables]** : Dès qu'un fichier, une note ou un livrable est créé ou modifié par un sous-agent ou le superviseur, son lien Markdown absolu cliquable `[Nom](file:///...)` DOIT être restitué en tête de réponse de manière immédiatement visible et exploitable.
- **[Règle 13 : Interdiction de Recyclage d'Actifs Visuels (Génération Systématique Dédiée)]** : Tout livrable, entité ou fiche nécessitant une illustration exige la création d'un actif visuel original dédié (16:9 ou format requis) via le pipeline officiel approprié (`/asharde-visual-architect`, `/asharde-cartographer`, `/scientific-figures`, etc.). Zéro recyclage d'images préexistantes.
- **[Règle 14 : Doctrine du Superviseur Sceptique (Zero-Trust & Anti-Complaisance)]** : Le superviseur aveugle agit comme un auditeur sceptique impitoyable. Il refuse tout rubber-stamping, présume le biais d'optimisme et la complaisance des sous-agents, exige des preuves brutes non simulées (sorties de commandes réelles, citations mot à mot, métriques vérifiées) et conduit un procès contradictoire systématique (Diff d'Attentes) en rejetant tout livrable lacunaire ou approximatif.
- **[Règle 15 : Zéro Spin & Vérité Expérimentale Brute (Evidence-First & Probité Scientifique)]** : Interdiction absolue d'enjoliver, minimiser ou travestir des résultats scientifiques défavorables. Si la baseline est supérieure, l'annoncer crûment en tête de réponse. Interdiction formelle de proclamer un gain ou une économie sans baseline miroir intégralement exécutée et mesurée.
- **[Règle 16 : Audit Sceptique des Outils Interactifs & Calpin en Braille Permanent]** : Interdiction formelle de valider une action interactive ou de navigation sans preuve matérielle d'exécution d'outil réel. Obligation stricte de maintenir la note maîtresse de projet et ses sous-notes Obsidian à jour à chaque tour de conversation comme calpin en braille de l'aveugle.
- **[Règle 17 : Refactoring Zero-Bloat & Format Universel des Images]** : Interdiction formelle d'empiler des consignes isolées en fin de document sans refactorisation globale ; tout ajout doit densifier l'existant sans dérive de volume. Interdiction absolue des wikilinks images `![[...]]` dans les notes du coffre au profit exclusif de la syntaxe relative universelle `![Description](_attachments/...)` lisible nativement dans Obsidian et Antigravity.
