# B-18-PREWARM-OW — pre-build design decision record (decompose-at-open)

*Arc open 2026-07-11 (dedicated session per the dashboard's next-action directive; the sole
registered `B-*` arc). Registered at CP spec v1.95 follow-on table + the arc-ledger row
(`parent_arc: B-18-3C-PREWARM`): "ADR-D4 §1.8 warm-up + cohort partition for
ORCHESTRATOR_WORKERS (+ contingent evaluator-optimizer multi-evaluator)". The
B-18-FENCE-LEDGER-FIDELITY-OW register-don't-silently-widen precedent, discharged.*

---

## 0. TL;DR

`[HIGH]` Extend the ADR-D4 §1.8 concurrent-prompt-cache warm-up — in its final v1.95 §25.19
cohort-partition form directly (no intermediate binary-gate stage) — to the
`ORCHESTRATOR_WORKERS` worker fan-out in `_execute_orchestrator_workers`: capture the full
`_d4` tunable at the existing resolution site, compute `_warmup_phase_split()` over the LIVE
worker `branch_plan` (inline dispatcher lookup; not-bound → non-capable), dispatch PROCEED as
two sequential gathers and the strict tiers as the inline two-phase
(watchdog + TaskGroup Phase 1 + NORMATIVE `task.result()` resurface + TaskGroup Phase 2) under
ONE deadline — both mirroring the parallelization shapes byte-adjacent. Gate=False routes to the
pre-arc paths byte-identical (existing ~91K of O-W tests carry zero `CohortKeyCapable` stubs →
they ARE the byte-identity regression net). The orchestrator is NOT a cohort member (named
rejection). Obligation-4 scan family (all EIGHT O-W sites) UNTOUCHED; ZERO store-write changes.
HIERARCHICAL_DELEGATION inherits per level (recursion re-enters this executor; zero HD-specific
code). The evaluator-optimizer multi-evaluator cell is CONTINGENT (sequential single-evaluator
at HEAD §25.11) — dispositioned, not built. CP spec v1.95→v1.96 + clearance.

**Pre-build review disposition (2026-07-11).** Fable-5 adversarial design review (advisor
unavailable — double-outage fallback per `[[fable5-fallback-reviewer]]`): **AMEND-THEN-BUILD,
0 blocking + 4 concern + 2 cosmetic — ALL folded below pre-build.** C1: D7's "rarity" leg was
empirically BACKWARDS (`cohort_key()` hashes `binding.agent_role`, but `resolve_step_binding`
builds non-overridden bindings WITHOUT `agent_role` — the per-worker derived role folds into the
CONTEXT only, never the hash → orchestrator↔worker key equality is the COMMON case for a
homogeneous no-override manifest); the D7 decision survives on its other three legs (resume
asymmetry / bounded cache-hit cost / ADR-D4 §1.8 sibling-set reading — the reviewer's steelman
found NO committed source requiring orchestrator credit); the rarity leg is REPLACED below. C2:
"ADR-D4 §1.8(f)" is a phantom §-label — the (f) item lives under ADR-D4 **Consequences**
(ADR-D4.md:396); relabeled below + in the delta (the shorthand is inherited from v1.87–v1.91
artifacts, noted as such). C3: D1 falsifies two v1.89-era characterizations — the v1.89
change-note's "warmup is irrelevant outside PARALLELIZATION" and the `d4_tunable` docstring's
"non-PARALLELIZATION callers omit this param" (`workload_engine_class_matrix.py:125-128`) — the
v1.96 delta MUST name the v1.89 supersession and the docstring is refreshed in-arc (the
silent-contradiction defect class). C4: the witness plan lacked a fence-family × partition
witness — OWP12 added (strict-tier recovered-fence-peer withheld as follower → arm-(3)
`completed` capture-less at the CASCADE_CANCEL exit) + the structural-reachability note recorded
(at HEAD only INFERENCE_STEP is capable → fence/TOOL_STEP + paused-child ordinals are Phase-1
non-beneficiaries in PRODUCTION; withheld-as-follower is constructible only via a capable stub —
the witness uses one). Cosmetic 1: §3 PROCEED × paused-child cell rebound to the correct exit
(under two-gather, followers cannot be withheld at the :10887 paused-child exit — Phase 2
completes before that check; withholding occurs only at the :10875 deadline exit, whose scan
covers it). Cosmetic 2: regression-net scope line added (NO O-W-reaching suite anywhere — HD /
fanout-pause / output-replay / handoff / cascade-policy / runtime integration — references
`CohortKeyCapable`; runtime integration fixtures never bind `frozen_tool_superset` → production
`cohort_key()` = None → gate False there too; under default-on a FUTURE fts-bound O-W
integration fixture silently opts into the partition — named tripwire). The reviewer verified
by execution (project interpreter): the P1 probe — a TaskGroup child whose CancelledError
handler records-then-reraises (the `_cancel_worker` shape) still exits the group CLEAN and
`task.result()` resurfaces — the NORMATIVE mitigation transfers; P4 — an OUTER watchdog cut
with the inner timeout unexpired resurfaces a NAKED CancelledError, matching the shipped
parallelization semantics for the nested-HD case.

