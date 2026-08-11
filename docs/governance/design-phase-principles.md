# Governance pack — design-phase operating principles

*Relocated BYTE-VERBATIM from Root `CLAUDE.md` §10 and §10.1–§10.9 by U-CTX-13 (R-CTX-1 Arc 5, 2026-08-11).*
*The root file keeps every heading with its number and position, plus a resolving
pointer to this file. Query this pack for the detail; do not preload it.*

---

## 10. Design-phase operating principles

*Applies to sessions doing design-phase work in this workspace (authoring/revising `design-substrate/*.md`). Phase 7 sessions consume design-substrate as canonical and operate under §§1–9 above; they do not author it. This section absorbs the framing originally encoded at the Drive `v3-system-prompt.md` (2026-05-09), updated for the post-Phase-6 committed state of H_T.*

### 10.1 Scope

These principles apply when a session is **authoring or revising** any of: ADRs, ADD, PRD, per-axis specs, per-axis plans, CXA, Workflow doc, Phase 7 Meta-Architecture, Sub-Agent Boundary Spec, fork docs, architect recommendations.

Phase 7 implementation sessions (touching `harness-*/src/`, etc.) are **out of scope** for §10 — they operate under §§1–9 and treat design-substrate as canonical.

The X-AL-3 silent-absorption rule (§4.4) is the hard boundary: Phase 7 sessions MUST NOT edit `design-substrate/*.md`. Mixed-scope sessions halt and route per §4.3.

### 10.2 What is committed at this stage

| Surface | Committed state | Source |
|---|---|---|
| Persona | Bridging-arc — `solo-developer` (design-time default) → `team-binding` → `multi-tenant-compliance`; `PersonaTier` is first-class (tier-distinct HITL-gate / redaction / sampler posture, exercised at R-CL-P3) | `Persona_Document_v1.md` §1/§2.1 (bridging-arc); Phase 2 persona surfacing |
| Stack | Python 3.12+ / Pydantic v2 / asyncio / uv / pyright strict / ruff / pytest | `Target_Stack_Commitment_v1.md` §5.1 (§3 of this doc) |
| Deployment surfaces | 3-tier: local-development / self-hosted-server / managed-cloud | ADR-D2 v1.2; ADR-F4 v1.1 |
| Multi-LLM | Anthropic + OpenAI + Ollama per-provider SDKs under capability-aware abstraction | ADR-F1 v1.2 |
| Foundational ADRs | F1–F5 + D1–D6 cleared at P3-CK | §2.2 |
| Architectural Design Document | v1.3 | §2.2 |
| PRD | v1.1 | §2.2 |
| Per-axis specs | All P5-CK cleared at v1+ | §2.3 |
| Per-axis plans | All P6-CK cleared at v2+ | §2.4 |
| Workflow doc | v1.19 (active discipline including §7.4 fidelity-grammar + §7.5 process-discipline catalogue; PD-9 adversarial-review-loop non-convergence discriminators — pointer verified current at v1.18 before this bump, no staleness this cadence) | §2.1 |
| Six topology patterns | 6-class enum locked at ADR-D4 v1.1 | §1.1 row CP |
| Permanent tensions | T-perm-1 (C4↔C10), T-perm-2 (C2↔C3), T-perm-3 (C1↔C9) resolved at canonical artifacts | §10.7 council voice-roster |

**Revisiting any committed surface above requires Class 1 fork → ADR back-flow per §4.3.** Not in-session re-litigation, not silent absorption at session-time.

### 10.3 What is NOT committed (and therefore live design surface)

| Surface | Status | Resolution path |
|---|---|---|
| In-flight per-axis spec revisions | Open per filed fork docs at `.harness/class_*_fork_*.md` | Operator ratification → spec-writer apply pass per §4.3 |
| In-flight per-axis plan revisions | Open per filed fork docs | implementation-planner revision absorption per §4.3 |
| CXA forward-tracking | Per `Cross_Axis_Composition_Document_v2_17.md` §0.4 marker CLOSED 2026-05-31 (6 PENDING → 6 ABSORBED at v2.17 §2.3.2 rows 38-43); future-PENDING marker now EMPTY | Per-CP-unit landing + CXA narrow-scope revision arcs (closed at v2.17 for the U-CP-74..U-CP-79 cohort) |
| Operating-principles refinements | Workflow v1.15 §7.4 + §7.5 lineage actively extends | Workflow doc revision per §7 of Workflow doc |

Anything not committed at §10.2 and not in §10.3 may require fresh design-phase work — surface to operator before authoring against absence.

### 10.4 Operating discipline for design-phase sessions

**Source-grounding.** Every non-trivial claim cites a specific resolvable source. Acceptable: byte-exact `§NN.M` cite to a design-substrate artifact at its current version; URL+date to vendor docs accessed this session; arXiv ID with title/authors. Not acceptable: "per Anthropic engineering posts," "the OTel spec says," or any reference that does not resolve to a single retrievable source.

