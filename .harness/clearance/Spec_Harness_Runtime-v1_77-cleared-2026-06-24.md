---
artifact: design-substrate/Spec_Harness_Runtime_v1.md
version: v1.77
cleared_at: 2026-06-24T09:00:00-06:00
clearance_type: Phase-7-absorbed-via-operator-ratified-amendment
back_reference:
  - .harness/r-fs-1-b-fanout-output-replay-impl-design.md (the materializable impl design; ✅ GATE RESOLVED)
  - PR #721 (operator RATIFIED A — the synthesis record-local self-hash, in-scope of the ratified mechanism; PR2 sequenced per v1.76)
  - design-substrate/Spec_Control_Plane_v1_56.md (the paired primary contract — C-CP-25 §25.12 v1.55 → v1.56)
merge_commit: <filled at merge>
reviewer_chain:
  - advisor — the integration-point trace, the three witness windows, the dedup-safe ledger re-append, relax-only-the-crash-path
  - out-of-family Codex — diff review (pending convergence)
  - spec-writer apply pass (this arc; the as-built EngineOutputStore synthesis sidecar API)
supersedes: <none>
superseded_by: <none>
---

# Clearance — `Spec_Harness_Runtime v1.77`

v1.77 is a **change-note-level** delta marking the **PR2 slice** of `B-FANOUT-OUTPUT-REPLAY` BUILT — the synthesis self-hash + captured-synthesis-output replay that RELAXES the v1.76 / CP v1.55 §3 synthesis-bearing crash-resume fail-closed. Paired with CP spec **v1.55 → v1.56**.

- **The §14.23 C-RT-32 `EngineOutputStore` synthesis sidecar API** — `record_synthesis(run_key, step_id, output, self_hash)` / `read_synthesis` / `synthesis_present` (a per-run `synthesis.jsonl` sidecar). The record carries a record-local capture-time self-hash; a record missing it is treated UNREADABLE → fail closed. RESERVE-before-COMMIT, gated on the same `_fanout_replay_store` predicate as the branch capture.
- **The relaxation** — a `POST_JOIN_SYNTHESIS` fan-out that crash-resumes under PROCEED replays its captured aggregate (W3 window) or re-dispatches fresh (pre-synthesis crash); CP spec v1.56 §1/§2. The PAUSE-resume synthesis path stays fail-closed (`B-FANOUT-PAUSE-SYNTHESIS`).

## Caveats for Phase 7 consumers

- Change-note-level: the §14.23 C-RT-32 contract body is the existing carrier; the synthesis API is a sibling extension (no new contract / fail-class / §5.2-hash / Protocol / CXA-edge). No §14.23 body section was edited.
- Reproducibility covers the post-capture W3 window only (CP v1.56 §1 honesty boundary).
- **R-FS-1 does NOT resolve at PR2** — three FULL-SPEC follow-ons (cascade-policy, timeout-replay, pause-synthesis) keep it ACTIVE (CP v1.56 §4).

## Notes

- Phase 7 consumers may rely on v1.77 as canonical until a successor marker is filed.
- See `.harness/clearance/README.md` for marker discipline.
