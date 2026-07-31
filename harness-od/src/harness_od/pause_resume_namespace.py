"""C-OD-30 `pause.*` + `resume.*` canonical namespace schema + PauseResumeAuditPayload.

U-OD-51 — Sub-arc A landing of `[[fork-u-cp-72-cost-and-pause-resume-prefix-gap]]`
3-arc cascade per fork §2.1 routing target (a). Declares the 8-attribute
`pause.*` + `resume.*` span namespace canonical authority for the
`PauseResumeProtocol` emitter homed at CP (per the D6 ingestion pattern:
CP emits, OD ratifies). Also declares the `PauseResumeAuditPayload`
field-set used by the `cp_audit_to_od_audit` converter at
`harness-cxa/src/harness_cxa/cp_audit_conversion.py` when the converter
encounters a `pause:`- or `resume:`-prefixed CP action_id (per CXA v2.8
§2.3.7 row 6 + U-CP-72 AC #1 discriminator-table 8-prefix coverage).

**8 attributes across 2 span sites** per OD spec v1.9 §C-OD-30.1:

| Site                | Attribute count |
|---------------------|-----------------|
| `pause.captured`    | 4               |
| `resume.attempted`  | 4               |

**Pattern-P1 alignment** with CP spec v1.11 §26.4 producer-side: attribute
names byte-exact match the §26.4 span emission table; consumers MAY
disambiguate `WorkflowPauseReason` values via `pause.reason` (5-class
taxonomy: hitl_defer / validator_escalate / engine_pause / operator_pause /
material_diff_arbitrate) and `MaterialDiffPolicy` via `resume.diff_policy`
(3-class: STRICT / LENIENT / OPERATOR_ARBITRATE) per CP spec v1.11 §26.2.

**Audit-ledger projection** per §C-OD-30.2: when a `pause.captured` or
`resume.attempted` span fires, the converter writes a `PauseResumeAuditPayload`
via `pause:` or `resume:` action_id prefix per CXA v2.8 §2.3.7 row 6 +
U-CP-72 expansion (8 prefixes). The payload extends per C-OD-24.6 CP-sourced
sub-namespace discipline (`audit.cp.*` tagging) — the 4 `audit_cp_*` fields
are the common CP-sourced field-set shared with Validator / MCP-trust /
HITL-webhook / operator-burden audit payloads at §29.2 / §31.2 / §32.2 /
§33.2. The 8 specific fields include `diff_summary_hash` (audit-only; not in
§30.1 span schema) per the pause/resume diff-arbitration discipline at CP
spec v1.11 §26.3.

**Sampling discipline.** `pause.captured` head=1.0 (always-sampled —
operator-explicit pause is audit-critical). `resume.attempted` head=1.0.
Per §C-OD-30.3.

**Path-conditional field population.** Per §C-OD-30.2 comment-line discipline:

| Path  | Always populated                              | Optional fields                                                            |
|-------|-----------------------------------------------|----------------------------------------------------------------------------|
| pause | `snapshot_hash`, `step_index`                 | `pause_reason`, `state_ledger_anchor`                                      |
| resume| `snapshot_hash`, `step_index`                 | `diff_detected`, `diff_policy`, `diff_summary_hash`, `resume_outcome`     |

Note: `snapshot_hash` + `step_index` are always-populated common-fields shared
by both paths per §C-OD-30.2 spec sample-code (both paths construct the same
payload class; path-specific fields populated as `Optional` Pydantic fields).

Authority: OD spec v1.9 §C-OD-30 (v1.8 NEW; v1.9 absorbs `PauseReason` →
`WorkflowPauseReason` identifier rename at attribute type cite); plan unit
U-OD-51 (OD plan v2.16, formerly v2.15 cross-axis-blocked on U-CP-62).
Sub-arc A landing arc per `[[fork-u-cp-72-cost-and-pause-resume-prefix-gap]]`
§2.1 routing target (a) — U-CP-62 landed at `49617e7` 2026-05-22.
"""

from __future__ import annotations

