# Phase 7 Session 1 Entry Directive — v1

*Workspace-level entry artifact for Phase 7 Session 1 at the new Claude Code CLI workspace. Loaded at session open. Authorizes Phase 7 sub-phase 7a (Bootstrap) execution. Authored at Phase 6.5 Session 7 (β); filed at the new workspace root per `Phase_6_5_Session_7_Kickoff.md` §2.1.2 handoff package.*

---

## §1 Session identity

### §1.1 Status block

| Field | Value |
|---|---|
| Artifact | `Phase_7_Session_1_Entry_Directive_v1.md` |
| Phase | Phase 7 — Implementation Execution |
| Sub-phase | 7a — Bootstrap |
| Session number | 1 of N (Phase 7 sub-phase 7a session count operator-discretion) |
| Workspace target | **New Claude Code CLI workspace** (DP-4 separate-workspace discipline per `Project_Workflow_v1_8.md` §2.7.2) |
| Authoring authority | `Phase_6_5_Session_7_Kickoff.md` §2.1; Phase 6.5 arc-completion criterion 7 per Workflow v1.8 §2.6.5.4 |
| Predecessor | `Phase_6_5_Session_7_Close_Handoff.md` (Phase 6.5 arc closure record); bootstrap substrate (10 artifacts) operator-pushed at Phase 6.5 Session 7 (β) close |
| Successor | Phase 7 Session 1 close handoff (authored at Session 1 close per session pattern carried forward from Phase 6.5) |
| Filing destination | `<new_workspace_root>/Phase_7_Session_1_Entry_Directive_v1.md` |

### §1.2 Authority chain

Per workspace root `CLAUDE.md` §1.3:

```
ADR (F1–F5 + D1–D6)
  → ADD v1.3
    → PRD v1.1
      → per-axis spec (IS v1.2 / AS v1.1 / CP v1.3 / OD v1.3)
        → per-axis plan (IS v2.2 / AS v1 / CP v2.3 / OD v2.4) + CXA v2.1
          → Phase 7 implementation [THIS SESSION OPERATES HERE]
```

Earlier artifacts in the chain are canonical for later artifacts. Conflicts route to `phase-7-back-flow-routing` skill per §8.

### §1.3 Two-harness framing

Per `Phase_7_Meta_Architecture_v1.md` §1 (canonical resolution of chicken-and-egg paradox):

| Harness | Role | Surface |
|---|---|---|
| **H_T** (target harness) | The multi-LLM agent harness being built per the v2.x plans + CXA v2.1 | Implementation work-product of Phase 7 |
| **H_E** (execution harness) | Claude Code CLI hosting the build | Development environment + bounded substitutions for not-yet-built H_T primitives |

**H_E patterns MUST NOT leak into H_T implementation.** Anti-leakage discipline binds from this directive's filing onward per §8.

---

## §2 Substrate inventory

### §2.1 Workspace-resident substrate (10 bootstrap artifacts)

Authored at Phase 6.5 Session 6 (ε) per `Phase_6_5_Session_6_Close_Handoff.md` §4.1. Operator-pushed to this workspace at Phase 6.5 Session 7 (β) close.

| # | Artifact | Workspace path | Role |
|---|---|---|---|
| 1 | `CLAUDE.md` (root) | `<workspace_root>/CLAUDE.md` | Workspace-level guidance; canonical pointer to design-phase artifacts; 9 sections |
| 2 | `harness-is/CLAUDE.md` | `<workspace_root>/harness-is/CLAUDE.md` | IS-axis guidance; 5 sections; 9 substitution surface entries |
| 3 | `harness-as/CLAUDE.md` | `<workspace_root>/harness-as/CLAUDE.md` | AS-axis guidance; 5 sections; 6 substitution surface entries |
| 4 | `harness-cp/CLAUDE.md` | `<workspace_root>/harness-cp/CLAUDE.md` | CP-axis guidance; 5 sections; 21 substitution surface entries (largest substitution load) |
| 5 | `harness-od/CLAUDE.md` | `<workspace_root>/harness-od/CLAUDE.md` | OD-axis guidance; 5 sections; 8 substitution surface entries |
| 6 | `Sub_Agent_Boundary_Specification_v1.md` | `<workspace_root>/Sub_Agent_Boundary_Specification_v1.md` | Sub-agent count (5) + per-sub-agent responsibility + activation sequence + anti-leakage citation; 9 sections |
| 7 | `phase-7-implementation/SKILL.md` | `<workspace_root>/.claude/skills/phase-7-implementation/SKILL.md` | Sub-phase 7b atomic unit consumption discipline; 8 sections |
| 8 | `phase-7-cross-axis-composition/SKILL.md` | `<workspace_root>/.claude/skills/phase-7-cross-axis-composition/SKILL.md` | Sub-phase 7c CXA seam instantiation; 8 sections |
| 9 | `phase-7-substitution-retirement/SKILL.md` | `<workspace_root>/.claude/skills/phase-7-substitution-retirement/SKILL.md` | Cross-sub-phase substitution retirement event discipline; 9 sections |
| 10 | `phase-7-back-flow-routing/SKILL.md` | `<workspace_root>/.claude/skills/phase-7-back-flow-routing/SKILL.md` | Cross-sub-phase fork detection + design-phase routing; 7 sections |

**Workspace skill activation.** Project-level skills at `.claude/skills/` take precedence over user-level skills at `~/.claude/skills/` on name collision per Anthropic Claude Code skill-directory precedence convention. Per OD-ε-2 (operator decision at Phase 6.5 Session 6).

### §2.2 Cross-workspace substrate (design-phase workspace canonical references)

