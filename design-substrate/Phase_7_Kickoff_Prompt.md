# Phase 7 Kickoff Prompt — Execution Phase (Portable to New Workspace)

*This artifact is portable. It is authored at the close of the design-phase project workspace and travels to the execution-phase workspace per `Project_Workflow_v1_7.md` DP-4 default ("Fork project into separate workspace for implementation execution | After P6-CK clearance"). It is self-contained for the new workspace's opening read.*

---

## §1 Identity + provenance

| Field | Value |
|---|---|
| Artifact | `Phase_7_Kickoff_Prompt.md` |
| Type | Portable phase-entry kickoff prompt; framing artifact for new workspace |
| Status | **Filed** at design-phase workspace; ready for transfer to execution workspace |
| Date | 2026-05-14 |
| Predecessor phase | Phase 6 — atomic implementation planning (CLOSED at `P6-CK_Iter4_Revision_Cycle_Close_Handoff.md`; cascade-substrate-clearance ISSUED; Phase 7 entry authorization GRANTED) |
| Predecessor artifact | `P6-CK_Iter4_Revision_Cycle_Close_Handoff.md` §9.2 (entry-gate disposition CLEARED) |
| Workflow authority | `Project_Workflow_v1_7.md` §2.6 + DP-4 (Phase 7 specification deferred to v1.8 §2.7 amendment; `Path_Delta_Workflow_v1_7_to_v1_8_Revision_Log_Entry.md` flags §4.1.4.6 amendment; §2.7 phase specification recommended as parallel work but non-blocking) |
| Forking discipline | DP-4 default selected by operator: Phase 7 runs in a **separate workspace** from the design-phase project. The design-phase workspace remains intact as canonical archive + back-flow target for execution-phase-discovered design defects (see §6 below). |

---

## §2 Project framing carried forward + Phase-7-specific updates

### §2.1 Carried forward verbatim from design-phase V3 system prompt

The design-phase project operated under V3 system prompt commitments. The following V3 commitments are **carried forward verbatim into Phase 7 execution** and must be loaded at the new-workspace system prompt:

- **Multi-LLM by design.** The harness supports routing across multiple LLMs.
- **Local development environment as design-time deployment target.** "Local development environment" means developer-owned hardware; **NOT** local-first software principles (offline-first, CRDTs, local primary storage); cloud-managed and hybrid deployment surfaces remain in scope as architectural options.
- **Production-grade engineering.** Source-grounded decisions, deterministic outer-harness discipline, observability as first-class, security boundaries at the harness level, reliability primitives composed correctly.
- **Operating principles.** Source-grounding every non-trivial claim; specific citations; confidence labels (`[HIGH]` / `[MODERATE]` / `[SPECULATIVE]`); never invent citations / version numbers / benchmarks / vendor capabilities / quotes; distinguish deterministic-outer-harness vs probabilistic-LLM-output where it materially changes a decision.
- **Anti-fabrication discipline.** A spec contract citation, ADR section reference, or atomic unit identifier that cannot be verified against the loaded substrate is a fabrication; halt and surface rather than invent.

### §2.2 Updated at Phase 7 (design-phase outputs ARE NOW committed)

The V3 system prompt declared the following "NOT committed at this stage":

- User persona; stack choices; orchestration substrate; durable-execution engine; observability backend; model providers; tool protocols; framework adoptions; language ecosystems; specific tools.

**At Phase 7 entry these are NOW COMMITTED** via the design-phase substrate inventory at §3 below. Specifically:

- **Persona is committed** at `Persona_Document_v1.md`.
- **Architectural decisions are committed** at F1–F5 + D1–D6 ADRs (versioned) consolidated at ADD v1.3.
- **Observable behavior is committed** at PRD v1.1.
- **Contract surfaces are committed** at the 4 axis specs (IS v1.2 + AS v1.1 + CP v1.3 + OD v1.3) + cross-axis composition spec (`Specification_v1.md` v1.1).
- **Atomic unit decomposition is committed** at the 4 axis plans (IS v2.1 + AS v1 + CP v2.3 + OD v2.3) + cross-axis composition document (CXA v2.1).
- **F2-12 cascade closure** is recorded at `F2-12_Closure_Declaration.md` (closure substrate at D1 v1.2 + D6 v1.2 + cascade artifacts).

**Phase 7 execution operates AGAINST these commitments, NOT free to revise them.** Design-phase artifacts are read-only at execution. Defects surfaced during execution route back to the design-phase workspace per §6 below; they are NOT silently revised at the execution workspace.

