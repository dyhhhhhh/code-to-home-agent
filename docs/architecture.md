# Architecture

本文描述一个从 code agent 改写而来的 home agent 架构。

## 设计目标

home agent 应当具备这些能力：

- 读取家庭状态，而不是凭空猜测。
- 理解用户自然语言意图。
- 把家庭目标拆解为可执行动作。
- 根据设备风险等级执行权限判断。
- 调用设备中枢或家电代理模块。
- 读取设备回执和传感器结果。
- 在失败时停止、重试、回退或请求人工确认。
- 对用户解释自己做了什么、为什么做、为什么拒绝。

## Code Agent 循环

code agent 的核心循环：

```text
observe repository
→ understand task
→ plan edits
→ call tools
→ mutate files
→ run verification
→ repair if needed
→ report result
```

其中最关键的不是“写代码”，而是闭环：

```text
观察 → 行动 → 验证 → 修正
```

## Home Agent 循环

home agent 的对应循环：

```text
observe home state
→ understand intent
→ plan environment changes
→ check policy and risk
→ call device tools
→ mutate home state
→ verify through sensors
→ repair or ask human
→ log and explain
```

映射关系：

| Code Agent | Home Agent |
|---|---|
| repo files | home state graph |
| shell tools | device tools |
| tests | sensor verification |
| git diff | action log |
| CI failure | device failure or unsafe precondition |
| commit | accepted household state change |

## 分层架构

```text
┌──────────────────────────────────────────────┐
│ User Interfaces                               │
│ voice, mobile app, wall panel, chat, buttons  │
└───────────────────────┬──────────────────────┘
                        ↓
┌──────────────────────────────────────────────┐
│ Local Agent Runtime                           │
│ ASR, LLM, memory, planner, tool router        │
└───────────────────────┬──────────────────────┘
                        ↓
┌──────────────────────────────────────────────┐
│ Policy Layer                                  │
│ permissions, risk levels, quiet hours, roles  │
└───────────────────────┬──────────────────────┘
                        ↓
┌──────────────────────────────────────────────┐
│ Orchestration Layer                           │
│ Home Assistant, Matter Hub, rule engine       │
└───────────────────────┬──────────────────────┘
                        ↓
┌──────────────────────────────────────────────┐
│ Appliance Adapter Layer                       │
│ device proxies, MCU modules, bridges          │
└───────────────────────┬──────────────────────┘
                        ↓
┌──────────────────────────────────────────────┐
│ Physical Home                                 │
│ appliances, sensors, rooms, people, energy    │
└──────────────────────────────────────────────┘
```

## 家庭状态图

home agent 不应只保存聊天上下文，而应维护一个家庭状态图：

```text
Home
├── Members
│   ├── adult_owner
│   ├── child
│   └── elder
├── Rooms
│   ├── living_room
│   ├── kitchen
│   └── bedroom
├── Devices
│   ├── light.living_room
│   ├── climate.bedroom
│   ├── lock.front_door
│   └── sensor.kitchen_gas
├── Policies
│   ├── quiet_hours
│   ├── child_permissions
│   └── high_risk_confirmation
└── Events
    ├── motion_detected
    ├── water_leak
    └── door_unlocked
```

## 风险等级

每个工具和设备动作都应被标注风险等级：

| 风险 | 示例 | 默认策略 |
|---|---|---|
| Low | 开灯、调亮度、播放本地音乐 | 可自动执行 |
| Medium | 启动扫地机、调空调、启动洗衣机 | 按规则执行，必要时确认 |
| High | 门锁、摄像头访问、热水器、大功率设备 | 默认需要确认 |
| Critical | 燃气、配电、报警系统、医疗设备 | 默认禁止自动执行 |

## 工具调用约束

LLM 不应看到无约束的硬件接口，而应看到结构化工具：

```json
{
  "tool": "set_climate",
  "args": {
    "entity_id": "climate.bedroom",
    "target_temperature": 24,
    "mode": "cool"
  },
  "risk": "medium",
  "requires_confirmation": false
}
```

执行前由 policy layer 再次检查：

```text
用户是谁？
用户是否有权限？
设备是否在线？
当前时间是否允许？
是否有人在房间？
是否违反节能/安静/安全规则？
是否需要人工确认？
```

## 验证机制

家庭动作需要验证，而不是只发命令。

示例：关闭客厅灯。

```text
1. 发送关闭命令。
2. 等待设备回执。
3. 读取 light.living_room 状态。
4. 读取照度传感器。
5. 若状态不一致，重试或提醒用户。
```

示例：启动洗衣机。

```text
1. 检查门锁状态。
2. 检查水浸传感器。
3. 检查当前是否为安静时段。
4. 若风险策略要求，向手机或中控屏请求确认。
5. 启动设备。
6. 读取功耗和运行状态。
7. 记录日志。
```

## 记忆系统

home agent 的记忆应分为三类：

```text
短期上下文：当前对话和任务。
结构化偏好：温度、灯光、作息、房间规则。
审计日志：所有重要动作和拒绝原因。
```

不要把家庭隐私随意上传到云端。默认设计应是本地优先，云端只作为用户授权后的增强能力。

## 最小实现路线

1. 使用 Home Assistant 作为设备抽象层。
2. 接入低风险设备和基础传感器。
3. 定义设备能力 schema。
4. 定义工具风险等级。
5. 使用本地 LLM 做意图理解和工具参数生成。
6. 所有工具调用先经过 policy layer。
7. 每次执行后读取状态并写入日志。
8. 高风险动作默认只提醒或要求确认。

