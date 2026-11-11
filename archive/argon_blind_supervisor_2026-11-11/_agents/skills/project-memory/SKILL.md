---
name: project-memory
description: Pilotage CLI des priorités de projets Obsidian et régulation de charge Pomodoro.
aliases:
  - project-memory
---
# Comment Fonctionne et se Pilote le Plugin Project Memory CLI ?

Ce skill documente l'utilisation complète de l'interface en ligne de commande `project_memory_cli.py` pour interagir avec le plugin Obsidian **Project Memory** du coffre Obsidian de Henri Jamet.

> [!IMPORTANT]
> ### ⚡ Dérogation Formelle d'Exécution CLI pour le Superviseur Racine ($P=0$)
> Par dérogation formelle aux règles générales de `_agents/rules/superviseur-aveugle.md`, le Superviseur Racine ($P=0$) est exclusivement habilité à exécuter en direct via `run_command` les commandes CLI suivantes :
> 1. `list` (avec ses options `--top`, `--reviewed`, `--unreviewed`, `--json`) et `dashboard` (régénération complète de `🎯 Projets.md` et des quotas)
> 2. `status-work` (avec ou sans `--all` ou ciblage)
> 3. `get "<Projet>"` (extraction des détails et métriques)
> 4. `feedback "<Projet>" <action> [--transcript auto]` (enregistrement rétrospectif et bilan)
> 5. `set-score "<Projet>" <score>` (calibrage direct de priorité)
> 6. `stop-work` (interruption manuelle optionnelle)
> 
> **TABLEAU DE BORD ZÉRO-TOKEN (`🎯 Projets.md` & alias `pm`)** : À chaque exécution de `project_memory_cli.py` (ainsi que via la sous-commande `dashboard` ou l'alias PowerShell `pm`), le fichier `c:\Users\hjamet\Documents\VoiceNotes\🎯 Projets.md` est automatiquement régénéré à la racine du coffre avec l'intégralité des projets actifs triés par priorité utilisateur, la flèche d'évolution de la priorité de base (`🟢 ↑`, `🔴 ↓`, `➖` par rapport à sa dernière valeur), des **liens relatifs à la racine du coffre** vers les notes principales (cliquables dans Antigravity et Obsidian) et les liens 1-clic vers les artefacts `[🤖 N](file:///...)`. Lors de l'appel de `pm` (`dashboard`), une **barre de progression visuelle en direct** affiche les projets synchronisés et met en évidence ceux qui ont avancé (livrables prêts à revoir).
> **AUCUNE OBLIGATION DE LANCER `work`** : Le Superviseur Racine ne lance plus de commande de fond bloquante ni d'alarme intrusive. Le travail s'effectue librement et la comptabilisation s'opère rétrospectivement exclusivement lorsque Henri invoque le skill `project-memory`.
> **AUCUNE AUTRE COMMANDE N'EST AUTORISÉE** : aucune création de script scratch, aucun code inline python -c, aucun build, aucun test.
> **Zéro sous-agent pour le triage /project-memory** : le Superviseur Racine exécute directement `status-work` et `list --top 10` pour afficher le tableau de bord en < 2s.

---

## 📍 Quels Sont les Chemins d'Accès Clés du Système ?

- **Tableau de Bord Racine (0 token)** : `c:\Users\hjamet\Documents\VoiceNotes\🎯 Projets.md` (régénéré automatiquement à chaque appel CLI ou via l'alias PowerShell `pm`)
- **Script CLI Python** : `c:\Users\hjamet\Documents\VoiceNotes\_agents\scripts-for-skills\project_memory_cli.py`
- **Fichier de Données JSON** : `c:\Users\hjamet\Documents\VoiceNotes\.obsidian\plugins\project-memory\data.json`
- **Racine du Vault Obsidian** : `c:\Users\hjamet\Documents\VoiceNotes`
- **Plugin Obsidian** : `c:\Users\hjamet\Documents\VoiceNotes\.obsidian\plugins\project-memory\`

---

## 🧮 Comment Fonctionne l'Algorithme Mathématique de Scoring & Priorisation ?

Chaque projet actif est représenté par une note Markdown dans le coffre comportant un tag de projet (ex: `#todo` ou `#project`) et **ne comportant pas** le tag d'archivage (`#done`).

Le score effectif d'un projet détermine sa priorité dynamique dans les révisions. Il est rigoureusement **confiné dans l'intervalle $[1.0, 100.0]$** via une combinaison affine convexe :

$$S_{\text{eff}} = \max\left(1.0,\, \min\left(100.0,\, S_{\text{pre}} - M_{\text{temporal}}(K)\right)\right)$$

avec :

$$S_{\text{pre}} = S_{\text{base}} + B_{\text{rot}} + U_{\text{temporal}}$$
$$U_{\text{temporal}} = \max\left(0.0,\, 100.0 - (S_{\text{base}} + B_{\text{rot}})\right) \times P_{\text{eff}}$$
$$P_{\text{eff}} = \max\left(P_{\text{deadline}},\, P_{\text{milestone}}\right) \in [0.0,\, 1.0]$$

> [!NOTE]
> **Propriété de Combinaison Convexe Bornée à 100.0** :
> En posant $S_{\text{rot}} = S_{\text{base}} + B_{\text{rot}} \le 100.0$, le score pré-malus s'écrit comme la combinaison convexe :
> $$S_{\text{pre}} = (1 - P_{\text{eff}}) \times S_{\text{rot}} + P_{\text{eff}} \times 100.0$$
> Puisque $S_{\text{rot}} \le 100.0$ et $P_{\text{eff}} \in [0.0, 1.0]$, on a mathématiquement $S_{\text{pre}} \le 100.0$. Le score effectif après déduction du malus temporel reste ainsi strictement borné supérieurement par $100.0$ et inférieurement par $1.0$.

### Quelles Sont les Composantes Mathématiques du Calcul ?

1. **Base Score ($S_{\text{base}}$)** : Valeur de base initiale (par défaut `100.0` ou fixée de `1.0` à `100.0`). Modifiée par les feedbacks utilisateur via la formule de rapprochement ($\text{facteur rf} = 0.2$) :
   - `more-often` / `emergency` (Friction / Urgence accrue) : $S_{\text{new}} = S + \text{rf} \times (100.0 - S)$
   - `less-often` (Aisance / Espacement) : $S_{\text{new}} = S - \text{rf} \times (S - 1.0)$
   - `ok` (Rythme nominal) : $S_{\text{new}} = S$ (maintien du score de base)
   - `finished` (Projet terminé) : Score ramené à $0.0$ (archivage avec tag `#done` et purge de `data.json`)
   - `non-projet` : Tags `#todo` / `#project` retirés et projet purgé de `data.json`

2. **Bonus de Rotation ($B_{\text{rot}}$) — Modèle d'Achille et la Tortue** :
   Le bonus de rotation favorise la découverte, la régularité et l'alternance équilibrée du portefeuille en évitant tout emballement :
   $$\Delta B = \alpha \times (100.0 - S_{\text{rot}}) \times \text{ratio}$$
   avec :
   - $S_{\text{rot}} = \min(100.0, S_{\text{base}} + B_{\text{rot}})$ : score courant intégrant le bonus accumulé.
   - $\alpha = \text{achillesAlpha}$ : paramètre de réglage (valeur par défaut `0.01` dans `settings`).
   - $\text{ratio} = \frac{T_{\text{elapsed}}}{T_{\text{target}}} \in [0.0, 1.0]$ : ratio d'accomplissement de la session de travail effectuée sur un **autre** projet.
   - **Garantie de Borne 100.0 & Dynamique Asymptotique** : L'incrément comble une fraction $\alpha \times \text{ratio}$ de l'écart restant jusqu'à 100.0. Le bonus est plafonné préventivement par $B_{\text{rot}} \le 100.0 - S_{\text{base}}$, garantissant $S_{\text{rot}} \le 100.0$. Plus un projet est prioritaire ($S_{\text{rot}} \to 100.0$), plus le gain se tasse (paradoxe d'Achille et la Tortue). Un projet dormant comble régulièrement la distance pour remonter naturellement sans jamais déborder.
   - **Amortissement lors du travail sur le projet** :
     - Si $\text{ratio} \ge 0.8$ : réinitialisation complète $B_{\text{rot}} \leftarrow 0.0$.
     - Si $\text{ratio} < 0.8$ : amortissement proportionnel $B_{\text{rot}} \leftarrow \max(0.0, B_{\text{rot}} \times (1.0 - \text{ratio}))$.

3. **Pression de Deadline ($P_{\text{deadline}}$) — Régime Stratégique vs Sprint Tactique ($J \le 7$)** :
   Calculé automatiquement si la note possède un champ frontmatter `deadline` ou `due` (ex: `deadline: 2026-10-18`), avec $\Delta t = \text{daysRemaining}$ :
   - **Régime Stratégique Moyen/Long Terme ($\Delta t > 7$ jours)** :
     $$P_{\text{deadline}} = \exp(-0.1 \times \Delta t)$$
     Décroissance exponentielle douce avec constante de temps de 10 jours.
   - **Régime de Sprint Tactique ($\Delta t \le 7$ jours)** :
     $$P_{\text{deadline}} = 0.75 + 0.25 \times \frac{7 - \Delta t}{7}$$
     À $J = 7$, $P_{\text{deadline}} = 0.75$ (au lieu de $\approx 0.496$), matérialisant une bascule nette vers l'urgence opérationnelle.
     Pour $\Delta t \le 0$ (le jour même ou échéance dépassée), $P_{\text{deadline}} = 1.0$ (urgence maximale absolue).

4. **Pression de Jalon Synchrone ($P_{\text{milestone}}$)** :
   Un jalon est exclusivement un rendez-vous synchrone avec un tiers (réunion, oral, supervision), jamais une étape interne de code ou de rédaction (qui relève des tâches AIVC). Calculé si la note comporte une réunion réelle planifiée (`milestone: "mercredi"`, `milestone: "2026-09-16"`, cron ou ISO ; champ absent sinon) :
   $$P_{\text{milestone}} = \exp(-0.3 \times \Delta t_{\text{milestone}})$$
   Si le jalon a été validé pour le cycle courant (`lastSatisfiedMilestoneDate`), $P_{\text{milestone}} = 0.0$.

5. **Enveloppe Non-Cumulative & Urgence Temporelle ($U_{\text{temporal}}$)** :
   $$P_{\text{eff}} = \max(P_{\text{deadline}},\, P_{\text{milestone}})$$
   $$U_{\text{temporal}} = \max(0.0, 100.0 - (S_{\text{base}} + B_{\text{rot}})) \times P_{\text{eff}}$$
   L'enveloppe retient la pression temporelle maximale sans les additionner, évitant l'hypertrophie des scores.

6. **Malus Temporel de Récence ($M_{\text{temporal}}(K)$)** :
   Évite qu'un projet récemment travaillé ne monopolise la tête de liste :
   $$M_{\text{temporal}}(K) = K \times \text{rf} \times w \times \max(0.0, S_{\text{pre}} - 1.0)$$
   - $K = \sum_i r_i \times \max\left(0,\, 1.0 - \frac{\Delta t_i}{6.0}\right)$ sommé sur les sessions des 6 dernières heures ($\Delta t_i < 6.0$ h) dans `recentWorkDates`.
   - $\text{rf} = 0.2$ (facteur de rapprochement) et $w = 0.5$ (`recencyPenaltyWeight`).
   - Le malus $K$ est strictement réservé aux sessions de travail réelles d'Henri.

7. **⚡ DIRECTIVE DRY MAJEURE : Source Unique de Vérité en Python & Consommation Unifiée** :
   > [!IMPORTANT]
   > **PRINCIPE DON'T REPEAT YOURSELF (DRY) UNIVERSEL** :
   > - **Autorité Canonique Unique** : Le script Python `project_memory_cli.py` constitue l'**unique source de vérité algorithmique** du coffre pour toutes les formules de calcul ($S_{\text{eff}}$, Achille & Tortue, sprint tactique, parseur de jalons, malus temporel $K$).
   > - **Interdiction Formelle de Duplication** : Aucune duplication ni réimplémentation divergente des formules dans le code TypeScript/JavaScript du plugin Obsidian ou dans des scripts satellites.
   > - **Persistance & Consommation Unifiée** : À chaque exécution, le CLI recalcule et persiste les scores effectifs dans `data.json` (`stats.projects[...].effectiveScore`). Les interfaces graphiques (StatsView, barre latérale, modales) consomment directement ces valeurs persistées ou délèguent à l'exécutable CLI sans recalcul local discordant.

8. **Paramètres de Configuration (`settings` dans `data.json`)** :
   | Paramètre | Défaut | Rôle |
   |---|---|---|
   | `achillesAlpha` | `0.01` | Facteur d'amortissement asymptotique du modèle d'Achille et la Tortue pour la rotation ($\Delta B$). |
   | `rotationBonus` | `0.3` | Incrément nominal legacy conservé pour rétro-compatibilité. |
   | `rapprochmentFactor` | `0.2` | Facteur de rapprochement $\text{rf}$ pour les feedbacks et le malus. |
   | `recencyPenaltyWeight` | `0.5` | Poids $w$ du malus temporel de récence dégressif sur 6h. |
   | `pomodoroDuration` | `60` | Durée nominale officielle en minutes d'une session de travail Pomodoro. |
   | `deadlineProperty` | `deadline` | Clé YAML frontmatter pour la date limite dure. |
   | `milestoneProperty` | `milestone` | Clé YAML frontmatter pour les réunions et jalons synchrones. |
   | `projectTags` | `todo, project` | Tags identifiant les projets actifs. |
   | `archiveTag` | `done` | Tag d'archivage des projets finalisés. |

9. **⚖️ Règle Fondamentale de Distinction : Retours Utilisateur & Sessions de Travail (`feedback`) vs Veille & Ajustements Agent (`set-score`)** :
   - **1. Retours Utilisateur & Sessions de Travail Réelles (`feedback "<projet>" <action>`)** :
     * Déclenché **exclusivement lorsque Henri invoque le skill project-memory** pour clore sa session ou formuler une consigne explicite de feedback (interdiction formelle de déclarer soi-même une fin de session ou de lancer un bilan de sa propre initiative).
     * **Obligation d'Interrogation Interactive Conditionnelle (`ask_question`)** : Antigravity ne doit pas appliquer de mutation unilatérale arbitraire. Lors de l'invocation de `project-memory` par Henri pour clore la session, Antigravity **appelle `ask_question`** pour recueillir le niveau de stress / confort réel d'Henri parmi les 4 options canoniques : `["À l'aise", "OK", "Stressé", "Terminé"]` (avec le suffixe ` (Recommandé)` apposé sur l'option suggérée selon l'analyse de marge calendaire), **UNIQUEMENT si Henri n'a pas déjà précisé son ressenti dans sa demande** (ex: `/project-memory ok`, « je suis à l'aise »). Interdiction formelle et absolue de déclencher `ask_question` de ressenti hors de cette invocation.
     * **🚫 INTERDICTION FORMELLE EN PHASE DE CONSULTATION / TRIAGE (`/project-memory`)** : Il est STRICTEMENT INTERDIT de déclencher l'outil modal `ask_question` lors d'une simple consultation, d'une invocation `/project-memory` ou pour demander à Henri sur quoi travailler. Antigravity DOIT TOUJOURS afficher d'abord en texte clair dans le chat le tableau visuel complet des priorités, échéances et contextes. Le choix du sujet s'effectue par dialogue naturel dans le chat.
     * **Enregistre la session de travail réelle** : ajoute automatiquement le timestamp UTC dans `recentWorkDates` pour appliquer le malus temporel $K$ anti-effet-tunnel dégressif sur 6 heures ($M_{\text{temporal}}(K)$), calculé via `--transcript auto` qui ventile désormais automatiquement la durée par projet lors d'une session multi-projets à partir des clés `Projet :`, `main_project_file` et des liens de notes maîtresses de chaque tour (sans nécessiter de découpage manuel `--duration`).
     * **Valide le jalon synchrone** : met à jour `lastSatisfiedMilestoneDate = now` si la session correspond à l'échéance.
     * **Gère la rotation des projets** : réinitialise ou amortit le bonus de rotation $B_{\text{rot}}$ du projet et applique le modèle d'Achille et la Tortue aux autres projets actifs.
     * Met à jour `lastReviewDate`, le score de base ($S_{\text{base}}$) et l'historique (`reviewHistory`).
     * Commande canonique : `python project_memory_cli.py feedback "<projet>" <action> --transcript auto` (ventilation multi-projets automatique intégrée).
   - **2. Veille, Triage & Ajustement de Priorités par l'Agent (`set-score "<projet>" <score_1_100>`)** :
     * Déclenché **quand l'Agent met à jour / ajuste des priorités ou effectue de la veille** (veille matinale, cycles Dream Vague 2 & Vague 3, qualification du portefeuille `0 unreviewed`, ou quand Henri demande dans le chat hors session de travail « rends ce projet plus urgent / augmente la prio »).
     * **L'Agent NE DOIT PAS utiliser `feedback`** (pour ne pas simuler une fausse session de travail d'Henri).
     * **L'Agent DOIT utiliser `set-score "<projet>" <score_1_100>`** (qui définit directement le score de base sans altérer `recentWorkDates` ni imposer de malus $K$).
     * **Garanties Système de `set-score`** :
       - `recentWorkDates` reste **strictement inchangé** ($K = 0.0$, aucun malus temporel indu).
       - `lastSatisfiedMilestoneDate` reste **strictement inchangé** (aucun jalon futur validé par erreur).
       - Le `rotationBonus` ($B_{\text{rot}}$) **du projet ciblé est réinitialisé à `0.0`** afin que son score pré-échéance $S_{\text{rot}}$ corresponde exactement au `<score_1_100>` demandé, tandis que les bonus de rotation $B_{\text{rot}}$ des **autres projets** restent strictement inchangés.
       - Met à jour le score de base ($S_{\text{base}}$), `lastReviewDate` et incrémente `totalReviews`.
     * Pour clore un projet terminé ou requalifier une note sans livrable lors de la veille : `feedback "<projet>" finished` ou `feedback "<projet>" non-projet`.

