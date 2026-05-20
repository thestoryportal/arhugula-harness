# Implementation Plan — Control Plane (CP axis) — v2.13

## §0 Change-note (v2.12 → v2.13)

**Revision:** v2.13 — Phase 7 architectural-tension revision pass, in-CLI. Absorbs
CP spec v1.5 §25.9 Cost-attribution emission composition (operator-ratified Q1e +
Q2-bounded + Q3c + Q4 from `.harness/fork_u_rt_49_cost_attribution_invocation_underspec.md`,
2026-05-20). The absorption is **convention-level** — §25.9 establishes that step
bodies (NOT the driver) own cost-attribution chain invocation per the §25.5
propagated-emission pattern. The driver, `DriverContext` Protocol, `WorkflowDriver`
class shape, and §25.7 fail-class taxonomy are all preserved verbatim from v2.12.

**No new atomic unit at v2.13.** §25.9 is a step-body authoring convention, not
a driver contract obligation. Materialization happens at step-body authoring time
(downstream consumer concern); the U-RT-49 smoke test step body is the first
materialization at this arc's runtime-side close. v2.13 is therefore a single-
section absorption pass: prose-only acknowledgment of the new spec contract at
the U-CP-56/U-CP-57 driver units (which remain unchanged — they do NOT invoke
cost-attribution; the convention is downstream of dispatch).

Predecessor: v2.12 (resolved `[[fork-u-cp-56-resumption-underspec]]` via Path
A-modified — `entry_version` field on `WorkflowManifestEntry` + N-lookup
resumption read).

**Spec stability invariant inverts at v2.13.** Unlike v2.12 (which closed a plan-
side gap with NO spec bump), v2.13 absorbs a spec amendment (CP spec v1.4 → v1.5
§25.9 new subsection). v2.13 carries the spec change downstream into the plan;
no further spec amendment required at v2.13 close.

### §0.1 Net delta from v2.12

1. **No atomic unit modified.** U-CP-56 (driver core), U-CP-57 (drain composition),
   and all other v2.12 units are preserved verbatim. The §25.9 convention is
   transparent to the driver: step bodies fire `ctx.cost_chain.compute_per_attempt_cost`
   on their own exit; the driver dispatches via the cap-aware router per §25.3.3.4
   and does not observe the cost-attribution emission.

2. **§25.9 acknowledgment note added at §1 (Plan-level contract reference).** A
   single paragraph documents that v2.13 absorbs the §25.9 convention, names the
   downstream materialization site (`harness-runtime/tests/integration/test_run_smoke.py`
   step body extension), and references the substitution carry-forward record
   `.harness/fork_price_table_ref_substitution_retirement.md`.

3. **§0.2 v2.13 fork-resolution traceability** (new sub-section, this revision):

   | Fork record | Status at v2.13 close |
   |---|---|
   | `.harness/fork_u_rt_49_cost_attribution_invocation_underspec.md` | spec-side ABSORBED (CP spec v1.5 §25.9); plan-side ABSORBED (this v2.13 change-note); runtime un-strike PENDING (smoke test extension) |
   | `.harness/class_1_tension_u_rt_44_workflow_loop_drain.md` (parent) | CLOSED-PARTIAL (since Lane 6) → PENDING fully CLOSED at smoke test extension |
   | `.harness/fork_price_table_ref_substitution_retirement.md` (NEW; filed this arc) | OPEN as bounded H_E substitution residual per X-AL-2; rate-table authoring out of scope for this arc; carries into sub-phase 7d substitution-retirement events |

4. **Open architectural question carried forward (Class 3 informational).** Cross-
   topology cost-attribution boundary (sub-agent-dispatch / orchestrator-workers /
   etc.) is out of scope at v2.13 — v2.13 scope tracks CP spec v1.5 §25.1
   `SINGLE_THREADED_LINEAR` topology only. New CP spec + plan revision-pass owed
   when the first non-linear topology materializes. Surface as a Phase 7 sub-phase
   7c CXA seam candidate at that time.

### §0.2 Coverage matrix delta

