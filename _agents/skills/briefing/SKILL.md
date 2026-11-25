---
name: briefing
description: "Maintains a living, 100% self-sufficient English Shared Project Note (`notes/Project Overview <Project>.md`) for supervisors and collaborators via `obsidian-comment-share` (`henri-obsidian-share.web.app`): strict first-person singular voice (`I` / `my`, never `we decided`), atomic question headings, concise senior scientific-writing prose (zero bullet lists, numbers in tables, zero em-dashes), zero decorative images (empirical graphs/diagrams only), zero spin or conclusions, strict zero-collaborator-naming rule, `[!quote]` callouts summarizing collaborator feedback with Henri's responses/results, and `[!question]` callouts for open decisions. Trigger on /briefing."
---
# 📋 `/briefing` — Self-Sufficient Collaborator Project Notes (`obsidian-comment-share`)

**Purpose**: Maintain **one single living English Shared Project Note per research project** (`notes/Project Overview <Project>.md`, replacing legacy dated briefings and Loop pages) published and updated in place on `https://henri-obsidian-share.web.app` via the **`obsidian-comment-share`** plugin CLI (`share_url` persisted in YAML frontmatter so collaborators see exact `vN -> vN+1` AST word-diffs, step with `↑`/`↓`, validate individual diffs with `Ctrl+Enter`, and leave inline comments on text and figures).

> [!IMPORTANT]
> **Mandatory Co-Activation with [`scientific-writing`](file:///c:/Users/hjamet/Documents/VoiceNotes/_agents/skills/scientific-writing/SKILL.md)**: Always enforce `scientific-writing` before drafting or updating any `Project Overview <Project>.md` note, and run `avoid-ai-writing` (`detect.js` + `check-style.js`) before publishing.

---

## 🎯 1. Core Communication Norms with Supervisors & Collaborators (MANDATORY)

1. **Strict First-Person Singular Voice (`I` / `my`) — NEVER `we` / `our`**:
   - This note is maintained solely by Henri as his personal research briefing to supervisors and collaborators. **Always write in the first person singular (`I ran`, `I propose`, `my analysis`, `my view`)** and **never write *"we decided"*, *"we chose"*, or *"our plan"*** (which falsely implies collaborators already approved pending choices). Refer to shared manuscripts neutrally (*"the submitted manuscript"*, *"the Phase I dataset"*).
2. **100% English, Atomic Question Headings & Tight Non-Verbose Prose**:
   - Every `H1` (`#`), `H2` (`##`), and `H3` (`###`) heading MUST be a concise, atomic question in plain academic English ending with `?`.
   - **Concise continuous paragraphs (`2` to `4` tight sentences), zero bullet lists, numbers in tables**: explain *what I tested*, *why*, *current status* (`Completed`, `In Progress`, `Planned`), and *how to read the table/figure* without verbose padding or multi-clause walls of text. Keep exact numbers, means $\pm$ SEM/SD, test statistics, and $p$-values in Markdown tables and figures (at most 1–2 orientation magnitudes in prose). Target `0` em-dashes (`—`, `--`) and `0` AI clichés (`avoid-ai-writing`).
3. **ZERO Decorative Images — Empirical Graphs, Plots & Technical Diagrams ONLY**:
   - **Strictly forbid** AI-generated header illustrations or decorative cover banners (omit `Image:` from body; use only scientific visuals). Only embed data plots, statistical comparison charts, heatmaps, protocol/architecture Mermaid diagrams, and timeline Gantt charts (`![[plot.png]]`).
4. **100% Self-Sufficient Snapshot & Zero Collaborator Naming**:
   - **Zero internal vault links or plumbing**: never include `[[notes/...]]`, local `file:///...` paths, script names, internal IDs (`#7201`, `LOOP #...`), server IPs, participant hashes, or low-level hyperparameters. Use only public external URLs (OpenReview, Overleaf view-only link, OSF DOI, published papers).
   - **NEVER name any collaborator or supervisor** (`Yash`, `Pamela`, `Michalis`, `Yuanjun`, etc.) anywhere in prose, headings, tables, figures, captions, or callouts, so the exact same link works cleanly for every co-author.
5. **Collaborator Feedback & My Response Callouts (`[!quote]`)**:
   - Whenever supervisors or collaborators raise comments, critiques, or requests (by email, in meetings, or via inline web comments), surface them **inside the relevant section** using a compact **`> [!quote] Feedback Addressed: <Topic>`** callout (rendered in slate-indigo on `henri-obsidian-share.web.app`).
   - Synthetically summarize the feedback raised (grouping related remarks together in `1–2` sentences, zero personal names) and immediately follow with Henri's first-person opinion, action taken, and empirical findings (`Feedback raised: ... My response: ...`), so every co-author sees all prior feedback and outcomes in one place without digging through email threads.
6. **Zero Spin, Zero "Conclusion" Section & High-Visibility `[!question]` Callouts**:
   - Include **no "Conclusion" section** and report null, marginal, and counter-intuitive results side-by-side in tables without spin.
   - Place open methodological or strategic questions inside `> [!question] Question N: <Atomic Question?>` (amber callout) inside the relevant thematic section, written in tight first-person sentences and **immediately preceded by 100% of the decision context** (trade-offs, power, timeline, budget). Remove questions once resolved.

---

## 🔄 2. Verification & `obsidian-comment-share` Publication Workflow

```powershell
# 1. Verify scientific prose hygiene (0 em-dashes, no AI clichés)
node "c:\Users\hjamet\Documents\VoiceNotes\_agents\scripts-for-skills\avoid-ai-writing\skills\ai-writing-detector\scripts\detect.js" --file "c:\Users\hjamet\Documents\VoiceNotes\notes\Project Overview <Project>.md" --context technical
node "c:\Users\hjamet\Documents\VoiceNotes\_agents\scripts-for-skills\avoid-ai-writing\scripts\check-style.js" "c:\Users\hjamet\Documents\VoiceNotes\notes\Project Overview <Project>.md" --config technical

# 2. Pull any pending collaborator comments, then publish/update the Shared Project Note in place
node "c:\Users\hjamet\Documents\VoiceNotes\.obsidian\plugins\obsidian-comment-share\cli.cjs" pull
node "c:\Users\hjamet\Documents\VoiceNotes\.obsidian\plugins\obsidian-comment-share\cli.cjs" share "notes/Project Overview <Project>.md"
```

**Mandatory Reporting to Henri**: Always provide `[Project Overview <Project>.md](file:///...)`, the live capability URL `https://henri-obsidian-share.web.app/n/<shareId>?k=<readKey>` (`vN`), and the exact `node "...\cli.cjs" share "notes/Project Overview <Project>.md"` command.
