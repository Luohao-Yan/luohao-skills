# Workflow — stage handoff, and what's mechanical vs. human judgment

The three stages (`references/investigate.md` → `training-doc.md` →
`deck-from-template.md`) are one pipeline and one mind's job. This file is the
handoff between them, and the honest list of which steps a machine can do and which
need your judgment. Read it when the overview table in `SKILL.md` doesn't route a
concern, or when you're deciding whether to automate a step.

## The pipeline, end to end

```
user need
   │
   ├─ Stage 0 BRIEF ──────────────────────────────────────────────┐
   │   3 rounds AskUserQuestion (all defaults skippable)          │
   │   → brief.yaml (13 fields: audience/tilt/pages/animation/      │
   │     template/language/emphasis/fidelity/need_arch_diagram/    │
   │     need_network_topo/outdir/subject/purpose)                 │
   │   drives every later stage; missing fields fall back to defs  │
   │                                                               ▼
   ├─ Stage 1 INVESTIGATE ────────────────────────────────────────┐
   │   fan out Explore agents across independent source lines      │
   │   (local code / installed apps / public-info / comparator)   │
   │   synthesize → ownership table + per-source evidence list     │
   │   (gaps explicitly marked)                                   │
   │                                                               ▼
   ├─ Stage 2 TRAINING DOC ──────────────────────────────────────┐
   │   7-section skeleton (TL;DR → what → how → inventory →        │
   │   why → compare → recommend → evidence appendix)             │
   │   every claim carries file_path:line; every section has a     │
   │   honest-limit counterweight                                   │
   │                                                               ▼
   └─ Stage 3 DECK FROM TEMPLATE ────────────────────────────────┐
       inspect user.pptx → profile.yaml → design gate →           │
       build (deckkit, colors from profile) → render →            │
       critic ×2 → fix → gate(strict + density.waived) → deliver  │
                                                                   ▼
                                                            pptx + pdf + viewer
```

Each stage's output is the next stage's input, and **each stage's contract must be
met before passing forward** — Stage 2 doesn't start until Stage 1's claims are
traced; Stage 3 doesn't start until the doc's skeleton is complete.

**Brief.yaml is the shared input contract** — Stage 0 writes it; Stages 1–3 read
the fields they need (`tilt/audience/purpose/emphasis` → Stage 1 scope;
`pages/emphasis/fidelity` → Stage 2 doc; `animation/template/language` +
`need_arch_diagram/need_network_topo` → Stage 3 deck + figures). Missing fields
fall back to `brief.DEFAULTS` (see `scripts/brief.py`), never error.

## What's mechanical (automate / script) vs. needs human judgment

### Mechanical — let scripts / the model do these without ceremony
- **Template inspection** → `scripts/inspect_and_profile.py` (reads slide size,
  layouts, placeholders, theme colors, fonts; emits `profile.yaml` + `profile.md`).
- **Profile loading** → `scripts/load_profile.py` (injects brand constants; no
  hand-copied hex).
- **Build scaffolding** → `scripts/new_deck.py` / `templates/build_skeleton.py`
  (open_template → per-slide add → lint → save).
- **Rendering** → slide-maker `render_deck` (pptx → PNG + viewer + pdf).
- **Layout lint** → slide-maker `lint_layout(strict=True)` (overflow, off-canvas,
  footer collision — these are hard gates, never waived).
- **Critic's mechanical checks** → text-wall word count, small-type detection,
  contrast ratio, overflow — `lint_deck.py` computes these.
- **The chapter-page contrast fix** → `deck_helpers.chap` draws the backing strip
  deterministically.
- **`viewer.html` / `num_circle` / `set_title` / `card`** calls.

### Needs human judgment — don't automate, don't rubber-stamp
- **Stage 1 conclusions** — reading source to line-level, judging installed-app
  attribution, reconciling conflicting public sources. Parallel Explore agents
  gather, but *you* synthesize and judge.
- **Naming / attribution clarification** — "is the user's 'X' the same as product
  Y?" needs a user confirm; never assume (see the "WPS Connect = Comate" case —
  confirming the name changed the whole section).
- **The 7-section outline & what goes in TL;DR vs. a section** — what's the one
  thing, what's supporting. The skeleton is a default; the subject's shape may
  demand a deviation, which you name.
- **`signature_move` design** — *which* slide is the visual peak and *how* the core
  argument becomes its geometry. This is taste, not a formula.
- **`semantic_contract`** — which accent = which semantic role, bound to *this*
  subject's content (red = the anchor subject; orange = the comparator; …).
  Template-derived but content-bound.
- **The critic's verdict & the waiver** — when the mechanical lint says `revise`
  but the deck is a legitimately dense training deck, *you* judge consent and record
  the written waiver reason in `.deck-gates.json density.waived`. A machine left to
  itself reports `revise` forever on a training deck; the waiver is the human
  override that says "this is meant to be presented with notes, not read alone."
- **Stage 6 recommendations** — stance-dependent ("don't ship to prod yet",
  "unify the messaging") cannot be auto-generated; they need your read of the
  situation.

## The two most common handoff failures (avoid these)

1. **Skipping Stage 1's trace into Stage 2.** Writing the doc from memory/web
   instead of from the traced evidence list → untraceable claims → a briefing that
   fails under scrutiny. The doc must be writable *without re-investigating*
   because Stage 1 already attached every locator.
2. **Letting the mechanical gate veto a training deck.** `--deliverables` refuses a
   deck over the density budget; the reflex is to shrink type or cut content until
   it passes — which ruins a training deck. The correct move is the written
   `density.waived` reason (Stage 3 §gate), *not* degrading the deck to satisfy a
   keynote-shaped gate.

## When to fan out vs. stay one mind

- **Fan out** across *independent* investigation lines (different source tiers,
  different products) and across *independent* asset prep (figure crops, equation
  PNGs).
- **Never fan out** one line's argument — one repo's intro/method/internals, one
  product's capabilities, one section's reasoning. The through-line is one mind.
- **Synthesize back into one mind** before Stage 2: reconcile, dedupe, tier-assign,
  build the ownership table. Two agents' unreconciled claims are a fabrication
  waiting to happen.
