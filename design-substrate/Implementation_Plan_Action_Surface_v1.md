# Implementation Plan — Action Surface (v1)

## Status block

| Field | Value |
|---|---|
| Artifact | `Implementation_Plan_Action_Surface_v1.md` |
| Status | **Proposed** (v1 pending P6-CK clearance per `Project_Workflow_v1_5.md` §3.1; aggregate adversarial review at Phase 6 Session 5 cross-axis composition close per `Phase_6_Entry_Handoff.md` §1.1 OD-6-4.A) |
| Date | 2026-05-14 |
| Phase | 6 — atomic implementation plan (Session 2 of 5 per `Project_Workflow_v1_5.md` §2.6) |
| Skill | `implementation-planner` SKILL.md in initial-authoring sub-mode |
| Axis | Action Surface (AS) — second-axis per `Phase_6_Entry_Handoff.md` §5.1 sequencing rationale |
| Source-set | `Spec_Action_Surface_v1.md` v1.1 §1–§16 (16 contracts: C-AS-01 through C-AS-16); `Implementation_Plan_Information_Substrate_v1.md` v1 (cross-axis substrate; U-IS-17 manifest); `Project_Workflow_v1_5.md` v1.5 §2.6 + §6.4; `implementation-planner` SKILL.md §1–§11; `Phase_6_Entry_Handoff.md` §3 inputs + §5 sequencing; `Phase_6_Session_2_Session_Prompt.md`; background substrate (consulted but not cited at units per SKILL.md §2): `Architectural_Design_Document_v1.md` v1.2 §3.2, `PRD_v1_0.md` v1.0.1 R-AS-01 through R-AS-07 |
| ODs applied | OD-S2-1.A (per-unit-cluster confirmation); OD-S2-2.A (per-axis coverage matrix only; no aggregate at Session 5); OD-S2-3.A (per-unit cross-axis IS dependency declarations; Session 5 retroactive verification) |
| Entry authorization | `Phase_6_Session_2_Session_Prompt.md` §4 entry-gate verified (8/8) |
| Exit gate | This plan filed at `/mnt/user-data/outputs/`; §[coherence pass] returns ✅ PASS at all 5 audit dimensions; `Phase_6_Session_3_Session_Prompt.md` authored at session close |
| Sub-mode | Initial authoring (Phase 6 Session 2; no prior AS plan filed; P5-CK-cleared AS spec v1.1 is substrate) |

---

## §1 Spec inventory

### §1.1 Contract inventory

Sixteen AS-spec contracts tagged by surfacing class; cross-axis surfacing posture identified.

| C-AS-NN | Spec § | Contract surface (one-line) | Surfacing class | Cross-axis surfacing |
|---|---|---|---|---|
| C-AS-01 | §1 | Four-tier sandbox-isolation tier-set + per-tier capability requirements + computer-use forcing condition | `data-type` (enum + per-tier capability table) | AS-internal |
| C-AS-02 | §2 | Per-tool sandbox-tier `max()` composition formula over five floors | `algorithm` (composition formula) | AS-internal |
| C-AS-03 | §3 | Per-tool `minimum_tier` authoring-time declaration on tool contract | `api-surface` (tool-contract attribute) | AS-internal |
| C-AS-04 | §4 | Sandbox-violation `sandbox.fail.class` seven-value enum + C9/C5/HITL routing staircase | `data-type` + `policy-enforcement` | AS-internal |
| C-AS-05 | §5 | `fetch_secret(name, scope) -> SecretRef` signature + per-tier resolution surface | `api-surface` + `algorithm` | AS-internal |
| C-AS-06 | §6 | Per-tool `required_secrets` allowlist + allowlist-intersection access control + MCP-passthrough prohibition | `data-type` + `policy-enforcement` | AS-internal |
| C-AS-07 | §7 | `secret.fail.class` five-value cause-attribution enum + per-`(secret_backend, scope)` breaker | `data-type` + `policy-enforcement` | AS-internal |
| C-AS-08 | §8 | Secret-fetch audit `outputs_hash` formula + audit-ledger composition + hash-chain integrity | `algorithm` + `module-boundary` | **Cross-axis IS consumer** (U-IS-07, U-IS-08, U-IS-09, U-IS-10, U-IS-11) |
| C-AS-09 | §9 | 12-cell `deployment-surface × blast-radius-tier` sandbox provider matrix + closed six-class provider taxonomy + operator-policy override scope per persona-tier | `data-type` + `policy-enforcement` | AS-internal |
| C-AS-10 | §10 | Per-MCP-transport `sandbox_tier_floor` lookup table + MCP-server four-level trust-tier framework | `data-type` + `policy-enforcement` | AS-internal |
| C-AS-11 | §11 | Sub-agent `sandbox_tier` monotonic-ascension formula + unconditional ascension rule + D4 override-clause non-extension | `algorithm` + `policy-enforcement` | AS-internal |
| C-AS-12 | §12 | 5-axis multiplicative gate-level tunable + cross-deployment monotonicity + override-scope per persona-tier | `algorithm` + `policy-enforcement` | AS-internal |
| C-AS-13 | §13 | Eleven-primitive Anthropic adoption enumeration + 11×4 workload-class adoption-depth matrix + per-engine-class composition overlay + workload-binding-time selection | `data-type` + `policy-enforcement` | **Cross-axis IS consumer** (U-IS-01, U-IS-02 via Skills filesystem-loading) |
| C-AS-14 | §14 | Six Anthropic-primitive attribute namespace declarations (40 attributes) + sampling discipline + audit-floor commitments | `data-type` + `policy-enforcement` | AS-internal |
| C-AS-15 | §15 | Sandbox-bounded span hierarchy + seven `sandbox.*` attribute names + `sandbox.tech` ↔ `sandbox.provider` join contract + sensitive-data discipline | `data-type` + `algorithm` | **Cross-axis IS consumer** (U-IS-07, U-IS-12) |
| C-AS-16 | §16 | AS-axis substrate seam exports surface: seven export sub-surfaces for CP + OD consumption | `module-boundary` | **Cross-axis AS exporter** |

Three AS contracts (C-AS-08, C-AS-13, C-AS-15) are cross-axis IS consumers. C-AS-16 is the AS-side exporter (mirror of C-IS-10).

### §1.2 Cluster decomposition realized

Eight clusters discovered from AS spec structure; ADR-anchoring + cross-axis-consumer separation:

| Cluster | Anchor ADR(s) | Contracts | Unit count | Unit IDs |
|---|---|---|---|---|
| 1 | F4 v1.1 | C-AS-01, C-AS-04 | 3 | U-AS-01, U-AS-02, U-AS-03 |
| 2 | F4 v1.1 | C-AS-02, C-AS-03, C-AS-11 | 6 | U-AS-04 → U-AS-09 |
| 3 | D2 v1.1 | C-AS-09, C-AS-10, C-AS-12 | 6 | U-AS-10 → U-AS-15 |
| 4 | D2 v1.1 (cross-axis IS) | C-AS-15 | 4 | U-AS-16 → U-AS-19 |
| 5 | F5 v1.1 | C-AS-05, C-AS-06, C-AS-07 | 5 | U-AS-20 → U-AS-24 |
| 6 | F5 v1.1 (cross-axis IS) | C-AS-08 | 3 | U-AS-25 → U-AS-27 |
| 7 | D3 v1.2 (cross-axis IS) | C-AS-13, C-AS-14 | 5 | U-AS-28 → U-AS-32 |
| 8 | F4 / F5 / D2 / D3 | C-AS-16 | 1 | U-AS-33 |
| **Total** | — | **16** | **33** | U-AS-01 → U-AS-33 |

### §1.3 Substrate-version citation alignment

Per Workflow v1.5 §7 use-latest-version body-citation discipline + SKILL.md §9 V3 deference:

| Substrate | Citation version | Rationale |
|---|---|---|
| AS spec (`Spec_Action_Surface_v1.md`) | **v1.1** | Latest filed; P5-CK-cleared |
| IS plan (`Implementation_Plan_Information_Substrate_v1.md`) | **v1** | Latest filed (Phase 6 Session 1 close) |
| ADR-F4 | v1.1 | Substrate-anchored by AS spec §1, §11 |
| ADR-F5 | v1.1 | Substrate-anchored by AS spec §5–§8 |
| ADR-D2 | v1.1 | Substrate-anchored by AS spec §9–§12, §15 |
| ADR-D3 | v1.2 | Substrate-anchored by AS spec §13–§14 |

All unit `Implements:` citations point to AS spec v1.1; no prior-version (v1) citations emitted. Cross-axis `Depends on: [U-IS-NN (cross-axis: IS)]` declarations cite IS plan v1.

---

## §2 Atomic-unit decomposition

### §2.1 Cluster 1 — F4 foundational enumerations (C-AS-01 + C-AS-04)

#### U-AS-01 — Declare `SandboxTier` enum + stability invariants + tier-monotonicity ordering

**Implements:** [C-AS-01 §1.1, §1.2]

**Depends on:** (none)

**Inputs:** None (foundational; root unit of AS-axis dependency graph for sandbox subsystem).

**Files affected:** AS-axis sandbox-tier type declaration (logical: `sandbox-tier-type-declaration`); AS-axis sandbox-tier metadata table (logical: `sandbox-tier-metadata-table`).

**Signatures:**

```
enum SandboxTier {
  TIER_1_PROCESS    = "tier-1-process",
  TIER_2_CONTAINER  = "tier-2-container",
  TIER_3_MICROVM    = "tier-3-microvm",
  TIER_4_FULL_VM    = "tier-4-full-vm"
}

enum MechanismClass {
  LANGUAGE_LEVEL_PLUS_FS_ACL,
  PROCESS_ISOLATION_SECCOMP_NS,
  SHARED_KERNEL_CONTAINER_OR_GVISOR_OR_KATA,
  HARDWARE_VIRT_MICROVM_OR_FULL_VM
}

enum BlastRadiusTier {
  READ_ONLY,
  LOCAL_MUTATION,
  EXTERNAL_REVERSIBLE,
  EXTERNAL_IRREVERSIBLE
}

record SandboxTierMetadata {
  tier                    : SandboxTier
  label                   : string
  mechanism_class         : MechanismClass
  capability_lower_bound  : BlastRadiusTier
}

function tier_metadata(t: SandboxTier) -> SandboxTierMetadata
function is_tier_at_or_above(candidate: SandboxTier, floor: SandboxTier) -> bool
```

**Acceptance criteria:**
1. `SandboxTier` enum carries exactly four values; identifiers byte-exact `tier-1-process` / `tier-2-container` / `tier-3-microvm` / `tier-4-full-vm`.
2. `BlastRadiusTier` enum carries exactly four values matching capability-requirement columns.
3. Adding a fifth `SandboxTier` value fails audit-test (per §1.2 row 2 "new tier additions are a Workflow §4.1.2 Class-2 ADR-F4 revision").
4. `tier_metadata` returns table per spec §1.1; `capability_lower_bound` mapped TIER_1→READ_ONLY, TIER_2→LOCAL_MUTATION, TIER_3→EXTERNAL_REVERSIBLE, TIER_4→EXTERNAL_IRREVERSIBLE.
5. `is_tier_at_or_above` implements tier-monotonic ordering (TIER_1 < TIER_2 < TIER_3 < TIER_4).
6. `SandboxTier` is structurally distinct from `sandbox.tech` (per ADR-F4 v1.1 §Consequences (a) — structural attribute vs swap-friendly discriminator).

**Tests:** `test_sandbox_tier_enum_cardinality_four`, `test_sandbox_tier_identifier_strings_kebab_case_byte_exact`, `test_blast_radius_tier_enum_cardinality_four`, `test_tier_metadata_table_complete`, `test_tier_metadata_capability_lower_bound_per_spec`, `test_is_tier_at_or_above_monotonic_ascending`, `test_is_tier_at_or_above_reflexive`.

**Rollback boundary:** Revert `SandboxTier` + `BlastRadiusTier` + `MechanismClass` enums + `SandboxTierMetadata` table + `is_tier_at_or_above` predicate as one coherent change. All downstream sandbox-subsystem units depend on this unit's product; rollback invalidates the entire sandbox subsystem dependency cone.

#### U-AS-02 — Implement forced-tier resolution predicates (computer-use + code-execution beta)

**Implements:** [C-AS-01 §1.3]

**Depends on:** [U-AS-01]

**Inputs:** `ToolContext` per tool invocation carrying `computer_use_bound: bool` and `code_execution_beta_invoked: bool`.

**Files affected:** AS-axis forced-tier resolution module (logical: `forced-tier-resolution`).

**Signatures:**

```
enum ForcedTierCause {
  COMPUTER_USE_BOUND,
  CODE_EXECUTION_BETA
}

record ForcedTierResult {
  tier   : SandboxTier
  cause  : ForcedTierCause
}

function forced_tier(ctx: ToolContext) -> Optional<ForcedTierResult>
```

**Acceptance criteria:**
1. Computer-use binding forces `TIER_4_FULL_VM` regardless of declared blast-radius (spec §1.3 row 2).
2. Code-execution beta forces `TIER_4_FULL_VM` (spec §1.3 row 1 "microVM minimum"; full-VM accepted under tier-monotonicity).
3. When both flags set, `COMPUTER_USE_BOUND` cause wins (full-VM ephemeral + network-egress-restricted is strictly stronger).
4. When neither flag set, `forced_tier` returns `None`.
5. Forced tier supersedes per-tool authoring-time `minimum_tier`.
6. Module is pure function over `ToolContext`; no side effects.

**Tests:** `test_forced_tier_computer_use_returns_tier_4_full_vm`, `test_forced_tier_code_execution_beta_returns_tier_4_full_vm`, `test_forced_tier_neither_returns_none`, `test_forced_tier_both_set_computer_use_cause_precedes`, `test_forced_tier_pure_function`.

**Rollback boundary:** Revert forced-tier resolution module. Absence reduces to "no forcing"; downstream C-AS-02 composition still resolves a tier from the floor-stack — contract violation surfaced at acceptance, build remains coherent.

#### U-AS-03 — Declare `SandboxFailClass` enum + per-class routing-posture metadata + sampling-posture

**Implements:** [C-AS-04 §4.1, §4.2 (metadata layer), §4.3]

**Depends on:** (none)

**Inputs:** None (foundational; consumed downstream by Cluster 4 span-emission unit and cross-axis by CP-axis pre-HITL staircase implementation).

**Files affected:** AS-axis sandbox-fail-class type declaration (logical: `sandbox-fail-class-type-declaration`); AS-axis fail-class routing-posture metadata table (logical: `sandbox-fail-class-routing-metadata`).

**Signatures:**

```
enum SandboxFailClass {
  ESCAPE_ATTEMPT    = "escape_attempt",
  EGRESS_DENIED     = "egress_denied",
  TIMEOUT           = "timeout",
  OOM               = "oom",
  SIGNAL            = "signal",
  EXIT_NONZERO      = "exit_nonzero",
  POLICY_OVERRIDE   = "policy_override"
}

enum C5FailClass { PERMANENT_FAIL, TRANSIENT_FAIL, GATE_CONTRACT_DEPENDENT, INFORMATIONAL }
enum C9RetryPosture { NO_RETRY, C9_BACKOFF_RETRY, PER_TOOL_RETRY_EXIT, AUDIT_LEDGER_ONLY }

record SandboxFailClassMetadata {
  fail_class               : SandboxFailClass
  c5_classification        : C5FailClass
  c9_retry_posture         : C9RetryPosture
  skips_pre_hitl_staircase : bool
  always_sampled           : bool
  tamper_evidence_relevant : bool
}

function fail_class_metadata(c: SandboxFailClass) -> SandboxFailClassMetadata
function permanent_fail_skips_staircase(c: SandboxFailClass) -> bool
```

**Acceptance criteria:**
1. `SandboxFailClass` enum carries exactly seven values; identifiers byte-exact snake_case per spec §4.1.
2. Adding an eighth value requires Workflow §4.1.2 Class-2 ADR-D2 revision.
3. `fail_class_metadata` returns per-row metadata matching spec §4.1 verbatim:
   - ESCAPE_ATTEMPT → PERMANENT_FAIL / NO_RETRY / skips=true / always_sampled=true / tamper=true
   - EGRESS_DENIED → PERMANENT_FAIL / NO_RETRY / skips=true / always_sampled=true / tamper=false
   - TIMEOUT → TRANSIENT_FAIL / C9_BACKOFF_RETRY / skips=false / always_sampled=true / tamper=false
   - OOM → TRANSIENT_FAIL / C9_BACKOFF_RETRY / skips=false / always_sampled=true / tamper=false
   - SIGNAL → PERMANENT_FAIL / NO_RETRY / skips=true / always_sampled=true / tamper=false
   - EXIT_NONZERO → GATE_CONTRACT_DEPENDENT / PER_TOOL_RETRY_EXIT / skips=false / always_sampled=true / tamper=false
   - POLICY_OVERRIDE → INFORMATIONAL / AUDIT_LEDGER_ONLY / skips=false / always_sampled=true / tamper=false
4. `permanent_fail_skips_staircase` returns true exactly for {ESCAPE_ATTEMPT, EGRESS_DENIED, SIGNAL}.
5. `always_sampled` uniform true across all values (per §4.3); not operator-tunable at base-rate.
6. `tamper_evidence_relevant` true only for ESCAPE_ATTEMPT.
7. C9 retry-posture is informational at this unit; actual retry-loop lives in CP-axis plan.

**Tests:** `test_sandbox_fail_class_enum_cardinality_seven`, `test_sandbox_fail_class_identifier_strings_snake_case_byte_exact`, `test_fail_class_metadata_table_complete`, `test_fail_class_metadata_per_spec_table_verbatim`, `test_permanent_fail_skips_staircase_for_escape_egress_signal_only`, `test_always_sampled_uniform_true_across_classes`, `test_tamper_evidence_relevant_only_for_escape_attempt`.

**Rollback boundary:** Revert `SandboxFailClass` + `C5FailClass` + `C9RetryPosture` enums + `SandboxFailClassMetadata` table + `permanent_fail_skips_staircase` predicate. Downstream Cluster 4 unit cannot emit `sandbox.fail.class` attribute; CP-axis pre-HITL staircase loses fail-class substrate.

---

### §2.2 Cluster 2 — F4+D2 per-tool sandbox-tier composition (C-AS-02 + C-AS-03 + C-AS-11)

#### U-AS-04 — Declare foundational discriminator enums (`DeploymentSurface`, `PersonaTier`, `MCPTransport`)

**Implements:** [C-AS-02 §2.3; C-AS-09 §9.1 (forward use); C-AS-12 §12.2 (forward use); C-AS-10 §10.1 (forward use)]

**Depends on:** (none)

**Inputs:** None (foundational; consumed by every downstream composition unit referencing call-site context).

**Files affected:** AS-axis deployment-surface / persona-tier / mcp-transport type declarations (logical: `deployment-surface-type-declaration`, `persona-tier-type-declaration`, `mcp-transport-type-declaration`).

**Signatures:**

```
enum DeploymentSurface {
  LOCAL_DEVELOPMENT     = "local-development",
  SELF_HOSTED_SERVER    = "self-hosted-server",
  MANAGED_CLOUD         = "managed-cloud"
}

enum PersonaTier {
  SOLO_DEVELOPER             = "solo-developer",
  TEAM_BINDING               = "team-binding",
  MULTI_TENANT_COMPLIANCE    = "multi-tenant-compliance"
}

enum MCPTransport {
  STDIO                      = "stdio",
  STREAMABLE_HTTP_L0_REFUSE  = "streamable_http_l0",
  STREAMABLE_HTTP_L1_PINNED  = "streamable_http_l1",
  STREAMABLE_HTTP_L2_SANDBOX = "streamable_http_l2",
  STREAMABLE_HTTP_L3_AUDIT   = "streamable_http_l3"
}
```

**Acceptance criteria:**
1. `DeploymentSurface` carries exactly three values matching C-AS-09 §9.1 row-axis labels byte-exact.
2. `PersonaTier` carries exactly three values; ordering SOLO_DEVELOPER < TEAM_BINDING < MULTI_TENANT_COMPLIANCE for cross-deployment monotonicity.
3. `MCPTransport` carries exactly five values matching C-AS-10 §10.1 transport-level labels.
4. Adding a value to any enum requires Workflow §4.1.2 Class-2 ADR-D2 revision (cardinality bounds: 3/3/5).
5. Identifier strings byte-exact spec-canonical kebab-case and snake_case.
6. Pure data types: no associated functions, no metadata tables.

**Tests:** `test_deployment_surface_cardinality_three`, `test_persona_tier_cardinality_three`, `test_persona_tier_ordering_monotonic`, `test_mcp_transport_cardinality_five`, `test_enum_identifier_strings_byte_exact`.

**Rollback boundary:** Revert all three enum declarations. Every downstream composition unit (U-AS-06, U-AS-08, U-AS-09, Cluster 3 units) consumes these enums; rollback invalidates the sandbox composition subsystem dependency cone.

