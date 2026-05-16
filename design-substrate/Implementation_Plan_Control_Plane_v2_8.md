# Implementation Plan — Control Plane v2.8

**Status:** Proposed

**Date:** 2026-05-16

**Revision:** v2.8 — Phase 7 sub-phase 7b in-CLI revision. **Specifies the 9 deferred structured shared types and conforms two carried verbatim-divergence units.** v2.7 split the U-CP-00b carrier and deferred 9 "CP-owned structured shared types" (declared name + kind + provenance only — no member sets, no field schemas), blocking ~35 CP units. v2.8 specifies each of the 9 type shapes by faithful factor-out from its committing contract — operator-ratified as a non-design-extension under the T2 X-AL-3 resolution (`.harness/xal3_resolution_recommendations.md`: all 9 are FACTOR-OUTs, the concepts are spec/ADR-committed, only the declaration site was missing) — and homes them in a new L0 foundational carrier unit **U-CP-00c**. v2.8 additionally conforms **U-CP-08** (`FallThroughCause`) and **U-CP-11** (`LEASE_NAMESPACE_SCHEMA`) to their cited spec contracts per the §4A conform-to-spec precedent. v2.8 is a delta over v2.7: **only the new §2.0c (U-CP-00c), the revised §2.1 U-CP-08 body, the revised §2.2 U-CP-11 body, the §0.5 deferred-edge note, and the §11.1 registry are revised**; every other section is preserved verbatim from v2.7/v2.6. Predecessor: v2.7 (U-CP-00b carrier split).

**Revision date:** 2026-05-16

**Authority chain:** `Project_Workflow_v1_8.md` §7.4 fidelity-grammar; `CLAUDE.md` §1.3 authority chain + §4.3 back-flow routing; `harness-cp/CLAUDE.md` §5; `implementation-planner` SKILL.md §8 revision-pass sub-mode; operator-ratified T2 X-AL-3 resolution (`.harness/xal3_resolution_recommendations.md`) — all 9 deferred structured types verdicted FACTOR-OUT (no design-substrate revision needed; the `implementation-planner` revision pass declares the carrier and the faithful factor-out shape).

**Entry authorization:** Operator ratification 2026-05-15 of the T2 X-AL-3 FACTOR-OUT resolution + the §4A conform-to-spec precedent applied to the carried U-CP-08 / U-CP-11 verbatim-divergence items.

---

## §0 Change-note

### §0.1 Trigger

Three carried items, all surfaced and recorded at prior Phase-7 passes, are absorbed at this revision:

1. **The 9 deferred structured shared types** (`.harness/class_1_tension_u_cp_00b_structured_types.md`, RESOLVED-split for the 2 enums / OPEN for the 9 types). v2.7 §0.3 deferred `ActorIdentity`, `AgentRole`, `ModelBinding`, `TraceContext`, `ProviderAgnosticPayload`, `RoutingDecisionTrace`, `MCPTrustTier`, `Axis`, `TailKeepPredicate` — declared name-only at v2.6 §2.0b, struck from U-CP-00b at v2.7. ~35 CP units (the 15 direct Pattern-D consumers per §0.11.2 + their transitive consumers) are blocked until the shapes exist.
2. **U-CP-08 `FallThroughCause`** (`.harness/class_1_tension_u_cp_08_fall_through_cause.md`, SKIPPED-HALT; `.harness/pipeline-fork-queue.md` item 3). The plan invents a 4-value `FallThroughCause` enum the cited section did not commit.
3. **U-CP-11 `LEASE_NAMESPACE_SCHEMA`** (`.harness/class_1_tension_u_cp_11_lease_namespace_schema.md`, SKIPPED; fork-queue item 5; v2.4 §0.8 carried item). The plan's 5-tuple contradicts cited spec C-CP-05 §5.3's attribute table.

### §0.2 Class + routing

The 9-type item was a Class 1 (plan signatures not at implementation-grade detail) per `CLAUDE.md` §4.3. The operator-ratified T2 X-AL-3 resolution (`.harness/xal3_resolution_recommendations.md`) verdicts all 9 as **FACTOR-OUT** — each type's *concept* is committed by an existing spec/ADR; only the declaration site and the concrete shape were missing. Specifying a faithful factor-out of the committing contract is **not** a design extension (no X-AL-3 violation; no design-substrate revision needed). Routing target: this Phase-6 plan revision (in-CLI). U-CP-08 and U-CP-11 are Class 1 verbatim-divergence forks conformed to spec per the §4A precedent (operator-ratified, produced CP plan v2.4/v2.5).

### §0.3 The 9 structured types — specified shapes (faithful factor-out, traced byte-exact)

Each shape below is a faithful factor-out of the cited committing contract. No member set or field is invented; where a contract defers a sub-shape to implementation discretion the factor-out adopts the spec's own opaque-vocabulary form (no extension). All 9 are specified — **none stays deferred; no new Class 1 record was filed.**

