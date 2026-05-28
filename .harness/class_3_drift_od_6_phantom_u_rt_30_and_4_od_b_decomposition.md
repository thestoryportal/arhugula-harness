# Class 3 drift: OD-6 phantom `U-RT-30` cite + missed 4-OD-B decomposition

**Status:** FILED 2026-05-28. Class 3 informational; non-blocking. 3 carry-shape findings at 3 layers — plan-side, spec-side, per-axis-CLAUDE.md side. Pre-impl-arc bookkeeping refresh.

**Trigger.** Operator routed OD-6 PARTIAL → RETIRE-READY advancement 2026-05-28. Empirical orientation surfaced the gate cite `U-RT-30 AC #2 STRUCK` at `harness-od/CLAUDE.md:146 + :169` references a unit that was **never authored** in any runtime plan version (`v2.5..v2.32`). Advisor pre-substantive verification (24th application of `[[advisor-before-substantive-work-for-cross-axis-blockers]]` discipline) caught the phantom before any production work.

---

## 1. Finding A — phantom `U-RT-30` cite in `harness-od/CLAUDE.md`

`harness-od/CLAUDE.md:146` cites `U-RT-30 PARTIAL-LAND, AC #2 STRUCK` as the OD-6 gate. `harness-od/CLAUDE.md:169` cites `U-RT-30 AC #2 un-STRIKE` as the closure path. **Both cites reference a unit ID that was never authored** at any runtime plan version. Verification:

```bash
git log --all --oneline -S "U-RT-30" -- design-substrate/Implementation_Plan_Harness_Runtime*
# → zero commits at any plan version

grep -rln "U-RT-30\b" design-substrate/Implementation_Plan_Harness_Runtime*.md
# → zero hits
```

`U-RT-30` originates as a forward-looking informal cite in `harness-runtime/src/harness_runtime/lifecycle/collector_daemon.py:69 + :160 + :233` authored at U-RT-29 landing. The collector daemon docstring named `U-RT-30` as the planned next unit but no plan unit by that ID was ever authored. The per-axis CLAUDE.md row picked up the code-comment shorthand and propagated it as canonical-sounding ledger framing.

## 2. Finding B — missed 4-OD-B SqliteWritePath decomposition

The actual closure path for OD-6 was **decomposed at OD plan v2.14** into cluster `4-OD-B — SqliteWritePath (4 units): U-OD-42 / U-OD-43 / U-OD-44 / U-OD-45` per `Phase D iteration-1 F1-04 absorption`:

| Unit | Scope | File |
|---|---|---|
| U-OD-42 | sqlite schema + WAL setup | `harness-od/src/harness_od/sqlite_span_store.py` (NEW) |
| U-OD-43 | RingBufferStage → sqlite batch INSERT flush | `harness-od/src/harness_od/ring_buffer.py` (EXTEND) + sqlite_span_store.py (EXTEND) |
| U-OD-44 | Retention policy lazy-on-write | `harness-od/src/harness_od/sqlite_span_store.py` (EXTEND) |
| U-OD-45 | Typed read interface | `harness-od/src/harness_od/sqlite_span_store_reader.py` (NEW) |

Cluster sibling `4-OD-C (U-OD-46..U-OD-49 rate-table)` is LANDED (`harness-od/src/harness_od/rate_table_*.py`). **4-OD-B is NOT landed** (verified: `find harness-od/src/harness_od -name "sqlite_span_store*"` returns no files).

The per-axis CLAUDE.md row at `harness-od/CLAUDE.md:146 + :169` never refreshed to cite the canonical U-OD-42..U-OD-45 unit IDs when the decomposition landed.

## 3. Finding C — spec-side phantom `U-RT-30` cites

OD spec v1.8 §C-OD-27 body text references the same phantom unit ID:

