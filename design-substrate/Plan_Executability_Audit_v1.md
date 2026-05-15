# Plan Executability Audit (v1)

*Phase 6.5 Session 2 (α) primary deliverable. Per-unit signature audit of v2.3 implementation plans (IS v2.1, AS v1, CP v2.3, OD v2.3, CXA v2.1) against the Python 3.12+ stack committed at `Target_Stack_Commitment_v1.md`.*

---

## §1 Status block

| Field | Value |
|---|---|
| Artifact | `Plan_Executability_Audit_v1.md` |
| Status | **Filed** — Session 2 (α) primary deliverable |
| Date | 2026-05-15 |
| Phase | Phase 6.5 (pre-transition arc) Session 2 (α — Pre-flight Executability Audit) |
| Authority | Operator directive 2026-05-14 (Phase 6.5 arc entry); `Phase_6_5_Session_2_Kickoff.md` |
| Predecessor | `Target_Stack_Commitment_v1.md` (Session 1 δ deliverable); v2.3 implementation plans + CXA v2.1 |
| Audit scope | 139 atomic units across 4 axes + 101 cross-axis edges + 40-cell bridging-arc verification + 15-namespace Pattern P1 verification |
| Successor | `Phase_6_5_Session_2_Close_Handoff.md`; `Phase_6_5_Session_3_Kickoff.md` |
| Filing destination | `/mnt/user-data/outputs/Plan_Executability_Audit_v1.md` → operator pushes to `/mnt/project/` |

---

## §2 Audit methodology

### §2.1 Per-unit signature audit

For each atomic unit in each implementation plan:

1.1.1 Read the unit's signature (function name, inputs, outputs, side effects, contracts touched).

1.1.2 Identify the Python primitives / libraries required to materialize the signature against `Target_Stack_Commitment_v1.md` §5.2.

1.1.3 Verify primitives are reachable from the committed stack (Python 3.12+ + uv + pyright + ruff + pytest + Pydantic v2 + `opentelemetry-{api,sdk,exporter-otlp}` + selective `opentelemetry-instrumentation-genai` + `python-keyring` + stdlib `sqlite3` + per-provider SDKs + `modelcontextprotocol/python-sdk` FastMCP).

1.1.4 Tag executability: **CLEAR** / **GUARDRAIL** / **FORK** per §2.3.

### §2.2 Cross-axis composition audit

For the CXA composition document v2.1:

1.2.1 Walk the axis-granularity topological sort (IS < AS < CP < OD).

1.2.2 Re-verify the 4×4 adjacency matrix (101 edges across 6 non-empty buckets).

1.2.3 Re-verify acyclicity at both axis granularity and within-axis at each plan.

1.2.4 Re-verify 40 bridging-arc transition cells (5 PERSONA_TIER_ASCENT + 3 DEPLOYMENT_SURFACE_ASCENT × 5 axes).

1.2.5 Re-verify Pattern P1 byte-exact alignment across 15 namespaces (producer-side declarers vs consumer-side ingestion).

1.2.6 Verify cost-attribution 5-step OD chain composes against substrate.

### §2.3 Feasibility tag taxonomy

| Tag | Definition |
|---|---|
| **CLEAR** | Unit signature materializes against committed stack with no deferred binding decision required at Phase 7 implementation entry |
| **GUARDRAIL** | Unit signature materializes but requires a documented binding decision routing to Session 6 (ε — Claude Code CLI bootstrap substrate) governance OR a single Session 3 (ζ) revision-pass absorption |
| **FORK** | Unit signature requires Class 1 (halt-arc) or Class 2 (operator-decision-blocking) revision; no FORK surfaced at this audit |

---

## §3 Per-axis audit findings

### §3.1 IS axis (17 units; 11 CLEAR / 6 GUARDRAIL / 0 FORK)

Substrate: `Implementation_Plan_Information_Substrate_v2_1.md`.

| Cluster | Units | CLEAR | GUARDRAIL | Notes |
|---|---|---|---|---|
| 1 — Foundational schemas (C-IS-01 + C-IS-02) | U-IS-01, U-IS-02, U-IS-03 | 3 | 0 | Pydantic v2 declarative |
| 2 — Git-tier + atomic deploy (C-IS-03 + C-IS-04) | U-IS-04, U-IS-05, U-IS-06 | 2 | 1 | U-IS-06: git library binding |
| 3 — Entry shape + hash-chain (C-IS-05 + C-IS-06) | U-IS-07, U-IS-08, U-IS-09, U-IS-10 | 3 | 1 | U-IS-08: JCS canonicalization |
| 4 — Read/write contract pair (C-IS-07) | U-IS-11, U-IS-12 | 1 | 1 | U-IS-11: cross-platform file-lock |
| 5 — Workload-class opt-in (C-IS-08 + C-IS-09) | U-IS-13, U-IS-14, U-IS-15, U-IS-16 | 1 | 3 | U-IS-14/15/16: git library binding |
| 6 — Substrate seam exports (C-IS-10) | U-IS-17 | 1 | 0 | Terminal aggregate exporter |