| Type | Kind | Shape (specified) | Committing contract |
|---|---|---|---|
| `ActorIdentity` | newtype (`str`) | `NewType('ActorIdentity', str)` | Carrier-map "`ActorIdentity` vs IS `Actor`" + C-CP-13 §13.5 (`LedgerEntryRef.actor` — parent actor identity, a string identity at the non-F2 consumers) |
| `AgentRole` | newtype (`str`) — **decided: newtype, not enum** | `NewType('AgentRole', str)` | C-CP-01 §1.3 (manifest authoring grain "per agent role"); C-CP-13 §13 cross-axis citation header (`Spec_Action_Surface_v1.md` C-AS-13 §13.4 per-sub-agent-role × model-binding) |
| `ModelBinding` | record | `{ provider: str, model: str }` | ADR-F1 v1.2 §Decision (capability-aware abstraction); C-CP-01 §1.4 (`routing.provider`, `routing.model`); C-CP-13 §13.3 (lead-agent model binding) |
| `TraceContext` | record | `{ trace_id: str, span_id: str, trace_flags: int, trace_state: Optional[str] }` | W3C Trace Context (Target_Stack_Commitment C-STK-09 OTel adoption); C-CP-14 §14.1 ("trace_id propagated"; `parent_span_id`) |
| `ProviderAgnosticPayload` | record | `{ messages: List[Mapping[str, Any]], tools: Optional[List[Mapping[str, Any]]], params: Mapping[str, Any] }` | ADR-F1 v1.2 §Decision (provider-neutral thin core); C-CP-01 §1.1 (the `(messages, tools, params)` 3-tuple vocabulary) |
| `RoutingDecisionTrace` | record | `{ layer: str, candidate: str, decision_ms: int, budget_exhausted: bool }` | C-CP-01 §1.4 (`routing.layer` 4-value vocabulary); C-CP-02 §2.1 (layer ordering); U-CP-05 unit body (re-homed per operator decision D7) |
| `MCPTrustTier` | enum (4 values) | `{ LEVEL_0_REFUSE_REMOTE, LEVEL_1_SIGNED_PINNED, LEVEL_2_SANDBOX_ALL, LEVEL_3_ALLOW_WITH_AUDIT }` | `Spec_Action_Surface_v1.md` C-AS-10 §10.3 (MCP server trust-tier framework — 4 levels enumerated verbatim) |
| `Axis` | enum (5 values) | `{ PER_TOOL_GATE_LEVEL, BLAST_RADIUS, MCP_TRUST, PERSONA_TIER, SANDBOX_TIER }` | C-CP-19 §19.1 (4-axis `max()`) + §19.3 (D2 5-axis specialization adds `sandbox_tier`) |
| `TailKeepPredicate` | type alias | `Callable[[Any], bool]` (span argument typed opaque — see §0.3.1) | C-CP-21 §21.3 (operator-burden eval + tail-keep rules); U-CP-51 unit body |

#### §0.3.1 Per-type decision notes

- **`ActorIdentity`** — operator decision D9 (v2.6 §11.1) already homed `ActorIdentity` as a CP-owned identity alias (NOT the IS-exported F2 `Actor` — the carrier-map "`ActorIdentity` vs IS `Actor`" note is explicit: at the four non-F2 consumers U-CP-14/27/30/49 it is a separate CP-axis identity alias; the F2-shaped `actor` at U-CP-34/35 resolves to the IS `Actor` via the declared cross-axis IS edge and is untouched). v2.8 re-points its carrier `U-CP-00b` → `U-CP-00c` (new sibling foundational unit) and gives it a concrete shape — a `str` newtype, consistent with the C-CP-13 §13.5 `LedgerEntryRef.actor` parent-identity field. **No reconciliation with IS `Actor` is required** — they are nominally distinct types by the carrier-map ruling.
- **`AgentRole` — kind decided: newtype, not enum.** v2.6 §11.1 recorded `AgentRole` as "enum/newtype (undecided)". The CP spec uses `agent_role` only as a manifest-lookup key (C-CP-01 §1.3 "per agent role × per workflow class × per step"; C-CP-02 §2.1 `Lookup manifest entry by (agent_role, workflow_class, step)`); it enumerates **no closed agent-role set**. An enum would require inventing a closed value set the spec does not commit — an X-AL-3 design extension. The faithful factor-out is an open-string newtype. **Decided: `NewType('AgentRole', str)`.**
- **`TraceContext`** — the v2.6/v2.7 provenance line cited "CP §8". CP spec §8 (C-CP-08 replay-resumption) does **not** carry `trace_id`/`span_id` tokens; the in-spec basis for trace-context propagation is C-CP-14 §14.1 ("child span; trace_id propagated; parent_span_id = …"). The record shape is the W3C Trace Context standard (a Target_Stack_Commitment C-STK-09 OTel adoption — OTel GenAI semconv); the stale "§8" citation is corrected to C-CP-14 §14.1 + C-STK-09.
- **`RoutingDecisionTrace`** — adopted byte-exact from the U-CP-05 v2.1 unit body. The `layer` field is typed `str` (not the U-CP-05 `RoutingLayer` enum) so U-CP-00c carries no dependency on U-CP-05's enum; the `str` domain is the C-CP-01 §1.4 `routing.layer` vocabulary. U-CP-05 imports `RoutingDecisionTrace` from U-CP-00c (re-home per operator decision D7 — dissolves the U-CP-03→U-CP-05 level inversion).
- **`MCPTrustTier`** — the task contemplated a Class 1 vs spec if the tier set is genuinely uncommitted. It is **not uncommitted.** CP §19.1 names a "C10 five-tier framework" only in narrative and enumerates nothing; but the cross-axis-cited `Spec_Action_Surface_v1.md` C-AS-10 §10.3 enumerates the trust framework **concretely and verbatim** — `Level 0 refuse-remote / Level 1 signed-pinned / Level 2 sandbox-all / Level 3 allow-with-audit` (4 levels). The determinate factor-out is the AS §10.3 4-value enum. **No Class 1 filed.** The CP §19.1 "five-tier" narrative ↔ AS §10.3 4-level enumeration wording inconsistency is logged as a Class 3 informational item (§0.6); it does not block this type — AS §10.3 is the enumerating contract and is canonical for the value set.
- **`Axis`** — the 5-axis gate-composition enum is the union of C-CP-19 §19.1's 4 D5-layer axes (`per_tool_gate_level`, `blast_radius`, `per_mcp_server_trust` = `MCP_TRUST`, `persona_tier`) and §19.3's D2 specialization fifth axis (`sandbox_tier`). All five members trace to enumerated spec content; the enum is a faithful factor-out, not a plan invention (the v2.6 "plan-introduced" note is superseded — §19.1+§19.3 commit the axis set).
- **`TailKeepPredicate`** — U-CP-51's `evaluate_tail_keep(span: Span) -> bool` and `TailKeepRule.keep_predicate` field consume a predicate over a span. The `Span` handle is OD-axis-owned observability substrate; typing the predicate's argument as `Span` here would create a U-CP-00c → OD cross-axis dependency on a foundational L0 unit. The faithful factor-out is the opaque alias `Callable[[Any], bool]`; U-CP-51 type-checks the `Span` argument at its own site against the OD span type via its declared edges. C-CP-21 §21.3 commits the tail-keep-rule concept; the predicate-callable shape is the §21.3 factor-out.

