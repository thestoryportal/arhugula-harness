---
artifact: design-substrate/Spec_Harness_Runtime_v1.md
version: v1.78
cleared_at: 2026-06-24T23:15:00-06:00
clearance_type: Phase-7-absorbed-via-bundled-absorption
back_reference:
  - design-substrate/Spec_Harness_Runtime_v1.md §14.23 C-RT-32 (the EngineOutputStore carrier — the v1.55 branch-API / v1.56 synthesis-API sibling-extension precedent this dispatched-marker + stamp API follows)
  - design-substrate/Spec_Harness_Runtime_v1.md §14.22 C-RT-31 (the effect-fence `try_reserve` reserve primitive this mirrors at branch granularity)
  - design-substrate/Spec_Control_Plane_v1_60.md §1/§2 (the paired CP primary contract — the strict-tier incomplete-recovery classification that consumes the markers + the cross-version stamp)
merge_commit: <filled at merge>
reviewer_chain:
  - advisor — see the paired Spec_Control_Plane v1.60 marker (the cross-version double-fire BLOCKING catch → the instrumented stamp; the synchronous-marker atomicity catch; the presence-only marker reading)
  - the §14.23 sibling-extension precedent check (the dispatched-marker + stamp API is non-attested, not in the §6 chain, consumed via the cp_is_wiring getattr idiom — the v1.55/v1.56 branch/synthesis-API shape)
  - out-of-family Codex — diff review (pending at PR-open)
supersedes: design-substrate/Spec_Harness_Runtime_v1.md v1.77 (delta chain; v1.77 body PRESERVED VERBATIM)
superseded_by: <none>
---

# Clearance — `Spec_Harness_Runtime v1.78`

v1.78 is a **change-note-level, bundled-absorption** delta (co-published with CP spec v1.60 + `harness-runtime`/`harness-cp` impl) — the runtime half of `B-FANOUT-CRASH-RESUME-STRICT-TIER-INCOMPLETE`: the §14.23 C-RT-32 `EngineOutputStore` gains the reserve-before-DISPATCH marker + cross-version stamp sidecar API.

- **`record_branch_dispatched(run_key, branch_index, step_id)` + `present_dispatched_indexes(run_key) → set[int]`** — the per-(run, branch) dispatch markers (`{sha256(run_key)}.branches/branch-{i}.dispatched`, no collision with the `branch-*.jsonl` capture files). Presence-only (a marker proves dispatch BEGAN; the at-most-once decision keys on `present_dispatched_indexes − recovered`).
- **`record_dispatch_instrumented(run_key)` + `dispatch_instrumented(run_key) → bool`** — the per-run cross-version stamp (`{sha256(run_key)}.branches/dispatch-instrumented.marker`), so the CP classifier trusts the markers only on a stamped (new-code) run.

## Caveats for Phase 7 consumers

- Change-note-level: sibling methods on the existing C-RT-32 carrier (the v1.55 branch-API / v1.56 synthesis-API precedent). NO new contract, NO new fail-class in the runtime, NO §5.2-hash change (the markers + stamp are non-attested, not state-ledger entries, not in the §6 chain), NO `StepDispatcher` Protocol widening, NO new CXA edge (consumed via the `cp_is_wiring` getattr idiom).
- Same crash-atomic `_append_path` (fsync + every-newly-created-ancestor-dir fsync) + same `_fanout_replay_store` gate as the branch capture. The CP driver writes the marker SYNCHRONOUSLY + fsynced strictly BEFORE the branch dispatches (the named invariant).
- The §14.23.1–.7 + §14.24 + the v1.59–v1.77 narrative are PRESERVED VERBATIM.
- Paired primary contract: CP spec C-CP-25 §25.12 / §25.15 v1.60.

## Notes

- Phase 7 consumers may rely on v1.78 as canonical until a successor marker is filed.
- See `.harness/clearance/README.md` for marker discipline.
