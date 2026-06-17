---
artifact: design-substrate/Spec_Control_Plane_v1_37.md
version: v1.37
cleared_at: 2026-06-17T00:00:00+00:00
clearance_type: Phase-7-absorbed-via-fork-doc
back_reference:
  - .harness/class_1_fork_b4_per_step_prompt_override_stepoverride_extension.md
  - .harness/beyond-mvp-capability-boundary-ledger.md (B4 Slice 3 spine registration)
merge_commit: <pending — co-published bundled-absorption PR>
reviewer_chain:
  - advisor (pre-substantive, full-transcript) — reframed A-vs-B onto provenance scope; named the three resolving checks; flagged the abstraction-level objection to Route B
  - HEAD re-ground — overturned the stale v1.27 "no production caller" reading (override state-ledger entry IS wired at workflow_driver.py:1913-1930)
  - out-of-family Codex review at PR (decorrelated diff review)
  - standing FULL-SPEC operator directive 2026-06-12 (design back-flow pre-authorized)
supersedes:
superseded_by:
---

# Clearance — `Spec_Control_Plane v1.37`

v1.37 is an additive delta over v1.36 absorbing the **R-FS-1 arc B4 Slice 3** per-step prompt override. It adds one optional field — `StepOverride.prompt_version_sha: str | None = None` (C-CP-06 §6.1) — propagates it through `StepEffectiveBinding` + `resolve_step_binding` (§6.2), and adds a NEW §6.6 documenting the per-step prompt override's **provenance scope**: the wired per-step override state-ledger entry (`emit_override_state_ledger_entry`, hashing `binding.model_dump`), NOT the run-level C-IS-05 §5.2 procedural-tier hash. Governed by the v1.27 §2(d) X-AL-3 explicit-extension discipline (mirror precedents v1.20 `default_gate_level` / v1.22 `tenant_id` / v1.34 webhook-ctor binding-lift arcs).

Reviewed during clearance: the surface choice (`StepOverride` over `PromptSelectionManifest` — `step_id` is a workflow-scoped instance, not a run-level category; Route B is a Track-B reuse hazard); the provenance scope (step-level override ledger entry, following the per-step MODEL override precedent, after a HEAD re-ground overturned the stale v1.27 §16.5.6 "no production caller" note); and the scope boundary (per-step **prompt** only — per-step **role** is foreclosed by the runtime §14.5.3 single-role-source invariant and is the distinct Slice-4 gate). No operator gate: additive optional field, no committed invariant sacrificed.

Caveat for Phase 7 consumers: the runtime dispatch mechanism (precedence per-step > per-role > default; fail-loud unauthored sha; binding-tier governance parity) is impl-discretion per runtime §14.5.3 and co-lands in the same bundled-absorption PR; no IS-spec change is owed (provenance at the override ledger entry; §5.2 recipe unchanged). Per-step role override is OUT of scope (Slice 4).

## Notes

- Phase 7 consumers may rely on this version as canonical until a successor marker is filed.
- See `.harness/clearance/README.md` for marker discipline.
