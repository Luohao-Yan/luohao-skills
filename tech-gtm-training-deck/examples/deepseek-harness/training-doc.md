# DeepSeek Harness 能力培训 · 给公司领导（示例培训稿）

> 本文档是 `tech-gtm-training-deck` skill 的 Stage 2 产物示例——一份完整的 7 节技术培训稿。
> 它脱敏自一次真实工作：从本地源码实测 + 本机应用核实 + 公开信息，做成给领导的培训材料。
> **可作为你写自己培训文档的结构模板**：7 节骨架 + 每结论带 `file_path:line` 证据 + 每节带诚实限度对冲。
>
> 证据来源：dsh 部分基于本地开源仓库源码（MIT）；Pi 部分基于本机已安装的 `@earendil-works/pi-coding-agent`；
> WorkBuddy / WPS Comate 基于本机已安装应用的文件级实测；WPS 灵犀基于官方与公开信息。
> （本示例已脱敏：去掉内部模板路径、作者署名、特定客户措辞，保留结构与证据范式。）

---

## 目录

- [0. 一页纸结论(TL;DR)](#0-一页纸结论tldr)
- [0.5 领导三问 · 直答速查](#05-领导三问--直答速查)
- [1. 这是什么:DeepSeek Harness 速览](#1-这是什么deepseek-harness-速览)
- [2. 核心机制:一切皆插件是怎么实现的(架构讲透)](#2-核心机制一切皆插件是怎么实现的架构讲透)
- [3. WorkBuddy / WPS 灵犀 / WPS Comate 到底是什么](#3-workbuddy--wps-灵犀--wps-comate-到底是什么)
- [4. DeepSeek 怎么通过 Harness 锁定模型底座市场](#4-deepseek-怎么通过-harness-锁定模型底座市场)
- [5. DeepSeek Harness vs Pi 对比](#5-deepseek-harness-vs-pi-对比)
- [6. 启示与建议](#6-启示与建议)
- [7. 预判追问三题(讲完答疑弹药)](#7-预判追问三题讲完答疑弹药)
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

## 0.5 领导三问 · 直答速查

> 本节给领导 30 秒抓到答案的三问直答,术语下沉到正文。每问附正文节号,深问再展开。

**问 ① DeepSeek Harness 如何实现"一切皆插件"?**
dsh 把每一项能力都做成一个可拔插的"插头",插在一块叫 `ctx` 的"插座板"上:模型(`ctx.llm`)、工具(`ctx.tools`)、命令行/沙箱(`ctx.shell`)、记忆(`ctx.sessions`)都是插头。想换模型就拔下 `ctx.llm` 换一个,调用方代码一行不改;想接私有环境就把 `ctx.shell` 指向远程沙箱,命令行/终端/LSP 全跟着搬走。最关键:没有特权内核,连 agent 循环本身都是一个插头——想加能力不是改框架,而是挂一个新插头,拔掉副作用自动撤销。底层这套机制叫 Cordis。(详见 1.5、2.1、2.3 节)

**问 ② WorkBuddy / 千万办公(灵犀)/ Comate 含 Coding 吗?除了 Coding 还有什么?WPS 功能在里面吗?**
四个产品归属不同、能力各异(本机实测 + 官方信息):
- **DeepSeek Harness(dsh)**:DeepSeek 官方开源,让模型干活的运行时框架,有编程能力,不含 WPS 办公。
- **WorkBuddy**:腾讯的(非 DeepSeek),有编程(内置 codebuddy 命令行);除了编程还有多 Agent、20+ 技能、企微/飞书遥控、定时任务、金融分析;WPS 办公**不在本体**,靠技能间接读写文件。
- **WPS 灵犀(=千万办公)**:金山自家,有编程(Python/Node/AirScript);除了编程还有对话、一键生成 Word/PPT、数据分析、网页自动化、AI 图像;**WPS 办公在,直处理 Word/Excel/PPT/PDF**——四者中唯一真正含 WPS 办公功能。
- **WPS Comate**:金山自家桌面 Agent,有编程;除了编程还有多 Agent(Excel/轻文档/渠道/定时/技能)、生图/生视频/OCR;WPS 办公不在本体,经 JSAPI 操控(API 级非完整编辑器)。**关键发现:Comate 内嵌的是第三方开源 Pi(v0.79.3),不是金山自研。**
(详见第 3 节)

**问 ③ DeepSeek 怎么通过 Harness 锁定模型底座市场?**
模型层趋同、利润变薄,竞争上移到 agent 层。DeepSeek 四步:① 模型在 dsh 是可换插件,但默认体验/示例/生态偏 DeepSeek,开发者起步默认带 DeepSeek;② 团队基于 dsh 建技术栈后迁移成本陡增,而换模型只是一个插件——留 harness 比留模型容易;③ 更多 Agent 跑在 DeepSeek 上,真实任务数据反哺模型迭代;④ 生态飞轮(Cordis + dsh-plugin 话题 + SDK)。一句话:谁定义了 harness 标准,谁就定义了模型被"怎么用、用谁的"——DeepSeek 同时开源模型和 harness,用动手层标准化反向锁定模型层。(详见第 4 节)

> 讲完 PPT 后领导可能再追问三题(为什么爆火 / 是否成中国标准 / 我们怎么用),答案见第 7 节。

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
- 开源约 2 天 GitHub star 近 9.5 万；仓库含 230+ 个 workspace 成员。**注意时效**：旧 `.dsh-plugin` 仓库插件市场已于 2026-08-09 移除，现在以 `dsh-plugin` GitHub topic + `dsh plugin add` 命令为准（详见 2.6）。
- **当前为开发者预览版，官方明确"未来将出现破坏兼容性的变更"**。面向开发者/二开，不适合追求稳定上生产。

### 1.5 整体架构全景(五层)

dsh 从底到顶五层，每层都是插件，上层组合下层：
- **Cordis 内核**(`vendor/`)：插件元框架（ctx 容器/inject/事件/注册可逆）。
- **核心服务 seams**(`ctx.<key>`)：ctx.llm / ctx.tools / ctx.agents / ctx.shell / ctx.fs / ctx.sessions / ctx.subagents。
- **能力插件包**(`packages/*`)：实现 seams 的具体后端（llm-deepseek/llm-pi-ai、tool-*、shell-*、fs、lsp、subagent-*、web、skill、workflow）。
- **组合包/组合点**：dsh-base bundle · preset(cordis.yml) · profile(用户 patch)。
- **apps 组装点**：apps/cli(dsh 命令) · apps/web · ACP · JSON-RPC。

组合方向自下而上，依赖方向自上而下（inject）。**host/client 双面**：core 既是被组合的插件集，也暴露 host/client 接口给外部进程集成——同一内核多种形态。

---

## 2. 核心机制:一切皆插件是怎么实现的(架构讲透)

> 〔备问弹药〕本节为讲者深问展开的弹药库,保留技术深度与 file_path:line 证据。领导不深问时,讲 0.5 节速查 + deck 大白话页即可,本节备查。

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

### 2.5 Agent loop：一轮 turn 怎么跑（ReactLoopAgent）

dsh 的 agent 循环由 `ReactLoopAgent` 驱动（`packages/core/agent/`），`while` 逐 **turn** 推进。一轮五阶段，每个阶段都是 Cordis 上可替换插件：
1. **构造请求 buildRequest**：上下文 + compaction 压缩 + 工具 schema 注入。
2. **调 LLM**：经 `ctx.llm` seam 调模型（deepseek/pi-ai/replay 可换）→ 流式输出 + tool calls。
3. **解析工具调用**：tool calls 落到 `ctx.tools` 对应工具。
4. **工具执行管线**：interaction 审批 → sandbox → 执行 → 结果喂回上下文。
5. **判停**：`agent/turn-stopping` 事件（goal 达成 / 用户中断 / max turns / 不再请求工具）。未停则继续下一 turn。

**四种模式不改 loop，改"工具集 + prompt"**：标准/PTC/极简/创造的主循环对所有模式完全一致——区别在 Cordis scope 父链注册的工具集和 prompt 段（PTC 用 `presentAs('code')` 把 schema 折叠成 `run_code`）。模式是配置层差异，不是 loop 分叉——正是一切皆插件。

### 2.6 生态：extensions 与插件分发

- **bundle / patch-layer**（`packages/bundle/`）：Cordis 配置 + 挂载代码的分发格式，可被上层 patch，无特权层。
- **官方插件安装**：`dsh plugin --profile <name> add <package-or-git-spec>`（npm 包或 git 仓库）。
- **发现渠道**：`dsh-plugin` GitHub topic（去中心化，非应用商店）。**时效**：旧 `.dsh-plugin` 仓库插件市场已于 2026-08-09 移除，以 GitHub topic + `dsh plugin add` 为准。
- **运行时自修改也属生态**：创造模式 agent 经 cordis-host-runner 临时挂载/卸载插件，等于"agent 给自己装临时插件"，和 `dsh plugin add` 同属"一切皆插件"。

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

> 〔备问弹药〕本节为对比深问弹药,领导深问 dsh vs Pi 异同再展开。

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

## 7. 预判追问三题(讲完答疑弹药)

> 讲完 PPT,领导可能追问这三题。本节是完整答案稿,每题带诚实限度对冲。所有结论只来自已确认的本地源码、本机实测、上轮调研与官方/公开信息;star 数等引用以 GitHub 公开数据为准,记忆数据标注"约/早期"。

### 7.1 为什么 dsh 爆火,Pi 却没有?

**dsh 爆火(已确认事实 + 分析)**:
- **品牌势能**:DeepSeek 是刚用 V 系列模型火过一次的中国 AI 头部公司,自带流量与信任——开源即聚焦。
- **官方全开源**:MIT,完整源码开放(非 demo),本地开源仓库可查。
- **形态广、门槛低**:Web UI + CLI + Python SDK + ACP/JSON-RPC,不只是命令行;有界面就降低了大众开发者门槛。
- **官方维护几十个能力包,开箱即用**(源码 `packages/*`):模型/工具/命令行/文件/子代理/网页/技能/工作流,一等公民。
- **架构叙事高**:一切皆插件 + Cordis + 同步发《时空可组合性》论文,有理论高度与记忆点("高速上换发动机")。
- **生态机制**:dsh-plugin GitHub topic + `dsh plugin add` + bundle/patch-layer 分发——去中心化但官方托底。开源早期(约 2 天)star 近 9.5 万、24h 内约 288 个 `dsh-plugin` 仓(早期数据,引用以 GitHub 为准)。
- **时机**:模型层趋同、agent 层竞争上移,开发者苦 Claude Code/Codex 闭源久矣,开源 agent 框架窗口打开。

**Pi 没同样爆火(已确认事实 + 分析)**:
- **独立开发者个人项目**:Mario Zechner(earendil-works),无 DeepSeek 级品牌势能与媒体资源。
- **纯终端 TUI,无 Web UI**:门槛高,只服务命令行开发者。
- **极简哲学**:把 subagent/plan/MCP/权限弹窗/后台 bash 都推给生态(README Philosophy 明列),不讨好大众开发者。
- **无官方能力包生态**:核心只 5 包(pi-ai/pi-agent-core/pi-coding-agent/pi-tui/pi-orchestrator),余靠扩展。

**关键转折(诚实)**:Pi 走"被产品集成"路线而非"自己爆火"——金山 WPS Comate 内嵌 Pi v0.79.3(本机实测)即证。两者定位不同:dsh 要做平台/标准(要爆火、要生态),Pi 要做被嵌入的极简内核(要被集成、不要爆火)。**Pi 没爆火不是失败,是路线选择**——它用"被金山产品采用"证明了价值,而非用 star 数。

> 诚实点:star ≠ 标准,爆火是"品牌 + 时机 + 叙事"共振,不代表技术更优;不编造 Pi 具体 star 数对比。dsh 爆火也不等于它能稳——见 7.2。

### 7.2 dsh 是否会成为 AI Agent 应用的中国标准?

**支持"最强候选"**:
- 唯一中国头部 AI 公司(DeepSeek)官方全开源 agent harness——品牌 + 开源 + 完整性三合一,国内目前独此一家有此量级。
- Cordis 时空可组合性有理论高度 + 论文 + 架构文档,可被引用为"方法论",不止是工具。
- seam 化适配中国政企"私有化、换模型、换部署、换沙箱"的强诉求——这恰是国产化交付的刚需。
- 多 provider 不硬绑 DeepSeek(`ctx.llm` 上 deepseek/pi-ai/replay 并列),降低"被单一厂商锁定"的抵触——反而利于成为公共标准。

**反对/存疑(诚实)**:
- 开发者预览,有破坏性变更,尚未稳定——标准需要长期承诺。
- 框架层竞争激烈:Claude Code、Codex、各类开源 agent 框架(含国人发起的)都在抢动手层标准,dsh 能否成事实标准未定。
- "中国标准"需要的不只是技术 + star:还需企业落地案例、行业认可、标准组织背书、长期稳定承诺——这些 dsh 现在都没有。
- 大厂未必甘心让 DeepSeek 定标准:阿里、腾讯、字节、百度各有 agent 框架/产品,标准之争会持续。
- 标准往往是"事实标准"(谁先占住开发者心智 + 企业落地),而非官方钦定。

**结论判断**:短期/中期,dsh 是"最有力的中国开源 agent 事实标准候选";但"是否真成标准"取决于 1-2 年内的企业落地、版本稳定性、生态是否超越 DeepSeek 自家。**现在说"会"为时过早,应说"是当前最强候选,未定"**。

### 7.3 我们可以怎么利用 dsh,能做什么?

> 立场:我们 = 正用公司云模型(wpsyun)+ Pi + ChatDB 做政企 AI 方案的团队。以下按"借鉴 / 接入 / 方案 / 卡位 / 风控"分层,由易到难。

1. **技术借鉴(不等于采用)**:借鉴 dsh 的 seam 化设计,把方案的"模型底座、文档能力(JSAPI)、沙箱、数据源"都做成可换插件,适配政企私有化"换模型/换部署/换沙箱"的交付诉求;借鉴 bundle/patch-layer 分发格式做私有化定制层叠加。这是把它的架构思想拿来提升我们方案的可替换性,不一定用它的代码。
2. **能力接入(短期 PoC)**:用 dsh + `llm-pi-ai` 适配器接公司 wpsyun 模型跑 PoC——因为 dsh 和 Pi 同源 `@earendil-works/pi-ai`,我们用 Pi 调通公司模型的经验(models.json 配置、compat 兼容性调参)可直接复用,验证"公司模型在第三方 agent 框架上可用";内部也可用 dsh 做提效/预研工具。
3. **方案机会(面向客户)**:政企客户若点名要 dsh,我们能基于 seam 化做私有化定制(换模型=wpsyun、换沙箱、换部署);把 dsh 作"平台化开源底座"备选,与 Pi(轻量、已被 Comate 验证)形成"轻 + 重"组合——Pi 做单兵提效 + Comate 级产品,dsh 做可对外交付的平台化方案。
4. **战略卡位**:跟踪 dsh 是否成标准(见 7.2),避免被动;若成势,提前积累 seam 化私有化交付能力 = 我们的差异化。内部培养 Cordis/插件化架构能力作技术储备。
5. **风险控制**:不上生产(开发者预览、有破坏性变更);不硬绑 DeepSeek 模型(接 wpsyun);版本收敛后再评估对外交付。相比之下 Pi 已到 0.84.2、有完整 SDK/RPC/容器化、且已被金山产品化,成熟度更高——短期主力仍走 Pi。

> 一句话:dsh 现阶段对我们是"借鉴其接缝化 + 跑 PoC 验证公司模型 + 作平台化备选观察",不是上生产、不是硬绑 DeepSeek。短期 Pi 路线坚定(已验证、本团队在用),dsh 是中期变量。

---

## 附录:证据出处

- **A. DeepSeek Harness(本地源码)**：`README.zh.md`(定位/预览提示)、`docs/architecture.zh.md:9-13`(一切皆插件)、`:102-107`(seam 三角色)、`:112-131`(加能力=挂插件)、`docs/cordis-primer.zh.md:7-14`(五概念)、`apps/cli/config/agent-presets/standard/agent.cordis.yml`(实测 251 行,三个 isolate 分组)、`packages/extensions/cordis-host-runner/src/{sandbox,guard}.ts`(self-modification)、`packages/llm/llm-pi-ai/`(pi-ai 适配器)。
- **B. Pi(本机已装)**：`@earendil-works/pi-coding-agent`(MIT)；本机 `models.json`(模型配置)；与 dsh 共用 `@earendil-works/pi-ai`。
- **C. WorkBuddy(本机实测)**：`AppData/Local/Programs/WorkBuddy/`(腾讯,Tencent Technology 签名,Electron 5.3.13)；内置 `codebuddy` CLI(tree-sitter/终端/沙箱)；`copilot.tencent.com` 模型后端。
- **D. WPS Comate(本机实测)**：`AppData/Local/WPS Comate/`(金山,Qt5 原生 0.1.0)；内嵌 `@earendil-works/pi-coding-agent` v0.79.3(Bun 运行时)；多 agent + 内置技能 + Git/Node/Python；`comate.wps.cn/llmproxy/v1/user` 模型后端。
- **E. WPS 灵犀(官方/公开)**：`lingxi.wps.cn`；含 Python/Node/AirScript 代码执行 + WPS Office 深度集成。
- **F. 三大 harness 互不内嵌(本机实测)**：WorkBuddy→codebuddy、WPS Comate→Pi、DeepSeek→dsh，三者互不内嵌。
- **G. 公开信息来源**：DeepSeek Harness 仓库 github.com/deepseek-ai/deepseek-harness；产品页 deepseek.com/harness；Pi github.com/earendil-works/pi；WPS 灵犀 lingxi.wps.cn；WorkBuddy 公开报道(腾讯云 CodeBuddy 团队)。
