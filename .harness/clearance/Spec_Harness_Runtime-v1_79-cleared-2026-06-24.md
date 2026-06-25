---
artifact: design-substrate/Spec_Harness_Runtime_v1.md
version: v1.79
cleared_at: 2026-06-24T23:55:00-06:00
clearance_type: Phase-7-absorbed-via-bundled-absorption
back_reference:
  - design-substrate/Spec_Harness_Runtime_v1.md §14.23 C-RT-32 (the EngineOutputStore carrier — the v1.55 branch-API / v1.56 synthesis-API / v1.78 branch-dispatched-marker sibling-extension precedent this orchestrator dispatched-marker API follows)
  - design-substrate/Spec_Harness_Runtime_v1.md v1.78 (the per-branch reserve-before-dispatch marker this mirrors at orchestrator granularity)
  - design-substrate/Spec_Control_Plane_v1_61.md §1/§2 (the paired CP primary contract — the orchestrator-dispatch classification that consumes the orchestrator marker + the cross-version stamp)
merge_commit: <filled at merge>
reviewer_chain:
  - advisor — see the paired Spec_Control_Plane v1.61 marker (the synchronous-dispatch-needs-no-atomicity-dance simplification; the maybe-ran residual + PROCEED-not-covered-by-#724 catch → the registered follow-on; the `_append_path`-fsync confirmation; the HIERARCHICAL nesting witness)
  - the §14.23 sibling-extension precedent check (the orchestrator dispatched-marker API is non-attested, not in the §6 chain, consumed via the cp_is_wiring getattr idiom — the v1.55/v1.56/v1.78 sibling-extension shape; a SINGLE per-run marker, no per-index)
  - out-of-family Codex — diff review (pending at PR-open)
supersedes: design-substrate/Spec_Harness_Runtime_v1.md v1.78 (delta chain; v1.78 body PRESERVED VERBATIM)
superseded_by: <none>
---

# Clearance — `Spec_Harness_Runtime v1.79`

v1.79 is a **bundled-absorption**, change-note-level delta over v1.78 (co-published with CP spec v1.61 + `harness-cp`/`harness-runtime` impl) — the build of `B-FANOUT-CRASH-RESUME-ORCHESTRATOR-DISPATCH`, extending the §14.23 C-RT-32 `EngineOutputStore` reserve-before-dispatch API to the orchestrator's own `steps[0]` sequential dispatch.

- **§14.23 C-RT-32 orchestrator reserve-before-dispatch API.** `record_orchestrator_dispatched(run_key, step_id)` + `orchestrator_dispatched(run_key) → bool` — a SINGLE per-run marker (`{sha256(run_key)}.branches/orchestrator.dispatched`, no collision with the `orchestrator.jsonl` reserve-before-COMMIT capture). Written synchronously + fsynced (same `_append_path` fsync + ancestor-dir fsync as the branch markers) STRICTLY BEFORE the orchestrator dispatch; the orchestrator dispatch is itself synchronous, so no atomicity dance is needed. Gated by the same `_fanout_replay_store` predicate + the per-run `record_dispatch_instrumented` cross-version stamp (also written in the orchestrator block before the dispatch).
- Presence-only: `orchestrator_dispatched` (a torn/unreadable marker still proves dispatch began → the conservative maybe-ran reading). The CP consumer keys the at-most-once decision on the marker's **presence alone** + the absent terminal capture ⟹ maybe-ran ⟹ fail closed; absent marker ⟹ provably-not-run / pre-arc ⟹ fresh. The cross-version guard is INHERENT (the marker is a new file → a pre-arc journal has none); the classifier needs no stamp gate, and an orphaned marker without the stamp still fails closed (out-of-family Codex [P2]).

## Caveats for Phase 7 consumers

- Change-note-level: sibling methods on the existing C-RT-32 carrier. **No new contract, no new fail-class in the runtime** (the CP consumer maps a maybe-ran orchestrator to FAILED via the NEW CP-side `fan-out-crash-resume-orchestrator-maybe-ran`; the store raises no taxonomy), **no §5.2-hash change** (the marker is non-attested, not in the §6 chain), **no `StepDispatcher` Protocol widening, no new CXA edge** (consumed via the `cp_is_wiring` getattr idiom).
- The §14.23.1–.7 + §14.24 + the v1.59–v1.78 narrative are PRESERVED VERBATIM. IS / OD / AS / ADR specs UNCHANGED. CXA v2.20 UNCHANGED.
- Paired primary contract: CP spec C-CP-25 §25.12 / §25.15 v1.60 → v1.61.

## Notes

- Phase 7 consumers may rely on v1.79 as canonical until a successor marker is filed.
- See `.harness/clearance/README.md` for marker discipline.
