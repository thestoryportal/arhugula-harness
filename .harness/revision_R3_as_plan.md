# Revision R3 — Action Surface Plan: Materializability + Verbatim Conformance

**Status:** Proposed
**Revision pass:** R3 — AS plan v1 → v1.1 (third of the 5-pass carrier-map absorption sequence R1–R5; R1 harness-core landed, R2 IS in flight).
**Authored:** 2026-05-15 by the `implementation-planner` role in revision-pass sub-mode (`implementation-planner` SKILL.md §8).
**Mode:** Revision-pass. This is a **revision proposal artifact**, not an applied plan edit. The operator ratifies before any `design-substrate/` plan is amended.

**HARD WALL.** This pass writes only `.harness/revision_R3_as_plan.md`. No `design-substrate/` file, no `CLAUDE.md`, no plan/spec/audit/carrier-map, no source code is edited. No git commit.

---

## §0 Change-note

### §0.1 Trigger

Two ratified upstream recommendations plus one canonical systemic-tension record:

- `.harness/verbatim_audit_as_plan.md` — the Q1 plan-wide systemic audit of `Implementation_Plan_Action_Surface_v1.md` (all 33 units). This audit **is** the canonical AS systemic-tension record (the way `verbatim_audit_cp_plan.md` was for CP); it supersedes `pipeline-fork-queue.md` items 9–15 and the per-unit provisional classifications. Verdict tally: **18 CLEARED · 3 CONFORM · 12 FORK.** It found two distinct systemic diseases — Pattern A (verbatim-claim divergence, 7 units) and Pattern B (undeclared auxiliary types, ≥7 units / ≥11 types).
- `.harness/shared_type_carrier_map.md` (T1) — the ratified carrier triage; its disposition rows place every AS Pattern B type.
- `.harness/xal3_resolution_recommendations.md` (T2) — the X-AL-3 design-extension verdicts: **27 of 27 candidates resolved FACTOR-OUT, 0 genuine extensions.** The AS Pattern B set requires **zero design-substrate revision** — every type is a faithful factor-out of spec/ADR prose with a missing declaration site.
- `.harness/revision_R1_harness_core.md` §3.2 + §4 — the R1 hand-off to AS: U-AS-04 is a declaration-site conversion; U-AS-30 needs a `WorkloadClass` edge; U-AS-02 is a landed unit needing a retrospective re-check.

R3 is the **third** of the five carrier-map absorption passes (R1 `harness-core` / R2 IS / R3 AS / R4 CP / R5 OD). R1 has landed `Implementation_Plan_Harness_Core_v1_0.md` (U-CORE-01); R3 cites it. AS consumes only IS + `harness-core` upstream (carrier map "Recommended ordering"); R3 is unblocked.

### §0.2 Scope of R3

| In scope | Out of scope |
|---|---|
| Pattern B carrier disposition for all AS undeclared types (§1) | Editing any `design-substrate/` plan or spec (operator applies post-ratification) |
| Pattern A verbatim conformance for the plan-determinate units (§2) | Authoring the C-AS-02 §2.2/§2.3/§11.1 spec fix — that is `spec-writer`'s scope, conditional on the §9 operator decision |
| U-AS-04 declaration-site conversion (§3) | CP / OD / IS plan revisions (R2/R4/R5 scope) |
| U-AS-02 landed-source retrospective flag (§4) | The U-CORE-01 carrier itself (R1 scope; landed) |
| Revised unit bodies for all FORK + CONFORM units (§5) | New CXA edges (CXA v2.1 §2.3 covers AS→IS; R3 only re-cites revised IS units) |
| The permanent auxiliary-type-audit section, structural fix (§6) | |

### §0.3 The two AS defect axes (unlike IS, AS carries both)

The AS plan is the only per-axis plan exhibiting **both** systemic diseases the audit pipeline found:

1. **Pattern A — verbatim-claim divergence (7 units).** A plan unit asserts a signature/enum is materialized "per §X verbatim" against a `Spec_Action_Surface` contract the signature does not transcribe. Sub-shapes: A1 enum-member substitution at matching cardinality (U-AS-08, U-AS-12); A2 signature carries a parameter the cited contract omits (U-AS-06, U-AS-09, U-AS-20); A3 acceptance criterion asserts a spec property the cited section does not contain (U-AS-10, U-AS-28). §2 of this proposal conforms the plan-determinate units; the §9 spec-gap units stay conditional.
2. **Pattern B — undeclared auxiliary types (≥7 units, ≥11 types).** A type is consumed at a typed signature position with no `record`/`enum` declaration site and no carrier in the consuming unit's `Depends on` cone. T2 verified all are spec-committed factor-outs. §1 re-points each to its ratified carrier.

### §0.4 CONFORM propagation (3 units — clear automatically, bodies preserved verbatim)

The 3 CONFORM units are **propagation-gated, not independently defective** — they clear once the divergent unit they cite conforms. Their unit bodies are **`[preserved verbatim]`** — no body edit. The propagation is recorded here so the operator sees it is handled:

- **U-AS-16** acc #6 cites U-AS-08's `AssignedTierReason` as the carrier for `sandbox.policy.assigned_tier_reason`. Once U-AS-08's enum conforms to the spec §15.2 7-value set (§2 below), U-AS-16 acc #6 resolves to the conformed enum automatically. U-AS-16's own seven `sandbox.*` attribute names + the tech/provider join transcribe §15.2/§15.3 faithfully — no body edit. **Citation unchanged (U-AS-08); referent member set conformed.**
- **U-AS-22** transcribes `SecretAllowlistEntry` per §6.1 faithfully. Its only defect is the carrier-ordering relative to U-AS-07 (U-AS-22 declares `SecretAllowlistEntry`, but U-AS-07 forward-consumes it as a `ToolContract.required_secrets` element type while U-AS-22 `Depends on` U-AS-07). The fix lives in **U-AS-07's revised body** (§5): U-AS-07 declares the interim element shape. U-AS-22's body is preserved verbatim; the graph edge is the fix.
- **U-AS-33** is the AS substrate seam exports manifest. Its 7-entry structure holds; the carrier-unit citations point at unit IDs (U-AS-08/09/10/28/30) that **do not change** under R3 — only the member sets / signatures inside those units change. The manifest stays valid. U-AS-33's body is preserved verbatim.

### §0.5 Type inventory delta

`Implementation_Plan_Action_Surface_v1.md` before R3: ~11 auxiliary types consumed at signature positions with **no declaration site** (`ToolMetadata`, `TaintState`, `MCPServer`, `AnchorCitation`, `ToolContext`, `RawContractInput`, `ExtendedThinkingEffort`, `BatchApiCell`, `WorkloadManifestOverrides`, `Provider`, `ModelClass`); plus `SecretAllowlistEntry` carrier-ordering; plus `SecretScope` ellipsis-body.

`Implementation_Plan_Action_Surface_v1.1` after R3: every type above has a named declaring carrier unit + an in-cone `Depends on` edge OR a `harness-core` import. `DeploymentSurface`/`PersonaTier` move OUT of the AS plan (to `harness-core` U-CORE-01); `MCPTransport` stays AS-owned at U-AS-04.

### §0.6 Decision-vocabulary posture

Per the carrier map / T2 vocabulary: **decided** (authority-chain-determinate — R3 applies it) / **proposing** (recommendation, operator confirms placement) / **open** (genuinely owed to the operator — R3 writes a conditional body, does not pick). The four operator-decision items (U-AS-06/09 spec gap, U-AS-12 reading, U-AS-20 direction) are **open** — §5 gives each a conditional body, not a guessed one.

### §0.7 Sections preserved verbatim

All 18 CLEARED units (U-AS-01, 03, 05, 11, 13, 15, 17, 18, 19, 21, 23, 24, 25, 26, 27, 29, 31, 32) and all 3 CONFORM units (U-AS-16, U-AS-22, U-AS-33) — **21 of 33 unit bodies preserved verbatim.** 12 FORK units carry a revised body (§5). §3 (dependency graph) + §4 (coverage matrix) of the plan take the deltas at §7/§8 of this proposal. A new §5.4.2 permanent auxiliary-type audit (§6 of this proposal) is added.

## §1 Pattern B — undeclared auxiliary types: carrier disposition

Every AS Pattern B type, its T1 carrier-map disposition, its T2 X-AL-3 verdict (all FACTOR-OUT), and the R3 carrier action. Per T2 §Summary, **no AS Pattern B type requires a design-substrate revision** and **no new standalone AS carrier unit is needed** — every type is declared in-place in its first-consuming AS unit. The "~5 AS-owned X-AL-3 factor-outs" the task names are the T2 AS-owned design-extension-candidate set: `ToolMetadata`, `TaintState`, `MCPServer`, `RawContractInput`, `WorkloadManifestOverrides` — all verdict FACTOR-OUT, all declared in-place.

### §1.1 Carrier disposition table

