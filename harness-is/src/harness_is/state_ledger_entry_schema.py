"""State-ledger entry shape schema — U-IS-07.

Implements C-IS-05 §5 (the F2 six-field state-ledger entry shape). Declares
`StateLedgerEntry` — the harness-canonical join key against which every
downstream axis composes (engine event history, audit ledger, sandbox-violation
events, span emission all join on `idempotency_key` per ADD §2.2).

The six F-layer fields `(action_id, idempotency_key, actor, response_hash,
timestamp, prior_event_hash)` are immutable; per-workload-class extension
records subclass `StateLedgerEntry`, inheriting the six fields and adding their
own (acceptance #5).

`Identifier` and `Timestamp` are abstract bindings — C-IS-05 §5 defers the
concrete identifier format and timestamp encoding to implementation discretion.
`Identifier` is an opaque `str`-newtype (any UUID / ULID string binds);
`Timestamp` binds to `datetime` (a wall-clock time-instant; monotonic-ordering
discipline per §5 is a write-path concern, not a schema concern).

Authority: Implementation_Plan_Information_Substrate_v2_3.md §2.1 U-IS-07
(preserved verbatim from v2.1 §2); Spec_Information_Substrate_v1.md §5 C-IS-05;
ADR-F2 v1.2 §Decision (state-ledger entry shape).
"""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import StrEnum
from typing import Annotated, Literal, NewType

from pydantic import BaseModel, ConfigDict, Field, field_validator

Identifier = NewType("Identifier", str)
"""Opaque identifier — concrete format (UUID v4 / ULID / …) deferred per §5."""

Timestamp = datetime
"""Wall-clock time-instant — the entry write-time (C-IS-05 §5)."""

Bytes32 = Annotated[bytes, Field(min_length=32, max_length=32)]
"""A fixed-length 32-byte sequence — a SHA-256 digest (C-IS-05 §5 / C-IS-06)."""

ALL_ZEROS_SENTINEL: Bytes32 = b"\x00" * 32
"""Chain-inception `prior_event_hash` sentinel — 32 zero bytes (C-IS-05 §5)."""


def reject_noncanonical_rotation_correlation_id(value: str | None) -> str | None:
    """Canonical-round-trip UUID check for `rotation_correlation_id` (C-IS-05 §5.6).

    `None` passes through unchanged (the default — every entry outside a
    rotation window). A non-`None` value MUST be the canonical 36-char
    hyphenated UUID string form: `str(uuid.UUID(value)) == value`. Bare
    `uuid.UUID`-parseability is INSUFFICIENT — it also accepts 32-char
    unhyphenated hex, brace-wrapped (`{...}`), and `urn:uuid:`-prefixed forms,
    none of which is the canonical form the field table requires; each is
    rejected here even though `uuid.UUID` parses it successfully.

    Shared by `StateLedgerEntry` and `EntryPayload` (state_ledger_write.py) —
    the same construction-time check applies to both carriers.
    """
    if value is None:
        return None
    try:
        parsed = uuid.UUID(value)
    except ValueError as exc:
        raise ValueError(
            f"rotation_correlation_id={value!r} is not a canonical UUID string"
        ) from exc
    if str(parsed) != value:
        raise ValueError(
            f"rotation_correlation_id={value!r} is not the canonical 36-char "
            "hyphenated UUID form (parseable but non-canonical spelling rejected)"
        )
    return value


class ActorClass(StrEnum):
    """The 3 actor classes of a state-ledger entry (C-IS-05 §5)."""

    AGENT = "agent"
    SUB_AGENT = "sub_agent"
    OPERATOR = "operator"


