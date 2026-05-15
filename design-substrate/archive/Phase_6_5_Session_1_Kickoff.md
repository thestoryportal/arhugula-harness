# Phase 6.5 Session 1 Kickoff — Target Stack Commitment (δ)

*Session entry artifact for Phase 6.5 Session 1. Loaded as substrate at session open. Authored at design-phase workspace; executed in a new session in this same project workspace.*

---

## §1 Session identity

| Field | Value |
|---|---|
| Artifact | `Phase_6_5_Session_1_Kickoff.md` |
| Phase | Phase 6.5 (provisional pre-transition arc; formal Workflow §6.5 specification authored at Session 5) |
| Session number | 1 of 7 |
| Session designator | δ |
| Session name | Target Stack Commitment |
| Skill activation | None (focused deliberation mode; ad-hoc C-voice consultation where specific tradeoffs warrant) |
| Authoring authority | Operator directive 2026-05-14 ("Proceed with #1 [full pre-transition rigor]; for Session 1: focused deliberation, no formal skill") |
| Predecessor artifact | `P6-CK_Iter4_Revision_Cycle_Close_Handoff.md` (Phase 6 close) |
| Companion artifact (canonical for entire arc) | `Phase_6_5_Pre_Transition_Arc_Manifest.md` |
| Successor artifact (at session close) | `Phase_6_5_Session_1_Close_Handoff.md` + `Phase_6_5_Session_2_Kickoff.md` |

---

## §2 Session scope

### §2.1 In scope

Commit the target stack the v2.3 implementation plans materialize against. The committed stack governs Phase 7 execution at the new Claude Code CLI workspace. Specific decisions:

1. **Programming language** (likely Python; alternatives considered: TypeScript, Rust)
2. **Package manager** (e.g., `uv`, `poetry`, `pip + venv`, `npm`, `cargo`)
3. **Type checker** (e.g., `pyright`, `mypy`, `tsc`)
4. **Linter / formatter** (e.g., `ruff`, `black`, `eslint`, `prettier`, `clippy`)
5. **Test runner** (e.g., `pytest`, `unittest`, `vitest`, `cargo test`)
6. **Repo structure** (monorepo with axis-subdirectories; single-package; multi-package; workspace organization)
7. **Git posture** (branching strategy; commit-per-unit vs PR-per-unit; conventional commits or other)
8. **CI substrate** (or explicit non-commit; CI may defer to post-bootstrap milestone)
9. **Multi-LLM provider SDK stance** (per ADR-F1 v1.2 — abstraction shape determines SDK approach)
10. **OTel SDK selection** (per ADR-D6 v1.2 + OD axis observability commitments)
11. **Local-development ergonomics** (sqlite per OD axis ledger commitments; OS keychain per ADR-F5 v1.1)
12. **Core dependency stance** — minimal-framework principle: AVOID LangGraph / Temporal / similar as foundational substrate; H_T's design must emerge from atomic-unit implementation, not be pre-empted by a framework that already does what H_T's axes specify

### §2.2 Out of scope

- H_T design revisions (ADRs / specs / plans) — these are committed at Phase 6 close
- Persona revisions — committed at Phase 2 close
- Workflow revisions — Session 5 owns this
- Plan executability validation against committed stack — Session 2 (α) owns this
- Meta-architecture (H_T ↔ H_E substitution mapping) — Session 4 (η) owns this
- Bootstrap substrate (CLAUDE.md + custom skills) — Session 6 (ε) owns this

If session deliberation surfaces a question about any of these, route per §6 fork-handling.

### §2.3 Deliverable

`Target_Stack_Commitment_v1.md` — operator decision artifact filed at `/mnt/user-data/outputs/`. Recommended structure:

- §1 Status block
- §2 Constraints enumeration (from substrate)
- §3 Stack candidate matrix
- §4 Tradeoff deliberation summary
- §5 Operator decision (committed stack with rationale)
- §6 Alternatives considered + reasons for rejection
- §7 Tradeoff acknowledgments (known limitations of committed stack)
- §8 Forward implications (what downstream sessions absorb from this commitment)
- §9 Filing footer

Filed as: standalone artifact (recommended) OR addendum to `Architectural_Design_Document_v1_3.md` per operator preference at Segment 4.

---

## §3 Substrate retrieval

### §3.1 Canonical Phase 6.5 substrate (load first)

