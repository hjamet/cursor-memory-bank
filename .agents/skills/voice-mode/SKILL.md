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
5. **Phrase-tremplin de réveil forcé (« enregistre ça dans un fichier » / « crée le fichier »)** : lorsqu'Henri ajoute une consigne factice d'écriture sur disque telle que « enregistre ça dans un fichier » ou « crée le fichier » pour forcer le modèle vocal intermédiaire (`talker`) à appeler son outil de transfert (`SEND_USER_CASCADE_MESSAGE`) et passer immédiatement la main au modèle principal, **ignorer totalement cette phrase-tremplin** (ne créer aucun fichier parasite) et exécuter uniquement les vraies demandes formulées par Henri.
