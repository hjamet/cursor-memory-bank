---
created: 2026-11-04
updated: 2026-11-04
type: skill
tags:
  - skill
  - sci
  - hellenvilliers
  - intendance
aliases:
  - Création de Tâches Opérationnelles SCI Hellenvilliers
  - sci-task-creator
---

# Skill SCI Task Creator (`sci-task-creator`)

Ce skill régit la création, la vérification factuelle et le formatage des tâches opérationnelles destinées à l'application de la SCI Hellenvilliers (`sci-family-app`), à partir d'une consigne écrite, d'une description orale ou d'un transcript brut d'Henri.

---

## 🎯 Quand utiliser ce skill ?

Activer systématiquement ce skill lorsque :
- Henri demande de préparer, rédiger, simplifier ou formater une tâche opérationnelle pour la SCI (ex. : entretien chaudière, livraison fioul, ramonage, assurances, piscine, maintenance, démarches administratives).
- Henri fournit une description orale ou un enregistrement de voicenote décrivant une mission ou un travail à faire réaliser par un membre de la famille.
- Une tâche opérationnelle existante doit être mise à jour ou épurée.

---

## 💬 Charte Rédactionnelle : Ton Familial, Concision & Utilité Pratique (MANDATOIRE)

> [!IMPORTANT]
> **On écrit pour les sœurs et les parents d'Henri, qui connaissent déjà la maison et la famille !**
> 1. **Ton agréable, familial et naturel** : Bannir le jargon technocratique, juridique ou robotique (« l'associé mandaté procèdera à… », « entretien courant du bassin de Rosings 10 x 4 m »). Écrire simplement, chaleureusement et directement, comme on explique quelque chose d'utile à ses sœurs.
> 2. **Principe du Delta d'Information (Zéro détail bêtement inutile)** : Ne donner **QUE ce que les membres de la famille ignorent et qui leur sert concrètement pour agir**. Supprimer les évidences (tout le monde sait où est la piscine et à quoi elle ressemble) et les chiffres ou références techniques superflus (dimensions du bassin, cubages théoriques, numéros de série abscons dans le texte).
> 3. **Répondre aux vraies questions pratiques et de sécurité** : Lorsqu'une tâche implique une manipulation matérielle ou l'achat d'un produit (ex. changer le bidon de pH Moins de la piscine), mettre immédiatement en avant :
>    - **Sécurité & Faisabilité** : Est-ce une manœuvre faisable facilement soi-même sans danger ? Quelles protections concrètes faut-il mettre avant d'y toucher (ex. gants, lunettes, attention aux éclaboussures acides) ?
>    - **Achat concret & Magasins** : Quel produit / quelle marque acheter exactement ? Est-ce qu'on en trouve facilement au E.Leclerc ou en magasin de bricolage à côté (Verneuil, Conches, Breteuil, Évreux), ou faut-il aller chez un pisciniste précis ?
>    - **Manœuvre étape par étape** : Comment faire le geste concrètement en 3 ou 4 phrases claires ?
> 4. **Brièveté et lisibilité immédiate** : Aller droit au but. Un membre de la famille doit trouver l'information essentielle en 20 secondes sans devoir lire un pavé formel.

---

## 🛑 Protocole d'Exécution Obligatoire (Zero-Trust & Contre-Vérification $N=2$)

### Étape 1 : Déploiement de $N=2$ Éclaireurs Indépendants à Tour 0 (Zéro Scission)

L'Agent Racine ne rédige **JAMAIS** la tâche à partir de ses seules suppositions. L'information étant dispersée entre plusieurs sources (`gdrive:`, coffre local, base Supabase et web pratique), il crée un unique artefact de questions (`questions_sci_task.md`) et déploie immédiatement **$N=2$ sous-agents `eclaireur` en parallèle** (`Model: 'flash'`, pointant tous deux vers ce même fichier unique, **zéro scission** — cf. [_agents/rules/sous-agents.md](file:///c:/Users/hjamet/Documents/VoiceNotes/_agents/rules/sous-agents.md)) afin que chacun croise :

1. **Fouille du Google Drive de Frédéric Jamet (`gdrive:`) & du Coffre VoiceNotes** :
   - Utilise le CLI `rclone` (skill `rclone-drive`) en lecture seule sur `gdrive:` et fouille `notes/`, `administratif/`, `_attachments/` et `voicenotes/`.
   - Isole les PDF originaux (factures antérieures, devis, contrats, notices) et les vraies photos des équipements dans `_attachments/`.
2. **Vérification pratique et concrète (achats, sécurité, manipulation)** :
   - Vérifie les conditions réelles d'achat des consommables (disponibilité en grande surface type E.Leclerc / bricolage vs pisciniste, marques compatibles, réglementation éventuelle) et les consignes de sécurité domestique.

---

## 📋 Structure Canonique de l'Artefact de Tâche

Tout artefact produit par ce skill (généré dans `<appDataDir>/brain/<id>/tache_<nom>.md` ou mis à jour en base / dans le coffre) respecte la structure en 5 sections suivantes :

### 1. Titre de la Tâche (prêt à copier)
Un bloc Markdown clair et naturel :
```text
[Verbe d'action clair] [Objet concret] ([Intervenant ou lieu si utile])
```

### 2. Description Complète (Bloc de Code UNIQUE Copiable)
Un **SEUL ET UNIQUE bloc de code copiable** (` ```text `), court, fluide et agréable à lire :
- **L'essentiel en 2 phrases** : à quoi sert la tâche et quand la faire.
- **Infos pratiques indispensables (ce qu'on ne sait pas déjà)** :
  - *Si manipulation / produit à acheter* : où acheter le produit (ex. Leclerc, magasin de bricolage ou pisciniste, quelles marques/formats prendre), si la manœuvre est sans danger pour un particulier et quelles protections porter (gants, etc.).
  - *Si artisan à faire venir* : qui appeler, combien ça coûtait d'habitude avec Papa et où se trouve la clé ou l'accès si ce n'est pas évident.
- **Règlement tout simple (1 phrase)** : payer avec la carte de la SCI (ou avancer et mettre la facture sur le site pour remboursement, au nom de la SCI HELLENVILLIERS).
- *(Important : Zéro coordonnées détaillées ni liste d'étapes dans ce bloc, elles sont déjà dans les sections 3 et 4 ci-dessous ; zéro dimension ou chiffre technique inutile).*

### 3. To-Do List des Étapes à Réaliser
Une liste courte et concrète (`- [ ]`) décrivant uniquement les vraies actions pratiques à faire (3 à 5 étapes courtes maximum, formulées simplement).

### 4. Informations Pratiques Importantes (Clé / Valeur)
Une liste `- **Clé** : Valeur` dans les notes du coffre Obsidian (zéro tableau, cf. [coffre-obsidian.md](file:///c:/Users/hjamet/Documents/VoiceNotes/_agents/rules/coffre-obsidian.md)) ou un tableau Markdown à 2 colonnes dans un artefact technique `brain/`, regroupant uniquement les données utiles (contact, téléphone, email, produit/marque à acheter, précautions de sécurité, prix habituel).

### 5. Documents & Photos Importants (avec liens locaux cliquables)
Une liste structurée (dans le coffre) ou un tableau (dans `brain/`) listant les pièces justificatives et vraies photos d'`_attachments/` utiles (avec lien `[Nom](file:///...)` et statut Déjà lié / À uploader).

---

## 🚫 Interdictions Absolues & Invariants Techniques (Garde-fous)

- **Attribution Obligatoire de la Création à Henri (`member_id = 1`) pour les Points de Validation** : Toute tâche créée en base de données par l'agent (via `POST /api/tasks` avec le token d'Henri ou en SQL) DOIT être créée au nom d'**Henri Jamet (`member_id = 1`, `created_by` / `proposed_by` = Henri)** et en statut `PROPOSED`, afin qu'Henri gagne systématiquement les points de création lorsqu'il valide la tâche sur `https://hellenvilliers.henri-jamet.com/taches`. De plus, pour les tâches dont Henri a déjà réalisé l'action lui-même (ex. bascule d'un contrat ou d'un RIB), il doit également être renseigné comme exécutant/assigné pour toucher les points de réalisation.
- **Zéro Ton Administratif ou Robotique** : On parle à sa famille, pas à un tribunal de commerce.
- **Zéro Détail Inutile** : Pas de dimensions de piscine (`10 x 4 m`), de volumes en $m^3$ ou de jargon technique qui n'aide pas concrètement à faire la tâche.
- **Zéro Sous-Sol ou Pièce Imaginaire** & **Zéro Image IA Inventée** : Uniquement les vrais emplacements et les vraies photos d'`_attachments/`.
- **Zéro Morcellement de la Description** : La description reste dans un unique bloc de code copiable en un clic.

---

## 🔄 Boucle d'Auto-Évolution (/learn — Rasoir d'Ockham à taille constante)

À chaque retour, critique ou simplification demandée par Henri ou un membre de la famille sur une tâche opérationnelle, l'agent déclenche une passe `/learn` pour affiner les consignes de rédaction, les magasins de référence et les règles de sécurité à taille constante sans empiler d'ajouts en bas de note.
