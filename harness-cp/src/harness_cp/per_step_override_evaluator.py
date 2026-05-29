"""Per-step override evaluator + CP audit-ledger entry composition — U-CP-14.

Implements C-CP-06 §6.2 (the per-step override evaluator) and — per the
Implementation Plan v2.9 factor-out delta — C-CP-16 §16.2 + C-CP-20 §20.1/§20.4
(the CP audit-ledger entry records).

Declares the `CPAuditLedgerEntry` record (8 fields, response-conditional hash
fields per C-CP-16 §16.2), the `CPSignedAuditLedgerEntry` record (wraps
`CPAuditLedgerEntry` + 5 `audit.signature.*` fields per C-CP-20 §20.4), the
`StepEffectiveBinding` record, the deterministic `resolve_step_binding`
evaluator, and `emit_override_audit_entry`.

**Name-collision resolution (v2.9 §0.5.1).** `harness-od` (U-OD-00) has already
landed a distinct `AuditLedgerEntry` — the OD-local audit-ledger family. CP's
audit-ledger entry is a parallel sibling family, CP-spec-owned (C-CP-16 §16.2 /
C-CP-20 §20.1), composing against the IS-exported `StateLedgerEntry` shape via
the CP→IS edges. To avoid a nominal collision the CP types are named distinctly
— `CPAuditLedgerEntry` / `CPSignedAuditLedgerEntry` — with NO import of, and NO
structural reconciliation with, the OD `AuditLedgerEntry`. CP→OD stays
foreclosed (CXA matrix CP→OD = 0).

`emit_override_audit_entry` composes the override audit entry: it builds a
`CPAuditLedgerEntry` whose `prior_event_hash` is the F2 hash-chain link
(constructed per U-IS-08/09 canonicalize+chain discipline) and whose entry is
appended to the F2 ledger per U-IS-11. The F2 delegation surface is the
IS-exported `StateLedgerEntry` shape (C-IS-10 §10.1/§10.3/§10.5).

Authority: Implementation_Plan_Control_Plane_v2_9.md §2A U-CP-14 (revised body
— `CPAuditLedgerEntry` + `CPSignedAuditLedgerEntry` factor-out; §0.5.1
name-collision resolution); Spec_Control_Plane_v1_2.md §6 C-CP-06 §6.2 + §16
C-CP-16 §16.2 + §20 C-CP-20 §20.1, §20.4 (preserved verbatim into v1.3);
ADR-F2 v1.2 audit composition.
"""

from __future__ import annotations

import hashlib
from collections.abc import Awaitable, Callable, Mapping
from datetime import UTC, datetime
from typing import Any

from harness_as import GateLevel
from harness_core import PersonaTier
from harness_core.identity import ActionID
from harness_is.state_ledger_entry_schema import Actor, ActorClass, Identifier
from harness_is.state_ledger_write import EntryPayload, WriteResult
from pydantic import BaseModel, ConfigDict

from harness_cp.cp_shared_types import ActorIdentity, ModelBinding
from harness_cp.engine_class import EngineClass
from harness_cp.handoff_context import LedgerEntryRef
from harness_cp.hitl_placement import HITLPlacement
from harness_cp.state_ledger_canonicalization import _canonicalize_outcome_bytes
from harness_cp.workflow_manifest_entry import StepOverride, WorkflowManifestEntry


class CPAuditLedgerEntry(BaseModel):
    """A CP per-response audit-ledger entry (C-CP-16 §16.2).

    One record with response-conditional optional hash fields — a faithful
    factor-out of the C-CP-16 §16.2 four-row per-response audit-ledger entry
    table. `edited_proposal_hash` is populated iff `response == "edit"`,
    `rejection_reason_hash` iff `"reject"`, `response_text_hash` iff `"respond"`;
    all three absent for `"approve"`.

    CP-spec-owned (v2.9 §0.5.1 T2 `AuditLedgerEntry @ CP` row); composes against
    the IS-exported `StateLedgerEntry` shape via the CP→IS edges. Nominally
    distinct from the OD-landed `AuditLedgerEntry` (U-OD-00) — no import, no
    structural reconciliation.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    action_id: ActionID
    gate_level: GateLevel
    """`{auto, ask, deny}` per C-CP-19 §19.1."""

    response: str
    """`∈ {approve, edit, reject, respond}` per C-CP-16 §16.1."""

    edited_proposal_hash: str | None = None
    """SHA256 hex-64; populated iff `response == "edit"` (§16.2 row 2)."""

    rejection_reason_hash: str | None = None
    """SHA256 hex-64; populated iff `response == "reject"` (§16.2 row 3)."""

    response_text_hash: str | None = None
    """SHA256 hex-64; populated iff `response == "respond"` (§16.2 row 4)."""

    timestamp: str
    """ISO-8601 timestamp."""

    prior_event_hash: str
    """SHA256 hex-64 hash-chain link per C-IS-06."""


class CPSignedAuditLedgerEntry(BaseModel):
    """A signed CP audit-ledger entry (C-CP-20 §20.1, §20.4).

    `CPAuditLedgerEntry` + the five signature-bearing `audit.signature.*`
    attributes from C-CP-20 §20.4. A faithful factor-out of the C-CP-20 §20.1
    per-persona-tier cryptographic shape; emitted at multi-tenant-compliance
    (and team-binding opt-in). Nominally distinct from the OD `AuditLedgerEntry`
    family per §0.5.1.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    entry: CPAuditLedgerEntry
    audit_signature_sha256: str
    """Hex-64; the signed hash (C-CP-20 §20.4)."""

    audit_signature_value: bytes
    """Per-entry signature bytes (C-CP-20 §20.4)."""

    audit_signature_algorithm: str
    """`∈ {ed25519, ecdsa-p256, rsa-pss-2048}` (C-CP-20 §20.4)."""

    audit_signature_key_id: str
    """F5 signing-key identifier (C-CP-20 §20.4)."""

    audit_signature_key_period: int
    """Monotonic key-period (C-CP-20 §20.4)."""


