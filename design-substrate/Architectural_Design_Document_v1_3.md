# Architectural Design Document v1.3

## Status block

| Field | Value |
|---|---|
| Artifact | `Architectural_Design_Document_v1_3.md` |
| Status | **Proposed** — F2-12 cascade Step 3 consolidation; promotion to Accepted at cascade close (after Step 6 plan revisions) |
| Version | v1.0 (2026-05-12) → v1.1 (2026-05-12) → v1.2 (2026-05-12) → **v1.3 (2026-05-14; F2-12 cascade Step 3 consolidation absorbing ADR-D1 v1.2 + ADR-D6 v1.2 per `F2-12_Closure_Path_Execution_Kickoff.md` §3.2 + `F2-12_Council_Deliberation_Output.md` §8.3 forward-routing)** |
| Date | 2026-05-14 (v1.3 consolidation pass) |
| Phase | 3d — ADD consolidation (post-Phase-3 F2-12 cascade Step 3 per `Project_Workflow_v1_7.md` §4.1.2; cascade-driven revision pass under `systems-architect` SKILL.md ADD consolidation sub-mode + Workflow v1.7 §7 fidelity-grammar discipline) |
| Skill | `systems-architect` (ADD-consolidation mode per SKILL.md §4) at v1.3 |
| Promotion path | Accepted at F2-12 cascade close (post-Step 6 plan v2.2 filing); F2-12 closure_pending false on cascade close |
| Source-set | F1 v1.2, F2 v1.2, F3 v1.1, F4 v1.1, F5 v1.1, D1 **v1.2** (post-F2-12 sub-scope (i)), D2 v1.1, D3 v1.1, D4 v1.1, D5 v1.3, D6 **v1.2** (post-F2-12 sub-scopes (ii) + (iii)) + `F2-12_Closure_Path_Execution_Kickoff.md` + `F2-12_Council_Deliberation_Output.md` (cascade Step 1 substrate) + `Integration_Verification_Report.md` (cleared) + `Persona_Document_v1.md` (read-only context) |
| Entry authorization | `F2-12_Closure_Path_Execution_Kickoff.md` §2.3 entry-gate disposition + §3.2 cascade Step 3 routing + `Project_Workflow_v1_7.md` §3.1 Status: Proposed preservation discipline |
| Exit gate | F2-12 cascade Step 4 (PRD v1.1 revision pass per `prd-author` SKILL.md revision-pass sub-mode) consuming this ADD v1.3 as substrate |

## Operator decisions front-matter

[v1.0–v1.2 OD-1 through OD-5 selections preserved verbatim from v1.2; not reproduced here for length. v1.3 cascade-driven revision pass authored under F2-12 cascade Step 3 routing per `F2-12_Closure_Path_Execution_Kickoff.md`; no new ODs surfaced at this revision.]

## Change-note (v1.2 → v1.3)

**Scope of revision.** F2-12 cascade Step 3 consolidation pass per `F2-12_Closure_Path_Execution_Kickoff.md` §3.2 + `F2-12_Council_Deliberation_Output.md` §8.3 forward-routing. The revision pass absorbs ADR-D1 v1.2 + ADR-D6 v1.2 substantive amendments into the ADD's cross-axis integration surface and closes the §6.3.1 F2-12 active-path carry-forward declaration. Six amendment sites:

| Site | Amendment shape | Substrate source |
|---|---|---|
| Status block | Version line extended with v1.3 entry; Source-set updated D1 v1.1 → v1.2, D6 v1.1 → v1.2; Entry authorization revised; Exit gate revised to cascade Step 4 | F2-12 cascade Step 3 entry |
| §3.1.1 D1 subsection | Synthesis + Constrained by + Decision summary + Rationale highlights + Operational implications + Engaged tensions paragraphs updated to absorb D1 v1.2 §1.1.1 4-attribute namespace + §1.1.2 per-engine-class replay-emission discipline + §1.1.2.2 F2 state-ledger entry shape extension | ADR-D1 v1.2 §1.1.1 + §1.1.2 + §1.1.2.2 |
| §3.4.1 D6 subsection | Synthesis + Constrained by + Decision summary + Rationale highlights + Operational implications + Engaged tensions paragraphs updated to absorb D6 v1.2 §1.2 engine.* row update + §1.2.2 retry.* namespace + §1.2.3 sub-agent boundary + §1.5 dedup algorithm + §1.5.1 / §1.5.2 / §1.5.3 sub-sections | ADR-D6 v1.2 §1.2 + §1.2.2 + §1.2.3 + §1.5 + §1.5.1–§1.5.3 |
| §5.2.2 T-perm-2 subsection | Residual surface paragraph updated to note F2-12 sub-scope (iii) ENGAGED at trace-ingestion dedup composition, reconciled via idempotency_key composition contract; ledger-reference-only carry-forward preserved | Council §7.2 TENSION block; ADR-D6 v1.2 §References ledger update |
| §5.2.3 T-perm-3 subsection | Residual surface paragraph updated to note F2-12 sub-scope (ii) ENGAGED at retry.attempt parent-child topology seam, honored at default `pre-declared-with-allowlist`; ledger-reference-only carry-forward preserved | Council §7.1 TENSION block; ADR-D6 v1.2 §References ledger update |
| §6.3.1 F2-12 carry-forward subsection | Status revised from 🔄 Deferred-acknowledged to **✅ CLOSED**; routing updated to record cascade execution path; completion forecast section replaced with closure summary; coordination shapes section closed | F2-12 cascade Step 3 closure |
| Appendix B | ADR inventory table rows D1 + D6 updated to reference v1.2 versions | Status block source-set update |

