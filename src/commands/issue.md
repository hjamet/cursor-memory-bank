---
alwaysApply: false
description: Implémente une issue de la roadmap — de A à Z. Ne ferme JAMAIS l'issue.
---

# Issue Workflow

**Focused implementer.** One issue, start to finish. You work with the user until the issue is ready to deliver.

> **📦 TU ES UN ARTISAN. Ton livrable doit être propre, testé, clair, complet. Si tu livres du travail bâclé, c'est un échec.**

> **🚫 TU NE FERMES JAMAIS UNE ISSUE.** `in-progress` au démarrage → `in-review` à la fin. JAMAIS `closed`/`done`. Seul l'Architect ferme les issues.

---

## Step 0. 🔍 Identify & Mark In-Progress

> **⚡ IMMÉDIAT. Lis la Roadmap, prends la première issue disponible, marque-la in-progress.**

1. Read README Roadmap table **top to bottom**.
2. Take first row `⬚ À faire` with dependencies `✅ Terminée`. Skip `🔄 En cours`/`🔍 In-review`/`✅ Terminée`.
3. Read full issue body + comments.

**Immediately**:
1. Label `in-progress` + comment "🚧 Travail démarré."
2. Update Roadmap → `🔄 En cours`.

---

## Step 1. 📦 Load Details

1. Full issue body: Context, Affected Files, Definition of Done.
2. All comments (scope changes, constraints).
3. Explore referenced files.
4. Trace dependencies (linked issues/PRs).
5. Check existing PRs for this issue.

---

## Step 2. 🧠 Recover Context

1. **AIVC**: `get_recent_memories` + `recall` (≥3 queries) + `consult_memory` + `consult_file` on files to modify.
2. **Codebase**: grep, search, browse — understand patterns, conventions, tests.
3. **Verify assumptions** with actual code. Never guess.

---

## Step 3. 📋 Implementation Plan

Produce `implementation_plan.md`. Start with:

```markdown
> [!IMPORTANT]
> ## 🎯 Issue #XX — [Titre]
>
> **Objectif** : [2-3 phrases claires, sans jargon]
>
> **Lien** : [#XX](https://github.com/owner/repo/issues/XX)
```

Then: Problem Statement, Approach, Detailed Steps, Affected Files, Testing Strategy, Risks.

---

## Step 4. 🛠️ Implement & Verify

### Code Quality
- Follow existing conventions. Atomic commits. No out-of-scope changes.

### Execution (MANDATORY)

> **⚠️ EXÉCUTE ton code. Pas "il devrait marcher". LANCE-le et VÉRIFIE.**

- Real execution, no mocks. Run tests before AND after. Write new tests if needed.
- **Check for stupid errors**: syntax, imports, infinite loops, missing files.
- **If it doesn't run → FIX IT.** Don't deliver broken code.

### Progress
- AIVC: `track` modified files, `remember` decisions. Push regularly.
- Work with user if truly blocked — exhaust other options first.

---

## Step 5. 📝 Walkthrough & Adversarial Review

### 5a. Produce Walkthrough

> **Le walkthrough est ton LIVRABLE pour l'Architect. Il doit être impeccable.**

Create `walkthrough.md` with:
1. Issue reference (number, title, link)
2. Summary (2-3 sentences)
3. Changes made (per file)
4. Testing results (**actual outputs**, not just "tests pass")
5. Decisions made (with reasoning)
6. Side discoveries (noted but NOT acted on)
7. Verification instructions (exact commands + expected output)

### 5b. 🤼 Adversarial Review (MANDATORY)

> **⚠️ JAMAIS in-review sans l'aval du reviewer. Système adversarial : tu produis, le reviewer détruit.**

Launch a sub-agent with this prompt:

```
CONSIGNE ABSOLUE : lis et suis À LA LETTRE `reviewer.md`
(dans .cursor/commands/ ou .agent/workflows/).

Contexte :
- Issue #XX : [TITRE]
- Definition of Done : [COLLER]
- Walkthrough : [CHEMIN]
- Repo : [owner/repo]

1. Relis l'issue AVANT le walkthrough.
2. Vérifie, exécute, critique selon reviewer.md.
3. SIGNE le walkthrough si approuvé.
4. Problèmes HORS SCOPE → ne bloquent pas, remontés dans la signature.
```

**Ping-pong**: REJETÉ → fix 🔴🟡 problems, relance. APPROUVÉ → reviewer signe le walkthrough. **Max 3 itérations**.

### 5c. 🚦 Mark In-Review (AFTER reviewer approval)

1. Label `in-review` (remove `in-progress`) + comment:
   ```
   ✅ Issue marquée in-review.
   Résumé: [fait] | Validation: [tests] | Review interne: Approuvé ([N] itérations)
   En attente de review par l'Architect.
   ```
2. Update Roadmap → `🔍 In-review`.
3. AIVC `remember` summary.

> **Tu ne fermes PAS l'issue. L'Architect s'en charge.**

---

## Style
French (walkthrough/comments/plan callout). English (code/commits). Result-oriented. Honest.

## Checklist
- [ ] Issue read (body + comments)?
- [ ] AIVC context recovered (≥3 recalls)?
- [ ] Implementation plan with French callout?
- [ ] Marked `in-progress` at start?
- [ ] Code executed in real conditions?
- [ ] Stupid errors checked?
- [ ] Atomic commits, pushed?
- [ ] Walkthrough with actual outputs?
- [ ] Review sub-agent approved + signed?
- [ ] Marked `in-review` (NOT closed)?
- [ ] Roadmap updated?
- [ ] AIVC memory saved?
