# 模板 PPT 母版占位符残留修复 — 设计文档

> 日期：2026-08-25 · 范围：tech-gtm-training-deck skill 持久化修复 · 落点：luohao-skills 仓库内（不动 npm 安装的 slide-maker 包）

## 1. 问题

用户反馈：复原生成的 PPT 首页，母版/版式的标题占位符提示语 `点击添加页面大标题 30号`（虚线框、灰色文字）残留在页面上，标题 `Loop Engineering` 是另起的手绘文本框，PPT 完成度不足。用户说"还是会有"，表明这是反复出现的坑。

### 根因（已实测定位）

LoopEngineering-deck 的 build.py 封面构造（L99-102）：

```python
s = prs.slides.add_slide(prs.slide_layouts[11])   # 用模板封面版式 11，它自带 idx0 标题占位符
try:
    s.placeholders[0].text = ""   # ← 只清空文本，没删除占位符元素
except Exception: pass
T(s, 1.5, 1.75, ..., "Loop Engineering", 44, RED, ...)   # 另手绘红色标题
```

实测模板 layout 11 占位符：`idx=0, TITLE, prompt_text='点击添加页面大标题 30号'`。把占位符 `.text=""` 只清空文字，**占位符元素仍在**。PowerPoint 中空占位符会渲染版式/母版定义的提示语 → 提示语残留。

正确做法二选一：(a) **删除占位符元素**（`drop_placeholders` / `ph._element.getparent().remove(...)`），(b) **填充它**。`deckkit.content_slide`（内容页）用填充法，所以内容页无此问题。

### 全 deck 排查结论

| 位置 | 处理方式 | 状态 |
|---|---|---|
| 封面 build.py (layout 11) | `placeholders[0].text=""` 清空未删 | ❌ 本次首页残留 |
| 内容页 ×10 (layout 0) | `title()`/`set_title()` 填充 idx0 | ✅ |
| 结语页 (layout 4) | `ph.text="结语"` 填充 | ✅ |
| `deck_helpers.chap()` 章节页 | 仅传 `sub` 才填 idx10，**不传则 idx10 留空** | ⚠️ 潜在残留（本 deck 未触发，同类坑） |
| skill 整体 | helper 已有 `cover()`(用 blank 版式自绘)、`strip_branding()`，文档已给正确路径；但**无确定性闸门阻止构建者写错** | ⚠️ 缺口 |

### 仓库现状（与 ~/.claude 副本差异）

仓库 `D:/develop/luohao-skills/tech-gtm-training-deck` 是源（最新），`~/.claude/skills/tech-gtm-training-deck` 是旧副本（非软链）。**仓库版 deck_helpers.py 已成熟**：已有 `cover(prs, deck, subject, subtitle, meta, style="band"|"hero")`（用 blank 版式自绘，避开封面占位符）、`strip_branding(prs)`（清母版/版式 logo+版权页脚）。文档 `references/deck-from-template.md` 已明确正确路径：`open_template → strip_branding → cover()`，并已记录"inherited template logo/branding"失败模式。

**结论**：正确的 skill 用法本可规避此 bug。LoopEngineering 的 build.py 是早期手写脚本，没走推荐路径（没 `strip_branding`、没 `cover()`），用了错误写法。**helper 层不缺正确路径，缺的是"阻止构建者写错"的确定性闸门**。

### 关键架构约束

- `slide-maker` 是 npm 安装包（`~/.agents/skills/slide-maker`，非 git），改它的 `lint_deck.py`/`deckkit.py` 会被升级覆盖 → **不持久**。
- tech-gtm `new_deck.py` 调 `dk.lint_layout(prs, strict=True)`（构建期 lint，在 deckkit 包内）。
- 决策（已与用户确认）：lint 闸门放 **luohao-skills 仓库内 tech-gtm 自有代码**，不动 slide-maker 包。

## 2. 方案 B（已确认）

