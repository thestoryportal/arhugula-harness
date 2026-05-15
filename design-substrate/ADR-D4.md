# ADR-D4: Multi-agent topology — six-pattern taxonomy with topology + fan-out cap + cascade-policy + writer-serialization parametric on workload-class × D1-engine-class

## Status

Accepted
Date: 2026-05-10
Phase: 3b Stage 1 (per `Project_Workflow_v1_1.md` §2.3.3)
Promotion path: Accepted at P3-CK clearance per Workflow v1.1 §3.1
Revision: v1 → v1.1 (P3c-CK iter-1 close mechanical revision per Path A — F2-14 Reading 1 resolution; `parent_fanout_close_entry` clarified as separate ledger primitive joining F2 via `action_id` reference)
Revision date: 2026-05-10
Promotion: P3c-CK final clearance — 2026-05-11

## Change-note (v1 → v1.1)

**Scope.** Mechanical revision pass per `Project_Workflow_v1_2.md` §3.1 (Path A LLM-assisted, single-finding) clearing `Adversarial_Review_3c.md` F2-14 (D4 §1.10 `parent_fanout_close_entry` shape relationship to F2 state-ledger entry shape ambiguous). Authored under `spec-writer` skill per Phase 3c-CK iteration 1 close handoff §5.1 Path A skill mapping.

**F2-14 disposition.** Operator selected **Reading 1 (separate ledger primitive)** at session entry per `Phase_3c_CK_Iter_2_Pre_Entry_Handoff_D4_Revision_Pass.md` §2.2 elicitation via `ask_user_input_v0`. Under Reading 1, `parent_fanout_close_entry` is a SEPARATE ledger primitive joining F2 state-ledger via `action_id` reference; it is NOT an F2 state-ledger entry. The missing F2 fields (`idempotency_key`, `actor`, `response_hash`) are intentional, not under-specification:

- `idempotency_key` is per-action; the fanout-close primitive is per-topology, not per-action.
- `actor` for a fanout-close is structurally the orchestrator agent; redundant with the topology-binding semantics.
- `response_hash` does not apply to a fanout-close (no single "response" exists at fanout aggregate level); the response is the merkle-root over siblings, carried in the fanout-specific field `sibling_ledger_root`.

**T-perm-2 impact.** None. T-perm-2 F2-layer resolution stands; no D4-layer note added to the permanent-tension ledger. Reading 1 preserves F2 as a single-write-contract primitive — F2 entries continue to honor the locked six-field shape `(action_id, idempotency_key, actor, response_hash, timestamp, prior_event_hash)` without polymorphic variation; the fanout-close primitive sits beside F2 and joins via `action_id`.

**Operator-decision rationale (captured).** The `parent_fanout_close_entry`'s semantics (topology-bound, multi-sibling aggregation, merkle-root construction) differ substantively from F2's per-action entry semantics. Treating it as a separate primitive that joins F2 via `action_id` reference is architecturally cleaner than forcing it into F2's six-field shape with semantic stretching (e.g., aliasing `response_hash` to `sibling_ledger_root` would have read as terminological compromise). Reading 1 also keeps the F2 substrate composable downstream without introducing per-entry-type dispatch logic at every F2-reading callsite.

**Changes inline.**

- Status block — Revision + Revision date lines added.
- This Change-note section — new, between Status and Context.
- §1.10 — clarifying paragraph and per-field rationale added after the `parent_fanout_close_entry` shape declaration, declaring it as a SEPARATE ledger primitive joining F2 state-ledger via `action_id` reference; merkle-root construction's read-side semantics over F2 entries made explicit; per-persona-tier cryptographic shape table headers annotated to distinguish F2 substrate from separate primitive.
- §Rationale (d) "With F2 (state-ledger entry shape)" sub-bullet — revised to make explicit that only per-sibling tool-call ledger entries are F2 entries; `parent_fanout_close_entry` is named as separate primitive joining via `action_id`; T-perm-2 F2-layer resolution explicitly stands.
- §References "Workflow and skill discipline references" — extended with six v1.1-related entries (Workflow v1.2 §3.1, Workflow v1.2 §4.1.2, spec-writer skill activation, Adversarial_Review_3c.md F2-14, Phase 3c-CK iteration 1 close handoff §4.1 D4 row, Phase 3c-CK iter-2 pre-entry handoff §2 operator decision record).
- Closing footer — revised to v1 → v1.1 history with revision scope and Status posture preservation noted.

**Sections preserved verbatim.** §Context; §Decision intro paragraph; §1.1 through §1.9; §1.11; §Rationale (a) Pattern this decision follows; §Rationale (b) Workload-constraint application; §Rationale (c) T-perm-3 D4-layer stance; §Rationale (d) cross-axis composition sub-bullets for D1 substrate / D5 substrate / F3 capability-floor / F1 chain-advancement / D2 forward-reference / D3 forward-reference / D6 forward-reference (only the "With F2" sub-bullet is revised); §Consequences (a)–(k); §Alternatives Alt-1 through Alt-8; §References Shape 1 through Shape 5; §References Substrate research citations; §References Convening artifact citations.

**F2-14 NOT-addressed deferrals.** None. F2-14 cleared at v1.1 mechanical revision pass under Reading 1 disposition.

**Status posture.** `Status: Proposed` preserved per `Project_Workflow_v1_2.md` §3.1. Promotion to `Accepted` blocked until P3c-CK iter-2 clearance.

## Context

This ADR closes the workload-dependent multi-agent-topology deferral declared at `Pattern Reference Catalog v1.0 §11.3.2 D4` (lines 3139–3148) and at `Cluster 5 V2 §3 D4` line 206 ("workload-dependent: single-threaded-writes is a strong default; parallel sub-agents only for read-heavy/exploration workloads"). F3 v1.1 (Status: Accepted post Step D) committed the harness to the stateless-reducer / launch-pause-resume durable-execution pattern (Pattern Reference Catalog v1.0 §10.1 P-CP-8) with a non-negotiable capability-requirement floor including (iv) observable lifecycle exposing workflow-start, step-boundary, fallback-trigger, retry-attempt, breaker-trip, lease-acquired/released, and resumption events. `ADR-D1.md` v1 (Status: Proposed, 2026-05-10) specialized F3 by committing a five-element engine-class taxonomy (event-sourced-replay / save-point-checkpoint / pure-pattern-no-engine / reconciler-loop / WAL-segment) with per-deployment-surface candidate mapping; D1 §1.3 encoded the `topology_fault_handling ∈ {ABOVE_ENGINE, BELOW_ENGINE, RECONCILER}` tunable parameter as the D1-layer T-perm-3 resolution. `ADR-D5.md` v1 (Status: Proposed, 2026-05-10) committed a four-component HITL synchrony specification including §1.3 three-placement HITL topology primitive (`pre-action` / `sub-agent-boundary` / `validator-escalation`); D5 §1.3.1 declared `cascade_policy ∈ {pause, proceed, cascade-cancel}` on the topology primitive interface signature with §1.6 final paragraph deferring cascade semantics to T-perm-3 D1-layer resolution without D5-layer revision. D4 specializes F3, D1, and D5 by traversing the topology-pattern candidate space competitively across the workload-class axis and committing topology pattern + sub-agent fan-out cap + cascade-policy default + writer-serialization stance parametric on workload-class × D1-engine-class.

The deliberation surface at D4 is the topology-pattern taxonomy across the candidate space, not a single-pattern pick. Cluster 1 §1 [HIGH] establishes the canonical Cognition-Anthropic adjudication: "parallelize read/research; serialize writes" — Cognition's "Don't Build Multi-Agents" (Walden Yan, June 2025) names the digital-gossiping failure mode at parallel writers; Anthropic's research system (Schluntz et al., June 2025) production-witnesses 3–5 sub-agents per fan-out for breadth-search workloads with ~15× chat-token budget. Cluster 1 §3 [HIGH] establishes cross-framework pattern equivalences: OpenAI manager pattern ≡ Anthropic orchestrator-workers ≡ revfactory/harness Supervisor; OpenAI decentralized ≡ Microsoft handoff. Cluster 1 §6 [HIGH] establishes the SFA (single-file-agent) ceiling at one tool family + ≤10 compute loops with sub-agent-as-tool as the natural escalation per smolagents `managed_agents` and OpenAI Agents SDK `agent.as_tool()`. Cluster 1 §7 [HIGH] documents parallelism-pattern primitives — concurrency caps; prompt-caching interaction with parallel fan-out (cache-warm-up requirement); self-consistency saturation curves; merger-bottleneck pattern. Cluster 4 §2.4.4 [HIGH] documents sub-agent HITL composition failure modes (sub-agent interrupt stranding; cascade-timeout composition with parallel sibling sub-agents) that D4's cascade-policy commitment must mitigate. Cluster 4 §2.2.7 [HIGH] establishes per-`{provider, model}` circuit breakers and Stripe-style idempotency-key construction `sha256(conversation_id || step_index || tool || canonical_args)` as harness-owned reliability primitives composing per-sub-agent at fan-out.

