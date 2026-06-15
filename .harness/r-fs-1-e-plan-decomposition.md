# R-FS-1 E-plan — Durable-Execution Engine Classes (E-1 + E-2) Atomic-Unit Decomposition

**Authored:** 2026-06-15 · **Arc:** R-FS-1 child arc **E** (durable-execution engine classes), **E-plan** leg · **Posture:** design-phase (authors `design-substrate/**` plan deltas + this `.harness/` companion + clearance markers; bundled-absorption with the mode-agnostic CLAUDE.md §2.4 pointer bump per root §11.4 — the B3-plan precedent) · **HEAD at authoring:** `d7102a6`

**What this is.** The implementation-planner decomposition of **E-1 EVENT_SOURCED_REPLAY + E-2 WAL_SEGMENT** — both **impl-against-cleared-spec (NO spec leg)** per the architect recommendation `.harness/architect_recommendation_e_engine_fork_vs_impl.md` (authoritative on fork-vs-impl) — into atomic units across two delta-only plan amendments: **CP v2.33 → v2.34** + **runtime v2.44 → v2.45**. Mirrors the B3-plan precedent (`r-fs-1-b3-plan-decomposition.md`: co-published CP + runtime deltas with an aggregate cross-axis DAG; clearance markers + pointer bumps). Decomposes; does not author spec or code.

