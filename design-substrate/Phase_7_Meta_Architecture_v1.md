# Phase 7 Meta-Architecture (v1)

*Canonical chicken-and-egg meta-architecture artifact for Phase 7 execution. Authored at Phase 6.5 Session 4 (η + θ). Combined-path artifact per kickoff §2.3 default — η (H_T ↔ H_E substitution discipline) + θ (Phase 7 internal workflow) co-located for η ↔ θ coupling preservation.*

---

## §0 Status block + provenance

| Field | Value |
|---|---|
| Artifact | `Phase_7_Meta_Architecture_v1.md` |
| Version | v1 |
| Status | **Proposed** — Phase 6.5 Session 4 (η + θ) primary deliverable |
| Date | 2026-05-15 |
| Phase | Phase 6.5 (pre-transition arc) Session 4 (η + θ — chicken-and-egg meta-architecture + Phase 7 internal workflow) |
| Authoring authority | Operator directive 2026-05-14 (Phase 6.5 arc entry); `Phase_6_5_Pre_Transition_Arc_Manifest.md` §3.2 Session 4 enumeration; `Phase_6_5_Session_4_Kickoff.md` §2 |
| Predecessor | `Phase_6_5_Session_3_Close_Handoff.md`; v2.2 / v1 / v2.3 / v2.4 implementation plans + CXA v2.1; `Target_Stack_Commitment_v1.md`; `Plan_Executability_Audit_v1.md` |
| Successor (immediate) | `Phase_6_5_Session_4_Close_Handoff.md`; `Phase_6_5_Session_5_Kickoff.md` |
| Successor (arc) | Phase 7 execution at separate Claude Code CLI workspace per Workflow DP-4 default |
| Skill activation | `council-orchestrator` SKILL.md (selective-convening sub-mode: C1 + C7 + C11); `spec-writer` SKILL.md (canonicalization) |
| Filing destination | `/mnt/user-data/outputs/Phase_7_Meta_Architecture_v1.md` → operator pushes to `/mnt/project/` |

---

## §1 Identity + scope

### §1.1 Purpose

Author the canonical H_T ↔ H_E substitution discipline (η scope) and Phase 7 internal workflow sub-phase structure (θ scope). The artifact governs Phase 7 execution under the chicken-and-egg paradox: building the target harness (**H_T** — multi-LLM agent harness per v2.2 / v1 / v2.3 / v2.4 plans + CXA v2.1) *inside* the execution harness (**H_E** — Claude Code CLI).

### §1.2 Critical discipline (load-bearing)

Per `Phase_6_5_Session_4_Kickoff.md` §6.2: η authors the substitution discipline; it does NOT extend H_T's commitments. H_T design lives at the v2.2 / v1 / v2.3 / v2.4 plans + CXA v2.1 + ADD v1.3. Substitutions are scaffolding; they retire at H_T self-hosting milestones (§6).

### §1.3 Project framing carried forward (verbatim from V3 system prompt)

- **Multi-LLM by design.** The harness supports routing across multiple LLMs.
- **Local development environment as design-time deployment target.** Developer-owned hardware; NOT local-first software principles; cloud + hybrid deployment surfaces remain architectural options.
- **Production-grade engineering.** Source-grounded decisions, deterministic outer-harness discipline, observability as first-class, security boundaries at the harness level, reliability primitives composed correctly.

### §1.4 Artifact organization

| Section | Scope |
|---|---|
| §2 | H_T components catalog — per-axis canonical primitives (49 primitives + 5 CXA seams) |
| §3 | H_E capabilities catalog — Claude Code CLI tool surface (69 capabilities across 15 categories) |
| §4 | Capability overlap map — ✓ native / ~ partial / ✗ absent classification |
| §5 | Substitution mapping table — 49 entries per H_T primitive requiring substitution |
| §6 | Self-hosting milestone gradient — per-primitive retirement criteria + cluster aggregation + cross-axis dependencies |
| §7 | Substitution-risk discipline — 18 anti-leakage rules across 5 axes + 3 cross-cutting |
| §8 | H_E-rich-zone disposition — 10 candidates resolved as anti-leakage or substitution routes |
| §9 | Class 2 substitution-risk surface — H_T-CP-1 multi-LLM runtime commitment |
| §10 | Phase 7 internal workflow — 4 sub-phases (7a / 7b / 7c / 7d) with entry-gate / exit / back-flow / HITL viability |
| §11 | η ↔ θ coupling verification — 6 coupling surfaces |
| §12 | Coherence pass verdict — 5-dimension audit |
| §13 | Filing footer |

---

## §2 H_T components catalog

Per-axis canonical primitives sourced from v2.2 / v1 / v2.3 / v2.4 plans + CXA v2.1. Primitive-level aggregation; each row backed by carrier unit IDs.

### §2.1 Information Substrate (IS) axis — 10 canonical primitives

**Anchoring ADRs:** F2 v1.2 (state ledger substrate); F3 v1.1 (engine event history); D1 v1.2 (engine + replay); D3 v1.2 (artifact filesystem residence).

| Primitive ID | Primitive | Anchor | Carrier units |
|---|---|---|---|
| H_T-IS-1 | Path-class registry + workflow-canonical path resolver | C-IS-01 §1 | U-IS-01, U-IS-02, U-IS-03 |
| H_T-IS-2 | Artifact-tier registry + cross-tier traceability invariant | C-IS-02 §2 | U-IS-03 |
| H_T-IS-3 | Git-tier substrate (worktree-aware) | C-IS-03 §3 | U-IS-04 |
| H_T-IS-4 | Atomic deploy primitive (commit-grain reversibility) | C-IS-04 §4 | U-IS-05, U-IS-06 |
| H_T-IS-5 | State-ledger entry shape (6-field idempotency-key carrier) | C-IS-05 §5 | U-IS-07, U-IS-08, U-IS-09, U-IS-10 |
| H_T-IS-6 | Hash-chain integrity discipline | C-IS-06 §6 | U-IS-08, U-IS-09, U-IS-10 |
| H_T-IS-7 | T-perm-2 F2-layer read/write contract pair (JSONL composition) | C-IS-07 §7 | U-IS-11, **U-IS-12** (canonical idempotency-key join carrier per F3-02 closure) |
| H_T-IS-8 | Workload-class-opt-in shadow-Git checkpoint | C-IS-08 §8 | U-IS-13, U-IS-14, U-IS-15 |
| H_T-IS-9 | Workload-class-opt-in worktree-isolation | C-IS-09 §9 | U-IS-15, U-IS-16 |
| H_T-IS-10 | IS substrate seam exports manifest | C-IS-10 §10 | U-IS-17 |

**Substrate posture.** IS is consumer-most-upstream (0 outbound cross-axis edges).

### §2.2 Action Surface (AS) axis — 9 canonical primitives

**Anchoring ADRs:** F4 v1.1 (tool contract surface); F5 v1.1 (Skills); D2 v1.1 (sandbox + blast radius); D3 v1.2 (filesystem residence).

| Primitive ID | Primitive | Anchor | Carrier units | Cross-axis posture |
|---|---|---|---|---|
| H_T-AS-1 | SandboxTier enum (4-tier) + tier-monotonicity ordering | C-AS-01 §1 | U-AS-01, U-AS-02 | AS-internal |
| H_T-AS-2 | Tool contract schema (I/O types; namespacing; strict-mode; description-as-prompt) | C-AS-02 + C-AS-03 + C-AS-11 | U-AS-04 → U-AS-09 | AS-internal |
| H_T-AS-3 | Tool gate policy (3-valued GateLevel AUTO / ASK / DENY) | C-AS-04 §4 | U-AS-03 | AS-internal |
| H_T-AS-4 | Sandbox observability (`sandbox.*` 7-attribute namespace) | C-AS-09 + C-AS-10 + C-AS-12 | U-AS-10 → U-AS-15 | AS-internal |
| H_T-AS-5 | Sandbox-event idempotency-key composition | C-AS-15 §15 | U-AS-16 → U-AS-19 | IS consumer (U-IS-07, U-IS-12) |
| H_T-AS-6 | SkillFrontmatter schema + Skills loading discipline | C-AS-05 + C-AS-06 + C-AS-07 | U-AS-20 → U-AS-24 | AS-internal |
| H_T-AS-7 | Skills filesystem residence + reachability | C-AS-08 §8 | U-AS-25, U-AS-26, U-AS-27 | IS consumer (U-IS-01, U-IS-02, U-IS-08, U-IS-09, U-IS-10, U-IS-11) |
| H_T-AS-8 | Anthropic + MCP primitive observability (15-namespace exports) | C-AS-13 + C-AS-14 | U-AS-28 → U-AS-32 | IS consumer |
| H_T-AS-9 | AS substrate seam exports manifest | C-AS-16 §16 | U-AS-33 | AS exporter to CP / OD |

**Substrate posture.** AS consumes IS substrate (13 outbound); exports to CP / OD via U-AS-33.

### §2.3 Control Plane (CP) axis — 22 canonical primitives

**Anchoring ADRs:** F1 v1.2 (provider portability); F2 v1.2; F3 v1.1; F5 v1.1; D1 v1.2; D2 v1.1; D3 v1.2; D4 v1.1 (workload classes); D5 v1.3 (cross-deployment monotonicity); D6 v1.2 (observability + cost-attribution).