Coverage matrix unchanged. CP spec v1.5 §25.9 is a convention-level subsection
that does not introduce a new C-CP-NN contract; the §[traceability] matrix at CP
spec v1.5 extended the existing C-CP-25 row with C-OD-14 substrate-consumed entry
(not a new contract row). No new unit ID. No new coverage cell.

---

## §0 [original] Change-note (v2.11 → v2.12)

**Revision:** v2.12 — Phase 7 architectural-tension revision pass, in-CLI. Resolves
`[[fork-u-cp-56-resumption-underspec]]` (Class 1 fork filed 2026-05-20 at U-CP-56
PARTIAL-LAND) via the operator-ratified **Path A-modified** path
(operator decision 2026-05-20 at fork-u-cp-56-resumption-underspec session):
extend `WorkflowManifestEntry` (U-CP-13) with `entry_version: int = 1`
default-valued field; un-strike U-CP-56 AC #6 with selective per-run
replay-resumption implemented via **N-lookup over the existing IS
`read_by_idempotency_key` primitive** (NOT a new IS prefix-match primitive —
the fork's original Path A second half is voided per operator deviation
sign-off; rationale: O(N) targeted reads over a small N — typical workflows
single-digit steps — is simpler than introducing an IS-axis primitive that
would have only one consumer at v2.12 scope).

Predecessor: v2.11 (added U-CP-56 + U-CP-57 absorbing C-CP-25 from CP spec v1.4).

**Spec stability invariant.** No CP spec bump. CP spec v1.4 §6.1 (preserved
verbatim from v1.2) already states the manifest schema is open at
"// ... additional per-workload fields"; CP spec v1.4 §25.6 already cites
`manifest_entry.entry_version` as if the field exists. v2.12 closes the
plan-side gap by declaring the field at U-CP-13's carrier; no spec contract
amendment required.

### §0.1 Net delta from v2.11

1. **U-CP-13 carrier-growth (re-open boundary).** `WorkflowManifestEntry` grows
   from 10 fields to 11: appends `entry_version: int = 1` (default-valued, so
   existing constructor sites do not break — see §0.3 ripple absorption).
   `entry_version` is the integer carried into the `run_idempotency_key` hash
   composition at U-CP-56 §25.6. Default value 1 means pre-versioning workflows
   compose with `entry_version=1` automatically; operators bump the value when
   the workflow's contract changes in a way that should invalidate cached
   step-resumption substrate.

2. **U-CP-56 AC #6 re-author (un-strike from PARTIAL-LAND).** Replaces the
   pending-fork stub at v2.11 AC #6 with the full selective-resumption
   implementation per the N-lookup approach. The shipped weaker behavior
   (RESUMPTION emit on any non-genesis ledger) is replaced with selective
   per-run RESUMPTION emit (only when prior step entries exist for THIS run's
   `run_idempotency_key`). The test `test_resumption_emit_shape_wired_for_save_
   point_checkpoint` (current name reflecting the weaker behavior) is renamed
   back to its original intent `test_workflow_resumption_emitted_on_save_
   point_checkpoint_reentry` plus a new test
   `test_resumption_not_emitted_for_unrelated_prior_run` asserting selective
   emit.

3. **LedgerReaderLike Protocol introduction.** The CP-axis workflow-driver
   module gains a new `LedgerReaderLike` Protocol mirroring the existing
   `LedgerWriterLike` shape (separation of read / write surfaces). The
   `DriverContext` Protocol extends to include `ledger_reader: LedgerReaderLike`
   alongside `ledger_writer` + `lifecycle_emitter` + `drained_flag`. Runtime
   composition (cross-axis bridge) provides a concrete `LedgerReader` adapter
   wrapping the existing `harness_is.state_ledger_read.LedgerNavigationPrimitive`
   + `harness_is.state_ledger_write.read_ledger` round-trip. No new IS-axis
   primitive lands.

### §0.2 No spec bump rationale

CP spec v1.4 §6.1 (verbatim from v1.2) declares the manifest schema with
explicit extension authorization: `// ... additional per-workload fields`.
Adding `entry_version` to the materialized U-CP-13 carrier consumes the
authorized extension surface — it does not extend the contract. Concurrently,
CP spec v1.4 §25.6 line 270 already references `manifest_entry.entry_version`
in the hash composition formula, presuming the field's existence. v2.12 closes
the plan-side defect (U-CP-13 not declaring a spec-presumed field) without
contract revision.

