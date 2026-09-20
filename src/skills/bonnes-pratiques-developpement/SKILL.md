---
name: bonnes-pratiques-developpement
description: "Bonnes pratiques de développement et règle d'or Fail-Fast d'Henri Jamet : interdiction absolue des try/except silencieux, crash immédiat en contexte expérimental, et traitement systématique de la cause racine."
---

# 🛠️ Quelles Sont les Bonnes Pratiques de Développement & la Règle d'Or Fail-Fast d'Henri ?

> [!IMPORTANT]
> **OBLIGATION DE LECTURE PRÉALABLE** :
> Tout agent (principal ou sous-agent) recevant une consigne d'écriture ou de modification de code (scripts, outils MCP, pipelines, modules, fonctions utilitaires) **DOIT impérativement lire ce fichier en amont via `view_file`** avant d'écrire la moindre ligne de code.

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

## 🔬 Pourquoi le Masquage d'Erreur Est-il Catastrophique en Recherche Scientifique ?

En science, en apprentissage automatique et en expérimentation de recherche :
- **Validité des résultats** : Tout calcul faussé, masqué ou remplacé par une heuristique par défaut vicie l'ensemble de la chaîne de preuve et invalide les conclusions expérimentales.
- **Règle d'or de l'intégrité** : **Interdiction formelle d'avancer sur des calculs faussés ou masqués.**
- **Supériorité du crash** : Un crash immédiat avec stacktrace explicite est **infiniment supérieur** à une exécution silencieusement altérée qui produit des métriques ou des graphiques trompeurs.
- **Reproductibilité stricte** : Si un modèle, un poids de checkpoint, un tokenizer ou un composant GPU est indisponible, l'évaluation DOIT s'arrêter net plutôt que de substituer un substitut silencieux.

---

## 🎯 Comment Traiter Systématiquement la Cause Racine et Bannir les Rustines ?

L'agent DOIT toujours réparer le problème à sa source fondamentale, et JAMAIS enrober le symptôme :

| Cause Racine | Action Obligatoire (Fix Réel) | Rustine / Pansement Formellement Proscrit |
|---|---|---|
| **Environnement Python** | Sélectionner et pointer vers l'interpréteur venv canonique du projet contenant les packages requis. | Ajouter un try/except `ImportError` renvoyant un mock ou une fonction vide. |
| **Typage & Schéma** | Valider et corriger les types en amont (dataclasses, Pydantic, signatures typées). | Utiliser des conversions implicites ou des valeurs `None` avalées en silence. |
| **Chemins de fichiers** | Résoudre les chemins absolus canoniques et vérifier l'existence via des assertions strictes. | Utiliser un chemin relatif hasardeux puis ignorer l'erreur `FileNotFoundError`. |
| **Dépendances manquantes** | Documenter et installer les dépendances exactes dans le venv approprié. | Dégrader silencieusement le service en renvoyant une réponse partielle factice. |
| **Données en entrée invalides** | Lever une `ValueError` ou une `KeyError` descriptive dès la frontière d'entrée. | Remplacer les champs manquants par des valeurs inventées ou plausibles. |

---

## 🚫 Quels Sont les Anti-Patterns Formellement Proscrits (Bannissement Absolu) ?

1. **Bannissement Absolu des `try...except Exception: pass`** :
   - Tout bloc `except: pass` ou `except Exception: return default_value` sans réémission explicite de l'exception ou sans gestion circonstanciée et justifiée est une falsification.
2. **Interdiction des Fallbacks Cosmétiques Factices** :
   - BANNISSEMENT ABSOLU des fallbacks renvoyant des valeurs plausibles par défaut (ex: scores factices à 5.0%, confiances simulées, mocks invisibles).
   - Si une fonction ne peut pas produire son résultat nominalement, elle **DOIT échouer bruyamment**.
3. **Interdiction de l'Imitation Manuelle d'Outils Machine** :
   - Ne jamais simuler par du texte ou des valeurs codées en dur ce qui doit être calculé par un modèle ou un script (`ai_detector.py`, `doc-version`, compilation LaTeX).

---

## 📋 Quelle Est la Checklist de Validation de Code pour les Agents ?

Avant de finaliser toute modification ou écriture de code :
- [ ] Le code lève-t-il une exception explicite dès qu'une précondition obligatoire échoue ?
- [ ] Y a-t-il zéro bloc `try/except` silencieux ou masquant une erreur inattendue ?
- [ ] Y a-t-il zéro valeur factice de remplacement ou score par défaut cosmétique ?
- [ ] La cause racine (environnement venv, dépendances, typage, chemins absolus) a-t-elle été résolue ?
- [ ] Le programme échoue-t-il bruyamment avec un message clair et actionnable en cas d'anomalie ?
