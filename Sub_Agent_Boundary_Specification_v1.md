# Sub_Agent_Boundary_Specification_v1.md

*Sub-agent boundary specification for the Phase 7 workspace. Canonical reference for Claude Code sub-agent topology scope, per-sub-agent responsibility, and per-sub-agent anti-leakage citation. Loaded by Claude Code at session startup alongside workspace root `CLAUDE.md`.*

---

## 1. Specification scope

### 1.1 What this document specifies

This specification declares the **H_E sub-agent topology** for the Phase 7 workspace. Specifically:

1.1.1 Sub-agent count + per-sub-agent identifier (§3)
1.1.2 Per-sub-agent responsibility scope, bounded by H_T axis decomposition (§4)
1.1.3 Per-sub-agent anti-leakage citation against CP-AL-1 verbatim per `Phase_6_5_Session_6_Kickoff.md` §5.2.4 (§5)
1.1.4 Per-sub-agent scope boundaries against the 4 axes (IS / AS / CP / OD) (§6)
1.1.5 Sub-agent lifecycle + process boundary discipline (§7)

### 1.2 What this document is NOT

This specification is **H_E topology only**. It does NOT:

1.2.1 Specify H_T's CP-axis TopologyPattern enum or any H_T topology primitive — **see CP-AL-1 at §5** for the anti-leakage discipline that forecloses this conflation.
1.2.2 Substitute for H_T's `WorkflowManifestEntry` schema, per-step override evaluator, or audit-ledger emission contract — **see CP-AL-5** (Meta-Architecture §7.4).
1.2.3 Define sub-agent communication protocol contracts at H_T-level — H_T cross-axis edges are typed contracts per CXA v2.1; H_E sub-agent communication is convention-based per Claude Code orchestrator-workers primitive.

---

## 2. Authority + predecessors

| Field | Value |
|---|---|
| Artifact | `Sub_Agent_Boundary_Specification_v1.md` |
| Authoring authority | `Phase_6_5_Session_6_Kickoff.md` §2.1.4 + §5.2.4 |
| Anti-leakage authority | `Phase_7_Meta_Architecture_v1.md` §7.4 (CP-axis anti-leakage rules) + §7.7 (cross-cutting anti-leakage discipline) |
| H_E surface authority | Anthropic Claude Code documentation — `code.claude.com/docs/en/sub-agents` (sub-agent orchestrator-workers primitive); accessed via `tool_search` against Claude Code H_E capability surface |
| Predecessor | `Phase_7_Meta_Architecture_v1.md` §10.2 (Phase 7 sub-phase 7b axis-stream parallelism) |
| Companion artifacts | Workspace root `CLAUDE.md` §5 (sub-agent boundary); `harness-cp/CLAUDE.md` §4.2 (CP-AL-1 citation) |

---

## 3. Sub-agent enumeration

### 3.1 Sub-agent count + responsibility mapping

Per `Phase_7_Meta_Architecture_v1.md` §10.2.3 axis-stream schedule, Phase 7 sub-phase 7b operates 4 parallel axis-streams (IS / AS / CP / OD). The sub-agent topology mirrors this axis-stream decomposition.

| Sub-agent ID | Responsibility scope | Activation window | Bounded carrier set |
|---|---|---|---|
| `sa-is` | IS-axis-stream execution | 7a exit → IS L5 (U-IS-17) lands | `harness-is/` subdirectory; 17 units U-IS-01 → U-IS-17 |
| `sa-as` | AS-axis-stream execution | IS clusters 1–3 land → AS L8 (U-AS-33) lands | `harness-as/` subdirectory; 33 units U-AS-01 → U-AS-33 |
| `sa-cp` | CP-axis-stream execution | IS clusters 1–4 + AS clusters 1–2 land → CP L8 (U-CP-55) lands | `harness-cp/` subdirectory; 55 units U-CP-01 → U-CP-55 |
| `sa-od` | OD-axis-stream execution | CP U-CP-54 lands → OD L9 (U-OD-34) lands | `harness-od/` subdirectory; 34 units U-OD-01 → U-OD-34 |
| `sa-cxa` | Cross-axis composition seam instantiation (7c sub-phase) | Per-axis terminal exporters all lands → CXA v2.1 101-edge wiring complete | `harness-cxa/` subdirectory; 5 CXA composition seams |

