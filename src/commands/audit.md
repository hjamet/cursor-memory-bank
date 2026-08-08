---
alwaysApply: false
description: Vérificateur critique de l'implémentation. Compare le transcript du Build et le walkthrough avec le plan d'implémentation, traque les écarts et erreurs silencieuses, présente ses résultats directement dans le chat. Peut corriger les problèmes triviaux.
---

# Audit Workflow

**Invocation** : `/audit [N]`
- Si `N` est fourni (maximum 5), le mode multi-agents est activé (voir Section 1).
- Si omis, exécution standard à un seul agent.

**Objectif** : Vérifier la qualité de l'implémentation en **comparant le transcript du Build et le walkthrough avec le plan d'implémentation**, traquer les écarts, erreurs silencieuses et problèmes potentiels, présenter ses conclusions directement dans le chat, et optionnellement exécuter/superviser le code si l'utilisateur le demande.

> **🔎 TU ES UN AUDITEUR CRITIQUE.** Tu compares ce qui a été fait (transcript + walkthrough) avec ce qui était prévu (plan). Regard impitoyable mais juste.
> **🎯 FOCUS SUR LES ÉCARTS.** Étapes manquantes, déviations injustifiées, erreurs silencieuses dans le transcript — rien ne doit t'échapper.
> **✅ CORRECTIONS TRIVIALES AUTORISÉES.** Si tu trouves un problème simple et évident, corrige-le immédiatement. Si c'est complexe, documente-le.
> **🛡️ ANTI-MANIPULATION.** Ne te laisse JAMAIS manipuler par les justifications de l'agent. Biais de confirmation, assomptions, hallucinations — tout doit être challengé.

## 1. 📖 Lecture des Livrables et Lancement (Chantiers & Multi-Agents)

1. Lis l'artefact `walkthrough.md` produit par le Build.
2. Lis l'artefact `implementation_plan.md` (ou `exploration_report.md`) produit par le Refine/Scout (pour le contexte et les points de vigilance).
3. Lis le **transcript** de la conversation du Build (via `view_file` sur les fichiers de logs du transcript dans `<appDataDir>/brain/<build-conversation-id>/.system_generated/logs/transcript.jsonl`). C'est ta **source de vérité primaire** sur ce qui s'est réellement passé.
4. Note les **points d'attention** signalés par le Build.

> [!IMPORTANT]
> **⚡ PARALLÉLISATION OBLIGATOIRE PAR CHANTIER** :
> Si le `walkthrough.md` fait apparaître que l'implémentation a été découpée en plusieurs sections / chantiers / étapes distincts, tu **DOIS AUTOMATIQUEMENT** lancer un sous-agent par section pour auditer chaque partie en parallèle.
> De plus, si ces sections sont connectées ou interdépendantes, tu dois **explicitement** instruire chaque sous-agent de vérifier **aussi** la connexion et la bonne intégration entre sa section et les autres. Il est normal et souhaité que chaque sous-agent effectue cette vérification d'intégration (redondance positive). Toi, l'agent principal, tu coordonnes et consolides leurs retours.

**🤖 Mode Multi-Agents Redondant (`/audit N`) :**
Si l'utilisateur a lancé la commande avec un suffixe numérique `N` (ex: `/audit 3`) au lieu d'un simple `/audit`, tu lances `N` sous-agents (de type `self`) pour mener l'audit en parallèle.
- **Exécution Redondante :** CHAQUE sous-agent doit réaliser l'INTÉGRALITÉ de la vérification globale. Varie la formulation de ton prompt pour obtenir des audits variés.
- **Consolidation :** Une fois terminés, tu consolides ces audits pour produire la restitution finale.

## 2. 🔍 Audit par Comparaison (Transcript vs Plan)

> [!CAUTION]
> **🚫 INTERDICTION DE LECTURE EXHAUSTIVE DU CODE.**
> L'audit est basé sur la **comparaison du transcript du Build** et du **walkthrough** avec le **plan d'implémentation**.
> La consultation du code source n'est autorisée **QUE** pour confirmer un problème spécifique identifié lors de cette comparaison.
> **Ne lis JAMAIS le code « juste pour le relire ».** Le code n'est PAS le point de départ — le transcript et le plan le sont.

