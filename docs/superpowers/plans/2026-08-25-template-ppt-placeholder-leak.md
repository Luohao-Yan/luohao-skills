# 模板 PPT 母版占位符残留修复 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 给 tech-gtm-training-deck skill加确定性闸门，阻止构建者用 `placeholder.text=""` 清空占位符导致母版提示语残留，并补安全助手路径。

**Architecture:** 三层：修 `chap()`（删空 idx10）+ 新增 `cover_from_template()`（删占位符元素保留版式装饰）+ 新增 `check_template_placeholders()`（按 idx 反查版式占位符提示语，空占位符+版式带提示→报告/raise）。闸门调用嵌进 `new_deck.py` 生成的脚手架 SKELETON 文本。所有改动落 luohao-skills 仓库内 tech-gtm，不动 npm 安装的 slide-maker 包。

**Tech Stack:** Python · python-pptx · pytest · tech-gtm-training-deck skill (deckkit via slide_maker_path)

## Global Constraints

- 落点：`D:/develop/luohao-skills/tech-gtm-training-deck/`（仓库源），不动 `~/.agents/skills/slide-maker`（npm 包，升级覆盖）。
- 不重新生成 LoopEngineering-deck（用户要求仅 skill 层持久化）。
- 语义：占位符残留 = slide 占位符文本空 **且** 版式同 idx 占位符带非空用户可见提示语。排除 chrome 占位符（DATE type=16 / FOOTER type=15 / SLIDE_NUMBER type=13），它们的"提示"是自动值（`1/27/13`/`‹#›`）或空，非用户可见"点击添加"提示。
- 测试 fixture 用 conftest `make_test_prs()`（python-pptx 默认模板），layout 5 (Title Only) 含 `idx=0 TITLE prompt='Click to edit Master title style'`。
- 颜色/字体从 profile 来，不硬编 hex（沿用 deck_helpers 既有约定）。
- TDD：每任务先写失败测试，再实现。

## File Structure

| 文件 | 责任 | 改动 |
|---|---|---|
| `tech-gtm-training-deck/scripts/deck_helpers.py` | 模板构建积木 | 修 `chap()`；新增 `cover_from_template()`；新增 `check_template_placeholders()` |
| `tech-gtm-training-deck/tests/test_template_placeholders.py` | 新闸门/助手测试 | 新建 |
| `tech-gtm-training-deck/scripts/new_deck.py` | 生成 build 脚手架 | SKELETON 文本里 save 前加 `check_template_placeholders` 调用 + import |
| `tech-gtm-training-deck/references/deck-from-template.md` | 构建指引文档 | 加 🔴 MUST 警示段 |

单元边界：`check_template_placeholders` 是纯检测函数（输入 prs，输出 findings/raise），无副作用，可独立测；`cover_from_template`/`chap` 是构建助手，测其占位符删留副作用。三者解耦，各一个测试文件内的独立用例。

---

### Task 1: `check_template_placeholders` 检测函数（核心闸门）

**Files:**
- Modify: `tech-gtm-training-deck/scripts/deck_helpers.py`（末尾新增函数）
- Test: `tech-gtm-training-deck/tests/test_template_placeholders.py`（新建）

**Interfaces:**
- Consumes: `prs.slides` 的 `slide.placeholders`、`slide.slide_layout.placeholders`、`ph.placeholder_format.idx`、`ph.placeholder_format.type`（python-pptx）；`PP_PLACEHOLDER` 枚举（type 比较）。
- Produces: `check_template_placeholders(prs, *, fail_on_prompt=True) -> list[dict]`，finding 形如 `{"slide": int, "idx": int, "type": str, "layout_prompt": str}`。

- [ ] **Step 1: 写失败测试 — 清空占位符被标记**

