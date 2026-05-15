# Finding — P6-CK process gap: verbatim-claim check never run at checkpoint

*Workspace finding record. Authored 2026-05-15, Phase 7 sub-phase 7b. Surfaced during the plan-wide verbatim-claim audit (`.harness/verbatim_audit_cp_plan.md` + `.harness/verbatim_audit_od_plan.md`) and its §4A resolution pass.*

## Fork classification

**§2.7.6 Class 3 (informational).** This record documents a process gap in a *completed* checkpoint procedure; it is non-blocking. The execution halt the gap caused is already handled by the per-cluster **Class 1** forks in the two audit reports — this finding does not re-halt anything. It is filed so the gap is durable and can inform future checkpoint procedure.

## The observation

The per-axis implementation plans were **P6-CK-cleared** (Phase 6 checkpoint) and entered Phase 7 as canonical execution authority per `CLAUDE.md` §1.3 and §2.4. Yet the plan-wide audit found **17 atomic units** whose acceptance criteria assert a signature is materialized "per §X **verbatim**" / "exactly N per §X" against a cited Phase-5 spec contract the signature does **not** transcribe:

- **CP plan — 7 units:** U-CP-01, U-CP-10, U-CP-19, U-CP-22, U-CP-43, U-CP-46, U-CP-47 (+ borderline U-CP-11).
- **OD plan — 10 units:** U-OD-02, U-OD-04, U-OD-09, U-OD-11, U-OD-12, U-OD-14, U-OD-28, U-OD-30, U-OD-32, U-OD-33.

Each is a self-contradicting acceptance criterion: the unit claims a verbatim match and the match does not hold. Several are masked by a coincidental cardinality match ("exactly N" is correct; the N members are not the spec's members — U-OD-11/12/14/32/33).

## The gap

P6-CK cleared the plans without running a **verbatim-claim check** — a mechanical pass that, for every acceptance criterion asserting "per §X verbatim" / "matches §X" / "exactly N per §X", opens the cited spec section and confirms the unit's signature transcribes it (value names, cardinality, member set, and the cited section number all matching).

The checkpoint verified plan *structure* (units present, dependency graph well-formed, citations resolve to real sections — every `Implements:` citation does resolve) but not plan *fidelity to cited content*. A citation that resolves to a real section is not the same as a signature that transcribes that section. The 17 divergences all clear the first check and fail the second.

This gap was not visible until Phase 7 execution because the divergences are internally consistent within each plan unit — the defect only surfaces when the unit body is cross-read against the spec, which is exactly what the verbatim-claim audit did and what P6-CK did not.

## Provenance — how the gap was discovered, not designed-around

The shape was first surfaced as three isolated execution-time forks (Tension 002 / Tension 004 / F3-01) during 7b unit landing. The §6 systemic-pattern threshold (≥3 occurrences) prompted the plan-wide audit rather than continued one-fork-at-a-time discovery. The audit confirmed the shape is systemic — 17 units — and the two audit reports were filed as the canonical systemic-tension records (no per-unit Tension 005+ proliferation). The `systems-architect` §4A pass (2026-05-15) recommended conform-to-spec for both clusters; operator sign-off pending.

Had the audit not been run, each of the 17 would have surfaced as a separate Class 1 halt at its own landing — 17 execution interruptions instead of one batched revision-pass. The cost of the P6-CK gap is measured in execution-time forks that a checkpoint check would have caught in one pass.

## Implication for future checkpoint procedure

A verbatim-claim check belongs in the P6-CK procedure (and, by extension, any checkpoint clearing an artifact that asserts verbatim fidelity to an upstream artifact): for every "verbatim" / "exactly N" / "matches §X" assertion, cross-read the cited upstream section and confirm transcription — not merely that the citation resolves. The check is mechanical and the audit demonstrates it is tractable plan-wide.

This is **not** a back-flow trigger against `Project_Workflow_v1_8.md` itself — it is an observation about how a checkpoint was *executed*, surfaced for the operator's judgment on whether the workflow's checkpoint-procedure description warrants the explicit check being added. That decision is the operator's; this record does not recommend a workflow revision, it documents the gap.

## Disposition

- **No execution halt** from this record (the halts are the per-cluster Class 1 forks).
- **Operator action:** none required for Phase 7 execution to proceed past the cluster resolution. Optional: decide whether `Project_Workflow_v1_8.md` checkpoint-procedure text should explicitly name the verbatim-claim check, and whether that is itself a workflow back-flow item.
- **Cross-reference:** `.harness/verbatim_audit_cp_plan.md`, `.harness/verbatim_audit_od_plan.md` (the systemic-tension records + §4A recommendations); Tension 002 (resolved, commit `45f104f`); Tension 003 + Tension 004 (open, folded into the cluster audits).

*Filed 2026-05-15 under Phase 7 sub-phase 7b. §2.7.6 Class 3 — informational, non-blocking.*
