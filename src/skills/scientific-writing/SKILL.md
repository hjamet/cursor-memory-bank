---
name: scientific-writing
description: Méthodologie complète pour la rédaction et la révision de papiers académiques. Inclut le style d'écriture scientifique (neutre, rigoureux, anti-IA) et l'utilisation systématique de sous-agents spécialisés (critique, recherche, rédaction).
---

# 📝 Comment Rédiger et Réviser des Papiers Scientifiques (Scientific Writing) ?

> [!IMPORTANT]
> **Règle absolue d'écriture académique :** 
> Le texte doit être extrêmement scientifique, neutre, rigoureux et précis. Tout langage promotionnel, adjectifs hyperboliques ou tournures typiques des IA sont formellement interdits.

---

## 1. 🤖 Comment les Sous-Agents Spécialisés se Répartissent-ils le Travail ?

Toute modification substantielle d'un papier académique doit mobiliser des sous-agents en parallèle. Trois rôles sont systématiques :

### 1.1 Quel est le Rôle du Sous-Agent Critique (*Paper Text Critic*) ?
- **Rôle** : Relire le texte actuel et identifier les faiblesses.
- **Focus** : Claims non étayés, langage "IA", gaps logiques, structure, comparaisons manquantes.
- **Output** : Rapport structuré par sévérité (🔴 critique → 🔵 mineur).
- **Quand** : Avant toute réécriture, pour disposer d'un diagnostic objectif.
- **Audit de Pagination & Contenu** : Recompiler systématiquement après tout `git pull` ou modification sur un document LaTeX (`pdflatex` / `latexmk`) avant d'auditer la pagination ou le contenu. Interdiction formelle d'auditer un `.pdf` préexistant sans compilation fraîche.

### 1.2 Quel est le Rôle du Sous-Agent Recherche (*Citation Researcher*) ?
- **Rôle** : Chercher des références pertinentes via MCP Consensus ou web search.
- **Focus** : Papiers de la conférence cible, travaux récents sur le sujet, citations manquantes.
- **Output** : Entrées BibTeX complètes + suggestion d'insertion subtile.
- **Quand** : En parallèle de la critique, pour alimenter la réécriture.

### 1.3 Quel est le Rôle du Sous-Agent Rédaction (*Paper Writer*) ?
- **Rôle** : Rédiger un passage spécifique selon le style défini ci-dessous (pour les textes longs).
- **Focus** : Section Results, Discussion, Related Work.
- **Output** : Texte LaTeX prêt à insérer.
- **Quand** : Pour les passages longs nécessitant un premier jet itératif.

> [!NOTE]
> Les sous-agents travaillent en parallèle. L'agent principal intègre leurs résultats et assure la cohérence globale du papier.

---

### 1.4 Comment la Boucle Granulaire `--commit` / `--diff` Orchestre-t-elle les Révisions ?

Toute révision de manuscrit s'appuie sur la note miroir Obsidian (`papers/<nom>.md`) et le convertisseur automatique :
1. **Avant toute modification suite à un retour** : Appeler systématiquement le convertisseur avec `--commit` en précisant la ligne du commentaire utilisateur :
   ```bash
   python antigravity/scripts/latex_to_markdown_artifact.py --commit --line <N>
   ```
   Le script valide automatiquement toutes les diffs en amont de la ligne `<N>`, crée le commit Git et pousse vers le remote.
2. **Édition de fond** : Réaliser les ajustements demandés dans les fichiers LaTeX sources (`.tex`, `.bib`).
3. **Rafraîchissement miroir** : Rappeler le script en mode `--diff` pour projeter le delta rafraîchi dans la note miroir :
   ```bash
   python antigravity/scripts/latex_to_markdown_artifact.py --diff
   ```
