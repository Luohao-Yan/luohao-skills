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
- `semantic_contract` — bind each accent to a **semantic role** with these exact
  keys: `anchor_subject` (the main subject / core conclusion — red), `comparator`
  (the comparison — orange), `neutral` (headers / structure — navy), `emphasis`
  (take-away / key line — gold). The key is `anchor_subject` (not `anchor`);
  the build script reads it as `D.anchor`. This is the `semantic_contract` block
  in `profile.yaml`. If left empty, `load_profile` falls back to
  accent1..4 by role so the build still runs — but filling it is what assigns
  colors to your semantics.
- `type_scale` — three tiers as numbers (`{display, title, body}`), drawn from the
  template's tokens.
- `icon_family` — if the machine has no SVG rasterizer (cairosvg/libcairo), record
  `carve: uses geometric idiom (numbered gradient circles, colored-edge cards,
  arrows) instead` and use the template's geometric vocabulary. Don't fail trying
  to rasterize icons.
- `diagram_pages` — **list every slide whose content is a structure (an architecture,
  a layering, a composition, a pipeline, a comparison-of-relationships), and commit to
  drawing it as a diagram, not a text list.** A page that reads as "5 rows of
  concept-name + description" is a missed diagram. See "The text-list-where-a-diagram-
  belongs" failure mode below.
- `storyline` — the **narrative contract**: `arc` (the beat order this deck follows,
  e.g. `纠偏→关键发现→定位→深入→战略→追问→应对→收尾`), `peak` (which slide is the
  signature-move peak, e.g. `6`), and `per_page` mapping `{page: {role, takeaway, leads_to}}`.
  This is the deck's "why this order" — commit to it at the design gate so the build
  doesn't drift into a page-N checklist. Every **content** slide must carry a
  `role` here; the cover/agenda/conclusion/appendix are structural.