| # | Artifact | Path | Role |
|---|---|---|---|
| 1 | `Phase_6_5_Pre_Transition_Arc_Manifest.md` | `/mnt/project/` (or `/mnt/user-data/outputs/` if not yet pushed) | Arc framing + sequence context + fork-handling discipline |
| 2 | `Canonical_Substrate_Inventory.md` | `/mnt/project/` (or `/mnt/user-data/outputs/`) | KB navigation anchor; disambiguates canonical vs superseded artifacts at retrieval time |
| 3 | `Phase_7_Kickoff_Prompt.md` | `/mnt/project/` (or `/mnt/user-data/outputs/`) | Phase 7 entry framing + execution discipline + back-flow routing |
| 4 | `P6-CK_Iter4_Revision_Cycle_Close_Handoff.md` | `/mnt/project/` (or `/mnt/user-data/outputs/`) | Phase 6 close record + Phase 7 entry authorization |

### §3.2 ADR substrate (Session-1-specific — language-and-stack-relevant)

| ADR | Version | Why relevant to Session 1 |
|---|---|---|
| ADR-F1 | v1.2 | Multi-LLM provider abstraction shape — determines SDK approach (provider-specific SDKs vs unified abstraction vs raw HTTP) |
| ADR-F2 | v1.2 | Filesystem-as-shared-substrate depth — determines repo structure + git-as-state-mechanism + filesystem-API requirements |
| ADR-F3 | v1.1 | Durable-execution coordination spine commitment — determines whether stack needs a durable-execution library or can implement primitives directly |
| ADR-F4 | v1.1 | Sandbox-isolation-strength-by-trust-level — determines sandbox library/mechanism requirements |
| ADR-F5 | v1.1 | OS-keychain-at-dev / vault-at-prod secret abstraction — determines secrets library |
| ADR-D2 | v1.1 | Tool / MCP integration — determines MCP client library + tool-schema validation library |
| ADR-D3 | v1.2 | (Reliability & retry) — determines retry / breaker library |
| ADR-D5 | v1.3 | Validation contract — determines schema validation library (pydantic vs zod vs serde) |
| ADR-D6 | v1.2 | OTel observability + retry mechanics — determines OTel SDK selection |

### §3.3 ADD + PRD + Persona substrate (cross-cutting context)

| Artifact | Path | Role |
|---|---|---|
| `Architectural_Design_Document_v1_3.md` | `/mnt/project/` | Architectural consolidation; cross-axis implications |
| `PRD_v1_1.md` | `/mnt/project/` | Observable-behavior implications (some R-* may constrain stack — e.g., R-OD-* observability requirements) |
| `Persona_Document_v1.md` | `/mnt/project/` | Persona-tier discipline; ergonomics expectations (e.g., local-dev ergonomics) |

### §3.4 Spec + plan substrate (consulted ad-hoc)

Per session need:
- Axis specs (IS v1.2 / AS v1.1 / CP v1.3 / OD v1.3) for contract-level implications
- Plan signatures (IS plan v2.1 / AS plan v1 / CP plan v2.3 / OD plan v2.3 / CXA v2.1) for atomic-unit-level type-checker + language-feature implications
- Specifically Session 1 should sample a few high-signature-density units to check language feasibility (e.g., U-CP-07 retry namespace; U-OD-20 ledger entry; U-IS-12 / 14 / 15 / 16 cluster around state ledger)

### §3.5 V3 system prompt

The V3 system prompt is loaded at workspace level. Carries forward verbatim per Phase 7 Kickoff §2.1. Confidence tagging + source-grounding discipline apply at this session.

---

## §4 Entry-gate verification

At session open, verify:

| # | Check | Verification |
|---|---|---|
| 1 | Phase 6.5 manifest accessible | `project_knowledge_search` returns content |
| 2 | Phase 6 closed at v2.3 / v2.1 / v1 | Per `P6-CK_Iter4_Revision_Cycle_Close_Handoff.md` §9.2 entry-gate disposition CLEARED |
| 3 | Phase 7 entry authorization GRANTED | Same source §9.2 |
| 4 | ADR substrate accessible (§3.2 list) | `project_knowledge_search` returns content for each |
| 5 | ADD + PRD + Persona accessible | Same |
| 6 | No open Class 1 forks from prior sessions | Manifest §4.1 review (Session 1 is arc entry; no priors) |

If any entry-gate item fails, halt session open; surface to operator before proceeding.

