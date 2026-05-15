# Phase 5 Entry Handoff

## Status block

| Field | Value |
|---|---|
| Artifact | `Phase_5_Entry_Handoff.md` |
| Status | **Filed** — routing substrate for Phase 5 specification authoring arc |
| Date | 2026-05-13 |
| Phase | 4 close → Phase 5 entry boundary |
| Substrate | `PRD_v1.0.md` (Phase 4 output; primary Phase 5 substrate); `Architectural_Design_Document_v1.md` v1.2 (deeper substrate); `Persona_Document_v1.md` (persona-linkage trace); F1 v1.2 + F2 v1.2 + F3 v1.1 + F4 v1.1 + F5 v1.1 + D1 v1.1 + D2 v1.1 + D3 v1.1 + D4 v1.1 + D5 v1.3 + D6 v1.1 ADRs (canonical commitment substrate); `Project_Workflow_v1_2.md` §2.5 + §2.5.1 (Phase 5 + P5-CK framing) |
| Skill activation | `spec-writer` SKILL.md (Stage-3 final-specification mode per skill description) + council voices as consultants per Workflow §2.5 Execution agent + council-orchestrator escalation when cross-voice contract precision needed |
| Entry authorization | `PRD_v1.0.md` filed at `/mnt/user-data/outputs/` with coherence pass ✅ PASS at all five dimensions; Phase 4 CLOSED (no P4-CK declared in Workflow v1.4); Phase 5 entry-gate AUTHORIZED per Phase_4_Session_Prompt.md §8.1 |
| Arc shape | Multi-session (4–6 sessions per Workflow §2.5 Sessions field); per-session session prompts authored at each session boundary; this handoff scopes the arc; `Phase_5_Session_1_Session_Prompt.md` scopes session 1 |
| Exit gate | All authored specification documents filed; every PRD requirement satisfied by ≥1 specification element; every ADR commitment honored; `Adversarial_Review_5.md` filed at P5-CK clearance per Workflow §2.5.1 |

---

## 1. Operator pre-decisions (ODs) — full menu at session 1 entry

Four ODs govern Phase 5 arc entry. The full menu is presented at session 1 entry via tappable `ask_user_input_v0` selection menus per established project protocol. Default-vector activation: `Proceed with defaults` applies OD-5-1.A + OD-5-2.A + OD-5-3.A + OD-5-4.A in one step.

### 1.1 OD menu

| OD | Question | Options | Default | Rationale |
|---|---|---|---|---|
| OD-5-1 | Specification decomposition shape? | A: Per-axis multi-document (4–5 docs mirroring ADD/PRD axes; one axis spec per session); B: Single monolithic `Specification_v1.md` across 4–6 sessions; C: Per-PRD-requirement spec sections (31 spec sections mirroring PRD precisely) | **A** | Workflow §2.5 outputs field reads "likely multi-document; structure determined by the ADD" — the ADD's axis structure (§2 / §3 axis groupings) is the natural decomposition. Mirrors the PRD's axis-led shape (OD-4-1.A) for trace-back continuity |
| OD-5-2 | Session-1 axis scope? | A: Spec-writer judgment at session-1 entry (recommendation: Information Substrate per §3.1); B: Operator-declared at handoff (operator names axis); C: Spec-writer authors §0 cross-axis composition primer before per-axis work | **A** | Spec-writer judgment preserves authoring flexibility; recommendation surfaced at §3.1 below |
| OD-5-3 | Council-voice consultant invocation pattern? | A: As-needed during authoring (spec-writer escalates to `council-orchestrator` when contract precision requires cross-voice deliberation); B: Pre-declared per session (operator names voices at each session entry) | **A** | Workflow §2.5 Execution agent reads "spec-writer (existing skill) + council voices as consultants"; as-needed escalation matches the consultant pattern and avoids over-convening |
| OD-5-4 | P5-CK review scope? | A: Aggregate review at full specification close (one P5-CK invocation after all spec documents file) per Workflow §2.5.1 Sessions field "1 session"; B: Per-axis review at each spec document close (P5-CK invocations spread across sessions) | **A** | Workflow §2.5.1 specifies 1 review session with full specification as input; aggregate review matches the workflow framing |