All canonical design-phase artifacts reside at the **design-phase workspace** (Claude.ai project; not co-resident with this workspace). Each Phase 7 session opens by reading required design-phase artifacts via cross-workspace reference per arc manifest §6 each-session opening read pattern. Citation byte-exact discipline per `Project_Workflow_v1_8.md` §7.4.2.

#### §2.2.1 Architectural Decision Records (11)

| ADR | Canonical version | Role |
|---|---|---|
| ADR-F1 | v1.2 | Provider portability (multi-LLM commitment) |
| ADR-F2 | v1.2 | State ledger substrate |
| ADR-F3 | v1.1 | Engine event history |
| ADR-F4 | v1.1 | Workspace + Git substrate |
| ADR-F5 | v1.1 | Skills filesystem |
| ADR-D1 | v1.2 | Engine + replay |
| ADR-D2 | v1.1 | Sandbox + blast radius |
| ADR-D3 | v1.2 | Filesystem residence |
| ADR-D4 | v1.1 | Workload classes |
| ADR-D5 | v1.3 | Cross-deployment monotonicity + HITL palette |
| ADR-D6 | v1.2 | Observability + cost-attribution |

#### §2.2.2 Consolidated design + requirements artifacts (3)

| Artifact | Version | Role |
|---|---|---|
| `Architectural_Design_Document_v1_3.md` | v1.3 | ADR consolidation |
| `PRD_v1_1.md` | v1.1 | Product requirements |
| `Cross_Axis_Composition_Document_v2_1.md` | v2.1 | 101 typed cross-axis edges across 6 composition buckets |

#### §2.2.3 Per-axis specifications (4)

| Spec | Canonical version | Contract count |
|---|---|---|
| `Spec_Information_Substrate_v1.md` | v1.2 (per ADD v1.3 attestation) | 10 (C-IS-01 → C-IS-10) |
| `Spec_Action_Surface_v1.md` | v1.1 | 16 (C-AS-01 → C-AS-16) |
| `Spec_Control_Plane_v1_3.md` | v1.3 | 24 (C-CP-01 → C-CP-24) |
| `Spec_Operational_Discipline_v1_3.md` | v1.3 | 23 (C-OD-01 → C-OD-23) |

#### §2.2.4 Per-axis implementation plans (4)

| Plan | Canonical version | Unit count | Cluster count |
|---|---|---|---|
| `Implementation_Plan_Information_Substrate_v2_2.md` | v2.2 (F3-02 closure record over v2.1) | 17 (U-IS-01 → U-IS-17) | 6 |
| `Implementation_Plan_Action_Surface_v1.md` | v1 | 33 (U-AS-01 → U-AS-33) | 9 |
| `Implementation_Plan_Control_Plane_v2_3.md` | v2.3 | 55 (U-CP-01 → U-CP-55) | 9 |
| `Implementation_Plan_Operational_Discipline_v2_4.md` | v2.4 (F3-02 closure + C3-15 Path (i-refined) absorption over v2.3) | 34 (U-OD-01 → U-OD-34) | 8 |

**H_T atomic unit aggregate: 139 units across 32 clusters.**

#### §2.2.5 Phase 7 governance substrate (6)

| Artifact | Role |
|---|---|
| `Project_Workflow_v1_8.md` | Canonical workflow at v1.8; §2.7 Phase 7 internal workflow |
| `Phase_7_Meta_Architecture_v1.md` | Chicken-and-egg paradox resolution; 49-row substitution mapping; 18-rule anti-leakage discipline; 4-sub-phase enumeration |
| `Phase_7_Kickoff_Prompt.md` | Portable Phase 7 kickoff (legacy framing; superseded for Session 1 by this directive) |
| `Target_Stack_Commitment_v1.md` | Committed stack: Python 3.12+ / Pydantic v2 / asyncio / uv / pyright / ruff / pytest / per-provider SDKs |
| `Plan_Executability_Audit_v1.md` | Framework-pull discipline: hand-rolled retry / breaker / idempotency; NO LiteLLM / langgraph / temporal / prefect / tenacity / pybreaker |
| `Canonical_Substrate_Inventory.md` | KB navigation anchor; updated at session close to reflect Class 3 informational items |

#### §2.2.6 Phase 6.5 arc artifacts (16)

| Artifact family | Count | Role |
|---|---|---|
| Phase 6.5 Session kickoff prompts | 7 | Sessions 1–7 entry artifacts |
| Phase 6.5 Session close handoffs | 7 | Sessions 1–7 close records |
| `Phase_6_5_Pre_Transition_Arc_Manifest.md` | 1 | Arc-level framing + sequence context |
| `Project_Workflow_Revision_log_v1_8_Entry.md` | 1 | Workflow v1.7 → v1.8 revision record |

**Cross-workspace substrate aggregate: 44+ canonical artifacts** (excluding adversarial reviews, ADR variants, integration verification reports, and pre-Phase-6.5 close handoffs which remain at design-phase workspace as archival substrate).

### §2.3 Substrate read protocol at each Phase 7 session open

| Step | Action | Source |
|---|---|---|
| 1 | Read workspace `CLAUDE.md` | `<workspace_root>/CLAUDE.md` |
| 2 | Read sub-phase-specific per-axis `CLAUDE.md` (per active sub-agent) | `<workspace_root>/harness-{is,as,cp,od}/CLAUDE.md` |
| 3 | Read `Sub_Agent_Boundary_Specification_v1.md` | `<workspace_root>/` |
| 4 | Load Phase 7-specific skills via `tool_search` per Claude Code activation surface | `<workspace_root>/.claude/skills/` |
| 5 | Read sub-phase-specific Meta-Architecture section (7a→§10.1, 7b→§10.2, 7c→§10.3, 7d→§10.4) | Design-phase workspace |
| 6 | Read sub-phase-specific design-phase artifacts (per session task) | Design-phase workspace |