| Type | Consuming unit(s) | T1 disposition | T2 verdict / spec basis | R3 carrier action | Status |
|---|---|---|---|---|---|
| `ToolMetadata` | U-AS-06 (`sandbox_tier_floor` `tool` param) | 2 — AS-owned | FACTOR-OUT — AS spec §2.2 commits `sandbox_tier(tool, ...)`; the tool-metadata input is the contract subject; §3 commits `minimum_tier` authoring | Declare `record ToolMetadata` **in U-AS-06** (the first-consuming unit). Fields = the §2.3 lookup inputs the row conditions need (`is_deterministic_inhouse`, `forces_computer_use`, `forces_code_execution`) — already named in U-AS-06's Inputs prose; promote prose to a `record`. | proposing |
| `TaintState` | U-AS-08 (`CallSiteContext.taint_state`) | 2 — AS-owned | FACTOR-OUT — AS spec §2.2 commits `blast_radius_floor(call_site_context.taint_state)`; §2 "Deferred to implementation discretion" names "taint-state propagation mechanism" | Declare `enum TaintState` **in U-AS-08** beside `CallSiteContext`. Field set deferred to plan per the §2 deferral clause — declare a closed enum with the taint poles the §2.2 `blast_radius_floor` call discriminates. | proposing |
| `MCPServer` | U-AS-08 (`CallSiteContext.mcp_server`, `FloorInterfaces`); U-AS-14 (`GateLevelFloorInterfaces`) | 2 — AS-owned | FACTOR-OUT — AS spec §2.2 commits `mcp_server_trust_tier_floor(call_site_context.mcp_server)`; §10 commits the MCP transport / trust-level surface | Declare `record MCPServer` **in U-AS-08** (first-consuming unit). U-AS-14 consumes it via a `Depends on: [U-AS-08]` edge (already present — U-AS-14 depends on U-AS-06; add U-AS-08). See §7 graph delta. | proposing |
| `AnchorCitation` | U-AS-28 (`ANTHROPIC_PRIMITIVE_ANCHORS` map value type) | 2 — AS-owned | FACTOR-OUT — AS spec §13.1 commits the eleven-primitive enumeration with primary-source anchors ([HIGH]-tagged) | Declare `record AnchorCitation` **in U-AS-28**. Fields = the citation shape the §13.1 [HIGH] anchors carry (source identifier + confidence tag). | proposing |
| `ToolContext` | U-AS-02 (`forced_tier` param — **LANDED unit**); U-AS-10 (`lookup_cell_with_forcing` param) | 2 — AS-owned | FACTOR-OUT — AS spec §1.3 commits the computer-use / code-execution-beta forcing conditions; `ToolContext` carries the two forcing flags | Declare `record ToolContext` **in U-AS-02** (the first-consuming unit, currently landed — see §4 retrospective). Fields = `computer_use_bound: bool`, `code_execution_beta_invoked: bool` — already in U-AS-02's Inputs prose. U-AS-10 consumes via its existing `Depends on: [U-AS-02]` edge. | proposing |
| `RawContractInput` | U-AS-07 (`validate_tool_contract_at_registration` param) | 2 — AS-owned | FACTOR-OUT — AS spec §3 commits `validate_tool_contract_at_registration` semantics; the registration-input is the §3 contract subject | Declare `record RawContractInput` **in U-AS-07** — the pre-validation tool-contract serialization shape (the un-validated counterpart of `ToolContract`). | proposing |
| `ExtendedThinkingEffort` | U-AS-30 (`WorkloadBindingDecision.extended_thinking_effort`) | 2 — AS-owned | FACTOR-OUT — AS spec §13.6 step 6 commits "Operator selects extended-thinking effort per cell" | Declare `enum ExtendedThinkingEffort` **in U-AS-30**. Closed enum of the effort levels §13.6 step 6 commits. | proposing |
| `BatchApiCell` | U-AS-30 (`WorkloadBindingDecision.batch_api_cells`) | 2 — AS-owned | FACTOR-OUT — AS spec §13.6 step 7 commits "binds Batch API cells" | Declare `record BatchApiCell` **in U-AS-30**. The §13.6 step-7 batch-cell binding shape. | proposing |
| `WorkloadManifestOverrides` | U-AS-30 (`compose_workload_binding_decision` param) | 2 — AS-owned | FACTOR-OUT — AS spec §13.6 "Workload-binding-time" surface commits "Workload manifest declares per-workload sandbox-tier overrides … provider-instance preferences" | Declare `record WorkloadManifestOverrides` **in U-AS-30** — the operator-override input shape the §13.6 manifest surface commits. | proposing |
| `Provider` | U-AS-30 (`C6_CROSS_FAMILY_FALLBACK_CHAIN` element type) | 2 — AS-owned (AS-30 use) | FACTOR-OUT — AS spec §13.5 row 4 commits the cross-family fallback chain `anthropic → bedrock → vertex → openai → ollama`; ADR-F1 v1.2 multi-LLM commitment | Declare `enum Provider` **in U-AS-30** — closed at the 5 §13.5-row-4 family identifiers. | proposing |
| `ModelClass` | U-AS-30 (`C6_CROSS_FAMILY_FALLBACK_CHAIN` element type) | 2 — AS-owned (AS-30 use) | FACTOR-OUT — AS spec §13.5 row 4 cross-family fallback element pairs `(Provider, ModelClass)` | Declare `enum ModelClass` **in U-AS-30** — the model-class identifier the §13.5 fallback-chain pairs carry. | proposing |
| `SecretAllowlistEntry` (carrier-ordering) | U-AS-07 (`ToolContract.required_secrets` element); declared by U-AS-22 | 2 — AS-owned (U-AS-22) | — (no X-AL-3 concern; faithful §6.1 transcription) | **Carrier-ordering fix.** U-AS-07 forward-consumes `SecretAllowlistEntry` as the `required_secrets` element type, but U-AS-22 (which declares it) `Depends on` U-AS-07. R3 fix: U-AS-07's revised body specifies the **interim element shape** — `required_secrets` declared as `List<SecretAllowlistEntry>` with `SecretAllowlistEntry`'s field set forward-declared at U-AS-07 (the §6.1 2-field shape `{name, scope}`), then U-AS-22 *populates the access-control semantics* against the already-declared shape. No graph cycle: the type shape moves up to U-AS-07; U-AS-22 keeps the allowlist-intersection function. | decided |
| `SecretScope` (ellipsis body) | U-AS-20 declares `record SecretScope { ... }`; consumed by U-AS-22/24/26/27/30 | 2 — AS-owned (U-AS-20) | — (Class-1 documentation drift per Q1) | **Field-set fix.** U-AS-20's revised body replaces the `{ ... }` ellipsis with the explicit field set. Spec §5.4 sanctions deferring *serialization*, not the *field set*. R3 declares the `SecretScope` field set per the §5.1 `scope` parameter semantics; serialization format stays deferred. | decided |

### §1.2 Cross-cutting types that LEAVE the AS plan (handed to `harness-core` U-CORE-01)

Two enums U-AS-04 currently *declares* are cross-cutting `harness-core` residents per R1 / U-CORE-01 (landed):

| Type | R1/U-CORE-01 disposition | R3 action |
|---|---|---|
| `DeploymentSurface` | `harness-core` resident — declared at U-CORE-01 | U-AS-04 converts from declaring site to importing site (§3 below) |
| `PersonaTier` | `harness-core` resident — declared at U-CORE-01 | U-AS-04 converts from declaring site to importing site (§3 below) |
| `MCPTransport` | **AS-owned** — carrier map "already-declared" table, *proposing*, NOT a U-CORE-01 type | **Stays declared at U-AS-04.** No change to `MCPTransport`. |

### §1.3 Types correctly NOT treated as Pattern B (transparency)

Per the Q1 audit Findings-rejected list, the following are **not** undeclared-type findings and R3 declares no carrier for them:

- **Cross-axis IS types** — `StateLedgerEntry`, `IdempotencyKey`, `Actor`, `Bytes32`, `ISO8601Timestamp`, `FilesystemPathContract`, `ChainVerificationResult` — arrive via declared `(cross-axis: IS)` edges to U-IS-07/08/09/10/11/01/02; carrier resolves out-of-axis-in-cone. R3 verifies these edges still cite live IS units after the R2 IS revision (§7.3).
- **Stack / OTel-SDK primitives** — `JSONSchema`, `SpanId`, `MonotonicTimestamp`, `AttributeValue`, `AttributeValueType`, `Cardinality` — `Target_Stack_Commitment` adoptions, the analog of `str`/`int`. No harness carrier.
- **Identity aliases** — `UnitId` (consumed at U-AS-33 `carrier_units: List<UnitId>`) — a U-CORE-01 plan-internal identity alias (R1 Q-R1-5, operator-ratified). U-AS-33 imports it from `harness-core`. See §7.2.

## §2 Pattern A — verbatim-claim conformance (7 units)

The 7 Pattern A units split into two classes by the §4A authority-chain analysis:

- **Plan-determinate (4 units — R3 conforms the body):** U-AS-08, U-AS-10, U-AS-12-Reading-A-portion, U-AS-28. The spec is canonical for the plan; the plan diverged; R3 conforms plan→spec. The conformed bodies are at §5.
- **Operator-decision (3 units — R3 writes a conditional body):** U-AS-06, U-AS-09 (the `sandbox_tier_floor` spec gap — see §9), U-AS-20 (conformance-direction operator decision), and U-AS-12 (Reading A vs B). For these, R3 does **not** pick — §5 gives each a body skeleton with explicit `[Option A | Option B]` branches.

### §2.1 The plan-determinate conformance instructions

| Unit | Divergence | Conformance (R3 applies — `decided`) |
|---|---|---|
| **U-AS-08** | `AssignedTierReason` plan 7-value set `{CONTRACT_MINIMUM, BLAST_RADIUS_FLOOR, MCP_SERVER_TRUST_FLOOR, OPERATOR_POLICY_FLOOR, SANDBOX_TIER_FLOOR, COMPUTER_USE_FORCING, CODE_EXECUTION_FORCING}` substitutes `COMPUTER_USE_FORCING`/`CODE_EXECUTION_FORCING` for spec §15.2's `persona_tier_floor`/`sub_agent_monotonic_ascension`. Cardinality 7 matches; member set diverges (A1). | Conform `AssignedTierReason` to the spec §15.2 7-value set **verbatim**: `CONTRACT_MINIMUM, BLAST_RADIUS_FLOOR, MCP_SERVER_TRUST_FLOOR, OPERATOR_POLICY_FLOOR, SANDBOX_TIER_FLOOR, PERSONA_TIER_FLOOR, SUB_AGENT_MONOTONIC_ASCENSION` (SCREAMING_SNAKE rendering of the §15.2 lowercase-snake set). The forced-tier causes (`COMPUTER_USE_FORCING`/`CODE_EXECUTION_FORCING`) are **not** lost — they belong on the `ForcedTierCause` enum already declared at U-AS-02 (`COMPUTER_USE_BOUND`/`CODE_EXECUTION_BETA`); U-AS-08 acc #2 routes forced-tier results through that enum. The `assigned_tier_reason` enum is the §15.2 audit-surface enum and conforms to §15.2 only. |
| **U-AS-10** | AC2 names provider-class `PROCESS_FS_OVERLAY`; the carrier enum `SandboxProviderClass` (U-AS-11, in-cone, CLEARED) has no such member — its members are `LANGUAGE_LEVEL`, `FILESYSTEM_OVERLAY_WORKTREE`, `PROCESS_ULIMIT_BUBBLEWRAP_SEATBELT`, `CONTAINER`, `MICROVM_FIRECRACKER`, `FULL_VM` (§9.2). | Re-state U-AS-10 AC2 against the **actual U-AS-11 / spec §9.2 member set**. The plan AC2 row-by-row text must name `LANGUAGE_LEVEL` / `FILESYSTEM_OVERLAY_WORKTREE` / `PROCESS_ULIMIT_BUBBLEWRAP_SEATBELT` / `CONTAINER` / `MICROVM_FIRECRACKER` / `FULL_VM` per the §9.1 12-cell matrix — never the non-existent `PROCESS_FS_OVERLAY`. The matrix *content* (which tier/provider per cell) transcribes §9.1; only the identifier vocabulary is the fix. |
| **U-AS-28** | AC1 claims `AnthropicPrimitive` is declared "exactly 11 values per §13.1 verbatim **kebab-case**" + test `test_anthropic_primitive_identifier_strings_byte_exact_per_spec_13_1`; but §13.1 is a **prose name table** ("Skills system", "MCP-as-code", …) with **no machine-identifier column**, and U-AS-28's own Signatures block is SCREAMING_SNAKE. The "kebab-case verbatim" claim has no spec-side string set to match (A3). | Drop the "kebab-case verbatim per §13.1" framing and the `test_anthropic_primitive_identifier_strings_byte_exact_per_spec_13_1` test. §13.1 commits the **eleven-primitive concept enumeration** (a prose name table) — the spec-traceable claim is *cardinality 11 + the concept-name → enum-member mapping*, not a byte-exact string set. SCREAMING_SNAKE is FM-D Python-stack naming convention (not a divergence). Revised AC1: "`AnthropicPrimitive` declares exactly 11 members, one per the §13.1 prose name table entry, mapped concept-name → SCREAMING_SNAKE member." Replacement test: `test_anthropic_primitive_cardinality_eleven_one_per_spec_13_1_concept`. |

### §2.2 The operator-decision Pattern A units (R3 conditional bodies)

| Unit | The decision owed | R3 posture |
|---|---|---|
| **U-AS-06** | The `sandbox_tier_floor` signature gap — a SPEC under-specification (§9). C-AS-02 §2.2 call site threads 4 args; §2.3 table rows 4–6 need `mcp_trust_level`; §11.1 inner call threads 3. The spec contradicts itself. | R3 cannot conform U-AS-06 to a spec section that is itself incomplete. §5 gives U-AS-06 a conditional body branching on the §9 spec decision. **Open.** |
| **U-AS-09** | Same `sandbox_tier_floor` gap, consumer-side: `sub_agent_sandbox_tier` plan signature has 5 params (adds `mcp_trust_level`); spec §11.1 has 4. Folds into the U-AS-06 spec reconciliation. | §5 gives U-AS-09 a conditional body keyed to the same §9 decision. **Open.** |
| **U-AS-20** | `fetch_secret` plan declares 3 params `(name, scope, tier)`; spec §5.1 + C-AS-05 title fix it at 2 `(name, scope)`. Two readings: **R1** spec adopts the 3-param form (Phase-5 spec revision); **R2** plan reverts to 2 params + context object. The audit explicitly does not pick. | §5 gives U-AS-20 a body with `[Option R1 | Option R2]` branches. **Open.** |
| **U-AS-12** | `override_scope` AC2 reads "SOLO_DEVELOPER → PERMITTED_APPEND_ONLY at any cell"; spec §9.4 reads solo-developer permitted "at **non-compliance cells**". Two readings: **A** "non-compliance cells" = "any cell" for the solo persona (claim merely loose — plan-internal text fix); **B** plan over-permits and `override_scope` is under-typed (its `(DeploymentSurface, BlastRadiusTier)` inputs cannot evaluate "compliance cell"). | §5 gives U-AS-12 a body with `[Reading A | Reading B]` branches. Under Reading A only the AC text changes; under Reading B the signature gains a compliance-status input. **Open.** |

