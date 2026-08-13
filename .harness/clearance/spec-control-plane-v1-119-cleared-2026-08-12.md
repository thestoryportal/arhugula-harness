---
artifact: design-substrate/Spec_Control_Plane_v1_119.md
version: v1.119
cleared_at: 2026-08-12T19:30:00-07:00
clearance_type: spec-writer-apply-pass
back_reference:
  - ".harness/council-b71-hitl-external-correlation-2026-08-12/DELIVERABLE.md v6 (the design record; all five hard preconditions closed on executed, mutation-probed witnesses)"
  - ".harness/forward-register.yaml B-71 row (registered at the B-39 spec-leg PR #1092; council CONVENED + CLOSED 2026-08-12)"
  - ".harness/clearance/spec-control-plane-v1-118-cleared-2026-08-11.md (predecessor)"
merge_commit: pending (this leg's PR merge; recorded at the PR)
reviewer_chain:
  - out-of-family `just codex-review` at this leg's PR (to convergence)
supersedes: spec-control-plane-v1-118-cleared-2026-08-11.md
---

# Clearance — Spec_Control_Plane v1.119 (B-71 spec leg: branch-distinct EXTERNAL correlation identity)

**What v1.119 changes.** `HITLEscalationBrief` (C-CP-28 §25.2, as canonically
supplemented at v1.18 §25.2.X) gains one optional field —
`escalation_instance_id: str | None = None` — plus three additive advisory keys on the
webhook `payload_body` (`branch_context`, `resolvability`, `resolvability_note`). The
token is opaque, deterministic, one-way, ≥128 bits, and equality is its sole promised
operation. The widening lands **once**, inside `compose_hitl_action_id`, so the webhook
`Idempotency-Key`, the CP audit `action_id` and the F2 ledger key stay one identity
family — which also closes the per-peer HITL audit-entry loss under the IS writer's
key-only dedup (C-IS-07 §7.5) as an absorbed half.

**Why the design was authorizable.** The design record's five hard preconditions are all
closed on **executed** evidence, not argument — the discipline that row demanded after
three prior attempts failed on unrun premises:

1. the nested-fan-out collision witness was executed (13 tests, 4 mutation probes);
2. the identity basis fork resolved to (B) on that evidence — candidate (A) FALSIFIED,
   since `_parallelization_fanout_action_id` carries no run identity;
3. `resolvability` re-derived to carry the **channel**, never the outcome, on a witnessed
   eligibility flip (6 tests);
4. the `entry_version` window scoped two-mode, with run-identity continuity witnessed at
   both the top-level (C-RT-35) and child-runner paths;
5. the observability disposition carried — the token rides the tracing export via
   `webhook.idempotency_key`, witnessed producer→exporter (8 tests), which is why the
   hashing requirement at §0.5 is load-bearing for tracing and not only the webhook.

**Not a design extension (X-AL-3).** No new contract number, no new fail class, no enum
extension, no new namespace or attribute, and no change to any existing field's type. The
`resolvability` vocabulary is the **existing closed** `PauseLocationVariant`, deliberately
reused so the webhook and the pause view cannot become two authorities over one concept.
The linear/validator population is byte-identical when the field is absent.

**Two things this clearance explicitly does NOT ratify**, recorded so a later reader does
not infer them:

- **The palette-suppression binding is WITHDRAWN** (§0.6.1). An earlier reading bound
  palette display to `resolvability`; a time-invariant channel cannot disarm a
  time-varying harm, and suppressing would hide a valid uniform action in the sole-owner
  state. The palette is preserved verbatim and the disarm is informational. The residual
  is explicitly left open.
- **The typed resume-outcome diagnostics carrier does not exist.** §0.10 discharges the
  council's sequencing condition by taking its *soften-the-wording* option: §0.7's
  diagnostic requirement binds the consumer of this spec, and is not a claim that a
  `ResumeKeyDisposition` type has shipped.

**One cross-axis note, stated not resolved.** The OD-canonical `hitl.webhook.deliver`
span is declared head=1.0 always-sampled at C-OD-32.3 while the implementation's
always-sampled member set omits it — a registered OD conformance defect. §0.5's leak bar
is written to hold under either resolution, so this delta does not depend on it.

**Residuals owed at the impl leg** (from the design record §5; none is a gate on this
spec text): the Runtime liveness round-trip; the driver keyed-only re-pause round-trip;
the mixed keyed-peer fan-out path; the dispatch-level round-trip for both escalation
venues; the span-processor end-to-end run; the OD redaction question; the
HIERARCHICAL_DELEGATION / DECENTRALIZED_HANDOFF shapes; and the in-window durability arc.

**Posture.** Design-phase (`design-substrate/**` + this `.harness/` clearance companion),
per workspace `CLAUDE.md` §11.2 auto-detection. The spec text applies a design that was
already decided and adversarially reviewed; it does not decide.
