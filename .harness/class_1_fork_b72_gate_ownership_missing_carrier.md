# Class 1 Fork — B-72: gate-ownership detection has no carrier for a pre-dispatch fan-out HITL gate pause

**Filed:** 2026-07-25 · autonomous-loop (`roadmap-continue`), round 6 on register `B-72`. **Classification:
Class 1** (the fix requires a NEW carrier field on `PeerFanOutResumeState`/`FanOutResumeState` — an
observable schema change to a P5-CK-cleared mechanism, not impl discretion against unambiguous spec text).
No `design-substrate/**` file is edited by this filing. `B-72`'s close-out net-position item (1) ("delivery-cell
construction alone suffices for the round-3-confirmed single-branch gate-owning case") is **empirically
falsified** by this pass. Status flips `registered_finding` → `design_substrate_gated` on item (1) specifically
(items (2)-(4) were already `design_substrate_gated`/open per round 5).

## §1 What advisor() asked to be verified before any code was written

Round 5's own close-out caveat (out-of-family Codex [P2], explicitly flagged "NOT independently verified
this pass"): `_collect_gate_owning_run_ids` (`workflow_driver.py:2665-2698`) treats any node carrying a
`fan_out_resume`/`peer_fan_out_resume` carrier as an unconditional container, recursing into
`paused_child_branches` regardless of its own `pause_reason` — and `PeerFanOutResumeState` is constructed
whenever *any* branch fails/pauses in a `PARALLELIZATION` run. The caveat's hypothesis: a branch paused at
its own gate with zero dispatched children could compute to an **empty** gate-owning set, meaning
`compute_hitl_uniform_fallback_eligible_run_id` never resolves to that branch's own `run_id` — so the
sanctioned "wire delivery-cell construction into `_execute_parallelization`/`_execute_orchestrator_workers`,
mirroring `workflow_driver.py:4777`" fix (net position item 1) would compile, look complete, and still not
converge the round-3 repro.

Before writing any implementation, `advisor()` was consulted (transcript-aware pre-work check per workspace
`CLAUDE.md` §13.1) and returned exactly this instruction: verify the caveat empirically against the real
captured `PauseSnapshot` from the existing round-3 repro before touching `_execute_parallelization`, because
the answer determines which of two different fixes is being built.

## §2 The empirical check (not reasoning — direct instrumentation of the real object)

Temporary debug prints were added inside
`harness-runtime/tests/integration/test_b72_fanout_sub_agent_dispatch_hitl_gate_resume.py::test_fanout_branch_gate_resume_with_resolved_answer_re_fires`
immediately after the first `resume()` call captured `paused.pause_snapshot`, calling
`compute_hitl_uniform_fallback_eligible_run_id(paused.pause_snapshot, resume_context)` directly and printing
the root snapshot's `pause_reason`, `fan_out_resume`, and `peer_fan_out_resume` fields. Ran via
`pytest ... -s -q`. Output (verbatim):

```
[B72-DEBUG] eligible_run_id=None
[B72-DEBUG] root pause_reason=<WorkflowPauseReason.EXPLICIT_OPERATOR: 'explicit_operator'> run_id='f2ca3718367d4b5fb1c5296265946cb2'
[B72-DEBUG] root fan_out_resume=None
[B72-DEBUG] root peer_fan_out_resume=PeerFanOutResumeState(branches=(), branch_count=1, paused_child_branches=(), synthesis_step_id=None, effect_fence_paused_branches=())
```

