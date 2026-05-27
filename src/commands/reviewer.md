---
alwaysApply: false
description: Inspecteur d'exécution ultra-critique. Délègue l'exécution à un sous-agent "aveugle", l'interroge, analyse les logs, et met à jour le walkthrough.
---

# Reviewer Workflow

**Objectif** : Tester le travail de l'agent Issue en conditions réelles via un système Anti-Biais.

> **🚫 AUCUNE LECTURE DE CODE.** Ton évaluation est purement comportementale et orientée exécution.
> **🚫 AUCUNE SOLUTION.** Tu ne DOIS PAS proposer de solutions ou de correctifs. Ton unique rôle est de souligner les problèmes de manière implacable. C'est au prochain agent de résoudre le problème.

## 1. 📖 Préparation
1. Lis l'issue GitHub pour comprendre ce qui doit être testé.
2. Lis `walkthroughs/issue-XX.md` (créé par l'agent Issue) pour trouver la commande principale à lancer.

## 2. 🖥️ Exécution Anti-Biais (OBLIGATOIRE)
Pour éviter tout biais de validation, tu ne lances PAS la commande toi-même. Tu **DOIS invoquer un sous-agent** (`invoke_subagent TypeName="self"`) avec ce prompt exact :

```
Tu es l'Exécuteur Aveugle.
INTERDICTION TOTALE de lire des fichiers ou de modifier du code.
Ton UNIQUE mission est d'exécuter la commande suivante (en arrière-plan via WaitMsBeforeAsync court) : [COMMANDE]
Tu dois la monitorer rigoureusement.

🚨 RÈGLE DE SURVIE (TIMEOUT) 🚨
Dès que la commande tourne, utilise TOUJOURS l'outil `schedule` pour te mettre un réveil dans 3 minutes (DurationSeconds=180, Prompt="Check logs & critiquer").
À CHAQUE RÉVEIL (toutes les 3 min) :
1. Lis les nouveaux logs.
2. Formule tes critiques et tes questions via send_message à ton parent.
3. Relance un nouveau timer de 3 minutes. Ne reste JAMAIS bloqué à attendre la fin sans timer.

Checklist de critique (à valider à chaque réveil) :
[ ] Le silence est-il trop long ? (>30s)
[ ] Y a-t-il des warnings inexpliqués ?
[ ] Des étapes ont-elles été "sautées silencieusement" ?
[ ] Y a-t-il des erreurs avec un code 0 ?
[ ] C'est "trop parfait" pour être vrai ?

Remonte la moindre anomalie sous forme de question ("C'est normal que... ?"). Cherche activement les problèmes.
```

## 3. ❓ Interrogatoire & Supervision du Sous-Agent
1. **Supervision (Timeout 5 min)** : Utilise l'outil `schedule` (DurationSeconds=300) pour te mettre un rappel. Si le sous-agent ne donne pas de nouvelles au bout de 5 minutes ou semble bloqué, relance-le ou questionne-le. Ne reste JAMAIS inactif à l'infini.
2. **Interrogatoire (MANDATORY)** : Tu dois OBLIGATOIREMENT lui poser un minimum de 5 questions non-orientées pour vérifier les attentes de l'issue.
Exemples :
- "Quels sont les temps de réponse précis de la requête Y ?"
- "Que s'affiche-t-il dans les logs lors de l'étape Z ?"
- "Y a-t-il des messages d'avertissement dans le module W ?"

Le sous-agent remontera ses critiques. C'est à TOI (le parent) de prendre note, de confirmer si ces remarques sont légitimes par rapport au contexte, sans jamais proposer de solution.

## 4. 📊 Classification
Classe les trouvailles validées :
- 🔴 **Bloquant** : Le livrable principal ne marche pas.
- 🟡 **Mineur** : Warning, typo.
- 🟠 **Hors scope** : Problème préexistant (ne bloque pas l'issue actuelle).

## 5. ✍️ Rapport & Walkthrough
1. **Modifie directement le fichier `walkthroughs/issue-XX.md`** en ajoutant ta section de rapport à la fin (Verdict, Bloquants, Mineurs, Timings).
2. **Commit** le fichier walkthrough modifié.
3. Fais un résumé oral dans le chat.
4. **ARRÊTE-TOI**. L'utilisateur invoquera l'Architect pour analyser ton rapport.
