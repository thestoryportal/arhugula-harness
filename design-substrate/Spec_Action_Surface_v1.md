# Spec — Action Surface v1.7

## Change-note (v1.6 → v1.7)

**Scope of revision.** GenAI span-name format Class 1 fork resolution R3 follow-on per `.harness/class_1_fork_genai_span_name_four_way_drift.md` §7.4.3 (R3) operator-ratified 2026-05-26 option (A) + option (b) alias-term abstraction. NEW alias-term convention introduced at §14.1 + applied at §14.2 + §14.7 + §14.8: literal string `llm.inference` (which was never an actual emitted span name at production — see fork §2.2) replaced with conceptual alias term **"the LLM inference span"** with cross-reference to OD spec v1.12 §C-OD-04 §4.1 for the actual runtime span-name format.

**Architectural rationale.** Per fork §7.4.3 architect Mode-3 finding: option (a) literal rename is structurally impossible because the post-R2 actual emitted span name is template-instantiated per-call (`{operation} {model}` resolves to e.g. `chat claude-opus-4-7` at one dispatch and `embeddings text-embedding-3` at another). A literal-string parent-anchor cite cannot point at a per-call-variable name. The current `llm.inference` literal works only because it's never emitted at production — phantom anchor. Option (b) alias-term abstraction decouples spec parent-anchor citations from runtime span-name resolution: future semconv version bumps (1.41.0 → 1.42.0 etc.) ripple only through OD §4.1 + production rename; AS spec parent-anchor cites are immune.

**Narrow-scope framing.** The amendment touches ONLY parent-span anchor citations for the `anthropic.*` namespace (the namespace that consumes the LLM-dispatch span). Other namespaces with literal parent-span anchors at §14.1 (`mcp.*` → `mcp.tool.call`, `skill.*` → `skill.activation`, `managed_agents.*` → `managed_agents.runtime`, `files.*` → `files.operation`, `memory.*` → `memory.operation`) PRESERVED VERBATIM — those parent-span names ARE the actual emitted span names at production (verified at filing). The `memory.context_editing_active` semantic at §14.7 cites "parent llm.inference" — also amended per the alias-term convention.

**Amendment sites.**

| Site | Amendment shape | Substrate source |
|---|---|---|
| **§14.1 (new sub-note before the 6-row table)** | NEW alias-term declaration: *"**The LLM inference span** is the conceptual reference used at this specification for the span opened by the runtime LLM dispatcher composer per OD spec v1.12 §C-OD-04 §4.1 (actual emitted span name = `{gen_ai.operation.name} {gen_ai.request.model}` 2-token byte-exact to OTel GenAI semconv 1.41.0). Cited at AS spec rows + downstream namespace schemas as 'the LLM inference span' — the literal span-name format is OD-axis-owned at §4.1. This decoupling means AS spec parent-anchor citations are immune to future OTel semconv version bumps; only OD §4.1 + production rename ripple."* | Class 1 fork §7.4.3 option (b) + OD spec v1.12 §C-OD-04 §4.1 |
| **§14.1 row 1129 `anthropic.*` parent-span column** | `llm.inference` → `the LLM inference span` (alias per §14.1 sub-note) | Class 1 fork §7.4.3 option (b) |
| **§14.2 section header** | `(ten attributes on \`llm.inference\` span)` → `(ten attributes on the LLM inference span)` | Class 1 fork §7.4.3 option (b) |
| **§14.7 `memory.context_editing_active` semantic cite** | `True if parent \`llm.inference\` uses \`clear_tool_uses_20250919\`...` → `True if parent (the LLM inference span) uses \`clear_tool_uses_20250919\`...` | Class 1 fork §7.4.3 option (b) |
| **§14.8 sampling-policy table row 1** | Key `llm.inference` → `the LLM inference span` (alias per §14.1 sub-note); remaining 5 rows (`skill.activation` / `mcp.tool.call` / `managed_agents.runtime` / `files.operation` / `memory.operation`) PRESERVED VERBATIM — those keys ARE actual emitted span names | Class 1 fork §7.4.3 option (b) |

**Cross-file absorption owed (per spec-writer §5; flagged for downstream).**

| Artifact | Required change | Owner |
|---|---|---|
| `harness-as/src/harness_as/anthropic_attribute_namespaces.py:110` | `_ANTHROPIC_SPAN = "llm.inference"` → `_ANTHROPIC_SPAN = "the LLM inference span"` (alias marker per §14.1 amendment) | Direct impl edit (R3 this session) |
| `harness-as/src/harness_as/anthropic_primitive_sampling.py:40` | Mapping key `"llm.inference"` → `"the LLM inference span"` matching alias | Direct impl edit (R3 this session) |
| `harness-cp/src/harness_cp/routing_namespace.py:50-52` | `_LLM_INFERENCE_PARENT` text content updated to alias phrasing (preserves OTel semconv citation, replaces literal with alias) | Direct impl edit (R3 this session) |
| `harness-cp/src/harness_cp/multi_agent_span_hierarchy.py:84` | `"llm.inference[]"` → `"the LLM inference span[]"` (alias marker) | Direct impl edit (R3 this session) |
| 11 source-file docstring sites | Replace literal `llm.inference` references with alias-term phrasing per fork §2.2 | Direct impl edit (R3 this session) |
| `harness-cp/tests/test_routing_namespace.py:6,35,37` | Alias-aware assertion (substring match against new alias text) | Direct test edit (R3 this session) |
| `Cross_Axis_Composition_Document_v2_10.md` → v2.11 | Declare AS §14.1 ↔ OD §4.1 cross-axis seam at §2.3.x convention bucket (alias-term ↔ format owner) | Direct CXA edit (R3 this session) |

**Adjacent observations (NOT patched per FM-2).**

(a) **Other §14.1 parent-span literals.** `mcp.tool.call` / `skill.activation` / `managed_agents.runtime` / `files.operation` / `memory.operation` literals are PRESERVED VERBATIM because those names ARE actual emitted span names at production. If future arcs introduce per-call-variable naming for any of these (unlikely per current design), the alias-term convention extends naturally — but no extension owed at this arc.

(b) **`gen_ai.system` vs `gen_ai.provider.name` attribute-name divergence at production (OD v1.12 §"Adjacent observations" (f)).** Unchanged; separate apply-pass arc.

(c) **`_PROVIDER_OPERATIONS` non-§4.2-enum-conformance at production (runtime spec v1.27 §"Adjacent observation").** Unchanged; separate apply-pass arc.

---

## Change-note (v1.5 → v1.6)

**Trigger.** Class 1 fork resolution apply pass per `.harness/class_1_fork_as_4_f4_enum_taxonomy_mismatch_and_production_bug.md` (operator-ratified 2026-05-25 — Reading B "NEW MCP-protocol-layer fail-class taxonomy at §15 (sibling to F4)"). The fork surfaced (i) production bug at `runtime_tool_dispatcher.py:400 + :407` assigning `sandbox_fail_class = "transport"` / `"schema-violation"` strings NOT in canonical `SandboxFailClass` (F4) enum, (ii) `sandbox.violation` child span absent in production (deferred per `runtime_tool_dispatcher.py:414` comment), (iii) structural taxonomy mismatch — F4 enum is process-execution-shaped (escape/egress/timeout/oom/signal/exit_nonzero/policy_override) but production exceptions are MCP-protocol-shaped (`ToolInvocationTimeoutError`, `ToolInvocationProtocolError`, `MCPHostUnreachableError`, `jsonschema.ValidationError`). Reading B authors a sibling taxonomy at the proper MCP-protocol abstraction layer, preserving F4 enum semantic coherence at process-execution layer.

**Scope of revision.** Additive contract extension at C-AS-15 §15. NEW §15.8 authors `MCPInvocationFailClass` 4-value StrEnum at AS-axis as canonical declaration site (parallel to F4 at C-AS-04 §4.1 + sandbox.* canonical attribute declaration at §15.2). NEW §15.9 authors `mcp.fail.class` attribute on `sandbox.violation` child span (sibling to existing `sandbox.fail.class` per §15.2 row 3). §15.10 authors a best-effort projection table mapping MCP-shape values to F4-shape values for cross-layer correlation. F4 enum at §4.1 PRESERVED VERBATIM — no field change. Existing §15.1..§15.7 PRESERVED VERBATIM. Producer-side mutation discipline at runtime spec §14.9 owns the dispatcher-side mapping (producer-vs-canonical-schema separation per D6 ingestion-pattern discipline, mirroring v1.4 §14.3 footer pattern: runtime emits, AS-axis owns canonical schema).

| Site | Amendment | Reason |
|---|---|---|
| **C-AS-15 §15.8** (NEW subsection) | NEW `MCPInvocationFailClass` 4-value StrEnum: `transport` / `protocol_error` / `schema_violation` / `timeout` + per-class semantic + cardinality | Canonical declaration of MCP-protocol-layer fail-class taxonomy at AS-axis. Sibling to F4 enum at C-AS-04 §4.1 (process-execution-layer). Carries MCP-protocol-boundary failure modes that production runtime catches at `harness-runtime/src/harness_runtime/lifecycle/runtime_tool_dispatcher.py:395-412` dispatcher exception handlers. |
| **C-AS-15 §15.9** (NEW subsection) | NEW `mcp.fail.class` attribute on `sandbox.violation` child span — enum string per §15.8 4-value enum; bounded (4); always-emitted on sandbox.violation event; discriminator role = MCP-protocol-boundary failure-class taxonomy (sibling to `sandbox.fail.class` F4 taxonomy at process-execution layer) | sandbox.violation child span now carries BOTH `sandbox.fail.class` (F4 process-shape per §15.2 row 3) AND `mcp.fail.class` (MCP-shape per §15.8). Both attributes always-emitted; either may carry null/empty when the violation does not span both layers (e.g., a sandbox `escape_attempt` may have no MCP-layer correlate). |
| **C-AS-15 §15.10** (NEW subsection) | NEW best-effort projection table from `MCPInvocationFailClass` (§15.8) to `SandboxFailClass` (§4.1) — partial mapping for cross-layer correlation discipline | When a `sandbox.violation` event carries a non-null `mcp.fail.class`, the runtime SHOULD also assign the projected `sandbox.fail.class` per §15.10 table to maintain F4 audit-ledger continuity. Projection is best-effort — semantic stretch is acknowledged at §15.10 footer; not all MCP-shape values have clean F4 correlates. |

**Sections preserved verbatim from v1.5.** All v1.5 content outside the three new C-AS-15 subsections preserved verbatim. C-AS-01 through C-AS-16 (v1.5 numbering) preserved. §4.1 F4 `sandbox.fail.class` enum PRESERVED VERBATIM. §15.1..§15.7 (existing C-AS-15 subsections) PRESERVED VERBATIM. The v1.5 + v1.4 + v1.3 + v1.2 + v1.1 + v1 chain preserved.

**Status posture.** Proposed (v1.5) → **Proposed (v1.6)**. v1.6 is an additive substantive amendment — new contract content authored at C-AS-15 §15.8 / §15.9 / §15.10; F4 enum at §4.1 unchanged; existing §15 subsections unchanged.