10. **Ordre de Priorité & Évaluation Initiale Obligatoire** :
   - Les **nouveaux projets non révisés** (`totalReviews == 0`) font l'objet d'une **évaluation initiale obligatoire** via le Protocole Dual-Track : exploration contextuelle (Obsidian, Spark) par sous-agents et attribution d'un score explicite de $1.0$ à $100.0$ avec `set-score`, jusqu'à ce qu'il reste 0 projet non révisé (`0 unreviewed`).
   - Les **projets déjà révisés** (`totalReviews > 0`) sont classés par `Effective Score` décroissant (`list --reviewed`).

11. **Gestion des Échéances & Jalons (`deadline` & `milestone`) & Règle Fondamentale de Distinction** :
   - **`deadline:` (Date Limite Dure)** :
     - Applicable à **tout projet ayant une échéance réelle et contraignante** : soumissions d'articles académiques (TheWebConf, AAAI, CSUR, FAccT, AAMAS), rapports d'activité ou de subventions (ex: HEC Research Fund), démarches légales/administratives (ex: permis de séjour), ou engagements contractuels fermes.
     - **Zéro restriction de domaine** : Les deadlines ne sont en aucun cas réservées aux seuls articles scientifiques. En revanche, les projets créatifs, personnels ou de fond sans contrainte temporelle externe (ex: JDR Asharde) ne requièrent pas de deadline artificielle.
     - Format ISO obligatoire : `YYYY-MM-DD` (ex: `deadline: 2026-10-18` ou `due: 2026-10-18`).
     - Sert de base mathématique de calcul pour l'urgence d'échéance $U_{\text{temporal}}$ via $P_{\text{deadline}}$ (avec régime de sprint à $J \le 7$).
   - **`milestone:` (Jalon Synchrone avec un Tiers)** :
     - **Définition stricte** : Réservé **exclusivement aux rendez-vous synchrones avec des tiers** (réunion DLLP, comités, oraux, entretiens de supervision). Ne représente **JAMAIS** une étape d'avancement interne, un objectif de code ou de rédaction (qui relèvent de la section `## 🚀 Quelles Sont les Prochaines Étapes ?` de la Note Maîtresse). Si aucune réunion synchrone n'est planifiée, le champ `milestone:` est **simplement absent du frontmatter** (ex: un renouvellement administratif ou un développement n'a qu'une `deadline:` dans le frontmatter et ses prochaines étapes dans la Note Maîtresse, zéro `milestone:`).
     - **Formats supportés** :
       * *Date fixe* : `milestone: 2026-08-28` ou `milestone: "2026-08-28"` (réunion ponctuelle, oral).
       * *Jour récurrent* : `milestone: "mercredi"` ou `milestone: "lundi"` (synchronisation hebdomadaire régulière).
       * *Périodicité paramétrée* : `milestone: "mercredi@3"` ou `milestone: "lundi@2"` (réunion toutes les $N$ semaines).
     - **Champ descriptif optionnel (`next_milestone:`)** : Phrase synthétique contextualisant l'objet du jalon (ex: `next_milestone: "Réunion DLLP le mercredi 26 août 2026"`).
   - **🚫 INTERDICTION D'ÉCHÉANCES PASSÉES** :
     - Les dates antérieures à la date actuelle (< date du jour) sont des **dates d'historique, de réception de documents ou d'événements passés**, JAMAIS des échéances ou des jalons.
     - Ne **JAMAIS lister d'événement passé dans les colonnes ou timelines d'échéances** ou dans les champs frontmatter `deadline:` / `milestone:`. Les dates passées doivent être consignées dans le corps de la note (section historique/contexte) et non en tant qu'échéances actives.