**Sub-agent count: 5.** Four axis-stream sub-agents (7b) + one cross-axis composition sub-agent (7c). All sub-agents operate under operator-orchestrator coordination per Claude Code orchestrator-workers primitive.

### 3.2 Sub-agent count rationale

3.2.1 **Per-axis decomposition.** The 4 axis-streams map 1:1 to the H_T design decomposition (IS / AS / CP / OD). Per-axis-stream sub-agent isolates within-axis unit consumption from cross-axis dependency complexity.

3.2.2 **Separate CXA sub-agent.** CXA seam instantiation (7c) operates against composed terminal exporters, not against in-flight per-axis units. Separating CXA from per-axis sub-agents preserves 7b → 7c sub-phase ordering and prevents premature cross-axis wiring against incomplete axis-stream substrate.

3.2.3 **No sub-agent for 7a or 7d.** Sub-phase 7a (bootstrap) operates under operator presence with no parallelism opportunity per Meta-Architecture §10.1. Sub-phase 7d (substitution retirement) operates as event-driven retirement against the self-hosting milestone gradient, not as parallel-stream execution.

### 3.3 Sub-agent count is operator-amendable

Per kickoff §2.1.4: "Sub-agent count + scope | Operator-discretion at session execution; bounded by Claude Code documented sub-agent surface." This specification commits 5 sub-agents as the architectural default. Operator may amend count + scope at Phase 7 session execution-time per Claude Code H_E capability surface. Amendments preserve the anti-leakage discipline at §5 unchanged.

---

## 4. Per-sub-agent responsibility

### 4.1 `sa-is` — IS-axis-stream sub-agent

| Property | Value |
|---|---|
| Responsibility | Execute IS-axis atomic units U-IS-01 → U-IS-17 in topological order per IS plan v2.1 §3.4 ASCII dependency graph |
| Activation | 7a exit criteria met (per Meta-Architecture §10.1.6) |
| Termination | U-IS-17 (terminal aggregate exporter) lands; coverage matrix verified per IS plan §4 |
| Working directory | `harness-is/` subdirectory |
| Canonical reference | `harness-is/CLAUDE.md` |
| Substitution authority | 9 IS-axis substitutions per Meta-Architecture §5.2 |
| Anti-leakage citation | IS-AL-1 through IS-AL-4 per Meta-Architecture §7.2 + cross-cutting X-AL-1 / X-AL-2 / X-AL-3 |

### 4.2 `sa-as` — AS-axis-stream sub-agent

| Property | Value |
|---|---|
| Responsibility | Execute AS-axis atomic units U-AS-01 → U-AS-33 in topological order per AS plan §3.5 ASCII dependency graph |
| Activation | IS clusters 1–3 (U-IS-01 → U-IS-10) land per Meta-Architecture §10.2.3 |
| Termination | U-AS-33 (terminal aggregate exporter) lands; coverage matrix verified per AS plan §4 |
| Working directory | `harness-as/` subdirectory |
| Canonical reference | `harness-as/CLAUDE.md` |
| Substitution authority | 6 AS-axis substitutions per Meta-Architecture §5.3 |
| Anti-leakage citation | AS-AL-1 through AS-AL-4 per Meta-Architecture §7.3 + cross-cutting X-AL-1 / X-AL-2 / X-AL-3 |

### 4.3 `sa-cp` — CP-axis-stream sub-agent

| Property | Value |
|---|---|
| Responsibility | Execute CP-axis atomic units U-CP-01 → U-CP-55 in topological order per CP plan §3.4 Kahn execution sequence |
| Activation | IS clusters 1–4 + AS clusters 1–2 land per Meta-Architecture §10.2.3 |
| Termination | U-CP-55 (terminal aggregate exporter; F2-12 cascade Step 6a closure record carrier) lands; coverage matrix verified per CP plan §4 |
| Working directory | `harness-cp/` subdirectory |
| Canonical reference | `harness-cp/CLAUDE.md` |
| Substitution authority | 21 CP-axis substitutions per Meta-Architecture §5.4 (**largest substitution load**) |
| Anti-leakage citation | **CP-AL-1 (verbatim at §5 below) + CP-AL-2 + CP-AL-3 + CP-AL-4 + CP-AL-5** per Meta-Architecture §7.4 + cross-cutting X-AL-1 / X-AL-2 / X-AL-3 |

