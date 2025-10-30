## Contexte

L'interface Streamlit UI et plusieurs éléments associés (pages/components, scripts de démarrage, dépendances ML) proviennent de l'ancien écosystème basé sur des serveurs MCP désormais obsolètes. Leur présence ajoute de la complexité au dépôt et au script `install.sh` (gestion de `install_streamlit_app`, modèle ML, flags de mode complet). Dans la trajectoire actuelle (suppression MCP, simplification `/agent`, unification de l'installation), ces composants doivent être retirés proprement et la procédure d'installation mise à jour en conséquence.

## Objectif

Explorer et cadrer la suppression complète de l'UI Streamlit et des artefacts reliés aux anciens serveurs MCP, puis mettre à jour `install.sh` pour un mode d'installation unique, clair et fail‑fast, sans branches liées à l'UI/ML.

## Fichiers Concernés

### Du travail effectué précédemment :
- `install.sh` : Contient l'installation de l'UI (Streamlit), du modèle ML et les branches `--full-install`
- `README.md` : Documente les deux modes et l'UI; devra être simplifié après retrait

### Fichiers potentiellement pertinents pour l'exploration :
- `.cursor/streamlit_app/` : Répertoires `app.py`, `pages/`, `components/`, `run_ui.sh`
- `.cursor/memory-bank/models/` : Emplacement du cache de modèle ML
- `.cursor/rules/` : Vérifier les références éventuelles à l'UI
- `.cursor/agents/` : Rapports mentionnant l'UI/ML (historique)

### Recherches à effectuer :
- Recherche sémantique : "Où install_streamlit_app est-il appelé et quelles dépendances installe-t-il ?"
- Recherche sémantique : "Où est géré le téléchargement du modèle ML et quels chemins sont utilisés ?"
- Documentation : Mettre à jour `README.md` pour refléter l'absence d'UI et le mode unique

### Fichiers de résultats d'autres agents (si pertinents) :
- `.cursor/agents/rapport-supprimer-outils-mcp-obsoletes.md` : Contexte de suppression MCP

**Fichier output pour le rapport final :**
- `.cursor/agents/rapport-supprimer-ui-et-restes-serveurs-mcp-mettre-a-jour-installation.md`

## Instructions de Collaboration

- Il est INTERDIT de commencer à implémenter immédiatement.
- Tu DOIS lire EXHAUSTIVEMENT tous les fichiers listés dans « Fichiers Concernés » et confirmer l'étendue exacte des artefacts UI/ML à supprimer.
- Tu DOIS effectuer les recherches sémantiques listées pour tracer toutes les références à l'UI et au modèle ML.
- Tu DOIS aligner avec l'utilisateur sur la portée précise (suppression des répertoires UI, fonctions d'installation, docs, flags) et les impacts.
- Tu DOIS écrire le rapport final dans le fichier output mentionné.
- Ce n'est QU'APRÈS cette exploration exhaustive et la planification convenue que tu pourras commencer l'implémentation.


