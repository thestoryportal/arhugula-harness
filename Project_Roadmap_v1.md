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
    remainder (R-410..R-440) is PROPOSED + live/infra-gated; §IV multi-LLM still decomposition-owed (its trigger
    R-100-mvp-real-workflow-execution is the operator-gated live e2e, not yet closed) — §4 re-derives to §VII cadence.

R-410-sandbox-tier-2-container-execution:
  title: Real TIER_2_CONTAINER sandbox execution — tool calls run in an isolated container, not in-process FastMCP
  surface: V
  status: PROPOSED   # live/infra-gated — requires a real container runtime; makes the tier model executable (today it is metadata-only)
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
    The honest heart of Surface V. At HEAD the sandbox tier/provider are observability + policy annotations only
    (mcp_client_host.call_tool always uses in-process FastMCP stdio regardless of tier). Building a real container
    provider is the first step toward executable isolation. Almost certainly opens a Class 1 fork: the execution-driver
    contract (how a resolved tier maps to an actual sandbox mechanism) is unspecified beyond spec v1.41 §14.9.8 resolver.

R-411-sandbox-tier-3-microvm-execution:
  title: Real TIER_3 microVM sandbox execution (gVisor / Kata / shared-kernel container)
  surface: V
  status: PROPOSED   # live/infra-gated — requires gVisor/Kata runtime
  depends_on: [R-410-sandbox-tier-2-container-execution]
  blocks: [R-412-sandbox-tier-4-full-vm-execution]
  posture: phase-7
  scope: { files: [harness-runtime/src/**, harness-as/src/**], contracts: [C-AS-15 §15], cross_axis: yes }
  skills: { primary: phase-7-implementation, secondary: [] }
  advisor_required: yes
  council_required: conditional:nameable-tension
  verification: { shape: e2e, must_pass: ["TIER_3-resolved TOOL_STEP executes under a microVM/gVisor boundary", "EXTERNAL_REVERSIBLE blast-radius enforced"] }
  close_shape: { type: PR-merge, artifact: "feat(sandbox): TIER_3 microVM execution provider", cascade: [R-412-sandbox-tier-4-full-vm-execution] }
  next_pointer: R-412-sandbox-tier-4-full-vm-execution
  notes: >
    Extends R-410 up the tier ladder. Inherits the same execution-driver contract question; once R-410 settles the
    pattern, R-411 + R-412 are provider-class additions (CONTAINER -> gVisor/Kata at TIER_3 per deployment_matrix.py).

R-412-sandbox-tier-4-full-vm-execution:
  title: Real TIER_4 full-VM / firecracker sandbox execution (MANAGED_CLOUD-only provider class)
  surface: V
  status: PROPOSED   # live/infra-gated — firecracker/full-VM; MANAGED_CLOUD per deployment_matrix.py
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
    row therefore co-gates on R-421 (a real MANAGED_CLOUD surface). Deferred-far per ADR-D2 graduated-isolation.

R-420-self-hosted-server-deployment-e2e:
  title: Exercise the harness at the SELF_HOSTED_SERVER deployment surface (real server + OTLP collector + tier secrets)
  surface: V
  status: PROPOSED   # operator/infra-gated — requires a real long-running server, a real OTLP collector, a tier-level secrets backend
  depends_on: []
  blocks: [R-421-managed-cloud-deployment-e2e, R-430-otlp-collector-tail-keep-preservation, R-440-tier-level-secrets-backend]
  posture: halt-route-to-operator   # needs operator infra provisioning before any execution
  scope: { files: [harness-runtime/**, deploy/**], contracts: [C-RT-29 §14.18 daemon mode, C-OD-09 §9.1], cross_axis: yes }
  skills: { primary: phase-7-implementation, secondary: [verify] }
  advisor_required: yes
  council_required: conditional:nameable-tension
  verification: { shape: e2e, must_pass: ["harness daemon runs at SELF_HOSTED_SERVER surface against a real OTLP collector", "tail-keep wrapping active (deployment_surface != LOCAL)", "per-cell base_rate matches the SELF_HOSTED cell", "secrets resolve via a tier-level backend (not env fallback)"] }
  close_shape: { type: PR-merge, artifact: "feat(deploy): SELF_HOSTED_SERVER deployment e2e", cascade: [R-421-managed-cloud-deployment-e2e] }
  next_pointer: R-421-managed-cloud-deployment-e2e
  notes: >
    The first real non-LOCAL surface. Unblocks the tail-keep preservation (R-430) + tier secrets (R-440) rows whose
    semantics only exist on a real collector / real secrets backend. Daemon mode (C-RT-29 §14.18, FastMCP Unix-socket
    server) is the entrypoint; the operator provisions the server + collector + secrets backend.

R-421-managed-cloud-deployment-e2e:
  title: Exercise the harness at the MANAGED_CLOUD deployment surface (cloud secrets + FULL_VM provider class + managed collector)
  surface: V
  status: PROPOSED   # operator/infra-gated — requires a real managed-cloud environment
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

R-430-otlp-collector-tail-keep-preservation:
  title: Verify tail-keep-on-classification preservation at a real OTLP collector boundary
  surface: V
  status: PROPOSED   # infra-gated — the TailKeepSpanProcessor buffer logic exists; the drop/keep preservation semantic is collector-side
  depends_on: [R-420-self-hosted-server-deployment-e2e]
  blocks: []
  posture: phase-7
  scope: { files: [harness-od/**, deploy/**], contracts: [C-OD-09 §9.1, §9.2], cross_axis: no }
  skills: { primary: phase-7-implementation, secondary: [verify] }
  advisor_required: no
  council_required: no
  verification: { shape: e2e, must_pass: ["a trace with a classification-trigger span (validator.fail.permanence=permanent / sandbox.violation / breaker.tripped) is preserved end-to-end at a real collector", "a non-triggering trace is sampled per base_rate"] }
  close_shape: { type: PR-merge, artifact: "test(od): tail-keep preservation at real OTLP collector", cascade: [] }
  next_pointer: null
  notes: >
    The TailKeepSpanProcessor (tail_keep_span_processor.py) buffers per-trace + replays at root close; the actual
    keep-vs-drop preservation is downstream at a real collector parsing is_classification_trigger. CI cannot deploy a
    real collector — this row verifies the end-to-end preservation that the LOCAL suite (R-400) structurally cannot.

R-440-tier-level-secrets-backend:
  title: Wire a SELF_HOSTED_SERVER tier-level secrets backend (currently operator-supplied / env-fallback only)
  surface: V
  status: PROPOSED   # infra-gated — real secrets backend (Vault / cloud secrets manager); harness does not implement a provider today
  depends_on: [R-420-self-hosted-server-deployment-e2e]
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
    At HEAD provider_secrets.py documents tier-level (SELF_HOSTED) vs in-sandbox (MANAGED_CLOUD) backends but ships only
    the LOCAL keyring + env-fallback path (per PR #16 binding-fix). This row implements a real tier-level backend per
    ADR-F5 tier-aware secret-fetch. Mirror precedent: keyring env-fallback at [[pr-16-keyring-env-fallback-adr-f5]].
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
  verification: { shape: grep, must_pass: ["all `[[pattern-name]]` cardinality ≥2 entries identified", "each promotion candidate evaluated against §7.4.7 catalogues"] }
  close_shape: { type: substrate-amendment, artifact: "Workflow doc revision absorbing N patterns", cascade: [] }
  next_pointer: null
  resume: .harness/R-600-pattern-bake-in-sweep.md   # ACTIVE-SURVEYED 2026-06-01: both must_pass met (104 cardinality-≥2 tokens identified; promotion set evaluated). Full closure (workflow-doc revision) owed to the DEFERRED R-600-workflow-v1-14-amendment — gated on operator scope authorization. A fresh session reads the survey before that arc; does NOT re-run the sweep until next ~10-PR cadence.
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

### 5.7 Halt-doc routings (2026-05-31 carries)

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
  status: PROPOSED
  depends_on: [R-100-mvp-real-workflow-execution]
  blocks: []
  posture: halt-route-to-operator
  scope: { files: [harness-runtime/tests/integration/**, harness-runtime/config/provider_secrets.py], contracts: [C-CP-04, ADR-F1], cross_axis: no }
  skills: { primary: phase-7-implementation, secondary: [] }
  advisor_required: yes
  council_required: no
  verification: { shape: e2e, must_pass: ["operator provisions openai_key + ollama host", "a fixture forces primary-provider failure and asserts cross-family advance (anthropic -> openai) with routing.*/fallback.* spans + per-candidate cost", "exercised across >=2 deployment surfaces"] }
  close_shape: { type: PR-merge, artifact: "test(routing): mixed-provider fallback exercise", cascade: [] }
  next_pointer: null
  notes: R-100 ran 3 steps single-provider (Anthropic) with empty fallback chain. retry_breaker_fallback.py (C-RT-16) DOES advance cross-family on failure — but no failure + no cross-family candidate at R-100 = unexercised. Register §B-2.
```

### 5.11 Multi-tenant (R-500..R-599) — Surface VI

*Decomposed 2026-06-01 from register §B-8 (discharges §9 Surface VI; the §VI trigger fired 2026-06-01 per §5.5). OD-4 per-session-toggle/tokenization is tracked separately at R-008. Fields plumbed (tenant_id + persona_tier); base-rate envelope + multi-tenant non-toggleability live; UNEXERCISED (SOLO×LOCAL only at MVP).*

```yaml
R-500-multi-tenant-deployment:
  title: Non-default tenant_id / non-SOLO persona_tier deployment exercise
  surface: VI
  status: PROPOSED
  depends_on: [R-420-self-hosted-server-deployment-e2e]
  blocks: []
  posture: halt-route-to-operator
  scope: { files: [harness-runtime/src/harness_runtime/lifecycle/tracer_provider.py, harness-runtime/src/harness_runtime/lifecycle/span_processor.py, harness-od/src/**], contracts: [C-OD-10 §10.3, C-OD-13 §13.1, ADR-D5, ADR-D6], cross_axis: yes }
  skills: { primary: phase-7-implementation, secondary: [] }
  advisor_required: yes
  council_required: conditional:nameable-tension   # C7 (observability/privacy) + C8 (security/compliance) vs C11 (operator-burden): how much redaction/audit ceremony is mandatory at TEAM vs MULTI_TENANT
  verification: { shape: e2e, must_pass: ["deploy with non-None tenant_id + non-SOLO persona_tier at a non-LOCAL surface", "§10.3 base_rate envelope + §13.1 redaction gradient behave per spec under real multi-tenant load", "audit-ledger separated by tenant_id"] }
  close_shape: { type: PR-merge, artifact: "feat(multitenant): non-SOLO persona_tier deployment", cascade: [] }
  next_pointer: null
  notes: tenant_id + persona_tier plumbed (types.py); MultiTenantOverrideRefusedError enforces non-toggleability; PER_PERSONA_TIER_REDACTION present-not-driven. Register §B-8.
```

### 5.12 External integrations (R-800..R-899) — Surface IX

*Decomposed 2026-06-01 from register §B-10..§B-13 (discharges §9 Surface IX). Files API (AS-8e/CP-17) + managed_agents (AS-8f) are STILL-BOUNDED-INDEFINITELY by design — tracked here as DEFERRED for operator-discretion timing at a managed-cloud arc.*

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
  status: DEFERRED
  depends_on: [R-421-managed-cloud-deployment-e2e]
  blocks: []
  posture: halt-route-to-operator
  scope: { files: [design-substrate (Files arc design-phase), harness-runtime/src/**], contracts: [runtime spec v1.17 §14.C, C-AS-13 §13.2, ADR-D3], cross_axis: yes }
  skills: { primary: phase-7-implementation, secondary: [phase-7-back-flow-routing] }
  advisor_required: yes
  council_required: no
  verification: { shape: e2e, must_pass: ["Files arc design-phase opened (runtime plan unit)", "consumer landing at managed-cloud binding", "e2e: upload + reference-by-id + Batch-API discount composition"] }
  close_shape: { type: PR-merge, artifact: "feat(files): Files API consumption contract", cascade: [] }
  next_pointer: null
  notes: STILL-BOUNDED-INDEFINITELY by design (runtime spec v1.17 §14.C Memory-only MVP; AS §13.2 excludes Files at local-development). Closes AS-8e + CP-17 bounded-residuals. Register §B-11.

R-820-managed-agents-integration:
  title: managed_agents integration (managed_agents.* namespace — AS-8f)
  surface: IX
  status: DEFERRED
  depends_on: [R-421-managed-cloud-deployment-e2e]
  blocks: []
  posture: halt-route-to-operator
  scope: { files: [harness-runtime/src/**], contracts: [runtime spec v1.33 §14.D, C-AS-13 §13.2, ADR-D3], cross_axis: yes }
  skills: { primary: phase-7-implementation, secondary: [] }
  advisor_required: yes
  council_required: no
  verification: { shape: e2e, must_pass: ["Anthropic managed_agents SDK integration authored", "production-surface managed_agents.* emission observed at managed-cloud"] }
  close_shape: { type: PR-merge, artifact: "feat(managed-agents): managed_agents integration", cascade: [] }
  next_pointer: null
  notes: STILL-BOUNDED-INDEFINITELY by design; AS schema landed (U-AS-31/32), zero runtime producer; criterion-B unexercisable in-CLI. Closes AS-8f bounded-residual. Register §B-12.

R-830-memory-tool-production-backend:
  title: Memory-tool production backend (cloud-vault / managed-db — CP-16)
  surface: IX
  status: PROPOSED
  depends_on: []
  blocks: []
  posture: phase-7
  scope: { files: [harness-runtime/src/harness_runtime/lifecycle/memory_tool_filesystem.py, harness-runtime/src/harness_runtime/bootstrap/factories/memory_tool_registry_factory.py], contracts: [runtime spec v1.17 §14.12 C-RT-22, ADR-D3], cross_axis: no }
  skills: { primary: phase-7-implementation, secondary: [] }
  advisor_required: no
  council_required: no
  verification: { shape: e2e, must_pass: ["new backend class implements MemoryToolStorageBackendProtocol", "operator binds via RuntimeConfig.memory_tool_backend_config", "e2e read/write/delete across a workflow lifecycle"] }
  close_shape: { type: PR-merge, artifact: "feat(memory): cloud Memory-tool backend", cascade: [] }
  next_pointer: null
  notes: Local-filesystem backend landed (CP-16 RETIRED-AS-BOUNDED-RESIDUAL batch-44); cloud/db deferred. Override point RuntimeConfig.memory_tool_backend_config exists. Register §B-13.
```

### 5.13 Existential / research (R-900..R-999) — Surface X

*Decomposed 2026-06-01 from register §B-16 (discharges §9 Surface X — single placeholder; surfaces opportunistically, not actively decomposed).*

```yaml
R-900-research-arcs:
  title: Open architectural / speculative arcs + research-corpus extensions
  surface: X
  status: PROPOSED
  depends_on: []
  blocks: []
  posture: mode-agnostic
  scope: { files: [research/**, design-substrate (opportunistic)], contracts: [], cross_axis: no }
  skills: { primary: systems-architect, secondary: [] }
  advisor_required: yes
  council_required: conditional:nameable-tension   # case-by-case, only if a named cross-domain tension surfaces
  verification: { shape: grep, must_pass: ["a specific research question is crystallized into a sub-entry before work begins"] }
  close_shape: { type: substrate-amendment, artifact: "research/** or a new R-90N sub-entry", cascade: [] }
  next_pointer: null
  notes: Placeholder. Candidates — workflow-doc v1.14+ Phase-8->Phase-9 retirement-criteria evolution (research/agentic-engineeriing-sdlc.md); NotebookLM 28-URL corpus extensions. Register §B-16.
```

### 5.14 Cross-axis composition seams (R-CXA-NN) — Surface I residual

*Decomposed 2026-06-01 from register §B-14 + closes the no-R-NNN-entry gap R-700 surfaced (draft §C item 2; A-3). Status spine = the R-700 dispositions merged at PR #207. These are mechanical wiring (runtime composer landings + production callers), not cross-domain tensions → council: no.*

```yaml
R-CXA-1-as-is-seam:
  title: CXA-1 (AS->IS) seam completion — secret-fetch audit production caller + remaining 12 edges
  surface: I
  status: PROPOSED
  depends_on: []
  blocks: [R-700-phase-8-substitution-accounting]
  posture: phase-7
  scope: { files: [harness-runtime/src/harness_runtime/lifecycle/as_is_wiring.py, harness-as/src/**], contracts: [CXA v2.18 §2.3.1 (13 edges)], cross_axis: yes }
  skills: { primary: phase-7-cross-axis-composition, secondary: [] }
  advisor_required: no
  council_required: no
  verification: { shape: e2e, must_pass: ["a production caller invokes emit_secret_fetch_audit_entry (AS secret-fetch driver path lands)", "remaining ~12 AS source-unit audit-emission callbacks threaded through AsIsWiring"] }
  close_shape: { type: PR-merge, artifact: "feat(cxa): complete AS->IS seam", cascade: [] }
  next_pointer: null
  notes: PARTIAL per R-700 — composer materialized + 7c-tested; only secret-fetch edge wired; zero production callers. Register §B-14.

R-CXA-2-cp-is-seam:
  title: CXA-2 (CP->IS) seam completion — runtime caller-site invocations + remaining §12.3 edges
  surface: I
  status: PROPOSED
  depends_on: []
  blocks: [R-700-phase-8-substitution-accounting]
  posture: phase-7
  scope: { files: [harness-runtime/src/harness_runtime/lifecycle/cp_is_wiring.py, harness-runtime/src/**], contracts: [CXA v2.18 §2.3.2, class_1_tension_u_rt_35_cp_is_wiring_gaps.md], cross_axis: yes }
  skills: { primary: phase-7-cross-axis-composition, secondary: [] }
  advisor_required: yes
  council_required: no
  verification: { shape: e2e, must_pass: ["6 §16.5 composer methods (U-CP-74..79) invoked at their firing sites + e2e", "remaining ~16 of 17 §12.3 edges materialized"] }
  close_shape: { type: PR-merge, artifact: "feat(cxa): complete CP->IS seam", cascade: [] }
  next_pointer: null
  notes: STILL-BOUNDED per R-700 — cp_is_wiring PARTIAL-LAND (1 of 17); U-RT-35 unit landed (batch-46) but full contract STILL-BOUNDED. Register §B-14.

R-CXA-3-cp-as-seam:
  title: CXA-3 (CP->AS) seam — runtime composer OR Memory-only-scope narrowing
  surface: I
  status: DEFERRED
  depends_on: []
  blocks: [R-700-phase-8-substitution-accounting]
  posture: halt-route-to-operator
  scope: { files: [harness-runtime/src/** (no cp_as_wiring.py at HEAD)], contracts: [CXA v2.18 §2.3.3 (24 edges), ledger §11.1b], cross_axis: yes }
  skills: { primary: phase-7-cross-axis-composition, secondary: [phase-7-back-flow-routing] }
  advisor_required: yes
  council_required: no
  verification: { shape: grep, must_pass: ["EITHER a CP->AS runtime composer at a Files-arc design-phase opening (α) OR operator AskUserQuestion ratifying Memory-only-scope narrowing (β)"] }
  close_shape: { type: PR-merge, artifact: "feat(cxa): CP->AS seam (α) OR scope-narrowing (β)", cascade: [] }
  next_pointer: null
  notes: STILL-BOUNDED per R-700 — no cp_as_wiring.py module (consistent with spec §12); NOT 'N/A' (a real open seam). Neither path in-session-actionable. Register §B-14.

R-CXA-4-od-multi-seam:
  title: CXA-4 (OD->IS/AS/CP) seam completion — remaining ~21 of 26 edges + production callers
  surface: I
  status: PROPOSED
  depends_on: []
  blocks: [R-700-phase-8-substitution-accounting]
  posture: phase-7
  scope: { files: [harness-runtime/src/harness_runtime/lifecycle/od_is_wiring.py, od_as_wiring.py, od_cp_wiring.py], contracts: [CXA v2.18 §2.3.4-§2.3.6 (26 edges)], cross_axis: yes }
  skills: { primary: phase-7-cross-axis-composition, secondary: [] }
  advisor_required: no
  council_required: no
  verification: { shape: e2e, must_pass: ["remaining ~21 of 26 edges materialized at the runtime composition layer (OR operator scope-narrowing of the 26-edge enumeration)"] }
  close_shape: { type: PR-merge, artifact: "feat(cxa): complete OD->multi seam", cascade: [] }
  next_pointer: null
  notes: PARTIAL per R-700 — 3 wiring modules exist + stage into bootstrap; OD audit-write seam exercised (6 callers); only ~5 of 26 edges materialized (batch-42). Register §B-14.
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
| IV | Multi-LLM maturity | `decomposed` (2026-06-01) | §5.10 R-300-series authored from post-Phase-8 register §B-1/§B-2 |
| V | Multi-deployment surfaces | `partially-decomposed` (R-400 series, 2026-06-01) | Triggered by R-100-mvp-multi-workflow-fixture-suite closure (PR #190); decomposed at §5.5 — R-400 RESOLVED (PR #194, the one LOCAL-testable row), R-410..R-440 PROPOSED (live/infra-gated) |
| VI | Multi-tenant | `decomposed` (2026-06-01) | §5.11 R-500-multi-tenant-deployment authored from register §B-8; live-gated on R-420. OD-4 at R-008 |
| VII | Process discipline | `partially-decomposed` (R-600 series + R-IF-roadmap-refresh) | Cadence-driven; sweep every ~10 PRs |
| VIII | Phase 8 retirement criteria | `placeholder` (R-700-phase-8-substitution-accounting only) | Triggered when §I substitutions ≥45/49 closed |
| IX | External integrations | `decomposed` (2026-06-01) | §5.12 R-800..R-830 authored from register §B-10..§B-13 (Files/managed_agents DEFERRED-indefinite) |
| X | Existential / research | `decomposed` (2026-06-01) | §5.13 R-900-research-arcs placeholder from register §B-16; surfaces opportunistically |
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