### §0.4 Carrier decision — new unit U-CP-00c

All 9 types are declared in a **new L0 foundational carrier unit U-CP-00c** (beside U-CP-00 / U-CP-00b), `Depends on: (none)`, residence `harness-cp`. None of the 9 is genuinely cross-axis shared: `ActorIdentity` is a CP-owned alias by the carrier-map D9 ruling (distinct from IS `Actor`); `MCPTrustTier` is a CP-axis re-declaration of a value set AS §10.3 enumerates (CP consumes it at gate-level composition, AS owns the AS-side framework — a parallel CP-axis enum, not a cross-axis import, consistent with the v2.6 §11.1 CP-owned `MCPTrustTier` placement); the remaining 7 are CP-axis routing/workflow/observability primitives consumed only by CP units. No type is re-homed to `harness-core`. Full U-CP-00c unit body at §2.0c below.

### §0.5 Deferred-edge note — v2.7 §0.5 superseded

The v2.7 §0.5 deferred Pattern-D `[U-CP-00b]` edges for the 9 structured types' consumer units. v2.8 makes them **live `[U-CP-00c]` edges**. The 15 direct consumer units (per v2.6 §0.11.2, carrier re-pointed `U-CP-00b` → `U-CP-00c`):

| Type | Consuming CP unit(s) | Live edge at v2.8 |
|---|---|---|
| `ActorIdentity` | U-CP-14, U-CP-27, U-CP-30, U-CP-49 | `[U-CP-00c]` |
| `AgentRole` | U-CP-03, U-CP-04, U-CP-09, U-CP-27, U-CP-29 | `[U-CP-00c]` |
| `ModelBinding` | U-CP-13, U-CP-14, U-CP-29, U-CP-50 | `[U-CP-00c]` |
| `TraceContext` | U-CP-03 | `[U-CP-00c]` |
| `ProviderAgnosticPayload` | U-CP-03 | `[U-CP-00c]` |
| `RoutingDecisionTrace` | U-CP-03, U-CP-05 | `[U-CP-00c]` (re-home per D7 — replaces the U-CP-03→U-CP-05 forward edge; keeps the DAG level-ordered) |
| `MCPTrustTier` | U-CP-43, U-CP-45 | `[U-CP-00c]` |
| `Axis` | U-CP-43 | `[U-CP-00c]` |
| `TailKeepPredicate` | U-CP-32, U-CP-51 | `[U-CP-00c]` |

Direct-consumer unit set (15 distinct): U-CP-03, 04, 05, 09, 13, 14, 27, 29, 30, 32, 43, 45, 49, 50, 51. U-CP-00c is `Depends on: (none)`, L0 — all edges point consumer → U-CP-00c, no inversion. The DAG remains acyclic. No consuming unit of the 9 types is landed yet, so no edge dangled in landed code between v2.7 and v2.8.

### §0.6 Changes at v2.8

| Site | v2.7 | v2.8 |
|---|---|---|
| §2.0c (new) | — | **New L0 carrier unit U-CP-00c** — declares the 9 structured types with concrete shapes (full unit body) |
| §2.1 U-CP-08 | v2.1 body (invented 4-value `FallThroughCause`); SKIPPED-HALT | **Conformed body** — `FallThroughCause` conformed to C-CP-03 §3.5 `fallback.cause` 4-value set; cited section corrected §3.2 → §3.5 |
| §2.2 U-CP-11 | v2.1 body (invented 5-tuple + `LeaseEventKind`); SKIPPED | **Conformed body** — `LEASE_NAMESPACE_SCHEMA` conformed to C-CP-05 §5.3 5-tuple; `LeaseEventKind` struck; `LeaseMechanism` + `LeaseReleaseCause` enums added per §5.3 |
| §0.5 deferred-edge note | 9 Pattern-D `[U-CP-00b]` edges deferred | 15 consumer-unit `[U-CP-00c]` edges **live** |
| §11.1 registry | 9 structured-type rows carrier `DEFERRED` | 9 rows carrier **U-CP-00c** with specified shapes (see §11.1 delta) |

**Class 3 informational item logged at this pass.** CP spec §19.1 narrative "C10 five-tier framework" vs `Spec_Action_Surface_v1.md` C-AS-10 §10.3 4-level enumeration — a narrative/enumeration count inconsistency. Non-blocking for v2.8 (`MCPTrustTier` factors out of AS §10.3, the enumerating contract). Recorded for a future CP-spec doc-hygiene touch; no plan or code consequence.

### §0.7 Sections preserved verbatim from v2.7/v2.6

