# Class 1 Fork — B-NONLINEAR-OVERRIDE-PROVENANCE (per-step override-ledger entry on non-linear topologies)

**Filed:** 2026-06-18 · R-FS-1 standalone `B-*` arc **B-NONLINEAR-OVERRIDE-PROVENANCE** (surfaced by the B4-Slice-4 out-of-family Codex review, registered at spine ledger `.harness/beyond-mvp-capability-boundary-ledger.md`; scoped honestly in CP spec v1.38 §6.6). Bundled-absorption posture: CP spec **v1.39 → v1.40** (C-CP-06 §6.6 topology-scope-note refresh) + `harness-cp/src` impl + by-execution tests. Class 1 (a design-substrate edit — the §6.6 note refresh — co-landing with impl). Design back-flow FULL-SPEC-pre-authorized (`[[feedback-full-spec-beyond-mvp-nothing-deferred]]`).

**Status:** ✅ RESOLVED + design decided — drives the impl. **NO operator gate.** This is **impl-to-cleared-spec** on the §6.6 provenance *contract* (general, never "linear only") + a `[[stale-carry-text-disposition]]` refresh of the v1.38 honest-scope *note*. It **sacrifices no committed invariant**, reuses the §16.5.4 idempotency-key formula verbatim, and is additive (absent override → byte-identical pre-arc behavior) → `[[feedback-gate-only-on-meaningful-architecture-change]]` says no gate. No nameable cross-domain tension (CP-axis driver-internal audit-emission) → advisor, **not council** (§10.9 discriminator applied). advisor-confirmed (Design A; advisor-not-council, no AUQ).

---

## §1 The gap — the per-step override-ledger entry was linear-only

The per-step override-application state-ledger entry (`action_id="cp.per-step-override-application"`, U-CP-14 §16.5) records that a step's per-step override was applied (model since v1.6 / prompt since v1.37 / role since v1.38). It is the **provenance** of a per-step override (CP spec §6.6 paragraph 1: the provenance is this entry, captured at `post_override_step_config = binding.model_dump(...)`, NOT the run-level §5.2 hash).

At HEAD it fired at **one** site — the `SINGLE_THREADED_LINEAR` per-step loop in `_execute_workflow_body` (`workflow_driver.py`, gated on `binding.override_applied`). The **5 non-linear strategies** (PARALLELIZATION / EVALUATOR_OPTIMIZER / ORCHESTRATOR_WORKERS / HIERARCHICAL_DELEGATION / DECENTRALIZED_HANDOFF) resolved the per-step binding (so the override **took effect at dispatch** on every topology — routing is correct everywhere) but emitted **no dedicated override-ledger entry**. CP spec v1.38 §6.6 disclosed this honestly as a pre-existing, all-topologies, all-dimensions audit-provenance gap and registered the closure as a forward item.

**Why pre-existing, not introduced by any one dimension:** the buffered-branch / concurrent-fan-out write boundary (ADR-F2 v1.2 single-threaded-write) precluded a synchronous per-worker override write from inside a concurrent branch — so no override dimension ever emitted on the non-linear paths.

---

## §2 Resolution — emit through the buffered-branch path (Design A)

CP spec v1.38 §6.6 named **both** valid closure mechanisms: "emitting the override entry **through the buffered-branch path / on the driver thread**." The arc adopts the **buffered-branch path**.

### §2.1 Design A (buffered-branch) vs Design B (driver-thread direct) — the decision

| Design | Shape | Verdict |
|---|---|---|
| **A — buffered-branch path** | New `append_branch_override_ledger_entry` buffers the override entry into the branch's `BufferingLedgerWriter`; `drain_branch_buffers` serializes it on the driver thread in branch-index order (the §25.13 step/terminal branch entries' discipline) | **CHOSEN.** |
| **B — driver-thread direct emission** | Emit via `ctx.cp_is_wiring.emit_override_state_ledger_entry` (real writer) on the driver thread, up-front before/after fan-out | REJECTED. |

**Decisive reason (advisor):** Design A is **thread-model-agnostic** — single-threaded-write + zero-tolerance timestamp-monotonicity are *inherited* from the buffer→drain discipline the whole non-linear path already runs on, regardless of what thread a branch executes on. Design B would require *proving*, per emission site, that the write is on the single write thread **and** outside any drain's capture→append window (the `drain_branch_buffers` docstring's named hazard: "a runtime audit / cost write interleaving between this drain's capture and its appends" → `NonMonotonicTimestampError`). B's LOC savings are real but trade a clean localized helper for a hidden per-site proof obligation.

### §2.2 Idempotency-key identity — the §16.5.4 per-`(step, outcome)` key, NOT branch-scoped

The override entry reuses the §16.5.4 idempotency-key 3-tuple `(workflow_id, step_id, sha256(outcome_canonical_bytes))` **verbatim** — *not* branch-scoped (unlike the §25.13 step/terminal branch entries, whose `compose_branch_path` scoping prevents the IS dedup from dropping a legitimately-repeated step *execution*).

Rationale: an override is a **static property of the resolved binding**, not a per-execution event. So a `(step, outcome)` repeated across non-linear iterations (EVALUATOR_OPTIMIZER re-dispatching `generate`) or recursion levels idempotently **dedups at the IS writer to one entry** — the spec's designed §16.5.4 semantic, and the property that makes override provenance **byte-shape-identical** across linear and non-linear (a consumer cannot tell which topology produced the entry). Branch-scoping the key would *change* the cleared §16.5.4 formula — an X-AL-3 spec change — and is foreclosed. Exercised explicitly by `test_evaluator_optimizer_repeated_step_override_dedups_to_one` (2 generate dispatches → exactly 1 persisted override entry).

