# Gateway context compression + auto-continue pitfall

## Symptom

A messaging-gateway conversation can appear to "repeat an old request" after a long session, context compression, or an interrupted turn. The user may see the agent answer a task that was completed hours earlier.

## Observed evidence pattern

- Original completed user request exists with an old timestamp, e.g. `2026-04-29T16:38:00`.
- A later compressed/resumed session contains the same old user message as an active transcript row with a new timestamp, e.g. `2026-04-29T21:19:26`.
- The same resumed turn may include a system note like:
  `Your previous turn was interrupted before you could process the last tool result(s)...`
- The gateway log may show `Watch pattern notification — injecting...` around the same time.
- The model then treats the stale user request as current and may rerun tools.

## Likely root cause class

This is not just a model-behavior issue. It is a boundary bug between:

1. context compression preserving early head messages as active transcript rows;
2. timestamp handling during compressed/resumed session creation;
3. gateway auto-continue/tool-tail recovery injecting an interruption note;
4. background process/watch notifications represented as user-like messages.

The dangerous combination is: an already-completed user request is preserved as an active message, gets a fresh timestamp, and is then framed by auto-continue as something whose tool results may still need processing.

## Investigation steps

1. Search session files for the repeated user text:
   ```bash
   grep -R "<old user request>" ~/.hermes/profiles/<profile>/sessions ~/.hermes/sessions 2>/dev/null
   ```
2. Compare timestamps in `.jsonl` transcripts. If the same text appears with both the original time and the later resume/compression time, suspect timestamp refresh during compaction/resume.
3. Inspect gateway logs around the repeated answer:
   ```bash
   tail -120 ~/.hermes/profiles/<profile>/logs/gateway.log
   tail -120 ~/.hermes/profiles/<profile>/logs/errors.log
   ```
4. Check these source areas:
   - `agent/context_compressor.py` — head/tail preservation and summary insertion.
   - `gateway/run.py` — auto-continue/tool-tail/resume_pending system-note injection.
   - process/watch notification plumbing — whether internal notifications are stored as ordinary user turns.

## Fix direction

- For gateway conversations, avoid preserving early ordinary user/assistant turns as active rows after compression; summarize completed head turns instead, while preserving only true system/session metadata and recent tail.
- Preserve original timestamps when copying transcript rows into compressed/resumed sessions; do not stamp old rows with the compression time.
- Gate auto-continue on more than `last role == tool`: validate tool-call pairing, freshness, and whether the user’s new message is clearly a new topic.
- Represent background process/watch notifications as internal/system events, not ordinary user requests.
- Add regression tests that an old completed request in protected head is not re-executed after compression plus a later tool-tail notification.