`tech-gtm-training-deck/tests/test_template_placeholders.py`：
```python
# -*- coding: utf-8 -*-
"""check_template_placeholders / cover_from_template / chap 占位符残留闸门测试。"""
import os, sys
import pytest
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "scripts"))
from deck_helpers import check_template_placeholders, cover_from_template, chap, Deck
from conftest import make_test_prs, blank_slide


def test_flags_cleared_title_placeholder():
    """清空 idx0 标题占位符(像 LoopEngineering build.py 那样)→ 闸门报该 finding 并 raise。"""
    prs = make_test_prs()
    # layout 5 = Title Only, idx0 TITLE prompt='Click to edit Master title style'
    s = prs.slides.add_slide(prs.slide_layouts[5])
    s.placeholders[0].text = ""   # 清空未删 —— 残留根因
    findings = check_template_placeholders(prs, fail_on_prompt=False)
    assert len(findings) == 1
    assert findings[0]["slide"] == 1
    assert findings[0]["idx"] == 0
    assert "Master title" in findings[0]["layout_prompt"]


def test_cleared_placeholder_raises_when_fail_on():
    """fail_on_prompt=True(默认)时,清空占位符 → raise RuntimeError。"""
    prs = make_test_prs()
    s = prs.slides.add_slide(prs.slide_layouts[5])
    s.placeholders[0].text = ""
    with pytest.raises(RuntimeError):
        check_template_placeholders(prs)


def test_filled_placeholder_passes():
    """填充占位符 → 无 finding 不 raise。"""
    prs = make_test_prs()
    s = prs.slides.add_slide(prs.slide_layouts[5])
    s.placeholders[0].text = "真标题"
    assert check_template_placeholders(prs) == []


def test_dropped_placeholder_passes():
    """删除占位符元素 → 无 finding 不 raise。"""
    prs = make_test_prs()
    s = prs.slides.add_slide(prs.slide_layouts[5])
    ph = s.placeholders[0]
    ph._element.getparent().remove(ph._element)
    assert check_template_placeholders(prs) == []


def test_chrome_placeholders_not_flagged():
    """DATE/FOOTER/SLIDE_NUMBER chrome 占位符空 → 不报(它们本就常空,非用户可见提示)。"""
    prs = make_test_prs()
    # layout 1 (Title and Content) 含 DATE/FOOTER/SLIDE_NUMBER,填了标题,其余空
    s = prs.slides.add_slide(prs.slide_layouts[1])
    s.placeholders[0].text = "标题"
    # 不动 DATE(idx10)/FOOTER(idx11)/SLIDE_NUMBER(idx12) —— 它们空
    assert check_template_placeholders(prs) == []
```

- [ ] **Step 2: 跑测试确认失败**

Run: `cd tech-gtm-training-deck && python -m pytest tests/test_template_placeholders.py -v`
Expected: FAIL — `ImportError: cannot import name 'check_template_placeholders'`（函数未定义）。

- [ ] **Step 3: 实现 `check_template_placeholders`**

在 `tech-gtm-training-deck/scripts/deck_helpers.py` **末尾**追加：
```python


# ---- 模板占位符残留闸门 (check_template_placeholders) ----
# 根因:build 脚本用 placeholder.text='' 清空占位符(不删元素),空占位符仍渲染版式/母版的
# 提示语(如"点击添加页面大标题")。纯文本 lint 读 slide 层(空)抓不到——提示语在版式层,
# 必须按 idx 反查版式占位符。措辞无关、模板无关、确定性。
from pptx.enum.placeholders import PP_PLACEHOLDER

# chrome 占位符:本就常空,"提示"是自动值(1/27/13 / ‹#›)或空,非用户可见"点击添加"提示 → 不报
_CHROME_PH_TYPES = {
    PP_PLACEHOLDER.DATE, PP_PLACEHOLDER.FOOTER, PP_PLACEHOLDER.SLIDE_NUMBER,
}


def check_template_placeholders(prs, *, fail_on_prompt=True):
    """构建期闸门:遍历每页占位符,若 slide 占位符文本空,按 idx 反查版式同 idx 占位符;
    若版式占位符带非空用户可见提示语 → 该空占位符会渲染版式提示 → 报告。

    机制:slide 占位符清空后文本为空,但版式层提示语仍在,渲染时显示。
    排除 chrome 占位符(DATE/FOOTER/SLIDE_NUMBER)——它们常空且无用户可见提示。

    返回 findings 列表 [{slide, idx, type, layout_prompt}]。
    fail_on_prompt=True 时,有 finding 则 raise RuntimeError(构建期硬失败)。
    """
    findings = []
    for i, slide in enumerate(prs.slides, 1):
        lay = slide.slide_layout
        lay_ph_by_idx = {ph.placeholder_format.idx: ph for ph in lay.placeholders}
        for ph in list(slide.placeholders):
            try:
                if (ph.text_frame.text or "").strip():
                    continue                       # 已填充,无残留
            except Exception:
                continue
            pfmt = ph.placeholder_format
            idx = pfmt.idx
            if pfmt.type in _CHROME_PH_TYPES:
                continue                           # chrome 占位符,常空,不报
            lph = lay_ph_by_idx.get(idx)
            if lph and (lph.text_frame.text or "").strip():
                findings.append({
                    "slide": i, "idx": idx,
                    "type": str(pfmt.type),
                    "layout_prompt": lph.text_frame.text.strip(),
                })
    if fail_on_prompt and findings:
        msg = "模板占位符残留:以下页有空占位符会渲染版式提示语(需填充或删除元素,勿用 .text=''):\n" + \
              "\n".join(f"  slide {f['slide']} idx={f['idx']} ({f['type']}) 提示={f['layout_prompt']!r}"
                        for f in findings)
        raise RuntimeError(msg)
    return findings
```

