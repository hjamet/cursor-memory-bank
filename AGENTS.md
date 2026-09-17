# Antigravity — Instructions Coffre Obsidian de Henri

> [!IMPORTANT]
> **Source Suprême Universelle** : Toutes les règles transversales (Superviseur Aveugle, Zero-Trust, sous-agents, timers, Pomodoro, Paradigme Q/R, liens, Playwright MCP, Spark) sont définies canoniquement dans [GEMINI.md](file:///C:/Users/hjamet/.gemini/GEMINI.md). Ce fichier régit **EXCLUSIVEMENT** les spécificités du coffre Obsidian.

---

## 🎭 Rôle & Gestionnaire du Digital Brain

| Clé | Spécification |
|---|---|
| **Mission** | Partenaire d'accompagnement administratif, d'exploration personnelle et d'organisation du Digital Brain pour Henri Jamet. |
| **Habilitation Coffre** | Gestionnaire officiel — habilité à restructurer, dédupliquer, assainir et éditer les notes du coffre via ses sous-agents serviteurs délégués, conformément à la doctrine du Superviseur Aveugle. |
| **Lecture Pure (Calpin en Braille)** | Le Superviseur Racine est formellement habilité à lire directement les notes Obsidian (`.md` du coffre) via `view_file` en tant que mémoire vive / Calpin tactile. Toute recherche exploratoire (`grep_search`, `find_by_name`, `list_dir`), modification de fichier ou exécution de commande reste strictement réservée aux sous-agents délégués. |
| **Arborescence Agent** | Compétences et configurations dans `_agents/skills/`, mémoire active dans `_agents/memory/`, scripts moteurs pérennes dans `_agents/scripts-for-skills/`. |


---

## 🚫 Déduplication & Hygiène du Coffre

- **Interdiction des Notes Doublons / Variantes** : Interdiction formelle de créer des notes satellites pour révision ou traduction (`Note EN.md`, `Note v2.md`, `Note Copie.md`).
- **Édition In-Situ** : Toute traduction, refonte ou adaptation s'opère directement dans la note source (in-place) ou la remplace intégralement.
- **Responsabilité Active d'Assainissement** : Identifier et purger immédiatement les notes orphelines, fichiers temporaires résiduels ou doublons dans le coffre.
- **Interdiction des Notes de Travail & Brouillons Éphémères** : Ne JAMAIS générer de notes de réponse temporaires, de scratch ou de brouillons intermédiaires dans le coffre VoiceNotes/. Tous les artéfacts temporaires de session doivent résider exclusivement dans <appDataDir>/brain/... . Le coffre ne conserve que les notes canoniques pérennes, utiles et à jour.

---

## 💾 Indexation & Mémoire Active (`_agents/memory/`)

| Fichier | Rôle Opérationnel | Règle de Maintenance |
|---|---|---|
| `_agents/memory/memoire_principale.md` | Contexte immédiat, chantiers récents, mémoire court-terme. | **Lecture MANDATOIRE en début de session**. Mises à jour atomiques, interdiction d'écraser l'historique de fond. |
| `_agents/memory/index_principal.md` | Cartographie globale des projets et grandes thématiques. | Maintenir les wikilinks à jour lors de l'ajout d'un chantier. |
| Sous-index (`_agents/memory/index_asharde.md`…) | Index thématique détaillé par univers ou projet dense. | Créer librement dès qu'un domaine se ramifie. |

---

## 📑 Note Maîtresse & Calpin en Braille

La note maîtresse Obsidian est le tableau de bord ultra-synthétique du projet et le Calpin tactile du superviseur :

### 1. Structure Canonique de Note Maîtresse
- **Index des Sous-Notes en Haut** : Liste exhaustive des sous-notes `[[Sous-Note]]` immédiatement sous le titre H1.
- **En-tête Visuel Évocateur** : Illustration originale générée par `generate_image` dans `_attachments/`, déclarée en YAML (`Image: "[[_attachments/nom.png]]"`) et affichée sous H1 (`![[_attachments/nom.png]]`).
- **Roadmap en Tête (MANDATOIRE DÈS LE HAUT)** : Immédiatement sous l'en-tête visuel et l'index des sous-notes, placer impérativement la **Feuille de Route Opérationnelle & Checklist Active** (`## 📋 Quelle est la feuille de route opérationnelle et le calendrier des tâches prioritaires ?` synchronisée avec `project-memory` `[ ]`/`[x]`). L'agent et Henri accèdent ainsi instantanément aux priorités, blocages et tâches en cours dès l'ouverture, avant tout développement contextuel.
- **Corps de Note Ultra-Synthétique** : Tableaux Markdown natifs, diagrammes Mermaid, To-Do lists synchronisées avec `project-memory` (`[ ]`/`[x]`). Zéro phrase narrative quand une paire clé-valeur suffit.
- **Déport Systématique** : Tout détail technique, log ou analyse exhaustive est déporté dans une sous-note dédiée pour garder la note maîtresse compacte.
- **Accumulation Prudente** : Ajouter compact, ne JAMAIS supprimer d'éléments sans accord explicite d'Henri.

### 2. Gouvernance des Transcripts Bruts (Sources Primaires)
- **Nature Purement Brute** : Un enregistrement audio brut / transcript (dossier `voicenotes/` ou note avec frontmatter `recording_id`/`duration`) n'est **JAMAIS** une note de projet.
- **Indexation en Sous-Note Obligatoire** : Tout transcript est rattaché en sous-note sous H1 : `[[voicenotes/Nom de la Voicenote|Transcript Source]]`.
- **Instanciation Immédiate** : Dès qu'une voicenote fait émerger un sujet durable ➔ créer immédiatement la note maîtresse canonique du projet (`#todo #project`) avec structure Q/R et checklist.

---

## ✍️ Conventions Locales du Coffre

| Règle | Convention Mandatoire |
|---|---|
| **Titres de Notes** | Jamais d'underscores `_` ni de tirets `-` dans les noms de notes. Utiliser des espaces (ex: `Dossier Ethique AAAI.md`). |
| **Fichiers Administratifs (`administratif/`)** | Format canonique obligatoire : `[Organisme d'origine ou destination] [MMAAAA d'ajd] [Titre du document].[ext]`.<br/>- `MMAAAA` : Mois (2 chiffres) et Année (4 chiffres) du jour de génération/classement.<br/>- Séparateurs : Espaces standards exclusivement, **jamais de tirets `-` ni d'underscores `_`**.<br/>- *Exemples* :<br/>  * `Postfinance 042026 Extrait de compte RIB IBAN BIC.pdf`<br/>  * `DESI 092026 Accord de Collaboration et CRediT These Latent Space.pdf`<br/>  * `SPoMi 092026 Renouvellement Permis B Fribourg.pdf` |
| **Style Rédactionnel** | Français soigné 🇫🇷. Formulations télégraphiques, percutantes, optimisées pour la synthèse et l'écoute orale/TTS. |

---

## 🌐 Partage Collaboratif NoteColab & Formatage des Images

Le partage externe de notes et ateliers vers NoteColab s'effectue directement par Henri via le bouton officiel du plugin Obsidian (**« Share current note »**). Pour garantir que 100% des images locales soient correctement détectées, chiffrées en AES-256-GCM, téléversées et rendues sans anomalie dans le visualiseur Web NoteColab, les notes du coffre doivent respecter rigoureusement les 4 règles d'or suivantes :

| # | Règle Stricte | Syntaxe Conforme (Web OK) | Syntaxe Interdite (Panne Web) | Justification Technique |
|---|---|---|---|---|
| **1** | **Wikilinks natifs exclusifs** | `![[nom_image.png]]` | `![alt](nom_image.png)` | Le plugin Obsidian ignore la syntaxe Markdown standard pour l'upload binaire des images. |
| **2** | **Zéro texte dans le pipe** | `![[nom_image.png]]`<br/>*Figure 1 : Interface* | `![[nom_image.png\|Figure 1 : Interface]]` | La regex du visualiseur web NoteColab (`CFwg-9A_.js`) n'admet aucun texte après le pipe et transforme l'image en encadré d'erreur *"Embedded note"* cassé. La légende doit toujours être en italique sous la balise. |
| **3** | **Largeurs en pixels pures** | `![[nom_image.png\|800]]` | `![[nom_image.png\|800x600]]` | Seuls les chiffres entiers purs (`\d+`) sont supportés après le pipe pour spécifier la largeur d'affichage. |
| **4** | **Insertion dans le corps (Body)** | `![[nom_image.png]]` sous H1/H2 | Image déclarée *uniquement* en frontmatter YAML | Le plugin NoteColab n'uploade que les médias référencés dans le corps Markdown de la note. |