All of §0 (v2.6 + v2.7 change-notes), §1, §2 except the new §2.0c and the revised U-CP-08 (§2.1) and U-CP-11 (§2.2) bodies, §3–§10, §11 except the §11.1 registry rows enumerated at the §11.1 delta below, §[carry-forwards], §[traceability], §[coherence pass]. §2.0b U-CP-00b (the 2 utility enums) is preserved verbatim from v2.7.

---

## §2.0c U-CP-00c — Declare the 9 CP-owned structured shared types [NEW — v2.8]

#### U-CP-00c — Declare the CP-owned structured shared types (`ActorIdentity`, `AgentRole`, `ModelBinding`, `TraceContext`, `ProviderAgnosticPayload`, `RoutingDecisionTrace`, `MCPTrustTier`, `Axis`, `TailKeepPredicate`) — new CP foundational carrier unit, v2.8; specifies the 9 structured shared types deferred at v2.7, each as a faithful factor-out of its committing contract per the operator-ratified T2 X-AL-3 FACTOR-OUT resolution

**Implements:** (carrier unit — no single spec contract). U-CP-00c homes the 9 CP-owned structured shared types that have no natural single-unit cluster. Per the operator-ratified T2 X-AL-3 resolution (`.harness/xal3_resolution_recommendations.md`), each of the 9 is a **FACTOR-OUT** — the type's concept is committed by an existing spec/ADR and its shape is a faithful operationalization of that contract's content. Per `implementation-planner` SKILL.md §4.2 a carrier unit cites the aggregate of the contracts it serves; the per-type byte-exact contract traces are: `ActorIdentity` — `[C-CP-13 §13.5]` + carrier-map; `AgentRole` — `[C-CP-01 §1.3]` + `[C-CP-13 §13]` cross-axis citation header; `ModelBinding` — `[ADR-F1 v1.2 §Decision]` + `[C-CP-01 §1.4]` + `[C-CP-13 §13.3]`; `TraceContext` — `[C-CP-14 §14.1]` + Target_Stack_Commitment C-STK-09 (W3C Trace Context / OTel adoption); `ProviderAgnosticPayload` — `[ADR-F1 v1.2 §Decision]` + `[C-CP-01 §1.1]`; `RoutingDecisionTrace` — `[C-CP-01 §1.4]` + `[C-CP-02 §2.1]`; `MCPTrustTier` — `[Spec_Action_Surface_v1.md C-AS-10 §10.3]`; `Axis` — `[C-CP-19 §19.1]` + `[C-CP-19 §19.3]`; `TailKeepPredicate` — `[C-CP-21 §21.3]`. (This is the U-CP-00 / U-CP-00b precedent: a foundational CP carrier unit homing a cross-cluster vocabulary against the aggregate of its serving contracts.)

**Depends on:** (none) — foundational; L0, beside U-CP-00 and U-CP-00b. Imports nothing; the 15 direct Pattern-D consumer units (§0.5) import it.

**Inputs:** None (foundational; substrate-supplying carrier unit — mirrors U-CP-00 / U-CP-00b).

**Files affected:** CP-axis structured shared types (logical: `cp-shared-types`). **Residence: `harness-cp`** (CP-axis-owned — §0.4: no type is genuinely cross-axis shared; `ActorIdentity` is CP-owned per carrier-map D9; `MCPTrustTier` is a CP-axis enum of the value set AS C-AS-10 §10.3 enumerates; the other 7 are CP-axis routing/workflow/observability primitives).

**Signatures:**

