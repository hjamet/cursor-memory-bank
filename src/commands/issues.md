# MISSION & OBJECTIF FINAL
Votre unique objectif est de traiter et d'implémenter l'intégralité des issues actuellement ouvertes sur le dépôt GitHub de manière totalement autonome et indépendante. Chaque issue doit être résolue, testée rigoureusement et clôturée sans intervention humaine.

---

# DIRECTIVES D'EXÉCUTION & WORKFLOW GIT
- **Délégation & Isolation :** Utilisez le MCP GitHub pour lister les issues. Pour chaque issue ouverte, lancez un sous-agent dédié. Chaque sous-agent se concentre exclusivement sur sa tâche sur une branche isolée. Vous ne devez jamais travailler sur deux sujets à la fois au sein d'un même sous-agent.
- **Gestion des Commits et Pushes :** 
  - Effectuez des commits réguliers tout au long du développement pour sauvegarder vos avancées locales.
  - Le push sur le dépôt distant est strictement réservé au moment où l'issue est entièrement implémentée, testée et finalisée. Ne pushez rien avant cette validation complète.

---

# VALIDATION, INTEGRATION LIVE & NAVIGATION
- **Tests en Conditions Réelles :** Ne vous limitez pas aux tests unitaires. Lancez l'application localement pour vérifier son comportement en situation réelle et s'assurer de la bonne liaison de toutes les issues corrigées ensemble.
- **Validation Web & UI:** Si le projet comporte une interface web, utilisez exclusivement l'outil de navigateur intégré pour tester manuellement et valider le rendu ainsi que les fonctionnalités (comme les flux de connexion). N'utilisez pas de frameworks d'automatisation externes comme Playwright.
- **Contrôle Qualité :** Un agent spécifique doit être désigné pour centraliser et vérifier que l'ensemble du système fonctionne parfaitement avant de valider l'intégration et de procéder au merge général.

---

# INTERACTION GITHUB & COMMENTAIRES
Vos interactions sur GitHub via le MCP doivent refléter votre totale autonomie :
- **Commentaires de Référence Uniquement :** Ne posez jamais de questions et n'attendez aucune réponse de l'opérateur humain dans les espaces de discussion.
- **Seuils d'Alerte :** Ne laissez un commentaire sur l'issue qu'en cas de réalisation majeure, de blocage technique absolu ou de décision architecturale lourde (par exemple, si une contrainte rend l'implémentation initiale impossible). Décrivez la situation ou le choix technique fait pour archive, puis continuez immédiatement votre travail.
- **Clôture :** Une fois l'implémentation validée en live, fermez définitivement l'issue.