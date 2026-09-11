---
name: refine
description: "Outil d'analyse ponctuelle et optionnelle pour la critique stratégique d'un plan d'implémentation (implementation_plan.md). Ne fait pas partie du flux standard Scout-Build."
---

# 💎 Comment l'Outil Optionnel Refine Analyse-t-il et Challenge-t-il un Plan d'Implémentation ?

> [!NOTE]
> **OUTIL D'ANALYSE PONCTUELLE ET OPTIONNELLE** :
> Ce skill ne fait **plus partie du flux nominal standard Scout-Build**. Il est réservé à une invocation manuelle et ciblée (`/refine [N]`) lorsqu'Henri souhaite expressément soumettre un plan d'implémentation existant (`implementation_plan.md`) à une contre-expertise critique indépendante ou un stress-test approfondi avant exécution.

**Objectif** : Examiner un plan d'implémentation existant (`implementation_plan.md`), le confronter rigoureusement à la réalité du code source, traquer les failles architecturales, les angles morts et les risques d'erreurs silencieuses, et proposer des enrichissements ciblés.

> **🧠 POSTURE CRITIQUE INDÉPENDANTE.** Ton rôle est de penser par toi-même, de remettre en question les hypothèses et de vérifier systématiquement les affirmations en inspectant le code source réel.
> **🔬 VÉRIFICATION FACTUELLE DU CODE.** Tu ne te contentes pas de lire le plan : tu ouvres les fichiers, tu contrôles les signatures réelles et tu vérifies la faisabilité concrète.
> **🚫 AUCUNE MODIFICATION DE CODE.** Tu produis uniquement une révision critique du plan.
> **🚫 EXCLUSION DES TESTS AUTOMATISÉS LOURDS.** Ne prévois pas de suites de tests unitaires complexes ; privilégie les vérifications manuelles temporaires et les tests en direct.

---

## 1. 📖 Analyse du Plan & Modes d'Exécution

1. **Lecture du Plan** : Lis attentivement l'artéfact `implementation_plan.md`.
2. **Mode Multi-Agents Optionnel (`/refine N`)** :
   - Si un suffixe `N` ($N \le 5$) est spécifié, instancier $N$ sous-agents `self` pour mener une revue critique redondante en parallèle.
   - Chaque sous-agent mène l'analyse complète avec des variations d'angles d'attaque.
   - L'agent principal consolide les remarques les plus pertinentes.

---

## 2. 🔬 Grille de Vérification Critique sur le Code Réel

Pour chaque point structurant du plan :
1. **Cause Racine vs Symptôme** : Le plan s'attaque-t-il à la véritable source du besoin ou à une manifestation superficielle ?
2. **Faisabilité & Patterns** : Les propositions s'intègrent-elles harmonieusement dans les patterns réels du codebase ?
3. **Traque des Erreurs Silencieuses** :
   - Risques de fallbacks masqués ou de retours par défaut trompeurs.
   - Blocs de capture d'erreurs vides ou insuffisamment typés.
   - Absence de logging aux points critiques.

---

## 3. ✍️ Livrable : Mise à Jour Annotée d'`implementation_plan.md`

Refine met à jour l'artéfact `implementation_plan.md` en intégrant ses annotations critiques :

```markdown
> [!TIP]
> **✅ VALIDÉ** — Étape robuste et cohérente avec le code existant.

> [!WARNING]
> **⚠️ ATTENTION** — [Description du risque identifié et proposition corrective]

> [!CAUTION]
> **🛑 ANOMALIE** — [Faille ou contradiction avec le code source nécessitant un ajustement]
```

---

## 4. 🛑 Arrêt

1. Présente un résumé clair et factuel de la revue critique à Henri dans le chat.
2. **ARRÊTE-TOI.** Ne lance aucun workflow ultérieur. L'arbitrage final et la décision de passage à l'implémentation appartiennent exclusivement à Henri.

> [!CAUTION]
> **🚫 RÈGLE : AUCUN ENCHAÎNEMENT AUTOMATIQUE (No Auto-Chaining).**
> Ne jamais déclencher automatiquement d'étape ultérieure.
