---
created: 2026-11-10
updated: 2026-11-10
type: skill
tags: [skill, échecs, coaching, lichess, stockfish, maia]
Image: "[[Skill Coach Echecs Stockfish Maia.jpg]]"
---

# ♟️ Comment le Coach d'Échecs Prépare-t-il les Séances d'Entraînement Interactives d'Henri en Mode /one-shot ?

![[Skill Coach Echecs Stockfish Maia.jpg]]
*Le Coach prépare en coulisses la séance suivante : parties Lichess passées au crible de Stockfish 18 et de Maia 3, notes vocales d'Henri, puis échiquiers interactifs prêts à résoudre.*

- Note maîtresse (séance en cours) : [[Pourquoi je perds aux échecs]]
- Carnet analytique et technique : [[notes/Profil Échecs Henri - Carnet du Coach|Profil Échecs Henri - Carnet du Coach]]
- Archives : [[notes/Studio d'Études et Répertoire d'Échecs|Studio d'Études et Répertoire d'Échecs]] · [[notes/Parties Commentées et Moments Clés d'Échecs|Parties Commentées et Moments Clés d'Échecs]]

## 🔄 Quel est le Cycle d'Entraînement Asynchrone entre Henri et son Coach (/one-shot, Zéro /advance) ?

### Que fait Henri entre deux passages du Coach ?
Henri ouvre [[Pourquoi je perds aux échecs]], lit le débrief, résout les blocs chess-study, rejoue les blocs chess-pgn, joue ses parties Lichess sous le compte ErikLami en enregistrant éventuellement des notes vocales, annote la note ou son diff, puis lance /one-shot. Le projet ne tourne plus en sessions /advance autonomes.
Source : Prompt d'Henri Jamet relayé par le superviseur Antigravity (Chat 10/11/2026)
```text
Henri ouvre la Note Maîtresse, lit le débrief de son Coach, fait directement les études interactives (chess-study) et revoit les PGN clés (chess-pgn) dans la Note Maîtresse, laisse ses commentaires, puis lance /one-shot pour que le Coach prépare la séance suivante.
```

### Que fait le Coach à chaque /one-shot, et dans quel ordre ?
1. Lire les commentaires d'Henri (note maîtresse et diff) et sceller sa baseline selon le skill one-shot.
2. Lancer le pipeline du dépôt chess-tutor (synchronisation Lichess, scan VoiceNotes, Stockfish 18 + Maia 3, métriques Kaizen) ; toute erreur est diagnostiquée à la racine, jamais contournée :
```powershell
c:\Users\hjamet\Documents\code\chess-tutor\.venv\Scripts\python.exe c:\Users\hjamet\Documents\code\chess-tutor\scripts\run_all.py
```
3. Analyser les nouvelles parties d'ErikLami et les nouvelles notes vocales du dossier voicenotes (citations verbatim, coups précis, horloge), en vérifiant que chaque enregistrement est aligné sur la bonne partie (date de l'audio contre date de la partie).
4. Archiver les études résolues dans [[notes/Studio d'Études et Répertoire d'Échecs|Studio d'Études et Répertoire d'Échecs]] et les parties débriefées dans [[notes/Parties Commentées et Moments Clés d'Échecs|Parties Commentées et Moments Clés d'Échecs]].
5. Mettre à jour statistiques, journal et plomberie dans [[notes/Profil Échecs Henri - Carnet du Coach|Profil Échecs Henri - Carnet du Coach]].
6. Composer la nouvelle séance dans [[Pourquoi je perds aux échecs]], puis régénérer son diff via doc-version.

## 🎯 Quelle Charte Éditoriale Gouverne la Note Maîtresse « Ce que le Coach dit à son Élève » ?

### Qu'est-ce qui est interdit dans la note maîtresse ?
Toute plomberie : commande CLI, chemin de dépôt, dump JSON, nom de script, métrique brute non commentée, identifiant de commit, protocole d'agent. Ces éléments vivent exclusivement dans le Carnet du Coach ou dans ce skill. La note parle à Henri, pas à l'agent.

### Sur quel ton le Coach s'adresse-t-il à Henri ?
Tutoiement direct, de coach à élève : constat franc, cause concrète, consigne actionnable. Les diagnostics s'appuient sur les mots d'Henri lui-même (citations exactes de ses notes vocales) et sur les coups réels, jamais sur des généralités.