from collections.abc import Mapping
from enum import StrEnum
from typing import Final

from harness_core import AttributeValueType, Cardinality
from harness_cp.pause_resume_protocol import (
    PauseEvent,
    ResumeAttempt,
    ResumeOutcome,
    ResumeOutcomeKind,
)
from pydantic import BaseModel, ConfigDict, model_validator

# ----------------------------------------------------------------------------
# Span-site identifiers (2 sites per §C-OD-30.1)
# ----------------------------------------------------------------------------

SPAN_SITE_PAUSE_CAPTURED: Final[str] = "pause.captured"
SPAN_SITE_RESUME_ATTEMPTED: Final[str] = "resume.attempted"


# ----------------------------------------------------------------------------
# AttributeSpec carrier (mirrors U-OD-50 + U-OD-52 namespace-module shape)
# ----------------------------------------------------------------------------


class AttributeSpec(BaseModel):
    """One canonical-namespace span attribute declaration.

    Pattern-P1 alignment carrier — consumers verify byte-exact attribute name
    + value type + cardinality + span site against the OD canonical schema.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    attribute_name: str
    """Byte-exact attribute name per §C-OD-30.1 + Pattern-P1 alignment with
    CP spec v1.11 §26.4 producer site."""

    value_type: AttributeValueType
    """Value-type discriminator per `harness_core.AttributeValueType`."""

    cardinality: Cardinality
    """Cardinality classification per `harness_core.Cardinality`."""

    span_site: str
    """One of the 2 span-site constants (`SPAN_SITE_PAUSE_CAPTURED` or
    `SPAN_SITE_RESUME_ATTEMPTED`)."""


# ----------------------------------------------------------------------------
# 8-attribute canonical schema (§C-OD-30.1 verbatim)
# ----------------------------------------------------------------------------


PAUSE_RESUME_SPAN_NAMESPACE_SCHEMA: Mapping[str, AttributeSpec] = {
    # --- pause.captured site (4 attrs) ---
    "pause.reason": AttributeSpec(
        attribute_name="pause.reason",
        value_type=AttributeValueType.ENUM_REF,
        cardinality=Cardinality.LOW,
        span_site=SPAN_SITE_PAUSE_CAPTURED,
    ),
    "pause.snapshot_hash": AttributeSpec(
        attribute_name="pause.snapshot_hash",
        value_type=AttributeValueType.STRING,
        cardinality=Cardinality.HIGH,
        span_site=SPAN_SITE_PAUSE_CAPTURED,
    ),
    "pause.step_index": AttributeSpec(
        attribute_name="pause.step_index",
        value_type=AttributeValueType.INT,
        cardinality=Cardinality.HIGH,
        span_site=SPAN_SITE_PAUSE_CAPTURED,
    ),
    "pause.state_ledger_anchor": AttributeSpec(
        attribute_name="pause.state_ledger_anchor",
        value_type=AttributeValueType.STRING,
        cardinality=Cardinality.HIGH,
        span_site=SPAN_SITE_PAUSE_CAPTURED,
    ),
    # --- resume.attempted site (4 attrs) ---
    "resume.snapshot_hash": AttributeSpec(
        attribute_name="resume.snapshot_hash",
        value_type=AttributeValueType.STRING,
        cardinality=Cardinality.HIGH,
        span_site=SPAN_SITE_RESUME_ATTEMPTED,
    ),
    "resume.diff_detected": AttributeSpec(
        attribute_name="resume.diff_detected",
        value_type=AttributeValueType.BOOL,
        cardinality=Cardinality.LOW,
        span_site=SPAN_SITE_RESUME_ATTEMPTED,
    ),
    "resume.diff_policy": AttributeSpec(
        attribute_name="resume.diff_policy",
        value_type=AttributeValueType.ENUM_REF,
        cardinality=Cardinality.LOW,
        span_site=SPAN_SITE_RESUME_ATTEMPTED,
    ),
    "resume.outcome": AttributeSpec(
        attribute_name="resume.outcome",
        value_type=AttributeValueType.ENUM_REF,
        cardinality=Cardinality.LOW,
        span_site=SPAN_SITE_RESUME_ATTEMPTED,
    ),
}
"""The 8 `pause.*` + `resume.*` span attributes per §C-OD-30.1 verbatim.

