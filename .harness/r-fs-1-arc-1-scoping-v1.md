# R-FS-1 Arc #1 — Scoping Pass: provably-complete build inventory

**Authored:** 2026-06-13 · **Posture:** mode-agnostic (process-substrate; grounds `harness-*/src` + canonical specs at HEAD `cf292da` by direct read; authors only this `.harness/` file + the roadmap/dashboard). **Arc:** R-FS-1 arc #1 (`next_pointer: R-FS-1-arc-1-scoping`). **Spine:** `.harness/beyond-mvp-capability-boundary-ledger.md`.

**Trigger:** the FULL-SPEC standing directive (operator 2026-06-12, roadmap §5.0, `[[feedback-full-spec-beyond-mvp-nothing-deferred]]`) makes "full spec, definitively closed" the objective. That is undefined without a **provably-complete** build inventory. Arc #1 closes the scope before any build arc opens, on two levels:

1. **MVP-marker boundaries** — the code-side sweep already captured these (ledger Bucket A re-opened + Bucket B + Bucket C). HIGH confidence.
2. **Contract-level completeness** — the deterministic overlay `contract w/o code cite` set (8 candidates at HEAD). MEDIUM-confidence half this arc resolves.
3. **Fuller spec-body pass** — the spec-side completeness check the ledger flagged as MEDIUM coverage (heads are delta files; bodies live in full-re-table versions).

**Method:** direct-read grounding per candidate (overlay cite-absence is *advisory* — cite-absence ≠ non-implementation, per the ledger). The blocking discriminator throughout is **producer-reachability, not function-existence** — the exact lens that flipped U-CP-12/U-CP-52 at R-CC-1 arc #8 (`[[r-cxa-seam-wiring-is-producer-discovery]]`): a composer/contract that *exists in code* but is reached only through a **dormant driver with zero production callers** is a BUILD item, not "built-but-uncited."

---

## Part 1 — The 8 `contract w/o code cite` candidates: per-contract disposition

`just overlay-query --orphans` → `contract_without_code` at HEAD = `C-CP-30, C-CP-37, C-CP-43, C-CP-49, C-CP-50, C-IS-11, C-OD-3, C-RT-28`.

**Result: 5 doc-hygiene (Q1, NOT build) + 3 genuine BUILD (all fold into existing program clusters — zero net-new arc from this half).**

