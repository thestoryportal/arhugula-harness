# Phase 4 PRD Authoring Entry Handoff

## Status block

| Field | Value |
|---|---|
| Artifact | `Phase_4_Entry_Handoff.md` |
| Status | **Active** — governs Phase 4 PRD authoring entry at fresh context |
| Date | 2026-05-12 |
| Phase | 4 — PRD authoring per `Project_Workflow_v1_2.md` §0; initial authoring mode per `prd-author` SKILL.md §1 |
| Skill | `prd-author` per SKILL.md §"Initial authoring mode" |
| Source-set | ADD v1.2 at `/mnt/project/Architectural_Design_Document_v1.md` (authoritative pre-PRD substrate) + `Persona_Document_v1.md` (persona-linkage trace target) + `Adversarial_Review_3_iter3.md` (P3-CK clearance evidence) + F1–F5 + D1–D6 ADRs at `/mnt/project/` (ADR section-citation substrate) + `Project_Workflow_v1_2.md` §0 (Phase 4 declaration) + `Project_Workflow_Revision_log.md` v1.4 entry (clause iv inheritance) + `harness-adversarial-reviewer` SKILL.md (P5-CK forward routing context only; not active at Phase 4) |
| Entry authorization | `Adversarial_Review_3_iter3.md` §7.1 disposition §4.1.1 CLEARANCE + P3-CK CLOSED routing per §7.2 |
| Exit gate | `PRD_v1.0.md` filed at `/mnt/user-data/outputs/` with coherence pass passed per `prd-author` SKILL.md §5.6 — no formal P4-CK declared in Workflow v1.4 per `prd-author` SKILL.md §7 |

---

## 1. Operator pre-decisions (ODs)

Three ODs govern Phase 4 entry. The PRD shape OD (OD-4-1) is substantive per `prd-author` SKILL.md §6 ("the skill discovers the PRD shape from the ADD's structure rather than imposing a canonical shape"). The remaining two ODs are operational and discipline-level. Default-vector activation is recommended unless the operator has a substantive reason to deviate.

### 1.1 OD menu (presented at session entry via `ask_user_input_v0`)

| OD | Question | Options | Default | Rationale |
|---|---|---|---|---|
| OD-4-1 | PRD shape | A: Axis-led (5 sections mirroring ADD §2/§3 axis groupings — control plane / information substrate / action surface / operational discipline / deployment surface) · B: Workload-class-led (4 sections mirroring persona §8.x — software engineering / content creation / pipeline automation / research-analysis) · C: Observer-led (3 sections per `prd-author` SKILL.md §3 — design-time operator / production-time operator / downstream maintainer) | **A** | ADD v1.2 is axis-structured per `add-consolidation-protocol.md` §3.2; §2 enumerates F-ADRs by axis; §3 groups D-ADRs by primary axis. Axis-led PRD shape preserves ADD-to-PRD section homology; minimizes traceability-matrix complexity (rows ≈ ADRs, columns ≈ PRD axis sections). Workload-class-led is defensible — persona enumerates four workload classes as first-class organizing dimensions — but introduces cross-axis fragmentation (D4's per-workload-class topology commitments distribute across all four classes; D6's 9-cell matrix distributes across deployment surfaces × persona tiers rather than workload classes). Observer-led is defensible when tensions dominate but produces less direct ADR-to-section mapping. Per `prd-author` SKILL.md §6 explicit guidance, default to axis-led when ADD is axis-structured. |
| OD-4-2 | Segmentation plan | A: Spec-writer judgment at execution time (default; segments declared at session as content volume becomes clear) · B: Operator-declared segmentation at entry (operator pre-commits to N-segment delivery with named boundaries) | **A** | Initial PRD authoring against 11 ADRs across five axes is substantial (target: 25–40 requirements at PRD grade); content volume per axis varies (control plane is dense; deployment surface is light). Spec-writer judgment at execution permits content-volume-adaptive segmentation. Operator-declared segmentation is appropriate only when prior precedent grounds the segment-count estimate; no precedent exists for PRD-initial-authoring in this project. |
| OD-4-3 | PRD §[carry-forwards] meta-section posture | A: Include §[carry-forwards] section documenting F2-12 + Workflow §7 substrate-skill propagation as deferred-acknowledged (consistent with ADD v1.2 §6.3.1 + Adversarial_Review_3_iter3 §7.3 carry-forward table) · B: Omit §[carry-forwards]; PRD scope strict to requirements with full ADR backing | **A** | ADD v1.2 §6.3.1 documents F2-12 as deferred-acknowledged with completion forecast per OD-3.A (Phase 3d precedent). The PRD inherits ADD scope; symmetric documentation of carry-forwards at PRD layer preserves operator-visibility of known gaps without introducing PRD requirements lacking ADR backing (which would violate `prd-author` SKILL.md §2 inversion discipline). Option B treats carry-forward acknowledgment as out-of-PRD-scope; would shift documentation burden to operator notes external to the PRD artifact. |

