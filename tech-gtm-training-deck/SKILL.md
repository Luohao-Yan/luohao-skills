---
name: tech-gtm-training-deck
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

## Stage 0 — Brief (interview before investigating)

Before touching the source, **interview the user** so the deck's audience, depth,
page count, and presentation choices are decided up-front, not guessed. This is
the part the old version skipped — and it is what makes a deck land for *this*
audience vs. a generic one.

Run **3 rounds** of `AskUserQuestion` (the tool caps at 4 questions/round, 2-4
options each). **Every item has a default** — the user can skip any round and the
pipeline still runs. The interview is a chance to lock direction, not a gate.

**Round 1 — direction** (4 questions)
- *主题偏向 (tilt)*: 技术深度 / 高层愿景 / 平衡 — default 平衡(balanced)
- *受众 (audience)*: 公司领导 / 技术团队 / 客户 / 混合 — default 公司领导(leaders)
- *语言 (language)*: 中文 / 英文 / 双语 — default 中文(zh)
- *模板来源 (template)*: 指定路径 / 用默认池(推荐) / 不用模板 — default 用默认池(auto)

**Round 2 — skeleton** (4 questions)
- *核心目的/故事线 (purpose)*: 自由文本(讲完记住/拍板什么) — default 由主题推导一句
- *目标页数 (pages)*: 10-15 / 15-20 / 20+ — default 15-20
- *内容侧重 (emphasis)*: 战略 / 架构 / 对比 / 操作 / 数据 / 平衡 — default 平衡(balanced)
- *准确度与讲稿 (fidelity)*: 保留 file_path:line 证据 / 简化 / 极简 — default 保留证据(traced)

**Round 3 — presentation + confirm** (2 questions)
- *是否要动画 (animation)*: 要 appear-build / 静态 — default 要(true)
- *访谈小结确认*: 把推导的 brief 摘要展示(含 need_arch_diagram 由 tilt 推导),选项 确认开始 / 我要改某项 — default 确认开始

> `need_arch_diagram` 不单列成题——由 `tilt` 推导(tilt=tech→true,否则 false),在轮 3 确认题里展示给用户,可改。`need_network_topo` 默认 false,若用户在轮 2 提到网络拓扑或调研内容含网络/部署拓扑,由 Stage 1/2 置 true。

**Product**: write `brief.yaml` to `<outdir>/brief.yaml` (13 fields). Use
`scripts/brief.py`:
```python
import sys, os
sys.path.insert(0, os.path.join("<tech-gtm-training-deck>", "scripts"))
import brief
data = brief.merge_with_defaults(answers_from_3_rounds)  # 缺失字段兜底
brief.write_brief(data, os.path.join(data["outdir"], "brief.yaml"))
```
brief.yaml fields: `subject / tilt / audience / purpose / pages / animation / template / language / emphasis / fidelity / need_arch_diagram / need_network_topo / outdir`. See `scripts/brief.py` `DEFAULTS` for exact values.

**Downstream stages read brief.yaml** — Stage 1 reads `tilt/audience/purpose/emphasis`
to scope the investigation; Stage 2 reads `pages/emphasis/fidelity` for doc
skeleton & evidence retention; Stage 3 reads `animation/template/language` +
`need_arch_diagram/need_network_topo` to decide deck params and which figures
to draw. If a field is missing, `brief.load_brief` falls back to defaults
(never error) — see `scripts/brief.py`.

## The four stages (this is the whole skill)

| Stage | What it does | Where the method lives |
|---|---|---|
| **0. Brief** | Interview the user (3 rounds, all defaults skippable) → write `brief.yaml` (audience/tilt/pages/animation/template/language/emphasis/fidelity + need_arch_diagram/need_network_topo). Drives every later stage. | this file §Stage 0; `scripts/brief.py` |
| **1. Investigate** | Read the source to line-level (local code, installed apps, public info); never fabricate; attach `file_path:line` to every claim. | `references/investigate.md` |
| **2. Training doc** | Turn the investigation into a structured training `.md` (TL;DR → what is it → how it works → object inventory → why it matters → comparison → recommendations → evidence appendix). | `references/training-doc.md` |
| **3. Deck from template** | Turn the doc + the user's `.pptx` template into a brand-consistent deck, via the **slide-maker** skill: inspect → profile → design gate → build → render → critic (2 rounds) → fix → gate(waived) → deliver. | `references/deck-from-template.md` |