IS spec v1.2 §7.4 "Deferred to implementation discretion" enumerates
`read_by_idempotency_key(key)` as an authorized read primitive — already
materialized at `harness_is.state_ledger_read.LedgerNavigationPrimitive`.
No IS spec amendment required.

### §0.3 Ripple absorption — U-CP-13 carrier-growth

`WorkflowManifestEntry` is consumed at 17 file locations across the workspace
(CP-axis source + tests + runtime composition + tests). The new field is
`int = 1` default-valued, so:

- **Source constructors:** all 0 sites currently constructing without
  `entry_version` continue to validate (default applies). No source-side
  changes required outside of U-CP-13's own declaration.
- **Test constructors:** all existing test constructors continue to work
  unchanged. New tests can pass an explicit `entry_version=N > 1` to exercise
  versioning semantics.
- **Cross-axis consumers (runtime composition):** runtime's
  `WorkflowObject` Protocol carries `manifest_entry: WorkflowManifestEntry`;
  the Protocol's surface is unchanged at v2.12 (the new field rides through
  via the Pydantic v2 frozen-record opaque transmission).

Net source-side ripple: 1 file (`harness-cp/src/harness_cp/workflow_manifest_entry.py`).
Net test ripple: optional growth (new tests added; no existing tests modified).

### §0.4 AC #6 re-author — concrete delta

**Old (struck at v2.11):** "STRUCK pending fork resolution — `WorkflowManifestEntry`
has no `entry_version` field; no IS prefix-match read primitive. Weaker behavior
shipped: save-point-checkpoint binding emits RESUMPTION whenever ledger is
non-genesis."

**New (v2.12):** "Under `manifest_entry.engine_class == 'save-point-checkpoint'`:
at driver entry, compute
`run_idempotency_key = sha256(run_id, manifest_entry.workflow_id, manifest_entry.entry_version)`;
for each step index `i ∈ [0, len(steps))`, compute
`expected_step_key = sha256(run_idempotency_key, i)` and call
`ctx.ledger_reader.read_by_idempotency_key(expected_step_key, BoundedWindow(...))`.
The driver advances `resume_at` to `i + 1` for each step whose expected key
returns ≥1 ledger entries; stops at the first step whose expected key returns
zero entries. If `resume_at > 0`, emit `WorkflowEventClass.RESUMPTION`. The
step iteration loop begins at `resume_at` instead of 0. Under
`pure-pattern-no-engine`: no resumption read at entry (state-ledger native
dedup per §8.2 row 3); per-step `idempotency_key = sha256(run_idempotency_key,
step.index)` for dedup."

**Acceptance:** `resume_at` index is determined by the highest contiguous
step index whose ledger entry exists. Non-contiguous prior runs (gap in step
sequence) treat as "resume at first gap" — conservative semantic; gap-fill
is out of scope.

### §0.5 LedgerReaderLike Protocol declaration

New Protocol declared at `harness_cp.workflow_driver`:

```python
@runtime_checkable
class LedgerReaderLike(Protocol):
    """Read-side state-ledger substrate (C-IS-07 §7.4 implementation-discretion
    primitive). Concretized by runtime LedgerReader wrapping
    harness_is.state_ledger_read.LedgerNavigationPrimitive.
    """

    def read_by_idempotency_key(
        self,
        idempotency_key: Identifier,
        bounded_window: BoundedWindow,
    ) -> ReadResult: ...
```

`DriverContext` Protocol extends:

```python
@runtime_checkable
class DriverContext(Protocol):
    ledger_writer: LedgerWriterLike
    ledger_reader: LedgerReaderLike  # NEW at v2.12
    lifecycle_emitter: LifecycleEventEmitterLike
    drained_flag: asyncio.Event
```

`HarnessContext` (runtime composition) extends to populate `ledger_reader` at
bootstrap stage 1 IS adjacent to existing `ledger_writer` materialization.
Cross-axis runtime composition.

### §0.6 Carry-forwards from v2.11 (preserved verbatim)