---

## §5 Session execution discipline

### §5.1 Segmented delivery contract

4-segment delivery; operator confirmation at each segment boundary:

| Segment | Scope | Approximate output |
|---|---|---|
| 1 | Constraints enumeration from ADR + persona + project commitments | Constraint inventory table; 8–12 constraints; each constraint cited to source artifact + section |
| 2 | Stack candidate matrix (3–4 candidates × 8–10 evaluation axes) | Candidate-vs-axis matrix; per-cell short justification with confidence tagging |
| 3 | Tradeoff deliberation with ad-hoc C-voice perspectives | Narrative deliberation; explicit C-voice consultations where invoked; convergence toward recommended stack |
| 4 | Operator decision + artifact filing + Session 2 kickoff authoring | `Target_Stack_Commitment_v1.md` filed; `Phase_6_5_Session_1_Close_Handoff.md` filed; `Phase_6_5_Session_2_Kickoff.md` filed |

### §5.2 C-voice consultation discipline

This session does NOT convene the full council (over-scoped for stack commitment). Ad-hoc C-voice consultation pattern:

- Invoke a single C-voice perspective when a stack tradeoff has a clear voice-owner (e.g., "C7, what does the observability substrate care about per language?" for OTel SDK maturity questions)
- Do NOT invoke multiple voices simultaneously
- Do NOT trigger CCR (cross-cutting reasoning) artifacts
- Each ad-hoc consultation is a single paragraph; cite the voice; integrate with overall deliberation

Voices likely invoked in this session:
- **C7 (Observability Architect)** — OTel SDK maturity per language; structure-not-content discipline implications
- **C9 (Reliability & Recovery)** — retry/breaker library availability per language; primitives-vs-library tradeoffs
- **C4 (Tool & Integration Surface)** — MCP client library availability; tool schema validation
- **C11 (Operator & Local Deployment)** — local-dev ergonomics; sqlite ergonomics; OS keychain access

### §5.3 Halt-and-ask discipline

Per `Phase_6_5_Pre_Transition_Arc_Manifest.md` §4 fork-handling — surface explicitly with operator decision menu when:

- Stack deliberation surfaces a Class 1 finding (severe; invalidates a Phase 6 commitment OR cascade-substrate-clearance)
- Stack deliberation surfaces a Class 2 finding (moderate; design-phase artifact defect surfaceable)
- Operator-decision-required item arises beyond pre-session OD scope
- Substrate retrieval returns unexpected content (e.g., ADR cite resolves to missing section)

Halt-and-ask is NOT a finding-class assertion; it is the discipline ensuring scope discoveries surface explicitly.

### §5.4 Confidence tagging discipline

Per V3 system prompt — every substantive claim tagged `[HIGH]` / `[MODERATE]` / `[SPECULATIVE]`. Specific to stack deliberation:

- Library version + maturity claims: verify against primary sources (PyPI / npm / crates.io) at this session; `[HIGH]` only if verified, otherwise `[MODERATE]` with note
- Performance claims: `[SPECULATIVE]` unless benchmark cited
- Ecosystem maturity claims: `[MODERATE]` typically; `[HIGH]` only if grounded in current documentation accessed this session
- Tradeoff claims: `[HIGH]` for well-known tradeoffs cited in primary sources; `[MODERATE]` for synthesis claims; `[SPECULATIVE]` for hypothesis-level claims

### §5.5 Anti-fabrication discipline

Per V3 — NEVER invent:
- Library version numbers
- Vendor capabilities not verified at this session
- Benchmark figures
- Maturity claims not grounded in primary documentation
- ADR section citations (verify against ADR substrate at this session)

If a fact cannot be verified against a source accessed this session, mark `[SPECULATIVE]` or omit.

---

## §6 Fork handling at Session 1

Per manifest §4 fork-handling discipline:

### §6.1 Anticipated Class 2 fork triggers

Specific to Session 1 — Class 2 forks may surface if stack deliberation reveals:

| Trigger | Affected design-phase artifact | Routing |
|---|---|---|
| ADR-F1 abstraction shape implies stack with poor multi-LLM SDK ecosystem | F1 v1.2 OR F1-derived plan units | Phase 3a/3b ADR revision OR Phase 6 plan revision |
| ADR-D6 OTel commitments imply stack with poor OTel SDK | D6 v1.2 OR OD axis units | Same routing |
| Spec contract implies language feature unavailable in any reasonable stack | Spec contract | Phase 5 spec revision-pass |
| Persona ergonomics commitment incompatible with all reasonable stacks | Persona document | Phase 2 revision-pass |