### 1.2 Default vector activation

Operator may invoke `Proceed with defaults` to apply OD-4-1.A + OD-4-2.A + OD-4-3.A in a single step. Author proceeds without re-narrating context per established protocol.

### 1.3 ODs explicitly NOT at the menu

Two candidate ODs were considered and rejected from the menu as non-decisions per skill discipline:

| Rejected OD | Reason for rejection |
|---|---|
| Persona-linkage requirement depth (every requirement vs persona-dependent only) | Not a real choice — `prd-author` SKILL.md §9 anti-patterns explicitly names "persona-disconnect" as a load-bearing failure mode: "every requirement should cite at least one persona-document anchor." Discipline-fixed at every-requirement form. |
| Acceptance-criterion grade (observable-threshold vs capability-availability) | Not a real choice — both are PRD-grade per `prd-author` SKILL.md §4 sub-discipline (3) observable framing. Choice is per-requirement stylistic, not session-level. Author selects per-requirement based on what the ADR commits at section level. |

---

## 2. Routing matrix

Phase 4 initial authoring mode per `prd-author` SKILL.md §1. No revision-pass routing applies (no prior PRD filed).

### 2.1 Session routing shape

```
P3-CK iter-3 disposition: §4.1.1 CLEARANCE → P3-CK CLOSED
  │
  ▼
Phase 3d output ratified: ADD v1.2 at /mnt/project/
  │
  ▼
Phase 4 entry-gate AUTHORIZED (this handoff §5)
  │
  ▼
Phase 4 session opens (fresh context per §3 of session prompt)
  │
  ├─ OD menu (handoff §1) → operator selection or "Proceed with defaults"
  │
  ▼
prd-author skill execution:
  ├─ §5.1 Read ADD v1.2 in full
  ├─ §5.2 Enumerate observable surfaces per ADR (handoff §6 substrate)
  ├─ §5.3 Cluster into requirements per OD-4-1 shape
  ├─ §5.4 Author requirements per references/prd-template.md
  ├─ §5.5 Build traceability matrix
  ├─ §5.6 Coherence pass (skill §4 four sub-disciplines applied)
  └─ Pre-emission self-audit (session prompt §6)
  │
  ▼
PRD_v1.0.md filed at /mnt/user-data/outputs/
  │
  ▼
Phase 4 CLOSED (no P4-CK declared in Workflow v1.4)
  │
  ▼
Phase 5 specification authoring entry-gate AUTHORIZED
```

### 2.2 No-revision-pass invariant

Initial authoring mode produces `PRD_v1.0.md` against ADD v1.2 as the substrate. A revision pass would only activate if a subsequent ADD revision (v1.2 → v1.3) requires PRD absorption — for example, if F2-12 closure lands as D1 v1.2 + D6 v1.2 and is absorbed into an ADD v1.3, the resulting PRD revision pass would produce `PRD_v1.1.md` per `prd-author` SKILL.md §7. No such ADD revision is in scope at Phase 4 entry.

---

## 3. Session-shape sketch

Single-session multi-segment authoring expected. Segmentation declared at execution time per OD-4-2.A.

### 3.1 Anticipated segment shape (advisory only)

