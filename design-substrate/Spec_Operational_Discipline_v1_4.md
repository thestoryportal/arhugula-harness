# Specification — Operational Discipline v1.4

## Status block

| Field | Value |
|---|---|
| Artifact | `Spec_Operational_Discipline_v1_4.md` |
| Status | **Proposed** — Phase 7 sub-phase 7b in-CLI revision pass (FF-2 resolution) |
| Revision | v1 → v1.1 → v1.2 → v1.3 (F2-12 cascade Step 5b) → **v1.4 (FF-2 collector-placement enum formalization, 2026-05-16)** |
| Revision date | 2026-05-16 (v1.4 revision pass) |
| Phase | 7 — sub-phase 7b OD axis-stream execution; in-CLI spec revision per `CLAUDE.md` §4.3 (design-phase back-flow deprecated 2026-05-15 — spec fixes applied in-CLI, tracked in `.harness/` tension records) |
| Predecessor | `Spec_Operational_Discipline_v1_3.md` (F2-12 cascade Step 5b — §14 amendments) |
| Entry authorization | Operator ratification 2026-05-16 of the FF-2 resolution (Option A — spec fix + plan conform); `.harness/class_1_tension_u_od_28_collector_placement_ff2.md` |
| Exit gate | OD plan v2.9 revision pass (U-OD-28 conform); OD-7b U-OD-28 landing |

## Change-note (v1.3 → v1.4)

**Scope of revision.** Resolves the **FF-2 carried Class 1 fork** (`Implementation_Plan_Operational_Discipline_v2_5.md` §0.6 FF-2; surfaced at OD-7b execution-time, `.harness/class_1_tension_u_od_28_collector_placement_ff2.md`). The collector-placement enum was a three-way mismatch: C-OD-01 §1.2 committed a **6-value** architectural-class enum sourced to C-OD-20; C-OD-20 §20.1 was an **8-row prose matrix with no enum declaration**; and §20.1's cell-2 / cell-4 prose described a placement ("the cell-committed single-node backend's own OTLP collector endpoint") with no home in §1.2's six values. v1.4 formalizes the enum:

| Site | Amendment shape |
|---|---|
| §1.2 Per-cell entry schema — Collector placement row | The 6-value enum grows to **7** — `self-hosted-backend-collector` added, naming the cell-2 / cell-4 self-hosted-backend OTLP-endpoint placement §20.1's prose already commits (ADR-D6 v1.1 §1.7-derived). The value space is otherwise unchanged. |
| §20.1 Per-cell collector placement matrix | An explicit `CollectorPlacement` **7-value enum** is declared (the §1.2 value space, byte-aligned). The 8-row per-cell matrix is restated as a `Cell → Set<CollectorPlacement>` mapping — singleton for the six committed cells, 2-element for the three alt-route cells (cell-2, cell-4, cell-7) whose §20.1 prose commits a design-time disjunction. The existing §20.1 prose rows are preserved as the deployment-detail backing column. |

**This is a formalization, not a new design commitment.** Every placement value names a placement §20.1's prose (transcribed from ADR-D6 v1.1 §1.7 per the §20 "ADR commitments honored" row) already describes. `self-hosted-backend-collector` names cell-2's "cell-committed single-node backend's collector preferred" and cell-4's "Langfuse self-hosted single-node OTLP endpoint". The §20.1 prose "collector-as-DaemonSet" (cell-5) is folded into `sidecar` — DaemonSet is a Kubernetes deployment-form of a sidecar-class collector; the enum names the architectural class, not the deployment-form. No ADR commitment is altered; no placement is added that §20.1's prose did not already commit.

**Status posture.** `Status: Proposed` per workspace discipline. v1.4 enters the OD plan v2.9 revision pass (U-OD-28 conform) as substrate.

**Sections preserved verbatim from v1.3.** All of the Change-note (v1.2 → v1.3), Front-matter, §1 C-OD-01 **except §1.2's Collector-placement row**, §2 C-OD-02 through §13, §14 C-OD-14 (all v1.3 amendments), §15 through §19, §20 C-OD-20 **except §20.1**, §21 through §23, §[carry-forwards], §[traceability], §[coherence pass]. Only the §1.2 Collector-placement row and §20.1 are revised at v1.4.

