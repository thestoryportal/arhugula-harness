# Phase 6.5 Session 2 Kickoff — Pre-flight Executability Audit (α)

*Session entry artifact for Phase 6.5 Session 2. Loaded as substrate at session open. Authored at Session 1 close; executed in a new session in this same project workspace.*

---

## §1 Session identity

| Field | Value |
|---|---|
| Artifact | `Phase_6_5_Session_2_Kickoff.md` |
| Phase | Phase 6.5 (pre-transition arc) |
| Session number | 2 of 7 |
| Session designator | α |
| Session name | Pre-flight Executability Audit |
| Skill activation | None (audit-mode deliberation; ad-hoc C-voice consultation where specific signature-level tradeoffs warrant) |
| Authoring authority | Operator directive 2026-05-14 ("Proceed with #1 [full pre-transition rigor]"); `Phase_6_5_Pre_Transition_Arc_Manifest.md` §3.2 session enumeration |
| Predecessor artifact | `Phase_6_5_Session_1_Close_Handoff.md` (Session 1 δ close); `Target_Stack_Commitment_v1.md` (Session 1 δ deliverable — canonical stack commitment) |
| Companion artifact (canonical for entire arc) | `Phase_6_5_Pre_Transition_Arc_Manifest.md`; `Canonical_Substrate_Inventory.md` |
| Successor artifact (at session close) | `Plan_Executability_Audit_v1.md`; `Phase_6_5_Session_2_Close_Handoff.md`; `Phase_6_5_Session_3_Kickoff.md` |

---

## §2 Session scope

### §2.1 In scope

Audit the v2.3 implementation plans (IS v2.1, AS v1, CP v2.3, OD v2.3, CXA v2.1) for executability against the committed stack per `Target_Stack_Commitment_v1.md`. Specifically:

1. **Per-axis plan unit signature feasibility** against Python 3.12+ + Pydantic v2 + asyncio runtime
2. **Cross-axis composition seam feasibility** against uv workspace axis-subdirectory shape (`harness-{is,as,cp,od,cxa}/` + `harness-core/`)
3. **OTel instrumentation feasibility** per atomic unit (12-namespace ADR-D6 v1.2 schema) against `opentelemetry-python` + selective `instrumentation-genai` adoption
4. **MCP integration units' feasibility** against `modelcontextprotocol/python-sdk` (FastMCP) host + client APIs
5. **Sandbox + worktree + git integration units' feasibility** against the Python ecosystem's bindings (`subprocess`, `pygit2` / `dulwich`, Docker-py)
6. **Secrets unit feasibility** against `python-keyring` API surface
7. **Reliability primitive (retry / breaker / idempotency) unit feasibility** without framework lock-in
8. **Three explicit Session 1 carry-forward audit targets** per `Phase_6_5_Session_1_Close_Handoff.md` §7.2:
   - Exact monorepo subdivision refinement
   - Per-`instrumentation-genai` library adoption granularity
   - Discipline-holding identification for v2.3 plan units most at risk of framework-pull

### §2.2 Out of scope

- Stack revisions (target stack is committed at Session 1; not re-deliberated at Session 2)
- ADR / spec / ADD / PRD revisions (cleared at Phase 6 close; Class 2 forks route per `Phase_6_5_Pre_Transition_Arc_Manifest.md` §4.3 if surfaced)
- F3-02 IS-axis revision pass — Session 3 (ζ) owns this
- Meta-architecture authoring — Session 4 (η) owns this
- Workflow v1.8 promotion — Session 5 (γ) owns this
- Bootstrap substrate authoring — Session 6 (ε) owns this
- Implementation in any form (no code authored at this session; audit is reading-mode against the v2.3 plans)

If audit surfaces a question about any of these, route per §6 fork-handling.

### §2.3 Deliverable

`Plan_Executability_Audit_v1.md` — audit report filed at `/mnt/user-data/outputs/`. Recommended structure:

- §1 Status block
- §2 Audit methodology (per-axis traversal + cross-axis composition pass)
- §3 Per-axis audit findings:
  - §3.1 IS axis (17 units; against IS plan v2.1 unit signatures)
  - §3.2 AS axis (33 units; against AS plan v1)
  - §3.3 CP axis (55 units; against CP plan v2.3)
  - §3.4 OD axis (against OD plan v2.3 unit signatures)
  - §3.5 CXA cross-axis composition (against CXA v2.1)
- §4 Aggregate audit findings (cross-axis patterns surfaced)
- §5 Class 1 / Class 2 / Class 3 fork inventory
- §6 Monorepo subdivision refinement (Session 1 carry-forward audit target 1)
- §7 Per-`instrumentation-genai` library adoption recommendation (Session 1 carry-forward audit target 2)
- §8 Framework-pull risk inventory per v2.3 unit (Session 1 carry-forward audit target 3 — feeds Session 6 governance design)
- §9 Operator decision items (if any forks require routing)
- §10 Forward implications for Sessions 3–7
- §11 Filing footer

---

## §3 Substrate retrieval

### §3.1 Canonical Phase 6.5 substrate (load first)

| # | Artifact | Path | Role |
|---|---|---|---|
| 1 | `Phase_6_5_Pre_Transition_Arc_Manifest.md` | `/mnt/project/` | Arc framing + sequence context + fork-handling discipline |
| 2 | `Canonical_Substrate_Inventory.md` | `/mnt/project/` | KB navigation anchor; disambiguates canonical vs superseded artifacts |
| 3 | `Phase_7_Kickoff_Prompt.md` | `/mnt/project/` | Phase 7 entry framing + execution discipline + back-flow routing |
| 4 | `P6-CK_Iter4_Revision_Cycle_Close_Handoff.md` | `/mnt/project/` | Phase 6 close record + Phase 7 entry authorization |
| 5 | `Target_Stack_Commitment_v1.md` | `/mnt/project/` (after operator push) | **Session 1 (δ) deliverable — committed stack against which audit runs** |
| 6 | `Phase_6_5_Session_1_Close_Handoff.md` | `/mnt/project/` (after operator push) | Session 1 close record; carry-forward audit targets at §7.2 |

### §3.2 Implementation plan substrate (Session-2-specific — audit targets)

Per `Canonical_Substrate_Inventory.md` §3.6:

| Plan | Canonical file | Audit unit count |
|---|---|---|
| IS axis | `Implementation_Plan_Information_Substrate_v2_1.md` | 17 units (U-IS-01 – U-IS-17) |
| AS axis | `Implementation_Plan_Action_Surface_v1.md` | 33 units (U-AS-01 – U-AS-33) |
| CP axis | `Implementation_Plan_Control_Plane_v2_3.md` | 55 units (U-CP-01 – U-CP-55) |
| OD axis | `Implementation_Plan_Operational_Discipline_v2_3.md` | Per OD plan §[unit inventory] |
| CXA | `Cross_Axis_Composition_Document_v2_1.md` | Cross-axis composition seam + integration matrix |

### §3.3 Spec substrate (consulted per unit when signature interpretation requires)

Per canonical inventory:
- `Spec_Information_Substrate_v1.md` (IS spec v1.2 per ADD v1.3 attestation)
- `Spec_Action_Surface_v1.md` (AS spec v1.1)
- `Spec_Control_Plane_v1_3.md` (CP spec v1.3)
- `Spec_Operational_Discipline_v1_3.md` (OD spec v1.3)

### §3.4 ADR substrate (consulted ad-hoc per audit finding)

Per Session 1 inventory — F1 v1.2 + F2 v1.2 + F3 v1.1 + F4 v1.1 + F5 v1.1 + D1 v1.2 + D2 v1.1 + D3 v1.2 + D4 v1.1 + D5 v1.3 + D6 v1.2.