---

## §3 Entry-gate verification for sub-phase 7a

Per `Phase_7_Meta_Architecture_v1.md` §10.1.4 (7 criteria):

| # | Criterion | Verification status at this directive |
|---|---|---|
| 1 | Target stack committed (`Target_Stack_Commitment_v1.md` canonical) | ✅ Filed at Phase 6.5 Session 1 (δ) close 2026-05-14; canonical at design-phase workspace |
| 2 | Claude Code CLI workspace operational under DP-4 separate-workspace discipline | ✅ This workspace is the DP-4 fork target; operational at this directive's loading |
| 3 | `Phase_7_Session_1_Entry_Directive.md` filed (Session 7 β output) | ✅ This artifact (filing target = `<workspace_root>/`) |
| 4 | Claude Code CLI bootstrap substrate landed (Session 6 ε output) | ✅ 10 artifacts at workspace per §2.1 |
| 5 | v2.2 / v1 / v2.3 / v2.4 plans + CXA v2.1 + ADD v1.3 + PRD v1.1 + canonical ADRs + specs accessible | ✅ Accessible via cross-workspace reference to design-phase workspace per §2.2 |
| 6 | `Phase_7_Meta_Architecture_v1.md` accessible | ✅ Accessible via cross-workspace reference per §2.2.5 |
| 7 | No open Class 1 / Class 2 forks from Phase 6.5 arc close | ✅ Verified at `Phase_6_5_Session_7_Close_Handoff.md` §[arc closure status] |

**Result: 7/7 entry-gate criteria CLEARED. Sub-phase 7a entry authorized.**

---

## §4 7a sub-phase activation

### §4.1 7a goal statement

Per `Phase_7_Meta_Architecture_v1.md` §10.1.1 (verbatim citation):

> Operational substrate scaffolding plus L0 design declarations across all axes. §5 substitutions stable and invocable. Harness executes a trivial workload end-to-end through substituted primitives.

### §4.2 7a operative boundary

Per OD-S4-4.A (Phase 6.5 Session 4 segment-boundary decision; recorded at `Phase_6_5_Session_4_Close_Handoff.md` §4.1):

> **Pragmatic** (7a operational minimum including L1–L2 units)
>
> *Rationale:* pure topological yields 7a not operationally bootable; operator-presence-gradient inverts organizing principle.

7a is NOT defined by topological level (L0-only); 7a is defined by **operational minimum to execute the canonical-workload smoke test** per Meta-Architecture §10.1.6. This includes some L0 anchors plus L1–L2 units required for substitution scaffolding to be invocable.

### §4.3 7a activation declaration

The following sub-phase 7a surfaces are **ACTIVATED** at this directive's filing:

| Surface | Activation state | Reference |
|---|---|---|
| Sub-phase 7a entry | OPEN | This directive §3 entry-gate verification 7/7 CLEARED |
| §6 substitution scaffolding (9 surfaces) | INVOCABLE | Per Meta-Architecture §10.1.3; this directive §6 declares each surface |
| Sub-agent topology (5 sub-agents) | DEFERRED to per-sub-agent activation windows | Per `Sub_Agent_Boundary_Specification_v1.md` §3.1; this directive §7 enumerates — see §4.4 below for 7a-specific posture |
| 4 Phase 7-specific skills | TOOL-SEARCH-DISCOVERABLE | Per `.claude/skills/` activation surface; this directive §7 enumerates |
| Anti-leakage discipline (18 axis-rules + 3 cross-cutting) | BINDING | Per Meta-Architecture §7; this directive §8 binds |
| Back-flow routing to design-phase workspace | ACTIVE | Per workspace root `CLAUDE.md` §4.3 + `phase-7-back-flow-routing` skill |

### §4.4 7a sub-agent posture

Per `Sub_Agent_Boundary_Specification_v1.md` §3.2.3 (verbatim):

> **No sub-agent for 7a or 7d.** Sub-phase 7a (bootstrap) operates under operator presence with no parallelism opportunity per Meta-Architecture §10.1.

**7a sub-agent topology: ZERO sub-agents instantiated.** All 7a unit landings (per §5) execute under the operator-orchestrator (Claude Code primary instance), not under delegated sub-agents. Sub-agent topology activates at sub-phase 7b entry per `Sub_Agent_Boundary_Specification_v1.md` §3.1 activation windows.

### §4.5 7a first action (Session 1 immediate)

At this directive's loading, Phase 7 Session 1 executes the following sequence:

```
7a Session 1 immediate action sequence:
─────────────────────────────────────────────────────────────────
  1. Load workspace `CLAUDE.md` (this directive's §2.3 read protocol)
  2. Load Meta-Architecture §10.1 (7a sub-phase canonical)
  3. Load Workflow v1.8 §2.7 (Phase 7 internal workflow)
  4. Verify 7a entry-gate (per §3 above; already cleared at directive filing)
  5. Proceed to substantive 7a Session 1 task:
     ─ Confirm session task scope (e.g., first unit landing batch
       per §5 unit landings table)
     ─ Begin substrate scaffolding instantiation per §6 substitution
       scaffolding declaration
```

### §4.6 7a session pacing

Per `Phase_7_Meta_Architecture_v1.md` §10.1.8 reduced-HITL viability assessment for sub-phase 7a:

| Property | Value |
|---|---|
| HITL viability at 7a | **HIGH** — operator-presence-intensive |
| Rationale | Substitution scaffolding decisions, MCP server boundary establishment, first unit landings each require operator confirmation; no reduced-HITL automation surface |
| Estimated session count for 7a closure | Operator-discretion; bounded by 7a exit criteria (§5.4 — per Meta-Architecture §10.1.5) |
| Session pattern | Per-cluster confirmation cadence per `ask_user_input_v0` tappable single-select menus (consistent with Phase 6.5 session pattern carried forward) |

