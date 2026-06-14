# Adversarial Review — U-CP-90 DECENTRALIZED_HANDOFF (R-FS-1 arc #16, B1-impl-10)

## Summary

- **Mode:** Phase-7 pre-merge implementation review (red-team of a Phase-7 impl arc against the cleared CP spec/plan).
- **Artifact reviewed:** branch `r-fs-1-arc-16-decentralized-handoff` @ HEAD `13c447a` — `git diff main...HEAD` (6 files, +1040/-45):
  - `harness-cp/src/harness_cp/workflow_driver.py` (+304/-5 — `_execute_decentralized_handoff`, `_compose_handoff_to_next`, `_handoff_record`; dispatch-table entry).
  - `harness-cp/tests/test_workflow_driver_decentralized_handoff.py` (NEW, 13 tests).
  - `harness-cp/tests/{test_workflow_driver.py, test_workflow_driver_branch_substrate.py, test_workflow_driver_envelope.py}` (repoints).
  - `harness-runtime/tests/integration/test_u_cp_90_decentralized_handoff_live_e2e.py` (NEW, live Ollama e2e).
- **Date:** 2026-06-14.
- **Taxonomy disambiguation (per skill title-section + advisor #4).** The caller requested a "Class 1 (blocking) / Class 2 (operator-decision) / Class 3 (informational)" structure — that is the **§2.7.6 Phase-7 execution-fork** scale, NOT the skill's §4.1 review-severity scale. **This report uses the §2.7.6 execution-fork scale as requested** (Class 1 = halt-execution/blocking; Class 2 = in-execution operator decision; Class 3 = informational). I flag this explicitly so no reader mis-maps a §2.7.6-Class-3 (informational) onto a §4.1-Class-3 (severe).
- **Finding count:** Class 1 (blocking): **0** · Class 2 (operator-decision): **0** · Class 3 (informational): **3**.
- **Highest-severity finding:** F3-01 (stage-0 synthetic anchor vs IS §5.4 prose) — informational; precedent-consistent with the cleared PARALLELIZATION strategy.
- **Verdict: APPROVE.** (No blocking finding; no operator decision required. The 3 Class-3 items are doc/transparency notes, foldable into a future CP touch — not merge gates.) The headline non-hollow claim is empirically verified; the advisor's live-e2e tripwire genuinely passes; every AC atom is genuinely (not grep-) met.

---

## What I verified as the headline (the non-hollow claim — verified by execution)

The arc's headline is "the persisted ledger distinguishes DECENTRALIZED_HANDOFF from BOTH EVALUATOR_OPTIMIZER (no `branch_metadata`) and ORCHESTRATOR_WORKERS (a STAR) — here it CHAINS." I attacked this hard and it holds:

- **vs EVALUATOR_OPTIMIZER (no `branch_metadata`).** Confirmed at source: EVALUATOR_OPTIMIZER uses `_append_buffered_sequential_entry` (`workflow_driver.py:2759`, docstring "NO branch_metadata … the carrier stays the default `None`"), while DECENTRALIZED_HANDOFF uses `append_branch_step_ledger_entry`/`append_branch_terminal_ledger_entry` which always `compose_branch_metadata`. Genuinely a persisted distinction, not prose.
- **vs ORCHESTRATOR_WORKERS (a STAR).** Confirmed at source: ORCHESTRATOR_WORKERS sets every worker's `branch_metadata.parent_action_id` to the ONE `orchestrator_action_id` (`workflow_driver.py:3183`). DECENTRALIZED_HANDOFF chains: `prev_action_id = this_action_id` per stage (`workflow_driver.py:3939`).
- **Empirical chain proof (simulated the 3-stage chain directly):**
  - stage 0 `branch_metadata.parent_action_id = workflow:wf-dh:step:0`; stage 1's = stage 0's step `action_id`; stage 2's = stage 1's step `action_id`. The 3 parents are all DISTINCT (a star would repeat one).
  - 6/6 distinct `action_id`s, 6/6 distinct idempotency keys for a 3-stage run → **no C-IS-07 §7.5 dedup collapse** → 6 persisted entries (3 step + 3 terminal).
  - On the **REAL** IS writer (`test_decentralized_handoff_live_real_ledger_chain_valid`, re-run by me): 6 entries, `verify_chain` = `VALID`, parents distinct.
- **Live e2e tripwire (the advisor's hardest gate) GENUINELY PASSES.** Ran `pytest harness-runtime/.../test_u_cp_90_decentralized_handoff_live_e2e.py` → `1 passed in 13.54s` with a real Ollama call at each of 3 stages, asserting `status=="completed"` AND `"ollama" in provider_names`. No deadlock, no `SUB_AGENT_DISPATCH` reach. The U-CP-89 hierarchical e2e deadlocks on the sub-agent bridge; this one does not — the `HandoffContext` being a RECORD (never a dispatch) is the load-bearing design decision and it is honored. The model is correct.

---

## Class 1 findings (blocking — halt-execution per §2.7.6)

**None.** No architectural defect, no spec contradiction requiring halt, no X-AL-3 silent design extension, no concurrency/idempotency hole, no silent effect loss. The headline claim is non-hollow.

---

## Class 2 findings (in-execution operator decision per §2.7.6)

**None.** Every fork in this arc (sync-vs-TaskGroup, cascade degeneracy, stage-0 anchor) is resolvable from the cleared spec + cleared-sibling precedent without an operator decision. No credential/irreversible/outward-facing step is involved.

---

## Class 3 findings (informational per §2.7.6)

### F3-01 — Stage-0 `branch_metadata.parent_action_id` is a synthetic, NON-persisted `action_id` (IS §5.4 prose says it "resolves to a prior persisted entry")
- **Decision-claim:** *decided* (the fact is unambiguous); the *disposition* is informational.
- **Location:** `harness-cp/src/harness_cp/workflow_driver.py:3819` (`prev_action_id = f"workflow:{workflow_id}:step:0"`) feeding `compose_branch_metadata` at stage 0. Spec: `design-substrate/Spec_Information_Substrate_v1.md:485` (§5.4 `BranchMetadata.parent_action_id` constraint: *"Resolves to a prior persisted entry's `action_id`"*).
- **Defect:** For stage 0, `branch_metadata.parent_action_id = "workflow:{wf}:step:0"`, but **no ledger entry with that `action_id` is ever persisted** by this strategy (the first persisted entry is `...:step:0:branch:0:step:0`). The audit ancestry graph therefore has a **dangling root** at stage 0 — the §5.4 prose "resolves to a prior persisted entry" is not literally satisfied for the chain root. Stages 1+ resolve correctly (each parent IS a persisted prior step `action_id`).
- **Evidence by execution:** I ran the strategy on the real IS writer and dumped action_ids + parents:
  ```
  PERSISTED action_ids: workflow:wf-dh:step:0:branch:0:step:0  (+terminal)  …:branch:0:step:0:branch:0:step:0  …
  ALL branch parents:   ['workflow:wf-dh:step:0', '…:branch:0:step:0', '…:branch:0:step:0:branch:0:step:0']
  stage-0 anchor 'workflow:wf-dh:step:0' IS PERSISTED?  False
  UNRESOLVED parents (not a persisted action_id): ['workflow:wf-dh:step:0']
  verify_chain: valid
  ```
- **Why this is informational, not blocking (the discriminator — precedent-consistency + non-enforcement):**
  1. **It is precedent-consistent with the already-CLEARED PARALLELIZATION strategy (U-CP-86).** I ran PARALLELIZATION on the real writer: its branches' `parent_action_id = workflow:{wf}:fanout`, which is **also never persisted** (`UNRESOLVED parents: ['workflow:wf-p:fanout']`). So the synthetic-root pattern is not introduced by this arc — a cleared sibling already does it. (ORCHESTRATOR_WORKERS/HIERARCHICAL_DELEGATION differ only because they have a *real* orchestrator step that IS persisted at `workflow:{wf}:step:0`, line 3220.)
  2. **The §5.4 constraint is NOT chain-enforced.** `verify_chain` returns `VALID` in every case — the "resolves to a prior persisted entry" line is audit-ancestry-graph prose, not a hash-chain or writer-enforced invariant. Nothing rejects a dangling root.
- **Resolution path (informational):** EITHER (a) accept as the established synthetic-fan-out-root convention shared with PARALLELIZATION and add a one-line reciprocal note where the §5.4 prose lives (a future CP/IS doc-hygiene touch — same class as the existing §5.4 line-497 "Class 3 informational doc-coordination" item), OR (b) if the design intends every branch root to resolve to a persisted entry, that is a cross-strategy spec clarification owed at PARALLELIZATION + DECENTRALIZED_HANDOFF together — a design-substrate touch, NOT a single-arc fix. Either way it does not block this merge. (Pattern checklist #6 spec-prose-vs-impl-body; #2 sibling-spec staleness.)

### F3-02 — Synchronous (no `TaskGroup`/`gather`) execution diverges from the §25.11 "Common substrate (all 5 non-linear strategies)" concurrency line — but is faithful to "single-owner-at-a-time"
- **Decision-claim:** *decided* (faithful; surface for transparency).
- **Location:** `workflow_driver.py:3841` (`for stage_index, step in enumerate(steps):` — a plain synchronous loop on the driver thread, no `to_thread`/`TaskGroup`/`gather`). Spec: `Spec_Control_Plane_v1_32.md:58` (§25.11 common substrate "Concurrency. `asyncio.TaskGroup` … or `asyncio.gather` … over branches") + line 60 ("Append discipline. The buffered/deferred-append path (§25.12), never the inline per-step append").
- **Defect (apparent):** The §25.11 common-substrate prose says all 5 non-linear strategies use `TaskGroup`/`gather` concurrency over branches; this strategy runs purely sequentially with no async barrier.
- **Why it is faithful, not a deviation (the discriminator):**
  1. The §25.11 DECENTRALIZED_HANDOFF row itself says **"Single-owner-at-a-time … Sequential ownership transfer"** (`Spec_Control_Plane_v1_32.md:68`). Single-owner has, by definition, no concurrent siblings to fan out — so `TaskGroup`/`gather` would be vacuous machinery. The concurrency prose is a substrate *affordance* for the fan-out patterns, not a per-strategy mandate.
  2. **The load-bearing half of the common substrate IS honored:** §25.12 D1.b (buffered/deferred-append, NEVER the inline linear append) is honored — the strategy uses `BufferingLedgerWriter` + `append_branch_*_ledger_entry` + `_drain_and_emit_step_boundaries` (`workflow_driver.py:3814,3866,3908,3826`), not the linear `_append_step_ledger_entry`. §25.15.2 obl. 8 (structured cancellation) targets not-yet-dispatched *siblings* — single-owner has none → vacuous. So no obligation is dropped.
  3. The cleared EVALUATOR_OPTIMIZER strategy (U-CP-87) is also sequential on the driver thread (`_dispatch_and_buffer`, no `to_thread`) — sequential-when-the-semantic-is-sequential is established cleared precedent.
- **Resolution path (informational):** no change owed; the sync impl is the correct reading of "single-owner-at-a-time." Optionally a future §25.11-prose touch could scope the "Concurrency: TaskGroup/gather" line to "the fan-out patterns" to remove the apparent-divergence read. Non-blocking.

### F3-03 — "cascade-cancel (U-CP-85) applies on stage failure" + the recursively-NESTED `action_id` are both grep-met-shaped surfaces that resolve cleanly on inspection
- **Decision-claim:** *decided* (both clean; named for transparency per FM-G smoothing-avoidance).
- **Location (a) cascade-cancel:** `workflow_driver.py:3877-3905` (the `except Exception` cascade block) + plan AC `Implementation_Plan_Control_Plane_v2_32.md:249` ("`cascade-cancel` (U-CP-85) applies on stage failure").
- **Location (b) nested action_id:** `workflow_driver_types.py:366` (`{parent_action_id}:branch:{branch_index}:step:{local_step_index}`) recursing per the chain.
- **(a) cascade-cancel disposition (the honest read):** For single-owner there is never a concurrent in-flight sibling to cancel, so U-CP-85's `cascade_cancel_barrier` / `TaskGroup` cancellation machinery is **structurally unreachable** here. The impl satisfies the AC at the **run-level-status** layer only: `cascade-cancel` (MTC tier) → the `else` branch → `RunStatus.FAILED` with the completed prefix persisted and the failed/later stages not persisted (verified by `test_decentralized_handoff_cascade_cancel_on_stage_failure_fails` — `disp.order == ["s0","s1"]`, only `s0`'s step entry persisted). This is the **correct degenerate reading** per the §25.11 row ("cascade_policy typically cascade-cancel, single-owner") and §25.15.2 obl. 6 (cascade-cancel → FAILED). The `proceed` → PARTIAL (salvage prefix) and `pause` → honest FAILED + `decentralized-handoff-pause-resume-not-yet-materialized` paths are genuinely implemented + tested (not faked PAUSED) — that honesty is a positive. **"Proceed stops the chain" is the right reading:** there is NO inter-step data flow (B-INTERSTEP), and a failed owner cannot hand off, so continuing past a failed stage would require fabricating a handoff — correctly foreclosed.
- **(b) nested action_id (the readability note):** because `prev_action_id = this_action_id` and `compose_branch_step_action_id` embeds the parent verbatim, the action_id grows **O(stage-count)** in length: stage 2's is `workflow:wf-dh:step:0:branch:0:step:0:branch:0:step:0:branch:0:step:0`. **Uniqueness holds** (verified: 6/6 distinct, `verify_chain` VALID), and `compose_branch_step_action_id`'s docstring (`workflow_driver_types.py:357`) explicitly blesses recursive nesting. So this is purely a readability/length cosmetic — not a correctness defect. Worth a note only because an operator reading the ledger sees ever-lengthening ids.
- **Resolution path (informational):** none owed; named here to discharge the grep-met-vs-genuinely-met checklist (#7) honestly. Both are genuinely met.

---

## What I checked and found CLEAN (with the command I ran) — transparency (FM-J / FM-E / FM-G)

1. **Non-hollow ledger discriminator — VERIFIED non-hollow.** Simulated the 3-stage chain via `uv run --package harness-cp python -c "…compose_branch_*…"` → 6/6 distinct action_ids + 6/6 distinct idempotency keys; parents chain (distinct), branch_index=0 throughout. Re-confirmed on the real writer (`test_…_live_real_ledger_chain_valid`). NOT decoration.
2. **HandoffContext composition vs the precedent — MATCHES.** Read `harness-runtime/.../sub_agent_dispatch.py:284-342` (`_compose_handoff_context`). The new `_compose_handoff_to_next` (`workflow_driver.py:3670`) mirrors it field-for-field: `entry_hash = parent_entry_hash` (`""` on the buffered path — same value the precedent passes), `summary_hash = sha256(b"").hexdigest()` (the v1.6 MVP default the precedent uses at line 333), empty deliberation tuples, `proposed_action.action_kind = SUB_AGENT_DISPATCH`. The `entry_hash=""` is **defensible** — it is the established MVP precedent, not a shortcut invented here. The payload carries only the next stage's *identity* `{next_stage, next_role}` (control-flow metadata), NOT prior-stage output — B-INTERSTEP honored (no inter-step data threading). Cmd: direct `Read` of both files.
3. **Idempotency keys — DISTINCT per stage, no C-IS-07 §7.5 collapse.** `_compute_step_idempotency_key` (verified its real source) hashes `(run_key, step_index, branch_path)`; `compose_branch_path(stage_ctx) = {prev_action_id}:0` differs per stage (prev nests), so step keys differ; terminal keys use the `:terminal`-suffixed path. Simulated → 6/6 unique. The real-ledger test asserts 6 entries + `verify_chain` VALID — confirmed real (re-ran it).
4. **Stage-0 anchor IS-invariant attack — discharged at the SOURCE (not via the CP docstring).** Read `Spec_Information_Substrate_v1.md` §5.4 directly (lines 469-509); the constraint is line 485. Then ran the strategy on the real writer to confirm the anchor is non-persisted, AND ran PARALLELIZATION to confirm the same synthetic-root pattern in a cleared sibling. → F3-01 (informational, precedent-consistent, non-chain-enforced).
5. **Dual-meaning branch_index — NOT a latent bug.** `writer.branch_index = stage_index` (drain-order key, `workflow_driver.py:3866`) vs `branch_metadata.branch_index = 0` (causality, line 3860) are genuinely different layers: the writer's index is the per-stage drain ordinal so `_drain_and_emit_step_boundaries` emits one STEP_BOUNDARY per stage in stage order; the entry's `branch_metadata.branch_index=0` records "single owner, no siblings." Confirmed each writer is a fresh per-stage `BufferingLedgerWriter`; drain order = stage order. The causality key `(parent_action_id, branch_index=0)` stays unique across stages because `parent_action_id` differs per stage (the chain). No collision. Cmd: `Read` + the 6/6-unique simulation.
6. **Repointed tests — coverage PRESERVED, intent NOT weakened.** `git diff main...HEAD` on the 3 repointed files. Each swapped the "still-unmaterialized" vehicle from DECENTRALIZED_HANDOFF (now materialized) to `EngineClass.EVENT_SOURCED_REPLAY` (still unmaterialized — verified `_IN_SCOPE_ENGINE_CLASSES = {PURE_PATTERN_NO_ENGINE, SAVE_POINT_CHECKPOINT}` at `workflow_driver.py:184`, so the raise is REAL not phantom). The NOT_YET_MATERIALIZED sentinel mechanism is genuinely RE-tested via `test_not_yet_materialized_sentinel_still_raises` (monkeypatches the dispatch table back to the sentinel and asserts the typed raise) — the original test's intent (sentinel-still-raises) is preserved, not lost. Cmd: `pytest` on all 3 → 67 passed.
7. **Plan AC genuinely met (not grep-met).** Read `Implementation_Plan_Control_Plane_v2_32.md:249`. Every atom maps to a passing test: 3-stage pipeline (`test_…three_stage_pipeline_succeeds`), HandoffContext ownership transfer (`test_…composes_handoff_chain` — `from_action_id` == prior stage's persisted step action_id), per-role context (`test_…per_role_stage_experts` — 3 distinct roles), terminal-on-no-handoff (`test_…terminal_when_no_further_handoff` — single stage → 0 handoffs), single-owner serial assertion (`test_…single_owner_at_a_time` — `max_concurrent == 1`, the AC's required "a test asserts serial ownership"), cascade-cancel on stage failure (`test_…cascade_cancel_…fails`).
8. **Spec cites byte-exact.** `§25.11` DECENTRALIZED_HANDOFF row exists at `Spec_Control_Plane_v1_32.md:68`; §25.13/§25.14/§25.15 exist (lines 87/95/103); C-CP-13 HandoffContext is the cited contract. CP plan U-CP-90 at line ~249. All resolve. Cmd: `grep -n` + `Read`.
9. **X-AL-3 anti-extension — CLEAN.** No new H_T design primitive surfaced; the arc materializes an already-cleared spec contract (§25.11 row, v1.32 — cleared at R-FS-1 arc #3). No `design-substrate/**` edit in the diff (Phase-7 posture, correct). `HandoffContext` is the EXISTING C-CP-13 schema; `SUB_AGENT_DISPATCH` ActionKind is existing. No enum widened. Cmd: `git diff --stat` (no `design-substrate/` files).
10. **Framework-pull discipline (I-6) — CLEAN.** No `tenacity`/`langgraph`/`crewai`/etc. The strategy is hand-rolled stdlib (a `for` loop + `hashlib` + the existing branch composers). Cmd: read of imports at the diff head.
11. **Empty/single-stage edge cases — handled.** Empty steps → trivially SUCCESS with `{"stages":{}, "handoffs":[]}` and zero appends (`test_…empty_steps_success`); single stage → SUCCESS, 0 handoffs (`test_…terminal_when_no_further_handoff`). Mirrors the other strategies. Cmd: `pytest` (13 passed).
11b. **Failed-stage (non-)persistence — VERIFIED CORRECT (explicit attack-surface, discharged by execution).** Ran the strategy with stage `s1` raising under MTC/cascade-cancel → exactly **2** persisted entries (the completed-prefix `s0`: 1 step + 1 `completed` terminal); the **failed stage `s1` persists NOTHING** (the `except` at `workflow_driver.py:3877` fires *before* `append_branch_step_ledger_entry` at line 3908), and `s2` never runs; `verify_chain` = VALID; `fail_class` carries the `RuntimeError`. This non-persistence is **correct, not a silent drop**: (a) precedent-consistent — EVALUATOR_OPTIMIZER's `_dispatch_and_buffer` does the same ("the entry is NOT buffered… for the failed step", `workflow_driver.py:2895`); (b) resume-safe — a failed stage with no terminal entry is correctly *re-dispatchable* (§25.15.2 obl. 7 forbids re-dispatch only of `cancelled`/`completed`/`timed_out`), and is moot here anyway since DECENTRALIZED_HANDOFF resume is the B-FANOUT-PAUSE forward build; (c) the only residual is the narrow §25.15.2 obl. 3 "effect-landed-then-result-processing-raised → no ledger entry" edge, which is a **pre-existing cross-strategy reading of obl. 3** (true of the linear path too), not introduced by this arc — informational at most. Output: `STATUS failed | PERSISTED entries: 2 | failed stage s1 persisted ANY entry? False | verify_chain: valid`. Cmd: `uv run --package harness-cp python -c "…fail_step_ids={'s1'}…read_ledger…"`.
12. **Full gate re-verification (spot).** `pytest test_workflow_driver_decentralized_handoff.py` → 13 passed; the 3 repointed files → 67 passed; live e2e → 1 passed (13.54s real Ollama). I did not re-run the entire 976-test harness-cp suite or the 1655 harness-runtime provider-free suite (trusted the caller's stated gate for those), but I independently re-ran every file this arc touches + the tripwire.

---

## Disposition

**APPROVE.** Zero Class-1 (blocking) and zero Class-2 (operator-decision) findings under the §2.7.6 execution-fork scale. The three Class-3 (informational) findings are documentation/transparency notes:
- **F3-01** (stage-0 synthetic anchor vs IS §5.4 prose) is precedent-consistent with the cleared PARALLELIZATION strategy and not chain-enforced — at most a future cross-strategy doc-hygiene note, never introduced by this arc.
- **F3-02** (sync vs TaskGroup) is the faithful reading of "single-owner-at-a-time," not a deviation.
- **F3-03** (cascade-cancel degeneracy + nested action_id) are correctly-degenerate / cosmetic, both genuinely met.

The headline non-hollow claim is empirically true (chain-not-star, 6/6 distinct keys, `verify_chain` VALID on the real writer). The advisor's live-e2e tripwire genuinely passes (real Ollama, no deadlock, no `SUB_AGENT_DISPATCH` reach) — confirming the single-owner-sequential model is sound. The 4 test repoints preserve coverage and the NOT_YET_MATERIALIZED sentinel is genuinely retained. No silent absorption, no X-AL-3 extension, no idempotency/effect-loss hole. This arc is mergeable as-is.

*(If the operator wants the F3-01/F3-02 prose notes folded in, they belong in a future CP/IS doc-coordination touch — e.g. alongside the existing §5.4 line-497 Class-3 informational item — not as a blocker on this merge.)*