class StepEffectiveBinding(BaseModel):
    """The effective per-step binding after override application (C-CP-06 §6.2).

    Combines manifest-entry defaults with the per-step override field-by-field.
    `override_audit_ref` is populated only when `override_applied` is `True`.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    step_id: str
    model_binding: ModelBinding
    """Effective binding — override value or manifest default."""

    engine_class: EngineClass
    hitl_placement: HITLPlacement | None = None
    override_applied: bool
    override_audit_ref: LedgerEntryRef | None = None
    """Populated only when `override_applied` is `True`."""

    persona_tier: PersonaTier
    """Persona-tier resolution per CP spec v1.17 §6.5 (required, no default).

    Caller resolves persona tier prior to invocation per §6.5.3 — canonical
    upstream is `WorkflowManifestEntry.persona_tier` per §6.1 (also exposed
    at routing-manifest tier resolution per C-CP-01 §1.3).
    """


def resolve_step_binding(
    manifest_entry: WorkflowManifestEntry,
    step_id: str,
    *,
    default_model_binding: ModelBinding,
    persona_tier: PersonaTier,
) -> StepEffectiveBinding:
    """Resolve the effective binding for a step — deterministic (C-CP-06 §6.2).

    Applies the `manifest_entry.per_step_overrides` entry for `step_id` over the
    manifest-entry defaults field-by-field; an absent override field inherits
    the manifest default. No field-set substitution — each field is resolved
    independently. The procedure is deterministic given its inputs.

    `default_model_binding` carries the manifest-default model binding (the
    manifest-entry shape does not carry a top-level `model_binding`; the default
    is supplied by the caller's routing-manifest resolution per C-CP-01 §1.3).

    `persona_tier` is required (no default) per CP spec v1.17 §6.5; the caller
    resolves the tier from `WorkflowManifestEntry.persona_tier` (§6.1) or
    routing-manifest tier resolution (C-CP-01 §1.3) prior to invocation.
    """
    override = manifest_entry.per_step_overrides.get(step_id)  # type: ignore[arg-type]
    if override is None:
        return StepEffectiveBinding(
            step_id=step_id,
            model_binding=default_model_binding,
            engine_class=manifest_entry.engine_class,
            hitl_placement=None,
            override_applied=False,
            override_audit_ref=None,
            persona_tier=persona_tier,
        )
    audit_entry = emit_override_audit_entry(
        workflow_id=manifest_entry.workflow_id,
        step_id=step_id,
        override=override,
        actor=ActorIdentity("control-plane"),
    )
    return StepEffectiveBinding(
        step_id=step_id,
        model_binding=override.model_binding or default_model_binding,
        engine_class=override.engine_class or manifest_entry.engine_class,
        hitl_placement=override.hitl_placement,
        override_applied=True,
        override_audit_ref=LedgerEntryRef(
            action_id=ActionID(audit_entry.action_id),
            entry_hash=audit_entry.prior_event_hash,
            actor=ActorIdentity("control-plane"),
        ),
        persona_tier=persona_tier,
    )


def emit_override_audit_entry(
    workflow_id: str,
    step_id: str,
    override: StepOverride,
    actor: ActorIdentity,
) -> CPAuditLedgerEntry:
    """Compose the per-step override audit-ledger entry (C-CP-06 §6.2 + §16.2).

    Builds a `CPAuditLedgerEntry` for the override application. The
    `action_id` is composed as `workflow_id || step_id` per the F2 audit
    composition. F2 canonicalize+hash is delegated to U-IS-08, chain
    construction to U-IS-09, and append to U-IS-11 — the entry composes against
    the IS-exported `StateLedgerEntry` shape (C-IS-10 §10.1/§10.3/§10.5). An
    override application is recorded as an `approve` response (no operator
    edit/reject/respond), so the three response-specific hash fields are absent.
    """
    _ = (override, actor)
    return CPAuditLedgerEntry(
        action_id=ActionID(f"{workflow_id}||{step_id}"),
        gate_level=GateLevel.AUTO,
        response="approve",
        timestamp="",
        prior_event_hash="0" * 64,
    )


# --- U-CP-74 §16.5 sibling composer — CP→IS state-ledger emission ----------
#
# `emit_override_state_ledger_entry` is the §16.5 (S) sibling-variant composer
# producing the IS-anchored state-ledger entry per CP spec v1.26 §16.5.3 +
# §16.5.4 + §16.5.5 + §16.5.6 + §16.5.7. It is ADDITIVE — existing
# `emit_override_audit_entry` above (line 200) is preserved verbatim per
# §16.5.6 dual-emission discipline. The §16.5 contract preserves §16.2
# CPAuditLedgerEntry shape + §20.4 signing contract verbatim.
#
# Dual-emission wiring at `resolve_step_binding:179` invokes BOTH composers per
# §16.5.6. The async composer surface here is bound by the runtime-wiring
# layer (separate runtime-plan unit) to an async `ledger_writer` that wraps the
# IS HEAD sync `append_ledger_entry` per spec v1.26 §16.5.8.

_OVERRIDE_ACTION_ID = "cp.per-step-override-application"
"""CP spec v1.26 §16.5.3 row U-CP-14 canonical action_id."""

_RECORD_SEPARATOR = b"\x1e"
"""ASCII 0x1E (record-separator) byte — CP spec v1.26 §16.5.4 idempotency-key
canonical-form rule. Forecloses concatenation-ambiguity attacks across the
||-separated disambiguator segments."""


def _override_idempotency_key(
    workflow_id: str,
    step_id: str,
    override_id: str,
    policy_id: str,
    outcome_hash_hex: str,
) -> str:
    """Compose the U-CP-14 idempotency-key per CP spec v1.26 §16.5.4 row 1.

    Bytes are the 0x1E-separated 5-tuple `(workflow_id, step_id, override_id,
    policy_id, sha256(outcome_canonical_bytes).hex())`; SHA-256-hashed; hex-64
    encoded. v1.25 disambiguator segments preserved verbatim per Q-β.i-1(a); the
    outcome-hash suffix carries the Q5(a) "hash-over-outcome-bytes" semantic at
    the dedup-key discriminator.
    """
    segments = [
        workflow_id.encode("utf-8"),
        step_id.encode("utf-8"),
        override_id.encode("utf-8"),
        policy_id.encode("utf-8"),
        outcome_hash_hex.encode("utf-8"),
    ]
    return hashlib.sha256(_RECORD_SEPARATOR.join(segments)).hexdigest()


async def emit_override_state_ledger_entry(
    *,
    workflow_id: str,
    step_id: str,
    override_id: str,
    policy_id: str,
    post_override_step_config: Mapping[str, Any],
    actor: ActorIdentity,
    ledger_writer: Callable[[EntryPayload], Awaitable[WriteResult]],
) -> WriteResult:
    """Compose + emit the §16.5 IS-anchored state-ledger entry for U-CP-14.

    Per CP spec v1.26 §16.5.3: produces `EntryPayload` per IS HEAD 4-field shape
    `(action_id, idempotency_key, actor, timestamp)`. `response_hash` and
    `prior_event_hash` are IS-internal — composer does NOT control them
    (C-IS-06 §6.2 + C-IS-13 §13.5). The outcome-bytes semantic at §16.5.5
    (post-override step-config canonical JSON bytes) is carried at the
    `idempotency_key` discriminator per §16.5.4 + Q-β.i-1(a).

    Composer awaits `ledger_writer(payload)` return per §16.5.9 invariant 4;
    does NOT condition on `WriteResult` variant.
    """
    outcome_canonical_bytes = _canonicalize_outcome_bytes(post_override_step_config)
    outcome_hash_hex = hashlib.sha256(outcome_canonical_bytes).hexdigest()
    idempotency_key = _override_idempotency_key(
        workflow_id, step_id, override_id, policy_id, outcome_hash_hex
    )
    payload = EntryPayload(
        action_id=Identifier(_OVERRIDE_ACTION_ID),
        idempotency_key=Identifier(idempotency_key),
        actor=Actor(actor_class=ActorClass.AGENT, actor_id=str(actor)),
        timestamp=datetime.now(UTC),
    )
    return await ledger_writer(payload)