### 2.5 Narrative self-check (before rendering)
At the design gate, verify the deck is a story, not a stack:
- Every content slide has a `role` in `storyline.per_page`; none is a bare "page N".
- No two **adjacent** slides share the same page-type (don't run 4-card → 4-card → 4-card).
- Every slide's speaker notes open with 承上→本页→启下 (use `deck_helpers.beat(…)`);
  if a page can't say what it's leading into, it's a loose end — fix the arc, not the copy.
- The `peak` slide is **led into and out of**: the page before sets up the mechanism and
  the page after draws its implication. A signature move with no pre-roll or follow-through
  is decoration.
- **Reduction test**: if you removed the `peak` slide, the core argument should no longer
  be fully explainable. If the story still survives, the peak isn't doing its job.

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

The build rhythm (proven, theme-independent): `dk.open_template(TPL)` → **`strip_branding(prs)`** (clear the template's inherited logo + copyright footers — see the "inherited template logo/branding" failure mode below) → **`cover(prs, D, subject, subtitle, meta, style=)`** for the designed cover (not bare placeholder-filling) → per content slide `add_slide(layout_idx)` → `set_title` → `dk.columns/rows/content_band` to get the
safe rect → `card` + `dk.text` + `num_circle` + `dk.bottom_callout` (or a page-type helper:
`quad_grid`/`steps3`/`code_card`/`text_right_card`) → optional
`Build.step()` for appear-builds on multi-step slides → `notes` / **`beat`** (speaker script — every single page opens with 承上→本页→启下 so the deck connects) →
`dk.lint_layout(prs, strict=True)` → `prs.save(OUT)`.

**Page-type helpers** (in `scripts/deck_helpers.py`, abstracted from real template
page skeletons — colors from profile, so re-theme changes all of them):
- `cover(...)` — designed cover, `band`/`hero` styles, gradient from profile, no logo.
- `quad_grid(slide, deck, items)` — 2×2 four-card (tab + head + body), for classifications.
- `steps3(slide, deck, steps)` — three vertical columns with Step-label header bands, for landing paths / phases.
- `code_card(slide, deck, left_title, left_body, code_title, code_lines)` — left prose + right dark code card.
- `text_right_card(slide, deck, left_title, left_body, right_title, right_body)` — left prose + right large card (architecture / scheme).

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

## The hard-coded brand-color drift (a real failure mode)

The first version of this skill's example build script hand-copied the template's theme
colors into Python constants at the top of the file: `RED = RGBColor(0xE6, 0x00, 0x2D)`
# copied from the template. That **silently drifts**: re-theme the template, or apply it
to a second template, and the hex stays frozen while the template moved — the deck
renders in last year's colors and nobody notices until it's on screen.

The fix (validated): `scripts/inspect_and_profile.py` reads the theme `clrScheme` straight
out of the `.pptx` and writes `profile.yaml`; `scripts/load_profile.py` injects those
colors into the build. **Never hand-copy a hex from the template into the build script.**
If you find yourself typing `RGBColor(0x..)`, stop — it belongs in `profile.yaml`, loaded
by `load_profile.load()`. The build script should say `D.anchor` / `D.comparator`, not a
raw hex. This also fixes the second template problem: `inspect_and_profile` on a new
`.pptx` regenerates the colors in one command, no edit-by-edit porting.

## The hard-coded slide-maker path (a real failure mode)

The build scripts import slide-maker's `deckkit` / `anim`. The first version hard-coded
one path — `~/.claude/skills/slide-maker/scripts` — which is **only correct on machines
that `npx skills`-installed slide-maker and got the symlink**. A colleague who
`git clone`d slide-maker to `~/.agents/`, or installed it per-project, hit
`ModuleNotFoundError: No module named 'deckkit'` the moment they ran the build — even
though `check_env` said slide-maker was present. The skill "worked on the author's
machine" and broke for real users: the textbook toy-vs-usable gap.

The fix (validated): `scripts/slide_maker_path.py`'s `find_slide_maker()` probes
`~/.claude`, `~/.agents`, `~/.codex` (and per-project) and returns the first dir that
actually contains `deckkit.py`. Build scripts call `sys.path.insert(0, find_slide_maker())`
**before** `import deckkit`. Never hard-code one skills-dir path — there are at least
three legitimate install locations and you don't know which your user used. (This also
matters for the **dependency-on-slide-maker** note in `SKILL.md` `## Install Source`:
state the dependency, but don't assume where it lives.)

## The chapter-page contrast (a real failure mode — you handle this, not chap)

Many corporate templates' chapter-divider layout (a full-bleed background image:
deep-red→orange gradient + dot-matrix) makes **white title text unreadable** in the
bright-orange dot regions — the page looks "empty" to the audience even though the
text is there.

**What `deck_helpers.chap` does and does NOT do:** `chap()` fills the template's
chapter-layout placeholders (idx0 title + idx10 subtitle) and tags CJK fonts — it
**does not draw a backing strip**. It trusts the template's own design language
(its placeholder is already positioned on the dark part of the background, where
white text reads). So on a *well-designed* template, `chap()` is enough.

**When the template is NOT well-designed** (white text genuinely unreadable on a
bright background), `chap()` will ship an unreadable divider — and that is a
**real failure mode you must handle yourself**, by drawing a semi-transparent
dark gradient backing strip behind the title in the build script:

```python
s = chap(prs, D, "chapter", "01", "标题", sub="...")
# 可选:模板章节页白字不可读时,手画半透明深色衬底条
dk.box(s, 0.5, 2.4, W_IN-1.0, 1.6,
       fill=RGBColor(0x00,0x00,0x00), round=True, r=0.08)
# (python-pptx 无原生透明度;用接近模板暗色的实色,或 deckkit 的半透明能力若有)
```

How to know you need it: **eyeball the chapter page's render after build.** If
white text is unreadable, it's a contrast problem, not a missing-content problem —
add the backing strip. `chap()` deliberately doesn't guess, because a strip on an
already-dark template would look wrong the other way. Treat it as: `chap()` lays
the text, you verify the render, you add backing only if the template needs it.

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
2. **Reserve enough bottom for the callout** — set the content block's `bottom` so its
   lowest edge (the card box) clears the callout top. With `bottom_callout_at(…,
   bottom_y=7.07)`, callout top ≈6.53, so `columns`/`rows` `bottom` ≥ ~1.25in on a 7.5in
   slide; `bottom≈0.75` or `0.95` is too tight. The box-on-callout overlap this causes
   is its own failure mode — see "The lint-blind box overlap" below; a text-only check
   won't catch it.

Do **not** shrink the content block so much that its own text overlaps (a too-tall
`bottom` compresses cards and the card's title/description text overlap each other —
also a `TEXT_OVERLAP`). The content block needs its real text height; reserve the
callout room by shortening the body, not by crushing the cards.

## The lint-blind box overlap (a real failure mode)

`lint_layout`'s `TEXT_OVERLAP` only fires on shapes that carry rendered **text** — it
compares text ink boxes. A `card` / `dk.box` with no `text_frame` (or whose text is in a
separate overlapping shape) is **invisible to that check**. So a card box that overhangs
a `bottom_callout`, or two boxes that overlap, passes lint clean — and you ship a deck
where a dark box sits on top of the callout band. This is exactly how slide 6/8 of the
reference deck broke: the content block's `bottom` was too small, the card box rendered
to 6.55–6.75in and overlapped the callout at 6.53in, but `TEXT_OVERLAP` saw nothing
because the box has no text.

The fix (validated):
- **When verifying, measure every shape's bottom — including boxes, not just text
  shapes.** A check that iterates `for sh in slide.shapes: if sh.has_text_frame` misses
  box overlaps. Iterate all shapes, take `sh.top + sh.height` as the bottom, confirm no
  non-callout shape's bottom crosses the callout's top (or any lower element's top).
  This is the only way to catch box-on-callout / box-on-box overlaps.
- **Reserve bottom by the box, not the text.** A card extends to its `bottom` param
  even if the text inside stops higher — set `bottom` so the *box* clears the callout,
  then confirm the text still fits inside the (now shorter) box.

Rule of thumb: **the render is the source of truth; lint is a safety net with blind
spots.** Eyeball every page's render after build — do not trust a green lint alone on
dense layouts.

## The callout floating-too-high fix (a visual-quality failure mode)

`dk.bottom_callout(x, w, …, footer_gap=0.15)` anchors above a `FOOTER_BAND=0.5in`
reserved zone, so its bottom lands at ~6.85in on a 7.5in slide — leaving ~0.65in of dead
space below it. The callout **doesn't collide with anything, but it reads as "floating"**
mid-lower-page, with uneven bottom margin. On a polished deck this looks unfinished.

The fix (validated against a hand-tuned reference slide): use
`deck_helpers.bottom_callout_at(slide, x, w, bottom_y, label, body)` — it anchors to an
**explicit bottom_y** (e.g. `7.07`), measuring the callout height and placing `y =
bottom_y - h`. This puts the callout's bottom edge where you want it (here ~0.43in from
the true bottom, snug above the footer band) and gives a consistent, even bottom margin
across every page that has a callout. Pair it with content blocks whose `bottom`
leaves ≥0.28in above the measured callout top (on the 7.07-anchor, callout top ≈6.53, so
content should end by ~6.25).

Prefer `bottom_callout_at` over `dk.bottom_callout` when you care about the *visual*
bottom margin — `bottom_callout` is correct (footer-safe) but visually conservative.
The even margin across pages is what makes a deck look designed, not auto-generated.

## The text-list-where-a-diagram-belongs (a real failure mode)

The cheapest way to put 5 concepts on a slide is 5 rows of "name + description" — and
it is almost always wrong. If the content is a **structure** (an architecture where
parts mount onto a container; a layering where layers stack and patch; a pipeline; a
comparison whose *relationship* is the point), a text list hides exactly the thing the
slide is there to show. The audience reads 5 parallel lines and never sees "plugins
mount onto ctx keys" or "layers stack and each can patch those below." The deck is
technically complete, visually lazy.

The fix (validated, on the reference deck's Cordis and plugin-tree slides):
- **At the design gate, flag every structure-content slide as a diagram.** List them
  in `diagram_pages` and commit to drawing the structure, not listing it.
- **Draw it with the geometric vocabulary**: a container box (`dk.box`) holding key
  slots, child cards (`card`) as the mountable units, `dk.connector(..., arrow=True)`
  lines from each slot to its unit to show the mount relationship; or a vertical stack
  of layer cards with `dk.arrow(..., direction='down')` between them to show stacking,
  and "← can patch below" labels on the patch-capable layers. `connector` (with
  `style='solid'|'dashed'|'dotted'`) carries edge semantics; `arrow` carries direction;
  `box`/`card` carry the nodes. This is real diagramming, not text-with-borders.
- **A text list is the fallback only when the items are genuinely parallel and
  independent** (e.g. "5 recommendations" — those ARE a list, not a structure). When in
  doubt, ask: "is the *relationship* between these the point?" If yes, draw it.

Rule of thumb: **if a reader could redraw the relationships from your slide, you drew
a diagram; if they can only read the items, you drew a list.** Training decks that
explain an architecture must pass the redraw test on the architecture slides.

> **选哪种图?** 见 `references/diagram-types.md` 的「内容形态→图类型」判别决策树 + 对照表。
> 尤其:有**分支/决策/多角色**的内容(用户流程、SSO 登录有 `?local=1` 分支)用**决策流程图**
> (deckkit `dk.node(shape="diamond")` 决策 + `shape="roundrect"` 起止 + `connect_boxes` 连线),
> **不要用 `steps3` 线性三步**——它画不出分支和泳道。拼装样板和两个 deckkit 坑(泳道不能
> fill、失败分支去终止节点别用 loop_path)见 `diagram-types.md` §user-flow-recipe。

## The inherited template logo/branding (a real failure mode)

`dk.open_template` keeps the template's **masters + layouts** (it only deletes slides) —
and many corporate templates carry the company **logo picture** (upper-right, ~1.0×0.32in)
and **copyright footer text** ("北京金山云网络技术有限公司 / WWW.KSYUN.COM / Copyright")
on those layouts. Every slide you add inherits them — so your deck ships with someone
else's brand on every page, which is exactly what a brand-clear skill must not do. This
was the previous version's bug: the build only filled placeholders and never touched the
inherited branding.

The fix (validated): call **`strip_branding(prs)`** once right after `open_template`,
before adding any slide. It walks every master + layout, removes pictures in the
upper-right region (position-based: `left > W*0.79 and top < H*0.13`, small size — so the
chapter page's large decorative background image is **not** removed, only small logos)
and removes text shapes containing brand keys (`金山云/KSYUN/Copyright/北京金山云网络技术/…`).
`keep_logo=True` skips it for the rare keep-branding case (an external-facing report on
that company's own template).

The companion fix: use **`cover(prs, D, subject, subtitle, meta, style=)`** instead of
filling the cover layout's placeholders. The template's cover layout *is* the logo page;
even after `strip_branding` it's an empty logo shell. `cover()` draws on the blank layout
instead — a designed cover (gradient band/bar + assertion title + story-line subtitle +
audience/date), colors from profile, no inherited brand. `band` (default, left bar +
left-aligned) or `hero` (big gradient block + centered).

Pair them: `prs = dk.open_template(TPL)` → `strip_branding(prs)` → `cover(prs, D, ...)`.
Eyeball the first slide's render after build — if a logo is still there, `strip_branding`
missed it (different canvas size / logo position) and you extend its detection thresholds.

## The cleared-placeholder prompt leak (a real failure mode)

A subtler inherited-branding bug: a build script clears a layout placeholder with
`placeholder.text = ""` (instead of filling or **deleting** it) and then draws its own
title text box beside it. The placeholder's *text* is empty, so a text-scanning lint sees
nothing — but an empty placeholder still **renders the layout/master's prompt text**
("点击添加页面大标题 30号", "Click to edit Master title style") as a grey dashed hint box.
The result: a hand-drawn title *and* the master's prompt on the same cover — exactly the
"完成度不足" defect.

🔴 **MUST — never clear a placeholder with `.text = ""`.** An empty placeholder renders the
layout's prompt. To hand-draw over a template layout, **delete the placeholder element**:
- `cover(prs, D, ...)` — draws on the blank layout (preferred; no inherited placeholders at all).
- `cover_from_template(prs, D, layout_role, drop_title=True)` — keeps the layout's background
  decoration, deletes the title placeholder element.
- `dk.drop_placeholders(slide, keep_idx=set())` — delete all inherited placeholders.
Or **fill** the placeholder (`set_title` / `chap` with `sub`). Never `.text = ""`.

The deterministic gate: **`check_template_placeholders(prs)`** before `save()` — it walks every
slide's placeholders, and for each *empty* one looks up the **same-idx placeholder on its layout**;
if that layout placeholder carries a non-empty user-visible prompt, it raises (covers, content
title, chapter subtitle — DATE/FOOTER/SLIDE_NUMBER chrome are excluded). Wording-agnostic and
template-agnostic, so it catches `点击添加…` / `Click to edit…` / any future prompt phrasing.
The `new_deck.py` scaffold already calls it; add it to hand-written build scripts too.

## What Stage 3 does NOT do
- Re-investigate (Stage 1) or re-structure the argument (Stage 2) — it projects the
  already-verified doc onto slides.
- Embed an internal/copyrighted template — the user supplies the `.pptx`; the skill
  ships only a sanitized example profile, never a real company template.
- Re-implement deckkit/anim/render/lint — it imports slide-maker. If slide-maker
  isn't installed, Stage 3 stops at "install slide-maker"; Stages 1–2 still work.
