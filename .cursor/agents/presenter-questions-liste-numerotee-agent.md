## Contexte

Lors de la présentation finale de la commande `/agent`, les questions destinées à l'utilisateur sont actuellement affichées sous forme de puces non numérotées. Pour faciliter la sélection (réponse par numéro) et améliorer la lisibilité, nous souhaitons normaliser l'affichage en liste numérotée.

## Objectif

Adapter la sortie de la commande `/agent` afin que la section « ❓ Questions » soit systématiquement présentée en **liste numérotée** (`1.`, `2.`, `3.`). Le changement est purement de présentation et ne modifie pas la logique métier.

## Fichiers Concernés

### Du travail effectué précédemment :
- `.cursor/commands/agent.md` : Définit le format de présentation standard incluant la section « ❓ Questions » actuellement en liste à puces.

### Fichiers potentiellement pertinents pour l'exploration :
- `README.md` : Référence globale des conventions de présentation pour cohérence.

### Recherches à effectuer :
- Vérifier la compatibilité Markdown/renderer de listes numérotées dans l'environnement cible (aucun changement fonctionnel attendu).

### Fichiers de résultats d'autres agents (si pertinents) :
- Aucun.

**Fichier output pour le rapport final :**
- `.cursor/agents/rapport-presenter-questions-liste-numerotee-agent.md`

## Instructions de Collaboration

- Il est **INTERDIT** de commencer à implémenter immédiatement.
- Tu **DOIS** lire exhaustivement les fichiers listés dans « Fichiers Concernés ».
- Tu **DOIS** discuter avec l'utilisateur pour valider le format exact si ambiguïtés.
- Tu **DOIS** conserver l'ordre et le contenu des questions, en ne changeant que le style de liste.
- Tu **DOIS** écrire le rapport final dans le fichier output mentionné.
- Seulement APRÈS cette exploration et validation, tu pourras modifier la présentation de la section « ❓ Questions » dans `.cursor/commands/agent.md`.


