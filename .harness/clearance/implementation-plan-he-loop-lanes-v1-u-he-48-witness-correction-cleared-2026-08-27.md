---
artifact: .harness/plan/Implementation_Plan_HE_Loop_Lanes_v1.md
version: v1.0 + rev 2026-08-27 (U-HE-48 baseline correction — the acceptance-witness bullet AND the §8.1 R3-baseline narrative, plus the same stamp on Workflow_Repair_Charter_v1.md §3)
cleared_at: 2026-08-27T12:30:00Z
clearance_type: execution-correction-H_E-tooling
back_reference:
  - ".harness/clearance/spec-he-loop-lanes-v1.6-cleared-2026-08-26.md (the spec head this plan executes; C-HE-25 X6e's contract text is UNCHANGED by this rev — the extractor, IET index, and additive-null field rule stand as cleared)"
  - ".harness/plan/Implementation_Plan_HE_Loop_Lanes_v1.md (U-HE-48 acceptance bullet: dated execution-time correction note; §8.1 R3-baseline narrative: same corrected figures stamped in place — one normative baseline)"
  - ".harness/spec/Workflow_Repair_Charter_v1.md (§3 baseline paragraph: the assert-the-shape numbers corrected with the same dated cite — the charter and the plan agree)"
  - "tools/arc_cost.py dedupe_calls (per-field-max merge, mutation-probe PINNED; same PR)"
  - "tools/test_arc_cost.py test_b_audit_headline_reproduced_on_the_archived_transcript (the witness asserting the corrected value)"
---

What changed and why it is a correction, not an extension:

The U-HE-48 acceptance figure for subagent IET (≈4.52M) and the derived R3
baseline totals (25.5M grand) were computed by [B]'s first-copy read of the
usage block. Measurement on the archived witness during the u-he-48 arc (codex
r1 finding, empirically vindicated) shows subagent transcripts stamp an early
PARTIAL output_tokens copy before the final one on 42 of 291 requestIds (main:
0 of 428), so the first-copy read undercounts subagent output. The extractor
merges copies by per-field max (order-independent; identical to the copy
whenever copies agree, which is every main-session call), and the ratified
figures become: subagent 4,636,541 IET (≈4.64M), main unchanged (418 calls /
20,996,434 IET), grand total ≈25.6M. All three normative carriers — the
acceptance bullet, the §8.1 R3-baseline narrative, and the charter §3
baseline — carry the same corrected values with this dated cite; the [B]
audit document itself is a historical record and keeps its printed numbers.
No contract number, field name, schema, or §6 ordering changes; the plan's
unit decomposition and the R0→R3 sequencing are untouched. Operator may
reverse by a dated plan note.