#### U-AS-05 — Implement `blast_radius_floor` default mapping

**Implements:** [C-AS-02 §2.4]

**Depends on:** [U-AS-01]

**Inputs:** `BlastRadiusTier` value (per call-site context).

**Files affected:** AS-axis blast-radius-floor mapping module (logical: `blast-radius-floor-mapping`).

**Signatures:**

```
function blast_radius_floor(tier: BlastRadiusTier) -> SandboxTier
  // READ_ONLY            → TIER_1_PROCESS
  // LOCAL_MUTATION       → TIER_2_CONTAINER
  // EXTERNAL_REVERSIBLE  → TIER_3_MICROVM
  // EXTERNAL_IRREVERSIBLE → TIER_4_FULL_VM
```

**Acceptance criteria:**
1. Mapping is total over `BlastRadiusTier`; every enum value resolves.
2. Per-row mapping matches C-AS-02 §2.4 table verbatim.
3. Mapping is "default" — subject to overrides from forcing conditions (U-AS-02) and upstream `sandbox_tier_floor` (U-AS-06).
4. Pure function; deterministic.

**Tests:** `test_blast_radius_floor_read_only_to_tier_1`, `test_blast_radius_floor_local_mutation_to_tier_2`, `test_blast_radius_floor_external_reversible_to_tier_3`, `test_blast_radius_floor_external_irreversible_to_tier_4`, `test_blast_radius_floor_total_function`.

**Rollback boundary:** Revert mapping function. U-AS-06 and U-AS-08 consume this function; rollback breaks the second-floor input to the `max()` composition.

#### U-AS-06 — Implement `sandbox_tier_floor` 10-row lookup table

**Implements:** [C-AS-02 §2.3]

**Depends on:** [U-AS-01, U-AS-04, U-AS-05]

**Inputs:** `ToolMetadata` (carries `is_deterministic_inhouse`, `forces_computer_use`, `forces_code_execution`); `DeploymentSurface`; `BlastRadiusTier`; `MCPTransport` (Optional); `MCPTrustLevel` (Optional).

**Files affected:** AS-axis sandbox-tier-floor lookup module (logical: `sandbox-tier-floor-lookup`).

**Signatures:**

```
enum SandboxTierFloorResult {
  RESOLVED(SandboxTier),
  REFUSE
}

enum MCPTrustLevel {
  L0_REFUSE_REMOTE,
  L1_SIGNED_PINNED,
  L2_SANDBOX_ALL,
  L3_ALLOW_WITH_AUDIT
}

function sandbox_tier_floor(
  tool: ToolMetadata,
  deployment_surface: DeploymentSurface,
  blast_radius_tier: BlastRadiusTier,
  mcp_transport: Optional<MCPTransport>,
  mcp_trust_level: Optional<MCPTrustLevel>
) -> SandboxTierFloorResult
```

**Acceptance criteria:**
1. Lookup implements ten rows per C-AS-02 §2.3 table verbatim (computer-use force, code-execution force, STDIO MCP, remote MCP L0/L1/L2/L3, read-only deterministic, local-mutation, external-reversible, external-irreversible).
2. Row precedence: forcing conditions → MCP-transport rows → blast-radius default rows.
3. REFUSE sentinel (row 4) is structurally distinct from any `SandboxTier` value.
4. Row 5 egress allow-listing requirement is downstream MCP registration concern.
5. Rows 7–10 reference `blast_radius_floor` from U-AS-05.
6. Alignment between this table and C-AS-10 §10.1 verified by integration test at U-AS-13 (Cluster 3).

**Tests:** `test_sandbox_tier_floor_computer_use_returns_tier_4`, `test_sandbox_tier_floor_code_execution_returns_tier_4`, `test_sandbox_tier_floor_stdio_with_read_only_returns_tier_3`, `test_sandbox_tier_floor_stdio_with_external_irreversible_returns_tier_4`, `test_sandbox_tier_floor_remote_l0_returns_refuse`, `test_sandbox_tier_floor_remote_l2_returns_tier_4`, `test_sandbox_tier_floor_remote_l1_returns_blast_radius_floor`, `test_sandbox_tier_floor_remote_l3_returns_blast_radius_floor`, `test_sandbox_tier_floor_read_only_deterministic_returns_tier_1`, `test_sandbox_tier_floor_local_mutation_returns_tier_2`, `test_sandbox_tier_floor_external_reversible_returns_tier_3`, `test_sandbox_tier_floor_external_irreversible_returns_tier_4`, `test_sandbox_tier_floor_forcing_precedence_over_blast_radius`, `test_sandbox_tier_floor_refuse_is_distinct_from_tier_values`.

**Rollback boundary:** Revert lookup function + `SandboxTierFloorResult` + `MCPTrustLevel`. U-AS-08 + U-AS-09 consume this function; rollback invalidates the D2-introduced `sandbox_tier_floor` axis.

#### U-AS-07 — Add `ToolContract.minimum_tier` field + declaration discipline + registration enforcement

**Implements:** [C-AS-03 §3.1, §3.2, §3.3]

**Depends on:** [U-AS-01]

**Inputs:** Tool contract serialization at registration boundary.

**Files affected:** AS-axis tool-contract schema (logical: `tool-contract-schema`); registration validator (logical: `tool-contract-registration-validator`).

**Signatures:**

```
record ToolContract {
  name              : string
  description       : string
  input_schema      : JSONSchema
  output_schema     : JSONSchema
  minimum_tier      : SandboxTier
  blast_radius_tier : BlastRadiusTier
  required_secrets  : List<SecretAllowlistEntry>
}

enum ContractValidationResult {
  VALID(ToolContract),
  MISSING_MINIMUM_TIER,
  MISSING_BLAST_RADIUS_TIER
}

function validate_tool_contract_at_registration(raw_contract: RawContractInput) -> ContractValidationResult

const RECOMMENDED_CONTRACT_DEFAULT_TIER: SandboxTier = TIER_4_FULL_VM
```

**Acceptance criteria:**
1. `minimum_tier` is required at registration; missing → `MISSING_MINIMUM_TIER`.
2. `blast_radius_tier` is required; missing → `MISSING_BLAST_RADIUS_TIER`.
3. `required_secrets` optional; empty list permitted; missing → treated as empty.
4. `RECOMMENDED_CONTRACT_DEFAULT_TIER` = TIER_4_FULL_VM (§3.3 fail-closed).
5. `minimum_tier` non-tier-promoting: a `max()` floor at U-AS-08, not a ceiling.
6. Declared `minimum_tier` visible to design-time operator at authoring.

**Tests:** `test_tool_contract_minimum_tier_required`, `test_tool_contract_blast_radius_tier_required`, `test_tool_contract_required_secrets_optional_empty_permitted`, `test_tool_contract_required_secrets_omitted_treated_as_empty`, `test_recommended_contract_default_tier_is_tier_4_full_vm`, `test_minimum_tier_non_tier_promoting`.

**Rollback boundary:** Revert `ToolContract` schema additions + registration validator. U-AS-08 reads `tool.contract.minimum_tier`; rollback removes the first floor of the `max()`.

#### U-AS-08 — Implement `sandbox_tier(tool, call_site_context)` composition function

**Implements:** [C-AS-02 §2.1, §2.2, §2.5]

**Depends on:** [U-AS-01, U-AS-02, U-AS-04, U-AS-05, U-AS-06, U-AS-07]

**Inputs:** `tool: ToolContract`; `call_site_context: CallSiteContext`; forward-declared interface signatures for `mcp_server_trust_tier_floor` and `operator_policy_floor` injected by CP plan (Session 3).

**Files affected:** AS-axis sandbox-tier composition module (logical: `sandbox-tier-composition`); call-site-context schema (logical: `call-site-context-schema`); forward-declared floor interfaces (logical: `floor-interface-declarations`).

**Signatures:**

```
record CallSiteContext {
  taint_state         : TaintState
  mcp_server          : Optional<MCPServer>
  deployment_surface  : DeploymentSurface
  blast_radius_tier   : BlastRadiusTier
  mcp_transport       : Optional<MCPTransport>
  mcp_trust_level     : Optional<MCPTrustLevel>
  persona_tier        : PersonaTier
  computer_use_bound  : bool
  code_execution_beta_invoked : bool
}

interface FloorInterfaces {
  mcp_server_trust_tier_floor : (Optional<MCPServer>) -> SandboxTier
  operator_policy_floor       : (PersonaTier) -> SandboxTier
}

enum SandboxTierCompositionResult { RESOLVED(SandboxTier, AssignedTierReason), REFUSE }

enum AssignedTierReason {
  CONTRACT_MINIMUM, BLAST_RADIUS_FLOOR, MCP_SERVER_TRUST_FLOOR,
  OPERATOR_POLICY_FLOOR, SANDBOX_TIER_FLOOR,
  COMPUTER_USE_FORCING, CODE_EXECUTION_FORCING
}

function sandbox_tier(
  tool: ToolContract,
  ctx: CallSiteContext,
  floors: FloorInterfaces
) -> SandboxTierCompositionResult
```

**Acceptance criteria:**
1. Composition implements C-AS-02 §2.2 formula: `max(minimum_tier, blast_radius_floor, mcp_server_trust_tier_floor, sandbox_tier_floor, operator_policy_floor)`.
2. Forced-tier predicate from U-AS-02 takes precedence: `forced_tier(ctx) = Some(...)` → RESOLVED with COMPUTER_USE_FORCING or CODE_EXECUTION_FORCING cause.
3. REFUSE propagation: `sandbox_tier_floor` returning REFUSE → composition returns REFUSE.
4. `AssignedTierReason` identifies winning floor; tie-breaking precedence: forcing → sandbox_tier_floor → operator_policy_floor → mcp_server_trust_floor → blast_radius_floor → contract_minimum.
5. Monotonically rising `max()` per §2.2 closing paragraph; neither C4 nor C10 voice suppressed.
6. Resolved tier recoverable from `sandbox.enter` event per C-AS-15 §15.2.
7. Pure given `floors` interface implementations.

**Tests:** `test_sandbox_tier_composition_max_of_five_floors`, `test_sandbox_tier_composition_forced_tier_precedence`, `test_sandbox_tier_composition_refuse_propagates`, `test_sandbox_tier_composition_minimum_tier_floor_when_others_lower`, `test_sandbox_tier_composition_assigned_tier_reason_at_tie`, `test_sandbox_tier_composition_pure_given_floors`, `test_sandbox_tier_composition_with_stub_floors_reduces_to_d2_axes`.

**Rollback boundary:** Revert composition function + `CallSiteContext` + `FloorInterfaces` + `SandboxTierCompositionResult` + `AssignedTierReason`. Cluster 3 floor units retain independent acceptance; only the composition is removed.

#### U-AS-09 — Implement `sub_agent_sandbox_tier` monotonic-ascension function

**Implements:** [C-AS-11 §11.1, §11.2, §11.3, §11.4, §11.5]

**Depends on:** [U-AS-01, U-AS-04, U-AS-06]

**Inputs:** `parent_sandbox_tier`, `blast_radius`, `mcp_transport`, `deployment_surface`. Parent tier resolved by U-AS-08 at parent call site.

**Files affected:** AS-axis sub-agent sandbox-tier resolution module (logical: `sub-agent-sandbox-tier-resolution`); sub-agent boundary violation detector (logical: `sub-agent-tier-downgrade-violation-detector`).

**Signatures:**

```
function sub_agent_sandbox_tier(
  parent_sandbox_tier: SandboxTier,
  blast_radius: BlastRadiusTier,
  mcp_transport: Optional<MCPTransport>,
  mcp_trust_level: Optional<MCPTrustLevel>,
  deployment_surface: DeploymentSurface
) -> SandboxTier
  =
  max(parent_sandbox_tier, sandbox_tier_floor(...))

enum SubAgentBoundaryViolation {
  TIER_DOWNGRADE_ATTEMPTED(parent: SandboxTier, attempted_child: SandboxTier),
  REGISTRY_OVERRIDE_WITH_TIER_DOWNGRADE(parent: SandboxTier, attempted_child: SandboxTier)
}

function detect_sub_agent_tier_downgrade(
  parent_sandbox_tier: SandboxTier,
  proposed_child_tier: SandboxTier
) -> Optional<SubAgentBoundaryViolation>
```

**Acceptance criteria:**
1. Sub-agent tier always ≥ parent tier (§11.2 row 1).
2. Tier downgrade structurally prohibited (§11.2 row 2); `detect_sub_agent_tier_downgrade` returns Some when proposed < parent.
3. D4 override-clause does not extend to sandbox monotonicity (§11.2 row 3 + §11.3) — even when registry-scoped override is set, downgrade detection returns Some.
4. Composition is `max(parent_tier, sandbox_tier_floor(...))` per §11.1 — other floors do not reset at sub-agent dispatch.
5. Sub-agent tier-escalation surface emits `sandbox.tier_escalation` event (downstream Cluster 4); this unit returns the structured result.
6. Cross-deployment monotonicity composition: persona-tier bridging-arc raises floors per §11.4.
7. Tier downgrade attempt emits `sandbox.fail.class = POLICY_OVERRIDE` per §11.5 row 3.

**Tests:** `test_sub_agent_tier_at_or_above_parent`, `test_sub_agent_tier_max_of_two_floors`, `test_sub_agent_tier_parent_wins_when_floor_lower`, `test_sub_agent_tier_downgrade_detected`, `test_sub_agent_tier_at_or_above_no_violation`, `test_sub_agent_tier_d4_override_does_not_extend`, `test_sub_agent_tier_pure_function`.

**Rollback boundary:** Revert `sub_agent_sandbox_tier` + downgrade detector + `SubAgentBoundaryViolation`. CP plan loses the sandbox-monotonicity contract at sub-agent dispatch; sub-agents could dispatch at weaker isolation than parent.

---

### §2.3 Cluster 3 — D2 deployment matrix + gate-level composition (C-AS-09 + C-AS-10 + C-AS-12)

#### U-AS-10 — Declare 12-cell deployment-matrix + cell-selection lookup function

**Implements:** [C-AS-09 §9.1, §9.3, §9.5]

**Depends on:** [U-AS-01, U-AS-02, U-AS-04, U-AS-11]

**Inputs:** `DeploymentSurface`; `BlastRadiusTier`; `ToolContext` (forwarded to `forced_tier` per U-AS-02).

**Files affected:** AS-axis deployment-matrix data declaration (logical: `deployment-matrix-declaration`); matrix cell-selection lookup module (logical: `matrix-cell-selection-lookup`).

**Signatures:**

```
record DeploymentMatrixCell {
  sandbox_tier        : SandboxTier
  provider_class      : SandboxProviderClass
  candidate_witnesses : List<string>
}

const DEPLOYMENT_MATRIX: Map<(DeploymentSurface, BlastRadiusTier), DeploymentMatrixCell>

function lookup_cell(surface: DeploymentSurface, blast_radius: BlastRadiusTier) -> DeploymentMatrixCell
function lookup_cell_with_forcing(surface, blast_radius, ctx: ToolContext) -> DeploymentMatrixCell
```

**Acceptance criteria:**
1. `DEPLOYMENT_MATRIX` declares exactly 12 cells (3 × 4) per spec §9.1 verbatim.
2. Per-cell `sandbox_tier` + `provider_class` match spec §9.1 row-by-row: local-dev/self-hosted = LANGUAGE_LEVEL / PROCESS_FS_OVERLAY / CONTAINER / MICROVM_FIRECRACKER at T1/T2/T3/T4; managed-cloud = LANGUAGE_LEVEL / CONTAINER / CONTAINER / FULL_VM at T1/T2/T3/T4.
3. `candidate_witnesses` non-normative documentation per §9.5 deployment-surface-time stage.
4. `lookup_cell` total function over (DeploymentSurface, BlastRadiusTier).
5. `lookup_cell_with_forcing` honors `forced_tier`: computer-use forcing or code-execution beta resolves to EXTERNAL_IRREVERSIBLE cell at relevant surface.
6. Matrix cell selection is D2-layer commitment per §9.5 row 1; specific candidate-within-provider-class is operator-selected at deployment-binding time.

**Tests:** `test_deployment_matrix_cardinality_twelve`, `test_deployment_matrix_local_development_row_per_spec`, `test_deployment_matrix_self_hosted_server_row_per_spec`, `test_deployment_matrix_managed_cloud_row_per_spec`, `test_lookup_cell_total_function`, `test_lookup_cell_sandbox_tier_monotonic_by_blast_radius`, `test_lookup_cell_with_forcing_computer_use_resolves_to_external_irreversible`, `test_lookup_cell_with_forcing_code_execution_resolves_to_external_irreversible`, `test_lookup_cell_with_forcing_no_forcing_matches_lookup_cell`.

**Rollback boundary:** Revert `DEPLOYMENT_MATRIX` + `DeploymentMatrixCell` + lookup functions. Cluster 4 span unit cannot emit `sandbox.tier` and `sandbox.tech` joined per cell; cell-selection-time provider-class binding fails.

#### U-AS-11 — Declare `SandboxProviderClass` enumeration + per-class metadata

**Implements:** [C-AS-09 §9.2]

**Depends on:** [U-AS-01]

**Inputs:** None (foundational; consumed by U-AS-10 matrix cells and downstream Cluster 4 `sandbox.tech` attribute).

**Files affected:** AS-axis sandbox-provider-class type declaration (logical: `sandbox-provider-class-type-declaration`); provider-class metadata table (logical: `sandbox-provider-class-metadata`).

**Signatures:**

```
enum SandboxProviderClass {
  LANGUAGE_LEVEL                      = "language-level",
  FILESYSTEM_OVERLAY_WORKTREE         = "filesystem-overlay-worktree",
  PROCESS_ULIMIT_BUBBLEWRAP_SEATBELT  = "process-ulimit-bubblewrap-seatbelt",
  CONTAINER                           = "container",
  MICROVM_FIRECRACKER                 = "microvm-firecracker",
  FULL_VM                             = "full-vm"
}

record ProviderClassMetadata {
  provider_class        : SandboxProviderClass
  mechanism_description : string
  tier_mapping          : Set<SandboxTier>
  cardinality           : ClassCardinality
}

enum ClassCardinality { OPEN }

function provider_class_metadata(c: SandboxProviderClass) -> ProviderClassMetadata
```

**Acceptance criteria:**
1. `SandboxProviderClass` enum carries exactly six values per spec §9.2 verbatim.
2. Provider-class taxonomy closed at six; adding seventh requires Workflow §4.1.2 Class-2 ADR-D2 revision.
3. Per-class `tier_mapping` matches spec §9.2 column 4:
   - LANGUAGE_LEVEL → {TIER_1_PROCESS, TIER_2_CONTAINER}
   - FILESYSTEM_OVERLAY_WORKTREE → {TIER_2_CONTAINER}
   - PROCESS_ULIMIT_BUBBLEWRAP_SEATBELT → {TIER_2_CONTAINER}
   - CONTAINER → {TIER_3_MICROVM}
   - MICROVM_FIRECRACKER → {TIER_4_FULL_VM}
   - FULL_VM → {TIER_4_FULL_VM}
4. Cardinality OPEN for every class (new candidates within existing class permitted at deployment-binding time).
5. `provider_class_metadata` total over enum.

**Tests:** `test_sandbox_provider_class_cardinality_six`, `test_sandbox_provider_class_identifier_strings_kebab_case_byte_exact`, `test_provider_class_metadata_table_complete`, `test_provider_class_metadata_tier_mapping_per_spec`, `test_container_class_maps_only_to_tier_3`, `test_microvm_firecracker_class_maps_only_to_tier_4`.

**Rollback boundary:** Revert enum + metadata table + helpers. U-AS-10 matrix cells cite provider-class names; rollback invalidates the `provider_class` field. Cluster 4 `sandbox.provider` ↔ `sandbox.tech` join contract loses provider-class anchor.

#### U-AS-12 — Operator-policy override scope per persona-tier

**Implements:** [C-AS-09 §9.4; C-AS-12 §12.2 reference]

**Depends on:** [U-AS-04]

**Inputs:** `PersonaTier`; proposed override target cell `(DeploymentSurface, BlastRadiusTier)`.

**Files affected:** AS-axis operator-policy override-scope module (logical: `operator-policy-override-scope`).

**Signatures:**

```
enum OverrideScopeResult {
  PERMITTED_APPEND_ONLY,
  PERMITTED_HASH_CHAINED,
  PROHIBITED_STRUCTURAL,
  PROHIBITED_BLAST_RADIUS_TIER
}

function override_scope(
  persona_tier: PersonaTier,
  proposed_cell: (DeploymentSurface, BlastRadiusTier)
) -> OverrideScopeResult
```

**Acceptance criteria:**
1. `override_scope` total over (PersonaTier, (DeploymentSurface, BlastRadiusTier)).
2. Per-persona-tier scope matches spec §9.4 verbatim:
   - SOLO_DEVELOPER → PERMITTED_APPEND_ONLY at any cell
   - TEAM_BINDING + EXTERNAL_IRREVERSIBLE → PROHIBITED_BLAST_RADIUS_TIER
   - TEAM_BINDING + other → PERMITTED_HASH_CHAINED
   - MULTI_TENANT_COMPLIANCE → PROHIBITED_STRUCTURAL at any cell