Workflow v1.7 §7 fidelity-grammar discipline applied across all amendment sites: no Pattern P1 cross-artifact name drift (D1 v1.2 §1.1.1 4-attribute namespace canonical at source; ADD §3.1.1 + §3.4.1 + Appendix B cite consistently); no Pattern P2 verbatim-claim-contradicted (all "per ADR-X v1.2 §Y" claims verify against source files at `/mnt/user-data/outputs/`); citation anchors substrate-verified per Workflow v1.7 §2.3.3.1 clause (iii).

**Status posture.** `Status: Proposed` preserved per `Project_Workflow_v1_7.md` §3.1 — promotion to `Accepted` blocked until F2-12 cascade close (post-Step 6 plan v2.2 filing). ADD v1.3 enters cascade Step 4 (PRD v1.1 revision pass) as substrate input.

**Sections preserved verbatim from v1.2.** §1 Persona summary; §§2.1–2.5 (F-ADR foundational decisions; all sub-elements at v1.2 form); §3.1.2 D4 (all sub-elements at v1.2 form); §3.1.3 D5 (all sub-elements at v1.2 form, including the v1.2-revised §3.1.3 Synthesis paragraph persona-tier emission characterization); §3.3.1 D2 + §3.3.2 D3 (all sub-elements at v1.2 form); §5.1 Resolved tensions (all sub-elements); §5.2.1 T-perm-1 subsection; §5.3 Cross-cutting properties; §5.4 Pattern P2 monitoring observation; §6.1 + §6.2 (Phase 4 + implementation deferral lists); §6.3.2 Pattern P2 monitoring subsection; Appendix A Traceability matrix (no cell mark changes; D1 + D6 rows reference v1.2 substrate at the row-header version annotation); Appendix C Coherence pass verification (all sub-sections at v1.2 form; the v1.3 revision pass does not re-run coherence at v1.2 boundaries); Appendix D Pattern P2 final-segment monitoring observation.

**Changes inline.** Status block (Version line extended with v1.3 entry; Date line extended; Source-set updated D1 v1.1 → v1.2 + D6 v1.1 → v1.2; Entry authorization extended with F2-12 cascade Step 3 entry; Exit gate revised to F2-12 cascade Step 4). This Change-note (v1.2 → v1.3) section inserted after Change-note (v1.1 → v1.2). §3.1.1 D1 subsection: all six paragraphs (Synthesis, Constrained by, Decision summary, Rationale highlights, Operational implications, Engaged tensions) revised per v1.3 amendment table above. §3.4.1 D6 subsection: all six paragraphs revised per v1.3 amendment table above. §5.2.2 T-perm-2 Residual surface paragraph: F2-12 sub-scope (iii) closure status noted. §5.2.3 T-perm-3 Residual surface paragraph: F2-12 sub-scope (ii) closure status noted. §6.3.1 F2-12 subsection: status revised from 🔄 → ✅; routing + completion + coordination sections collapsed into closure summary. Appendix B ADR inventory rows D1 + D6 updated to v1.2. Closing footer updated to v1.3.

**Cross-cascade-step coordination.** ADD v1.3 produces three downstream effects:

| Downstream cascade step | Substrate consumed from ADD v1.3 |
|---|---|
| Step 4 — PRD v1.1 revision pass | §3.1.1 D1 v1.2 absorption + §3.4.1 D6 v1.2 absorption + §6.3.1 F2-12 CLOSED declaration; R-CP-04 + R-CP-07 + R-OD-* requirements absorb engine.replay_disposition attribute requirement, retry.* namespace requirement, dedup-algorithm requirement, per-attempt cost-attribution discipline |
| Step 5a — CP spec v1.3 revision pass | §3.1.1 D1 v1.2 + §6.3.1 F2-12 closure → C-CP-08 §8.4 affected-contract notation closes + C-CP-09 §9.1 engine.* declaration extends 3 → 4 attributes citing D1 v1.2 §1.1.1 |
| Step 5b — OD spec v1.3 revision pass | §3.4.1 D6 v1.2 + §6.3.1 F2-12 closure → C-OD-14 cost-attribution-per-span contract absorbs dedup algorithm + per-attempt cost discipline per D6 v1.2 §1.5 + §1.5.3 |

