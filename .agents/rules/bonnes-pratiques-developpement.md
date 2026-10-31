---
description: "Règle d'or Fail-Fast d'Henri Jamet, DRY radical, zéro hardcoding, primauté des tests ciblés/Playwright et traitement systématique de la cause racine."
trigger: glob
globs: "**/*.{py,sh,bash,ps1,js,jsx,ts,tsx,go,rs,c,cpp,h,hpp,html,css}"
---

# 🛠️ Quelles Sont les Bonnes Pratiques de Développement & la Règle d'Or Fail-Fast d'Henri ?

> [!IMPORTANT]
> **OBLIGATION DE CONFORMITÉ PRÉALABLE** :
> Tout agent (principal ou sous-agent) recevant une consigne d'écriture ou de modification de code (scripts, composants React, backend FastAPI, outils MCP, pipelines) **DOIT impérativement se conformer à cette règle** avant d'écrire la moindre ligne de code.

---

## ⚡ Pourquoi la Règle d'Or du Fail-Fast Est-elle Inviolable ?

> **« Un programme qui ne crashe pas en cas d'erreur n'est pas un programme robuste, c'est un programme menteur. »**  
> — *Henri Jamet*

| Principe | Réalité Technique & Invariant d'Exécution |
|---|---|
| **Vérité brute vs Illusion** | Cacher une exception sous le tapis ne résout rien : cela transforme un bug visible et traçable en corruption silencieuse de données ou en dérive indétectable. |
| **Crash immédiat & Stacktrace** | Lorsqu'une précondition n'est pas remplie ou qu'un calcul échoue, le programme DOIT crasher immédiatement avec une stacktrace explicite et un message d'erreur clair. |
| **Zéro tolérance au mensonge** | Mieux vaut une interruption nette à la milliseconde zéro qu'un pipeline qui tourne pendant des heures sur des valeurs corrompues ou par défaut. |

---

## 🧪 Pourquoi Faut-il Bannir les Suites de Tests Unitaires Lourdes au Profit de Tests Ciblés et Temporaires ?