| Primitive ID | Primitive | Anchor | Carrier units | Cross-axis posture |
|---|---|---|---|---|
| H_T-CP-1 | Routing core + ProviderCapabilities + `routing.*` namespace | C-CP-01 §1 | U-CP-01 | IS + AS consumer |
| H_T-CP-2 | Layered routing strategy (declarative → embedding → LLM-as-router) | C-CP-02 §2 | U-CP-02 | CP-internal |
| H_T-CP-3 | Per-layer time-budget + `retry.*` 6-attribute namespace + dual-emission | C-CP-03 §3 | U-CP-03 → U-CP-07 | CP-internal |
| H_T-CP-4 | Fallback chain composition + cross-family fallback | C-CP-04 §4 | U-CP-04, U-CP-05 | CP-internal |
| H_T-CP-5 | Routing attribute namespaces + per-class sampling | C-CP-05 §5 | U-CP-11, U-CP-12 | CP-internal |
| H_T-CP-6 | Workflow manifest schema + per-step override + audit | C-CP-06 §6 | U-CP-13, U-CP-14 | CP-internal |
| H_T-CP-7 | EngineClass 5-class enum + workload-binding 5-step selection | C-CP-07 §7 | U-CP-15, U-CP-16, U-CP-17 | CP-internal |
| H_T-CP-8 | F2-substrate-join contract | C-CP-08 §8 | U-CP-18 | IS consumer |
| H_T-CP-9 | ResumptionKind 5-class taxonomy + `engine.*` namespace | C-CP-09 §9 | U-CP-19, U-CP-20, U-CP-21 | CP-internal |
| H_T-CP-10 | TopologyPattern 6-class enum + admissibility + CascadePolicy | C-CP-10 §10 | U-CP-22 | CP-internal |
| H_T-CP-11 | Per-workload commitment table + D4 multiplicative tunable | C-CP-11 §11 | U-CP-23, U-CP-24, U-CP-25 | CP-internal |
| H_T-CP-12 | Sandbox-tier dispatch (cross-deployment monotonicity) | C-CP-12 §12 | U-CP-26, U-CP-27 | AS consumer |
| H_T-CP-13 | Sub-agent handoff (HandoffContext, SubAgentBrief, StateSummary, LedgerEntryRef) | C-CP-13 §13 | U-CP-28, U-CP-29, U-CP-30 | IS consumer |
| H_T-CP-14 | Multi-agent span hierarchy + `topology.*` + `subagent.*` namespaces | C-CP-14 §14 | U-CP-31, U-CP-32 | CP-internal |
| H_T-CP-15 | Skills enabling discipline (CP-side composition) | C-CP-15 §15 | U-CP-33 → U-CP-37 | AS consumer |
| H_T-CP-16 | Memory primitives + `memory.*` consumption | C-CP-16 §16 | U-CP-38 → U-CP-41 | AS consumer |
| H_T-CP-17 | Files primitives + `files.*` consumption | C-CP-17 §17 | U-CP-42, U-CP-43, U-CP-44 | AS + IS consumer |
| H_T-CP-18 | MCP integration + per-server trust + `mcp.*` consumption | C-CP-18 §18 | U-CP-45 | AS consumer |
| H_T-CP-19 | D5 cross-deployment monotonicity | C-CP-19 §19 | U-CP-46 | CP-internal |
| H_T-CP-20 | HITL primitive + 4-response palette + `hitl.*` / `audit.*` | C-CP-20 §20 | U-CP-46 | CP-internal |
| H_T-CP-21 | ValidatorFailClass 5-class + operator-burden eval primitive | C-CP-21 §21 | U-CP-47, U-CP-48, U-CP-51, U-CP-52 | CP-internal |
| H_T-CP-22 | Pause/resume protocol + state_summary snapshot + material-diff | C-CP-22 §22 | U-CP-49, U-CP-50 | IS consumer |
| H_T-CP-23 | Bridging-arc traversal composition (F1 + D1 + D4) | C-CP-23 §23 | U-CP-53 | CP-internal |
| H_T-CP-24 | CP substrate seam exports + F2-12 closure manifest | C-CP-24 §24 | U-CP-54, U-CP-55 | CP exporter to OD; OD consumer for `harness.breaker.*` |

**Substrate posture.** CP consumes IS + AS substrate (60 outbound); exports to OD via U-CP-54 + U-CP-55. F2-12 CLOSED at v2.2 cascade.

### §2.4 Operational Discipline (OD) axis — 8 canonical primitives

**Anchoring ADRs:** D6 v1.2 (observability + cost-attribution); D1 v1.2; F2 v1.2; F3 v1.1.

| Primitive ID | Primitive | Anchor | Carrier units | Cross-axis posture |
|---|---|---|---|---|
| H_T-OD-1 | Deferral envelope | C-OD-01 — C-OD-03 | U-OD-01 → U-OD-03 | OD-internal |
| H_T-OD-2 | OTel SDK base + GenAI semconv binding | C-OD-04 — C-OD-08 | U-OD-04 → U-OD-08 | AS + CP consumer |
| H_T-OD-3 | Composite Sampler (head/tail gradient) | C-OD-09 — C-OD-12 | U-OD-09 → U-OD-12 | AS consumer |
| H_T-OD-4 | Pre-Collector redaction SpanProcessor | C-OD-13 — C-OD-16 | U-OD-13 → U-OD-16 | OD-internal |
| H_T-OD-5 | Cost-attribution 5-step chain | C-OD-09 — C-OD-14 | U-OD-17 → U-OD-22 | IS + AS + CP consumer (4 IS edges post-C3-15) |
| H_T-OD-6 | Local-first OTLP ingestion (in-process collector + sqlite + TUI) | C-OD-15 — C-OD-19 | U-OD-23 → U-OD-27 | AS + CP consumer |
| H_T-OD-7 | Preservation invariants (5-dimension) | C-OD-20 — C-OD-22 | U-OD-28 → U-OD-33 | CP consumer |
| H_T-OD-8 | OD aggregate manifest + F-CP-01 Stage 3b inversion | C-OD-23 §23 | U-OD-34 | OD exporter to CP (single inversion); terminal aggregate |

**Substrate posture.** OD is consumer-most (26 outbound: IS=4, AS=10, CP=12); single inverted exporter at `harness.breaker.*` namespace.

### §2.5 Cross-axis (CXA) composition — 5 canonical seams

| Seam ID | Composition surface | Edge cardinality | Anchor |
|---|---|---|---|
| H_T-CXA-1 | AS → IS substrate consumption | 13 edges | CXA v2.1 §2.3.1 |
| H_T-CXA-2 | CP → IS substrate consumption | 36 edges | CXA v2.1 §2.3.2 |
| H_T-CXA-3 | CP → AS substrate consumption | 24 edges | CXA v2.1 §2.3.3 |
| H_T-CXA-4 | OD → IS / AS / CP substrate consumption | 26 edges (4+10+12 post-C3-15) | CXA v2.1 §2.3.4–§2.3.6 |
| H_T-CXA-5 | OD → CP inversion (`harness.breaker.*` substrate-anchored-outside-CP) | 1 edge | CXA v2.1 §2.3.7 |

**CXA-OD-IS-EDGE-DRIFT note.** CXA v2.1 baseline carries 6 OD→IS edges; OD plan v2.4 carries 4 OD→IS edges per C3-15 Path (i-refined). Drift recorded as Class 3 informational at IS plan v2.2 §0.9; resolution at 7c via CXA v2.1 → v2.2 revision.

### §2.6 Catalog aggregate

| Axis | Canonical primitives | Atomic units | Contracts |
|---|---|---|---|
| IS | 10 | 17 | 10 |
| AS | 9 | 33 | 16 |
| CP | 22 | 55 | 24 |
| OD | 8 | 34 | 23 |
| CXA | 5 seams | — | — |
| **Total** | **49 primitives + 5 seams** | **139 units** | **73 contracts** |

---

## §3 H_E capabilities catalog

Claude Code CLI tool surface per code.claude.com/docs/en/tools-reference [HIGH — accessed 2026-05-15] + code.claude.com/docs/en/cli-reference [HIGH — accessed 2026-05-15].

### §3.1 Capability categories — aggregate

| Category | Capability count | Representative capabilities |
|---|---|---|
| Filesystem | 7 | `Read` / `Write` / `Edit` / `Glob` / `Grep` / `NotebookEdit` / `--add-dir` |
| Shell execution | 4 | `Bash` / `PowerShell` (opt-in) / Bash internal behavior |
| Web | 3 | `WebSearch` / `WebFetch` / `--chrome` |
| Sub-agent + delegation | 6 | `Agent` / `AskUserQuestion` / `--bg` + `claude attach` / agent teams (experimental) |
| Code intelligence | 3 | `LSP` (def / refs / type info) |
| Task list + scheduling | 3 | `TaskCreate/Get/List/Update/Stop` / `TodoWrite` / `CronCreate` |
| Worktree management | 4 | `EnterWorktree` / `ExitWorktree` / `--worktree` / `--tmux` |
| Plan + permission modes | 3 | `EnterPlanMode` / 6-mode permission gradient / allow-deny rules |
| MCP integration | 5 | `claude mcp` / `--mcp-config` / `--strict-mcp-config` / `ListMcpResourcesTool` / `ToolSearch` |
| Skills | 4 | `Skill` tool / `.claude/skills/` layout / frontmatter / shell selection |
| Configuration hierarchy | 6 | `CLAUDE.md` / `.claude/settings.json` / `.claude/agents/` / `.claude/mcp.json` / `--settings` / `--bare` |
| Hooks | 5 | Setup / SessionStart / tool-lifecycle hooks |
| Session management | 7 | Resume / fork / rename / background lifecycle / Checkpointing |
| Output + integration modes | 6 | Print mode / JSON output / `--json-schema` / `--max-budget-usd` / `--max-turns` / `--fallback-model` |
| Plugins | 3 | `claude plugin` / `--plugin-dir` / `--plugin-url` |
| **Aggregate** | **69 capabilities** | — |

Full per-capability enumeration with source citations at `Phase_6_5_Session_4_Kickoff.md` companion conversation (Segment 1). Capability IDs `H_E-{category}-{n}` referenced throughout this document.

---

## §4 Capability overlap map

### §4.1 Classification taxonomy

| Symbol | Reading | Operational meaning |
|---|---|---|
| ✓ | H_E provides native capability isomorphic to H_T primitive at shape and discipline level | No substitution required at §5 |
| ~ | H_E provides partial-substitute capability — mechanism present, shape or discipline divergent | Substitution at §5; substitution carries shape-translation cost |
| ✗ | H_E does not provide capability | Substitution at §5 if H_T primitive must be operational during 7a; otherwise H_T-native at 7b |

### §4.2 Per-axis overlap aggregate

```
                         ✓ Native    ~ Partial    ✗ Absent    Total
                         ────────    ─────────    ────────    ─────
IS axis                       1           5           4         10
AS axis                       3           2           4          9
CP axis                       1          10          11         22
OD axis                       0           1           7          8
CXA seams                     0           3           2          5
                         ────────    ─────────    ────────    ─────
Aggregate                     5          21          28         54
                          (9.3%)      (38.9%)      (51.9%)    (100%)
```

### §4.3 Per-axis overlap density verdict

| Axis | Overlap density | Reading |
|---|---|---|
| AS (33%) | Highest | Skills + worktree + gate policy + Bash-mediated git substrate are direct H_E primitives. H_E built for the same kind of agentic-coding surface H_T's AS axis specifies. |
| IS (10%) | Moderate | Git substrate is the single ✓; all other IS primitives are H_T-axis authoring artifacts or schema-typed primitives that H_E does not expose. |
| CP (4.5%) | Low | Multi-LLM routing, engine-class taxonomy, validator framework, bridging-arc traversal absent. CP is the load-bearing self-hosting work in Phase 7. |
| OD (0%) | None | H_E telemetry serves Claude Code's own analytics, not user-harness instrumentation. OD is H_T-native from 7a. |
| CXA | n/a (composition) | CXA seams bounded by endpoint overlap density. |

### §4.4 Per-primitive overlap classification

#### §4.4.1 IS axis classification

