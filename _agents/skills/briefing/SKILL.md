---
name: briefing
description: "Tient à jour la sous-note hebdomadaire de briefing d'un projet (compte rendu de la dernière réunion + flux incrémental de composants Microsoft Loop prêts à copier dans Teams sur les décisions méthodologiques, résultats et jalons du papier via /draft) ou produit sur demande une fiche A4 imprimable. Activer sur /briefing."
---
# 📋 Comment Fonctionne le Skill `/briefing` (Composants Loop Teams Incrémentaux & Suivi de Supervision) ?

**Objectif** : permettre à Henri de transmettre en continu à ses superviseurs (Yash Raj Shrestha, Pamela Delgado, Michalis Vlachos…) des mises à jour asynchrones naturelles, directes et digestes sur **Microsoft Teams (composants Loop)**, tout en tenant à jour dans le coffre une sous-note hebdomadaire sourcée sur les **sources primaires originales**.

---

## 🎯 1. Quel est le Filtre Éditorial et Stylistique Strict (« Public = Superviseurs ») ?

> [!IMPORTANT]
> **RÈGLES CARDINALES ISSUES DES RETOURS DE YASH, PAMELA, MICHALIS ET HENRI :**
> 1. **Ce que veulent savoir les superviseurs (et séparation claire des préoccupations)** :
>    - **Avancement concret et calendrier daté** : dates exactes de lancement (pilote, étude principale), nombre de participants terminés vs cible, travail actif de supervision en coulisse (ex. surveillance continue des sessions et relance régulière des participants qui n'ont pas terminé), et estimation personnelle honnête du calendrier d'ici la deadline.
>    - **Tendances empiriques digestes (appuyées sur des figures jointes)** : ce que montrent concrètement les données sur nos variables cibles et nos groupes (sans noyer le message sous des dizaines de moyennes $\pm$ écarts-types qui sont déjà dans les figures ou les tables de l'Overleaf).
>    - **État réel du manuscrit Overleaf (assumé comme WIP tant que l'étude tourne)** : indiquer clairement quelles sections sont rédigées ou mises à jour en brouillon de travail (*Work in Progress*), sans jamais donner l'illusion que l'article est « terminé » ni prendre un ton justificatif ou défensif.
> 2. **Ce que l'on bannit intégralement (zéro cuisine interne, zéro auto-congratulation IA)** :
>    - **Zéro détail du coffre Obsidian ou d'intendance interne** : ne jamais mentionner la synchronisation d'une note Obsidian, des scripts internes, des commits Git, des conteneurs Docker ou des détails de code.
>    - **Zéro formule promotionnelle ou triomphaliste IA** : bannir absolument les `(100% Data Integrity)`, `everything is perfect`, `sharp collapse`, `flawless`, `self-contained paper immediately`. Rester sobre, neutre et scientifique.
>    - **Zéro présent de vérité générale / ton impersonnel LLM** : bannir les affirmations péremptoires du type *« finishing by Wednesday gives a realistic 48-hour buffer »*. Utiliser systématiquement la **voix personnelle d'Henri avec ses opinions, ses réserves et ses estimations** : **`"I think..."`**, **`"In my view..."`**, **`"My estimate is..."`**, **`"I hope..."`**, **`"Honestly, 25 evaluations from 5 reviewers is still way too small for a precise statistical evaluation, but it already gives a first glimpse of..."`**.
> 3. **Première personne du singulier obligatoire (`I` / `my`) et nomenclature unifiée du papier** :
>    - Toujours écrire au singulier (`I launched`, `I am monitoring`, `I think`) pour le travail d'Henri, avec des smileys textuels sobres (`:)`, `:D`) quand c'est naturel (cf. [`email-style/SKILL.md`](file:///c:/Users/hjamet/Documents/VoiceNotes/_agents/skills/email-style/SKILL.md)).
>    - Toujours utiliser la **nomenclature explicite du papier** (ex. `G1 (HITL + MA + PKG)`, `G2 (HITL + MA)`, `G3 (HITL + PKG)`, `G4-TWIN (PKG + MA)`, `G5-TWIN (single-LLM baseline)`) et jamais des identifiants de base de données obscurs.
> 4. **Usage strict des émojis d'état (`✅`, `🔄`) : UNIQUEMENT pour l'état des tâches, JAMAIS devant des résultats ou analyses** :
>    - `✅` et `🔄` n'ont de sens que devant des **tâches opérationnelles** (jalon terminé vs jalon en cours). **Il est strictement interdit de mettre `✅` ou `🔄` devant des points d'analyse scientifique ou des résumés de résultats** : utiliser des puces simples (`- `) sans emoji.
> 5. **Composant Loop Question (`Q&A`) : contraintes complètes (pool, éthique, OSF) & synchronisation de relecture** :
>    - Jamais de ligne `Recommendation:` ni d'options `Option 1 / Option 2 / Poll`.
>    - Lorsqu'une question porte sur un filtre Prolific ou le protocole expérimental, toujours inclure : (a) la **taille exacte du vivier éligible actuel**, (b) l'impact sur le **pré-enregistrement OSF** (et le fait que modifier l'OSF pendant la collecte est méthodologiquement douteux), et (c) la compatibilité avec **l'approbation éthique CER-HEC** (qui ne peut plus être modifiée).
>    - Lorsqu'un draft Overleaf est partagé en relecture, toujours inclure une question de synchronisation invitant les superviseurs à signaler dès qu'ils ont terminé leur lecture : *"Could you reply to this question as soon as you have finished reading the article so that I can go through your edits in detail and align my revisions with the direction you want to give the paper? :)"*

---

## 🗂️ 2. Où Vivent les Sous-Notes de Briefing et Quelles Règles de Sourçage S'Appliquent ?

Chaque projet suivi en supervision possède une sous-note de briefing hebdomadaire liée sous le H1 de la note maîtresse :
- **Emplacement dans le coffre** : `c:\Users\hjamet\Documents\VoiceNotes\notes\Briefing <Nom Projet> <YYYY MM DD>.md` (espaces uniquement, ex. `Briefing DLLP 2026 10 19.md`), indexée sous le H1 de la note maîtresse.
- **Ancres de source primaires obligatoires** : dans la sous-note Obsidian, chaque section (`##` / `###`) suit le format `Question ➔ 1–2 phrases d'explication directe ➔ Source : <ancre primaire originale> ➔ bloc de citation`. **Ne jamais citer un artefact temporaire de session (`brain/`) comme `Source :`** ; toujours citer la source primaire originale (requête DB, script, API Prolific, note de réunion).

---

## 🧩 3. Quel est le Format Canonique des Composants Microsoft Loop pour Teams ?

Un briefing Teams se compose de **3 blocs Loop complémentaires et concis** :

### Bloc 1 — Avancement des Tâches & Collecte (`Task & Data Collection Update`)
*Seul bloc où `✅` (tâche finie) et `🔄` (tâche en cours) sont autorisés, car chaque puce est une tâche du calendrier.*

```markdown
# Where do we stand on the Prolific study and the WWW 2027 timeline?

- ✅ <Tâche terminée avec dates exactes (ex. Pilot 5+5 launched on Oct X and completed on Oct Y)> : <Résumé factuel court et sobre, sans "100% parfait">.
- 🔄 <Tâche en cours avec date de lancement (ex. Main Phase 1 study launched on Oct Z — X / 25 teacher courses completed)> : <État actuel, mention explicite de la surveillance continue et des relances régulières des professeurs en cours ("I am continuously monitoring active sessions and regularly following up with teachers who haven't finished yet"), et estimation personnelle ("Wait times are slower than I hoped, but I think / I hope we can finish Phase 1 by...")>.
- 🔄 <Tâche manuscrit Overleaf (WIP)> : <Explication simple et directe de l'état WIP du draft partagé sur Overleaf pour recueillir leurs premiers retours>.
```

### Bloc 2 — Premières Tendances des Résultats (`First Empirical Trends — Preliminary`)
*Zéro emoji `✅`/`🔄`. Synthèse digeste en puces simples (`- `), renvoyant aux figures jointes pour les chiffres détaillés et précisant d'emblée la taille limitée de l'échantillon actuel.*

```markdown
# What are the first trends in our preliminary data (see attached plots)?

- **Sample & Preliminary Scope** : <Préciser honnêtement que l'échantillon actuel (ex. 15 professeurs en Phase 1 et seulement 5×5 = 25 évaluations croisées du pilote en Phase 2) est encore bien trop petit pour tirer des conclusions définitives, mais permet déjà de vérifier la qualité des données et d'observer de premières tendances>.
- **Course Structure & Perceived Usefulness (Phase 1, Q2 & Telemetry)** : <Expliquer l'enseignement principal de façon claire et parlante sans noyer sous les SD, ex. l'effondrement en bloc unique sans Knowledge Graph en G2 vs les cours modulaires en G1/G3, et le contraste d'utilité perçue>.
- **Double-Blind Peer Review (Phase 2 Pilot, 5×5 = 25 evaluations, Q3)** : <Synthétiser en 2 phrases la hiérarchie observée de G1 à G5-TWIN et le contraste entre utilité perçue par le créateur et qualité réelle jugée à l'aveugle, en renvoyant au graphique>.
```

### Bloc 3 — Composant Loop Question (`Loop Q&A`)
*Questions ouvertes numérotées permettant aux superviseurs de répondre directement dessous dans Teams.*

```markdown
# Questions on Prolific recruitment and Overleaf review (Loop Q&A)

1. <Question méthodologique / recrutement incluant : (a) le nombre exact de participants éligibles avec les filtres actuels, (b) le fait qu'élargir les filtres obligerait à modifier le pré-enregistrement OSF en pleine collecte (ce qui semble très douteux), et (c) le fait que cela risque de sortir du cadre de notre approbation éthique CER-HEC que nous ne pouvons pas modifier ?>
2. <Question de coordination sur la relecture Overleaf : "Could you reply to this question as soon as you have finished reading the article so that I can go through your edits in detail and align my revisions with the direction you want to give the paper? :)" >
3. <Question ponctuelle éventuelle (ex. affiliation exacte d'un co-auteur)>
```

---

## ⚙️ 4. Quelle Procédure Suivre à Chaque Invocation de `/briefing` ?

1. **Lire la sous-note de briefing** (`notes/Briefing <Projet> <YYYY MM DD>.md`) et vérifier en direct l'état de l'étude / du dépôt.
2. **Mettre à jour la sous-note dans le coffre** avec les sources primaires originales.
3. **Générer ou mettre à jour l'artéfact `/draft` (`doc-version`)** pour les composants Loop Teams (`virtual_draft_briefing_*.md`) et, s'il y a un courriel d'accompagnement court (ex. pour prévenir par mail que le draft WIP est sur Overleaf et que le détail est dans les composants Loop sur Teams), appliquer strictement [`email-style/SKILL.md`](file:///c:/Users/hjamet/Documents/VoiceNotes/_agents/skills/email-style/SKILL.md) (2–3 paragraphes courts, zéro chiffre lourd dans le mail, ton direct adapté à Yash et Pamela).
4. **Restituer à Henri** avec les liens en tête : note maîtresse, sous-note de briefing et artéfact(s) `/draft`.
