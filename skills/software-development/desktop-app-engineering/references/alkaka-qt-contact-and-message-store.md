# Alkaka-qt default contact + SQLite message store checkpoint

Session learning from a verified Qt/QML Hermes-native chat-client iteration.

## Context

Alkaka-qt is a clean Qt 6/QML/C++ desktop client for a Hermes/Alkaka first-party chat experience. Ordinary users should see an in-app AI partner named `Alkaka`, not Hermes profile/gateway internals. The app manages a local Hermes engine and connects to `/v1/runs` + SSE.

## Verified implementation pattern

### Default contact model

Add a dedicated `ContactListModel : QAbstractListModel` instead of keeping static QML side-bar data.

Roles used in the verified checkpoint:

- `name`
- `title`
- `statusText`
- `online`
- `avatarText`
- `accentColor`

Default row:

```text
name: Alkaka
title: 默认 AI 伙伴
statusText: 智能引擎准备中
online: false
avatarText: A
accentColor: #8b5cf6
```

Expose it from `AppController` as a QML property:

```cpp
Q_PROPERTY(ContactListModel* contactListModel READ contactListModel CONSTANT)
```

Bind engine lifecycle signals to contact status:

- `AlkakaEngineManager::engineReady` → `ContactListModel::setEngineReady(true, ...)` → `在线 · 可聊天`, `online=true`.
- `AlkakaEngineManager::engineFailed` → `ContactListModel::setEngineFailed(...)` → `智能引擎异常 · 可重试`, `online=false`.
- Initial state remains `智能引擎准备中`.

QML sidebar should receive `contactModel: appController.contactListModel` and render a `ListView` over model roles. Avoid static arrays such as `["Hermes 项目组", "Skill 库", ...]` once a real contact model exists.

### SQLite message store MVP

Add a focused persistence boundary before wiring it into live models:

```cpp
class MessageStore final {
public:
    explicit MessageStore(QString databasePath);
    bool open();
    bool appendEvent(const HermesEvent &event);
    QVector<HermesEvent> loadConversation(const QString &conversationId, int limit = 200) const;
    QString lastError() const;
};
```

Schema verified in this checkpoint:

```sql
CREATE TABLE IF NOT EXISTS messages (
  id TEXT PRIMARY KEY,
  conversation_id TEXT NOT NULL,
  kind TEXT NOT NULL,
  actor TEXT NOT NULL,
  title TEXT NOT NULL,
  body TEXT NOT NULL,
  payload_json TEXT NOT NULL DEFAULT '{}',
  created_at TEXT NOT NULL,
  collapsed_by_default INTEGER NOT NULL DEFAULT 1
);
CREATE INDEX IF NOT EXISTS idx_messages_conversation_created
  ON messages(conversation_id, created_at);
```

Implementation notes:

- Use a unique Qt SQL connection name per store instance, e.g. `alkaka-message-store-<uuid>`.
- In the destructor, close the database, assign `m_database = QSqlDatabase()`, then call `QSqlDatabase::removeDatabase(connectionName)` to avoid dangling connection warnings.
- Store `HermesEvent::payload` as compact JSON via `QJsonDocument(QJsonObject::fromVariantMap(payload))`.
- Store `createdAt` as `Qt::ISODateWithMs`; load with the same format.
- `INSERT OR REPLACE` is acceptable for the MVP to make event IDs idempotent.

## TDD sequence used

1. Add `test_contact_list_model.cpp` before production model code:
   - default row exists
   - default status is preparing/offline
   - `setEngineReady(true, ...)` marks online and emits `dataChanged`
   - `setEngineFailed(...)` marks offline/error
2. Add `AppController` tests:
   - exposes non-null `contactListModel`
   - engine ready/failed signals update default contact status
3. Add `test_message_store.cpp` before storage implementation:
   - `QTemporaryDir` database path
   - append two events and reopen the DB to prove persistence
   - verify ordering, kind mapping, body, payload JSON
   - verify separate conversations do not leak events
4. Only then add CMake sources and Qt `Sql` link dependency.

### Wiring `MessageStore` into `AppController`

After the storage boundary is green, the next pre-visual-polish task is app-level persistence/restart recovery:

1. Add a failing `ConversationModel` test for an empty persistence mode plus `loadEvents(...)`, so persisted events can be restored without seeding demo messages.
2. Add a failing `AppController` test using `QTemporaryDir` and a testing startup mode that does not start the engine:
   - construct controller with a temp SQLite path
   - clear model-only UI state if needed
   - feed a `HermesEvent` through `handleHermesEventForTesting`
   - destroy controller
   - construct a second controller over the same DB path
   - assert the event is restored and no demo seed leaked into the conversation
