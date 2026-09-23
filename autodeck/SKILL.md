---
name: autodeck
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

Before touching the source, **lock the deck's audience, depth, page count, and
presentation choices up-front, not by guessing**. Stage 0 produces `brief.yaml`,
the contract every later stage reads. Two modes — pick by whether a human is in
the loop:

- **Interactive mode (a human is in the loop)** — run the `AskUserQuestion`
  interview below. Ask **only the fields the user hasn't already supplied**
  (a pre-filled `brief.yaml` or prior answers count as supplied). Every item has
  a default, so the user can skip any round and the pipeline still runs. The
  interview is a chance to lock direction, not a gate.
- **Unattended mode (no human: cron / loop / SDK / "don't ask me")** — **do not
  call `AskUserQuestion` at all**; `AskUserQuestion` blocks forever with no one
  to answer. Instead build the brief from existing answers + defaults only.
  When to use unattended is decided by an **explicit signal**, never inferred:
  the user says "无人值守 / 后台跑 / 不要问我", or `brief.yaml` already exists
  (= "answers already given"), or the run is from `/loop`/cron/SDK. Never silently
  downgrade a deck the user thinks is being tailored.

Both modes go through the same pure function so the "ask / don't ask" decision
is code, not agent improvisation:

```python
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))          # 这段脚本所在目录
# autodeck/scripts(本 skill 的 scripts):
SKILL_SCRIPTS = os.path.join(HERE, "..", "scripts") if os.path.isdir(
    os.path.join(HERE, "..", "scripts")) else os.path.join(os.path.expanduser("~"),
    ".claude", "skills", "autodeck", "scripts")
sys.path.insert(0, SKILL_SCRIPTS)
import brief

# 交互:有人在 → interactive=True,传一个调 AskUserQuestion 的 asker(见下「轮次编排」)
# 无人:interactive=False,asker 不传 → 全默认 + existing 直入,绝不 hang
data = brief.stage0_brief(subject, existing=prior_answers,
                          interactive=not UNATTENDED, asker=asker)
brief.write_brief(data, os.path.join(data["outdir"], "brief.yaml"))
```

