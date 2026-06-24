---
artifact: design-substrate/Spec_Harness_Runtime_v1.md
version: v1.76
cleared_at: 2026-06-23T20:00:00-06:00
clearance_type: Phase-7-absorbed-via-operator-ratified-amendment
back_reference:
  - .harness/r-fs-1-b-fanout-output-replay-impl-design.md (the materializable impl design; ✅ GATE RESOLVED)
  - PR #719 (C1⊥C9 dyadic council DESIGN pass — D1 framing narrowed)
  - PR #721 (operator RATIFIED A — non-attested branch-index-keyed sidecar)
  - PR for the B-FANOUT-OUTPUT-REPLAY PR1 core slice (this branch feat/b-fanout-output-replay)
merge_commit: <filled at merge>
reviewer_chain:
  - C1⊥C9 dyadic council + advisor red-team (PR #719) — the D1 framing correction
  - advisor — the store-as-authority correction (the binary ledger holds no mid-fan-out branch set), the synthesis-crash open-path catch, the shared-gate / wire-both-or-fail-closed traps
  - Operator AskUserQuestion 2026-06-23 — chose A (PR #721)
  - spec-writer apply pass (this arc; the as-built EngineOutputStore branch API + the CP crash-resume consumer)
supersedes: <none>
superseded_by: <none>
---

# Clearance — `Spec_Harness_Runtime v1.76`

v1.76 is a **change-note-level** delta marking the §14.23.7 / §14.21.7-registered "concurrent-fan-out output recording" follow-on **BUILT** — the PR1 core slice of `B-FANOUT-OUTPUT-REPLAY`. Paired with CP spec **v1.54 → v1.55**.

- **The §14.23 C-RT-32 `EngineOutputStore` branch sidecar API** — sibling methods to the linear `record`/`read_outputs`: `record_branch` / `read_branch_outputs` / `present_branch_indexes` / `record_orchestrator` / `read_orchestrator_output` / `orchestrator_present`. Per-branch-file keyed (`{sha256(run_key)}.branches/branch-{n}.jsonl` — N concurrent writers, no shared-file contention), RESERVE-before-COMMIT, with the `present_branch_indexes − read_branch_outputs.keys()` present-vs-readable fail-closed discriminator (the branch-level analogue of `journal_exists`).
- **The D1 framing correction** — supersedes the v1.74/v1.75 "SECOND §25.12-D1 sacrifice" forward-note (council-corrected #719 + operator-ratified #721): the sidecar is non-attested (NOT in the §6 hash chain), so §25.12 D1 is preserved literally. See CP spec v1.55 §4.
- **Synthesis-bearing crash-resume is FAIL-CLOSED** in this slice (CP spec v1.55 §3); the §14.24 C-RT-33 synthesis self-hash + captured-output replay that relaxes it is the registered PR2 follow-on slice.

## Caveats for Phase 7 consumers

- Change-note-level: the §14.23 C-RT-32 contract body is the existing carrier; the branch API is a sibling extension (no new contract / fail-class / §5.2-hash / Protocol / CXA-edge). No §14.23 body section was edited.
- PR1 core slice — the arc-ledger stays `registered` until the PR2 follow-on lands.

## Notes

- Phase 7 consumers may rely on v1.76 as canonical until a successor marker is filed.
- See `.harness/clearance/README.md` for marker discipline.
