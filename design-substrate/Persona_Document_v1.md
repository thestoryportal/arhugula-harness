# Persona Document v1

**Project:** Multi-LLM Agent Harness (V3-framed; agnostic on persona, stack, deployment surface beyond V3 commitments).

**Phase:** 2 — Persona Surfacing (Project Workflow v1.0 §2.2).

**Deliverable Source:** Single Phase 2 dialogue session conducted by `systems-architect` skill in persona-surfacing mode, per `references/persona-surfacing-protocol.md`.

**Status:** v1 — first persona surfacing pass complete. Open items routed to §11 with closing paths.

**Confidence schema (V3):** [HIGH] / [MODERATE] / [SPECULATIVE] applied to substantive analytical claims in §§8–10. Persona statements in §§2–7 are operator-asserted and not tagged per protocol §4.

**Section guide:**

- §1 Persona definition (one-paragraph synthesis)
- §2 User — Dimension 1 output
- §3 Workloads — Dimension 2 output
- §4 Scale — Dimension 3 output
- §5 Integration surface — Dimension 4 output
- §6 Hard constraints — Dimension 5 output
- §7 Soft preferences — Dimension 6 output
- §8 Workload-shape implications across the five axes
- §9 Deployment-surface implications
- §10 Persona-dependent decision pre-classifications (F1–F5, T-tensions, cross-axis tension clusters)
- §11 Open items with closing paths

---

## §1 Persona definition

A **bridging-arc persona**. The operator at design-time is a sole mixed/multi-role operator with direct host access; the harness is expected to evolve to a team or multi-tenant binding state later. Workloads are heterogeneous: software/web engineering, content creation, pipeline & automation, and research/analysis-knowledge-work are all first-class, with operator-asserted extensibility for workload classes not yet realized. Work-unit shape distribution spans single-shot ephemeral through multi-day durable, with mixed cardinality (serial, parallel-interactive, batch coexist). Scale targets tens of concurrent harness workflows — possibly per-task-class — at a 99.9%+ completion SLO. Action surface is broad: code execution, computer-use / browser-driving (at both design-time and production-time, with a stronger sandbox tier in production), and API / SaaS / MCP integrations are all in-scope. Persistent state lives on local filesystem + remote git. Multi-LLM provider mix is hosted majors plus a local / open-weight routable tier (Ollama, vLLM, llama.cpp). Operator stack is Python-first with pragmatic-mixed ecosystem affinity (Anthropic primitives where they fit; vendor-neutral abstraction otherwise). Workflow-definition surface supports both markdown-spec-driven and code-driven authoring.

---

## §2 User

*Output of Dimension 1 (protocol §2.1).*

### 2.1 Directly-captured facts

- **Operator cardinality:** Bridging — sole operator at design-time; team or multi-tenant binding state later. Persona must accommodate both ends of the arc.
- **Operator role and expertise:** Mixed / multi-role (operator wears several hats).
- **Operator interaction with harness host:** Direct host access (terminal / IDE on the machine running the harness) at design-time.

### 2.2 Implied by bridging-arc cardinality (not separately probed)

- **Same-operator-across-sessions:** Trivially same at design-time (sole operator). At multi-tenant binding state, operators will vary by definition of multi-tenant. Specifics routed to §11.
- **Future-state operator interaction layer** (CLI / IDE / web UI / API consumer / scheduled trigger at team or multi-tenant binding): not probed; routed to §11.
- **Tenant-isolation expectations:** non-trivial at the future state. Resurfaces in §6 (compliance regime open at multi-tenant binding), §10 (T3 traversal as a Phase 3 architectural challenge), and §11.

---

## §3 Workloads

*Output of Dimension 2 (protocol §2.2).*

### 3.1 Primary task classes (each first-class)

**3.1.1 Software / web engineering.** Code generation, refactoring, debugging, build/test work, dev-loop integration. Highest natural alignment with the broad action surface (code execution + filesystem + git).

**3.1.2 Content creation.** Writing, editing, marketing/media-asset creation, long-form authoring.

**3.1.3 Pipeline & automation.** ETL, scheduled jobs, multi-step data and document workflows. Highest natural alignment with the durable end of the work-unit-shape distribution.

**3.1.4 Research, analysis, knowledge work.** Literature review, summarization, structured investigation.

