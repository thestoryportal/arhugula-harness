# Class 1 Tension — U-CP-00b 9 structured shared types under-specified

*Phase 7 sub-phase 7b. Fork detected at U-CP-00b execution-time. Routed per
`CLAUDE.md` §4.3 + `harness-cp/CLAUDE.md` §5. RESOLVED (split) — operator ruling
2026-05-15. The 9 structured types remain OPEN pending a future CP plan revision.*

---

## 1. Identification

| Field | Value |
|---|---|
| Tension ID | Class-1 / U-CP-00b / structured-types |
| Sub-phase | 7b (per-axis-stream implementation — carrier-unit cluster) |
| Surfaced at | Landing U-CP-00b (CP-axis foundational carrier) |
| Class | **1** — plan signatures not at implementation-grade detail |
| Routing target | Phase 6 plan revision — `Implementation_Plan_Control_Plane` (in-CLI) |
| Status | **RESOLVED (split)** 2026-05-15 — U-CP-00b narrowed + landed; the 9 structured types **OPEN**, deferred to a future CP plan revision |

## 2. The defect

The v2.6 §2.0b U-CP-00b unit body bundled two materializability classes:

- **Materializable:** `AttributeValueType` (5 values) + `Cardinality` (4 values)
  — fully-specified byte-exact relocations of enums previously inline at
  U-CP-01.
- **Under-specified:** 9 "CP-owned structured shared types" declared in the
  Signatures block as a type *name* + kind keyword + a one-line provenance
  comment only — no enum member sets, no record field schemas:

  | Type | Kind | Provenance cited |
  |---|---|---|
  | `ActorIdentity` | newtype | carrier-map "`ActorIdentity` vs IS `Actor`" |
  | `AgentRole` | enum/newtype (plan undecided) | C-CP-13 §13.4 |
  | `ModelBinding` | record | ADR-F1 v1.2 / C-CP-13 §13.4 |
  | `TraceContext` | record | OTel W3C Trace Context / CP §8 |
  | `ProviderAgnosticPayload` | record | ADR-F1 v1.2 / C-CP-01/02 |
  | `RoutingDecisionTrace` | record | re-homed from U-CP-05 / CP §2 |
  | `MCPTrustTier` | enum | C-CP-43 gate-level |
  | `Axis` | enum | 5-axis gate enum (plan-introduced) |
  | `TailKeepPredicate` | type | CP §51 tail-keep |

The §11.1 registry itself records `AgentRole` as "enum/newtype" — the plan has
not decided the type's kind. Authoring 9 shapes (3 records) from 6+ scattered
spec sections + U-CP-05's body at execution-time discretion is genuine design
surface — X-AL-3 silent-design-extension risk if a shape is guessed wrong. The
9 types are not at implementation-grade detail (`implementation-planner`
SKILL.md §3.8 / §6).

## 3. Operator ruling — 2026-05-15 (split)

U-CP-00b is **narrowed to the 2 utility enums** (`AttributeValueType`,
`Cardinality`) — they land now and unblock the 7 Pattern-C `…AttributeSchema`
consumer units (U-CP-01/07/11/21/31/37/46/47). The 9 structured shared types
are **struck from U-CP-00b** and deferred.

## 4. Resolution applied + OPEN item

- `Implementation_Plan_Control_Plane_v2_7.md` filed — §2.0b U-CP-00b narrowed
  to the 2 enums; §11.1 registry's 9 structured-type rows → carrier DEFERRED.
- `CLAUDE.md` §2.4 CP plan pointer updated v2_6 → v2_7.
- U-CP-00b (2 enums) landed against v2.7.

**OPEN — owed work.** A future CP plan revision MUST specify, for each of the 9
structured types, its concrete shape (enum member set or record field schema)
traced to its committing contract, before any consuming unit lands:

| Type | Consuming units (none landed) | Spec read owed |
|---|---|---|
| `ActorIdentity` | U-CP-14/27/30/49 | carrier-map; likely a `str` newtype |
| `AgentRole` | U-CP-03/04/09/27/29 | C-CP-13 §13.4 — and decide enum vs newtype |
| `ModelBinding` | U-CP-13/14/29/50 | ADR-F1 v1.2 + C-CP-13 §13.4 |
| `TraceContext` | U-CP-03 | W3C Trace Context standard + CP §8 |
| `ProviderAgnosticPayload` | U-CP-03 | ADR-F1 v1.2 + C-CP-01/02 |
| `RoutingDecisionTrace` | U-CP-03, U-CP-05 | U-CP-05 body + CP §2 |
| `MCPTrustTier` | U-CP-43/45 | C-CP-43 |
| `Axis` | U-CP-43 | CP 5-axis gate composition (C-CP-19) |
| `TailKeepPredicate` | U-CP-32/51 | CP §51 |

