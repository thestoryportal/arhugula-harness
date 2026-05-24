# Specification — Operational Discipline v1.11

## Change-note (v1.10 → v1.11)

**Scope of revision.** Pause/resume back-flow arc (narrow scope per operator AskUserQuestion 2026-05-24 — "Narrow — OD-side helper only") per `[[fork-u-cp-72-cost-and-pause-resume-prefix-gap]]` §9 residual routing target. NEW §C-OD-30.4 — `PauseResumeAuditPayload` canonical production-invocation contract authoring (helper signatures + canonical invocation pattern + invariants + deferred discretion). Mirrors the cost-axis Sub-arc B v1.10 §C-OD-26.1 amendment shape, scoped to pause/resume — the typed carrier `PauseResumeAuditPayload` is already authored at §C-OD-30.2 (v1.8 NEW, preserved verbatim through v1.10); the v1.11 amendment authors the canonical production-helper contract for constructing the carrier at production callsites.

**v1.10 substantive content preserved verbatim.** All v1.10 content (NEW §C-OD-26.6 CostRecordAuditPayload typed-carrier + §C-OD-26.1 invocation-signature amendment) preserved unchanged. All v1.9 content (v1.9 §C-OD-30.1 attribute-type-citation absorption preserving verbatim through v1.10) preserved. All v1.8 NEW C-OD-25 through C-OD-33 contracts preserved verbatim. The v1.7 + v1.6 + ... + v1 chain all preserved.

**Source of fix.** Pause/resume Sub-arc residual per `[[fork-u-cp-72-cost-and-pause-resume-prefix-gap]]` §9 (Sub-arc A FULLY-LANDED at `5d6051d` 2026-05-23; production-callsite migration deferred at fork doc §9 to operator-decision back-flow arc; arc opened 2026-05-24 per operator selection). Companion artifacts at this arc: OD plan v2.17 → v2.18 U-OD-51 AC re-decomposition absorbing the new production-helper contract (separately-authored per implementation-planner skill); impl arc materializing helper(s) at `harness-od/src/harness_od/pause_resume_namespace.py`.

**Narrow-scope framing (explicit).** The arc lands the OD-side production-invocation contract + helper. Under the operator-ratified narrow scope, **no production callsite exists** in the harness — `capture_pause_snapshot` + `attempt_resume` at `harness-cp/src/harness_cp/pause_resume_protocol.py:106-147` are `NotImplementedError` stubs, and `harness-cp/src/harness_cp/workflow_driver.py` does not invoke the `PauseResumeProtocol` (per `harness-cp/CLAUDE.md` §4.1 H_T-CP-22 PARTIAL gate). The helper authored at v1.11 § C-OD-30.4 lands as a contract + library surface ready for the CP composer authoring arc (separate scope; out of this arc; gates H_T-CP-22 PARTIAL → RETIRE-READY). This is the **structural asymmetry from cost-axis Sub-arc B**: cost-axis Sub-arc B widened an EXISTING production callsite (`cost_attribution_llm_dispatch.py:198-202`, operational since U-OD-38); pause/resume Sub-arc lands the helper without a callsite to migrate. The v1.11 contract authoring is honest about this gap and explicitly defers production-callsite construction per §C-OD-30.4.5.

**Amendment site.**

| Site | Amendment shape | Substrate source |
|---|---|---|
| **§C-OD-30.4 (NEW) PauseResumeAuditPayload canonical production-invocation contract** | NEW sub-section under existing C-OD-30 (`pause.*` + `resume.*` 8-attribute namespace), positioned after §C-OD-30.3 (Sampling discipline). Authors (i) the canonical production-invocation pattern routing through `cp_audit_to_od_audit` converter consuming `PauseResumeAuditPayload`; (ii) two helper signatures — `_project_pause_event_to_audit_payload` + `_project_resume_outcome_to_audit_payload`; (iii) per-payload composition discipline (action_id prefix pattern, prior_event_hash chain, audit_cp_response constant); (iv) invariants; (v) deferred-to-implementation-discretion items (production callsite construction; tracer/observer integration). | §C-OD-30.2 `PauseResumeAuditPayload` declaration (v1.8 NEW, preserved verbatim) + §C-OD-26.1 cost-axis Sub-arc B canonical-invocation pattern (parallel structure) + CXA v2.9 §2.3.7 row(s) for `pause:` + `resume:` action_id prefix discriminators (already enumerated at v2.6 composer-arc absorption — no CXA amendment owed at this arc) + empirical `PauseResumeAuditPayload` field-set at `harness-od/src/harness_od/pause_resume_namespace.py:176-273` (Sub-arc A landing at `5d6051d`) |