**Confidence tagging.** Substantive claims carry `[HIGH]` / `[MODERATE]` / `[SPECULATIVE]` tags. A response with no `[SPECULATIVE]` tags anywhere is suspicious — most non-trivial design discussions carry at least one uncertain step.

**No fabrication.** Citations, version numbers, function signatures, file paths, line numbers — all of these must be empirically verified at session-time against the current state of the workspace. The `[[advisor-before-substantive-work-for-cross-axis-blockers]]` pattern (catalogued across 36+ applications in the workspace) is the active discipline: before authoring substantive changes, verify the cited surface exists at the version cited.

**Deterministic-vs-probabilistic.** Production reliability lives in the deterministic outer harness. Surface this boundary when it materially changes a recommendation — not as a default in every answer.

**Citation byte-exact.** Per Workflow §7.4.2 — when this `CLAUDE.md` cites a canonical artifact at version `v1.26`, the cite must resolve byte-exact to the version named.

### 10.5 Failure modes to actively prevent

These are inherited from the original v3 framing and remain operative. The five most-relevant for the post-Phase-6 committed state:

| Failure mode | Description | Mitigation |
|---|---|---|
| **Silent H_T design extension** | Phase 7 execution-time absorbs a not-yet-committed design surface as if it were canonical | X-AL-3 hard rule (§4.4); X-AL-3 guard (pre-commit + CI per follow-on PR) |
| **Fabricated citations** | Claims with cites that resolve to nothing, or that paraphrase memory of titles/sections/versions | Always verify empirically at session-time; prefer byte-exact grep over recall |
| **Silent scope narrowing** | When budget is tight, covering fewer surfaces than requested rather than segmenting delivery | Segment + announce continuation contract; do not omit silently |
| **Stale-carry-text disposition** | A finding flagged at v_N gets resolved at production/spec downstream, but the carry-text at v_{N+1}, v_{N+2}, ... is not refreshed; the carry becomes stale-as-described | Per Workflow §7.4.7 — pre-substantive empirical-verification audit at every amendment arc |
| **Cross-context bleed at venue boundary** | Design-phase session pulling Phase 7 implementation-detail framing into ADR/spec authoring, or vice versa | Posture declaration at session start (per follow-on PR); audit edit scope before committing |

### 10.6 Response shape

**Deliverable mode** — when authoring an artifact (ADR draft, spec amendment, plan revision, fork doc), the full apparatus applies: pre-condition gate, confidence tagging, citation specificity, segmentation if response exceeds budget, end with open questions + contested claims + recommended next probes.

**Conversational mode** — clarifications, scope checks, decisions between options. Confidence tags + citation specificity still required for non-trivial factual claims; the segmented-delivery / bibliography / pre-condition-gate apparatus does NOT apply.

Default to conversational mode when structure is unspecified.

### 10.7 Design-phase council

The eleven-voice council (Slate E11 — C1 through C11) lives at `.claude/skills/council/`:

- `.claude/skills/council/council-orchestrator/` — multi-voice deliberation router; emits Convening Block + CCR + voice contributions + TENSION block per `references/output-templates.md`.
- `.claude/skills/council/c1-orchestration/` through `c11-operator-loop-local-deployment/` — eleven subject-matter voices, each owning a domain across the four H_T axes (CP: C1/C5/C6/C9; AS: C4/C10; IS: C2/C3; OD: C7/C8/C11).

Council activates on multi-domain design questions, cross-cutting concerns by name (security / observability / cost / reliability / eval-ability / HITL-local-first), or explicit operator convocation. Single-domain questions route directly to the named voice. See orchestrator `SKILL.md` for full activation discipline.

The council composes with the existing role-discipline skills:

- `systems-architect` — ADD consolidation, Phase 7 architectural-tension resolution. Convenes council voices as sources of domain depth.
- `spec-writer` — applies operator-decided fixes to specs. Consumes council deliberations as authority anchor.
- `implementation-planner` — decomposes specs to atomic units. Operates after spec-writer.
- `harness-adversarial-reviewer` — red-teams completed artifacts. Consumes council deliberations.

### 10.8 Continuity discipline

Multi-session work carries forward decisions, terminology, and scope established in earlier sessions. The canonical record is the design-substrate corpus + fork doc ledger at `.harness/` + workspace `CLAUDE.md` row updates + memory entries at `/Users/robertrhu/.claude/projects/-Users-robertrhu-Projects-arhugula-v2/memory/`.

When a new request contradicts a prior decision, surface the contradiction explicitly and ask before overwriting. Do not silently override a committed surface.

This workspace operates in strict isolation from any other project. Within-workspace, the design-phase venue and the Phase 7 execution venue are **logically separate** even though physically co-resident in the same git repo — the X-AL-3 rule (§4.4) is the boundary.

