# Deck reference layout — a reusable编排样板 for high-density tech-training decks

## 这是什么 / 何时用

这是 Stage 3 的**编排参考样板**：当你拿到一个企业/政企模板、探查出主色、要做一份**高密度技术培训 deck**（给领导讲清一个技术主题）时，照这个骨架组织页面。

它不是方法论——那是 `deck-from-template.md` 的流程 + 7 个失败模式；也不是完整案例——那是 `examples/deepseek-harness/`；而是两者之间的**中间层**：一个可复用的「页序列 + 配色语义契约 + 视觉语汇」模板，已清除任何具体品牌。

**适用**：高密度、讲者备注驱动、15-17 页的技术培训 deck。
**不适用**：纯 keynote（太密）、营销 deck（不需要这么结构化）。

## 配色语义契约（通用，不限主调）

模板探查出 `accent1..6` 后，把它们绑到**四个语义角色**（+ 一个可选深色页底）。这是「主题色 → 内容语义」的绑定层，机器无法推断，必须人填（`profile.yaml` 的 `semantic_contract`）。build 脚本通过 `D.anchor / D.comparator / D.neutral / D.emphasis` 取色。

| 角色 | 语义 | 用在哪 | 选色指引 |
|---|---|---|---|
| `anchor` 主锚 | 本次主主题 / 核心结论 / 主标题 | 标题、主主题卡边框、编号圆、结论页底 | = 用户指定的主色（accent1） |
| `comparator` 对比 | 对比对象 / 次要产品 / 另一条路线 | 对比产品卡、次要点 | 主色的**对比/互补**色（红→橙；蓝→橙/青；绿→琥珀/品红） |
| `neutral` 中性 | 表头 / 中性说明 / 结构线 | 表头色条、分隔线、次要标签 | 深中性（深蓝灰/深石板/深墨绿），低饱和 |
| `emphasis` 强调 | take-away / 关键句 / 金句 | callout label、关键发现高亮、结论金句 | 暖强调（金/橙黄/琥珀），高明度 |
| `dark_bg` 深底(可选) | 深色关键发现页底 | 关键发现页背景 | 极深（近黑 + 主色调，如 `#2A1418`） |

**不同主调的填法**（举例，以你探查出的实际 accent 为准，别抄 hex）：
- **红主调政企**：anchor=主红 / comparator=橙 / neutral=深蓝灰 / emphasis=金 / dark_bg=深红黑
- **蓝主调科技**：anchor=主蓝 / comparator=橙(暖对比) / neutral=深石板 / emphasis=青或金 / dark_bg=深蓝黑
- **绿主调**：anchor=主绿 / comparator=琥珀或品红 / neutral=深墨绿灰 / emphasis=金 / dark_bg=深绿黑
- **深色/单色主调**：anchor=主色 / comparator=主色降饱和 / neutral=灰 / emphasis=主色提亮

> 原则：**一色一义**——同一个 hue 在全 deck 只代表一个语义角色（见 slide-maker `semantic-color-contract`）。anchor 色只给主主题，不给对比对象；别让红色同时是主主题和某个对比产品的色。

## 页型编排骨架（高密度技术培训，15-17 页）

经过一次完整实战验证的页序列。每页给：**页型 / 内容角色 / 配色用法**。照抄骨架、换内容即可。

| # | 页型 | 内容角色 | 配色/形式 |
|---|---|---|---|
| 1 | 封面（`cover()` 自绘，非模板 logo 版式） | 断言主标题 + 故事线副标题 + 受众/日期 | 左渐变色带(band)/大渐变色块(hero),anchor→comparator 渐变,无模板 logo |
| 2 | 三段目录（3-col） | 把领导关心的 N 问作骨架，每栏一 PART + 一句问句 | 三栏分别用 anchor/comparator/neutral 色条 |
| 3 | 章节页 ×N | PART 分隔 | 模板章节 layout；深色背景白字 → `chap()` 加半透明深衬底（修对比坑） |
| 4 | 归属/对比表（4-card 或 table） | 「X 是谁的 / 含什么 / 不含什么」速查 | 每卡顶色条 = 该卡归属色 |
| 5 | 双栏对比（2-col） | 直答「除了 X 还有什么」/ 两条路线 | 左右各一对比色，底部红字直答关键判断 |
| 6 | 深色关键发现（dark layout） | 最值得汇报的一个发现 | dark_bg 底 + emphasis 高亮关键词 |
| 7 | 公式 + 四模式（居中大公式 + chips） | 一句话定位 + N 种模式 | 公式用 anchor/comparator 色，chips 逐个 appear-build |
| 8 | 大白话概念图（插座/容器比喻） | 把抽象机制画成生活比喻 | 中央大容器（anchor 描边）+ N 插槽，右栏「想换 X？换一个插头」 |
| 9 | 分层堆叠图（竖向卡片 + 向下箭头） | N 层结构，每层一句大白话 | 每层色条，层间 `dk.arrow(down)` |
| 10 | signature move（插槽 → N provider 卡） | 核心论点做成几何隐喻 | 左深色插槽（emphasis 标）→ 红箭头 → 右 N 卡，默认那张高亮 |
| 11 | 编号步骤（numbered-steps） | N 步打法/路径 | 编号渐变圆（anchor→comparator）+ 卡片，appear-build |
| 12 | 追问双栏（支持/存疑 或 正/反） | 预判听众追问，正反对比 | 左「支持」(绿) / 右「存疑」(橙)，底部结论 callout |
| 13 | 建议编号（5-row） | 「我们怎么做」直答 | 编号圆 + 卡片，底部口径行 neutral |
| 14 | 结论页（red_conclusion） | 三段式（短/中/长期 或 借鉴/接入/卡位） | 主色底 + emphasis 金句 |
| 15 | 附录（证据出处） | 按来源分组 | 小字、neutral 分组标签 |