### §2.3 Scope discipline at Phase 7

The V3 scope discipline is preserved with one adjustment:

- **Design phase V3:** "Do NOT respond as if a specific persona, stack, or deployment choice has already been made unless the user explicitly states it in the current session."
- **Phase 7 update:** Persona, stack-shape (per ADRs), and contract surfaces ARE made — they are the v2.3 plan substrate. Execution-phase responses MUST cite these commitments as authoritative; questioning them is a back-flow signal (see §6), not a design-phase deliberation.
- **Stack-detail still committable at execution.** ADRs commit to *kinds* (e.g., "durable-execution coordination spine" per F3 v1.1) without naming a *specific* tool. Execution-phase agent selects the specific tool (e.g., Temporal vs LangGraph vs custom) subject to the F3 contract surface. The selection is execution-phase scope; not a back-flow to design.

---

## §3 Canonical substrate inventory

The execution workspace must load (or have available for reference) the following artifacts. All paths reference the design-phase workspace at the design-phase-close timestamp 2026-05-14.

### §3.1 Top-of-stack — implementation plans (primary execution substrate)

| Artifact | Version | Role at Phase 7 |
|---|---|---|
| `Implementation_Plan_Information_Substrate_v2_1.md` | v2.1 | IS-axis atomic units (U-IS-01 through U-IS-17) |
| `Implementation_Plan_Action_Surface_v1.md` | v1 | AS-axis atomic units (U-AS-01 through U-AS-33) |
| `Implementation_Plan_Control_Plane_v2_3.md` | **v2.3** | CP-axis atomic units (U-CP-01 through U-CP-55); revised at this session's Segment 1 absorbing F2-01 + F2-02 + F2-03 |
| `Implementation_Plan_Operational_Discipline_v2_3.md` | **v2.3** | OD-axis atomic units (U-OD-01 through U-OD-34); revised at this session's Segment 2 absorbing F1-01 + F2-04 + F3-01 + F3-02 acknowledged-deferred |
| `Cross_Axis_Composition_Document_v2_1.md` | v2.1 | Cross-axis composition seams + aggregate dependency graph + aggregate coverage matrix + topological sort |

### §3.2 Contract substrate — axis specifications (consulted from plan units' `Implements:` citations)

| Artifact | Version | Status |
|---|---|---|
| `Spec_Information_Substrate_v1.md` | v1.2 | P5-CK cleared; no F2-12 cascade |
| `Spec_Action_Surface_v1.md` | v1.1 | P5-CK cleared |
| `Spec_Control_Plane_v1_3.md` | **v1.3** | F2-12 cascade Step 5a |
| `Spec_Operational_Discipline_v1_3.md` | **v1.3** | F2-12 cascade Step 5b |
| `Specification_v1.md` | v1.1 | Cross-axis composition spec (top-level) |

### §3.3 Architectural substrate — ADRs (consulted from spec contract `ADR commitments honored:` rows)

| ADR | Version | Status | Source location |
|---|---|---|---|
| ADR-F1 | v1.2 | Accepted | `/mnt/project/ADR-F1.md` |
| ADR-F2 | v1.2 | Accepted | `/mnt/project/ADR-F2.md` |
| ADR-F3 | v1.1 | Accepted | `/mnt/project/ADR-F3.md` |
| ADR-F4 | v1.1 | Accepted | `/mnt/project/ADR-F4.md` |
| ADR-F5 | v1.1 | Accepted | `/mnt/project/ADR-F5.md` |
| ADR-D1 | **v1.2** | Proposed (F2-12 cascade Step 2a; promotion to Accepted at operator discretion post-cascade-close) | `ADR-D1_v1_2.md` |
| ADR-D2 | v1.1 | Accepted | `/mnt/project/ADR-D2.md` |
| ADR-D3 | v1.2 | Accepted | `/mnt/project/ADR-D3.md` |
| ADR-D4 | v1.1 | Accepted | `/mnt/project/ADR-D4.md` |
| ADR-D5 | v1.3 | Accepted | `/mnt/project/ADR-D5.md` |
| ADR-D6 | **v1.2** | Proposed (F2-12 cascade Step 2b) | `ADR-D6_v1_2.md` |

Consolidating artifact: **ADD v1.3** at `Architectural_Design_Document_v1_3.md` (post-F2-12 cascade Step 3).

### §3.4 Requirements substrate — PRD

