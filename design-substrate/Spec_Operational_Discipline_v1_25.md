# Spec: Operational Discipline — v1.25 (delta over v1.24)

---

## Change-note (v1.24 → v1.25)

**Scope of revision.** Fidelity-pure citation-correction patch closing 3 sibling phantom-`U-RT-30`-cite sites at §C-OD-27 spec body (line 10 §"What ships" enumeration + line 169 §C-OD-27 chapeau + line 199 §27.2 row 1) — all 3 are forward-looking unit-ID cites authored at OD spec v1.8 publication 2026-05-22 that never materialized as a runtime-axis plan unit (`U-RT-30` was the informal cite at `collector_daemon.py:69 + :160 + :233` for the deferred sqlite-write-path; closure path canonicalized at OD plan v2.14 §3.5..§3.8 as the `4-OD-B SqliteWritePath` cluster U-OD-42..U-OD-45 at OD-axis ownership per axis-ownership convention; real production carriers live at `harness-runtime/src/harness_runtime/lifecycle/ring_buffer.py` U-RT-29 landing + `harness-od/src/harness_od/sqlite_span_store.py` U-OD-42 landing — same mirror-shape as PR #17's phantom-U-RT-30 cite closure at the OD-6 retirement row + plan U-OD-43 file-path phantom closure at OD plan v2.24 §1.3 sibling delta). v1.8 file body PRESERVED VERBATIM per delta-only-spec-file convention; v1.25 publishes a canonical-reading amendment table at §1 that downstream readers apply when interpreting §C-OD-27.

**Closure event.** Production `4-OD-B SqliteWritePath` cluster LANDED at PR #18 single bundled arc 2026-05-28 (U-OD-42 + U-OD-43 + U-OD-44 + U-OD-45). H_T-OD-6 retirement transit: **PARTIAL → RETIRE-READY-on-merge** (structural-criterion-B MET via production binding chain; full RETIRED gates on operator deployment per X-AL-2). The v1.8 spec body cites to `U-RT-30` were correct-at-authoring (the phantom cite was the canonical informal pointer at production code-comment layer pre-v2.14 plan decomposition); they became stale at OD plan v2.14 cluster decomposition 2026-05-21+ (~7 days carry), and surfaced at empirical-verification orientation during PR #18 4-OD-B impl arc (advisor 25th + 27th + 28th applications spanning PR #17 + PR #18 lineage).

**Sub-species 3.forward-looking-code-comment-becomes-phantom-ledger-cite catalogued at workflow v1.12 §7.4.7.2.** Closure-event-class: (1) informal cite at production code-comment layer authored at landing-time-arc N as forward-looking placeholder; (2) cite propagates to design-substrate artifacts (spec body, retirement ledger row, plan file-path field) as canonical-text at arcs N+1..N+M; (3) plan decomposition at arc M+1 retires the forward-looking unit ID in favor of a real cluster; (4) cite-cascade at the propagation sites becomes phantom-as-written; (5) closure-arc empirical-verification at impl-time discovers + refreshes the cite-cascade. Distinct closure-event-class from prior species-3 sub-species (3.code-resolution / 3.fork-doc-closure / 3.workflow-grammar / 3.empirical-verification-of-external-authority / 3.same-session-immediate-sequel / 3.retirement-event-filing-arc / 3.binding-fix-not-schema-extension / 3.intra-spec-sibling-supersession / 3.carry-suggests-foreclosed-reading / 3.gate-text-stale-vs-production-landings). Three instances of this sub-species in 8 days: (i) PR #17 OD-6 retirement-row phantom-cite; (ii) plan U-OD-43 carrier-path phantom; (iii) spec §C-OD-27 §27.2 row 1 phantom-cite (this arc). Empirical cardinality at species-3 now ELEVEN sub-species; workflow v1.12 §7.4.7.2 "Sub-species" column extension increasingly warranted.

**Sibling-arc co-publication.** OD plan v2.23 → v2.24 absorbs the 4-OD-B cluster status + 4 plan-side drift carries at the same close (separate delta-only-plan-chain file per workspace convention). PR #18 production-side merged-ready at HEAD; v1.25 + v2.24 form the design-substrate doc-hygiene closure for the 4-OD-B cluster arc.

**ZERO contract change; ZERO signature change; ZERO acceptance-criterion change; ZERO behavior change; ZERO cross-axis cascade.** Fidelity-pure cite-correction patch under FM-2 single-focus arc scope.

**v1.24 + earlier PRESERVED VERBATIM.** All v1.24 substantive content (AttributeTier DERIVATIVE-naming retirement; §C-OD-04 §4.3.1 stability-classification table; v1.23 §4.3 4-tier requirement-level split; etc.) preserved unchanged. 2026-05-28.

---

## §1 — §C-OD-27 phantom-`U-RT-30`-cite canonical-reading amendment

Per delta-only convention, OD spec v1.8 §C-OD-27 body is NOT edited byte-exact; v1.25 publishes a canonical-reading amendment table that downstream readers apply when interpreting the 3 phantom-cite sites.

### §1.1 v1.8 line 10 — §"What ships" enumeration

| Pre-v1.25 reading (v1.8 + preserved v1.9..v1.24) | v1.25 canonical reading |
|---|---|
| `C-OD-27 (NEW) — Sqlite write-path contract. Lifts U-RT-30 PARTIAL-LAND (sqlite write deferred per [[fork-trace-storage-pathclass-gap]]) to spec form; closes H_T-OD-6 partial retirement frontier.` | `C-OD-27 (NEW) — Sqlite write-path contract. Lifts U-RT-29 in-memory ring-buffer LANDED + sqlite-write-path deferral (per [[fork-trace-storage-pathclass-gap]] Path B 2026-05-20 resolution: sqlite trace-storage is OD-internal, not via IS PATH_CLASS_REGISTRY) to spec form. Canonical closure path = OD plan v2.14 §3.5..§3.8 4-OD-B SqliteWritePath cluster U-OD-42..U-OD-45 (LANDED PR #18 2026-05-28); closes H_T-OD-6 partial retirement frontier on operator deployment per X-AL-2.` |

### §1.2 v1.8 line 169 — §C-OD-27 "Unblocks H_T-OD-6 PARTIAL" chapeau

| Pre-v1.25 reading (v1.8 + preserved v1.9..v1.24) | v1.25 canonical reading |
|---|---|
| `**Unblocks H_T-OD-6 PARTIAL.** Per ledger §6 + U-RT-30 PARTIAL-LAND status: in-memory ring-buffer operative at U-RT-30; sqlite write path deferred. C-OD-27 closes the partial.` | `**Unblocks H_T-OD-6 PARTIAL.** Per ledger §6 + U-RT-29 LANDED status: in-memory ring-buffer + collector daemon supervisor operative at `harness-runtime/src/harness_runtime/lifecycle/{ring_buffer.py,collector_daemon.py}` (RingBufferStage + RuntimeRingBuffer + CollectorDaemonSupervisor; LANDED at U-RT-29 cluster close); sqlite write path deferred at v1.8 publication, LANDED 2026-05-28 at 4-OD-B SqliteWritePath cluster (U-OD-42 schema + U-OD-43 batched-INSERT flush + U-OD-44 retention + U-OD-45 typed read; PR #18). C-OD-27 closes the partial at structural-criterion-B (production binding chain); full RETIRED gates on operator deployment exercising flush against real OTel span ingest per X-AL-2.` |

### §1.3 v1.8 line 199 — §27.2 row 1 "Flush from in-memory ring-buffer"

| Pre-v1.25 reading (v1.8 + preserved v1.9..v1.24) | v1.25 canonical reading |
|---|---|
| `1. **Flush from in-memory ring-buffer.** Existing `RingBufferStage` (per U-RT-30) flushes to sqlite via batched INSERT every `flush_interval_ms` (default 1000ms).` | `1. **Flush from in-memory ring-buffer.** Existing `RingBufferStage` + `RuntimeRingBuffer` (per U-RT-29 collector daemon + lifecycle/ring_buffer.py LANDED) flush to sqlite via batched INSERT through `async RuntimeRingBuffer.flush_to_sqlite(conn, *, now_ns)` invocation (per U-OD-43 LANDED 2026-05-28 at PR #18); cadence is operator-orchestrator-driven (NOT bound to `flush_interval_ms` at v1.8-baseline default 1000ms — the default-cadence binding is deferred to the orchestrator composition site per §27.5 row 1 implementer-discretion). Schema-pure helper `insert_spans(conn, rows: Iterable[SpanInsertRow]) -> int` at `harness-od/src/harness_od/sqlite_span_store.py` performs the executemany + INSERT OR IGNORE; `RuntimeRingBuffer.flush_to_sqlite` projects placeholder 6-field `SpanRow` → 14-field `SpanInsertRow` via `_project_span_row` runtime-axis helper.` |

---

## §2 — Sibling-cite cascade disposition

| Cite site | Pre-v1.25 carry | v1.25 disposition |
|---|---|---|
| OD plan v2.14 §3.6 U-OD-43 phantom file-path + dependency cite | `harness-od/src/harness_od/ring_buffer.py (EXTEND)` + `RingBufferStage carrier at harness-od/src/harness_od/ring_buffer.py (in-memory operative per OD plan v2.13)` | Closed at sibling delta OD plan v2.23 → v2.24 §1.3 canonical-reading amendment (this session co-publication). |
| `harness-od/CLAUDE.md` §4.1 OD substitution row for H_T-OD-6 phantom `U-RT-30 PARTIAL-LAND` cite | Closed at PR #17 doc-hygiene merge 2026-05-28 (workspace `[[pr-17-od-6-phantom-cite-bookkeeping]]`) | PRESERVED VERBATIM at v1.25; PR #17 closure stands. |
| `.harness/class_3_drift_od_6_phantom_u_rt_30_and_4_od_b_decomposition.md` filing 2026-05-28 (PR #17 anchor) | Class 3 informational drift filing | PRESERVED VERBATIM at v1.25; serves as historical anchor for the multi-arc phantom-cite cascade. |
| Workspace `CLAUDE.md` §2.3 OD spec row | Cites v1.24 | v1.25 row bump owed at sibling co-publication arc (this session); status = canonical-reading amendment over v1.24 (delta-only). |

---

## §3 — Sections preserved verbatim

| Section | Source | Status |
|---|---|---|
| §C-OD-27.1 canonical schema (14-column `spans` table + 4 indexes) | v1.8 §27.1 | PRESERVED VERBATIM; production at PR #18 implements verbatim including composite `idx_workflow` + composite `idx_time_range`. |
| §C-OD-27.2 row 2 (WAL mode + foreign-keys off) | v1.8 §27.2 | PRESERVED VERBATIM; production at PR #18 emits both `PRAGMA journal_mode=WAL` AND `PRAGMA foreign_keys=OFF`. |
| §C-OD-27.2 row 3 (retention policy default 7 days) | v1.8 §27.2 | PRESERVED VERBATIM; production at PR #18 (U-OD-44) implements via `retention_cleanup_lazy(conn, retention_days, now_ns)` at OD axis + `CollectorConfig.sqlite_retention_days: int = 7` operator-configurable field at runtime axis. |
| §C-OD-27.3 (typed read interface, no ad-hoc SQL) | v1.8 §27.3 | PRESERVED VERBATIM; production at PR #18 (U-OD-45) implements via `read_spans_by_workflow` + `read_spans_by_trace` + `read_span_by_id` at `harness-od/src/harness_od/sqlite_span_store_reader.py` (parameterized SQL only). |
| §C-OD-27.4 invariants 1 (per-deployment path) + 2 (WAL concurrent reads) + 3 (INSERT OR IGNORE idempotent writes) | v1.8 §27.4 | PRESERVED VERBATIM; production at PR #18 satisfies inv 3 via `INSERT OR IGNORE` at `insert_spans`; inv 2 via WAL pragma; inv 1 via deterministic db_path at `db_path.parent.mkdir(parents=True, exist_ok=True)`. |
| §C-OD-27.5 implementer-discretion (flush-interval tunability + retention policy implementation = lazy-on-write default) | v1.8 §27.5 | PRESERVED VERBATIM; production at PR #18 selects lazy-on-write per §27.5 row 2 default (U-OD-44 + retention-after-INSERT in flush_to_sqlite). |
| §C-OD-28 (`PRICE_TABLE_REF` rate-table format) and all sections at v1.9..v1.24 lineage | v1.9..v1.24 | PRESERVED VERBATIM per delta-only convention; v1.25 scope is single-focus §C-OD-27 phantom-cite refresh. |

---

## Adjacent observations (NOT patched per FM-2)

(a) **v1.8 §27.2 row 1 default `flush_interval_ms=1000ms` cadence carrier-name drift.** PR #18 production resolves cadence at the orchestrator composition site (NOT inside `RuntimeRingBuffer.flush_to_sqlite`); the v1.8 cite to `flush_interval_ms (default 1000ms)` is unbound at any production field. Routing target = future cadence-binding arc (orchestrator-driven cadence vs. configurable field on `CollectorConfig`). Class 3 informational.

(b) **v1.8 §27.5 row 1 "flush-interval tunability — default 1000ms; operator may tune via bootstrap config" deferred-to-implementation-discretion clause** un-bound at v1.8 publication; production at PR #18 inherits the implementer-discretion. Sibling to observation (a). Future spec revision could canonicalize the cadence-binding contract.

(c) **`flush_to_sqlite` `now_ns` kw-only parameter at production** at `harness-runtime/lifecycle/ring_buffer.py:RuntimeRingBuffer.flush_to_sqlite` is NOT in v1.8 spec; introduced at U-OD-43 + U-OD-44 absorption to thread the clock to retention-cleanup invocation. Implementation-layer addition; not a contract extension at OD spec layer.

(d) **`check_same_thread=False` at `initialize_span_store`** at production not constrained at v1.8 §C-OD-27 (spec is silent on threading model). Implementation-layer addition resolved at impl arc; not a contract extension.

(e) **`SpanInsertRow` 14-field Pydantic carrier at `harness-od/src/harness_od/sqlite_span_store.py`** introduced at U-OD-43 as the typed-API surface; v1.8 §C-OD-27 declares only the SQL schema, not the in-process carrier shape. Carrier-name candidate for future canonical-reading amendment if downstream consumers (TUI per §C-OD-27.3 deferred; audit-trace reconciliation per IS-OD composition) cite the carrier directly.

(f) **`_project_span_row` runtime-axis projection helper** at `harness-runtime/lifecycle/ring_buffer.py` resolves the placeholder `SpanRow` (6 fields at U-OD-27 + U-RT-29) → `SpanInsertRow` (14 fields) schema gap at the runtime axis boundary. Future widening at OTLP receiver replaces the projection without touching the OD helper surface. Class 3 informational; routing target = future OTLP-receiver impl arc + U-RT-29 `SpanRow` widening.

---

*End of `Spec_Operational_Discipline_v1_25.md` delta. Per delta-only convention, v1.24 + v1.23 + ... + v1.8 + v1.7 + ... + v1 file bodies PRESERVED VERBATIM and remain canonical-at-authoring for their respective scopes. v1.25 is the operative canonical reading for §C-OD-27 phantom-`U-RT-30`-cite interpretation going forward.*