| Primitive | Status | Brief rationale |
|---|---|---|
| H_T-IS-1 | ~ | H_E filesystem primitives present; 4-class registry semantics absent |
| H_T-IS-2 | ✗ | No artifact-tier concept in H_E |
| H_T-IS-3 | ✓ | `Bash(git *)` + `EnterWorktree` direct match |
| H_T-IS-4 | ~ | Bash+git commit-grain available; harness-level deploy contract absent |
| H_T-IS-5 | ✗ | H_E session history shape ≠ H_T 6-field ledger entry |
| H_T-IS-6 | ✗ | No hash-chain primitive |
| H_T-IS-7 | ~ | Filesystem I/O sufficient for substitute; no append-only/selective-read contract |
| H_T-IS-8 | ~ | H_E Checkpointing on session-state grain ≠ H_T manifest-cadence on harness-state |
| H_T-IS-9 | ~ | Worktree native; workload-class-opt-in manifest discipline absent |
| H_T-IS-10 | ✗ | Authoring artifact; no H_E concept |

#### §4.4.2 AS axis classification

| Primitive | Status | Brief rationale |
|---|---|---|
| H_T-AS-1 | ~ | Permission modes ≠ SandboxTier; mode-gate vs capability-gate |
| H_T-AS-2 | ~ | MCP server provides extension surface; not direct H_T tool contract |
| H_T-AS-3 | ✓ | Permission rules direct map to GateLevel 3-valued |
| H_T-AS-4 | ✗ | No `sandbox.*` namespace emission |
| H_T-AS-5 | ✗ | No idempotency-key primitive |
| H_T-AS-6 | ✓ | H_E Skills frontmatter native |
| H_T-AS-7 | ✓ | `.claude/skills/<name>/SKILL.md` direct match |
| H_T-AS-8 | ✗ | No 15-namespace emission |
| H_T-AS-9 | ✗ | Authoring artifact |

#### §4.4.3 CP axis classification

| Primitive | Status | Brief rationale |
|---|---|---|
| H_T-CP-1 | ✗ | Single-Anthropic-model via `--model`; no multi-LLM routing core |
| H_T-CP-2 | ✗ | Depends on H_T-CP-1 absence |
| H_T-CP-3 | ✗ | SDK retry invisible; no namespace emission |
| H_T-CP-4 | ~ | `--fallback-model` single-target only |
| H_T-CP-5 | ✗ | Depends on H_T-CP-1, H_T-CP-2 |
| H_T-CP-6 | ~ | `CLAUDE.md` flat instruction surface ≠ typed manifest |
| H_T-CP-7 | ✗ | No engine-class taxonomy |
| H_T-CP-8 | ✗ | Depends on IS-axis primitives absent in H_E |
| H_T-CP-9 | ~ | Session resume binary; not 5-class typed taxonomy |
| H_T-CP-10 | ~ | One implicit topology; not 6-class enum |
| H_T-CP-11 | ✗ | No workload-class taxonomy |
| H_T-CP-12 | ~ | Permission-mode gradient ≠ sandbox-tier dispatch |
| H_T-CP-13 | ~ | `Agent` free-text handoff ≠ typed schemas |
| H_T-CP-14 | ✗ | No topology/subagent namespace emission |
| H_T-CP-15 | ✓ | Automatic Skills enabling per frontmatter |
| H_T-CP-16 | ~ | `CLAUDE.md` memory; no `memory.*` observability |
| H_T-CP-17 | ~ | Filesystem primitives native; no `files.*` observability |
| H_T-CP-18 | ~ | MCP native; per-server trust framework absent |
| H_T-CP-19 | ✗ | Single deployment shape |
| H_T-CP-20 | ~ | `AskUserQuestion` mechanism present; 4-response palette + namespaces absent |
| H_T-CP-21 | ✗ | No validator framework |
| H_T-CP-22 | ~ | `/compact` + resume coarse; not typed pause/resume |
| H_T-CP-23 | ✗ | No bridging-arc concept |
| H_T-CP-24 | ✗ | Authoring artifact |

#### §4.4.4 OD axis classification

| Primitive | Status | Brief rationale |
|---|---|---|
| H_T-OD-1 | ✗ | `ToolSearch` ≠ deferral envelope (categorical mismatch) |
| H_T-OD-2 | ✗ | H_E telemetry closed; no OTel SDK injection |
| H_T-OD-3 | ✗ | No sampling-discipline surface |
| H_T-OD-4 | ✗ | No SpanProcessor injection |
| H_T-OD-5 | ~ | `/cost` + `--max-budget-usd` coarse; not 5-step chain |
| H_T-OD-6 | ✗ | No in-process OTLP collector exposed |
| H_T-OD-7 | ✗ | No preservation discipline |
| H_T-OD-8 | ✗ | Authoring artifact |

#### §4.4.5 CXA classification

| Seam | Status | Brief rationale |
|---|---|---|
| H_T-CXA-1 | ~ | Filesystem composition mechanism; not typed 13-edge contract |
| H_T-CXA-2 | ~ | Mechanism present; typed 36-edge contract absent |
| H_T-CXA-3 | ~ | Sub-agent + Skills + MCP composition; typed 24-edge contract absent |
| H_T-CXA-4 | ✗ | OD-axis substrate absent at endpoints |
| H_T-CXA-5 | ✗ | Breaker primitive absent both endpoints |

---

## §5 Substitution mapping table

Per H_T primitive lacking H_E native support: substitution mechanism + bounded scope + retirement criterion. 49 entries.

### §5.1 Entry shape

| Field | Content |
|---|---|
| Substitution mechanism | Exact H_E surface(s) used as scaffolding |
| Bounded scope | What the substitution covers; what it explicitly does NOT cover |
| Retirement criterion | H_T unit ID(s) whose landing retires the substitution |

### §5.2 IS axis substitutions (9 entries)

| Primitive | Substitution | Bounded scope | Retirement |
|---|---|---|---|
| H_T-IS-1 | `CLAUDE.md` declares 4-class path convention; sub-agent `Read`/`Write` calls obey via prompt-discipline; `Glob` enumerates against declared roots | Covers: directory convention + sub-agent compliance. Does NOT cover: programmatic registry lookup at runtime; path-class-aware tool gating | U-IS-01 + U-IS-02 + U-IS-03 |
| H_T-IS-2 | `CLAUDE.md`-declared tier-naming convention; manual cross-tier traceability in ledger entries | Covers: human-readable tier tagging. Does NOT cover: programmatic invariant enforcement | U-IS-03 |
| H_T-IS-4 | `Bash(git *)` sequence — `git add --all` + `git commit -m=<canonical>` per deploy; rollback via `git revert` | Covers: commit-grain reversibility on git-tracked artifacts. Does NOT cover: pre-deploy verification gate; post-deploy invariant check; deploy-failure roll-forward | U-IS-05 + U-IS-06 |
| H_T-IS-5 | JSONL at `.harness/state.jsonl`; `Bash` `python -c 'import json...'` produces canonical 6-field entries; `Bash(cat <<EOF >>)` appends; sub-agents `Read` to consume | Covers: schema-shape parity (6 fields). Does NOT cover: append-only invariant enforcement; concurrent-write coordination | U-IS-07 |
| H_T-IS-6 | `Bash` invocation of Python stdlib `hashlib.sha256` + JCS canonicalization; sub-agents construct entries with hash via prompt-discipline | Covers: 4-step canonicalize → SHA-256 → chain construct → verify at single-writer cadence. Does NOT cover: tamper-evidence audit at scale; runtime chain-break detection on read | U-IS-08 + U-IS-09 + U-IS-10 |
| H_T-IS-7 | C3-pole: `Bash(cat <<EOF >> .harness/state.jsonl)` for append; C2-pole: `Bash(jq ...)` or `Read` + Python `json.loads` filtering | Covers: JSONL format; read/write distinction via prompt-discipline. Does NOT cover: idempotency on `(thread_id, step_id, idempotency_key)`; navigation-primitive contract | U-IS-11 + U-IS-12 |
| H_T-IS-8 | H_E built-in Checkpointing on session-state grain; `Bash(git commit)` at H_E-decided cadence for harness-state; cadence via `CLAUDE.md` convention | Covers: filesystem-state checkpointing at coarse cadence. Does NOT cover: manifest-declared cadence enum (4 classes); per-workload-class opt-in selection; reversal-granularity contract | U-IS-13 + U-IS-14 + U-IS-15 |
| H_T-IS-9 | H_E native worktree primitives: `EnterWorktree` for per-sub-agent isolation; `--worktree <name>` flag; worktree paths at `<repo>/.claude/worktrees/<name>` | Covers: per-sub-agent worktree isolation; concurrent-read isolation at git-backend. Does NOT cover: manifest-driven workload-class opt-in selection; multi-writer scaling boundary | U-IS-15 + U-IS-16 |
| H_T-IS-10 | None at runtime; authoring artifact. Downstream-axis sub-agents consult IS plan v2.2 §2.6 U-IS-17 manifest text directly | Covers: documentation reference. Does NOT cover: runtime resolution of substrate seam references | U-IS-17 |

### §5.3 AS axis substitutions (6 entries)

| Primitive | Substitution | Bounded scope | Retirement |
|---|---|---|---|
| H_T-AS-1 | Tier-1 = `--permission-mode plan`; Tier-2 = default mode + `deny` patterns; Tier-3 = `acceptEdits`; Tier-4 = `bypassPermissions` | Covers: 4-level gating gradient against tool-invocation approval. Does NOT cover: actual sandboxed execution; `sandbox.tech` ↔ `sandbox.provider` join contract; cross-deployment monotonicity | U-AS-01 + U-AS-02 |
| H_T-AS-2 | All H_T tools authored at FastMCP server registered via `.claude/mcp.json` local scope; Pydantic v2 schemas at server side; namespacing via FastMCP naming; description-as-prompt in MCP `description` field | Covers: tool-schema authoring + namespacing + description-as-prompt at MCP boundary. Does NOT cover: strict-mode contract verification at harness side; cross-tool dependency declaration | U-AS-04 → U-AS-09 |
| H_T-AS-4 | OTel SDK at MCP server emits `sandbox.*` 7-attribute namespace from server-side code; OTLP export to user-launched Collector subprocess | Covers: 7-attribute `sandbox.*` emission at server side. Does NOT cover: sampling discipline; H_E-side instrumentation | U-AS-10 → U-AS-15 |
| H_T-AS-5 | FastMCP server constructs idempotency keys from `(tool_name, canonicalize(input_payload))` via SHA-256 server-side; key appended to JSONL ledger | Covers: per-tool-invocation key construction at server side. Does NOT cover: cross-axis idempotency-key join contract; harness-layer key validation on read | U-AS-16 → U-AS-19 |
| H_T-AS-8 | OTel emission at MCP server boundary for `mcp.*` / `skill.*` / `files.*` / `memory.*` / `managed_agents.*`; `anthropic.*` namespace remains absent (closed H_E surface) | Covers: 5 of 7 server-side-instrumentable namespaces. Does NOT cover: `anthropic.*` (requires H_T-CP-1 retirement); `sandbox.*` (covered by H_T-AS-4); full Pattern P1 byte-exact alignment until OD substrate retires | U-AS-28 → U-AS-32 |
| H_T-AS-9 | None at runtime; authoring artifact at U-AS-33 | Covers: documentation reference. Does NOT cover: runtime resolution | U-AS-33 |