`Persona_Document_v1` §3.1 enumerates four primary workload classes as first-class — software engineering (§3.1.1), content creation (§3.1.2), pipeline automation (§3.1.3), research (§3.1.4); §3.2 records workload-class extensibility flag preserving topology-above-engine viability; §3.3 records work-unit shape distribution as heterogeneous; §4 sets the 99.9%+ completion SLO at tens-concurrent scale; §6 records per-workload-class cost ceiling; §7 records "Anthropic primitives where they fit" as soft preference with vendor-neutral abstraction otherwise; §8.1 names software engineering "[HIGH] Multi-step session shape dominant; evaluator-optimizer / Reflexion-style validation loops natural fit. [MODERATE] Parallel multi-agent reads (review, eval) acceptable; writes single-threaded per Cognition strong-convergence"; §8.2 names content creation "[MODERATE] Multi-step session shape typical; lower parallelism need than software-eng"; §8.3 names pipeline automation "[HIGH] F3 durable-execution-spine territory par excellence; multi-stage workflows with explicit step boundaries"; §8.4 names research as mixed F3 with breadth-search canonical at Anthropic-pattern; §10.4 names compliance-readiness foundational primitives that compose against multi-agent span hierarchy and per-sibling audit-ledger discipline; §11.4 records throughput rough order-of-magnitude per day as open at design-time and contributing to fan-out-cap calibration deferral.

