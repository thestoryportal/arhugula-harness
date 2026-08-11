# Class 1 fork — B-145 GAP-2a: the Runtime escalate clauses are written against a phantom staircase API

**Status:** ✅ APPLIED-AS-(B) (Runtime v1.115 → v1.116, this PR) — adjudicated via
loop-mode decorrelated review per
`[[feedback-noncoding-operator-decorrelated-adjudication]]`: out-of-family codex
verdict **OPTION B**; transcript advisor verdict **VOTE: B** (agreement; RESOLVE
row logged at `.harness/loop_status.md`). Clearance
`spec-harness-runtime-v1-116-cleared-2026-08-11.md`.

*Filed 2026-08-11 by the loop orchestrator (B-145 GAP-2a leg — the last open
B-145 leg; grounding split at `.harness/b145-grounding-split-2026-08-11.md`;
dispatch-path sibling discrepancy routed here by PR #1306's branch-contract
witness). All cites re-read at HEAD this session.*

## The discrepancy

`Spec_Harness_Runtime_v1.md` §14.6 (:4236) and §14.9 (:5692) both order the
retry composers to *"advance the staircase via
`ctx.retry_breaker.advance_staircase(policy, attempt_count,
validator_fail_class)`"* and to stamp `retry.terminal = "escalate"` *"if
staircase result escalates beyond `RETRY_WITH_BACKOFF`"*.

That signature **never existed**. The landed library API is
`advance_staircase(current: StaircaseStage, cause: ValidatorRetryExitClass,
attempt: int)` — a **stage-keyed** lookup
(`harness-cp/src/harness_cp/validator_fail_transient_staircase.py:238-267`)
whose docstring states `attempt` is *"carried for caller bookkeeping and does
not alter the deterministic transition lookup"* (:252-253). The spec bullets
were authored against a hypothesized attempt-indexed API in which the staircase
itself escalates with `attempt_count`; the landed API escalates only if the
**caller threads the stage** across attempts.

No production caller threads it:

- `retry_breaker_tool.py:252-256` passes `STAGE_1_REFLEXION` hard-coded per
  attempt; `(STAGE_1, TRANSIENT_RETRY) → STAGE_2` is unconditional
  (`validator_fail_transient_staircase.py:114-120`), so "escalates beyond
  RETRY_WITH_BACKOFF" cannot occur on the tool path.
- `retry_breaker_fallback.py:1365-1367` likewise passes `STAGE_1` fresh per
  attempt, under an explicit documented reading (:1221-1231): the staircase is
  consulted as a **cause-class classifier** — transient classes → STAGE_2
  (retry), skip-classes → STAGE_5 (escalate). Its escalate branch is live code
  but unreachable today because `_classify_provider_exception` returns only
  `TRANSIENT_RETRY` or `None` (PR #1306 stamped it with a branch-contract
  witness, `test_b145_terminal_escalate_branch_contract`, and routed the
  discrepancy here).
- The staircase's true home — the C-CP-21 validator surface — has **no**
  `advance_staircase` caller at all: `validator_escalation_composer.py:33`
  imports only `CrossTrustBoundaryState` (palette restriction).

## The two candidate resolutions

**(A) Thread the stage across attempts** (make escalate genuinely reachable).
Rejected on four grounds:

1. **It silently overrides the operator-supplied `RetryPolicy`.** With
   threading, a 2nd consecutive transient yields `(STAGE_2, TRANSIENT_RETRY) →
   STAGE_3` = escalate — capping effective attempts at 2 regardless of
   `max_attempts` (an operator-supplied contract surface at §14.6 step 1 /
   §14.9 bullet 1, default 3). The §14.6/§14.9 "bounded by
   `RetryPolicy.max_attempts`" loop bound and the max-attempts terminal become
   dead letters — the defect is inverted, not fixed.
2. **STAGE_3 is semantically void on the tool path.** `CROSS_FAMILY_FALLBACK`
   presumes model-family candidates; tool dispatch has none (§14.9 bullet:
   *"no `rebound` operation — tool dispatch has no candidate parameter to
   override"*). The spec's own tool-path escalate examples (:5692) omit
   `CROSS_FAMILY_FALLBACK`, conceding the mismatch.
3. **The dispatch path already realizes stages 3–5 structurally.**
   Cross-family fallback IS the candidate-chain advance (`advance_or_raise`);
   local-terminal IS the chain floor; HITL escalation IS the driver's terminal
   `RT-FAIL-*` mapping per C-CP-25 §25.3.3.4. Threading would duplicate the
   mechanism inside the per-attempt loop — a second authority for the same
   escalation truth.
4. **C-CP-21 §21.2 does not bind these call sites.** The §21.2 staircase is
   indexed by *validator* fail count (`validator.fail.class ∈ {transient-retry,
   Reflexion-recoverable}` — `Spec_Control_Plane_v1_2.md:1855-1878`, preserved
   into v1.3); the retry composers classify *provider/tool transport* errors.
   The ADR-D3 cite at :5676 composes the "retry-staircase semantics" as a
   shared library API, not as a mandate that transport retries traverse the
   validator staircase.

**(B) Ratify the carve-out** (recommended). Amend the two Runtime escalate
clauses to state the as-built composition as canonical:

- The staircase at BOTH retry composers is consulted **stage-fresh**
  (`STAGE_1` per call) as a cause-class classifier; the call-shape prose is
  corrected to the landed `advance_staircase(current, cause, attempt)`
  signature.
- The `retry.terminal = "escalate"` clause is a **defensive branch contract**:
  it fires iff the composer's transient classifier ever yields a transition
  beyond `STAGE_2` (e.g. a future skip-class return), and is UNREACHABLE at
  the v1.116 classifiers — matching the #1306 branch-contract witness on the
  dispatch path and a mirrored witness on the tool path.
- Model-tier escalation semantics on these paths remain realized structurally
  (candidate-chain advance / chain floor / driver terminal mapping); making
  the staircase-driven escalation genuinely reachable (stage threading) is
  declared a future design arc requiring its own back-flow.
- C-CP-21 §21.2 itself is untouched — it stays canonical for the validator
  surface it was authored for.

## Blast radius

Spec prose (Runtime §14.6/§14.9 escalate + staircase-call bullets) + one
impl companion (tool-path defensive escalate branch, mirroring #1306's
dispatch-path treatment) + witnesses. Zero behavioral change to any reachable
path. `retry.terminal` value set unchanged (all five values remain declared;
two remain defensively-contracted). No CXA seam change; no C-CP-21 change; no
ADR change.

## Routing

Class 1 (spec revision) per `Project_Workflow_v1_8.md` §2.7.6 →
`Spec_Harness_Runtime_v1.md` v1.115 → v1.116 amendment + clearance marker,
bundled-absorption arc per root `CLAUDE.md` §11.4 (this fork doc is the
back-flow documentation; X-AL-3 guard satisfied). Closes the last open B-145
leg; `B-145` register row flips closed at ship.
