# 咨询叙事 deck 能力增强 — 设计文档

> 日期：2026-08-26 · 范围：autodeck skill（仓库版） · 参考：`AI-Story_CC_260812_Rev05.pptx`
> 落点：`D:/develop/luohao-skills/autodeck`（git 仓库内，持久） · 不动 slide-maker npm 包

## 1. 背景与问题

### 1.1 用户反馈
当前 skill 产出的 PPT "太简单、太单调"。参考样本是一份金山云《政企 AI 战略叙事》客户高层沟通材料（18 页 / 1209 形状 / 206 图标），信息密度高、版式多样、品牌框架强。

### 1.2 参考 PPT 的设计语言（已实测提取，见 `_ppt_skill_analysis/reference_design_analysis.md`）

- **配色**：蓝梯度为主（主深蓝 `#17479E` → 浅蓝面板 `#EFF4FD`），**红色克制强调**（`#E60023`，只用于"那一个关键点"：关键数字红框、标题下红短线、第 4 编号圆点）。
- **字体**：MiSans（正文，1040 处）+ 思源宋体（大标题，30 处，衬线制造仪式感对比）。
- **品牌框架**：每页贯穿——页眉左上机构名 + 右上 logo + 页脚分隔线 + 页码 `XX/20` + 标题下红短线。
- **版式高度多样**（12+ 种）：5 阶段横向流程、双环形飞轮、4×6 能力矩阵、四层架构、数据指标大数字卡、三情景测算表、ROI 公式可视化、左侧导航总分总页、3+5+3+横幅总结页——几乎不重复。
- **图形语言**：线性图标密集（每页 10–30 个，"每个概念配一个图标"）、编号圆点（蓝常规，第 N 点红突出）、栏目标题栏（蓝底白字）、白卡蓝边、浅蓝提示/结论区（灯泡）。

### 1.3 根因（为什么产出"太简单单调"）

slide-maker 整套体系围绕"演讲视觉辅助 / 一页一想法 / 少字大图"建立。高密度咨询 deck 在其中处处被推回：

| # | 根因 | 证据 |
|---|---|---|
| 1 | 无"咨询/战略叙事"purpose，最接近的 investor readout 反规定 low density | design-by-purpose.md:201 |
| 2 | `consulting` 预设 guard 主动限图标密度（"sparingly, not on every tile"）且无品牌页眉页脚 | presets.py:200-204 |
| 3 | 默认 lint 在 ~40 词/页、~70% 占用即报 TEXT WALL / CROWDED | lint_deck.py:1411-1422 |
| 4 | deckkit 里参考 PPT 的 13 版式只有 5 个有现成组件（且多是卡片网格），飞轮/平面四层/侧导航/蓝头矩阵/红框 ROI/多区总结页都得手拼 | deckkit.py 实测 |
| 5 | 多样性闸门按规模分级 + 一句话豁免，中小册无硬约束 → 模型退回"卡片网格"最短路径 | slide-design.md:430-432 |
| 6 | 无"每页 logo+机构名+页码"统一品牌框架组件，chrome 靠每页手动调，易遗漏 | deckkit.py grep 无 brand_frame |
| 7 | 图标哲学是"克制按需"，与参考 PPT"每概念配图标"密集叙事反向 | icons.md:224-235 |

### 1.4 架构约束（延续 2026-08-25 spec）

- `slide-maker` 是 npm 安装包，改它会被升级覆盖 → **不持久**。
- `autodeck` 仓库版（`D:/develop/luohao-skills/autodeck`）是源码，有自有 `scripts/`（`deck_helpers.py` / `builtin_palettes.py` / `new_deck.py`），调 slide-maker 的 deckkit 基元组合。
- **持久化改动落仓库内 tech-gtm 自有代码**，不动 slide-maker 包。新组件在 `deck_helpers.py` 里调 `dk.*` 基元组合实现（不重写 deckkit）。

## 2. 目标

- 让 tech-gtm 能**稳定产出**参考 PPT 那种"高密度咨询 / 战略叙事 deck"：信息密度饱满、版式多样不重复、强品牌框架、内容布局有骨架。
- **通用能力**：抽象成可复用能力，不固化金山云品牌（金山云色值仅作为 `consulting-blue` 预设的取色参考）。
- **持久化**：改动全部落 git 仓库内，随仓库提交，不被 npm 覆盖。
- **中等力度**：配色 + 版式组件 + 品牌框架 + 页型骨架 + 内容布局；不动 SKILL.md purpose 体系与密度门禁（那是重度力度的范围）。

## 3. 设计（5 层，全部落 tech-gtm 仓库内）

### 3.1 第 1 层 · 配色 — `scripts/builtin_palettes.py` 加 `consulting-blue` 预设