**GUARDRAIL inventory:**

| Unit | Concern | Recommendation |
|---|---|---|
| U-IS-06 | Git library binding | subprocess→git CLI (stdlib + zero new dep cost; git binary universally present) [HIGH] |
| U-IS-08 | JCS canonicalization library | `rfc8785` PyPI [HIGH on availability] or in-tree authoring [MODERATE] |
| U-IS-11 | Cross-platform file-lock | `filelock` PyPI [HIGH — mature, single-purpose, cross-platform fcntl + Windows binding] |
| U-IS-14, U-IS-15, U-IS-16 | Git library binding | Inherits U-IS-06 decision (subprocess→git CLI) |

**F3-02 acknowledged-deferred.** IS plan v2.1 lacks the canonical IS-axis ledger-write site unit cited at OD plan v2.3 U-OD-20 acceptance #11 (`U-IS-NN` placeholder). Routes to Session 3 (ζ) per §5.4.

### §3.2 AS axis (33 units; 29 CLEAR / 4 GUARDRAIL / 0 FORK)

Substrate: `Implementation_Plan_Action_Surface_v1.md`. 16 contracts; 9 topological levels (L0–L8).

| Cluster group | Unit range | CLEAR | GUARDRAIL | Notes |
|---|---|---|---|---|
| Sandbox substrate | U-AS-01 — U-AS-08 | 8 | 0 | OS process isolation primitives; subprocess + resource limits |
| MCP trust | U-AS-09 — U-AS-15 | 7 | 0 | FastMCP host + client; trust-tier taxonomy declarative |
| OTel emission | U-AS-16 — U-AS-18 | 1 | 2 | U-AS-17, U-AS-18: custom OTel SpanProcessor + Sampler |
| Tool surface | U-AS-19 — U-AS-22 | 3 | 1 | U-AS-20: TIER_3 / TIER_4 in-sandbox HTTP bootstrap server |
| Canonicalization | U-AS-23 — U-AS-26 | 3 | 1 | U-AS-25: JCS carry-forward from U-IS-08 |
| Model catalog | U-AS-27 — U-AS-30 | 4 | 0 | Anthropic + OpenAI + Ollama SDK reflection |
| Terminal exports | U-AS-31, U-AS-32, U-AS-33 | 3 | 0 | Substrate seam aggregate exporter |

**GUARDRAIL inventory:**

| Unit | Concern | Recommendation |
|---|---|---|
| U-AS-17 | Custom OTel SpanProcessor for SENSITIVE_DATA_EXCLUSIONS | Project-authored against `opentelemetry.sdk.trace.SpanProcessor` ABC [HIGH] |
| U-AS-18 | Always-sampled-with-tail-keep Sampler authoring | Project-authored against `opentelemetry.sdk.trace.sampling.Sampler` ABC [HIGH] |
| U-AS-20 | TIER_3 / TIER_4 in-sandbox HTTP bootstrap server | Project-authored; `http.server` stdlib candidate; route to Session 6 |
| U-AS-25 | JCS carry-forward from U-IS-08 | Inherits U-IS-08 binding decision |

**C7 consultation outcome.** `opentelemetry-instrumentation-genai` adoption limited to LLM-call spans against anthropic + openai providers; project-authored emission for ollama + all 11 specialization namespaces.

### §3.3 CP axis (55 units; 51 CLEAR / 4 GUARDRAIL / 0 FORK)

Substrate: `Implementation_Plan_Control_Plane_v2_3.md`. 24 contracts; 9 clusters; 9 topological levels (L0–L8); 184 total edges (124 within-axis + 36→IS + 24→AS).

| Cluster | Units | CLEAR | GUARDRAIL | Notes |
|---|---|---|---|---|
| 1 — F1 routing + fallback | U-CP-01 — U-CP-09 | 8 | 1 | U-CP-05: EMBEDDING layer model binding |
| 2 — F3 lifecycle + manifest | U-CP-10 — U-CP-13 | 4 | 0 | v2.3 F2-02 + F2-03 absorption at U-CP-12 |
| 3 — D1 engine + replay | U-CP-14 — U-CP-21 | 8 | 0 | F2-12 ✅ CLOSED at v2.2; preserved at v2.3 |
| 4 — D4 topology + sub-agent | U-CP-22 — U-CP-27 | 6 | 0 | RC-1 reconciliation preserved |
| 5 — D4 handoff + spans + audit | U-CP-28 — U-CP-36 | 9 | 0 | RC-2 reconciliation preserved; U-CP-33 asyncio coordination CLEAR |
| 6 — D5 HITL palette + placement + matrix | U-CP-37 — U-CP-41 | 5 | 0 | Pure Pydantic v2 dispatch |
| 7 — D5 multiplicative gate + audit crypto | U-CP-42 — U-CP-46 | 3 | 2 | U-CP-44, U-CP-45: signature algorithm + key rotation |
| 8 — D5 escalation + revalidation | U-CP-47 — U-CP-52 | 5 | 1 | U-CP-52: async HTTP client for webhook delivery |
| 9 — T-perm-3 + exports | U-CP-53 — U-CP-55 | 3 | 0 | Terminal aggregate exporters |