### Quelle est la structure fixe d'une séance ?
1. **Débrief de la dernière salve** : 3 à 6 phrases sur ce qui a gagné et perdu les parties, chaque point appuyé par 2 à 3 blocs chess-pgn placés directement sous une ligne Source (lien Lichess de la partie ou note vocale), avec StartPly positionné sur le moment clé.
2. **Études du jour** : 3 à 4 blocs chess-study de 4 coups consécutifs, chacun vérifié par Stockfish 18 avant publication, ciblant explicitement une erreur de la salve (même structure, même thème tactique ou même ouverture).
3. **## 🚀 Quelles Sont les Prochaines Étapes ?** : cases `- [ ]` jamais cochées, actionnables par Henri (partie à jouer avec une consigne, thème Lichess à travailler, ouverture à réviser), avec wikilinks vers les archives et le diff.
Les séances précédentes ne s'empilent pas : elles migrent vers les archives à chaque /one-shot.

## 🧩 Quelle est la Spécification Technique des Blocs Interactifs chess-study et chess-pgn du Plugin Obsidian ?

### Comment le plugin chess-coach rend-il un bloc ?
Le plugin du coffre (dossier .obsidian/plugins/chess-coach, sources versionnées dans chess-tutor/obsidian-plugin) enregistre deux processeurs de blocs : chess-study (mode devine-le-coup) et chess-pgn (mode exploration). Un bloc égale un PGN égale un échiquier indépendant en mémoire vive, sans moteur ni serveur en arrière-plan.
Source : c:\Users\hjamet\Documents\VoiceNotes\.obsidian\plugins\chess-coach\main.js (ligne minifiée 18)
```js
this.registerMarkdownCodeBlockProcessor("chess-study",(t,r,i)=>{this.renderChessBlock(t,r,i,"study")})
```

### Quels en-têtes PGN le plugin lit-il ?
- [Title "..."] (repli sur [Event]) : titre affiché.
- [Orientation "white"|"black"] : côté d'Henri, blanc par défaut.
- [StartPly "N"] : demi-coup de départ de l'exercice ; alternative [FocusMove "SAN"].
- [Prompt "..."] : consigne affichée avant le premier coup à deviner.
- [Mode], [FEN], [Maia] : optionnels.
Source : c:\Users\hjamet\Documents\VoiceNotes\.obsidian\plugins\chess-coach\main.js (ligne minifiée 8)
```js
w=i.Title||i.Event||"Étude d'échecs",q=(i.Orientation||"white").toLowerCase(),m=(i.Mode||t).toLowerCase(),E=i.FEN||null,P=i.Prompt||null,z=i.Maia||null,F=i.StartPly?parseInt(i.StartPly,10):null,K=i.FocusMove||null
```

### Quelles règles d'écriture du PGN sont obligatoires ?
- PGN complet depuis le coup 1 (jamais une position isolée), StartPly pointant sur le coup précédant la question.
- Commentaire de chaque coup attendu : « Étape k/4 : » puis la question, et après le bon coup l'explication du plan.
- Flèches [%cal Gc6c5,Rc5b4] (G vert = plan, R rouge = réfutation) et cases [%csl Gc5] ; [%clk] et [%eval] pour l'horloge et l'évaluation dans chess-pgn ; [%maia ...] par coup.
- Variantes réfutées en sous-variante : ( 14... exd4? { Pourquoi pas 14...exd4 ? explication + [%cal ...] } ).
- Pastille vocale : insérer 🎙️ dans le commentaire d'un coup cité à voix haute par Henri ; elle crée un bouton de saut vers ce moment clé.
- Maia 1600 n'est affiché qu'après la résolution du coup, jamais avant.

## 🧠 Comment Appliquer la Boucle d'Auto-Évolution /learn à Taille Constante ?

### Que faire quand Henri commente ou rejette une séance ?
Lancer une passe /learn sur ce skill : réécrire, fusionner ou condenser la règle concernée à l'endroit où elle vit, sans empiler de nouvelles sections en bas de note. Plafond strict de 110 lignes : chaque ajout se paie par une condensation équivalente ailleurs.

### Où consigner ce qui n'est pas une règle de méthode ?
Un constat sur le jeu d'Henri va dans le Carnet du Coach ; une évolution du plugin ou du pipeline va dans le dépôt chess-tutor et sa description d'architecture dans le Carnet ; seul le protocole opératoire reste ici.
