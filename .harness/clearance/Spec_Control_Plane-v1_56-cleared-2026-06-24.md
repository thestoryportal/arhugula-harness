---
artifact: design-substrate/Spec_Control_Plane_v1_56.md
version: v1.56
cleared_at: 2026-06-24T09:00:00-06:00
clearance_type: Phase-7-absorbed-via-operator-ratified-amendment
back_reference:
  - .harness/r-fs-1-b-fanout-output-replay-impl-design.md (the materializable impl design; ✅ GATE RESOLVED + the "B-POSTJOIN-LLM-SYNTHESIS riding the above" section)
  - PR #721 (operator RATIFIED A — "the synthesis output gets a record-local capture-time self-hash either way"; PR2 sequenced per v1.55 §5)
  - Spec_Control_Plane_v1_55.md §3/§5 (named PR2 as the registered follow-on slice)
merge_commit: <filled at merge>
reviewer_chain:
  - advisor — the integration-point trace (the strategy still receives the synthesis step on the crash path), the three witness windows (W3 replay / pre-synthesis fresh / fail-closed), the dedup-safe ledger re-append, relax-only-the-crash-path (line 1798 pause-path stays fail-closed)
  - out-of-family Codex — diff review (pending convergence)
  - spec-writer apply pass (this arc; the as-built synthesis self-hash + capture + replay)
supersedes: <none>
superseded_by: <none>
---

# Clearance — `Spec_Control_Plane v1.56`

v1.56 is an **additive** delta over v1.55 — the **PR2 slice** of `B-FANOUT-OUTPUT-REPLAY`: the **synthesis self-hash + captured-synthesis-output replay** that RELAXES the v1.55 §3 crash-resume synthesis fail-closed. Paired with runtime spec **v1.76 → v1.77**.

- **§1 — synthesis self-hash + captured-output replay (C-CP-25 §25.12).** A captured terminal `POST_JOIN_SYNTHESIS` output carries a record-local capture-time self-hash (the #719 C9 residual: no ledger response_hash, sole authority on a W3 crash). On a crash-resume the captured output REPLAYS (self-hash + step_id material-diff verified), reproducible across the W3 window. Three fail-closed gates: present-but-unreadable / self-hash mismatch / changed body.
- **§2 — the v1.55 §3 crash-resume synthesis fail-closed is RELAXED.** A synthesis fan-out that crash-resumes under PROCEED recovers + replays/fresh-dispatches. The PAUSE-resume path stays fail-closed (the registered `B-FANOUT-PAUSE-SYNTHESIS` follow-on).
- **§3/§4 — three FULL-SPEC follow-ons registered** (cascade-policy, timeout-replay, pause-synthesis) → **R-FS-1 does NOT resolve at PR2** (the v1.55 §5 "PR2 resolves R-FS-1" is superseded by the PR1-surfaced cascade-policy Class-1 finding).

## Caveats for Phase 7 consumers

- Reproducibility covers the **post-capture W3 window only**; a crash BEFORE the synthesis ran re-dispatches FRESH on the reproduced branches (a new non-deterministic compose, consistent but not byte-reproducible) — see §1 honesty boundary.
- Additive: no new contract / enum / committed-invariant change; §25.12 Point 1 + D1 + D1.b PRESERVED LITERALLY (the synthesis record is a non-attested sidecar, not in the §6 chain). No §5.2-hash / §16.5-key change.
- PR2 flips the arc-ledger `registered → built`, but the three §3 follow-ons keep R-FS-1 ACTIVE.

## Notes

- Phase 7 consumers may rely on v1.56 as canonical until a successor marker is filed.
- See `.harness/clearance/README.md` for marker discipline.
