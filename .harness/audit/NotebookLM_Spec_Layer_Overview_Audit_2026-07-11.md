# NotebookLM Spec-Layer Overviews vs As-Built Codebase — Completeness Audit — 2026-07-11

**Posture:** mode-agnostic / process-substrate (reads `.harness/**`, `design-substrate/**`, `harness-*/src`; edits nothing in either). Read-only assessment; no code implemented.

**Against HEAD:** `e6664f74` (clean tree, no open PRs; post-#933, `rfs1_status: resolved`, registered `B-*` queue empty).

**Question posed (operator, 2026-07-11):** the nine NotebookLM-generated summaries at `.harness/01-planning/01-harness-planning/00-harness-research/02-notebooklm-queries/00-harness-spec-layers-overviews/` (files `01-context-engineering.md` … `09-prompts-skills-workflows-agents.md`, generated from the notebook holding the original research + specification corpus) enumerate features "expected to be built." Compare each surfaced feature against the codebase: implemented completely, partially, not at all, or modified during the development arc.

**Relation to the two prior audits.** This is a **third lens** over the same corpus, complementary to:

- `Spec_Implementation_Gap_Audit_2026-07-09.md` (PR #916) — spec→code **presence**: 432 head contracts/units, 0 designed-but-unbuilt gaps.
- `Upstream_Decomposition_Audit_2026-07-09.md` (PR #918) — intent→spec **decomposition**: 0 silent narrowings, 12 documented deferrals.

This audit runs **research-era summary → as-built**. Its distinctive value is the reverse direction: NotebookLM summarizes the corpus *as it read at research/spec time*, so divergences surface (a) features that evolved during the build, (b) research material never committed, and (c) summary mis-attributions. Its verdicts are consistent with both prior audits everywhere they overlap (see §6).

**Method.** (1) All nine files read in full (~80 discrete claims deduplicated). (2) Five parallel read-only sweep agents verified claims per axis (IS / AS / CP / OD-evals / runtime-context) against `design-substrate/**` (delta-chain-aware, archive excluded), `harness-*/src`, and the `01-planning` research corpus. (3) Per the workspace re-grounding discipline, **~20 load-bearing or audit-conflicting sweep verdicts were re-verified by direct read** — 14 were corrected (see §5 scope-honesty; the sweep is presence-not-correctness). (4) Statuses of tracked deferrals re-grounded against `.harness/arc-ledger.yaml`, `.harness/post-phase-8-forward-register.md`, and the in-code `harness_od/deferral_envelope.py` registry. Prompting NotebookLM itself was **not needed**: the notebook's sources live in-repo, so every `[nnn]`-cited claim resolved locally against the research corpus + specs.

**Verdict vocabulary.**

| Verdict | Meaning |
|---|---|
| **BUILT** | Production code implements the claim substantially as described (code cite). |
| **BUILT-MODIFIED** | The capability exists; the as-built mechanism differs materially from the summary's description (delta stated). |
| **PARTIAL** | An identifiable half is built, an identifiable half is not. |
| **SPEC-DEFERRED** | Committed in the authority chain, no production code — and the deferral is *acknowledged* (fork / register / spec-OQ / in-code deferral envelope). |
| **RESEARCH-ONLY** | Lives in the `01-planning` research corpus (or is an H_E/Claude-Code feature described there); never committed by ADR/spec; no code. Not a gap — never promised. |
| **ABSENT** | In neither specs, research framing that was adopted, nor code. |

---

## 1. Headline

Across ~80 deduplicated claims (≈98 table rows including cross-references): **≈45 BUILT, ≈16 BUILT-MODIFIED, 7 PARTIAL, ≈4 SPEC-DEFERRED, ≈12 RESEARCH-ONLY, 3 ABSENT** (per-file tables below are authoritative; several claims span categories and are counted once at the dominant verdict; the BUILT ↔ BUILT-MODIFIED boundary is judgment-loaded on a handful of rows).

Three top-level conclusions:

1. **The spec'd core is built.** Every load-bearing contract family the summaries describe — five-tier layering, six-field hash-chained ledger, sandbox tiers with real drivers, HITL gate/rewrite, routing layers, breaker/fallback, engine taxonomy with five live substrates, the 15-row namespace map, cost engine, eval primitives, memory tool, Files API — has verified production code. This is consistent with #916's zero-gap result at the granularity #916 measured (contract/unit keyspace), with one ADR-prose-level refinement surfaced at §4 item 1 / §6.
2. **The summaries' single biggest error mode is presenting research-corpus material as spec commitments.** ~12 claims (XGrammar/Outlines, code-execution-with-MCP, MicroCompact/AutoCompact tiers, named markdown personas, Meta-Harness outer loop, Zheng judge-bias protocol numbers, κ/TPR/TNR gates, token-count targets, docs-over-outputs, skill self-evolution) trace only to `01-planning` research files — several describe **H_E (Claude Code) features** the research documented, or framework pulls the workspace's I-6 discipline explicitly forecloses. These are not gaps.
3. **The genuinely open surface this lens finds is small and almost entirely already-acknowledged** (§4): the boot-time cache pre-warm + keep-alive halves of ADR-D3 §1.5 (explicitly deferred, currently unregistered), the C-OD-19 TUI trace browser bundle (formally registered in the in-code deferral envelope), the ADR-D5 two-row rotation runtime sliver, `tool_search` runtime realization, plus the known discretionary/optional items (B-19 breaker attrs, B-18-LANEB prompt semver, B-13 managed-DB live proof, managed-cloud hold).

---

## 2. Per-file classification

### 2.1 File 01 — Context Engineering

| # | Claim (as summarized) | Verdict | Evidence / delta |
|---|---|---|---|
| 1 | Five-tier artifact layering `C-IS-02` (working/episodic/semantic/procedural/durable) | **BUILT** | Tiers verbatim at `Spec_Information_Substrate_v1.md:268-274`; carried in `harness_is/state_ledger_entry_schema.py:95-132`. |
| 2 | "Selective section routing (`C-IS-10`)" via stage `CONTEXT.md` Inputs tables | **RESEARCH-ONLY + mis-attributed ID** | C-IS-10 is actually "Substrate seam exports surface" (`Spec_Information_Substrate_v1.md:765-843`). The CONTEXT.md-Inputs-table mechanism is ICM-methodology vocabulary from the research corpus (`Pattern_Reference_Catalog_v1.0.md`). Nearest as-built relative: the C2-pole *selective bounded read* contract (C-IS-07 §7.2) + `LedgerNavigationPrimitive` — BUILT, but a different mechanism at a different layer. |
| 3 | XML structured-event message encoding | **ABSENT** (research-only) | No XML event-tag encoding in prompt assembly; the runtime uses typed Pydantic event records. Research provenance: cluster-2 context/prompts file. |
| 4a | Static-prefix/dynamic-suffix + `cache_control` breakpoints (up to 4 segments) | **BUILT-MODIFIED** | As-built (B-18 slices 1–2, runtime spec v1.94–v1.95): ONE authored breakpoint at the end of the `[tools + system]` prefix via structured system content (`lifecycle/llm_dispatch.py`), not a 4-segment stack. ADR-D3 §1.5 commits **two** breakpoint layers (parent-agent + per-sub-agent-role); "4" is the Anthropic API ceiling, not the design. |
| 4b | Cache TTL discipline | **BUILT** | Workload-class TTL 5m/1h (`RuntimeConfig.prompt_cache_long_ttl_workloads`, `RuntimeLLMDispatcher.cache_ttl`; B-18 slice 3b, runtime v1.97), values exactly as ADR-D3 §1.5:188 commits. |
| 4c | Pre-warm: `max_tokens: 0` at boot + 4-min keep-alive | **SPEC-DEFERRED** (open) | ADR-D3 §1.5:189-190 commits both. As-built warm-up is the **fan-out cohort** protocol instead (ADR-D4 §1.8; B-18-3C-PREWARM family through #933) — and modified even there: awaits `branch[0]` **completion**, since no cache-ack signal exists on the real API. Boot-time pre-warm + keep-alive were explicitly deferred at `.harness/u1-slice3b-epoch-partition-design.md` §5 ("opt-in, default off" named for when built) — see §4 item 1. |
| 4d | Tool-set freezing | **BUILT-MODIFIED** | As-built: `frozen_tool_superset` computed per cacheable epoch (`lifecycle/frozen_tool_superset.py`) + child-scoped downgrade (slice 3a, CP v1.86 `sub_agent_descent`) — the ADR-D3 §1.5 discipline. NOT the research shape (tools array collapsed to bash/read via code-execution-with-MCP — that is RESEARCH-ONLY, §2.3 #8). |
| 5a | Multi-tier compaction (MicroCompact / AutoCompact 95-98% / Full / `/compact`) | **RESEARCH-ONLY** | These are H_E (Claude Code) features the research documented. The harness's own surface is the memory-substrate compaction-safety dispositions (`memory_compaction_safety.py`: DISCARD/KEEP_EPISODIC/PROMOTE/QUEUE) — a different mechanism for a different problem. |
| 5b | Server-side selective clearing (`clear_tool_uses_20250919`, `clear_thinking_20251015`) | **PARTIAL** | `clear_tool_uses_20250919` IS handled: `lifecycle/memory_tool_dispatch.py:114-147` processes `context_management` edits with the memory-tool exclusion; `harness_as` attr schema tracks it. `clear_thinking_20251015` not found anywhere. |
| 5c | Pre-compaction constraint dump to `NOTES.md` | **ABSENT** (research-only) | As-built durability answer is the memory substrate (promotion/capture), not a NOTES.md convention. |
| 6 | HITL-resume context revalidation (`C-CP-22` `material_diff`) | **BUILT** | `harness_cp/material_diff_detection.py` (`MaterialDiff`, `detect_material_diff()`); contract ID accurate. |
| 7 | JIT retrieval convention (paths-only prompts; glob/grep navigation) | **RESEARCH-ONLY / convention** | Stated in Persona/research framing; no (and plausibly should be no) runtime enforcement surface. |
| 8 | Four-field sub-agent Brief (`C-CP-13/14`) with 1–2k token condensed return | **BUILT-MODIFIED** | `harness_cp/sub_agent_brief.py:65-86`: `objective`, `output_format` (OutputSchema), `guidance` (not `tool_guidance`), `task_boundaries` (in/out-of-scope + termination criteria) + plan-added `summary_hash`. The "task() tool" wrapper and token numbers are research framing. |
| 9 | Docs-over-outputs invariant | **RESEARCH-ONLY** | Only in research corpus; no spec contract or code. |

### 2.2 File 02 — State / Memory / Persistence

| # | Claim | Verdict | Evidence / delta |
|---|---|---|---|
| 1 | Dual-mode state record (git commit stream + JSONL event ledger) | **BUILT** | C-IS-01/C-IS-03; `state_ledger_write.py`, `jsonl_event_ledger_lifecycle.py`; `state.jsonl` path-class. |
| 2 | Six-field record `C-IS-05` (action_id, idempotency_key, actor, response_hash, timestamp, prior_event_hash) | **BUILT** (verbatim) | `state_ledger_entry_schema.py:123-128` — field names exact. |
| 3 | C3-pole write / C2-pole read seam contracts | **BUILT** | C-IS-07 §7.1/§7.2; write keyed `(thread_id, step_id, idempotency_key)` (nuance: v1.4 §7.5 ratified thread/step as write-time args, idempotency_key the sole persisted discriminator). |
| 4 | RFC 8785 JCS + SHA-256 chaining + operator verification | **BUILT-MODIFIED** | `entry_hash.py`: hand-rolled NFC + sorted-keys canonicalization, RFC-8785-conformant *for the entry shape* (no floats); the spec's "[MODERATE — confirm at D-ADR]" never became a library pull (I-6-consistent). `chain_verification.py:verify_chain` + `harness-inspect` CLI give the verification surface. |
| 5 | Persona-tier audit crypto (`C-CP-20`→OD): SQLite append-only → hash-chained → signed (ed25519/ecdsa-p256/rsa-pss-2048) + two-row rotation | **BUILT minus one sliver** | 3-algorithm set verbatim + `audit.signature.*` 4-attr set at `harness_od/audit_ledger_types.py:56-99`; `sign_audit_entry` (`multi_tenant_trace_separation_and_audit_ledger.py:177`) + `verify_hash_chain_integrity` (`:211`). The **two-row rotation dual-signature pattern** (ADR-D5 v1.3 §1.4, `rotation_correlation_id`) is committed in the ADR + sqlite schema prose but no runtime rotation-pair signer was located → §4 item 3. |
| 6 | Structure-not-content (`outputs_hash` fingerprints) | **BUILT** | `harness_as/secret_outputs_hash.py` (U-AS-25, C-AS-08 §8.1) + ledger `response_hash` + default-off content attrs (§2.6 #5). |
| 7 | Shadow-git checkpointing w/ cadence enum + atomic rollback | **BUILT-MODIFIED** | `harness_is/shadow_git_checkpoint.py` per C-IS-08; rollback writes a ledger record. The four-value **cadence enum is spec-deferred to implementation discretion** (IS spec §8 :713); as-built cadence is manifest-driven. |
| 8 | Git worktree isolation for siblings | **BUILT** | `worktree_isolation.py:128` (`git worktree add`), `:153` (`git worktree remove --force` inside `reclaim_worktree`, :139). |
| 9 | Five-element engine-class taxonomy + durable floor + `resumption.kind` | **BUILT** | `engine_class.py:23-53` + `resumption_kind.py:27-47`, both 5-member verbatim. **All five classes have live substrates** (pure-pattern journal; WAL-segment U-RT-121/U-CP-94-95; save-point; reconciler CAS-lease U-RT-123/U-CP-96-97; event-sourced-replay) per the R-FS-1 E-impl arcs. NOTE: the summary's "e.g. Temporal / LangGraph" examples are research color — those frameworks are **foreclosed by I-6**; every substrate is hand-rolled. |
| 10 | Files API (`files-api-2025-04-14`, file_id referencing) | **BUILT** | `lifecycle/files_api.py`; R-810 RESOLVED with live Anthropic upload/reference/delete + managed-cloud `files.operation` trace proof (forward register B-11). *(The IS-axis sweep initially mis-called this research-only; corrected by direct read.)* |
| 11 | Memory tool (`memory_20250818`, /memories, harness backend) | **BUILT** | C-MEM family (`Spec_Memory_Substrate_v1.md`) built as U-MEM-01..25 (PRs #855–#907); `memory_tool_executor.py` (31K, full executor), stores + retrieval + promotion; bootstrap-wired (stage-5, verified at #916). Production backends (SELF_HOSTED SQLite, S3 cloud-vault, provider-free managed-DB) done; **one operator-gated live managed-DB e2e pending** (forward register B-13). |
| 12 | Memory-tool exclusion from context editing | **BUILT** | `memory_tool_dispatch.py:114-147` — `clear_tool_uses_20250919` edits exclude `"memory"`. |
| 13 | Cross-sibling Merkle root (`sibling_ledger_root` in `parent_fanout_close_entry`) | **BUILT** | `harness_cp/parent_fanout_close_entry.py:53-85` per C-CP-15 §15.2–15.4. |

### 2.3 File 03 — Tools Integration

| # | Claim | Verdict | Evidence / delta |
|---|---|---|---|
| 1 | MCP as universal substrate (FastMCP, out-of-process) | **BUILT** | MCP host/client factories (`bootstrap/factories/mcp_client_host_factory.py`); real external stdio e2e green (R-800). |
| 2 | STDIO → tier-3-microvm minimum floor | **BUILT** | Enforced in code: `harness_as/sandbox_tier_floor.py:140-142`. *(Sweep initially said spec-only; corrected.)* |
| 3 | Remote MCP trust taxonomy + OAuth 2.1 / PKCE / RFC 8707 | **PARTIAL** | Trust taxonomy BUILT: `MCPTransport` 5-member fused transport/trust enum (`discriminators.py:31-43`: STDIO + STREAMABLE_HTTP L0_REFUSE/L1_PINNED/L2_SANDBOX/L3_AUDIT) with floor composition. OAuth-2.1-resource-server **validation enforcement code not located** [MODERATE — may be deliberately deployment-binding-time]. Do not confuse with the *external-CLI OAuth provider routing* (PR #914) — a different, built surface. |
| 4 | `mcp.primitive.signature.sha256` rug-pull audit gate | **PARTIAL** | Attribute declared in the namespace schema (`anthropic_attribute_namespaces.py:171`); a registration-time hash-verification *gate* was not located. |
| 5 | Skills per agentskills.io (SKILL.md + frontmatter constraints) | **PARTIAL** | Contracts + filesystem residence (`skills_loads_from_filesystem_path`, path-class) + activation telemetry BUILT; a production **frontmatter constraint validator** (name ≤64 etc.) was not located. |
| 6 | Three-level progressive disclosure "(C-AS-13)" | **BUILT-MODIFIED + mis-attributed ID** | C-AS-13 is actually the "Eleven-primitive Anthropic-adoption-depth matrix" (`anthropic_primitive_adoption.py`, U-AS-28). Progressive disclosure is realized as `skill.activation_mode ∈ {frontmatter_only, tool_search, filesystem_read}`; the ~100/5,000-token budgets are research prose, not enforced limits. |
| 7 | Tool Search Tool / `defer_loading` | **PARTIAL → SPEC-DEFERRED** | Committed in ADR-D3 §1.5 ("per-MCP capability discovery via `tool_search` rather than tools[] mutation") and modeled (activation mode; adoption matrix; C-RT-27 emitter handles the mode) — but no runtime tool-search dispatch mechanism landed; the frozen superset is the current realization. §4 item 4. |
| 8 | Code-execution-with-MCP (servers-as-files, bash/read-only tools array) | **RESEARCH-ONLY** | Anthropic-blog pattern in the research corpus; never spec-committed; no code. |
| 9 | Four-tier sandbox set `C-AS-01` | **BUILT** | `sandbox_tier.py:27-33` enum + **real drivers for all four tiers**: process, Docker (tier-2, R-410), gVisor/runsc (`GVisorRunscToolRunnerExecutionDriver`, factory `:64,:212` — R-411, Lima VM), E2B full-VM (tier-4, R-412). *(Sweep missed the gVisor driver; corrected.)* |
| 10 | `max()` tier composition + unconditional tier-4 escalations | **BUILT** | `sandbox_tier_composition.py:100-136`; forced escalations (LLM-generated code / untrusted remote MCP) live at the runtime dispatcher (runtime spec §14.9.11). |
| 11 | `minimum_tier` mandatory at registration | **BUILT** | `tool_contract.py:167-194` — MISSING_MINIMUM_TIER rejection. |
| 12 | Monotonic sub-agent tier ascension + policy_override violation | **BUILT** | `sub_agent_sandbox_tier.py:60-114`. |
| 13 | HITL rewrite trio (request_human_input / await_human_approval / escalate_to_human) | **BUILT** (names verbatim) | `harness_cp/hitl_as_tool_call_rewriting.py:54-112` + runtime placement registry. |
| 14 | `mcp.*` / `skill.*` / `sandbox.*` namespaces "(C-AS-14)" | **BUILT** | Within the 15-row map (§2.6 #3); C-AS-14 declares six AS namespaces (anthropic/mcp/skill/managed_agents/files/memory) + sandbox attrs at C-AS-04. |
| 15 | `skill.activation` span (id/name/body_tokens/version_sha) | **BUILT** | SKILL namespace schema (`anthropic_attribute_namespaces.py:181-212`, includes `skill.frontmatter.version`) + C-RT-27 emitter (`lifecycle/skill_activation.py`). |
| 16 | Skill "Self-Evolution" block | **RESEARCH-ONLY** | No spec/code trace. |
| 17 | `sandbox.fail.class` (7) + `secret.fail.class` (5) enums | **BUILT** (verbatim) | `sandbox_fail_class.py:31-40`, `secret_fail_class.py:33-41`. |

### 2.4 File 04 — Validation Contracts

| # | Claim | Verdict | Evidence / delta |
|---|---|---|---|
| 1 | Constrained decoding via XGrammar / Outlines | **RESEARCH-ONLY** (foreclosed) | Zero spec/code presence; the committed L1 is **Pydantic v2** + hand-rolled gates (I-6 / stack commitment) + the ADR-D3 §1.6 vendor structured-outputs adoption contract. |
| 2 | Tool contract without `minimum_tier` rejected | **BUILT** | §2.3 #11. |
| 3 | Idempotency-keyed write validation | **BUILT** | §2.2 #3. |
| 4 | 5-axis multiplicative `gate_level = max(...)` | **BUILT-MODIFIED** | `gate_level_rule.py:208-256`: max() composition over per-tool gate level, blast-radius tier, persona tier, MCP trust tier (via `MCP_TRUST_GATE_LEVEL_FLOOR` — the #918 T-5 deferral has since been realized). The 5th axis of the summary's list (sandbox-tier floor) composes at *tier* resolution, not gate level; `deployment_surface` was dropped at plan v2.20. Net: same contract intent, different axis bookkeeping. |
| 5 | Monotonic-ascension validation | **BUILT** | §2.3 #12. |
| 6 | Fail-class taxonomies (`sandbox.fail.class`, `secret.fail.class`) | **BUILT** | §2.3 #17. |
| 7 | Five-class `validator.fail.class` (transient-retry / Reflexion-recoverable / HITL-recoverable / permanent-fail-exit / terminal-fail-exit) | **BUILT** (verbatim) | `validator_fail_taxonomy.py:46-75` — member strings exact, C-CP-21 §21.1. A sibling cause-attribution enum (`ValidatorFailClass`: schema/semantic/safety/resource/external) coexists; the summary's taxonomy maps to the retry-exit enum. |
| 8 | Model-tier escalation on 2nd failure | **BUILT-MODIFIED** | Staircase is 5 stages verbatim (C-CP-21 §21.2, `validator_fail_transient_staircase.py:39-47`): Reflexion → retry-with-backoff → **cross-family-fallback** → local-terminal → HITL-escalation. Model-tier escalation exists as `MODEL_TIER_ESCALATION_CHAIN` (U-AS-30, C-AS-13 §13.4) composed into the fallback chain (`cross_family_fallback_chain.py:16,92`) — not a literal "2nd-consecutive-failure hot-swap" stair. |
| 9 | Asymmetric two-agent Verifier | **PARTIAL** | EVALUATOR_OPTIMIZER topology is a built first-class pattern (multi-evaluator cells guarded by the v1.96 item-9 tripwire); the specific "read-only, inputs-disabled parallel verifier" discipline is research framing. |
| 10 | Ledger + Merkle + multi-tenant signing integrity | **BUILT** (rotation sliver open) | §2.2 #4/#5/#13. |
| 11 | `gen_ai.eval.kind` inline_gate/offline_judge + separate child spans + alignment-floor drift | **BUILT** | C-OD-18 §18.3 / C-OD-17 §17.2; `eval_vs_runtime_gate.py`, `alignment_floor_drift_detection.py` (event `gen_ai.eval.alignment_floor.drift_detected`, 4 attrs, always-sampled). |
| 12 | Error-analysis-first calibration (Husain; κ against 100-trace gold set) | **PARTIAL / RESEARCH-ONLY numbers** | C-OD-17 §17.3 references the Husain loop against the ring-buffer; the **loop tooling + holdout-set construction are formally deferred** in the in-code deferral envelope (`deferral_envelope.py`, C-OD-17/§18 entries). The κ ≥ 0.7 / TPR/TNR numbers appear only in research. |

### 2.5 File 05 — Model Routing

| # | Claim | Verdict | Evidence / delta |
|---|---|---|---|
| 1 | CDF three-layer routing `C-CP-02` (manifest / embedding kNN / LLM-as-router) | **BUILT** | `routing_layer.py:38-52` (3-layer enum); L2/L3 built by Arc R (PRs #602/#606), **production-inert until the routing-activation gate + a second live provider** — an infra gate, not a build gap (#918 T-1). |
| 2 | Per-layer time budgets + deterministic fall-through | **BUILT** | LayerBudget + `RoutingDecisionTrace.budget_exhausted` (C-CP-03). |
| 3 | Role × model "temperament" bindings (Sonnet leads, Haiku workers, parallel caps) | **PARTIAL** | The per-role binding *surface* is built (B4: `WorkflowManifestEntry.agent_role:135`, `derive_agent_role`, folded to `StepExecutionContext.agent_role`; runtime-indexing exercised once a 2nd provider is standing). The specific model-name temperament table + parallel-instance caps are research color, not code. |
| 4 | Circuit breakers per {provider, model} + 7-attribute schema | **BUILT** | `harness_od/harness_breaker_schema.py:95-141` — 7 attrs verbatim. `breaker.cause` / `breaker.cooldown_ms` confirmed absent = the **known discretionary U-2/B-19** (a conscious v1→v1.1 design drop, per #918). |
| 5 | Cross-family fallback + provider-sticky keys + cache invalidation event | **BUILT** | `cross_family_fallback_chain.py:73-144` (`fallback.cross_family_triggered`, `cache_state_lost`, 4-family enum); exercised live Anthropic→OpenAI (#281) and Ollama (#283). |
| 6 | `routing.*` span attrs incl. `binding_rationale` | **BUILT** | Threaded at the dispatch wrapper (`llm_dispatch.py:124-142`, `retry_breaker_fallback.py:581`) per B-L2-ROUTING-SPAN-LAYER-ATTRIBUTION (#693). *(Sweep saw only the CP-internal trace type; corrected.)* |

### 2.6 File 06 — Observability

| # | Claim | Verdict | Evidence / delta |
|---|---|---|---|
| 1 | OTel GenAI semconv 1.41.0 pinning; span-name format; CLIENT kind | **BUILT** | OD spec v1.2 §4; `otel_genai_base.py:58-162` (9-operation enum, name format). |
| 2 | Span hierarchy + W3C propagation + conversation.id | **BUILT** | `multi_agent_span_hierarchy.py:61-100`; conversation.id on invoke_agent/chat only per semconv (cardinality-safe). |
| 3 | "Eleven-namespace export map (6+4+1)" | **BUILT-MODIFIED** | As-built: **15-row attribute-namespace ingestion map** (`namespace_map.py:105-204`, byte-exact vs OD spec §5.1): 7 AS-source (anthropic, mcp, skill, managed_agents, sandbox, files, memory) + 6 CP-source (hitl, topology.fanout, subagent, engine, audit, validator.fail) + harness.breaker + provider_discriminator. The summary's `fallback.*`/`retry.*`/`lease.*` are **F3 lifecycle event classes** (8, spec §5 :378-388) emitted as span events with CP-declared attr namespaces — not rows in the map; `routing.*` rides `llm.inference`. Lineage [MODERATE]: NotebookLM's 11 = the ADR-D6-era framing; root CLAUDE.md's "12" predates the three Anthropic-primitive additions (files, memory, managed_agents) → 15 today. CLAUDE.md §1.1 is stale on this count (fits the already-queued §2 pointer catch-up sweep). |
| 4 | Sampling: head local / tail prod + tail-keep-on-classification | **BUILT** | `composite_sampler.py`, `tail_keep_span_processor.py`; B-TAIL closed (PR #717); collector-side tail-keep proven live (R-430). |
| 5 | Always-sampled set | **BUILT** | `sampling_mode.py` carries the §9.2 **18-entry** set (the summary lists 9 of them). |
| 6 | Cardinality-safe discipline | **BUILT** | C-OD-11; e.g. `otel_genai_base.py:160-161` (span-attr-only annotations). |
| 7 | Structure-not-content default-off + pre-collector redaction | **BUILT** | Content attrs tiered OPT_IN (`otel_genai_base.py:196-206`); `RedactionSpanProcessor` wired at bootstrap stage-0 preamble (SDK-side, ahead of export batching); opaque-token audit (`redaction_token_audit.py`); per-session toggle + tokenization closed at R-008/OD-4. |
| 8 | Cost engine (formula, cache attribution, dedup) | **BUILT** | `cost_formula.py:8-13` — *more precise than the summary*: `(input − cache_read − cache_creation)×BASE_INPUT + cache_creation×1.25×BASE_INPUT + cache_read×0.10×BASE_INPUT + output×BASE_OUTPUT`, keyed by 3-field `PriceRateKey (provider, model, tokenizer_version)` (C-OD-15 §15.2 — the tokenizer-drift anchor, BUILT). Replay dedup rides the idempotency-key join (D6 §1.5) [MODERATE — not independently re-executed]. |
| 9 | `sandbox.cost.tier_overhead_*` | **BUILT** | `cost_attribution_sandbox_fanout.py:4-51` per C-AS-15 §15.6. |
| 10 | Operator-burden 5 eval primitives | **BUILT** | C-OD-17 §17.1 verbatim; `operator_burden_eval_primitives.py` + dashboard binding. |
| 11 | 9-cell matrix implementations | **BUILT-MODIFIED** | Matrix + per-cell collector placement / redaction / retention BUILT (`per_cell_collector_placement_matrix.py`, `observability_matrix.py`). Cell-1: in-process collector + sqlite ring buffer BUILT (`local_first_otlp_collector.py`, `sqlite_span_store_reader.py`); the **TUI trace browser** is formally registered as deferred (C-OD-19 entry in `deferral_envelope.py`; ring-buffer rotation Phase-2 likewise) with `harness-inspect` (U-RT-47) as a read-only CLI partial substitute — §4 item 2. Cell-5/8: bindings built; self-hosted + managed-cloud e2e proven (R-420/R-421); full managed-cloud *deployment-surface dispatch* remains the operator-held DEFER (R-1). |

### 2.7 File 07 — Evaluations

| # | Claim | Verdict | Evidence / delta |
|---|---|---|---|
| 1 | Three-layer validator cascade (L1 syntactic / L2 programmatic / L3 judge+HITL) | **BUILT-MODIFIED** | The ladder exists (C-CP-28 ValidatorFramework; C-CP-21 fail namespace; HITL gates; sandboxed execution) with **Pydantic v2** as L1 — not XGrammar/Outlines (research-only, I-6). |
| 2 | Zheng judge-bias mitigations (position swap, length-norm, cross-family judging, reference-guided) | **RESEARCH-ONLY** | Only in `01-planning`; no spec contract, no code. |
| 3 | Husain/Shankar loops (binary pass/fail, first-upstream-failure, κ≥0.7, TPR/TNR, gold sets) | **RESEARCH-ONLY numbers; loop referenced + tooling SPEC-DEFERRED** | C-OD-17 §17.3 names the Husain loop; its tooling/holdout construction/threshold values sit in the formal C-OD-17/C-OD-18 deferral-envelope entries. |
| 4 | Telemetry ingestion (eval.kind, child spans, drift events, 5 primitives) | **BUILT** | §2.4 #11, §2.6 #10. |
| 5 | Three-step gate cadence (pre-commit / pre-deploy / weekly audit) | **RESEARCH-ONLY** | A process pattern, not harness code; no spec commitment at these fixture scales. |

### 2.8 File 08 — Reliability & Recovery

| # | Claim | Verdict | Evidence / delta |
|---|---|---|---|
| 1 | Durable execution + 5 engine classes + resumption floor | **BUILT** | §2.2 #9; crash-resume behavior carries a large fail-on-main witness corpus (B-FANOUT + B-18 families). |
| 2 | Idempotency key = sha256(conversation_id ‖ step_index ‖ tool ‖ canonical_args) | **BUILT-MODIFIED** | As-built sibling key (`sibling_ledger_entry_composition.py:104-118`): sha256 over `(parent_action_id, sibling_thread_id, step_index, tool, canonical_args)` — sibling-scoped, not conversation-scoped; base writes are keyed by the C-IS-07 WriteKey tuple. Same intent, different composition. |
| 3 | Full-jitter backoff; 429 retry-after; 529 quota-exempt; 402→429; 10% global retry budget | **BUILT-MODIFIED** | Hand-rolled full-jitter retry + breaker registry BUILT (`retry_breaker.py:120-151`; bounded 3-attempt stage loops, typed no-retry auth failures at `providers.py:105-163`). Per-HTTP-status special-casing (retry-after honor, 529 quota exemption, 402 mapping) and a global 10% retry budget were **not found in code** — that granularity is research-level (note: provider SDKs internally honor retry-after). |
| 4 | Breakers + 7-attr schema + cross-family fallback + sticky keys | **BUILT** | §2.5 #4/#5. |
| 5 | Pre-HITL staircase (Reflexion → escalation → HITL) | **BUILT-MODIFIED** | §2.4 #8 — 5 stages verbatim; model-tier escalation via chain composition. |
| 6 | Adaptive early-stopping / plateau detection (Δscore<ε over 3) | **ABSENT** (research-only) | No epsilon/plateau logic in validator or Reflexion paths. |

### 2.9 File 09 — Prompts, Skills, Workflows, Agents

| # | Claim | Verdict | Evidence / delta |
|---|---|---|---|
| 1 | Prompts as git-versioned files, procedural tier, atomic deploy | **BUILT** (convention half is convention) | `harness_is/prompt_manifest.py` `PromptVersion` with `version_sha` (the cache-correct key per the slice-3b probe); routing manifest git-resident. |
| 2 | Multi-segment caching + pre-warm (restated) | see §2.1 #4a–4c | Same verdicts. |
| 3 | Prompt eval gates (assertion CI, judge κ/TPR/TNR) | **RESEARCH-ONLY** | §2.7 #3/#5. |
| 4 | `anthropic.*` cache attrs (cache_creation/read, thinking_budget, breakpoint id) | **BUILT** | `llm_dispatch.py:373-405`; extractor scans translated wire kwargs (B-18-CACHE-TTL-OBSERVABILITY #923) — `anthropic.cache_breakpoint_id` ∈ {tools, system, msg-N}, `cache_ttl_seconds` ∈ {300, 3600}. |
| 5 | Skills standard + progressive disclosure + `skill.activation` | see §2.3 #5/#6/#15 | Adds: `skill.frontmatter.version` (operator semver) committed at ADR-D3 §1.8.1 and present in the attr schema — skills have the semver field; **prompts do not** (PromptVersion semver = registered-optional B-18-LANEB, not built — matches the sweep). |
| 6 | Skill self-evolution | **RESEARCH-ONLY** | §2.3 #16. |
| 7 | Workflows as stateless reducers + declarative manifest | **BUILT** | C-CP-05/C-CP-06 manifest contracts + the ADR-F3 reducer commitment; `workflow_manifest_entry.py`. |
| 8 | Per-step `@f3_invocation` decorators | **BUILT-MODIFIED** | Realized as `StepOverride` manifest fields (model_binding, engine_class, hitl_placement, prompt_version_sha) + the per-step override evaluator — not decorator syntax. |
| 9 | Outer-loop optimization (Meta-Harness Pareto search) | **RESEARCH-ONLY** | `01-planning` only (architectural-tensions + filesystem-substrate query files). |
| 10 | Markdown personas (Sisyphus, Hephaestus, Oracle, Architect) | **RESEARCH-ONLY** | Names appear only in the research inventory/catalog (they are another OSS project's agents). |
| 11 | Worktree isolation; Brief; monotonic tier; staircase | see §2.2 #8, §2.1 #8, §2.3 #12, §2.4 #8 | Same verdicts. |
| 12 | `subagent.*` result status {completed, failed, cascade-cancelled} | **BUILT-MODIFIED** | `topology_subagent_namespace.py:34-48` — 4 members: the three claimed **+ PAUSED** (added by B-HIERARCHICAL-PAUSE). As-built is a superset. |
| 13 | Merkle rollup at fan-out close | **BUILT** | §2.2 #13. |
| 14 | Topology 6-class enum + topology.* | **BUILT** | `topology_pattern.py:38-52` verbatim + CascadePolicy {PAUSE, PROCEED, CASCADE_CANCEL}. |

---

## 3. What "modified during the arc" looks like (the recurring shapes)

1. **Framework-pull discipline replaced named tools with hand-rolled equivalents.** Temporal/LangGraph → five hand-rolled engine substrates; XGrammar/Outlines → Pydantic v2 + deterministic gates; RFC 8785 library → shape-conformant hand-rolled canonicalization. The *taxonomies* the research proposed were kept verbatim; the *vendors* were not.
2. **Anthropic-API realities reshaped cache mechanics.** No cache-ack signal exists → warm-up awaits branch[0] completion; `max_tokens: 0` isn't a valid call shape → boot pre-warm deferred; one `[tools+system]` breakpoint (+ per-sub-agent layer) instead of a 4-segment stack; TTL values kept exactly (5m/1h).
3. **Enums grew or split during hardening.** `SubAgentResultStatus` gained PAUSED; validator taxonomy split into retry-exit classes vs cause-attribution classes; the namespace map grew 12→15 with the files/memory/managed_agents integrations; gate-level axes were re-bookkept (deployment_surface dropped, MCP trust folded via floor table).
4. **H_E features documented in research were never H_T commitments.** Compaction tiers, `/compact`, code-execution-with-MCP, CONTEXT.md section routing, JIT-retrieval conventions, named personas — these describe Claude Code or ICM patterns the research studied, not harness contracts. NotebookLM's summaries blend them into "the specifications implement…" prose; the corpus itself is layered (research vs committed) and the summaries flatten that layering.

---

## 4. Open items this lens surfaces (all acknowledged somewhere; none silent)

Ordered by actionability. Under the standing FULL-SPEC directive, documented deferrals are build targets; items 5–8 are already registered/held elsewhere.

| # | Item | Committed at | Acknowledged at | State |
|---|---|---|---|---|
| 1 | **Boot-time cache pre-warm (`max_tokens=0`) + 4-min keep-alive loop** | ADR-D3 §1.5:189-190 (cleared) | `.harness/u1-slice3b-epoch-partition-design.md` §4.3 + §3.3 R2 ("3c-adjacent, deferred; opt-in default-off when built"); the 3c DDR §8 (`u1-3c-prewarm-design-decision-record.md:145`) even **names the SPINE arc ID `B-18-KEEPALIVE`** as a registration follow-on | **Deferred + never registered** — named for SPINE registration at 3c-close, but the ID never entered `arc-ledger.yaml`/the SPINE ledger, and the registered queue has since emptied. Candidate for a small registration decision. The design docs already name the C11-safe default (opt-in, off) and the R2 cost-pressure carve-out. (Adversarially re-verified: ADR lines byte-exact; zero code hits; zero ledger hits.) |
| 2 | **TUI trace browser + ring-buffer rotation + otelcol config manifest (cell-1)** | C-OD-19 §19.3 | Formal in-code deferral registry `harness_od/deferral_envelope.py` (C-OD-19 entry, closure target Phase-6/implementation) | Deferred-by-contract ("implementation discretion" block); `harness-inspect` CLI (U-RT-47) + `sqlite_span_store_reader` give a read-only partial substitute today. |
| 3 | **Two-row rotation dual-signature runtime path** | ADR-D5 v1.3 §1.4 (`rotation_correlation_id`, co-signed pair, auditor walk semantics) | Committed schema prose; signer exists (`sign_audit_entry`) | Rotation-pair signing/verification code not located [MODERATE]. Persona-tier-gated in practice (only bites at team/multi-tenant key rotation). |
| 4 | **`tool_search` runtime realization** | ADR-D3 §1.5 cache-prefix discipline | Modeled (activation mode, adoption matrix); frozen superset is the current mechanism | Becomes load-bearing only when the tool surface outgrows the frozen superset. |
| 5 | `breaker.cause` + `breaker.cooldown_ms` | CP spec v1 (dropped v1→v1.1, semantic-loss note) | B-19 / U-2 — operator-discretionary (conscious design drop) | Known; surface the ambient-vs-event redundancy before building. |
| 6 | `PromptVersion` operator semver field | ADR-D3 §1.8.1 analogue (skills have it; prompts don't) | `B-18-LANEB-PROMPT-SEMVER` named in DDR + clearance-marker prose as optional — but **ledger-unregistered** (zero hits in `arc-ledger.yaml` / SPINE ledger / forward register; the same registration state as item 1) | Known-optional; version_sha is the cache key either way. If item 1 is registered, decide this one's disposition in the same pass. |
| 7 | Memory-tool managed-DB **live** proof | C-MEM backends | Forward register B-13 (operator DSN + approval) | Built; one operator-gated e2e pending. |
| 8 | Managed-cloud deployment-surface dispatch; Husain-loop tooling + drift-algorithm implementations; OAuth-2.1 resource-server enforcement for remote MCP L2/L3 | Persona §9 / C-OD-17,18 / AS trust taxonomy | R-1 operator-held DEFER; C-OD-17/18 deferral-envelope entries; deployment-binding-time envelope [MODERATE] | Held / deferred-by-contract. The OAuth item is worth a one-probe confirmation of intent next time the AS axis is touched. |

**Doc-hygiene (non-blocking):** root `CLAUDE.md` §1.1 "12-namespace OTel schema" is stale against the 15-row C-OD-05 map — fold into the already-queued root-CLAUDE.md §2 pointer catch-up sweep (same class as the CP v1.86→v1.96 pointer drift noted at #933).

---

## 5. Scope honesty

- **Presence, not correctness.** Like the #916 audit, verdicts assert that mechanisms exist and match/diverge from descriptions — not that built code is bug-free. The B-18/B-FANOUT witness corpora cover behavioral correctness for their surfaces separately.
- **Sweep-agent error rate.** The five parallel sweeps mis-classified **14 of ~80** claims (mostly BUILT features called SPEC-ONLY/ABSENT: Files API, gVisor driver, audit signing, cost engine, tier-overhead metric, outputs_hash, STDIO floor, routing span attrs, per-role binding, retry-exit taxonomy, clear_tool_uses, memory executor depth, one hallucinated `lease.` map row, one self-contradictory redaction verdict). Every verdict used in this report that conflicted with a prior audit, a ledger, or another sweep was re-verified by direct file read; cites in the tables are from those direct reads or from sweep cites spot-confirmed. Un-conflicted BUILT verdicts with specific file:line cites were accepted from the sweeps [residual risk: MODERATE-low].
- **[MODERATE] tags** mark the four claims not fully re-executed: OAuth-enforcement absence, replay-dedup cost join, rotation-code absence, and the 12→15 namespace lineage narrative.
- The NotebookLM `[nnn]` citation indices are notebook-internal and were not resolved one-by-one; provenance was established by grepping the in-repo corpus instead.
- **Decorrelated review.** An independent Fable-5 adversarial reviewer attempted to refute the report against the repo (advisor + Codex outage fallback, both-roles pattern): §4 item 1 survived all four refutation axes and was *strengthened* (the `B-18-KEEPALIVE` named-ID provenance); 8/8 BUILT-cite spot checks passed on substance; no missed major feature across the nine files. Its three concerns (LANEB registration state, a report-authored C-CP-23 mis-cite, #916-consistency wording) and three cosmetics are folded into this revision.

## 6. Consistency with the prior audits

No verdict here contradicts either prior audit, with one granularity caveat stated plainly: everything this audit marks BUILT is consistent with #916's 432-item verification, and everything marked SPEC-DEFERRED is acknowledged in the authority chain or the in-code deferral envelope — #918's "zero silent narrowings" survives this third lens. The caveat: **item 4.1 (boot pre-warm/keep-alive) is an unqualified ADR-D3 commitment with no code and no spec-side deferral block** — by a *literal* reading of #916's gap definition ("committed in the authority chain with no landed, reachable code") it qualifies, and it escaped #916 only because that audit hunted at contract/unit granularity (overlay keyspace) and did not line-scan ADR bodies. Not a method error in #916 — but "zero gaps" should not be read as covering ADR-line granularity. The acknowledgment for 4.1 also lives only in design-decision-record prose, not any machine ledger — and **item 4.6 (LANEB prompt semver) is in the identical state** — so there are **two** items where "documented" and "tracked-forward" have drifted apart. The TUI reconciliation (item 4.2), by contrast, is anchored to a spec-side "Deferred to implementation discretion" block carried in code (`deferral_envelope.py:270-276` with a committed/deferred disjointness assertion) and is a genuine non-gap under #916's own deferred-vs-placed discriminator.

---

*Filed 2026-07-11. Instruments: 5 parallel read-only sweep agents + ~20 direct-read re-grounds; `.harness/arc-ledger.yaml`; `.harness/post-phase-8-forward-register.md`; `harness_od/deferral_envelope.py`; delta-chain-aware spec greps. Companions: `Spec_Implementation_Gap_Audit_2026-07-09.md`, `Upstream_Decomposition_Audit_2026-07-09.md`.*