| Segment | Content | Estimated volume |
|---|---|---|
| Segment 1 | Front-matter (PRD shape declaration + persona summary + scope) + observable-surface inventory per ADR (11 ADRs × 1–3 surfaces each ≈ 22–33 surface entries) + PRD section structure declaration | ~150–250 lines |
| Segment 2 | PRD body per OD-4-1 shape — requirements clustered into sections; each requirement carries ID + observable-behavior statement + observer role + ADR citation(s) + persona linkage + acceptance criterion per `references/prd-template.md` | ~400–600 lines |
| Segment 3 | Traceability matrix + carry-forwards section + coherence pass results + pre-emission self-audit + filing footer | ~150–250 lines |

**Total estimate**: ~700–1100 lines for `PRD_v1.0.md`. Operator can compress or expand at execution time based on requirement density per axis.

### 3.2 Single-segment alternative

If the operator selects a strict-scope PRD (≤20 requirements, no §[carry-forwards] section per OD-4-3.B), single-segment delivery is feasible at ~400–500 lines. Default OD-4-2.A defers this decision to execution time.

---

## 4. Carry-forwards from P3-CK closure

Three carry-forward items inherited from `Adversarial_Review_3_iter3.md` §7.3 carry-forward table. Each must be addressed at Phase 4 entry per OD-4-3 disposition.

### 4.1 F2-12 (D1 v1.1 → v1.2 replay-trace-emission contract)

| Dimension | Status |
|---|---|
| Origin | ADD v1.0 §6.3.1 per OD-3.A; iter-1 disposition preserved at iter-2 + iter-3 |
| Current state | Deferred-acknowledged at ADD v1.2 §6.3.1; not blocking P3-CK closure |
| Substrate readiness | D5 v1.2 §1.4.1 + §1.4 substrate available; D1 v1.2 absorption deferred pending parallel `council-orchestrator` C7+C9 session |
| Phase 4 disposition under OD-4-3.A | PRD §[carry-forwards] documents F2-12 as deferred-acknowledged; no PRD requirement bound to replay-trace-emission semantics (would violate `prd-author` SKILL.md §2 inversion discipline since D1 commitment is not filed at v1.2) |
| Phase 4 disposition under OD-4-3.B | F2-12 not mentioned in PRD; operator tracks externally |
| Forward routing | Parallel `council-orchestrator` C7+C9 session at operator discretion; ADD v1.3 absorption pass at PRD revision-pass entry if D1 v1.2 + D6 v1.2 land |

### 4.2 Workflow §7 substrate-skill propagation

| Dimension | Status |
|---|---|
| Origin | `Project_Workflow_Revision_log.md` v1.4 entry line 297 footnote — `add-consolidation-protocol.md` §3.5 Step 5 substrate-skill update to reference v1.4 §2.3.5 clause (iv) is a separate skill-substrate revision not in v1.4 scope |
| Current state | Open operator decision; outside P3-CK closure scope; not blocking Phase 4 entry |
| Phase 4 disposition | Not in PRD scope (skill-substrate, not architectural commitment, not observable behavior). Operator decision tracked separately; out of `prd-author` skill activation territory per skill §"Do NOT activate for" list |
| Forward routing | Operator decision; potential spec-writer Path A follow-on pass against `add-consolidation-protocol.md` skill-substrate file |

### 4.3 Pattern P2 + Pattern P3 monitoring

| Dimension | Status |
|---|---|
| Pattern P2 | ✅ CLOSED at iter-1 per `Adversarial_Review_3.md` §6.2 counter-reset zero; no further monitoring required at Phase 4 |
| Pattern P3 | ✅ RESOLVED at both halves at v1.2 filing per `Adversarial_Review_3_iter3.md` §6.2; Workflow v1.4 §2.3.5 clause (iv) prevention binding at PRD authoring per `prd-author` SKILL.md §8 cross-mode V3 deference ("Workflow v1.4 §2.3.5 clause (iv) — the synthesis-paragraph verbatim-enumeration discipline at ADD consolidation — is structurally analogous to the §4 trace-back sub-discipline here") |
| PRD-layer Pattern P3 prevention | Trace-back discipline at `prd-author` SKILL.md §4 sub-discipline (1) requires section-level ADR citation, not just ADR ID. This is the PRD-layer analog of clause (iv) — citation discipline at requirement granularity prevents the synthesis-paragraph-style enumeration drift from reaching the PRD layer |

---

## 5. Entry-gate verification criteria

Six entry-gate criteria verified at Phase 4 session entry before authoring begins.

