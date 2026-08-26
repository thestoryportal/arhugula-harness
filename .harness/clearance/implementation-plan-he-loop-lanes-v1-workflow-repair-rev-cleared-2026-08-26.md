---
artifact: .harness/plan/Implementation_Plan_HE_Loop_Lanes_v1.md
version: v1.0 + rev 2026-08-26 (workflow-repair program §8 — U-HE-46…51 + U-SR-01…09, R0→R3)
cleared_at: 2026-08-26T23:30:00-06:00
clearance_type: execution-correction-H_E-tooling
back_reference:
  - ".harness/clearance/spec-he-loop-lanes-v1.6-cleared-2026-08-26.md (the spec head this rev decomposes; bucket-1 units cite the X6-tagged clauses)"
  - ".harness/spec/Workflow_Repair_Charter_v1.md (bucket-2 authority; U-SR-* units cite charter WR-ids — the family is minted so a U-HE-* id never implies a C-HE-* cite that does not exist)"
  - ".harness/plan/Implementation_Plan_HE_Loop_Lanes_v1.md (§8: sequencing R0→R3 with instruments-before-levers as dependency edges on U-HE-50/U-HE-51; §8.2 item-coverage table over every [A]/[B] recommendation id; §8.5 two open operator decisions surfaced, not decided)"
reviewer_chain:
  - "harness-adversarial-reviewer pass (same round as the spec marker): both P1s were plan-side (coverage-table id collision; U-HE-50 missing its R0 edge) and are absorbed; coverage check confirmed all 23 [B] ids + five [A] repairs + laws:prompt wiring map to exactly one unit or an explicit no-unit disposition"
  - "LEAN protocol on the doc-only PR (no merge-gate; one codex round)"
  - "council NOT convened (proportionality: plan decomposition of two evidence audits' repairs; no committed surface revisited)"
supersedes: ".harness/clearance/implementation-plan-he-loop-lanes-v1-u-he-34-as-built-rev-cleared-2026-08-25.md"
superseded_by: null
---

# Clearance — `Implementation_Plan_HE_Loop_Lanes_v1` (workflow-repair program rev, 2026-08-26)

§8 encodes the U-HE-35 workflow-repair program as fifteen atomic units in four
strictly-motivated rounds: R0 instruments (round derivation, attribution
writers, arc-cost extractor, launch-admission guard) before R1 levers (span
emission from the wrapper; the preflight-suite, laws:prompt, and governance
repairs), then the R2 mechanical sweep, then the R3 eval arc riding the next
code unit with the X6f lens trial — judged against the recorded [B] baseline
(13 rounds, 25.5M IET, 418 calls). Authoring-only: no repair executed in the
landing PR; the two operator forks (advisor() provision-vs-rewrite; U-HE-36
ordering) are surfaced at §8.5 with recommendations, undecided.

**§8.5 ratification (2026-08-26, U-HE-46 arc).** The operator ratified both
decisions via the `/roadmap-continue` invocation opening the U-HE-46 arc:
decision 1 = **REWRITE** (arm (a) — conform the four advisor() carriers to the
instrument that exists; U-SR-06 executes this arm), decision 2 = **arm (a)**
(R0→R1→R2, with U-HE-36 riding as the R3 eval arc carrying U-HE-51's trial).
Recorded at plan §8.5 in the same PR; the "surfaced, not decided" constraint
above is discharged.
