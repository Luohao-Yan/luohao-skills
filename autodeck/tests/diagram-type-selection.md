# 压力测试:图类型选型(验证 diagram-types.md 知识层有效)

这不是 pytest,是 agent 选型判断的场景描述。验证方法:让一个 fresh-context agent 读
`references/diagram-types.md` 后,对每个场景的「输入内容」输出图类型选择,核对是否选对、
是否避开了「不该选」的项。核心目标:agent 遇到 user flow **不用用户给网站示例**就能选对图。

知识层若有效,场景1(SSO 有分支)应选「决策流程图」而非 `steps3`——这是本次优化的核心验证点。

---

## 场景1:用户流程(应选 决策流程图,NOT steps3)← 核心验证

**输入内容**:
> SSO 登录:login 跳 UIAP 授权 → 回调 state 校验(防 CSRF) + 换 token + 匹配 sys_user
> → 建 sid 会话(Redis 8h) → 前端落 token + getUserMenus 写 menuStore → 按角色落地菜单
> 分支:`?local=1` 走本地账号分支(BCrypt)

**预期判断**:
- 内容形态 = **用户流程/决策流**(有分支 `?local=1` + 多角色 前端/后端/Redis)
- 选中图类型 = **决策流程图**
- **不该选** `steps3`(线性三步画不出分支和泳道)
- 画法 = deckkit recipe:`node(shape="diamond")` state 校验决策 + `shape="roundrect"` 起止 +
  `shape="cylinder"` Redis + `connect_boxes` 主线 + 失败/本地分支去终止节点
- 命中判别决策树第 1 条(有分支)或第 2 条(多角色 + 泳道)

**验证**:agent 输出里出现「决策流程图」且**不出现**「steps3」作为该页方案。

---

## 场景2:纯线性步骤(应选 steps3)

**输入内容**:
> 配置 Key 三步:1. 新建选归属+计费方式 2. 生成 ak/sk/code 3. 返回一次性 code:ak:sk

**预期判断**:
- 无分支、无决策、无多角色 → **`steps3`**(或 `flow_chain` 若 N>3)
- 命中决策树第 5 条(纯线性)

**验证**:agent 选 `steps3`,不强行套决策流程图(无分支的内容用 steps3 是对的)。

---

## 场景3:分层架构(应选 arch_layers,不是流程图)

**输入内容**:
> 后端分层:接入层(Web, App) → 服务层(svcA, svcB, svcC) → 存储层(DB)

**预期判断**:
- 内容形态 = 分层堆叠(层级关系,非流程) → **`arch_layers`**
- 命中决策树第 6 条(分层堆叠)
- **不该选**决策流程图或 steps3(这是层级不是流程,没有分支没有顺序动作)

**验证**:agent 选 `arch_layers`,不误判成流程图。

---

## 场景4:旧 vs 新 流程对比(应选 flow_compare)

**输入内容**:
> 旧流程:人工审核 7 天 → 邮件通知 → Excel 记录
> 新流程:自动审核 2 小时 → 站内通知 → 系统记录

**预期判断**:
- 内容形态 = 前后对比(同一流程改造) → **`dk.flow_compare`**
- 命中决策树第 3 条(前后对比)
- **不该选** `steps3`(steps3 是单条流程,不是新旧对比)

**验证**:agent 选 `flow_compare`,识别出「对比」语义。

---

## 判别口诀自测

agent 读 diagram-types.md 后应能复述:
- 看到 if/else/成功失败/条件分支 → 决策流程图
- 看到「角色A做X,角色B做Y」→ 决策流程图 + 泳道
- 看到纯顺序无分支 → steps3
- 混淆时问:去掉分支还能理解吗?不能 → 必须决策流程图

若 agent 对场景1选了 steps3,说明知识层未生效,需检查 diagram-types.md 的判别决策树是否
够显眼、SKILL.md/deck-from-template.md 的交叉引用是否把 agent 路由到了 diagram-types.md。
