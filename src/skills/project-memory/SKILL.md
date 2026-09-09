---
name: project-memory
description: Interface CLI pour le plugin Obsidian project-memory. Permet à Antigravity d'interroger la priorité des projets, de lister les projets les plus urgents, d'obtenir le détail d'un projet, de consigner le feedback utilisateur via feedback, de calibrer les scores via set-score, d'effectuer/cocher des tâches de roadmap et de réguler la charge cognitive et la priorité en interrogeant obligatoirement Henri via ask_question à chaque point d'étape.
---

# Skill Guide — Project Memory CLI

Ce skill documente l'utilisation complète de l'interface en ligne de commande `project_memory_cli.py` pour interagir avec le plugin Obsidian **Project Memory** du coffre Obsidian de Henri Jamet.

---

## 📍 Chemins d'Accès Clés

- **Script CLI Python** : `C:\Users\Jamet\Documents\VoiceNotes\antigravity\scripts\project_memory_cli.py`
- **Fichier de Données JSON** : `C:\Users\Jamet\Documents\VoiceNotes\.obsidian\plugins\project-memory\data.json`
- **Racine du Vault Obsidian** : `C:\Users\Jamet\Documents\VoiceNotes`
- **Plugin Obsidian** : `C:\Users\Jamet\Documents\VoiceNotes\.obsidian\plugins\project-memory\`

---

## 🧮 Algorithme de Scoring & Priorisation

Chaque projet actif est représenté par une note Markdown dans le coffre comportant un tag de projet (ex: `#todo` ou `#project`) et **ne comportant pas** le tag d'archivage (`#done`).

Le score effectif d'un projet détermine sa priorité dynamique dans les révisions :

$$S_{\text{eff}} = \max\left(1.0,\, S_{\text{base}} + B_{\text{rot}} + U_{\text{deadline}} - M_{\text{temporal}}(K)\right)$$

### Composantes du calcul :

1. **Base Score** ($S_{\text{base}}$) : Valeur de base initiale (par défaut `100.0` ou fixée de `1.0` à `100.0`). Modifiée par les feedbacks utilisateur via la formule de rapprochement ($\text{facteur rf} = 0.2$) :
   - `more-often` / `emergency` (Friction / Urgence accrue) : $S_{\text{new}} = S + \text{rf} \times (100.0 - S)$
   - `less-often` (Aisance / Espacement) : $S_{\text{new}} = S - \text{rf} \times (S - 1.0)$
   - `ok` (Rythme nominal) : $S_{\text{new}} = S$ (maintien du score de base)
   - `finished` (Projet terminé) : Score ramené à $0.0$ (archivage avec tag `#done` et purge de `data.json`)
   - `non-projet` : Tags `#todo` / `#project` retirés et projet purgé de `data.json`

2. **Bonus de Rotation** ($B_{\text{rot}}$) : Favorise la découverte et l'alternance des projets :
   - S'accumule de **$+0.3$** à chaque session de travail effectuée sur un **autre** projet (via `feedback`, `work` ou `complete-task`).
   - Réinitialisé à **$0.0$** dès que ce projet fait l'objet d'une session de travail réelle.

3. **Urgence d'Échéance** ($U_{\text{deadline}}$) : Calculé automatiquement si la note possède un champ frontmatter `deadline` ou `due` (ex: `deadline: 2026-10-18`) :
   $$U_{\text{deadline}} = (100.0 - (S_{\text{base}} + B_{\text{rot}})) \times \exp(-0.1 \times \text{daysRemaining})$$
   - Comble progressivement jusqu'à 100% de l'écart restant à l'échéance ($S \to 100.0$).
   - Si l'échéance est aujourd'hui ou dépassée ($\text{daysRemaining} \le 0$), le facteur exponentiel vaut $1.0$ (urgence maximale).

4. **Malus Temporel de Récence** ($M_{\text{temporal}}(K)$) : Évite qu'un projet récemment travaillé ne monopolise la tête de liste lors des sessions de travail réelles :
   $$M_{\text{temporal}}(K) = K \times \text{rf} \times w \times (S_{\text{pre}} - 1.0)$$
   - $S_{\text{pre}} = S_{\text{base}} + B_{\text{rot}} + U_{\text{deadline}}$
   - $K = \sum_i \max\left(0,\, 1.0 - \frac{\Delta t_i}{6.0}\right)$ sommé sur l'ensemble des sessions de travail réelles enregistrées dans le tableau `recentWorkDates` survenues depuis moins de 6 heures ($\Delta t_i < 6.0$ heures).
   - $\text{rf} = 0.2$ (facteur de rapprochement) et $w = 0.5$ (`recencyPenaltyWeight`).
   - Le score effectif global reste toujours borné inférieurement par $1.0$ ($S_{\text{eff}} \ge 1.0$).
   - **Règle Stricte** : Le malus $K$ est **strictement réservé aux vraies sessions de travail d'Henri** (Pomodoro `work`, `complete-task`, ou retour utilisateur `feedback`).