| # | Verification | Source of evidence |
|---|---|---|
| 1 | ADD v1.2 ratified at `/mnt/project/Architectural_Design_Document_v1.md` | Status block reads `v1.0 → v1.1 → v1.2`; Filing footer at line 759 reads v1.2; `Adversarial_Review_3_iter3.md` §7.1 disposition is §4.1.1 CLEARANCE |
| 2 | P3-CK iter-3 review artifact filed | `Adversarial_Review_3_iter3.md` present at `/mnt/project/`; disposition declared at §7.1 |
| 3 | Persona Document available as trace target | `Persona_Document_v1.md` present at `/mnt/project/`; cited at ADD §1 persona summary and §2.x / §3.x.y persona linkage sub-elements |
| 4 | F1–F5 + D1–D6 ADRs available for section-citation substrate | All 11 ADR files present at `/mnt/project/`; versions match ADD v1.2 Source-set declaration (F1 v1.2, F2 v1.2, F3 v1.1, F4 v1.1, F5 v1.1, D1 v1.1, D2 v1.1, D3 v1.1, D4 v1.1, D5 v1.3, D6 v1.1) |
| 5 | OD selections recorded | Session entry tappable menu (handoff §1 / session prompt §2) or `Proceed with defaults` invocation |
| 6 | `prd-author` SKILL.md §"Initial authoring mode" discipline active | SKILL.md read at session entry; §2 inversion discipline + §3 observable-behavior framing + §4 four sub-disciplines + §5 authoring procedure all loaded; pre-emission self-audit binding active per session prompt §6 |

If any precondition fails, author halts and surfaces the gap before authoring begins.

---

## 6. Authoring-scope substrate

The PRD absorbs 11 ADRs into requirements per the inverted-design discipline. Each ADR's observable surfaces are pre-enumerated below as authoring-scope substrate. This is **not** a pre-committed requirement list — it is the substrate the author uses at `prd-author` SKILL.md §5.2 step ("Enumerate observable surfaces").

### 6.1 Five-axis ADR inventory

Per `add-consolidation-protocol.md` §3.2 five-axis decomposition mirrored at ADD §2/§3:

| ADR | Primary axis | Decision summary (per ADD §2.x / §3.x.y) |
|---|---|---|
| F1 | Control plane | Capability-aware multi-LLM provider abstraction with layered cheapest-deterministic-first routing |
| F2 | Information substrate | Filesystem + git canonical state substrate with files-as-artifacts and combined git tier |
| F3 | Control plane | Stateless-reducer / launch-pause-resume durable-execution pattern with capability-requirement floor and per-workload-class engine selection |
| F4 | Action surface | Graduated-isolation four-tier sandbox with `max()`-composed per-tool tier and tier × deployment-context tech split |
| F5 | Action surface | Tier-aware secret-fetch abstraction with OS-keyring dev-tech and structure-not-content audit composition |
| D1 | Control plane | Specific durable-execution substrate: engine-class commitment with per-deployment-surface candidate mapping |
| D2 | Action surface | Specific sandbox provider per deployment-surface × per-blast-radius-tier |
| D3 | Action surface | Anthropic-primitive adoption depth with five-tier mapping |
| D4 | Control plane | Multi-agent topology: six-pattern taxonomy with workload-class × engine-class parametric commitments |
| D5 | Control plane | HITL synchrony: four-response palette with synchrony class parametric on persona-tier × engine-class |
| D6 | Operational discipline | Observability backend: per-deployment-surface × per-persona-tier with unified span schema ingestion contract |

**Axis distribution**: Control plane (F1, F3, D1, D4, D5 = 5 ADRs); Information substrate (F2 = 1 ADR); Action surface (F4, F5, D2, D3 = 4 ADRs); Operational discipline (D6 = 1 ADR); Deployment surface (0 — empty per ADD §3 OD-2.A; deployment-surface decisions distributed across D1, D2, D3, D6 per-cell commitments).

### 6.2 Observable-surface enumeration per ADR (advisory)

Per `prd-author` SKILL.md §5.2 step. Each ADR yields one or more observable surfaces visible to one or more of the three observer roles. The author confirms or revises this inventory at session execution by reading each ADR's `Decision` and `Consequences` sections.