Per CP plan v2.7 §0.5, the Pattern-D `[U-CP-00b]` edges for these types' consumers
are deferred with the types; no landed code dangles (no consumer landed).

## 5. Filing footer

| Field | Value |
|---|---|
| Artifact | `.harness/class_1_tension_u_cp_00b_structured_types.md` |
| Authored | Phase 7 7b, 2026-05-15 |
| Resolution authority | Operator ruling 2026-05-15 (split U-CP-00b) |
| Status | RESOLVED (split) for the 2 enums; **RESOLVED 2026-05-16** for the 9 structured types (CP plan v2.8 — see §6) |

---

## §6 Resolution of the 9 structured types — 2026-05-16

`Implementation_Plan_Control_Plane_v2_8.md` filed. The 9 structured shared types
are specified, each as a faithful factor-out of its committing contract per the
operator-ratified T2 X-AL-3 FACTOR-OUT resolution
(`.harness/xal3_resolution_recommendations.md` — all 9 verdicted FACTOR-OUT, no
design-substrate revision needed). They are declared in a **new L0 foundational
carrier unit U-CP-00c** (`Depends on: (none)`, residence `harness-cp`):

- `ActorIdentity` — `NewType('ActorIdentity', str)` — C-CP-13 §13.5 + carrier-map.
- `AgentRole` — `NewType('AgentRole', str)` (kind DECIDED: newtype, not enum — CP
  spec commits no closed agent-role set) — C-CP-01 §1.3 + C-CP-13 §13.
- `ModelBinding` — record `{provider: str, model: str}` — ADR-F1 v1.2 / C-CP-01
  §1.4 / C-CP-13 §13.3.
- `TraceContext` — record `{trace_id, span_id, trace_flags, trace_state}` (W3C) —
  C-CP-14 §14.1 + Target_Stack_Commitment C-STK-09 (stale "§8" citation corrected).
- `ProviderAgnosticPayload` — record `{messages, tools, params}` (opaque mappings)
  — ADR-F1 v1.2 / C-CP-01 §1.1.
- `RoutingDecisionTrace` — record `{layer: str, candidate, decision_ms,
  budget_exhausted}` — C-CP-01 §1.4 / C-CP-02 §2.1 / U-CP-05 body.
- `MCPTrustTier` — enum 4 values — `Spec_Action_Surface_v1.md` C-AS-10 §10.3
  (no Class 1 filed — AS §10.3 enumerates the framework concretely).
- `Axis` — enum 5 values — C-CP-19 §19.1 + §19.3.
- `TailKeepPredicate` — `Callable[[Any], bool]` alias — C-CP-21 §21.3.

§11.1 registry rows updated DEFERRED → U-CP-00c. v2.7 §0.5 deferred-edge note
superseded — the 15 direct Pattern-D consumer-unit edges are now live `[U-CP-00c]`.
`CLAUDE.md` §2.4 CP plan pointer updated v2_7 → v2_8. **No type stays deferred;
no new Class 1 record filed.** A Class 3 informational item logged at v2.8 §0.6
(CP §19.1 "five-tier" narrative vs AS §10.3 4-level enumeration — non-blocking).

---

## Audit reconciliation (2026-05-20)

**Verified status:** RESOLVED

**Resolving artifact / evidence:** Already labeled RESOLVED 2026-05-16 (CP plan v2.7/v2.8 — U-CP-00b narrowed to 2 enums; 9 structured types moved to U-CP-00c). Audit confirms.

**Audit context:** Workspace-wide tension-record audit 2026-05-20 (post-U-RT-52 merge to main at 2b945ab). 33 records reviewed against current code + spec state. Result: 28 RESOLVED, 5 DEFERRED-PARTITION, 0 STILL-OPEN. The 'Status' line earlier in this record predates the audit; this section is the current verified state.
