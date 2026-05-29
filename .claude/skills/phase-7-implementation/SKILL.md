---
name: phase-7-implementation
description: Execute Phase 7 sub-phase 7b atomic unit consumption against the per-axis implementation plans (IS v2.2 / AS v1 / CP v2.3 / OD v2.4). Activates when the user requests implementation of a specific atomic unit ("implement U-IS-01", "consume U-CP-23", "land U-OD-20", "execute the next atomic unit"), opens a cluster for axis-stream execution, authorizes per-cluster traversal at the axis-stream sub-agents (sa-is / sa-as / sa-cp / sa-od), or references an atomic unit ID from the canonical plans. Use this skill whenever the user mentions atomic units, unit consumption, axis-stream implementation, cluster open or close authorization, U-IS-NN / U-AS-NN / U-CP-NN / U-OD-NN identifiers, acceptance-criteria-driven implementation, topological-sort traversal, per-unit signature materialization, coverage matrix updates, or any reference to specific unit IDs from the v2.x plans. Always activate when the user says "implement", "execute", "consume", "land", "atomic unit", "cluster", or "traverse" in the context of Phase 7 execution, even if no unit ID is explicitly named.
---

# phase-7-implementation

Phase 7 sub-phase 7b atomic unit consumption discipline. Drives execution of per-axis atomic units from the v2.x implementation plans under the deterministic outer-harness invariants of the multi-LLM agent harness build.

## 0. Posture precondition

**This skill is Phase 7 only.** Per workspace `CLAUDE.md` §11 (posture declaration — third axis of the X-AL-3 enforcement triad), this workspace co-resides three logical postures (design-phase / Phase 7 / mode-agnostic). Atomic unit consumption is a Phase-7 activity by definition: it reads `design-substrate/*` as canonical and edits `harness-*/src/**` + `harness-*/tests/**`.

Before doing substantive work, verify the session posture:

| Detected posture | Action |
|---|---|
| **Phase 7** (explicit declaration OR edit scope is `harness-*/src/**` + tests only) | Proceed. |
| **Mode-agnostic** (workspace ops; edits are root `CLAUDE.md` / `.github/` / `.claude/` / etc.) | This skill is not the right tool. Suggest mode-agnostic work proceed without this skill's framing; defer to operator. |
| **Design-phase** (explicit declaration OR edit scope is `design-substrate/**` / `.harness/**` back-flow docs) | **HALT.** Atomic unit consumption at design-phase posture is X-AL-3 silent H_T design extension (`CLAUDE.md` §4.4 + I-2). Surface the conflict; suggest the operator either (a) re-declare posture as Phase 7 if the intent IS impl execution, OR (b) invoke a design-phase skill (`implementation-planner`, `spec-writer`, `systems-architect`, `harness-adversarial-reviewer`) if the intent is plan/spec authoring. Do NOT proceed with atomic unit work. |
| **Unclear** (no explicit declaration; ambiguous edit scope) | Halt + ask per `CLAUDE.md` §11.6. Present the 3 posture options; honor the response. |

A bundled-absorption arc (legitimate mixed-posture per `CLAUDE.md` §11.4) — e.g., a spec amendment that cascades into impl in the same PR — DOES carry a `.harness/` back-flow doc (fork doc / architect recommendation / retirement event / clearance marker). If the operator declares "bundled-absorption arc" + names the back-flow doc, this skill activates for the impl portion while the design-phase skills handle the substrate portion in the same session. If no back-flow doc is named, treat as unclear → halt + ask.

## 1. Activation surface

### 1.1 Active during

- Sub-phase 7b per-axis-stream execution (IS / AS / CP / OD axis-streams)
- Per-cluster traversal at sa-is / sa-as / sa-cp / sa-od sub-agents
- Operator request for specific unit implementation or cluster open

### 1.2 NOT active during

| Sub-phase | Alternate skill |
|---|---|
| 7a (bootstrap) | None specific; consult Meta-Architecture §5 + §6 directly |
| 7c (cross-axis composition) | `phase-7-cross-axis-composition` |
| 7d (substitution retirement) | `phase-7-substitution-retirement` |
| Fork detection (any sub-phase) | `phase-7-back-flow-routing` |