**Plan shape preserved.** v1.10's structure preserved verbatim. NO new C-OD-NN top-level contract; ONLY a NEW §C-OD-30.4 sub-section under existing C-OD-30 (Pause/resume canonical namespace contract). No new fail class; no new span site; no new attribute set at §C-OD-30.1; no sampling-discipline change at §C-OD-30.3.

**Status posture.** Proposed (v1.10) → **Proposed (v1.11)**. v1.11 is an additive contract authoring (NEW §C-OD-30.4). No v1.10 contract removed; no acceptance criterion change at preserved sections.

**Adjacent defects surfaced (not patched per FM-2 no-extension discipline).**

(i) **`PauseResumeProtocol` body stubs.** `harness-cp/src/harness_cp/pause_resume_protocol.py:106-147` `capture_pause_snapshot` + `attempt_resume` raise `NotImplementedError`. Surfaced; the body authoring is CP-axis scope (not OD-axis); H_T-CP-22 PARTIAL → RETIRE-READY gates on workflow_driver invocation per `harness-cp/CLAUDE.md` §4.1. The v1.11 helper contract is ready-to-consume the moment those bodies + workflow_driver invocation land.

(ii) **CXA v2.9 §2.3.7 row(s) for `pause:` + `resume:` discriminators.** Already enumerated at v2.6 composer-arc absorption — NO CXA amendment owed at this arc. The CXA v2.9 §0.3 8-prefix discriminator table covers `pause:` and `resume:` per the v2.6 7-row enumeration that grew to 8 at v2.9 (cost-axis row 8 added; pause/resume rows preserved).

(iii) **`audit_cp_action_id` pattern divergence between cost-axis and pause/resume.** Cost-axis at §C-OD-26.6 uses `cost:<workflow_id>:<step_action_id>` (per CXA v2.9 §0.3 row 8 discriminator). Pause/resume per §C-OD-30.2 comment-line discipline uses `pause:{workflow_id}:{step_index}` / `resume:{workflow_id}:{step_index}` (step_index not step_action_id). This divergence is preserved at v1.11 (the empirical Sub-arc A landing at `harness-od/src/harness_od/pause_resume_namespace.py:216-218` documents the `step_index`-based pattern); surfaced as a future-arc reconciliation candidate if the `step_action_id`-style pattern proves preferable at CP composer arc.

(iv) **`PauseResumeProtocol` invocation surface enumeration not yet committed.** No spec section enumerates exactly which CP composer events trigger `_project_pause_event_to_audit_payload` vs `_project_resume_outcome_to_audit_payload`. The §C-OD-26.2 cost-axis precedent enumerates billable-span exits as the invocation trigger; the pause/resume parallel would enumerate `pause.captured` + `resume.attempted` span sites per §C-OD-30.1 — but production binding requires the CP composer to author the span-fire-to-helper-call edge. Surfaced; the §C-OD-30.4 contract authors the helper shape, not the composer binding (out of scope per narrow framing).

**Downstream absorption owed (post-v1.11).**

(a) Workspace `CLAUDE.md` §2.3 OD row version bump (v1.10 → v1.11); description amendment to enumerate NEW §C-OD-30.4. APPLIED at this batch session.

(b) Co-published artifacts at this session: OD plan v2.17 → v2.18 U-OD-51 plan revision (separately-authored per implementation-planner skill — AC re-decomposition mirroring U-OD-41 5→9 AC pattern; production-callsite-construction AC marked PARTIAL per `[[halt-route-split-AC-pattern]]` — deferred to CP composer arc).

(c) Impl arc landings: helper(s) at `harness-od/src/harness_od/pause_resume_namespace.py` extension (NEW `_project_pause_event_to_audit_payload` + `_project_resume_outcome_to_audit_payload` module-level functions) + unit tests verifying helper-construction shape. NO production callsite migration at this arc (out of scope per narrow framing).

(d) Memory entry `[[fork-u-cp-72-cost-and-pause-resume-prefix-gap]]` description amendment: advance pause/resume Sub-arc B status to reflect the production-helper contract authoring landing.