| Artifact | Version | Role |
|---|---|---|
| `PRD_v1_1.md` | v1.1 | Observable-behavior requirements (R-IS-01 through R-IS-04 / R-AS-01 through R-AS-07 / R-CP-01 through R-CP-12 / R-OD-01 through R-OD-08); cited transitively through spec contracts per design-phase spec-to-plan-traceability discipline |

### §3.5 Persona substrate

| Artifact | Version | Role |
|---|---|---|
| `Persona_Document_v1.md` | v1 | Persona-tier monotonic discipline at units implementing C-AS-12 / C-CP-19 / C-OD-13 |

### §3.6 Closure record + governance substrate

| Artifact | Role |
|---|---|
| `F2-12_Closure_Declaration.md` | F2-12 carry-forward formal closure record; cascade Step 1–6b inventory; OD-F212-5.B disposition record |
| `P6-CK_Iter4_Revision_Cycle_Close_Handoff.md` | Revision-cycle close handoff; cascade-substrate-clearance ISSUED; Phase 7 entry authorization GRANTED |
| `Governance_Substrate_Propagation_Note_F1-01.md` | F1-01 §1.5 → §14.5.1 citation correction propagation record |
| `Project_Workflow_v1_7.md` | Workflow authority at design-phase close; v1.8 amendment proposed at `Path_Delta_Workflow_v1_7_to_v1_8_Revision_Log_Entry.md` (operator-discretion filing; non-blocking for Phase 7 entry) |
| `Project_Workflow_Revision_log.md` | Workflow revision history |

### §3.7 Adversarial review substrate (read for context; not for revision)

P6-CK iter 1–4 adversarial reviews + revision-cycle close handoff (Iter 4 revision-cycle within Iter 4 scope per `P6-CK_Iter4_Revision_Cycle_Close_Handoff.md` §2.1 single-iteration discipline):

- `Adversarial_Review_6.md` (Iter 1)
- `Adversarial_Review_6_iter2.md` (Iter 2)
- `Adversarial_Review_6_iter4.md` (Iter 4 — cascade-substrate-verification iteration)
- `P6-CK_Iter1_Revision_Cycle_Close_Handoff.md` (Iter 1 revision-cycle close precedent)
- `P6-CK_Iter4_Revision_Cycle_Close_Handoff.md` (Iter 4 revision-cycle close — this revision-cycle)

---

## §4 Execution discipline at Phase 7

### §4.1 The atomic-unit execution contract

Per `implementation-planner` SKILL.md §2 consequence 2:

> Post-plan, only execution remains. The planner does not produce further design decisions. The plan's job is to give the executor enough commitment to execute without designing.

Phase 7 execution operates at the granularity of **atomic units** declared in the v2.3 plans. Each atomic unit has:

- A spec contract citation (`Implements: [C-AXIS-NN §X.Y]`)
- A dependency declaration (`Depends on: [U-AXIS-MM, ...]` including cross-axis edges with `(cross-axis: Y)` annotation)
- A signature block (data types, functions, schemas; specification-grade authoring; executor implements, does not redesign)
- An acceptance criteria list (testable invariants)
- A test specification (named tests; executor implements test cases)
- A rollback boundary (what reverts together as a coherent unit)

**Execution unit-by-unit, in topological order**, per the dependency graph at each axis plan + the aggregate graph at CXA v2.1.

### §4.2 Foundational-first ordering

The dependency graph terminates at Level 0 foundational units with `Depends on: (none)`. These are the canonical execution entry points:

- IS axis Level 0 units: foundational data types + state-ledger entry shape + hash-chain construction discipline (canonical IS-axis ledger-write site is the F3-02 acknowledged-deferred resolution target — see §7 below)
- CP axis Level 0 units: namespace declarations (U-CP-01 routing.*; U-CP-07 fallback.* + harness.breaker.* + retry.* per v2.3 amendment; U-CP-10 LifecycleEventClass enum; U-CP-11 lease.*; etc.)
- AS axis Level 0 units: foundational ACL + sandbox tier + manifest schemas
- OD axis Level 0 units: foundational cost-attribution + telemetry primitives

**Cross-axis dependencies declared explicitly** at unit `Depends on:` lines with `(cross-axis: Y)` annotation. Execution order MUST respect cross-axis edges; if an axis's Level 0 unit depends on another axis's unit, the dependent axis's unit blocks until the dependency is satisfied.

### §4.3 Per-unit execution shape (recommended; not pre-committed)

For each atomic unit, the recommended execution shape:

1. **Read** the unit declaration end-to-end (Implements + Depends on + Inputs + Files affected + Signatures + Acceptance + Tests + Rollback boundary).
2. **Read** the cited spec contract section at full granularity (per the §3.2 spec inventory).
3. **Read** the parent ADR section(s) the spec contract `ADR commitments honored:` row cites (per the §3.3 ADR inventory).
4. **Verify** all declared dependencies (the units this unit depends on) are complete and their outputs satisfy this unit's `Inputs`.
5. **Implement** the unit's signatures + tests at production-grade fidelity. The plan's signatures are specification-level; the executor's task is to materialize them at the target language/stack.
6. **Verify** the acceptance criteria are met by the implementation (each criterion → test → green).
7. **Mark** the unit as complete in the execution workspace's progress ledger (workspace-internal artifact, not specified at this kickoff).

### §4.4 Deterministic outer harness vs probabilistic LLM output

The design phase rigorously separated:

- **Deterministic** outer-harness components: schemas, linters, gates, idempotency keys, sandboxes, OTel span emission, hash-chain construction, dedup algorithms, retry mechanics, breaker state machines.
- **Probabilistic** LLM-output components: agent inference outputs, tool-call payloads at the model surface, validator-judge probabilistic outputs.

Phase 7 execution preserves this boundary. Tests on deterministic components MUST be deterministic (no LLM-in-the-test-loop). Tests on probabilistic components use the design-phase eval methodology (per OD axis C-OD-23 operator-burden eval primitive + IS-side data-fixture discipline).

---

## §5 Session shape (recommended; new-workspace operator decisions)

The new-workspace operator selects session pacing. Recommended patterns (not pre-committed):

| Pattern | Shape | When to use |
|---|---|---|
| **Per-unit sessions** | One session per atomic unit | Highest traceability; fits ~120 units × ~30-60 min/unit; multi-day cumulative wall-clock |
| **Per-cluster sessions** | One session per per-axis cluster (CP plan has 9 clusters; OD plan has 8; etc.) | Medium pacing; respects intra-cluster cohesion; ~30 sessions cumulative |
| **Per-axis sessions** | One session per axis (4 sessions + 1 for cross-axis composition seams) | Fastest; assumes high-throughput per-session execution; risk of mid-session context exhaustion |
| **Topological-band sessions** | One session per topological level across all axes | Maximizes parallel implementation; fits well with multi-executor coordination |

The new-workspace kickoff session should select the pattern at session 1 entry via operator decision. None is pre-committed at this kickoff.

---

## §6 Defect routing — back-flow to design-phase workspace

Execution may surface design-phase defects: a spec contract that doesn't compose at implementation; an acceptance criterion that's infeasible at the target stack; a cross-axis composition that fails at execution. Per `implementation-planner` SKILL.md §2 consequence 1:

> The implementation planner never extends a specification commitment. If authoring surfaces a specification-shaped gap (a deferred-to-implementation item the unit would need to commit to, a contradiction between two contracts at a composition site, a missing surface the contract does not commit), the gap is itself the finding — back-flow to Phase 5 per workflow §4 fork-handling.

At Phase 7 the same discipline applies, escalated to the appropriate design-phase layer:

| Defect class | Routing | Design-phase target |
|---|---|---|
| **Plan unit defect** (acceptance criterion infeasible at target stack; signatures mis-decomposed; tests mis-specified) | Open ticket against design-phase workspace; design-phase implementation-planner revision pass at affected unit | Phase 6 revision-pass (analogous to Iter 1–4 revision cycles) |
| **Spec contract defect** (contract under-specifies; contracts contradict at composition site; contract claims a capability the stack cannot deliver) | Open ticket against design-phase workspace; spec-writer revision pass at affected contract | Phase 5 revision-pass |
| **ADR-level defect** (architectural commitment infeasible; ADR consequences not honored by downstream substrate) | Open ticket against design-phase workspace; council-orchestrator + harness-adversarial-reviewer convening | Phase 3a or 3b revision-pass |
| **PRD-level defect** (observable behavior infeasible; requirement not implementable) | Open ticket against design-phase workspace; prd-author revision pass | Phase 4 revision-pass |
| **Persona-level defect** (persona substrate mis-frames execution-time decision) | Open ticket against design-phase workspace; systems-architect revision pass | Phase 2 revision-pass |
| **Workflow-level defect** (workflow grammar / phase ordering / fidelity-grammar issue surfaces at execution) | Open ticket; operator-discretion Workflow §7 amendment + revision-log entry | Workflow revision-pass (Path δ-style) |

