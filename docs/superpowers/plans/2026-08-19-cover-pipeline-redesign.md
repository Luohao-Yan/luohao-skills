# 封面链路重设计 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 让 `tech-gtm-training-deck` 的封面链路可靠:cover 优先用模板自带封面(填占位符+自绘兜底,不静默吞错)、strip_branding 不误删占位符、inspect 选占位符最丰富的封面 layout。

**Architecture:** 三处改动互相支撑——inspect 选对封面 layout(§3.3)→ strip 不删该 layout 的占位符(§3.2)→ cover 填占位符,缺了自绘兜底(§3.1)。改完用《龙岗政策打标》deck 回测封面正确。

**Tech Stack:** python-pptx, PyYAML, pytest;skill 在 `D:\develop\luohao-skills\tech-gtm-training-deck`;依赖 slide-maker 的 deckkit。

## Global Constraints

- 工作目录:`D:\develop\luohao-skills\tech-gtm-training-deck`(git 仓库根 `D:\develop\luohao-skills`,main 分支)
- 测试命令:`cd D:\develop\luohao-skills\tech-gtm-training-deck && python -m pytest tests/ -q`(基线 26 passed,改后必须仍绿)
- 真模板(回测用):`C:\Users\KC\Documents\AI热点技术培训 - 智能体记忆系统v1.0.pptx`,其 layout 15「标题幻灯片」有 idx0(标题,默认文本"金山云标准模板-大标题 38号")/ idx10(副标题)/ idx11(日期)三占位符 + 「图形 12」logo + 「文本框 10/11」品牌文本
- 绝不 `except: pass` 静默吞错——占位符取不到要 `print("[cover] ...")` + 兜底
- 颜色走 `deck.anchor/comparator/neutral/emphasis`(profile),不硬编 hex
- 提交信息结尾加 `Co-Authored-By: Kscc <noreply@owtffssent.com>`

---

## Task 1: strip_branding 删 brand text 时跳过占位符

**Files:**
- Modify: `scripts/deck_helpers.py:321-344`(`strip_branding` 函数体)
- Test: `tests/test_cover_pagetypes.py`(现有 `test_strip_branding_*`) + 新增用例

**Interfaces:**
- Consumes: `_is_logo_pic`, `_is_brand_text`, `BRAND_TEXT_KEYS`(同文件,不变)
- Produces: `strip_branding(prs, keep_logo=False, verbose=False)` 行为变——删 text 前跳过 placeholder;签名不变

- [ ] **Step 1: 写失败测试**

在 `tests/test_cover_pagetypes.py` 末尾加(用真模板,需 pytest 能读到路径——用 `conftest` 不便,直接内联):

```python
def test_strip_branding_keeps_placeholder_with_brand_default_text():
    """idx0 占位符默认文本含"金山云"也不该被删——它是 build 要填的主标题位。"""
    import os, sys
    sys.path.insert(0, os.path.join(os.path.dirname(HERE), "scripts"))
    from slide_maker_path import find_slide_maker
    sys.path.insert(0, find_slide_maker())
    import deckkit as dk
    from deck_helpers import strip_branding
    TPL = r"C:\Users\KC\Documents\AI热点技术培训 - 智能体记忆系统v1.0.pptx"
    if not os.path.isfile(TPL):
        pytest.skip("真模板不在本机,跳过(layout 级 strip 回归)")
    prs = dk.open_template(TPL)
    strip_branding(prs)
    lay15 = prs.slide_layouts[15]
    idxs = sorted(sh.placeholder_format.idx for sh in lay15.placeholders if sh.is_placeholder)
    assert idxs == [0, 10, 11], f"封面占位符应全保留,实际 {idxs}"
    # logo 图应被清
    assert not any(sh.name == "图形 12" for sh in lay15.shapes)
```

- [ ] **Step 2: 跑测试确认失败**