### §5.4 CP axis substitutions (21 entries)

| Primitive | Substitution | Bounded scope | Retirement |
|---|---|---|---|
| H_T-CP-1 | Single-LLM during 7a: `--model claude-sonnet-4-6` at every sub-agent invocation; `CLAUDE.md` documents single-LLM constraint | Covers: single-Anthropic-model surface. Does NOT cover: multi-LLM routing (project commitment unmet at runtime — Class 2 surface §9) | U-CP-01 |
| H_T-CP-2 | None — depends on H_T-CP-1 | n/a | U-CP-02 |
| H_T-CP-3 | H_E SDK internal retries invisible; no `LayerBudget` enforcement | Does NOT cover: time-budget enforcement; retry namespace; dual-emission | U-CP-03 → U-CP-07 |
| H_T-CP-4 | `--fallback-model` (print mode); single-target | Covers: single-step fallback. Does NOT cover: multi-step chain; cross-family fallback; `fallback.*` namespace | U-CP-04 + U-CP-05 |
| H_T-CP-5 | None — depends on H_T-CP-1, H_T-CP-2 | n/a | U-CP-11 + U-CP-12 |
| H_T-CP-6 | `CLAUDE.md` carries workflow conventions as prose; per-step override via operator-edited prompt | Covers: human-readable declaration. Does NOT cover: typed `WorkflowManifestEntry` schema; programmatic per-step override evaluator; audit composition | U-CP-13 + U-CP-14 |
| H_T-CP-7 | None — single-engine during 7a (Claude Code itself is engine) | Does NOT cover: 5-class taxonomy; workload-binding selection | U-CP-15 + U-CP-16 + U-CP-17 |
| H_T-CP-8 | None — depends on H_T-IS-5, H_T-IS-7; six-field shape via prompt-discipline | Does NOT cover: typed F2-substrate-join at runtime | U-CP-18 |
| H_T-CP-9 | H_E `--resume` / `--continue` / `--fork-session`; ResumptionKind via `CLAUDE.md` manual classification | Covers: session-level binary resume. Does NOT cover: 5-class typed taxonomy; per-resumption observable behavior; `engine.*` + `workflow.resumption` discipline | U-CP-19 + U-CP-20 + U-CP-21 |
| H_T-CP-10 | H_E implicit orchestrator-worker pattern; remaining 5 patterns approximated by sub-agent patterns under `CLAUDE.md` discipline | Covers: single pattern. Does NOT cover: 6-class enum + admissibility predicate; `CascadePolicy` | U-CP-22 |
| H_T-CP-11 | None — single-workload-class during 7a | Does NOT cover: workload-class commitment table; per-engine overlay; 2D matrix; D4 multiplicative tunable | U-CP-23 + U-CP-24 + U-CP-25 |
| H_T-CP-12 | Permission-mode at session open; per-tool allow/deny by convention | Covers: coarse default-downgrade. Does NOT cover: monotonic-descent invariant; override-with-audit; cross-deployment monotonicity; dispatch-audit composition | U-CP-26 + U-CP-27 |
| H_T-CP-13 | H_E `Agent` tool free-text prompt + tool list; schemas collapse to prose in prompt; brief-authoring inheritance via `CLAUDE.md` | Covers: untyped free-text handoff. Does NOT cover: typed schemas | U-CP-28 + U-CP-29 + U-CP-30 |
| H_T-CP-14 | None at H_E layer — span emission deferred to harness-authored orchestration at MCP server side | Does NOT cover: multi-agent span hierarchy; `topology.*` / `subagent.*` namespaces | U-CP-31 + U-CP-32 |
| H_T-CP-16 | `CLAUDE.md` hierarchy as memory; no `memory.*` namespace emission | Covers: persistent memory at H_E hierarchy. Does NOT cover: observability namespace; programmatic memory mutation API | U-CP-38 → U-CP-41 |
| H_T-CP-17 | H_E `Read`/`Write`/`Edit`/`Glob`/`Grep`; no `files.*` namespace emission | Covers: filesystem ops. Does NOT cover: `files.*` namespace; files-primitive composition with ledger | U-CP-42 + U-CP-43 + U-CP-44 |
| H_T-CP-18 | H_E `claude mcp` + `.claude/mcp.json` + scope hierarchy; no `mcp.*` namespace emission | Covers: MCP server registration + scope-based access. Does NOT cover: 5-tier trust framework; `mcp.*` namespace; tool-poisoning detection | U-CP-45 |
| H_T-CP-19 | None — single deployment shape during 7a | Does NOT cover: sandbox-tier floor + gate-level floor across deployment surfaces | U-CP-46 |
| H_T-CP-20 | `AskUserQuestion` tool + permission-prompt approval; no 4-response palette; no `hitl.*` / `audit.*` namespaces | Covers: HITL invocation surface. Does NOT cover: 4-response palette (APPROVE / APPROVE_WITH_NOTE / DEFER / REJECT); namespace emission | U-CP-46 |
| H_T-CP-21 | Operator reviews every sub-agent output before commit; no automated validator framework; operator-burden via manual ledger annotation | Covers: human-mediated validation gate. Does NOT cover: 5-class ValidatorFailClass; transient staircase; cause-branching; operator-burden eval primitive | U-CP-47 + U-CP-48 + U-CP-51 + U-CP-52 |
| H_T-CP-22 | H_E `/compact` + resume + `--fork-session`; `state_summary` as compacted-conversation summary | Covers: coarse pause/resume + summarization. Does NOT cover: typed `state_summary` schema; material-diff 5-category; summarization fallback under revalidation | U-CP-49 + U-CP-50 |
| H_T-CP-23 | None — manual operator orchestration during 7a | Does NOT cover: 20-cell reading; three-layer F1+D1+D4 composition | U-CP-53 |
| H_T-CP-24 | None at runtime; authoring artifacts at U-CP-54 + U-CP-55 (F2-12 already CLOSED at v2.2 cascade) | Covers: documentation reference | U-CP-54 + U-CP-55 |

### §5.5 OD axis substitutions (8 entries)

| Primitive | Substitution | Bounded scope | Retirement |
|---|---|---|---|
| H_T-OD-1 | None at runtime; authoring artifact at U-OD-01 → U-OD-03; scope deferrals tracked in `CLAUDE.md` | Covers: prose deferral tracking | U-OD-01 + U-OD-02 + U-OD-03 |
| H_T-OD-2 | OTel SDK (`opentelemetry-api`, `opentelemetry-sdk`, `opentelemetry-exporter-otlp`, selective `opentelemetry-instrumentation-genai`) at MCP server boundary; GenAI semconv 1.41.0 [HIGH — Target_Stack_Commitment_v1 §7] applied at server-side `Tracer` initialization | Covers: OTel SDK base at MCP server; specialization-layer ingestion at server boundary. Does NOT cover: H_E-internal events (closed); cross-process OTel context propagation between H_E and user code | U-OD-04 → U-OD-08 |
| H_T-OD-3 | Project-authored `Sampler` subclass at MCP server per `opentelemetry.sdk.trace.sampling.Sampler` ABC; head-based at cell-1 (local-first); tail-based discipline not invoked during 7a | Covers: head-based sampling at server side. Does NOT cover: tail-based-prod sampling; cross-cell transitions | U-OD-09 → U-OD-12 |
| H_T-OD-4 | Project-authored `SpanProcessor` subclass per `opentelemetry.sdk.trace.SpanProcessor` ABC; structure-not-content redaction applied at server emission before OTLP export | Covers: pre-export redaction at server side. Does NOT cover: multi-tenant redaction discipline | U-OD-13 → U-OD-16 |
| H_T-OD-5 | H_E `/cost` for session-level visibility; `--max-budget-usd` (print mode) enforces budget; per-attempt attribution via JSONL ledger annotated with token-counts from H_E reporting; idempotency-key join not exercised | Covers: session-level cost + budget cap. Does NOT cover: 5-step chain (per-attempt + idempotency-key join + hash-chain integrity composition + replay-aware dedup + cause_attribution invariance) | U-OD-17 → U-OD-22 |
| H_T-OD-6 | User-launched OTel Collector subprocess via `Bash` (`otelcol --config ./otel-config.yaml &`); writes to local sqlite via OTLP→sqlite exporter; TUI deferred (CLI-only inspection via `Bash(sqlite3 ...)`) during 7a | Covers: out-of-process Collector + sqlite ingestion. Does NOT cover: in-process Collector composition; Textual TUI; ring-buffer eviction discipline | U-OD-23 → U-OD-27 |
| H_T-OD-7 | None — manual operator verification at scope boundaries | Does NOT cover: 5-dimension preservation (SCHEMA / CARDINALITY / ORDERING / IDEMPOTENCY / TRACEABILITY) | U-OD-28 → U-OD-33 |
| H_T-OD-8 | None at runtime; authoring artifact at U-OD-34; F-CP-01 Stage 3b inversion not exercised during 7a | Covers: documentation reference | U-OD-34 |

### §5.6 CXA seam substitutions (5 entries)

| Seam | Substitution | Bounded scope | Retirement |
|---|---|---|---|
| H_T-CXA-1 | Filesystem composition by convention: sub-agents `Read`/`Write`/`Glob` against IS-axis filesystem-resident substrate; idempotency-key join at MCP server side per H_T-AS-5 | Covers: read/write composition. Does NOT cover: 13-edge typed contract surface | AS clusters 4 + 6 + 7 land |
| H_T-CXA-2 | State-ledger composition by convention: CP-axis sub-agents `Read` against H_T-IS-5 substitution JSONL; entry-shape conformance via prompt-discipline; hash-chain verification deferred | Covers: read composition at filesystem level. Does NOT cover: 36-edge typed contract surface | CP clusters 3 + 8 land |
| H_T-CXA-3 | Sub-agent spawning composes with Skills + MCP via H_E `Agent` + Skills loading + MCP registration; brief-authoring via `CLAUDE.md` | Covers: untyped composition. Does NOT cover: 24-edge typed contract surface | CP clusters 5 + 6 + 7 land |
| H_T-CXA-4 | None at H_E layer — OD substrate consumption depends on OTel substrate (H_T-OD-2 substitution) at MCP server side; Collector consumes server-side emission only | Covers: out-of-process telemetry consumption. Does NOT cover: 26-edge typed contract surface | OD clusters 3 + 5 + 7 land |
| H_T-CXA-5 | None — breaker primitive absent both endpoints during 7a | Does NOT cover: F-CP-01 Stage 3b inversion; `harness.breaker.*` namespace | U-OD-09 + U-CP-54 §24.1.C joint-landing |

