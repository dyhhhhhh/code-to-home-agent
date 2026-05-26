# Project Goals

本项目的目标是把 code agent 的工程范式迁移到家庭环境，形成一套可讨论、可实现、可审计的 home agent 架构草案。

它不把重点放在“让大模型说一句话控制某个设备”上，而是关注更基础的问题：

```text
家庭如何被 agent 观察？
家庭动作如何被 agent 安全请求？
家电如何声明自己的能力、状态和风险？
执行结果如何被传感器验证？
高风险动作如何被权限系统和本地规则阻止？
用户如何随时理解、撤销和接管？
```

## Goals

### 1. Map the code-agent loop to the home-agent loop

code agent 的核心循环是：

```text
observe → plan → act → verify → repair → report
```

home agent 的对应循环应是：

```text
observe home state
→ plan household actions
→ request device operations
→ check policy and risk
→ execute through safe adapters
→ verify with sensors
→ explain or recover
```

本项目希望把这个映射讲清楚，并形成可以被实现的接口和流程。

### 2. Define a device capability contract

传统家电不能只暴露“开”和“关”。一个适合 home agent 的设备节点应声明：

- 设备身份。
- 所在位置。
- 可执行能力。
- 当前状态。
- 风险等级。
- 前置条件。
- 是否需要人工确认。
- 是否支持状态回读。
- 是否支持手动接管。

这个 contract 是 LLM 和真实硬件之间的边界。

### 3. Put a safety proxy between LLMs and appliances

本项目的原则是：

```text
LLM can request.
Policy decides.
Hardware adapter executes.
Sensors verify.
Humans can override.
```

AI 不应直接驱动市电负载、燃气阀、门锁或其他高风险设备。它只能通过受限工具和安全代理层提出请求。

### 4. Treat home automation as a verified state transition

家庭动作不应止步于“命令已发送”。home agent 应尝试确认：

- 设备是否收到命令。
- 状态是否发生变化。
- 传感器是否验证结果。
- 失败时是否重试、停止或提醒。
- 重要动作是否写入日志。

这对应 code agent 中的测试、lint、编译和 diff。

### 5. Make local-first home intelligence possible

家庭数据高度敏感。摄像头、门锁、作息、儿童和老人照护数据不应默认上传云端。

本项目优先考虑：

- 本地模型。
- 本地设备中枢。
- 本地审计日志。
- 本地权限判断。
- 用户授权后的云端增强。

### 6. Provide a hardware adaptation path

现有家庭不会一夜之间变成原生 AI 家庭。因此本项目提出从 Level 0 到 Level 5 的接入模型：

```text
Level 0: observe only
Level 1: non-invasive control
Level 2: power-level control
Level 3: low-voltage interface integration
Level 4: controller replacement
Level 5: AI-native appliances
```

这个模型帮助区分哪些设备适合自动化，哪些设备只能监测，哪些设备必须保持人工确认。

## Non-Goals

### 1. Not a ready-to-run smart home product

本项目当前不是可以直接安装并接管家庭设备的产品。

### 2. Not a hardware hacking tutorial

本项目不会提供危险的市电、燃气、门锁、配电箱或医疗设备改造教程。

### 3. Not an LLM-only architecture

本项目不主张让大模型直接控制一切。home agent 必须由模型、规则、权限、设备中枢、硬件代理、传感器和人工接管共同构成。

### 4. Not cloud-first by default

云端模型可以作为增强能力，但不应成为家庭敏感数据和关键控制的默认唯一依赖。

## Success Criteria

一个成熟的 home agent 架构至少应满足：

- 可观察：家庭状态能被结构化读取。
- 可授权：不同成员、设备、房间和风险等级有不同权限。
- 可执行：设备动作通过明确工具和代理层完成。
- 可验证：执行结果能通过设备状态和传感器确认。
- 可解释：用户能知道 agent 做了什么、为什么做、为什么拒绝。
- 可审计：关键动作和失败原因被记录。
- 可接管：用户和本地安全系统能随时覆盖 AI 决策。

## Positioning

本项目的定位是一份 home agent 架构与硬件接入提案。

它的核心不是“让 AI 控制灯光”，而是建立一套更完整的家庭智能体框架：

```text
Code-agent loop
+ local LLM
+ device capability contract
+ safety proxy
+ risk policy
+ sensor verification
+ human override
= home-agent architecture
```

