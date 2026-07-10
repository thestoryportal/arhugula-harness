---
artifact: design-substrate/Spec_Harness_Runtime_v1.md
version: v1.93
cleared_at: 2026-07-10T00:45:00-06:00
clearance_type: doc-hygiene-refresh
back_reference:
  - .harness/audit/Spec_Implementation_Gap_Audit_2026-07-09.md (finding F-B)
  - PR (cite-hygiene F-B/F-C apply pass, branch fix/cite-hygiene-f-b-f-c)
merge_commit: (squash-merge of the F-B/F-C cite-hygiene PR)
reviewer_chain:
  - 2026-07-09 spec-implementation gap audit (26-agent verify+refute re-audit; the phantom-cite family surfaced as DEFINITIONAL_NA)
  - advisor() full-transcript design-vet — scoped F-B correctly (caught the over-broad code-sweep hazard; the ~14 contract-cite sites are NOT this fix's targets)
  - spec-writer-style apply pass (change-note + version bump)
---

# Clearance — `Spec Harness Runtime v1.93`

v1.93 is a cite-hygiene correction absorbing gap-audit finding **F-B**. The §8b / §8d sub-agent-dispatch-composer prose cited a phantom **`C-IS-11 §11.1`** IS contract that does not exist (the IS spec defines only C-IS-01..10; this spec's own v1.8 §"Cross-axis citation substrate" change-note already flagged "prior v1 cited C-IS-11/14/15 which don't exist"). Corrected in place: §8b strikes the phantom "+ C-IS-11 §11.1" (the co-cited **C-IS-10 §10.5** JSONL-event-ledger seam already carries the `state_ledger_writer.append → WriteResult` contract); §8d's `WriteResult` semantic cite (APPENDED / IDEMPOTENT_NOOP) moves to **C-IS-07 §7.1** (the canonical IS idempotent-write contract). NO runtime-behavior / contract / identifier change.

**Companion code edits in the same PR (Phase-7 half of this bundled-absorption arc):**
- **F-C** — added authority docstring cites to the two `code_without_cite` files: `automatic_memory.py` → C-MEM-08/09/11/12/14; `external_cli_provider.py` → ADR-D7 §Decision / C-RT-05 / C-RT-02. Both `code_without_cite` overlay orphans are now cleared (overlay-check green, 355 nodes / 31 seams).
- **F-B / U-OD-30 carrier** — `harness-od/.../multi_tenant_trace_separation_and_audit_ledger.py` (the named CXA-OD-IS remap edge carrier) had its C-IS-14 §14.2 → **C-IS-10 §10.5** and C-IS-13 §13.5 → **C-IS-10 §10.3** anchors applied, per the already-decided remap at OD plan v2.4 §0.4.2 + CXA v2.18 §remap. Its test docstring updated to match.

## Scope accuracy + deferred residue (the record, so deferred ≠ dropped)

- **Audit-report scope correction.** The merged audit's F-B row said "propagate into remaining Runtime/CP/OD **spec** sites." Grounding showed there are **no live axis-spec sites** for C-IS-13/14 — they appear only in archive/handoff docs + `Plan_Executability_Audit_v1.md` (historical records, must not be rewritten) and superseded delta-chain versions (preserved verbatim). The only live *spec* site was the runtime `C-IS-11` (fixed here). The report slightly overstated F-B's spec surface; this marker is the accurate record.
- **Deferred by convention — ~8 files / ~14 contract-cite `C-IS-13 §13.5` sites** (`cost_namespace.py`, `pause_resume_protocol.py`, `per_step_override_evaluator.py`, `workload_binding_engine_class_selection.py`, `hitl_as_tool_call_rewriting.py`, `cp_audit_conversion.py`, `audit_ledger_types.py`, `local_first_otlp_collector.py`) are **intentionally NOT swept.** Correctness reason: they cite `C-IS-06 §6.2 + C-IS-13 §13.5` as a **contract** pairing, where **C-IS-06** is already the canonical hash-chain contract — so the right eventual fix is *drop the redundant `C-IS-13 §13.5`*, NOT inject the `C-IS-10 §10.3` seam anchor (which would be the wrong *kind* of cite at a contract site). Per the corpus convention (CXA v2.3 §remap anchor-note: "updated when next touched — non-blocking"), these are fixed opportunistically when the carrier code is next touched. They trip no gate (overlay-check green; not `code_without_cite` orphans since C-IS-06 satisfies them).

## Notes

- Phase 7 consumers may rely on this version as canonical until a successor marker is filed.
- See `.harness/clearance/README.md` for marker discipline.