**F2-12 status.** ✅ CLOSED at ADD v1.3 filing. Sub-scope (i) closed at D1 v1.2 §1.1.1 + §1.1.2 (cascade Step 2a); sub-scopes (ii) + (iii) closed at D6 v1.2 §1.2 + §1.2.2 + §1.2.3 + §1.5 + §1.5.1–§1.5.3 (cascade Step 2b); cross-axis consolidation closed at this ADD v1.3 (cascade Step 3). Closure declaration deferred to `F2-12_Closure_Declaration.md` filed at cascade close (post-Step 6). The §6.3.1 carry-forward record at this ADD v1.3 records closure status; the cascade-close declaration records the formal `closure_pending false` flag transition for the F2-12 carry-forward.

## Scope and out-of-scope

[Preserved verbatim from v1.2.]

## Reading order

[Preserved verbatim from v1.2.]

## §1 Persona summary

[Preserved verbatim from v1.2.]

## §2 Foundational decisions

[All sub-sections §2.1–§2.5 preserved verbatim from v1.2.]

## §3 Derivative decisions

[§3 preamble preserved verbatim from v1.2.]

### §3.1 Control plane

[§3.1 preamble preserved verbatim from v1.2.]

#### §3.1.1 ADR-D1 — Specific durable-execution substrate: engine-class commitment with per-deployment-surface candidate mapping (v1.3 amendment absorbs D1 v1.2)

**Synthesis.** D1 closes the F3 deferral on "specific durable-execution substrate" by committing a **five-element engine-class taxonomy** (event-sourced-replay / save-point-checkpoint / pure-pattern-no-engine / reconciler-loop / WAL-segment) and a **per-deployment-surface candidate mapping** across local-development, self-hosted-server, and managed-cloud surfaces. Engine class is committed at D1; specific engine-within-class is deferred to deployment-surface-time per surface row of the §1.2 mapping table. The rationale anchors at Brainstorm_Synthesis_For_Phase_2 §6 pattern-vs-engine decoupling combined with Pattern Reference Catalog v1.0 §11.3.2 D1's nine candidate set plus seven production-pattern witnesses (langchain-ai/deepagents on LangGraph+checkpointer; humanlayer/agentcontrolplane on K8s CRDs; langgenius/dify self-hosted workflow engine; VoltAgent Workflow Engine; jonwiggins/optio K8s+Postgres+Redis self-hosted; humanlayer/12-factor-agents Factors 6+12; shareAI-lab/Kode-Agent seven-segment WAL resume). **At v1.2 (F2-12 sub-scope (i) closure), the engine-class taxonomy table extends with a sixth column `Replay-emission disposition` carrying the per-class `engine.replay_disposition` default value; the `engine.*` span attribute namespace extends from 3 → 4 attributes at D1 §1.1.1 with the new `engine.replay_disposition` attribute (5-value enum closed-mapped to `engine.class`); the per-engine-class replay-emission discipline is committed at new D1 §1.1.2; the F2 state-ledger entry shape extends with `original_trace_id` + `original_span_id` fields at D1 §1.1.2.2 to support trace-context durability under `deterministic_replay`.** The key consequence is that **the `engine.*` span attribute namespace is declared canonically at D1 §1.1.1** (4 attributes at v1.2: `engine.class`, `engine.event_history.tier`, `engine.event.id`, `engine.replay_disposition`) and ingested at D6 §1.2 — D6 reads from D1; D1 owns declaration.

**Constrained by.** F3 v1.1 capability-requirement floor (i)–(iv); F2 state-ledger entry shape `(action_id, idempotency_key, actor, response_hash, timestamp, prior_event_hash)` as the join substrate (extended at v1.2 D1 §1.1.2.2 with `original_trace_id` + `original_span_id` fields for trace-context durability); F1 manifest-default invocation discipline; persona §10.2 workload-class-dependent constraint; persona §9 [HIGH] local-development design-time surface; **F2-12 council deliberation output §4 sub-scope (i) C7 schema authority + C3 ledger extension + C5 fail-class durability + C11 TUI UX + C1 topology preservation invariants** (cascade Step 1).

**Decision summary.** D1 commits the engine-class taxonomy + per-deployment-surface candidate mapping; **at v1.2, D1 also commits the 4-attribute `engine.*` namespace + per-engine-class replay-emission discipline + F2 state-ledger entry shape extension for trace-context durability** (cite `ADR-D1_v1_2.md` §Decision + §1.1 + §1.1.1 + §1.1.2 + §1.2).

