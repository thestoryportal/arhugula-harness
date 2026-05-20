# Class 2 Tension — HarnessContext axis-type mapping (Phase 2 Session 5)

**Filed:** 2026-05-19 — Phase 2 Session 5, pre-U-RT-02 landing.
**Defect class:** Class 2 — in-execution operator decision. The spec named
forward-looking types that the runtime must compose itself; the library shipped
contracts/schemas/policies, not runtime composition primitives. No upstream
artifact revision required — the L0 landing of U-RT-02 declares the mapping.
**Operator decision:** Class 2 confirmed 2026-05-19. Runtime owns the
composition primitives. U-RT-02 defines them as `typing.Protocol` stubs (or
thin runtime-defined classes) in `harness_runtime.types`; L2–L6 units
narrow/concretize.

## Defect

`Spec_Harness_Runtime_v1.md` v1.1 §4 (C-RT-04 `HarnessContext` schema) names
~20 axis-typed fields. Pre-flight grep of the landed library at Session 5 open
(2026-05-19, commit `6c45383`) shows **13 of those field types do not exist as
classes in the landed axis packages**.

## Evidence

Grep `^class <Name>` across `harness-{core,is,as,cp,od}/src/` at HEAD = `6c45383`:

| Spec C-RT-04 reference | Field | Resolved? |
|---|---|---|
| `harness_is.PathResolver` | `path_resolver` | ✅ `harness-is/src/harness_is/path_resolver.py:40` |
| `harness_is.WorktreeIsolationManager` | `worktree_manager` | ✅ `harness-is/src/harness_is/worktree_isolation.py:83` |
| `harness_is.ContentAddressedIndex` | `index` | ❌ no `*Index` class in IS |
| `harness_is.SemanticCache` | `cache` | ❌ no `*Cache` class in IS |
| `harness_as.Skill` | `skills` value type | ❌ |
| `harness_as.ToolContract` | `tool_contracts` value type | ✅ `harness-as/src/harness_as/tool_contract.py:62` |
| `harness_as.MCPHost` | `mcp_host` | ❌ |
| `harness_as.MCPClient` | `mcp_clients` value type | ❌ |
| `harness_as.SandboxDispatchTable` | `sandbox_dispatch` | ❌ |
| `harness_cp.RoutingManifest` | `routing_manifest` | ✅ `harness-cp/src/harness_cp/routing_manifest_residence.py:118` |
| `harness_cp.EngineSelector` | `engine_selector` | ❌ |
| `harness_cp.FallbackChain` | `fallback_chain` | ✅ `harness-cp/src/harness_cp/cross_family_fallback_chain.py:52` |
| `harness_cp.RetryBreakerRegistry` | `retry_breaker` | ❌ |
| `harness_cp.HITLPlacementRegistry` | `hitl_registry` | ❌ |
| `harness_cp.HandoffRegistry` | `handoff_registry` | ❌ |
| `harness_cp.PerStepOverrideEvaluator` | `override_evaluator` | ❌ |
| `harness_cp.TopologyDispatcher` | `topology_dispatcher` | ❌ |
| `harness_cp.TopologyPattern` | (RuntimeConfig.default_topology) | ✅ `harness-cp/src/harness_cp/topology_pattern.py:38` |
| `harness_od.CostAttributionChain` | `cost_chain` | ❌ no class with that name in OD |
| `harness_core.identity.SkillID` `ToolName` `ClientName` | dict-key types | ❌ identity exports 9 IDs, not these three |

The 5 spec-acknowledged runtime-defined types (`ShadowGitSupervisor`,
`LedgerWriter`, `AuditLedgerWriter`, `CollectorDaemonHandle`,
`LifecycleEventEmitter`) are correctly absent from the library by spec design
— the spec explicitly tags them "runtime-defined".

## Reading and resolution

**Reading A (selected):** The library shipped *contracts* (Pydantic schemas,
StrEnums, policies, terminal exporter manifests). It did not ship *runtime
composition primitives* (the indexes/caches/registries/dispatchers that wrap
contract types into runnable wiring). That composition is what
`harness-runtime` exists to do, per F-P2-1..F-P2-5 fork resolutions. The
spec was forward-looking about the names; the names land here, in
`harness_runtime.types` or `harness_runtime.lifecycle.*`/`wiring.*` modules.

This is the same shape as the 5 explicitly-marked runtime-defined types —
extending that pattern to the 13 currently-unmarked names.

**Reading B (rejected):** Library has genuine gaps; spec amendments to IS/AS/
CP/OD plus library extensions required first. Rejected because the AS
`__init__.py` public surface (schemas, policies, validators, no runtime
composition classes) matches the F-P2-N "runtime owns lifecycle" framing
exactly. No evidence of unintentional omission; the library design is
contract-first by intent.

## Mapping decision at U-RT-02

`harness_runtime.types` defines the 13 names as `typing.Protocol` stubs (PEP
544 structural). Each stub captures the minimum method shape implied by spec
C-RT-04 field semantics + the runtime's stage-N post-condition (e.g.,
`ContentAddressedIndex.lookup(key) -> bytes | None` is enough for the L2 stage
1 post-condition to type-check). L2–L6 units that actually construct these
either (a) implement the Protocol with a concrete class in
`harness_runtime.lifecycle.*` / `harness_runtime.wiring.*`, or (b) — if the
right concrete type emerges in the axis library between now and that unit —
narrow the field type to the concrete axis type via a model revision.

The 6 axis-typed names that DO resolve (`PathResolver`,
`WorktreeIsolationManager`, `ToolContract`, `RoutingManifest`, `FallbackChain`,
`TopologyPattern`) are imported concretely with `arbitrary_types_allowed=True`
per C-RT-04 invariant.

The 3 dict-key newtype references (`SkillID`, `ToolName`, `ClientName`) are
defined in `harness_runtime.types` as `typing.NewType('SkillID', str)` etc.
until/unless `harness_core.identity` grows them. Adding them to
`harness_core.identity` is a candidate sideband fix (one-line additions per
the existing 9-ID pattern); not blocking U-RT-02.

## Downstream traceability

- **Spec §16 open questions:** carry-forward "L2–L6 narrowing or concretizing
  of Protocol stubs" as a new question #10 if it surfaces drift.
- **Plan §9 traceability:** unchanged; U-RT-02 still traces to C-RT-03 +
  C-RT-04. The Protocol-stub mapping is an implementation-discretion call
  per C-RT-04 "Deferred to implementation discretion" clause.
- **No spec revision required.** Mapping decision documented here is
  sufficient.

## Resolution status

**RESOLVED — Class 2.** U-RT-02 proceeds with Protocol stubs in
`harness_runtime.types`. This record is the audit trail. Re-open as Class 1
only if an L2–L6 unit surfaces a Protocol-vs-concrete mismatch that the
runtime cannot resolve without a library change.

---

*Filed at: `.harness/class_2_tension_phase_2_session_5_harness_context_axis_type_mapping.md`. Anchor commit: `6c45383` (plan v2.1).*
