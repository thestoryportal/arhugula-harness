# R-FS-1 E-impl-1 / U-CP-93 — Impl Finding (EVENT_SOURCED_REPLAY resumption-routing)

**Authored:** 2026-06-15 · **Arc:** R-FS-1 child arc **E** (durable-execution engine classes), **E-impl-1** leg (U-CP-93) · **Posture:** Phase-7 execution (edits `harness-cp/src` + tests; this `.harness/` finding + the SPINE-ledger build-arc registration are the back-flow substrate accompanying the impl PR — the bundled-impl + `.harness/`-doc pattern, root `CLAUDE.md` §11.4) · **HEAD at authoring:** `f7cff3a`

**What this records.** U-CP-93 materializes `EVENT_SOURCED_REPLAY` as **resumption-routing impl** against the cleared C-CP-07/08 contracts, following the **controlling U-CP-56 precedent** (`402a7ea`: `SAVE_POINT_CHECKPOINT` added to `_IN_SCOPE_ENGINE_CLASSES` as impl, "no spec bump"; the architect rec `.harness/architect_recommendation_e_engine_fork_vs_impl.md` §0/§6 cleared E-1/E-2 as impl-against-cleared-spec on this precedent). Two findings surfaced during impl are recorded here (neither is a halt — see §3 classification).

---

## §1 — Finding 1 (Class-3 plan-doc-hygiene): the F2-as-event-history substrate premise is empirically false

CP plan `Implementation_Plan_Control_Plane_v2_34.md` U-CP-93 **Notes** state the §7.4-deferred event-history substrate can be filled by *"reuse the F2 IS state-ledger as the event history (each materialized step = a ledger entry read by `idempotency_key`), **cached activity outputs being the entry payloads**."*

**The bolded clause is empirically false at HEAD.** `harness_is.state_ledger_write.EntryPayload` (C-IS-07 §7.1) carries only `action_id`, `idempotency_key`, `actor`, `timestamp`, and two optional sidecars (`procedural_tier_snapshot_ref`, `branch_metadata`). The persisted JSONL line carries a `response_hash` **digest** — never the activity output. **The F2 ledger cannot store cached activity outputs.**

**The non-false half stands:** the F2 `idempotency_key` join (C-CP-08 §8.2 row 1) *does* give the **resume_at index** — the count of contiguous already-materialized steps — which is the resumption-routing computation `_determine_resume_at` already performs for save-point. So U-CP-93's resume_at uses that join (via `_determine_event_replay_resume_at`, which delegates); only the "cached outputs being the entry payloads" parenthetical is wrong.