### 10.9 Standing posture — council + adversarial reviewer + research corpus (2026-05-31 bake-in)

Standing posture amendments from the H_T-IS-2 cascade-scope council pilot (2026-05-31) — encoded here so they auto-apply at every session without HITL invocation.

**Council orchestrator (`.claude/skills/council/council-orchestrator/`):**

1. **Nameable-tension discriminator at activation.** Before convening, ask: can I name in advance a tension I expect between two voices? If no, route to single voice + advisor(). The pilot's lesson — councils that converge to single-voice + cosmetic consultants are primary-collapse failures. Tension-surfacing is the load-bearing value.
2. **Dyadic mode default.** Default convening size is 2 voices (primary + 1 consultant), not 3. Expand to 3 only when you can name a distinct third axis-specific concern AND Layer C scoring places a 3rd voice meaningfully above threshold. Hard cap at 5 unchanged.
3. **Slim CCR.** Enumerate Touched concerns only with one-sentence pre-check notes; collapse Not-Touched concerns into a single `n/a` line listing unaddressed concerns by name. CCR ritualization (6 verbose rows every time) is the failure mode being corrected.
4. **Pre-bind to current spec versions.** Each convened voice's first cite MUST be from the canonical spec at the current version recorded in workspace `CLAUDE.md` §2 at session-start (not freelance from SKILL.md memory). External authority citations from `.harness/01-planning/` are encouraged when intra-spec authority is insufficient.
5. **Probe-first discipline at tension resolution.** Before emitting any TENSION block, run a 1-5 minute empirical probe at the most specific primary source relevant to the dispute. The pilot's lesson — council surfaces, primary sources decide. If probe resolves the tension, surface as `surfaced + probe-resolved` with the probe finding as resolution rationale. If probe is silent, emit Layer 1 surfaced-unresolved.

**Adversarial reviewer (`.claude/skills/harness-adversarial-reviewer/`):**

1. **Pre-merge gate posture.** Fire at PR-open / PR-ready-for-review for any `design-substrate/**` amendment or Phase 7 impl arc against previously-cleared spec/plan — not post-merge. X-AL-3 guard is file-presence; adversarial review is substantive complement.
2. **Pattern-catalogue-aware standing checklist.** Every review audits against the 9-item workspace pattern checklist (stale-carry-text disposition; sibling-spec staleness; forward-looking cite phantom; checkpoint-listed-as-open-but-already-applied; plan-revision-against-not-yet-built-substrate; spec-prose-vs-plan-body drift; verification-shape grep-vs-e2e; X-AL-3 anti-extension; halt-route-split-AC). Findings against checklist items follow standard Class 1/2/3 discriminator.
3. **Cross-spec drift probes.** For any per-axis spec/plan review, MUST grep across sibling specs/plans for stale cite-shapes against the artifact under review. The workspace's biggest defect class is cross-spec coordination drift; intra-artifact review misses it structurally.
4. **External-canon mode (NEW Class 2 finding category).** Review the artifact's contracts/patterns against canonical industry patterns at `.harness/01-planning/Pattern_Reference_Catalog_v1.0.md` + cluster deep-dives. Flag divergences as either (a) intentional + needs ADR/spec rationale, or (b) accidental + needs correction. Voice → cluster mapping at `.claude/skills/council/council-orchestrator/references/research-citations.md`.

**Research corpus (`.harness/01-planning/`):**

The Phase 1 substrate at `.harness/01-planning/` (11 files, ~8,500 lines) was consumed and crystallized into ADRs + ADD + PRD + specs at the design phase. For settled design decisions, the corpus is derivative-redundant. For ongoing work, it serves three roles:

1. **Council external-authority citations.** Voices cite cluster deep-dives or Pattern Reference Catalog when their position needs grounding beyond intra-spec authority. Voice → cluster mapping at `.claude/skills/council/council-orchestrator/references/research-citations.md`.
2. **Phase 7 implementation grounding.** Before authoring any cluster impl arc, grep the relevant cluster deep-dive for production failure modes from real systems (LangGraph, Temporal, OpenAI Agents SDK).
3. **Adversarial reviewer external-canon mode.** Per posture amendment 4 above.

**`agentic-engineeriing-sdlc.md`** at `.harness/01-planning/` is NEW (not in the Phase 1 council context). It applies the 8-phase canonical SDLC to agent-native development as a delta against an `sdlc-research.md` baseline. Currently mapped to **workflow doc v1.14+ revision arcs** rather than a council voice's primary domain. When workflow v1.14 revision opens, this file SHOULD be consulted for: Phase 7 → Phase 8 retirement criteria; cross-cutting concern application (PM/Risk/CM/QA/Security/Compliance/Documentation/Measurement); canonical SDLC checkpoint vs. workspace's P3a-CK/P3-CK/P5-CK/P6-CK convention gap analysis.

---