### 3.2 Secondary / future task classes

Operator-asserted: *"potentially others not currently realized."* Captured as a **workload-class extensibility flag** — the harness must accommodate task classes not enumerated at design-time. Constraint level (hard requirement vs soft preference vs per-class) deferred to §11.

### 3.3 Work-unit shape distribution

Heterogeneous across the spectrum: single-shot ephemeral, long-running durable (hours-to-days, survives restarts), and intermediate shapes all coexist. Selection per-workload-instance is determined by the project's requirements, not by harness configuration.

### 3.4 Cardinality

Mixed — serial single-active-workflow, parallel-interactive multiple-concurrent-workflows-the-operator-is-steering, and batch / queued non-interactive throughput all coexist.

### 3.5 Out-of-scope task classes

None flagged at this dimension.

---

## §4 Scale

*Output of Dimension 3 (protocol §2.3); each sub-field tagged.*

- **Concurrency:** Tens of concurrent harness workflows, possibly per-task-class (i.e., approaching ~10 per class × 4 primary classes ≈ low-tens to ~40 aggregate). [order-of-magnitude]
- **Throughput:** **§11 open item.** Closing path: emerges from operational telemetry once harness is running and workloads materialize.
- **Retention:** Mixed by artifact class — some artifacts ephemeral after session close; others long-retained (the latter likely living on git history and/or checkpointed filesystem-tier per §5).
- **Reliability target:** **99.9%+ completion** (harness-grade SLO). Implication named per protocol §2.3 trigger: production reliability lives in the deterministic outer harness, not in LLM behavior. Tens-concurrent + 99.9% is mathematically incompatible with operator-in-loop-on-every-failure HITL — HITL must be selective, with the deterministic outer harness absorbing most recovery.

---

## §5 Integration surface

*Output of Dimension 4 (protocol §2.4); in-scope and out-of-scope separated.*

### 5.1 In-scope

- **Model providers:** Hosted majors (Anthropic, OpenAI, presumably others to be enumerated downstream) **plus** local / open-weight tier (Ollama, vLLM, llama.cpp) as routable.
- **Tool / action surface:** Broad — code execution, computer-use / browser-driving, API / SaaS / MCP integrations all first-class.
- **Computer-use specifically:** At both **design-time AND production-time**, with **stronger sandbox tier at production-time** (operator-asserted).
- **Repository and persistent storage:** Local filesystem + remote git (GitHub / GitLab class).

### 5.2 Out-of-scope

None explicitly flagged at this dimension. **§11 routing:** revisit when a specific exclusion surfaces (e.g., during F1 provider-abstraction or F4 sandbox-tier deliberation in Phase 3a).

---

## §6 Hard constraints

*Output of Dimension 5 (protocol §2.5); each item with stated source.*

| Constraint | Status | Source |
|---|---|---|
| Compliance regime | Open / customer-mix-dependent at multi-tenant binding | Operator-asserted deferral |
| Cost ceiling | Per-workload-class ceiling (different limits per class) | Operator-asserted |
| Vendor restrictions | None formal at this dimension | Operator-asserted |
| IP-handling rules | None formal at this dimension | Operator-asserted |
| Latency budget | None flagged this dimension; §11 open item | Operator-asserted (no signal); §11 routing |
| Data-locality / residency | Folded into compliance — also open | Operator-asserted deferral |

**Source-discipline note (protocol §2.5).** At design-time / early-bridging, the operator is the canonical hard-constraint authority because no external regime is contractually binding. External regimes (compliance, vendor allowlists, IP-handling rules) bind later in the bridging arc when contractually triggered. The harness's hard-constraint surface is therefore **temporally bound**, not statically given — itself a persona finding.

---

## §7 Soft preferences

*Output of Dimension 6 (protocol §2.6); each item tagged soft.*

- **Stack familiarity** (soft): **Python-first** (data, ML, scripting; broadest LLM-ecosystem alignment).
- **Ecosystem affinity** (soft): **Pragmatic-mixed** — Anthropic primitives where they fit (prompt caching, batch API, extended-thinking budget controls, MCP, structured outputs); vendor-neutral abstraction where they don't.
- **Workflow-definition surface** (soft): **Both** markdown-spec-driven AND code-driven authoring supported (operator picks per workload class). Workflow-class-extensibility-friendly per the §3.2 flag.

