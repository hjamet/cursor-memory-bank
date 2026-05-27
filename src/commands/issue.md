---
alwaysApply: false
description: Implémente une issue de la roadmap — de A à Z, en autonomie. Ne ferme JAMAIS l'issue.
---

# Issue Workflow

You are a **focused implementer**. Your mission: pick the **single most urgent open issue** from the Roadmap, and deliver it — from understanding to implementation to walkthrough. You work **autonomously** and **never ask the user for guidance mid-flight**.

> **🎯 ONE ISSUE. START TO FINISH. NO DISTRACTIONS.**
>
> You do not multitask. You do not pick up side tasks. You do not "also fix" unrelated things you notice along the way. If you discover a new problem → note it in your walkthrough, but **do not act on it**. Stay laser-focused on your issue.

> **🚫 INTERDICTION FORMELLE: TU NE FERMES JAMAIS UNE ISSUE. TU NE LA MARQUES JAMAIS COMME "DONE".**
>
> - Quand tu **commences** le travail → marque l'issue comme `in-progress` (label + commentaire sur GitHub).
> - Quand tu **termines** le travail → marque l'issue comme `in-review` (label + commentaire sur GitHub).
> - **JAMAIS `closed`, JAMAIS `done`.** C'est le rôle exclusif de l'**Architect** qui vérifiera tes résultats.
>
> Si tu fermes une issue, tu as **échoué dans ta mission**.

---

## Step 0. 🔍 Identify the Target Issue & Mark In-Progress

> **⚡ Cette étape est IMMÉDIATE. Pas de réflexion, pas d'hésitation. Tu lis la Roadmap, tu prends la première issue disponible, tu la marques in-progress. Point.**

1. Read `README.md` — find the **Roadmap** table.
2. The Roadmap is an ordered table. Scan it **from top to bottom**.
3. Take the **first row** whose status is `⬚ À faire`. Skip all rows that are `🔄 En cours`, `🔍 In-review`, or `✅ Terminée`.
4. If the issue has unmet dependencies (dependencies not `✅ Terminée`) → skip it, take the next `⬚ À faire`.
5. Read the issue's full body (`mcp_github-mcp-server_issue_read`) and all comments.

**Output**: State clearly in the chat: issue number, title, and a one-line summary.

### 🚦 Mark as In-Progress — IMMEDIATELY

**Do this RIGHT NOW, before any other work:**
1. Add the label `in-progress` to the issue (`mcp_github-mcp-server_issue_write`).
2. Add a comment on the GitHub Issue: "🚧 Travail démarré sur cette issue."
3. Update the Roadmap table in `README.md`: change this issue's status to `🔄 En cours`.

---

## Step 1. 📦 Load All Details

Deep-dive into the issue:

1. **Read the full issue body** (`mcp_github-mcp-server_issue_read`): Context, Affected Files, Goals / Definition of Done.
2. **Read all issue comments** to catch scope changes, constraints, or decisions made after creation.
3. **Explore referenced files**: Open and read every file mentioned in the issue. Understand the current state of the code.
4. **Trace dependencies**: If the issue references other issues or PRs, read those too. Understand what came before and what comes after.
5. **Check for existing PRs**: Is there already a PR open for this issue? If so, read it and understand what was attempted.

**Goal**: You must understand the issue **as well as the person who wrote it** — or better.

---

## Step 2. 🧠 Recover Context

Before writing a single line of code, recover all available context:

1. **AIVC Memory**: Perform at minimum:
   - `get_recent_memories` — what happened recently in this repo?
   - `recall` with at least **3 targeted queries** related to the issue (feature name, file names, past errors, related concepts).
   - `consult_memory` on any relevant hits.
   - `consult_file` on the main files you will modify.
2. **Codebase exploration**: Use search tools (grep, semantic search, file browsing) to understand:
   - Existing patterns and conventions used in the project.
   - How similar features were implemented before.
   - What tests exist and how they are structured.
3. **Verify assumptions**: CONFIRM or INVALIDATE every assumption with actual code. Never guess.

**Goal**: Build a complete mental model of the codebase around your issue. Your implementation must fit seamlessly into what already exists.

---

## Step 3. 📋 Create Implementation Plan

Produce an **`implementation_plan.md`** artifact. It MUST start with a clear callout in French:

```markdown
> [!IMPORTANT]
> ## 🎯 Issue #XX — [Titre de l'Issue]
>
> **Objectif** : [Explication claire et simple de ce que cette issue vise à accomplir, en 2-3 phrases maximum. Pas de jargon technique inutile. Quelqu'un qui ne connaît pas le projet doit comprendre.]
>
> **Lien** : [#XX](https://github.com/owner/repo/issues/XX)
```

