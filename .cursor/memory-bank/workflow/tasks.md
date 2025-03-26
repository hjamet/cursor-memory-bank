# In Progress

## 1. Développement des règles
1.1. [ ] **Ajouter les exemples de workflow** : Créer les sections Exemple pour implementation.mdc et tests.mdc
- Actions:
  * Lire les fichiers implementation.mdc et tests.mdc
  * Créer une section Exemple dans chaque fichier
  * Ajouter des exemples d'utilisation avec [...] pour le contenu dynamique
  * Ajouter des phrases explicatives pour chaque étape
  * Positionner la section entre Next Rules et Start Rule
- Fichiers: implementation.mdc, tests.mdc
- Dépendances: Aucune
- Validation: Les exemples sont clairs et suivent le format standard

1.2. [ ] **Ajouter les exemples de contexte** : Créer les sections Exemple pour context-update.mdc et user-preference-saving.mdc
- Actions:
  * Lire les fichiers context-update.mdc et user-preference-saving.mdc
  * Créer une section Exemple dans chaque fichier
  * Ajouter des exemples d'utilisation avec [...] pour le contenu dynamique
  * Ajouter des phrases explicatives pour chaque étape
  * Positionner la section entre Next Rules et Start Rule
- Fichiers: context-update.mdc, user-preference-saving.mdc
- Dépendances: Aucune
- Validation: Les exemples sont clairs et suivent le format standard

1.3. [ ] **Ajouter l'exemple de correction** : Créer la section Exemple pour fix.mdc
- Actions:
  * Lire le fichier fix.mdc
  * Créer une section Exemple
  * Ajouter un exemple d'utilisation avec [...] pour le contenu dynamique
  * Ajouter des phrases explicatives pour chaque étape
  * Positionner la section entre Next Rules et Start Rule
- Fichiers: fix.mdc
- Dépendances: Aucune
- Validation: L'exemple est clair et suit le format standard

## 2. Validation
2.1. [ ] **Vérifier la cohérence** : S'assurer que tous les exemples suivent le même format
- Actions:
  * Vérifier chaque fichier de règle
  * Confirmer l'utilisation de [...] pour le contenu dynamique
  * Vérifier la position des sections Exemple
  * Vérifier la présence des phrases explicatives
- Fichiers: Tous les fichiers .mdc
- Dépendances: Toutes les tâches de développement
- Validation: Tous les exemples sont cohérents et suivent le même format

2.2. [ ] **Tester les exemples** : Vérifier que les exemples sont clairs et utiles
- Actions:
  * Lire chaque exemple du point de vue d'un nouvel utilisateur
  * Vérifier que les exemples aident à comprendre l'utilisation
  * Vérifier que les phrases explicatives sont claires
  * Identifier les points d'amélioration potentiels
- Fichiers: Tous les fichiers .mdc
- Dépendances: Toutes les tâches de développement
- Validation: Les exemples sont compréhensibles et utiles

# Done

## 1. Préparation des exemples
1.1. [x] **Analyser l'exemple fourni** : Comprendre la structure et le format de l'exemple donné
1.2. [x] **Définir le format standard** : Établir un format cohérent pour tous les exemples

## 2. Ajout des exemples - Règles de base
2.1. [x] **Ajouter l'exemple dans system.mdc** : Ajouter un exemple d'utilisation de la règle system
2.2. [x] **Ajouter l'exemple dans context-loading.mdc** : Ajouter un exemple d'utilisation de la règle context-loading

## 3. Ajout des exemples - Règles d'analyse
3.1. [x] **Ajouter l'exemple dans request-analysis.mdc** : Ajouter un exemple d'utilisation de la règle request-analysis
3.2. [x] **Ajouter l'exemple dans task-decomposition.mdc** : Ajouter un exemple d'utilisation de la règle task-decomposition

## 4. Standardisation des exemples
4.1. [x] **Standardiser les exemples existants** : Remplacer tout contenu dynamique par [...] dans system.mdc, context-loading.mdc et request-analysis.mdc
4.2. [x] **Ajouter les phrases explicatives** : Ajouter des phrases que devrait dire le modèle à chaque étape dans les exemples
4.3. [x] **Repositionner les sections Exemple** : Déplacer la section Exemple entre Next Rules et Start Rule dans toutes les règles
4.4. [x] **Vérifier les modifications** : Utiliser la commande cat pour s'assurer que les changements sont bien appliqués

## 5. Standardisation des règles
5.1. [x] **Modifier task-decomposition.mdc** : Adapter la règle pour avoir des sections de plus haut niveau avec des tâches plus détaillées
5.2. [x] **Vérifier les modifications** : Utiliser la commande cat pour s'assurer que les changements sont bien appliqués 