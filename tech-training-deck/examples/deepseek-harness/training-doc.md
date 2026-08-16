# DeepSeek Harness 能力培训 · 给公司领导（示例培训稿）

> 本文档是 `tech-training-deck` skill 的 Stage 2 产物示例——一份完整的 7 节技术培训稿。
> 它脱敏自一次真实工作：从本地源码实测 + 本机应用核实 + 公开信息，做成给领导的培训材料。
> **可作为你写自己培训文档的结构模板**：7 节骨架 + 每结论带 `file_path:line` 证据 + 每节带诚实限度对冲。
>
> 证据来源：dsh 部分基于本地开源仓库源码（MIT）；Pi 部分基于本机已安装的 `@earendil-works/pi-coding-agent`；
> WorkBuddy / WPS Comate 基于本机已安装应用的文件级实测；WPS 灵犀基于官方与公开信息。
> （本示例已脱敏：去掉内部模板路径、作者署名、特定客户措辞，保留结构与证据范式。）

---

## 目录

- [0. 一页纸结论(TL;DR)](#0-一页纸结论tldr)
- [1. 这是什么:DeepSeek Harness 速览](#1-这是什么deepseek-harness-速览)
- [2. 核心机制:一切皆插件是怎么实现的(架构讲透)](#2-核心机制一切皆插件是怎么实现的架构讲透)
- [3. WorkBuddy / WPS 灵犀 / WPS Comate 到底是什么](#3-workbuddy--wps-灵犀--wps-comate-到底是什么)
- [4. DeepSeek 怎么通过 Harness 锁定模型底座市场](#4-deepseek-怎么通过-harness-锁定模型底座市场)
- [5. DeepSeek Harness vs Pi 对比](#5-deepseek-harness-vs-pi-对比)
- [6. 启示与建议](#6-启示与建议)
- [附录:证据出处](#附录证据出处)

---

## 0. 一页纸结论(TL;DR)

**先纠正最容易被讲混的点**：DeepSeek Harness(dsh)、WorkBuddy、WPS 灵犀、WPS Comate 是不同归属的东西，市面常被混为一谈。

| 名字 | 归属 | 形态 | 含 Coding? | 含 WPS 办公功能? | 模型后端 | 内嵌的 Agent harness |
|---|---|---|---|---|---|---|
| **DeepSeek Harness (dsh)** | DeepSeek 官方,MIT 开源 | 开源 Agent 框架(运行时底座),Web UI + CLI | 是 | 否 | 多 provider,默认 DeepSeek | 自家 Cordis |
| **WorkBuddy** | **腾讯**，非 DeepSeek | 桌面工作台,Electron | **有**（内置 codebuddy CLI） | 否(靠技能间接读写) | `copilot.tencent.com` | 自家 codebuddy |
| **WPS 灵犀**(="千万办公") | 金山 WPS | AI 办公智能体 | **是**(Python/Node/AirScript) | **是**(深度集成 WPS Office) | WPS 自有 | (独立产品) |
| **WPS Comate** | 金山 WPS | 桌面 Agent,Qt5 原生 | **有** | 否(经 JSAPI 操控,API 级) | `comate.wps.cn` 代理 | **内嵌 Pi** v0.79.3 |

**一句话理解 DeepSeek Harness**：它是 DeepSeek 开源的"让大模型能真正动手干活的运行时框架"。官方公式 **`Agent = 模型 + Harness`**——模型负责"想"，Harness 负责理解环境、调工具、组织多步任务。对标 Claude Code / Codex，但走开源路线。

**核心架构**：没有特权内核，模型适配器、工具、会话日志、agent 循环本身都是插件，由 **Cordis** 插件框架驱动；换一个 Provider 插件就能换模型，指向远程沙箱就能把 Bash/终端/LSP 一并搬走，agent 甚至能在创造模式里改自己的插件。

**战略判断**：模型层趋同质化、利润变薄，**谁掌握 agent harness 谁就掌握模型分发权**——DeepSeek 开源 Harness 的意图，是用"动手层"的标准化反向锁定"模型层"。

**一个关键发现**：金山自家的桌面 Agent 产品 **WPS Comate 内嵌的就是 Pi**(`@earendil-works/pi-coding-agent` v0.79.3)——第三方开源 harness 已被产品化落地。

---

## 1. 这是什么:DeepSeek Harness 速览

### 1.1 定位
dsh 是 DeepSeek AI 开源的 agent harness。它不是聊天产品、不是办公套件、不是 IDE，而是"让大模型在真实环境里持续工作的运行时底座"。
- 仓库 `github.com/deepseek-ai/deepseek-harness`，MIT，完整源码开放。
- 公式 **`Agent = 模型 + Harness`**；开发者可在配置层替换/扩展任何能力，无需改源码。
- 对标 OpenAI Codex、Anthropic Claude Code；区别在于开源与"一切皆插件"。

### 1.2 怎么跑起来
```sh
npx @deepseek-ai/dsh web          # Web UI,默认 http://127.0.0.1:3080
dsh --profile headless "跑测试并修复失败"   # 命令行一次性任务
```
同一内核，不同插件组合 = Web UI / headless / ACP / JSON-RPC 多种形态。

### 1.3 四种运行模式
| 模式 | 说明 | 场景 |
|---|---|---|
| **标准** | 默认,带全套工具 | 日常开发 |
| **PTC** | 模型生成 TypeScript 程序组合多轮工具调用 | 一连串按序操作 |
| **极简** | 只留 Shell + 文件编辑 | 跑模型基准 |
| **创造** | agent 动态挂载/卸载临时插件、改自己的配置 | 高级实验(信任等级=shell 访问) |

### 1.4 生态热度与诚实提示
- 开源约 2 天 GitHub star 近 9.5 万，24h 内 288 个 `dsh-plugin` 仓库；仓库含 230+ 个 workspace 成员。
- **当前为开发者预览版，官方明确"未来将出现破坏兼容性的变更"**。面向开发者/二开，不适合追求稳定上生产。

---

## 2. 核心机制:一切皆插件是怎么实现的(架构讲透)

### 2.1 底层是 Cordis:五个核心概念
dsh 底层是 **Cordis**(vendor 引入的插件框架，源自 Koishi 生态)。五个概念：
1. **插件 = 实现 Service 的对象**（带 `apply(ctx)` 的函数或 `Service` 子类）。
2. **上下文(ctx)是服务的容器**，按稳定 `ctx.<key>`（如 `ctx.tools`、`ctx.llm`）找服务，**不 import 实现**——这是"可替换"的关键。
3. **`inject` 声明依赖**，加载顺序由依赖决定（空间可组合性）。
4. **类型化事件**，`emit`/`waterfall`/`parallel`/`serial` 四模式：观察·改写·扇出·按序。
5. **注册是可逆的副作用**，`ctx.effect()`/`ctx.on()` 安装的，卸载时自动撤销（时间可组合性）。

> 架构文档原话："产品的每一部分都是插件，包括模型适配器、工具注册表、会话日志，以及 agent loop 本身……**不存在需要打补丁的特权内核**。"

### 2.2 能力 Seam(接缝):一个能力 = 三个角色
- **Service Definition**(声明接口，占一个 `ctx.<key>`)
- **Service Provider**(并列可换的实现)
- **Consumer**(使用方，通常是面向模型的工具)
> "文件系统与进程提供方共享同一个执行世界，把它们指向远程沙箱，也就把 Bash、PTY 和 LSP 一并搬了过去。"

### 2.3 三个 Seam 实例:换一个插件换一个世界
| Seam | 并列的 Provider(可换) | Consumer |
|---|---|---|
| **`ctx.llm`**(模型底座) | `llm-deepseek`(原生)、`llm-pi-ai`(经 pi-ai 接任意)、`llm-replay`(回放) | `agent-loop` |
| **`ctx.shell`+`ctx.subprocess`** | `bash-local`/`bash-sandbox`/`pwsh-local`；`subprocess-local`/`subprocess-e2b`(远程) | `tool-bash`/`terminal-bash`/`lsp-stdio` |
| **`ctx.subagents`** | `spawn-in-process`/`fork-in-process`/`acp`/`codex`/`claude-code`/`dsh-sdk` | `tool-subagent` |

**换模型底座 = 换一个 `ctx.llm` Provider 插件**——这是第 4 节战略的核心证据。接私有/远程环境 = 把 `subprocess` 指向 E2B，Bash/终端/LSP 全跟着搬走。

### 2.4 插件树怎么长 + 创造模式
- **profile/bundle/preset**：运行中的 dsh 是一棵插件树，按序叠加；任何层可 patch 其下所有层（`agent.cordis.yml` 的 isolate realm 分组，实测 `:104/:137/:174`）。
- **加能力 = 挂插件**：加模型/工具/shell/终端/命令/后台任务/文件系统……全是挂插件（架构文档:112-131）。
- **创造模式 self-modification**：agent 运行时检查、挂载、卸载自己的插件。底层 `vm` 沙箱(`sandbox.ts:129/96/227`) + 白名单 guard(`guard.ts:551/626/718`) + `cordis_run` 工具。信任等级 = shell 访问。

---

## 3. WorkBuddy / WPS 灵犀 / WPS Comate 到底是什么

| 产品 | 归属(本机核实) | 含 Coding? | WPS 办公功能? | 内嵌 harness |
|---|---|---|---|---|
| **WorkBuddy** | 腾讯 | 有(内置 codebuddy CLI) | 否(靠技能间接读写) | 自家 codebuddy |
| **WPS 灵犀**(="千万办公") | 金山 WPS | 是(Python/Node/AirScript) | **是**(深度集成 WPS Office) | (独立) |
| **WPS Comate** | 金山 WPS | 有 | 否(经 JSAPI 操控,API 级) | **内嵌 Pi** v0.79.3 |

**关键纠偏**：① WorkBuddy **不是 DeepSeek 的**(腾讯，DeepSeek 仅其可选模型之一)；② WPS Comate **内嵌 Pi**(不是金山自研)；③ 只有 WPS 灵犀真正含 WPS 办公编辑能力。三大 harness 互不内嵌：WorkBuddy 用 codebuddy、WPS Comate 用 Pi、DeepSeek 用 dsh。

---

## 4. DeepSeek 怎么通过 Harness 锁定模型底座市场

### 4.1 现状
模型层趋同、API 价格战、利润变薄。竞争上移到 agent 层：谁能把模型变成"能持续干活的 Agent"，谁就掌握分发。

### 4.2 打法(四步)
1. **默认带 DeepSeek**：模型在 dsh 是可换插件，但默认体验/示例/生态偏 DeepSeek。
2. **先选 harness 再选模型**：团队基于 dsh 建技术栈后迁移成本陡增；换模型只是一个插件——留 harness 比留模型容易。
3. **数据/反馈回流**：更多 Agent 跑在 DeepSeek 上，真实任务数据反哺模型迭代。
4. **生态飞轮**：Cordis + `dsh-plugin` 话题 + Code Mode/Python SDK；24h 已 288 个插件仓。

### 4.3 意图
**谁定义了 harness 标准，谁就定义了模型被"怎么用、用谁的"。** DeepSeek 同时开源模型(V 系列)和 harness(dsh)，在模型层和动手层都布点——用动手层标准化反向强化模型层粘性。

### 4.4 诚实限度与风险
- 开发者预览，有破坏性变更，现阶段面向开发者/二开，非稳定生产形态。
- "锁定"是软锁定(默认偏好 + 迁移成本)，非硬绑定：模型确是可换插件，开发者随时能切。
- 框架层竞争激烈(Claude Code、Codex、各类开源 agent 框架都在抢动手层标准)，dsh 是否成事实标准仍未定。

---

## 5. DeepSeek Harness vs Pi 对比

> **纠偏**：Pi 不是金山自研，是独立开发者(earendil-works)的开源终端 coding harness(MIT)。但金山 WPS Comate 已内嵌采用，且本团队也已接公司模型在用。

| 维度 | DeepSeek Harness (dsh) | Pi |
|---|---|---|
| 定位 | 官方开源,有 Web UI+CLI | 独立开发者,纯终端 TUI(已入 Comate) |
| 架构 | 一切皆插件,Cordis DI 容器 | 最小核心,注册式扩展 |
| 模型 | 默认 DeepSeek,多 provider | 不锁定,30+ provider |
| 能力包 | 官方维护几十个(一等公民) | 核心 5 包,余靠扩展 |
| 部署 | `npx dsh web` 一键起 | `npm i -g pi-coding-agent` |
| 底层 | 把 pi-ai 当可插拔后端 | 把 pi-ai 当内置底座 |

**关键同源**：两者共用 `@earendil-works/pi-ai` 作 LLM 抽象层——用 Pi 调通公司模型的经验可直接复用到评估 dsh，迁移成本不高。

---

## 6. 启示与建议

> 立场说明：本节按"正用公司云模型 + Pi 做方案的团队"角度写。若立场不同请自行调整。

1. **把"agent harness = 模型分发权"列为新战略变量**——政企选型可能先选框架再选模型。
2. **研究 dsh seam 化对自身架构的借鉴**——适配私有化"换模型/换部署/换沙箱"诉求。
3. **Pi 路线可坚定**——已被产品化验证、与 dsh 同源可迁移；短期提效，dsh 作平台化备选观察。
4. **勿上生产**——dsh 是开发者预览、有破坏性变更；定位预研/POC，版本收敛再评估。
5. **厘清口径**——对外：WorkBuddy=腾讯、灵犀=金山、Comate=金山(内嵌Pi)、Pi=第三方、dsh=DeepSeek；讲混损害可信度。

---

## 附录:证据出处

- **A. DeepSeek Harness(本地源码)**：`README.zh.md`(定位/预览提示)、`docs/architecture.zh.md:9-13`(一切皆插件)、`:102-107`(seam 三角色)、`:112-131`(加能力=挂插件)、`docs/cordis-primer.zh.md:7-14`(五概念)、`apps/cli/config/agent-presets/standard/agent.cordis.yml`(实测 251 行,三个 isolate 分组)、`packages/extensions/cordis-host-runner/src/{sandbox,guard}.ts`(self-modification)、`packages/llm/llm-pi-ai/`(pi-ai 适配器)。
- **B. Pi(本机已装)**：`@earendil-works/pi-coding-agent`(MIT)；本机 `models.json`(模型配置)；与 dsh 共用 `@earendil-works/pi-ai`。
- **C. WorkBuddy(本机实测)**：`AppData/Local/Programs/WorkBuddy/`(腾讯,Tencent Technology 签名,Electron 5.3.13)；内置 `codebuddy` CLI(tree-sitter/终端/沙箱)；`copilot.tencent.com` 模型后端。
- **D. WPS Comate(本机实测)**：`AppData/Local/WPS Comate/`(金山,Qt5 原生 0.1.0)；内嵌 `@earendil-works/pi-coding-agent` v0.79.3(Bun 运行时)；多 agent + 内置技能 + Git/Node/Python；`comate.wps.cn/llmproxy/v1/user` 模型后端。
- **E. WPS 灵犀(官方/公开)**：`lingxi.wps.cn`；含 Python/Node/AirScript 代码执行 + WPS Office 深度集成。
- **F. 三大 harness 互不内嵌(本机实测)**：WorkBuddy→codebuddy、WPS Comate→Pi、DeepSeek→dsh，三者互不内嵌。
- **G. 公开信息来源**：DeepSeek Harness 仓库 github.com/deepseek-ai/deepseek-harness；产品页 deepseek.com/harness；Pi github.com/earendil-works/pi；WPS 灵犀 lingxi.wps.cn；WorkBuddy 公开报道(腾讯云 CodeBuddy 团队)。
