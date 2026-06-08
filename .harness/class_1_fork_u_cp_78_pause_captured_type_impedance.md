# Class 1 (halt-execution) — U-CP-78 `pause-captured` composer type impedance

**Filed at:** R-CXA-2 producer-seam design arc (2026-06-08), HEAD `7ae493d`
**Locus:** `harness-cp/src/harness_cp/pause_resume_protocol.py:864` (`emit_pause_captured_state_ledger_entry`) vs the engine-layer producer `capture_pause_snapshot` (`:252`)
**Status:** **OPEN — surfaced, recommended reading attached, NOT resolved (X-AL-3: do not pick a reading in-spec without ratification).**
**Routing:** CP-axis design-phase (CP spec §16.5 / C-CP-22 / C-CP-26) — choose the type-seam reading, then cascade to runtime plan producer arc.
**Parent lineage:** `class_1_tension_u_rt_35_cp_is_wiring_gaps.md` (CLOSED; this is a firing-site-layer continuation per its line-355 re-verifiability clause). Companion design brief: `r-cxa-1-2-producer-seam-spec.md` §4.6.
**Precedent:** `[[carrier-home-defect-pattern]]` (cross-axis type seam) · `[[halt-route-split-ac-pattern]]` · v2.34 AC #8 disambiguator-availability flag.

## The defect

The U-CP-78 engine-layer composer:

```python
async def emit_pause_captured_state_ledger_entry(
    *, workflow_id, step_id, pause_event_id,
    pause_snapshot: PauseSnapshot,   # <-- WORKFLOW-layer type (C-CP-26)
    actor, ...
) -> WriteResult                      # pause_resume_protocol.py:864
```

consumes **`PauseSnapshot`** — the **workflow-layer** 8-field type (`pause_resume_protocol_types.py:92`; fields: `workflow_id, run_id, step_index, pause_reason: WorkflowPauseReason, state_summary, snapshot_hash, created_at, state_ledger_anchor`).

Its docstring (`:883`) says it "Fires AFTER `capture_pause_snapshot(...)` at line 106 returns the `PauseSnapshot` and BEFORE the snapshot returns to the caller" — and is labelled the **engine-layer** composer (U-CP-49, `cp.pause-captured`). But the engine-layer producer it names is the **free function**:

```python
def capture_pause_snapshot(workflow_id: WorkflowID, pause_reason: PauseReason) -> PauseEvent  # :252
```

which returns **`PauseEvent`** — the **engine-layer** 5-field type (`pause_resume_protocol.py:59`; fields: `paused_at, pause_reason: PauseReason, state_summary_snapshot, external_refs_captured, pause_audit_entry_id`). `PauseEvent` has **no** `snapshot_hash`, `run_id`, `step_index`, or `state_ledger_anchor`; its `pause_reason` is the engine-layer `PauseReason` enum, not the workflow-layer `WorkflowPauseReason`.

**Net:** a real engine recovery-loop producer that calls the engine free function `capture_pause_snapshot()` receives a `PauseEvent` and **cannot feed it to `emit_pause_captured_state_ledger_entry()` (which requires a `PauseSnapshot`) without a type adaptation that does not exist at HEAD.** Synthesizing a `PauseSnapshot` from a `PauseEvent` at the runtime axis would invent `snapshot_hash` / `state_ledger_anchor` / `run_id` / `step_index` values not present in the engine surface — exactly the X-AL-3 silent design extension the v2.34 AC #8 flag forbids.

## Asymmetry (why this is `pause-captured`-specific)

The sibling U-CP-79 composer `emit_resume_attempted_state_ledger_entry(..., resume_outcome: ResumeOutcome, ...)` (`:967`) consumes **`ResumeOutcome`** — the **engine-layer** type (`:104`) that the engine free function `attempt_resume(attempt) -> ResumeOutcome` (`:272`) actually returns. **No impedance.** The defect is isolated to `pause-captured` consuming the *workflow-layer* `PauseSnapshot` while its named producer emits the *engine-layer* `PauseEvent`.

