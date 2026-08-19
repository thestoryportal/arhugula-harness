---
artifact: .harness/spec/Spec_HE_Loop_Lanes_v1.md
version: v1.3
cleared_at: 2026-08-19T16:30:00-06:00
clearance_type: execution-correction-H_E-tooling
back_reference:
  - .harness/clearance/spec-he-loop-lanes-v1.2-cleared-2026-08-19.md (the v1.2 clearance this note amends by ONE parenthetical sentence in C-HE-30)
  - .harness/plan/Implementation_Plan_HE_Loop_Lanes_v1.md (U-HE-14, the executing unit; S3)
  - ".harness/spec/store-audit-he-loop-lanes.md + tools/test_store_audit.py (the C-HE-30 audit + its phase0 witness; `test_family_table_relation_cells_are_classified` pins each family's classification)"
merge_commit: pending (pre-merge at filing time; same PR as the S3 audit)
reviewer_chain:
  - "out-of-family codex rounds 2–4 on the U-HE-14 PR held the audit against the v1.2 C-HE-30 parenthetical and showed six named families are sole carriers of new coordination facts (transition marker payload per C-HE-06 §6; attempts/ rate window; tier-clean-cycles/ counter; lanes/<k>; hil-deliveries/; mechanized-checks-state.json promotion state) — not derived copies; round 4 named the resulting contract drift explicitly"
  - "author grounding: C-HE-06 §6 marker payload `{pid, host, target_action, created_at}` + third-party completion; C-HE-31 §4d promotion recorded only in the state file; C-HE-11 lane index exclusive create"
  - "out-of-family codex round 5+ on the U-HE-14 PR runs under X3 (recorded in the PR body)"
  - "council NOT convened (proportionality: one wording parenthetical; no store count, contract number, invariant, verification row, or implementation site changed; operator may reverse via v1.4)"
supersedes: spec-he-loop-lanes-v1.2-cleared-2026-08-19.md
superseded_by: null
---

# Clearance — `Spec_HE_Loop_Lanes` v1.3 (execution correction X3; H_E tooling, `C-HE-*` namespace)

v1.3 is v1.2 plus ONE dated change-note (X3) correcting the C-HE-30 clearance-fold parenthetical: v1–v1.2 described the families the fold added (reservation generations, the `transition.<token>` marker + `released.*/reclaimed.*` history, `lanes/<k>`, `.harness/mechanized-checks-state.json`) as "all derived from the authorities above, none a new authority for an existing fact". The S3 audit found the first clause false for six of them — each is the sole carrier of a NEW coordination fact the spec introduces and cannot be recomputed from the eight authorities — while the operative invariant (no existing fact gains a second carrier; the authority set for existing facts is exactly the eight) holds for every family. The parenthetical now says exactly that, and the audit classifies every family as `derived` or `sole carrier (new fact)` with a test pinning each cell. Every other sentence of every contract is byte-identical to v1.2; nothing re-litigates the v1 council pass, D5–D8, X1 or X2.

**What this admits.** Consumers may rely on v1.3 as canonical for `C-HE-*` until a successor marker is filed. The v1 marker remains the record of the full clearance chain; v1.1 records X1; v1.2 records X2; this marker records only X3 and its proportionate review. **Operator may reverse** X3 by a v1.4 change-note; there is no implementation site — the S4 units create these files against the unchanged C-HE-06/C-HE-11 contracts.