### §5.7 Substitution-type breakdown

| Substitution type | Count |
|---|---|
| H_E primitive used directly (with shape divergence noted) | 11 |
| MCP server-side authoring (FastMCP + Pydantic + OTel SDK) | 12 |
| `CLAUDE.md` convention + prompt-discipline | 9 |
| `Bash` shell-out (python -c, sqlite3, git, otelcol) | 8 |
| None — manual operator orchestration during 7a | 5 |
| None — authoring artifact only | 4 |
| **Total** | **49** |

---

## §6 Self-hosting milestone gradient

### §6.1 Per-primitive retirement gradient

Per-primitive granularity preserved for spec-traceability fidelity. Full table preserved at Phase 6.5 Session 4 Segment 4 conversation §14.2 (IS axis 10 rows / AS axis 9 rows / CP axis 22 rows / OD axis 8 rows / CXA seams 5 rows = 54 rows).

### §6.2 Cluster-aggregation milestone phases

```
PHASE 7a — BOOTSTRAP (L0 anchors + L1–L2 operational-minimum)
═══════════════════════════════════════════════════════════════════════
  IS  L0–L1  →  H_T-IS-1, H_T-IS-2, H_T-IS-3 operational
  AS  L0    →  H_T-AS-1 (partial), H_T-AS-3, H_T-AS-6 native
  CP  L0    →  H_T-CP-10, H_T-CP-15 native; H_T-CP-3/7/9 partial
  OD  L0–L1 →  H_T-OD-1 declarative envelope

PHASE 7b — PER-AXIS INTERIOR EXECUTION (axis cluster completion)
═══════════════════════════════════════════════════════════════════════
  IS  L2–L5  →  H_T-IS-4 through H_T-IS-10 retire substitutions
  AS  L1–L8  →  H_T-AS-1 (full), H_T-AS-2, H_T-AS-4 through H_T-AS-9
  CP  L1–L8  →  H_T-CP-1 (Class 2 retired), H_T-CP-2 through H_T-CP-24
  OD  L1–L9  →  H_T-OD-2 through H_T-OD-8

PHASE 7c — CROSS-AXIS INTEGRATION (CXA seam activation)
═══════════════════════════════════════════════════════════════════════
  H_T-CXA-1 → H_T-CXA-5 activate as endpoint clusters complete

PHASE 7d — SELF-HOSTING MILESTONES (substitution retirement cadence)
═══════════════════════════════════════════════════════════════════════
  Substitution-retirement complete; H_E reduced to host-process role
  H_T runs against H_T-authored substrate; H_E executes the model loop
```

### §6.3 Cross-axis retirement dependencies

#### §6.3.1 `anthropic.*` namespace emission dependency

```
H_T-AS-8 substitution (5 of 7 namespaces emitted)
        │
        │ depends on
        ▼
H_T-CP-1 retired (U-CP-01 lands; multi-LLM routing core operational)
        │
        │ enables
        ▼
H_T-AS-8 substitution → full 7-namespace coverage (anthropic.* becomes harness-emittable)
```

Until H_T-CP-1 retires, `anthropic.*` namespace remains absent — H_E owns the Anthropic provider surface and does not expose its telemetry. After H_T-CP-1 retires, H_T provider-portability layer carries the Anthropic provider with harness-authored instrumentation.

#### §6.3.2 F-CP-01 Stage 3b inversion ordering

```
H_T-OD-2 retired (U-OD-09 lands; harness.breaker.* canonical declaration)
        │
        │ + parallel
        ▼
H_T-CP-24 retired (U-CP-54 lands; CP-side ingestion of breaker namespace)
        │
        │ jointly enables
        ▼
H_T-CXA-5 inversion seam operational
```

Both endpoints land before the inversion seam activates. Neither blocks the other.

---

## §7 Substitution-risk discipline

### §7.1 Anti-leakage doctrine

Substitutions during 7a are *scaffolding*, NOT architectural commitments. Three failure modes the discipline forecloses:

| Failure mode | Mechanism | Foreclosed by |
|---|---|---|
| Shape-collapse | H_T contracts silently absorb H_E shape | Per-axis anti-leakage rules (§7.2–§7.6) with explicit H_E-vs-H_T contrast |
| Decomposition contamination | New H_T design surfaced during 7a borrows H_E's decomposition | Kickoff §6.2: no H_T design extension at η; new surfaces route to ADR back-flow (Phase 3) |
| Substitution permanence | Substitution becomes the design surface; retirement forgotten | §6 self-hosting milestone gradient binds retirement to specific unit IDs |

### §7.2 IS-axis anti-leakage rules

| Rule | Statement | Anti-pattern foreclosed |
|---|---|---|
| IS-AL-1 | `.claude/` hierarchy ≠ path-class registry. The 4 H_T path classes (`SKILLS` / `PROMPTS` / `ROUTING_MANIFEST` / `STATE_LEDGER`) are a typed registry with workflow-canonical resolution, not a filesystem-organization convention | Modeling H_T path classes after `.claude/` sub-directories |
| IS-AL-2 | H_E Checkpointing ≠ shadow-Git workload-class-opt-in checkpoint. H_E operates on session state at H_E-decided cadence; H_T operates on harness state at manifest-declared cadence | Authoring U-IS-13 to delegate checkpoint construction to H_E Checkpointing |
| IS-AL-3 | H_E conversation history ≠ state ledger entry shape. H_E retains `(role, content, tool_calls, tool_results)` tuples; H_T retains 6-field `(action_id, idempotency_key, actor, response_hash, timestamp, prior_event_hash)` entries per C-IS-05 §5 (relationship to the C-IS-07 §7.1 keying tuple deferred per C-IS-07 §7.4) | Re-deriving the H_T state ledger entry shape from H_E session history records |
| IS-AL-4 | `Bash` shell-outs are substitutions, not contracts. Hash-chain integrity via Python stdlib invoked through `Bash` is execution-time scaffolding; H_T contract at C-IS-06 is typed at U-IS-08/09/10 | Treating "we already have a Python script that does SHA-256 chain construction" as evidence that U-IS-08 is functionally complete |

### §7.3 AS-axis anti-leakage rules

| Rule | Statement | Anti-pattern foreclosed |
|---|---|---|
| AS-AL-1 | Permission modes ≠ SandboxTier enum. Permission modes gate tool-invocation approval; SandboxTier gates code-execution capability per blast-radius taxonomy (ADR-D2 v1.1) | Adopting H_E's 6-mode taxonomy as H_T's SandboxTier decomposition |
| AS-AL-2 | H_E built-in tools are NOT user-extensible H_T tools. All H_T tool surface lives behind MCP server boundary | Collapsing the MCP-server boundary at the H_T design site |
| AS-AL-3 | H_E Skills loading mechanism is isomorphic; H_T Skills filesystem residence additionally carries cross-axis IS-dependencies (filesystem-path classification per C-IS-01) | Treating "Skills work natively" as license to skip authoring U-AS-25 → U-AS-27 cross-axis edge declarations |
| AS-AL-4 | Workflow-shape-specific H_E surfaces (LSP / plan mode / Chrome / remote control / agent teams) are OUT OF H_T scope. H_T is workflow-shape-agnostic | Adding H_T primitives for LSP / plan mode / Chrome / remote control / agent teams under any pretext |

### §7.4 CP-axis anti-leakage rules

| Rule | Statement | Anti-pattern foreclosed |
|---|---|---|
| CP-AL-1 | H_E sub-agent topology (orchestrator-workers via `Agent` tool) ≠ H_T TopologyPattern 6-class enum (ORCHESTRATOR_WORKERS / DECENTRALIZED_HANDOFF / EVALUATOR_OPTIMIZER / PARALLELIZATION / ROUTING / SEQUENTIAL_PIPELINE) | Concluding "we already have orchestrator-workers" implies H_T-CP-10 is met |
| CP-AL-2 | H_E session resume binary operations ≠ ResumptionKind 5-class typed taxonomy (CRASH_RECOVERY / EXPLICIT_PAUSE / TIMEOUT / HITL_PENDING / VALIDATOR_FAIL) | Treating any H_E session resume as evidence that U-CP-19/U-CP-20/U-CP-21 are functionally complete |
| CP-AL-3 | H_E `--fallback-model` (single-target, overload-only, print-mode-only) ≠ H_T multi-step chain composition with cross-family fallback | Authoring U-CP-04 / U-CP-05 to wrap `--fallback-model` as the fallback chain implementation |
| CP-AL-4 | H_E `--model` single-LLM ≠ routing core. Single-LLM-during-7a is *runtime* substitution; multi-LLM design commitment unchanged at ADR-F1 v1.2 + U-CP-01 specification | Concluding "we use Claude exclusively" implies the project's multi-LLM commitment is abandoned |
| CP-AL-5 | H_E `CLAUDE.md` (prose convention loaded into system prompt) ≠ typed `WorkflowManifestEntry` schema with per-step override evaluator + audit | Treating `CLAUDE.md` declarations as functional substitute for typed workflow manifest entries |

### §7.5 OD-axis anti-leakage rules

| Rule | Statement | Anti-pattern foreclosed |
|---|---|---|
| OD-AL-1 | H_E telemetry (internal Claude Code analytics, closed surface) ≠ harness observability substrate (instruments the harness for harness operators) | Assuming H_E telemetry covers H_T's `sandbox.*` / `mcp.*` / `skill.*` / `topology.*` / `subagent.*` / `engine.*` / `audit.*` / `validator.fail.*` / `harness.breaker.*` namespace emission |
| OD-AL-2 | H_E `/cost` (session-grain coarse cost) ≠ H_T cost-attribution 5-step chain (per-attempt + idempotency-key join + hash-chain integrity composition + replay-aware dedup + cause_attribution invariance) | Authoring U-OD-17 → U-OD-22 to delegate cost computation to `/cost`-derived data |
| OD-AL-3 | All OTel emission during 7a happens at MCP server boundary (H_T-authored code). H_E does not participate in OTel emission. Boundary is load-bearing — prevents H_E internal telemetry from contaminating H_T trace schemas | Attempting to inject OTel SpanProcessors into H_E's emission path; constructing H_T spans by parsing H_E session logs |

### §7.6 CXA anti-leakage rule

