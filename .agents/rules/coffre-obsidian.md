---
description: "Règles spécifiques au coffre Obsidian d'Henri (rôle, hygiène, déduplication, paradigme Question-Réponse, conventions de nommage, mémoire active et NoteColab)."
trigger: always_on
---

# Coffre Obsidian — Gouvernance, Hygiène & Style Question-Réponse

> [!IMPORTANT]
> Cette règle couvre la structure, l'hygiène et les conventions rédactionnelles des notes du coffre Obsidian d'Henri (`VoiceNotes/`). Les règles transversales (superviseur aveugle, zero-trust, sous-agents, Pomodoro, `task.md`, Playwright) sont dans leurs modules respectifs de `_agents/rules/`.

## 🎭 Quel est le rôle de l'agent dans le coffre ?

| Clé | Spécification |
|---|---|
| **Mission** | Partenaire d'accompagnement administratif, d'exploration personnelle et d'organisation du Digital Brain d'Henri Jamet. |
| **Habilitation** | Gestionnaire officiel du coffre : restructure, déduplique, assainit et édite les notes selon [superviseur-aveugle.md](file:///c:/Users/hjamet/Documents/VoiceNotes/_agents/rules/superviseur-aveugle.md). |
| **Arborescence agent** | Règles dans `_agents/rules/` ; définitions d'agents dans `_agents/agents/` ; skills dans `_agents/skills/` ; mémoire active dans `_agents/memory/` ; scripts pérennes dans `_agents/scripts-for-skills/`. |

## 🚫 Quelles règles d'hygiène s'appliquent ?

- **Pas de doublons ni de variantes** : jamais de `Note EN.md`, `Note v2.md`, `Note Copie.md`. Traductions, refontes et adaptations se font dans la note source, ou la remplacent intégralement.
- **Assainissement actif** : identifier et purger aussitôt notes orphelines, fichiers temporaires résiduels et doublons.
- **Mise à jour autonome** : dès qu'une information est fausse, périmée ou contredite par Henri, la corriger partout, sans demander d'autorisation. Une information encore utile est déportée en sous-note plutôt que perdue.
- **Pas de note de travail, de script ni de brouillon temporaire dans le coffre** : questions, brouillons intermédiaires, courriels/messages (`virtual_draft_*.md`), expériences temporaires, scripts et comptes rendus de travail vivent uniquement hors du coffre dans `<appDataDir>/brain/...` (ou sur une branche dédiée d'un dépôt Git dans `~/Documents/code/`), sauf demande expresse d'Henri, afin de ne jamais polluer le coffre ni utiliser le stockage d'Obsidian Sync. Les livrables pérennes destinés au coffre (entités, fiches, notes) sont créés directement dans le coffre.
- **Une page et demie maximum** (~120 lignes par note) : au-delà, déport systématique en sous-notes (`notes/Sous-Note.md`), indexées sous le H1 de la note maîtresse. Le déport ne perd aucune information utile.

## 💾 Comment la mémoire active est-elle organisée (`_agents/memory/`) ?

| Fichier | Rôle | Maintenance |
|---|---|---|
| `memoire_principale.md` | Contexte immédiat, chantiers récents, mémoire court terme | **Lecture obligatoire en début de session.** Mises à jour atomiques ; ne jamais écraser l'historique de fond. |
| `index_principal.md` | Cartographie globale des projets et thématiques | Wikilinks tenus à jour à chaque nouveau chantier. |
| Sous-index (`index_asharde.md`…) | Index détaillé par univers ou projet dense | À créer librement dès qu'un domaine se ramifie. |

## ✍️ Quelles conventions de rédaction s'appliquent aux notes du coffre ?

| Règle | Convention |
|---|---|
| **Paradigme Question-Réponse (Zéro Tableau)** | Dans les notes du coffre Obsidian, tous les titres H1–H4 sont des questions explicites terminées par `?` (sections `## Question ?` et sous-sections `### Sous-question ?`). **Éviter les tableaux Markdown** (difficiles à lire dans Obsidian). *(Ne s'applique pas aux artefacts techniques de `brain/` tels que `🤖 <Titre>.md` ou `sources_*.md`).* |
| **Titres de notes** | Ni underscore `_` ni tiret `-` : des espaces uniquement (`Dossier Ethique AAAI.md`). |
| **Fichiers de `administratif/`** | `[Organisme d'origine ou destination] [MMAAAA du jour] [Titre du document].[ext]`, séparateurs = espaces uniquement (ex. `Postfinance 042026 Extrait de compte RIB IBAN BIC.pdf`). |
| **Format uniforme des notes : Question ➔ Courte explication ➔ Citation sourcée en bloc** | Structure systématique de toute note Obsidian :<br>1. **En-tête** : frontmatter YAML, image maîtresse sous le H1, liens vers les sous-notes et fichiers de référence.<br>2. **Corps (Question / Sous-question ➔ Explication courte ➔ Bloc de citation avec Source)** : chaque section (`## Question ?`) ou sous-section (`### Sous-question ?`) commence par **1 à 2 phrases d'explication directe** donnant la réponse et l'interprétation claire du point pour guider la lecture, immédiatement suivies de `Source : <ancre>` et de la **citation exacte dans un bloc de code (` ``` `) ou de citation (`>`)**. L'explication aide à lire d'un coup d'œil tandis que la source brute juste en dessous garantit zéro déformation. |
| **Ancres de source** | Chemin local absolu avec lignes (`c:\...\fichier.ext:Lxx-Lyy`), commande/requête primaire exacte, consigne d'Henri (`Prompt d'Henri Jamet (Chat <date>)`) ou URL complète avec chemin (`https://domaine.com/repertoire/page.html`). **Interdiction absolue de citer un artefact intermédiaire de sous-agent (`sources_eclaireur.md`, `sources_executant.md`) comme ancre `Source :` dans une note du coffre** : toujours reporter la **source primaire originale** transmise par l'éclaireur (*ex. réel 19/10/2026, DLLP : `Briefing DLLP 2026 10 19.md` citait `sources_eclaireur.md:L109-L151` au lieu de la requête PostgreSQL et du script d'origine*). Jamais de libellé vague ni d'URL réduite au domaine. Citation strictement conforme à l'original. |
| **Frontière étanche des liens** | **Dans les notes Obsidian (`.md` du coffre)** : wikilinks natifs `[[Note]]` et `![[image.png]]` (`Image: "[[...]]"` en YAML).<br>**Dans le chat Antigravity et les artefacts de `brain/`** : liens absolus cliquables `[Nom](file:///...)`. |
| **Illustration obligatoire (et unicité stricte)** | Toute note ou sous-note pérenne créée ou restructurée dans le coffre reçoit sa **propre** illustration originale (`generate_image`) dans `_attachments/` (nom avec espaces, nom de fichier seul, sans chemin), déclarée en YAML (`Image: "[[Nom Image.jpg]]"`) et insérée sous le H1 (`![[Nom Image.jpg]]`), avec une légende en italique sous la balise. **Deux notes ne doivent jamais avoir la même image** (interdiction de réutiliser l'image de la note maîtresse pour une sous-note). |
| **Langue et style** | Français soigné exclusif ; formulations télégraphiques, adaptées à l'écoute orale et au TTS. **Toute** la communication de l'agent dans le chat est en français, sans exception. Lors des retours intermédiaires de sous-agents (avant d'avoir les résultats finaux), un **court résumé d'un paragraphe** est bienvenu pour tenir Henri informé, en évitant toute répétition et tout long pavé temporaire. |

## 🌐 Comment formater les images pour le partage NoteColab ?

Henri partage ses notes via le bouton du plugin Obsidian (« Share current note »). Pour que chaque image soit détectée, chiffrée (AES-256-GCM), téléversée et affichée correctement dans le visualiseur web :

| # | Règle | Conforme | Interdit | Raison |
|---|---|---|---|---|
| 1 | Wikilinks natifs | `![[nom_image.png]]` | `![alt](nom_image.png)` | Le plugin ignore la syntaxe Markdown standard pour l'upload. |
| 2 | Nom de fichier seul, sans chemin | `![[nom_image.png]]` | `![[_attachments/.../nom_image.png]]` | L'API rejette tout `/` ou `\` (`HTTP 400 Invalid image filename`). Obsidian retrouve seul le fichier dans `_attachments/`. |
| 3 | Pas de texte après le pipe | `![[nom_image.png]]` puis *Figure 1 : Interface* | `![[nom_image.png\|Figure 1 : Interface]]` | La regex du visualiseur affiche alors un encadré « Embedded note » cassé. La légende va en italique sous la balise. |
| 4 | Largeur en pixels uniquement | `![[nom_image.png\|800]]` | `![[nom_image.png\|800x600]]` | Seul un entier pur (`\d+`) est admis après le pipe. |
| 5 | Image dans le corps de la note | `![[nom_image.png]]` sous un H1/H2 | Image seulement dans le frontmatter | Seuls les médias du corps Markdown sont téléversés. |
