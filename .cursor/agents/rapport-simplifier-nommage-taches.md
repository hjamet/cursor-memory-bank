# Rapport : Simplifier le format de nommage des fichiers de tâches

## Résumé

Simplification du format de nommage des fichiers de tâches en supprimant les timestamps (dates) des noms de fichiers. Le format passe de `{titre-kebab-case}_{DD-MM-YYYY}.md` à `{titre-kebab-case}.md`.

## Modifications effectuées

### Fichiers modifiés

1. **`.cursor/commands/task.md`**
   - Supprimé l'étape d'obtention de la date du jour
   - Format simplifié : `{titre-kebab-case}.md` au lieu de `{titre-kebab-case}_{DD-MM-YYYY}.md`
   - Ajouté une instruction pour vérifier l'unicité du titre dans la roadmap

2. **`.cursor/rules/agent.mdc`**
   - Adapté la section "Générer le Nom de Fichier" pour supprimer les dates
   - Mis à jour les exemples avec le nouveau format
   - Ajouté une instruction pour vérifier l'unicité du titre

3. **`.cursor/agents/TEMPLATE.md`**
   - Mis à jour la documentation du format de nommage
   - Supprimé les références aux timestamps dans les exemples
   - Ajouté une note sur l'importance de l'unicité des titres

4. **`.cursor/agents/roadmap.yaml`**
   - Mis à jour tous les noms de fichiers pour refléter le nouveau format sans dates

5. **`README.md`**
   - Mis à jour les références au format de nommage dans la documentation

### Fichiers renommés

1. `supprimer-outils-mcp-obsoletes_30-10-2025.md` → `supprimer-outils-mcp-obsoletes.md`
2. `supprimer-mise-a-jour-statut-timestamps-roadmap_30-10-2025.md` → `supprimer-mise-a-jour-statut-timestamps-roadmap.md`
3. `simplifier-script-installation_30-10-2025.md` → `simplifier-script-installation.md`
4. `corriger-comportement-agent-mode-plan-planifier-tache-selectionnee-plutot-que-selection_30-10-2025.md` → `corriger-comportement-agent-mode-plan-planifier-tache-selectionnee-plutot-que-selection.md`
5. `rapport-supprimer-outils-mcp-obsoletes_30-10-2025.md` → `rapport-supprimer-outils-mcp-obsoletes.md`

## Solutions implémentées

### Gestion des collisions

Pour éviter les collisions de noms de fichiers, une instruction a été ajoutée dans les commandes et règles pour vérifier l'unicité du titre dans la roadmap avant de créer une nouvelle tâche. L'agent doit s'assurer de ne pas donner le même titre à chaque tâche.

### Format final

- **Nom de fichier de tâche** : `{titre-kebab-case}.md`
- **Nom de fichier de rapport** : `rapport-{titre-kebab-case}.md`
- **Exemple** : "Supprimer tous les serveurs MCP obsolètes" → `supprimer-tous-les-serveurs-mcp-obsoletes.md`

## Résultat

Le système de nommage est maintenant simplifié et ne nécessite plus d'exécuter une commande terminal pour obtenir la date à chaque création de tâche. La création de tâches est désormais plus fluide et moins dépendante d'outils externes.

## Validation

- ✅ Tous les fichiers de configuration ont été mis à jour
- ✅ Tous les fichiers existants ont été renommés
- ✅ La roadmap.yaml reflète les nouveaux noms de fichiers
- ✅ La documentation (README.md) a été mise à jour
- ✅ Les instructions pour éviter les collisions ont été ajoutées

## Notes

Le format simplifié rend la création de tâches plus rapide et évite la dépendance à des commandes externes pour obtenir la date. La responsabilité de l'unicité des titres incombe désormais à l'agent lors de la création des tâches.

