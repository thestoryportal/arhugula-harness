"""Stage 4 OD — tracer + span_processor + collector + ring buffer + cost chain + audit writer.

Per `Spec_Harness_Runtime_v1.md` v1.1 §2 stage 4 post-conditions:
`opentelemetry.trace.get_tracer_provider()` returns the runtime-registered
provider; `ctx.collector_daemon` is running (health-check ok); `ctx.cost_chain`,
`ctx.audit_writer` non-None.

Composer call order (intra-stage dependencies):
1. `materialize_tracer_provider_stage` — globally registers TracerProvider.
2. `materialize_audit_writer_stage(config, ledger_writer)` — depends on stage 1.
3. `materialize_span_processor_stage(config, provider, audit_writer=...)` —
   attaches redaction + BSP + exporter; multi-tenant token maps can persist
   through the audit writer.
4. `materialize_collector_daemon_stage(config)` — supervisor (NOT started yet).
5. `await daemon.start()` — start the collector daemon explicitly (docstring
   at `lifecycle/collector_daemon.py` line ~60: "The bootstrap orchestrator
   (U-RT-43) calls `await stage.daemon.start()` at the stage 4 entry").
6. `materialize_ring_buffer_stage(config, daemon)` — depends on running daemon.
7. `materialize_cost_attribution_stage(config)`.

**Tracer rollback (Class 3 informational).** OTel has no `unset_tracer_provider`
API. On stage 4 failure, rollback leaves the global provider registered;
subsequent process invocations replace via `set_tracer_provider`. Deferred to
U-RT-44/45 shutdown work if a true unregister API is needed.
"""

from __future__ import annotations

from harness_core import PersonaTier
from harness_core.workload_class import WorkloadClass

from harness_runtime.bootstrap.factories.validator_framework_factory import (
    materialize_validator_framework_stage,
)
from harness_runtime.bootstrap.mutable_context import _MutableHarnessContext
from harness_runtime.config.audit_signing import make_audit_signing_backend
from harness_runtime.lifecycle.audit_signing_fail_closed_validation import (
    initialize_mtc_audit_signing_record,
    validate_mtc_audit_signing_config,
)
from harness_runtime.lifecycle.audit_writer import (
    AUDIT_SIDECAR_FILENAME,
    ledger_holds_audit_refs,
    materialize_audit_writer_stage,
)
from harness_runtime.lifecycle.collector_daemon import materialize_collector_daemon_stage
from harness_runtime.lifecycle.cost_attribution import materialize_cost_attribution_stage
from harness_runtime.lifecycle.ring_buffer import materialize_ring_buffer_stage
from harness_runtime.lifecycle.span_processor import (
    materialize_span_processor_stage,
    validate_audit_signing_for_span_stage,
)
from harness_runtime.lifecycle.tracer_provider import materialize_tracer_provider_stage
from harness_runtime.types import RuntimeConfig

__all__ = ["execute"]