---

## 🧠 Comment S'Articule le Protocole de Gestion de la Charge Cognitive & Interrogation Interactive du Stress ?

Antigravity a pour mission fondamentale de préserver la sérénité et l'énergie cognitive d'Henri en adaptant dynamiquement l'agenda et la granularité d'accompagnement via une écoute active et interactive de son ressenti réel.

### 1. Pourquoi l'Interrogation Interactive (`ask_question`) Est-elle une Obligation Stricte ?
> [!IMPORTANT]
> **OBLIGATION STRICTE D'INTERROGER HENRI SUR SON NIVEAU DE STRESS / CONFORT** :
> - **Antigravity NE DOIT JAMAIS appliquer de mutation unilatérale arbitraire de feedback sans interroger Henri.**
> - **STRICTEMENT RÉSERVÉ À L'INVOCATION DE `project-memory` PAR HENRI** : L'outil modal `ask_question` de ressenti n'est appelé QUE lorsque Henri invoque expressément le skill `project-memory` pour clore la session (et si son ressenti n'est pas déjà précisé dans sa demande). Interdiction formelle et absolue de poser la question de ressenti de soi-même en cours de travail, à la complétion d'une tâche, ou d'auto-déclarer une fin de session.
> - **🚫 INTERDICTION FORMELLE EN PHASE DE CONSULTATION / TRIAGE (`/project-memory`)** : Il est STRICTEMENT INTERDIT d'utiliser la modal `ask_question` lors d'une simple consultation ou pour le choix de projet. La modal masque le visuel du tableau de bord et prive Henri de la visibilité sur ses priorités. Le choix du projet s'effectue par dialogue naturel dans le chat.
> - L'interrogation doit comporter **strictement les 4 options canoniques dans l'ordre suivant** :
>   1. `À l'aise` (ou `À l'aise (Recommandé)`)
>   2. `OK` (ou `OK (Recommandé)`)
>   3. `Stressé` (ou `Stressé (Recommandé)`)
>   4. `Terminé` (ou `Terminé (Recommandé)`)
> - Le suffixe ` (Recommandé)` est **obligatoirement apposé sur l'unique option conseillée** par Antigravity suite à l'analyse objective de la marge calendaire résiduelle.

### 2. Comment S'Évalue Objectivement la Recommandation (Marge Calendaire & Buffer 20-30%) ?
Avant de poser la question interactive via `ask_question`, Antigravity calcule l'option à recommander selon des critères factuels :
- **`Stressé (Recommandé)`** : Marge temporelle résiduelle avant deadline dure < 20-30%, point de blocage technique critique non résolu, dépendance externe bloquante, ou charge lourde imminente.
- **`OK (Recommandé)`** : Progression nominale, marge confortable (> 30%), rythme maîtrisé, pas de friction majeure.
- **`À l'aise (Recommandé)`** : Forte avance sur planning, livrables intermédiaires en avance, sujet totalement maîtrisé nécessitant un espacement au profit d'autres urgences.
- **`Terminé (Recommandé)`** : Tous les livrables du projet sont intégralement finalisés et validés.

### 3. Quelle Est la Matrice de Conversion & Son Impact sur la Priorisation ?

Dès qu'Henri sélectionne son option dans le prompt `ask_question`, Antigravity exécute la commande CLI correspondante (`feedback "<projet>" <action>`) :

| Option Sélectionnée | Action CLI Exécutée | Évolution du Score | Impact sur la Charge Cognitive & Priorisation |
| :--- | :--- | :--- | :--- |
| **`À l'aise`** | `feedback "<projet>" less-often` | Réduction de priorité : $S_{\text{new}} = S - 0.2 \times (S - 1.0)$ | **Allègement & Espacement** : Le projet est espacé dans la file pour libérer la bande passante cognitive sur les dossiers plus complexes. Horodate dans `recentWorkDates` et applique le malus $K$. |
| **`OK`** | `feedback "<projet>" ok` | Maintien du score : $S_{\text{new}} = S$ | **Rythme Nominal & Alternance Saine** : Progression conforme aux attentes. Horodate la session dans `recentWorkDates` (malus temporaire $M_{\text{temporal}}$) et applique $+0.3$ aux autres projets pour encourager la rotation. |
| **`Stressé`** | `feedback "<projet>" more-often` *(ou `emergency`)* | Hausse de priorité : $S_{\text{new}} = S + 0.2 \times (100.0 - S)$ | **Soutien Renforcé & Décompression** : Signal objectif de tension ou de retard. Le projet remonte en priorité pour qu'Antigravity prenne en charge les tâches lourdes et propose un découpage fin. Horodate dans `recentWorkDates`. |
| **`Terminé`** | `feedback "<projet>" finished` | Clôture : Score = $0.0$ (Tag `#done`) | **Libération Mentale Immédiate** : Le projet est archivé, taggé `#done` et purgé de la liste active dans `data.json`. La charge mentale associée est totalement évacuée. |

---

## 🚀 Quel Est le Répertoire Exhaustif des Commandes CLI ?

Toutes les commandes s'exécutent via l'interprète Python avec le chemin absolu du script :

```bash
python "C:\Users\hjamet\Documents\VoiceNotes\_agents\scripts-for-skills\project_memory_cli.py" <sous-commande> [options]
```

---

### 1. Comment Utiliser la Commande `list` pour Lister et Classer les Projets ?

Affiche la liste des projets actifs classés par priorité/urgence dynamique.

#### Quelle Est la Syntaxe ?
```bash
python "C:\Users\hjamet\Documents\VoiceNotes\_agents\scripts-for-skills\project_memory_cli.py" list [--top N | -n N] [--unreviewed] [--reviewed] [--clean-orphans] [--json]
```

#### Quelles Sont les Colonnes du Tableau CLI & de `🎯 Projets.md` ?
- `Title` : Titre du projet / nom de la note Obsidian (largeur dynamique sans troncature agressive, lien relatif encodé).
- `Eff.Score` / `Score` : Score effectif $S_{\text{eff}}$ calculé en temps réel (borné strictement dans $[1.0, 100.0]$).
- `Diff` : Badge cliquable `[🤖 N](_agents/project_diffs/%F0%9F%A4%96%20<Titre>.md)` ouvrant en 1 clic l'artéfact de diff cumulé `doc-version` du projet (généré dans `VoiceNotes/_agents/project_diffs/` et synchronisé par Obsidian Sync, avec conversion automatique des `[[wikilinks]]` en liens cliquables Antigravity) comparant la Note Maîtresse actuelle à la dernière baseline validée par Henri (`author="henri"`).
- `Base` : Score de base $S_{\text{base}}$ issu des feedbacks et évaluations.
- `Rot.Bonus` : Bonus de rotation $B_{\text{rot}}$ asymptotique d'Achille et la Tortue ($\Delta B = \alpha \times (100 - S_{\text{rot}}) \times \text{ratio}$).
- `Deadline Urg.` : Valeur ajoutée par l'urgence d'échéance $U_{\text{temporal}}$ (avec régime de sprint tactique à $J \le 7$).
- `Malus(K)` : Pénalité de récence temporelle déduite $M_{\text{temporal}}$ et coefficient d'activité récent $K$ (ex: `-6.2 (K=0.8)` ou `0.0 (K=0)`).
- `Deadline` : Date limite déclarée dans le frontmatter (`deadline` ou `due`).
- `Reviews` : Nombre total de révisions/sessions (`NEW` si non révisé).

#### Quelles Sont les Options Disponibles ?
- `--top N` ou `-n N` *(int)* : Limite l'affichage aux $N$ premiers projets les plus prioritaires (ex: `--top 5`).
- `--unreviewed` ou `--new` *(flag)* : Affiche uniquement les nouveaux projets en attente d'évaluation initiale (`totalReviews == 0`).
- `--reviewed` *(flag)* : Affiche uniquement les projets déjà révisés et classés par ordre d'urgence effectif.
- `--clean-orphans` *(flag)* : Purge automatiquement les projets orphelins de `data.json` avant de lister les projets actifs.
- `--json` *(flag)* : Génère un tableau JSON structuré contenant tous les détails calculés des projets (incluant `malus_temporal`, `k_recency`, `recent_work_count`).