Run: `cd D:\develop\luohao-skills\tech-gtm-training-deck && python -m pytest tests/test_cover_pagetypes.py::test_strip_branding_keeps_placeholder_with_brand_default_text -v`
Expected: FAIL,`idxs == [10, 11]`(idx0 被误删)

- [ ] **Step 3: 改 strip_branding(跳过占位符)**

`scripts/deck_helpers.py` 第 338 行附近,把:
```python
            if _is_brand_text(sh):
                to_del.append(sh); ntxt += 1
```
改为:
```python
            if _is_brand_text(sh) and not sh.is_placeholder:
                to_del.append(sh); ntxt += 1
```
并更新 docstring:"删 brand text 时跳过占位符(占位符默认文本可能含品牌词,但 build 填占位符会覆盖默认文本,不应删整个占位符)"。

- [ ] **Step 4: 跑测试确认通过**

Run: `cd D:\develop\luohao-skills\tech-gtm-training-deck && python -m pytest tests/test_cover_pagetypes.py -v`
Expected: PASS(含新用例 + 现有 `test_strip_branding_*`)

- [ ] **Step 5: 跑全量确认无回归**

Run: `cd D:\develop\luohao-skills\tech-gtm-training-deck && python -m pytest tests/ -q`
Expected: 27 passed

- [ ] **Step 6: 提交**

```bash
cd D:\develop\luohao-skills
git add tech-gtm-training-deck/scripts/deck_helpers.py tech-gtm-training-deck/tests/test_cover_pagetypes.py
git commit -m "fix(tech-gtm-training-deck): strip_branding 不删含品牌词的占位符

idx0「标题 2」占位符默认文本'金山云标准模板-大标题 38号'含品牌词,
被 _is_brand_text 连占位符一起删,导致 cover 取不到主标题位。
改为删 brand text 时跳过 placeholder(占位符由 cover 填时覆盖默认文本)。

Co-Authored-By: Kscc <noreply@owtffssent.com>"
```

---

## Task 2: inspect 选占位符最丰富的封面 layout

**Files:**
- Modify: `scripts/inspect_and_profile.py:69-87`(`pick_key_layouts` cover 分支)
- Test: `tests/test_template_pool.py`(现有)或新增 `tests/test_inspect_cover.py`

**Interfaces:**
- Consumes: `layouts`(dict idx→info with `name`),从 `inspect_template` 来
- Produces: `pick_key_layouts` 返回的 `cover` = 占位符最丰富候选的 idx;`profile.yaml layouts.cover` 随之正确

- [ ] **Step 1: 写失败测试**

新建 `tests/test_inspect_cover.py`:
```python
# -*- coding: utf-8 -*-
"""inspect 应选占位符最丰富的封面 layout(layout 15 而非 11)。"""
import os, sys
import pytest
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "scripts"))
from inspect_and_profile import pick_key_layouts

def _layouts(names):
    """造 {idx: {"name": n, "placeholders": [...]}}。"""
    return {i: {"name": n, "placeholders": []} for i, n in enumerate(names)}

def test_cover_picks_placeholder_richest():
    # layout 11「标题页」(只标题) vs layout 15「标题幻灯片」(标题+副标题+日期)
    lays = {
        11: {"name": "标题页", "placeholders": [{"type": "TITLE"}]},
        15: {"name": "标题幻灯片", "placeholders": [{"type": "TITLE"}, {"type": "BODY"}, {"type": "BODY"}]},
    }
    km = pick_key_layouts(lays)
    assert km["cover"] == 15, "应选占位符更丰富的 layout 15"

def test_cover_falls_back_to_first_when_only_title():
    lays = {11: {"name": "标题页", "placeholders": [{"type": "TITLE"}]}}
    km = pick_key_layouts(lays)
    assert km["cover"] == 11
```

- [ ] **Step 2: 跑测试确认失败**

Run: `cd D:\develop\luohao-skills\tech-gtm-training-deck && python -m pytest tests/test_inspect_cover.py -v`
Expected: FAIL(`test_cover_picks_placeholder_richest` 得 11 而非 15,因首个命中)