### 1.2 ODs explicitly NOT at the menu (non-decisions per skill discipline)

| Rejected OD | Reason for rejection |
|---|---|
| Specification grade for cross-cutting properties (specification-grade thresholds vs deferred to implementation discretion) | Per Workflow §2.5.1 exit criteria: "ambiguities either resolved or explicitly deferred to implementation discretion" — the choice is per-contract not session-level; spec-writer surfaces per-contract |
| ADR re-authoring vs index-by-citation discipline | Discipline-fixed at index-by-citation: the specification translates PRD requirements into contract precision via composition with ADR-committed material; ADRs remain canonical for architecture they commit. Re-authoring ADR material in specification would violate the project's inversion discipline analog at Phase 5. Specification adds contract precision WHERE ADRs are silent or PRD-grade only |
| PRD requirement re-statement at spec sections | Discipline-fixed at translate-not-restate: per `prd-author` SKILL.md §9 anti-pattern (ADR paraphrase) extended to spec-writer; spec sections translate PRD requirements into contracts without restating PRD text |

---

## 2. Routing matrix

### 2.1 Arc routing shape

```
Phase 4 close (PRD_v1.0.md filed; coherence pass ✅ PASS)
  │
  ▼
Phase 5 entry-gate AUTHORIZED (this handoff)
  │
  ├─ OD menu at session 1 entry → operator selection or "Proceed with defaults"
  │
  ▼
Session 1: Per-axis spec authoring (axis per OD-5-2 selection)
  │  ├─ spec-writer SKILL.md activated (Stage-3 final-specification mode)
  │  ├─ Council-voice consultant escalation per OD-5-3
  │  ├─ Pre-emission self-audit before filing
  │  └─ Phase 5 session prompt for session 2 authored at session 1 close
  │
  ▼
Session 2..N: Per-axis spec authoring (axes remaining per OD-5-1.A; N depends on §3 advisory)
  │  ├─ Same skill activation pattern
  │  ├─ Each session inherits prior-session-filed specs as substrate
  │  └─ Each session authors next session's session prompt at close
  │
  ▼
Final session: Top-level Specification_v1.md cross-axis composition document
  │  ├─ Spec-writer authors composition layer over per-axis specs
  │  ├─ Coherence pass across all axis specs + composition document
  │  └─ Pre-P5-CK self-audit
  │
  ▼
P5-CK entry-gate AUTHORIZED per Workflow §2.5.1
  │
  ▼
P5-CK adversarial review session (1 session per Workflow §2.5.1 Sessions field)
  │  ├─ harness-adversarial-reviewer SKILL.md activated (specification review mode)
  │  ├─ Inputs: full specification (per-axis docs + composition document)
  │  └─ Output: Adversarial_Review_5.md
  │
  ▼
P5-CK disposition routing:
  ├─ All Class-3 findings resolved + ambiguities resolved-or-deferred → P5-CK CLEARED → Phase 6 entry-gate AUTHORIZED
  ├─ Class-3 findings unresolved → spec revision pass (analog to ADD revision passes) → P5-CK iter-2
  └─ Workflow re-opening (Adv-3) → phase re-open per Workflow §3 fork triggers
```

### 2.2 Per-session session prompt authoring pattern

Each Phase 5 session authors the next session's session prompt at session close, following the pattern Phase 3a/3b/3c/3d sessions established. Session prompt scope: which axis (per OD-5-1.A) is in scope, which spec contracts are produced, which substrate sections are read at session entry, which carry-forwards inherit.

---

## 3. Session-shape sketch (advisory)

Per OD-5-1.A (per-axis multi-document) and Workflow §2.5 (4–6 sessions estimate). The sequencing below is **recommended**; spec-writer judgment at OD-5-2.A may diverge based on per-axis substrate density observed at session 1 entry.

### 3.1 Recommended axis sequencing

