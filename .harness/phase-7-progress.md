# Phase 7 — Atomic-Unit Landing Progress

Workspace-internal progress ledger (skill `phase-7-implementation` Step 7).
NOT a design-phase artifact. One row per landed atomic unit. Coverage-matrix
updates happen at cluster close, not per unit.

## Sub-phase 7b — per-axis-stream landings

| Unit | Surface | Spec | Status | Commit | Date |
|---|---|---|---|---|---|
| U-IS-01 | Path-class registry schema | C-IS-01 §1 | ✅ landed | `feat(is): land U-IS-01` | 2026-05-15 |
| U-IS-03 | Artifact-tier registry schema | C-IS-02 §2 | ✅ landed | `feat(is): land U-IS-03` | 2026-05-15 |
| U-IS-02 | Path-resolver primitive | C-IS-01 §1 | ✅ landed | `feat(is): land U-IS-02` | 2026-05-15 |
| U-IS-04 | Git tier sub-role taxonomy | C-IS-03 §3 | ✅ landed | `feat(is): land U-IS-04` | 2026-05-15 |
| U-AS-01 | Sandbox-tier type declaration | C-AS-01 §1.1-1.2 | ✅ landed | `feat(as): land U-AS-01` | 2026-05-15 |
| U-AS-02 | Forced-tier resolution | C-AS-01 §1.3 | ✅ landed | `feat(as): land U-AS-02` | 2026-05-15 |
| U-AS-03 | Sandbox-fail-class taxonomy | C-AS-04 §4 | ✅ landed | `feat(as): land U-AS-03` | 2026-05-15 |
| U-AS-04 | Foundational discriminator enums | C-AS-02 §2.3 | ✅ landed | `feat(as): land U-AS-04` | 2026-05-15 |
| U-CP-15 | EngineClass enum + capability floors | C-CP-07 §7.1+§7.4 | ✅ landed | `feat(cp): land U-CP-15` | 2026-05-15 |
| U-OD-01 | 9-cell observability matrix | C-OD-01 §1.1+§1.3-1.5 | ✅ landed | `feat(od): land U-OD-01` | 2026-05-15 |
| U-OD-04 | OTel GenAI semconv 1.41.0 base layer | C-OD-04 §4.1-§4.5 | ✅ landed | `feat(od): land U-OD-04` | 2026-05-15 |
| U-CP-00 | WorkloadClass closed 4-value enum | C-CP-07 §7.3 | ✅ landed | `feat(core): land U-CP-00` | 2026-05-15 |
| U-CP-22 | TopologyPattern enum + admissibility | C-CP-10 §10.1-§10.3 | ✅ landed | `feat(cp): land U-CP-22` | 2026-05-15 |
| U-AS-05 | `blast_radius_floor` default mapping | C-AS-02 §2.4 | ✅ landed | `feat(as): land U-AS-05` | 2026-05-15 |
| U-AS-11 | `SandboxProviderClass` enum + metadata | C-AS-09 §9.2 | ✅ landed | `feat(as): land U-AS-11` | 2026-05-15 |
| U-CP-19 | `ResumptionKind` taxonomy + bindings | C-CP-08 §8.1 | ✅ landed | `feat(cp): land U-CP-19` | 2026-05-15 |
| U-CORE-01 | Cross-cutting shared-type set (`DeploymentSurface`, `PersonaTier`, `WorkflowEventClass`, 9 identity aliases) — carrier-thin | C-AS-09 §9.1+§9.4, C-IS-05 §5, C-CP-05 §5.1-§5.2, C-CP-13 §13.4 | ✅ landed | `feat(core): land U-CORE-01` | 2026-05-15 |
| U-OD-00 | OD-local audit-ledger composition types (`AuditPayload`, `AuditLedgerEntry`, `AuditLedger`, `AuditSignatureAttributes`, `SignatureAlgorithm`) | C-OD-14 §14.5, ADR-D5 §1.4/§1.4.1, C-OD-21 §21.2 | ✅ landed | `feat(od): land U-OD-00` | 2026-05-15 |
| U-CP-00b | CP schema-attribute utility enums (`AttributeValueType`, `Cardinality`) — carrier-split (9 structured types deferred) | aggregate of 7 CP attribute-schema contracts | ✅ landed | `feat(cp): land U-CP-00b` | 2026-05-15 |
| U-IS-07 | State-ledger entry shape schema (`StateLedgerEntry`, `Actor`, `ActorClass`, `Bytes32`, `ALL_ZEROS_SENTINEL`) | C-IS-05 §5 | ✅ landed | `feat(is): land U-IS-07` | 2026-05-15 |
| U-IS-13 | Workload manifest opt-in schema (`WorkloadManifestOptIns`, `CheckpointCadence`) | C-IS-08 §8.1-§8.2, C-IS-09 §9.1 | ✅ landed | `feat(is): land U-IS-13` | 2026-05-15 |
| U-IS-05 | JSONL event ledger file lifecycle (`initialize_jsonl_event_ledger`, `validate_jsonl_event_ledger_format`, `JsonlLedgerHandle`) | C-IS-03 §3 | ✅ landed | `feat(is): land U-IS-05` | 2026-05-15 |
| U-IS-06 | Atomic deploy-event composition + `verify_deploy_atomicity` (git-shell-out split-deploy verification) | C-IS-04 §4 | ✅ landed | `feat(is): land U-IS-06` | 2026-05-15 |
| U-IS-08 | Entry canonicalization + per-entry SHA-256 hash (`canonicalize`, `compute_response_hash`) | C-IS-06 §6.1-§6.2 | ✅ landed | `feat(is): land U-IS-08` | 2026-05-15 |
| U-IS-14 | Shadow-Git checkpoint primitive (`create_shadow_git_checkpoint`, `should_checkpoint`) — `on_workflow_event` deferred (tension F-3) | C-IS-08 §8.2-§8.4 | ✅ landed | `feat(is): land U-IS-14` | 2026-05-16 |
| U-IS-16 | Worktree-isolation primitive (`WorktreeIsolationManager`: allocate/reclaim, concurrency cap) | C-IS-09 §9.2-§9.3 | ✅ landed | `feat(is): land U-IS-16` | 2026-05-16 |
| U-IS-09 | Chain-link construction primitive (`construct_prior_event_hash`) | C-IS-06 §6.3 | ✅ landed | `feat(is): land U-IS-09` | 2026-05-16 |
| U-IS-10 | Chain verification + tamper-evidence (`verify_chain`, `ChainVerificationResult`) | C-IS-06 §6.4-§6.5 | ✅ landed | `feat(is): land U-IS-10` | 2026-05-16 |
| U-IS-12 | C2-pole selective bounded read (`NavigationPrimitive`, 4 concrete primitives) | C-IS-07 §7.2-§7.3 | ✅ landed | `feat(is): land U-IS-12` | 2026-05-16 |
| U-IS-11 | C3-pole append-only write contract (`append_ledger_entry`, JSONL §7.3 format) | C-IS-07 §7.1-§7.3 | ✅ landed | `feat(is): land U-IS-11` | 2026-05-16 |
| U-IS-15 | Shadow-Git rollback primitive (`rollback_to_checkpoint`) | C-IS-08 §8.3 | ✅ landed | `feat(is): land U-IS-15` | 2026-05-16 |
| U-IS-17 | IS substrate seam exports manifest (terminal exporter — 6 seams) | C-IS-10 §10.1-§10.6 | ✅ landed | `feat(is): land U-IS-17` | 2026-05-16 |
| U-AS-12 | Operator-policy override scope per persona-tier (`override_scope`, `OverrideScopeResult`) | C-AS-09 §9.4 | ✅ landed | `feat(as): land U-AS-12` | 2026-05-16 |
| U-AS-20 | `fetch_secret` 3-param + `SecretRef` opaque + `SecretScope` + 4-row tier-resolution table | C-AS-05 §5.1-§5.2,§5.4 | ✅ landed | `feat(as): land U-AS-20` | 2026-05-16 |
| U-AS-28 | Eleven-primitive `AnthropicPrimitive` enum + 44-cell adoption-depth matrix + cross-axis IS path-contract binding | C-AS-13 §13.1-§13.2 | ✅ landed | `feat(as): land U-AS-28` | 2026-05-16 |
| U-AS-07 | `ToolContract` schema + `RawContractInput` + `SecretAllowlistEntry` carrier + registration validator | C-AS-03 §3.1-§3.3 | ✅ landed | `feat(as): land U-AS-07` | 2026-05-16 |
| U-AS-06 | `sandbox_tier_floor` 10-row 5-arg lookup + `ToolMetadata` + `MCPServer` carriers + REFUSE sentinel | C-AS-02 §2.3 | ✅ landed | `feat(as): land U-AS-06` | 2026-05-16 |
| U-AS-10 | 12-cell `DEPLOYMENT_MATRIX` + `lookup_cell` / `lookup_cell_with_forcing` | C-AS-09 §9.1,§9.3,§9.5 | ✅ landed | `feat(as): land U-AS-10` | 2026-05-16 |
| U-AS-22 | `AllowlistDecision` + `check_secret_allowlist` intersection (consumes `SecretAllowlistEntry` from U-AS-07) | C-AS-06 §6.1-§6.2 | ✅ landed | `feat(as): land U-AS-22` | 2026-05-16 |
| U-AS-24 | `SecretFailClass` 5-value taxonomy + C5/C9 metadata + per-backend breaker key | C-AS-07 §7.1-§7.3 | ✅ landed | `feat(as): land U-AS-24` | 2026-05-16 |
| U-AS-25 | Secret-fetch `outputs_hash` structure-not-content fingerprint (GUARDRAIL — C-IS-06 §6.1 scheme) | C-AS-08 §8.1 | ✅ landed | `feat(as): land U-AS-25` | 2026-05-16 |
| U-AS-29 | Engine-class composition overlay + 20-cell model-binding matrix + pre-HITL escalation | C-AS-13 §13.3-§13.4 | ✅ landed | `feat(as): land U-AS-29` | 2026-05-16 |
| U-AS-31 | Six Anthropic-primitive attribute namespaces (40 attrs) + skill-version dual-field enforcement | C-AS-14 §14.1-§14.7 | ✅ landed | `feat(as): land U-AS-31` | 2026-05-16 |
| U-AS-08 | `sandbox_tier` 5-floor max() composition + `CallSiteContext` + `AssignedTierReason` | C-AS-02 §2.1-§2.2,§2.5 | ✅ landed | `feat(as): land U-AS-08` | 2026-05-16 |
| U-AS-09 | `sub_agent_sandbox_tier` monotonic ascension + downgrade detector | C-AS-11 §11.1-§11.5 | ✅ landed | `feat(as): land U-AS-09` | 2026-05-16 |
| U-AS-13 | Per-MCP-transport sandbox-tier floor lookup + `rejects_at_registration` | C-AS-10 §10.1-§10.3 | ✅ landed | `feat(as): land U-AS-13` | 2026-05-16 |
| U-AS-14 | 5-axis gate-level multiplicative composition + `GateLevel` + `tier_to_gate_level_floor` | C-AS-12 §12.1,§12.5 | ✅ landed | `feat(as): land U-AS-14` | 2026-05-16 |
| U-AS-15 | Cross-deployment sandbox-tier monotonicity + bridging-arc raise + governance-violation detector | C-AS-12 §12.4, C-AS-11 §11.4 | ✅ landed | `feat(as): land U-AS-15` | 2026-05-16 |
| U-AS-26 | Secret-fetch audit-ledger entry composition (cross-axis IS: U-IS-07/09/10) | C-AS-08 §8.2-§8.3 | ✅ landed | `feat(as): land U-AS-26` | 2026-05-16 |
| U-AS-30 | Anthropic-API graceful degradation policy + workload-binding-decision composition | C-AS-13 §13.5-§13.6 | ✅ landed | `feat(as): land U-AS-30` | 2026-05-16 |
| U-AS-16 | Seven `sandbox.*` attribute names + `sandbox.tech` ↔ `sandbox.provider` join | C-AS-15 §15.2-§15.3,§15.7 | ✅ landed | `feat(as): land U-AS-16` | 2026-05-16 |
| U-AS-17 | Sandbox span hierarchy + 5 span event kinds + sensitive-data exclusions (GUARDRAIL) | C-AS-15 §15.1,§15.5 | ✅ landed | `feat(as): land U-AS-17` | 2026-05-16 |
| U-AS-18 | Sandbox-event sampling discipline + audit-floor commitments (GUARDRAIL) | C-AS-15 §15.4 | ✅ landed | `feat(as): land U-AS-18` | 2026-05-16 |
| U-AS-19 | Cross-axis idempotency-key composition + cost-attribution join (cross-axis IS: U-IS-07/12) | C-AS-15 §15.6 | ✅ landed | `feat(as): land U-AS-19` | 2026-05-16 |
| U-AS-21 | Negative-observation invariant enforcement (secrets absent from prompts/logs/ledger) | C-AS-05 §5.3 | ✅ landed | `feat(as): land U-AS-21` | 2026-05-16 |
| U-AS-23 | Secret-passthrough constraint enforcement (output/input redaction + MCP prohibition) | C-AS-06 §6.3 | ✅ landed | `feat(as): land U-AS-23` | 2026-05-16 |
| U-AS-27 | Per-fetch secret-audit emission discipline + span emission (cross-axis IS: U-IS-11) | C-AS-08 §8.4-§8.5 | ✅ landed | `feat(as): land U-AS-27` | 2026-05-16 |
| U-AS-32 | Anthropic-primitive sampling discipline + audit-floor commitments + D6 alignment | C-AS-14 §14.8-§14.9 | ✅ landed | `feat(as): land U-AS-32` | 2026-05-16 |
| U-AS-33 | AS-axis substrate seam exports manifest (terminal exporter — 7 seams) | C-AS-16 §16.1-§16.7 | ✅ landed | `feat(as): land U-AS-33` | 2026-05-16 |
| U-CP-41 | Both-by-tier overlay + two-agent-observer meta-class + persona-tier-binding selection (`ToolTier`, `VerifierVerdict`/`OverlayOutcome` enums, `VerifierResult`/`OverlayResolution` records, `BothByTierOverlay`/`TwoAgentObserverMetaClass` + consts, persona-tier-binding input/result, `evaluate_both_by_tier_overlay`/`dispatch_two_agent_observer`/`compose_persona_tier_binding_selection`) — v2.9-revised body; `ToolTier` declared (C-CP-18 §18.3 per-tool tier, distinct from `GateLevel`); `Cell` typed `HITLMatrixCell` | C-CP-18 §18.3-§18.5 | ✅ landed | `feat(cp): land U-CP-41` | 2026-05-16 |
| U-CP-39 | HITL-as-tool-call rewriting algorithm + 3 semantic variants (`HITLSemanticVariant` 3-enum, `EngineBindingClass`, `HITL_SEMANTIC_VARIANTS` 3-entry, `RewrittenToolCall`, `select_variant`, `rewrite_tool_call_to_hitl`) — `ToolName`/`MCPServerID` typed `str` (AS-owned, no NewType landed); `rewrite_tool_call_to_hitl` takes a 7th `hitl_required: bool` param (Class 3 — plan v2.1 6-param signature carries no `GateLevelInput` to call U-CP-43's predicate; verdict injected by the caller) | C-CP-17 §17.2 | ✅ landed | `feat(cp): land U-CP-39` | 2026-05-16 |
| U-CP-27 | Sub-agent gate-level monotonic descent + override audit (`SubAgentGateLevelDescent`, `GateOverride` opaque alias, `dispatch_sub_agent`, `assert_monotonic_descent`/`ascent`, `emit_sub_agent_dispatch_audit` → `CPAuditLedgerEntry`) — `GateOverride` opaque per §12.5 authoring-schema deferral (RoleRoutingBinding precedent); `EngineClassPreferences` NOT homed here (not in v2.1/v2.9 U-CP-27 body — U-CP-17 tension carry stays open) | C-CP-12 §12.2-§12.5 | ✅ landed | `feat(cp): land U-CP-27` | 2026-05-16 |
| U-CP-03 | Thin routing core surface (`InferenceRequest` 6-field envelope, `InferenceResponse`, `infer` entry-point) — `infer` is the ADD §5.3.3 probabilistic core; orchestration body delegates to U-CP-05 + AS-plan SDK boundary | C-CP-01 §1.1 | ✅ landed | `feat(cp): land U-CP-03` | 2026-05-16 |
| U-CP-02 | `ProviderCapabilities` reflection contract (10-field record + `ProviderCapability` enum) | C-CP-01 §1.2 | ✅ landed | `feat(cp): land U-CP-02` | 2026-05-16 |
| U-CP-01 | `routing.*` namespace + 4-attribute schema (`RoutingAttributeSchema`, `ROUTING_NAMESPACE_SCHEMA`) | C-CP-01 §1.4 | ✅ landed | `feat(cp): land U-CP-01` | 2026-05-16 |
| U-CP-21 | `engine.*` namespace + 4-attribute schema (`EngineAttributeSchema`, `ENGINE_NAMESPACE_SCHEMA`, `ReplayDisposition`, `REPLAY_DISPOSITION_MAPPING`) | C-CP-09 §9.1 | ✅ landed | `feat(cp): land U-CP-21` | 2026-05-16 |
| U-CP-26 | Sub-agent default-downgrade rule (`SubAgentDefaultDowngrade`, `DEFAULT_DOWNGRADE_RULE`, `compute_child_blast_radius_ceiling`) — cross-axis AS: U-AS-01 | C-CP-12 §12.1 | ✅ landed | `feat(cp): land U-CP-26` | 2026-05-16 |
| U-CP-37 | 4-response HITL palette (`HITLResponse`, `HITL_RESPONSE_SEMANTICS`, `PER_RESPONSE_AUDIT_ENTRY_SHAPES`, `PALETTE_INVARIANTS`, `HITL_RESPONSE_CLASS_ATTRIBUTE`) | C-CP-16 §16.1-§16.4 | ✅ landed | `feat(cp): land U-CP-37` | 2026-05-16 |
| U-CP-28 | `SubAgentBrief` schema (`SubAgentBrief`, `OutputSchema`, `OutputSchemaKind`, `ClearTaskBoundaries`, `canonicalize_brief`, `compute_brief_summary_hash`) | C-CP-13 §13.2 | ✅ landed | `feat(cp): land U-CP-28` | 2026-05-16 |
| U-CP-10 | Lifecycle-event span-name map + `ParentRelation` enum (`LifecycleEventClassMetadata`, `LIFECYCLE_EVENT_CLASS_METADATA`) — cross-axis core: U-CORE-01 | C-CP-05 §5.1 | ✅ landed | `feat(cp): land U-CP-10` | 2026-05-16 |
| U-CP-07 | `fallback.*`/`harness.breaker.*`/`retry.*` namespace schemas + `RetryCause` + `RETRY_ATTEMPT_EVENT_SCHEMA` — **partial land** (acc #7 dual-emission discipline struck → Class 1) | C-CP-03 §3.5 | ⚠️ partial-landed | `feat(cp): land U-CP-07` | 2026-05-16 |
| U-CP-11 | `lease.*` namespace + 5-attribute schema (`LeaseAttributeSchema`, `LEASE_NAMESPACE_SCHEMA` 5-entry, `LeaseMechanism` 6-value, `LeaseReleaseCause` 4-value) — **v2.8-conformed body** (prior SKIP resolved: §2.2 conforms to spec C-CP-05 §5.3; invented `LeaseEventKind` struck) | C-CP-05 §5.3 | ✅ landed | `feat(cp): land U-CP-11` | 2026-05-16 |
| U-CP-06 | `LayerBudget` data type + `RoutingLayer` carrier (`LayerBudget`, `DEFAULT_LAYER_BUDGETS`, `effective_budget`, `RoutingLayer`) — **partial land** (acc #4 span-emission struck → halt-route-split-AC); `RoutingLayer` carrier-homed here per U-CP-05↔U-CP-06 cycle | C-CP-03 §3.1 | ⚠️ partial-landed | `feat(cp): land U-CP-06` | 2026-05-16 |
| U-CP-08 | Deterministic fall-through procedure — **SKIPPED** (Class 1: plan invents 4-value `FallThroughCause` enum; cited spec C-CP-03 §3.2 commits no enum — X-AL-3 silent design extension) | C-CP-03 §3.2, §3.3 | 🛑 skipped | — | 2026-05-16 |
| U-CP-16 | Per-deployment-surface engine-class candidate mapping (`EngineClassCandidate`, `ENGINE_CLASS_CANDIDATES`) — `DeploymentSurface` imported from harness-core (U-CORE-01 carrier) | C-CP-07 §7.2 | ✅ landed | `feat(cp): land U-CP-16` | 2026-05-16 |
| U-CP-23 | Per-workload-class topology commitment table (`PerWorkloadClassTopologyCommitment`, `PER_WORKLOAD_CLASS_TOPOLOGY`) — v2.4 body; carried Class-2: `software-engineering` single-vs-dual `default_pattern` mismatch (non-blocking, fork-queue item 4) | C-CP-11 §11.1 | ✅ landed | `feat(cp): land U-CP-23` | 2026-05-16 |
| U-CP-38 | 3-placement enum + `hitl_gate` signature + `HITLPlacement` schema — **SKIPPED** (Class 1: dep U-CP-30 `HandoffContext` not landed; Pattern D undeclared `ProposedAction`/`ToolName`/`SHA256`) | C-CP-17 §17.1, §17.1.1, §17.3 | 🛑 skipped | — | 2026-05-16 |
| U-CP-38 | 3-placement HITL enum + `hitl_gate` interface signature + `HITLPlacement` schema (`HITLPlacementKind` 3-value, `HITLPlacementTrigger`, `HITL_PLACEMENT_TRIGGERS`, `HITLResult` 6-field, `hitl_gate`, `HITLPlacement` 4-field) — **LANDED** (prior skip stale: U-CP-30 landed against v2.9; `ProposedAction`/`HandoffContext` resolved; `hitl_gate` body is a `NotImplementedError` interface stub per §17.1.1; `ToolName`→`str`, `Duration`→`int` per U-CP-04 precedent) | C-CP-17 §17.1, §17.1.1, §17.3 | ✅ landed | `feat(cp): land U-CP-38` | 2026-05-16 |
| U-CP-47 | 5-class validator-fail taxonomy + `validator.fail.*` namespace (`ValidatorFailClass`, `ValidatorFailMetadata`, `VALIDATOR_FAIL_METADATA`, `ValidatorFailAttributeSchema`, `VALIDATOR_FAIL_NAMESPACE_SCHEMA`, `validator_fail_permanence`) — v2.4 §4A-conformed body; carrier (`AttributeValueType`/`Cardinality`) from harness-core | C-CP-21 §21.1, §21.5 | ✅ landed | `feat(cp): land U-CP-47` | 2026-05-16 |
| U-CP-17 | Workload-binding engine-class selection (`WorkloadBindingSelectionInput`, `WorkloadBindingSelectionResult`, `select_engine_class`, `WorkloadBindingError`) — **PARTIAL**: §7.3 5-step procedure landed as 4 steps; step 4 (`operator_preferences`) + 1 test struck — `EngineClassPreferences` homed at blocked U-CP-27 | C-CP-07 §7.3 | ⚠️ partial-landed | `feat(cp): land U-CP-17` | 2026-05-16 |
| U-CP-31 | `topology.*` + `subagent.*` span attribute namespace schemas (`TopologyAttributeSchema`, `TOPOLOGY_NAMESPACE_SCHEMA` 10-attr, `SubAgentAttributeSchema`, `SUBAGENT_NAMESPACE_SCHEMA` 7-attr, `SubAgentResultStatus` 3-value) — pure declaration unit; carrier from harness-core re-export | C-CP-14 §14.2 | ✅ landed | `feat(cp): land U-CP-31` | 2026-05-16 |
| U-CP-18 | F2 substrate join discipline (`F2JoinKind` 3-value, `EngineF2JoinContract`, `ENGINE_F2_JOIN_CONTRACTS` 5-entry, `f2_join_contract`) — R-CP-07-satisfying contract; IS read/write/chain/idempotency as string delegation pointers to U-IS-07/09/12 | C-CP-08 §8.2 | ✅ landed | `feat(cp): land U-CP-18` | 2026-05-16 |
| U-CP-40 | Persona-tier × engine-class HITL matrix (`SynchronyClass` 4-value, `HITLPrimitiveShape` 12-value, `HITLMatrixCell`, `HITL_MATRIX` 15-entry, `matrix_cell_for`) — v2.6 decl-site conversion: `PersonaTier` from harness-core; 2 cells EXCLUDED inheriting C-CP-07 §7.2 | C-CP-18 §18.1+§18.2 | ✅ landed | `feat(cp): land U-CP-40` | 2026-05-16 |
| U-CP-48 | Transient staircase + cause-attribution branching + palette restriction (`StaircaseStage` 5-value, `StaircaseTransition`, `TRANSIENT_STAIRCASE_TRANSITIONS`, `CrossTrustBoundaryState` 4-value, `PaletteRestriction`, `PALETTE_RESTRICTION_TABLE` 4-entry, `advance_staircase`, `compute_restricted_palette`) — v2.4-conformed body | C-CP-21 §21.2+§21.3 | ✅ landed | `feat(cp): land U-CP-48` | 2026-05-16 |
| U-CP-42 | Per-persona-tier audit-ledger cryptographic shape table (`CryptographicShape` 3-value, `PersonaTierCryptographicShape`, `PERSONA_TIER_CRYPTOGRAPHIC_SHAPES` 3-entry, `cryptographic_shape_for`, `shape_strength`) | C-CP-20 §20.1+§20.2 | ✅ landed | `feat(cp): land U-CP-42` | 2026-05-16 |
| U-CP-04 | Routing manifest residence (`RetryPolicy` 3-field, `RoutingManifest` 5-field, `RoutingManifestValidationError`, `validate_routing_manifest`, `resolve_manifest_residence_path`, `load_routing_manifest`) — **partial-land** (v2.9 §0.5: `RetryPolicy` factor-out specified; `RoleRoutingBinding`/`WorkloadRoutingOverride` value-types opaque Class 1 carry → `.harness/class_1_tension_role_routing_binding_underspec.md`). Class 3: `retry_policies` keyed by `str` — AS `ToolName` NewType not landed. | C-CP-01 §1.3 + C-CP-03 §3.5 | ⚠️ partial-landed | `feat(cp): land U-CP-04` | 2026-05-16 |
| U-CP-05 | Layered routing strategy (`InferenceRequest` = U-CP-00c `ProviderAgnosticPayload` per v2.9 §0.1, `LAYER_ORDER`, `LayerDecisionFn`, `layer_budget_for`, `route`) — imports `RoutingLayer` (U-CP-06 carrier-home) + `RoutingDecisionTrace` (U-CP-00c); DECLARATIVE→EMBEDDING→LLM_AS_ROUTER fall-through | C-CP-02 §2.1+§2.2 | ✅ landed | `feat(cp): land U-CP-05` | 2026-05-16 |
| U-CP-08 | Deterministic fall-through (v2.8-conformed `FallThroughCause`) — **SKIPPED** (Class 1: dep U-CP-05 blocked; body itself materializable) | C-CP-03 §3.5 | 🛑 skipped | — | 2026-05-16 |
| U-CP-08 | Deterministic fall-through procedure (`FallThroughCause` 4-value byte-exact §3.5, `FallThroughResult`, `fall_through`) — **LANDED** (prior skip stale: dep U-CP-05 now landed; v2.8-conformed body materializable) | C-CP-03 §3.5 | ✅ landed | `feat(cp): land U-CP-08` | 2026-05-16 |
| U-CP-09 | Cross-family fallback chain (`ProviderFamily` 4-value, `ProviderCandidate`, `FallbackChain` 4-field, `OnFailureResult`, `compose_fallback_chain`, `on_provider_failure`) — §4.2 same→cross→terminal ordering; §4.3 cross-family attribution flags | C-CP-04 §4.1-§4.3 | ✅ landed | `feat(cp): land U-CP-09` | 2026-05-16 |
| U-CP-13 | `WorkflowManifestEntry` schema — **SKIPPED** (Class 1: `HITLPlacement` from blocked U-CP-38; deps U-CP-04/09/30/38 blocked) | C-CP-06 §6.1 | 🛑 skipped | — | 2026-05-16 |
| U-CP-13 | `WorkflowManifestEntry` 10-field schema + `StepOverride` — **LANDED** (prior skip stale: deps U-CP-04/09/30/38 all landed; `WorkloadClass`/`PersonaTier`/`StepID` from harness-core, `ModelBinding` from U-CP-00c) | C-CP-06 §6.1 | ✅ landed | `feat(cp): land U-CP-13` | 2026-05-16 |
| U-CP-14 | Per-step override evaluator — **SKIPPED** (Class 1: dep U-CP-13 blocked; `LedgerEntryRef` from blocked U-CP-30) | C-CP-06 §6.2 | 🛑 skipped | — | 2026-05-16 |
| U-CP-14 | Per-step override evaluator + CP audit-ledger entries (`CPAuditLedgerEntry` 8-field, `CPSignedAuditLedgerEntry` 5-sig-field, `StepEffectiveBinding`, `resolve_step_binding`, `emit_override_audit_entry`) — **LANDED** (v2.9 factor-out: CP audit types named CP-distinct per §0.5.1 name-collision resolution vs OD `AuditLedgerEntry`; deps U-CP-13/15 landed, `GateLevel` from harness-as) | C-CP-06 §6.2 + C-CP-16 §16.2 + C-CP-20 §20.1/§20.4 | ✅ landed | `feat(cp): land U-CP-14` | 2026-05-16 |
| U-CP-30 | `HandoffContext` family (`ActionKind` 3-value, `ActionPayload` opaque alias, `ProposedAction`, `FailedAttempt`, `Alternative`, `RetryHistory`, `LedgerEntryRef`, `ExternalReference`, `ReferenceClass` 4-value, `StateSummary`, `HandoffContext` 7-field) — v2.9 factor-out delta; Pattern-D tail types specified | C-CP-13 §13.1+§13.4+§13.5 | ✅ landed | `feat(cp): land U-CP-30` | 2026-05-16 |
| U-CP-33 | Concurrent-prompt-cache warm-up — **SKIPPED** (dep-block, not type-block: `LeadAgentPlan` type-side now resolved by v2.9 §0.5.2 opaque alias, but `Depends on: [U-CP-32, …]` stands — U-CP-32 unlanded, out of L1-L3 scope. Clears transitively when U-CP-32 lands per v2.9 §0.5.2) | C-CP-14 §14.4 | 🛑 skipped | — | 2026-05-16 |
| U-CP-39 | HITL-as-tool-call rewriting — **SKIPPED** (dep-block, not type-block: `ProposedAction`/U-CP-38 now landed, but `Depends on: [U-CP-37, U-CP-38, U-CP-43, U-CP-48]` — U-CP-43 unlanded, L4-L8 next batch. Lands after U-CP-43) | C-CP-17 §17.2 | 🛑 skipped | — | 2026-05-16 |
| U-CP-44 | F5 signing-key resolution — **SKIPPED** (Class 1: Pattern-D undeclared `AuditLedgerEntry`/`SignedAuditLedgerEntry`; `SecretRef` from forked U-AS-20) | C-CP-20 §20.3.1 | 🛑 skipped | — | 2026-05-16 |
| U-CP-44 | F5 signing-key resolution (`SecretScopeKind` 3-value, `KeyRotationState` 3-value, `SigningKeyResolutionError`, `SigningKeyScope`, `SigningKeyHandle`, `SigningKeyResult`, `VerificationResult`, `resolve_signing_key`, `sign_audit_entry`, `verify_audit_entry_signature`) — **LANDED** (prior skip stale: `CPAuditLedgerEntry`/`CPSignedAuditLedgerEntry` landed at U-CP-14 per v2.9 §0.5.1; `SecretRef`/`fetch_secret` available from U-AS-20 in harness-as) | C-CP-20 §20.3.1 | ✅ landed | `feat(cp): land U-CP-44` | 2026-05-16 |
| U-CP-53 | T-perm-3 three-layer composition + per-cell reading + outer-harness boundary (`LayerOwner` 3-value + `RuntimeFault` 3-value promoted enums, `F1LayerState`/`D1LayerState`/`D4LayerState`/`TPerm3LayerComposition`, `PerCellReadingKind` 3-value, `PerCellTPerm3Reading`/`PER_CELL_T_PERM_3_READINGS` 20-cell, `DeterministicOuterHarnessBoundary`/`DETERMINISTIC_OUTER_HARNESS_BOUNDARY` 5-primitive, `compose_t_perm_3`/`read_per_cell_t_perm_3`/`handle_runtime_fault`) — acc #5 deployment-keyed cell exclusion noted as U-CP-16-owned (the §23.2 table is workload×engine) | C-CP-23 §23.1-§23.4 | ✅ landed | `feat(cp): land U-CP-53` | 2026-05-16 |
| U-CP-36 | Per-persona-tier cryptographic shape composition + trace-inspection read (`CrossSiblingCryptographicComposition`, `CROSS_SIBLING_CRYPTOGRAPHIC_COMPOSITION` 3-entry, `TraceInspectionSurface`/`CROSS_SIBLING_TRACE_INSPECTION` 3-surface, `ResolutionError`, `VerificationResult`, `compose_per_persona_tier_cryptographic_shape`, `resolve_audit_ledger_entry_from_trace`) — delegates per-tier shape to U-CP-42; acc #5 `verify_multi_tenant_compliance_signature` is a delegation-pending stub (U-CP-45 unlanded — within-axis forward ref) | C-CP-15 §15.5+§15.6 | ✅ landed | `feat(cp): land U-CP-36` | 2026-05-16 |
| U-CP-43 | 4-axis multiplicative gate-level rule (`GateLevel` 3-value `{auto,ask,deny}`, `GateLevelInput`, `GateLevelComputation`, `BLAST_RADIUS_GATE_LEVEL_FLOOR` + `PERSONA_TIER_GATE_LEVEL_FLOOR` §19.1-verbatim, `gate_level`, `hitl_required`/`_hitl_required`, `assert_cross_persona_monotonicity`) — **partial-land** (acc #5 `MCP_TRUST_GATE_LEVEL_FLOOR` + acc #6 `DEPLOYMENT_SURFACE_GATE_LEVEL_FLOOR` struck — §19.1 spec-silent; acc #2 degraded to 2-axis `max()`; `.harness/class_1_tension_u_cp_43_spec_silent_floors.md`) | C-CP-19 §19.1+§19.2+§19.4 | ⚠️ partial-landed | `feat(cp): land U-CP-43` | 2026-05-16 |
| U-CP-35 | `parent_fanout_close_entry` separate primitive + merkle-root construction (`CascadeDecisionAtFanoutClose` 3-value, `ParentFanoutCloseEntry` 6-field non-F2 primitive, `MerkleRoot`, `MerkleStepOperation`/`F2Effect`/`MerkleConstructionStep`, `MERKLE_CONSTRUCTION_STEPS` 4-entry, `construct_parent_fanout_close_entry`/`construct_sibling_ledger_root`) — read side accepts U-IS-12 `LedgerNavigationPrimitive` | C-CP-15 §15.2+§15.4 | ✅ landed | `feat(cp): land U-CP-35` | 2026-05-16 |
| U-CP-34 | Per-sibling F2 ledger entry composition + F2-14 Reading 1 rationale (`SiblingLedgerEntry` (F2-shape subclass), `F2_14_READING_1_RATIONALE` 3-entry, `construct_sibling_ledger_entry`, `append_sibling_ledger_entry`) — delegates canonicalize/hash/chain/append to U-IS-08/09/11 | C-CP-15 §15.1+§15.3 | ✅ landed | `feat(cp): land U-CP-34` | 2026-05-16 |
| U-CP-29 | Brief-authoring model-binding inheritance table (`InheritanceRule` 2-value, `BriefAuthoringInheritance`, `BRIEF_AUTHORING_INHERITANCE` 4-entry, `inheritance_for`) — **partial-land** (acc #3 `resolve_brief_authoring_model_binding` struck → cross-axis ModelBinding seam, routed to 7c; `.harness/class_1_tension_u_cp_29_cross_axis_modelbinding_seam.md`) | C-CP-13 §13.3 | ⚠️ partial-landed | `feat(cp): land U-CP-29` | 2026-05-16 |
| U-CP-25 | Workload-class x engine-class 2D matrix + D4 multiplicative tunable (`WorkloadEngineMatrixCell`, `WORKLOAD_ENGINE_MATRIX` 20-cell, `D4MultiplicativeTunable`, `lookup_cell`, `d4_tunable`) | C-CP-11 §11.3+§11.4 | ✅ landed | `feat(cp): land U-CP-25` | 2026-05-16 |
| U-CP-24 | Per-engine-class topology overlay + T-perm-3 reading (`TopologyFaultHandling` 3-value, `CascadeEnforcementMechanism` 3-value, `WriterSerializationMechanism` 3-value, `PER_ENGINE_CLASS_OVERLAYS` 5-entry, `overlay_for`) | C-CP-11 §11.2 | ✅ landed | `feat(cp): land U-CP-24` | 2026-05-16 |
| U-CP-20 | Per-resumption observable behavior catalog (`PER_RESUMPTION_OBSERVABLE_BEHAVIOR` 5-entry, `ContinuityGuarantee` 5-value, `F2_12_CARRY_FORWARD_CLOSED`) — v2.2 amendment body; F2-12 carry-forward CLOSED | C-CP-08 §8.3 | ✅ landed | `feat(cp): land U-CP-20` | 2026-05-16 |
| U-CP-12 | Per-class attribute composition + sampling discipline (`PER_CLASS_ATTRIBUTE_SETS` 8, `SAMPLING_DISPOSITIONS` 8, `RETRY_SURFACE_SAMPLING_DISPOSITIONS` 2, `DUAL_EMISSION_DISCIPLINE`, `required_attributes_for`) — v2.4 amendment body; sampling conformed to §5.4 per-row table | C-CP-05 §5.2+§5.4 | ✅ landed | `feat(cp): land U-CP-12` | 2026-05-16 |
| U-CP-00c | 9 CP-owned structured shared types (`ActorIdentity`/`AgentRole` newtypes, `ModelBinding`/`ProviderAgnosticPayload`/`RoutingDecisionTrace`/`TraceContext` records, `MCPTrustTier`/`Axis` enums, `TailKeepPredicate` alias) — v2.8 §2.0c carrier; acc #10 full 15-consumer composition deferred (`.harness/class_1_tension_u_cp_00c_acc10_deferred.md`) | v2.8 §2.0c (aggregate) | ⚠️ partial-landed | `feat(cp): land U-CP-00c` | 2026-05-16 |

**IS axis stream COMPLETE — 17/17 units landed 2026-05-16.** U-IS-17 is the terminal aggregate exporter.

**CP axis stream — NOT COMPLETE. 44/57 units landed (2026-05-16).** Final-batch
landed 4 of 9 brief units: U-CP-35, U-CP-43 (partial), U-CP-36, U-CP-53.
5 brief units BLOCKED on unlanded dependency units (U-CP-46/32/33/50/55); a
further 8 CP units (U-CP-03/27/39/41/45/49/51/52/54) were never in any batch.
14 CP units remain unlanded — see `.harness/class_1_tension_cp_scope_discrepancy.md`
for the residual list + dependency-unblock order. The "9 = final batch" brief
under-counted the residual.

## Operational-minimum set (7a exit-criterion #1 — 12 units)

U-IS-01 ✅ · U-IS-02 ✅ · U-IS-03 ✅ · U-IS-04 ✅ · U-AS-01 ✅ · U-AS-02 ✅ ·
U-AS-03 ✅ · U-AS-04 ✅ · U-CP-15 ✅ · U-CP-22 ✅ · U-OD-01 ✅ · U-OD-04 ✅

**✅ 12 of 12 operational-minimum units landed (2026-05-15).** 7a exit-criterion
#1 met. Final two: U-OD-04 (against conformed OD plan v2.5) and U-CP-22 (against
CP plan v2.5 — after Tension 002 vocabulary conformance + Tension 003 resolution).
Tension 003 resolved by adding foundational unit **U-CP-00** (`WorkloadClass` in
`harness-core`), landed as the unblocking dependency. Operator authorized
land-now without v2.4/v2.5 pre-implementation re-clearance.

## Spec tensions

| Record | Tension | Status |
|---|---|---|
| `Phase_7_Class_3_Tension_001_Git_Tier_Sub_Role_Count.md` | C-IS-03 §3 "four" vs 5 rows | ✅ resolved — spec fixed in-CLI; block cleared |
| `Phase_7_Class_1_Tension_002_Topology_Pattern_Enum.md` | TopologyPattern enum 3-way divergence | ✅ resolved 2026-05-15 — operator signed off Set 2 (spec C-CP-10 §10.1); CP-AL-1 conformed at 4 loci; commit `45f104f` |
| `class_1_tension_u_core_01_workflow_event.md` | U-CORE-01 `WorkflowEvent` payload model unmaterializable as a `harness-core` carrier type | ✅ resolved 2026-05-15 — operator ruled carrier-thin; payload model struck; harness-core plan v1.0→v1.1; U-CORE-01 landed without it |
| `class_1_tension_u_as_31_attribute_schema_enums.md` | U-AS-31 consumes `AttributeValueType`/`Cardinality` homed in `harness-cp`; AS→CP package edge would cycle against the 24 CP→AS edges | ✅ resolved 2026-05-16 — operator ruled re-home; enums moved to `harness-core`, `harness-cp` re-exports, carrier map line 100 updated; U-AS-31 landed |
| `class_1_tension_u_od_00_carrier_defects.md` | U-OD-00 §3.0 three carrier defects — SignatureAlgorithm cycle (D-1), missing CellID edge / false L0 (D-2), AuditSignatureAttributes un-spec'd field (D-3) | ✅ resolved 2026-05-15 — operator ruled micro-revise; OD plan v2.6→v2.7; U-OD-00 landed against v2.7 |
| `class_1_tension_u_cp_00b_structured_types.md` | U-CP-00b bundled 9 structured shared types declared name-only (no shapes at plan grade) | ⚠️ resolved-split 2026-05-15 — operator ruled split; CP plan v2.6→v2.7; U-CP-00b landed as the 2-enum carrier. **OPEN:** the 9 structured types await a future CP plan revision specifying each shape |
| `Phase_7_Class_1_Tension_003_WorkloadClass_Undeclared.md` | `WorkloadClass` type used by ~10 CP units, declared by none | 🛑 OPEN 2026-05-15 — U-CP-22 halted; plan-gap (missing declaring unit) |
| `Phase_7_Class_1_Tension_004_OD04_Span_Schema_Divergence.md` | U-OD-04 plan signature diverges from spec C-OD-04 at 4 points | 🛑 OPEN 2026-05-15 — U-OD-04 halted; subsumed into the OD-plan systemic audit below |
| `class_1_tension_u_cp_07_dual_emission.md` | U-CP-07 acc #7 bundles a runtime dual-emission discipline (OTel span emitter) into an L0 schema-declaration unit — no emitter exists at 7b L0 | ⚠️ resolved-split 2026-05-16 — halt-route-split-AC; U-CP-07 partial-landed (schemas, acc #1–#6); acc #7 + 5 emission tests struck, routed to a downstream emitter unit. **OPEN:** CP plan revision must re-home acc #7 |
| `class_1_tension_u_cp_11_lease_namespace_schema.md` | U-CP-11 plan acc #1 names a 5-tuple `LEASE_NAMESPACE_SCHEMA` that contradicts the cited spec C-CP-05 §5.3 attribute table (only `lease.holder` overlaps) | 🛑 OPEN 2026-05-16 — U-CP-11 halted; SKIPPED; spec-vs-plan 5-tuple contradiction; CP plan or spec revision required |
| `class_1_tension_u_cp_17_engine_class_preferences_homing.md` | U-CP-17 `operator_preferences: Optional<EngineClassPreferences>` consumes a record homed at blocked U-CP-27 — hidden dep not in the `Depends on:` line | ⚠️ resolved-split 2026-05-16 — halt-route-split-AC; U-CP-17 partial-landed (§7.3 4 of 5 steps); `operator_preferences` field + step 4 + 1 test struck. **OPEN:** re-land step 4 at U-CP-27 landing; CP plan revision to re-home `EngineClassPreferences` or forward-defer |

## Systemic finding — Phase-6 plan "verbatim"-claim divergence (2026-05-15)

Plan-wide adversarial audit (`harness-adversarial-reviewer` Phase-7 mode) found
the Tension-002/004 shape — plan units claiming "per §X verbatim" against
signatures that diverge from the cited spec — is **systemic across the CP + OD
plans**. The two audit reports are the canonical systemic-tension records
(supersede the per-unit Tension 002/004 framing; no further per-unit records filed).

| Audit report | Divergent units | Resolution |
|---|---|---|
| `.harness/verbatim_audit_cp_plan.md` | 7: U-CP-01, U-CP-10, U-CP-19, U-CP-22, U-CP-43, U-CP-46, U-CP-47 (+ borderline U-CP-11) | one CP-plan revision-pass — conform to spec |
| `.harness/verbatim_audit_od_plan.md` | 10: U-OD-02, U-OD-04, U-OD-09, U-OD-11, U-OD-12, U-OD-14, U-OD-28, U-OD-30, U-OD-32, U-OD-33 | one OD-plan revision-pass — conform to spec |
| `.harness/adversarial_review_phase7_cp_od_preimpl.md` | U-CP-22 + U-OD-04 pre-impl review (F3-01, F1-02 CLAUDE.md §2.2 mislabel) | feeds the two passes above |

**17 units total**, all §4.1 Class 3 / §2.7.6 Class 1. All authority-chain-
determinate (spec canonical per CLAUDE.md §1.3 — conform the plan) **except**
Tension 003 (`WorkloadClass` residence — genuinely non-determinate, needs operator).
Meta-finding: the Phase-6 plans were P6-CK-cleared yet carry 17 plan-vs-spec
divergences → P6-CK process gap (verbatim-claim check was not run at checkpoint).
Filed: `.harness/finding_p6ck_verbatim_check_gap.md`.

## §4A conformance — systems-architect recommendations + implementation-planner revision-pass (2026-05-15)

- `systems-architect` §4A: two per-axis resolution recommendations appended to
  the audit reports (conform plan to spec — authority-chain-determinate).
  **Operator-accepted.**
- `implementation-planner` revision-pass: **CP v2.4** + **OD v2.5** authored
  (commit after `3209254`). Determinate cluster conformed — 7 CP units + 3
  consumers, 9 OD units. U-CP-22 + U-OD-04 cleanly conformed (verified vs spec).
- **New findings surfaced during conformance** (not in the original audit;
  carried, not absorbed): U-CP-43 input-set divergence + `MCP_TRUST` under-spec
  (extends carry list to 4); U-CP-46 coverage shrink (plan-invented `audit.gate.*`
  dissolved — orphans `composition_winner`); U-CP-23 pre-existing structural
  mismatch; OD compound-spec-row rendering judgment call.
- **Owed:** pre-implementation re-clearance of v2.4/v2.5 before U-CP-22 + U-OD-04
  land; disposition of the new findings + the 5 original flagged items
  (U-CP-08, U-CP-11, U-OD-09 acc#2, U-OD-28, U-OD-29).

## §5 AS axis-stream — Cluster L1 close (2026-05-16)

AS Level-1 cluster complete — U-AS-07, U-AS-12, U-AS-20, U-AS-28 landed; the
AS plan's entire L0+L1 is now covered (10/33 AS units). 5-dimension coherence
pass clean (atomicity / spec-traceability / dependency-awareness / impl-grade
detail / anti-pattern audit). 70/70 harness-as tests green; ruff + pyright
clean. state.jsonl hash-chain length 36.

**Class 3 informational observations (non-blocking, not filed as records):**
- **U-AS-12 plan dependency-declaration gap.** Plan `Depends on [U-AS-04]`
  omits `[U-AS-01]`, yet `BlastRadiusTier` (carried by U-AS-01) is the second
  component of the `proposed_cell` tuple input. U-AS-01 is an L0 unit
  transitively in-cone of every AS unit; the edge is trivially satisfied.
  Documented in the `operator_policy_override_scope.py` docstring.
- **U-AS-28 surface-conditioned-cell materialization discretion.** §13.2 has 8
  surface-conditioned cells (Managed Agents + Files API rows) whose adoption
  depth varies by deployment surface; `AdoptionDepthBinding` carries one
  `depth`. Materialized as `depth` = managed-cloud reference-surface value,
  `notes` = verbatim §13.2 cell text, `surface_qualifier` = divergent surface.
  Full §13.2 content preserved in `notes`. Uses the binding's provided
  `notes` / `surface_qualifier` fields as intended — not a fork.
- **AS→IS package edge.** `harness-is` added to `harness-as` pyproject deps —
  first AS→IS package dependency (materializes the U-AS-28 plan-declared
  cross-axis IS edges; read-only consumption of the IS SKILLS path contract).

**Spec divergence checked + cleared:** AS plan v1.2 §0.6 action items A-1
(U-AS-04 re-point to harness-core) and A-5 (C-AS-05 §5.1 3-param `fetch_secret`
spec revision) are both already discharged — A-1 in the landed
`discriminators.py`, A-5 in AS spec v1.3 §5.1. The plan's stale caveats do not
block; no tension.

## §6 AS axis-stream — Cluster L2 close (2026-05-16)

AS Level-2 cluster — **all 7 landed**: U-AS-06, U-AS-10, U-AS-22, U-AS-24,
U-AS-25, U-AS-29, U-AS-31. **AS now 17/33; AS L0+L1+L2 complete.** 148/148
harness-as tests green; ruff + pyright clean. state.jsonl hash-chain length 43.

**U-AS-31 Class 1 fork — RESOLVED** (`class_1_tension_u_as_31_attribute_schema_enums.md`).
U-AS-31's `AttributeSchema` consumes `AttributeValueType` / `Cardinality`, which
U-CP-00b landed in `harness-cp` (operator decision D3, premise "no cross-axis
sharing"). An AS→CP package edge would cycle against the 24 declared CP→AS
edges (CXA §2.3.4). Operator ruled re-home 2026-05-16: the two enums moved to
`harness-core` (`schema_attribute_enums.py`), `harness-cp` re-exports them for
CP-citation stability, the landed U-CP-00b test was re-pointed, carrier map
line 100 updated (carrier = core; consumers = CP + AS). 4th carrier-home fork
after U-CORE-01 / U-OD-00 / U-CP-00b.

## §7 AS axis-stream — COMPLETE (2026-05-16)

**All 33 AS units landed.** AS Levels 0-8 complete (L3 = U-AS-08/09/13/14/15/26/30;
L4 = U-AS-16; L5-L8 = U-AS-17/18/19/21/23/27/32/33). U-AS-33 is the terminal
aggregate exporter. 299/299 harness-as tests green; ruff + pyright clean.
state.jsonl hash-chain length 59 (43 units across IS/AS/CP/OD + harness-core).

**Class 3 observations (L3-L8, non-blocking — documented implementation discretion):**
- **U-AS-08** — four v1-body / v1.2-propagation gaps resolved: `mcp_trust_level`
  field dropped (completes the G-1 reconciliation); `blast_radius_floor(taint_state)`
  → `blast_radius_floor(blast_radius_tier)` (U-AS-05 landed §2.4); `TaintState`
  minimal 2-pole enum (§2 deferral); `tool_metadata` param threaded.
- **U-AS-14** — `tier_to_gate_level_floor` SandboxTier→GateLevel mapping is not
  spec-given; monotone mapping chosen (tier-1/2→AUTO, tier-3→ASK, tier-4→DENY).
- **U-AS-15** — `bridging_arc_effective_tier_raise` takes the `persona_tier_floor`
  as an injected interface (CP session-3 deferred per §12.5).
- **U-AS-16** — `emitted_on` materialized as a span-name string (SpanEventKind is
  declared downstream at U-AS-17 — carrier ordering).
- **U-AS-21 / U-AS-23** — secret-detection mechanism is spec-deferred (§5.3/§6.3:
  regex/fingerprint/taint); marker-substring detector is the unit-grade placeholder.
- **U-AS-30** — 5 Pattern B carriers minimally resolved; `memory_tool_storage_backend`
  self-hosted-server filled with the composable subset (AC5 gives only LOCAL+MANAGED).
- GUARDRAIL units U-AS-17/18 — the OTel SpanProcessor / Sampler wiring is
  project-authored downstream; the units declare the policy + predicates.

**Class 3 observations (L2, non-blocking):**
- **U-AS-10 surface-conditioned provider-class.** §9.1 labels the tier-2
  local-mutation cell "process-fs-overlay" — not a §9.2 six-class member.
  Mapped to `PROCESS_ULIMIT_BUBBLEWRAP_SEATBELT` (the §9.1 cell witnesses are
  Seatbelt/bubblewrap-dominant; self-hosted tier-2 is pure bubblewrap). Full
  §9.1 witness list preserved in `candidate_witnesses`.
- **U-AS-25 cross-axis canonicalization seam.** U-IS-08's `canonicalize` is
  `StateLedgerEntry`-typed — not a reusable cross-axis primitive. U-AS-25
  (GUARDRAIL) re-applies the C-IS-06 §6.1 scheme (NFC + sorted-key JSON, no
  whitespace) to its fingerprint triple per spec §8.1's "library binding
  deferred" framing. 7c may want to factor a shared canonicalization primitive.
- **U-AS-24 accessor rename.** Plan names the accessor `fail_class_metadata`;
  renamed to `secret_fail_class_metadata` to avoid the U-AS-03 collision.
- **U-CP-48 palette-set narrowing (spec vs plan).** CP spec C-CP-21 §21.3 says
  the cross-trust-boundary palette is "restricted to `{approve, reject,
  respond}` (no `edit`)". The U-CP-48 plan acceptance #5 (preserved at v2.4)
  narrows the three cross-trust-state table entries further to `{REJECT,
  RESPOND}`. `{reject, respond}` is a subset of the spec's edit-free set — a
  within-allowed refinement, not a verbatim divergence — so U-CP-48 landed per
  the plan table. Non-blocking; flagged for a future CP spec/plan reconcile.
- **U-CP-39 `rewrite_tool_call_to_hitl` predicate-input gap.** The plan v2.1
  signature is 6-param `(tool, server, persona_tier, proposed_action,
  cell_synchrony_class, cross_trust_boundary_state)` and AC #3 requires the
  function to "evaluate `_hitl_required` via U-CP-43". But U-CP-43's
  `hitl_required` predicate consumes a `GateLevelInput` (`persona_tier`,
  `blast_radius_tier`, `deployment_surface`, `mcp_trust_tier`) — and the
  6-param signature carries only `persona_tier`; `blast_radius_tier` /
  `mcp_trust_tier` / `deployment_surface` are not in the argument set (AC #6
  says per-tool tier is read from frontmatter "at runtime"). The function
  therefore takes a 7th `hitl_required: bool` param — the caller (which holds
  the gate context) evaluates U-CP-43 and injects the verdict. Non-blocking;
  flagged for a CP plan signature reconcile.
