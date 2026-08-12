# B-71 design record — branch-distinct EXTERNAL correlation identity for HITL escalations

**Version:** v1 (2026-08-12) · **Status:** DESIGN RECORD — spec leg NOT yet authorizable
(five hard preconditions below) · **Arc:** council (CP layer) per
`.harness/council/council-workflow.harness-aware.yaml` v1

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

## 4. THE OPEN FORK — the identity basis (do not draft spec text against a guess)

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

1. **Execute the nested-fan-out collision witness** against the chosen basis. Cheap —
   the witness file exists and the shape is already covered for the internal identity.
2. **Resolve the basis fork** (A) vs (B) on that evidence, not on argument.
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
   different token. Registering the wider defect does not close this window. May
   dissolve for free under basis (A) or (B).
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