(e) Fork doc `.harness/class_1_fork_u_cp_72_cost_and_pause_resume_prefix_gap.md` §10 footer appendage documenting Sub-arc B opening + narrow-scope ratification + helper landing.

---

## §1 — §C-OD-30.4 NEW canonical production-invocation contract (v1.11)

NEW sub-section under existing C-OD-30 (`pause.*` + `resume.*` 8-attribute namespace), positioned after §C-OD-30.3 (Sampling discipline). Pattern parallel to §C-OD-26.1 cost-axis Sub-arc B canonical-invocation contract + §C-OD-26.6.5 deferred-to-implementation-discretion section, scoped to the pause/resume helper surface.

### §C-OD-30.4 — `PauseResumeAuditPayload` canonical production-invocation contract (NEW at v1.11)

**Contract surface.** Canonical helper-based construction pattern for `PauseResumeAuditPayload` (declared at §C-OD-30.2; landed at `harness-od/src/harness_od/pause_resume_namespace.py:176-273` per Sub-arc A). Two module-level helpers compose the payload from `PauseEvent` (pause path) or `(ResumeAttempt, ResumeOutcome)` (resume path) carriers per CP spec v1.11 §26.1 + `harness-cp/src/harness_cp/pause_resume_protocol.py:46-104`. Helpers route through the canonical `cp_audit_to_od_audit` converter via the `pause:` / `resume:` action_id prefix branch per CXA v2.9 §0.3 8-prefix discriminator table (already operational at `harness-cxa/src/harness_cxa/cp_audit_conversion.py:289-299` per Sub-arc A landing).

**Narrow-scope framing.** Under the operator-ratified narrow scope (AskUserQuestion 2026-05-24), the v1.11 contract authors the helper-construction shape WITHOUT authoring production-callsite construction. The CP composer arc — which gates H_T-CP-22 PARTIAL → RETIRE-READY per `harness-cp/CLAUDE.md` §4.1 — is the consumer of the helper; the production callsite binding lives at that follow-on arc (workflow_driver pause-event handler + PauseResumeProtocol body authoring). Helper landing at this arc is **dead code until the CP composer arc lands** — this is honest framing, not a defect.

**Canonical production-invocation pattern (post-v1.11; consumed at the CP composer arc).**

```python
# At pause boundary (CP composer / workflow_driver pause-event handler):
pause_event: PauseEvent = capture_pause_snapshot(workflow_id, pause_reason)  # CP-side; landed at follow-on arc
pause_payload = _project_pause_event_to_audit_payload(
    pause_event,
    workflow_id=workflow_id,
    step_index=step_index,
    snapshot_hash=snapshot_hash,  # computed from pause_event.state_summary_snapshot
    state_ledger_anchor=state_ledger_anchor,  # entry_hash at pause boundary
    prior_event_hash=step_context.parent_event_hash or "0" * 64,
    timestamp=step_context.timestamp or "",
)
audit_entry = cp_audit_to_od_audit(
    pause_payload,
    key_id=ctx.audit_signing_key_id,
    algo=ctx.audit_signing_algorithm,
    entry_core=StateLedgerEntryRef(<step's F2 state-ledger entry_hash>),
)
ctx.audit_writer.append(tenant_id, audit_entry)

# At resume boundary (CP composer / workflow_driver resume-event handler):
resume_outcome: ResumeOutcome = attempt_resume(resume_attempt)  # CP-side; landed at follow-on arc
resume_payload = _project_resume_outcome_to_audit_payload(
    resume_attempt,
    resume_outcome,
    step_index=step_index,
    snapshot_hash=snapshot_hash,  # the prior snapshot being resumed from
    diff_summary_hash=diff_summary_hash,  # sha256 hex if diff_detected; else None
    prior_event_hash=step_context.parent_event_hash or "0" * 64,
    timestamp=step_context.timestamp or "",
)
audit_entry = cp_audit_to_od_audit(
    resume_payload,
    key_id=ctx.audit_signing_key_id,
    algo=ctx.audit_signing_algorithm,
    entry_core=StateLedgerEntryRef(<step's F2 state-ledger entry_hash>),
)
ctx.audit_writer.append(tenant_id, audit_entry)
```

**Helper signatures (canonical at v1.11).**

