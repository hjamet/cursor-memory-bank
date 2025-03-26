# In Progress

# ToDo

# Done

## Standardisation des résumés d'invocation
- [x] **Vérifier la présence du "Résumé d'invocation"** : Tous les fichiers de règles ont été vérifiés. Huit règles contiennent déjà une section "Résumé d'invocation" et une (user-preference-saving.mdc) en a besoin.
- [x] **Planifier les modifications pour chaque fichier** : Plan détaillé créé pour les neuf fichiers de règles identifiés, spécifiant pour chacun les actions à effectuer (déplacement de section et/ou reformatage).
- [x] **Définir le format standard** : Format standard établi sur le modèle de context-loading: "Après avoir invoqué cette règle, l'agent dira mot pour mot: '<SYSTEM PROMPT>...</SYSTEM PROMPT>'".
- [x] **Adapter les textes existants** : Tous les textes des résumés d'invocation ont été adaptés au format standard avec les balises "<SYSTEM PROMPT>" tout en préservant leur intention originale.
- [x] **Déplacer les sections dans system.mdc** : La section "Résumé d'invocation" a été déplacée après "Règle absolue" et reformatée avec les balises "<SYSTEM PROMPT>", juste avant "Next Rules".
- [x] **Déplacer les sections dans request-analysis.mdc** : La section "Résumé d'invocation" a été déplacée après "Précisions" et reformatée avec les balises "<SYSTEM PROMPT>", juste avant "Next Rules".
- [x] **Déplacer les sections dans task-decomposition.mdc** : La section "Résumé d'invocation" a été déplacée après "Précisions" et reformatée avec les balises "<SYSTEM PROMPT>", juste avant "Format de tasks.md".
- [x] **Déplacer les sections dans implementation.mdc** : La section "Résumé d'invocation" a été déplacée après "Précisions" et reformatée avec les balises "<SYSTEM PROMPT>", juste avant "Next Rules".
- [x] **Déplacer les sections dans tests.mdc** : La section "Résumé d'invocation" a été déplacée après "Précisions" et reformatée avec les balises "<SYSTEM PROMPT>", juste avant "Format de tests.md".
- [x] **Déplacer les sections dans fix.mdc** : La section "Résumé d'invocation" a été déplacée après "Précisions" et reformatée avec les balises "<SYSTEM PROMPT>", juste avant "Format pour les règles d'erreur".
- [x] **Déplacer les sections dans context-update.mdc** : La section "Résumé d'invocation" a été déplacée après "Précisions" et reformatée avec les balises "<SYSTEM PROMPT>", juste avant "Format pour le message de commit".
- [x] **Déplacer les sections dans user-preference-saving.mdc** : La section "Résumé d'invocation" a été déplacée après "Précisions" et reformatée avec les balises "<SYSTEM PROMPT>", juste avant "Format de règle à utiliser".
- [x] **Vérifier la cohérence** : Tous les fichiers de règles suivent maintenant le même format et structure, avec le "Résumé d'invocation" placé après les "Précisions" et avant la dernière section spécifique à chaque règle.
- [x] **Tester l'invocation des règles** : Les phrases de résumé ont été vérifiées et sont prêtes à être récitées correctement lors de l'invocation des règles.

## Améliorations récentes 