## How this arose (provenance, not blame)

U-CP-78 landed at PR #43 (`a815ac9`) in the Cluster-A composer-library arc. The composer was authored against `PauseSnapshot` (the richer, hashed workflow-layer envelope) — sensible in isolation (it has a `snapshot_hash` ideal for an idempotency suffix). The engine free function `capture_pause_snapshot` returning `PauseEvent` predates it (U-CP-49). The two were never reconciled because **no producer ever wired them together** — the firing-site absence masked the type seam until a producer was actually specced (this arc).

## Candidate readings (operator decision pending)

### Reading A — change the composer input type to `PauseEvent` (engine-layer alignment)
Re-type `emit_pause_captured_state_ledger_entry(..., pause_event: PauseEvent, ...)`; re-derive the idempotency suffix from `PauseEvent` canonical bytes + `pause_audit_entry_id` (instead of `snapshot_hash`). Aligns the engine-layer composer with the engine-layer producer.
- Blast radius: small (one composer signature + its idempotency-key segment + its tests). CP spec §16.5.4/§16.5.5 row U-CP-49 outcome-bytes recipe re-stated for `PauseEvent`.
- Defect risk: low — matches the layer label ("engine-layer") to the actual engine producer type.
- **Recommended** — the composer is *labelled* engine-layer; its input type should be the engine-layer type its named producer emits.

### Reading B — engine recovery loop produces a `PauseSnapshot`
Require the DP-2 engine recovery loop to construct a workflow-layer `PauseSnapshot` (computing `snapshot_hash` + `state_ledger_anchor`) rather than calling the engine free function. Collapses the engine free-function surface in favor of the workflow-layer `PauseResumeProtocol.capture_pause_snapshot` everywhere.
- Blast radius: medium-large — questions whether the engine-layer free-function surface should exist at all (potential C-CP-22 vs C-CP-26 layer-collapse, which the spec deliberately keeps distinct per §26 NEW NOTE).
- Defect risk: medium — risks erasing the deliberate two-layer distinction.

### Reading C — define an explicit `PauseEvent -> PauseSnapshot` adapter
Author a CP-axis adapter that lifts a `PauseEvent` into a `PauseSnapshot` (minting `snapshot_hash` from the `PauseEvent` canonical bytes, mapping `PauseReason -> WorkflowPauseReason`, sourcing `state_ledger_anchor` from the recovery loop's ledger handle).
- Blast radius: medium — a new typed adapter + the `PauseReason -> WorkflowPauseReason` mapping must be authored (the two enums are NOT 1:1; `ENGINE_NATIVE_PAUSE` has no workflow-layer twin).
- Defect risk: medium — the enum mapping is itself a design decision (and a place to silently lose information).

## Recommendation

**Reading A.** Smallest blast radius; restores the engine-layer composer ↔ engine-layer producer type coherence the "engine-layer" label already asserts; preserves the deliberate C-CP-22/C-CP-26 two-layer distinction (no layer-collapse); avoids authoring a lossy enum-mapping adapter. The `snapshot_hash`-based idempotency suffix is replaced by a `PauseEvent`-canonical-bytes suffix — equivalent dedup strength.

## Acceptance criterion (on ratification)
- Composer input type matches the type its production producer emits.
- A `test_pause_captured_consumes_real_engine_output` proves the engine free-function output flows into the composer without runtime-axis field synthesis.
- C-CP-22 / C-CP-26 layer distinction preserved (no `PauseReason`/`WorkflowPauseReason` collapse).

## Cross-axis observability
Resolution of this fork is a **precondition** for the R-CXA-2 engine-layer producer (design brief §4.7 AC #3). It composes with — but is independent of — DP-2 (engine recovery-loop ownership) and DP-3 (disambiguator derivation) at `class_2_fork_r_cxa_2_producer_loop_ownership.md`. Closure-back-reference owed here at ratification.
