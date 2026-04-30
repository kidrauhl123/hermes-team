# Hermes-native chat client base selection notes

Use when planning a dedicated desktop chat client for Hermes / multi-agent gateways, especially when the user is worried that a from-scratch Qt app will underdeliver compared with Telegram-like mature clients.

## Key framing correction

Do **not** frame the product as "turning a terminal into a chat app." Hermes already supports IM/gateway platforms such as Telegram, Feishu/Lark, Discord, Slack, Matrix, etc. The product goal is a **Hermes-native first-party client** that reuses/extends Hermes' existing gateway/session/profile/skill/tool concepts and improves what generic IMs do poorly:

- collapsible process timelines
- full tool/path/command/output inspection
- Skill library UI
- task state and approvals
- multi-agent/persona collaboration
- delivery failure recovery
- local event/session persistence

## User trust issue: avoid blind from-scratch implementation

If the user says they do not trust starting from zero, do not argue for a blank app. Convert the decision into a base feasibility evaluation:

```text
Route A: fork/adapt Telegram Desktop
Route B: adapt a smaller Qt chat client such as Nheko / NeoChat
Route C: clean Alkaka/Hermes-native app built after module-level study
```

The outcome should be evidence-based: clone, build/inspect, locate protocol/UI boundaries, identify reusable patterns, estimate replacement cost, then decide.

## Telegram Desktop as a base

Facts checked in-session:

- Telegram Desktop README states it is the official Telegram desktop client based on Telegram API and MTProto.
- License is GPLv3 with OpenSSL exception.

Implications:

- Directly copying/forking Telegram Desktop is possible only if GPLv3 obligations are acceptable.
- Keep upstream copyright/license/attribution; heavy modification does **not** remove license obligations.
- It may still be a poor engineering base if Telegram account/API/MTProto/media/sync assumptions are deeply coupled to UI and storage.

Evaluate before choosing it:

1. Can the Telegram account/protocol layer be bypassed or replaced cleanly?
2. Can the chat list/message rendering/input/scrolling subsystems be retained independently?
3. Can Hermes Gateway/API structured events map into the data model without fighting Telegram assumptions?
4. Is GPLv3 acceptable for the user's intended distribution/commercial/private-code goals?
5. Can the local environment build it reliably enough for iterative AI-assisted modification?

## Nheko / NeoChat as bases

These may be easier Qt-oriented bases because their Matrix room/event model is conceptually closer to projects, conversations, and events than Telegram's MTProto-specific model. They may not match Telegram's polish, so evaluate both experience quality and modification surface.

## Recommended decision workflow

1. Keep the main Alkaka-qt repo free of copied GPL code until the license decision is explicit.
2. Clone candidate repos into an external `references/` or sibling research directory, not into the product source tree.
3. For each candidate, capture:
   - license and attribution obligations
   - build feasibility on the user's machine
   - UI modules: chat list, message view, composer, media/file cards, responsive layout
   - backend/protocol coupling points
   - what can be reused, what can only be studied, what blocks adoption
4. Produce a short decision table before creating the actual app skeleton.
5. If forking a GPL base is chosen, make the repo license/attribution explicit from the first commit.

## Product architecture reminder

Telegram teaches "how a desktop chat client feels." Hermes decides "what the client can do." Alkaka-qt should combine mature chat UX with Hermes-native structured events, Skill library, tools, files, tasks, approvals, profiles/personas, and multi-agent collaboration.
