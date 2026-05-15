# Phase 6.5 Pre-Transition Arc — Sequence Manifest

*Canonical sequence-tracking artifact for the Phase 6.5 pre-transition arc. Loaded as substrate by every Phase 6.5 session. Authoritative reference for inter-session dependencies, fork-handling discipline, and arc completion criteria.*

---

## §1 Provenance + status

| Field | Value |
|---|---|
| Artifact | `Phase_6_5_Pre_Transition_Arc_Manifest.md` |
| Type | Pre-transition arc sequence-tracking artifact; manifest substrate |
| Status | **Filed** at design-phase workspace; reference substrate for every Phase 6.5 session |
| Date | 2026-05-14 |
| Predecessor | `P6-CK_Iter4_Revision_Cycle_Close_Handoff.md` (Phase 6 close; cascade-substrate-clearance ISSUED; Phase 7 entry authorization GRANTED) |
| Successor at arc completion | Phase 7 entry at new Claude Code CLI workspace per Workflow DP-4 default |
| Authoring authority | Operator directive at session 2026-05-14 ("Proceed with #1 [full pre-transition rigor]") |
| Workflow authority at arc open | `Project_Workflow_v1_7.md` (provisional; Workflow §6.5 formal specification authored at Phase 6.5 Session 5 = Workflow v1.7 → v1.8 promotion) |

---

## §2 Phase 6.5 framing

### §2.1 Provisional phase designation

Phase 6.5 is a pre-transition arc bridging Phase 6 close → Phase 7 (execution) entry. The arc is provisionally framed as Phase 6.5; formal Workflow §6.5 specification is authored retroactively at this arc's Session 5 (Workflow v1.7 → v1.8 promotion). Sessions 1–4 operate under provisional authority anchored at `P6-CK_Iter4_Revision_Cycle_Close_Handoff.md` §10.1 forward-routing + operator directive 2026-05-14.

### §2.2 Arc purpose

Phase 6 produced cleared implementation plans approved-for-execution at v2.3 / v2.1 / v1 revisions. Phase 7 hosts the build of the **target harness (H_T)** — the multi-LLM agent harness specified by ADRs + ADD + specs + plans — in **Claude Code CLI** as the **execution harness (H_E)**. Phase 6.5 is the disciplined pre-transition work that closes the gap between "cleared plans" and "confident execution start."

Specifically:
- Commits the target stack (language + ecosystem + tooling) that the v2.3 plans materialize against
- Validates plan executability against that committed stack
- Resolves the F3-02 acknowledged-deferred finding (independent route; eliminates execution-time back-flow risk on IS↔OD coordination surface)
- Authors the meta-architecture distinguishing H_T from H_E — the chicken-and-egg paradox resolution
- Promotes Workflow v1.7 → v1.8 with §6.5 + §2.7 phase specifications
- Authors Claude Code CLI bootstrap substrate (root + per-axis `CLAUDE.md`, custom skills, sub-agent boundaries)
- Authors Phase 7 Session 1 Entry Directive (closes the structural gap surfaced by the kickoff-vs-directive distinction)

### §2.3 Chicken-and-egg paradox — load-bearing meta-frame

Two agent harnesses coexist during the build:

- **H_T (target harness)** — what the v2.3 plans specify. Multi-LLM by design, with the design-phase-committed control plane / IS / AS / OD axes. NOT YET BUILT at Phase 7 entry.
- **H_E (execution harness)** — Claude Code CLI + operator + filesystem; itself an agent harness with its own control plane (turn loop + tool use), action surface (bash + file ops + MCP), context engineering (CLAUDE.md hierarchy + sub-agents), operational discipline (Claude Code's own logging). EXISTS NOW; hosts the build.

The paradox: H_E has design choices that are NOT H_T's design choices. Without discipline, H_E patterns can leak into H_T implementation, producing "H_T-shaped-like-Claude-Code" rather than H_T-as-specified.

**Two non-negotiable disciplines:**

1. **H_T's design is authoritative.** H_T's commitments (ADRs + ADD + specs + plans) are canonical. H_E patterns must NOT leak into H_T implementation. Each atomic unit implements H_T's contract, not H_E's natural patterns.
2. **H_E provides bounded substitutions for not-yet-built H_T primitives.** During the build, H_T primitives that don't exist yet are substituted by H_E-side artifacts (e.g., a JSON progress ledger substitutes for the IS axis state ledger; pytest substitutes for the OD axis validation contract; Claude Code's turn loop substitutes for the CP axis orchestration). Substitutions are bounded, documented, and explicitly mapped from build-time → target-time.