| Rule | Statement | Anti-pattern foreclosed |
|---|---|---|
| CXA-AL-1 | Convention-based composition (H_E filesystem-primitives + sub-agents + operator-authored prompts) ≠ typed seam contracts (101 cross-axis edges across 6 buckets per CXA v2.1 §2.3 with Pattern P1 byte-exact alignment) | Treating "the sub-agent reads the JSONL ledger via convention" as functional satisfaction of the 36-edge CP→IS typed seam |

### §7.7 Cross-cutting anti-leakage discipline

| Rule | Statement |
|---|---|
| X-AL-1 | **Substrate boundary discipline.** H_E and H_T are distinct substrates. The boundary lives at the MCP server process: H_E on one side; H_T-authored harness code on the other. Boundary enforced by process isolation, not convention |
| X-AL-2 | **Retirement criterion fidelity.** Every substitution at §5 carries a retirement criterion. Retirement = (cited unit IDs landed) ∧ (substituted H_E surface no longer invoked at substitution site). Both conditions required |
| X-AL-3 | **No silent H_T design extension at η.** Per kickoff §6.2: if 7a execution reveals an H_T design gap, the gap routes to ADR back-flow (Phase 3) per `Phase_7_Kickoff_Prompt.md` §6, not silent absorption at the substitution mapping site |

### §7.8 X-AL-1 architectural diagram

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

H_T contracts are authored on the H_T side. H_E does not implement H_T contracts. The MCP boundary is the discipline-enforcement surface.

---

## §8 H_E-rich-zone disposition

Per kickoff §6.2: H_E provides capabilities for which H_T has no corresponding primitive. 10 candidates surfaced; all resolved within this artifact.

| H_E surface | Disposition | Anti-leakage anchor | Rationale |
|---|---|---|---|
| Plan mode (`EnterPlanMode` / `--permission-mode plan`) | Anti-leakage | AS-AL-4 | Session-state ergonomic; H_T's CP topology + AS gate policy compose this implicitly |
| LSP code intelligence | Anti-leakage | AS-AL-4 | Workflow-shape-specific (coding); H_T workflow-shape-agnostic |
| Session-scoped cron scheduling | Anti-leakage | CP-AL-1 (topology scope) | H_T scheduling at CP-axis workflow manifest level (R-CP-09); session-scoped cron does not match H_T durable-execution model |
| Background session lifecycle | Substitution route | (substitution at H_T-CP-22) | `claude attach/logs/stop/respawn/rm` substitutes for H_T pause/resume during 7a |
| Agent teams (experimental) | Anti-leakage | CP-AL-1 | Experimental H_E surface (env-gated); H_T C-CP-10 admits specific topology patterns |
| Remote control | Anti-leakage | AS-AL-4 | Session-multi-presence surface; outside H_T HITL scope at C-CP-20 |
| Chrome integration | Anti-leakage | AS-AL-4 | Workflow-shape-specific (web automation); reachable via MCP tool surface if needed |
| Plugin packaging | Anti-leakage | AS-AL-2 | H_T Skills primitive is the H_T extension surface; plugins are H_E-side packaging |
| Bare mode (`--bare`) | Anti-leakage | (ergonomic only) | Startup-time ergonomic without architectural meaning |
| JSON-schema-validated output (`--json-schema`) | Substitution route | (substitution at H_T-AS-2 strict-mode) | Transition-period validator surface during 7a |

**Disposition summary.** 8 of 10 candidates resolve as anti-leakage rules. 2 of 10 resolve as substitution routes already covered in §5.

---

## §9 Class 2 substitution-risk surface — H_T-CP-1 multi-LLM commitment

### §9.1 Surface statement

H_T-CP-1 substitution at §5.4 specifies single-`--model` selection during 7a. The project-level commitment "multi-LLM by design" per `<project_context>` and ADR-F1 v1.2 is **unmet at runtime** during the 7a substitution window.

### §9.2 Disposition

The 7a single-LLM posture is *runtime* substitution; the project commitment lives at *design* surface (ADR-F1 v1.2 + U-CP-01 specification at CP plan v2.3). Design commitment is unchanged; only runtime exercise is delayed.

| Layer | Status during 7a | Status at U-CP-01 landing |
|---|---|---|
| Project commitment (multi-LLM) | Unmet at runtime | Met at runtime |
| ADR-F1 v1.2 design commitment | Met at design | Met at design |
| CP plan v2.3 U-CP-01 specification | Met at specification | Met at specification + at runtime |
| H_T-CP-1 primitive operational | Substituted | Operational |

### §9.3 Risk-management discipline

| Anchor | Mechanism |
|---|---|
| Retirement criterion | §6.1 row H_T-CP-1: U-CP-01 landing |
| Anti-leakage rule | CP-AL-4 (§7.4) |
| Operator visibility | This §9 + §10.4 7d exit criterion #3 + Phase 6.5 Session 4 close handoff §5 + Session 5 (γ) Workflow v1.8 amendment scope + Session 7 (β) Phase 7 Session 1 Entry Directive substrate |

### §9.4 Class disposition

**Class 2** — operator-decision-blocking only at design-extension boundary. Substitution itself is admissible scaffolding. No design-phase artifact revision required. Surface recorded.

---

## §10 Phase 7 internal workflow (θ — sub-phase structure)

Pragmatic sub-phase derivation: 7a lands operational-minimum (L0 anchors + L1–L2 required for substitution scaffolding); 7b drives axis-internal completion topologically; 7c activates CXA seams; 7d verifies substitution retirement.

### §10.1 Sub-phase 7a — Bootstrap

#### §10.1.1 Goal

Operational substrate scaffolding plus L0 design declarations across all axes. §5 substitutions stable and invocable. Harness executes a trivial workload end-to-end through substituted primitives.

#### §10.1.2 Unit landings

| Axis | Units landed at 7a | Rationale |
|---|---|---|
| IS | U-IS-01, U-IS-02, U-IS-03, U-IS-04 | Path/tier registries + git-tier substrate |
| AS | U-AS-01, U-AS-02, U-AS-03, U-AS-04 | SandboxTier + tier-monotonicity + GateLevel + tool contract schema declaration |
| CP | U-CP-15, U-CP-22 | EngineClass enum + TopologyPattern enum (foundational taxonomies) |
| OD | U-OD-01, U-OD-04 | Deferral envelope + OTel SDK base |
| **Aggregate** | **12 units (8.6% of 139)** | — |

#### §10.1.3 Substitution scaffolding established

| Scaffolding surface | Mechanism |
|---|---|
| Path conventions | `CLAUDE.md` declares 4-class path semantics |
| State ledger | `.harness/state.jsonl` directory; append-write via `Bash(cat <<EOF)` |
| Hash-chain | Python stdlib SHA-256 + RFC 8785 canonicalization via `Bash` |
| MCP server | FastMCP at `.claude/mcp.json` local scope; ≥ 3 representative tools per axis |
| Sub-agent spawning | H_E `Agent` tool with prompt template |
| OTel emission | OTel SDK at MCP server boundary; OTLP to user-launched Collector |
| HITL primitive | H_E `AskUserQuestion` + permission-prompt approval |
| Sandbox tier dispatch | `--permission-mode` at session open |
| Workflow conventions | `CLAUDE.md` per-workflow declarations |

#### §10.1.4 Entry-gate criteria

| # | Criterion |
|---|---|
| 1 | Target stack committed (`Target_Stack_Commitment_v1.md` canonical) |
| 2 | Claude Code CLI workspace operational under DP-4 separate-workspace discipline |
| 3 | `Phase_7_Session_1_Entry_Directive.md` filed (Session 7 β output) |
| 4 | Claude Code CLI bootstrap substrate landed (Session 6 ε output) |
| 5 | v2.2 / v1 / v2.3 / v2.4 plans + CXA v2.1 + ADD v1.3 + PRD v1.1 + canonical ADRs + specs accessible |
| 6 | `Phase_7_Meta_Architecture_v1.md` (this document) accessible |
| 7 | No open Class 1 / Class 2 forks from Phase 6.5 arc close |

#### §10.1.5 Exit criteria

| # | Criterion |
|---|---|
| 1 | All 12 L0/L1–L2 operational-minimum units land with acceptance tests passing |
| 2 | All §10.1.3 substitution mechanisms invocable end-to-end (canonical-workload smoke test) |
| 3 | MCP server hosts ≥ 3 representative tools per axis (≥ 12 total) with strict Pydantic v2 validation |
| 4 | State ledger writes succeed under substitution; hash-chain verification readable via `Bash(jq + python)` |
| 5 | OTel emission visible at MCP server boundary; consumed by Collector subprocess; sqlite ring-buffer populated |
| 6 | 7a close handoff filed at execution workspace |

#### §10.1.6 Canonical-workload smoke test

```
INPUT:  "Read README.md, summarize it in 3 bullets, write summary to /tmp/summary.md,
         and append a state ledger entry recording the operation."

EXPECTED BEHAVIOR:
  1. main session ──> Agent spawn ──> sub-agent context
  2. sub-agent ──> MCP harness.read_file("README.md")       [H_T-AS-2 substitution]
  3. MCP server ──> Bash(cat README.md)
  4. MCP server ──> emit files.read.completed span          [H_T-AS-8 substitution]
  5. sub-agent ──> probabilistic summarization (LLM)        [H_T-CP-1 substitution]
  6. sub-agent ──> MCP harness.write_file(summary.md, ...)
  7. MCP server ──> Bash(write file) + emit span
  8. sub-agent ──> MCP harness.append_state_ledger(...)     [H_T-IS-5 substitution]
  9. MCP server ──> Bash(cat <<EOF >> .harness/state.jsonl)
 10. MCP server ──> compute SHA-256 chain via python stdlib  [H_T-IS-6 substitution]
 11. OTel Collector ingests all 4 spans into sqlite

VERIFICATION GATES:
  - State ledger entry parseable; idempotency_key + response_hash + prior_event_hash present
  - All 4 spans queryable from sqlite ring-buffer
  - Sub-agent returns summary matching README structure
  - No H_E built-in tool invoked outside MCP server boundary (per X-AL-1)
```

#### §10.1.7 Back-flow routing

| Class | Trigger | Routing |
|---|---|---|
| Class 1 | Design-defect surfaced | Halt 7a; route to design-phase workspace; back-flow per defect locus (ADR / plan / spec) |
| Class 2 | Operator-decision-blocking surface | Halt 7a; operator decision in execution workspace; back-flow if design artifact affected |
| Class 3 | Informational | Log at 7a close; continue |

#### §10.1.8 Reduced-HITL viability

**HITL viability: HIGH.** Operator presence required throughout. Estimated session count: 5–8 sessions at moderate density. Not overnight-executable.

### §10.2 Sub-phase 7b — Per-axis interior execution