| Session | Axis | ADRs in scope | PRD requirements in scope | Output | Rationale |
|---|---|---|---|---|---|
| 1 | Information substrate | F2 v1.2 | R-IS-01 through R-IS-04 (4 requirements) | `Spec_Information_Substrate_v1.md` | Smallest axis surface (1 ADR, 4 requirements); F2 state-ledger entry shape is the substrate seam every downstream axis composes against; natural session-1 warmup that locks the substrate contract for the arc |
| 2 | Action surface | F4 v1.1 + F5 v1.1 + D2 v1.1 + D3 v1.1 | R-AS-01 through R-AS-07 (7 requirements) | `Spec_Action_Surface_v1.md` | F-layer sandbox + secrets contracts settled at ADR; D2 §1.7 sandbox-bounded span schema + §1.8 fail-class taxonomy + D3 §1.8.1 six namespaces are specification-grade material already in ADRs — spec composes via citation + gap-fill |
| 3 | Control plane | F1 v1.2 + F3 v1.1 + D1 v1.1 + D4 v1.1 + D5 v1.3 | R-CP-01 through R-CP-12 (12 requirements) | `Spec_Control_Plane_v1.md` | Largest axis (5 ADRs, 12 requirements); heaviest cross-axis composition (T-perm-3 settlements across F1, F3, D1, D4, D5; D5 cross-axis HITL composition). Sequenced after action surface so D5 § ↔ F4 sandbox composition can cite filed action-surface spec |
| 4 | Operational discipline | D6 v1.1 (with operational-discipline secondary-axis surfaces from F1, F2, F3, F4, F5, D1, D2, D3, D4, D5) | R-OD-01 through R-OD-08 (8 requirements) | `Spec_Operational_Discipline_v1.md` | D6 absorbs span attribute namespaces from all five D-ADRs per ADD §3.4.1 — natural last per-axis session because composes against everything else; specification can cite filed per-axis specs for namespace-source declarations |
| 5 (optional) | Cross-axis composition | All 11 ADRs + all 31 PRD requirements + 8 in-scope bridging-arc transitions | `Specification_v1.md` (top-level composition + index) | Cross-axis emergent properties (T-perm-1 5-axis tunable, T-perm-2 multi-seam, T-perm-3 D1/D4 composition, bridging-arc invariants, replay-determinism semantics) get a single specification-grade composition document. Per Workflow §2.5 outputs field "likely multi-document" — this is the top-level |
| 6 (optional) | Pre-P5-CK self-audit pass | Full specification surface | `Specification_v1_pre_P5-CK_audit.md` | Pre-P5-CK self-audit analogous to PRD §[coherence pass]; verifies every PRD requirement satisfied by ≥1 spec element; every ADR commitment honored; cross-spec consistency (Sessions 5-6 may collapse into one) |

**Session count estimate.** 4 sessions minimum (per-axis only, no top-level composition); 5 sessions typical (per-axis + composition); 6 sessions if pre-P5-CK self-audit warrants a dedicated session. Within Workflow §2.5 "4-6 sessions" estimate.

### 3.2 Single-axis-per-session alternative

If session 1 spec-writer judgment surfaces unanticipated per-axis density, the per-axis split may extend (e.g., Action Surface split into F-layer session + D-layer session). Operator may also collapse sessions 2-3 if Action Surface + Control Plane density is low. Spec-writer surfaces session-count adjustment at session 1 close per OD-5-2.A judgment authority.

---

## 4. Carry-forwards inherited from PRD §[carry-forwards]

Two items inherited from `PRD_v1.0.md` §[carry-forwards]. Each must be addressed at session 1 entry.

### 4.1 [CF-1] F2-12 — D1 v1.1 → v1.2 replay-trace-emission contract

