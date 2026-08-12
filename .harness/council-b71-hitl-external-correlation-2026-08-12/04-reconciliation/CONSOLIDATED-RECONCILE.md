# Consolidated reconcile (E2b + E3b collapsed) — B-71

*Orchestrator adjudication of the full reviewer docket, 2026-08-12. The charter
declared the reorder option: E2b and E3b collapse into ONE consolidated reconcile
after all reviewer input is gathered. Reviewers: E2 adversarial (in-family),
E3 advisor (in-family, transcript-aware), E3 Codex (out-of-family, cold).*

---

## The decorrelation result — read this first

**Three-way convergence on one defect, and an out-of-family-only catch on another.**

| Finding | Adversarial | advisor | Codex | Orchestrator |
|---|---|---|---|---|
| Reverse-thread carrier key unsound (bare `branch_index`) | **F2-01** | risk #1 (as "untested uniqueness") | **[P1]** | confirmed |
| **Digest BASIS has the same defect** (one layer deeper) | — | — | — | **FOUND** |
| Sole-owner resolvability = liveness failure | — | — | **[P1]** | confirmed |
| entry_version crash window not closed by the registration | — | risk #3 (adjacent) | **[P2]** | confirmed |
| C7 observability dropped in reconciliation | **F2-02** | — | — | confirmed |
| "byte-identical" scope unstated | F1-01 | — | — | accepted |

The workflow's own rule is *"3-way convergence → ship with confidence; divergence →
dig there."* Here the convergence is on a **defect**, not on confidence — and the
divergence (Codex alone finding the liveness bug) is exactly the decorrelation
dividend the out-of-family reviewer is paid for. Five in-family voices, an in-family
adversarial, and an in-family advisor all missed it.

---

## R-1 [P1, CONVERGENT ×3 + orchestrator escalation] — the identity basis, not just its carrier, is not tree-wide unique

**What the reviewers found.** The reverse-thread carrier `Mapping[int, str]` keyed by
bare `branch_index` cannot represent a root branch 0 and a nested branch 0
simultaneously (adversarial F2-01; Codex P1). Codex named an EXISTING witness that
covers exactly this shape —
`harness-cp/tests/test_workflow_driver_hitl_uniform_fallback_property4.py::test_pre_dispatch_gate_owning_branches_at_different_tree_positions_never_collide`
— **verified to exist**. That is the executed collision test advisor demanded; the
B-72 arc already built it.

**What the orchestrator found, and it is worse.** The reviewers attacked the
*carrier*. The **digest basis itself carries the same defect**.
`compose_branch_child_context` (`workflow_driver_types.py:586-650`) states in its own
docstring: *"All other fields are inherited from `parent_context` (`workflow_id`,
`parent_sandbox_tier`, `parent_actor`, `parent_entry_hash`, **`parent_idempotency_key`**,
`tenant_id`, **`step_index`**); the branch-scoped idempotency key is composed
downstream (U-CP-83)."* So a nested fan-out's branches inherit the **same**
`parent_idempotency_key` and the **same** `step_index` as the outer frame — and the
branch-scoped key is composed *later*, for ledger writes, not into the context field
the design reads. Therefore:

> root branch 0 and nested branch 0, at the same placement, produce the **same
> `(parent_idempotency_key, branch_index, placement.position)` triple** — and so the
> same token, the same widened idempotency key, and the same audit/ledger key.
> **This is B-71's own defect, recreated by the fix.**

C1 rated this claim [HIGH] on an analytic argument (run_id folding). The argument
establishes *run-instance* distinctness, which is real — but says nothing about
*nesting depth*, which is where the collision lives. advisor predicted this exact
failure shape and named its category: *"sound reasoning about a uniqueness property is
precisely the failure category this register row exists to distrust."*

**Disposition — the claim is DEMOTED from [HIGH] to OPEN; the basis is a fork, not a
settled element.** Two candidate bases, each with a stated empirical question the
witness must answer:

- **(A) `(parent_action_id, branch_index, placement)`** — the codebase's own
  branch-causality convention. `compose_branch_child_context`'s docstring argues
  `(parent_action_id, branch_index)` "uniquely identifies a branch **even under
  NESTED fan-out**" resting on action_id global uniqueness per IS §5. **Open
  question:** `parent_action_id` is re-set per step at `workflow_driver.py:5331`
  (`f"workflow:{workflow_id}:step:{step_index}"`) and `:10932`, but at `:8187` it is
  `_parallelization_fanout_action_id(workflow_id)` — which, on its signature, does
  **not** appear to include `step_index`. If so, two parallelization fan-outs in one
  workflow share it and (A) fails too.
- **(B) the tree-wide internal identity** already composed for exactly this purpose
  (`{snapshot_run_id}:pre-dispatch-gate:{branch_index}`, `pause_state_projection.py:521`),
  hashed one-way. C10's original proposal, adjudicated away at S1 for omitting
  `placement` and for `snapshot_run_id` being out of composer scope — **both
  objections survive and must be answered** (placement can be added; the scope
  objection is the real one).

**PRECONDITION (hard):** the executed nested-fan-out collision witness runs against
the chosen basis **before any spec text is drafted**. It is cheap — the witness file
already exists and the shape is already covered for the internal identity.

## R-2 [P1, Codex-only] — the sole-owner resolvability flag introduces a liveness failure

