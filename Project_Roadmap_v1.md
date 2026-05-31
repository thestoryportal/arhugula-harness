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
| IX | External integrations | R-800..R-899 | Real external MCP servers; managed_agents primitive (deferred per AS-8f); Files API (deferred per AS-8e) |
| X | Existential / research | R-900..R-999 | Open architectural questions; speculative arcs; research-corpus extensions |
| XI | Operator tooling / observability | R-XI-NN | Human-facing dashboards, status pages, CI-deployed observability surfaces; NOT for Claude consumption (Claude reads `.harness/roadmap_status.md` directly) |

**Decomposition status:** §I + §II + §III + §VII + §XI have R-NNN actions populated at §5. §IV–§VI + §VIII–§X are named with decomposition-owed markers per §9.

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

---

## 5. R-NNN action catalog

**Populated entries: 26.** Decomposition-owed markers per §9 for §IV–§VI + §VIII–§X.

### 5.1 Mode-agnostic infrastructure (R-IF-NNN)

```yaml
R-IF-108:
  title: PR #108 — workflow v1.12 §7.4.7.3.C audit at per-axis CLAUDE.md §4.1
  surface: VII
  status: ACTIVE
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
  notes: In-flight; track for merge. Do not touch.

R-IF-109:
  title: PR #109 — memory entries round-3 audit
  surface: VII
  status: ACTIVE
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
  notes: In-flight; track for merge.

R-IF-110:
  title: PR #110 — CXA v2.18 absorb OD-IS-EDGE-DRIFT (halt-doc Item 11)
  surface: VII
  status: ACTIVE
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
  notes: In-flight; design-phase posture session must merge.

R-IF-111:
  title: PR #111 — OD plan v2.27 NEW §4.6 OD-INTERNAL carve-out (halt-doc Item 12)
  surface: VII
  status: ACTIVE
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
  notes: In-flight; sibling to PR #110.

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
  status: ACTIVE   # unblocked — depends_on [R-003] RESOLVED at PR #136 + #137 merge 2026-05-31
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
    UNBLOCKED 2026-05-31 — R-003 RESOLVED at PR #136 + #137 merge. The producer-site cascade that gated IS-2 RETIRED is complete: all 7 sites handled (4 lifted, 3 documented None-canonical). Execution = file the PARTIAL → RETIRED retirement event (batch-NN) + refresh harness-is/CLAUDE.md §4.1 + ledger-v2 §3, verifying X-AL-2 second conjunct. Was PARTIAL per batch-49 / runtime plan v2.42.

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
  status: DEFERRED
  depends_on: []
  blocks: [R-700-phase-8-substitution-accounting]
  posture: halt-route-to-operator
  scope: { files: [.harness/phase-7d-retirement-events-batch-NN.md], contracts: [], cross_axis: no }
  skills: { primary: phase-7-substitution-retirement, secondary: [] }
  advisor_required: no
  council_required: no
  verification: { shape: none, must_pass: ["operator decision to author Files API surface OR carry as RETIRED-AS-BOUNDED-RESIDUAL at Phase 8"] }
  close_shape: { type: retirement-event, artifact: "Phase 8 substitution accounting (R-700) OR a future Files-arc retirement event", cascade: [] }
  next_pointer: null
  notes: STILL-BOUNDED-INDEFINITELY per runtime spec v1.17 §14.C (Files arc DEFERRED INDEFINITELY, Memory-only MVP scope). Not executable in-CLI; gated on operator Files-API surface-authoring decision. X-AL-2 bounded-residual carry; resolves at R-700 Phase 8 accounting if not authored.

R-006-as-8f-managed-agents-indefinite:
  title: H_T-AS-8f (managed_agents.* namespace) — INDEFINITE deferral accounting
  surface: I
  status: DEFERRED
  depends_on: []
  blocks: [R-700-phase-8-substitution-accounting]
  posture: halt-route-to-operator
  scope: { files: [.harness/phase-7d-retirement-events-batch-NN.md], contracts: [], cross_axis: no }
  skills: { primary: phase-7-substitution-retirement, secondary: [] }
  advisor_required: no
  council_required: no
  verification: { shape: none, must_pass: ["operator decision on Anthropic managed_agents beta SDK integration + managed-cloud deployment OR carry as RETIRED-AS-BOUNDED-RESIDUAL at Phase 8"] }
  close_shape: { type: retirement-event, artifact: "Phase 8 substitution accounting (R-700) OR a future managed_agents retirement event", cascade: [] }
  next_pointer: null
  notes: STILL-BOUNDED-INDEFINITELY per `.harness/class_1_fork_as_8f_managed_agents_namespace_production_only_exclusion.md` Q1=(C) + runtime spec v1.33 + AS spec v1.7 §14.5 footer (mirror AS-8e). Not executable in-CLI; gated on managed_agents beta SDK + managed-cloud surface. X-AL-2 bounded-residual carry.

R-007-od-3-sampler-retired:
  title: H_T-OD-3 (Composite Sampler) RETIRE-READY → RETIRED transit
  surface: I
  status: BLOCKED
  depends_on: [R-100-mvp-real-workflow-execution]
  blocks: [R-700-phase-8-substitution-accounting]
  posture: halt-route-to-operator
  scope: { files: [.harness/phase-7d-retirement-events-batch-NN.md], contracts: [], cross_axis: no }
  skills: { primary: phase-7-substitution-retirement, secondary: [] }
  advisor_required: yes
  council_required: no
  verification: { shape: e2e, must_pass: ["HarnessCompositeSampler + TailKeepSpanProcessor exercised at a production-surface deployment (non-LOCAL_DEVELOPMENT)", "X-AL-2 second conjunct — head-based sampler substitution no longer the active path at production OTel pipeline"] }
  close_shape: { type: retirement-event, artifact: ".harness/phase-7d-retirement-events-batch-NN.md", cascade: [R-IF-roadmap-refresh] }
  next_pointer: R-009-od-6-otlp-retired
  notes: RETIRE-READY at batch-36 (both gates closed — §9.1 tail-keep + §10.3 base_rate envelope). Like OD-5/OD-6, RETIRED transit needs the X-AL-2 second conjunct at a real deployment; or operator-AUQ Reading α RETIRED-AS-BOUNDED-RESIDUAL. Sibling-arc candidate with OD-6 (joint same-arc tier advancement precedent batches 33-34).

R-008-od-4-redaction-partial:
  title: H_T-OD-4 (Pre-Collector redaction SpanProcessor) PARTIAL → RETIRE-READY gate closures
  surface: I
  status: BLOCKED
  depends_on: []
  blocks: [R-700-phase-8-substitution-accounting]
  posture: phase-7
  scope: { files: [harness-od/**, harness-runtime/**], contracts: [C-OD-12, C-OD-13 §13.1 §13.2], cross_axis: no }
  skills: { primary: phase-7-implementation, secondary: [phase-7-substitution-retirement] }
  advisor_required: conditional:if a gate closure touches a cross-axis contract
  council_required: no
  verification: { shape: integration, must_pass: ["§13.1 per-session redaction toggle mechanism authored (deferred at PR #25 apply arc)", "§13.2 opaque-token tokenization mode (strip-not-tokenize MVP scope-lock lifted)"] }
  close_shape: { type: PR-merge, artifact: "PR closing the remaining OD-4 gates → PARTIAL → RETIRE-READY", cascade: [R-IF-roadmap-refresh] }
  next_pointer: R-007-od-3-sampler-retired
  notes: PARTIAL (refined) at batch-35; gate (a) partially closed at PR #25 (deployment-level persona_tier + multi-tenant non-toggleability). Remaining — per-session toggle (needs session-control substrate) + §13.2 tokenization. NOT yet RETIRE-READY; further substrate before a retirement transit.

R-009-od-6-otlp-retired:
  title: H_T-OD-6 (Local-first OTLP ingestion) RETIRE-READY → RETIRED transit
  surface: I
  status: BLOCKED
  depends_on: [R-100-mvp-real-workflow-execution]
  blocks: [R-700-phase-8-substitution-accounting]
  posture: halt-route-to-operator
  scope: { files: [.harness/phase-7d-retirement-events-batch-NN.md], contracts: [], cross_axis: no }
  skills: { primary: phase-7-substitution-retirement, secondary: [] }
  advisor_required: yes
  council_required: no
  verification: { shape: e2e, must_pass: ["4-OD-B SqliteWritePath ingestion exercised against real spans at a deployment", "X-AL-2 second conjunct — local-first OTLP substitution surface no longer invoked at production"] }
  close_shape: { type: retirement-event, artifact: ".harness/phase-7d-retirement-events-batch-NN.md", cascade: [R-IF-roadmap-refresh] }
  next_pointer: R-001-h-t-is-2-retired
  notes: RETIRE-READY at batch-33 ("Terminal in-CLI state"); substrate U-OD-42..U-OD-45 LANDED (PR #18). RETIRED transit needs X-AL-2 second conjunct at a real deployment; or operator-AUQ Reading α RETIRED-AS-BOUNDED-RESIDUAL. Sibling-arc candidate with OD-3.
```

