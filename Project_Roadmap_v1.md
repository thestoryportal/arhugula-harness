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

**Populated entries: 27.** Decomposition-owed markers per §9 for §IV–§VI + §VIII–§X.

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
  title: Implement spec §3.7 `harness.toml` auto-discovery at workspace root (or amend the spec)
  surface: II
  status: BLOCKED
  depends_on: []
  blocks: []
  posture: phase-7
  scope: { files: [harness-runtime/src/harness_runtime/cli/**, harness-runtime/src/harness_runtime/config_source.py, design-substrate/Spec_Harness_Runtime_v1.md], contracts: [C-RT-30 §3.7, C-RT-29 §14.18.1], cross_axis: no }
  skills: { primary: phase-7-back-flow-routing, secondary: [phase-7-implementation] }
  advisor_required: yes
  council_required: no
  verification: { shape: integration, must_pass: ["with harness.toml at CWD and no --config, `harness run <manifest>` discovers it", "no-file case preserves env+CLI-only behavior", "dead DEFAULT_CONFIG_FILE_NAME constant wired or retired"] }
  close_shape: { type: PR-merge, artifact: "fix: harness.toml default discovery per spec §3.7 (or spec amendment)" }
  next_pointer: R-100-mvp-real-workflow-execution
  notes: >
    BLOCKED on operator ratification of `.harness/class_1_fork_harness_toml_default_discovery_unimplemented.md`
    (PROPOSING). Spec §3.7 (line 391) + §14.18.1 declare `harness.toml` is discovered at
    workspace root "by default"; the impl never wired it — `DEFAULT_CONFIG_FILE_NAME`
    (config_source.py:43) is a dead constant and a positive-control probe (file present at
    CWD, no --config) still fails "missing required fields". "Workspace root" is undefined
    for discovery (CWD vs the config's own repository_root — circular), so the fix shape is a
    Class 1 fork: Reading (A) CWD discovery / (B) upward search / (C) spec amendment dropping
    the clause. Worked around in R-100 via the `just run` recipe passing `--config` (option B
    at the recipe layer); this entry is the spec-conforming closure. Does not block the MVP.

R-100-mvp-real-workflow-execution:
  title: Real multi-step workflow at SOLO_DEVELOPER tier against Anthropic provider
  surface: II
  status: ACTIVE   # 3 of 4 ACs PASS (AC #1 + #3 + #4) via test_r100_real_workflow_e2e.py. AC #4 cost fork RESOLVED-AS-INVALID 2026-06-01 (test-bug). AC #2 (tool dispatch via api.run) NOT CLOSED and NOT one gap away: converter CONFIG SURFACE applied at spec v1.40 (R-100-tool-step-converter RESOLVED), but a pre-merge completeness critic (PR #171) found ≥2 more bootstrap gaps (B: stage-3a never calls host.start() → converter unreachable; C: no sandbox_decision_resolver; D? provider construction). AC #2 closes only via a full-path echo-via-api.run e2e at R-100-tool-step-sandbox-resolver (the AC#2-closing arc).
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
  status: PROPOSING   # Gap C (resolver) is a design decision needing operator AskUserQuestion + a spec amendment; B/E/F are impl, D is config. Class 1 fork filed 2026-06-01; gap set execution-confirmed (5 gaps) 2026-06-01.
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