`stage0_brief(subject, existing, interactive, asker)` is the single entry point:
- `interactive=False` → never calls `asker` (unattended).
- `asker=None` (caller forgot / can't ask) → never calls `asker`, falls back to
  defaults (safety net — no hang, no crash).
- `interactive=True` with an `asker` → calls `asker(missing_fields)` **once**, only
  for fields `existing` didn't supply; nothing missing → doesn't call.
Every path finally passes `merge_with_defaults`, so `need_arch_diagram` derives
from `tilt`, `purpose`/`outdir` derive from `subject`, explicit values win, and
missing fields fall back — never error. See `scripts/brief.py`.

### The interview (interactive mode — ask only what isn't already filled)

Run `AskUserQuestion` in rounds (the tool caps at 4 questions/round, 2-4 options
each). The 4 default-skippable rounds below are the **full question set**; in
unattended mode none of these run, and in interactive mode you **skip any
question whose answer `existing` already supplies**. Group the still-missing
fields into rounds of ≤4 and ask; if everything's already filled, skip the
interview entirely.

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

### Unattended mode — what changes downstream (the implicit-confirm rule)

When you ran Stage 0 unattended, **no human is coming back to confirm**. Two
later stages have implicit "ask the user" steps that would hang — both must
degrade, not block:

- **Stage 1 attribution ambiguity** (e.g. "is the user's 'X' the same as product
  Y?"): in interactive mode this is a user-confirm; in unattended mode **take the
  most conservative reading and mark it** — write "此项存疑，未与用户确认" in the
  doc rather than stopping to ask. A labeled gap is honest; a blocking question
  with no answer is a hang. See `references/investigate.md`.
- **Stage 3 critic verdict + waiver**: the "you judge consent" step is a human
  call; in unattended mode **default to the `density.waived` path** (record the
  waiver reason, never block) and at deliver **flag prominently that the deck is
  machine-produced, unrevised by a human critic** so the receiver knows to spot-check.
  Never ship a machine-only deck silently. See `references/workflow.md`.

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
| **0. Brief** | Lock audience/tilt/pages/animation/template/language/emphasis/fidelity + need_arch_diagram/need_network_topo + storyline (叙事合同) into `brief.yaml` (14 fields). **Interactive**: AskUserQuestion interview, ask only unfilled fields, all defaults skippable. **Unattended**: no interview — `stage0_brief(interactive=False)` builds from existing + defaults, never hangs. Drives every later stage. See §Storyline below for how the story arc is derived and flows to Stage 2/3. | this file §Stage 0; `scripts/brief.py` `stage0_brief` |
| **1. Investigate** | Read the source to line-level (local code, installed apps, public info); never fabricate; attach `file_path:line` to every claim. | `references/investigate.md` |
| **2. Training doc** | Turn the investigation into a structured training `.md` (TL;DR → what is it → how it works → object inventory → why it matters → comparison → recommendations → evidence appendix). | `references/training-doc.md` |
| **3. Deck from template** | Turn the doc + the user's `.pptx` template into a brand-consistent deck, via the **slide-maker** skill: inspect → profile → design gate → build → render → critic (2 rounds) → fix → gate(waived) → deliver. Build rhythm is **narrative-mandatory**: every page's speaker notes open with 承上→本页→启下 (use `beat()`), and the page order follows the storyline arc — never a "page N" checklist. See §Storyline below. | `references/deck-from-template.md` |

The four stages (Brief → Investigate → Training doc → Deck) are one pipeline and one mind's job — the Brief stage is up-front, the other three are the through-line. Do not split a single
subject's investigation/document/deck across blind agents. Fan out only across
*independent* investigation lines (different source types), then synthesize back
into one mind before the doc. See `references/workflow.md` for the stage-to-stage
handoff and which steps are mechanical vs. need human judgment.

## Storyline (叙事合同) — how decks get 上下承接

A deck feels "硬凑" when the arc lives nowhere structural — `content页1/2/3` scaffolding and
a one-line `purpose` can't carry a narrative. So the pipeline makes the story a **first-class
data structure** (`storyline` in `brief.yaml`) and the design gate + build rhythm **enforce**
it. The whole through-line:

- **Stage 0/2 — derive the storyline.** `storyline` is *not* part of the 4-round interview (keeps
  unattended runs from hanging). The agent writes it into `brief.yaml` while researching/writing
  the training doc, from `subject/emphasis/tilt/audience`. If the user already supplied a
  `storyline`, merge + prefer theirs. Shape:
  ```yaml
  storyline:
    arc:  纠偏 → 关键发现 → 定位 → 深入(架构/机制) → 战略 → 追问 → 应对 → 收尾
    peak: 6                       # signature move 峰值页(机制/比喻那页)
    beats:
      - { page: 3, role: "hook纠偏",  takeaway: "别再混为一谈",  from: "封面承诺", to: "关键发现" }
      - { page: 6, role: "深入机制",  takeaway: "Agent=模型+Harness", from: "定位",   to: "战略" }
      # ... 每页一个 beat:role/一句话takeaway/承上(from)/启下(to)
  ```
  `purpose` stays a one-line cover subtitle (unchanged, backward-compatible).
- **Stage 3 — generate the narrative scaffold.** `new_deck.py` no longer emits `内容页N`;
  it emits the approved arc page order (封面→目录→钩子·纠偏→关键发现→定位→深入·机制→
  战略→追问→应对→总结→结论→附录), each stub pre-filled with 承上/本页/启下 notes. See
  `references/deck-reference-layout.md` §页型编排骨架.
- **Stage 3 — every page carries 承上→本页→启下.** Use `deck_helpers.beat(slide, point,
  carried_from=..., leads_to=...)` so the transition is written into the speaker notes, not
  left implicit. This is a mandatory build step (like `strip_branding`/`cover`), not optional.
- **Design gate — check the narrative, not just density.** `.deck-gates.json` carries a
  `storyline` block (arc/peak/beats); critic self-check verifies each page has a role, no two
  adjacent pages share a page-type, every page's notes state 承上/启下, and the peak page is
  led into/out of by structure diagrams. See `references/deck-from-template.md` §design gate.

**Why this order sells**: 先立主张(封面/钩子) → 给硬证据(关键发现) → 给判断(定位) →
深入机制让"为什么可信"(peak) → 落到我们能做什么(战略) → 替听众先把异议问出来(追问) →
给路(应对) → 收回到最初承诺(结论). Each beat answers the one the previous page just raised.

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
npx skills add <your-github-user>/autodeck -g -y
#   or, before publishing:  git clone <repo> ~/.claude/skills/autodeck/

# 3. verify + install python deps
python check_env.py
pip install -r requirements.txt
```

`check_env.py` reports what's missing (slide-maker present? python-pptx? PyYAML?
LibreOffice for rendering?) and prints the exact fix command per OS. It only
reports — it never auto-installs.

## Template pool & brand-less palettes

The `template` field (set in Stage 0) resolves via `scripts/template_pool.py`:

| `template` 值 | 行为 |
|---|---|
| `auto` (default) | 取默认池首个存在的 `.pptx` |
| `<style 名>` (如 `red-gov`) | 取池中该风格名对应的 `.pptx` |
| `builtin:<名>` (如 `builtin:slate-business`) | 不用 `.pptx`,用 `scripts/builtin_palettes.py` 的内置无品牌配色 |
| `<路径>` | 该 `.pptx`(存在与否交给 inspect 报错) |
| `none` | None(slide-maker 从零设计) |

```
默认模板池(forker 改自己机器的模板路径 + 在 template_pool.STYLES 起风格名):
  red-gov:     .../deepseek-harness培训/DeepSeek-Harness能力培训.pptx
  red-gov-mem: C:\Users\KC\Documents\AI热点技术培训 - 智能体记忆系统v1.0.pptx
内置无品牌配色(scripts/builtin_palettes.py,template=none/builtin: 时用):
  slate-business  藏青商务(深藏青+琥珀+金)
  ink-data        深墨数据(深墨蓝+青+橙)
```

These paths are **this author's machine defaults** — forkers should edit the list in
`scripts/template_pool.py` (`DEFAULT_POOL` + `STYLES`) to their own brand templates, and
can add built-in palettes in `scripts/builtin_palettes.py`. The list lives in code (not
this doc) so it's one place to edit.

**Branding is stripped automatically**: `strip_branding(prs)` runs right after
`open_template`, removing inherited logo pics + copyright footers from every layout (see
`## Cover & branding` below). So even `auto` no longer ships the template's 金山云 logo.
If you genuinely need to keep a template's branding (e.g. an external-facing report on
that company's own template), pass `keep_logo=True` — otherwise default is brand-cleared.

## Cover & branding

Two things the old version got wrong, both fixed in `scripts/deck_helpers.py`:

- **`cover(prs, deck, subject, subtitle, meta, style=)`** — a *designed* cover (not bare
  placeholder-filling). `band` (left gradient bar + left-aligned title) is the default;
  `hero` (big gradient block + centered) for vision decks. Pulls `subject` as a
  one-line assertion, `subtitle` as the story-line from `brief.purpose`, `meta` as
  audience+date. Colors + gradient from profile (`anchor`/`comparator`), no template logo.
- **`strip_branding(prs, keep_logo=False)`** — call once after `open_template`, before
  adding any slide. Removes logo pictures (detected by position: upper-right region on a
  13.33×7.5 canvas) and brand-text shapes (含 金山云/KSYUN/Copyright/北京金山云网络技术)
  from every master + layout. Big decorative background images (e.g. chapter-page art)
  are NOT removed — only small upper-right logos + copyright footers. `keep_logo=True`
  skips it for the keep-branding case.

Build skeleton (`templates/build_skeleton.py`) calls both: `strip_branding(prs)` then
`cover(...)`. See `deck-from-template.md` §failure-modes for the "inherited template
logo/branding" failure mode this fixes.

## Overview routing (where things live)

| Concern | Route to |
|---|---|
| Stage 1 method (source tiers, evidence trace, attribution correction, parallel investigation) | `references/investigate.md` |
| Stage 2 method (7-section doc skeleton, honest-limit pairing, evidence appendix) | `references/training-doc.md` |
| Stage 3 method (template branch: inspect→profile→design gate→build→render→critic→gate→deliver; gate+waiver; **8 real failure modes**: brand-color drift, hard-coded slide-maker path, chapter-page contrast, bottom_callout overlap, callout floating-too-high, lint-blind box overlap, text-list-where-a-diagram-belongs, **inherited template logo/branding**) | `references/deck-from-template.md` |
| **Reusable deck编排样板** (color semantic contract for any accent → page-type sequence → signature move pattern → visual vocabulary; brand-cleared, for high-density training decks) | `references/deck-reference-layout.md` |
| Stage-to-stage handoff; what's mechanical vs. needs human judgment | `references/workflow.md` |
| Stage 0 product: read/write `brief.yaml` + defaults | `scripts/brief.py` |
| Layered architecture diagram helper (`arch_layers`) | `scripts/deck_helpers.py` |
| Network topology diagram helper (`network_topo`, with built-in `assets/icons/`) | `scripts/deck_helpers.py` |
| Inspect a user `.pptx` → emit `profile.yaml` + `profile.md` | `scripts/inspect_and_profile.py` |
| Load `profile.yaml` into build-time color/font constants (no hand-copied hex) | `scripts/load_profile.py` |
| Reusable deck helpers (set_title / num_circle / chap / card / notes), colors from profile | `scripts/deck_helpers.py` |
| **Narrative beat helper** (`beat(slide, point, carried_from, leads_to)` — writes 承上/本页/启下 into every page's notes) | `scripts/deck_helpers.py` |
| **Narrative-role scaffold** (`new_deck.py` emits 封面→钩子·纠偏→关键发现→定位→深入→战略→追问→应对→结论→附录, no more `内容页N`) | `scripts/new_deck.py` |
| **Storyline contract** (`storyline` block in brief.yaml: arc/peak/beats + 承上启下 per page; drives design gate + scaffold) | `scripts/brief.py`; `references/deck-reference-layout.md` §页型编排骨架 |
| **Designed cover** (`cover()`, band/hero styles, gradient, no template logo) | `scripts/deck_helpers.py` |
| **Strip template branding** (`strip_branding()`, removes inherited logo pics + copyright footers) | `scripts/deck_helpers.py` |
| **Content page-type helpers** (`quad_grid` 2×2 / `steps3` 三步走 / `code_card` 左文右代码 / `text_right_card` 左文右图) | `scripts/deck_helpers.py` |
| **Diagram type selection** (内容形态→图类型判别表 + user-flow recipe + 标准符号;有分支/决策/多角色用决策流程图 NOT steps3) | `references/diagram-types.md` |
| Layered architecture diagram helper (`arch_layers`) | `scripts/deck_helpers.py` |
| Network topology diagram helper (`network_topo`, with built-in `assets/icons/`) | `scripts/deck_helpers.py` |
| Template pool (multi-style `.pptx`) + resolve `template` field (`auto`/style-name/`builtin:`/path/`none`) | `scripts/template_pool.py` |
| Built-in brand-less palettes (slate-business / ink-data; for `template=none`/`builtin:`) | `scripts/builtin_palettes.py` |
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

### `arch_layers` — three optional args for branded/gov formal diagrams

`arch_layers` gained three optional args (all default off → original behavior
unchanged). Use them when a branded or government-formal architecture diagram is
needed, not for a generic colorful stack:

- **`style="ksyun"`** — 金山云品牌红配色:色带用浅红 `#FDECEE`,组件描边用主红
  `#C8102E`,公文正式调性(不分层花色)。`accent` 不传时自动用金山云红;传别的色
  可覆盖。源自从上海广电立项书架构图实践沉淀的品牌一致需求。
- **`sidebar=True | list | None`** — 右侧安全合规侧栏。`True`=用内置 9 项默认
  (`ARCH_SIDEBAR_DEFAULT`:数据不出局/信创合规/UIAP/ RBAC/国密/脱敏/敏感词/审计/全链路);
  传 list 用自定义条目;`None`=不画。有侧栏时主图自动收窄 1.7 inch 让位。
- **`show_arrows=True`** — 层间自下而上支撑箭头(层名左侧实心上指箭头,用
  `deckkit.arrow(direction="up")`)。政务架构图常需表达"逐层支撑"语义。

**三件套组合**(上海广电立项书场景):
```python
arch_layers(s, layers, x=0.4, y=1.2, w=12.5, total_h=5.6,
            style="ksyun", sidebar=True, show_arrows=True)
```

### `arch_layers` — 画图经验沉淀(非显而易见的坑)

- **deckkit `box` 不支持 `dash` 虚线**(签名无该参数)。侧栏想表"虚线区分"用
  实线细边框 + 浅色底,别传 `dash=`,否则 `TypeError`。
- **层间箭头别用 `connect_boxes`**——它会吸附到最近的组件块边缘,箭头会斜穿过
  组件而不是画在空白处。用 `deckkit.arrow(direction="up")` 画实心块箭头,放在
  层名左侧空白区(x+0.12),不与组件冲突。
- **视觉自检不可省**:`pytest` 只验证"不抛错",**不验证视觉正确**。改 `arch_layers`
  画法后,必须生成真实 `.pptx` → LibreOffice 转 PNG → 肉眼核对色带/箭头/侧栏/
  中文位置正确。曾出现"测试全过但箭头穿过组件"的视觉 bug,只有渲染看图才发现。
  见 `tests/test_arch_layers.py` 末尾 `test_arch_layers_ksyun_full_combo_renders`。

### Figure helpers — when NOT to use them (内容形态 → 图类型)

`arch_layers` 和 `network_topo` 只覆盖**两种**图(分层架构、网络拓扑)。其余内容形态——
**用户流程/决策流、时序、状态机、数据管道、前后对比、循环**——的选型和画法见
`references/diagram-types.md`。

**关键判别**:内容有**分支/决策点**(if-else、成功失败、`?local=1 走本地`)或**多角色各走各路径**
时,用**决策流程图**(deckkit `dk.node(shape="diamond")` 决策 + `shape="roundrect"` 起止 +
`connect_boxes` 主线 + 失败分支去终止节点),**NOT `steps3`**——`steps3` 是线性三列说明,
画不出分支、决策菱形、起止、泳道,把流程内容压成三段会丢掉「流程」的灵魂。判别口诀和拼装
样板见 `diagram-types.md` §user-flow-recipe(引用 slide-maker 的 `design-gallery.md:157-174`
recipe + 标准符号,不重造)。