Keyed by attribute name for O(1) Pattern-P1 alignment lookup at the
`cp_audit_to_od_audit` converter + at consumer-side downstream filtering.
"""


# ----------------------------------------------------------------------------
# PauseResumeAuditPayload (§C-OD-30.2 audit-ledger projection)
# ----------------------------------------------------------------------------


class PauseResumeAuditPayload(BaseModel):
    """Audit-ledger projection emitted on `pause.captured` OR `resume.attempted`
    span fires (§C-OD-30.2).

    Written by `cp_audit_to_od_audit` converter at
    `harness-cxa/src/harness_cxa/cp_audit_conversion.py` via `pause:` or
    `resume:` action_id prefix per CXA v2.8 §2.3.7 row 6 + U-CP-72 expansion
    (8 prefixes — Sub-arc A un-STRIKE per `[[fork-u-cp-72-cost-and-pause-
    resume-prefix-gap]]` §3 partial-land table re-binding criteria).

    Extends the C-OD-24.6 CP-sourced sub-namespace discipline: the 4
    `audit_cp_*` fields are the common CP-sourced field-set; the 8 trailing
    fields are pause/resume-specific. At serialization the payload composes
    into `AuditPayload.audit_namespace_attrs` as `audit.cp.*` +
    `audit.pause_resume.*` sub-namespace keys.

    Note: per the U-OD-50 `ValidatorEscalationAuditPayload` + U-OD-52
    `TrustEvaluationAuditPayload` precedent, this class is a STANDALONE
    projection container that the converter uses to compose
    `AuditPayload.audit_namespace_attrs` dict — literal Python
    `class Foo(AuditPayload)` inheritance is NOT what the spec requires; the
    §24.6 sub-namespace tagging discipline is what's preserved.

    **Path-conditional field population.** The same class serves both pause
    and resume paths; path-specific fields populated as Optional per the table
    at module docstring + §C-OD-30.2 sample-code. `snapshot_hash` and
    `step_index` are always-populated common-fields across both paths.

    **`pause_reason` enum-value semantics.** Per OD spec v1.9 §C-OD-30.2 +
    v1.9 change-note: declared as `str | None` (enum value serialized as
    string at the audit-ledger row) — type annotation is `str | None`, not
    the enum class identifier. Comment-line cite preserved as canonical-by-
    prose ("WorkflowPauseReason enum value (pause path)") per v1.9 path γ
    absorption — the enum-value semantics (5 string values) are unchanged
    from v1.8's pre-rename PauseReason identifier.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    # CP-sourced inherited per §C-OD-24.6 sub-namespace discipline:
    audit_cp_action_id: str
    """f"pause:{workflow_id}:{step_index}" OR f"resume:{workflow_id}:{step_index}"
    per §C-OD-30.2 + CXA v2.8 §2.3.7 + U-CP-72 expansion."""

    audit_cp_response: str
    """`"paused"` | `"resumed"` | `"diff_detected"` per §C-OD-30.2."""

    audit_cp_timestamp: str
    """ISO-8601 OR "" at MVP per v1.7 §24.4 NOTE 8a-iii."""

    audit_cp_prior_event_hash: str
    """SHA-256 hex (64) OR "0"*64 at MVP."""

    # Pause/resume-specific fields per §C-OD-30.2 (always-populated):
    snapshot_hash: str
    """SHA-256 hex (64) snapshot identifier. Always populated on BOTH paths
    (pause emits the snapshot of paused state; resume references the prior
    snapshot being resumed from). Pattern-P1 byte-exact alignment with
    producer-side `pause.snapshot_hash` and `resume.snapshot_hash` span
    attrs at CP spec v1.11 §26.4."""

    step_index: int
    """Workflow step index at pause/resume event. Always populated on BOTH
    paths."""

    # Pause-path-specific fields (Optional — populated on pause path only):
    pause_reason: str | None
    """WorkflowPauseReason enum value (pause path) per CP spec v1.11 §26.2
    5-class taxonomy: `hitl_defer` / `validator_escalate` / `engine_pause` /
    `operator_pause` / `material_diff_arbitrate`. Serialized as string at the
    audit-ledger row — type annotation `str | None` not the enum class
    identifier per OD spec v1.9 §C-OD-30.2 explicit preservation."""

    state_ledger_anchor: str | None
    """`entry_hash` reference to the state-ledger entry at the pause boundary
    (pause path only). Anchors the pause-point in the F2-substrate per
    C-IS-06 §6 entry-hash discipline."""

    # Resume-path-specific fields (Optional — populated on resume path only):
    diff_detected: bool | None
    """Whether a material-diff was detected at resume-attempt (resume path
    only). True triggers diff-policy branching per `diff_policy`."""

    diff_policy: str | None
    """MaterialDiffPolicy enum value (resume path only) per CP spec v1.11
    §26.2 3-class: `STRICT` / `LENIENT` / `OPERATOR_ARBITRATE`. Serialized
    as string at the audit-ledger row."""

    diff_summary_hash: str | None
    """SHA-256 hex (64) summary-hash of the detected material-diff (resume
    path only). Audit-only field — NOT in §C-OD-30.1 span schema; populated
    at AuditPayload row when `diff_detected=True`. Per CP spec v1.11 §26.3
    diff-arbitration discipline."""

    resume_outcome: str | None
    """resume.outcome enum value (resume path only): `resumed` /
    `diff_aborted` / `arbitration_owed`. Serialized as string at the audit-
    ledger row per §C-OD-30.1 row 8 attribute type."""