**Rationale highlights.** The five-element taxonomy partitions the candidate space by **failure-containment and lifecycle-ownership** rather than by vendor — every candidate inhabits exactly one class, and class is the harness-canonical discriminator at the routing layer. The per-deployment-surface mapping resolves the bridging-arc constraint (Persona §2) by enumerating which engine classes are reachable at each surface tier: local-development admits classes 1–3 + 5; self-hosted-server admits classes 1–4; managed-cloud admits class 1 with Anthropic / AWS / GCP / vendor candidates. **At v1.2, the per-engine-class replay-emission discipline at §1.1.2 commits that a uniform replay-emission policy across all five classes is incorrect: event-sourced-replay engines (Temporal/DBOS/Restate) require zero-span-re-emission under deterministic_replay because replay is deterministic re-read of the original execution; save-point-checkpoint engines (LangGraph) require new-span-re-emission under checkpoint_resume because the activity-level resumption is a genuinely new execution from the engine's perspective; pure-pattern-no-engine harnesses have no replay concept and ERROR on unexpected re-ingestion; reconciler-loop and WAL-segment engines re-emit per iteration / per consumption respectively.** The 5-value enum closed-mapping to engine.class encodes this per-class discipline as a stable observability attribute (cite `ADR-D1_v1_2.md` §Rationale (a)–(d) for full chain + v1.2 amendment trace).

**Operational implications.** D1 §1.1.1 declares the `engine.*` span attribute namespace (4 attributes at v1.2); D6 §1.2 inherits without re-declaration. **At v1.2, D6 §1.2 engine.* row updates from 3-attribute to 4-attribute citing D1 v1.2 §1.1.1 as canonical source; D6 §1.5 dedup algorithm consumes `engine.replay_disposition` as the per-class dedup discriminator; D6 §1.5.1 retry-attempt orthogonality composes `retry.attempt_number` × `engine.replay_disposition` as orthogonal dedup discriminators.** Cross-deployment trust-tier inheritance from managed-cloud event-sourced-replay engines (Temporal Cloud, Bedrock AgentCore, Vertex Agent Engine impose trust-tier-3 on sandbox isolation) flows to D2 by reference per `ADR-D1_v1_2.md` §Consequences (d). **F2-12 (replay-trace-emission contract) closure status: ✅ CLOSED at D1 v1.2 + D6 v1.2; see §6.3.1 closure declaration.**

**Engaged tensions.** D1 **DIRECT ENGAGE T-perm-3** at the D1-layer per-deployment-surface engine-class commitment shape (cite `ADR-D1_v1_2.md` §1.3 "D1-layer T-perm-3 resolution"; see §5.2.3). T-perm-2 F2-layer resolution stands; D1 carries T-perm-2 by reference only; **at v1.2, T-perm-2 surfaces at sub-scope (iii) trace-ingestion dedup composition (engaged at D6 v1.2; resolved via idempotency_key composition; see §5.2.2 residual surface).** T-perm-1 adjacency carry-forward to D2 by reference (managed-cloud event-sourced-replay engines impose trust-tier-3 requirement on D2 sandbox provider selection).

#### §3.1.2 ADR-D4 — Multi-agent topology: six-pattern taxonomy with workload-class × engine-class parametric commitments

[Preserved verbatim from v1.2.]

#### §3.1.3 ADR-D5 — HITL synchrony: four-response palette with synchrony class parametric on persona-tier × engine-class

[Preserved verbatim from v1.2.]

### §3.3 Action surface

[§3.3 preamble + §3.3.1 D2 + §3.3.2 D3 preserved verbatim from v1.2.]

### §3.4 Operational discipline

[§3.4 preamble preserved verbatim from v1.2.]

#### §3.4.1 ADR-D6 — Observability backend: per-deployment-surface × per-persona-tier with unified span schema ingestion contract (v1.3 amendment absorbs D6 v1.2)

**Synthesis.** D6 commits a **nine-component observability backend specification**: a **9-cell deployment-surface × persona-tier matrix** (one cell EXCLUDED — multi-tenant-compliance × local-development) committing per-cell backend class + provider candidate(s) + sampling discipline + redaction posture + trace storage tier (per C3 five-tier durability) + cost-attribution dashboard binding + operator-burden eval primitive dashboard binding + local-first OTLP collector composition; a **unified span schema ingestion contract** assembling D2 §1.7 + D3 §1.8 + D4 §1.9 + D5 §1.8 + F3 v1.1 capability-floor (iv) + OTel GenAI semconv 1.41.0 [HIGH] base schema across additive namespaces; **sampling discipline**; **redaction discipline**; **cost-attribution-per-span dashboarding contract**; **operator-burden eval primitive dashboard binding**; **local-first OTLP collector commitment**; **multi-tenant tenant-isolation**; and a **cell-selection contract**. Observability backend class is committed at D6 per cell; specific provider candidate-within-class is deferred to deployment-surface-time × persona-tier-binding-time per §1.9. The v1.1 revision materialized the synthesis half of Pattern P1 by absorbing ten iter-1 partial-resolved findings + four iter-1 not-resolved findings. **At v1.2 (F2-12 sub-scopes (ii) + (iii) closure), D6 §1.2 engine.* row updates from 3-attribute to 4-attribute citing D1 v1.2 §1.1.1; the §1.2 specialization-layer table adds a new `retry.*` namespace row (was 0 attributes at v1.1; retry.attempt was lifecycle event only); §1.2 lifecycle event set retry.attempt terminology corrects "sibling" to "child-per-attempt"; new §1.2.2 declares the 6-attribute retry-attempt child span schema + 3-field parent-span retry.attempt event schema; new §1.2.3 declares sub-agent boundary composition under retry; §1.5 cost-attribution-per-span amends with dedup algorithm specification; new §1.5.1 declares replay-aware dedup with retry orthogonality; new §1.5.2 declares cause_attribution invariance check at deterministic_replay; new §1.5.3 declares per-attempt cost-attribution discipline.**