**GUARDRAIL inventory:**

| Unit | Concern | Recommendation |
|---|---|---|
| U-CP-05 | EMBEDDING layer model binding (sentence-transformers vs Voyage vs no-op fall-through) | Defer to no-op fall-through at v1.0; preserve 3-layer interface for future expansion [HIGH] |
| U-CP-44 | Ed25519 vs ECDSA-P256 signature algorithm | Multi-tenant out-of-scope at design-time; `cryptography` library supports both via `hazmat.primitives.asymmetric` [HIGH] |
| U-CP-45 | Key-rotation cryptographic primitives | Inherits U-CP-44 algorithm binding decision; multi-tenant out-of-scope |
| U-CP-52 | Async HTTP client for webhook delivery | `httpx` (async + sync API parity, widely adopted) [HIGH]; routes to Session 6 (ε) per OD-S2-2.A |

**GateLevel cardinality note.** AS-side `GateLevel` 3-valued (AUTO / ASK / DENY at U-AS-14); CP-side audit-policy `GateLevel` 4-valued (adds REVIEW_BOARD for TIER_4_UNTRUSTED at U-CP-43 §19.1). Non-conflicting across substrate.

### §3.4 OD axis (34 units; 29 CLEAR / 5 GUARDRAIL / 0 FORK)

Substrate: `Implementation_Plan_Operational_Discipline_v2_3.md`. 23 contracts; 8 clusters; 28 outbound cross-axis edges (6→IS + 10→AS + 12→CP).

| Cluster | Units | CLEAR | GUARDRAIL | Notes |
|---|---|---|---|---|
| OD-CL-1 — Deferral envelope | U-OD-01 — U-OD-03 | 3 | 0 | Declarative |
| OD-CL-2 — OTel base + specialization ingestion | U-OD-04 — U-OD-08 | 5 | 0 | OTel SDK base layer |
| OD-CL-3 — Sampling | U-OD-09 — U-OD-12 | 2 | 2 | U-OD-11 Composite Sampler; U-OD-12 tail-keep |
| OD-CL-4 — Redaction | U-OD-13 — U-OD-16 | 3 | 1 | U-OD-16 pre-Collector SpanProcessor |
| OD-CL-5 — Cost attribution | U-OD-17 — U-OD-22 | 5 | 1 | U-OD-20 F3-02 carry-forward to Session 3 (ζ) |
| OD-CL-6 — Ingestion | U-OD-23 — U-OD-27 | 4 | 1 | U-OD-27 local-first OTLP composition |
| OD-CL-7 — Preservation invariants | U-OD-28 — U-OD-33 | 6 | 0 | 5-dimension preservation composition |
| OD-CL-8 — Aggregate manifest | U-OD-34 | 1 | 0 | Terminal aggregate exporter |

**GUARDRAIL inventory:**

| Unit | Concern | Recommendation |
|---|---|---|
| U-OD-11 | Composite Sampler authoring | Project-authored against `opentelemetry.sdk.trace.sampling.Sampler` ABC; routes to Session 6 |
| U-OD-12 | Tail-keep at tail-based-prod cells | OTel Collector `tail_sampling` processor (deployment-tier substrate); cell-1 local-first uses head-only sampling per ADR-D6 v1.2 |
| U-OD-16 | Pre-Collector redaction SpanProcessor | Project-authored against `SpanProcessor` ABC; multi-tenant out-of-scope at design-time |
| U-OD-20 | F3-02 acknowledged-deferred (canonical IS-axis ledger-write site absent) | **Routes to Session 3 (ζ) IS-axis revision pass** — NOT Session 6 |
| U-OD-27 | Local-first OTLP composition pattern | In-process OTLP ingestion + stdlib sqlite3 ring-buffer + Textual TUI; project-authored composition |

### §3.5 CXA cross-axis composition (101 edges; 40/40 bridging-arc; 15/15 Pattern P1)

Substrate: `Cross_Axis_Composition_Document_v2_1.md`.

#### §3.5.1 Adjacency matrix re-verification

| Source ↓ / Target → | IS | AS | CP | OD |
|---|---|---|---|---|
| **IS** | *(self)* | 0 | 0 | 0 |
| **AS** | **13** | *(self)* | 0 | 0 |
| **CP** | **36** | **24** | *(self)* | 0 |
| **OD** | **6** | **10** | **12** | *(self)* |