3. Add `ConversationModel::SeedPolicy::{DemoEvents, EmptyForPersistence}` and `loadEvents(const QVector<HermesEvent>&)`.
4. Add `AppController(const QString &databasePath, StartupMode, QObject*)`, where `StartupMode::NoEngineForTesting` disables the `QTimer::singleShot(...prepareEngine)` side effect.
5. Default production constructor should use `QStandardPaths::AppDataLocation/messages.sqlite`, create the directory, open `MessageStore`, and load `defaultConversationId()`.
6. Funnel user messages, engine/connection status, and Hermes events through an `appendAndPersistEvent(...)` helper. Generate a UUID before both model append and store append; otherwise empty IDs collide under the SQLite primary key and later status events overwrite earlier rows.
7. Add `MessageStore.cpp/.h` and `Qt6::Sql` to the `alkaka_app_controller_tests` target as well as the app/test storage target.

Verified outputs after this follow-on step:

```text
ctest: 8/8 tests passed
ALKAKA_GUI_E2E_ENGINE_READY=1
ALKAKA_GUI_E2E_FINAL_RESPONSE=OK
ALKAKA_GUI_E2E_MATCHED=1
git diff --check: clean
```

## First lightweight visual pass after persistence

After default contact, persistence, and GUI E2E are green, the first visual pass can safely focus on the narrow-window chat-list feel without detaching from real app state.

Verified pattern:

1. Write a lightweight QML visual-contract test before changing QML. In Alkaka-qt this was `tests/test_qml_visual_contract.py`, registered in CTest as `alkaka_qml_visual_contract_tests`.
2. Lock the product-level visual constraints that matter more than pixel-perfect screenshots at this stage:
   - `minimumWidth: 360` so desktop can shrink phone-like.
   - `compact: width < 640` so narrow mode becomes one-column.
   - white background with purple as an accent, not a heavy purple card shell.
   - a phone-like `ConversationSidebar` with `phoneLike`, large `伙伴` title, search/compose actions, `56` px avatars, `86` px rows, thin `#edf0f5` separators, and purple `#6d4aff` unread badges.
   - compact bottom nav labels such as `伙伴 / 工具 / 文件 / 我`.
3. Run the visual contract once and confirm RED before implementation.
4. Rewrite `Main.qml`/`ConversationSidebar.qml` minimally to satisfy the contract while keeping the existing `appController.contactListModel` and `appController.conversationModel` bindings.
5. Keep wide mode functional: left partner list + middle chat. For the first narrow pass, showing the partner list as the compact surface is acceptable; later work should add list/chat switching.
6. Verify with full structure check, build, all CTest targets, `git diff --check`, and the GUI final-response smoke.

Verified outputs after the first visual pass:

```text
Alkaka-qt structure verification passed.
ctest: 9/9 tests passed
ALKAKA_GUI_E2E_ENGINE_READY=1
ALKAKA_GUI_E2E_FINAL_RESPONSE=OK
ALKAKA_GUI_E2E_MATCHED=1
git diff --check: clean
```

Pitfall: do not make the visual contract assert every QML line. It should freeze product-critical responsive/visual promises, not prevent normal QML refactors.

## SQLite schema v2 expansion after first UI pass

When the user asks to make the local database more comprehensive before deeper UI work, extend the storage boundary with TDD rather than jumping straight to QML.

Verified Alkaka-qt pattern:

1. Add failing tests in `tests/test_message_store.cpp` for durable tables and old-database migration:
   - `schema_metadata`
   - `conversations`
   - `partners`
   - `tool_calls`
   - `file_changes`
   - `run_errors`
   - preserving legacy `messages` rows when opening an older database.
2. Add behavior tests for store APIs, not just table existence:
   - `upsertPartner/loadPartners`
   - `upsertConversation/loadConversations`
   - `upsertToolCall/loadToolCalls`
   - `upsertFileChange/loadFileChanges`
   - `upsertRunError/loadRunErrors`
3. Add an `AppController` test that opens a temp DB, emits engine ready, injects a final response, then reopens `MessageStore` and verifies:
   - default `alkaka` partner is persisted and marked `online`.
   - default conversation row exists.
   - `last_message_preview` reflects the final answer.
4. Implement nested record structs in `MessageStore` and keep MVP API simple: typed `upsert*` plus typed `load*` methods.
5. Keep legacy message persistence intact: use `CREATE TABLE IF NOT EXISTS` and write `schema_metadata(schema_version=2)` after creating new tables.
6. Project app-level state conservatively in `AppController`: persist default partner on startup/engine ready/engine failed; update `conversations.last_message_preview` whenever an event is appended.
7. Document the schema in `docs/data-model.md` and add structure assertions for all critical tables.
8. Verify full structure check, `git diff --check`, CMake build, all CTest targets, and GUI final-response smoke.