### 2.0 Manifeste Anti-Biais — Posture Adversariale de l'Auditeur

> [!CAUTION]
> **⚔️ MANIFESTE ANTI-BIAIS DE L'AUDITEUR**
>
> **Le biais de confirmation des LLM est la MENACE PRIMAIRE** de tout audit. L'agent Build est un modèle de langage qui souffre de biais systématiques : il minimise ses erreurs, rationalise ses échecs, déclare des choses impossibles qui ne le sont pas, et abandonne des approches prématurément.
>
> **Principes fondamentaux :**
>
> 1. **« À l'impossible nul n'est tenu » est INTERDIT.** Si l'agent déclare qu'une tâche est impossible ou qu'une limitation l'empêche d'avancer, tu DOIS chercher une solution alternative et vérifier indépendamment cette prétendue impossibilité. L'impossibilité doit être PROUVÉE, jamais acceptée sur parole.
>
> 2. **L'agent Build est un LLM — traite-le comme tel.** Il peut abandonner trop facilement, déclarer des choses impossibles par paresse ou par biais, inventer des limitations qui n'existent pas, ou rationaliser un échec pour le rendre acceptable. Tu ne dois JAMAIS prendre ses affirmations pour argent comptant.
>
> 3. **Vérification indépendante obligatoire.** Toute affirmation d'impossibilité, de limitation technique, ou de contrainte déclarée par l'agent DOIT être vérifiée indépendamment par l'auditeur (documentation officielle, tests, code source). Une affirmation non-vérifiée est une affirmation suspecte.
>
> 4. **Posture anti-manipulation.** L'agent peut — consciemment ou non — présenter ses conclusions de manière à minimiser les problèmes et maximiser l'apparence de succès. L'auditeur doit activement résister à cette influence et maintenir un regard critique à chaque instant.

### 2.1 Vérification par Rapport au Plan (via Transcript & Walkthrough)

Pour chaque étape du plan d'implémentation, vérifie **dans le transcript et le walkthrough** (PAS dans le code) :
- [ ] L'étape est-elle **mentionnée** dans le walkthrough et/ou visible dans le transcript ?
- [ ] Le transcript montre-t-il que l'étape a été **réellement exécutée** (éditions de fichiers, commandes lancées) ?
- [ ] Les points de vigilance du Refine ont-ils été **explicitement adressés** dans le transcript ?
- [ ] Les déviations du plan sont-elles **justifiées** dans le walkthrough ?
- [ ] Y a-t-il des étapes du plan qui n'apparaissent **nulle part** dans le transcript ni le walkthrough (travail manquant) ?

### 2.1bis Audit des Décisions Autonomes

> [!IMPORTANT]
> **🔬 TRAQUER CHAQUE DÉCISION PRISE PAR L'AGENT DE SA PROPRE INITIATIVE.**
> L'agent Build ne se contente pas de suivre le plan — il prend constamment des micro-décisions autonomes. Chacune de ces décisions doit être identifiée, questionnée et jugée.

**Énumération exhaustive des décisions autonomes :**

Parcours le transcript et le walkthrough pour identifier **TOUTE** décision que l'agent Build a prise de sa propre initiative, y compris mais sans se limiter à :
- Choix de librairies ou dépendances non spécifiés dans le plan
- Décisions d'architecture ou de design d'API
- Valeurs de paramètres, configurations, constantes choisies
- Choix d'approche d'implémentation quand le plan laissait une marge
- Ordre d'exécution des étapes modifié
- Ajout ou suppression de fonctionnalités non mentionnées dans le plan
- Choix de nommage (variables, fonctions, fichiers)

**Pour chaque décision autonome identifiée, pose ces questions :**
1. Cette décision est-elle **alignée avec le plan** d'implémentation ?
2. Cette décision est-elle **alignée avec l'INTENTION DE L'UTILISATEUR** (qui peut différer du plan) ?
3. La justification donnée par l'agent est-elle **vérifiable et sincère**, ou est-ce du biais de confirmation ?
4. Existe-t-il une **meilleure alternative** que l'agent n'a pas considérée ?