7a Session 1 does not target 7a closure. 7a closure requires all 6 exit criteria satisfied (§5.4 — per Meta-Architecture §10.1.5).

---

## §5 7a execution mechanics — unit landings, cadence, exit criteria

### §5.1 L0 inventory vs 7a unit landings disambiguation

Two distinct concepts share citation surface; this section separates them:

| Concept | Source | Count | Semantic role |
|---|---|---|---|
| L0 entry-point inventory | Per-axis `CLAUDE.md` §3 | 23 (IS=5 / AS=3 / CP=13 / OD=2) | Full in-degree-0 inventory across axis DAGs; **7b axis-stream activation surface** for sa-is / sa-as / sa-cp / sa-od (NOT the 7a landing set) |
| 7a unit landings | `Phase_7_Meta_Architecture_v1.md` §10.1.2 | 12 (IS=4 / AS=4 / CP=2 / OD=2) | Pragmatic operational-minimum per OD-S4-4.A; **the actual 7a landing target** — includes some L0 anchors + some L1–L2 units required for substitution scaffolding |

**Operative discipline at 7a.** Land the 12-unit operational minimum per §5.2. The 23-unit L0 inventory becomes operative at 7b axis-stream entry per `Sub_Agent_Boundary_Specification_v1.md` §3.1.

### §5.2 7a unit landings (12 units; 8.6% of 139)

Per `Phase_7_Meta_Architecture_v1.md` §10.1.2 (verbatim):

| Axis | Units landed at 7a | Topological level | Rationale |
|---|---|---|---|
| IS | U-IS-01, U-IS-02, U-IS-03, U-IS-04 | L0, L1, L0, L0 | Path/tier registries + git-tier substrate (foundational substrate primitives for state ledger residence + worktree isolation) |
| AS | U-AS-01, U-AS-02, U-AS-03, U-AS-04 | L0, L1, L0, L0 | SandboxTier + tier-monotonicity + SandboxFailClass + DeploymentSurface/PersonaTier/MCPTransport enums (foundational AS enum substrate consumed by 6 of 7 L1 units) |
| CP | U-CP-15, U-CP-22 | L0, L0 | EngineClass 5-class enum + TopologyPattern 6-class enum (foundational CP taxonomies) |
| OD | U-OD-01, U-OD-04 | L0, L0 | Foundational cost-attribution primitive + foundational telemetry primitive |
| **Aggregate** | **12 units** | — | — |

### §5.3 Per-unit confirmation cadence at 7a

Per `Phase_7_Meta_Architecture_v1.md` §10.1 (7a operator-presence intensive) + `Sub_Agent_Boundary_Specification_v1.md` §8.2 (per-cluster confirmation pattern from §10.2.4, adapted for 7a per-unit grain):

```
Operator authorizes unit landing (ask_user_input_v0)
        │
        ▼
H_T-authored implementation at MCP server boundary
        │
        │  • Pydantic v2 typed schemas
        │  • Acceptance test materialization (per plan §1 per-unit acceptance criteria)
        │  • State ledger entry append (per substitution scaffolding §6.2 row 2)
        │  • Traceability cross-reference (spec contract C-{IS,AS,CP,OD}-NN)
        │
        ▼
Per-unit coherence verification
        │
        │  • Acceptance tests pass
        │  • Cross-axis dependencies (where applicable) resolve to landed substrate
        │  • Anti-leakage rules per axis hold (no H_E surface inversion)
        │
        ▼
Operator confirms unit close (terse confirmation cadence)
        │
        ▼
Next unit eligible for landing
```

**7a cadence vs 7b cadence.** 7a operates at per-unit grain (12 isolated landings); 7b operates at per-cluster grain (full intra-axis cluster traversal per Meta-Architecture §10.2.4). The 7a → 7b transition shifts cadence at sub-phase boundary per `Sub_Agent_Boundary_Specification_v1.md` §3.1 sa-is activation window.

### §5.4 7a exit criteria

Per `Phase_7_Meta_Architecture_v1.md` §10.1.5 (verbatim):

| # | Criterion | Verification mechanism |
|---|---|---|
| 1 | All 12 L0/L1–L2 operational-minimum units land with acceptance tests passing | Per-unit pytest pass at each unit close |
| 2 | All §10.1.3 substitution mechanisms invocable end-to-end (canonical-workload smoke test) | §5.5 smoke test execution |
| 3 | MCP server hosts ≥ 3 representative tools per axis (≥ 12 total) with strict Pydantic v2 validation | MCP server enumeration + Pydantic v2 schema verification |
| 4 | State ledger writes succeed under substitution; hash-chain verification readable via `Bash(jq + python)` | `.harness/state.jsonl` parse + SHA-256 chain verification |
| 5 | OTel emission visible at MCP server boundary; consumed by Collector subprocess; sqlite ring-buffer populated | OTLP Collector subprocess + sqlite query verification |
| 6 | 7a close handoff filed at execution workspace | Filing verification at `<workspace_root>/Phase_7_Session_N_Close_Handoff.md` |

### §5.5 Canonical-workload smoke test (7a exit criterion #2)

Per `Phase_7_Meta_Architecture_v1.md` §10.1.6 (verbatim):

