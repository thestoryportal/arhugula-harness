<!--
VENUE PROVENANCE — imported 2026-05-29 from Drive folder 1Je_dlorQQEIRp...
References to `s4-c1-orchestration-spec.md` etc. are historical provenance pointers.
In this workspace, voices are addressable at `.claude/skills/council/cN-{name}/SKILL.md`.
Canonical H_T design substrate at `design-substrate/*.md` per CLAUDE.md §2.
-->

# Voice Roster — Slate E11

Compact lookup for the orchestrator's Layer B (question-type templating) and Layer C (scope-keyword scoring). Source: the eleven voice SKILL.md files in this council, §3 (activation triggers) of each.

When you need full per-voice scope, anchored / consulted question types, scope-keyword profiles, or co-primary candidates, read the source voice's SKILL.md at `.claude/skills/council/cN-{name}/SKILL.md`. This roster is the routing-decision summary, not the full voice identity.

---

## Voice-by-voice quick lookup

### C1 — Orchestration & Control (`c1-orchestration`)
- **Anchors:** Architectural (between-turn topology / control flow)
- **Consults:** Tradeoff (control-flow lever), Failure-mode (control plane), Contract (inter-agent), Cross-cutting (topology-touched)
- **Strong-keyword cues:** orchestrator-worker, manager pattern, decentralized handoff, prompt chaining, sectioning, voting, parallelization, evaluator-optimizer (topology), ReAct, sub-agent, topology, control flow, hand-off, fan-out, gather, dispatch (control-flow sense), interrupt, resume, max iterations, async/synchronous, sub-agent boundary, isolated context, return contract
- **Cross-cutting concern owned:** none (consults broadly)
- **Likely co-primaries:** C5 (validation-loop topology), C9 (retry-as-control-flow), C11 (HITL placement), C6 (model-routing-as-topology)
- **H_T axis:** CP

### C2 — Context Engineering (`c2-context-engineering`)
- **Anchors:** Architectural (within-turn prompt structure), Tradeoff (cost-vs-quality of context)
- **Consults:** Failure-mode (context-related), Contract (prompt-structure), Cross-cutting (cost joint, eval consult, observability consult)
- **Strong-keyword cues:** context engineering, attention budget, system prompt, prompt altitude, just-in-time, JIT retrieval, compaction, context window, prompt structure, prompt cache, cache breakpoint, cache_control, cache hit/miss, static prefix, dynamic suffix, working memory, RAG (within-turn), CLAUDE.md (read-into-context), context truncation, sliding window, progressive disclosure (loading aspect), tool_search (the discipline), context rot, lost-in-the-middle, U-shaped attention
- **Cross-cutting concern owned:** joint #3 cost (with C4, C6)
- **Likely co-primaries:** C3 (read/write seam to durable state), C4 (Skills/tools loading discipline), C6 (model tier × cache discipline), C1 (rare — when topology is a context-window choice)
- **H_T axis:** IS

### C3 — State, Memory & Persistence (`c3-state-memory-persistence`)
- **Anchors:** Architectural (across-turn lifecycle), Contract (durability)
- **Consults:** Failure-mode (state-implicating), Cross-cutting (reliability shape, eval state-divergence, cost storage), Tradeoff (durability axis)
- **Strong-keyword cues:** durability, persistence, durable state, recovery, replay, time-travel, restart, crash recovery, fault tolerance, filesystem state, claude-progress.txt, init.sh, git-as-state, audit trail, vector store, KV store, SQLite, BaseCheckpointSaver, checkpoint, snapshot, durability mode, episodic memory, semantic memory, procedural memory, long-term memory, CoALA, atomicity, consistency, ACID, two-phase commit, rollback, savepoint, idempotent write, state ledger, append-only log, WAL, materialized view, garbage collection, eviction policy, retention policy, `clear_tool_uses_20250919` (durable side), state divergence, drift detection
- **Cross-cutting concern owned:** none (consults broadly)
- **Likely co-primaries:** C1 (topology ↔ durability requirement), C5 (rollback boundary on validator fail), C9 (resume-from-checkpoint mechanics)
- **H_T axis:** IS