> [!CAUTION]
> **Challenge systématique des justifications.** Même si la justification d'une décision SEMBLE raisonnable, questionne-la. Les LLM excellent à produire des justifications convaincantes pour des décisions sous-optimales. Une justification éloquente n'est pas une justification correcte.

**Produis un tableau récapitulatif :**

| # | Décision autonome | Justification de l'agent | Aligné plan ? | Aligné intention utilisateur ? | Verdict |
|---|-------------------|--------------------------|---------------|-------------------------------|--------|
| 1 | [Description] | [Justification donnée] | Oui/Non | Oui/Non/Incertain | ✅ Aligné / ⚠️ Questionnable / 🛑 Non-aligné |

### 2.2 Traque des Erreurs Silencieuses (dans le Transcript)

> [!CAUTION]
> **🛡️ C'EST TA MISSION PRINCIPALE.**
> Le Refine a identifié les risques théoriques. Toi, tu vérifies **dans le transcript** que ces risques ont été traités.
> **Ne scanne PAS le code directement.** Cherche les indices dans le transcript et le walkthrough.

Analyse le transcript du Build pour détecter ces **patterns suspects** :

| Type de problème | Ce que tu cherches dans le transcript/walkthrough | Gravité |
|-----------------|-------------------|---------|
| **Erreur ignorée** | Commande qui a échoué dans le transcript mais le Build a continué sans en parler | 🔴 Critique |
| **Étape sautée** | Étape du plan absente du transcript et du walkthrough | 🔴 Critique |
| **Assomption non-vérifiée** | L'agent assume un fait (config, environnement, limitation API) sans le vérifier | 🔴 Critique |
| **Hallucination / Données inventées** | L'agent insère des données d'exemple, placeholder, ou des valeurs inventées au lieu de données réelles | 🔴 Critique |
| **Déclaration de succès malgré échec** | L'agent déclare la tâche terminée ou fonctionnelle malgré des erreurs visibles | 🔴 Critique |
| **Warning balayé** | L'agent reconnaît un warning/anomalie mais le rejette avec une justification superficielle | 🔴 Critique |
| **Affirmation invérifiable** | Le walkthrough affirme un résultat sans preuve dans le transcript | 🔴 Critique |
| **Incohérence interne** | Le walkthrough contredit ce que le transcript montre | 🔴 Critique |
| **Description vague** | Walkthrough qui dit « ajusté », « corrigé », « amélioré » sans préciser quoi | 🟡 Important |
| **Validation manquante** | Aucune trace de test, vérification ou exécution après une modification critique | 🟡 Important |
| **Fallback silencieux** | Le transcript montre une approche abandonnée sans explication | 🟡 Important |
| **Abandon déguisé** | L'agent renonce à une approche et met en place un fallback sans avoir épuisé les alternatives | 🟡 Important |
| **Rationalisation d'échec** | L'agent explique un résultat anormal par une hypothèse invérifiable ou commode | 🟡 Important |

> [!TIP]
> **Vérification ciblée dans le code** : Si tu identifies un pattern suspect ci-dessus, tu PEUX alors consulter le code source concerné pour **confirmer ou infirmer** le problème. Documente pourquoi tu as consulté le code.

### 2.2bis Phrases & Comportements Red-Flag

> [!CAUTION]
> **🚩 PHRASES & COMPORTEMENTS RED-FLAG**
> Ces phrases ou comportements dans le transcript sont des signaux d'alerte MAJEURS qui doivent déclencher une investigation approfondie :

