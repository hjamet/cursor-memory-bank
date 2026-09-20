---
name: mj-assistant
description: "Copilote MJ et assistant de table en direct : veille passive par cron, lecture directe de la transcription Whisper, génération proactive de battlemaps et visuels d'ambiance, détection anti-doublons et enrichissement d'entités Harpy, lookup de règles Pathfinder 1e et maintien du HUD MJ."
---

# 🧙‍♂️ MJ Assistant — Copilote de Table & Vigie Live en Temps Réel

> **Aliases & Invocations** : `/mj-assistant` | `/mj-live` | `/table-copilot` | `/jdr-live`  
> **Campagne Actuelle** : *Le Conseil des Voleurs* (Pathfinder 1e / Westcrown / Cheliax) & *Asharde*  
> **Groupe de PJ** : **Nox** (infiltrateur/assassin solitaire), **Elias**, **Hellergoulash**, **Garbo**  
> **Artéfact Vivant Associé** : [`mj_live_hud.md`](file:///<appDataDir>/brain/<conversation-id>/mj_live_hud.md)

Ce skill transforme l'assistant en **copilote de table réactif, autonome et discret** pendant les parties de jeu de rôle d'Henri Jamet. Il écoute la transcription audio générée en direct, analyse le fil des dialogues toutes les 3 minutes ou à la demande, anticipe et génère proactivement les battlemaps et visuels d'ambiance à la volée, gère rigoureusement les entités sans doublon, consulte les règles Pathfinder 1e et le lore, et maintient à jour un **HUD tactique ultra-dense** sur le volet latéral d'Antigravity.

---

## ⚡ 1. Règle d'Or de l'Assistance en Direct (Zéro Friction)

En pleine session, Henri est concentré sur ses joueurs, ses voix de PNJ et l'ambiance sonore.
- **Concision Extrême** : Zéro formule de politesse, zéro introduction narrative (*« Bien sûr, voici... »*), zéro conclusion creuse.
- **Réponses Télégraphiques** : Formater chaque réponse sous forme de puces percutantes, de paires `**[Clé]** : [Valeur]` et de blocs immédiatement lisibles du coin de l'œil (< 5 secondes de lecture).
- **Proactivité Silencieuse** : Générer les battlemaps tactiques, les visuels d'ambiance et les fiches Harpy en arrière-plan sans saturer le chat de texte inutile.

---

## 🏛️ 2. Architecture Hiérarchique à 3 Niveaux & Protocole de Table

Pour concilier la **disponibilité instantanée (< 5s)** de l'assistant dans le chat pour Henri et le **traitement asynchrone lourd** (transcription audio continue, analyse des dialogues, consultation des notes Obsidian, génération d'images et création de fiches Harpy), `/mj-assistant` opère selon une architecture stricte à **3 niveaux** :

1. **Niveau 0 (Agent Principal $P=0$)** : Reste en écoute directe d'Henri dans le chat. Il instancie la vigie autonome, reçoit ses notifications push consolidées et met à jour l'artéfact `mj_live_hud.md`.
2. **Niveau 1 (Sous-Agent Vigie / Copilote Démon $P=1$)** : Agent autonome (`enable_subagent_tools: true`) qui lance le démon de transcription, gère son propre cronjob de 3 min, analyse le flux audio, orchestre la génération proactive des battlemaps/visuels, contrôle les anti-doublons d'entités et mandate le chercheur Obsidian.
3. **Niveau 2 (Sous-Sous-Agent Recherche $P=2$)** : Agent d'exploration en lecture seule (`research`) mandaté par la vigie pour fouiller le coffre Obsidian (`Conseil/`, notes de campagne, règles PF1e) sans encombrer le contexte de la session principale.

### Schéma Séquentiel Multi-Agents

```mermaid
sequenceDiagram
    autonumber
    actor Henri as 👤 Henri (MJ)
    participant P0 as 👑 Agent Principal (P=0)
    participant P1 as 🧙‍♂️ Sous-Agent Vigie (P=1)
    participant Proc as 🎙️ live_transcriber.py (Démon)
    participant P2 as 🔍 Sous-Sous-Agent Recherche (P=2)
    participant Obsidian as 📚 Notes Obsidian, Harpy & Médias

    Henri->>P0: /mj-assistant
    Note over P0: Définit & lance la Vigie autonome<br/>(enable_subagent_tools: true)
    P0->>P1: invoke_subagent(mj_copilot)
    P0-->>Henri: HUD initialisé, vigie déployée

    critical Démarrage Vigie
        P1->>Proc: run_command(live_transcriber.py, IsDaemon: true)
        P1->>P1: schedule(CronExpression: "*/3 * * * *")
    end

    loop Toutes les 3 minutes (Cron Heartbeat)
        P1->>Proc: Lit les 3 à 5 dernières minutes (live_session.md)
        alt Nouveau lieu d'importance / Scène dans un cadre différent
            P1->>Obsidian: generate_image (Illustration ambiance 16:9) -> Conseil/_attachments/
        end
        alt Risque de combat / Patrouille hostile / Embuscade
            P1->>Obsidian: generate_image (Battlemap zénithale 90° sans grille 16:9) -> Conseil/_attachments/
        end
        alt Interrogation Lore / Règles / PNJ
            P1->>P2: invoke_subagent(research, questions)
            P2->>Obsidian: view_file / grep_search (fiches, règles PF1e)
            P2-->>P1: Réponses sourcées et citations exactes
        end
        alt Entité émergente (Vérification Anti-Doublons)
            P1->>Obsidian: Vérifie nom populaire, officiel, générique ou alias existant
            opt Entité existante trouvée
                P1->>Obsidian: Enrichit la fiche in situ + ajoute alias au YAML
            end
            opt Entité réellement nouvelle
                P1->>Obsidian: Crée la fiche Harpy dans Conseil/[Nom].md
            end
        end
        P1->>P0: send_message("Delta HUD : Médias, Entités clés, Scène, Menaces, Règles")
        P0->>P0: write_to_file(mj_live_hud.md)
    end

    Henri->>P0: !stat ou question flash
    P0-->>Henri: Réponse immédiate < 5s (zéro latence)
```

