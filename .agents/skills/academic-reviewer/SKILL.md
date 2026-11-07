---
name: academic-reviewer
description: "[DEPRECIE / ALIAS VERS /reviewer] Ce skill a ete fusionne dans le skill unifie reviewer. Invoquer /reviewer pour toute relecture de papier de recherche ou audit logiciel."
---

# ⚠️ Pourquoi ce Skill est-il Déprécié au Profit de `/reviewer` ?

> [!IMPORTANT]
> **FUSION COMPLÈTE EFFECTUÉE DANS `/reviewer` :**
> Le skill `academic-reviewer` a été fusionné de manière unifiée au sein du méta-skill canonique [`/reviewer`](file:///C:/Users/Jamet/Documents/VoiceNotes/agents/skills/reviewer/SKILL.md).
> Pour toute évaluation de manuscrit scientifique, relecture par les pairs (AAAI, EAAI, Nature, NeurIPS), audit de claims ou contrôle couplé papier $\leftrightarrow$ code, **invoquer directement `/reviewer`**.

---

## 🔄 Comment Basculer vers le Nouveau Système Unifié ?

Le moteur unifié [`/reviewer`](file:///C:/Users/Jamet/Documents/VoiceNotes/agents/skills/reviewer/SKILL.md) intègre l'intégralité des directives historiques d'évaluation académique sous trois modes complémentaires :

1. **Mode 1 : Code & Live Execution Auditor** : Supervision d'exécutions logicielles, traque d'anomalies de logs et de crashs.
2. **Mode 2 : Academic Peer Reviewer** : Évaluation médico-légale de manuscrits scientifiques LaTeX, posture impitoyable de Reviewer 2, respect des Directives Vitales (zéro critique d'état incomplet, traitement des métriques comme données empiriques), 4 dimensions d'analyse et notation /10.
3. **Mode 3 : Full-Stack Scientific Audit** : Contrôle croisé et couplé certifiant la conformité exacte entre le texte du papier LaTeX et les simulations/code réels (`src/`, logs bruts, audit `main.log` et pagination).

---

## 🚀 Comment Invoquer le Reviewer Académique Désormais ?

L'invocation s'effectue directement via :
- **Slash command / Prompt standard** : `/reviewer` en précisant le contexte du papier (ex: *"Effectue une relecture académique Mode 2 du manuscrit paper/main.tex"* ou *"Lance un audit couplé Mode 3 entre paper/ et src/"*).
- **Agent autonome dédié (Gemini Pro)** :
  ```bash
  antigravity-agents run --model pro --prompt "Agis en tant que reviewer (Mode 2) pour évaluer le manuscrit..." --workspace-dir "<workspace_path>"
  ```
