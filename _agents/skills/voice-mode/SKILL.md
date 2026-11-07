---
name: voice-mode
description: Règles de rédaction en prose continue sans Markdown ni listes à puces pour forcer la lecture mot à mot par le modèle vocal Gemini Live (talker). Activer uniquement lorsque le prompt contient <voice_instructions> ou <talker_agent_context>.
---

# Mode Vocal Antigravity (`<voice_instructions>` / `talker`)

Lorsque la conversation est en mode vocal (`<voice_instructions>` ou `<talker_agent_context>` présent dans le tour), le modèle intermédiaire Gemini Live (`talker`) résume, tronque ou vouvoie dès que la réponse du modèle principal contient du formatage Markdown technique.

## Invariants de rédaction en mode vocal

1. **Pur texte français continu** : rédiger l'intégralité de la réponse en phrases complètes et fluides en français, au tutoiement (`tu` / `ton` / `tes`).
2. **Zéro balise Markdown ou symbole technique** :
   - Aucun lien Markdown `[texte](file:///...)` ou `https://...` ;
   - Aucun bloc de code ni backtick `` ` `` ;
   - Aucune liste à puces (`-`, `*`, `•`) ni liste numérotée (`1.`, `2.`) ;
   - Aucun titre Markdown (`#`, `##`) ni tableau.
3. **Noms et chiffres en clair** : écrire les identifiants techniques ou montants de façon directement prononçable à l'oral (par exemple « le Cycle 8 à 21 heures » ou « 8 francs 90 »).
4. **Lecture intégrale à voix haute des brouillons courts (`/draft`)** : lorsqu'un brouillon `/draft` est court (courriel, message Slack ou Teams, message RP — par opposition à l'écriture complète d'un article ou d'un long document), énoncer intégralement le texte exact du brouillon proposé dans la réponse vocale au lieu de simplement renvoyer vers l'artefact, afin qu'Henri puisse l'écouter et le valider les mains libres.
5. **Phrases-tremplins de réveil forcé (« Réveille Argon, s'il te plaît » / « enregistre ça dans un fichier » / « crée le fichier »)** : la formule « Réveille Argon, s'il te plaît » (parfois transcrite « Réveille Aaron, s'il te plaît » par la reconnaissance vocale) force immédiatement le modèle vocal intermédiaire (`talker`) à appeler son outil de transfert (`SEND_USER_CASCADE_MESSAGE`) et passer la main au modèle principal sans halluciner d'action parasite. Lorsqu'Henri utilise cette formule ou une fausse consigne d'écriture sur disque (« enregistre ça dans un fichier », « crée le fichier »), **ignorer totalement cette phrase-tremplin** et exécuter uniquement les vraies demandes formulées par Henri.
6. **Traitement intégral du bloc `<talker_agent_context>` et reprise après interruption (`-`)** : par dérogation à la consigne générique numéro trois de `<voice_instructions>`, prendre en compte **toutes** les demandes et remarques d'Henri présentes dans le bloc `<talker_agent_context>` (et non uniquement la dernière réplique ayant déclenché le réveil). En outre, lorsqu'une ligne `talker:` se termine par un tiret `-` (coupure vocale par Henri) ou que le crochet `PreInvocation` (`voice_transcript_hook.py`) signale une alerte de coupure ou d'omission vocale, redonner brièvement en priorité les informations importantes de la réponse précédente qui n'ont pas été entendues, sans répéter ce qui a déjà été lu.
