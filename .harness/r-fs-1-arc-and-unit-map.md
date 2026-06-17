# R-FS-1 Arc-and-Unit Map

*The single plain-language home for the whole full-spec build. Every arc, what it gives the
harness in non-technical terms, where it sits in the build order, what it depends on, and its
atomic units (real + as-built for finished arcs; anticipated scope for not-yet-started arcs).*

**Authored:** 2026-06-17 · **Posture:** mode-agnostic (process-substrate; this `.harness/` file
only — no `design-substrate/**` or `harness-*/src` edit, X-AL-3 trivially clean). · **Status:**
the dashboard's forward-build sections (arc strip / remaining-work panel / dependency graph) parse
**this file** as their single arc→unit source; `roadmap_status.md` "Remaining forward work" points
here rather than duplicating it.

> **Why this exists.** The dashboard previously showed only opaque counts ("5/11 arcs", "25
> forward items") with no way to see *what* each arc or unit actually is. This file is the
> human-readable map behind those numbers — read it top-to-bottom to understand the entire
> program in plain language; the dashboard renders it section-by-section.

---

## 1. What is being built (plain-language primer)

**The harness** (call it H_T) is the software being built: a **multi-LLM agent harness** — a
reliable outer shell that runs AI agents, calls tools, routes work across different LLM providers
(Anthropic / OpenAI / Ollama), pauses for humans when needed, survives crashes, tracks cost, and
records an audit trail. Think of it as the dependable "operating system" that sits *around* the
LLMs and makes a fleet of agents production-trustworthy.

The work is organized as a four-level hierarchy. The operator asked "what exactly is an arc?" —
this is the answer:

| Level | What it is | Size | Example |
|---|---|---|---|
| **Program** (`R-FS-1`) | The whole commitment: build the *complete* spec, every capability, nothing skipped or deferred. | The entire remaining project. | "Build the full harness beyond the MVP." |
| **Arc** | One **capability / feature area** of the harness. **Generally several atomic units**; a thin arc can be ~1 unit. This is the granularity the build order is frozen at. | A few PRs to many PRs. | "Run agents in parallel team topologies" (B1, 14 units). |
| **Leg** | One **phase** of building an arc: design → spec → plan → build (impl). Roughly one PR each. | ~1 PR. | "B1-impl-6: the PARALLELIZATION strategy." |
| **Atomic unit** (`U-CP-NN`, `U-RT-NN`, `U-IS-NN`, `U-AS-NN`, `U-OD-NN`) | The **smallest indivisible buildable piece**, with its own written pass/fail acceptance test. Lives in a per-axis implementation plan. | Part of a PR. | `U-CP-86` — the parallelization driver strategy. |

So: **an arc is a capability, usually made of multiple atomic units.** A unit is one indivisible
plan item. The prefix says which subsystem owns it — `CP` = control plane (routing, workflow,
topology), `RT` = harness runtime (the run loop, dispatch), `IS` = information substrate (state
ledger, memory), `AS` = action surface (tools, sandbox, MCP), `OD` = operational discipline
(HITL, audit, cost, telemetry).

**Honest asymmetry you should know up front.** Finished arcs list their **real, as-built units**
(taken from the actual commit history — `git log`). Not-yet-started arcs list their **anticipated
scope** (from the grounding sweep) and are marked *"units formally decomposed at arc-open"* — the
atomic units are deliberately *not* fabricated ahead of time, because units are decomposed during
each arc's own plan leg (just-in-time). Inventing them now would be guessing, and the workspace
rule (X-AL-3) forbids treating un-decomposed work as if it were already specified.

---

## 2. Build order + dependency model

**Frozen order** (decided once, not re-litigated): **B1 → B3 → E → B2 → R → B4 → CA → B5 → B6 →
B7 → M.** DONE: **B1 ✅ B3 ✅ E ✅ B2 ✅ R ✅ B4 ✅ CA ✅ B5 ✅ B7 ✅ M ✅** (10 of 11; B7 + M landed out-of-order — independent, parallel-safe). NEXT: **B6 Slice 2** (operator-gated; Slice 1 ✅) — the only remaining FROZEN child arc.

**Two kinds of "dependency."** The frozen order is a chosen *sequence*; it is **not** the same as
a hard *blocker*. Most remaining arcs' real prerequisites have already landed, so they are
sequenced — not blocked — by the order.

- **Serial cluster — "SHARED-RUNTIMECONFIG".** Arcs that all edit the same two surfaces (the
  `RuntimeConfig` object + the workflow-driver dispatch path) are kept **serial** so they don't
  collide: **B3 ✅, B2 ✅, E ✅, B4 ✅, B6**. (M ✅ landed as a standalone `MANAGED_AGENTS` StepKind + a surface-gated stage-5 binding — it did NOT contend the shared dispatch path.) These should land one at a time.
- **Genuinely independent (parallel-safe).** **CA ✅, B5 ✅, B7 ✅, M ✅** touch none of the cluster's shared
  surfaces — they can be built in parallel with the serial cluster and with each other.
- **Standalone arcs (`B-*`).** Nine smaller capabilities that surfaced *during* implementation
  (not in the frozen order). Each is a committed build, sequenced as a follow-on when its turn
  comes (see §5).

**What's actually unblocked today:** B7 has its real prerequisites landed
(CA ✅ #625; B5 ✅ #628). It is sequenced by the frozen order, not blocked. B6 Slice 2 (NEXT) is best
done within the serial cluster (after B4 ✅, to avoid `RuntimeConfig` contention) — the only remaining
FROZEN child arc now that M ✅ landed (#635).

---

## 3. Finished arcs (real, as-built units)

### R-FS-1·B1 — Non-linear topology orchestration

- **Status:** ✅ done (build position 1 of 11) · **Cluster:** SHARED-RUNTIMECONFIG · **Units:** as-built
- **Depends-on:** foundational runtime/CP carriers (landed in its own first legs)
- **What it gives the harness.** The ability to run agents in **team shapes beyond a single straight
  line.** Before B1, the harness could only run one step after another. B1 added the six
  collaboration patterns: agents working in **parallel**, an **orchestrator** handing sub-tasks to
  **worker** agents, a **reviewer↔improver** loop, a **delegation hierarchy**, and peer **hand-offs**.
  This is what lets the harness coordinate a *fleet* of agents, not just one.

| Unit(s) | Leg / PR | What it does (plain language) |
|---|---|---|
| U-IS-19 + U-RT-113 | impl-1 (#537) | Foundational carriers — the data structures that record which branch of a multi-agent run produced what. |
| U-CP-80 + U-CP-81 | impl-2 (#538) | The driver substrate — the engine piece that actually executes a non-linear topology. |
| U-CP-82 + U-CP-83 | impl-3 (#539) | Buffered-append substrate — safely records each branch's results without races. |
| U-CP-84 | impl-4 (#540) | Writes each branch's terminal status (succeeded / failed) at the right cadence. |
| U-CP-85 | impl-5 (#542) | Cascade policy — how a failure in one branch propagates (or doesn't) to siblings. |
| U-CP-86 | impl-6 (#544) | **PARALLELIZATION** — run independent agent steps at the same time. |
| U-CP-87 | impl-7 (#545) | **EVALUATOR_OPTIMIZER** — one agent proposes, another critiques, loop to improve. |
| U-CP-88 + U-RT-114 | impl-8 (#546) | **ORCHESTRATOR_WORKERS** — a lead agent farms sub-tasks to workers; plus the per-role *model* selection seam (each role can get its own model). |
| U-CP-89 | impl-9 (#547) | **HIERARCHICAL_DELEGATION** — multi-level delegation down a tree of agents. |
| U-CP-90 | impl-10 (#548) | **DECENTRALIZED_HANDOFF** — peers pass control directly to one another. |

### R-FS-1·B3 — Smart human-in-the-loop (HITL) decision intelligence

- **Status:** ✅ done (build position 2 of 11) · **Cluster:** SHARED-RUNTIMECONFIG · **Units:** as-built
- **Depends-on:** B1 (topology) for the dispatch path it extends
- **What it gives the harness.** Makes the harness **smarter about when to pause for a human.**
  Instead of always pausing (or never pausing) at a checkpoint, it can **conditionally skip** an
  approval that clearly isn't needed, **degrade gracefully** if a human doesn't respond in time
  (per the run's mode), and let a human **edit** a pending action instead of only approve/reject.

| Unit(s) | Leg / PR | What it does (plain language) |
|---|---|---|
| U-CP-91 + U-RT-115 + U-RT-116 + U-RT-117 + U-RT-118 | impl-1 (#554) | Conditional skip — decide when an approval checkpoint can be safely bypassed. |
| U-CP-92 + U-RT-119 | impl-2 (#584) | Timeout-degradation — what to do (per run mode) when a human doesn't answer in time. |
| U-RT-120 | impl-3 (#584) | EDIT = replace-not-merge — a human-edited action cleanly replaces the pending one. |

### R-FS-1·E — Durable execution engines

- **Status:** ✅ done (build position 3 of 11) · **Cluster:** SHARED-RUNTIMECONFIG · **Units:** as-built
- **Depends-on:** B1 (shares the workflow-driver dispatch site)
- **What it gives the harness.** Lets a long-running agent workflow **survive a crash or restart
  and pick up where it left off** instead of starting over. Three durable "engine" styles were
  hand-rolled (no vendored Temporal/K8s, per the stack rules): **replay-from-event-history**,
  **write-ahead-log segments**, and a **reconciler loop** that keeps re-converging to the desired
  state.

| Unit(s) | Leg / PR | What it does (plain language) |
|---|---|---|
| U-CP-93 | impl-1 (#562) | EVENT_SOURCED_REPLAY — rebuild state by replaying the recorded event history. |
| U-CP-94 + U-CP-95 + U-RT-121 + U-RT-122 | impl-2 (#564) | WAL_SEGMENT — an append-only write-ahead log with per-segment resume. |
| U-CP-96 | impl-3a (#570) | RECONCILER_LOOP — materialize the control-loop engine class. |
| U-RT-123 | impl-3b (#574) | Revision-CAS reconciler substrate — safe compare-and-set so a resumed loop doesn't double-execute. |
| U-CP-97 + U-RT-124 | impl-3c (#576) | The engine-layer pause/resume seam (brings the CP→IS durable-recovery composition live). |

### R-FS-1·B2 — Multi-server MCP client

- **Status:** ✅ done (build position 4 of 11) · **Cluster:** SHARED-RUNTIMECONFIG · **Units:** as-built
- **Depends-on:** single-server MCP client (pre-existing); reshapes it to many servers
- **What it gives the harness.** Lets the harness connect to **many tool servers at once** (not
  just one), route each tool call to the right server, handle two servers offering the same tool
  name, and apply **per-server trust** rules. (MCP = the standard protocol agents use to call
  external tools.)

| Unit(s) | Leg / PR | What it does (plain language) |
|---|---|---|
| U-RT-129 | impl-1 (#588) | Per-server trust telemetry keyed by a stable server identity. |
| U-RT-125 | impl-2a (#590) | Reshape the single `mcp_client_host` into a `dict` of many hosts. |
| U-RT-126 + U-RT-127 + U-RT-128 + U-RT-130 | impl-2b (#592) | Multi-server routing, dispatch, same-tool-name collision policy, and per-host handling. |
| U-CP-98 + U-RT-131 | impl-3 (#594) | The MCP-trust gate axis — enforce each server's trust tier at dispatch time. |

### R-FS-1·R — Routing intelligence (LLM-as-router + embedding)

- **Status:** ✅ done (build position 5 of 11) · **Cluster:** SHARED-RUNTIMECONFIG · **Units:** as-built
- **Depends-on:** the layered routing infrastructure (pre-existing); adds the L2/L3 decision functions
- **What it gives the harness.** Lets the harness **intelligently pick which model handles a
  request.** Two layers were built: **Layer 3 (LLM_AS_ROUTER)** asks a small "router" LLM to choose,
  and **Layer 2 (EMBEDDING)** matches the request against labeled examples using embeddings.
  Both are **built and proven** but **not yet switched on in production** — production still uses the
  simple declarative layer; turning L2/L3 on needs a second provider configured (see the
  routing-activation gate, §6).

| Unit(s) | Leg / PR | What it does (plain language) |
|---|---|---|
| U-CP-99 + U-CP-100 + U-RT-132 + U-RT-133 | impl-1 (#602) | LLM_AS_ROUTER L3 — the router-resolution contract + the run-loop branch that calls it (mock router, no paid call). |
| *(impl-discretion, no new unit)* | impl-2 (#604) | The real Ollama router behind L3 + a gated live end-to-end test (free local model). |
| *(impl, no spec change)* | R/L2 (#606) | EMBEDDING L2 — an in-process `fastembed` k-NN classifier behind an injected embedding function. |

---

### R-FS-1·B4 — Per-role / per-step dispatch indexing

- **Status:** ✅ done (build position 6 of 11) · **Cluster:** SHARED-RUNTIMECONFIG · **Units:** as-built
- **Depends-on:** B1 ✅ (per-role *model* seam), R ✅, B2 ✅
- **What it gives the harness.** Makes the per-role **model and prompt actually take effect**, with
  individual steps able to override either — so a "researcher" and a "writer" worker in the same
  workflow each get their own model *and* system prompt, and any step (branch *or* straight-line)
  can be pinned to a specific role. The per-role *model* half landed in B1; **B4 finished the
  per-role *prompt*, the binding catalog, per-step prompt + role overrides, and linear-path role
  indexing.** (The 4 slices extended existing contracts — C-CP-06 `StepOverride` / C-RT-15 dispatch
  / C-IS-05 §5.2 — rather than minting new plan-units, so they are keyed by slice + PR.)

| Unit(s) | Leg / PR | What it does (plain language) |
|---|---|---|
| *(impl + IS spec v1.9)* | Slice 1 (#616) | Per-role PROMPT threading — a fan-out branch's role selects + injects its own system prompt at dispatch; the IS C-IS-05 §5.2 procedural-tier hash widened (`prompt_selection_manifest_sha`) so per-role bindings are audit-hash-visible. |
| `harness_cp.per_role_catalog` | Slice 2 (#618) | The per-role binding **catalog** surface (`derive_agent_role` + `validate_per_role_catalog`) — the single `step_id→AgentRole` derivation operators key their role→model/prompt tables on. |
| `StepOverride.prompt_version_sha` (CP spec v1.37) | Slice 3 (#619) | Per-step **PROMPT** override — a step injects a chosen prompt version; precedence per-step > per-role > default, with deployment-tier governance parity. |
| `StepOverride.agent_role` (CP v1.38 + runtime v1.52) | Slice 4 (#621) | Per-step **ROLE** override + linear-path role indexing — any step is pinned to a role (Option-B composition-time fold; operator-ratified §14.5.3 invariant-2/3 relaxation). |

---

## 4. Remaining arcs (anticipated scope — units decomposed at arc-open)

These are committed builds (the full-spec directive defers nothing). The atomic units are **not
yet decomposed** — that happens in each arc's own plan leg. The slices below are *leads* from the
grounding sweep (`.harness/r-fs-1-remaining-arcs-grounding-sweep-v1.md`), re-grounded at arc-open.

### R-FS-1·CA — Cost aggregate rollup

- **Status:** ✅ DONE (build position 7 of 11; PR #625, runtime spec v1.53 §9 C-RT-09) · **Cluster:** independent (parallel-safe) · **Type:** small spec fork + bounded impl
- **Depends-on:** B1 ✅ (so multi-branch runs produce real per-call costs to roll up) — **was unblocked**
- **Parallel-safe with:** the serial cluster, B5, B7
- **What it gave the harness.** The harness now **reports the total cost of a run, broken down by
  provider+model** (`RunResult.cost_attribution`, was hard-coded `()`). Per-call cost records
  (LLM/tool/validator/webhook) accumulate over the run and roll up at `_build_run_result` along
  `RollupAxis.PER_PROVIDER_AND_MODEL` (single axis ⟹ `sum(total_cost)` = true run cost).

| As-built slice (PR #625) | What it did | Fork / impl |
|---|---|---|
| Aggregate-shape contract | Named the axis `PER_PROVIDER_AND_MODEL` + reconciled the phantom `CostAttribution` type-name (runtime spec v1.52→v1.53 §9). `PER_PROVIDER_DISCRIMINATOR` inadmissible (production dispatch-type tags ∉ `CrossFamilyTag` → registered as `B-COST-DISCRIMINATOR-TAXONOMY`). | fork (pre-authorized, no operator gate) |
| Run-scoped accumulator | `CostRecordAccumulator` holder on `HarnessContext` (by-reference — a typed `list` would be Pydantic-copied at `freeze()`; advisor-caught). | impl |
| Wire the rollup | 4 per-dispatch cost wrappers append; `_build_run_result` rolls up + sets the field. Freeze-by-reference regression test added. | impl |

### R-FS-1·B5 — Memory backend per deployment surface

- **Status:** ✅ DONE (build position 8 of 11) · **Cluster:** independent (parallel-safe) · **Units:** as-built (PR #628) · **Type:** thin impl, no fork
- **Depends-on:** R-830 ✅ (the filesystem / SQLite / S3 / managed-DB backends already exist) — **unblocked**
- **Parallel-safe with:** the serial cluster, CA ✅, B7
- **What it gives the harness.** Lets the agent's **memory store pick the right backend for where
  it's deployed** — a local file for local dev, a cloud database or S3 in the cloud. The backends
  all exist; the selector previously **ignored the deployment surface and always returned one
  backend**. B5 makes that selection real (a surface→backend map resolved once at startup).

| As-built slice (PR #628) | What it did | Fork / impl |
|---|---|---|
| Registry surface→backend map | `MemoryToolRegistry` keeps the single-backend constructor (override / one-backend-for-any-surface) + adds `from_surface_map`; `resolve_backend` is a pure lookup over the bootstrap-frozen map that replays a frozen `RT-FAIL` for an unconfigured surface. | impl |
| Factory populates the map | Default path resolves each surface independently (config-free `FILESYSTEM`, built once per distinct enum) + freezes a deferred `RT-FAIL` for surfaces with no config-free backend (`MANAGED_CLOUD`); the **active surface must resolve or bootstrap aborts fail-closed** (preserves pre-B5 active-`MANAGED_CLOUD`-no-override). Override forces one backend for every surface. | impl |
| Anti-vacuity + fail-closed lock | `resolve_backend(LOCAL)`→filesystem vs `resolve_backend(MANAGED)`→`RT-FAIL` (constructs-vs-raises proves the arg is read) + a regression test locking the active-`MANAGED`-no-override bootstrap-abort. | impl |

*Active-surface dispatch is byte-identical (production threads the single active surface); the multi-surface map is contract-shape, not a runtime multiplex feature. The two spec'd-but-unimplemented backends (`ENCRYPTED_FILESYSTEM`, `OPERATOR_DEFINED`) registered as the forward arc `B-MEMORY-SURFACE-BACKEND-IMPLS` (§5).*

### R-FS-1·B6 — Per-tool sandbox tier + STDIO transport floor

- **Status:** ▶ NEXT (build position 9 of 11) · **Cluster:** SHARED-RUNTIMECONFIG (serial) · **Units:** anticipated · **Type:** medium fork + impl
- **Depends-on:** the per-server sandbox resolver (#503 ✅); couples with B2 ✅ (multi-server)
- **Serial with:** B4 (avoid `RuntimeConfig` / dispatch-path contention)
- **What it gives the harness.** Lets the harness apply a **different security sandbox level per
  individual tool** (instead of one level for the whole server), and enforce a **minimum container
  level for local-pipe (STDIO) tools.** The full per-tool security table already exists in the
  action-surface code; B6 **wires it into per-tool dispatch** (today dispatch uses one constant
  per-server tier).

| Anticipated slice | What it does (plain language) | Fork / impl |
|---|---|---|
| Per-tool resolver contract | Amend the runtime spec so the sandbox decision may discriminate per tool. | fork (pre-authorized) |
| Wire the discriminating floor | Call the existing per-cell tier table per (tool, step) — delivers per-tool tier *and* the STDIO floor in one move. | impl |
| Per-dispatch driver granularity | Pick the sandbox driver per dispatch (so a high-tier tool gets a high-tier sandbox). | impl (coupled to the fork) |

### R-FS-1·B7 — Sampler conditional over-sampling refinement

- **Status:** ✅ DONE (build position 10 of 11; PR #632 — OD SSOT predicate + head-sampler wiring) · **Cluster:** independent (parallel-safe) · **Units:** as-built #632 (`sampling_mode` predicate + `composite_sampler` wiring; no new plan-unit) · **Type:** thin impl, no fork (impl-to-cleared-spec §9.2/§10.1)
- **Depends-on:** none hard (stdlib + OTel already in stack) — was **unblocked**
- **Parallel-safe with:** everything
- **What it gives the harness.** Refines the **telemetry sampler** so it only force-captures the
  spans that truly matter — data **mutations**, **permanent failures**, and **root** spans —
  instead of force-capturing *everything* in those categories. It's safe today (it over-captures,
  never under), so this is a precision/cost refinement, not a correctness fix.
- **As-built (#632) + honest boundary.** Built the §9.2 attribute-conditional resolution as the OD
  SSOT (`is_always_sampled(name, attributes)`: files/memory mutation-`kind`, `validator.fail.*`
  permanence; conservative-absent) + wired it into `should_sample`. The head sampler governs only
  **root** spans (ParentBased) and the live files/memory producers emit non-root spans + set
  `*.kind` post-creation, so full non-root / production-tail enforcement is the forward arc
  **`B-TAIL-CONDITIONAL-SAMPLING`** (tail-keep span processor; gated on R-420/R-421). `subagent.span`
  root-ness is delivered by ParentBased (no change). No fork, no operator gate.

| Anticipated slice | What it does (plain language) | Fork / impl |
|---|---|---|
| Attribute-aware predicate | Decide "always sample?" using the span's attributes (mutation kind / failure permanence / root-ness), not just its name. | impl |
| Wire it into the sampler | Route non-mutation / non-permanent / non-root spans to the normal base rate. | impl |
| Test by execution | Confirm a mutation always samples while a read falls to base rate. | impl |

### R-FS-1·M — Managed-agents contract + production wiring

- **Status:** ✅ DONE (build position 11 of 11; PR #635 — C-RT-28 §14.20 + CP v1.39 `StepKind.MANAGED_AGENTS`) · **Cluster:** independent (parallel-safe — a new StepKind + a surface-gated stage-5 binding, NOT shared-dispatch contention) · **Units:** as-built · **Type:** spec delta + impl + the operator-gated closed-at-5 StepKind extension
- **Depends-on:** the managed-agents adapter (built + live-proven via R-820 ✅)
- **What it gives the harness.** Formalized and **production-wired the integration with Anthropic's
  Managed Agents service** (vendor-runs-the-loop). M **authored the formal contract** (C-RT-28) and
  **wired a `StepKind.MANAGED_AGENTS` step through the run loop** — previously nothing in the
  production run loop reached the R-820 carrier.

| As-built slice | What it does (plain language) | Fork / impl |
|---|---|---|
| Contract authoring | Authored C-RT-28 §14.20 (runtime v1.55) + the paired CP v1.39 `StepKind.MANAGED_AGENTS`. | fork (operator-ratified — Option B) |
| Production wiring | `ManagedAgentsStepDispatcher` bound (via `SyncDispatcherFacade`) on a NEW `StepKind.MANAGED_AGENTS`, surface-gated to `MANAGED_CLOUD` + opt-in. Option A (riding `SUB_AGENT_DISPATCH`) probe-foreclosed. | impl |
| Live run | A real managed-cloud run (`@pytest.mark.e2e` + skipif-gated; touches paid + cloud credentials) — surfaced at the boundary, **never auto-fired**. H_T-AS-8f already SUBSTANTIVE_RETIRED (R-820), so it is NOT a retirement prerequisite. | vendor-gate |

---

## 5. Standalone forward arcs (`B-*`) — design-fork-first, unsequenced

Smaller capabilities that surfaced *during* implementation. Each is a committed build (full-spec
directive), sequenced as a follow-on R-FS-1 child arc when its turn comes. Full disposition: the
spine ledger (`.harness/beyond-mvp-capability-boundary-ledger.md`).

| id | Owner-axis | What it gives the harness (plain language) |
|---|---|---|
| B-INTERSTEP | runtime | Pass **data** from one workflow step to the next (today steps share control-flow only, not each other's outputs). |
| B-FANOUT-PAUSE | CP + runtime | **Resume a paused parallel fan-out** from where it stopped (today it fails honestly instead of resuming). |
| B-ENGINE-OUTPUT-REPLAY | CP + runtime/IS | **Replay cached step outputs** from event history (today a resume skips finished steps but can't reproduce their outputs). |
| B-EFFECT-FENCE | runtime + AS | Guarantee a side-effecting step **runs at most once** across retries/resumes. |
| B-EDIT-CARRIER | runtime + CP | Let a human **EDIT** a pending action even when its data shape differs (today EDIT raises for some shapes). |
| B-LAYER-BUDGET-OVERRIDE | CP | Enforce **per-layer time budgets** honoring per-workload/persona overrides. |
| B-TOOL-GATE | runtime | Wire the **real per-server MCP-trust source** at the tool-step human-approval gate (today gate sites auto-approve). |
| B-L2-EMBEDDING-ACTIVATION | runtime + CP | **Switch on L2/L3 routing in production** (the routing-activation gate below + wire the classifier/router + promote `fastembed`). |
| B-MEMORY-SURFACE-BACKEND-IMPLS | runtime | Build the two remaining spec'd memory backends — **`ENCRYPTED_FILESYSTEM`** (filesystem + per-path encryption) and **`OPERATOR_DEFINED`** (operator-supplied class resolved by introspection) — that B5's surface→backend routing will then dispatch to (today the factory raises for both). |

---

## 6. Routing-activation gate — visibility-only, currently UNOWNED

The shared production-activation switch for **both** L2 EMBEDDING and L3 LLM_AS_ROUTER: make the
declarative routing layer **conditional** so a request can actually reach the EMBEDDING /
LLM_AS_ROUTER layers (today the declarative layer always resolves first, so `route()`
short-circuits before them — both routing layers are **built and proven but production-inert**).

Both R-300 items closed **without** doing this work (routing-activation kept declarative behavior
by design; second-provider added credentials + fallback only), so this gate has **no open owner**.
It is **not** a derivation-eligible roadmap item (minting one would split the single-next-action
rule); it is a real forward unit that needs an owner once routing-among-candidates becomes
meaningful — i.e., once a second production provider is configured. Captured at
`B-L2-EMBEDDING-ACTIVATION` in the spine ledger.

---

## 7. At-a-glance summary

| Arc | Capability (plain language) | Status | Pos | Cluster | Units |
|---|---|---|---|---|---|
| B1 | Run agents in team topologies (parallel, orchestrator, etc.) | ✅ done | 1 | serial | 14 as-built |
| B3 | Smart pausing for humans (skip / degrade / edit) | ✅ done | 2 | serial | 8 as-built |
| E | Survive crashes & resume (durable engines) | ✅ done | 3 | serial | 9 as-built |
| B2 | Connect to many tool servers at once | ✅ done | 4 | serial | 8 as-built |
| R | Intelligently pick which model handles a request | ✅ done | 5 | serial | 4 as-built (+L2/L3 impl) |
| B4 | Per-role & per-step model + prompt | ✅ done | 6 | serial | 4 slices as-built (#616/#618/#619/#621) |
| CA | Report total run cost, broken down | ✅ done | 7 | independent | 3 slices as-built (#625) |
| B5 | Pick the memory backend per deployment | ✅ | 8 | independent | as-built #628 |
| B6 | Per-tool security sandbox level + STDIO floor | ▶ next | 9 | serial | at arc-open |
| B7 | Sample only the telemetry that matters | ✅ | 10 | independent | as-built #632 |
| M | Formal contract + wiring for managed agents | ✅ | 11 | independent | as-built #635 |

*Counts: as-built unit totals are grouped by arc from `git log` (B1=14, B3=8, E=9, B2=8, R=4 core
units + the L2/L3 impl-discretion legs; B4=4 slices #616/#618/#619/#621, which extended existing
contracts C-CP-06 / C-RT-15 / C-IS-05 rather than minting new plan-units; CA=3 slices #625, which
extended C-RT-09 rather than minting new plan-units). Remaining arcs decompose at arc-open.*

---

*Filing footer — Artifact: `.harness/r-fs-1-arc-and-unit-map.md`. Single arc→unit home; dashboard
forward sections parse this. As-built units sourced from `git log --grep="R-FS-1"`; remaining-arc
scope from `.harness/r-fs-1-remaining-arcs-grounding-sweep-v1.md` (re-ground at arc-open,
presence-not-correctness). Spine: `.harness/beyond-mvp-capability-boundary-ledger.md`. Posture:
mode-agnostic; X-AL-3 trivially clean.*
