# Implementation Plan: Operational Discipline — v2.24 (delta over v2.23)

---

## Change-note (v2.23 → v2.24)

**Scope of revision.** Bundled fidelity-pure canonical-reading amendment closing 4 drift carries opened at the **`4-OD-B SqliteWritePath` cluster** impl arc landing 2026-05-28 (PR #18 single bundled cluster traversal U-OD-42 + U-OD-43 + U-OD-44 + U-OD-45). All four unit bodies at `Implementation_Plan_Operational_Discipline_v2_14.md` §3.5..§3.8 preserved verbatim per delta-only-plan-chain convention; v2.24 publishes the canonical-reading amendment table at §1 that downstream readers apply when interpreting U-OD-42 + U-OD-43 + U-OD-44 + U-OD-45.

**4-OD-B cluster status.** All four units **LANDED at PR #18 single arc 2026-05-28**. H_T-OD-6 transit: **PARTIAL → RETIRE-READY-on-merge** (structural-criterion-B MET at production binding chain — `sqlite_span_store.py` schema + INSERT helper + retention helper + reader module + `RuntimeRingBuffer.flush_to_sqlite` composition; full RETIRED gates on operator deployment exercising the flush path against real OTel span ingest per X-AL-2).

**Drift carries closed at v2.24.** 4 of 5 drift carries opened at PR #18 close at this arc:

| Carry | Closure path |
|---|---|
| **U-OD-42 AC #1 column count drift** (plan v2.14 cites "12 columns"; spec §C-OD-27.1 declares 14) | v2.24 §1.1 canonical-reading: "12 columns" → "14 columns per §C-OD-27.1"; 11 NEW tests at `test_sqlite_span_store.py` verify schema verbatim via `PRAGMA table_info` introspection |
| **U-OD-42 AC #3 missing pragma** (plan v2.14 cites WAL only; spec §27.2 row 2 mandates both `journal_mode=WAL` AND `foreign_keys=OFF`) | v2.24 §1.2 canonical-reading: AC #3 text refresh to include `PRAGMA foreign_keys=OFF`; advisor (27th application) caught at U-OD-42 authoring; emitted both at production + tests |
| **U-OD-43 phantom carrier-path** (plan v2.14 Files cite `harness-od/src/harness_od/ring_buffer.py (EXTEND)` + Depends-on cites `RingBufferStage carrier at harness-od/src/harness_od/ring_buffer.py (in-memory operative per OD plan v2.13)` — both phantom; real `RingBufferStage` lives at `harness-runtime/src/harness_runtime/lifecycle/ring_buffer.py` per U-RT-29 landing) | v2.24 §1.3 canonical-reading: Option (B) axis-split per operator routing this session — schema-pure helper at OD axis (`insert_spans` + `SpanInsertRow` carrier) + lifecycle composition at runtime axis (`RuntimeRingBuffer.flush_to_sqlite`); phantom unit-ID cite `U-RT-30 PARTIAL-LAND` refreshed to the real authoring site `U-RT-29 collector_daemon.py + lifecycle/ring_buffer.py LANDED` (mirror-shape to PR #17's phantom `U-RT-30` cite closure at OD-6 retirement row) |
| **U-OD-44 AC #3 operator-configurable field** (plan v2.14 cites "Operator-configurable retention_days via bootstrap config" without naming the carrier) | v2.24 §1.4 canonical-reading: NEW field `CollectorConfig.sqlite_retention_days: int = 7` at `harness-runtime/types.py:401` with positive-validator gate; threaded through `materialize_ring_buffer_stage` → `RuntimeRingBuffer.__init__(retention_days=)` → `flush_to_sqlite` retention-cleanup-after-INSERT call. 1 NEW config-threading test at `test_lifecycle_ring_buffer.py` |

**Sub-species 7c "retirement-ID-scoping-too-coarse" sibling pattern catalogued.** Phantom-carrier-path drift at plan U-OD-43 is sibling-class to PR #17's phantom-unit-ID drift at OD-6 retirement row + workspace species-3 sub-species `3.forward-looking-code-comment-becomes-phantom-ledger-cite` catalogued at workflow v1.12 §7.4.7.2. Common ancestor — **forward-looking-cite-at-authoring-time-becomes-phantom-at-landing-time** — emerges across multiple consecutive arcs (3 instances in 8 days: OD-6 retirement row + plan U-OD-43 file-path + spec §C-OD-27 §27.2 row 1). Sub-species catalogue expansion candidate at next workflow-doc revision pass.

**Co-publication this session.** Sibling delta OD spec v1.24 → v1.25 absorbing the §C-OD-27 `U-RT-30` phantom cite refresh + the §27.2 row 2 pragma enumeration audit at the spec declaration site (separate delta-only-spec-file per workspace convention). PR #18 production-side already merged-ready at HEAD with all 5 drift carries surfaced at PR description for operator visibility.

**ZERO new units; ZERO DAG topology change; ZERO coverage matrix structural delta; ZERO cross-axis cascade.** Bundled canonical-reading amendment at delta-only-plan-chain layer; U-OD-42..U-OD-45 unit-body authoring site at v2.14 §3.5..§3.8 preserved verbatim per delta-only convention.

**v2.23 + earlier PRESERVED VERBATIM.** All v2.23 substantive content (U-OD-40 status: LANDED + 5 ACs LANDED) preserved unchanged. 2026-05-28.

---

## §1 — `4-OD-B SqliteWritePath` cluster canonical-reading amendment

Per delta-only convention, U-OD-42..U-OD-45 unit bodies at the v2.14 authoring file (`Implementation_Plan_Operational_Discipline_v2_14.md` §3.5..§3.8) are NOT edited byte-exact; v2.24 publishes a canonical-reading amendment table that downstream readers apply when interpreting the cluster.

### §1.1 U-OD-42 — schema cardinality

| Pre-v2.24 reading (v2.14 authoring) | v2.24 canonical reading |
|---|---|
| AC #1: `spans` table created with **12 columns** per §C-OD-27.1 | AC #1: `spans` table created with **14 columns** per OD spec v1.8 §C-OD-27.1 (canonical schema enumerates `span_id` + `trace_id` + `parent_span_id` + `name` + `kind` + `start_time_ns` + `end_time_ns` + `status_code` + `status_message` + `attributes_json` + `events_json` + `workflow_id` + `workflow_run_id` + `workflow_idempotency_key`). v2.14 authoring carried a "12 columns" miscount that did not surface at any prior arc; closed at PR #18 production landing via `PRAGMA table_info` test cardinality assertion. |

### §1.2 U-OD-42 — pragma enumeration

| Pre-v2.24 reading (v2.14 authoring) | v2.24 canonical reading |
|---|---|
| AC #3: WAL mode enabled (`PRAGMA journal_mode=WAL`) | AC #3: WAL mode + foreign-keys-off enabled per OD spec v1.8 §C-OD-27.2 row 2 ("WAL mode + foreign-keys off"). BOTH `PRAGMA journal_mode=WAL` AND `PRAGMA foreign_keys=OFF` applied at `initialize_span_store` per declarative-DDL idempotency discipline. v2.14 AC #3 cited WAL only; advisor (27th `[[advisor-before-substantive-work-for-cross-axis-blockers]]` application) caught the §27.2 row 2 second-pragma elision at U-OD-42 authoring; production emits both + tests verify both via `PRAGMA journal_mode` + `PRAGMA foreign_keys` introspection. |

### §1.3 U-OD-43 — carrier-path + dependency

| Pre-v2.24 reading (v2.14 authoring) | v2.24 canonical reading |
|---|---|
| Files: `harness-od/src/harness_od/ring_buffer.py (EXTEND)` + `harness-od/src/harness_od/sqlite_span_store.py (EXTEND)`. Depends on: [U-OD-42]; **Requires existing (landed at main per U-RT-30 PARTIAL-LAND):** `RingBufferStage` carrier at `harness-od/src/harness_od/ring_buffer.py` (in-memory operative per OD plan v2.13). | Files: `harness-od/src/harness_od/sqlite_span_store.py (EXTEND)` (schema-pure helper `insert_spans` + `SpanInsertRow` typed carrier — OD-axis ownership of SQL composition per axis-ownership convention) + `harness-runtime/src/harness_runtime/lifecycle/ring_buffer.py (EXTEND)` (runtime-axis composition of lifecycle flush via NEW `async RuntimeRingBuffer.flush_to_sqlite(conn, *, now_ns)` + NEW `_project_span_row` helper for placeholder-`SpanRow`-to-14-column-`SpanInsertRow` projection at the runtime axis boundary). Depends on: [U-OD-42]; **Requires existing (landed at main per `U-RT-29` collector daemon + `harness-runtime/src/harness_runtime/lifecycle/ring_buffer.py`):** `RingBufferStage` + `RuntimeRingBuffer` carriers at runtime axis (NOT OD axis — phantom carrier-path correction). Mirror-shape closure to PR #17's phantom `U-RT-30` cite at OD-6 retirement row. Option (B) axis-split per operator routing 2026-05-28 (alternative considered: Option A monolithic harness-runtime extension; Option C phantom-path materialization at OD — both foreclosed at routing decision in favor of axis-boundary cleanliness). |

### §1.4 U-OD-44 — operator-configurable retention horizon

| Pre-v2.24 reading (v2.14 authoring) | v2.24 canonical reading |
|---|---|
| AC #3: Operator-configurable `retention_days` via bootstrap config | AC #3: Operator-configurable `retention_days` via NEW field `CollectorConfig.sqlite_retention_days: int = 7` at `harness-runtime/src/harness_runtime/types.py:401` per OD spec v1.8 §C-OD-27.2 row 3 default-7-days commitment. Positive-validator gate via `CollectorConfig._positive` field-validator. Threaded from `materialize_ring_buffer_stage(config, daemon)` → `RuntimeRingBuffer(retention_days=config.collector.sqlite_retention_days)` → `flush_to_sqlite` retention-cleanup-after-INSERT invocation. 1 NEW config-threading test at `test_lifecycle_ring_buffer.py::test_ring_buffer_carries_retention_days_from_config`. |

### §1.5 U-OD-43 — flush signature

| Pre-v2.24 reading (v2.14 authoring) | v2.24 canonical reading |
|---|---|
| Signatures: `async def flush_to_sqlite(self, conn, spans: list[Span]) -> int` | Signatures: `async def flush_to_sqlite(self, conn: sqlite3.Connection, *, now_ns: int \| None = None) -> int` — `spans` parameter dropped (buffer source-of-truth at `self._daemon._ingested_rows` per non-draining snapshot discipline at AC #5); NEW `now_ns` kw-only param threading the clock to U-OD-44 retention cleanup invocation (defaults to `time.time_ns()` for production; tests inject deterministic value). |

---

## §2 — Sibling-cite cascade disposition

| Cite site | Pre-v2.24 carry | v2.24 disposition |
|---|---|---|
| `harness-od/CLAUDE.md` §4.1 OD substitution row for H_T-OD-6 | Cites `4-OD-B SqliteWritePath` cluster (U-OD-42 + U-OD-43 + U-OD-44 + U-OD-45) as canonical closure path; status PARTIAL | Closure path verbatim correct; status transit PARTIAL → RETIRE-READY-on-merge owed at PR #18 merge close (retirement batch filing arc owed at follow-on per `[[verification-shape-sharpened-grep-vs-e2e]]` discipline — full RETIRED requires operator deployment exercising flush against real OTel ingest per X-AL-2). |
| Workspace `CLAUDE.md` §2.4 OD plan row | Cites v2.23 unit count 55 (U-OD-00, U-OD-01 – U-OD-54) | v2.24 row bump owed at sibling co-publication arc (this session); unit count preserved at 55; v2.24 status = canonical-reading amendment over v2.23 (delta-only). |
| OD spec v1.24 §C-OD-27 `U-RT-30` cite at §27.2 row 1 + §27.4 + §27.5 row 1 | Phantom unit-ID cite (mirror-shape to PR #17 + plan U-OD-43 sibling phantom) | Sibling delta OD spec v1.24 → v1.25 absorbs cite refresh this session (co-publication; separate delta-only-spec-file per workspace convention). |

---

## §3 — Sections preserved verbatim

| Section | Source | Status |
|---|---|---|
| U-OD-42 ACs #2 (4 indexes) + #4 (idempotent re-init) + #5 (unit test §C-OD-27.1 verbatim) | v2.14 §3.5 | PRESERVED VERBATIM at canonical-reading interpretation; production at PR #18 + 11 tests satisfy as-authored. |
| U-OD-43 ACs #1 + #2 + #3 + #4 + #5 (batched INSERT, INSERT OR IGNORE, JSON serialization, rowcount return, 100-span <100ms) | v2.14 §3.6 | PRESERVED VERBATIM at canonical-reading interpretation; production at PR #18 + 6 NEW runtime-side tests satisfy as-authored. |
| U-OD-44 ACs #1 (DELETE WHERE end_time_ns < cutoff) + #2 (lazy-on-write during flush) + #4 (rowcount return) + #5 (100-span 14-day retention integration test) | v2.14 §3.7 | PRESERVED VERBATIM at canonical-reading interpretation; production at PR #18 + 3 NEW retention tests + 1 NEW integration test satisfy as-authored. |
| U-OD-45 ACs #1 (parameterized SQL) + #2 (read_spans_by_workflow signature) + #3 (read_spans_by_trace signature) | v2.14 §3.8 | PRESERVED VERBATIM at canonical-reading interpretation; production at PR #18 + 6 NEW reader tests + NEW `read_span_by_id` convenience function (additive surface; not amendment) satisfy as-authored. |
| §0 plan-level invariants (unit count 55; DAG; coverage matrix) | v2.14 §0 preserved through v2.15..v2.23 | PRESERVED VERBATIM; ZERO structural delta at v2.24. |
| §4 coverage matrix | v2.14 §4 preserved through v2.15..v2.23 | PRESERVED VERBATIM; C-OD-27 §C-OD-27 (SqliteWritePath) → U-OD-42, U-OD-43, U-OD-44, U-OD-45 coverage row remains operative. |

---

## Adjacent observations (NOT patched per FM-2)

(a) **NEW `read_span_by_id` helper at U-OD-45.** Production module `harness-od/src/harness_od/sqlite_span_store_reader.py` includes a `read_span_by_id(conn, span_id) -> SpanInsertRow | None` helper not enumerated at v2.14 U-OD-45 AC #2 + #3 (which name only `read_spans_by_workflow` + `read_spans_by_trace`). This is additive — `read_span_by_id` exercises the existing primary-key index; not a new contract — but a future canonical-reading amendment could surface it for completeness. Class 3 informational.

(b) **Schema-gap projection at runtime axis** (production `SpanRow` 6 fields → `SpanInsertRow` 14 fields via `_project_span_row` defaults). Plan U-OD-43 is silent on the projection layer because v2.14 authoring assumed runtime would supply the full 14-column shape at ingest. Empirical at U-RT-29 + U-OD-27 lineage: production placeholder `SpanRow` is 6-field per Phase-2 deferral. Projection defaults are OTel-canonical (`kind=0` UNSPECIFIED + `status_code=0` UNSET + `events_json="[]"` + `parent_span_id` / `status_message` / `workflow_*` None). Future widening at OTLP receiver (or richer `SpanRow` carrier at U-RT-29) closes the gap without touching the OD helper surface. Class 3 informational; routing target = future OTLP-receiver impl arc.

(c) **Cross-thread sqlite via `check_same_thread=False`** at `initialize_span_store`. Plan U-OD-42 is silent on the threading model; production resolves at impl time via `asyncio.to_thread` dispatch from `flush_to_sqlite`. Single-writer invariant preserved via asyncio scheduler serialization of `RuntimeRingBuffer.flush_to_sqlite` calls. Class 3 informational; documented at module docstring at PR #18.

(d) **NEW `_NS_PER_DAY = 86_400 * 1_000_000_000` constant at `harness-od/sqlite_span_store.py`** introduced at U-OD-44 absorption. Mirror-constant `_NS_PER_HOUR` already lives at `harness-runtime/lifecycle/ring_buffer.py`. Future consolidation candidate at `harness-od/` time-unit primitives module. Class 3 informational.

(e) **Sibling-cite-cascade carry at workspace `CLAUDE.md` §2.4 OD plan row.** Co-publication this session bumps the row to v2.24; ZERO content amendment otherwise.

---

*End of `Implementation_Plan_Operational_Discipline_v2_24.md` delta. Per delta-only convention, v2.23 + v2.22 + ... + v2.14 + v2.13 + ... + v2.1 file bodies PRESERVED VERBATIM and remain canonical-at-authoring for their respective scopes. v2.24 is the operative canonical reading for U-OD-42..U-OD-45 unit-status + AC-text interpretation going forward.*
