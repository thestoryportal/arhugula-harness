# Arc-open design — `B-FANOUT-CRASH-RESUME-MAYBE-RAN-SUBAGENT` (R-FS-1)

> **⚠️ SUPERSEDED IN PART (2026-06-26) — historical #746 checkpoint, landed for provenance.** This was authored at the #746 arc-open and left UNTRACKED after that branch was reverted. The CURRENT head record is `.harness/b-fanout-crash-resume-maybe-ran-subagent-design-finding-v2.md` (+ finding-v1). What still stands: the §"capability gap" / §"load-bearing blocker" / §"three pre-code verifications" / the deterministic-child-identity mechanism (prerequisite #1) + the "corrected decomposition" (the two prerequisites). What is STALE: the "⏩ Branch state" section (the `feat/b-fanout-maybe-ran-subagent` branch was REVERTED — not merged), its tally (`48 closed / 6 forward` is #746-era; current is 55/4 + the newly-registered `B-CHILD-CRASH-RESUME-FINAL-STATE-RECONSTRUCT`), and the `…-NONREPLAY-CHILD` decompose (the real blocker is final_state-reconstruction, not non-replay-child — finding v2). The arc-ledger.yaml is the SoT for counts, NOT this doc.*

*Durable design checkpoint authored 2026-06-25 at arc-open. Advisor-vetted (full-transcript). Resumable: if context runs out, the next loop iteration resumes from this note + the committed impl.*

## 🛑 ARC BLOCKED — does NOT close (2026-06-25, Codex round 2 + advisor)

**The arc is deeper than the roadmap assumed. DO NOT merge `feat/b-fanout-maybe-ran-subagent` as-is — it ships result corruption.**

**Codex round 2 [P1] (verified real):** the recovery makes child *effects* at-most-once (auto-resume skips committed steps) but the child's `RunResult.final_state` is rebuilt ONLY from new-envelope-executed steps (`accumulated` at `workflow_driver.py:3165` init empty, `:3851` populated per executed step; recovered prefix steps are rehydrated into the inter-step CHANNEL but NOT into `accumulated`). So a resumed child returns suffix-only/EMPTY `final_state` → the parent folds corrupted branch output. The empty case (child committed ALL steps before the parent crashed) is the CENTRAL maybe-ran scenario, not an edge.

**Not safe to land the infra alone either:** the deterministic child run_id makes ANY re-dispatch (fan-out maybe-ran OR linear-parent resume) auto-resume the child → the SAME final_state corruption. There is no vacuous-but-safe subset.

**Pre-existing (verified):** `accumulated` is never seeded from the store → EVERY resumed workflow returns suffix-only `final_state`, including the existing B-HIERARCHICAL-PAUSE captured-child-resume fold. A latent defect in cleared code — filed as a Class-3 note (`.harness/class_3_*child_resume_final_state*.md`).

### Corrected decomposition (advisor-vetted) — TWO prerequisites, ONE built

The maybe-ran SUB_AGENT_DISPATCH recovery needs BOTH:
1. **Deterministic child identity** (built on this branch) — makes the child auto-resumable across a parent crash.
2. **Child-`final_state`-reconstruction** (NOT built — the blocking prerequisite) — seed `accumulated` from the recovered store outputs (`read_outputs`, already read by `_rehydrate_replay_prefix`) on auto-resume so a resumed child returns its FULL `final_state`. This is an all-workflows crash-resume change → needs its own witness (resumed-linear `final_state` == no-crash run) + its own Codex round. Advisor conditions to confirm at its arc-open: (a) no runtime-spec clause specifies suffix-only resume `final_state`; (b) no existing test depends on suffix-only; (c) `read_outputs` holds the recovered prefix for BOTH WAL_SEGMENT + EVENT_SOURCED_REPLAY.

**Next cycle:** build prerequisite #2 (the child-`final_state`-reconstruction arc) FIRST — its own design-first cycle (witness + Codex) — then the SUB_AGENT recovery (the classifier disjunct + the deterministic identity) closes on top, gated on replay-capable BOTH dispatch + resumed (the round-1 [P1] fix, already on the branch). The branch's impl (deterministic identity + replay marker + classifier disjunct + the round-1 resumed-replay fix) is a durable BASIS to reuse once #2 lands — but is NOT mergeable until then.

---

## ⏩ Branch state (durable basis, NOT mergeable) — `feat/b-fanout-maybe-ran-subagent`, 9 commits

**DONE + committed (all green, pyright 0/0/0):**
- Impl: runtime deterministic child run_id (`child_workflow_runner.py` + `sub_agent_dispatch.py` `compose_child_run_id_seed` + the C-RT-17 Protocol kwarg) + store `child_replay_capable` marker/reader (`engine_output_store.py`) + CP `_subagent_child_replay_capable` extractor + `_fence_unrecoverable_maybe_ran_indices` SUB_AGENT disjunct + both consume sites. Test mocks updated.
- Witnesses (11): runtime deterministic-seed (4, `test_lifecycle_sub_agent_dispatch.py`) + CP classifier recovery decision both directions (7, `test_workflow_driver_fanout_output_replay.py`). CP 1317 + runtime 2108 green.
- Spec deltas: CP v1.67 (`Spec_Control_Plane_v1_67.md`) + runtime v1.82 (prepended to `Spec_Harness_Runtime_v1.md`).
- Clearance: CP v1.67 + runtime v1.82 markers.
- arc-ledger: SUBAGENT flipped closed + NONREPLAY-CHILD registered (tally 48 closed / 6 forward — `tools/arc_ledger.py --check` PASSES). Spine updated.