### C4 — Tools & Integration (`c4-tools-integration`)
- **Anchors:** Contract (integration — input/output schema, idempotency posture), Architectural (action surface in aggregate)
- **Consults:** Failure-mode (tool-related), Tradeoff (cost-vs-capability of action surface), Cross-cutting (cost joint, reliability via idempotency, security via capability-blast-radius, eval via tool metrics)
- **Strong-keyword cues:** tool, tool_use, tool_call, tool definition, tool description, tool schema, tool input, tool output, tool selection, tool namespacing, parallel tool use, `disable_parallel_tool_use`, `tool_choice`, structured output, strict mode, `strict: true`, JSON schema, response schema, server tool, hosted tool, web_search, web_fetch, code_execution, MCP, MCP server, JSON-RPC, stdio transport, MCP primitive (Tools / Resources / Prompts / Roots / Elicitation / Sampling), SKILL.md, frontmatter, progressive disclosure (description-writing aspect), bundled resources, idempotent, idempotency key, exactly-once, at-least-once, action surface, tool sprawl, tool catalog, wrap-as-tool, equip-as-Skill, tool poisoning (contract aspect)
- **Cross-cutting concern owned:** joint #3 cost (with C2, C6)
- **Likely co-primaries:** C2 (loading-budget impact), C5 (tool output gating), C9 (idempotency × retry), C10 (capability surface ↔ trust boundary — canonical Layer-3 tension)
- **H_T axis:** AS

### C5 — Validation Contract (`c5-validation-contract`)
- **Anchors:** Contract (validation gate), Failure-mode (gate failure classification)
- **Consults:** Architectural (Reflexion / evaluator-optimizer co-primary with C1), Tradeoff (judge cost vs catch rate co-primary with C6), Cross-cutting (reliability via fail-class, eval-ability via gate measurement, observability via gate event surface)
- **Strong-keyword cues:** validator, validation, validation contract, gate, deterministic gate, schema validation, output validation, evaluator-optimizer, generator-evaluator, Reflexion, in-loop, retry exit, exit-on-pass, permanent fail, transient fail, fail classification, judge (in-loop), model-based judge, judge-as-validator, sandbox contract, validation sandbox, verbal feedback, reflect-step, reflection prompt, gate contract, pass condition, fail condition, gate event, typecheck, linter, test gate, exit-code mapping, structured output gate, hard fail, soft fail, escalate, gate-fail-recovery
- **Cross-cutting concern owned:** none (consults on reliability, eval, observability)
- **Likely co-primaries:** C1 (Reflexion topology), C4 (tool output gating), C8 (judge calibration vs judge contract), C9 (validator-fail × transient retry), C10 (validation gate × action-safety gate composition), C11 (human-as-validator)
- **H_T axis:** CP

### C6 — Model Strategy & Routing (`c6-model-routing`)
- **Anchors:** Tradeoff (model strategy — signature anchor on cost-vs-quality), Failure-mode (fallback-chain composition), Contract (per-agent-role model-strategy contract)
- **Consults:** Architectural (routing-as-topology co-primary with C1), Cross-cutting (cost joint owner, reliability/observability/eval/security/HITL standing pre-checks)
- **Strong-keyword cues:** model selection, model strategy, model routing, Haiku, Sonnet, Opus, model tier, frontier model, frontier-vs-cheap, capability profile, fallback chain, fallback model, cross-family fallback, local model fallback, extended thinking, thinking budget, prompt caching strategy, semantic cache, embedding cache, Batch API, batch processing, server tool cost, web_search cost, code_execution cost, router agent, routing rule, routing accuracy, cost per task, cascade routing, escalation routing, FrugalGPT, OptiRoute, CARGO, multi-provider, capability shortfall, p50/p95 latency, xhigh thinking
- **Cross-cutting concern owned:** joint #3 cost (with C2, C4)
- **Likely co-primaries:** C1 (routing-as-topology), C2 (cache-discipline × model-tier), C4 (cost on action-surface axis), C5 (judge model selection), C9 (chain composition vs mechanics), C11 (local model fallback)
- **H_T axis:** CP

### C7 — Observability (`c7-observability`)
- **Anchors:** Contract (span schema / attribute set / sampling / redaction / cost-attribution schema), Cross-cutting #2 (observability hooks — sole owner), Architectural (when the architecture *is* the trace topology)
- **Consults:** Failure-mode (forensic legibility), Tradeoff (instrumentation vs cost; head-vs-tail sampling), Cross-cutting #3 (cost-attribution-per-span co-primary with C2/C4/C6)
- **Strong-keyword cues:** OTel, OpenTelemetry, span, trace, attribute, GenAI semconv, instrumentation, tracing, trace propagation, exporter, collector, OTLP, sampling, head-based sampling, tail-based sampling, redaction, cost attribution per span, trace dashboard, runtime introspection, post-mortem trace, distributed tracing
- **Cross-cutting concern owned:** #2 observability hooks (sole)
- **Likely co-primaries:** the voice that owns the events under discussion (e.g., C9 on breaker-trip events, C5 on gate events, C10 on audit-trail events)
- **H_T axis:** OD