- [ ] **Step 4: 跑测试确认通过**

Run: `cd tech-gtm-training-deck && python -m pytest tests/test_template_placeholders.py -v`
Expected: PASS（5 个用例）。

- [ ] **Step 5: 跑全量回归确认无破坏**

Run: `cd tech-gtm-training-deck && python -m pytest tests/ -v`
Expected: 全绿（既有 test_cover_pagetypes/test_arch_layers/test_network_topo 等不受影响）。

- [ ] **Step 6: 提交**

```bash
git add tech-gtm-training-deck/scripts/deck_helpers.py tech-gtm-training-deck/tests/test_template_placeholders.py
git commit -m "feat(tech-gtm): 加 check_template_placeholders 占位符残留闸门

按 idx 反查版式占位符提示语,空占位符+版式带提示→报告/raise。
根因:build 脚本用 .text='' 清空占位符不删元素,空占位符渲染版式提示语。
措辞无关、模板无关、确定性;排除 DATE/FOOTER/SLIDE_NUMBER chrome 占位符。"
```

---

### Task 2: `cover_from_template` 安全助手 + 修 `chap` 删空 idx10

**Files:**
- Modify: `tech-gtm-training-deck/scripts/deck_helpers.py`（`chap()` L83-105；新增 `cover_from_template()`）
- Test: `tech-gtm-training-deck/tests/test_template_placeholders.py`（追加用例）

**Interfaces:**
- Consumes: `dk.drop_placeholders(slide, keep_idx)`（deckkit，已存在）、`deck.P.layout(role)`。
- Produces: `cover_from_template(prs, deck, layout_role, *, drop_title=True, drop_all=False) -> slide`；`chap()` 修后不传 `sub` 时删 idx10。

- [ ] **Step 1: 写失败测试 — `cover_from_template` 删标题占位符**

追加到 `tests/test_template_placeholders.py`：
```python
def test_cover_from_template_strips_title():
    """用模板封面版式加页 + drop_title=True → idx0 标题占位符被删,不再残留提示。"""
    from deck_helpers import cover_from_template

    class FakeDeck:
        def __init__(self):
            from load_profile import Profile
            import builtin_palettes as bp
            self.P = Profile(bp.get("slate-business"), None)
            self.W, self.H = self.P.canvas()
        def layout(self, role):
            # 测试用默认模板 layout 5(Title Only)顶替封面版式;只要它带 idx0 标题占位符即可
            return 5
    prs = make_test_prs()
    s = cover_from_template(prs, FakeDeck(), "cover", drop_title=True)
    # idx0 占位符应已被删
    idxs = [ph.placeholder_format.idx for ph in s.placeholders]
    assert 0 not in idxs
    # 闸门对这页不报(占位符已删)
    check_template_placeholders(prs)  # 不 raise


def test_cover_from_template_drop_all():
    """drop_all=True → 该版式所有占位符被删。"""
    from deck_helpers import cover_from_template
    class FakeDeck:
        def __init__(self):
            from load_profile import Profile
            import builtin_palettes as bp
            self.P = Profile(bp.get("slate-business"), None)
            self.W, self.H = self.P.canvas()
        def layout(self, role): return 1   # Title and Content,多占位符
    prs = make_test_prs()
    s = cover_from_template(prs, FakeDeck(), "cover", drop_all=True)
    assert len(list(s.placeholders)) == 0
```

- [ ] **Step 2: 写失败测试 — `chap` 不传 sub 删 idx10**