#### §10.2.1 Goal

Drive each axis from L1 → L8 along intra-axis dependency-graph traversal. All 127 remaining units (139 − 12 landed at 7a) land under cluster-grained operator confirmation cadence.

#### §10.2.2 Axis sequencing under cross-axis substrate dependency

```
         IS  ────► AS  ────► CP  ────► OD
         (0)      (13)      (60)      (28)    cross-axis outbound edge cardinality

  Within-axis parallelism opportunity:
    AS and CP partially parallel after IS clusters 1–3 land
    OD waits until CP substrate seam exports operational (U-CP-54)
```

#### §10.2.3 Recommended axis stream schedule

| Stream | In flight | Trigger to start |
|---|---|---|
| IS (L1–L5; 13 remaining units) | IS-only | 7a exit met |
| AS (L1–L8; 29 remaining units) | IS + AS | IS clusters 1–3 land |
| CP (L1–L8; 53 remaining units) | IS + AS + CP | IS clusters 1–4 + AS clusters 1–2 land |
| OD (L1–L9; 32 remaining units) | IS + AS + CP + OD | CP U-CP-54 lands |

#### §10.2.4 Per-cluster traversal pattern

| Step | Action |
|---|---|
| 1 | Operator authorizes cluster open via `ask_user_input_v0` |
| 2 | Cluster units land in topological order within cluster |
| 3 | Per unit: implementation + acceptance tests + coverage matrix update + traceability cross-reference verification |
| 4 | Cluster coherence pass per `implementation-planner` SKILL.md §6 5-dimension audit |
| 5 | Operator confirms cluster close |
| 6 | Cluster substrate exposed at axis-level surface |

#### §10.2.5 Entry-gate criteria

| # | Criterion |
|---|---|
| 1 | 7a exit criteria all met |
| 2 | Axis sequencing order declared per §10.2.3 |
| 3 | Per-cluster substrate dependency check (cluster `Depends on:` resolves to landed units) |
| 4 | §5 substitution mechanisms remain stable through axis transitions |

#### §10.2.6 Exit criteria

| # | Criterion |
|---|---|
| 1 | All 139 atomic units land with acceptance tests passing |
| 2 | Within-axis dependency-graph traversal complete (all topological levels covered) |
| 3 | Per-axis coverage matrix verified (10 / 16 / 24 / 23 contracts × units; 100% coverage) |
| 4 | Substrate seam export manifests operational: U-IS-17, U-AS-33, U-CP-55, U-OD-34 |
| 5 | Within-axis acyclicity invariant preserved at runtime |
| 6 | 7b close handoff filed |

#### §10.2.7 Back-flow routing

Identical class taxonomy to §10.1.7. Three axis-specific routing surfaces:

| Surface | Class | Routing |
|---|---|---|
| Within-axis dependency-graph edge discovered insufficient | Class 2 | Operator decision; back-flow to plan revision (Phase 6) at design-phase workspace |
| Within-axis cycle introduced through implementation | Class 1 | Halt axis stream; route to design-phase plan revision |
| Cross-axis edge target mismatch | Class 2 | Operator decision; back-flow to CXA v2.1 revision OR plan revision |

#### §10.2.8 Reduced-HITL viability per axis

| Axis | HITL viability | Driver |
|---|---|---|
| IS | MEDIUM | Schema-heavy units; foundational primitives admit batch-author + morning-review |
| AS | HIGH | Sandbox + observability + MCP integration require per-unit verification |
| CP | HIGH | Routing + retry + fallback + validator runtime behavior; verification heavy |
| OD | HIGH | OTel emission + sampling + redaction require verification against telemetry stream |

Estimated session count: 25–40 sessions depending on stream-parallelism utilization.

### §10.3 Sub-phase 7c — Cross-axis integration

#### §10.3.1 Goal

Instantiate 101 cross-axis edges as typed contracts. Activate 5 CXA seams. Verify Pattern P1 byte-exact alignment across 15 namespaces and 40-cell bridging-arc transitions.

#### §10.3.2 Per-seam activation

| Seam | Activation trigger | Edge count | Verification gate |
|---|---|---|---|
| H_T-CXA-1 (AS → IS) | AS clusters 4 + 6 + 7 land | 13 | Idempotency-key join + Skills filesystem residence + secret-fetch canonicalization typed-contract |
| H_T-CXA-2 (CP → IS) | CP clusters 3 + 8 land | 36 | F2-substrate-join + entry-shape preservation + pause/resume F2-layer composition typed-contract |
| H_T-CXA-3 (CP → AS) | CP clusters 5 + 6 + 7 land | 24 | Sandbox-tier dispatch + sub-agent handoff + primitive observability composition typed-contract |
| H_T-CXA-4 (OD → IS/AS/CP) | OD clusters 3 + 5 + 7 land | 26 | Cost-attribution join + sampling input + preservation invariants typed-contract |
| H_T-CXA-5 (OD → CP inversion) | U-OD-09 + U-CP-54 §24.1.C joint-landing | 1 | F-CP-01 Stage 3b inversion + `harness.breaker.*` 7-attribute byte-exact |

Per-seam activation may begin during 7b (after endpoint clusters land) and complete during 7c.

#### §10.3.3 Pattern P1 byte-exact verification gate

```
NAMESPACE              PRODUCER SITE                       CONSUMER SITE
─────────────────────────────────────────────────────────────────────────
provider_discriminator OD-canonical                        OD-internal (U-OD-05)
anthropic.* (10 attrs) AS U-AS-31 (C-AS-14 §14.2)          OD U-OD-08
mcp.* (7 attrs)        AS U-AS-31 (C-AS-14 §14.3)          OD U-OD-08
skill.* (6 attrs)      AS U-AS-31 (C-AS-14 §14.4)          OD U-OD-08
managed_agents.* (3)   AS U-AS-31 (C-AS-14 §14.5)          OD U-OD-08
sandbox.* (7 attrs)    AS U-AS-16 (C-AS-15 §15.2)          OD U-OD-06
files.* (8 attrs)      AS U-AS-31 (C-AS-14 §14.6)          OD U-OD-08
memory.* (6 attrs)     AS U-AS-31 (C-AS-14 §14.7)          OD U-OD-08
hitl.* (4 attrs)       CP U-CP-46 (C-CP-20 §20.5)          OD U-OD-08
topology.* (10 attrs)  CP U-CP-31 (C-CP-14 §14.2)          OD U-OD-08
subagent.* (7 attrs)   CP U-CP-31 (C-CP-19)                OD U-OD-08
engine.* (3 attrs)     CP U-CP-21 (C-CP-09 §9.1)           OD U-OD-08
audit.* (7 attrs)      CP U-CP-46 (C-CP-20 §20.4)          OD U-OD-08
validator.fail.* (3)   CP U-CP-47 (C-CP-21 §21.5)          OD U-OD-08
harness.breaker.* (7)  OD U-OD-09 (C-OD-07 §7.1)           CP U-CP-54 §24.1.C
```

Gate: 15/15 byte-exact match against producer + consumer landed implementations. Single attribute-name divergence triggers Class 1 fork.

#### §10.3.4 Bridging-arc verification gate

40-cell verification per CXA v2.1 §4.3.3: 8 transitions × 5 axes = 40 cells. Gate: 40/40 PASS at runtime verification. Three T-perm-1 5-axis multiplicative tunable invariants:

| Invariant | Verification |
|---|---|
| T-perm-1 monotonic-tightening across all 8 transitions | Per-transition tier/level inequality assertion |
| Strict ascent on `GATE_POLICY` + `SANDBOX_TIER` at 3 deployment-surface ascent transitions | Per-transition strict-inequality assertion |
| 6 T-perm-1 closure-shape properties | Closure-shape property verification per CXA v2.1 §4.4 |

#### §10.3.5 CXA v2.1 → v2.2 revision

Class 3 informational CXA-OD-IS-EDGE-DRIFT (per IS plan v2.2 §0.9) resolved at 7c: 6-row OD→IS enumeration → 4-row per OD plan v2.4 §4.5.1. Revision lands as 7c sub-deliverable. Aggregate cross-axis edge count: 101 → 99.

#### §10.3.6 Entry-gate criteria

| # | Criterion |
|---|---|
| 1 | 7b exit criteria met for axes whose seams are being integrated |
| 2 | Pattern P1 producer-side declarer units (U-AS-16, U-AS-31, U-CP-21, U-CP-31, U-CP-46, U-CP-47, U-OD-09) landed |
| 3 | Pattern P1 consumer-side ingestion units (U-OD-05, U-OD-06, U-OD-07, U-OD-08, U-CP-54) landed |
| 4 | §5 substitution mechanisms for cross-axis seams remain stable |

#### §10.3.7 Exit criteria

| # | Criterion |
|---|---|
| 1 | All 99 cross-axis edges (post-CXA v2.2 revision) typed-contract-instantiated |
| 2 | Pattern P1 byte-exact alignment verified 15/15 |
| 3 | 40-cell bridging-arc verification PASS |
| 4 | 5 CXA seams activated and operational |
| 5 | CXA v2.1 → v2.2 revision filed; CXA-OD-IS-EDGE-DRIFT CLOSED |
| 6 | 7c close handoff filed |

#### §10.3.8 Back-flow routing

| Surface | Class | Routing |
|---|---|---|
| Pattern P1 namespace alignment break | Class 1 | Halt 7c; route to design-phase CXA revision; possibly plan revision at endpoint axis |
| 40-cell bridging-arc verification cell FAIL | Class 1 | Halt 7c; route to design-phase CXA + endpoint axis spec revision |
| Cross-axis edge contract type mismatch | Class 2 | Operator decision; back-flow to plan revision at endpoint axes |

#### §10.3.9 Reduced-HITL viability

**HITL viability: HIGH.** Pattern P1 + bridging-arc verification + per-seam contract instantiation require operator presence. Estimated session count: 6–10 sessions. Verification itself admits automated test + morning review.

### §10.4 Sub-phase 7d — Self-hosting milestones

#### §10.4.1 Goal

Verify substitution retirement per §6 milestone gradient. H_T primitives operational; H_E reduced to host-process role. Project commitment satisfaction verified at runtime.

#### §10.4.2 Retirement verification contract

Per X-AL-2 (§7.7):

```
Condition A: Cited unit ID(s) per §6.1 row LANDED with acceptance tests passing
Condition B: Substituted H_E surface NO LONGER INVOKED at substitution site
              (verified via runtime trace inspection + code-search audit)

Retirement = Condition A ∧ Condition B
```

#### §10.4.3 H_T-CP-1 multi-LLM commitment satisfaction

