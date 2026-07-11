# B-18-EPOCH-PARTITION — pre-build design decision record (decompose-at-open)

*Arc open 2026-07-11 (dedicated session per the dashboard's next-action directive). The sole
registered `B-*` arc. Registered at CP spec v1.87 follow-on table ("version_sha cohort HASH +
heterogeneous partition (warm one per cohort)") and reshaped at
`.harness/u1-slice3b-epoch-partition-design.md` §6 ("3b-epochkey ships coupled with 3c — its only
consumer"). Arc-ledger `anticipated_scope`: partition N branches into K cohorts at the CP fan-out
site and warm one per cohort; the degenerate K=1 case is covered by B-18-3C-PREWARM.*

---

## 0. TL;DR

`[HIGH]` Replace the binary `_same_prefix_cohort() -> bool` (ALL branches must share ONE non-None
cohort key) with a **cohort partition**: group the live `branch_plan` by
`dispatcher.cohort_key(binding, step)`; Phase 1 dispatches one **leader per multi-member cohort
PLUS every non-beneficiary branch** (None-key / non-`CohortKeyCapable` / singleton-cohort)
concurrently; Phase 2 releases the followers. Degenerate K=1 (all-same key) reduces **exactly** to
today's serialize-branch[0] shape; no-multi-member-cohort reduces exactly to today's gate-False
all-concurrent baseline. Zero store-write changes; the §25.15.2 obligation-4 scan is
disposition-keyed and phase-agnostic — untouched. CP spec v1.94→v1.95 (NEW **§25.19**) + clearance.

**Pre-build review disposition (2026-07-11).** Fable-5 adversarial design review (advisor
unavailable — double-outage fallback per `[[fable5-fallback-reviewer]]`): **AMEND-THEN-BUILD, 2
blocking + 5 concern + 4 cosmetic — ALL folded below pre-build.** B1: the original §25.18 target
SHADOWED the live v1.32 baseline §25.18 (impl-discretion + recorded forks; cited at v1.32 §25.15.1
/ §25.15.2-ob.5 + six v1.45 cites) — the wrong-version-read-delta-only-baseline defect class;
re-verified at source; carrier is now §25.19 (zero hits verified across design-substrate + src).
B2: TaskGroup child-CancelledError swallow — CONVERGENT with this session's own probe (both
empirical, independently); reviewer added the REAL reachability vehicle (nested fan-out: the outer
barrier's watchdog registers in every enclosing `_BRANCH_INFLIGHT_DISPATCHES` registry and is
armed δ earlier, so it cuts the INNER fan-out's Phase-1 inflight inside the window where the inner
`asyncio.timeout` has not fired; a sub-agent child running its own `_execute_parallelization` can
also surface a naked CancelledError through `dispatch()`) — without resurfacing, the inner fan-out
would dispatch EVERY follower after the cut, inverting the v1.90 item-4 effect-set subset
invariant on the strict tiers. Mitigation (already in D3-AMENDMENT) is now a NORMATIVE §25.19
obligation + dedicated witness EP9.

---

## 1. Committed sources (all verified byte-exact at HEAD this session)

| Source | Commitment |
|---|---|
| ADR-D4 §1.8 (lines 228–242) | "cache-write at breakpoint" before "cache-hit on shared prefix" at fan-out; **"The protocol applies to all cells where fan-out cap > 1 (orchestrator-workers, parallelization, evaluator-optimizer with multi-evaluator)"** |
| CP spec v1.87 follow-on table | `B-18-EPOCH-PARTITION` — "version_sha cohort HASH + heterogeneous partition (warm one per cohort)" |
| `.harness/u1-slice3b-epoch-partition-design.md` §4.1 | `cacheable_epoch = (agent_role, workload_class) × prefix_content_hash`; byte-exact ⇒ two dispatches share a warm cache iff their `[tools + system]` prefixes are byte-identical |
| CP spec v1.88 §25.16 | `CohortKeyCapable.cohort_key(binding, step) -> str \| None`; 16-hex sha256 over provider\|model\|agent_role\|prompt_version_sha\|thinking\|cache_ttl\|fts_bound |
| CP spec v1.90 | Gate lift above the cascade_policy branch; inline two-phase `_cancel_fanout` (ONE deadline + ONE watchdog); item 3 R3 Phase-1 guard; item 4 effect-set invariant |
| Arc-ledger row `B-18-EPOCH-PARTITION` | "Requires per-cohort cohort_key() from B-18-3C-PREWARM-COHORTKEY plus the epoch-partition key design from §4.1" |

### 1.1 Grounding disposition — the §4.1 "prefix_content_hash" is REALIZED BY `cohort_key()`; no second hash is built

`[HIGH]` The arc-ledger's anticipated `sha256(canonical(frozen_tool_superset) ‖ version_sha)` was
registered BEFORE B-18-3C-PREWARM-COHORTKEY shipped. The v1.88 dispatcher-oracle **subsumed** the
§4.1 key recipe: `cohort_key()` already encodes `prompt_version_sha` (= version_sha) plus the
prefix-stability attributes §4.1 folds in via "canonical(frozen_tool_superset)". The `fts_bound`
SENTINEL (presence, not content-hash) is sufficient **within a fan-out** because
`frozen_tool_superset` is a run-scoped constant on the ONE `RuntimeLLMDispatcher` instance shared
by every INFERENCE branch (stage-5 binding; `branch_dispatchers` resolves per `step_kind` from one
registry) — two branches of one fan-out cannot disagree on fts content. Cross-RUN byte-identity is
arbitrated by Anthropic's cache itself, outside the partition's scope (the partition only groups
branches of ONE fan-out). **The epoch identity for this arc = `cohort_key()`. The residual is the
PARTITION semantics, not a new hash.**

### 1.2 Heterogeneity is real at HEAD (arc is non-hollow)

`[HIGH]` Per-branch `StepEffectiveBinding` varies under the B4 per-step override family:
`StepOverride.prompt_version_sha` (CP v1.37) and per-step model/role overrides produce branches
with different `psha`/`model`/`role` → different cohort keys within one fan-out. Today such a
fan-out gets NO warm-up at all (binary gate False) → each multi-member cohort cache-miss-storms
independently — the exact ADR-F2 §(b)(ii) 4-10× detonation the warm-up exists to prevent, striking
per-cohort.

---

## 2. Design decisions

### D1 — Partition definition + gate

```
if len(branch_plan) < 2: no partition, gate False   # explicit short-circuit: preserves the
                                                    # v1.90 "gate never runs ahead" call-count-
                                                    # exact property (zero cohort_key() calls
                                                    # on a singleton plan) — review cosmetic 1
keys[bi]  = (step.step_kind, dispatcher.cohort_key(binding, step))  if capable and key not None
          = None                                                     otherwise
          # grouping key includes step_kind (review C3): equal 16-hex keys are only attested
          # comparable within one capable dispatcher instance, which the registry resolves
          # per step_kind; at HEAD only INFERENCE_STEP is capable so this is behavior-inert,
          # but it forecloses a silent cross-kind collision if a second capable kind lands
cohorts   = ordinals grouped by non-None (step_kind, key), insertion (= ordinal) order
followers = for each cohort with ≥2 members: members[1:]
phase1    = branch_plan minus followers      (leaders + singletons + None/non-capable)
phase2    = followers, ordinal order
_warmup_gate = _d4.concurrent_cache_warmup AND phase2 non-empty
```

- `[HIGH]` Gate condition "phase2 non-empty" ⟺ "some cohort has ≥2 members" — subsumes the H3
  `len(branch_plan) >= 2` guard (a <2 plan cannot have a 2-member cohort) and the v1.88 None/
  non-capable collapses **for the branches concerned** while no longer letting one unstable branch
  veto sibling cohorts' warm-up.
- `[HIGH]` Deterministic: iteration over `branch_plan` in ordinal order; dict preserves insertion
  order; leader = first-seen ordinal per key. A partial-recovery resume recomputes over the LIVE
  (post-recovery-seed) plan → new leaders per remaining cohort (the v1.90 H3-generalization,
  witnessed today at W4b for K=1).

### D2 — Phase-1 membership: leaders ∪ non-beneficiaries (Option A)

`[HIGH]` Non-beneficiary branches (None-key / non-capable / singleton-cohort) dispatch in
**Phase 1**, concurrently with the leaders. Rationale:

- Cache-neutral either way (no shared prefix with anyone) — but Phase-2 placement would delay them
  behind other cohorts' cache-writes for **zero benefit** (pure latency loss vs the baseline they
  get today).
- Keeps the K=1 degenerate case EXACT: all-same key → phase1 = {first ordinal}, phase2 = rest —
  byte-consistent with today's serialize-branch[0].
- Strict-tier effect-set: a Phase-1 failure withholds only `phase2` (followers). Option B
  (leaders-only Phase 1) would put non-beneficiaries in Phase 2 alongside followers — a LARGER
  dispatched set at any Phase-2 failure. Option A is lower-latency AND smaller-effect-set.

Rejected: **Option B** (leaders-only Phase 1) per above.

Rejected (named per review C2, so the next arc doesn't re-litigate blind): **per-cohort Phase-2
release** (each cohort's followers release when THEIR leader completes, instead of the global
Phase-1 barrier). Latency cost of the global barrier is real — a fast cohort's followers wait on
`max(phase1)` including slow non-beneficiaries, and on strict tiers a non-beneficiary failure
withholds followers of already-completed leaders — but per-cohort release requires K independent
completion signals under ONE shared deadline + ONE watchdog (the v1.90 never-two-barrier-calls
commitment), effectively a third phase structure with per-cohort cancellation scopes. No committed
per-cohort-release grain exists (ADR-D4 §1.8 lines 236–239 is single-breakpoint), the withheld-set
direction matches the v1.90 item-4 subset invariant, and the global two-phase preserves the
CASCADE machinery byte-adjacent. If latency data ever motivates it, it is a registrable follow-on
against this named rejection.

### D3 — Strict-tier Phase-1 shape: uniform `asyncio.TaskGroup` (supersedes the v1.90 item-3 solo+wrap)

`[HIGH]` Phase 1 in `_cancel_fanout` becomes a TaskGroup over `phase1` (even when singleton),
replacing the solo-await + `except asyncio.CancelledError: raise` + manual
`BaseExceptionGroup("cascade-warmup-branch0", [exc])` wrap. The R3 guard's OBLIGATIONS are met
natively by TaskGroup:

- A child's bare `TimeoutError` → `ExceptionGroup([TimeoutError])`, which `except TimeoutError`
  does NOT catch (no implicit group unwrap) → propagates to the caller's
  `except BaseExceptionGroup` → `branch_failed = True`. The R3 classification (branch failure,
  never barrier-deadline) is preserved BY CONSTRUCTION; W7 pins it by execution.
- The outer `asyncio.timeout` cancellation propagates through TaskGroup as `CancelledError`
  (TaskGroup does not wrap parent-cancellation) → `TimeoutError` at `__aexit__` →
  `BranchBarrierDeadlineExceededError`, unchanged.
- Any other child exception (incl. the fence errors) → `BaseExceptionGroup` subclass → identical
  post-barrier classification; the fence dicts are populated inside `_cancel_branch` before the
  re-raise, ordinal-keyed, phase-agnostic.
- Laziness preserved: only `phase1` coroutines are instantiated; a Phase-1 failure never
  instantiates a follower coroutine (the v1.90 no-un-awaited-coroutine-leak property).
- `_BRANCH_INFLIGHT_DISPATCHES`: TaskGroup children copy the context; the registry SET OBJECT is
  shared (exactly the existing Phase-2 mechanics).
- In-flight Phase-1 members on a sibling Phase-1 failure run to completion under
  `dispatch_branch_step_shielded` and record their own terminals — identical to today's Phase-2
  sibling semantics (all handlers live in `_cancel_branch`, per-branch).

**D3-AMENDMENT (empirical, 2026-07-11, verified under BOTH system 3.14.5 and project uv 3.12.13):**
`asyncio.TaskGroup` **SWALLOWS a child's spontaneous `CancelledError`** (the watchdog-cut shape:
the child's awaited future is cancelled, the child task itself was never `.cancel()`ed — the group
exits CLEANLY with `task.cancelled()=True`, even inside an un-expired `asyncio.timeout`). A naive
`async with TaskGroup: create_task(...)` Phase 1 would therefore CONTINUE to Phase 2 in the
microsecond window where the watchdog fired before the outer timeout (the watchdog's
`sleep(deadline)` starts before the `asyncio.timeout(deadline)` block opens, so the window is
real), diverging from main's solo shape (which propagates `CancelledError`). **Mitigation folded
into the design: after the Phase-1 TaskGroup, collect `task.result()` for every Phase-1 task —
a cancelled task re-raises `CancelledError` there — byte-mirroring Phase 2's existing
result-collection shape (`workflow_driver.py:8074`), which is exactly how main's Phase 2 already
resurfaces a swallowed watchdog-cut child.** Probe transcript: scenario A (spontaneous child
CancelledError → group clean, `result()` re-raises), B (same inside un-expired timeout → clean),
C (solo await propagates), D (child bare TimeoutError → `BaseExceptionGroup`, NOT caught by
`except TimeoutError` — the R3 classification holds natively).

The v1.95 delta records this as an explicit supersession of v1.90 item 3 (the guard's obligations
carried by the TaskGroup construction + the mandatory Phase-1 `task.result()` collection; W7
retained as the by-execution pin).

### D4 — PROCEED Phase-1 shape: `asyncio.gather(..., return_exceptions=True)` over `phase1`

`[HIGH]` Generalizes the H1 capture (a leader/Phase-1 failure must still dispatch Phase 2 and
drain buffered entries): gather-with-return_exceptions captures per-branch `Exception`s exactly as
the solo try/except did, and propagates the deadline `CancelledError` exactly as today's Phase-2
gather does. Phase 2 unchanged (gather over followers). Results reassembled in `branch_plan`
ordinal order (D5).

**Named carve-out (review C1 — explicit, not silently absorbed):** a SPONTANEOUS child
`CancelledError` (a branch's own dispatch raising CancelledError, not the outer deadline) is
CAPTURED as a gather result under this shape (→ `any_failed` → PARTIAL), whereas today's K=1
warm-up solo (`except Exception`, workflow_driver.py:7792) lets it escape naked. This ALIGNS the
warm-up path with today's gate=False all-concurrent baseline (also gather-captured) — the solo
shape was the outlier — but it is a real edge-shape change on the K=1 warm-up reduction, named in
§25.19. (The strict tiers are governed by D3's resurface obligation instead: there the
CancelledError MUST propagate — the withheld-followers invariant.)

### D5 — Result assembly

`[MODERATE]` `_proceed_fanout` returns results in `branch_plan` order via an ordinal-keyed map
(today's `[first, *rest]` IS plan order; the only current consumer is order-insensitive
`any_failed`, but plan-order is preserved for shape fidelity).

### D6 — Leader failure does NOT promote a replacement leader

`[HIGH]` If a cohort's leader fails in Phase 1 (PROCEED), its followers still dispatch in Phase 2
and may cache-miss-storm within that cohort — exactly today's committed H1 behavior for K=1
(progress > cost under PROCEED). Re-serializing a promoted leader has no committed basis, adds a
third phase, and pays latency. On the strict tiers the question is moot (any Phase-1 failure
halts the fan-out; followers are withheld).

### D7 — Obligation-4 scan family: UNTOUCHED

`[HIGH]` `_synthesize_undispatched_terminals()` (all five PARALLELIZATION call sites + the O-W
counterpart) keys on writer-disposition ABSENCE + the fence/reconstruct dicts — all ordinal-keyed,
none phase-aware. Withheld Phase-2 followers at any terminal exit get exactly today's arms
(`cancelled` baseline / fence-family `completed` arms). ZERO changes to the scan, to store writes,
to statuses, to fail_classes. The partition changes only WHEN dispatches fire, never what is
recorded about them.

### D8 — ORCHESTRATOR_WORKERS (+ evaluator-optimizer): REGISTER, do not silently widen

`[HIGH]` ADR-D4 §1.8 commits the warm-up protocol for "all cells where fan-out cap > 1
(orchestrator-workers, parallelization, evaluator-optimizer with multi-evaluator)". v1.87
deliberately scoped the BUILD to PARALLELIZATION and no follow-on ever registered the O-W
extension — O-W has NO warm-up gate at HEAD (verified: `_warmup_gate` exists only in
`_execute_parallelization`). Extending warm-up (and the partition) to O-W is its own design pass
(different dispatch mechanics, stash/paused-child machinery, eight scan sites) — the exact shape
that produced B-18-FENCE-LEDGER-FIDELITY-OW as a REGISTERED sibling rather than a silent widen.
**Register `B-18-PREWARM-OW`** (warm-up + cohort partition for the remaining ADR-D4 §1.8 cells) at
the arc-ledger in this PR.

### D9 — routing_activation carve-out (v1.88): carried unchanged

`[MODERATE]` Content-sensitive routing may promote different models per branch despite equal
cohort keys → warm-up serializes without cache benefit (latency-only). The partition neither fixes
nor worsens the fidelity of `cohort_key()`; the carve-out text carries forward verbatim. (It
remains a runtime-side `cohort_key()` sharpening, not a CP partition concern.)

### D10 — Witness-contract change: CK-3 premise is superseded (explicit, not silent)

`[HIGH]` `test_cohort_key_capable.py` CK-3 (keys A/B/B + reverse-completion, asserting
non-uniform → all-concurrent) breaks under the partition — its premise is exactly the contract
this arc supersedes. Precise failure mode (review C4 trace, replacing this DDR's earlier
"deadlock" wording): SOLO_DEVELOPER → PROCEED; cohorts A={0}, B={1,2} → phase1={0,1},
phase2={2}; branch 1 blocks on event[2] (withheld) and branch 0 on event[1] → both
`assert wait(timeout=10.0)` fail CONCURRENTLY at ~10 s inside the to_thread dispatch →
AssertionErrors captured by the Phase-1 gather → Phase 2 dispatches branch 2 clean → run
PARTIAL ≠ asserted SUCCESS → **test fails in ~10 s** (not a live deadlock, not a 300 s barrier
hang). Every other capable fixture in the warm-up/fence/reconstruct suites returns the single
uniform key → K=1 exact reduction → unchanged-green (all 12 capable stubs enumerated by the
review). Disposition:

- CK-3 is RESHAPED to the surviving half of the old contract: all-DISTINCT keys (A/B/C) → every
  cohort singleton → gate False → all-concurrent (reverse-completion still proves it).
- The superseded half (multi-member cohort + differing branch) is pinned by the NEW EP witnesses
  (below) asserting partition behavior instead.

---

## 3. Failure-semantics table (per tier × phase)

| Event | PROCEED | CASCADE_CANCEL / PAUSE |
|---|---|---|
| Phase-1 member fails | captured (gather return_exceptions) → Phase 2 still dispatches → PARTIAL | TaskGroup cancels in-flight Phase-1 peers (shielded → run to completion, record terminals); Phase 2 withheld; post-barrier: FAILED / pause path; scan records followers `cancelled` (or fence arms) |
| Deadline strikes in Phase 1 | in-flight record `timed_out` at own handler; withheld followers get scan `cancelled`; PARTIAL | same mechanics; `BranchBarrierDeadlineExceededError` → FAILED (+ scan at the enumerated exits) |
| Phase-1 all-clean | Phase 2 gathers (per-branch capture) | Phase 2 TaskGroup (first failure cascades) |
| Fence pause/abort in Phase 1 | n/a (PROCEED fence-resume rejected pre-dispatch; aborted/paused dicts unreachable) | ordinal-keyed dicts populated in `_cancel_branch`; post-barrier fence exits + scan arms fire exactly as today |
| Crash mid-Phase-1 | entry-time reconstruct gates (v1.68/v1.70/v1.71) intercept BEFORE the barrier on resume — partition recomputes over the reconstructed LIVE plan | same |

## 4. Degenerate-reduction table (the byte-preservation contract)

| Input shape | Today | Under partition |
|---|---|---|
| All branches same non-None key | gate ON: branch[0] solo, rest Phase 2 | phase1={first}, phase2=rest — SAME dispatch schedule |
| Any branch None / non-capable, rest uniform ≥2 | gate OFF: all concurrent | None-branch Phase 1 (immediate, as today) + cohort warms — CHANGED (the arc's purpose) |
| All keys distinct | gate OFF: all concurrent | all singleton → phase2 empty → gate OFF — SAME |
| All None / non-capable | gate OFF | phase2 empty → gate OFF — SAME |
| len(branch_plan) < 2 | gate OFF (H3) | no 2-member cohort possible → gate OFF — SAME |
| `concurrent_cache_warmup=False` | gate OFF | gate OFF — SAME |
| Heterogeneous multi-member cohorts | gate OFF: all concurrent | K leaders Phase 1, followers Phase 2 — THE new behavior |

## 5. Witness plan

| # | Witness | Pins | Fails on main? |
|---|---|---|---|
| EP1 | PROCEED two-cohort (A,A,B,B): each cohort's leader completes before ITS followers start (CK-1 sleep+event pattern per cohort) | per-cohort serialization | YES (all-concurrent on main) |
| EP2 | strict tiers ×2 (param): same two-cohort ordering via `_cancel_fanout` | partition on strict tiers | YES |
| EP3 | leaders BLOCK until a None-key branch completes (would deadlock if None-branch were Phase 2) | non-beneficiaries dispatch in Phase 1 (D2) | control (green both — deadlock-detector; review C5 label fix) |
| EP4 | all-distinct keys + reverse-completion → all-concurrent | singleton cohorts → gate False (CK-3 successor) | control (green both) |
| EP5 | strict tier: leader failure → followers of ALL cohorts withheld, dispatch-marker ABSENCE + scan `cancelled`; in-flight Phase-1 peers complete | effect-set + obligation-4 under partition | YES |
| EP6 | PROCEED: one leader fails → Phase 2 still dispatches (incl. the failed cohort's followers) → PARTIAL | H1 generalization (D6) | YES |
| EP7 | deadline wedge in multi-cohort Phase 1 → withheld followers `cancelled` via scan | ML-family generalization | YES |
| EP8 | PAUSE partial-recovery resume with heterogeneous remainder → recomputed partition (new leaders) | D1 LIVE-plan recompute | YES |
| EP9 | strict tier: a Phase-1 leader's dispatch raises SPONTANEOUS CancelledError → followers' dispatch markers ABSENT + Phase 2 never dispatches (the B2 resurface obligation; K=1 parity with main's solo re-raise pinned by execution) | D3 `task.result()` collection — the swallow-window closer | YES vs a naive TaskGroup impl (designed to catch the B2 regression) |
| CK-3′ | reshaped all-distinct | surviving old-contract half | — |
| — | existing 29 warm-up + fence + reconstruct + CK-1/CK-2 witnesses | K=1 exact reduction, unchanged-green | regression net |

## 6. What does NOT change

- ZERO store-write changes; ZERO new crash-visible additions (stronger than v1.92/v1.93 — same as
  v1.94). All store writes remain inside `_cancel_branch` / the scan arms, ordinal-keyed.
- Run statuses, fail_classes, step counts, ledger entry shapes: byte-unchanged.
- §5.2 IS-hash, contracts, enums, CXA edges, `WorkflowManifestEntry`, `D4MultiplicativeTunable`,
  `CohortKeyCapable`, `cohort_key()` implementations: untouched.
- PAUSED boundary stays scan-free; the five enumerated terminal exits stay the ONLY scan sites.
- O-W engine: untouched (D8 registration instead).

## 7. Spec + accounting

- CP spec v1.94 → v1.95: **NEW §25.19** (heterogeneous cohort partition: D1 partition incl. the
  (step_kind, key) grouping + len<2 short-circuit, D2 membership + named-rejected per-cohort
  release, D3 TaskGroup supersession of v1.90 item 3 WITH the normative Phase-1 `task.result()`
  resurface obligation, D4 C1 carve-out, D6, D7-unchanged note, D9 carve-out carry, CK-3
  witness-contract note). **§25.18 is TAKEN** (v1.32 baseline: impl-discretion + recorded forks;
  review B1) — §25.19 verified zero-hit across design-substrate + harness-cp/src +
  harness-runtime/src this session.
- Accepted micro-divergence (review cosmetic 2, recorded not engineered-around): under a Phase-1
  TaskGroup child there is one scheduling tick before `_mark_branch_dispatched` where a sub-tick
  deadline could cancel pre-marker; unreachable at the non-injectable 300 s default.
- Clearance marker + bundled-absorption (spec + impl + witnesses in one PR, the slice-cadence).
- Arc-ledger: `B-18-EPOCH-PARTITION` registered → closed (standalone 77→78); NEW row
  `B-18-PREWARM-OW` registered (D8) with the review's scope-note: the ADR-D4 §1.8 third cell
  (evaluator-optimizer multi-evaluator) is CONTINGENT — at HEAD evaluator-optimizer is
  sequential single-evaluator (§25.11), so the registration covers it only if that cell ever
  materializes. Snapshot bumped same-commit.