## §3 U-AS-04 declaration-site conversion

Per `revision_R1_harness_core.md` §3.2 hand-off and `Implementation_Plan_Harness_Core_v1_0.md` (U-CORE-01, landed): U-AS-04 currently **declares** `DeploymentSurface`, `PersonaTier`, and `MCPTransport`. R1 / U-CORE-01 promoted `DeploymentSurface` + `PersonaTier` to `harness-core` residents. R3 converts U-AS-04 from a *declaring* site to a *consuming* (importing) site for those two enums. **`MCPTransport` stays AS-owned and declared at U-AS-04** (carrier map "already-declared" table — *proposing*, not a U-CORE-01 type).

This is a **declaration-site conversion**, not just an edge add — three things change in U-AS-04's body (full revised body at §5):

1. **Signatures block:** delete the `enum DeploymentSurface { ... }` and `enum PersonaTier { ... }` declarations. Retain `enum MCPTransport { ... }` unchanged. Add an import line: `import { DeploymentSurface, PersonaTier } from harness-core` (U-CORE-01 product).
2. **`Implements` line:** the U-AS-04 `Implements` currently cites `[C-AS-02 §2.3; C-AS-09 §9.1 (forward use); C-AS-12 §12.2 (forward use); C-AS-10 §10.1 (forward use)]`. After conversion U-AS-04 no longer *declares* the `DeploymentSurface`/`PersonaTier` types — C-AS-09 §9.1's deployment-surface axis and the persona-tier ladder are covered at U-CORE-01. U-AS-04's `Implements` reduces to the contract it still covers: `[C-AS-10 §10.1]` (the `MCPTransport` 5-value transport-level set). The C-AS-09 §9.1 / C-AS-12 §12.2 forward-use citations move off U-AS-04 — see §8 coverage delta.
3. **`Depends on` line:** changes from `(none)` to `[U-CORE-01 (cross-axis: core)]` — the import edge. Per R1 §3, a `harness-core` import is flagged cross-axis but is an *import* edge, not an outbound CXA edge.
4. **Acceptance criteria:** ACs 1 and 2 (the `DeploymentSurface` cardinality-3 and `PersonaTier` cardinality-3 + ordering claims) **move to U-CORE-01** (which already carries `test_deployment_surface_cardinality_three` etc.). U-AS-04's revised ACs retain only the `MCPTransport` claims (AC3 cardinality-5, the relevant AC4 cardinality-bound clause, AC5 identifier-strings, AC6 pure-data-type) — restated for `MCPTransport` alone. The cardinality-bound AC4 drops the `3/3` bounds and keeps `5` for `MCPTransport`.

**U-AS-04 is a LANDED unit** (operational-minimum set, per `.harness` memory — it declares the foundational L0 enums). The conversion therefore carries a **landed-source re-check action item** identical in kind to the U-AS-02 retrospective (§4): R3-application must verify the landed U-AS-04 source deletes the local `DeploymentSurface`/`PersonaTier` definitions and re-points to the `harness-core` import, and that the landed enum values matched U-CORE-01 byte-exact before deletion (they do — `local-development | self-hosted-server | managed-cloud` and `solo-developer | team-binding | multi-tenant-compliance` are identical in U-AS-04 v1 and U-CORE-01). Recorded as **R3-application action item A-1** (§10).

## §4 U-AS-02 retrospective

U-AS-02 is **LANDED** (operational-minimum, 2026-05-15). Its Signatures block declares `function forced_tier(ctx: ToolContext)` and its Inputs prose describes `ToolContext` as "carrying `computer_use_bound: bool` and `code_execution_beta_invoked: bool`" — but **no unit, U-AS-02 included, declares a `record ToolContext`**. U-AS-02 `Depends on: [U-AS-01]`; U-AS-01 does not declare `ToolContext`. U-AS-02 therefore **landed against an undeclared type** — the Pattern B shape, in a unit already in `state.jsonl`.

R3's Pattern B disposition (§1.1) assigns the `ToolContext` carrier to **U-AS-02 itself** — it is the first-consuming unit. R3's revised U-AS-02 body (§5) declares `record ToolContext { computer_use_bound: bool; code_execution_beta_invoked: bool }`, promoting the Inputs prose to a `record`.

Because U-AS-02 is landed, R3 cannot assume the revised plan body and the landed source agree. **R3-application action item A-2 (§10):** before any further AS unit consuming `ToolContext` lands (U-AS-10 is the next such unit, and it is FORK-blocked anyway), a retrospective check of the landed U-AS-02 source must confirm:

1. **(i) field-completeness** — the landed `ToolContext` materialization (whether inline-materialized from the Inputs prose at landing, or a bare `str`/`Any` placeholder, or imported from a sibling) is field-complete against the §5 revised body: exactly `computer_use_bound: bool` + `code_execution_beta_invoked: bool`.
2. **(ii) shape-consistency** — the landed materialization matches the field set R3's §5 body gives `ToolContext`. If the landed code inlined a different shape or merged `ToolContext` into another record, the landed U-AS-02 must be revised to match the R3 carrier.

If the landed source already inline-materialized `ToolContext` field-complete and consistent, the retrospective is a no-op confirmation. If not, **U-AS-02 must be re-visited** — the operator should not treat U-AS-02's landed status as closing the Pattern B gap. This is a §2.7.6 **Class 3 (informational)** back-flow logged against the Phase 7 execution log; the retrospective check is the operator action it triggers. It is the AS-pass's responsibility (a source-vs-plan reconciliation); R3 flags it so it is not missed. R3 itself does not touch source (HARD WALL).

> **Note — U-AS-02 is also a CONFORM-adjacent beneficiary of the U-AS-08 fix.** The §2 U-AS-08 conformance routes forced-tier causes through U-AS-02's existing `ForcedTierCause` enum (`COMPUTER_USE_BOUND`/`CODE_EXECUTION_BETA`). U-AS-02's `ForcedTierCause` is unchanged by R3 — it already transcribes spec §1.3 faithfully. The retrospective is purely about the `ToolContext` carrier, not `ForcedTierCause`.

## §5 Revised unit bodies (12 FORK units)

Full revised bodies for every FORK unit. CONFORM units (U-AS-16, U-AS-22, U-AS-33) are **`[preserved verbatim]`** per §0.4 — not restated here. CLEARED units (18) are `[preserved verbatim]` — not restated. Only the **changed** elements of each unit are shown with a `CHANGE:` annotation; unchanged elements are marked `[unchanged]`. On ratification these transcribe into `Implementation_Plan_Action_Surface_v1.1.md`.

---

### U-AS-02 — Implement forced-tier resolution predicates (computer-use + code-execution beta)

`[Pattern B carrier — ToolContext. Landed unit; see §4 retrospective.]`

- **Implements:** `[C-AS-01 §1.3]` `[unchanged]`
- **Depends on:** `[U-AS-01]` `[unchanged]`
- **Inputs:** `ToolContext` per tool invocation. `CHANGE:` prose no longer describes `ToolContext` as an external type — it is now declared in this unit's Signatures block.
- **Signatures:** `CHANGE:` add the carrier declaration:
  ```
  record ToolContext {
    computer_use_bound          : bool
    code_execution_beta_invoked : bool
  }
  ```
  `enum ForcedTierCause`, `record ForcedTierResult`, `function forced_tier(ctx: ToolContext) -> Optional<ForcedTierResult>` — `[unchanged]`.
- **Acceptance criteria:** `CHANGE:` add AC7 — "`ToolContext` is declared in this unit as a `record` carrying exactly `computer_use_bound: bool` + `code_execution_beta_invoked: bool`; it is the carrier for `ToolContext` consumed downstream at U-AS-10." ACs 1–6 `[unchanged]`.
- **Tests:** `CHANGE:` add `test_tool_context_record_two_fields`. Others `[unchanged]`.
- **Rollback boundary:** `CHANGE:` add — "Revert also removes the `ToolContext` carrier; U-AS-10's `lookup_cell_with_forcing` loses its parameter type."

---

### U-AS-04 — Declare `MCPTransport` enum + import cross-cutting discriminator enums from `harness-core`

`[Declaration-site conversion — see §3. Landed unit; see §3 action item A-1.]`

- **Implements:** `CHANGE:` from `[C-AS-02 §2.3; C-AS-09 §9.1 (forward use); C-AS-12 §12.2 (forward use); C-AS-10 §10.1 (forward use)]` to **`[C-AS-10 §10.1]`** — U-AS-04 now covers only the `MCPTransport` transport-level set; `DeploymentSurface`/`PersonaTier` coverage moved to U-CORE-01.
- **Depends on:** `CHANGE:` from `(none)` to **`[U-CORE-01 (cross-axis: core)]`** — the import edge for `DeploymentSurface` + `PersonaTier`.
- **Inputs:** None (foundational) `[unchanged]`.
- **Signatures:** `CHANGE:` delete `enum DeploymentSurface { ... }` and `enum PersonaTier { ... }`. Add import line. Retain `MCPTransport`:
  ```
  import { DeploymentSurface, PersonaTier } from harness-core   // U-CORE-01 product

  enum MCPTransport {
    STDIO                      = "stdio",
    STREAMABLE_HTTP_L0_REFUSE  = "streamable_http_l0",
    STREAMABLE_HTTP_L1_PINNED  = "streamable_http_l1",
    STREAMABLE_HTTP_L2_SANDBOX = "streamable_http_l2",
    STREAMABLE_HTTP_L3_AUDIT   = "streamable_http_l3"
  }
  ```
- **Acceptance criteria:** `CHANGE:` ACs 1 + 2 (`DeploymentSurface`/`PersonaTier` cardinality + ordering) **deleted** — covered at U-CORE-01. Revised AC set:
  1. `MCPTransport` carries exactly five values matching C-AS-10 §10.1 transport-level labels byte-exact.
  2. Adding a value to `MCPTransport` requires Workflow §4.1.2 Class-2 ADR-D2 revision (cardinality bound: 5).
  3. `MCPTransport` identifier strings byte-exact spec-canonical.
  4. `DeploymentSurface` + `PersonaTier` are imported from `harness-core` (U-CORE-01); U-AS-04 does not redeclare them. A local redeclaration is a defect.
  5. Pure data type: no associated functions, no metadata tables.
- **Tests:** `CHANGE:` `test_deployment_surface_*` / `test_persona_tier_*` deleted (they live at U-CORE-01). Retain `test_mcp_transport_cardinality_five`, `test_enum_identifier_strings_byte_exact` (scoped to `MCPTransport`). Add `test_u_as_04_does_not_redeclare_core_enums`.
- **Rollback boundary:** `CHANGE:` Revert the `MCPTransport` declaration + the `harness-core` import. Downstream composition units lose `MCPTransport`; `DeploymentSurface`/`PersonaTier` remain available from `harness-core` (unaffected by an U-AS-04 revert).

---

### U-AS-06 — Implement `sandbox_tier_floor` lookup table  `[CONDITIONAL — see §9 spec gap]`

