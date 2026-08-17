# tech-training-deck

把一个技术主题，做成给领导的可视化培训材料：**调研 → 培训文档 → 模板品牌 PPT** 一条龙。

这是一个 [Claude Code](https://claude.com/claude-code) skill。它把"把 XX 技术讲给领导听/做成汇报 PPT"的完整工作流沉淀成可复用流程：源码实测 + 本机应用核实 + 公开信息（每结论带 `file_path:line` 证据，不编造）→ 7 节结构化培训 md → 套用**你自己的 .pptx 模板**生成品牌一致的 deck（经独立 critic 两轮审）。

- **一个完整流水线**，三段编排，同事一句话从技术主题产出整套培训材料。
- **模板无关**——用你自己的企业/个人 .pptx 模板，skill 不内置任何版权模板。
- **诚实调研契约**——每个结论附 `file_path:line` 证据，查不到就说查不到，绝不臆测。
- **门禁 + 豁免**——技术培训 deck 天然高密度，机械 lint 的投影 floor 会报不过；skill 保留"带书面豁免理由放行"机制，不把 deck 降级成空洞。

## 它解决什么

让一个技术主题（一个开源框架、一个新产品、一次技术调研）从"我大致了解"到"我能给领导讲 15 分钟、有 deck、经得起追问"——而且全程有据可查、品牌一致、可复现。

适合：技术架构师/方案架构师/研发 leader 给管理层做技术培训、做竞品/方案汇报、把一次调研做成可交付材料。

## 依赖

**Stage 3（生成 PPT）依赖 [slide-maker](https://github.com/addsumtech/slides_maker) skill**（提供 deckkit / anim / render / lint 引擎）。Stage 1-2（调研、写文档）不依赖它，可独立用。

## 安装

```sh
# 1) 先装依赖 skill（Stage 3 的 PPT 引擎）
npx skills add addsumtech/slides_maker -g -y

# 2) 装本 skill
npx skills add Luohao-Yan/luohao-skills@tech-training-deck -g -y
#   或直接 git clone:
#   git clone https://github.com/Luohao-Yan/luohao-skills ~/.claude/skills/luohao-skills/

# 3) 预检环境 + 装 Python 依赖
python check_env.py
pip install -r requirements.txt
```

`check_env.py` 报告 slide-maker 是否已装、Python 依赖是否齐、LibreOffice 是否在（渲染用），并打印每项缺失的修复命令。它只报告，不自动装。

装好后，Claude Code 在会话启动时自动发现本 skill——你不用记 skill 名，直接说"帮我把 XX 技术讲给领导听 / 做个 XX 技术培训 deck / 把这份调研做成汇报 PPT"即可触发。

## 用法

跟 Claude 说你的需求即可，例如：

- "调研一下 DeepSeek Harness，给领导做个培训 deck，用我们公司的 .pptx 模板"
- "把这份框架调研做成给团队的培训材料和 PPT"
- "对比一下 A 和 B 两个产品，做个给领导的汇报"

Claude 会按三段走：
1. **调研**（用后台 agent 并行读源码/查本机应用/核实公开信息，每个结论附证据）
2. **写培训 md**（7 节骨架 + 证据附录）
3. **生成 deck**（探查你的 .pptx 模板 → 生成 profile → 设计 → build → 渲染 → critic 两轮 → 修 → 交付）

## 仓库结构

```
tech-training-deck/
├─ SKILL.md              # 主编排:三段工作流 + 触发条件 + 依赖声明
├─ references/           # 四篇方法论
│  ├─ investigate.md     #   阶段1:源码实测+本机核实+公开信息,证据链,归属纠偏,不编造
│  ├─ training-doc.md     #   阶段2:7节培训md通用骨架 + 诚实限度对冲
│  ├─ deck-from-template.md # 阶段3:模板→profile→设计→build→critic→门禁豁免
│  └─ workflow.md         #   三段衔接 + 哪步自动/哪步人工判断
├─ scripts/              # 工具
│  ├─ inspect_and_profile.py  # 探查.pptx→profile.yaml+profile.md(修配色漂移坑)
│  ├─ load_profile.py     #   build脚本从profile.yaml加载品牌色(非硬编)
│  ├─ deck_helpers.py     #   通用helper:set_title/num_circle/chap/card/notes
│  └─ new_deck.py         #   生成build脚手架
├─ templates/
│  └─ build_skeleton.py   # build脚本模板(从profile读,含完整deck节奏)
├─ examples/
│  └─ deepseek-harness/   # 完整脱敏范例(培训md + build + profile)
└─ check_env.py / requirements.txt / LICENSE(MIT)
```

## 示例

`examples/deepseek-harness/` 是一次真实工作的脱敏范例：从 DeepSeek Harness 源码调研 → 7 节培训 md → 17 页品牌 deck（signature move 把"模型即插件"画成可换插槽图）。看它的 `README.md` 了解三段怎么衔接，`training-doc.md` 可直接作为你写培训文档的模板。

> 该示例**不含任何企业 .pptx 模板本体**（版权），只含脱敏的 md / build / profile。复现需你提供自己的 .pptx 模板。

## 关键设计

- **依赖 slide-maker，不重造轮子**——PPT 段 import slide-maker 的 deckkit/anim，不 vendor 6990 行。
- **profile 机制修漂移坑**——`inspect_and_profile.py` 探查你的模板生成结构化 `profile.yaml`，build 脚本从 yaml 读配色/字体，不再人工抄硬编码（手工抄易与模板漂移）。
- **门禁 + 豁免**——技术培训 deck 高密度，`.deck-gates.json` 的 `density.waived`/`provenance.waived` 记录书面豁免理由放行，而非降级成空洞 deck。layout criticals（溢出/越界）永不豁免。
- **章节页对比修复**——深暖背景图上白字对比不足时，`deck_helpers.chap` 自动加半透明深色衬底条。

## License

MIT。见 [LICENSE](LICENSE)。