- [ ] **Step 3: 改 pick_key_layouts(cover 选占位符最丰富者)**

`scripts/inspect_and_profile.py` `pick_key_layouts` 函数,在现有 `role_map` 循环前先收集 cover 候选并选最优。把函数体改为(保留其他 role 的启发式不变):

```python
def pick_key_layouts(layouts):
    """从 layouts 里挑出 build 脚本常用的角色。cover 选占位符最丰富者(非首个命中)。"""
    role_map = {}
    # cover: 收集所有封面候选,选占位符最丰富者
    cover_keys = ["标题幻灯片", "标题页", "Title Slide"]
    cover_cands = [(idx, info) for idx, info in layouts.items()
                   if any(k in info["name"] for k in cover_keys)]
    if cover_cands:
        def _score(info):
            phs = info.get("placeholders", [])
            s = 0
            for ph in phs:
                t = str(ph.get("type", ""))
                if "TITLE" in t: s += 2
                elif "BODY" in t or "DATE" in t: s += 1
            return s
        cover_cands.sort(key=lambda x: (-_score(x[1]), x[0]))
        role_map["cover"] = cover_cands[0][0]
    # 其余 role: 首个命中
    for idx, info in layouts.items():
        n = info["name"]
        if "章节" in n and "chapter" not in role_map:
            role_map["chapter"] = idx
        elif "深色" in n and "有底线" in n and "dark" not in role_map:
            role_map["dark"] = idx
        elif "红色" in n and "有底线" in n and "red_conclusion" not in role_map:
            role_map["red_conclusion"] = idx
        elif "浅色" in n and "有底线" in n and "content" not in role_map:
            role_map["content"] = idx
        elif n.strip() == "空白" and "blank" not in role_map:
            role_map["blank"] = idx
    return role_map
```

- [ ] **Step 4: 跑测试确认通过**

Run: `cd D:\develop\luohao-skills\tech-gtm-training-deck && python -m pytest tests/test_inspect_cover.py -v`
Expected: PASS

- [ ] **Step 5: 跑全量 + 真模板验证**

Run: `cd D:\develop\luohao-skills\tech-gtm-training-deck && python -m pytest tests/ -q`
Expected: 29 passed
再跑:`python scripts/inspect_and_profile.py "C:\Users\KC\Documents\AI热点技术培训 - 智能体记忆系统v1.0.pptx" --out /tmp/covercheck 2>&1 | head -3`(或 Windows 临时目录),确认 `layouts: ... key roles: {'cover': 15, ...}`。

- [ ] **Step 6: 提交**

```bash
cd D:\develop\luohao-skills
git add tech-gtm-training-deck/scripts/inspect_and_profile.py tech-gtm-training-deck/tests/test_inspect_cover.py
git commit -m "feat(tech-gtm-training-deck): inspect cover role 选占位符最丰富的 layout

原启发式首个命中,选了 layout 11(只标题)而非 layout 15(标题+副标题+日期)。
改为收集所有封面候选,按占位符丰富度打分(TITLE+2/BODY/DATE+1)选最高。

Co-Authored-By: Kscc <noreply@owtffssent.com>"
```

---

## Task 3: cover 翻转哲学——优先模板封面 + 填占位符兜底

**Files:**
- Modify: `scripts/deck_helpers.py:237-289`(`cover` 函数)
- Test: `tests/test_cover_pagetypes.py`(现有 cover 用例 + 新增)

**Interfaces:**
- Consumes: `deck.P.layout("cover")`(Task 2 后指向对的 idx),`dk.text`, `dk.box`, profile 色
- Produces: `cover(prs, deck, subject, subtitle="", meta="", use_template=True, style="band")` 默认用模板封面;返回 slide

- [ ] **Step 1: 写失败测试**