**Constrained by.** F3 v1.1 capability-floor (iv) observable lifecycle as base ingestion contract; F2 state-ledger entry shape (extended at v1.2 with `original_trace_id` + `original_span_id` per D1 v1.2 §1.1.2.2); **D1 v1.2 §1.1 engine-class taxonomy + §1.1.1 4-attribute `engine.*` namespace (D6 reads at v1.2; D1 v1.2 owns declaration) + §1.1.2 per-engine-class replay-emission discipline (D6 §1.5 dedup algorithm consumes as discriminator) + §1.1.2.2 F2 state-ledger entry shape extension (D6 §1.5 dedup lookup consumes)**; D2 §1.7 sandbox-bounded span schema + §1.7.1 `sandbox.*` namespace; D3 §1.8 per-Anthropic-primitive span attribute schema + §1.8.1 six namespace declarations; D4 §1.9 multi-agent span hierarchy + §1.10 cross-sibling audit-ledger merkle-root; D5 §1.4 per-persona-tier ledger cryptographic shape + §1.4.1 `audit.*` seven attributes + §1.8 `hitl.*` four distinct events + §1.10.1 `validator.fail.*` three-attribute joint declaration; OTel GenAI semconv 1.41.0 [HIGH]; persona §10.2 cost-attribution-per-span + §10.4 compliance-readiness foundational primitive; **F2-12 council deliberation output §5 + §6 (cascade Step 1 substrate for sub-scopes (iii) + (ii) resolutions)**.

**Decision summary.** D6 commits the 9-cell matrix + unified span schema ingestion contract + sampling discipline + redaction discipline + cost-attribution dashboarding + operator-burden eval dashboard binding + local-first OTLP collector + multi-tenant tenant-isolation + cell-selection contract; **at v1.2, D6 commits the engine.* 4-attribute row update + retry.* 6-attribute namespace + sub-agent boundary under retry composition + trace-ingestion dedup algorithm with replay-aware orthogonality + cause_attribution invariance check + per-attempt cost-attribution discipline** (cite `ADR-D6_v1_2.md` §Decision + §§1.1–1.9 + §1.2.1 + §1.2.2 + §1.2.3 + §1.5.1–§1.5.3).

**Rationale highlights.** The 9-cell matrix resolves the deployment-surface × persona-tier matrix at the observability axis without coupling to specific provider candidates. The unified span schema ingestion contract makes D6 the **single integration surface** for all other D-ADRs' span attribute declarations. **At v1.2, D6 §1.2 declares 16 specialization-layer rows** (was 15 at v1.1; +1 row added for `retry.*` namespace): `anthropic.*`, `mcp.*`, `skill.*`, `managed_agents.*`, `sandbox.*`, `hitl.*`, `topology.fanout.*`, `subagent.*`, `engine.*` (4 attributes at v1.2; was 3 at v1.1), `audit.*`, `validator.fail.*`, `files.*`, `memory.*`, `harness.breaker.*`, `retry.*` (6 attributes at v1.2; new), `provider_discriminator`. **The retry.* namespace declaration at §1.2.2 commits BOTH event AND span discipline: each retry emits a `retry.attempt` event on the parent operation span (3-field event schema: `parent.attempt_count`, `parent.attempts_remaining`, `parent.next_delay_ms`) AND a new child span representing the retry-attempt execution (6-attribute span schema: `retry.attempt_number`, `retry.original_span_id`, `retry.delay_ms`, `retry.cause_attribution`, `retry.fail_class`, `engine.replay_disposition`). The terminology correction from v1.1 (`sibling` → `child-per-attempt`) reflects C1's topology authority per F2-12 council §6.3 (retry attempts are children of the parent operation; attempts are siblings to each other under that parent).** **The trace-ingestion dedup algorithm at §1.5 discriminates per-class via `engine.replay_disposition`: `deterministic_replay` DROPs idempotent re-reads (zero additional cost accrual); `checkpoint_resume` / `reconciler_iteration` / `wal_consume` RECORD new replay-derived spans; `no_replay` ERRORs on unexpected re-ingestion. The cause_attribution invariance check at §1.5.2 detects replay-contract violations by comparing replayed span's cause_attribution against the F2 state-ledger entry's stored cause_attribution; mismatch ESCALATES to terminal-fail-exit with `replay_semantic_divergence` cause_attribution.**