### §3.5 V3 system prompt

Loaded at workspace level. Confidence tagging + source-grounding discipline apply at this session.

---

## §4 Entry-gate verification

At session open, verify:

| # | Check | Verification |
|---|---|---|
| 1 | Phase 6.5 manifest accessible | `project_knowledge_search` returns content |
| 2 | Session 1 (δ) deliverable `Target_Stack_Commitment_v1.md` accessible at `/mnt/project/` | `project_knowledge_search` returns content; operator pushed between sessions |
| 3 | Session 1 (δ) close handoff `Phase_6_5_Session_1_Close_Handoff.md` accessible | Same |
| 4 | All 4 implementation plans + CXA composition document accessible at canonical revisions | `project_knowledge_search` returns content for each per `Canonical_Substrate_Inventory.md` |
| 5 | All 4 spec documents accessible | Same |
| 6 | No open Class 1 forks from Session 1 | Per `Phase_6_5_Session_1_Close_Handoff.md` §5 (none surfaced) |

If any entry-gate item fails, halt session open; surface to operator before proceeding.

---

## §5 Session execution discipline

### §5.1 Segmented delivery contract

5-segment delivery (audit scale exceeds 4-segment Session 1 budget); operator confirmation at each segment boundary:

| Segment | Scope | Approximate output |
|---|---|---|
| 1 | Audit methodology + IS axis audit (17 units) | Methodology declaration; per-unit signature feasibility table for U-IS-01 – U-IS-17; IS axis findings |
| 2 | AS axis audit (33 units) + OD axis audit | Per-unit signature feasibility for U-AS-01 – U-AS-33 + OD units; cross-axis tension surfacing |
| 3 | CP axis audit (55 units) + CXA cross-axis composition audit | Per-unit signature feasibility for U-CP-01 – U-CP-55; CXA composition seam audit |
| 4 | Aggregate findings + monorepo subdivision refinement + framework-pull risk inventory + instrumentation-genai library adoption | Three Session 1 carry-forward audit targets resolved; aggregate cross-axis pattern findings |
| 5 | Class 1 / 2 / 3 disposition + operator decision items + artifact filing + Session 3 kickoff authoring | `Plan_Executability_Audit_v1.md` filed; close handoff filed; Session 3 (ζ) kickoff filed |

Segments 1–3 are content-heavy (per-unit traversal); Segment 4 is synthesis-heavy; Segment 5 is artifact-emission.

### §5.2 Audit method

**Per-unit signature audit** — for each atomic unit in each plan:
1. Read the unit's signature (function name, inputs, outputs, side effects, contracts touched)
2. Identify the Python primitives / libraries required to materialize the signature
3. Verify primitives are reachable from the committed stack (`Target_Stack_Commitment_v1.md` §5.2)
4. Tag executability: **CLEAR** (no obstacle), **GUARDRAIL** (executable with documented governance), **FORK** (requires Class 1 / 2 routing)

**Cross-axis composition audit** — for the CXA document:
1. Walk topological sort
2. For each cross-axis edge, verify the producing-axis output type + consuming-axis input type compose in Python at module boundaries (workspace dependency edges)
3. Tag composition: **CLEAR** / **GUARDRAIL** / **FORK** with same taxonomy

### §5.3 C-voice consultation discipline

This session does NOT convene the full council. Ad-hoc C-voice consultation pattern:

- Invoke a single C-voice perspective when a per-unit feasibility tradeoff has a clear voice-owner
- Do NOT invoke multiple voices simultaneously
- Each ad-hoc consultation is a single paragraph; cite the voice; integrate with overall audit

