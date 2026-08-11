---
artifact: design-substrate/Spec_Control_Plane_v1_117.md
version: v1.117
cleared_at: 2026-08-11T22:30:00-07:00
clearance_type: Phase-7-absorbed-via-fork-doc
back_reference:
  - .harness/class_1_fork_b144_cp_24_1b_stale_retable.md
  - .harness/forward-register.yaml B-144 row (step-1 re-verified at HEAD this session)
  - "OD v1.32 change-note §Cardinality (mandated the downstream CP count updates)"
merge_commit: pending (this leg's PR merge; recorded at the PR)
reviewer_chain:
  - "loop-mode /resolve: codex VENUE A + advisor VENUE A (agreement, RESOLVE row); hitl scope SPLIT (codex in-delta / advisor follow-up) -> safer surgical option, B-153 minted, RESOLVE-SPLIT row"
  - "advisor grounding correction absorbed: breaker 7->9 venue is OD v1.32 (Spec_Operational_Discipline_v1_32.md), NOT CP v1.32 (zero breaker mentions) — verified at HEAD; code comment mislabels corrected in cascade"
  - out-of-family `just codex-review` at this leg's PR (to convergence)
  - merge-gate per LEAN protocol (single spec-conformance lens; tiny code surface)
supersedes: spec-control-plane-v1-116-cleared-2026-08-09.md
---

# Clearance — Spec_Control_Plane v1.117 (B-144 §24.1.B re-table, venue A)

**What v1.117 changes.** One amendment site: the C-CP-24 §24.1.B export table
(declared only at v1_2:2152-2166) is re-tabled to the live ratified counts —
`retry.*` 4 → 6 (C-CP-03 §3.5 v1.3 wholesale replacement) and `harness.breaker.*`
7 → 9 (OD C-OD-07 §7.1 as amended at OD v1.32). Declared §24.1.B subtotal 25 → 29;
declared CP-axis export sum 65 → 67. `fallback.*` / `lease.*` rows, §24.1.C, and the
composition-path summary byte-preserved.

**Same-PR cascade (bundled absorption §11.4).** `cp_namespace_export_manifest.py`
retry row 4 → 6 + comment rewrite (OD-v1.32 lineage mislabel fixed; docstring sum 67);
`test_cp_namespace_export_manifest.py` per-row dict + acceptance-#6 assertion 65 → 67.
Runtime breaker inversion check unaffected (compares breaker only, 9 == 9).

**Explicitly out of scope.** The hitl.*/Attribute-count column-semantics question —
minted as register row B-153; the re-table does not ratify span-names-as-attributes.