3. PROHIBITED_STRUCTURAL produces violation-event audit per §12.3, not a tier change.
4. Override-scope consumed downstream by Cluster 4 span unit (POLICY_OVERRIDE emission) and Cluster 6 audit unit.

**Tests:** `test_override_scope_solo_developer_permitted_at_all_cells`, `test_override_scope_team_binding_permitted_at_non_irreversible`, `test_override_scope_team_binding_prohibited_at_external_irreversible`, `test_override_scope_multi_tenant_compliance_prohibited_at_all_cells`, `test_override_scope_total_function`.

**Rollback boundary:** Revert override-scope module + `OverrideScopeResult`. Cluster 4 cannot discriminate POLICY_OVERRIDE emission posture at multi-tenant-compliance; Cluster 6 audit cannot emit per-persona-tier append-only vs hash-chained ledger entry.

#### U-AS-13 — Per-MCP-transport sandbox-tier floor lookup table + framework references

**Implements:** [C-AS-10 §10.1, §10.2, §10.3]

**Depends on:** [U-AS-01, U-AS-04, U-AS-05, U-AS-06]

**Inputs:** `MCPTransport`; `MCPTrustLevel`; `BlastRadiusTier`.

**Files affected:** AS-axis per-MCP-transport floor lookup module (logical: `mcp-transport-floor-lookup`); MCP server registration discriminator (logical: `mcp-server-registration-discriminator`); alignment-verifier (logical: `mcp-floor-alignment-verifier`).

**Signatures:**

```
function mcp_transport_floor(
  transport: MCPTransport,
  trust_level: MCPTrustLevel,
  blast_radius: BlastRadiusTier
) -> SandboxTierFloorResult

function rejects_at_registration(transport: MCPTransport, trust_level: MCPTrustLevel) -> bool
```

**Acceptance criteria:**
1. `mcp_transport_floor` implements §10.1 table verbatim (5 rows: STDIO → max(TIER_3, blast_radius_floor); L0 → REFUSE; L1 → blast_radius_floor; L2 → max(TIER_4, blast_radius_floor); L3 → blast_radius_floor).
2. Row 4 egress allow-list requirement is downstream MCP registration concern.
3. Row 5 audit-ledger entry requirement is Cluster 6 concern.
4. `rejects_at_registration` returns true exactly when `mcp_transport_floor` returns REFUSE (L0 case).
5. Alignment with U-AS-06 §2.3 rows 3-6: this unit's lookup returns semantically equivalent results; alignment enforced by `test_mcp_floor_alignment_with_u_as_06_sandbox_tier_floor`.
6. Per §10.3 four-level MCP server trust-tier framework: names align with `MCPTrustLevel` from U-AS-06; this unit declares the per-(transport, trust_level) → tier mapping.
7. Five-tier framework at §10.3 closing paragraph lives in CP plan; this unit does NOT implement that function.

**Tests:** `test_mcp_transport_floor_stdio_with_read_only_returns_tier_3`, `test_mcp_transport_floor_stdio_with_external_irreversible_returns_tier_4`, `test_mcp_transport_floor_l0_returns_refuse`, `test_mcp_transport_floor_l1_returns_blast_radius_floor`, `test_mcp_transport_floor_l2_returns_tier_4`, `test_mcp_transport_floor_l3_returns_blast_radius_floor_with_audit_marker`, `test_rejects_at_registration_only_for_l0`, `test_mcp_floor_alignment_with_u_as_06_sandbox_tier_floor`.

**Rollback boundary:** Revert per-MCP-transport floor module + alignment verifier. U-AS-08 composition cannot resolve MCP-bound tool sandbox-tier via per-transport floor input; U-AS-06's §2.3 MCP rows still function (duplicate declaration); alignment guarantee lost.

#### U-AS-14 — Implement 5-axis gate-level multiplicative tunable composition

**Implements:** [C-AS-12 §12.1, §12.2 reference, §12.5]

**Depends on:** [U-AS-01, U-AS-04, U-AS-05, U-AS-06]

**Inputs:** `tool`, `mcp_server`, `persona_tier`, `deployment_surface`, `blast_radius_tier`, `mcp_transport`, `mcp_trust_level`. Forward-declared interfaces injected by CP plan (Session 3).

**Files affected:** AS-axis gate-level enum declaration (logical: `gate-level-enum-declaration`); 5-axis gate-level composition module (logical: `gate-level-5-axis-composition`); gate-level floor interface declarations (logical: `gate-level-floor-interfaces`).

**Signatures:**

```
enum GateLevel {
  AUTO   = "auto",
  ASK    = "ask",
  DENY   = "deny"
}

interface GateLevelFloorInterfaces {
  per_tool_gate_level       : (ToolContract) -> GateLevel
  blast_radius_gate_floor   : (ToolContract) -> GateLevel
  per_mcp_server_trust_floor: (Optional<MCPServer>) -> GateLevel
  persona_tier_floor        : (PersonaTier) -> GateLevel
}

function tier_to_gate_level_floor(tier: SandboxTier) -> GateLevel
function gate_level(tool: ToolContract, ctx: CallSiteContext, floors: GateLevelFloorInterfaces) -> GateLevel
```

**Acceptance criteria:**
1. Composition implements §12.1 formula: `max(per_tool_gate_level, blast_radius_gate_floor, per_mcp_server_trust_floor, persona_tier_floor, tier_to_gate_level_floor(sandbox_tier_floor(...)))`.
2. `GateLevel` carries exactly three values byte-exact ("auto" / "ask" / "deny").
3. `max()` ordering: AUTO < ASK < DENY; highest gate-level wins.
4. Multiplicative discipline preservation per §12.5: every floor expresses its concern; higher wins by construction.
5. T-perm-1 closure is structural composition per §12.5.
6. Fifth axis (sandbox_tier) enters via `tier_to_gate_level_floor` after U-AS-06 resolves.
7. Forward-declared `per_tool_gate_level` consumes `ToolContract`; field added by CP plan (C4 contract).
8. Per §12.2 reference: operator-policy override per persona-tier from U-AS-12 composes into `persona_tier_floor` interface at CP plan.
9. Pure given `floors` interface implementations.

**Tests:** `test_gate_level_enum_cardinality_three`, `test_gate_level_ordering_auto_lt_ask_lt_deny`, `test_tier_to_gate_level_floor_per_spec`, `test_gate_level_composition_max_of_five_axes`, `test_gate_level_composition_deny_wins`, `test_gate_level_composition_no_suppression`, `test_gate_level_composition_with_cp_floor_stubs_reduces_to_d2_axes`, `test_gate_level_composition_pure_given_floors`.

**Rollback boundary:** Revert `GateLevel` + composition function + `GateLevelFloorInterfaces` + `tier_to_gate_level_floor`. CP plan retains independent floor implementations; AS-side 5-axis composition is removed.

#### U-AS-15 — Implement cross-deployment sandbox-tier monotonicity contract

**Implements:** [C-AS-12 §12.4; C-AS-11 §11.4 cross-deployment composition]

**Depends on:** [U-AS-01, U-AS-04, U-AS-06]

**Inputs:** Persona-tier transition (old → new); cell state; deployment-binding-time vs runtime-binding-time discriminator.

**Files affected:** AS-axis cross-deployment monotonicity invariant module (logical: `cross-deployment-monotonicity`); tier-escalation event detector (logical: `tier-escalation-event-detector`); tier-downgrade revision guard (logical: `tier-downgrade-revision-guard`).

**Signatures:**

```
function persona_tier_traversal_ascends(from: PersonaTier, to: PersonaTier) -> bool

function bridging_arc_effective_tier_raise(
  from_persona: PersonaTier,
  to_persona: PersonaTier,
  cell: (DeploymentSurface, BlastRadiusTier),
  in_flight_workflow_count: int
) -> TierRaiseResult

record TierRaiseResult {
  old_floor          : SandboxTier
  new_floor          : SandboxTier
  raised_immediately : bool
  affected_workflows : int
}

function detect_tier_downgrade_governance_violation(
  proposed_change: (DeploymentSurface, BlastRadiusTier, SandboxTier_old, SandboxTier_new)
) -> Optional<GovernanceViolation>

enum GovernanceViolation {
  TIER_DOWNGRADE_REQUIRES_CLASS_2_REVISION(
    cell: (DeploymentSurface, BlastRadiusTier),
    from: SandboxTier,
    to: SandboxTier
  )
}
```

**Acceptance criteria:**
1. `persona_tier_traversal_ascends` returns true exactly when to > from (SOLO < TEAM < MULTI_TENANT).
2. Bridging-arc traversal under ascending persona-tier transitions raises `sandbox_tier_floor` monotonically per §12.4 row 1.
3. In-flight effective raise per §12.4 row 3: `raised_immediately = true`; all workflows raise immediately.
4. No tier-equivalence-below-floor per §12.4 row 2.
5. Tier-downgrade-as-Class-2-revision per §12.4 row 4: runtime tier downgrade structurally prohibited.
6. Composition with C-AS-11 sub-agent ascension: sub-agent tier ≥ parent tier ≥ persona-tier floor.
7. Bridging-arc events emit `sandbox.tier_escalation` events (Cluster 4 emission).

**Tests:** `test_persona_tier_traversal_ascends_solo_to_team_returns_true`, `test_persona_tier_traversal_ascends_team_to_multi_tenant_returns_true`, `test_persona_tier_traversal_ascends_multi_tenant_to_team_returns_false`, `test_persona_tier_traversal_ascends_equal_returns_false`, `test_bridging_arc_raises_immediately_under_ascending_traversal`, `test_bridging_arc_no_raise_under_equal_persona_tier`, `test_bridging_arc_in_flight_workflows_all_raised`, `test_detect_tier_downgrade_returns_some_for_strict_decrease`, `test_detect_tier_downgrade_returns_none_for_no_change_or_increase`, `test_monotonicity_composes_with_sub_agent_ascension`.

**Rollback boundary:** Revert cross-deployment monotonicity module + governance-violation detector + bridging-arc raise handler. Persona-tier transitions occur but lose in-flight effective-raise contract; tier downgrades silently permitted; sub-agent ascension at U-AS-09 remains independent.

---

### §2.4 Cluster 4 — Sandbox-bounded span schema (C-AS-15)

#### U-AS-16 — Declare seven `sandbox.*` attribute names + `sandbox.tech` ↔ `sandbox.provider` join contract

**Implements:** [C-AS-15 §15.2, §15.3, §15.7]

**Depends on:** [U-AS-01, U-AS-03, U-AS-08]

**Inputs:** None (foundational attribute schema; consumed by span-emission and OD plan ingestion).

**Files affected:** AS-axis sandbox attribute namespace declaration (logical: `sandbox-attribute-namespace-declaration`); sandbox-tech-to-provider join table (logical: `sandbox-tech-provider-join-table`).

**Signatures:**

```
enum SandboxTechClass {
  MICROVM         = "microvm",
  CONTAINER       = "container",
  VM              = "vm",
  LANGUAGE_LEVEL  = "language-level",
  FS_OVERLAY      = "fs-overlay"
}

enum SandboxProvider {
  E2B_FIRECRACKER, MODAL_GVISOR, KATA, BEDROCK_AGENTCORE,
  VERTEX_AGENT_ENGINE, ANTHROPIC_COMPUTER_USE_VM,
  DOCKER_OCI, OPENSANDBOX, DIFY_SANDBOX, DAYTONA,
  DENO, LANGUAGE_LEVEL,
  BUBBLEWRAP, SEATBELT, FUSE_OVERLAY, FUSE_PROJFS, KILOCODE_WORKTREE
}

record SandboxAttributeSchema {
  attribute_name    : string
  value_type        : AttributeValueType
  cardinality       : Cardinality
  emitted_on        : SpanEventKind
  discriminator_role: string
}

const SANDBOX_ATTRIBUTE_SCHEMA: List<SandboxAttributeSchema>   // exactly seven entries

function provider_belongs_to(provider: SandboxProvider) -> SandboxTechClass
function tech_admits_provider(tech: SandboxTechClass, provider: SandboxProvider) -> bool
```

**Acceptance criteria:**
1. `SANDBOX_ATTRIBUTE_SCHEMA` declares exactly seven entries per §15.2 verbatim: `sandbox.tier`, `sandbox.tech`, `sandbox.fail.class`, `sandbox.policy.assigned_tier_reason`, `sandbox.cost.tier_overhead_ms`, `sandbox.cost.tier_overhead_usd`, `sandbox.provider`.
2. Attribute names byte-exact per §15.2; F4-authoritative naming per ADR-F4 v1.1 §Consequences (a) — OD plan §1.2 ingests verbatim.
3. `SandboxTechClass` carries exactly five values; `VM` reserved at v1.1 (no candidate providers).
4. `SandboxProvider` carries exactly 17 values at v1.1; operator-tunable at workload-binding-time within existing tech-class.
5. `provider_belongs_to` total function; functional belongs-to per §15.3:
   - MICROVM ← {E2B_FIRECRACKER, MODAL_GVISOR, KATA, BEDROCK_AGENTCORE, VERTEX_AGENT_ENGINE, ANTHROPIC_COMPUTER_USE_VM}
   - CONTAINER ← {DOCKER_OCI, OPENSANDBOX, DIFY_SANDBOX, DAYTONA}
   - VM ← ∅
   - LANGUAGE_LEVEL ← {DENO, LANGUAGE_LEVEL}
   - FS_OVERLAY ← {BUBBLEWRAP, SEATBELT, FUSE_OVERLAY, FUSE_PROJFS, KILOCODE_WORKTREE}
6. Enum references: `sandbox.tier` references U-AS-01 `SandboxTier`; `sandbox.fail.class` references U-AS-03 `SandboxFailClass`; `sandbox.policy.assigned_tier_reason` references U-AS-08 `AssignedTierReason`.
7. Capability-floor (iv) traceability per §15.7: F2-05 sandbox sub-finding closure declaration site; OD plan cites this unit as source.

**Tests:** `test_sandbox_attribute_schema_cardinality_seven`, `test_sandbox_attribute_names_byte_exact_per_spec_15_2`, `test_sandbox_attribute_emitted_on_per_spec`, `test_sandbox_tech_class_cardinality_five`, `test_sandbox_provider_cardinality_seventeen_at_v1_1`, `test_provider_belongs_to_total_function`, `test_provider_belongs_to_microvm_class_six_members`, `test_provider_belongs_to_container_class_four_members`, `test_provider_belongs_to_vm_class_zero_members`, `test_provider_belongs_to_language_level_class_two_members`, `test_provider_belongs_to_fs_overlay_class_five_members`, `test_tech_admits_provider_functional_join`.

**Rollback boundary:** Revert attribute schema + tech-class enum + provider enum + join functions. U-AS-17 consumes the attribute names; rollback invalidates the span-emission attribute set. OD plan §1.2 sandbox.* row loses source-of-truth.

#### U-AS-17 — Declare span hierarchy + five span event kinds + sensitive-data discipline

**Implements:** [C-AS-15 §15.1, §15.5]

**Depends on:** [U-AS-01, U-AS-03, U-AS-08, U-AS-16]

**Inputs:** Span emission triggered at sandbox-bounded tool-call lifecycle.

**Files affected:** AS-axis sandbox span event kind declaration (logical: `sandbox-span-event-kind-declaration`); span emission shape (logical: `sandbox-span-emission-shape`); sensitive-data exclusion list (logical: `sandbox-span-sensitive-data-exclusions`).

**Signatures:**

```
enum SpanEventKind {
  SANDBOX_ENTER,
  TOOL_CALL,
  SANDBOX_VIOLATION,
  SANDBOX_TIER_ESCALATION,
  SANDBOX_EXIT
}

record SandboxSpanEvent {
  kind            : SpanEventKind
  parent_span_id  : SpanId
  attributes      : Map<string, AttributeValue>
  timestamp       : MonotonicTimestamp
}

const SANDBOX_ENTER_ATTRIBUTES: Set<string>
const SANDBOX_VIOLATION_ATTRIBUTES: Set<string>
const SANDBOX_TIER_ESCALATION_ATTRIBUTES: Set<string>
const SANDBOX_EXIT_ATTRIBUTES: Set<string>

const SENSITIVE_DATA_EXCLUSIONS: Set<string> = {
  "sandbox_resident_filesystem_state",
  "sandbox_resident_screenshot_context",
  "tool_io_raw_content",
  "secret_value"
}

function emit_sandbox_event(event: SandboxSpanEvent) -> EmissionResult
function validate_span_attributes_against_exclusions(attrs) -> ValidationResult
```

**Acceptance criteria:**
1. Span hierarchy matches §15.1 verbatim: `subagent.span[i] → sandbox.enter → tool.call[] / sandbox.violation / sandbox.tier_escalation / sandbox.exit`.
2. Each `SpanEventKind` carries attribute set per its constant; presence on wrong event kind is contract violation.
3. `sandbox.enter` carries 10 attributes (tier, tech, provider, policy.assigned_tier_reason, deployment_surface, blast_radius_tier, mcp_transport, cold_start_ms, pool_acquired, persona_tier); `sandbox.violation` carries 1+; `sandbox.tier_escalation` carries 3 (from_tier, to_tier, escalation_cause); `sandbox.exit` carries 5.
4. `SENSITIVE_DATA_EXCLUSIONS` contains four entries; `validate_span_attributes_against_exclusions` rejects spans carrying exclusion-set attributes.
5. T-perm-2 surface exclusion per §15.5 row 2: sandbox-resident filesystem state + screenshot context structurally excluded.
6. Structure-not-content invariant per §15.5 row 1: span attributes never carry raw tool I/O content.
7. Composition with C-AS-08 per §15.5 row 3: sandbox-violation tamper-evidence emits audit-ledger entry via C-AS-08 (Cluster 6).
8. Parent-span linkage per §15.1: `sandbox.enter` parented under `subagent.span[i]` or `tool.call` root.

**Tests:** `test_span_event_kind_cardinality_five`, `test_sandbox_enter_attributes_set_per_spec_15_1`, `test_sandbox_violation_attributes_include_fail_class`, `test_sandbox_tier_escalation_attributes_per_spec`, `test_sandbox_exit_attributes_per_spec`, `test_sensitive_data_exclusions_cardinality_four`, `test_validate_rejects_sandbox_resident_filesystem_state`, `test_validate_rejects_screenshot_context`, `test_validate_rejects_tool_io_raw_content`, `test_validate_rejects_secret_value`, `test_validate_accepts_structure_only_attributes`, `test_parent_span_linkage_per_spec_hierarchy`.

**Rollback boundary:** Revert `SpanEventKind` + span shape + attribute sets + sensitive-data exclusions. Sandbox-bounded observability surface lost; OD plan ingestion has no span schema to consume.

#### U-AS-18 — Sampling discipline for sandbox events + audit-floor commitments

**Implements:** [C-AS-15 §15.4]

**Depends on:** [U-AS-17]

**Inputs:** Span emission events per U-AS-17; deployment-binding-time sampling configuration.

**Files affected:** AS-axis sandbox event sampling policy module (logical: `sandbox-event-sampling-policy`).

**Signatures:**

```
enum SamplingPosture {
  BASE_RATE_MATCHES_PARENT,
  ALWAYS_SAMPLED_HEAD_1_0,
  ALWAYS_SAMPLED_WITH_TAIL_KEEP
}

const SAMPLING_POLICY: Map<SpanEventKind, SamplingPosture> = {
  SANDBOX_ENTER:            BASE_RATE_MATCHES_PARENT,
  SANDBOX_EXIT:             BASE_RATE_MATCHES_PARENT,
  SANDBOX_VIOLATION:        ALWAYS_SAMPLED_WITH_TAIL_KEEP,
  SANDBOX_TIER_ESCALATION:  ALWAYS_SAMPLED_HEAD_1_0
}

function sampling_posture(kind: SpanEventKind) -> SamplingPosture
function is_operator_tunable_at_base_rate(kind: SpanEventKind) -> bool
function audit_floor_violated(proposed_policy) -> bool
```

**Acceptance criteria:**
1. Per-event sampling per §15.4 verbatim (enter/exit: base-rate-matches-parent; violation: always-sampled-with-tail-keep; tier_escalation: always-sampled-head-1.0).
2. Always-sampled posture for violation + tier_escalation is hard floor at deployment-binding layer; not operator-tunable at base-rate.
3. `audit_floor_violated` returns true when proposed policy downgrades ALWAYS_SAMPLED_* to BASE_RATE for violation/tier_escalation.
4. `sandbox.enter`/`sandbox.exit` base-rate inheritance from parent `tool.call`.
5. Cost-attribution-per-sandbox-instance via `sandbox.cost.tier_overhead_*` at `sandbox.exit` follows base-rate; per-cell rollup at fan-out close (CP plan Session 3).
6. `tail-keep-on-classification=true` for sandbox.violation per §15.4 row 3.

