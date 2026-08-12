# B-71 design record — branch-distinct EXTERNAL correlation identity for HITL escalations

**Version:** v2 (2026-08-12) · **Status:** DESIGN RECORD — spec leg STILL NOT
authorizable; preconditions **1 + 2 CLOSED on executed evidence**, **4 BOUNDED**,
**3 + 5 OPEN** · **Arc:** council (CP layer) per
`.harness/council/council-workflow.harness-aware.yaml` v1

## Change-note (v1 → v2)

Discharges §5 **precondition 1** (execute the nested-fan-out collision witness) and
**precondition 2** (resolve the basis fork on that evidence, not on argument), and
bounds **precondition 4**. The witness is
`harness-runtime/tests/test_b71_escalation_identity_basis_collision_witness.py`
(8 tests, green; mutation-probed — neutering
`pre_dispatch_gate_owning_branch_identity` turns 3 of them RED). It composes every
candidate basis from the **real production composers** and runs them over the
realizable collision tree. §4 is rewritten from OPEN FORK to RESOLVED; §5's
precondition list is re-stated with per-precondition status. **No spec text, no plan
delta, no production-code change** — v2, like v1, is documentary plus its witness.

Two v1 claims are corrected by the evidence, both in the direction of *less*
confidence in the v1 escalation, not more:

1. v1 §4 withdrew the council's `(parent_idempotency_key, branch_index, placement)`
   pick on the ground that `compose_branch_child_context` inherits
   `parent_idempotency_key` verbatim. Verbatim inheritance is real
   (`workflow_driver_types.py:632-645`) but **does not produce the claimed
   collision**: it is inheritance *within one run*, where `branch_index` still
   separates the peers, and nested fan-out is **cross-run** (every
   `compose_branch_child_context` call site descends from a single per-run fan-out
   point; nesting is reached by dispatching a child run through
   `child_workflow_runner`). `parent_idempotency_key` descends from
   `_compute_run_idempotency_key(run_id, workflow_id, entry_version)`
   (`workflow_driver.py:646-665`), so it is run-distinguishing. That triple survives
   the collision witness.
2. The **collision is real, but it lands on candidate (A)**, not on the council's
   pick — and on a shape neither the council nor any of the three reviewers named.

## Change-note (— → v1)

First versioned design record for register row `B-71`, discharging the row's standing
instruction: *"next attempt must ground the branch-distinct-identity design BEFORE
drafting spec text."* Produced by a five-voice council (primaries C1 orchestration +
C10 action-safety; consultants C9 reliability, C5 validation-contract, C11
operator-loop), a ten-seam cross-read reconciled to internal zero, and three
decorrelated reviewers (in-family adversarial, in-family transcript-aware advisor,
out-of-family Codex). **No spec text, no plan delta, no code.** The one substantive
change this arc makes to the workspace is documentary: it records a settled design
skeleton, an OPEN fork at the identity basis, two live defects at HEAD, and six
registered follow-ons.

---

## 1. The problem, restated at HEAD