```
// --- Identity ---
type ActorIdentity = NewType('ActorIdentity', str)
// CP-owned identity alias (operator decision D9 — Q-R4-7). Distinct from the
// IS-exported F2 `Actor` (carrier-map "ActorIdentity vs IS Actor"). String
// identity per C-CP-13 §13.5 LedgerEntryRef.actor ("parent actor identity").

type AgentRole = NewType('AgentRole', str)
// Open-string newtype — DECIDED kind (v2.8 §0.3.1). CP spec uses `agent_role`
// only as a manifest-lookup key (C-CP-01 §1.3; C-CP-02 §2.1
// `Lookup manifest entry by (agent_role, workflow_class, step)`); it commits
// NO closed agent-role set. An enum would invent an uncommitted value set
// (X-AL-3). Faithful factor-out: string newtype.

// --- Provider / routing ---
record ModelBinding {
  provider : str    // provider identity; cf. C-CP-01 §1.4 routing.provider
  model    : str    // model identifier within provider; cf. C-CP-01 §1.4 routing.model
}
// Per ADR-F1 v1.2 §Decision capability-aware abstraction + C-CP-13 §13.3
// lead-agent model binding. The (provider, model) pair is the §1.4 / §4.1
// routing-binding vocabulary.

record ProviderAgnosticPayload {
  messages : List[Mapping[str, Any]]            // provider-neutral message list
  tools    : Optional[List[Mapping[str, Any]]]  // optional tool definitions
  params   : Mapping[str, Any]                  // generation params
}
// Per ADR-F1 v1.2 §Decision provider-neutral thin core + C-CP-01 §1.1
// (the generate/stream/tool_use `(messages, tools, params)` 3-tuple). Sub-shapes
// are opaque mappings — C-CP-01 §1.4 defers the "provider-adapter binding
// library" to implementation discretion; opaque-mapping factor-out is faithful.

record RoutingDecisionTrace {
  layer            : str    // routing layer; C-CP-01 §1.4 routing.layer vocabulary
  candidate        : str    // "provider:model" tuple
  decision_ms      : int
  budget_exhausted : bool
}
// Re-homed from the U-CP-05 v2.1 unit body per operator decision D7 (Q-R4-5).
// `layer` typed `str` (not U-CP-05's RoutingLayer enum) so U-CP-00c carries no
// dependency on U-CP-05; the str domain is C-CP-01 §1.4 routing.layer.

// --- Observability ---
record TraceContext {
  trace_id    : str            // W3C trace-id
  span_id     : str            // W3C span-id
  trace_flags : int            // W3C trace-flags
  trace_state : Optional[str]  // W3C tracestate
}
// W3C Trace Context standard (Target_Stack_Commitment C-STK-09 OTel adoption)
// + C-CP-14 §14.1 ("child span; trace_id propagated; parent_span_id = …").

type TailKeepPredicate = Callable[[Any], bool]
// Predicate over a span, evaluated at tail-sampling time. The span argument is
// typed opaque (`Any`) — the Span handle is OD-axis-owned observability
// substrate; typing it here would create a U-CP-00c → OD cross-axis dependency
// on a foundational L0 unit. U-CP-51 type-checks the Span argument at its own
// site. Per C-CP-21 §21.3 operator-burden eval + tail-keep rules.

// --- Gate-level composition ---
enum MCPTrustTier {
  LEVEL_0_REFUSE_REMOTE,    // refuse-remote (REFUSE at registration)
  LEVEL_1_SIGNED_PINNED,    // signed-pinned (signature + version pin)
  LEVEL_2_SANDBOX_ALL,      // sandbox-all (tier-4-full-vm with egress allow-list)
  LEVEL_3_ALLOW_WITH_AUDIT  // allow-with-audit (audit-ledger entry per fetch/call)
}
// Closed at cardinality 4. Byte-exact factor-out of the 4-level MCP server
// trust-tier framework enumerated at `Spec_Action_Surface_v1.md` C-AS-10 §10.3.

enum Axis {
  PER_TOOL_GATE_LEVEL,  // C-CP-19 §19.1 — C4 contract input
  BLAST_RADIUS,         // C-CP-19 §19.1 — C10 four-tier blast-radius floor
  MCP_TRUST,            // C-CP-19 §19.1 — C10 five-tier per-MCP-server trust floor
  PERSONA_TIER,         // C-CP-19 §19.1 — D5 persona-tier floor
  SANDBOX_TIER          // C-CP-19 §19.3 — D2 5-axis specialization (added axis)
}
// Closed at cardinality 5. Factor-out of the gate-level `max()` axis set:
// the four D5-layer axes at C-CP-19 §19.1 + the fifth (sandbox_tier) at the
// D2 5-axis specialization C-CP-19 §19.3.
```

**Acceptance criteria:**

1. `ActorIdentity` is a `str` newtype; nominally distinct from the IS-exported `Actor` (no import of, and no structural reconciliation with, the IS F2 `Actor` type). Consumed by U-CP-14/27/30/49 via `[U-CP-00c]`.
2. `AgentRole` is a `str` newtype — not an enum. No closed agent-role value set is declared (the CP spec commits none; an enum would be an X-AL-3 extension). Consumed by U-CP-03/04/09/27/29.
3. `ModelBinding` declares exactly two fields `provider: str`, `model: str` — a faithful factor-out of the C-CP-01 §1.4 `routing.provider` / `routing.model` vocabulary and the C-CP-13 §13.3 lead-agent binding. No field beyond the `(provider, model)` pair. Consumed by U-CP-13/14/29/50.
4. `TraceContext` declares exactly four fields `trace_id: str`, `span_id: str`, `trace_flags: int`, `trace_state: Optional[str]` — the W3C Trace Context standard shape (Target_Stack_Commitment C-STK-09). The cited basis is C-CP-14 §14.1, not the stale "§8" of the v2.6/v2.7 provenance line. Consumed by U-CP-03.
5. `ProviderAgnosticPayload` declares exactly three fields `messages`, `tools` (optional), `params`, each typed as an opaque mapping/list-of-mapping — a faithful factor-out of the C-CP-01 §1.1 `(messages, tools, params)` 3-tuple; no provider-specific field is lifted into the record (C-CP-01 §1.4 defers the adapter binding to implementation discretion). Consumed by U-CP-03.
6. `RoutingDecisionTrace` declares exactly four fields `layer: str`, `candidate: str`, `decision_ms: int`, `budget_exhausted: bool` — byte-exact with the U-CP-05 v2.1 unit-body record; `layer` is typed `str` (not the `RoutingLayer` enum) so U-CP-00c depends on nothing. Consumed by U-CP-03/05.
7. `MCPTrustTier` declares exactly four values `LEVEL_0_REFUSE_REMOTE | LEVEL_1_SIGNED_PINNED | LEVEL_2_SANDBOX_ALL | LEVEL_3_ALLOW_WITH_AUDIT` — byte-exact factor-out of the 4-level framework at `Spec_Action_Surface_v1.md` C-AS-10 §10.3. Closed at cardinality 4. Consumed by U-CP-43/45.
8. `Axis` declares exactly five values `PER_TOOL_GATE_LEVEL | BLAST_RADIUS | MCP_TRUST | PERSONA_TIER | SANDBOX_TIER` — the four C-CP-19 §19.1 D5-layer axes plus the §19.3 D2 fifth axis. Closed at cardinality 5. Consumed by U-CP-43.
9. `TailKeepPredicate` is a `Callable[[Any], bool]` type alias; the span argument is opaque (no OD-axis `Span` import). Consumed by U-CP-32/51.
10. All 9 types reside in `harness-cp` and are exposed at the CP-axis package surface; each of the 15 direct Pattern-D consumer units (§0.5) resolves a single nominal type via `[U-CP-00c]`; `pyright` strict resolves one nominal type per type across all consumers.
11. No spec extension: each of the 9 types is a faithful factor-out of the cited committing contract per the operator-ratified T2 X-AL-3 FACTOR-OUT resolution; no member set, field, or value is invented beyond what the contract characterizes.

