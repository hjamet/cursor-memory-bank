---
name: project-memory
description: "Pilotage CLI des priorités de projets Obsidian et régulation de charge Pomodoro."
---
# Comment Fonctionne et se Pilote le Plugin Project Memory CLI ?

Ce skill documente l'utilisation complète de l'interface en ligne de commande `project_memory_cli.py` pour interagir avec le plugin Obsidian **Project Memory** du coffre Obsidian de Henri Jamet.

> [!IMPORTANT]
> ### ⚡ Dérogation Formelle d'Exécution CLI pour le Superviseur Racine ($P=0$)
> Par dérogation formelle aux règles générales de GEMINI.md, le Superviseur Racine ($P=0$) est exclusivement habilité à exécuter en direct via `run_command` les commandes CLI suivantes :
> 1. `status-work` (avec ou sans `--all` ou ciblage)
> 2. `list` (avec ses options `--top`, `--reviewed`, `--unreviewed`, `--json`)
> 3. `work "<Projet>"` (lancement de session)
> 4. `stop-work` (interruption de session)
> 
> **AUCUNE AUTRE COMMANDE N'EST AUTORISÉE** : aucune création de script scratch, aucun code inline python -c, aucun build, aucun test.
> **Zéro sous-agent pour le triage /project-memory** : le Superviseur Racine exécute directement `status-work` et `list --top 10` pour afficher le tableau de bord en < 2s.

---

## 📍 Quels Sont les Chemins d'Accès Clés du Système ?

