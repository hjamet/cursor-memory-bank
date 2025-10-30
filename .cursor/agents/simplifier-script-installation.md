## Contexte

Lors du travail actuel sur la suppression des outils MCP obsolètes dans `install.sh`, il est apparu que le script d'installation maintient deux modes distincts : le mode basique (rules only) et le mode complet (`--full-install`). Cette distinction ajoute de la complexité inutile au script.

Le mode basique installe seulement les règles essentielles, tandis que le mode complet installe le système de workflow complet avec Streamlit UI et ML model. Cependant, après la suppression des serveurs MCP, cette distinction devient moins pertinente et ajoute de la complexité de maintenance.

Simplifier le script en un seul mode d'installation permettrait de réduire la complexité, faciliter la maintenance et rendre le script plus clair et direct.

## Objectif

Explorer la possibilité de simplifier le script d'installation en supprimant la distinction entre mode basique et mode complet. Créer un seul mode d'installation qui installe tout ce qui est nécessaire de manière cohérente.

## Fichiers Concernés

### Du travail effectué précédemment :
- `install.sh` : Script d'installation actuel avec deux modes (basique et `--full-install`)
- `.cursor/agents/supprimer-outils-mcp-obsoletes_30-10-2025.md` : Tâche actuelle de suppression des serveurs MCP qui révèle la complexité du script

### Fichiers potentiellement pertinents pour l'exploration :
- `install.sh` : Analyser toute la logique conditionnelle basée sur `FULL_INSTALL`
- `README.md` : Vérifier les sections documentant les deux modes d'installation
- `.cursor/rules/agent.mdc` : Vérifier si des règles mentionnent les modes d'installation

### Recherches à effectuer :
- Recherche sémantique : "Comment fonctionne le système de modes d'installation dans install.sh ?"
- Recherche sémantique : "Quelles sont les différences entre le mode basique et le mode complet ?"
- Documentation : Lire `README.md` pour comprendre les différences documentées entre les modes

### Fichiers de résultats d'autres agents (si pertinents) :
- `.cursor/agents/rapport-supprimer-outils-mcp-obsoletes_30-10-2025.md` : Rapport de la tâche actuelle de suppression MCP (quand disponible)

**Fichier output pour le rapport final :**
- `.cursor/agents/rapport-simplifier-script-installation_30-10-2025.md`

## Instructions de Collaboration

Tu es **INTERDIT** de commencer à implémenter quoi que ce soit immédiatement. Ta première et UNIQUE tâche est l'exploration et la compréhension :

1. **LIS EXHAUSTIVEMENT** tous les fichiers listés ci-dessus dans "Fichiers Concernés" - tu dois comprendre comment fonctionne actuellement le système de deux modes d'installation
2. **EFFECTUE les recherches sémantiques** mentionnées pour identifier toutes les références aux modes d'installation dans le codebase
3. **LIS le README.md** et identifie toutes les sections/documentations qui mentionnent les deux modes d'installation
4. **ANALYSE** toutes les branches conditionnelles dans `install.sh` basées sur `FULL_INSTALL`
5. **IDENTIFIE** ce qui est spécifique au mode complet vs mode basique
6. **COMPRENDS** l'impact de la suppression de cette distinction
7. **DISCUTE avec l'utilisateur** pour clarifier :
   - Qu'est-ce qui doit être installé par défaut dans le mode unique ?
   - Faut-il garder certaines choses optionnelles ou tout installer systématiquement ?
   - Comment gérer les cas où certains composants ne sont pas nécessaires ?
8. **ÉTABLIS un plan d'action détaillé** avec l'utilisateur avant toute modification
9. **DOIT** écrire le rapport final dans le fichier output mentionné après avoir terminé

Seulement APRÈS avoir complété cette exploration exhaustive et cette planification collaborative, tu peux commencer à considérer tout travail de simplification. L'exploration est OBLIGATOIRE, pas optionnelle.