Verified outputs after schema v2:

```text
Alkaka-qt structure verification passed.
Checked 39 required files and 23 content assertions.
ctest: 9/9 tests passed
ALKAKA_GUI_E2E_ENGINE_READY=1
ALKAKA_GUI_E2E_FINAL_RESPONSE=OK
ALKAKA_GUI_E2E_MATCHED=1
```

Pitfalls:

- Do not report a higher CTest target count if schema tests were added to an existing target; in this checkpoint it remained 9/9 while `alkaka_message_store_tests` and `alkaka_app_controller_tests` gained more cases.
- `qmldir file not found at .../build/AlkakaQt/QML` can still appear during configure but was non-blocking in this checkpoint.

## SQLite-driven contact/conversation list projection

After schema v2 exists, wire the sidebar/list model to the database projection before deeper visual work. Keep this TDD-driven because regressions are subtle: the UI can look fine with the default row while restored state is wrong.

Verified Alkaka-qt pattern:

1. Extend `ContactListModel` roles for Telegram-like list metadata:
   - `conversationId`
   - `unreadCount`
   - `pinned`
   - `timestampText`
2. Add failing tests in `tests/test_contact_list_model.cpp` for:
   - loading a row from `MessageStore::PartnerRecord` + `ConversationRecord`.
   - keeping the partner visible when the engine is ready but no conversation exists yet; otherwise `persistDefaultPartner("online")` can reload the model back to the offline default row.
   - Telegram-like ordering: skip archived conversations, show pinned rows first, then sort non-pinned by `lastEventAt` descending.
3. Add an `AppController` test that pre-populates a temp SQLite DB with `partners` + `conversations`, constructs `AppController(..., NoEngineForTesting)`, and asserts the contact list restores `lastMessagePreview`, unread count, pinned state, and online status.
4. In `AppController`, only create the default `alkaka` partner if `loadPartners()` is empty. Then call a single `reloadContactListFromStore()` helper after startup, partner status updates, and conversation projection updates.
5. In QML, use the model-provided `timestampText` instead of hard-coded demo times.
6. Add structure assertions for `ContactListModel::loadFromStoreRecords`, list sorting, and QML `timestampText` binding.
7. Keep the CTest target count accurate: these are extra cases inside existing targets, so the verified count can remain `9/9 tests passed`.

Verified outputs after SQLite-driven list projection:

```text
Alkaka-qt structure verification passed.
Checked 39 required files and 26 content assertions.
ctest: 9/9 tests passed
ALKAKA_GUI_E2E_ENGINE_READY=1
ALKAKA_GUI_E2E_FINAL_RESPONSE=OK
ALKAKA_GUI_E2E_MATCHED=1
```

Pitfall: if `loadFromStoreRecords(partners, {})` falls back to `makeDefaultContact()` unconditionally, the UI will incorrectly show `智能引擎准备中` after the engine-ready partner row has already been persisted.

## Projecting Hermes process artifacts into SQLite

After `tool_calls`, `file_changes`, and `run_errors` exist, do not leave them as unused schema. Wire `AppController` to project structured Hermes events into these tables so later process-rail UI can restore state without parsing chat text.

Verified Alkaka-qt pattern:

1. Add a failing `AppController` test first. Use a temp SQLite DB, feed `HermesEvent` values through `handleHermesEventForTesting`, destroy the controller, reopen `MessageStore`, and assert:
   - `ToolStart` + `ToolComplete` with the same id upsert one `tool_calls` row whose status becomes `completed`.
   - `FileChange` writes path/change type/status/summary into `file_changes`.
   - `StatusUpdate` with payload `api_event=run.failed` writes a retryable/non-retryable `run_errors` row.
2. Add `persistArtifactProjection(const HermesEvent&)` next to `persistConversationProjection(...)`; call it immediately after `appendEvent(...)` and conversation projection.
3. Read robust payload key variants because Hermes events may evolve:
   - run id: `run_id` or `runId`.
   - tool id: `tool_call_id`, `toolCallId`, payload `id`, or fallback event id.
   - tool name: `name`, `tool`, `tool_name`, `toolName`, or fallback event title.
   - file path: `path`, `file`, `file_path`, `filePath`, or fallback event title.
   - file change type: `change_type`, `changeType`, `type`, `operation`; default `modified`.
   - error type: `error_type`, `errorType`, `type`, `code`; default `run_failed`.
4. Store original event payload compactly in `inputJson` for running tool calls and `outputJson` for completed tool calls. This keeps raw details available even before a polished UI exists.
5. Add structure assertions for `persistArtifactProjection`, `upsertToolCall`, `upsertFileChange`, and `upsertRunError`.
6. Verify full structure check, `git diff --check`, build, all CTest targets, and GUI E2E final-response smoke.

