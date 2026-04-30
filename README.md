# Hermes Team

这是基于 [NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent) 的个人 fork，重点是把 Hermes 改造成更适合**多机器人长期运行**的版本。

> 原版 Hermes Agent 的完整 README、安装方式和官方文档请看：
> - 官方仓库：[NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent)
> - 官方文档：[hermes-agent.nousresearch.com/docs](https://hermes-agent.nousresearch.com/docs/)

## 和原版 Hermes 主要不一样的地方

### 1. 单个 Feishu gateway 支持多个机器人账号

原版 Hermes 通常是“一个 Feishu/Lark 机器人 = 一个 Hermes profile = 一个 gateway 进程”。这个 fork 增加了单进程多 Feishu account 的实验性支持：

- 一个 Hermes gateway 可以同时连接多个 Feishu/Lark app；
- 每个账号有独立 `account_id`，例如 `1`、`2`、`3`、`4`；
- 日志会标出账号来源，例如 `[Feishu:1] Connected in websocket mode`；
- gateway routing/session key 带账号 namespace，避免不同机器人收发串线；
- 忙碌提示、重启提示等非最终回复也保留账号 metadata，避免多账号 gateway 误用默认账号回消息；
- 启动采用 fail-closed 语义：配置了多个账号时，任一账号没连上，整个 Feishu multi-account 启动会失败，而不是假装部分成功。

### 2. 修复 Python Lark SDK 多 websocket 共享全局状态的问题

Python `lark_oapi.ws.client` SDK 内部存在模块级全局 event loop / websocket connect 状态。多个 Feishu websocket 在同一个进程里运行时，容易互相覆盖，出现“日志显示 connected，但实际只有部分 websocket 在线”的问题。

这个 fork 增加了：

- thread-local Lark loop facade；
- thread-local websocket connect proxy；
- websocket thread 异常传播；
- readiness barrier：等待 SDK 真的建立 `_conn` 后才认为账号 connected；
- 可配置 readiness timeout，例如 `FEISHU_WS_READY_TIMEOUT=60`。

### 3. 多机器人 persona / soul 分层

原版 Hermes 有 `$HERMES_HOME/SOUL.md`，但同一个 gateway 内无法天然区分多个 bot 的身份。这个 fork 支持更清晰的分层：

```text
$HERMES_HOME/SOUL_base.md
  全局 Hermes 基底人格/总体风格；不写具体 bot 身份
  兼容：如果没有 SOUL_base.md，会 fallback 读取旧的 SOUL.md

$HERMES_HOME/souls/<account_id>.md
  当前账号/机器人的私有人设、称呼、口吻、身份

$HERMES_HOME/memories/USER.md
$HERMES_HOME/memories/MEMORY.md
  多机器人共享的用户偏好、项目事实、环境经验、工具经验
```

注入顺序是：

```text
全局 SOUL_base.md（fallback: SOUL.md）
+ 当前 account 的 souls/<account_id>.md
+ shared USER/MEMORY
+ 当前会话上下文
+ shared skills
```

### 4. `memory` tool 支持写当前 bot 的 soul

除了原来的 shared `target="user"` / `target="memory"`，这个 fork 增加了 `target="soul"`：

- bot 身份、人设、说话风格、称呼、关系设定 → 写入当前账号的 `souls/<account_id>.md`；
- 用户偏好、项目事实、工具经验 → 仍写入 shared `USER.md` / `MEMORY.md`；
- 第一版不做 per-account memory，只隔离 persona/soul。

### 5. 会话检索默认按当前聊天隔离

多机器人可以共享长期记忆和 skills，但**会话上下文 / 历史检索默认不共享**。这个 fork 给 SQLite session 记录增加 provenance 字段，并让 `session_search` 默认只查当前聊天：

```text
current_chat = platform/source + profile + account_id + chat_id + thread_id
```

只有在用户明确要求跨范围查看时，工具才会放宽 scope：

- `current_chat`：默认，只看当前平台、当前 profile、当前账号、当前聊天/线程；
- `current_account`：同一账号内跨聊天；
- `current_profile`：同一 profile 内跨账号/机器人；
- `global`：显式全局检索。

跨账号、跨聊天或跨 profile 的结果会带 `provenance`，例如 `source`、`profile`、`account_id`、`chat_id`、`thread_id`、`route_profile`，避免某个机器人把另一个机器人/聊天里的内容说成自己的上下文。旧 session 如果缺少 provenance，不会混进默认 `current_chat` 检索；需要通过 runtime session index backfill 或显式跨范围搜索处理。

### 6. 推荐部署形态

这个 fork 适合把一组相关机器人放进同一个 profile / gateway，例如：

```text
main / 默认个人入口
  HERMES_HOME=$HOME/.hermes
  LaunchAgent=ai.hermes.gateway

TeamA / 多机器人统一 gateway
  HERMES_HOME=$HOME/.hermes/profiles/TeamA
  LaunchAgent=ai.hermes.gateway.TeamA
```

`TeamA` profile 内可以用简单内部编号管理账号，例如：

```text
1 = assistant-a
2 = assistant-b
3 = assistant-c
4 = assistant-d
```

这些编号只用于配置、路由和 `souls/<account_id>.md` 文件命名，不能写进机器人自我认知里。机器人面向用户时只需要知道自己的用户可见身份，例如“我是 assistant-a”，不应说“我是编号 1”或“我是飞书机器人”。

如果后续要把默认入口也迁入统一 gateway，可以重新规划内部编号，例如：

```text
1 = primary-assistant
2 = assistant-a
3 = assistant-b
4 = assistant-c
5 = assistant-d
```

以上只是匿名示例；实际部署时请按自己的机器人名称、profile 名称和路径调整，并避免把真实昵称、私有路径、凭证或运行数据写进公开 README。

## 当前状态

这是个人 fork/实验分支，主要服务于多 Feishu 机器人统一运行、记忆共享、persona 隔离等场景。上游 Hermes 的通用说明请直接参考官方仓库与官方文档。

## License

本 fork 继承上游 Hermes Agent 的 MIT License。原项目版权与许可证声明见 [LICENSE](./LICENSE) 以及 [NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent)。