```python
def _project_pause_event_to_audit_payload(
    event: PauseEvent,
    *,
    workflow_id: str,
    step_index: int,
    snapshot_hash: str,
    state_ledger_anchor: str,
    prior_event_hash: str,
    timestamp: str = "",
) -> PauseResumeAuditPayload: ...


def _project_resume_outcome_to_audit_payload(
    attempt: ResumeAttempt,
    outcome: ResumeOutcome,
    *,
    step_index: int,
    snapshot_hash: str,
    diff_summary_hash: str | None,
    prior_event_hash: str,
    timestamp: str = "",
) -> PauseResumeAuditPayload: ...
```

**Helper signature rationale.**

- **Two helpers, not one.** Pause and resume paths populate disjoint optional-field subsets per §C-OD-30.2 path-conditional discipline (pause: `pause_reason` + `state_ledger_anchor`; resume: `diff_detected` + `diff_policy` + `diff_summary_hash` + `resume_outcome`). Two helpers enforce path-correct field population at the type level — the pause helper cannot populate resume-path fields and vice versa. Mirrors the cost-axis single-helper precedent at §C-OD-26.6 (single carrier shape per producer event) but adapted for the §C-OD-30.2 two-path payload structure.

- **Keyword-only args after the carrier.** Mirrors cost-axis `_project_cost_record_to_audit_payload` keyword-only convention (`*` separator). Forces callsites to be explicit about which composition argument flows from which source — auditability discipline.

- **`workflow_id` not required at resume helper.** `ResumeAttempt.paused_workflow_id` already carries the workflow_id (line 68 of `pause_resume_protocol.py`); helper extracts it from the carrier. The pause helper requires explicit `workflow_id` kwarg because `PauseEvent` does not carry it (5 fields per CP spec v1.11 §26.4 do not include workflow_id; composition site is responsible for plumbing).