**Tests:** `test_actor_identity_is_str_newtype`; `test_actor_identity_distinct_from_is_actor`; `test_agent_role_is_str_newtype_not_enum`; `test_model_binding_two_fields`; `test_trace_context_four_fields_w3c_shape`; `test_provider_agnostic_payload_three_fields_opaque_mappings`; `test_routing_decision_trace_four_fields_byte_exact_u_cp_05`; `test_mcp_trust_tier_cardinality_four_byte_exact_as_10_3`; `test_axis_cardinality_five_byte_exact_cp_19`; `test_tail_keep_predicate_callable_alias`; `test_all_nine_types_reside_in_harness_cp`; `test_pattern_d_consumers_resolve_single_nominal_type` (a `pyright`-strict cross-unit composition check across the 15 consumer units).

**Rollback boundary:** Revert the U-CP-00c type declarations from `harness-cp`. Downstream impact: the 15 direct Pattern-D consumer units (§0.5) lose their structured-type carrier; each consuming unit's `[U-CP-00c]` edge dangles and the unit fails `pyright`. Because no consuming unit is landed at the time of this revision, a revert before any consumer lands has no landed-code impact. A single coherent revert.

---

## §2.1 Cluster 1 — U-CP-08 conformed body [REVISED — v2.8]

#### U-CP-08 — Implement deterministic fall-through procedure (v2.8 — `FallThroughCause` conformed to C-CP-03 §3.5 `fallback.cause` 4-value enumeration; cited section corrected §3.2 → §3.5; the invented `{LAYER_NO_DECISION, LAYER_BUDGET_EXHAUSTED, PROVIDER_UNAVAILABLE, CAPABILITY_SHORTFALL}` enum struck)

[v2.1-introduced unit; SKIPPED-HALT at Phase 7 7b per `.harness/class_1_tension_u_cp_08_fall_through_cause.md`. **v2.8 conformance delta.** The tension file halted on the basis that C-CP-03 §3.2/§3.3 commit no fall-through-cause enum — which is true of §3.2/§3.3 (procedures naming string-literal causes). But the same contract's §3.5 **does** enumerate the cause taxonomy verbatim: the `fallback.*` namespace row declares `fallback.cause ∈ {time_budget_exceeded, capability_shortfall, breaker_open, rate_limit_storm}` (a closed 4-value set). The unit's `Implements` already cites C-CP-03; v2.8 corrects the section pointer from §3.2 to §3.5 and conforms the enum to the §3.5 value set. This is the §4A conform-to-spec resolution (operator-ratified, produced CP plan v2.4/v2.5) applied: there IS a spec enumeration to conform to — the prior halt under-read §3.5. No design extension; no Class 1. All non-signature content preserved verbatim from the v2.1 body.]

**Implements:** [C-CP-03 §3.5, §3.2, §3.3]

**Depends on:** [U-CP-01, U-CP-05, U-CP-06, U-CP-07]

**Inputs:** `routing.*` namespace (U-CP-01); layered routing strategy (U-CP-05); `LayerBudget` (U-CP-06); `fallback.*` namespace (U-CP-07).

**Files affected:** CP-axis fall-through procedure (logical: `fall-through-procedure`).

**Signatures:**

```
enum FallThroughCause {
  TIME_BUDGET_EXCEEDED,   // per-layer time budget exceeded (C-CP-03 §3.2)
  CAPABILITY_SHORTFALL,   // provider/model capability shortfall (C-CP-03 §3.3)
  BREAKER_OPEN,           // circuit breaker open for {provider, model} (C-CP-03 §3.4)
  RATE_LIMIT_STORM        // rate-limit-storm preemptive advancement (C-CP-04 §4.2)
}
// Closed at cardinality 4. Byte-exact factor-out of the C-CP-03 §3.5
// `fallback.cause` attribute domain: ∈ {time_budget_exceeded,
// capability_shortfall, breaker_open, rate_limit_storm}. SCREAMING_SNAKE_CASE
// Python-stack rendering of the spec lowercase tokens; stems match 1:1.

record FallThroughResult {
  triggered_at_layer    : RoutingLayer
  cause                 : FallThroughCause
  next_layer            : Optional<RoutingLayer>
  emit_fallback_event   : bool
}

function fall_through(
    current_layer: RoutingLayer,
    cause: Optional<FallThroughCause>,
    request: InferenceRequest
) -> FallThroughResult
    // cause = None  -> the "layer produced no decision" case: advance to the
    //                  next layer per C-CP-03 §3.2 step 2 WITHOUT emitting a
    //                  fallback.triggered event (no spec cause applies).
    // cause = <FallThroughCause> -> emit fallback.triggered span event per
    //                  C-CP-03 §3.2/§3.3 with fallback.cause = cause.
    // Returns next layer in DECLARATIVE -> EMBEDDING -> LLM_AS_ROUTER order.
```