---

## §8 Workload-shape implications

Per protocol §3, per primary workload class × five axes (control plane, information substrate, action surface, operational discipline, deployment surface). Implications-only — no mechanism commitments.

### 8.1 Software / web engineering

- **Control plane.** [HIGH] Multi-step session shape dominant; evaluator-optimizer / Reflexion-style validation loops natural fit. [MODERATE] Parallel multi-agent reads (review, eval) acceptable; writes single-threaded per synthesis §1 strong-convergence ("digital gossiping" failure mode, Cognition).
- **Information substrate.** [HIGH] F2 leverage maximal — code-as-files-in-git is canonical; scratch in workspace, durable artifacts versioned via commits.
- **Action surface.** [HIGH] Code execution + filesystem + git as primary; LLM-generated code execution requires F4 sandbox per synthesis §9 Q13. [MODERATE] MCP for external services secondary; computer-use for browser testing situational.
- **Operational discipline.** [HIGH] Linters, type-checks, unit tests as in-loop deterministic gates per synthesis §8 strong-convergence. [MODERATE] Per-class cost ceiling applies; long sessions warrant cost-aware routing within budget.
- **Deployment surface.** [HIGH] Design-time on developer machine. [MODERATE] Production-time depends on sub-shape (CI integration, dev-environment automation, agent-as-service patterns).
- **F3 durability:** mixed — refactor and short fixes ephemeral; multi-day investigations durable.

### 8.2 Content creation

- **Control plane.** [MODERATE] Multi-step session shape typical; lower parallelism need than software-eng. [HIGH] HITL naturally synchronous at design-time (operator review-in-loop); at multi-tenant binding, async HITL becomes feasible.
- **Information substrate.** [HIGH] Filesystem + git for versioned drafts. [MODERATE] Long-form content with non-text media (images, video, audio) may surface object-storage-tier need that current §5 in-scope items don't cover; flagged for §11-adjacent revisit.
- **Action surface.** [MODERATE] Lighter — LLM calls + filesystem dominant; MCP for asset retrieval; computer-use for media-tool integration situational.
- **Operational discipline.** [HIGH] Quality gates are predominantly subjective (out-of-loop LLM-as-judge per synthesis §9 Q21); in-loop gates limited to format / structural validation. [MODERATE] Cost-aware routing relevant — long-form generation can burn tokens fast.
- **Deployment surface.** [MODERATE] Tolerant of any surface; lightest deployment-surface constraint among the four classes.
- **F3 durability:** mostly ephemeral or session-scoped; occasional multi-stage editorial workflow durable.

### 8.3 Pipeline & automation

- **Control plane.** [HIGH] F3 durable-execution-spine territory par excellence; multi-stage workflows with explicit step boundaries; durable state across hours-to-days. [MODERATE] Often scheduled or event-triggered, not interactive.
- **Information substrate.** [HIGH] State ledger as first-class; per-stage checkpointing; durability tier mandatory.
- **Action surface.** [MODERATE] API / SaaS / MCP integrations dominant; less code-execution; less computer-use.
- **Operational discipline.** [HIGH] Retry / breaker discipline most rigorous of all four classes; idempotency keys non-negotiable; rate-limit-storm prevention non-trivial; cross-step traceability is the dominant observability requirement.
- **Deployment surface.** [MODERATE] Production-time deployment most likely needed (scheduled jobs run without operator presence). [SPECULATIVE] Pushes toward cloud-managed or hybrid surfaces at multi-tenant binding.
- **F3 durability:** typically durable (defining feature of the class).

### 8.4 Research / analysis / knowledge work

- **Control plane.** [MODERATE] Variable shape — quick lookups (single-shot) through multi-day investigations (long-running). [HIGH] Multi-agent reads / evaluation pattern natural fit per synthesis §8 strong-convergence ("multi-agent for reads/evaluation only; writes single-threaded").
- **Information substrate.** [HIGH] Knowledge artifacts (notes, summaries, citations) typically markdown + filesystem; long retention common for research products → long-retained artifact tier from §4 applies.
- **Action surface.** [HIGH] Web / API / browser-driving for research collection; document parsing tools; less code execution.
- **Operational discipline.** [MODERATE] Judge-base-model alignment matters (synthesis §4 Husain loop); citation-discipline gates as in-loop deterministic checks.
- **Deployment surface.** [MODERATE] Tolerant; design-time fits naturally.
- **F3 durability:** mixed — quick lookup ephemeral; multi-day investigation durable.