#### 6.2.1 Control plane ADRs

| ADR | Observable surface | Primary observer role |
|---|---|---|
| F1 | Provider selection visible at routing decision; cross-family fallback announced at fallback-trigger; cost/latency reported per provider | Production-time operator |
| F1 | Capability introspection visible at authoring-time tool/contract surface | Design-time operator |
| F3 | Workflow lifecycle events (start, step-boundary, fallback-trigger, retry-attempt, breaker-trip, lease, resumption) visible on run dashboard | Production-time operator |
| F3 | Manifest-default invocation surface visible at authoring-time workflow definition | Design-time operator |
| F3 | Per-workload-class engine selection visible at workflow definition time | Design-time operator |
| D1 | Engine class committed per deployment surface visible at deployment-binding time | Design-time operator |
| D1 | Replay semantics visible at run-resumption surface (operator perceives whether resumption replays prior steps) | Production-time operator |
| D4 | Multi-agent topology visible at workflow definition surface; fan-out / handoff / hierarchical-delegation patterns selectable | Design-time operator |
| D4 | Sub-agent privilege inheritance visible at audit ledger per-event attribution | Downstream maintainer |
| D4 | Cascade-policy default per topology pattern visible at run-time event surface | Production-time operator |
| D5 | HITL prompt with four-response palette (approve / edit / reject / respond) visible at gate-evaluation surface | Production-time operator |
| D5 | Synchrony-class per cell (immediate-block / workflow-pause) visible as HITL UX shape | Production-time operator |
| D5 | Three-placement topology primitive (pre-action gate / sub-agent boundary / validator-failure escalation) visible at workflow definition surface | Design-time operator |
| D5 | Audit ledger cryptographic shape per persona tier (append-only / hash-chained / hash-chained-plus-signature) visible at ledger inspection surface | Downstream maintainer |

#### 6.2.2 Information substrate ADRs

| ADR | Observable surface | Primary observer role |
|---|---|---|
| F2 | Files-as-artifacts visible on filesystem at canonical paths | Production-time operator + Downstream maintainer |
| F2 | Git history visible as state-transition record; combined git tier (versioning + state-ledger + JSONL event ledger + opt-in shadow-Git checkpoint + worktree-isolation) visible at git inspection surface | Downstream maintainer |
| F2 | State-ledger entry shape `(action_id, idempotency_key, actor, response_hash, timestamp, prior_event_hash)` visible at ledger inspection surface | Downstream maintainer |

#### 6.2.3 Action surface ADRs

| ADR | Observable surface | Primary observer role |
|---|---|---|
| F4 | Sandbox tier per tool invocation visible at run-time event surface; `sandbox.tier` span attribute on every sandbox-bounded tool span | Production-time operator |
| F4 | Sandbox failure-class taxonomy (`escape_attempt` / `egress_denied` / `timeout` / `oom` / `signal` / `exit_nonzero` / `policy_override`) visible at failure-event surface | Production-time operator |
| F4 | Per-tool tier assignment visible at authoring-time contract surface (`minimum_tier`) and run-time policy surface (`max()` composition with floors) | Design-time operator + Production-time operator |
| F5 | Secret fetch through tier-aware abstraction; never present in stored prompts/logs | Production-time operator (negative-observation: secret content absence in logs is the observable) |
| F5 | Secret-fetch audit visible at ledger as structure-not-content event | Downstream maintainer |
| D2 | Specific sandbox provider per deployment surface × blast-radius tier visible at deployment-binding time | Design-time operator |
| D2 | Sandbox span schema visible at observability backend (per cell) | Production-time operator + Downstream maintainer |
| D3 | Anthropic-primitive adoption depth per cell visible at deployment-binding time; six namespace declarations (`anthropic.*` / `mcp.*` / `skill.*` / `managed_agents.*` / `files.*` / `memory.*`) visible at span attribute surface | Design-time operator + Production-time operator |

#### 6.2.4 Operational discipline ADRs

