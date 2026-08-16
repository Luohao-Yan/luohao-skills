# Stage 2 — Training doc (the 7-section leadership-briefing skeleton)

You are writing the `.md` that a technical lead will turn into a deck (Stage 3) and
that leaders may read directly. It is a **briefing**, not a manual: structured for
"understood in minutes," every claim carrying the `file_path:line` trace from Stage 1
(`references/investigate.md`), every section paired with an honest limit.

This skeleton was validated on a real technical briefing (a DeepSeek-Harness
leadership training). It is the default — deviate when the subject's shape demands
it, and name the deviation in the doc's opening.

## The 7-section skeleton

### 0. TL;DR (one-page conclusion)
The page a busy leader reads first. Three parts:
- **A scannable ownership/summary table** — one row per key entity, columns =
  name / owner / form / key capability / model backend (or the dimensions the
  subject demands). This is the Stage-1 ownership table, promoted to the top.
- **Three bold punchlines** — one-sentence each: "one-line understanding",
  "core mechanism", "strategic judgment" (or the subject's equivalent three).
- **One key-finding callout** — the single most important thing the investigation
  surfaced (often an attribution correction or a "X embeds Y" discovery).

### 1. What it is (orientation)
- **Definition / positioning formula** if one exists (e.g. `Agent = Model +
  Harness`), quoted from the source with its locator.
- **How it runs** — a minimal `sh` block a reader could execute.
- **Modes / variants table** — if the thing has runtime modes, one table row each.
- **Honest note** — maturity, breaking-change risk, "developer preview" status,
  quoted from the source (`README.zh.md:11`). This is the first limit-pairing.

### 2. How it works (the mechanism, "讲透" depth)
The technical core, bottom-up, each step carrying `file_path:line`:
- **Underlying concepts in plain language** (e.g. the framework's 5 core concepts,
  each = name + one-line + its source locator).
- **Abstract model** (e.g. a capability seam = 3 roles; cite the architecture doc).
- **Composition mechanism** — a `mermaid` flowchart when the thing composes layers
  (profile → bundle → preset → patched tree), with source locators under it.
- **Instance table** — the abstract model made concrete (e.g. one row per seam:
  `ctx.<key>` | Service Definition | swappable Providers | Consumer).
- **"I want to add X → mount which plugin" mapping table** — the proof that
  extension is configuration, not surgery. Cite the doc section that lists it.
- **The most distinctive capability** last (e.g. self-modification), with
  line-level source (`sandbox.ts:129`, `guard.ts:551/626/718`).

### 3. Object inventory (the things in scope, per-entity detail)
For a subject that spans multiple products/components:
- **A summary table** (same columns as §0, plus a "source tier" column: local-code /
  installed-app / public-info).
- **Per-entity detail**, each with a **fixed facet set** so they're comparable:
  owner & form / does it contain capability X / what else besides X / model backend
  / relationship to the anchor subject. Same facets every entity → horizontally
  scannable.
- **One-line distinguisher** at the end ("一句话区分四者").

### 4. Why it matters (the strategic read)
- **Current state** — the market condition that makes this matter (e.g. model-layer
  commoditization, margin compression).
- **The play** — numbered steps (1..N) of how the subject's owner exploits it.
- **Intent behind the formula** — connect back to §1's positioning formula; compare
  to an analogous play (e.g. Meta open-sourcing Llama for the model layer).
- **Honest limits & risks** (limit-pairing): the play's softness, the competing
  standards, what's unsettled. A briefing that only sells is not credible.

### 5. Comparison (anchor subject vs. comparator)
- **Correction up front** if the comparator is commonly misattributed.
- **Multi-dimension comparison table** (7±2 rows: positioning / architecture / model
  / capability / office / deploy / shared-underlying).
- **The most interesting layer** — the one where they're same-origin or most-divergent
  (e.g. both use the same LLM-abstraction library, one as built-in base, one as
  swappable backend). Give both dependency versions + the adapter path as evidence.
- **One-line distinguisher.**

### 6. Recommendations (for "us")
- **Our current situation** (facts — what we're already doing with the subject).
- **Numbered recommendations**, each = title + stance + how-to. Be specific and
  actionable; this is the part the leaders act on.
- **One-line close.**
- State the **stance** the recommendations are written from (e.g. "we're on the
  WPS-cloud-model side doing enterprise AI presales") so readers can adjust if
  their stance differs.

### Appendix — Evidence provenance
Grouped by source (A. local source / B. installed app / C. …), each group listing
the `file_path:line` locators or install-dir paths used. This is the Stage-1 evidence
list, organized so a reader can audit any claim. The appendix is what makes the
briefing defensible.

## Two cross-cutting contracts

1. **`file_path:line` on every conclusion.** Source-trace is the credibility source.
   The doc opens by declaring "all source-code conclusions carry `file_path:line`"
   and the tier of each evidence type.
2. **Honest limit-pairing in every section.** §1 has the maturity note, §2 the
   "what's still unsettled," §4 the limits & risks, §6 the stance caveat. A briefing
   that never admits a limit is a sales pitch, not a briefing — and leaders discount
   it accordingly.

## Output of stage 2

A single `.md` (typically 6000–9000 words for a real subject) that the Stage-3 deck
build (`references/deck-from-template.md`) will condense onto slides — the doc keeps
the full reasoning, the deck keeps the phrase + the speaker-notes narration. Write
the doc first, fully; the deck is its projection, not its replacement.