### 5.3 MVP-operator-usable (R-100..R-199)

```yaml
R-100-mvp-operator-usable-cli-shipped:
  title: harness CLI end-to-end smoke — config load + workflow load + provider dispatch
  surface: II
  status: ACTIVE
  depends_on: []
  blocks: [R-001, R-004, R-100-mvp-real-workflow-execution]
  posture: phase-7
  scope: { files: [harness-runtime/src/harness_runtime/cli/**, harness.toml.example, .env.example, justfile], contracts: [C-RT-29, C-RT-30], cross_axis: no }
  skills: { primary: phase-7-implementation, secondary: [verify, run] }
  advisor_required: conditional:if CLI dispatch surface diverges from C-RT-29 §13.4
  council_required: no
  verification: { shape: e2e, must_pass: ["`just harness-run minimal.toml` exits 0", "audit-ledger entry written to .harness/state.jsonl", "non-empty LLM response observed at stdout"] }
  close_shape: { type: PR-merge, artifact: "mvp: harness CLI smoke + minimal.toml workflow", cascade: [R-100-mvp-real-workflow-execution] }
  next_pointer: R-100-mvp-real-workflow-execution
  notes: Builds on PRs #82-#86 + #84 CLI parent-app subcommand pattern. Use-the-product probe pattern (workspace memory) is the discipline here.

R-100-mvp-real-workflow-execution:
  title: Real multi-step workflow at SOLO_DEVELOPER tier against Anthropic provider
  surface: II
  status: BLOCKED
  depends_on: [R-100-mvp-operator-usable-cli-shipped]
  blocks: [R-001, R-004, R-100-mvp-yaml-loader-shipped, R-300-multi-llm-second-provider]
  posture: phase-7
  scope: { files: [harness-runtime/tests/integration/**, examples/**], contracts: [], cross_axis: no }
  skills: { primary: phase-7-implementation, secondary: [verify, run] }
  advisor_required: no
  council_required: no
  verification: { shape: e2e, must_pass: ["3+ step workflow executes", "tool dispatch surface exercised ≥1 site", "audit-ledger emits step-by-step entries", "cost-attribution entries present per OD plan v2.25 binding"] }
  close_shape: { type: PR-merge, artifact: "mvp: 3-step workflow e2e against Anthropic", cascade: [] }
  next_pointer: R-001
  notes: Unblocks AS-8d + OD-5 RETIRED transits.

R-100-mvp-yaml-loader-shipped:
  title: YAML manifest loader operational (close Class 1 forks PR #79 / PR #80 lineage)
  surface: II
  status: BLOCKED
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
  status: BLOCKED
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
  notes: Some patterns (parallelization, evaluator-optimizer) may require multiple PRs.
```