## 2. Authority chain

Per workspace root `CLAUDE.md` §1.3:

```
ADR (F1–F5 + D1–D6)
  → ADD v1.3
  → PRD v1.1
  → per-axis spec v1.x
  → per-axis plan v2.x + CXA v2.1
  → Phase 7 implementation (this skill operates here)
```

Earlier artifacts are canonical for later artifacts. Conflicts route to `phase-7-back-flow-routing`.

Canonical artifacts at design-phase workspace (see workspace root `CLAUDE.md` §2):

| Artifact family | Canonical versions |
|---|---|
| Per-axis specs | IS v1.2 / AS v1.1 / CP v1.3 / OD v1.3 |
| Per-axis plans | IS v2.2 / AS v1 / CP v2.3 / OD v2.4 |
| Cross-axis | CXA v2.1 |
| ADR consolidation | ADD v1.3 |
| Product requirements | PRD v1.1 |

## 3. Per-unit execution shape

Per `Phase_7_Kickoff_Prompt.md` §4.3, every atomic unit follows:

### 3.1 Step 1 — Read the unit declaration end-to-end

Load the unit's complete declaration from the per-axis plan: **Implements** + **Depends on** + **Inputs** + **Files affected** + **Signatures** + **Acceptance criteria** + **Tests** + **Rollback boundary**. Do NOT proceed without complete unit context.

### 3.2 Step 2 — Read the cited spec contract section

From the unit's `Implements: [C-AXIS-NN §X.Y]` field, load the cited spec contract section at full granularity. The spec contract is the authoritative source for signatures and invariants; the plan is the executable specification of the spec contract.

### 3.3 Step 3 — Read the parent ADR section(s)

From the spec contract's `ADR commitments honored:` row, load the parent ADR section(s). ADRs anchor architectural commitments; understanding ADR rationale prevents drift during implementation.

### 3.4 Step 4 — Verify dependencies landed

For each entry in `Depends on:`:

| Dependency type | Verification |
|---|---|
| Within-axis | The dependent unit's outputs satisfy this unit's `Inputs` field |
| Cross-axis `(cross-axis: AXIS)` | The dependency's terminal exporter manifest (U-IS-17 / U-AS-33 / U-CP-55 / U-OD-34) is operational |

DO NOT proceed if any dependency is not landed. Halt and route per `phase-7-back-flow-routing` if dependency cannot be resolved.

### 3.5 Step 5 — Implement signatures + tests

Materialize the plan's specification-level signatures at the target stack:

| Stack element | Commitment |
|---|---|
| Language | Python 3.12+ |
| Type contracts | Pydantic v2 |
| Concurrency | `asyncio` |
| Package management | `uv` workspace |
| Type checker | `pyright` (strict mode) |
| Linter / formatter | `ruff` |
| Test runner | `pytest` + `pytest-asyncio` |

Source: `Target_Stack_Commitment_v1.md` (design-phase workspace); workspace root `CLAUDE.md` §3.1.

**Framework-pull discipline binds** per `Plan_Executability_Audit_v1.md` and workspace root `CLAUDE.md` §3.2:

| Category | NOT permitted |
|---|---|
| Reliability primitives | `tenacity`, `pybreaker`, `circuitbreaker` |
| Workflow orchestration | `prefect`, `temporal`, `langgraph`, `crewai`, `langchain`, `llamaindex` |
| Multi-LLM abstraction | LiteLLM |
| Validation | `pydantic-validators-plus` |

Hand-roll reliability primitives, workflow orchestration, multi-LLM abstraction, and validation per the per-axis-plan units.

Test cases per the unit's `Tests:` field. Each acceptance criterion maps to at least one test → green.

### 3.6 Step 6 — Verify acceptance criteria

Each criterion in the unit's `Acceptance criteria:` list must be met by the implementation. Cross-check each criterion against:

1. Spec contract requirements (per the cited section)
2. Test cases (each criterion mapped to at least one test)
3. Implementation behavior (concrete observable invariant)

### 3.7 Step 7 — Update progress + traceability

- Mark the unit complete in workspace progress ledger (workspace-internal artifact; not specified at design-phase)
- Update per-axis coverage matrix
- Verify cross-axis traceability if the unit emits to a cross-axis edge consumed by another axis