**Acceptance criteria:**
1. `FallThroughCause` declares exactly four values `TIME_BUDGET_EXCEEDED | CAPABILITY_SHORTFALL | BREAKER_OPEN | RATE_LIMIT_STORM` — byte-exact (modulo SCREAMING_SNAKE_CASE stack rendering) with the `fallback.cause` attribute domain enumerated at C-CP-03 §3.5. Closed at cardinality 4. No value invented; the prior v2.1 set (`LAYER_NO_DECISION` etc.) is struck.
2. The "layer produced no decision" case is **not** an enum member — it is represented as `cause = None` at the `fall_through` signature, which advances to the next layer per C-CP-03 §3.2 step 2 *without* emitting a `fallback.triggered` event (the spec §3.2 procedure emits the event only on a budget/capability cause; "no decision" is a silent advance).
3. `fall_through` honors the layer ordering invariant from U-CP-05; no upward layer skip permitted.
4. `cause = None` triggers fall-through silently (no `fallback.triggered` event); a non-`None` `cause` emits `fallback.triggered` per the U-CP-07 `fallback.*` namespace with `fallback.cause` set per C-CP-03 §3.2/§3.3.
5. Final-layer fall-through (LLM_AS_ROUTER → no next layer) returns `next_layer = None` and emits `fallback.exhausted` per C-CP-03 §3.2 step 3.
6. Procedure is deterministic given inputs.

**Tests:** `test_fall_through_cause_cardinality_four`, `test_fall_through_cause_values_byte_exact_with_spec_3_5`, `test_fall_through_honors_layer_ordering`, `test_no_decision_cause_none_silent`, `test_time_budget_exceeded_emits_event`, `test_capability_shortfall_emits_event`, `test_breaker_open_emits_event`, `test_rate_limit_storm_emits_event`, `test_final_layer_exhausted`.

**Rollback boundary:** Revert fall-through procedure. U-CP-05 layered routing loses fall-through implementation; budget exhaustion or capability shortfall blocks inference at the failed layer without recovery path. A single coherent revert.

---

## §2.2 Cluster 2 — U-CP-11 conformed body [REVISED — v2.8]

#### U-CP-11 — Declare `lease.*` namespace + 5-attribute schema (v2.8 — `LEASE_NAMESPACE_SCHEMA` conformed to C-CP-05 §5.3's attribute table; the invented 5-tuple `{lease.id, lease.acquired_at, lease.duration_ms, lease.event_kind}` + the `LeaseEventKind` enum struck; `LeaseMechanism` + `LeaseReleaseCause` enums added per §5.3)

[v2.1-introduced unit; SKIPPED at Phase 7 7b per `.harness/class_1_tension_u_cp_11_lease_namespace_schema.md`. **v2.8 conformance delta.** The plan's acc #1 5-tuple (`lease.id`, `lease.holder`, `lease.acquired_at`, `lease.duration_ms`, `lease.event_kind`) contradicted cited spec C-CP-05 §5.3, which declares `lease.key`, `lease.holder`, `lease.ttl_ms`, `lease.mechanism`, `lease.release_cause`. Per the §4A conform-to-spec resolution (operator-ratified) and the tension file's reading (1) — spec §5.3 is internally coherent and cross-referenced at C-CP-09 §9.1 + §5.2; the plan carried a contradicted "verbatim" claim — the plan body is conformed to the spec §5.3 attribute set. The invented `LeaseEventKind` enum (discriminator for the non-existent `lease.event_kind` attribute) is struck. The spec §5.3 `lease.mechanism` 6-value enum and `lease.release_cause` 4-value enum are declared as `LeaseMechanism` / `LeaseReleaseCause` at this unit (lease-specific — not shared, so not homed at U-CP-00c). All non-signature content otherwise preserved verbatim from the v2.1 body.]

**Implements:** [C-CP-05 §5.3]

**Depends on:** [U-CP-00b]

**Inputs:** `AttributeValueType` + `Cardinality` enums (U-CP-00b).

**Files affected:** CP-axis lease namespace (logical: `lease-namespace-attribute-schema`); CP-axis lease mechanism enum (logical: `lease-mechanism-enum`); CP-axis lease release-cause enum (logical: `lease-release-cause-enum`).

**Signatures:**

```
record LeaseAttributeSchema {
  attribute_name : string
  value_type     : AttributeValueType
  cardinality    : Cardinality
}
const LEASE_NAMESPACE_SCHEMA: List<LeaseAttributeSchema>  // exactly 5 entries

enum LeaseMechanism {
  ENGINE_NATIVE,
  REDIS_LEASE,
  DB_UNIQUE_CONSTRAINT,
  WORKTREE_ISOLATION,
  ETCD_CAS,
  PER_SEGMENT
}
// Closed at cardinality 6. Byte-exact factor-out of the C-CP-05 §5.3
// `lease.mechanism` enum-string domain ∈ {engine_native, redis_lease,
// db_unique_constraint, worktree_isolation, etcd_cas, per_segment}.

enum LeaseReleaseCause {
  NORMAL,
  TTL_EXPIRY,
  HOLDER_LOSS,
  LEASE_REVOKED
}
// Closed at cardinality 4. Byte-exact factor-out of the C-CP-05 §5.3
// `lease.release_cause` enum-string domain ∈ {normal, ttl_expiry,
// holder_loss, lease_revoked}.
```

**Acceptance criteria:**
1. `LEASE_NAMESPACE_SCHEMA` declares exactly five attributes per C-CP-05 §5.3 verbatim: `lease.key`, `lease.holder`, `lease.ttl_ms`, `lease.mechanism`, `lease.release_cause`. The prior v2.1 5-tuple (`lease.id`, `lease.acquired_at`, `lease.duration_ms`, `lease.event_kind`) is struck — it contradicted the cited section.
2. Per-attribute `value_type` / `cardinality` match the C-CP-05 §5.3 table: `lease.key` (string / per-active-lease); `lease.holder` (string / medium); `lease.ttl_ms` (int / unbounded-metric); `lease.mechanism` (`ENUM_REF` into `LeaseMechanism` / bounded-6); `lease.release_cause` (`ENUM_REF` into `LeaseReleaseCause` / bounded-4).
3. `LeaseMechanism` declares exactly six values `ENGINE_NATIVE | REDIS_LEASE | DB_UNIQUE_CONSTRAINT | WORKTREE_ISOLATION | ETCD_CAS | PER_SEGMENT` — byte-exact (modulo stack casing) with the C-CP-05 §5.3 `lease.mechanism` domain.
4. `LeaseReleaseCause` declares exactly four values `NORMAL | TTL_EXPIRY | HOLDER_LOSS | LEASE_REVOKED` — byte-exact with the C-CP-05 §5.3 `lease.release_cause` domain.
5. The invented `LeaseEventKind` enum is **struck** — it discriminated a `lease.event_kind` attribute that does not exist in spec §5.3.
6. No spec extension: the schema is a faithful transcription of the C-CP-05 §5.3 attribute table; no attribute or value is invented.

