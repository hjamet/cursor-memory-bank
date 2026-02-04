---
description: Générer un prompt de passation (Handover) narratif pour maintenir le contexte.
---

# Workflow: Context Handover

Ce workflow sert à générer un **"Prompt de Passation"** à la fin d'une conversation. L'objectif est de transmettre l'histoire de la session de manière naturelle mais **extrêmement précise**, comme si tu faisais une passation de dossier critique à un collègue.

## Philosophie
*   **Narratif ET Structuré** : On veut l'histoire, mais aussi les faits durs.
*   **Contenu Inclus** : ⚠️ **INTERDICTION DE CITER DES ARTEFACTS**. Le prochain agent n'y a PAS accès. Tu dois RÉ-EXPLIQUER ici tout ce qui était dans tes plans ou notes. N'aie pas peur de faire long.
*   **User-Centric** : Ce sur quoi l'utilisateur a *insisté* est sacré.
*   **Pas de Plan d'Implémentation** : ⚠️ Tu donnes le but, le brainstorming et les contraintes, mais **JAMAIS le plan d'exécution**. C'est au prochain agent de construire son plan.

## Structure du Prompt
Le prompt doit être généré dans un bloc de code Markdown.

### 1. 👋 Relai : [Titre de l'Action]
Un titre accrocheur résumant la mission immédiate.

### 2. Le Contexte & La Discussion (Narratif Détaillé)
Raconte l'histoire de la session.
*   **Le "Pourquoi"** : Quel était le problème initial ?
*   **Le "Comment"** : Quelles pistes avons-nous explorées ? (Explique les idées, ne dis pas "voir plan").
*   **Les Fichiers** : Cite les fichiers clés modifiés (ex: `server.py`).

### 3. Décisions Actées & Brainstorming
Liste clairement (tu as le droit aux listes ici pour la clarté) :
*   **Décisions Techniques** : "On a décidé d'utiliser X plutôt que Y car..."
*   **Insistance de l'Utilisateur** : "L'utilisateur a REFUSÉ qu'on touche à..." ou "Il veut ABSOLUMENT que..." (C'est crucial).
*   **Points identifiés** : Détails techniques importants trouvés pendant l'analyse (IDs, noms de variables, conflits...).

### 4. La Mission & L'Ordre de Marche
**CRITIQUE : INSTRUCTION OBLIGATOIRE POUR LE PROCHAIN AGENT**
Tu DOIS inclure cette phrase (ou équivalent) en gras :
> **⚠️ ATTENTION : Ne pars PAS directement dans le code. Commence par établir un PLAN d'implémentation clair et soumets-le à l'utilisateur. Discute des détails ambigus AVANT de toucher à quoi que ce soit.**

Donne ensuite le cap général de la mission (le "Quoi", pas le "Comment faire").

## Exemple de Sortie
```markdown
# 👋 Relai : Stabilisation des Logs & Refonte Config

### Contexte & Discussion
On est partis d'un problème de logs muets. On a découvert que `logging_config.py` était ignoré par `main.py`. J'ai commencé le fix, mais on est tombés sur un conflit de versions des libs. J'avais noté dans mon plan que le module `urllib3` posait problème, il faudra vérifier ça spécifiquement car la version installée est la 1.26 et on a besoin de la 2.0.

### Décisions & Points d'Attention
*   **INSISTANCE USER** : Ne JAMAIS modifier `custom_logger.py` (c'est une lib partagée).
*   **Décision** : On passe toutes les configs par variables d'env plutôt que par fichier .ini.
*   **A Discuter** : L'utilisateur n'est pas sûr de vouloir garder `Loguru`, il faut lui en reparler avant de l'intégrer partout.

### Mission
Finaliser la migration vers les variables d'env pour les logs.
**⚠️ STOP ! Ne code pas tout de suite. Fais un plan pour valider la structure des variables d'env avec l'utilisateur et confirme pour Loguru.**
```
