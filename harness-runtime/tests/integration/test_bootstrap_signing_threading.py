"""B-47 PR B2a — REAL-bootstrap witness for audit-signing backend threading.

Merge-gate round-1 test-witness lens on PR B1 (register item (k)): the
stage-4 `signing_backend=` kwarg into the span processor was
unwitnessed-but-fail-loud, and PR B2a adds five more construction-site
kwargs (three `RuntimeHITLGateComposer`s + `RuntimeSubAgentDispatcher` +
the LLM dispatcher) plus factory hops (tool / webhook / validator). Each of
those is a single deletable line that unit tests constructing composers
directly can never see. This witness runs the REAL bootstrap through stage
5 with an `aws-kms` config (hermetic fake KMS client) and asserts the ONE
`ctx.audit_signing_backend` instance reached every reachable signing
carrier — deleting any threading kwarg leaves that carrier's
`signing_backend` at its `None` default and fails the identity check.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
from harness_runtime.bootstrap import (
    BootstrapFailure,
    run_bootstrap,
    stage_6_cxa_wiring,
)
from harness_runtime.config.audit_signing import BreakerGuardedSigningBackend
from harness_runtime.types import AuditSigningBackendKind, AuditSigningConfig

from tests.integration.conftest import WORKLOAD, build_config

_ARN = "arn:aws:kms:us-east-1:111122223333:key/deadbeef-dead-beef-dead-beefdeadbeef"

_WRAPPER_ATTRS = ("inner", "_inner", "post_evaluate_hook")
_CARRIER_ATTRS = ("signing_backend", "_signing_backend")


def _collect_signing_carriers(root: Any) -> dict[str, Any]:
    """Walk wrapper chains from `root`, returning {class_name: carried value}
    for every object that DECLARES a signing-backend attribute (value may be
    None — that is exactly the mutation this witness exists to catch)."""
    found: dict[str, Any] = {}
    seen: set[int] = set()
    frontier = [root]
    while frontier:
        obj = frontier.pop()
        if obj is None or id(obj) in seen or len(seen) > 100:
            continue
        seen.add(id(obj))
        for attr in _CARRIER_ATTRS:
            if hasattr(obj, attr):
                found[type(obj).__name__] = getattr(obj, attr)
                break
        for attr in _WRAPPER_ATTRS:
            nxt = getattr(obj, attr, None)
            if nxt is not None and not isinstance(nxt, (str, bytes, int, float, bool)):
                frontier.append(nxt)
    return found


@pytest.mark.asyncio
async def test_kms_backend_threads_into_every_reachable_audit_composer(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    patched_runtime: dict[str, Any],
) -> None:
    _ = patched_runtime
    config = build_config(tmp_path).model_copy(
        update={
            "audit_signing": AuditSigningConfig(
                backend=AuditSigningBackendKind.AWS_KMS,
                key_arns={
                    "harness-runtime-redaction-token": _ARN,
                    "harness-runtime-dev": _ARN,
                    "harness-cost-attribution-v1": _ARN,
                },
            )
        }
    )
    # Hermetic KMS: patch ONLY the boto3 client constructor — stage 4 still
    # runs the real make_audit_signing_backend (breaker wrap included).
    monkeypatch.setattr(
        "harness_runtime.config.audit_signing._default_kms_client",
        lambda region: object(),
    )

    captured: list[Any] = []

    async def _capture_and_boom(ctx: Any, config_: Any, workload_class: Any) -> None:
        _ = config_, workload_class
        captured.append(ctx)
        raise RuntimeError("stop after stage 5")

    monkeypatch.setattr(stage_6_cxa_wiring, "execute", _capture_and_boom)

    with pytest.raises(BootstrapFailure):
        await run_bootstrap(config, workload_class=WORKLOAD)

    assert len(captured) == 1
    ctx = captured[0]
    backend = ctx.audit_signing_backend
    assert isinstance(backend, BreakerGuardedSigningBackend)

    roots = {
        "llm_dispatcher": ctx.llm_dispatcher,
        "sub_agent_dispatcher": ctx.sub_agent_dispatcher,
        "tool_dispatcher": ctx.tool_dispatcher,
        "webhook_delivery_composer": ctx.webhook_delivery_composer,
        "validator_framework": ctx.validator_framework,
    }
    all_found: dict[str, Any] = {}
    for root in roots.values():
        all_found.update(_collect_signing_carriers(root))

    # Every carrier that DECLARES the seam must hold the ONE backend
    # instance — a deleted threading kwarg leaves its None default here.
    assert all_found, f"no signing carriers reachable from roots {list(roots)}"
    wrong = {name: val for name, val in all_found.items() if val is not backend}
    assert not wrong, f"carriers not threaded with ctx backend: {wrong!r}"

    # The two dataclass composers this PR threads must be among the
    # reachable carriers (guards against the walker silently losing them).
    assert "RuntimeHITLGateComposer" in all_found
    assert "RuntimeSubAgentDispatcher" in all_found
