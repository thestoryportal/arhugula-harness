---
artifact: design-substrate/Spec_Harness_Runtime_v1.md
version: v1.81
cleared_at: 2026-06-25T00:00:00-06:00
clearance_type: Phase-7-absorbed-via-bundled-absorption
back_reference:
  - design-substrate/Spec_Harness_Runtime_v1.md §14.23 C-RT-32 (the EngineOutputStore carrier — the v1.79 orchestrator-dispatched-marker + the v1.80 branch-dispatched-marker-kind sibling-extension precedent this orchestrator-marker kind field follows)
  - design-substrate/Spec_Harness_Runtime_v1.md v1.79 (the orchestrator dispatched marker this extends with the step_kind field) + v1.80 (the per-branch dispatched-marker kind extension this is the single-orchestrator analogue of)
  - design-substrate/Spec_Control_Plane_v1_64.md §1/§2 (the paired CP primary contract — the orchestrator-maybe-ran re-fire-safety classifier that keys on the dispatch-time kind)
merge_commit: <filled at merge>
reviewer_chain:
  - advisor — see the paired Spec_Control_Plane v1.64 marker (the ×2 design + decomposition reconcile; the re-fire-safe = {DECLARATIVE_STEP, INFERENCE_STEP} anchored to step_blast_radius READ_ONLY; advisor affirmed (a1) needs a runtime SPEC delta — the orchestrator marker records step_id, not kind, so there is no existing orchestrator-kind reader → extending C-RT-32 is a runtime spec delta, mirror v1.78→v1.79 / v1.79→v1.80)
  - out-of-family Codex — see the paired Spec_Control_Plane v1.64 marker for the full verdict (1 GENUINE [P2] on the CP-side re-fire-safe relaxation — a missing dispatch-instrumented-stamp gate that would have let an orphaned orchestrator marker re-dispatch; FIXED + witnessed — plus 3 out-of-scope [P2]s on pre-existing untracked dashboard-design / skills artifacts NOT in this PR). NO finding on this runtime store delta (the `orchestrator_dispatched_kind` reader + the `step_kind` field).
  - the §14.23 sibling-extension precedent check (the orchestrator dispatched-marker kind field + `orchestrator_dispatched_kind` read method are non-attested, not in the §6 chain, consumed via the cp_is_wiring getattr idiom — the v1.55/v1.78/v1.79/v1.80 sibling-extension shape; the torn / pre-v1.81 marker → None reading mirrors `dispatched_branch_kinds`' torn-marker safety boundary)
  - by-execution: the real-store `orchestrator_dispatched_kind` round-trip across restart + the pre-v1.81-marker → None (test_engine_output_store.py); the full-chain re-fire-safe-recovers / effect-bearing-fails-closed / pre-v1.81-fails-closed (test_workflow_driver_fanout_output_replay_full_chain.py); harness-runtime 2114 passed / 23 skipped / 1 xfailed; pyright 0/0/0
supersedes: design-substrate/Spec_Harness_Runtime_v1.md v1.80 (delta chain; v1.80 body PRESERVED VERBATIM)
superseded_by: <none>
---

# Clearance — `Spec_Harness_Runtime v1.81`

v1.81 is a **bundled-absorption**, change-note-level delta over v1.80 (co-published with CP spec v1.64 + `harness-cp` / `harness-runtime` impl) — the §14.23 C-RT-32 `EngineOutputStore` ORCHESTRATOR dispatched-marker gains a DISPATCH-TIME step-kind field so the CP orchestrator-maybe-ran re-fire-safety classifier (CP v1.64) keys on the original kind, not the resumed manifest's kind. The single-orchestrator analogue of the v1.80 per-branch dispatched-marker kind extension.

- **§14.23 C-RT-32 orchestrator dispatched-marker kind extension.** `record_orchestrator_dispatched(run_key, step_id)` gains a `step_kind: str` parameter (persisted alongside `step_id` in the same single `orchestrator.dispatched` marker JSON line) + a new read method `orchestrator_dispatched_kind(run_key) → str | None`. A marker with no / unreadable / non-str `step_kind` (a pre-v1.81 v1.79-era orchestrator marker, which recorded only `step_id`, or a torn write) maps to `None` → the CP classifier fails closed (cannot prove re-fire-safety; the v1.79 behavior preserved). Presence remains the v1.79 fail-closed signal (`orchestrator_dispatched`); the kind is best-effort.
- **§14.23 C-RT-32 cardinality presence reader (Codex R3).** A new presence-only `fanout_cardinality_present(run_key) → bool` (a sibling of `read_fanout_cardinality`, mirroring `orchestrator_present`): returns whether the cardinality MARKER file exists, distinct from `read_fanout_cardinality` (which returns `None` for BOTH an absent AND a present-but-torn marker). The CP orchestrator re-fire-safe corruption guard keys on this presence so a torn cardinality marker — which still proves the run advanced past orchestrator capture — fails closed (`[[durable-recovery-presence-validity-scope]]`).
- **The at-most-once changed-manifest guard.** Recording the kind at dispatch time makes the CP classifier immune to a same-shape changed-manifest resume — an orchestrator that dispatched as an effect-bearing kind and crashed before capture stays classified effect-bearing, never re-dispatched as a re-fire-safe one.

## Caveats for Phase 7 consumers

- Change-note-level: a field + read method on the existing C-RT-32 carrier. **No new contract, no new fail-class in the runtime** (the CP consumer maps an effect-bearing / un-kinded maybe-ran orchestrator to the existing CP-side `fan-out-crash-resume-orchestrator-maybe-ran`), **no §5.2-hash change** (the marker is non-attested, not in the §6 chain), **no `StepDispatcher` Protocol widening, no new CXA edge** (consumed via the `cp_is_wiring` getattr idiom).
- The §14.23.1–.7 + §14.24 + the v1.59–v1.80 narrative are PRESERVED VERBATIM. IS / OD / AS / ADR specs UNCHANGED. CXA v2.20 UNCHANGED.
- Paired primary contract: CP spec C-CP-25 §25.12 / §25.15 v1.63 → v1.64.

## Notes

- Phase 7 consumers may rely on v1.81 as canonical until a successor marker is filed.
- See `.harness/clearance/README.md` for marker discipline.
