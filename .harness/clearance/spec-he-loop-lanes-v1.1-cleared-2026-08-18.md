---
artifact: .harness/spec/Spec_HE_Loop_Lanes_v1.md
version: v1.1
cleared_at: 2026-08-18T21:00:00-06:00
clearance_type: execution-correction-H_E-tooling
back_reference:
  - .harness/clearance/spec-he-loop-lanes-v1-cleared-2026-08-18.md (the v1 clearance this note amends by ONE mechanism parenthetical)
  - .harness/plan/Implementation_Plan_HE_Loop_Lanes_v1.md (U-HE-01, the executing unit)
  - "tools/finding_record.py (`_append_line`, the single implementation site) + tools/test_finding_record.py (witnesses)"
merge_commit: pending (pre-merge at filing time; same PR as the U-HE-01 code)
reviewer_chain:
  - "out-of-family Codex on the U-HE-01 PR: round 6 [P2] + round 7 [P1] surfaced C-HE-23 §2's `PIPE_BUF` parenthetical as unsatisfiable for a C-HE-24 row on the reference macOS host; round 8 reviews the amended text"
  - "author grounding: `PC_PIPE_BUF` = 512 on macOS; a minimal C-HE-24 row encodes to ≈700 bytes; POSIX scopes PIPE_BUF atomicity to pipes/FIFOs"
  - "council NOT convened (proportionality: mechanism-only, no contract guarantee changed; operator may reverse via v1.2)"
supersedes: spec-he-loop-lanes-v1-cleared-2026-08-18.md
superseded_by: null
---

# Clearance — `Spec_HE_Loop_Lanes` v1.1 (execution correction X1; H_E tooling, `C-HE-*` namespace)

v1.1 is v1 plus ONE dated change-note (X1) correcting the mechanism parenthetical in C-HE-23 §2's write-order clause: v1 said the JSONL finding row is written "single `write` under `PIPE_BUF`"; a C-HE-24 row cannot fit under macOS `PIPE_BUF` (512 B) and `PIPE_BUF` is a pipe/FIFO guarantee. The clause now states the regular-file guarantee the implementation carries — one `write` syscall per row on an `O_APPEND` descriptor, writers serialized by an exclusive lock on the log's own descriptor (outside C-HE-02 §1's scope: the log is REPO-resident and per lane, not `QUEUE_DIR` coordination state), short write rolled back before the failure surfaces. Every other sentence of every contract is byte-identical to v1; nothing re-litigates the v1 council pass or D5–D8.

**What this admits.** Consumers may rely on v1.1 as canonical for `C-HE-*` until a successor marker is filed. The v1 marker remains as the record of the full clearance chain (council + adversarial + Codex); this marker records only the X1 correction and its proportionate review. **Operator may reverse** X1 by a v1.2 change-note; `tools/finding_record.py::_append_line` is the single site.