助手正确化 + tech-gtm 自有确定性 lint 闸门，均落仓库内、随仓库提交、不被 npm 覆盖。

### 2.1 修 `deck_helpers.chap()` — 消除章节页潜在残留

当前 `chap()`（L83-105）仅当传 `sub` 时填 idx10；不传则 idx10 留空 → 渲染版式提示 `可添加副标题或英文-20号`。修复：不传 `sub` 时**删除 idx10 占位符元素**而非留空。用现成 `dk.drop_placeholders` 或显式 `ph._element.getparent().remove(ph._element)`。

```python
# chap() 末尾：无 sub 时删 idx10 占位符，避免渲染版式提示
if not sub:
    for ph in list(s.placeholders):
        if ph.placeholder_format.idx == 10:
            ph._element.getparent().remove(ph._element)
```

### 2.2 新增 `deck_helpers.cover_from_template()` — "坚持用模板封面版式自绘"的安全路径

仓库已有 `cover()`（用 blank 版式）。但若构建者（如 LoopEngineering 复原场景）**坚持沿用模板封面版式**（要保留模板封面的背景装饰，只替换标题文字），当前没有安全助手——只能手写 `add_slide(layouts[N]) + drop_placeholders`。补一个：

```python
def cover_from_template(prs, deck, layout_role, *, drop_title=True, drop_all=False):
    """用模板的封面版式加页（保留版式自带背景装饰），然后剥离继承的占位符，
    避免空占位符渲染版式提示语。返回干净画布供自绘标题。

    drop_title: 删除 idx0 标题占位符（自绘标题时用，默认 True）
    drop_all  : 删除该版式所有占位符（完全自绘时用）
    其余占位符（如 idx10 body）若不填充，也应在此 drop——调用方按需传 keep_idx。
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

> 设计取舍：`cover()`（blank 版式，纯自绘）仍是推荐默认；`cover_from_template()` 是"保留模板封面装饰"的补充路径。两者都用**删除占位符元素**而非清空，从源头消除残留。不在 `cover()` 里加 `keep_logo`/版式选择等参数，保持单一职责。

### 2.3 新增 `deck_helpers.check_template_placeholders()` — tech-gtm 自有确定性 lint 闸门

这是核心。**结构化检测**，不依赖占位符提示语的措辞（中/英文/任意措辞都能抓）：

```python
def check_template_placeholders(prs, *, fail_on_prompt=True):
    """构建期闸门:遍历每页占位符,若 slide 占位符文本为空,按 idx 反查版式同 idx 占位符;
    若版式占位符带非空提示语 → 该空占位符会渲染版式提示 → 报告。

    机制:slide 占位符清空(.text='')后文本为空,但版式层提示语仍在,渲染时显示。
    纯文本 lint 读 slide 层(空)抓不到,必须按 idx 对应到版式层取提示语。

    返回 findings 列表 [{slide, idx, type, layout_prompt}]。
    fail_on_prompt=True 时,有 finding 则 raise(构建期硬失败,逼构建者填或删)。
    模板无关、措辞无关、确定性。
    """
    findings = []
    for i, slide in enumerate(prs.slides, 1):
        lay = slide.slide_layout
        lay_ph_by_idx = {ph.placeholder_format.idx: ph for ph in lay.placeholders}
        for ph in list(slide.placeholders):
            if (ph.text_frame.text or "").strip():
                continue                       # 已填充,无残留
            idx = ph.placeholder_format.idx
            lph = lay_ph_by_idx.get(idx)
            if lph and (lph.text_frame.text or "").strip():
                findings.append({
                    "slide": i, "idx": idx,
                    "type": str(ph.placeholder_format.type),
                    "layout_prompt": lph.text_frame.text.strip(),
                })
    if fail_on_prompt and findings:
        msg = "模板占位符残留:以下页有空占位符会渲染版式提示语(需填充或删除元素):\n" + \
              "\n".join(f"  slide {f['slide']} idx={f['idx']} ({f['type']}) 提示={f['layout_prompt']!r}"
                        for f in findings)
        raise RuntimeError(msg)
    return findings