### §6.2 Anticipated Class 1 fork triggers

Class 1 forks at Session 1 imply a Phase 6 commitment is broken. Examples:

- No reasonable stack can implement the v2.3 plans at production-grade fidelity → cascade-substrate-clearance invalidated
- Cross-axis composition seam (CXA v2.1 §[topological sort]) implies execution-time dependency that no stack supports → P6-CK clearance invalidated

These are unlikely at this session (the v2.3 plans are language-agnostic by design), but if surfaced, route per manifest §4.2 with operator decision menu.

### §6.3 In-project fork management reaffirmed

All forks at Session 1 route within this project workspace. NO transfer to new Claude Code CLI workspace at this stage. Forks discovered at Phase 7 execution (post-arc-completion) route back per Phase 7 Kickoff §6 back-flow discipline.

---

## §7 Exit criteria

Session 1 closes when:

| # | Criterion | Verification |
|---|---|---|
| 1 | `Target_Stack_Commitment_v1.md` filed at `/mnt/user-data/outputs/` | File exists |
| 2 | Operator decision recorded at §5 of deliverable | Operator confirmation at Segment 4 |
| 3 | `Phase_6_5_Session_1_Close_Handoff.md` filed | File exists |
| 4 | `Phase_6_5_Session_2_Kickoff.md` filed | File exists |
| 5 | All Class 1 / 2 forks (if any) dispositioned with operator decision recorded | Close handoff §[forks] |
| 6 | Constraint inventory + candidate matrix + tradeoff deliberation preserved at deliverable | Deliverable §2–§4 non-empty |

---

## §8 Forward routing

### §8.1 Immediate post-session artifacts

| Order | Artifact | Authored at |
|---|---|---|
| 1 | `Target_Stack_Commitment_v1.md` | Segment 4 |
| 2 | `Phase_6_5_Session_1_Close_Handoff.md` | Segment 4 |
| 3 | `Phase_6_5_Session_2_Kickoff.md` | Segment 4 |

### §8.2 Operator action between Session 1 and Session 2

Push the 3 outputs from `/mnt/user-data/outputs/` to `/mnt/project/`. Phase 6.5 sessions use same between-session push pattern as Phase 6.

### §8.3 Session 2 entry

Session 2 (α — Pre-flight executability audit) opens at next operator session entry against `Phase_6_5_Session_2_Kickoff.md`. Session 2 absorbs Session 1's committed stack and validates plan executability against it.

---

## §9 Recommended session opening protocol

When this session opens in a new Claude session, the recommended opening sequence:

1. **Load substrate per §3.** Read manifest first; then Phase 7 Kickoff; then ADR substrate; then ADD / PRD / Persona overview.
2. **Verify entry-gate per §4.** Halt-and-ask if any item fails.
3. **Declare segmented delivery contract per §5.1.** Acknowledge to operator that delivery is 4-segment; operator confirmation at each boundary.
4. **Begin Segment 1.** Constraints enumeration.

If at any point a fork surfaces, halt segment; surface to operator with decision menu per §6 + manifest §4.2.

---

## §10 Filing footer

| Field | Value |
|---|---|
| Artifact | `Phase_6_5_Session_1_Kickoff.md` |
| Status | Filed at design-phase workspace; ready for next-session execution |
| Phase | Phase 6.5 Session 1 |
| Authoring discipline | Workflow v1.7 §7 fidelity-grammar; project session-prompt pattern |
| Predecessor | `P6-CK_Iter4_Revision_Cycle_Close_Handoff.md` (Phase 6 close) |
| Companion (arc canonical) | `Phase_6_5_Pre_Transition_Arc_Manifest.md` |
| Successor | `Phase_6_5_Session_1_Close_Handoff.md` (authored at Segment 4) |
| Filing destination | `/mnt/user-data/outputs/Phase_6_5_Session_1_Kickoff.md` |
| Date | 2026-05-14 |

---

*End of Phase 6.5 Session 1 Kickoff Prompt. Execute in new session against `Phase_6_5_Pre_Transition_Arc_Manifest.md` + this artifact + §3 substrate. Segmented delivery contract per §5.1.*