```
INPUT:  "Read README.md, summarize it in 3 bullets, write summary to /tmp/summary.md,
         and append a state ledger entry recording the operation."

EXPECTED BEHAVIOR:
  1.  main session ──> Agent spawn ──> sub-agent context
  2.  sub-agent ──> MCP harness.read_file("README.md")       [H_T-AS-2 substitution]
  3.  MCP server ──> Bash(cat README.md)
  4.  MCP server ──> emit files.read.completed span          [H_T-AS-8 substitution]
  5.  sub-agent ──> probabilistic summarization (LLM)        [H_T-CP-1 substitution]
  6.  sub-agent ──> MCP harness.write_file(summary.md, ...)
  7.  MCP server ──> Bash(write file) + emit span
  8.  sub-agent ──> MCP harness.append_state_ledger(...)     [H_T-IS-5 substitution]
  9.  MCP server ──> Bash(cat <<EOF >> .harness/state.jsonl)
  10. MCP server ──> compute SHA-256 chain via python stdlib  [H_T-IS-6 substitution]
  11. OTel Collector ingests all 4 spans into sqlite

VERIFICATION GATES:
  - State ledger entry parseable; idempotency_key + response_hash + prior_event_hash present
  - All 4 spans queryable from sqlite ring-buffer
  - Sub-agent returns summary matching README structure
  - No H_E built-in tool invoked outside MCP server boundary (per X-AL-1)
```

### §5.6 7a reduced-HITL viability

Per `Phase_7_Meta_Architecture_v1.md` §10.1.8:

| Property | Value |
|---|---|
| HITL viability | **HIGH** (operator-presence-intensive throughout 7a) |
| Overnight-executable surfaces | None at 7a |
| Estimated session count | 5–8 sessions at moderate density |
| Session 1 scope target | Substrate scaffolding instantiation + first unit landing(s) at operator discretion; does NOT target 7a closure |

---

## §6 Substitution scaffolding declaration

### §6.1 Substitution mapping aggregate (49 entries across 5 surfaces)

Per `Phase_7_Meta_Architecture_v1.md` §5 (per-axis breakdown):

| Axis | Substitutions | Source | Authority |
|---|---|---|---|
| IS | 9 | Meta-Architecture §5.2 | `harness-is/CLAUDE.md` §4.1 |
| AS | 6 | Meta-Architecture §5.3 | `harness-as/CLAUDE.md` §4.1 |
| CP | 21 (largest substitution load; 42.9%) | Meta-Architecture §5.4 | `harness-cp/CLAUDE.md` §4.1 |
| OD | 8 | Meta-Architecture §5.5 | `harness-od/CLAUDE.md` §4.1 |
| CXA | 5 | Meta-Architecture §5.6 | `phase-7-cross-axis-composition/SKILL.md` §6 |
| **Aggregate** | **49** | — | — |

### §6.2 7a substitution scaffolding (9 invocable surfaces)

Per `Phase_7_Meta_Architecture_v1.md` §10.1.3 — established at sub-phase 7a entry; INVOCABLE for canonical-workload smoke test per §5.5:

| # | Scaffolding surface | Mechanism | Substitution authority |
|---|---|---|---|
| 1 | Path conventions | `CLAUDE.md` declares 4-class path semantics | H_T-IS-1 (path-class registry); harness-is/CLAUDE.md §1.3 |
| 2 | State ledger | `.harness/state.jsonl` directory; append-write via `Bash(cat <<EOF)` | H_T-IS-5 (state-ledger entry shape); harness-is/CLAUDE.md §4.1 |
| 3 | Hash-chain | Python stdlib SHA-256 + RFC 8785 canonicalization via `Bash` | H_T-IS-6 (hash-chain integrity discipline); harness-is/CLAUDE.md §4.1 |
| 4 | MCP server | FastMCP at `.claude/mcp.json` local scope; ≥ 3 representative tools per axis | H_T-AS-2 (tool contract schema); harness-as/CLAUDE.md §4.1 |
| 5 | Sub-agent spawning | H_E `Agent` tool with prompt template | H_T-CP-10 partial (one implicit topology ≠ 6-class enum); harness-cp/CLAUDE.md §4.1 |
| 6 | OTel emission | OTel SDK at MCP server boundary; OTLP to user-launched Collector | H_T-OD-2 (OTel SDK injection); H_T-OD-4 (SpanProcessor injection); harness-od/CLAUDE.md §4.1 |
| 7 | HITL primitive | H_E `AskUserQuestion` + permission-prompt approval | H_T-CP-20 partial (`AskUserQuestion` ≠ 4-response palette); harness-cp/CLAUDE.md §4.1 |
| 8 | Sandbox tier dispatch | `--permission-mode` at session open | H_T-CP-12 partial (permission modes ≠ sandbox-tier dispatch); harness-cp/CLAUDE.md §4.1 |
| 9 | Workflow conventions | `CLAUDE.md` per-workflow declarations | H_T-CP-6 partial (`CLAUDE.md` flat ≠ typed manifest); harness-cp/CLAUDE.md §4.1 |

### §6.3 H_T-CP-1 single-LLM-during-7a substitution explicit (Class 2 surface)

Per `Phase_7_Meta_Architecture_v1.md` §5.4 (H_T-CP-1 substitution) + §9 (Class 2 substitution-risk surface):

#### §6.3.1 Substitution statement

| Property | Value |
|---|---|
| H_T primitive | H_T-CP-1 (multi-LLM routing core) |
| H_E classification | ✗ absent (no H_E surface) |
| 7a substitution mechanism | Single-`--model` selection at Claude Code CLI session open |
| Substitution scope | 7a runtime exercise only; design commitment intact |
| Retirement criterion | U-CP-01 landing per Meta-Architecture §6.1 row H_T-CP-1 |

#### §6.3.2 Class 2 disposition

