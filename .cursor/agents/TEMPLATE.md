# Template de Fichier de Tâche

Ce fichier sert de **template et de documentation** pour le format attendu des fichiers de tâches dans `.cursor/agents/`.

## Format Obligatoire

Tous les fichiers de tâches doivent suivre **exactement** ce format avec les 4 sections obligatoires :

---

## Contexte

[Écrire en français une histoire narrative expliquant pourquoi cette tâche existe. Mentionner ce qui a été découvert, les problèmes identifiés, ou les opportunités qui justifient cette tâche. Utiliser un langage naturel et narratif, sans trop de détails techniques.]

Cette section doit raconter une histoire : qu'est-ce qui s'est passé qui a mené à identifier cette tâche ? Quels problèmes ont été découverts ? Quelles opportunités ont été identifiées ?

---

## Objectif

[Écrire en français une description vague mais claire de ce qui doit être accompli. L'objectif doit être exploratoire, pas trop précis. Accepter le vague - la précision viendra avec la discussion lors de l'implémentation.]

Exemples de bons objectifs :
- ✅ "Explorer la possibilité d'optimiser le système d'authentification pour améliorer les performances sous charge"
- ✅ "Implémenter un système de cache pour réduire les requêtes répétées à la base de données"
- ❌ "Configurer un cache Redis avec paramètres spécifiques X, Y, Z" (trop précis)
- ❌ "Améliorer le code" (trop vague)

L'objectif doit être **assez précis pour être actionnable** mais **assez vague pour permettre l'exploration collaborative**.

---

## Fichiers Concernés

[Écrire en français. Lister les fichiers, dossiers, recherches et documentation nécessaires pour comprendre le contexte.]

### Du travail effectué précédemment :
- `chemin/vers/fichier1` : [Expliquer ce qui a été fait ou découvert dans ce fichier]
- `chemin/vers/fichier2` : [Expliquer ce qui est pertinent]

### Fichiers potentiellement pertinents pour l'exploration :
- `chemin/vers/fichier3` : [Expliquer pourquoi ce fichier pourrait être important]
- `chemin/vers/dossier/` : [Expliquer la pertinence]

### Recherches à effectuer :
- Recherche sémantique : "Comment sont gérées les performances dans le codebase ?"
- Recherche web : "Meilleures pratiques pour optimiser l'authentification JWT"
- Documentation : Lire `README.md` et `documentation/architecture.md`

### Fichiers de résultats d'autres agents (si pertinents) :
- `.cursor/agents/rapport-tache-precedente_19-01-2025.md` : [Expliquer pourquoi ce rapport est utile]

**Fichier output pour le rapport final :**
- `.cursor/agents/rapport-{titre-kebab-case}_{DD-MM-YYYY}.md`

**IMPORTANT** : L'agent qui traitera cette tâche devra lire TOUS ces fichiers avant de commencer. Assure-toi que la liste est exhaustive.

---

## Instructions de Collaboration

[Écrire en français. **OBLIGATOIRE ET CRITIQUE** : Cette section doit être extrêmement directive et impérative.]

Tu DOIS spécifier que l'agent :

- **EST INTERDIT** de commencer à implémenter quoi que ce soit immédiatement
- **DOIT** lire EXHAUSTIVEMENT tous les fichiers listés dans "Fichiers Concernés" avant toute action
- **DOIT** effectuer toutes les recherches sémantiques et web mentionnées
- **DOIT** lire le README et toute documentation pertinente
- **DOIT** atteindre une compréhension approfondie du contexte et du projet avant toute discussion
- **DOIT** discuter avec l'utilisateur pour clarifier les attentes précises, poser des questions sur les contraintes techniques, et établir un plan d'action détaillé ensemble
- **DOIT** écrire le rapport final dans le fichier output mentionné après avoir terminé
- Seulement APRÈS avoir complété cette exploration exhaustive et cette planification collaborative, peut commencer toute implémentation

**Emphasizer que l'exploration est OBLIGATOIRE, pas optionnelle.**

---

## Notes pour la Création de Tâches

- **Nom de fichier** : `{titre-kebab-case}_{DD-MM-YYYY}.md`
- **Fichier output** : `rapport-{titre-kebab-case}_{DD-MM-YYYY}.md`
- **Langue** : Tout le contenu doit être en français
- **Format** : Respecter exactement les 4 sections ci-dessus
- **Références** : Mentionner les fichiers de résultats d'autres agents si pertinents

## Exemple Complet

Voir les fichiers de tâches existants dans `.cursor/agents/` pour des exemples concrets.