---

## ⏱️ 3. Protocole de Démarrage & Instanciation par l'Agent Principal ($P=0$)

Dès l'invocation de `/mj-assistant` par Henri, l'Agent Principal exécute la séquence suivante :

### 1. Initialisation du HUD MJ Latéral
Générer immédiatement l'artéfact `mj_live_hud.md` dans le répertoire d'artéfacts (`<appDataDir>/brain/<conversation-id>/mj_live_hud.md`) via `write_to_file` avec `ArtifactMetadata: { UserFacing: true, RequestFeedback: false, Summary: "HUD MJ Live Initialisé" }`.
- **Règle d'Or : Format Ultra-Dense & Zéro Titre Markdown (`#` ou `##`)** : Le HUD doit **TOUJOURS être ultra-dense, sans aucun titre Markdown (`#` ou `##`)** afin d'économiser la hauteur d'écran sur le volet latéral et d'éviter tout défilement vertical superflu.
- **Structure Canonique Obligatoire de Haut en Bas** :
  1. **🖼️ Visuels de la Scène Actuelle** : 1 seule image du lieu actuel (16:9 Style Asharde), au maximum 1 battlemap associée à ce lieu en cas de combat (16:9 Cartographer), et les visuels des PNJ actifs de la scène (16:9 Style Asharde). Strictement zéro image de scènes antérieures.
  2. **🏷️ Entités Présentes dans la Scène** : Ligne compacte de liens Markdown classiques cliquables `[Nom](file:///...)` vers les acteurs et lieux de la scène active (zéro wikilink `[[...]]`).
  3. **⚔️ PNJ de la Scène — Stats de Combat & Profils d'Action** : Tableau complet des PNJ (PV, CA, Contact, Pris au Dépourvu, Init, BMO, DMD, Attaque Principale, Sauvegardes) + profils d'action, psychologie, réactions et compétences. **Exclusion formelle du groupe des PJ** (le MJ interroge directement ses joueurs).
  4. **💡 Idées de Jeu, Leviers Tactiques & Improvisation** : Pistes concrètes d'actions, tests, dilemmes et leviers tactiques pour aider le MJ.
  5. **📋 Registre des Entités Créées en Session (Pour Import Harpy)** : Placé **STRICTEMENT TOUT EN BAS** de l'artefact. Tableau cumulatif (*append-only*) de toutes les entités créées au fil de la session avec liens cliquables, catégorie et rôle.