```

调用点：`new_deck.py` 在 `dk.lint_layout(prs, strict=True)` 之后、`prs.save()` 之前调用 `check_template_placeholders(prs)`；build 脚本（如 LoopEngineering 的 build.py）在 save 前也应调用（文档指引）。

### 2.4 文档警示

`tech-gtm-training-deck/references/deck-from-template.md`：在 cover/strip_branding 失败模式段后加一条 🔴 MUST：

> **禁止用 `placeholder.text = ""` 清空占位符**——空占位符仍会渲染版式/母版的提示语（如"点击添加页面大标题"）。要自绘就**删除占位符元素**（`cover()` 用 blank 版式 / `cover_from_template(drop_title=True)` / `dk.drop_placeholders`），或**填充它**。构建期 `check_template_placeholders(prs)` 会硬失败捕获此类残留——它按 idx 反查版式占位符提示语，措辞无关。

### 2.5 测试（tech-gtm 仓库内 pytest）

`tests/test_template_placeholders.py`（新增）：
- `test_chap_no_sub_drops_idx10`：`chap()` 不传 sub → slide 上无 idx10 占位符（已被删）。
- `test_cover_from_template_strips_title`：`cover_from_template(drop_title=True)` → slide 上无 idx0 占位符。
- `test_check_flags_cleared_placeholder`：构造 `add_slide(带提示的版式) + placeholders[0].text=''` → `check_template_placeholders` 返回该 finding 并 raise。
- `test_check_passes_filled_or_dropped`：填充占位符 / 删除占位符 → 无 finding 不 raise。
- fixture 用 conftest 的 `make_test_prs` + 造一个带提示语的 layout（python-pptx 加占位符设 prompt 文本）。

复用 `tests/test_cover_pagetypes.py` 的 `FakeDeck` + `make_test_prs` 范式。

## 3. 不做

- 不改 slide-maker 包（npm，会被覆盖）。
- 不重新生成 LoopEngineering-deck（用户要求仅 skill 层持久化）。可选：临时用新 lint 跑一次当前 build.py 验证闸门能抓到首页残留（仅验证，不交付）。
- 不在 deckkit `lint_layout` 加检测（在包内，不持久）。

## 4. 验证

1. `cd tech-gtm-training-deck && python -m pytest tests/` 全绿（含新增 test_template_placeholders）。
2. 可选验证闸门有效：临时在 LoopEngineering build.py save 前加 `check_template_placeholders(prs)`，跑构建 → 应 raise 并报 `slide 1 idx=0 提示='点击添加页面大标题 30号'`（不交付，仅证闸门能抓首页 bug）。
3. 把封面改成 `cover_from_template(drop_title=True)` 后重跑 → 不再 raise（证修复路径有效）。

## 5. 改动清单

| 文件 | 改动 |
|---|---|
| `scripts/deck_helpers.py` | 修 `chap()`（无 sub 删 idx10）；新增 `cover_from_template()`；新增 `check_template_placeholders()` |
| `references/deck-from-template.md` | 加 🔴 MUST 警示段 |
| `tests/test_template_placeholders.py` | 新增 4 个测试 |
| `scripts/new_deck.py` | save 前调 `check_template_placeholders(prs)` |

## 6. 风险

- `check_template_placeholders` 误报风险：仅当"slide 占位符空 且 版式同 idx 占位符带提示语"才报。已填充或已删占位符均不报。模板未带提示语的占位符也不报（空但不渲染提示）。低误报。
- `cover_from_template` 删 idx0 后，若构建者后续又 `s.placeholders[0]` 访问会 KeyError——但既已删除就不该再访问，符合"删除即自绘"契约。文档需点明。