**Operational implications.** D6 §1.2 namespace map is the canonical ingestion-contract table — every span attribute the harness emits at runtime sits in exactly one of the 16 namespace rows (was 15 at v1.1); every row cites its declaring D-ADR's §1.x source section. **At v1.2, the engine.* row Source column cites D1 v1.2 §1.1.1 (was D1 v1.1 §1.1.1 at v1.1); the retry.* row cites `c9-reliability-recovery` SKILL.md primary anchor with D1 v1.2 §1.1.2 composition context.** D6 §1.2.1 `harness.breaker.*` seven-attribute breaker-trip event schema is the F2-16 closure. D6 §1.2.2 retry.* namespace is the F2-12 sub-scope (ii) closure. D6 §1.5 cost formula amends at v1.2 with dedup algorithm specification per F2-12 sub-scope (iii) closure; per-attempt cost-attribution at §1.5.3 ensures cost accrues per attempt without aggregation across attempts. D6 §1.7 OTLP collector boundary commits the within-turn / across-turn seam at all nine cells.

**Engaged tensions.** T-perm-1, T-perm-2, T-perm-3 are all engaged at D6. **At v1.2, T-perm-2 (C2↔C3 within-turn-vs-durable) engages at sub-scope (iii) trace-ingestion dedup composition** — within-turn span emission (C7 territory; OTel SDK) composes with across-turn durable F2 state-ledger storage (C3 territory) via `idempotency_key` composition contract; reconciled without re-litigation of the F2-layer resolution (see §5.2.2 residual surface). **At v1.2, T-perm-3 (C1↔C9 control-flow-vs-reliability) engages at sub-scope (ii) retry.attempt parent-child topology seam** — retry attempts as children of parent operation; sub-agent boundary composition under retry; `topology_fault_handling` honored at default `pre-declared-with-allowlist` (see §5.2.3 residual surface). D6 inherits the locked tunable `per_tool_gate_level × per_mcp_server_trust_tier × persona_tier × blast_radius_tier × sandbox_tier` for T-perm-1; no D6-layer revision.

---

## §5 Cross-axis integration

[§5 preamble + §5.1 Resolved tensions preserved verbatim from v1.2.]

### §5.2 Permanent tensions accepted

[§5.2 preamble preserved verbatim from v1.2.]

#### §5.2.1 T-perm-1 (C4 ↔ C10 — capability vs gating)

[Preserved verbatim from v1.2.]

#### §5.2.2 T-perm-2 (C2 ↔ C3 — within-turn vs across-turn)

[v1.2 content preserved verbatim except Residual surface paragraph; v1.3 amendment to Residual surface only:]

**Residual surface (v1.3 amendment).** F2-layer resolution stands per F3 v1.1 §References explicit framing; D6 inherits at the OTLP collector boundary as the within-turn / across-turn seam. **At v1.3 (post-F2-12 cascade Step 3), T-perm-2 surfaces at F2-12 sub-scope (iii) trace-ingestion dedup composition: within-turn span emission (C7 territory, OTel SDK in-process) composes with across-turn durable F2 state-ledger storage (C3 territory, Tier 5 ledger with hash-chain integrity per `c10-action-safety` + `c11-operator-local` SKILL substrate) via `idempotency_key` composition contract. The composition is the resolution: within-turn emission populates ledger; replay recovers from ledger; D6 v1.2 §1.5 dedup algorithm enforces consistency. Status: ENGAGED at F2-12 sub-scope (iii) per cascade Step 1 council §7.2; reconciled via idempotency_key composition without re-litigation of the F2-layer resolution; ledger-reference-only carry-forward preserved.** F2-12 closure (cascade Step 3) does NOT re-open T-perm-2; the permanent tension is preserved at Layer 3.

#### §5.2.3 T-perm-3 (C1 ↔ C9 — control-flow vs reliability)

[v1.2 content preserved verbatim except Residual surface paragraph; v1.3 amendment to Residual surface only:]

**Residual surface (v1.3 amendment).** F1-layer (per-layer time-budget shape per `ADR-F1.md` §Decision) + D1-layer (`topology_fault_handling` per-deployment-surface mapping per `ADR-D1.md` §1.3) + D4-layer (`topology_fault_handling × workload_class × topology_pattern` per `ADR-D4.md` §1.6) resolutions stand. **At v1.3 (post-F2-12 cascade Step 3), T-perm-3 surfaces at F2-12 sub-scope (ii) `retry.attempt` parent-child topology seam: retry attempts are CHILDREN of the parent operation span per C1's topology authority (council §6.3); sub-agent spans under retry are children of the retry-attempt-span, NOT of the original parent operation (per ADR-D6 v1.2 §1.2.3 per-attempt isolation invariance); `topology_fault_handling` honored at default `pre-declared-with-allowlist` per the D1-layer tunable's locked default. Status: ENGAGED at F2-12 sub-scope (ii) per cascade Step 1 council §7.1; honored at default; no D6-layer or D1-layer revision; ledger-reference-only carry-forward preserved.** F2-12 closure (cascade Step 3) does NOT re-open T-perm-3; the permanent tension is preserved at Layer 3.

### §5.3 Cross-cutting properties

