# Diagram types — content shape → diagram type → helper or recipe

## 何时读这个

Stage 3 的 **design gate** 时读——你给每页内容定视觉形态时。它补充两个已有文件:
- `deck-from-template.md` §text-list-where-a-diagram-belongs:教你「内容是结构就该画图,别列清单」(判别该不该画图)
- `deck-reference-layout.md` §内容页型 helper 速查:页型→helper 一对一映射(画哪种页)

本文件回答速查表没答的问题:**内容有结构时,该选哪种图?为什么?怎么画?** 尤其:有分支/决策/多角色的内容,**不要用 `steps3` 线性三步**——它画不出分支和泳道。这类内容用**决策流程图**(deckkit 原语拼,见 §user-flow-recipe)。

## 判别决策树 (命中即停,从上到下)

1. 内容有**分支/决策点**(if-else / 成功失败 / 条件分叉 / `?local=1 走本地`)?
   → **决策流程图** (§user-flow-recipe),**NOT steps3**
2. 内容有**多个角色/系统各走各的路径**(前端做X、后端做Y、Redis 存Z)?
   → **决策流程图 + 泳道** (§user-flow-recipe)
3. 内容是**前后对比**(同一流程的改造,旧 vs 新)?
   → `dk.flow_compare` (两行 stage chips)
4. 内容是**闭环**(输出反馈为输入,循环)?
   → `dk.cycle_diagram`
5. 内容是**纯线性步骤**(无分支无角色,就是 1→2→3)?
   → `steps3(slide, D, steps)` (3 步) 或 `dk.flow_chain` (N 步)
6. 内容是**分层堆叠**(不是流程,是层级,clients→gateway→services→data)?
   → `arch_layers(slide, layers)`
7. 内容是**网络拓扑**(多节点互连,非分层,部署/调用关系网)?
   → `network_topo(slide, nodes, links)`
8. 内容是 **4 个等权分类**(2×2 四象限)?
   → `quad_grid(slide, D, items)`
9. 以上都不是 → `text_right_card` 或 `deck-from-template.md` 的通用几何积木

> 混淆时问一句话:**去掉分支还能理解吗?** 不能 → 必须画决策流程图,不能用 steps3。
> steps3 是线性三列说明,把分支内容压成三段会丢掉「流程」的灵魂(决策点、起止、方向)。

## 内容形态 → 图类型 → 画法 对照表

| 内容形态 | 关键信号 | 图类型 | 画法 | 标准符号 |
|---|---|---|---|---|
| 分层堆叠 | 组件分层;多数边连相邻层 | 分层架构 | `arch_layers(slide, layers)` | 色带+组件块,`dk.arrow(down)` 支撑 |
| 网络拓扑 | 多节点互连;拓扑/部署位置是重点 | 网络拓扑 | `network_topo(slide, nodes, links)` | 图标节点+边到边连线 |
| 线性流程(3-5步无分支) | 顺序执行;无决策无角色 | 线性步骤链 | `steps3(slide, D, steps)` / `dk.flow_chain` | 矩形+箭头 |
| 4 等权分类 | 4 个独立等权重类别 | 四宫格 | `quad_grid(slide, D, items)` | 2×2 卡片,交替色 |
| 左文右代码 | 概念+代码片段 | 代码卡 | `code_card(slide, D, …)` | 左文右深色代码块 |
| 左文右大卡 | 场景+方案并排 | 文本右卡 | `text_right_card(slide, D, …)` | 左文右卡(可嵌 arch_layers) |
| **用户流程/决策流** | **有分支+决策点+起止+多角色** | **决策流程图** | **deckkit recipe (§user-flow-recipe)** | roundrect=起止·rect=动作·diamond=决策·parallelogram=输入输出·cylinder=数据存 |
| 旧vs新流程对比 | 同一流程前后改造 | 流程对比 | `dk.flow_compare(slide, …)` | 两行 stage chips,高亮瓶颈 |
| 循环反馈 | 输出反馈为输入成环 | 循环图 | `dk.cycle_diagram(slide, …)` | 环形节点+虚线反馈箭头 |
| 时序交互 | 多角色按时间消息交互 | 时序图 | deckkit recipe:`node` 生命线+`connector(head=open)` | 垂直生命线;实线=同步,开口=异步;见 `design-gallery.md:170` |
| 状态转换 | 实体在离散状态间转移 | 状态机 | deckkit recipe:`node(circle)` 状态+`connector` 转移 | 实心点=初始,靶心=终态,event[guard]/action;见 `design-gallery.md:171` |
| 数据管道 | 数据从左到右流经阶段 | 管道 | `dk.flow_chain(slide, …, vertical=False)` | 一列一阶段,箭头连接 |

## §user-flow-recipe — 决策流程图拼装

**不重造轮子**:slide-maker 的 `design-gallery.md:157-162` 已有完整 Decision flowchart recipe,`design-gallery.md:167-174` 有标准符号表。本节是 autodeck 视角的速查 + 两个 deckkit 原语没明说的坑(泳道、分支连线)。

### 核心 recipe (引用 design-gallery.md:157-162)
- Happy path 走一条直线 **spine**
- 决策处:成功分支续 spine,失败分支**侧出到一侧**
- 分支用 `elbow_connector` rejoin(若分支要汇回主线)
- 回环用 `loop_path` + `elbow_connector`(仅「重试/回环」场景)
- outcome label 在**出口箭头上**,按语义着色(good=proceed · risk=reject)
- 错误/异常路径**虚线 (dashed)** + risk 色
- spine 连线全力度,分支连线降一档(让主线先被读到)