### 8.5 Cross-class pattern — cost × reliability × capability routing

[MODERATE] Per-class cost ceiling (§6) + 99.9% reliability target (§4) + hosted+local provider mix (§5) produces a coupled routing-strategy deliberation no single class fully exhibits but every class is touched by. Local / open-weight is cheap but variably capable; hosted frontier is expensive but reliable; per-class budgets are real. Routing must be simultaneously cost-aware (synthesis §9 Q19–20), reliability-aware (synthesis §9 Q23 alignment-floor telemetry), and capability-aware (synthesis §9 Q14 layered routing). Phase 3a/3b derivative-decision cluster — surfaced here to flag the cross-axis coupling.

---

## §9 Deployment-surface implications

[HIGH] **Design-time:** forced to local-development environment per V3 commitment. Direct-host-access answer (§2) confirms.

[MODERATE] **Production-time:** option space narrowed but not picked. Persona constraints on the production surface:

- Computer-use-at-production with stronger sandbox tier (§5) → microVM-class isolation availability required.
- Tens-concurrent + durable workloads + 99.9% (§4) → operational depth required (durable-execution coordination, multi-process or job-queue topology, observability with retention controls).
- Bridging arc to multi-tenant → per-tenant isolation accommodation at multi-tenant binding (T3 traversal).
- [SPECULATIVE] Pure local-only production with computer-use-at-scale + tens-concurrent + 99.9% is feasible operator-side but operationally heavy; not excluded.

Persona constrains the production-time option space; does NOT pick a specific surface. Cloud-managed, hybrid, and on-prem-with-sufficient-infrastructure remain live options pending Phase 3 deliberation.

---

## §10 Persona-dependent decision pre-classifications

Per protocol §3 — three lists with stated source dimension(s). Incorporates per-F-decision review pass conducted this session.

**Structural note.** Persona is strongly opinionated about foundational *principles* (F1-commitment, F2 substrate principle, F4 graduated-isolation principle, F5 cross-deployment secrets bridge principle) but explicitly defers the engineering of those principles to Phase 3a/3b D-derivatives. F3 is the heterogeneity-exception — coarse classification with detail in §8. §10 row structure is therefore heterogeneous; intentional and reads cleanly for downstream council deliberation.

### 10.1 Persona-answered

| Decision | Source |
|---|---|
| F1-commitment (multi-LLM scope: hosted majors + local/open-weight tier) | §5, §7, V3 framing |
| F2 substrate principle (filesystem + git as canonical state shape) | §5 |
| F4 graduated-isolation principle (sandbox-strength-by-trust-level) | §5 (operator phrasing) |
| F5 cross-deployment secrets bridge principle | §2 (bridging arc), §5 |
| Durable-execution capability requirement (long-running survives-restarts as workload class) | §3 |
| 99.9%+ reliability → deterministic-outer-harness commitment | §4 + protocol §2.3 implication |
| Computer-use-at-production with graduated sandbox tier | §5 |

### 10.2 Persona-constrained

| Decision | Constraint summary | Source |
|---|---|---|
| F3 (durable-execution-as-coordination-spine) | Coarse: workload-class dependent; capability requirement set by long-running subset; detail in §8 | §3, F3 review |
| Routing strategy (D-derivative; synthesis §9 Q14 layered) | Must be cost-aware AND reliability-aware AND capability-aware (coupled; §8.5) | §5, §6, §4 |
| Production-time deployment surface | Option space narrows per §9; no specific surface picked | §5, §4, §2 |
| HITL synchrony | Must be selective (math of tens-concurrent + 99.9%); UX shape open | §4 implication |
| Cost-attribution-per-span | Required as observability primitive (per-class ceiling enforcement) | §6 |
| Multi-process or job-queue topology | Required for durable pole; ephemeral subset can be single-process; both coexist | §3, §4 |
| Compliance-regime extensibility | Architectural posture: preserve regime-extensibility as structural property pending customer-mix binding | §6 |
| Workload-class extensibility | Architectural posture: accommodate task classes not enumerated at design-time; constraint level in §11 | §3 (operator-asserted flag) |