5. **⚖️ Règle Fondamentale de Distinction : Retours Utilisateur & Sessions de Travail (`feedback`) vs Veille & Ajustements Agent (`set-score`)** :
   - **1. Retours Utilisateur & Sessions de Travail Réelles (`feedback "<projet>" <action>`)** :
     * Déclenché **exclusivement lors d'une session de travail réelle** (bilan post-tâche, fin de Pomodoro, clôture de session de travail, ou consigne explicite d'Henri dans la conversation).
     * **Obligation Stricte d'Interrogation Interactive (`ask_question`)** : Antigravity **NE DOIT PAS appliquer de mutation unilatérale arbitraire**. À chaque point d'avancement, fin de session de travail ou `/project-memory`, Antigravity **DOIT OBLIGATOIREMENT appeler `ask_question`** pour recueillir le niveau de stress / confort réel d'Henri parmi les 4 options canoniques : `["À l'aise", "OK", "Stressé", "Terminé"]` (avec le suffixe ` (Recommandé)` apposé sur l'option suggérée selon l'analyse de marge calendaire).
     * **Enregistre la session de travail réelle** : ajoute automatiquement le timestamp UTC dans `recentWorkDates` pour appliquer le malus temporel $K$ anti-effet-tunnel dégressif sur 6 heures ($M_{\text{temporal}}(K)$).
     * **Valide le jalon synchrone** : met à jour `lastSatisfiedMilestoneDate = now` si la session correspond à l'échéance.
     * **Gère la rotation des projets** : réinitialise le bonus de rotation $B_{\text{rot}}$ du projet à **`0.0`** et applique **`+0.3`** à tous les autres projets actifs.
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

6. **Ordre de Priorité & Évaluation Initiale Obligatoire** :
   - Les **nouveaux projets non révisés** (`totalReviews == 0`) font l'objet d'une **évaluation initiale obligatoire** via le Protocole Dual-Track : exploration contextuelle (Obsidian, AIVC, Spark) par sous-agents et attribution d'un score explicite de $1.0$ à $100.0$ avec `set-score`, jusqu'à ce qu'il reste 0 projet non révisé (`0 unreviewed`).
   - Les **projets déjà révisés** (`totalReviews > 0`) sont classés par `Effective Score` décroissant (`list --reviewed`).

7. **Gestion des Échéances & Jalons (`deadline` & `milestone`) & Règle Fondamentale de Distinction** :
   - **`deadline:` (Date Limite Dure)** :
     - Réservé **EXCLUSIVEMENT aux soumissions d'articles académiques** (ex: TheWebConf, AAAI, CSUR, FAccT, AAMAS), **dépôts légaux/administratifs** (ex: SPOP Permis B avant le 30 septembre), ou **livraisons contractuelles fermes**.
     - Format ISO obligatoire : `YYYY-MM-DD` (ex: `deadline: 2026-10-18` ou `due: 2026-10-18`).
     - Sert de base mathématique de calcul pour l'urgence d'échéance $U_{\text{deadline}}$.
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

## 🧠 Protocole de Gestion de la Charge Cognitive & Interrogation Interactive du Stress

Antigravity a pour mission fondamentale de préserver la sérénité et l'énergie cognitive d'Henri en adaptant dynamiquement l'agenda et la granularité d'accompagnement via une écoute active et interactive de son ressenti réel.

### 1. Principe Fondamental : Obligation Stricte d'Interrogation Interactive (`ask_question`)
> [!IMPORTANT]
> **OBLIGATION STRICTE D'INTERROGER HENRI SUR SON NIVEAU DE STRESS / CONFORT** :
> - **Antigravity NE DOIT JAMAIS appliquer de mutation unilatérale arbitraire de feedback sans interroger Henri.**
> - À chaque **point d'avancement**, **accomplissement de tâche (`complete-task`)**, **fin de session Pomodoro / `/work`**, **clôture de session de travail** ou **invocation manuelle `/project-memory`**, Antigravity **DOIT OBLIGATOIREMENT appeler l'outil `ask_question`** pour recueillir son niveau de stress / confort réel.
> - L'interrogation doit comporter **strictement les 4 options canoniques dans l'ordre suivant** :
>   1. `À l'aise` (ou `À l'aise (Recommandé)`)
>   2. `OK` (ou `OK (Recommandé)`)
>   3. `Stressé` (ou `Stressé (Recommandé)`)
>   4. `Terminé` (ou `Terminé (Recommandé)`)
> - Le suffixe ` (Recommandé)` est **obligatoirement apposé sur l'unique option conseillée** par Antigravity suite à l'analyse objective de la marge calendaire résiduelle.

### 2. Calcul Objectif de la Recommandation (Marge Calendaire & Buffer 20-30%)
Avant de poser la question interactive via `ask_question`, Antigravity calcule l'option à recommander selon des critères factuels :
- **`Stressé (Recommandé)`** : Marge temporelle résiduelle avant deadline dure < 20-30%, point de blocage technique critique non résolu, dépendance externe bloquante, ou charge lourde imminente.
- **`OK (Recommandé)`** : Progression nominale, marge confortable (> 30%), rythme maîtrisé, pas de friction majeure.
- **`À l'aise (Recommandé)`** : Forte avance sur planning, livrables intermédiaires en avance, sujet totalement maîtrisé nécessitant un espacement au profit d'autres urgences.
- **`Terminé (Recommandé)`** : Tous les livrables du projet sont intégralement finalisés et validés.