在 `tests/test_cover_pagetypes.py` 加(用真模板验证填占位符):
```python
def test_cover_uses_template_fills_placeholders():
    import os
    from conftest import make_test_prs
    # 用真模板:strip 后 idx0 应在(Task1),cover 应填进 idx0
    TPL = r"C:\Users\KC\Documents\AI热点技术培训 - 智能体记忆系统v1.0.pptx"
    if not os.path.isfile(TPL):
        pytest.skip("真模板不在本机")
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(HERE), "scripts"))
    from slide_maker_path import find_slide_maker
    sys.path.insert(0, find_slide_maker())
    import deckkit as dk
    from deck_helpers import cover, strip_branding
    from load_profile import Profile
    import builtin_palettes as bp
    P = Profile(bp.get("slate-business"), None)
    class D2:
        P=P
        W,H=P.canvas()
        anchor=P.color("anchor_subject");comparator=P.color("comparator")
        neutral=P.color("neutral");emphasis=P.color("emphasis")
        def layout(self,k): return 15 if k=="cover" else 0
    dd=D2()
    prs = dk.open_template(TPL); strip_branding(prs)
    s = cover(prs, dd, subject="龙岗政策打标", subtitle="副标", meta="团队·日期")
    texts = [sh.text_frame.text for sh in s.shapes if sh.has_text_frame]
    assert any("龙岗政策打标" in t for t in texts), "主标题必须填进封面"
    # 主标题字号 ≥44
    big = [r.font.size.pt for sh in s.shapes if sh.has_text_frame
           for p in sh.text_frame.paragraphs for r in p.runs if "龙岗政策打标" in r.text and r.font.size]
    assert big and max(big) >= 44, f"主标题字号应≥44,实际 {big}"

def test_cover_template_fallback_draws_when_no_cover_layout(capfd):
    """profile 无 cover layout(use_template=True 但 layout() 抛错)→ 自绘兜底,不静默吞错。"""
    from conftest import make_test_prs
    prs = make_test_prs()
    class DNoCover:
        P=type("P",(),{"color":staticmethod(lambda k: __import__("pptx").dml.color.RGBColor(0xE6,0x00,0x2D))})()
        W,H=13.333,7.5
        anchor=comparator=neutral=emphasis=__import__("pptx").dml.color.RGBColor(0xE6,0x00,0x2D)
        def layout(self,k):
            raise KeyError(k)
    s = cover(prs, DNoCover(), subject="兜底主题", subtitle="s", meta="m")
    texts = [sh.text_frame.text for sh in s.shapes if sh.has_text_frame]
    assert any("兜底主题" in t for t in texts), "无模板封面时必须自绘兜底主标题"
    out = capfd.readouterr().out
    assert "cover" in out.lower() or "兜底" in out, "兜底时应 log,不静默吞错"
```

- [ ] **Step 2: 跑测试确认失败**

Run: `cd D:\develop\luohao-skills\tech-gtm-training-deck && python -m pytest tests/test_cover_pagetypes.py::test_cover_uses_template_fills_placeholders tests/test_cover_pagetypes.py::test_cover_template_fallback_draws_when_no_cover_layout -v`
Expected: FAIL(现有 cover 在 blank 自绘,不填模板占位符)

- [ ] **Step 3: 改 cover(优先模板 + 兜底)**