---

## §1 C-OD-01 — 9-cell deployment-surface × persona-tier matrix

[§1.1 + §1.3 preserved verbatim from v1.3 (→ v1.2). §1.2 revised at v1.4 — Collector-placement row only.]

### §1.2 Per-cell entry schema (v1.4 amendment — Collector-placement row)

Each active cell carries a six-field entry. [Backend class / Provider candidates / Trace storage tier / Redaction class / Retention class rows preserved verbatim from v1.2.] The **Collector placement** row is revised at v1.4:

| Field | Value space | Bound by |
|---|---|---|
| **Collector placement** | enum ∈ `{in-process, self-hosted-backend-collector, sidecar, vendor-pipeline, sidecar with per-tenant routing, per-tenant collector instance, vendor-managed collector}` — **7 values (v1.4: `self-hosted-backend-collector` added)**. The canonical enum declaration is at §20.1. | C-OD-20 §20.1 + ADR-F4 v1.1 §Consequences (b)(iv) |

*(v1.4 note: the value space grows from 6 → 7. `self-hosted-backend-collector` names the cell-committed self-hosted single-node backend's own OTLP collector endpoint — the placement §20.1's cell-2 and cell-4 prose commits. The §20.1 enum declaration is canonical; this §1.2 row references it.)*

---

## §20 C-OD-20 — Per-cell OTLP collector placement + F4 process-tier reachability

[§20.2 + §20.3 + §20.4 preserved verbatim from v1.3 (→ v1.2). §20.1 revised at v1.4 — explicit enum declaration + per-cell set mapping added; the v1.2 prose matrix preserved as the deployment-detail backing column.]

### §20.1 Per-cell collector placement matrix (v1.4 amendment — enum declaration + set-valued per-cell mapping)

**`CollectorPlacement` enum (v1.4 — canonical declaration).** Seven architectural placement classes; the §1.2 per-cell-entry-schema Collector-placement field draws from this set:

| Value | Meaning |
|---|---|
| `in-process` | In-process otelcol-contrib collector reached via localhost socket; co-resident with the harness process. |
| `self-hosted-backend-collector` | The cell-committed self-hosted single-node observability backend's own OTLP collector endpoint (e.g. Langfuse self-hosted single-node OTLP endpoint, Arize Phoenix OSS OTLP endpoint, Helicone HTTP-proxy). |
| `sidecar` | A co-located sidecar-class collector — collector-as-sidecar at non-Kubernetes deployments, collector-as-DaemonSet at Kubernetes-resident deployments (DaemonSet is a Kubernetes deployment-form of the sidecar architectural class). |
| `vendor-pipeline` | A vendor-managed ingestion pipeline reached via vendor SDK or vendor agent (Langfuse Cloud SDK, Datadog Agent, Sentry SDK, Arize SaaS SDK, collector-as-Lambda). |
| `sidecar with per-tenant routing` | A sidecar-class collector configured with per-tenant routing — per-tenant resource attributes and per-tenant rate limits at the collector boundary. |
| `per-tenant collector instance` | A distinct collector instance per tenant — full per-tenant collector-process isolation. |
| `vendor-managed collector` | A vendor-managed collector at the vendor-managed multi-tenant runtime (AWS Bedrock AgentCore, Google Vertex Agent Engine, LangSmith Enterprise SDK). |

**Per-cell placement mapping (v1.4 — `Cell → Set<CollectorPlacement>`).** Each ACTIVE cell commits a **non-empty set** of placement classes — a singleton for the six committed cells, a 2-element set for the three cells (cell-2, cell-4, cell-7) whose placement is a design-time disjunction (an alt-route, per the prose backing column):

