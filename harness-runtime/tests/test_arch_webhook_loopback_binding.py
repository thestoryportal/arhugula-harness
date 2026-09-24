"""Local-only webhook operator binding guards for the first Omarchy profile."""

from __future__ import annotations

import asyncio
import hashlib
import json
from pathlib import Path

import httpx
import pytest
from harness_core.deployment_surface import DeploymentSurface
from harness_cp.hitl_timeout_degradation import WebhookConfig, WebhookPayload
from harness_cp.topology_pattern import TopologyPattern
from harness_cp.validator_framework_types import HITLEscalationBrief, ValidatorFailClass
from harness_runtime.bootstrap.factories.webhook_delivery_composer_factory import (
    WebhookDeliveryComposerStageMaterializeError,
    materialize_webhook_delivery_composer_stage,
)
from harness_runtime.bootstrap.mutable_context import _MutableHarnessContext
from harness_runtime.config_source import RuntimeConfigLoadError, RuntimeConfigSource
from harness_runtime.lifecycle.pause_resume_protocol_types import PauseResumeProtocolConfig
from harness_runtime.lifecycle.webhook_delivery_composer import (
    WebhookDeliveryComposer,
    WebhookDeliveryExhaustedError,
)
from harness_runtime.lifecycle.webhook_delivery_composer_types import (
    WebhookDeliveryComposerConfig,
    parse_loopback_webhook_endpoint,
)
from harness_runtime.types import OTelConfig, RuntimeConfig


def _config(tmp_path: Path, webhook: WebhookDeliveryComposerConfig) -> RuntimeConfig:
    return RuntimeConfig(
        deployment_surface=DeploymentSurface.LOCAL_DEVELOPMENT,
        repository_root=tmp_path,
        default_topology=TopologyPattern.SINGLE_THREADED_LINEAR,
        otel=OTelConfig(otlp_endpoint="http://localhost:4318"),
        webhook_delivery_composer_config=webhook,
    )


@pytest.mark.parametrize(
    "url",
    [
        "http://localhost:1234/hitl",
        "http://127.0.0.2:1234/hitl",
        "http://192.168.1.2:1234/hitl",
        "http://169.254.169.254/latest",
        "http://[::ffff:127.0.0.1]:1234/hitl",
        "http://example.com:1234/hitl",
        "http://127.0.0.1:1234/hitl?token=x",
        "http://127.0.0.1:1234/hitl?",
        "http://user:pass@127.0.0.1:1234/hitl",
        "http://127.0.0.1:1234/hitl#fragment",
        "http://127.0.0.1:1234/hitl#",
        "http://0x7f000001:1234/hitl",
        "http://127.0.0.1:0/hitl",
        "https://127.0.0.1:1234/hitl",
    ],
)
def test_operator_endpoint_refuses_nonliteral_or_ambiguous_targets(url: str) -> None:
    with pytest.raises(ValueError):
        parse_loopback_webhook_endpoint(url)


@pytest.mark.parametrize("url", ["http://127.0.0.1:1234/hitl", "http://[::1]:1234/hitl"])
def test_operator_endpoint_accepts_only_exact_loopback_literals(url: str) -> None:
    assert parse_loopback_webhook_endpoint(url) == url


def test_runtime_toml_loads_typed_webhook_and_refuses_unknown_fields(tmp_path: Path) -> None:
    path = tmp_path / "harness.toml"
    stem = (
        "[runtime]\n"
        'deployment_surface = "local-development"\n'
        f'repository_root = "{tmp_path}"\n'
        'default_topology = "single-threaded-linear"\n'
        "[runtime.otel]\n"
        'otlp_endpoint = "http://localhost:4318"\n'
        "[runtime.webhook_delivery_composer_config]\n"
        'webhook_id = "local-approval"\n'
        'endpoint_url = "http://127.0.0.1:1234/hitl"\n'
        "timeout_seconds = 3\n"
    )
    path.write_text(stem)
    config = RuntimeConfigSource.load(config_file=path)
    assert config.webhook_delivery_composer_config == WebhookDeliveryComposerConfig(
        webhook_id="local-approval",
        endpoint_url="http://127.0.0.1:1234/hitl",
        timeout_seconds=3,
    )
    path.write_text(stem + 'unexpected = "bad"\n')
    with pytest.raises(RuntimeConfigLoadError, match="unexpected"):
        RuntimeConfigSource.load(config_file=path)


@pytest.mark.asyncio
async def test_stage_five_binds_one_attempt_loopback_client(tmp_path: Path) -> None:
    webhook = WebhookDeliveryComposerConfig(
        webhook_id="local-approval",
        endpoint_url="http://127.0.0.1:1234/hitl",
        timeout_seconds=3,
    )
    composer = await materialize_webhook_delivery_composer_stage(
        _config(tmp_path, webhook), _MutableHarnessContext()
    )
    assert composer is not None
    assert composer._webhook_config is not None
    assert composer._webhook_config.webhook_id == "local-approval"
    assert composer._webhook_config.endpoint_url == webhook.endpoint_url
    assert composer._webhook_config.timeout == 3
    assert composer._retry_max_attempts == 1
    async with composer._http_client_factory() as client:
        assert client.follow_redirects is False
        assert client._trust_env is False