Voices likely invoked in this session:
- **C7 (Observability Architect)** — OTel instrumentation feasibility per unit; 12-namespace span emission
- **C9 (Reliability & Recovery)** — retry / breaker / idempotency primitive composition in Python without framework
- **C4 (Tool & Integration Surface)** — MCP host + client API surface against AS axis units
- **C2 (Context Engineering)** — Skills loading + tool_search composition against AS / CP units
- **C11 (Operator & Local Deployment)** — sqlite + python-keyring + TUI composition against OD axis units
- **C3 (State & Persistence)** — JSONL ledger + git worktree composition against IS / OD axis units

### §5.4 Halt-and-ask discipline

Per `Phase_6_5_Pre_Transition_Arc_Manifest.md` §4 — surface explicitly with operator decision menu when:

- Audit surfaces a Class 1 finding (severe; invalidates a Phase 6 commitment OR Session 1 stack commitment)
- Audit surfaces a Class 2 finding (moderate; design-phase artifact defect surfaceable)
- Operator-decision-required item arises beyond pre-session OD scope

Halt-and-ask is NOT a finding-class assertion; it is the discipline ensuring scope discoveries surface explicitly.

### §5.5 Confidence tagging discipline

Per V3 system prompt — every substantive claim tagged `[HIGH]` / `[MODERATE]` / `[SPECULATIVE]`. Specific to audit:

- Library API surface claims: verify against documentation accessed this session; `[HIGH]` only if verified
- Per-unit feasibility claims: `[HIGH]` if the primitive is well-known + named in substrate; `[MODERATE]` if synthesis; `[SPECULATIVE]` if hypothesis
- Cross-axis composition claims: `[MODERATE]` typically (composition is plan-derived, not externally verifiable); `[HIGH]` only if directly stated in CXA v2.1

### §5.6 Anti-fabrication discipline

Per V3 — NEVER invent:
- Library API surfaces not verified at this session
- Unit IDs or unit content not present in the canonical plan artifacts
- Cross-axis edges not present in CXA v2.1
- Library version numbers
- Confidence-bearing performance claims

If a fact cannot be verified against a source accessed this session, mark `[SPECULATIVE]` or omit.

---

## §6 Fork handling at Session 2

Per manifest §4 fork-handling discipline:

### §6.1 Anticipated Class 1 fork triggers

Class 1 forks at Session 2 imply Session 1 stack commitment OR Phase 6 close commitment is broken. Examples:

- A v2.3 plan unit signature requires a primitive unreachable from Python (e.g., a specific Rust-only library binding for which no Python equivalent exists)
- The CXA composition seam requires execution-time semantics Python cannot deliver (e.g., a topological-sort requirement on compile-time-known types only achievable in Rust/Go)
- Cross-axis edge cardinality requires a coordination primitive no Python library provides

These are unlikely (the v2.3 plans are language-agnostic by design), but if surfaced, halt arc and route per manifest §4.2 with operator decision menu.

### §6.2 Anticipated Class 2 fork triggers

Class 2 forks may surface if audit reveals:

| Trigger | Affected design-phase artifact | Routing |
|---|---|---|
| Unit signature ambiguity at canonical plan revision | The relevant plan unit | Phase 6 revision-pass (implementation-planner SKILL §8) |
| Spec contract under-specification surfacing at audit time | The relevant spec contract | Phase 5 revision-pass (spec-writer SKILL) |
| ADR commitment under-specification surfacing at audit time | The relevant ADR | Phase 3a/3b revision (council-orchestrator + relevant C-voice) |
| CXA composition gap surfacing at audit time | CXA composition document | Phase 6 revision-pass |

### §6.3 In-project fork management reaffirmed

All forks at Session 2 route within this project workspace. NO transfer to new Claude Code CLI workspace at this stage.

---

## §7 Exit criteria

Session 2 closes when:

| # | Criterion | Verification |
|---|---|---|
| 1 | `Plan_Executability_Audit_v1.md` filed at `/mnt/user-data/outputs/` | File exists |
| 2 | Per-axis audit findings recorded for IS / AS / CP / OD / CXA | Deliverable §3.1–§3.5 non-empty |
| 3 | Aggregate findings recorded | Deliverable §4 non-empty |
| 4 | Class 1 / 2 / 3 fork inventory recorded | Deliverable §5 |
| 5 | Three Session 1 carry-forward audit targets resolved | Deliverable §6 + §7 + §8 |
| 6 | `Phase_6_5_Session_2_Close_Handoff.md` filed | File exists |
| 7 | `Phase_6_5_Session_3_Kickoff.md` filed | File exists |
| 8 | All Class 1 / 2 forks (if any) dispositioned with operator decision recorded | Close handoff §[forks] |

---

## §8 Forward routing

### §8.1 Immediate post-session artifacts

| Order | Artifact | Authored at |
|---|---|---|
| 1 | `Plan_Executability_Audit_v1.md` | Segment 5 |
| 2 | `Phase_6_5_Session_2_Close_Handoff.md` | Segment 5 |
| 3 | `Phase_6_5_Session_3_Kickoff.md` | Segment 5 |

### §8.2 Operator action between Session 2 and Session 3

Push the 3 outputs from `/mnt/user-data/outputs/` to `/mnt/project/`. Same between-session pattern.

### §8.3 Session 3 entry

Session 3 (ζ — F3-02 IS-axis revision pass) opens at next operator session entry against `Phase_6_5_Session_3_Kickoff.md`. Session 3 absorbs Session 2's audit findings; if Session 2 surfaces additional IS-axis findings beyond F3-02, they merge into Session 3 scope.

### §8.4 Conditional re-routing

If Session 2 surfaces Class 1 forks, the arc halts before Session 3 entry; operator decision per manifest §4.2 routes the resolution. Session 3 kickoff (this artifact's planned successor) may be deferred or restructured per the fork's disposition.

---

## §9 Recommended session opening protocol

When this session opens in a new Claude session:

1. **Load canonical Phase 6.5 substrate per §3.1.** Read manifest first; then Canonical Substrate Inventory; then Phase 7 Kickoff; then Session 1 deliverable + close handoff.
2. **Load Session-2-specific substrate per §3.2.** Read the 4 implementation plans + CXA composition document at canonical revisions.
3. **Verify entry-gate per §4.** Halt-and-ask if any item fails.
4. **Declare segmented delivery contract per §5.1.** Acknowledge to operator that delivery is 5-segment; operator confirmation at each boundary.
5. **Begin Segment 1.** Audit methodology declaration + IS axis audit.

If at any point a fork surfaces, halt segment; surface to operator with decision menu per §6 + manifest §4.2.

---

## §10 Filing footer

| Field | Value |
|---|---|
| Artifact | `Phase_6_5_Session_2_Kickoff.md` |
| Status | Filed at Session 1 close; ready for next-session execution |
| Phase | Phase 6.5 Session 2 (α) entry |
| Authoring discipline | Workflow v1.7 §7 fidelity-grammar; project session-prompt pattern (mirrors `Phase_6_5_Session_1_Kickoff.md` structure) |
| Predecessor | `Phase_6_5_Session_1_Close_Handoff.md`; `Target_Stack_Commitment_v1.md` |
| Companion (arc canonical) | `Phase_6_5_Pre_Transition_Arc_Manifest.md`; `Canonical_Substrate_Inventory.md` |
| Successor | `Plan_Executability_Audit_v1.md` (Segment 5 deliverable); `Phase_6_5_Session_2_Close_Handoff.md` (Segment 5) |
| Filing destination | `/mnt/user-data/outputs/Phase_6_5_Session_2_Kickoff.md` → operator pushes to `/mnt/project/` |
| Date | 2026-05-15 |

---

*End of Phase 6.5 Session 2 (α) Kickoff Prompt. Execute in new session against `Phase_6_5_Pre_Transition_Arc_Manifest.md` + `Canonical_Substrate_Inventory.md` + this artifact + §3 substrate. Segmented delivery contract per §5.1.*
