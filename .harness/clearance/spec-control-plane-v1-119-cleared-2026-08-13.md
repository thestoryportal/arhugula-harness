---
artifact: design-substrate/Spec_Control_Plane_v1_119.md
version: v1.119
cleared_at: 2026-08-13T16:00:00-07:00
clearance_type: spec-writer-apply-pass
back_reference:
  - ".harness/council-b71-hitl-external-correlation-2026-08-12/DELIVERABLE.md v6 (the design record; all five hard preconditions closed on executed, mutation-probed witnesses)"
  - ".harness/forward-register.yaml B-71 row (registered at the B-39 spec-leg PR #1092; council CONVENED + CLOSED 2026-08-12)"
  - ".harness/clearance/spec-control-plane-v1-118-cleared-2026-08-11.md (predecessor)"
  - "PR #1326 (the leg's TRUE shape recorded on main after PR #1325 was deliberately NOT landed as under-scoped)"
co_requisite:
  - ".harness/clearance/spec-harness-runtime-v1-121-cleared-2026-08-13.md (the Runtime minter + fold; neither half is independently observable)"
merge_commit: pending (this leg's PR merge; recorded at the PR)
reviewer_chain:
  - "four out-of-family `just codex-review` rounds at PR #1325 (14 findings absorbed; the leg was then withheld as under-scoped rather than landed)"
  - out-of-family `just codex-review` at this leg's PR (to convergence)
supersedes: spec-control-plane-v1-118-cleared-2026-08-11.md
---

# Clearance — Spec_Control_Plane v1.119 (B-71 spec leg: branch-distinct EXTERNAL correlation identity)

**What v1.119 changes.** `HITLEscalationBrief` (C-CP-28 §25.2, as canonically
supplemented at v1.18 §25.2.X) gains one optional field —
`escalation_instance_id: str | None = None` — plus **four** additive keys on the webhook
`payload_body`: the **BARE** `escalation_instance_id` (required because the composed
`Idempotency-Key` is deliberately non-parseable, so without the bare token the webhook cannot
equality-match the §0.4.4 pause-view projection and the correlation loop stays open), plus
`branch_context`, `resolvability` and `resolvability_note`. The
token is opaque, deterministic, one-way, ≥128 bits, and equality is its sole promised
operation. The widening lands **once**, inside `compose_hitl_action_id`, so the webhook
`Idempotency-Key`, the CP audit `action_id` and the F2 ledger key stay one identity
family — which also closes the per-peer HITL audit-entry loss under the IS writer's
key-only dedup (C-IS-07 §7.5) as an absorbed half.

**What changed between PR #1325 and this clearance — the gaps that made the earlier
draft unlandable.** Two were found by PR #1325's own round 4; five more by out-of-family
review of THIS leg's first push. All seven are closed below.

**Found by review of this leg (round 1), all absorbed:** the minted token had no declared
WRITER, so the §26.9 echo would have stayed `None` forever and every resume would still
have recomputed — the §0.4.3 read-side gap in mirror image; the new resume-state field
would have broken **already-durable** snapshots by changing their recomputed hash on
upgrade (closed by the drop-when-`None` contract, mirroring
`_strip_default_fanout_resume_fields`'s existing treatment of `hitl_gate_config_hash`);
the token-PRESENT composed-key format was unpinned while the digest was pinned, so two
compliant implementations could disagree and a deployment change during an unresolved gate
would emit a different key for one escalation (§0.4(2-bis) pins the output, not the call
shape); the design record's own precondition — `PreDispatchUniformFallbackOnlyLocation`
gains the external token, *"without this the correlation loop terminates in a struct no
operator reads"* — had been deferred with the whole pause-view half (§0.4.4 restores it as
read-only CORRELATION, keeping the deferred ADDRESSING half deferred); and §0.4(3)'s
mint-authority rule named no owning site, so it is now enforced by **overwriting** the
validator-supplied value at the acceptance point rather than merely ignoring it, since
ignoring alone still ships the operator's value on the wire.

**Found by PR #1325's round 4:** PR #1325 carried this text with three carrier amendments and was
deliberately closed rather than merged, because its fourth review round found two defects
that are structural rather than editorial. Both are closed here, and neither was closable
by rewording:

1. **The persist-once contract was unsatisfiable, not merely unimplemented.** §0.4.2 puts
   the authoritative echo on the resume state and declares a normative "use it, do not
   recompute" order — but the reader is the composer at §14.8.8.1 step 1, which holds a
   `StepExecutionContext` that knew only the pre-hash basis. The echo was written to a
   carrier the reader never consults, so **every** resume would have reached the recompute
   arm that §0.4(5) designates as the crash-fallback. §0.4.3 / `§25.21` adds the echo READ
   carrier and states the read order as one three-arm rule over both fields.
   With §0.4.4 the amendment count moves 3 → **5**.
2. **The Runtime spec was a zero-change claim by omission.** §0.11 listed OD / CXA / ADR /
   ADD / PRD as unchanged and simply did not mention Runtime, which reads as zero. It is
   not zero: `Spec_Harness_Runtime_v1.md` §14.8.8.1 step 2 specifies the **two-argument**
   `compose_hitl_action_id`, verified at HEAD. §0.13 names both owed Runtime sites, and the
   co-requisite delta is filed at Runtime spec v1.121.

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