**Disposition.** Class-3 (informational; non-blocking). The false clause is a non-load-bearing Note parenthetical, not the materializable AC core. It **owes a plan-doc-hygiene refresh** at a future CP-plan pass (cite-don't-relocate — this Phase-7 session does not edit `design-substrate/**`). The correct substrate reading: F2-read → resume_at (skip-prefix); a dedicated **output-carrying** event-history substrate is required for output replay (§2 + the registered build arc).

---

## §2 — Finding 2 (recorded-not-gated, O-CP-4 precedent): EVENT_SOURCED_REPLAY is degenerate-vs-save-point until two substrates land

The §8.1 `engine_replay` semantic is: *"Prior steps replay from Event History deterministically; activity outputs cached and replayed; **no re-execution of activities**."* In the current driver architecture this decomposes into two clauses with **different materializability**:

| §8.1 clause | Materializable at U-CP-93? | Why |
|---|---|---|
| "no re-execution of activities" | **YES — delivered** | The dispatch loop begins at `resume_at`; the materialized prefix is not re-dispatched. The dispatcher call-count (`_EchoDispatcher.dispatched`) is the side-effect counter — prefix steps are absent from it. Verified by `test_event_sourced_replay_resumes_across_restart_without_refire`. |
| "activity outputs cached and **replayed**" (into downstream-visible state) | **NO — degenerate, deferred** | (a) No output-carrying substrate exists (Finding 1 — F2 stores `response_hash`, not outputs); (b) the driver threads **no inter-step data flow** — `dispatch(binding, step, step_context=...)` carries no prior-output parameter, and `accumulated` is never read downstream (verified at `workflow_driver.py:1631`; this is the registered **B-INTERSTEP** arc). With neither a store nor a consumer, "replay outputs" has no observable manifestation. |

**Consequence.** EVENT_SOURCED_REPLAY materialized within U-CP-93's cleared scope (CP-only, "no new carrier", F2-read) is **behaviorally identical to `SAVE_POINT_CHECKPOINT` skip-prefix**. The distinguishing §8.1 cached-output-replay semantic only manifests once **both** an output-carrying event-history substrate **and** inter-step data flow (B-INTERSTEP) exist. This is the **same accepted bar** the landed `SAVE_POINT_CHECKPOINT` class already has (its resumption tests assert only the RESUMPTION emission + prefix-not-re-dispatched; no output-replay) — so it is **not** a new degeneracy, and **not** the `[[built-but-vacuous-reground-ledger-asis]]` trap *provided the gap is surfaced (here) and the genuine capability is registered as a build arc (§4), not buried under the passing counter test.*

The thin `_determine_event_replay_resume_at` helper is the **named extension seam** where the genuine output-replay refinement lands once those substrates exist; at HEAD it delegates to `_determine_resume_at` and its docstring states the degeneracy explicitly (no masking duplicate).

**Sub-finding (Codex decorrelated review, [P2] — accurate-but-pre-existing):** EVENT_SOURCED_REPLAY is added to the **global** `_IN_SCOPE_ENGINE_CLASSES`, but the resume_at/RESUMPTION block lives only on the `SINGLE_THREADED_LINEAR` path — the 5 non-linear strategies (`_execute_parallelization` / `_evaluator_optimizer` / `_orchestrator_workers` / `_hierarchical_delegation` / `_decentralized_handoff`) return before it. So `EVENT_SOURCED_REPLAY + <non-linear topology>` does not skip-prefix on restart. **Verified pre-existing:** the non-linear strategies are **resume-blind for every in-scope engine class** — they compute no `resume_at` and emit no RESUMPTION at all (grep-confirmed: the only `resume_at`/`RESUMPTION` references after the linear block are in the two `_determine_*_resume_at` helpers). `SAVE_POINT_CHECKPOINT + non-linear` already behaves identically; EVENT_SOURCED_REPLAY inherits it, introducing no new defect class. **Not restricted** to the linear path — that would diverge from the save-point/pure-pattern precedent and add an uncleared `engine_class × topology` admissibility constraint (X-AL-3). Non-linear/fan-out resumption is the already-registered **B-FANOUT-PAUSE** arc. Recorded here + at the `_IN_SCOPE` code comment (decorrelation payoff: Codex surfaced it; the disposition is surface-don't-restrict).

---

## §3 — Classification (per `phase-7-back-flow-routing` §2.4): Class-3, NOT Class-1

| Class-1 indicator | Present? |
|---|---|
| Spec contract under-specifies a surface | NO — C-CP-08 §8.1 fully specifies `engine_replay`; the impl lands the same slice save-point did |
| Plan signature cannot be materialized at target stack | NO — implementable as resumption-routing per the **U-CP-56 controlling precedent** |
| ADR commitment contradicted | NO |
| New H_T primitive surfaced (X-AL-3) | NO — consumes the cleared closed `EngineClass`/`ResumptionKind` enums; introduces no new carrier/contract |
| Cross-axis edge cardinality contradicts CXA | NO — no new cross-axis import (the helper is pure `harness-cp`) |

Both findings are **observations + a registered build arc** (Class-3, §2.3 CONTINUE). Re-classifying Class-1 would re-litigate the cleared impl-not-fork verdict (`[[cleared-spec-resolves-it-before-first-principles-fix]]`). Does not meaningfully change the architecture (`[[feedback-gate-only-on-meaningful-architecture-change]]`) — it confirms E-1 follows the cleared save-point pattern. **No operator gate; driven autonomously + reported.** (Advisor pre-overload concurred: bare RESUMPTION = reading (a), not a halt; the degeneracy = recorded-not-gated finding to surface, O-CP-4 precedent.)

---

## §4 — What U-CP-93 delivers vs the registered deferred build arc

**Delivered (this PR):**
- `EngineClass.EVENT_SOURCED_REPLAY` added to `_IN_SCOPE_ENGINE_CLASSES` (gate at `workflow_driver.py:1351` no longer raises for it).
- Driver dispatch branch at the resume-path computing `resume_at` via `_determine_event_replay_resume_at` (F2 `idempotency_key`-join prefix; delegates to `_determine_resume_at`) + bare `WorkflowEventClass.RESUMPTION` emission when `resume_at > 0`.
- The §8.1 "no re-execution of activities" clause (materialized prefix not re-dispatched).
- F3 capability-floors: **(i)** durable-replay-across-(simulated)-restart ✓ (`test_event_sourced_replay_resumes_across_restart_without_refire`); **(ii)** idempotency-keyed exactly-once / no-double-apply ✓ (same test — prefix not re-fired); **(iv)** observable-lifecycle ✓ (`test_event_sourced_replay_observable_lifecycle_events_emit`). **(iii)** lease-coordination is **not exercised at this driver slice** — it is the orthogonal C-IS-09 worktree / harness-owned-lease layer (consistent with the save-point precedent, whose resumption tests also do not exercise lease); the `CAPABILITY_FLOORS` registry (`engine_class.py`) preserves the floor descriptor for all 5 classes.
- Consumer no-orphaning: the 3 engine-class consumers (`per_engine_class_topology_overlay`, `workload_engine_class_matrix`, `workload_binding_engine_class_selection`) already enumerate all 5 closed-enum members — no change needed; EVENT_SOURCED_REPLAY is already recognized.
- SINGLE_THREADED_LINEAR byte-unchanged: the new `elif` branch is reached only for `engine_class == EVENT_SOURCED_REPLAY`; the genesis-run test proves the happy path is unperturbed; the full harness-cp suite (993 passed/1 xfailed) is the regression proof.

**Deferred span-attribute layer (NOT fabricated here):** `resumption.kind = engine_replay` (C-CP-08 §8.1) and `resumption.is_replay` on `step.boundary` spans (§8.3 item 2) are the **standing deferred OTel-span layer shared across all engine classes** — the runtime `RuntimeLifecycleEventEmitter` records bare `WorkflowEventClass` events ("OTel-span emission lands at L9 wiring"); CP emits typed events, OD/runtime ingests + populates span attributes (the D6 ingestion pattern; `resumption.kind` is derivable downstream from the bound `engine_class`). U-CP-93 emits bare RESUMPTION per the §25.5 v1.4 carve-out + the save-point precedent. No test asserts a span attribute that has no producer.

**Registered deferred build arc — `B-ENGINE-OUTPUT-REPLAY`** (SPINE ledger `.harness/beyond-mvp-capability-boundary-ledger.md`): the genuine §8.1 cached-output replay — an **output-carrying event-history substrate** (the storage half) composed with **B-INTERSTEP** (the inter-step data-flow half, already registered) — so post-resume steps deterministically observe replayed prior outputs. BUILD, design-fork-first per X-AL-3. On landing, EVENT_SOURCED_REPLAY (and WAL_SEGMENT at E-impl-2) gain their genuine distinguishing semantic over save-point.

---

## §5 — Files

- `harness-cp/src/harness_cp/workflow_driver.py` — `_IN_SCOPE_ENGINE_CLASSES` += `EVENT_SOURCED_REPLAY`; resume-path `elif EVENT_SOURCED_REPLAY` dispatch branch; `_determine_event_replay_resume_at` helper (delegates to `_determine_resume_at`; documents the degeneracy + extension seam).
- `harness-cp/tests/test_workflow_driver.py` — 3 new EVENT_SOURCED_REPLAY tests + re-pointed 2 still-raises-vehicle tests (EVENT_SOURCED_REPLAY → WAL_SEGMENT).
- `harness-cp/tests/test_workflow_driver_drain.py` + `test_workflow_driver_envelope.py` — re-pointed 2 still-raises-vehicle tests (EVENT_SOURCED_REPLAY → WAL_SEGMENT).
- `.harness/beyond-mvp-capability-boundary-ledger.md` — registered `B-ENGINE-OUTPUT-REPLAY` build arc.
- This finding doc.