[All sub-sections §5.3.1–§5.3.3 preserved verbatim from v1.2.]

### §5.4 Pattern P2 in-flight monitoring observation during Segment 4 §5 authoring

[Preserved verbatim from v1.2.]

---

## §6 Open items and deferrals

[§6.1 + §6.2 preserved verbatim from v1.2.]

### §6.3 Carry-forward monitoring

#### §6.3.1 F2-12 — D1 v1.1 → v1.2 + D6 v1.1 → v1.2 replay-trace-emission contract (✅ CLOSED at v1.3)

**Status (v1.3 amendment).** ✅ **CLOSED** at ADD v1.3 filing. F2-12 cascade execution path closed at cascade Step 3 (this ADD consolidation); formal `closure_pending false` declaration deferred to `F2-12_Closure_Declaration.md` filed at cascade close (post-Step 6 plan v2.2 filings). The v1.0 → v1.2 status was 🔄 Deferred-acknowledged carry-forward; v1.3 transitions to ✅ CLOSED.

**Scope (preserved verbatim from v1.2).** D1 v1.1 → v1.2 replay-trace-emission contract: (i) span re-emission semantics under engine replay; (ii) `retry.attempt` sibling-span discipline; (iii) trace-ingestion dedup composition with F2 `idempotency_key`.

**Closure execution path (v1.3 amendment replacing v1.2 Routing + Coordination shapes + Completion forecast sections).**

| Cascade step | Artifact | Sub-scope closed |
|---|---|---|
| 1 — Council deliberation | `F2-12_Council_Deliberation_Output.md` (filed 2026-05-14; full 6-voice convening per OD-F212-2.A: C7 + C9 primaries; C3, C5, C1, C11 consultants; sequential (i) → (iii) → (ii) sub-scope ordering per OD-F212-3.C) | Substantive resolution substrate for all three sub-scopes |
| 2a — ADR-D1 revision | `ADR-D1_v1_2.md` (filed 2026-05-14; `spec-writer` SKILL.md council-formalization sub-mode) | (i) span re-emission semantics: 3 → 4 attribute `engine.*` namespace with new `engine.replay_disposition` enum at §1.1.1; per-engine-class replay-emission discipline at new §1.1.2; F2 state-ledger entry shape extension at §1.1.2.2 |
| 2b — ADR-D6 revision | `ADR-D6_v1_2.md` (filed 2026-05-14; `spec-writer` SKILL.md council-formalization sub-mode) | (ii) retry.attempt sibling-span discipline: terminology correction + 6-attribute retry-attempt child span schema at new §1.2.2 + sub-agent boundary under retry at new §1.2.3; (iii) trace-ingestion dedup composition: dedup algorithm at §1.5 + replay-aware retry orthogonality at §1.5.1 + cause_attribution invariance check at §1.5.2 + per-attempt cost-attribution at §1.5.3 |
| 3 — ADD consolidation | `Architectural_Design_Document_v1_3.md` (this artifact; `systems-architect` SKILL.md ADD-consolidation sub-mode) | Cross-axis consolidation; §3.1.1 D1 absorption + §3.4.1 D6 absorption + §5.2.2 T-perm-2 update + §5.2.3 T-perm-3 update + this §6.3.1 closure declaration |
| 4 — PRD revision (pending) | `PRD_v1_1.md` (next cascade step; `prd-author` SKILL.md revision-pass sub-mode) | R-CP-04 + R-CP-07 + R-OD-* requirements absorb engine.replay_disposition + retry.* + dedup algorithm + per-attempt cost-attribution |
| 5a — CP spec revision (pending) | `Spec_Control_Plane_v1_3.md` (cascade Step 5a; `spec-writer` SKILL.md §12 spec-revision-pass sub-mode) | C-CP-08 §8.4 affected-contract notation closes; C-CP-09 §9.1 4-attribute engine.* declaration |
| 5b — OD spec revision (pending) | `Spec_Operational_Discipline_v1_3.md` (cascade Step 5b; `spec-writer` SKILL.md §12 spec-revision-pass sub-mode) | C-OD-14 cost-attribution-per-span contract amends with dedup algorithm + per-attempt cost discipline |
| 6a — CP plan revision (pending) | `Implementation_Plan_Control_Plane_v2_2.md` (cascade Step 6a; `implementation-planner` SKILL.md §8 revision-pass sub-mode) | U-CP-20 acceptance #5 carry-forward declaration revised to closure; U-CP-21 engine.* namespace 4-attribute; U-CP-55 §24.4 export manifest update |
| 6b — OD plan revision (pending) | `Implementation_Plan_Operational_Discipline_v2_2.md` (cascade Step 6b; `implementation-planner` SKILL.md §8 revision-pass sub-mode) | U-OD-20 closure_path closure status revised; U-OD-14 cost-attribution-per-span unit update |
| Close | `F2-12_Closure_Declaration.md` (cascade close) | Formal `closure_pending false` declaration; per-sub-scope resolution summary; cascade-artifact inventory |