All v2.11 §0.6 (adjacent-defect findings from CP spec v1.4 Change-note) entries
preserved verbatim. v2.12 does not introduce new spec carry-forwards.

### §0.7 Forward-flag (preserved verbatim)

All v2.11 §0.7 entries preserved. v2.12 closes the previously-listed
`[[fork-u-cp-56-resumption-underspec]]` residual carry-forward.

### §0.8 Dependency-graph delta

**No new units.** v2.12 modifies U-CP-13 (existing L1 unit) and U-CP-56
(existing L? unit). DAG topology unchanged. Within-axis edges unchanged.

**No new cross-axis edges.** U-CP-56's existing cross-axis edges to U-IS-07 /
U-IS-10 / U-IS-11 (already declared at v2.11) suffice. The LedgerReaderLike
Protocol composes against the same IS substrate via different navigation
primitives (`read_by_idempotency_key` rather than `append_ledger_entry`). No
new CXA edge declaration required at the next CXA revision pass.

### §0.9 Coverage matrix delta

Coverage matrix unchanged. C-CP-25 §25.6 cell mark for U-CP-56 was `✓` at
v2.11 (covered by partial-land); v2.12 makes it `✓ (full)` (covered by
full-land). Cell-mark change is informational; matrix cardinality unchanged.

### §0.10 Status block + filing footer