### 3. Matrice de Conversion & Impact sur la Priorisation & Charge Cognitive

Dès qu'Henri sélectionne son option dans le prompt `ask_question`, Antigravity exécute la commande CLI correspondante (`feedback "<projet>" <action>`) :

| Option Sélectionnée | Action CLI Exécutée | Évolution du Score | Impact sur la Charge Cognitive & Priorisation |
| :--- | :--- | :--- | :--- |
| **`À l'aise`** | `feedback "<projet>" less-often` | Réduction de priorité : $S_{\text{new}} = S - 0.2 \times (S - 1.0)$ | **Allègement & Espacement** : Le projet est espacé dans la file pour libérer la bande passante cognitive sur les dossiers plus complexes. Horodate dans `recentWorkDates` et applique le malus $K$. |
| **`OK`** | `feedback "<projet>" ok` | Maintien du score : $S_{\text{new}} = S$ | **Rythme Nominal & Alternance Saine** : Progression conforme aux attentes. Horodate la session dans `recentWorkDates` (malus temporaire $M_{\text{temporal}}$) et applique $+0.3$ aux autres projets pour encourager la rotation. |
| **`Stressé`** | `feedback "<projet>" more-often` *(ou `emergency`)* | Hausse de priorité : $S_{\text{new}} = S + 0.2 \times (100.0 - S)$ | **Soutien Renforcé & Décompression** : Signal objectif de tension ou de retard. Le projet remonte en priorité pour qu'Antigravity prenne en charge les tâches lourdes et propose un découpage fin. Horodate dans `recentWorkDates`. |
| **`Terminé`** | `feedback "<projet>" finished` | Clôture : Score = $0.0$ (Tag `#done`) | **Libération Mentale Immédiate** : Le projet est archivé, taggé `#done` et purgé de la liste active dans `data.json`. La charge mentale associée est totalement évacuée. |

---

## 🚀 Répertoire des Commandes CLI

Toutes les commandes s'exécutent via l'interprète Python avec le chemin absolu du script :

```bash
python "C:\Users\Jamet\Documents\VoiceNotes\antigravity\scripts\project_memory_cli.py" <sous-commande> [options]
```

---

### 1. `list` — Lister et Classer les Projets

Affiche la liste des projets actifs classés par priorité/urgence dynamique.

#### Syntaxe
```bash
python "C:\Users\Jamet\Documents\VoiceNotes\antigravity\scripts\project_memory_cli.py" list [--top N | -n N] [--unreviewed] [--reviewed] [--clean-orphans] [--json]
```

#### Colonnes du Tableau CLI
- `Rank` : Rang du projet dans l'ordre de priorité.
- `Title` : Titre du projet / nom de la note Obsidian.
- `Eff.Score` : Score effectif $S_{\text{eff}}$ calculé en temps réel (intégrant base, rotation, deadline et malus temporel).
- `Base` : Score de base $S_{\text{base}}$ issu des feedbacks et évaluations.
- `Rot.Bonus` : Bonus de rotation $B_{\text{rot}}$ accumulé ($+0.3$ par session de travail sur un autre projet).
- `Deadline Urg.` : Valeur ajoutée par l'urgence d'échéance $U_{\text{deadline}}$.
- `Malus(K)` : Pénalité de récence temporelle déduite $M_{\text{temporal}}$ et coefficient d'activité récent $K$ (ex: `-6.2 (K=0.8)` ou `0.0 (K=0)`).
- `Deadline` : Date limite déclarée dans le frontmatter (`deadline` ou `due`).
- `Reviews` : Nombre total de révisions/sessions (`NEW` si non révisé).

#### Options
- `--top N` ou `-n N` *(int)* : Limite l'affichage aux $N$ premiers projets les plus prioritaires (ex: `--top 5`).
- `--unreviewed` ou `--new` *(flag)* : Affiche uniquement les nouveaux projets en attente d'évaluation initiale (`totalReviews == 0`).
- `--reviewed` *(flag)* : Affiche uniquement les projets déjà révisés et classés par ordre d'urgence effectif.
- `--clean-orphans` *(flag)* : Purge automatiquement les projets orphelins de `data.json` avant de lister les projets actifs.
- `--json` *(flag)* : Génère un tableau JSON structuré contenant tous les détails calculés des projets (incluant `malus_temporal`, `k_recency`, `recent_work_count`).

#### Exemple d'utilisation
```bash
# Lister les 5 nouveaux projets à évaluer et les 5 projets révisés les plus urgents
python "C:\Users\Jamet\Documents\VoiceNotes\antigravity\scripts\project_memory_cli.py" list --top 5

# Obtenir uniquement les projets révisés au format JSON
python "C:\Users\Jamet\Documents\VoiceNotes\antigravity\scripts\project_memory_cli.py" list --reviewed --json
```

---

### 2. `get` — Détails d'un Projet, Historique & Roadmap

Extrait l'ensemble des métriques d'un projet, le détail de ses sessions de travail récentes (`recentWorkDates`), son historique de révisions, ainsi que la liste des tâches roadmap (cases à cocher pendantes `[ ]` et complétées `[x]`).