**Tests:** `test_sampling_policy_cardinality_four`, `test_sandbox_enter_base_rate_matches_parent`, `test_sandbox_exit_base_rate_matches_parent`, `test_sandbox_violation_always_sampled_with_tail_keep`, `test_sandbox_tier_escalation_always_sampled_head_1_0`, `test_is_operator_tunable_at_base_rate_returns_true_for_enter_exit`, `test_is_operator_tunable_at_base_rate_returns_false_for_violation_escalation`, `test_audit_floor_violated_detects_downgrade_attempt`, `test_audit_floor_violated_returns_false_for_compliant_policy`.

**Rollback boundary:** Revert sampling policy + audit-floor enforcement. Sandbox events fall back to default base-rate sampling; audit-floor commitments lost; sandbox.violation + sandbox.tier_escalation become operator-tunable to base-rate; compliance posture breaks.

#### U-AS-19 — Cross-axis idempotency-key composition + sub-agent boundary inheritance + cost-attribution joining

**Implements:** [C-AS-15 §15.6]

**Depends on:** [U-AS-09, U-AS-17, U-IS-07 (cross-axis: IS), U-IS-12 (cross-axis: IS)]

**Inputs:** `idempotency_key` from `StateLedgerEntry` per C-IS-05 (carried by U-IS-07 — STATE_LEDGER_ENTRY_SHAPE_EXPORT per U-IS-17 §10.1); `idempotency_key` join-key contract per C-IS-10 §10.2 (carried by U-IS-07 + U-IS-12); parent `tool.call` span.

**Files affected:** AS-axis sandbox-event idempotency-key composition module (logical: `sandbox-event-idempotency-key-composition`); sub-agent idempotency-key derivation (logical: `sub-agent-idempotency-key-derivation`); cost-attribution join module (logical: `sandbox-cost-attribution-join`).

**Signatures:**

```
function attach_idempotency_key_to_sandbox_event(
  event: SandboxSpanEvent,
  parent_tool_call_idempotency_key: IdempotencyKey
) -> SandboxSpanEvent

function derive_sub_agent_idempotency_key(
  parent_idempotency_key: IdempotencyKey,
  sub_agent_dispatch_id: SubAgentDispatchId
) -> IdempotencyKey

interface SubAgentKeyDerivationStrategy {
  derive: (IdempotencyKey, SubAgentDispatchId) -> IdempotencyKey
}

function join_cost_attribution_by_idempotency_key(
  sandbox_exit_events: List<SandboxSpanEvent>
) -> Map<IdempotencyKey, CostAttribution>

record CostAttribution {
  idempotency_key            : IdempotencyKey
  total_tier_overhead_ms     : int
  total_tier_overhead_usd    : float
  contributing_event_count   : int
}
```

**Acceptance criteria:**
1. Every sandbox event on a `tool.call` parent carries the parent's `idempotency_key` per §15.6 row 1.
2. `idempotency_key` on `SandboxSpanEvent` resolves to the field on parent `StateLedgerEntry` per C-IS-05 (consumed via U-IS-07).
3. Cross-axis join contract per C-IS-10 §10.2 (U-IS-07, U-IS-12): sandbox-violation events join with state-ledger entries on identical `idempotency_key`; cost-attribution events join with sandbox-exit events.
4. Sub-agent boundary inheritance per §15.6 row 2: derived `idempotency_key` at sub-agent dispatch via `SubAgentKeyDerivationStrategy`; strategy filled by CP plan per ADR-D4 v1.1 §1.9.
5. `join_cost_attribution_by_idempotency_key` aggregates `sandbox.cost.tier_overhead_*` per §15.6 row 3; consumed at D6 cost-attribution dashboarding (OD plan Session 4).
6. `idempotency_key` opacity per C-IS-10 §10.2: this unit treats key as opaque; construction lives at C-IS-07 §7.1 + Cluster 4 §2.2.7 [HIGH].
7. F2-12 carry-forward acknowledgment per IS plan §[carry-forwards] [CF-1]: `idempotency_key` join behavior uniform across replay scenarios; AS plan does not engage F2-12 directly.
8. Sub-agent boundary violation per U-AS-09: `sandbox.tier_escalation` event composes derived sub-agent key.

**Tests:** `test_attach_idempotency_key_propagates_from_parent`, `test_idempotency_key_is_opaque_join_key`, `test_derive_sub_agent_idempotency_key_uses_strategy_interface`, `test_sub_agent_idempotency_key_differs_from_parent`, `test_sub_agent_idempotency_key_deterministic_per_dispatch_id`, `test_join_cost_attribution_aggregates_per_idempotency_key`, `test_join_cost_attribution_separates_keys`, `test_cross_axis_state_ledger_entry_shape_compatible`, `test_f2_12_uniform_across_replay_scenarios`.

**Rollback boundary:** Revert idempotency-key composition + sub-agent derivation + cost-attribution join. Sandbox events lose `idempotency_key`; cross-axis correlation with state-ledger entries (D1, D5, D6) breaks; cost-attribution dashboarding loses join surface.

---

### §2.5 Cluster 5 — F5 secret-fetch surface (C-AS-05 + C-AS-06 + C-AS-07)

#### U-AS-20 — Declare `fetch_secret` signature + `SecretRef` opaque type + tier-aware resolution mechanism table

**Implements:** [C-AS-05 §5.1, §5.2, §5.4]

**Depends on:** [U-AS-01]

**Inputs:** Secret identifier (`name`) and scope (`SecretScope`); resolved sandbox tier per call site (per U-AS-08).

**Files affected:** AS-axis secret-fetch type declarations (logical: `secret-fetch-type-declarations`); secret-fetch API surface (logical: `secret-fetch-api-surface`); tier-aware resolution mechanism table (logical: `tier-aware-secret-resolution-table`).

**Signatures:**

```
opaque type SecretRef                            // no value-accessor API per §5.4
record SecretScope { ... }                        // serialization deferred

enum SecretResolutionMechanism {
  ENV_VAR_AT_SANDBOX_STARTUP,
  CONTAINER_ENV_VAR_WITH_KEYRING_HANDLES,
  IN_SANDBOX_HTTP_BOOTSTRAP_TOKEN,
  IN_SANDBOX_HTTP_WITH_ROTATION_REFRESH
}

enum TPerm2Pole { C2_WITHIN_TURN_SNAPSHOT, C3_ACROSS_TURN_FRESH_FETCH }

record TierResolutionMechanism {
  tier            : SandboxTier
  mechanism       : SecretResolutionMechanism
  pole_expressed  : TPerm2Pole
}

const TIER_RESOLUTION_TABLE: List<TierResolutionMechanism>      // exactly 4 entries

function fetch_secret(name: string, scope: SecretScope, tier: SandboxTier) -> SecretRef
function tier_resolution_mechanism(tier: SandboxTier) -> TierResolutionMechanism
```

**Acceptance criteria:**
1. `fetch_secret(name, scope)` signature matches §5.1 verbatim; `tier` injected by U-AS-08.
2. `SecretRef` opaque per §5.4 row 1: no value-accessor API.
3. `SecretRef` lifetime bounded by sandbox lifetime per §5.4 row 2; cross-sandbox sharing prohibited.
4. `SecretRef` fresh-on-restart per §5.4 row 3: no in-process cache across restarts.
5. `TIER_RESOLUTION_TABLE` declares four entries per §5.2 verbatim:
   - TIER_1_PROCESS → ENV_VAR_AT_SANDBOX_STARTUP / C2
   - TIER_2_CONTAINER → CONTAINER_ENV_VAR_WITH_KEYRING_HANDLES / C2
   - TIER_3_MICROVM → IN_SANDBOX_HTTP_BOOTSTRAP_TOKEN / C3
   - TIER_4_FULL_VM → IN_SANDBOX_HTTP_WITH_ROTATION_REFRESH / C3
6. T-perm-2 F5-layer closure: tier choice picks pole; both poles expressed; structural composition with F4.
7. `tier_resolution_mechanism` total over `SandboxTier`.

**Tests:** `test_secret_ref_no_value_accessor_api`, `test_secret_ref_lifetime_bounded_to_sandbox`, `test_secret_ref_no_cross_sandbox_sharing`, `test_tier_resolution_table_cardinality_four`, `test_tier_resolution_mechanism_per_spec_row_by_row`, `test_tier_1_process_pole_is_c2_within_turn`, `test_tier_3_microvm_pole_is_c3_across_turn`, `test_fetch_secret_signature_matches_spec`.

**Rollback boundary:** Revert `SecretRef` + `SecretScope` + `TIER_RESOLUTION_TABLE` + `fetch_secret` signature. All downstream secret-handling units (U-AS-21, U-AS-22, U-AS-23, U-AS-24, Cluster 6) lose foundational surface; secrets handling subsystem invalidated.

#### U-AS-21 — Enforce negative-observation invariants (secrets absent from prompts, logs, ledger)

**Implements:** [C-AS-05 §5.3]

**Depends on:** [U-AS-17, U-AS-20]

**Inputs:** Surface-emission events at prompt-cache construction (cross-axis to CP), span emission (U-AS-17), audit-ledger write (cross-axis to IS at Cluster 6).

**Files affected:** AS-axis negative-observation invariant validator (logical: `secret-negative-observation-validator`); sole-resolution-path enforcement guard (logical: `secret-sole-resolution-path-guard`).

**Signatures:**

```
enum NegativeObservationSurface {
  STATIC_PROMPT_CACHE_PREFIX,
  SPAN_ATTRIBUTES,
  LOG_RECORDS,
  AUDIT_LEDGER_ENTRY
}

record NegativeObservationViolation {
  surface       : NegativeObservationSurface
  detected_at   : string
  invariant     : string
}

function validate_no_secret_in_static_prefix(prefix_content) -> Optional<NegativeObservationViolation>
function validate_no_secret_in_span_attributes(attributes) -> Optional<NegativeObservationViolation>
function validate_no_secret_in_audit_ledger_entry(entry) -> Optional<NegativeObservationViolation>
function verify_sole_resolution_path(secret_arrival_site) -> Optional<NegativeObservationViolation>
```

**Acceptance criteria:**
1. Four invariants enforced per §5.3:
   - Absence in stored prompts (static prompt cache prefix)
   - Absence in log surfaces (span attributes, log records)
   - Absence in ledger (audit-ledger entries; structure-not-content fingerprint per C-AS-08)
   - Sole resolution path (only `fetch_secret` reaches a sandbox)
2. `validate_no_secret_in_static_prefix` consumes prompt-cache prefix; detection mechanism implementation discretion.
3. `validate_no_secret_in_span_attributes` composes with U-AS-17 `SENSITIVE_DATA_EXCLUSIONS`.
4. `verify_sole_resolution_path` enforces no manifest/prompt/log/ledger delivery of secret content.
5. Violation events emit `sandbox.violation` with `sandbox.fail.class = POLICY_OVERRIDE` (Cluster 4 emission).

**Tests:** `test_validate_no_secret_in_static_prefix_detects_known_pattern`, `test_validate_no_secret_in_static_prefix_passes_clean_prefix`, `test_validate_no_secret_in_span_attributes_composes_with_u_as_17_exclusions`, `test_validate_no_secret_in_audit_ledger_entry_detects_value_content`, `test_verify_sole_resolution_path_rejects_manifest_arrival`, `test_verify_sole_resolution_path_accepts_fetch_secret_arrival`.

**Rollback boundary:** Revert invariant validators + sole-resolution-path guard. Secrets handling loses structural prohibition enforcement at prompt/log/ledger surfaces; manifest/static-prefix secret-leak silently permitted; compliance posture breaks.

#### U-AS-22 — Declare `SecretAllowlistEntry` + extend `ToolContract.required_secrets` + access-control composition

**Implements:** [C-AS-06 §6.1, §6.2]

**Depends on:** [U-AS-07, U-AS-20]

**Inputs:** Tool contract serialization; `fetch_secret(name, scope)` call site.

**Files affected:** AS-axis secret-allowlist entry type declaration (logical: `secret-allowlist-entry-type-declaration`); tool-contract required-secrets field extension (logical: `tool-contract-required-secrets-extension`); allowlist-intersection access-control module (logical: `secret-allowlist-intersection-access-control`).

**Signatures:**

```
record SecretAllowlistEntry {
  name   : string
  scope  : SecretScope
}

// Populates the previously-empty-shape field on ToolContract at U-AS-07
ToolContract.required_secrets : List<SecretAllowlistEntry>

enum AllowlistDecision {
  PERMITTED,
  DENIED_NOT_IN_TOOL_ALLOWLIST,
  DENIED_NOT_IN_OPERATOR_POLICY_OVERRIDE
}

function check_secret_allowlist(
  tool: ToolContract,
  requested_name: string,
  requested_scope: SecretScope,
  operator_policy_override: Set<SecretAllowlistEntry>
) -> AllowlistDecision
```

**Acceptance criteria:**
1. `SecretAllowlistEntry` carries exactly two fields per §6.1 verbatim.
2. `ToolContract.required_secrets` at U-AS-07 populated with `List<SecretAllowlistEntry>`; empty list default.
3. Allowlist intersection per §6.2 row 1: PERMITTED ⇔ (name, scope) ∈ tool.required_secrets ∩ operator_policy_override.
4. `required_secrets` orthogonal to sandbox tier per §6.2 row 2: not a fifth `max()` floor; does NOT enter C-AS-02 composition.
5. Authoring-time declarable per §6.2 row 3; empty list permitted.
6. Audit composition per §6.2 row 4: successful `fetch_secret` emits audit-ledger entry per C-AS-08 (Cluster 6).
7. Operator-policy override scope is implementation-discretion (per-call vs cached per-session).

**Tests:** `test_secret_allowlist_entry_two_fields_only`, `test_required_secrets_empty_list_permitted`, `test_required_secrets_missing_field_treated_as_empty`, `test_check_allowlist_permitted_when_in_both_sets`, `test_check_allowlist_denied_when_not_in_tool`, `test_check_allowlist_denied_when_not_in_operator_policy`, `test_required_secrets_orthogonal_to_sandbox_tier`.

**Rollback boundary:** Revert allowlist entry + `ToolContract.required_secrets` field population + intersection module. Tools can call `fetch_secret` for any (name, scope) without authoring-time declaration; access-control discipline breaks.

#### U-AS-23 — Enforce secret-passthrough constraints (output redaction + input redaction + MCP passthrough prohibition)

**Implements:** [C-AS-06 §6.3]

**Depends on:** [U-AS-17, U-AS-20, U-AS-22]

**Inputs:** Tool input/output at sandbox boundary; MCP server invocations with upstream forwarding.

**Files affected:** AS-axis output redaction (logical: `secret-passthrough-output-redaction`); input redaction (logical: `secret-passthrough-input-redaction`); MCP passthrough prohibition guard (logical: `mcp-server-secret-passthrough-prohibition-guard`).

**Signatures:**

```
enum PassthroughViolationKind {
  OUTPUT_CONTAINS_SECRET_MATERIAL,
  INPUT_SPAN_ATTRIBUTE_CONTAINS_SECRET_MATERIAL,
  MCP_SERVER_FORWARDED_TOKEN_UPSTREAM
}

record PassthroughViolation {
  kind            : PassthroughViolationKind
  detection_site  : string
  redaction_applied : bool
}

function redact_secrets_in_output(output: ToolOutput) -> ToolOutput
function redact_secrets_in_input_span_attributes(attributes) -> Map<string, AttributeValue>
function detect_mcp_server_token_passthrough(mcp_call_record) -> Optional<PassthroughViolation>
```

**Acceptance criteria:**
1. Output redaction per §6.3 row 1 at C-AS-15 span-emission boundary; structure-not-content discipline.
2. Input redaction per §6.3 row 2: span attributes redacted; resolved secret only inside sandbox at tier-specific resolution per U-AS-20 §5.2.
3. MCP-server passthrough prohibition per §6.3 row 3 + MCP authorization spec 2025-06-18 [HIGH]: cross-server secret-leak structurally prohibited.
4. `detect_mcp_server_token_passthrough` returns Some when MCP server forwards client-issued token to upstream API.
5. Redaction non-blocking; structure-not-content preserved at C-AS-15 emission.
6. Composition with U-AS-22 allowlist: redaction applies to `fetch_secret`-resolved values; no other secret-arrival path per U-AS-21.
7. Passthrough violation emits `sandbox.fail.class = EGRESS_DENIED` per U-AS-03.

**Tests:** `test_redact_secrets_in_output_replaces_secret_material`, `test_redact_secrets_in_output_preserves_non_secret_content`, `test_redact_secrets_in_input_span_attributes_redacts_secret_attribute_values`, `test_detect_mcp_server_token_passthrough_detects_forwarded_token`, `test_detect_mcp_server_token_passthrough_no_violation_on_distinct_upstream_token`, `test_passthrough_violation_emits_egress_denied_class`.

**Rollback boundary:** Revert redaction modules + MCP passthrough guard. Tool outputs and span attributes may carry secret content; MCP cross-server secret-leak silently permitted; lethal-trifecta architectural cut breaks.

#### U-AS-24 — Declare `SecretFailClass` enum + per-class C5/C9 metadata + per-`(secret_backend, scope)` breaker placement

**Implements:** [C-AS-07 §7.1, §7.2, §7.3]

**Depends on:** [U-AS-03, U-AS-20]

**Inputs:** Secret-fetch invocation result (SUCCESS / FAILURE); breaker key construction at per-(secret_backend, scope) granularity.

**Files affected:** AS-axis secret-fetch fail-class type declaration (logical: `secret-fail-class-type-declaration`); per-class metadata table (logical: `secret-fail-class-routing-metadata`); per-(secret_backend, scope) breaker key construction (logical: `secret-backend-scope-breaker-key-construction`).

**Signatures:**

```
enum SecretFailClass {
  SECRET_UNKNOWN      = "secret_unknown",
  SECRET_UNAVAILABLE  = "secret_unavailable",
  SECRET_EXPIRED      = "secret_expired",
  SECRET_LOCKED       = "secret_locked",
  SECRET_REVOKED      = "secret_revoked"
}

enum SecretC5FailClass { PERMANENT_FAIL, TRANSIENT_FAIL, REFLEXION_RECOVERABLE, HITL_RECOVERABLE }
enum SecretC9RetryPosture {
  NO_RETRY_ROUTE_TO_HITL,
  C9_BACKOFF_RETRY_WITH_BACKEND_BREAKER,
  REFRESH_AND_RETRY_PRESERVING_IDEMPOTENCY_KEY,
  WORKLOAD_MODE_AWARE_EPHEMERAL_FAIL_FAST_OR_DURABLE_PAUSE
}

record SecretFailClassMetadata {
  fail_class             : SecretFailClass
  c5_classification      : SecretC5FailClass
  c9_retry_posture       : SecretC9RetryPosture
  orthogonal_to_sandbox  : bool
}

record SecretBackendBreakerKey {
  secret_backend : string
  scope          : SecretScope
}

function fail_class_metadata(c: SecretFailClass) -> SecretFailClassMetadata
function construct_breaker_key(backend: string, scope: SecretScope) -> SecretBackendBreakerKey
```

**Acceptance criteria:**
1. `SecretFailClass` carries exactly five values per §7.1 verbatim snake_case.
2. Per-class metadata matches §7.1 table verbatim:
   - SECRET_UNKNOWN → PERMANENT_FAIL / NO_RETRY_ROUTE_TO_HITL
   - SECRET_UNAVAILABLE → TRANSIENT_FAIL / C9_BACKOFF_RETRY_WITH_BACKEND_BREAKER
   - SECRET_EXPIRED → REFLEXION_RECOVERABLE / REFRESH_AND_RETRY_PRESERVING_IDEMPOTENCY_KEY
   - SECRET_LOCKED → HITL_RECOVERABLE / WORKLOAD_MODE_AWARE_EPHEMERAL_FAIL_FAST_OR_DURABLE_PAUSE
   - SECRET_REVOKED → HITL_RECOVERABLE / WORKLOAD_MODE_AWARE_*
3. Orthogonality with `sandbox.fail.class` per §7.2: independent enums; compose at C-AS-15 span-emission layer.
4. SECRET_EXPIRED idempotency-key preservation per §7.1 row 3: refresh-and-retry preserves key across attempt.
5. SECRET_LOCKED + SECRET_REVOKED workload-mode-aware per §7.1 rows 4-5; ephemeral fail-fast vs durable pause-and-wait per ADR-F3.
6. Per-`(secret_backend, scope)` breaker per §7.3: analog of F1 per-(provider, model) breaker; trip on SECRET_UNAVAILABLE rate; trip behavior is advance-fallback OR fail-closed.
7. `construct_breaker_key` deterministic; identical inputs produce identical keys.

**Tests:** `test_secret_fail_class_cardinality_five`, `test_secret_fail_class_identifier_strings_snake_case_byte_exact`, `test_secret_fail_class_metadata_table_per_spec_row_by_row`, `test_orthogonal_to_sandbox_uniform_true`, `test_secret_expired_routes_refresh_and_retry`, `test_secret_locked_and_revoked_route_workload_mode_aware`, `test_secret_unknown_routes_no_retry_to_hitl`, `test_construct_breaker_key_deterministic`, `test_construct_breaker_key_distinct_for_different_backend`, `test_construct_breaker_key_distinct_for_different_scope`.