---

## 1. Committed sources (all verified byte-exact at HEAD `8213a681` this session)

| Source | Commitment |
|---|---|
| ADR-D4 §1.8 (lines 228–242) | "The harness MUST serialize warm-up at fan-out"; **"The protocol applies to all cells where fan-out cap > 1 (orchestrator-workers, parallelization, evaluator-optimizer with multi-evaluator)"** |
| CP spec v1.95 §25.19 (items 1–8) | The heterogeneous cohort partition: `(step_kind, cohort_key)` grouping over the LIVE plan; Phase 1 = leader per multi-member cohort + non-beneficiaries; PROCEED two-gather; strict Phase-1 TaskGroup + NORMATIVE `task.result()` collection; degenerate reductions EXACT; scan family untouched |
| CP spec v1.95 follow-on table + arc-ledger row `B-18-PREWARM-OW` | The registration this arc discharges; scope-note: evaluator-optimizer multi-evaluator CONTINGENT |
| CP spec v1.88 §25.16 | `CohortKeyCapable.cohort_key(binding, step) -> str \| None` dispatcher oracle (16-hex sha256) |
| ADR-D4 **Consequences (f)** (ADR-D4.md:396; the "§1.8(f)" shorthand in v1.87–v1.91 artifacts names THIS item — review C2) via PR #926 (B-18-3C-PREWARM-DEFAULT-ON) | `WorkflowManifestEntry.concurrent_cache_warmup` defaults **True** — the same manifest field governs this arc (no new field; default-on for O-W = impl-to-cleared-ADR: Consequences (f) is cell-agnostic + §1.8 line 242 names orchestrator-workers) |
| `Phase_7_Meta_Architecture_v1.md` §7.4 CP-AL-1 | H_E sub-agent topology ≠ H_T TopologyPattern — this arc builds H_T's O-W engine surface, no H_E leakage |

### 1.1 Grounding disposition — O-W dispatch mechanics inventory (verified by direct read)