#### Quels Sont les Exemples d'Utilisation ?
```bash
# Lister les 5 nouveaux projets à évaluer et les 5 projets révisés les plus urgents
python "C:\Users\hjamet\Documents\VoiceNotes\_agents\scripts-for-skills\project_memory_cli.py" list --top 5

# Obtenir uniquement les projets révisés au format JSON
python "C:\Users\hjamet\Documents\VoiceNotes\_agents\scripts-for-skills\project_memory_cli.py" list --reviewed --json
```

---

### 2. Comment Extraire les Détails d'un Projet avec `get` ?

Extrait l'ensemble des métriques d'un projet, le détail de ses sessions de travail récentes (`recentWorkDates`), ainsi que son historique de révisions. *(Le suivi de la feuille de route vit dans la section `## 🚀 Quelles Sont les Prochaines Étapes ?` de la Note Maîtresse et son diff cumulatif dans `_agents/project_diffs/🤖 <Titre>.md`).*

#### Quelle Est la Syntaxe ?
```bash
python "C:\Users\hjamet\Documents\VoiceNotes\_agents\scripts-for-skills\project_memory_cli.py" get "<project_path_or_name>" [--json]
```

#### Quelles Sont les Informations Affichées ?
- **Scores et Métriques** : $S_{\text{eff}}$, $S_{\text{base}}$, $B_{\text{rot}}$ (Achille & Tortue), $U_{\text{temporal}}$ ($P_{\text{deadline}}$, $P_{\text{milestone}}$), $M_{\text{temporal}}(K)$, $K$, deadline, nombre de révisions et dernière date de révision.
- **Sessions de Travail Récentes (`recentWorkDates`)** : Liste des sessions enregistrées dans les 6 dernières heures avec leur ancienneté $\Delta t$, la contribution pondérée à $K$, et l'impact sur le malus temporel.
- **Historique de Révision** : Les dernières actions consignées (`ok`, `more-often`, `less-often`, etc.) avec le score résultant.

#### Quels Sont les Arguments & Options ?
- `<project_path_or_name>` *(string)* : Chemin relatif dans le coffre (ex: `"Projets/MonProjet.md"`) ou titre/nom du fichier sans extension (ex: `"MonProjet"`). Le CLI prend en charge la résolution floue (fuzzy matching).
- `--json` *(flag)* : Renvoie l'intégralité des données du projet au format JSON structuré.

#### Quels Sont les Exemples d'Utilisation ?
```bash
python "C:\Users\hjamet\Documents\VoiceNotes\_agents\scripts-for-skills\project_memory_cli.py" get "Composer une musique pour orchestre"
```

---

### 3. Comment Enregistrer le Feedback Utilisateur & la Session de Travail avec `feedback` ?

Enregistre l'évaluation issue du retour recueilli via `ask_question` auprès d'Henri (ou consigne explicite dans la conversation) dans `data.json`, met à jour ses scores et son historique, horodate la session dans `recentWorkDates` (appliquant le malus $K$ dégressif sur 6h pour prévenir l'effet tunnel), recalcule et persiste les scores effectifs (DRY), et applique la rotation des bonus aux autres projets via le modèle d'Achille et la Tortue.

> [!IMPORTANT]
> **Règle d'Usage de `feedback`** :
> - **Réservé EXCLUSIVEMENT aux sessions de travail réelles** suite au retour recueilli interactivement via `ask_question` auprès d'Henri lors de l'invocation de `project-memory` (ou consigné suite à une demande explicite d'Henri dans la conversation).
> - **L'Agent NE DOIT PAS utiliser `feedback` lors de la veille ou du triage autonome** (utiliser `set-score` à la place).

#### Quelle Est la Syntaxe ?
```bash
python "C:\Users\hjamet\Documents\VoiceNotes\_agents\scripts-for-skills\project_memory_cli.py" feedback "<project_path_or_name>" <action> [--transcript auto | <path_to_transcript>]
```

#### Quelles Sont les Actions Disponibles ?
- `less-often` : Réduit la priorité du projet (sélection « À l'aise » : aisance constatée, avance sur planning, charge allégée).
- `ok` : Maintient le score actuel (sélection « OK » : rythme maîtrisé, session de travail nominale).
- `more-often` : Augmente la priorité du projet (sélection « Stressé » : friction détectée, marge faible, besoin de suivi rapproché).
- `emergency` : Augmente fortement la priorité (urgence critique).
- `finished` : Marque le projet comme terminé (sélection « Terminé » : score ramené à $0.0$, tag `#done` ajouté, purge de `data.json`).
- `non-projet` : Marque la note comme un **non-projet** (note de mémoire, résumé, pensée sans livrables ni feuille de route). Les tags `#todo` et `#project` sont retirés du frontmatter YAML et la note est purgée des projets actifs.

#### Comment Fonctionne la Prise en Charge Rétrospective de `--transcript` ?
L'option `--transcript [path_or_auto]` (avec `--transcript auto` par défaut recommandé) permet de calculer et consigner avec exactitude le temps de travail effectif sans aucun chronomètre de fond ni démon :
1. **Auto-Détection du Transcript Antigravity** : Avec `--transcript auto`, le CLI localise automatiquement le journal de la conversation active (`<appDataDir>\brain\<conversation-id>\.system_generated\logs\transcript.jsonl`).
2. **Comptage Strict des Messages Utilisateur Réels & Pondération par Flèches (`->` / `→`) et Commentaires d'Artéfacts (`Comment: "..."`)** : Le script filtre et comptabilise strictement les messages authentiques d'Henri (`USER_EXPLICIT` / saisies directes dans le chat). Pour chaque message utilisateur $m$, le script compte le nombre de flèches d'arguments $N_{\text{arrows}}(m)$ (`->` ou `→`) ainsi que le nombre de commentaires déposés directement sur des artéfacts $N_{\text{comments}}(m)$ (`Comment: "..."` avant `<USER_REQUEST>`), soit $N_{\text{args}}(m) = N_{\text{arrows}}(m) + N_{\text{comments}}(m)$, et crédite $\max(T_{\text{base}},\, 2 \times N_{\text{args}}(m))$ minutes de temps de travail effectif sans plafond (où $T_{\text{base}} = 6\text{ min}$ est le temps nominal d'un message simple et chaque flèche ou commentaire d'artéfact vaut **2 minutes** lorsque le total dépasse le temps habituel d'un message).
3. **Ventilation Multi-Projets Déterministe par Tour Humain & Watermark Anti-Double-Comptage (`lastCreditedStepByConv`)** : Lors d'une conversation couvrant plusieurs projets, `--transcript auto` découpe le journal en tours humains (`USER_EXPLICIT`), identifie automatiquement les projets suivis touchés (via les briefs `Projet : <chemin>`, les appels AIVC `main_project_file` et les liens de notes maîtresses) et ventile équitablement la durée de chaque tour sur le projet ciblé (avec affichage transparent du temps extrait vs temps total de conversation). De plus, chaque appel de `feedback --transcript auto` enregistre dans `data.json` le dernier `step_index` comptabilisé pour le couple `(conversation_id, projet)` (`lastCreditedStepByConv[conv_id]`) : si `feedback` est rappelé plusieurs fois au cours d'une même conversation, seuls les nouveaux tours postérieurs au marque-page (`step_index > last_step`) sont crédités.
4. **Immunité aux Commentaires d'Artéfacts & Bruits Système** : Les notifications d'outils, les validations internes de sous-agents et les messages générés par les artéfacts sont ignorés afin de garantir une métrique pure.
5. **Enregistrement Proportionnel dans `recentWorkDates`** : La durée cumulée $T_{\text{elapsed}}$ est enregistrée dans `recentWorkDates` avec son ratio proportionnel ($r = T_{\text{elapsed}} / T_{\text{target}}$), appliquant le malus temporel $M_{\text{temporal}}(K)$ dégressif sur 6h pour prévenir l'effet tunnel.
6. **Cumul dans les Statistiques Globales** : Le volume calculé est incrémenté dans `globalStats.totalPomodoroTime += T_elapsed`.

#### Quelle Est la Règle d'Interrogation Interactive du Ressenti ?
- **Ressenti Déjà Fourni par Henri** : Si Henri a déjà précisé son ressenti dans sa demande ou lors de l'invocation (ex: `/project-memory ok`, `/project-memory a l'aise`, ou « c'est bon, on a fini, je suis à l'aise »), l'agent **NE DOIT PAS appeler `ask_question`** et exécute directement la commande CLI avec l'action correspondante.
- **Ressenti Non Précisé** : L'outil modal `ask_question` n'intervient que si le ressenti n'a pas été formulé, strictement à la clôture de la session de travail.

#### Quel Est le Comportement Système de `feedback` ?
1. Met à jour le score de base $S_{\text{base}}$ et la date de dernière revue `lastReviewDate`.
2. Consigne l'entrée dans l'historique `reviewHistory`.
3. Ajoute automatiquement le timestamp UTC actuel dans `recentWorkDates` avec le temps calculé via `--transcript auto`.
4. Enregistre `lastSatisfiedMilestoneDate = now` pour valider le cycle de jalon.
5. Réinitialise le `rotationBonus` $B_{\text{rot}}$ du projet à **`0.0`** (si ratio nominal $\ge 0.8$) et incrémente le `rotationBonus` de **tous les autres projets actifs via le modèle asymptotique d'Achille et la Tortue ($\Delta B = \alpha \times (100 - S_{\text{rot}}) \times \text{ratio}$)**.
6. Recalcule et persiste immédiatement `effectiveScore` dans `data.json` selon le principe DRY.
7. Met à jour les statistiques globales (`totalReviews`, `totalPomodoroTime`, etc.).

#### Quels Sont les Exemples d'Utilisation ?
```bash
# Bilan de session avec calcul automatique du temps de conversation
python "C:\Users\hjamet\Documents\VoiceNotes\_agents\scripts-for-skills\project_memory_cli.py" feedback "MonProjet" ok --transcript auto

# Espacement de priorité suite au choix "À l'aise"
python "C:\Users\hjamet\Documents\VoiceNotes\_agents\scripts-for-skills\project_memory_cli.py" feedback "MonProjet" less-often --transcript auto

# Hausse de priorité suite au choix "Stressé"
python "C:\Users\hjamet\Documents\VoiceNotes\_agents\scripts-for-skills\project_memory_cli.py" feedback "MonProjet" more-often --transcript auto
```

---

### 4. Comment Calibrer la Priorité par l'Agent & Veille avec `set-score` ?

Définit directement le score d'urgence d'un projet ($1.0$ à $100.0$) et comptabilise la révision (`totalReviews`) **sans altérer `recentWorkDates` ni imposer de malus temporel $K$**.

> [!IMPORTANT]
> **Règle d'Usage de `set-score`** :
> - **OBLIGATOIRE pour l'Agent lors de toute action autonome de veille, de triage ou de réévaluation** (cycles Dream Vague 2 & Vague 3, veille matinale, qualification du portefeuille `0 unreviewed`).
> - **OBLIGATOIRE lors d'une demande d'Henri hors session de travail** (« rends ce projet plus urgent », « calibre ce projet à 80 »).
> - Permet d'ajuster précisément la priorité sans simuler de fausse session de travail d'Henri ($K = 0.0$, jalons futurs intacts, pas de rotation induite).

#### Quelle Est la Syntaxe ?
```bash
python "C:\Users\hjamet\Documents\VoiceNotes\_agents\scripts-for-skills\project_memory_cli.py" set-score "<project_path_or_name>" <score_1_100>
```

#### Quels Sont les Arguments & Options ?
- `<project_path_or_name>` *(string)* : Chemin relatif dans le coffre ou nom du projet.
- `<score_1_100>` *(float)* : Valeur numérique du score d'urgence entre `1.0` (faible priorité) et `100.0` (urgence maximale).

#### Quels Sont les Exemples d'Utilisation ?
```bash
# Évaluation initiale obligatoire d'un nouveau projet non révisé (0 unreviewed)
python "C:\Users\hjamet\Documents\VoiceNotes\_agents\scripts-for-skills\project_memory_cli.py" set-score "Digital Language Learning Platform" 95.0

# Réajustement de priorité par l'Agent lors de la veille Dream suite à la détection d'un email critique
python "C:\Users\hjamet\Documents\VoiceNotes\_agents\scripts-for-skills\project_memory_cli.py" set-score "TheWebConf 2027" 92.0
```

---

### 5. Comment Gérer et Mettre à Jour les Prochaines Étapes & le Diff d'un Projet via `doc-version` (`_agents/project_diffs/🤖 <Titre>.md`) ?

Conformément à [`task-tracking.md`](file:///c:/Users/hjamet/Documents/VoiceNotes/_agents/rules/task-tracking.md), la sous-commande legacy `complete-task` est obsolète. L'unique source de vérité du projet est sa **Note Maîtresse** (`notes/<Titre>.md`), qui se termine par la section **`## 🚀 Quelles Sont les Prochaines Étapes ?`** (où chaque tâche est listée sous forme `- [ ]` jamais cochée, avec wikilinks Obsidian `[[...]]` vers les notes et diffs liés), associée à son unique artéfact de diff cumulatif **`_agents/project_diffs/🤖 <Titre>.md`** généré par `doc-version` (`get_diff_artifact`) et synchronisé entre PC par Obsidian Sync.

> [!IMPORTANT]
> **CYCLE DE VALIDATION `author="henri"` ➔ MODIFICATIONS `author="agent"` ➔ DIFF `_agents/project_diffs/🤖 <Titre>.md`** :
> 1. **Baseline unique `author="henri"` (`_agents/doc_version_cas/`)** : Lorsqu'Henri valide l'état d'une note (en début de `/one-shot` avant traitement de ses commentaires, ou automatiquement lors d'un `feedback "<Projet>" <action>` humain sans `--agent`), `commit_document(..., author="henri")` scelle cette version comme nouvelle baseline de référence et purge automatiquement les anciens snapshots de cette cible (auto-compaction).
> 2. **Diff cumulatif anti-perte (`author="henri"` $\to$ état actuel)** : À chaque modification de la Note Maîtresse (ou d'une sous-note / d'un brouillon `virtual:<Sujet>`), `get_diff_artifact` écrase sur place `_agents/project_diffs/🤖 <Nom>.md` en comparant **toujours** l'état actuel à la dernière baseline `author="henri"` (et convertit à la volée tous les `[[wikilinks]]` et `![[images]]` en liens Markdown cliquables dans Antigravity).
> 3. **Interdiction d'appeler `ask_question` de ressenti** en cours de session (l'interrogation de ressenti et la clôture via `feedback` ne se font QUE si Henri invoque expressément le skill `project-memory`).