The four stages (Brief → Investigate → Training doc → Deck) are one pipeline and one mind's job — the Brief stage is up-front, the other three are the through-line. Do not split a single
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
npx skills add <your-github-user>/tech-gtm-training-deck -g -y
#   or, before publishing:  git clone <repo> ~/.claude/skills/tech-gtm-training-deck/

# 3. verify + install python deps
python check_env.py
pip install -r requirements.txt
```

`check_env.py` reports what's missing (slide-maker present? python-pptx? PyYAML?
LibreOffice for rendering?) and prints the exact fix command per OS. It only
reports — it never auto-installs.

## Default template pool

When the user picks `template: auto` (the default in Stage 0), the skill inspects
the **first existing** of these two templates to derive `profile.yaml`. They are
the same brand style (金山云 red-accent 政企 template: accent1 #E6002D, 微软雅黑,
13.333×7.5, identical layout roles), so no tilt-based picking — first-available wins.

```
默认模板池(同风格,template=auto 时取首个可用者):
  1. C:\Users\KC\orca\projects\Pre-seles-architect-scheme\output\deepseek-harness培训\DeepSeek-Harness能力培训.pptx
  2. C:\Users\KC\Documents\AI热点技术培训 - 智能体记忆系统v1.0.pptx
```

If neither exists, fall back to `template: none` (slide-maker designs from scratch)
and tell the user "未找到默认模板，已用内置风格". These paths are **this author's
machine defaults** — forkers should edit this list to their own brand templates.
The list lives here (not in code) so it's easy to edit without touching Python.

## Overview routing (where things live)

| Concern | Route to |
|---|---|
| Stage 1 method (source tiers, evidence trace, attribution correction, parallel investigation) | `references/investigate.md` |
| Stage 2 method (7-section doc skeleton, honest-limit pairing, evidence appendix) | `references/training-doc.md` |
| Stage 3 method (template branch: inspect→profile→design gate→build→render→critic→gate→deliver; gate+waiver; **7 real failure modes**: brand-color drift, hard-coded slide-maker path, chapter-page contrast, bottom_callout overlap, callout floating-too-high, lint-blind box overlap, text-list-where-a-diagram-belongs) | `references/deck-from-template.md` |
| **Reusable deck编排样板** (color semantic contract for any accent → page-type sequence → signature move pattern → visual vocabulary; brand-cleared, for high-density training decks) | `references/deck-reference-layout.md` |
| Stage-to-stage handoff; what's mechanical vs. needs human judgment | `references/workflow.md` |
| Stage 0 product: read/write `brief.yaml` + defaults | `scripts/brief.py` |
| Layered architecture diagram helper (`arch_layers`) | `scripts/deck_helpers.py` |
| Network topology diagram helper (`network_topo`, with built-in `assets/icons/`) | `scripts/deck_helpers.py` |
| Inspect a user `.pptx` → emit `profile.yaml` + `profile.md` | `scripts/inspect_and_profile.py` |
| Load `profile.yaml` into build-time color/font constants (no hand-copied hex) | `scripts/load_profile.py` |
| Reusable deck helpers (set_title / num_circle / chap / card / notes), colors from profile | `scripts/deck_helpers.py` |
| Scaffold a new build script from a profile + page outline | `scripts/new_deck.py` |
| A ready-to-edit build skeleton (reads profile.yaml, not hard-coded) | `templates/build_skeleton.py` |
| A full worked example (investigation → doc → deck), sanitized | `examples/deepseek-harness/` |

When the overview table doesn't route a concern, read `references/workflow.md` first
(the stage handoff), then the specific stage reference.

## Figure helpers — when to draw architecture / topology

Two helpers in `scripts/deck_helpers.py` cover the technical-depth figures this
skill previously couldn't draw:

- **`arch_layers(slide, layers, ...)`** — layered architecture diagram (full-width
  color bands + component blocks, alternating tints). Draw it when
  `brief.need_arch_diagram is True` (i.e. `tilt=tech` unless overridden) AND the
  doc's "how it works / architecture" section has architecture content. One page.
- **`network_topo(slide, nodes, links, ...)`** — network topology (icon nodes +
  edge-to-edge connectors, no line crosses a node). Draw it when
  `brief.need_network_topo is True` OR the doc covers network/deploy topology.
  Icons come from the built-in `assets/icons/` (offline, no Chrome needed at runtime).

Both reuse slide-maker's deckkit (`node`/`connect_boxes`/`box`) — colors/fonts come
from `profile.yaml` via `deck_helpers.Deck`. See `scripts/deck_helpers.py` for
signatures and `tests/test_arch_layers.py` / `tests/test_network_topo.py` for usage.