| Site | Text |
|---|---|
| §C-OD-27 introduction (line 169) | "in-memory ring-buffer operative at U-RT-30; sqlite write path deferred" |
| §C-OD-27.2 row 1 (line 199) | "Existing `RingBufferStage` (per U-RT-30) flushes to sqlite via batched INSERT" |
| `[[fork-trace-storage-pathclass-gap]]` (line 10 cite at v1.8 top change-note) | "Lifts U-RT-30 PARTIAL-LAND" |

These references survive verbatim through v1.9..v1.24 per delta-only spec-file convention. The spec body text is internally coherent (the `RingBufferStage` exists at production; the phantom-ness is only in the unit ID cite shape), so no spec-correctness amendment is owed — the cite-shape refresh is doc-hygiene only.

## 4. Finding D — U-OD-42 AC #1 column count drift

Plan v2.14 §U-OD-42 AC #1 text: "`spans` table created with **12 columns** per §C-OD-27.1".

OD spec v1.8 §C-OD-27.1 schema declares **14 columns** (span_id, trace_id, parent_span_id, name, kind, start_time_ns, end_time_ns, status_code, status_message, attributes_json, events_json, workflow_id, workflow_run_id, workflow_idempotency_key).

Plan AC undercount by 2. Implementation will follow the spec schema (14 columns) regardless of plan AC text per workspace convention "plan-conforms-to-spec at carrier-shape divergence." Plan AC text should refresh at the impl arc as a canonical-reading amendment.

---

## 5. Resolution disposition

**Findings A + B** (per-axis CLAUDE.md): **APPLIED at this arc** via bookkeeping refresh at `harness-od/CLAUDE.md:146 + :169`. Phantom `U-RT-30 AC #2 STRUCK` cite replaced with canonical `4-OD-B U-OD-42..U-OD-45 cluster (OD plan v2.14) not landed`.

**Finding C** (spec-side): NOT patched per FM-2 single-focus arc scope. Spec-body cite-shape refresh owed at OD spec v1.25 follow-on (or as adjacent observation at next substantive amendment). Production code follows spec semantics regardless of unit-ID cite shape.

**Finding D** (plan AC column count): NOT patched per FM-2. Plan AC text refresh owed at impl-arc canonical-reading amendment when U-OD-42 lands. Implementation follows spec verbatim.

## 6. ZERO production code change at this arc

This filing is doc-hygiene only:
- ZERO contract change
- ZERO signature change
- ZERO test addition
- ZERO production landing
- ZERO cross-axis cascade

## 7. Routing for the impl arc

Whoever opens the impl arc for U-OD-42..U-OD-45 4-OD-B cluster should:
1. Follow OD spec v1.8 §C-OD-27.1 schema verbatim (14 columns, not the 12-column AC text)
2. Refresh AC #1 text from "12 columns" → "14 columns" at canonical-reading amendment in OD plan v2.24 (sibling delta-only)
3. Optionally refresh §C-OD-27 spec-body U-RT-30 cites → U-OD-42..U-OD-45 at OD spec v1.25 (sibling)
4. Note: OD-6 PARTIAL → RETIRE-READY requires all 4 of U-OD-42..U-OD-45 landed + sqlite_span_store.py operational; TUI sub-gate per §C-OD-27.3 is independently deferred

## 8. Pattern catalogued

**Sub-species candidate at workflow v1.12 §7.4.7.2: `3.forward-looking-code-comment-becomes-phantom-ledger-cite`**. Distinct from prior species-3 sub-species. Closure-event-class: a code-author at unit N writes a docstring referencing planned-but-not-yet-authored unit N+1; downstream readers (per-axis CLAUDE.md authors, spec authors at substantive amendment arcs) pick up the cite as canonical-sounding shorthand; the planned unit N+1 never materializes (gets decomposed into different unit IDs); the phantom cite propagates verbatim across all delta files until empirical-verification audit at impl-arc orientation surfaces it.

Detection requires the workflow v1.9 §7.4.7.3.B-style empirical-verification audit. Strengthens the candidate "Sub-species" column extension at §7.4.7.2 already being tracked since v1.10.