### 5.4 CI substrate (R-200..R-299)

```yaml
R-200-ci-pytest-pyright-ruff-matrix:
  title: GitHub Actions workflow — pytest + pyright + ruff matrix at PR open
  surface: III
  status: ACTIVE
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
  notes: Currently only X-AL-3 guard runs at CI. This is the first substantive CI job.

R-200-ci-axis-matrix:
  title: Per-axis test isolation matrix
  surface: III
  status: BLOCKED
  depends_on: [R-200-ci-pytest-pyright-ruff-matrix]
  blocks: []
  posture: mode-agnostic
  scope: { files: [.github/workflows/ci.yml], contracts: [], cross_axis: no }
  skills: { primary: phase-7-implementation, secondary: [] }
  advisor_required: no
  council_required: no
  verification: { shape: integration, must_pass: ["each axis runs in isolation (no harness-cp leak into harness-is run)", "matrix completes in <10min"] }
  close_shape: { type: PR-merge, artifact: "ci: per-axis isolation matrix", cascade: [] }
  next_pointer: null
  notes: Reveals cross-axis import leaks early.

R-200-ci-coverage-gating:
  title: Coverage gating at PR (informational at first; enforce later)
  surface: III
  status: BLOCKED
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
  notes: Don't enforce a threshold at v1; gather data first.

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

### 5.5 Process discipline (R-600..R-699)

```yaml
R-600-workflow-v1-14-amendment:
  title: Workflow v1.13 → v1.14 — roadmap-driven discipline catalogue
  surface: VII
  status: PROPOSED
  depends_on: [PR-merge-of-this-roadmap]
  blocks: []
  posture: design-phase
  scope: { files: [design-substrate/Project_Workflow_*.md], contracts: [Workflow §7.4, §7.5 NEW], cross_axis: no }
  skills: { primary: spec-writer, secondary: [harness-adversarial-reviewer] }
  advisor_required: yes
  council_required: conditional:nameable-tension
  verification: { shape: grep, must_pass: ["§7.5 NEW roadmap-discipline section authored", "next-action derivation rule canonicalized at workflow doc layer", "clearance marker filed"] }
  close_shape: { type: substrate-amendment, artifact: "Workflow v1.13 → v1.14", cascade: [R-IF-roadmap-refresh] }
  next_pointer: null
  notes: Sibling arc to this roadmap PR per scoping decision. Operator-discretion timing.

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
  verification: { shape: grep, must_pass: ["all `[[pattern-name]]` cardinality ≥2 entries identified", "each promotion candidate evaluated against §7.4.7 catalogues"] }
  close_shape: { type: substrate-amendment, artifact: "Workflow doc revision absorbing N patterns", cascade: [] }
  next_pointer: null
  notes: Cadence: every ~10 PRs or operator-discretion. NOT every session.