### 3.8 Step 8 — Cluster coherence pass (at cluster boundary)

Per `Phase_7_Meta_Architecture_v1.md` §10.2.4 step 4: at cluster close, apply 5-dimension audit per `implementation-planner` SKILL.md §6:

| Dimension | Audit question |
|---|---|
| Atomicity | Does each unit cover exactly one surface? |
| Spec-traceability | Does every unit cite its contract by C-AXIS-NN §X.Y? |
| Dependency-awareness | Are within-axis + cross-axis edges declared correctly? |
| Implementation-grade detail | Are signatures + tests + rollback boundary complete? |
| Anti-pattern audit | Have any of the foreclosed patterns at Meta-Architecture §7 surfaced? |

### 3.9 Step 9 — Operator confirmation at cluster close

Per Meta-Architecture §10.2.4 step 5: operator confirms cluster close before next cluster opens. Sub-agents do NOT cross cluster boundaries without operator confirmation per `Sub_Agent_Boundary_Specification_v1.md` §8.2.

## 4. Anti-leakage discipline

Per workspace root `CLAUDE.md` §8 execution invariants and per-axis `CLAUDE.md` §4.2 axis-specific rules:

### 4.1 Cross-cutting invariants

| Invariant | Statement | Source |
|---|---|---|
| I-1 | Citations resolve byte-exact | Workflow v1.8 §7.4.2 |
| I-2 | NO H_T design extension at execution-time | X-AL-3 |
| I-3 | Substitution retirement is event-driven (delegate to `phase-7-substitution-retirement`) | X-AL-2 |
| I-4 | H_E ↔ H_T substrate boundary at MCP server process | X-AL-1 |
| I-5 | Class 1 forks halt sub-phase execution (delegate to `phase-7-back-flow-routing`) | Workflow v1.8 §2.7.6 |
| I-6 | Framework-pull discipline holds | `Plan_Executability_Audit_v1.md` |
| I-7 | Multi-LLM commitment unchanged | ADR-F1 v1.2; CP-AL-4 |

### 4.2 Per-axis anti-leakage rules

Consult the relevant per-axis `CLAUDE.md` §4.2 before any per-axis implementation:

| Axis | Anti-leakage location |
|---|---|
| IS | `harness-is/CLAUDE.md` §4.2 (IS-AL-1 through IS-AL-4) |
| AS | `harness-as/CLAUDE.md` §4.2 (AS-AL-1 through AS-AL-4) |
| CP | `harness-cp/CLAUDE.md` §4.2 (CP-AL-1 through CP-AL-5); CP-AL-1 also at `Sub_Agent_Boundary_Specification_v1.md` §5.1 |
| OD | `harness-od/CLAUDE.md` §4.2 (OD-AL-1 through OD-AL-3) |

## 5. Cross-axis dependency handling

When the unit declares `Depends on: [U-IS-NN (cross-axis: IS)]` (or equivalent for AS / CP / OD):

### 5.1 Read-only consumption

1. READ the cross-axis dependency's substrate from the dependency's terminal exporter manifest (U-IS-17 / U-AS-33 / U-CP-55 / U-OD-34)
2. DO NOT execute the cross-axis dependency's atomic unit — that unit is owned by the other axis-stream sub-agent
3. VERIFY the cross-axis dependency landed before proceeding with the dependent within-axis unit

Per `Sub_Agent_Boundary_Specification_v1.md` §6.2: cross-axis substrate access is READ-ONLY via terminal exporter manifests.

### 5.2 Cross-axis edge cardinality

| Edge direction | Edges | Source |
|---|---|---|
| AS → IS | 13 | CXA v2.1 §2.3.1 |
| CP → IS | 36 | CXA v2.1 §2.3.2 |
| OD → CP | 12 | CXA v2.1 §2.3.3 |
| CP → AS | 24 | CXA v2.1 §2.3.4 |
| OD → IS | 6 (baseline) / 4 (OD v2.4) | CXA v2.1 §2.3.5 |
| OD → AS | 10 | CXA v2.1 §2.3.6 |
| **Aggregate** | **101 / 99** | CXA v2.1 §2.1 |