在现有 `PALETTES` 字典加一项，遵循现有结构（canvas / colors / fonts / semantic_contract / layouts），**不加新语义 key**，面板/边框用 accent5/6 直取，最小侵入：

| 语义角色 | accent | 色值（取自参考 PPT） | 用途 |
|---|---|---|---|
| anchor 主锚 | accent1 | `#17479E` | 主结构色：编号圆、标题栏、节点 |
| comparator 次级 | accent2 | `#2E7CE4` | 次级节点、流程条 |
| neutral 中性 | accent3 | `#5A6472` | 结构线、次文字 |
| emphasis 强调 | accent4 | `#E60023` | **红克制**：关键点、关键数字红框、标题红线 |
| （卡片边框） | accent5 | `#C6D8F5` | 白卡蓝边（helper 直取） |
| （浅蓝面板） | accent6 | `#EFF4FD` | 提示/结论区/面板背景（helper 直取） |

- `fonts`：`latin=MiSans, ea=MiSans`；大标题可选 `思源宋体`（helper 支持 `font=` 覆盖）。
- `layouts`：无模板时全 0（blank 起手），与现有预设一致。
- **密度出口**：`density.waived` 仍走高密度合规出口（现有门禁机制），consulting-blue 预设不在 lint 阈值上开特例——高密度靠"门禁豁免"而非"调阈值"，避免污染其他预设。

### 3.2 第 2 层 · 版式组件 — `scripts/deck_helpers.py` 加 8 个 helper

全部遵循现有 `Deck` 类取色模式（接收 `deck`，走 `deck.anchor/comparator/neutral/emphasis` 语义色 + `deck.P.color("accent5/6")` 直取面板/边框，调 `dk.*` 基元组合，**不硬编颜色**），补齐"必须手拼"的 5 个 + 强化 3 个：

| helper | 解决的参考版式 | 关键设计 |
|---|---|---|
| `brand_frame(slide, deck, page, total, org, logo=None)` | 每页品牌框架 | 页眉机构名 + 右上 logo + 页脚分隔线 + 页码 `page/total` + 标题下红短线。**核心，解根因 #6** |
| `horizontal_pipeline(slide, deck, stages)` | 5 阶段横流程（子项带图标） | `stages=[{name, icon, items}]`，编号圆 + 子项图标 + 阶段间箭头 |
| `flywheel(slide, deck, nodes)` | 双环形飞轮 | 闭环节点 + 弧形箭头；可调两次画左右双环 |
| `capability_matrix(slide, deck, rows, cols, cells)` | 4×6 蓝头能力矩阵 | 行列头蓝底白字 + 白卡单元格 |
| `kpi_row(slide, deck, kpis)` | 4 大数字指标卡 | 大数字 + 单位 + 对比小字 |
| `roi_formula(slide, deck, factors, result)` | ROI 公式可视化 | `数字×数字×…≈结果`，**结果红框**突出（emphasis 描边） |
| `side_nav(slide, deck, items, active)` | 左侧纵向导航栏 | 总分总页左侧导航 + 高亮当前项 |
| `summary_board(slide, deck, top, mid, bot, banner)` | 3+5+3+横幅总结页 | 上判断 + 中流程 + 下动作 + 深蓝结论横幅 |

> `side_nav` 是纯视觉导航栏；"本章 N 子点跨页连续编号"的状态管理由第 5 层的 `chapter_nav` 负责，二者分工：`chapter_nav` 算状态、`side_nav` 画。

### 3.3 第 3 层 · 编排骨架 — `references/deck-reference-layout.md` 加"咨询叙事编排骨架"小节

**新增小节，不替换**现有技术培训骨架。内容：

- **12–18 页型序列**（参考 PPT 实测页序，作为咨询叙事 deck 的可复用骨架）：
  封面(左标题+右面板) → 一张图总览(横流程) → 挑战(N 卡+提示) → 飞轮(双环) → 总体框架(N 阶段) → 分层架构 → 能力矩阵 → 三分类路径 → 纵向流程 → 价值(侧导航总分总) → 总结(3+5+3+横幅) → 数据机会(KPI+流程) → 测算对比表 → ROI → 附录。
  每页型给：**页型 / 内容角色 / 对应 helper / 配色用法**。
- **节奏原则**：版式轮换不重复（与现有骨架同精神，"别让一种页型连出现两次"）。
- **signature move 范式（咨询版）**：把核心论点做成飞轮 / 插槽几何，是全册视觉峰值。
- **图标密集叙事指导**：咨询叙事 deck 明确放开"每概念配图标"——这是 tech-gtm 对咨询场景的**特化**，与 slide-maker `icons.md` 的克制哲学区分开（tech-gtm 自己的 references 里说明，不改 slide-maker）。