| Layer | 7a status | 7d status |
|---|---|---|
| Project commitment (multi-LLM) | Unmet at runtime | **Met at runtime** |
| ADR-F1 v1.2 design commitment | Met at design | Met at design |
| CP plan v2.3 U-CP-01 specification | Met at specification | Met at specification + at runtime |
| H_T-CP-1 primitive operational | Substituted (single `--model`) | **Operational (multi-provider routing)** |

7d exit gate REQUIRES U-CP-01 retirement verification. Class 2 substitution-risk surface from §9 **CLOSES** at this gate.

#### §10.4.4 H_E residual role at 7d close

| Residual H_E surface | Role | Anti-leakage discipline |
|---|---|---|
| Claude Code CLI runtime | Host process | Boundary at MCP protocol (X-AL-1) |
| `Agent` tool / sub-agent spawning | Spawning mechanism | Topology lives at H_T-CP-10 contract |
| `EnterWorktree` / worktree | Worktree mechanism | H_T worktree governance wraps H_E primitive |
| Skills loading | Skill discovery + loading | H_T Skills filesystem residence wraps H_E discovery |
| `AskUserQuestion` | HITL mechanism | H_T HITL primitive (H_T-CP-20) wraps H_E with 4-response palette |
| `Bash` / `Read` / `Write` / `Edit` / `Glob` / `Grep` | Filesystem + shell primitives | Only invoked at MCP server side (X-AL-1) |
| Permission gating | Coarse approval gate | H_T tool gate policy contract uses H_E rules as enforcement |

All other H_E surfaces retired at 7d.

#### §10.4.5 Entry-gate criteria

| # | Criterion |
|---|---|
| 1 | 7b axis exit complete |
| 2 | 7c CXA integration complete |
| 3 | Self-hosting milestone gradient (§6) cited per row with all unit IDs landed |
| 4 | H_T-CP-1 retirement (U-CP-01) landed and operational |

#### §10.4.6 Exit criteria

| # | Criterion |
|---|---|
| 1 | All §6 substitution retirements verified per §10.4.2 contract |
| 2 | H_E residual-role inventory per §10.4.4 audited at runtime (zero invocation of retired H_E surfaces) |
| 3 | H_T-CP-1 multi-LLM runtime commitment met — Class 2 surface from §9 CLOSED |
| 4 | Project commitment satisfaction verified at runtime: (a) multi-LLM by design, (b) production-grade engineering, (c) workflow-shape-agnostic, (d) observability-first |
| 5 | All §7 anti-leakage rules continue to hold (no shape-collapse / decomposition-contamination / substitution-permanence) |
| 6 | 7d close handoff + Phase 7 close handoff filed |

#### §10.4.7 Back-flow routing

| Surface | Class | Routing |
|---|---|---|
| Substitution retirement cannot be verified | Class 1 | Halt 7d; investigate; potentially back-flow to plan revision |
| H_E residual-role audit surfaces unauthorized H_E invocation | Class 1 | Halt 7d; route to implementation revision at substitution site |
| Project commitment satisfaction cannot be verified | Class 1 | Halt 7d; route to design-phase root-cause investigation |
| Anti-leakage rule violation surfaced | Class 2 | Operator decision; back-flow to substitution-site revision OR anti-leakage rule revision |

#### §10.4.8 Reduced-HITL viability

**HITL viability: MEDIUM-LOW.** Verification procedural and largely automatable. Estimated session count: 3–6 sessions.

### §10.5 Cross-cutting θ surfaces

#### §10.5.1 Sub-phase parallelism aggregate

```
                                    7a → 7b → 7c → 7d
                                    └────┴────┴────┘
                                     SEQUENTIAL (strict)

                                    Within 7b:
                                    IS  ─── stream 1 ───────────────►
                                          │
                                          └──► AS  ─── stream 2 ────►
                                          │
                                          └──► CP  ─── stream 3 ────►
                                                       │
                                                       └─► OD  ─ stream 4 ─►

                                    Within 7b-to-7c transition:
                                    H_T-CXA-1 / H_T-CXA-2 / H_T-CXA-3
                                      activatable during 7b as endpoints land
                                    H_T-CXA-4 / H_T-CXA-5 require OD complete
```

#### §10.5.2 Reduced-HITL viability heat-map

| Sub-phase | HITL viability | Overnight-executable surfaces |
|---|---|---|
| 7a | HIGH | None |
| 7b — IS | MEDIUM | IS clusters 1–3 batched (~5 units) |
| 7b — AS | HIGH | Cluster 7 namespace-declarers (~5 units) |
| 7b — CP | HIGH | Cluster 9 namespace declarers (~3 units) |
| 7b — OD | HIGH | Clusters 1–2 declarative (~5 units) |
| 7c | HIGH | Automated test execution + morning review |
| 7d | MEDIUM-LOW | Retirement audit + residual-role audit (entire scope) |

Aggregate operator-burden estimate: 7a (5–8) + 7b (25–40) + 7c (6–10) + 7d (3–6) = **39–64 sessions**.

#### §10.5.3 Back-flow routing aggregate

All Class 1 forks halt the affected sub-phase + stream and back-flow to design-phase workspace per `Phase_7_Kickoff_Prompt.md` §6. Class 2 forks halt at operator-decision boundary; back-flow optional. Class 3 logged + continue.

| Defect locus | Back-flow target |
|---|---|
| ADR design commitment | ADR (Phase 3a/3b) → ADD (Phase 3d) → spec (Phase 5) → plan (Phase 6) |
| Spec contract | Spec (Phase 5) → plan (Phase 6) |
| Plan atomic unit | Plan (Phase 6) |
| CXA cross-axis edge | CXA v2.1 → v2.2 / v2.3 revision |
| PRD requirement | PRD (Phase 4) |
| Workflow discipline | Workflow v1.7 → v1.8 amendment scope |

#### §10.5.4 Operator-burden eval primitive

Per C-CP-21 §21.3, operator-burden eval lands at H_T-CP-21 retirement (U-CP-47 / U-CP-48 / U-CP-51 / U-CP-52). Operator-burden estimates at §10.5.2 are *unmeasured* during 7a + early 7b. After H_T-CP-21 retires (estimated mid-7b under CP stream), estimates become measurable.

---

## §11 η ↔ θ coupling verification

| η surface | θ binding site | Coupling |
|---|---|---|
| §5 substitution mapping table | §10.1.3 7a scaffolding establishment | 7a establishes all §5 substitutions as operational |
| §6 self-hosting milestone gradient | §10.4.2 retirement verification matrix | 7d verifies each §6 gradient row |
| §7 anti-leakage discipline | §10.4.6 exit criterion #5 | 7d verifies no anti-leakage rule violated through 7b–7d |
| §9 Class 2 H_T-CP-1 substitution risk | §10.4.3 multi-LLM commitment satisfaction + §10.4.6 exit criterion #3 | 7d CLOSES Class 2 surface at U-CP-01 retirement verification |
| §6.3 cross-axis retirement dependencies | §10.2.3 axis sequencing + §10.3.2 CXA seam activation | 7b/7c ordering respects retirement dependency graph |
| §8 H_E-rich-zone disposition | §10.4.4 H_E residual-role inventory | 7d residual-role inventory consistent with §8 anti-leakage dispositions (zero adopted H_E-rich-zone surfaces) |

**η ↔ θ coupling: ✅ VERIFIED at all 6 surfaces.**

---

## §12 Coherence pass verdict

5-dimension audit per `implementation-planner` SKILL.md §6 + `spec-writer` SKILL.md canonicalization discipline:

| Dimension | Verification | Result |
|---|---|---|
| Atomicity | Per-primitive granularity preserved across §2, §5, §6 (49 primitives + 5 seams consistent) | ✅ PASS |
| Spec-traceability | All unit ID citations resolve against v2.2 / v1 / v2.3 / v2.4 plans + CXA v2.1; 100% sample-citation resolution verified | ✅ PASS |
| Dependency-awareness | Cross-axis retirement dependencies (§6.3) consistent with CXA v2.1 §2.4 outbound posture (IS=0, AS=13, CP=60, OD=28 outbound) | ✅ PASS |
| Implementation-grade-detail | Substitution mechanisms (§5) cite specific H_E surfaces with permission gates [HIGH — tools-reference]; θ sub-phase entry/exit criteria measurable | ✅ PASS |
| Anti-pattern audit | η ↔ θ coupling verified (§11); no H_T design extension at η; no Class 1 forks; 1 Class 2 surface documented (§9; non-blocking) | ✅ PASS |

**Coherence pass: ✅ PASS at all 5 dimensions.** Artifact authorization granted.

### §12.1 Fork inventory

| Class | Count | Description |
|---|---|---|
| Class 1 | 0 | None surfaced through η + θ authoring |
| Class 2 | 1 | H_T-CP-1 multi-LLM substitution-risk surface (§9; recorded, non-blocking; design artifacts unchanged) |
| Class 3 | 6 | CXA-OD-IS-EDGE-DRIFT (§2.5); cross-axis retirement ordering anthropic.* (§6.3.1); cross-axis retirement ordering F-CP-01 Stage 3b (§6.3.2); 10 H_E-rich-zone dispositions (§8; collectively recorded); 7b axis-stream parallelism schedule (§10.2.3); operator-burden eval substitution during 7a + early 7b (§10.5.4) |

---

## §13 Filing footer

| Field | Value |
|---|---|
| Artifact | `Phase_7_Meta_Architecture_v1.md` |
| Version | v1 |
| Status | Proposed (Phase 6.5 Session 4 ζ primary deliverable; pending arc-close clearance) |
| Date | 2026-05-15 |
| Phase | Phase 6.5 Session 4 (η + θ) close |
| Authoring discipline | `council-orchestrator` SKILL.md selective-convening (C1 + C7 + C11); `spec-writer` SKILL.md canonicalization; `implementation-planner` SKILL.md §4 spec-traceability + §6 coherence-pass |
| Predecessor | `Phase_6_5_Session_3_Close_Handoff.md`; `Phase_6_5_Session_4_Kickoff.md`; v2.2 / v1 / v2.3 / v2.4 plans + CXA v2.1; `Target_Stack_Commitment_v1.md`; `Plan_Executability_Audit_v1.md` |
| Companion artifact | `Phase_6_5_Session_4_Close_Handoff.md`; `Phase_6_5_Session_5_Kickoff.md` |
| Successor (arc) | Phase 7 execution at separate Claude Code CLI workspace per Workflow DP-4 default |
| Filing destination | `/mnt/user-data/outputs/Phase_7_Meta_Architecture_v1.md` → operator pushes to `/mnt/project/` |

---

*End of Phase 7 Meta-Architecture v1. Filed at Phase 6.5 Session 4 (η + θ) close. Governs Phase 7 execution against the v2.2 / v1 / v2.3 / v2.4 implementation plans under chicken-and-egg substitution discipline.*