class Actor(BaseModel):
    """The actor responsible for the action a state-ledger entry records."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    actor_class: ActorClass
    actor_id: str


class BranchMetadata(BaseModel):
    """Fan-out branch causality + per-branch terminal disposition (C-IS-05 §5.4).

    The v1.8 D-derivative sidecar record the CP non-linear-topology
    `WorkflowDriver` composes (Route Y) and the IS state ledger persists. A
    three-field record carrying which fan-out branch an entry belongs to
    (`parent_action_id` + `branch_index`, which jointly identify a branch even
    under nested fan-out per §5.4) and the branch's **dispatch-boundary**
    terminal disposition (`terminal_status`).

    `terminal_status` is dispatch-boundary disposition, **not** step-outcome
    (§5.4): a branch whose in-flight step ran-and-errored is `completed` — its
    step failure is recorded at that step's own ordinary entry. The value set
    therefore carries no `failed`. `None` on a branch's non-terminal step
    entries; exactly one of the three values at the branch's terminal entry
    (the value-set + per-value semantics are CP-producer-owned per CP spec
    v1.32 §25.15.2 obligation 4).

    **Carrier home.** Co-located here with `StateLedgerEntry` (the `harness-is`
    reading of the §5.4 `harness-core`-vs-`harness-is` impl-discretion): it
    reuses the same `Identifier` and travels the §10.1 entry-shape export with
    no new cross-package dependency. The §5.4 hard constraint — NOT
    `harness-cp` (IS 0-outbound) — is honored: CP consumes this from IS via the
    established CP→IS direction.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    parent_action_id: Identifier
    branch_index: Annotated[int, Field(ge=0)]
    terminal_status: Literal["cancelled", "completed", "timed_out"] | None = None


class StateLedgerEntry(BaseModel):
    """The F2 six-field state-ledger entry shape (C-IS-05 §5).

    The six fields are the F-layer — immutable. Per-workload-class extension
    records subclass `StateLedgerEntry`: they inherit all six F-layer fields
    (a subclass cannot rename or omit them) and MAY add fields (acceptance #5).
    `frozen` → instances are immutable; the schema is statically validatable.

    v1.3 NEW D-derivative sidecar field — `procedural_tier_snapshot_ref` per
    C-IS-05 §5.1 (NEW). Carries the content-hash digest identifying which
    procedural-tier snapshot was in scope at the entry's write-time. Optional;
    default `None` permitted at entries written outside an active workflow
    context (bootstrap-stage entries; operator-explicit administrative entries).
    The F-layer six-field shape PRESERVED VERBATIM above; sidecar is additive
    at the D-derivative extension layer authorized by §5 "Field-shape
    extensibility commitment."

    v1.8 NEW D-derivative sidecar field — `branch_metadata` per C-IS-05 §5.4
    (NEW). Carries fan-out branch causality + per-branch terminal disposition
    the CP non-linear-topology `WorkflowDriver` composes (Route Y). Optional;
    `None` at every entry written outside a fan-out branch (the
    `SINGLE_THREADED_LINEAR` path, bootstrap-stage entries, non-branch steps —
    every pre-v1.8 entry). Additive at the same D-derivative extension layer as
    the §5.1 sidecar; the six-field shape stays inviolate.

    v1.12 NEW D-derivative sidecar field — `rotation_correlation_id` per
    C-IS-05 §5.6 (NEW). Carries the rotation-event correlation identity a
    CP-side audit-walk verifier requires and joins to prove a genuine
    key-rotation boundary occurred (C-CP-20). Optional; `None` at every entry
    outside a rotation window (every pre-v1.12 entry). A non-`None` value MUST
    be a canonical-form UUID string — rejected at construction otherwise (see
    `reject_noncanonical_rotation_correlation_id`). Additive at the same
    D-derivative extension layer as the §5.1/§5.4 sidecars; the six-field
    shape stays inviolate.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    action_id: Identifier
    idempotency_key: Identifier
    actor: Actor
    response_hash: Bytes32
    timestamp: Timestamp
    prior_event_hash: Bytes32
    # v1.3 NEW D-derivative sidecar (C-IS-05 §5.1).
    procedural_tier_snapshot_ref: Identifier | None = None
    # v1.8 NEW D-derivative sidecar (C-IS-05 §5.4).
    branch_metadata: BranchMetadata | None = None
    # v1.12 NEW D-derivative sidecar (C-IS-05 §5.6).
    rotation_correlation_id: str | None = None

    @field_validator("rotation_correlation_id")
    @classmethod
    def _validate_rotation_correlation_id(cls, value: str | None) -> str | None:
        return reject_noncanonical_rotation_correlation_id(value)