### 10.3 Persona-open (D-derivatives and unbound decisions)

- **F1 sub-aspects:** F1-abstraction-shape (capability-aware vs LCD vs ad-hoc); F1-routing-strategy (declarative / embedding / LLM-as-router specific layering)
- **F2 sub-aspects:** F2-adoption-depth (skills-as-files, prompts-as-files, state-ledger-as-files, artifact-tier layering); F2-git-tier (versioning vs state-ledger vs checkpoint vs combination)
- **F3 sub-aspects:** F3-engine (Temporal, Restate, DBOS, LangGraph checkpointing, custom-on-Postgres, filesystem-journal, etc.); F3-invocation-discipline (manifest declaration, auto-inferred, per-invocation operator choice, per-step annotations)
- **F4 sub-aspects:** F4-tier-set (process / container / microVM composition); F4-tech (Firecracker / gVisor / Kata / Docker / etc.)
- **F5 sub-aspects:** F5-tech-dev (macOS keychain / Linux secret service / Windows Credential Manager / KWallet); F5-tech-prod (Hashicorp Vault / AWS Secrets Manager / Azure Key Vault / Doppler)
- **Tensions:** T1 (filesystem-orchestrator vs framework-orchestration) — leaning framework but not bound; T4 (markdown-spec vs code-driven) — both supported per soft preference; specific composition open
- **Evaluation methodology infrastructure:** judge-human alignment, alignment-floor TPR/TNR/κ telemetry implementation, holdout-set methodology, meta-eval — primitives required; specific tools/methods open

### 10.4 Cross-axis tension clusters flagged for Phase 3 attention

- **Routing-coupled deliberation:** cost × reliability × capability (§8.5).
- **T3 traversal:** bridging arc traverses per-task → per-company deployment-unit tension structurally; computer-use-at-production-with-multi-tenant-isolation compounds.
- **Compliance-readiness as architectural posture:** primitives any plausible regime will demand (hash-chained audit ledger, granular access controls, encryption-at-rest, retention controls, tenant isolation, secrets rotation, comprehensive observability) need to be foundational, not bolt-on. Mirrors workload-class-extensibility posture.

---

## §11 Open items

| # | Item | Source dimension | Closing path |
|---|---|---|---|
| 1 | Shared-vs-siloed harness infrastructure for primary task classes | Dim 2 follow-up | Phase 3a F2 (filesystem-as-substrate) deliberation |
| 2 | Workload-class extensibility constraint level (hard / soft / per-class) | Dim 2 follow-up | Revisit when first non-original workload class surfaces |
| 3 | Long-tail duration of durable pole | Dim 2 follow-up | Capture as workload patterns emerge; affects state-retention and engine option space |
| 4 | Throughput rough order-of-magnitude per day | Dim 3 follow-up | Emerges from operational telemetry once harness is running |
| 5 | Out-of-scope integrations | Dim 4 follow-up | Revisit when specific exclusion surfaces during Phase 3a deliberation |
| 6 | Compliance regime determination | Dim 5 | Bound when initial customer / contractual relationship materializes; revisit before first multi-tenant production deployment |
| 7 | Vendor / IP-handling restrictions at multi-tenant binding | Dim 5 | Alongside compliance regime resolution |
| 8 | Hard latency budget | Dim 5 | Revisit if latency-bound sub-task class surfaces |
| 9 | Future-state operator interaction surface (CLI / IDE / UI / API at team or multi-tenant binding) | Dim 1 follow-up (bridging-arc derivation) | Bound at multi-tenant binding state design |
| 10 | Tenant isolation specifics at multi-tenant binding (data, cost, model access, per-tenant sandbox) | Dim 1 follow-up trigger | Bound when multi-tenant deployment design begins; couples with §6 compliance and §10.4 T3 traversal |
| 11 | Session-state continuity across operators at team / multi-tenant binding state | Dim 1 follow-up (bridging-arc derivation) | Bound at multi-tenant deployment design |
| 12 | Object-storage-tier need for non-text media in content creation workload | §8.2 implication | Revisit when content-creation workload patterns mature; potentially folds into F2-adoption-depth Phase 3a/3b |

---

*End of Persona Document v1. Filed at Phase 2 close. Feeds Phase 3a foundational decision deliberation (F1–F5) by the Slate council per Project Workflow v1.0 §2.3.1.*