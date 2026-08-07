"""Per-site witnesses for the runtime half of IS plan v2.9 §2.1 —
C-IS-07 §7.6.1 per-call-site writer-owned ELECTION (IS spec v1.13, `B-57`).

Rows 11-14 live in `harness-runtime`:

- **row 11** `hitl_gate_composer` — ELECT;
- **row 12** `audit_writer` — the first injection-caveat row, resolved ELECT
  (witnessed in its own module at `test_lifecycle_audit_writer.py`, where the
  affected determinism tests also live);
- **row 13** `cost_attribution_f2_write` — the second injection-caveat row,
  resolved ELECT;
- **row 14** `as_is_wiring` — **RETAIN**: it carries genuine EVENT time and
  §7.6.1's eligibility rule FORBIDS electing there. That control is the guard
  against a blanket sweep, and it is the one witness in this file whose PD-8
  probe is an addition rather than a reversion: ELECT at row 14 and it fails.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path

from harness_as.secret_fetch import SecretScope
from harness_as.secret_fetch_audit import SecretFetchEvent
from harness_core.deployment_surface import DeploymentSurface
from harness_core.workload_class import WorkloadClass
from harness_cp.topology_pattern import TopologyPattern
from harness_is.path_class_registry import PathClass
from harness_is.path_resolver import PathResolver
from harness_is.state_ledger_entry_schema import Actor, ActorClass, Identifier
from harness_is.state_ledger_write import (
    WRITER_OWNED_TIMESTAMP,
    EntryPayload,
    WriteKey,
    WriteResult,
    read_ledger,
)
from harness_runtime.config.path_bindings import build_path_binding
from harness_runtime.lifecycle.as_is_wiring import materialize_as_is_wiring_stage
from harness_runtime.lifecycle.cost_attribution_f2_write import (
    compose_cost_f2_entry_core,
)
from harness_runtime.lifecycle.state_ledger import (
    LedgerWriter,
    materialize_state_ledger,
)
from harness_runtime.types import (
    CollectorConfig,
    OTelConfig,
    PathBindingConfig,
    ProviderSecretsConfig,
    RuntimeConfig,
)


def _resolver_for(tmp_path: Path) -> PathResolver:
    config = PathBindingConfig(
        raw_entries=(
            {
                "path_class": PathClass.STATE_LEDGER,
                "workflow_class": WorkloadClass.SOFTWARE_ENGINEERING,
                "deployment_surface": DeploymentSurface.LOCAL_DEVELOPMENT,
                "path": str(tmp_path / "state.jsonl"),
            },
        ),
    )
    return PathResolver(build_path_binding(config))


def _ledger_writer(tmp_path: Path) -> LedgerWriter:
    return materialize_state_ledger(
        _resolver_for(tmp_path),
        workflow_class=WorkloadClass.SOFTWARE_ENGINEERING,
        deployment_surface=DeploymentSurface.LOCAL_DEVELOPMENT,
        actor=Actor(actor_class=ActorClass.AGENT, actor_id="test-runtime"),
    )


def _config(tmp_path: Path) -> RuntimeConfig:
    return RuntimeConfig(
        deployment_surface=DeploymentSurface.LOCAL_DEVELOPMENT,
        repository_root=tmp_path,
        path_bindings=PathBindingConfig(),
        provider_secrets=ProviderSecretsConfig(),
        otel=OTelConfig(otlp_endpoint="http://localhost:4317"),
        collector=CollectorConfig(),
        default_topology=TopologyPattern.SINGLE_THREADED_LINEAR,
    )


class _CapturingLedgerWriter:
    """Minimal `ledger_writer` duck-type for `compose_cost_f2_entry_core`."""

    def __init__(self) -> None:
        self.captured: list[EntryPayload] = []

    def append(self, payload: EntryPayload, write_key: WriteKey) -> WriteResult:
        self.captured.append(payload)
        return WriteResult.APPENDED


# ---------------------------------------------------------------------------
# Row 13 — `cost_attribution_f2_write`, injection-caveat resolved ELECT.
# ---------------------------------------------------------------------------


def test_row_13_cost_f2_entry_elects() -> None:
    """PD-8: restore `timestamp=time_source()` and this FAILS."""
    writer = _CapturingLedgerWriter()
    ref = compose_cost_f2_entry_core(
        ledger_writer=writer,
        procedural_tier_snapshot_resolver=None,
        workflow_id="wf-1",
        parent_action_id="parent-1",
        parent_idempotency_key="parent-idem-1",
        dispatch_disambiguator="span-1",
    )
    assert ref is not None
    [payload] = writer.captured
    assert payload.timestamp == WRITER_OWNED_TIMESTAMP, (
        "IS plan v2.9 §2.1 row 13 must ELECT writer-owned sampling"
    )


def test_row_13_injected_time_source_no_longer_reaches_the_payload() -> None:
    """The AC #18 caveat at row 13, resolved and witnessed.

    Row 13's `time_source` is a DEFAULTED parameter that no caller — production
    or test — ever overrides, so electing here overrides no live injection.
    Supplying one deliberately shows the seam's timestamp role is retired: the
    absurd instant below does not reach the payload, and the parameter is still
    accepted (API stability).

    PD-8: restore `timestamp=time_source()` and the persisted value becomes the
    2026-01-01 fixture exactly.
    """
    writer = _CapturingLedgerWriter()
    absurd = datetime(2026, 1, 1, 0, 0, 0, tzinfo=UTC)
    compose_cost_f2_entry_core(
        ledger_writer=writer,
        procedural_tier_snapshot_resolver=None,
        workflow_id="wf-1",
        parent_action_id="parent-1",
        parent_idempotency_key="parent-idem-1",
        dispatch_disambiguator="span-1",
        time_source=lambda: absurd,
    )
    [payload] = writer.captured
    assert payload.timestamp != absurd
    assert payload.timestamp == WRITER_OWNED_TIMESTAMP


# ---------------------------------------------------------------------------
# Row 14 — `as_is_wiring` RETAINS caller-supplied EVENT-time semantics.
# ---------------------------------------------------------------------------


def test_as_is_wiring_event_time_append_is_not_writer_owned(tmp_path: Path) -> None:
    """AC #16 — the eligibility-rule control, and the guard against a blanket
    sweep converting an event-time site.

    `as_is_wiring` persists `composed.timestamp`, an instant passed through from
    the upstream `SecretFetchEvent` — *when the secret fetch happened*, not when
    the entry was appended. §7.6.1 REQUIRES caller-supplied semantics there, and
    an out-of-order refusal on that path is the honest outcome by design.

    PD-8: elect at row 14 and this test FAILS — the persisted instant stops
    being the composed record's own value.
    """
    wiring = materialize_as_is_wiring_stage(_config(tmp_path), _ledger_writer(tmp_path)).wiring
    event_time = datetime(2026, 5, 19, 12, 0, 0, tzinfo=UTC)
    result = wiring.emit_secret_fetch_audit_entry(
        SecretFetchEvent(
            secret_name="OPENAI_API_KEY",
            secret_scope=SecretScope(name="default"),
            secret_last_rotated_at="2026-05-01T00:00:00+00:00",
            actor=Actor(actor_class=ActorClass.AGENT, actor_id="emission-site"),
            timestamp=event_time,
            thread_id=Identifier("thread-1"),
            step_id=Identifier("step-1"),
        )
    )
    assert result is WriteResult.APPENDED

    [entry] = read_ledger(wiring.ledger_writer.handle)
    assert entry.timestamp == event_time, (
        "row 14 RETAINS caller-supplied EVENT-time semantics — the persisted "
        "instant IS the upstream composed record's own value"
    )
    # Stated positively too: the sentinel never resolves to a year-2026-05
    # fixture, so this is not an accidental match.
    assert entry.timestamp != WRITER_OWNED_TIMESTAMP
    assert abs(entry.timestamp - datetime.now(UTC)) > timedelta(days=1)