**Tests:** `test_lease_namespace_cardinality_five`, `test_lease_attributes_byte_exact_with_spec_5_3`, `test_lease_mechanism_cardinality_six`, `test_lease_release_cause_cardinality_four`, `test_no_lease_event_kind_enum` (regression — the struck enum does not reappear).

**Rollback boundary:** Revert `LEASE_NAMESPACE_SCHEMA` + `LeaseMechanism` + `LeaseReleaseCause`. Lease-event observability degrades; U-CP-12 per-class attribute composition for `lease.acquired` / `lease.released` events loses substrate. A single coherent revert.

---

## §11.1 CP auxiliary-type registry — v2.8 delta

The following 9 rows are revised — carrier `DEFERRED` → **U-CP-00c**, with the v2.8-specified shape and the corrected trace:

| Type | Kind | Carrier | Consuming units | Trace |
|---|---|---|---|---|
| `ActorIdentity` | newtype (`str`) | **U-CP-00c** | U-CP-14/27/30/49 | C-CP-13 §13.5 + carrier-map "`ActorIdentity` vs IS `Actor`" |
| `AgentRole` | newtype (`str`) — **decided** | **U-CP-00c** | U-CP-03/04/09/27/29 | C-CP-01 §1.3 + C-CP-13 §13 cross-axis citation header |
| `ModelBinding` | record | **U-CP-00c** | U-CP-13/14/29/50 | ADR-F1 v1.2 §Decision / C-CP-01 §1.4 / C-CP-13 §13.3 |
| `TraceContext` | record | **U-CP-00c** | U-CP-03 | C-CP-14 §14.1 + Target_Stack_Commitment C-STK-09 (W3C / OTel) |
| `ProviderAgnosticPayload` | record | **U-CP-00c** | U-CP-03 | ADR-F1 v1.2 §Decision / C-CP-01 §1.1 |
| `RoutingDecisionTrace` | record | **U-CP-00c** | U-CP-03, U-CP-05 | C-CP-01 §1.4 / C-CP-02 §2.1 / U-CP-05 unit body |
| `MCPTrustTier` | enum (4) | **U-CP-00c** | U-CP-43/45 | `Spec_Action_Surface_v1.md` C-AS-10 §10.3 |
| `Axis` | enum (5) | **U-CP-00c** | U-CP-43 | C-CP-19 §19.1 + §19.3 |
| `TailKeepPredicate` | type alias | **U-CP-00c** | U-CP-32/51 | C-CP-21 §21.3 + U-CP-51 unit body |

Two enums are added to the registry — declared at U-CP-11 (v2.8-conformed body), lease-specific (not shared):

| Type | Kind | Carrier | Consuming units | Trace |
|---|---|---|---|---|
| `LeaseMechanism` | enum (6) | U-CP-11 (v2.8) | U-CP-11 | C-CP-05 §5.3 |
| `LeaseReleaseCause` | enum (4) | U-CP-11 (v2.8) | U-CP-11 | C-CP-05 §5.3 |

The `FallThroughCause` enum (U-CP-08, v2.8-conformed) is an in-unit enum declared at its consuming unit — registry row: carrier `U-CP-08`, kind `enum (4)`, trace `C-CP-03 §3.5`. The `AttributeValueType` / `Cardinality` rows (carrier `U-CP-00b`) and all other §11.1 rows are preserved verbatim from v2.7/v2.6. Per §11.2 registry discipline, all 9 structured-type rows now carry a reachable carrier (U-CP-00c) — the Pattern-D items are closed; the 15 direct consumer units (§0.5) may land against U-CP-00c. The v2.7 `LeaseEventKind` registry presence (if any) is struck with the enum.

---

## §5 Filing footer

| Field | Value |
|---|---|
| Artifact | `Implementation_Plan_Control_Plane_v2_8.md` |
| Authored at | Phase 7 sub-phase 7b, 2026-05-16 — v2.8 revision (9 structured-type specification + U-CP-08 / U-CP-11 conformance) |
| Authoring authority | Operator ratification of the T2 X-AL-3 FACTOR-OUT resolution (`.harness/xal3_resolution_recommendations.md`) + the §4A conform-to-spec precedent applied to U-CP-08 / U-CP-11 |
| Predecessor | `Implementation_Plan_Control_Plane_v2_7.md` (U-CP-00b carrier split) |
| Successor consumption | U-CP-00c lands as an L0 foundational carrier; the 15 direct Pattern-D consumer units (§0.5) and U-CP-08 / U-CP-11 land against this file |
| Revision policy | Canonical for the CP axis plan; revisions in-CLI per workspace discipline |

*End of Implementation Plan — Control Plane v2.8. Delta over v2.7 — the new §2.0c U-CP-00c carrier unit, the conformed §2.1 U-CP-08 + §2.2 U-CP-11 bodies, the §0.5 deferred-edge note, and the §11.1 registry revised. All other sections preserved verbatim from v2.7/v2.6.*