**E-3 RECONCILER_LOOP is OUT of this plan.** Per the architect rec §6, E-3 carries a **narrow Class-1 fork** (a single C-CP-07 §7.4 substrate-deferral reconciliation sentence reconciling the spec's named "K8s controller / etcd + CRD" substrate with I-6 "no vendored K8s"), operator-ratified at its own **E-spec-3** leg before its E-plan opens. This E-plan covers only the two no-fork classes.

**Inputs re-grounded by direct read at HEAD `d7102a6`:** the architect rec (fork-vs-impl authority); the E-DESIGN doc (`r-fs-1-e-engine-classes-design-v1.md`, §3/§4/§6 — substantive engine semantics survive; its per-slice fork labels superseded); the cleared CP spec `Spec_Control_Plane_v1_2.md` §7.1/§7.4 (C-CP-07) + §8.1/§8.2/§8.3 (C-CP-08); the code surfaces (`workflow_driver.py:183-184` `_IN_SCOPE`, `:1351-1352` gate, `:1445-1453` save-point resume fork, `:1974` `_determine_resume_at`, `:1200` workflow-layer pause-fire, `:1493` per-step pre-entry pause-trigger; `engine_class.py:23-111` enum + 4 F3 floors; `pause_resume_protocol.py:123-135` `EnginePauseResumeSubstrate` Protocol + `:171` Deterministic + `:856/:951` C-CP-49/50 composers; `journal_pause_resume_substrate.py:123` #475 Journal substrate; `r_cxa_2_producer_loop_factory.py:208-214` factory binding Deterministic; `engine_recovery_loop.py:45-104` `RuntimeEngineRecoveryLoop`); `test_u_rt_95...py:129-131,347-368` (Path-(i) skip + DURABLE_ASYNC cell mapping).

---

## §1 — The keystone homing facts (what drives the unit placement)

1. **Three of five engine classes are genuinely UNBUILT durable-execution semantics.** `_IN_SCOPE_ENGINE_CLASSES = {PURE_PATTERN_NO_ENGINE, SAVE_POINT_CHECKPOINT}` (`workflow_driver.py:184`); the gate at `:1351-1352` raises `EngineClassNotYetMaterializedError` for EVENT_SOURCED_REPLAY / RECONCILER_LOOP / WAL_SEGMENT. The `EngineClass` enum is the **closed 5-member set** (`engine_class.py:31-50`) and the `ResumptionKind` taxonomy is closed at 5 (C-CP-08 §8.1) — so E-1/E-2 **consume cleared closed enumerations**; no new primitive is introduced (X-AL-3-clean, per architect rec §3).

2. **Two separable mechanisms** (the load-bearing decomposition driver — advisor-confirmed):
   - **(A) Per-class resumption semantics** — `_IN_SCOPE` widening + the driver dispatch fork at `:1445` (analogous to the SAVE_POINT_CHECKPOINT fork) + `resumption.kind` emission (`engine_replay` / `segment_replay`, C-CP-08 §8.1) + the F2-ledger join (§8.2). This is the U-CP-56 move (it materialized SAVE_POINT_CHECKPOINT resumption **without ever firing the engine recovery loop**).
   - **(B) The engine-layer recovery-loop firing** — `RuntimeEngineRecoveryLoop.capture_pause` / `.attempt_resume` (`engine_recovery_loop.py:52/:74`) → the C-CP-49/50 composers (`pause_resume_protocol.py:856/:951`) → the **R-CXA-2 CP→IS engine-layer seam goes LIVE**. The loop is bound at `ctx.engine_recovery_loop` (`r_cxa_2_producer_loop_factory.py:216`) but its methods have **ZERO production callers** — genuinely dormant.

   Folding (B) into (A) is the `[[built-but-vacuous-reground-ledger-asis]]` trap: "class in `_IN_SCOPE` + tests green" reads as done while the recovery loop stays dormant — adjacent to the design doc's foreclosed "cosmetic Journal swap." So (A) and (B) are **distinct units**.

3. **The engine-layer recovery loop is a C-CP-22 pause/resume-SNAPSHOT surface**, distinct from the driver's prefix-replay path. The driver's pause path (`:1200`) fires the **workflow-layer** `ctx.pause_resume_protocol` (C-CP-26); the **engine-layer** `ctx.engine_recovery_loop` is the separate, dormant surface. A CP-driver branch may fire `ctx.engine_recovery_loop` duck-typed (`Any` on the runtime ctx, exactly as `ctx.pause_resume_protocol` is consumed at `:1200`) — **no CP→runtime import, no cycle.**

4. **Package homing** (verified by direct read): the driver / engine_class / consumers / C-CP-49/50 composers are **`harness-cp`**; the recovery loop / #475 Journal substrate / the R-CXA-2 factory are **`harness-runtime`**; PathClass is **`harness-is`**. E-1/E-2 therefore span CP + runtime (PathClass is an AC-level conditional, not an IS delta — see §3 OQ-3).

---

## §2 — Unit list (5 NEW units: 3 CP + 2 RT)

### CP plan v2.34 (3 NEW units — U-CP-93/94/95)

| Unit | Title | Engine class | Mechanism | Depends on | Spec-cite |
|---|---|---|---|---|---|
| **U-CP-93** | EVENT_SOURCED_REPLAY engine materialization (deterministic event-history replay) | E-1 | (A) resumption-semantics | (none) | C-CP-07 §7.1 row 1 + §7.4 (substrate impl-discretion) + C-CP-08 §8.1 `engine_replay` + §8.2 + §8.3; architect rec §0/§6; U-CP-56 precedent |
| **U-CP-94** | WAL_SEGMENT engine materialization (segment replay + per-segment dedup) + Path-(i) `test_u_rt_95` un-skip | E-2 | (A) resumption-semantics | (none) | C-CP-07 §7.1 row 5 + §7.4 ("specific WAL implementation" deferred) + C-CP-08 §8.1 `segment_replay` + §8.2 row 5 + §8.3 |
| **U-CP-95** | WAL_SEGMENT engine-layer recovery-loop firing branch (`ctx.engine_recovery_loop` → C-CP-49/50) | E-2 | (B) recovery-loop firing (CP-half) | [U-CP-94] | C-CP-22 §22.1 (engine-layer pause/resume free fns) + C-CP-49/50 (= U-CP-49/U-CP-50 §16.5.2 composers) + CXA §2.3.2 R-CXA-2 |

### Runtime plan v2.45 (2 NEW units — U-RT-121/122)

| Unit | Title | Engine class | Mechanism | Depends on | Spec-cite |
|---|---|---|---|---|---|
| **U-RT-121** | Hand-rolled WAL segment-log `EnginePauseResumeSubstrate` (extend #475 Journal) | E-2 | (B) durable substrate | (none) | C-CP-07 §7.1 row 5 ("WAL-owned: append-only segment log with per-segment resume"; per-segment harness-owned lease) + §7.4 (impl-discretion); `pause_resume_protocol.py:123` Protocol |
| **U-RT-122** | R-CXA-2 engine-layer activation: bind U-RT-121 in the factory (replace Deterministic) + durable e2e | E-2 | (B) recovery-loop firing (RT-half) + go-live proof | [U-RT-121, U-CP-95 (cross-axis: CP)] | C-CP-49/50 + R-CXA-2 (CXA §2.3.2); CP spec §16.5.9 invariant 5 (ZERO `CPAuditLedgerEntry` greenfield) |

**Total: 5 NEW units** (3 CP + 2 RT) + 1 cross-axis edge (U-RT-122 → U-CP-95, RT→CP downstream).

---

## §3 — Coverage matrix (every cleared spec subsection in E-1/E-2 scope + every design §6 cross-cutting → unit or disposition)

| Cleared spec / design surface | Disposition |
|---|---|
| C-CP-07 §7.1 row 1 (event-sourced-replay lifecycle = Engine) + §7.4 substrate (impl-discretion) | **U-CP-93** |
| C-CP-08 §8.1 `engine_replay` ("replay from Event History deterministically; activity outputs cached; no re-execution") | **U-CP-93** (the **determinism contract** is an explicit U-CP-93 AC — §8.4/`Spec…v1_2.md:770` deferred span-re-emission to impl; the *semantics* are §8.1-committed, so pinning the no-re-fire behavior falls to the plan now that E-spec-1 is dropped — advisor #4) |
| C-CP-07 §7.1 row 5 (WAL-segment lifecycle = Harness; append-only segment log) + §7.4 ("specific WAL implementation" deferred) | **U-CP-94** (driver/resumption) + **U-RT-121** (substrate) |
| C-CP-08 §8.1 `segment_replay` ("replay from WAL segments; per-segment dedup") + §8.2 row 5 (per-segment ledger entries join F2 on `idempotency_key`) | **U-CP-94** |
| design §4.3 Path-(i) `test_u_rt_95` un-skip (WAL_SEGMENT = canonical DURABLE_ASYNC class per CP §18.1; `test_u_rt_95:129-131`) | **U-CP-94** (un-skip + correct skip-reason + flip Path-(i) fork CLOSED-DEFERRED → CLOSED-BUILT) |
| C-CP-49/50 engine-layer CP→IS emits + R-CXA-2 CP→IS engine-layer seam go-live (design §0/§6.3) | **U-CP-95** (firing branch) + **U-RT-122** (durable substrate bind + e2e) — **the §5 surfaced finding: this homes at E-2, NOT E-1** |
| design §6.1 — F3 capability-floor verification (4 floors, `engine_class.py:74-111` / C-CP-07 §7.4) | **AC-level** per class: 4 sub-ACs each in U-CP-93 + U-CP-94 (resolves design OQ-6 — depth: floor (i) durable-replay-across-restart by e2e restart-simulation; (ii) idempotency, (iii) lease, (iv) observable-lifecycle by integration test) |
| design §6.2 — PathClass placement (closed 4-class `PathClass` enum; IS-AL-1) | **AC-level conditional** in U-RT-121: recommend `STATE_LEDGER` (existing closed-enum member → impl-against-cleared-spec, no IS delta); IF an on-disk substrate cannot honestly map to an existing member, that surfaces the conditional **F-E-IS** sub-fork at impl (resolves OQ-3) — `[[cross-spec-enum-overlap-carrier-segregation]]` |
| design §6.3 — consumer updates (`per_engine_class_topology_overlay` / `workload_engine_class_matrix` / `workload_binding_engine_class_selection`) + CP substitution rows | **AC-level** in U-CP-93 + U-CP-94 (wiring the new class into cleared consumers = impl; design §6.3 "folded into each impl slice, not a separate arc") |
| CP §25.10 Invariant 1 (SINGLE_THREADED_LINEAR byte-unchanged regression guard) | **AC-level** in U-CP-93 + U-CP-94 + U-CP-95 (E touches the dispatch path — advisor #5) |
| EVENT_SOURCED_REPLAY → a §18.1 DURABLE_ASYNC cell? (design OQ-2) | **RESOLVED — NO.** `test_u_rt_95:129-131` maps only RECONCILER_LOOP / WAL_SEGMENT to DURABLE_ASYNC cells → **only U-CP-94 (WAL_SEGMENT) un-skips `test_u_rt_95`**; U-CP-93 does not. |
| E-3 RECONCILER_LOOP semantics + §7.4 reconciliation | **OUT of scope** — narrow Class-1 fork at E-spec-3 (operator-ratified), then a separate E-plan leg (architect rec §6) |

**No silent gap.** Every E-1/E-2-scope cleared spec subsection + every design §6 cross-cutting surface → a unit OR an explicit AC-level disposition. The one **surfaced finding** is §5 (R-CXA-2 ownership).

---

## §4 — Aggregate cross-axis DAG (E arc, E-1/E-2)

5 nodes (3 CP + 2 RT). Cross-axis home: CP plan v2.34 §3.5.

**Per-unit deps:**
- Leaves (`(none)`): **U-CP-93**, **U-CP-94**, **U-RT-121**
- **U-CP-95** → {U-CP-94} (CP-internal: the firing branch composes with the materialized WAL_SEGMENT class)
- **U-RT-122** → {U-RT-121, U-CP-95 (cross-axis: CP)}

**Topological order:** `U-CP-93, U-CP-94, U-RT-121` (foundational) → `U-CP-95` → `U-RT-122`. A valid linear extension exists ⟹ **DAG**.

**Acyclicity + cross-axis cycle guard:**
- The single cross-axis edge (U-RT-122 → U-CP-95) runs **RT→CP**, matching the `harness-runtime` → `harness-cp` package dependency (downstream).
- No CP unit depends on any U-RT-* (U-CP-95 consumes `ctx.engine_recovery_loop` **duck-typed** — `Any` on the runtime ctx, exactly as `ctx.pause_resume_protocol` at `workflow_driver.py:1200`; no `harness_cp`→`harness_runtime` import) → **no CP↔RT cycle**.
- U-CP-94's resume_at reads the **F2 IS ledger** per-segment metadata (C-CP-08 §8.2 row 5) — a CP→IS read (downstream), **not** a read of the runtime segment-log substrate → no CP→RT edge from the resume path either.
- RT-internal: U-RT-122 → U-RT-121 points to a strictly-earlier node. No back-edge.
- **Acyclic confirmed.** No edge to a not-yet-existing unit (all C-CP-49/50 composers, the `EnginePauseResumeSubstrate` Protocol, #475, and the factory pre-exist at HEAD).

---

## §5 — The one finding surfaced: R-CXA-2 engine-layer activation homes at E-2 (WAL_SEGMENT), NOT E-1

**The design doc (`r-fs-1-e-engine-classes-design-v1.md` §0/§2/§3.3) attributed R-CXA-2 activation to E-1** ("On the first slice landing (E-1), C-CP-49/50 fire … R-CXA-2 engine seam goes LIVE"). **Empirical re-grounding at HEAD relocates it to E-2.** This is a plan-level re-sequencing **within impl-against-cleared-spec** — no spec touch, no committed-decision sacrifice — so it is driven autonomously and surfaced here (the B3-plan §5 G2c pattern), per `[[feedback-gate-only-on-meaningful-architecture-change]]`.

**Why E-2, not E-1** (three corroborating facts):
1. The recovery loop is a **C-CP-22 pause/resume-SNAPSHOT** surface (`capture_pause_snapshot` captures one `PauseEvent`; `attempt_resume` reads the latest). EVENT_SOURCED_REPLAY's §8.1 semantic is **deterministic replay-from-event-history (no re-execution)** — not a discrete snapshot-pause boundary. Forcing the snapshot-loop into pure event-replay is contrived — the foreclosed "fake producer" (design §0 anti-pattern list).
2. EVENT_SOURCED_REPLAY does **not** map to a §18.1 DURABLE_ASYNC cell (`test_u_rt_95:129-131`) — it has no DURABLE_ASYNC pause-trigger cycle.
3. **WAL_SEGMENT IS the canonical DURABLE_ASYNC class** whose pause-trigger cycle (`test_u_rt_95`) is the natural engine-layer pause boundary; its append-then-resume maps cleanly onto the snapshot Protocol (#475's append-JSONL / read-latest is exactly this shape).

**Disposition.** Unit B (U-CP-95 firing branch + U-RT-122 durable substrate + go-live e2e) homes at **E-2 (WAL_SEGMENT)**. **U-CP-93 (E-1) delivers event-replay resumption only** — it does NOT fire the recovery loop. IF a natural engine-layer pause boundary for event-sourced surfaces at E-1 impl (e.g. a checkpoint-event boundary), it earns its own Unit B then; the default is R-CXA-2 owned by E-2. The design doc's engine-semantics, hand-roll-per-I-6, and anti-pattern foreclosures all **survive**; only the which-class-activates-R-CXA-2 attribution is corrected.

**U-RT-122's go-live AC is by-execution** (`[[verification-shape-sharpened-grep-vs-e2e]]`): an e2e proving `cp.pause-captured` / `cp.resume-attempted` land with the correct shape (distinct `action_id`s from the workflow-layer `cp.pause-resume-protocol`; ZERO `CPAuditLedgerEntry` greenfield per CP §16.5.9 invariant 5) against the **durable** segment-log substrate — NOT "bound" / "has a caller."

---

## §6 — E-impl sequencing (design §7.3, corrected)

| Arc | Units | What it delivers |
|---|---|---|
| **E-impl-1** | U-CP-93 | EVENT_SOURCED_REPLAY deterministic event-history replay (`_IN_SCOPE` + `:1445` dispatch fork + `engine_replay` resumption.kind + the no-re-fire **determinism AC** + 4 F3-floor ACs + consumer updates + byte-unchanged guard). Does NOT un-skip `test_u_rt_95`; does NOT fire the recovery loop. |
| **E-impl-2** | U-CP-94 + U-RT-121 + U-CP-95 + U-RT-122 | WAL_SEGMENT: (A) segment-replay resumption + `test_u_rt_95` un-skip + Path-(i) fork flip (U-CP-94); (B) hand-rolled segment-log substrate extending #475 (U-RT-121) → firing branch (U-CP-95) → durable factory bind + R-CXA-2 go-live e2e (U-RT-122). **This is the slice that activates R-CXA-2 + gives `RuntimeEngineRecoveryLoop` its first production driver.** |
| **E-spec-3 → E-impl-3** | (separate arc) | RECONCILER_LOOP — narrow §7.4 substrate-deferral reconciliation (operator-ratified) + hand-rolled etcd-style reconciler; live K8s e2e is a deployment-surface operator gate (`engine_class_candidate.py:70`). OUT of this plan. |

Each E-impl-N is its own PR-cluster. E sits in the **SHARED-RUNTIMECONFIG cluster** (serial with B1/B3/B4/B6/B2 on the `workflow_driver` dispatch path); materializing an engine class MUST compose with the landed 6-pattern topology dispatch (`:1375+`) without regressing the SINGLE_THREADED_LINEAR byte-unchanged invariant (CP §25.10 Invariant 1).

---

## §7 — Files written

- `design-substrate/Implementation_Plan_Control_Plane_v2_34.md` (delta over v2.33; +3 units U-CP-93/94/95 + §3.5 E aggregate DAG + §4.3 coverage + §6 finding + §7 footer; all prior content PRESERVED VERBATIM — 0 prior unit-body line changes)
- `design-substrate/Implementation_Plan_Harness_Runtime_v2_45.md` (delta over v2.44; +2 units U-RT-121/122 + DAG + coverage + footer; all prior content PRESERVED VERBATIM)
- `.harness/r-fs-1-e-plan-decomposition.md` (this summary)

**Clearance markers:** `.harness/clearance/Implementation_Plan_Control_Plane-v2_34-cleared-2026-06-15.md` + `Implementation_Plan_Harness_Runtime-v2_45-cleared-2026-06-15.md`. Workspace `CLAUDE.md` §2.4 + `.harness/claude-artifact-pointers.md` §2.4 plan-head bumps (CP v2.33→v2.34; runtime v2.44→v2.45).

**Authority chain — no operator gate at this plan-layer arc.** E-1/E-2 are impl-against-cleared-spec (architect rec §0/§6 — operator-cleared reading; the `next_action` was set to E-plan); the plan deltas decompose cleared C-CP-07/08 closed-enum contracts into units; ZERO spec amendment, ZERO new contract ID, ZERO X-AL-3 risk (no new primitive — architect rec §3). The §5 finding (R-CXA-2 owned by E-2) is a within-impl-against-cleared-spec re-sequencing, not a fork. The ONE genuine operator decision in the E sub-program — the **E-3 §7.4 substrate-deferral reconciliation** — is OUT of this plan (its own E-spec-3 leg, architect rec §7).

**Decorrelated review:** [recorded at the clearance markers + `.harness/adversarial-review-r-fs-1-e-plan.md` after the review pass].
