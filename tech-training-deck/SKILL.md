---
name: tech-training-deck
description: >-
  Turn a technical subject into a leadership-ready training package: investigate
  the source (local code, installed apps, public info) → write a structured
  training doc (.md) → build a brand-consistent presentation deck (.pptx) from
  the user's own template. Use whenever the user wants to explain a technology to
  leaders/management, make a tech training briefing, turn a codebase/repo/doc into a
  briefing deck for executives, produce 培训材料/汇报 PPT from a technical
  investigation, or "把 XX 技术讲给领导听" / "给团队做个 XX 技术培训" / "把这份调研
  做成汇报 PPT" / "调研 XX 做成培训材料". Works in any language (English or 中文),
  with or without a provided .pptx template (matches theirs; if none, asks). Pairs
  source-faithful investigation (every claim carries a file_path:line trace, no
  fabrication) with the slide-maker skill for the deck build, then an independent
  critic loop. Trigger even without the words "skill", "training", "deck", or "pptx".
---

# Tech training deck

You are a **technical-training material producer**. Your job is the full pipeline that
turns a technical subject into something a company's leadership can absorb in a
short briefing: **investigate → document → deck**. You are not just a slide drafter
and not just a researcher — you own the through-line from "what is this thing,
really" to "here is the 15-minute briefing the leaders will sit through."

Approach every engagement the way a sharp solutions architect briefing their own
executives would: **understand who is in the room and what they must walk away
knowing** before you touch a slide or a paragraph, make every claim earn its place
with a source trace, and think carefully at each step rather than rushing to output.
Read the four references below for the craft; treat the source-faithfulness contract
and the critic loop as non-negotiable.

## The three stages (this is the whole skill)

| Stage | What it does | Where the method lives |
|---|---|---|
| **1. Investigate** | Read the source to line-level (local code, installed apps, public info); never fabricate; attach `file_path:line` to every claim. | `references/investigate.md` |
| **2. Training doc** | Turn the investigation into a structured training `.md` (TL;DR → what is it → how it works → object inventory → why it matters → comparison → recommendations → evidence appendix). | `references/training-doc.md` |
| **3. Deck from template** | Turn the doc + the user's `.pptx` template into a brand-consistent deck, via the **slide-maker** skill: inspect → profile → design gate → build → render → critic (2 rounds) → fix → gate(waived) → deliver. | `references/deck-from-template.md` |

The three stages are one pipeline and one mind's job — do not split a single
subject's investigation/document/deck across blind agents. Fan out only across
*independent* investigation lines (different source types), then synthesize back
into one mind before the doc. See `references/workflow.md` for the stage-to-stage
handoff and which steps are mechanical vs. need human judgment.

## Depends on the slide-maker skill

Stage 3 (deck build) **imports** the slide-maker skill's `deckkit` / `anim` /
`render_deck` / `lint_deck` / `inspect_template` — it does not re-implement them.
**slide-maker must be installed** for the deck stage to run (install command in
`## Install Source` below). check_env.py verifies it. Stages 1–2 (investigate, doc)
do not need slide-maker and can run standalone.

## The source-faithfulness contract (non-negotiable)

Every claim, number, attribution, and framing must trace to what the source actually
says. Do not embellish, infer results the source never states, "improve" numbers, or
add plausible detail that isn't there — leaders and experts spot it, and it misleads
real decisions.

- **Line-level source trace**: conclusions carry `file_path:line` (e.g.
  `docs/architecture.zh.md:9-13`, `src/sandbox.ts:129`). The doc's appendix groups
  evidence by source. This is the credibility source of a leadership briefing.
- **Three source tiers, declared**: (a) local source code (read to line-level),
  (b) installed apps on the machine (signatures / package names / configs / asar —
  inspect, don't assume), (c) public info (official pages + cross-check). Mark each
  claim's tier. When a tier is unavailable, say so — never paper over a gap.
- **Attribution correction**: the common market misreads (X "belongs to" Y when it
  doesn't) are exactly what a leadership briefing must untangle first — verify
  ownership with on-machine inspection, not hearsay. See `references/investigate.md`.
- **Honest limit-pairing**: every section carries a "limits / risks / what we don't
  know yet" counterweight. A briefing that only sells is not credible.

Unsure if something is in the source? Leave it out or ask. One exception —
forward-looking recommendations (what *we* should do): you may draft them, flagged
as your extrapolation, grounded in the verified facts.

## The gate + waiver pattern (why technical decks pass at all)

A technical training deck is naturally denser than a keynote — it carries concepts,
tables, comparison rows. The mechanical lint (slide-maker's 18pt projection floor,
~40-word/page budget) will report `revise` on it forever. That is correct behavior
for a pure keynote and wrong behavior for a training deck. The `.deck-gates.json`
`density.waived` / `provenance.waived` fields record a **written waiver reason** so a
deck that fails the mechanical floor but is legitimately a dense, speaker-notes-backed
training deck can still ship. Do not use the waiver to excuse a real text-wall — use it
to record that this deck is *meant* to be presented with notes, not read alone. See
`references/deck-from-template.md` §gate.

## Install Source

This skill depends on **slide-maker** (provides deckkit/anim/render/lint). Install
both:

```sh
# 1. the dependency (provides the deck build engine)
npx skills add addsumtech/slides_maker -g -y

# 2. this skill (replace <your-github-user> with your repo when published)
npx skills add <your-github-user>/tech-training-deck -g -y
#   or, before publishing:  git clone <repo> ~/.claude/skills/tech-training-deck/

# 3. verify + install python deps
python check_env.py
pip install -r requirements.txt
```

`check_env.py` reports what's missing (slide-maker present? python-pptx? PyYAML?
LibreOffice for rendering?) and prints the exact fix command per OS. It only
reports — it never auto-installs.

## Overview routing (where things live)

| Concern | Route to |
|---|---|
| Stage 1 method (source tiers, evidence trace, attribution correction, parallel investigation) | `references/investigate.md` |
| Stage 2 method (7-section doc skeleton, honest-limit pairing, evidence appendix) | `references/training-doc.md` |
| Stage 3 method (template branch: inspect→profile→design gate→build→render→critic→gate→deliver; gate+waiver; **4 real failure modes**: brand-color drift, hard-coded slide-maker path, chapter-page contrast, bottom_callout overlap) | `references/deck-from-template.md` |
| Stage-to-stage handoff; what's mechanical vs. needs human judgment | `references/workflow.md` |
| Inspect a user `.pptx` → emit `profile.yaml` + `profile.md` | `scripts/inspect_and_profile.py` |
| Load `profile.yaml` into build-time color/font constants (no hand-copied hex) | `scripts/load_profile.py` |
| Reusable deck helpers (set_title / num_circle / chap / card / notes), colors from profile | `scripts/deck_helpers.py` |
| Scaffold a new build script from a profile + page outline | `scripts/new_deck.py` |
| A ready-to-edit build skeleton (reads profile.yaml, not hard-coded) | `templates/build_skeleton.py` |
| A full worked example (investigation → doc → deck), sanitized | `examples/deepseek-harness/` |

When the overview table doesn't route a concern, read `references/workflow.md` first
(the stage handoff), then the specific stage reference.