Three permanent tensions interact with D4. **T-perm-3 (C1 ↔ C9 — control-flow vs reliability)** is the **direct engagement at D4** — multi-agent topology is exactly the C1-control-flow (topology declaration drives cascade behavior; sub-agent fan-out cap; parallel-branch coordination) vs C9-reliability (cascade-timeout enforcement; sub-agent error propagation; per-sibling breaker placement; rate-limit-storm prevention) axis. The `cascade_policy` parameter inherited from D5 §1.3.1 is one resolution surface; per-pattern fault-handling-responsibility (orchestrator-workers: lead handles; decentralized-handoff: target handles; hierarchical-delegation: parent handles) is another. **T-perm-1 (C4 ↔ C10 — capability vs gating)** surfaces at the sub-agent privilege seam (sub-agent inherits parent's tool registry per C4 contract; sub-agent cannot escalate gate level per C10 contract; sub-agent privilege downgrade is a D4-layer commitment); D5-layer resolution shape `per_tool_gate_level × per_mcp_server_trust_tier × persona_tier × blast_radius_tier` stands. **T-perm-2 (C2 ↔ C3 — within-vs-across-turn)** surfaces at the HandoffContext serialization seam (HandoffContext assembly is within-turn; sub-agent dispatch is across-turn); F2-layer resolution stands per F3 v1.1 §References explicit framing.

ADR-F1 (Status: Proposed) composes against D4 at the chain-advancement seam — F1 §"Permanent tensions engaged" accepted T-perm-3 with per-layer time-budget shape as F1-layer resolution; D4 specializes the parametric mapping with two new dimensions (workload_class × topology_pattern) per §1.6 below. ADR-F2 (Status: Proposed) composes against D4 at the per-sub-agent state-isolation seam — F2 state-ledger entry shape `(action_id, idempotency_key, actor, response_hash, timestamp, prior_event_hash)` is the substrate per-sibling state-ledger entries write to without revision.

## Decision

Commit at the D4 layer to a **six-component multi-agent topology specification**:

1. **Six-pattern topology taxonomy** (single-threaded linear / orchestrator-workers / decentralized-handoff / hierarchical-delegation / evaluator-optimizer / parallelization) as the harness-canonical pattern enumeration (§1.1).
2. **Per-workload-class topology commitment** (4 rows: workload class → primary topology pattern + sub-agent fan-out cap + cascade-policy default + writer-serialization stance) (§1.2).
3. **Per-engine-class implementation mechanism overlay** (5 rows: engine class → cascade-enforcement mechanism + writer-serialization mechanism + per-sibling lease coordination + T-perm-3 reading) (§1.3).
4. **2D matrix (workload-class × D1-engine-class)** committing T-perm-3 reading per cell (§1.4).
5. **Sub-agent privilege inheritance contract** with default-downgrade rule per blast-radius tier (§1.5).
6. **T-perm-3 D4-layer multiplicative tunable parameter specialization** with `workload_class × topology_pattern` axes added to the D1-layer locked tunable (§1.6).

Topology pattern is committed at D4 per cell; specific candidate-within-pattern (e.g., LangGraph Supervisor vs Anthropic-research-system vs deer-flow vs revfactory/harness Supervisor for orchestrator-workers) is deferred to workload-binding-time downstream of Phase 3 per §1.11 contract.

### 1.1 Six-pattern topology taxonomy

| # | Pattern class | Lifecycle ownership | Primary candidates from §11.3.2 D4 + Cluster 1 |
|---|---|---|---|
| 1 | **single-threaded linear** | Sole agent owns full lifecycle | humanlayer/12-factor-agents Factor 10 (small focused agents; reliability ceiling 3–10 steps); Cognition-canonical for write-heavy work |
| 2 | **orchestrator-workers** | Lead decomposes; workers execute concurrently; lead synthesizes | Anthropic research system (3–5 subagents per fan-out [HIGH]); OpenAI manager pattern; revfactory/harness Supervisor; bytedance/deer-flow (concurrency cap = 3); langchain-ai/deepagents SubAgentMiddleware |
| 3 | **decentralized handoff** | Each agent owns until handoff; recipient owns post-handoff | OpenAI decentralized; Microsoft handoff; shareAI-lab/Kode-Agent multi-agent room; mvschwarz/openrig RigSpec multi-process |
| 4 | **hierarchical delegation** | Parent owns until delegation; child owns sub-task; recursion permitted | revfactory/harness Hierarchical Delegation; ruvnet/ruflo hive-mind queen-led; Cognition manager-Devin spawning child-Devins follow-up |
| 5 | **evaluator-optimizer / producer-reviewer** | Generator + evaluator(s) in loop until convergence | Anthropic Building Effective Agents (evaluator-optimizer); revfactory/harness Producer-Reviewer; langchain-ai/deepagents HITL approval gates with evaluator role; disler/the-verifier-agent two-agent observer |
| 6 | **parallelization (sectioning + voting)** | Independent agents on independent sub-tasks; aggregator merges | Anthropic Building Effective Agents (parallelization); disler/infinite-agentic-loop wave-based generation; oh-my-openagent role-temperament parallel |

The pattern taxonomy at the topology layer is closed at D4; pattern extensibility (new pattern class added) is a Workflow §4.1.2 Class-2 D4 revision.

### 1.2 Per-workload-class topology commitment

Per-workload-class commitment carries the dominant signal from Persona §8.1–§8.4 and Cluster 1 §1 [HIGH] adjudication "parallelize read/research; serialize writes":

| Workload class | Primary topology pattern | Sub-agent fan-out cap | Cascade-policy default | Writer-serialization stance |
|---|---|---|---|---|
| **software-engineering** (§3.1.1, §8.1) | evaluator-optimizer (writes); orchestrator-workers (reads/review/eval) | writes: 1 generator + 1–3 evaluators; reads: 3 max | writes: `pause` (HITL escalation per D5 §1.3 validator-escalation); reads: `proceed` | **strict** — single-threaded writer per Cognition strong-convergence; merge through generator only |
| **content-creation** (§3.1.2, §8.2) | evaluator-optimizer (operator-as-reviewer dominant at design-time) | 1 generator + 1–2 evaluators | `pause` | **strict** — single-threaded author |
| **pipeline-automation** (§3.1.3, §8.3) | sequential default; orchestrator-workers for idempotent parallel stages only | 3 max (deer-flow witness) | `cascade-cancel` | **strict** — sequential durable spine; parallel only on idempotent stages |
| **research** (§3.1.4, §8.4) | orchestrator-workers (Anthropic research system canonical) | 3–5 (Anthropic [HIGH]) | `proceed` (lossy synthesis acceptable) | **relaxed** — parallel breadth-search; lead synthesizes |

Hierarchical-delegation and decentralized-handoff are admissible non-primary patterns:

```
hierarchical-delegation : admissible at software-engineering and research workloads
                          when scope-bounded recursion is justified
                          (Cognition manager-Devin pattern); fan-out cap 3 per parent;
                          cascade-policy inherits parent cell
decentralized-handoff   : admissible at pipeline-automation per-stage-expert workflows
                          (mvschwarz/openrig RigSpec); cascade-policy `cascade-cancel`;
                          single-owner-at-a-time invariant
parallelization (s+v)   : admissible at research breadth-search and content-creation
                          A/B-variant generation; cap 3–5; voting aggregator at synthesis
```

### 1.3 Per-engine-class implementation mechanism overlay

Per-engine-class commitment carries the implementation-mechanism dimension from D1 §1.1 taxonomy:

| D1 engine class | Cascade-enforcement mechanism | Writer-serialization mechanism | Per-sibling lease coordination | T-perm-3 reading |
|---|---|---|---|---|
| **event-sourced-replay** (Temporal-class) | Engine-native: workflow timeout + child-workflow cancellation API | Engine-native task-queue partitioning by `thread_id`; activity-level mutex via Temporal placement primitive | Engine-native lease (Temporal placement; DBOS transaction boundary) | **`BELOW_ENGINE`** — engine owns lifecycle; harness authors topology atop |
| **save-point-checkpoint** (LangGraph-class) | Application-level: harness-owned cascade timeout + node cancellation | Application-level: parent node's `interrupt_before_writers` checkpoint barrier | Application-level (Redis lease, DB unique constraint, worktree isolation per F2) | **`ABOVE_ENGINE`** — harness owns topology and durability composition |
| **pure-pattern-no-engine** (12-Factor methodology) | Harness-owned: filesystem-journal + state-ledger cascade marker | Harness-owned: F2 state-ledger entry serialization on writer slot | Harness-owned (worktree isolation per F2 [HIGH]; DB unique constraint) | **`ABOVE_ENGINE`** — harness owns full durability contract |
| **reconciler-loop** (K8s CRD; humanlayer/agentcontrolplane) | Reconciler-native: CRD status reconciliation + child-CRD cancellation events | etcd compare-and-swap on writer-CRD spec | etcd compare-and-swap | **`RECONCILER`** — control-loop owns reconvergence |
| **WAL-segment** (shareAI-lab/Kode-Agent reference) | Per-segment harness-owned: cascade-marker segment + segment-resume on restart | Harness-owned: per-segment writer-slot lease | Harness-owned per-segment lease | **`ABOVE_ENGINE`** — harness owns WAL + topology |

### 1.4 2D matrix: workload-class × D1-engine-class

The matrix below renders per-cell T-perm-3 reading + cell-specific implementation note. Topology pattern, fan-out cap, and writer-serialization are dominantly workload-driven per §1.2 and constant across engine-class within a workload row; cascade-enforcement mechanism varies per §1.3.

| workload \ engine-class | event-sourced-replay | save-point-checkpoint | pure-pattern-no-engine | reconciler-loop | WAL-segment |
|---|---|---|---|---|---|
| **software-engineering** | `BELOW_ENGINE`; engine cancellation API; activity-level write-mutex | `ABOVE_ENGINE`; harness cascade timeout; checkpoint barrier on writes | `ABOVE_ENGINE`; F2-ledger writer-slot serialization | `RECONCILER`; CRD reconciliation; rare for SE | `ABOVE_ENGINE`; segment-resume EO loop |
| **content-creation** | `BELOW_ENGINE`; engine timeout; rare at this surface | `ABOVE_ENGINE`; harness-owned EO loop | `ABOVE_ENGINE`; filesystem-journal default | `RECONCILER`; rare | `ABOVE_ENGINE`; segment-resume |
| **pipeline-automation** | `BELOW_ENGINE`; engine-native fail-fast; idempotency-key engine-bound | `ABOVE_ENGINE`; **composition-discipline required** per D1 §1.2 self-hosted-server row | `ABOVE_ENGINE`; **excluded for durable pole at scale** per D1 §1.2 | `RECONCILER`; ACP CRD-native; HD acceptable | `ABOVE_ENGINE`; per-segment fail-fast |
| **research** | `BELOW_ENGINE`; engine `wait_condition` natural fit for breadth-search | `ABOVE_ENGINE`; harness OW with checkpoint at synthesis barrier | `ABOVE_ENGINE`; lightweight; well-suited for solo-developer × research | `RECONCILER`; rare | `ABOVE_ENGINE`; per-segment OW |

Cells reading "rare" or "excluded" inherit D1 §1.2 candidate-set exclusions; D4 does not introduce new exclusions.

### 1.5 Sub-agent privilege inheritance contract

Sub-agent privilege at fan-out is governed by a default-downgrade rule that composes with D5 §1.5.1 multiplicative gate-level rule:

```
sub_agent_tool_registry(parent_registry, blast_radius) =
    {
        read-only           : INHERIT (sub-agent receives parent's read-only tools as-is)
        local-mutation      : INHERIT (sub-agent receives parent's local-mutation tools as-is)
        external-reversible : DOWNGRADE_TO_ASK (parent's `auto` becomes `ask` at sub-agent;
                                                operator approves per-sub-agent at gate)
        external-irreversible: REMOVE (sub-agent registry omits the tool;
                                       parent must invoke directly post-synthesis)
    }

sub_agent_gate_level(tool, mcp_server, persona_tier, parent_gate_level) =
    max(
        parent_gate_level,                        // monotonic ascending per D5 §1.5.2
        per_tool_gate_level,                      // C4 contract per D5 §1.5
        blast_radius_floor(tool),                 // C10 four-tier taxonomy per D5 §1.5
        per_mcp_server_trust_floor(mcp_server),   // C10 five-tier framework per D5 §1.5
        persona_tier_floor                        // D5 §1.5
    )
```

**Rationale.** Principle-of-least-privilege at the topology layer. Breadth-search sub-agents (per Anthropic research system, Cluster 1 §[HIGH]) operate with read-only tools by design; downgrading external-reversible to `ask` and removing external-irreversible forces parent-mediated execution where the parent owns the higher-trust authority.

**Override.** At cells where the topology pattern is hierarchical-delegation with explicit operator declaration that child agents own external-reversible authority (e.g., manager-Devin-spawning-child-Devin where child writes), the sub-agent registry inherits external-reversible at parent's gate level. The override is per-sub-agent-class declaration at workload-binding-time and must be recorded in the audit ledger per D5 §1.4 cryptographic shape.

### 1.6 T-perm-3 D4-layer resolution — multiplicative tunable parameter specialization

T-perm-3 is promoted to Layer 3 with D4-layer resolution shape encoded as the tunable parameter

```
topology_fault_handling × workload_class × topology_pattern
```

per spec-writer s3 §6.3. This specializes the D1-layer locked tunable `topology_fault_handling ∈ {ABOVE_ENGINE, BELOW_ENGINE, RECONCILER}` by adding two D4-introduced dimensions:

```
topology_fault_handling : {ABOVE_ENGINE, BELOW_ENGINE, RECONCILER}     (D1-layer, inherited)
workload_class          : {software-engineering, content-creation,
                           pipeline-automation, research}              (D4-layer, new axis)
topology_pattern        : {single-threaded, orchestrator-workers,
                           decentralized-handoff, hierarchical-delegation,
                           evaluator-optimizer, parallelization}       (D4-layer, new axis)
```

The §1.4 2D matrix operationalizes the specialization. Per-cell `cascade_policy` default + writer-serialization stance + fan-out cap + topology pattern jointly resolve the tension within each cell. Compositional layering along the chain-advancement seam:

```
F1-layer resolution         per-layer time-budget shape (ADR-F1 §Decision)
       +
D1-layer resolution         topology_fault_handling per deployment surface (ADR-D1 §1.3)
       +
D4-layer resolution         topology_fault_handling × workload_class × topology_pattern
                            (this ADR §1.4)
       =
Concrete fault-handling     resolved at deployment-surface-time × workload-binding-time;
binding                     per-cell cascade-enforcement mechanism per §1.3
```

The tension is **structural to the slate** per `references/output-templates.md` Layer-3 list and is not collapsed at any layer. C1's `ABOVE_ENGINE` reading is correct at save-point and pure-pattern engine classes; C9's `BELOW_ENGINE` reading is correct at event-sourced-replay class; C9's `RECONCILER` reading is correct at K8s-resident reconciler-loop class. Each reading earns its keep at the workload × engine-class cells where it dominates.

### 1.7 HandoffContext serialization contract

Per Cluster 4 §2.4.3 [HIGH] HandoffContext shape, sub-agent dispatch surrenders within-turn parent context to across-turn durable handoff with the following payload:

```
HandoffContext {
    proposed_action       : ProposedAction       // sub-agent's task scope statement
    agent_confidence      : Float                // optional; lead's prior estimate
    failed_attempts       : List<FailedAttempt>  // prior sub-agent failures on
                                                 //   the same task (cascade reattempt)
    alternatives_considered: List<Alternative>   // lead's deliberation context
    state_summary         : StateSummary         // F2 state-ledger entries relevant
                                                 //   to sub-agent's scope
    audit_trail_link      : LedgerEntryRef       // pointer to parent's audit ledger entry
    retry_history         : RetryHistory         // C9 retry primitives state
}
```

**Brief object structure for orchestrator-workers cells per Anthropic research system [HIGH]:**

```
SubAgentBrief {
    objective       : String                      // single sentence; bounded scope
    output_format   : OutputSchema                // sub-agent's required output shape
    guidance        : String                      // approach hints; non-prescriptive
    task_boundaries : ClearTaskBoundaries         // explicit scope-limit declaration;
                                                  //   prevents sub-agent scope-creep
}
```

The brief object is authored by the lead agent and embedded in HandoffContext.proposed_action at orchestrator-workers cells. Brief authoring per Anthropic research system [HIGH] is itself an inference cost the lead agent absorbs; D3 (Anthropic-primitive adoption depth) will commit lead-agent model binding (Sonnet or Opus) per workload class.

**T-perm-2 adjacency.** HandoffContext assembly is within-turn (C2 stake); HandoffContext serialization at sub-agent dispatch is across-turn (C3 stake). F2-layer resolution stands; HandoffContext crosses the seam without revising T-perm-2 D5-layer or F2-layer commitments.

### 1.8 Concurrent-prompt-cache warm-up protocol

Per Cluster 1 §[HIGH], parallel sub-agent dispatch with cold prompt caches produces a cache-miss storm at the `cache_control` breakpoint. The harness MUST serialize warm-up at fan-out:

```
on_fanout_dispatch(siblings: List<SubAgent>, cache_breakpoint_id: String):
    1. lead_agent.persist_plan_to_filesystem(plan)        # CoALA episodic memory residence
                                                          # per Anthropic research system [HIGH]
    2. dispatch siblings[0] synchronously                  # cache-write at breakpoint
    3. await siblings[0].cache_acknowledgement OR
       await siblings[0].first_token_emission             # cache write completion proxy
    4. dispatch siblings[1..N-1] concurrently             # cache-hit on shared prefix
```

**Composition.** Step 1 (plan persistence) is C2-owned context-engineering primitive composing orthogonally with topology pattern; step 2–4 (warm-up serialization) is harness-owned. The protocol applies to all cells where fan-out cap > 1 (orchestrator-workers, parallelization, evaluator-optimizer with multi-evaluator).

### 1.9 Multi-agent span hierarchy schema

D4 extends F3 v1.1 capability-floor (iv) observable lifecycle with the multi-agent span schema:

```
parent_session                                   (root span)
├── topology.fanout.opened                       (attrs: pattern, fan_out_cap, cascade_policy,
│                                                          workload_class, engine_class,
│                                                          concurrent_token_budget_at_dispatch)
├── subagent.span[0]                             (child span; trace_id propagated;
│   │                                             parent_span_id = topology.fanout.opened)
│   ├── llm.inference[]                          (per-sibling inference; cost attribution
│   │                                             per Anthropic ~15× chat-token budget [HIGH])
│   ├── tool.call[]                              (per-sibling tool spans;
│   │                                             gate_level_computed per §1.5)
│   ├── hitl.gate.evaluated                      (D5 §1.8 schema; if gate triggered)
│   └── subagent.span.closed                     (attrs: result_status, request_blocked_by_budget,
│                                                          tokens_in, tokens_out, cached_tokens_in)
├── subagent.span[1] ... [N-1]                   (siblings; concurrent or serialized
│                                                  per §1.8 warm-up protocol)
└── topology.fanout.closed                       (attrs: results_collected, results_failed,
                                                          cascade_applied, synthesis_token_budget,
                                                          cascade_decision_audit_ledger_id)
```

**Sampling discipline** (per `c7-observability` SKILL.md):

| Span | Sampling rate | Rationale |
|---|---|---|
| `topology.fanout.opened` / `topology.fanout.closed` | always-sampled (head=1.0) | Tamper-evidence-relevant under Persona §10.4; cost attribution requires fan-out boundaries |
| `subagent.span` root | always-sampled (head=1.0) | Per-sibling cost attribution |
| `llm.inference` / `tool.call` inside sub-agent | base sampling rate (head-based-dev / tail-based-prod) | Volume-bounded; tail-keep-on-classification for failures |
| `hitl.gate.evaluated` / HITL spans | always-sampled (head=1.0) | Per D5 §1.8; tamper-evidence-relevant |
| `fallback.triggered` (C7 schema) | always-sampled with `provider_discriminator` attribute | Cross-family fallback traceability per `c7-observability` SKILL.md |

**Per-sibling cost attribution** sums to fan-out totals at `topology.fanout.closed`; the discrepancy between fan-out total and parent's pre-dispatch token budget is the operator-visible token-budget-multiplier signal (Anthropic research system witness ~15× [HIGH]).

### 1.10 Cross-sibling audit-ledger discipline

Per-sibling tool calls produce ledger entries keyed on the sibling's `thread_id` per F2 entry shape. The parent's audit ledger entry at `topology.fanout.closed` includes the merkle-root of the per-sibling ledger entries:

```
parent_fanout_close_entry = (
    action_id           : ParentActionID,
    fanout_topology     : Pattern,
    sibling_ledger_root : MerkleRoot[sibling_thread_ids → sibling_ledger_entry_hashes],
    cascade_decision    : "completed" | "cascade-cancelled" | "paused-on-failure",
    timestamp           : ISO-8601,
    prior_event_hash    : SHA-256
)
```

**F2 substrate relationship (per F2-14 Reading 1 disposition).** `parent_fanout_close_entry` is a SEPARATE ledger primitive that joins F2 state-ledger via `action_id` reference; it is NOT an F2 state-ledger entry. The fields differ from F2's six-field entry shape deliberately:

- **Per-sibling tool-call ledger entries** — written by sub-agents during execution — honor F2's six-field entry shape `(action_id, idempotency_key, actor, response_hash, timestamp, prior_event_hash)` per `ADR-F2 §(c)`. These are the F2 substrate primitives; D4 introduces no F2 revision at this surface.
- **`parent_fanout_close_entry`** — written by the orchestrator at fan-out close — is a separate ledger primitive with fanout-specific fields (`fanout_topology`, `sibling_ledger_root`, `cascade_decision`). The missing F2 fields are intentional, not under-specification:
  - `idempotency_key` is per-action; fanout-close is per-topology, not per-action. F2's idempotency-key contract attaches to action-scoped writes per Cluster 4 §2.2.7 [HIGH] Stripe-style construction `sha256(conversation_id || step_index || tool || canonical_args)`; the fanout-close primitive sits at topology boundary, not action boundary.
  - `actor` for a fanout-close is structurally the orchestrator agent; the topology context already disambiguates the writer, so `actor` would be redundant.
  - `response_hash` does not apply at fanout aggregate level — there is no single response. The response IS the merkle-root over siblings, carried in the fanout-specific field `sibling_ledger_root`.
- **Merkle-root construction (read-side semantics).** `sibling_ledger_root` is computed by reading per-sibling F2 ledger entries via `action_id` join (each sibling's F2 entries reference the parent's `ParentActionID` as their conversation/topology root through F2's `action_id` field) and computing the merkle tree over the read set's per-sibling entry hashes. The construction does NOT write F2 entries; it reads them.

This disposition preserves the F2 substrate as a single-write-contract primitive: F2 entries continue to honor the locked six-field shape `(action_id, idempotency_key, actor, response_hash, timestamp, prior_event_hash)` without polymorphic variation, and the fanout-close primitive sits beside F2, joining via `action_id` reference. T-perm-2 F2-layer resolution stands without D4-layer revision.

**Per-persona-tier cryptographic shape** per D5 §1.4:

| Persona tier | Sibling ledger entries (F2 substrate) | Parent fanout-close entry (separate primitive joining F2 via `action_id`) |
|---|---|---|
| solo-developer | Append-only SQLite | Append-only SQLite with merkle-root |
| team-binding | Hash-chained SQLite | Hash-chained SQLite with merkle-root |
| multi-tenant-compliance | Hash-chained SQLite + cryptographic signature per entry | Hash-chained SQLite + signed merkle-root + tamper-evident trace proof |

### 1.11 Workload-binding-time selection contract

Per-cell topology pattern + fan-out cap + cascade-policy default + writer-serialization stance is committed at D4; specific candidate-within-pattern is deferred to workload-binding-time downstream of Phase 3:

```
At workload-binding-time downstream of Phase 3:

1. Operator declares workload class (software-engineering | content-creation |
   pipeline-automation | research).
2. Operator declares deployment surface per D1 §1.2 (local-development |
   self-hosted-server | managed-cloud).
3. Cell at (workload-class × D1-engine-class) lookup yields:
     - topology pattern (§1.2)
     - fan-out cap (§1.2)
     - cascade-policy default (§1.2)
     - writer-serialization stance (§1.2)
     - cascade-enforcement mechanism (§1.3)
     - T-perm-3 reading (§1.3, §1.4)
4. Operator selects specific candidate from §11.3.2 D4 enumeration meeting
   the cell's pattern + cap + cascade-policy + writer-serialization commitments.
5. Composition with §1.5 sub-agent privilege inheritance, §1.7 HandoffContext
   contract, §1.8 cache warm-up protocol, §1.9 span hierarchy, §1.10 audit
   ledger discipline is enforced at runtime regardless of candidate choice.
```

## Rationale

### (a) Pattern this decision follows

The six-pattern taxonomy follows Pattern Reference Catalog v1.0 §10.1 P-CP series at depth — P-CP (chaining) at single-threaded; P-CP (parallelization) at orchestrator-workers and parallelization-sectioning-voting; P-CP (orchestrator-workers) at orchestrator-workers; P-CP (evaluator-optimizer) at evaluator-optimizer; routing handled at F1-layer not D4-layer. P-CP-8 (stateless reducer / launch-pause-resume control flow) is the F3 substrate the per-engine-class implementation mechanism overlay (§1.3) composes against. Cluster 1 §1–§3 [HIGH] cross-framework pattern equivalences ground the taxonomy across the corpus: OpenAI manager ≡ Anthropic orchestrator-workers ≡ revfactory/harness Supervisor; OpenAI decentralized ≡ Microsoft handoff. The per-workload-class commitment (§1.2) follows Cluster 1 §1 [HIGH] Cognition-Anthropic adjudication "parallelize read/research; serialize writes" applied per Persona §8.1–§8.4 per-class characterization. The fan-out cap commitments follow the Anthropic research system witness (3–5 per fan-out [HIGH]) and deer-flow witness (concurrency cap = 3) and 12-Factor Factor 10 (small-focused-agents reliability ceiling 3–10 steps). The sub-agent-as-tool composition pattern follows Cluster 1 §6 [HIGH]: smolagents `managed_agents` and OpenAI Agents SDK `agent.as_tool()` as canonical. The HandoffContext contract follows Cluster 4 §2.4.3 [HIGH]; the brief object structure follows Anthropic research system [HIGH]. The concurrent-prompt-cache warm-up protocol follows Cluster 1 §[HIGH] cache-miss-storm prevention pattern. The T-perm-3 multiplicative tunable parameter encoding follows the spec-writer s3 §6.3 architecture for permanent-tension carry-forward shapes. The multi-agent span hierarchy schema follows OTel GenAI semconv per `c7-observability` SKILL.md.

### (b) Workload-constraint application

D4 inherits the F3-layer / D1-layer / D5-layer persona-and-workload-class framing and operationalizes per Persona §3.1 four-class enumeration:

- **§3.1.1 software engineering** + §8.1 control-plane characterization "[HIGH] Multi-step session shape dominant; evaluator-optimizer / Reflexion-style validation loops natural fit. [MODERATE] Parallel multi-agent reads (review, eval) acceptable; writes single-threaded per Cognition strong-convergence" → §1.2 row 1: evaluator-optimizer for writes (1 generator + 1–3 evaluators); orchestrator-workers for reads (cap 3); pause-on-write / proceed-on-read; strict writer-serialization.
- **§3.1.2 content creation** + §8.2 "[HIGH] HITL naturally synchronous at design-time (operator review-in-loop); multi-step session shape typical; lower parallelism need than software-eng" → §1.2 row 2: evaluator-optimizer with 1 generator + 1–2 evaluators; pause; strict.
- **§3.1.3 pipeline automation** + §8.3 "[HIGH] F3 durable-execution-spine territory par excellence; multi-stage workflows with explicit step boundaries; retry/breaker discipline most rigorous; idempotency keys non-negotiable" → §1.2 row 3: sequential default; orchestrator-workers (cap 3) on idempotent parallel stages only; cascade-cancel; strict.
- **§3.1.4 research** + §8.4 mixed-F3 with Anthropic-canonical 3–5 fan-out → §1.2 row 4: orchestrator-workers (cap 3–5) per Anthropic research system [HIGH]; proceed (lossy synthesis acceptable); relaxed.

Persona §3.2 workload-class extensibility flag forces topology-above-engine viability — save-point and pure-pattern engine classes preserved at every cell where T-perm-3 reading allows ABOVE_ENGINE. Persona §3.3 work-unit-shape distribution heterogeneity forces multi-pattern accommodation within a single workload class — §1.2 row 1 commits two primary patterns (evaluator-optimizer for writes; orchestrator-workers for reads) per the Cognition-Anthropic adjudication. Persona §4 99.9%+ SLO at tens-concurrent forces fan-out cap ceilings at 3–5 — beyond this cap the synthesis bottleneck and rate-limit-storm risk per Cluster 4 §2.2.7 [HIGH] and Cluster 1 §[HIGH] dominate. Persona §6 per-workload-class cost ceiling forces fan-out cap to be cost-tunable per workload class — research's 3–5 cap is justified by Anthropic research system witness; pipeline-automation's 3 cap is justified by deer-flow witness; software-engineering writes' 1+1–3 cap is justified by Cognition strong-convergence. Persona §7 "Anthropic primitives where they fit" composes with §1.2 row 4 research-row Anthropic-research-system-canonical pattern. Persona §10.4 compliance-readiness foundational primitives compose with §1.10 cross-sibling audit-ledger discipline at multi-tenant-compliance tier. Persona §11.4 throughput rough order-of-magnitude open at design-time forces fan-out cap calibration deferral to workload-binding-time per §1.11.

### (c) T-perm-3 D4-layer stance

D4 promotes T-perm-3 to Layer 3 with the multiplicative tunable parameter specialization `topology_fault_handling × workload_class × topology_pattern` per §1.6. The tension is structural to the slate per `references/output-templates.md` Layer-3 list: C1 reads control-flow as authored above the engine to preserve Persona §3.2 workload-class-extensibility (topology-pattern decisions are first-class harness primitives independent of engine choice); C9 reads reliability as living below topology with engine-as-reliability-substrate giving the strongest guarantees per Cluster 2 V2 §2.3.4 [HIGH] and Diagrid Feb 25 2026 [HIGH]. Both readings are correct in their respective regimes — local-development × save-point / pure-pattern engine classes favor the C1 reading; pipeline-automation × event-sourced-replay favors the C9 reading; K8s-resident reconciler-loop favors the C9 RECONCILER reading. The §1.4 matrix operationalizes the per-cell resolution; §1.6 specifies the compositional layering with F1-layer per-layer-time-budget and D1-layer per-deployment-surface resolutions along the chain-advancement seam.

D4-layer additions to the tunable parameter:

- `workload_class` axis is **necessary** because Persona §8.1–§8.4 per-class control-plane characterization differs at the cascade-policy default (pause vs proceed vs cascade-cancel); without this axis, cascade-policy collapses to a single-cell default, contradicting §3.1 four-class first-class commitment.
- `topology_pattern` axis is **necessary** because per-pattern fault-handling-responsibility differs (orchestrator-workers: lead handles synthesis-on-failure; decentralized-handoff: target handles; hierarchical-delegation: parent handles cascade upward); without this axis, the cascade-decision routing collapses across patterns, masking the pattern-specific fault semantics.

### (d) Cross-axis composition

**With D1 substrate (per-engine-class topology primitive shape).** §1.3 inherits D1 §1.1 five-element taxonomy; §1.4 2D matrix specializes per cell with T-perm-3 reading per §1.3. D4 introduces no D1 revision; D1's per-deployment-surface candidate mapping at §1.2 stands.

**With D5 substrate (sub-agent-boundary HITL placement and cascade_policy declaration).** §1.5 sub-agent privilege inheritance composes with D5 §1.5.1 multiplicative gate-level rule via `max(parent_gate_level, ..., persona_tier_floor)` formula extension to the sub-agent boundary. §1.4 cascade-policy default per cell instantiates D5 §1.3.1 `cascade_policy` parameter. §1.7 HandoffContext contract instantiates Cluster 4 §2.4.3 [HIGH] shape declared at D5 §1.3.1 interface signature. §1.10 cross-sibling audit-ledger discipline composes with D5 §1.4 per-persona-tier ledger cryptographic shape via merkle-root construction.

**With F3 capability-floor.** §1.9 multi-agent span hierarchy schema extends F3 v1.1 capability-floor (iv) observable lifecycle with `topology.fanout.*` and `subagent.span` schema; §1.10 cross-sibling audit-ledger discipline composes with F3 capability-floor (ii) idempotency-keyed exactly-once via per-sibling F2 ledger entries.

**With F1 (chain-advancement coordination).** §1.6 compositional layering of F1-layer per-layer-time-budget + D1-layer per-deployment-surface + D4-layer per-workload × pattern resolves T-perm-3 across the chain-advancement seam; F1 fallback-trigger spans propagate per §1.9 span hierarchy at sub-agent boundary with `provider_discriminator` attribute per `c7-observability` SKILL.md.

**With F2 (state-ledger entry shape).** §1.10 per-sibling tool-call ledger entries write to F2 substrate per F2's six-field entry shape `(action_id, idempotency_key, actor, response_hash, timestamp, prior_event_hash)` without revision. The §1.10 `parent_fanout_close_entry` is a SEPARATE ledger primitive joining F2 state-ledger via `action_id` reference (NOT an F2 entry per F2-14 Reading 1 disposition); merkle-root construction reads F2 entries via `action_id` join and aggregates per-sibling entry hashes into `sibling_ledger_root` without writing F2 entries. F2 substrate single-write-contract preserved; T-perm-2 F2-layer resolution stands without D4-layer revision.

**With D2 (sandbox provider) — forward-reference.** Sub-agent privilege inheritance per §1.5 composes with D2 sandbox tier per F4 graduated-isolation principle — sub-agent's effective sandbox tier inherits parent's tier with monotonic ascension (sub-agent cannot escape a stricter sandbox); D2 binds the per-tier sandbox provider downstream.

**With D3 (Anthropic-primitive adoption depth) — forward-reference.** Per-sub-agent model binding (Haiku for breadth-search; Sonnet for synthesis; Opus for high-fidelity orchestrator) per Cluster 1 §[HIGH] Anthropic research system witness composes with D4 §1.2 fan-out cap commitments; cost-amortization at fan-out cap = 5 × Haiku siblings + Sonnet synthesizer is the Anthropic-research-system-canonical regime D3 will commit per cell.

**With D6 (observability backend) — forward-reference.** §1.9 multi-agent span hierarchy + §1.10 cross-sibling audit-ledger discipline produces the OTel GenAI semconv schema D6 will ingest; per-persona-tier sampling discipline at §1.9 propagates to D6 backend selection.

## Consequences

**(a) Per-cell topology pattern committed at D4.** Workload-binding-time selection is reduced to candidate-within-pattern selection per §1.11; the topology-pattern decision is closed at D4 across the matrix.

**(b) Sub-agent fan-out cap committed at D4.** Operator cannot override fan-out cap upward without Workflow §4.1.2 Class-2 D4 revision. Operator may override fan-out cap downward (e.g., declare fan-out cap = 1 at research workload to operate single-threaded) at workload-binding-time per §1.11.

**(c) T-perm-3 D4-layer tunable parameter `topology_fault_handling × workload_class × topology_pattern` carry-forward to permanent-tension ledger.** F1-layer + D1-layer + D4-layer compositional resolution preserved per §1.6.

**(d) T-perm-1 D5-layer resolution stands; D4 introduces sub-agent privilege inheritance contract per §1.5 without ledger revision.** Sub-agent privilege seam is C4-and-C10-jointly-owned; the §1.5 default-downgrade rule is the D4-layer commitment without modifying the D5-layer multiplicative tunable parameter.

**(e) T-perm-2 F2-layer resolution stands; D4 introduces HandoffContext serialization contract per §1.7 without ledger revision.** Within-vs-across-turn boundary at sub-agent dispatch is preserved; HandoffContext crosses the seam with explicit shape per Cluster 4 §2.4.3 [HIGH].

**(f) Concurrent-prompt-cache warm-up protocol is required at fan-out cap > 1.** The harness-owned serialization of the first sibling adds a one-sibling-latency overhead at fan-out dispatch; the cost-amortization (cache-hit on remaining N-1 siblings) outweighs this at any fan-out cap ≥ 2 per Cluster 1 §[HIGH].

**(g) Multi-agent span hierarchy schema extends F3 v1.1 capability-floor (iv).** D6 (observability backend) ingestion contract receives the §1.9 schema as a D4-layer commitment; backend selection at deployment-surface-time must support OTel `traceparent` propagation + child-span hierarchy + `provider_discriminator` attribute.

**(h) Cross-sibling audit-ledger discipline at multi-tenant-compliance persona tier requires merkle-root signing.** Persona §10.4 compliance-readiness primitive is operationalized at §1.10 with per-persona-tier cryptographic shape; multi-tenant-compliance tier requires signed merkle-root + tamper-evident trace proof. F2 substrate stands without revision; D4 adds a merkle-root construction primitive that composes atop F2 entry shape.

**(i) Hierarchical-delegation pattern is admissible but non-primary.** Cognition manager-Devin-spawning-child-Devin pattern requires explicit operator declaration at workload-binding-time per §1.5 override; default is non-primary placement to prevent topology-bloat per Persona §4 99.9%+ SLO.

**(j) D3 forward-reference: per-sub-agent model binding will bind Haiku/Sonnet/Opus per role per cell.** D4 commits fan-out cap and topology pattern; D3 will commit model-routing per role per cell; the joint commitment produces the Anthropic-research-system-canonical regime at research workload + ~15× chat-token budget visibility per §1.9.

**(k) Per-workload-class fan-out-cap operator-burden eval.** `expected_fan_out_cap_per_task` per `c8-eval-engineer` SKILL.md is the canonical operator-burden eval primitive; per-workload-class calibration targets:

| Workload class | Target `expected_fan_out_cap_per_task` |
|---|---|
| Software engineering writes | 1 (>1 indicates Cognition violation) |
| Software engineering reads | 1–3 (>3 indicates topology-bloat) |
| Content creation | 1–2 |
| Pipeline automation | 1–3 (deer-flow witness) |
| Research | 3–5 (<3 breadth-under-coverage; >5 Anthropic-canonical-violation) |

## Alternatives considered

**Alt-1 — Harness-uniform topology commitment (single pattern across all workload classes).** Rejected: Persona §3.1 four-class first-class enumeration + §8.1–§8.4 per-class control-plane characterization heterogeneity makes single-pattern commitment incompatible with workload-class specialization. Cluster 1 §1 [HIGH] Cognition-Anthropic adjudication "parallelize read/research; serialize writes" forces minimum two patterns at the workload axis (single-threaded for writes; orchestrator-workers for reads).

**Alt-2 — Single-threaded-uniform commitment (Cognition-only reading).** Rejected: Persona §8.4 research mixed-F3 with Anthropic-canonical 3–5 fan-out + Persona §7 "Anthropic primitives where they fit" + Cluster 1 §[HIGH] Anthropic research system production-witness contradict single-threaded-uniform. Anthropic research system's 90.2% improvement over single-agent on breadth-first benchmark per Cluster 1 §[HIGH] is the witness D4 must accommodate.

**Alt-3 — Parallelize-everything commitment (Anthropic-only reading).** Rejected: Cluster 1 §1 [HIGH] Cognition-Anthropic adjudication explicitly excludes parallel writes; "digital gossiping" failure mode at parallel writers is named at Cluster 1 §[HIGH]. Persona §8.1 software-engineering writes single-threaded per Cognition strong-convergence + Persona §8.3 pipeline-automation sequential durable spine contradict parallelize-everything.

**Alt-4 — Pattern-class-only-at-D4 (OD-3.C rejected).** Rejected at OD selection: pattern-class commitment without per-workload-class candidate evaluation leaves the production-pattern witnesses (Anthropic research system 3–5 fan-out for research; Cognition single-threaded-writer for software engineering; deer-flow concurrency-cap-3 for pipeline workflows; deepagents SubAgentMiddleware for context-isolation-required workloads) unconnected to D4's decision rationale. Per Persona §8.1–§8.4 per-class control-plane characterization, the per-class differentiation IS the decision surface; pattern-class commitment alone produces under-closure relative to OD-3.A 2D matrix.

**Alt-5 — Workload-class-assumed-at-D4 (OD-3.B rejected).** Rejected at OD selection: §3.1 four-class first-class commitment is project-level. OD-3.B compresses two decisions (workload-class commitment + topology pattern commitment) into one; the project commits to all four workload classes simultaneously per §3.1 + §3.2 extensibility flag.

**Alt-6 — Anthropic-canonical narrowed scope (OD-1.C rejected).** Rejected at OD selection: pre-commits a framework-canon dimension Persona §7 records as soft-preference rather than hard constraint; D4 should preserve framework-pluralism at the topology layer per Persona §7 "vendor-neutral abstraction otherwise." The non-Anthropic candidates at §11.3.2 D4 (revfactory/harness six-pattern enumeration; humanlayer/12-factor Factor 10; bytedance/deer-flow concurrency cap; mvschwarz/openrig RigSpec; oh-my-openagent role-temperament; ruvnet/ruflo hive-mind; disler/infinite-agentic-loop; shareAI-lab/Kode-Agent multi-agent room) are part of the deliberation surface, not the deferred specification.

**Alt-7 — Sub-agent privilege inheritance (full-inherit, no downgrade).** Rejected: principle-of-least-privilege at the topology layer + Persona §10.4 compliance-readiness foundational primitive force default-downgrade at external-reversible (to ask) and removal at external-irreversible. C10 §3.11.1 stake at council deliberation grounds the §1.5 commitment; full-inherit reading is admissible only via explicit operator override at workload-binding-time per §1.5 override clause.

**Alt-8 — Cascade-policy single-default (no per-cell variation).** Rejected: Cluster 4 §2.4.4 [HIGH] sub-agent HITL composition documents distinct cascade-timeout semantics per topology pattern (pause at sub-agent-boundary HITL with parallel siblings; cascade-cancel at sequential durable pipeline; proceed at lossy-synthesis research). Single-default cascade-policy collapses these distinctions.

## References

### Shape 1 — Substrate dependency declaration

- `Cluster 5 V2 §3 D4` (within `Agent_Harness_Architecture__Deployment_Surfaces__Anthropic_Primitives__and_Foundational_Tradeoffs.md`) line 206 — D4 workload-dependent classification: "single-threaded-writes is a strong default; parallel sub-agents only for read-heavy/exploration workloads (Yan 2026 follow-up)".

### Shape 2 — Pattern Reference Catalog source citations

- `Pattern Reference Catalog v1.0 §10.1 P-CP series` (chaining, routing, parallelization, orchestrator-workers, evaluator-optimizer) — load-bearing pattern catalog at D4 layer; Anthropic six-pattern canon per Schluntz & Zhang Dec 2024 "Building Effective Agents".
- `Pattern Reference Catalog v1.0 §10.1 P-CP-8` (stateless reducer / launch-pause-resume control flow) — F3-cited; topology pause/resume substrate composition with §1.3 per-engine-class implementation mechanism overlay.
- `Pattern Reference Catalog v1.0 §10.4 P-OD-3` (audit ledger / decision log / hash-chained provenance) — composes with §1.10 cross-sibling audit-ledger discipline at multi-tenant-compliance tier.

### Shape 3 — Per-axis recommendation citation

- `Pattern Reference Catalog v1.0 §11.3.2 D4` (lines 3139–3148) — Multi-agent topology decision; workload-dependent classification; candidate set: revfactory/harness (six topology patterns: Pipeline / Fan-out-Fan-in / Expert Pool / Producer-Reviewer / Supervisor / Hierarchical Delegation); humanlayer/12-factor-agents (Factor 10 — small focused agents; 3–10 step reliability ceiling); bytedance/deer-flow (concurrency cap = 3); langchain-ai/deepagents (SubAgentMiddleware for context isolation); mvschwarz/openrig (RigSpec multi-process topology); code-yeongyu/oh-my-openagent (11-role taxonomy with model temperament binding); shareAI-lab/Kode-Agent (Multi-agent room); ruvnet/ruflo (hive-mind queen-led + mesh); disler/infinite-agentic-loop (wave-based parallel sub-agent generation).

### Shape 4 — Parent F-ADR / D-ADR citations

- `ADR-F3 §Decision` (durable-execution-as-coordination-spine pattern P-CP-8; capability-requirement floor (i)–(iv); manifest-declaration invocation default; per-step annotation opt-in; F3-engine selection deferred to per-workload-class D-ADRs) — D4 specializes per workload-class × engine-class.
- `ADR-F3 §Decision floor (iv)` (observable lifecycle exposing workflow-start, step-boundary, fallback-trigger, retry-attempt, breaker-trip, lease-acquired/released, and resumption events) — extended at D4 §1.9 with multi-agent span hierarchy schema.
- `ADR-F1 §Consequences (c)` (D-ADR on routing-strategy implementation must specify per-layer time budgets, breaker placement per `{provider, model}` pair, and chain-advancement coordination with C9 retry mechanics; engages T-perm-3 directly) — D4 §1.6 compositional layering F1-layer + D1-layer + D4-layer.
- `ADR-F2 §(c)` (state-ledger entry shape `(action_id, idempotency_key, actor, response_hash, timestamp, prior_event_hash)` — F2 ledger as canonical substrate per-sibling state-ledger entries write to without revision) — D4 §1.10 cross-sibling audit-ledger discipline composes atop F2 substrate via merkle-root construction.
- `ADR-D1 §1.1` (five-element engine-class taxonomy: event-sourced-replay / save-point-checkpoint / pure-pattern-no-engine / reconciler-loop / WAL-segment) — D4 §1.3 per-engine-class implementation mechanism overlay inheritance source.
- `ADR-D1 §1.2` (per-deployment-surface candidate mapping; per-engine-class topology primitive shape inheritance source) — D4 §1.4 2D matrix per-engine-class column source.
- `ADR-D1 §1.3` (D1-layer T-perm-3 resolution `topology_fault_handling ∈ {ABOVE_ENGINE, BELOW_ENGINE, RECONCILER}`) — D4 §1.6 multiplicative tunable parameter specialization parent source.
- `ADR-D5 §1.3` (three-placement HITL topology primitive: pre-action / sub-agent-boundary / validator-escalation) — D4 §1.5 sub-agent privilege inheritance contract composition source.
- `ADR-D5 §1.3.1` (topology primitive interface signature with `cascade_policy ∈ {pause, proceed, cascade-cancel}`) — D4 §1.2 cascade-policy default per-cell instantiation source.
- `ADR-D5 §1.5` (T-perm-1 D5-layer multiplicative gate-level composition rule `per_tool_gate_level × per_mcp_server_trust_tier × persona_tier × blast_radius_tier`) — D4 §1.5 sub-agent gate-level computation extension source.
- `ADR-D5 §1.5.2` (cross-deployment monotonicity: `persona_tier_floor` monotonic ascending; tier downgrade structurally prohibited) — D4 §1.5 sub-agent monotonic-ascension inheritance source.
- `ADR-D5 §1.4` (per-persona-tier ledger cryptographic shape: solo-developer append-only; team-binding hash-chained; multi-tenant-compliance hash-chained + signed) — D4 §1.10 cross-sibling audit-ledger per-persona-tier composition source.
- `ADR-D5 §1.6` final paragraph (sub-agent cascade timeout per Cluster 4 §2.4.4 [HIGH]; `cascade_policy ∈ {pause, proceed, cascade-cancel}`; T-perm-3 D1-layer resolution shape `topology_fault_handling` covers this composition without D5-layer revision) — D4 §1.6 T-perm-3 D4-layer specialization mandate source.

### Shape 5 — Persona document trace

- `Persona_Document_v1 §2` (bridging-arc persona — sole operator at design-time; team or multi-tenant binding state later) — D4 §1.10 per-persona-tier audit-ledger discipline source.
- `Persona_Document_v1 §3` (workload classes including long-running-survives-restarts subset) — D4 workload-class differentiation source.
- `Persona_Document_v1 §3.1` (four primary workload classes as first-class) — D4 §1.2 per-workload-class commitment row enumeration source.
- `Persona_Document_v1 §3.1.1` (software engineering as primary workload class) — D4 §1.2 row 1 source.
- `Persona_Document_v1 §3.1.2` (content creation as primary workload class) — D4 §1.2 row 2 source.
- `Persona_Document_v1 §3.1.3` (pipeline automation as primary workload class) — D4 §1.2 row 3 source.
- `Persona_Document_v1 §3.1.4` (research as primary workload class) — D4 §1.2 row 4 source.
- `Persona_Document_v1 §3.2` (workload-class-extensibility flag) — D4 topology-pattern-extensibility-via-Workflow-Class-2-revision constraint source; T-perm-3 C1-reading-anchor.
- `Persona_Document_v1 §3.3` (work-unit shape distribution heterogeneous) — D4 §1.2 row 1 multi-pattern commitment source (evaluator-optimizer + orchestrator-workers within single workload class).
- `Persona_Document_v1 §3.4` (per-workload-class HITL synchrony differentiation) — D4 §1.2 cascade-policy default per-row pause-vs-proceed-vs-cascade-cancel source.
- `Persona_Document_v1 §4` (scale, 99.9%+ SLO, tens-concurrent, mathematical incompatibility with operator-in-loop-on-every-failure HITL) — D4 fan-out cap ceiling source (3–5 max); rate-limit-storm risk source.
- `Persona_Document_v1 §5` (integration surface — hosted majors + local/open-weight tier; broad action surface; computer-use at design-time AND production-time) — D4 §1.5 sub-agent privilege inheritance external-reversible / external-irreversible classification source.
- `Persona_Document_v1 §6` (per-workload-class cost ceiling) — D4 §1.2 fan-out cap cost-tunability per-class source.
- `Persona_Document_v1 §7` ("Anthropic primitives where they fit"; vendor-neutral abstraction otherwise) — D4 §1.2 row 4 research-row Anthropic-research-system-canonical pattern source; framework-pluralism preservation rationale source.
- `Persona_Document_v1 §8.1` (software engineering — "[HIGH] Multi-step session shape dominant; evaluator-optimizer / Reflexion-style validation loops natural fit. [MODERATE] Parallel multi-agent reads (review, eval) acceptable; writes single-threaded per Cognition strong-convergence ('digital gossiping' failure mode, Cognition)") — D4 §1.2 row 1 evaluator-optimizer + orchestrator-workers binding source; Cognition strong-convergence writer-serialization source.
- `Persona_Document_v1 §8.2` (content creation — "[MODERATE] Multi-step session shape typical; lower parallelism need than software-eng") — D4 §1.2 row 2 evaluator-optimizer with low fan-out cap source.
- `Persona_Document_v1 §8.3` (pipeline automation — "[HIGH] F3 durable-execution-spine territory par excellence; multi-stage workflows with explicit step boundaries"; retry/breaker discipline most rigorous; idempotency keys non-negotiable) — D4 §1.2 row 3 sequential default + cascade-cancel source; T-perm-3 C9-reading-anchor.
- `Persona_Document_v1 §8.4` (research — F3 mixed; Anthropic-canonical 3–5 fan-out territory) — D4 §1.2 row 4 orchestrator-workers + 3–5 fan-out + proceed cascade-policy + relaxed writer-serialization source.
- `Persona_Document_v1 §10.1` (durable-execution capability requirement persona-answered) — F3 v1.1 capability-floor parent source; D4 §1.9 multi-agent span hierarchy schema extension source.
- `Persona_Document_v1 §10.2` (F3 persona-constrained — workload-class dependent; production-time deployment surface persona-constrained-but-not-picked) — D4 deferral framing source; per-cell deployment-surface-time × workload-binding-time selection contract source.
- `Persona_Document_v1 §10.4` (compliance-readiness foundational primitives — hash-chained audit ledger, comprehensive observability, retention controls) — D4 §1.10 cross-sibling audit-ledger merkle-root signing at multi-tenant-compliance tier source; §1.9 always-sampled topology spans source.
- `Persona_Document_v1 §11.4` (throughput rough order-of-magnitude per day — open item) — D4 fan-out cap calibration deferral to workload-binding-time per §1.11 source.

### Substrate research citations (corpus-derived)

- Cluster 1 §1 [HIGH] (Cognition-Anthropic debate adjudication "parallelize read/research; serialize writes"; production-grade-multi-agent-research-system characterization) — D4 §1.2 per-workload-class commitment dominant rule source.
- Cluster 1 §2 [HIGH] (Anthropic research system orchestrator-worker prompt structure; 3–5 subagents per fan-out; ~15× chat-token budget; brief object structure: objective / output format / guidance / clear task boundaries; concurrent-prompt-cache warm-up requirement) — D4 §1.2 row 4 fan-out cap source; §1.7 brief object structure source; §1.8 cache warm-up protocol source; §1.9 ~15× cost attribution source.
- Cluster 1 §3 [HIGH] (cross-framework pattern equivalence: OpenAI manager ≡ Anthropic orchestrator-workers ≡ revfactory/harness Supervisor; OpenAI decentralized ≡ Microsoft handoff) — D4 §1.1 taxonomy cross-framework grounding source.
- Cluster 1 §6 [HIGH] (sub-agents and SFAs; SFA ceiling characterization: one tool family + ≤10 compute loops; sub-agent-as-tool composition pattern via smolagents `managed_agents` and OpenAI Agents SDK `agent.as_tool()`) — D4 §1.5 sub-agent-as-tool composition rationale source.
- Cluster 1 §7 [HIGH] (parallelism patterns; concurrency caps; prompt-caching interaction with parallel fan-out; self-consistency saturation curves; merger-bottleneck pattern) — D4 §1.2 fan-out cap ceiling source; §1.8 cache warm-up source.
- Cluster 4 §2.4.3 [HIGH] (HandoffContext shape: `proposed_action`, `agent_confidence`, `failed_attempts`, `alternatives_considered`, `state_summary`, `audit_trail_link`, `retry_history`) — D4 §1.7 HandoffContext serialization contract source.
- Cluster 4 §2.4.4 [HIGH] (sub-agent HITL composition; sub-agent interrupt stranding; cascade-timeout composition with parallel sibling sub-agents) — D4 §1.6 cascade-policy semantics source; §1.5 sub-agent privilege inheritance composition source.
- Cluster 4 §2.2.3 [HIGH] retry protocol (3rd-validator-fail → human-handoff; 2nd-validator-fail → re-prompt-with-different-system-prompt OR escalate-model-tier) — D4 §1.2 row 1 evaluator-optimizer retry-exit composition source.
- Cluster 4 §2.2.7 [HIGH] (per-`{provider, model}` circuit breakers; Stripe-style idempotency-key construction `sha256(conversation_id || step_index || tool || canonical_args)`; full-jitter retry default) — D4 §1.10 per-sibling idempotency-key qualified by sub-agent `thread_id` source.
- Cluster 2 V2 §2.3.4 [HIGH] (engine-tradeoff table — cost / latency / reliability / debuggability / RPO / RTO / operational complexity) — D4 §1.3 per-engine-class implementation mechanism overlay tradeoff source.
- Anthropic, "Building Effective Agents," Schluntz & Zhang, Dec 2024, anthropic.com/engineering/building-effective-agents — six-pattern canon source for §1.1 taxonomy.
- Anthropic, "How we built our multi-agent research system," Schluntz et al., June 2025, anthropic.com/engineering/multi-agent-research-system — Anthropic research system 3–5 fan-out witness; orchestrator-worker prompt structure source.
- Anthropic, "Effective harnesses for long-running agents," Nov 26 2025, anthropic.com/engineering/effective-harnesses-for-long-running-agents — long-running harness composition source.
- Cognition AI, "Don't Build Multi-Agents," Walden Yan, June 2025, cognition.ai/blog/dont-build-multi-agents — single-threaded writer canonical source for §1.2 row 1 + row 3 writes.
- Diagrid, "Checkpoints Are Not Durable Execution," Yaron Schneider, Feb 25 2026, diagrid.io/blog/checkpoints-are-not-durable-execution-why-langgraph-crewai-google-adk-and-others-fall-short-for-production-agent-workflows — `BELOW_ENGINE` reading rationale source.
- HumanLayer, "12-Factor Agents," Factor 10 (small focused agents), github.com/humanlayer/12-factor-agents — single-threaded reliability ceiling 3–10 steps source.
- bytedance/deer-flow, github.com/bytedance/deer-flow — concurrency cap = 3 production witness source.
- langchain-ai/deepagents, github.com/langchain-ai/deepagents — SubAgentMiddleware context-isolation reference source.
- shareAI-lab/Kode-Agent, github.com/shareAI-lab/Kode-Agent — multi-agent room + WAL-segment reference source.
- revfactory/harness, github.com/revfactory/harness — six-pattern enumeration (Pipeline / Fan-out-Fan-in / Expert Pool / Producer-Reviewer / Supervisor / Hierarchical Delegation) reference source.
- smolagents — `managed_agents` sub-agent-as-tool composition pattern source.
- OpenAI Agents SDK — `agent.as_tool()` sub-agent-as-tool composition pattern source.

### Workflow and skill discipline references

- `Project_Workflow_v1_1.md` §2.3.3 (Phase 3b D-ADR exit criteria — all six D-ADRs filed; each References section satisfies §2.3.3.1 discipline).
- `Project_Workflow_v1_1.md` §2.3.3.1 (References-section discipline for Phase 3b D-ADRs — five declaration shapes required; shape 5 mandatory for workload-dependent D-ADRs).
- `Project_Workflow_v1_1.md` §3.2 (Phase dependencies — D-ADR composition against F-ADR parent + Persona document + Cluster 5 V2 §3 substrate dependency declaration).
- `Project_Workflow_v1_1.md` §5.1 DP-1 (Phase 3a/3b execution-agent decision — DP-1-A full-council default applied at Phase 3b kickoff; DP-1-A confirmed at OD-2.A).
- `council-orchestrator` skill (`/mnt/skills/user/council-orchestrator/SKILL.md`) — convening discipline; Convening Block + CCR + voice contributions + TENSION block emission; T-perm-3 known-permanent labeling.
- `c1-orchestration-control` SKILL.md — multi-agent topology, control-flow patterns, sub-agent boundaries, parallelism mode, hand-off mechanics, loop termination criteria; T-perm-3 anchor at control-flow side.
- `c9-reliability-recovery` SKILL.md — per-`{provider, model}` circuit breakers; full-jitter retry; rate-limit-storm prevention; T-perm-3 anchor at reliability side.
- `c11-operator-local` SKILL.md — sub-agent HITL inheritance composition; D5 §1.3 sub-agent-boundary placement.
- `c2-context-engineering` SKILL.md — HandoffContext within-turn assembly; concurrent-prompt-cache warm-up; per-sub-agent context budget.
- `c3-state-persistence` SKILL.md — sub-agent state isolation; durable state across handoff; CoALA episodic memory residence.
- `c4-tools-integration` SKILL.md — sub-agent-as-tool composition; per-tool tier annotation; T-perm-1 anchor at capability side.
- `c5-validation-contract` SKILL.md — evaluator-optimizer pattern composition; producer-reviewer topology validator role; retry-exit criteria.
- `c6-model-routing` SKILL.md — per-sub-agent model binding (D3 forward-reference); cost-amortization at fan-out.
- `c7-observability` SKILL.md — multi-agent span hierarchy; parent-child span propagation per OTel GenAI semconv; provider_discriminator attribute; cost-attribution-per-span.
- `c8-eval-engineer` SKILL.md — `expected_fan_out_cap_per_task` operator-burden eval primitive; Husain manual-review→categorize→automate→align loop; meta-eval on topology selection routing accuracy.
- `c10-action-safety` SKILL.md — trust gradient across sub-agents; sub-agent privilege inheritance; cross-sibling tool-call audit; T-perm-1 anchor at gating side.
- spec-writer s3 §6.3 (permanent-tension-ledger tunable-parameter encoding architecture) — T-perm-3 D4-layer multiplicative tunable parameter shape source.

#### v1.1 revision-pass references (Phase 3c-CK iter-1 close, Path A LLM-assisted)

- `Project_Workflow_v1_2.md` §3.1 (D-ADR `Status: Proposed → Accepted` promotion gated on P3c-CK clearance; revision passes carry Proposed posture; revision-history convention) — v1.1 Status posture authority and Status-block revision-line convention source.
- `Project_Workflow_v1_2.md` §4.1.2 (Class-2 D-ADR revision criteria; surgical-edit discipline preserving verbatim content outside amendment surfaces) — v1.1 surgical-edit-discipline authority.
- `spec-writer` skill (`/mnt/skills/user/spec-writer/SKILL.md`) — v1.1 synthesis primitive activated at Phase 3c-CK iter-1 close mechanical revision pass per Path A skill mapping; ingestion contract Layer C narrative synthesis applied at §1.10 clarifying-prose authoring.
- `Adversarial_Review_3c.md` F2-14 (D4 §1.10 `parent_fanout_close_entry` shape relationship to F2 state-ledger entry shape ambiguous; lines 188–199 finding text with Reading 1 / Reading 2 disposition options) — v1.1 amendment target finding source.
- `Phase 3c-CK iteration 1 close handoff §4.1 D4 row` — v1.1 revision-scope authority; Path A LLM-assisted single-finding routing source.
- `Phase_3c_CK_Iter_2_Pre_Entry_Handoff_D4_Revision_Pass.md` §2 (F2-14 operator decision record with Reading 1 selected via `ask_user_input_v0` elicitation at session entry; recommendation-if-deferred captured as Reading 1) — v1.1 operator-decision-record source.

### Convening artifact citations (from this session's substrate review)

- Convening Block + CCR + voice contributions (C1 primary; C9 co-primary; C11 / C2 / C3 / C4 / C5 / C6 / C7 / C8 / C10 consultants) — preceding response in this session, segment 1 of 2.
- TENSION block (T-perm-3 promoted to Layer 3 with D4-layer multiplicative tunable parameter specialization `topology_fault_handling × workload_class × topology_pattern`; T-perm-1 / T-perm-2 adjacencies carry-forward by reference to ledger) — preceding response in this session, segment 1 of 2.

---

*Filed v1 2026-05-10 at Phase 3b Stage 1 close per Workflow v1.1 §2.3.3 (recommended next session at v1 filing: D3 Anthropic-primitive adoption depth per Phase 3b kickoff §4 sequencing — D3 composes against D4 §1.2 per-workload-class fan-out cap commitments and §1.7 brief object structure with per-sub-agent model binding Haiku/Sonnet/Opus per role per cell; D3 references D1 substrate; D3 references D5 §1.10 per-tier model binding for handoff-context summarization).*

*Revised v1.1 2026-05-10 per Phase 3c-CK iter-1 close mechanical revision pass (Path A LLM-assisted, single-finding) clearing `Adversarial_Review_3c.md` F2-14 under Reading 1 disposition (operator selection via `ask_user_input_v0` at session entry; `parent_fanout_close_entry` clarified as separate ledger primitive joining F2 via `action_id` reference). `Status: Proposed` preserved per `Project_Workflow_v1_2.md` §3.1; promotion to `Accepted` blocked until P3c-CK iter-2 clearance. T-perm-2 F2-layer resolution stands; no D4-layer ledger note added. See §Change-note (v1 → v1.1) for revision scope, F2-14 disposition rationale, sections-preserved-verbatim list, and inline changes inventory.*

*Next session at v1.1 filing: D6 v1.1 mechanical revision pass per parallel handoff (`Phase_3c_CK_Iter_2_Pre_Entry_Handoff_D6_Revision_Pass.md`); upon D6 v1.1 filing, P3c-CK iter-2 entry unblocked.*