# R-FS-1 E — Durable-Execution Engine Classes: Design

**Arc:** R-FS-1 arc #24 (E-DESIGN) — the design leg of the **E sub-program** (3rd sub-program of the full-spec build program; frozen `B1✅ → B3✅ → E → B2 → R → B4 → CA → B5 → B6 → B7 → M` order per the SPINE ledger Program section).
**Posture:** mode-agnostic (back-flow documentation; authors only this `.harness/` file — no `harness-*/src` or `design-substrate/**` edit). X-AL-3-clean. Mirrors the B1-DESIGN / B3-DESIGN (#549) design-first precedent.
**Filed:** 2026-06-15 · **Grounded at HEAD `11c27fb6`** (every code/spec cite resolved by direct read this session; the prior grounding-sweep was at `3835408e`, so engine-layer line numbers were re-verified at current HEAD).
**Authority chain:** `[[feedback-full-spec-beyond-mvp-nothing-deferred]]` (STANDING 2026-06-12) → SPINE ledger `.harness/beyond-mvp-capability-boundary-ledger.md` (Bucket A "Engine classes: 2 of 5" RE-OPENED AS BUILD; the Program-section arc-1 scoping folded `C-CP-49/50` into this build) → grounding-sweep `.harness/r-fs-1-remaining-arcs-grounding-sweep-v1.md` (Arc E right-sizing) → this design doc → E-spec-1/2/3 → E-plan → E-impl-N.

---

## §0 — TL;DR

The SPINE ledger's E row ("Engine classes: 2 of 5; `event-sourced-replay` / `reconciler-loop` / `WAL-segment` deferred — the durable/recoverable execution engines") is **behaviorally accurate.** Direct read at HEAD confirms: the `EngineClass` enum is CLOSED at 5 members (`engine_class.py:23-50`), but only **2 of 5** are durable-execution-MATERIALIZED at the workflow driver — `_IN_SCOPE_ENGINE_CLASSES = {PURE_PATTERN_NO_ENGINE, SAVE_POINT_CHECKPOINT}` (`workflow_driver.py:183-184`); the gate at `:1351-1352` RAISES `EngineClassNotYetMaterializedError` for `EVENT_SOURCED_REPLAY` / `RECONCILER_LOOP` / `WAL_SEGMENT`. So **3 of 5 engine classes are genuinely UNBUILT as durable-execution semantics** [HIGH].

E is therefore a **genuine LARGE build, not a wiring nit** — but it carries one structural finding the sweep already surfaced and this design ratifies: the engine-layer recovery driver `RuntimeEngineRecoveryLoop` is **built-but-UNWIRED** (`engine_recovery_loop.py:45`; its `.capture_pause`/`.attempt_resume` have ZERO production callers — only `test_*`). E supplies the missing piece: **a REAL hand-rolled engine that fires that loop**, which (a) gives `RuntimeEngineRecoveryLoop` a production driver, (b) fires the cleared `C-CP-49`/`C-CP-50` engine-layer CP→IS emits, and (c) brings the **R-CXA-2 CP→IS engine-layer seam live in production** — all of which currently sit as ratified bounded-residuals awaiting exactly this trigger.

**The DEFER-supersession (the central re-grounding).** Four ratified dispositions deferred this work, and **all four share the same re-open trigger**: a real hand-rolled engine landing. The full-spec directive now mandates building it, so the trigger is ACTIVE:

| Disposition | Status before full-spec | Re-open trigger (byte-exact) |
|---|---|---|
| Path-(i) fork `class_1_fork_path_i…` | CLOSED-DEFERRED (option E, 2026-05-25) | "future DURABLE_ASYNC engine class materialization via full design-phase back-flow" (§9) |
| `r-cl-p2-engine-recovery-grounding.md` | DEFERRED (2026-06-10) | forward-register `post-phase-8-forward-register.md` line 181 (quoted by r-cl-p2) — "re-open only when a real event-sourced replay, reconciler-loop, WAL-segment, or engine-native-pause recovery loop lands" |
| `class_2_fork_engine_durable_resume…` | engine-layer = ratified CXA-2 bounded-residual (workflow-layer re-aim DONE as R-CC-1 arc #3) | forward-register line 181 (same) |
| forward-register `post-phase-8-forward-register.md` line 181 (CXA-2 row) | CXA-2 RETIRED-AS-BOUNDED-RESIDUAL (batch-55) | "a real event-sourced replay, reconciler-loop, WAL-segment, or engine-native-pause recovery loop" |

**CRITICAL layer distinction** (the sweep flagged it; this design pins it): the **workflow-layer** durable-resume (`api.resume()`, R-CC-1 arc #3, PR #513/#514) is **DONE and is the SIBLING — NOT arc E.** E is the **ENGINE layer** (`ctx.engine_recovery_loop` + the 3 unbuilt `EngineClass` durable semantics). Do not re-scope `api.resume` into E [HIGH].

**Scope & disposition (detail §2–§6):**

| Slice | Engine class | Classification | Fork? | Substrate (hand-rolled, I-6) | Est. (fork-doc) |
|---|---|---|---|---|---|
| **E-1** | `EVENT_SOURCED_REPLAY` | UNBUILT durable semantics | **FORK** (driver-boundary design-extension, X-AL-3) | in-house append-only event store (filesystem/sqlite event history + cached activity outputs) | 15–25 commits |
| **E-2** | `WAL_SEGMENT` | UNBUILT durable semantics; **the canonical DURABLE_ASYNC class** | **FORK** (X-AL-3) | append-only segment-log writer + per-segment replay + idempotent per-segment consumer state (extend `JournalEnginePauseResumeSubstrate` #475) | 20–35 commits |
| **E-3** | `RECONCILER_LOOP` | UNBUILT durable semantics; **live-e2e infra-gated** | **FORK** (X-AL-3) | hand-rolled reconciler tick-loop + state read/diff/converge over a real persistence layer (etcd-style, NO vendored K8s) | 25–45 commits |
| **E-X** | cross-cutting (per class) | IMPL-against-cleared-spec + 1 IS sub-fork candidate | conditional | F3 floor verification + PathClass placement + consumer updates + `C-CP-49/50` go-live | folded per slice |

**Net:** **3 certain forks** (E-1/E-2/E-3 per-class driver-boundary spec amendments — full-spec PRE-AUTHORIZES the back-flow per `[[feedback-full-spec-beyond-mvp-nothing-deferred]]`, but each must still be **authored** as a runtime/CP spec amendment + clearance marker, not silently absorbed) **+ 1 conditional IS sub-fork** (PathClass placement, *iff* the on-disk substrate cannot honestly map to an existing closed-enum member) **+ impl-against-cleared-spec** (`C-CP-49/50` emits — already cleared contracts; firing them is impl) **+ 1 e2e un-skip** (Path-(i) `test_u_rt_95` un-skips at the WAL_SEGMENT slice). Sequence by ascending substrate cost: **E-1 → E-2 → E-3**. Downstream at §7.

**What this design forecloses** (all three are the fake-producer family, foreclosed by line 181 + I-6 + the full-spec "real, not cosmetic" bar):
- ✗ Path-(i) fork **option (D)** — stub-widening `_IN_SCOPE_ENGINE_CLASSES` just to land the e2e against a synthetic marker.
- ✗ the **cosmetic Journal swap** (binding #475 into the factory with no real driver — the literal class-2-fork Option 2 / R-CL-P2 anti-pattern).
- ✗ piping the **workflow-layer** DURABLE_ASYNC pause *through* the engine loop as a fake engine producer.

---

## §1 — Re-grounding (the DEFER-supersession)

### §1.1 What HEAD shows (engine-class materialization state)

Re-verified at HEAD `11c27fb6` by direct read (line numbers current; the Path-(i) fork's `:81-83`/`:604-605` cites are from old HEAD `bd50cd6` and have drifted):

| Engine class | In `_IN_SCOPE_ENGINE_CLASSES`? | Durable semantics at HEAD | Substrate implication |
|---|---|---|---|
| `PURE_PATTERN_NO_ENGINE` | YES (`workflow_driver.py:184`) | in-process, no-resume | none |
| `SAVE_POINT_CHECKPOINT` | YES (`:184`) | real resumption fork (`:1445-1446` → `_determine_resume_at` `:1974` over IS `read_by_idempotency_key`) | filesystem checkpoint |
| `EVENT_SOURCED_REPLAY` | **NO** — raises at `:1351-1352` | **UNBUILT** | event store (deterministic replay) |
| `RECONCILER_LOOP` | **NO** — raises at `:1351-1352` | **UNBUILT** | K8s control plane (`engine_class_candidate.py:70` — excluded at local-development) |
| `WAL_SEGMENT` | **NO** — raises at `:1351-1352` | **UNBUILT** | write-ahead log |

The enum is the closed 5-member set at `engine_class.py:31-50` (`EVENT_SOURCED_REPLAY` `:31`, `SAVE_POINT_CHECKPOINT` `:36`, `PURE_PATTERN_NO_ENGINE` `:41`, `RECONCILER_LOOP` `:46`, `WAL_SEGMENT` `:50`). The 3 unbuilt classes are **enum members with no durable-execution semantics** — declaration-only [HIGH].

### §1.2 The engine-layer recovery driver is built-but-UNWIRED (the producer gap)

`RuntimeEngineRecoveryLoop` (`engine_recovery_loop.py:45`) is the engine-layer recovery driver. Its methods:
- `.capture_pause` (`:52`) → calls `self.wiring.emit_pause_captured_state_ledger_entry` (`:63`)
- `.attempt_resume` (`:74`) → calls `self.wiring.emit_resume_attempted_state_ledger_entry` (`:93`)

The OBJECT is produced — constructed at `r_cxa_2_producer_loop_factory.py` (`materialize_r_cxa_2_producer_loop_stage`), reached from a real production path (`stage_5_loop_init.py` → run bootstrap), stored at `ctx.engine_recovery_loop`. But the METHODS are **dormant**: `.capture_pause` / `.attempt_resume` have ZERO production callers — invoked only in `test_r_cxa_2_producer_loop_factory.py` + `test_engine_recovery_loop.py` [HIGH].

The composers those methods call — `emit_pause_captured_state_ledger_entry` (`pause_resume_protocol.py:856`, `C-CP-49`) + `emit_resume_attempted_state_ledger_entry` (`:951`, `C-CP-50`) — are therefore reachable ONLY through the dormant loop. The factory binds the **in-memory `DeterministicEnginePauseResumeSubstrate`** (`pause_resume_protocol.py:171`), not the durable `JournalEnginePauseResumeSubstrate` (`journal_pause_resume_substrate.py:123`, the #475 F2-recovery substrate — EXISTS + tested but UNBOUND in production).

**The production pause/resume that DOES fire is the WORKFLOW-LAYER `PauseResumeProtocol`** (DURABLE_ASYNC HITL pause + `attempt_resume` at the workflow_driver), a **distinct layer** emitting `cp.pause-resume-protocol` — NOT the engine layer's `cp.pause-captured` / `cp.resume-attempted`. **A real hand-rolled engine that genuinely emits engine-layer pauses is exactly the producer E must create** — wiring that real driver is what finally fires `C-CP-49/50` and activates the R-CXA-2 CP→IS engine-layer seam in production [HIGH].

### §1.3 The four DEFER dispositions and their shared re-open trigger — now ACTIVE

Each of the four dispositions in §0's table deferred E on the **same** producer-discovery logic: *the engines that emit engine-layer pauses (Temporal / K8s / Kafka / LangGraph) are I-6-forbidden to vendor, so a real producer was "producer-discovery-empty by ratified disposition"* (`r-cl-p2…` §1, the 4th `[[r-cxa-seam-wiring-is-producer-discovery]]` DEFER). The full-spec directive **rewrites that premise**: I-6 is a HOW constraint (no *vendored* engine), NOT a vendor-gate — there is **no external corpus / model / credential to wait on**; the full-spec resolution is to **HAND-ROLL the substrates** (`grounding-sweep` Arc-E "Fork vs impl detail"). So this is **not a vendor-gate** — it is fork-owed-and-buildable [HIGH].

The re-open is procedural, not a re-litigation: the Path-(i) fork §9 defines it — *"Reopening requires: re-classifying CLOSED-DEFERRED → PROPOSING + new operator routing decision + new closure arc."* The full-spec directive IS the routing decision (build options A+B+C — all 3 classes). This design doc is the re-open record; §7.1 files the per-slice forks; the Path-(i) fork carries a status-pointer to here at the E-1 arc.

**This is the B3-DESIGN pattern exactly** — B3-DESIGN corrected the ledger AS-IS (machinery built-but-unwired, not unbuilt) and surfaced the genuine builds. Here the correction is narrower (the ledger's "2 of 5" count is already accurate); the supersession is the load-bearing move (DEFER → BUILD under full-spec).

---

## §2 — Dispositioned scope

The build target is the **engine LAYER**: materialize durable-execution semantics for the 3 unbuilt `EngineClass` members + give `RuntimeEngineRecoveryLoop` a real production driver. Each slice:

1. **adds its class to `_IN_SCOPE_ENGINE_CLASSES`** (`workflow_driver.py:183-184`) + a **driver dispatch fork** at the gate (`:1351`), so the workflow driver routes the class to real durable-execution semantics instead of raising;
2. **hand-rolls a real `EnginePauseResumeSubstrate`** (the durable store) per I-6 — no vendored engine;
3. **binds that substrate so `RuntimeEngineRecoveryLoop` gains a production driver** firing `C-CP-49` (`emit_pause_captured…`) + `C-CP-50` (`emit_resume_attempted…`) — activating the R-CXA-2 CP→IS engine-layer seam;
4. **verifies the 4 F3 capability-floors genuinely hold** for the new class (not enum-membership) — see §6;
5. **updates the engine-class consumers** (per_engine_class_topology_overlay, workload_engine_class_matrix, workload_binding_engine_class_selection) + the relevant CP substitution rows.

`C-CP-49`/`C-CP-50` are **already-cleared contracts** (SPINE ledger Program-section arc-1 scoping confirmed they are "substantive build → fold into the engine-classes build"). Firing them from a real driver is **impl-against-cleared-spec**, not a fork — the fork in each slice is the **per-class durable-execution semantics + the `_IN_SCOPE_ENGINE_CLASSES` widening** (the driver-boundary design-extension).

**What each slice unblocks:**
- **E-1 (EVENT_SOURCED_REPLAY)** → first real engine-layer producer; `C-CP-49/50` fire in production; R-CXA-2 engine seam goes live.
- **E-2 (WAL_SEGMENT)** → the canonical DURABLE_ASYNC class → **un-skips Path-(i)** `test_u_rt_95` (`:347` skip; the §18.1 DURABLE_ASYNC matrix cell maps to RECONCILER_LOOP / WAL_SEGMENT per the test reasoning `:129-130`).
- **E-3 (RECONCILER_LOOP)** → the T-perm-3 D1-layer `topology_fault_handling=RECONCILER` engine; the only class with an **infra-gated live e2e** (K8s).

---

## §3 — Slice E-1: `EVENT_SOURCED_REPLAY` (lowest substrate cost)

**Classification:** FORK (driver-boundary design-extension, X-AL-3) + hand-rolled substrate. **Sequenced first** (lowest substrate cost; deterministic event-sourced replay is independently useful — Path-(i) fork option (C) framing).

### §3.1 Durable-execution semantics (design)

`EVENT_SOURCED_REPLAY` = **deterministic replay from a persisted event history**. The engine records each completed activity's effect as an immutable event; on recovery, it **replays the event history** to reconstruct workflow state up to the last persisted event, then resumes forward. The guarantee is *deterministic reconstruction* — given the same event history, replay yields the same state. (`engine_class.py:31-34` EVENT_SOURCED_REPLAY docstring: "replay from Event History with cached activity outputs. Substrate: Temporal / Restate / DBOS" — the vendored engines I-6 forbids; E-1 hand-rolls the in-house equivalent. Per-member substrate citations live in each member's docstring, acceptance #2.)

**This is NOT a DURABLE_ASYNC matrix cell** (`test_u_rt_95:129-130` — only RECONCILER_LOOP / WAL_SEGMENT map to DURABLE_ASYNC cells). So E-1 does **not** un-skip Path-(i); its value is the first real engine-layer producer + R-CXA-2 seam activation. [MODERATE — the exact §18.1 cell mapping resolves at the E-spec leg; see §8 OQ-2.]

### §3.2 Hand-rolled substrate (I-6)

An **in-house append-only event store**: a filesystem/sqlite event-history log (one ordered, immutable event record per completed activity, with cached activity outputs for replay short-circuiting). NO vendored engine (no Temporal/DBOS/Restate). Candidate: a new `EnginePauseResumeSubstrate` implementation (`pause_resume_protocol.py:123` Protocol) sitting alongside `DeterministicEnginePauseResumeSubstrate` / `JournalEnginePauseResumeSubstrate`.

**Research grounding** [HIGH — corpus-cited]: event-sourcing + deterministic-replay failure modes are documented in `Pattern_Reference_Catalog_v1.0.md` (replay/checkpoint/recover clusters) + `agent-harness-eng-research-cluster-4-observability-reliability-security.md` (Temporal, replay, idempotency, and durable-execution patterns all well-represented). The canonical hazards to design against: **non-deterministic replay** (any wall-clock / RNG / external-read inside a replayed activity diverges — replayed effects MUST be cached, not re-executed), and **event-log compaction/snapshotting** (unbounded history). The E-spec leg pins the determinism contract.

### §3.3 Driver dispatch + producer wiring

- Add `EngineClass.EVENT_SOURCED_REPLAY` to `_IN_SCOPE_ENGINE_CLASSES` (`workflow_driver.py:184`).
- Add a driver dispatch fork at the engine-class gate (`:1351`) — route EVENT_SOURCED_REPLAY to its replay-resume semantics (analogous to the SAVE_POINT_CHECKPOINT fork at `:1445`).
- Bind the real event-store substrate so `RuntimeEngineRecoveryLoop.capture_pause`/`.attempt_resume` gain a production driver → `C-CP-49`/`C-CP-50` fire.
- e2e against the **real** substrate (not the in-memory Deterministic).

---

## §4 — Slice E-2: `WAL_SEGMENT` (canonical DURABLE_ASYNC)

**Classification:** FORK (X-AL-3) + hand-rolled substrate. **The canonical DURABLE_ASYNC engine class** — un-skips Path-(i).

### §4.1 Durable-execution semantics (design)

`WAL_SEGMENT` = **append-only write-ahead segment log with per-segment resume**. Each unit of progress is written to an append-only segment before its effect is applied (write-ahead); recovery replays from the last durably-written segment; per-segment idempotent consumer state ensures exactly-once application. This is the **canonical DURABLE_ASYNC** substrate — it maps to the §18.1 DURABLE_ASYNC HITL matrix cell (`test_u_rt_95:129-130`, Path-(i) fork §1/§4-option-B).

### §4.2 Hand-rolled substrate (I-6) — extend #475

The `JournalEnginePauseResumeSubstrate` (#475, `journal_pause_resume_substrate.py:123`) is a **real, proven durable filesystem-journal engine substrate** (F2 recovery) — EXISTS + tested but UNBOUND in production. E-2 **extends/repurpose its journal mechanism** into a segment-log writer + segment replay + idempotent per-segment consumer state. This is the line-181-respecting use of #475: bound via a **REAL driver that fires it** (the WAL_SEGMENT engine), NOT the cosmetic-swap anti-pattern (binding #475 into the factory with no driver — explicitly foreclosed by `r-cl-p2…` §1 + class-2-fork Option 2).

**Research grounding** [HIGH — corpus-cited]: WAL patterns appear in `Pattern_Reference_Catalog_v1.0.md` (WAL, reconciler, and checkpoint patterns well-represented) + cluster-4 (WAL + idempotency coverage). Canonical hazards: **torn writes / partial-segment corruption** (a segment half-written at crash MUST be detectable + discarded on replay — checksum/length-prefix per segment), and **fsync durability** (a segment is "durable" only after fsync; the write-ahead ordering is the load-bearing invariant). The E-spec leg pins the segment durability + idempotency contract.

### §4.3 Driver dispatch + producer wiring + Path-(i) un-skip

- Add `EngineClass.WAL_SEGMENT` to `_IN_SCOPE_ENGINE_CLASSES`; driver dispatch fork at `:1351`; bind the segment-log substrate → `RuntimeEngineRecoveryLoop` fires `C-CP-49/50`.
- **Un-skip `test_u_rt_95_hitl_pause_trigger_durable_async_full_execution_path`** (`:347` `@pytest.mark.skip`) — the e2e gate the arc lands, exercising the full Path-(i) DURABLE_ASYNC pause-trigger cycle through `execute_workflow` against the real WAL_SEGMENT class. On un-skip, correct the skip-reason text + the Path-(i) fork status (CLOSED-DEFERRED → CLOSED-BUILT).

---

## §5 — Slice E-3: `RECONCILER_LOOP` (highest substrate cost; live-e2e infra-gated)

**Classification:** FORK (X-AL-3) + hand-rolled substrate. **Sequenced last** (highest substrate cost; the only class with an infra-gated LIVE e2e).

### §5.1 Durable-execution semantics (design)

`RECONCILER_LOOP` = **control-loop / CRD-reconciler engine**: a tick-loop that repeatedly reads desired-vs-actual state, diffs, and converges (read/diff/converge per iteration) over a real persistence layer. This is the T-perm-3 D1-layer `topology_fault_handling=RECONCILER` engine (`grounding-sweep` Arc-E slice 3). It also maps to a §18.1 DURABLE_ASYNC matrix cell (Path-(i) fork §4 option A).

### §5.2 Hand-rolled substrate (I-6) — etcd-style, NO vendored K8s

Hand-roll a reconciler tick-loop + state read/diff/converge over a **real persistence layer (etcd-style, in-house)** — NO vendored K8s operators/controllers. Per I-6, the control-loop machinery is hand-rolled; only the *deployment substrate* a live run targets (a K8s control plane) is external.

**Research grounding** [HIGH — corpus-cited]: reconciler/control-loop patterns are heavily represented in `Pattern_Reference_Catalog_v1.0.md` + appear in cluster-1 + cluster-4 (recovery). Canonical hazards: **convergence stability** (a reconciler that oscillates / never reaches steady state), and **idempotent reconcile actions** (each tick MUST be safe to re-run — the converge step is level-triggered, not edge-triggered). The E-spec leg pins the reconcile-loop convergence + idempotency contract.

### §5.3 The infra gate (live e2e only)

`engine_class_candidate.py:70` excludes `RECONCILER_LOOP` at `local-development` with reason **"requires K8s control plane"**; it **IS a candidate** at `self-hosted-server` + `managed-cloud` (`:75-98` candidate sets — only `local-development` excludes it). So the **LIVE e2e** for RECONCILER_LOOP is **infra-gated at the local dev surface** — it needs a K8s control plane (available on the server/managed surfaces, absent on local-dev). **The BUILD + non-live unit/integration proof are unblocked** (hand-rolled reconciler logic + a local in-memory/filesystem persistence layer prove the semantics); only the LIVE proof carries the gate. Per `[[probe-provisioned-environment-before-unavailable]]` + `[[feedback-background-agent-no-unilateral-paid-calls-or-secret-relocation]]`: the E-3 arc surfaces the infra gate at the live-proof boundary as a genuine operator decision (provision K8s for live-proof, or carry RECONCILER_LOOP's live-e2e as a deployment-surface-gated residual with non-live proof landed) — it does NOT block the slice's build.

---

## §6 — Cross-cutting design (per slice)

### §6.1 F3 capability-floor verification (not enum-membership)

The 4 F3 capability-floors (`engine_class.py:74-111`, C-CP-07 §7.4) MUST genuinely hold per new class — verified by behavior, not enum-membership [HIGH, per `[[built-but-vacuous-reground-ledger-asis]]`]:

| Floor (`engine_class.py`) | Per-class verification bar |
|---|---|
| (i) `durable_replay_across_restart` (`:76`) | a paused workflow resumes from the real substrate **across a process restart** (the engine-layer durable-resume the workflow-layer `api.resume` is the sibling of) |
| (ii) `idempotency_keyed_exactly_once` (`:85`) | replay/re-dispatch via the F2 ledger `idempotency_key` does NOT double-apply (C-CP-07 §7.4) |
| (iii) `lease_coordination` (`:94`) | the engine emits `lease.acquired`/`lease.released` (CP §5.3) where the class composes lease semantics |
| (iv) `observable_lifecycle` (`:102`) | the class emits the **8 lifecycle events** per C-CP-05 §5.1 (`engine_class.py:106`) — same observability bar the 2 built classes meet |

### §6.2 PathClass placement (closed 4-class enum; IS-AL-1)

Each on-disk substrate (E-1 event store / E-2 segment log / E-3 etcd-style store) MUST resolve against the **CLOSED 4-class `PathClass` enum** — `SKILLS / PROMPTS / ROUTING_MANIFEST / STATE_LEDGER` (`path_class_registry.py:31-37`). IS-AL-1 forecloses inventing a new class. **Recommendation** [MODERATE]: the engine-durability data is workflow execution-state → maps to **`STATE_LEDGER`** (the natural fit; the IS state ledger is already the durable execution-state surface). **Decide WITH the driver per slice** (per `r-cl-p2…` §1 — "journal-path placement is decided with the driver that consumes it"). If a substrate genuinely cannot honestly map to `STATE_LEDGER` (or another existing member), that slice carries an **IS path-class-registry spec-extension sub-fork** (IS-AL-1) — the §0 conditional fork. This is the one cross-axis (CP↔IS) seam in E; resolve it descriptively per `[[cross-spec-enum-overlap-carrier-segregation]]`, halt only on conflicting-semantics on a shared carrier.

### §6.3 Consumer updates + seam go-live

Each slice updates the engine-class consumers so the new class is not orphaned:
- `per_engine_class_topology_overlay.py` — per-engine-class topology overlay.
- `workload_engine_class_matrix.py` — the D4-tunable workload×engine matrix (`workflow_driver.py:100` imports `d4_tunable, lookup_cell`).
- `workload_binding_engine_class_selection.py` — workload→engine selection.
- the relevant CP substitution rows (`tools/substitution_ledger.py` / `.harness/substitutions.yaml`) + the Path-(i) and engine-recovery fork docs.

On the **first** slice landing (E-1), `C-CP-49`/`C-CP-50` fire from a real driver → the **R-CXA-2 CP→IS engine-layer seam goes LIVE** (currently a ratified bounded-residual; CP §16.5.2/.3/.7, ZERO `CPAuditLedgerEntry` greenfield per §16.5.9 invariant 5, distinct `cp.pause-captured`/`cp.resume-attempted` action_ids vs the workflow-layer `cp.pause-resume-protocol`). The §16.5 contract lives in the CP delta chain (v1.25/26/29/30).

---

## §7 — Fork inventory + downstream arc sequence

### §7.1 Forks owed (design-substrate amendments, X-AL-3 back-flow — full-spec PRE-AUTHORIZED, must be AUTHORED)

| Fork | Scope | Routing |
|---|---|---|
| **F-E-1** | EVENT_SOURCED_REPLAY durable-execution semantics: runtime/CP spec amendment for the deterministic event-sourced-replay engine + `_IN_SCOPE_ENGINE_CLASSES` widening + clearance marker | → E-spec-1 |
| **F-E-2** | WAL_SEGMENT durable-execution semantics: spec amendment for the append-only segment-log engine + per-segment resume + clearance marker | → E-spec-2 |
| **F-E-3** | RECONCILER_LOOP durable-execution semantics: spec amendment for the control-loop/CRD-reconciler engine (`topology_fault_handling=RECONCILER`, T-perm-3 D1-layer) + clearance marker + the live-e2e infra-gate surfacing | → E-spec-3 |
| **F-E-IS** (conditional) | IS PathClass placement: *iff* an on-disk substrate cannot honestly map to a closed-enum member (IS-AL-1) → IS path-class-registry spec-extension | folds into the owning slice's spec leg |

Each F-E-N **re-opens** the corresponding §0 dispositions: F-E-N collectively flip the Path-(i) fork (CLOSED-DEFERRED → PROPOSING → CLOSED-BUILT per slice), R-CL-P2 (DEFERRED → superseded), the class-2 engine-layer residual, and line 181 (re-open trigger fired). **SPINE-ledger registration** per `[[spine-ledger-forward-arc-registration]]`: E is already the tracked frozen arc (Bucket A row + the Program section), so no new `B-*` entry is minted; the per-slice F-E-N forks ARE the registration mechanism (analogous to how B3 spawned F-B3-1/F-B3-2). If an E-impl arc surfaces a NEW sub-fork beyond F-E-1/2/3/IS, register it as a `B-*` SPINE entry then (the B-EDIT-CARRIER precedent).

### §7.2 Impl-against-cleared-spec (no fork)

- `C-CP-49` / `C-CP-50` engine-layer CP→IS emits — already-cleared contracts (SPINE Program-section arc-1); firing them from a real driver is impl. (Reconciling the SPINE's "substantive build" label vs this doc's "impl-not-fork" framing: the §16.5 composer contracts + the composers themselves are cleared+built; what is missing is the production *driver*. The "substantive build" the SPINE names is the real engine driver — the per-class fork — while firing the already-cleared composer from that driver is the impl half. The decomposition is more precise than the coarse label, not in conflict with it.)
- F3 capability-floor verification (§6.1) — the floors are cleared (C-CP-07 §7.4); verifying they hold is impl.
- Consumer updates (§6.3) — wiring the new class into existing cleared consumers is impl.

### §7.3 Sequence (research → design[this] → spec → plan → impl)

```
E-design  ✅ (this doc)
  → E-spec-1  : F-E-1 EVENT_SOURCED_REPLAY engine semantics → runtime/CP spec amendment + clearance.
                 Resolve OQ-2 (does EVENT_SOURCED satisfy a §18.1 DURABLE_ASYNC cell?) at the §18.1 reading.
  → E-spec-2  : F-E-2 WAL_SEGMENT segment-log engine + per-segment resume → spec amendment + clearance.
  → E-spec-3  : F-E-3 RECONCILER_LOOP control-loop engine + infra-gate surfacing → spec amendment + clearance.
                 (E-spec-N may bundle the F-E-IS PathClass sub-fork if §6.2 placement needs an IS extension.)
  → E-plan    : atomic-unit decomposition of E-spec-1/2/3 + the impl-against-cleared-spec gaps
                 (U-CP/U-RT-NN: per-class substrate, driver dispatch fork, recovery-loop real producer,
                  C-CP-49/50 go-live, F3 floor verification, consumer updates) — coverage-matrix-complete.
  → E-impl-1  : EVENT_SOURCED_REPLAY — hand-rolled event store + driver dispatch + real recovery-loop
                 producer (fires C-CP-49/50; R-CXA-2 engine seam goes live) + e2e against real substrate.
  → E-impl-2  : WAL_SEGMENT — segment-log substrate (extend #475) + driver dispatch + producer wiring
                 + UN-SKIP Path-(i) test_u_rt_95 + correct Path-(i) fork status.
  → E-impl-3  : RECONCILER_LOOP — hand-rolled reconciler tick-loop + driver dispatch + producer wiring
                 + non-live unit/integration proof; LIVE e2e infra-gated (operator decision at the gate).
  → E-impl-X  : cross-cutting per-class F3 floor verification + consumer updates + substitution-row refresh
                 (folded into each impl slice, not a separate arc).
```

Each E-impl-N is its own PR-cluster (likely multi-session per the fork-doc 15–45-commit estimates). E sits in the **SHARED-RUNTIMECONFIG cluster** (serial with B3/B4/B6/B2 — converges on `RuntimeConfig` + the `workflow_driver` dispatch path). Materializing an engine class MUST compose with the already-landed topology-strategy dispatch (`:1375+`, all 6 patterns) without regressing the `SINGLE_THREADED_LINEAR` byte-unchanged invariant (CP §25.10 Invariant 1) [HIGH].

---

## §8 — Open questions (resolved + surfaced)

| # | Question | Disposition |
|---|---|---|
| OQ-1 | All 3 unbuilt classes, or a priority subset? | **RESOLVED** — all 3, per `[[feedback-full-spec-beyond-mvp-nothing-deferred]]` ("nothing deferred"). Sequence by ascending substrate cost: E-1 → E-2 → E-3. |
| OQ-2 | Does EVENT_SOURCED_REPLAY satisfy the §18.1 DURABLE_ASYNC matrix-cell semantics, or is that strictly RECONCILER_LOOP / WAL_SEGMENT? | **SURFACED to E-spec-1** — the `test_u_rt_95:129-130` reasoning says only RECONCILER_LOOP/WAL_SEGMENT map to DURABLE_ASYNC cells, so the Path-(i) un-skip lands at **E-2 (WAL_SEGMENT)**, not E-1. Confirm at the §18.1 reading [MODERATE]. (Path-(i) fork option C flagged this scope-clarification.) |
| OQ-3 | PathClass placement for the on-disk substrates against the closed 4-class enum? | **RESOLVED (recommendation) + conditional fork** — recommend `STATE_LEDGER`; decide WITH each driver; if no honest mapping, the slice carries the F-E-IS sub-fork (§6.2). |
| OQ-4 | Should #475 `JournalEnginePauseResumeSubstrate` be the WAL_SEGMENT / EVENT_SOURCED foundation, and how to bind it via a REAL driver? | **RESOLVED** — YES for E-2 (extend the journal mechanism into a segment log), bound via the REAL WAL_SEGMENT engine driver (NOT the cosmetic factory swap). §4.2. |
| OQ-5 | RECONCILER_LOOP: hand-rolled etcd-style reconciler in scope, or deferred to a K8s-present deployment surface? | **SURFACED to E-3 (genuine operator decision at the live-proof gate)** — the BUILD + non-live proof are in scope + unblocked; only the LIVE e2e carries the K8s infra gate (`engine_class_candidate.py:70`). Operator decides provision-for-live-proof vs deployment-surface-gated residual. §5.3. |
| OQ-6 | Per-class capability-floor verification depth (unit vs e2e per floor)? | **SURFACED to E-plan** — the acceptance bar per F3 floor (§6.1) is an E-plan atomic-unit decision; default: durable-replay-across-restart proven by e2e (restart simulation), the other 3 by integration tests. |

---

## §9 — Decorrelated review record

Per the standing posture (root `CLAUDE.md` §10.9 + §13.1):

- **advisor()** — overloaded across 4 attempts this session (the gating pre-done check was genuinely unavailable). The two decorrelated reviewers below supplied the coverage; the approach (mode-agnostic design-first dossier mirroring B3-DESIGN; build all 3 classes hand-rolled per I-6; sequence by cost; per-slice forks) follows a well-established precedent.
- **harness-adversarial-reviewer** (dedicated agent, 38 tool-uses, **24 cites re-grounded byte-exact**) — **APPROVE**. Found 5 cite-hygiene errors + 1 reconciliation (C-CP-49/50 impl-vs-build label) — **all folded in** (the §90→Program-section, line-181→forward-register, server/managed RECONCILER inclusion, engine_class.py:43→:31-34, corpus-count softening fixes above). Report: `.harness/adversarial_review_r_fs_1_e_design.md`. Confirmed: the 3-of-5-unbuilt state; the built-but-unwired producer gap; api.resume is the workflow-layer SIBLING; the fake-producer anti-patterns genuinely foreclosed; F-E-1/2/3 genuinely-owed; PathClass respects IS-AL-1; X-AL-3-clean.
- **Codex out-of-family** (`just codex-review`) — **converged with the adversarial agent** (decorrelation payoff): independently flagged the RECONCILER_LOOP server/managed mapping [P2] + the engine_class.py:43 cite [P3] — both already fixed — plus a [P2] that the `roadmap_status.md` refresh is owed (the standard §12.2.1 post-merge terminating-refresh step, not a design-PR defect). No correctness blocker on the design substance.
- **Council** — NOT convened. Per the §10.9 nameable-tension discriminator: the central tension (C9 reliability/crash-recovery ⊥ C10 blast-radius + I-6 no-vendor across the engine-vs-workflow-layer boundary, C1) was **already named + resolved** in `class_2_fork_engine_durable_resume…` §3 (workflow-layer took it as R-CC-1 arc #3; engine-layer is E per full-spec). The remaining E-design decisions are determined by the existing forks + I-6 + the grounding sweep (primary sources decide), not by an unresolved cross-voice tension. Routed to advisor + adversarial-reviewer instead.

---

## §10 — Filing footer

| Field | Value |
|---|---|
| Artifact | `.harness/r-fs-1-e-engine-classes-design-v1.md` |
| Arc | R-FS-1 arc #24 (E-DESIGN) |
| Posture | mode-agnostic (back-flow documentation; no `harness-*/src` or `design-substrate/**` edit) |
| Grounded at HEAD | `11c27fb6` (cites resolved by direct read this session) |
| Authority | `[[feedback-full-spec-beyond-mvp-nothing-deferred]]`; SPINE ledger Program section (E frozen arc; C-CP-49/50 folded in); grounding-sweep Arc E |
| Supersedes (re-opens) | Path-(i) fork (CLOSED-DEFERRED option E); `r-cl-p2-engine-recovery-grounding` (DEFERRED); class-2 engine-layer residual; forward-register line 181 — all share the now-ACTIVE re-open trigger |
| Distinct from | R-CC-1 arc #3 `api.resume()` (workflow-layer, DONE, #513/#514) — E is the ENGINE layer |
| Successor | E-spec-1 (F-E-1 EVENT_SOURCED_REPLAY) → E-spec-2/3 → E-plan → E-impl-1/2/3 |
| Forecloses | Path-(i) option (D) stub-widening; cosmetic Journal swap; workflow-pause-piped-through-engine fake producer |
