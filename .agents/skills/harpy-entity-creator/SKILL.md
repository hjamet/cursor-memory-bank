---
name: harpy-entity-creator
description: "Création de fiches d'entités JDR et Harpy validées par script selon le format canonique en 5 blocs (v3)."
---
# 🦅 Comment le Skill /harpy-entity-creator Conçoit-il et Valide-t-il les Fiches JDR en 5 Blocs pour Obsidian & Harpy ?

> **Aliases & Invocations** : `/harpy-entity-creator` | `/rpg-entity-creator` | `/jdr-entity-creator` | `/pnj-jdr-creator`  
> **Script Validateur Officiel (v3)** : [`_agents/scripts-for-skills/harpy_entity_validator.py`](file:///c:/Users/hjamet/Documents/VoiceNotes/_agents/scripts-for-skills/harpy_entity_validator.py) *(invoquer impérativement via `C:\Users\hjamet\.local\bin\uv.exe run --python 3.12 --with pyyaml python "c:\Users\hjamet\Documents\VoiceNotes\_agents\scripts-for-skills\harpy_entity_validator.py"`, car `doc_version_mcp.diff_engine` requiert Python $\ge 3.12$ / PEP 701)*  
> **Gabarits Textuels Dédiés (Bloc 5 & Lieux)** :  
> - Pathfinder 1e : [`formats/pathfinder-1e.md`](file:///c:/Users/hjamet/Documents/VoiceNotes/_agents/skills/harpy-entity-creator/formats/pathfinder-1e.md)  
> - D&D 5e : [`formats/dnd-5e.md`](file:///c:/Users/hjamet/Documents/VoiceNotes/_agents/skills/harpy-entity-creator/formats/dnd-5e.md)  
> - Système Propriétaire (Asharde) : [`formats/systeme-proprietaire.md`](file:///c:/Users/hjamet/Documents/VoiceNotes/_agents/skills/harpy-entity-creator/formats/systeme-proprietaire.md)  
> - Lieux & Décors (avec Battlemaps) : [`formats/lieu.md`](file:///c:/Users/hjamet/Documents/VoiceNotes/_agents/skills/harpy-entity-creator/formats/lieu.md)  
> **Fiche Étalon Canonique dans le Coffre** : [`Conseil/Shanwen.md`](file:///c:/Users/hjamet/Documents/VoiceNotes/Conseil/Shanwen.md)

Ce skill est le **moteur unifié de rédaction, mise en page, audit et validation** de toute fiche d'entité de jeu de rôle (PNJ, monstre, lieu, décor) pour le coffre Obsidian d'Henri Jamet et l'application **Harpy**. Il répond aux trois besoins majeurs d'Henri en partie :
1. **Survoler instantanément l'apparence physique pure** d'une entité dans la liste (Bloc 2, $\le 100$ caractères) sans risquer de divulguer son identité, sa fonction ou son allégeance.
2. **Disposer immédiatement d'une ouverture double en questions H2** :
   - `## 🎭 Comment l'improviser ?` : aide à l'improvisation immédiate dévoilable aux joueurs avec mots en **gras**.
   - `## 🗝️ Qui est-il vraiment ?` : tout ce que le MJ doit savoir (histoire, origine, motivations, nature profonde, secrets de fond, $\ge 350$ caractères).
   Puis accéder aux secrets détaillés (`## 🔒 Quels sont les secrets MJ...`), avant de partager la **description joueurs riche et sensorielle** (Bloc 4, 1-2 paragraphes, $\ge 450$ caractères, synesthésies, description générale décontextualisée réutilisable à toute rencontre).
3. **Accéder instantanément aux statistiques de combat dans la fiche Harpy** au format texte pur lisible, avec descriptions opérationnelles immédiates des attaques, capacités et sorts sous forme de sous-lignes « ↳ » ($\le 70$ caractères/ligne).

```mermaid
flowchart TD
    A["🎲 Demande de PNJ, Monstre ou Lieu JDR"] --> B["🎲 Tirage Aléatoire d'Angle Narratif (--tirage)"]
    B --> C["📝 Rédaction du Fichier d'Entrée Structuré (YAML)"]
    C --> D["⚙️ Exécution de harpy_entity_validator.py v3"]
    D --> E{"🔍 Validation Conforme ?<br/>Bloc 2 Apparence Pure <= 100 car.<br/>Ouverture : Improvisation + Vérité MJ >= 350 car.<br/>Bloc 4 Joueurs 1-2 Paragraphes >= 450 car.<br/>Zéro Mention de Source<br/>Bloc 5 Texte Pur & ↳ <= 70 car."}
    E -->|❌ Échec (Code 1)| F["✏️ Correction Ciblée Fail-Fast & Réitération"]
    F --> D
    E -->|✅ Succès (Code 0)| G["💾 Assemblage Automatique Canonique"]
    G --> H["📋 Fiche Finale Validée dans Obsidian / Harpy"]
```

---

## 1. 🎯 Quels Sont les Principes Fondateurs & Invariants Absolus ?

### 📁 1.1. Règle Stricte du Fichier Unique — Zéro Doublon
- **Emplacement Canonique Unique** : Une fiche d'entité ne réside qu'en **UN SEUL et unique endroit** dans le coffre Obsidian.
- **Dossier de Campagne Prioritaire** : Si la campagne dispose d'un sous-dossier dédié (ex: `Conseil/` pour *Le Conseil des Voleurs*, `Asharde/` pour *Asharde*), la fiche est créée **EXCLUSIVEMENT** dans ce dossier thématique (ex: `Conseil/Shanwen.md`).
- **Interdiction Formelle de Duplication** : Interdiction absolue de créer une copie satellite ou temporaire dans `notes/` ou ailleurs.
- **Liaisons par Wikilinks Directs** : Les notes de session pointent vers le fichier unique via `[[Conseil/NomEntité|Alias]]`.

### 📜 1.2. Ancrage Obligatoire dans la Fiche de Style de Campagne
Avant de poser la moindre ligne, consulter la Fiche de Style de la campagne active (ex: `[[Conseil/Fiche de Style Le Conseil des Voleurs]]` ou `[[Asharde/Fiche de Style Asharde]]`) pour adopter le système de règles approprié, le barème de FP et le lexique local.

### 🎨 1.3. Illustrations & Cartographie Dédiées (Zéro Placeholder)
- **PNJ, Créatures, Monstres** : Visuel 16:9 cinématographique généré obligatoirement via la Master Formula en 7 points du skill [`/asharde-illustration`](file:///c:/Users/hjamet/Documents/VoiceNotes/_agents/skills/asharde-illustration/SKILL.md) (`c:\Users\hjamet\Documents\VoiceNotes\_agents\skills\asharde-illustration\SKILL.md`).
- **Lieux, Décors & Bâtiments** : Battlemaps 16:9 en vue strictement zénithale à 90° sans grille générées via [`/asharde-battlemap`](file:///c:/Users/hjamet/Documents/VoiceNotes/_agents/skills/asharde-battlemap/SKILL.md) (`c:\Users\hjamet\Documents\VoiceNotes\_agents\skills\asharde-battlemap\SKILL.md`).
  * **Règle de Simplicité** : **Garder autant que possible une seule carte par simplicité**. Ne générer des cartes secondaires que si des étages nettement séparés et indispensables le justifient.
- L'image réside physiquement dans `_attachments/`. Zéro placeholder vide toléré.

### 🚫 1.4. Interdiction Stricte des Mentions de Sources dans la Note Finale (v3)
> [!CAUTION]
> **ZÉRO MENTION DE SOURCE DANS LA NOTE PRODUITE :**
> - Ne JAMAIS insérer de pagination (`p. 32`, `page 14`), de nom de recueil (`module`), de `transcript` ou de `voicenote`.
> - Ne JAMAIS insérer de balise métatextuelle telle que `(canon)` ou `(proposition MJ)`.
> - **Justification d'Henri** : Ces mentions alourdissent la note et ne facilitent pas la lecture en cours de jeu.
> - **Traçabilité Déportée** : La rigueur des sources et la distinction entre données officielles et propositions du MJ restent obligatoires pour l'agent, mais figurent **exclusivement dans son rapport de session**, jamais dans la note Markdown du coffre.

### 🌍 1.5. Pourquoi la Description Joueurs (Bloc 4) Doit-elle Être Strictement Générale et Décontextualisée ?
> [!IMPORTANT]
> **Consigne Canonique d'Henri** : *« Attention, même si elles sont excellentes, les descriptions pour les joueurs doivent toujours être générales, elles ne doivent pas être liées à un contexte spécifique !!! Mettre à jour le skill ! »*

- **Description Intrinsèque et Permanente** : Le Bloc 4 décrit l'entité **en elle-même** (apparence physique, allure, vêtements habituels, odeurs corporelles ou d'équipement, voix, posture coutumière, démarche et impression générale qu'elle dégage).
- **Réutilisabilité Universelle** : Le texte doit pouvoir être lu tel quel aux joueurs quelle que soit la rencontre (dans une ruelle, une taverne, de jour comme de nuit, en plein combat ou lors d'un interrogatoire).
- **Interdiction Formelle d'Ancrage Spécifique** :
  - **Zéro lieu spécifique** (aucun pont, carrefour, buisson, canal ou bâtiment précis).
  - **Zéro moment ou éclairage temporel précis** (aucun « soleil du début d'après-midi », « brume de l'aube », « crépuscule » ou heure de la journée).
  - **Zéro météo extérieure** (aucune chaleur écrasante, pluie battante, neige ou vent particulier).
  - **Zéro action en cours ou événement circonstanciel** (aucun guet embusqué, convoi qui ralentit, matelots qui amarrent ou fuite en cours).
  - **Zéro état circonstanciel éphémère** (aucun état de captif blessé dans un convoi : les états actuels vont dans les sections MJ, pas dans le Bloc 4).
- **Avertissement Automatique du Validateur** : Le script `harpy_entity_validator.py` analyse automatiquement le Bloc 4 et signale les marqueurs contextuels résiduels (moments, météo, actions immédiates) via des avertissements non bloquants (`⚠️ [Bloc 4 - Avertissement Marqueur de Scène]`), guidant la révision sans interrompre la validation technique.
- **Exemple Comparatif** :
  - ❌ **Interdit (Ancré dans une scène spécifique)** : *« Tapi dans les buissons d'épines sous le soleil cuisant du début d'après-midi, le jeune homme guette le sentier menant à l'ouvrage de pierre, le souffle court avant l'assaut. »*
  - ✅ **Autorisé (Général et réutilisable)** : *« Un jeune homme à la silhouette sèche et nerveuse, sanglé dans un pourpoint de cuir fauve criblé de rivets de fer sombre. Une toison de cheveux noirs tondus à ras découvre un visage émacié aux pommettes saillantes, d'où dardent deux yeux vifs couleur de noisette toujours en alerte. Entre ses doigts maigres et calleux, la hampe polie d'une longue pique d'acier noirci oscille avec une agilité fébrile. Une odeur persistante de cuir tanné et de sueur l'accompagne, tandis que sa voix éraillée s'échappe avec une vivacité saccadée au moindre mouvement suspect. »*

### 🎲 1.6. Part d'Aléatoire & Tirage d'Angle Narratif (`--tirage`)
Pour éviter que les descriptions des personnages, monstres ou lieux ne deviennent mécaniques ou stéréotypées, le script `harpy_entity_validator.py` fournit l'option `--tirage` qui tire au hasard un ensemble cohérent de 6 dimensions narratives à respecter :
1. **Sens dominant** (acoustique, effluves, rugosité/température, lumière crue/contrastes, synesthésie).
2. **Point de vue** (contre-plongée, face-à-face, profil oblique, regard périphérique).
3. **Distance** (observation lointaine 10-15 m, portée moyenne 4-6 m, proximité immédiate 2-3 m).
4. **Moment & lumière** (lumière rasante, torches vacillantes, éclat de midi, brume matinale).
5. **Détail inattendu** (usure singulière, immobilité statuaire, accessoire patiné, respiration lente, trace de suie).
6. **Rythme de phrase** (staccato incisif, période ample équilibrée, attaque brute, cadence syncopée).

---

## 2. 🏛️ Quelle Est la Structure Universelle des Sections (v3) ?

Toute fiche produite par `/harpy-entity-creator` respecte rigoureusement l'enchaînement suivant :

| # | Section Canonique | Balisage & Format | Destination & Contenu |
|---|---|---|---|
| **1** | **Image / Battlemap** | `![[nom_image.png]]` | Illustration 16:9 pleine largeur (`/asharde-illustration`), couplée à la battlemap 16:9 zénithale (`/asharde-battlemap`) pour les lieux. |
| **2** | **Description Externe** | ````text ... ```` | **100 caractères maximum stricts** dans un bloc de code copiable. **Apparence physique visible pure exclusivement**. Zéro nom, zéro fonction, zéro faction, zéro action narrative. |
| **3** | **Ouverture : Comment l'improviser ?** | `## 🎭 Comment l'improviser ?` | **Paragraphe 1** : Aide à l'improvisation immédiate, informations dévoilables aux joueurs, mots les plus importants en **gras**, structure et adjectifs distincts du Bloc 4. |
| **4** | **Ouverture : Qui est-il vraiment ?** | `## 🗝️ Qui est-il vraiment ?` | **Paragraphe 2 ($\ge 350$ caractères stricts)** : Tout ce que le MJ doit savoir (histoire résumée, origine, motivations, nature profonde, secrets inavouables). |
| **5** | **Secrets MJ Détaillés** | `## 🔒 Quels sont les secrets MJ, l'inventaire et les coulisses de [Nom] ?` | Rubriques H3 détaillées : inventaire, guide d'interprétation, répliques types, secrets inavouables et liaisons, destin. Zéro mention de source. |
| **6** | **Description Joueurs** | ````markdown ... ```` | **1 ou 2 paragraphes détaillés ($\ge 450$ caractères stricts)** dans un bloc de code copiable. Sentiments évoqués, synesthésies, opulence, couleurs, matières, style, allure. Description générale décontextualisée (zéro lieu, météo, horaire ou scène spécifique). Zéro spoiler. Angle stimulé par `--tirage`. |
| **7** | **Fiche Harpy (Texte Pur)** | ````text ... ```` | Bloc de code copiable pour Harpy. **Texte pur strict, émojis repères, sous-lignes « ↳ » descriptives**, max 70 car./ligne, ordonné pour le combat immédiat. |

---

## 3. 🔍 Quels Sont les Contrôles Bloquants du Validateur (v3) ?

Le script [`harpy_entity_validator.py`](file:///c:/Users/hjamet/Documents/VoiceNotes/_agents/scripts-for-skills/harpy_entity_validator.py) applique les vérifications Fail-Fast suivantes :

1. **Zéro Mention de Source** : Détection et rejet immédiat de tout motif de source (`(proposition MJ)`, `(canon)`, `p. XX`, `module`, `transcript`, `voicenote`).
2. **Description Externe (Bloc 2)** : Plafond de $\le 100$ caractères Unicode. Interdiction absolue du nom, des entités liées et des mots de rôle/faction/comportement.
3. **Ouverture de Note** :
   - Paragraphe 1 (`aide_improvisation`) non vide avec mots importants en **gras** et zéro secret.
   - Paragraphe 2 (`resume_mj`) non vide et $\ge 350$ caractères stricts détaillant l'histoire et les secrets pour le MJ.
4. **Description Joueurs (Bloc 4)** : Exigence de 1 ou 2 paragraphes stricts et d'un seuil minimal de $\ge 450$ caractères. Zéro fuite de secrets.
5. **Fiche Harpy (Bloc 5)** : Absence totale de syntaxe Markdown (`|`, `**`, `#`, backticks, `[[...]]`) et respect de la largeur maximale par ligne ($\le 70$ car.).
6. **Wikilinks du Coffre (`--vault`)** : Audit complet de tous les liens `[[...]]`. En cas de lien manquant, le script propose les 3 correspondances les plus proches sur noms et alias.
7. **Détection d'IA Déterministe (`detect.js` + `fr_ai_patterns.py`)** : Audit déterministe unifié via `style_guard.check_style(language="fr", context_mode="general")`, intégrant 38 motifs déterministes transposés sur les 45 de `avoid-ai-writing-multilingual` (`fr_ai_patterns.py`, les 7 motifs restants étant documentés comme structurels/statistiques), les Hard Blockers P0/P1 et les em-dashes.

---

## 4. ⚙️ Exemple Complet d'Entrée YAML (Shanwen v3)

```yaml
nom: "Shanwen"
systeme: "Pathfinder 1e"
image: "shanwen_profile_qyrdld.png"
description_externe: "Jeune homme au regard sévère, vêtu d'un harnois d'acier poli et portant un symbole en bois sculpté."

ouverture_mj:
  aide_improvisation: |
    Une silhouette d'une **rigidité martiale** juchée sur l'impériale d'un convoi de transport lourdement bardé de fer. Le harnois d'acier renvoie un éclat mat sous la lumière poussiéreuse de la chaussée. Ses ordres résonnent d'un **ton sec et impérieux**, sans le moindre flottement dans la voix, tandis que sa main gantée de fer repose avec assurance sur le manche d'une **lourde masse d'armes**.
  resume_mj: |
    Issu d'une lignée de petite noblesse appauvrie de Couronne d'Ouest dévouée au culte d'Asmodéus, Shanwen a été confié dès l'adolescence au clergé pour redorer le blason familial. Désormais prêtre ordonné et Signifer infernal de rang inférieur au sein de l'Ordre du Chevalet, il exerce la charge de parrain disciplinaire auprès d'une promotion de dix novices qu'il mène d'une main de fer. Son ambition dévorante est d'obtenir une promotion d'officier à la Citadelle de Rivad en réussissant sans anicroche le transfert du captif Arael, espérant ainsi laver l'humiliation subie par ses apprentis lors de la traque des rebelles dans les égouts. Sous une contenance marmoréenne et un zèle doctrinal intraitable, il redoute par-dessus tout l'échec et la perte de son honneur militaire ; il garde jalousement sur lui un pli confidentiel scellé du maire Arvanxi réclamant des renforts contre les Bâtards de l'Érèbe, document qu'il envisage comme la preuve éclatante de son utilité auprès du commandement infernal.

secrets_mj:
  inventaire: |
    - Masse d'armes lourde en acier et grande arbalète fixée sur le toit du [[Conseil/Chariot Blindé|Chariot Blindé]] garnie de dix carreaux.
    - Une fiole de soins légers conservée dans une sacoche de ceinture en cuir bouilli.
    - Lettre cachetée du maire Abérian Arvanxi adressée au capitaine de la garnison de la [[Conseil/Citadelle de Rivad|Citadelle de Rivad]].
    - Trousseau de clés ouvrant les portes du chariot cellulaire et les fers entravant [[Conseil/Arael|Arael]].
    - Harnois de plates complet d'ordonnance et symbole sacré en bois dur taillé aux armes d'Asmodéus.
  guide_interpretation: |
    - Posture d'une autorité implacable, toisant les assaillants comme de vulgaires perturbateurs de l'ordre public.
    - Reste posté sur le toit du véhicule pour faire pleuvoir des tirs d'arbalète lourde. Si un assaillant monte, déchaîne un cône de flammes ardentes.
    - Trop fier pour concevoir la reddition ; combat avec une obstination fanatique jusqu'à la défaite.
  repliques_types: |
    - « L'autorité ne pactise point avec les séditieux de la basse-fosse. »
    - « Gardez vos rangs, apprentis ! Nul fauteur de trouble ne franchira ce passage ! »
  secrets_coulisses: |
    - Mission de transfert cellulaire ordonnée par les autorités pour incarcérer [[Conseil/Arael|Arael]] dans les geôles profondes de la forteresse.
    - Liaisons : [[Conseil/Arael|Arael]], [[Conseil/Janiven|Janiven]], [[Conseil/Les Enfants de Couronne d'Ouest|Les Enfants de Couronne d'Ouest]], [[Conseil/Citadelle de Rivad|Citadelle de Rivad]], [[Conseil/Couronne d'Ouest|Couronne d'Ouest]], [[Conseil/Pont sur l Athua Site de l Embuscade|Pont sur l'Athua]].
  destin_trajectoire: |
    - En cas de déroute, les survivants de l'escorte refluent vers les portes de la cité. Si le convoi parvient à destination, le captif est soumis aux interrogatoires de Rivad.

description_joueurs: |
  Une haute silhouette à la stature droite et d'une rigidité martiale implacable, drapée dans l'austérité d'un harnois complet de plates d'acier poli. Le métal renvoie des éclats mats et réguliers, soulignant une cuirasse sans la moindre fioriture où ne tranche que le grain sombre d'un lourd pendentif de bois dur sculpté aux armes d'Asmodéus. Une odeur tenace d'huile d'armurerie, de suif et de cuir neuf accompagne chacun de ses mouvements mesurés.

  Sous une chevelure sombre coupée ras, son visage glabre aux traits acérés affiche une impassibilité hautaine, balayant les alentours d'un regard d'acier froid et dépourvu d'hésitation. Ses mains gantées de fer reposent d'un geste assuré sur la garde de sa lourde masse d'armes, prêtes à frapper avec une précision méthodique. Sa voix résonne d'un timbre sec et tranchant, portant sans effort l'autorité implacable d'un prêtre de la Loi.

bloc_harpy: |
  👤 IDENTITÉ
  Shanwen / FP 1/2 (200 px)
  Humain prêtre d'Asmodéus 1 / Loyal Mauvais
  
  🛡️ DÉFENSE
  CA 18 (contact 9, pris au dépourvu 18)
  Détail CA : +9 harnois de plates, -1 Dex
  PV 14 (1d8+1)
  Sauvegardes : Vig +4, Réf -1, Vol +4
  Immunités : Aucune
  
  ⚡ TACTIQUE
  Initiative : -1
  Vitesse : 6 m (encombré par harnois)
  Sens : Perception +3, vision normale
  
  ⚔️ ATTAQUES & CAPACITÉS
  Masse d'armes lourde : +1 (1d8+1 / x2)
  Arbalète lourde de toit taille G : -3 (2d6 / 19-20, 36 m)
  ↳ Fixée au toit. Arme à 2 mains (-2 att.). Action complexe recharg.
  Trait de feu : contact distance -1 (1d6 feu, 9 m, 5/j)
  ↳ 1 action simple, rayon ardent d'énergie infernale (domaine Feu).
  Canalisation d'énergie négative : 1d6 négatif (Vol DD 10 demi, 3/j)
  ↳ 1 action simple, onde 9 m. Blesse vivants ou soigne morts-vivants.
  Toucher de la Loi : contact +1 (5/j)
  ↳ 1 action simple, 1 rd. Cible traite tous ses d20 comme résultat 11.
  
  🔮 SORTS (NLS 1, DD base 12 + niveau)
  Niv 1 (2+1/j) :
  - Injonction (DD 13)
    ↳ 1 action simple, 7,5 m, 1 rd, Vol annule. Cible obéit à 1 ordre :
      approche, lâche, tombe, fuis ou arrête-toi.
  - Mains brûlantes (DD 13, domaine Feu)
    ↳ 1 action simple, cône 4,5 m, instantané, Réf demi. 1d4 dégâts feu.
  - Soins légers
    ↳ 1 action simple, contact, instantané. Rend 1d8+1 pv à 1 vivant.
  Niv 0 (3 à volonté) :
  - Lumière : 1 action simple, contact. Brille comme torche (rayon 6 m).
  - Réparation : 10 min, contact. Répare 1d4 pv d'objet brisé < 0,5 kg.
  - Stabilisation : 1 action simple, 7,5 m. Stabilise 1 mourant à 0 pv.
  Domaines : Feu (Flammes infernales), Loi (Tyrannie)
  
  🎯 COMPÉTENCES
  Connaissances (plans) +5, Connaissances (religion) +5
  Perception +3, Premiers secours +6
  Langues : commun, infernal
  
  📊 CARACTÉRISTIQUES
  FOR 12 (+1) / DEX 8 (-1) / CON 14 (+2)
  INT 13 (+1) / SAG 15 (+2) / CHA 10 (+0)
  BBA +0 / BMO +1 / DMD 10
  
  🎖️ DONS
  Port des armures lourdes, Robustesse
  
  🎒 ÉQUIPEMENT DE COMBAT
  Masse d'armes lourde, arbalète de toit (10 carreaux)
  1 potion de soins légers (1d8+1 pv)
  Harnois complet de plates, symbole sacré en bois
  Clés du chariot de transport et des menottes
  Lettre scellée du maire Abérian Arvanxi
```

---

## 5. 📋 Quelle Est la Checklist de Validation Finale (v3) ?

- [ ] L'image a-t-elle été générée selon [`/asharde-illustration`](file:///c:/Users/hjamet/Documents/VoiceNotes/_agents/skills/asharde-illustration/SKILL.md) (et battlemap unique via [`/asharde-battlemap`](file:///c:/Users/hjamet/Documents/VoiceNotes/_agents/skills/asharde-battlemap/SKILL.md) si lieu) ?
- [ ] Le script `harpy_entity_validator.py` v3 a-t-il été exécuté avec succès (code retour 0) ?
- [ ] La note finale est-elle 100% exempte de mentions de sources (zéro `p. XX`, zéro `module`, zéro `canon`, zéro `proposition MJ`) ?
- [ ] La description externe (Bloc 2) fait-elle bien $\le 100$ caractères stricts d'apparence physique pure ?
- [ ] L'ouverture contient-elle les deux sections H2 distinctes : `## 🎭 Comment l'improviser ?` (mots en **gras**) et `## 🗝️ Qui est-il vraiment ?` ($\ge 350$ caractères détaillant l'histoire et les secrets) ?
- [ ] La description joueurs (Bloc 4) compte-t-elle 1 ou 2 paragraphes riches totalisant $\ge 450$ caractères avec synesthésies, et est-elle rigoureusement générale et décontextualisée (zéro scène, horaire, météo, action en cours ou lieu spécifique) ?
- [ ] Le Bloc 5 Harpy est-il en texte pur strict, $\le 70$ caractères par ligne avec sous-lignes « ↳ » ?
- [ ] 100% des wikilinks pointent-ils vers des notes existantes dans le coffre ?
