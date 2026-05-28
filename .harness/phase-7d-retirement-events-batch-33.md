# Phase 7d Retirement Events — Batch 33

| Field | Value |
|---|---|
| Batch number | 33 |
| Filed at | 2026-05-28 (post PR #18 `4-OD-B SqliteWritePath cluster` merge to main at `406fbf5` — U-OD-42 + U-OD-43 + U-OD-44 + U-OD-45 + design-substrate OD plan v2.24 + OD spec v1.25 doc closures all landed) |
| Filed by | `phase-7-substitution-retirement` skill §3.2 verification-shape steps 1–5; structural-criterion-B closure per X-AL-2 first conjunct (units landed + production binding-chain complete) |
| Predecessor batch | `phase-7d-retirement-events-batch-32.md` (2026-05-28, H_T-OD-5 RETIRE-READY → RETIRED via mech-β AC #8 green; cumulative 37/54 RETIRED + 0/54 RETIRE-READY + 4/54 PARTIAL + 11/54 STILL-BOUNDED + 2/54 STILL-BOUNDED-INDEFINITELY = 41/54 = 75.9% pipeline-advanced) |

---

## §0 Batch context

**Status type: 1 PARTIAL → RETIRE-READY transit (H_T-OD-6). Cumulative RETIRED count unchanged at 37/54 (68.5%); RETIRE-READY count increments 0/54 → 1/54 (**RETIRE-READY bucket re-populates after the batch-32 EMPTY-state — one calendar-day flip); PARTIAL count decrements 4/54 → 3/54; STILL-BOUNDED count unchanged at 11/54; STILL-BOUNDED-INDEFINITELY count unchanged at 2/54; pipeline-advanced 41/54 = 75.9% (unchanged — within-tier promotion PARTIAL → RETIRE-READY). Cardinality check: 37 + 1 + 3 + 11 + 2 = 54 ✓.**

This batch records the structural-criterion-B closure for **H_T-OD-6** (Local-first OTLP ingestion per OD spec v1.8 §C-OD-27 sqlite write-path contract; carriers U-OD-42 schema + U-OD-43 batched-INSERT flush + U-OD-44 lazy-on-write retention + U-OD-45 typed read interface; Meta-Architecture §5.4 row OD-6 local-first OTLP ingestion) from PARTIAL → RETIRE-READY via PR #18 merge at single bundled arc:

| Commit | Artifact | Authority |
|---|---|---|
| `406fbf5` | `harness-od/src/harness_od/sqlite_span_store.py` NEW — 14-col schema + WAL + foreign_keys=OFF + 4 indexes + INSERT OR IGNORE + retention helper; `harness-od/src/harness_od/sqlite_span_store_reader.py` NEW typed read interface; `harness-runtime/src/harness_runtime/lifecycle/ring_buffer.py` EXTEND — `async RuntimeRingBuffer.flush_to_sqlite` + `_project_span_row` schema-gap projection; `harness-runtime/src/harness_runtime/types.py` EXTEND — `CollectorConfig.sqlite_retention_days: int = 7`; `design-substrate/Implementation_Plan_Operational_Discipline_v2_24.md` + `design-substrate/Spec_Operational_Discipline_v1_25.md` NEW doc closures | PR #18 squash-merge to main 2026-05-28 |
| (this commit) | `.harness/phase-7d-retirement-events-batch-33.md` (this file) — retirement event filing documenting Criterion A + B structural transit | X-AL-2 first conjunct + retirement-shape discipline at workspace's "deployment-time opt-in gate" precedent (operator deployment required for full RETIRED transit) |
| (this commit) | `harness-od/CLAUDE.md` §4.1 row PARTIAL → RETIRE-READY transition for H_T-OD-6; cumulative-counts line refresh per workflow v1.12 §7.4.7.3.C retirement-tier-transit audit | Workspace bookkeeping discipline per `.harness/phase-7d-retirement-ledger-v2.md` |
| (this commit) | Memory entry `h-t-od-6-retire-ready-batch-33.md` documenting the PARTIAL → RETIRE-READY transit (post-deployment-opt-in-gate closure pattern; sibling to OD-5 batch-28 transit-shape) | Workspace memory discipline |

Per the operator-ratified runtime-only substitution-site reading at `.harness/phase-7d-retirement-ledger-v2.md` §2.1 + line-33 strict-reading discipline + the batch-16 §6 verification-shape sharpening discipline (eleventh prospective application at batch-33):

> RETIRE-READY = (criterion A MET) ∧ (criterion B structural-MET) ∧ (deployment-time opt-in gate identified as terminal in-CLI state).
> RETIRED = above ∧ (criterion B operational-MET via real-substrate exercise at deployment time).

Under that discipline, H_T-OD-6 transitions PARTIAL → **RETIRE-READY** via PR #18 single bundled arc:

- **Criterion A** (cited unit IDs landed). MET at this batch. U-OD-42 (sqlite schema + WAL/foreign_keys=OFF + 4 indexes at `harness-od/src/harness_od/sqlite_span_store.py`) + U-OD-43 (batched INSERT OR IGNORE via `insert_spans` helper + `async RuntimeRingBuffer.flush_to_sqlite` at runtime axis with `_project_span_row` schema-gap projection from placeholder 6-field `SpanRow` to 14-field `SpanInsertRow`) + U-OD-44 (lazy-on-write retention via `retention_cleanup_lazy` helper + operator-configurable `CollectorConfig.sqlite_retention_days: int = 7`) + U-OD-45 (typed read interface at `harness-od/src/harness_od/sqlite_span_store_reader.py` — `read_spans_by_workflow` / `read_spans_by_trace` / `read_span_by_id`). All 4 cluster units landed at PR #18 merge `406fbf5`.

- **Criterion B structural-MET at this batch.** Three binding-chain stages empirically verified for the sqlite-write-path surface:
  - Stage 1 (carrier landed) — `sqlite_span_store.py` opens connection with `check_same_thread=False` + WAL mode + foreign_keys=OFF pragmas + 14-col schema with composite `idx_workflow` + composite `idx_time_range` + `idx_idempotency` + `idx_trace` indexes per OD spec v1.8 §C-OD-27.1; `SpanInsertRow` Pydantic v2 frozen carrier preserves §C-OD-27.1 column-set + nullability discipline at the OD-axis schema boundary.
  - Stage 2 (production consumer site) — `RuntimeRingBuffer.flush_to_sqlite(conn, *, now_ns)` at `harness-runtime/src/harness_runtime/lifecycle/ring_buffer.py` snapshots the daemon's `_ingested_rows` buffer + projects each `SpanRow` to `SpanInsertRow` via `_project_span_row` (OTel-canonical defaults — kind=0 UNSPECIFIED, status_code=0 UNSET, events_json="[]", workflow_* and parent_span_id None) + dispatches `insert_spans` via `asyncio.to_thread` (sqlite blocking calls; runtime event loop free) + applies `retention_cleanup_lazy` per §C-OD-27.5 row 2 lazy-on-write default after every flush.
  - **Stage 3 (e2e exercise PASS against real substrate) — NOT MET at this batch.** Production workflow has not yet executed `RuntimeRingBuffer.flush_to_sqlite` against the daemon's live ingested span buffer at a real deployment runtime; the orchestrator binding-site that periodically invokes flush is owed at a follow-on integration arc (or at `harness run` / `harness daemon` startup binding once operator deployment exercises the flush cadence).

- **Deployment-time opt-in gate identified as terminal in-CLI state (sub-species 7.deployment-time-opt-in-gate — THIRD member, sibling to AS-8d batch-31 + OD-5 batch-32).** Full RETIRED transit requires (a) operator deploys harness against real workload generating spans; (b) collector daemon (U-RT-29) ingests spans into `_ingested_rows`; (c) orchestrator (or operator-bound flush trigger) invokes `RuntimeRingBuffer.flush_to_sqlite(conn, ...)` against the runtime sqlite span store; (d) sqlite spans table observed populated at the deployment's `.harness/observability/spans.db` deterministic per-deployment path. Mirror H_T-AS-8d batch-25 + H_T-OD-5 batch-28 operator-opt-in pattern.

## §1 Sub-row substitution-status table

Pre-batch-33 OD-axis bucket (post-batch-32):

| Substitution | Status | Source |
|---|---|---|
| H_T-OD-1 (deferral envelope) | STILL-BOUNDED | No `deferral_envelope` import in `harness-runtime/` |
| H_T-OD-2 (OTel SDK base + GenAI semconv) | RETIRED batch-2 (2026-05-20) | LIVE at `lifecycle/llm_dispatch.py` |
| H_T-OD-3 (Composite Sampler) | STILL-BOUNDED | Stock `ParentBased(ALWAYS_ON)` (transits to PARTIAL at batch-34) |
| H_T-OD-4 (Pre-Collector redaction SpanProcessor) | STILL-BOUNDED | Stock `BatchSpanProcessor`; zero redaction references |
| H_T-OD-5 (Cost-attribution 5-step chain) | RETIRED batch-32 (2026-05-28) | mech-β AC #8 green on main |
| H_T-OD-6 (Local-first OTLP ingestion) | **PARTIAL → RETIRE-READY at this batch (batch-33)** | 4-OD-B cluster landed; structural-criterion-B MET; deployment-time opt-in gates remainder |
| H_T-OD-7 (Preservation invariants 5-dimension) | STILL-BOUNDED | Library carrier only; no runtime enforcement loop |
| H_T-OD-8 (aggregate manifest + Stage 3b inversion) | RETIRED (v1 §1 authoring-only) | Authoring-close |

Post-batch-33 OD-axis bucket: 2 RETIRED + 1 RETIRE-READY + 0 PARTIAL + 4 STILL-BOUNDED + 1 (OD-8 authoring-close) = 8.

Workspace-layer cumulative post-batch-33: **37/54 RETIRED (68.5%) + 1/54 RETIRE-READY (1.9%) + 3/54 PARTIAL (5.6%) + 11/54 STILL-BOUNDED (20.4%) + 2/54 STILL-BOUNDED-INDEFINITELY (3.7%)**. Pipeline-advanced (R+RR+P): 41/54 = 75.9% (preserved across PARTIAL → RETIRE-READY within-tier transit per X-AL-2).

## §2 Adjacent observations

(a) **First post-batch-32 RETIRE-READY repopulation.** Batch-32 cleared the RETIRE-READY bucket to EMPTY for the first time in ledger history; batch-33 re-populates at +1 (OD-6 NEW). Calendar-day flip; expected dynamic.

(b) **OD-axis sub-row transit asymmetry vs AS/CP axes.** OD-6 RETIRE-READY transit at batch-33 follows the same shape as OD-5 batch-28 (structural-criterion-B MET + deployment-time-opt-in-gate identified as terminal in-CLI state); the OD-axis now carries TWO members of sub-species 7.deployment-time-opt-in-gate across its lifetime (OD-5 batch-28→32; OD-6 batch-33→future). Pattern consolidating as canonical for OD-axis retirements where production-binding-chain requires operator orchestration of the cadence trigger.

(c) **No CXA cascade.** PR #18 ZERO cross-axis cascade verified at PR description; OD spec v1.25 doc closures preserve §C-OD-27 contract semantics; no edge change at CXA v2.15.

(d) **Workspace `CLAUDE.md` §2.3 + §2.4 row bumps to v1.25 + v2.24 deferred** per PR #18 carry. Sibling-cite cascade at workspace index not blocking; bookkeeping owed at follow-on arc.

(e) **Plan + spec doc closures co-published.** OD plan v2.24 §1.1..§1.5 (canonical-reading amendments at U-OD-42 + U-OD-43 + U-OD-44 columns/pragmas/file-path/config/signature) + OD spec v1.25 §1.1..§1.3 (phantom-`U-RT-30`-cite refresh at v1.8 body line 10 + 169 + 199) are operative canonical readings going forward.

## §3 Filing footer

| Field | Value |
|---|---|
| Authored at | 2026-05-28 (this commit) |
| Authoring authority | `phase-7-substitution-retirement` skill §3.2 verification-shape steps 1–5 |
| Predecessor | `phase-7d-retirement-events-batch-32.md` |
| Successor | `phase-7d-retirement-events-batch-34.md` (this same arc — H_T-OD-3 STILL-BOUNDED → PARTIAL transit via PR #19 merge `b39dc50`) |
