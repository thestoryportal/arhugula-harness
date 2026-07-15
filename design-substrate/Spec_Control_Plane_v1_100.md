# Spec: Control Plane — v1.100 (delta over v1.99)

*Delta-only file. The v1.99 body + the entire C-CP-01 … C-CP-29 contract body are PRESERVED VERBATIM (delta-only-spec-file convention). This delta corrects v1.97's Change-note registered-forward-work paragraph's framing: gaps (b) [per-child HITL response ROUTING] and (c) [nested pause_reason propagation] are no longer accurately described as "coupled ... travel together as one forward arc" — (c) has independently closed (`B-32`); (b) remains open, tracked at `B-39`.*

## Change-note (v1.99 → v1.100)

**Scope of revision.** Prose-only correction to v1.97's Change-note (v1.96→v1.97) registered-forward-work paragraph (unheaded prose, not a numbered section). No new carrier, no new exception, no runtime-side change, no code change of any kind — this delta exists solely to retire a stale normative claim in a cleared spec's carry-text before it contradicts a landed fix.

**The stale claim.** v1.97's Change-note (v1.96→v1.97) registered-forward-work paragraph (PRESERVED VERBATIM at v1.98/v1.99) states: *"(b) two CONCURRENT paused-child branches awaiting operator HITL resume share the single run-level `ctx.resume_context_holder` ... (c) the parent's `_pause_reason` derivation examines only `effect_fence_paused_dispositions`, not a nested child's OWN pause reason ... (b) and (c) are coupled — propagating a nested reason without per-branch response routing is a false affordance — and travel together as one forward arc."*

This delta corrects that framing. Gap (c) has been closed **independently of (b)**, per the `B-32` standalone arc (registered at `.harness/forward-register.yaml`; grounded to convergence via two rounds of out-of-family Codex review — the first caught 3 real routing-mechanism defects, fully reverted and split to `B-39`; the second re-raised the exact "false affordance" concern that paragraph itself anticipated, against the corrected label alone).

**Why (c) alone is NOT a false affordance.** The v1.97 Change-note's coupling claim assumed `pause_reason` would drive an operator/caller surface to auto-supply a single run-level resume without first inspecting which children paused and why. Grounded by direct code read before closing (c): `pause_reason` is read in exactly one non-telemetry site in `harness_cp` — the `_pause_reason` derivation itself (`workflow_driver.py`, both `PARALLELIZATION` and `ORCHESTRATOR_WORKERS`/`HIERARCHICAL_DELEGATION` closures) — and the composer's actual resume path (`ResumeContextHolder.consume_and_clear`) never branches on `pause_reason` at all; it unconditionally consumes the single shared resume context regardless of label. No consumer auto-dispatches a response off this label today. `HITL_PENDING` is therefore an honest, informational signal ("a HITL response is owed somewhere in this round"), not a promise that a single supplied response safely and correctly routes to the right child — that promise is exactly what (b)/`B-39` would need to provide, and remains unbuilt.

**Revised framing — (b) and (c) are SEQUENTIAL, not coupled.** (c) is the weaker, honest half: it corrects a mislabeling (`EXPLICIT_OPERATOR` when a nested reason is genuinely `HITL_PENDING`) without over-promising safe multi-child routing. (b) is the stronger, harder half: safely delivering a distinct operator response to each of ≥2 concurrently-paused children sharing one run-level holder. (c) does not need (b) to be honest; (b) still needs its own design (branch-unique keying, true one-shot-per-key consumption, and a threading mechanism into a recursive child's own re-entry — `execute_workflow`/`child_workflow_runner` currently accept no `resume_context` parameter at all). Both concrete constraints are recorded at `B-39` (`.harness/forward-register.yaml` + `.harness/post-phase-8-forward-register.md`) from the reverted first attempt at (b).

**v1.99 + prior body PRESERVED VERBATIM.** All v1.99 content — the entire C-CP-01 … C-CP-29 body incl. §20.x/§25.x/§26.x — is PRESERVED VERBATIM per the delta-only-spec-file convention; the **only** change is this change-note's correction of v1.97's Change-note registered-forward-work paragraph's framing (a change-note-level correction, not an amendment to any numbered contract section).

---

## §1 — Status

No amended contract section. This delta retires v1.97's Change-note (v1.96→v1.97) registered-forward-work paragraph's "(b) and (c) are coupled ... travel together" framing (change-note prose, not a numbered `C-CP-NN` contract clause) and replaces it with the sequential framing above. `WorkflowPauseReason.HITL_PENDING`'s existing semantic (§26, PRESERVED VERBATIM since its introduction) already covers a nested-gate pause without extension — no new enum value, no new carrier, no new exception type.

**No operator gate.** This is a stale-carry-text correction (per workspace `CLAUDE.md` §10.5 failure-mode catalogue) surfaced by a merge-gate spec-conformance reviewer, not a design decision — the underlying safety question (is (c) alone honest) was resolved by direct code grounding, not by operator judgment call. No committed invariant changed; no `snapshot_hash` change; no cross-axis edge change.

Apply pass: this delta co-published with the harness-cp impl closing `B-32`'s pause_reason half (`workflow_driver.py` — the two `_pause_reason` derivation sites, each now carrying an inline comment cross-referencing this delta's grounding + `B-39`) + by-execution tests (`test_workflow_driver_parallelization_pause.py` — contrasting-baseline + positive tests; `test_workflow_driver_fanout_pause.py` — contrasting-baseline assertion added to the existing cancellation-race test + a new positive test — all four mutation-probed: the guard's `is`/`is not` flip and the guard's deletion each correctly fail the corresponding test, then restored) + full workspace `just check` + build record at the forward register + clearance marker, per workspace `CLAUDE.md` §11.4 bundled-absorption.

v1.99 + earlier PRESERVED VERBATIM per delta-only-spec-file convention. IS spec UNCHANGED. Runtime spec UNCHANGED (composer's `consume_and_clear` behavior is unchanged by this delta — its pre-existing never-branches-on-pause_reason behavior is what this delta's grounding relies on, not something it modifies). CXA v2.19 UNCHANGED. ADR-F1/F2/F3/D1–D6 UNCHANGED. ADD v1.3 + PRD v1.1 UNCHANGED.

Clearance marker filed at `.harness/clearance/spec-control-plane-v1-100-cleared-2026-07-15.md`.

2026-07-15.