`[HIGH]` `_execute_orchestrator_workers` (`workflow_driver.py:9213`): `steps[0]` = orchestrator,
dispatched SYNCHRONOUSLY on the driver thread at :9852 BEFORE the worker plan build; `steps[1:]`
= workers fanned out concurrently. Worker `branch_plan` (5-tuples `(branch_index, step, child,
writer, binding)`, the parallelization shape) built at :9990–10098 over the LIVE remainder
(recovery-seeded ordinals `continue`d out: terminal-recovered skipped, scoped-abort skipped;
paused-child + fence-paused re-planned). `cascade_policy` resolved at :9513 via
`d4_tunable(lookup_cell(...), persona_tier).cascade_policy` — the full `_d4` is NOT captured and
`concurrent_cache_warmup` is NOT passed (parallelization's :6948 passes it). Dispatch shapes:
PROCEED `_proceed_fanout` (:10862) = ONE `asyncio.gather(return_exceptions=True)` under
`asyncio.timeout(deadline)`; strict `_cancel_fanout` (:11120) = ONE
`cascade_cancel_barrier(...)` call (the :2097 helper: TaskGroup + deadline watchdog over
`_BRANCH_INFLIGHT_DISPATCHES`). NO warm-up gate exists anywhere in the O-W executor (verified:
`_warmup_gate` / `_warmup_phase_split` appear only in `_execute_parallelization`). Workers
resolve dispatchers INLINE per-dispatch (`step_dispatchers.lookup(step.step_kind)` at :10772 /
:10921) — there is NO prebuilt `branch_dispatchers` map (that pre-flight was a
parallelization-specific fail-loud mitigation; O-W's committed failure surface for an unbound
kind is per-worker: PROCEED → gather-captured → PARTIAL; strict → grouped → cascade).
Obligation-4 scan closure `_synthesize_undispatched_terminals` (:10382, O-W-local; six arms +
reconstruct arms) fires at EIGHT call sites (:10558 reconstruct-block, :10885 PROCEED-deadline,
:10896 PROCEED-paused-child, :11154 fence-ABORT, :11172 CASCADE_CANCEL, :11216 PAUSE-deadline,
:11233 not-yet-materialized, :11249 protocol-not-bound) — all keyed on writer-disposition
ABSENCE + the fence/reconstruct/paused-child dicts, ordinal-keyed, phase-free.

### 1.2 The arc is non-hollow at HEAD

`[HIGH]` The same B4 per-step override family that makes parallelization heterogeneous
(`StepOverride.prompt_version_sha` / model / role, C-CP-06 §6.1) applies to O-W workers —
worker bindings vary per step. Today an O-W fan-out with ANY multi-member cohort cache-miss-
storms that cohort unconditionally (no gate at all — worse than parallelization's pre-partition
binary gate, which at least warmed the uniform case). The ADR-F2 §(b)(ii) 4-10× detonation the
warm-up exists to prevent strikes every O-W fan-out with a shared prefix. ADR-D4 §1.8 commits
the fix for this cell explicitly.

---

## 2. Design decisions

### D1 — Full `_d4` capture at the existing resolution site

`[HIGH]` `:9513` becomes the parallelization `:6948` shape:

```python
_d4 = d4_tunable(
    lookup_cell(manifest_entry.workload_class, manifest_entry.engine_class),
    manifest_entry.persona_tier,
    concurrent_cache_warmup=manifest_entry.concurrent_cache_warmup,
)
cascade_policy = _d4.cascade_policy
```

Same call count, same site, same comment lineage ("Resolve cascade policy before the RECONCILER
CAS gate…" retained). No second `d4_tunable` call is added. **Supersession named (review C3):**
this falsifies the v1.89 change-note characterization ("Non-PARALLELIZATION topology strategies
call `d4_tunable()` without specifying `concurrent_cache_warmup` … warmup is irrelevant outside
PARALLELIZATION") and the `d4_tunable` docstring's "non-PARALLELIZATION callers omit this param"
(`workload_engine_class_matrix.py:125-128`) — the v1.96 delta names the v1.89 supersession
explicitly and the docstring is refreshed in-arc. The other four `d4_tunable` callers (crash
gates :2977/:3181, EVALUATOR_OPTIMIZER :8738, DECENTRALIZED_HANDOFF :11737) remain
cascade_policy-only and correct (no warm-up in those engines; E-O per D9).

### D2 — Split site: after the `not branch_plan` short-circuit + the PROCEED fence guard, before the PROCEED branch

`[HIGH]` `_warmup_phase_split()` + `_warmup_phase1/_warmup_phase2/_warmup_gate` are computed at
`:10761` (immediately after the `orchestrator-workers-effect-fence-resume-requires-strict-tier`
fail-closed guard at :10755, immediately before `if cascade_policy is CascadePolicy.PROCEED:`
at :10763) — the exact relative position parallelization uses (:7501 after its :7494 guard).
Consequences, all inherited from the v1.95 §25.19 lineage:

- The split — and its `cohort_key()` oracle calls — never runs ahead of the honest-FAILED
  guards (the empty-plan short-circuits, the reconstruct block, the fence-resume guard).
- Keyed on the LIVE (post-recovery-seed) `branch_plan`: a partial-recovery resume re-partitions
  the REMAINDER (new leader per remaining cohort — the §25.19 item-1 lineage).
- The `len(branch_plan) < 2` short-circuit + gate-off (`concurrent_cache_warmup=False` → split
  never computed) preserve the zero-oracle-call properties verbatim.
- Shared by all three §25.15.1 paths (PROCEED / CASCADE_CANCEL / PAUSE).

### D3 — Dispatcher resolution INSIDE the split: inline lookup; not-bound → non-capable

`[HIGH]` The O-W split adapts the §25.19 item-1 partition for the no-prebuilt-registry engine:

```python
try:
    dispatcher = step_dispatchers.lookup(step.step_kind)
except StepKindDispatcherNotBoundError:
    continue  # non-capable: the worker fails at ITS OWN dispatch site, as today
if not isinstance(dispatcher, CohortKeyCapable):
    continue
key = dispatcher.cohort_key(binding, step)
```

An unbound `StepKind` must keep O-W's committed per-worker failure surface BYTE-EXACT (PROCEED:
gather-captured → PARTIAL, zero ledger footprint for that worker — a pre-existing surface this
arc neither fixes nor worsens; strict: grouped → cascade + scan `cancelled`). REJECTED-NAMED:
pre-resolving a `branch_dispatchers` map with parallelization's fail-loud-on-unbound pre-flight —
that mitigation was a parallelization-specific decision (out-of-family Codex [P2] there); porting
it here would CHANGE O-W's committed failure classification for a setup error, which is not this
arc's mandate (registrable separately if ever wanted). The registry resolves per `step_kind`
(same instance per kind), so the `(step_kind, key)` attested-comparability property of §25.19
item 1 holds identically.

### D4 — Partition semantics: §25.19 items 1–2 VERBATIM (leaders ∪ non-beneficiaries; exact degenerate reductions)

`[HIGH]` Grouping by `(step.step_kind, cohort_key)`, insertion (= ordinal) order; Phase 1 = one
LEADER (first ordinal) per multi-member cohort PLUS every non-beneficiary (None-key /
non-capable / singleton-cohort); Phase 2 = followers; `_warmup_gate = bool(_warmup_phase2)`
(computed only when `_d4.concurrent_cache_warmup`). O-W lands the PARTITION form directly —
there is no committed basis for reproducing the superseded v1.88 binary predicate as an
intermediate stage, and §25.19 is the live warm-up contract.

### D5 — PROCEED: two sequential gathers under the ONE existing `asyncio.timeout`

`[HIGH]` `_proceed_fanout` mirrors parallelization `:7811–7845`: gate-False → the pre-arc single
gather byte-identical; gate-True → Phase-1 gather (`return_exceptions=True`), Phase-2 gather
(same), results reassembled in `branch_plan` ordinal order. O-W-specific composition points, all
phase-agnostic by construction: `paused_child_dispositions` / `effect_fence_*` stashes are
written inside `_proceed_worker`/`_cancel_worker` keyed by ordinal (which phase a worker ran in
is invisible to them); the post-barrier `paused_child_dispositions` check (:10887) and the
deadline handler (:10875) are unchanged. No NEW carve-out arises: O-W's baseline was ALREADY the
gather (there is no v1.87-era solo `except Exception` outlier here), so a spontaneous worker
CancelledError is gather-captured in both phases exactly as the baseline captures it — the
§25.19 item-3 named carve-out is parallelization-historical and does not extend.

### D6 — Strict tiers: inline two-phase, engine-local copy (the FIDELITY-OW locality precedent)

`[HIGH]` `_cancel_fanout` mirrors parallelization `:8059–8148`: gate-False → the pre-arc
`cascade_cancel_barrier` call byte-identical; gate-True → inline two-phase sharing ONE deadline
budget + ONE `_BRANCH_INFLIGHT_DISPATCHES` watchdog registry across both phases (a composed
second barrier call would grant a full second `deadline` — the §25.11 wall-clock cap doubling
the v1.90 DDR rejected): registry token push; `_deadline_cutoff()` watchdog; `asyncio.timeout
(deadline)`; Phase-1 `asyncio.TaskGroup` over `_cancel_worker(*plan)`; **NORMATIVE post-group
`task.result()` collection for every Phase-1 task** (the §25.19 item-4 swallow-window closer —
CPython's TaskGroup swallows a spontaneously-cancelled child; without the resurface the
followers would dispatch after a watchdog cut, inverting the effect-set subset invariant;
OWP9 pins by execution); Phase-2 TaskGroup + result collection; `except TimeoutError` →
`BranchBarrierDeadlineExceededError`; `finally` reaps the watchdog + resets the registry.
ENGINE-LOCAL copy, not a shared helper: the closure closes over engine-local state
(`_cancel_worker`, `deadline`, the phase lists), and the workspace precedent for exactly this
fork is per-engine locality (`_synthesize_undispatched_terminals` was deliberately factored
O-W-LOCAL at B-18-FENCE-LEDGER-FIDELITY-OW rather than shared — the two engines' terminal
machinery is intentionally independent). A parameterized shared barrier is a registrable
refactor if a THIRD engine ever needs it; two call sites do not justify the coupling.
Laziness preserved: only `phase1` coroutines are instantiated on a Phase-1 failure (no
un-awaited-coroutine leak). Per-worker records byte-identical — all handlers live in
`_cancel_worker`, ordinal-keyed, phase-agnostic. The v1.95 accepted micro-divergence (one
scheduling tick between TaskGroup child start and its synchronous `_mark_branch_dispatched`
under a sub-tick deadline) carries to O-W verbatim — recorded, not engineered around,
unreachable at the non-injectable 300 s default.

### D7 — The orchestrator is NOT a cohort member

`[HIGH]` The partition groups the WORKER fan-out only (`branch_plan` = `steps[1:]` ordinals).
The orchestrator's sequential dispatch (:9852, completes BEFORE the plan build) is NOT credited
as a cohort cache-write even when its `(step_kind, cohort_key)` would equal a worker cohort's:

- **Resume asymmetry**: on resume the orchestrator is NOT re-dispatched (output recovered from
  the snapshot) — its original cache-write may be arbitrarily stale (5m/1h ttl), so crediting
  its cohort would need `_is_resume`-awareness and a freshness model the arc has no committed
  basis for (cross-time cache warmth is Anthropic-side, outside the partition's scope — the
  v1.95 DDR §1.1 boundary).
- **Key equality with the orchestrator is COMMON, and that is fine (review C1 — replaces the
  earlier backwards "rarity" leg)**: `cohort_key()` hashes `binding.agent_role`, but
  `resolve_step_binding` builds non-overridden bindings WITHOUT `agent_role` (the per-worker
  derived role folds into the CONTEXT via `compose_branch_child_context(..., agent_role=role)`,
  never the hash) — so a homogeneous no-override manifest yields orchestrator↔worker key
  equality as the COMMON case. The decision therefore rests on the other legs, and the cost
  analysis below covers the common case, not an edge case.
- **Bounded cost of not crediting**: when the keys DO match on a fresh run, the workers form one
  cohort whose leader serializes and itself cache-HITS (warm from the orchestrator's completed
  dispatch) → completes fast → followers release. Latency ≈ one warm dispatch; zero correctness
  impact; strict-tier effect-set is strictly smaller (never larger).
- ADR-D4 §1.8's sibling set ("siblings[0]", "siblings[1..N-1]") is the fan-out's siblings; the
  orchestrator is not a sibling.

REJECTED-NAMED: orchestrator-as-cohort-leader credit (skip Phase-1 serialization for the
orchestrator's own cohort on a fresh run). Registrable follow-on against this named rejection
if latency data ever motivates it.

### D8 — Obligation-4 scan family: UNTOUCHED (all EIGHT sites)

`[HIGH]` The O-W-local `_synthesize_undispatched_terminals()` keys on writer-disposition ABSENCE
+ the paused-child / fence / reconstruct dicts — all ordinal-keyed, none phase-aware. Withheld
Phase-2 followers at any terminal exit get exactly today's arms (`cancelled` baseline /
paused-child + fence-family `completed` arms / reconstruct arms). ZERO changes to the scan, to
store writes, to statuses, to fail_classes, to step counts. The PAUSED boundary stays scan-free
(snapshot omission IS the re-dispatchable contract): a strict-tier Phase-1 failure under PAUSE
leaves ALL followers omitted from the snapshot → re-dispatchable on resume → the resume
re-partitions the remainder (D2 LIVE-plan recompute). The partition changes only WHEN worker
dispatches fire, never what is recorded about them.

### D9 — HIERARCHICAL_DELEGATION inherits per level; evaluator-optimizer stays CONTINGENT

`[HIGH]` HD reuses `_execute_orchestrator_workers` at each recursion level (the B-HIERARCHICAL-
PAUSE lineage), so each level's worker fan-out partitions independently over its own live plan —
zero HD-specific code, the FIDELITY-OW precedent. The ADR-D4 §1.8 third cell
(evaluator-optimizer with multi-evaluator) is CONTINGENT: at HEAD evaluator-optimizer is
sequential single-evaluator (§25.11) — there is no fan-out>1 cell to warm, and building one
would be silent design extension (X-AL-3). Disposition: the v1.96 delta RECORDS the contingency
discharge — any future multi-evaluator arc MUST carry the warm-up + partition as part of its own
registration (the spec text is the forward tripwire). The arc-ledger row closes with the O-W
half LANDED + the E-O half CONTINGENT-dispositioned (complete-at-scope; the registration's own
scope-note says "covers it only if that cell ever materializes").

### D10 — Default-on posture carried (no new tunable surface)

`[HIGH]` The SAME `WorkflowManifestEntry.concurrent_cache_warmup` field (default True per
ADR-D4 §1.8(f), PR #926) governs the O-W gate — no new field, no new enum, no §5.2 hash change
(the field already participates exactly as it does for parallelization). Operator opt-out is
per-manifest, engine-uniform. Default-on for O-W is impl-to-cleared-ADR ("all cells"), not a new
operator gate.

---

## 3. Failure-semantics table (per tier × phase; all rows = today's committed classifications)

| Event | PROCEED | CASCADE_CANCEL / PAUSE |
|---|---|---|
| Phase-1 worker fails | gather-captured → Phase 2 still dispatches → PARTIAL (H1 lineage) | TaskGroup cancels in-flight Phase-1 peers (shielded → run to completion, record terminals); Phase 2 withheld; post-barrier: CASCADE_CANCEL → FAILED + scan; PAUSE → snapshot (followers omitted = re-dispatchable) |
| Deadline strikes in Phase 1 | in-flight cut records `timed_out` at its own handler; gather cancelled → TimeoutError → scan (`cancelled` for never-started) → PARTIAL | same mechanics → `BranchBarrierDeadlineExceededError` → FAILED + scan at the deadline exit |
| Phase-1 all-clean | Phase-2 gather (per-worker capture) | Phase-2 TaskGroup (first failure cascades) |
| Worker's child PAUSES in Phase 1 | gather-captures the re-raise → Phase 2 STILL dispatches (no withholding at the :10887 paused-child exit — review cosmetic 1) → post-barrier FAILED (`child-paused-not-resumable-under-proceed`) + scan records the stashed child `completed` terminal-only; follower withholding under PROCEED occurs ONLY at the :10875 deadline exit, whose scan covers it | strict: stash + re-raise halts fan-out at the pause boundary → PAUSE tier: paused-child snapshot carrier; followers omitted (scan-free PAUSED boundary) |
| Fence pause/abort in Phase 1 | structurally unreachable under PROCEED (fence-resume rejected pre-dispatch; fence dicts populated only in `_cancel_worker`) | ordinal-keyed dicts populated in `_cancel_worker`; post-barrier fence exits + scan arms fire exactly as today |
| Spontaneous CancelledError in a Phase-1 worker (watchdog-cut shape) | gather-captures it (baseline parity — O-W's baseline IS the gather) | NORMATIVE `task.result()` resurfaces it → followers NEVER dispatch (OWP9) |
| Crash mid-Phase-1 | the entry-time reconstruct gates intercept BEFORE the barrier on resume; partition recomputes over the reconstructed LIVE plan | same |

## 4. Degenerate-reduction table (the byte-preservation contract)

| Input shape | Today (O-W has NO gate) | Under this arc |
|---|---|---|
| All workers same non-None key | all concurrent (cache-miss storm) | phase1={first}, phase2=rest — THE new serialize-worker[0] behavior (ADR-D4 §1.8 steps 2–4) |
| Heterogeneous multi-member cohorts | all concurrent (per-cohort storms) | K leaders Phase 1, followers Phase 2 — the §25.19 partition |
| Any/all keys None / non-capable / all-distinct | all concurrent | phase2 empty → gate False → all-concurrent BYTE-IDENTICAL |
| `len(branch_plan) < 2` | all concurrent (trivially) | short-circuit; zero oracle calls — BYTE-IDENTICAL |
| `concurrent_cache_warmup=False` | all concurrent | gate False; split never computed — BYTE-IDENTICAL |
| Existing O-W test corpus (zero capable stubs) | green | gate False everywhere → unchanged-green (the regression net) |

## 5. Witness plan (`harness-cp/tests/test_workflow_driver_orchestrator_workers_warmup.py`, NEW file)

| # | Witness | Pins | Fails on main? |
|---|---|---|---|
| OWP1 | PROCEED two-cohort (A,A,B,B workers): each cohort's leader completes before ITS followers start | per-cohort serialization through `_proceed_fanout` | YES (all-concurrent on main) |
| OWP2 ×2 (param) | strict tiers: same two-cohort ordering via `_cancel_fanout` | partition on strict tiers | YES |
| OWP3 | leaders BLOCK until a None-key worker completes (would deadlock if the None-branch were Phase 2) | non-beneficiary Phase-1 placement (D4) | control (deadlock-detector; green both) |
| OWP4 | all-distinct keys + reverse-completion → all-concurrent | all-singleton cohorts → gate False | control (green both) |
| OWP5 | CASCADE_CANCEL: leader failure → followers of ALL cohorts withheld — dispatch-marker ABSENCE + scan `cancelled` | effect-set + obligation-4 under partition | YES |
| OWP6 | PROCEED: one leader fails → Phase 2 still dispatches (incl. the failed cohort's followers) → PARTIAL, with followers-start-after-Phase-1 pinned | H1 generalization | YES (ordering half) |
| OWP7 | PAUSE deadline wedge in multi-cohort Phase 1 → withheld followers `cancelled` via the deadline-exit scan; in-flight cut records `timed_out` | ML-family generalization at the O-W deadline exit | YES (marker/disposition shape) |
| OWP8 | PAUSE partial-recovery resume with heterogeneous remainder → re-computed partition (new leaders over the LIVE plan) | D2 LIVE-plan recompute | YES |
| OWP9 | strict: Phase-1 leader's dispatch raises SPONTANEOUS CancelledError → resurfaced; followers' dispatch markers ABSENT + Phase 2 never dispatches | D6 NORMATIVE `task.result()` collection — the swallow-window closer | YES (vs a naive-TaskGroup impl AND vs main's all-concurrent) |
| OWP10 | PROCEED cross-cohort leader∥leader Phase-1 concurrency | leaders are concurrent WITH each other | control (deadlock-detector) |
| OWP11 | strict PAUSE: a Phase-1 worker's child PAUSES → followers omitted from the snapshot (re-dispatchable) + paused-child captured; NO follower terminal synthesized | partition × paused-child third-disposition composition; PAUSED boundary scan-free | YES (on main followers dispatched → appear terminal in the snapshot) |
| OWP12 | strict CASCADE_CANCEL resume: a recovered-fence-peer ordinal withheld as a Phase-2 FOLLOWER → scan arm (3) records `completed` CAPTURE-LESS at the CASCADE_CANCEL exit (review C4) | fence-family × partition composition — the recovered-union arm fires for a withheld follower | YES (on main the peer re-dispatches concurrently — no withheld state) |
| — | existing O-W suites (`test_workflow_driver_orchestrator_workers.py` + `_fence_ledger.py`, zero capable stubs) | gate-False byte-identity | regression net |

**Structural-reachability note (review C4).** At HEAD only INFERENCE_STEP dispatchers are
`CohortKeyCapable` in production, so fence-family (TOOL_STEP) and paused-child (sub-agent)
ordinals are structurally Phase-1 NON-BENEFICIARIES — never withheld-by-partition in production.
Withheld-as-follower for those dispositions is constructible only via a capable stub of those
kinds (OWP11/OWP12 use one); the witnesses pin the composition contract AGAINST the day a second
capable kind lands. **Regression-net scope (review cosmetic 2):** NO O-W-reaching suite anywhere
(HD / fanout-pause / output-replay / handoff / cascade-policy / branch-substrate + runtime
integration) references `CohortKeyCapable`/`cohort_key`, and runtime integration fixtures never
bind `frozen_tool_superset` → production `cohort_key()` returns None → gate False there too.
Under default-on, a FUTURE fts-bound O-W integration fixture silently opts into the partition —
named tripwire, not a defect.

## 6. What does NOT change

- ZERO store-write changes; ZERO new crash-visible additions. All store writes remain inside
  `_cancel_worker` / the scan arms, ordinal-keyed.
- Run statuses, fail_classes, step counts, ledger entry shapes, snapshot schemas: byte-unchanged.
- §5.2 IS-hash, contracts, enums, CXA edges, `WorkflowManifestEntry` fields,
  `D4MultiplicativeTunable`, `CohortKeyCapable`, `cohort_key()` implementations: untouched.
- The obligation-4 scan closure + all EIGHT O-W call sites: untouched. PAUSED boundary scan-free.
- `_execute_parallelization`: untouched (its §25.19 build is the shipped reference).
- The orchestrator dispatch (:9852), the resume/material-diff guards, the reconstruct block,
  the fold/synthesis surfaces: untouched.
- Evaluator-optimizer executor: untouched (CONTINGENT cell, D9).

## 7. Spec + accounting

- CP spec v1.95 → v1.96: §25.19 EXTENDED to ORCHESTRATOR_WORKERS (delta change-note records
  D1–D10: the gate/split site, the inline-lookup not-bound→non-capable adaptation, PROCEED
  two-gather, strict inline two-phase + NORMATIVE resurface, orchestrator-not-a-cohort-member
  named rejection, HD per-level inheritance, E-O contingency discharge-forward, scan-family
  untouched, default-on carried). **Explicit v1.89 supersession** (review C3): the "warmup is
  irrelevant outside PARALLELIZATION" characterization + the `d4_tunable` docstring param note
  are superseded; docstring refreshed in-arc. No new contract / ADR / enum / fail-class / CXA
  edge.
- Clearance marker + bundled-absorption (spec + impl + witnesses in one PR, the slice cadence).
- Arc-ledger: `B-18-PREWARM-OW` registered → closed (standalone 78→79; registered 1→0 — the
  `B-*` registered queue EMPTIES at this close). Snapshot bumped same-commit.
- Runtime spec / IS / OD / AS / CXA: UNCHANGED.