The **meta-architecture artifact authored at Session 4 (η)** canonicalizes the H_T ↔ H_E substitution mapping + substitution-risk discipline + self-hosting milestone gradient (when H_T primitives go live, the H_E substitutions retire).

---

## §3 7-session enumeration

### §3.1 Sequence overview

| # | Designator | Session name | Skill / mode | Primary deliverable |
|---|---|---|---|---|
| 1 | δ | Target stack commitment | Focused deliberation (no formal skill); ad-hoc C-voice consultation | `Target_Stack_Commitment_v1.md` (ADD addendum or standalone decision artifact) |
| 2 | α | Pre-flight executability audit | implementation-planner SKILL (audit sub-mode if extensible; otherwise ad-hoc) | `Plan_Executability_Audit_v1.md` per-axis or aggregate |
| 3 | ζ | F3-02 IS-axis revision pass | implementation-planner SKILL §8 revision-pass sub-mode | `Implementation_Plan_Information_Substrate_v2_2.md` + revision-cycle close handoff |
| 4 | η + θ | Chicken-and-egg meta-architecture + Phase 7 internal workflow | Council-orchestrator (selective: C1 + C7 + C11) + spec-writer for canonicalization | `Phase_7_Meta_Architecture_v1.md` (H_T↔H_E substitution mapping + substitution-risk discipline + self-hosting milestones + Phase 7 sub-phase structure) |
| 5 | γ | Workflow v1.7 → v1.8 promotion | Operator-authored; assistant-drafted | `Project_Workflow_v1_8.md` + `Path_Delta_Workflow_v1_7_to_v1_8_Revision_Log_Entry.md` update absorbing §2.7 + §6.5 amendments |
| 6 | ε | Claude Code CLI bootstrap substrate | Multi-skill (skill-creator for custom skills; spec-writer for CLAUDE.md authoring) | Root `CLAUDE.md` + per-axis `CLAUDE.md`s + custom Claude Code skills (e.g., `atomic-unit-executor`, `substrate-chain-reader`, `unit-completion-recorder`, `verification-sub-agent`) + slash command sketches + sub-agent boundary declarations |
| 7 | β | Phase 7 Session 1 Entry Directive | spec-writer (directive-shaped artifact) | `Phase_7_Session_1_Entry_Directive.md` + final operator handoff package |

### §3.2 Per-session scope detail

#### Session 1 — δ — Target stack commitment

