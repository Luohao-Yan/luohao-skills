# Stage 3 — Deck from the user's template (orchestrates slide-maker)

You are turning the Stage-2 training doc (`.md`) into a brand-consistent `.pptx`
deck, **using the user's own `.pptx` template** — never an embedded internal
template (copyright). The heavy lifting (deck build, render, lint, critic) is done
by the **slide-maker** skill, which must be installed (see SKILL.md `## Install
Source`). This stage's job is the **template-specific glue**: inspect the user's
template, capture its brand into a reusable profile, design the deck on that brand,
build via slide-maker, then pass the critic with a recorded waiver for the training
deck's natural density.

Read `references/investigate.md` (the doc's claims must already be source-traced)
and `references/training-doc.md` (the doc skeleton) before this — Stage 3 projects
that doc onto slides; it does not re-investigate.

## The template branch, step by step

### 1. Inspect the template → emit `profile.yaml` + `profile.md`
Run `scripts/inspect_and_profile.py <user.pptx>`. It uses slide-maker's
`inspect_template` to read slide size, layout indices+names, placeholder geometry,
and master/layout media, **plus** extracts the theme `clrScheme` (accent1..6 with
hex) and the font scheme (latin + ea typefaces). Output:
- `profile.yaml` — **machine-readable**, the build script loads it (no hand-copied
  hex constants). Fields: `canvas {w_in, h_in}`, `colors {accent1: "#E6002D", …}`,
  `fonts {latin, ea}`, `layouts {idx: {name, role, placeholders}}`,
  `semantic_contract {<role>: <accent>}` (you fill this — see below).
- `profile.md` — human-readable brand brief (canvas, theme colors with semantic
  roles, fonts, layouts, cover composition, content-page visual idiom, footprint
  notes e.g. "no SVG rasterizer on this machine → use geometric idiom").

This fixes the biggest drift bug from the reference build: there, brand colors were
hand-copied into the build script and could silently desync from the template.
`profile.yaml` is the single source; `scripts/load_profile.py` injects it.

### 2. Design gate (before building)
Record the design plan, mirroring slide-maker's design checkpoint, in a
`.deck-gates.json` you keep alongside the build:
- `boldness` — default `balanced+`.
- `signature_move` — **the one slide that is the deck's visual peak**, a scoped
  aesthetic risk where the core argument becomes geometry (e.g. drawing the model
  base as a swappable slot with three provider cards). This is not decoration — it
  is the argument itself, made visible. Name it, and let 2–3 other slides carry the
  same motif structurally (`carried_by`).
- `form_ledger` — which layout archetype each slide uses (4-card / 2-col compare /
  dark key-finding / formula+chips / slot-diagram / 3-column / table / numbered-steps
  / red-conclusion / chapter dividers). Vary the protagonist; don't let one skeleton
  dominate.
- `semantic_contract` — bind each accent to a **semantic role** (red = the anchor
  subject / core conclusion; orange = the comparator; navy = neutral; gold =
  emphasis). This is the `semantic_contract` block in `profile.yaml`.
- `type_scale` — three tiers as numbers (`{display, title, body}`), drawn from the
  template's tokens.
- `icon_family` — if the machine has no SVG rasterizer (cairosvg/libcairo), record
  `carve: uses geometric idiom (numbered gradient circles, colored-edge cards,
  arrows) instead` and use the template's geometric vocabulary. Don't fail trying
  to rasterize icons.

### 3. Build (via slide-maker's deckkit, colors from profile)
Use `templates/build_skeleton.py` as the starting point — it reads `profile.yaml`
(through `scripts/load_profile.py`) rather than hard-coding hex, and ships the
reusable helpers from `scripts/deck_helpers.py`:
- `set_title(slide, text, …)` — fills the title placeholder (idx 0) and tags CJK
  with the ea font (`dk._apply_ea`) so it renders + kinsoku engages. **Every** content
  layout needs this; without the ea tag, CJK renders via uncontrolled fallback.
- `num_circle(slide, cx, cy, d, num, …)` — the numbered gradient circle (template
  idiom), colors from profile.
- `chap(prs, num, title, sub)` — chapter divider. See the contrast fix below.
- `card`, `para`, `notes` — thin semantic wrappers over `dk.box` / run-tuples /
  `dk.speaker_notes`.

The build rhythm (proven, theme-independent): `dk.open_template(TPL)` → per slide
`add_slide(layout_idx)` → `set_title` → `dk.columns/rows/content_band` to get the
safe rect → `card` + `dk.text` + `num_circle` + `dk.bottom_callout` → optional
`Build.step()` for appear-builds on multi-step slides → `notes` (speaker script) →
`dk.lint_layout(prs, strict=True)` → `prs.save(OUT)`.

**Put full sentences in `notes`, phrases on the slide.** The deck is a visual aid
for a speaker; the narration lives in speaker notes (Stage-2 doc → on-slide phrase
+ notes narration).

### 4. Render + critic (2 rounds, via slide-maker)
`render_deck` → per-slide PNG + `viewer.html` + `.pdf`. Then run the independent
critic (slide-maker's `agents/critic.md`) twice — round 1 finds the majors
(text-wall, small-type), round 2 confirms fixes and finds residuals. Fix what the
critic flags; the critic is not the final judge of your work, you are — but ignoring
it is the failure.

### 5. The gate + waiver (§gate — why training decks pass at all)
slide-maker's `--deliverables` gate wants `.deck-gates.json` with `critic.verdict`
(`consent`|`revise`), a `design_plan` block, and a `density` block. For a **training
deck** the mechanical density check (18pt projection floor, ~40-words/page) will
fail — and should, for a pure keynote. A training deck is denser by nature. Record:

```json
"density": {"waived": "<why this deck is meant to be presented with speaker notes, not read alone; on-slide text is parallel phrases/tables/numbered points, not prose walls; this density is required to carry the concept, not a self-read wall-of-text>"}
```

and `"provenance": {"waived": "<built from the user's own local source, not web research>"}` when applicable. The waiver is a **written reason**, not an omission —
use it to record a deliberate, defensible choice, never to excuse a real text-wall.
The `lint_layout(strict=True)` criticals (overflow, off-canvas, footer collision)
are **non-negotiable** — waive density, never waive a layout fault.

### 6. Deliver
pptx + pdf + viewer.html + render/ PNGs, copied to the user's chosen location. Flag
the font dependency (the template's CJK font, e.g. 微软雅黑, must be present on any
machine that opens the deck) and the animation caveat (appear-builds need
PowerPoint/Keynote to play; LibreOffice renders only the final state).

## The chapter-page contrast fix (a real failure mode)

Many corporate templates' chapter-divider layout (a full-bleed background image:
deep-red→orange gradient + dot-matrix) makes **white title text unreadable** in the
bright-orange dot regions — the page looks "empty" to the audience even though the
text is there. The fix (validated): draw a **semi-transparent dark gradient backing
strip** behind the chapter title (number + title + optional subtitle), so white
text sits on a controlled dark band. `deck_helpers.chap` does this; adjust the
backing alpha/geometry per template. If a divider looks empty after build, this is
the first thing to check — it's a contrast problem, not a missing-content problem.

## The bottom_callout + content overlap fix (a real failure mode)

`dk.bottom_callout(x, w, label, body, footer_gap=…)` **measures its own height from
the body text and grows upward from above the footer** — it returns its top y. A long
body (two wrapped lines) makes it tall, so its top rises and **collides with the
content above** (numbered cards, chip rows) that you placed with a hard-coded
`bottom`. The failure is silent at build (the cards don't know the callout's top), so
`lint_layout`'s `TEXT_OVERLAP` critical is your only alarm.

Two safe fixes (use either, often both):
1. **Keep the on-slide body short** — move the long sentence to speaker notes; the
   callout body should be one line. This is the cheapest fix and matches "sentences in
   notes, phrases on the slide."
2. **Reserve enough bottom for the callout** — set the content block's `bottom` so the
   content's lowest edge sits above where a callout's top would land (~6.3in on a 7.5in
   slide with the default footer_gap). For a 4-row numbered block, `bottom≈1.25in`
   leaves room; `bottom≈0.95in` is too tight and will overlap when the body wraps.

Do **not** shrink the content block so much that its own text overlaps (a too-tall
`bottom` compresses cards and the card's title/description text overlap each other —
also a `TEXT_OVERLAP`). The content block needs its real text height; reserve the
callout room by shortening the body, not by crushing the cards.

## What Stage 3 does NOT do
- Re-investigate (Stage 1) or re-structure the argument (Stage 2) — it projects the
  already-verified doc onto slides.
- Embed an internal/copyrighted template — the user supplies the `.pptx`; the skill
  ships only a sanitized example profile, never a real company template.
- Re-implement deckkit/anim/render/lint — it imports slide-maker. If slide-maker
  isn't installed, Stage 3 stops at "install slide-maker"; Stages 1–2 still work.