| Dimension | Status |
|---|---|
| Origin | ADD v1.2 §6.3.1 deferred-acknowledged; carried at PRD §[carry-forwards] [CF-1]; impacts R-CP-07 contract precision |
| Current state | Deferred-acknowledged; not blocking Phase 5 entry; not blocking session 3 (Control Plane) authoring |
| Phase 5 disposition | Specification of R-CP-07 (replay-resumption semantics) binds at engine-class-visible granularity only per PRD §[carry-forwards] [CF-1]; per-event-class replay-emission contract carries forward to Phase 5 §[carry-forwards] for explicit operator-visibility; spec contract is open at the replay-emission attribute layer until D1 v1.2 + D6 v1.2 land |
| Forward routing | Parallel `council-orchestrator` C7+C9 session at operator discretion per ADD §6.3.1 active path; closure expected as D1 v1.2 + D6 v1.2 absorbed into ADD v1.3 → PRD revision pass (`PRD_v1.1.md`) → Phase 5 revision-pass at affected spec sections |

### 4.2 [CF-2] Workflow §7 substrate-skill propagation

| Dimension | Status |
|---|---|
| Origin | `Project_Workflow_Revision_log.md` v1.4 entry line 297 footnote; carried at PRD §[carry-forwards] [CF-2] |
| Current state | Outside Phase 5 scope (skill-substrate revision territory) |
| Phase 5 disposition | Not in specification scope; documented at Phase 5 §[carry-forwards] for operator-visibility continuity from PRD §[carry-forwards] |
| Forward routing | Operator decision at discretion; no specification revision triggered |

---

## 5. Entry-gate verification (verified at session 1 entry per session prompt §4)

Six entry-gate criteria. Spec-writer verifies all six at session 1 open before authoring begins.

| # | Verification | Source of evidence |
|---|---|---|
| 1 | `PRD_v1.0.md` filed and coherence-pass-passed | File present at project KB; PRD §[coherence pass] returns ✅ PASS at all five audit dimensions |
| 2 | ADD v1.2 ratified and P3-CK-cleared | `Adversarial_Review_3_iter3.md` §7.1 disposition §4.1.1 CLEARANCE; ADD status block reads v1.0 → v1.1 → v1.2 |
| 3 | `Persona_Document_v1.md` available | Present at project KB |
| 4 | F1 v1.2 + F2 v1.2 + F3 v1.1 + F4 v1.1 + F5 v1.1 + D1 v1.1 + D2 v1.1 + D3 v1.1 + D4 v1.1 + D5 v1.3 + D6 v1.1 ADRs available | All 11 ADR files present at project KB |
| 5 | OD selections recorded (session 1) | Session 1 entry tappable menu (§1.1) or `Proceed with defaults` invocation |
| 6 | `spec-writer` SKILL.md available | Skill at `/mnt/skills/user/spec-writer/SKILL.md`; activated in Stage-3 final-specification mode per skill description |

If any precondition fails at session 1 open, spec-writer halts and surfaces the gap before authoring begins.

---

## 6. Authoring-scope substrate

The specification absorbs `PRD_v1.0.md` 31 requirements + 11 ADRs + ADD v1.2 + Persona Document into specification-grade contracts per Workflow §2.5 Activity field.

### 6.1 Per-axis spec contract scope

Per OD-5-1.A, each axis specification commits per-axis specification-grade contracts:

| Axis spec | Contract scope (specification-grade material) | Citation discipline |
|---|---|---|
| Information substrate | State-ledger entry shape (six-field schema with field types + canonicalization library binding); JSONL event ledger format; canonical filesystem paths; shadow-Git checkpoint cadence contract; worktree-isolation read-coordination contract | Cite ADR-F2 v1.2 §Decision + §Rationale (a.1) verbatim; add field-type precision + canonicalization library candidate per §Consequences (c); cite PRD R-IS-01 through R-IS-04 by ID |
| Action surface | Sandbox tier composition formula (`max()` over `minimum_tier` × context floor × operator floor); seven-value `sandbox.fail.class` enum; `fetch_secret(name, scope) -> SecretRef` signature with `SecretRef` shape; structure-not-content `outputs_hash` formula; 12-cell sandbox provider matrix per cell; D3 9-primitive adoption depth per cell | Cite ADR-F4 v1.1 §Decision + §Consequences (a); ADR-F5 v1.1 §Decision; ADR-D2 v1.1 §1.5 + §1.7 + §1.7.1 + §1.8; ADR-D3 v1.1 §1.8 + §1.8.1; cite PRD R-AS-01 through R-AS-07 by ID |
| Control plane | F1 capability-introspection API surface + per-layer time-budget contract; F3 capability-floor lifecycle event schema (eight event classes); D1 five-element engine-class taxonomy with per-cell mapping; D4 six-pattern topology + sub-agent privilege inheritance contract; D5 four-response palette + synchrony matrix + audit ledger cryptographic shape per persona tier | Cite ADR-F1 v1.2 §Decision; ADR-F3 v1.1 §Decision floor (iv); ADR-D1 v1.1 §1.1 + §1.2; ADR-D4 v1.1 §1.1 + §1.2 + §1.5; ADR-D5 v1.3 §1.1 + §1.2 + §1.3 + §1.4 + §1.4.1 + §1.8; cite PRD R-CP-01 through R-CP-12 by ID |
| Operational discipline | D6 9-cell observability matrix per cell; unified span schema with 15 specialization-layer namespaces; sampling discipline with always-sampled exception set; redaction discipline per persona tier; cost-attribution-per-span formula; operator-burden eval primitive set; local-first OTLP collector contract | Cite ADR-D6 v1.1 §1.1 through §1.9; ADR-D5 v1.3 §1.4.1 (audit.* namespace source); ADR-D2 v1.1 §1.7.1 (sandbox.* namespace source); ADR-D3 v1.1 §1.8.1 (six namespaces source); F3 v1.1 §Decision floor (iv) (lifecycle events source); cite PRD R-OD-01 through R-OD-08 by ID |

### 6.2 Cross-axis composition document scope (session 5 optional)

| Cross-axis element | Specification-grade composition | Citation discipline |
|---|---|---|
| T-perm-1 5-axis multiplicative tunable (gate-level × MCP-trust × persona × blast-radius × sandbox-tier) | Full tunable parameter formula with per-axis monotonicity rules; cross-deployment monotonicity contract | Cite ADD §5.2.1 + ADR-D5 v1.3 §1.5 + ADR-D2 v1.1 §1.5; cite per-axis specs by section |
| T-perm-2 multi-seam engagement (F2 state-ledger + F5 sandbox seam + D3/D5/D6 D-layer seams) | Per-seam composition contract with explicit read/write boundaries | Cite ADD §5.2.2 + per-axis specs by section |
| T-perm-3 D1/D4 composition | Composition contract for engine-class × topology-pattern Cartesian product | Cite ADD §5.2.3 + ADR-D1 v1.1 §1.3 + ADR-D4 v1.1 §1.6; cite per-axis specs by section |
| Bridging-arc traversal invariants (8 in-scope transitions per IVR §5.1) | Per-transition invariance contract: span schema, sampling, redaction, trace storage, gate-level monotonicity | Cite ADD §5.3.1; cite operational-discipline spec by section |
| Sub-agent boundary monotonic-only descent | Composition contract preserving gate-level, sandbox-tier, persona-tier monotonicity at sub-agent dispatch | Cite ADD §5.3.2 + control-plane spec + action-surface spec by section |
| Deterministic-outer-harness boundary | Composition contract: every reliability property lives in deterministic layer (cross-axis composition mapping) | Cite ADD §5.3.3; cite per-axis specs by section |

### 6.3 PRD-to-spec mapping discipline

Per the `prd-author` SKILL.md §2 inversion discipline analog at Phase 5:

- **Every spec contract traces to ≥1 PRD requirement** by ID. Spec contracts that do not satisfy any PRD requirement either (a) reflect a gap in the PRD that should back-flow to Phase 4 revision pass per Workflow §4.1.2, or (b) are out of Phase 5 scope.
- **Every PRD requirement is satisfied by ≥1 spec contract** at Phase 5 close per Workflow §2.5.1 exit criteria. The traceability matrix at the spec composition document tracks this.
- **Every ADR commitment is honored** by the specification per Workflow §2.5.1 exit criteria. Contracts that deviate from ADR commitments fail the spec coherence pass and either back-flow to Phase 3 revision or are rewritten.

### 6.4 Substrate-read posture per session