# ----------------------------------------------------------------------------
# Canonical production-invocation helpers (§C-OD-30.4 — NEW at OD spec v1.11)
# ----------------------------------------------------------------------------
#
# Per `[[fork-u-cp-72-cost-and-pause-resume-prefix-gap]]` §9 + OD spec v1.11
# §C-OD-30.4 + OD plan v2.18 U-OD-51 ACs #6 + #7 + #8 + #10.
#
# Two module-level helpers project PauseEvent / (ResumeAttempt, ResumeOutcome)
# carriers from harness-cp into PauseResumeAuditPayload instances ready for the
# `cp_audit_to_od_audit` converter (already operational at
# `harness-cxa/src/harness_cxa/cp_audit_conversion.py:289-299` per Sub-arc A).
#
# Narrow-scope framing: no production callsite exists at the harness today —
# capture_pause_snapshot + attempt_resume at harness-cp/.../pause_resume_protocol.py
# are NotImplementedError stubs; workflow_driver.py does not invoke
# PauseResumeProtocol. These helpers land as a library surface ready for the
# CP composer authoring arc (gates H_T-CP-22 PARTIAL → RETIRE-READY per
# harness-cp/CLAUDE.md §4.1). Helpers are DEAD CODE at landing.


def _project_pause_event_to_audit_payload(
    event: PauseEvent,
    *,
    workflow_id: str,
    step_index: int,
    snapshot_hash: str,
    state_ledger_anchor: str,
    prior_event_hash: str,
    timestamp: str = "",
) -> PauseResumeAuditPayload:
    """Project a `PauseEvent` into a `PauseResumeAuditPayload` per §C-OD-30.4.

    Per OD spec v1.11 §C-OD-30.4.1 step 2: sets `audit_cp_action_id` to
    `f"pause:{workflow_id}:{step_index}"` per the canonical CXA v2.9 §0.3
    8-prefix discriminator table entry. Per §C-OD-30.4.1 step 3: hard-codes
    `audit_cp_response` to `"paused"` per the §C-OD-30.2 comment-line
    discipline. Per §C-OD-30.4.1 step 8: nulls resume-path fields
    (`diff_detected`, `diff_policy`, `diff_summary_hash`, `resume_outcome`).

    Composition discipline (per §C-OD-30.4 helper-signature rationale):

    - `workflow_id` kwarg required (PauseEvent does not carry it).
    - `step_index` kwarg required (carried at audit payload + appears in
      action_id pattern).
    - `snapshot_hash` external — composition site computes from the snapshot
      serialization per §22.1 acceptance #9 implementer-discretion.
    - `state_ledger_anchor` external — composition site supplies the F2
      state-ledger `entry_hash` written at pause boundary.
    - `prior_event_hash` + `timestamp` external — step-context-derived sentinel
      values (`"0" * 64` zero-hash; `""` empty-string) caller-set per sibling-
      subclass convention.

    The `event.pause_reason` (a `PauseReason` StrEnum at
    harness_cp/pause_resume_protocol.py) is serialized to its string value per
    §C-OD-30.2 `pause_reason: str | None` field typing (enum-value serialized
    at the audit-ledger row, not enum class identifier).

    Args:
        event: The CP-side `PauseEvent` captured at the pause boundary.
        workflow_id: The workflow's identifier (composition-site-supplied).
        step_index: The step index at the pause event.
        snapshot_hash: SHA-256 hex of the snapshot at pause boundary.
        state_ledger_anchor: `entry_hash` of the F2 state-ledger entry written
            at pause boundary (composition-site-supplied).
        prior_event_hash: SHA-256 hex (64) of prior CP event hash, or
            `"0" * 64` sentinel.
        timestamp: ISO-8601 UTC timestamp, or `""` MVP sentinel.

    Returns:
        A frozen `PauseResumeAuditPayload` ready for the
        `cp_audit_to_od_audit` converter via the `pause:` prefix branch.
    """
    return PauseResumeAuditPayload(
        # CP-sourced common fields per §C-OD-24.6:
        audit_cp_action_id=f"pause:{workflow_id}:{step_index}",
        audit_cp_response="paused",
        audit_cp_timestamp=timestamp,
        audit_cp_prior_event_hash=prior_event_hash,
        # Always-populated common fields per §C-OD-30.2:
        snapshot_hash=snapshot_hash,
        step_index=step_index,
        # Pause-path-specific fields (populated):
        pause_reason=event.pause_reason.value,
        state_ledger_anchor=state_ledger_anchor,
        # Resume-path-specific fields (nulled per §C-OD-30.4.1 step 8):
        diff_detected=None,
        diff_policy=None,
        diff_summary_hash=None,
        resume_outcome=None,
    )