- **Script CLI Python** : `C:\Users\Jamet\Documents\VoiceNotes\_agents\scripts-for-skills\project_memory_cli.py`
- **Fichier de Données JSON** : `C:\Users\Jamet\Documents\VoiceNotes\.obsidian\plugins\project-memory\data.json`
- **Racine du Vault Obsidian** : `C:\Users\Jamet\Documents\VoiceNotes`
- **Plugin Obsidian** : `C:\Users\Jamet\Documents\VoiceNotes\.obsidian\plugins\project-memory\`

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
   Calculé pour les réunions, oraux ou synchronisations d'équipe réelles (`milestone: "mercredi"`, `milestone: "2026-09-16"`, cron ou ISO) :
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
     * Déclenché **exclusivement lors d'une session de travail réelle** (bilan post-tâche, fin de Pomodoro, clôture de session de travail, ou consigne explicite d'Henri dans la conversation).
     * **Obligation Stricte d'Interrogation Interactive (`ask_question`)** : Antigravity **NE DOIT PAS appliquer de mutation unilatérale arbitraire**. À chaque point d'avancement, accomplissement de tâche (`complete-task`) ou clôture de session de travail Pomodoro réelle, Antigravity **DOIT OBLIGATOIREMENT appeler `ask_question`** pour recueillir le niveau de stress / confort réel d'Henri parmi les 4 options canoniques : `["À l'aise", "OK", "Stressé", "Terminé"]` (avec le suffixe ` (Recommandé)` apposé sur l'option suggérée selon l'analyse de marge calendaire).
     * **🚫 INTERDICTION FORMELLE EN PHASE DE CONSULTATION / TRIAGE (`/project-memory`)** : Il est STRICTEMENT INTERDIT de déclencher l'outil modal `ask_question` lors d'une simple consultation, d'une invocation `/project-memory` ou pour demander à Henri sur quoi travailler. Antigravity DOIT TOUJOURS afficher d'abord en texte clair dans le chat le tableau visuel complet des priorités, échéances et contextes. Le choix du sujet s'effectue par dialogue naturel dans le chat.
     * **Enregistre la session de travail réelle** : ajoute automatiquement le timestamp UTC dans `recentWorkDates` pour appliquer le malus temporel $K$ anti-effet-tunnel dégressif sur 6 heures ($M_{\text{temporal}}(K)$).
     * **Valide le jalon synchrone** : met à jour `lastSatisfiedMilestoneDate = now` si la session correspond à l'échéance.
     * **Gère la rotation des projets** : réinitialise ou amortit le bonus de rotation $B_{\text{rot}}$ du projet et applique le modèle d'Achille et la Tortue aux autres projets actifs.
     * Met à jour `lastReviewDate`, le score de base ($S_{\text{base}}$) et l'historique (`reviewHistory`).
     * Commande canonique : `python project_memory_cli.py feedback "<projet>" <action>`
   - **2. Veille, Triage & Ajustement de Priorités par l'Agent (`set-score "<projet>" <score_1_100>`)** :
     * Déclenché **quand l'Agent met à jour / ajuste des priorités ou effectue de la veille** (veille matinale, cycles Dream Vague 2 & Vague 3, qualification du portefeuille `0 unreviewed`, ou quand Henri demande dans le chat hors session de travail « rends ce projet plus urgent / augmente la prio »).
     * **L'Agent NE DOIT PAS utiliser `feedback`** (pour ne pas simuler une fausse session de travail d'Henri).
     * **L'Agent DOIT utiliser `set-score "<projet>" <score_1_100>`** (qui définit directement le score de base sans altérer `recentWorkDates` ni imposer de malus $K$).
     * **Garanties Système de `set-score`** :
       - `recentWorkDates` reste **strictement inchangé** ($K = 0.0$, aucun malus temporel indu).
       - `lastSatisfiedMilestoneDate` reste **strictement inchangé** (aucun jalon futur validé par erreur).
       - Les bonus de rotation $B_{\text{rot}}$ des autres projets restent inchangés.
       - Met à jour le score de base ($S_{\text{base}}$), `lastReviewDate` et incrémente `totalReviews`.
     * Pour clore un projet terminé ou requalifier une note sans livrable lors de la veille : `feedback "<projet>" finished` ou `feedback "<projet>" non-projet`.

10. **Ordre de Priorité & Évaluation Initiale Obligatoire** :
   - Les **nouveaux projets non révisés** (`totalReviews == 0`) font l'objet d'une **évaluation initiale obligatoire** via le Protocole Dual-Track : exploration contextuelle (Obsidian, AIVC, Spark) par sous-agents et attribution d'un score explicite de $1.0$ à $100.0$ avec `set-score`, jusqu'à ce qu'il reste 0 projet non révisé (`0 unreviewed`).
   - Les **projets déjà révisés** (`totalReviews > 0`) sont classés par `Effective Score` décroissant (`list --reviewed`).

11. **Gestion des Échéances & Jalons (`deadline` & `milestone`) & Règle Fondamentale de Distinction** :
   - **`deadline:` (Date Limite Dure)** :
     - Applicable à **tout projet ayant une échéance réelle et contraignante** : soumissions d'articles académiques (TheWebConf, AAAI, CSUR, FAccT, AAMAS), rapports d'activité ou de subventions (ex: HEC Research Fund), démarches légales/administratives (ex: permis de séjour), ou engagements contractuels fermes.
     - **Zéro restriction de domaine** : Les deadlines ne sont en aucun cas réservées aux seuls articles scientifiques. En revanche, les projets créatifs, personnels ou de fond sans contrainte temporelle externe (ex: JDR Asharde) ne requièrent pas de deadline artificielle.
     - Format ISO obligatoire : `YYYY-MM-DD` (ex: `deadline: 2026-10-18` ou `due: 2026-10-18`).
     - Sert de base mathématique de calcul pour l'urgence d'échéance $U_{\text{temporal}}$ via $P_{\text{deadline}}$ (avec régime de sprint à $J \le 7$).
   - **`milestone:` (Jalon Synchrone / Synchronisation d'Équipe)** :
     - Réservé **STRICTEMENT aux réunions, oraux ou synchronisations d'équipe planifiées** (ex: réunion DLLP du mercredi, oral d'examen, point d'avancement avec directeurs/collaborateurs).
     - **Date fixe** : `milestone: 2026-08-28` ou `milestone: "2026-08-28"` (ex: date d'une réunion de cadrage, oral planifié).
     - **Jour de semaine récurrent** : `milestone: "mercredi"` ou `milestone: "lundi"` (ex: synchronisation hebdomadaire régulière).
     - **Périodicité paramétrée** : `milestone: "mercredi@3"` ou `milestone: "lundi@2"` (ex: réunion toutes les $N$ semaines un jour donné).
   - **Champ Descriptif Optionnel (`next_milestone:`)** : Phrase synthétique contextualisant le contenu exact du prochain jalon synchrone (ex: `next_milestone: "Réunion DLLP le mercredi 26 août 2026"`).
   - **🚫 INTERDICTION FORMELLE DE FAUX JALONS** :
     - Ne **JAMAIS inventer ou insérer de champ `milestone:`** s'il n'y a pas de réunion, oral ou synchronisation synchrone formelle planifiée.
     - *Exemple* : Un renouvellement de permis B ou un dépôt administratif n'a **PAS de `milestone:`**, seulement une `deadline:`. Si un projet n'implique aucune réunion synchrone planifiée, omettre totalement le champ `milestone:`.
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
> - À chaque **point d'avancement**, **accomplissement de tâche (`complete-task`)**, **fin de session Pomodoro / `/work`** ou **clôture de session de travail**, Antigravity **DOIT OBLIGATOIREMENT appeler l'outil `ask_question`** pour recueillir son niveau de stress / confort réel.
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

#### Quelles Sont les Colonnes du Tableau CLI ?
- `Rank` : Rang du projet dans l'ordre de priorité.
- `Title` : Titre du projet / nom de la note Obsidian (largeur dynamique sans troncature agressive).
- `Eff.Score` : Score effectif $S_{\text{eff}}$ calculé en temps réel (borné strictement dans $[1.0, 100.0]$).
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

Extrait l'ensemble des métriques d'un projet, le détail de ses sessions de travail récentes (`recentWorkDates`), son historique de révisions, ainsi que la liste des tâches roadmap (cases à cocher pendantes `[ ]` et complétées `[x]`).

#### Quelle Est la Syntaxe ?
```bash
python "C:\Users\hjamet\Documents\VoiceNotes\_agents\scripts-for-skills\project_memory_cli.py" get "<project_path_or_name>" [--json]
```

#### Quelles Sont les Informations Affichées ?
- **Scores et Métriques** : $S_{\text{eff}}$, $S_{\text{base}}$, $B_{\text{rot}}$ (Achille & Tortue), $U_{\text{temporal}}$ ($P_{\text{deadline}}$, $P_{\text{milestone}}$), $M_{\text{temporal}}(K)$, $K$, deadline, nombre de révisions et dernière date de révision.
- **Sessions de Travail Récentes (`recentWorkDates`)** : Liste des sessions enregistrées dans les 6 dernières heures avec leur ancienneté $\Delta t$, la contribution pondérée à $K$, et l'impact sur le malus temporel.
- **Historique de Révision** : Les dernières actions consignées (`ok`, `more-often`, `less-often`, etc.) avec le score résultant.
- **Tâches Roadmap** : Tâches en attente `[ ]` et accomplies `[x]` avec leurs numéros de ligne dans la note.

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
> - **Réservé EXCLUSIVEMENT aux sessions de travail réelles** suite au retour recueilli interactivement via `ask_question` auprès d'Henri (ou consigné suite à une demande explicite d'Henri dans la conversation).
> - **L'Agent NE DOIT PAS utiliser `feedback` lors de la veille ou du triage autonome** (utiliser `set-score` à la place).

#### Quelle Est la Syntaxe ?
```bash
python "C:\Users\hjamet\Documents\VoiceNotes\_agents\scripts-for-skills\project_memory_cli.py" feedback "<project_path_or_name>" <action>
```

#### Quelles Sont les Actions Disponibles ?
- `less-often` : Réduit la priorité du projet (sélection « À l'aise » : aisance constatée, avance sur planning, charge allégée).
- `ok` : Maintient le score actuel (sélection « OK » : rythme maîtrisé, session de travail nominale).
- `more-often` : Augmente la priorité du projet (sélection « Stressé » : friction détectée, marge faible, besoin de suivi rapproché).
- `emergency` : Augmente fortement la priorité (urgence critique).
- `finished` : Marque le projet comme terminé (sélection « Terminé » : score ramené à $0.0$, tag `#done` ajouté, purge de `data.json`).
- `non-projet` : Marque la note comme un **non-projet** (note de mémoire, résumé, pensée sans livrables ni feuille de route). Les tags `#todo` et `#project` sont retirés du frontmatter YAML et la note est purgée des projets actifs.