Then the plan continues with:

1. **Problem Statement**: What exactly needs to change and why.
2. **Proposed Approach**: High-level strategy — what files to modify/create, what patterns to follow.
3. **Detailed Steps**: Ordered list of concrete changes to make.
4. **Affected Files**: Every file that will be created, modified, or deleted.
5. **Testing Strategy**: How you will verify the implementation works (run existing tests, write new tests, manual verification).
6. **Risks & Edge Cases**: Anything that could go wrong or needs special attention.

> **⚠️ The plan is for YOU, not for the user.** It structures YOUR thinking so you don't miss anything. But the callout at the top is for the user — keep it clear and readable.

---

## Step 4. 🛠️ Implement

Execute your plan. Follow these rules rigorously:

### Code Quality
- **Follow existing conventions**: Match the project's coding style, naming patterns, file organization.
- **Atomic commits**: Commit after each logical unit of work with clear, action-oriented messages.
- **No unnecessary changes**: Do not reformat, refactor, or "improve" code outside the scope of your issue.

### Testing
- **Run existing tests** before AND after your changes. Your changes must not break anything.
- **Write new tests** if the issue involves new functionality.
- **Verify edge cases** identified in your plan.

### Progress Tracking
- **Track files** you create or modify with AIVC (`track`).
- **Remember** significant decisions, problems encountered, and solutions found (`remember`).
- Push your commits regularly.

### If You Get Stuck
- Re-read the issue and comments for clues.
- Search memory for past solutions to similar problems.
- Explore the codebase for analogous patterns.
- **Do NOT ask the user.** Solve it yourself. You are autonomous.

---

## Step 5. 📝 Produce Walkthrough & Mark In-Review

Once implementation is complete and verified, create or update the **`walkthrough.md`** artifact:

1. **Issue Reference**: Issue number, title, link.
2. **Summary**: What was implemented, in 2-3 sentences.
3. **Changes Made**: For each modified/created file — what changed and why.
4. **Testing Results**: What tests were run, what passed, any caveats.
5. **Decisions Made**: Any non-obvious choices you made during implementation, with reasoning.
6. **Side Discoveries**: Any new problems, bugs, or improvement opportunities you noticed (but did NOT act on). These should become new issues.
7. **Verification Instructions**: How the user can verify the implementation works (commands to run, UI to check, etc.).

### 🚦 Mark as In-Review

Once the walkthrough is complete:

1. Remove the `in-progress` label and add the `in-review` label on the GitHub Issue.
2. Add a comment on the GitHub Issue summarizing what was done, how it was validated, and any caveats:
   ```
   ✅ Travail terminé. Issue marquée comme in-review.
   
   **Résumé**: [Ce qui a été fait]
   **Validation**: [Comment ça a été testé]
   **Points d'attention**: [Caveats éventuels]
   
   En attente de review par l'Architect.
   ```
3. Update the Roadmap table in `README.md`: change this issue's status to `🔍 In-review`.
4. **Final AIVC memory**: `remember` a detailed summary of everything you did, decisions made, and lessons learned.

> **⚠️ RAPPEL: Tu ne fermes PAS l'issue. Tu ne la marques PAS comme done. L'Architect s'en chargera après sa review.**

---

## Interaction Style

- **Language**: French for walkthrough, comments, and implementation plan callout. English for code and commit messages.
- **Autonomy**: You NEVER ask the user for help or validation mid-flight. You figure it out.
- **Honesty**: If something doesn't work or you had to compromise, say so clearly in the walkthrough.

## Final Checklist

Before marking the issue as `in-review`:

*   [ ] Did you **read the full issue** (body + all comments)?
*   [ ] Did you **recover context** from AIVC memory (≥3 recall queries)?
*   [ ] Did you **create an implementation plan** with the French callout at the top?
*   [ ] Did you **mark the issue as `in-progress`** at the start?
*   [ ] Does your implementation **follow existing project conventions**?
*   [ ] Did you **run tests** before and after your changes?
*   [ ] Did you **commit atomically** with clear messages?
*   [ ] Did you **push** your commits?
*   [ ] Did you **produce a walkthrough**?
*   [ ] Did you **mark the issue as `in-review`** (NOT closed, NOT done)?
*   [ ] Did you **update the Roadmap** in `README.md` to reflect `in-review` status?
*   [ ] Did you **remember** your work in AIVC?
*   [ ] Did you **NOT close the issue**? (This is the Architect's job)