### 4.4 `sa-od` — OD-axis-stream sub-agent

| Property | Value |
|---|---|
| Responsibility | Execute OD-axis atomic units U-OD-01 → U-OD-34 in topological order per OD plan §3 dependency graph |
| Activation | CP U-CP-54 lands per Meta-Architecture §10.2.3 |
| Termination | U-OD-34 (terminal aggregate exporter) lands; coverage matrix verified per OD plan §4 |
| Working directory | `harness-od/` subdirectory |
| Canonical reference | `harness-od/CLAUDE.md` |
| Substitution authority | 8 OD-axis substitutions per Meta-Architecture §5.5 |
| Anti-leakage citation | OD-AL-1 + OD-AL-2 + OD-AL-3 per Meta-Architecture §7.5 + cross-cutting X-AL-1 / X-AL-2 / X-AL-3 |

### 4.5 `sa-cxa` — Cross-axis composition sub-agent

| Property | Value |
|---|---|
| Responsibility | Instantiate CXA v2.1 cross-axis composition seams across 6 composition buckets (101 typed edges) |
| Activation | All 4 axis-stream sub-agents complete; per-axis terminal exporters (U-IS-17, U-AS-33, U-CP-55, U-OD-34) all land |
| Termination | All 101 CXA edges wired with byte-exact alignment per CXA v2.1 §2.3 Pattern P1; 5 CXA composition seams operational |
| Working directory | `harness-cxa/` subdirectory |
| Canonical reference | `Cross_Axis_Composition_Document_v2_1.md` (design-phase workspace) |
| Substitution authority | 5 CXA-axis substitutions per Meta-Architecture §5.6 |
| Anti-leakage citation | CXA-AL-1 per Meta-Architecture §7.6 + cross-cutting X-AL-1 / X-AL-2 / X-AL-3 |

---

## 5. Anti-leakage citation — CP-AL-1 verbatim

Per `Phase_6_5_Session_6_Kickoff.md` §5.2.4: "Sub-agent boundary specification MUST cite anti-leakage rule CP-AL-1 (Claude Code sub-agent topology ≠ H_T CP-axis topology) verbatim or per `Phase_7_Meta_Architecture_v1.md` §7 citation-only grammar per §7.4.4."

### 5.1 CP-AL-1 verbatim (per Meta-Architecture §7.4)

> **CP-AL-1.** H_E sub-agent topology (orchestrator-workers via `Agent` tool) ≠ H_T TopologyPattern 6-class enum (ORCHESTRATOR_WORKERS / DECENTRALIZED_HANDOFF / EVALUATOR_OPTIMIZER / PARALLELIZATION / ROUTING / SEQUENTIAL_PIPELINE)
>
> *Anti-pattern foreclosed:* Concluding "we already have orchestrator-workers" implies H_T-CP-10 is met

### 5.2 Application to this specification