**Critical discipline.** Execution-phase agents must NOT silently work around design defects. The design-phase commitments are the canonical contract; defects route back rather than being absorbed at execution. This preserves the design-execution boundary and prevents implementation-time drift from undermining the design phase's adversarial review investment.

---

## §7 Forward-flagged concerns inherited from Phase 6 close

The following concerns are KNOWN at Phase 6 close. They are NOT Phase-7-entry-blocking per `P6-CK_Iter4_Revision_Cycle_Close_Handoff.md` §5.2, but execution-phase agents should be aware:

### §7.1 F3-02 acknowledged-deferred — IS-axis ledger-schema unit ownership

- **Surface:** `Implementation_Plan_Operational_Discipline_v2_3.md` U-OD-20 acceptance #11 (cross-axis dependency placeholder `U-IS-NN`) + §0.8 row F3-02.
- **Disposition:** Deferred to future IS-axis revision-pass per session-open OD at the Iter 4 revision-cycle session (default/recommended disposition).
- **Execution-phase implication:** When the executor reaches U-OD-20 acceptance #15 (hash-chain integrity composition; `ledger_entry_hash` 8-field SHA-256 per OD spec v1.3 §14.5.1), the OD-side composition surface stands independently of the IS-axis canonical ledger-write site. The IS-axis canonical chain construction at C-IS-06 §6.3 is the authoritative reference. If execution surfaces a coordination gap between OD-side composition and IS-side canonical chain construction, route back to design-phase as an IS-axis revision-pass.

### §7.2 `replay_semantic_divergence` C5 cause_attribution catalog extension

- **Surface:** `Implementation_Plan_Operational_Discipline_v2_3.md` §0.8 row 3 (preserved from v2.2); referenced at U-OD-20 acceptance #13 ESCALATION semantics.
- **Disposition:** Forward-flagged for future ADR-D5 revision pass + corresponding OD spec + plan absorption per v2.2 disposition.
- **Execution-phase implication:** ESCALATION events emitted from `cause_attribution_invariance_check` use `replay_semantic_divergence` as the `validator.fail.cause_attribution` value. The ADR-D5 v1.2 §1.10.1 `validator.fail.cause_attribution` open-set enum has not yet absorbed this value canonically. Execution proceeds with the OD-spec-v1.3 + D6-v1.2 declaration as authoritative; ADR-D5 catalog extension is the deferred reconciliation target.

### §7.3 `Project_Workflow_v1_8.md` filing status

- **Surface:** `Path_Delta_Workflow_v1_7_to_v1_8_Revision_Log_Entry.md` (filed at design-phase workspace).
- **Disposition:** Operator-discretion filing; non-blocking for Phase 7 entry per `P6-CK_Iteration_4_Entry_Handoff.md` §8.2 + `P6-CK_Iter4_Revision_Cycle_Close_Handoff.md` §9.3.
- **Execution-phase implication:** Workflow v1.7 is canonical at Phase 7 entry. v1.8 amendment is asynchronous; no Phase 7 dependency on v1.8 filing. A §2.7 Phase 7 specification is RECOMMENDED as parallel design-phase work but does NOT block execution.

### §7.4 Iter-3 Path C disposition re-entry route

- **Surface:** `Iter-3_Path_C_Disposition_Cascade_Sequencing_Note.md` at design-phase workspace.
- **Disposition:** Suspended pre-cascade; remains independently routable.
- **Execution-phase implication:** None unless explicitly invoked by operator. Independent of Phase 7 execution.

---

## §8 Out-of-scope at new workspace

The following are explicitly OUT of scope at the new execution workspace. They remain at the design-phase workspace:

| Item | Workspace ownership |
|---|---|
| Design-phase skills (`implementation-planner`, `council-orchestrator`, `harness-adversarial-reviewer`, `spec-writer`, `prd-author`, `systems-architect`, C1–C11 voice skills) | Design-phase workspace |
| Adversarial review iteration cycles | Design-phase workspace |
| ADR / ADD / PRD / spec / plan revision passes | Design-phase workspace (triggered by back-flow per §6) |
| Workflow revisions (Path δ / future paths) | Design-phase workspace (operator authority per Workflow §1) |
| Iter-3 Path C disposition re-entry | Design-phase workspace (independent route) |
| F2-12 closure record amendment | Closed; preserved as cascade-close record |

### §8.1 Execution-phase agent and skill selection

The new-workspace operator selects:

- **Execution agent.** Candidates include Claude Code (per V3 product knowledge — agentic CLI tool for codebase work), operator-authored implementation, hybrid LLM-assisted operator-driven implementation, or other. NOT pre-committed at this kickoff.
- **Test runner + harness.** Per target stack (TypeScript / Python / Rust / etc. — also operator decision per ADR-F1 v1.2 multi-LLM-provider-abstraction-shape consequences and ADR-D-layer stack consequences).
- **CI/CD substrate.** Operator decision; out of design-phase scope.
- **Build / packaging discipline.** Operator decision; out of design-phase scope.

No new-workspace skill is pre-committed. If a `harness-executor` skill is desirable, it should be JIT-built at new-workspace session 1 per design-phase skill-build precedent (e.g., implementation-planner skill was JIT-built at Phase 6 entry).

---

## §9 Entry-gate prerequisites

Phase 7 entry at new workspace requires:

| # | Prerequisite | Verification |
|---|---|---|
| 1 | All §3.1 implementation plan artifacts at canonical v2.3 / v2.1 / v1 revisions loaded into new workspace (or accessible as cross-workspace reference) | New-workspace operator verifies file inventory |
| 2 | All §3.2 spec artifacts at v1.x canonical revisions accessible | Same |
| 3 | All §3.3 ADR artifacts at canonical revisions accessible | Same |
| 4 | `ADD_v1_3` + `PRD_v1_1` + `Persona_Document_v1` accessible | Same |
| 5 | `P6-CK_Iter4_Revision_Cycle_Close_Handoff.md` §9.2 entry-gate disposition CLEARED | Confirmed at design-phase workspace 2026-05-14 ✅ |
| 6 | F2-12 closure record (`F2-12_Closure_Declaration.md`) accessible | Same |
| 7 | New-workspace operator confirms understanding of §6 back-flow discipline | New-workspace session 1 confirmation |
| 8 | New-workspace operator selects execution agent + session pattern + target stack | New-workspace session 1 decisions |

---

## §10 First-session opening read recommendation

The new-workspace operator's session 1 opening read sequence (recommended):

1. **This kickoff prompt** (substrate inventory + execution discipline + back-flow routing).
2. **`P6-CK_Iter4_Revision_Cycle_Close_Handoff.md`** (entry-gate authorization record + cascade-substrate-clearance disposition).
3. **`Cross_Axis_Composition_Document_v2_1.md`** (aggregate dependency graph + aggregate coverage matrix + topological sort — the load-bearing execution-ordering substrate).
4. **`Implementation_Plan_Information_Substrate_v2_1.md`** + foundational Level 0 units of other axes (the canonical execution entry points).
5. **As needed during execution:** the per-unit substrate chain (plan unit → spec contract → ADR commitment → ADD / PRD / persona transitively).

**Recommended session 1 deliverable:** A new-workspace-internal execution plan artifact declaring:
- Selected session pattern (per §5)
- Selected execution agent + target stack
- First atomic unit(s) to execute + their substrate-read chain
- Workspace-internal progress-ledger schema

This kickoff prompt does not pre-author the session 1 artifact. Operator authority at new-workspace entry.

---

## §11 Filing footer

| Field | Value |
|---|---|
| Artifact | `Phase_7_Kickoff_Prompt.md` |
| Status | **Filed at design-phase workspace** as portable kickoff |
| Phase | Phase 6 close → Phase 7 entry boundary |
| Authoring discipline | Workflow v1.7 §7 fidelity-grammar; portable artifact discipline (self-contained; no design-phase-workspace context dependencies) |
| Predecessor artifact | `P6-CK_Iter4_Revision_Cycle_Close_Handoff.md` §9.2 (Phase 7 entry authorization GRANTED) |
| Successor artifact | (New-workspace operator authority) — new-workspace session 1 entry artifact |
| Companion design-phase artifacts | `P6-CK_Iter4_Revision_Cycle_Close_Handoff.md`; `F2-12_Closure_Declaration.md`; `Governance_Substrate_Propagation_Note_F1-01.md`; full §3 substrate inventory |
| Filing destination | `/mnt/user-data/outputs/Phase_7_Kickoff_Prompt.md` (design-phase workspace; transferable to new workspace) |
| Date | 2026-05-14 |

---

*End of Phase 7 Kickoff Prompt. Portable to new workspace per Workflow v1.7 DP-4 default. Design-phase workspace remains canonical archive + back-flow target. New-workspace operator authority at session 1 entry: execution agent selection + session pattern + target stack + first atomic unit substrate-read.*
