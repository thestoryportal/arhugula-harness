# Implementation Plan: Harness Runtime — v2.63 (delta over v2.62)

*v2.63 absorbs the Runtime half of the `B-71` spec leg (Runtime spec v1.121, CP spec
v1.119) by adding **ONE new unit, U-RT-155**, carrying the §14.8.8.1 step-1 minter and the
step-2 `compose_hitl_action_id` fold. NO landed unit's body is amended — new obligations
ride a new unit and landed criteria stand as HISTORY. Every existing unit body, signature
block, cluster assignment and all other plan content are PRESERVED VERBATIM. No contract
number, fail class, configuration field, `HarnessContext` field, CXA row or cross-axis
edge is minted.*

**Status:** Proposed

## §0 Change-note (v2.62 → v2.63)

### §0.1 Why the Runtime half is a unit at all

`B-71`'s defect is CP-observable (two peer fan-out branches produce byte-identical
operator-facing escalations, and the shared composed key drops the second peer's HITL
audit entry under C-IS-07 §7.5 dedup), but **both sites that must change are
Runtime-owned**: the escalation brief is constructed at §14.8.8.1 step 1, and the
idempotency key is composed at step 2. An earlier draft of the CP leg carried no Runtime
delta at all, which out-of-family review identified as a zero-change claim by omission —
the CP carriers would have shipped with nothing writing to them.

### §0.2 U-RT-155 (NEW) — `B-71` escalation-token minter and idempotency-key fold

| | |
|---|---|
| **Unit** | U-RT-155 |
| **Cluster** | the §14.8.8 durable-async HITL composer cluster (the §14.8.8.1 owner) |
| **Spec authority** | `Spec_Harness_Runtime_v1.md` v1.121 change-note sites 1 and 2; token contract at `Spec_Control_Plane_v1_119.md` §0.2 / §0.4 / §0.4.3 / §0.5 / §0.12 |
| **Depends on** | **U-CP-102** for the four carriers (bidirectional co-requisite — see §0.4) |
| **Level** | terminal within its cluster; introduces no new DAG node upstream of any landed unit |

**Acceptance criteria.**

1. **Step 1 mints per the three-arm read order** (CP spec §0.4.3): the persisted echo on
   `StepExecutionContext.pre_dispatch_escalation_instance_id` wins verbatim when non-`None`;
   otherwise `pre_dispatch_escalation_basis` is hashed per CP §0.4(2); otherwise the brief's
   field stays `None`. Witnessed as three arms, with the echo arm asserting the compute path
   is **not entered** rather than only that the output matches.
2. **No echo-vs-recompute comparison** (CP §0.4.3 arm 1): a resume whose recompute would
   differ from the persisted echo does NOT fail the run. Witnessed directly, because the
   natural defensive implementation is exactly the one the contract forbids.
3. **The fold is at the single existing site** (spec v1.121 site 2): the token is folded
   inside `compose_hitl_action_id`, not composed into a second key beside it. Witnessed by
   asserting the webhook `Idempotency-Key`, the CP audit `action_id` and the F2 ledger key
   are the SAME value for one escalation — the one-identity-family promise of CP §0.2, and
   the property whose violation reintroduces the §0.1 aliasing.
4. **Byte-identity when the token is absent** (spec v1.121 site 2; CP §0.12): with
   `escalation_instance_id` `None`, the composed key equals the pre-arc two-argument key
   exactly. Witnessed against a pre-arc fixture value, not by asserting a shape.
5. **Two peer branches sharing a `child_workflow_id` now produce DISTINCT keys**, and both
   HITL audit entries survive the C-IS-07 §7.5 key-only dedup. This is the defect witness
   and is the criterion by which `B-71` closes; anything weaker witnesses the carriers, not
   the fix.
6. **The pre-hash basis never reaches an exported carrier** (CP §0.5): asserted at this
   seam specifically, because §14.8.8.1 is where the value crosses from internal carriage
   into the webhook payload and the `hitl.webhook.deliver` span. A negative witness covers
   both the webhook body and the exported span attributes.
7. Signature shape is **implementation discretion** and is NOT asserted by any criterion —
   whether the token arrives as a third parameter, a widened context argument, or otherwise
   is settled by execution at this unit, per the §14.8.8.10 CONTRACT-not-mechanism precedent.

**Mutation-probe obligations (Workflow v1.19 PD-9).** Criteria 3, 4 and 5 each carry a
`# mutation-probe:` annotation: compose the token as a second key beside the existing one,
emit the token on the linear path, and blind the fold to the token — each must redden its
own witness and no other.

### §0.3 Sites NOT touched, named so the scope is auditable

The two other live `compose_hitl_action_id` mentions — the §14.8.2 step 4h substep 8b-HITL
cite and the §14.8.8 helper construction-shape note — are PRESERVED VERBATIM as the
historical two-argument shape and are canonically read through the v1.121 delta. They are
narrative/suggestion surfaces, not call sites, so no criterion asserts against them; naming
them here is what makes "two sites, not four" checkable rather than assumed.

### §0.4 The CP co-requisite is bidirectional

U-CP-102 declares the carriers; U-RT-155 writes and folds. Neither is independently
observable — carriers with no minter stay `None` forever, and a minter with no carriers has
nothing to write — so they land in one arc. Recorded here as well as in CP plan v2.53 §0.4
so the fact survives whichever plan a future session reads first.

### §0.5 What this delta is NOT

NOT the impl leg — the code lands at U-RT-155 / U-CP-102. NOT a contract, fail-class,
config-field, `HarnessContext`-field, CXA-row or cross-axis-edge mint. NOT an amendment to
any landed unit body. NOT a prescription of the `compose_hitl_action_id` signature. NOT any
of the follow-ons registered at CP spec §0.9.