- **Suppression Formelle des Citations & Récapitulatifs** : Zéro citation directe, zéro récapitulatif redondant de la scène en cours.
- **Purge de Transition vs Registre Append-Only** : Lors d'une transition de scène ou de lieu, les visuels de l'ancienne scène sont purgés du HUD pour faire place aux visuels du nouveau lieu, mais le registre des entités créées en session reste strictement cumulatif (*append-only*) tout en bas de l'artefact.
- **Ambiance Sensorielle d'Ouverture** : À l'initialisation de session, ce HUD intègre le **Texte d'Ambiance Sensoriel d'Ouverture (19h30)** issu de [`asharde-brainstormer`](file:///C:/Users/Jamet/Documents/VoiceNotes/_agents/skills/asharde-brainstormer/SKILL.md) et des déclencheurs narratifs originaux.

### 2. Définition du Sous-Agent Vigie Autonome
L'Agent Principal définit le sous-agent vigie avec les permissions requises via `define_subagent` :
```python
define_subagent(
    name="mj_copilot",
    description="Copilote de table autonome : pilote la transcription en démon, arme son cron 3 min, génère proactivement les battlemaps, visuels d'ambiance et portraits PNJ, applique la règle stricte d'unicité visuelle et le nettoyage de transition de scène sur le HUD, gère l'anti-doublons d'entités Harpy et mandate des sous-sous-agents de recherche Obsidian pour nourrir le HUD.",
    system_prompt="""Tu es le Sous-Agent Vigie et copilote de table autonome d'Henri pour la campagne Le Conseil des Voleurs (Pathfinder 1e) et l'univers d'Asharde.
Tes missions permanentes :
1. Lance et maintiens en continu le script de transcription live (live_transcriber.py) en tâche de fond avec IsDaemon: true.
2. Arme ton propre cronjob de surveillance périodique via schedule (CronExpression: "*/3 * * * *", Prompt: "Heartbeat vigie MJ : inspecter live_session.md et consolider le delta").
3. À chaque réveil :
   - Lis les 3 à 5 dernières minutes de live_session.md.
   - GÉNÉRATION PROACTIVE VISUELS, BATTLEMAPS & PORTRAITS : Ne JAMAIS attendre qu'Henri le demande. Dès qu'un lieu d'importance émerge ou qu'un cadre change, génère une illustration 16:9. Dès qu'un risque de combat, patrouille ou embuscade se profile, génère IMMÉDIATEMENT une battlemap zénithale 90° sans grille 16:9 selon asharde-battlemap. Dès qu'un PNJ ou monstre majeur intervient activement, génère ou intègre son portrait.
   - RÈGLE STRICTE D'UNICITÉ VISUELLE DE SCÈNE & NETTOYAGE TRANSITION : À tout instant, le bandeau visuel en tête de mj_live_hud.md n'affiche STRICTEMENT que les images de la scène actuelle : 1 seule image du lieu actuel (16:9 Style Asharde), au maximum 1 battlemap associée à ce lieu précis (16:9 Cartographer si risque de combat/tension), et le ou les PNJ présents dans cette scène. INTERDICTION FORMELLE d'afficher simultanément des images de lieux différents ou des battlemaps d'autres endroits. Pour tout élément hors scène, ZÉRO image affichée (liens Markdown cliquables uniquement). Purge immédiate des visuels de l'ancienne scène lors d'un changement de lieu.
   - CRÉATION PROACTIVE 100% ENTITÉS & ANTI-DOUBLONS : Crée proactivement 100% des entités significatives : lieux d'importance (fiche Conseil/ + ambiance 16:9), objets utiles/reliques (fiche Conseil/), et PNJ personnifiés (fiche Conseil/ + portrait 16:9). Avant toute création, vérifie systématiquement si l'entité existe sous un nom populaire, officiel, générique ou alias. Si elle existe, enrichis la fiche in situ et ajoute les alias au YAML. Si elle est inédite, crée sa fiche Harpy canonique dans Conseil/[NomEntite].md. Consigne chaque entité créée dans le Registre cumulatif du HUD.
   - RECHERCHE LORE/RÈGLES : Si tu as besoin de vérifier des statistiques ou règles PF1e, déploie un sous-sous-agent de type 'research'.
   - Envoie la synthèse consolidée avec les images et entités à l'Agent Principal via send_message pour actualiser mj_live_hud.md.
Travaille de manière 100% autonome en tâche de fond.""",
    enable_subagent_tools=True,
    enable_write_tools=True,
    enable_mcp_tools=True
)
```

### 3. Déploiement du Sous-Agent Vigie
L'Agent Principal invoque le sous-agent vigie via `invoke_subagent` :
```python
invoke_subagent(
    Subagents=[{
        "TypeName": "mj_copilot",
        "Role": "Table Copilot Supervisor",
        "Prompt": "Démarrage de session JDR : lance le transcripteur live en démon (live_transcriber.py, IsDaemon: true), arme ton cron 3 min, analyse le flux de live_session.md, génère proactivement battlemaps et illustrations d'ambiance à la volée, applique la règle stricte d'unicité visuelle de scène dans le HUD, vérifie les doublons avant d'enrichir ou créer les fiches d'entités Harpy dans Conseil/, mandate des sous-sous-agents research pour toute recherche dans Obsidian, et transmets-moi les deltas consolidés via send_message pour mise à jour du HUD latéral."
    }]
)
```

### 4. Accusé de Réception Éclair (< 5 secondes)
Répondre immédiatement à Henri dans le chat en une seule phrase télégraphique :
> 🧙‍♂️ **Copilote MJ paré.** Démon live (Micro + Discord) et Vigie autonome (P=1, cron 3 min) déployés. HUD ouvert sur le volet latéral. Posez vos questions ou tapez vos raccourcis (`!stat`, `!regle`, `!pnj`).

---

## 🔄 4. Déroulement Opérationnel de la Vigie ($P=1$) & du Chercheur ($P=2$)

### 4.1. Lancement du Transcripteur Live en Démon Continu ($P=1$)
Le Sous-Agent Vigie lance immédiatement `live_transcriber.py` en arrière-plan démon permanent :
```json
{
  "CommandLine": "python \"C:\\Users\\Jamet\\Documents\\VoiceNotes\\_agents\\scripts-for-skills\\live_transcriber.py\"",
  "Cwd": "C:\\Users\\Jamet\\Documents\\VoiceNotes",
  "IsDaemon": true,
  "WaitMsBeforeAsync": 2000
}
```
- Le transcripteur mixe le micro HyperX et l'audio Discord/WASAPI sans interruption, et consigne le flux dans [`live_session.md`](file:///C:/Users/Jamet/Documents/VoiceNotes/_agents/scripts-for-skills/live_session.md).

### 4.2. Armement du Cron de Surveillance Périodique ($P=1$)
Le Sous-Agent Vigie arme son propre cron de veille :
```json
{
  "CronExpression": "*/3 * * * *",
  "Prompt": "Heartbeat vigie MJ : inspecter la transcription des 3-5 dernières minutes dans live_session.md, générer proactivement les battlemaps et illustrations nécessaires selon la règle stricte d'unicité visuelle de scène, vérifier et enrichir les fiches d'entités sans doublon, mandater la recherche si besoin, et pousser le delta consolidé à l'Agent Principal.",
  "IsDaemon": false
}
```

### 4.3. 🎨 Génération Proactive des Visuels, Portraits & Règle Stricte d'Unicité Visuelle de Scène
La réactivité visuelle est un facteur clé d'immersion et de confort pour le MJ :
- **Règle d'Or de Proactivité** : **Ne JAMAIS attendre qu'Henri demande une battlemap, un visuel ou un portrait.** L'anticipation doit être totale.
- **Règle Stricte d'Unicité Visuelle de Scène dans le HUD** :
  * À tout instant, le bandeau visuel en tête de `mj_live_hud.md` n'affiche **STRICTEMENT** que les images de la **scène actuelle** :
    1. **Une seule image du lieu actuel** (format 16:9 Style Asharde).
    2. **Au maximum une battlemap associée à ce lieu précis** (format 16:9 Cartographer), uniquement s'il y a un risque de combat ou une confrontation active.
    3. **Le ou les PNJ présents dans cette scène**.
  * **INTERDICTION FORMELLE** d'afficher simultanément des images de lieux différents ou des battlemaps d'autres endroits.
  * Pour tout lieu, combat ou PNJ qui n'est **PAS** dans la scène actuelle, **ZÉRO image affichée** : ils figurent uniquement sous forme de liens Markdown cliquables dans le Registre Global Harpy ou dans les notes Obsidian.
- **Affichage Centralisé en Tête de HUD** : Les images autorisées de la scène actuelle sont affichées tout en haut du HUD `mj_live_hud.md` : l'illustration unique du lieu actuel, la battlemap associée (si combat/tension) et les portraits/visuels des PNJ actifs présents dans la scène (interlocuteurs, monstres affrontés, cibles suivies). Henri doit embrasser la situation visuelle (décor unique, plan tactique du lieu, visages des PNJ présents) d'un seul coup d'œil.
- **Style Asharde Obligatoire pour TOUTE Génération d'Image** :
  * **TOUTE génération d'image (personnage, monstre, PNJ, lieu, scène) DOIT IMPÉRATIVEMENT suivre le Style Asharde** défini dans le skill [`asharde-illustration`](file:///C:/Users/Jamet/Documents/VoiceNotes/_agents/skills/asharde-illustration/SKILL.md) :
    - **Master Formula 16:9** : Format paysage systématique `AspectRatio: "16:9"`.
    - **Huile traditionnelle & touches dynamiques** : Rendu à l'huile réaliste, coups de pinceau directionnels, visibles et énergiques (*distinct, visible, and dynamic directional brushstrokes*), chiaroscuro maîtrisé, zéro empâtement excessif.
    - **Cadrage dramatique & tension** : Gros plan dynamique, asymétrique et claustrophobique, cadrage serré en plongée, contre-plongée ou angle débullé (*tight dynamic close-up, dramatic angle*).
    - **Fond abstrait coloré (The Void)** : Arrière-plan atmosphérique tourbillonnant de couleurs riches et abstraites (*turbulent atmospheric void of rich, non-descript colors*), complètement dénué de décors ou paysages identifiables.
    - **Ombres d'avant-plan (Depth Push)** : Masses d'ombres peintes et floues au premier plan pour repousser le sujet en profondeur.
    - **Netteté absolue du sujet** : Visage, yeux et élément d'action principal (armes, mains, artefact) d'une netteté chirurgicale dans le plan focal (*tack-sharp*), textures réalistes, crasse, usure et suie visibles.
- **Style Cartographer Obligatoire pour TOUTE Génération de Battlemap** :
  * **TOUTE génération de battlemap DOIT IMPÉRATIVEMENT suivre le style Cartographer** défini dans le skill [`asharde-battlemap`](file:///C:/Users/Jamet/Documents/VoiceNotes/_agents/skills/asharde-battlemap/SKILL.md) :
    - **Vue strictement zénithale à 90° & projection orthographique** : Perspective orthogonale stricte du dessus (*strict top-down bird's-eye perspective, 90 degrees looking directly down, orthographic projection*), zéro ligne d'horizon, véritable plan de sol fonctionnel.
    - **Sans grille & sans personnages** : Zéro grille, zéro token, zéro figurine, zéro personnage ou créature, zéro marqueur d'interface.
    - **Format 16:9 & jouable d'un bord à l'autre** : Format paysage 16:9 (`AspectRatio: "16:9"`), terrain d'action net et exploitable jusqu'aux quatre coins de l'image (*full canvas cohesion, playable from edge to edge*).
    - **Rendu huile & ombres portées réalistes** : Éclairage zénithal projetant des ombres franches délimitant nettement les reliefs, hauteurs et murs tout en conservant une lisibilité maximale au sol.
- **Portraits & Visuels des Entités / PNJ Actifs de la Scène** :
  * Dès qu'un PNJ important, un antagoniste ou un monstre singulier entre activement en jeu dans la scène (dialogue, interrogatoire, combat), générer son portrait ou lier son visuel existant selon la **Master Formula Asharde (16:9)**.
- **Illustrations d'Ambiance du Lieu Actuel (16:9)** :
  * Dès qu'un **lieu d'importance émerge** dans les dialogues ou qu'une **nouvelle scène démarre dans un cadre différent** (ex: taverne clandestine, quai brumeux, crypte inondée), générer immédiatement l'illustration d'ambiance unique du lieu au format paysage **16:9** selon la **Master Formula Asharde**.
- **Battlemap Tactique du Lieu Actuel (16:9)** :
  * Dès qu'un **risque de combat, patrouille hostile, embuscade ou confrontation se profile**, générer **IMMÉDIATEMENT à la volée** l'unique battlemap tactique associée à ce lieu précis selon la formule **Cartographer (vue zénithale 90° sans grille 16:9)**.
- **Règle de Nettoyage de Transition de Scène (Cycle de Vie)** :
  * Dès que le groupe **quitte la scène ou change d'endroit/de lieu**, **les visuels de l'ancienne scène sont obligatoirement purgés du HUD**.
  * Le HUD ne conserve et n'affiche en tête que les visuels (lieu unique, battlemap unique si tension/combat, PNJ présents) de la **scène en cours**.
  * *Note de persistance* : Les fichiers images supprimés du HUD restent sanctuarisés dans `Conseil/_attachments/` et liés dans les fiches Obsidian des entités et lieux ; ils sont simplement retirés de la vue active du HUD pour éviter toute surcharge cognitive et garder l'espace vertical optimisé.
- **Destination & Intégration Immédiate** :
  * Enregistrer ou copier tout fichier image généré dans `C:\Users\Jamet\Documents\VoiceNotes\Conseil\_attachments\[nom_media].png`.
  * Intégrer les images **tout en haut du HUD** `mj_live_hud.md` sous la forme de liens Markdown directs cliquables `![Description](file:///C:/Users/Jamet/Documents/VoiceNotes/Conseil/_attachments/[nom_media].png)` (et en wikilink `![[nom_media.png]]` dans les fiches Obsidian) afin qu'Henri ait la scène active sous les yeux avant même le premier jet d'initiative ou la première prise de parole.

### 4.4. 🛡️ Création Proactive Systématique & Protocole Anti-Doublons des Entités
Pour enrichir en continu l'univers de jeu sans jamais perdre une idée ni polluer le coffre :
- **Règle de Création Proactive Systématique de 100% des Entités Significatives** :
  Ne JAMAIS attendre une consigne explicite du MJ pour consigner ce qui est nommé ou mis en scène. Dès qu'un élément significatif apparaît dans la narration ou les dialogues :
  * **Lieux d'importance** : Dès qu'un **lieu d'importance** est abordé (planque, échoppe, sanctuaire, auberge, quartier, ruine, tour) ➔ **création immédiate de la fiche de lieu dans `Conseil/[NomLieu].md`** + **génération d'une illustration d'ambiance 16:9 au Style Asharde** (enregistrée dans `Conseil/_attachments/` et insérée dans la fiche et en tête du HUD).
  * **Objets ou reliques utiles** : Dès qu'un **objet ou relique potentiellement utile ou important** émerge (clé, passe-partout, artefact maudit, fiole rare, arme singulière, document, lettre, registre, parchemin) ➔ **création immédiate de la fiche d'objet dans `Conseil/[NomObjet].md`**.
  * **Personnages personnifiés (PNJ)** : Dès qu'un **personnage personnifié** avec un nom, une fonction ou une personnalité émerge (marchand, passant nommé, garde singulier, informateur, antagoniste, contact) ➔ **création immédiate de la fiche PNJ dans `Conseil/[NomPNJ].md`** + **portrait 16:9 au Style Asharde** (enregistré dans `Conseil/_attachments/` et inséré dans la fiche et en tête du HUD).
  * **Respect Absolu du Protocole Anti-Doublons** : Avant toute création, exécuter systématiquement la vérification préalable (`grep_search` / `find_by_name`). Si l'entité existe déjà, enrichir in situ et ajouter les alias au YAML sans créer de doublon.
- **Vérification Systématique Préalable** : Avant de créer toute nouvelle entité dans `Conseil/`, vérifier systématiquement via `grep_search` ou `find_by_name` si elle existe déjà sous un **nom populaire**, **officiel**, **générique** ou un **alias** (ex: *Bête d'Ombre* vs *Laerith*, *Gardes du Rempart* vs *Dottari*).
- **Enrichissement In Situ (Zéro Fichier Doublon)** :
  * Si l'entité existe déjà, **INTERDICTION FORMELLE de créer un nouveau fichier**.
  * Ouvrir et enrichir directement la fiche existante in situ avec les nouvelles informations révélées par la session (nouvelles compétences, répliques marquantes, secrets dévoilés, état de santé, objets portés).
  * Ajouter les nouveaux noms ou surnoms entendus dans le champ `aliases:` du frontmatter YAML de la note.
- **Création d'Entité Neuve & Inscription au Registre du HUD** :
  * Uniquement si l'entité est authentiquement nouvelle et n'a aucune fiche existante.
  * Rédiger la fiche canonique selon [`harpy-entity-creator`](file:///C:/Users/Jamet/Documents/VoiceNotes/_agents/skills/harpy-entity-creator/SKILL.md) dans `C:\Users\Jamet\Documents\VoiceNotes\Conseil\[NomEntite].md`.
  * **Consigner immédiatement l'entité créée dans le Registre cumulatif du HUD** (`mj_live_hud.md`) avec son lien Markdown cliquable, sa catégorie et sa description courte pour l'import Harpy en clôture de partie.

### 4.5. Cycle de Veille Périodique (Toutes les 3 minutes)
À chaque expiration du cron :
1. **Lecture de la Transcription** : Le Sous-Agent Vigie lit les répliques récentes dans `live_session.md` (filtrage des 3 à 5 dernières minutes selon les timestamps).
2. **Détection d'Ambiance, Portraits & Menaces Tactiques (Règle d'Unicité Visuelle)** :
   - Lieu inédit ➔ Génération proactive de l'illustration d'ambiance unique 16:9.
   - Transition de lieu / scène ➔ Purge immédiate des visuels de l'ancienne scène du HUD (règle stricte d'unicité visuelle).
   - Tension martiale / patrouille / embuscade ➔ Génération immédiate au maximum d'une battlemap 90° sans grille 16:9 associée à ce lieu précis.
   - PNJ ou monstre actif dans cette scène ➔ Génération ou intégration du portrait/visuel de l'entité en tête du HUD.
3. **Analyse & Création Proactive des Entités avec Contrôle Anti-Doublons** :
   - Création proactive immédiate de 100% des entités significatives : lieux (+ ambiance 16:9), objets/reliques utiles, PNJ personnifiés (+ portrait 16:9).
   - Vérification de l'existence préalable de chaque entité.
   - Enrichissement in situ + alias YAML ou création d'une nouvelle fiche Harpy dans `Conseil/` inscrite au Registre cumulatif du HUD.
4. **Délégation Chirurgicale au Sous-Sous-Agent Recherche ($P=2$)** :
   Pour toute question narrative, mécanique ou statblock manquant, la Vigie déploie un agent de recherche dédié :
   ```python
   invoke_subagent(
       Subagents=[{
           "TypeName": "research",
           "Role": "Obsidian Lore & Rules Scout",
           "Prompt": "Recherche dans Conseil/ et notes/Le Conseil des Voleurs : 1) Les statistiques complètes et attaques de [Entité]. 2) La règle PF1e sur [Mécanique]. Restitue uniquement les faits bruts, statblocks et citations exactes."
       }]
   )
   ```
5. **Remontée à l'Agent Principal via `send_message`** :
   La Vigie transmet à l'Agent Principal ($P=0$) une synthèse prête à intégrer dans le HUD :
   ```python
   send_message(
       Recipient="parent",
       Message="Delta HUD Session :\n- Médias : [Battlemap du lieu actuel, ambiance du lieu actuel et portraits PNJ de la scène active (anciens purgés selon unicité visuelle)]\n- Entités présentes : [Liens cliquables vers acteurs et lieux de la scène active]\n- PNJ de la scène : [Statblocks complets de combat et profils d'action (hors PJ)]\n- Idées de jeu : [Leviers tactiques, dilemmes et improvisation]\n- Registre Harpy : [Nouvelles entités créées à ajouter en bas de registre]"
   )
   ```

### 4.6. Rôle de l'Agent Principal à Réception du Push
Dès réception du message de la Vigie :
- L'Agent Principal rafraîchit immédiatement l'artéfact `mj_live_hud.md` via `write_to_file`.
- Il n'interrompt pas le chat avec Henri sauf alerte narrative critique.

---

## ⌨️ 5. Commandes Express & Raccourcis MJ

Lorsque Henri tape un message court ou un raccourci pendant la partie, répondre instantanément :

| Raccourci | Syntaxe | Action de l'Agent | Exemple de Réponse |
|---|---|---|---|
| **Stats Express** | `!stat <Nom>` | Affiche en 3 lignes : PV, CA, Init, Sauvegardes et Attaque principale. | **Chevalier du Chevalet** : CA 19 (contact 11), PV 22. Épée bâtarde +5 (1d10+3 / 19-20). Vigueur +5, Réfl +1, Vol +2. |
| **Règle Flash** | `!regle <Sujet>` | Résumé de règle PF1e en 2 lignes : modificateurs, DD et jets requis. | **Prise au dépourvu** : Perte du bonus Dex à la CA, interdit les AdO (sauf Réflexes de combat). Attaque sournoise active. |
| **Secrets & Lore** | `!secret <PNJ/Lieu>` | Rappel des allégeances secrètes, faiblesses et déclencheurs de réaction. | **Barnabé Limon Sec** : Passeur payé par les Bâtards d'Érèbe. Craint la torture, parlera pour 15 PO ou si menacé de noyade. |
| **Improvisation PNJ** | `!pnj <Concept>` | Génère nom chélois authentique, voix, manie et statblock rapide. | **Corrado Vane** : Greffier corrompu, voix sifflante, frotte une pièce de cuivre. CA 12, PV 8, Diplomatie +6, Psychologie +4. |
| **Battlemap Express** | `!map <Lieu>` | Déclenche immédiatement une battlemap 90° sans grille 16:9 dans `Conseil/_attachments/`. | Battlemap générée : `battlemap_arche_deluges.png`. Insérée en tête du HUD. |
| **Visuel Ambiance** | `!visuel <Scène>` | Génère une illustration d'ambiance 16:9 de la scène en cours. | Illustration générée : `ambiance_quai_deluges.png`. Insérée en tête du HUD. |
| **Bilan Étape** | `!status` ou `.` | Synthèse des 3 dernières minutes et refresh du HUD. | 3 répliques PJ. Elias explore le quai, Nox en filature. 1 garde Dottari repéré. HUD actualisé. |

---

## 📋 6. Gabarit Canonique du HUD MJ Ultra-Dense (`mj_live_hud.md`)

L'artéfact affiché sur le volet latéral doit suivre rigoureusement cette architecture **ultra-dense sans aucun titre Markdown (`#` ou `##`) et sans en-tête verbeux**.

### Structure Obligatoire de Haut en Bas :
1. **🖼️ Visuels de la Scène Actuelle** :
   - 1 seule image du lieu actuel (format 16:9 Style Asharde).
   - Au maximum 1 battlemap associée à ce lieu en cas de combat ou tension (format 16:9 Cartographer).
   - Les visuels / portraits des PNJ actifs de la scène (format 16:9 Style Asharde).
   - **Strictement zéro image de scènes antérieures** ou de lieux hors scène (liens cliquables uniquement).
2. **🏷️ Entités Présentes dans la Scène** :
   - Ligne compacte de liens Markdown classiques cliquables `[Nom](file:///...)` vers les entités et lieux de la scène active (zéro wikilink `[[...]]`).
3. **⚔️ PNJ de la Scène — Stats de Combat & Profils d'Action** :
   - Tableau complet des PNJ : PV, CA, Contact, Pris au Dépourvu, Init, BMO, DMD, Attaque Principale, Sauvegardes (Vig / Réf / Vol).
   - Profils d'action, psychologie, réactions probables, compétences importantes.
   - **EXCLUSION DU GROUPE DES PJ** : Le groupe des héros n'est pas inclus dans le HUD (le MJ interroge directement les joueurs à sa table).
4. **💡 Idées de Jeu, Leviers Tactiques & Improvisation** :
   - Pistes concrètes d'actions, de tests, de dilemmes ou de réactions pour stimuler et assister le MJ.
   - Leviers tactiques exploitables dans l'environnement immédiat.
5. **📋 Registre des Entités Créées en Session (Pour Import Harpy)** :
   - Placé **STRICTEMENT TOUT EN BAS** de l'artefact.
   - Tableau cumulatif (*append-only*) de toutes les entités créées au fil de la session (Lieux, Objets, PNJ, Monstres, Documents) avec liens cliquables, catégorie et rôle.
- **Suppression Formelle des Citations Directes & Récapitulatifs Redondants** : Zéro citation en direct de répliques, zéro récapitulatif narratif redondant de ce qui vient d'être dit (le MJ et les joueurs viennent de le vivre).
- **Règle de Purge de Transition & Persistance Append-Only** : Les visuels de scène sont renouvelés et purgés à chaque changement de décor ou déplacement du groupe (seuls les visuels de la scène active restent affichés en tête), mais le **registre des entités créées en session reste strictement cumulatif (*append-only*) tout en bas de l'artefact**.
- **Liens Markdown Classiques Cliquables Exclusifs (Zéro Wikilink)** : **TOUS les liens dans l'artéfact doivent être expressément des liens Markdown classiques cliquables au format `[Nom](file:///...)` et JAMAIS de wikilinks Obsidian `[[...]]`** qui ne sont pas cliquables dans l'interface Antigravity.

```markdown
![Battlemap zénithale 90° sans grille — Rempart Nord & Plage aux Galets](file:///C:/Users/Jamet/Documents/VoiceNotes/Conseil/_attachments/battlemap_rempart_nord.png)
*Battlemap zénithale 90° sans grille — Rempart Nord & Plage aux Galets*

![Ambiance 16:9 — Arche des Déluges](file:///C:/Users/Jamet/Documents/VoiceNotes/Conseil/_attachments/ambiance_arche_des_deluges.png)
*Ambiance 16:9 — Arche des Déluges sous la pluie battante*

![Portrait PNJ Actif — Barnabé Limon Sec](file:///C:/Users/Jamet/Documents/VoiceNotes/Conseil/_attachments/portrait_barnabe_limon_sec.png)
*Portrait PNJ Actif — Barnabé Limon Sec (passeur trempé et méfiant)*

---

🏷️ **ENTITÉS PRÉSENTES DANS LA SCÈNE** : [Arche des Déluges](file:///C:/Users/Jamet/Documents/VoiceNotes/Conseil/Arche%20des%20Déluges.md) • [Barnabé Limon Sec](file:///C:/Users/Jamet/Documents/VoiceNotes/Conseil/Barnabé%20Limon%20Sec.md) • [Sentinelles Dottari](file:///C:/Users/Jamet/Documents/VoiceNotes/Conseil/Dottari%20de%20Westcrown.md) • [Bêtes d'Ombre (Laerith)](file:///C:/Users/Jamet/Documents/VoiceNotes/Conseil/Laerith.md)

---

⚔️ **PNJ DE LA SCÈNE — STATS DE COMBAT & PROFILS D'ACTION** *(Groupe PJ exclu)*  
| PNJ / Créature | PV | CA | Contact | Dépourvu | Init | BMO | DMD | Attaque Principale | Sauvegardes (Vig/Réf/Vol) |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|---|:---:|
| **Barnabé Limon Sec** (Roublard 2) | 13 | 14 | 12 | 12 | +2 | +1 | 13 | Dague de maître +4 (1d4 / 19-20) | +1 / +5 / +0 |
| **Sentinelle Dottari** (Guerrier 2) | 18 | 16 | 11 | 15 | +1 | +4 | 15 | Guisarme +4 (2d4+3 / ×3, allonge) ou Arbalète +3 (1d8) | +4 / +1 / +1 |
| **Bête d'Ombre (Laerith)** (FP 3) | 19 | 15 | 15 | 13 | +2 | +4 | 16 | Contact spectral +4 (1d6 froid + 1d6 affaibl. For) | +3 / +3 / +4 |

- **Barnabé Limon Sec** :
  * *Psychologie & Réactions* : Lâche, opportuniste, terrifié par l'obscurité. Parle vite, accepte 15 PO ou trahit à la première menace de noyade.
  * *Profil Tactique* : Cherche le couvert (+4 CA), tente une Attaque Sournoise (+1d6) si un allié prend en tenaille, sinon jette sa bourse comme diversion et s'enfuit dans l'eau.
  * *Compétences Clés* : Discrétion +7, Natation +6, Bluff +5, Connaissances (local) +6.
- **Sentinelles Dottari** :
  * *Psychologie & Réactions* : Disciplinées mais réticentes à entrer sous l'Arche sans torche. Craignent les sanctions de leur capitaine.
  * *Profil Tactique* : Verrouillent l'issue à la guisarme (allonge 3 m, croc-en-jambe BMO +6), tirent à vue à l'arbalète si les PJ restent à distance.
  * *Compétences Clés* : Intimidation +5, Perception +2 (vision normale, pénalité en pénombre).
- **Bêtes d'Ombre (Laerith)** :
  * *Psychologie & Réactions* : Entités affamées, agressivité instinctive envers toute source de chaleur vivante.
  * *Profil Tactique* : Traversent la maçonnerie (Incorporel : 50% raté armes magiques, immunisé armes non-magiques). Ciblent le personnage au score de Force le plus bas.
  * *Compétences Clés* : Discrétion +10 (dans la pénombre), Vulnérabilité : *Lumière vive* (Volonté DD 15 ou fuite à 9 m).

---

💡 **IDÉES DE JEU, LEVIERS TACTIQUES & IMPROVISATION**  
- 🪵 **Levier Tactique — Grille des Vannes d'Évacuation** : Manivelle rouillée sur le pilier est (Force DD 14). Ouvrir la vanne déverse un flot de boue créant un terrain difficile (9 m) et éteint les torches des Dottari.
- 🕳️ **Exutoire des Eaux Usées** : Anfractuosité dans la maçonnerie du rempart crénelé (Escalade DD 12) permettant une extraction discrète vers la ruelle des Teinturiers.
- 🌧️ **Météo Sensorielle** : Averse torrentielle glaciale, pavé rendu glissant (Acrobaties DD 10 en course), odeur étouffante de suif brûlé, de limon croupi et de bitume.
- 🗝️ **Dilemme & Pression Temporelle** : Les cloches de l'Horloge du Rempart sonnent le couvre-feu dans 3 rounds ; une patrouille de cavaliers des Dottari arrive par la chaussée haute si l'alerte retentit.
- 🏛️ **Secret Révélable par Barnabé** : Si interrogé avec succès (Intimidation DD 12 ou Diplomatie DD 14), révèle le mot de passe de la planque des Bâtards d'Érèbe : *« Les yeux fermés voient l'Ombre »*.

---

📋 **REGISTRE DES ENTITÉS CRÉÉES EN SESSION (POUR IMPORT HARPY)**  
*(Tableau cumulatif append-only — placé strictement tout en bas)*  
| Type | Entité & Fiche | Rôle / Description Courte | Import Harpy |
|---|---|---|:---:|
| 🏛️ **Lieu** | [Arche des Déluges](file:///C:/Users/Jamet/Documents/VoiceNotes/Conseil/Arche%20des%20Déluges.md) | Arche monumentale sous le rempart nord, zone de submersion | À importer |
| 👤 **PNJ** | [Barnabé Limon Sec](file:///C:/Users/Jamet/Documents/VoiceNotes/Conseil/Barnabé%20Limon%20Sec.md) | Passeur clandestin de Westcrown, informateur réticent | À importer |
| 🗝️ **Objet** | [Passe-Partout des Caniveaux](file:///C:/Users/Jamet/Documents/VoiceNotes/Conseil/Passe-Partout%20des%20Caniveaux.md) | Clé triangulaire ouvrant les grilles d'évacuation | À importer |
| 📜 **Document** | [Registre de Péage Clandestin](file:///C:/Users/Jamet/Documents/VoiceNotes/Conseil/Registre%20de%20Péage%20Clandestin.md) | Liste codée des cargaisons passées sous l'Arche | À importer |
```

---

## 🛑 7. Clôture de Session (`/relay` ou arrêt)

À la fin de la partie :
1. Arrêter le cron périodique `schedule` via `manage_task(Action='kill', TaskId=...)`.
2. Arrêter le démon de transcription `live_transcriber.py`.
3. Injecter ou importer dans Harpy les entités créées recensées dans le Registre du HUD (`Conseil/`).
4. Produire la synthèse des événements marquants, XP distribués et butins acquis.
5. Raccorder les nouvelles fiches et médias générés dans la note maîtresse de campagne `[[notes/Le Conseil des Voleurs]]`.