Aggregate: **101 cross-axis edges across 6 non-empty buckets**. Audit re-counts match CXA v2.1 declaration. ✅

#### §3.5.2 Acyclicity verification

Axis-level topological order: **IS < AS < CP < OD** (acyclic). Within-axis acyclicity verified at each plan (§3 of each plan): IS plan v2.1 6 levels, AS plan v1 9 levels (L0–L8), CP plan v2.3 9 levels (L0–L8), OD plan v2.3 ACYCLIC. ✅

#### §3.5.3 Bridging-arc transition audit

40 cells (8 transitions × 5 axes) declared PASS at CXA v2.1 §4.3.3. Re-confirmed at audit: T-perm-1 5-axis multiplicative tunable composition is monotonic-tightening across all 8 transitions; strict ascent on GATE_POLICY + SANDBOX_TIER at 3 deployment-surface ascent transitions; 6 T-perm-1 closure-shape properties hold. ✅

#### §3.5.4 Pattern P1 byte-exact alignment

15 namespaces verified byte-exact between producer-side (U-AS-31, U-AS-16, U-CP-21, U-CP-31, U-CP-46, U-CP-47, U-OD-09) and consumer-side (U-OD-06, U-OD-07, U-OD-08, U-OD-20, U-CP-54): `anthropic.*` (10 attrs), `mcp.*` (7), `skill.*` (6), `managed_agents.*` (3), `sandbox.*` (7), `files.*` (8), `memory.*` (6), `hitl.*` (4), `topology.*` (10), `subagent.*` (7), `engine.*` (4), `audit.*` (7), `validator.fail.*` (3), `harness.breaker.*` (7), `retry.*` (6 child span + 3-field parent event). ✅

#### §3.5.5 Cost-attribution cross-axis composition

5-step OD chain (U-OD-18 → U-OD-19 → U-OD-20 → U-OD-21 → U-OD-22) consumes 1 IS edge + 1 AS edge + 2 CP edges. F2-12 ✅ CLOSED at v2.2 cascade (preserved at v2.3). COHERENT.

---

## §4 Aggregate audit findings

### §4.1 Per-axis verdict roll-up

```
Axis  | Units | CLEAR | GUARDRAIL | FORK | Class 1 | Class 2 | Class 3
──────┼───────┼───────┼───────────┼──────┼─────────┼─────────┼────────
IS    |   17  |   11  |     6     |   0  |    0    |    0    |   4
AS    |   33  |   29  |     4     |   0  |    0    |    0    |   3
CP    |   55  |   51  |     4     |   0  |    0    |    0    |   4
OD    |   34  |   29  |     5     |   0  |    0    |    0    |   4 (incl. F3-02)
──────┼───────┼───────┼───────────┼──────┼─────────┼─────────┼────────
Total |  139  |  120  |    19     |   0  |    0    |    0    |  15 + 1 informational
```

### §4.2 Cross-axis pattern findings

Three structural patterns surface across the per-axis traversal:

4.2.1 **JCS canonicalization concentration.** Single carry-forward (U-IS-08) propagates to 11 downstream units across AS + CP + OD. Single binding decision unblocks ~8% of total unit count.

4.2.2 **OTel SpanProcessor / Sampler authoring concentration.** Four units (U-AS-17, U-AS-18, U-OD-11, U-OD-16) author custom OTel SDK components. All four CLEAR by feasibility (OTel SDK admits `SpanProcessor` + `Sampler` subclassing); routing to Session 6 governance for canonical authoring discipline. Composition pattern: AS + CP emit attributes → OD-authored Processor/Sampler dispatch.

4.2.3 **Git CLI binding consolidation.** Four IS units (U-IS-06, U-IS-14, U-IS-15, U-IS-16) require git library binding. Single Session 6 binding decision resolves all four. Audit recommendation: subprocess→git CLI [HIGH].

### §4.3 Guardrail concentration analysis

| Concentration site | GUARDRAIL count | Disposition target |
|---|---|---|
| JCS canonicalization (U-IS-08 + propagators) | 1 source + 11 propagators | Session 6 |
| Git CLI binding | 4 units (U-IS-06, U-IS-14/15/16) | Session 6 |
| File-lock | 1 unit (U-IS-11) | Session 6 |
| OTel SpanProcessor / Sampler authoring | 4 units (U-AS-17, U-AS-18, U-OD-11, U-OD-16) | Session 6 |
| HTTP client (httpx) | 2 units (U-AS-20, U-CP-52) | Session 6 (per OD-S2-2.A) |
| Crypto algorithm | 2 units (U-CP-44, U-CP-45) | Session 6 (multi-tenant out-of-scope) |
| EMBEDDING layer | 1 unit (U-CP-05) | Session 6 (defer to no-op fall-through) |
| F3-02 IS-axis revision | 1 unit (U-OD-20) | **Session 3 (ζ)** |
| Local-first OTLP composition | 1 unit (U-OD-27) | Session 6 |
| Tail-keep (Collector) | 1 unit (U-OD-12) | Session 6 |