**Rollback boundary:** Revert `SecretFailClass` + metadata + breaker key construction. Secret-fetch failures lack structured classification; per-backend breaker discipline breaks; rate-limit storms possible.

---

### §2.6 Cluster 6 — F5 secret-fetch audit composition (C-AS-08)

#### U-AS-25 — Implement `outputs_hash` structure-not-content fingerprint formula

**Implements:** [C-AS-08 §8.1]

**Depends on:** [U-AS-20, U-IS-08 (cross-axis: IS)]

**Inputs:** Secret-fetch event metadata: `secret.name`, `secret.scope`, `secret.last_rotated_at`.

**Files affected:** AS-axis outputs-hash formula composition module (logical: `secret-fetch-outputs-hash-formula`).

**Signatures:**

```
function compute_outputs_hash(
  secret_name: string,
  secret_scope: SecretScope,
  secret_last_rotated_at: ISO8601Timestamp
) -> Bytes32
  // outputs_hash = SHA-256(canonicalize_concat(secret_name, secret_scope, secret_last_rotated_at))
  // canonicalize_concat is C-IS-06 §6.1 canonicalization from U-IS-08

function canonicalize_concat_secret_fingerprint(
  secret_name: string,
  secret_scope: SecretScope,
  secret_last_rotated_at: ISO8601Timestamp
) -> Bytes
```

**Acceptance criteria:**
1. `compute_outputs_hash` implements §8.1 formula verbatim; return 32 bytes.
2. `canonicalize_concat_secret_fingerprint` delegates to U-IS-08's `canonicalize` per §8.1 ("`canonicalize_concat` is the canonicalization function per C-IS-06 §6.1").
3. Three input fields capture structure only; secret value never enters function input — sensitive-data default-off discipline enforced at signature.
4. Determinism per C-IS-06 §6.1 (via U-IS-08): byte-identical output for logically-equal triples across runs.
5. Collision resistance per SHA-256.
6. Composition: consumed by U-AS-26 to populate `response_hash` per §8.2 row 4.

**Tests:** `test_compute_outputs_hash_length_32_bytes`, `test_compute_outputs_hash_deterministic_same_invocation`, `test_compute_outputs_hash_uses_canonicalize_concat_from_u_is_08`, `test_compute_outputs_hash_collision_smoke`, `test_compute_outputs_hash_rotation_changes_hash`, `test_compute_outputs_hash_scope_separation`, `test_compute_outputs_hash_no_value_input`, `test_compute_outputs_hash_library_binding_flex`.

**Rollback boundary:** Revert formula. U-AS-26 cannot populate `response_hash`; secret-fetch audit-ledger entries lose structure-not-content fingerprint; rotation-detection and tamper-evidence break.

#### U-AS-26 — Compose secret-fetch audit-ledger entry against C-IS-05 entry shape + C-IS-06 hash-chain integrity

**Implements:** [C-AS-08 §8.2, §8.3]

**Depends on:** [U-AS-25, U-IS-07 (cross-axis: IS), U-IS-09 (cross-axis: IS), U-IS-10 (cross-axis: IS)]

**Inputs:** Secret-fetch event (name, scope, last_rotated_at, actor, timestamp); prior ledger entry (Optional); idempotency_key construction per C-IS-07 §7.1.

**Files affected:** AS-axis secret-fetch audit-ledger entry composer (logical: `secret-fetch-audit-entry-composer`); hash-chain participation module (logical: `secret-fetch-hash-chain-participation`).

**Signatures:**

```
record SecretFetchEvent {
  secret_name           : string
  secret_scope          : SecretScope
  secret_last_rotated_at: ISO8601Timestamp
  actor                 : Actor                    // from U-IS-07
  timestamp             : Timestamp                // from U-IS-07
  thread_id             : Identifier
  step_id               : Identifier
}

function compose_secret_fetch_audit_entry(
  event: SecretFetchEvent,
  prior_entry: Optional<StateLedgerEntry>
) -> StateLedgerEntry

function verify_secret_fetch_entry_in_chain(
  entry: StateLedgerEntry,
  ledger_position: int,
  full_ledger: List<StateLedgerEntry>
) -> ChainVerificationResult
```

**Acceptance criteria:**
1. Returned `StateLedgerEntry` conforms to U-IS-07 six-field shape; no AS-side additions per §8.2.
2. Per-field population matches §8.2 table verbatim:
   - `action_id` = harness-generated unique ID
   - `idempotency_key` = (thread_id, step_id, idempotency_key) per Stripe-style per C-IS-07 §7.1
   - `actor` = event.actor
   - `response_hash` = `compute_outputs_hash(name, scope, last_rotated_at)` from U-AS-25
   - `timestamp` = event.timestamp (monotonic non-decreasing)
   - `prior_event_hash` = `construct_prior_event_hash(prior_entry)` from U-IS-09
3. Hash-chain participation per §8.3 row 1 via U-IS-09.
4. Tamper-evidence per §8.3 row 2: five tamper scenarios per C-IS-06 §6.5 covered by U-IS-10 test suite.
5. Verification surface per §8.3 row 3: `verify_secret_fetch_entry_in_chain` delegates to U-IS-10.
6. Idempotency-key construction per C-IS-07 §7.1: `sha256(conversation_id || step_index || tool || canonical_args)` plus secret-fetch metadata; construction delegated to U-IS-11.
7. Secret-fetch entries indistinguishable from other entries at schema level (six-field uniform).
8. Inception handling: `prior_entry = None` → `prior_event_hash = ALL_ZEROS_SENTINEL`.

**Tests:** `test_compose_audit_entry_six_field_shape`, `test_compose_audit_entry_response_hash_from_u_as_25`, `test_compose_audit_entry_prior_event_hash_from_u_is_09`, `test_compose_audit_entry_inception_sentinel`, `test_compose_audit_entry_actor_preservation`, `test_compose_audit_entry_idempotency_key_uses_thread_step`, `test_verify_secret_fetch_entry_in_chain_delegates_to_u_is_10`, `test_compose_audit_entry_schema_uniform_with_non_secret_entries`, `test_compose_audit_entry_negative_no_secret_value_field`.

**Rollback boundary:** Revert audit-entry composer + chain-participation module. Secret-fetch events cannot produce StateLedgerEntry records; downstream ledger writes fail; hash-chain tamper-evidence breaks; compliance posture breaks.

#### U-AS-27 — Per-fetch emission discipline + span emission alongside + cross-axis composition reference

**Implements:** [C-AS-08 §8.4, §8.5]

**Depends on:** [U-AS-17, U-AS-22, U-AS-24, U-AS-26, U-IS-11 (cross-axis: IS)]

**Inputs:** `fetch_secret(name, scope)` call result; call-site context (actor, thread_id, step_id).

**Files affected:** AS-axis secret-fetch emission orchestrator (logical: `secret-fetch-audit-emission-orchestrator`); span emission composer (logical: `secret-fetch-span-emission`); cross-axis composition reference table (logical: `secret-fetch-audit-cross-axis-references`).

**Signatures:**

```
enum FetchOutcome { SUCCESS(SecretRef), FAILURE(SecretFailClass) }

function emit_secret_fetch_audit(
  outcome: FetchOutcome,
  event_metadata: SecretFetchEvent,
  call_site_context: CallSiteContext
) -> EmissionResult

record SecretFetchSpanAttributes {
  name                          : string
  scope                         : SecretScope
  backend                       : string
  fail_class                    : Optional<SecretFailClass>
  cache_tier_overhead_ms        : int
  policy_access_decision_reason : string
}

function emit_secret_fetch_span(
  outcome: FetchOutcome,
  span_attrs: SecretFetchSpanAttributes,
  parent_span_id: SpanId
) -> EmissionResult
```

**Acceptance criteria:**
1. Per-fetch emission per §8.4 row 1: SUCCESS → exactly one ledger entry.
2. Per-fail emission per §8.4 row 2: FAILURE → exactly one entry with `secret.fail.class` per U-AS-24.
3. Span emission alongside per §8.4 row 3 + ADR-F5 v1.1 §Consequences (c): six-attribute D-derivative span schema (`secret.name`, `secret.scope`, `secret.backend`, `secret.fail.class`, `secret.cache.tier_overhead_ms`, `secret.policy.access_decision_reason`).
4. Negative-observation per §8.4 row 4: ledger entry + span carry structure, never secret value; validated by U-AS-21.
5. Write contract per §8.4 + C-IS-07 §7.1: ledger write delegates to U-IS-11; idempotency on (thread_id, step_id, idempotency_key); duplicate writes no-op.
6. Emission ordering: ledger entry write precedes span emission; partial emission prohibited; write failure blocks span emission.
7. Cross-axis composition reference per §8.5:
   - IS (C-IS-10 §10.1): F2 state-ledger entry shape exports to AS; this contract is consumption surface
   - OD (D5 v1.3 §1.4 audit-ledger cryptographic shape per persona-tier): per-persona-tier signature extensions compose at OD plan Session 4
8. Cross-axis reference is documentation; no executable behavior beyond audit-entry emission.
9. Composition with U-AS-22 allowlist: emission only for PERMITTED `fetch_secret`; denied calls don't reach this unit.

**Tests:** `test_emit_audit_one_entry_per_successful_fetch`, `test_emit_audit_one_entry_per_failed_fetch`, `test_emit_audit_n_successive_fetches_n_entries`, `test_emit_span_alongside_ledger_entry`, `test_emit_span_attributes_six_fields_per_d_derivative_schema`, `test_emit_span_no_secret_value_attribute`, `test_emit_audit_ledger_entry_no_secret_value`, `test_emit_audit_writes_via_u_is_11_write_contract`, `test_emit_audit_idempotency_on_thread_step_key`, `test_emit_audit_write_failure_blocks_span_emission`, `test_emit_audit_only_for_allowlist_permitted_fetches`.

**Rollback boundary:** Revert emission orchestrator + span emission + cross-axis reference. Secret-fetch events do not produce audit-ledger entries; ledger-based tamper-evidence over secret-fetch breaks; observability surface loses secret-fetch attribution; compliance posture breaks.

---

### §2.7 Cluster 7 — D3 Anthropic-primitive adoption (C-AS-13 + C-AS-14)

#### U-AS-28 — Declare eleven-primitive enumeration + per-primitive × workload-class adoption-depth matrix

**Implements:** [C-AS-13 §13.1, §13.2]

**Depends on:** [U-AS-04, U-IS-01 (cross-axis: IS), U-IS-02 (cross-axis: IS)]

**Inputs:** None (foundational enumeration + matrix declaration).

**Files affected:** AS-axis Anthropic-primitive enumeration (logical: `anthropic-primitive-enum-declaration`); adoption-depth matrix (logical: `primitive-workload-class-adoption-matrix`); Skills primitive filesystem-loading binding (logical: `skills-primitive-filesystem-loading-binding`).

**Signatures:**

```
enum AnthropicPrimitive {
  SKILLS_SYSTEM, MCP_AS_CODE, MANAGED_AGENTS, PER_ROLE_MODEL_BINDING,
  PROMPT_CACHE_BREAKPOINT_PLACEMENT, EXTENDED_THINKING_BUDGET, BATCH_API,
  CLAUDE_CODE_HOOKS, CLAUDE_MD_AGENTS_MD_CONVENTION, FILES_API, MEMORY_TOOL
}

enum WorkloadClass { SOFTWARE_ENGINEERING, CONTENT_CREATION, PIPELINE_AUTOMATION, RESEARCH }
enum AdoptionDepth { REQUIRED, RECOMMENDED, OPTIONAL, EXCLUDED }

record AdoptionDepthBinding {
  primitive          : AnthropicPrimitive
  workload_class     : WorkloadClass
  depth              : AdoptionDepth
  surface_qualifier  : Optional<DeploymentSurface>
  notes              : Optional<string>
}

const ANTHROPIC_PRIMITIVE_ANCHORS: Map<AnthropicPrimitive, AnchorCitation>
const ADOPTION_DEPTH_MATRIX: Map<(AnthropicPrimitive, WorkloadClass), AdoptionDepthBinding>

function adoption_depth(primitive: AnthropicPrimitive, workload_class: WorkloadClass) -> AdoptionDepthBinding
function skills_loads_from_filesystem_path() -> FilesystemPathContract
```

**Acceptance criteria:**
1. `AnthropicPrimitive` declares exactly 11 values per §13.1 verbatim kebab-case; closed enumeration; adding 12th requires Class-2 ADR-D3 revision.
2. `WorkloadClass` declares exactly 4 values per §13.2 column headers.
3. `AdoptionDepth` declares exactly 4 values (R/r/o/X).
4. `ANTHROPIC_PRIMITIVE_ANCHORS` declares 11 anchor-citation entries per §13.1 with [HIGH]-tagged primary sources.
5. `ADOPTION_DEPTH_MATRIX` declares exactly 44 cells per §13.2 verbatim with surface-conditioning where spec specifies.
6. Per-row population per §13.2 verbatim (Skills system: r/r/R/r uniform; Managed Agents: surface-conditioned with X at local-development; Per-role model binding: R uniform; Files API: surface-conditioned r-managed/hybrid / o-local; Memory tool: per-workload selection with backend per §13.6).
7. Cross-axis IS binding per §13.2 row 1: Skills system loads SKILL.md from filesystem per ADR-D3 v1.2 cache-prefix integrity; `skills_loads_from_filesystem_path` returns canonical path contract from U-IS-01 + U-IS-02; Skills resides in `procedural` artifact tier per C-IS-02.
8. `adoption_depth` total over (AnthropicPrimitive, WorkloadClass).

**Tests:** `test_anthropic_primitive_cardinality_eleven`, `test_anthropic_primitive_identifier_strings_byte_exact_per_spec_13_1`, `test_workload_class_cardinality_four`, `test_adoption_depth_cardinality_four`, `test_anthropic_primitive_anchors_complete`, `test_adoption_depth_matrix_cardinality_44`, `test_adoption_depth_matrix_row_by_row_per_spec_13_2`, `test_managed_agents_excluded_at_local_development`, `test_per_role_model_binding_required_all_workloads`, `test_skills_loads_from_filesystem_via_u_is_01_and_u_is_02`, `test_adoption_depth_total_function`.

**Rollback boundary:** Revert primitive enum + workload-class enum + adoption-depth matrix + Skills filesystem-loading binding. Downstream units lose primitive enumeration anchor; cross-axis composition with IS filesystem-path substrate fails for Skills.

#### U-AS-29 — Per-D1-engine-class composition overlay + per-sub-agent-role × model-binding contract

**Implements:** [C-AS-13 §13.3, §13.4]

**Depends on:** [U-AS-04, U-AS-28, U-IS-01 (cross-axis: IS), U-IS-02 (cross-axis: IS)]

**Inputs:** D1 engine class (resolved at workload binding); workload class + persona tier (call-site context).

**Files affected:** AS-axis per-engine-class composition overlay (logical: `per-engine-class-composition-overlay`); per-sub-agent-role model-binding matrix (logical: `per-sub-agent-role-model-binding`); pre-HITL escalation order metadata (logical: `pre-hitl-escalation-order-metadata`).

**Signatures:**

```
enum D1EngineClass {
  EVENT_SOURCED_REPLAY, SAVE_POINT_CHECKPOINT, PURE_PATTERN_NO_ENGINE,
  RECONCILER_LOOP, WAL_SEGMENT
}

enum SubAgentRole { LEAD_ORCHESTRATOR, GENERATOR, EVALUATOR, REVIEWER, SUB_AGENT }
enum AnthropicModel { HAIKU_4_5, SONNET_4_6, OPUS_4_6, OPUS_4_7 }

record EngineClassComposition {
  engine_class                     : D1EngineClass
  prompt_cache_scope               : string
  batch_api_integration            : string
  extended_thinking_placement      : string
  skills_filesystem_residence      : string
}

const ENGINE_CLASS_COMPOSITION_OVERLAY: Map<D1EngineClass, EngineClassComposition>

record ModelBinding {
  primary_model : AnthropicModel
  qualifier     : Optional<string>
  cap           : Optional<int>
}

const MODEL_BINDING_MATRIX: Map<(WorkloadClass, SubAgentRole), Optional<ModelBinding>>

function model_binding(workload: WorkloadClass, role: SubAgentRole) -> Optional<ModelBinding>

enum PreHITLEscalationStep {
  STEP_1_C9_BACKOFF,
  STEP_2_C6_MODEL_TIER_ESCALATION,
  STEP_3_C11_HITL
}

const PRE_HITL_ESCALATION_ORDER: List<PreHITLEscalationStep>
const MODEL_TIER_ESCALATION_CHAIN: List<AnthropicModel>
```

**Acceptance criteria:**
1. `D1EngineClass` carries exactly 5 values per §13.3 column 1 verbatim.
2. `ENGINE_CLASS_COMPOSITION_OVERLAY` declares 5 rows per §13.3 verbatim (event-sourced-replay → Activity-internal; save-point-checkpoint → Node-internal; pure-pattern-no-engine → Harness-managed; reconciler-loop → CR-cycle-scoped; WAL-segment → Per-segment).
3. Cross-axis IS binding per §13.3 column 5: every engine class references SKILL.md filesystem residence via U-IS-01 + U-IS-02.
4. `SubAgentRole` carries 5 values; `AnthropicModel` carries 4 values.
5. `MODEL_BINDING_MATRIX` declares exactly 20 cells per §13.4 verbatim; `n/a` cells resolve to `None`.
6. Lead-agent brief-authoring NOT reducible to Haiku per §13.4 closing paragraph.
7. `PRE_HITL_ESCALATION_ORDER` declares three-step staircase per §13.4: STEP_1 → C9 backoff; STEP_2 → C6 model-tier escalation; STEP_3 → C11 HITL.
8. `MODEL_TIER_ESCALATION_CHAIN` ascending: HAIKU_4_5 → SONNET_4_6 → OPUS_4_6 → OPUS_4_7.
9. Cross-axis to CP: pre-HITL staircase execution lives at CP plan Session 3.

**Tests:** `test_d1_engine_class_cardinality_five`, `test_engine_class_composition_overlay_per_spec_row_by_row`, `test_skills_filesystem_residence_uniform_across_engine_classes`, `test_sub_agent_role_cardinality_five`, `test_anthropic_model_cardinality_four`, `test_model_binding_matrix_cardinality_20_cells`, `test_model_binding_software_engineering_lead_is_sonnet_4_6_with_opus_qualifier`, `test_model_binding_content_creation_reviewer_is_none`, `test_model_binding_pipeline_automation_evaluator_is_none`, `test_model_binding_research_generator_is_none`, `test_lead_orchestrator_not_reducible_to_haiku`, `test_pre_hitl_escalation_order_three_steps`, `test_model_tier_escalation_chain_ascending`.

**Rollback boundary:** Revert engine-class composition overlay + model-binding matrix + pre-HITL escalation metadata. CP plan loses metadata anchors for engine-class composition + pre-HITL staircase.

#### U-AS-30 — Anthropic-API graceful-degradation per primitive + workload-binding-time selection contract

**Implements:** [C-AS-13 §13.5, §13.6]

**Depends on:** [U-AS-04, U-AS-28, U-AS-29, U-IS-01 (cross-axis: IS), U-IS-02 (cross-axis: IS)]

**Inputs:** Anthropic-API outage signal (per C9 breaker key `(provider=anthropic, model)` — cross-axis CP); workload manifest at workload-binding time.

**Files affected:** AS-axis per-primitive graceful-degradation policy (logical: `per-primitive-graceful-degradation`); workload-binding-time selection procedure (logical: `workload-binding-time-selection-procedure`); Memory tool storage backend selection (logical: `memory-tool-storage-backend-selection`).

**Signatures:**

```
enum OutageBehavior {
  CONTINUES, FALLS_THROUGH_TO_HARNESS_OWNED_TOPOLOGY,
  C6_CROSS_FAMILY_FALLBACK, CACHE_STATE_LOST,
  RUNS_WITHOUT_PRIMITIVE, IN_FLIGHT_RESUME_ON_RECOVERY,
  HARNESS_OWNED_HOOK_LIFECYCLE, CROSS_FAMILY_LOSES_REFERENCES,
  CROSS_FAMILY_COMPATIBLE_VIA_CLIENT_STORAGE
}

record GracefulDegradationPolicy {
  primitive       : AnthropicPrimitive
  outage_behavior : OutageBehavior
  fallback_detail : string
}

const GRACEFUL_DEGRADATION_POLICY: Map<AnthropicPrimitive, GracefulDegradationPolicy>
const C6_CROSS_FAMILY_FALLBACK_CHAIN: List<(Provider, ModelClass)>

enum MemoryToolStorageBackend {
  FILESYSTEM, S3, DATABASE, ENCRYPTED_FILESYSTEM, OPERATOR_DEFINED
}

function memory_tool_storage_backend(deployment_surface: DeploymentSurface) -> Set<MemoryToolStorageBackend>

record WorkloadBindingDecision {
  workload_class           : WorkloadClass
  persona_tier             : PersonaTier
  deployment_surface       : DeploymentSurface
  per_primitive_adoption   : Map<AnthropicPrimitive, AdoptionDepth>
  per_role_model_binding   : Map<SubAgentRole, Optional<ModelBinding>>
  extended_thinking_effort : Map<SubAgentRole, ExtendedThinkingEffort>
  batch_api_cells          : Set<BatchApiCell>
  memory_tool_backend      : Optional<MemoryToolStorageBackend>
}

function compose_workload_binding_decision(
  workload_class: WorkloadClass,
  persona_tier: PersonaTier,
  deployment_surface: DeploymentSurface,
  operator_overrides: WorkloadManifestOverrides
) -> WorkloadBindingDecision
```