#### Syntaxe
```bash
python "C:\Users\Jamet\Documents\VoiceNotes\antigravity\scripts\project_memory_cli.py" get "<project_path_or_name>" [--json]
```

#### Informations Affichées
- **Scores et Métriques** : $S_{\text{eff}}$, $S_{\text{base}}$, $B_{\text{rot}}$, $U_{\text{deadline}}$, $M_{\text{temporal}}(K)$, $K$, deadline, nombre de révisions et dernière date de révision.
- **Sessions de Travail Récentes (`recentWorkDates`)** : Liste des sessions enregistrées dans les 6 dernières heures avec leur ancienneté $\Delta t$, la contribution pondérée à $K$, et l'impact sur le malus temporel.
- **Historique de Révision** : Les dernières actions consignées (`ok`, `more-often`, `less-often`, etc.) avec le score résultant.
- **Tâches Roadmap** : Tâches en attente `[ ]` et accomplies `[x]` avec leurs numéros de ligne dans la note.

#### Arguments & Options
- `<project_path_or_name>` *(string)* : Chemin relatif dans le coffre (ex: `"Projets/MonProjet.md"`) ou titre/nom du fichier sans extension (ex: `"MonProjet"`). Le CLI prend en charge la résolution floue (fuzzy matching).
- `--json` *(flag)* : Renvoie l'intégralité des données du projet au format JSON structuré.

#### Exemple d'utilisation
```bash
python "C:\Users\Jamet\Documents\VoiceNotes\antigravity\scripts\project_memory_cli.py" get "Composer une musique pour orchestre"
```

---

### 3. `feedback` — Enregistrer le Feedback Utilisateur & Session de Travail

Enregistre l'évaluation issue du retour recueilli via `ask_question` auprès d'Henri (ou consigne explicite dans la conversation) dans `data.json`, met à jour ses scores et son historique, horodate la session dans `recentWorkDates` (appliquant le malus $K$ dégressif sur 6h pour prévenir l'effet tunnel) et applique la rotation des bonus (+0.3 aux autres projets).

> [!IMPORTANT]
> **Règle d'Usage de `feedback`** :
> - **Réservé EXCLUSIVEMENT aux sessions de travail réelles** suite au retour recueilli interactivement via `ask_question` auprès d'Henri (ou consigné suite à une demande explicite d'Henri dans la conversation).
> - **L'Agent NE DOIT PAS utiliser `feedback` lors de la veille ou du triage autonome** (utiliser `set-score` à la place).

#### Syntaxe
```bash
python "C:\Users\Jamet\Documents\VoiceNotes\antigravity\scripts\project_memory_cli.py" feedback "<project_path_or_name>" <action>
```