Eleven Session 6 binding-decision surfaces; one Session 3 (ζ) carry-forward.

---

## §5 Class 1 / 2 / 3 fork inventory

### §5.1 Class 1 forks: 0

No Phase 6 commitment invalidated; no cascade-substrate-clearance invalidation; no Phase 7 entry authorization invalidation.

### §5.2 Class 2 forks: 0

No design-phase artifact defect requires operator decision before Phase 6.5 progression.

### §5.3 Class 3 inventory (16 items)

| # | Unit(s) | Concern | Routing |
|---|---|---|---|
| C3-01 | U-IS-06, U-IS-14/15/16 | Git library binding | Session 6 (ε) |
| C3-02 | U-IS-08 + 11 propagators | JCS canonicalization library | Session 6 (ε) |
| C3-03 | U-IS-11 | Cross-platform file-lock library | Session 6 (ε) |
| C3-04 | U-AS-17 | Custom OTel SpanProcessor authoring | Session 6 (ε) |
| C3-05 | U-AS-18 | Always-sampled-with-tail-keep Sampler authoring | Session 6 (ε) |
| C3-06 | U-AS-20 | TIER_3/TIER_4 in-sandbox HTTP bootstrap server | Session 6 (ε) |
| C3-07 | U-CP-05 | EMBEDDING layer model binding | Session 6 (ε) |
| C3-08 | U-CP-44, U-CP-45 | Signature algorithm (Ed25519 vs ECDSA-P256) | Session 6 (ε) |
| C3-09 | U-CP-52 + U-AS-20 | httpx async HTTP client binding | Session 6 (ε) per OD-S2-2.A |
| C3-10 | U-OD-11 | Composite Sampler authoring | Session 6 (ε) |
| C3-11 | U-OD-12 | Tail-based-prod cell composition (OTel Collector tail_sampling) | Session 6 (ε) |
| C3-12 | U-OD-16 | Pre-Collector redaction SpanProcessor | Session 6 (ε) |
| C3-13 | U-OD-27 | Local-first OTLP composition pattern | Session 6 (ε) |
| C3-14 | U-OD-20 | F3-02 (canonical IS-axis ledger-write site absent) | **Session 3 (ζ)** |
| C3-15 | OD plan §4.5.1 | Non-existent IS spec contract citations (C-IS-13, C-IS-14, C-IS-08 §8.4) | **Session 3 (ζ) per OD-S2-1.A — broadened scope** |
| C3-16 | (subsumed) | httpx Stack §5.2 amendment | Subsumed by C3-09 per OD-S2-2.A |

### §5.4 Disposition routing summary

```
13 items → Session 6 (ε — Claude Code CLI bootstrap substrate)
 2 items → Session 3 (ζ — IS-axis revision pass; broadened per OD-S2-1.A)
 1 item  → subsumed (C3-16 by C3-09 per OD-S2-2.A)
─────────
16 total
```

---

## §6 Monorepo subdivision refinement

### §6.1 Committed shape preserved

`harness-{is,as,cp,od,cxa}/ + harness-core/` shape per `Target_Stack_Commitment_v1.md` §5.2 item 6 preserved at audit. No subdivision revision required.

### §6.2 Per-cluster subpackage assignment