Two peer fan-out branches sharing a `child_workflow_id` produce **byte-identical**
operator-facing HITL escalation requests. `HITLEscalationBrief`
(`validator_framework_types.py:134-151`) declares no run- or branch-distinct member,
and the delivery key is `compose_hitl_action_id(parent_action_id, placement)`
(`hitl_gate_composer.py:428-440`, used at `:1302`) — workflow-scoped. The escalation
fires **before** any child run exists, so no dispatched-child `run_id` can serve as
the discriminator (this is what falsified the row's three prior attempts).

## 2. Two live defects this arc surfaced at HEAD (independent of the fix)

**D-1 — per-peer HITL audit-entry loss.** The same composed `hitl_action_id` is the
F2 state-ledger `idempotency_key` **and** `action_id`
(`hitl_gate_composer.py:1566-1570`, orchestrator-verified). Under the IS writer's
key-only dedup (C-IS-07 §7.5) the second peer's HITL audit entry is dropped as an
idempotent no-op. **The workspace already fixed this exact aliasing class for the
sibling step-ledger write** via `branch_path` (U-CP-83 / C-CP-25 §25.16), documented
at `workflow_driver.py:674-684`: *"N parallel branches at the same declared
`step_index` do not collapse to one ledger entry under the IS writer's
`idempotency_key`-only dedup."* The HITL write is the un-fixed sibling — which both
confirms the defect and supplies the fix its precedent shape (branch discriminator
folded in; `None` on the linear path; byte-identical when absent).

**D-2 — the palette advertises actionability the resolver discards.**
`proposed_response_palette` is projected outward (`webhook_brief_adapter.py:81-83`)
on pre-dispatch requests whose responses are silently dropped
(`pause_state_projection.py:338-341`). An action affordance shipped across a trust
boundary that the ingress will not honor. Live today, independent of B-71.

## 3. The settled design (survived all three reviewers)

- **One opaque token**, `escalation_instance_id: str | None = None` — the sole new
  field on `HITLEscalationBrief`. `branch_index` on **neither** carrier. Optional-with-
  `None`-default is the honest discriminated shape of the two real populations
  (fan-out escalations vs linear/validator ones); a model split would re-commit
  falsified premise 2 one level up, because the operator-authored validator
  population cannot choose a variant.
- **Opaque, deterministic, one-way, ≥128 bits**, never truncated in the key or any
  equality-bearing field. Equality is the sole promised operation.
- **Mint authority:** one *authoritative minter* (the runtime composer at
  `_escalate_to_secondary_channel`, `hitl_gate_composer.py:1259-1268`, reached by
  widening the private helper to take `step_context` — both callers already hold it
  at `:2039`/`:2172`) and one *authoritative read* (persisted value wins over
  recompute). `ValidatorResult.escalation_brief` (`validator_framework_types.py:170`)
  is a second constructor of the TYPE but never a minter of the FIELD — non-`None`
  from it is ignored-and-diagnosed at the trust seam.
- **Pre-dispatch availability by construction** — the basis fields are *inputs* to
  `compose_child_run_id_seed`, not outputs of dispatch, so `PURE_PATTERN_NO_ENGINE`
  (where the child uuid is minted only at dispatch) is covered. Charter constraint 4
  satisfied.
- **Persist-once:** the snapshot echo is authoritative once written; deterministic
  recompute is the crash-fallback for the mint→persist window only (the webhook fires
  at `:1328` before the signal at `:1336`, so the external world can legitimately lead
  the snapshot). Independently required by the carried-forward population
  (`workflow_driver.py:10276-10281`), which has **no live mint at all**.
- **Stability:** the unresolved gate's lifetime **within one run, across re-fires AND
  resume cycles**. Non-commitments: across runs, after resolve/abort, across any
  activated `new_run_id` resumption (dead at HEAD).
- **Widening lands once**, inside `compose_hitl_action_id`, so the webhook
  `Idempotency-Key`, the CP audit `action_id`, and the F2 ledger key stay **one
  identity family** — preserving the caller-side audit join and closing D-1.
  Verified absorbable: all consumers trace to the one shared function.
- **Delivery:** at-least-once per re-fire, dedupable by stable key. **No harness-side
  suppression store** — the retention window is the consumer's; harness-side
  suppression would convert unresolved-gate visibility from at-least-once to
  at-most-once, the liveness failure for an escalation channel.
- **Ingress:** advisory-correlation-only as a **structural** one-way rule (the
  C-CP-21 §21.3 palette-restriction precedent — restriction in the contract, not
  operator discipline). No ingress surface accepts the token; a match is
  counted-as-unaddressed **and diagnosed** via a typed disposition landing on the
  resume outcome (primary) and the pause view (secondary). A log line alone is
  insufficient.
- **The webhook carries no ingress keys.** No real `run_id` transits it; addressing
  capability lives on the operator-held pause view. Fan-out-only population first;
  presence/absence is the discriminator.
- **Operator surface:** token + display-only prose `branch_context` (the ordinal in
  prose, under an explicit no-format commitment, **contractually barred** from
  carrying `snapshot_run_id`, the internal identity, run_id-shaped strings, or raw
  basis material) + a structured `resolvability` + `resolvability_note`; all
  `payload_body`-only (additive keys on the contractually-opaque Mapping, C-CP-21
  §21.8). Palette display bound to the posture — the disarm for D-2.
- **Public projection:** `PreDispatchUniformFallbackOnlyLocation` gains the EXTERNAL
  token, with v1.112 §2.2 constraint 2 restated alongside — internal identity still
  never. Without this the correlation loop terminates in a struct no operator reads.
- **2+-concurrent shape:** N distinct, stably-identified requests, collectively
  parked. Aggregate rejected on four control-flow grounds (no honest mint site; the
  escalations are not simultaneous; an aggregate has no stable key as membership
  changes, defeating the dedup the design depends on; the posture is satisfiable
  statically). The aggregate VIEW belongs on the projection.
- **Byte-identical, scoped:** the ledger/audit key composition is byte-identical on
  the linear path by construction (`None` discriminator, per the `branch_path`
  precedent); the webhook wire body is byte-identical because
  `project_brief_to_payload` (`webhook_brief_adapter.py:47`) is an explicit
  field-by-field mapper, so an unset Optional adds no key.

## 4-bis. THE FORK, RESOLVED (v2) — basis (B), on executed evidence

§4 below is preserved verbatim as it stood at v1. This section supersedes its
verdict; read §4 for the fork as posed, and this section for how it closed.

### 4-bis.1 The collision tree the witness actually runs

A root PARALLELIZATION run of `wf-root` fans out two peer branches; **both** are
`SUB_AGENT_DISPATCH` steps pointing at the **same** `child_workflow_id`. This is not
a contrived shape — it is the shape `compose_child_run_id_seed`'s own docstring names
as live (`sub_agent_dispatch.py:371-380`: *"two sibling SUB_AGENT_DISPATCH workers
that dispatch the SAME `child_workflow_id` would derive the SAME child run_id →
ALIASED durable output + fence state → cross-branch corruption EVEN WITHOUT A
CRASH"*), and it is the reason `branch_path` was folded into the child-run seed at
U-CP-83. Each child run is itself a PARALLELIZATION run whose own branch 0 fires a
pre-dispatch escalation. The two child runs are genuinely distinct (the witness pins
this first, so the collision assertions are not vacuous).

### 4-bis.2 The evidence

| Basis | Tree-wide distinct? | Stable across an `entry_version` bump, snapshot recovered | Stable with no snapshot (crash before persist) |
|---|---|---|---|
| **(A)** `(parent_action_id, branch_index, placement)` | **NO — COLLIDES** | yes | yes |
| **(C)** `(parent_idempotency_key, branch_index, placement)` — the council's pick | yes | **NO — ROTATES** | no |
| **(B)** run-scoped internal identity + `placement` | **yes** | **yes** | no |

**(A) is falsified.** A PARALLELIZATION branch's `parent_action_id` is
`_parallelization_fanout_action_id(workflow_id)` (`workflow_driver.py:8187` →
`:7168-7177`), which takes `workflow_id` **and nothing else** — it carries no run
identity at all. Two sibling child runs of the same `child_workflow_id` therefore
compose the identical triple, and the collision propagates through the real
`compose_hitl_action_id` (`hitl_gate_composer.py:428-440`, used at `:1302`) into the
webhook `Idempotency-Key`, the CP audit `action_id`, and the F2 ledger key at once.
This recreates B-71's own defect inside the fix — the failure v1 §4 predicted, on a
different shape than the one it predicted it on. The orchestrator-workers sibling has
the same run-blindness (`orchestrator_action_id = f"workflow:{workflow_id}:step:0"`,
`workflow_driver.py:12137`), so the defect is not PARALLELIZATION-local.

**(C) is falsified on precondition 4, not on uniqueness.** `entry_version` is folded
into `run_idempotency_key` (`workflow_driver.py:3312-3316`), so a resume after an
`entry_version` bump recomputes a different token — on the **ordinary** resume path,
where the paused child's original `run_id` is reused verbatim
(`child_workflow_runner.py:230-234`). That is not the narrow mint→persist crash
window §5 precondition 4 scopes; it is *every resumed escalation*. Choosing (C) would
make the unguarded-`entry_version` defect (registered separately as a follow-on)
load-bearing for the correlation token rather than adjacent to it — the design's
"stability across resume cycles" commitment (§3) would be false as written.

**(B) survives both.** Its run component is the child's `run_id`, which a resume
reuses from the snapshot rather than re-deriving, so the token does not rotate on an
`entry_version` bump. Its only residual is the crash-BEFORE-persist window — which is
*precisely* the window the persist-once rule at §3 already declares and scopes ("the
snapshot echo is authoritative once written; deterministic recompute is the
crash-fallback for the mint→persist window only"). The witness pins that boundary in
both directions.

### 4-bis.3 The two objections that defeated (B) at the cross-read

- **"It omitted `placement`."** Fixed, and the fix is what the witness tests — every
  basis in the table carries `placement`.
- **"`snapshot_run_id` is not in composer scope."** The real objection, and it stands
  as stated: `StepExecutionContext` carries no run identity
  (`workflow_driver_types.py` field set — `workflow_id`, `parent_action_id`,
  `parent_idempotency_key`, `step_index`, `branch_index`, `tenant_id`, …; no
  `run_id`). It is **not** a blocker on the basis, because the driver **already
  composes exactly this identity** for exactly this branch population, at
  `workflow_driver.py:8346` and `:12670`, via
  `pre_dispatch_gate_owning_branch_identity(run_id, branch_index)`
  (`pause_state_projection.py:500`) — where `run_id` *is* in scope. Getting it to the
  mint site is one additive `StepExecutionContext` field, the shape the context
  already carries six times (`hitl_uniform_fallback_eligible_run_id`,
  `effect_fence_uniform_fallback_eligible_key`,
  `effect_fence_tree_wide_abort_present`, `sub_agent_descent`, `resume_context`,
  `child_resume_snapshot`) — each `None`-defaulted and byte-identical when absent.
  **The spec leg must carry this thread explicitly; it is not free.**

### 4-bis.4 What carries forward unchanged

The three-way-convergent finding stands and is re-pinned by the witness: **the
reverse-thread carrier must be keyed by a tree-wide identity, never by bare
`branch_index`** — the witness shows a bare-ordinal carrier collapsing the two
branches while (B) separates them, so the separation is attributable to the run
component alone.

**Scope honesty.** The witness covers the PARALLELIZATION fan-out shape. It does not
exercise HIERARCHICAL_DELEGATION recursion or the DECENTRALIZED_HANDOFF stage chain
(`workflow_driver.py:15375-15441`, where `parent_action_id` chains off the previous
stage's `action_id` and `branch_index` is not a fan-out ordinal). (A) is already
falsified, so those shapes cannot rescue it; whether they add a *further* constraint
on (B) is unexamined and is a named residual on the spec leg.

---

## 4. THE OPEN FORK — the identity basis (do not draft spec text against a guess)

*(v1 text, preserved verbatim; superseded by §4-bis above.)*

The council selected `(parent_idempotency_key, branch_index, placement.position)` and
rated tree-wide uniqueness [HIGH]. **That rating is withdrawn.**
`compose_branch_child_context` (`workflow_driver_types.py:586-650`) inherits
`parent_idempotency_key` **and** `step_index` verbatim into branch child contexts
(the branch-scoped key is composed downstream at U-CP-83, for ledger writes, not into
this context field). A nested fan-out's branch 0 and the root fan-out's branch 0, at
the same placement, therefore compose the **same triple** — recreating B-71's own
defect inside the fix. Codex named an existing witness that covers exactly this tree
shape (`harness-cp/tests/test_workflow_driver_hitl_uniform_fallback_property4.py`,
verified to exist); advisor predicted the failure category in advance.

**Candidate (A) — `(parent_action_id, branch_index, placement)`.** The codebase's own
branch-causality convention; `compose_branch_child_context`'s docstring argues
`(parent_action_id, branch_index)` is unique *even under nested fan-out*, resting on
action_id global uniqueness (IS §5). **Open question:** `parent_action_id` is per-step
at `workflow_driver.py:5331`/`:10932` but is `_parallelization_fanout_action_id(workflow_id)`
at `:8187`, which on its signature does not include `step_index` — if so, two
parallelization fan-outs in one workflow share it and (A) fails too.

**Candidate (B) — the tree-wide internal identity**
(`{snapshot_run_id}:pre-dispatch-gate:{branch_index}`, `pause_state_projection.py:521`)
hashed one-way, with `placement` added. C10's original proposal. Both objections that
defeated it at the cross-read survive and must be answered: it omitted `placement`
(fixable) and `snapshot_run_id` is not in composer scope (the real one).

**Whichever is chosen, the reverse-thread carrier must be keyed by a tree-wide
identity — not bare `branch_index`** (three-way convergent finding).

## 5. Hard preconditions on the spec leg

**Status at v2: 1 CLOSED · 2 CLOSED · 3 OPEN · 4 BOUNDED · 5 OPEN.** The spec leg
remains NOT authorizable — 3 and 5 are unaddressed, and 4 is bounded rather than
closed. Preconditions 1 and 2 are struck through as discharged; their v1 text is kept
so the discharge is auditable against what was asked.

1. ~~**Execute the nested-fan-out collision witness** against the chosen basis. Cheap —
   the witness file exists and the shape is already covered for the internal identity.~~
   **CLOSED at v2** — executed at
   `harness-runtime/tests/test_b71_escalation_identity_basis_collision_witness.py`
   (8 green, mutation-probed). Note the correction: the pre-existing file Codex named
   (`harness-cp/tests/test_workflow_driver_hitl_uniform_fallback_property4.py:327`)
   witnesses the *internal* identity's tree-distinctness, which was already settled;
   it does **not** exercise any candidate EXTERNAL basis. The new module is the
   witness this precondition actually asked for.
2. ~~**Resolve the basis fork** (A) vs (B) on that evidence, not on argument.~~
   **CLOSED at v2 — basis (B).** (A) collides; (C), the council's original pick,
   survives uniqueness but rotates under precondition 4 on the ordinary resume path.
   Full evidence + the answer to (B)'s in-scope objection at §4-bis.
3. **Re-derive `resolvability` so it cannot assert a false negative.** A sole
   pre-dispatch owner IS answerable — `if len(unaddressed) == 1: return unaddressed[0]`
   (`workflow_driver.py:2895-2897`). A static `held-for-sole-resolution` stamp would
   tell the operator not to reply to the one request whose reply resolves the run, and
   posture-change redelivery is a registered follow-on that would never correct it.
   **Recommended:** the field states the branch is pre-dispatch and routes the operator
   to the pause view for live status, rather than asserting non-actionability.
   `resolvability_note` re-drafts against whichever shape is chosen.
4. **Close or explicitly scope the entry_version crash window** — crash after delivery
   but before persist, then resume after an `entry_version` bump, recomputes a
   different token. Registering the wider defect does not close this window. ~~May
   dissolve for free under basis (A) or (B).~~
   **BOUNDED at v2, not closed.** It does not dissolve for free. Under the chosen
   basis (B) the window is exactly as originally described — crash after delivery,
   before persist — and no wider: the ordinary resume path reuses the snapshot's
   `run_id`, so the token is stable there (witnessed both ways). The spec leg still
   owes an explicit scope statement; what v2 removes is the *unbounded* reading (which
   is what basis (C) would have had).
5. **Carry the observability disposition** — resolve the charter's "not a span
   attribute" premise against C1's `hitl.escalation.instance_id` proposal, and extend
   C10's leak-bar analysis from the webhook channel to the **tracing-export** channel
   (`webhook.idempotency_key` at `webhook_delivery_composer.py:58,270`;
   `hitl.invocation.audit_ledger_entry_id` at `hitl_gate_composer.py:2238-2242`).

Plus the three conditions carried from the council: **sequencing** (the resume-outcome
diagnostics leg ships with the spec leg or C11's wording softens in the same commit),
**scope** (the `entry_version` guard defect stays registered; folding it in is a fork
to surface), and the **`branch_context` leak bar**.

## 6. Absorbed in-arc vs registered

**Absorbed** (same mechanism; splitting ships the widening half-applied): the D-1
audit-loss fix, mint-authority ignore-and-diagnose, the palette/`resolvability`
binding, the projection amendment, the persist-once reverse-thread field.

**Registered as follow-on `B-*` rows** (each an observable contract change to a
cleared mechanism → its own spec leg per X-AL-3): (1) uniform-response target
selector; (2) redelivery-on-posture-change; (3) uniform-treatment extension to
depth-0 root and already-dispatched children; (4) the addressing half (pause-view-side
capability question — the webhook answer is settled NO); (5) unguarded `entry_version`
across the pause boundary (rotates **every** step idempotency key on resume, not just
this token); (6) typed `ResumeKeyDisposition` + resume-outcome diagnostics carrier —
a **named companion leg, not a deferral**, bound by the sequencing condition.

## 7. Why this arc did not produce a spec leg, and why that is the result

B-71 has failed three times, each on a uniqueness-or-accessibility premise that
entered a fix without being run to ground. This deliberation caught the fourth
**before it reached spec text**: the council reconciled to internal zero on a design
whose load-bearing uniqueness claim the reviewer stage then falsified, with the
in-family voices, the in-family reviewers, and the out-of-family reviewer each
contributing a finding the others missed. Two claims were falsified *inside* the
deliberation before they could enter the record (C10's cited dedup consumer; C1's own
echo-implementability claim), and the orchestrator's own re-grounding falsified a
third (the basis). That is the process working — not a stalled arc.

**v2 addendum.** The same pattern held one round further out: v1's own escalation —
the withdrawal of the [HIGH] uniqueness rating — was itself an argument, not a run
result, and running it to ground moved the defect from the basis v1 accused to a
different one, on a tree shape nobody in the deliberation had named. Two of the four
falsifications in this row's history were of claims *made by the falsifier*. The
operative discipline is not "distrust the council" but "no uniqueness claim enters
this row's record without an executed witness" — which is why preconditions 1 and 2
were written as *execute* and *resolve on that evidence*, and why 3 and 5, which are
argument-work rather than evidence-work, are still open.
