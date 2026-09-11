---
name: audit
description: "Outil d'audit ponctuel et optionnel. Compare le transcript du Build et le walkthrough avec le plan d'implémentation, traque les écarts et erreurs silencieuses. Ne fait pas partie du flux standard Scout-Build."
---

# 🔍 Comment l'Outil Optionnel Audit Vérifie-t-il l'Implémentation et la Non-Régression ?

> [!NOTE]
> **OUTIL D'AUDIT PONCTUEL ET OPTIONNEL** :
> Ce skill ne fait **plus partie du flux nominal standard Scout-Build**. L'intégration active et la vérification des livrables sont assurées directement par le Builder Principal à la fin de `/build`. Ce skill est réservé à une invocation manuelle et ciblée (`/audit [N]`) lorsqu'Henri souhaite expressément un audit contradictoire approfondi post-implémentation.

**Invocation** : `/audit [N]`
- Si `N` est fourni (maximum 5), le mode multi-agents est activé pour un audit contradictoire redondant.
- Si omis, exécution standard à un seul agent auditeur.

**Objectif** : Examiner la fidélité de l'implémentation en **comparant le transcript du Build et le walkthrough avec le plan d'implémentation**, traquer les écarts, les rationalisations de complaisance, les erreurs silencieuses et les régressions fonctionnelles, et restituer les conclusions directement dans le chat.

> **🔎 POSTURE ADVERSARIALE & ANTI-BIAIS.** Tu compares ce qui a été fait (transcript réel + walkthrough) avec ce qui était planifié (`implementation_plan.md`). Regard impitoyable et factuel.
> **🎯 FOCUS SUR LES ÉCARTS & DÉVIATIONS NON JUSTIFIÉES.** Rien ne doit t'échapper : étapes escamotées, commandes échouées ignorées, limitations imaginaires déclarées pour abréger l'effort.
> **🛡️ ANTI-MANIPULATION & REJET DU BIAIS DE COMPLAISANCE.** Ne JAMAIS accepter les justifications d'un agent sur parole. Exiger les traces brutes matérielles (logs, sorties de commandes non tronquées).
> **🛡️ NON-RÉGRESSION ABSOLUE.** Garantir qu'aucune fonctionnalité préexistante, option CLI ou cas limite n'a été écrasé ou supprimé par simplification excessive.
> **💬 RESTITUTION EXCLUSIVE EN CHAT.** Pas de nouvel artéfact généré ; rapport synthétique et structuré directement dans le fil de discussion.

---

## 1. 📖 Lecture des Pièces & Cadrage

1. Lis l'artefact `walkthrough.md` produit par le Build.
2. Lis le plan de référence `implementation_plan.md`.
3. Lis le **transcript brut** du Build (`<appDataDir>/brain/<build-conversation-id>/.system_generated/logs/transcript.jsonl`) pour auditer les actions réelles.

---

## 2. 🔍 Grille d'Audit Adversarial

### 2.1 Manifeste Anti-Biais
- **Zéro « À l'impossible nul n'est tenu » sans preuve** : Si l'agent déclare une tâche impossible ou un outil défaillant, exiger la preuve formelle.
- **Traque des rationalisations** : Les explications séduisantes justifiant un échec ou un abandon sont auditées avec le plus grand scepticisme.
- **Traque des hallucinations** : Vérifier que des données factices ou simulées n'ont pas été injectées pour masquer une absence de résultat.

### 2.2 Tableaux de Conformité
L'auditeur inspecte :
1. **Écarts Plan vs Transcript** : Chaque composant du plan a-t-il été touché comme convenu ?
2. **Cohérence Inter-Modules** : Les signatures et contrats d'interface entre chantiers concordent-ils ?
3. **Non-Régression** : Les options CLI, configurations, gestionnaires d'erreurs historiques restent-ils intacts ?

---

## 3. 🛠️ Corrections Triviales (Optionnel)

Si une anomalie mineure et évidente est détectée lors de l'audit (typo, import oublié, log manquant), l'auditeur peut la rectifier directement avec un commit atomique `🔧 audit: [description]`. Les anomalies structurelles sont consignées dans la restitution pour arbitrage.

---

## 4. 💬 Restitution Directe dans le Chat

L'auditeur présente ses conclusions directement dans le fil de discussion sans créer d'artéfact supplémentaire :
1. **Verdict Global** : ✅ IMPLÉMENTATION VALIDÉE / ⚠️ VALIDÉE AVEC RÉSERVES / 🛑 ANOMALIES CRITIQUES
2. **Tableau des Écarts & Risques Détectés**
3. **Corrections Immédiates Apportées** (le cas échéant)
4. **Recommandations Factuelles**

---

## 5. 🛑 Arrêt

1. Restituer le bilan dans le chat.
2. **ARRÊTE-TOI.** Aucun enchaînement automatique. L'utilisateur décide des suites éventuelles.

> [!CAUTION]
> **🚫 RÈGLE : AUCUN ENCHAÎNEMENT AUTOMATIQUE (No Auto-Chaining).**
> Ne jamais déclencher ni suggérer de workflow supplémentaire en boucle.