def _project_resume_outcome_to_audit_payload(
    attempt: ResumeAttempt,
    outcome: ResumeOutcome,
    *,
    step_index: int,
    snapshot_hash: str,
    diff_summary_hash: str | None,
    prior_event_hash: str,
    timestamp: str = "",
) -> PauseResumeAuditPayload:
    """Project a `(ResumeAttempt, ResumeOutcome)` pair into a
    `PauseResumeAuditPayload` per §C-OD-30.4.

    Per OD spec v1.11 §C-OD-30.4.1 step 2: sets `audit_cp_action_id` to
    `f"resume:{attempt.paused_workflow_id}:{step_index}"` — workflow_id
    extracted from the carrier per §C-OD-30.4 helper-signature rationale.

    Per §C-OD-30.4.1 step 3: selects `audit_cp_response` per `outcome.outcome_kind`:
    - `RESUME_CLEAN` → `"resumed"`
    - `RESUME_AFTER_REVALIDATION` → `"resumed"` (revalidation succeeded)
    - `ABORT_REVALIDATION_FAILED` → `"diff_detected"` (material diff blocked)
    - `ABORT_SNAPSHOT_CORRUPTED` → `"diff_detected"` (integrity failure)

    Per §C-OD-30.4.1 step 8: nulls pause-path fields (`pause_reason`,
    `state_ledger_anchor`).

    Per §C-OD-30.4.1 step 9: `diff_policy` inlined as `None` for `RESUME_CLEAN`
    outcomes; for non-clean outcomes the helper sets the active policy enum
    value per implementer discretion. v1.11 takes the simplest path: emit the
    outcome_kind's value as a stand-in for the diff_policy until the composer
    arc surfaces the actual policy as input (per §C-OD-30.4.5 deferred
    discretion). Future arc MAY widen the signature to accept `diff_policy`
    as an explicit kwarg.

    Args:
        attempt: The CP-side `ResumeAttempt` consumed at the resume boundary.
        outcome: The CP-side `ResumeOutcome` produced by `attempt_resume`.
        step_index: The step index at the resume event.
        snapshot_hash: SHA-256 hex of the prior snapshot being resumed from.
        diff_summary_hash: SHA-256 hex of the material-diff summary if
            `outcome.outcome_kind != RESUME_CLEAN`; `None` for `RESUME_CLEAN`.
        prior_event_hash: SHA-256 hex (64) of prior CP event hash, or
            `"0" * 64` sentinel.
        timestamp: ISO-8601 UTC timestamp, or `""` MVP sentinel.

    Returns:
        A frozen `PauseResumeAuditPayload` ready for the
        `cp_audit_to_od_audit` converter via the `resume:` prefix branch.
    """
    # Per §C-OD-30.4.1 step 3 outcome-kind switch:
    if outcome.outcome_kind in (
        ResumeOutcomeKind.RESUME_CLEAN,
        ResumeOutcomeKind.RESUME_AFTER_REVALIDATION,
    ):
        response = "resumed"
    else:
        # ABORT_REVALIDATION_FAILED + ABORT_SNAPSHOT_CORRUPTED both surface as
        # diff_detected per §C-OD-30.4.1 step 3 (integrity-failure → audit row
        # marks diff_detected per §C-OD-30.2 comment).
        response = "diff_detected"

    diff_detected = outcome.outcome_kind != ResumeOutcomeKind.RESUME_CLEAN

    # Per §C-OD-30.4.1 step 9: diff_policy inlined None for RESUME_CLEAN;
    # outcome_kind value as stand-in for non-clean (implementer-discretion
    # per §C-OD-30.4.5 deferred discretion until composer arc surfaces the
    # actual policy as input).
    if outcome.outcome_kind == ResumeOutcomeKind.RESUME_CLEAN:
        diff_policy: str | None = None
    else:
        diff_policy = outcome.outcome_kind.value

    return PauseResumeAuditPayload(
        # CP-sourced common fields per §C-OD-24.6:
        audit_cp_action_id=f"resume:{attempt.paused_workflow_id}:{step_index}",
        audit_cp_response=response,
        audit_cp_timestamp=timestamp,
        audit_cp_prior_event_hash=prior_event_hash,
        # Always-populated common fields per §C-OD-30.2:
        snapshot_hash=snapshot_hash,
        step_index=step_index,
        # Pause-path-specific fields (nulled per §C-OD-30.4.1 step 8):
        pause_reason=None,
        state_ledger_anchor=None,
        # Resume-path-specific fields (populated):
        diff_detected=diff_detected,
        diff_policy=diff_policy,
        diff_summary_hash=diff_summary_hash,
        resume_outcome=outcome.outcome_kind.value,
    )