### 3.4 第 4 层 · 品牌框架 — `brand_frame` 系统 + `new_deck.py` 脚手架接入

- `brand_frame()` 组件（第 2 层已含）。
- 在 `scripts/new_deck.py` 的 `SKELETON` 里，把 `brand_frame(s, D, page, total, org)` 作为**内容页标准步骤**（封面 / 章节页跳过——它们有自己的 chrome），解决"每页记得分别调 logo+footer+页码"易遗漏的根因。
- 脚手架同时 import 新 helper，让生成的 `build_<topic>.py` 开箱即用。

### 3.5 第 5 层 · 内容布局 — 文档 + `chapter_nav` helper

这是"每章要讲的内容"的布局层，**补视觉层之外的缺口**。参考 PPT 的内容布局是三层：

1. **整体叙事弧**：封面"回答三个问题"(Why/How/WhyUs) = 全册三幕预告。
2. **章节展开**：大主题拆 N 子点，左侧导航跨页连续编号，逐页展开（参考 p11+p12"价值"章，导航 1–6 跨两页）。
3. **每页三段式骨架**：断言标题 + 支撑副标题 → 多模块证据区 → 底部结论/提示栏。

落地：

- **`references/deck-reference-layout.md` 加"咨询叙事内容布局"小节**：三幕叙事弧 + 章节展开模式 + 每页三段式骨架，配示例。
- **`scripts/deck_helpers.py` 加 `chapter_nav` helper**（比 `side_nav` 更上层）：
  - 管理一个"本章 N 子点 + 当前页讲到第几点"的状态对象（`ChapterNav(items=[...], start_page=K)`）。
  - 提供 `.render(slide, deck, current_page)`：算出当前页该高亮第几项 + 跨页连续编号，调 `side_nav` 画左侧导航。
  - 解决"跨页连续编号易错"——模型只需声明本章子点列表和起始页，编号/高亮状态由 helper 算。

## 4. 不做（out of scope，中等力度的边界）

- **不改 slide-maker npm 包**（会被覆盖）。
- **不改 tech-gtm `SKILL.md` 的 purpose 体系与密度门禁阈值**（那是重度力度；中等力度靠现有 `density.waived` 出口，不开新特例）。
- **不固化金山云品牌**：`consulting-blue` 是通用预设，金山云色值仅作取色参考；不内置金山云 logo / 机构名。
- **不新建独立 skill**：能力加到现有 tech-gtm 内。
- **不改 slide-maker 的 critic rubric / icons.md**（npm 包，且其克制哲学对其他场景仍正确；咨询密集图标在 tech-gtm 自有 references 里特化说明）。

## 5. 验证

- **代表页复现**：用 `consulting-blue` 预设 + 新 helper 重建参考 PPT 的 4 个代表页（封面 / 双飞轮 / 能力矩阵 / ROI 公式），与原图对比，确认设计语言到位。
- **lint 门禁**：`dk.lint_layout(prs, strict=True)` 0 critical；`check_template_placeholders` 通过。
- **回归**：现有 `tests/` 全过；现有 `slate-business` / `ink-data` 预设与原有 helper 行为不变（新加项不破坏既有）。
- **取色一致性**：换预设（consulting-blue → slate-business）全 deck 配色跟着变（验证语义色契约未被硬编破坏）。

## 6. 与现有文件的关系

| 文件 | 改动 | 角色 |
|---|---|---|
| `scripts/builtin_palettes.py` | +1 预设 `consulting-blue` | 配色层 |
| `scripts/deck_helpers.py` | +9 helper（8 版式 + chapter_nav） | 组件层 + 内容布局层 |
| `scripts/new_deck.py` | SKELETON 接入 `brand_frame` + import 新 helper | 品牌框架层 |
| `references/deck-reference-layout.md` | +2 小节（咨询编排骨架 / 内容布局） | 编排骨架层 + 内容布局层 |
| `SKILL.md` | 路由指向新骨架小节（一行） | 可发现性 |
| slide-maker npm 包 | **不动** | — |

## 7. 开放问题（实现时确认）

- `brand_frame` 的 logo：无模板时用 `dk.wordmark`（文字标）还是有可选 logo 参数？倾向 `logo=None` 时画机构名 wordmark，有 logo 路径时贴图。
- `flywheel` 弧形箭头：deckkit 无现成弧形连接器，需用 `dk.connector` 曲线或 `dk.box`+旋转近似——实现时验证可读性。
- `chapter_nav` 状态对象在 build 脚本里跨页传递的方式（实例化后传给每页 render）——实现时定接口。