**Downstream absorption owed (post-v1.6).**
(a) Workspace `CLAUDE.md` §2.3 AS row version bump (v1.5 → v1.6); co-published this arc.
(b) AS plan v1.2 → v1.3 — U-AS-17 + U-AS-18 absorption (sandbox.violation child span gains `mcp.fail.class` attribute per §15.9; U-AS-17 AC #3 attribute count grows; U-AS-18 sampling-discipline carries §15.4 row 3 unchanged; potentially NEW carrier unit for `MCPInvocationFailClass` enum or extend U-AS-03 fail-class enum carrier unit). Owed at follow-on plan revision arc.
(c) `harness-as/src/harness_as/` impl — NEW `mcp_invocation_fail_class.py` (or extend `sandbox_fail_class.py` module) authoring `MCPInvocationFailClass` StrEnum carrier. Owed at impl arc.
(d) `harness-runtime/src/harness_runtime/lifecycle/runtime_tool_dispatcher.py:395-412` impl — fix exception handler mapping (lines 400 + 407) per §15.8 enum + open `sandbox.violation` child span per §15.1 hierarchy (currently deferred at line 414 comment) emitting both `sandbox.fail.class` (per §4.1 projected via §15.10) and `mcp.fail.class` (per §15.8 directly). Owed at impl arc.
(e) Retirement batch — H_T-AS-4 PARTIAL → RETIRED at impl arc landing (mirrors `[[fork-validator-composer-arc-stage-4-absence]]` Reading A close pattern); AS-axis advances 3/5 → 4/5 (60% → 80%).
(f) Fork doc §8 closure block — file at fork close per `[[fork-cp-spec-section-25-contract-id-collision]]` two-arc resolution pattern (arc 1 = this spec amendment; arc 2 = plan + impl + retirement bundle at fresh worktree per FM-4 risk-aware scoping).

**Adjacent defects surfaced (not patched at v1.6).**

(i) **CXA / OD spec cite cascade.** OD spec v1.11 §C-OD-05 (namespace-ingestion-map at U-OD-05) declares the AS-source namespace 7-entry set (anthropic / mcp / skill / managed_agents / sandbox / files / memory). NEW `mcp.fail.class` attribute is at AS-axis sandbox.* namespace, not a new top-level namespace, so §C-OD-05 row count unchanged. However OD §C-OD-06 (AS-source namespace verification at U-OD-06) MAY require attribute-set verification refresh — owed at follow-on OD spec revision pass if attribute-set verification surfaces. NOT patched at v1.6 per FM-2 no-extension discipline.

(ii) **CXA v2.10 §2.3 AS→OD bucket attribute-shape carry.** CXA v2.10 §2.3 AS→OD bucket lists sandbox.* namespace as AS→OD typed seam. The new `mcp.fail.class` attribute composes into the existing seam at attribute layer (not new edge). CXA cardinality unchanged at semantics layer; potential CXA-side §0.3 attribute-list refresh owed at follow-on CXA revision pass. NOT patched at v1.6 per FM-2 no-extension discipline.

(iii) **ADR-D2 reference frame.** ADR-D2 v1.2 §1.7 + §1.7.1 declared the F4 enum at C-AS-04 §4.1 as canonical declaration site. The NEW MCPInvocationFailClass at §15.8 is NOT declared at ADR-D2 — it is an AS-spec-internal contract additive at C-AS-15 §15. ADR-D2 reference frame UNCHANGED; no ADR revision triggered. Future ADR-D2 revision arcs MAY surface the MCP-protocol-layer fail-class as a downstream ADR-D2 §1.7.X sub-section if cross-axis composition demands it; deferred to operator-discretion timing per X-AL-3 no-silent-design-extension discipline at later phases.

(iv) **Production bug at `runtime_tool_dispatcher.py:400 + :407`.** The string assignments `"transport"` and `"schema-violation"` to `sandbox_fail_class` are bugs — those strings are not in canonical F4 enum at §4.1. v1.6 spec authoring does NOT fix the production bug; the bug fix is owed at impl arc per downstream absorption item (d). At impl arc landing, the strings become canonical F4 values (per §15.10 projection table) AND the MCP-shape exception type → mcp.fail.class enum value is also assigned at the new attribute. The bug is filed at the fork doc Defect (i); fix lands at impl arc.

(v) **`SandboxTierFloorViolationError` raise site.** This exception fires at dispatcher line 330 BEFORE any sandbox.* span opens. Per fork doc §6 adjacent finding (b): the violation child span must open in the exception path, not at sandbox.exit. Impl-arc design owes this discriminator: open `sandbox.violation` span DURING exception unwinding (OTel allows; child spans can open/close on exception paths). NOT patched at v1.6 — owed at impl arc per (d).

---

**Trigger.** Class 1 fork resolution apply pass per `.harness/class_1_fork_h_t_cp_16_17_executable_consumer_absence.md` §16 (operator-ratified 2026-05-23). The fork's §13 systems-architect Mode 3 recommendation §13.6.D ratified at §14 routing requires AS spec §14.7 `memory.*` namespace to gain a producer-site reference footer note pointing at the NEW runtime spec v1.17 §14.12 C-RT-22 `MemoryToolRegistry` / `MemoryToolStorageBackendProtocol` callback-invocation sites (parallel to v1.4 §14.3 mcp.* footer pattern). Co-published with runtime spec v1.17.

**Scope of revision.** Pure annotation-level extension. NO field-set change. NO attribute-list change. NO new AS-AL rule. NO contract signature change. ONE new footer note added at §14.7 `memory.*` namespace.

| Site | Amendment | Reason |
|---|---|---|
| **C-AS-14 §14.7** (footer note) | NEW NOTE: *"At H_T-as-Memory-tool-consumer sites (i.e., when H_T invokes Anthropic Memory tool via runtime spec v1.17 §14.5.1 C-RT-15 callback-injection composer-step + §14.12 C-RT-22 `MemoryToolRegistry`), the `memory.*` 6-attribute namespace is emitted by the storage-backend callback per C-RT-15 §14.5.1 step 4 + C-RT-22 §14.12.2 invariant 2. The attribute set declared at this §14.7 is canonical; runtime spec §14.5.1 + §14.12 own the producer-side emission discipline at each storage-backend callback span context. Memory tool is **client-side** per ADR-D3 §1.1 #11 — the harness implements the storage backend; the Anthropic SDK runs the message loop; the harness storage-backend callback emits one `memory.operation` span per CRUD invocation (`view` / `create` / `delete` / `str_replace` / `insert` callbacks per C-RT-22 §14.12.1). This pattern differs structurally from C-AS-14 §14.3 `mcp.*` (single dispatch-site emission at C-RT-19 §14.9.4 `mcp.tool.call` span) — per-callback emission, not per-dispatch."* | Documents producer-side ownership of `memory.*` namespace at the H_T-as-Memory-tool-consumer callback-invocation sites. Per `.harness/class_1_fork_h_t_cp_16_17_executable_consumer_absence.md` §13.6.D recommendation: emission site differs from MCP single-dispatch-span pattern — each storage-backend callback emits its own span. |

**Files API (§14.6) NOT amended at v1.5.** Per `.harness/class_1_fork_h_t_cp_16_17_executable_consumer_absence.md` §14.C ratification: Files API arc deferred indefinitely. The `files.*` namespace at §14.6 retains its existing declaration without a producer-site reference footer (no runtime spec executable consumer contract authored at v1.17 to reference). Re-opens at future Files arc when operational driver materializes.

**Sections preserved verbatim from v1.4.** All v1.4 content outside the single §14.7 footer note preserved verbatim. C-AS-01 through C-AS-16 (v1.4 numbering) preserved. The v1.4 §14.3 `mcp.*` footer note + §15 `sandbox.*` footer note (both new at v1.4) preserved. The v1.4 + v1.3 + v1.2 + v1.1 + v1 chain preserved.

**Status posture.** Proposed (v1.4) → **Proposed (v1.5)**. v1.5 is a documentary-only patch — one producer-site reference NOTE at §14.7; no signature change; no acceptance criterion change; no AS-AL rule extension.

**Downstream absorption owed (post-v1.5).**
(a) Workspace `CLAUDE.md` §2.3 AS row version bump (v1.4 → v1.5); co-published this arc.
(b) `harness-as/CLAUDE.md` §1.2 + §4.1 retirement-table extension shapes pending runtime spec v1.17 §14.12 implementation arc (H_T-AS-related shapes deferred to implementation arc per existing v1.4 (b) carry-forward pattern).
(c) Co-published with runtime spec v1.16 → v1.17 in this single Class 1 fork resolution arc.

**Adjacent defects surfaced (not patched).**

(i) **Files API §14.6 footer note absence.** Per §14.C ratification, Files API arc deferred indefinitely; corresponding §14.6 producer-site reference footer note NOT authored at v1.5. Re-opens at future Files arc opening (operator-discretion timing). The §14.6 namespace declaration itself preserved verbatim from v1.4.

(ii) **§14.3 `mcp.*` footer note structural-pattern comparison.** The v1.4 §14.3 footer note points at a single canonical dispatch site (C-RT-19 §14.9.4 `mcp.tool.call` span). The v1.5 §14.7 footer note points at per-callback emission sites (5 distinct `memory.operation` spans per CRUD callback per C-RT-22 §14.12.2 invariant 2). The structural divergence is intentional per §13.6.D architect recommendation — Memory tool is client-side per ADR-D3 §1.1 #11 (no single dispatch site). This is a documentary observation, not a defect; NOT patched per FM-2 no-extension discipline.

---

## Status block

| Field | Value |
|---|---|
| Artifact | `Spec_Action_Surface_v1.md` |
| Status | **Proposed** — Phase 5 session 2 axis specification; no clearance until aggregate P5-CK per `Project_Workflow_v1_2.md` §2.5.1 + OD-5-4.A |
| Date | 2026-05-13 |
| Phase | 5 — specification authoring (session 2 of 4–6) per `Project_Workflow_v1_2.md` §2.5 |
| Skill | `spec-writer` SKILL.md in Stage-3 final-specification mode per skill description |
| Axis | Action Surface (per `Phase_5_Entry_Handoff.md` §3.1 axis sequencing) |
| Source-set | `PRD_v1.0.md` §3 (R-AS-01 through R-AS-07); `Architectural_Design_Document_v1.md` v1.2 §2.4 + §2.5 + §3.3.1 + §3.3.2 + §5.1 + §5.2.1 + §5.3.2; `ADR-F4.md` v1.1 (§Decision + §Rationale + §Consequences); `ADR-F5.md` v1.1 (§Decision + §Rationale + §Consequences + §"Permanent tensions engaged"); `ADR-D2.md` v1.2 (§1.1 + §1.2 + §1.3 + §1.4 + §1.5 + §1.5.1 + §1.5.2 + §1.6 + §1.7 + §1.7.1 + §1.8 + §1.9 + §1.10); `ADR-D3.md` v1.2 (§1.1 + §1.2 + §1.3 + §1.4 + §1.5 + §1.6 + §1.7 + §1.8 + §1.8.1 + §1.9); `Persona_Document_v1.md` §X.y anchors inherited from PRD requirements; `Spec_Information_Substrate_v1.md` (cross-axis citation substrate at C-IS-05 + C-IS-06 + C-IS-07 + C-IS-10) |
| Entry authorization | `Phase_5_Session_2_Session_Prompt.md` §4 entry-gate verified 7/7; session-1 spec filed and coherence-pass-passed |
| ODs applied | OD-5-1.A (per-axis multi-document) + OD-5-2.A (Action Surface confirmed per handoff §3.1; no divergence) + OD-5-3.A (as-needed council consultant; no escalation invoked at session 2) + OD-5-4.A (aggregate P5-CK at full close) |
| Exit gate | This spec filed at `/mnt/user-data/outputs/`; §[coherence pass] returns ✅ PASS at all five audit dimensions; `Phase_5_Session_3_Session_Prompt.md` authored at session close |
| Revision | v1 → v1.1 (P5-CK iter-1 close mechanical revision per modified `Project_Workflow_v1_2.md` §4.1.2 path — Source-set ADR-D3 token bump v1.1 → v1.2 per Stage 1 ADR-D3 revision; comprehensive body-citation alignment v1.1 → v1.2 at 27 sites under use-latest-version discipline (Stage 4 precedent) applied to lines 1–1281; §[coherence pass] section lines 1282–1361 preserved verbatim as v1 point-in-time audit; line 28 Axis-grounding note bare-form D3 v1.1 → D3 v1.2; line 936 + 937 historical parentheticals "(v1.1 — F2-11 Reading 2 closure)" preserved as accurate ADR-D3 v1.1 namespace-introduction event references; no substantive content amendment per handoff §3.1 verification-only scope) |
| Revision date | 2026-05-13 |
| Revision | v1.1 → v1.2 (Phase 7 C-AS-02 `sandbox_tier_floor` signature reconciliation per `spec-writer` application of the operator-ratified `.harness/s1_c_as_02_reconciliation.md` recommendation — 2026-05-15; §2.2 + §2.3 + §10.2 + §11.1 + §12.1 reconciled to the canonical 5-argument `sandbox_tier_floor(tool, deployment_surface, blast_radius_tier, mcp_transport, mcp_server) -> SandboxTier | REFUSE` signature; ADR-D2 source-set token bump v1.1 → v1.2 with comprehensive body-citation alignment at 40 sites under use-latest-version discipline reflecting the parallel ADR-D2 v1.1 → v1.2 reconciliation; §[coherence pass] section preserved verbatim as v1 point-in-time audit) |
| Revision date | 2026-05-15 |
| Revision | v1.2 → v1.3 (Phase 7 C-AS-05 `fetch_secret` signature reconciliation per `spec-writer` application of the operator-ratified Q-R3-2 / decision D1 R1-direction decision — 2026-05-15; C-AS-05 contract title + §5.1 signature + §5.1 parameter table + §6.2 + §8.4 reconciled from the 2-parameter `fetch_secret(name, scope) -> SecretRef` form to the 3-parameter `fetch_secret(name, scope, tier) -> SecretRef` form, where `tier` is the call site's resolved `SandboxTier` passed as a plain explicit argument — not a bundled context object; aligns C-AS-05 with AS plan U-AS-20's body per `Implementation_Plan_Action_Surface_v1_2.md`; no other section changed) |
| Revision date | 2026-05-15 |
| Revision | v1.3 → v1.4 (Phase A.2 ratified-drafts apply pass per `.harness/Phase_A_2_Contract_Drafts_v1.md` — 2026-05-21; C-AS-14 §14.3 + C-AS-15 §15 extended with producer-site reference notes ONLY; `mcp.*` 7-attribute namespace at H_T-as-MCP-client site is now contracted via CP spec v1.10 §27 C-CP-27 MCPClientNamespaceEmitter; `sandbox.*` namespace at tool-invocation site is now contracted via runtime spec v1.13 §14.9 C-RT-19 RuntimeToolDispatcher; no field-set change, no attribute-list change, no AS-AL rule added, no other section changed) |
| Revision date | 2026-05-21 |
| Revision | v1.4 → v1.5 (Class 1 fork resolution apply pass per `.harness/class_1_fork_h_t_cp_16_17_executable_consumer_absence.md` §16 — 2026-05-23; C-AS-14 §14.7 NEW producer-site reference footer note for `memory.*` 6-attribute namespace pointing at runtime spec v1.17 §14.5.1 C-RT-15 callback-injection + §14.12 C-RT-22 `MemoryToolRegistry` per-callback emission discipline; Memory tool client-side per ADR-D3 §1.1 #11 — per-callback emission structurally distinct from §14.3 mcp.* per-dispatch pattern; Files API §14.6 footer NOT authored per §14.C ratification; pure annotation-level extension; no field-set change, no AS-AL rule added) |
| Revision date | 2026-05-23 |
| Revision | v1.5 → v1.6 (Class 1 fork resolution apply pass per `.harness/class_1_fork_as_4_f4_enum_taxonomy_mismatch_and_production_bug.md` Reading B — 2026-05-25; C-AS-15 §15 extended with NEW §15.8 `MCPInvocationFailClass` 4-value StrEnum (`transport` / `protocol_error` / `schema_violation` / `timeout`) + NEW §15.9 `mcp.fail.class` attribute on `sandbox.violation` child span + NEW §15.10 best-effort projection table MCP-shape → F4-shape; F4 enum at §4.1 PRESERVED VERBATIM; existing §15.1..§15.7 PRESERVED VERBATIM; additive substantive amendment authored at AS-axis as canonical declaration site for MCP-protocol-layer fail-class taxonomy sibling to F4 process-execution-layer taxonomy at C-AS-04; producer-side mutation discipline at runtime spec §14.9 owns the dispatcher-side mapping per existing v1.4 §14.3 footer producer-vs-canonical-schema separation pattern; resolves AS-4 retirement gate at sandbox.violation emission absence) |
| Revision date | 2026-05-25 |

---

## Change-note (v1.3 → v1.4)

**Trigger.** Phase A.2 ratified-drafts apply pass per `.harness/Phase_A_2_Contract_Drafts_v1.md` (operator-ratified 2026-05-21 at session plan file `/Users/robertrhu/.claude/plans/begin-comprehensive-and-sharded-bird.md` Phase A.2). Three new composer contracts authored at runtime spec v1.13 (§14.9 C-RT-19 + §14.10 C-RT-20) + CP spec v1.10 (§25 + §26 + §27 + §17.4). The new contracts CONSUME the existing `mcp.*` 7-attribute namespace per C-AS-14 §14.3 and `sandbox.*` 7-attribute namespace per C-AS-15 §15. v1.4 adds producer-site reference notes documenting which downstream contract emits each namespace at the canonical tool-invocation site.

**Scope of revision.** Pure annotation-level extension. NO field-set change. NO attribute-list change. NO new AS-AL rule. NO contract signature change. The amendments are documentary back-references to v1.13 runtime spec + v1.10 CP spec contracts:

| Site | Amendment | Reason |
|---|---|---|
| **C-AS-14 §14.3** (footer note) | NEW NOTE: *"At H_T-as-MCP-client sites (i.e., when H_T consumes external MCP servers via runtime spec v1.13 §14.9 `RuntimeToolDispatcher` / `MCPClientHost`), the `mcp.*` 7-attribute namespace is emitted by `MCPClientNamespaceEmitter` per CP spec v1.10 §27 C-CP-27. The attribute set declared at this §14.3 is canonical; CP §27 owns the producer-side mutation discipline at the `mcp.tool.call` span context."* | Documents producer-side ownership of the namespace at the H_T-as-MCP-client tool-invocation site (Class 2 C.1 Path X composer landing). |
| **C-AS-15 §15** (footer note) | NEW NOTE: *"At tool-invocation runtime sites (i.e., the H_T-as-MCP-client dispatch path landed at runtime spec v1.13 §14.9 `RuntimeToolDispatcher`), the `sandbox.*` 7-attribute namespace at §15 + the `sandbox.enter` / `sandbox.violation` / `sandbox.exit` / `sandbox.tier_escalation` event emission is owned by C-RT-19 §14.9.4 span emission discipline. The attribute set + always-sampled discipline declared at this §15 are canonical; runtime §14.9 owns the producer-side span lifecycle."* | Documents producer-side ownership of sandbox observability at the H_T-as-MCP-client tool-invocation site. |

**Sections preserved verbatim from v1.3.** All v1.3 content outside the two footer notes preserved verbatim. C-AS-01 through C-AS-16 (v1.3 numbering) preserved. The v1.3 + v1.2 + v1.1 + v1 chain preserved.

**Status posture.** Proposed (v1.3) → **Proposed (v1.4)**. v1.4 is a documentary-only patch — two producer-site reference NOTEs; no signature change; no acceptance criterion change.

**Downstream absorption owed (post-v1.4).**
(a) Workspace `CLAUDE.md` §2.3 AS row version bump (v1.3 → v1.4).
(b) `harness-as/CLAUDE.md` §1.2 + §4.1 retirement-table extensions (H_T-AS-2 / H_T-AS-4 / H_T-AS-5 / H_T-AS-8 transition shapes pending runtime spec v1.13 §14.9 implementation arc).
(c) Co-published with runtime spec v1.13 + CP spec v1.10 in this single Phase A.2 arc.

**Adjacent defects surfaced (not patched).** None.

---

## C-AS-14 §14.3 producer-site reference note (NEW at v1.4)

> **Producer-site reference (v1.4).** At H_T-as-MCP-client sites — i.e., when H_T consumes external MCP servers via runtime spec v1.13 §14.9 `RuntimeToolDispatcher` / `MCPClientHost` — the `mcp.*` 7-attribute namespace declared at this §14.3 is **emitted by `MCPClientNamespaceEmitter`** per CP spec v1.10 §27 C-CP-27. The attribute set (`mcp.server.name`, `mcp.server.trust_tier`, `mcp.protocol_version`, `mcp.transport`, `mcp.auth_present`, `mcp.primitive.kind`, `mcp.primitive.signature.sha256`) and sampling discipline (head=1.0 always) declared at this §14.3 are canonical; CP §27 owns the producer-side mutation discipline at the `mcp.tool.call` span context. Producer-vs-canonical-schema separation per D6 ingestion-pattern discipline (workspace `CLAUDE.md` §1.1: "CP emits, OD ingests; canonical schema at OD"; analogous discipline applies here: "CP-axis emits, AS-axis owns canonical schema").

---

## C-AS-15 §15 producer-site reference note (NEW at v1.4)

> **Producer-site reference (v1.4).** At tool-invocation runtime sites — i.e., the H_T-as-MCP-client dispatch path landed at runtime spec v1.13 §14.9 `RuntimeToolDispatcher` — the `sandbox.*` 7-attribute namespace at this §15 plus the `sandbox.enter` / `sandbox.violation` / `sandbox.exit` / `sandbox.tier_escalation` event emission are **owned by C-RT-19 §14.9.4** span emission discipline. The attribute set (`sandbox.tier`, `sandbox.tech`, `sandbox.provider`, `sandbox.policy.assigned_tier_reason`, `sandbox.cost.tier_overhead_ms`, `sandbox.fail.class`, `sandbox.tier_escalation` event) plus always-sampled discipline (head=1.0 for `sandbox.violation` + `sandbox.tier_escalation`) declared at this §15 are canonical; runtime §14.9 owns the producer-side span lifecycle.

---

## C-AS-14 §14.7 producer-site reference note (NEW at v1.5)

> **Producer-site reference (v1.5).** At H_T-as-Memory-tool-consumer sites — i.e., when H_T invokes Anthropic Memory tool via runtime spec v1.17 §14.5.1 C-RT-15 callback-injection composer-step + §14.12 C-RT-22 `MemoryToolRegistry` — the `memory.*` 6-attribute namespace declared at this §14.7 is **emitted by the storage-backend callback** per C-RT-15 §14.5.1 step 4 + C-RT-22 §14.12.2 invariant 2. The attribute set (`memory.operation.kind`, `memory.path`, `memory.backend`, `memory.bytes_read`, `memory.bytes_written`, `memory.context_editing_active`) plus sampling discipline (head=1.0 at `kind ∈ {write, update, delete}` audit-floor; base-rate at `kind ∈ {read, list}`) declared at this §14.7 are canonical; runtime spec §14.5.1 + §14.12 own the producer-side span lifecycle at each storage-backend callback boundary.
>
> **Structural-pattern divergence from §14.3 mcp.* footer note.** Memory tool is **client-side** per ADR-D3 §1.1 #11 — the harness implements the storage backend; the Anthropic SDK runs the message loop; the harness storage-backend callback emits one `memory.operation` span per CRUD invocation (5 callbacks per C-RT-22 §14.12.1: `view` / `create` / `delete` / `str_replace` / `insert`). This is **per-callback emission**, not per-dispatch as in the §14.3 mcp.* pattern (single `mcp.tool.call` span per C-RT-19 §14.9.4 dispatch). The producer-vs-canonical-schema separation per D6 ingestion-pattern discipline (workspace `CLAUDE.md` §1.1) applies analogously: runtime spec §14.5.1 + §14.12 emit at callback sites; AS spec §14.7 owns the canonical attribute-set schema + sampling discipline + audit-floor commitment.
>
> **Files API §14.6 footer note NOT authored at v1.5.** Per `.harness/class_1_fork_h_t_cp_16_17_executable_consumer_absence.md` §14.C ratification (2026-05-23): Files API runtime executable consumer arc deferred indefinitely. The §14.6 `files.*` namespace declaration retains canonical status without a producer-site footer reference until the future Files arc opens.

---

## Change-note (v1.2 → v1.3)

**Trigger.** Phase 7 R3.1 AS micro-pass. The AS-plan verbatim audit surfaced a C-AS-05 internal contradiction (AS plan U-AS-20 declared a 3-parameter `fetch_secret(name, scope, tier)` while spec §5.1 + the C-AS-05 contract title read the 2-parameter `fetch_secret(name, scope)` form). The R3 implementation-planner pass carried U-AS-20 with a conditional body (`.harness/revision_R3_as_plan.md` §5 + Q-R3-2). The operator ratified decision D1 / Q-R3-2 (`.harness/decision_brief_R3-1_R4.md` D1 — "R1 direction — the spec adopts the 3-param form") on 2026-05-15. This revision applies that decision. It discharges action item A-5 flagged at `Implementation_Plan_Action_Surface_v1_2.md` §0.6.

**Scope of revision.** C-AS-05's `fetch_secret` contract signature is reconciled from the 2-parameter `fetch_secret(name: string, scope: SecretScope) -> SecretRef` form to the 3-parameter `fetch_secret(name: string, scope: SecretScope, tier: SandboxTier) -> SecretRef` form. The `tier` argument is the resolved sandbox tier of the call site, passed as a plain explicit argument — **not** a bundled context object — for parity with the C-AS-02 `sandbox_tier_floor` G-1 explicit-argument resolution already landed at spec v1.2 and so the tier-aware resolution input is visible at the call surface. `tier` is resolved at the call site per C-AS-10 (consistent with AS plan U-AS-20, where U-AS-08 resolves it). The §5.2 tier-aware resolution table is unchanged — `tier` makes explicit the input that table was already keyed on.

**Sub-decisions.** None — the fix is fully decided by the operator-ratified Q-R3-2 / D1 R1-direction decision; this pass applies the 3-parameter signature verbatim per AS plan U-AS-20's body.

**Sections revised (substantive).** C-AS-05 contract title (`## §5` heading — `fetch_secret(name, scope)` → `fetch_secret(name, scope, tier)`). §5.1 function signature — the signature line gains the `tier: SandboxTier` parameter; the §5.1 parameter table gains a `tier` row. §6.2 "Allowlist intersection" row — the `fetch_secret(name, scope)` call reference updated to `fetch_secret(name, scope, tier)` (arity-asserting back-reference; the `(name, scope)` allowlist-tuple itself is unchanged — `tier` is not an allowlist-key dimension). §8.4 "One ledger entry per successful fetch" + "One ledger entry per failed fetch" rows — the `fetch_secret(name, scope)` call references updated to `fetch_secret(name, scope, tier)` (arity-asserting back-references; the rest of each row unchanged).

**Sections preserved verbatim.** All of §1–§4; C-AS-05 §5.2 + §5.3 + §5.4 + §5's "Deferred to implementation discretion"; §6 C-AS-06 except the §6.2 "Allowlist intersection" row — including §6.1's `SecretAllowlistEntry` comments `matches fetch_secret(name, ...) parameter` / `matches fetch_secret(..., scope) parameter` (ellipsis-form parameter-name references, not arity assertions — the `...` already stands for unspecified parameters, so the comments remain true and are preserved verbatim); §6.3; §7; §8 C-AS-08 except the two §8.4 per-fetch-emission rows; §9–§16; §[traceability] matrix; §[carry-forwards]; §[coherence pass] section (v1 point-in-time historical audit). No citation tokens touched.

**Surfaced findings (not patched).** None — all `fetch_secret` arity-asserting sites (C-AS-05 title, §5.1, §6.2, §8.4) are reconciled in this pass; no adjacent defect surfaced.

**Downstream absorption owed (`implementation-planner` revision-pass / operator).** AS plan U-AS-20 already applies the 3-parameter `fetch_secret` body per the operator-ratified R1 direction (`Implementation_Plan_Action_Surface_v1_2.md`); its `Implements` C-AS-05 citation may be bumped to spec v1.3 at the next plan touch (the §0.6 A-5 caveat is now discharged at the spec layer). Workspace root `CLAUDE.md` §2.3 lists the AS spec at v1.2; a follow-up token bump to v1.3 is owed (out of spec-writer remit; flagged).

---

## Change-note (v1.1 → v1.2)

**Trigger.** Phase 7 C-AS-02 `sandbox_tier_floor` contract self-contradiction surfaced by the AS-plan verbatim audit (`verbatim_audit_as_plan.md` F3-01 / Pattern A2) and re-stated by the R3 implementation-planner pass. The `systems-architect` S1 reconciliation recommendation (`.harness/s1_c_as_02_reconciliation.md`, authored 2026-05-15) was operator-ratified 2026-05-15; this revision applies it. `sandbox_tier_floor` was called at five spec sites (§2.2, §2.3, §10.2, §11.1, §12.1) with three different signatures — §2.2/§10.2/§12.1 with a 4-arg `(tool, deployment_surface, blast_radius_tier, mcp_transport)` form, §11.1 with a 3-arg `(blast_radius, deployment_surface, mcp_transport)` form omitting `tool`, and the §2.3 lookup table requiring an MCP-server trust-level input no call site threaded.

**Scope of revision.** Reconcile all `sandbox_tier_floor` call sites to one canonical 5-argument signature: `sandbox_tier_floor(tool, deployment_surface, blast_radius_tier, mcp_transport, mcp_server) -> SandboxTier | REFUSE`. The `tool` argument is retained (§2.3 rows 1–2 — computer-use / LLM-generated-code-execution — are tool-keyed; the 3-arg §11.1 form could not evaluate them). The MCP-server trust-level input the §2.3 lookup table requires (rows 4–6) is threaded as the explicit `mcp_server` argument (G-1, explicit-argument resolution — the same `call_site_context.mcp_server` the sibling `mcp_server_trust_tier_floor` already consumes at §2.2; not carrier-borne, for parity with the four sibling `max()` floors and the `assigned_tier_reason` audit surface). No §2.3 lookup-table rows are changed; the row→argument keying is made explicit.

**Sub-decisions.** None — the fix is fully decided by the operator-ratified S1 recommendation; this pass applies the 5-arg signature and the row→argument keying note verbatim per `s1_c_as_02_reconciliation.md` §3.3 + §4.

**Sections revised (substantive).** §2.2 composition formula — the `sandbox_tier_floor(...)` call gains `call_site_context.mcp_server` as the fifth argument. §2.3 `sandbox_tier_floor` lookup table — no row changes; a row→argument keying contract note added beneath the table tying each row band to its keying argument, closing the "table requires an input the signature lacks" gap. §10.2 — the prose `sandbox_tier_floor(tool, deployment_surface, blast_radius_tier, mcp_transport)` reference in the "Floor input" row updated to the 5-arg form. §11.1 sub-agent tier-resolution signature — the `sandbox_tier_floor(blast_radius, deployment_surface, mcp_transport)` body call reconciled to the canonical 5-arg form, and `sub_agent_sandbox_tier`'s outer signature gains `tool` and `mcp_server` parameters so it has them to thread through. §12.1 — the `sandbox_tier_floor(tool, deployment_surface, blast_radius_tier, mcp_transport)` call in the `gate_level` body gains the `mcp_server` argument (`gate_level`'s outer signature already carries `mcp_server`).

**Body-citation alignment (token-level, non-substantive).** ADR-D2 source-set token bump v1.1 → v1.2 applied under use-latest-version discipline (the named discipline this spec applied at the v1 → v1.1 pass for the ADR-D3 bump). Comprehensive `ADR-D2 v1.1` → `ADR-D2 v1.2` citation alignment at 40 sites — the Source-set field (`ADR-D2.md` v1.1 → v1.2), the §"ADR scope" note ("D2 v1.1" → "D2 v1.2"), and 38 body-citation sites across §[requirement-trace], §[carry-forwards], the C-AS-02 / C-AS-04 / C-AS-09 / C-AS-10 / C-AS-11 / C-AS-12 / C-AS-15 / C-AS-16 contracts (`Per ADR-D2 v1.x §...` and `ADR commitment(s) honored` lines). Token-level only; the cited ADR-D2 content at §1.1–§1.10 is materially unchanged except §1.4 / §1.5.1 (the reconciled `sandbox_tier_floor` signature) — those two citations' targets changed substantively and are reconciled here per spec-writer SKILL §5 intra-file back-reference discipline. The §[coherence pass] section (lines 1295 / 1348 / 1350 `ADR-D2 v1.1` occurrences) and this Change-note's own §"Downstream absorption owed" historical reference to `ADR-D2 v1.1` are preserved verbatim as point-in-time records.

**Sections preserved verbatim.** §Front-matter except the new Revision / Revision date line pair + the Source-set `ADR-D2.md` token + the §"ADR scope" "D2" token; §1 C-AS-01 (citation tokens aligned only); §2 C-AS-02 except §2.2 + §2.3 substantive edits (§2.1 + §2.4 + §2.5 unchanged; citation tokens aligned); §3–§9 (citation tokens aligned only); §10 C-AS-10 except the §10.2 "Floor input" row (§10.1 + §10.3 unchanged; citation tokens aligned); §11 C-AS-11 except the §11.1 signature (§11.2 + §11.3 unchanged; citation tokens aligned); §12 C-AS-12 except the §12.1 `gate_level` body (§12.2 + §12.3 unchanged; citation tokens aligned); §13–§16 (citation tokens aligned only); §[traceability] matrix; §[carry-forwards] (citation tokens aligned); §[coherence pass] section (preserved verbatim as the v1 point-in-time historical audit — its `ADR-D2 v1.1` references left as accurate v1-audit record).

**Surfaced findings (not patched).** None — all five `sandbox_tier_floor` sites are reconciled in this pass; no adjacent defect surfaced.

**Downstream absorption owed (`implementation-planner` revision-pass).** AS plan units U-AS-06 (`sandbox_tier_floor` carrier — its Signatures block already declared the 5-arg form) and U-AS-09 (`sub_agent_sandbox_tier` carrier) require an R3.1 micro-pass to finalize bodies against the reconciled signature. U-AS-05 / U-AS-10 / U-AS-13 are re-verify-only. Workspace root `CLAUDE.md` §2.2 ADR-version table lists `ADR-D2 v1.1`; a follow-up token bump to `v1.2` is owed (out of spec-writer remit; flagged). ADR-D2 itself was revised v1.1 → v1.2 in the same reconciliation (the contradiction originated at the ADR layer).

---

## Change-note (v1 → v1.1)

**Scope of revision.** Source-set ADR-D3 version-bump revision pass per `P5-CK_Iteration_1_Close_Handoff.md` §3.1 + §6.1 row 7 — Source-set field `ADR-D3.md` v1.1 → v1.2 reflecting Stage 1 ADR-D3 revision (F-AS-01 closure: §Decision nine-component → nine-commitment terminology + nine-primitive → eleven-primitive enumeration alignment with §1.1 body canonical eleven-primitive count). Comprehensive body-citation alignment v1.1 → v1.2 applied under Stage 4 use-latest-version discipline (28 sites across §Axis-grounding note + R-AS-07 PRD requirement citation + C-AS-13 ADR commitments + §13.x lifecycle commitment citations + C-AS-14 ADR commitments + §14.x namespace declaration citations).

**Sub-decisions.** None — F-AS-01 closure was mechanical at the upstream ADR (Stage 1) + PRD R-AS-07 citation (Stage 2). C-AS-13 §13.1 body verified to cite §1.1 body canonical eleven-primitive count per handoff §3.1 confirmation; no §Decision-text restatement defect surfaced; substantive AS-spec content unchanged.

**§13.1 verification.** C-AS-13 §13.1 ADR-anchored eleven-primitive enumeration reads §1.1 body of ADR-D3 (canonical eleven-primitive count) rather than the prior §Decision text (which formerly read "nine-primitive" at v1.1). The Stage 1 ADR-D3 §Decision revision aligned the §Decision text with §1.1 body (both now say "eleven-primitive enumeration" at v1.2). C-AS-13 §13.1 was already substrate-anchored to the §1.1 body and required no content amendment; the §Decision-text alignment at upstream ADR is transparent to this spec's content commitments.

**Citation-version alignment scope.** Body citations updated under use-latest-version discipline. The cited content at ADR-D3 §1.1–§1.9 and §1.8.1 is materially unchanged in v1.2 — Stage 1 ADR-D3 v1.1 → v1.2 modified §Decision text only (nine-component → nine-commitment; nine-primitive enumeration → eleven-primitive enumeration). Citation tokens bumped for within-spec consistency with Source-set; no semantic content drift introduced.

**Forward-flagged out-of-scope discoveries (non-blocking iteration 2).** Three concerns inherited from Stage 3b/3c/4:

1. **CP §24.1 export table ↔ D6 §1.2 ingest map substrate-level alignment drift** (Stage 3b §35.5). CP §24.1 enumerates 11 namespaces; D6 §1.2 specialization-layer map enumerates only six CP-source namespaces. Resolution path is operator decision at iteration 2 entry-gate or downstream D6 v1.2 revision.

2. **F-CP-02 OD-RP-3.A Reading 1 vs D6 §1.2 row naming.** D6 §1.2 declares `topology.fanout.*` directly as a namespace; Reading 1 interprets it as a sub-tree under broader `topology.*`. Substrate-level resolution may require D6 v1.2 rename for full cross-spec alignment.

3. **F-CP-01 attribute semantic-loss** (`breaker.cause` + `breaker.cooldown_ms` dropped under canonical 4-attr → 7-attr replacement). Re-introduction would require OD C-OD-07 §7.1 schema expansion. Operator-decision territory at iteration 2 entry-gate.

**Sections preserved verbatim.** §Front-matter except Axis-grounding note bare-form D3 v1.1 → v1.2 at line 28; §1 C-AS-01 + §2 C-AS-02 + §3 C-AS-03 + §4 C-AS-04 + §5 C-AS-05 + §6 C-AS-06 + §7 C-AS-07 + §8 C-AS-08 + §9 C-AS-09 + §10 C-AS-10 + §11 C-AS-11 + §12 C-AS-12 (all F4-anchored + F5-anchored + D2-anchored contracts); §13 C-AS-13 entire contract (every ADR-D3 v1.1 citation → v1.2 token-level alignment only; substantive content preserved verbatim); §14 C-AS-14 entire contract (every ADR-D3 v1.1 citation → v1.2 token-level alignment only; substantive content preserved verbatim; lines 936 + 937 historical parentheticals "(v1.1 — F2-11 Reading 2 closure)" preserved as accurate ADR-D3 v1.1 namespace-introduction event references); §15 C-AS-15 + §16 C-AS-16 (substrate seam exports surface); §[traceability] matrix; §[carry-forwards]; §[coherence pass] section lines 1282–1361 (preserved verbatim as v1 point-in-time historical audit per Stage 2 + Stage 3a + Stage 3b + Stage 3c + Stage 4 precedent — audit rows referencing v1 substrate state, including "F4 v1.1 / F5 v1.1 / D2 v1.1 / D3 v1.1" enumeration at line 1276, are accurate historical record of the v1 audit pass; v1.1 → v1.2 (if needed at iteration 2 entry or post-iter-2) is the proper moment for fresh coherence pass).

**Status posture.** `Status: Proposed (v1.1 pending P5-CK iteration 2 clearance per Project_Workflow_v1_2.md §3.1)`. v1.1 enters P5-CK iteration 2 as input artifact alongside ADR-D3 v1.2, PRD v1.0.1, IS spec v1.1, CP spec v1.1, OD spec v1.1, and composition doc v1.1 per handoff §6.1 entry-gate checklist (all rows ✅ MET).

**Changes inline.** Status block (Status row revised; Source-set ADR-D3 token bumped v1.1 → v1.2 via bounded sed; Revision row + Revision date row appended). This Change-note section (new). §Front-matter Axis-grounding note line 28 (bare-form D3 v1.1 → v1.2 alignment). Body citation tokens at 27 sites across §13 + §14 + §Front-matter (R-AS-07 + ADR scope + Axis-grounding note) bumped ADR-D3 v1.1 → v1.2 via bounded sed (line range 1–1281). No semantic content modified — token-level version-citation alignment only.

**§[coherence pass] preservation discipline.** §[coherence pass] section is v1 point-in-time audit; v1.1 mechanical revision does not re-run the audit. Audit rows referencing v1 substrate state (including ADR-D3 v1.1 references at lines 1276, 1291, 1293, 1318) are accurate historical record of the v1 audit pass; v1.1 → v1.2 (if needed at iteration 2 entry or post-iter-2) is the proper moment for fresh coherence pass.

---

## Front-matter

### Axis declaration

Per OD-5-2.A spec-writer judgment with handoff §3.1 recommendation followed: **Action Surface** is the session-2 axis.

### Axis-grounding note

The Action Surface axis hosts **two foundational ADRs** (F4 v1.1 graduated-isolation four-tier sandbox; F5 v1.1 tier-aware secret-fetch abstraction) and **two derivative ADRs** (D2 v1.2 specific sandbox provider per cell; D3 v1.2 Anthropic-primitive adoption depth) per ADD §2.4 + §2.5 + §3.3.1 + §3.3.2. Cross-axis composition with:

- **Information Substrate** (this spec consumes C-IS-05 entry shape + C-IS-06 hash-chain construction + C-IS-07 read/write contract pair + C-IS-10 substrate seam exports at session-1 spec citations)
- **Control Plane** (this spec exports the sandbox-bounded span schema and Anthropic-primitive adoption-depth surfaces for D5 HITL composition, D4 sub-agent privilege, and D1 engine-class composition at session 3)
- **Operational Discipline** (this spec exports the `sandbox.*` + six Anthropic-primitive namespaces for D6 unified span schema ingestion at session 4)

is captured at C-AS-16 (Action Surface substrate seam exports surface) for downstream-axis specs to consume by citation.

### PRD requirement scope

| PRD requirement | Observer role | Primary ADR section citation |
|---|---|---|
| R-AS-01 — Sandbox tier per tool invocation visible at run-event surface | Production-time operator | ADR-F4 v1.1 §Decision; ADR-D2 v1.2 §1.7 + §1.7.1; ADD §2.4 Synthesis |
| R-AS-02 — Sandbox failure-class taxonomy at failure event | Production-time operator | ADR-F4 v1.1 §Consequences (a); ADR-D2 v1.2 §1.8; ADD §2.4 Synthesis |
| R-AS-03 — Per-tool sandbox tier assignment declarable at authoring time | Design-time operator + Production-time operator | ADR-F4 v1.1 §Decision; ADD §2.4 Synthesis |
| R-AS-04 — Secret content never present in stored prompts or logs | Production-time operator (negative observation) | ADR-F5 v1.1 §Decision; ADD §2.5 Synthesis |
| R-AS-05 — Secret-fetch audit as structure-not-content event | Downstream maintainer | ADR-F5 v1.1 §Decision; ADD §2.5 Synthesis |
| R-AS-06 — Specific sandbox provider per deployment-surface × blast-radius cell | Design-time operator | ADR-D2 v1.2 §Decision + §1.5; ADD §3.3.1 Synthesis |
| R-AS-07 — Anthropic-primitive adoption depth per workload-class cell | Design-time operator | ADR-D3 v1.2 §Decision + §1.7 + §1.8 + §1.8.1; ADD §3.3.2 Synthesis |

### ADR scope

| ADR | Version | Role in axis |
|---|---|---|
| F4 | v1.1 | Foundational; commits four-tier sandbox-isolation tier-set + per-tool `max()`-composed tier-assignment + per-tier capability requirements + tier × deployment-context tech-commitment split |
| F5 | v1.1 | Foundational; commits tier-aware `fetch_secret` abstraction + dev-tech at OS-keyring abstraction layer + structure-not-content audit composition + five fail-class refinements + per-tool secret-allowlist |
| D2 | v1.1 | Derivative; commits 12-cell deployment-surface × blast-radius-tier matrix + provider-class enumeration + per-MCP-transport floor + sub-agent monotonic-ascension + T-perm-1 D2-layer multiplicative tunable specialization + cross-deployment monotonicity + sandbox-bounded span schema |
| D3 | v1.2 | Derivative; commits eleven-primitive adoption-depth matrix + per-engine-class composition overlay + per-sub-agent-role model binding + prompt-cache breakpoint placement + structured-outputs adoption-depth + Anthropic-API graceful-degradation + six attribute namespaces |

### Cross-axis citation substrate

| Source spec | Contracts consumed | Composition shape |
|---|---|---|
| `Spec_Information_Substrate_v1.md` | C-IS-05 (state-ledger entry shape) | C-AS-08 secret-fetch audit entries inherit the six-field record signature; `outputs_hash` populates `response_hash` |
| `Spec_Information_Substrate_v1.md` | C-IS-06 (hash-chain integrity construction) | C-AS-08 audit entries participate in the hash-chain via `prior_event_hash` chaining |
| `Spec_Information_Substrate_v1.md` | C-IS-07 (read/write contract pair) | C-AS-08 audit writes follow the C3-pole append-only structured idempotent write contract |
| `Spec_Information_Substrate_v1.md` | C-IS-10 §10.1 (state-ledger entry shape export — Action Surface row) | C-AS-15 sandbox-violation events join on `idempotency_key` per the cross-axis composition surface |

### Persona-linkage substrate

| Persona anchor | Inheriting requirement(s) |
|---|---|
| §4 (99.9%+ completion SLO at tens-concurrent scale) | R-AS-02 |
| §5 (integration surface — hosted majors + local/open-weight tier; MCP first-class; computer-use first-class) | R-AS-07 |
| §5.1 (computer-use at design-time AND production-time with stronger sandbox tier at production-time) | R-AS-01, R-AS-03, R-AS-04, R-AS-06 |
| §6 (per-workload-class cost ceiling) | R-AS-07 |
| §7 (pragmatic-mixed ecosystem affinity — Anthropic primitives where they fit) | R-AS-07 |
| §8.1 (software engineering — LLM-generated code execution requires F4 sandbox per synthesis §9 Q13) | R-AS-01 |
| §9 (deployment-surface implications — microVM-class isolation required at production-time) | R-AS-06 |
| §10.1 (graduated-isolation as operator-confirmed locked principle) | R-AS-01, R-AS-03, R-AS-04, R-AS-06 |
| §10.2 (cost-attribution-per-span composes against ledger) | R-AS-05 |
| §10.4 (compliance-readiness — hash-chained audit ledger + secrets-handling + sandbox-violation tamper-evidence) | R-AS-02, R-AS-04, R-AS-05, R-AS-06 |

### Scope and out-of-scope

| In scope | Out of scope |
|---|---|
| Specification-grade contract precision for R-AS-01 through R-AS-07 (signatures, schemas, formulas, enums, surface contracts, matrices) | New architectural commitments (Phase 3 territory; back-flow to ADR revision if surfaced) |
| Citation-by-section to PRD requirements + ADR commitments + ADD synthesis paragraphs + Information Substrate spec contracts | ADR revision; ADD revision; PRD revision; Information Substrate spec revision |
| Persona-linkage trace preservation from PRD requirements | Cross-axis spec coherence beyond Information Substrate seam consumption + Action Surface seam exports surface (deferred to session 5 composition document) |
| Cross-axis citation discipline (C-IS-* references at section/contract granularity) | Control Plane / Operational Discipline contracts (sessions 3–4) |
| Action Surface substrate seam exports surface (C-AS-16) for sessions 3–4 to consume by citation | Specific candidate-within-provider-class selection (deferred per ADR-D2 v1.2 §1.10 workload-binding-time × deployment-surface-time contract) |
| §[carry-forwards] inheritance from PRD §[carry-forwards] + session-1 spec §[carry-forwards] | F2-12 closure (parallel `council-orchestrator` C7+C9 session territory; carry-forward only here) |
| Deferred-to-implementation discretion notation per Workflow §2.5.1 exit criteria language | Implementation-grade choices beyond specification surface (specific keyring library bindings, specific vault provider candidates, specific OTLP collector implementations) |

---

## §1 C-AS-01 — Four-tier sandbox-isolation tier-set enumeration

**Contract surface.** Enum with per-tier capability requirements.

**PRD requirement(s) satisfied.** R-AS-01 (sandbox tier per tool invocation visible at run-event surface).

**ADR commitment(s) honored.** ADR-F4 v1.1 §Decision (four-tier sandbox-isolation tier-set: process / container / microVM / full-VM); ADR-F4 v1.1 §Rationale (a) (per-mechanism tradeoff axes); ADD §2.4 Synthesis ("four-tier sandbox-isolation tier-set with `max()`-composed per-tool tier at call time").

**Persona linkage.** Persona §5.1 (computer-use at production-time with stronger sandbox tier); §8.1 (LLM-generated code execution requires F4 sandbox); §10.1 (graduated-isolation as locked principle).

**Specification content.**

### §1.1 Tier-set enumeration

The harness commits to a **four-tier sandbox-isolation tier-set**. Tier identifiers are stable across tech swap (per ADR-F4 v1.1 §Consequences (a) "`sandbox.tier` as structural attribute").

| Tier identifier | Tier label | Mechanism class | Escape risk (per Cluster 3 §2.2 [HIGH]) | Cold-start (per Cluster 3 §2.2 [HIGH]) | Capability requirement |
|---|---|---|---|---|---|
| `tier-1-process` | Tier 1 minimal isolation | Language-level + filesystem-ACL | High if no language sandbox | <10 ms | Read-only operations; deterministic in-house tools at solo-developer non-compliance cells (operator-tunable under §1.5.2 policy override) |
| `tier-2-container` | Tier 2 process isolation | Process isolation with seccomp / namespacing / sandbox-exec (Seatbelt / bubblewrap+socat / filesystem-overlay) | Medium (kernel CVE class) | 10–50 ms | Local-mutation operations; cross-platform filesystem-bound process-tier composable via worktree-isolation per ADR-F2 |
| `tier-3-microvm` | Tier 3 container isolation | Shared-kernel container (Docker / Podman) OR user-space kernel (gVisor) OR microVM-backed container (Kata) | Docker medium / gVisor low / Kata very low | 100–150 ms | External-reversible operations; design-time default Docker-on-OCI per ADR-F4 v1.1 §Decision |
| `tier-4-full-vm` | Tier 4 VM isolation | Hardware-virt microVM (Firecracker) OR full VM (ephemeral; network-egress-restricted) | Very low (hardware boundary) | Firecracker ~150 ms / full-VM seconds | External-irreversible operations; LLM-generated code execution mandatory; computer-use binding forces resolution regardless of nominal blast-radius |

### §1.2 Tier-label stability invariant

| Property | Contract |
|---|---|
| **Identifier stability across tech swap** | Tier identifiers (`tier-1-process` / `tier-2-container` / `tier-3-microvm` / `tier-4-full-vm`) are stable across mechanism-class swap; `sandbox.tier` is the structural attribute, `sandbox.tech` is the swap-friendly discriminator (per ADR-F4 v1.1 §Consequences (a) line 40) |
| **Cardinality bound** | Four values; new tier additions are a Workflow §4.1.2 Class-2 ADR-F4 revision |
| **Per-tier capability lower bound** | A tier's capability-requirement column above is the **lower bound** of what operations the tier accommodates; higher tiers structurally accommodate lower-tier operations (tier monotonicity per §1.1 escape-risk descending) |

### §1.3 Forced-tier rules

Two rules force tier resolution regardless of declared per-tool minimum:

| Forcing condition | Forced tier | Source |
|---|---|---|
| `code-execution-2025-08-25` beta invoked | `tier-4-full-vm` (microVM minimum) | ADR-D2 v1.2 §1.1 LLM-generated-code-execution cells |
| Computer-use model bound | `tier-4-full-vm` (full-VM; ephemeral; network-egress-restricted) | ADR-D2 v1.2 §1.1 Computer-use cells |

**Deferred to implementation discretion.** Specific tier-mechanism candidate within class at microVM / full-VM tiers per deployment surface (per ADR-D2 v1.2 §1.10 contract); specific container-runtime selection within `tier-3-microvm` (Docker / Podman / containerd) per Pattern Reference Catalog v1.0 §11.3.2 derivative.

---

## §2 C-AS-02 — Per-tool sandbox tier `max()` composition formula

**Contract surface.** Function signature + composition formula + `sandbox_tier_floor` lookup table.

**PRD requirement(s) satisfied.** R-AS-01 (sandbox tier per tool invocation visible — composition half); R-AS-03 (per-tool sandbox tier assignment declarable at authoring time — runtime resolution half).

**ADR commitment(s) honored.** ADR-F4 v1.1 §Decision (per-tool tier assignment computed as `max(contract.minimum_tier, blast_radius_floor, mcp_server_trust_tier_floor, operator_policy_floor)` per call site); ADR-D2 v1.2 §1.5.1 (composition rule extending F4 with `sandbox_tier_floor` axis); ADD §2.4 Synthesis; ADD §5.2.1 T-perm-1 D2-layer multiplicative tunable.

**Persona linkage.** Persona §5.1 (broad action surface — code execution, computer-use, MCP, API/SaaS); §10.1 (graduated-isolation locked).

**Specification content.**

### §2.1 Composition signature

```
sandbox_tier(tool, call_site_context) -> SandboxTier
```

where `SandboxTier ∈ {tier-1-process, tier-2-container, tier-3-microvm, tier-4-full-vm}` per C-AS-01 §1.1.

### §2.2 Composition formula

```
sandbox_tier(tool, call_site_context) =
    max(
        tool.contract.minimum_tier,                                          # F4 C4-side capability-introspection
        blast_radius_floor(call_site_context.taint_state),                  # F4 C10 four-tier taxonomy
        mcp_server_trust_tier_floor(call_site_context.mcp_server),          # F4 C10 five-tier framework
        sandbox_tier_floor(                                                  # D2 §1.5.1 NEW
            tool,
            call_site_context.deployment_surface,
            call_site_context.blast_radius_tier,
            call_site_context.mcp_transport,
            call_site_context.mcp_server
        ),
        operator_policy_floor(call_site_context.persona_tier)                # F4 + D5 §1.5
    )
```

The composition is **monotonically rising `max()`** — every floor expresses its concern; the higher tier always wins by construction; neither C4 (capability-introspection) nor C10 (gating) is suppressed.

### §2.3 `sandbox_tier_floor` lookup table

Per ADR-D2 v1.2 §1.5.1:

| Condition | `sandbox_tier_floor` |
|---|---|
| Computer-use model bound, any deployment surface | `tier-4-full-vm` (ephemeral; network-egress-restricted) |
| LLM-generated code execution, any deployment surface | `tier-4-full-vm` (microVM minimum; E2B Firecracker class) |
| STDIO MCP transport, any blast-radius | `max(tier-3-microvm, blast_radius_floor)` |
| Remote MCP, trust level 0 (refuse-remote) | `REFUSE` (sentinel; harness rejects connection at MCP server registration) |
| Remote MCP, trust level 2 (sandbox-all) | `max(tier-4-full-vm, blast_radius_floor)` with allow-listed upstream domains |
| Remote MCP, trust level 1 (signed-pinned) OR trust level 3 (allow-with-audit) | `blast_radius_floor` |
| Read-only, deterministic in-house tool | `tier-1-process` (operator-tunable at solo-developer × non-compliance cells per §1.5.2 per C-AS-12) |
| Local-mutation, any | `tier-2-container` |
| External-reversible, any | `tier-3-microvm` |
| External-irreversible, any | `tier-4-full-vm` |

**Row→argument keying.** `sandbox_tier_floor` is a 5-argument function — `sandbox_tier_floor(tool, deployment_surface, blast_radius_tier, mcp_transport, mcp_server) -> SandboxTier | REFUSE` per ADR-D2 v1.2 §1.5.1. Each row band of the table above is keyed on a specific named argument: rows 1–2 (`Computer-use model bound` / `LLM-generated code execution`) are keyed on the **`tool`** argument — these are tool / call-site classifications, not properties of blast-radius or transport; row 3 (`STDIO MCP transport, any blast-radius`) is keyed on the **`mcp_transport`** argument; rows 4–6 (`Remote MCP, trust level 0` / `level 2 sandbox-all` / `level 1 OR level 3`) are keyed on the remote-MCP trust level read from the **`mcp_server`** argument — trust level is not derivable from `mcp_transport` (a Streamable-HTTP server may be any of Level 1/2/3 per §10.3), so the `mcp_server` argument supplies it; rows 7–10 (`Read-only` / `Local-mutation, any` / `External-reversible, any` / `External-irreversible, any`) are keyed on the **`blast_radius_tier`** argument. This keying makes explicit that every row band's discriminating input is a named argument of the 5-arg signature; no row requires an input the signature does not carry.

### §2.4 `blast_radius_floor` enum

Per ADR-D2 v1.2 §1.1 four-tier blast-radius taxonomy:

| Blast-radius tier | Semantic | Default `sandbox_tier_floor` (subject to forcing-condition overrides) |
|---|---|---|
| `read-only` | No state mutation; pure data read | `tier-1-process` |
| `local-mutation` | Filesystem / process / state mutation within sandbox | `tier-2-container` |
| `external-reversible` | External effects rollbackable (e.g., HTTP write to durable record with rollback API) | `tier-3-microvm` |
| `external-irreversible` | External effects not rollbackable (e.g., email send, payment, computer-use input) | `tier-4-full-vm` |

### §2.5 Composition output verification

Per R-AS-01 acceptance criterion: the resolved `sandbox.tier` value is **verifiable at the `sandbox.enter` event** as the `max()` of the formula's five input floors. Verification surface is the sandbox-bounded span schema per C-AS-15 — `sandbox.tier` plus `sandbox.policy.assigned_tier_reason` (enum naming which floor source won the `max()`) plus the inputs recoverable via call-site context attributes.

**Deferred to implementation discretion.** Specific `blast_radius_floor()` taint-state propagation mechanism (per-call dataflow analysis vs operator-annotated vs hybrid); specific `mcp_server_trust_tier_floor()` registry lookup mechanism; specific `operator_policy_floor()` audit-ledger entry construction (composed against C-AS-08).

---

## §3 C-AS-03 — Per-tool `minimum_tier` authoring-time declaration

**Contract surface.** Tool contract field signature + declaration discipline.

**PRD requirement(s) satisfied.** R-AS-03 (per-tool sandbox tier declarable at authoring time).

**ADR commitment(s) honored.** ADR-F4 v1.1 §Consequences (a) ("per-tool tier declaration at authoring time via contract-attached `minimum_tier`"); ADR-F4 v1.1 §Rationale (a) (contract-attached `minimum_tier` as C4-side capability-introspection extension); ADD §2.4 Synthesis.

**Persona linkage.** Persona §5.1 (broad action surface — code execution, computer-use, MCP, API/SaaS); §10.1 (graduated-isolation locked).

**Specification content.**

### §3.1 Tool contract field signature

```
ToolContract {
    name: string,
    description: string,
    input_schema: JSONSchema,
    output_schema: JSONSchema,
    minimum_tier: SandboxTier,                  # REQUIRED — drives F4 capability-introspection-floor at C-AS-02
    blast_radius_tier: BlastRadiusTier,          # REQUIRED — drives C-AS-02 default sandbox_tier_floor
    required_secrets: List[SecretAllowlistEntry], # OPTIONAL — per C-AS-06; empty list permitted
    ...
}
```

### §3.2 Declaration discipline

| Property | Contract |
|---|---|
| **Author-time mandatory** | `minimum_tier` is required at tool-contract authoring time; tool contracts missing `minimum_tier` declaration are rejected at tool registration |
| **Authoring-time visibility** | The declared `minimum_tier` is visible to the design-time operator at tool authoring; the runtime-resolved `sandbox.tier` is visible to the production-time operator at the `sandbox.enter` event per C-AS-15 |
| **Non-tier-promoting** | A tool's declared `minimum_tier` cannot lower the runtime-resolved tier below the `sandbox_tier_floor` (per C-AS-02 `max()` composition); a tool MAY declare a higher `minimum_tier` than its blast-radius would imply (capability declaration is an upper-floor bound only when other floors are lower) |
| **Composition reading** | At runtime, the per-tool `minimum_tier` enters C-AS-02 as the first `max()` floor; the C4 capability-introspection-floor is expressed by construction |

### §3.3 Default-tier policy

Per ADR-F4 v1.1 §Consequences (c) "contract-default-tier policy (proposed default `microvm` fail-closed)" — tool registration MAY apply a default `minimum_tier` per the contract-default-tier policy at the tool registry layer. The fail-closed default (`tier-4-full-vm`) is the recommended default-tier policy posture; permissive defaults are operator-tunable at the registry layer with audit-ledger entry per C-AS-08.

**Deferred to implementation discretion.** Specific tool-contract serialization format (JSON / YAML / Python decorator / etc.); specific tool-registry storage and lookup mechanism; specific contract-validation enforcement implementation; specific contract-default-tier policy commitment value (the recommended posture is `tier-4-full-vm`; specific commitment is a tool-registry D-ADR).

---

## §4 C-AS-04 — Sandbox-violation `sandbox.fail.class` taxonomy

**Contract surface.** Seven-value enum + per-class C5/C9 routing posture.

**PRD requirement(s) satisfied.** R-AS-02 (sandbox failure-class taxonomy at failure event).

**ADR commitment(s) honored.** ADR-F4 v1.1 §Consequences (a) line 40 (six-value failure taxonomy seed); ADR-D2 v1.2 §1.8 (seven-value taxonomy with `policy_override` addition); ADR-D2 v1.2 §1.7.1 (canonical attribute declaration); ADD §2.4 Synthesis closing sentence.

**Persona linkage.** Persona §4 (99.9% SLO — failure-class taxonomy is C9-routable substrate for retry policy); §10.4 (compliance-readiness — sandbox-violation events are tamper-evidence-relevant).

**Specification content.**

### §4.1 `sandbox.fail.class` enum

Seven values per ADR-D2 v1.2 §1.7.1 + §1.8 canonical declaration:

| `sandbox.fail.class` | Semantic | C5 fail-class | C9 retry posture |
|---|---|---|---|
| `escape_attempt` | Sandbox containment breach attempt detected (escape from process / container / microVM boundary) | permanent-fail | NO retry; immediate HITL escalation per ADR-D5 v1.3 §1.3 validator-escalation; tamper-evidence-relevant |
| `egress_denied` | Network egress to a destination outside the sandbox's allow-list denied by the sandbox enforcement layer | permanent-fail (deterministic policy hit) | NO retry; tool registry update OR HITL escalation |
| `timeout` | Sandbox-resident execution exceeded per-call time budget | transient-fail | C9 backoff + retry; max 3 attempts per Cluster 3 retry protocol [HIGH] |
| `oom` | Sandbox-resident execution exceeded memory budget | transient-fail | C9 backoff + retry with sandbox-resource adjustment via operator-policy override per C-AS-12 §12.2 |
| `signal` | Sandbox-resident process terminated by external signal (e.g., SIGKILL from operator) | permanent-fail (operator-induced) | NO retry; record audit ledger per C-AS-08 |
| `exit_nonzero` | Sandbox-resident process exited with nonzero status without escape / egress-denial / timeout / OOM | depends on tool contract; C5 fail-classification at gate time | Per-tool C9 retry-exit per Cluster 4 §2.2.3 [HIGH] |
| `policy_override` | Operator-tunable downgrade per C-AS-12 §12.2 (operator-policy override audit-ledger entry, not a containment failure) | informational; not a fail | Audit ledger entry only per C-AS-08; no retry |

### §4.2 Pre-HITL escalation order

Per ADR-D5 v1.3 §1.10 composes (cross-axis surface; full Control Plane composition at session 3):

```
1st sandbox-violation (transient class) → C9 backoff + retry
2nd sandbox-violation (same class)       → C6 model-tier escalation per ADR-D3 v1.2 §1.4
3rd sandbox-violation                    → C11 HITL escalation per ADR-D5 v1.3 §1.3
```

Permanent-fail violations (`escape_attempt`, `egress_denied`, `signal`) **skip the staircase** and route directly to HITL per the discriminated five-class encoding at ADR-D5 v1.3 §1.10.

### §4.3 Sampling discipline at emission

| Emission posture | Rule |
|---|---|
| **Always-sampled (head=1.0)** | `sandbox.violation` events carrying any `sandbox.fail.class` value; `sandbox.tier_escalation` events |
| **Base-rate sampled** | None — sandbox-violation events are uniformly always-sampled per ADR-D2 v1.2 §1.7 sampling discipline |

The always-sampled posture is a **hard floor at the deployment-binding layer** — not operator-tunable at base-rate per ADR-D3 v1.2 §1.8 audit-floor commitments analog.

**Deferred to implementation discretion.** Specific sandbox-violation detection mechanism per tier (seccomp filter / cgroup-OOM-kill detector / Firecracker hypervisor exit-code mapping); specific `signal` source-attribution mechanism; specific `exit_nonzero` per-tool retry-exit policy serialization.

---

## §5 C-AS-05 — `fetch_secret(name, scope, tier) -> SecretRef` signature

**Contract surface.** Function signature + tier-aware resolution discipline + `SecretRef` opaque type.

**PRD requirement(s) satisfied.** R-AS-04 (secret content never present in stored prompts or logs — fetch abstraction half).

**ADR commitment(s) honored.** ADR-F5 v1.1 §Decision (single capability-aware secret-fetch abstraction interface with tier-aware resolution); ADR-F5 v1.1 §"Permanent tensions engaged" T-perm-2 F5-layer closure (process-tier within-turn-snapshot via env vars; microVM/full-VM tier across-turn fresh-fetch via in-sandbox HTTP client); ADD §2.5 Synthesis.

**Persona linkage.** Persona §5.1 (broad action surface — API/SaaS/MCP integrations require credential resolution at every call site); §10.1 (graduated-isolation composition with secrets handling); §10.4 (compliance-readiness — secrets handling).

**Specification content.**

### §5.1 Function signature

```
fetch_secret(name: string, scope: SecretScope, tier: SandboxTier) -> SecretRef
```

where:

| Parameter / return | Type | Semantic |
|---|---|---|
| `name` | `string` | Secret identifier within the scoped namespace; structure-not-content (the name is metadata; the value is fetched opaquely) |
| `scope` | `SecretScope` | Credential-dimension session key per ADR-F5 v1.1 §Context; orthogonal to ADR-F1's routing-dimension session key |
| `tier` | `SandboxTier` | The resolved sandbox tier of the call site, governing which tier-aware resolution mechanism per §5.2 applies; resolved at the call site (per C-AS-10) and passed as a plain explicit argument — **not** bundled in a context object — so the tier-aware resolution input is visible at the call surface |
| `SecretRef` | Opaque handle type | An opaque reference to the resolved secret; **the value is not embedded in `SecretRef`**; tool-internal code accesses the value via tier-specific resolution per §5.2 |

### §5.2 Tier-aware resolution

Per the T-perm-2 F5-layer closure shape at ADR-F5 v1.1 §"Permanent tensions engaged":

| Sandbox tier | Resolution mechanism | T-perm-2 pole expressed |
|---|---|---|
| `tier-1-process` | Direct read into sandboxed process via environment variables at sandbox startup | C2 (within-turn snapshot) |
| `tier-2-container` | Container-environment variable injection at container startup; long-lived agent-process-with-keyring-handles pattern per ADR-F5 v1.1 §Rationale (b) (i) | C2 (within-turn snapshot) |
| `tier-3-microvm` | In-sandbox HTTP client over network using sandbox-identity bootstrap token bounded by sandbox lifetime | C3 (across-turn fresh-fetch) |
| `tier-4-full-vm` | In-sandbox HTTP client over network using sandbox-identity bootstrap token bounded by sandbox lifetime; rotation-aware refresh within sandbox lifetime | C3 (across-turn fresh-fetch) |

Tier choice picks pole; both poles expressed; closure is **structural composition with F4**, not a choice between C2 and C3.

### §5.3 Negative-observation invariant

| Property | Contract |
|---|---|
| **Absence in stored prompts** | Secret values MUST NOT enter the static prompt cache prefix; cache-prefix integrity per ADR-F2 §Rationale (b)(ii) preserved |
| **Absence in log surfaces** | Secret values MUST NOT enter span attributes, log records, or any observability content-attribute capture surface; sensitive-data default-off discipline per ADR-D2 v1.2 §1.7 sampling discipline + structure-not-content per ADR-D6 v1.1 |
| **Absence in ledger** | Secret values MUST NOT enter audit-ledger entries; structure-not-content fingerprint per C-AS-08 is the audit-ledger composition |
| **Sole resolution path** | `fetch_secret` is the **only** path through which secrets reach a sandbox; secret content arriving by any other path (manifest, prompt, log, ledger) is a contract violation |

### §5.4 `SecretRef` opaque-type discipline

| Property | Contract |
|---|---|
| **Opaque** | `SecretRef` exposes no API surface that returns the secret value as a string; access is tier-mechanism-specific (env-var read at process / container tiers; in-sandbox HTTP at microVM / full-VM tiers) |
| **Lifetime-bounded** | `SecretRef` lifetime bounded by sandbox lifetime; release on sandbox termination; no cross-sandbox `SecretRef` sharing |
| **Fresh-on-restart** | Per ADR-F5 v1.1 §Consequences (b): no in-process secret cache across restart boundaries; test-fetch on resumption per ADR-F3 resumption events |

**Deferred to implementation discretion.** Specific keyring-library binding per language ecosystem (`python-keyring` / `keytar` / `@napi-rs/keyring` / `zalando/go-keyring`) — D-derivative per ADR-F5 v1.1 §Consequences (c); specific in-sandbox HTTP client implementation at microVM / full-VM tiers; specific bootstrap-token issuance protocol per prod-tech (AWS STS / Vault wrapped / GCP Workload Identity / etc.) — D-derivative per ADR-F5 v1.1 §Consequences (c); specific `SecretScope` serialization format; specific `pass` / `gpg` headless fallback implementation.

---

## §6 C-AS-06 — Per-tool `required_secrets` allowlist

**Contract surface.** Tool contract field signature + access-control composition + invariant.

**PRD requirement(s) satisfied.** R-AS-04 (secret content never present — access-control half).

**ADR commitment(s) honored.** ADR-F5 v1.1 §Decision (per-tool secret-allowlist `required_secrets` as separate access-control dimension alongside ADR-F4 `assigned_tier`); ADR-F5 v1.1 §"Permanent tensions engaged" (T-perm-1 touch but not re-open — `required_secrets` is NOT a fifth `max()` floor); ADD §2.5 Synthesis.

**Persona linkage.** Persona §10.4 (compliance-readiness — secrets handling); §5.1 (broad action surface — API/SaaS integrations require secrets).

**Specification content.**

### §6.1 Allowlist entry signature

```
SecretAllowlistEntry {
    name: string,                       # secret identifier; matches fetch_secret(name, ...) parameter
    scope: SecretScope,                 # scope dimension; matches fetch_secret(..., scope) parameter
}
```

### §6.2 Access-control composition

| Property | Contract |
|---|---|
| **Allowlist intersection** | A tool's `fetch_secret(name, scope, tier)` call succeeds only if `(name, scope)` ∈ `tool.contract.required_secrets` intersected with the operator-policy override |
| **Not a fifth `max()` floor** | `required_secrets` is an orthogonal access-control dimension alongside `assigned_tier`; secrets and sandbox tier are not tier-promoting per ADR-F5 v1.1 §"Permanent tensions engaged" — `required_secrets` does NOT enter the C-AS-02 `max()` composition |
| **Authoring-time declarable** | `required_secrets` is declared at tool-contract authoring time per C-AS-03; empty list permitted (tool requires no secrets) |
| **Audit composition** | Every successful `fetch_secret` call emits an audit-ledger entry per C-AS-08 |

### §6.3 Secret-passthrough constraint

Per ADR-F5 v1.1 §Decision (MCP authorization spec 2025-06-18 directive [HIGH]):

| Property | Contract |
|---|---|
| **Output redaction** | Tool outputs MUST NOT include secret material; redaction at the C-AS-15 span-emission boundary applies structure-not-content discipline |
| **Input redaction** | Tool inputs containing secrets are redacted in span attributes; the resolved secret is present only inside the sandbox at the tier-specific resolution surface per C-AS-05 §5.2 |
| **MCP-server passthrough prohibition** | An MCP server MUST NOT pass through to upstream APIs the token it received from the MCP client; cross-server secret-leak is structurally prohibited per the MCP authorization spec 2025-06-18 verbatim directive |

**Deferred to implementation discretion.** Specific allowlist-enforcement implementation (per-call lookup vs cached lookup with rotation-invalidation); specific operator-policy override mechanism for `required_secrets` (per-call vs per-session); specific secret-passthrough detection at output emission (regex / fingerprint comparison / cryptographic taint-tracking).

---

## §7 C-AS-07 — Secret-fetch fail-class taxonomy (five cause-attribution refinements)

**Contract surface.** Five-value cause-attribution enum + C9 retry-posture per class + C5/C9 fail-class mapping.

**PRD requirement(s) satisfied.** R-AS-04 (secret content absent — fail-handling half); R-AS-02 cross-cutting (fail-class composition with sandbox fail-class taxonomy per C-AS-04).

**ADR commitment(s) honored.** ADR-F5 v1.1 §Decision (five cause-attribution refinements of the secret-fetch fail surface within the C5/C9 fail-class taxonomy); ADR-F5 v1.1 §Rationale (Framing on the five-class clause) (FM-J cause_attribution + FM-C no-redesign joint compliance); ADD §2.5 Synthesis.

**Persona linkage.** Persona §4 (99.9% SLO — failure-class taxonomy as C9-routable substrate); §10.4 (compliance-readiness — secrets-handling tamper-evidence).

**Specification content.**

### §7.1 `secret.fail.class` enum

Five values; each is a **cause-attribution refinement on the existing C5/C9 fail-class taxonomy** (not a redesigned top-level taxonomy) per ADR-F5 v1.1 §Rationale framing:

| `secret.fail.class` | Cause | C5 fail-class mapping | C9 retry posture |
|---|---|---|---|
| `secret_unknown` | Unprovisioned secret; (name, scope) does not exist in any backend | permanent-fail | NO retry; route to HITL escalation |
| `secret_unavailable` | Transient backend unavailability (vault down, keychain unreachable) | transient-fail | C9 backoff + retry; per-`{secret_backend, scope}` breaker per ADR-F5 v1.1 §Consequences (c) D-derivative |
| `secret_expired` | Short-lived token aged out mid-step | Reflexion-recoverable | Refresh-and-retry with **idempotency-key preservation** per ADR-F2 state-ledger entry shape (`idempotency_key` from C-IS-05 preserved across the refresh attempt) |
| `secret_locked` | Operator-input-required (e.g., macOS keychain ACL prompt blocking unsigned process per ADR-F5 v1.1 §Rationale (b)(i)) | HITL-recoverable | Workload-mode-aware: ephemeral fail-fast; durable pause-and-wait per ADR-F3 lease-coordination |
| `secret_revoked` | Rotation-needed; existing token revoked by backend | HITL-recoverable | Workload-mode-aware: same shape as `secret_locked` with rotation-specific operator signaling |

### §7.2 Composition with C-AS-04

`secret.fail.class` and `sandbox.fail.class` are **orthogonal**: a `secret_expired` cause-attribution at a Tier 4 sandbox does NOT promote to `escape_attempt` and is not a `policy_override` event. The two enums compose at the span-emission layer per C-AS-15 — `tool.call` spans carrying secret-fetch failures emit `secret.fail.class`; sandbox-boundary spans carrying containment violations emit `sandbox.fail.class`.

### §7.3 Per-`{secret_backend, scope}` breaker placement

Per ADR-F5 v1.1 §Consequences (c) (D-derivative deferred per ADR-F5 v1.1 §References "D-ADR on per-`{secret_backend, scope}` breaker placement"):

| Property | Contract |
|---|---|
| **Breaker key** | `(secret_backend, scope)` — analog of ADR-F1 per-`{provider, model}` breaker |
| **Trip condition** | Repeated `secret_unavailable` rate exceeding per-cell threshold; threshold deferred to D-derivative D-ADR |
| **Trip behavior** | Advance-fallback-backend OR fail-closed per cell selection at breaker D-ADR |
| **Composition with C9** | C9 retry/breaker mechanics at session 3 Control Plane spec inherits this contract by citation |

**Deferred to implementation discretion.** Specific `secret.fail.class` detection mechanism per backend (HTTP status code mapping at vault clients; keyring-library error-code mapping at OS-keychain clients); specific breaker trip-threshold values per cell (D-derivative); specific workload-mode-aware ephemeral-vs-durable selection logic (composes with ADR-F3 capability-floor at session 3); specific operator-input mechanism for `secret_locked` / `secret_revoked` HITL prompts.

---

## §8 C-AS-08 — Secret-fetch structure-not-content audit composition

**Contract surface.** `outputs_hash` formula + audit-ledger entry composition + per-fetch event emission discipline.

**PRD requirement(s) satisfied.** R-AS-05 (secret-fetch audit as structure-not-content event).

**ADR commitment(s) honored.** ADR-F5 v1.1 §Decision (structure-not-content fingerprinting `outputs_hash = sha256(secret.name || secret.scope || secret.last_rotated_at)`); ADR-F5 v1.1 §"Permanent tensions engaged" T-perm-2 F5-layer composition against ADR-F2 state-ledger entry shape; ADD §2.5 Synthesis.

**Cross-axis citation.** `Spec_Information_Substrate_v1.md` C-IS-05 (state-ledger entry shape — six-field record); C-IS-06 (hash-chain integrity construction discipline — canonicalize → SHA-256 → prior-event-hash chain); C-IS-07 §7.1 (C3-pole write contract — append-only structured idempotent JSONL); C-IS-10 §10.1 (state-ledger entry shape export — D2 sandbox-violation events row applies analogously to F5 secret-access events).

**Persona linkage.** Persona §10.4 (compliance-readiness — auditable secrets handling without value disclosure); §10.2 (cost-attribution-per-span composes against ledger).

**Specification content.**

### §8.1 `outputs_hash` formula

```
outputs_hash = SHA-256(
    canonicalize_concat(
        secret.name,            # string identifier (structure)
        secret.scope,            # SecretScope identifier (structure)
        secret.last_rotated_at   # ISO-8601 timestamp (version attribute)
    )
)
```

where `canonicalize_concat` is the canonicalization function per C-IS-06 §6.1 (RFC 8785 JCS baseline candidate; library binding deferred per ADR-F2 §Consequences (c)).

### §8.2 Audit-ledger entry shape (composes against C-IS-05)

Every secret fetch emits one ledger entry conforming to the C-IS-05 six-field shape:

| Field (from C-IS-05) | Per-secret-fetch population |
|---|---|
| `action_id` | Harness-generated unique identifier for this fetch event |
| `idempotency_key` | `(thread_id, step_id, idempotency_key)` per Stripe-style convention per C-IS-07 §7.1 |
| `actor` | Agent / sub-agent / operator that originated the fetch |
| `response_hash` | `outputs_hash` per §8.1 above — the structure-not-content fingerprint |
| `timestamp` | Wall-clock instant of fetch event (monotonic non-decreasing per C-IS-05) |
| `prior_event_hash` | Per C-IS-06 §6.3 chain-construction discipline |

### §8.3 Hash-chain integrity composition

| Property | Contract |
|---|---|
| **Chain participation** | Secret-fetch audit entries participate in the F2 state-ledger hash-chain per C-IS-06 §6.3; `prior_event_hash` references the SHA-256 of the prior entry's canonical-JSON byte representation |
| **Tamper-evidence** | Per C-IS-06 §6.5 — entry-content modification, `prior_event_hash` modification, mid-chain insertion / deletion all detectable at chain verification per C-IS-06 §6.4 |
| **Verification surface** | Downstream maintainer verifies secret-fetch audit chain end-to-end via re-canonicalization + SHA-256 recomputation + prior-event-hash traversal per C-IS-06 §6.4 |

### §8.4 Per-fetch emission discipline

| Property | Contract |
|---|---|
| **One ledger entry per successful fetch** | Every `fetch_secret(name, scope, tier)` returning a `SecretRef` emits exactly one audit-ledger entry |
| **One ledger entry per failed fetch** | Every `fetch_secret(name, scope, tier)` returning a non-success result emits exactly one audit-ledger entry with `secret.fail.class` attribute per C-AS-07 |
| **Span emission alongside ledger entry** | Per the C-AS-15 sandbox-bounded span schema and ADR-F5 v1.1 §Consequences (c) `secret.fetch` span attribute schema, a `secret.fetch` span is emitted alongside the ledger entry; span attributes carry `secret.name`, `secret.scope`, `secret.backend`, `secret.fail.class`, `secret.cache.tier_overhead_ms`, `secret.policy.access_decision_reason` (D-derivative span attribute schema deferred per ADR-F5 v1.1 §Consequences (c)) |
| **Negative-observation invariant** | The audit-ledger entry contains the structure (`outputs_hash`) but NOT the secret value; the span attributes contain the structure but NOT the secret value (sensitive-data default-off discipline) |

### §8.5 Cross-axis composition reference

| Consuming axis | Composition reference |
|---|---|
| Information Substrate (C-IS-10 §10.1) | F2 state-ledger entry shape exports to Action Surface; this contract is the consumption surface |
| Operational Discipline (D5 audit-ledger cryptographic shape per persona-tier) | Per-persona-tier signature extensions (team-binding hash-chained; multi-tenant-compliance signature attributes) compose at session 4 Operational Discipline spec |

**Deferred to implementation discretion.** Specific `canonicalize_concat` implementation per language ecosystem (delegated to C-IS-06 §6.1 deferral); specific `last_rotated_at` discovery mechanism per backend (vault metadata API / keyring metadata API / etc.); specific span attribute schema D-ADR per ADR-F5 v1.1 §Consequences (c).

---

## §9 C-AS-09 — 12-cell deployment-surface × blast-radius-tier sandbox provider matrix

**Contract surface.** 2D matrix committing per-cell sandbox tier + provider-class + persona-tier compliance composition.

**PRD requirement(s) satisfied.** R-AS-06 (specific sandbox provider per deployment-surface × blast-radius cell).

**ADR commitment(s) honored.** ADR-D2 v1.2 §1.1 (12-cell matrix verbatim); ADR-D2 v1.2 §1.2 (sandbox provider-class enumeration); ADR-D2 v1.2 §1.10 (workload-binding-time × deployment-surface-time selection contract); ADD §3.3.1 Synthesis.

**Persona linkage.** Persona §5.1 (computer-use at production-time with stronger sandbox tier); §9 (deployment-surface implications — microVM-class isolation required at production-time); §10.1 (graduated-isolation locked); §10.4 (compliance-readiness).

**Specification content.**

### §9.1 12-cell matrix

Per ADR-D2 v1.2 §1.1 verbatim. Cell schema: `sandbox tier (F4) | provider-class (per §9.2) | candidate witnesses`.

| deployment-surface ↓ \ blast-radius-tier → | read-only | local-mutation | external-reversible | external-irreversible |
|---|---|---|---|---|
| **local-development** | `tier-1-process` \| language-level \| in-process / deer-flow LocalSandboxProvider | `tier-2-container` \| process-fs-overlay \| Seatbelt (macOS) / bubblewrap+socat (Linux/WSL) / kilocode-style worktree | `tier-3-microvm` \| container \| Docker-on-OCI; gVisor; OpenHands Docker reference / dify-sandbox / Kode-Agent OpenSandbox | `tier-4-full-vm` \| microVM \| Firecracker (E2B class); E2B self-host; full VM for computer-use cells ephemeral + network-egress-restricted |
| **self-hosted-server** | `tier-1-process` \| language-level \| same as local-development | `tier-2-container` \| process-fs-overlay \| bubblewrap+socat (Linux); container upgrade acceptable | `tier-3-microvm` \| container \| Docker-on-OCI default; Kata Containers; gVisor; humanlayer/agentcontrolplane K8s-resident | `tier-4-full-vm` \| microVM \| Firecracker (E2B self-host); Modal gVisor; deepagents CompositeBackend; Kata as microVM-backed; full VM for computer-use |
| **managed-cloud** | `tier-1-process` \| language-level \| vendor-managed runtime; Lambda / Cloud Run / Cloud Functions class | `tier-2-container` \| vendor-managed process-tier \| Bedrock AgentCore Runtime sandbox primitive; Vertex Agent Engine; Cloudflare Workers Durable Objects | `tier-3-microvm` \| container \| Bedrock AgentCore Runtime (vendor-managed sandbox); Vertex Agent Engine | `tier-4-full-vm` \| microVM / VM \| Bedrock AgentCore Runtime computer-use sandbox primitive; Anthropic Computer Use VMs (vendor-managed full VM ephemeral network-egress-restricted); Vertex Agent Engine equivalent |

### §9.2 Sandbox provider-class enumeration (closed six-class taxonomy)

Per ADR-D2 v1.2 §1.2:

| # | Provider class | Mechanism | Tier mapping | Cardinality |
|---|---|---|---|---|
| 1 | `language-level` | In-process language sandbox (Pyodide / Starlark / ulimit) | `tier-1-process` (read-only); `tier-2-container` only with strict language-level + filesystem-ACL | Open class; new candidates per Workflow §4.1.2 Class-2 ADR-D2 revision |
| 2 | `filesystem-overlay / worktree` | Git-worktree isolation (kilocode pattern); fuse-overlay / fuse-projfs (oh-my-pi pattern) | `tier-2-container` (cross-platform filesystem-bound process-tier composable per ADR-F2) | Open class |
| 3 | `process + ulimit / bubblewrap / Seatbelt` | OS-level process isolation with seccomp / namespacing / sandbox-exec | `tier-2-container` (F4 process-tier tech commitment: Seatbelt macOS; bubblewrap+socat Linux/WSL) | Open class |
| 4 | `container` | Shared-kernel container (Docker / Podman) OR user-space kernel (gVisor) OR microVM-backed container (Kata) | `tier-3-microvm` (F4 container-tier abstraction Docker-on-OCI design-time default; gVisor and Kata as escape-risk-low alternatives) | Open class |
| 5 | `microVM (Firecracker)` | Hardware-virt microVM with KVM | `tier-4-full-vm` (F4 microVM-tier tech committed for code-execution cells) | Open class |
| 6 | `full VM` | Hardware-virt full VM; ephemeral; network-egress-restricted | `tier-4-full-vm` (F4 full-VM-tier tech committed for computer-use cells) | Open class |

Provider-class taxonomy is closed at six classes; new mechanism-class addition is a Workflow §4.1.2 Class-2 ADR-D2 revision.

### §9.3 Forcing-condition cell resolution

Per ADR-D2 v1.2 §1.1:

| Forcing condition | Cell resolution |
|---|---|
| Computer-use model bound | Resolves to `tier-4-full-vm` (ephemeral; network-egress-restricted) at the `external-irreversible` column of any deployment surface, **regardless of nominal blast-radius declaration** |
| `code-execution-2025-08-25` beta invoked | Resolves to `tier-4-full-vm` (microVM minimum) at any cell; `sandbox_tier_floor` enforces |

### §9.4 Operator-policy override scope per persona tier

Per ADR-D2 v1.2 §1.5.2 (full composition at C-AS-12 §12.2):

| Persona tier | Cell-default override scope |
|---|---|
| `solo-developer` | Permitted at non-compliance cells; audit-ledger entry append-only per ADR-D5 v1.3 §1.4 |
| `team-binding` | Permitted only at non-`external-irreversible` cells; audit-ledger entry hash-chained per C-IS-06 |
| `multi-tenant-compliance` | **Structurally prohibited** at any cell per ADR-D5 v1.3 §1.5.2 cross-deployment monotonicity + ADR-D2 v1.2 §1.6 |

### §9.5 Cell selection contract

Per ADR-D2 v1.2 §1.1 + §1.10:

| Stage | Commitment |
|---|---|
| **D2-layer (this spec)** | Per-cell sandbox tier + provider-class committed at the matrix; closed enumeration of six provider classes |
| **Deployment-surface-time** | Operator selects specific candidate within provider-class per cell at deployment-binding time |
| **Workload-binding-time** | Workload manifest declares per-workload sandbox-tier overrides (subject to monotonicity per C-AS-11) and per-workload provider-instance preferences |

**Deferred to implementation discretion.** Specific candidate-within-provider-class selection per cell at deployment binding (e.g., Firecracker vs Kata at managed-cloud × external-irreversible — operator-tunable per §9.5 stage); specific cell-defaults storage and lookup mechanism; specific deployment-surface capability detection at deployment-binding time.

---

## §10 C-AS-10 — Per-MCP-transport sandbox-tier floor

**Contract surface.** Per-transport × per-trust-level lookup table with REFUSE sentinel.

**PRD requirement(s) satisfied.** R-AS-06 (specific sandbox provider per cell — MCP-transport floor enforcement half).

**ADR commitment(s) honored.** ADR-D2 v1.2 §1.3 (per-MCP-transport sandbox-tier floor table); ADD §3.3.1 Synthesis; substrate at Cluster 4 §2.3.3 [HIGH] MCP authorization spec 2025-06-18 STDIO-transport directive.

**Persona linkage.** Persona §5.1 (MCP first-class); §10.1 (graduated-isolation); §10.4 (compliance-readiness).

**Specification content.**

### §10.1 Per-MCP-transport floor lookup table

Per ADR-D2 v1.2 §1.3 verbatim:

| MCP transport | MCP trust level (per Cluster 4 §2.3.3 [HIGH]) | `sandbox_tier_floor` | Rationale |
|---|---|---|---|
| **STDIO** | zero protocol-level auth (per MCP authorization spec 2025-06-18 [HIGH] — STDIO transports excluded from OAuth 2.1 + RFC 8707 + RFC 9728 + PKCE; "retrieve credentials from environment") | **`tier-3-microvm` minimum** regardless of declared blast-radius | Sandbox is the only boundary; container-tier minimum prevents kernel-CVE-class escape into host filesystem; gVisor or Kata acceptable at trusted-workload subset under operator-policy override per C-AS-12 §12.2 |
| **Streamable HTTP+SSE, Level 0** (refuse-remote) | not trusted | `REFUSE` (sentinel) | Tier-irrelevant; harness rejects connection at MCP server registration |
| **Streamable HTTP+SSE, Level 1** (signed-pinned) | signed; pinned at registration | per `blast_radius_floor` | OAuth 2.1 + signature verification provides protocol-level boundary; sandbox-tier follows blast-radius |
| **Streamable HTTP+SSE, Level 2** (sandbox-all) | sandbox-mediated | **`tier-4-full-vm` minimum** with allow-listed upstream domains | F4-layer enabler of lethal-trifecta architectural cut per Cluster 4 §2.3.2 [HIGH]; egress allow-listing prevents exfil to attacker-controlled destinations |
| **Streamable HTTP+SSE, Level 3** (allow-with-audit) | trusted; auditable | per `blast_radius_floor` with audit-ledger entry | Trust boundary established at OAuth + audit; sandbox-tier follows blast-radius; audit-ledger entry per persona-tier cryptographic shape per ADR-D5 v1.3 §1.4 |

### §10.2 Composition with C-AS-02

| Property | Contract |
|---|---|
| **Floor input to `sandbox_tier_floor()`** | The per-MCP-transport floor feeds the `mcp_transport` argument of `sandbox_tier_floor(tool, deployment_surface, blast_radius_tier, mcp_transport, mcp_server)` at C-AS-02 §2.3 (the 5-arg canonical signature; the remote-MCP trust level keying §2.3 rows 4–6 is read from the separate `mcp_server` argument) |
| **REFUSE sentinel propagation** | When `sandbox_tier_floor` returns the `REFUSE` sentinel, the harness rejects the MCP server connection at the registration boundary; no `sandbox_tier` value is resolved; the action does not occur |
| **`max()` precedence** | Per the C-AS-02 `max()` composition, the per-MCP-transport floor wins whenever it exceeds the other floors (blast-radius floor, operator-policy floor, per-tool minimum_tier) |

### §10.3 MCP server trust-tier framework

Per Cluster 4 §2.3.3 [HIGH] four-level MCP server trust posture (and ADR-D5 v1.3 §1.5 five-tier framework cross-axis composition for the per-MCP-server-trust-tier_floor at Control Plane session 3):

```
Level 0 — refuse-remote        (REFUSE at registration)
Level 1 — signed-pinned        (signature + version pin at registration)
Level 2 — sandbox-all          (tier-4-full-vm with egress allow-list)
Level 3 — allow-with-audit     (audit-ledger entry per fetch / call)
```

The per-MCP-server-trust-tier_floor enters the gate-level `max()` composition at C-AS-12 §12.1 (the 5-axis multiplicative tunable). The MCP server trust level is operator-declared at MCP server registration; trust-level assignment is recorded in the audit ledger per C-AS-08 composition.

**Deferred to implementation discretion.** Specific MCP server registration mechanism (manifest declaration vs runtime discovery); specific signature verification implementation at Level 1 (PKI registry / signed-pinned certificates / etc.); specific egress allow-list authoring schema at Level 2; specific per-call audit cadence at Level 3.

---

## §11 C-AS-11 — Sub-agent sandbox-tier monotonic-ascension contract

**Contract surface.** Sub-agent tier-resolution signature + unconditional ascension rule + override-clause non-extension.

**PRD requirement(s) satisfied.** R-AS-01 (sandbox tier at run-event surface — sub-agent boundary half); R-AS-06 (specific sandbox provider — cross-axis composition with Control Plane sub-agent boundary).

**ADR commitment(s) honored.** ADR-D2 v1.2 §1.4 (sub-agent sandbox-tier monotonic-ascension as unconditional containment rule); ADD §5.3.2 sub-agent boundary as monotonic-only descent; ADD §5.2.1 T-perm-1 sub-agent-boundary preservation.

**Cross-axis citation.** Sub-agent privilege inheritance contract at ADR-D4 v1.1 §1.5 (the D4-layer surface composes against this contract; full Control Plane composition at session 3 spec); cross-deployment monotonicity of gate-level at ADR-D5 v1.3 §1.5.2 (composed at session 3 spec).

**Persona linkage.** Persona §4 (99.9% SLO; sub-agent fan-out as primary parallelism); §10.1 (graduated-isolation locked); §10.4 (compliance-readiness — containment unconditional).

**Specification content.**

### §11.1 Sub-agent tier-resolution signature

```
sub_agent_sandbox_tier(
    parent_sandbox_tier: SandboxTier,
    tool: Tool,
    blast_radius: BlastRadiusTier,
    mcp_transport: MCPTransport,
    deployment_surface: DeploymentSurface,
    mcp_server: MCPServer
) -> SandboxTier
    =
    max(
        parent_sandbox_tier,                                            # monotonic ascending
        sandbox_tier_floor(tool, deployment_surface, blast_radius,
                           mcp_transport, mcp_server)
    )
```

per ADR-D2 v1.2 §1.4.

### §11.2 Unconditional ascension rule

| Property | Contract |
|---|---|
| **Sub-agent tier ≥ parent tier** | A sub-agent's resolved sandbox tier is always greater than or equal to its parent's resolved sandbox tier |
| **Tier downgrade structurally prohibited** | A sub-agent cannot run at a weaker isolation tier than its parent under any condition; tier downgrade at the sub-agent boundary is a contract violation |
| **D4 override-clause does NOT extend to sandbox tier** | Per ADD §5.3.2 + ADR-D2 v1.2 §1.4: ADR-D4 v1.5 sub-agent privilege override-clause (where parent declares child agents own external-reversible authority) is registry-scoped only; **sandbox monotonicity is unconditional even when registry inheritance is overridden** |

### §11.3 Rationale anchor

Per ADR-D2 v1.2 §1.4:

```
Sub-agent registry-downgrade per D4 §1.5     ⟶ REMOVES capability  (sub-agent
                                                                    cannot invoke
                                                                    a tool)
Sub-agent sandbox-monotonicity per D2 §1.4   ⟶ CONSTRAINS           (sub-agent
                                              CONTAINMENT            runs at
                                                                    no-weaker
                                                                    isolation)
```

Principle-of-least-containment is the **wrong principle** at the sub-agent boundary; child-agent containment must always meet or exceed parent's.

### §11.4 Composition with cross-deployment monotonicity

Per ADR-D2 v1.2 §1.6 + ADR-D5 v1.3 §1.5.2:

| Property | Contract |
|---|---|
| **Bridging-arc traversal** | Under persona-tier traversal (solo-developer → team-binding → multi-tenant-compliance), `sandbox_tier_floor` is monotonic ascending per ADR-D2 v1.2 §1.6 |
| **In-flight effective tier raise** | Tier upgrade at bridging-arc traversal raises the effective sandbox tier for in-flight workflows immediately |
| **Tier downgrade requires Class-2 D2 revision** | Cell-level tier downgrade requires explicit Workflow §4.1.2 Class-2 ADR-D2 revision; not operator-tunable at runtime |
| **Composition with §11.2** | Sub-agent monotonicity (this contract) plus cross-deployment monotonicity (ADR-D2 v1.2 §1.6) jointly produce sub-agent tier ≥ parent tier ≥ persona-tier floor; all three axes ascend monotonically |

### §11.5 Sub-agent boundary verification

| Verification surface | Contract |
|---|---|
| Run-event surface (production-time operator) | Sub-agent `sandbox.enter` event carries `sandbox.tier` ≥ parent `sandbox.tier` per C-AS-15; verifiable at trace inspection |
| Audit-ledger surface (downstream maintainer) | Sub-agent sandbox-tier transitions emit `sandbox.tier_escalation` events per C-AS-15 with `sandbox.policy.assigned_tier_reason = sub_agent_monotonic_ascension` |
| Tamper-evidence | Sub-agent boundary violations (downgrade attempt) are deterministic policy hits; emit `sandbox.fail.class = policy_override` per C-AS-04 with audit-ledger entry per C-AS-08 |

**Deferred to implementation discretion.** Specific sub-agent dispatch mechanism per topology pattern (orchestrator-workers / decentralized-handoff / hierarchical-delegation — D4-layer Control Plane spec at session 3); specific parent-child tier-resolution call-site instrumentation; specific sandbox-pool warm-up policy per fan-out cap (composed against ADR-D2 v1.2 §1.9 — session 3 cross-axis territory).

---

## §12 C-AS-12 — T-perm-1 D2-layer 5-axis multiplicative tunable

**Contract surface.** 5-axis gate-level composition function + cross-deployment monotonicity contract + operator-policy override scope per persona-tier.

**PRD requirement(s) satisfied.** R-AS-01 (sandbox tier visible — gate-level composition surface); R-AS-06 (specific sandbox provider per cell — D2-layer tunable surface).

**ADR commitment(s) honored.** ADR-D2 v1.2 §1.5 (T-perm-1 D2-layer multiplicative tunable parameter specialization); ADR-D2 v1.2 §1.5.1 (composition rule); ADR-D2 v1.2 §1.5.2 (composition with operator-policy override); ADR-D2 v1.2 §1.6 (cross-deployment sandbox-tier monotonicity); ADD §5.2.1 T-perm-1 multi-layer resolution.

**Persona linkage.** Persona §4 (99.9% SLO — multiplicative composition as deterministic outer harness); §10.1 (graduated-isolation locked); §10.4 (compliance-readiness — multi-tenant override prohibition).

**Specification content.**

### §12.1 5-axis multiplicative tunable parameter

Per ADR-D2 v1.2 §1.5, the locked tunable parameter is:

```
per_tool_gate_level × per_mcp_server_trust_tier × persona_tier × blast_radius_tier × sandbox_tier
```

This is the **D2-layer specialization** of ADR-D5 v1.3 §1.5's 4-axis locked tunable, adding `sandbox_tier` as the fifth axis. The composition rule extends ADR-D5 v1.3 §1.5.1:

```
gate_level(tool, mcp_server, persona_tier, deployment_surface,
           blast_radius_tier, mcp_transport) =
    max(
        per_tool_gate_level,                                    # C4 contract: {auto, ask, deny}
        blast_radius_floor(tool),                                # C10 four-tier taxonomy
        per_mcp_server_trust_floor(mcp_server),                 # C10 five-tier framework
        persona_tier_floor,                                      # D5 §1.5
        sandbox_tier_floor(tool, deployment_surface,             # D2 NEW
                          blast_radius_tier, mcp_transport,
                          mcp_server)
    )
```

### §12.2 Composition with operator-policy override per persona-tier

Per ADR-D2 v1.2 §1.5.2 (full table at C-AS-09 §9.4):

| Persona-tier | Operator-policy override of `sandbox_tier_floor` |
|---|---|
| `solo-developer` | Permitted at non-compliance cells (e.g., `tier-4-full-vm` → gVisor at managed-cloud; `tier-3-microvm` → process at short-session × cache-friendly cells); audit-ledger entry append-only per ADR-D5 v1.3 §1.4 |
| `team-binding` | Permitted only at non-`external-irreversible` cells; audit-ledger entry hash-chained with `prior_event_hash` per C-IS-06 |
| `multi-tenant-compliance` | **Structurally prohibited** per ADR-D5 v1.3 §1.5.2 + ADR-D2 v1.2 §1.6; operator-policy override at multi-tenant-compliance produces an **audit-ledger violation event**, not a tier change |

### §12.3 Override-event audit composition

| Property | Contract |
|---|---|
| **Audit-ledger entry per override** | Every operator-policy override emits one audit-ledger entry per C-AS-08; `sandbox.fail.class = policy_override` per C-AS-04 |
| **Violation-event emission at multi-tenant-compliance** | At multi-tenant-compliance, operator-policy override emits an audit-ledger entry with violation semantic (override-attempted-but-prohibited); tier does NOT change |
| **Span emission** | Override events emit `sandbox.violation` spans with `sandbox.fail.class = policy_override` per C-AS-15; always-sampled (head=1.0) |

### §12.4 Cross-deployment monotonicity contract

Per ADR-D2 v1.2 §1.6:

| Property | Contract |
|---|---|
| **Ascending under bridging-arc traversal** | When persona tier ascends (solo-developer → team-binding → multi-tenant-compliance), `sandbox_tier_floor` is monotonic ascending; a tool running at `tier-2-container` at solo-developer × local-mutation **must ascend** to the team-binding × local-mutation cell's floor if higher |
| **No tier-equivalence-below-floor** | Tier-equivalence at lower-than-floor is structurally prohibited; the tool cannot remain at a tier below the destination cell's floor |
| **In-flight effective raise** | Tier upgrade is permitted at any time and raises the effective sandbox tier for in-flight workflows immediately |
| **Tier downgrade as Class-2 D2 revision** | Tier downgrade requires explicit Workflow §4.1.2 Class-2 ADR-D2 revision |

### §12.5 Multiplicative discipline preservation

Per ADD §5.2.1: the composition is **multiplicative `max()`** — both axes (C4 capability via `per_tool_gate_level` and contract-attached `minimum_tier`; C10 gating via `blast_radius_floor`, `per_mcp_server_trust_floor`, `persona_tier_floor`, `sandbox_tier_floor`) express their concern; the higher tier always wins by construction; neither voice is suppressed. T-perm-1 closure is **structural composition**, not a choice between C4 and C10.

**Deferred to implementation discretion.** Specific runtime evaluation engine for the 5-axis `max()` (per-call vs cached); specific `persona_tier_floor` lookup table per ADR-D5 v1.3 §1.5 (Control Plane spec session 3 territory); specific operator-policy override authoring schema (manifest field / API call / TUI action).

---

## §13 C-AS-13 — Eleven-primitive Anthropic-adoption-depth matrix

**Contract surface.** Closed eleven-primitive enumeration + 2D adoption-depth matrix + per-engine-class composition overlay + workload-binding-time selection contract.

**PRD requirement(s) satisfied.** R-AS-07 (Anthropic-primitive adoption depth per workload-class cell at deployment-binding time).

**ADR commitment(s) honored.** ADR-D3 v1.2 §1.1 (eleven-primitive enumeration); ADR-D3 v1.2 §1.2 (per-primitive × workload-class adoption-depth matrix); ADR-D3 v1.2 §1.3 (per-engine-class composition site overlay); ADR-D3 v1.2 §1.4 (per-sub-agent-role × model-binding contract); ADR-D3 v1.2 §1.5 (prompt-cache breakpoint placement); ADR-D3 v1.2 §1.6 (structured-outputs adoption-depth); ADR-D3 v1.2 §1.7 (Anthropic-API graceful-degradation); ADR-D3 v1.2 §1.9 (workload-binding-time selection contract); ADD §3.3.2 Synthesis.

**Persona linkage.** Persona §5 (integration surface); §6 (per-workload-class cost ceiling); §7 (pragmatic-mixed ecosystem affinity — Anthropic primitives where they fit).

**Specification content.**

### §13.1 Closed eleven-primitive enumeration

Per ADR-D3 v1.2 §1.1; enumeration closed at eleven; new primitive addition is a Workflow §4.1.2 Class-2 ADR-D3 revision:

| # | Primitive | Anchor citation |
|---|---|---|
| 1 | **Skills system** (SKILL.md frontmatter; three-level progressive disclosure; agentskills.io open standard ratified 18 Dec 2025) | platform.claude.com/docs/en/agents-and-tools/agent-skills/overview [HIGH] |
| 2 | **MCP-as-code** (code-execution-with-MCP per Anthropic Nov 4 2025; `tool_search` lazy-loading; per-server trust tier) | modelcontextprotocol.io/specification/2025-06-18 [HIGH]; anthropic.com/engineering/code-execution-with-mcp [HIGH] |
| 3 | **Managed Agents** (`managed-agents-2026-04-01` beta; Anthropic-Platform-only path) | platform.claude.com/docs/en/managed-agents/overview [HIGH] |
| 4 | **Per-role model binding** (Haiku 4.5 / Sonnet 4.6 / Opus 4.6 / Opus 4.7 per role per cell) | Cluster 1 §[HIGH] Anthropic research system; Cluster 5 V2 §[HIGH] Q2 2026 rate card |
| 5 | **Prompt-caching + breakpoint placement** (4 explicit breakpoints; static-prefix / dynamic-suffix; concurrent warm-up) | Cluster 2 V2 §1.1 [HIGH]; platform.claude.com/docs/en/build-with-claude/prompt-caching |
| 6 | **Extended-thinking budget** (adaptive only on Opus 4.7; manual budget deprecated on Opus / Sonnet 4.6) | Cluster 5 V2 §[HIGH]; platform.claude.com/docs/en/build-with-claude/extended-thinking |
| 7 | **Batch API** (50% discount; 100K requests; 24h SLA; stacks with prompt caching) | Cluster 5 V2 §[HIGH]; platform.claude.com/docs/en/build-with-claude/batch-processing |
| 8 | **Claude Code hooks** (PreToolUse / PostToolUse / PreSubagent lifecycle hooks; portability-bracketed) | disler/body-of-work hooks-mastery; mindfold-ai/Trellis bracketed-hooks witness |
| 9 | **claude.md / agents.md convention** (filesystem-resident system-prompt-extension; cache-prefix integrity required) | Anthropic Claude Code convention |
| 10 | **Files API** (`files-api-2025-04-14` beta; `/v1/files` upload/list/metadata/delete; workspace-scoped; `file_id` reference in message content; composes with code execution and Batch API 50% discount) | platform.claude.com/docs/en/build-with-claude/files [HIGH] |
| 11 | **Memory tool** (`memory_20250818`; beta header `context-management-2025-06-27`; **client-side**: harness implements storage backend; filesystem-style interface in `/memories` Claude controls; distinct from Managed Agents server-side memory) | docs.claude.com/en/docs/agents-and-tools/tool-use/memory-tool [HIGH] |

### §13.2 Per-primitive × workload-class adoption-depth matrix

Per ADR-D3 v1.2 §1.2. Adoption-depth values: **R** = required, **r** = recommended, **o** = optional, **X** = excluded. Cell selection is at deployment-binding time per §13.6.

| Primitive ↓ \ Workload class → | software-engineering | content-creation | pipeline-automation | research |
|---|---|---|---|---|
| 1. Skills system | r | r | R | r |
| 2. MCP-as-code | r | o | R | r |
| 3. Managed Agents | o at managed-cloud / hybrid; **X** at local-development | o at managed-cloud / hybrid; **X** at local-development | r at managed-cloud; o at hybrid; **X** at local-development | r at managed-cloud; o at hybrid; **X** at local-development |
| 4. Per-role model binding | R | R | R | R |
| 5. Prompt-cache breakpoint placement | R | r | R | R |
| 6. Extended-thinking budget | r (xhigh recommended) | o (low if adopted) | o (low to medium) | r (high at orchestrator; low at Haiku siblings) |
| 7. Batch API | o | o | r | r |
| 8. Claude Code hooks | r | o | r | o |
| 9. claude.md / agents.md convention | r | r | r | r |
| 10. Files API | r at managed-cloud / hybrid; o at local-development | r at managed-cloud / hybrid; o at local-development | R at managed-cloud / hybrid; o at local-development | R at managed-cloud / hybrid; o at local-development |
| 11. Memory tool | per-workload selection; structurally available all surfaces (storage backend per §13.6) | per-workload selection | per-workload selection | per-workload selection |

### §13.3 Per-engine-class composition site overlay

Per ADR-D3 v1.2 §1.3:

| D1 engine class | Prompt-cache scope | Batch API integration | Extended-thinking placement | Skills filesystem residence |
|---|---|---|---|---|
| `event-sourced-replay` (Temporal-class) | Activity-internal | Submission as Activity; engine-native idempotency | Activity-internal | Activity reads SKILL.md from project-root filesystem at call time |
| `save-point-checkpoint` (LangGraph-class) | Node-internal | Submission at node boundary; `interrupt()` + Command resume | Node-internal | Node reads SKILL.md; checkpoint state includes loaded-Skill manifest for replay determinism |
| `pure-pattern-no-engine` (12-Factor) | Harness-managed | Submission idempotency-keyed via F2 state-ledger entry per C-IS-05 | Harness-managed | Harness reads SKILL.md from F2 filesystem |
| `reconciler-loop` (K8s CRD) | CR-cycle-scoped | Submission represented as CR; idempotency on CR `metadata.uid` | CR-cycle-scoped | SKILL.md mounted as ConfigMap / PVC |
| `WAL-segment` (Kode-Agent reference) | Per-segment | Submission as WAL entry; per-segment fail-fast | Per-segment | SKILL.md per-segment metadata |

Idempotency-key construction per Cluster 4 §2.2.7 [HIGH] composes against C-IS-05 `idempotency_key`: `sha256(conversation_id || step_index || tool || canonical_args)` plus `batch_id` (Batch API) plus `skill_name + skill_version_sha` (Skills) plus `file_id_set` (Files API) plus memory-op metadata (Memory tool — engine-class-conditional storage per ADR-D3 v1.2 §1.3).

### §13.4 Per-sub-agent-role × model-binding contract

Per ADR-D3 v1.2 §1.4:

| Workload class | Lead / orchestrator | Generator | Evaluator | Reviewer | Sub-agent |
|---|---|---|---|---|---|
| software-engineering | Sonnet 4.6 default; Opus 4.6 at multi-tenant-compliance | Sonnet 4.6 | Sonnet 4.6 (×1–3) | Haiku 4.5 (cap 3) | Haiku 4.5 (review/eval reads) |
| content-creation | Sonnet 4.6 | Sonnet 4.6 | Haiku 4.5 (operator-as-reviewer dominant) | n/a | n/a |
| pipeline-automation | Sonnet 4.6 per-stage default; Haiku 4.5 high-volume idempotent | Sonnet 4.6 synthesis; Haiku 4.5 idempotent | n/a (deterministic gates) | n/a | Haiku 4.5 (idempotent parallel; cap 3) |
| research | Sonnet 4.6 default; Opus 4.6 multi-tenant-compliance high-fidelity | n/a | n/a | Haiku 4.5 (synthesis pre-pass) | Haiku 4.5 (breadth-search × 3–5) |

Lead-agent brief-authoring binding inherits the lead/orchestrator binding (per ADR-D3 v1.2 §1.4 brief-authoring NOT reducible to Haiku). Pre-HITL escalation order: 1st validator fail → C9 backoff; 2nd fail → C6 model-tier escalation (Haiku → Sonnet → Opus 4.6 → Opus 4.7); 3rd fail → C11 HITL per ADR-D5 v1.3 §1.10 (cross-axis to Control Plane spec at session 3).

### §13.5 Anthropic-API graceful-degradation per primitive

Per ADR-D3 v1.2 §1.7. Under Anthropic-API outage (C9 breaker key `(provider=anthropic, model)`):

| Primitive | Outage behavior |
|---|---|
| Skills system | Continues; SKILL.md filesystem residence is provider-independent |
| MCP-as-code | Continues; MCP servers are provider-independent |
| Managed Agents | **Falls through to harness-owned topology**; D4 §1.2 patterns at the cell's workload-class row |
| Per-role model binding | **C6 cross-family fallback** per F1; chain `(anthropic, model) → (bedrock, claude-equivalent) → (vertex, claude-equivalent) → (openai, gpt-class) → (local, ollama)` |
| Prompt-caching | Cache state lost on cross-family fallback; warm-up cycle restarts |
| Extended-thinking budget | Anthropic-only; cross-family runs without extended thinking |
| Batch API | Anthropic-only; in-flight resume on Anthropic recovery |
| Claude Code hooks | Claude-Code-specific; harness-owned hook lifecycle if implemented independently |
| claude.md / agents.md | Continues; static-prefix content provider-independent |
| Files API | Anthropic-API-bound; cross-family loses `file_id` references; harness MAY pre-cache locally |
| Memory tool | Cross-family-compatible via client-side storage; underlying memory data survives fallback; integration layer harness-implementation-conditional |

### §13.6 Workload-binding-time selection contract

Per ADR-D3 v1.2 §1.9; per-primitive structural adoption depth committed at this spec; specific Anthropic-primitive content deferred to workload-binding-time:

```
At workload-binding-time:

1. Operator declares workload class, persona tier, deployment surface
2. C-AS-13 §13.2 cell selects per-primitive adoption depth
3. C-AS-13 §13.3 selects per-engine-class composition site per D1 row
4. C-AS-13 §13.4 selects per-sub-agent-role model binding per D4 §1.2 row
5. Operator authors specific Anthropic-primitive content:
   a. Per-Skill SKILL.md authoring per C4 + C2 + C10 jointly-owned contract
      (`name`, `description`, `allowed-tools`, `tier ∈ {auto, ask, deny}`)
   b. Per-MCP-server adoption per C-AS-10 trust-tier framework
   c. Per-Managed-Agent declaration (if cell adoption-depth admits) per C4 + C1
   d. claude.md / agents.md authoring per C2 + C11 jointly-owned operator-surface
6. Operator selects extended-thinking effort per cell of §13.2 row 6
7. Operator binds Batch API submission cells per cell of §13.2 row 7
8. Operator selects Memory tool storage backend per cell (filesystem / s3 /
   database / encrypted-filesystem / operator-defined)
```

**Deferred to implementation discretion.** Specific Memory tool storage backend per deployment surface (filesystem at local-development with F2 worktree-isolation; cloud-vault or managed-database at managed-cloud; composable at hybrid); specific per-MCP-server-registration mechanism; specific Skill authoring schemata beyond SKILL.md frontmatter; specific Managed Agent session lifecycle binding; specific Batch API job-ID storage per engine class; specific `tools[]` array warm-up cycle at restart per Cluster 2 V2 §[HIGH].

---

## §14 C-AS-14 — Six Anthropic-primitive attribute namespace declarations

**Contract surface.** Six attribute namespaces + per-namespace attribute enumeration + per-namespace sampling discipline + audit-floor commitments.

**PRD requirement(s) satisfied.** R-AS-07 (Anthropic-primitive adoption depth — observability emission half).

**ADR commitment(s) honored.** ADR-D3 v1.2 §1.8 (per-Anthropic-primitive span attribute schema); ADR-D3 v1.2 §1.8.1 (canonical attribute namespace declarations); ADR-D3 v1.2 §1.8 forward-reference clause (D6 §1.3 sampling-discipline alignment per F2-09 closure); ADD §3.3.2 Synthesis.

**Persona linkage.** Persona §10.2 (cost-attribution-per-span); §10.4 (compliance-readiness — tamper-evidence at primitive invocations).

**Specification content.**

### §14.1 Six namespace declarations

**Alias-term convention (v1.7 NEW per `.harness/class_1_fork_genai_span_name_four_way_drift.md` §7.4.3 R3 option (b)).** **The LLM inference span** is the conceptual reference used at this specification for the span opened by the runtime LLM dispatcher composer per OD spec v1.12 §C-OD-04 §4.1 (actual emitted span name = `{gen_ai.operation.name} {gen_ai.request.model}` 2-token byte-exact to OTel GenAI semantic conventions 1.41.0 archived text). Cited at AS spec rows + downstream namespace schemas as "the LLM inference span" — the literal span-name format is OD-axis-owned at §4.1. This decoupling means AS spec parent-anchor citations are immune to future OTel semconv version bumps; only OD §4.1 + production rename ripple.

| Namespace | Attribute count | Parent span | Per ADR-D3 v1.2 §1.8.1 declaration site |
|---|---|---|---|
| `anthropic.*` | 10 | the LLM inference span | ADR-D3 v1.2 §1.8.1 anthropic namespace block |
| `mcp.*` | 7 | `mcp.tool.call` | ADR-D3 v1.2 §1.8.1 mcp namespace block (F2-02 alignment with D6) |
| `skill.*` | 6 | `skill.activation` | ADR-D3 v1.2 §1.8.1 skill namespace block (F2-03 joint set preserving semantic distinction) |
| `managed_agents.*` | 3 | `managed_agents.runtime` | ADR-D3 v1.2 §1.8.1 managed_agents namespace block (F2-04 namespace consolidated) |
| `files.*` | 8 | `files.operation` | ADR-D3 v1.2 §1.8.1 files namespace block (v1.1 — F2-11 Reading 2 closure) |
| `memory.*` | 6 | `memory.operation` | ADR-D3 v1.2 §1.8.1 memory namespace block (v1.1 — F2-11 Reading 2 closure) |

### §14.2 `anthropic.*` namespace (ten attributes on the LLM inference span)

| Attribute | Type | Semantic | Cardinality |
|---|---|---|---|
| `anthropic.cache_creation_input_tokens` | int | Cache write count | unbounded (metric) |
| `anthropic.cache_read_input_tokens` | int | Cache read count (0.10× cost) | unbounded (metric) |
| `anthropic.cache_breakpoint_id` | string | Which of ≤4 breakpoints hit | low (≤4) |
| `anthropic.cache_ttl_seconds` | int | 300 (5min) or 3600 (1hr) | binary |
| `anthropic.thinking_mode` | enum string | `adaptive` / `enabled` / `disabled` | bounded (3) |
| `anthropic.thinking_budget_tokens` | int | Adaptive: actual; enabled: budget | unbounded (metric) |
| `anthropic.thinking_effort` | enum string | `low` / `medium` / `high` / `xhigh` / `max` | bounded (5) |
| `anthropic.batch_id` | string (optional) | Batch API submission marker | unbounded |
| `anthropic.tokenizer_version` | string | `v1` (default); `v2` (Opus 4.7) | low |
| `anthropic.inference_geo` | enum string (optional) | `us` if data-residency premium | low |

### §14.3 `mcp.*` namespace (seven attributes on `mcp.tool.call` span)

| Attribute | Type | Semantic | Cardinality |
|---|---|---|---|
| `mcp.server.name` | string | Per-deployment server registry identifier | medium |
| `mcp.server.trust_tier` | enum string | Four-tier per Cluster 4 §2.3.3 | bounded (4) |
| `mcp.protocol_version` | string | `2025-06-18` | low |
| `mcp.transport` | enum string | `stdio` / `streamable_http` | binary |
| `mcp.auth_present` | bool | Always false on STDIO | binary |
| `mcp.primitive.kind` | enum string | `tool` / `resource` / `prompt` / `sampling` per modelcontextprotocol.io spec | bounded (4) |
| `mcp.primitive.signature.sha256` | string (hex) | Per-primitive content-addressable hash (tool-poisoning detection per Cluster 4 §2.3.3 [HIGH]) | per-primitive |

### §14.4 `skill.*` namespace (six attributes on `skill.activation` span)

| Attribute | Type | Semantic | Cardinality |
|---|---|---|---|
| `skill.id` | string | Canonical Skill identifier | medium |
| `skill.name` | string | SKILL.md frontmatter `name` | medium |
| `skill.version_sha` | string (hex) | Git content hash (replay-determinism anchor) | per-Skill-version |
| `skill.frontmatter.version` | string | SKILL.md frontmatter `version` field (migration-tracking) | per-Skill-version |
| `skill.body_tokens` | int | Cost attribution (Skills coverage holdout per C8) | unbounded (metric) |
| `skill.activation_mode` | enum string | `frontmatter_only` / `tool_search` / `filesystem_read` | bounded (3) |

**Semantic distinction (load-bearing per ADR-D3 v1.2 §1.8.1).** `skill.version_sha` is the git content hash (changes on any byte change including comments and whitespace) — replay-determinism anchor. `skill.frontmatter.version` is the operator-declared semantic version — migration-tracking surface. **Both required**: replay determinism uses `version_sha`; cache-prefix integrity uses both jointly.

### §14.5 `managed_agents.*` namespace (three attributes on `managed_agents.runtime` span)

| Attribute | Type | Semantic | Cardinality |
|---|---|---|---|
| `managed_agents.runtime_ms` | int | Runtime in milliseconds | unbounded (metric) |
| `managed_agents.session_id` | string | Per-session identifier | high (per-session) |
| `managed_agents.billable_seconds` | float | × $0.08/3600 = cost | unbounded (metric) |

### §14.6 `files.*` namespace (eight attributes on `files.operation` span)

| Attribute | Type | Semantic | Cardinality |
|---|---|---|---|
| `files.operation.kind` | enum string | `upload` / `list` / `metadata` / `delete` / `reference` | bounded (5) |
| `files.file_id` | string | Workspace-scoped file identifier per Files API beta header | per-artifact |
| `files.filename` | string | Original filename (structure-not-content; sensitive-data discipline applies) | per-artifact |
| `files.mime_type` | string | MIME type discriminator | medium |
| `files.size_bytes` | int | Uploaded size for cost attribution | unbounded (metric) |
| `files.workspace_id` | string | Workspace scope (Files API is workspace-scoped per platform.claude.com [HIGH]) | per-workspace |
| `files.batch_composition` | bool (optional) | True if file referenced in a Batch API submission (50% discount stacking marker) | binary |
| `files.code_execution_composition` | bool (optional) | True if file passed to code execution tool via `file_ids` parameter | binary |

### §14.7 `memory.*` namespace (six attributes on `memory.operation` span)

| Attribute | Type | Semantic | Cardinality |
|---|---|---|---|
| `memory.operation.kind` | enum string | `read` / `write` / `update` / `delete` / `list` | bounded (5) |
| `memory.path` | string | Path within `/memories` (structure-not-content discipline) | per-memory-file |
| `memory.backend` | enum string | `filesystem` / `s3` / `database` / `encrypted_filesystem` / `operator_defined` (deployment-binding-time per C-AS-13 §13.6) | bounded (5) |
| `memory.bytes_read` | int (optional) | Read operations; cost attribution | unbounded (metric) |
| `memory.bytes_written` | int (optional) | Write operations; cost attribution | unbounded (metric) |
| `memory.context_editing_active` | bool | True if parent (the LLM inference span) uses `clear_tool_uses_20250919` with `exclude_tools: ["memory"]` per docs.claude.com [HIGH] | binary |

### §14.8 Sampling discipline + audit-floor commitments

Per ADR-D3 v1.2 §1.8 sampling table:

| Span | Sampling rate | Rationale |
|---|---|---|
| the LLM inference span | head-based-dev / tail-based-prod | Volume-bounded; tail-keep-on-classification for failures |
| `skill.activation` | head=1.0 design-time; base-rate at production | Skills coverage holdout per C8 |
| `mcp.tool.call` | **head=1.0 with tail-keep-on-trust-tier-floor-violations** | C10 audit requirement (audit-floor commitment) |
| `managed_agents.runtime` | head=1.0 always | Cost attribution ($0.08/hr non-trivial) |
| `files.operation` | head=1.0 at `kind ∈ {upload, delete}`; base-rate at `kind ∈ {list, metadata, reference}` | Audit on workspace-scoped artifact mutation |
| `memory.operation` | head=1.0 at `kind ∈ {write, update, delete}`; base-rate at `kind ∈ {read, list}` | Audit on memory mutations |

**Audit-floor commitments** (NOT operator-tunable at base-rate; deployment-binding-time hardcoded floors per ADR-D3 v1.2 §1.8.1):

```
mcp.tool.call             head=1.0 with tail-keep-on-trust-tier-floor-violations
files.operation (mutation) head=1.0
memory.operation (mutation) head=1.0
managed_agents.runtime    head=1.0
skill.activation          head=1.0 design-time; base-rate at production
```

### §14.9 Forward-reference to D6 sampling-discipline alignment

Per ADR-D3 v1.2 §1.8 F2-09 forward-reference: D6 §1.3 sampling discipline MUST distinguish `mcp.tool.call` (always-sampled per this audit-floor commitment) from non-MCP `tool.call` (base-rate sampled). Any D6 disposition that does NOT preserve `mcp.tool.call` always-sampled posture violates this commitment.

**Cross-axis citation.** Full D6 sampling-discipline composition at Operational Discipline spec (session 4).

**Deferred to implementation discretion.** Specific OTel/OTLP exporter implementation per cell (composes at session 4 Operational Discipline spec); specific sensitive-data redaction implementation at `files.filename` / `memory.path` (delegated to D6 §1.4 redaction discipline at session 4); specific metric-dimension cardinality enforcement at `skill.body_tokens` / `files.size_bytes` / `memory.bytes_*` (delegated to `c7-observability` SKILL.md cardinality-safe discipline at implementation).

---

## §15 C-AS-15 — Sandbox-bounded span schema (`sandbox.*` namespace)

**Contract surface.** Span hierarchy + seven `sandbox.*` attribute names with `sandbox.tech` ↔ `sandbox.provider` join contract + sampling discipline + capability-floor (iv) traceability.

**PRD requirement(s) satisfied.** R-AS-01 (sandbox tier at run-event surface — span emission half); R-AS-02 (sandbox failure-class taxonomy — span emission half); R-AS-06 (specific sandbox provider per cell — span emission half).

**ADR commitment(s) honored.** ADR-D2 v1.2 §1.7 (sandbox-boundary span schema); ADR-D2 v1.2 §1.7.1 (canonical attribute names declared at D2 source under F4-authoritative-naming-honored-at-source-D-ADR rule); ADR-D2 v1.2 §1.8 (sandbox-violation fail-class taxonomy table); ADR-F4 v1.1 §Consequences (a) line 40 + line 57 (F4-canonical attribute names); ADD §2.4 Synthesis closing sentence (sandbox.tier / sandbox.tech / sandbox.fail.class three-attribute structural anchor).

**Cross-axis citation.** `Spec_Information_Substrate_v1.md` C-IS-10 §10.1 (state-ledger entry shape export — Action Surface row; sandbox-violation events join on `idempotency_key`).

**Persona linkage.** Persona §10.2 (cost-attribution-per-span); §10.4 (compliance-readiness — tamper-evidence at sandbox-violation events).

**Specification content.**

### §15.1 Span hierarchy

Per ADR-D2 v1.2 §1.7:

```
subagent.span[i]  (or root tool.call span)
├── sandbox.enter         (attrs: sandbox.tier, sandbox.tech,
│                                 sandbox.provider,
│                                 sandbox.policy.assigned_tier_reason,
│                                 deployment_surface, blast_radius_tier,
│                                 mcp_transport, cold_start_ms,
│                                 pool_acquired: bool, persona_tier)
├── tool.call[]            (per-tool spans inside sandbox)
├── sandbox.violation      (attrs: sandbox.fail.class ∈ §15.5 enum;
│                                 details: depending on fail class)
├── sandbox.tier_escalation (attrs: from_tier, to_tier,
│                                  escalation_cause)
└── sandbox.exit           (attrs: sandbox.tier, sandbox.tech,
                                   sandbox.cost.tier_overhead_ms,
                                   sandbox.cost.tier_overhead_usd,
                                   pool_returned: bool)
```

### §15.2 Seven `sandbox.*` attribute names (declared at this contract per D2 §1.7.1)

Per ADR-D2 v1.2 §1.7.1 (canonical declaration site; six F4-canonical + one D2-introduced):

| Attribute | Type | Cardinality | Always-emitted on | Discriminator role |
|---|---|---|---|---|
| `sandbox.tier` | enum string ∈ `{tier-1-process, tier-2-container, tier-3-microvm, tier-4-full-vm}` | bounded (4) | `sandbox.enter` event | Structural; stable across tech swap (F4 canonical) |
| `sandbox.tech` | enum string ∈ `{microvm, container, vm, language-level, fs-overlay}` | low (5) | `sandbox.enter` event | Technology class; swap-friendly without schema migration (F4 canonical) |
| `sandbox.fail.class` | enum string per C-AS-04 §4.1 (seven values) | bounded (7) | `sandbox.violation` event | Failure-class taxonomy (F4 canonical) |
| `sandbox.policy.assigned_tier_reason` | enum string ∈ `{contract_minimum, blast_radius_floor, mcp_server_trust_floor, operator_policy_floor, sandbox_tier_floor, persona_tier_floor, sub_agent_monotonic_ascension}` | bounded (7) | `sandbox.enter` event | Audit surface for which `max()` floor won (F4 canonical) |
| `sandbox.cost.tier_overhead_ms` | int (milliseconds) | unbounded (metric) | `sandbox.exit` event | Per-call latency overhead (F4 canonical) |
| `sandbox.cost.tier_overhead_usd` | float (USD) | unbounded (metric) | `sandbox.exit` event | Per-call dollar overhead (F4 canonical) |
| `sandbox.provider` | enum string ∈ 17-value enumeration per ADR-D2 v1.2 §1.7 join table | medium (17 at v1.1; phase-2 may add) | `sandbox.enter` event | Vendor+tech instance (D2-introduced; declare-both-with-join with `sandbox.tech`) |

### §15.3 `sandbox.tech` ↔ `sandbox.provider` join contract

Per ADR-D2 v1.2 §1.7. Each `sandbox.provider` value belongs to exactly one `sandbox.tech` class (provider belongs-to tech is **functional**):

| `sandbox.tech` | `sandbox.provider` values |
|---|---|
| `microvm` | `e2b_firecracker`, `modal_gvisor`, `kata`, `bedrock_agentcore`, `vertex_agent_engine`, `anthropic_computer_use_vm` |
| `container` | `docker_oci`, `opensandbox`, `dify_sandbox`, `daytona` |
| `vm` | (reserved; full-VM tier candidates per F4 deferred microVM / full-VM tier; D2 §1.2 carries this as future) |
| `language-level` | `deno`, `language_level` |
| `fs-overlay` | `bubblewrap`, `seatbelt`, `fuse_overlay`, `fuse_projfs`, `kilocode_worktree` |

The join mapping is **operator-tunable at workload-binding-time** (operators with custom microVM providers register them under `sandbox.tech=microvm`); the table above is the design-time default per Pattern Reference Catalog v1.0 §11.3.2 D2 substrate enumeration.

### §15.4 Sampling discipline

Per ADR-D2 v1.2 §1.7:

| Event | Sampling rate |
|---|---|
| `sandbox.enter` | Base-rate sampled (matches `tool.call` parent) |
| `sandbox.exit` | Base-rate sampled (matches `tool.call` parent) |
| `sandbox.violation` | **Always-sampled (head=1.0; tail-keep-on-classification=true)** |
| `sandbox.tier_escalation` | **Always-sampled (head=1.0)** |

The always-sampled posture for `sandbox.violation` and `sandbox.tier_escalation` is a **hard floor at the deployment-binding layer** — not operator-tunable at base-rate. Cost-attribution-per-sandbox-instance via `sandbox.cost.tier_overhead_*` follows base-rate at `sandbox.exit` with per-cell rollup at fan-out close per ADR-D4 v1.1 §1.9 (cross-axis to Control Plane spec session 3).

### §15.5 Sensitive-data discipline

Per ADR-D2 v1.2 §1.7 sensitive-data default-off + structure-not-content discipline:

| Property | Contract |
|---|---|
| **Structure-not-content** | Span attributes record sandbox boundary semantics (tier, tech, provider, surface, fail class, policy reason) but NEVER raw tool I/O content |
| **Exclusion at T-perm-2 surface** | Sandbox-resident filesystem state and screenshot context (T-perm-2 surface per ADD §5.2.2) are explicitly excluded from span attributes |
| **Composition with C-AS-08** | Sandbox-violation tamper-evidence emits audit-ledger entry via C-AS-08 with `outputs_hash` covering the structure (not the violation content) |

### §15.6 Cross-axis composition reference

Per `Spec_Information_Substrate_v1.md` C-IS-10 §10.1 (state-ledger entry shape export — Action Surface row "Sandbox-violation events join on `idempotency_key` per ADR-D2 v1.2 §1.8 fail-class taxonomy"):

| Property | Contract |
|---|---|
| **Idempotency-key join** | `sandbox.violation` events on a given `tool.call` parent span carry the same `idempotency_key` as the parent; cross-axis correlation surface for cost-attribution-per-span (D6) and engine event history (D1) |
| **Sub-agent boundary inheritance** | At sub-agent dispatch, the sub-agent's `sandbox.enter` event carries a new `idempotency_key` derived from the parent's `idempotency_key` via sub-agent-dispatch-keyed extension (composes against ADR-D4 v1.1 §1.9 multi-agent span hierarchy at session 3) |
| **Cost-attribution joining** | `sandbox.cost.tier_overhead_*` per-sandbox-instance attributes join on `idempotency_key` at D6 cost-attribution-per-span dashboarding (cross-axis to Operational Discipline spec at session 4) |

### §15.7 Capability-floor (iv) traceability

Per ADR-D2 v1.2 §1.7.1 + ADR-F3 v1.1 capability-floor (iv): F3 capability-floor (iv) requires observable lifecycle including sandbox-related events. This contract declares the attribute substrate at D2 source per F2-05 sandbox sub-finding closure. **ADR-D6 §1.2 row `sandbox.*` reads from this contract verbatim**; the F4-authoritative-naming honored at this source contract — D6 §1.2 ingests without re-declaration (cross-axis to Operational Discipline spec at session 4).

**Deferred to implementation discretion.** Specific OTel/OTLP span emission implementation; specific tail-keep-on-classification filter implementation; specific per-cell `sandbox.cost.tier_overhead_*` metric aggregation window; specific sub-agent `idempotency_key` extension algorithm (delegated to D4 §1.9 at session 3).

### §15.8 `MCPInvocationFailClass` enum (NEW at v1.6)

Four-value MCP-protocol-layer fail-class taxonomy, sibling to the F4 process-execution-layer taxonomy at C-AS-04 §4.1. F4 carries what FAILED inside the sandboxed process; this enum carries what FAILED at the MCP-protocol boundary. The two layers compose at the `sandbox.violation` child span carrying both `sandbox.fail.class` (F4) and `mcp.fail.class` (this enum) attributes per §15.9.

| `mcp.fail.class` | Semantic | Production exception correlate | C5 fail-class | C9 retry posture |
|---|---|---|---|---|
| `transport` | MCP host process unreachable; network-layer or process-lifecycle failure prevents reaching the MCP server boundary at all | `MCPHostUnreachableError` (and equivalent host-reachability failures) | transient-fail | C9 backoff + retry; max 3 attempts per Cluster 3 retry protocol [HIGH]; on exhaustion → HITL escalation |
| `protocol_error` | MCP protocol-layer error — the MCP exchange itself was malformed (invalid JSON-RPC envelope, missing required fields, protocol-version mismatch, etc.) | `ToolInvocationProtocolError` (and equivalent protocol-violation failures) | permanent-fail (deterministic protocol hit; the same exchange will fail identically on retry) | NO retry; tool registry update OR HITL escalation per C-AS-12 §12.2 operator-policy override |
| `schema_violation` | Tool I/O schema mismatch — the MCP exchange completed but the tool's response did not match its declared JSON schema (or the request was rejected at schema validation pre-dispatch) | `jsonschema.ValidationError` raised at tool-input/output schema enforcement | permanent-fail (the tool contract is the violated invariant) | NO retry; per-tool C9 retry-exit per Cluster 4 §2.2.3 [HIGH] absent; audit ledger per C-AS-08 |
| `timeout` | MCP call exceeded its per-call time budget at the protocol boundary (the call MAY have completed inside the sandboxed process; the MCP exchange itself timed out) | `ToolInvocationTimeoutError` (and equivalent MCP-call-timeout failures) | transient-fail | C9 backoff + retry; max 3 attempts per Cluster 3 retry protocol [HIGH]; note: parallels F4 `timeout` at process-execution layer but they are distinct attributes — an MCP timeout MAY have a sandbox process that completed (server-side delay) or did not complete (client-side blocking); both `mcp.fail.class = timeout` and `sandbox.fail.class = timeout` MAY co-occur or independently fire |

**Cardinality + sampling.** Bounded (4); always-emitted on `sandbox.violation` event per §15.9 alongside `sandbox.fail.class`. Always-sampled (head=1.0) discipline at §15.4 row 3 applies to the carrying event (`sandbox.violation`); both attribute names ride the same sampling posture.

**Authority anchors.** This contract is authored at AS-axis as canonical declaration site per the producer-vs-canonical-schema separation discipline at v1.4 §14.3 footer note (workspace `CLAUDE.md` §1.1: "CP-axis emits, AS-axis owns canonical schema" generalizes to: "runtime-axis emits the MCP-fail-class mapping at dispatcher; AS-axis owns the canonical enum + sampling + sensitive-data discipline"). Cross-axis citation: `Spec_Harness_Runtime_v1.md` §14.9 C-RT-19 producer-side mutation discipline owns the dispatcher exception-handler-to-`mcp.fail.class` mapping at `harness-runtime/src/harness_runtime/lifecycle/runtime_tool_dispatcher.py:395-412`.

**Composition with F4.** §15.10 below authors a best-effort projection table mapping MCP-shape values to F4-shape values, used at the dispatcher to emit BOTH attributes simultaneously per §15.9. The projection is best-effort because MCP-protocol-shape concerns DO NOT cleanly map to process-execution-shape concerns at all values; the projection table acknowledges semantic stretch where it occurs.

**Deferred to implementation discretion.** Specific dispatcher exception-handler-to-enum-value mapping at runtime spec §14.9 producer site; specific projection-table application at the §15.10 projection layer; specific telemetry filtering at tail-keep-on-classification per §15.4.

### §15.9 `mcp.fail.class` attribute on `sandbox.violation` child span (NEW at v1.6)

The `sandbox.violation` child span per §15.1 hierarchy carries TWO fail-class attributes simultaneously at v1.6 forward:

| Attribute | Source enum | Layer | Discriminator role |
|---|---|---|---|
| `sandbox.fail.class` | C-AS-04 §4.1 7-value `SandboxFailClass` | Process-execution layer | What FAILED inside the sandboxed process (escape attempt, OOM, signal, etc.) |
| `mcp.fail.class` | §15.8 4-value `MCPInvocationFailClass` (NEW at v1.6) | MCP-protocol layer | What FAILED at the MCP-protocol boundary (host unreachable, protocol malformed, schema violated, timeout) |

**Emission discipline.** Both attributes always-emitted on the `sandbox.violation` event per §15.4 always-sampled (head=1.0) discipline. Either attribute MAY carry `null` (or be omitted-not-null per OTel attribute semantics) when the violation does not span both layers:

| Violation scenario | `sandbox.fail.class` | `mcp.fail.class` |
|---|---|---|
| Sandbox containment breach detected by seccomp / cgroup / hypervisor; MCP exchange did not begin | `escape_attempt` | omitted-not-null (no MCP-layer event) |
| MCP host process unreachable (network failure pre-dispatch) | omitted-not-null (no process-layer event) | `transport` |
| Tool returned valid response but its content fails schema validation post-dispatch | omitted-not-null (process completed normally) | `schema_violation` |
| MCP call timed out at protocol boundary; sandboxed process may or may not have completed | per §15.10 projection table (`timeout` at process layer if completion not detectable; omitted-not-null if process completed but server-side held the response) | `timeout` |
| Sandbox tier downgrade attempt via operator policy override (deterministic policy hit) | `policy_override` per §4.1 + §11.5 row 3 | omitted-not-null (policy hit is process-layer concern, not MCP-protocol) |

**Cross-axis composition.** `mcp.fail.class` joins on `idempotency_key` per §15.6 — the violation event's `idempotency_key` matches the parent `tool.call` span's. Audit-ledger surface at C-AS-08 records BOTH attribute values (or null) per F2-12 closure manifest (Audit Schema records the structure, not the content; both fail-class attribute values are structural metadata).

**Sensitive-data discipline.** Per §15.5 structure-not-content rule: both attribute values are enum-bounded (4 + 7 = 11 distinct strings); neither carries raw I/O content. The structure is auditable; the content remains in T-perm-2 surface exclusion.

**Authority anchors.** ADR-D2 v1.2 §1.7 + §1.7.1 (canonical sandbox.* attribute declaration site at C-AS-15); ADR-D6 §1.2 row `sandbox.*` ingests this attribute verbatim post-v1.6 (the namespace continues to be C-AS-15 §15 owned; OD-axis reads via §C-OD-04 base layer + §C-OD-06 AS-source verification per OD spec v1.11).

### §15.10 Best-effort projection table — `mcp.fail.class` → `sandbox.fail.class` (NEW at v1.6)

When a `sandbox.violation` event carries a non-null `mcp.fail.class` value AND the violation does not have a clean independent process-execution-layer signal, the runtime SHOULD project to a `sandbox.fail.class` value per the following table to maintain F4 audit-ledger continuity at the structural level:

| `mcp.fail.class` (MCP-shape) | Projected `sandbox.fail.class` (F4 process-shape) | Projection rationale | Semantic stretch |
|---|---|---|---|
| `transport` | `exit_nonzero` | Host unreachable = sandboxed process unable to communicate; cleanest F4 correlate per "process exited without normal completion" | MODERATE — F4 `exit_nonzero` means process exited with non-zero status; transport failure may or may not involve a process exit at all (e.g., process never started). Projection is for audit-ledger continuity, not semantic equivalence. |
| `protocol_error` | `exit_nonzero` | Protocol malformed = sandboxed process produced output that failed protocol-layer validation; cleanest F4 correlate per "process completed but output is not consumable" | MODERATE — same rationale as `transport`. The projection treats protocol violation as a structural process-exit anomaly even though the process may have exited cleanly. |
| `schema_violation` | `policy_override` | Schema violation = the tool contract (the I/O schema) was violated; closest F4 correlate per §4.1 row 7 "operator-tunable downgrade per C-AS-12 §12.2 audit-ledger entry" (analogous: a contract violation is an audit-ledger entry, not a process containment breach) | HIGH — F4 `policy_override` is documented as "operator-tunable downgrade", not "contract violation". The projection acknowledges this stretch; future spec revision MAY add a F4 `contract_violation` value to absorb this projection cleanly. |
| `timeout` | `timeout` | Direct one-to-one mapping at the value name (both enums share the value); the projection asserts that an MCP-layer timeout SHOULD also fire a process-layer timeout attribute when the dispatcher cannot independently detect process completion | CLEAN at value name; SEMANTIC STRETCH at layer interpretation — an MCP timeout MAY have a process that completed (server-side held the response); the projection assigns the process-layer timeout for audit-ledger continuity even when the process semantically did not time out. |

**Projection is best-effort.** The rationale + semantic-stretch columns acknowledge that MCP-shape and F4 process-shape are different abstraction layers; projection forces a structural correspondence for audit-ledger continuity but does NOT claim semantic equivalence. The `mcp.fail.class` attribute remains the authoritative MCP-layer record; `sandbox.fail.class` (projected) provides F4-layer compatibility for systems that read only the F4 attribute.

**Implementation discretion.** The dispatcher at runtime spec §14.9 producer site MAY:
(a) Apply the projection table verbatim at exception-handler binding (recommended default — emit BOTH attributes from BOTH enums per §15.9 emission discipline matrix), OR
(b) Emit only `mcp.fail.class` and let downstream OD-axis ingestion compute the projected `sandbox.fail.class` at audit-ledger consumption (per OD spec §C-OD-06 AS-source verification) — this option requires an OD spec extension authoring the projection logic at OD axis, NOT undertaken at v1.6 spec amendment.

**Authority anchors.** §15.8 (MCPInvocationFailClass enum); §4.1 (SandboxFailClass enum, PRESERVED VERBATIM); §15.9 (dual-attribute emission discipline). Future ADR-D2 revision arc MAY ratify the projection at ADR layer (currently AS-spec-internal contract additive); deferred to operator-discretion timing per X-AL-3 no-silent-design-extension discipline.

---

## §16 C-AS-16 — Action Surface substrate seam exports surface

**Contract surface.** Cross-axis exports from this spec for sessions 3–4 and session 5 composition document to consume by citation.

**PRD requirement(s) satisfied.** All seven R-AS-* (cross-axis composition surface; this contract is the analog of C-IS-10 for the Action Surface axis).

**ADR commitment(s) honored.** ADR-D2 v1.2 §1.7.1 (sandbox-bounded span schema source declaration); ADR-D3 v1.2 §1.8.1 (six attribute namespace source declarations); ADR-F4 v1.1 §Consequences (a) (F4-authoritative attribute naming); ADR-F5 v1.1 §Decision (structure-not-content audit composition).

**Persona linkage.** Persona §10.2 (cost-attribution-per-span); §10.4 (compliance-readiness — cross-axis tamper-evidence composition).

**Specification content.**

### §16.1 Sandbox-bounded span schema export

**Export surface.** C-AS-15 — seven `sandbox.*` attributes with `sandbox.tech` ↔ `sandbox.provider` join contract.

| Consuming axis | Composition reference | Cross-spec citation target |
|---|---|---|
| Operational Discipline (D6 v1.1 §1.2 row `sandbox.*`) | D6 §1.2 reads from C-AS-15 §15.2 verbatim under F4-canonical-naming-honored-at-source-D-ADR rule | `Spec_Operational_Discipline_v1.md` C-OD-* on D6 §1.2 ingestion |
| Control Plane (D4 v1.1 §1.9 multi-agent span hierarchy) | Sub-agent dispatch composes with sandbox-enter/exit events per the parent/child relationship | `Spec_Control_Plane_v1.md` C-CP-* on D4 §1.9 |
| Control Plane (D5 v1.3 §1.10 pre-HITL escalation) | Sandbox-violation `sandbox.fail.class` routes per C-AS-04 §4.2 staircase; C11 HITL composition | `Spec_Control_Plane_v1.md` C-CP-* on D5 §1.10 |

### §16.2 5-axis multiplicative tunable export

**Export surface.** C-AS-12 — `per_tool_gate_level × per_mcp_server_trust_tier × persona_tier × blast_radius_tier × sandbox_tier`.

| Consuming axis | Composition reference |
|---|---|
| Control Plane (D5 v1.3 §1.5 multiplicative gate-level rule) | C-AS-12 §12.1 specializes the D5-layer 4-axis tunable by adding `sandbox_tier`; D5 4-axis surface composes at session 3 |
| Control Plane (D4 v1.1 §1.5 sub-agent privilege inheritance) | C-AS-11 sub-agent sandbox-tier monotonic-ascension composes with D4 §1.5 sub-agent privilege inheritance default-downgrade per ADD §5.3.2 |
| Cross-axis (ADD §5.2.1 T-perm-1 multi-layer resolution) | T-perm-1 closure shape locked at C-AS-12 §12.5 multiplicative `max()`; future Phase 4+ adjacencies engage this contract |

### §16.3 Secret-fetch structure-not-content audit export

**Export surface.** C-AS-08 — `outputs_hash` formula + audit-ledger entry composition against C-IS-05.

| Consuming axis | Composition reference |
|---|---|
| Operational Discipline (D5 v1.3 §1.4 audit-ledger cryptographic shape per persona-tier) | C-AS-08 §8.5 per-persona-tier signature extensions compose at session 4 |
| Information Substrate (C-IS-10 §10.1) | C-AS-08 is a consumer of C-IS-10; the export pattern is established at the Information Substrate spec |

### §16.4 Six Anthropic-primitive attribute namespace export

**Export surface.** C-AS-14 — six namespaces (`anthropic.*` / `mcp.*` / `skill.*` / `managed_agents.*` / `files.*` / `memory.*`) with audit-floor commitments.

| Consuming axis | Composition reference |
|---|---|
| Operational Discipline (D6 v1.1 §1.2 specialization-layer rows) | D6 §1.2 ingests each namespace row from C-AS-14 §§14.2–14.7 verbatim under Pattern P1 mechanical-alignment discipline at session 4 |
| Operational Discipline (D6 v1.1 §1.3 sampling discipline) | C-AS-14 §14.8 audit-floor commitments are binding on D6 §1.3 ingestion (per ADR-D3 v1.2 §1.8 F2-09 forward-reference); D6 must distinguish `mcp.tool.call` from non-MCP `tool.call` |

### §16.5 Per-tool `required_secrets` allowlist export

**Export surface.** C-AS-06 — per-tool allowlist as separate access-control dimension alongside `assigned_tier`.

| Consuming axis | Composition reference |
|---|---|
| Control Plane (D5 v1.3 §1.5 multiplicative gate-level rule) | `required_secrets` is orthogonal to gate-level; per ADR-F5 v1.1 §"Permanent tensions engaged" T-perm-1 touch — NOT a fifth `max()` floor; ledger-reference-only carry-forward |

### §16.6 Eleven-primitive adoption-depth matrix export

**Export surface.** C-AS-13 — 11-primitive × 4-workload-class matrix + per-engine-class composition overlay + workload-binding-time selection contract.

| Consuming axis | Composition reference |
|---|---|
| Control Plane (D4 v1.1 §1.2 per-workload-class topology commitment) | C-AS-13 §13.4 per-sub-agent-role × model-binding contract inherits D4 §1.2 row at session 3 |
| Control Plane (D1 v1.1 §1.1 engine-class taxonomy) | C-AS-13 §13.3 per-engine-class composition site overlay specializes D1 engine classes at session 3 |
| Cross-axis (T-perm-3 D3-layer adjacency per ADD §5.2.3) | C-AS-13 §13.5 Anthropic-API graceful-degradation composes with F1 cross-family fallback at session 3 |

### §16.7 Forcing-condition export

**Export surface.** C-AS-01 §1.3 + C-AS-09 §9.3 forcing-condition cell resolution rules.

| Consuming axis | Composition reference |
|---|---|
| Control Plane (D5 v1.3 §1.10 pre-HITL escalation) | `escape_attempt` / `egress_denied` / `signal` (permanent-fail) skip the C-AS-04 §4.2 staircase per D5 §1.10 — cross-axis composition at session 3 |

**Deferred to implementation discretion.** Specific cross-spec citation strings (resolved at sessions 3–4 + session 5 composition document); specific seam-versioning convention if F4 / F5 / D2 / D3 ever revise (out of scope at v1).

---

## §[carry-forwards]

This meta-section documents PRD-inherited carry-forward items per `Phase_5_Session_2_Session_Prompt.md` §5.4. Entries are **documentation, not contract-bearing** — they do not engage the §[coherence pass] §6.1 per-contract audit; they engage the spec's operator-visibility surface.

### [CF-1] F2-12 — D1 v1.1 → v1.2 replay-trace-emission contract

**Status.** 🔄 Deferred-acknowledged at ADD v1.2 §6.3.1 (inherited at PRD v1.0 §[carry-forwards] [CF-1]; inherited at session-1 spec §[carry-forwards] [CF-1]; inherited here); not blocking session 2 entry; not blocking session 2 filing.

**Action Surface spec engagement.** Minimal. D2 v1.1 sandbox-violation events join on `idempotency_key` per ADR-D2 v1.1 §1.8 (composed at C-AS-15 §15.6); the `idempotency_key` join consumes C-IS-10 §10.2 export. F2-12 (the replay-trace-emission contract) routes through Control Plane (session 3) where D1 v1.1 → v1.2 lives; specifically, R-CP-07 binding to engine-class-visible replay-resumption per PRD §[carry-forwards] [CF-1] is the Control Plane surface that engages F2-12. **No Action Surface contract is open as a function of F2-12** — the Action Surface substrate consumption of `idempotency_key` is uniform across replay scenarios (sandbox-violation events join semantically regardless of whether the parent `tool.call` is a replay or a fresh execution).

**Forward routing.** Parallel `council-orchestrator` C7+C9 session at operator discretion per ADD §6.3.1 active path. Closure expected as D1 v1.2 + D6 v1.2; absorbed into ADD v1.3; PRD revision pass produces `PRD_v1.1.md`; Phase 5 revision-pass at affected spec sections (Control Plane spec + Operational Discipline spec). Action Surface spec is NOT a revision target for F2-12 closure.

### [CF-2] Workflow §7 substrate-skill propagation

**Status.** Open operator decision; outside P3-CK closure scope; outside PRD scope; outside Phase 5 scope.

**Origin.** `Project_Workflow_Revision_log.md` v1.4 entry line 297 footnote — `add-consolidation-protocol.md` §3.5 Step 5 substrate-skill update to reference Workflow v1.4 §2.3.5 clause (iv) is a separate skill-substrate revision not in v1.4 scope.

**Action Surface spec engagement.** Not in spec scope (skill-substrate revision is neither architectural commitment nor observable behavior nor specification-grade contract). Documented here for operator-visibility per inheritance from PRD §[carry-forwards] [CF-2] and session-1 spec §[carry-forwards] [CF-2].

**Forward routing.** Operator decision at discretion. No specification revision is triggered by skill-substrate propagation.

---

## §[traceability]

PRD-requirement-to-spec-contract sub-matrix for the Action Surface axis. Rows = 7 PRD requirements; columns = 16 spec contracts. `✓` indicates the contract satisfies the requirement (≥1 contract surface implements the requirement's observable behavior).

| PRD R-ID | C-AS-01 | C-AS-02 | C-AS-03 | C-AS-04 | C-AS-05 | C-AS-06 | C-AS-07 | C-AS-08 | C-AS-09 | C-AS-10 | C-AS-11 | C-AS-12 | C-AS-13 | C-AS-14 | C-AS-15 | C-AS-16 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| R-AS-01 | ✓ | ✓ |  |  |  |  |  |  |  |  | ✓ | ✓ |  |  | ✓ | ✓ |
| R-AS-02 |  |  |  | ✓ |  |  | ✓ |  |  |  |  |  |  |  | ✓ | ✓ |
| R-AS-03 |  | ✓ | ✓ |  |  |  |  |  |  |  |  |  |  |  |  | ✓ |
| R-AS-04 |  |  |  |  | ✓ | ✓ | ✓ |  |  |  |  |  |  |  |  | ✓ |
| R-AS-05 |  |  |  |  |  |  |  | ✓ |  |  |  |  |  |  |  | ✓ |
| R-AS-06 |  |  |  |  |  |  |  |  | ✓ | ✓ | ✓ | ✓ |  |  | ✓ | ✓ |
| R-AS-07 |  |  |  |  |  |  |  |  |  |  |  |  | ✓ | ✓ |  | ✓ |

**Sub-matrix verification checks:**

| Rule | Result |
|---|---|
| Every R-AS-* has ≥1 satisfying contract | ✅ — R-AS-01 (5); R-AS-02 (3); R-AS-03 (3); R-AS-04 (4); R-AS-05 (2); R-AS-06 (6); R-AS-07 (3) |
| Every C-AS-* has ≥1 R-AS-* it satisfies | ✅ — C-AS-01 (R-AS-01); C-AS-02 (R-AS-01 + R-AS-03); C-AS-03 (R-AS-03); C-AS-04 (R-AS-02); C-AS-05 (R-AS-04); C-AS-06 (R-AS-04); C-AS-07 (R-AS-02 + R-AS-04); C-AS-08 (R-AS-05); C-AS-09 (R-AS-06); C-AS-10 (R-AS-06); C-AS-11 (R-AS-01 + R-AS-06); C-AS-12 (R-AS-01 + R-AS-06); C-AS-13 (R-AS-07); C-AS-14 (R-AS-07); C-AS-15 (R-AS-01 + R-AS-02 + R-AS-06); C-AS-16 (all seven) |
| 7 PRD requirements present (R-AS-01 through R-AS-07) | ✅ |
| 16 spec contracts present (C-AS-01 through C-AS-16) | ✅ |
| Substrate ADR versions match PRD substrate set | ✅ — F4 v1.1 / F5 v1.1 / D2 v1.1 / D3 v1.1 (matches `Phase_5_Session_2_Session_Prompt.md` §3.2 substrate version table) |

**Sub-matrix verification: PASS (5/5 rules).**

---

## §[coherence pass]

Pre-emission self-audit per `Phase_5_Session_2_Session_Prompt.md` §6. Five audit dimensions; spec does not file unless all five return ✅ PASS.

### Audit 6.1 — Per-contract audit (16 contracts × 8 sub-dimensions)

| Sub-dimension | Verification posture | Result |
|---|---|---|
| PRD requirement trace | Every spec contract cites ≥1 PRD R-ID; cited requirement is in session-2 axis scope (R-AS-01 through R-AS-07) | ✅ PASS — spot-check: C-AS-01 cites R-AS-01; C-AS-04 cites R-AS-02; C-AS-08 cites R-AS-05; C-AS-13 cites R-AS-07; C-AS-16 cites all seven as the substrate seam exports surface. 16 of 16 contracts carry PRD requirement citations |
| ADR commitment trace | Every spec contract cites ≥1 ADR by ID **and** section per inversion-discipline analog | ✅ PASS — spot-check: C-AS-01 cites `ADR-F4 v1.1 §Decision + §Rationale (a) + ADD §2.4 Synthesis`; C-AS-04 cites `ADR-F4 v1.1 §Consequences (a) + ADR-D2 v1.1 §1.8 + §1.7.1 + ADD §2.4 Synthesis`; C-AS-08 cites `ADR-F5 v1.1 §Decision + §"Permanent tensions engaged" + ADD §2.5 Synthesis`; C-AS-13 cites `ADR-D3 v1.1 §1.1 + §1.2 + §1.3 + §1.4 + §1.5 + §1.6 + §1.7 + §1.9 + ADD §3.3.2 Synthesis`. 16 of 16 contracts carry section-level ADR citations |
| Cross-axis citation | Spec contracts that compose against the Information Substrate substrate seam cite `Spec_Information_Substrate_v1.md` C-IS-* by contract ID + section | ✅ PASS — C-AS-08 cites C-IS-05 + C-IS-06 + C-IS-07 §7.1 + C-IS-10 §10.1 (four cross-axis citations); C-AS-15 cites C-IS-10 §10.1 (one cross-axis citation); C-AS-16 declares the Action Surface exports surface analogous to C-IS-10 (no consumption citation; export surface). Three contracts carry cross-axis Information Substrate citations; all resolve to section/contract present in `Spec_Information_Substrate_v1.md` |
| No-architecture-introduction | No spec contract adds architectural commitment beyond ADR + ADD + Information Substrate spec content; contracts compose committed material into specification-grade precision | ✅ PASS — all 16 contracts derive directly from ADR-F4 v1.1 + ADR-F5 v1.1 + ADR-D2 v1.1 + ADR-D3 v1.1 + ADD v1.2 + Information Substrate spec content. No contract asserts architecture beyond the substrate. The contract-default-tier policy at C-AS-03 §3.3 carries explicit "specific commitment is a tool-registry D-ADR" notation preserving deferral |
| Translate-not-restate | No spec contract restates PRD observable-behavior text, ADR Decision text, or Information Substrate spec contract text verbatim; contracts translate via composition | ✅ PASS — every contract section provides specification-grade structure (signatures, schemas, formulas, enums, tables, surface contracts) absent from PRD prose; ADR Decision text is cited by section, not restated; Information Substrate spec contracts are cited by ID + section, not restated. Spot-check: C-AS-08 §§8.1–8.5 decomposes ADR-F5 v1.1 §Decision structure-not-content audit composition into per-step signatures + per-step contracts + cross-axis composition matrix (the audit composition is asserted at F5 but not signatured) |
| Persona linkage preserved | Every spec contract preserves the persona §X.y anchor from its parent PRD requirement | ✅ PASS — spot-check: C-AS-01 carries Persona §5.1 + §8.1 + §10.1 inherited from R-AS-01; C-AS-08 carries Persona §10.4 + §10.2 inherited from R-AS-05; C-AS-13 carries Persona §5 + §6 + §7 inherited from R-AS-07; C-AS-15 carries Persona §10.2 + §10.4 inherited from R-AS-01/02/06. 16 of 16 contracts carry persona anchors |
| Contract grade | Every spec contract sits at specification grade (signature / schema / formula / enum / surface contract / matrix); no implementation-grade choices beyond what ADRs commit | ✅ PASS — contract surfaces are: C-AS-01 tier-set enum (4 values) + per-tier capability requirements (schema); C-AS-02 composition signature + formula + lookup table (signature + formula + table); C-AS-03 tool contract field signature (schema); C-AS-04 seven-value enum + retry-posture per class (enum + table); C-AS-05 function signature + tier-aware resolution table (signature + table); C-AS-06 allowlist entry signature + access-control composition (schema + surface contract); C-AS-07 five-value enum + breaker placement (enum + table); C-AS-08 hash formula + audit composition (formula + schema); C-AS-09 12-cell matrix + 6-class enumeration (matrix + enum); C-AS-10 per-transport lookup table (table); C-AS-11 sub-agent tier signature + monotonic ascension rule (signature + surface contract); C-AS-12 5-axis multiplicative composition (formula + table); C-AS-13 11-primitive enumeration + 2D matrix + per-engine overlay + binding contract (enum + matrices + contract); C-AS-14 six namespace declarations × per-namespace attribute tables (schemas); C-AS-15 span hierarchy + seven attribute names + join contract (schema + tables); C-AS-16 export surfaces analogous to C-IS-10 (surface contract). No implementation-grade commitments beyond ADR-declared (specific candidate selection, library bindings, API surfaces explicitly deferred) |
| Deferred-to-implementation discretion documented | Contracts that defer detail to Phase 6 implementation discretion per Workflow §2.5.1 exit criteria language carry explicit "deferred to implementation discretion" notation | ✅ PASS — 15 of 16 contracts carry explicit "Deferred to implementation discretion" notation (C-AS-16 is a meta-contract referencing other contracts' implementation deferrals); deferrals include: specific tier-mechanism candidates per cell (C-AS-01); blast-radius taint-state propagation mechanism (C-AS-02); tool-contract serialization format (C-AS-03); sandbox-violation detection mechanism (C-AS-04); specific keyring-library binding (C-AS-05); allowlist-enforcement implementation (C-AS-06); breaker trip-threshold values (C-AS-07); canonicalize_concat implementation (C-AS-08); candidate-within-provider-class selection (C-AS-09); MCP server registration mechanism (C-AS-10); sub-agent dispatch mechanism (C-AS-11); runtime evaluation engine for 5-axis max() (C-AS-12); Memory tool storage backend (C-AS-13); OTel/OTLP exporter implementation (C-AS-14); OTel/OTLP span emission implementation (C-AS-15) |

**Audit 6.1 aggregate: ✅ PASS (8/8 sub-dimensions across all 16 contracts).**

### Audit 6.2 — PRD-requirement-to-spec sub-matrix audit (Action Surface axis only)

| Sub-dimension | Result |
|---|---|
| Every session-2 PRD requirement has ≥1 spec contract satisfying it | ✅ PASS — R-AS-01 (5 contracts: C-AS-01, C-AS-02, C-AS-11, C-AS-12, C-AS-15); R-AS-02 (3 contracts: C-AS-04, C-AS-07, C-AS-15); R-AS-03 (3 contracts: C-AS-02, C-AS-03, plus C-AS-16 export surface); R-AS-04 (4 contracts: C-AS-05, C-AS-06, C-AS-07, plus C-AS-16); R-AS-05 (2 contracts: C-AS-08, plus C-AS-16); R-AS-06 (6 contracts: C-AS-09, C-AS-10, C-AS-11, C-AS-12, C-AS-15, plus C-AS-16); R-AS-07 (3 contracts: C-AS-13, C-AS-14, plus C-AS-16) |
| Every session-2 spec contract has ≥1 PRD requirement it satisfies | ✅ PASS — no orphan contracts; every C-AS-01 through C-AS-16 cites ≥1 PRD R-ID |
| ADR commitments cited at session-2 spec are at versions matching PRD substrate set | ✅ PASS — F4 cited at v1.1; F5 cited at v1.1; D2 cited at v1.1; D3 cited at v1.1; matches `Phase_5_Session_2_Session_Prompt.md` §3.2 substrate version table; matches PRD §"ADR substrate set" table |
| Cross-axis citations resolve | ✅ PASS — every Information Substrate spec citation (C-IS-XX § Y.Z) verified to resolve to a section / contract present in `Spec_Information_Substrate_v1.md`: C-IS-05 (state-ledger entry shape, present at §5); C-IS-06 (hash-chain integrity construction, present at §6); C-IS-07 §7.1 (C3-pole write contract, present at §7.1); C-IS-10 §10.1 (state-ledger entry shape export, present at §10.1); C-IS-10 §10.2 (idempotency-key join export, present at §10.2) |

**Audit 6.2 aggregate: ✅ PASS (4/4 rules).**

### Audit 6.3 — Front-matter audit (session-2 spec)

| Sub-dimension | Result |
|---|---|
| Session-2 axis declared at front-matter | ✅ PASS — Status block records "Axis: Action Surface"; Front-matter §"Axis declaration" + §"Axis-grounding note" carry rationale per OD-5-2.A handoff §3.1 recommendation followed |
| PRD substrate reference | ✅ PASS — `PRD_v1.0.md` §3 cited at Status block Source-set + Front-matter §"PRD requirement scope" |
| ADR substrate reference | ✅ PASS — F4 v1.1 + F5 v1.1 + D2 v1.1 + D3 v1.1 enumerated at Status block Source-set + Front-matter §"ADR scope" table |
| ADD substrate reference | ✅ PASS — ADD v1.2 §2.4 + §2.5 + §3.3.1 + §3.3.2 + §5.1 + §5.2.1 + §5.3.2 cited at Status block Source-set; specific ADD sub-sections cited at every contract that derives from F4 / F5 / D2 / D3 substrate |
| Information Substrate spec reference | ✅ PASS — `Spec_Information_Substrate_v1.md` cited at Status block Source-set; specific contracts (C-IS-05, C-IS-06, C-IS-07, C-IS-10) cited at Front-matter §"Cross-axis citation substrate" table; C-AS-08 + C-AS-15 + C-AS-16 specifically cite Information Substrate contracts |
| Persona substrate reference | ✅ PASS — Persona Document §4 + §5 + §5.1 + §6 + §7 + §8.1 + §9 + §10.1 + §10.2 + §10.4 enumerated at Status block Source-set + Front-matter §"Persona-linkage substrate" table; per-contract persona linkage inherited |
| Status posture | ✅ PASS — `Status: Proposed` per `Project_Workflow_v1_2.md` §3.1 (no clearance until aggregate P5-CK per Workflow §2.5.1 + OD-5-4.A) |

**Audit 6.3 aggregate: ✅ PASS (7/7 sub-dimensions).**

### Audit 6.4 — §[carry-forwards] inheritance audit

| Sub-dimension | Result |
|---|---|
| F2-12 carry-forward documented at session-2 spec | ✅ PASS — [CF-1] entry inherits PRD v1.0 §[carry-forwards] [CF-1] + session-1 spec §[carry-forwards] [CF-1] verbatim; explicit Action Surface spec engagement statement documents that no Action Surface contract is open as a function of F2-12 (Action Surface substrate consumption of `idempotency_key` is uniform across replay scenarios); forward routing documented |
| Workflow §7 substrate-skill propagation carry-forward documented | ✅ PASS — [CF-2] entry inherits PRD v1.0 §[carry-forwards] [CF-2] + session-1 spec §[carry-forwards] [CF-2] verbatim; explicit Action Surface spec engagement statement documents non-engagement |
| Carry-forward entries labeled as non-contract-bearing | ✅ PASS — meta-section preamble explicitly states "Entries are documentation, not contract-bearing — they do not engage the §[coherence pass] §6.1 per-contract audit" |

**Audit 6.4 aggregate: ✅ PASS (3/3 sub-dimensions).**

### Audit 6.5 — V3 deference audit

| Sub-dimension | Result |
|---|---|
| Confidence-tag schema | ✅ PASS — V3 `[HIGH]` / `[MODERATE]` / `[SPECULATIVE]` schema preserved; tags applied at the specification surfaces where uncertainty surfaces: MCP authorization spec 2025-06-18 cited [HIGH] at C-AS-10 §10.1 + C-AS-06 §6.3; lethal-trifecta architectural-cut cited [HIGH] at C-AS-10 §10.1; Cluster 3 §2.2 sandbox tradeoff table cited [HIGH] at C-AS-01 §1.1 mechanism-class column; Cluster 4 §2.3.3 tool-poisoning anchor cited [HIGH] at C-AS-14 §14.3 `mcp.primitive.signature.sha256`; primary-source [HIGH] anchors at C-AS-13 §13.1 eleven-primitive substrate; no fabricated [HIGH] tags |
| Citations resolve at section level | ✅ PASS — every ADR citation verified by reading the ADR section at the indicated location during substrate read (`view` calls on ADR-F4.md, ADR-F5.md, ADR-D2.md, ADR-D3.md, PRD_v1.0.md, Architectural_Design_Document_v1.md, Spec_Information_Substrate_v1.md, Phase_5_Session_2_Session_Prompt.md at session entry); every persona §X.y anchor verifiable at the indicated section (anchors inherited from PRD §[coherence pass] which audited persona anchors at PRD filing); every Information Substrate spec contract ID + section verifiable |
| Anti-fabrication discipline applied | ✅ PASS — no fabricated PRD requirements; no fabricated ADR sections; no fabricated Information Substrate spec contracts; no invented benchmarks / vendor capabilities; substrate retrieved via `view` against source files at session execution before emission; no novel primitives, providers, or mechanisms introduced beyond ADR substrate enumeration |
| Workflow v1.4 §2.3.5 clause (iv) analog | ✅ PASS — section-level citation discipline applied at contract granularity (analog to PRD requirement-granularity citation); every contract carries ADR-ID + section pair in its "ADR commitment(s) honored" sub-section; cross-axis citations carry spec-ID + contract-ID + section pair in their "Cross-axis citation" sub-sections |

**Audit 6.5 aggregate: ✅ PASS (4/4 sub-dimensions).**

### Coherence pass aggregate

| Audit dimension | Result |
|---|---|
| 6.1 Per-contract audit | ✅ PASS (8/8) |
| 6.2 PRD-requirement-to-spec sub-matrix audit | ✅ PASS (4/4) |
| 6.3 Front-matter audit | ✅ PASS (7/7) |
| 6.4 §[carry-forwards] inheritance audit | ✅ PASS (3/3) |
| 6.5 V3 deference audit | ✅ PASS (4/4) |

**Coherence pass: ✅ PASS at all five dimensions. Spec authorized for filing.**

---

*Filed 2026-05-13 at Phase 5 session 2 close → Phase 5 session 3 entry boundary. Session 2 scope: Action Surface axis specification per OD-5-2.A spec-writer judgment (handoff §3.1 recommendation followed); output `Spec_Action_Surface_v1.md` per OD-5-1.A axis-led decomposition. Phase 5 arc continues to session 3 (Control Plane) per `Phase_5_Entry_Handoff.md` §3.1 axis sequencing; session 3 session prompt filed at `Phase_5_Session_3_Session_Prompt.md`. Aggregate P5-CK at full specification close per Workflow §2.5.1 + OD-5-4.A. Phase 5 session 3 entry-gate AUTHORIZED against `PRD_v1.0.md` + ADD v1.2 + Persona Document + F1 v1.2 + F3 v1.1 + D1 v1.1 + D4 v1.1 + D5 v1.3 ADRs + `Spec_Information_Substrate_v1.md` + `Spec_Action_Surface_v1.md` as substrate.*