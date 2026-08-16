# Example: DeepSeek Harness 技术培训 deck

这是一个**完整范例**,演示 `tech-training-deck` skill 的三段流水线如何从零走到一套领导培训 deck。它脱敏自一次真实工作(本地源码实测 + 本机应用核实 + 公开信息 → 培训 md → 模板品牌 PPT)。

> **本目录不含任何企业 .pptx 模板本体**(版权)。`profile.yaml` 是格式示例,颜色取自一个典型红主调政企模板的 theme clrScheme 作示范;同事用自己的模板跑 `inspect_and_profile.py` 生成自己的 profile。

## 这个案例讲了什么

主题:DeepSeek 2026-08-13 开源的 agent harness(`dsh`),"一切皆插件"架构。给公司领导的 15 分钟培训,讲清:
1. **厘清产品**:市面易混的 DeepSeek Harness / WorkBuddy / WPS灵犀 / WPS Comate 到底各是谁的、含不含 Coding、含不含办公(归属纠偏是重点)
2. **看懂架构**:Cordis 五概念 → 能力 seam → 插件树 → 创造模式(self-modification)
3. **战略**:DeepSeek 用开源 harness 锁定模型底座市场的四步打法
4. **对比与建议**:dsh vs Pi(同源 pi-ai,分道于架构)+ 给"我们"的五条建议

## 三段流水线对应的产物

| Stage | 产物 | 在本目录 / 上游 |
|---|---|---|
| 1. Investigate(源码实测+本机核实+公开信息,带 `file_path:line`) | 后台 Explore agent 报告(散落,结论沉淀进 md) | 本次会话(不入仓) |
| 2. Training doc(7节骨架 + 证据附录) | `training-doc.md` | **本目录** |
| 3. Deck from template | `build.py` + `profile.yaml` | **本目录**(需你提供 .pptx 模板才能跑出 deck) |

## 怎么复现这个案例

```sh
# 1. 装好本 skill + 依赖 slide-maker(见仓库根 README)
# 2. 准备一个你自己的 .pptx 模板(任意企业/个人模板)
# 3. 探查它生成你的 profile.yaml(覆盖本目录的示例 profile.yaml):
python ../../scripts/inspect_and_profile.py /path/to/your.pptx --out .
# 4. 填 profile.yaml 的 semantic_contract(把 accent 绑到语义角色,仿本文件)
# 5. 改 build.py 里的 TPL 路径为你的 .pptx
# 6. 跑 build:
python build.py
# 7. 渲染 + 看效果(用 slide-maker 的 render_deck):
python ~/.claude/skills/slide-maker/scripts/render_deck.py training-deck.pptx render
```

## build.py 的结构(供学习)

`build.py` 是本次真实 build 脚本的通用化版本:
- 从 `profile.yaml` 读品牌色/字体/layout(**非硬编**),通过 `load_profile` + `deck_helpers.Deck`
- 完整 deck 节奏:封面 → 目录 → 3 章节页 → 内容页(4-card 对比 / 双栏对比 / 深色关键发现 / 大公式+四模式 / 5行概念 / **signature move 插槽图** / 3栏 / 红色结论 / 附录)
- **signature move**:slide 10 把 `ctx.llm` 画成可换插槽 → 红箭头 → 三张 provider 卡(deepseek 高亮默认),每张标"换这个=换模型底座"——核心论点做成可视隐喻
- 动画:多步页(slide 8/11/13)用 `Build.step()` 逐个出现
- 讲者备注:每页 `notes()` 放话术,幻灯片只留短语
- 门禁:`lint_layout(strict=True)` + `.deck-gates.json` 的 `density.waived`(技术培训 deck 高密度的合规出口)

## 为什么这个案例值得看

它同时演示了本 skill 的几个非显然之处:
- **归属纠偏**(WorkBuddy=腾讯非DeepSeek、Pi=第三方但金山已采用)用本机实测破除市面误读
- **signature move** 不是装饰,是论点本身做成几何
- **门禁+豁免**:技术培训 deck 天然超 lint 的 40词/18pt 预算,带书面豁免理由放行而非降级成空洞 deck
- **章节页对比修复**:深暖背景图上白字对比不足 → 加半透明深色衬底条(`deck_helpers.chap`)

`training-doc.md` 是完整的 7 节培训稿,可直接作为写自己培训文档的模板。