5.2.1 The 5 sub-agents declared at §3 are **H_E sub-agents** (orchestrator-workers via Claude Code's `Agent` tool primitive). They are NOT instantiations of H_T's TopologyPattern 6-class enum.

5.2.2 The H_E sub-agent orchestrator-workers pattern at this workspace coincidentally maps to the ORCHESTRATOR_WORKERS value of H_T's TopologyPattern enum. **This coincidence does not satisfy H_T-CP-10.** H_T-CP-10 requires the full 6-class enum + admissibility predicate + CascadePolicy per C-CP-10 §10, all of which are H_T contracts implemented at U-CP-22 (CP plan v2.3 Cluster 4).

5.2.3 The 5 sub-agents declared at §3 do NOT substitute for any H_T TopologyPattern primitive. Substitution retirement at U-CP-22 landing applies to H_T-CP-10 only; the H_E sub-agents at this workspace remain active as H_E execution-time scaffolding regardless of H_T-CP-10 status (the H_E sub-agents are not subject to retirement criterion at §6 — they exist for the duration of Phase 7 workspace lifetime).

5.2.4 **The H_T TopologyPattern 6-class enum operates at H_T runtime, not at Phase 7 build-time.** H_T workflow topology decisions (which TopologyPattern value a workflow uses) happen when H_T is executing user workflows — Phase 7 build-time decisions are H_E orchestration decisions, not H_T topology decisions.

### 5.3 Related anti-leakage rules

CP-AL-1 is the most-direct anti-leakage application at this specification, but the following rules also bind:

| Rule | Binding at this specification |
|---|---|
| CP-AL-5 | `CLAUDE.md` declarations (this spec + per-axis `CLAUDE.md`) are H_E sub-agent scaffolding; NOT H_T's typed `WorkflowManifestEntry` schema |
| X-AL-1 | Sub-agents do NOT cross the MCP server boundary. The H_E ↔ H_T substrate boundary lives at the MCP server process; H_E sub-agents operate on the H_E side; H_T-authored code (eventually) operates on the H_T side |
| X-AL-3 | Sub-agents implementing per-axis atomic units MUST NOT silently extend H_T design. New H_T primitives surfaced at sub-agent execution-time route to design-phase back-flow (Class 1 fork) before implementation proceeds |

---

## 6. Per-sub-agent scope boundaries against the 4 axes

### 6.1 Within-axis scope discipline

Each axis-stream sub-agent (§4.1 → §4.4) operates EXCLUSIVELY within its declared axis subdirectory:

| Sub-agent | Working dir | DOES execute | DOES NOT execute |
|---|---|---|---|
| `sa-is` | `harness-is/` | U-IS-01 → U-IS-17 | Any U-AS / U-CP / U-OD unit |
| `sa-as` | `harness-as/` | U-AS-01 → U-AS-33 | Any U-IS / U-CP / U-OD unit |
| `sa-cp` | `harness-cp/` | U-CP-01 → U-CP-55 | Any U-IS / U-AS / U-OD unit |
| `sa-od` | `harness-od/` | U-OD-01 → U-OD-34 | Any U-IS / U-AS / U-CP unit |

### 6.2 Cross-axis dependency handling

When an axis-stream sub-agent encounters a cross-axis dependency (e.g., `sa-as` encounters U-AS-19 which depends on `U-IS-07 (cross-axis: IS)`), the sub-agent:

6.2.1 **READS** the cross-axis dependency's substrate from the dependency's terminal exporter manifest (e.g., U-IS-17 substrate seam exports manifest for IS-axis exports).
6.2.2 **DOES NOT** execute the cross-axis dependency's atomic unit — that unit is owned by the other axis-stream sub-agent.
6.2.3 **VERIFIES** the cross-axis dependency landed before proceeding with the dependent within-axis unit.

This discipline is enforced by the axis-stream activation ordering at §3.1: cross-axis dependencies always land before the consuming sub-agent activates.

### 6.3 CXA seam instantiation scope

`sa-cxa` (§4.5) operates against ALL 4 per-axis subdirectories at 7c sub-phase. The CXA sub-agent activates ONLY after all 4 axis-stream sub-agents complete (per §3.1 activation window). CXA seam instantiation reads terminal exporter manifests from all 4 axes; it does NOT execute any per-axis atomic unit.

### 6.4 Out-of-scope actions

The following actions are OUT OF SCOPE for any sub-agent declared at §3:

6.4.1 H_T design extension (X-AL-3 forecloses this).
6.4.2 ADR / spec / plan / ADD / PRD revision (these are design-phase artifacts at design-phase workspace; Phase 7 forks route to design-phase back-flow per workspace root `CLAUDE.md` §4.3).
6.4.3 Workflow governance revision (`Project_Workflow_v1_8.md` is canonical at design-phase workspace).
6.4.4 H_E configuration changes (user-level `~/.claude/` config is operator-domain, not sub-agent-domain).
6.4.5 Cross-sub-agent direct coordination (sub-agents coordinate via the operator-orchestrator, not peer-to-peer; this is consistent with Claude Code orchestrator-workers primitive).

---

## 7. Sub-agent lifecycle + process boundary discipline

### 7.1 Lifecycle phases

| Phase | Description | Operator presence |
|---|---|---|
| Initialization | Sub-agent spawned per Claude Code orchestrator-workers primitive; working directory set; canonical reference loaded | Required |
| Active execution | Sub-agent consumes per-axis atomic units in topological order; per-unit acceptance criteria + tests + coverage matrix updated | Per Meta-Architecture §10.2.5 + §10.2.6 (operator confirmation per cluster close) |
| Termination | Sub-agent completes terminal aggregate exporter unit; coverage matrix verified; sub-agent state surfaced to operator | Required |

### 7.2 Process boundary discipline

7.2.1 **H_E sub-agents operate within the H_E process boundary.** Sub-agents do NOT cross the MCP server boundary per X-AL-1 (Meta-Architecture §7.7). Sub-agents at this workspace are H_E-process-resident; H_T primitives (eventually) operate at MCP server processes spawned by H_T-authored harness code.

7.2.2 **Concurrent sub-agent execution preserves substrate isolation.** When multiple axis-stream sub-agents execute in parallel per §3.1 activation windows, each operates against its own working directory. Cross-axis substrate access is read-only via terminal exporter manifests.

7.2.3 **Sub-agent state is ephemeral.** Sub-agent state at sub-agent termination is captured at:
   - Within-axis: per-axis plan progress + coverage matrix updates
   - Cross-axis: terminal exporter manifest content
   
   No sub-agent "memory" persists across Phase 7 sessions beyond what's captured at the canonical artifacts (per-axis plans + CXA composition document).

### 7.3 Back-flow routing from sub-agents

When a sub-agent encounters a Class 1 fork (design-phase artifact defect; see workspace root `CLAUDE.md` §4.3), the sub-agent:

7.3.1 **HALTS** within-axis execution at the current atomic unit.
7.3.2 **SURFACES** the defect to the operator with class disposition + routing target (Phase 6 plan / Phase 5 spec / Phase 3a/3b ADR / Phase 3d ADD / Phase 4 PRD / Workflow revision).
7.3.3 **DOES NOT** proceed past the halt point until the design-phase artifact is re-issued at re-clearance.
7.3.4 **DOES NOT** silently absorb the defect (X-AL-3 forecloses this).

The `phase-7-back-flow-routing` skill at `<workspace_root>/.claude/skills/` governs fork detection discipline at sub-agent execution-time.

---

## 8. Operator-orchestrator coordination

### 8.1 Operator-orchestrator role

The operator-orchestrator (operator + Claude Code main session) coordinates sub-agent activation, per-cluster confirmation, and cross-axis transition. Per Meta-Architecture §10.2.4 per-cluster traversal pattern:

```
Operator authorizes cluster open (ask_user_input_v0)
  ↓
Sub-agent executes cluster units in topological order
  ↓
Per unit: implementation + acceptance tests + coverage matrix update + traceability cross-reference
  ↓
Cluster coherence pass (implementation-planner SKILL.md §6 5-dimension audit)
  ↓
Operator confirms cluster close
  ↓
Cluster substrate exposed at axis-level surface
```

### 8.2 Per-cluster confirmation cadence

Per Meta-Architecture §10.2.4: operator confirmation REQUIRED at each cluster boundary. Sub-agents do NOT cross cluster boundaries without operator confirmation. This is the canonical 7b operator-presence discipline.

### 8.3 Cross-sub-agent coordination

Sub-agents coordinate ONLY via the operator-orchestrator (per Claude Code orchestrator-workers primitive). Direct sub-agent-to-sub-agent coordination is OUT OF SCOPE per §6.4.5. Cross-axis substrate access happens via terminal exporter manifests (read-only) per §6.2.

---

## 9. Filing footer

| Field | Value |
|---|---|
| Artifact | `Sub_Agent_Boundary_Specification_v1.md` |
| Authored at | Phase 6.5 Session 6 (ε), 2026-05-15 |
| Authoring authority | `Phase_6_5_Session_6_Kickoff.md` §2.1.4 + §5.2.4 |
| Anti-leakage authority | `Phase_7_Meta_Architecture_v1.md` §7.4 (CP-AL-1) + §7.7 (X-AL-1 / X-AL-2 / X-AL-3) |
| Predecessor | `Phase_7_Meta_Architecture_v1.md` §10.2 (Phase 7 sub-phase 7b axis-stream parallelism) |
| Successor consumption | Phase 7 Session 1 onward (this workspace) |
| Revision policy | This file is canonical for this workspace; revisions route to design-phase back-flow per workspace root `CLAUDE.md` §4.3 |

---

*End of `Sub_Agent_Boundary_Specification_v1.md`. Parent guidance at workspace root `CLAUDE.md` §5 (sub-agent boundary). CP-AL-1 anti-leakage authority at `Phase_7_Meta_Architecture_v1.md` §7.4 (design-phase workspace).*