`scripts/deck_helpers.py` 把 `cover` 函数(237-289)替换为:
```python
def cover(prs, deck, subject, subtitle="", meta="", use_template=True, style="band"):
    """封面。use_template=True(默认):用模板封面 layout,按占位符类型填(TITLE→subject,
    BODY→subtitle/meta),取不到自绘兜底,绝不静默吞错。use_template=False:blank 自绘(band/hero)。"""
    W, H = deck.W, deck.H
    anchor = deck.anchor; neutral = deck.neutral; ea = dk.EAFONT
    if use_template:
        try:
            cidx = deck.P.layout("cover")
        except Exception as e:
            print(f"[cover] profile 无 cover layout({e}),回退自绘")
            return _cover_draw(prs, deck, subject, subtitle, meta, style)
        s = prs.slides.add_slide(prs.slide_layouts[cidx])
        _fill_cover_placeholders(s, subject, subtitle, meta, deck)
        return s
    return _cover_draw(prs, deck, subject, subtitle, meta, style)

# 兜底坐标(模板 layout 15 原占位符位置)
_COV_POS = {"subject": (1.57, 1.25, 7.81, 1.57),
            "subtitle": (1.57, 2.99, 6.61, 0.53),
            "meta": (1.61, 4.19, 2.96, 0.79)}
_COV_MIN_PT = {"subject": 44, "subtitle": 18, "meta": 13}

def _set_run(r, size, color, ea):
    from pptx.util import Pt
    r.font.size = Pt(size); r.font.bold = True; r.font.color.rgb = color
    r.font.name = ea; dk._apply_ea(r, ea)

def _fill_cover_placeholders(s, subject, subtitle, meta, deck):
    """按占位符 type 匹配填;缺的字段自绘兜底。不静默吞错。"""
    from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
    ea = dk.EAFONT; WHITE = RGBColor(0xFF,0xFF,0xFF)
    filled = {"subject": False, "subtitle": False, "meta": False}
    body_count = 0
    for ph in list(s.placeholders):
        try:
            t = str(ph.placeholder_format.type)
        except Exception:
            continue
        if "TITLE" in t and not filled["subject"]:
            ph.text = subject
            for p in ph.text_frame.paragraphs:
                for r in p.runs: _set_run(r, _COV_MIN_PT["subject"], WHITE, ea)
            filled["subject"] = True
        elif "BODY" in t:
            if not filled["subtitle"]:
                ph.text = subtitle; body_count = 0
                for p in ph.text_frame.paragraphs:
                    for r in p.runs: _set_run(r, _COV_MIN_PT["subtitle"], WHITE, ea)
                filled["subtitle"] = True
            elif not filled["meta"]:
                ph.text = meta
                for p in ph.text_frame.paragraphs:
                    for r in p.runs: _set_run(r, _COV_MIN_PT["meta"], WHITE, ea)
                filled["meta"] = True
        elif "DATE" in t and not filled["meta"]:
            ph.text = meta
            for p in ph.text_frame.paragraphs:
                for r in p.runs: _set_run(r, _COV_MIN_PT["meta"], WHITE, ea)
            filled["meta"] = True
    # 兜底:缺的字段自绘
    for field, txt in [("subject", subject), ("subtitle", subtitle), ("meta", meta)]:
        if not filled[field] and txt:
            x, y, w, h = _COV_POS[field]
            print(f"[cover] {field} 占位符缺失,自绘兜底")
            dk.text(s, x, y, w, h,
                    [[(txt, _COV_MIN_PT[field], WHITE, True, False, ea)]],
                    align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.MIDDLE, line_spacing=1.1)

def _cover_draw(prs, deck, subject, subtitle, meta, style):
    """原 blank 自绘(band/hero),修 band 没背景/hero 阴阳对半两个体验 bug。作 fallback。"""
    s = prs.slides.add_slide(prs.slide_layouts[deck.P.layout("blank")])
    W, H = deck.W, deck.H; anchor = deck.anchor; ea = dk.EAFONT
    if style == "hero":
        dk.box(s, 0, 0, W, H, grad=[(0.0, anchor, 1.0), (1.0, deck.comparator, 0.85)], grad_angle=90, round=False)
        dk.text(s, 0.6, H*0.30, W-1.2, 1.4, [[(subject, 44, WHITE, True, False, ea)]], align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
        if subtitle: dk.text(s, 0.6, H*0.30+1.4, W-1.2, 0.5, [[(subtitle, 18, RGBColor(0xF3,0xF5,0xF8), False, False, ea)]], align=PP_ALIGN.CENTER)
        if meta: dk.text(s, 0.6, H*0.62, W-1.2, 0.4, [[(meta, 13, deck.neutral, False, False, ea)]], align=PP_ALIGN.CENTER)
        dk.box(s, 0, H-0.18, W, 0.18, grad=[(0.0, deck.comparator, 1.0), (1.0, anchor, 1.0)], grad_angle=0, round=False)
    else:
        dk.box(s, 0, 0, W, H, fill=RGBColor(0xF7,0xF7,0xFA), round=False)  # 修 #1:浅底,不再大片留白
        dk.box(s, 0, 0, 0.32, H, grad=[(0.0, anchor, 1.0), (1.0, deck.comparator, 0.9)], grad_angle=90, round=False)
        dk.text(s, 1.1, H*0.30, W-1.6, 1.3, [[(subject, 44, anchor, True, False, ea)]], align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, line_spacing=1.12, wrap=True)
        if subtitle: dk.text(s, 1.12, H*0.30+1.35, W-1.7, 0.9, [[(subtitle, 18, deck.neutral, False, False, ea)]], align=PP_ALIGN.LEFT, line_spacing=1.25, wrap=True)
        if meta:
            dk.box(s, 1.12, H-0.95, 1.6, 0.02, fill=anchor)
            dk.text(s, 1.12, H-0.80, W-1.7, 0.35, [[(meta, 13, MUTE, False, False, ea)]], align=PP_ALIGN.LEFT)
    return s
```