`[Pattern B carrier — ToolMetadata. Pattern A2 — signature gap is a SPEC under-specification; body is conditional on the §9 operator decision.]`

- **Implements:** `[C-AS-02 §2.3]` `[unchanged]` — *citation may bump to the revised C-AS-02 version if the operator routes the §9 gap to `spec-writer`.*
- **Depends on:** `[U-AS-01, U-AS-04, U-AS-05]` `[unchanged]`.
- **Signatures — Pattern B fix (decided, applies under both options):** add the `ToolMetadata` carrier:
  ```
  record ToolMetadata {
    is_deterministic_inhouse : bool
    forces_computer_use      : bool
    forces_code_execution    : bool
  }
  ```
  `enum SandboxTierFloorResult { RESOLVED(SandboxTier), REFUSE }`, `enum MCPTrustLevel { ... }` — `[unchanged]`.
- **Signatures — `sandbox_tier_floor` signature (CONDITIONAL on §9):**
  - **`[Option G-1 — spec adopts the 5-arg signature]`** (C-AS-02 §2.2/§2.3/§11.1 reconciled to thread `mcp_trust_level`): the plan signature is conformed to the revised spec — `sandbox_tier_floor(tool: ToolMetadata, deployment_surface, blast_radius_tier, mcp_transport: Optional<MCPTransport>, mcp_trust_level: Optional<MCPTrustLevel>) -> SandboxTierFloorResult`. The current plan signature is then correct as-written; only the "verbatim per §2.3" claim is re-grounded to the revised §2.3.
  - **`[Option G-2 — spec keeps the 4-arg call site; trust level travels inside a context object]`** (the §2.2 call site is canonical; §2.3's trust-dependent rows resolve via `mcp_transport` carrying trust as a richer type, or via `ToolMetadata`/a context object): the plan signature drops the standalone `mcp_trust_level` parameter and the §2.3 rows 4–6 resolve from whatever carrier the spec fix designates.
  - R3 does **not** pick. The conformed signature is owed to the §9 spec decision.
- **Acceptance criteria:** `CHANGE:` AC1 — drop "verbatim" until the §9 reconciliation; re-state as "Lookup implements the ten C-AS-02 §2.3 rows; the row-4–6 trust-level conditioning conforms to the §2.3 signature as reconciled per the §9 spec decision." Add AC: "`ToolMetadata` is declared in this unit carrying `is_deterministic_inhouse` / `forces_computer_use` / `forces_code_execution` — the §2.3 row discriminators." Other ACs `[unchanged]`.
- **Tests:** add `test_tool_metadata_record_three_fields`. The trust-level row tests stay but their argument shape is conditional on §9.
- **Status:** **Open — body conditional. Class 1 (halt) until §9 resolved.**

---

### U-AS-07 — Add `ToolContract.minimum_tier` field + declaration discipline + registration enforcement

`[Pattern B carrier — RawContractInput; carrier-ordering fix for SecretAllowlistEntry.]`

- **Implements:** `[C-AS-03 §3.1, §3.2, §3.3]` `[unchanged]`.
- **Depends on:** `[U-AS-01]` `[unchanged]`.
- **Signatures — Pattern B fixes (decided):**
  - Declare `record RawContractInput` — the pre-validation tool-contract serialization shape (un-validated counterpart of `ToolContract`; the §3 registration-input subject). Field set = the raw serialized form of the `ToolContract` fields prior to validation.
  - **Carrier-ordering fix for `SecretAllowlistEntry`:** U-AS-07 forward-declares the **interim element shape** of `required_secrets`. The `ToolContract.required_secrets : List<SecretAllowlistEntry>` field stays, and `SecretAllowlistEntry`'s 2-field shape `{ name: string; scope: SecretScope }` (spec §6.1) is **declared at U-AS-07** as the element type. U-AS-22 then *populates the access-control semantics* (the allowlist-intersection function) against the already-declared shape — U-AS-22 no longer *declares* the type, it *consumes* it. This removes the carrier-downstream-of-consumer defect with no graph cycle.
  ```
  record RawContractInput { ... raw serialized ToolContract fields, pre-validation ... }
  record SecretAllowlistEntry { name: string; scope: SecretScope }   // moved up from U-AS-22
  record ToolContract { name; description; input_schema: JSONSchema; output_schema: JSONSchema;
                        minimum_tier: SandboxTier; blast_radius_tier: BlastRadiusTier;
                        required_secrets: List<SecretAllowlistEntry> }
  ```
  > **Cross-unit note:** `SecretAllowlistEntry.scope : SecretScope` references the `SecretScope` type declared at U-AS-20. U-AS-07 `Depends on [U-AS-01]` only — and U-AS-20 also depends only on U-AS-01, with no edge between them. To keep `SecretScope` in-cone for U-AS-07, **either** (a) U-AS-07 gains a `Depends on: [U-AS-20]` edge — but U-AS-22 already depends on both, and U-AS-20 does not depend on U-AS-07, so no cycle — **or** (b) `SecretAllowlistEntry` stays declared at U-AS-22 and U-AS-07 declares only the *interim opaque shape* of `required_secrets` (a forward-declared element-type placeholder). **R3 recommends (a)** — add `Depends on: [U-AS-20]` to U-AS-07; it is acyclic (U-AS-20 → U-AS-01; U-AS-07 → U-AS-01, U-AS-20) and gives `SecretAllowlistEntry` a single clean carrier. Flagged **proposing** — see Q-R3-3 (§10).
- **Acceptance criteria:** `CHANGE:` add "`RawContractInput` is declared in this unit as the pre-validation registration-input record." Add "`SecretAllowlistEntry` is declared in this unit (carrier-ordering fix); U-AS-22 consumes it, does not re-declare it." Other ACs `[unchanged]`.
- **Tests:** add `test_raw_contract_input_declared`, `test_secret_allowlist_entry_declared_at_u_as_07`.
- **Status:** Pattern B fixes **decided**; the §10 Q-R3-3 graph-edge choice is **proposing**.

---

### U-AS-08 — Implement `sandbox_tier(tool, call_site_context)` composition function

`[Pattern A1 conformance — AssignedTierReason. Pattern B carriers — TaintState, MCPServer.]`

- **Implements:** `[C-AS-02 §2.1, §2.2, §2.5]` `[unchanged]`.
- **Depends on:** `[U-AS-01, U-AS-02, U-AS-04, U-AS-05, U-AS-06, U-AS-07]` `[unchanged]`.
- **Signatures — Pattern B fixes (decided):** declare the two carriers beside `CallSiteContext`:
  ```
  enum TaintState { ... }              // closed; the taint poles blast_radius_floor(taint_state) discriminates (spec §2.2 + §2 deferral clause)
  record MCPServer { ... }             // the MCP-server identity/trust shape (spec §10 MCP transport/trust surface)

  record CallSiteContext {
    taint_state         : TaintState           // now carrier-declared in-unit
    mcp_server          : Optional<MCPServer>   // now carrier-declared in-unit
    deployment_surface  : DeploymentSurface     // imported from harness-core (transitively via U-AS-04)
    blast_radius_tier   : BlastRadiusTier
    mcp_transport       : Optional<MCPTransport>
    mcp_trust_level     : Optional<MCPTrustLevel>
    persona_tier        : PersonaTier           // imported from harness-core
    computer_use_bound  : bool
    code_execution_beta_invoked : bool
  }
  ```
- **Signatures — Pattern A1 conformance (decided):** conform `AssignedTierReason` to the spec §15.2 7-value set verbatim:
  ```
  enum AssignedTierReason {
    CONTRACT_MINIMUM, BLAST_RADIUS_FLOOR, MCP_SERVER_TRUST_FLOOR,
    OPERATOR_POLICY_FLOOR, SANDBOX_TIER_FLOOR,
    PERSONA_TIER_FLOOR, SUB_AGENT_MONOTONIC_ASCENSION
  }
  ```
  `CHANGE:` `COMPUTER_USE_FORCING` and `CODE_EXECUTION_FORCING` are **removed** from `AssignedTierReason` — they are not §15.2 members. Forced-tier results are reported via U-AS-02's `ForcedTierCause` enum (already declared, `COMPUTER_USE_BOUND`/`CODE_EXECUTION_BETA`); the composition's `SandboxTierCompositionResult` carries the forced-tier cause from there. `enum SandboxTierCompositionResult`, `interface FloorInterfaces`, `function sandbox_tier(...)` — signatures `[unchanged]` except `FloorInterfaces` now references the in-unit `MCPServer` carrier.
- **Acceptance criteria:** `CHANGE:`
  - AC4 — re-state: "`AssignedTierReason` is the spec §15.2 audit-surface enum, exactly seven members `{contract_minimum, blast_radius_floor, mcp_server_trust_floor, operator_policy_floor, sandbox_tier_floor, persona_tier_floor, sub_agent_monotonic_ascension}` (SCREAMING_SNAKE rendering). It identifies the winning `max()` floor. Forced-tier outcomes are reported via the `ForcedTierCause` enum (U-AS-02), not via `AssignedTierReason`."
  - AC2 — re-state to route forced-tier through `ForcedTierResult`/`ForcedTierCause` (U-AS-02) rather than `AssignedTierReason` members.
  - Add: "`TaintState` and `MCPServer` are declared in this unit as the `CallSiteContext` field carriers."
  - ACs 1, 3, 5, 6, 7 `[unchanged]`.
- **Tests:** `CHANGE:` `test_sandbox_tier_composition_assigned_tier_reason_at_tie` re-grounded to the 7-member §15.2 set. Add `test_assigned_tier_reason_members_match_spec_15_2_verbatim`, `test_taint_state_declared`, `test_mcp_server_declared`.
- **Rollback boundary:** `CHANGE:` add — "Revert also removes the `TaintState` + `MCPServer` carriers; U-AS-14's `GateLevelFloorInterfaces` loses its `MCPServer` type."
- **Status:** Pattern A1 conformance + Pattern B carriers — **decided** (authority-chain-determinate).

> **Propagation (decided):** U-AS-16 acc #6 cites this unit's `AssignedTierReason` for `sandbox.policy.assigned_tier_reason`. The conformed 7-member set is what U-AS-16 references — U-AS-16 body unchanged (CONFORM, §0.4). U-AS-16's `test_sandbox_attribute_names_byte_exact_per_spec_15_2` tests the *attribute name*; an `assigned_tier_reason`-*value* test (`test_sandbox_policy_assigned_tier_reason_values_match_spec_15_2`) should be added at U-AS-16 to catch the enum-value layer the name-test misses — flagged as a minor U-AS-16 test addition (Q-R3-4, §10).

---

### U-AS-09 — Implement `sub_agent_sandbox_tier` monotonic-ascension function  `[CONDITIONAL — see §9 spec gap]`

`[Pattern A2 — folds into the U-AS-06 sandbox_tier_floor spec reconciliation.]`

- **Implements:** `[C-AS-11 §11.1, §11.2, §11.3, §11.4, §11.5]` `[unchanged]` — *citation may bump if §9 routes to `spec-writer`.*
- **Depends on:** `[U-AS-01, U-AS-04, U-AS-06]` `[unchanged]`.
- **Signatures — `sub_agent_sandbox_tier` (CONDITIONAL on §9):** the plan declares a 5-param signature `(parent_sandbox_tier, blast_radius, mcp_transport, mcp_trust_level, deployment_surface)`; spec §11.1 declares 4 `(parent_sandbox_tier, blast_radius, mcp_transport, deployment_surface)`. Spec §11.1's inner `sandbox_tier_floor(blast_radius, deployment_surface, mcp_transport)` is itself a **3-arg** form — a third distinct `sandbox_tier_floor` shape (see §9).
  - **`[Option G-1]`** — if the §9 reconciliation adopts a trust-level argument on `sandbox_tier_floor`, then `sub_agent_sandbox_tier` legitimately threads `mcp_trust_level` and the plan's 5-param form conforms to the revised §11.1.
  - **`[Option G-2]`** — if the §9 reconciliation keeps `sandbox_tier_floor` trust-level-free at the call site, `sub_agent_sandbox_tier` drops `mcp_trust_level` and conforms to the spec §11.1 4-param form as-written.
  - R3 does **not** pick.
- **Acceptance criteria:** `CHANGE:` AC4 — drop "verbatim" until §9; re-state "Composition is `max(parent_tier, sandbox_tier_floor(...))` per §11.1; the `sandbox_tier_floor` argument list conforms to the §11.1 signature as reconciled per the §9 spec decision." Other ACs `[unchanged]`.
- **Status:** **Open — body conditional. Class 1 (halt) until §9 resolved. The §9 `spec-writer` pass MUST reconcile §11.1 in the same pass as §2.2/§2.3 (three-way gap — see §9).**

---

### U-AS-10 — Declare 12-cell deployment-matrix + cell-selection lookup function

`[Pattern A3 conformance — provider-class vocabulary. Pattern B — ToolContext consumed via U-AS-02 carrier.]`

- **Implements:** `[C-AS-09 §9.1, §9.3, §9.5]` `[unchanged]`.
- **Depends on:** `[U-AS-01, U-AS-02, U-AS-04, U-AS-11]` `[unchanged]` — `ToolContext` resolves via the existing `[U-AS-02]` edge (U-AS-02 now declares the carrier, §5/§4).
- **Signatures:** `[unchanged]` — `lookup_cell_with_forcing(surface, blast_radius, ctx: ToolContext)` now has its `ToolContext` type in-cone via U-AS-02.
- **Acceptance criteria:** `CHANGE:` **AC2 re-stated against the actual `SandboxProviderClass` member set (spec §9.2 / U-AS-11):**
  - OLD (divergent): "...local-dev/self-hosted = LANGUAGE_LEVEL / **PROCESS_FS_OVERLAY** / CONTAINER / MICROVM_FIRECRACKER..."
  - NEW (conformed): "Per-cell `sandbox_tier` + `provider_class` match spec §9.1 row-by-row, naming `provider_class` values from the `SandboxProviderClass` enum (U-AS-11): `LANGUAGE_LEVEL`, `FILESYSTEM_OVERLAY_WORKTREE`, `PROCESS_ULIMIT_BUBBLEWRAP_SEATBELT`, `CONTAINER`, `MICROVM_FIRECRACKER`, `FULL_VM`. The non-existent `PROCESS_FS_OVERLAY` identifier is removed; the §9.1 cell content (tier + provider-class per `(DeploymentSurface, BlastRadiusTier)` cell) transcribes §9.1 using only these six carrier members."
  - Add AC: "`ToolContext` consumed by `lookup_cell_with_forcing` resolves to the U-AS-02 carrier (in-cone via the `[U-AS-02]` dependency)."
  - ACs 1, 3, 4, 5, 6 `[unchanged]`.
- **Tests:** `CHANGE:` the row-per-spec tests stay; any test asserting `PROCESS_FS_OVERLAY` is corrected to the actual member. Add `test_deployment_matrix_provider_classes_all_in_sandbox_provider_class_enum`.
- **Status:** Pattern A3 conformance — **decided**.

---

### U-AS-12 — Operator-policy override scope per persona-tier  `[CONDITIONAL — Reading A vs B]`

`[Pattern A1 — override_scope "any cell" vs spec §9.4 "non-compliance cells".]`

- **Implements:** `[C-AS-09 §9.4; C-AS-12 §12.2 reference]` `[unchanged]`.
- **Depends on:** `[U-AS-04]` `[unchanged]` — `PersonaTier` resolves via the `harness-core` import (transitively through U-AS-04 / U-CORE-01).
- **Signatures (CONDITIONAL):**
  - **`[Reading A — "non-compliance cells" = "any cell" for the solo persona; the verbatim claim is merely loose]`** — signature `[unchanged]`: `override_scope(persona_tier: PersonaTier, proposed_cell: (DeploymentSurface, BlastRadiusTier)) -> OverrideScopeResult`. Only AC2 text changes (below).
  - **`[Reading B — the plan over-permits; `override_scope` is under-typed]`** — `override_scope`'s declared inputs `(DeploymentSurface, BlastRadiusTier)` **cannot evaluate** whether a cell is a "compliance cell". The signature gains a compliance-status input: `override_scope(persona_tier: PersonaTier, proposed_cell: (DeploymentSurface, BlastRadiusTier), cell_compliance_status: CellComplianceStatus) -> OverrideScopeResult`, with `CellComplianceStatus` a new closed enum. Reading B requires a Phase-5 spec decision on what supplies `cell_compliance_status` — i.e. it co-routes with a small spec reconciliation.
  - R3 does **not** pick.
- **Acceptance criteria:** `CHANGE:` AC2:
  - **Reading A:** "...SOLO_DEVELOPER → PERMITTED_APPEND_ONLY at non-compliance cells. For the solo-developer persona every cell is treated as a non-compliance cell, so the scope is effectively total over `(DeploymentSurface, BlastRadiusTier)` — the §9.4 'non-compliance cells' qualifier and 'any cell' coincide for this persona. (The 'verbatim per §9.4' framing is dropped; §9.4 says 'non-compliance cells', and AC2 states the persona-specific equivalence explicitly.)"
  - **Reading B:** "...SOLO_DEVELOPER → PERMITTED_APPEND_ONLY only at cells where `cell_compliance_status = NON_COMPLIANCE` per §9.4; `override_scope` evaluates the compliance status via the new `cell_compliance_status` input."
- **Status:** **Open — body conditional on the Reading A/B operator decision. §2.7.6 Class 1/2 pending the read.**

---

### U-AS-14 — Implement 5-axis gate-level multiplicative tunable composition

`[Pattern B — MCPServer consumed in GateLevelFloorInterfaces; resolved via U-AS-08 carrier.]`

- **Implements:** `[C-AS-12 §12.1, §12.2 reference, §12.5]` `[unchanged]`.
- **Depends on:** `CHANGE:` from `[U-AS-01, U-AS-04, U-AS-05, U-AS-06]` to **`[U-AS-01, U-AS-04, U-AS-05, U-AS-06, U-AS-08]`** — add the `[U-AS-08]` edge so `MCPServer` (declared at U-AS-08, §5) is in-cone for `GateLevelFloorInterfaces.per_mcp_server_trust_floor : (Optional<MCPServer>) -> GateLevel`. Acyclic: U-AS-08 → {U-AS-01,02,04,05,06,07}; U-AS-14 → {…,U-AS-08}; no back-edge.
- **Signatures:** `[unchanged]` — `GateLevelFloorInterfaces` now has `MCPServer` in-cone. `GateLevel` 3-value enum transcribes §12.1 faithfully (Q1 clean-list — no change).
- **Acceptance criteria:** `CHANGE:` add "`MCPServer` consumed in `GateLevelFloorInterfaces` resolves to the U-AS-08 carrier (in-cone via the new `[U-AS-08]` dependency)." Others `[unchanged]`.
- **Status:** Pattern B dependency-graph completion — **decided**.

---

### U-AS-20 — Declare `fetch_secret` signature + `SecretRef` opaque type + tier-aware resolution table  `[CONDITIONAL — R1 vs R2]`

`[Pattern A2 — fetch_secret 3-param vs spec §5.1 2-param. Pattern B — SecretScope ellipsis-body.]`

- **Implements:** `[C-AS-05 §5.1, §5.2, §5.4]` `[unchanged]` — *citation bumps if §10 Q-R3-2 routes to a Phase-5 spec revision.*
- **Depends on:** `[U-AS-01]` `[unchanged]`.
- **Signatures — Pattern B fix (decided):** replace the `SecretScope` ellipsis body with an explicit field set. Spec §5.4 sanctions deferring *serialization*, not the *field set*:
  ```
  record SecretScope { ... explicit field set per the §5.1 `scope` parameter semantics ... }
  // serialization format remains deferred per §5.4; the FIELD SET is no longer { ... }
  ```
- **Signatures — `fetch_secret` (CONDITIONAL on §10 Q-R3-2):**
  - **`[Option R1 — spec adopts the 3-param form]`**: C-AS-05 §5.1 + the C-AS-05 contract title are revised (Phase-5 spec revision) to `fetch_secret(name, scope, tier) -> SecretRef`. The plan's current 3-param signature then conforms to the revised spec.
  - **`[Option R2 — plan reverts to the 2-param spec form]`**: `fetch_secret(name: string, scope: SecretScope) -> SecretRef` per spec §5.1 as-written; the `tier` the resolution table needs is threaded via a context object or read from the resolved `SandboxTier` at the call site (per U-AS-08), not as a `fetch_secret` parameter.
  - R3 does **not** pick.
- **Acceptance criteria:** `CHANGE:` AC1 — remove the internally-contradictory "`fetch_secret(name, scope)` matches §5.1 verbatim while declaring `(name, scope, tier)`". Re-state per the chosen option: R1 — "signature `(name, scope, tier)` conforms to the revised C-AS-05 §5.1"; R2 — "signature `(name, scope)` conforms to spec §5.1; `tier` is supplied by call-site context, not a parameter." Add "`SecretScope` is declared with an explicit field set (serialization deferred per §5.4)." ACs 2–7 `[unchanged]`.
- **Tests:** `CHANGE:` `test_fetch_secret_signature_matches_spec` re-grounded to the chosen option. Add `test_secret_scope_field_set_explicit_not_ellipsis`.
- **Status:** **Open — `fetch_secret` body conditional on Q-R3-2; the `SecretScope` field-set fix is decided. §2.7.6 Class 1 (halt) pending the direction.**

---

### U-AS-28 — Declare eleven-primitive enumeration + per-primitive × workload-class adoption-depth matrix

`[Pattern A3 conformance — "kebab-case verbatim" claim. Pattern B carrier — AnchorCitation.]`

- **Implements:** `[C-AS-13 §13.1, §13.2]` `[unchanged]`.
- **Depends on:** `[U-AS-04, U-IS-01 (cross-axis: IS), U-IS-02 (cross-axis: IS)]` `[unchanged]` — see §7.3 on the IS edge re-cite.
- **Signatures — Pattern B fix (decided):** declare the `AnchorCitation` carrier:
  ```
  record AnchorCitation {
    source_identifier : string
    confidence_tag    : ConfidenceTag       // [HIGH] / [MODERATE] / [SPECULATIVE]
  }
  const ANTHROPIC_PRIMITIVE_ANCHORS: Map<AnthropicPrimitive, AnchorCitation>
  ```
  `enum AnthropicPrimitive` (11 members), `enum WorkloadClass`, `enum AdoptionDepth`, `record AdoptionDepthBinding` — `[unchanged]`.
  > **`WorkloadClass` note:** U-AS-28 declares a local `enum WorkloadClass`. This is the same spec concept as the `harness-core` `WorkloadClass` (U-CP-00). The carrier map flags `WorkloadClass` as a `harness-core` resident; U-AS-30 already takes a `[U-CP-00]` edge (R1 §3.2). **R3 recommends U-AS-28 also consume `WorkloadClass` from `harness-core` (U-CP-00) rather than re-declare it** — the multi-declaration defect the carrier map targets. Flagged Q-R3-5 (§10), *proposing*. If the operator confirms, delete the local `enum WorkloadClass` from U-AS-28 and add a `[U-CP-00]` edge; U-AS-29/U-AS-30 (which consume `WorkloadClass`) inherit it.
- **Acceptance criteria:** `CHANGE:` **AC1 conformed (Pattern A3):**
  - OLD (divergent): "`AnthropicPrimitive` declares exactly 11 values per §13.1 verbatim **kebab-case**."
  - NEW (conformed): "`AnthropicPrimitive` declares exactly 11 members, one per the §13.1 prose name-table entry (`Skills system`, `MCP-as-code`, `Managed Agents`, `Per-role model binding`, …), mapped concept-name → SCREAMING_SNAKE member. §13.1 is a prose name table with no machine-identifier column; the member identifiers are a Python-stack naming-convention rendering (FM-D), not a byte-exact transcription of a spec string set. Closed enumeration; adding a 12th requires Class-2 ADR-D3 revision."
  - Add: "`AnchorCitation` is declared in this unit as the `ANTHROPIC_PRIMITIVE_ANCHORS` map value type."
  - ACs 2–8 `[unchanged]`.
- **Tests:** `CHANGE:` **delete `test_anthropic_primitive_identifier_strings_byte_exact_per_spec_13_1`** (no spec-side string set to compare to). Replace with `test_anthropic_primitive_cardinality_eleven_one_per_spec_13_1_concept` (cardinality + one-member-per-§13.1-concept). Add `test_anchor_citation_declared`. Other tests `[unchanged]`.
- **Status:** Pattern A3 conformance + Pattern B carrier — **decided**. The Q-R3-5 `WorkloadClass` re-home is **proposing**.

---

### U-AS-30 — Anthropic-API graceful-degradation per primitive + workload-binding-time selection contract

`[Pattern B carriers — ExtendedThinkingEffort, BatchApiCell, WorkloadManifestOverrides, Provider, ModelClass. Plus the WorkloadClass [U-CP-00] edge per R1 §3.2.]`

- **Implements:** `[C-AS-13 §13.5, §13.6]` `[unchanged]`.
- **Depends on:** `CHANGE:` from `[U-AS-04, U-AS-28, U-AS-29, U-IS-01 (cross-axis: IS), U-IS-02 (cross-axis: IS)]` to **`[U-AS-04, U-AS-28, U-AS-29, U-CP-00 (cross-axis: core), U-IS-01 (cross-axis: IS), U-IS-02 (cross-axis: IS)]`** — add the `[U-CP-00]` edge for `WorkloadClass` per `revision_R1_harness_core.md` §3.2 ("U-AS-30 — `WorkloadClass`* → `[U-CP-00]`").
- **Signatures — Pattern B fixes (decided), all declared in-unit:**
  ```
  enum ExtendedThinkingEffort { ... }        // §13.6 step 6 effort levels
  record BatchApiCell { ... }                // §13.6 step 7 batch-cell binding shape
  record WorkloadManifestOverrides { ... }   // §13.6 workload-manifest operator-override shape
  enum Provider { ANTHROPIC, BEDROCK, VERTEX, OPENAI, OLLAMA }   // §13.5 row-4 fallback families
  enum ModelClass { ... }                    // §13.5 row-4 fallback-pair model-class identifier
  ```
  `WorkloadBindingDecision`, `compose_workload_binding_decision`, `GRACEFUL_DEGRADATION_POLICY`, `MemoryToolStorageBackend` — signatures `[unchanged]`; their `WorkloadClass` field now resolves to the `harness-core` (U-CP-00) type, not a local declaration.
- **Acceptance criteria:** `CHANGE:` add "`ExtendedThinkingEffort`, `BatchApiCell`, `WorkloadManifestOverrides`, `Provider`, `ModelClass` are each declared in this unit (Pattern B carriers — faithful factor-outs of §13.5/§13.6 per T2)." Add "`WorkloadClass` is consumed from `harness-core` (U-CP-00); U-AS-30 does not declare it." AC2 (`C6_CROSS_FAMILY_FALLBACK_CHAIN` 5-step `anthropic→bedrock→vertex→openai→ollama`) re-grounded to the in-unit `Provider` enum. ACs 1, 3–9 `[unchanged]`.
- **Tests:** add `test_extended_thinking_effort_declared`, `test_batch_api_cell_declared`, `test_workload_manifest_overrides_declared`, `test_provider_enum_five_families`, `test_model_class_declared`, `test_workload_class_consumed_from_harness_core`.
- **Status:** Pattern B carriers + `[U-CP-00]` edge — **decided**.

---

### CONFORM units — bodies preserved verbatim

- **U-AS-16** — `[preserved verbatim]`. Propagation handled at §0.4 + the U-AS-08 propagation note above. Minor test addition Q-R3-4 (§10).
- **U-AS-22** — `[preserved verbatim]`. The carrier-ordering defect is fixed in U-AS-07's revised body (above); U-AS-22 now *consumes* `SecretAllowlistEntry` (declared at U-AS-07) rather than declaring it. The line "Populates the previously-empty-shape field on `ToolContract` at U-AS-07" stays accurate — U-AS-22 still populates the access-control semantics. **One micro-change** the operator should note: U-AS-22's Signatures block currently shows `record SecretAllowlistEntry { name; scope }` — under the §1.1 carrier-ordering fix this declaration **moves to U-AS-07**; U-AS-22's block changes to a consumption reference. This is the single exception to "preserved verbatim" for U-AS-22 and is recorded as Q-R3-3-dependent (§10): if the operator picks option (b) of §5/U-AS-07's cross-unit note instead, `SecretAllowlistEntry` stays declared at U-AS-22 and U-AS-22 is fully verbatim-preserved.
- **U-AS-33** — `[preserved verbatim]`. Manifest carrier-unit citations (U-AS-08/09/10/28/30) are unit IDs; R3 changes member sets *inside* those units, not the IDs. The manifest stays valid. `carrier_units: List<UnitId>` — `UnitId` is a U-CORE-01 import (§1.3); U-AS-33 gains a `[U-CORE-01 (cross-axis: core)]` edge for it — see §7.2.

## §6 Permanent auxiliary-type-audit section (structural fix — new plan §5.4.2)

The AS plan v1's own §5.4.1 auxiliary-type audit claimed "47 auxiliary typed entities … each verified as faithful factor-out" and §5.5 reported "Missing dependencies ✅ NOT PRESENT" — yet **11 distinct types** consumed at signature positions had no carrier. The self-audit had a blind spot exactly where the systemic defect lived. The Pattern B disease will recur unless the audit is made *exhaustive and mechanical*.

R3 adds a **new permanent plan section §5.4.2 — Exhaustive auxiliary-type audit** to `Implementation_Plan_Action_Surface_v1.1.md`. It is the structural fix: it enumerates **every** type appearing at a typed signature position across all 33 units, with its declaring carrier and a declaring-vs-consuming position record. A type with no carrier row is a defect, surfaced by the audit, not discovered later by adversarial review.

### §6.1 Audit method (mandatory, mechanical)

1. **Enumerate.** For every unit, list every identifier at a typed signature position — record/enum field types, function parameter types, function return types, `const` value types, map key/value types.
2. **Classify each** into exactly one of four classes:
   - **(C) Carrier-declared** — declared by a `record`/`enum`/`opaque type`/`newtype` in some unit's Signatures block.
   - **(X) Cross-axis import** — arrives via a declared `(cross-axis: IS)` or `(cross-axis: core)` edge.
   - **(S) Stack/SDK primitive** — `Target_Stack_Commitment` adoption (`JSONSchema`, OTel-SDK span/attribute primitives, `str`/`int`/`bool`).
   - **(U) Undeclared** — none of the above. **Every (U) is a defect.** The audit must return zero (U) rows.
3. **In-cone check.** For every (C) row, verify the declaring carrier is inside the consuming unit's `Depends on` transitive cone. A carrier out-of-cone is a defect.
4. **Carrier-ordering check.** For every (C) row, verify the carrier unit is not topologically *downstream* of a consumer. A downstream carrier is a defect (the U-AS-07/U-AS-22 `SecretAllowlistEntry` shape).

### §6.2 The §5.4.2 audit table (post-R3 — illustrative rows; the plan section enumerates all)

| Type | Class | Carrier unit | Consuming units | In-cone? | Note |
|---|---|---|---|---|---|
| `SandboxTier` | C | U-AS-01 | most AS units | ✓ | foundational L0 |
| `BlastRadiusTier`, `MechanismClass`, `SandboxTierMetadata` | C | U-AS-01 | — | ✓ | |
| `ToolContext` | C | **U-AS-02** | U-AS-02, U-AS-10 | ✓ | R3 Pattern B fix |
| `ForcedTierCause`, `ForcedTierResult` | C | U-AS-02 | U-AS-08 | ✓ | |
| `SandboxFailClass` + metadata enums | C | U-AS-03 | U-AS-16, U-AS-17 | ✓ | |
| `MCPTransport` | C | U-AS-04 | composition units | ✓ | stays AS-owned |
| `DeploymentSurface`, `PersonaTier` | X (core) | U-CORE-01 | U-AS-04/08/10/12/30/… | ✓ | R3 — imported from `harness-core` |
| `ToolMetadata` | C | **U-AS-06** | U-AS-06 | ✓ | R3 Pattern B fix |
| `SandboxTierFloorResult`, `MCPTrustLevel` | C | U-AS-06 | U-AS-08, U-AS-09, U-AS-13 | ✓ | |
| `RawContractInput` | C | **U-AS-07** | U-AS-07 | ✓ | R3 Pattern B fix |
| `ToolContract`, `ContractValidationResult` | C | U-AS-07 | U-AS-08, U-AS-14, U-AS-22 | ✓ | |
| `SecretAllowlistEntry` | C | **U-AS-07** (moved from U-AS-22) | U-AS-07, U-AS-22 | ✓ | R3 carrier-ordering fix (Q-R3-3) |
| `TaintState`, `MCPServer` | C | **U-AS-08** | U-AS-08, U-AS-14 | ✓ | R3 Pattern B fix; U-AS-14 gains `[U-AS-08]` edge |
| `CallSiteContext`, `FloorInterfaces`, `SandboxTierCompositionResult`, `AssignedTierReason` | C | U-AS-08 | U-AS-16 | ✓ | `AssignedTierReason` conformed to §15.2 |
| `SandboxProviderClass` | C | U-AS-11 | U-AS-10, U-AS-16 | ✓ | U-AS-10 AC2 conformed to these members |
| `SecretRef`, `SecretScope` | C | U-AS-20 | U-AS-07/22/24/26/27/30 | ✓ | `SecretScope` field set now explicit |
| `AnchorCitation` | C | **U-AS-28** | U-AS-28 | ✓ | R3 Pattern B fix |
| `WorkloadClass` | X (core) | U-CP-00 | U-AS-28/29/30 | ✓ | R3 — `[U-CP-00]` edge (Q-R3-5 confirms re-home) |
| `ExtendedThinkingEffort`, `BatchApiCell`, `WorkloadManifestOverrides`, `Provider`, `ModelClass` | C | **U-AS-30** | U-AS-30 | ✓ | R3 Pattern B fix |
| `UnitId` | X (core) | U-CORE-01 | U-AS-33 | ✓ | R3 — `[U-CORE-01]` edge |
| `StateLedgerEntry`, `IdempotencyKey`, `Actor`, `FilesystemPathContract`, … | X (IS) | IS plan U-IS-01/02/07/08/09/10/11/12 | U-AS-19/25/26/27/28/29/30 | ✓ | cross-axis IS edges; §7.3 re-cite check |
| `JSONSchema`, `SpanId`, `MonotonicTimestamp`, `AttributeValue`, `AttributeValueType`, `Cardinality` | S | — | various | n/a | stack/OTel-SDK primitives — no carrier needed |
| **(U) rows** | — | — | — | — | **ZERO — the audit must return no (U) row. R3 declares a carrier for all 11 former (U) types.** |

### §6.3 Standing discipline clause (added to the plan)

The §5.4.2 audit is **re-run at every AS-plan revision pass**. Any new unit or any new typed signature position must appear in the table with a (C)/(X)/(S) class — never (U). A revision pass that adds a type without a carrier row fails its own coherence pass. This converts the Pattern B defect from "found by adversarial review after the fact" to "blocked at authoring".

## §7 Dependency-graph delta

The AS plan §3 dependency graph takes the following deltas. The acyclic invariant is re-verified at §7.4.

### §7.1 New / changed edges

| Unit | Edge change | Reason |
|---|---|---|
| U-AS-04 | `Depends on` `(none)` → `[U-CORE-01 (cross-axis: core)]` | `harness-core` import of `DeploymentSurface`/`PersonaTier` (§3) |
| U-AS-14 | `Depends on` add `[U-AS-08]` → `[U-AS-01, U-AS-04, U-AS-05, U-AS-06, U-AS-08]` | `MCPServer` carrier in-cone (declared at U-AS-08) for `GateLevelFloorInterfaces` |
| U-AS-07 | `Depends on` add `[U-AS-20]` → `[U-AS-01, U-AS-20]` | `SecretScope` in-cone for `SecretAllowlistEntry.scope` (carrier-ordering fix; **proposing — Q-R3-3**) |
| U-AS-30 | `Depends on` add `[U-CP-00 (cross-axis: core)]` | `WorkloadClass` carrier (R1 §3.2 hand-off) |
| U-AS-33 | `Depends on` add `[U-CORE-01 (cross-axis: core)]` | `UnitId` identity alias from `harness-core` (§1.3) |
| U-AS-28 | `Depends on` add `[U-CP-00 (cross-axis: core)]` | **proposing — Q-R3-5** — only if the operator confirms re-homing `WorkloadClass` |
| U-AS-29 | `Depends on` add `[U-CP-00 (cross-axis: core)]` | **proposing — Q-R3-5** — consequential to Q-R3-5 (U-AS-29 consumes `WorkloadClass`) |

Pattern A conformance (U-AS-08, U-AS-10, U-AS-12, U-AS-28) introduces **no** new edges — enum-member / signature / AC-text changes only. The `ToolContext` carrier at U-AS-02 needs no new edge (U-AS-10 already `Depends on [U-AS-02]`).

### §7.2 `harness-core` import edges (R1-pattern)

Per `revision_R1_harness_core.md` §3, a `harness-core` import is flagged `(cross-axis: core)` but is an *import* edge, not an outbound CXA edge — it does not affect the AS→IS edge count of 13 (CXA v2.1 §2.3.1). AS units taking a core edge under R3: U-AS-04 (`[U-CORE-01]`), U-AS-30 (`[U-CP-00]`), U-AS-33 (`[U-CORE-01]`), and conditionally U-AS-28/U-AS-29 (`[U-CP-00]`, Q-R3-5). `DeploymentSurface`/`PersonaTier`/`WorkloadClass` consumed by other AS units (U-AS-08/10/12/etc.) resolve **transitively** — U-AS-08 etc. depend on U-AS-04, which carries the `harness-core` import; no separate edge per consumer is required so long as the import re-exports through the AS package surface. *(Operator may prefer explicit per-unit core edges for reviewability — flagged Q-R3-6, §10.)*

### §7.3 Cross-axis AS→IS edge re-cite (R2 IS revision interaction)

The AS plan cites IS plan v1 units (U-IS-01/02/07/08/09/10/11/12) via `(cross-axis: IS)` edges. The R2 IS revision pass produced `Implementation_Plan_Information_Substrate_v2_3.md` (proposed status). Per `implementation-planner` SKILL.md §9 use-latest-version discipline, R3's AS→IS citations must point to the latest filed IS plan version. **R3 action:** the AS plan §3.4 cross-axis edge enumeration bumps its IS-plan citation version from v1 to v2.3, and each AS unit citing a U-IS-NN verifies the cited IS unit still exists and carries the same export seam in v2.3. The audit (Q1 Findings-rejected #3) confirms the 6 cross-axis IS types (`StateLedgerEntry`, `IdempotencyKey`, `Actor`, `Bytes32`, `ISO8601Timestamp`, `FilesystemPathContract`) resolve via these edges; R3 records the version bump as **R3-application action item A-3** (§10) — a mechanical re-cite, not a re-decomposition. If R2 renumbered or removed any cited U-IS-NN, that surfaces as a Class 1 fork at A-3 (not anticipated — the IS revision was a `harness-core`-import + verbatim pass, not a unit-inventory change).

### §7.4 Acyclic invariant re-verification

All new edges are either (a) inbound to a Level-0 source node (`[U-CORE-01]`, `[U-CP-00]` — both pure source nodes, no outbound deps; inbound-only edges to a source cannot create a cycle), or (b) `[U-AS-08]`→added-to-U-AS-14 and `[U-AS-20]`→added-to-U-AS-07 — both forward edges in the existing topological order (U-AS-08 at L≈3 < U-AS-14 at L≈3; U-AS-20 at L1 < U-AS-07 at L1, and U-AS-07 does not transitively reach U-AS-20 — U-AS-20 `Depends on [U-AS-01]` only). **No cycle introduced. The graph remains a DAG; the 9-level topological structure (L0–L8) is preserved** — U-AS-04 moves from a pure L0 source to an L0 node with one inbound-from-core import (still L0 within the AS axis, since `harness-core` is upstream substrate). Kahn verification still consumes all 33 AS units.

## §8 Coverage-matrix delta

The AS plan §4.1 contract-section → unit coverage matrix takes these deltas. **No contract loses coverage; no coverage gap is introduced.**

| Contract section | v1 coverage | v1.1 coverage | Delta reason |
|---|---|---|---|
| C-AS-09 §9.1 (deployment-surface enum axis) | U-AS-04 (declares `DeploymentSurface`) + U-AS-10 (12-cell matrix) | **U-CORE-01** (enum axis) + U-AS-10 (12-cell matrix) | U-AS-04 no longer declares the enum; U-CORE-01 covers the deployment-surface enum axis (multi-unit coverage — U-AS-10 still covers the matrix proper). U-AS-04's §9.1 mark moves to U-CORE-01. |
| C-AS-09 §9.4 (persona-tier ladder / override scope) | U-AS-04 (declares `PersonaTier`) + U-AS-12 (override scope) | **U-CORE-01** (persona-tier enum) + U-AS-12 (override scope) | U-AS-04's `PersonaTier` declaration moves to U-CORE-01; U-AS-12 still covers §9.4 override-scope. |
| C-AS-12 §12.2 (override-scope reference) | U-AS-04 (forward use) + U-AS-12 + U-AS-14 | U-AS-12 + U-AS-14 | U-AS-04's forward-use citation is dropped (it no longer declares the discriminator enums). §12.2 stays covered by U-AS-12 + U-AS-14 — no gap. |
| C-AS-10 §10.1 (MCP transport-level set) | U-AS-04 (forward use) + U-AS-13 | **U-AS-04** (declares `MCPTransport`) + U-AS-13 | U-AS-04's §10.1 citation strengthens from "forward use" to a declaring citation — `MCPTransport` is the §10.1 transport-level set, stays AS-owned at U-AS-04. |
| C-AS-02 §2.3 | U-AS-04 (forward use) + U-AS-06 | U-AS-06 (+ conditional on §9) | U-AS-04's §2.3 forward-use citation dropped. U-AS-06 covers §2.3; the §9 spec gap may bump the cited C-AS-02 version. |
| C-AS-13 §13.1 | U-AS-28 | U-AS-28 | No coverage change — only AC text + the `AnthropicPrimitive` claim re-grounded. |
| C-AS-15 §15.2 | U-AS-08 (`AssignedTierReason`) + U-AS-16 (attribute names) | U-AS-08 (conformed enum) + U-AS-16 | No coverage change — U-AS-08's `AssignedTierReason` now transcribes §15.2 verbatim. |

> **Coverage-matrix cross-plan note:** the C-AS-09 §9.1 / §9.4 marks moving to U-CORE-01 means the `harness-core` plan's coverage matrix (`Implementation_Plan_Harness_Core_v1_0.md` §4) *adds* a mark for those contract rows. R1 already filed this (the U-CORE-01 coverage matrix lists C-AS-09 §9.1 + §9.4). R3 confirms the AS plan v1.1 and the `harness-core` plan v1.0 coverage matrices are consistent: a contract covered by multiple units across plans is permitted (`implementation-planner` SKILL.md §4.2); the AS plan v1.1 must **not silently drop** the contract row — it retains the row, attributing the enum-axis coverage to U-CORE-01 with an in-plan cross-reference note.

## §8 Coverage-matrix delta

## §9 The C-AS-02 spec under-specification — OPEN operator question (special item)

This is the task's special item. R3 **cannot** conform U-AS-06 / U-AS-09 to a spec section that is itself incomplete. R3 surfaces the gap, describes its shape, recommends whether a `spec-writer` pass must run first — and does **not** author the spec fix or guess the signature.

### §9.1 The gap is three-way, not two-way

The Q1 audit named this a "§2.2/§2.3" gap. Reading the spec directly, the `sandbox_tier_floor` signature appears **three times in the AS spec with three different shapes**:

| Spec site | `sandbox_tier_floor` signature as written | Args |
|---|---|---|
| **C-AS-02 §2.2** composition formula (line 197–202) | `sandbox_tier_floor(tool, call_site_context.deployment_surface, call_site_context.blast_radius_tier, call_site_context.mcp_transport)` | **4** — includes `tool`, **no `mcp_trust_level`** |
| **C-AS-02 §2.3** lookup table (lines 213–224) | rows 4–6 ("Remote MCP, trust level 0 / 1 / 2 / 3") are **keyed on MCP trust level** — the table *requires* a trust-level input to select a row | implies a **trust-level argument** the §2.2 call site does not thread |
| **C-AS-11 §11.1** sub-agent inner call (line 701) | `sandbox_tier_floor(blast_radius, deployment_surface, mcp_transport)` | **3** — **no `tool`**, no trust level |

The §2.2 4-arg signature **cannot evaluate** the §2.3 rows 4–6 (it carries no trust level). The §11.1 3-arg signature is a *third* distinct shape — it drops `tool` as well. The three call sites of one named function disagree on its arity. **This is a genuine SPEC under-specification (a self-contradiction inside C-AS-02 + C-AS-11), not a plan defect.** The plan's U-AS-06 5-arg signature `(tool, deployment_surface, blast_radius_tier, mcp_transport, mcp_trust_level)` is in fact the *only* signature that can express all of §2.3's rows — but it is not what any spec call site declares, so the plan "diverges" from a spec that is itself incoherent.

### §9.2 Why R3 cannot resolve it

`CLAUDE.md` §1.3 authority chain: the spec is canonical for the plan. R3 (`implementation-planner`, revision-pass) conforms the plan to the spec. When the *spec* is the artifact in error, conforming the plan to the spec-as-written is impossible — there is no single coherent spec signature to conform to. Per `implementation-planner` SKILL.md §2 (Consequence 1): "the implementation planner never extends a specification commitment … the gap is itself the finding." R3 surfaces the gap; it does not invent the missing commitment.

### §9.3 R3 recommendation: a `spec-writer` pass MUST run first

**R3 recommends the operator route this to a `spec-writer` C-AS-02 reconciliation pass BEFORE the U-AS-06 / U-AS-09 unit bodies are finalized.** The U-AS-06 and U-AS-09 bodies in §5 are explicitly conditional (`[Option G-1 | Option G-2]`) on that spec decision. The reconciliation pass must:

1. **Touch all three sites in one pass** — C-AS-02 **§2.2** (composition-formula call site), C-AS-02 **§2.3** (lookup table), and C-AS-11 **§11.1** (sub-agent inner call). The task framing named §2.2/§2.3/§11.1 — this matches; the §11.1 site is non-optional. A reconciliation that fixes §2.2/§2.3 but leaves §11.1 at 3 args re-creates the divergence for U-AS-09.
2. **Decide the canonical `sandbox_tier_floor` signature.** Two shapes are coherent:
   - **G-1 — trust level is an explicit argument.** `sandbox_tier_floor` gains a `mcp_trust_level` parameter; all three call sites thread it; §2.3 rows 4–6 become expressible. The plan's current 5-arg U-AS-06 signature then conforms to the revised §2.2/§2.3 and U-AS-09's 5-arg signature conforms to the revised §11.1. (Also: §11.1's missing `tool` argument must be reconciled — either §11.1 threads `tool` or §2.2 drops it; the spec must pick one.)
   - **G-2 — trust level travels inside a carrier.** `sandbox_tier_floor` keeps a smaller argument list; `mcp_transport` is enriched to a type that carries trust level, or trust is read from `ToolMetadata`/a context object. §2.3 rows 4–6 then resolve from that carrier.
   R3 does **not** pick between G-1 and G-2 — that is a spec decision, owed to `spec-writer` + the operator.
3. **Reconcile the `tool` argument disagreement** — §2.2 includes `tool`, §11.1 omits it. The reconciliation must make all three call sites agree on whether `tool`/`ToolMetadata` is an argument.
4. **C-AS-02 §11.1 and the C-AS-05 §11.1 cross-reference** — §11.1 is the C-AS-11 sub-agent contract; verify the reconciliation does not break C-AS-11 §11.2–§11.5 (the ascension rule, the D4 non-extension clause) which compose against the §11.1 signature.

### §9.4 Shape of the spec gap (for the `spec-writer` brief)

The `spec-writer` pass receives this as its scope statement:

> **C-AS-02 §2.2/§2.3 + C-AS-11 §11.1 — `sandbox_tier_floor` signature reconciliation.** The `sandbox_tier_floor` function is declared with three inconsistent signatures across §2.2 (4-arg, includes `tool`, no trust level), §2.3 (lookup table requires a trust-level key the §2.2 signature lacks), and §11.1 (3-arg, no `tool`, no trust level). The §2.3 lookup table is **inexpressible** from the §2.2 call-site signature. Reconcile all three sites to one canonical signature; decide whether `mcp_trust_level` is an explicit argument (G-1) or carrier-borne (G-2); decide whether `tool`/`ToolMetadata` is an argument; bump C-AS-02 + C-AS-11 spec versions; record the change in a `Phase_7_Class_N_Tension` record per `CLAUDE.md` §4.3 + the `spec-tension-record-pattern`.

### §9.5 Disposition

- **Class 1 (halt-execution)** for U-AS-06 and U-AS-09 — a Phase-5 spec artifact requires revision before the affected units land.
- **Sequencing:** the `spec-writer` C-AS-02/§11.1 reconciliation runs **before** the R3 AS plan v1.1 is finalized for U-AS-06/U-AS-09 — OR the AS plan v1.1 ships with U-AS-06/U-AS-09 carrying the `[Option G-1 | Option G-2]` conditional bodies and a `Status: blocked-on-C-AS-02-reconciliation` flag, finalized at a follow-on R3.1 micro-pass once the spec decision lands. R3 recommends the latter (do not block the other 10 FORK units' conformance on the spec gap) — the 10 plan-determinate / operator-decision-non-spec FORK units can land at v1.1; U-AS-06/09 finalize at R3.1.
- R3 **does not author the spec fix and does not guess the signature.** §9 is the finding; the operator decides.

## §10 Open questions + R3-application action items for the operator

### §10.1 Open questions (operator decides — R3 wrote conditional bodies, did not pick)

| ID | Question | R3 default / recommendation |
|---|---|---|
| **Q-R3-1** | **The C-AS-02 §2.2/§2.3/§11.1 `sandbox_tier_floor` spec gap (§9).** Route to a `spec-writer` reconciliation? Decide G-1 (trust level explicit arg) vs G-2 (trust level carrier-borne)? Decide the `tool`-argument disagreement? | **Route to `spec-writer`** — the gap is a genuine spec self-contradiction; R3 cannot resolve it. R3 does not pick G-1/G-2. U-AS-06/U-AS-09 carry conditional bodies until this lands. |
| **Q-R3-2** | **U-AS-20 `fetch_secret` conformance direction.** R1 (spec adopts 3-param `(name, scope, tier)`) vs R2 (plan reverts to 2-param `(name, scope)` + context object). | R3 does not pick (audit §4A.4 item 2 — "the reviewer does not pick"). Conditional body in §5. |
| **Q-R3-3** | **U-AS-07 / U-AS-22 `SecretAllowlistEntry` carrier-ordering.** Option (a) — declare `SecretAllowlistEntry` at U-AS-07, add `U-AS-07 Depends on [U-AS-20]`; U-AS-22 consumes. Option (b) — keep it at U-AS-22, U-AS-07 declares only an interim opaque element-type placeholder. | **Recommend (a)** — single clean carrier at U-AS-07, acyclic. Under (a), U-AS-22's Signatures block changes (the one micro-edit to an otherwise-verbatim CONFORM unit). Under (b), U-AS-22 is fully verbatim-preserved but U-AS-07 carries a placeholder. *Proposing.* |
| **Q-R3-4** | **U-AS-12 reading.** Reading A ("non-compliance cells" = "any cell" for solo persona — AC-text fix only) vs Reading B (`override_scope` under-typed, needs a `cell_compliance_status` input + a small spec decision). | R3 does not pick (audit §4A.4 item 3). Conditional body in §5. Reading B co-routes a minor spec reconciliation. |
| **Q-R3-5** | **U-AS-28 local `WorkloadClass` re-home.** U-AS-28 declares a local `enum WorkloadClass`; it is the same spec concept as the `harness-core` `WorkloadClass` (U-CP-00). Re-home to `harness-core` (delete local, add `[U-CP-00]` edges to U-AS-28/29) — consistent with the carrier-map multi-declaration-prevention finding and U-AS-30's existing `[U-CP-00]` edge? | **Recommend yes** — re-home; it is the exact defect the carrier map targets. *Proposing.* If declined, U-AS-28/29 keep the local enum and U-AS-30's `[U-CP-00]` edge is the lone core-`WorkloadClass` consumer (inconsistent but not incorrect). |
| **Q-R3-6** | **`harness-core` import edge granularity.** Per-unit explicit `(cross-axis: core)` edges for every `DeploymentSurface`/`PersonaTier`/`WorkloadClass` consumer, or transitive resolution through U-AS-04's import re-export (§7.2)? | **Recommend explicit per-unit core edges** for reviewability — matches R1's edge-form discipline. R3's §7 lists the minimum edge set; the operator may add per-consumer edges. *Proposing.* |
| **Q-R3-7** | **U-AS-06/U-AS-09 sequencing (§9.5).** Block AS plan v1.1 finalization on the Q-R3-1 spec pass, or ship v1.1 with U-AS-06/09 carrying conditional bodies + a `blocked-on-C-AS-02` flag and finalize at a follow-on R3.1 micro-pass? | **Recommend ship v1.1 + R3.1** — do not block the other 10 FORK units' conformance on the spec gap. |
| **Q-R3-8** | **T2 `proposing`-row faithfulness confirmation.** T2 classified the AS Pattern B types FACTOR-OUT, but 21 of 27 X-AL-3 rows are *proposing* — the operator should confirm each R3 in-place carrier's field set is a faithful operationalization of the cited spec prose, not a quiet over-reach. | The §5 carrier declarations name the spec section each field set traces to. Operator confirms per type at ratification; none requires a design-substrate revision (T2 verdict). |

### §10.2 R3-application action items (mechanical, executed when the operator applies the proposal)

| ID | Action | Locus |
|---|---|---|
| **A-1** | **U-AS-04 landed-source re-check.** U-AS-04 is landed; the declaration-site conversion (§3) requires verifying the landed source deletes the local `DeploymentSurface`/`PersonaTier` definitions and re-points to the `harness-core` import. Landed enum values matched U-CORE-01 byte-exact before deletion (confirmed identical). Source-vs-plan reconciliation; not a re-implementation. | landed `harness-as/` source |
| **A-2** | **U-AS-02 landed-source retrospective (§4).** Verify the landed `ToolContext` materialization is field-complete (`computer_use_bound` + `code_execution_beta_invoked`) and shape-consistent with the R3 §5 carrier. If not, U-AS-02 must be re-visited. §2.7.6 Class 3 informational. | landed `harness-as/` source |
| **A-3** | **AS→IS edge version re-cite (§7.3).** Bump the AS plan §3.4 cross-axis IS-plan citation from v1 to `Implementation_Plan_Information_Substrate_v2_3` (latest filed); verify each cited U-IS-NN still exists with the same export seam. Mechanical re-cite; a renumbered/removed U-IS-NN would surface as a Class 1 fork (not anticipated). | AS plan §3.4 |
| **A-4** | **§5.4.1 → §5.4.2 audit replacement.** The plan's defective §5.4.1 auxiliary-type audit is superseded by the new exhaustive §5.4.2 audit (§6). Apply the §5.4.2 table; run it to zero (U) rows. | AS plan §5.4 |

## §11 Filing footer

| Field | Value |
|---|---|
| Artifact | `.harness/revision_R3_as_plan.md` |
| Role | `implementation-planner`, revision-pass sub-mode (`implementation-planner` SKILL.md §8) |
| Authored | 2026-05-15, Phase 7 sub-phase 7b — revision pass R3 (third of R1–R5 carrier-map absorption sequence) |
| Inputs | `.harness/verbatim_audit_as_plan.md` (Q1 — canonical AS systemic-tension record); `.harness/shared_type_carrier_map.md` (T1); `.harness/xal3_resolution_recommendations.md` (T2); `.harness/revision_R1_harness_core.md` §3.2 + §4; `design-substrate/Implementation_Plan_Harness_Core_v1_0.md` (U-CORE-01); `design-substrate/Implementation_Plan_Action_Surface_v1.md`; `design-substrate/Spec_Action_Surface_v1.md` (§2.2/§2.3/§9.4/§11.1/§13.1/§15.2 read directly); `CLAUDE.md` + `harness-as/CLAUDE.md` |
| Scope | AS plan v1 → v1.1 — Pattern A verbatim conformance (7 units) + Pattern B carrier declaration (≥11 types) + U-AS-04 declaration-site conversion + U-AS-02 retrospective + CONFORM propagation + permanent §5.4.2 auxiliary-type audit |
| Status | `Proposed` — pending operator ratification of §10.1 open questions (Q-R3-1 through Q-R3-8) and authorization of §10.2 action items. U-AS-06/U-AS-09 bodies remain conditional on the Q-R3-1 `spec-writer` decision (§9). |
| Successor | On ratification: `Implementation_Plan_Action_Surface_v1.1.md` carries the §5 revised bodies + §6–§8 deltas; U-AS-06/U-AS-09 finalize at a follow-on R3.1 micro-pass once the C-AS-02/§11.1 `spec-writer` reconciliation lands. R4 (CP) / R5 (OD) follow per the carrier-map ordering. |
| HARD WALL attested | This pass wrote only `.harness/revision_R3_as_plan.md`. No `design-substrate/` file, no `CLAUDE.md`, no plan/spec/audit/carrier-map, no source code edited. No git commit. |

*End of Revision R3 — Action Surface Plan Materializability + Verbatim Conformance. The operator ratifies. R3 is the third of the five carrier-map absorption passes; R4 (CP) and R5 (OD) follow.*