**Scope.** Commit the target stack the v2.3 plans materialize against. Specifically:
- Programming language
- Package manager
- Type checker
- Linter / formatter
- Test runner
- Repo structure convention
- Git posture (branching strategy; commit-per-unit vs PR-per-unit; conventional commits or other)
- CI substrate (or explicit non-commit if CI deferred to post-bootstrap)
- Core dependency stance (minimal-framework principle: avoid LangGraph / Temporal / similar as foundational substrate — H_T's design must emerge, not be pre-empted)
- Multi-LLM provider SDK stance (per ADR-F1 v1.2)
- OTel SDK selection (per ADR-D6 v1.2 + OD axis observability commitments)
- Local-development ergonomics (sqlite, OS keychain integration per ADR-F5 v1.1)

**Out of scope.** H_T design revisions; persona revisions; ADR revisions. Any of these arising during stack deliberation routes per §6 fork-handling discipline.

**Deliverable.** `Target_Stack_Commitment_v1.md` — operator decision artifact recording the stack + rationale + alternatives considered + tradeoff acknowledgments. Filed as ADD v1.3 addendum OR standalone artifact per operator preference.

**Session structure.** Recommended 4-segment delivery:
- Segment 1 — Constraints enumeration from ADR substrate + persona + project commitments
- Segment 2 — Stack candidate matrix (3–4 candidates × 8–10 evaluation axes)
- Segment 3 — Tradeoff deliberation; ad-hoc C-voice perspectives where warranted (e.g., "C7, what does the observability substrate care about per language?")
- Segment 4 — Operator decision + artifact filing + Session 2 kickoff authoring

#### Session 2 — α — Pre-flight executability audit

**Scope.** Read each axis plan end-to-end + validate against the Session-1-committed stack. Validate that:
- Signatures translate cleanly to target language (no impossible-in-stack constructs)
- Acceptance criteria are testable in the committed test runner
- Test specifications are concrete (named tests + verifiable invariants)
- Substrate-chain navigation works in practice (plan unit → spec contract → ADR commitment → ADD / PRD / persona)
- Cross-axis composition seams are executable (CXA v2.1 §[topological sort] + §[coverage matrix] verify against stack)
- No design-execution gap surfaces that wasn't caught at P6-CK Iter 4

**Deliverable.** `Plan_Executability_Audit_v1.md` (per-axis sections OR aggregate) — finding inventory + finding-class disposition + remediation routing.

**Fork handling at α.** If executability audit surfaces:
- Class 1 (severe; spec contract un-implementable in committed stack) → halt; route to Session 1 stack re-deliberation OR Phase 5 spec revision (operator decides at fork point)
- Class 2 (moderate; signature mis-decomposition surfaceable as plan-unit defect) → route to Phase 6 revision-pass (implementation-planner SKILL §8); may close in-Phase-6.5-arc or defer to dedicated revision session
- Class 3 (informational; documentation clarity) → log in audit artifact; no routing

**Session structure.** Likely 2-segment per axis × 4 axes + 1 segment for cross-axis seams + 1 segment for finding inventory close = ~10 segments. May span multiple sessions if dense.

#### Session 3 — ζ — F3-02 IS-axis revision pass

**Scope.** Resolve the F3-02 acknowledged-deferred finding from Iter 4: author IS plan v2.2 with the canonical IS-axis ledger-write site unit; resolve OD plan U-OD-20 acceptance #11 cross-axis dependency placeholder `U-IS-NN` to a real unit identifier.

**Why now (not deferred).** Per Operator full pre-transition rigor directive: eliminates execution-time back-flow risk on the IS↔OD coordination surface; closes the one outstanding acknowledged-deferred Iter 4 finding; brings the IS plan to v2.2 alignment with OD plan v2.3.

**Deliverable.** `Implementation_Plan_Information_Substrate_v2_2.md` + `Phase_6_5_Session_3_F3-02_Resolution_Close_Handoff.md`.

**Skill.** implementation-planner SKILL.md §8 revision-pass sub-mode (Phase 6 still-canonical for plan authorship; this is a thin Phase-6-style revision-pass within Phase 6.5 arc).

**Session structure.** 2–3 segments: (1) F3-02 substrate read + canonical IS-axis ledger-write site decomposition; (2) U-IS-NN unit authoring + cross-unit agreement invariant with OD plan U-OD-20 acceptance #11; (3) coherence pass + close handoff.

#### Session 4 — η + θ — Meta-architecture + Phase 7 internal workflow

**Scope (η — meta-architecture).** Author the canonical H_T ↔ H_E substitution mapping and substitution-risk discipline. Specifically:
- H_T components catalog (control plane / IS / AS / OD axes; per-axis canonical primitives)
- H_E capabilities catalog (Claude Code's tool surface; turn loop; sub-agent boundaries; CLAUDE.md hierarchy; filesystem access; bash + git access)
- Capability overlap map (where H_E natively provides an H_T-shaped primitive; where it doesn't)
- Substitution mapping table (per not-yet-built-H_T-primitive: H_E substitution + bounded scope + retirement criterion at self-hosting milestone)
- Substitution-risk discipline (rules preventing H_E patterns from leaking into H_T design — e.g., "Claude Code's sub-agent topology is NOT H_T's CP-axis topology; do not copy")
- Self-hosting milestone gradient (when each H_T primitive goes live + retires the H_E substitution)

**Scope (θ — Phase 7 internal workflow).** Author Phase 7's sub-phase structure:
- 7a — Bootstrap (foundational Level 0 units across all axes; minimum viable IS + OD + CP primitives operational)
- 7b — Per-axis interior execution (axis-level cluster completion)
- 7c — Cross-axis integration (CXA v2.1 composition seams)
- 7d — Self-hosting milestones (per η substitution-retirement schedule)
- Per-sub-phase entry-gate + exit criteria
- Per-sub-phase back-flow routing
- Per-sub-phase reduced-HITL viability assessment (which sub-phases are overnight-executable; which require operator presence)

**Deliverable.** `Phase_7_Meta_Architecture_v1.md` — combined η + θ artifact OR separate `Phase_7_Meta_Architecture_v1.md` + `Phase_7_Internal_Workflow_v1.md` per session-1-style operator decision.

**Skill.** Council-orchestrator selective convening (C1 for CP-axis meta-design; C7 for observability meta-design; C11 for operator-loop meta-design); spec-writer for canonicalization. Full-council convening NOT required (η is not a primary architectural decision; it's a build-time discipline overlay).

**Session structure.** Multi-segment likely 5–6 segments: (1) H_T components + H_E capabilities cataloging; (2) capability overlap mapping; (3) substitution mapping table authoring; (4) substitution-risk discipline; (5) Phase 7 sub-phase structure (θ); (6) close handoff.

**Fork handling at η.** This is the only Phase 6.5 session doing genuine *new* architectural work (not absorbing existing substrate). If η surfaces a question about H_T design that wasn't resolved at Phase 6, route per §6 fork-handling — DO NOT silently extend H_T design at η. The discipline is: η authors the substitution discipline; it does NOT extend H_T's commitments.

#### Session 5 — γ — Workflow v1.7 → v1.8 promotion

**Scope.** Promote Workflow v1.7 → v1.8 absorbing:
- Path δ revision-log entry already filed at `Path_Delta_Workflow_v1_7_to_v1_8_Revision_Log_Entry.md`: §4.1.4.6 amendment authorizing P6-CK Iter 4 cascade-substrate-verification (already-applied amendment; now formalized)
- New §6.5 Phase 6.5 specification (authored from this manifest + sessions 1–4 outputs)
- New §2.7 Phase 7 specification (authored from session 4 θ output)
- Any §7 fidelity-grammar updates surfaced during Phase 6.5 sessions (advisory observations from Iter 4 review have been logged)

**Deliverable.** `Project_Workflow_v1_8.md` + revision-log entry update.

**Session structure.** Largely mechanical given upstream inputs (this manifest + session 4 outputs). 2–3 segments: (1) §2.7 + §6.5 specifications authoring; (2) v1.7 → v1.8 promotion + revision-log update; (3) close handoff.

#### Session 6 — ε — Claude Code CLI bootstrap substrate

**Scope.** Author the concrete Claude Code CLI substrate the new workspace receives at Phase 7 entry. Specifically:

- **Root `CLAUDE.md`** — project framing pointer (substrate inventory; execution discipline; back-flow rules; meta-architecture reference)
- **Per-axis `CLAUDE.md`** — axis context (axis spec + plan substrate; cluster entry points; substrate-chain shortcuts)
- **Custom Claude Code skills:**
  - `atomic-unit-executor` — reads unit signatures + acceptance + tests verbatim; implements only those (substitution-risk discipline enforcement)
  - `substrate-chain-reader` — navigates plan unit → spec contract → ADR → ADD / PRD / persona efficiently
  - `unit-completion-recorder` — updates progress ledger (JSON / JSONL hybrid per η Pattern D recommendation)
  - `verification-sub-agent` — fresh-context review of completed units against acceptance criteria
- **Slash command sketches** for the build's common operations (e.g., `/next-unit`, `/verify-unit`, `/report-block`)
- **Sub-agent boundary declarations** per η substitution-mapping (e.g., per-axis sub-agents only if context budget pressure surfaces; verification sub-agent for completed-unit review)

**Deliverable.** `Phase_7_Bootstrap_Substrate_v1/` directory containing all above artifacts.

**Skill.** Multi-skill: skill-creator SKILL for custom Claude Code skills; spec-writer for CLAUDE.md authoring.

**Session structure.** Multi-segment 4–5 segments: (1) root CLAUDE.md; (2) per-axis CLAUDE.md (batch); (3) custom skill authoring; (4) slash commands + sub-agent boundaries; (5) close handoff.

#### Session 7 — β — Phase 7 Session 1 Entry Directive

**Scope.** Author the directive-shaped session prompt for Phase 7's first execution session at the new Claude Code CLI workspace. Closes the structural gap surfaced earlier (kickoff-as-framing vs directive-as-action).

**Deliverable.** `Phase_7_Session_1_Entry_Directive.md` — directive-shaped artifact:
- §1 Session identity (Phase 7 Session 1; new workspace entry; sub-phase 7a bootstrap entry)
- §2 OD menu (first sub-phase 7a unit set selection; first atomic unit substrate-read order; execution agent confirmation [Claude Code]; session pattern selection from η)
- §3 Substrate retrieval (v1.8 workflow + v2.2 IS plan + bootstrap substrate from session 6 + meta-architecture from session 4)
- §4 Entry-gate verification
- §5 Session 1 execution discipline (reduced-HITL viability per η; verification sub-agent enforcement)
- §6 Exit criteria

Plus a **final operator handoff package** consolidating: this manifest + all 7 session close handoffs + Phase 7 kickoff (already authored) + Phase 7 Session 1 Entry Directive + complete substrate inventory.

**Skill.** spec-writer for directive artifact.

**Session structure.** Short session likely 2 segments: (1) directive authoring + handoff package consolidation; (2) close handoff + arc-completion declaration.

### §3.3 Inter-session dependency graph

```
Session 1 (δ — target stack)
  │
  ├──> Session 2 (α — executability audit; requires committed stack)
  │     │
  │     └──> Session 3 (ζ — F3-02 resolution; informed by audit but executable in parallel)
  │           │
  │           ▼
  │     Session 4 (η + θ — meta-architecture; requires audit findings + F3-02 closure)
  │           │
  │           ▼
  │     Session 5 (γ — Workflow v1.8 promotion; requires η + θ outputs)
  │           │
  │           ▼
  │     Session 6 (ε — Claude Code bootstrap; requires meta-architecture + workflow + executability)
  │           │
  │           ▼
  │     Session 7 (β — Phase 7 Session 1 Entry Directive; consolidates all upstream)
  │
  ▼ Arc completion → Phase 7 entry at new workspace
```

**Parallelization opportunities** (if operator pacing favors compressed wall-clock):
- Sessions 2 (α) and 3 (ζ) can run in either order or interleaved (audit doesn't block F3-02; F3-02 doesn't block audit). RECOMMENDED order: α first (because audit may surface findings that affect F3-02 scope).
- Sessions 5 (γ) and 6 (ε) can partially overlap (γ is mechanical absorption; ε authors substrate). Sequential is cleaner.
- No other parallelization advised; downstream sessions strictly depend on upstream outputs.

### §3.4 Per-session output → next-session input

| Session | Output | Consumed at |
|---|---|---|
| 1 (δ) | `Target_Stack_Commitment_v1.md` | Sessions 2 + 6 + 7 |
| 2 (α) | `Plan_Executability_Audit_v1.md` | Session 3 (if findings affect IS axis) + Session 4 (η informed by execution-time gaps) + Session 6 (bootstrap substrate aware of audit findings) |
| 3 (ζ) | IS plan v2.2 + close handoff | Session 4 (η; closes F3-02 acknowledged-deferred status) + Session 6 (bootstrap substrate references v2.2) + Session 7 (substrate inventory at directive) |
| 4 (η + θ) | `Phase_7_Meta_Architecture_v1.md` | Session 5 (γ; θ output becomes §2.7 specification source) + Session 6 (η output drives bootstrap substrate design) + Session 7 (substrate at directive) |
| 5 (γ) | `Project_Workflow_v1_8.md` | Session 6 + Session 7 (canonical workflow authority for Phase 7) |
| 6 (ε) | Bootstrap substrate directory | Session 7 (substrate at directive) |
| 7 (β) | Phase 7 Session 1 Entry Directive + handoff package | Phase 7 new-workspace session 1 entry |

---

## §4 Fork-handling discipline

### §4.1 Fork class taxonomy

Per `Project_Workflow_v1_7.md` §4.1 finding-class disposition routing — adapted for Phase 6.5 arc:

| Class | Definition | Phase 6.5 routing |
|---|---|---|
| Class 1 | Severe — invalidates a Phase 6 close commitment OR cascade-substrate-clearance OR Phase 7 entry authorization | Halt arc; surface to operator; route per §4.2 below |
| Class 2 | Moderate — surfaces a design-phase artifact defect (ADR / spec / plan / ADD / PRD / persona) | Route back to design-phase channel; arc continues if defect is non-blocking for current session |
| Class 3 | Informational — documentation refinement; no design-phase artifact defect | Log in session close handoff; no routing |

### §4.2 Class 1 fork routing

Class 1 forks during Phase 6.5 sessions invoke the following options (operator decision required):

| Option | Shape | When appropriate |
|---|---|---|
| (A) Halt arc; re-open Phase 6 revision-pass | Phase 6.5 sessions pause; Phase 6 revision-pass executes; Phase 6.5 sessions resume after Phase 6 re-clearance | Severe finding implies plan v2.3 / IS plan v2.1 is not approved-for-execution |
| (B) Halt arc; re-open Phase 5 spec revision | Phase 6.5 sessions pause; Phase 5 spec revision cascade; downstream Phase 6 revision-pass; Phase 6.5 sessions resume | Severe finding implies spec contract is broken (per implementation-planner SKILL §2 consequence 1) |
| (C) Halt arc; re-open Phase 3a/3b ADR revision + cascade | Phase 6.5 sessions pause; ADR revision; downstream Phase 4 PRD + Phase 5 spec + Phase 6 plan cascade; Phase 6.5 sessions resume | Severe finding implies architectural commitment is broken |
| (D) Re-scope Phase 6.5 arc | Operator amends manifest §3 enumeration; arc continues at re-scoped sequence | Finding implies the Phase 6.5 arc itself is mis-scoped (e.g., a missing session needs insertion) |

**Discipline:** Class 1 forks are NEVER silently absorbed. Surface immediately; halt session; operator decides routing.

### §4.3 Class 2 fork routing

Class 2 forks during Phase 6.5 sessions route to design-phase channels:

| Target artifact | Design-phase channel | Skill |
|---|---|---|
| Plan unit defect | Phase 6 revision-pass | implementation-planner SKILL §8 |
| Spec contract defect | Phase 5 revision-pass | spec-writer SKILL |
| ADR defect | Phase 3a or 3b revision-pass | council-orchestrator + relevant C-voice |
| PRD defect | Phase 4 revision-pass | prd-author SKILL |
| Persona defect | Phase 2 revision-pass | systems-architect SKILL |
| Workflow defect | Workflow §7 amendment | Operator authority + revision-log entry |

**Discipline:** Class 2 forks documented at session close handoff; routing decision at operator discretion. Arc continues if defect is non-blocking for current session; pauses if defect blocks.

### §4.4 Class 3 fork routing

Class 3 forks logged at session close handoff; no routing.

### §4.5 In-project fork management

Per operator directive 2026-05-14: "if any forks present themselves these must be managed in the context of this project."

**Operationalization:**
- All Phase 6.5 sessions run in the current design-phase project workspace (NOT the future Claude Code CLI workspace)
- All fork-routing channels (Phase 6 / 5 / 3a/3b / 4 / 2 / Workflow) are in-project channels
- New-workspace transfer occurs ONLY at arc completion (Session 7 close)
- Forks discovered AFTER arc completion (at Phase 7 execution) route back to this project workspace per Phase 7 Kickoff Prompt §6 back-flow discipline

---

## §5 Arc completion criteria

The Phase 6.5 arc closes when all of the following hold:

| # | Criterion | Verification |
|---|---|---|
| 1 | All 7 sessions executed; per-session deliverables filed | This manifest §3.2 deliverables list |
| 2 | All session close handoffs filed | Per-session close handoff inventory |
| 3 | No open Class 1 forks | Fork inventory at Session 7 close |
| 4 | All Class 2 forks dispositioned (resolved OR routed with operator decision recorded) | Fork inventory at Session 7 close |
| 5 | Workflow v1.8 filed (Session 5 output) | `Project_Workflow_v1_8.md` at `/mnt/project/` |
| 6 | Meta-architecture artifact filed (Session 4 output) | `Phase_7_Meta_Architecture_v1.md` at `/mnt/project/` |
| 7 | Bootstrap substrate directory filed (Session 6 output) | `Phase_7_Bootstrap_Substrate_v1/` at `/mnt/project/` |
| 8 | Phase 7 Session 1 Entry Directive filed (Session 7 output) | `Phase_7_Session_1_Entry_Directive.md` at `/mnt/project/` |
| 9 | Final operator handoff package consolidated | Session 7 close handoff |

Arc completion enables Phase 7 entry at new Claude Code CLI workspace per Workflow DP-4 default.

---

## §6 Each-session opening read (canonical pattern)

Every Phase 6.5 session opens by loading:

1. **This manifest** (`Phase_6_5_Pre_Transition_Arc_Manifest.md`) — sequence context + fork-handling discipline + arc completion criteria
2. **`Canonical_Substrate_Inventory.md`** — KB navigation anchor; disambiguates retrieval-time canonical-vs-superseded artifact ambiguity; updated at every session close
3. **The session's kickoff prompt** (`Phase_6_5_Session_N_Kickoff.md`) — session-specific scope + segmented delivery contract + entry-gate verification
4. **Predecessor session's close handoff** (if N ≥ 2) — inheritance of outputs + open forks
5. **`P6-CK_Iter4_Revision_Cycle_Close_Handoff.md`** — Phase 6 close record + Phase 7 entry authorization
6. **`Phase_7_Kickoff_Prompt.md`** — portable kickoff (substrate inventory + execution discipline + back-flow routing reference)
7. **Session-specific substrate** per kickoff §3 substrate retrieval

---

## §7 Each-session close handoff (canonical pattern)

Every Phase 6.5 session closes by producing:

| Artifact | Contents |
|---|---|
| `Phase_6_5_Session_N_Close_Handoff.md` | Session deliverable inventory + open forks + class-1/2/3 disposition + arc completion criteria status + Session N+1 entry-gate prerequisites |
| `Phase_6_5_Session_N+1_Kickoff.md` | Next session's kickoff prompt (per project precedent: each session authors next session's prompt at close) |

---

## §8 Workflow authority anchors

| Anchor | Document | Section |
|---|---|---|
| Provisional Phase 6.5 authorization | Operator directive 2026-05-14 + `P6-CK_Iter4_Revision_Cycle_Close_Handoff.md` §10.1 | n/a |
| Formal Phase 6.5 authorization | `Project_Workflow_v1_8.md` §6.5 (authored at Session 5) | §6.5 (pending) |
| Fork-handling | `Project_Workflow_v1_7.md` §4.1 + this manifest §4 | §4.1 |
| Plan revision-pass discipline (if Class 2 fork triggers Phase 6 revision) | `implementation-planner` SKILL.md §8 | §8 |
| Spec revision-pass discipline (if Class 2 fork triggers Phase 5 revision) | `spec-writer` SKILL.md | (full skill) |
| ADR revision discipline (if Class 2 fork triggers Phase 3a/3b revision) | `council-orchestrator` SKILL.md + relevant C-voice SKILLs | (full skill) |
| In-project fork management | Operator directive 2026-05-14 + this manifest §4.5 | §4.5 |

---

## §9 Filing footer

| Field | Value |
|---|---|
| Artifact | `Phase_6_5_Pre_Transition_Arc_Manifest.md` |
| Status | Filed at design-phase workspace |
| Phase | Phase 6.5 (provisional; formalized at Session 5) |
| Authoring discipline | `Project_Workflow_v1_7.md` §7 fidelity-grammar; manifest substrate authoring pattern |
| Predecessor | `P6-CK_Iter4_Revision_Cycle_Close_Handoff.md` (Phase 6 close) |
| Successor at arc completion | Phase 7 entry at new Claude Code CLI workspace |
| Filing destination | `/mnt/user-data/outputs/Phase_6_5_Pre_Transition_Arc_Manifest.md` |
| Date | 2026-05-14 |

---

*End of Phase 6.5 Pre-Transition Arc Manifest. Reference substrate for every Phase 6.5 session. Authoritative for inter-session dependencies, fork-handling discipline, and arc completion criteria.*
