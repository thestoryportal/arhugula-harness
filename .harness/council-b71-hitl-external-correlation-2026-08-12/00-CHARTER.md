# Council charter — B-71 branch-distinct EXTERNAL correlation identity for HITL escalations

*Convened 2026-08-12 by the loop session (autonomous per the standing loop-mode
authorization; hil_gates run without HALT per `[[feedback-autonomous-loop-dont-stop-to-ask]]`,
with the consolidated-reconcile collapse per the workflow's reorder option).
Workflow: `.harness/council/council-workflow.harness-aware.yaml` v1.*

## The question

Design the branch-distinct EXTERNAL correlation identity for operator-facing HITL
escalation requests (`HITLEscalationBrief` + the webhook payload), co-designed with
CP spec v1.108 §1.2 property 6, such that two peer fan-out branches sharing a
`child_workflow_id` no longer produce byte-identical escalation requests.

## Spine tension (named in advance — the nameable-tension gate PASSES)

**C1 orchestration** (peer-branch escalations need distinct operator-facing
correlation — B-39's `hitl_responses` addressing and plain operator comprehension
both fail when two requests are byte-identical) **⊥ C10 action-safety/blast-radius**
(a NEW identity on an operator-facing / webhook-EXTERNAL payload is a new external
contract surface — every field shipped outward is a commitment, a correlation
handle, and a potential replay/spoof/confusion vector).

## Layer + voices

CP layer (HITL escalation contract). Primaries capped at the genuine domain
center: **C1** (orchestration) + **C10** (action-safety/blast-radius). Consultants:
**C9** (reliability/recovery — webhook idempotency-key semantics, resume
addressing), **C5** (validation-contract — the brief is a typed CP contract
surface, C-CP-25→C-CP-28 §25.2 family), **C11** (operator-loop/local-first — the
operator is the webhook consumer; correlation must be humanly usable). C6/C7/C8/C2
not convened: no model-routing/eval question; the identity is not a span attribute
(C7's adjacent interest is noted for the deliverable's observability paragraph).

## Hard constraints (from the register row + v1.108 — violating any is a design error)

1. **Never alter property 1's key shape** (the `hitl_responses` map keys stay
   run_id-shaped).
2. **Never make the pre-dispatch internal identity `hitl_responses`-keyable**
   (v1.108 §1.1(b): `f"{snapshot_run_id}:pre-dispatch-gate:{branch_index}"` is
   INTERNAL-only; pre-dispatch gate-owning branches resolve ONLY via property 4/6
   sole-membership uniform fallback).
3. **Target v1.108's open 2+-concurrent-unaddressed case** (property 6(c): when
   2+ branches are unaddressed, NO delivery cell is built for any — the design
   must say what the operator-facing story is there, not just relabel requests).
4. **Round-7 narrowing resolved FIRST**: the identity must cover NOT-yet-dispatched
   peers — exposing an already-dispatched child's `run_id` cannot (for
   `PURE_PATTERN_NO_ENGINE`, `compose_child_run_id_seed` falls through to None and
   a uuid is minted only at dispatch; the escalation fires BEFORE that).

## Three falsified premises on record (do not re-fall into them)

(i) registration-time "run_id already accessible at the brief site" — FALSE;
(ii) round-1 "a required field add is safe" — FALSE (Optional-vs-required breakage);
(iii) round-5 "run_id disambiguates peers" — FALSE (execute_workflow's run_id is
per-PARENT-RUN; every peer branch of one fan-out shares it).

## Grounding pack (verified at HEAD e033c1ce, 2026-08-12 — cite these, do not re-derive from recall)

- Brief fields (NO run-distinct member): `harness-cp/src/harness_cp/validator_framework_types.py:134-151`
  (`parent_step_id`, `parent_action_id`, `fail_class`, `fail_detail_hash`,
  `escalation_reason`, `proposed_response_palette`; frozen, ConfigDict(frozen=True)).
- Escalation composition site: `harness-runtime/src/harness_runtime/lifecycle/hitl_gate_composer.py:1259-1345`
  (`_escalate_to_secondary_channel` — constructs the brief; NO branch-distinct
  value in scope: parameters are parent_action_id/step/placement/palette/reason/tenant_id).
- Idempotency key: `hitl_gate_composer.py:1302` — `str(compose_hitl_action_id(parent_action_id, placement.position))`,
  i.e. `f"hitl:{parent_action_id}:{placement}"` (`:428-440`) — workflow-scoped;
  byte-identical for peer branches sharing a child_workflow_id.
- Webhook delivery: `deliver_webhook_for_brief(durable_brief, idempotency_key, tenant_id=...)`
  (`:1332-1334`) — the brief projects to WebhookPayload via the brief adapter.
- Property 6 (internal identity, never-keyable): `design-substrate/Spec_Control_Plane_v1_108.md`
  §1.1(b)/§1.2 property 6 + impl at `harness-cp/src/harness_cp/workflow_driver.py`
  (`_collect_gate_owning_run_ids` walks `PreDispatchGateOwningBranchResumeState(branch_index, step_id, step_kind, child_workflow_id)`;
  internal identity `f"{snapshot_run_id}:pre-dispatch-gate:{branch_index}"`; resume
  validation at `workflow_driver.py:~8067-8102`).
- Register rows: `.harness/forward-register.yaml` B-71 (full history incl. the
  5-round reverted fix) + B-72 close_out (property-6 lineage);
  `.harness/class_1_tension_b72_pre_dispatch_gate_owning_branch_identity.md`.

## Deliverable

A reconciled DESIGN RECORD (this tree's DELIVERABLE.md): the chosen identity shape,
its carrier(s) (brief field? webhook-payload-only? idempotency-key composition?),
its threading path (who mints it, where it flows), the 2+-concurrent story, the
external-contract commitments and non-commitments, and the follow-on legs (CP spec
delta + impl leg) — versioned v1 + change-note. The SPEC LEG IS NOT AUTHORED in
this arc (design-record-first per the B-72 precedent: repro/grounding → design →
spec leg → impl leg).

## Stages

E1 (A1 primaries independent → A2 consultants react → B seam cross-read) → E2
adversarial → E3 codex(cold primer)+advisor(transcript) → CONSOLIDATED reconcile
(E2b+E3b collapsed) → E4 bounded adversarial gate → close (doc-only PR).