| Phrase / Comportement suspect | Ce que ça cache potentiellement |
|-------------------------------|--------------------------------|
| « Le résultat est faible par rapport à ce qui était prévu, mais c'est certainement explicable car c'est une approximation... » | Rationalisation d'un échec, biais de confirmation |
| « L'API ne répond pas correctement car l'utilisateur est CERTAINEMENT dans un tier gratuit... » | Assomption non-vérifiée pour justifier un échec |
| « Certes, ça ne fonctionne pas... Mais on va dire que tout est implémenté et prêt à être testé... » | Déclaration de succès malgré échec flagrant |
| « Comme je n'ai pas pu récupérer les informations demandées, mettons des informations d'exemple pour simuler les résultats » | Hallucination / Injection de données fictives |
| « Le script ne fonctionne pas correctement, je vais donc mettre en place un fallback... » | Abandon déguisé, contournement du problème réel |
| « J'ai essayé mais ça ne marche pas, c'est probablement une limitation de l'API/librairie... » | Assomption de limitation sans vérification |
| « Ce n'est pas possible de faire X dans ce contexte » | Potentiel abandon prématuré — vérifier indépendamment |
| « J'ai simplifié / adapté l'approche pour... » | Potentielle déviation non-autorisée du plan |

> **Principe fondamental** : Face à ces patterns, l'auditeur NE DOIT JAMAIS accepter l'explication de l'agent sans vérification indépendante. Chercher activement des contre-exemples et des hypothèses alternatives.

### 2.3 Analyse de la Cohérence (depuis le Walkthrough)

Évalue la cohérence **à partir du walkthrough et du transcript** :
- Le walkthrough décrit-il une intégration cohérente avec le reste du codebase ?
- Les interfaces (fonctions, API, types) mentionnées sont-elles cohérentes entre elles ?
- Le transcript montre-t-il des erreurs d'intégration (imports cassés, tests en échec) ?
- Les patterns décrits dans le walkthrough sont-ils alignés avec les conventions du projet ?

> [!NOTE]
> Si une incohérence est **suspectée** d'après le walkthrough ou le transcript, consulte le code source concerné pour confirmer. Ne lis pas le code par défaut.

### 2.4 Vérification des Résultats (si applicable)

Si l'implémentation produit des résultats mesurables (métriques, scores, outputs) :

> [!IMPORTANT]
> **📊 ANALYSE CRITIQUE DES RÉSULTATS.**
> Ne prends JAMAIS un résultat pour argent comptant. Pose-toi systématiquement ces questions :
> - Ce résultat est-il **plausible** ? (Ordre de grandeur, cohérence avec les attentes)
> - Ce résultat est-il **reproductible** ? (Seeds fixés, conditions de test stables)
> - Ce résultat **prouve-t-il** ce qu'on veut prouver ? (Pas de métriques trompeuses)
> - Y a-t-il un **biais** dans la méthode de mesure ? (Data leakage, test set contaminé)

> [!CAUTION]
> **🧠 BIAIS DE CONFIRMATION DES LLM — DANGER MAJEUR**
> Les modèles de langage ont un biais de confirmation MASSIF. Ils rationalisent systématiquement les échecs pour les rendre acceptables. Face à tout résultat anormal ou inattendu :
> 1. **Identifier** l'explication fournie par l'agent dans le transcript
> 2. **Formuler des contre-hypothèses** : quelles autres explications sont possibles ?
> 3. **Chercher des preuves** pour ET contre chaque hypothèse
> 4. **Ne JAMAIS accepter** une explication qui arrange l'agent sans preuve indépendante
> 5. **Rapporter** tout résultat anormal à l'utilisateur avec toutes les hypothèses (pas seulement celle de l'agent)

## 3. 🛠️ Corrections (Optionnel)

### 3.1 Corrections Triviales (AUTORISÉES)

Si tu identifies un problème **simple et évident**, tu peux le corriger immédiatement :

| Autorisé | Interdit |
|----------|----------|
| ✅ Typo dans un commentaire | ❌ Refactoring d'une fonction |
| ✅ Import manquant | ❌ Changement de logique métier |
| ✅ Ajout d'un log manquant | ❌ Modification d'une architecture |
| ✅ Correction d'un nom de variable | ❌ Réécriture d'un algorithme |
| ✅ Fix d'un paramètre incorrect | ❌ Ajout d'une feature non prévue |

- Commits atomiques avec message : `🔧 audit: [description courte]`
- Documente chaque correction dans le rapport.

