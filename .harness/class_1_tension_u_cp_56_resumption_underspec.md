# Class 1 Tension — U-CP-56 AC #6 (save-point-checkpoint replay-resumption) under-implementable

**Status:** **CLOSED** 2026-05-20 — resolved via operator-ratified
**Path A-modified** (extend `WorkflowManifestEntry` with `entry_version` field;
N-lookup over existing IS `read_by_idempotency_key` primitive instead of new
prefix-match primitive). CP plan v2.11 → v2.12. No spec bump required.
Worktree branch `worktree-cp-56-resumption-fix`.
**Filed:** 2026-05-20 (U-CP-56 PARTIAL-LAND)
**Trigger unit:** U-CP-56 (`Implementation_Plan_Control_Plane_v2_11.md` AC #6)
**Pattern:** `[[halt-route-split-AC-pattern]]`
**Routing target:** CP plan v2.12 (`Implementation_Plan_Control_Plane_v2_12.md`); no CP spec bump (CP spec v1.4 §6.1 "// ... additional per-workload fields" extension clause + §25.6 already-cited `manifest_entry.entry_version` suffice).

---

## Surface

Plan v2.11 U-CP-56 AC #6 specifies four behaviors for save-point-checkpoint
re-entry per CP spec v1.4 §25.6:

1. Compute `run_idempotency_key = sha256(run_id, workflow_id, entry_version)`
2. Read C-IS-07 state-ledger for entries **matching this run's prefix**
3. Emit `RESUMPTION` **if matches exist**
4. **Skip already-replayed steps; resume at first unmaterialized step**

## Defect

Two substrate gaps prevent full materialization:

1. **`WorkflowManifestEntry` has no `entry_version` field.** AC #6 step 1 requires
   `entry_version` in the hash composition for run-scope identity. U-CP-13
   declares 10 fields; none is `entry_version`. The spec recommendation cited it
   as a hash input but U-CP-13 was already landed without the field. Extending
   `WorkflowManifestEntry` is a foundational-unit-modification (cross-axis ripple
   — anything that constructs the manifest must absorb the new field).

2. **No per-run prefix-match read primitive.** The IS state-ledger read surface
   (`harness_is.state_ledger_write.read_ledger`) returns all entries; there is
   no `read_entries_matching_prefix(run_idempotency_key)` primitive. The driver
   would need to implement prefix-match in CP via filter-after-read, OR an IS
   primitive needs to land.

Without (1) and (2), the driver cannot:
- Compute the run-scope idempotency key correctly (no `entry_version`)
- Determine which prior entries belong to *this* run vs. unrelated runs
- Skip already-replayed steps
- Resume at first unmaterialized step

## U-CP-56 partial-land

| AC | LAND/STRIKE |
|---|---|
| AC #1 (type surface materialized) | LAND |
| AC #2 (topology + engine-class validation) | LAND |
| AC #3 (workflow.start emission) | LAND |
| AC #4 (step iteration loop happy path) | LAND |
| AC #5 (lifecycle event filter — single-threaded-linear) | LAND |
| **AC #6 (replay-resumption read at re-entry)** | **STRUCK** pending fork resolution |
| AC #7 (terminal SUCCESS return) | LAND |
| AC #8 (failure-mode taxonomy) | LAND |
| AC #9 (determinism) | LAND |

**Weaker behavior shipped at PARTIAL-LAND:** save-point-checkpoint binding
emits `RESUMPTION` when ledger is non-genesis (no prefix match; any prior
workflow's entry triggers the emit). This satisfies the *emission-shape* wiring
but not the *selective-resumption* semantics. Test renamed from
`test_workflow_resumption_emitted_on_save_point_checkpoint_reentry` to
`test_resumption_emit_shape_wired_for_save_point_checkpoint` to reflect the
shipped behavior.

## Resolution paths

### Path A — Extend U-CP-13 `WorkflowManifestEntry` + add IS read primitive [RECOMMENDED]

CP plan v2.12 revision-pass:
- Extend `WorkflowManifestEntry` with `entry_version: int` (or `str`) field; CP
  spec v1.5 §6.1 amendment adds 11th field.
- Land a new IS unit (U-IS-NN) or extend U-IS-07 with a prefix-match read
  primitive (`read_entries_matching_prefix(prefix: bytes) -> Sequence[StateLedgerEntry]`).
- Re-author U-CP-56 AC #6 with full prefix-match + step-skip + resume.

**Pros:** matches the spec authority chain; foundational unit extension is
honest; cross-axis ripple bounded (entry_version is additive).

**Cons:** modifies LANDED U-CP-13 (cross-axis ripple — consumers must absorb);
needs IS-axis coordination if read primitive lands at IS.

### Path B — Author the resumption logic CP-internal without IS primitive [REJECTED]

Read full ledger via `read_ledger(ledger.handle)`, filter in CP by prefix in
memory. Skip step-by-step in driver.

**Pros:** no IS-axis coordination needed.

**Cons:** O(N) memory + filter per workflow start; defeats the F2-state-ledger-
backed-replay design intent at scale; not architecturally honest.

### Path C — Re-author AC #6 to weaker behavior [REJECTED]

Soften AC #6 in plan + spec to specify the weaker shipped behavior (any prior
entry → RESUMPTION).

**Pros:** no further code changes.

**Cons:** silent contract loosening; OD/runtime consumers that assumed selective
resumption break silently; per spec-writer no-extension discipline this would
be a spec extension (loosening the contract).

## Operator decision

**Path A recommended.** Sign-off via in-session AskUserQuestion at fork-filing
time (this filing, 2026-05-20).

## Provenance

- Spec source: `design-substrate/Spec_Control_Plane_v1_4.md` §25.6
- Plan source: `design-substrate/Implementation_Plan_Control_Plane_v2_11.md`
  U-CP-56 AC #6
- Discovery: advisor pushback during phase-7-implementation U-CP-56 land
  audit, 2026-05-20
- Predecessor session checkpoint: `~/.gstack/projects/arhugula-v2/checkpoints/
  20260520-035000-cp-workflow-driver-spec-gap-locked.md`
- Related fork: `.harness/class_1_tension_u_rt_44_workflow_loop_drain.md`
  (parent fork CLOSED-PARTIAL at Lane 6; this sub-fork was the residual.
  With this resolution, the parent's only remaining residual is
  `[[fork-u-od-21-span-cost-record-missing-rollup-keys]]`.)

---

## Resolution (2026-05-20)

**Path:** A-modified (operator-ratified at fork-u-cp-56-resumption-underspec
session 2026-05-20). Operator deviation from the fork as-filed: skip the
"add IS prefix-match primitive" second half; use N-lookup over the
existing `read_by_idempotency_key` primitive instead.

**Decisions ratified:**

1. **IS primitive:** A — N-lookup via existing `read_by_idempotency_key`
   (no new IS-axis surface).
2. **Reader composition:** A — new `LedgerReaderLike` Protocol on
   `DriverContext`, mirrors LedgerWriterLike/LifecycleEventEmitterLike
   separation.

**Landed:**

- CP plan v2.11 → v2.12 at `design-substrate/Implementation_Plan_Control_Plane_v2_12.md`.
- `WorkflowManifestEntry` grew 10 → 11 fields (`entry_version: int = 1`
  default; backward-compatible).
- `LedgerReaderLike` Protocol added to `harness_cp.workflow_driver`.
- `DriverContext` extended with `ledger_reader` field.
- Driver `_determine_resume_at()` helper added; AC #6 logic replaces the
  weaker non-genesis emit with selective per-run N-lookup.
- `LedgerReader` concrete added to `harness_runtime.lifecycle.state_ledger`
  + wired into bootstrap stage 1 IS + `HarnessContext`.

**Tests:**
- Renamed `test_resumption_emit_shape_wired_for_save_point_checkpoint` →
  `test_workflow_resumption_emitted_on_save_point_checkpoint_reentry`
  with full selective-resumption assertion.
- Added: `test_resumption_not_emitted_for_unrelated_prior_run`,
  `test_resumption_skips_already_replayed_steps`,
  `test_resume_at_advances_over_contiguous_prefix_only`,
  `test_entry_version_changes_idempotency_key_basis`.
- Added: 3 v2.12 manifest-entry tests.
- Updated: `test_harness_context_declares_all_c_rt_04_fields` (added
  `ledger_reader`), `test_freeze_raises_incomplete_when_required_field_none`
  (28 fields, was 27).

**Test totals at close:**
- CP: 505 (was 498; +7 v2.12).
- Runtime: 654 (unchanged from Lane 6).
- IS / AS / OD / Core: 125 / 302 / 599 / 18 (unchanged).
- pyright: zero regression on src (21 baseline preserved).
- ruff: zero regression.

**No spec bump rationale:** CP spec v1.4 §6.1 (verbatim from v1.2)
authorizes manifest carrier extension via "// ... additional per-workload
fields" clause. CP spec v1.4 §25.6 already cites
`manifest_entry.entry_version` in the hash composition formula. IS spec
v1.2 §7.4 enumerates `read_by_idempotency_key(key)` as an authorized
read primitive (already materialized at `LedgerNavigationPrimitive`).
Plan-only revision suffices.

---

## Audit reconciliation (2026-05-20)

**Verified status:** RESOLVED

**Resolving artifact / evidence:** Already labeled CLOSED 2026-05-20 (Path A-modified — WorkflowManifestEntry entry_version extended 10→11; LedgerReader Protocol added; CP v2.12 filed). Audit confirms.

**Audit context:** Workspace-wide tension-record audit 2026-05-20 (post-U-RT-52 merge to main at 2b945ab). 33 records reviewed against current code + spec state. Result: 28 RESOLVED, 5 DEFERRED-PARTITION, 0 STILL-OPEN. The 'Status' line earlier in this record predates the audit; this section is the current verified state.