| Cell | Collector placement (`Set<CollectorPlacement>`) | Deployment-detail backing (prose; preserved verbatim from v1.2 §20.1) | Backing |
|---|---|---|---|
| solo-developer × local-development (cell-1) | `{in-process}` | In-process otelcol-contrib + BatchSpanProcessor; sqlite ring-buffer; TUI trace browser | C-OD-19 |
| solo-developer × self-hosted-server (cell-2) | `{in-process, self-hosted-backend-collector}` | In-process collector permitted as alt-route; cell-committed single-node backend's collector preferred (Langfuse self-hosted single-node OTLP endpoint / Arize Phoenix OSS OTLP endpoint / Helicone HTTP-proxy) | C-OD-02 §2.2 cell-2 candidates |
| solo-developer × managed-cloud (cell-3) | `{vendor-pipeline}` | Vendor-pipeline (Langfuse Cloud SDK / Datadog Agent / Sentry SDK / Arize SaaS SDK) | C-OD-02 §2.2 cell-3 candidates |
| team-binding × local-development (cell-4) | `{in-process, self-hosted-backend-collector}` | In-process collector + sqlite ring-buffer for short-window traces, OR Langfuse self-hosted single-node OTLP endpoint at the shared instance | C-OD-02 §2.2 cell-4 candidates |
| team-binding × self-hosted-server (cell-5) | `{sidecar}` | Sidecar OR collector-as-DaemonSet at K8s-resident deployments (humanlayer/agentcontrolplane class per ADR-D1 §1.2 row 4); collector-as-sidecar at non-K8s deployments | C-OD-02 §2.2 cell-5 candidates |
| team-binding × managed-cloud (cell-6) | `{vendor-pipeline}` | Vendor-pipeline (collector-as-Lambda OR vendor SDK); per-vendor OTel ingestion path | C-OD-02 §2.2 cell-6 candidates |
| multi-tenant-compliance × self-hosted-server (cell-7) | `{sidecar with per-tenant routing, per-tenant collector instance}` | Sidecar with per-tenant routing OR per-tenant collector instance; collector configuration is per-tenant-isolation-aware (per-tenant resource attributes; per-tenant rate limits at collector boundary) | C-OD-21 + C-OD-02 §2.2 cell-7 candidates |
| multi-tenant-compliance × managed-cloud (cell-8) | `{vendor-managed collector}` | Vendor-managed collector (BedrockAgent / Vertex Agent Engine / LangSmith Enterprise SDK); pre-collector redaction at SDK / wrapper boundary applies per C-OD-13 §13.2 | C-OD-02 §2.2 cell-8 candidates |

**Invariants.** (i) Each ACTIVE cell's placement set is non-empty. (ii) Cells 2, 4, 7 carry a 2-element set (a design-time alt-route disjunction — the operator selects one alternant at deployment-binding time); the other five cells carry a singleton. (iii) The enum value `in-process` composes with C-OD-19 per §20.4 — at cell-1 in-process is committed, at cell-2 and cell-4 in-process is the alt-route. (iv) cell-5's `sidecar` value covers both the collector-as-sidecar (non-K8s) and collector-as-DaemonSet (K8s) deployment-forms — DaemonSet is not a distinct architectural class. (v) cell-7's two values are both per-tenant-isolation-aware placements; selection between them is per-tenant-routing-granularity at deployment-binding time.

---

## Filing footer

| Field | Value |
|---|---|
| Artifact | `Spec_Operational_Discipline_v1_4.md` |
| Status | Proposed — Phase 7 7b in-CLI FF-2 resolution |
| Predecessor | `Spec_Operational_Discipline_v1_3.md` (F2-12 cascade Step 5b) |
| Substrate consumed | `.harness/class_1_tension_u_od_28_collector_placement_ff2.md` (FF-2 tension record); ADR-D6 v1.1 §1.7 (per-cell collector placement table — §20.1 source); ADR-F4 v1.1 §Consequences (b)(iv) |
| Successor | `Implementation_Plan_Operational_Discipline_v2_9.md` (U-OD-28 conform revision pass) |
| Revision policy | In-CLI per workspace discipline (`CLAUDE.md` §4.3) |
| Date | 2026-05-16 |

*Filed at OD-7b execution-time as the FF-2 resolution. C-OD-01 §1.2 Collector-placement enum grown 6 → 7 (`self-hosted-backend-collector` added); C-OD-20 §20.1 given an explicit 7-value `CollectorPlacement` enum declaration + a `Cell → Set<CollectorPlacement>` per-cell mapping (set-valued at the three alt-route cells 2/4/7). Formalization of §20.1's existing ADR-D6 §1.7-derived prose; no ADR commitment altered. Successor: OD plan v2.9 U-OD-28 conform.*
