# R-FS-1 E-impl-3b / RECONCILER_LOOP — Impl Finding (U-RT-123 durable etcd-style substrate)

**Authored:** 2026-06-15 · **Arc:** R-FS-1 child arc **E** (durable-execution engine classes), **E-impl-3b** leg (the RECONCILER_LOOP durable substrate; the runtime half of E-3, after E-impl-3a/#572 landed the CP/IS resumption materialization U-CP-96) · **Posture:** Phase-7 execution (edits `harness-runtime/src` + tests; this `.harness/` finding + the council ledger at `.harness/council/u-rt-123-cas-lease/` are the back-flow substrate accompanying the impl PR — the bundled-impl + `.harness/`-doc pattern, root `CLAUDE.md` §11.4) · **HEAD at authoring:** `0c0bf66` (the WIP-substrate commit this PR rewrites).

**What this records.** E-impl-3b materializes **U-RT-123** — the hand-rolled (I-6, no vendored K8s/etcd) **durable etcd-style reconciler `EnginePauseResumeSubstrate`** — as **impl-against-cleared-spec** against C-CP-07 §7.1 row 4 / §7.4 (v1_33 substrate impl-discretion) + C-CP-08 §8.1 `reconciler_converge`, per the E-3 plan decomposition (`.harness/r-fs-1-e3-plan-decomposition.md` §2 U-RT-123). The HOW was decided by a **genuine multi-agent council** (5 voices + adversarial + Codex out-of-family + advisor; 4-way convergence; operator-ratified 2026-06-15) — the design rationale lives at `.harness/council/u-rt-123-cas-lease/DELIVERABLE.md`; this doc records the IMPL + the impl-surfaced findings. Findings surfaced during impl are recorded here (none is a halt — see §5 classification).

---

## §1 — What landed (U-RT-123)

The WIP substrate at commit `0c0bf66` shipped a **defeated owner-token CAS** ([P1], Codex-found): a per-`(workflow, resource_version)` `O_EXCL`/`os.link` claim stamped with `owner = str(attempt.resume_request_actor)`, same-owner re-acquire allowed. The defect: `resume_request_actor` defaults to the SHARED `harness-runtime` actor for every process (`engine_recovery_loop.py:167` `resume_request_actor or self.actor`), so two concurrent DISTINCT reconcilers carried the SAME token, both passed the same-owner re-entry check, and both re-executed → **double-execution**. The static owner-identity cannot distinguish (a) crash-then-retry by one logical reconciler (prior DEAD → MUST re-enter) from (b) two concurrent distinct reconcilers (both LIVE → exactly one proceeds); the real discriminator is liveness/time, not identity.

**The core correction (the design win).** etcd's compare-and-swap compares `mod_revision` — it is **optimistic concurrency on the resource revision, NOT an owner-identity mutex**. U-RT-123 realizes the genuine primitive: a **write-back-conditional CAS on `resource_version`** over the engine-owned convergence store. **NO owner token.**

| Surface | Delivers |
|---|---|
| **`reconciler_pause_resume_substrate.py`** (REWRITTEN) | `ReconcilerEnginePauseResumeSubstrate` subclassing the #475 `JournalEnginePauseResumeSubstrate`: per-revision checksum-framed, monotonic-`resource_version`-stamped convergence log + contiguous-valid-prefix recovery (torn tail discarded; gap-safe, stops at first corruption) + fsync durability (the U-RT-121 sibling structure). The NEW floor-(iii) capability over WAL: **`_claim_resume_revision` — write-back-conditional CAS on `resource_version`** (the etcd `mod_revision` analogue) via the POSIX `O_EXCL`/`os.link` atomic create on `(workflow, revision)`. FIRST resume of a revision wins; ANY later resume of the SAME revision loses (`FileExistsError` → `ABORT_REVALIDATION_FAILED`; → §22.1). Crash-atomic publish (fsync'd `host:pid` incarnation stamp to a uuid temp, then `os.link` into place — a crash leaves at most an orphan temp, never a half-published claim). |
| **`LeaseBackend` enum** (NEW, `harness_runtime`-private) | `{LOCAL_SINGLE_HOST (default, zero-config), SHARED_STORE_CAS}` — the parameterize-and-assert backend. `harness_runtime`-PRIVATE: it MUST NOT leak into `harness_cp.pause_resume_protocol` / the cleared C-CP-22 Protocol signature (X-AL-3-clean — a substrate choice within v1_33 §7.4 impl-discretion, not a new contract). |
| **`_assert_atomic_link_or_fail_closed`** (SHARED_STORE_CAS only) | A one-shot **SAME-HOST sanity probe**, HONESTLY labeled NOT a cross-host CAS verifier; fail-closed via a substrate `RuntimeError` (NOT a `ResumeOutcome` — store-unverifiability stays OUT of the closed enum) if the store cannot back atomic create-exclusive. The cross-host guarantee reduces to the operator's config-time declaration that the store has atomic `link`/`O_EXCL` (NFSv4/lockd or a shared block volume). |
| **20 tests** | The keystone `test_cas_concurrent_resume_one_wins_one_aborts` + the genuinely-concurrent OS-process variant (`subprocess.Popen` × 3, robust vs spawn-Pool-under-pytest re-import fragility); `test_crash_after_claim_retry_of_claimed_revision_aborts` (the honest F-1 limit); per-workflow + per-revision CAS scoping; torn-tail/gap-safe recovery; the parameterized-backend fail-closed; + the [P2] regression test (§2). |

`PathClass.STATE_LEDGER` (existing closed enum → IS-AL-1-clean, no IS delta). Lost race → `ABORT_REVALIDATION_FAILED` (the closed C-CP-22 `ResumeOutcomeKind`, X-AL-3-clean — no new primitive).

---

## §2 — Decorrelated CODE review reconciled to zero (Codex out-of-family + advisor transcript-aware)

Per root `CLAUDE.md` §13.1 (a high-blast-radius concurrency rewrite of a durable substrate → pre-merge decorrelated review). The two reviewers **independently converged on the SAME bug** — strong decorrelation signal (`[[hooks-codex-pilots-decorrelation-validated]]`):

- **[P2] fixed-probe-name collision** (`_assert_atomic_link_or_fail_closed`): a FIXED probe target (`.cas-atomicity-probe`) made two concurrent `SHARED_STORE_CAS` startups over the same shared dir — OR a startup after a prior crashed startup left the probe — collide (`B`'s first `os.link` hits the leftover → `FileExistsError` → spurious `UNSAFE` RuntimeError on a perfectly atomic store). Codex `[P2]` (out-of-family, diff-only) and advisor (transcript-aware) flagged it independently. **Fix:** uuid-unique probe TARGET per invocation (`probe = .cas-atomicity-probe.{uuid4}`); `finally`-unlink both (no orphan litter). The atomicity property is still tested (link the same tmp to the same unique target twice; the second must raise `FileExistsError`).
- **Regression test proven NON-VACUOUS** (`test_shared_store_cas_startup_tolerates_stale_probe_file`): a contrasting-baseline test pre-creating the EXACT fixed name the pre-fix code used. Verified by execution — a temporary revert of the probe target to the fixed name makes the test FAIL (`FileExistsError` → the false fail-closed); restoring the uuid token makes it pass. (`[[conformance-validator-disciplines]]` — a named finding → enforcement + contrasting-baseline test; `[[built-but-vacuous-reground-ledger-asis]]`.)

Post-fix: ruff clean, pyright 0/0/0, 20 reconciler tests pass; full `harness-runtime` suite **1742 passed / 18 skipped / 1 xfailed** (the lone failure is `test_r410_container_tool_execution_e2e` — a local Docker-daemon 500/API-version environment artifact, unrelated to this change).

---

## §3 — Finding O-E3b-1 (the run-scoping precondition on U-RT-124's binding — advisor-caught, resolved favorably)

**The blind spot the tests + Codex (diff-only) + the probe-bug catch all structurally missed** (advisor, transcript-aware; `[[durable-recovery-presence-validity-scope]]` — "run-scope storage, plain workflow_id in ledger"): the substrate keys EVERYTHING — `_claim_file` / `_journal_file` / `_lock_file` — off `attempt.paused_workflow_id` only (`sha256(str(workflow_id))`), and `attempt_resume(attempt)` receives **no `run_id`**. Every test runs a single run with a plain workflow_id, so they cannot surface a **cross-run claim-file DoS**: a completed/crashed prior run's lingering `{sha256(wf)}.vN.claim` would, for a fresh run of the same `workflow_id` converging to revision `N` again, collide on `os.link` → `ABORT_REVALIDATION_FAILED` on **every future run** — a permanent false-abort. **Worse than the E-impl-2 WAL case** (Codex round-4 [P2]) because the lingering artifact is a **lock that blocks**, not just a stale data record.

**Resolved favorably by empirical grounding (NOT a code defect in U-RT-123):** run-scoping is ALREADY built and **engine-class-AGNOSTIC** — `engine_recovery_loop.py:30-54` `run_scoped_substrate_key(workflow_id, run_id)` composes a collision-free `sha256(b"engine-pause" \x1e wf \x1e run)` and `RuntimeEngineRecoveryLoop` passes it AS the substrate's `paused_workflow_id` on EVERY `capture_pause` / `attempt_resume` / `has_pause_record` path (`:115/:134/:165`), regardless of which `ResumableEngineSubstrate` is bound (the loop "binds ONE substrate and is class-blind" — plan-decomp §3 item 5 + §3 row 69). So when U-RT-124 binds the reconciler substrate **through `RuntimeEngineRecoveryLoop`** (the same loop the WAL substrate uses), run-scoping is inherited for free — the cross-run claim-file DoS is structurally prevented (a different `run_id` → a different digest → a disjoint claim-file namespace).

**The committed precondition (registered here so it cannot become a silent re-introduction of the E-impl-2 bug):** **U-RT-124 MUST bind the `ReconcilerEnginePauseResumeSubstrate` through `RuntimeEngineRecoveryLoop`** (which run-scopes the storage key), NEVER a direct/plain-`workflow_id` binding. This is an explicit AC on U-RT-124 (composes with finding O-E3-1, the substrate-selection mechanism). Within a SINGLE run, claim-file accumulation across revisions is **retention residual** — the same accepted bar as E-impl-2's per-run segment files (note, don't fix; a separate retention/compaction refinement).

---

## §4 — Routed findings (committed FULL-SPEC build arcs — NOT silent absorption; X-AL-3)

Per the council DELIVERABLE §B and the FULL-SPEC standing directive (`[[feedback-full-spec-beyond-mvp-nothing-deferred]]`): these are **committed build arcs**, registered so fork+raise is not-a-defer (`[[spine-ledger-forward-arc-registration]]`). The HOW stays I-6 hand-rolled.

| Finding | What | Registration home |
|---|---|---|
| **F-1 — case-(ii) zombie / crash-mid-resume fence (CP-scope)** | A holder that WON the claim then crashed (or GC-paused) mid-re-execution is already inside the CP driver step-loop (`workflow_driver.py:1681`) and never re-calls `attempt_resume`. The substrate fail-closes that window to HITL (a retry of an already-claimed revision ABORTs → §22.1), never a double-execution. AUTO-recovering it needs the CP driver to hold the engine lock across the full suffix OR consult the engine generation per step-commit. | **Directive on the immediate-next units U-CP-96/97** (already in the frozen E order) + this finding — NOT a parallel B-* row (advisor: don't over-proliferate; `[[grounding-reveals-claude-closeable-slice-close-honestly]]`). |
| **F-2 — floor-(ii) at-most-once EXECUTION (effect-boundary fencing)** | The CAS guarantees at-most-once *claim of a revision*, not at-most-once *execution* of the workflow steps the resume re-runs (a non-idempotent external effect — git_push/send_email — fires, THEN a stale claimant can fail). The `idempotency_key` is on the `cp.resume-attempted` AUDIT entry, not the effect. | **NEW B-* arc `B-EFFECT-FENCE`** in `.harness/beyond-mvp-capability-boundary-ledger.md` (the one genuinely-new capability). |
| **F-CC — multi-host AUTO crash-recovery (the constraint-collision) + the cross-host stale-revision window** | Cross-host AUTO crash-recovery (a maybe-dead cross-host holder) is distributed-systems-impossible under {I-6 no-vendored-consensus ∧ no-unsafe-TTL} (the failure-detector/FLP problem). **HITL-mediated multi-host recovery (fail-closed to §22.1) is the spec-faithful posture** (Reading A: §7.4/ADR-D1 §1.1 name the durable-store *mechanism*, not auto-vs-HITL; §22.1 escalation is contract-blessed). The cross-host stale-revision window (a concurrent capture bumping head N→N+1 during a resume's post-claim diff/revalidate on stale N; same-host the `flock` prevents it) folds here. Genuine AUTO multi-host is reachable hand-rolled only AFTER F-2 (a fenced bounded-synchrony lease, fenced-safe at every sink). | **Carried to the already-deferred O-E3-2** deployment-admissibility gate + the existing Bucket-A "Engine classes" item (multi-host isn't reachable now anyway) — NOT a new parallel B-* row. |

Single-host is **COMPLETE for both correctness cases** (case b via the CAS; case a via flock-release-on-death + durable-log recovery). With the CP-side F-1 fence (U-CP-96/97), case-(ii) zombie also closes on single-host.

---

## §5 — Classification (per `phase-7-back-flow-routing` §2.4): Class-3, NOT Class-1

| Class-1 indicator | Present? |
|---|---|
| Spec contract under-specifies a surface | NO — C-CP-07 §7.4 (v1_33 substrate impl-discretion) + the council DELIVERABLE decide the HOW within that cleared latitude; no spec amendment. |
| Plan signature cannot be materialized | NO — U-RT-123 is a drop-in `EnginePauseResumeSubstrate` for the class-blind recovery loop, exactly as U-RT-121 (plan-decomp §3 item 5). |
| ADR commitment contradicted | NO — I-6 hand-roll honored (no vendored etcd/K8s); the revision-CAS is the genuine etcd `mod_revision` primitive, not a relax-I-6 vendor pull (the relax-I-6 alternative was ELIMINATED as spec-violating at ratification). |
| New H_T primitive surfaced (X-AL-3) | NO — consumes the closed `ResumeOutcomeKind` / `PathClass` enums + the cleared C-CP-22 Protocol; the `LeaseBackend` enum is `harness_runtime`-private and never widens the cleared Protocol. |
| Cross-axis edge cardinality contradicts CXA | NO — no new cross-axis import (the substrate imports `harness_cp.pause_resume_protocol` + `harness_cp.handoff_context`, identical to the sibling WAL/Journal substrates); no new CXA edge. |

The findings are observations + committed build arcs (Class-3, §2.3 CONTINUE). **No operator gate beyond the one the council already took (the ratified design); driven autonomously + reported** per `[[feedback-gate-only-on-meaningful-architecture-change]]` — E-impl-3b confirms U-RT-123 follows the cleared impl-against-cleared-spec verdict and does not change the architecture.

---

## §6 — Files

- `harness-runtime/src/harness_runtime/lifecycle/reconciler_pause_resume_substrate.py` — REWRITTEN: the revision-CAS `ReconcilerEnginePauseResumeSubstrate` (replacing the defeated owner-token CAS), `LeaseBackend` enum, `_claim_resume_revision`, `_assert_atomic_link_or_fail_closed` (uuid-unique probe target — [P2] fix), per-workflow flock + per-revision claim, durable per-revision convergence-log I/O.
- `harness-runtime/tests/test_reconciler_pause_resume_substrate.py` — REWRITTEN: 20 tests incl. the OS-process concurrent-CAS keystone, the honest F-1 limit, the parameterized-backend fail-closed, and the [P2] non-vacuous regression test.
- `.harness/council/u-rt-123-cas-lease/` — the genuine multi-agent council ledger (CHARTER · A1/A2/B · adversarial · Codex/advisor · RECONCILE · DELIVERABLE); the design rationale + the operator ratification (DELIVERABLE prose tightened: same-revision-collision mechanism + the cross-host stale-revision caveat folding into F-CC).
- `.harness/beyond-mvp-capability-boundary-ledger.md` — NEW `B-EFFECT-FENCE` forward arc (F-2).
- This finding doc.