`compute_hitl_uniform_fallback_eligible_run_id` ends
`if len(unaddressed) == 1: return unaddressed[0]` (`workflow_driver.py:2895-2897`,
**orchestrator-verified**). A **sole** pre-dispatch gate owner therefore IS
answerable through the uniform response. The design statically stamps every
pre-dispatch escalation `held-for-sole-resolution` at mint (C11's field, C10's MUST 5)
and binds the reply affordance to it — so the operator is told *not to reply* to the
one request whose reply would resolve the run, and posture-change redelivery is a
*registered follow-on*, so nothing ever corrects the stamp. **The design would create
a permanent pause while trying to prevent an operator trap.**

**Disposition — ACCEPTED, and it forces a design change, not a wording change.**
`resolvability` cannot be a static mint-time constant derived from branch context
alone. Options for the spec leg, in preference order: (i) derive it from the
tree-wide sole-member computation at mint where that is knowable; (ii) if it is not
knowable at mint, the field must not assert a *negative* actionability claim — it
states the branch is pre-dispatch and directs the operator to the pause view for live
status, which is the surface that *can* compute sole-membership; (iii) promote the
posture-change redelivery registration into the arc. **(ii) is the orchestrator's
recommendation** — it keeps the mint honest, keeps the arc's scope, and is consistent
with C1's own "the aggregate/live view belongs on the projection" answer to seam Q2.
C11's `resolvability_note` wording must be re-drafted against whichever is chosen.

## R-3 [P2, Codex] — the entry_version crash window is NOT closed by registering the wider defect

Crash after the webhook delivers token X but before the driver persists it, then
resume after an `entry_version` bump: no persisted value wins, the crash-fallback
recomputes from a changed `parent_idempotency_key` (`workflow_driver.py:3312-3316`),
and emits Y — producing exactly the ghost request and pause-view mismatch persist-once
exists to prevent. **Disposition — ACCEPTED; the design's own scoping argument
("confined to the recompute fallback, made inert by persist-once") is circular here,
because this IS the recompute-fallback path.** The registered follow-on (item 5)
addresses the wider defect but leaves this B-71-specific window open. Resolve in the
spec leg by either excluding `entry_version` from the seed (which candidate basis (A)
or (B) may do for free) or landing an enforced guard with this mechanism. Note this
finding partly *dissolves* if the basis fork resolves to (A) or (B), since neither
folds `entry_version` — a further reason R-1 is the arc's pivot.

## R-4 [Class 2, adversarial] — C7 observability was produced and then dropped

Two voices supplied dispositions (C1 proposing `hitl.escalation.instance_id`, which
**contradicts the charter's own "not a span attribute" premise**; C10 rating the
`webhook.idempotency_key` cardinality growth benign) and neither survived
reconciliation — zero occurrences of span/OTel/trace in the reconciled document. Two
real attributes carry the widened identity (`webhook_delivery_composer.py:58,270`;
`hitl_gate_composer.py:2238-2242`), and **OTel export is a different trust boundary
than the webhook channel** — C10's leak-bar analysis was never extended to it.
**Disposition — ACCEPTED; my synthesis error, not the voices'.** The deliverable
carries an explicit observability disposition resolving the charter contradiction and
extending the leak bar to the tracing-export channel.

## R-5 [Class 1, adversarial] — "byte-identical" scope

**ACCEPTED.** The deliverable states which claim is made: the ledger/audit key
composition is byte-identical on the linear path by construction (`None` discriminator,
the `branch_path` precedent); the webhook wire body is byte-identical because
`project_brief_to_payload` (`webhook_brief_adapter.py:47`) is an explicit field-by-field
mapper, so an unset Optional adds no key — **stated, not inferred**.

---

## What survives unchanged (reviewers actively cleared these)

The adversarial verified all four charter hard constraints SATISFIED and enumerated
12 rejected findings, including two the arc most needed cleared: **the F2 audit-loss
fix IS genuinely the same widening** (all consumers traced to one shared function —
absorbable, not smuggled scope), and **~25 citations resolved exactly**. advisor
confirmed the arc is a coherent single arc rather than the prior multi-layer thrash,
that the absorb/register split shows real X-AL-3 discipline, and that the sequencing
condition is real and self-defusing. None of the five voices' core reasoning is
overturned: the opaque-token construction, mint authority, ingress-rejection rule,
one-family widening, no-ingress-keys-on-the-webhook, and the operator-surface shape
all stand.

---

## Reconcile verdict

**NOT CLEAR-TO-SPEC-LEG. The design record ships as v1 with the basis fork OPEN.**

This is the correct and honest outcome, and it is the arc succeeding rather than
failing: B-71 has three falsified premises on record, every one of them a uniqueness
or accessibility claim that entered a fix without being run to ground. This
deliberation caught the fourth one **before it reached spec text** — which is exactly
what the register row's standing instruction ("ground the design BEFORE drafting spec
text") demanded.

**Preconditions on the spec leg, all hard:**
1. Execute the nested-fan-out collision witness against the chosen basis (R-1).
2. Resolve the basis fork (A) vs (B) on that evidence.
3. Re-derive `resolvability` so it cannot assert a false negative (R-2).
4. Close or explicitly scope the entry_version crash window (R-3).
5. Carry the observability disposition (R-4) and the byte-identical scoping (R-5).
6. The pre-existing conditions from E1 §3 stand unchanged (sequencing; entry_version
   stays registered; the `branch_context` leak bar).