**Workflow discipline.** Cascade authored under `Project_Workflow_v1_7.md` §7 fidelity-grammar discipline (Path δ revision; in force post-Path-δ-closure 2026-05-14). All cascade-step artifacts apply Pattern P1 (cross-artifact name drift) prevention and Pattern P2 (verbatim-claim-contradicted) prevention disciplines.

**Cross-tension status at closure.** T-perm-2 (C2↔C3 via C7) ENGAGED at sub-scope (iii); reconciled via idempotency_key composition contract; permanent tension preserved at Layer 3 without re-litigation (see §5.2.2). T-perm-3 (C1↔C9) ENGAGED at sub-scope (ii); honored at default `pre-declared-with-allowlist`; permanent tension preserved at Layer 3 without re-litigation (see §5.2.3). T-perm-1 (C4↔C10) NOT actively engaged at F2-12 scope (conditional engagement per kickoff §4.3 did not fire).

**Impact on ADD v1.3.** D1 v1.2 + D6 v1.2 substantive amendments absorbed at §3.1.1 + §3.4.1 + §5.2.2 + §5.2.3 + this §6.3.1. No new tensions surfaced; no other ADD sub-sections affected; §3.1.2 D4, §3.1.3 D5, §3.3.1 D2, §3.3.2 D3 carry no F2-12 closure impact (their substrate citations to D1/D6 reference v1.1 at v1.2 form; v1.3 does not retro-edit those citations because the cited content at v1.1 is preserved at v1.2 except where v1.2 amendments explicitly engage — which they do not at D4/D5/D2/D3 surfaces).

#### §6.3.2 Pattern P2 monitoring — cross-D-ADR composition-contract under-specification (per OD-4.A)

[Preserved verbatim from v1.2.]

---

## Appendix A — Traceability matrix

[Preserved verbatim from v1.2; the v1.3 amendment to §3.1.1 D1 + §3.4.1 D6 + §5.2.2 T-perm-2 + §5.2.3 T-perm-3 + §6.3.1 F2-12 does not introduce new ADR rows or remove existing ones; all v1.2 cell marks preserved. The ADR row-header version annotations for D1 + D6 are updated from v1.1 → v1.2 at the row label per v1.3 amendment; matrix body unchanged.]

## Appendix B — ADR inventory table

[v1.2 entries preserved verbatim except D1 + D6 version rows:]

| ADR | v1.2 entry | v1.3 entry |
|---|---|---|
| ADR-D1 | v1.1 (Accepted) | **v1.2 (Proposed; F2-12 cascade Step 2a)** |
| ADR-D6 | v1.1 (Accepted) | **v1.2 (Proposed; F2-12 cascade Step 2b)** |

All other ADR entries preserved verbatim from v1.2.

## Appendix C — Step 5 coherence pass verification (v1.1 upgrade per Workflow v1.4 §2.3.5 clause (iv))

[All sub-sections C.1–C.8 + Coherence pass disposition preserved verbatim from v1.2. The v1.3 revision pass is a cascade-driven absorption pass and does not re-run the v1.1+ coherence pass at v1.2 boundaries; v1.3 coherence verification is performed inline at the v1.3 amendment sites per Workflow v1.7 §7 fidelity-grammar discipline.]

## Appendix D — Pattern P2 final-segment monitoring observation (per OD-4.A)

[Preserved verbatim from v1.2.]

---

## Filing footer

| Field | Value |
|---|---|
| Artifact | `Architectural_Design_Document_v1_3.md` |
| Filing destination | `/mnt/user-data/outputs/Architectural_Design_Document_v1_3.md` |
| Status | Proposed (pending F2-12 cascade close per cascade Step 6 plan v2.2 filings) |
| Predecessor | `Architectural_Design_Document_v1.md` (v1.0 → v1.1 → v1.2 baseline); `ADR-D1_v1_2.md` + `ADR-D6_v1_2.md` (cascade Step 2 substrate) |
| Successor | `PRD_v1_1.md` (F2-12 cascade Step 4; `prd-author` SKILL.md revision-pass sub-mode) |
| F2-12 closure status | ✅ CLOSED at cascade Step 3 (this artifact); formal closure_pending false declaration deferred to `F2-12_Closure_Declaration.md` at cascade close |
| Workflow discipline | `Project_Workflow_v1_7.md` §7 fidelity-grammar |
| Date | 2026-05-14 |

*Filed at F2-12 cascade Step 3 close. D1 v1.2 + D6 v1.2 cross-axis consolidation absorbed; §6.3.1 F2-12 active-path carry-forward closed; T-perm-2 + T-perm-3 ENGAGED-at-sub-scope status declared with permanent-tension preservation at Layer 3. Cascade segment boundary per OD-F212-4.A. Recommended next cascade step: Step 4 (PRD v1.1 revision pass per `F2-12_Closure_Path_Execution_Kickoff.md` §3.2) — R-CP-04 + R-CP-07 + R-OD-* requirements absorption against this ADD v1.3.*