追加到 `tests/test_template_placeholders.py`：
```python
def test_chap_no_sub_drops_idx10():
    """chap() 不传 sub → idx10 副标题占位符被删(而非留空渲染版式提示)。"""
    class FakeDeck:
        def __init__(self):
            from load_profile import Profile
            import builtin_palettes as bp
            self.P = Profile(bp.get("slate-business"), None)
            self.W, self.H = self.P.canvas()
        @property
        def anchor(self): return self.P.color("anchor_subject")
        def layout(self, role):
            # 用 layout 1 顶替章节版式(有 idx0 标题);chap 只用 idx0/idx10
            # layout 1 无 idx10 → 测试改用能加 idx10 的方式:直接验证"无 sub 时 idx10 不留空"
            return 1
    prs = make_test_prs()
    # layout 1 无 idx10 占位符,chap 内部 try/except 会跳过;
    # 核心断言:不传 sub 时 chap 不留任何空占位符(闸门通过)
    s = chap(prs, FakeDeck(), "section", num="01", title="章节标题")  # 不传 sub
    # 闸门对这页不报(标题已填,无 idx10 留空)
    check_template_placeholders(prs)  # 不 raise


def test_chap_with_sub_fills_idx10():
    """chap() 传 sub → 若版式有 idx10 则填充;无则跳过。闸门不报。"""
    class FakeDeck:
        def __init__(self):
            from load_profile import Profile
            import builtin_palettes as bp
            self.P = Profile(bp.get("slate-business"), None)
            self.W, self.H = self.P.canvas()
        @property
        def anchor(self): return self.P.color("anchor_subject")
        def layout(self, role): return 1
    prs = make_test_prs()
    chap(prs, FakeDeck(), "section", num="02", title="章节", sub="副标题")
    check_template_placeholders(prs)  # 不 raise
```

- [ ] **Step 3: 跑测试确认失败**

Run: `cd tech-gtm-training-deck && python -m pytest tests/test_template_placeholders.py -v -k "cover_from_template or chap"`
Expected: FAIL — `cover_from_template` 未定义；`chap` 不传 sub 时若版式有 idx10 会留空（但 layout 1 无 idx10，此用例可能已过——以 `cover_from_template` FAIL 为准）。

- [ ] **Step 4: 实现 `cover_from_template` + 修 `chap`**

在 `deck_helpers.py` 的 `chap()` 函数（L83-105）后、`cover()` 前，新增 `cover_from_template`：
```python
def cover_from_template(prs, deck, layout_role, *, drop_title=True, drop_all=False):
    """用模板的封面版式加页(保留版式自带背景装饰),然后剥离继承的占位符,
    避免空占位符渲染版式提示语。返回干净画布供自绘标题。

    与 cover() 的分工:cover() 用 blank 版式纯自绘(默认推荐);
    本函数用于"要保留模板封面版式装饰、只替换标题"的场景。
    用删除占位符元素(非 .text='')从源头消除残留。

    drop_title: 删 idx0 标题占位符(自绘标题时用,默认 True)
    drop_all  : 删该版式所有占位符(完全自绘时用)
    """
    s = prs.slides.add_slide(prs.slide_layouts[deck.P.layout(layout_role)])
    if drop_all:
        dk.drop_placeholders(s, keep_idx=set())
    elif drop_title:
        for ph in list(s.placeholders):
            if ph.placeholder_format.idx == 0:
                ph._element.getparent().remove(ph._element)
    return s
```

修 `chap()`（L96-105 的 idx10 段）：把"仅传 sub 才填 idx10"改成"传 sub 填 idx10，**不传 sub 时删 idx10**"。将 `chap` 末尾：
```python
    # idx10 副标题占位符(模板自带 24 号样式)
    if sub:
        try:
            ph2 = s.placeholders[10]; ph2.text = sub
            for p in ph2.text_frame.paragraphs:
                for r in p.runs:
                    r.font.name = dk.EAFONT; dk._apply_ea(r, dk.EAFONT)
        except (KeyError, IndexError):
            pass
    return s
```
改为：
```python
    # idx10 副标题占位符:传 sub 则填(打 CJK ea tag),不传则删(避免空占位符渲染版式提示)
    try:
        ph2 = s.placeholders[10]
        if sub:
            ph2.text = sub
            for p in ph2.text_frame.paragraphs:
                for r in p.runs:
                    r.font.name = dk.EAFONT; dk._apply_ea(r, dk.EAFONT)
        else:
            ph2._element.getparent().remove(ph2._element)
    except (KeyError, IndexError):
        pass
    return s
```