| Layer | Status during 7a | Status at U-CP-01 landing |
|---|---|---|
| Project commitment (multi-LLM by design) | Unmet at runtime | Met at runtime |
| ADR-F1 v1.2 design commitment | Met at design | Met at design |
| CP plan v2.3 U-CP-01 specification | Met at specification | Met at specification + at runtime |
| H_T-CP-1 primitive operational | Substituted (single `--model`) | Operational (multi-provider routing) |

#### §6.3.3 Risk-management discipline

| Anchor | Mechanism |
|---|---|
| Retirement criterion | `Phase_7_Meta_Architecture_v1.md` §6.1 row H_T-CP-1: U-CP-01 landing |
| Anti-leakage rule | CP-AL-4 (Meta-Architecture §7.4) — single-LLM-during-7a is runtime substitution; multi-LLM design commitment unchanged |
| Operator visibility | This directive §6.3 + Meta-Architecture §9 + §10.4.3 + Phase 6.5 Session 4 close handoff §5.2 + Workflow v1.8 §2.7.7 |
| Class 2 disposition | **CLOSED with operator visibility** per Workflow v1.8 §2.7.7 — no design-phase artifact revision required |

### §6.4 Retirement contract (X-AL-2)

Per `Phase_7_Meta_Architecture_v1.md` §7.7:

```
Condition A: Cited unit ID(s) per §6.1 row LANDED with acceptance tests passing
Condition B: Substituted H_E surface NO LONGER INVOKED at substitution site
              (verified via runtime trace inspection + code-search audit)

Retirement = Condition A ∧ Condition B
```

**Partial retirement is non-retirement.** Both conditions required. Retirement events governed by `phase-7-substitution-retirement` skill.

---

## §7 Sub-agent topology + skill activation surface

### §7.1 Sub-agent topology (5 architectural; 0 active at 7a)

Per `Sub_Agent_Boundary_Specification_v1.md` §3 + §4:

| Sub-agent ID | Activation window | Termination | Working directory | Substitution authority | Anti-leakage citation |
|---|---|---|---|---|---|
| `sa-is` | 7a exit (per §5.4 criteria) → IS L5 lands | U-IS-17 lands; coverage matrix verified | `harness-is/` | 9 IS-axis substitutions | IS-AL-1..4 + X-AL-1/2/3 |
| `sa-as` | IS clusters 1–3 (U-IS-01 → U-IS-10) land | U-AS-33 lands; coverage matrix verified | `harness-as/` | 6 AS-axis substitutions | AS-AL-1..4 + X-AL-1/2/3 |
| `sa-cp` | IS clusters 1–4 + AS clusters 1–2 land | U-CP-55 lands; coverage matrix verified | `harness-cp/` | 21 CP-axis substitutions (largest load) | CP-AL-1..5 + X-AL-1/2/3 (CP-AL-1 verbatim at Sub-Agent Boundary Spec §5.1) |
| `sa-od` | CP U-CP-54 lands | U-OD-34 lands; coverage matrix verified | `harness-od/` | 8 OD-axis substitutions | OD-AL-1..3 + X-AL-1/2/3 |
| `sa-cxa` | All 4 axis-stream sub-agents complete; terminal exporters (U-IS-17, U-AS-33, U-CP-55, U-OD-34) all land | All 101 CXA edges wired with Pattern P1 byte-exact alignment | `harness-cxa/` | 5 CXA-axis substitutions | CXA-AL-1 + X-AL-1/2/3 |

### §7.2 7a sub-agent posture: ZERO sub-agents instantiated

Per `Sub_Agent_Boundary_Specification_v1.md` §3.2.3 (verbatim):

> **No sub-agent for 7a or 7d.** Sub-phase 7a (bootstrap) operates under operator presence with no parallelism opportunity per Meta-Architecture §10.1.

All 7a unit landings execute under the operator-orchestrator (Claude Code primary session), NOT under delegated sub-agents. First sub-agent activation = `sa-is` at 7a → 7b transition.

### §7.3 Sub-agent count amendability

Per `Sub_Agent_Boundary_Specification_v1.md` §3.3 + Phase 6.5 Session 6 kickoff §2.1.4:

| Property | Value |
|---|---|
| Architectural default | 5 sub-agents |
| Operator amendment surface | Phase 7 session execution-time; bounded by Claude Code documented sub-agent surface |
| Anti-leakage discipline at amendment | §7.4 anti-leakage rules unchanged regardless of count amendment |

### §7.4 Skill activation surface (4 Phase 7-specific skills)

| Skill | Path | Primary activation | Event-driven activation |
|---|---|---|---|
| `phase-7-implementation` | `<workspace_root>/.claude/skills/phase-7-implementation/SKILL.md` | Sub-phase 7b per-axis-stream execution | Operator request for unit/cluster open at 7b |
| `phase-7-cross-axis-composition` | `<workspace_root>/.claude/skills/phase-7-cross-axis-composition/SKILL.md` | Sub-phase 7c CXA seam instantiation | `sa-cxa` active OR cross-axis edge request |
| `phase-7-substitution-retirement` | `<workspace_root>/.claude/skills/phase-7-substitution-retirement/SKILL.md` | Event-driven across 7b / 7c / 7d | Retirement event detection (X-AL-2 contract satisfaction) |
| `phase-7-back-flow-routing` | `<workspace_root>/.claude/skills/phase-7-back-flow-routing/SKILL.md` | **Event-driven across ALL sub-phases (7a / 7b / 7c / 7d)** | Fork detection (Class 1 / Class 2 / Class 3); **critical-failure-mode skill** |

### §7.5 Skill activation discipline at 7a