# ----------------------------------------------------------------------------
# §C-OD-30.5 (NEW at OD spec v1.36) — the B-69 durable-pause-state read + the
# staleness-refused resume. A SIBLING payload type, per §30.5.2 option (b).
# ----------------------------------------------------------------------------

PAUSE_STATE_EVENT_HEAD_SAMPLING_RATE: Final[float] = 1.0
"""Head sampling rate for BOTH §C-OD-30.5 event kinds (OD spec v1.36 §30.5.4).

DECLARED, not inherited: C-OD-30's existing sampling discipline names only the
two event kinds it already carries, so "inherit the existing convention" would
have left these REQUIRED emissions with no rule at all. Both take the SAME rate
the existing pause/resume event kinds take, because §30.5.3's pairing requirement
is only sound if BOTH members of a pair are retained — independent sampling would
break causal-pair reconstruction at exactly the rate it drops either one.
"""


class PauseStateCauseAttribution(StrEnum):
    """The FIVE stable identifiers a failed §14.14.9 read reports (Runtime v1.107 §30).

    Declared here so the audit row's `cause_attribution` carries a CLOSED domain
    rather than an inherited `str`. `harness-od` must not import `harness-runtime`
    (the axis direction runs the other way), so the vocabulary is re-declared, not
    re-derived — and any divergence from the Runtime-side enum fails the
    cross-surface identity witness the §30 contract term requires.

    Cause class ONLY — never exception text, never a resolved filesystem path.
    """

    ABSENT = "absent"
    EMPTY_JOURNAL = "empty-journal"
    READ_ERROR = "read-error"
    CORRUPT_LATEST = "corrupt-latest"
    WORKFLOW_MISMATCH = "workflow-mismatch"