- [ ] **Step 4: 跑测试确认通过**

Run: `cd D:\develop\luohao-skills\tech-gtm-training-deck && python -m pytest tests/test_cover_pagetypes.py -v`
Expected: PASS(新用例 + 现有 band/hero 用例——注意现有 `test_cover_band_makes_one_slide_no_logo` 用 `style="band"` 默认 use_template=True 会走模板,但 `make_test_prs` 无 cover layout,会回退自绘,仍应过)

- [ ] **Step 5: 跑全量**

Run: `cd D:\develop\luohao-skills\tech-gtm-training-deck && python -m pytest tests/ -q`
Expected: 31 passed

- [ ] **Step 6: 提交**

```bash
cd D:\develop\luohao-skills
git add tech-gtm-training-deck/scripts/deck_helpers.py tech-gtm-training-deck/tests/test_cover_pagetypes.py
git commit -m "feat(tech-gtm-training-deck): cover 优先模板封面+填占位符兜底,不静默吞错

默认 use_template=True:用模板封面 layout,按占位符 type 填(TITLE→subject/BODY→subtitle,meta),
取不到自绘兜底并 log(绝不 except:pass)。主标题字号下限 44pt。
use_template=False 保留 band/hero 自绘(修 band 没背景/hero 阴阳对半)作 fallback。

Co-Authored-By: Kscc <noreply@owtffssent.com>"
```

---

## Task 4: SKILL.md / deck-from-template.md 文档同步

**Files:**
- Modify: `SKILL.md`(§Cover & branding + 失败模式段)
- Modify: `references/deck-from-template.md`(build rhythm + "inherited template logo/branding" 段)

**Interfaces:** 无(纯文档)

- [ ] **Step 1: 改 SKILL.md cover 段**

找到"## Cover & branding"段(约 195-211 行),把描述 cover 哲学的句子从"自绘,避免继承模板 logo"改为:
- `cover(prs, deck, subject, subtitle, meta, use_template=True)` — 默认用**模板自带的封面 layout**(由 profile `layouts.cover` 指定),按占位符类型填,取不到自绘兜底(不静默吞错),主标题字号下限 44pt。`use_template=False` 走 band/hero 自绘作 fallback。
- 保留 strip_branding 描述,补一句"删 brand text 时跳过占位符(占位符默认文本可能含品牌词,由 cover 填时覆盖)"。

- [ ] **Step 2: 改 deck-from-template.md build rhythm + 失败模式段**

约 76 行 build rhythm:`strip_branding(prs)` → `cover(prs, D, subject, subtitle, meta)`(默认 use_template=True 用模板封面)。
约 265-292 行"inherited template logo/branding"段:补"strip 误删占位符"子失败模式——"占位符默认文本含品牌词(如'金山云标准模板-大标题')会被 _is_brand_text 误删,导致 cover 取不到主标题位;修复:删 brand text 跳过 placeholder"。