> **节奏原则**：别让一种页型连出现两次。归属表(4-card)后接双栏(2-col)，深色页后接浅色公式页，堆叠图后接插槽图——形式交替才不疲劳。signature move 是全 deck 视觉峰值，放第 10 页左右，前后用结构图铺垫和承接（`carried_by`）。

## 内容页型 helper 速查（`scripts/deck_helpers.py`）

骨架表里的页型都有现成 helper，配色全走 profile（换主色→全 deck 跟着变）：

| 页型 | helper | 用法要点 |
|---|---|---|
| 封面 | `cover(prs, D, subject, subtitle, meta, style="band"/"hero")` | 断言主标题 + 故事线 + 受众日期；渐变从 profile；**别再裸填 cover 版式占位符** |
| 四宫格(2×2) | `quad_grid(slide, D, [{tab,head,body},…]×4)` | 四分类/对比，红橙交替边框 + tab 角标 |
| 三步走 | `steps3(slide, D, [{tag,head,body},…]×3)` | 落地路径/阶段，顶部 Step 色条 |
| 左文右代码 | `code_card(slide, D, left_title, left_body, code_title, code_lines)` | 原理 + 代码示例，右卡深色底 |
| 左文右图/架 | `text_right_card(slide, D, …, right_title, right_body)` | 场景 + 方案，右卡可换 `arch_layers` |
| 分层架构 | `arch_layers(slide, layers)` | 全宽色带分层 + 组件块 |
| 网络拓扑 | `network_topo(slide, nodes, links)` | 图标节点 + 边到边连线 |

> 这些 helper 抽自真实模板页骨架（如记忆培训 deck 的 slide7 四宫格 / slide22 三步走 / slide16 代码卡），不是凭空设计——照真实页型复刻，配色随 profile 变。

## signature move 范式

signature move = **把核心论点做成一个几何隐喻**，是全 deck 的视觉峰值，不是装饰。

通用做法：
1. 找出这次 deck 的**一句话核心论点**（如「模型是可换零件」「换底座不用改代码」）。
2. 把它画成一个**可操作的几何**：一个插槽 + N 个可换的卡，箭头表示「换这个 = 换那个」。
3. 默认那张高亮（anchor 色 + ★默认标），其余降一档。
4. 让 2-3 张其他页**结构上承载同一母题**：大白话插座图、分层堆叠图都用「插槽/可换」语汇，让 motif 在 deck 里回响。

> 判断标准：抽掉这张页，论点就讲不清——它是论点本身，不是配图。如果每张页都能追溯到某个默认模板，deck 就是「带额外步骤的模板」，不是设计。

## 视觉形式清单（组件级语汇）

从模板几何词汇里来，无 SVG 也能画（见 `deck-from-template.md` `icon_family`）：

- **卡片 + 顶部色条**：`card()` + `dk.box(corners='top')` 顶色条 = 该卡归属色。最常用的「带归属的块」。
- **编号渐变圆**：`num_circle()`，anchor→comparator 径向渐变，白字编号。用于步骤/要点。
- **章节页深色衬底**：`chap()` 在模板章节 layout 的深色背景图上，给白字标题加半透明深色衬底条（修对比坑）。
- **深色关键发现页**：模板 dark layout，`dark_bg` 底 + `emphasis` 高亮关键词 + 浅色正文。
- **bottom_callout 贴底**：`bottom_callout_at(bottom_y=7.07)` 锚定显式底，全 deck 一致底边距（修悬浮坑；别用裸 `dk.bottom_callout`）。
- **箭头堆叠**：层间 `dk.arrow(direction='down')` 表「上一层搭下一层 / 组合方向」。
- **插槽图**：深色 `dk.box` 当插槽 + 红箭头 + N 张 provider 卡。signature move 专用。
- **分隔细线**：`dk.box(h=0.012)` 当卡内分隔，neutral 灰。

## 怎么用（拿到模板 + 主色后）

1. 对模板跑 `inspect_and_profile.py` → `profile.yaml`（accent1..6 + 字体 + layout idx）。
2. 填 `semantic_contract`：按上面「配色语义契约」把 accent 绑到 anchor/comparator/neutral/emphasis/dark_bg。
3. 照「页型编排骨架」定你的页序列（你的内容映射到第 4-13 页的页型）。
4. 定 signature move：找你的一句话核心论点，画成插槽/可换几何。
5. 用 `templates/build_skeleton.py` 起手（已从 profile 读色，非硬编），逐页填。
6. 渲染 + critic 2 轮 + 修（见 `deck-from-template.md` 流程 + 7 个失败模式）。
7. 门禁：`lint_layout(strict=True)` 0 critical + `density.waived`（高密度培训 deck 的合规出口）。

## 和其他文件的关系

- `deck-from-template.md` = **流程 + 7 个失败模式**（怎么做、别踩什么坑）
- 本文件 = **编排样板 + 视觉语汇**（照什么骨架排、用什么形式）
- `examples/deepseek-harness/` = **完整实例**（这套样板的一个真实落地，含 build.py / profile.yaml / training-doc.md）
- `templates/build_skeleton.py` = **空白骨架**（从 profile 读色，复制改内容）