#### Actions disponibles (`<action>`)
- `less-often` : Réduit la priorité du projet (sélection « À l'aise » : aisance constatée, avance sur planning, charge allégée).
- `ok` : Maintient le score actuel (sélection « OK » : rythme maîtrisé, session de travail nominale).
- `more-often` : Augmente la priorité du projet (sélection « Stressé » : friction détectée, marge faible, besoin de suivi rapproché).
- `emergency` : Augmente fortement la priorité (urgence critique).
- `finished` : Marque le projet comme terminé (sélection « Terminé » : score ramené à $0.0$, tag `#done` ajouté, purge de `data.json`).
- `non-projet` : Marque la note comme un **non-projet** (note de mémoire, résumé, pensée sans livrables ni feuille de route). Les tags `#todo` et `#project` sont retirés du frontmatter YAML et la note est purgée des projets actifs.

#### Comportement Système de `feedback` :
1. Met à jour le score de base $S_{\text{base}}$ et la date de dernière revue `lastReviewDate`.
2. Consigne l'entrée dans l'historique `reviewHistory`.
3. Ajoute automatiquement le timestamp UTC actuel dans `recentWorkDates` (activant le malus temporel $M_{\text{temporal}}(K)$ dégressif sur 6 heures pour prévenir l'effet tunnel).
4. Enregistre `lastSatisfiedMilestoneDate = now` pour valider le cycle de jalon.
5. Réinitialise le `rotationBonus` $B_{\text{rot}}$ du projet à **`0.0`** et incrémente le `rotationBonus` $B_{\text{rot}}$ de **tous les autres projets actifs de $+0.3$**.
6. Met à jour les statistiques globales (`totalReviews`, etc.).

#### Exemples d'utilisation
```bash
# Espacement de priorité suite au choix "À l'aise"
python "C:\Users\Jamet\Documents\VoiceNotes\antigravity\scripts\project_memory_cli.py" feedback "MonProjet" less-often

# Maintien de score suite au choix "OK"
python "C:\Users\Jamet\Documents\VoiceNotes\antigravity\scripts\project_memory_cli.py" feedback "MonProjet" ok

# Hausse de priorité suite au choix "Stressé"
python "C:\Users\Jamet\Documents\VoiceNotes\antigravity\scripts\project_memory_cli.py" feedback "MonProjet" more-often
```

---

### 4. `set-score` — Calibrer la Priorité par l'Agent & Veille (Score 1 à 100)

Définit directement le score d'urgence d'un projet ($1.0$ à $100.0$) et comptabilise la révision (`totalReviews`) **sans altérer `recentWorkDates` ni imposer de malus temporel $K$**.

> [!IMPORTANT]
> **Règle d'Usage de `set-score`** :
> - **OBLIGATOIRE pour l'Agent lors de toute action autonome de veille, de triage ou de réévaluation** (cycles Dream Vague 2 & Vague 3, veille matinale, qualification du portefeuille `0 unreviewed`).
> - **OBLIGATOIRE lors d'une demande d'Henri hors session de travail** (« rends ce projet plus urgent », « calibre ce projet à 80 »).
> - Permet d'ajuster précisément la priorité sans simuler de fausse session de travail d'Henri ($K = 0.0$, jalons futurs intacts, pas de rotation induite).

#### Syntaxe
```bash
python "C:\Users\Jamet\Documents\VoiceNotes\antigravity\scripts\project_memory_cli.py" set-score "<project_path_or_name>" <score_1_100>
```

#### Arguments & Options
- `<project_path_or_name>` *(string)* : Chemin relatif dans le coffre ou nom du projet.
- `<score_1_100>` *(float)* : Valeur numérique du score d'urgence entre `1.0` (faible priorité) et `100.0` (urgence maximale).

#### Exemples d'utilisation
```bash
# Évaluation initiale obligatoire d'un nouveau projet non révisé (0 unreviewed)
python "C:\Users\Jamet\Documents\VoiceNotes\antigravity\scripts\project_memory_cli.py" set-score "Digital Language Learning Platform" 95.0

# Réajustement de priorité par l'Agent lors de la veille Dream suite à la détection d'un email critique
python "C:\Users\Jamet\Documents\VoiceNotes\antigravity\scripts\project_memory_cli.py" set-score "TheWebConf 2027" 92.0
```

---

### 5. `complete-task` — Cocher une Tâche Roadmap

Recherche une case à cocher non cochée `[ ]` correspondant à un extrait de texte dans la note du projet, la transforme en case cochée `[x]`, réécrit le fichier Markdown et horodate la session de travail dans `recentWorkDates` (réinitialisation du bonus de rotation du projet et $+0.3$ sur tous les autres projets).

> [!IMPORTANT]
> **COMPORTEMENT POST-TÂCHE & INTERROGATION INTERACTIVE (`ask_question`)** :
> Dès l'exécution de `complete-task`, la tâche est cochée et la session de travail automatiquement horodatée. Antigravity **DOIT OBLIGATOIREMENT appeler `ask_question`** pour interroger Henri avec les 4 options canoniques dans l'ordre strict `["À l'aise", "OK", "Stressé", "Terminé"]` (en apposant ` (Recommandé)` sur l'option conseillée selon la marge calendaire) afin d'enregistrer son ressenti réel et d'ajuster le score via `feedback "<projet>" <action>`.

#### Syntaxe
```bash
python "C:\Users\Jamet\Documents\VoiceNotes\antigravity\scripts\project_memory_cli.py" complete-task "<project_path_or_name>" "<task_text>"
```

#### Arguments
- `<project_path_or_name>` *(string)* : Chemin relatif ou nom du projet.
- `<task_text>` *(string)* : Extrait du texte de la tâche à cocher.

#### Exemple d'utilisation
```bash
python "C:\Users\Jamet\Documents\VoiceNotes\antigravity\scripts\project_memory_cli.py" complete-task "Composer une musique" "Rédiger la partition d'ouverture"
```

---

### 6. `work` — Démarrer une Session Pomodoro Active & Pause

Démarre une session de travail Pomodoro sur un projet. La durée de la session est déterminée automatiquement par le paramètre `pomodoroDuration` configuré dans le fichier `data.json` du plugin (durée configurée par Henri dans les réglages Obsidian, actuellement 60 minutes / 1h), à moins qu'une durée spécifique ne soit fournie via l'option `--duration N`.

> [!IMPORTANT]
> **RÈGLE D'OR DU POMODORO PERMANENT (ZÉRO TRAVAIL SANS POMODORO)** :
> - **Interdiction Formelle** : Il est formellement interdit de travailler sur un projet sans qu'un Pomodoro actif ne soit en cours d'exécution en arrière-plan (`work "<projet>"` ou timer calqué sur `data.json`, 60 min par défaut).
> - **Lancement Automatique Systématique** : Dès le début effectif de tout travail sur un projet quel qu'il soit (note taggée `#todo`/`#project`, `/teacher`, `/work`, rédaction, apprentissage), exécuter **IMMÉDIATEMENT et sans attendre** la commande CLI en arrière-plan : `python antigravity/scripts/project_memory_cli.py work "<NomDuProjet>"`. Interdiction d'attendre une consigne explicite ou d'imposer une durée arbitraire (la durée configurée dans `data.json`, actuellement 60 min, est appliquée par défaut). Pause obligatoire de 5 min à l'échéance.
> - **Enchaînement et Relance après Feedback** : Dès qu'un Pomodoro se termine et qu'Henri donne son feedback (`ask_question`) :
>   - *Même projet* : Si Henri continue sur le même projet ➔ Relance IMMÉDIATE et automatique d'un nouveau Pomodoro (durée par défaut de `data.json`, 60 min) sur ce projet.
>   - *Changement de projet* : Si Henri change de projet ➔ Lancement IMMÉDIAT du Pomodoro sur le nouveau projet.
>   - *Transition douce* : En cas de transition douce (finalisation de l'ancien en démarrant le nouveau) ➔ Lancement IMMÉDIAT du Pomodoro sur le NOUVEAU projet, tout en laissant les sous-agents de l'ancien projet terminer leur exécution en arrière-plan.
> - **Exception Unique** : Seules les questions ponctuelles isolées et hors projet (1 question/réponse triviale de 30 secondes) peuvent se passer de Pomodoro.
> - **Auto-Suffisance Absolue de la Commande `work` (Zéro Timer Manuel `schedule`)** : La commande CLI `work` exécutée en arrière-plan via `run_command` dort pendant toute la durée nominale (par défaut 60 min). À son échéance, le processus se termine et réveille automatiquement Antigravity via le système push réactif. **Il est FORMELLEMENT INTERDIT d'armer un timer manuel `schedule` en parallèle d'un Pomodoro `work`.**

#### Syntaxe
```bash
python "C:\Users\Jamet\Documents\VoiceNotes\antigravity\scripts\project_memory_cli.py" work "<project_path_or_name>" [--duration N]
```

#### Arguments & Options
- `<project_path_or_name>` *(string)* : Chemin relatif dans le coffre (ex: `"Projets/MonProjet.md"`) ou titre/nom du fichier (résolution floue supportée).
- `--duration N` *(int)* : Durée personnalisée de la session Pomodoro en minutes (outrepasse la valeur `pomodoroDuration` de `data.json`).

#### Workflow d'Interaction d'Antigravity
1. **Lancement & Réveil Automatique par Processus** : Antigravity lance la commande `work` en tâche de fond (`run_command`). La terminaison naturelle du processus de fond réveille automatiquement Antigravity à l'échéance exacte de la session Pomodoro, sans aucun timer manuel `schedule`.
2. **Incitation Obligatoire à la Pause (5 min)** : Dès la fin de la session Pomodoro, Antigravity doit **obligatoirement** inviter Henri à effectuer une pause de 5 minutes avant d'évaluer l'avancement ou de poursuivre le travail.
3. **Interrogation Interactive du Stress (`ask_question`) & Feedback** : À la fin de la session ou lors du bilan d'étape, Antigravity évalue lucidement la progression selon les signaux réels (marge calendaire, fluidité d'exécution, complexité), détermine l'option conseillée avec le suffixe ` (Recommandé)`, et interroge **obligatoirement** Henri via `ask_question` avec les 4 options canoniques dans l'ordre strict : `["À l'aise", "OK", "Stressé", "Terminé"]`. Suite à sa réponse, Antigravity exécute `feedback "<projet>" <action>`.
4. **Recommandation Proactive & Relance** : Suite au bilan ou au moment de la pause, Antigravity recommande de manière proactive l'un des 3 projets les plus urgents suivants et enchaîne immédiatement le Pomodoro approprié.

#### Protocole d'Évaluation Autonome, Anti-Biais & Rigueur Réaliste (Anti-Confirmation Bias & Anti-Optimistic Nihilism)
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

#### Exemple d'utilisation
```bash
# Démarrer une session de travail Pomodoro standard avec attente jusqu'à terme
python "C:\Users\Jamet\Documents\VoiceNotes\antigravity\scripts\project_memory_cli.py" work "Digital Language Learning Platform"

# Démarrer une session de 45 minutes avec durée spécifique
python "C:\Users\Jamet\Documents\VoiceNotes\antigravity\scripts\project_memory_cli.py" work "Digital Language Learning Platform" --duration 45
```

---

### 7. `stop-work` (ou `cancel-work` / `stop`) — Interrompre Proprement un Pomodoro & Enregistrer le Temps Proportionnel

Permet d'interrompre proprement une session Pomodoro en cours (ou d'enregistrer manuellement une session partielle).

Lors de l'interruption :
1. **Calcul du temps réel** : Calcule avec précision le temps écoulé $T_{\text{elapsed}}$ en minutes.
2. **Statistiques globales** : Incrémente le temps global passé (`globalStats.totalPomodoroTime += T_elapsed`).
3. **Poids proportionnel** : Calcule le ratio d'accomplissement $r = \frac{T_{\text{elapsed}}}{T_{\text{target}}}$.
4. **Malus temporel proportionnel** : Enregistre la session dans `recentWorkDates` avec son ratio $r$, appliquant une pénalité de récence proportionnelle au temps réellement travaillé ($k_i = r \times (1.0 - \Delta t / 6.0)$).
5. **Bonus de rotation** : Réduit proportionnellement le bonus de rotation du projet travaillé et applique $+0.3 \times r$ aux autres projets.
6. **Validation de jalon** : Si $r \ge 0.5$, valide le jalon synchrone (`lastSatisfiedMilestoneDate = now`).

#### Syntaxe
```bash
# Interrompt la session en cours d'exécution
python "C:\Users\Jamet\Documents\VoiceNotes\antigravity\scripts\project_memory_cli.py" stop-work

# Enregistrement manuel d'une session partielle sans daemon actif
python "C:\Users\Jamet\Documents\VoiceNotes\antigravity\scripts\project_memory_cli.py" stop-work "NomDuProjet" --elapsed 12.5 --target-duration 35
```

---

### 8. `status-work` (ou `status` / `active-pomodoro`) — État de la Session Pomodoro Active

Affiche la progression en temps réel de la session Pomodoro active (temps écoulé, temps restant, pourcentage, PID du processus, ou état `idle`).

#### Syntaxe
```bash
python "C:\Users\Jamet\Documents\VoiceNotes\antigravity\scripts\project_memory_cli.py" status-work [--json]
```

---

### 9. `clean-orphans` — Nettoyer les Projets Orphelins de `data.json`

Scanne le coffre pour détecter et purger de `data.json` toutes les entrées orphelines (fichiers supprimés, renommés ou n'ayant plus de tag `#todo` / `#project`).

#### Syntaxe
```bash
python "C:\Users\Jamet\Documents\VoiceNotes\antigravity\scripts\project_memory_cli.py" clean-orphans [--dry-run] [--json]
```

#### Arguments & Options
- `--dry-run` *(flag)* : Mode simulation. Liste les entrées orphelines détectées dans `data.json` sans modifier le fichier sur le disque.
- `--json` *(flag)* : Renvoie la liste des entrées nettoyées au format JSON.

#### Exemple d'utilisation
```bash
# Vérifier les projets orphelins sans altérer data.json
python "C:\Users\Jamet\Documents\VoiceNotes\antigravity\scripts\project_memory_cli.py" clean-orphans --dry-run

# Exécuter le nettoyage effectif
python "C:\Users\Jamet\Documents\VoiceNotes\antigravity\scripts\project_memory_cli.py" clean-orphans
```

---

## 🎯 Comportement Lors de l'Invocation Manuelle par Henri (`/project-memory`)

Lorsque Henri invoque manuellement le skill ou la slash-command `/project-memory`, Antigravity adapte son comportement selon le contexte temporel de la conversation :

### 1. En Début de Conversation (Orientation & Choix de Focus)
* **État Global** : Fournir une vue synthétique des projets actifs (total des projets révisés et détection des éventuels nouveaux projets non révisés).
* **Top 3 Urgent** : Présenter immédiatement les **Top 3 projets révisés les plus urgents** (`list --reviewed --top 3`) sous forme de liens Markdown cliquables avec leurs scores effectifs $S_{\text{eff}}$, leurs échéances futures réelles (deadlines dures et jalons de synchronisation réels, à l'exclusion stricte de tout événement passé) et le malus temporel éventuel.
* **Recommandations Stratégiques** : Formuler une recommandation concrète sur le meilleur projet à prioriser pour démarrer la session.

### 2. En Milieu de Conversation / Clôture de Session de Travail (Bilan & Enchaînement)
* **Vérification & Mise à Jour des Notes Obsidian (Mandatoire)** : Moment privilégié pour **auditer et synchroniser la note maîtresse et toutes les sous-notes liées du projet dans Obsidian**. Vérifier qu'elles reflètent fidèlement 100% des avancées, décisions prises, arbitrages, travaux effectués et nouveaux jalons de la session.
* **Bilan d'Avancement Factuel** : Résumer précisément ce sur quoi Henri et Antigravity viennent de travailler (tâches réalisées, décisions clés, note de projet mise à jour).
* **Interrogation Interactive du Stress (`ask_question`) & Évolution du Score** :
  * Appeler obligatoirement `ask_question` avec les 4 options canoniques dans l'ordre strict `["À l'aise", "OK", "Stressé", "Terminé"]` (avec le suffixe ` (Recommandé)` apposé sur l'option conseillée selon la marge calendaire).
  * Exécuter l'action CLI correspondante (`feedback "<projet>" <action>`) choisie par Henri.
  * Indiquer factuellement le score de base $S_{\text{base}}$ et le score effectif $S_{\text{eff}}$ mis à jour.
  * Préciser le **malus temporel cumulatif** appliqué via `recentWorkDates` (valeur de $K$, nombre de sessions consécutives dans les 6h, pénalité en points).
* **Enchaînement Suivant (Top 3)** : Présenter immédiatement les **Top 3 projets les plus urgents suivants** sous forme de liens Markdown cliquables pour choisir le prochain focus de travail ou enchaîner après la pause de 5 minutes.

---

## 💡 Workflows Recommandés pour Antigravity

0. **Affichage Système & Lien Cliquable de la Note de Projet (MANDATOIRE DÈS LE DÉBUT)** :
   - Dès qu'une session de travail démarre sur un projet (ou qu'un projet est sélectionné), Antigravity **DOIT OBLIGATOIREMENT fournir au tout début de son message le lien Markdown cliquable absolu vers la note du projet dans le coffre Obsidian** (ex: `[Nom de la Note](file:///C:/Users/Jamet/Documents/VoiceNotes/notes/NomProjet.md)`).
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
   - **Zéro Travail sans Pomodoro** : Lancer systématiquement `work "<NomProjet>"`. Au tout début, afficher immédiatement le lien Markdown cliquable vers la note Obsidian. À l'échéance, faire respecter la pause obligatoire de 5 minutes.
   - **Interrogation Interactive & Enchaînement Immédiat** : Interroger obligatoirement Henri via `ask_question` avec les 4 options canoniques `["À l'aise", "OK", "Stressé", "Terminé"]` (avec la recommandation calendaire), puis appliquer le feedback choisi via `feedback "<NomProjet>" <action>`.
   - **Relance & Enchaînement Permanent** :
     * *Même projet* : Si Henri continue sur le même projet ➔ Relance IMMÉDIATE et automatique d'un nouveau Pomodoro (durée par défaut de `data.json`, 60 min) sur ce projet.
     * *Changement de projet* : Si Henri change de projet ➔ Lancement IMMÉDIAT du Pomodoro sur le nouveau projet.
     * *Transition douce* : En cas de transition douce (finalisation de l'ancien en démarrant le nouveau) ➔ Lancement IMMÉDIAT du Pomodoro sur le NOUVEAU projet, tout en laissant les sous-agents de l'ancien projet terminer leur exécution en arrière-plan.
     * Seules les questions ponctuelles isolées et hors projet (1 question/réponse triviale de 30 secondes) peuvent se passer de Pomodoro.

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
     1. **Index des Sous-Notes en Haut de Page (MANDATOIRE)** : Placer systématiquement un bloc **Index des Sous-Notes & Documents Clés `[[Sous-Note.md]]` tout en haut du document** (immédiatement sous le titre H1 et le callout de cadrage) pour naviguer instantanément dans le réseau du projet.
     2. **Lisibilité & Concision Radicale** : La note maîtresse doit rester un tableau de bord ultra-lisible, concis et propre. Elle ne contient que les mots-clés, faits capitaux, nombres clés, tableaux synthétiques et diagrammes Mermaid.
     3. **Déport Systématique des Détails en Sous-Notes** : Tout développement approfondi, protocole technique lourd, historique de factures ou compte-rendu exhaustif DOIT être **déporté dans une sous-note dédiée** liée dans l'index du haut.
     4. **Zéro Paragraphe Narratif & Zéro Liste Interminable** : Bannir les blocs de texte denses. Privilégier les tableaux synthétiques, émojis, alertes GitHub compactes (`> [!NOTE]`) et diagrammes.
     5. **Accumulation d'informations de haut niveau** : Toujours **ajouter** les décisions stratégiques, arbitrages et résultats majeurs du travail effectué.
     6. **Interdiction de suppression arbitraire** : Ne JAMAIS supprimer d'informations existantes sans l'accord d'Henri.
     7. **Audit d'obsolescence** : S'assurer que la note maîtresse et ses sous-notes contiennent uniquement des informations exactes et à jour.
     8. **Rigueur sur les Échéances & Frontmatter** : Vérifier que le frontmatter respecte strictement la distinction `deadline:` (date limite dure académique/légale/contractuelle) vs `milestone:` (réunion synchrone planifiée uniquement), sans inventer de faux jalons et sans laisser de dates passées dans les champs d'échéance active.

---

## 📌 Autonomie Stricte (1 Note = 1 Projet) & Gestion des Notes Auxiliaires

> **Principe Fondamental : 1 Note taggée `#todo` / `#project` = 1 Projet Autonome** :
> Chaque note comportant le tag `#todo` ou `#project` est un projet autonome à part entière, suivi et priorisé individuellement dans `project-memory`. Il n'y a **aucune hiérarchie implicite parent-enfant** ni d'absorption automatique par graphe de wikilinks (`[[...]]`). Les liens entre notes sont de simples références documentaires hypertextes.
>
> **Gestion des Notes Auxiliaires, Fiches Dérivées & Non-Projets** :
> Si une note (sous-note technique, compte-rendu, fiche de travail, pensée ponctuelle) ne doit **pas** constituer un projet distinct dans `project-memory` :
> 1. **Retrait manuel des tags** : Retirer simplement le tag `#todo` ou `#project` du frontmatter et du corps de la note.
> 2. **Commande `non-projet`** : Exécuter `python project_memory_cli.py feedback "<nom>" non-projet` pour retirer automatiquement les tags et purger la note de `data.json`.
> 3. **Nettoyage orphelin** : Exécuter `python project_memory_cli.py clean-orphans` (ou `list --clean-orphans`) pour maintenir `data.json` parfaitement synchronisé avec le coffre.

---

## 🔍 Traitement des Problèmes & Résolution d'Erreurs

- **Note non trouvée** : Le CLI effectue une recherche floue. Si un nom partiel est fourni et ne correspond à aucun fichier, le script signale une erreur. Vérifier le titre exact dans Obsidian.
- **Tâche non trouvée lors de `complete-task`** : Le script affiche la liste de toutes les tâches pendantes disponibles dans la note pour permettre d'ajuster l'extrait de recherche `<task_text>`.
- **Encodage Windows** : Le script gère automatiquement l'encodage `utf-8` sur stdout sous Windows.
