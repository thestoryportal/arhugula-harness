---
artifact: design-substrate/Spec_Harness_Runtime_v1.md
version: v1.80
cleared_at: 2026-06-24T00:00:00-06:00
clearance_type: Phase-7-absorbed-via-bundled-absorption
back_reference:
  - design-substrate/Spec_Harness_Runtime_v1.md §14.23 C-RT-32 (the EngineOutputStore carrier — the v1.55 branch-API / v1.78 branch-dispatched-marker / v1.79 orchestrator-dispatched-marker sibling-extension precedent this dispatched-marker kind field follows)
  - design-substrate/Spec_Harness_Runtime_v1.md v1.78 (the per-branch dispatched marker this extends with the step_kind field)
  - design-substrate/Spec_Control_Plane_v1_62.md §1/§3 (the paired CP primary contract — the maybe-ran re-fire-safety classifier that keys on the dispatch-time kind)
merge_commit: <filled at merge>
reviewer_chain:
  - advisor — see the paired Spec_Control_Plane v1.62 marker (the residual-sizing reconcile; the re-fire-safe = {DECLARATIVE_STEP, INFERENCE_STEP} anchored to step_blast_radius READ_ONLY)
  - out-of-family Codex — the [P1] changed-manifest catch that MOTIVATED this delta (R1): reading the re-fire-safety kind from the resumed manifest opened an at-most-once hole (a TOOL_STEP-dispatched maybe-ran branch re-supplied as DECLARATIVE on a same-cardinality resume would re-dispatch + double-fire). The fix records the DISPATCH-TIME kind in the marker so the classifier is immune to manifest changes. R2 flagged an un-caught UnicodeDecodeError in `dispatched_branch_kinds` — a verified FALSE POSITIVE (`UnicodeDecodeError ⊆ ValueError`, already caught), made EXPLICIT in the except tuple + a torn-marker witness (test_dispatched_branch_kinds_torn_marker_maps_to_none) so the unreadable-marker → None → fail-closed boundary is self-evident. `[[hooks-codex-pilots-decorrelation-validated]]`.
  - the §14.23 sibling-extension precedent check (the dispatched-marker kind field + dispatched_branch_kinds read method are non-attested, not in the §6 chain, consumed via the cp_is_wiring getattr idiom — the v1.55/v1.78/v1.79 sibling-extension shape)
  - by-execution: the real-store dispatched_branch_kinds round-trip across restart (test_engine_output_store.py) + the full-chain changed-manifest fail-closed (test_workflow_driver_fanout_output_replay_full_chain.py); harness-runtime 2111 passed; pyright 0/0/0
supersedes: design-substrate/Spec_Harness_Runtime_v1.md v1.79 (delta chain; v1.79 body PRESERVED VERBATIM)
superseded_by: <none>
---

# Clearance — `Spec_Harness_Runtime v1.80`

v1.80 is a **bundled-absorption**, change-note-level delta over v1.79 (co-published with CP spec v1.62 + `harness-cp` / `harness-runtime` impl) — the §14.23 C-RT-32 `EngineOutputStore` dispatched-marker gains a DISPATCH-TIME step-kind field so the CP maybe-ran re-fire-safety classifier (CP v1.62) keys on the original kind, not the resumed manifest's kind.

- **§14.23 C-RT-32 dispatched-marker kind extension.** `record_branch_dispatched(run_key, branch_index, step_id)` gains a `step_kind: str` parameter (persisted alongside `step_id` in the same per-branch `.dispatched` marker JSON line) + a new read method `dispatched_branch_kinds(run_key) → dict[int, str | None]`. A marker with no / unreadable / non-str `step_kind` (a pre-arc v1.60/v1.61 marker, or a torn write) maps to `None` → the CP classifier fails closed (cannot prove re-fire-safety). Presence-only on the index (mirrors `present_dispatched_indexes`); the kind is best-effort.
- **The at-most-once changed-manifest guard (Codex [P1]).** Recording the kind at dispatch time makes the CP classifier immune to a same-cardinality changed-manifest resume — a branch that dispatched as an effect-bearing kind and crashed before capture stays classified by its original effect-bearing kind, never re-dispatched as a re-fire-safe one.

## Caveats for Phase 7 consumers

- Change-note-level: a field + read method on the existing C-RT-32 carrier. **No new contract, no new fail-class in the runtime** (the CP consumer maps a re-fire-unsafe maybe-ran branch to the existing `fan-out-crash-resume-cascade-policy-incomplete-recovery`), **no §5.2-hash change** (the marker is non-attested, not in the §6 chain), **no `StepDispatcher` Protocol widening, no new CXA edge** (consumed via the `cp_is_wiring` getattr idiom).
- The §14.23.1–.7 + §14.24 + the v1.59–v1.79 narrative are PRESERVED VERBATIM. IS / OD / AS / ADR specs UNCHANGED. CXA v2.20 UNCHANGED.
- Paired primary contract: CP spec C-CP-25 §25.12 / §25.15 v1.61 → v1.62.

## Notes

- Phase 7 consumers may rely on v1.80 as canonical until a successor marker is filed.
- See `.harness/clearance/README.md` for marker discipline.
