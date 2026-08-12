# E2 adversarial review — B-71 E1 reconciled disposition

*(Genuine `harness-adversarial-reviewer` invocation, Sonnet, 2026-08-12. Findings
verbatim; the full report is in the arc transcript.)*

**Verdict: CLEAR-WITH-REVISION.** Class 1: 1 · Class 2: 2 · Class 3: 0.
Citation fidelity: ~25 cites spot-checked, **every one resolved exactly** — "unusually
high grounding fidelity for an artifact this size."

## F2-01 (Class 2) — Reverse-thread carrier keyed by bare `branch_index` collides across nested fan-out frames

The design models the new carrier on the branch-*shared* pass-through family
(`workflow_driver_types.py:483-545`) but changes its shape to a flat
`Mapping[int, str]` keyed by bare `branch_index`. **That key choice is unsound:
`branch_index` is unique only within one fan-out frame, not tree-wide.** The
codebase's own discipline confirms it — `_ChildPosition` is the PAIR
`(step_id, branch_index)` (`pause_state_projection.py:578-586`), and
`_collect_gate_owning_run_ids` / `_collect_pre_dispatch_gate_owning_identities`
(`workflow_driver.py:2778-2824`) flatten the tree into globally-unique STRINGS
precisely because a bare ordinal is not safe to flatten across nesting levels.
A depth-2 `HIERARCHICAL_DELEGATION` tree with `branch_index=2` at two levels would
silently overwrite or misattribute one branch's token. **Anti-fabrication attack
engaged: A2 (silent scope narrowing)** — the "computed once at the depth-0 root,
threaded down unchanged" framing was copied from the branch-shared precedent
without re-deriving whether the safety argument survives a per-branch carrier.
The design itself flags "one disanalogy to honor" but does not follow it through
to the key-safety consequence. **This is an in-arc ABSORBED item, so shipping it
unrevised ships a real defect, not a documented gap.**

## F2-02 (Class 2) — C7 observability disposition produced by two voices, dropped in reconciliation

`00-CHARTER.md:32-33` promised the deliverable an observability paragraph; the
reconciled document contains **zero** occurrences of "span", "OTel",
"observability", or "trace". Two voices did supply dispositions and neither
survived: C1 (`A1-c1-orchestration.md:48`) proposed
`hitl.escalation.instance_id` on the `hitl.invocation.*` family — which **directly
contradicts the charter's own "the identity is not a span attribute" premise** —
and C10 (`A1-c10-action-safety.md:43`) rated the `webhook.idempotency_key`
cardinality growth benign. Verified independently: the widened
`compose_hitl_action_id` output flows into TWO span attributes neither primary
swept together — `ATTR_WEBHOOK_IDEMPOTENCY_KEY` (`webhook_delivery_composer.py:58,270`)
and `hitl.invocation.audit_ledger_entry_id` (`hitl_gate_composer.py:2238-2242`).
C10's entire "advisory-correlation-only is safe" argument is scoped to *the webhook
channel*; **OTel traces commonly export to third-party vendors — a materially
different trust boundary that was never brought into that analysis.**

## F1-01 (Class 1) — "Linear paths byte-identical" scope unstated

Unclear whether the claim covers the ledger idempotency_key/action_id (true by
construction) or the full webhook JSON wire body (depends on the not-yet-written
adapter update). `project_brief_to_payload` (`webhook_brief_adapter.py:47`) is an
explicit field-by-field mapper, not a blanket `model_dump()`, so the wire reading
is likely also true — but the record should say which claim it makes.

## Findings considered and REJECTED (transparency — 12 enumerated)

All four charter hard constraints verified SATISFIED (constraint 2 checked directly
against `compute_hitl_uniform_fallback_eligible_run_id`'s `never_keyable` exclusion,
`workflow_driver.py:2850-2895`; constraint 4 verified — basis fields set at
branch-spawn, strictly before any dispatch). C10's self-conceded wrong citation
verified honest. Persist-once vs "no stability across runs" — no contradiction.
At-least-once vs ghost-requests — not a contradiction. **The F2 audit-loss fix IS
genuinely the same widening (traced all consumers back to the one shared function)
— legitimately absorbable, not smuggled scope-creep.** Registered item 5
(entry_version) deferral judged defensible and non-unsafe.