async def execute(
    ctx: _MutableHarnessContext,
    config: RuntimeConfig,
    workload_class: WorkloadClass,
) -> None:
    """Populate stage 4 OD fields on `ctx`."""
    _ = workload_class
    assert ctx.ledger_writer is not None, "stage 1 IS must precede stage 4 OD"

    # 0a. Audit-signing config-VALUE-SHAPE validation (U-RT-134, C-RT-03
    # v1.101) — runs FIRST, before `make_audit_signing_backend` is even
    # called (out-of-family Codex [P2] finding: an invalid explicit-`false`-
    # at-MTC config could otherwise fail on backend CONSTRUCTION first —
    # missing boto3, region resolution, credential discovery — instead of
    # deterministically producing the spec-mandated typed
    # `AuditSigningConfigInvalidError`/`IncompatibleConfigVersion`). This
    # pass touches config only — no backend I/O, no side effects.
    validate_mtc_audit_signing_config(config)
    # 0b. Audit-signing backend (B-47 PR B — OD spec v1.33 §21.2.1 composition
    # root) — constructed AND validated BEFORE the one-shot global tracer
    # registration (out-of-family Codex round-18: OTel registration cannot be
    # undone, so a KMS config failure surfacing after it poisoned
    # same-process bootstrap retry). `None` for the default `backend = "none"`
    # config: every signing surface keeps the placeholder path byte-for-byte;
    # a configured backend that cannot be built (missing boto3, alias ARN,
    # missing consumer key) fails the stage loud — a deployment that asked
    # for real signing never silently degrades. `tokenizer_will_bind` uses
    # the persona predicate directly: stage 4 always materializes the audit
    # writer below, so MTC ⇒ the token map WILL bind.
    ctx.audit_signing_backend = make_audit_signing_backend(config.audit_signing)
    validate_audit_signing_for_span_stage(
        config,
        signing_backend=ctx.audit_signing_backend,
        tokenizer_will_bind=config.persona_tier == PersonaTier.MULTI_TENANT_COMPLIANCE,
        # B-47 PR B2a — the key_ids the threaded composers/builders sign
        # under on EVERY audit write (tokenizer-independent): the stage-5
        # HITL/sub-agent composers' "harness-runtime-dev" and the four cost
        # builders' shared "harness-cost-attribution-v1"
        # (`_DEFAULT_SIGNING_KEY_ID`). Validated here so a KMS mapping gap
        # fails BOOTSTRAP, not the first mid-run audit write.
        additional_key_ids=("harness-runtime-dev", "harness-cost-attribution-v1"),
    )
    # U-RT-134 — side-effecting cutover-record load-or-greenfield-init, run
    # LAST of the three audit-signing checks (still before tracer
    # registration, same round-18 rationale): by this point every OTHER
    # signing-config gap (missing/invalid inputs; the additional_key_ids
    # mapping) has already been rejected, so a record is never written to
    # disk only to have bootstrap fail moments later on an unrelated gap.
    # The ledger-freshness gate's two inputs (codex [P1] rounds 4/5) are
    # derived from the STAGE-1 ledger handle directly, since the audit
    # writer itself materializes only at step 2 below: the sidecar location
    # (shared `AUDIT_SIDECAR_FILENAME` source of truth) plus the lazy
    # IS-refs probe (the freshness AUTHORITY — a deleted sidecar alongside
    # surviving hash-chained `audit:` refs must still read NOT-fresh).
    stage_1_ledger_writer = ctx.ledger_writer
    initialize_mtc_audit_signing_record(
        config,
        signing_backend=ctx.audit_signing_backend,
        audit_sidecar_path=(
            stage_1_ledger_writer.handle.canonical_path.parent / AUDIT_SIDECAR_FILENAME
        ),
        ledger_has_audit_refs=lambda: ledger_holds_audit_refs(stage_1_ledger_writer),
    )

    # 1. Tracer provider — globally registered.
    tracer = materialize_tracer_provider_stage(config)
    ctx.tracer_provider = tracer.provider

    # 2. Audit-ledger writer (depends on stage 1 ledger writer). The redaction
    # token-map path consumes this at multi-tenant cells, so it must exist
    # before the span processor is attached.
    audit = materialize_audit_writer_stage(config, ctx.ledger_writer)
    ctx.audit_writer = audit.writer

    # 3. Span processor + exporter (attaches to the registered tracer provider).
    materialize_span_processor_stage(
        config,
        tracer.provider,
        audit_writer=ctx.audit_writer,
        signing_backend=ctx.audit_signing_backend,
    )
    # The span processor's lifetime is tied to the tracer provider; the stage
    # record is not held on HarnessContext (the BSP is reachable via the
    # tracer provider's processor list). The C-RT-10 shutdown will need to
    # retain a typed handle — addressed at U-RT-45.

    # 4. Collector daemon supervisor (constructed; NOT yet started).
    daemon_stage = materialize_collector_daemon_stage(config)

    # 5. Start the daemon. Failure here surfaces as a stage 4 failure and
    # triggers rollback of stages 0-3 + stage-4 partial-state cleanup.
    await daemon_stage.daemon.start()
    ctx.collector_daemon = daemon_stage.daemon

    # 6. Ring buffer (depends on running daemon).
    materialize_ring_buffer_stage(config, daemon_stage.daemon)
    # Like the span processor, the ring buffer's lifetime is tied to the
    # daemon supervisor; HarnessContext exposes the daemon, not the buffer.

    # 7. Cost attribution chain. The concrete chain narrows the Protocol's
    # deliberately `object`-typed method params (documented decoupling at
    # types.py); concrete → Protocol-typed field is a benign contravariance.
    cost = materialize_cost_attribution_stage(config)
    ctx.cost_chain = cost.chain  # pyright: ignore[reportAttributeAccessIssue]

    # 8. Validator framework (U-RT-84) — final stage-4 binding per runtime
    # spec v1.18 §14.13.3. Operator-opt-in: `None` (default) preserves the
    # v1.17 production-default state; non-`None` constructs an empty-registry
    # ConcreteValidatorFramework per Reading A scope.
    #
    # U-OD-40 cost-attribution hook wiring per CP spec v1.24 §28.10.5
    # mechanism (a): pass rate_table + cost_chain + audit_writer through to
    # the factory. When opt-in and all 3 substrates bound, the factory
    # constructs a CostAttributingValidatorHook and injects it via the
    # ConcreteValidatorFramework's optional post_evaluate_hook ctor param
    # per CP spec v1.24 §28.10.2.
    from harness_od.rate_table_v1 import RATE_TABLE_V1

    ctx.validator_framework = await materialize_validator_framework_stage(
        config,
        rate_table=RATE_TABLE_V1,
        cost_chain=ctx.cost_chain,
        audit_writer=ctx.audit_writer,
        # R-FS-1 arc CA + B-INTERSTEP-PERRUN-ISOLATION — thread the run-scoped
        # accumulator PROXY (not its `.records` list) so per-validator
        # SpanCostRecords `append` through to the current run's accumulator →
        # `RunResult.cost_attribution` (runtime v1.53 §9).
        cost_record_sink=ctx.cost_record_accumulator,
        # B-23 — threaded to CostAttributingValidatorHook so the
        # cost-attribution audit entry's `entry_core` is a real F2 anchor
        # instead of a fabricated `cp-audit:<action_id>` marker. Both are
        # already bound on `ctx` by stage 3b (`_materialize_cp_is_wiring_for_
        # routing`), well before this stage-4 call.
        ledger_writer=ctx.ledger_writer,
        procedural_tier_snapshot_resolver=ctx.procedural_tier_snapshot_resolver,
        # B-47 PR B2a — OD spec v1.33 §21.2.1 signing seam (constructed at
        # step 0 of this same stage).
        signing_backend=ctx.audit_signing_backend,
    )