class PauseStateEventKind(StrEnum):
    """The TWO NEW event kinds within the EXISTING C-OD-30 namespace family."""

    ACCESSOR_READ = "pause.state.read"
    """Every invocation of the Runtime §14.14.9 durable-pause-state read accessor,
    whether it succeeds or fails (OD spec v1.36 §30.5.1)."""

    STALENESS_REFUSED_RESUME = "resume.refused.pause_state_stale"
    """A `resume()` refused on the Runtime v1.107 §30 staleness precondition —
    raised PRE-BOOTSTRAP, so it rides this sibling payload rather than the
    `(ResumeAttempt, ResumeOutcome)`-composed `PauseResumeAuditPayload`
    (OD spec v1.36 §30.5.2)."""


class PauseStateAuditPayload(BaseModel):
    """§C-OD-30.5 sibling payload for the B-69 read + staleness-refusal events.

    **Why a SIBLING type and not an additive field on `PauseResumeAuditPayload`.**
    OD spec v1.36 §30.5.2 authorizes either; option (b) is taken here because
    `PauseResumeAuditPayload` is `frozen` + `extra="forbid"` and is constructed at
    every existing pause/resume site — widening it would put a
    never-populated-on-those-paths field on every already-shipped row, whereas a
    sibling leaves the existing field set and BOTH existing §C-OD-30.4 helpers
    **PRESERVED VERBATIM** and the existing converter branch unchanged for every
    event it already handles.

    **Content is SPLIT BY OUTCOME**, because §14.14.9.4's fail-closed rule means a
    failed read mints no token and returns no projection, so a single conflated
    content rule would be unimplementable:

    | Event | token | per-variant counts | cause |
    |---|---|---|---|
    | read, succeeded | REQUIRED | REQUIRED (four) | absent |
    | read, failed | absent | absent | REQUIRED |
    | staleness-refused resume | REQUIRED | absent | absent |

    The split is ENFORCED here rather than documented — an illegal combination is
    rejected at construction.

    **Disclosure limits (§30.5.1), each closing a specific hazard.** NEVER the
    locations' associated payload; NEVER the never-keyable pre-dispatch or
    depth-0-root internal identity (emit presence + classification, which the
    per-variant counts carry exactly, never identity); the cause attribution names
    the CAUSE CLASS ONLY — never exception text, never a resolved filesystem path.
    No field on this payload can carry any of them: they are absent by type.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    event_kind: PauseStateEventKind
    """Which of the two §C-OD-30.5 event kinds this row records."""

    workflow_id: str
    """The read's only key (§30.5.1)."""

    succeeded: bool
    """Whether the read produced a projection. Always `False` for a
    staleness-refused resume (nothing succeeded on that path)."""

    staleness_token: str | None = None
    """The pairing key (§30.5.3) — the token minted by a SUCCESSFUL read, and the
    SAME value re-emitted by the resume that refuses on it, so the two are
    reconstructable as ONE causal pair from telemetry alone. `None` on a failed
    read, where no token exists by construction."""

    cause_attribution: PauseStateCauseAttribution | None = None
    """One of the FIVE stable identifiers Runtime v1.107 §30 declares — on an
    UNSUCCESSFUL read only. Cause class ONLY.

    The domain is DECLARED here rather than inherited as `str`: a free `str` would
    persist an unrouteable row (`cause_attribution="typo"`) that satisfies the
    closed-schema posture in form while defeating the routing decision the whole
    refinement exists to enable. *(Out-of-family review [P2] at the impl leg.)*
    The vocabulary is re-declared rather than imported because `harness-od` must
    not depend on `harness-runtime` (the axis direction runs the other way); the
    five values are byte-identical to the Runtime-side enum, and a divergence
    would fail the cross-surface identity witness."""

    hitl_addressable_count: int | None = None
    effect_fence_addressable_count: int | None = None
    uniform_fallback_only_count: int | None = None
    transitively_paused_count: int | None = None
    """PER-VARIANT counts of returned locations — FOUR counts, never one aggregate
    total (§30.5.1): a single scalar cannot express classification, while the
    disclosure limit requires classification WITHOUT identity. Populated on a
    successful read only."""

    @model_validator(mode="after")
    def _enforce_outcome_split(self) -> PauseStateAuditPayload:
        """Reject the field combinations §30.5.1's outcome split forbids."""
        counts = (
            self.hitl_addressable_count,
            self.effect_fence_addressable_count,
            self.uniform_fallback_only_count,
            self.transitively_paused_count,
        )
        if self.event_kind is PauseStateEventKind.STALENESS_REFUSED_RESUME:
            if self.succeeded:
                raise ValueError("a staleness-refused resume never succeeded")
            if self.staleness_token is None:
                raise ValueError(
                    "a staleness-refused resume MUST carry the supplied staleness "
                    "token — it is §30.5.3's pairing key"
                )
            if self.cause_attribution is not None or any(c is not None for c in counts):
                raise ValueError(
                    "a staleness-refused resume carries neither a cause attribution "
                    "nor location counts"
                )
            return self
        if self.succeeded:
            if self.staleness_token is None:
                raise ValueError("a successful read MUST carry the token it minted")
            if self.cause_attribution is not None:
                raise ValueError("a successful read carries no cause attribution")
            if any(c is None for c in counts):
                raise ValueError(
                    "a successful read MUST carry all FOUR per-variant counts; a "
                    "single aggregate total cannot express classification"
                )
            return self
        if self.cause_attribution is None:
            raise ValueError("a failed read MUST carry its cause attribution")
        if self.staleness_token is not None or any(c is not None for c in counts):
            raise ValueError(
                "a failed read mints no token and returns no projection, so it "
                "carries neither a token nor location counts"
            )
        return self