> [!CAUTION]
> **INTERDICTION DE S'EMBOURBER DANS DES SUITES UNITAIRES COMPLEXES :**
> - **Zéro usine à gaz de tests unitaires** : Ne JAMAIS perdre de temps à concevoir, maintenir ou empiler des suites de tests unitaires rigides et lourdes (`pytest`, mocks artificiels, suites de tests par dizaines) qui ralentissent le flux de livraison et créent de la friction sans apporter de réelle valeur.
> - **Primauté des tests manuels et temporaires** :
>   1. **Recette Visuelle & Navigateur en Direct** : Privilégier systématiquement les tests manuels via le **MCP Playwright** (`browser_navigate`, `browser_click`, `browser_snapshot`, `browser_take_screenshot`) sur le site ou l'interface réelle.
>   2. **Scripts Jetables de Session** : Pour valider un comportement ou un endpoint, utiliser des scripts jetables et ciblés logés exclusivement dans le dossier temporaire `<appDataDir>\brain\<conversation-id>\scratch\`.
>   3. **Validation de Build & Typage** : Une exécution propre de `npm run build` (0 erreur Vite) et un sondage HTTP direct suffisent amplement à valider les modifications frontend.

---

## 🧩 Comment Appliquer le DRY Radical et la Factorisation ?

> [!IMPORTANT]
> **INTERDICTION ABSOLUE DE DUPLIQUER DU CODE (DRY) :**
> - Appliquer systématiquement le **Critère de Simplicité d'Ockham (`autoresearch`)** défini dans [zero-trust.md](file:///c:/Users/hjamet/Documents/VoiceNotes/_agents/rules/zero-trust.md) : privilégier la suppression de code et rejeter toute complexité (`if/else`, abstractions, hyperparamètres) sans gain net massif.
> - **Ne JAMAIS coder deux fois la même chose** : dès qu'une interface, une carte, un formulaire ou une mécanique s'approche d'un élément existant, extraire un composant ou utilitaire partagé paramétré par props/arguments.
> - Avant d'écrire un nouveau composant ou fonction, rechercher dans le codebase si un existant ne remplit pas déjà 80 % du besoin pour l'adapter plutôt que de le réinventer.

---

## 🌐 Pourquoi Interdire Absolument les Valeurs d'Exemples Hardcodées ?

- **Zéro Donnée Factice en Dur** : Ne JAMAIS hardcoder de valeurs d'exemples, de fausses données de démonstration ou de textes arbitraires (ex: pseudos statuts, dates fictives, "2 personnes", budgets inventés) directement dans le code source ou les composants JSX.
- **Dynamisme Intégral Exclusif** : 100% des données affichées doivent être dérivées dynamiquement de la base de données, de l'état utilisateur réel (`currentUser`), des APIs ou de la télémétrie matérielle.
- **Repli Gracieux Neutre** : Si aucune donnée n'existe en base pour un utilisateur ou un champ, l'application doit afficher un état vide propre ou un libellé neutre (`[]`, masquage élégant), sans jamais combler le vide par des données fictives codées en dur.

---

## 🎯 Comment Traiter Systématiquement la Cause Racine et Bannir les Rustines ?

L'agent DOIT toujours réparer le problème à sa source fondamentale, et JAMAIS enrober le symptôme :

| Cause Racine | Action Obligatoire (Fix Réel) | Rustine / Pansement Formellement Proscrit |
|---|---|---|
| **Environnement & Venv** | Sélectionner et pointer vers l'interpréteur venv canonique du projet contenant les packages requis. | Ajouter un try/except `ImportError` renvoyant un mock ou une fonction vide. |
| **Typage & Schéma** | Valider et corriger les types en amont (dataclasses, Pydantic, signatures typées). | Utiliser des conversions implicites ou des valeurs `None` avalées en silence. |
| **Chemins de fichiers** | Résoudre les chemins absolus canoniques et vérifier l'existence via des assertions strictes. | Utiliser un chemin relatif hasardeux puis ignorer l'erreur `FileNotFoundError`. |
| **Duplication de Code** | Factoriser immédiatement le composant ou la fonction utilitaire partagée. | Copier-coller le composant en changeant 2 lignes de style dans une autre page. |
| **Données Manquantes** | Rendre l'affichage conditionnel ou afficher un état vide élégant. | Insérer des fausses valeurs en dur dans le JSX. |

---

## 🌿 Pourquoi Travailler Directement sur la Branche Principale et Éviter la Prolifération de Branches ?

- **Branche Principale par Défaut** : Coder directement sur la branche principale (`main`) pour éliminer les fusions hasardeuses, les branches orphelines et le code oublié.
- **Exceptions Rares & Éphémères** : Création de branche tolérée uniquement pour des exceptions courtes et justifiées ; fusion et suppression immédiates dès le chantier achevé.
- **Interdiction de Déploiement Hors Main** : Interdiction formelle de déployer en production depuis une branche non fusionnée (`main = prod`).
- **Parallélisme Multi-Agents** : Les sous-agents travaillent en parallèle sur la même branche sur des chantiers disjoints, avec commits courts sur chemins explicites et `git pull --rebase` avant push (détails opérationnels : [sous-agents.md](file:///c:/Users/hjamet/Documents/VoiceNotes/_agents/rules/sous-agents.md)).

---

## 🚫 Quels Sont les Anti-Patterns Formellement Proscrits ?

1. **`try...except Exception: pass` ou repli silencieux** : tout bloc avalant une erreur ou retournant une valeur factice par défaut (ex. score à 5.0 %) sans réémission explicite est une falsification.
2. **Imitation manuelle d'outils machine** : cf. [zero-trust.md](file:///c:/Users/hjamet/Documents/VoiceNotes/_agents/rules/zero-trust.md).
