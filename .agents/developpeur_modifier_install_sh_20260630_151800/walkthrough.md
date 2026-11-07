# Walkthrough - Modification de `install.sh`

## Objectif
Modifier le script d'installation `install.sh` pour que, par défaut, l'installation soit uniquement globale, et qu'elle ne devienne locale (dans le dépôt d'exécution) que si l'option `--local` (ou `-l`) est fournie.

## Contexte
Auparavant, le script `install.sh` installait systématiquement les règles (`.cursor/rules`), les commandes personnalisées (`.cursor/commands`), les configurations d'agent (`.agent/rules` et `.agent/workflows`) localement dans le répertoire cible, en plus des installations globales (workflows globaux, outil de monitoring global, etc.). Afin d'éviter de polluer par défaut le dépôt d'exécution avec des configurations locales, l'installation locale est désormais optionnelle.

## Action
1. **Ajout de l'argument de ligne de commande `--local` (ou `-l`)** :
   - Mise à jour du parseur d'arguments dans `install.sh` pour intercepter `-l` et `--local` et lever la variable `INSTALL_LOCAL=1`.
   - Mise à jour de la fonction `show_help` pour documenter cette nouvelle option.
2. **Conditionalisation de l'installation locale dans `install_basic_rules`** :
   - Encapsulation des blocs d'installation locaux (`.cursor/rules`, `install_commands`, `install_agent_config`, `manage_gitignore`) sous une condition vérifiant la présence de la variable `INSTALL_LOCAL`.
3. **Robustesse de l'installation globale** :
   - Ajout d'une vérification du clone du dépôt Git (`temp_dir/repo`) avant le démarrage de l'installation globale (workflows, monitor, etc.) pour garantir que les fichiers requis soient présents même si l'installation locale a été sautée.
4. **Correction des fins de ligne** :
   - Conversion du fichier `install.sh` au format Unix LF (suppression des retours chariot `\r` problématiques pour Bash sous Windows).
5. **Validation & Tests** :
   - Création de répertoires temporaires pour valider l'installation avec et sans l'option `--local`. Les résultats confirment le comportement attendu.

## Impact Envisagé
- **Propreté** : Les utilisateurs peuvent désormais exécuter `install.sh` pour mettre à jour ou installer l'environnement globalement (workflows et monitor global) sans impacter/polluer leur espace de travail Git local par défaut.
- **Flexibilité** : L'option `--local` permet aux développeurs de forcer l'installation de la structure locale lorsque nécessaire.