| ADR | Observable surface | Primary observer role |
|---|---|---|
| D6 | 9-cell deployment-surface × persona-tier matrix visible at deployment-binding time | Design-time operator |
| D6 | 15 specialization-layer span attribute namespaces visible at observability backend ingestion | Production-time operator + Downstream maintainer |
| D6 | Sampling discipline (head-based-dev / tail-based-prod with per-event-class always-sampled exceptions) visible at backend trace-coverage surface | Production-time operator |
| D6 | Redaction discipline per persona tier visible at content-attribute capture surface | Production-time operator + Downstream maintainer |
| D6 | Cost-attribution-per-span dashboarding visible at run cost-attribution surface | Production-time operator |
| D6 | Operator-burden eval primitive (expected HITL invocations per session) visible at per-cell dashboard surface | Production-time operator |

### 6.3 Cross-axis emergent properties

Three permanent tensions (T-perm-1, T-perm-2, T-perm-3) and four cross-axis emergent properties per ADD §5.1 + §5.3. Each warrants either a dedicated PRD section (cross-axis-property requirements) or per-axis distributed requirements with explicit cross-reference:

| Cross-axis property | ADD reference | PRD authoring guidance |
|---|---|---|
| T-perm-1 5-axis multiplicative tunable (gate-level × MCP-trust × persona × blast-radius × sandbox-tier) | ADD §5.2.1 | Observable at gate-evaluation surface; per-axis tunable visible at authoring-time + run-time policy surfaces |
| T-perm-2 multi-seam engagement (F2 state-ledger + F5 sandbox seam + D3/D5/D6 D-layer seams) | ADD §5.2.2 | Observable at JSONL ledger surface (write contract) and selective-read surface (within-turn context curation) |
| T-perm-3 D1-layer engine-class commitment + D4-layer multiplicative `workload_class × topology_pattern` specialization | ADD §5.2.3 | Observable at workflow definition surface (engine class per deployment) + topology pattern per workload class |
| Replay-determinism semantics across durable boundary (C1+C3+C7+C11 engagement) | ADD §5.3 | Observable at run-resumption surface; per-event-class replay-determinism visible at audit ledger |
| Per-cell observability composition (D6 backend × persona tier × deployment surface) | ADD §5.3 | Observable at per-cell dashboard surface |
| Compliance-readiness primitive (audit ledger hash-chain + cryptographic signature per persona tier) | ADD §5.3 | Observable at audit-ledger inspection surface; persona-tier-conditional cryptographic shape |
| Cost attribution as architectural primitive (per-span cost dashboarding) | ADD §5.3 | Observable at run cost-attribution surface |

### 6.4 Persona linkage substrate

Per `prd-author` SKILL.md §9 anti-pattern (persona-disconnect): every PRD requirement cites at least one `Persona_Document_v1.md` anchor. Common anchors per ADD §C.3 inventory:

| Persona section | Anchor content |
|---|---|
| §1 | Operator role + bridging arc |
| §2 | Bridging-arc constraint (design-time → production-time transition) |
| §3.1 | Primary task classes (heterogeneous workflow shape commitment) |
| §4 | Scale + 99.9% completion SLO |
| §5 | Integration surface (code execution + computer-use + MCP first-class) |
| §5.1 | Computer-use at production-time with stronger sandbox tier |
| §6 | Per-class cost ceiling |
| §7 | Pragmatic-mixed ecosystem affinity |
| §8.1–8.4 | Four workload classes (software engineering / content creation / pipeline automation / research-analysis) |
| §9 | Deployment-surface implications |
| §10.1–10.4 | Foundational primitives (F4 graduated-isolation; cost-attribution-per-span; HITL selectivity; compliance-readiness) |
| §11 | Cross-cutting persona constraints |

---

## 7. Exit criteria

No formal P4-CK declared in Workflow v1.4 per `prd-author` SKILL.md §7 ("The current workflow does not declare a P4-CK; if a future workflow revision introduces one, defer to that revision's clearance criteria"). Phase 4 exits when the PRD is filed and the coherence pass passes.

### 7.1 PRD coherence pass criteria

Per `prd-author` SKILL.md §5.6 coherence pass. Every requirement satisfies all four sub-disciplines:

| Sub-discipline | Verification |
|---|---|
| (1) Trace-back | Cites ≥1 ADR by ID **and section**; section-level citation mandatory per skill §4 |
| (2) Non-contradiction | Does not contradict any commitment in ADD v1.2 |
| (3) Observable framing | States observer-perceptible behavior (WHAT), not implementation mechanism (HOW) |
| (4) No-architecture-introduction | Does not add architectural commitment beyond ADD v1.2 |