R-600-clearance-marker-backfill-survey:
  title: Survey design-substrate amendments lacking clearance markers
  surface: VII
  status: ACTIVE
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
  notes: Non-retroactive per CLAUDE.md §4.5; survey identifies post-2026-05-29 gaps only.

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
      - "Test query against URL-scrape corpus returns content NOT in static research/notebooks/ extracts"
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
    Static extracts at research/notebooks/ remain load-bearing for ~95% of queries;
    interactive corpus for the trigger events above. Memory entry [[notebooklm-harness-corpus-url]]
    refreshed in same PR. RESOLVED in one arc (skipped PROPOSED → ACTIVE) since setup +
    verification + documentation all closed at this PR's merge.
```

### 5.6 Halt-doc routings (2026-05-31 carries)

R-700 prefix used because these are halt-resolutions awaiting downstream substantive arcs.

```yaml
R-700-OD-IS-EDGE-DRIFT:
  title: OD→IS edge cardinality reconciliation (halt-doc Item 11; routes via PR #110)
  surface: VII
  status: BLOCKED
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
  status: BLOCKED
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

### 5.7 Operator tooling / observability (R-XI-NN)

Surface XI = human-facing tooling. Distinct from `.harness/roadmap_status.md` which is Claude-consumed. Gates on §III CI substrate so dashboards auto-regenerate (avoiding the manual-refresh failure mode v1 hit).

```yaml
R-XI-01:
  title: Browser-based operator dashboard MVP — at-a-glance harness development status
  surface: XI
  status: PROPOSED
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
  status: PROPOSED
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
  status: PROPOSED
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
### 5.8 Phase 8 accounting (R-700..R-799)

```yaml
R-700-phase-8-substitution-accounting:
  title: All 49 substitutions accounted for — RETIRED or RETIRED-AS-BOUNDED-RESIDUAL with rationale
  surface: VIII
  status: BLOCKED
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
  notes: Phase 7 closure gate. Requires comprehensive operator review.
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
3. Commit the dashboard refresh as `ops: roadmap status refresh post-PR-NN`.
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
| IV | Multi-LLM maturity | `decomposition-owed` | Triggered by R-100-mvp-real-workflow-execution closure |
| V | Multi-deployment surfaces | `decomposition-owed` | Triggered by R-100-mvp-multi-workflow-fixture-suite closure |
| VI | Multi-tenant | `decomposition-owed` | Triggered by R-400 surface decomposition |
| VII | Process discipline | `partially-decomposed` (R-600 series + R-IF-roadmap-refresh) | Cadence-driven; sweep every ~10 PRs |
| VIII | Phase 8 retirement criteria | `placeholder` (R-700-phase-8-substitution-accounting only) | Triggered when §I substitutions ≥45/49 closed |
| IX | External integrations | `decomposition-owed` | Triggered by R-300 multi-LLM decomposition |
| X | Existential / research | `decomposition-owed` | Surfaces opportunistically; not actively decomposed |
| XI | Operator tooling / observability | `partially-decomposed` (R-XI-01 + R-XI-02 + R-XI-03, all PROPOSED) | Triggered by R-200-ci-pytest-pyright-ruff-matrix closure; R-XI-01 flips PROPOSED → ACTIVE at that point |

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