__all__ = [  # noqa: RUF022 — grouped public-symbols-then-helpers with an
    # explanatory comment block between the groups; alphabetic re-sort would
    # destroy the documented two-group structure.
    "AttributeSpec",
    "PAUSE_RESUME_SPAN_NAMESPACE_SCHEMA",
    "PAUSE_STATE_EVENT_HEAD_SAMPLING_RATE",
    "PauseResumeAuditPayload",
    "PauseStateAuditPayload",
    "PauseStateCauseAttribution",
    "PauseStateEventKind",
    "SPAN_SITE_PAUSE_CAPTURED",
    "SPAN_SITE_RESUME_ATTEMPTED",
    # Production-invocation helpers (§C-OD-30.4 NEW at OD spec v1.11; dead code
    # at landing until CP composer authoring arc — gates H_T-CP-22 PARTIAL →
    # RETIRE-READY per harness-cp/CLAUDE.md §4.1). Underscore-prefixed names
    # mirror cost-axis sibling precedent at `cost_record_audit_writer.py` per
    # the AuditPayload-subclass canonical helper convention; explicitly
    # re-exported via __all__ to make the helper-only production-construction
    # discipline per §C-OD-30.4.1 step 1 explicit at the module boundary.
    "_project_pause_event_to_audit_payload",
    "_project_resume_outcome_to_audit_payload",
]