A requirement that fails any sub-discipline is not a partial requirement; it is the wrong artifact per skill §4 explicit guidance — re-author or surface as finding.

### 7.2 Traceability matrix completeness

Per `prd-author` SKILL.md §5.5. Rows = 11 ADRs; columns = N PRD sections (N determined by OD-4-1 shape).

| Completeness criterion | Verification |
|---|---|
| Every ADR row has ≥1 column mark | No orphan ADR (ADR-without-PRD-requirement) |
| Every PRD section column has ≥1 row mark | No orphan PRD section (PRD-section-without-ADR-backing) |
| Cross-axis emergent properties have explicit cross-row marks | Per ADD §5 cross-axis integration; matrix surfaces multi-ADR composition |

Missing marks are findings per skill §5.5.

### 7.3 PRD front-matter declarations

Per `prd-author` SKILL.md §6 + skill §10 references. The PRD front-matter declares:

| Declaration | Source of value |
|---|---|
| PRD shape (axis-led / workload-class-led / observer-led) | OD-4-1 selection at session entry |
| ADD substrate reference | ADD v1.2 at `/mnt/project/Architectural_Design_Document_v1.md` |
| Persona substrate reference | `Persona_Document_v1.md` at `/mnt/project/` |
| ADR substrate set | F1 v1.2 + F2 v1.2 + F3 v1.1 + F4 v1.1 + F5 v1.1 + D1 v1.1 + D2 v1.1 + D3 v1.1 + D4 v1.1 + D5 v1.3 + D6 v1.1 (per ADD v1.2 Source-set) |
| Status posture | `Status: Proposed` per `prd-author` SKILL.md §7 (no checkpoint to promote against; preserved through Phase 4 close) |

### 7.4 Status posture at filing

Per `prd-author` SKILL.md §7. `Status: Proposed` preserved through filing — no P4-CK to clear against. Promotion to `Accepted` deferred to a future workflow revision that declares P4-CK or equivalent gate.

---

## 8. Entry preconditions and activation flow

### 8.1 Entry preconditions (verified at §5)

1. ADD v1.2 ratified at `/mnt/project/` (§5 criterion 1)
2. Adversarial_Review_3_iter3.md filed (§5 criterion 2)
3. Persona_Document_v1.md available (§5 criterion 3)
4. F1–F5 + D1–D6 ADRs available at versions matching ADD Source-set (§5 criterion 4)
5. OD selections recorded (§5 criterion 5)
6. `prd-author` SKILL.md §"Initial authoring mode" discipline active (§5 criterion 6)

### 8.2 Phase 5 entry-gate readiness (forward-looking)

Phase 5 specification authoring opens against `PRD_v1.0.md` as substrate, with ADD v1.2 + 11 ADRs as deeper substrate. The Phase 5 entry-gate is bounded by:

| Phase 5 entry-gate item | Source |
|---|---|
| `PRD_v1.0.md` filed and coherence-pass-passed | Phase 4 exit (§7) |
| ADD v1.2 ratified and P3-CK-cleared | Carry-forward from P3-CK closure |
| Persona Document available | Persistent substrate |
| Phase 5 ADR substrate (F1–F5 + D1–D6) available | Persistent substrate |
| P5-CK adversarial review scope declared | Phase 5 session prompt authoring (subsequent) |

Phase 5 session prompt + entry handoff are authored at Phase 4 close or at Phase 5 entry per operator routing decision.

---

*Filed 2026-05-12 at P3-CK iter-3 close → Phase 4 entry boundary. Phase 4 initial PRD authoring entry-gate AUTHORIZED per Adversarial_Review_3_iter3.md §7.1 disposition §4.1.1 CLEARANCE. Defaults: OD-4-1.A axis-led / OD-4-2.A spec-writer-judgment segmentation / OD-4-3.A include §[carry-forwards] meta-section. Exit target: PRD_v1.0.md filed with coherence pass passed; no formal P4-CK in Workflow v1.4; Phase 5 entry-gate AUTHORIZED on PRD filing.*