**Acceptance criteria:**
1. `GRACEFUL_DEGRADATION_POLICY` declares exactly 11 rows per §13.5 verbatim (Skills/MCP/claude.md → CONTINUES; Managed Agents → FALLS_THROUGH; Per-role binding → C6_CROSS_FAMILY_FALLBACK; Caching → CACHE_STATE_LOST; Extended-thinking → RUNS_WITHOUT_PRIMITIVE; Batch API → IN_FLIGHT_RESUME; Hooks → HARNESS_OWNED_HOOK_LIFECYCLE; Files → CROSS_FAMILY_LOSES_REFERENCES; Memory → CROSS_FAMILY_COMPATIBLE).
2. `C6_CROSS_FAMILY_FALLBACK_CHAIN` declares 5 steps per §13.5 row 4: anthropic → bedrock → vertex → openai → ollama.
3. Outage signal source: C9 breaker key per ADR-F1; breaker mechanics at CP plan Session 3.
4. `MemoryToolStorageBackend` carries 5 values per §13.6 step 8.
5. `memory_tool_storage_backend` returns per-surface backend set: LOCAL_DEVELOPMENT → {FILESYSTEM, ENCRYPTED_FILESYSTEM}; MANAGED_CLOUD → {S3, DATABASE}.
6. Cross-axis IS binding per §13.6 step 8: FILESYSTEM backend at LOCAL_DEVELOPMENT consumes FILESYSTEM_PATH_CONTRACT_EXPORT (C-IS-10 §10.4 via U-IS-01 + U-IS-02) plus worktree-isolation per C-IS-09.
7. `compose_workload_binding_decision` implements 8-step procedure per §13.6 verbatim.
8. Decision deterministic given inputs.
9. Composable with cross-deployment monotonicity at U-AS-15.

**Tests:** `test_graceful_degradation_policy_cardinality_eleven`, `test_graceful_degradation_policy_per_spec_row_by_row`, `test_c6_cross_family_fallback_chain_five_steps`, `test_c6_cross_family_fallback_chain_ordered`, `test_memory_tool_storage_backend_cardinality_five`, `test_memory_tool_storage_backend_local_development_returns_filesystem_options`, `test_memory_tool_storage_backend_managed_cloud_returns_cloud_options`, `test_memory_tool_filesystem_backend_consumes_u_is_01_path_contract`, `test_compose_workload_binding_decision_eight_steps`, `test_compose_workload_binding_decision_deterministic`, `test_compose_workload_binding_decision_delegates_to_u_as_28_and_u_as_29`.

**Rollback boundary:** Revert graceful-degradation policy + workload-binding procedure + Memory backend selection. Outage handling falls back to single behavior per primitive; workload-binding decision impossible at runtime.

#### U-AS-31 — Declare six Anthropic-primitive attribute namespaces

**Implements:** [C-AS-14 §14.1, §14.2, §14.3, §14.4, §14.5, §14.6, §14.7]

**Depends on:** [U-AS-04, U-AS-28]

**Inputs:** None (foundational attribute namespace declarations).

**Files affected:** AS-axis Anthropic-primitive attribute namespace declarations (logical: `anthropic-primitive-attribute-namespaces`); per-namespace attribute schema tables (logical: `per-namespace-attribute-schemas`); skill-version-sha semantic-distinction enforcement (logical: `skill-version-sha-semantic-distinction-enforcement`).

**Signatures:**

```
enum AttributeNamespace {
  ANTHROPIC, MCP, SKILL, MANAGED_AGENTS, FILES, MEMORY
}

record AttributeSchema {
  attribute_name : string
  value_type     : AttributeValueType
  semantic       : string
  cardinality    : Cardinality
  parent_span    : string
  required       : bool
}

const ANTHROPIC_NAMESPACE_SCHEMA: List<AttributeSchema>          // 10
const MCP_NAMESPACE_SCHEMA: List<AttributeSchema>                // 7
const SKILL_NAMESPACE_SCHEMA: List<AttributeSchema>              // 6
const MANAGED_AGENTS_NAMESPACE_SCHEMA: List<AttributeSchema>     // 3
const FILES_NAMESPACE_SCHEMA: List<AttributeSchema>              // 8
const MEMORY_NAMESPACE_SCHEMA: List<AttributeSchema>             // 6

function namespace_schema(ns: AttributeNamespace) -> List<AttributeSchema>
function validate_skill_attributes_carry_both_version_fields(skill_span_attrs) -> ValidationResult
```

**Acceptance criteria:**
1. `AttributeNamespace` declares 6 values per §14.1 verbatim.
2. Per-namespace counts: ANTHROPIC=10, MCP=7, SKILL=6, MANAGED_AGENTS=3, FILES=8, MEMORY=6. Aggregate = 40 attributes.
3. ANTHROPIC schema (§14.2): `anthropic.cache_creation_input_tokens`, `cache_read_input_tokens`, `cache_breakpoint_id`, `cache_ttl_seconds`, `thinking_mode`, `thinking_budget_tokens`, `thinking_effort`, `batch_id`, `tokenizer_version`, `inference_geo`.
4. MCP schema (§14.3): `mcp.server.name`, `server.trust_tier`, `protocol_version`, `transport`, `auth_present`, `primitive.kind`, `primitive.signature.sha256`.
5. SKILL schema (§14.4): `skill.id`, `name`, `version_sha`, `frontmatter.version`, `body_tokens`, `activation_mode`.
6. **Semantic distinction enforcement (load-bearing per §14.4):** `skill.version_sha` (git content hash; replay-determinism anchor) AND `skill.frontmatter.version` (operator-declared; migration-tracking) both REQUIRED at every skill.activation span. Spans carrying only one rejected.
7. MANAGED_AGENTS schema (§14.5): `managed_agents.runtime_ms`, `session_id`, `billable_seconds`.
8. FILES schema (§14.6): `files.operation.kind`, `file_id`, `filename`, `mime_type`, `size_bytes`, `workspace_id`, `batch_composition`, `code_execution_composition`.
9. MEMORY schema (§14.7): `memory.operation.kind`, `path`, `backend`, `bytes_read`, `bytes_written`, `context_editing_active`.
10. Attribute names byte-exact spec-verbatim; ADR-D3 v1.2 §1.8.1 canonical declaration site.
11. F2-11 namespace history per §14.1: `files.*` and `memory.*` introduced at ADR-D3 v1.1 — F2-11 Reading 2 closure.
12. Optional attributes per spec: `anthropic.batch_id`, `inference_geo`, `files.batch_composition`, `code_execution_composition`, `memory.bytes_read`, `bytes_written`.

**Tests:** `test_attribute_namespace_cardinality_six`, `test_anthropic_namespace_ten_attributes_per_spec_14_2`, `test_mcp_namespace_seven_attributes_per_spec_14_3`, `test_skill_namespace_six_attributes_per_spec_14_4`, `test_managed_agents_namespace_three_attributes_per_spec_14_5`, `test_files_namespace_eight_attributes_per_spec_14_6`, `test_memory_namespace_six_attributes_per_spec_14_7`, `test_aggregate_attribute_count_40`, `test_skill_span_requires_both_version_fields`, `test_skill_span_requires_both_version_fields_reverse`, `test_skill_span_accepts_both_version_fields`, `test_attribute_names_byte_exact_per_spec`, `test_optional_attributes_per_spec`.

**Rollback boundary:** Revert all six namespace declarations + `AttributeNamespace` + skill-version-sha enforcement. Anthropic-primitive observability surface loses attribute schema substrate; OD plan ingestion loses six namespace rows for D6 §1.2 cross-axis verbatim consumption.

#### U-AS-32 — Sampling discipline + audit-floor commitments + D6 forward-reference

**Implements:** [C-AS-14 §14.8, §14.9]

**Depends on:** [U-AS-18, U-AS-31]

**Inputs:** Per-span-kind sampling configuration; D6 sampling-discipline alignment check (forward-reference per F2-09).

**Files affected:** AS-axis Anthropic-primitive sampling policy (logical: `anthropic-primitive-sampling-policy`); audit-floor commitments enforcement (logical: `audit-floor-commitments-enforcement`); D6 alignment forward-reference (logical: `d6-sampling-alignment-forward-reference`).

**Signatures:**

```
enum AnthropicPrimitiveSamplingPosture {
  HEAD_BASED_DEV_TAIL_BASED_PROD,
  HEAD_1_0_DESIGN_TIME_BASE_RATE_PROD,
  HEAD_1_0_WITH_TAIL_KEEP_ON_VIOLATIONS,
  HEAD_1_0_ALWAYS,
  HEAD_1_0_AT_MUTATION_BASE_RATE_AT_READ
}

const ANTHROPIC_PRIMITIVE_SAMPLING_POLICY: Map<string, AnthropicPrimitiveSamplingPosture>

enum AuditFloorScope {
  MCP_TOOL_CALL_ALWAYS_SAMPLED,
  FILES_OPERATION_MUTATION_ALWAYS_SAMPLED,
  MEMORY_OPERATION_MUTATION_ALWAYS_SAMPLED,
  MANAGED_AGENTS_RUNTIME_ALWAYS_SAMPLED,
  SKILL_ACTIVATION_DESIGN_TIME_ALWAYS_SAMPLED
}

const AUDIT_FLOOR_COMMITMENTS: Set<AuditFloorScope>

function audit_floor_commitment_violated(proposed_policy) -> Set<AuditFloorScope>
function d6_sampling_discipline_alignment_check(d6_proposed_policy) -> AlignmentResult
```

**Acceptance criteria:**
1. Sampling policy declares 6 rows per §14.8 verbatim: llm.inference → head/tail; skill.activation → head=1.0 design-time/base-rate prod; mcp.tool.call → head=1.0 with tail-keep; managed_agents.runtime → head=1.0 always; files.operation → head=1.0 at mutation/base-rate at read; memory.operation → same.
2. `AUDIT_FLOOR_COMMITMENTS` declares 5 scopes; hard floors at deployment-binding layer; not operator-tunable at base-rate.
3. `audit_floor_commitment_violated` returns violated scope set on downgrade attempt.
4. files/memory.operation distinguish mutation (`upload`/`delete`/`write`/`update`) from read (`list`/`metadata`/`reference`/`read`).
5. mcp.tool.call tail-keep-on-trust-tier-floor-violations per §14.8 row 3.
6. D6 forward-reference per §14.9: alignment check verifies D6-proposed policy distinguishes `mcp.tool.call` (always-sampled) from non-MCP `tool.call` (base-rate).
7. Cross-axis citation: full D6 sampling-discipline composition at OD plan Session 4.
8. Composition with U-AS-18 sandbox sampling: orthogonal namespaces; no overlap.

**Tests:** `test_anthropic_primitive_sampling_policy_six_rows_per_spec_14_8`, `test_audit_floor_commitments_cardinality_five`, `test_audit_floor_commitment_violated_detects_mcp_tool_call_downgrade`, `test_audit_floor_commitment_violated_returns_empty_for_compliant_policy`, `test_files_operation_sampling_distinguishes_mutation_from_read`, `test_memory_operation_sampling_distinguishes_mutation_from_read`, `test_mcp_tool_call_tail_keep_on_trust_tier_violation`, `test_d6_sampling_alignment_check_distinguishes_mcp_from_non_mcp_tool_call`, `test_d6_sampling_alignment_check_passes_compliant_d6_policy`.

**Rollback boundary:** Revert sampling policy + audit-floor commitments + D6 forward-reference. Anthropic-primitive spans fall back to default base-rate; audit-floor commitments lost; mcp.tool.call may become tunable to base-rate; D6 plan loses alignment-check anchor.

---

### §2.8 Cluster 8 — AS-axis substrate seam exports surface (C-AS-16)

#### U-AS-33 — Declare AS-axis substrate seam exports manifest

**Implements:** [C-AS-16 §16.1, §16.2, §16.3, §16.4, §16.5, §16.6, §16.7]

**Depends on:** [U-AS-09, U-AS-10, U-AS-14, U-AS-15, U-AS-16, U-AS-17, U-AS-18, U-AS-22, U-AS-25, U-AS-26, U-AS-27, U-AS-28, U-AS-29, U-AS-30, U-AS-31, U-AS-32]

**Inputs:** AS spec §16.1 through §16.7 export sub-surfaces (seven seams).

**Files affected:** AS-axis substrate seam exports manifest (logical: `as-axis-substrate-seam-exports-manifest`).

**Scope.** Declarative manifest only; no executable behavior. Per OD-S2-3.A symmetric with U-IS-17 precedent: consumer-axis dependency declarations authored at consumer-axis sessions (CP plan Session 3, OD plan Session 4); Session 5 retroactive verification.

**Signatures:**

```
enum ASSeamId {
  SANDBOX_BOUNDED_SPAN_SCHEMA_EXPORT,                  // §16.1
  FIVE_AXIS_MULTIPLICATIVE_TUNABLE_EXPORT,             // §16.2
  SECRET_FETCH_AUDIT_EXPORT,                           // §16.3
  SIX_ANTHROPIC_PRIMITIVE_ATTRIBUTE_NAMESPACE_EXPORT,  // §16.4
  PER_TOOL_REQUIRED_SECRETS_EXPORT,                    // §16.5
  ELEVEN_PRIMITIVE_ADOPTION_DEPTH_MATRIX_EXPORT,       // §16.6
  FORCING_CONDITION_EXPORT                             // §16.7
}

enum ASConsumingAxis { CONTROL_PLANE, OPERATIONAL_DISCIPLINE, CROSS_AXIS }

record ASSubstrateSeamExport {
  seam_id                   : ASSeamId
  spec_citation             : string
  export_surface            : string
  carrier_units             : List<UnitId>
  consuming_axes            : List<ASConsumingAxis>
  composition_references    : List<string>
  cross_spec_citation_target: List<string>
}

const AS_SUBSTRATE_SEAM_EXPORTS: List<ASSubstrateSeamExport>   // exactly 7 entries

function as_seam_carrier_units(seam: ASSeamId) -> List<UnitId>
function as_seam_consuming_axes(seam: ASSeamId) -> List<ASConsumingAxis>
function as_seam_export_surface(seam: ASSeamId) -> string
```

**Manifest content:**

| Seam | Spec citation | Carrier units | Consuming axes |
|---|---|---|---|
| SANDBOX_BOUNDED_SPAN_SCHEMA_EXPORT | C-AS-16 §16.1 | U-AS-16, U-AS-17, U-AS-18 | CP, OD |
| FIVE_AXIS_MULTIPLICATIVE_TUNABLE_EXPORT | C-AS-16 §16.2 | U-AS-09, U-AS-14, U-AS-15 | CP, CROSS_AXIS |
| SECRET_FETCH_AUDIT_EXPORT | C-AS-16 §16.3 | U-AS-25, U-AS-26, U-AS-27 | OD |
| SIX_ANTHROPIC_PRIMITIVE_ATTRIBUTE_NAMESPACE_EXPORT | C-AS-16 §16.4 | U-AS-31, U-AS-32 | OD |
| PER_TOOL_REQUIRED_SECRETS_EXPORT | C-AS-16 §16.5 | U-AS-22 | CP |
| ELEVEN_PRIMITIVE_ADOPTION_DEPTH_MATRIX_EXPORT | C-AS-16 §16.6 | U-AS-28, U-AS-29, U-AS-30 | CP, CROSS_AXIS |
| FORCING_CONDITION_EXPORT | C-AS-16 §16.7 | U-AS-02, U-AS-10 | CP |

**Composition references (verbatim from spec):** §16.1 → OD D6 v1.1 §1.2 row `sandbox.*` ingests C-AS-15 §15.2 verbatim under F4-canonical-naming-honored-at-source-D-ADR; CP D4 v1.1 §1.9 multi-agent span hierarchy composes sub-agent dispatch with sandbox.enter/exit per parent/child relationship; CP D5 v1.3 §1.10 pre-HITL escalation routes sandbox-violation `sandbox.fail.class` per C-AS-04 §4.2. §16.2 → CP D5 v1.3 §1.5 multiplicative gate-level rule specialized by C-AS-12 §12.1 adding `sandbox_tier` as fifth axis; CP D4 v1.1 §1.5 sub-agent privilege inheritance composes with C-AS-11 monotonic-ascension per ADD §5.3.2; cross-axis ADD §5.2.1 T-perm-1 closure shape locked at C-AS-12 §12.5. §16.3 → OD D5 v1.3 §1.4 per-persona-tier audit-ledger cryptographic shape composes at Session 4; IS C-IS-10 §10.1 export pattern established at IS spec. §16.4 → OD D6 v1.1 §1.2 ingests namespace rows from C-AS-14 §§14.2–14.7 verbatim under Pattern P1 mechanical-alignment at Session 4; D6 §1.3 ingestion binding per ADR-D3 v1.2 §1.8 F2-09 forward-reference. §16.5 → CP D5 v1.3 §1.5 multiplicative gate-level rule; `required_secrets` orthogonal per ADR-F5 v1.1 §"Permanent tensions engaged" T-perm-1 touch; NOT a fifth `max()` floor. §16.6 → CP D4 v1.1 §1.2 per-workload-class topology commitment inherits C-AS-13 §13.4 row at Session 3; CP D1 v1.1 §1.1 engine-class taxonomy specialized by C-AS-13 §13.3 overlay at Session 3; cross-axis T-perm-3 D3-layer adjacency per ADD §5.2.3 composes C-AS-13 §13.5 graceful-degradation with F1 cross-family fallback at Session 3. §16.7 → CP D5 v1.3 §1.10 pre-HITL escalation skips C-AS-04 §4.2 staircase for `escape_attempt` / `egress_denied` / `signal` per D5 §1.10 at Session 3.

**Acceptance criteria:**
1. `AS_SUBSTRATE_SEAM_EXPORTS` enumerates exactly seven entries matching spec §16.1 through §16.7 verbatim.
2. Each `carrier_units` field cites ≥1 unit from U-AS-01 through U-AS-32; every cited carrier resolves to a filed unit in §2.1–§2.7 of this plan.
3. Each `consuming_axes` matches spec §16.X "Consuming axis" column verbatim.
4. Each `spec_citation` has form `C-AS-16 §16.X` with X ∈ {1..7}.
5. Manifest introduces no executable behavior — declarative records only.
6. ADR body-citation versions aligned: F4 v1.1, F5 v1.1, D2 v1.1, D3 v1.2, D4 v1.1, D5 v1.3, D6 v1.1 (latest filed per Workflow v1.5 §7).
7. Per OD-S2-3.A: consumer-axis dependency declarations NOT authored at this unit; CP plan (Session 3) + OD plan (Session 4) declare cross-axis dependencies citing this manifest's `carrier_units`; Session 5 retroactive verification.
8. Symmetric posture with U-IS-17 (IS plan Cluster 6).
9. F4-authoritative-naming honored: SANDBOX_BOUNDED_SPAN_SCHEMA_EXPORT carries the seven `sandbox.*` attribute names declared at U-AS-16.
10. Pattern P1 mechanical-alignment per §16.4: D6 §1.2 ingests namespace rows from C-AS-14 §§14.2–14.7 verbatim; U-AS-31 is source of truth; D6 does not re-declare.

**Tests:** `test_as_substrate_seam_exports_cardinality_seven`, `test_as_seam_carrier_units_resolve`, `test_as_seam_carrier_units_cover_export_surface`, `test_as_seam_consuming_axes_match_spec_verbatim`, `test_as_seam_spec_citation_stable_anchor`, `test_as_seam_manifest_no_executable_behavior`, `test_as_seam_adr_body_citation_versions_aligned`, `test_as_seam_consumer_axis_declarations_not_authored_here`, `test_as_seam_sandbox_attribute_names_match_u_as_16_byte_exact`, `test_as_seam_anthropic_primitive_namespaces_match_u_as_31_byte_exact`, `test_as_seam_symmetric_with_u_is_17_shape`.

**Rollback boundary:** Revert AS-axis substrate seam exports manifest. CP plan + OD plan lose stable citation target for AS-axis exports; cross-axis dependency declarations cannot resolve. Session 5 cross-axis composition cannot verify consumer-axis declarations against AS export surface. AS plan loses its mirror to IS plan's U-IS-17.