#### Quel Est le Comportement Système de `feedback` ?
1. Met à jour le score de base $S_{\text{base}}$ et la date de dernière revue `lastReviewDate`.
2. Consigne l'entrée dans l'historique `reviewHistory`.
3. Ajoute automatiquement le timestamp UTC actuel dans `recentWorkDates` (activant le malus temporel $M_{\text{temporal}}(K)$ dégressif sur 6 heures pour prévenir l'effet tunnel).
4. Enregistre `lastSatisfiedMilestoneDate = now` pour valider le cycle de jalon.
5. Réinitialise le `rotationBonus` $B_{\text{rot}}$ du projet à **`0.0`** (si session nominale $\text{ratio} \ge 0.8$) et incrémente le `rotationBonus` de **tous les autres projets actifs via le modèle asymptotique d'Achille et la Tortue ($\Delta B = \alpha \times (100 - S_{\text{rot}}) \times \text{ratio}$)**.
6. Recalcule et persiste immédiatement `effectiveScore` dans `data.json` selon le principe DRY.
7. Met à jour les statistiques globales (`totalReviews`, etc.).

#### Quels Sont les Exemples d'Utilisation ?
```bash
# Espacement de priorité suite au choix "À l'aise"
python "C:\Users\hjamet\Documents\VoiceNotes\_agents\scripts-for-skills\project_memory_cli.py" feedback "MonProjet" less-often

# Maintien de score suite au choix "OK"
python "C:\Users\hjamet\Documents\VoiceNotes\_agents\scripts-for-skills\project_memory_cli.py" feedback "MonProjet" ok

# Hausse de priorité suite au choix "Stressé"
python "C:\Users\hjamet\Documents\VoiceNotes\_agents\scripts-for-skills\project_memory_cli.py" feedback "MonProjet" more-often
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

### 5. Comment Cocher une Tâche Roadmap avec `complete-task` ?

Recherche une case à cocher non cochée `[ ]` correspondant à un extrait de texte dans la note du projet, la transforme en case cochée `[x]`, réécrit le fichier Markdown et horodate la session de travail dans `recentWorkDates` (réinitialisation du bonus de rotation du projet et rotation d'Achille et la Tortue sur tous les autres projets).

> [!IMPORTANT]
> **COMPORTEMENT POST-TÂCHE & INTERROGATION INTERACTIVE (`ask_question`)** :
> Dès l'exécution de `complete-task`, la tâche est cochée et la session de travail automatiquement horodatée. Antigravity **DOIT OBLIGATOIREMENT appeler `ask_question`** pour interroger Henri avec les 4 options canoniques dans l'ordre strict `["À l'aise", "OK", "Stressé", "Terminé"]` (en apposant ` (Recommandé)` sur l'option conseillée selon la marge calendaire) afin d'enregistrer son ressenti réel et d'ajuster le score via `feedback "<projet>" <action>`.

#### Quelle Est la Syntaxe ?
```bash
python "C:\Users\hjamet\Documents\VoiceNotes\_agents\scripts-for-skills\project_memory_cli.py" complete-task "<project_path_or_name>" "<task_text>"
```

#### Quels Sont les Arguments ?
- `<project_path_or_name>` *(string)* : Chemin relatif ou nom du projet.
- `<task_text>` *(string)* : Extrait du texte de la tâche à cocher.

#### Quel Est un Exemple d'Utilisation ?
```bash
python "C:\Users\hjamet\Documents\VoiceNotes\_agents\scripts-for-skills\project_memory_cli.py" complete-task "Composer une musique" "Rédiger la partition d'ouverture"
```

---

### 6. Comment Démarrer une Session Pomodoro Active & Pause avec `work` (Support Multi-Sessions Parallèles) ?

Démarre une session de travail Pomodoro sur un projet. La durée de la session est déterminée automatiquement par le paramètre `pomodoroDuration` configuré dans le fichier `data.json` du plugin (durée configurée par Henri dans les réglages Obsidian, actuellement 60 minutes / 1h), à moins qu'une durée spécifique ne soit fournie via l'option `--duration N`.

> [!TIP]
> **🚀 Support Natif des Sessions Pomodoro Parallèles** :
> - **Multi-Projets Simultanés** : Il est possible de lancer simultanément plusieurs sessions Pomodoro en arrière-plan pour des projets **distincts** (par exemple en alternant d'un chat ou d'un volet à l'autre sur deux projets en parallèle).
> - **Prévention des Doublons sur le Même Projet** : Si une session est déjà en cours pour le **même projet exact**, le CLI refuse le doublon et affiche un avertissement clair rappelant le PID existant et la commande pour l'interrompre.
> - **Architecture Multi-Sessions Rétrocompatible** : Les sessions actives sont stockées dans `.obsidian/plugins/project-memory/.active_pomodoro.json` et synchronisées dans `data.json`. Les deux fichiers exposent à la racine la session principale (`activeSession`) ainsi que le dictionnaire complet `activeSessions: { [rel_path]: sessionData }`, garantissant une interopérabilité descendante absolue avec tous les outils et composants de l'interface Obsidian.

> [!IMPORTANT]
> **RÈGLE D'OR DU POMODORO PERMANENT (ZÉRO TRAVAIL SANS POMODORO)** :
> - **Interdiction Formelle** : Il est formellement interdit de travailler sur un projet sans qu'un Pomodoro actif ne soit en cours d'exécution en arrière-plan (`work "<projet>"` ou timer calqué sur `data.json`, 60 min par défaut).
> - **Lancement Automatique Systématique** : Dès le début effectif de tout travail sur un projet quel qu'il soit (création de projet, note taggée `#todo`/`#project`, `/scout`, `/build`, `/draft`, `/teacher`, `/work`, rédaction, apprentissage, exploration d'architecture), exécuter **IMMÉDIATEMENT et sans attendre** la commande CLI en arrière-plan : `python _agents/scripts-for-skills/project_memory_cli.py work "<NomDuProjet>"`. Interdiction d'attendre une consigne explicite, d'exclure les phases de cadrage ou d'imposer une durée arbitraire (la durée configurée dans `data.json`, actuellement 60 min, est appliquée par défaut). Pause obligatoire de 5 min à l'échéance.
> - **Clôture Obligatoire & Zéro Relance Automatique** : À la fin d'une session Pomodoro (60 min), **INTERDICTION FORMELLE ET ABSOLUE de relancer automatiquement un Pomodoro**. L'agent déroule le protocole de fin de session en 4 points (pause de 5 min, feuille de route unifiée par chantiers synchronisée en tête de note maîtresse, interrogation interactive via `ask_question`, et clôture définitive de la conversation sans suggérer de projets suivants).
> - **Exception Unique** : Seules les questions ponctuelles isolées et hors projet (1 question/réponse triviale de 30 secondes) peuvent se passer de Pomodoro.
> - **Auto-Suffisance Absolue de la Commande `work` (Zéro Timer Manuel `schedule`)** : La commande CLI `work` exécutée en arrière-plan via `run_command` dort pendant toute la durée nominale (par défaut 60 min). À son échéance, le processus se termine et réveille automatiquement Antigravity via le système push réactif. **Il est FORMELLEMENT INTERDIT d'armer un timer manuel `schedule` en parallèle d'un Pomodoro `work`.**

#### Quelle Est la Syntaxe ?
```bash
python "C:\Users\hjamet\Documents\VoiceNotes\_agents\scripts-for-skills\project_memory_cli.py" work "<project_path_or_name>" [--duration N]
```

#### Quels Sont les Arguments & Options ?
- `<project_path_or_name>` *(string)* : Chemin relatif dans le coffre (ex: `"Projets/MonProjet.md"`) ou titre/nom du fichier (résolution floue supportée).
- `--duration N` *(int)* : Durée personnalisée de la session Pomodoro en minutes (outrepasse la valeur `pomodoroDuration` de `data.json`).

#### Quel Est le Protocole de Fin de Session & Workflow d'Interaction ?
1. **Lancement & Réveil Automatique par Processus** : Antigravity lance la commande `work` en tâche de fond (`run_command`). La terminaison naturelle du processus de fond réveille automatiquement Antigravity à l'échéance exacte de la session Pomodoro, sans aucun timer manuel `schedule`.
2. **Protocole de Fin de Session en 4 Points (Obligatoire)** :
   1. **Pause de 5 Minutes Obligatoire** : Inviter impérativement Henri à faire une pause de récupération de 5 minutes avant toute autre action cognitive.
   2. **Feuille de Route Unifiée par Chantiers & Synchronisation Note Maîtresse** :
      - *Format Unique par Chantiers* : Supprimer toute section narrative redondante de « travail accompli ». Restituer directement la feuille de route sous la forme d'une **checklist unique structurée par chantiers thématiques**, regroupant pour chaque domaine les actions accomplies (`- [x]`) et les tâches restantes (`- [ ]`) par rapport aux échéances/jalons.
      - *Item Unique 'Build Plan' pour les chantiers non implémentés* : Ne jamais éclater les chantiers techniques futurs en cases à cocher multiples de premier niveau. Les regrouper sous un seul item actif pointant vers l'artéfact pérenne :
        `- [ ] Build Plan : [[notes/Plan d'Implémentation <Projet>|Plan d'Implémentation Technique Détaillé]]` (dans Obsidian) ou `[Build Plan](file:///...)` (dans le chat).
      - *Usage Systématique des Menus Dépliants (`<details>`)* :
        * Encapsuler les tâches accomplies dans un menu dépliant :
          `<details><summary>✅ Cadrage Validé / Tâches Accomplies</summary>\n\n- [x] ...\n</details>`
        * Encapsuler la checklist détaillée des chantiers de build dans un menu dépliant :
          `<details><summary>🏗️ Détail des Chantiers Techniques de Build</summary>\n\n- [ ] **Chantier 1** ...\n</details>`
        * Seul l'item principal `- [ ] Build Plan` et les tâches opérationnelles immédiates restent visibles dépliés.
      - *Synchronisation en Tête de Note Maîtresse* : Mettre systématiquement à jour la section Roadmap et To-Do list (`[ ]`/`[x]`) tout en haut de la note maîtresse (immédiatement sous l'en-tête visuel et l'index, conformément à `AGENTS.md`).
      - *Obligation Systématique d'Archivage des Plans Non Builts* : Si des rapports d'exploration (`exploration_report_X.md`) ou un plan non encore exécuté par `/build` existent, Antigravity **DOIT OBLIGATOIREMENT** créer ou mettre à jour la note pérenne de cadrage : `notes/Plan d'Implémentation [NomProjet].md` dans le coffre, et la lier immédiatement dans l'index des sous-notes tout en haut de la note maîtresse (sous H1).
   3. **Interrogation Interactive du Ressenti (`ask_question`) & Feedback** : Antigravity évalue lucidement la progression selon les signaux réels (marge calendaire, fluidité d'exécution, complexité), détermine l'option conseillée avec le suffixe ` (Recommandé)`, et interroge **obligatoirement** Henri via `ask_question` avec les 4 options canoniques dans l'ordre strict : `["À l'aise", "OK", "Stressé", "Terminé"]`. Suite à sa réponse, Antigravity exécute `feedback "<projet>" <action>`.
   4. **Clôture Définitive de la Conversation (Zéro Relance & Zéro Suggestion Suivante)** :
      - *Interdiction Formelle de Relance Automatique* : INTERDICTION FORMELLE ET ABSOLUE de relancer un Pomodoro automatiquement.
      - *Suppression des Projets Suivants* : Ne plus calculer ni recommander les 3 projets suivants. Clôturer proprement la conversation sans pousser à un enchaînement compulsif.

3. **Rappels Systèmes Émis par la Sortie Terminale CLI** :
   La sortie terminale du CLI lors de l'échéance d'une session `work` (ou appel de `stop-work`) rappelle explicitement l'ensemble de ces devoirs (pause de 5 min obligatoire, archivage immédiat de `notes/Plan d'Implémentation [NomProjet].md`, mise à jour de la roadmap `[ ]`/`[x]` en tête de note maîtresse) ainsi que l'ordre impératif de relire le skill `project-memory` via `view_file`.

#### Quel Est le Protocole d'Évaluation Autonome & Anti-Biais ?
Lors de la clôture d'une session de travail ou de l'émission d'une recommandation, Antigravity doit respecter une rigueur d'analyse stricte :

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
* **Consommation Directe de la Sortie Standard** :
  - Reprendre directement le tableau Markdown généré par la commande `list` dans le message de chat (le script formate déjà nativement les rangs, scores, échéances et jalons).
  - Fournir les liens Markdown cliquables absolus `[Nom](file:///...)` vers les notes Obsidian correspondantes.
* **Recommandations Stratégiques Motivées** :
  - Formuler une analyse concrète et tranchée sur le focus le plus pertinent d'après les échéances du tableau.
* **Échange Naturel dans le Chat** :
  - Laisser Henri arbitrer et réagir directement dans la conversation sur son choix de projet (l'outil modal `ask_question` est réservé aux bilans de fin de session et feedbacks de charge).

### 2. Que Faire en Milieu de Conversation ou Clôture de Session (Bilan & Clôture) ?
* **Vérification & Mise à Jour des Notes Obsidian (Mandatoire)** : Moment privilégié pour **auditer et synchroniser la note maîtresse et toutes les sous-notes liées du projet dans Obsidian**. Vérifier qu'elles reflètent fidèlement 100% des avancées, décisions prises, arbitrages, travaux effectués et nouveaux jalons de la session.
* **Bilan d'Avancement Factuel & Roadmap Unifiée** : Restituer la feuille de route sous forme de checklist unique par chantiers (`- [x]` accompli, `- [ ]` restant) sans section narrative redondante.
* **Interrogation Interactive du Stress (`ask_question`) & Évolution du Score** :
  * Appeler obligatoirement `ask_question` avec les 4 options canoniques dans l'ordre strict `["À l'aise", "OK", "Stressé", "Terminé"]` (avec le suffixe ` (Recommandé)` apposé sur l'option conseillée selon la marge calendaire).
  * Exécuter l'action CLI correspondante (`feedback "<projet>" <action>`) choisie par Henri.
  * Indiquer factuellement le score de base $S_{\text{base}}$ et le score effectif $S_{\text{eff}}$ mis à jour.
  * Préciser le **malus temporel cumulatif** appliqué via `recentWorkDates` (valeur de $K$, nombre de sessions consécutives dans les 6h, pénalité en points).
* **Clôture Définitive de Session (Zéro Relance & Zéro Suggestion Suivante)** : Clôturer définitivement la conversation après le feedback sans relancer de Pomodoro et sans suggérer de projets suivants.

---

## 💡 Quels Sont les Workflows Recommandés pour Antigravity ?

0. **Affichage Système & Lien Cliquable de la Note de Projet (MANDATOIRE DÈS LE DÉBUT)** :
   - Dès qu'une session de travail démarre sur un projet (ou qu'un projet est sélectionné), Antigravity **DOIT OBLIGATOIREMENT fournir au tout début de son message le lien Markdown cliquable absolu vers la note du projet dans le coffre Obsidian** (ex: `[Nom de la Note](file:///C:/Users/hjamet/Documents/VoiceNotes/notes/NomProjet.md)`).
   - **Objectif** : Permettre à Henri de garder la note du projet ouverte sur son écran de droite dans Obsidian pour interagir, commenter, corriger et enrichir la note au fil de la discussion synchrone.

1. **Orientation & Protocole Dual-Track des Projets Urgents** :
   - **Piste Synchrone (Zéro-latence)** : Exécuter `list --reviewed --top 3` pour extraire et fournir immédiatement à Henri les Top 3 projets révisés sous forme de liens Markdown cliquables.
   - **Piste Asynchrone (Sous-agents d'évaluation)** : En parallèle, lancer en arrière-plan un sous-agent d'évaluation (`research`) qui spawne un sous-agent par projet non révisé (`list --unreviewed`), explore 100% de son contexte (notes Obsidian, AIVC `recall`, e-mails Spark), et attribue un score d'urgence initial (1-100) via `set-score "<nom>" <score>` jusqu'à ce qu'il reste 0 projet non révisé.
   - **Restitution Artefact** : Antigravity présente un tableau synthétique sous forme d'artefact listant l'ensemble des nouveaux projets évalués et leurs scores pour révision et validation.

2. **Récupération Proactive du Contexte Global & Exploration par Sous-Agents** :
   - Exécuter `get "<NomProjet>"` pour extraire les objectifs, la deadline (date limite dure), les jalons (`milestone` synchrone uniquement, sans faux jalons ni dates passées), les sessions récentes (`recentWorkDates`) et la liste des tâches pendantes (`[ ]`).
   - **Exploration Périphérique Immédiate** : Antigravity ne se contente pas de lire la note maîtresse. Antigravity doit **récupérer tout le contexte environnant** (lire les sous-notes liées `[[Sous-Note.md]]`, interroger la mémoire AIVC via `recall`, rechercher les derniers e-mails pertinents dans Spark, et inspecter le dossier de code associé).
   - **Délégation & Sous-Agents d'Exploration** : Si le projet est vaste ou comporte des dépendances multiples, Antigravity **doit spontanément lancer un ou plusieurs sous-agents d'exploration** (`research`) pour fouiller la documentation, les échanges récents ou le codebase afin de posséder 100% du contexte dès le début du travail.

3. **Session de Travail Pomodoro & Suivi de Rythme (Règle d'Or du Pomodoro Permanent)** :
   - **Zéro Travail sans Pomodoro** : Lancer systématiquement `work "<NomProjet>"`. Au tout début, afficher immédiatement le lien Markdown cliquable vers la note Obsidian.
   - **Protocole de Clôture en 4 Points** : À l'échéance de la session Pomodoro (60 min) :
     1. Inviter obligatoirement à la pause de 5 minutes.
     2. Restituer la feuille de route sous forme de checklist unique par chantiers (`- [x]` accompli, `- [ ]` restant par rapport aux échéances) synchronisée en tête de note maîtresse.
     3. Interroger Henri via `ask_question` avec les 4 options canoniques `["À l'aise", "OK", "Stressé", "Terminé"]` (avec la recommandation calendaire), puis appliquer le feedback choisi via `feedback "<NomProjet>" <action>`.
     4. Clôturer définitivement la session et la conversation. **INTERDICTION FORMELLE ET ABSOLUE de relancer un Pomodoro automatiquement et de suggérer les projets suivants.**
   - Seules les questions ponctuelles isolées et hors projet (1 question/réponse triviale de 30 secondes) peuvent se passer de Pomodoro.

4. **Accomplissement d'une Étape & Interrogation Interactive** :
   - Une fois une tâche réalisée dans le projet, exécuter `complete-task "<NomProjet>" "<ExtraitTâche>"` pour cocher la tâche et enregistrer automatiquement la session de travail.
   - Déclencher immédiatement `ask_question` avec les 4 options canoniques `["À l'aise", "OK", "Stressé", "Terminé"]` pour recueillir son ressenti et appliquer le `feedback "<NomProjet>" <action>` correspondant.

5. **Clôture de Session sans Tâche Spécifique** :
   - Si du travail a été effectué sans cocher de tâche spécifique, interroger Henri via `ask_question` avec les 4 options canoniques et consigner l'action choisie (`feedback "<NomProjet>" <action>`).

6. **Archivage & Finalisation** :
   - Lorsqu'un projet est achevé, exécuter `feedback "<NomProjet>" finished`.

7. **Mise à Jour Systématique de la Fiche de Projet Obsidian (Fin de Session)** :
   - À chaque fin de travail sur un projet, Antigravity **DOIT OBLIGATOIREMENT** mettre à jour la note Markdown du projet dans le coffre Obsidian.
   - **Règles d'or de mise à jour & Structure Tableau de Bord** :
     0. **Roadmap en Tête (MANDATOIRE DÈS LE HAUT)** : Mettre à jour la feuille de route opérationnelle (`## 📋 Quelle est la feuille de route opérationnelle...`) placée au sommet de la note (sous l'en-tête visuel et l'index des sous-notes), intégrant scrupuleusement TOUTES les tâches restantes `[ ]` du projet au vu de l'échéance/deadline et des points discutés, et cochant les tâches achevées `[x]`.
     0bis. **Sauvegarde Pérenne des Plans d'Implémentation et Rapports Non Builts** : Si des rapports d'exploration (`exploration_report_X.md`) ou un plan non encore exécuté par `/build` existent, Antigravity **DOIT OBLIGATOIREMENT** créer ou mettre à jour la note pérenne de cadrage : `notes/Plan d'Implémentation [NomProjet].md` dans le coffre, et la lier immédiatement dans l'index des sous-notes tout en haut de la note maîtresse (sous H1).
     1. **Index des Sous-Notes en Haut de Page (MANDATOIRE)** : Placer systématiquement un bloc **Index des Sous-Notes & Documents Clés `[[Sous-Note.md]]` tout en haut du document** (immédiatement sous le titre H1 et le callout de cadrage) pour naviguer instantanément dans le réseau du projet.
     2. **Lisibilité & Concision Radicale** : La note maîtresse doit rester un tableau de bord ultra-lisible, concis et propre. Elle ne contient que les mots-clés, faits capitaux, nombres clés, tableaux synthétiques et diagrammes Mermaid.
     3. **Déport Systématique des Détails en Sous-Notes** : Tout développement approfondi, protocole technique lourd, historique de factures ou compte-rendu exhaustif DOIT être **déporté dans une sous-note dédiée** liée dans l'index du haut.
     4. **Zéro Paragraphe Narratif & Zéro Liste Interminable** : Bannir les blocs de texte denses. Privilégier les tableaux synthétiques, émojis, alertes GitHub compactes (`> [!NOTE]`) et diagrammes.
     5. **Accumulation d'informations de haut niveau** : Toujours **ajouter** les décisions stratégiques, arbitrages et résultats majeurs du travail effectué.
     6. **Interdiction de suppression arbitraire** : Ne JAMAIS supprimer d'informations existantes sans l'accord d'Henri.
     7. **Audit d'obsolescence** : S'assurer que la note maîtresse et ses sous-notes contiennent uniquement des informations exactes et à jour.
     8. **Rigueur sur les Échéances & Frontmatter** : Vérifier que le frontmatter respecte strictement la distinction `deadline:` (date limite dure réelle et contraignante) vs `milestone:` (réunion synchrone planifiée uniquement), sans inventer de faux jalons et sans laisser de dates passées dans les champs d'échéance active.

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
- **Tâche non trouvée lors de `complete-task`** : Le script affiche la liste de toutes les tâches pendantes disponibles dans la note pour permettre d'ajuster l'extrait de recherche `<task_text>`.
- **Encodage Windows** : Le script gère automatiquement l'encodage `utf-8` sur stdout sous Windows.
