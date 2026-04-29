"""Regression tests for multi-Feishu busy/drain acknowledgements."""

from unittest.mock import MagicMock, patch

import pytest

from gateway.config import Platform
from gateway.platforms.base import MessageEvent, MessageType, merge_pending_message_event
from gateway.run import GatewayRunner
from gateway.session import SessionSource, build_session_key


class MetadataCapturingAdapter:
    """Adapter stub that records send metadata for multi-account routing tests."""

    def __init__(self):
        self._pending_messages = {}
        self.sent = []

    @staticmethod
    def _metadata_for_source(source):
        metadata = {}
        if getattr(source, "thread_id", None):
            metadata["thread_id"] = source.thread_id
        if getattr(source, "account_id", None):
            metadata["account_id"] = source.account_id
        return metadata or None

    async def _send_with_retry(self, chat_id, content, reply_to=None, metadata=None):
        self.sent.append({
            "chat_id": chat_id,
            "content": content,
            "reply_to": reply_to,
            "metadata": metadata,
        })
        return MagicMock(success=True)


def make_feishu_account_event(text="hello", chat_id="oc_3", account_id="3"):
    source = SessionSource(
        platform=Platform.FEISHU,
        chat_id=chat_id,
        chat_type="dm",
        user_id="u1",
        account_id=account_id,
    )
    return MessageEvent(text=text, message_type=MessageType.TEXT, source=source)


def make_busy_runner(adapter):
    runner = object.__new__(GatewayRunner)
    runner.adapters = {Platform.FEISHU: adapter}
    runner._draining = False
    runner._busy_input_mode = "queue"
    runner._busy_ack_ts = {}
    runner._running_agents = {}
    runner._running_agents_ts = {}

    def queue_or_replace(session_key, event):
        merge_pending_message_event(adapter._pending_messages, session_key, event)

    runner._queue_or_replace_pending_event = queue_or_replace
    runner._queue_during_drain_enabled = lambda: True
    return runner


@pytest.mark.asyncio
async def test_busy_ack_preserves_feishu_account_metadata():
    """Busy acknowledgements must route through the inbound Feishu account.

    Multi-Feishu sends use metadata['account_id'] to choose the child adapter.
    Dropping account_id makes the composite adapter fall back to the default
    account, which cannot send into another account's DM and yields Feishu
    [230002] "Bot/User can NOT be out of the chat".
    """
    adapter = MetadataCapturingAdapter()
    runner = make_busy_runner(adapter)
    event = make_feishu_account_event(account_id="3")
    session_key = build_session_key(event.source)
    running_agent = MagicMock()
    running_agent.get_activity_summary.return_value = {}
    runner._running_agents[session_key] = running_agent

    with patch("agent.onboarding.is_seen", return_value=True):
        handled = await runner._handle_active_session_busy_message(event, session_key)

    assert handled is True
    assert adapter.sent[-1]["metadata"] == {"account_id": "3"}


@pytest.mark.asyncio
async def test_draining_ack_preserves_feishu_account_metadata():
    """Drain/restart acknowledgements also need account_id for delivery."""
    adapter = MetadataCapturingAdapter()
    runner = make_busy_runner(adapter)
    runner._draining = True
    runner._status_action_gerund = lambda: "restarting"
    event = make_feishu_account_event(account_id="3")
    session_key = build_session_key(event.source)

    handled = await runner._handle_active_session_busy_message(event, session_key)

    assert handled is True
    assert adapter.sent[-1]["metadata"] == {"account_id": "3"}
