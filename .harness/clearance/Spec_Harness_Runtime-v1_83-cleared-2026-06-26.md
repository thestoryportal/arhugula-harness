---
artifact: design-substrate/Spec_Harness_Runtime_v1.md
version: v1.83
cleared_at: 2026-06-26T00:00:00-06:00
clearance_type: Phase-7-absorbed-via-bundled-absorption
back_reference:
  - design-substrate/Spec_Control_Plane_v1_71.md §2 (registered B-FANOUT-CRASH-RESUME-PAUSE-RECONSTRUCT-MAYBE-RAN-FENCE-STEP-ID, owner_axis "CP + runtime" — "likely a per-branch dispatch-step_id store reader (runtime)")
  - design-substrate/Spec_Harness_Runtime_v1.md §14.23 C-RT-32 (the EngineOutputStore reserve-before-dispatch marker — record_branch_dispatched persists {step_id, step_kind} since v1.55/v1.80; this delta adds the step_id read accessor) + the v1.80 dispatched_branch_kinds sibling reader it mirrors
  - harness-runtime/src/harness_runtime/lifecycle/engine_output_store.py (the dispatched_branch_step_ids reader)
  - design-substrate/Spec_Control_Plane_v1_72.md (the paired PRIMARY consumer delta — the fence-recoverable PAUSE-reconstruct lift + the #742 crash-time step_id conjunct)
  - .harness/clearance/Spec_Control_Plane-v1_72-cleared-2026-06-26.md (the paired CP marker — full reviewer chain)
merge_commit: <filled at merge>
reviewer_chain:
  - advisor (full-transcript) — directed the reader (the marker already records step_id "for parity"; a sibling accessor of dispatched_branch_kinds avoids reading the opaque step_payload); confirmed the derivability finding (CP cannot derive the runtime fence key → the reader exposes only the step_id half, which is what the changed-step_id guard needs). Full chain in the paired CP v1.72 marker.
  - out-of-family Codex — diff review owed pre-merge.
  - by-execution witnesses: the real-store dispatched_branch_step_ids round-trip across restart + the torn-marker None boundary (test_engine_output_store.py); 36 store tests pass; the CP consumer full-chain witnesses (paired CP v1.72). pyright 0/0/0; ruff clean.
supersedes: <none>
superseded_by: <none>
---

# Clearance — `Spec_Harness_Runtime v1.83`

v1.83 is a **change-note-level bundled-absorption** delta (co-published with `harness-runtime` + `harness-cp` impl + tests + the paired CP delta v1.72) — the runtime half of the registered R-FS-1 arc `B-FANOUT-CRASH-RESUME-PAUSE-RECONSTRUCT-MAYBE-RAN-FENCE-STEP-ID`.

- **The §14.23 C-RT-32 `EngineOutputStore` gains `dispatched_branch_step_ids(run_key) → dict[int, str | None]`** — the step_id sibling of the v1.80 `dispatched_branch_kinds` accessor, reading the SAME per-branch `.dispatched` marker's already-recorded `step_id` field (persisted since the v1.55 reserve-before-dispatch API). A torn / missing / non-str step_id maps to `None` (→ the CP fence-recoverable classifier fails closed; cannot prove the original fence key). Presence-only on the index; best-effort step_id.
- **No new field, no new contract.** The marker shape `{"step_id": …, "step_kind": …}` is UNCHANGED; only a read accessor is added. The CP consumer (v1.72) keys the fence-recoverable PAUSE-reconstruct carrier + the #742 crash-time changed-step_id conjunct on this — without reading the opaque `step_payload` (X-AL axis isolation).

## Caveats for Phase 7 consumers

- Change-note-level: ADDITIVE. No new contract, no new field (the marker step_id predates this), no new fail-class, no §5.2-hash change (the marker is non-attested), no StepDispatcher Protocol widening, no new CXA edge. The §14.23.1–.7 + the v1.59–v1.82 narrative PRESERVED VERBATIM. IS / OD / AS / ADR specs UNCHANGED. CXA v2.20 UNCHANGED.
- **CP spec C-CP-25 §25.12 / §25.15 v1.71 → v1.72** is the paired PRIMARY contract.