```
Repository root
├── harness-core/           ← shared primitives (see §6.3 inventory)
├── harness-is/             ← 17 units across 6 clusters
│   ├── path_registry/        U-IS-01, U-IS-02
│   ├── artifact_tier/        U-IS-03
│   ├── git_tier/             U-IS-04, U-IS-05, U-IS-06    [GUARDRAIL: git CLI]
│   ├── ledger/               U-IS-07, U-IS-08, U-IS-09, U-IS-10    [GUARDRAIL: JCS]
│   ├── rw_contract/          U-IS-11, U-IS-12             [GUARDRAIL: filelock]
│   ├── workload_opt_in/      U-IS-13, U-IS-14, U-IS-15, U-IS-16    [GUARDRAIL: git CLI]
│   └── exports/              U-IS-17
├── harness-as/             ← 33 units
│   ├── sandbox_substrate/    U-AS-01 — U-AS-08
│   ├── mcp_trust/            U-AS-09 — U-AS-15
│   ├── otel_emission/        U-AS-16 — U-AS-18            [GUARDRAIL: Processor + Sampler]
│   ├── tool_surface/         U-AS-19 — U-AS-22            [GUARDRAIL: U-AS-20 HTTP bootstrap]
│   ├── canonicalization/     U-AS-23 — U-AS-26            [GUARDRAIL: JCS propagation]
│   ├── model_catalog/        U-AS-27 — U-AS-30
│   └── exports/              U-AS-31, U-AS-32, U-AS-33
├── harness-cp/             ← 55 units across 9 clusters
│   ├── routing/              U-CP-01 — U-CP-09            [GUARDRAIL: U-CP-05 embedding]
│   ├── lifecycle/            U-CP-10 — U-CP-13
│   ├── engine/               U-CP-14 — U-CP-21
│   ├── topology/             U-CP-22 — U-CP-27
│   ├── handoff/              U-CP-28 — U-CP-36
│   ├── hitl/                 U-CP-37 — U-CP-41
│   ├── gate_crypto/          U-CP-42 — U-CP-46            [GUARDRAIL: U-CP-44/45 algorithm]
│   ├── escalation/           U-CP-47 — U-CP-52            [GUARDRAIL: U-CP-52 HTTP client]
│   └── exports/              U-CP-53, U-CP-54, U-CP-55
├── harness-od/             ← 34 units across 8 clusters
│   ├── deferral_envelope/    U-OD-01 — U-OD-03
│   ├── otel_base/            U-OD-04 — U-OD-08
│   ├── sampling/             U-OD-09 — U-OD-12            [GUARDRAIL: Sampler authoring]
│   ├── redaction/            U-OD-13 — U-OD-16            [GUARDRAIL: pre-collector processor]
│   ├── cost_attribution/     U-OD-17 — U-OD-22            [F3-02: U-OD-20 → Session 3]
│   ├── ingestion/            U-OD-23 — U-OD-27            [GUARDRAIL: local-first OTLP]
│   ├── preservation/         U-OD-28 — U-OD-33
│   └── exports/              U-OD-34
└── harness-cxa/            ← cross-axis composition (no plan units)
    ├── bridging_arc_audit/   property-based test harness (40-cell verification)
    ├── adjacency_matrix/     101-edge cross-axis registry
    ├── pattern_p1_audit/     15-namespace byte-exact alignment registry
    └── cost_attribution/     5-step OD chain test harness
```

### §6.3 harness-core content inventory

Per-axis substrate that surfaces independently at three or more axes promotes to `harness-core`:

| Primitive | Authority | Promoted | Rationale |
|---|---|---|---|
| `PersonaTier` enum (3 values) | Persona document | **YES** | AS + CP + OD all consume |
| `DeploymentSurface` enum | ADR-F4 v1.1 | **YES** | AS + CP + OD all consume |
| `WorkloadClass` enum (4 values) | ADD §3.2 | **YES** | CP + OD consume |
| Identifier type aliases (`ActionID`, `ThreadID`, `EntryID`, `Timestamp`) | F2 substrate | **YES** | Span 4+ axes |
| Pydantic v2 base config (`strict_mode`, `frozen` records) | C-STK-08 | **YES** | Shared model configuration |
| `BlastRadiusTier` enum (4 values) | AS C-AS-01 § U-AS-01 | **NO** | AS-authoritative; CP consumes cross-axis |
| `SandboxTier` enum | AS C-AS-04 § U-AS-05 | **NO** | AS-authoritative |
| F2 state-ledger entry shape | IS C-IS-05 § U-IS-07 | **NO** | IS-authoritative; substrate flows via U-IS-17 manifest |

[HIGH] on enum promotion decisions; [MODERATE] on identifier type-alias placement.

### §6.4 uv workspace declaration

```toml
# pyproject.toml at repository root
[tool.uv.workspace]
members = [
    "harness-core",
    "harness-is",
    "harness-as",
    "harness-cp",
    "harness-od",
    "harness-cxa",
]
```

Per-member dependency declarations enforce axis-level topological ordering verified at §3.5.2: `harness-is` → `harness-core`; `harness-as` → `harness-core + harness-is`; `harness-cp` → `harness-core + harness-is + harness-as`; `harness-od` → all lower; `harness-cxa` → all lower. [HIGH]

---

## §7 Per-`instrumentation-genai` library adoption recommendation

### §7.1 Per-provider matrix

| Provider | Usage | Source | Confidence |
|---|---|---|---|
| Anthropic | Primary harness LLM per ADR-D3 v1.2 | **Project-authored** `gen_ai.*` emission against anthropic Python SDK + `anthropic.*` 10-attribute namespace per U-AS-31 + U-OD-06 | [HIGH on approach] |
| OpenAI | Cross-family fallback per U-CP-09 | **Adopt `opentelemetry-instrumentation-openai-v2`** per Stack §3.1 row A3 substrate signal | [HIGH on availability] |
| Ollama | Local-tier + LOCAL_OPEN_WEIGHT terminal fallback | **Project-authored** `gen_ai.*` emission against ollama Python SDK | [HIGH on approach] |
| Google GenAI | Not in current scope | Not adopted at v1.0; deferred | [HIGH on deferral] |

### §7.2 Project-authored emission discipline

For Anthropic + Ollama LLM calls:

1. Open OTel span with name format per U-OD-04 §4.1: `"{gen_ai.operation.name} {gen_ai.request.model}"`
2. Set base-layer `gen_ai.*` attributes per U-OD-04 §4.3 (Required + Conditional tiers)
3. Set provider-specialization attributes per U-OD-06 (anthropic.* 10 attrs)
4. Emit per-attempt `retry.*` attributes per U-CP-07 v2.3 6-attribute child span schema
5. Compose with cost-attribution per U-OD-18 → U-OD-22 5-step chain

Pure OTel SDK API; no contrib library required.

### §7.3 Adoption recommendation

| Decision | Recommendation |
|---|---|
| `opentelemetry-instrumentation-openai-v2` | **Adopt at v1.0** |
| Project-authored anthropic emission | **Required at v1.0** |
| Project-authored ollama emission | **Required at v1.0** |
| Google GenAI instrumentation | **Defer** (out of scope at v1.0) |
| Generic semconv constants module | **Adopt as base** (prevents attribute-name typos) |

---

## §8 Framework-pull risk inventory

### §8.1 Risk methodology

A unit is at framework-pull risk if its signature surface overlaps territory occupied by a mainstream Python agent-harness framework (LangGraph, LangChain, LlamaIndex, CrewAI, AutoGen, Temporal). Risk graded HIGH / MODERATE / LOW by signature overlap depth.

### §8.2 Per-unit risk inventory

| Risk | Unit cluster | Framework overlap |
|---|---|---|
| **HIGH** | U-CP-15 — U-CP-21 (D1 engine + replay) | LangGraph `StateGraph` + checkpointer; Temporal workflow + activity |
| **HIGH** | U-CP-22 — U-CP-25, U-CP-32, U-CP-33 (D4 topology + sub-agent + spans) | CrewAI `Crew` + `Agent` + `Task`; AutoGen `GroupChat`; LangGraph subgraph |
| **HIGH** | U-CP-37 — U-CP-41 (D5 HITL palette + placement + matrix) | LangGraph `interrupt()`; CrewAI human-in-the-loop callback |
| **HIGH** | U-CP-13, U-CP-14 (workflow manifest + per-step override) | LangGraph `StateGraph.compile()`; CrewAI `Crew.kickoff()` |
| **MODERATE** | U-CP-05, U-CP-09 (layered routing + cross-family fallback) | LangChain LCEL `RouterChain`; LiteLLM router |
| **MODERATE** | U-CP-27, U-CP-28, U-CP-30 (sub-agent dispatch + handoff + brief) | CrewAI `Agent.delegate()`; AutoGen agent message passing |
| **MODERATE** | U-CP-47, U-CP-48 (validator-fail + transient staircase) | LangGraph evaluator-optimizer |
| **MODERATE** | U-CP-49, U-CP-50 (pause/resume + material-diff) | LangGraph durable execution `Command(resume=...)` |
| **MODERATE** | U-IS-07 — U-IS-12 (F2 state-ledger) | LangGraph `Checkpointer` ABC; LangChain memory; LlamaIndex storage |
| **MODERATE** | U-AS-19 — U-AS-22 (tool surface + MCP server) | LangChain `Tool` abstraction; OpenAI tools SDK |
| **LOW** | All OTel emission units (U-OD-04 — U-OD-12) | OTel SDK is the substrate; not a framework |
| **LOW** | All cryptographic units (U-IS-08, U-CP-42, U-CP-44, U-CP-45) | `cryptography` library is a primitive |
| **LOW** | All sandbox primitives (U-AS-04 — U-AS-08) | OS process isolation primitives |
| **LOW** | All pure-schema units | Pydantic is the primitive |
| **LOW** | All terminal exporters (U-IS-17, U-AS-33, U-CP-54+55, U-OD-34) | No framework occupies "substrate seam exports" territory |

### §8.3 Risk concentration

```
HIGH risk units:      ~25 units      (18% of total; concentrated at CP D1 + D4 + D5)
MODERATE risk units:  ~20 units      (14% of total; spread across CP routing/handoff + IS F2 + AS tool surface)
LOW risk units:       ~94 units      (68% of total; OTel + crypto + sandbox + schema)
```

### §8.4 Session 6 governance surfaces required

Four specific Session 6 governance surfaces required to enforce framework-pull discipline:

8.4.1 **CLAUDE.md design constraint declaration.** Explicit prohibition of LangGraph / LangChain / LlamaIndex / CrewAI / AutoGen / Temporal as foundational dependencies. List names per Stack §5.2 item 12 verbatim.

8.4.2 **Custom skill `engine-implementation-discipline`.** Enforces project-authored State/Checkpoint primitives at CP D1 unit implementation (U-CP-15 — U-CP-21); rejects "wrap LangGraph StateGraph" pattern.

8.4.3 **Custom skill `multi-agent-discipline`.** Enforces project-authored Agent/Topology primitives at CP D4 unit implementation against the 20-cell workload×engine matrix; rejects CrewAI/AutoGen abstraction adoption.