---

## §3 Dependency graph

### §3.1 Within-axis topological levels

Nine levels. Foundational units (L0) anchor the graph; substrate seam exports manifest (L8) closes it.

| Level | Unit count | Units |
|---|---|---|
| L0 | 3 | U-AS-01, U-AS-03, U-AS-04 |
| L1 | 7 | U-AS-02, U-AS-05, U-AS-07, U-AS-11, U-AS-12, U-AS-20, U-AS-28 |
| L2 | 7 | U-AS-06, U-AS-10, U-AS-22, U-AS-24, U-AS-25, U-AS-29, U-AS-31 |
| L3 | 7 | U-AS-08, U-AS-09, U-AS-13, U-AS-14, U-AS-15, U-AS-26, U-AS-30 |
| L4 | 1 | U-AS-16 |
| L5 | 1 | U-AS-17 |
| L6 | 5 | U-AS-18, U-AS-19, U-AS-21, U-AS-23, U-AS-27 |
| L7 | 1 | U-AS-32 |
| L8 | 1 | U-AS-33 |
| **Total** | **33** | — |

Level assignment rule: a unit's level equals max(level of within-axis dependencies) + 1. Cross-axis IS dependencies do not contribute to within-axis level (the IS axis is upstream; cross-axis edges are unidirectional AS → IS).

### §3.2 Per-unit dependency declarations

Within-axis dependencies + cross-axis IS dependencies (flagged `(cross-axis: IS)` per OD-S2-3.A).

| Unit | Depends on |
|---|---|
| U-AS-01 | (none) |
| U-AS-02 | U-AS-01 |
| U-AS-03 | (none) |
| U-AS-04 | (none) |
| U-AS-05 | U-AS-01 |
| U-AS-06 | U-AS-01, U-AS-04, U-AS-05 |
| U-AS-07 | U-AS-01 |
| U-AS-08 | U-AS-01, U-AS-02, U-AS-04, U-AS-05, U-AS-06, U-AS-07 |
| U-AS-09 | U-AS-01, U-AS-04, U-AS-06 |
| U-AS-10 | U-AS-01, U-AS-02, U-AS-04, U-AS-11 |
| U-AS-11 | U-AS-01 |
| U-AS-12 | U-AS-04 |
| U-AS-13 | U-AS-01, U-AS-04, U-AS-05, U-AS-06 |
| U-AS-14 | U-AS-01, U-AS-04, U-AS-05, U-AS-06 |
| U-AS-15 | U-AS-01, U-AS-04, U-AS-06 |
| U-AS-16 | U-AS-01, U-AS-03, U-AS-08 |
| U-AS-17 | U-AS-01, U-AS-03, U-AS-08, U-AS-16 |
| U-AS-18 | U-AS-17 |
| U-AS-19 | U-AS-09, U-AS-17, **U-IS-07 (cross-axis: IS)**, **U-IS-12 (cross-axis: IS)** |
| U-AS-20 | U-AS-01 |
| U-AS-21 | U-AS-17, U-AS-20 |
| U-AS-22 | U-AS-07, U-AS-20 |
| U-AS-23 | U-AS-17, U-AS-20, U-AS-22 |
| U-AS-24 | U-AS-03, U-AS-20 |
| U-AS-25 | U-AS-20, **U-IS-08 (cross-axis: IS)** |
| U-AS-26 | U-AS-25, **U-IS-07 (cross-axis: IS)**, **U-IS-09 (cross-axis: IS)**, **U-IS-10 (cross-axis: IS)** |
| U-AS-27 | U-AS-17, U-AS-22, U-AS-24, U-AS-26, **U-IS-11 (cross-axis: IS)** |
| U-AS-28 | U-AS-04, **U-IS-01 (cross-axis: IS)**, **U-IS-02 (cross-axis: IS)** |
| U-AS-29 | U-AS-04, U-AS-28, **U-IS-01 (cross-axis: IS)**, **U-IS-02 (cross-axis: IS)** |
| U-AS-30 | U-AS-04, U-AS-28, U-AS-29, **U-IS-01 (cross-axis: IS)**, **U-IS-02 (cross-axis: IS)** |
| U-AS-31 | U-AS-04, U-AS-28 |
| U-AS-32 | U-AS-18, U-AS-31 |
| U-AS-33 | U-AS-09, U-AS-10, U-AS-14, U-AS-15, U-AS-16, U-AS-17, U-AS-18, U-AS-22, U-AS-25, U-AS-26, U-AS-27, U-AS-28, U-AS-29, U-AS-30, U-AS-31, U-AS-32 |

### §3.3 Acyclic invariant verification

Within-axis graph: 33 nodes, 88 within-axis edges enumerated at §3.2. Topological sort exists per §3.1 (all 33 units placed across 9 levels). **AS-internal dependency graph is a DAG.** No cycle resolution required.

Cross-axis edges are unidirectional AS → IS by construction (IS plan v1 filed prior to this plan; IS units do not depend on AS units). Cross-axis cycles are structurally impossible at this composition site.

Verification procedure: enumerate within-axis edges → compute in-degree (L0 units have in-degree 0: U-AS-01, U-AS-03, U-AS-04) → apply Kahn's algorithm → algorithm terminates with all 33 units removed.

**Result: ✅ Acyclic.**

### §3.4 Cross-axis edge enumeration (AS → IS)

13 cross-axis edges from 8 AS units. All edges resolve to IS plan v1 §2 unit declarations per U-IS-17 manifest carrier-units field.

| AS unit | IS unit | IS manifest seam | AS spec citation |
|---|---|---|---|
| U-AS-19 | U-IS-07 | STATE_LEDGER_ENTRY_SHAPE_EXPORT (C-IS-10 §10.1) | C-AS-15 §15.6 row 1 |
| U-AS-19 | U-IS-12 | IDEMPOTENCY_KEY_JOIN_EXPORT (C-IS-10 §10.2) | C-AS-15 §15.6 row 1+3 |
| U-AS-25 | U-IS-08 | HASH_CHAIN_CONSTRUCTION_DISCIPLINE_EXPORT — canonicalize carrier (C-IS-10 §10.3) | C-AS-08 §8.1 |
| U-AS-26 | U-IS-07 | STATE_LEDGER_ENTRY_SHAPE_EXPORT (C-IS-10 §10.1) | C-AS-08 §8.2 |
| U-AS-26 | U-IS-09 | HASH_CHAIN_CONSTRUCTION_DISCIPLINE_EXPORT — chain-link carrier (C-IS-10 §10.3) | C-AS-08 §8.3 |
| U-AS-26 | U-IS-10 | HASH_CHAIN_CONSTRUCTION_DISCIPLINE_EXPORT — verification carrier (C-IS-10 §10.3) | C-AS-08 §8.3 |
| U-AS-27 | U-IS-11 | JSONL_EVENT_LEDGER_FORMAT_EXPORT — write contract (C-IS-10 §10.5) | C-AS-08 §8.4 |
| U-AS-28 | U-IS-01 | FILESYSTEM_PATH_CONTRACT_EXPORT (C-IS-10 §10.4) | C-AS-13 §13.2 row 1 |
| U-AS-28 | U-IS-02 | FILESYSTEM_PATH_CONTRACT_EXPORT (C-IS-10 §10.4) | C-AS-13 §13.2 row 1 |
| U-AS-29 | U-IS-01 | FILESYSTEM_PATH_CONTRACT_EXPORT (C-IS-10 §10.4) | C-AS-13 §13.3 column 5 |
| U-AS-29 | U-IS-02 | FILESYSTEM_PATH_CONTRACT_EXPORT (C-IS-10 §10.4) | C-AS-13 §13.3 column 5 |
| U-AS-30 | U-IS-01 | FILESYSTEM_PATH_CONTRACT_EXPORT (C-IS-10 §10.4) | C-AS-13 §13.6 step 8 |
| U-AS-30 | U-IS-02 | FILESYSTEM_PATH_CONTRACT_EXPORT (C-IS-10 §10.4) | C-AS-13 §13.6 step 8 |

#### §3.4.1 IS export seam consumption profile

| IS export seam | Consumed by (AS units) | Edge count |
|---|---|---|
| STATE_LEDGER_ENTRY_SHAPE_EXPORT (C-IS-10 §10.1) | U-AS-19, U-AS-26 | 2 |
| IDEMPOTENCY_KEY_JOIN_EXPORT (C-IS-10 §10.2) | U-AS-19 | 1 |
| HASH_CHAIN_CONSTRUCTION_DISCIPLINE_EXPORT (C-IS-10 §10.3) | U-AS-25, U-AS-26 | 4 (via 3 carrier units) |
| FILESYSTEM_PATH_CONTRACT_EXPORT (C-IS-10 §10.4) | U-AS-28, U-AS-29, U-AS-30 | 6 (via 2 carrier units) |
| JSONL_EVENT_LEDGER_FORMAT_EXPORT (C-IS-10 §10.5) | U-AS-27 | 1 (via write contract carrier U-IS-11) |
| WORKLOAD_CLASS_OPT_IN_MANIFEST_EXPORT (C-IS-10 §10.6) | (none — CP-axis exclusive) | 0 |

#### §3.4.2 IS carrier-unit consumption profile

| IS carrier unit | Consumed by (AS units) | Edge count |
|---|---|---|
| U-IS-01 | U-AS-28, U-AS-29, U-AS-30 | 3 |
| U-IS-02 | U-AS-28, U-AS-29, U-AS-30 | 3 |
| U-IS-07 | U-AS-19, U-AS-26 | 2 |
| U-IS-08 | U-AS-25 | 1 |
| U-IS-09 | U-AS-26 | 1 |
| U-IS-10 | U-AS-26 | 1 |
| U-IS-11 | U-AS-27 | 1 |
| U-IS-12 | U-AS-19 | 1 |
| **Total** | — | **13** |

Per OD-S2-3.A retroactive verification at Session 5: each cited carrier unit resolves to a unit declared in IS plan v1 §2.

### §3.5 ASCII dependency graph (compact, level-layered)

```
LEVEL 0 — Foundational (no deps)
─────────────────────────────────────────────────────────────────────────
  U-AS-01 [SandboxTier+BlastRadiusTier+MechanismClass]
  U-AS-03 [SandboxFailClass]
  U-AS-04 [DeploymentSurface+PersonaTier+MCPTransport]

LEVEL 1 — Direct foundational consumers
─────────────────────────────────────────────────────────────────────────
  U-AS-02 [forced-tier predicate]               ← U-AS-01
  U-AS-05 [blast_radius_floor mapping]          ← U-AS-01
  U-AS-07 [ToolContract.minimum_tier]           ← U-AS-01
  U-AS-11 [SandboxProviderClass]                ← U-AS-01
  U-AS-12 [override scope per persona-tier]     ← U-AS-04
  U-AS-20 [fetch_secret + SecretRef + tiers]    ← U-AS-01
  U-AS-28 [eleven-primitive matrix]             ← U-AS-04  [+ IS]

LEVEL 2 — Composition floors + L1 consumers
─────────────────────────────────────────────────────────────────────────
  U-AS-06 [sandbox_tier_floor lookup]           ← U-AS-01, U-AS-04, U-AS-05
  U-AS-10 [12-cell matrix]                      ← U-AS-01, U-AS-02, U-AS-04, U-AS-11
  U-AS-22 [SecretAllowlist + required_secrets]  ← U-AS-07, U-AS-20
  U-AS-24 [SecretFailClass + breaker]           ← U-AS-03, U-AS-20
  U-AS-25 [outputs_hash formula]                ← U-AS-20  [+ IS]
  U-AS-29 [engine-class + model-binding]        ← U-AS-04, U-AS-28  [+ IS]
  U-AS-31 [six attribute namespaces]            ← U-AS-04, U-AS-28

LEVEL 3 — Sandbox-tier composition + downstream
─────────────────────────────────────────────────────────────────────────
  U-AS-08 [sandbox_tier composition]            ← 01,02,04,05,06,07
  U-AS-09 [sub_agent_sandbox_tier]              ← U-AS-01, U-AS-04, U-AS-06
  U-AS-13 [per-MCP-transport floor]             ← U-AS-01, U-AS-04, U-AS-05, U-AS-06
  U-AS-14 [5-axis gate-level composition]       ← U-AS-01, U-AS-04, U-AS-05, U-AS-06
  U-AS-15 [cross-deployment monotonicity]       ← U-AS-01, U-AS-04, U-AS-06
  U-AS-26 [audit-entry composition]             ← U-AS-25  [+ IS]
  U-AS-30 [degradation + workload-binding]      ← U-AS-04, U-AS-28, U-AS-29  [+ IS]

LEVEL 4 — Span attribute schema
─────────────────────────────────────────────────────────────────────────
  U-AS-16 [seven sandbox.* attributes]          ← U-AS-01, U-AS-03, U-AS-08

LEVEL 5 — Span hierarchy + sensitive-data
─────────────────────────────────────────────────────────────────────────
  U-AS-17 [span hierarchy + exclusions]         ← U-AS-01, U-AS-03, U-AS-08, U-AS-16

LEVEL 6 — Sampling + invariants + cross-axis-IS consumers
─────────────────────────────────────────────────────────────────────────
  U-AS-18 [sandbox sampling discipline]         ← U-AS-17
  U-AS-19 [idempotency-key composition]         ← U-AS-09, U-AS-17  [+ IS]
  U-AS-21 [negative-observation invariants]     ← U-AS-17, U-AS-20
  U-AS-23 [passthrough constraints]             ← U-AS-17, U-AS-20, U-AS-22
  U-AS-27 [audit emission orchestrator]         ← U-AS-17, U-AS-22, U-AS-24, U-AS-26  [+ IS]

LEVEL 7 — Anthropic-primitive sampling
─────────────────────────────────────────────────────────────────────────
  U-AS-32 [primitive sampling + audit-floor]    ← U-AS-18, U-AS-31

LEVEL 8 — AS-axis substrate seam exports manifest
─────────────────────────────────────────────────────────────────────────
  U-AS-33 [substrate seam exports manifest]
              ← U-AS-09, U-AS-10, U-AS-14, U-AS-15, U-AS-16, U-AS-17,
                U-AS-18, U-AS-22, U-AS-25, U-AS-26, U-AS-27, U-AS-28,
                U-AS-29, U-AS-30, U-AS-31, U-AS-32
```

#### §3.5.1 Cross-axis edge overlay

```
                     AS plan (this plan)         IS plan v1 (filed)
                     ════════════════════         ═══════════════════

  Skills/Memory filesystem ───────────────────►   U-IS-01, U-IS-02
    U-AS-28 ──┐                                     (FILESYSTEM_PATH_
    U-AS-29 ──┤───── 6 edges                         CONTRACT_EXPORT)
    U-AS-30 ──┘

  Sandbox-event idempotency ──────────────────►   U-IS-07, U-IS-12
    U-AS-19   ─── 2 edges                            (STATE_LEDGER +
                                                      IDEMPOTENCY_KEY)

  Secret-fetch audit canonicalization ────────►   U-IS-08
    U-AS-25   ─── 1 edge                             (HASH_CHAIN
                                                      canonicalize)

  Secret-fetch audit entry composition ───────►   U-IS-07, U-IS-09, U-IS-10
    U-AS-26   ─── 3 edges                            (entry + chain-link
                                                      + verification)

  Secret-fetch audit emission ────────────────►   U-IS-11
    U-AS-27   ─── 1 edge                             (JSONL write contract)
```

### §3.6 Foundational-first ordering verification

L0 units are the foundational substrate anchors:

| L0 unit | Foundational role |
|---|---|
| U-AS-01 | SandboxTier + BlastRadiusTier + MechanismClass — sandbox subsystem foundation |
| U-AS-03 | SandboxFailClass — sandbox-violation taxonomy foundation |
| U-AS-04 | DeploymentSurface + PersonaTier + MCPTransport — call-site discriminator foundation |

These three units have no dependencies; they declare the foundational enum substrate that every downstream sandbox-subsystem and secret-fetch-subsystem unit consumes.

#### §3.6.1 No transitive omission

Each unit declares direct dependencies only. Sample verification:

| Unit | Direct deps | Transitive closure check |
|---|---|---|
| U-AS-08 | U-AS-01, U-AS-02, U-AS-04, U-AS-05, U-AS-06, U-AS-07 | U-AS-06 transitively depends on U-AS-01, U-AS-04, U-AS-05; U-AS-08 also depends on U-AS-02 and U-AS-07 not via U-AS-06. All direct deps required; no over-declaration. |
| U-AS-17 | U-AS-01, U-AS-03, U-AS-08, U-AS-16 | U-AS-16 transitively covers U-AS-01, U-AS-03, U-AS-08; U-AS-17 explicitly uses SandboxTier (U-AS-01), SandboxFailClass (U-AS-03), AssignedTierReason (U-AS-08) at signatures. Direct declaration warranted. |
| U-AS-33 | 16 carriers across L1–L7 | Each carrier is the source of a specific export sub-surface; no carrier transitively covered by another at export-surface granularity. Direct declaration warranted. |

### §3.7 Coverage discipline verification

Per SKILL.md §7: each unit's declared dependencies are sufficient for its acceptance criterion.

| Sample acceptance verification | Direct deps cover acceptance? |
|---|---|
| U-AS-08 acceptance 1 (composition max() over 5 floors) | ✓ — U-AS-05, U-AS-06, U-AS-07, U-AS-02, plus injected `FloorInterfaces` |
| U-AS-17 acceptance 2.1 (span hierarchy) | ✓ — U-AS-16, U-AS-08, U-AS-01, U-AS-03 |
| U-AS-19 acceptance 4.1 (idempotency_key from parent) | ✓ — U-AS-17, U-IS-07, U-AS-09 |
| U-AS-27 acceptance 3.1-3.7 (emission orchestration) | ✓ — U-AS-26, U-AS-22, U-AS-24, U-AS-17, U-IS-11 |
| U-AS-33 acceptance 1.2 (carrier_units resolve) | ✓ — all 16 cited carriers are explicit direct deps |

No missing-dependency defects.

---

## §4 Coverage matrix (per OD-S2-2.A)

Per-axis coverage matrix mapping each AS-spec contract section to its covering unit(s). Per OD-S2-2.A inheriting OD-S1-2.A precedent: per-axis matrix self-contained; no aggregate matrix composed at Session 5.

### §4.1 Contract-section → unit coverage matrix