### C8 — Eval Engineer (`c8-eval-engineer`)
- **Anchors:** Contract (eval contract — holdout, regression set, judge-human alignment, drift), Cross-cutting #5 (eval-ability — sole owner)
- **Consults:** Failure-mode (regression / drift over time), Tradeoff (eval-cost vs eval-coverage; judge-cost vs judge-quality), Contract (standing pre-check on what's measurable about a contract being designed)
- **Strong-keyword cues:** eval, eval set, eval contract, holdout, holdout-corpus, regression set, regression test, judge-human alignment, judge calibration, judge drift, alignment floor, alignment cadence, drift detection, drift score, drift window, manual review, categorize, automate, align loop, end-state evaluation, counterfactual baseline, Cohen's kappa, percent agreement, Spearman rank correlation, F1 on human labels, gate catch-rate, Reflexion-loop convergence, routing accuracy, cost-adjusted accuracy, semantic-cache false-positive rate, leakage prevention, train/test split, freshness rule, meta-eval, eval-of-eval, eval-of-skill, phase-2 skill eval
- **Cross-cutting concern owned:** #5 eval-ability (sole)
- **Likely co-primaries:** C5 (judge-as-validator vs judge-as-eval-tool), C6 (routing-accuracy eval; judge model selection joint with cost), C7 (eval-substrate completeness; reverse pre-check), C9 (graceful-degradation eval), C10 (eval-grade redaction; eval-data trust boundary), C11 (HITL-as-eval-rater for alignment runs)
- **H_T axis:** OD

### C9 — Reliability & Recovery (`c9-reliability-recovery`)
- **Anchors:** Failure-mode (default cluster anchor)
- **Consults:** Contract (reliability semantics — idempotency, retry-exit, fallback, durability), Tradeoff (depth vs cost, retry-aggression vs latency, breaker sensitivity), Cross-cutting (security via gating semantics, cost via retry storms / fallback depth, eval via graceful-degradation, HITL via local-rate-limit-storm prevention)
- **Strong-keyword cues:** retry, backoff, exponential backoff, jittered, full jitter, retry budget, retry attempt, retry storm, thundering herd, transient failure, retry policy, retry posture, retryable, replayable, timeout, per-attempt timeout, total budget, deadline, time budget, latency budget, idempotency key (mechanism side), dedupe, dedupe window, content hash, exactly-once, at-least-once (mechanism side), circuit breaker, breaker, breaker trip, breaker threshold, breaker open, breaker half-open, breaker reset, fallback trigger, fallback timing, capability-shortfall trigger, chain advancement, terminal step, retry-budget-exhausted, graceful degradation, degraded mode, degradation trigger, degradation scope, staggered rollout (degradation), reduced-capability operation, rate-limit storm, self-induced rate-limit, parallel-call coordination, retry coordinator, Retry-After header, X-RateLimit-Reset
- **Cross-cutting concern owned:** #4 reliability & failure containment (sole)
- **Likely co-primaries:** C1 (retry-as-topology — Layer-3 tension), C3 (rollback primitive × retry policy), C5 (validator-fail-class × mechanics), C6 (chain composition vs mechanics), C10 (breaker-trip carries gating semantics), C11 (local rate-limit-storm prevention)
- **H_T axis:** CP

### C10 — Action Safety & Blast Radius (`c10-action-safety-blast-radius`)
- **Anchors:** Cross-cutting #1 (security & blast radius — sole owner), Contract (gate / permission / trust-boundary contract), Failure-mode (blast-radius outlier / trust-boundary breach — promotes from default-consultant to co-primary on these)
- **Consults:** Tradeoff (security implications), Architectural (topology touches trust boundaries), Cross-cutting (audit-trail co-primary with C7; HITL escalation surface co-primary with C11)
- **Strong-keyword cues:** trust boundary, blast radius, gate, gate policy, gate level, allow / ask / deny, deny-wins, write-path gate, action gate, action-safety gate, permission, permission pipeline, authorization, audit trail, audit log, audit integrity, tamper-evident, append-only, MCP signing, MCP pinning, MCP attestation, MCP allowlist, MCP supply chain, tool poisoning (trust posture), rug pull (trust posture), cross-tool poisoning, sandbox isolation, sandbox enforcement, UID isolation, network policy, secrets at rest, secrets in prompts, secrets in traces, redaction, cross-deployment trust, eval-grade redaction, content capture posture, trust gradient, model-tier safety, cross-family safety, local-model trust posture, untrusted-output, breaker-trip subscription, gating signal, capability-vs-gating, blast-radius classification, read-only / write-bounded / write-unbounded, escalation trigger, prompt injection, indirect prompt injection
- **Cross-cutting concern owned:** #1 security & blast radius (sole)
- **Likely co-primaries:** C4 (capability surface vs gating — canonical permanent tension), C5 (validation-sandbox isolation), C7 (audit-trail trust boundary), C9 (breaker-trip-as-gating-signal), C11 (HITL-as-escalation-surface; secrets local subscope; audit-ledger storage; cross-deployment trust UX)
- **H_T axis:** AS

### C11 — Operator Loop & Local Deployment (`c11-operator-loop-local-deployment`)
- **Anchors:** Cross-cutting #6 (HITL & local-first — sole owner), Failure-mode (operator-touchpoint subtype — anchor when the failing surface is the operator's interface)
- **Consults:** Architectural (HITL placement co-primary with C1), Contract (when contract is harness↔operator), Tradeoff (operator-burden vs autonomy), Cross-cutting (concerns #1/#4/#5 composed with operator surfaces)
- **Strong-keyword cues:** HITL, human-in-the-loop, approval queue, approve/edit/reject/respond, interrupt, resume, checkpointer, operator approval, operator review, operator confirmation, gate-on-every-call, ask response, escalation trigger, approval fatigue, gate fatigue, mandatory HITL, optional HITL, opt-in approval, operator UI, operator prompt, rubric prompt, side-by-side display, terminal banner, status indicator, escalation surface, operator response, verbatim retention, redacted retention, local-first, single-process, single-developer, local deployment, single-machine, developer hardware, OS keychain, secrets at rest (local), env-var fallback, .env file, git-ignored, rotation event, secret-rotation command, sqlite schema (local), sqlite-backed, parquet, in-memory ring buffer, OTLP collector (local), otelcol-contrib, in-process collector, BatchSpanProcessor, durable execution alternatives, checkpointing-to-disk, local Ollama, Ollama, vLLM, llama.cpp, LM Studio, local inference engine, local model fallback, local-terminal step, local-terminal active, capability-floor-reached, untrusted-output (when source is local model), zero-platform-safeguards, restart-survival, persist across restart, in-flight state, fresh-on-restart, durability tier (local), integrity verification on startup, ledger restore on restart, queue persistence, corruption response
- **Cross-cutting concern owned:** #6 HITL & local-first deployment (sole)
- **Likely co-primaries:** C5 (HITL-as-validator), C8 (HITL-as-eval-rater), C10 (escalation surfaces, secrets local, audit-ledger storage, local-terminal trust posture), C9 (local reliability mechanisms), C7 (local trace storage UX), C6 (local model fallback), C3 (Tier-5 sqlite-schema specifics)
- **H_T axis:** OD

---

## Cross-cutting concern ownership map

| # | Concern | Owner | Sole or joint |
|---|---|---|---|
| 1 | Security & blast radius | C10 | Sole |
| 2 | Observability hooks | C7 | Sole |
| 3 | Token economy & cost | C2 + C4 + C6 | Joint (no single owner) |
| 4 | Reliability & failure containment | C9 | Sole |
| 5 | Eval-ability | C8 | Sole |
| 6 | HITL & local-first deployment | C11 | Sole |

For joint #3 (cost): when the topic touches cost, all three of C2/C4/C6 are convening candidates. The orchestrator picks based on which cost driver is dominant (prompt structure → C2; action surface → C4; model tier/config → C6); when the dominant driver is genuinely shared, two of the three co-primary.

---

## Layer-3 permanent tensions

These tensions never resolve at runtime. The orchestrator surfaces them when convened voices touch the contested seam:

- **C4 ↔ C10** — capability vs gating — canonical permanent tension. Two-axis tunable parameter `per_tool_gate_level × per_mcp_server_trust_tier`. H_T resolution: C-AS-10 §10.3 4-tier blast radius + CP §19.1.1 4-axis floor composition.
- **C2 ↔ C3** — within-turn vs across-turn (the read/write seam between active context and durable state). H_T resolution: IS spec read/write boundaries between active context and state ledger.
- **C1 ↔ C9** — control-flow vs reliability. Tunable parameter `topology_fault_handling`. H_T resolution: CP §22 ResumptionKind taxonomy + `engine.replay_disposition`.

Permanent boundaries (NOT Layer-3 — clean seams that don't contend, just compose):

- C5 ↔ C8 (in-loop deterministic vs out-of-loop statistical)
- C7 ↔ C8 (runtime substrate vs eval methodology)
- C2 ↔ C4 (loading discipline vs contract surface)
- C6 ↔ C9 (chain composition vs mechanics)
- C3 ↔ C9 (rollback primitive vs retry policy)
