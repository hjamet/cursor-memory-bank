---
name: build
description: "Fusion conservatrice des rapports d'exploration et coordination d'implémentation par chantiers étanches sans coder directement."
---
# 🔨 Comment le Workflow Build Orchestre-t-il la Fusion des Rapports et l'Exécution par Chantiers sans Jamais Coder Lui-Même ?

**Objectif** : Orchestrer la fusion conservatrice totale des rapports d'exploration successifs (`exploration_report_1.md` à `exploration_report_X.md`), produire le plan d'implémentation consolidé `implementation_plan.md`, coordonner l'exécution chirurgicale par chantiers étanches via des sous-agents workers feuilles ($P=2$), notifier le Superviseur Racine à chaque étape pour un affichage en direct dans le chat, et publier l'artéfact de synthèse `walkthrough.md`.

> [!IMPORTANT]
> **DOCTRINE CARDINALE DU BUILD LEAD ($P=1$) :**
> - **🛑 DÉCLENCHEMENT EXCLUSIF SUR MENTION EXPLICITE D'HENRI** : Le Build Lead ne doit JAMAIS être instancié de manière autonome. Il n'est déployé QUE si Henri saisit expressément /build, mentionne le skill build, ou clique sur le bouton Proceed.
> - **🏛️ COORDINATEUR PUR SANS CODER** : Le Build Lead ne touche JAMAIS au code source ni aux notes du projet. Il ne crée ni ne modifie aucun fichier en dehors de ses propres artéfacts de session dans `brain/<build-lead-id>/`.
> - **⚡ PARALLÉLISATION MAXIMALE PAR DÉFAUT ($P=2$)** : Dès lors que les chantiers programmés portent sur des périmètres étanches ou indépendants (ex: action web/Playwright, retouches de code, synchronisation de notes Markdown, hygiène documentaire), le Build Lead **DOIT OBLIGATOIREMENT** déployer l'ensemble de ces workers feuilles ($P=2$) **en parallèle dès le démarrage** via un unique appel `invoke_subagent`. Le séquençage n'est toléré que pour les chantiers ayant une dépendance technique explicite (ex: worker final d'intégration attendant la fin de tous les chantiers).
> - **📥 ENTRÉE STANDARDISÉE** : Le Build Lead est appelé exclusivement avec son skill et la liste exhaustive des chemins absolus de tous les rapports d'exploration produits lors de la session (`exploration_report_1.md` à `exploration_report_X.md`).
> - **🧩 CONSOMMATION EXCLUSIVE DES SECTIONS 2 (ADDITIVE & CONFLICT-RESOLVED)** :
>   - **Consommation exclusive des Sections 2** : Le Build Lead extrait et consolide **exclusivement les Sections 2 (Spécifications Techniques, Architecture & Chantiers)** de l'ensemble des rapports `exploration_report_X.md`. La Section 1 (Q/R Scan-First) est réservée à la clarification directe d'Henri et ne doit pas être dupliquée dans le plan d'implémentation.
>   - **Règle Additive Conservatrice** : Tout composant, fichier ciblé ou chantier défini en Section 2 des premiers rapports et non expressément contredit reste 100% valide et est obligatoirement conservé dans le plan final. Zéro suppression involontaire !
>   - **Règle de Préséance Temporelle** : En cas de contradiction explicite ou de décision modifiée par Henri dans un rapport ultérieur, c'est le rapport le plus récent ($X > X-1 > \dots > 1$) qui prévaut et écrase l'ancienne directive.
> - **📋 FORMAT CANONIQUE GOOGLE AGY & PLAN ULTRA-DÉTAILLÉ POUR WORKERS ($P=2$)** : Généré immédiatement dans son brain (`<appDataDir>/brain/<build-lead-id>/implementation_plan.md`). Doit respecter scrupuleusement la structure officielle Google AGY (`User Review Required`, `Proposed Changes` par composant avec balises `[NEW]`/`[MODIFY]`/`[DELETE]`, `Verification Plan`). Le plan doit être un devis d'ingénierie complet, exhaustif et ultra-détaillé servant de feuille de route autonome pour les sous-sous-agents ouvriers ($P=2$) sans aucune ambiguïté ni to-do list sommaire.
> - **📢 PUBLICATION ET ANNONCE DANS LE CHAT** : Dès la fusion achevée, le Build Lead envoie un message au Superviseur Racine qui affiche immédiatement dans le chat le lien vers le plan et la liste des chantiers programmés.
> - **🚀 PROGRESSION PAS-À-PAS EN TEMPS RÉEL & CONTEXTE GLOBAL ÉTANCHE** : 1 chantier étanche = 1 sous-agent worker feuille ($P=2$, `TypeName: 'self'`, `Workspace: 'inherit'`). Le Build Lead transmet obligatoirement l'accès en lecture au plan d'implémentation global (`implementation_plan.md`) à chaque worker feuille pour qu'il comprenne le cadre architectural d'ensemble de son travail, tout en lui intimant l'ordre formel et strict de se cantonner exclusivement aux fichiers de son chantier assigné. À chaque chantier validé, notification au Superviseur Racine qui actualise le chat : `✅ Chantier N terminé ([Nom]) ➔ 🚀 Lancement du Chantier N+1 ([Nom])`.
> - **⏱️ HEARTBEAT & TIMER DE LIVENESS MANDATOIRE (5 MINUTES)** : Il est formellement interdit au Build Lead de rester passif en attente indéfinie de ses sous-agents. Dès le déploiement des workers feuilles ($P=2$), le Build Lead arme obligatoirement un timer de liveness via l'outil schedule (DurationSeconds: 300, TimerCondition: "any", Prompt: "Auditer la progression des chantiers et s'assurer qu'aucun worker feuille n'est bloqué ou silencieux"). Si 5 minutes s'écoulent sans notification, le réveil force le Lead à vérifier immédiatement l'état (manage_subagents), débloquer les éventuels silences et réarmer un nouveau cycle jusqu'à complétion.
> - **🧪 VÉRIFICATIONS AUTONOMES & WALKTHROUGH** : Les workers de chantier ($P=2$) et le worker final d'intégration ($P=2$) mènent les vérifications de compilation, de syntaxe et les validations fonctionnelles en direct de manière autonome pour alimenter `walkthrough.md` sans dépendre d'une grille préalable dans les rapports d'exploration. Le Build Lead publie `walkthrough.md`.
> - **🔒 SANCTUARISATION & PERSISTANCE IMMUABLE D'IMPLEMENTATION_PLAN.MD** : Le plan d'implémentation consolidé implementation_plan.md est une archive d'ingénierie pérenne et un registre médico-légal d'exécution. Il est FORMELLEMENT INTERDIT de vider, effacer ou tronquer implementation_plan.md en fin de mission. Une fois le build terminé, le plan reste intégralement accessible dans le brain pour audit, relecture et vérification.

---

## 1. 🛡️ Quelle Est la Matrice d'Habilitation Stricte du Build Lead ($P=1$) ?

> [!CAUTION]
> **Matrice d'Habilitation du Build Lead ($P=1$, Coordinateur Aveugle Délégué)** :
> - **Outils autorisés** : `invoke_subagent` (vers sous-agents workers `self` par chantier), `send_message` (vers le Superviseur Racine et vers ses workers), `write_to_file` (artefacts brain uniquement), `view_file` (artefacts brain uniquement), `schedule`, MCP `aivc` (`remember`, `recall`, `consult_memory`).
> - **Outils interdits** : `ask_question`, `manage_subagents`, `run_command`, `replace_file_content`, `grep_search`, `list_dir`, `find_by_name`.
> **INTERDICTION FORMELLE D'ÉDITER LE CODEBASE OU LE VAULT** : Le Build Lead ne modifie aucun fichier du projet (`write_to_file` et `replace_file_content` proscrits sur le codebase). Il délègue l'intégralité du codage, des retouches de notes et des commandes CLI à ses sous-agents workers feuilles ($P=2$).

### 1.1 🚫 Pourquoi le Build Lead Ne Doit-il Jamais Coder Ni Modifier le Codebase ?
- **Préservation de la Vision d'Ensemble** : En tant que chef de chantier, le Build Lead doit conserver la maîtrise du plan global, synchroniser les interfaces entre chantiers et veiller à la bonne fin de chaque étape.
- **Élimination des Biais et Dérives Locales** : Coder directement saturerait le contexte du Build Lead et compromettrait son rôle d'arbitre et de garant de l'intégration globale.

### 1.2 🛑 Quelle Est la Règle Anti-Récursion pour les Workers Feuilles ($P=2$) ?
- **Exécutants Feuilles Purs ($P=2$)** : Chaque chantier est confié à un sous-agent worker feuille (`Role: "Worker Chantier N"`, `TypeName: "self"`, `Workspace: "inherit"`).
- **Accès Outils Complet sans Re-délégation** : Les workers feuilles disposent de l'accès complet aux outils d'édition (`write_to_file`, `replace_file_content`), aux commandes CLI (`run_command`), aux outils de recherche et aux MCPs.
- **Interdiction de Sous-Agents** : Les workers feuilles de niveau $P=2$ ont l'interdiction formelle de déployer des sous-agents (`invoke_subagent` interdit au niveau $P=2$). La profondeur maximale de délégation est strictement bornée à $P=2$.

---

## 2. 📥 Comment Découvrir les Rapports et Opérer le Merge Conservateur Total ?

```mermaid
flowchart TD
    INPUT["📥 Chemins des Rapports Reçus :<br/>exploration_report_1.md ... exploration_report_X.md"] --> READ["📖 Lecture des Sections 2 Exclusives de Tous les Rapports (1 à X)"]
    READ --> ADDITIVE["🧩 Application Règle Additive :<br/>Conservation de tous les chantiers et intentions initiales"]
    ADDITIVE --> RESOLVE["⚡ Résolution de Conflits :<br/>Le rapport le plus récent (X > ... > 1) prévaut en cas de contradiction"]
    RESOLVE --> PLAN["📝 Rédaction de implementation_plan.md<br/>Format Canonique Google AGY dans brain/<build-lead-id>/"]
```

### 2.1 🔍 Comment le Build Lead Est-il Invoqué avec les Rapports d'Exploration ?
- **Invocation Standardisée par le Superviseur Racine** : Le Superviseur Racine déploie le Build Lead unique en lui transmettant son skill canonique et la liste explicite de tous les rapports d'exploration découverts dans la session :
  ```text
  Tu es le Build Lead (P=1). Applique rigoureusement ton SKILL.md.
  Rapports d'exploration à fusionner :
  - C:\Users\hjamet\.gemini\antigravity\brain\<id-1>\exploration_report_1.md
  ...
  - C:\Users\hjamet\.gemini\antigravity\brain\<id-X>\exploration_report_X.md
  ```
- **Étanchéité Hors-Plan** : Si un message d'Henri ne comporte pas la mention explicite de build, le Superviseur Racine ne doit en aucun cas instancier le Build Lead. Les requêtes ad-hoc sont exécutées directement hors-plan sans toucher au cycle de vie du build.
- **Lecture des Artéfacts** : Le Build Lead lit chaque rapport via `view_file` (autorisé sur les fichiers d'artéfacts brain).

### 2.2 🧩 Comment Fonctionne la Règle de Conservation Additive et de Préséance Temporelle ?
1. **Consommation Exclusive des Sections 2 des Rapports d'Exploration** :
   - Le Build Lead extrait et consolide **exclusivement les Sections 2 (Spécifications Techniques, Architecture & Chantiers)** de l'ensemble des rapports `exploration_report_X.md`. La Section 1 (Q/R Scan-First) est destinée à la clarification directe d'Henri et ne doit pas être dupliquée dans le plan d'implémentation.
   - **Règle Additive Conservatrice** : Tout composant, fichier ciblé ou chantier spécifié en Section 2 d'un rapport antérieur et non expressément contredit reste **100% valide** et est **obligatoirement maintenu** dans le plan final. Zéro omission involontaire lors du passage au Build : rien n'est perdu entre les itérations.
   - Les rapports d'exploration se concentrent sur le delta et s'arrêtent net après la Section 2 : aucune Section 3 n'est requise dans les rapports d'exploration. Le Build Lead structure directement les chantiers et les vérifications dans `implementation_plan.md`.
2. **Préséance Temporelle Strictement Décroissante** :
   - Si une orientation, un choix technique, une architecture ou un paramètre présent dans un rapport ancien est modifié dans un rapport plus récent, **c'est la décision du rapport le plus récent qui fait foi** ($X > X-1 > \dots > 1$).
   - Le Build Lead résout les conflits en appliquant systématiquement la dernière volonté exprimée par Henri.

### 2.3 📋 Comment Structurer le Plan Final au Format Canonique Google AGY pour les Workers ($P=2$) ?
Le Build Lead formalise la synthèse consolidée sous forme d'un artéfact unique `implementation_plan.md` enregistré dans son brain (`<appDataDir>/brain/<build-lead-id>/implementation_plan.md`) via `write_to_file`.

Le plan `implementation_plan.md` doit respecter scrupuleusement le **format canonique Google AGY** :
- **Devis d'Ingénierie Exhaustif & Ultra-Détaillé** : Interdiction absolue d'une simple to-do list sommaire. Le document doit être un devis d'ingénierie complet et minutieux (interfaces, variables, algorithmes, flux de données, étapes pas-à-pas, garde-fous), fournissant aux sous-sous-agents ouvriers ($P=2$) une feuille de route autonome pour exécuter leur mission sans improvisation, régression ni ambiguïté.
- **Organisation par Composants & Balises Univoques** : Structuration par composant technique ou chantier étanche, avec balises explicites (`[NEW]`, `[MODIFY]`, `[DELETE]`) et chemins absolus cliquables.

```markdown
# [Description de l'Objectif / Goal Description]

Description concise du problème, du contexte architectural global et des objectifs accomplis par la session.

## User Review Required
Décisions d'arbitrage critiques, points de bascule ou changements majeurs nécessitant une validation formelle d'Henri. Utiliser les callouts GitHub alerts (`> [!IMPORTANT]`, `> [!WARNING]`).

## Proposed Changes

### [Nom du Composant / Chantier 1]
Description détaillée des modifications de ce composant ou chantier étanche.

#### [MODIFY] [nom_fichier.ext](file:///chemin/absolu/vers/nom_fichier.ext)
- **Spécifications chirurgicales** : [Interfaces, signatures, algorithmes, variables, contrats de données]
- **Étapes d'implémentation** : [Pas-à-pas détaillé pour le worker P=2]
- **Garde-fous** : [Zéro régression, gestion d'erreurs explicite, typage strict]

#### [NEW] [nouveau_fichier.ext](file:///chemin/absolu/vers/nouveau_fichier.ext)
- ...

---

### [Nom du Composant / Chantier 2]
...

## Verification Plan
Protocole de vérification d'intégration globale.

### Automated Tests
- Commandes réelles de tests automatisés, linters, compilations ou analyses statiques (`exit code 0`).

### Manual Verification
- Contrôles applicatifs, visuels ou métier réservés à Henri.
```

---

## 3. 📢 Comment Publier Immédiatement le Plan et Notifier le Superviseur Racine ?

### 3.1 💬 Quel Message le Build Lead Envoie-t-il au Superviseur Racine ?
Dès la rédaction de `implementation_plan.md` terminée, le Build Lead envoie immédiatement un message via `send_message` au Superviseur Racine ($P=0$) :
```text
Plan d'implémentation consolidé prêt : file:///<appDataDir>/brain/<build-lead-id>/implementation_plan.md
Chantiers programmés :
- Chantier 1 : [Nom]
- Chantier 2 : [Nom]
...
Démarrage du premier chantier.
```

### 3.2 🗣️ Comment le Superviseur Racine Restitue-t-il le Lancement dans le Chat ?
Dès réception du message, le Superviseur Racine affiche immédiatement à Henri dans le chat :
1. Le lien absolu cliquable vers `implementation_plan.md`.
2. La liste numérotée des chantiers étanches qui vont être déroulés.
3. Le lancement du Chantier 1.

---

## 4. 🚀 Comment Piloter la Progression Pas-à-Pas et Informer le Chat en Direct ?

```mermaid
flowchart TD
    LEAD["Build Lead (P=1)"] -->|invoke_subagent unique| FORK["🚀 Déploiement Parallèle Massif"]
    FORK --> W1["Worker Feuille (P=2) : Chantier 1 (Web / Playwright)"]
    FORK --> W2["Worker Feuille (P=2) : Chantier 2 (Notes Coffre)"]
    FORK --> W3["Worker Feuille (P=2) : Chantier 3 (Hygiène Vault)"]
    W1 -->|send_message| LEAD
    W2 -->|send_message| LEAD
    W3 -->|send_message| LEAD
    LEAD -->|Une fois tous les chantiers reçus| W_INT["Worker Intégration & Vérification (P=2)"]
    W_INT -->|walkthrough.md| LEAD
```

### 4.1 👥 Comment Déployer les Workers Feuilles ($P=2$) en Parallèle Maximal ?
- **Règle d'Or de Parallélisme** : Le Build Lead analyse la matrice de dépendances des chantiers. Tous les chantiers étanches $N_1, N_2, \dots$ sont lancés **simultanément au même tour** dans un tableau `Subagents: [...]`.
- **Zéro Goulot Séquentiel Artificiel** : Interdiction de temporiser ou d'attendre la complétion d'un chantier indépendant avant de lancer les autres.
- **Séquençage Réservé aux Dépendances Strictes** : Seul le Worker d'Intégration & Vérification Finale ($P=2$) est déployé après réception des confirmations de tous les chantiers.
- **Armement Systématique du Timer de Liveness (300s)** : Immédiatement après le déploiement des workers, appeler schedule avec DurationSeconds: 300, TimerCondition: "any", Prompt: "Heartbeat Liveness : vérifier l'avancement des workers de chantiers et unblocker tout worker silencieux.". Dès que le timer expire ou qu'un worker répond, auditer l'état actif et réarmer le timer tant que des workers P=2 sont en cours.
- **Transmission Obligatoire du Plan d'Implémentation Global** : Le Build Lead transmet systématiquement le lien absolu vers implementation_plan.md (file:///<appDataDir>/brain/<build-lead-id>/implementation_plan.md) dans le prompt de chaque worker feuille avec consigne impérative de le lire en action n°1 via view_file pour assimiler l'architecture générale, les interfaces et la finalité de la session.
- **Garde-Fou Infranchissable de Confinement au Chantier** : Bien que le worker comprenne le tableau d'ensemble, il a l'interdiction formelle et absolue de modifier, créer ou supprimer le moindre fichier en dehors du périmètre chirurgical de son propre chantier assigné.
- **Template de Prompt pour Worker Feuille** :
  ```text
  Tu es le Worker Feuille pour le Chantier N (P=2).
  Périmètre exclusif : [Nom du chantier, fichiers ciblés, spécifications exactes]

  CADRE ARCHITECTURAL GLOBAL & PLAN D'IMPLÉMENTATION :
  Consulte obligatoirement en première action le plan d'implémentation global de la session via view_file :
  file:///<appDataDir>/brain/<build-lead-id>/implementation_plan.md
  Objectif : Assimiler le contexte d'ensemble, les tenants et aboutissants, les interfaces partagées et la cohérence systémique du projet.

  GARDE-FOU D'ÉTANCHÉITÉ STRICTE (CONFINEMENT OBLIGATOIRE AU CHANTIER N) :
  Bien que tu aies la pleine visibilité sur le plan global, TU DOIS TE CANTONNER STRICTEMENT ET EXCLUSIVEMENT À TON CHANTIER ASSIGNÉ.
  Il t'est FORMELLEMENT ET ABSOLUMENT INTERDIT de modifier, créer, renommer ou supprimer un quelconque fichier en dehors du périmètre précis spécifié pour ton Chantier N.

  Consignes impératives :
  1. Édition chirurgicale in-situ. Zéro régression, zéro erreur silencieuse.
  2. S'aligner fidèlement sur l'architecture et les conventions existantes.
  3. INTERDICTION FORMELLE de déployer des sous-agents (exécutant direct P=2).
  4. Mener de manière autonome toutes les vérifications locales (compilation, syntaxe, lint, tests live dans scratch).
  5. Rapporter la fin du chantier avec preuves matérielles brutes par send_message au Build Lead.
  ```

### 4.2 📡 Quel Est le Protocole de Notification à Chaque Fin de Chantier ?
- Dès qu'un worker feuille termine son chantier et confirme ses vérifications par `send_message`, le Build Lead audite le résultat matériel.
- Si le chantier est validé, le Build Lead envoie immédiatement un message au Superviseur Racine indiquant la fin du Chantier N et le passage au Chantier N+1.

### 4.3 💬 Quel Est le Format d'Avancement Temps Réel Affiché dans le Chat ?
À chaque notification reçue du Build Lead, le Superviseur Racine diffuse en temps réel dans le chat la ligne d'avancement suivante :
`✅ Chantier N terminé ([Nom du Chantier]) ➔ 🚀 Lancement du Chantier N+1 ([Nom du Chantier])`

---

## 5. 🧪 Comment Vérifier l'Intégration Globale et Rédiger le Walkthrough ?

### 5.1 🤖 Comment le Worker Final ($P=2$) Valide-t-il l'Intégrité Matérielle Autonome ?
Une fois l'ensemble des chantiers achevés, le Build Lead déploie un sous-agent worker final d'intégration (`Role: "Integration & Verification Worker"`, `TypeName: "self"`, `Workspace: "inherit"`).
Ce worker final mène de façon autonome et rigoureuse l'ensemble des vérifications nécessaires (sans dépendre d'une grille prédéfinie dans les rapports d'exploration) :
1. **Compilation & Syntaxe** : Exécution réelle des commandes de compilation, linters ou analyse statique (`exit code 0`).
2. **Audit des Interfaces & Imports** : Vérification de la synchronisation de tous les modules modifiés ou créés.
3. **Validation Fonctionnelle Live** : Lancement d'un test fonctionnel concret ou d'une commande d'inspection sur les sorties réelles (scripts jetables dans `<appDataDir>/brain/<build-lead-id>/scratch/`).
4. **Rapport de Clôture** : Envoi au Build Lead des preuves matérielles brutes (logs, sorties de commandes, métriques réelles).

### 5.2 📄 Quelle Est la Structure Canonique de walkthrough.md ?
Le Build Lead produit l'artéfact `walkthrough.md` dans son brain (`<appDataDir>/brain/<build-lead-id>/walkthrough.md`) via `write_to_file` :

```markdown
# 🏗️ Walkthrough d'Implémentation : [Titre du Projet] ?

## 🎯 Quel Est le Rappel de la Mission & la Synthèse Exécutive ?
- **Plan Fusionné** : `implementation_plan.md` (consolidation des Sections 2 des rapports 1 à X)
- **Chantiers Réalisés** : [Liste ordonnée des chantiers menés à bien]

## 🛠️ Quelles Sont les Modifications Chirurgicales Réalisées par Chantier ?

### Chantier 1 : [Nom du Chantier]
- **Fichiers modifiés / créés** :
  - `[NomFichier](file:///chemin/vers/fichier)` : [Description précise des ajouts/modifications]
- **Garde-fous respectés** : [Mesures prises contre les erreurs silencieuses et régressions]

### Chantier 2 : [Nom du Chantier]
- ...

## 🧪 Quelles Sont les Preuves Matérielles des Vérifications d'Intégration ?

| Point de Contrôle | Commande ou Méthode Autonome | Résultat Matériel | Preuve Brute Vérifiée |
|---|---|:---:|---|
| **Compilation / Syntaxe** | `[Commande exacte]` | ✅ Conforme | Exit code 0, zéro erreur |
| **Cohérence des Interfaces** | Audit signatures & contrats | ✅ Conforme | Types et signatures synchronisés |
| **Validation Live** | `[Commande / Script live]` | ✅ Validé | [Données / sorties réelles] |

## 👤 Quelles Sont les Actions Manuelles Réservées à Henri ?
- [Vérifications applicatives ou métier spécifiques nécessitant un contrôle visuel par Henri]
```

### 5.3 🔒 Comment S'Opère le Scellement Post-Build d'Implementation Plan ?
Une fois walkthrough.md publié et validé :
- Le Build Lead conserve implementation_plan.md strictement intact et complet dans son répertoire brain.
- Aucune purge ni remise à blanc n'est tolérée : le document demeure l'archive technique canonique de référence de la session d'implémentation.

---

## 6. 🛑 Comment S'Arrêter Proprement et Restituer la Clôture Finale ?

### 6.1 📊 Quel Est le Format de Clôture Définitive dans le Chat ?
Le Build Lead notifie le Superviseur Racine de la fin de mission avec le lien vers `walkthrough.md`.
Le Superviseur Racine compose sa réponse de clôture dans le fil de discussion :
1. **Ligne 1 (MANDATOIRE)** : Lien cliquable vers la note maîtresse Obsidian du projet : `[Nom de la Note Maîtresse](file:///chemin/absolu/vers/la/note.md)`.
2. **Bloc d'Artéfact** : Référence directe au walkthrough : `[walkthrough.md](file:///<appDataDir>/brain/<build-lead-id>/walkthrough.md)`.
3. **Synthèse d'Accomplissement** : Résumé des chantiers exécutés et des preuves matérielles d'intégration obtenues.
4. **Vérifications Manuelles Henri** : Rappel clair des contrôles métier réservés à Henri.

### 6.2 🚫 Pourquoi Aucun Enchaînement Automatique N'est-il Toléré ?

> [!CAUTION]
> **RÈGLE CARDINALE : AUCUN ENCHAÎNEMENT AUTOMATIQUE (No Auto-Chaining).**
> Ne jamais relancer automatiquement de skill ni d'outil à la suite du Walkthrough. La clôture de Build marque la fin du cycle de développement. Toute nouvelle action requiert une instruction explicite d'Henri.