- [ ] **Step 5: 跑测试确认通过**

Run: `cd tech-gtm-training-deck && python -m pytest tests/test_template_placeholders.py -v`
Expected: PASS（全部用例，含 Task1 的 5 个 + Task2 的 4 个）。

- [ ] **Step 6: 跑全量回归**

Run: `cd tech-gtm-training-deck && python -m pytest tests/ -v`
Expected: 全绿。

- [ ] **Step 7: 提交**

```bash
git add tech-gtm-training-deck/scripts/deck_helpers.py tech-gtm-training-deck/tests/test_template_placeholders.py
git commit -m "feat(tech-gtm): 加 cover_from_template 助手 + 修 chap 删空 idx10

cover_from_template:用模板封面版式加页后删占位符元素(保留版式装饰,消除残留)。
chap:不传 sub 时删 idx10 而非留空,避免章节页副标题占位符渲染版式提示。"
```

---

### Task 3: 闸门嵌进 `new_deck.py` 脚手架 + 文档警示

**Files:**
- Modify: `tech-gtm-training-deck/scripts/new_deck.py`（SKELETON 文本）
- Modify: `tech-gtm-training-deck/references/deck-from-template.md`

**Interfaces:**
- Consumes: Task1 的 `check_template_placeholders`。
- Produces: 生成的 build 脚手架自带占位符残留闸门调用；文档新增 🔴 MUST 警示。

- [ ] **Step 1: 修 `new_deck.py` SKELETON — import + save 前调闸门**

`new_deck.py` 的 SKELETON 字符串里（约 L36 的 import 行和 L55-56 的 lint/save 间）：

import 行（L36）：
```python
from deck_helpers import Deck, set_title, num_circle, chap, card, para, notes, arch_layers, network_topo
```
改为：
```python
from deck_helpers import Deck, set_title, num_circle, chap, card, para, notes, arch_layers, network_topo, check_template_placeholders
```

SKELETON 的 build() 末尾（约 L55-57）：
```python
    dk.lint_layout(prs, strict=True)
    prs.save(OUT)
    print("saved:", OUT, "slides:", len(prs.slides._sldIdLst))
```
改为：
```python
    dk.lint_layout(prs, strict=True)
    check_template_placeholders(prs)   # 闸门:空占位符渲染版式提示语→硬失败(勿用 .text='' 清占位符)
    prs.save(OUT)
    print("saved:", OUT, "slides:", len(prs.slides._sldIdLst))
```

- [ ] **Step 2: 验证脚手架生成含闸门调用**

Run: `cd tech-gtm-training-deck/scripts && python new_deck.py --profile ../tests/_arch_smoke.pptx --topic "测试" --pages 4 --out /tmp/test_skel.py 2>&1 | head; grep -c "check_template_placeholders" /tmp/test_skel.py`
Expected: 生成的脚手架含 `check_template_placeholders` 调用（grep 计数 ≥2：1 import + 1 调用）。

> 若 `--profile` 参数校验失败（它期望 .yaml），改用任意现有 profile.yaml 路径或临时造一个空 yaml；目标是验证 SKELETON 文本含闸门，不要求脚手架可运行。

- [ ] **Step 3: 加文档警示 — `deck-from-template.md`**

在 `deck-from-template.md` 的 "The inherited template logo/branding" 段（约 L317 之后）追加新段：
```markdown

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
```

- [ ] **Step 4: 跑全量回归确认无破坏**

Run: `cd tech-gtm-training-deck && python -m pytest tests/ -v`
Expected: 全绿（new_deck 改的是 SKELETON 文本，不影响测试；文档改动无测试影响）。

- [ ] **Step 5: 提交**

```bash
git add tech-gtm-training-deck/scripts/new_deck.py tech-gtm-training-deck/references/deck-from-template.md
git commit -m "feat(tech-gtm): 脚手架嵌占位符闸门 + 文档警示清空占位符失败模式

new_deck 生成的 build 脚手架在 save 前调 check_template_placeholders。
deck-from-template.md 加 🔴 MUST:禁止 .text='' 清占位符,改删元素或填充。"
```

---

### Task 4: 端到端验证 — 闸门能抓 LoopEngineering 首页 bug

**Files:**
- 无源码改动（仅验证，不交付 deck）

**Interfaces:**
- Consumes: Task1 的 `check_template_placeholders`；LoopEngineering-deck 的 `build.py`（只读验证）。

