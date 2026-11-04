---
description: "Règle d'or Fail-Fast d'Henri Jamet, DRY radical, zéro hardcoding, interdiction des tests unitaires au profit des tests manuels en conditions réelles et traitement de la cause racine."
trigger: always_on
---

# 🛠️ Bonnes Pratiques de Développement & Règle d'Or Fail-Fast (MANDATOIRE)

Tout agent écrivant ou modifiant du code (scripts, React, FastAPI, MCP, pipelines) DOIT respecter ces invariants avant d'écrire la moindre ligne :

| Principe | Invariant Technique & Interdits |
|---|---|
| **1. Règle d'Or Fail-Fast** (*« Un programme qui ne crashe pas en cas d'erreur n'est pas un programme robuste, c'est un programme menteur. »* — Henri Jamet) | Lorsqu'une précondition échoue, le programme DOIT crasher immédiatement avec une stacktrace explicite. **Interdiction formelle de tout `try...except Exception: pass` ou repli silencieux** retournant une valeur factice par défaut. |
| **2. Interdiction absolue des tests unitaires (`pytest`, `unittest`, `jest`, `vitest`) — Tests manuels humains exclusivement par l'Auditeur (`inherit`)** | **Il est strictement interdit d'écrire, de maintenir ou d'exécuter des suites de tests unitaires (`pytest`, dossiers `tests/` ou `src/tests/`, mocks)**, qui prennent un temps fou sans tester la réalité (*ex. réel 02/11/2026, AIVC : 30 runs `pytest` de 81 s ayant fait perdre > 1h*). Supprimer les tests unitaires existants s'ils ralentissent un dépôt personnel. **C'est à l'auditeur (`auditeur-alignement`, toujours en `Model: 'inherit'`), et NON à l'exécutant (l'ouvrier, en `flash`), de tester manuellement les modifications faites (si testables)** : vraiment comme le ferait un humain, sommairement mais en allant droit au but, en vérifiant le bon fonctionnement des fonctionnalités **via leur canal d'utilisation prévu** (navigateur via MCP Playwright pour une UI, vraie commande CLI utilisateur, vrai appel d'outil MCP), **sans aucune triche, sans aucun mock et sans aucun raccourci**. |
| **3. DRY Radical & Simplicité d'Ockham (`autoresearch`)** | Appliquer le *Simplicity criterion* ([zero-trust.md](file:///c:/Users/Jamet/Documents/VoiceNotes/_agents/rules/zero-trust.md)) : privilégier la suppression de code et rejeter toute complexité sans gain net massif. Ne jamais coder deux fois la même chose : chercher et factoriser l'existant. |
| **4. Zéro Donnée Factice en Dur** | Jamais de valeurs d'exemples, dates fictives ou textes arbitraires codés en dur dans le code ou le JSX. 100 % des données proviennent dynamiquement de la BDD, de l'état réel ou des APIs (avec état vide propre `[]` si aucune donnée n'existe). |
| **5. Cause Racine vs Rustines** | Toujours réparer la cause fondamentale : pointer vers le bon `.venv` (jamais de `try/except ImportError` mocké) ; valider les types/schémas en amont (jamais de `None` avalé) ; résoudre les chemins absolus canoniques (jamais ignorer `FileNotFoundError`). |
| **6. Branche Principale (`main`) par Défaut** | Travailler et pousser directement sur `main` (`main = prod`), en parallèle sur des chantiers disjoints avec `git -c core.editor=true pull --rebase` avant push (exceptions : branches éphémères immédiatement fusionnées, ou sessions autonomes `/advance`). |
