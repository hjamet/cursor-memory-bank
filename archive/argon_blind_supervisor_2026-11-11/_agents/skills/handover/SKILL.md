---
name: handover
description: "Génération chirurgicale d'un prompt de passation (handover) auto-suffisant dans un bloc Markdown à 4 backticks pour relayer et reprendre une mission complexe dans une nouvelle conversation sans perte de contexte. Trigger sur /handover ou /handhover."
---

# Comment Générer un Prompt de Passation (Handover) Auto-Suffisant ?

Ce skill formalise la procédure pour synthétiser fidèlement l'état exact d'une session de travail complexe ou au long cours, et produire un prompt de passation (**handover**) autonome, clair et immédiatement exploitable par un nouvel agent démarrant une nouvelle conversation.

> [!IMPORTANT]
> ### ⚡ Invariant d'Encapsulation : La Règle des 4 Backticks (````markdown)
> Le prompt de passation généré contient fréquemment des blocs de code internes (commandes shell, extraits Python/TypeScript, diffs, diagrammes Mermaid, JSON).
> Pour éviter que les délimiteurs Markdown à 3 backticks (` ``` `) internes ne ferment prématurément le bloc d'affichage dans le chat, **le prompt de passation DOIT être rigoureusement enveloppé dans un bloc de code à 4 backticks** :
> ````text
> ````markdown
> [Contenu intégral du handover avec ses blocs internes à 3 backticks]
> ````
> ````

---

## 🎯 Quand Utiliser ce Skill ?

- **Déclenchement exclusif** : Uniquement et expressément lorsque l'utilisateur tape `/handover` ou `/handhover`.
- Aucun déclenchement automatique ni implicite.

---

## 🤝 Philosophie de Passation : D'Ingénieur à Ingénieur

Le prompt de passation n'est pas un rapport administratif lourd ni une accumulation de preuves à charge. Il se conçoit comme **une passation directe entre deux ingénieurs pairs** :
> *« Moi j'étais en train de faire ceci, voici notre perspective d'ensemble, voici le protocole qu'on suivait, voici où on en était, les anomalies qu'on a repérées, et voilà ce que tu dois prendre en charge pour continuer. »*

- **Pas de redite des règles générales du coffre** : Le nouvel agent possède déjà ses règles système dans son prompt. Inutile de gaspiller du contexte à lui réciter les règles de sous-agents, de zero-trust ou de superviseur aveugle.
- **Pas de preuves superflues a priori** : Le nouvel agent ira vérifier lui-même sur le terrain (fichiers, git, base de données).
- **Concentration sur l'action, l'état réel et la vision** : Ce qui compte, c'est la clarté du but, l'explication des choix récents, les fichiers touchés et la suite logique du plan.

---

## 📋 Quelle Est la Structure Canonique du Prompt de Passation ?

Le prompt produit doit comporter les sections suivantes :

### 1. 🎯 Perspective Générale & But de Fond
- Quel est l'objectif macroscopique du projet / de l'étude / du chantier en cours ?
- Pourquoi ce travail est-il réalisé (enjeux, échéances, contexte de recherche ou de production) ?
- Lien direct vers la note maîtresse Obsidian associée dans le coffre (`file:///...`).

### 2. 🧭 Protocole Méthodologique Adopté
- Comment procédait-on jusqu'à présent ? Quelle était notre approche méthodologique globale ?
- Quelle est la boucle de travail ou la démarche suivie (ex: audit ➔ test ➔ remontée ➔ correctif ➔ re-test) ?
- Les partis-pris ou directives spécifiques données par Henri pour cette mission.

### 3. 🏗️ Opérations Récentes & Derniers Sous-Agents Déployés
- Résumé chronologique des dernières opérations concrètes : qu'est-ce qui a été fait, tenté ou découvert ?
- Rôle et bilan des derniers sous-agents lancés (qui a fait quoi, ce qui a fonctionné, ce qui a été interrompu ou laissé en suspens).
- État des lieux git et système :
  - Commits en production vs commits poussés non déployés vs worktrees actifs.
  - État des conteneurs, services ou environnements distants.

### 4. 📂 Fichiers Clés du Chantier
- Liste explicite des **fichiers et répertoires les plus importants** sur lesquels le travail était en cours (chemins absolus, rôle de chaque fichier dans le problème ou le correctif).

### 5. 🔍 Problèmes & Anomalies Identifiés (Diagnostic Actuel)
- Quels sont les points de friction, bugs, erreurs ou comportements anormaux repérés ?
- Où en était-on dans leur compréhension ou leur résolution ?

### 6. 🚀 Feuille de Route Immédiate pour la Relève
- Que doit faire le nouvel agent dès qu'il prend la main ?
- Les prochaines étapes ordonnées et concrètes.
- Les critères de succès ou de terminaison clairs (quand le travail sera considéré comme réellement terminé).

---

## 🛠️ Protocole de Génération Pas à Pas pour l'Agent

Lorsque l'utilisateur saisit `/handover` ou `/handhover` :

1. **Relever l'état des lieux** :
   - Lire `_agents/project_diffs/🤖 <Titre>.md` (diff cumulatif `doc-version` depuis la dernière baseline validée par Henri) ainsi que la Note Maîtresse (dont `## 🚀 Quelles Sont les Prochaines Étapes ?`) et les artefacts de session.
   - Identifier les fichiers récents modifiés, les commits et les branches/worktrees.
2. **Rédiger le prompt de passation** :
   - Structurer le texte selon les 6 sections canoniques ci-dessus, avec un ton franc, direct et sans verbiage superflu.
3. **Encapsuler strictement dans 4 backticks (` ````markdown `)** et afficher dans la réponse.
