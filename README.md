# Hermes Team

Hermes Team 是基于 [NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent) 的 fork，目标是让 Hermes 更适合**一组长期在线的多机器人/多账号助手**：共享长期知识和技能，同时保持每个机器人、账号、聊天的身份与会话边界清晰。

> 原版 Hermes Agent 的安装、完整功能说明和官方文档请看：
> - 官方仓库：[NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent)
> - 官方文档：[hermes-agent.nousresearch.com/docs](https://hermes-agent.nousresearch.com/docs/)

## 与原版 Hermes 的主要区别

### 1. 单 gateway 多 Feishu/Lark 账号

原版 Hermes 通常按“一个机器人账号 = 一个 profile = 一个 gateway 进程”部署。Hermes Team 支持在同一个 gateway 进程里连接多个 Feishu/Lark 机器人账号。

- 每个账号有独立的 `account_id` 和路由上下文。
- 收消息、发消息、编辑消息、进度提示、忙碌提示等都会按来源账号路由。
- 日志会带账号标识，例如 `[Feishu:1] Connected in websocket mode`。
- 多账号启动采用 fail-closed 语义：配置了多个账号时，如果任一账号未能就绪，Feishu multi-account gateway 会整体启动失败，避免“看起来在线但部分账号不可用”。

### 2. 多机器人 persona / soul 分层

Hermes Team 把“共享知识”和“机器人身份”拆开：

```text
$HERMES_HOME/SOUL_base.md
  全局基础风格；不放具体机器人身份

$HERMES_HOME/souls/<account_id>.md
  当前账号/机器人的私有人设、称呼、语气、身份

$HERMES_HOME/memories/USER.md
$HERMES_HOME/memories/MEMORY.md
  多机器人共享的用户偏好、项目事实、环境经验、工具经验
```

最终上下文按以下顺序组合：

```text
全局 SOUL_base.md（fallback: SOUL.md）
+ 当前账号的 souls/<account_id>.md
+ shared USER/MEMORY
+ 当前会话上下文
+ shared skills
```

这意味着：一组机器人可以共享长期记忆和技能，但不会共享彼此的人设和称呼方式。

### 3. `memory` tool 支持写入当前机器人 soul

除原版 shared memory 外，Hermes Team 的 `memory` tool 支持 `target="soul"`：

- 机器人身份、人设、称呼、口吻、关系设定 → 写入当前账号的 `souls/<account_id>.md`；
- 用户偏好、项目事实、工具经验 → 写入 shared `USER.md` / `MEMORY.md`；
- skills 仍作为共享的过程知识使用。

### 4. 会话检索默认按当前聊天隔离

原版 Hermes 的历史会话检索更偏全局。Hermes Team 为 session 记录增加了 provenance，并让 `session_search` 默认只查当前聊天上下文。

默认 `current_chat` 边界包含：

```text
source/platform
profile
account_id
chat_id
thread_id
user_id（已知时）
route_profile（已知时）
```

支持的检索范围：

- `current_chat`：默认，只看当前账号、当前聊天/线程、当前用户边界；
- `current_account`：同一账号内跨聊天；
- `current_profile`：同一 profile 内跨账号/机器人；
- `global`：显式全局检索。

跨账号、跨聊天或跨 profile 的结果会带 `provenance`，例如 `source`、`profile`、`account_id`、`chat_id`、`thread_id`、`route_profile`。缺少 provenance 的旧 session 不会混进默认 `current_chat` 检索。

### 5. 多账号 Feishu websocket 更适合单进程运行

Hermes Team 对 Feishu/Lark websocket 多账号运行做了适配，包括：

- account-aware websocket lifecycle；
- readiness barrier，确认账号真正 connected 后才标记可用；
- websocket thread 异常传播；
- 可配置 readiness timeout，例如 `FEISHU_WS_READY_TIMEOUT=60`。

这些改动让一个 gateway 同时维护多个 Feishu/Lark 机器人连接时更可观测、更不容易出现部分账号静默失败。

## 推荐部署形态

Hermes Team 适合把一组相关机器人放进同一个 profile / gateway，例如：

```text
main / 默认个人入口
  HERMES_HOME=$HOME/.hermes
  LaunchAgent=ai.hermes.gateway

TeamA / 多机器人统一 gateway
  HERMES_HOME=$HOME/.hermes/profiles/TeamA
  LaunchAgent=ai.hermes.gateway.TeamA
```

`TeamA` profile 内可以用内部编号管理账号：

```text
1 = assistant-a
2 = assistant-b
3 = assistant-c
4 = assistant-d
```

这些编号只用于配置、路由和 `souls/<account_id>.md` 文件命名。机器人面向用户时应使用自己的用户可见身份，不应暴露内部账号编号、平台实现或运行路径。

## 当前状态

这是面向多 Feishu/Lark 机器人长期运行的个人 fork。它保留上游 Hermes 的核心能力，并在多账号 gateway、persona 隔离、共享记忆、会话检索隔离等方面做了扩展。

## License

本 fork 继承上游 Hermes Agent 的 MIT License。原项目版权与许可证声明见 [LICENSE](./LICENSE) 以及 [NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent)。
