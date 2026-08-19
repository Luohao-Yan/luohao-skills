# tech-gtm-training-deck 封面链路重设计

- **日期**:2026-08-19
- **skill**:`D:\develop\luohao-skills\tech-gtm-training-deck`
- **触发**:用该 skill 生成《龙岗政策打标》deck 时,封面链路连续踩了四个坑,全部是 skill 层面的缺陷,非用户操作问题。本 spec 据此重设计封面链路。

## 1. 问题(实战证据,非假设)

用 `tech-gtm-training-deck` 生成 deck 时,封面阶段连续四次出错:

| # | 现象 | 根因(skill 层面) |
|---|---|---|
| 1 | 封面"没背景"——主体大片白底 | `cover(style="band")` 只画左侧 0.32in 窄色带,主体留白;docstring 主动"避免继承模板 logo 版式"而弃用模板封面 |
| 2 | `style="hero"` 阴阳对半——上半色块下半白底,硬分界,且与白底内页不协调 | `cover(style="hero")` 画 `H*0.58` 色块 + 下半白底,机械对半;自绘配色与模板内页不同源 |
| 3 | 主标题"龙岗政策打标"从未渲染——读图看到的"主标题"其实是副标题 | 填模板 layout 15 占位符时 `s.placeholders[0]` 取不到 idx0 占位符,抛 KeyError 被 `except Exception: pass` 静默吞掉 |
| 4 | layout 15 自带的「图形 12」logo 图 strip_branding 没清到,要手动删 | 调研修正:`strip_branding` 其实**已在遍历 layouts**(第 330 行 `targets = masters + layouts`),logo 确实会被清。但暴露了更深 bug——见 #5 |
| 5 | **封面主标题占位符 idx0 被 strip_branding 误删**,导致 `placeholders[0]` 取不到(坑 #3 的真正根因) | idx0「标题 2」占位符默认文本是"金山云标准模板-大标题 38号",含"金山云"关键词,被 `_is_brand_text` 命中**连占位符 shape 一起删了**。strip 应只删非占位符的 brand text shape,占位符的默认文本由 cover 填时覆盖 |

**共性**:skill 的 cover 哲学是"弃模板自绘",但自绘质量不如模板自带封面(渐变圆/点阵),且自绘/填占位符两条路都有 bug。模板自带封面是最稳的封面来源,却被弃用。

## 2. 设计决策(已与用户确认)

1. **cover 哲学翻转**:优先用模板自带封面 layout(填占位符),用不上才回退自绘。模板封面质量高、与内页同源。
2. **填占位符可靠**:cover 内部填占位符,取不到就自绘兜底,**绝不 `except: pass` 静默吞错**——取不到要 log + fallback。
3. **strip_branding 不删占位符**:调研发现它已在遍历 layouts,真正 bug 是误删含品牌词的占位符(idx0「标题 2」默认文本"金山云标准模板-大标题 38号"被当 brand text 删了,导致 #3)。改为删 brand text 时跳过 placeholder。
4. **inspect 选占位符最丰富的封面 layout**:在候选里选占位符最多者(标题+副标题+日期优先),而非首个命中。

两个低风险默认(不再追问):
- `profile.yaml layouts.cover` 指向 inspect 选中的 idx,build 脚本用 `D.P.layout("cover")` 取,不硬编。
- `cover(..., use_template=True)` 默认用模板;`use_template=False` 走自绘 fallback。

## 3. 详细设计

### 3.1 `cover()` 翻转哲学(`scripts/deck_helpers.py`)

**新签名**:`cover(prs, deck, subject, subtitle="", meta="", use_template=True, style="band")`

**`use_template=True`(默认,新增主路径)**:
1. 取 `deck.P.layout("cover")` 得到模板封面 layout idx;若 profile 无 cover role,记 log 并回退自绘(见下)。
2. `add_slide(layout_idx)`。
3. **填占位符,按类型/位置智能匹配**:
   - 遍历该 slide 的 placeholders,按 `placeholder_format.type` 分:TITLE(1) → 主标题 subject;BODY(2) → 第一个填 subtitle,第二个填 meta;DATE(16) → meta。无占位符匹配到的字段,自绘兜底(见下)。
   - 占位符存在但 idx 与预期不符时(如本例 idx0 缺失),不靠固定 idx,靠 type 匹配——这是 #3 的根治点。
4. **字号下限**:主标题若占位符未给大字号或字号过小,cover 覆盖设 ≥44pt(13.3in 画布的体面下限),避免"中等字号"撑不起封面。副标题 ≥18pt,meta ≥13pt。
5. 不清 logo——strip_branding 已预先清过(见 3.2)。
6. 返回 slide。

**自绘兜底(每个字段独立判断)**:
- 某字段(如主标题)无匹配占位符 → 用 `dk.text` 在该字段的"默认位置"自绘一个文本框:主标题 (1.57,1.25,7.81,1.57)、副标题 (1.57,2.99,6.61,0.53)、meta (1.61,4.19,2.96,0.79)——这些是模板 layout 15 原占位符位置,作为兜底坐标。
- **绝不静默吞错**:占位符访问异常时 `print("[cover] <field> 占位符缺失,自绘兜底")` 再兜底,不 `except: pass`。让"取不到"可观测,这是 #3 的根治点。

**`use_template=False`(回退自绘,保留原逻辑)**:
- 现有 band/hero 自绘逻辑保留,但修两个体验 bug:
  - band:主体不再大片留白——加一个极浅的全屏底色块(anchor 的 5% 不透明铺底)或左色带加宽,避免"没背景"感(#1)。
  - hero:去掉 `H*0.58` 机械对半——改为整页渐变底(anchor 深色 → 透明),标题居中,无硬分界线(#2)。
- 此路径是 fallback,默认不用。

### 3.2 `strip_branding()` 不删占位符(`scripts/deck_helpers.py`)

**现状**:`strip_branding` 第 330 行已 `targets = list(prs.slide_masters) + list(prs.slide_layouts)`——**已在遍历 layouts**,layout 级 logo 图(「图形 12」)本来就被清(实测:strip 删了 5 pics + 12 texts)。所以"扩 layout 级"不需要做。

**真正的 bug**:`_is_brand_text` 命中后,连**占位符 shape 一起删**了。本例 idx0「标题 2」占位符默认文本"金山云标准模板-大标题 38号"含"金山云",被误删——这正是 #3 主标题丢失的根因(不是 `placeholders[0]` 取不到,是占位符被 strip 删了)。

**改后**:
- 删 brand text 时**跳过占位符**:`if _is_brand_text(sh) and not sh.is_placeholder:` 才删。占位符的默认文本不该导致整个占位符被删——build 填占位符时会覆盖默认文本。
- logo pic 删除逻辑不变(`_is_logo_pic` 只命中右上角小图,占位符不是 PICTURE,不会误删)。
- 其余不变(`keep_logo=True` 跳过、大装饰图保留、返回计数)。

**效果**:strip 后 idx0「标题 2」占位符保留,cover 能 `placeholders[0]` 取到并填主标题(#3 根治)。layout 级 logo 仍被清(原行为不变)。

**验证命令**:`python -c "import sys; sys.path.insert(0,'scripts'); from slide_maker_path import find_slide_maker; sys.path.insert(0,find_slide_maker()); import deckkit as dk; from deck_helpers import strip_branding; prs=dk.open_template(r'<TPL>'); strip_branding(prs); print([sh.placeholder_format.idx for sh in prs.slide_layouts[15].placeholders if sh.is_placeholder])"` 应输出 `[0, 10, 11]`。

### 3.3 `inspect` 选占位符最丰富的封面 layout(`scripts/inspect_and_profile.py`)

**现状**:`key_layouts()` 启发式:
```python
if any(k in n for k in ["标题幻灯片","标题页","Title Slide"]) and "cover" not in role_map:
    role_map["cover"] = idx  # 首个命中即定,不再看后续
```
本例 layout 11「标题页」(只 TITLE)先命中,盖过 layout 15「标题幻灯片」(TITLE+BODY+BODY)。

**改后**:
- 收集所有封面候选 `[(idx, name, placeholders), ...]`(名字含上述关键字的 layout)。
- 给每个候选打分:TITLE 占位符 +1,BODY 占位符 每个 +1,DATE 占位符 +1;有 TITLE 才入围。
- 选分最高者;平局取 idx 较小者(稳定)。
- 写入 `profile.yaml layouts.cover` = 该 idx,`profile.md` 标注"占位符最丰(N 件)"。
- 无候选 → `cover` role 不写,cover 运行时回退自绘并 log。

**效果**:本模板 cover=15(三占位符)而非 11(一占位符)(#3 预防,#4 让 cover 拿到对的 layout)。

### 3.4 profile.yaml / build 脚本

- `profile.yaml layouts.cover` 由 inspect 写入正确 idx;build 脚本 `D.P.layout("cover")` 取,不硬编(本 deck build.py 里 `prs.slide_layouts[15]` 硬编可改回 `D.P.layout("cover")`)。
- `templates/build_skeleton.py`:`cover(prs, D, subject, subtitle, meta)` 调用签名兼容(新增 `use_template` 默认 True,skeleton 不传即用模板)。

## 4. 波及文件

| 文件 | 改动 |
|---|---|
| `scripts/deck_helpers.py` | `cover()` 翻转哲学 + 填占位符兜底 + 字号下限;`strip_branding()` 删 brand text 时跳过 placeholder(修误删 idx0) |
| `scripts/inspect_and_profile.py` | `key_layouts()` cover role 选占位符最丰富者 |
| `SKILL.md` | §Cover & branding / 失败模式段:哲学从"自绘避免 logo"改"优先模板+兜底" |
| `references/deck-from-template.md` | "inherited template logo/branding" 失败模式段 + build rhythm 段同步 |
| `templates/build_skeleton.py` | cover 调用兼容(签名加 use_template 默认 True) |
| `examples/deepseek-harness/build.py` | 若调 cover,同步(检查后定) |

## 5. 测试

`tests/` 现有:`test_cover_pagetypes.py`、`test_template_pool.py`、`test_arch_layers.py`、`test_network_topo.py`、`test_brief.py`、`conftest.py`。

- **`test_cover_pagetypes.py` 扩展**:
  - 用例 A:cover(use_template=True) + 模板有 cover layout(三占位符)→ 占位符被正确填进(subject/subtitle/meta 各归位)。
  - 用例 B:cover(use_template=True) + 占位符缺失(如 idx0 无 TITLE)→ 自绘兜底 + **不静默吞错**(捕获 log 或断言 slide 上有该文本)。
  - 用例 C:主标题字号 ≥44pt 下限。
  - 用例 D:use_template=False 仍工作(band/hero 不崩)。
- **strip_branding 新用例**(可能新文件 `test_strip_branding.py`):用现有模板(其 layout 15 的 idx0 默认文本含"金山云"、且「图形 12」是 layout 级 logo)断言:strip 后 **idx0 占位符仍保留**(`[0,10,11]`),且「图形 12」logo 被清。这是 #3/#5 的回归保护。
- **inspect 用例**(扩 `test_template_pool.py` 或新文件):对现有两个模板跑 inspect,断言 `cover` role = 占位符最丰富者(本模板 = 15,不是 11)。
- 所有测试在 `D:\develop\luohao-skills\tech-gtm-training-deck` 跑 `pytest tests/` 通过。

## 6. 验收标准

1. 用本 spec 改后的 skill 重生成《龙岗政策打标》deck 封面:`cover(prs, D, "龙岗政策打标", subtitle, meta)`(默认 use_template=True)即得到模板原版封面(白底+渐变圆+点阵+白字大标题),无金山云标识,主标题"龙岗政策打标"在且字号撑得起封面。
2. build_skeleton.py 默认调 cover 不改也能出对的封面。
3. `pytest tests/` 全绿。
4. `strip_branding` 后,任意 layout 的右上角 logo 图 + 品牌文本被清(不再有「图形 12」残留)。
5. inspect 对现有两模板都选出占位符最丰富的封面 layout。

## 7. 非目标(不做)

- 不改内页 helper(quad_grid/steps3/arch_layers/network_topo 等)——本次痛点只在封面链路。
- 不改 brief.yaml / Stage 0/1/2 流程。
- 不碰 `editing-office-docs` skill(本次未用)。
- 不重写 cover 自绘 fallback 的全部样式——只修 band/hero 两个明显体验 bug,fallback 是次路径。