Each Phase 5 session reads at session entry: (i) `PRD_v1.0.md` for the in-scope axis requirements; (ii) the relevant ADRs at section granularity; (iii) the ADD §2.x / §3.x.y for the in-scope axis synthesis paragraphs; (iv) Persona Document anchors cited at the PRD requirements; (v) any prior-session-filed spec documents for cross-axis composition reference. Substrate read is operationalized via `project_knowledge_search` against named sections (continuation of Phase 4 substrate-read posture).

---

## 7. Exit criteria

Phase 5 exits at P5-CK clearance per Workflow §2.5.1. Two-stage exit:

### 7.1 Stage 1 — Phase 5 specification authoring close

| Criterion | Verification |
|---|---|
| All authored specification documents filed | Per-axis spec files (4-5 docs) + top-level composition document (optional) present at `/mnt/user-data/outputs/` and moved to `/mnt/project/` |
| Every PRD requirement satisfied by ≥1 specification element | Spec coherence pass produces full PRD-requirement → spec-element matrix; no orphan PRD requirements per Workflow §2.5.1 exit criteria |
| Every ADR commitment honored | Spec coherence pass verifies no contradiction with any ADR commitment per Workflow §2.5.1 exit criteria |
| Phase 5 §[carry-forwards] documented | F2-12 + Workflow §7 substrate-skill propagation carried forward from PRD; any new Phase 5 carry-forwards added |

### 7.2 Stage 2 — P5-CK adversarial review clearance

Per Workflow §2.5.1:

| Criterion | Verification |
|---|---|
| Adversarial_Review_5.md filed | Output present at `/mnt/user-data/outputs/` and moved to `/mnt/project/` |
| All Class-3 findings resolved | Per Workflow §2.5.1 exit criteria; severe defects require spec revision pass at affected sections |
| Ambiguities resolved or explicitly deferred to implementation discretion | Per Workflow §2.5.1 exit criteria; deferred ambiguities are documented as Phase 6 carry-forwards |

P5-CK CLEARED → Phase 6 entry-gate AUTHORIZED per Workflow §2.6.

---

## 8. Entry preconditions and activation flow

### 8.1 Entry preconditions (verified at session 1 §4)

1. `PRD_v1.0.md` filed and coherence-pass-passed (§5 criterion 1)
2. ADD v1.2 ratified and P3-CK-cleared (§5 criterion 2)
3. `Persona_Document_v1.md` available (§5 criterion 3)
4. F1–F5 + D1–D6 ADRs available at versions matching PRD substrate set (§5 criterion 4)
5. OD selections recorded for session 1 (§5 criterion 5)
6. `spec-writer` SKILL.md available (§5 criterion 6)

### 8.2 Phase 6 entry-gate readiness (forward-looking)

Phase 6 (atomic implementation plan) opens against the cleared specification per Workflow §2.6. Phase 6 entry-gate items:

| Phase 6 entry-gate item | Source |
|---|---|
| Specification filed and P5-CK-cleared | Phase 5 exit (§7) |
| ADD v1.2 ratified | Carry-forward |
| PRD v1.0 filed | Carry-forward |
| Implementation planner skill built | Per Workflow §2.6 skill build sequence (built after Phase 5 close, JIT for Phase 6) |
| Phase 6 ADR substrate (F1–F5 + D1–D6 + any Phase 5 spec revisions) available | Persistent substrate |

Phase 6 entry handoff + session prompt authored at Phase 5 close or at Phase 6 entry per operator routing decision.

---

*Filed 2026-05-13 at Phase 4 close → Phase 5 entry boundary. Phase 5 specification authoring entry-gate AUTHORIZED per `PRD_v1.0.md` filing with coherence pass ✅ PASS. Defaults: OD-5-1.A (per-axis multi-document) + OD-5-2.A (spec-writer judgment, session-1 recommendation: Information Substrate) + OD-5-3.A (council-voice as-needed escalation) + OD-5-4.A (aggregate P5-CK review). Arc shape: 4–6 sessions per Workflow §2.5 + 1 P5-CK session per §2.5.1. Exit target: full specification filed; every PRD requirement satisfied; every ADR commitment honored; P5-CK CLEARED.*
