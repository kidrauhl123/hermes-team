import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from gateway.config import Platform, PlatformConfig, GatewayConfig
from gateway.platforms.base import BasePlatformAdapter
from gateway.platforms.feishu import (
    FeishuAdapter,
    MultiFeishuAdapter,
    _ThreadLocalWebsocketsConnectProxy,
    _ensure_lark_ws_threadlocal_runtime,
)
from gateway.run import GatewayRunner
from gateway.session import SessionSource, build_session_key


def test_session_source_serializes_account_route_fields():
    source = SessionSource(
        platform=Platform.FEISHU,
        chat_id="oc_chat",
        chat_type="dm",
        user_id="ou_user",
        account_id="bot2",
        route_profile="feishu-bot-2",
    )

    data = source.to_dict()
    restored = SessionSource.from_dict(data)

    assert data["account_id"] == "bot2"
    assert data["route_profile"] == "feishu-bot-2"
    assert restored.account_id == "bot2"
    assert restored.route_profile == "feishu-bot-2"


def test_session_key_includes_feishu_account_id_to_avoid_cross_bot_collisions():
    base = dict(platform=Platform.FEISHU, chat_id="oc_same_chat", chat_type="dm")

    key_a = build_session_key(SessionSource(**base, account_id="default"))
    key_b = build_session_key(SessionSource(**base, account_id="bot2"))
    legacy = build_session_key(SessionSource(**base))

    assert key_a == "agent:main:feishu:acct:default:dm:oc_same_chat"
    assert key_b == "agent:main:feishu:acct:bot2:dm:oc_same_chat"
    assert legacy == "agent:main:feishu:dm:oc_same_chat"
    assert len({key_a, key_b, legacy}) == 3


def test_base_build_source_can_tag_account_and_route_profile():
    class StubAdapter(BasePlatformAdapter):
        async def connect(self):
            return True

        async def disconnect(self):
            return None

        async def send(self, chat_id, content, reply_to=None, metadata=None):
            return None

        async def get_chat_info(self, chat_id):
            return {}

    adapter = StubAdapter(PlatformConfig(enabled=True), Platform.FEISHU)
    source = adapter.build_source(
        chat_id="oc_chat",
        account_id="bot3",
        route_profile="feishu-bot-3",
    )

    assert source.account_id == "bot3"
    assert source.route_profile == "feishu-bot-3"


def test_multi_feishu_adapter_builds_one_child_per_account_and_preserves_bindings():
    config = PlatformConfig(
        enabled=True,
        extra={
            "domain": "feishu",
            "accounts": {
                "default": {
                    "app_id": "cli_default",
                    "app_secret": "secret_default",
                    "route_profile": "default",
                },
                "bot2": {
                    "app_id": "cli_bot2",
                    "app_secret": "secret_bot2",
                    "route_profile": "feishu-bot-2",
                },
            },
        },
    )

    adapter = MultiFeishuAdapter(config)

    assert set(adapter.children) == {"default", "bot2"}
    assert adapter.children["default"].account_id == "default"
    assert adapter.children["default"].route_profile == "default"
    assert adapter.children["bot2"].account_id == "bot2"
    assert adapter.children["bot2"].route_profile == "feishu-bot-2"
    assert adapter.children["bot2"]._app_id == "cli_bot2"


def test_gateway_runner_create_adapter_uses_multi_feishu_when_accounts_configured():
    runner = GatewayRunner.__new__(GatewayRunner)
    runner.config = GatewayConfig()
    runner.config.platforms = {}
    runner.config.group_sessions_per_user = True
    runner.config.thread_sessions_per_user = False

    config = PlatformConfig(
        enabled=True,
        extra={
            "accounts": {
                "a": {"app_id": "cli_a", "app_secret": "secret_a"},
                "b": {"app_id": "cli_b", "app_secret": "secret_b"},
            }
        },
    )

    adapter = runner._create_adapter(Platform.FEISHU, config)

    assert isinstance(adapter, MultiFeishuAdapter)
    assert set(adapter.children) == {"a", "b"}


@pytest.mark.asyncio
async def test_multi_feishu_send_routes_by_account_metadata():
    config = PlatformConfig(
        enabled=True,
        extra={
            "accounts": {
                "default": {"app_id": "cli_default", "app_secret": "secret_default"},
                "bot2": {"app_id": "cli_bot2", "app_secret": "secret_bot2"},
            }
        },
    )
    adapter = MultiFeishuAdapter(config)
    adapter.children["default"].send = AsyncMock(return_value="sent-default")
    adapter.children["bot2"].send = AsyncMock(return_value="sent-bot2")

    result = await adapter.send("oc_chat", "hello", metadata={"account_id": "bot2"})

    assert result == "sent-bot2"
    adapter.children["bot2"].send.assert_awaited_once()
    adapter.children["default"].send.assert_not_called()