| Field | Value |
|---|---|
| Plan version | v2.12 |
| Predecessor | `Implementation_Plan_Control_Plane_v2_11.md` (preserved verbatim except U-CP-13 + U-CP-56 §6 amendments per this Change-note) |
| Spec authority | `Spec_Control_Plane_v1_4.md` (unchanged; no spec bump at v2.12) |
| Unit count | 60 (unchanged from v2.11) |
| Fork resolution | `[[fork-u-cp-56-resumption-underspec]]` Class 1 → CLOSED at v2.12 |
| Next downstream consumer | `phase-7-implementation` skill — atomic-unit consumption against U-CP-13 (re-open boundary) then U-CP-56 (AC #6 un-strike) |
| Filing date | 2026-05-20 |

---

## §1 Spec inventory + cluster decomposition

Preserved verbatim from v2.11.

---

## §2 Atomic-unit decomposition

Preserved verbatim from v2.11 **except**:

### §2.2 Cluster 2 — F3 lifecycle + manifest

#### U-CP-13 — `WorkflowManifestEntry` schema (re-open boundary at v2.12)

**Implements:** [C-CP-06 §6.1 manifest field schema (carrier materialization;
spec §6.1 "// ... additional per-workload fields" authorizes the v2.12 carrier
growth from 10 → 11 fields)]

**Depends on:** [U-CP-00 `WorkloadClass`, U-CP-15 `EngineClass`, U-CP-22
`TopologyPattern`, U-CP-38 `HITLPlacement`, U-CP-03 `LayerBudget`, U-CP-04
`FallbackChain`, U-CP-28 `SubAgentBrief`, U-CORE-01 `StepID` carrier, U-CP-00c
`ModelBinding`, U-CP-30 `HandoffContext`-family substrate]

**Inputs:** No new dependencies at v2.12.

**Files affected:** `harness-cp/src/harness_cp/workflow_manifest_entry.py`
(field-set growth 10 → 11; rollback-boundary singular).

**Signatures:**

```python
class WorkflowManifestEntry(BaseModel):
    """The workflow-manifest-entry shape — canonical per-workflow customization.

    Exactly eleven top-level fields at v2.12 (was ten at v2.11).
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    workflow_id: str
    workload_class: WorkloadClass
    persona_tier: PersonaTier
    engine_class: EngineClass
    topology_pattern: TopologyPattern
    layer_budgets: tuple[LayerBudget, ...]
    fallback_chain: FallbackChain
    hitl_placements: tuple[HITLPlacement, ...]
    sub_agent_briefs: tuple[SubAgentBrief, ...] | None = None
    per_step_overrides: dict[StepID, StepOverride]

    entry_version: int = 1
    """v2.12 addition. Integer carried into the U-CP-56 §25.6
    `run_idempotency_key = sha256(run_id, workflow_id, entry_version)`
    composition. Default value 1 means pre-versioning workflows compose
    deterministically without explicit caller-side annotation. Operators
    bump the value when the workflow's contract changes in a way that
    should invalidate cached step-resumption substrate (semantic version
    of the workflow declaration itself; orthogonal to the workflow's
    body steps' content)."""
```

**Acceptance criteria (v2.12 delta — growth only):**

1. **Field-set growth (v2.12).** `WorkflowManifestEntry.model_fields` includes
   `entry_version` of type `int` with default `1`. All ten v2.11 fields
   preserved verbatim (field-set is purely additive).
2. **Default value semantics.** Constructing `WorkflowManifestEntry(...)`
   without explicit `entry_version` succeeds and produces an instance with
   `entry_version == 1`. Constructing with `entry_version=42` produces an
   instance with `entry_version == 42`.
3. **Backward compatibility (test-suite stability).** All existing
   `WorkflowManifestEntry(...)` constructor sites in tests continue to
   validate without modification. Pydantic v2 `extra='forbid'` is unchanged
   (additive field-set growth respects forbid semantics).

**Tests (additive — no v2.11 test renamed or removed):**
- `test_workflow_manifest_entry_has_entry_version_field`
- `test_workflow_manifest_entry_default_entry_version_is_1`
- `test_workflow_manifest_entry_accepts_explicit_entry_version`

**Rollback boundary:** Revert the single `workflow_manifest_entry.py` file to
its v2.11 state (remove `entry_version` declaration). Any consumer that
references `entry_version` (driver §25.6 logic) reverts in lockstep at U-CP-56
§2.9 amendment rollback.

---

### §2.9 Cluster 9 (v2.11 addendum, v2.12 amendment) — Workflow execution driver

[U-CP-56 cluster header preserved from v2.11.]

#### U-CP-56 — Workflow execution driver core (v2.12 AC #6 un-strike)

[U-CP-56 description preserved from v2.11 §2.9 until acceptance criteria.]

**Acceptance criteria (v2.12 amendment — AC #6 only; ACs #1–#5 + #7–#9
preserved verbatim from v2.11):**

[ACs #1–#5 preserved verbatim from v2.11 §2.9.]

6. **Replay-resumption read at re-entry (§25.6) — full implementation at v2.12.**
   Resolves `[[fork-u-cp-56-resumption-underspec]]`. Under
   `manifest_entry.engine_class == 'save-point-checkpoint'`:

   (a) At driver entry, compute
       `run_idempotency_key = sha256(run_id, manifest_entry.workflow_id, manifest_entry.entry_version)`.
       Per CP spec v1.4 §25.6 line 270 verbatim. `entry_version` defaults to
       1 per U-CP-13 v2.12 carrier-growth; explicit caller-supplied values
       bump the hash composition (selective invalidation of cached
       resumption substrate when workflow contract changes).

   (b) Determine `resume_at`: for `i ∈ [0, len(steps))`, compute
       `expected_step_key = sha256(run_idempotency_key, i)` per §25.6's
       `idempotency_key = sha256(run_idempotency_key, step.index)`
       discipline. Query
       `ctx.ledger_reader.read_by_idempotency_key(expected_step_key,
       BoundedWindow(max_entries=ctx.ledger_writer.entry_count or 1,
       workload_class=manifest_entry.workload_class))`. If returned
       `entries` is non-empty, set `resume_at = i + 1` and continue.
       Otherwise (returned entries empty), break — `resume_at` is the
       index of the first unmaterialized step.

   (c) If `resume_at > 0`, emit `WorkflowEventClass.RESUMPTION` per
       §25.6 step 3. If `resume_at == 0`, no resumption emit (genesis run
       under save-point-checkpoint binding).

   (d) Step iteration loop (acceptance #4) begins at `resume_at` rather
       than 0. Steps `[0, resume_at)` are skipped — they are already
       materialized in the ledger from a prior run that crashed or was
       drained partway through.

   Under `manifest_entry.engine_class == 'pure-pattern-no-engine'`:
   no resumption read at entry (state-ledger native dedup per §8.2 row 3
   handles dedup at per-step `idempotency_key` level — no driver-side
   resumption discrimination required). Per-step `idempotency_key =
   sha256(run_idempotency_key, step.index)` per §25.6's hash composition.

   **Conservative semantic — gap behavior.** If the ledger contains a
   gap (e.g., step 0 + step 2 entries exist but step 1 entry missing),
   `resume_at` advances only over the contiguous prefix (step 0). Step 1
   re-runs from fresh; step 2's entry is left in place. This may produce
   a duplicate ledger entry at step 2 (idempotent at the C-IS-07 §7.1
   keying tuple level — the second append is rejected as duplicate, or
   accepted-idempotently per write-key semantics; either is acceptable).
   Gap-fill resumption is out of scope at v2.12.

[ACs #7–#9 preserved verbatim from v2.11 §2.9.]

**Tests (v2.12 delta from v2.11):**

- **Rename:** `test_resumption_emit_shape_wired_for_save_point_checkpoint` →
  `test_workflow_resumption_emitted_on_save_point_checkpoint_reentry`
  (test body grown to assert selective per-run emit, not any-prior-entry emit).
- **Add:** `test_resumption_not_emitted_for_unrelated_prior_run` (prior
  ledger entries exist from a different `run_id` / `workflow_id` /
  `entry_version` → expected step keys produce zero matches → no
  RESUMPTION emit; step iteration begins at 0).
- **Add:** `test_resumption_skips_already_replayed_steps` (prior ledger
  entries match steps `[0, 1, 2]` for this run's expected keys; driver
  resumes at step 3; steps `[0, 1, 2]` skipped — verified by step_dispatcher
  invocation count).
- **Add:** `test_resume_at_advances_over_contiguous_prefix_only` (gap in
  step sequence — step 0 + step 2 entries exist, step 1 missing →
  `resume_at = 1`; step 1 re-runs; step 2 produces second-entry).
- **Preserve:** all other U-CP-56 tests from v2.11 unchanged.

**Rollback boundary (v2.12 amendment):** Revert the `_compute_run_idempotency_key`
extras parameter usage at driver to its v2.11 baseline (no `entry_version`
input); revert the §25.6 resumption read loop to the v2.11 weaker
non-genesis emit; revert LedgerReaderLike Protocol introduction at
`workflow_driver.py`; revert DriverContext extension. Composes with U-CP-13
carrier-growth rollback (§0.3 above).

---

## §3 Within-axis DAG topology

Preserved verbatim from v2.11.

---

## §4 Coverage matrix

Preserved verbatim from v2.11 with the C-CP-25 §25.6 cell-mark for U-CP-56
upgraded from `✓` (partial-land) to `✓ (full)` (v2.12 un-strike).

---

## §5 Cross-axis edge inventory

Preserved verbatim from v2.11. No new cross-axis edges at v2.12.

---

## §6 Adjacent-defect findings (preserved verbatim from v2.11)

Preserved verbatim from v2.11.

---

## §7 Forward-flag (preserved verbatim from v2.11)

Preserved verbatim from v2.11; the previously-listed
`[[fork-u-cp-56-resumption-underspec]]` carry-forward is RESOLVED at v2.12.

---

## §8 Status block + filing footer

| Field | Value |
|---|---|
| Plan version | v2.13 |
| Predecessor | `Implementation_Plan_Control_Plane_v2_12.md` (preserved verbatim — v2.13 is convention-level absorption only; no v2.12 unit body modified) |
| Spec authority | `Spec_Control_Plane_v1_5.md` (NEW at this revision — absorbs §25.9 Cost-attribution emission composition) |
| Unit count | 60 (unchanged) |
| Fork resolution | `[[fork_u_rt_49_cost_attribution_invocation_underspec]]` Class 1 → spec-side + plan-side ABSORBED at v2.13; runtime un-strike PENDING at smoke test extension; parent `[[fork_u_rt_44_workflow_loop_drain]]` CLOSED-PARTIAL → fully CLOSED at same arc completion |
| Filing date | 2026-05-20 |
| Authoring authority | In-CLI revision pass per `Project_Workflow_v1_8.md` §2.7.6 back-flow routing — Class 1 routing path applied to absorbed CP spec v1.5 §25.9 convention (step-body-owned propagated cost-attribution emission; downstream materialization at U-RT-49 smoke test step body) |