4. **Boucle Fermée Actor-Critic & Seuil Anti-IA P(IA) <= 10% (MANDATOIRE)** :
   Après chaque appel à `python latex_to_markdown_artifact.py --diff` :
   Si le script retourne l'alerte `🚨 [ACTION AGENT REQUISE : REFORMULATION OBLIGATOIRE — SEUIL P(IA) > 10% NON RESPECTÉ]`, l'agent a l'obligation stricte d'itérer immédiatement : reformuler les paragraphes incriminés dans le .tex et réexécuter `--diff`, jusqu'à l'obtention du feu vert `✅ [CERTIFICATION IA CONFORME] 100% des paragraphes modifiés respectent le seuil strict P(IA) <= 10.0%`.
   L'agent NE DOIT JAMAIS s'arrêter ni déclarer sa tâche terminée tant que le script signale un paragraphe > 10.0%.

---

## 2. ✒️ Quels sont les Invariants du Style d'Écriture Scientifique ?

### Quel Ton & Registre Adopter ?
- **Extrêmement scientifique, neutre, rigoureux, précis.**
- Faire comprendre de manière subtile l'intérêt et la qualité du travail sans l'affirmer de manière explicite ou pompeuse.
- Jamais d'adjectifs hyper-mélioratifs : rester strictement objectif.
- Écrire de manière humaine : varier la longueur des phrases et le vocabulaire employé.

### Quelle Structure & Mise en Page Privilégier ?
- Privilégier les **paragraphes clairs et denses**.
- Pas de formatting excessif : éviter les sous-titres superflus et les listes à puces sauf si absolument nécessaire.
- Varier la mise en page pour rendre la lecture fluide et agréable.
- Chaque phrase doit porter une information précise. Aucune phrase vide ou de remplissage.

### ❌ Quels sont les Anti-Patterns INTERDITS (Style IA) ?
- ❌ **Phrases vides non porteuses d'information** (ex: *"In this section, we discuss..."*)
- ❌ **Phrases de conclusion inutiles** (ex: *"In summary, we have shown that..."*)
- ❌ **Adjectifs superlatifs non justifiés** (ex: *"groundbreaking"*, *"revolutionary"*, *"powerful"*)
- ❌ **Formulations grandiloquentes** (ex: *"demonstrating the power of..."*)
- ❌ **Répétition de l'évidence** (ex: *"as mentioned earlier"*, *"as we have seen"*)
- ❌ **Hedging excessif** (ex: *"it is worth noting that"*, *"interestingly"*)
- ❌ **Listes numérotées comme substitut de prose** (ex: *"What we observe is the following: (1)... (2)..."*)

### ✅ Quels sont les Patterns RECOMMANDÉS ?
- ✅ **Attaque directe** : Commencer directement par l'observation ou le résultat.
- ✅ **Quantification** : Quantifier systématiquement les claims (pourcentages, p-values, intervalles de confiance).
- ✅ **Contextualisation** : Situer les résultats par rapport aux baselines de la littérature.
- ✅ **Connecteurs logiques variés** (*however*, *consistent with*, *in contrast*, *nevertheless*).
- ✅ **Rythme** : Alterner phrases courtes et phrases complexes.
- ✅ **Nuance** : Qualifier les résultats avec mesure plutôt que de manière catégorique.
- ✅ **Citations ciblées** : Intégrer les citations de la conférence cible de manière subtile et naturelle.

---

## 3. 📚 Comment Intégrer Subtilement les Citations de la Conférence Cible ?

Lors de la préparation ou de la révision d'un papier pour une conférence spécifique :
1. **Recherche ciblée** : Rechercher 2 à 3 papiers publiés récemment **dans cette conférence** qui sont thématiquement proches.
2. **Insertion naturelle** : Les intégrer dans le texte de manière **extrêmement subtile** (la citation doit s'insérer naturellement dans le flux argumentatif, jamais comme une mention forcée).
3. **Vérification rigoureuse** : Toujours vérifier les DOI, auteurs et venues via DBLP, Consensus ou le site officiel de l'éditeur.