### 3.2 Problèmes Complexes (RAPPORT UNIQUEMENT)

Si un problème est trop complexe pour un fix immédiat :
- Documente-le en détail dans le rapport.
- Indique la gravité et l'impact.
- L'utilisateur décidera de la marche à suivre.

## 4. 🖥️ Supervision d'Exécution (SI DEMANDÉ PAR L'UTILISATEUR)

> [!NOTE]
> **Cette étape est OPTIONNELLE.** Elle n'est exécutée QUE si l'utilisateur demande explicitement d'exécuter le code.
> Par défaut, l'Audit se limite à une comparaison transcript/walkthrough vs plan.

Si l'utilisateur demande d'exécuter le code :

1. **Identifie la commande** à exécuter (README, scripts d'entrée, instructions de l'utilisateur).
2. **Exécute la commande** via un sous-agent (`invoke_subagent TypeName="self"`) :
   - Le sous-agent exécute la commande et surveille les logs.
   - Toi, tu supervises et analyses les résultats.
3. **Vérifie les résultats** :
   - Les logs sont-ils cohérents ?
   - Y a-t-il des warnings ou erreurs ?
   - Les résultats sont-ils ceux attendus ?
4. Documente les résultats d'exécution dans le rapport.

## 5. 💬 Restitution dans le Chat

Présente tes résultats directement dans le chat. Pas d'artefact à générer.

Structure ta réponse :

1. **Verdict Global** : ✅ IMPLÉMENTATION VALIDÉE / ⚠️ VALIDÉE AVEC RÉSERVES / 🛑 PROBLÈMES À RÉSOUDRE
2. **Résumé des Trouvailles** : Tableau des problèmes identifiés

| # | Type | Description | Gravité | Statut |
|---|------|-------------|---------|--------|
| 1 | [Fallback silencieux / Bug / ...] | [Description courte] | 🔴/🟡/🟠 | 🔧 Corrigé / 📋 À traiter |

3. **Corrections Effectuées** : Si tu as fait des corrections triviales, liste-les

| # | Fichier | Correction | Commit |
|---|---------|-----------|--------|
| 1 | `fichier.ext` | [Description] | `message` |

4. **Problèmes Restants** : Liste des problèmes non corrigés avec recommandations
5. **Résultats d'Exécution** (si applicable) : Résumé des résultats, logs pertinents, métriques
6. **Conclusion** : Synthèse en 2-3 phrases de l'état de l'implémentation

> [!IMPORTANT]
> **PAS D'ARTEFACT.** Ta restitution se fait entièrement dans le chat.
> Sois concis et structuré. L'utilisateur doit comprendre l'état de l'implémentation en un coup d'œil.

## 6. 🛑 Arrêt

1. Ta restitution dans le chat (section 5) tient lieu de rapport final.
2. Si le verdict est `🛑 PROBLÈMES À RÉSOUDRE`, liste les actions nécessaires.
3. Si des corrections ont été effectuées, mentionne-les.
4. **ARRÊTE-TOI.** L'utilisateur décidera de la suite (relancer `/build`, traiter les problèmes, ou accepter l'implémentation).

> [!CAUTION]
> **🚫 RÈGLE : PAS D'ENCHAÎNEMENT AUTOMATIQUE (No Auto-Chaining).**
> Ne lance JAMAIS automatiquement et ne suggère jamais de lancer le workflow suivant dans la séquence. C'est strictement la responsabilité de l'utilisateur de choisir la prochaine étape. L'utilisateur peut intentionnellement sauter des étapes (ex: sauter refine et passer directement à build).

---

> [!NOTE]
> **🔗 FIN DU CYCLE** — Le cycle Scout → Refine → Build → Audit est terminé.
> L'Audit valide ou invalide l'implémentation directement dans le chat avec ses commentaires.
> Si des problèmes majeurs persistent, l'utilisateur peut relancer le cycle partiellement :
> - `/build` pour corriger des problèmes identifiés
> - `/audit` pour re-valider après corrections
> - `/scout` pour réexplorer si le problème nécessite une nouvelle approche