**Confirmed:** `peer_fan_out_resume` is non-`None` (so `_collect_gate_owning_run_ids` takes the "container"
branch, never reaching its own-`pause_reason`-check fallback), yet **both** `branches` and
`paused_child_branches` are empty tuples — `branch_count=1` is the only non-empty field. There is currently
**no data captured anywhere** identifying "branch ordinal 0 paused at its own `SUB_AGENT_BOUNDARY` gate,
here is its identity for delivery addressing." `compute_hitl_uniform_fallback_eligible_run_id` therefore
returns `None`, not the branch's own `run_id` — the uniform-fallback arm (`run_id ==
hitl_uniform_fallback_eligible_run_id`) can never fire for this branch, no matter what gets wired into
`_execute_parallelization`.

**A second, independent instrumentation pass measured the mechanism directly** (not just the outcome): a
temporary print immediately before `workflow_driver.py:9698`'s `if branch_failed or
_crash_pause_reestablish:` check, dumping `terminal_dispositions` and `branch_failed`. Output: `terminal_
dispositions={} branch_failed=True`. This confirms — measured, not merely round-1's static trace carried
forward — that `branch_failed` becomes `True` from the `gather(return_exceptions=True)` result scan
directly (an `isinstance(r, BaseException)` check independent of `terminal_dispositions`), while `terminal_
dispositions` itself never gains an entry for this branch's ordinal. `FanOutBranchResumeState` construction
iterates `sorted(terminal_dispositions.items())`, so an ordinal absent from `terminal_dispositions` cannot
produce a `branches` entry either — this is the reason `branches=()` above, not merely a coincidence.

Both debug instrumentation passes were reverted after their checks (`git diff --stat` confirmed clean
before this filing) — neither is part of any committed change.

**One datum this filing does NOT explain, flagged for the spec-leg rather than silently dropped:** the
root `PauseSnapshot.pause_reason` in the captured object is `WorkflowPauseReason.EXPLICIT_OPERATOR`, not
`HITL_PENDING`. Round 3 independently noted a run ending `paused` with `pause_reason='explicit_operator'`
for this same child shape and filed it as "a separate, not-yet-understood quirk" (found via a gate-bypass
experiment, not via this snapshot). Whether this is the same quirk or a related one is unknown. It matters
for §4's recommendation: `_collect_gate_owning_run_ids`'s leaf-branch test checks `pause_reason is HITL_
PENDING` — if the fan-out pause-capture path does not label a HITL-caused pause that way at the ROOT level
(as opposed to whatever reason a per-branch carrier entry would carry, which is a separate, not-yet-existing
field), a new carrier alone might not be sufficient even once added; the reason-labeling convention for a
gate-owning branch's captured entry needs to be part of the same design pass, not assumed compatible with
the existing `HITL_PENDING`-checking leaf test. Root-level `pause_reason` is otherwise documented elsewhere
in this codebase as informational-only and never consulted by the composer's resume path — whether that
same informational-only status applies to whatever NEW per-branch carrier gets added is exactly the open
question here, not a settled fact.

## §3 Why this is Class 1, not a Phase-7 code fix

`PeerFanOutResumeState` (and its `ORCHESTRATOR_WORKERS`/`HIERARCHICAL_DELEGATION` sibling
`FanOutResumeState`) currently has exactly two per-branch carriers: `branches` (terminal dispositions +
outputs for branches that ran to completion or ordinary failure) and `paused_child_branches` (branches whose
*recursively-dispatched child* paused, capturing the child's nested `PauseSnapshot`). Neither carrier has a
slot for "this branch itself paused at its own gate before any child run existed." The gap is structural: a
`HITLPauseRequestedSignal` raised directly from `RuntimeHITLGateComposer`'s Step 0 (before
`_dispatch_inner`/`inner.dispatch()` ever runs) is a `BaseException` that the fan-out branch-dispatch
try/except chain does not catch (round 1's already-confirmed trace — only `CancelledError`,
`SubAgentChildPausedError`, `SubAgentDispatchCapacityError`, and `Exception` are handled), so it propagates
through `asyncio.gather(..., return_exceptions=True)` as a raw captured exception object — never entering
`terminal_dispositions`, never becoming a `FanOutBranchResumeState`, never becoming a
`PausedChildBranchResumeState` (there is no child to have one). Adding a place to capture this case is an
**additive schema change** to a CP-spec-owned carrier (`Spec_Control_Plane_v1_106.md` §1's `PeerFanOutResumeState`
family), which changes what property 4/5's resolver can observe — the same class of change property 4 and
property 5 themselves were (CP spec v1.106's own B-39 spec leg). Per X-AL-3 this is design-substrate-gated,
not Phase-7 impl discretion, and per the workspace's own B-70/B-33/B-39 precedent (a real gap needing a new
spec-level carrier/property before code is `design_substrate_gated`, not `registered_finding`).

## §4 Recommendation (for the eventual spec-leg arc; not built by this filing)

**Stated as a requirement, not a carrier shape** — the exact field name/type is spec-leg design work, not
something this filing should pre-select (round 5's own experience: a first-draft field name/shape was
proposed at the B-39 spec leg, found wrong, and had to be pulled back twice by advisor()/out-of-family
review; prescribing a shape here would repeat that mistake one level earlier):

1. A carrier must exist (on `PeerFanOutResumeState` and its `ORCHESTRATOR_WORKERS`/`HIERARCHICAL_DELEGATION`
   sibling `FanOutResumeState`) that records, for a branch that pauses at its own gate before any child run
   is dispatched, enough identity for a resumed cycle to address a delivered answer to it.
2. That identity must be compatible with whatever key shape the spec-leg settles on for `B-71`'s own
   keyed-addressing question (property 1 already normatively fixes `hitl_responses`' key as a child's
   `run_id` for the already-dispatched case — a not-yet-dispatched branch has no child `run_id` yet, so this
   is genuinely a new question, not a reuse of the existing key).
3. Whatever reason-label convention the new carrier's entries carry needs to be explicitly decided against
   `_collect_gate_owning_run_ids`'s existing `pause_reason is HITL_PENDING` leaf test (see the unexplained
   `EXPLICIT_OPERATOR` datum in §2) — not silently assumed compatible.

This is the same design pass round 5 already scoped for keyed multi-peer addressing — the identity question
("what identifies a not-yet-dispatched gate-owning branch, compatible with whatever key shape `B-71`
settles on") is common to both this carrier gap and the keyed-addressing question already gated on `B-71`.
Recommend co-designing this carrier alongside that question rather than as a separate narrower fix — a
carrier added now with the wrong identity shape would need to change again once `B-71` lands.

`_collect_gate_owning_run_ids` and `compute_hitl_uniform_fallback_eligible_run_id` (`workflow_driver.py`)
also need amendment once the carrier exists — the current implementation only walks `paused_child_branches`;
it would need a matching walk over the new carrier plus a matching `sole-member` uniform-fallback check.

## §5 Scope fence — what this filing does NOT change

No `design-substrate/**` edit. No code edit (the debug instrumentation was reverted). `B-72`'s close-out
items (2) keyed multi-peer addressing (B-71-gated), (3) property 4's resolver set-membership mechanism, and
(4) the round-1 hybrid case remain exactly as round 5 left them — untouched by this pass. This filing adds
a fifth open item: (5) the missing gate-owning-branch carrier for the zero-dispatched-children case, which
item (1) ("delivery-cell construction alone suffices") depended on and is now known to be false without it.

## §6 Operator decision

**Recommended: open the CP spec-leg now, co-designed with `B-71`** — per the B-70/B-33/B-39 same-day-
spec-leg-open precedent, and because both questions need the identical "identity for a not-yet-dispatched
gate-owning branch" answer (§4). **Note the scope difference from those precedents:** B-70/B-33/B-39 each
opened on a single narrow spec delta; this is now a genuine **two-row co-design** (`B-72` item 5 + `B-71`),
since neither can be soundly designed without the other's answer. The operator should weigh that wider scope
before authorizing, not assume it mirrors the earlier single-delta precedents. Alternative: hold both `B-72`
and `B-71` at `design_substrate_gated` pending a future session. A council pass (round 5's own standing
recommendation, likely C10 blast-radius + whichever voice owns liveness/fallback-safety composition) was
already recommended for the property-4-safe resolver design broadly — this carrier gap is naturally in the
same scope, not a separate council question.