---

### 6. Comment Démarrer une Session Pomodoro Active & Pause avec `work` (Support Multi-Sessions Parallèles) ?

Démarre une session de travail Pomodoro sur un projet. La durée de la session est déterminée automatiquement par le paramètre `pomodoroDuration` configuré dans le fichier `data.json` du plugin (durée configurée par Henri dans les réglages Obsidian, actuellement 60 minutes / 1h), à moins qu'une durée spécifique ne soit fournie via l'option `--duration N`.

> [!TIP]
> **🚀 Support Natif des Sessions Pomodoro Parallèles** :
> - **Multi-Projets Simultanés** : Il est possible de lancer simultanément plusieurs sessions Pomodoro en arrière-plan pour des projets **distincts** (par exemple en alternant d'un chat ou d'un volet à l'autre sur deux projets en parallèle).
> - **Prévention des Doublons sur le Même Projet** : Si une session est déjà en cours pour le **même projet exact**, le CLI refuse le doublon et affiche un avertissement clair rappelant le PID existant et la commande pour l'interrompre.
> - **Architecture Multi-Sessions Rétrocompatible** : Les sessions actives sont stockées dans `.obsidian/plugins/project-memory/.active_pomodoro.json` et synchronisées dans `data.json`. Les deux fichiers exposent à la racine la session principale (`activeSession`) ainsi que le dictionnaire complet `activeSessions: { [rel_path]: sessionData }`, garantissant une interopérabilité descendante absolue avec tous les outils et composants de l'interface Obsidian.

> [!NOTE]
> **Utilitaire Optionnel de Chronométrage Manuel (`work`)** :
> La commande `work` est conservée uniquement comme un utilitaire manuel optionnel pour ceux qui souhaitent un chronomètre visuel de compte à rebours en console.
> **Elle n'est plus requise ni exécutée en tâche de fond par les agents Antigravity**, éliminant les processus d'arrière-plan bloquants et les interruptions intempestives. Le travail s'effectue librement et sans coupure, et la comptabilisation du temps réel est assurée rétrospectivement lors de la clôture via `feedback "<projet>" <action> --transcript auto`.

#### Quelle Est la Syntaxe ?
```bash
python "C:\Users\hjamet\Documents\VoiceNotes\_agents\scripts-for-skills\project_memory_cli.py" work "<project_path_or_name>" [--duration N]
```

#### Quels Sont les Arguments & Options ?
- `<project_path_or_name>` *(string)* : Chemin relatif dans le coffre (ex: `"Projets/MonProjet.md"`) ou titre/nom du fichier (résolution floue supportée).
- `--duration N` *(int)* : Durée personnalisée de la session Pomodoro en minutes (outrepasse la valeur `pomodoroDuration` de `data.json`).

#### Quel Est le Protocole de Clôture & Workflow d'Interaction ?
1. **Travail Fluide & Sans Démon** : Aucun démon `work` n'est lancé en arrière-plan pendant la session. Le travail se déroule sans contrainte ni réveil forcé.
2. **Protocole de Clôture de Session (Sur Invocation Explicite de `project-memory` par Henri Uniquement)** :
   1. **Synchronisation Ciblée de la Note Maîtresse, Sous-Notes & Portabilité Multi-Ordinateurs via `doc-version` (`_agents/project_diffs/🤖 <Titre>.md`)** :
      - **Mise à jour de la Note Maîtresse (`notes/<Titre>.md`) & Diff Cumulatif (`get_diff_artifact`)** : Mettre à jour la Note Maîtresse (et sa section narrative `## 🚀 Quelles Sont les Prochaines Étapes ?`, zéro `- [ ]` / `- [x]`) ainsi que les sous-notes éventuelles, puis régénérer `_agents/project_diffs/🤖 <Titre>.md` via `doc-version` (`get_diff_artifact`), synchronisé entre PC par Obsidian Sync. Vérifier que tout code modifié dans `~/Documents/code/` est commité et poussé (`git push`).
      - **Garantie de Relais Sans Perte** : Lorsqu'Henri reprend le projet (même sur un autre ordinateur via Obsidian Sync), la Note Maîtresse et `_agents/project_diffs/🤖 <Titre>.md` exposent immédiatement l'intégralité des modifications et prochaines étapes sans aucune perte de contexte.
   2. **Recueil du Ressenti & Feedback Rétrospectif** :
      - *Si Henri a déjà précisé son ressenti* (ex: `/project-memory ok`, « je suis à l'aise ») : appliquer directement `feedback "<projet>" <action> --transcript auto` sans appeler `ask_question`.
      - *Si non précisé* : interroger obligatoirement Henri via `ask_question` avec les 4 options canoniques `["À l'aise", "OK", "Stressé", "Terminé"]` (suffixe ` (Recommandé)` selon la marge objective), puis exécuter `feedback "<projet>" <action> --transcript auto`.
   3. **Clôture Définitive de la Conversation (Zéro Relance & Zéro Suggestion Suivante)** :
      - *Interdiction Formelle de Relance Automatique* : INTERDICTION FORMELLE ET ABSOLUE de relancer un Pomodoro automatiquement.
      - *Suppression des Projets Suivants* : Ne plus calculer ni recommander les 3 projets suivants. Clôturer proprement la conversation sans pousser à un enchanement compulsif.

#### Quel Est le Protocole d'Évaluation Autonome & Anti-Biais ?
Lors de la clôture d'une session de travail invoquée par Henri ou de l'émission d'une recommandation, Antigravity doit respecter une rigueur d'analyse stricte :

1. **Lutte contre le Biais de Confirmation & la Sycophancie (Anti-Sycophancy)** :
   - Bannir catégoriquement la validation aveugle, l'enthousiasme naïf ou les flatteries rassurantes (« Tout est parfait », « On a largement le temps »).
   - Ne jamais évaluer artificiellement un projet comme maîtrisé (`less-often` ou `ok`) si la marge opérationnelle réelle est étroite ou si des incertitudes majeures subsistent.

2. **Lutte contre le Nihilisme Optimiste & la Procrastination Passive** :
   - Rejeter formellement l'illusion selon laquelle « les retards se rattraperont magiquement à la dernière minute » ou « ce n'est pas grave de décaler ».
   - Les projets académiques et techniques majeurs (deadlines de conférences TheWebConf, FAccT, AAMAS, déploiements, protocoles éthiques, recrutements Prolific, modélisation LMM, rédaction Overleaf et révisions co-auteurs) comportent des dépendances séquentielles **strictement incompressibles**.

3. **Évaluation Lucide de la Marge Réelle avant Échéance (Deadline Margin Assessment)** :
   - Calculer le temps restant effectif en **jours ouvrés réels** jusqu'à l'échéance dure (`deadline`).
   - Quantifier la charge résiduelle de travail et les temps de latence externes incompressibles (ex: délais de passation des participants Prolific, cycles de relecture des directeurs Pamela/Yash, instruction institutionnelle).
   - **Règle du Seuil de Marge de Sécurité (Buffer 20-30%)** :
     - Si la marge temporelle résiduelle est **inférieure à 20-30% du temps total imparti**, ou si un point de blocage / dépendance externe critique est non résolu, le statut objectif DOIT IMPÉRATIVEMENT conduire à recommander **`Stressé (Recommandé)`** (hausse de priorité via `more-often`, découpage immédiat en micro-tâches gérées par l'IA et décharge cognitive renforcée).
     - Si la marge est supérieure à 30% avec une cadence maîtrisée : **`OK (Recommandé)`**.
     - Si le projet est très en avance sur le calendrier et risque de monopoliser du temps au détriment d'urgences réelles : **`À l'aise (Recommandé)`**.
     - Si tous les livrables sont définitivement finalisés : **`Terminé (Recommandé)`**.

#### Quels Sont les Exemples d'Utilisation ?
```bash
# Démarrer une première session de travail Pomodoro (ex: IA in Business)
python "C:\Users\hjamet\Documents\VoiceNotes\_agents\scripts-for-skills\project_memory_cli.py" work "Organisation du cours Artificial Intelligence in Business 2026"

# Démarrer simultanément une seconde session en parallèle (ex: DLLP)
python "C:\Users\hjamet\Documents\VoiceNotes\_agents\scripts-for-skills\project_memory_cli.py" work "Digital Language Learning Platform"

# Démarrer une session de 45 minutes avec durée spécifique
python "C:\Users\hjamet\Documents\VoiceNotes\_agents\scripts-for-skills\project_memory_cli.py" work "Digital Language Learning Platform" --duration 45
```

---

### 7. Comment Interrompre Proprement un Pomodoro avec `stop-work` ?

Permet d'interrompre proprement une session Pomodoro en cours (ou d'enregistrer manuellement une session partielle). Supporte le ciblage précis par projet ou l'interruption groupée.

Lors de l'interruption :
1. **Calcul du temps réel** : Calcule avec précision le temps écoulé $T_{\text{elapsed}}$ en minutes pour la session arrêtée.
2. **Statistiques globales** : Incrémente le temps global passé (`globalStats.totalPomodoroTime += T_elapsed`).
3. **Poids proportionnel** : Calcule le ratio d'accomplissement $r = \frac{T_{\text{elapsed}}}{T_{\text{target}}}$.
4. **Malus temporel proportionnel** : Enregistre la session dans `recentWorkDates` avec son ratio $r$, appliquant une pénalité de récence proportionnelle au temps réellement travaillé ($k_i = r \times (1.0 - \Delta t / 6.0)$).
5. **Bonus de rotation** : Amortit proportionnellement le bonus de rotation du projet travaillé ($B_{\text{rot}} \times (1 - r)$) et applique le modèle d'Achille et la Tortue ($\Delta B = \alpha \times (100 - S_{\text{rot}}) \times r$) aux autres projets.
6. **Validation de jalon** : Si $r \ge 0.5$, valide le jalon synchrone (`lastSatisfiedMilestoneDate = now`).
7. **Nettoyage sélectif** : Seule la session arrêtée est purgée du registre actif ; les autres sessions en parallèle continuent leur course sans perturbation.

#### Quelle Est la Syntaxe ?
```bash
# Interrompt une session spécifique ciblée par son nom ou chemin
python "C:\Users\hjamet\Documents\VoiceNotes\_agents\scripts-for-skills\project_memory_cli.py" stop-work "<project_path_or_name>"

# Interrompt la session unique (ou la session échue/la plus récente si plusieurs tournent)
python "C:\Users\hjamet\Documents\VoiceNotes\_agents\scripts-for-skills\project_memory_cli.py" stop-work

# Interrompt TOUTES les sessions Pomodoro actives simultanément
python "C:\Users\hjamet\Documents\VoiceNotes\_agents\scripts-for-skills\project_memory_cli.py" stop-work --all

# Enregistrement manuel d'une session partielle sans daemon actif
python "C:\Users\hjamet\Documents\VoiceNotes\_agents\scripts-for-skills\project_memory_cli.py" stop-work "NomDuProjet" --elapsed 12.5 --target-duration 35
```

#### Quels Sont les Arguments & Options ?
- `<project_path_or_name>` *(string, optionnel)* : Projet spécifique à interrompre.
- `--all`, `-a` *(flag)* : Interrompt simultanément l'ensemble des sessions Pomodoro actives en parallèle.
- `--elapsed`, `-e` *(float)* : Temps manuellement écoulé en minutes (outrepasse le chronomètre).
- `--target-duration`, `-d` *(float)* : Durée cible manuelle si enregistrement sans daemon actif.
- `--json` *(flag)* : Sortie au format JSON structuré.

---

### 8. Comment Connaître l'État des Sessions Pomodoro Actives avec `status-work` ?

Affiche la progression en temps réel de la session Pomodoro en cours (temps écoulé, temps restant, pourcentage avec barre visuelle `[██░░]`, PID du processus et commandes d'interruption). Supporte le filtrage strict par projet (isolation cognitive inter-chats) et l'affichage exhaustif de toutes les sessions parallèles via `--all`.

#### Quelle Est la Syntaxe ?
```bash
# Affiche la session active la plus récente (comportement par défaut, propre et sans dispersion)
python "C:\Users\hjamet\Documents\VoiceNotes\_agents\scripts-for-skills\project_memory_cli.py" status-work

# Isole strictement la session du projet cible (indispensable pour un agent travaillant dans un chat dédié)
python "C:\Users\hjamet\Documents\VoiceNotes\_agents\scripts-for-skills\project_memory_cli.py" status-work "<project_path_or_name>"

# Affiche l'ensemble exhaustif de toutes les sessions Pomodoro actives en parallèle
python "C:\Users\hjamet\Documents\VoiceNotes\_agents\scripts-for-skills\project_memory_cli.py" status-work --all

# Sortie au format JSON structuré
python "C:\Users\hjamet\Documents\VoiceNotes\_agents\scripts-for-skills\project_memory_cli.py" status-work [projet] [--all] [--json]
```

#### Quels Sont les Arguments & Options ?
- `<project_path_or_name>` *(string, optionnel)* : Cible un projet précis (titre ou chemin relatif) pour n'afficher **exclusivement** que sa session. Si le projet est actif, affiche sa progression sans mentionner les autres projets. Si aucune session n'est active pour ce projet précis, renvoie un statut `idle` propre. Cet argument est hautement recommandé pour les agents travaillant dans des fenêtres de chat parallèles.
- `--all`, `-a` *(flag)* : Force l'affichage simultané de toutes les sessions Pomodoro actives en parallèle sur la machine.
- `--json` *(flag)* : Renvoie l'état sous forme de JSON structuré (conforme à l'isolation demandée ou global si `--all`).

#### Quels Sont les Formats de Sortie ?
- **Mode Console** :
  - *Session unique ou ciblée par projet* : Encadré synthétique avec barre de progression, temps écoulé / restant, PID, et commande d'arrêt ciblée.
  - *Mode global (`--all` ou sessions multiples sans filtre)* : Liste détaillée numérotée pour chaque projet en cours avec sa barre propre, ses métriques individuelles, son PID, et le rappel des commandes d'arrêt sélective ainsi que `--all`.
- **Mode JSON (`--json`)** :
  - *Si projet ciblé* : Objet JSON dédié à la session unique du projet demandé.
  - *Si global / standard* : Objet unifié exposant la session principale à la racine (`pid`, `project`, `elapsed_minutes`, `remaining_minutes`, `progress_percent`) ainsi que le tableau complet `sessions: [...]` pour une interopérabilité descendante totale.

---

### 9. Comment Nettoyer les Projets Orphelins de `data.json` avec `clean-orphans` ?

Scanne le coffre pour détecter et purger de `data.json` toutes les entrées orphelines (fichiers supprimés, renommés ou n'ayant plus de tag `#todo` / `#project`).

#### Quelle Est la Syntaxe ?
```bash
python "C:\Users\hjamet\Documents\VoiceNotes\_agents\scripts-for-skills\project_memory_cli.py" clean-orphans [--dry-run] [--json]
```

#### Quels Sont les Arguments & Options ?
- `--dry-run` *(flag)* : Mode simulation. Liste les entrées orphelines détectées dans `data.json` sans modifier le fichier sur le disque.
- `--json` *(flag)* : Renvoie la liste des entrées nettoyées au format JSON.

#### Quels Sont les Exemples d'Utilisation ?
```bash
# Vérifier les projets orphelins sans altérer data.json
python "C:\Users\hjamet\Documents\VoiceNotes\_agents\scripts-for-skills\project_memory_cli.py" clean-orphans --dry-run

# Exécuter le nettoyage effectif
python "C:\Users\hjamet\Documents\VoiceNotes\_agents\scripts-for-skills\project_memory_cli.py" clean-orphans
```

---

## 🎯 Quel Est le Comportement Attendu Lors de l'Invocation Manuelle (`/project-memory`) ?

Lorsque Henri invoque manuellement le skill ou la slash-command `/project-memory`, Antigravity adapte son comportement selon le contexte temporel de la conversation :

### 1. Que Faire en Début de Conversation (Orientation & Choix de Focus) ?

* **Protocole CLI Direct & Zéro-Latence (< 2s) [Exécution Directe Racine P=0]** :
  Zéro sous-agent pour le triage /project-memory : le Superviseur Racine exécute directement :
  1. Vérifier le statut de session de travail active :
     ```bash
     python "_agents\scripts-for-skills\project_memory_cli.py" status-work --all
     ```
  2. Extraire immédiatement le tableau de bord des priorités (Top 10 par défaut) :
     ```bash
     python "_agents\scripts-for-skills\project_memory_cli.py" list --top 10
     ```
* **Consommation Directe de la Sortie Standard (Tableau Markdown Rendu, ZÉRO Bloc de Code)** :
  - Coller directement le **tableau Markdown GFM** généré par la commande `list` dans le message de chat **SANS JAMAIS l'entourer d'un bloc de code (````text` ou ````bash` strictement interdit)**, afin que tous les liens cliquables absolus `[Nom](file:///...)` vers les notes Obsidian et `[🤖 N](file:///...)` de la colonne `Diff` vers l'artefact `_agents/project_diffs/🤖 <Titre>.md` soient immédiatement rendus et cliquables dans le tableau.
* **Recommandations Stratégiques Motivées & Mise en Avant des Notes `🤖 <Titre>.md`** :
  - Formuler une analyse concrète et tranchée sur le focus le plus pertinent d'après les échéances du tableau et l'état réel des échanges récents, en **mentionnant systématiquement les artefacts `[🤖 <Titre>](file:///...)` les plus intéressants et importants** pour chaque option recommandée (résumé des modifications non revues et des prochaines étapes de la Note Maîtresse).
* **Échange Naturel dans le Chat** :
  - Laisser Henri arbitrer et réagir directement dans la conversation sur son choix de projet (l'outil modal `ask_question` est strictement réservé à la clôture de session lors de l'invocation explicite de `project-memory`).

### 2. Que Faire Lors de la Clôture de Session Demandée par Henri (Bilan & Clôture) ?
*Ce protocole s'applique EXCLUSIVEMENT lorsque Henri invoque expressément le skill `project-memory` pour clore la session. L'agent ne doit jamais le déclencher de sa propre initiative.*
* **Comptage du Transcript & Temps de Session** : Compter les messages utilisateur réels (`USER_EXPLICIT`) et le temps effectif du jour sur la conversation d'après le transcript via `feedback "<projet>" <action> --transcript auto` (pondéré par les flèches `->` / `→` et commentaires d'artéfacts).
* **Sauvegarde Ciblée de la Note Maîtresse, des Sous-Notes & Portabilité Multi-Ordinateurs** :
  * **Synchronisation Git Obligatoire de Tout Dépôt Lié (`git commit` & `git push`)** : Lorsqu'un ou plusieurs dépôts Git sont liés au projet (`repo_url`, `local_latex_path`, dépôt dans `~/Documents/code/`), vérifier systématiquement `git status` sur chaque dépôt lié et, si des modifications ou nouveaux fichiers ont été produits pendant la session (code, données, CSV d'annotations saisis par Henri, sources LaTeX ou rebuttal), faire exécuter `git add`, `git commit` et `git push` vers le remote distant (GitHub et/ou Overleaf) afin que 100 % des modifications soient synchronisées en ligne (*ex. réel 21/10/2026, DMKD Revision : nouvelles annotations de `annotations_henri.csv` saisies sur Streamlit et `Response_to_Reviewers.tex`/`.pdf` corrigés committés et poussés sur GitHub lors du `/project-memory ok`*).
  * **Mise à jour de la Note Maîtresse & Régénération de `_agents/project_diffs/🤖 <Titre>.md` (`doc-version`)** : Mettre à jour la Note Maîtresse (et sa section finale `## 🚀 Quelles Sont les Prochaines Étapes ?` en discours naturel fluide, 1 paragraphe par tâche, zéro `- [ ]` / `- [x]`) ainsi que les sous-notes liées, puis régénérer l'artéfact de diff cumulatif `_agents/project_diffs/🤖 <Titre>.md` via `doc-version` (`get_diff_artifact`) comparé à la baseline `author="henri"` (synchronisé entre les PC par Obsidian Sync).
* **Vérification & Mise à Jour des Notes Obsidian (Mandatoire)** : Moment privilégié pour **auditer et synchroniser la note maîtresse et toutes les sous-notes liées du projet dans Obsidian**. Vérifier qu'elles reflètent fidèlement 100% des avancées, décisions prises, arbitrages, travaux effectués et nouveaux jalons de la session, conformément au format de `_agents/rules/coffre-obsidian.md` (**Zéro tableau, Question ➔ Courte explication d'interprétation en 1–2 phrases ➔ Source + Citation exacte en bloc**).
* **Interrogation Interactive du Stress (`ask_question`) & Évolution du Score** :
  * Recueillir le ressenti d'Henri : si Henri a déjà précisé son ressenti dans sa demande (ex: `/project-memory ok`, `/project-memory a l'aise`), appliquer directement sans pop-up. Sinon, appeler obligatoirement `ask_question` avec les 4 options canoniques dans l'ordre strict `["À l'aise", "OK", "Stressé", "Terminé"]` (avec le suffixe ` (Recommandé)` apposé sur l'option conseillée selon la marge calendaire).
  * Exécuter l'action CLI correspondante (`feedback "<projet>" <action> --transcript auto`) pour enregistrer le ressenti et comptabiliser le temps réel de session.
  * Indiquer factuellement le score de base $S_{\text{base}}$ et le score effectif $S_{\text{eff}}$ mis à jour.
  * Préciser le **malus temporel cumulatif** appliqué via `recentWorkDates` (valeur de $K$, nombre de sessions consécutives dans les 6h, pénalité en points).
* **Clôture Définitive de Session (Zéro Relance & Zéro Suggestion Suivante)** : Clôturer définitivement la conversation après le feedback sans relancer de Pomodoro et sans suggérer de projets suivants.

### 3. Variante Asynchrone en Passe Unique (`/one-shot`)
Lorsqu'Henri souhaite déposer tous ses commentaires et consignes en une seule passe puis quitter immédiatement la conversation pendant que l'agent scelle l'état validé (`author="henri"`), exécute ses demandes, actualise la Note Maîtresse Obsidian, régénère `_agents/project_diffs/🤖 <Titre>.md` via `doc-version` et clôture `project-memory` sans poser de question, appliquer [`_agents/skills/one-shot/SKILL.md`](file:///c:/Users/hjamet/Documents/VoiceNotes/_agents/skills/one-shot/SKILL.md).

---

## 💡 Quels Sont les Workflows Recommandés pour Antigravity ?

0. **Affichage Système & Double Lien Vivant en Tête (`Note Obsidian` + `🤖 <Titre>.md`)** :
   - Dès qu'une session de travail démarre sur un projet (ou qu'un projet est sélectionné), Antigravity **DOIT OBLIGATOIREMENT fournir au tout début de son message le double lien Markdown cliquable absolu vers la note du projet dans le coffre Obsidian et vers son diff `_agents/project_diffs/🤖 <Titre>.md`**.
   - **Protocole de Reprise de Session (Nouvelle Conversation)** : En coordination avec `_agents/rules/pomodoro-projets.md`, l'agent :
     1. **Lecture de `_agents/project_diffs/🤖 <Titre>.md` et de la Note Maîtresse** : Au Tour 0, le superviseur lit la note maîtresse et `_agents/project_diffs/🤖 <Titre>.md` (généré par `doc-version`), sans jamais créer ni utiliser de `task.md`.
     2. **Souveraineté de la baseline `author="henri"`** : Tant qu'Henri n'a pas revu un fichier, l'agent utilise `author="agent"` et ne modifie jamais `🤖 <Titre>.md` à la main autrement que via `doc-version` `get_diff_artifact` (selon `_agents/rules/task-tracking.md`).
     3. **Vérifie l'existence des sous-notes et artéfacts** : Vérifie sur disque si les plans et rapports listés existent et actualise leurs liens.
   - **Objectif** : Permettre à Henri de retrouver instantanément dans Obsidian et son volet latéral ses modifications et prochaines étapes d'un PC à l'autre via Obsidian Sync.

1. **Orientation & Protocole Dual-Track des Projets Urgents** :
   - **Piste Synchrone (Zéro-latence)** : Exécuter `list --reviewed --top 3` pour extraire et fournir immédiatement à Henri les Top 3 projets révisés sous forme de liens Markdown cliquables.
   - **Piste Asynchrone (Sous-agents d'évaluation)** : En parallèle, lancer en arrière-plan un sous-agent d'évaluation (`research`) qui spawne un sous-agent par projet non révisé (`list --unreviewed`), explore 100% de son contexte (notes Obsidian, e-mails Spark), et attribue un score d'urgence initial (1-100) via `set-score "<nom>" <score>` jusqu'à ce qu'il reste 0 projet non révisé.
   - **Restitution Artefact** : Antigravity présente un tableau synthétique sous forme d'artefact listant l'ensemble des nouveaux projets évalués et leurs scores pour révision et validation.

2. **Récupération Proactive du Contexte Global & Exploration par Sous-Agents** :
   - Exécuter `get "<NomProjet>"` pour extraire les objectifs, la deadline (date limite dure), les jalons (`milestone` synchrone uniquement, sans faux jalons ni dates passées) et les sessions récentes (`recentWorkDates`), et lire `_agents/project_diffs/🤖 <Titre>.md`.
   - **Exploration Périphérique Immédiate** : Antigravity ne se contente pas de lire la note maîtresse. Antigravity doit **récupérer tout le contexte environnant** (lire les sous-notes liées `[[Sous-Note.md]]`, rechercher les derniers e-mails pertinents dans Spark, et inspecter le dossier de code associé).
   - **Délégation & Sous-Agents d'Exploration** : Si le projet est vaste ou comporte des dépendances multiples, Antigravity **doit spontanément lancer un ou plusieurs sous-agents d'exploration** (`eclaireur`) selon l'échelle de déterminisme de `sous-agents.md` pour fouiller la documentation, les échanges récents ou le codebase afin de posséder 100% du contexte dès le début du travail.

3. **Session de Travail sans Démon & Bilan Rétrospectif** :
   - **Travail Fluide & Sans Coupure** : Interdiction formelle de lancer des démons de fond (`work`). Le travail s'effectue librement. Au tout début, afficher immédiatement le double lien Markdown cliquable vers la note Obsidian et vers `_agents/project_diffs/🤖 <Titre>.md`.
   - **Protocole de Clôture de Session** : Déclenché EXCLUSIVEMENT sur invocation explicite par Henri du skill `project-memory` :
     1. Mettre à jour la Note Maîtresse Obsidian (et sa section finale `## 🚀 Quelles Sont les Prochaines Étapes ?`, zéro `- [ ]` / `- [x]`) et régénérer `_agents/project_diffs/🤖 <Titre>.md` via `doc-version` (`get_diff_artifact`).
     2. Recueillir le ressenti d'Henri : si déjà précisé dans l'échange (ex: `/project-memory ok`, « je suis à l'aise »), appliquer directement. Sinon, interroger via `ask_question` avec les 4 options canoniques `["À l'aise", "OK", "Stressé", "Terminé"]` (avec recommandation calendaire).
     3. Appliquer le feedback et créditer automatiquement le temps réel de session via `feedback "<NomProjet>" <action> --transcript auto`.
     4. Clôturer définitivement la session et la conversation sans relancer de chronomètre et sans suggérer de projets suivants.

4. **Accomplissement d'une Étape en Cours de Session (Zéro Interruption)** :
   - Une fois une étape réalisée dans le projet, mettre à jour la Note Maîtresse et régénérer `_agents/project_diffs/🤖 <Titre>.md` via `doc-version` (`get_diff_artifact`). Interdiction formelle d'appeler `ask_question` de ressenti (réservé à l'invocation de `project-memory` par Henri).