Verified outputs after artifact projection:

```text
Alkaka-qt structure verification passed.
Checked 39 required files and 30 content assertions.
ctest: 9/9 tests passed
ALKAKA_GUI_E2E_ENGINE_READY=1
ALKAKA_GUI_E2E_FINAL_RESPONSE=OK
ALKAKA_GUI_E2E_MATCHED=1
```

Pitfall: `run.failed` currently maps to `StatusUpdate`, so projection must key off `payload["api_event"] == "run.failed"` (or title `任务失败`), not only a dedicated enum.

## Wiring artifact tables into process-rail UI

After `tool_calls`, `file_changes`, and `run_errors` are populated, add a thin model boundary before polishing the QML. Verified Alkaka-qt pattern:

1. Add `tests/test_artifact_model.cpp` first. Feed `MessageStore::ToolCallRecord`, `FileChangeRecord`, and `RunErrorRecord` directly and assert UI roles such as kind/title/summary/status/accent/retryable. Also assert newest artifacts sort first.
2. Add a QML visual-contract assertion that `Main.qml` passes `artifactModel: appController.artifactModel` and `ProcessRail.qml` declares `required property var artifactModel`; this catches regressions back to ad-hoc per-message process rows.
3. Add an `AppController` restoration test that pre-populates artifact tables, constructs `AppController(..., NoEngineForTesting)`, and asserts `controller.artifactModel()` is populated from SQLite.
4. Implement `ArtifactModel : QAbstractListModel` as a read model over the existing store record structs. Keep role names QML-friendly, e.g. `artifactKind`, `artifactTitle`, `artifactSummary`, `artifactStatusText`, `artifactTimestampText`, `artifactAccentColor`, `retryable`.
5. Expose it via `Q_PROPERTY(ArtifactModel* artifactModel READ artifactModel CONSTANT)` and reload it on startup plus after each `persistArtifactProjection(...)` write.
6. Convert `ProcessRail.qml` into a model-driven weak card list for tool/file/error summaries. Detailed expansion, diff viewers, and retry actions can come later.
7. Update structure assertions, docs, full tests, and GUI E2E. This checkpoint increased CTest target count from 9 to 10.

Verified outputs after process-rail artifact UI:

```text
Alkaka-qt structure verification passed.
Checked 42 required files and 37 content assertions.
ctest: 10/10 tests passed
ALKAKA_GUI_E2E_ENGINE_READY=1
ALKAKA_GUI_E2E_FINAL_RESPONSE=OK
ALKAKA_GUI_E2E_MATCHED=1
```

Pitfall: when adding restoration tests, populate required NOT NULL fields such as `tool_calls.run_id`; otherwise the test fails in setup rather than proving AppController wiring.

## Verification commands from the checkpoint

```bash
PATH="$HOME/Library/Python/3.9/bin:$PATH" \
cmake -S . -B build -DCMAKE_BUILD_TYPE=Debug \
  -DCMAKE_PREFIX_PATH="$HOME/Qt/6.7.3/macos"

PATH="$HOME/Library/Python/3.9/bin:$PATH" cmake --build build --parallel 2
PATH="$HOME/Library/Python/3.9/bin:$PATH" ctest --test-dir build --output-on-failure

git diff --check

ALKAKA_GUI_E2E_SMOKE_PROMPT='只回复两个字：OK' \
ALKAKA_GUI_E2E_SMOKE_EXPECT='OK' \
PATH="$HOME/Library/Python/3.9/bin:$PATH" \
./build/alkaka-qt
```

Verified outputs:

```text
ctest: 8/8 tests passed
ALKAKA_GUI_E2E_ENGINE_READY=1
ALKAKA_GUI_E2E_CONNECTION_STATUS=已连接 Alkaka 智能引擎。
ALKAKA_GUI_E2E_CONNECTION_STATUS=Alkaka 已开始执行。
ALKAKA_GUI_E2E_FINAL_RESPONSE=OK
ALKAKA_GUI_E2E_MATCHED=1
git diff --check: clean
```

## Pitfalls

- Do not leave the sidebar as static QML demo data after implementing first-run/default-contact behavior; it hides whether engine state is reaching UI.
- `/health` OK does not mean chat is usable; keep GUI E2E final-response smoke in the verification loop.
- Remember to add `Qt6::Sql` to both top-level app linking and test target linking when adding SQLite.
- `git diff --stat` may not show newly created files if they were not staged; check `git status --short` before committing.
- A local commit is not a push: if `git remote -v` is empty, report that the repo has no remote instead of claiming publication.
