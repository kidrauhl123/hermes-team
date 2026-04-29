# Hermes Team

这是基于 [NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent) 的个人 fork，重点是把 Hermes 改造成更适合多机器人长期运行的版本。

> 原版 Hermes Agent 的完整 README、安装方式和官方文档请看：
> - 官方仓库：[NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent)
> - 官方文档：[hermes-agent.nousresearch.com/docs](https://hermes-agent.nousresearch.com/docs/)

## 和原版 Hermes 主要不一样的地方

### 1. 单个 Feishu gateway 支持多个飞书机器人账号

原版 Hermes 通常是“一个 Feishu/Lark 机器人 = 一个 Hermes profile = 一个 gateway 进程”。这个 fork 增加了单进程多 Feishu account 的实验性支持：

- 一个 Hermes gateway 可以同时连接多个 Feishu/Lark app；
- 每个账号有独立 `account_id`，例如 `1`、`2`、`3`、`4`；
- 日志会标出账号来源，例如 `[Feishu:1] Connected in websocket mode`；
- gateway routing/session key 带账号 namespace，避免不同机器人收发串线；
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

### 5. 当前本机验证过的运行形态

本机目前采用两个常驻 gateway：

```text
default / 九妹
  HERMES_HOME=/Users/zuiyou/.hermes
  LaunchAgent=ai.hermes.gateway

feishu / 多飞书机器人统一 gateway
  HERMES_HOME=/Users/zuiyou/.hermes/profiles/feishu
  LaunchAgent=ai.hermes.gateway.feishu
```

`feishu` profile 内当前内部账号编号：

```text
1 = 二妹
2 = 三妹
3 = 丞相
4 = 赵高
```

这些编号只用于配置、路由和 `souls/<account_id>.md` 文件命名，不能写进机器人自我认知里。机器人面向用户时只需要知道自己是谁，例如“我是二妹”，不应说“我是编号 1”或“我是飞书机器人”。

后续如果迁移九妹进统一 Feishu gateway，推荐内部编号调整为：

```text
1 = 九妹
2 = 二妹
3 = 三妹
4 = 丞相
5 = 赵高
```

## 当前状态

这是个人 fork/实验分支，主要服务于多 Feishu 机器人统一运行、记忆共享、persona 隔离等场景。上游 Hermes 的通用说明请直接参考官方仓库与官方文档。

## License

本 fork 继承上游 Hermes Agent 的 MIT License。原项目版权与许可证声明见 [LICENSE](./LICENSE) 以及 [NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent)。