### 标准符号 (引用 design-gallery.md:167-174)
| 符号 | deckkit 调用 | 语义 |
|---|---|---|
| 起止 | `dk.node(slide, x,y,w,h, "标签", shape="roundrect")` | 开始/结束 |
| 动作 | `dk.node(…, shape="rect")` | 处理步骤 |
| 决策 | `dk.node(…, shape="diamond")` | 判断分支 |
| 输入输出 | `dk.node(…, shape="parallelogram")` | 数据输入/输出 |
| 数据存储 | `dk.node(…, shape="cylinder")` | Redis/DB/文件 |
| 可选节点 | `dk.node(…, dashed=True)` | 推断/可选 |

> 起止用 **roundrect(圆角矩形)** 不是圆——这是 deckkit 标准 crib。`node(shape="circle")` 实为椭圆(要 w==h 才真圆),且 crib 不把它当起止。

### 连线
- 主线 spine:`dk.connect_boxes(s, rectA, rectB, color=anchor)` — 两端自动 edge-dock 到 block 边,不会从方块中心穿出(安全)。
- 分支:`dk.connect_boxes(s, dec_rect, outcome_rect, style="dashed", label="失败", color=risk)` — 失败分支去一个**终止节点**,不是回环。
- 回环(仅重试场景):`dk.elbow_connector(s, dk.loop_path(x_from, x_to, y_row, y_drop), style="dotted")`。

### 两个坑 (deckkit 原语没明说,实测撞过)

**坑1:泳道不能有 fill。** deckkit lint 把有 fill 的 AUTO_SHAPE 当 block(`containers_z`),连线端点落进泳道中央区会触发 `CONNECTOR_IN_BOX` critical。**泳道用 `fill=None`,只靠细边框+标题区分**:
```python
dk.box(s, 0.5, ly, 12.3, lane_h, fill=None,
       round=True, line=RGBColor(0xCC,0xCC,0xCC), line_w=0.8, r=0.04)
dk.text(s, 0.62, ly+0.04, 1.4, 0.3, [[(lane_name, 12, MUTE, True, False, dk.EAFONT)]], wrap=False)
```

**坑2:失败分支去终止节点,别用 loop_path 回环。** `loop_path` 的 U 形端点会落进泳道背景区触发 `CONNECTOR_IN_BOX`;失败分支(如 CSRF 拒绝)应画到一个**终止节点**(`connect_boxes` edge-dock 到 node 边,不进空区)。`loop_path` 只留给「重试回环」(回到自身流程某步)。

### 拼装样板 (build.py 片段,可直接拷改编用)

以 SSO 登录为例:3 泳道(前端/后端/Redis)+ 起止 + 动作 + 决策 + 数据存储 + 失败分支终止节点。

```python
s = prs.slides.add_slide(prs.slide_layouts[D.P.layout("content")])
set_title(s, "核心流程:SSO 登录", D.anchor)
MUTE = RGBColor(0x80,0x80,0x80); RISK = RGBColor(0xC0,0x40,0x2A)

# 1. 泳道(fill=None 避坑1;最底层背景)
lane_y, lane_h = 1.3, 1.6
for i, name in enumerate(["前端", "后端", "Redis"]):
    ly = lane_y + i * lane_h
    dk.box(s, 0.5, ly, 12.3, lane_h, fill=None, round=True,
           line=RGBColor(0xCC,0xCC,0xCC), line_w=0.8, r=0.04)
    dk.text(s, 0.62, ly+0.04, 1.4, 0.3,
            [[(name, 12, MUTE, True, False, dk.EAFONT)]], wrap=False)

# 2. 节点坐标(记 rect 供连线)
start = (1.2, 1.45, 1.5, 0.4); act = (3.4, 1.45, 1.8, 0.4)
dec   = (6.0, 2.95, 1.5, 0.7); store = (9.0, 4.5, 1.5, 0.5)
reject= (3.4, 4.5, 1.8, 0.4)

# 3. Z-ORDER: 泳道 → 连线 → 节点(node 盖端点 seam)
dk.connect_boxes(s, start, act, color=D.anchor)
dk.connect_boxes(s, act, dec, color=D.anchor)
dk.connect_boxes(s, dec, store, color=D.anchor, label="通过")
dk.connect_boxes(s, dec, reject, color=RISK, style="dashed", label="失败")  # 坑2:去终止节点
dk.node(s, *start, "登录",       shape="roundrect", accent=D.anchor)   # 起止
dk.node(s, *act,   "跳 UIAP",     shape="rect",      accent=D.anchor)   # 动作
dk.node(s, *dec,   "state 校验?", shape="diamond",   accent=D.emphasis) # 决策
dk.node(s, *store, "Redis 8h",   shape="cylinder",  accent=D.comparator)# 数据存储
dk.node(s, *reject,"CSRF 拒绝",  shape="roundrect", accent=RISK)        # 失败终止

dk.lint_layout(prs, strict=True)   # 无 critical = 配方对
notes(s, "SSO 有分支:state 校验通过建会话,失败拒绝。?local=1 走本地 BCrypt 是另一分支。")
```

### steps3 vs user-flow 判别口诀
- 看到「if/else」「成功/失败」「条件分支」「`?local=1` 走本地」→ **决策流程图**
- 看到「角色A做X,角色B做Y」→ 决策流程图 **+ 泳道**
- 看到「步骤1→步骤2→步骤3」纯顺序无分支 → `steps3`
- 混淆时:去掉分支还能理解吗?不能 → 必须决策流程图

## 和其他文件的关系
- `deck-from-template.md` §text-list-where-a-diagram-belongs = 该不该画图(判别)
- `deck-reference-layout.md` §helper 速查 = 页型→helper(画哪种页)
- 本文件 = 内容形态→图类型(画哪种图)+ user-flow recipe(怎么画决策流程图)
- `design-gallery.md:157-174` (slide-maker) = 决策流程图 recipe 原文 + 标准符号表(本文件引用,不复制)