@pytest.mark.asyncio
async def test_durable_pause_refuses_empty_webhook_marker(tmp_path: Path) -> None:
    config = _config(tmp_path, WebhookDeliveryComposerConfig.default()).model_copy(
        update={"pause_resume_protocol_config": PauseResumeProtocolConfig(durable=True)}
    )
    with pytest.raises(WebhookDeliveryComposerStageMaterializeError, match="endpoint"):
        await materialize_webhook_delivery_composer_stage(config, _MutableHarnessContext())


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "webhook",
    [
        WebhookDeliveryComposerConfig(endpoint_url="http://127.0.0.1:1234/hitl"),
        WebhookDeliveryComposerConfig(webhook_id="local-approval"),
        WebhookDeliveryComposerConfig(timeout_seconds=99),
        WebhookDeliveryComposerConfig(
            webhook_id="local-approval",
            endpoint_url="http://127.0.0.1:1234/hitl",
            timeout_seconds=0,
        ),
    ],
)
async def test_stage_five_refuses_partial_or_unbounded_operator_config(
    tmp_path: Path, webhook: WebhookDeliveryComposerConfig
) -> None:
    with pytest.raises(WebhookDeliveryComposerStageMaterializeError):
        await materialize_webhook_delivery_composer_stage(
            _config(tmp_path, webhook), _MutableHarnessContext()
        )


@pytest.mark.asyncio
async def test_cost_audit_target_uses_digest_not_url_path(monkeypatch: pytest.MonkeyPatch) -> None:
    import harness_runtime.lifecycle.cost_attribution_webhook_dispatch as cost_module
    import harness_runtime.lifecycle.webhook_delivery_composer as composer_module

    captured: dict[str, object] = {}

    def capture(**kwargs: object) -> None:
        captured.update(kwargs)

    async def inline_offload(fn: object, *args: object, **kwargs: object) -> object:
        return fn(*args, **kwargs)

    monkeypatch.setattr(cost_module, "attribute_webhook_dispatch_cost", capture)
    monkeypatch.setattr(composer_module, "run_audit_off_loop", inline_offload)
    endpoint = "http://127.0.0.1:1234/hooks/pathsecret"
    composer = WebhookDeliveryComposer(
        retry_max_attempts=1,
        http_client_factory=lambda: httpx.AsyncClient(
            transport=httpx.MockTransport(lambda _request: httpx.Response(204))
        ),
        rate_table=object(),
        cost_chain=object(),
        audit_writer=object(),
        workflow_id="wf-local",
        parent_action_id="hitl:wf-local:gate:0",
        parent_idempotency_key="parent-idem",
    )
    result = await composer.deliver_webhook(
        WebhookConfig(
            webhook_id="public-local-id",
            endpoint_url=endpoint,
            timeout=3,
            degradation_mode="fail-closed",
        ),
        WebhookPayload(
            approval_id="approve-local",
            idempotency_key="idem-payload",
            gate_evaluation_ref="entry-local",
            payload_body={"prompt": "Approve?"},
        ),
        "idem-request",
    )
    assert result.delivered is True
    target = captured["webhook_target"]
    assert target == hashlib.sha256(endpoint.encode()).hexdigest()
    assert "pathsecret" not in str(captured)
    assert endpoint not in str(captured)


@pytest.mark.asyncio
@pytest.mark.parametrize("redirect", [False, True])
async def test_real_loopback_post_ignores_proxy_and_redirect(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, redirect: bool
) -> None:
    requests: list[tuple[bytes, bytes]] = []

    async def handle(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        head = await reader.readuntil(b"\r\n\r\n")
        length = next(
            int(line.split(b":", 1)[1].strip())
            for line in head.split(b"\r\n")
            if line.lower().startswith(b"content-length:")
        )
        body = await reader.readexactly(length)
        requests.append((head, body))
        if redirect:
            writer.write(
                b"HTTP/1.1 302 Found\r\nLocation: http://169.254.169.254/latest\r\n"
                b"Content-Length: 0\r\nConnection: close\r\n\r\n"
            )
        else:
            writer.write(
                b"HTTP/1.1 204 No Content\r\nContent-Length: 0\r\nConnection: close\r\n\r\n"
            )
        await writer.drain()
        writer.close()
        await writer.wait_closed()

    server = await asyncio.start_server(handle, "127.0.0.1", 0)
    port = server.sockets[0].getsockname()[1]
    monkeypatch.setenv("HTTP_PROXY", "http://127.0.0.1:1")
    monkeypatch.setenv("NO_PROXY", "")
    config = _config(
        tmp_path,
        WebhookDeliveryComposerConfig(
            webhook_id="local-approval",
            endpoint_url=f"http://127.0.0.1:{port}/hitl",
            timeout_seconds=3,
        ),
    )
    try:
        composer = await materialize_webhook_delivery_composer_stage(
            config, _MutableHarnessContext()
        )
        assert composer is not None
        brief = HITLEscalationBrief(
            parent_step_id="step-0",
            parent_action_id="action-local-1",
            fail_class=ValidatorFailClass.EXTERNAL_REJECTION,
            fail_detail_hash=None,
            escalation_reason="local-test",
        )
        if redirect:
            with pytest.raises(WebhookDeliveryExhaustedError):
                await composer.deliver_webhook_for_brief(brief, "idem-local-1")
        else:
            result = await composer.deliver_webhook_for_brief(brief, "idem-local-1")
            assert result.delivered and result.status_code == 204 and result.delivery_attempts == 1
        assert len(requests) == 1
        head, body = requests[0]
        assert head.startswith(b"POST /hitl HTTP/1.1\r\n")
        assert b"idempotency-key: idem-local-1" in head.lower()
        assert b"authorization:" not in head.lower()
        assert json.loads(body)["idempotency_key"] == "idem-local-1"
    finally:
        server.close()
        await server.wait_closed()