- **`snapshot_hash` external (not computed from carrier).** Both helpers receive `snapshot_hash` as a kwarg rather than computing it from `event.state_summary_snapshot` (pause) or via lookup from `attempt.paused_workflow_id` (resume). Snapshot-hash computation is composition-site discipline (the snapshot may be serialized in different forms; the hash discipline is determined per the §22.1 acceptance #9 deferral). Helpers consume the hash as an external input; do not impose serialization format.

- **`state_ledger_anchor` external at pause helper.** The `entry_hash` of the F2 state-ledger entry written at pause boundary is composition-site discipline (the F2 append happens at CP composer; the helper receives the resulting `entry_hash`). Resume path does not have this field.

- **`diff_summary_hash` external at resume helper, `str | None`.** When `outcome.outcome_kind` indicates `RESUME_AFTER_REVALIDATION` or `ABORT_REVALIDATION_FAILED`, the composition site computes `diff_summary_hash = sha256(canonicalize(outcome.material_diff))` and passes it; for `RESUME_CLEAN`, pass `None`.

- **`prior_event_hash` + `timestamp` external.** Same convention as cost-axis `_project_cost_record_to_audit_payload` — these are step-context-derived values that the helper does not compute. Sentinel values (`"0"*64` zero-hash; `""` empty-string) are caller-set per the §C-OD-30.2 + §C-OD-26.6 sibling convention.

**Path discipline.** No operator-supplied paths; the payloads are composed entirely from the input carriers + composition-site-supplied kwargs. The helpers reside at the same `harness-od/src/harness_od/pause_resume_namespace.py` module as the `PauseResumeAuditPayload` class (Sub-arc A landed it there per the sibling-namespace-module pattern at `cost_namespace.py` + sibling modules).

### §C-OD-30.4.1 Per-payload composition discipline

1. **Helper-composed.** `PauseResumeAuditPayload` instances at production callsites are constructed only via the canonical helpers `_project_pause_event_to_audit_payload` / `_project_resume_outcome_to_audit_payload`. Direct construction at production callsites is forbidden (the helpers enforce path-correct field population + action_id prefix pattern + audit_cp_response constant). Direct construction at TEST fixtures and at the converter's own isinstance branch is permitted (mirrors cost-axis §C-OD-26.6.1 carve-out for test fixtures).

2. **`audit_cp_action_id` pattern.**
   - Pause path: `pause:<workflow_id>:<step_index>` per §C-OD-30.2 + CXA v2.9 §0.3 7-prefix discriminator-table entry (preserved through v2.6 7-row composer-arc absorption).
   - Resume path: `resume:<workflow_id>:<step_index>` per §C-OD-30.2 + CXA v2.9 §0.3 (same source). At resume helper, `<workflow_id>` is `attempt.paused_workflow_id`.
   - Discriminator at OD audit-trace consumers is the 2-prefix subset `pause:` / `resume:` per the 8-prefix CXA v2.9 §0.3 discriminator table.

3. **`audit_cp_response` constants.**
   - Pause helper hard-codes `"paused"` per §C-OD-30.2 comment-line discipline (3 documented values: `"paused"` / `"resumed"` / `"diff_detected"`).
   - Resume helper selects between `"resumed"` and `"diff_detected"` based on `outcome.outcome_kind`:
     - `RESUME_CLEAN` → `"resumed"`
     - `RESUME_AFTER_REVALIDATION` → `"resumed"` (revalidation succeeded; final outcome was resume)
     - `ABORT_REVALIDATION_FAILED` → `"diff_detected"` (material diff blocked resume)
     - `ABORT_SNAPSHOT_CORRUPTED` → `"diff_detected"` (treated as integrity-failure → audit row marks diff_detected per §C-OD-30.2 comment)
   - The helper sets the field at construction (NOT a Pydantic field-with-default — preserves sibling-subclass uniformity).

4. **`audit_cp_prior_event_hash` chain.** Joins via `idempotency_key` per existing C-OD-24.4 invariant. Composition site supplies the prior CP event hash; helper does not extract it. String-typed (not Optional) per sibling-subclass convention.

5. **`audit_cp_timestamp`.** ISO-8601 OR `""` MVP sentinel per §24.4 NOTE 8a-iii. Composition site supplies; helper does not compute.

6. **`snapshot_hash` always-populated invariant.** Per §C-OD-30.2 the field is non-Optional (path-conditional fields are Optional; `snapshot_hash` is always-populated common-field). Both helpers REQUIRE `snapshot_hash` kwarg (no default).

7. **`step_index` always-populated invariant.** Per §C-OD-30.2 the field is non-Optional. Both helpers REQUIRE `step_index` kwarg.

8. **Path-specific field exclusion.** The pause helper MUST set `diff_detected` / `diff_policy` / `diff_summary_hash` / `resume_outcome` to `None`. The resume helper MUST set `pause_reason` / `state_ledger_anchor` to `None`. Enforced at helper construction (helper body explicitly passes `None` for path-disjoint fields).

9. **`diff_policy` source at resume helper.** Extracted from the resume composition context per CP spec v1.11 §26.2 `MaterialDiffPolicy` 3-class (`STRICT` / `LENIENT` / `OPERATOR_ARBITRATE`). The resume helper signature does not include `diff_policy` as a kwarg because it's derived from the resume composition lifecycle (composer arc determines policy from manifest + step context). Helper inlines `None` for `RESUME_CLEAN` outcomes (no diff to apply policy to); inlines the active policy enum value for other outcomes. **Adjacent finding:** the resume helper signature could be widened to accept `diff_policy` as a kwarg at a future arc if the composer surfaces it as input; v1.11 carries the inlined approach per FM-2.

10. **Frozen / extra-forbid invariant preserved.** Helper composes the existing `PauseResumeAuditPayload` Pydantic v2 BaseModel per Sub-arc A landing (`model_config = ConfigDict(extra="forbid", frozen=True)` at `pause_resume_namespace.py:213`). Helpers do not extend or modify the BaseModel; they construct it.

### §C-OD-30.4.2 Converter integration (already operational per Sub-arc A)

The `cp_audit_to_od_audit` converter at `harness-cxa/src/harness_cxa/cp_audit_conversion.py:289-299` already routes `PauseResumeAuditPayload` through the `pause:` + `resume:` action_id prefix branches per Sub-arc A landing at `5d6051d`. **No converter amendment owed at v1.11.** The helpers introduced at §C-OD-30.4 produce `PauseResumeAuditPayload` instances that consume the existing converter dispatch unchanged.

Specifically:

1. **Import already exists:** `PauseResumeAuditPayload` import at `cp_audit_conversion.py` per Sub-arc A.
2. **Namespace prefix constant already exists:** `PAUSE_RESUME_AUDIT_NAMESPACE_PREFIX` per Sub-arc A.
3. **`CpAuditCarrier` union already includes `PauseResumeAuditPayload`** per Sub-arc A (line 96-104).
4. **isinstance branch already operational** per Sub-arc A (line 289-299; emits to `audit.pause_resume.*` sub-namespace).

The §C-OD-30.4 contract authors the producer-side helper; the consumer-side converter binding is preserved verbatim.

### §C-OD-30.4.3 Failure-mode taxonomy

No new fail class introduced at v1.11. Helper construction is guarded by Pydantic v2 validation at the `PauseResumeAuditPayload` BaseModel (`extra="forbid"` catches drift; type validation catches mis-typed kwargs); construction failures surface as `pydantic.ValidationError` which the CP composer arc MAY catch and log per implementer discretion (no fail-class commitment at v1.11).

Adjacent fail-class commitment owed at the CP composer arc (separate scope): per `harness-cp/CLAUDE.md` H_T-CP-22 PARTIAL gate, the workflow_driver pause-event handler will need a fail class equivalent to `CP-FAIL-PAUSE-RESUME-AUDIT-COMPOSE` (mirrors `RT-FAIL-SUB-AGENT-AUDIT-COMPOSE` at runtime spec v1.7 §14 from the U-RT-59 Fork 2 audit-write resolution arc). Surfaced; not authored at v1.11.

### §C-OD-30.4.4 Invariants

1. **Helper-only production construction.** Per §30.4.1 #1; direct construction at production callsites is forbidden. Tests + converter dispatch may construct directly.

2. **`audit_cp_action_id` carries `pause:` or `resume:` prefix.** Enforced at helper construction (helper body inlines the prefix-format string per #2 above). Pydantic v2 validator MAY be added at impl if helper inlining proves brittle.

3. **Path-disjoint field nullification.** Pause helper nulls resume-path fields; resume helper nulls pause-path fields. Per §30.4.1 #8. Enforced at helper body construction (explicit `None` for path-disjoint fields).

4. **Audit-write idempotency.** Downstream `audit_writer.append` is idempotent on the F2 state-ledger `entry_hash` (per existing OD audit-writer discipline). The helpers do not need idempotency-key handling — that lives at the CP composer arc that calls them.

5. **No spec-extension at helper-deferred fields.** Per change-note (iii) + (iv): the `step_index`-vs-`step_action_id` divergence with cost-axis is preserved; the composer-binding enumeration is deferred to CP composer arc.

6. **NotImplementedError absence post-v1.11.** The helper bodies at impl arc MUST NOT raise `NotImplementedError`. The `PauseResumeProtocol` body stubs (`capture_pause_snapshot` + `attempt_resume`) remain `NotImplementedError` until the CP composer arc; the OD-side helpers must be fully-bodied (constructing valid `PauseResumeAuditPayload` instances from supplied carriers + kwargs). Dead-code-status is a deployment property (no caller invokes the helpers), not a body-incompleteness property.

### §C-OD-30.4.5 Deferred to implementation discretion

- **Production callsite construction.** Out of scope at v1.11 per narrow framing. The CP composer arc (separate scope; gates H_T-CP-22 PARTIAL → RETIRE-READY per `harness-cp/CLAUDE.md` §4.1) authors:
  - The body of `capture_pause_snapshot` + `attempt_resume` at `harness-cp/src/harness_cp/pause_resume_protocol.py:106-147`.
  - The workflow_driver pause-event handler invoking `PauseResumeProtocol`.
  - The composition site that invokes `_project_pause_event_to_audit_payload` / `_project_resume_outcome_to_audit_payload` at pause / resume boundaries.
  - The F2 state-ledger entry that anchors `state_ledger_anchor`.
  - The IS bounded-read for snapshot retrieval at resume boundary.

- **`diff_policy` resume-helper kwarg.** Per §30.4.1 #9: v1.11 inlines `None` for `RESUME_CLEAN` outcomes and the active policy enum value for non-clean outcomes. Future arc MAY widen the resume helper signature to accept `diff_policy` as an explicit kwarg if the composer surfaces it as input.

- **Snapshot-hash serialization format.** Per §22.1 acceptance #9: snapshot serialization format is implementer-discretion at the CP composer arc; the OD-side helpers consume `snapshot_hash` as an external input without prescribing the serialization. v1.11 does not pin a serialization format.

- **`step_index` source semantics.** Whether `step_index` derives from a per-workflow monotonic counter, the manifest-declared step ordinal, or the workflow-driver dispatch index is composer-arc discretion. The helpers consume `step_index` as an integer kwarg.

- **Tracer/observer integration.** Helpers do not emit tracer spans (`pause.captured` / `resume.attempted` per §C-OD-30.1) — span emission lives at the CP composer arc adjacent to the audit-write helper invocation. v1.11 explicitly decouples span emission from audit-payload composition.

---

## §2 — Preservation guarantees

| Section | Preservation |
|---|---|
| All v1.10 contracts (NEW §C-OD-26.6 CostRecordAuditPayload + amended §C-OD-26.1) | Preserved verbatim |
| All v1.9 contracts (§C-OD-30.1 attribute-type-citation absorption) | Preserved verbatim |
| All v1.8 NEW contracts (C-OD-25 through C-OD-33 including §C-OD-30.1 / .2 / .3) | Preserved verbatim |
| v1.8 §C-OD-30.1 `pause.*` + `resume.*` 8-attribute canonical schema | Preserved verbatim |
| v1.8 §C-OD-30.2 `PauseResumeAuditPayload` declaration (with v1.9 `WorkflowPauseReason` cite absorption) | Preserved verbatim |
| v1.8 §C-OD-30.3 sampling discipline | Preserved verbatim |
| v1.8 §24 audit-ledger schema + C-OD-24 4-section chain + `compute_entry_hash` helper | Preserved verbatim |
| §C-OD-26.1 v1.10 cost-axis invocation signature | Preserved verbatim |
| §C-OD-26.6 v1.10 CostRecordAuditPayload typed carrier | Preserved verbatim |
| §C-OD-30.4 (NEW) PauseResumeAuditPayload canonical production-invocation contract | **NEW at v1.11** per §1 above |

---

## Filing footer

| Field | Value |
|---|---|
| Artifact | `Spec_Operational_Discipline_v1_11.md` |
| Version | v1.11 |
| Filing event | Pause/resume back-flow arc (narrow scope per operator AskUserQuestion 2026-05-24) per `[[fork-u-cp-72-cost-and-pause-resume-prefix-gap]]` §9 residual routing target. 2026-05-24 |
| Predecessor | `Spec_Operational_Discipline_v1_10.md` (v1.10 substantive content preserved verbatim outside the NEW §C-OD-30.4 sub-section) |
| Successor | (none — current canonical) |
| Co-published with | `Implementation_Plan_Operational_Discipline_v2_18.md` (companion U-OD-51 plan revision at this session — AC re-decomposition mirroring U-OD-41 5→9 AC pattern; production-callsite-construction AC marked PARTIAL per `[[halt-route-split-AC-pattern]]`) + impl arc landings (helper(s) at `pause_resume_namespace.py` extension + unit tests) |
| Status posture | Proposed (v1.10) → Proposed (v1.11). v1.11 is an additive contract authoring (NEW §C-OD-30.4). No v1.10 contract removed. |
| Operator authority | AskUserQuestion 2026-05-24 — operator selected "Narrow — OD-side helper only" scope. Reverses fork doc §9 doc-only deferral. |
| Related forks | `[[fork-u-cp-72-cost-and-pause-resume-prefix-gap]]` §9 (pause/resume Sub-arc residual — narrow scope ratification + helper authoring) |
| Related memory | `[[fork-u-cp-72-cost-and-pause-resume-prefix-gap]]` (advance pause/resume Sub-arc B status); `[[halt-route-split-AC-pattern]]` (production callsite construction deferred at §C-OD-30.4.5 per FM-2); `[[verification-shape-sharpened-grep-vs-e2e]]` (helper is dead code until CP composer arc; H_T-CP-22 PARTIAL → RETIRE-READY gate is workflow_driver invocation, not helper authoring) |
| Revision policy | In-CLI per workspace discipline (`CLAUDE.md` §4.3) |
| Date | 2026-05-24 |

*Filed at Phase 7 sub-phase 7b/7c as the OD-side pause/resume back-flow arc landing per fork doc §9 routing target. v1.10 substantive content preserved verbatim; 1 new sub-section at §C-OD-30.4 authoring the canonical production-invocation contract + helper signatures. Co-published with OD plan v2.18 U-OD-51 AC re-decomposition + impl arc helper landings. NO production callsite migration at this arc per operator-ratified narrow scope — helper is dead code until CP composer arc lands.*