| Contract | What it is | Grounding (HEAD `cf292da`) | Reachable? | Disposition |
|---|---|---|---|---|
| **C-CP-30** | §16.5.2 `emit_pause_resume_state_ledger_entry` (workflow-layer pause/resume CP→IS emit) | def `pause_resume_protocol.py`; **production callers** `workflow_driver.py:582/808/965` (the CP workflow driver, live; pause/resume itself live since `api.resume` #513/#514) | ✅ prod | **built-but-uncited → Q1 cite hygiene** |
| **C-CP-37** | §16.5.2 `emit_hitl_tool_call_rewriting_state_ledger_entry` (HITL tool-call-rewriting CP→IS emit) | def `hitl_as_tool_call_rewriting.py`; fired at `hitl_tool_loop.py:131`, which is driven by `RuntimeHITLToolLoop.run_tool_calls` at **`llm_dispatch.py:1256`** (production LLM dispatch path) | ✅ prod | **built-but-uncited → Q1 cite hygiene** |
| **C-CP-43** | `MCPTrustTier` 4-level gate-level trust-tier enum | `class MCPTrustTier(StrEnum)` at `cp_shared_types.py:172`; consumed by `per_server_trust_evaluator.py`, `mcp_client_host.py`, `runtime_tool_dispatcher_factory.py` (`default_tier`/`require_audit_below_tier`) — production-wired | ✅ prod | **built-but-uncited → Q1 cite hygiene** (the *multi-server* per-server-trust extension is part of **B2**, but the contract/enum itself is satisfied) |
| **C-IS-11** | — (phantom) | IS spec (`Spec_Information_Substrate_v1.md`) defines contracts only through **C-IS-10**; runtime spec line 1836 explicitly: *"prior v1 cited C-IS-11/14/15 which **don't exist**."* The overlay catches stale **cross-axis cites** in CP spec v1_4/v1_5/v1_6 + runtime spec — not a real contract. | n/a | **phantom → stale-cite hygiene (Q1), NOT build** |
| **C-OD-3** | composite sampler contract | `class HarnessCompositeSampler(Sampler)` + `build_default_sampler` at `composite_sampler.py`; bound at the bootstrap, per-tier base-rate proven live at R-CC-1 arc #5 | ✅ prod | **built-but-uncited → Q1 cite hygiene** (B7 conditional-row over-sampling is the only residual refinement, already in Bucket B) |
| **C-CP-49** | §16.5.2 `emit_pause_captured_state_ledger_entry` (**engine-layer** pause-capture CP→IS emit) | def `pause_resume_protocol.py`; reached **only** via `RuntimeEngineRecoveryLoop.capture_pause` (`engine_recovery_loop.py:63`). The recovery loop is *constructed* at stage 5 (`r_cxa_2_producer_loop_factory`) but its `capture_pause`/`attempt_resume` methods have **ZERO production callers** — the dormant engine-recovery driver (Bucket A residual; the engines that emit engine-layer pauses are unbuilt). | ❌ dormant driver | **BUILD → folds into engine-classes (Bucket A)** |
| **C-CP-50** | §16.5.2 `emit_resume_attempted_state_ledger_entry` (**engine-layer** resume-attempt CP→IS emit) | def `pause_resume_protocol.py`; reached only via `RuntimeEngineRecoveryLoop.attempt_resume` — same dormant driver, zero production callers | ❌ dormant driver | **BUILD → folds into engine-classes (Bucket A)** |
| **C-RT-28** | managed_agents runtime executable-consumer contract — **never authored** | runtime spec line 579: *"no managed_agents executable consumer contract authored at v1.33; no §14.18 C-RT-28 sibling to v1.32 §14.17 C-RT-27"* (AS-8f managed_agents indefinite-defer, Q1=(C) 2026-05-28). `managed_agents.py` exists only as the local-development-**excluded** namespace surface (R-CL-P6), not a runtime consumer that *runs* managed agents. | n/a (no contract) | **BUILD → new managed-cloud-surface arc (contract authoring + pipeline)** |

**Provably-complete claim for Part 1:** the overlay `contract_without_code` set decomposes with **zero unexplained entries** into `{phantom: C-IS-11} ∪ {built-but-uncited→Q1: C-CP-30, C-CP-37, C-CP-43, C-OD-3} ∪ {never-authored/dormant-driver→BUILD: C-CP-49, C-CP-50, C-RT-28}`. None of the BUILD-classified contracts is a net-new *arc* — C-CP-49/50 are subsumed by the engine-classes build; C-RT-28 is the managed-cloud surface arc (Part 3 §M).

---

## Part 2 — Fuller spec-body pass (live-at-head filter)

**Method (advisor-recommended, bounded):** grep the full `design-substrate/Spec_*.md` corpus for capability-level deferral markers → dedup by capability → **live-at-head filter** (a deferral resolved in a later delta is CLOSED, not open — the spec-side twin of how Bucket C discarded stale docstrings) → cross-ref Bucket A/B/C → keep only net-new.

**Keyword frequency** (capability-deferral phrases, full corpus): every signal maps to an existing bucket — `fan-out`(10)/`topology`(3)/`orchestrat`/`handoff` → **B1**; `per-tool`(4) → **B6**; `per-step`(4) → **B4**; `single-server`/`multi-server` → **B2**; `single-tenant` → **Bucket C** (already lifted).

**Eyeballed deferral sentences → live-at-head verification of the 3 candidates that looked potentially net-new:**

| Spec-declared boundary | Live-at-head check | Verdict |
|---|---|---|
| **Circuit-breaker** "retry-only MVP at v1; breaker semantics deferred to a future OD-axis-coordinated arc (Q1a=(i))" | `retry_breaker.py` has a **real `BreakerState` machine** — `CLOSED → OPEN` after 5 consecutive failures, `OPEN → HALF_OPEN` after 30 s. The "retry-only" framing is **superseded** — the breaker is built. Only the *config tuning* is hardcoded (`retry_breaker.py:23` "Breaker config is spec-deferred per C-CP-03 §3.5"). | **NOT net-new.** Breaker built; config-tuning = minor field-level scope (folds under the reliability/routing arc). |
| **SE workload** "SOFTWARE_ENGINEERING structurally unrunnable via YAML/TOML manifest path at MVP" | runtime spec v1.38 line 216: *"MVP-scope SE-workload runnability **CLOSED**"* — single-step SE loads. The **residual** ("SE's matrix-permitted `{EVALUATOR_OPTIMIZER, ORCHESTRATOR_WORKERS}` both unmaterialized at C-CP-25 v1.4 MVP") **IS B1**. | **Covered by B1** (the 5 non-linear topologies). Single-step closed. |
| **Idempotent MCP-host restart** "out of scope at v1 (deferred to operator-driven restart arc)" — STDIO/HTTP/SSE host lifecycle | No restart/recovery for an `MCPClientHost` at HEAD (one subprocess/connection per bootstrap; no idempotent re-spawn). Genuinely open; not in Bucket A/B. | **NET-NEW (minor)** → folds under **B2** (multi-server MCP lifecycle) as a sub-item. |

**Part-2 result:** the fuller spec-body pass surfaces **no net-new *major* capability arc** beyond Bucket A/B. It adds **two minor field-level scopes** — (a) breaker config-tuning (under the routing/reliability arc), (b) idempotent MCP-host restart (under B2) — and confirms every other spec-declared boundary already maps to B1–B7 / Bucket A / Bucket C. Spec-side coverage is thereby raised from MEDIUM to HIGH for capability completeness.

---

## Part 3 — The authoritative ordered R-FS-1 child-arc list (the deliverable)

Sequence = capability-unlock-first, design-fork-first per X-AL-3 (each large arc: research → design → spec → plan → implement). This refines the roadmap §5.0 default sequence with the Part-1/Part-2 grounding folded in. **Default-if-silent: proceed as ordered** (the directive settles build-vs-defer; only re-ordering is operator-open, and no hard dependency contradicts this order).

| # | Arc | Scope (grounded) | Folds in | Gate |
|---|---|---|---|---|
| **B1** | **Topology orchestration** (the largest; the multi-agent / parallel / cross-comm payload) | Materialize real orchestration semantics for the 5 non-`SINGLE_THREADED_LINEAR` patterns — `PARALLELIZATION` (true fan-out), `ORCHESTRATOR_WORKERS`, `DECENTRALIZED_HANDOFF`, `HIERARCHICAL_DELEGATION`, `EVALUATOR_OPTIMIZER`. CP contract C-CP-25 design+build. | SE non-linear topologies (Part 2); `cascade-cancelled` fan-out semantics; CP-entry `timestamp`/`prior_event_hash` fan-out population | design-fork-first |
| **B3** | **Smart-HITL gate intelligence** | §14.8.2 step-4c conditional gating (replace always-True `_hitl_required`) + step-4d palette narrowing/escalation + placement matrix + `HandoffContext` binding | **HITL OQ-6** auto-timeout-degradation producer (Bucket A) — the smart-HITL L8 wall-clock-wait orchestrator is its producer | design-fork-first |
| **E** | **Engine classes** (hand-roll, I-6 — NO vendored framework) | Build the 3 deferred durable engines: `event-sourced-replay` / `reconciler-loop` / `WAL-segment`. Their drivers fire the engine-recovery loop. | **C-CP-49 + C-CP-50** (the engine-layer pause-captured/resume-attempted emits gain their production driver); R-CL-P2 engine-recovery; R-CXA-2 durable-recovery residual | design-fork-first |
| **B2** | **Multi-server MCP** | `mcp_client_host: MCPClientHost` (singular) → a mapping of named servers + per-server discovery/routing/trust-tier resolution | **C-CP-43** multi-server per-server-trust extension; **idempotent MCP-host restart** (Part 2 net-new minor) | design-fork-first |
| **R** | **LLM_AS_ROUTER + EMBEDDING** (routing Layers 3 + 2) | LLM_AS_ROUTER via Reading B at the async `infer()` layer; EMBEDDING similarity routing | — | **vendor gate** — router-model / corpus + embedding-model surfaced at the boundary, never auto-fired (`[[feedback-background-agent-no-unilateral-paid-calls-or-secret-relocation]]`) |
| **B4** | **Per-role / per-step dispatch** | Thread `AgentRole` (+ per-step override) through dispatch so per-role model + per-role prompt take effect (both manifests carry the binding structurally; role is discarded at `llm_dispatch.py:489`) | per-step gate-level surfacing (`parent_gate_level` AUTO minor) | composes with B1 |
| **CA** | **Cost aggregate** | `RunResult.cost_attribution` rollup (per-dispatch cost already in the audit ledger; only the run-result rollup is empty — U-RT-49) | Q2 shared-carrier (first non-linear topology, motivated by B1) | — |
| **B5** | **Memory per-surface selection** | `resolve_backend(deployment_surface)` honors its argument (U-RT-80 factory); backends already live (R-830) | — | small |
| **B6** | **Per-tool sandbox + STDIO transport-floor** | §14.9.8 per-tool tier resolution + ADR-D2 §1.3 STDIO tier-3 transport-floor (arc #1/#503 landed per-server-uniform only) | — | bounded |
| **B7** | **OD sampler conditional-row** | §9.2 per-attribute (`kind`/`permanence`/root) conditional sampling (currently over-samples — safe) | breaker config-tuning (Part 2 minor) could ride here or under R | Class-3 (RATIFY-or-build) |
| **M** | **Managed-cloud managed_agents consumer** (net-new from Part 1) | Author **C-RT-28** (managed_agents runtime executable-consumer contract) + the runtime consumer that runs managed agents on the managed-cloud surface. Managed-cloud is committed scope (3-tier deployment; team→multi-tenant persona arc). | AS-8f managed_agents indefinite-defer re-opened | **vendor/surface gate** — Anthropic managed-agents API access surfaced at the boundary |
| | **Minor field-level scopes** | roll under whichever arc touches them | `workflow_driver_types.py` `parent_entry_hash` sentinel; `skills.py` cost = description-length proxy (§14.17.7 token-counting); `pause_resume` `StateSummary`/`PauseContextReader` MVP-minimal; anchor-validation U-CP-22 | — |

**Bucket C** (stale docstrings: `mutable_context.py:282`, `composite_sampler.py:37`, `workflow_driver_types.py:193`, roadmap §5 line 1078) → **R-CL-Q1 doc-hygiene**, nothing to build.

**Q1 cite-hygiene fold-in** (from Part 1 — Phase-7 src edits, NOT this mode-agnostic arc): tag `C-CP-30/37/43` + `C-OD-3` carriers with their contract cites; correct the stale `C-IS-11` cross-axis cites in CP spec v1_4/5/6 + runtime spec. These ride R-CL-Q1 (or each arc's own hygiene), not a build arc.

---

## Part 4 — Verification + confidence + what's next

**Provably-complete verification (R-FS-1 `must_pass` half 2 — "overlay `contract w/o code cite` driven to zero or each proven implemented-but-uncited"):** ✅ all 8 overlay candidates resolved per-contract above — 5 proven implemented-but-uncited/phantom, 3 routed to build clusters with their producer gap named. The set has zero unexplained entries.

**Confidence.** Code-side capability coverage: **HIGH** (ledger's 47-file re-ground). Contract-level: **HIGH** (8/8 resolved by direct read). Spec-body: **raised MEDIUM → HIGH** (Part 2 keyword-frequency + 3 live-at-head checks; every signal maps to a known bucket). Residual uncertainty: a deep per-delta-body read could surface a further *minor* field-level scope, but no *major* arc — the code-side sweep is the stronger signal for what is actually reduced at runtime, and it agrees.

**Scope is closed.** The R-FS-1 build inventory is now provably complete: **B1 → B3 → E(engines) → B2 → R(router/embedding) → B4 → CA(cost) → B5 → B6 → B7 → M(managed-cloud)** + minor field-level + Bucket C→Q1.

**Next action:** open **B1 — topology orchestration** as R-FS-1 arc #2 (design-fork-first per X-AL-3; the largest arc; research → design → spec → plan → implement). It is the multi-agent / parallel / cross-agent-communication capability and unlocks B4 (per-role dispatch) + the SE non-linear topologies + fan-out cost/cascade semantics.

---

*Filing footer — Artifact: `.harness/r-fs-1-arc-1-scoping-v1.md`; Arc: R-FS-1 #1 scoping; Posture: mode-agnostic; X-AL-3: trivially clean (zero `design-substrate/**` or `harness-*/src` edit). Decorrelated review: advisor (pre-substantive: producer-reachability discriminator + bounded spec-body method) + out-of-family Codex (PR). Spine: `.harness/beyond-mvp-capability-boundary-ledger.md`. Directive: `[[feedback-full-spec-beyond-mvp-nothing-deferred]]`.*