## 6. Halt conditions

HALT unit execution and surface to operator (via `phase-7-back-flow-routing`) when:

| Halt trigger | Class | Routing target |
|---|---|---|
| Cited spec contract section unreachable or under-specifies the surface | 1 | Phase 5 spec revision |
| Plan signature cannot be materialized at target stack | 1 | Phase 6 plan revision |
| Cross-axis dependency not landed (cross-axis-stream out of sequence) | 1 | Halt; await cross-axis sub-agent |
| Acceptance criterion incompatible with another criterion | 1 | Spec or plan revision |
| New H_T primitive surfaced | 1 | Design-phase ADR back-flow (X-AL-3) |
| Framework adoption proposed beyond Plan_Executability_Audit_v1.md | 2 | Operator decision |

DO NOT silently absorb defects. DO NOT proceed past halt point without explicit operator authorization.

## 7. Reference artifacts

| Reference | Location | Authority |
|---|---|---|
| Workspace root `CLAUDE.md` | This workspace | Workspace-level guidance + canonical artifact pointers |
| Per-axis `CLAUDE.md` | `harness-{is,as,cp,od}/` | Per-axis substrate authority |
| `Sub_Agent_Boundary_Specification_v1.md` | Workspace root | Sub-agent topology + scope boundaries |
| `Phase_7_Meta_Architecture_v1.md` | Design-phase workspace | Substitution mapping + anti-leakage rules + sub-phase enumeration |
| `Project_Workflow_v1_8.md` | Design-phase workspace | Workflow governance + back-flow routing |
| `Target_Stack_Commitment_v1.md` | Design-phase workspace | Stack discipline |
| `Plan_Executability_Audit_v1.md` | Design-phase workspace | Framework-pull discipline + GUARDRAIL inventory |

## 8. Common patterns

### 8.1 Foundational (L0) unit consumption

Foundational units have `Depends on: (none)` or cross-axis-only deps. Per-axis L0 unit counts:

| Axis | L0 units | List |
|---|---|---|
| IS | 5 | U-IS-01, U-IS-03, U-IS-04, U-IS-07, U-IS-13 |
| AS | 3 | U-AS-01, U-AS-03, U-AS-04 |
| CP | 13 | U-CP-01, U-CP-02, U-CP-03, U-CP-07, U-CP-10, U-CP-11, U-CP-15, U-CP-19, U-CP-21, U-CP-22, U-CP-26, U-CP-28, U-CP-37 |
| OD | 2 | U-OD-01, U-OD-04 |

7b axis-stream execution begins from these entry-points per per-axis `CLAUDE.md` §3.

### 8.2 Terminal exporter unit consumption

Terminal aggregate exporter units (U-IS-17 / U-AS-33 / U-CP-55 / U-OD-34) close each per-axis-stream. After landing, the axis-stream sub-agent terminates per `Sub_Agent_Boundary_Specification_v1.md` §4.1–§4.4 termination criteria.

### 8.3 GUARDRAIL unit consumption

Per `Plan_Executability_Audit_v1.md`, certain units require project-authored substrate (custom OTel SpanProcessor, custom Sampler, in-sandbox HTTP server). Per-axis GUARDRAIL inventories:

| Axis | GUARDRAIL units | Source |
|---|---|---|
| IS | (per Plan_Executability_Audit §3.1) | Plan_Executability_Audit_v1.md |
| AS | U-AS-17, U-AS-18, U-AS-20, U-AS-25 | Plan_Executability_Audit_v1.md §3.2 |
| CP | (per Plan_Executability_Audit §3.3) | Plan_Executability_Audit_v1.md |
| OD | (per Plan_Executability_Audit §3.4) | Plan_Executability_Audit_v1.md |

Project-authoring proceeds against documented ABCs (e.g., `opentelemetry.sdk.trace.SpanProcessor`) per the audit's recommendation column.

---

*End of `phase-7-implementation` skill. Loaded at sub-phase 7b activation. Delegates to `phase-7-cross-axis-composition` (7c), `phase-7-substitution-retirement` (event-driven), `phase-7-back-flow-routing` (fork detection).*
