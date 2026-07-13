# B-HYGIENE-CITE-POINTER-SWEEP — R-FS-2 Wave 5 closure record

**Status:** CLOSED. Docs/cite-hygiene only, no behavioral code change.

## 1. Scope (per `.harness/r-fs-2-final-closure-implementation-plan-v1.md` §6)

1. Root `CLAUDE.md` §1.1 "12-namespace OTel schema" → 15 (cite C-OD-05 map); §2.3 CP pointer v1.86 → current head.
2. The ~14 `C-IS-13 §13.5` redundant-cite sites → drop per the recorded convention (clearance marker `Spec_Harness_Runtime-v1_93-cleared-2026-07-09.md`).
3. Any stale-carry text the Wave 1-4 arcs surfaced.

## 2. What was done

**Item 1.** Root `CLAUDE.md` §1.1 OD row: "12-namespace OTel schema" → "15-namespace OTel schema per C-OD-05 §5.1" (matching `harness-od/CLAUDE.md`'s already-correct 15-namespace count). The §2.3 "CP pointer v1.86" half of item 1 was already resolved before this arc opened — the 2026-07-12 R-600 cadence-5 pointer-staleness catch-up already moved the CP spec pointer to its current head (v1.96) and documented the v1.86→v1.96 chain inline; re-verified this is current, no further edit owed.

**Item 2.** Found and corrected all 9 `C-IS-13 §13.5` redundant-cite occurrences across 7 files (the clearance marker named 8 files; one, `local_first_otlp_collector.py`, was checked and found to cite a genuinely distinct, non-redundant `C-IS-13 §13.2` — untouched):
- `harness-cp/src/harness_cp/pause_resume_protocol.py` (3 occurrences) — dropped ` + C-IS-13 §13.5`, kept `C-IS-06 §6.2`.
- `harness-cp/src/harness_cp/per_step_override_evaluator.py` — same.
- `harness-cp/src/harness_cp/hitl_as_tool_call_rewriting.py` — same.
- `harness-cp/src/harness_cp/workload_binding_engine_class_selection.py` — same.
- `harness-od/src/harness_od/cost_namespace.py` — `C-IS-06 + C-IS-13 §13.5` → `C-IS-06`.
- `harness-cxa/src/harness_cxa/cp_audit_conversion.py` — same pattern.
- `harness-od/src/harness_od/audit_ledger_types.py` — this site cited `C-IS-13 §13.5` alone (no co-cited `C-IS-06`); replaced with `C-IS-06 §6.2` (the canonical hash-chain contract, per the clearance marker's own reasoning) rather than dropping to a bare, uncited docstring.

Re-verified empirically: `grep -rn "C-IS-13 §13.5"` across all axes returns zero hits post-fix.

**Item 3 (stale-carry text).** The one concrete stale-carry item Wave 1-4 surfaced was B-19's Class-3 finding: the CP-side `HARNESS_BREAKER_NAMESPACE_SCHEMA`'s 7 pre-v1.32 entries carry attribute names/concepts that don't match OD's canonical §7.1 emission set. Grounded further at this arc's opening: correcting it is NOT a byte-exact rename (only `scope` overlaps directly between the two 7-entry sets; the rest are genuinely different concepts — e.g. a single `state` field vs OD's separate `from_state`/`to_state`, and 4 OD-nonexistent concepts with no clear replacement target). This is a small design decision, not a mechanical sweep, so it's out of Wave 5's S-M budget. Registered as `B-20` at `.harness/post-phase-8-forward-register.md` (not built) rather than either silently fixed-under-scope or silently dropped.

## 3. Verification

- `grep -rn "C-IS-13 §13.5"` across all `harness-*` axes → 0 hits.
- `just overlay-check` → 364 nodes, 31/31 seams wired.
- `uv run pytest` workspace-wide → 5661 passed / 41 skipped / 1 xfailed (unchanged from pre-arc — no test assertions referenced these docstring-only cites).
- `uv run ruff check` / `ruff format --check` on touched axes → clean.
- `uv run pyright` on touched axes → 0/0/0.

No production behavior changed — every edit is a docstring/comment cite correction.