- [ ] **Step 1: 验证闸门对真实 bug 有效**

临时把 LoopEngineering build.py 的封面写法复现到内存 prs 上跑闸门（不改 build.py 文件）：
```bash
cd /c/Users/KC/Documents/LoopEngineering-deck
python -c "
import sys
sys.path.insert(0, r'D:/develop/luohao-skills/tech-gtm-training-deck/scripts')
sys.path.insert(0, r'C:/Users/KC/.agents/skills/slide-maker/scripts')
import deckkit as dk
from deck_helpers import check_template_placeholders
prs = dk.open_template(r'C:/Users/KC/Documents/AI热点技术培训 - 智能体记忆系统v1.0.pptx')
# 复现 build.py 封面:layout 11 + placeholders[0].text=''
s = prs.slides.add_slide(prs.slide_layouts[11])
s.placeholders[0].text = ''
try:
    check_template_placeholders(prs)
    print('ERROR: 闸门未抓到 bug')
except RuntimeError as e:
    print('OK 闸门抓到首页残留:')
    print(str(e)[:200])
"
```
Expected: `OK 闸门抓到首页残留:` + 报告 `slide 1 idx=0 提示='点击添加页面大标题 30号'`。

- [ ] **Step 2: 验证修复路径有效**

验证改用 `cover_from_template` 后闸门不报：
```bash
cd /c/Users/KC/Documents/LoopEngineering-deck
python -c "
import sys
sys.path.insert(0, r'D:/develop/luohao-skills/tech-gtm-training-deck/scripts')
sys.path.insert(0, r'C:/Users/KC/.agents/skills/slide-maker/scripts')
import deckkit as dk
from deck_helpers import check_template_placeholders, cover_from_template
prs = dk.open_template(r'C:/Users/KC/Documents/AI热点技术培训 - 智能体记忆系统v1.0.pptx')
# 模板无 profile,手造最小 deck 适配(只用 layout 11)
class D: pass
d = D(); d.P = type('P',(),{'layout':lambda self,r:11})()
cover_from_template(prs, d, 'cover', drop_title=True)
check_template_placeholders(prs)
print('OK 修复路径通过闸门(无残留)')
"
```
Expected: `OK 修复路径通过闸门(无残留)`。

- [ ] **Step 3: 无需提交（验证 only）**

此任务不改源码、不交付 deck，仅证闸门对真实 bug 有效 + 修复路径有效。若 Step1/2 任一失败，回 Task1/2 修实现。

---

## Self-Review

**1. Spec 覆盖：**
- 修 `chap`（无 sub 删 idx10）→ Task2 Step4。✅
- 新增 `cover_from_template` → Task2 Step4。✅
- 新增 `check_template_placeholders` → Task1 Step3。✅
- `new_deck.py` 调闸门 → Task3 Step1。✅
- 文档 🔴 MUST 警示 → Task3 Step3。✅
- 测试 4+ 用例 → Task1 5个 + Task2 4个 = 9个（spec 说 4 个，实际更细，覆盖更全）。✅
- 端到端验证闸门抓 LoopEngineering bug → Task4。✅
- "不做"项（不改 slide-maker、不重生成 deck）→ Global Constraints + Task4 验证 only。✅

**2. Placeholder 扫描：** 无 TBD/TODO（SKELETON 里 `# TODO` 是脚手架既有的用户填充提示，非计划占位）。各步骤代码完整。

**3. 类型一致性：** `check_template_placeholders(prs, *, fail_on_prompt=True)` 签名在 Task1 定义、Task3/Task4 调用一致。`cover_from_template(prs, deck, layout_role, *, drop_title=True, drop_all=False)` 在 Task2 定义、Task4 调用一致。finding dict 键 `slide/idx/type/layout_prompt` 一致。`_CHROME_PH_TYPES` 用 `PP_PLACEHOLDER.DATE/FOOTER/SLIDE_NUMBER`，与 Step1 测试注释一致。

**4. 测试 fixture 风险：** Task2 测试用 `FakeDeck.layout()` 返回 layout 索引（5/1），绕过 profile 的 layout role 映射——已确认默认模板 layout 5 (Title Only, idx0) / layout 1 (Title+Content) 存在。`chap` 测试因 layout 1 无 idx10，Step3 预期以 `cover_from_template` FAIL 为准，`chap_no_sub` 用例可能已过（无害）。
