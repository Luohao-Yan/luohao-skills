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
| 4 | layout 15 自带的「图形 12」logo 图 strip_branding 没清到,要手动删 | `strip_branding` 只遍历 masters,不清 layout 级 shape |

**共性**:skill 的 cover 哲学是"弃模板自绘",但自绘质量不如模板自带封面(渐变圆/点阵),且自绘/填占位符两条路都有 bug。模板自带封面是最稳的封面来源,却被弃用。

## 2. 设计决策(已与用户确认)

1. **cover 哲学翻转**:优先用模板自带封面 layout(填占位符),用不上才回退自绘。模板封面质量高、与内页同源。
2. **填占位符可靠**:cover 内部填占位符,取不到就自绘兜底,**绝不 `except: pass` 静默吞错**——取不到要 log + fallback。
3. **strip_branding 扩到 layout 级**:同时清母版级 + 各 layout 级 logo 图/品牌文本,不再只清母版。
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

### 3.2 `strip_branding()` 扩 layout 级(`scripts/deck_helpers.py`)

**现状**:`for master in prs.slide_masters: for layout in master.slide_layouts:` 只清母版继承的。实际 `strip_branding` 遍历 masters,但 layout 自带的 shape(非母版继承)不清。

**改后**:
- 遍历范围:`prs.slide_masters` 的每个 master + 该 master 的每个 `slide_layouts`——**对每个 layout 本身的 shapes 也跑 `_is_logo_pic` / `_is_brand_text` 清理**(不只是母版继承的)。
- 判据不变:`_is_logo_pic`(右上角小图:`left > W*0.79 and top < H*0.13, w<1.6, h<0.7`)+ `_is_brand_text`(含 金山云/KSYUN/Copyright/北京金山云网络技术/金山软件/kingsoft/ksyun)。
- 大装饰背景图(章节页点阵)仍保留——`_is_logo_pic` 的位置+尺寸判据已排除大图。
- `keep_logo=True` 仍整体跳过。
- 返回计数 `{pics, texts}` 含 layout 级清掉的。

**效果**:layout 15 的「图形 12」logo 被 strip 自动清,cover 不用手动删(#4 根治)。

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
| `scripts/deck_helpers.py` | `cover()` 翻转哲学 + 填占位符兜底 + 字号下限;`strip_branding()` 扩 layout 级 |
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
- **strip_branding 新用例**(可能新文件 `test_strip_branding.py`):优先用现有模板(其 layout 15 自带「图形 12」logo 图)断言 strip 后该 layout 的 logo shape 被清;若现有模板不便于断言,再造一个带 layout 级右上角小图的假模板。
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