| Property | Value |
|---|---|
| Pre-loaded skills | None |
| Tool-search-discoverable skills | 4 (per §7.4) |
| 7a primary skill | None specific per workspace root `CLAUDE.md` §7; "consult Meta-Architecture §5 + §6 directly" |
| 7a always-on event-driven skill | `phase-7-back-flow-routing` (fork detection at 7a is the critical-failure-mode surface) |
| Skill precedence | Project-level `<workspace_root>/.claude/skills/` precedes user-level `~/.claude/skills/` on name collision (Anthropic Claude Code skill-directory convention) |
| Per OD-ε-2 | Project-level path convention canonical |

---

## §8 Back-flow routing + anti-leakage discipline binding

### §8.1 Workspace transition discipline

Per `phase-7-back-flow-routing/SKILL.md` §3.2 (canonical):

```
Phase 7 workspace (this workspace)
        │
        │ Class 1 fork detected
        ▼
Halt sub-phase execution
        │
        │ Surface to operator
        ▼
Operator routes to design-phase workspace
        │
        │ Open design-phase session at relevant phase channel
        ▼
Design-phase artifact revision (e.g., spec v1.x → v1.y)
        │
        │ Revision cleared (e.g., revision-pass complete)
        ▼
Design-phase artifact re-issued
        │
        │ Operator pushes re-issued artifact to design-phase /mnt/project/
        ▼
Phase 7 workspace re-loads artifact
        │
        │ Verify byte-exact integrity
        ▼
Resume Phase 7 sub-phase execution from halt point
        OR
Restart sub-phase if revised artifact invalidates prior progress
```

### §8.2 Class 1 routing table (back-flow to design-phase channels)

Per `Project_Workflow_v1_8.md` §2.7.6 + `phase-7-back-flow-routing/SKILL.md` §3.1:

| Defect locus | Routing channel | Predecessor cleared at |
|---|---|---|
| Plan atomic unit (signature unimplementable; cross-unit dependency wrong; acceptance criterion incompatible) | Phase 6 plan revision-pass at design-phase workspace | P6-CK Iter 4 (Phase 6 close 2026-05-14) |
| Spec contract (under-specifies surface; spec inconsistent with ADR) | Phase 5 spec revision-pass | P5-CK Iter 2 |
| ADR (F1–F5 or D1–D6) anchor decision | Phase 3a/3b ADR revision via council convening | P3a-CK + P3-CK |
| ADD attestation mismatch | Phase 3d ADD revision | P3-CK Iter 3 |
| PRD observable-behavior gap | Phase 4 PRD revision | (P4 close) |
| CXA edge enumeration / cardinality / Pattern P1 | Phase 6 CXA revision-pass | (Phase 6 close) |
| Workflow governance defect | Workflow revision (path-delta amendment process) | `Project_Workflow_v1_8.md` |

### §8.3 Class 2 routing (workspace-local)

Per `phase-7-back-flow-routing/SKILL.md` §3.3:

```
Class 2 fork surfaced
        │
        │ Surface to operator
        ▼
Operator decision via ask_user_input_v0
        │
        │ Decision recorded at sub-phase log
        ▼
Resume Phase 7 sub-phase execution
```

No design-phase workspace transition. Workspace-local disposition only.

### §8.4 Class 3 disposition

Class 3 informational items: logged at sub-phase close handoff; routed to applicable future revision pass OR design-choice rationale documented. Non-blocking.

### §8.5 Anti-leakage discipline binding (20 rules total)

| Source | Rule | Statement summary | Per `harness-{is,as,cp,od}/CLAUDE.md` §4.2 |
|---|---|---|---|
| Meta-Architecture §7.2 | IS-AL-1 | Path-class registry is canonical; H_E filesystem ≠ path-class semantics | IS axis |
| Meta-Architecture §7.2 | IS-AL-2 | Artifact-tier registry is typed; H_E flat dir structure ≠ cross-tier traceability | IS axis |
| Meta-Architecture §7.2 | IS-AL-3 | State ledger entry shape (6-field) ≠ H_E Bash-only writes | IS axis |
| Meta-Architecture §7.2 | IS-AL-4 | Bash shell-outs are substitutions, not contracts; retire at U-IS-08/09/10 | IS axis |
| Meta-Architecture §7.3 | AS-AL-1 | Permission modes ≠ SandboxTier enum (gate vs. capability) | AS axis |
| Meta-Architecture §7.3 | AS-AL-2 | H_E built-in tools ≠ user-extensible H_T tools; MCP server boundary canonical | AS axis |
| Meta-Architecture §7.3 | AS-AL-3 | Skills loading isomorphism ≠ exemption from cross-axis IS dependencies | AS axis |
| Meta-Architecture §7.3 | AS-AL-4 | Workflow-shape-specific H_E surfaces (LSP / plan mode / Chrome / remote / agent teams) out of H_T scope | AS axis |
| Meta-Architecture §7.4 | **CP-AL-1** | H_E sub-agent topology ≠ H_T TopologyPattern 6-class enum **(verbatim at Sub-Agent Boundary Spec §5.1)** | CP axis |
| Meta-Architecture §7.4 | CP-AL-2 | H_E session resume binary ≠ ResumptionKind 5-class typed taxonomy | CP axis |
| Meta-Architecture §7.4 | CP-AL-3 | H_E `--fallback-model` (single-target) ≠ H_T multi-step chain composition | CP axis |
| Meta-Architecture §7.4 | CP-AL-4 | H_E `--model` single-LLM ≠ routing core; single-LLM-during-7a is runtime substitution | CP axis |
| Meta-Architecture §7.4 | CP-AL-5 | H_E `CLAUDE.md` prose convention ≠ typed `WorkflowManifestEntry` schema | CP axis |
| Meta-Architecture §7.5 | OD-AL-1 | H_E telemetry (closed) ≠ harness observability substrate | OD axis |
| Meta-Architecture §7.5 | OD-AL-2 | H_E `/cost` (session-grain) ≠ H_T cost-attribution 5-step chain | OD axis |
| Meta-Architecture §7.5 | OD-AL-3 | All OTel emission at MCP server boundary; H_E does NOT participate in OTel emission (X-AL-1 concretization) | OD axis |
| Meta-Architecture §7.6 | CXA-AL-1 | Convention-based composition ≠ typed seam contracts (101 cross-axis edges across 6 buckets) | CXA cross-axis |
| Meta-Architecture §7.7 | **X-AL-1** | **Substrate boundary discipline.** H_E and H_T are distinct substrates; boundary at MCP server process (process isolation, not convention) | Cross-cutting |
| Meta-Architecture §7.7 | **X-AL-2** | **Retirement criterion fidelity.** Retirement = (cited unit IDs landed) ∧ (substituted H_E surface no longer invoked); both required | Cross-cutting |
| Meta-Architecture §7.7 | **X-AL-3** | **No silent H_T design extension at execution.** H_T design gaps surfaced at 7a route to design-phase back-flow (Class 1), NOT silent absorption | Cross-cutting |