- [ ] **Step 3: 验证文档无残留旧哲学**

Run: `cd D:\develop\luohao-skills\tech-gtm-training-deck && grep -n "避免继承模板\|在 blank layout 上自绘" SKILL.md references/deck-from-template.md`
Expected: 无输出(旧哲学描述已清)

- [ ] **Step 4: 提交**

```bash
cd D:\develop\luohao-skills
git add tech-gtm-training-deck/SKILL.md tech-gtm-training-deck/references/deck-from-template.md
git commit -m "docs(tech-gtm-training-deck): 同步封面链路新哲学(优先模板+兜底+strip不删占位符)

Co-Authored-By: Kscc <noreply@owtffssent.com>"
```

---

## Task 5: 回测——《龙岗政策打标》deck 封面正确

**Files:**
- 不改 skill;用本 deck 的 build.py 验证(`C:\Users\KC\orca\projects\Pre-seles-architect-scheme\output\longgang-policy-tagging-deck\build.py`)

**Interfaces:** 验证 Task 1-3 端到端

- [ ] **Step 1: 把 deck build.py 封面段改回用 cover helper(可选,验证 helper 好用)**

本 deck build.py 当前是手填 layout 15 + 自绘主标题的 workaround。改成调 cover helper:
```python
s = cover(prs, D, subject="龙岗政策打标",
          subtitle="闭环实验与落地选型汇报  —  60 样本 × 4 方法实测",
          meta="技术团队  ·  2026/08/19")
notes(s, "开场:...")
```
(需先对 deck 的 profile.yaml 跑 inspect 确认 `layouts.cover: 15`——见 Task 2 Step 5 输出)

- [ ] **Step 2: 重新生成 deck 封面**

Run: `cd C:\Users\KC\orca\projects\Pre-seles-architect-scheme\output\longgang-policy-tagging-deck && python build.py 2>&1 | grep -E "critical|saved" | tail -2`
Expected: `saved: ...training-deck.pptx slides: 18` + 0 critical

- [ ] **Step 3: 渲染封面并人工确认**

Run: `python "C:\Users\KC\.claude\skills\slide-maker\scripts\render_deck.py" training-deck.pptx render 2>&1 | grep rendered`
读 `render/slide01.png`,确认:① 主标题"龙岗政策打标"在且字号大;② 副标题/日期在;③ 模板渐变圆+点阵背景在;④ 无金山云 logo/版权。

- [ ] **Step 4: 提交 deck 改动(若改了 build.py)**

```bash
cd C:\Users\KC\orca\projects\Pre-seles-architect-scheme
git add output/longgang-policy-tagging-deck/build.py
git commit -m "feat: 龙岗deck封面改用 cover helper(skills 更新后)

Co-Authored-By: Kscc <noreply@owtffssent.com>"
```

---

## Self-Review

**1. Spec 覆盖:**
- §3.1 cover 翻转 → Task 3 ✓
- §3.2 strip 不删占位符 → Task 1 ✓
- §3.3 inspect 选占位符最丰 → Task 2 ✓
- §4 波及文件(SKILL/deck-from-template/skeleton)→ Task 4 ✓(skeleton 签名兼容,无需改)
- §5 测试 → Task 1-3 各含 ✓
- §6 验收 → Task 5 回测 ✓

**2. Placeholder 扫描:** 无 TBD/TODO;测试代码全给了;`_cover_draw`/`_fill_cover_placeholders`/`_set_run` 都在 Task 3 定义。

**3. Type 一致:** `cover(prs, deck, subject, subtitle, meta, use_template, style)` 签名 Task 3 定义,Task 4/5 引用一致;`pick_key_layouts(layouts) -> dict` Task 2 定义,Task 5 Step 1 引用 `D.P.layout("cover")` 一致;`strip_branding(prs, keep_logo, verbose)` 签名不变。
