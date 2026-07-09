# Project Roadmap v1

*Workspace-root roadmap delivering deterministic next-action derivation. Loaded at every session start via CLAUDE.md §12. Refreshed via `.harness/roadmap_status.md` dashboard.*

---

## 0. Change note + scope

**What this is.** A machine-readable (by Claude) roadmap that lets a fresh session pick its next action from a structured queue without operator AskUserQuestion. Per-action discipline encoding (skill, posture, advisor/council requirements, verification shape, close shape) means future-Claude knows not only *what* to do but *how* to do it correctly.

**What this is not.** A planning narrative. A status report. A re-synthesis of design substrate. A commitment device against execution drift (workspaces drift; this doc detects + handles drift, doesn't prevent it).

**Locus rationale.** Workspace root, not `design-substrate/`. Roadmaps are *process-substrate* — refreshing them at every PR merge is the design. Placing them under `design-substrate/` would trap each refresh behind X-AL-3 guard + design-phase posture + clearance marker = same failure mode as the checkpoint convention (advisory drift). Process-substrate lives at workspace root or `.harness/`; design-substrate lives at `design-substrate/`.

**Why this exists.** Operator directive 2026-05-31: *"I no longer ask whats next. After each chunk of work Claude knows with certainty which next work to proceed to and what disciplines are to be applied and executed for each."* The roadmap delivers this; partial delivery (no derivation rule, or no discipline encoding, or no drift detection) is failure.

**Success criterion.** Close a session. Open a fresh one tomorrow. Read only `CLAUDE.md` + this roadmap + `.harness/roadmap_status.md`. Point at a specific R-NNN and execute without asking the operator. If you catch yourself wanting to AUQ "should I do X or Y" — the discipline encoding or derivation rule is not sharp enough; iterate this doc before continuing execution.

**Versioning.** v1 = scaffolding (this PR). Per-workstream atomic decomposition for §IV–§IX is incremental (future PRs). Workflow v1.14 amendment cataloguing roadmap-driven discipline is a sibling arc.

---

## 1. Surface synthesis (compressed)

Ten surfaces of remaining work between current state and Phase 7 closure + Phase 8 graduation. Each surface gets an R-NNN ID block in §5.

| § | Surface | R-NNN block | One-line scope |
|---|---|---|---|
| I | Phase 7 axis-clean | R-001..R-099 | Atomic-unit landings + substitution retirement until §1.3 closure criterion met |
| II | MVP-operator-usable | R-100..R-199 | `harness run` exercises a real workflow at SOLO_DEVELOPER tier against ≥1 LLM provider with audit-ledger emission |
| III | CI substrate | R-200..R-299 | GitHub Actions for pytest + pyright + ruff + workspace-wide test matrix; X-AL-3 guard already landed |
| IV | Multi-LLM maturity | R-300..R-399 | Provider capability discovery; capability-aware abstraction exercise; mixed-provider workflow |
| V | Multi-deployment surfaces | R-400..R-499 | LOCAL_DEVELOPMENT → SELF_HOSTED_SERVER → MANAGED_CLOUD; sandbox tier wiring per ADR-D2 / ADR-F4 |
| VI | Multi-tenant | R-500..R-599 | `RuntimeConfig.tenant_id` non-default deployments; `persona_tier` non-SOLO_DEVELOPER deployments; redaction policy per §C-OD-13 §13.1 |
| VII | Process discipline | R-600..R-699 | Workflow doc evolution; species/sub-species catalogue; pattern bake-in; clearance marker maturity |
| VIII | Phase 8 retirement criteria | R-700..R-799 | All 49 substitutions either RETIRED or RETIRED-AS-BOUNDED-RESIDUAL with documented rationale per X-AL-2 |
| IX | External integrations | R-800..R-899 | Real external MCP servers; managed_agents primitive (closed by R-820); Files API (deferred per AS-8e) |
| X | Existential / research | R-900..R-999 | Open architectural questions; speculative arcs; research-corpus extensions |
| XI | Operator tooling / observability | R-XI-NN | Human-facing dashboards, status pages, CI-deployed observability surfaces; NOT for Claude consumption (Claude reads `.harness/roadmap_status.md` directly) |

**Decomposition status:** §I + §II + §III + §V + §VII + §XI have R-NNN actions populated at §5. §IV + §VI + §VIII–§X are named with decomposition-owed markers per §9.

---

## 2. Sequencing rationale + dependency graph

**Multipliers (do first, unlock more):**

1. **CI substrate (§III)** — lifts the cadence ceiling. Without CI, every PR merge depends on local-test discipline; with CI, parallel branches + pre-merge validation = ~2-3× cadence on the no-shared-state arcs.
2. **MVP-operator-usable (§II)** — unlocks every X-AL-2 second-conjunct closure that requires real workflow execution. AS-8d + OD-5 + future RETIRE-READY transits gate on MVP. Without MVP, the RETIRE-READY bucket grows indefinitely.
3. **Multi-deployment surfaces (§V)** — gates ~40-60% of remaining substitution retirements (tier-conditional emission, multi-tenant redaction, sandbox tier 2+3). LOCAL_DEVELOPMENT-only deployments cannot exercise the full substitution-retirement gradient.

**Dependency graph (high-level):**

```
§III CI substrate ────┬─────────────► §II MVP-usable ──┬──► §V multi-deployment ──┬──► §VI multi-tenant
                      │                                │                          │
                      └─► §I axis-clean ──► §VIII Phase 8 retirement              │
                                                                                  ▼
                                                                          §VII process maturity
                                                                          (parallel arc; not gating)

§IV multi-LLM ──┐
§IX external ───┤── all gate on §II MVP-usable
                ┘
§X existential — research, no execution dependency

§XI operator tooling — gates on §III CI substrate (auto-regenerate);
                       parallel arc after §III opens
```

**Hard dependencies (must respect):**

- Any RETIRED transit gated on X-AL-2 second conjunct (substituted H_E surface no longer invoked) requires §II MVP-usable.
- Any tier-conditional retirement (OD sampler envelope; OD redaction; sandbox tier 2+3) requires §V multi-deployment.
- Any cross-provider capability discovery requires §IV multi-LLM.
- Phase 8 closure (§VIII) requires all 49 substitutions accounted for.

**Soft dependencies (cross-cutting but not strictly blocking):**

- Process discipline maturity (§VII) compounds at every arc — defer indefinitely and the workflow doc accumulates uncatalogued patterns.
- CI substrate (§III) enables faster execution of every other surface but is not strictly blocking.

---

## 3. Discipline-encoding schema (the load-bearing section)

Every R-NNN entry uses this schema. **Read this section once, then read §5 entries pattern-matched against it.**

```yaml
R-NNN:
  title: <one-line scope>
  surface: <§I..§X>
  status: <PROPOSED|ACTIVE|BLOCKED|RESOLVED|DEFERRED|CANCELLED>
  depends_on: [R-NNN, ...]    # all must be RESOLVED before this can be ACTIVE
  blocks: [R-NNN, ...]        # this must be RESOLVED before these can be ACTIVE
  posture: <design-phase|phase-7|mode-agnostic|halt-route-to-operator>
  scope:
    files: [path glob, ...]   # what gets edited
    contracts: [C-XX-NN, ...] # which contracts touched (empty if none)
    cross_axis: <yes|no>      # crosses an axis boundary?
  skills:
    primary: <skill-name|null>
    secondary: [skill-name, ...]
  advisor_required: <yes|no|conditional:reason|satisfied:YYYY-MM-DD>
  council_required: <yes|no|conditional:nameable-tension>
  verification:
    shape: <e2e|integration|unit|grep|none>
    must_pass: [<assertion description>, ...]
  close_shape:
    type: <PR-merge|fork-doc-filing|retirement-event|substrate-amendment|clearance-marker>
    artifact: <expected output path or PR title pattern>
    cascade: [<downstream R-NNN to refresh>, ...]
  next_pointer: <R-NNN or null>   # if this is RESOLVED, next likely action
  resume: <.harness/<R-NNN>-checkpoint.md>   # OPTIONAL; present ONLY when paused mid-execution (status stays ACTIVE). Pointer to the orientation checkpoint a fresh session reads before resuming.
  notes: <free text, ≤3 lines>
```

**Field semantics:**

- **status** — PROPOSED = not yet authorized; ACTIVE = can be executed now; BLOCKED = unmet hard dependency; RESOLVED = PR merged or equivalent closure; DEFERRED = operator-decision to park; CANCELLED = scope removed (with rationale at notes). The enum is **closed** — there is no in-progress value. An entry **paused mid-execution** (orientation done, work not finished) stays `ACTIVE` (resuming *is* executing) and carries a `resume:` pointer; the presence of `resume:` is the paused-and-oriented signal.
- **depends_on** vs **blocks** — depends_on is what must close before this opens; blocks is what this opens once closed (inverse view; both populated for fast traversal both directions).
- **posture** — `design-phase` = edits `design-substrate/**`; `phase-7` = edits `harness-*/src/**`; `mode-agnostic` = workspace-operational (root, `.github/`, `.claude/`, this roadmap, status dashboard); `halt-route-to-operator` = requires operator AUQ before execution.
- **skills.primary** — invoke this first. **skills.secondary** — invoke during execution as triggered.
- **advisor_required** — `yes` = call `advisor()` before substantive work; `conditional:<reason>` = call advisor() if condition holds; `satisfied:<YYYY-MM-DD>` = a `yes` entry whose advisor consultation already happened on that date and resolved the cross-axis blocker — re-run advisor only if a NEW cross-axis question surfaces. Used on a paused entry (with `resume:`) so a fresh session does not redundantly re-consult.
- **council_required** — `yes` = open council per `.claude/skills/council/council-orchestrator/`; `conditional:nameable-tension` = open council only if a tension between two voices can be named in advance (per workspace CLAUDE.md §10.9 amendment 1).
- **verification.shape** — `e2e` = real workflow execution; `integration` = cross-module test; `unit` = single-module test; `grep` = static verification; `none` = doc-only or process-only.
- **close_shape.cascade** — downstream R-NNN entries that should be refreshed (status check, next_pointer recompute) upon close.
- **next_pointer** — best-guess at next action upon close; the derivation rule (§4) may override if dependencies / postures changed.
- **resume** — OPTIONAL; set ONLY when an entry is paused mid-execution. Points at a `.harness/<R-NNN>-checkpoint.md` artifact carrying the orientation a fresh session needs to resume without re-deriving (resolved decisions, operator ratifications, injection-point maps, sub-cluster plan). When present, `status` stays `ACTIVE` and the dashboard Next-action shows the resume instruction. Removed when the entry RESOLVES.

**When the schema is silent.** If a field cannot be populated without orientation (e.g., dependencies on not-yet-authored substrate), set the field to `TBD:<one-line-reason>` and route to operator at execution time. Do NOT silently default to "no" or "none" — silent defaults are the failure mode.

**When you pause mid-execution (checkpoint-on-pause rule).** If a substantive entry (especially `phase-7` / multi-PR) is paused after orientation but before completion — advisor + scope-ratification done, implementation not started — make the stop seamless across a session `/clear`: (1) write `.harness/<R-NNN>-checkpoint.md` capturing the resolved decisions + a "read this FIRST; do not re-derive" instruction; (2) set the entry's `resume:` field to that path and keep `status: ACTIVE` (downgrade `advisor_required: yes` → `satisfied:<date>` if the advisor pass is banked); (3) put an explicit "➡️ ON RESUME: …" instruction + checkpoint pointer in the dashboard Next-action. A fresh session then resumes via `/clear` → SessionStart hook (`next=R-NNN`) → `continue` → checkpoint → execution, with zero re-derivation. Remove `resume:` and the checkpoint pointer when the entry RESOLVES.

---

## 4. Next-action derivation rule

**Executed by Claude at session start (per CLAUDE.md §12) and after every PR merge.**

```
def next_action(roadmap, workspace_state, session_posture):
    """
    Returns the R-NNN to execute next, or None if blocked / awaiting operator.

    workspace_state: dict computed from git HEAD + open PRs + open fork docs +
                     last-retirement-batch-count + RETIRED-count + CLAUDE.md row-set hash.
    session_posture: 'design-phase' | 'phase-7' | 'mode-agnostic' | None.
                     If None, derive from edit-scope intent or AUQ operator.
    """

    # 1. Refresh status dashboard against workspace_state.
    #    If hash mismatch with .harness/roadmap_status.md → HALT (drift detected).
    if hash(workspace_state) != roadmap_status.workspace_state_hash:
        return HALT("DRIFT_DETECTED",
                    diff=workspace_state_diff(workspace_state, dashboard))

    # 2. Build candidate queue:
    #    - status == ACTIVE
    #    - all depends_on in RESOLVED
    #    - no operator-halt-marker
    #    - posture matches session_posture (or session_posture is None and
    #      we let the candidate's posture drive the AUQ)
    candidates = [
        r for r in roadmap.actions
        if r.status == 'ACTIVE'
        and all(roadmap[d].status == 'RESOLVED' for d in r.depends_on)
        and not r.operator_halt_marker
        and (session_posture is None or r.posture == session_posture
             or r.posture == 'mode-agnostic')
    ]

    # 3. If empty, look for BLOCKED actions whose blockers just RESOLVED;
    #    flip those to ACTIVE and retry step 2.
    if not candidates:
        flipped = [r for r in roadmap.actions
                   if r.status == 'BLOCKED'
                   and all(roadmap[d].status == 'RESOLVED' for d in r.depends_on)]
        if flipped:
            for r in flipped: r.status = 'ACTIVE'
            return next_action(roadmap, workspace_state, session_posture)

    # 4. If still empty, surface to operator.
    if not candidates:
        return HALT("NO_ACTIVE_CANDIDATES", queue_size=len(roadmap.actions))

    # 5. Apply priority order (lower R-NNN first within surface;
    #    surface order = blockers-first per §2 dependency graph).
    candidates.sort(key=lambda r: (surface_priority(r.surface), r.id))

    # 6. Return top.
    return candidates[0]
```

**Priority order (surface_priority):**

1. `mode-agnostic` infrastructure (R-IF-NNN in-flight tracking; refresh-roadmap actions)
2. `§I axis-clean` — close substitutions whose dependencies are met
3. `§III CI substrate` — multiplier
4. `§II MVP-operator-usable` — multiplier
5. `§VII process discipline` — parallel arc
6. `§V multi-deployment` → `§VI multi-tenant` → `§IV multi-LLM` → `§IX external`
7. `§XI operator tooling` — parallel arc; opens after §III CI substrate baseline
8. `§VIII Phase 8` (only when most of §I closed)
9. `§X existential` (when bored, or when an arc surfaces one)

**When to depart from the rule.** Operator AUQ overrides at any step. Class 1 fork detection (§4.3 of CLAUDE.md) halts the rule and routes to design-phase back-flow. Drift detection halts immediately. The rule is not a contract — it is a discipline that fails loudly.

**`NO_ACTIVE_CANDIDATES` does NOT terminate the session (anti-parking — CLAUDE.md §12.4.1, operator directive 2026-06-02).** Step-4 `HALT("NO_ACTIVE_CANDIDATES")` means "no item is *auto-`ACTIVE`*", NOT "no Claude work remains." The `not r.operator_halt_marker` filter and the `PROPOSED`/`DEFERRED`/`infra-gated` statuses exclude items from the *auto* queue — they do **not** make those items the operator's to execute. The operator executes nothing manually. When the auto-queue is empty, **do not stop**: pick the highest-value forward item per the priority order above, **ground it**, and **drive its Claude-executable slice to the genuine gate** (build the stdlib/mockable slice + scaffolding + the recipe the operator runs), then surface only the genuine gate — a real decision, a credential, paid-call authorization, or an irreversible action — batched and minimal (the paid-call/secret boundary stays per `[[feedback-background-agent-no-unilateral-paid-calls-or-secret-relocation]]`; a *held* operator decision is honored, not overridden). See CLAUDE.md §12.4.1 + `[[feedback-operator-labels-are-claude-driven-no-parking]]`.

---

## 5. R-NNN action catalog

**Populated entries: 28.** Decomposition-owed markers per §9 for §IV–§VI + §VIII–§X.

### ⚑ 5.0 STANDING DIRECTIVE — FULL SPEC, NOTHING DEFERRED (operator 2026-06-12, will-NOT-drift)

> *"Nothing is deferred and the full spec will be built beyond MVP, no exceptions or excuses. This is the objective and it will not drift moving forward. If a producer, wiring, surface, etc must be researched, designed, speced and planned to unblock code implementation then it will happen...period."*

**Effect on this catalog + §4 derivation:**
- **"confirm-defer" / "ratified-bounded" / "DEFERRED-by-design" are no longer valid closes for an unbuilt capability.** Every such entry is RE-OPENED as a build arc under the single umbrella program **`R-FS-1`** below.
- The previously-DEFERRED capability entries (`R-CL-P1` routing intelligence, `R-CL-P2` engine-recovery, the arc-#6 confirm-defers, EMBEDDING/LLM_AS_ROUTER residuals, `R-CXA-2` durable-recovery, `CP-16`/`OD-6` register residuals) **folded under `R-FS-1` as child arcs** — they kept their DEFERRED status-field while R-FS-1 sequenced the build work.
- **`R-CL-Q1..C1` (the entire quality/close track) moved BEHIND `R-FS-1`** — quality runs ONCE on the full-spec harness. `R-CL-Q1` is now ACTIVE after R-FS-1 Tier-1 closure.
- Committed invariants stay the HOW (I-6 hand-roll; ADR-F1 per-provider SDKs); the directive is about scope, NOT overriding ADRs.

Spine: `.harness/beyond-mvp-capability-boundary-ledger.md` (the build inventory) + `[[feedback-full-spec-beyond-mvp-nothing-deferred]]`.

```yaml
R-FS-1:
  title: Full-spec build program — build every MVP-bounded / deferred capability to full spec (nothing deferred)
  surface: I-fullspec
  status: RESOLVED   # 2026-06-28 — Tier-1 build-complete closed: arc ledger pins 69 closed / 0 gated / 4 resolved / 0 forward; closure_gate.py automatable predicates pass; manual G1.4/G1.7/G1.8 signed at .harness/r-fs-1-tier1-manual-signoff.json.
  depends_on: []
  blocks: [R-CL-Q1, R-CL-Q2, R-CL-Q3, R-CL-Q4, R-CL-D1, R-CL-C1]
  posture: design-phase   # most arcs are design-fork-first (X-AL-3): research→design→spec→plan→implement
  scope: { files: [.harness/beyond-mvp-capability-boundary-ledger.md (spine), design-substrate/** (spec/plan/ADR amendments), harness-*/src/**], contracts: [C-CP-25 topology, C-CP-07 engine-classes, C-RT-17/18 HITL, C-RT-15 dispatch, C-CP-02/03 routing, + contract-completeness candidates], cross_axis: yes }
  skills: { primary: systems-architect, secondary: [spec-writer, implementation-planner, phase-7-implementation, harness-adversarial-reviewer, council-orchestrator] }
  advisor_required: yes
  council_required: conditional:nameable-tension
  verification: { shape: e2e, must_pass: ["the build inventory (ledger Bucket A re-opened + Bucket B + the contract-w/o-cite candidates + the fuller spec-body pass) is COMPLETE and every item BUILT (research/design/spec/plan/impl) — no item closed as deferred/bounded-residual", "the overlay `contract w/o code cite` driven to zero (or each remaining one proven implemented-but-uncited)", "ONLY THEN do R-CL-Q1..C1 open on the full-spec harness"] }
  close_shape: { type: program, artifact: "per-arc PRs tracked in the ledger", cascade: [R-IF-roadmap-refresh] }
  next_pointer: R-CL-Q1   # R-FS-1 build-complete; quality/close track opens at Q1.
  notes: |
    OPERATOR STANDING DIRECTIVE 2026-06-12 (verbatim above; will-NOT-drift). Retires the MVP+bounded-residual posture.
    SPINE: `.harness/beyond-mvp-capability-boundary-ledger.md` (grounded inventory: Bucket B = topology / engine-classes /
    smart-HITL / multi-server-MCP / per-role-dispatch / memory-per-surface / per-tool-sandbox; Bucket A re-opened =
    LLM_AS_ROUTER / EMBEDDING / cost-aggregate / HITL-OQ-6 / engine-recovery; Bucket C = stale-docstring doc-hygiene → Q1).
    SCOPE = TWO LEVELS: (1) MVP-marker boundaries (reduced-but-present); (2) contract-level completeness (specced C-* with
    no/partial carrier — `just overlay-query --orphans`, 8 candidates at HEAD: C-CP-30/37/43/49/50, C-IS-11, C-OD-3, C-RT-28).
    Arc #1 closes the scope (resolve the 8 + fuller spec-body pass) before sequencing builds.
    SEQUENCE (capability-unlock first; design-fork-first per X-AL-3): arc-1 scoping → B1 topology orchestration (multi-agent /
    parallel / cross-comm; the biggest) → B3 smart-HITL (supplies OQ-6 producer) → engine classes (hand-roll, I-6) →
    B2 multi-server MCP → LLM_AS_ROUTER + EMBEDDING (router-model / corpus surfaced at the vendor boundary) → B4 per-role
    dispatch → cost-aggregate → B5/B6/B7 + minor field-level. Each large item: research→design→spec→plan→implement.
    HOW-INVARIANTS PRESERVED: I-6 (hand-roll engines/orchestration, no vendored framework/LiteLLM); ADR-F1 (per-provider SDKs).
    RETAINED EXTERNAL GATES (not deferral): EMBEDDING corpus+model; LLM_AS_ROUTER router-model — design to the decision
    point, surface the one input at the vendor boundary, never auto-fire (`[[feedback-background-agent-no-unilateral-paid-calls-or-secret-relocation]]`).
```

### 5.1 Mode-agnostic infrastructure (R-IF-NNN)

```yaml
R-IF-108:
  title: PR #108 — workflow v1.12 §7.4.7.3.C audit at per-axis CLAUDE.md §4.1
  surface: VII
  status: RESOLVED
  depends_on: []
  blocks: []
  posture: mode-agnostic
  scope: { files: [harness-*/CLAUDE.md], contracts: [], cross_axis: no }
  skills: { primary: null, secondary: [] }
  advisor_required: no
  council_required: no
  verification: { shape: grep, must_pass: ["§4.1 cumulative-count lines refreshed against batch-NN production state"] }
  close_shape: { type: PR-merge, artifact: "PR #108", cascade: [R-IF-roadmap-refresh] }
  next_pointer: null
  notes: RESOLVED at PR #108 merge `54337c1` (2026-05-31). Stale-ACTIVE status reconciled at the R-001 close refresh (PR #141 cascade).

R-IF-109:
  title: PR #109 — memory entries round-3 audit
  surface: VII
  status: RESOLVED
  depends_on: []
  blocks: []
  posture: mode-agnostic
  scope: { files: [memory/**], contracts: [], cross_axis: no }
  skills: { primary: null, secondary: [] }
  advisor_required: no
  council_required: no
  verification: { shape: grep, must_pass: ["3 findings resolved per PR body"] }
  close_shape: { type: PR-merge, artifact: "PR #109", cascade: [R-IF-roadmap-refresh] }
  next_pointer: null
  notes: RESOLVED at PR #109 merge `a81fe2d` (2026-05-31). Stale-ACTIVE status reconciled at the R-001 close refresh.

R-IF-110:
  title: PR #110 — CXA v2.18 absorb OD-IS-EDGE-DRIFT (halt-doc Item 11)
  surface: VII
  status: RESOLVED
  depends_on: []
  blocks: [R-700-OD-IS-EDGE-DRIFT]
  posture: design-phase
  scope: { files: [design-substrate/Cross_Axis_Composition_Document_*.md], contracts: [CXA §2.3.5], cross_axis: yes }
  skills: { primary: spec-writer, secondary: [harness-adversarial-reviewer] }
  advisor_required: yes
  council_required: conditional:nameable-tension
  verification: { shape: grep, must_pass: ["CXA §2.3.5 cardinality reconciled with OD plan v2.6 §4.5.1", "clearance marker filed"] }
  close_shape: { type: substrate-amendment, artifact: "CXA v2.17 → v2.18", cascade: [R-IF-roadmap-refresh] }
  next_pointer: R-IF-111
  notes: RESOLVED at PR #110 merge `2f14604` (2026-05-31). Stale-ACTIVE status reconciled at the R-001 close refresh.

R-IF-111:
  title: PR #111 — OD plan v2.27 NEW §4.6 OD-INTERNAL carve-out (halt-doc Item 12)
  surface: VII
  status: RESOLVED
  depends_on: []
  blocks: [R-700-OD-INTERNAL-FORMALIZATION]
  posture: design-phase
  scope: { files: [design-substrate/Implementation_Plan_Operational_Discipline_*.md], contracts: [], cross_axis: no }
  skills: { primary: implementation-planner, secondary: [harness-adversarial-reviewer] }
  advisor_required: yes
  council_required: no
  verification: { shape: grep, must_pass: ["§4.6 OD-INTERNAL section authored", "clearance marker filed"] }
  close_shape: { type: substrate-amendment, artifact: "OD plan v2.26 → v2.27", cascade: [R-IF-roadmap-refresh] }
  next_pointer: null
  notes: RESOLVED at PR #111 merge `fdf120b` (2026-05-31). Stale-ACTIVE status reconciled at the R-001 close refresh.

R-IF-112:
  title: spec-code-overlay arc — overlay spec↔code↔CXA↔substitution semantic layer onto the code graph (drift-detection)
  surface: VII
  status: RESOLVED
  depends_on: []
  blocks: []
  posture: mode-agnostic
  scope: { files: [.harness/spec-code-overlay/**, tools/**], contracts: [], cross_axis: no }
  skills: { primary: null, secondary: [] }
  advisor_required: no
  council_required: no
  verification: { shape: e2e, must_pass: ["deterministic cross-reference linter flags orphans (code w/o cite · contract w/o landed code · CXA seam w/o producer · substitution w/o carrier)", "runs parse-only per-merge — no LLM pass"] }
  close_shape: { type: PR-merge, artifact: "tools/ spec↔code cross-reference linter", cascade: [R-IF-roadmap-refresh] }
  next_pointer: null
  notes: >
    Seeded 2026-06-04 at PR #288 (canonical-ICM workspace `.harness/spec-code-overlay/` per
    `RinDig/Interpreted-Context-Methdology`; stage-01 exploration LANDED). Premise: understand-anything
    models code↔code only; this repo's load-bearing relationship is spec-contract ↔ code ↔ CXA-edge ↔
    substitution. Stage-01 probe: ~99.6% (277/278) of source files carry a parseable authority cite →
    the traceability layer is deterministically extractable (no LLM pass). MVP = a `tools/` orphan-linter
    (sibling to `substitution_ledger.py`), built before any visualization. Forward stages: 02-design
    (overlay JSON schema + linter contract; fork-vs-sidecar) · 03-build (`tools/` linter + freshness hook;
    gate-vs-advisory). Composes with the council context-memory arc (interpretable-context); does not duplicate it.
    Resolved by the R-IF-112 implementation closeout: `tools/semantic_overlay/overlay.py` now derives the
    code cite layer, design-substrate `C-*` keyspace, CXA seam endpoint graph, and substitution ledger join
    without LLM calls; `overlay.py check` is CI-gated for hard CXA/stale-artifact drift; advisory orphan
    reporting covers code without cite, contract without code cite, and substitution without direct carrier.

R-IF-114:
  title: dashboard-generate test rot — `tools/test_dashboard_generate.py` ungated brittle arc-map snapshot
  surface: VII
  status: RESOLVED    # 2026-06-30 — stale ACTIVE closed; dashboard tests now derive from arc-ledger and are CI-gated.
  depends_on: []
  blocks: []
  posture: mode-agnostic
  scope: { files: [tools/test_dashboard_generate.py, .github/workflows/ci.yml], contracts: [], cross_axis: no }
  skills: { primary: null, secondary: [] }
  advisor_required: no
  council_required: no
  verification: { shape: none, must_pass: ["tools/test_dashboard_generate.py green against the current arc-map", "chosen disposition (robust+gated OR drop-live-assertions) recorded"] }
  close_shape: { type: PR-merge, artifact: "tools/test_dashboard_generate.py disposition", cascade: [R-IF-roadmap-refresh] }
  next_pointer: null
  notes: >
    RESOLVED 2026-06-30 — the stale ACTIVE entry is closed after re-grounding against HEAD.
    The old brittle hard-coded live-data assertions were replaced with schema/ledger-derived
    invariants in `tools/test_dashboard_generate.py`: frozen arc order derives from
    `.harness/arc-ledger.yaml`, standalone status counts derive from the ledger, and registered
    forward arcs carry parent/anticipated-scope/decompose markers without fabricated U-* units.
    CI now gates the dashboard/arc-ledger/tooling lane at `.github/workflows/ci.yml` via
    `uv run python -m pytest test_arc_ledger.py test_dashboard_generate.py test_runtime_contract_ids.py -q`.
    Verification on the close branch: `tools/test_dashboard_generate.py` included in the focused
    dashboard/context suite and prior PR #845/#846 CI green. No further operator disposition is
    owed for the original stale-count rot class.

R-IF-115:
  title: Remaining-build audit surface + closure gate — fold into the loop
  surface: VII
  status: RESOLVED    # 2026-06-30 — stale ACTIVE closed; PR #676 landed the audit and closure gate, now green at HEAD.
  depends_on: []
  blocks: []
  posture: mode-agnostic
  scope: { files: [.harness/audit/**, tools/semantic_overlay/overlay.py, Project_Roadmap_v1.md], contracts: [], cross_axis: no }
  skills: { primary: null, secondary: [harness-adversarial-reviewer] }
  advisor_required: yes
  council_required: no
  verification: { shape: none, must_pass: ["audit report + register (48 rows) + Closure_Gate_v1.md authored at .harness/audit/", "overlay contract-orphan head-scoping landed (6 phantoms -> 1) + head-scoped unit_without_code advisory added; overlay-check HARD gate green; 17 overlay tests pass", "findings routed to their R-CL/R-IF homes (notes)", "live sources stay canonical — NO maintained parallel CSV"] }
  close_shape: { type: PR-merge, artifact: ".harness/audit/* + overlay head-scoping + this entry", cascade: [R-IF-roadmap-refresh] }
  next_pointer: null
  notes: >
    RESOLVED 2026-06-30 — PR #676 landed the 2-pass remaining-build audit
    (`.harness/audit/Remaining_Build_Audit_Report.md` + `Remaining_Build_Register.csv`),
    `.harness/audit/Closure_Gate_v1.md`, `tools/closure_gate.py`, and `tools/test_closure_gate.py`.
    The checker is no longer a defined-but-unbuilt follow-on: `just closure-gate` delegates to the
    live authorities and reports Tier-1 build-complete plus Tier-2 quality/close signed at HEAD
    (5/5 automatable Tier-1, 3/3 manual Tier-1, 6/6 Tier-2 phases RESOLVED).
    Findings routed by the original point-in-time audit have either landed in the Q1-Q4/D1/C1
    close track or remain deliberately represented in the live arc ledger / closure-gate residual
    review instead of this stale ACTIVE entry. No new build arc is opened here.

R-IF-roadmap-refresh:
  title: Refresh roadmap status dashboard after PR merge
  surface: VII
  status: ACTIVE
  depends_on: []
  blocks: []
  posture: mode-agnostic
  scope: { files: [.harness/roadmap_status.md], contracts: [], cross_axis: no }
  skills: { primary: null, secondary: [] }
  advisor_required: no
  council_required: no
  verification: { shape: none, must_pass: ["dashboard workspace_state_hash matches git HEAD", "RETIRED count current", "open-PR list current"] }
  close_shape: { type: PR-merge, artifact: "ops: roadmap status refresh post-PR-NN", cascade: [] }
  next_pointer: null
  notes: Triggered automatically per CLAUDE.md §12 post-merge hook. Manual fallback if hook absent.

R-IF-council-context-memory:
  title: Context & memory layer grounding — domain council arc (the FIRST of the charter's planned domain-council series)
  surface: VII
  status: RESOLVED
  depends_on: []
  blocks: []
  posture: mode-agnostic
  scope: { files: [.harness/council/context-memory-grounding/**], contracts: [], cross_axis: no }
  skills: { primary: council-orchestrator, secondary: [c2, c3, c1, c5, c7, c8, c9, harness-adversarial-reviewer] }
  advisor_required: yes
  council_required: yes
  verification: { shape: none, must_pass: ["every pairwise reviewer gate reconciled-to-zero", "adversarial #2 gate CLEAR / CLEAR-WITH-FOLD", "deliverable DESIGN.md committed + merged"] }
  close_shape: { type: PR-merge, artifact: "DESIGN.md v2 (context+memory grounding + alignment plan)", cascade: [R-IF-council-workflow] }
  next_pointer: R-IF-council-workflow
  notes: >
    RESOLVED at PR #292 merge `2b19d4e` (2026-06-04). The FIRST domain council per the charter's "planned series
    of domain councils." Genuinely-invoked 7-voice council (C2/C3 primaries + C1/C5/C7/C9 + C8 consultants) →
    adversarial #1 → Codex (out-of-family gpt-5.5) + advisor (in-family) → consolidated council reconcile →
    adversarial #2 gate (CLEAR-WITH-FOLD). Every reviewer/voice genuinely invoked (skills adopted by dedicated
    agents, debating by name); every pairwise gate reconciled-to-zero. Deliverable = DESIGN.md v2 (a falsifiable
    WS-0-drift-gated plan to ground the harness's own context/memory governance layer). Ledger at
    `.harness/council/context-memory-grounding/`. Spine held: zero new MVP workstreams; one new mechanism (G-LINK)
    deferred. Reusable workflow codified at R-IF-council-workflow. (Dashboard hash-refresh for #292 = the
    SessionStart-audit / §12.2.1 fixed point — NOT this entry.)

R-IF-council-workflow:
  title: Council workflow productization — codify the genuinely-invoked council -> adversarial -> Codex/advisor reconcile-to-zero loop as reusable YAML + /commands
  surface: VII
  status: RESOLVED
  depends_on: [R-IF-council-context-memory]
  blocks: []
  posture: mode-agnostic
  scope: { files: [.harness/council/**, .claude/commands/**], contracts: [], cross_axis: no }
  skills: { primary: null, secondary: [] }
  advisor_required: yes
  council_required: no
  verification: { shape: none, must_pass: ["two YAMLs of the same shape/flow — (1) harness-layer-aware council-skill router (council-skill-agnostic pre-invocation; invokes the relevant cN voices per the harness layer/axis), (2) fully council-skill-agnostic for any future council/task", "the HIL gates that kept the context-memory arc on track captured (halt-before-each-full-council-convening / primaries->consultants->cross-read / decorrelated-reviewer wiring [Codex cold + advisor transcript-aware] / reconcile-to-zero per pairwise gate)", "a /command invokes each YAML"] }
  close_shape: { type: PR-merge, artifact: "council-workflow YAMLs + /commands + workflow doc", cascade: [R-IF-roadmap-refresh] }
  next_pointer: null
  notes: >
    Operator-directed 2026-06-04 immediately after R-IF-council-context-memory closed. Synthesizes the lived
    workflow into a documented, reusable shape (surface VII process-discipline tooling, sibling to the council
    skills at `.claude/skills/council/`). Resolved 2026-06-08 by materializing the command targets under
    `.harness/council/`: the harness-layer-aware YAML, the generic same-shape YAML, the prose companion, and the
    context-memory grounding provenance pointer. The existing `/council-workflow` and `/council-generic` commands
    now invoke real specs rather than missing paths.

```

### 5.2 Phase 7 axis-clean (R-001..R-099)

```yaml
R-001:
  title: H_T-OD-5 cost-attribution — RETIRED (reconciled at R-002 survey)
  surface: I
  status: RESOLVED
  depends_on: [R-100-mvp-operator-usable-cli-shipped, R-100-mvp-real-workflow-execution]
  blocks: [R-700-phase-8-substitution-accounting]
  posture: halt-route-to-operator
  scope: { files: [.harness/phase-7d-retirement-events-batch-NN.md], contracts: [], cross_axis: no }
  skills: { primary: phase-7-substitution-retirement, secondary: [] }
  advisor_required: yes
  council_required: no
  verification: { shape: e2e, must_pass: ["operator-bound RuntimeConfig.validator_framework_config non-None", "operator-explicit WebhookDeliveryComposer with cost-attribution substrates", "≥1 real dispatch surface exercised", "cost:-prefixed audit-ledger entries observed at production"] }
  close_shape: { type: retirement-event, artifact: ".harness/phase-7d-retirement-events-batch-NN.md", cascade: [R-IF-roadmap-refresh] }
  next_pointer: R-IF-roadmap-refresh
  notes: RESOLVED — OD-5 already RETIRED 2026-05-28 batch-32 via mech-β AC #8 green (PR #14 `24a9363`); harness-od/CLAUDE.md §4.1 gates sub-section confirms "Terminal in-CLI state at RETIRED ... full RETIRED achieved at batch-32". The BLOCKED-awaiting-operator-deployment model here was a stale-authoring error (used the stale dashboard "RETIRE-READY 2 active" claim). Reconciled at R-002 survey 2026-05-31.

R-002:
  title: Remaining substitution retirements survey (Surface-I decomposition)
  surface: I
  status: RESOLVED
  depends_on: []
  blocks: [R-700-phase-8-substitution-accounting]
  posture: phase-7
  scope: { files: [harness-*/CLAUDE.md §4.1, .harness/phase-7d-retirement-events-batch-*.md], contracts: [], cross_axis: no }
  skills: { primary: phase-7-substitution-retirement, secondary: [] }
  advisor_required: conditional:if a candidate retirement crosses ≥2 axes
  council_required: no
  verification: { shape: grep, must_pass: ["all STILL-BOUNDED + PARTIAL + RETIRE-READY rows enumerated", "each row classified executable-now / awaiting-MVP / awaiting-multi-deployment / awaiting-operator-decision"] }
  close_shape: { type: substrate-amendment, artifact: "Roadmap §5.2 expanded with per-row R-NNN", cascade: [] }
  next_pointer: R-003
  notes: RESOLVED at first execution 2026-05-31 (Surface-I decomposition pass). Survey enumerated all non-RETIRED rows across harness-*/CLAUDE.md §4.1. Output — IS-2 PARTIAL (covered R-003 + R-001-h-t-is-2-retired); OD-5 + AS-8d RETIRED (reconciled R-001 + R-004 stale BLOCKED → RESOLVED — they were retired via mech-β batches 31-32, not the operator-deployment path the entries modeled); AS-8e + AS-8f STILL-BOUNDED-INDEFINITELY (NEW R-005 + R-006 DEFERRED); OD-3 + OD-6 RETIRE-READY (NEW R-007 + R-009 BLOCKED on real-deployment X-AL-2 second conjunct OR operator-AUQ Reading α); OD-4 PARTIAL (NEW R-008 BLOCKED on §13.1/§13.2 gate closures). CP-axis §4.1 fully RETIRED — no entries owed. 7 distinct non-RETIRED rows now mapped. Dashboard "Phase 7 retirement progress" table reconciled in the same PR.

R-003:
  title: Producer-site lifts of EntryPayload.procedural_tier_snapshot_ref (workflow-context sites)
  surface: I
  status: RESOLVED
  depends_on: []
  blocks: [R-001-h-t-is-2-retired]
  posture: phase-7
  scope: { files: [harness-cp/**, harness-runtime/**], contracts: [C-IS-05 §5.1 §5.2], cross_axis: yes }
  skills: { primary: phase-7-implementation, secondary: [phase-7-cross-axis-composition] }
  advisor_required: satisfied:2026-05-31   # 55th application; X-AL-3 cleared (IS §5.1 general principle). Re-run only on a NEW cross-axis question.
  council_required: no
  verification: { shape: integration, must_pass: ["each LIFTED workflow-context site populates EntryPayload.procedural_tier_snapshot_ref via resolver closure", "no lifted site bypasses resolver", "documented outside-context sites keep None per IS §5.1", "HALT-on-resolver-failure (no ledger write)"] }
  close_shape: { type: PR-merge, artifact: "PR per cluster — Cluster A (runtime: sub_agent_dispatch + hitl_gate_composer); Cluster B (CP: workflow_driver + sibling_ledger); + 5/6/7 None-canonical docs", cascade: [R-IF-roadmap-refresh, R-001-h-t-is-2-retired] }
  next_pointer: R-001-h-t-is-2-retired
  notes: >
    RESOLVED 2026-05-31 — delivered across PR #136 (Cluster A: runtime sub_agent_dispatch + hitl_gate_composer, resolver built at bootstrap stage 5) + PR #137 (Cluster B: CP workflow_driver _append_step_ledger_entry + sibling-ledger via the cp_is_wiring resolver, resolver wired onto HarnessContext + DriverContext Protocol at stage 6) + the 3 None-canonical doc-comments (audit_writer, as_is_wiring, shadow_git_rollback). All 7 IS-2 producer sites handled (4 lifted, 3 documented). 2281 tests pass; ruff+pyright clean vs main. resume:/checkpoint pointer removed per §3 on RESOLVE; .harness/R-003-checkpoint.md retained as historical record. Unblocks R-001-h-t-is-2-retired.

R-001-h-t-is-2-retired:
  title: H_T-IS-2 PARTIAL → RETIRED transit
  surface: I
  status: RESOLVED   # H_T-IS-2 RETIRED at batch-50; PR #141 merge `4a0aa1d` 2026-05-31
  depends_on: [R-003]
  blocks: [R-700-phase-8-substitution-accounting]
  posture: phase-7
  scope: { files: [.harness/phase-7d-retirement-events-batch-NN.md, harness-is/CLAUDE.md, .harness/phase-7d-retirement-ledger-v2.md], contracts: [], cross_axis: no }
  skills: { primary: phase-7-substitution-retirement, secondary: [] }
  advisor_required: no
  council_required: no
  verification: { shape: grep, must_pass: ["all 7 producer sites handled — 4 lifted (sub_agent_dispatch, hitl_gate_composer, sibling_ledger, workflow_driver step) + 3 documented None-canonical (audit_writer, as_is_wiring, shadow_git_rollback) per PR #136/#137", "X-AL-2 second conjunct (H_E surface no longer invoked) met"] }
  close_shape: { type: retirement-event, artifact: ".harness/phase-7d-retirement-events-batch-NN.md", cascade: [R-IF-roadmap-refresh] }
  next_pointer: R-002
  notes: >
    RESOLVED 2026-05-31 at PR #141 merge `4a0aa1d` — batch-50 filed (H_T-IS-2 PARTIAL → RETIRED; X-AL-2 BOTH conjuncts MET). All 13 producer sites handled: 6 §16.5 composers (PR #107) + 4 lifted (R-003 Cluster A #136: sub_agent_dispatch + hitl_gate_composer; Cluster B #137: workflow_driver + sibling_ledger) + 3 documented None-canonical (audit_writer, as_is_wiring, shadow_git_rollback). harness-is/CLAUDE.md §4.1 IS-2 row → RETIRED (IS-axis 9/9 RETIRED = 100%, FIRST axis fully RETIRED at the strict RETIRED view); ledger v2 §11.4h supersession entry (forward-only; §3 snapshot preserved). next_pointer R-002 already RESOLVED → re-derived next-action = R-200-ci-pytest-pyright-ruff-matrix (§III, rank 3) per §4.

R-004:
  title: H_T-AS-8d skill.* — RETIRED (reconciled at R-002 survey)
  surface: I
  status: RESOLVED
  depends_on: [R-100-mvp-operator-usable-cli-shipped, R-100-mvp-real-workflow-execution]
  blocks: [R-700-phase-8-substitution-accounting]
  posture: halt-route-to-operator
  scope: { files: [.harness/phase-7d-retirement-events-batch-NN.md], contracts: [], cross_axis: no }
  skills: { primary: phase-7-substitution-retirement, secondary: [] }
  advisor_required: yes
  council_required: no
  verification: { shape: e2e, must_pass: ["operator-bound RuntimeConfig.skill_activation_hook_config non-None", "≥1 real workflow exercises ≥1 of 3 skill activation hook surfaces", "skill.* namespace span emitted at production"] }
  close_shape: { type: retirement-event, artifact: ".harness/phase-7d-retirement-events-batch-NN.md", cascade: [R-IF-roadmap-refresh] }
  next_pointer: R-IF-roadmap-refresh
  notes: RESOLVED — AS-8d already RETIRED 2026-05-28 batch-31 via mech-β AC #7 green (PR #14 `24a9363`); harness-as/CLAUDE.md §4.1 row confirms RETIRED. BLOCKED-awaiting-operator-deployment model was a stale-authoring error. Reconciled at R-002 survey 2026-05-31.

# ── R-005..R-009 authored at R-002 Surface-I decomposition pass (2026-05-31) ──
# Survey of all non-RETIRED substitution rows across harness-*/CLAUDE.md §4.1.
# Covered pre-survey: IS-2 (R-003 + R-001-h-t-is-2-retired); OD-5 (R-001 → RESOLVED);
# AS-8d (R-004 → RESOLVED). NEW per-row entries below for the 5 uncovered rows.

R-005-as-8e-files-indefinite:
  title: H_T-AS-8e (files.* namespace) — INDEFINITE deferral accounting
  surface: I
  status: RESOLVED   # batch-52: R-810 live Files proof back-flowed AS-8e into SUBSTANTIVE_RETIRED
  depends_on: []
  blocks: [R-700-phase-8-substitution-accounting]
  posture: halt-route-to-operator
  scope: { files: [.harness/phase-7d-retirement-events-batch-NN.md], contracts: [], cross_axis: no }
  skills: { primary: phase-7-substitution-retirement, secondary: [] }
  advisor_required: no
  council_required: no
  verification: { shape: e2e, must_pass: ["R-810 live Anthropic Files upload/reference/delete", "managed-cloud files.operation trace carries files.* attributes"] }
  close_shape: { type: retirement-event, artifact: ".harness/phase-7d-retirement-events-batch-52.md", cascade: [] }
  next_pointer: null
  notes: RESOLVED at batch-52. The original R-005 entry tracked the accepted-indefinite-defer state for AS-8e while the Files arc was not opened. The operator later opened R-810; the real Anthropic Files adapter uploaded/referenced/deleted a live file, exported `files.operation` through the authenticated managed collector, and Cloud Trace `bfd28fa8fc8ecc3ba973d1e405cdb865` carried `files.*` attrs. Batch-52 back-flows AS-8e from `SB_INDEFINITE` to `SUBSTANTIVE_RETIRED`.

R-006-as-8f-managed-agents-indefinite:
  title: H_T-AS-8f (managed_agents.* namespace) — INDEFINITE deferral accounting
  surface: I
  status: RESOLVED   # batch-52: R-820 live Managed Agents proof back-flowed AS-8f into SUBSTANTIVE_RETIRED
  depends_on: []
  blocks: [R-700-phase-8-substitution-accounting]
  posture: halt-route-to-operator
  scope: { files: [.harness/phase-7d-retirement-events-batch-NN.md], contracts: [], cross_axis: no }
  skills: { primary: phase-7-substitution-retirement, secondary: [] }
  advisor_required: no
  council_required: no
  verification: { shape: e2e, must_pass: ["R-820 real Anthropic Managed Agents SDK/session integration", "managed-cloud managed_agents.runtime trace carries managed_agents.* attributes"] }
  close_shape: { type: retirement-event, artifact: ".harness/phase-7d-retirement-events-batch-52.md", cascade: [] }
  next_pointer: null
  notes: RESOLVED at batch-52. The original R-006 entry tracked the accepted-indefinite-defer state for AS-8f while the managed_agents integration was production-only / managed-cloud gated. R-820 later added the real Anthropic Managed Agents SDK/session adapter, observed session `sesn_019aMgaF8sAW2cXhhpMTYij4` reach `session.status_idle`, exported `managed_agents.runtime`, and confirmed Cloud Trace `009d7716b19c75e4ad7edb93e78f8d2b` carried `managed_agents.*` attrs. Batch-52 back-flows AS-8f from `SB_INDEFINITE` to `SUBSTANTIVE_RETIRED`.

R-010-cp-17-files-indefinite:
  title: H_T-CP-17 (files.* primitives consumption) — INDEFINITE deferral accounting
  surface: I
  status: RESOLVED   # batch-52: R-810 live Files proof back-flowed CP-17 into SUBSTANTIVE_RETIRED
  depends_on: []
  blocks: [R-700-phase-8-substitution-accounting]
  posture: halt-route-to-operator
  scope: { files: [.harness/phase-7d-retirement-events-batch-NN.md], contracts: [], cross_axis: no }
  skills: { primary: phase-7-substitution-retirement, secondary: [] }
  advisor_required: no
  council_required: no
  verification: { shape: e2e, must_pass: ["R-810 live Anthropic Files API adapter/reference composition", "managed-cloud files.operation trace carries files.* attrs"] }
  close_shape: { type: retirement-event, artifact: ".harness/phase-7d-retirement-events-batch-52.md", cascade: [] }
  next_pointer: null
  notes: >
    Authored 2026-06-02 per R-700 ratification (operator chose "Author R-NNN entries" at AskUserQuestion) —
    closes the R-700 draft §C item 2 coverage gap for CP-17, the last of the 5 flagged rows lacking a
    dedicated entry (CXA-1/2/3/4 already covered by R-CXA-1..4, authored at PR #209; the draft's "no R-entry"
    framing for those was stale — compiled post-#206, before #209). CP-17 = the Files-primitives sibling of
    AS-8e (R-005); reclassified STILL-BOUNDED-INDEFINITELY at batch-44 per runtime spec v1.17 §14.C
    (Files-arc ratified Memory-only-MVP scope). Implementation-bundled into `R-810-files-api-integration`
    (AS-8e/CP-17); this entry gives CP-17 standalone substitution-accounting tracking parallel to R-005/R-006.
    The operator later opened R-810; the live Anthropic Files API adapter/reference composition and managed-cloud
    `files.operation` proof consumed the Files arc. Batch-52 back-flows CP-17 from `SB_INDEFINITE` to
    `SUBSTANTIVE_RETIRED`.

R-007-od-3-sampler-retired:
  title: H_T-OD-3 (Composite Sampler) RETIRE-READY → RETIRED transit
  surface: I
  status: RESOLVED   # H_T-OD-3 substantive RETIRED at batch-51 (2026-06-01); flipped BLOCKED → eligible once R-100-mvp-real-workflow-execution RESOLVED, then closed
  depends_on: [R-100-mvp-real-workflow-execution]
  blocks: [R-700-phase-8-substitution-accounting]
  posture: phase-7
  scope: { files: [.harness/phase-7d-retirement-events-batch-NN.md], contracts: [], cross_axis: no }
  skills: { primary: phase-7-substitution-retirement, secondary: [] }
  advisor_required: satisfied:2026-06-01   # advisor caught the bounded-residual pre-commit + named the condition-(B) discriminator that produced the OD-3 (substantive) vs OD-6 (bounded-residual) split
  council_required: no
  verification: { shape: e2e, must_pass: ["HarnessCompositeSampler + TailKeepSpanProcessor exercised at a production-surface deployment (non-LOCAL_DEVELOPMENT)", "X-AL-2 second conjunct — head-based sampler substitution no longer the active path at production OTel pipeline"] }
  close_shape: { type: retirement-event, artifact: ".harness/phase-7d-retirement-events-batch-51.md", cascade: [R-IF-roadmap-refresh] }
  next_pointer: R-009-od-6-otlp-retired
  notes: >
    RESOLVED 2026-06-01 at batch-51 — H_T-OD-3 RETIRE-READY → RETIRED (substantive) via the
    gate-text-stale-vs-production-landings audit (workflow v1.12 §7.4.7.2 sub-species 10, THIRD closure).
    Condition-(B) audit: HarnessCompositeSampler is the live root sampler at materialize_tracer_provider_stage
    (the R-100-mvp-real-workflow-execution e2e exercised the production tracer provider with real spans);
    the H_E 7a-scaffold sampler is no longer invoked. The must_pass framing above (TailKeepSpanProcessor at a
    non-LOCAL deployment) was a production-FEATURE-validation over-reach — tail-keep is bypassed at LOCAL by
    design (§9.1) and observing §10.2 preservation at a real collector is roadmap R-430 (infra-gated), NOT an
    X-AL-2 retirement gate; the condition-(B) audit corrected this. Operator-ratified AskUserQuestion 2026-06-01
    (substantive RETIRED over bounded-residual). Drains an R-700 blocker. See
    .harness/phase-7d-retirement-events-batch-51.md §1 + ledger-v2 §11.4i.

R-008-od-4-redaction-partial:
  title: H_T-OD-4 (Pre-Collector redaction SpanProcessor) PARTIAL → RETIRE-READY gate closures
  surface: I
  status: RESOLVED   # batch-53: runtime residual closed by prior R-008 slices; OD-4 back-flowed into SUBSTANTIVE_RETIRED
  depends_on: []
  blocks: [R-700-phase-8-substitution-accounting]
  posture: phase-7
  scope: { files: [harness-od/**, harness-runtime/**], contracts: [C-OD-12, C-OD-13 §13.1 §13.2], cross_axis: no }
  skills: { primary: phase-7-implementation, secondary: [phase-7-substitution-retirement] }
  advisor_required: conditional:if a gate closure touches a cross-axis contract
  council_required: no
  verification: { shape: integration, must_pass: ["§13.1 per-session redaction toggle mechanism authored (deferred at PR #25 apply arc) — ✅ MET 2026-06-02 (gate a)", "§13.2 opaque-token tokenization substrate — ✅ OD provider-free substrate authored 2026-06-07; durable audit-ledger token-map persistence — ✅ authored 2026-06-07; provider-free category-token classifier seam — ✅ authored 2026-06-07; eval-grade semantic classifier + runtime multi-tenant audit-backed tokenization — ✅ authored 2026-06-07", "batch-53 accounting/back-flow moves OD-4 from PARTIAL to SUBSTANTIVE_RETIRED"] }
  close_shape: { type: retirement-event, artifact: ".harness/phase-7d-retirement-events-batch-53.md", cascade: [R-IF-roadmap-refresh] }
  next_pointer: R-007-od-3-sampler-retired
  notes: >
    PARTIAL (refined) at batch-35; gate (a) partially closed at PR #25 (deployment-level persona_tier +
    multi-tenant non-toggleability). **Gate (a) FULLY CLOSED 2026-06-02 (this arc): solo-developer §13.1
    per-session redaction toggle** — `session_content_capture()` ContextVar mechanism at
    `harness-od/redaction_span_processor.py`, honored only at solo-developer (`toggleable=True`); team-binding +
    multi-tenant ignore it (§13.3 downgrade-rejection). Grounding-first finding: the fork-doc-framed
    "session-control-substrate arc" was already satisfied by the existing per-session ContextVar idiom
    (`_CURRENT_TOOL_CTX`) — no heavy substrate owed (`[[grounding-reveals-claude-closeable-slice-close-honestly]]`).
    X-AL-3-clean (spec'd mechanism; §13.3 defers only the UX); 10 new tests incl. async-boundary propagation
    (create_task + to_thread); pyright/ruff clean; 898 harness-od green. **Gate (b) §13.2 opaque-token
    tokenization advanced 2026-06-07:** `harness_od.redaction_tokenizer` now provides an OD-owned,
    provider-free opaque-token substrate (`OpaqueRedactionTokenizer`, `RedactionTokenMap`, and
    `InMemoryRedactionTokenMap`), and `RedactionSpanProcessor(tokenizer=...)` can replace content-bearing
    span attributes with `[REDACTED:CONTENT:<id>]` placeholders while storing raw values only behind the
    token-map sink. Default strip-not-tokenize behavior remains unchanged unless a tokenizer is injected, and
    the solo-developer `session_content_capture()` override still bypasses tokenization only at the toggleable
    tier. **Durable audit-ledger token-map persistence advanced 2026-06-07:** `harness_od.redaction_token_audit`
    composes one signed OD `AuditLedgerEntry` per `RedactionTokenRecord`, and
    `harness_runtime.lifecycle.redaction_token_audit_map.AuditLedgerRedactionTokenMap` lets
    `OpaqueRedactionTokenizer` persist token→raw mappings through the runtime `AuditLedgerWriter` while exported
    spans still carry only opaque tokens. **Category-token seam advanced 2026-06-07:** `RedactionAttributeClassifier`
    / `RedactionAttributeClassification` plus `DeterministicRedactionClassifier` let the same token path emit
    conservative provider-free category placeholders such as `[REDACTED:PII:<id>]` and `[REDACTED:MCP_ARG:<id>]`,
    and the signed audit token-map entry now persists `audit.redaction_token.semantic_category`. **Runtime classifier
    + materialization advanced 2026-06-07:** `EvalGradeSemanticRedactionClassifier` now extends the category seam
    with provider-free attribute-semantic categories (`GENAI_PROMPT`, `GENAI_RESPONSE`, `TOOL_RESULT`,
    `RETRIEVAL_CONTENT`) plus high-signal `PII` / `SECRET` content cues, and stage 4 OD materialization wires
    `MULTI_TENANT_COMPLIANCE` redaction through `OpaqueRedactionTokenizer` + `AuditLedgerRedactionTokenMap` when
    an audit writer is available. Exported multi-tenant spans now carry only opaque category tokens such as
    `[REDACTED:PII:<id>]`, while token→raw mappings persist through the signed audit ledger; without an audit sink
    the runtime preserves the fail-closed strip mode. This closes the remaining runtime code gate for the classifier
    pipeline but does **not** alter the Phase-8 retirement tally in this implementation PR: OD-4's
    `RETIRED-AS-CROSS-AXIS-DEFERRED` accounting label was operator-ratified at R-700, so any bucket/tally
    reclassification is a separate accounting/back-flow action rather than part of this runtime slice.
    R-700 accounting: OD-4's code residual is now closed at runtime, but the ratified label remains unchanged here.
    **R-700 forward-pointer (operator decision):** with gate (b) established as cross-axis/Phase-6+,
    OD-4 can NEVER reach RETIRE-READY via Claude → it `blocks: [R-700]` indefinitely. This is the
    OD-6/R-009 shape from the prior session (drained via an operator-ratified bounded-residual close) —
    BUT the disposition differs: gate (b) is "not-built-cross-axis" (c10-action-safety owns it), NOT
    OD-6's "built-but-dormant", so a literal bounded-residual may not fit; a RETIRED-AS-CROSS-AXIS-DEFERRED
    (or equivalent) operator ruling is the candidate to unblock R-700. Surfaced for operator decision; NOT
    self-resolved (`[[r-007-r-009-od-retirement-condition-b-discriminator]]`).
    **✅ RATIFIED 2026-06-02 (R-700 AskUserQuestion):** operator accepted OD-4's `RETIRED-AS-CROSS-AXIS-DEFERRED`
    disposition as a Phase-8 sign-off (R-700 PART C item 3) — but **HELD the formal declaration** (PART C item 4),
    so the bucket flip (OD-4 PARTIAL → CROSS-AXIS-DEFERRED) executes at the eventual `phase-8-graduation.md` close,
    not now. R-008's remaining unclosed work is the eval-grade semantic classifier/category pipeline, not another
    OD-owned token-map substrate.
    **Propagation scope (honest bound):** the gate (a) tests verify language-primitive ContextVar
    propagation (create_task / to_thread); they do NOT drive the operator trigger path
    `with session_content_capture(): api.run(wf)`, which crosses the in-process MCP transport
    (server-task-dispatched run_workflow). That trigger hop is part of the §13.3-deferred toggle UX and
    may need an internal set-point inside the run_workflow handler — settled at the UX arc, not this
    mechanism close. must_pass[0] ("mechanism authored") is honestly MET; the trigger UX is §13.3-deferred.
    **RESOLVED 2026-06-08 at batch-53:** the later R-008 runtime slices closed the §13.2 tokenization/classifier
    residual that made the R-700 `RETIRED-AS-CROSS-AXIS-DEFERRED` label appropriate at Phase-8 declaration time.
    Batch-53 removes that active sign-off label from the live structured ledger and moves OD-4 from `PARTIAL` to
    `SUBSTANTIVE_RETIRED`. Historical Phase-8 prose remains historical.

R-009-od-6-otlp-retired:
  title: H_T-OD-6 (Local-first OTLP ingestion) RETIRE-READY → RETIRED transit
  surface: I
  status: RESOLVED   # H_T-OD-6 RETIRED-AS-BOUNDED-RESIDUAL at batch-51 (2026-06-01); FIRST bounded-residual close in the ledger
  depends_on: [R-100-mvp-real-workflow-execution]
  blocks: [R-700-phase-8-substitution-accounting]
  posture: phase-7
  scope: { files: [.harness/phase-7d-retirement-events-batch-NN.md], contracts: [], cross_axis: no }
  skills: { primary: phase-7-substitution-retirement, secondary: [] }
  advisor_required: satisfied:2026-06-01   # advisor named the condition-(B) discriminator (live vs dormant primitive) that split OD-3 (substantive) from OD-6 (bounded-residual)
  council_required: no
  verification: { shape: e2e, must_pass: ["4-OD-B SqliteWritePath ingestion exercised against real spans at a deployment", "X-AL-2 second conjunct — local-first OTLP substitution surface no longer invoked at production"] }
  close_shape: { type: retirement-event, artifact: ".harness/phase-7d-retirement-events-batch-51.md", cascade: [R-IF-roadmap-refresh] }
  next_pointer: R-001-h-t-is-2-retired
  notes: >
    RESOLVED 2026-06-01 at batch-51 — H_T-OD-6 RETIRE-READY → RETIRED-AS-BOUNDED-RESIDUAL (FIRST bounded-residual
    close in the ledger) per X-AL-2 §5.3. Condition-(B) audit: 4-OD-B SqliteWritePath substrate LANDED
    (U-OD-42..U-OD-45 / PR #18) but RuntimeRingBuffer.flush_to_sqlite is dormant at MVP (zero production callers;
    the collector→sqlite loop is not wired into the run path) → the boundary has not moved → substantive RETIRED
    is not honestly available at MVP (recording it would be silent-X-AL-3-absorption: a wired surface that is
    actually un-invoked). The must_pass above (ingestion exercised at a deployment) is exactly the residual:
    substantive RETIRED is gated on an operator deployment wiring the collector daemon (future milestone roadmap
    R-420/R-421, infra-gated). Operator-ratified AskUserQuestion 2026-06-01 (bounded-residual over
    keep-RETIRE-READY), a Class 2 in-execution decision per phase-7-substitution-retirement §5.3. Drains an
    R-700 blocker as bounded-residual. See .harness/phase-7d-retirement-events-batch-51.md §2 + ledger-v2 §11.4j.
```

### 5.3 MVP-operator-usable (R-100..R-199)

```yaml
R-100-mvp-operator-usable-cli-shipped:
  title: harness CLI end-to-end smoke — config load + workflow load + provider dispatch
  surface: II
  status: RESOLVED   # live green verified 2026-05-31 via operator-authorized `just run examples/minimal.toml`: EXIT=0, status=completed, 2 hash-chained ledger entries. PR #164.
  depends_on: []
  blocks: [R-001, R-004, R-100-mvp-real-workflow-execution]
  posture: phase-7
  scope: { files: [examples/**, harness.toml.example, .env.example, justfile, .gitignore], contracts: [C-RT-29, C-RT-30], cross_axis: no }
  skills: { primary: phase-7-implementation, secondary: [verify, run] }
  advisor_required: satisfied:2026-05-31   # advisor 2x this arc: don't fire the paid call / cross the .env boundary unilaterally (live green = operator's run); use recipe-passes-`--config` (option B) over a src default-discovery fix; substantiate the discovery gap before asserting it. Re-run only on a NEW cross-axis question.
  council_required: no
  verification: { shape: e2e, must_pass: ["`just run examples/minimal.toml` exits 0", "audit-ledger entry written to bound STATE_LEDGER (.harness/state.jsonl)", "non-empty LLM response observed at stdout"] }
  close_shape: { type: PR-merge, artifact: "mvp: harness CLI smoke + examples/minimal.toml workflow", cascade: [R-100-mvp-real-workflow-execution] }
  next_pointer: R-100-mvp-real-workflow-execution
  notes: >
    Builds on PRs #82-#86 + #84 CLI parent-app subcommand pattern. Use-the-product
    probe (workspace memory) is the discipline here, and it surfaced four gaps that
    block an operator running the smoke. Scaffolding + fixes shipped (branch
    r-100-mvp-cli-smoke): (1) examples/minimal.toml — operator-discoverable,
    dispatch-ready manifest (the buried test fixture lacked `messages`, so it could
    not dispatch); (2) examples/README.md quickstart; (3) harness.toml.example —
    path bindings aligned to pipeline-automation (matched the shipped example) + NEW
    [runtime.routing_manifest] with ≥1 fallback_chain (without it, stage 3b CP_ROUTING
    raises FallbackChainBindError) + corrected the false "discovers this file by
    default" header; (4) justfile `run`/`daemon` pass `--config harness.toml`
    (option B per advisor — zero src change); (5) `.gitignore` now ignores
    `harness.toml` (operator-local config with machine paths). Verified at config-load
    + dispatch-boundary (all stages pre-inference pass). Entry stays ACTIVE: the live
    green (the final paid inference dispatch) is the operator's `just run` with their
    own ANTHROPIC_API_KEY — a background agent does not fire the paid call / relocate
    secrets across the worktree boundary. Recipe-name drift fixed in must_pass
    (`just harness-run` → `just run`). Discovery gap (spec §3.7 auto-discovery
    unimplemented) split out to R-100-mvp-config-discovery — does not block this entry.

R-100-mvp-config-discovery:
  title: Implement spec §3.7 `harness.toml` auto-discovery at workspace root
  surface: II
  status: RESOLVED   # Reading A CWD discovery shipped at PR #279 (`a394032`); fork doc status refreshed 2026-06-06.
  depends_on: []
  blocks: []
  posture: phase-7
  scope: { files: [harness-runtime/src/harness_runtime/cli/**, harness-runtime/src/harness_runtime/config_source.py, design-substrate/Spec_Harness_Runtime_v1.md], contracts: [C-RT-30 §3.7, C-RT-29 §14.18.1], cross_axis: no }
  skills: { primary: phase-7-back-flow-routing, secondary: [phase-7-implementation] }
  advisor_required: yes
  council_required: no
  verification: { shape: integration, must_pass: ["with harness.toml at CWD and no --config, `harness run <manifest>` discovers it", "no-file case preserves env+CLI-only behavior", "dead DEFAULT_CONFIG_FILE_NAME constant wired or retired"] }
  close_shape: { type: PR-merge, artifact: "PR #279 `a394032` — fix: harness.toml default discovery per spec §3.7" }
  next_pointer: R-100-mvp-real-workflow-execution
  notes: >
    RESOLVED. The operator ratified `.harness/class_1_fork_harness_toml_default_discovery_unimplemented.md`
    Reading A (CWD discovery) on 2026-06-06; empirical grounding found the implementation had
    already shipped at PR #279 (`a394032`). `RuntimeConfigSource.load(config_file=None)` now
    discovers `Path.cwd() / DEFAULT_CONFIG_FILE_NAME` when present, preserves env+CLI-only
    behavior when absent, and lets explicit `--config` bypass discovery. Targeted verification
    on 2026-06-06: `uv run pytest harness-runtime/tests/test_config_source.py -q` -> 19 passed.
    No spec amendment is owed.

R-100-mvp-real-workflow-execution:
  title: Real multi-step workflow at SOLO_DEVELOPER tier against Anthropic provider
  surface: II
  status: RESOLVED   # 4 of 4 ACs PASS. AC #1 + #3 + #4 via test_r100_real_workflow_e2e.py (real Anthropic, prior operator-authorized runs; AC #4 cost fork RESOLVED-AS-INVALID 2026-06-01 test-bug). AC #2 (TOOL_STEP dispatch via api.run) CLOSED 2026-06-01 — test_r100_ac2_tool_step_e2e.py green via live local ollama (free, zero-token reachability ping; echo-MCP TOOL_STEP subprocess, not inference) after PR #181 fixed the test's ollama branch (ProviderFamily.OLLAMA → LOCAL_OPEN_WEIGHT). All 5 bootstrap gaps {B,C,D,E,F} wired at spec v1.41 §14.9.8 (PR #172).
  depends_on: [R-100-mvp-operator-usable-cli-shipped]
  blocks: [R-001, R-004, R-100-mvp-yaml-loader-shipped, R-300-multi-llm-second-provider]
  posture: phase-7
  scope: { files: [harness-runtime/tests/integration/**, examples/**], contracts: [], cross_axis: no }
  skills: { primary: phase-7-implementation, secondary: [verify, run] }
  advisor_required: satisfied:2026-05-31   # advisor reframed AC #4 to the landed per-dispatch cost: writes (not the U-OD-21-blocked RunResult aggregate) + cheap-tool-path bet. Re-run only on a NEW cross-axis question.
  council_required: no
  verification: { shape: e2e, must_pass: ["3+ step workflow executes", "tool dispatch surface exercised ≥1 site", "audit-ledger emits step-by-step entries", "cost-attribution entries present (landed per-dispatch cost: writes per U-OD-39/41 seam — NOT the U-OD-21-blocked RunResult.cost_attribution aggregate)"] }
  close_shape: { type: PR-merge, artifact: "mvp: 3-step real-workflow e2e against Anthropic", cascade: [] }
  next_pointer: R-001
  notes: >
    PARTIAL via PR (branch r-100-real-workflow-e2e): `test_r100_real_workflow_e2e.py`
    runs a real 3-step Anthropic INFERENCE workflow through api.run. **AC #1 ✓**
    (status=completed) + **AC #3 ✓** (3 hash-chained `workflow:...:step:N` ledger
    entries read from disk) verified by a live operator-authorized run. **AC #2 + #4
    gated on two forks the use-the-product probe surfaced:**
    (a) `class_1_fork_tool_step_no_operator_supplied_converter.md` (PROPOSING) —
    TOOL_STEP not dispatchable via api.run: no operator config surface for
    `tool_contract_converter`; the bootstrap host uses a default-that-raises. AC #2's
    surface IS exercised at the dispatcher level by `test_u_rt_86` (passing on main),
    but not inside an operator api.run workflow. → R-100-tool-step-converter.
    (b) `class_1_fork_llm_cost_attribution_not_firing_on_real_dispatch.md` (PROPOSING) —
    a real inference run emits ZERO `cost:` entries despite the wiring at
    llm_dispatch.py:517 + substrate bound at stage_5_loop_init.py:147-149. AC #4 is a
    runtime `pytest.xfail` in the test citing the fork (auto-converts to a regression
    guard once fixed). **Carries an OD-5 retirement-validity implication** (OD-5 was
    RETIRED on mech-β unit tests; production api.run emits no cost — the grep-vs-e2e
    gap). → R-100-cost-attribution-firing. The note's prior "Unblocks AS-8d + OD-5
    RETIRED transits" was stale — both already RETIRED at batches 31-32.

R-100-tool-step-converter:
  title: TOOL_STEP dispatchable via api.run — per-server default policy converter (Reading B)
  surface: II
  status: RESOLVED   # converter CONFIG SURFACE delivered at spec v1.40 (PR #171). This entry's scope is the config surface only; AC #2 e2e gate lives at R-100-tool-step-sandbox-resolver.
  depends_on: []
  blocks: []
  posture: design-phase   # mixed-posture bundled-absorption: runtime spec amendment + harness-runtime impl (per CLAUDE.md §11.4; needs clearance marker)
  scope: { files: [design-substrate/Spec_Harness_Runtime_v1.md, harness-runtime/src/harness_runtime/types.py, harness-runtime/src/harness_runtime/bootstrap/factories/mcp_client_host_factory.py, harness-runtime/tests/**, .harness/clearance/**], contracts: [C-RT-22, C-RT-30 §14.9.3], cross_axis: no }
  skills: { primary: spec-writer, secondary: [phase-7-implementation, verify] }
  advisor_required: conditional:if the MCPClientConfig field shape diverges from C-RT-22 §14.9.3
  council_required: no
  verification: { shape: unit, must_pass: ["MCPClientConfig carries default_minimum_tier + default_blast_radius — DONE", "materialize_mcp_client_host_stage builds a default-policy converter from them (unit-tested with a synthetic Tool) — DONE"] }   # scope narrowed to the converter CONFIG SURFACE; the api.run e2e gate moved to R-100-tool-step-sandbox-resolver (the converter is not even reachable through the bootstrap until host start() lands — see that entry).
  close_shape: { type: PR-merge, artifact: "feat: per-server default tool-contract policy — TOOL_STEP via api.run converter half (Reading B)" }
  next_pointer: R-100-tool-step-sandbox-resolver
  notes: >
    RESOLVED (converter CONFIG SURFACE) 2026-06-01 at PR #171 — spec v1.40 §14.9.3 stage-3a
    Reading B clause + MCPClientConfig +2 fields (default_minimum_tier / default_blast_radius)
    + mcp_client_host_factory._build_default_policy_converter + 5 converter unit tests +
    clearance marker `.harness/clearance/Spec_Harness_Runtime-v1_40-cleared-2026-06-01.md`.
    Field count +2 as ratified per fork §3 (NOT re-decided to +1 despite the pre-existing
    unconsumed `blast_radius` overlap — logged as Class 3 finding). 1344/1344 harness-runtime
    non-e2e tests pass; pyright strict + ruff clean.
    SCOPE = the converter config surface ONLY. This is one necessary piece of the api.run
    TOOL_STEP path, NOT the whole path. A pre-merge completeness critic (PR #171) found the
    converter is currently UNREACHABLE through the bootstrap because the stage-3a body never
    calls host.start() (registry empty → converter never runs); the 5 unit tests exercise the
    converter with a synthetic _FakeTool, not the path. The api.run e2e gate + the remaining
    gaps (B: host start(); C: sandbox_decision_resolver; D?: provider construction) live at
    R-100-tool-step-sandbox-resolver (the AC#2-closing arc). AC #2 closes there, by execution.

R-100-tool-step-sandbox-resolver:
  title: AC#2-closing arc — wire the full 5-gap bootstrap TOOL_STEP path {D,B,C,E,F} + echo-via-api.run e2e
  surface: II
  status: RESOLVED   # Reading B ratified + spec v1.41 §14.9.8 + all 5 gaps wired + 18 CI-green tests (PR #172). AC #2 CLOSED 2026-06-01 — the skipif-gated test_r100_ac2_tool_step_e2e.py ran green against a live LOCAL ollama daemon (Gap D constructible provider via a zero-token reachability ping; the dispatch is an echo-MCP TOOL_STEP, not inference — no paid call). PR #181 fixed the test's dead ollama branch (ProviderFamily.OLLAMA → LOCAL_OPEN_WEIGHT) that had blocked the free route; the Anthropic-key route was already viable. Self-verifiable locally for free; no operator-gated paid call required.
  depends_on: [R-100-tool-step-converter]
  blocks: []
  posture: design-phase   # NEW §14.9.x resolver contract (spec amendment) + 4 impl/config fixes + e2e; mixed-posture bundled-absorption
  scope: { files: [design-substrate/Spec_Harness_Runtime_v1.md, harness-runtime/src/harness_runtime/bootstrap/factories/runtime_tool_dispatcher_factory.py, harness-runtime/src/harness_runtime/lifecycle/runtime_tool_dispatcher.py, harness-runtime/src/harness_runtime/bootstrap/stage_3a_cp_clients.py, harness-runtime/src/harness_runtime/shutdown.py, harness-cp/src/harness_cp/mcp_client_namespace_emitter.py, harness-runtime/tests/**, .harness/clearance/**], contracts: [C-RT-19 §14.9.1, C-RT-30 §14.9.3 stage-3a + stage-5, NEW §14.9.x resolver contract], cross_axis: no }
  skills: { primary: phase-7-back-flow-routing, secondary: [spec-writer, phase-7-implementation, verify] }
  advisor_required: yes   # design-surface ratification for the resolver (NO §14.9.7 discretion escape — that cite is phantom; ratification + spec amendment required for BOTH Readings A and B)
  council_required: no
  verification: { shape: integration, must_pass: ["Gap D: bootstrap succeeds with a constructible provider (ANTHROPIC_API_KEY ping is non-inference / zero-token, OR live ollama) for a tool-only workflow", "Gap B: stage-3a calls host.start() when mcp_clients non-empty — DE-RISKED: all 6 bootstrap-going tests use mcp_clients=[] so the `if config.mcp_clients:` guard is safe", "Gap C: bootstrap-produced RuntimeToolDispatcher has a non-raising sandbox_decision_resolver per ratified Reading + NEW §14.9.x spec contract + phantom §14.9.7 cites at runtime_tool_dispatcher.py:85,:98 corrected", "Gap E: emitter info_lookup built from ctx.mcp_client_host (4 MCPServerInfo fields host-derivable)", "Gap F: host.shutdown() wired into shutdown.py step 4", "AC #2 e2e: a TOOL_STEP completes through api.run end-to-end (echo MCP) BY EXECUTION — skipif-gated (live-green is operator's run per Gap D)", "xfail marker at test_u_rt_75::test_ac2_bootstrap_dispatcher_resolves_sandbox_decision removed (xpass → strict-fail forces it)"] }
  close_shape: { type: PR-merge, artifact: "feat: wire full bootstrap TOOL_STEP path {D,B,C,E,F} — closes R-100 AC #2 by e2e" }
  next_pointer: R-001
  notes: >
    THE AC#2-CLOSING ARC. AC #2 closes only when the FULL bootstrap TOOL_STEP path is wired
    AND demonstrated end-to-end (echo MCP via api.run). EXECUTION-CONFIRMED gap set is FIVE,
    not three (the "converter + resolver" model undercounted twice; a scratch run wired all
    five + completed a real TOOL_STEP) — see fork §4 table. Ordered by firing point:
    - Gap D (config-around): providers.py raises ProviderNoneConfiguredError if zero providers
      (unconditional, step-kind-blind). e2e needs ≥1 constructible provider → it CANNOT be
      CI-green under config-around (skipif-gated; live-green is operator's run). A heavier
      alternative — inference-step-gate provider construction so tool-only workflows bootstrap
      with zero providers — is its OWN design decision (changes a bootstrap invariant + needs a
      stage-5 llm_dispatch:998 carve-out); surfaced as a conditional 2nd AskUserQuestion.
    - Gap B (impl, spec-conformant): stage_3a_cp_clients.py:48 never calls host.start(); §14.9.6
      inv 1 mandates it. DE-RISKED: all 6 bootstrap-going tests use mcp_clients=[] → empty-
      sentinel → `if config.mcp_clients: await host.start()` is safe. Flag: stage_3a docstring
      "only network-I/O stage" tension with spec's stage-3a spawn; confirm eager-start in-arc.
    - Gap C (THE DESIGN DECISION; fork PROPOSING): bootstrap wires no sandbox_decision_resolver
      (defaults-to-raise at runtime_tool_dispatcher.py:449). The §14.9.7 "implementer-discretion"
      escape is PHANTOM (verified — §14.9.7 covers only emitter/idempotency/health-check; the
      resolver has zero spec anchor). So ratification is required, AND a spec amendment authoring
      NEW §14.9.x (SandboxDispatchDecision + SandboxDecisionResolver) is required for BOTH
      Readings — Reading A is NOT impl-only. Readings: (A) identity resolver (tier=minimum_tier;
      no new config; RECOMMENDED) — tradeoffs: makes the floor vacuous + can overstate isolation
      in telemetry (sandbox.enter span; ship a "default_minimum_tier must reflect real mechanism"
      note); (B) per-server sandbox-mechanism fields (meaningful floor; bigger config surface);
      (C) defer (rejected). Also fix the phantom §14.9.7 cites at runtime_tool_dispatcher.py:85,:98.
    - Gap E (impl-wiring): factory:109 MCPClientNamespaceEmitter() bare → step-7 LookupError.
      Build info_lookup from ctx.mcp_client_host (health_check builds all 4 MCPServerInfo fields).
    - Gap F (impl-wiring): host.shutdown() never wired → teardown anyio error. Wire into
      shutdown.py step 4 (same-task as run_bootstrap per api.py:449→509). §14.9.6 inv 1 mandates.
    Gap G (NOT AC#2 — AC#4 cost only): RATE_TABLE_V1.tool_rates=={} → add echo/default rate if
    AC#4 bundled; secondary doc-drift at rate_table_v1.py:87-92 (mis-cites §C-OD-28.2 zero-fallback;
    canonical default is fail-closed=raise per OD spec v1.8 §C-OD-28:257).
    NEW Gap D-1 (latent, NOT AC#2): config/loader.py _ENV_SCALAR_FIELDS omits anthropic_optional/
    openai_optional → HARNESS_*_OPTIONAL env vars ignored on api.run(config=None); route separately.
    All five {D,B,C,E,F} land in ONE PR; the e2e is the only artifact that proves the path complete.
    U-RT-86 already proves the dispatcher-level chain given a started host + B+C+E hand-supplied.

R-100-cost-attribution-firing:
  title: Per-dispatch cost-attribution fires on the real api.run inference path
  surface: II
  status: RESOLVED   # RESOLVED-AS-INVALID 2026-06-01 — was a test-observation bug, not a defect. Cost-attribution fires + writes (WriteResult.APPENDED ×3). OD-5 retirement valid.
  depends_on: []
  blocks: []
  posture: phase-7
  scope: { files: [harness-runtime/tests/integration/**], contracts: [], cross_axis: no }
  skills: { primary: phase-7-implementation, secondary: [] }
  advisor_required: no
  council_required: no
  verification: { shape: e2e, must_pass: ["a real inference run writes ≥1 audit-thread cost-attribution entry per dispatch", "test_r100_real_workflow_e2e.py AC #4 passes"] }
  close_shape: { type: PR-merge, artifact: "fix: R-100 AC #4 test-observation bug + close cost fork as INVALID" }
  next_pointer: R-001
  notes: >
    RESOLVED-AS-INVALID 2026-06-01 at fork-ratification grounding. The fork
    `.harness/class_1_fork_llm_cost_attribution_not_firing_on_real_dispatch.md` is
    WITHDRAWN: cost-attribution DOES fire + write on the real api.run path
    (instrumentation: `_attribute_cost_best_effort` entered ×3, usage present,
    `audit_writer.append` → WriteResult.APPENDED ×3). The "zero cost: entries" was a
    test-observation bug — `RuntimeAuditLedgerWriter` writes the OD cost entry under the
    audit thread as an `audit:<tenant>:<hash>` state-ledger entry (the `cost:` action_id
    is in the hashed `payload`, not the state-ledger action_id). AC #4 in
    test_r100_real_workflow_e2e.py corrected to assert ≥1 `audit:` entry per dispatch;
    test now PASSES. **OD-5 retirement (batch-32) is VALID** — the retirement-validity
    concern is withdrawn. Discipline lesson: verify the observation layer/sink before
    concluding a defect.

R-100-mvp-yaml-loader-shipped:
  title: YAML manifest loader operational (close Class 1 forks PR #79 / PR #80 lineage)
  surface: II
  status: RESOLVED   # 2026-06-01: dep R-100-mvp-real-workflow-execution RESOLVED → unblocked. Both verification criteria green at the Claude-executable/CI level in test_track_b_e2e.py: must_pass[1] (round-trip YAML↔TOML byte-equivalent payload) via test_ac2_yaml_and_toml_manifests_produce_equivalent_loaded_workflow — strengthened to assert step_payload byte-equality + native int max_tokens=8 (the v1.39 StrictSafeLoader parity); must_pass[0] (YAML loads + dispatches identically to TOML) via NEW test_ac2_loaded_yaml_and_toml_dispatch_identically_deterministic — loads both fixtures and runs each through the real bootstrap + execute_workflow with a deterministic dispatcher (no key/ollama/daemon, CI-runnable) → both reach identical SUCCESS. No paid call.
  depends_on: [R-100-mvp-real-workflow-execution]
  blocks: [R-100-mvp-multi-workflow-fixture-suite]
  posture: phase-7
  scope: { files: [harness-runtime/src/harness_runtime/lifecycle/strict_safe_loader.py, harness-runtime/tests/**], contracts: [C-RT-30 §14.19], cross_axis: no }
  skills: { primary: phase-7-implementation, secondary: [verify] }
  advisor_required: conditional:if loader-spec surface diverges from v1.39
  council_required: no
  verification: { shape: e2e, must_pass: ["YAML fixture loads and dispatches identically to TOML equivalent", "round-trip YAML↔TOML byte-equivalent payload"] }
  close_shape: { type: PR-merge, artifact: "mvp: YAML loader operational; PR #79 + PR #80 resolved", cascade: [] }
  next_pointer: R-100-mvp-multi-workflow-fixture-suite
  notes: Per runtime spec v1.39 Reading A apply; integration testing now first-class.

R-100-mvp-multi-workflow-fixture-suite:
  title: Workflow fixture suite covering all 6 topology patterns
  surface: II
  status: RESOLVED   # 2026-06-01: dep R-100-mvp-yaml-loader-shipped RESOLVED → unblocked. 6 operator-facing example manifests at examples/workflows/topology/*.yaml — one per TopologyPattern — each a parent workflow with a sub-agent-dispatch step whose child manifest declares that pattern paired with an admissible workload (single-threaded-linear↔pipeline-automation, orchestrator-workers↔research, decentralized-handoff↔pipeline-automation, hierarchical-delegation↔software-engineering, evaluator-optimizer↔content-creation, parallelization↔research). Integration suite harness-runtime/tests/integration/test_topology_fixture_suite.py (26 tests) loads each via the real WorkflowManifestLoader and runs each parent fixture through the CP execute_workflow DRIVER LOOP to a terminal RunStatus.SUCCESS (driver-level e2e; mirror of test_track_b_e2e mech-α: real run_bootstrap + faked provider/OD stages; child sub-agent is a deterministic stand-in so the gate fires for real), deterministically (no key/ollama/daemon — CI-runnable per CI `not e2e` selector). must_pass green: [0] all 6 execute end-to-end through the driver to SUCCESS; [1] is_topology_permitted gate fires per pattern + topology.pattern/topology.workload_class span attrs; [2] ≥1 OD audit-ledger entry per dispatch. Plus completeness guard (all 6 patterns covered) + negative admissibility test (parallelization+pipeline-automation raises SubAgentDispatchTopologyInadmissibleError) + per-fixture load/model_validate coverage. HONESTY CAVEAT: topology has NO distinct per-pattern orchestration at MVP (dispatch is a stateless passthrough emitting telemetry); this suite is regression coverage of the PER_WORKLOAD_CLASS_TOPOLOGY admissibility matrix + dispatch-composer + telemetry, NOT distinct orchestration semantics (unbuilt; CP-axis contract work — Class 1 back-flow, out of this entry's contracts:[] cross_axis:no fences). 26 passed; ruff+pyright clean. Phase-7; roadmap §5.
  depends_on: [R-100-mvp-yaml-loader-shipped]
  blocks: [R-400-multi-deployment-self-hosted-server]
  posture: phase-7
  scope: { files: [examples/workflows/**, harness-runtime/tests/integration/**], contracts: [], cross_axis: no }
  skills: { primary: phase-7-implementation, secondary: [verify] }
  advisor_required: no
  council_required: conditional:nameable-tension
  verification: { shape: e2e, must_pass: ["6 fixture workflows execute end-to-end", "each fixture exercises ≥1 topology pattern", "audit-ledger emits expected lifecycle events per fixture"] }
  close_shape: { type: PR-merge, artifact: "mvp: 6-topology fixture suite", cascade: [] }
  next_pointer: R-400-multi-deployment-self-hosted-server
  notes: >
    RESOLVED 2026-06-01. MVP materializes no per-pattern orchestration — the
    suite proves admissibility-matrix + dispatch-composer + telemetry coverage
    for all 6 patterns via deterministic sub-agent dispatch. Distinct
    orchestration semantics (true fan-out for parallelization, generator/
    evaluator loop for evaluator-optimizer, etc.) remain unbuilt and are
    CP-axis contract work routed via Class 1 back-flow when scheduled.
```

### 5.4 CI substrate (R-200..R-299)

```yaml
R-200-ci-pytest-pyright-ruff-matrix:
  title: GitHub Actions workflow — pytest + pyright + ruff matrix at PR open
  surface: III
  status: RESOLVED   # PR #144 squash-merged `f06c30a` 2026-05-31; CI run green overall
  depends_on: []
  blocks: [R-200-ci-coverage-gating, R-200-ci-axis-matrix]
  posture: mode-agnostic
  scope: { files: [.github/workflows/ci.yml, pyproject.toml], contracts: [], cross_axis: no }
  skills: { primary: phase-7-implementation, secondary: [] }
  advisor_required: no
  council_required: no
  verification: { shape: integration, must_pass: ["CI runs on every PR open + push", "all 5 axis packages tested", "pyright strict passes", "ruff check passes"] }
  close_shape: { type: PR-merge, artifact: "ci: pytest + pyright + ruff matrix", cascade: [] }
  next_pointer: R-200-ci-axis-matrix
  notes: >
    RESOLVED 2026-05-31 at PR #144 merge `f06c30a` (.github/workflows/ci.yml). 3 jobs on PR + push-to-main
    via astral-sh/setup-uv@v5 + Python 3.12 + `uv sync --all-packages`: `test` (`uv run pytest -m "not e2e"`)
    BLOCKING and green (3543 passed / 7 skipped); `lint` (ruff check + format-check) + `typecheck` (pyright strict)
    ADVISORY (continue-on-error) at v1. ADVISORY because the tree is NOT lint/type-clean — `ruff check .` = 366,
    `pyright` = 894 (even src-only: ruff 112, pyright 186, incl. a real dup-`Skill`-type bug at
    harness-runtime/.../types.py:1683). Making them blocking on day one = permanently-red CI. Tightening tracked at
    R-200-ci-lint-typecheck-blocking. next_pointer R-200-ci-axis-matrix.

R-200-ci-axis-matrix:
  title: Per-axis test isolation matrix
  surface: III
  status: RESOLVED   # PR #147 — axis-isolation matrix added to ci.yml
  depends_on: [R-200-ci-pytest-pyright-ruff-matrix]
  blocks: []
  posture: mode-agnostic
  scope: { files: [.github/workflows/ci.yml], contracts: [], cross_axis: no }
  skills: { primary: phase-7-implementation, secondary: [] }
  advisor_required: no
  council_required: no
  verification: { shape: integration, must_pass: ["each axis runs in isolation (no harness-cp leak into harness-is run)", "matrix completes in <10min"] }
  close_shape: { type: PR-merge, artifact: "ci: per-axis isolation matrix", cascade: [] }
  next_pointer: R-200-ci-od-cp-dependency-leak
  notes: >
    RESOLVED at PR #147. NEW `axis-isolation` matrix job in `.github/workflows/ci.yml`:
    6 legs (core / is / as / cp / od / cxa), `fail-fast: false`. Each leg `uv sync --package
    harness-<axis>` (installs only that package + its DECLARED workspace deps; uv prunes
    siblings), layers `pytest`+`pytest-asyncio` via `uv pip install` (the root `dev` group is
    not pulled by `--package`; neither tool depends on a harness axis so isolation holds), then
    `uv run --no-sync pytest harness-<axis>/tests -m "not e2e"`. A test or src module importing
    an undeclared sibling axis fails to import — the leak the all-packages `test` job masks.
    harness-runtime omitted (depends on every axis → its isolation == the all-packages `test`
    job). Empirically verified at authoring: core 26 / is 133 / as 317 / cp 813 / cxa 28 PASS in
    isolation; **od RED** — undeclared od->cp dependency at
    `harness-od/src/harness_od/pause_resume_namespace.py:295` (`from harness_cp.pause_resume_protocol
    import ...`) + 4 od test modules import harness_cp while harness-od declares only core+as.
    Posture: 5 clean legs BLOCKING (catch NEW leaks); `od` leg ADVISORY via
    `continue-on-error: ${{ matrix.axis == 'od' }}`. Each leg installs/tests a single small
    package subset in parallel → well under the <10min budget. od fix tracked at
    R-200-ci-od-cp-dependency-leak.

R-200-ci-od-cp-dependency-leak:
  title: Resolve the undeclared harness-od -> harness-cp dependency, then make the od isolation leg blocking
  surface: III
  status: RESOLVED   # surfaced by the axis-isolation matrix (PR #147); closed via option (a)
  depends_on: [R-200-ci-axis-matrix]
  blocks: []
  posture: phase-7   # build-metadata + ci.yml (no src/test relocation needed) — design call on the dep graph
  scope: { files: [harness-od/pyproject.toml, harness-od/src/**, harness-od/tests/**, .github/workflows/ci.yml], contracts: [], cross_axis: yes }
  skills: { primary: phase-7-back-flow-routing, secondary: [phase-7-implementation] }
  advisor_required: yes   # cross-axis dependency-graph change; may be a Class 3 cross-axis-import-drift fork
  council_required: no
  verification: { shape: integration, must_pass: ["harness-od tests pass under `uv sync --package harness-od` isolation", "od leg drops the continue-on-error carve-out in ci.yml", "no new dependency cycle (cp must not depend on od)"] }
  close_shape: { type: PR-merge, artifact: "fix(od): declare harness-cp dependency / relocate CP->OD seam; flip od isolation leg blocking", cascade: [] }
  next_pointer: null
  notes: >
    RESOLVED 2026-05-31 via option (a) — declare the deps. CORRECTED DIRECTION ANALYSIS (advisor 2026-05-31):
    harness-od -> harness-cp is the CANONICAL OD->CP consumer direction (CXA v2.18 §2.3.3, 12 edges; OD ingests
    CP-emitted namespaces incl. `engine.*`), NOT a reverse-direction drift — the "relocate the seam" framing was
    mistaken. The forcing consumer is `ReplayDisposition` (harness_cp.engine_namespace) read READ-ONLY at
    idempotency_join_dedup.py (live; fans out to cost_namespace/cross_family_rollup/runtime cost-attribution) —
    not relocatable (OD-internal C-OD-08 logic; re-homing the enum violates CP axis-ownership). Broadened grep
    also surfaced a 2nd undeclared dep a cp-only grep would miss: od tests import `harness_is`
    (state_ledger_entry_schema) — canonical OD->IS (§2.3.4). harness-od now declares harness-cp + harness-is in
    [project.dependencies] + [tool.uv.sources]; both acyclic-safe (cp deps={core,as}; is deps={core}; neither
    depends on od; reverse CP->OD audit seam §2.3.7 is mediated via harness-cxa, no direct cp->od import).
    Verified green in isolation: `uv sync --package harness-od && pytest harness-od/tests -m "not e2e"` = 887 passed.
    `continue-on-error: ${{ matrix.axis == 'od' }}` dropped from ci.yml — full 6-leg matrix now blocks. Direction
    analysis + re-home-to-core future-hygiene alternative recorded at .harness/class_3_drift_od_cp_undeclared_dependency.md.

R-200-ci-coverage-gating:
  title: Coverage gating at PR (informational at first; enforce later)
  surface: III
  status: RESOLVED   # PR #150 `5d06106` — advisory coverage job + pytest-cov
  depends_on: [R-200-ci-pytest-pyright-ruff-matrix]
  blocks: []
  posture: mode-agnostic
  scope: { files: [.github/workflows/ci.yml, pyproject.toml], contracts: [], cross_axis: no }
  skills: { primary: phase-7-implementation, secondary: [] }
  advisor_required: no
  council_required: no
  verification: { shape: integration, must_pass: ["coverage report uploaded to PR", "trend visible across last 5 PRs"] }
  close_shape: { type: PR-merge, artifact: "ci: coverage reporting", cascade: [] }
  next_pointer: null
  notes: >
    RESOLVED 2026-05-31 at PR #150 merge `5d06106`. NEW advisory `coverage` job in `ci.yml`
    (continue-on-error) + `pytest-cov>=6.0` in dev group + `[tool.coverage.run]` (branch=true,
    source = 7 import packages, tests omitted). Runs the non-e2e suite under coverage, publishes
    total line/branch coverage to the job step-summary (visible on the PR Checks tab), uploads
    coverage.xml as an artifact. CI-verified: coverage job PASSED + coverage-xml artifact (36KB)
    uploaded at the PR #150 run. v1 = informational, NO `fail_under` threshold ("gather data
    first"); cross-PR trend via codecov/badge + a threshold are a future tightening (mirrors the
    lint/typecheck advisory-until-justified stance). Per must_pass row 2, true cross-PR trend
    needs a service — deferred; per-run step-summary + artifact is the v1 informational surface.

R-200-ci-lint-typecheck-blocking:
  title: Drive the tree ruff/pyright-clean, then flip CI lint + typecheck from advisory to blocking
  surface: III
  status: RESOLVED
  resolved_at: "PR #161 (d904055) 2026-05-31 — pyright half: 846 → 0; typecheck job flipped blocking (renamed `pyright (strict) — blocking`); verified green-as-blocking in CI alongside all 6 axis-isolation legs. Lint half was PR #159. BOTH lint + typecheck now blocking; surface III CI substrate gate complete."
  depends_on: [R-200-ci-pytest-pyright-ruff-matrix]
  blocks: []
  posture: phase-7
  scope: { files: [harness-*/**, tests/**, .github/workflows/ci.yml], contracts: [], cross_axis: no }
  skills: { primary: phase-7-implementation, secondary: [verify] }
  advisor_required: conditional:if a fix touches a cross-axis contract or production type
  council_required: no
  verification: { shape: integration, must_pass: ["uv run ruff check . exits 0", "uv run ruff format --check . exits 0", "uv run pyright exits 0 (strict, tree-wide)", "ci.yml lint + typecheck jobs drop continue-on-error"] }
  close_shape: { type: PR-merge, artifact: "ci: lint + typecheck blocking (tree clean)", cascade: [R-IF-roadmap-refresh] }
  next_pointer: R-200-ci-axis-matrix
  notes: >
    Authored at the R-200-ci-pytest close (PR #144). CI shipped lint/typecheck ADVISORY because the tree is dirty:
    `ruff check .` = 366 (≈222 `--fix`-able), `pyright` = 894; src-only ruff 112 / pyright 186, INCLUDING a genuine
    production bug — two distinct `Skill` classes (`harness_runtime.types.Skill` vs `harness_runtime.lifecycle.skills.Skill`)
    at harness-runtime/src/harness_runtime/types.py:1683 (reportArgumentType). Likely multi-PR: (a) `ruff check --fix`
    + format sweep; (b) pyright cleanup incl. the Skill dedup; (c) flip continue-on-error -> false. Mostly test-module noise.

R-200-session-start-audit-hook:
  title: SessionStart hook automating CLAUDE.md §12.1 audit at every Claude Code session open
  surface: III
  status: RESOLVED
  depends_on: []
  blocks: []
  posture: mode-agnostic
  scope:
    files: [.claude/settings.json, tools/roadmap-audit/session-start.sh]
    contracts: []
    cross_axis: no
  skills: { primary: null, secondary: [] }
  advisor_required: no
  council_required: no
  verification:
    shape: integration
    must_pass:
      - "Hook registered at .claude/settings.json (project-shared; ${CLAUDE_PROJECT_DIR} placeholder for portability)"
      - "Script computes workspace_state_hash per §12.1 step 2 recipe"
      - "Script handles 3 cases: match (~13 tokens), lag-expected via §12.2.1 carve-out (~19 tokens), drift (~25 tokens)"
      - "Script outputs valid JSON with hookSpecificOutput.additionalContext field per Claude Code SessionStart protocol"
      - "Script always exits 0 (failure encoded in additionalContext, never silent skip)"
      - "Token budget: all 3 output cases under 30 tokens to honor operator-stated context-optimization constraint"
  close_shape:
    type: PR-merge
    artifact: "ops: SessionStart audit hook + tools/roadmap-audit/session-start.sh"
    cascade: []
  next_pointer: null
  notes: |
    Closes the enforcement-layer gap surfaced at the dashboard-discipline conversation 2026-05-31.
    v1 shipped the discipline + data + recipes; v1.2 (this entry) ships the automation that
    makes §12.1 fire automatically without operator prompting.

    Token-optimization design constraint (operator AskUserQuestion 2026-05-31):
    - Match case: "[ROADMAP] hash=ok next=R-IF-108 in_flight=4 forks=39" = ~13 tokens
    - Lag case (post-refresh fixed-point per §12.2.1): "[ROADMAP] hash=lag-expected next=R-IF-108 (post-refresh fixed-point §12.2.1)" = ~19 tokens
    - Drift case: "[ROADMAP DRIFT] dashboard=AAAA computed=BBBB next=R-IF-108 action=§12.3" = ~25 tokens

    Hook output is JSON-wrapped per Claude Code's stdout-injection protocol (jq builds
    additionalContext field); Claude sees the additionalContext as a system message
    BEFORE the operator's first message reaches it.

    NEW pattern candidate: [[enforcement-layer-vs-discipline-layer]] — codifying a rule in
    a doc (discipline layer) is necessary but not sufficient; automation that fires the
    rule at the right time (enforcement layer) is required for genuine self-application.
    Mirror precedent: §12.2.1 codification at PR #114 was discipline-layer; this hook is
    the enforcement-layer companion. Cardinality 1; awaits second instance.
```

### 5.5 Multi-deployment surfaces (R-400..R-499)

Decomposition authored 2026-06-01 (triggered by `R-100-mvp-multi-workflow-fixture-suite` closure at PR #190 per §9). **Honest scope split** (grounded by empirical HEAD survey 2026-06-01): the harness models 3 deployment surfaces (`LOCAL_DEVELOPMENT` → `SELF_HOSTED_SERVER` → `MANAGED_CLOUD` at `harness-core/.../deployment_surface.py:26`) and a 4-tier sandbox model (`SandboxTier` + `BlastRadiusTier` + 6-class `SandboxProviderClass` + 12-cell `deployment_matrix.py` per ADR-D2 v1.2 / ADR-F4 v1.1). The sandbox tier model is **real at the policy + observability layer** (tier-floor `SandboxTierFloorViolationError` raised at `runtime_tool_dispatcher.py:455`; `sandbox.enter/exit/violation` span emission; operator-supplied `SandboxDecisionResolver`) but **execution is metadata-only** — no code path spins up a container / microVM / VM; tool calls always run in-process via FastMCP stdio (`mcp_client_host.py call_tool`). The OD deployment-conditional emission (per-cell sampler base-rate envelope; tail-keep wrap-iff-not-LOCAL; persona-tier redaction) is **deployed + LOCAL-testable at the materializer layer**, but the tail-keep *preservation* + multi-tenant *segregation* semantics live at a real OTLP collector (infra-gated). Net: **exactly one row (R-400) is Claude-executable at LOCAL_DEVELOPMENT**; the rest are live/infra-gated (real container runtime, real server, real collector, real cloud secrets backend) and PROPOSED pending operator infra provisioning.

```yaml
R-400-deployment-surface-conditional-emission-suite:
  title: Cross-surface deployment-conditional OD-emission integration suite (LOCAL / SELF_HOSTED / MANAGED)
  surface: V
  status: RESOLVED
  depends_on: []
  blocks: []
  posture: phase-7   # edits harness-runtime/tests (+ possibly harness-od/tests); deterministic, CI-runnable
  scope: { files: [harness-runtime/tests/**, harness-od/tests/**], contracts: [C-OD-09 §9.1, C-OD-10 §10.3, C-OD-13 §13.1], cross_axis: no }
  skills: { primary: phase-7-implementation, secondary: [verify] }
  advisor_required: no
  council_required: no
  verification:
    shape: integration
    must_pass:
      - "For each of the 3 DeploymentSurface members, materialize_tracer_provider_stage(RuntimeConfig(deployment_surface=X, persona_tier=Y)) resolves sampler base_rate == PER_CELL_BASE_RATE_ENVELOPE[CellID(Y, X)].default_rate"
      - "materialize_span_processor_stage wraps TailKeepSpanProcessor IFF deployment_surface != LOCAL_DEVELOPMENT (bypassed at LOCAL per §9.1 head-based mandate)"
      - "RedactionSpanProcessor present at all 3 surfaces; per-persona toggle resolves per §13.1"
      - "deterministic; no key / ollama / daemon / real collector; CI-runnable under the not-e2e marker"
  close_shape: { type: PR-merge, artifact: "test(od): cross-surface deployment-conditional emission integration suite", cascade: [] }
  next_pointer: null   # surface-V remainder is infra-gated; §4 re-derives (likely §IV multi-LLM decomposition or §VII cadence)
  notes: >
    The one CI-runnable Surface-V row. Consolidates 3 deployment-conditional OD behaviors (sampler envelope
    + tail-keep conditional + redaction) into ONE materializer-layer regression across all 3 surfaces. Honest
    caveat: unit coverage of each behavior exists in isolation (test_base_rate_set_and_envelope.py /
    test_redaction_gradient.py / tail-keep tests); the gap closed is the *composed cross-surface* assertion
    driven through the real materialize stages. ZERO src change expected; mirror the #190 deterministic-suite shape.
    RESOLVED at PR #194 merge `18b2d5d` (2026-06-01). `test_cross_surface_emission_suite.py` (17 tests) drives all
    four must_pass through the real stage-4 composers: sampler base_rate == envelope default_rate for every ACTIVE
    cell (8 = 3x3 minus EXCLUDED, read back via ParentBased._root.base_rate — no public .root, verified empirically);
    tail-keep wrapped IFF non-LOCAL; RedactionSpanProcessor present + persona threads at all 3 surfaces; plus a
    negative case (EXCLUDED multi-tenant×local-development raises TracerProviderBindError wrapping CellBindingViolation,
    mirroring #190's negative test). Honest MVP caveat banked: the §13.1 per-persona behavioral toggle is plumbed-not-
    consumed at the SDK boundary — that differential lives in test_redaction_gradient.py (cited in the suite docstring).
    ZERO src change; full integration dir 161 passed/10 skipped; ruff+pyright+pytest CI all GREEN. §V multi-deployment
    remainder now starts at R-411/R-420 after R-410's local Docker provider slice; §IV multi-LLM still decomposition-owed (its trigger
    R-100-mvp-real-workflow-execution is the operator-gated live e2e, not yet closed) — §4 re-derives to §VII cadence.

R-410-sandbox-tier-2-container-execution:
  title: Real TIER_2_CONTAINER sandbox execution — tool calls run in an isolated container, not in-process FastMCP
  surface: V
  status: RESOLVED   # this PR: local-only Docker driver + live TIER_2 TOOL_STEP e2e make the tier executable
  depends_on: []
  blocks: [R-411-sandbox-tier-3-microvm-execution]
  posture: phase-7
  scope: { files: [harness-runtime/src/harness_runtime/lifecycle/**, harness-as/src/**], contracts: [C-AS-15 §15, runtime spec v1.41 §14.9.8 (sandbox-decision-resolver; no C-RT-NN ID)], cross_axis: yes }
  skills: { primary: phase-7-implementation, secondary: [phase-7-back-flow-routing] }
  advisor_required: yes   # the SandboxDecisionResolver returns a tier decision but NO code path enforces isolation today; wiring real execution likely surfaces a Class 1 spec gap (execution-driver contract is unspecified)
  council_required: conditional:nameable-tension   # C10 (action-safety / blast-radius wants real isolation) vs C11 (operator-loop / local-deployment wants minimal provisioning burden)
  verification: { shape: e2e, must_pass: ["a TOOL_STEP resolved to TIER_2_CONTAINER actually executes inside a container boundary (verifiable FS/network isolation)", "tier-floor still raises on under-tier resolution", "sandbox.enter/exit spans carry the real provider/tech"] }
  close_shape: { type: PR-merge, artifact: "feat(sandbox): TIER_2 container execution provider", cascade: [R-411-sandbox-tier-3-microvm-execution] }
  next_pointer: R-411-sandbox-tier-3-microvm-execution
  notes: >
    RESOLVED by the local Docker execution-provider slice. The dispatcher now delegates post-policy tool execution
    through a `ToolExecutionDriver` seam: the default `MCPHostToolExecutionDriver` preserves prior in-process FastMCP
    behavior, while `DockerToolRunnerExecutionDriver` requires `TIER_2_CONTAINER`, resolves the configured image via
    local `docker inspect`, runs the immutable image id with `--network none`, and exchanges one JSON request/response
    over stdin/stdout. The live R-410 e2e uses an operator-provided local Docker runtime + local `python:3.11-slim`
    image only (no pull, no credentials, no paid provider call): a TOOL_STEP resolved to TIER_2 returns from inside the
    container, confirms outbound network is blocked, and confirms the host worktree path is not visible. Existing
    dispatcher tests continue to cover tier-floor rejection and sandbox.enter/exit provider/tech span attribution.
    Bootstrap/config selection for a production provider registry can be a future hardening slice; the roadmap's first
    executable TIER_2 container boundary is now built, and R-411/R-412 inherit the driver pattern as provider-class
    extensions rather than a new execution-contract fork.

R-411-sandbox-tier-3-microvm-execution:
  title: Real TIER_3 microVM sandbox execution (gVisor / Kata / shared-kernel container)
  surface: V
  status: RESOLVED   # closed by Docker + gVisor/runsc ToolExecutionDriver on the provisioned Linux VM
  depends_on: [R-410-sandbox-tier-2-container-execution]
  blocks: [R-412-sandbox-tier-4-full-vm-execution]
  posture: phase-7
  scope: { files: [harness-runtime/src/**, harness-as/src/**], contracts: [C-AS-15 §15], cross_axis: yes }
  skills: { primary: phase-7-implementation, secondary: [] }
  advisor_required: yes
  council_required: conditional:nameable-tension
  verification: { shape: e2e, must_pass: ["TIER_3-resolved TOOL_STEP executes under a microVM/gVisor boundary", "EXTERNAL_REVERSIBLE blast-radius enforced"] }
  close_shape: { type: PR-merge, artifact: "feat(sandbox): TIER_3 gVisor/runsc execution provider", cascade: [R-412-sandbox-tier-4-full-vm-execution] }
  next_pointer: R-412-sandbox-tier-4-full-vm-execution
  notes: >
    Extends R-410 up the tier ladder. Inherits the same execution-driver contract question; once R-410 settles the
    pattern, R-411 + R-412 are provider-class additions (CONTAINER -> gVisor/Kata at TIER_3 per deployment_matrix.py).
    Host-readiness prep now distinguishes the R-411 provider path from Firecracker: `r411-gvisor` points at
    `google/gvisor` (`runsc` + Docker), and `r411-kata` points at `kata-containers/kata-containers`
    (`kata-runtime`, with KVM access for the VM-backed path). `r411-shuru` (`superhq-ai/shuru`) and
    `r411-microsandbox` (`superradcompany/microsandbox`) are local-first microVM candidates worth evaluating on
    compatible hosts; both require Apple Silicon on macOS, while their Linux paths require KVM. `r411-libkrun`
    (`containers/libkrun`) is now tracked as an embeddable virtualization/process-isolation substrate candidate:
    Linux requires KVM, macOS requires Apple Silicon/HVF, and the upstream security model means host OS isolation
    around the VMM remains part of any implementation. Firecracker and QEMU `microvm` belong to R-412. `mvm-sh/mvm`
    was reviewed and intentionally not registered as a sandbox provider: it is a Go bytecode VM/interpreter, not
    an OS/hardware isolation runtime for arbitrary TOOL_STEP execution. `just sandbox-host-check <provider>` is
    the non-mutating probe for the exact runtime boundary before opening the provider implementation. The 2026-06-07
    NotebookLM + official-source infrastructure selection is recorded at
    `deploy/managed-cloud/r411-r421-infrastructure-selection.md`: first no-taxonomy-change R-411 recommendation is
    Linux + Docker + gVisor/runsc; Kata is the stronger follow-on when Linux KVM is available. The operator
    provisioned that compatible Linux host abstraction as a Lima Ubuntu VM on the external SSD, and this row is now
    closed by `GVisorRunscToolRunnerExecutionDriver` plus `just r411-gvisor-live-e2e` targeting the VM rootful Docker
    daemon with `R411_GVISOR_DOCKER_COMMAND`. The live proof passed: R-411 host readiness reported `ready: yes`; a
    TOOL_STEP resolved at `tier-3-microvm` executed under Docker `--runtime=runsc`; network egress was blocked with
    `--network=none`; and the host repo path was not visible from the sandbox. E2B remains a managed/remote
    R-421/R-412 candidate, not the local R-411 closure path.

R-412-sandbox-tier-4-full-vm-execution:
  title: Real TIER_4 full-VM / firecracker sandbox execution (MANAGED_CLOUD-only provider class)
  surface: V
  status: RESOLVED   # closed by the managed E2B full-VM ToolExecutionDriver + live Tier-4 dispatcher e2e
  depends_on: [R-411-sandbox-tier-3-microvm-execution, R-421-managed-cloud-deployment-e2e]
  blocks: []
  posture: phase-7
  scope: { files: [harness-runtime/src/**, harness-as/src/**], contracts: [C-AS-15 §15], cross_axis: yes }
  skills: { primary: phase-7-implementation, secondary: [] }
  advisor_required: yes
  council_required: conditional:nameable-tension
  verification: { shape: e2e, must_pass: ["TIER_4-resolved TOOL_STEP executes under firecracker/full-VM", "FULL_VM provider class active only at MANAGED_CLOUD surface", "EXTERNAL_IRREVERSIBLE blast-radius enforced"] }
  close_shape: { type: PR-merge, artifact: "feat(sandbox): TIER_4 full-VM execution provider", cascade: [] }
  next_pointer: null
  notes: >
    Top of the tier ladder. The 12-cell deployment_matrix.py reserves FULL_VM exclusively for MANAGED_CLOUD; this
    row therefore co-gates on R-421 (a real MANAGED_CLOUD surface). Closed by the operator-approved managed E2B
    path after local Intel macOS + Lima probing confirmed no `/dev/kvm` is exposed in the R-411 VM. The
    `E2BManagedFullVMToolRunnerExecutionDriver` now plugs into the existing `ToolExecutionDriver` seam, requires
    `SandboxTier.TIER_4_FULL_VM`, creates an E2B managed sandbox with outbound internet disabled by default, and
    exchanges the same stable JSON request/response shape used by the local Docker/gVisor runners. Live proof:
    `just r412-e2b-full-vm-live-e2e` passed on 2026-06-08 with one usage-billed E2B sandbox; the dispatcher
    resolved `tier-4-full-vm`, provider `e2b-managed`, tech `e2b-firecracker`, and the hosted runner returned
    `e2b:hello-r412`. Local Firecracker and QEMU `microvm` remain valid future self-managed variants, but not
    R-412 blockers: upstream Firecracker requires Linux KVM + read/write `/dev/kvm`, and QEMU `microvm` is
    host-gated on Linux x86_64 + KVM + `qemu-system-x86_64` for the canonical KVM path.

R-420-self-hosted-server-deployment-e2e:
  title: Exercise the harness at the SELF_HOSTED_SERVER deployment surface (real server + OTLP collector + tier secrets)
  surface: V
  status: RESOLVED   # closed by the local single-node SELF_HOSTED_SERVER daemon + collector + keyring live e2e
  depends_on: []
  blocks: [R-421-managed-cloud-deployment-e2e, R-430-otlp-collector-tail-keep-preservation]
  posture: phase-7
  scope: { files: [harness-runtime/**, deploy/**], contracts: [C-RT-29 §14.18 daemon mode, C-OD-09 §9.1], cross_axis: yes }
  skills: { primary: phase-7-implementation, secondary: [verify] }
  advisor_required: yes
  council_required: conditional:nameable-tension
  verification: { shape: e2e, must_pass: ["harness daemon runs at SELF_HOSTED_SERVER surface against a real OTLP collector", "tail-keep wrapping active (deployment_surface != LOCAL)", "per-cell base_rate matches the SELF_HOSTED cell", "secrets resolve through self-hosted-keyring (not env fallback)"] }
  close_shape: { type: PR-merge, artifact: "feat(deploy): SELF_HOSTED_SERVER deployment e2e", cascade: [R-421-managed-cloud-deployment-e2e] }
  next_pointer: R-421-managed-cloud-deployment-e2e
  notes: >
    The first real non-LOCAL surface. Unblocks the tail-keep preservation (R-430) row whose
    semantics only exist on a real collector. Daemon mode (C-RT-29 §14.18, FastMCP Unix-socket
    server) is the entrypoint; the operator provisions the server + collector + keyring entries. The
    non-mutating `just self-hosted-readiness --config <harness.toml>` probe now validates the static pre-e2e
    gates (SELF_HOSTED_SERVER config, real collector placement, OTLP endpoint, provider allowlist, tier backend
    selector) without starting the daemon or making network/secret calls. R-440 supplies the `self-hosted-keyring`
    selector. Closed 2026-06-07 by the local single-node self-hosted bootstrap at `deploy/self-hosted-local/`:
    Docker Compose runs OTel Collector Contrib + Tempo + Grafana, the harness daemon stays host-run,
    `harness.selfhosted.local.example.toml` selects `SELF_HOSTED_BACKEND_COLLECTOR` + `self-hosted-keyring`,
    the no-paid live workflow uses local Ollama plus a non-secret `r420_probe_key` sentinel in OS keyring, and
    `just r420-self-hosted-live-e2e harness.selfhosted.local.toml` passed with workflow
    `r420-self-hosted-tool-echo`, daemon status `success`, cost `0`, hosted-provider-calls `0`.

R-421-managed-cloud-deployment-e2e:
  title: Exercise the harness at the MANAGED_CLOUD deployment surface (cloud secrets + FULL_VM provider class + managed collector)
  surface: V
  status: RESOLVED   # closed by approved E2B + GCP Secret Manager + Cloud Run collector live e2e
  depends_on: [R-420-self-hosted-server-deployment-e2e]
  blocks: [R-412-sandbox-tier-4-full-vm-execution]
  posture: halt-route-to-operator
  scope: { files: [harness-runtime/**, deploy/**], contracts: [C-RT-29 §14.18, C-OD-13 §13.1], cross_axis: yes }
  skills: { primary: phase-7-implementation, secondary: [] }
  advisor_required: yes
  council_required: conditional:nameable-tension
  verification: { shape: e2e, must_pass: ["harness runs at MANAGED_CLOUD surface", "secrets resolve via a cloud backend (in-sandbox encrypted-fs per ADR-F5)", "MANAGED_CLOUD per-cell sampler + redaction posture active"] }
  close_shape: { type: PR-merge, artifact: "feat(deploy): MANAGED_CLOUD deployment e2e", cascade: [R-412-sandbox-tier-4-full-vm-execution] }
  next_pointer: null
  notes: >
    The terminal deployment surface. Co-gates R-412 (FULL_VM provider class is MANAGED_CLOUD-only per deployment_matrix.py).
    Heaviest infra dependency; deferred-far. ADR-F5 tier-aware secret-fetch (in-sandbox encrypted-filesystem at this tier).
    E2B (`e2b-dev/e2b`) is a candidate managed-cloud sandbox provider to evaluate if the operator wants a hosted
    sandbox instead of provisioning the cloud substrate directly. It remains credential/remote-execution gated:
    `E2B_API_KEY` + Python SDK readiness can be checked locally with `just sandbox-host-check r421-e2b`, but no E2B
    sandbox call should run without explicit approval. The 2026-06-07 R-421 closure pass added
    `just r421-managed-cloud-readiness <config> --hosted-sandbox-provider e2b`, an operator copy/edit template at
    `deploy/managed-cloud/harness.managed-cloud.e2b.example.toml`, and a separate `just r421-e2b-live-probe`
    command. The 2026-06-07 GCP backend slice adds `ProviderSecretBackend.GCP_SECRET_MANAGER`,
    `ProviderSecretsConfig.gcp_project_id`, a mockable `GcpSecretManagerResolver`, and a static-ready template
    with `backend = "gcp-secret-manager"`. The E2B live probe is ready to run once explicitly approved, but it
    only proves the hosted sandbox candidate; it does not close the provisioned cloud-secret entries or managed
    collector requirements.
    Operator-present NotebookLM + official-source research on 2026-06-07 selected the fastest honest first closure
    path as E2B hosted sandbox + GCP Secret Manager + Google-built OpenTelemetry Collector on Cloud Run, with
    Langfuse/Arize/AWS alternatives documented at `deploy/managed-cloud/r411-r421-infrastructure-selection.md`.
    The approved E2B live probe passed this session, and static readiness now passes for the selected GCP backend
    shape without daemon start, OTLP probe, secret fetch, SDK install, or managed-cloud provider call. The next
    closure slice is a gated live e2e only after the operator provisions GCP credentials, the
    `google-cloud-secret-manager` SDK, the named Secret Manager entries following the `servicename-secret`
    convention (starting with `e2b-secret`), a non-loopback managed OTLP endpoint, and a cost-approved collector.
    The 2026-06-07 live R-421 collector pass provisioned an authenticated Google Cloud Run OTel collector at
    `https://arhugula-r421-otel-collector-543404640214.us-central1.run.app`, stored the non-secret collector
    YAML as Secret Manager entry `r421-otel-collector-config`, and proved static readiness plus redacted
    `e2b-secret` resolution against project `project-ba535aa4-f08d-46b2-ba6`. Approved E2B sandbox calls ran
    the deterministic command before the full e2e hit the runtime OTLP materialization gate. The 2026-06-07
    runtime/design follow-on (PR #344) resolves that static mismatch by adding
    `CollectorConfig.bootstrap_sandbox_tier`: the default remains `TIER_1_PROCESS` for LOCAL/self-hosted
    host-process bootstrap, while the E2B/FULL_VM managed-cloud template declares `tier-4-full-vm` so
    C-OD-20 reachability is checked against the actual network-capable bootstrap tier instead of weakening
    Tier-1. The readiness and live e2e gates now fail fast on stale Tier-1 + `VENDOR_PIPELINE` bindings before
    creating another E2B sandbox. Closed 2026-06-07 by the approved live e2e against
    `/private/tmp/r421-managed-cloud.live.toml`: static readiness passed after binding
    `bootstrap_sandbox_tier = "tier-4-full-vm"`; `e2b-secret` resolved through GCP Secret Manager without printing
    the secret; the hosted E2B sandbox ran the deterministic `r421-e2b-ok` command; authenticated OTLP export to
    Cloud Run used a short-lived impersonated service-account ID token carried as gRPC call credentials; and
    Cloud Trace observed trace `d848a4da6622f42407a5e58c507513c5` with spans `r421.managed_cloud.root` and
    `sandbox.violation`. The R-421 closure also enabled `iamcredentials.googleapis.com`, granted the impersonated
    compute service account Cloud Run Invoker on the collector service, and fixed the live e2e tool so future
    authenticated gRPC exports do not drop the Authorization metadata. The temporary local
    `roles/iam.serviceAccountTokenCreator` binding used for the proof was removed and verified absent after the
    live run. R-412 later closed on the selected managed E2B full-VM provider path.

R-430-otlp-collector-tail-keep-preservation:
  title: Verify tail-keep-on-classification preservation at a real OTLP collector boundary
  surface: V
  status: RESOLVED   # local R-420 collector stack exercised the tail-keep preservation semantic end-to-end
  depends_on: [R-420-self-hosted-server-deployment-e2e]
  blocks: []
  posture: phase-7
  scope: { files: [harness-od/**, deploy/**, tools/**, justfile], contracts: [C-OD-09 §9.1, §9.2], cross_axis: no }
  skills: { primary: phase-7-implementation, secondary: [verify] }
  advisor_required: no
  council_required: no
  verification: { shape: e2e, must_pass: ["a trace with a classification-trigger span (validator.fail.permanence=permanent / sandbox.violation / breaker.tripped) is preserved end-to-end at a real collector", "a non-triggering trace is sampled per base_rate"] }
  close_shape: { type: PR-merge, artifact: "test(od): tail-keep preservation at real OTLP collector", cascade: [] }
  next_pointer: null
  notes: >
    The TailKeepSpanProcessor (tail_keep_span_processor.py) buffers per-trace + replays at root close; the R-420
    local collector stack now provides the real OTLP/Tempo substrate that LOCAL suite R-400 structurally could not.
    Closure evidence 2026-06-07: `just r430-tail-keep-live-e2e harness.selfhosted.local.toml` emitted a
    `sandbox.violation` trace and a non-triggering trace through the real OTLP exporter/collector. Tempo exposed
    trigger trace `4972258a693b5d34c32c89ecd30749bc` with spans `r430.trigger.root` + `sandbox.violation`, while
    plain trace `364f9516e5f95cae58f4b44219981626` stayed absent through the negative window
    (`trigger-trace-preserved=true`, `non-trigger-trace-exported=false`, `cost=0`, `hosted-provider-calls=0`).

R-440-tier-level-secrets-backend:
  title: Wire a SELF_HOSTED_SERVER tier-level secrets backend (currently operator-supplied / env-fallback only)
  surface: V
  status: RESOLVED   # self-hosted-keyring selector + keyring-only resolver path landed; live exercise folds into R-420
  depends_on: []
  blocks: []
  posture: phase-7
  scope: { files: [harness-runtime/src/harness_runtime/config/**], contracts: [ADR-F5 §1, C-AS-05 §5.1 fetch_secret], cross_axis: no }
  skills: { primary: phase-7-implementation, secondary: [] }
  advisor_required: conditional:if a fix touches the fetch_secret contract or a cross-axis type
  council_required: no
  verification: { shape: integration, must_pass: ["secrets resolve via a tier-level backend at SELF_HOSTED_SERVER (not env fallback)", "LOCAL_DEVELOPMENT keyring + env-fallback path preserved (no regression)"] }
  close_shape: { type: PR-merge, artifact: "feat(secrets): SELF_HOSTED tier-level secrets backend", cascade: [] }
  next_pointer: null
  notes: >
    This row is closed by adding `ProviderSecretBackend` and the `self-hosted-keyring` selector on
    `ProviderSecretsConfig`. The default LOCAL path remains keyring + env fallback; the SELF_HOSTED path resolves
    from keyring only and refuses ambient env fallback. `just self-hosted-readiness --config <harness.toml>` now passes
    the R-440 static gate when `[runtime.provider_secrets] backend = "self-hosted-keyring"` is configured. The live
    server/collector/keyring-entry exercise remains R-420; MANAGED_CLOUD bootstrap-token / cloud secrets remains R-421.
```

**Surface VI (multi-tenant) trigger fired.** Per §9, authoring this R-400 decomposition triggers §VI (Multi-tenant) decomposition. §VI remains `decomposition-owed` + live-gated (real multi-tenant deployment required); R-500-series authoring is a follow-on arc — not bundled here.

### 5.6 Process discipline (R-600..R-699)

```yaml
R-600-workflow-v1-14-amendment:
  title: Workflow v1.13 → v1.14 — roadmap-driven discipline catalogue
  surface: VII
  status: RESOLVED   # Workflow v1.14 authored 2026-06-01 — NEW §7.5 Process-discipline catalogue (4 disciplines seeded PD-1..PD-4 + OPEN clause)
  depends_on: [PR-merge-of-this-roadmap]
  blocks: []
  posture: design-phase
  scope: { files: [design-substrate/Project_Workflow_*.md], contracts: [Workflow §7.4, §7.5 NEW], cross_axis: no }
  skills: { primary: spec-writer, secondary: [harness-adversarial-reviewer] }
  advisor_required: satisfied:2026-06-01   # advisor reshaped the candidate set: per-candidate independence gate; v1.9 framework-precedent; PD-4 supersession + cardinality honesty; 2 candidates parked; landed-substrate exclusion confirmed
  council_required: no   # nameable-tension discriminator (§13) — no cross-axis tension in a process-discipline catalogue; routed single-author + advisor per §10.9
  verification: { shape: grep, must_pass: ["§7.5 NEW roadmap-discipline section authored", "next-action derivation rule canonicalized at workflow doc layer", "clearance marker filed"] }
  close_shape: { type: substrate-amendment, artifact: "Workflow v1.13 → v1.14", cascade: [R-IF-roadmap-refresh] }
  next_pointer: null
  notes: >
    RESOLVED 2026-06-01 — design-substrate/Project_Workflow_v1_14.md authored: NEW §7.5 Process-discipline
    catalogue under §7 (sibling to §7.4 fidelity-grammar), following the v1.9 §7.4.7 framework-establishing
    precedent. 4 disciplines seeded (PD-1 halt-route-split-AC; PD-2 use-the-product-probe; PD-3
    verification-shape-grep-vs-e2e w/ CLAUDE.md §13.1 cross-ref; PD-4 plan-revision-against-not-yet-built-substrate,
    single-unit-multi-rescope + SUPERSEDES the U-RT-111 v2.36 §7.4.7.2-sub-species framing) + OPEN accumulation
    clause + 5 parked candidates failing the §7.5.1 independence gate. The must_pass[1] "next-action derivation
    rule canonicalized at workflow doc layer" is N/A as written (the derivation rule lives at Project_Roadmap §4 +
    CLAUDE.md §12, not the workflow doc; §7.5 is a process-discipline catalogue, not a next-action-derivation
    surface) — the substantive close is the §7.5 catalogue + clearance marker. Co-published: workspace CLAUDE.md
    §2.1 row bump v1.13→v1.14 + §10.2/§10.3 stale-v1.12-cite refresh + clearance marker
    .harness/clearance/Project_Workflow-v1_14-cleared-2026-06-01.md. ZERO cross-axis cascade. See
    design-substrate/Project_Workflow_v1_14.md + .harness/R-600-pattern-bake-in-sweep.md §2.
    must_pass[1] DISPOSITION — N/A operator-RATIFIED at AskUserQuestion 2026-06-01 (post-#201): the
    criterion ("next-action derivation rule canonicalized at workflow doc layer") was a speculative
    pre-survey draft inconsistent with the entry's actual scope (a §7.5 process-discipline catalogue,
    not a next-action-derivation surface); the derivation rule's canonical home stays roadmap §4 +
    CLAUDE.md §12 (no second home / no drift). Entry stands RESOLVED on must_pass[0] (§7.5 authored) +
    must_pass[2] (clearance marker filed); must_pass[1] retired as malformed. Fully closed.

R-600-pattern-bake-in-sweep:
  title: Sweep workspace memory for pattern candidates ready for workflow-doc promotion
  surface: VII
  status: ACTIVE
  depends_on: []
  blocks: []
  posture: mode-agnostic
  scope: { files: [memory/**, design-substrate/Project_Workflow_*.md], contracts: [], cross_axis: no }
  skills: { primary: null, secondary: [] }
  advisor_required: no
  council_required: no
  verification: { shape: grep, must_pass: ["all `[[pattern-name]]` cardinality ≥2 entries identified", "each promotion candidate evaluated against the §7.4.7 + §7.5 catalogues"] }   # must_pass[1] refreshed at cadence-2: pre-v1.14 text said "§7.4.7" only; §7.5 now exists and is where process-disciplines land
  close_shape: { type: substrate-amendment, artifact: "Workflow doc revision absorbing N patterns", cascade: [] }
  next_pointer: null
  resume: .harness/R-600-pattern-bake-in-sweep.md   # ACTIVE-SURVEYED (cadence-4) 2026-06-30 HEAD 3177fab8: both must_pass met. Cadence-4's full-chain witness candidate matured via independent composed-runtime arcs and was promoted at workflow v1.16 as PD-6 composed-chain non-vacuity witness. ZERO new §7.4.7 owed. Next run only after the cadence trips again (~10 PRs) or a concrete new candidate reaches independent instance-cardinality >=2.
  notes: >
    Cadence: every ~10 PRs or operator-discretion. NOT every session. FIRST run 2026-06-01
    (HEAD d7574b3). Survey at .harness/R-600-pattern-bake-in-sweep.md. Result: ZERO new §7.4.7.2
    stale-carry-text sub-species owed (strike-revision already promoted at v1.13; species 1/4
    EMPTY, 3/5 unchanged). Load-bearing finding (3rd independent surfacing after v1.13 §3(a) +
    v1.14 deferral): the strong disciplines (verification-shape-sharpened-grep-vs-e2e,
    halt-route-split-AC, plan-revision-against-not-yet-built-substrate,
    LANDED-substrate-pending-upstream-loop, use-the-product-probe — counts in the survey are
    [[..]]-citation salience, NOT instance-cardinality; confirm per-candidate at v1.14) are ALL non-§7.4.7-shape →
    a NEW §7.5 / §7.4.7.X process-discipline catalogue is the correct home, to be seeded at the
    v1.14 amendment. Memory-hygiene dups flagged (§3 of survey) → route to MEMORY.md audit.
    CADENCE-2 (2026-06-02, HEAD 2e60741, post-PR-242; survey "Cadence-2 run" section): the v1.14
    amendment LANDED (PR #201) and absorbed cadence-1's strong set (PD-1 halt-route-split-AC /
    PD-2 use-the-product-probe / PD-3 verification-shape / PD-4 plan-revision-against-not-yet-built-substrate;
    LANDED-substrate routed to .harness/ 7d; carrier-home + spec-prose-drift PARKED at §7.5.3) →
    cadence-1 cycle DISCHARGED. Fresh enumeration (161 files / 166 tokens / 104 at card≥2, unchanged):
    ONE new §7.5 candidate PD-5 = r-cxa-seam-wiring-is-producer-discovery (card 3), cardinality-QUALIFIED
    per the PD-4 honesty precedent (R-CXA-1/R-CXA-4 same-session multi-seam; U-RT-111 likely shared with
    PD-4's lineage) — needs a 2nd genuinely-independent arc + a home/consolidation decision (standalone vs
    cite-under-PD-2/3 vs head of the consolidating card-1 grounding-first family: closeable-slice-honest-close,
    wrong-version-read-delta-only-baseline, porting-old-wip-superseded, verify-observation-layer). ZERO new
    §7.4.7 owed (4th surfacing). must_pass[1] text refreshed (§7.4.7 → §7.4.7 + §7.5). PD-5 promotion is a
    FUTURE v1.15/v1.16 design-phase arc (spec-writer + advisor; operator-discretion; discharged at CADENCE-3 below).
    Memory-hygiene dups → FILED as R-600-memory-hygiene-normalization (below) and RESOLVED same arc (2026-06-02).
    CADENCE-3 (2026-06-10, HEAD a7f7d1f4, post-PR-466; survey "Cadence-3 run" section): cadence trigger met
    (248 commits since cadence-2; 199 memory files / 713 refs / 192 tokens / 124 at card>=2). The cadence-2 PD-5
    candidate matured as a broader grounding-first producer/slice discovery discipline: R-CXA seam producer discovery,
    R-830 backend-slice honesty, R-410/R-411/R-412 infra feasibility grounding, and post-Phase-8 roadmap re-grounding
    provide independent instances. Workflow v1.15 authored PD-5; clearance marker filed; CLAUDE pointers updated.
    ZERO new §7.4.7 owed. R-600 remains recurring, but the v1.15 promotion debt is discharged.

R-600-memory-hygiene-normalization:
  title: Normalize duplicate/case-split [[..]] wiki-link tokens in the auto-memory store
  surface: VII
  status: RESOLVED   # 2026-06-02 — 39 refs across 30 files normalized to canonical slugs; total refs unchanged (579); backed up pre-edit
  depends_on: []
  blocks: []
  posture: mode-agnostic
  scope: { files: ["memory/** (auto-memory store; NOT version-controlled in this repo)"], contracts: [], cross_axis: no }
  skills: { primary: null, secondary: [] }
  advisor_required: no
  council_required: no
  verification: { shape: grep, must_pass: ["each dup/case-split token has a verified canonical own-file before rename", "old tokens → 0 refs; canonical tokens absorb the counts; total [[..]] ref-count unchanged", "only [[..]] tokens changed (no other content drift); pre-edit backup taken"] }
  close_shape: { type: memory-store-edit, artifact: "5 token renames across the auto-memory store", cascade: [] }
  next_pointer: null
  notes: >
    RESOLVED 2026-06-02 (R-600 cadence-2 follow-on; operator-approved). The 5 dup/case-split
    [[..]] tokens flagged at the cadence-1 §3 + cadence-2 C2-§3 survey were normalized to their
    canonical own-file slugs via literal bracketed-token replacement (Python; pre-edit backup):
    [[halt-route-split-AC-pattern]]→[[halt-route-split-ac-pattern]] (25); [[use-the-product-probe]]
    →[[use-the-product-probe-pattern]] (6); [[fork-u-rt-44]]→[[fork-u-rt-44-workflow-loop-drain]] (3);
    [[LANDED-substrate-pending-upstream-loop-substrate]]→[[landed-substrate-pending-upstream-loop-substrate-sub-species]]
    (4); [[h-t-cp-19-default-gate-level-spec-extension]]→[[fork-h-t-cp-19-default-gate-level-spec-extension]] (1).
    Verified: all 5 old tokens → 0; canonicals absorbed every count (e.g. ac-pattern 12→37); total
    refs unchanged at 579 (pure rename); 30 files differ from backup, token-only. Improves memory
    recall (links now resolve to real files). The store is NOT in this repo, so this is a memory-store
    edit, not a repo diff — the roadmap entry + the survey C2-§3 close-out are the durable record.
    SCOPE NOTE: the survey also flagged MEMORY.md index near-cap (24,297 B vs ~24.4 KB); index
    PRUNING is deliberately OUT of scope (judgment-heavy; loses recall pointers; under cap at close)
    → left as a watch item, not pruned.

R-600-clearance-marker-backfill-survey:
  title: Survey design-substrate amendments lacking clearance markers
  surface: VII
  status: RESOLVED   # 2026-06-01 — survey complete; no spec/ADR/ADD/PRD/CXA/Workflow gap; intermediate-plan-version exemption documented at .harness/clearance/README.md
  depends_on: []
  blocks: []
  posture: mode-agnostic
  scope: { files: [design-substrate/**, .harness/clearance/**], contracts: [], cross_axis: no }
  skills: { primary: null, secondary: [] }
  advisor_required: no
  council_required: no
  verification: { shape: grep, must_pass: ["every design-substrate amendment merged after 2026-05-29 has a clearance marker", "exceptions documented at .harness/clearance/README.md"] }
  close_shape: { type: PR-merge, artifact: "ops: clearance marker backfill", cascade: [] }
  next_pointer: null
  notes: >
    RESOLVED 2026-06-01. Surveyed all 18 design-substrate/** amendments merged since 2026-05-29
    against the 17 clearance markers on main. Result: every spec (CP v1.26–v1.30, runtime
    v1.38–v1.41, IS v1.3), CXA (v2.17/v2.18), Workflow (v1.13), and every TERMINAL plan version
    (runtime v2.42, CP v2.31, IS v2.5, OD v2.27) has a marker. The only versions lacking a
    per-version marker are 10 INTERMEDIATE, already-superseded plan versions (runtime v2.34–v2.41,
    CP v2.30, IS v2.4) — all covered by their cluster's terminal marker per the latest-consumed
    Supersession rule. No backfill owed for the contract-authority surfaces (specs/ADR/ADD/PRD/
    CXA/Workflow are gap-free). Codified the terminal-marker-covers-chain exemption (plans only)
    + the survey log at .harness/clearance/README.md per must_pass #2. Non-retroactive per CLAUDE.md §4.5.

R-600-notebooklm-mcp-server-setup:
  title: NotebookLM MCP server (jacob-bd/notebooklm-mcp-cli) installed as supplement to skill
  surface: VII
  status: RESOLVED
  depends_on: [R-600-notebooklm-skill-setup]
  blocks: []
  posture: mode-agnostic
  scope:
    files: [.mcp.json, memory/notebooklm-harness-corpus-url.md]
    contracts: []
    cross_axis: no
  skills: { primary: null, secondary: [] }
  advisor_required: no
  council_required: no
  verification:
    shape: integration
    must_pass:
      - "notebooklm-mcp-cli==0.6.13 installed via uv tool (Python 3.12)"
      - "Auth via nlm login (interactive Chrome sign-in; cookie-import path fails because raw-string format loses per-domain metadata)"
      - "nlm login --check returns Authentication valid + 23 notebooks visible"
      - ".mcp.json registers notebooklm server at stdio transport"
      - "Server starts cleanly on stdio (smoke-test)"
  close_shape:
    type: PR-merge
    artifact: "ops: NotebookLM MCP server supplement + .mcp.json registration"
    cascade: []
  next_pointer: null
  notes: |
    SUPPLEMENT, not replacement. Two tools live concurrently per operator decision:
    - This MCP server (jacob-bd) — Claude-native invocation via mcp__notebooklm__* tools;
      35 granular tools; faster (no Chromium per query); preferred for council pre-bind
      probes + adversarial external-canon + workflow v1.14 absorption deliberations.
    - teng-lin skill (R-600-notebooklm-skill-setup) — CLI shellout from justfile recipes;
      artifact generation surfaces (podcasts, video, mind maps); operator-direct queries.

    Auth path lesson: nlm's `--manual --file` accepts raw "name=value; ..." cookie string
    but strips per-domain metadata. When nlm refreshes CSRF token, ALL cookies arrive at
    notebooklm.google.com with no domain attribution → SID name collisions → server
    redirects to login. Only `nlm login` interactive flow yields working auth (~30s
    one-time browser interaction). Memory entry refreshed in same PR with this finding.

    NEW pattern candidate: [[raw-cookie-string-vs-per-domain-metadata]] — cookie auth via
    a flat header string format only works when the receiving HTTP client doesn't
    cross-domain. nlm cross-domains (accounts.google.com refresh + notebooklm.google.com
    API) so raw-string fails. Cardinality 1; awaits second instance.

    Audit usage after ~1 month: which tool fires more queries; retire the loser if
    usage is clearly imbalanced.

R-600-notebooklm-skill-setup:
  title: NotebookLM skill integration — interactive access to 28-URL-scrape research corpus
  surface: VII
  status: RESOLVED
  depends_on: []
  blocks: []
  posture: mode-agnostic
  scope:
    files: [memory/notebooklm-harness-corpus-url.md]
    contracts: []
    cross_axis: no
  skills: { primary: null, secondary: [] }
  advisor_required: no
  council_required: no
  verification:
    shape: integration
    must_pass:
      - "notebooklm-py 0.6.0 installed via uv tool (Python 3.12 base for rookiepy compat)"
      - "Playwright Chromium installed at ~/Library/Caches/ms-playwright/"
      - "Auth via Chrome cookie extraction (zero OAuth flow); status=ok + token_fetch=true"
      - "Claude Code skill at ~/.claude/skills/notebooklm/ + Agent skill at ~/.agents/skills/notebooklm/"
      - "Notebook 57b8d946-... pinned as default"
      - "Test query against URL-scrape corpus returns content NOT in static .harness/01-planning/01-harness-planning/00-harness-research/02-notebooklm-queries/ extracts"
  close_shape:
    type: PR-merge
    artifact: "ops: notebooklm-py skill installed + auth via chrome cookies + test query passed"
    cascade: []
  next_pointer: null
  event_trigger: |
    NotebookLM consultation now ACTIVE for:
    - Workflow v1.14+ revision arc (Phase 7 → Phase 8 retirement; SDLC absorption)
    - Adversarial reviewer external-canon mode (static-extract-unresolvable divergence)
    - State-of-the-art queries post-2026-05-09 source-cutoff
    - Council orchestrator pre-bind probe (voice cite needing primary-source verification)
  notes: |
    Framing correction at setup: integration is skill-based via teng-lin/notebooklm-py,
    NOT MCP-server-based as the prior memory entry framed it. Repo provides Python CLI +
    Playwright browser automation + Claude Code skill via `notebooklm skill install`.
    Static extracts at .harness/01-planning/01-harness-planning/00-harness-research/02-notebooklm-queries/ remain load-bearing for ~95% of queries;
    interactive corpus for the trigger events above. Memory entry [[notebooklm-harness-corpus-url]]
    refreshed in same PR. RESOLVED in one arc (skipped PROPOSED → ACTIVE) since setup +
    verification + documentation all closed at this PR's merge.

R-600-substitution-ledger-schema:
  title: Extract the 54-row substitution ledger to a schema-backed source + derive the counts (kill the count-drift / stale-carry defect class for the accounting surface)
  surface: VII
  status: RESOLVED   # 2026-06-02 — built (operator authorized). .harness/substitutions.yaml (55 rows = 54 canonical + CP-24) + tools/substitution_ledger.py (derive/validate, --check CI gate) + tools/test_substitution_ledger.py (live canonical pin 49/52/54 after batch-52 + historical Phase-8 seed 46/49/54 + both per-axis breakdowns + label≠count + 4 negative tests) + ci.yml substitution-ledger blocking job + generate.py consumes the derivation (killed NONRETIRED_LEDGER counts + 46-48 range prose) + prose pointers. Derivation reproduced graduation §3 exactly at seed time (46/49/54), and batch-52 now advances the live ledger to 49/52/54.
  depends_on: [R-700-phase-8-substitution-accounting]   # RESOLVED 2026-06-02 — the canonical 46/54 disposition set (.harness/phase-8-graduation.md §3) is the schema's seed data
  blocks: []
  posture: mode-agnostic
  scope:
    files:
      - .harness/substitutions.yaml            # NEW — one typed row per substitution (source of truth)
      - tools/dashboard/generate.py            # derive counts; stop regex-scraping "RETIRED N/54" prose
      - .github/workflows/**                    # NEW tally-validation gate (impossible bucket sum = CI fail)
      - .harness/roadmap_status.md             # cite the derived number, don't hand-maintain
      - .harness/phase-7d-retirement-ledger-v2.md
      - harness-cp/CLAUDE.md
      - harness-od/CLAUDE.md
      - CLAUDE.md
    contracts: []
    cross_axis: no
  skills: { primary: null, secondary: [] }
  advisor_required: conditional:if the disposition-enum design or the forward-only-append model touches a load-bearing accounting invariant
  council_required: no
  verification:
    shape: integration
    must_pass:
      - "NEW .harness/substitutions.yaml holds 54 typed rows {id, axis, disposition (enum), counted_in_retired (bool), canonical (bool — resolves the CP-21-vs-22 / AS-3↔AS-9 accounting ambiguity explicitly), rationale, r_pointer, batch}"
      - "a generator derives the buckets + integers; seed output == phase-8-graduation.md §3 canonical (46/54 RETIRED + 49/54 pipeline-advanced), and forward retirement batches update the live integers structurally (batch-52: 49/54 + 52/54)"
      - "an impossible tally (e.g. RETIRED=48 with 3 PARTIAL) is a CI failure, not a months-later draft discovery"
      - "label != count-membership enforced structurally — disposition label is orthogonal to counted_in_retired; a RETIRED-AS-X label with counted_in_retired=false is legal + tested (the R-700 OD-4/OD-6 case)"
      - "the 5 prose copies (dashboard / ledger §11.x / harness-cp+od CLAUDE.md / root CLAUDE.md) CITE the derived number instead of hand-maintaining it; dashboard trend reads structured data, not regex"
      - "forward-only audit trail preserved (append/supersede; never silently rewrite a historical row — mirrors ledger §0.5)"
  close_shape:
    type: PR-merge
    artifact: "feat(tooling): schema-backed substitution ledger + derived counts + tally CI gate"
    cascade: []
  next_pointer: null
  notes: >
    Motivated by the R-700 Phase-8 close (2026-06-02): `48/54` was internally impossible (48 RETIRED but
    3 PARTIAL ⇒ ≤1 possible) and survived ~51 batch footers + 5 hand-maintained files before a draft
    caught it; the 46-vs-47 ambiguity + the label≠count-membership rule had to be reasoned out with
    advisor. A typed one-row-per-substitution source + generator makes the buckets DERIVED and an
    impossible tally a CI failure — killing the workspace #1 defect class (stale-carry-text, CLAUDE.md
    §10.9) for the accounting surface. SCOPE DISCIPLINE: schema-fy ONLY the counted/derived state (the
    ledger). Prose REASONING (change-notes, fork Readings, council, the "why") stays prose — schema
    flattens the epistemic nuance (§10.4) and buys validation, not readability. Mirror precedent: the
    roadmap R-NNN entries are already schema-backed (§3 + tools/dashboard/generate.py + the session-start
    hash hook); this extends the same pattern to the substitution ledger. CI-gate component relates to
    Surface III (R-200) but the dominant character is process-discipline anti-drift. Minimal first step,
    NOT a migration — the prose docs reference the derived numbers.

R-600-post-merge-refresh-hook:
  title: PostToolUse hook — auto-detect "terminating refresh owed" after a gh pr merge
  surface: VII
  status: RESOLVED   # built + hermetic-tested this PR; goes live NEXT session (settings.json loads at session start)
  depends_on: []
  blocks: []
  posture: mode-agnostic
  scope: { files: [tools/roadmap-audit/post-merge-refresh.sh, tools/roadmap-audit/test_post_merge_refresh.sh, .claude/settings.json], contracts: [], cross_axis: no }
  skills: { primary: null, secondary: [] }
  advisor_required: satisfied:2026-06-03   # advisor: PostToolUse > Stop (noise); hook can't self-activate this session (test by direct invocation); gate on a REAL origin advance
  council_required: no
  verification: { shape: integration, must_pass: ["hermetic test 4/4 (non-merge / no-advance / refresh-tip stay silent; substantive-advance emits + pre-computes hash)", "PostToolUse wired in .claude/settings.json matcher=Bash", "advisory only — exit 0, additionalContext injection, never blocks the tool flow"] }
  close_shape: { type: tooling, artifact: "post-merge-refresh.sh + settings.json PostToolUse + hermetic test", cascade: [] }
  next_pointer: null
  notes: >
    Hook A from the 2026-06-02 hooks/codex exploration. Automates the §12.2 post-merge refresh toil
    (hand-computing the sha256 anchor ~4×/session). PostToolUse matcher=Bash; the script early-exits
    unless the command matched `gh pr merge`, then (timeout-guarded fetch) emits ONLY when
    origin/<default> advanced past the dashboard's pinned git_head to a commit whose title does NOT
    match `^ops: roadmap status refresh ` — one condition covering failed merges + refresh-PR merges
    (no false positives; the criterion that keeps advisory hooks alive). Pre-computes the new
    workspace_state_hash + emits the §12.2 checklist. ADVISORY, not blocking (keep-advisory per
    CLAUDE.md §13.2; CI gates are the hard layer). Cannot self-activate (settings.json loads at session
    start) → tested by direct synthetic-stdin invocation; the hermetic test builds its own fixture repo
    so it never rots against the live dashboard. POST_MERGE_REFRESH_REF env override = test seam only.
    PILOT: observe whether it fires accurately + stays quiet over coming sessions; expand to sibling
    hooks (just check pre-push / posture-guard / substitutions --check) only if the ergonomics hold.

R-600-codex-context-guard:
  title: Codex deterministic context guard — source-of-truth workflow + preflight/closeout tooling
  surface: VII
  status: RESOLVED   # 2026-06-05 — PR #301 merged. Codex preflight/checkpoint/closeout guard, hard-failing hooks, local checkpoint artifacting, and credential-gate ledger semantics are live.
  depends_on: []
  blocks: []
  posture: mode-agnostic
  scope:
    files:
      - .codex/notes/deterministic-context-workflow.md
      - tools/codex_context_guard.py
      - tools/test_codex_context_guard.py
      - AGENTS.md
      - justfile
      - .codex/hooks.json
      - .codex/hooks/README.md
      - .codex/hooks/permission_request.py
      - .codex/hooks/session_start.py
      - .codex/hooks/stop_gate.py
      - .codex/notes/codex-compatibility-outline.md
      - .harness/codex_credential_gates.jsonl
      - .github/workflows/ci.yml
      - tools/dashboard/roadmap.html
    contracts: []
    cross_axis: no
  skills: { primary: null, secondary: [] }
  advisor_required: no
  council_required: no
  verification:
    shape: integration
    must_pass:
      - "preflight materializes cwd/root/branch/HEAD/worktree status/dashboard hash/fork count/latest batch from HEAD"
      - "closeout fails hard on edits in the root checkout, design+implementation mixing, default-branch dashboard drift, and stale committed human-dashboard snapshot"
      - "closeout warns on cite-bearing changes needing overlay-check and on missing tracking-surface review"
      - "Codex SessionStart and Stop hooks invoke the guard and propagate hard guard findings as hook failures"
      - "preflight/checkpoint/closeout write an ignored local checkpoint artifact; closeout/local check require the current checkpoint to match HEAD/status/dashboard"
      - "credential-gated units can be logged only with unit/gate/resume/forward-closed evidence; secret-looking command values are redacted; closeout hard-fails when a credential-gate ledger change is not surfaced in roadmap/status"
      - "CI runs the guard runtime smoke with explicit post-merge dashboard-drift allowance plus focused guard tests as a blocking tools job"
      - "focused tests prove each hard failure class, checkpoint freshness behavior, plus overlay/tracking warnings"
  close_shape:
    type: PR-merge
    artifact: "ops: Codex deterministic context workflow + guard CLI"
    cascade: []
  next_pointer: null
  notes: >
    Operator-surfaced defect class 2026-06-05: the Codex compatibility layer had reminders but no
    deterministic context-rot control. A remembered checklist is itself a drift surface. This arc
    promotes the missing discipline into a checked-in source-of-truth note plus a pure Python guard
    with objective findings. Same-arc operator challenge tightened two gaps: hook-invoked guard
    failures now propagate nonzero instead of only printing, and context checkpoints are concrete
    ignored artifacts under .harness/.checkpoints/ with freshness checks at closeout/local check.
    Follow-on operator clarification added credential-gate continuation semantics: Codex builds to the
    exact credential boundary, proves non-credential work closed, logs `.harness/codex_credential_gates.jsonl`
    when no HIL surface is available, surfaces it through roadmap/status, and then proceeds to the next
    implementable unit.
    PR #301 merged 2026-06-05 with all blocking CI green. This complements, not replaces,
    Claude's richer native hooks.

R-600-codex-out-of-family-review:
  title: Codex CLI as a decorrelated out-of-family reviewer (subscription auth) — pilot
  surface: VII
  status: RESOLVED   # pilot validated; review discipline now lives as a standing gate, not an open roadmap item
  depends_on: []
  blocks: []
  posture: mode-agnostic
  scope: { files: [justfile], contracts: [], cross_axis: no }
  skills: { primary: null, secondary: [harness-adversarial-reviewer] }
  advisor_required: satisfied:2026-06-03   # advisor: VERIFY subscription auth empirically (don't reason about precedence); smoke-test ≠ epistemic A/B
  council_required: no
  verification: { shape: integration, must_pass: ["just codex-review runs `codex review --base` on subscription auth (codex login status = ChatGPT; $0 metered)", "guard _require-codex-subscription FAILS LOUD if not logged in via ChatGPT (no silent metered fallback)", "first run validates the pipe (wiring); later A/B evidence validates the standing discipline"] }
  close_shape: { type: tooling, artifact: "justfile codex-review + codex-review-uncommitted + _require-codex-subscription guard + .harness/R-600-codex-out-of-family-review-pilot-closure.md", cascade: [] }
  next_pointer: null
  notes: >
    Codex (B) from the 2026-06-02 exploration. Out-of-family (OpenAI) reviewer complementing Claude
    advisor() — advisor = Claude reviewing Claude = correlated blind spots; Codex gives DECORRELATED
    errors; the strongest signal is DISAGREEMENT between the two (surface to operator). COST: runs on
    the operator's ChatGPT SUBSCRIPTION, not metered API — empirically verified (codex 0.132.0 `login
    status` = "Logged in using ChatGPT" under all env conditions incl. OPENAI_API_KEY present from
    dotenv-load). The recipe forces subscription: `env -u OPENAI_API_KEY` + `-c
    preferred_auth_method=chatgpt`; the _require-codex-subscription guard FAILS LOUD if login is
    absent/stale so codex never silently bills the metered key. ROLE BOUNDARY (X-AL-1): Codex = H_E DEV
    TOOLING, NOT H_T's OpenAI provider (metered-API per ADR-F1 / R-300-multi-llm-second-provider) — the
    subscription can't be hit programmatically by the harness SDK, only by the Codex CLI tool. PILOT:
    the self-referential first run (Codex reviews this PR's diff) is a WIRING SMOKE TEST, not the
    decorrelation A/B. The real A/B = run Codex alongside advisor on the next 3-4 high-stakes forks, log
    what each uniquely catches, let DATA decide keep/expand/drop. Disclosed self-bias: Claude assessing a
    Claude alternative → keep the A/B mechanical (log verbatim, don't self-grade). RESOLVED 2026-06-30:
    later high-stakes forks produced enough data, CLAUDE.md institutionalized `just codex-review` as the
    default concrete-diff artifact reviewer, and `.codex/notes/codex-autonomous-loop.md` keeps it as a
    standing autonomous-loop gate. Tenant policy can still block uncommitted private-diff upload; in that
    case record a local substitute/decorrelated review rather than keeping this pilot open.
```

### 5.7 Halt-doc routings (2026-05-31 carries)

R-700 prefix used because these are halt-resolutions awaiting downstream substantive arcs.

```yaml
R-700-OD-IS-EDGE-DRIFT:
  title: OD→IS edge cardinality reconciliation (halt-doc Item 11; routes via PR #110)
  surface: VII
  status: RESOLVED   # PR #110 merged (must_pass satisfied); reconciliation end-state achieved. NOTE: v2.18's absorption rested on a phantom-drift premise (CXA was already conformed at v2.3) — corrected at CXA v2.19 / PR #226; CXA HEAD now consistent at aggregate 107. The edge cardinality IS reconciled, so RESOLVED is correct.
  depends_on: [R-IF-110]
  blocks: []
  posture: design-phase
  scope: { files: [], contracts: [], cross_axis: yes }
  skills: { primary: null, secondary: [] }
  advisor_required: no
  council_required: no
  verification: { shape: none, must_pass: ["PR #110 merged"] }
  close_shape: { type: substrate-amendment, artifact: "CXA v2.18 absorbs the edge", cascade: [] }
  next_pointer: null
  notes: Tracker for the closure; actual work at PR #110.

R-700-OD-INTERNAL-FORMALIZATION:
  title: OD plan §4.6 OD-INTERNAL carve-out (halt-doc Item 12; routes via PR #111)
  surface: VII
  status: RESOLVED   # PR #111 merged (must_pass satisfied); OD plan v2.27 §4.6.OD-INTERNAL carve-out landed. Was stale-BLOCKED.
  depends_on: [R-IF-111]
  blocks: []
  posture: design-phase
  scope: { files: [], contracts: [], cross_axis: no }
  skills: { primary: null, secondary: [] }
  advisor_required: no
  council_required: no
  verification: { shape: none, must_pass: ["PR #111 merged"] }
  close_shape: { type: substrate-amendment, artifact: "OD plan v2.27 absorbs the carve-out", cascade: [] }
  next_pointer: null
  notes: Tracker for the closure; actual work at PR #111.
```

### 5.8 Operator tooling / observability (R-XI-NN)

Surface XI = human-facing tooling. Distinct from `.harness/roadmap_status.md` which is Claude-consumed. Gates on §III CI substrate so dashboards auto-regenerate (avoiding the manual-refresh failure mode v1 hit).

```yaml
R-XI-01:
  title: Browser-based operator dashboard MVP — at-a-glance harness development status
  surface: XI
  status: RESOLVED   # 2026-06-01: build LANDED (generate.py + roadmap.html + dashboard-deploy.yml, PR #177); operator made the repo public → Pages enabled (build_type=workflow); dashboard-deploy build+deploy both GREEN (run 26750144964); live at https://thestoryportal.github.io/arhugula-harness/ (HTTP 200). R-XI-02/R-XI-03 (PROPOSED) now unblocked.
  depends_on: [R-200-ci-pytest-pyright-ruff-matrix]
  blocks: [R-XI-02, R-XI-03]
  posture: mode-agnostic
  scope:
    files: [tools/dashboard/**, .github/workflows/dashboard-deploy.yml]
    contracts: []
    cross_axis: no
  skills: { primary: phase-7-implementation, secondary: [verify, run] }
  advisor_required: conditional:if tech-stack choice diverges from MVP recommendation (single static HTML + Tailwind CDN + vanilla JS)
  council_required: no
  verification:
    shape: integration
    must_pass:
      - "Generator script reads from .harness/roadmap_status.md + Project_Roadmap_v1.md §5 + gh PR API + git log + harness-*/CLAUDE.md §4.1 and emits single-page roadmap.html"
      - "GitHub Pages auto-deploys roadmap.html on every main push"
      - "Dashboard surfaces: Phase 7 retirement progress bar, R-NNN status board, in-flight PRs with CI status, recently completed, operator gate inventory, drift detection log, next-action panel"
      - "Loads under 2s in modern browser"
      - "Operator can scan progress in <30 seconds without opening other tools"
  close_shape:
    type: PR-merge
    artifact: "operator-dashboard: MVP at https://thestoryportal.github.io/arhugula-harness/"
    cascade: [R-XI-02, R-XI-03]
  next_pointer: R-XI-02
  notes: |
    Recommended tech stack: Python or Node generator script + Tailwind CSS (CDN, no build) + vanilla JS + Chart.js or uPlot for sparklines. NO bundler at MVP — pure static HTML.
    Authored per dashboard-assessment conversation 2026-05-31. Surface XI added to roadmap at same arc.
    PROPOSED until R-200-ci-pytest baseline closes — without CI auto-deploy, this becomes manual-refresh burden (same shape as v1 dashboard bug).

R-XI-02:
  title: Dashboard dependency-graph viz + sparklines (iteration 2)
  surface: XI
  status: RESOLVED   # 2026-06-02 (PR #235, 9cce771): built on the Almanac Noir canonical (PR #234). Mermaid dep-graph (61 nodes, click->discipline-schema panel) + PR-cadence sparkline + RETIRED-count trend (parsed off "RETIRED N/54" phrasings; endpoint 48 = headline). Data wiring authored directly; the one loop-elevatable element (dep-panel) polished via the genuine 4-skill loop (all 4 fired). Runtime-verified in headless Chrome (mermaid renders, click populates panel, 3 canvases). + 3 operator readability passes (type scale up, full-viewport-width responsive, dim tokens lightened for contrast, .rem/.led/.prose/.r/.pr/.rn2 -> 16px/#ddd5bd). NEXT: R-XI-03.
  depends_on: [R-XI-01]
  blocks: []
  posture: mode-agnostic
  scope:
    files: [tools/dashboard/**]
    contracts: []
    cross_axis: no
  skills: { primary: phase-7-implementation, secondary: [verify] }
  advisor_required: no
  council_required: no
  verification:
    shape: integration
    must_pass:
      - "Mermaid.js renders R-NNN dependency graph from §5 catalog"
      - "Click R-NNN node → opens discipline schema panel"
      - "PR cadence sparkline (last 30 days) renders correctly"
      - "RETIRED count trend chart populated from git log + retirement-batch files"
  close_shape:
    type: PR-merge
    artifact: "operator-dashboard: dep graph + sparklines"
    cascade: []
  next_pointer: R-XI-03
  notes: Visual depth-of-decomposition by surface; spot bottleneck R-NNN that unblock most downstream work.

R-XI-03:
  title: Live-update mode — webhook or short-poll
  surface: XI
  status: RESOLVED   # 2026-06-02 (PR #237, 23b80ae): short-poll path. generate.py embeds the real generation-time git HEAD as <meta dashboard-live-head>; a 45s client-side poll of the page's own URL detects a change (DOMParser) and soft-reloads (scroll preserved, background tabs skipped); LIVE indicator in masthead. No webhook/backend → static-deploy-friendly (must_pass #2); works on Pages + :8137. must_pass #1 met at mechanism level (detects within poll interval; end-to-end latency bounded upstream by CI deploy ~1-2min / local-main sync <=5min). Runtime-verified headless (reload fired on change; no reload when unchanged). advisor N/A (only webhook path was infra-gated). LAST Surface XI lever (next_pointer null) → Surface XI COMPLETE.
  depends_on: [R-XI-01]
  blocks: []
  posture: mode-agnostic
  scope:
    files: [tools/dashboard/**]
    contracts: []
    cross_axis: no
  skills: { primary: phase-7-implementation, secondary: [verify] }
  advisor_required: conditional:if webhook approach requires backend infra
  council_required: no
  verification:
    shape: integration
    must_pass:
      - "Dashboard refreshes within 60s of PR merge"
      - "Refresh mechanism does not require operator-managed server (static-deploy-friendly)"
  close_shape:
    type: PR-merge
    artifact: "operator-dashboard: live refresh"
    cascade: []
  next_pointer: null
  notes: |
    MVP path: GitHub Actions on main push triggers Pages redeploy; browser sees fresh dashboard on reload.
    Live-mode path: short-poll GitHub API from browser every 60s; or webhook → static-file regeneration via Cloudflare Workers / Netlify functions.
    Decide at execution time per cost + complexity tradeoff.
```
### 5.9 Phase 8 accounting (R-700..R-799)

```yaml
R-700-closure-accounting-draft:
  title: Draft the definitive remaining-to-full-closure log — Part A 54-row substitution accounting + Part B beyond-substitutions register (Surface-V infra-gated + R-100-config-discovery)
  surface: VIII
  status: RESOLVED   # 2026-06-01 — draft landed at .harness/R-700-phase-8-closure-accounting-draft.md; advisor-passed
  depends_on: []
  blocks: [R-700-phase-8-substitution-accounting]
  posture: mode-agnostic
  scope: { files: [.harness/R-700-phase-8-closure-accounting-draft.md, .harness/roadmap_status.md], contracts: [], cross_axis: no }
  skills: { primary: phase-7-substitution-retirement, secondary: [] }
  advisor_required: yes   # the 54-row arithmetic reconciliation is the main correctness risk — advisor-passed this arc (thesis confirmed load-bearing)
  council_required: no
  verification: { shape: grep, must_pass: ["Part A: all 54 raw-ledger substitution rows enumerated + reconciled to the ledger §11.5 count (48 RETIRED / 6 non-RETIRED, or corrected)", "Part B: R-410..R-440 + R-100-mvp-config-discovery each with summary + vendor + persona/deployment-surface + spec/ADR cites", "feeds R-700-phase-8-substitution-accounting (operator still owns final Phase-8 review)"] }
  close_shape: { type: substrate-amendment, artifact: ".harness/R-700-phase-8-closure-accounting-draft.md", cascade: [R-IF-roadmap-refresh] }
  next_pointer: R-700-phase-8-substitution-accounting
  notes: >
    Operator-requested 2026-06-01 (post-#204): a definitive remaining-to-closure log. The prior session
    deliberately PAUSED before drafting (operator clearing the session for a fresh one) and banked the full task
    spec + resolved facts + captured Surface-V data at the resume checkpoint. ➡️ ON RESUME: read
    .harness/R-700-closure-accounting-draft-checkpoint.md FIRST (do not re-derive). The verified open-substitution
    set is OD-4 (PARTIAL/R-008) + AS-8e (R-005) + AS-8f (R-006); the 48/54-vs-3-open arithmetic gap (CXA 5 subs
    not in any per-axis §4.1 + CP-22 + authoring/bounded tail) is the reconciliation work Part A must close. This
    draft is the Claude-executable input to R-700; the operator still owns the final Phase-8 review + bounded-residual
    sign-offs (AS-8e/AS-8f/OD-6).
    RESOLVED 2026-06-01: draft landed (Part A 54-row table + Part B 8-entry register). KEY FINDING — the published
    48/54-RETIRED/49-pipeline figure is internally impossible (49 pipeline-advanced ⇒ ≤1 PARTIAL, but OD-4 + CXA-1 +
    CXA-4 = 3 PARTIAL). Per-row reconciliation = 46 RETIRED + 3 PARTIAL + 2 STILL-BOUNDED + 3 SB-INDEF = 54
    (accounting (i); pipeline-advanced 49 — matches published 49). RETIRED integer is 46–47; the buckets co-vary
    (accounting (ii) = 47 RETIRED / 2 SB-INDEF / pipeline 50). Root cause: the 5 CXA rows have no per-axis §4.1 + the CXA corrective was never folded
    into the cumulative (ledger §11.1a line 278). True open set = 8 rows (OD-4, CXA-1/2/3/4, AS-8e, AS-8f, CP-17), not 3.
    NOT a regression. 4 flagged Phase-8 ratification items at draft §C (operator owns the final integer; dashboard 48/54
    intentionally NOT overwritten). NEW gap surfaced: CXA-1/2/3/4 + CP-17 have no R-NNN entries — recommend an
    R-002-style Surface-I decomposition pass over CXA + CP-17.

R-700-phase-8-substitution-accounting:
  title: All 49 substitutions accounted for — RETIRED or RETIRED-AS-BOUNDED-RESIDUAL with rationale
  surface: VIII
  status: RESOLVED   # 2026-06-02 — operator lifted the HELD declaration ("kick off"); formal close authored at .harness/phase-8-graduation.md. Canonical: 46/54 RETIRED (85.2%) + 49/54 pipeline-advanced (90.7%); 8 rows carry ratified terminal sign-off dispositions; zero un-dispositioned open substitutions. PHASE 8 CLOSED.
  depends_on: [R-002, R-001, R-001-h-t-is-2-retired, R-004]
  blocks: []
  posture: halt-route-to-operator
  scope: { files: [.harness/phase-7d-retirement-events-batch-*.md, .harness/phase-8-graduation.md], contracts: [], cross_axis: no }
  skills: { primary: phase-7-substitution-retirement, secondary: [] }
  advisor_required: yes
  council_required: yes
  verification: { shape: grep, must_pass: ["all 49 rows of Meta-Architecture §5 accounted", "each RETIRED-AS-BOUNDED-RESIDUAL has documented operator rationale"] }
  close_shape: { type: substrate-amendment, artifact: ".harness/phase-8-graduation.md", cascade: [] }
  next_pointer: null
  notes: >
    Phase 7 closure gate. **RESOLVED 2026-06-02 — operator lifted the held declaration ("kick off the
    declaration"); formal close authored at `.harness/phase-8-graduation.md`.** Item 4 executed: canonical
    **46/54 RETIRED (85.2%) + 49/54 pipeline-advanced (90.7%)** (operator-ratified accounting (i)); the 48→46
    supersession applied forward at ledger §11.7 + harness-cp/CLAUDE.md + dashboard (prior batch records stand
    verbatim per forward-only discipline); bucket dispositions flipped (OD-4 → RETIRED-AS-CROSS-AXIS-DEFERRED;
    AS-8e/8f/CP-17 → accepted-indefinite-defer sign-off — labels do NOT re-tally into the 46; CXA-1..4 →
    Phase-2-runtime-deferred). Advisor confirmed 46 is the forced reading of the joint item-1+item-3
    ratification (the OD-6-in-both-lists tell). Council convene SKIPPED-justified (accounting ratified; the one
    live C10⊥C11 tension at OD-4 was dispositioned at R-008). must_pass SATISFIED (all 49 §5 rows accounted;
    each RETIRED-AS-BOUNDED-RESIDUAL has rationale). **PHASE 8 CLOSED.** — historical HELD-state notes follow. —
    **Prior status: BLOCKED — 3 of 4 PART C rulings
    RATIFIED 2026-06-02 (AskUserQuestion); the formal Phase-8 declaration is HELD by operator choice.**
    Ratifications (see `.harness/R-700-phase-8-closure-accounting-draft.md` PART C): **(1) RETIRED integer =
    46** (accounting (i); pipeline-advanced 49/54). **Cascade DEFERRED** by operator choice — the published
    `48/54` is NOT yet rewritten in the ledger / `harness-cp/CLAUDE.md` / dashboard; `46` is the ratified
    canonical going forward and the wide 48→46 count rewrite lands at the formal declaration (owed-at-declaration).
    **(2) CXA + CP-17 R-NNN coverage CLOSED** — operator chose "author entries"; grounding found CXA-1/2/3/4
    already covered by `R-CXA-1..4` (authored #209, post-dating the draft) + NEW `R-010-cp-17-files-indefinite`
    authored this arc → all 5 flagged rows now have dedicated entries. **(3) Bounded-residual / deferred
    sign-offs RATIFIED** — `AS-8e` (R-005), `AS-8f` (R-006), `CP-17` (R-010), `OD-6` (batch-51 bounded-residual),
    and **`OD-4` (R-008) as a NEW `RETIRED-AS-CROSS-AXIS-DEFERRED` disposition** (gate (a) closed #244; gate (b)
    §13.2 cross-axis at c10-action-safety/Phase-6+ → never OD-axis-Claude-closeable). **(4) HELD** — operator
    accepts the dispositions but defers the formal "Phase-8 substitution accounting CLOSED" declaration pending
    further review; R-700 stays BLOCKED. When lifted, the formal close authors `.harness/phase-8-graduation.md`
    + executes the deferred 48→46 cascade + flips the dispositioned buckets (OD-4 PARTIAL → CROSS-AXIS-DEFERRED;
    AS-8e/8f/CP-17 SB-INDEF → bounded-residual). The `blocks:[R-700]` gating set (R-005/006/008/010 + R-CXA-1..4)
    is now all dispositioned-or-ratified; only the held operator declaration remains.
```

### 5.10 Multi-LLM maturity (R-300..R-399) — Surface IV

*Decomposed 2026-06-01 from `.harness/post-phase-8-forward-register.md` §B-1/§B-2 (discharges the §9 decomposition owed for Surface IV). Commitment: ADR-F1 v1.2 + Target_Stack_Commitment §5.1. Providers all constructed + failure-time fallback wired; capability-aware routing-SELECTION stubbed; multi-provider UNEXERCISED at MVP.*

```yaml
R-300-multi-llm-routing-activation:
  title: Activate layered capability-aware routing-selection (infer() composition seam)
  surface: IV
  status: RESOLVED   # 2026-06-01 (PR #213, merged c047aa2) — infer() activated CP-pure (composes route() + injected async dispatch callable); live INFERENCE_STEP dispatch routes through infer(); full routing.* span attribution (C-CP-01 §1.4; zero emitted before). DECLARATIVE-echo = behavior-preserving SELECTION at MVP. council gate NOT met this arc (route() already fixes cheapest-deterministic-first ordering; only DECLARATIVE live → no live C5⊥C9 decision; that tension fires at R-300-second-provider). must_pass #1/#2/#3 met — #2 split: routing.layer span attr at e2e (in-process fake, mech-α, NOT paid) + InferenceResponse.routing_decision.layer at unit (live path discards InferenceResponse; span is canonical routing-visibility surface). 818 cp + 1239 rt non-e2e + 161 integration + 36 dispatch tests pass; pyright/ruff clean.
  depends_on: [R-100-mvp-real-workflow-execution]
  blocks: []
  posture: phase-7
  scope: { files: [harness-cp/src/harness_cp/routing_core_surface.py, harness-cp/src/harness_cp/layered_routing_strategy.py, harness-runtime/src/**], contracts: [C-CP-01, C-CP-02, C-CP-03, C-CP-04], cross_axis: yes }
  skills: { primary: phase-7-implementation, secondary: [phase-7-back-flow-routing] }
  advisor_required: yes
  council_required: conditional:nameable-tension   # C5 (cost / cheapest-deterministic-first) vs C9 (reliability / when-to-fallback) vs capability-preservation
  verification: { shape: e2e, must_pass: ["routing_core_surface.infer() invokes layered_routing_strategy.route() (no longer NotImplementedError)", "InferenceResponse.routing_decision.layer == 'manifest' on a declarative-layer hit", "per-layer LayerBudget bound per C-CP-03"] }
  close_shape: { type: PR-merge, artifact: "feat(routing): activate layered capability-aware routing", cascade: [] }
  next_pointer: R-300-multi-llm-second-provider
  notes: At HEAD infer() raises NotImplementedError (routing_core_surface.py:83/:97); route() has zero non-test callers (verified 2026-06-01). Provider SELECTION is taken statically from the manifest model_binding. Register §B-1.

R-300-multi-llm-second-provider:
  title: Multi-provider credentials + mixed-provider fallback exercise
  surface: IV
  status: RESOLVED   # 2026-06-03 (PR #281 `2dc25e6` + PR #283 `e436252`) — B-2 fully closed: deterministic cross-family fallback, live Anthropic→OpenAI fallback, and live Ollama fallback exercised.
  depends_on: [R-100-mvp-real-workflow-execution]
  blocks: []
  posture: phase-7
  scope: { files: [harness-runtime/tests/integration/**, harness-runtime/config/provider_secrets.py], contracts: [C-CP-04, ADR-F1], cross_axis: no }
  skills: { primary: phase-7-implementation, secondary: [] }
  advisor_required: yes
  council_required: no
  verification: { shape: e2e, must_pass: ["deterministic production-path fixture forces Anthropic primary failure and asserts cross-family OpenAI advance", "live Anthropic invalid-model failure advances to real OpenAI response", "live Ollama invalid-model failure advances to reachable local Ollama model"] }
  close_shape: { type: PR-merge, artifact: "PR #281 deterministic + live OpenAI; PR #283 live Ollama", cascade: [] }
  next_pointer: null
  notes: >
    Closed by the 2026-06-03 R-300 B-2 sequence recorded in `.harness/roadmap_status.md`: PR #281
    (`2dc25e6`) added the deterministic production-path fixture plus the live Anthropic invalid-model →
    OpenAI `gpt-4o-mini` fallback run (`just mvp-r300-cross-family`, live PASS 4.55s); PR #283
    (`e436252`) added the free local Ollama fallback exercise (invalid model → `llama3.2:3b`, live PASS
    4.17s through `api.run`). Together these exercise the multi-provider fallback path that R-100 left
    untouched: cross-family OpenAI and local Ollama provider traversal are both covered, with deterministic
    CI coverage retained for non-credentialed runs. No further R-300 second-provider gate remains. Register
    §B-2.

R-300-external-cli-oauth-routing:
  title: External-CLI (OAuth/subscription) multi-LLM routing — port from deployed repo into main (prefer-OAuth default)
  surface: IV
  status: RESOLVED   # 2026-07-09 (PR #914) — ported external_cli_provider adapters + config types + dispatch branch + providers/retry wiring from deployed thestoryportal/arhugula (ad690ed + c2ca63c); operator-ratified prefer-OAuth default posture (fork §10); memory retrieval wired on the CLI dispatch path (F2). Two decorrelated reviewers (Fable 5 out-of-family + adversarial) cleared MERGE; codex-check 5355 passed; overlay green.
  depends_on: [R-300-multi-llm-second-provider]
  blocks: []
  posture: phase-7
  scope: { files: [harness-runtime/src/harness_runtime/lifecycle/external_cli_provider.py, harness-runtime/src/harness_runtime/types.py, harness-runtime/src/harness_runtime/lifecycle/providers.py, harness-runtime/src/harness_runtime/lifecycle/llm_dispatch.py, harness-cp/src/harness_cp/memory_access_mode.py, tools/external_cli_provider_config.py], contracts: [ADR-F1, C-MEM-16], cross_axis: no }
  skills: { primary: phase-7-implementation, secondary: [] }
  advisor_required: yes
  council_required: no
  verification: { shape: e2e, must_pass: ["argv-only subprocess adapters for claude_code/codex/antigravity/gemini/generic", "prefer-OAuth default ratified (fork §10), not silently flipped", "memory packet reaches the CLI dispatch prompt (full-chain witness)", "scrubbed child env prevents OAuth→metered billing"] }
  close_shape: { type: PR-merge, artifact: "PR #914 feat(runtime): port external-CLI OAuth routing", cascade: [R-IF-roadmap-refresh] }
  next_pointer: R-300-external-cli-routing-governance
  notes: >
    Ported from the deployed sibling repo thestoryportal/arhugula so the routing lives in both repos; feature
    work continues here (the deployed repos were point-in-time tests). Operator ratified deployed-parity
    (prefer OAuth by default, 2026-07-09 AskUserQuestion; fork §10 amendment of
    class_1_fork_provider_construction_allowlist_semantic.md). Full review findings + dispositions at
    .harness/external-cli-routing-port-review-findings.md.

R-300-external-cli-routing-governance:
  title: Governance reconciliation for the external-CLI routing port + memory substrate (WS2)
  surface: IV
  status: ACTIVE   # opened 2026-07-09 alongside R-300-external-cli-oauth-routing
  depends_on: [R-300-external-cli-oauth-routing]
  blocks: []
  posture: design-phase
  scope: { files: [design-substrate/ADR-D7_memory_substrate.md, CLAUDE.md, .harness/clearance/**], contracts: [ADR-D7], cross_axis: no }
  skills: { primary: null, secondary: [] }
  advisor_required: no
  council_required: no
  verification: { shape: none, must_pass: ["ADR-D7 §15/§86 stale 'not in this repo' claim corrected", "external_cli_provider.py carries a C-* cite (advisory overlay orphan cleared)", "clearance markers filed for the 5 Proposed memory design artifacts (ADR-D7 + Spec_Memory_Substrate_v1 + PRD_v1_2 + Memory_Substrate_Design_v1 + Implementation_Plan_Memory_Substrate_v1)", "CLAUDE.md §2 pointers refreshed (memory substrate + OAuth routing; CP v1.85 / OD v1.30 / Runtime v1.92)"] }
  close_shape: { type: PR-merge, artifact: "governance reconciliation PR", cascade: [R-IF-roadmap-refresh] }
  next_pointer: null
  notes: >
    Separate PR (design-phase posture) from the impl port (R-300-external-cli-oauth-routing, phase-7 posture)
    to keep postures clean per CLAUDE.md §11. Clearance markers (§4.5) serve as X-AL-3 back-flow so the
    design-substrate edits pass the guard.
```

### 5.11 Multi-tenant (R-500..R-599) — Surface VI

*Decomposed 2026-06-01 from register §B-8 (discharges §9 Surface VI; the §VI trigger fired 2026-06-01 per §5.5). OD-4 per-session-toggle/tokenization is tracked separately at R-008. Fields plumbed (tenant_id + persona_tier); base-rate envelope + multi-tenant non-toggleability live; exercised at SELF_HOSTED_SERVER by the R-500 local multi-tenant proof.*

```yaml
R-500-multi-tenant-deployment:
  title: Non-default tenant_id / non-SOLO persona_tier deployment exercise
  surface: VI
  status: RESOLVED
  depends_on: [R-420-self-hosted-server-deployment-e2e]
  blocks: []
  posture: phase-7
  scope: { files: [harness-runtime/src/harness_runtime/lifecycle/tracer_provider.py, harness-runtime/src/harness_runtime/lifecycle/span_processor.py, harness-od/src/**], contracts: [C-OD-10 §10.3, C-OD-13 §13.1, ADR-D5, ADR-D6], cross_axis: yes }
  skills: { primary: phase-7-implementation, secondary: [] }
  advisor_required: yes
  council_required: conditional:nameable-tension   # C7 (observability/privacy) + C8 (security/compliance) vs C11 (operator-burden): how much redaction/audit ceremony is mandatory at TEAM vs MULTI_TENANT
  verification: { shape: e2e, must_pass: ["deploy with non-None tenant_id + non-SOLO persona_tier at a non-LOCAL surface", "§10.3 base_rate envelope + §13.1 redaction gradient behave per spec under real multi-tenant load", "audit-ledger separated by tenant_id"] }
  close_shape: { type: PR-merge, artifact: "feat(multitenant): non-SOLO persona_tier deployment", cascade: [] }
  next_pointer: null
  notes: >
    Closed by the R-500 self-hosted live proof against the R-420 local OTel Collector/Tempo stack.
    RuntimeConfig.tenant_id now materializes as authoritative tenant.id OTel resource attr;
    `just r500-multitenant-live-e2e harness.selfhosted.local.toml` overlays two non-default tenants
    with `multi-tenant-compliance`, verifies base_rate=0.2, confirms non-toggleable redaction
    strips content before Tempo while preserving structure attributes, and proves
    `RuntimeAuditLedgerWriter.read_for_tenant()` separation. Closure evidence 2026-06-07:
    tenant A trace `5c0e5916bf84933296323f2038c6680b`, tenant B trace
    `a847370bbc76adc41b85e3328d3279aa`, `tenant-resource-separated=true`,
    `content-redacted=true`, `audit-ledger-separated=true`, `cost=0`, `hosted-provider-calls=0`.
    Register §B-8.
```

### 5.12 External integrations (R-800..R-899) — Surface IX

*Decomposed 2026-06-01 from register §B-10..§B-13 (discharges §9 Surface IX). Files API (AS-8e/CP-17) is live-proven and closed by R-810; managed_agents (AS-8f) is live-proven and closed by R-820. Batch-52 back-flows AS-8e/AS-8f/CP-17 into the substitution ledger as substantive retired rows.*

```yaml
R-800-external-mcp-server:
  title: Real external MCP server connection (host lifecycle wiring)
  surface: IX
  status: RESOLVED
  depends_on: []
  blocks: []
  posture: phase-7
  scope: { files: [harness-runtime/src/harness_runtime/bootstrap/stage_3a_cp_clients.py, harness-runtime/src/harness_runtime/bootstrap/**], contracts: [runtime spec v1.41 §14.9.3, §14.9.8], cross_axis: no }
  skills: { primary: phase-7-implementation, secondary: [] }
  advisor_required: no
  council_required: no
  verification: { shape: e2e, must_pass: ["bootstrap stage-3a calls host.start() after construction (registry populated)", "host.shutdown() wired at stage-7 teardown", "live e2e against a real external MCP server with operator MCPClientConfig.connection_url"] }
  close_shape: { type: PR-merge, artifact: "feat(mcp): wire external MCP host lifecycle", cascade: [] }
  next_pointer: null
  notes: >
    RESOLVED 2026-06-01 — all 3 must_pass met; verified empirically (no production change owed).
    must_pass[1] host.start() = DONE at stage_3a_cp_clients.py:59; must_pass[2] host.shutdown() = DONE
    at shutdown.py:484-489 — BOTH landed earlier at PR #172 (spec v1.41 §14.9.8 Gaps B/F), NOT at a new
    R-800 arc. must_pass[3] real-external-MCP e2e = SATISFIED by test_u_rt_86 (production factory
    materialize_mcp_client_host_stage + real stdio subprocess + handshake + list_tools + TOOL_STEP
    dispatch + 7-attr mcp.* span) — unconditional, no LLM, 9/9 green. The PROPOSED-era "host.start()
    never called / host.shutdown() zero callers" framing was STALE (authored at PR #209; described
    pre-#172 state) — a stale-carry-text disposition (CLAUDE.md §10.5). RESIDUAL (out of R-800 scope):
    the FULL api.run TOOL_STEP path (must_pass[3] strict reading) is Gap D / R-100 AC#2 — bootstrap
    pings ≥1 provider regardless of step kind, so it is operator-gated by design (not fired
    unilaterally). A bootstrap-skip-provider-ping-for-inference-free-workflows change is a Class 1
    fork candidate (C9⊥C11 nameable tension → dyadic-council-eligible per §10.9) if the operator
    opens it. Register §B-10.

R-810-files-api-integration:
  title: Files API integration (files.* namespace — AS-8e / CP-17)
  surface: IX
  status: RESOLVED
  depends_on: [R-421-managed-cloud-deployment-e2e]
  blocks: []
  posture: phase-7
  scope: { files: [design-substrate (Files arc design-phase), harness-runtime/src/**], contracts: [runtime spec v1.17 §14.C, C-AS-13 §13.2, ADR-D3], cross_axis: yes }
  skills: { primary: phase-7-implementation, secondary: [phase-7-back-flow-routing] }
  advisor_required: yes
  council_required: no
  verification: { shape: e2e, must_pass: ["Files arc design-phase opened (runtime plan unit)", "consumer landing at managed-cloud binding", "e2e: upload + reference-by-id + Batch-API discount composition"] }
  close_shape: { type: PR-merge, artifact: "feat(files): Files API consumption contract", cascade: [] }
  next_pointer: null
  notes: Operator opened the previously deferred Files arc on 2026-06-08. The design-phase shape is grounded in `.harness/class_1_fork_h_t_cp_16_17_executable_consumer_absence.md` §13.6.C (FilesAPIClient protocol + adapter, file_id reference composition, files.* emission) and implemented by the R-810 provider-free runtime port plus the real Anthropic Files adapter. Live managed-cloud proof uploaded plaintext file `file_011CbqJqTs21yENfK4xfEpqp`, referenced it by file_id, composed a Batch API request shape, exported `files.operation` through the authenticated managed collector, and observed Cloud Trace `bfd28fa8fc8ecc3ba973d1e405cdb865` with files.* attrs. The uploaded file is gone (cleanup retry returned Anthropic 404); temporary GCP TokenCreator IAM was removed. Closes AS-8e + CP-17 bounded-residuals. Register §B-11.

R-820-managed-agents-integration:
  title: managed_agents integration (managed_agents.* namespace — AS-8f)
  surface: IX
  status: RESOLVED
  depends_on: [R-421-managed-cloud-deployment-e2e]
  blocks: []
  posture: phase-7
  scope: { files: [harness-runtime/src/**], contracts: [runtime spec v1.33 §14.D, C-AS-13 §13.2, ADR-D3], cross_axis: yes }
  skills: { primary: phase-7-implementation, secondary: [] }
  advisor_required: yes
  council_required: no
  verification: { shape: e2e, must_pass: ["Anthropic managed_agents SDK integration authored", "production-surface managed_agents.* emission observed at managed-cloud"] }
  close_shape: { type: PR-merge, artifact: "feat(managed-agents): managed_agents integration", cascade: [] }
  next_pointer: null
  notes: RESOLVED 2026-06-07 by PR #380. Added the real Anthropic Managed Agents SDK/session adapter plus live managed-cloud e2e proof that created session `sesn_019aMgaF8sAW2cXhhpMTYij4`, observed `session.status_idle`, exported `managed_agents.runtime`, and confirmed Cloud Trace trace `009d7716b19c75e4ad7edb93e78f8d2b` carried `managed_agents.*` attributes. Temporary Cloud Run Token Creator IAM used only for the live proof was removed and verified absent after the run. This closes the R-820 runtime/integration gate; Phase-8 AS-8f substitution-tally movement, if any, remains a separate accounting/back-flow action.

R-830-memory-tool-production-backend:
  title: Memory-tool MANAGED_CLOUD production backend (cloud-vault / managed-db — CP-16) — managed-DB live-proven
  surface: IX
  status: RESOLVED    # managed-DB implementation + operator-approved Neon PostgreSQL live e2e passed
  depends_on: []
  blocks: []
  posture: phase-7    # optional managed-DB remainder is operator-gated (real service/creds/infra)
  scope: { files: [harness-runtime/src/harness_runtime/lifecycle/memory_tool_sqlite.py, harness-runtime/src/harness_runtime/lifecycle/memory_tool_filesystem.py, harness-runtime/src/harness_runtime/bootstrap/factories/memory_tool_registry_factory.py], contracts: [runtime spec v1.17 §14.12 C-RT-22, ADR-D3], cross_axis: no }
  skills: { primary: phase-7-implementation, secondary: [] }
  advisor_required: no
  council_required: no
  verification: { shape: e2e, must_pass: ["optional MANAGED_CLOUD managed-DB backend implements MemoryToolStorageBackendProtocol", "operator binds it via RuntimeConfig.memory_tool_backend_config with real connection_string/creds", "e2e read/write/delete against the real managed-DB backend (operator-gated on creds/infra)"] }
  close_shape: { type: PR-merge, artifact: "feat(memory): optional MANAGED_CLOUD managed-DB Memory-tool backend", cascade: [] }
  next_pointer: null
  notes: |
    SELF_HOSTED DATABASE backend (SQLite, stdlib sqlite3) LANDED earlier:
    SqliteMemoryToolBackend at lifecycle/memory_tool_sqlite.py implements the
    already-spec'd MemoryToolStorageBackend.DATABASE enum value; operator binds
    via memory_tool_backend_config; full read/write/delete e2e is provider-free
    (no creds, no new deps).

    MANAGED_CLOUD S3 cloud-vault backend also LANDED and was live-proven:
    S3MemoryToolBackend implements MemoryToolStorageBackend.S3 behind a narrow
    S3 client protocol; the approved live R-830 S3 e2e bound S3 on
    DeploymentSurface.MANAGED_CLOUD, used AWS CLI profile credentials, and
    exercised create/view/str_replace/insert/delete through the Memory tool
    dispatch seam. FILESYSTEM backend landed earlier (CP-16
    RETIRED-AS-BOUNDED-RESIDUAL batch-44).

    R-830 therefore no longer carries a pending S3/cloud-vault blocker.

    MANAGED_CLOUD managed-DB backend implementation ADDED and live-proven:
    ManagedSqlMemoryToolBackend implements MemoryToolStorageBackend.DATABASE
    for PostgreSQL-compatible managed databases; the factory selects it for
    postgres:// or postgresql:// backend_params['connection_string'] values,
    with optional psycopg construction isolated behind the factory. Provider-free
    unit coverage proves protocol conformance, path discipline, persistence,
    update semantics, and factory binding. The operator-approved live e2e bound
    R830_MANAGED_DB_CONNECTION_STRING to the Neon `Arhugula` PostgreSQL project
    and `just r830-managed-db-live-e2e` passed, exercising create/view/
    str_replace/insert/delete through the Memory tool dispatch seam with cleanup.
    Gate closure is logged at `.harness/codex_credential_gates.jsonl`.
    Register §B-13.
```

### 5.13 Existential / research (R-900..R-999) — Surface X

*Decomposed 2026-06-01 from register §B-16 (discharges §9 Surface X — single placeholder; surfaces opportunistically, not actively decomposed).*

```yaml
R-900-research-arcs:
  title: Open architectural / speculative arcs + research-corpus extensions
  surface: X
  status: RESOLVED   # 2026-06-08: decomposed the placeholder into R-901; R-XI-02/R-XI-03 were already RESOLVED, so Surface X now carries the next explicit non-credential frontier.
  depends_on: []
  blocks: []
  posture: mode-agnostic
  scope: { files: [.harness/01-planning/01-harness-planning/00-harness-research/**, design-substrate (opportunistic)], contracts: [], cross_axis: no }
  skills: { primary: systems-architect, secondary: [] }
  advisor_required: yes
  council_required: conditional:nameable-tension   # case-by-case, only if a named cross-domain tension surfaces
  verification: { shape: grep, must_pass: ["a specific research question is crystallized into a sub-entry before work begins"] }
  close_shape: { type: substrate-amendment, artifact: ".harness/01-planning/01-harness-planning/00-harness-research/** or a new R-90N sub-entry", cascade: [R-901] }
  next_pointer: R-901-phase-9-retirement-criteria
  notes: Placeholder decomposed 2026-06-08 into R-901. R-XI-02/R-XI-03 are already RESOLVED, so the selector should not keep advertising dashboard iteration work as open.

R-901-phase-9-retirement-criteria:
  title: Phase-9 retirement criteria research brief
  surface: X
  status: RESOLVED   # 2026-06-08 — research brief filed in the harness research corpus; result is research-only + roadmap selector guidance, no design-substrate back-flow.
  depends_on: []
  blocks: []
  posture: mode-agnostic
  scope: { files: [.harness/01-planning/01-harness-planning/00-harness-research/**, Project_Roadmap_v1.md], contracts: [], cross_axis: no }
  skills: { primary: systems-architect, secondary: [notebooklm] }
  advisor_required: yes
  council_required: conditional:nameable-tension
  verification:
    shape: grep
    must_pass:
      - "crystallize the Phase-9 retirement-criteria research question before any substrate amendment"
      - "ground the brief in the existing harness research corpus and cite source documents used"
      - "record whether the result is research-only, roadmap-only, or design-substrate back-flow"
  close_shape: { type: PR-merge, artifact: ".harness/01-planning/01-harness-planning/00-harness-research/phase-9-retirement-criteria.md or roadmap-only disposition", cascade: [] }
  next_pointer: null
  notes: >
    RESOLVED 2026-06-08: research brief filed at `.harness/01-planning/01-harness-planning/00-harness-research/phase-9-retirement-criteria.md`.
    Research question crystallized as a post-Phase-8 decision model: how to route bounded-residual
    promotion, live-ledger back-flow, and producer-gated CXA seams without rewriting the historical
    Phase-8 accounting declaration. Grounding sources: Phase-8 graduation, R-700 accounting draft,
    batches 51-55, retirement-event-pattern catalogue, NotebookLM Agent Harness Engineering query,
    and a supplemental Perplexity query. Result disposition: research-only + roadmap selector guidance;
    no design-substrate back-flow owed. Next selector returns to the remaining genuine producer-gated residual
    (`R-CXA-1`) unless a future `R-902` is explicitly opened for Phase-9 workflow
    mechanics or corpus ingestion.
```

### 5.14 Cross-axis composition seams (R-CXA-NN) — Surface I residual

*Decomposed 2026-06-01 from register §B-14 + closes the no-R-NNN-entry gap R-700 surfaced (draft §C item 2; A-3). Status spine = the R-700 dispositions merged at PR #207. These are mechanical wiring (runtime composer landings + production callers), not cross-domain tensions → council: no.*

```yaml
R-CXA-1-as-is-seam:
  title: CXA-1 (AS->IS) seam completion — scoped secret-fetch producer + edge-scope audit
  surface: I
  status: RESOLVED   # batch-56: AS->IS producer-gated seam substantively retired
  depends_on: []
  blocks: [R-700-phase-8-substitution-accounting]
  posture: phase-7
  scope: { files: [harness-runtime/src/harness_runtime/lifecycle/as_is_wiring.py, harness-as/src/**], contracts: [CXA v2.18 §2.3.1 (13 edges)], cross_axis: yes }
  skills: { primary: phase-7-cross-axis-composition, secondary: [] }
  advisor_required: no
  council_required: no
  verification: { shape: integration+overlay-audit, must_pass: ["workflow-time scoped secret-fetch production caller invokes emit_secret_fetch_audit_entry with non-hollow metadata — ✅ closed by PR #458", "remaining ~12 AS source-unit audit-emission callbacks threaded through AsIsWiring or narrowed/back-flowed by edge-scope audit — ✅ closed by .harness/r-cxa-1-as-is-edge-audit-2026-06-09.md + batch-56 sidecar wiring"] }
  close_shape: { type: retirement-event, artifact: ".harness/phase-7d-retirement-events-batch-56.md", cascade: [dashboard; register §B-14] }
  next_pointer: null
  notes: >
    Formerly PARTIAL per R-700: the AS->IS composer existed, but the scoped secret-fetch producer had no real
    workflow-time caller and the legacy CXA prose still implied "remaining ~12" callback sites. The bootstrap-value
    secret path remains excluded under the 2026-06-01 Reading-D decision in
    `.harness/class_1_fork_cxa_1_secret_fetch_audit_bootstrap_ordering.md`; wiring that path would still be hollow
    because it has name-only secret resolution and no scope/rotation metadata. PR #458 closed must_pass #1 by moving
    scoped secret-fetch audit production to `RuntimeToolDispatcher` at active `TOOL_STEP` dispatch with non-hollow
    scope and backend rotation metadata. Batch-56 closes must_pass #2: the edge-scope audit narrows current direct
    AS->IS obligations to U-AS-19/U-AS-28 read-only IS carrier imports plus the U-AS-26/U-AS-27 secret-fetch audit
    producer family, and this arc threads the R-003 procedural-tier sidecar through the production
    `RuntimeAsIsWiring` write. H_T-CXA-1 moves to `SUBSTANTIVE_RETIRED`; no non-retired substitution row remains.

R-CXA-2-cp-is-seam:
  title: CXA-2 (CP->IS) seam completion — runtime caller-site invocations + remaining §12.3 edges
  surface: I
  status: RESOLVED   # batch-55: CP->IS producer surface closed as counted bounded residual
  depends_on: []
  blocks: [R-700-phase-8-substitution-accounting]
  posture: phase-7
  scope: { files: [harness-runtime/src/harness_runtime/lifecycle/cp_is_wiring.py, harness-runtime/src/**], contracts: [CXA v2.18 §2.3.2, class_1_tension_u_rt_35_cp_is_wiring_gaps.md], cross_axis: yes }
  skills: { primary: phase-7-cross-axis-composition, secondary: [] }
  advisor_required: yes
  council_required: no
  verification: { shape: e2e, must_pass: ["6 §16.5 composer methods (U-CP-74..79) invoked at their firing sites + e2e", "remaining ~16 of 17 §12.3 edges materialized"] }
  close_shape: { type: retirement-event, artifact: ".harness/phase-7d-retirement-events-batch-55.md", cascade: [dashboard; register §B-14] }
  next_pointer: null
  notes: >
    STILL-BOUNDED per R-700 — cp_is_wiring PARTIAL-LAND; U-RT-35 unit landed (batch-46) but full contract
    STILL-BOUNDED. **GROUNDED 2026-06-02 (producer-discovery, [[r-cxa-seam-wiring-is-producer-discovery]] —
    3rd CXA seam grounded after R-CXA-1/R-CXA-4):** of the 6 §16.5 composer methods on
    `cp_is_wiring.py`, 3 now have production firing methods — `emit_pause_resume_state_ledger_entry`
    (workflow_driver.py:582/:808/:965), `emit_override_state_ledger_entry` (workflow_driver.py:859),
    and `emit_workload_class_selection` after the early CP→IS wiring / stage-3b workload-selection slice
    landed.
    **Advanced 2026-06-07:** the previously deferred `workflow_driver.py:965` HITL-signal caller-site now has
    direct integration coverage via
    `test_caller_site_pause_resume_protocol_emission_pause_captured_hitl_signal`; the test raises the real
    `HITLPauseRequestedSignal`, verifies `RunStatus.PAUSED`, `pause_reason=hitl_pending`, and persists the
    `cp.pause-resume-protocol` CP→IS ledger entry through `ctx.cp_is_wiring`.
    The remaining 3 are blocked by deliberately ratified upstream-loop gaps, NOT by missing placeholder
    ledger calls: (a) `emit_hitl_tool_call_rewriting` remains bounded because HITL disambiguator semantics
    (`semantic_variant_binding_id`) are spec-silent and `rewrite_tool_call` still has test callers only /
    0 production callers; (b)+(c) `emit_pause_captured` + `emit_resume_attempted` require production
    engine-layer recovery loops for `capture_pause_snapshot` + `attempt_resume`. At that point R-CXA-2 had the
    same producer-discovery shape as R-CXA-1 (DEFER) + R-CXA-4 (0 wireable): **3/6 fired, 3/6 gated on
    future HITL rewrite / engine recovery-loop producers**. Wiring static tool-dispatch or ledger-only
    placeholders would be the silent X-AL-3 extension the U-RT-111 saga forbade. NO clean
    Claude-executable wiring slice exists at current MVP scope. **2026-06-08 refresh audit at HEAD
    `4baefe0b` reaffirmed the producer gate:** `rewrite_tool_call(...)` still has no production
    LLM/tool inner-loop caller, workflow-driver pause/resume sites already emit the workflow-layer
    `cp.pause-resume-protocol` action rather than the engine-layer `cp.pause-captured` /
    `cp.resume-attempted` actions, and the free-function engine-layer surfaces remain substrate APIs
    without a recovery-loop producer. Evidence: `.harness/r-cxa-2-producer-audit-2026-06-08.md`.
    This pre-PR-449 state was superseded by the producer primitives, stage-5 composition, provider-turn HITL
    continuation, and batch-55 bounded-residual close recorded below. Register §B-14.
    **2026-06-08 producer-seam DESIGN SPEC filed and ratified** — `.harness/r-cxa-1-2-producer-seam-spec.md` §3–§4 specs the
    3 producers + files 2 forks: `class_1_fork_u_cp_78_pause_captured_type_impedance.md` (Class 1 DEFECT — the
    engine-layer `cp.pause-captured` composer consumes the workflow-layer `PauseSnapshot` while its named producer
    `capture_pause_snapshot()` emits the engine-layer `PauseEvent`; resume-attempted has no such mismatch) +
    `class_2_fork_r_cxa_2_producer_loop_ownership.md` (DP-1 HITL model-driven inner-loop firing site / DP-2
    engine recovery-loop ownership / DP-3 pause-resume disambiguator derivation `pause_event_id`/`resume_event_id`/
    `resume_attempt_count`). HITL `semantic_variant_binding_id = variant.value` cited as SETTLED (runtime plan
    v2.39 Reading B). 2026-06-08 ratification selected U-CP-78 Reading A; DP-1(c) bounded-residual defer for the absent
    model-driven HITL inner loop; DP-2(c) bounded-residual defer for the absent engine recovery loop; DP-3(a) future
    recovery-loop-context-supplied opaque identities. No new ADR (decisions are spec/plan-granularity; native mechanism =
    the fork docs); no PRD (internal architecture). Producer gaps now SPECIFIED + RATIFIED, but R-CXA-2 has no MVP
    wireable producer; hollow callers remain disallowed.
    **2026-06-09 PR #449 advanced the post-MVP build:** U-CP-78 Reading A is applied in CP/runtime code so
    `cp.pause-captured` consumes engine-layer `PauseEvent`; runtime now has provider-neutral
    `RuntimeHITLToolLoop` and `RuntimeEngineRecoveryLoop` producer primitives with focused CP/runtime tests and green
    overlay/CI. **2026-06-09 PR #452 advanced Slice 4/5:** bootstrap LOOP_INIT now binds both
    primitives onto `HarnessContext` and focused tests prove direct CP→IS producer emissions through the bound
    runtime context (`cp.hitl-tool-call-rewriting`, `cp.pause-captured`, `cp.resume-attempted`). **2026-06-09
    PR #454 closed the provider-turn HITL producer:** Anthropic non-memory `tool_use` continuation now runs through
    `ctx.hitl_tool_loop` and returns `tool_result` continuation messages. **2026-06-09 batch-55 closes the live-ledger
    residual as bounded residual:** R-CXA-2 is RESOLVED-AS-BOUNDED-RESIDUAL. The durable/journaled recovery loop is
    still not claimed as substantive production evidence; it remains an explicit re-open trigger for a future
    event-sourced replay, reconciler-loop, WAL-segment, or engine-native-pause recovery implementation.

R-CXA-3-cp-as-seam:
  title: CXA-3 (CP->AS) seam — runtime composer
  surface: I
  status: RESOLVED   # batch-54: CP->AS runtime composer landed and H_T-CXA-3 retired
  depends_on: []
  blocks: [R-700-phase-8-substitution-accounting]
  posture: phase-7
  scope: { files: [harness-runtime/src/harness_runtime/lifecycle/cp_as_wiring.py, harness-runtime/src/harness_runtime/bootstrap/stage_6_cxa_wiring.py, harness-runtime/src/harness_runtime/bootstrap/mutable_context.py, harness-runtime/src/harness_runtime/types.py], contracts: [CXA v2.18 §2.3.3 (24 edges), ledger §11.1b], cross_axis: yes }
  skills: { primary: phase-7-cross-axis-composition, secondary: [] }
  advisor_required: yes
  council_required: no
  verification: { shape: pytest, must_pass: ["RuntimeCpAsWiring materializes CP-consumed AS terminal seam exports", "stage 6 binds cp_as_wiring", "HarnessContext exposes cp_as_wiring", "batch-54 moves H_T-CXA-3 to SUBSTANTIVE_RETIRED"] }
  close_shape: { type: PR-merge, artifact: "feat(cxa): add CP->AS runtime composer", cascade: [dashboard; register §B-14; substitution-ledger batch-54] }
  next_pointer: null
  notes: >
    RESOLVED 2026-06-08 at batch-54. Operator explicitly rejected MVP scope narrowing and directed the runtime-composer path.
    `RuntimeCpAsWiring` now materializes the CP-consumed AS terminal seam export registry at bootstrap stage 6,
    fail-closes on AS manifest coverage drift, and is exposed as `HarnessContext.cp_as_wiring`. Focused lifecycle
    and bootstrap tests prove the composer shape, identity binding, coverage check, and frozen-context exposure.
    H_T-CXA-3 moves from STILL_BOUNDED to SUBSTANTIVE_RETIRED. Batch-55 later moves CXA-2 to
    BOUNDED_RESIDUAL, leaving CXA-1 as the only non-retired CXA row.

R-CXA-4-od-multi-seam:
  title: CXA-4 (OD->IS/AS/CP) seam — GROUNDED-NO-WIREABLE; NO cleanup task (placeholders resolved at v2.3/v2.11); probe surfaced+fixed v2.18 matrix defect (CXA v2.19)
  surface: I
  status: RESOLVED   # batch-53: bookkeeping-only PARTIAL row back-flowed to SUBSTANTIVE_RETIRED
  depends_on: []
  blocks: [R-700-phase-8-substitution-accounting]
  posture: design-phase    # the convention-formalization follow-on was a PHANTOM (placeholders already resolved at v2.3/v2.11); the design-phase work that DID surface was the CXA v2.19 correction of v2.18's erroneous matrix
  scope: { files: [design-substrate/Cross_Axis_Composition_Document_v2_19.md (corrects v2.18's erroneous §2.1 matrix + aggregate)], contracts: [CXA v2.3 §2.3.5-§2.3.6 (OD-outbound placeholders ALREADY RESOLVED to real unit IDs); OD plan v2.11 (mirror resolution)], cross_axis: yes }
  skills: { primary: spec-writer, secondary: [council-orchestrator] }
  advisor_required: no
  council_required: no    # nameable-tension discriminator: no real voice-tension; fidelity-pure count-correction
  verification: { shape: grep, must_pass: ["NO cleanup task remains — the U-AS-NN/U-CP-NN placeholders were resolved at CXA v2.3 + OD plan v2.11; the probe of the phantom follow-on instead surfaced+corrected v2.18's erroneous §2.1 matrix (CXA v2.19, aggregate 105->107); batch-53 accounting/back-flow moves the 0-wireable bookkeeping row to SUBSTANTIVE_RETIRED"] }
  close_shape: { type: retirement-event, artifact: ".harness/phase-7d-retirement-events-batch-53.md", cascade: [dashboard; register §B-14] }
  next_pointer: null
  notes: |
    CORRECTED 2026-06-01 (probe of the R-CXA-4 follow-on, operator-picked "Also probe the v2.18 §2.4 defect"). The prior framing ("stale U-AS-NN/U-CP-NN placeholders; CXA convention-formalization revision owed, mirroring v2.18 C3-15") was ITSELF a wrong-version-read mis-framing (CLAUDE.md §10.5): the OD->AS/OD->CP placeholders were RESOLVED to real producer unit IDs at CXA v2.3 (2026-05-17; e.g. U-OD-17->U-AS-14, U-OD-29->U-AS-15(G), U-OD-23->U-CP-46) and at OD plan v2.11 (2026-05-16, Form A; resolution table .harness/cxa_7c_placeholder_resolution.md). The §2.3.5/§2.3.6 row-table headers appear only in v2.1/v2.2/v2.3 → v2.3 is canonical HEAD; every v2.4-v2.18 delta preserves them verbatim. THERE IS NO CLEANUP TASK at CXA or the OD plan; the prior register/roadmap framing read the v2.1 baseline.
    The probe of that phantom follow-on surfaced a real defect in v2.18: it re-absorbed the C3-15 OD->IS cleanup already done at v2.3 (same wrong-version-read), corrupting the §2.1 matrix (AS->IS 13->11, CP->OD 0->8, OD->CP 8->12) and publishing aggregate 105 (correct = 107) + a downstream-fabricated 37/48/20 sub-split (correct = 37/48/22). v2.18's OD->IS=4 / OD-outbound=26 end-state was already correct since v2.3 and is preserved. Fixed at CXA v2.19 (this PR) + CLAUDE.md §1.1/§2.4 + clearance marker. "CXA-OD-IS-EDGE-DRIFT" halt-doc Item 11 was a PHANTOM drift (CXA already conformed at v2.3).
    SUBSTANTIVE conclusion preserved: R-CXA-4 = 0 wireable edges (1 genuine OD->IS seam already wired at 4 producers; 6 phase-2-runtime already at bootstrap stage 6; convention edges discharged by §3 Pattern P1 + stage-6 verify_*). ZERO production code. No further Claude-executable follow-on remained; batch-53 consumes the bookkeeping/accounting residual and moves R-CXA-4 to `SUBSTANTIVE_RETIRED`. Register §B-14. Mirrors R-CXA-1 producer-discovery [[r-cxa-seam-wiring-is-producer-discovery]] + the wrong-version-read lesson [[wrong-version-read-delta-only-baseline]].
```

---

### 5.15 Post-MVP full closure track (R-CL-NN) — the spec-closure spine

> Authored 2026-06-10 per operator directive "develop the full harness to closure." The execution spine is `.harness/post-mvp-full-closure-plan-v1.md`; the P0 scope-lock (verified against HEAD `37b7c80`) is `.harness/closure-p0-scope-lock.md`. These 13 entries register the plan's phases. **Operator override** (§4): the closure track is the directed active work; `next_action` points into it. Quality phases (Q/D/C) gate on the capability phases (P) per the plan §7 graph.

```yaml
R-CL-P0:
  title: Phase 0 — ground + scope-lock + file design-gated forks
  surface: I-closure
  status: RESOLVED     # closed #477 (scope-lock merged + operator-ratified merge-and-proceed)
  depends_on: []
  blocks: [R-CL-P1, R-CL-P2, R-CL-P3, R-CL-P4, R-CL-P5, R-CL-P6]
  posture: mode-agnostic
  scope: { files: [.harness/closure-p0-scope-lock.md, .harness/class_1_fork_prompts_management_surface_active_prompt_version.md, .harness/class_1_fork_keying_tuple_entry_shape_d_adr.md], contracts: [], cross_axis: no }
  skills: { primary: null, secondary: [] }
  advisor_required: yes
  council_required: no
  verification: { shape: e2e, must_pass: ["every Cat-1..4 surface re-verified vs HEAD incl. the register's CLOSED claims; 2 design-gated forks filed; scope frozen in closure-p0-scope-lock.md"] }
  close_shape: { type: PR-merge, artifact: "scope-lock PR", cascade: [R-IF-roadmap-refresh] }
  next_pointer: R-CL-P1
  notes: |
    Verified 2 material register corrections: (C-1) sandbox Docker/gVisor/E2B drivers exist+e2e but are NOT selected by the production dispatcher (factory omits tool_execution_driver=) → NEW item folded into P2; (C-2) routing is Cat-1 PURE IMPL (C-CP-02 §2.1 specifies shape; params impl-discretion) → no fork. Exit gate: operator ratifies the frozen scope + the 2 forks.

R-CL-P1:
  title: Phase P1 — routing intelligence (EMBEDDING + LLM_AS_ROUTER layers + capability-shortfall fallback)
  surface: IV
  status: RESOLVED     # 2026-06-16 — superseded by R-FS-1 (FULL-SPEC directive re-opened the bounded-residual; the re-open trigger fired): capability-shortfall fallback LANDED #479; LLM_AS_ROUTER L3 BUILT at arc R (#602 mock / #604 real Ollama); EMBEDDING L2 BUILT at arc R (#606, Option B fastembed). Production-activation residual = the UNOWNED routing-activation gate, tracked forward at roadmap_status.md "## Remaining forward work" + B-L2-EMBEDDING-ACTIVATION.
  depends_on: [R-CL-P0]
  blocks: [R-CL-Q1, R-CL-Q2, R-CL-Q3]
  posture: phase-7
  scope: { files: [harness-cp/src/.../layered_routing_strategy.py, harness-runtime/src/.../llm_dispatch.py], contracts: [C-CP-02, C-CP-03, C-CP-04], cross_axis: no }
  skills: { primary: phase-7-implementation, secondary: [harness-adversarial-reviewer] }
  advisor_required: yes
  council_required: conditional:nameable-tension   # cost ⊥ reliability ⊥ capability-preservation (dyadic)
  verification: { shape: e2e, must_pass: ["a capability-requiring step routes to a capable provider before failing; an EMBEDDING/LLM_AS_ROUTER escalation fires on an ambiguous route; per-layer LayerBudget bounds each layer; no LCD capability flattening"] }
  close_shape: { type: PR-merge, artifact: "routing-intelligence PR(s)", cascade: [R-IF-roadmap-refresh] }
  next_pointer: R-CL-P2
  notes: |
    RESOLVED 2026-06-16 — superseded by R-FS-1 arc R (see status). Deferral history retained below as record.
    PARTIAL (#479). Council SKIPPED — grounding falsified the ⚖️ flag (policy spec-pinned at C-CP-02 §2.1/§2.2 + C-CP-03 §3.2/§3.3; operator chose build-direct).
    LANDED: C-CP-03 §3.3 capability-shortfall fallback (pre-dispatch check in RetryBreakerFallbackDispatcher; the capability-preservation axis) + Codex-caught reflect_provider_capabilities real-model-ID fix (P1) + exhaustion-cause telemetry (P2).
    DEFERRED (X-AL-3-documented, re-open triggers at .harness/r-cl-p1-routing-intelligence-plan.md): EMBEDDING (no trained corpus/embedding model; §2.2 fall-through correct until a corpus exists) + LLM_AS_ROUTER (faithful async router-call would widen cleared sync U-CP-03/U-CP-05 — not silently absorbable).
    FOLLOW-UPS: params['thinking']=={"type":"disabled"} would false-positive the THINKING derivation (latent — no current emitter found; 2-line guard); capability-shortfall is unit-verified only (mock inner + hand-built chain) — e2e/production-config reachability → R-CL-Q3.

R-CL-P2:
  title: Phase P2 — engine-recovery activation + external-engine seam (sandbox C-1 unbundled → R-410-family)
  surface: V
  status: RESOLVED     # 2026-06-16 — superseded by R-FS-1 (FULL-SPEC directive re-opened the bounded-residual; DP-2 trigger fired): engine-recovery / durable engine classes BUILT at arc E (#562–#576, incl. RECONCILER_LOOP engine-layer go-live #576); tier→driver sandbox execution BUILT via R-410-family + #503. Residuals tracked forward at roadmap_status.md "## Remaining forward work" (B6 per-tool sandbox / B-TOOL-GATE / B-EFFECT-FENCE / B-ENGINE-OUTPUT-REPLAY).
  depends_on: [R-CL-P0]
  blocks: [R-CL-Q1, R-CL-Q2, R-CL-Q3]
  posture: phase-7
  scope: { files: [harness-runtime/src/.../runtime_tool_dispatcher_factory.py, harness-runtime/src/.../engine_recovery_loop.py, harness-runtime/src/.../journal_pause_resume_substrate.py (PR #475)], contracts: [C-CP-07, C-CP-08, C-CP-22], cross_axis: yes }
  skills: { primary: phase-7-implementation, secondary: [harness-adversarial-reviewer] }
  advisor_required: yes
  council_required: conditional:nameable-tension   # C10 blast-radius ⊥ C11 operator-burden
  verification: { shape: e2e, must_pass: ["a production TOOL_STEP resolved to TIER_2/3/4 actually executes in the Docker/gVisor/E2B driver (tier→driver selection seam wired); the engine recovery loop drives the bound durable F2 substrate through capture→restart→resume; SAVE_POINT reference adapter passes its deterministic contract test"] }
  close_shape: { type: re-open-on-DP-2-trigger, artifact: "n/a (DEFERRED)", cascade: [R-IF-roadmap-refresh] }
  next_pointer: R-CL-P3
  notes: |
    RESOLVED 2026-06-16 — superseded by R-FS-1 arc E (see status). Deferral history retained below as record.
    DEFERRED at entry-grounding 2026-06-10 (`.harness/r-cl-p2-engine-recovery-grounding.md`; advisor-confirmed). The buildable, non-hollow Phase-7 slice is empty:
    - Engine-recovery DRIVER: producer-discovery-empty by RATIFIED disposition — forward-register line 181 (CXA-2 = RETIRED-AS-BOUNDED-RESIDUAL, batch-55): "do not wire workflow_driver.py as a fake engine recovery loop; re-open only when a real event-sourced-replay / reconciler-loop / WAL-segment / engine-native-pause loop lands." Engine-layer loop has NO production caller (only tests); the engines that would emit engine-layer pauses are I-6 no-vendor. Building = fake-producer anti-pattern + X-AL-3. Do NOT bind #475 Journal substrate into the factory (cosmetic — nothing calls ctx.engine_recovery_loop; would force PathClass enum extension = IS-AL-1 violation, for zero production benefit).
    - SAVE_POINT reference adapter: speculative (its only consumer is the dormant recovery loop → zero consumers); live-proof deployment-gated per D-2.
    - HITL OQ-5/7: hollow (retry_breaker_fallback/retry_breaker do not compose with hitl_tool_loop; no per-tool-call turn journal; no production scenario fires fallback/breaker mid-HITL-turn). OQ-6 timeout degradation: thin-latent (factory passes timeout_seconds=None, no config path → branch never fires) — captured as a Q-phase robustness latent gap.
    ROADMAP-HYGIENE: the prior title bundled "sandbox driver→dispatch wiring (C-1)", which closure-plan §P2 does NOT contain. UNBUNDLED → R-410-family finding: production tier→driver SELECTION is unwired (factory omits tool_execution_driver=; no tier/tech/provider→driver registry; every TOOL_STEP runs in-process regardless of resolved TIER_2/3/4 — enforcement is test-injection-only, a real security-posture gap). Design-adjacent: the R-410 fork (APPLIED-AS-BOUNDED-READING-B) frames tier→mechanism as a design-phase contract; spec v1.41 §14.9.8 dangles consumption as "future-arc"; R-410/411/412 deliberately closed with injected-driver e2e. file-don't-build (X-AL-1-clean).

R-CL-P3:
  title: Phase P3 — persona-tier TEAM_BINDING breadth (e2e proof of the bridging-arc middle tier)
  surface: VI
  status: APPLIED-PENDING-OPERATOR-E2E   # #481 (2026-06-10): infra-free run-observable posture proofs LANDED (sampler full config→bootstrap flow + gate runtime-resolver, TEAM distinct from both neighbours, non-vacuous); §10.2 reconciled (mode-agnostic, NOT design-substrate — Persona_Document un-drifted). PENDING operator-gated sub-step: full-workflow live multi-tier e2e (api.run echo-MCP is skipif-gated/infra) + the redaction collector-boundary proof (deployment, not in-process) + cost (U-RT-49 struck). Partial-land per D-2 build-seam-defer-live-proof.
  depends_on: [R-CL-P0]
  blocks: [R-CL-Q1, R-CL-Q2, R-CL-Q3]
  posture: phase-7
  scope: { files: [harness-cp/src, harness-od/src, harness-as/src (TEAM_BINDING branch-points)], contracts: [C-CP-19, C-OD-10, C-OD-13], cross_axis: yes }
  skills: { primary: phase-7-implementation, secondary: [harness-adversarial-reviewer] }
  advisor_required: yes
  council_required: conditional:nameable-tension   # C7 observability + C8 security ⊥ C11 operator-burden
  verification: { shape: e2e, must_pass: ["a TEAM_BINDING workflow exhibits the correct HITL-gate/redaction/sampler/cost posture distinct from SOLO and MULTI_TENANT; reconcile root CLAUDE.md §10.2 persona drift"] }
  close_shape: { type: PR-merge, artifact: "#481 team-binding posture proof", cascade: [R-IF-roadmap-refresh] }
  next_pointer: R-CL-P5
  notes: |
    PARTIAL-LAND (#481, advisor-confirmed; harness-runtime/tests/test_r_cl_p3_persona_tier_posture.py — 9 tests). BUILD-NOT-FORK confirmed (TEAM_BINDING branches across all 4 axes). Grounding refined the deliverable: of the 4 §P3 behaviours, only 2 are in-process run-observable, and they ARE proven tier-distinct (TEAM ≠ both neighbours, non-vacuous):
    - SAMPLER (OD obs): SELF_HOSTED base-rate 1.0/0.1/0.2 via the REAL bootstrap (config.persona_tier → materialize_tracer_provider_stage → bound HarnessCompositeSampler) — full config→runtime flow.
    - GATE (CP HITL): SAVE_POINT_CHECKPOINT synchrony SYNC_BLOCKING/BOTH_BY_TIER/DURABLE_ASYNC via the runtime _evaluate_cell_synchrony resolver (binding-layer proof).
    PENDING (operator-gated / not-in-process, per D-2): full-workflow live multi-tier e2e (api.run echo-MCP skipif-gated/infra) + full config→binding→gate flow (CP step-binding path, infra-free but unbuilt) ; REDACTION = OTLP-collector-boundary deployment posture (not in-process-observable) ; COST = U-RT-49-struck (RunResult.cost_attribution empty). §10.2 root-CLAUDE.md persona drift RECONCILED (mode-agnostic; Persona_Document verified un-drifted → no clearance marker).

R-CL-P4:
  title: Phase P4 — spec-completion deferrals (prompts surface + 3rd hash component; keying-tuple D-ADR; OD buffer bounds)
  surface: I-closure
  status: RESOLVED     # all 3 sub-parts closed: OD tail-keep buffer (#490, OD v1.28) + keying-tuple reading-(iii) (#492, IS v1.4) + prompts/active_prompt_version 3rd hash component (#496, IS v1.5 + runtime v1.42, APPLIED-AS-MINIMAL-BINDING). The Q/D/C quality track is now UNBLOCKED.
  depends_on: [R-CL-P0]   # AND the 2 P0 forks ratified (design-before-build)
  blocks: [R-CL-Q1, R-CL-Q2, R-CL-Q3]
  posture: design-phase   # then bundled-absorption into phase-7 (clearance markers)
  scope: { files: [design-substrate/Spec_Information_Substrate_v1.x, harness-runtime/src (prompts carrier), harness-od/src (buffer bounds)], contracts: [C-IS-05 §5.2, C-IS-07 §7.4, C-OD-09 §9.3], cross_axis: yes }
  skills: { primary: spec-writer, secondary: [systems-architect, implementation-planner] }
  advisor_required: yes
  council_required: no
  verification: { shape: e2e, must_pass: ["procedural-tier snapshot includes the prompt-version 3rd hash component; keying-tuple↔entry-shape reading ratified + §7.4 cite refreshed; tail-keep buffer bounded under a pathological producer; clearance markers filed"] }
  close_shape: { type: PR-merge, artifact: "spec-completion PR(s) + clearance markers", cascade: [R-IF-roadmap-refresh] }
  next_pointer: R-CL-Q1
  notes: >
    RESOLVED 2026-06-11 — all 3 sub-parts closed. (1) OD tail-keep bounded-buffer (C-OD-09 §9.3,
    Category-1 Claude-closeable) — #490, OD spec v1.28: CollectorConfig.tail_keep_max_buffered_traces +
    tail_keep_max_spans_per_trace (drop-oldest + per-trace overflow drop, both counted); clearance
    marker Spec_Operational_Discipline-v1_28-cleared-2026-06-10. (2) keying-tuple D-ADR (C-IS-07 §7.4) —
    #492, IS spec v1.4: RATIFIED reading (iii) + §7.4→§7.5 flip + stale F2-12 cite refresh; doc-only
    docstring reconciliation; fork class_1_fork_keying_tuple_entry_shape_d_adr.md RESOLVED. (3) prompts /
    active_prompt_version 3rd hash component (C-IS-05 §5.2) — #496, APPLIED-AS-MINIMAL-BINDING: IS spec
    v1.5 (recipe 2→3-component) + runtime spec v1.42 (prompt_manifest at §3 RuntimeConfig + §4
    HarnessContext + stage-0 copy) + harness_is.prompt_manifest carriers (mirror RoutingManifest);
    clearance markers Spec_Information_Substrate-v1_5 + Spec_Harness_Runtime-v1_42-cleared-2026-06-11;
    fork class_1_fork_prompts_management_surface_active_prompt_version.md APPLIED.
    SCOPE-RECONCILE: this entry had carried "FULL prompts-management scope" — a never-applied prior-session
    memory capture; the P0-ratified closure-plan scope (#477) + fork DP-4 both pin MINIMAL binding, and the
    operator's 2026-06-11 AUQ chose minimal → closed at minimal (mirror RoutingManifest, close the §5.2
    deferral); fuller versioning/selection surface deferred per DP-4 (re-openable). The Q/D/C quality track
    (R-CL-Q1..C1) is now unblocked.

R-CL-P5:
  title: Phase P5 — CXA phase-2 edge verification + cost-model rate tables + validator thresholds
  surface: I-closure
  status: RESOLVED     # verify-emit close 2026-06-10 (advisor-confirmed, 2-pass decorrelation). All three sub-parts grounding-falsified the "build" framing: CXA edges already materialized at stage 6; cost default table + chain already wired through bootstrap; validator sub-part = mis-cited already-built surfaces. Record: `.harness/r-cl-p5-cxa-cost-validator-verification.md`.
  depends_on: [R-CL-P0]
  blocks: [R-CL-Q1, R-CL-Q2, R-CL-Q3]
  posture: phase-7
  scope: { files: [harness-runtime/src/.../stage_6_cxa_wiring.py, harness-runtime/src/.../cp_is_wiring.py, harness-od/src (cost), harness-cp/src (validator)], contracts: [CXA v2.19 §2.3.x, C-OD-14 (cost — NOT C-OD-17, which is eval primitives), ADR-D2 §2.3/§332(d) + D5 §1.5 (validator↔tier — NOT §1.9, which is sandbox-pool warm-up)], cross_axis: yes }
  skills: { primary: phase-7-implementation, secondary: [phase-7-cross-axis-composition] }
  advisor_required: no
  council_required: no
  verification: { shape: e2e, must_pass: ["each GENUINE phase-2 edge has an executed producer-emit proof (0-wireable ones recorded honestly, NOT padded); cost attribution produces correct non-zero figures on a real dispatch; a validator fires at its tier threshold; stage_6_cxa_wiring.py:4 doc-drift 24→22 fixed"] }
  close_shape: { type: PR-merge, artifact: "R-CL-P5 cxa-verify+cost+validator verify-emit PR + verification record", cascade: [R-IF-roadmap-refresh] }
  next_pointer: R-CL-P6
  notes: |
    VERIFY-EMIT close (not a build). Per-edge disposition + decorrelation record at `.harness/r-cl-p5-cxa-cost-validator-verification.md`.
    - CXA (must_pass #1+#4): 24 §2.3.x R-tagged edges = 14 producer-emit + 7 convention/0-wireable/runtime-delegated + 3 DEFERRED (U-CP-12 + U-CP-52, X-AL-3 per U-RT-35 — NOT rescued). U-CP-34→U-IS-08/09 are runtime-delegated inside the IS append (the genuine U-IS-11 sibling seam is separate). U-CP-74..79 back-flow landed (cp_is_wiring docstring was stale; reconciled). stage_6_cxa_wiring.py:4 24→22 fixed (canonical CXA v2.19 §2.1; the §2.3-rows-24-vs-§2.1-aggregate-22 gap = Class 3 residual routed to a future CXA fidelity-pass).
    - COST (must_pass #2): RATE_TABLE_V1 (U-OD-47 default) already wired through bootstrap (stage_4_od + stage_5_loop_init) into tool/validator/LLM dispatch; non-zero proven against RATE_TABLE_V1 at `test_lifecycle_cost_attribution_llm_dispatch.py` (LLM path — tool_rates ship empty); fires-through-bootstrap at `test_r100_real_workflow_e2e.py` AC#4. `RunResult.cost_attribution=()` aggregate-surfacing stays U-RT-49-bounded.
    - VALIDATOR (must_pass #3): roadmap mis-cited ADR-D2 §1.9 (=warm-up). Already-built surfaces: validator fires post-step (`validator_framework.py`); `sandbox_tier` is the 5th gate-level floor (ADR-D2 §332(d)); sandbox-violation→escalation staircase (§2.3/§1.8 + D5 §1.5). Verify-emit; NO row-11 built (X-AL-3); no design fork owed.

R-CL-P6:
  title: Phase P6 — spec-prose ↔ impl hygiene (reconcile stale spec footers to landed reality)
  surface: VII
  status: RESOLVED     # closed 2026-06-10 by AS spec v1.8→v1.9 footer reconciliation + clearance marker (`.harness/clearance/Spec_Action_Surface-v1_9-cleared-2026-06-10.md`). §14.5 managed_agents footer gained a leading Supersession(v1.9) banner; §14.6 files.* producer-site footer authored; stale v1.7 title → v1.9; overlay-check clean; cross-spec rg negative confirmed (sibling hits all frozen change-note blocks). harness-as/CLAUDE.md narrative drift (Phase-7 posture) filed as R-CL-Q1 follow-on, NOT bundled (§11.4). [was: ACTIVE, promoted from BLOCKED, depends_on R-CL-P0+P5 RESOLVED.] R-CL-P4 stays BLOCKED-on-forks; the Q/D/C quality track gates on P4.
  depends_on: [R-CL-P0]
  blocks: [R-CL-Q1, R-CL-Q2, R-CL-Q3]
  posture: design-phase
  scope: { files: [design-substrate/Spec_Action_Surface_v1.x (C-AS-14 §14.5/§14.6)], contracts: [C-AS-14], cross_axis: no }
  skills: { primary: spec-writer, secondary: [harness-adversarial-reviewer] }
  advisor_required: no
  council_required: no
  verification: { shape: grep, must_pass: ["AS Files/managed-agents 'deferred indefinitely' footers refreshed to landed R-810/R-820 reality; overlay-check clean (no stale tracked snapshots, no HARD seam-missing-endpoint); cross-spec rg clean; clearance markers filed"] }
  close_shape: { type: PR-merge, artifact: "spec-prose-hygiene PR + clearance markers", cascade: [R-IF-roadmap-refresh] }
  next_pointer: null
  notes: The [[spec-prose-plan-body-drift-pattern]] class. RECONCILED — Files/managed-agents footers refreshed from "deferred indefinitely" to the landed R-810/R-820 reality (substitutions.yaml AS-8e/8f/CP-17 = SUBSTANTIVE_RETIRED batch-52). Verified premise TRUE before touching prose (authoritative ledger, not the roadmap's own cite). Frozen historical change-note blocks preserved per stale-carry-text disposition (rg hits remain by construction). Producer-sites are code adapters (files_api.py / managed_agents.py), no phantom C-RT-NN footer cite.

R-CL-Q1:
  title: Phase Q1 — DevEx + whole-codebase code-review & simplification sweep
  surface: VII
  status: RESOLVED    # closed 2026-06-29 by PR #833 (`f2831cbe`): final structured Q1 review artifact covers all seven packages plus tools/, justfile, and harness.toml.example; clean-checkout-to-green DevEx path and provider-free `just check` verified.
  depends_on: [R-CL-P4, R-CL-P5, R-CL-P6, R-CC-1, R-PM-1, R-FS-1]   # +R-FS-1 (full-spec build program) per §5.0. P1/P2/P3 stay dropped as R-CC-1-subsumed (their open items reopened AS BUILD under R-FS-1, not as Q1 deps). R-FS-1 is now resolved; Q1 admits because the full spec is built.
  blocks: [R-CL-Q4]
  posture: phase-7
  scope: { files: [harness-*/src, justfile, harness.toml, tools/], contracts: [], cross_axis: yes }
  skills: { primary: harness-adversarial-reviewer, secondary: [] }
  advisor_required: yes
  council_required: no
  verification: { shape: e2e, must_pass: ["per-package review pass (codex + /code-review + /simplify) with all findings closed; clean-checkout-to-green DevEx walkthrough; just check green at a verified fixed point"] }
  close_shape: { type: PR-merge, artifact: "code-review/devex sweep PR(s)", cascade: [R-IF-roadmap-refresh] }
  next_pointer: null
  notes: Workflow candidate (broad parallel audit) if operator opts in. Clean/simple/commented code; no dead code, no over-abstraction. FOLLOW-ON closed by `r-cl-q1-as-substitution-posture-drift`: `harness-as/CLAUDE.md` now points AS-axis counts at the derived substitution ledger and records AS-8e/AS-8f as `SUBSTANTIVE_RETIRED` batch-52; `tools/test_substitution_ledger.py` guards the stale-posture regression. ALSO INHERITED FROM R-CL-P6 (closure-plan P6 Work bullet 3, an attempt-item NOT in P6's verification gate — explicitly deferred here, not dropped, per §10.5 anti-silent-narrowing): "confirm every Cat-4 impl-discretion footer is satisfied-or-bound and recorded." P6 confirmed only its own touched footer — C-AS-14 §(line 1303) impl-discretion (OTel/OTLP exporter per cell) is satisfied-or-bound (R-810/R-820 landed the exporter for files/managed_agents; spec-level deferral remains correct). The CROSS-AXIS Cat-4 sweep (git cadence, canonicalization library binding, worktree naming, composer caching shape, validator-tier thresholds — IS/CP/runtime specs per closure-plan §1 row 4) is Q1's broad-impl-discretion-audit territory: confirm-and-record each is satisfied-or-still-bound, don't build. FOLLOW-ON closed by `r-cl-q1-runtime-contract-id-collisions`: runtime contract-ID hygiene now has `tools/test_runtime_contract_ids.py`; the later-used §14.21 `InterStepOutputChannel` is `C-RT-34` and §30 `resume()` is `C-RT-35`, while v1.35 §14.18 `HarnessRunCLI` remains `C-RT-29` and §14.19 `WorkflowManifestLoader` remains `C-RT-30`.

R-CL-Q2:
  title: Phase Q2 — security testing + review
  surface: VII
  status: RESOLVED    # 2026-06-29 — PR #835 landed the Q2 security review/threat model and fixed the mutable GitHub Actions supply-chain finding.
  depends_on: [R-CL-P1, R-CL-P2, R-CL-P3, R-CL-P4, R-CL-P5, R-CL-P6]
  blocks: [R-CL-Q4]
  posture: phase-7
  scope: { files: [harness-*/src, uv.lock], contracts: [], cross_axis: yes }
  skills: { primary: null, secondary: [harness-adversarial-reviewer] }
  advisor_required: yes
  council_required: conditional:nameable-tension   # C8 security ⊥ C11 operator-burden
  verification: { shape: e2e, must_pass: ["threat-model doc + per-surface test (sandbox isolation/secrets/MCP-trust/redaction/audit-integrity/supply-chain); /security-review; every finding fixed-or-risk-accepted; no secret/PII in any telemetry/ledger artifact (proven by probe)"] }
  close_shape: { type: PR-merge, artifact: "security audit PR + threat-model doc", cascade: [R-IF-roadmap-refresh] }
  next_pointer: null
  notes: Pen-style probes against the 4-tier sandbox + secret backends; dependency audit composes with I-6.

R-CL-Q3:
  title: Phase Q3 — QA + 100%-evidence closure
  surface: III
  status: RESOLVED    # 2026-06-29 — PR #837 landed the Q3 evidence matrix/checker with 123/123 contract proofs and 31/31 CXA seams wired.
  depends_on: [R-CL-P1, R-CL-P2, R-CL-P3, R-CL-P4, R-CL-P5, R-CL-P6]
  blocks: [R-CL-Q4]
  posture: phase-7
  scope: { files: [harness-*/tests, harness-*/src], contracts: [all C-*], cross_axis: yes }
  skills: { primary: null, secondary: [] }
  advisor_required: no
  council_required: no
  verification: { shape: e2e, must_pass: ["full suite green at a verified fixed point (/self-heal, env-artifact reds distinguished); every C-* contract has ≥1 executed-path proof (coverage/evidence matrix); tri-tier use-the-product probes pass; flaky tests eliminated"] }
  close_shape: { type: PR-merge, artifact: "QA/evidence PR + coverage matrix", cascade: [R-IF-roadmap-refresh] }
  next_pointer: null
  notes: 100% = executed-path proof for buildable surfaces; deployment-gated get reference/deterministic now + operator-gated live-proof later (D-2). Workflow candidate for the broad coverage audit.

R-CL-Q4:
  title: Phase Q4 — portable packaging + deployment
  surface: V
  status: RESOLVED    # 2026-06-29 — PR #839 added the packaging gate + deploy image artifacts and merged at ce344811.
  depends_on: [R-CL-Q1, R-CL-Q2, R-CL-Q3]
  blocks: [R-CL-D1]
  posture: phase-7
  scope: { files: [pyproject.toml, deploy/, Dockerfiles, justfile], contracts: [C-RT-29], cross_axis: no }
  skills: { primary: null, secondary: [] }
  advisor_required: yes
  council_required: no
  verification: { shape: e2e, must_pass: ["uv build wheels + pinned reproducible install; per-tier images (self-hosted daemon + managed-cloud + sandbox runners); one-command bring-up per tier reaches readiness-green from a fresh environment"] }
  close_shape: { type: PR-merge, artifact: "packaging PR + deploy artifacts", cascade: [R-IF-roadmap-refresh] }
  next_pointer: null
  notes: Extend the RC just r4xx-*-readiness recipes into a packaged installer; reproducibility proof from a clean environment.

R-CL-D1:
  title: Phase D1 — documentation suite
  surface: XI
  status: RESOLVED    # 2026-06-30 — PR #841 added the D1 runtime docs suite, docs-completeness gate, and evidence matrix; merged at e3dba297.
  depends_on: [R-CL-Q4]
  blocks: [R-CL-C1]
  posture: mode-agnostic
  scope: { files: [docs/, README, .harness/], contracts: [all C-*], cross_axis: yes }
  skills: { primary: null, secondary: [] }   # /document-generate + /document-release
  advisor_required: no
  council_required: no
  verification: { shape: e2e, must_pass: ["feature/functionality + dependency + user/operator + deployment + architecture/API docs authored; every claim cite-grounded vs HEAD (no fabricated cites); docs-completeness check (every public surface + every audience); operator readthrough"] }
  close_shape: { type: PR-merge, artifact: "docs suite PR", cascade: [R-IF-roadmap-refresh] }
  next_pointer: R-CL-C1
  notes: Includes the substitution/retirement story, the 4-axis+CXA concept map, contributor guide, troubleshooting.

R-CL-C1:
  title: Phase C1 — full-spec closure certification + ship
  surface: VIII
  status: RESOLVED    # 2026-06-30 — PR #843 added the closure certification, provider-free C1 gate, and shipped the close-track release at 62d19553.
  depends_on: [R-CL-D1]
  blocks: []
  posture: mode-agnostic
  scope: { files: [.harness/closure-certification.md, Project_Roadmap_v1.md, .harness/roadmap_status.md], contracts: [all C-*], cross_axis: yes }
  skills: { primary: harness-adversarial-reviewer, secondary: [council-orchestrator] }
  advisor_required: yes
  council_required: no
  verification: { shape: e2e, must_pass: ["coverage matrix 100% (every C-* + CXA seam + ADR: built∧activated∧tested∧reviewed∧documented); final adversarial+council completeness critic; phase-9 promotion model applied to remaining bounded-residuals; shipped release"] }
  close_shape: { type: PR-merge, artifact: "closure-certification PR + shipped release", cascade: [R-IF-roadmap-refresh] }
  next_pointer: null
  notes: >
    RESOLVED 2026-06-30 at PR #843 — `.harness/closure-certification.md` records the
    5-dimension coverage matrix, final completeness critic, Phase-9 bounded-residual review,
    tenant-policy external-review limitation, and ship evidence. Provider-free C1 gate
    `just closure-certification-check` is wired into `just check` / `just codex-check`.
    No non-recurring close-track arc remains.
```

---

### 5.16 Prompts management — full surface (R-PM-NN) — net-new forward capability

> Authored 2026-06-11 per operator directive "I do ultimately want full prompts management" + the AskUserQuestion that ratified **FULL-STACK-UPFRONT** scope, sequenced **after R-CL-Q1**. This is a net-new forward capability beyond the 13-phase closure plan (§5.15), born from R-CL-P4's DP-4 deferral. The MINIMAL binding (#496) — active-prompt *version identity* in the procedural-tier hash — is the foundation; this arc builds the surface that makes prompts actually *function*. First deliverable is a design-phase spec/ADR (X-AL-3), then phase-7 impl after clearance.

```yaml
R-PM-1:
  title: Full prompts-management surface — injection + selection + versioning/authoring + per-tier governance
  surface: I-prompts
  status: RESOLVED     # ✅ all 5 cascade PRs landed (#506 injection / #508 store / #509 selection / #510 governance / #511 CXA seam), 2026-06-12. The distributed per-axis cascade (runtime v1.44 / IS v1.7 / CP v1.31 / OD v1.29 / CXA v2.20 §2.3.8) delivered all 4 layers (injection + selection + versioning/authoring + per-tier governance); no new ADR (ADR-F1-faithful). Was BLOCKED (capability arc #2 of the R-CC-1 program §5.17, FULL-STACK-UPFRONT per 2026-06-11 AUQ).
  depends_on: [R-CC-1]   # was [R-CL-Q1] — inverted by the capability-first directive; R-PM-1 is a capability arc IN the R-CC-1 program (sequenced #2), no longer after Q1.
  blocks: []
  posture: design-phase   # spec/ADR authoring first; then bundled-absorption into phase-7 (clearance markers)
  scope: { files: [design-substrate/ (new prompts-management spec/ADR), harness-is/src (prompt versioning/authoring + PROMPTS path-class), harness-cp/src (selection — routing-style per-role binding), harness-runtime/src (dispatch injection seam), harness-od/src (per-tier governance)], contracts: [C-IS-05 §5.2 (existing version-identity binding), C-IS-01 (PROMPTS path-class), ADR-F1 (ProviderAgnosticPayload — injection-mechanism touch), C-CP-02 (routing per-role precedent for selection), C-RT-15 (LLM dispatch composer)], cross_axis: yes }
  skills: { primary: systems-architect, secondary: [spec-writer, implementation-planner, council-orchestrator, harness-adversarial-reviewer] }
  advisor_required: yes
  council_required: conditional:nameable-tension   # (i) selection-ownership IS⊥CP; (ii) injection-mechanism blast-radius (bounded HarnessContext channel vs foundational ADR-F1 ProviderAgnosticPayload change — C10 action-safety/contract-stability)
  verification: { shape: e2e, must_pass: ["a comprehensive prompts-management spec/ADR covers all 4 layers (injection + selection + versioning/authoring + per-tier governance), cleared (clearance marker)", "the active prompt's CONTENT reaches the provider as a system prompt on a real dispatch (injection proven e2e — not just version-identity in the ledger hash)", "selection resolves which prompt is active per role/step/workload", "per-tier (persona) prompt-governance posture distinct across SOLO/TEAM_BINDING/MULTI_TENANT"] }
  close_shape: { type: design-then-impl, artifact: "prompts-management spec/ADR + clearance markers, then phase-7 impl PR(s)", cascade: [R-IF-roadmap-refresh] }
  next_pointer: null
  notes: |
    OPERATOR-CONFIRMED 2026-06-11 (AskUserQuestion): FULL prompts management, scope = FULL-STACK-UPFRONT (all
    four layers designed in one comprehensive spec/ADR before any impl), sequenced AFTER R-CL-Q1. (The operator
    OVERRODE the injection-first-MVP recommendation in favor of full-stack — record faithfully: all 4 layers are
    in-scope for the upfront design.) Re-opens R-CL-P4's DP-4 deferral
    (fork class_1_fork_prompts_management_surface_active_prompt_version.md) at FULL scope; the #496 MINIMAL
    binding (IS spec v1.5 §C-IS-05 §5.2) — active-prompt VERSION IDENTITY in the procedural-tier hash — is the
    correct foundation, NOT a redo.
    THE FOUR LAYERS (all in-scope, design upfront): (a) INJECTION — the active prompt's CONTENT reaches the
    provider as a system prompt at LLM dispatch (the missing load-bearing piece; today nothing reaches the model);
    (b) SELECTION — which prompt is active for which role/step/workload (mirrors CP routing's per-role bindings,
    C-CP-02); (c) VERSIONING/AUTHORING — multiple prompt versions on the PROMPTS path-class (C-IS-01) + authoring
    discipline; (d) PER-TIER GOVERNANCE — persona-tier-aware prompt policy (redaction/approval) composing with the
    bridging-arc SOLO→TEAM_BINDING→MULTI_TENANT tiers.
    GROUNDING PRESERVED (the expensive 2026-06-11 finding — do NOT re-excavate after Q1): there is NO system-prompt
    route at the dispatch layer today. All 3 provider-translate functions (_payload_to_anthropic/openai/ollama_kwargs,
    harness-runtime/.../llm_dispatch.py:917-946) build kwargs from exactly messages+tools+params; ProviderAgnosticPayload
    (harness-cp/.../cp_shared_types.py:89, frozen, extra=forbid, ADR-F1) has NO `system` field and is only ever
    constructed in production as an empty placeholder (llm_dispatch.py:479 — the real payload is supplied by the
    caller / workflow step). So injection is NET-NEW H_T design (X-AL-3) → first deliverable is a design-phase
    spec/ADR, then impl after clearance.
    TWO CANDIDATE INJECTION MECHANISMS (the live arc-fork to resolve at arc-open): (1) translate-time channel on
    HarnessContext (carry active-prompt content like prompt_manifest already is; inject at translate time — prepend
    a role=system message for OpenAI/Ollama, add a system= kwarg for Anthropic) = BOUNDED, no ADR change; vs (2) add
    `system` to the frozen ProviderAgnosticPayload contract = FOUNDATIONAL ADR-F1 touch → Class 1 back-flow.
    COUNCIL (conditional:nameable-tension, surface both at arc-open): (i) SELECTION-OWNERSHIP IS⊥CP — prompt
    authoring/versioning is IS-native, but per-role/step binding mirrors CP routing; who owns the selection surface?
    (the routing per-role-binding precedent may pre-resolve this). (ii) INJECTION-MECHANISM BLAST-RADIUS — bounded
    HarnessContext channel vs foundational ADR-F1 ProviderAgnosticPayload change (C10 action-safety / contract-stability).
    Cross-ref: forward register .harness/post-phase-8-forward-register.md (2026-06-01 snapshot; R-PM-1 is a net-new
    capability beyond it — not back-filed into that historical doc).
```

---

### 5.17 Capability-completion program (R-CC-NN) — land all open units before the quality sweep

> Authored 2026-06-11 per operator strategic directive: *"work through all blocked and deferred units even if this requires planning sweeps to make decisions for their producer, disciplines, vendors, corpus/embedding models or run e2e tests … now to land all units fully. Then run the devex, code review and simplification pass on the fully developed harness."* The execution spine is `.harness/capability-completion-inventory-v1.md` (the grounded per-unit inventory, verified at HEAD `9c38b91`). This re-sequences the closure track: **R-CL-Q1 (DevEx/review/simplification) moves to LAST**, run once on the complete harness; **R-PM-1 moves before Q1** (it is a capability). Grounding finding: the open set is **small** — nearly every forward surface (sandbox tiers, deployment, multi-tenant, external integrations, memory backends) is already live-proven; the genuine open set is ~11 units enumerated in the inventory.

```yaml
R-CC-1:
  title: Capability-completion program — land all open capability units (inventory spine) before R-CL-Q1
  surface: I-capability
  status: RESOLVED     # CAPABILITY FRONTIER COMPLETE 2026-06-12 (arc #8 dispositioned the last item #5 — P5 CXA edges U-CP-12/U-CP-52: 1 close + 1 confirm-defer, no fork, no build owed; `.harness/r-cc-1-arc-8-p5-cxa-edges-disposition.md`). All inventory units landed-or-dispositioned: #1/#2/#4/#5/#6/#8/#9 landed; #3/#7 deferred-by-design; #10/#11 ratified-bounded. R-CL-Q1 unblocks. [was: ACTIVE/live-frontier operator-directed 2026-06-11.]
  depends_on: [R-CL-P0]
  blocks: [R-CL-Q1, R-PM-1]
  posture: design-phase   # design-forks first (X-AL-3), then phase-7 impl as bundled-absorption arcs per fork
  scope: { files: [.harness/capability-completion-inventory-v1.md (spine), design-substrate/** (forks/specs), harness-*/src/**], contracts: [C-CP-02/03/04, C-IS-01/05, ADR-F1, C-RT-15, C-AS-15], cross_axis: yes }
  skills: { primary: systems-architect, secondary: [spec-writer, implementation-planner, phase-7-implementation, harness-adversarial-reviewer, council-orchestrator] }
  advisor_required: yes
  council_required: conditional:nameable-tension   # several arcs carry forks (tier→driver C10⊥C11; prompts selection IS⊥CP + injection blast-radius; api.run C9⊥C11)
  verification: { shape: e2e, must_pass: ["every inventory unit is landed (built+tested) OR dispositioned as a documented bounded-residual with a re-open trigger", "the 2 operator-gate residuals recorded (Gate A=hand-roll engine-recovery → BUILT; Gate B=embedding → DEFERRED-documented)", "only THEN does R-CL-Q1 open on the complete harness"] }
  close_shape: { type: program, artifact: "per-arc PRs (design forks + impl) tracked in the inventory", cascade: [R-IF-roadmap-refresh] }
  next_pointer: R-CL-Q1   # PROGRAM COMPLETE through arc #8. arc #1 tier→driver #503 · #2 R-PM-1 prompts #506-511 · #3 durable-resume #513/#514 · #4 inference-conditional bootstrap #515 · #5 live multi-tier e2e #516 · #6 LLM_AS_ROUTER confirm-defer #517 · #7 redaction e2e #519 · #8 P5 CXA edges DISPOSITIONED (this arc). Frontier complete → R-CL-Q1 opens.
  notes: |
    OPERATOR STRATEGIC DIRECTIVE 2026-06-11 — capability-complete-BEFORE-quality. Rationale: running the
    DevEx/review/simplification sweep (R-CL-Q1) on incomplete code means re-running it once capabilities land =
    double token cost the operator declined. So: land all open capability units first, THEN run Q1 once on the
    fully-developed harness.
    SPINE: `.harness/capability-completion-inventory-v1.md` (grounded per-unit inventory, HEAD `9c38b91`). The
    ~11 open units + their categories ([C-now] / [design] / [wall] / [vendor] / [hollow]) + the recommended
    sequence live there; this entry is the roadmap umbrella.
    TWO OPERATOR GATES ANSWERED (2026-06-11 AskUserQuestion):
    - Gate A (engine-recovery vs I-6) → **HAND-ROLL** (operator overrode the accept-residual recommendation).
      Build a real in-house event-sourced/journal recovery substrate — preserving I-6 (NO vendored engine) —
      reframed as durable-resume/crash-recovery (resume a workflow from the #475 journal after a process restart)
      with a real `api.run` resume-from-journal caller (avoids the fake-producer trap). Design-first (X-AL-3).
    - Gate B (EMBEDDING corpus) → **DEFER** (documented bounded-residual; re-open trigger = real routing traffic +
      operator-supplied embedding model; the layer correctly falls through today — no behavior missing).
    SEQUENCE (inventory §4): arc #1 sandbox tier→driver selection contract ✅DONE #503 → #2 R-PM-1 full prompts
    ✅DONE (#506-#511) → #3 **workflow-layer** durable-resume (RE-AIMED from engine-layer per the Class-2 scoping
    fork class_2_fork_engine_durable_resume_no_production_producer.md — Gate A's hand-roll intent preserved, line 181
    unviolated since the engine-layer loop has no production producer; cascade step 1 = api.resume + C-RT-35 (runtime
    v1.45) ✅DONE #513, step 2 = harness-owned JournalWorkflowPauseStore + api.resume resume_handle (runtime v1.46)
    ✅DONE #514 — anchor-validation U-CP-22 deferred; arc #3 cascade COMPLETE) → #4 api.run provider-ping fork → P3 live
    multi-tier e2e (free Ollama) → #5 LLM_AS_ROUTER async-widening fork → #6 P5 CXA edges → #7 Claude-closeable
    cleanups (P3 redaction proof, cost rollup, HITL OQ-6, CXA doc count) → THEN R-CL-Q1.
    RE-SEQUENCING APPLIED: R-CL-Q1 ACTIVE→BLOCKED (depends_on +R-CC-1,+R-PM-1); R-PM-1 depends_on [R-CL-Q1]→[R-CC-1]
    (capability, now BEFORE Q1). R-CL-P1/P2/P3 grounding docs carry the per-unit detail; their dispositions are
    superseded by the inventory (P1 embedding=defer/llm-router=design-fork; P2 engine-recovery=hand-roll BUILD +
    tier→driver=design-build + OQ-6=build/OQ-5/7=hollow-residual; P3 residuals=build).
    HONEST RESIDUALS (post-Gate): only EMBEDDING (Gate B defer) + P2 OQ-5/7 (genuinely hollow — no composition
    scenario) remain bounded-residuals; everything else is buildable. So Q1 runs on a capability-complete harness
    modulo one deferred optimization (nothing to optimize yet) — accounted for at the C1 completeness-critic.
    NEXT: arc #1 — sandbox tier→driver selection contract (design-phase, X-AL-3). Workflow is an option for the
    broad design-fork cluster (operator opt-in), not gated on it.
```

---

## 6. Operator gate inventory

Actions where genuine human decision is required (not Claude judgment). Flagged via `posture: halt-route-to-operator` in §5; enumerated here for fast scan.

| R-NNN | Gate description | Why operator-decision |
|---|---|---|
| R-001 | H_T-OD-5 RETIRE-READY → RETIRED | Operator deployment substrate not autonomous-overnight territory; Reading α (BOUNDED-RESIDUAL) requires operator AUQ |
| R-004 | H_T-AS-8d RETIRE-READY → RETIRED | Same shape as R-001 |
| R-700-phase-8-substitution-accounting | Phase 7 closure | Comprehensive scope review; per-row disposition choices |
| R-600-workflow-v1-14-amendment | Workflow doc revision | Process-doc evolution requires operator scope authorization |

**Operator-AUQ shape for halt-route actions.** Claude prepares the brief (current state, options, recommendations) and presents via AskUserQuestion. Claude does not execute the halt-route action until operator response. If session ends without response, R stays at status BLOCKED with note `awaiting-operator-AUQ-since-YYYY-MM-DD`.

---

## 7. Audit cadence + drift-detection protocol

**Two mandatory audit points per session lifecycle.**

### 7.1 Session-start audit (always run before first substantive action)

1. Read `.harness/roadmap_status.md`.
2. Compute current `workspace_state_hash`:
   - `git rev-parse HEAD` (8 chars)
   - `gh pr list --state open --json number,headRefName --jq '. | sort_by(.number) | map("\(.number):\(.headRefName)") | join(",")'` (sorted)
   - `ls .harness/class_1_fork_*.md .harness/class_2_fork_*.md 2>/dev/null | sort | wc -l` (open fork doc count)
   - `ls .harness/phase-7d-retirement-events-batch-*.md 2>/dev/null | tail -1` (latest retirement batch)
   - SHA256 of the concatenation; first 12 chars.
3. Compare with `dashboard.workspace_state_hash`.
4. **If mismatch** → HALT, write a diff to session output, surface to operator with options:
   - (a) refresh dashboard from current state, proceed
   - (b) revert workspace to dashboard state (only if drift is uncommitted)
   - (c) operator manually resolves
5. **If match** → proceed to next-action derivation rule (§4).

### 7.2 Post-PR-merge audit (always run after every PR merge)

1. Recompute `workspace_state_hash` per §7.1.
2. Update `.harness/roadmap_status.md`:
   - `workspace_state_hash` → new value
   - `last_refreshed` → now (ISO 8601)
   - `recently_completed` → prepend (R-NNN, PR-link)
   - `in_flight` → remove merged PR, add new opened PRs
   - `next_action` → recompute via §4 rule
3. Commit the dashboard refresh with a title beginning `ops: roadmap status refresh ` (e.g. `…post-PR-NN` or `…post-#NN`; the §12.2.1 carve-out + session-start hook key on the prefix, suffix format-free).
4. Push.

### 7.3 Drift sources (catalogued so future-Claude recognizes them)

| Drift source | How it appears | Resolution |
|---|---|---|
| PR merged but dashboard not refreshed | `dashboard.recently_completed` missing the merged PR | Refresh dashboard, commit |
| New PR opened but dashboard not refreshed | `dashboard.in_flight` missing the open PR | Refresh dashboard, commit |
| Fork doc filed but dashboard not refreshed | `dashboard.open_fork_docs` count mismatch | Refresh dashboard, commit |
| Retirement batch filed but dashboard not refreshed | `dashboard.latest_retirement_batch` outdated | Refresh dashboard, commit |
| R-NNN's depends_on RESOLVED but status still BLOCKED | Stale per §4 rule step 3 | Flip status to ACTIVE, re-derive |
| R-NNN landed but not marked RESOLVED in this roadmap | The §5 entry is stale | Mark RESOLVED, refresh next_pointer |
| Operator added a new requirement not in roadmap | New R-NNN authored mid-session | Add entry at §5, refresh dashboard |
| Workspace edit by non-Claude actor (operator hand-edit) | `workspace_state_hash` mismatch | Operator confirms drift is intentional; refresh from current state |

---

## 8. Refresh + update protocol

### 8.1 When to add a new R-NNN

- Operator surfaces a new requirement → add R-NNN immediately (mode-agnostic posture; this doc is process-substrate).
- Closure of one R-NNN reveals a sub-action — add child R-NNN with `depends_on: [parent]`.
- Pattern catalogue cardinality ≥2 reaches workflow-doc promotion threshold → add an R-600 series entry.
- Surface I-X decomposition pass executes → batch-add R-NNN entries for that surface's atomic actions.

### 8.2 When to refresh an existing R-NNN

- `status` change at PR merge or upstream dependency closure.
- `depends_on` / `blocks` change at workspace state evolution.
- `verification.must_pass` change at spec/contract amendment (cascade per close_shape).
- `notes` clarification at session learning.

### 8.3 When to delete an R-NNN

Don't. Mark `CANCELLED` with rationale at `notes` instead. Provenance preserved.

### 8.4 PR labels

Add these labels (operator-discretion) for fast scan:

- `roadmap-r-nnn` — PR closes one or more R-NNN; PR body cites them.
- `roadmap-drift-detected` — PR introduces drift; dashboard refresh owed in same PR.
- `roadmap-design-extension` — adds new R-NNN entries; not just refreshing existing ones.

---

## 9. Workstream catalog

Decomposition status per surface. **`decomposed`** means R-NNN entries exist at §5. **`decomposition-owed`** means surface is named but atomic R-NNN entries pending.

| § | Surface | Decomposition status | Decomposition trigger |
|---|---|---|---|
| I | Phase 7 axis-clean | `partially-decomposed` (R-001..R-004 + R-001-h-t-is-2-retired + R-003) | R-002 execution generates per-row R-NNN |
| II | MVP-operator-usable | `partially-decomposed` (R-100 series) | Each merged PR generates next R-NNN at this surface |
| III | CI substrate | `partially-decomposed` (R-200 series) | After R-200-ci-pytest closure, decompose §V multi-deployment dependencies |
| IV | Multi-LLM maturity | `decomposed` (2026-06-01) | §5.10 R-300-series authored from post-Phase-8 register §B-1/§B-2 |
| V | Multi-deployment surfaces | `partially-decomposed` (R-400 series, 2026-06-01) | Triggered by R-100-mvp-multi-workflow-fixture-suite closure (PR #190); decomposed at §5.5 — R-400 RESOLVED (PR #194, the one LOCAL-testable row), R-410..R-440 PROPOSED (live/infra-gated) |
| VI | Multi-tenant | `decomposed` (2026-06-01) | §5.11 R-500-multi-tenant-deployment authored from register §B-8; live-gated on R-420. OD-4 at R-008 |
| VII | Process discipline | `partially-decomposed` (R-600 series + R-IF-roadmap-refresh) | Cadence-driven; sweep every ~10 PRs |
| VIII | Phase 8 retirement criteria | `placeholder` (R-700-phase-8-substitution-accounting only) | Triggered when §I substitutions ≥45/49 closed |
| IX | External integrations | `decomposed` (2026-06-01) | §5.12 R-800..R-830 authored from register §B-10..§B-13 (Files/managed_agents DEFERRED-indefinite) |
| X | Existential / research | `decomposed` (2026-06-08) | §5.13 R-900 placeholder decomposed into R-901 Phase-9 retirement criteria research brief |
| XI | Operator tooling / observability | `complete` (R-XI-01 + R-XI-02 + R-XI-03 all RESOLVED; 2026-06-02) | Live operator dashboard: Almanac Noir, dependency-graph + sparklines, client-side live-update. Public Pages + launchd :8137 (auto-syncing). No open XI levers. |

**Decomposition-owed marker discipline.** When opening any surface for decomposition, operator AUQ required ONLY if scope is ambiguous; otherwise Claude decomposes per current workspace state. The roadmap is not a contract — it is a discipline.

---

## 10. Filing footer

| Field | Value |
|---|---|
| Artifact | `Project_Roadmap_v1.md` (workspace root) |
| Authored at | 2026-05-31 |
| Authoring authority | Operator directive 2026-05-31 + advisor 54th application (5 corrections accepted) |
| Predecessor | None (v1 = origin) |
| Successor consumption | Every session via CLAUDE.md §12 |
| Refresh cadence | Session-start audit + post-PR-merge audit; per §7 |
| Revision policy | This doc is process-substrate. Edits land via PRs labelled `roadmap-design-extension` (new R-NNN) or `roadmap-r-nnn` (closure). |

---

*End of `Project_Roadmap_v1.md`. Dashboard at `.harness/roadmap_status.md`. Audit protocol enforced at `CLAUDE.md` §12.*