8.4.4 **Custom skill `hitl-discipline`.** Enforces project-authored 4-response palette + 3-placement primitive at CP D5 HITL unit implementation against LangGraph `interrupt()` adoption.

[HIGH] on surface identification; [MODERATE] on Session 6's capacity to enforce in practice (Session 6 deliverable validates).

---

## §9 Operator decision items

Two operator decisions surfaced at Segment 5; both dispositioned in-session.

### §9.1 OD-S2-1 disposition

| Field | Value |
|---|---|
| Decision | **A — Broaden Session 3 (ζ) scope to reconcile both F3-02 + C3-15 citation drift** |
| Rationale | Single revision-cycle absorbs both defects; no scope-leak across multiple revision cycles |
| Implication | `Phase_6_5_Session_3_Kickoff.md` §2.1 scope statement includes both items |

### §9.2 OD-S2-2 disposition

| Field | Value |
|---|---|
| Decision | **A — Defer httpx binding to Session 6 (ε); CLAUDE.md encodes binding** |
| Rationale | No Stack Commitment revision required; bootstrap substrate is the canonical encoding site for library bindings |
| Implication | `Target_Stack_Commitment_v1.md` v1 preserved as canonical; Session 6 CLAUDE.md design constraints declare httpx as canonical async HTTP client |

---

## §10 Forward implications for Sessions 3–7

| Session | Inheritance from this audit |
|---|---|
| Session 3 (ζ — IS-axis revision pass) | F3-02 absorption (canonical IS-axis ledger-write site unit) + C3-15 absorption (OD plan §4.5.1 OD→IS citation reconciliation); deliverable: IS plan v2.2 |
| Session 4 (η — Chicken-and-egg meta-architecture) | H_T ↔ H_E substitution mapping authored against §6.2 monorepo subdivision; §8.4 framework-pull governance surfaces inform H_E substitution boundaries |
| Session 5 (γ — Workflow v1.8 promotion) | Audit confirms Workflow v1.7 + v1.8 amendment §4.1.4.6.3 revision-cycle pattern adequate for F3-02 absorption at Session 3 (ζ) |
| Session 6 (ε — Claude Code CLI bootstrap substrate) | 13 Class 3 implementation binding decisions absorbed into CLAUDE.md + 4 custom skills (§8.4); 5-primitive harness-core content inventory (§6.3) informs bootstrap directory shape |
| Session 7 (β — Phase 7 Session 1 Entry Directive) | Pre-flight executability verdict (§11) attests to Phase 7 readiness against committed stack |

---

## §11 Pre-flight executability verdict

```
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║   PRE-FLIGHT EXECUTABILITY VERDICT                                   ║
║                                                                      ║
║   139 of 139 atomic units executable against Target_Stack_v1         ║
║   - 120 CLEAR (86.3%)                                                ║
║   - 19 GUARDRAIL with documented deferred-binding decisions (13.7%)  ║
║   - 0 FORK (no Class 1 or Class 2 surfaces)                          ║
║                                                                      ║
║   101 of 101 cross-axis edges resolve cleanly                        ║
║   40 of 40 bridging-arc transitions preserved                        ║
║   15 of 15 Pattern P1 namespaces byte-exact aligned                  ║
║                                                                      ║
║   F2-12 ✅ CLOSED at v2.2 cascade (preserved at v2.3)                 ║
║   F3-02 ACKNOWLEDGED-DEFERRED to Session 3 (ζ)                       ║
║   C3-15 BROADENED into Session 3 (ζ) per OD-S2-1.A                   ║
║                                                                      ║
║   Phase 7 execution at Claude Code CLI workspace is FEASIBLE         ║
║   under committed Python 3.12+ stack per Target_Stack_v1             ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
```

---

## §12 Filing footer

| Field | Value |
|---|---|
| Artifact | `Plan_Executability_Audit_v1.md` |
| Status | Filed at Session 2 (α) close 2026-05-15 |
| Phase | Phase 6.5 Session 2 (α) close |
| Authoring discipline | Workflow v1.7 §7 fidelity-grammar; `Phase_6_5_Session_2_Kickoff.md` §2.3 recommended structure |
| Predecessor | `Target_Stack_Commitment_v1.md`; `Phase_6_5_Session_2_Kickoff.md`; v2.3 implementation plans + CXA v2.1 |
| Successor (immediate) | `Phase_6_5_Session_2_Close_Handoff.md`; `Phase_6_5_Session_3_Kickoff.md` |
| Companion arc artifact | `Phase_6_5_Pre_Transition_Arc_Manifest.md` |
| Filing destination | `/mnt/user-data/outputs/Plan_Executability_Audit_v1.md` → operator pushes to `/mnt/project/` |
| Date | 2026-05-15 |

---

*End of Plan Executability Audit v1. Filed at Session 2 (α) close. Attests Phase 7 pre-flight executability under Target_Stack_v1 against v2.3 implementation plans.*