5. **Clôture de Session (Sur Invocation Explicite)** :
   - Lors de l'invocation de `project-memory` par Henri, si le ressenti n'est pas déjà indiqué, interroger Henri via `ask_question` avec les 4 options canoniques et consigner l'action choisie (`feedback "<NomProjet>" <action> --transcript auto`).

6. **Archivage & Finalisation** :
   - Lorsqu'un projet est achevé, exécuter `feedback "<NomProjet>" finished`.

7. **Mise à Jour Systématique de la Fiche de Projet Obsidian (Fin de Session)** :
   - À chaque fin de travail sur un projet, Antigravity **DOIT OBLIGATOIREMENT** mettre à jour la note Markdown du projet dans le coffre Obsidian selon `_agents/rules/coffre-obsidian.md` et `_agents/rules/task-tracking.md`.
   - **Règles d'or de mise à jour & Structure de la Note Maîtresse** :
     0. **Suivi Unifié via la Note Maîtresse (`## 🚀 Quelles Sont les Prochaines Étapes ?`) & `_agents/project_diffs/🤖 <Titre>.md` (`doc-version`) & Zéro `- [ ]` dans Obsidian** : La Note Maîtresse se termine par la section narrative `## 🚀 Quelles Sont les Prochaines Étapes ?` (un paragraphe distinct par tâche, zéro checklist `- [ ]` ni `- [x]`) et son diff cumulatif par rapport à la baseline `author="henri"` est généré dans `_agents/project_diffs/🤖 <Titre>.md` via `doc-version` (`get_diff_artifact`).
     0bis. **Sauvegarde Pérenne de Tout Livrable ou Brouillon (Portabilité Multi-Ordinateurs via Obsidian Sync)** : Tout plan ou développement volumineux est archivé en sous-note (`notes/<Sous-Note>.md` indexée sous le H1 de la note maîtresse) et tout brouillon de message (`virtual:<Sujet>`) est généré dans `_agents/project_diffs/🤖 <Sujet>.md` via `doc-version`.
     1. **Index des Sous-Notes & Section `## Skills` en Haut de Page (MANDATOIRE)** : Placer systématiquement en haut du document (immédiatement sous le titre H1 et l'image maîtresse) l'**Index des Sous-Notes & Documents Clés `[[Sous-Note.md]]`**, suivi de la section **`## Skills`** (`- [[skills/<nom>|Titre]] — <condition d'utilisation en Lazy Loading>`, référençant les notes de skills centralisées dans `skills/` du coffre en relation Many-to-Many). L'agent inspecte `## Skills` dès l'ouverture du projet, ne lit un skill qu'à la demande lorsque sa tâche remplit la condition indiquée (en le traçant dans `read_files` de `task_commit`), et l'affine via `/learn` en réécrivant/condensant ses règles à taille constante (Rasoir d'Ockham, zéro empilement en bas de note) à chaque commentaire, critique ou modification de brouillon par Henri.
     2. **Format Question ➔ Courte Explication ➔ Citation Sourcée en Bloc (Zéro Tableau)** : Conformément à [coffre-obsidian.md](file:///c:/Users/hjamet/Documents/VoiceNotes/_agents/rules/coffre-obsidian.md), éviter les tableaux Markdown dans les notes du coffre ; ouvrir chaque section/sous-section par une question (`## ... ?` / `### ... ?`), suivie de 1 à 2 phrases d'explication directe donnant la réponse et l'interprétation claire du point, puis de `Source : <ancre>` et de la citation exacte en bloc.
     3. **Déport Systématique au-delà d'une Page et Demie (~120 lignes)** : Tout développement approfondi, protocole technique lourd, historique de factures ou compte-rendu exhaustif DOIT être **déporté dans une sous-note dédiée** liée dans l'index du haut.
     4. **Accumulation d'informations de haut niveau & Interdiction de suppression arbitraire** : Toujours **ajouter** les décisions stratégiques, arbitrages et résultats majeurs du travail effectué sans perdre d'information utile.
     5. **Audit d'obsolescence & Rigueur sur les Échéances** : S'assurer que la note maîtresse et ses sous-notes contiennent uniquement des informations exactes et à jour, et que le frontmatter respecte strictement la distinction `deadline:` (date limite dure réelle et contraignante) vs `milestone:` (réunion synchrone planifiée uniquement), sans faux jalons ni dates passées.

---

## 📌 Comment S'Applique le Principe d'Autonomie Stricte (1 Note = 1 Projet) ?

> **Principe Fondamental : 1 Note taggée `#todo` / `#project` = 1 Projet Autonome** :
> Chaque note comportant le tag `#todo` ou `#project` est un projet autonome à part entière, suivi et priorisé individuellement dans `project-memory`. Il n'y a **aucune hiérarchie implicite parent-enfant** ni d'absorption automatique par graphe de wikilinks (`[[...]]`). Les liens entre notes sont de simples références documentaires hypertextes.
>
> **Gestion des Notes Auxiliaires, Fiches Dérivées & Non-Projets** :
> Si une note (sous-note technique, compte-rendu, fiche de travail, pensée ponctuelle) ne doit **pas** constituer un projet distinct dans `project-memory` :
> 1. **Retrait manuel des tags** : Retirer simplement le tag `#todo` ou `#project` du frontmatter et du corps de la note.
> 2. **Commande `non-projet`** : Exécuter `python project_memory_cli.py feedback "<nom>" non-projet` pour retirer automatiquement les tags et purger la note de `data.json`.
> 3. **Nettoyage orphelin** : Exécuter `python project_memory_cli.py clean-orphans` (ou `list --clean-orphans`) pour maintenir `data.json` parfaitement synchronisé avec le coffre.

---

## 🔍 Comment Traiter les Problèmes & Résoudre les Erreurs ?

- **Note non trouvée** : Le CLI effectue une recherche floue. Si un nom partiel est fourni et ne correspond à aucun fichier, le script signale une erreur. Vérifier le titre exact dans Obsidian.
- **Encodage Windows** : Le script gère automatiquement l'encodage `utf-8` sur stdout sous Windows.

---

## 📋 Spécificités issues des règles générales (Pomodoro & Task Tracking)

- **Clôture & Bilan Rétrospectif** : Une session ne se termine QUE lorsque Henri le demande expressément via l'invocation du skill project-memory. Interdiction formelle de déclarer de soi-même une fin de session (même si toutes les tâches sont faites ou qu'une clôture future est listée). Le bilan des chantiers, le calcul du temps réel et la mise à jour du registre sont réservés exclusivement à cette invocation.
- **Feedback Réservé à la Clôture de Session** : L'outil modal `ask_question` pour le ressenti est strictement réservé à l'invocation explicite par Henri du skill project-memory (et UNIQUEMENT si son ressenti n'est pas déjà précisé dans sa demande). Interdiction formelle et absolue de poser la question de ressenti hors de cette invocation.
- **Suivi Unifié par Projet via la Note Maîtresse & `_agents/project_diffs/🤖 <Titre>.md` (`doc-version`) & Zéro `task.md`** : L'unique source de vérité du projet est sa Note Maîtresse (`notes/<Titre>.md`, incluant en bas de note `## 🚀 Quelles Sont les Prochaines Étapes ?` en langage naturel) couplée à son artéfact de diff cumulatif `_agents/project_diffs/🤖 <Titre>.md` généré par `doc-version` (`get_diff_artifact`) par rapport à la baseline `author="henri"`.
