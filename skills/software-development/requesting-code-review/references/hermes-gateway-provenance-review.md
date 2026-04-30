# Hermes gateway provenance review lesson

Session: review of Hermes multi-Feishu `session_search` isolation fix.

## What worked

The fix direction was sound: persist provenance (`profile`, `account_id`, `chat_id`, `thread_id`, `route_profile`), make `session_search` default to `current_chat`, expose broader scopes only explicitly, and include provenance in results.

## Review finding to reuse

A subtle blocker can occur when a gateway/session store creates the session row before the main agent does:

1. Gateway writes `sessions(id, source, user_id)` only.
2. Agent later calls `create_session()` with complete provenance for the same `id`.
3. If DB insertion uses `INSERT OR IGNORE`, the complete write is ignored.
4. The row remains without provenance.
5. Strict `current_chat` search then cannot find the session.

Minimal reproduction shape:

```python
db.create_session(session_id="sid", source="feishu", user_id="u")
db.create_session(
    session_id="sid",
    source="feishu",
    user_id="u",
    profile="team-profile",
    account_id="2",
    chat_id="chat",
    route_profile="bot-b",
)
row = db.get_session("sid")
assert row["profile"] is None  # complete metadata was swallowed
```

## What to check in future reviews

- Search for all session creators, not just the modified `SessionDB.create_session()` call site.
- Inspect conflict behavior (`INSERT OR IGNORE`, `ON CONFLICT`, unique IDs).
- Verify gateway/session-store creation includes the same provenance fields as agent creation.
- Ensure later complete writes can backfill NULL metadata without overwriting non-NULL metadata.
- Verify group/channel isolation uses the same dimensions as session-key generation, including `user_id` when per-user group sessions are enabled.
- Decide whether `route_profile` is an isolation dimension or only display metadata; add tests for that choice.

## Recommended tests

- Gateway `SessionStore.get_or_create_session()` persists full provenance.
- Gateway-first, agent-second creation order still ends with full provenance.
- Multi-account Feishu search: account A cannot retrieve account B's session under default scope.
- Same chat, different users in group/channel do not cross when per-user sessions are enabled.
- Same account/chat but different `route_profile` follows the documented isolation behavior.