**REMAINING (next turn / on codex notification):**
1. **Codex review** — `codex review --base main` running in background (task bltms33gq); address any P1/P2 at-most-once findings (the family's pattern — expect ≥1 round).
2. **advisor() pre-done** sanity.
3. **PR** — `gh pr create` (branch is bundled CP+runtime + design-substrate w/ clearance markers → X-AL-3 guard passes). Title must NOT use the `ops: roadmap status refresh` prefix (substantive).
4. **Post-merge §12.2 refresh** — roadmap_status.md + roadmap.html regen (`tools/dashboard/generate.py`) + hash bump, as a SEPARATE terminating-refresh PR.

**KEY at-most-once facts for codex-finding triage:** recovery gated on the DISPATCH-TIME `child_replay_capable` marker (changed-manifest guard); non-replay/changed-kind/out-of-range fail closed; the deterministic seed re-derives from the STABLE `parent_idempotency_key` across crash-resume; child-workflow-id swap = accepted parity (per-child at-most-once). The one full-chain integration witness (real parent crash → re-dispatch → child auto-resume) is NOT yet written — the layered witnesses (seed determinism + classifier decision + existing child crash-resume coverage) cover it; consider adding the integration witness if codex/advisor flags the composition as under-proven.

## The capability gap

A fan-out branch that is a **SUB_AGENT_DISPATCH worker** which crashes after dispatch but before terminal/pause capture is "maybe-ran". Today it **fails closed** (`_fence_unrecoverable_maybe_ran_indices`, `workflow_driver.py:802-854`: SUB_AGENT_DISPATCH is neither in `_FANOUT_MAYBE_RAN_REFIRE_SAFE_KIND_VALUES={DECLARATIVE,INFERENCE}` nor `_FANOUT_MAYBE_RAN_FENCE_RECOVERABLE_KIND_VALUES={TOOL_STEP}`).

Unlike TOOL_STEP (fenced at its own sink, #742) or MANAGED_AGENTS (unfenced vendor sink → separate `…-UNFENCED-EXTERNAL` arc), a SUB_AGENT_DISPATCH worker is **READ_ONLY at the parent gate**; its only external effects live at the **child's tool sinks**, each independently fenced (C-RT-31 §14.22). So at-most-once is **compositional**: the parent delegates to the child's *own* crash-resume, which recursively re-applies the same classifier (child TOOL_STEP→fence, INFERENCE/DECLARATIVE→re-fire-safe, child SUB_AGENT_DISPATCH→recurse, child MANAGED_AGENTS→fail-closed). The parent never sees inside the child.

## The load-bearing blocker (verified)

`child_workflow_runner.py:153-155`: on a **first dispatch** the child gets a fresh transient `uuid.uuid4().hex` run_id. The child's `run_idempotency_key = sha256(run_id, workflow_id, …)` derives from it → the child's durable store + fence reserves are keyed on a **transient identity lost when the parent crashes** → re-dispatching fresh re-runs the child from scratch under a *new* uuid → **every child tool effect double-fires**. That is exactly why maybe-ran SUB_AGENT_DISPATCH must currently fail closed.

## Three pre-code verifications (all resolved)

- **V1 (child auto-resumes from durable shared store):** YES. `execute_workflow` auto-resumes from `_fanout_replay_store(ctx, manifest_entry)` keyed on `run_idempotency_key` (`workflow_driver.py:2109-2503`) with NO explicit snapshot; the child shares that durable store via `ctx` and it survives a crash under `_FANOUT_REPLAY_ENGINE_CLASSES`. The ONLY blocker is the transient child key.
- **V2 (replay-capable-child guard — REQUIRED, not optional):** A maybe-ran SUB_AGENT_DISPATCH worker whose **child manifest declares a non-replay engine class** has no child crash-resume → must STAY fail-closed. Record child replay-capability per branch in the dispatch marker (mirroring `dispatched_branch_kinds`); the CP classifier reads it.
- **V3 (does child_run_id reach a committed hash → mechanism choice):** `_compute_snapshot_hash` includes `run_id` (`pause_resume_protocol.py:655`) but it is a **within-run** integrity hash (validated at resume over the snapshot's own run_id), NOT a cross-version invariant. Deterministic-derive is **hash-safe** and is the chosen mechanism (re-derivable on resume → no crash window for the key; preferred over persist-uuid-in-marker which needs a durable pre-effect write).

## The build (bundled CP + runtime — like #736/#740)

1. **Runtime — deterministic child run identity** (`child_workflow_runner.py` + C-RT-17 §14.7.4 Protocol signature, runtime spec delta). On first dispatch derive `child_run_id = sha256(parent_run_idempotency_key, branch_index, step_id, child_workflow_id)` instead of a uuid. On resume (`pause_snapshot_input` non-None) keep reusing `snapshot.run_id` VERBATIM. Thread the discriminators down via the Protocol. Now a plain re-dispatch of a maybe-ran SUB_AGENT_DISPATCH worker **auto-recovers the child** (its `execute_workflow` auto-resumes from the durable store under the re-derived key) — no child_resume_snapshot needed.
2. **CP — record child replay-capability in the dispatch marker** (V2 guard) at dispatch, when the child manifest is available.
3. **CP — relax the maybe-ran classifier** (`_fence_unrecoverable_maybe_ran_indices` / a parallel SUB_AGENT classifier, CP spec delta): a maybe-ran SUB_AGENT_DISPATCH worker whose marker says child-replay-capable is **re-dispatchable** (recovers compositionally via deterministic key + child auto-resume); non-replay-capable child stays fail-closed.
4. **By-execution witnesses (both base-case directions per advisor):** (a) a grandchild TOOL_STEP effect fenced+recovered across a **real** parent crash → resume; (b) a child MANAGED_AGENTS unfenced effect correctly **failing closed at the child level** and propagating up. If (b) fail-closes, the unfenced-grandchild case is *handled*, not a residual.

## Decompose-at-open (honest, net-zero like #744)

- **CLOSE:** maybe-ran SUB_AGENT_DISPATCH recovery for **replay-capable** children (whole capability + both witnesses).
- **REGISTER (genuinely distinct, per V2):** `B-FANOUT-CRASH-RESUME-MAYBE-RAN-SUBAGENT-NONREPLAY-CHILD` — recovering a maybe-ran sub-agent worker whose child declares a **non-replay** engine class needs a different durable mechanism (eager child snapshot at dispatch / forced durable child engine). Stays fail-closed here.

## Implementation layering (resolved at arc-open)

- **Deterministic child key — composer-side, no marker.** Compute in the runtime composer (`sub_agent_dispatch.py`, which has `step_context` + `payload`) as `sha256(step_context.parent_idempotency_key, step_context.branch_index, step_context.step_index, payload.child_workflow_id)`; pass to the runner via ONE additive Protocol kwarg (e.g. `child_run_id_seed: str | None = None`). Runner: `child_run_id = pause_snapshot_input.run_id if pause_snapshot_input else (child_run_id_seed if child_run_id_seed is not None else uuid.uuid4().hex)` (uuid fallback preserves byte-compat for callers not passing the seed). Re-derived identically on re-dispatch (same step_context) → child auto-resumes. **Verify at build:** step_context reconstructed identically at resume; collision-free for the DAG (branch_index + step_index discriminate).
- **V2 child-replay-capability marker — runtime-composer-records (NOT CP).** `step_payload` is OPAQUE to the CP driver (`workflow_driver_types.py:110-118`); harness-cp does not import the runtime payload type. So the CP classifier cannot read the child engine class. The composer records `child_replay_capable` (= `payload.child_manifest_entry.engine_class in _FANOUT_REPLAY_ENGINE_CLASSES`) to the shared store durably BEFORE invoking the child runner, keyed by the parent run key + branch_index (mirroring `record_branch_dispatched`, `workflow_driver.py:925`). Crash-safe: record-absent → CP classifier fails closed. **Verify at build:** that `step_context.parent_idempotency_key` equals the marker's `run_idempotency_key` (the parent RUN key) — if not, thread the run key to the composer or have the parent record it.
- **CP classifier relaxation** reads the new marker: a maybe-ran SUB_AGENT_DISPATCH worker is recoverable iff `child_replay_capable` recorded True (dispatch-time value — the changed-manifest guard); else fail closed.

## Build sequence (next iteration resumes here)

1. Runtime: `child_workflow_runner.py` deterministic key + Protocol kwarg + `sub_agent_dispatch.py` composer (compute key + record replay-capability) + runtime spec delta (C-RT-17 §14.7.4) + clearance marker.
2. CP: marker reader + `_fence_unrecoverable_maybe_ran_indices` relaxation (or parallel SUB_AGENT classifier) + CP spec delta + clearance marker.
3. By-execution witnesses (both directions per advisor).
4. arc-ledger (close 1 + register `…-NONREPLAY-CHILD` → net-zero) + spine + dashboard regen.
5. Adversarial review + Codex convergence + advisor pre-done → PR + §12.2.1 refresh.

## At-most-once invariants preserved

- Per-branch key-bind unchanged; ABORT stays run-level-terminal; absent resolution re-pauses INERT.
- Deterministic child key is collision-free for the DAG case (branch_index discriminates fan-out, step_id discriminates within-workflow); existing durable snapshots resume via stored uuid (resume path unchanged).
- Non-replay child → fail closed (V2). Child MANAGED_AGENTS → fail closed at child level (recursion bottoms out).