def test_multi_feishu_unknown_delivery_account_fails_closed():
    config = PlatformConfig(
        enabled=True,
        extra={
            "accounts": {
                "default": {"app_id": "cli_default", "app_secret": "secret_default"},
            }
        },
    )
    adapter = MultiFeishuAdapter(config)

    try:
        adapter._child_for_metadata({"account_id": "missing"})
    except ValueError as exc:
        assert "Unknown Feishu account_id" in str(exc)
    else:
        raise AssertionError("unknown account_id should not silently fall back")


@pytest.mark.asyncio
async def test_multi_feishu_connect_fails_closed_if_any_account_fails():
    config = PlatformConfig(
        enabled=True,
        extra={
            "accounts": {
                "default": {"app_id": "cli_default", "app_secret": "secret_default"},
                "bot2": {"app_id": "cli_bot2", "app_secret": "secret_bot2"},
            }
        },
    )
    adapter = MultiFeishuAdapter(config)
    adapter.children["default"].connect = AsyncMock(return_value=False)
    adapter.children["bot2"].connect = AsyncMock(return_value=True)
    adapter.children["bot2"].disconnect = AsyncMock(return_value=None)

    assert await adapter.connect() is False
    assert adapter._running is False
    assert adapter.fatal_error_code == "feishu_multi_connect_error"
    adapter.children["bot2"].disconnect.assert_awaited_once()


@pytest.mark.asyncio
async def test_multi_feishu_connect_fails_when_no_accounts_connect():
    config = PlatformConfig(
        enabled=True,
        extra={
            "accounts": {
                "default": {"app_id": "cli_default", "app_secret": "secret_default"},
                "bot2": {"app_id": "cli_bot2", "app_secret": "secret_bot2"},
            }
        },
    )
    adapter = MultiFeishuAdapter(config)
    adapter.children["default"].connect = AsyncMock(return_value=False)
    adapter.children["bot2"].connect = AsyncMock(return_value=False)

    assert await adapter.connect() is False
    assert adapter._running is False
    assert adapter.fatal_error_code == "feishu_multi_connect_error"


@pytest.mark.asyncio
async def test_feishu_websocket_readiness_waits_for_live_conn():
    adapter = FeishuAdapter(PlatformConfig(enabled=True, extra={"app_id": "cli_a", "app_secret": "secret_a"}))
    adapter._ws_client = SimpleNamespace(_conn=None)
    adapter._ws_future = asyncio.get_running_loop().create_future()

    async def mark_ready():
        await asyncio.sleep(0.02)
        adapter._ws_client._conn = object()

    asyncio.create_task(mark_ready())

    await adapter._wait_for_websocket_ready(timeout_seconds=0.5)


@pytest.mark.asyncio
async def test_feishu_websocket_readiness_propagates_executor_failure():
    adapter = FeishuAdapter(PlatformConfig(enabled=True, extra={"app_id": "cli_a", "app_secret": "secret_a"}))
    adapter._ws_client = SimpleNamespace(_conn=None)
    adapter._ws_future = asyncio.get_running_loop().create_future()
    adapter._ws_future.set_exception(RuntimeError("boom"))

    with pytest.raises(RuntimeError, match="boom"):
        await adapter._wait_for_websocket_ready(timeout_seconds=0.5)


@pytest.mark.asyncio
async def test_lark_ws_connect_proxy_applies_ping_overrides_per_thread():
    calls = []

    async def original_connect(*args, **kwargs):
        calls.append(kwargs)
        return "conn"

    proxy = _ThreadLocalWebsocketsConnectProxy(original_connect)
    adapter = SimpleNamespace(_ws_ping_interval=7, _ws_ping_timeout=8)
    proxy.set_adapter(adapter)

    result = await proxy("wss://example.test")

    assert result == "conn"
    assert calls == [{"ping_interval": 7, "ping_timeout": 8}]


@pytest.mark.asyncio
async def test_lark_ws_threadlocal_runtime_keeps_existing_connect_proxy():
    async def original_connect(*args, **kwargs):
        return None

    module = SimpleNamespace(
        loop=object(),
        websockets=SimpleNamespace(connect=original_connect),
    )

    loop_proxy, connect_proxy = _ensure_lark_ws_threadlocal_runtime(module)

    assert module.loop is loop_proxy
    assert module.websockets.connect is connect_proxy
    assert _ensure_lark_ws_threadlocal_runtime(module) == (loop_proxy, connect_proxy)