**Total: 17 axis-bound rules + 3 cross-cutting rules = 20 rules.**

#### §8.5.1 Anti-leakage rule arithmetic note (C3-ε-14 carry-forward)

Per `Phase_6_5_Session_6_Close_Handoff.md` §5.3 Class 3 item C3-ε-14:

| Item | Status |
|---|---|
| Meta-Architecture narration cites | "18 rules across 5 axes" |
| Verbatim per-axis enumeration (§7.2–§7.6) sums to | 17 (IS=4 + AS=4 + CP=5 + OD=3 + CXA=1) |
| Disposition | Class 3 informational; canonical narration-arithmetic drift; non-blocking; future Meta-Architecture revision pass route |
| At this directive | Verbatim enumeration (17 axis + 3 cross-cutting = 20) is operative; narration "18" cited as-is per kickoff §2.1.1 row 11 |

### §8.6 X-AL-1 substrate boundary diagram

Per `Phase_7_Meta_Architecture_v1.md` §7.8 (canonical reproduction):

```
  ┌─────────────────────────────────────────────────────┐
  │  H_E SUBSTRATE — Claude Code CLI process            │
  │                                                     │
  │  • Built-in tools (Read, Write, Bash, Edit, ...)    │
  │  • Skills loading                                   │
  │  • Sub-agent spawning (Agent tool)                  │
  │  • CLAUDE.md context                                │
  │  • Session persistence                              │
  │  • Permission gating                                │
  │  • H_E-internal telemetry (closed)                  │
  └────────────────┬────────────────────────────────────┘
                   │  MCP protocol (FastMCP)
                   │  ━━━━━━━━━━━━━━━━━━━━━━━━━━ ◄── BOUNDARY
                   │
  ┌────────────────▼────────────────────────────────────┐
  │  H_T SUBSTRATE — harness-authored Python code       │
  │                                                     │
  │  • Tool implementations (Pydantic-typed)            │
  │  • State ledger writes (JSONL append-only)          │
  │  • Hash-chain construction (SHA-256 + JCS)          │
  │  • Idempotency-key construction                     │
  │  • OTel SDK emission (15-namespace at full)         │
  │  • Validator gates (when U-CP-47/48 land)           │
  │  • Sandbox-tier execution (when U-AS land)          │
  └─────────────────────────────────────────────────────┘
```

**H_T contracts are authored on the H_T side. H_E does not implement H_T contracts. The MCP boundary is the discipline-enforcement surface.**

### §8.7 Binding scope

| Property | Value |
|---|---|
| Binding from | This directive's filing at Phase 6.5 Session 7 (β) close |
| Binding scope | All Phase 7 sessions (7a + 7b + 7c + 7d) at new Claude Code CLI workspace |
| Binding mechanism | Workspace root `CLAUDE.md` §4 + per-axis `CLAUDE.md` §4.2 + Sub-Agent Boundary Spec §5 + `phase-7-back-flow-routing` SKILL §4 |
| Violation handling | `phase-7-back-flow-routing` skill event-driven activation; Class 1 if design-defect implication |
| Retirement | None — anti-leakage rules persist through Phase 7 close; X-AL-3 specifically binds against H_T design extension at execution-time |

---

## §9 Filing footer

| Field | Value |
|---|---|
| Artifact | `Phase_7_Session_1_Entry_Directive_v1.md` |
| Status | Filed at Phase 6.5 Session 7 (β) close 2026-05-15 |
| Phase | Phase 7 Session 1 entry — sub-phase 7a (Bootstrap) |
| Authoring discipline | Workflow v1.8 §7 fidelity-grammar; `systems-architect` SKILL.md Phase 7 entry directive authoring sub-mode (analog to Phase 4 PRD authoring discipline — directive-from-substrate inverted ordering) |
| Authoring authority | `Phase_6_5_Session_7_Kickoff.md` §2.1; Phase 6.5 arc-completion criterion 7 per Workflow v1.8 §2.6.5.4 |
| Predecessor | `Phase_6_5_Session_7_Close_Handoff.md`; 10 bootstrap substrate artifacts |
| Successor | Phase 7 Session 1 execution at new Claude Code CLI workspace |
| Filing destination | `<new_workspace_root>/Phase_7_Session_1_Entry_Directive_v1.md` |
| Coherence pass | ✅ PASS at 5/5 dimensions (Phase 6.5 Session 7 β Segment 3) |
| Date | 2026-05-15 |

---

*End of Phase 7 Session 1 Entry Directive v1. Phase 7 sub-phase 7a entry authorized. 7/7 entry-gate criteria CLEARED. Anti-leakage discipline binding from this filing onward.*