| C-AS-NN | Spec sub-section | Covering unit(s) | Cluster |
|---|---|---|---|
| C-AS-01 | §1.1 Tier-set enumeration | U-AS-01 | 1 |
| C-AS-01 | §1.2 Tier-label stability invariant | U-AS-01 | 1 |
| C-AS-01 | §1.3 Forced-tier rules | U-AS-02 | 1 |
| C-AS-02 | §2.1 Composition signature | U-AS-08 | 2 |
| C-AS-02 | §2.2 Composition formula | U-AS-08 | 2 |
| C-AS-02 | §2.3 `sandbox_tier_floor` lookup table | U-AS-06 | 2 |
| C-AS-02 | §2.4 `blast_radius_floor` enum + default mapping | U-AS-05 (mapping) + U-AS-01 (enum) | 2 / 1 |
| C-AS-02 | §2.5 Composition output verification | U-AS-08 | 2 |
| C-AS-03 | §3.1 Tool contract field signature | U-AS-07 | 2 |
| C-AS-03 | §3.2 Declaration discipline | U-AS-07 | 2 |
| C-AS-03 | §3.3 Default-tier policy | U-AS-07 | 2 |
| C-AS-04 | §4.1 `sandbox.fail.class` enum | U-AS-03 | 1 |
| C-AS-04 | §4.2 Pre-HITL escalation order (metadata layer) | U-AS-03 (metadata) + U-AS-29 (escalation chain) | 1 / 7 |
| C-AS-04 | §4.3 Sampling discipline at emission | U-AS-03 (metadata) + U-AS-18 (enforcement) | 1 / 4 |
| C-AS-05 | §5.1 Function signature | U-AS-20 | 5 |
| C-AS-05 | §5.2 Tier-aware resolution | U-AS-20 | 5 |
| C-AS-05 | §5.3 Negative-observation invariant | U-AS-21 | 5 |
| C-AS-05 | §5.4 `SecretRef` opaque-type discipline | U-AS-20 | 5 |
| C-AS-06 | §6.1 Allowlist entry signature | U-AS-22 | 5 |
| C-AS-06 | §6.2 Access-control composition | U-AS-22 | 5 |
| C-AS-06 | §6.3 Secret-passthrough constraint | U-AS-23 | 5 |
| C-AS-07 | §7.1 `secret.fail.class` enum | U-AS-24 | 5 |
| C-AS-07 | §7.2 Composition with C-AS-04 | U-AS-24 | 5 |
| C-AS-07 | §7.3 Per-`(secret_backend, scope)` breaker placement | U-AS-24 | 5 |
| C-AS-08 | §8.1 `outputs_hash` formula | U-AS-25 | 6 |
| C-AS-08 | §8.2 Audit-ledger entry shape | U-AS-26 | 6 |
| C-AS-08 | §8.3 Hash-chain integrity composition | U-AS-26 | 6 |
| C-AS-08 | §8.4 Per-fetch emission discipline | U-AS-27 | 6 |
| C-AS-08 | §8.5 Cross-axis composition reference | U-AS-27 | 6 |
| C-AS-09 | §9.1 12-cell matrix | U-AS-10 | 3 |
| C-AS-09 | §9.2 Sandbox provider-class enumeration | U-AS-11 | 3 |
| C-AS-09 | §9.3 Forcing-condition cell resolution | U-AS-10 (via `lookup_cell_with_forcing`) | 3 |
| C-AS-09 | §9.4 Operator-policy override scope per persona tier | U-AS-12 | 3 |
| C-AS-09 | §9.5 Cell selection contract | U-AS-10 (D2-layer stage) | 3 |
| C-AS-10 | §10.1 Per-MCP-transport floor lookup table | U-AS-13 | 3 |
| C-AS-10 | §10.2 Composition with C-AS-02 | U-AS-13 + U-AS-06 (alignment) | 3 / 2 |
| C-AS-10 | §10.3 MCP server trust-tier framework | U-AS-13 (framework reference) | 3 |
| C-AS-11 | §11.1 Sub-agent tier-resolution signature | U-AS-09 | 2 |
| C-AS-11 | §11.2 Unconditional ascension rule | U-AS-09 | 2 |
| C-AS-11 | §11.3 Rationale anchor | U-AS-09 | 2 |
| C-AS-11 | §11.4 Composition with cross-deployment monotonicity | U-AS-09 (within-call) + U-AS-15 (cross-deployment) | 2 / 3 |
| C-AS-11 | §11.5 Sub-agent boundary verification | U-AS-09 | 2 |
| C-AS-12 | §12.1 5-axis multiplicative tunable parameter | U-AS-14 | 3 |
| C-AS-12 | §12.2 Composition with operator-policy override per persona-tier | U-AS-12 + U-AS-14 (reference) | 3 |
| C-AS-12 | §12.3 Override-event audit composition | U-AS-12 (substrate) + cross-cluster forward to U-AS-17 + U-AS-27 | 3 / 4 / 6 |
| C-AS-12 | §12.4 Cross-deployment monotonicity contract | U-AS-15 | 3 |
| C-AS-12 | §12.5 Multiplicative discipline preservation | U-AS-14 | 3 |
| C-AS-13 | §13.1 Eleven-primitive enumeration | U-AS-28 | 7 |
| C-AS-13 | §13.2 Per-primitive × workload-class adoption-depth matrix | U-AS-28 | 7 |
| C-AS-13 | §13.3 Per-engine-class composition site overlay | U-AS-29 | 7 |
| C-AS-13 | §13.4 Per-sub-agent-role × model-binding contract | U-AS-29 | 7 |
| C-AS-13 | §13.5 Anthropic-API graceful-degradation per primitive | U-AS-30 | 7 |
| C-AS-13 | §13.6 Workload-binding-time selection contract | U-AS-30 | 7 |
| C-AS-14 | §14.1 Six namespace declarations | U-AS-31 | 7 |
| C-AS-14 | §14.2 `anthropic.*` namespace | U-AS-31 | 7 |
| C-AS-14 | §14.3 `mcp.*` namespace | U-AS-31 | 7 |
| C-AS-14 | §14.4 `skill.*` namespace | U-AS-31 | 7 |
| C-AS-14 | §14.5 `managed_agents.*` namespace | U-AS-31 | 7 |
| C-AS-14 | §14.6 `files.*` namespace | U-AS-31 | 7 |
| C-AS-14 | §14.7 `memory.*` namespace | U-AS-31 | 7 |
| C-AS-14 | §14.8 Sampling discipline + audit-floor commitments | U-AS-32 | 7 |
| C-AS-14 | §14.9 D6 sampling-discipline alignment forward-reference | U-AS-32 | 7 |
| C-AS-15 | §15.1 Span hierarchy | U-AS-17 | 4 |
| C-AS-15 | §15.2 Seven `sandbox.*` attribute names | U-AS-16 | 4 |
| C-AS-15 | §15.3 `sandbox.tech` ↔ `sandbox.provider` join contract | U-AS-16 | 4 |
| C-AS-15 | §15.4 Sampling discipline | U-AS-18 | 4 |
| C-AS-15 | §15.5 Sensitive-data discipline | U-AS-17 | 4 |
| C-AS-15 | §15.6 Cross-axis composition reference | U-AS-19 | 4 |
| C-AS-15 | §15.7 Capability-floor (iv) traceability | U-AS-16 (acceptance 1.7) | 4 |
| C-AS-16 | §16.1 Sandbox-bounded span schema export | U-AS-33 | 8 |
| C-AS-16 | §16.2 5-axis multiplicative tunable export | U-AS-33 | 8 |
| C-AS-16 | §16.3 Secret-fetch audit export | U-AS-33 | 8 |
| C-AS-16 | §16.4 Six Anthropic-primitive attribute namespace export | U-AS-33 | 8 |
| C-AS-16 | §16.5 Per-tool `required_secrets` export | U-AS-33 | 8 |
| C-AS-16 | §16.6 Eleven-primitive adoption-depth matrix export | U-AS-33 | 8 |
| C-AS-16 | §16.7 Forcing-condition export | U-AS-33 | 8 |

Coverage row count: 74 spec sub-section rows; 100% coverage; zero spec gaps.

### §4.2 Inverse mapping — unit → contracts coverage

| Unit | Contracts/sections covered | Count |
|---|---|---|
| U-AS-01 | C-AS-01 §1.1, §1.2; C-AS-02 §2.4 (enum component) | 3 |
| U-AS-02 | C-AS-01 §1.3 | 1 |
| U-AS-03 | C-AS-04 §4.1, §4.2 (metadata), §4.3 (metadata) | 3 |
| U-AS-04 | C-AS-09 §9.1 axes; C-AS-10 §10.1 axes; C-AS-12 §12.2 axes | 3 |
| U-AS-05 | C-AS-02 §2.4 (default mapping) | 1 |
| U-AS-06 | C-AS-02 §2.3; C-AS-10 §10.2 (alignment) | 2 |
| U-AS-07 | C-AS-03 §3.1, §3.2, §3.3 | 3 |
| U-AS-08 | C-AS-02 §2.1, §2.2, §2.5 | 3 |
| U-AS-09 | C-AS-11 §11.1, §11.2, §11.3, §11.4 (within-call), §11.5 | 5 |
| U-AS-10 | C-AS-09 §9.1, §9.3, §9.5 | 3 |
| U-AS-11 | C-AS-09 §9.2 | 1 |
| U-AS-12 | C-AS-09 §9.4; C-AS-12 §12.2 (substrate); §12.3 (substrate) | 3 |
| U-AS-13 | C-AS-10 §10.1, §10.2, §10.3 | 3 |
| U-AS-14 | C-AS-12 §12.1, §12.2 (reference), §12.5 | 3 |
| U-AS-15 | C-AS-12 §12.4; C-AS-11 §11.4 (cross-deployment) | 2 |
| U-AS-16 | C-AS-15 §15.2, §15.3, §15.7 | 3 |
| U-AS-17 | C-AS-15 §15.1, §15.5 | 2 |
| U-AS-18 | C-AS-15 §15.4; C-AS-04 §4.3 (enforcement) | 2 |
| U-AS-19 | C-AS-15 §15.6 | 1 |
| U-AS-20 | C-AS-05 §5.1, §5.2, §5.4 | 3 |
| U-AS-21 | C-AS-05 §5.3 | 1 |
| U-AS-22 | C-AS-06 §6.1, §6.2 | 2 |
| U-AS-23 | C-AS-06 §6.3 | 1 |
| U-AS-24 | C-AS-07 §7.1, §7.2, §7.3 | 3 |
| U-AS-25 | C-AS-08 §8.1 | 1 |
| U-AS-26 | C-AS-08 §8.2, §8.3 | 2 |
| U-AS-27 | C-AS-08 §8.4, §8.5 | 2 |
| U-AS-28 | C-AS-13 §13.1, §13.2 | 2 |
| U-AS-29 | C-AS-13 §13.3, §13.4; C-AS-04 §4.2 (escalation chain) | 3 |
| U-AS-30 | C-AS-13 §13.5, §13.6 | 2 |
| U-AS-31 | C-AS-14 §14.1 through §14.7 | 7 |
| U-AS-32 | C-AS-14 §14.8, §14.9 | 2 |
| U-AS-33 | C-AS-16 §16.1 through §16.7 | 7 |

Inverse coverage: 33 units; every unit covers ≥1 spec sub-section. Zero orphan units.

### §4.3 Cross-cluster coverage (multi-cluster composition)

| Spec sub-section | Covering clusters | Composition rationale |
|---|---|---|
| C-AS-02 §2.4 | 1 (U-AS-01) + 2 (U-AS-05) | Enum declared at foundational Cluster 1; default mapping at Cluster 2 composition |
| C-AS-04 §4.2 | 1 (U-AS-03 metadata) + 7 (U-AS-29 escalation chain) | Per-class metadata at foundational unit; escalation chain composition at D3 Anthropic-primitive cluster |
| C-AS-04 §4.3 | 1 (U-AS-03 metadata) + 4 (U-AS-18 enforcement) | Always-sampled metadata at fail-class declaration; sampling enforcement at span emission |
| C-AS-10 §10.2 | 3 (U-AS-13 canonical) + 2 (U-AS-06 alignment) | Per-MCP-transport floor canonical at C-AS-10; alignment with §2.3 verified at U-AS-06 |
| C-AS-11 §11.4 | 2 (U-AS-09 within-call) + 3 (U-AS-15 cross-deployment) | Sub-agent monotonic-ascension at Cluster 2; cross-deployment bridging-arc at C-AS-12 cluster |
| C-AS-12 §12.2 | 3 (U-AS-12 canonical + U-AS-14 reference) | Canonical override-scope at §9.4 declaration site; reference at 5-axis composition |
| C-AS-12 §12.3 | 3 (U-AS-12 substrate) + 4 (U-AS-17 span emission) + 6 (U-AS-27 audit ledger) | Override-event audit composition spans three clusters |

### §4.4 Coverage audit verdict

| Audit dimension | Result |
|---|---|
| Aggregate spec coverage | ✅ 74/74 spec sub-sections covered |
| No orphan units | ✅ 33/33 units cover ≥1 spec sub-section |
| No coverage gaps | ✅ Every C-AS-NN section has ≥1 covering unit |
| Multi-cluster coverage is legitimate composition | ✅ All seven multi-cluster sub-sections are spec-explicit composition surfaces |
| Per OD-S2-2.A: per-axis matrix self-contained | ✅ Matrix declared at this section; no aggregate at Session 5 |
| Inheriting OD-S1-2.A precedent | ✅ Same posture as IS plan §4 |

**Stage 5 result: ✅ PASS at all coverage-discipline dimensions.**

---

## §[carry-forwards]

### [CF-1] F2-12 — D1 v1.1 → v1.2 replay-trace-emission contract

**Status.** 🔄 Deferred-acknowledged at ADD v1.2 §6.3.1 (inherited from PRD §[carry-forwards] [CF-1] and IS plan §[carry-forwards] [CF-1]).

**AS plan engagement.** U-AS-19 acceptance criterion 4.7 explicitly acknowledges F2-12 carry-forward: `idempotency_key` join behavior is uniform across replay scenarios (sandbox events join semantically regardless of whether the parent `tool.call` is a replay or fresh execution). No AS plan unit is open as a function of F2-12. F2-12 closure routes through Control Plane plan (Session 3) where D1 v1.1 → v1.2 lives — specifically, the replay-trace-emission contract concerns CP-axis C-CP-08 replay-resumption semantics + `retry.attempt` sibling-span discipline.

**Forward routing.** Parallel `council-orchestrator` C7+C9 session at operator discretion per ADD §6.3.1 active path. Closure expected as D1 v1.2 + D6 v1.2; absorbed into ADD v1.3; PRD revision pass produces `PRD_v1.1.md`; Phase 6 revision pass at affected plan sections (CP plan + OD plan). AS plan is **not** a revision target for F2-12 closure.

### [CF-2] Workflow §7 substrate-skill propagation

**Status.** Open operator decision; outside P6-CK closure scope; outside Phase 6 scope.

**Origin.** `Project_Workflow_Revision_log.md` v1.4 entry — `add-consolidation-protocol.md` §3.5 Step 5 substrate-skill update.

**AS plan engagement.** Not in AS plan scope (skill-substrate revision is neither architectural commitment nor observable behavior nor specification-grade contract nor implementation unit). Documented here for operator-visibility per inheritance from PRD §[carry-forwards] [CF-2] and IS plan §[carry-forwards] [CF-2].

**Forward routing.** Operator decision at discretion. No plan revision triggered by skill-substrate propagation.

---

## §[coherence pass]

Five audit dimensions per SKILL.md §5 step 9 + §4 four sub-disciplines + §10 anti-pattern audit.

### §5.1 Audit 1 — Atomicity (SKILL.md §3)

Per-unit verification: single coherent change (§3.1) + single focused session (§3.2) + independently testable (§3.3) + coherent rollback boundary (§3.4).

| Audit dimension | Result |
|---|---|
| §3.1 single coherent change | ✅ 33/33 units |
| §3.2 single focused session | ✅ 33/33 units |
| §3.3 independently testable | ✅ 33/33 units (with stub interfaces for cross-cluster + cross-axis composition) |
| §3.4 coherent rollback boundary | ✅ 33/33 units declare explicit rollback boundary |

**Audit 1 verdict: ✅ PASS at 132/132 cells.**

Notes: U-AS-31 carries six namespace declarations (40 attributes total) at upper edge of "single focused session"; justified as single coherent change = namespace family declaration; per-namespace split rejected on coherent-change grounds. U-AS-33 has 16 direct deps (largest in plan); justified by manifest's structural role as enumerator over every export carrier.

### §5.2 Audit 2 — Spec-traceability (SKILL.md §4 sub-discipline 2)

| Audit row | Result |
|---|---|
| Every unit cites ≥1 C-AS-NN ID + section number | ✅ 33/33 units |
| All 16 C-AS-NN contracts covered by ≥1 unit | ✅ verified at §4.1 matrix |
| Section-level citation discipline (not contract-ID-only) | ✅ every citation includes §N.N granularity |
| AS spec version-citation alignment (Workflow §7) | ✅ all citations point to v1.1 |
| Cross-axis IS citations resolve to IS plan v1 units | ✅ all 13 cross-axis edges cite U-IS-NN IDs declared in IS plan v1 §2 |
| No fabricated section citations | ✅ every cited §N.N verified at substrate-read stage |

**Audit 2 verdict: ✅ PASS at all rows.**

### §5.3 Audit 3 — Dependency-awareness (SKILL.md §4 sub-discipline 3 + §7)

| Audit dimension | Result |
|---|---|
| Every unit declares `Depends on:` explicitly | ✅ 33/33 units |
| Acyclic invariant (within-axis) | ✅ DAG verified by Kahn's algorithm at §3.3 |
| Foundational-first ordering | ✅ L0 = U-AS-01, U-AS-03, U-AS-04 |
| Cross-axis edges flagged `(cross-axis: IS)` | ✅ 13/13 cross-axis edges annotated |
| Cross-axis edges do not engage within-axis cycle check | ✅ IS plan filed prior; AS → IS direction only |
| No transitive omission | ✅ Sample verification at §3.6.1 |
| Coverage discipline (deps sufficient for acceptance) | ✅ Sample verification at §3.7 |
| Cross-axis declarations resolve to U-IS-17 carrier-units | ✅ 8 distinct U-IS-NN units cited; all in U-IS-17 manifest |

**Audit 3 verdict: ✅ PASS at all dimensions.**

### §5.4 Audit 4 — Implementation-grade-detail (SKILL.md §4 sub-discipline 4)

| Audit dimension | Result |
|---|---|
| Every unit names logical files affected | ✅ 33/33 units |
| Every unit names function / class / schema signatures | ✅ 33/33 units in code-block form |
| Every unit has testable acceptance criteria | ✅ 33/33 units |
| Every unit has named tests | ✅ 33/33 units; `test_<unit>_<criterion>` convention |
| No library/framework/protocol introductions beyond spec | ✅ SHA-256, RFC 8785 JCS, MCP authorization 2025-06-18, OTel — all spec-cited |
| No spec extension at unit level | ✅ every introduced type is typed factor-out of spec content |
| No PR / commit / filesystem-path granularity pre-commitment | ✅ all file names at logical level |

#### §5.4.1 Auxiliary type introductions — spec-extension audit

47 auxiliary typed entities (enums, records, interfaces) introduced. Each verified as faithful factor-out:

| Auxiliary type class | Examples | Spec anchor |
|---|---|---|
| Composition-result enums | `SandboxTierFloorResult`, `SandboxTierCompositionResult`, `AllowlistDecision`, `OverrideScopeResult` | Spec result-discriminator language at composition formulas |
| Forward-declared interfaces | `FloorInterfaces`, `GateLevelFloorInterfaces`, `SubAgentKeyDerivationStrategy` | Spec cross-axis composition declarations (filled by CP plan) |
| Metadata records | `SandboxTierMetadata`, `SandboxFailClassMetadata`, `ProviderClassMetadata`, `SandboxAttributeSchema` | Spec per-row table content |
| Discriminator enums | `MechanismClass`, `MCPTrustLevel`, `AnthropicModel`, `D1EngineClass`, `OutageBehavior`, `TPerm2Pole` | Spec column values typed for compile-time correctness |
| Violation records | `NegativeObservationViolation`, `PassthroughViolation`, `SubAgentBoundaryViolation`, `GovernanceViolation` | Spec violation-detection language |
| Export manifest types | `ASSeamId`, `ASConsumingAxis`, `ASSubstrateSeamExport` | Spec §16 export-surface enumeration |

Every auxiliary type is a typed representation of spec content, not a new commitment.

**Audit 4 verdict: ✅ PASS at all dimensions.**

### §5.5 Audit 5 — Anti-pattern audit (SKILL.md §10)

| Anti-pattern | Audit result |
|---|---|
| Under-decomposition | ✅ NOT PRESENT — largest unit (U-AS-31) is single-session scope |
| Over-decomposition | ✅ NOT PRESENT — smallest units are coherent functional surfaces |
| Spec extension | ✅ NOT PRESENT — auxiliary types audited at §5.4.1 |
| Vague acceptance | ✅ NOT PRESENT — every criterion testable |
| Cyclic dependencies | ✅ NOT PRESENT — DAG verified at §3.3 |
| Missing dependencies | ✅ NOT PRESENT — coverage discipline at §3.7 |
| Under-specified acceptance | ✅ NOT PRESENT — every acceptance has named tests |
| Coverage gaps | ✅ NOT PRESENT — 74/74 sub-sections covered at §4.1 |
| Risk / estimate annotations | ✅ NOT PRESENT |
| Trace-omission | ✅ NOT PRESENT — every unit cites C-AS-NN §N.N |
| PR / commit / filesystem-path granularity | ✅ NOT PRESENT — all file names at logical level |
| Confidence-schema redefinition | ✅ NOT PRESENT — V3 schema preserved |
| Citation invention | ✅ NOT PRESENT — all citations verified |

**Audit 5 verdict: ✅ PASS at all 13 anti-patterns.**

### §5.6 Coherence pass aggregate

| Audit | Dimensions | Result |
|---|---|---|
| Audit 1 — Atomicity (§3) | 4 criteria × 33 units = 132 cells | ✅ PASS |
| Audit 2 — Spec-traceability (§4.2) | 6 rows | ✅ PASS |
| Audit 3 — Dependency-awareness (§4.3, §7) | 8 dimensions | ✅ PASS |
| Audit 4 — Implementation-grade-detail (§4.4) | 7 dimensions + 47 auxiliary type audit | ✅ PASS |
| Audit 5 — Anti-pattern audit (§10) | 13 anti-patterns | ✅ PASS |

**Coherence pass aggregate: ✅ PASS at all five audit dimensions.**

Plan authorized for filing.

---

## Filing footer

| Field | Value |
|---|---|
| Status | Filed at `/mnt/user-data/outputs/Implementation_Plan_Action_Surface_v1.md` (Phase 6 Session 2 close) |
| Aggregate adversarial review | Deferred to Phase 6 Session 5 close per `Phase_6_Entry_Handoff.md` §1.1 OD-6-4.A; standalone P6-CK then runs against cross-axis composition output |
| Operator action | Push from `/mnt/user-data/outputs/` to `/mnt/project/Implementation_Plan_Action_Surface_v1.md` at session close |
| Next session | Phase 6 Session 3 (Control Plane axis) per session prompt `/mnt/user-data/outputs/Phase_6_Session_3_Session_Prompt.md` |
| Exit-gate verification | 9/9 criteria met (per session prompt §7); §[coherence pass] returns ✅ PASS |

**Plan filed.** v1 implementation plan for AS axis closes Phase 6 Session 2.