### §2.3 The impl

1. **`compose_override_entry_payload`** factored out of the async `emit_override_state_ledger_entry` composer (`per_step_override_evaluator.py`) — the single source of truth for the override entry shape (action_id + §16.5.4 key + 5-field payload). Behavior-preserving (the async composer delegates to it; existing composer tests stay green).
2. **`append_branch_override_ledger_entry`** (`workflow_driver.py`) — composes via `compose_override_entry_payload` (buffer-time placeholder timestamp the drain re-stamps) and `branch_writer.append(...)`. WriteKey shape matches the linear path (`thread_id=workflow_id, step_id=step_id`).
3. **`_buffer_branch_override_if_applied`** — the shared guard (`binding.override_applied`) + `binding.model_dump(mode="json")` projection + actor derivation, wired at each strategy's branch-plan / sequential-dispatch site, **uniformly BEFORE dispatch** (matching the linear path, which emits the override before dispatch — so a failed/cancelled dispatch still records the resolution-time override fact; out-of-family Codex caught + corrected an earlier after-success placement on the orchestrator/handoff sites that lost the override on a failed dispatch):
   - PARALLELIZATION + ORCHESTRATOR_WORKERS workers — buffered in the branch-plan loop on the driver thread (the writer's first op, before fan-out spawns → no concurrent access; drains override-then-step in branch-index order). The fan-out FAILURE drain (`_drain_and_emit_step_boundaries`) persists the override even for a branch whose dispatch raised.
   - EVALUATOR_OPTIMIZER — buffered before each (re-)dispatch (sequential, driver thread; repeats dedup at the IS writer).
   - ORCHESTRATOR_WORKERS orchestrator step — binding resolved (pure) + override buffered before the dispatch try; the orchestrator-failure path drains `orchestrator_writer` so the override persists on a failed orchestrator dispatch.
   - DECENTRALIZED_HANDOFF stage — the stage writer joins `stage_writers` + the override is buffered before the dispatch try, so `_finish` (which drains `stage_writers` on every cascade-policy outcome) persists the override even for a failed stage.
   - HIERARCHICAL_DELEGATION inherits it — its recursion re-enters `_execute_orchestrator_workers`.

   An override-only writer (a step whose dispatch raised before buffering a step entry) does NOT inflate `workflow.step_count` / emit a spurious `STEP_BOUNDARY`: `_writer_ran_a_step` is hardened to require a present `branch_metadata` (the override entry carries `branch_metadata=None`) — advisor-caught.

### §2.4 Why no operator gate

The §6.6 **provenance contract** is general (never "linear only"); the v1.38 second paragraph was a present-tense **limitation disclosure** registered as a forward item. Closing it **fulfills** the contract — no committed-invariant sacrifice (contrast: v1.38's §14.5.3 invariant-2/3 *relaxation* was gated). The §16.5.4 key formula is reused verbatim; the behavior is additive. → adopt-and-note, advisor-confirmed, no AUQ (`[[feedback-gate-only-on-meaningful-architecture-change]]` + `[[enforce-floor-no-bypass-seam]]`-adjacent: a cleared-contract fulfillment, not an invariant change).

---

## §3 Verification

- `test_workflow_driver_nonlinear_override_provenance.py` — by-execution, per-topology, into the REAL IS writer (so §16.5.4 dedup + §6.3 chain re-verification are genuinely exercised): PARALLELIZATION (1 entry for 1 overridden branch; 2 for 2; 0 for none), EVALUATOR_OPTIMIZER (repeated-step → exactly 1), ORCHESTRATOR_WORKERS (orchestrator + worker → 2), HIERARCHICAL_DELEGATION (top-level worker + a nested-child-via-SUB_AGENT_DISPATCH worker), DECENTRALIZED_HANDOFF (stage → 1). Chain `verify_chain` VALID in every case.
- Full `harness-cp` suite green (no regression; existing topology suites use no per-step overrides → emission is a no-op for them).
- Refactor behavior-preserving: `test_override_state_ledger_emission.py` + `test_per_step_override_evaluator.py` + `test_procedural_tier_resolver_v1_30_apply.py` all green.
- **Covered-by-construction (advisor-noted, non-blocking):** the override tests run with `resolver=None` (R-003 `procedural_tier_snapshot_ref` omitted), so the resolver-*present* branch is proven for the override entry only by construction — its resolver threading (`_buffer_branch_override_if_applied` → `append_branch_override_ledger_entry` → `compose_override_entry_payload`) is IDENTICAL to the already-proven step-entry threading + the `run_bootstrap` resolver-present LINEAR override e2e (`test_cp_is_caller_site_integration.py`). A `run_bootstrap` non-linear+override+resolver e2e would close the intersection cell; low-risk (both factors independently proven), registered as an optional follow-up.

---

## §4 Disposition

- CP spec v1.39 → **v1.40** (§6.6 topology-scope-note refresh) + clearance `.harness/clearance/Spec_Control_Plane-v1_40-cleared-2026-06-18.md`.
- Spine ledger `B-NONLINEAR-OVERRIDE-PROVENANCE` → BUILT; arc-and-unit-map §5 standalone-arcs panel: closed +1 / remaining −1.
- Decorrelated review: advisor (Design A; idempotency identity; §6.6 note disposition) + out-of-family Codex (pending at the impl-diff PR).
