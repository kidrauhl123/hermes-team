# Hermes-native chat client onboarding model

Use this reference when designing first-run/onboarding for a first-party Hermes/Alkaka-native chat client.

## Core product correction

For ordinary users, do **not** present Hermes as the product they must install/configure. Treat Hermes as the hidden local intelligent engine / partner runtime behind the app.

The desired first-run mental model is:

```text
Open app → log in → Alkaka is already in contacts → start chatting
```

Not:

```text
Install Hermes → choose provider → paste API key → configure gateway → create profile
```

## Default first-run flow

```text
User opens Alkaka-qt
  ↓
User logs in to Alkaka account
  ↓
App automatically installs/prepares local intelligent engine
  ↓
App binds a system-provided trial model quota
  ↓
App auto-creates the first partner/contact: Alkaka
  ↓
Alkaka connects to the app's built-in first-party chat channel
  ↓
Contact list already shows Alkaka
  ↓
User clicks Alkaka and starts chatting
```

## Two things the underlying engine needs, hidden from first-run UX

Hermes-like setup mainly needs:

1. **AI model config** — first-run should use an app-provided trial/default model quota. Do not block new users with API key/provider selection. Custom API keys, providers, OAuth, and model switching belong in advanced settings or after trial limits are reached.
2. **Gateway/IM connection** — first-run should default to the app's built-in first-party chat channel. Do not ask users to choose Telegram/Feishu/Slack on first launch.

External IMs are an expansion path for later:

```text
Add new robot / add channel → choose Telegram, Feishu, Slack, Discord, Matrix, etc.
```

## Partner/contact model

The first partner should appear as a normal contact named `Alkaka`. The user should not feel they are creating a profile/persona/config.

Product UI → likely engine mapping:

| User-facing concept | Engine concept |
| --- | --- |
| Contact `Alkaka` | default profile/account/persona |
| Partner personality | soul/persona config |
| Capabilities | skills/toolsets/MCP/permissions |
| Trial model | provider/model config supplied by app account |
| In-app chat | first-party gateway/API channel |

## Product rules

- Hide `Hermes`, `profile`, `SOUL.md`, `gateway`, `toolset`, and API-key jargon from first-run UX.
- Show progress as product actions: `正在准备 Alkaka 智能引擎…`, `正在创建联系人 Alkaka…`, `Alkaka 已准备好，可以开始对话。`
- New users should not need to pick templates before their first chat. Templates such as coding/research/creative assistants can appear in “add partner” later.
- Preserve advanced-user escape hatches: import existing Hermes config, use existing profiles/skills/memory, or create an isolated app-specific engine home.
- Never silently mutate an existing Hermes CLI/gateway environment; imports/reuse must be visible and reversible.

## MVP service boundaries to reserve

- `EngineDetector` — detect local engine availability/version/health.
- `EngineInstaller` — install/upgrade/repair the local engine.
- `TrialModelService` — bind app-provided trial model quota.
- `PartnerProfileService` — create/read/update the default `Alkaka` contact and future partners.
- `InAppGatewayService` — connect first partner to the app's first-party chat channel.
- `ModelSetupService` — advanced provider/API-key/model configuration.
- `SkillLibraryService` — browse/bind default skills.
- `OnboardingState` — first-run state machine.
