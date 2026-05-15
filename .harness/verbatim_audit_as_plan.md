# Verbatim-Claim + Undeclared-Type Audit — Action Surface Implementation Plan (U-AS-01 – U-AS-33)

## Summary

- Mode: Phase-7 pre-implementation review (per `harness-adversarial-reviewer` SKILL.md §"Phase-7 pre-implementation review mode"), review-ahead pipeline pass Q1. Plan-wide systemic audit of the entire AS-axis plan — **two** systemic attacks: (1) the **"verbatim"-claim divergence** pattern (the Tension 002 / 004 / F3-01 shape) and (2) the **undeclared-type / no-carrier** pattern (the F3-03 / U-AS-07 shape).
- Corpus reviewed:
  - `design-substrate/Implementation_Plan_Action_Surface_v1.md` — unit bodies U-AS-01 – U-AS-33; §3 dependency graph; §4 coverage matrix; §5.4.1 auxiliary-type audit
  - `design-substrate/Spec_Action_Surface_v1.md` v1.1 — contracts C-AS-01 through C-AS-16 (§1–§16)
  - `design-substrate/ADR-F4.md` / `ADR-F5.md` / `ADR-D2.md` / `ADR-D3.md` (anchoring ADRs; consulted where a plan unit cites an ADR directly)
  - `.harness/adversarial_review_as_buffer_1.md` — buffer-1 review (findings on U-AS-06 / 08 / 10 / 20 / 28 folded in by reference, not re-derived)
  - `.harness/verbatim_audit_cp_plan.md` + `.harness/verbatim_audit_od_plan.md` — calibration precedent + report-shape contract
  - `.harness/pipeline-fork-queue.md` items 9–15
- Date: 2026-05-15
- Finding count by §4.1 review-severity class: **Class 3: 11 · Class 2: 4 · Class 1: 2** (15 distinct units carry a blocking or operator-decision finding; 2 carry Class-1 drift only).
- Highest-severity finding: the two systemic patterns jointly (verbatim-divergence cluster + undeclared-type cluster) — see §4A.
- **Bottom-line:** of 33 AS units, **18 CLEARED** (no blocking divergence), **3 CONFORM** (authority-chain-determinate plan→spec fix), **12 FORK** (operator decision or back-flow needed). The AS plan carries the verbatim-divergence disease the §4A audit found in CP/OD, **plus** a second systemic disease (undeclared auxiliary types) the CP/OD plans did not exhibit.

### Class-taxonomy disambiguation (per SKILL.md title-section)

Per-unit severity below is the **§4.1 review-severity** scale (Class 1 minor / Class 2 moderate / Class 3 severe — phase re-opening). Each divergent unit's *disposition* is a **§2.7.6 Phase-7 execution fork**; the §2.7.6 fork class is stated explicitly per row. A §4.1 Class 3 review finding here ≠ a §2.7.6 Class 3 (informational) fork.

---

## Method

For every unit U-AS-01 – U-AS-33, two checks were applied:

1. **Verbatim-claim calibration.** Every acceptance criterion / signature note asserting "per §X verbatim", "matches §X verbatim", "exactly N per §X", or "byte-exact per §X" was cross-checked against the cited `Spec_Action_Surface_v1.md` section. A claim is a **DIVERGENCE** when the signature's value set / cardinality / vocabulary does not transcribe the cited section. The recurring sub-shape (also seen in OD) is **cardinality-matches / member-set-diverges**.

2. **Undeclared-type / carrier check.** Every type/enum/record at a typed signature position was checked for a declaring carrier (`record`/`enum`/`opaque type` declaration in some unit's Signatures block) AND for that carrier being inside the consuming unit's `Depends on` cone. Cross-axis types carried by the IS plan via declared `(cross-axis: IS)` dependency edges (`StateLedgerEntry`, `IdempotencyKey`, `Actor`, `Bytes32`, `ISO8601Timestamp`, `FilesystemPathContract`) are NOT undeclared — they resolve in-cone.

**Casing discipline (FM-D self-check).** SCREAMING_SNAKE_CASE renderings of spec lowercase-hyphen identifiers (`TIER_1_PROCESS`↔`tier-1-process`, `MICROVM_FIRECRACKER`↔`microvm-firecracker`, `AUTO`↔`auto`) are a Python-stack naming convention, not a divergence — token stems match 1:1. Divergences below are flagged because the *stems* diverge, not the casing.

---

## Fork inventory table — verbatim-divergence cluster (Pattern A)

| Unit | Claimed-verbatim surface | Divergence (plan says X / spec says Y) | §4.1 severity | §2.7.6 fork class |
|---|---|---|---|---|
| **U-AS-08** | acc #4 `AssignedTierReason` "identifies winning floor"; U-AS-16 acc #6 cites U-AS-08 `AssignedTierReason` as the carrier for `sandbox.policy.assigned_tier_reason` "per §15.2 verbatim" | Plan `AssignedTierReason` 7 values: `CONTRACT_MINIMUM, BLAST_RADIUS_FLOOR, MCP_SERVER_TRUST_FLOOR, OPERATOR_POLICY_FLOOR, SANDBOX_TIER_FLOOR, COMPUTER_USE_FORCING, CODE_EXECUTION_FORCING`. Spec §15.2 `sandbox.policy.assigned_tier_reason` enum (7 values): `contract_minimum, blast_radius_floor, mcp_server_trust_floor, operator_policy_floor, sandbox_tier_floor, persona_tier_floor, sub_agent_monotonic_ascension`. **Cardinality 7 in both; 5 of 7 stems overlap — plan substitutes `COMPUTER_USE_FORCING`/`CODE_EXECUTION_FORCING` for spec's `persona_tier_floor`/`sub_agent_monotonic_ascension`.** This is the OD-shape "cardinality-matches / member-set-diverges". Test `test_sandbox_attribute_names_byte_exact_per_spec_15_2` at U-AS-16 would not catch the enum-*value* divergence; a `assigned_tier_reason` value test would fail. | Class 3 | Class 1 (halt-execution) |
| **U-AS-12** | acc #2 `override_scope` "matches spec §9.4 verbatim", incl. `SOLO_DEVELOPER → PERMITTED_APPEND_ONLY at any cell` | **Already filed — fork-queue item 10.** Spec §9.4 + §12.2: solo-developer override permitted "at **non-compliance cells**". Plan acc #2 reads "at any cell". "compliance cell" is not a function of `(DeploymentSurface, BlastRadiusTier)` — `override_scope`'s declared inputs cannot evaluate it. Two readings (item 10): (A) "non-compliance cells" = "any cell" for the solo persona (claim merely loose) vs (B) plan over-permits and the function is under-typed. Both make the "verbatim" claim unsupportable. | Class 3 | Class 1 (halt-execution) |
| **U-AS-20** | acc #1 "`fetch_secret(name, scope)` signature matches §5.1 verbatim" while Signatures block declares `fetch_secret(name, scope, tier)` | **Already filed — buffer-1 F3-02, fork-queue item 14.** Spec §5.1 + C-AS-05 contract title (spec line 340) fix the signature at **2** parameters `(name, scope)`. Plan Signatures block declares **3** (`tier: SandboxTier` added). AC1 simultaneously claims "verbatim" and concedes "`tier` injected by U-AS-08" — internally contradictory verbatim claim. Tension-002 shape exactly. | Class 3 | Class 1 (halt-execution) |
| **U-AS-28** | acc #1 "`AnthropicPrimitive` declares exactly 11 values per §13.1 verbatim **kebab-case**"; test `test_anthropic_primitive_identifier_strings_byte_exact_per_spec_13_1` | **Already filed — buffer-1 F2-02, fork-queue item 15.** Spec §13.1 is a prose name table ("Skills system", "MCP-as-code", …) with **no machine-identifier column**. AC1 claims "kebab-case" but the unit's own Signatures block is SCREAMING_SNAKE (`SKILLS_SYSTEM`, `MCP_AS_CODE`); AC1 contradicts the unit's own signature. The `byte_exact_per_spec_13_1` test has no spec-side string set to compare to — not materializable as written. | Class 2 (per buffer-1) | Class 2 (operator-decision) |
| **U-AS-10** | acc #2 "Per-cell `sandbox_tier` + `provider_class` match spec §9.1 row-by-row …" naming `PROCESS_FS_OVERLAY` | **Already filed — buffer-1 F2-01, fork-queue item 13.** AC2 names provider-class `PROCESS_FS_OVERLAY`; the carrier enum `SandboxProviderClass` (U-AS-11, in-cone) has no such member — its members are `FILESYSTEM_OVERLAY_WORKTREE` / `PROCESS_ULIMIT_BUBBLEWRAP_SEATBELT`. AC2's identifier set disagrees with its carrier's declared member set. | Class 2 (per buffer-1) | Class 2 (operator-decision) |

**Note on the verbatim-divergence cluster scope.** Unlike CP (7 enum-rename divergences) and OD (9), the AS plan's verbatim defect is concentrated in **signature-shape** divergences (U-AS-20, U-AS-09 — see Pattern A2 below) and a small number of enum/value divergences (U-AS-08, U-AS-12). The AS plan's foundational enums (`SandboxTier`, `BlastRadiusTier`, `SandboxFailClass`, `SandboxProviderClass`, `MCPTransport`, `GateLevel`, `WorkloadClass`, `AdoptionDepth`, `D1EngineClass`, `SecretFailClass`, the six attribute namespaces) were each cross-checked against their cited spec section and **transcribe it faithfully** — see the clean-list. AS does **not** carry the CP/OD wholesale-enum-rename disease; the verbatim defect here is the signature-parameter and enum-member-substitution shape.

### Sub-pattern A2 — signature carries a parameter the cited spec contract does not contain

| Unit | Signature divergence | §4.1 / §2.7.6 |
|---|---|---|
| **U-AS-06** | `sandbox_tier_floor` declared with **5** params (adds `mcp_trust_level`); spec §2.2 call site + §2.3 table express a **4**-arg signature. Spec §2.3 lookup table *requires* trust level to evaluate rows 4–6, but the §2.2 call site does not thread it — the spec under-specifies its own contract. **Already filed — buffer-1 F3-01, fork-queue item 11.** | Class 3 / Class 1 (halt) |
| **U-AS-09** | `sub_agent_sandbox_tier` declared with **5** params (`parent_sandbox_tier, blast_radius, mcp_transport, mcp_trust_level, deployment_surface`); spec §11.1 signature has **4** (`parent_sandbox_tier, blast_radius, mcp_transport, deployment_surface`) — `mcp_trust_level` is plan-added. Same shape as F3-01: the spec §11.1 `sandbox_tier_floor(...)` call inside the §11.1 formula does not name a trust-level argument, and §11.1 is the cited contract. **Newly surfaced by this plan-wide pass.** | Class 3 / Class 1 (halt) |

U-AS-09's divergence is the **consumer-side propagation of the F3-01 spec under-specification** — the same `sandbox_tier_floor` signature gap surfaces a second time. It is folded into the F3-01 systemic-pattern scope: a single reconciliation of the C-AS-02 §2.2/§2.3 `sandbox_tier_floor` signature must conform the §11.1 sub-agent call site in the same pass.

---

## Fork inventory table — undeclared-type / no-carrier cluster (Pattern B)

The buffer-1 review surfaced this as the F3-03 / F2-04 systemic pattern across ≥4 units. The plan-wide sweep confirms it and **extends it to a sixth and seventh consuming surface** the buffer did not reach (U-AS-30, and the U-AS-07 element-type). Every type below is referenced at a typed signature position with **no `record`/`enum`/`opaque type` declaration anywhere in the plan** (verified by grep — each identifier appears only at consumption positions) and **no carrier in the consuming unit's `Depends on` cone**.

| Undeclared type | Consuming unit(s) | Position | §4.1 / §2.7.6 |
|---|---|---|---|
| **`ToolMetadata`** | U-AS-06 (Inputs + `sandbox_tier_floor` param) | `function sandbox_tier_floor(tool: ToolMetadata, ...)` | Class 3 / Class 1 (halt) — buffer-1 F3-03 |
| **`TaintState`** | U-AS-08 (`CallSiteContext` field) | `record CallSiteContext { taint_state: TaintState; ... }` | Class 3 / Class 1 (halt) — buffer-1 F3-03 |
| **`MCPServer`** | U-AS-08 (`CallSiteContext` field; `FloorInterfaces`); U-AS-14 (`GateLevelFloorInterfaces`) | `mcp_server: Optional<MCPServer>` | Class 3 / Class 1 (halt) — buffer-1 F3-03 |
| **`AnchorCitation`** | U-AS-28 (`ANTHROPIC_PRIMITIVE_ANCHORS` map value type) | `const ANTHROPIC_PRIMITIVE_ANCHORS: Map<AnthropicPrimitive, AnchorCitation>` | Class 3 / Class 1 (halt) — buffer-1 F3-03 |
| **`ToolContext`** | U-AS-02 (`forced_tier` param — **landed unit**); U-AS-10 (`lookup_cell_with_forcing` param) | `function forced_tier(ctx: ToolContext)` / `lookup_cell_with_forcing(..., ctx: ToolContext)` | Class 2 / Class 2 (operator-decision) for U-AS-10 — buffer-1 F2-04; U-AS-02 retrospective at §"U-AS-02 retrospective" |
| **`RawContractInput`** | U-AS-07 (`validate_tool_contract_at_registration` param) | `function validate_tool_contract_at_registration(raw_contract: RawContractInput)` | Class 2 / Class 2 — **newly surfaced** |
| **`SecretAllowlistEntry`** (forward-consumed before its carrier) | U-AS-07 (`ToolContract.required_secrets` field type) | `required_secrets: List<SecretAllowlistEntry>` — but `SecretAllowlistEntry` is declared by **U-AS-22**, which `Depends on` U-AS-07. The carrier is **downstream of the consumer**; U-AS-22 line 1125 says it "Populates the previously-empty-shape field on `ToolContract` at U-AS-07" — but U-AS-07 never specifies the interim shape. | — / Class 2 — **already filed, fork-queue item 9** |
| **`ExtendedThinkingEffort`, `BatchApiCell`, `WorkloadManifestOverrides`** | U-AS-30 (`WorkloadBindingDecision` fields; `compose_workload_binding_decision` param) | `extended_thinking_effort: Map<SubAgentRole, ExtendedThinkingEffort>`; `batch_api_cells: Set<BatchApiCell>`; `operator_overrides: WorkloadManifestOverrides` | Class 3 / Class 1 (halt) — **newly surfaced; extends the F3-03 pattern to a sixth unit** |
| **`Provider`, `ModelClass`** | U-AS-30 (`C6_CROSS_FAMILY_FALLBACK_CHAIN` element type) | `const C6_CROSS_FAMILY_FALLBACK_CHAIN: List<(Provider, ModelClass)>` | Class 3 / Class 1 (halt) — **newly surfaced** |
| **`SecretScope`** | U-AS-20 declares `record SecretScope { ... }` with an **ellipsis body** ("serialization deferred"); consumed as a typed field by U-AS-22, U-AS-24, U-AS-26, U-AS-27, U-AS-30 | The declaration exists but the **field set is `{ ... }`** — a downstream consumer reads it as "fields TBD by this unit". Spec §5.4 sanctions deferring *serialization*, not the field set. | Class 1 / Class 3 (informational) — buffer-1 F1-02 |

**The plan's own §5.4.1 auxiliary-type audit misses this cluster.** `Implementation_Plan_Action_Surface_v1.md` §5.4.1 claims "47 auxiliary typed entities … Each verified as faithful factor-out" and §5.5 anti-pattern audit reports "Missing dependencies ✅ NOT PRESENT" and "Spec extension ✅ NOT PRESENT". The §5.4.1 example enumeration does **not** list `ToolMetadata`, `TaintState`, `MCPServer`, `AnchorCitation`, `ToolContext`, `RawContractInput`, `ExtendedThinkingEffort`, `BatchApiCell`, `WorkloadManifestOverrides`, `Provider`, `ModelClass`. These types are neither declared by a carrier unit nor enumerated in the spec-extension audit — the plan's self-audit had a blind spot exactly where the systemic defect lives. This is itself evidence the pattern is structural, not a per-unit slip.

---

## Clean-list — "verbatim" / cardinality claims checked and confirmed to HOLD

The following units carry "verbatim" / "per §X" / "exactly N" claims that were cross-checked against the cited spec section and **do hold** (cardinality + value stems + cited section all match; SCREAMING_SNAKE casing is convention, not divergence):

- **U-AS-01** — `SandboxTier` 4 values (`tier-1-process`…`tier-4-full-vm`), `BlastRadiusTier` 4 values, `MechanismClass`, `SandboxTierMetadata`, `is_tier_at_or_above` monotonic ordering — all match spec §1.1/§1.2. Holds. *(`ToolContext` does not appear in U-AS-01.)*
- **U-AS-03** — `SandboxFailClass` 7 values byte-exact snake_case per §4.1 (`escape_attempt, egress_denied, timeout, oom, signal, exit_nonzero, policy_override`); per-row metadata (C5/C9/skips/sampled/tamper) transcribes the §4.1 table; `permanent_fail_skips_staircase` = {escape, egress, signal} per §4.2; always-sampled uniform per §4.3. Holds — a faithful transcription.
- **U-AS-04** — `DeploymentSurface` 3 / `PersonaTier` 3 / `MCPTransport` 5 values, all matching the §9.1 row-axis labels, Persona §3 ordering, and §10.1 transport-level labels. Holds.
- **U-AS-05** — `blast_radius_floor` 4-row mapping matches spec §2.4 table verbatim. Holds.
- **U-AS-11** — `SandboxProviderClass` 6 values per §9.2; per-class `tier_mapping` matches §9.2 column 4 row-by-row. Holds. *(The kebab-case names `filesystem-overlay-worktree` etc. are stem-faithful to spec §9.2's `filesystem-overlay / worktree`.)*
- **U-AS-13** — `mcp_transport_floor` 5-row table per §10.1 (STDIO→`max(T3,blast_radius)`, L0→REFUSE, L1/L3→`blast_radius_floor`, L2→`max(T4,blast_radius)`); `rejects_at_registration` true only for L0. Holds.
- **U-AS-14** — `GateLevel` 3 values byte-exact (`auto`/`ask`/`deny`) per §12.1; 5-axis `max()` composition transcribes the §12.1 formula. Holds. *(Contrast CP U-CP-43, whose `GateLevel` was a 4-value invented enum — the AS plan's `GateLevel` is the spec-canonical 3-value set. C-AS-12 §16.2/§12.1 cite `{auto, ask, deny}`; AS conforms.)*
- **U-AS-15** — `persona_tier_traversal_ascends`, bridging-arc raise, `detect_tier_downgrade_governance_violation` all transcribe spec §12.4. Holds.
- **U-AS-16** — `SANDBOX_ATTRIBUTE_SCHEMA` 7 entries with attribute names byte-exact per §15.2; `SandboxTechClass` 5 values (`microvm/container/vm/language-level/fs-overlay`); `SandboxProvider` 17 values; `provider_belongs_to` join matches §15.3 row-by-row. **Holds on the seven `sandbox.*` attribute names + the tech/provider join.** *(The one defect on U-AS-16 is acc #6's reliance on U-AS-08's divergent `AssignedTierReason` enum — folded into the U-AS-08 row above, not a separate U-AS-16 fork.)*
- **U-AS-17** — span hierarchy 5 event kinds per §15.1; `sandbox.enter` 10-attribute set per §15.1 hierarchy block. Holds. *(`SENSITIVE_DATA_EXCLUSIONS` "cardinality 4" — see Findings-rejected item 1.)*
- **U-AS-18** — sampling policy 4 rows per §15.4 (enter/exit base-rate; violation always-sampled-with-tail-keep; tier_escalation always-sampled-head-1.0); audit-floor enforcement. Holds.
- **U-AS-19** — idempotency-key composition, sub-agent derivation strategy, cost-attribution join — consume cross-axis IS types via declared `(cross-axis: IS)` edges to U-IS-07/U-IS-12; no within-axis verbatim claim diverges. Holds.
- **U-AS-21** — 4 negative-observation invariants per §5.3 (`NegativeObservationSurface` 4 values match the four §5.3 rows). Holds.
- **U-AS-22** — `SecretAllowlistEntry` 2 fields per §6.1 verbatim; allowlist-intersection per §6.2; orthogonal-to-tier per §6.2 row 2. Holds **on the §6.1 transcription** — the defect is purely the carrier-ordering relative to U-AS-07 (Pattern B row, fork-queue item 9), not a §6.1 divergence.
- **U-AS-23** — `PassthroughViolationKind` 3 values + redaction surfaces per §6.3 three rows. Holds.
- **U-AS-24** — `SecretFailClass` 5 values byte-exact snake_case per §7.1 (`secret_unknown`…`secret_revoked`); per-class C5/C9 metadata transcribes the §7.1 table row-by-row; per-`(secret_backend, scope)` breaker per §7.3. Holds — a faithful transcription.
- **U-AS-25** — `compute_outputs_hash` implements the §8.1 `SHA-256(canonicalize_concat(name, scope, last_rotated_at))` formula; `canonicalize_concat` delegated to U-IS-08 cross-axis. Holds.
- **U-AS-26** — audit-entry composition against the C-IS-05 six-field shape; per-field population transcribes the §8.2 table; cross-axis IS deps (U-IS-07/09/10) declared. Holds.
- **U-AS-27** — per-fetch emission discipline per §8.4; six-attribute D-derivative span schema per §8.4 row 3 + ADR-F5 §Consequences (c). Holds.
- **U-AS-29** — `D1EngineClass` 5 values; `ENGINE_CLASS_COMPOSITION_OVERLAY` 5 rows per §13.3; `MODEL_BINDING_MATRIX` 20 cells (4×5) per §13.4; `MODEL_TIER_ESCALATION_CHAIN` ascending. Holds. *(`SubAgentRole` / `AnthropicModel` are declared in U-AS-29's own Signatures block.)*
- **U-AS-31** — six namespaces `anthropic/mcp/skill/managed_agents/files/memory` with per-namespace attribute counts 10/7/6/3/8/6 = 40, every attribute name byte-exact against §14.2–§14.7. Holds — the cleanest large transcription in the plan.
- **U-AS-32** — sampling policy 6 rows per §14.8; `AUDIT_FLOOR_COMMITMENTS` 5 scopes per §14.8 audit-floor block; D6 forward-reference per §14.9. Holds.
- **U-AS-33** — `AS_SUBSTRATE_SEAM_EXPORTS` 7 entries matching spec §16.1–§16.7; carrier-unit lists resolve to filed units. Holds **as a manifest** — but every carrier-unit citation that points at a Pattern-A/B-divergent unit (U-AS-08, U-AS-09, U-AS-10, U-AS-28, U-AS-30) inherits that unit's divergence; folded into the cross-unit propagation note, not a separate U-AS-33 fork.
- **U-AS-30** — `GRACEFUL_DEGRADATION_POLICY` 11 rows per §13.5; `C6_CROSS_FAMILY_FALLBACK_CHAIN` 5 steps per §13.5 row 4; `MemoryToolStorageBackend` 5 values per §13.6 step 8. **The §13.5/§13.6 transcription holds** — U-AS-30's defect is purely the undeclared element/field types (`Provider`, `ModelClass`, `ExtendedThinkingEffort`, `BatchApiCell`, `WorkloadManifestOverrides`; Pattern B row), not a verbatim-content divergence.

---

## Findings considered and rejected (transparency)

1. **U-AS-17 `SENSITIVE_DATA_EXCLUSIONS` "cardinality 4" — marginal, NOT escalated to a fork.** Acc #4 claims the exclusion set has 4 entries (`sandbox_resident_filesystem_state`, `sandbox_resident_screenshot_context`, `tool_io_raw_content`, `secret_value`). Spec §15.5 is a 3-row prose table (structure-not-content / T-perm-2-surface exclusion / C-AS-08 composition) and does **not** enumerate a 4-element machine set. The plan's 4-entry set is a faithful *operationalization* of §15.5's prose (the four items are each named in §15.5 prose or in §5.3) but the "cardinality 4 verbatim per §15.4" framing is loose — §15.4 is the sampling section, not the exclusion list. Recorded as a marginal citation/count drift, Class 1; not escalated because the set contents are spec-traceable. Operator may fold the citation correction (§15.4→§15.5) into any U-AS-17 revision. *Decision-vocabulary label: proposing.*
2. **Casing convention is not a divergence (FM-D self-check).** `TIER_1_PROCESS`↔`tier-1-process`, `MICROVM_FIRECRACKER`↔`microvm-firecracker`, `AUTO`↔`auto`, `SECRET_UNKNOWN`↔`secret_unknown`, `EVENT_SOURCED_REPLAY`↔`event-sourced-replay` were checked at U-AS-01/03/04/11/14/24/29 and treated as Python-stack naming convention. Mechanical "any casing difference is a finding" was avoided.
3. **Cross-axis IS types are NOT undeclared-type findings.** `StateLedgerEntry`, `IdempotencyKey`, `Actor`, `Bytes32`, `ISO8601Timestamp`, `FilesystemPathContract`, `ChainVerificationResult` arrive via the IS plan v1 export seams; every consuming unit (U-AS-19/25/26/27/28/29/30) declares the corresponding `(cross-axis: IS)` dependency edge to U-IS-07/08/09/10/11/01/02. Carrier resolves out-of-axis-in-cone. No finding. (Contrast `ToolMetadata`/`TaintState`/etc. — no IS carrier, no edge.)
4. **`JSONSchema` + OTel-SDK / data-model primitives — NOT findings.** `JSONSchema` (U-AS-07 `ToolContract.input_schema`/`output_schema`) is a stack-primitive (the JSON Schema standard), the analog of `string`/`int`; spec §3.1 itself types the field `JSONSchema`. Likewise `SpanId`, `MonotonicTimestamp`, `AttributeValue`, `AttributeValueType`, `Cardinality` (U-AS-16/17/19) are OpenTelemetry SDK / span-data-model primitives — the OTel libraries are a `Target_Stack_Commitment` adoption, not harness auxiliary types requiring a plan carrier. Excluded from Pattern B on the same ground as `JSONSchema`. No carrier needed for any.
5. **Dependency-graph acyclicity — checked, no finding.** §3.2's 88 within-axis edges + §3.3 Kahn verification place all 33 units across 9 levels; cross-axis edges are unidirectional AS→IS. No cycle. The undeclared-type findings are NOT cycle findings — they are *missing nodes/edges*, a distinct defect (the graph is acyclic but incomplete).
6. **A2 (silent scope narrowing) self-check.** U-AS-06/09/20 each silently extend or alter the cited signature contract; U-AS-08/12 silently substitute enum members. Same A2 shape behind Tension 002. Confirmed present.
7. **A4 (fabricated citations) self-check.** All `Implements:` citations resolve to real spec C-AS-NN sections; the defect is divergence-from-cited-content and missing-carrier, not citation fabrication. U-AS-28 acc #1's `byte_exact_per_spec_13_1` test cites a real section (§13.1) that simply contains no string set — folded into the U-AS-28 row, not a separate A4 finding.
8. **A8 (framing contamination) sweep.** No AS unit commits a persona, stack, or deployment value the workspace `CLAUDE.md` framing leaves uncommitted; `DeploymentSurface`/`PersonaTier` appear as committed AS spec enums, not single-surface assumptions. No framing-contamination finding.
9. **U-AS-31 — checked hardest, cleanest result.** The six-namespace 40-attribute transcription was the largest verbatim surface in the plan; every attribute name was cross-checked against §14.2–§14.7. It holds byte-exact. Recorded here so the operator sees the clean outcome is a *result*, not an unchecked unit.
10. **`SandboxProvider` 17-value enum (U-AS-16) — checked, holds.** The 17 provider values map onto spec §15.3's join table (6 microvm + 4 container + 0 vm + 2 language-level + 5 fs-overlay = 17). Cardinality and the per-tech partition match §15.3. No finding.
11. **The buffer-1 findings are folded, not re-derived.** U-AS-06 (F3-01), U-AS-08 (F3-03), U-AS-10 (F2-01), U-AS-20 (F3-02), U-AS-28 (F2-02), U-AS-10/U-AS-02 (F2-04) appear in the inventory tables above as single rows with a `buffer-1` reference. Re-deriving them was explicitly out of scope per the task.

---

## §4.1 severity classification

All 11 Class-3 findings share one discriminator: **discriminator (b) — requires upstream-phase artifact revision.** Each is a Phase-6 plan artifact whose divergence is resolved only by a Phase-6 implementation-plan revision-pass (and, for U-AS-06/09, a Phase-5 spec reconciliation). The spec C-AS-* sections are canonical for the plan per `CLAUDE.md` §1.3; the plan is the artifact in error — **except** U-AS-06 / U-AS-09, where the spec C-AS-02 §2.2/§2.3 itself under-specifies the `sandbox_tier_floor` signature (the §2.3 trust-level table is inexpressible from the §2.2 four-arg call site), so resolution there requires a *spec* revision, not a plan conformance.

The 4 Class-2 findings name discriminator **(a)** — substantive content of a current-phase (Phase-6 plan) artifact; resolution is plan-internal (carrier declaration / acceptance-criterion correction) with no upstream change. The 2 Class-1 findings (U-AS-17 §15.4 citation drift; U-AS-20 `SecretScope` ellipsis-body) are documentation drift.

Severity distribution: 11/4/2 — not skewed to either extreme (FM-A / FM-B check). The 15 units carrying a blocking-or-operator-decision finding = 12 FORK + 3 CONFORM (the 3 CONFORM units clear automatically once their cited divergent unit conforms — they are propagation-gated, not independently defective). 18 of 33 units CLEAR — within the buffer-1-calibrated band (~half the plan carries a verbatim/carrier issue once the CLEARED-but-propagation-tainted units are counted).

---

## Systemic-pattern section (SKILL.md §6 — ≥3 occurrences)

The §6 threshold (≥3 → systemic pattern) is crossed **twice**. The AS plan carries two distinct systemic diseases; the CP/OD plans carried only the first.

### Pattern A — un-audited "verbatim" acceptance-criterion claims

Occurrences: U-AS-06, U-AS-08, U-AS-09, U-AS-10, U-AS-12, U-AS-20, U-AS-28 — **7 units**. The shape: a Phase-6 plan unit asserts a signature/enum is materialized "per §X verbatim" / "exactly N" / "byte-exact" against a `Spec_Action_Surface` contract the signature does not transcribe. Sub-shapes:
- **A1 — enum-member substitution at matching cardinality** (U-AS-08 `AssignedTierReason`, U-AS-12 `override_scope` scope set) — the OD "cardinality-matches / set-diverges" shape.
- **A2 — signature carries a parameter the cited contract omits** (U-AS-06, U-AS-09 — both the `sandbox_tier_floor` 4-vs-5-arg gap; U-AS-20 `fetch_secret` 2-vs-3-arg).
- **A3 — acceptance criterion asserts a spec property the cited section does not contain** (U-AS-28 "kebab-case verbatim" against a §13.1 prose name table; U-AS-10 `PROCESS_FS_OVERLAY` against the landed `SandboxProviderClass`).

This is the same disease the §4A audit found in the CP plan (7 units) and OD plan (10 units). AS plan v1 was never §4A-verbatim-audited; this pass is the canonical systemic-tension record for AS, the way `verbatim_audit_cp_plan.md` was for CP.

### Pattern B — auxiliary types referenced at typed signature positions with no declaring carrier

Occurrences: `ToolMetadata` (U-AS-06), `TaintState` + `MCPServer` (U-AS-08), `MCPServer` (U-AS-14), `AnchorCitation` (U-AS-28), `ToolContext` (U-AS-02, U-AS-10), `RawContractInput` (U-AS-07), `ExtendedThinkingEffort` + `BatchApiCell` + `WorkloadManifestOverrides` + `Provider` + `ModelClass` (U-AS-30), and the carrier-ordering case `SecretAllowlistEntry` (U-AS-07 consumes before U-AS-22 declares). **≥7 consuming units, ≥11 distinct types.** No `record`/`enum`/`opaque type` declaration site exists for any of them; none is in the consuming unit's `Depends on` cone.

This pattern is **distinct** from the CP/OD experience — neither CP nor OD plan exhibited it systemically (Tension 003's lone `WorkloadClass` was a single instance, resolved by adding U-CP-00). The AS plan's §5.4.1 auxiliary-type audit (47 types "verified as faithful factor-out") and §5.5 anti-pattern audit ("Missing dependencies ✅ NOT PRESENT") **both missed it** — the plan's self-audit blind spot is itself a marker of the structural defect.

The two patterns have **different conformance shapes** and the §4A recommendation addresses each: Pattern A is a signature/enum *transcription* fix (conform plan to spec, with two units routing to a *spec* reconciliation); Pattern B is a dependency-graph *completion* fix (declare carriers + add `Depends on` edges, or document an inline-auxiliary-type discipline).

---

## U-AS-02 retrospective (task-mandated)

U-AS-02 is **landed** (operational-minimum, 2026-05-15). Its Signatures block declares `function forced_tier(ctx: ToolContext)` and its Inputs prose describes `ToolContext` as "carrying `computer_use_bound: bool` and `code_execution_beta_invoked: bool`" — but **no unit, U-AS-02 included, declares a `record ToolContext`**. U-AS-02's `Depends on` is `[U-AS-01]`, and U-AS-01 does not declare `ToolContext`. The field set is given only as Inputs prose, never in record form.

U-AS-02 therefore landed against an **undeclared type** — the Pattern B shape, in a unit that is already in `state.jsonl`. Two possibilities, neither verifiable from the plan text and the reviewer being READ-ONLY with respect to landed source: (a) the coding lane inline-materialized `ToolContext` from the Inputs prose at landing time, or (b) the gap was silently absorbed (X-AL-3 risk — `CLAUDE.md` §4.4 / I-2). Buffer-1 F2-04 already flagged this; the plan-wide pass confirms it.

**Verdict: this is a §2.7.6 Class 3 (informational) back-flow at minimum, and it requires explicit operator attention.** The recommendation: before any further AS unit that consumes `ToolContext` lands (U-AS-10 is the next such unit, and it is FORK-blocked anyway), a retrospective check of the landed U-AS-02 materialization must confirm the inline `ToolContext` is (i) field-complete against the Inputs prose and (ii) consistent with the shape the AS-plan revision-pass will give `ToolContext` when it declares the carrier (Pattern B resolution). If the revision-pass gives `ToolContext` a different field set or merges it into `CallSiteContext`, the landed U-AS-02 must be revised to match — i.e. **U-AS-02 may need re-visiting** and the operator should not treat its landed status as closing the gap. Logged as a §2.7.6 Class 3 informational against the Phase 7 execution log; the retrospective check is the operator action it triggers.

---

# §4A Resolution Recommendation — AS-plan verbatim-divergence + undeclared-type cluster

*Appended 2026-05-15 per `systems-architect` SKILL.md §4A (Phase-7 tension-resolution mode). This audit report is the canonical systemic-tension record for the AS-plan cluster (per the Phase-7 checkpoint decision: no per-unit Tension proliferation). The §4A recommendation is **a recommendation** — the operator holds decision authority (§4A.4).*

## §4A.1 — Precise tension statement

The AS plan v1 carries two systemic defects, both crossing the SKILL.md §6 ≥3-occurrence threshold:

- **Pattern A (verbatim-divergence):** 7 units — U-AS-06, U-AS-08, U-AS-09, U-AS-10, U-AS-12, U-AS-20, U-AS-28 — assert a signature/enum is materialized "per §X verbatim" against a `Spec_Action_Surface` contract the signature does not transcribe. Precise per-unit divergence in the Pattern A inventory tables above (not re-summarized here per §4A.2).
- **Pattern B (undeclared-type / no-carrier):** ≥7 units consume ≥11 distinct auxiliary types at typed signature positions with no declaring carrier and no dependency-graph edge. Precise per-type list in the Pattern B inventory table above.

## §4A.2 — Authority-chain placement

`CLAUDE.md` §1.3 chain: ADR → ADD v1.3 → PRD v1.1 → **per-axis spec v1.x** → **per-axis plan v2.x**. The spec is canonical for the plan.

- **Pattern A, most units:** the divergent surface is a Phase-5 `Spec_Action_Surface` contract vs. a Phase-6 `Implementation_Plan_Action_Surface_v1` unit body. Spec strictly above plan; **the plan is the artifact in error** — conform plan to spec. This is authority-chain-determinate (the §4A "an artifact simply diverged from the chain" case).
- **Pattern A, U-AS-06 + U-AS-09 exception:** the `sandbox_tier_floor` signature gap is a **spec under-specification** — C-AS-02 §2.3's trust-level lookup table is inexpressible from the §2.2 four-argument call site. Here the *spec* is the artifact in error; conforming the plan to the spec-as-written is impossible. This routes to a **Phase-5 AS spec revision** reconciling the §2.2 call site and §2.3 table (and the §11.1 sub-agent call site in the same pass).
- **Pattern B:** the AS plan declares (or fails to declare) H_T structured types the spec does not enumerate field-by-field. For most Pattern-B types the resolution is plan-internal (the plan adds the carrier). But the operator must confirm, per type, whether the type is a *faithful factor-out of spec content* (plan-internal carrier declaration suffices) or a *plan-introduced design extension* (X-AL-3 / I-2 — route to spec back-flow). `ToolMetadata`, `TaintState`, `MCPServer`, `RawContractInput`, `WorkloadManifestOverrides` are the candidates that may be design extensions rather than factor-outs.

## §4A.3 — §2-discipline analysis

- **Five-axis:** every divergent surface is an Action-Surface-axis primitive (sandbox-tier composition, gate-level, override scope, secret-fetch, Anthropic-primitive matrix). Within-axis plan/spec conformance + plan dependency-graph completion; no cross-axis re-decomposition.
- **Probabilistic–deterministic boundary:** every divergent surface is a **deterministic-side** primitive — an enum, a composition-function signature, an audit-floor table. A divergent `AssignedTierReason` value or a 5-vs-4-arg `sandbox_tier_floor` propagates verbatim into every consumer and breaks composition silently. The cost of leaving it unconformed is high.
- **Decision ordering:** the divergences are **D-level** (derivative materialization), not F-level. *That* the AS axis commits these enums/signatures/types is held by the spec and not in question; the defect is the plan's derivative materialization diverging — except the Pattern-A U-AS-06/09 spec-gap and the Pattern-B design-extension candidates, where a genuine (small) design decision is owed.

## §4A.4 — Recommended reading

**A single `implementation-planner` revision-pass on `Implementation_Plan_Action_Surface` (next version bump), carrying two internal sub-passes:**

1. **Pattern A sub-pass — verbatim conformance.** Conform U-AS-08, U-AS-10, U-AS-12, U-AS-20, U-AS-28 to the cited spec section verbatim (enum members / signature shape / acceptance-criterion text). For U-AS-08 this is the OD "conform the member set, not just the count" instruction — `AssignedTierReason` must become the spec §15.2 7-value set. For U-AS-20, conform `fetch_secret` to the 2-parameter §5.1 signature and thread `tier` via a context object (or — operator's call — adopt the 3-param form by Phase-5 spec revision; the reviewer does not pick).
2. **Pattern B sub-pass — carrier declaration + dependency-graph completion.** For each undeclared type, either (a) declare the carrier (`record`/`enum`) in a unit with an explicit `Depends on` edge to it, or (b) document an inline-auxiliary-type materialization discipline (type materialized inline at first-consuming unit, §3.4 table noting it). Fix the `SecretAllowlistEntry` carrier-ordering: U-AS-07 must specify the interim `required_secrets` element shape, or U-AS-22's declaration must move ahead of U-AS-07 in the graph. Re-run the §5.4.1 auxiliary-type audit so it actually enumerates all consumed types.
3. **Cross-unit propagation (mandatory, same pass):** conforming a foundational enum/signature renames every downstream consumer. U-AS-08 `AssignedTierReason` → U-AS-16 (`sandbox.policy.assigned_tier_reason`), U-AS-17, U-AS-33. The `sandbox_tier_floor` signature reconciliation → U-AS-06, U-AS-08, U-AS-09, U-AS-13, U-AS-14. `ToolContext` carrier declaration → U-AS-02 (landed — retrospective check), U-AS-10. The pass must conform consumers in the same revision or composition breaks at the rename.

### Items requiring a Phase-5 spec revision or an explicit operator decision (NOT plan-internal conform)

1. **U-AS-06 + U-AS-09 `sandbox_tier_floor` signature gap — Phase-5 AS spec revision.** C-AS-02 §2.2/§2.3 (and §11.1) must be reconciled so the `sandbox_tier_floor` signature and its call sites agree on the trust-level argument. Not resolvable inside the plan conformance pass. §2.7.6 **Class 1 (halt)**.
2. **U-AS-20 conformance direction — operator decision.** (R1) spec §5.1 + C-AS-05 title adopt the 3-parameter `fetch_secret` form (Phase-5 spec revision), or (R2) plan reverts to 2 parameters + context object (plan revision). The reviewer does not pick. §2.7.6 **Class 1 (halt)**.
3. **U-AS-12 reading — operator decision (fork-queue item 10).** Reading (A) "non-compliance cells" = "any cell" for solo persona (only the "verbatim" claim is loose — plan-internal fix) vs Reading (B) plan over-permits and `override_scope` needs a compliance-status input (Phase-5 spec or plan signature revision). §2.7.6 **Class 1 (halt)** pending the read.
4. **Pattern B factor-out-vs-extension classification — per-type operator confirmation.** For each Pattern-B type, the operator confirms it is a faithful factor-out (plan-internal carrier OK) or a design extension (route to spec back-flow per X-AL-3). The likely-factor-outs (`AnchorCitation`, `ToolContext`, `ExtendedThinkingEffort`, `BatchApiCell`, `Provider`, `ModelClass`) need only carrier declaration; the likely-extensions (`ToolMetadata`, `TaintState`, `MCPServer`, `RawContractInput`, `WorkloadManifestOverrides`) may need a C-AS-02/§3 spec extension first.
5. **U-AS-02 retrospective check (§"U-AS-02 retrospective").** §2.7.6 **Class 3 (informational)** — verify the landed `ToolContext` materialization before the revision-pass fixes the carrier; revise U-AS-02 if the carrier shape differs.

## §4A.5 — Tiebreaker check

No ADR / ADD / PRD revision postdates the cited `Spec_Action_Surface` sections and re-commits the plan's divergent vocabulary. The AS spec v1→v1.1 change-note records only an ADR-D3 v1.1→v1.2 citation-token bump (F-AS-01 nine→eleven-primitive alignment) — it touches none of the seven Pattern-A divergent surfaces. No D-ADR re-enumerates sandbox-tier composition, gate-level, override-scope, or secret-fetch vocabulary post-spec. **Determinate for Pattern A's plain-conformance units: spec canonical, plan conforms.** The non-determinate items are exactly those enumerated in §4A.4's "requiring a decision" list.

**Citation-pattern note.** Unlike OD U-OD-30, no AS Pattern-A unit cites an ADR in its divergent acceptance criterion as the verbatim authority — every divergent AS unit cites a `Spec_Action_Surface` C-AS-NN section. The ADR-direct tiebreaker read was therefore not load-bearing for AS. (ADR-F4/F5/D2/D3 were consulted for the U-AS-06/09 spec-gap analysis; none contradicts the audit.)

**Load-bearing-artifact flag:** the resolution touches no `CLAUDE.md` anti-leakage rule and no F-ADR. The cluster needs operator **ratification** of the Pattern-A conformance direction + the Pattern-B classification calls + the §4A.4 decision items.

## §4A.6 — Fork classification

Per `Project_Workflow_v1_8.md` §2.7.6: **Class 1 (halt-execution)** for the 11 Class-3 findings — a design-phase artifact (the AS plan, and for U-AS-06/09 the AS spec) requires revision before the affected units land. Under the `design-substrate/`-is-canonical posture (back-flow deprecated 2026-05-15), Class 1 means: halt landing of the affected units, run the `implementation-planner` revision-pass (and `spec-writer` reconciliation for the §2.2/§2.3 gap) in-CLI, re-clear, land. **U-AS-02 is the one cluster-adjacent unit already landed** — it is the §4A.4 item 5 retrospective check.

## §4A.7 — Operator decision required

**The operator decides.** This §4A section recommends; it does not decide and does not edit the plan. Operator actions:

1. **Ratify** the Pattern-A conform-to-spec direction for the plain-conformance units (U-AS-08, U-AS-10, U-AS-12-if-Reading-A, U-AS-28) — authority-chain-determinate.
2. **Decide** the §4A.4 decision items: U-AS-06/09 spec reconciliation; U-AS-20 R1-vs-R2; U-AS-12 Reading A-vs-B.
3. **Classify** each Pattern-B type as factor-out (plan-internal carrier) vs design extension (spec back-flow).
4. **Authorize** the U-AS-02 retrospective check before the revision-pass lands.

On ratification: `implementation-planner` revision-pass on `Implementation_Plan_Action_Surface` (Pattern A conformance + Pattern B carrier declaration + cross-unit propagation + re-run §5.4.1 audit) → version bump; `spec-writer` reconciliation of C-AS-02 §2.2/§2.3/§11.1 if the operator routes U-AS-06/09 to spec → AS spec version bump → re-clear → land.

---

## Pipeline disposition

Per-unit verdict for `pipeline-cleared-queue.md` / `pipeline-fork-queue.md`. **CLEARED** = no divergence, enters cleared queue. **CONFORM** = authority-chain-determinate plan→spec fix (no operator decision; `implementation-planner` applies, then clears). **FORK** = operator decision / spec back-flow needed before clearing.

| Unit | Verdict | Basis |
|---|---|---|
| U-AS-01 | **CLEARED** | `SandboxTier`/`BlastRadiusTier`/`MechanismClass` transcribe spec §1.1/§1.2; no divergence |
| U-AS-02 | **FORK** | Landed unit; `ToolContext` undeclared (Pattern B) — §2.7.6 Class 3 informational retrospective check (§4A.4 item 5) |
| U-AS-03 | **CLEARED** | `SandboxFailClass` 7-value + metadata transcribe spec §4.1–§4.3 |
| U-AS-04 | **CLEARED** | `DeploymentSurface`/`PersonaTier`/`MCPTransport` transcribe spec §9.1/§10.1 |
| U-AS-05 | **CLEARED** | `blast_radius_floor` transcribes spec §2.4 |
| U-AS-06 | **FORK** | buffer-1 F3-01 (`sandbox_tier_floor` 5th param — spec under-specification) + F3-03 (`ToolMetadata` undeclared) — §2.7.6 Class 1 |
| U-AS-07 | **FORK** | `RawContractInput` undeclared; `SecretAllowlistEntry` carrier-ordering (fork-queue item 9) — §2.7.6 Class 2 |
| U-AS-08 | **FORK** | `AssignedTierReason` 7-value member-set diverges from spec §15.2 (Pattern A1); `TaintState`/`MCPServer` undeclared (F3-03) — §2.7.6 Class 1 |
| U-AS-09 | **FORK** | `sub_agent_sandbox_tier` 5-param vs spec §11.1 4-param (Pattern A2) — §2.7.6 Class 1; folded into U-AS-06 spec reconciliation |
| U-AS-10 | **FORK** | buffer-1 F2-01 (`PROCESS_FS_OVERLAY` not in landed enum) + F2-04 (`ToolContext` undeclared) — §2.7.6 Class 2 |
| U-AS-11 | **CLEARED** | `SandboxProviderClass` 6-value + tier_mapping transcribe spec §9.2 |
| U-AS-12 | **FORK** | `override_scope` "any cell" vs spec §9.4 "non-compliance cells" (Pattern A1; fork-queue item 10, two readings) — §2.7.6 Class 1/2 |
| U-AS-13 | **CLEARED** | `mcp_transport_floor` 5-row transcribes spec §10.1 |
| U-AS-14 | **FORK** | `GateLevel` transcribes §12.1 (clean), but `MCPServer` undeclared in `GateLevelFloorInterfaces` (Pattern B) — §2.7.6 Class 1 |
| U-AS-15 | **CLEARED** | cross-deployment monotonicity transcribes spec §12.4 |
| U-AS-16 | **CONFORM** | 7 `sandbox.*` attribute names + tech/provider join hold; only defect is acc #6 citing U-AS-08's divergent `AssignedTierReason` — clears once U-AS-08 conforms (determinate propagation) |
| U-AS-17 | **CLEARED** | span hierarchy + event kinds transcribe spec §15.1; `SENSITIVE_DATA_EXCLUSIONS` count drift is Class-1 inline fix (Findings-rejected item 1), non-blocking |
| U-AS-18 | **CLEARED** | sampling policy 4-row transcribes spec §15.4 |
| U-AS-19 | **CLEARED** | idempotency-key composition; cross-axis IS deps declared; no divergence |
| U-AS-20 | **FORK** | buffer-1 F3-02 (`fetch_secret` 3-param vs spec §5.1 2-param; R1-vs-R2 operator decision) — §2.7.6 Class 1 |
| U-AS-21 | **CLEARED** | negative-observation invariants transcribe spec §5.3 |
| U-AS-22 | **CONFORM** | `SecretAllowlistEntry` transcribes §6.1; carrier-ordering defect is plan-internal graph fix (folded with U-AS-07); clears once the graph edge is fixed |
| U-AS-23 | **CLEARED** | passthrough constraints transcribe spec §6.3 |
| U-AS-24 | **CLEARED** | `SecretFailClass` 5-value + metadata transcribe spec §7.1–§7.3 |
| U-AS-25 | **CLEARED** | `outputs_hash` formula transcribes spec §8.1; cross-axis IS dep declared |
| U-AS-26 | **CLEARED** | audit-entry composition transcribes spec §8.2/§8.3; cross-axis IS deps declared |
| U-AS-27 | **CLEARED** | per-fetch emission transcribes spec §8.4/§8.5 |
| U-AS-28 | **FORK** | buffer-1 F2-02 (`AnthropicPrimitive` "kebab-case verbatim" vs §13.1 prose name table) + F3-03 (`AnchorCitation` undeclared) — §2.7.6 Class 2 |
| U-AS-29 | **CLEARED** | engine-class overlay + model-binding matrix transcribe spec §13.3/§13.4 |
| U-AS-30 | **FORK** | §13.5/§13.6 content transcribes cleanly, but `ExtendedThinkingEffort`/`BatchApiCell`/`WorkloadManifestOverrides`/`Provider`/`ModelClass` undeclared (Pattern B — newly surfaced) — §2.7.6 Class 1 |
| U-AS-31 | **CLEARED** | six-namespace 40-attribute schema transcribes spec §14.1–§14.7 byte-exact |
| U-AS-32 | **CLEARED** | sampling policy + audit-floor commitments transcribe spec §14.8/§14.9 |
| U-AS-33 | **CONFORM** | manifest 7-entry structure holds; carrier-unit citations to U-AS-08/09/10/28/30 inherit those units' divergences — clears once the cluster conforms (determinate propagation) |

**Tally: CLEARED 18 · CONFORM 3 (U-AS-16, U-AS-22, U-AS-33 — all propagation-determinate, clear once their cited divergent unit conforms) · FORK 12 (U-AS-02, 06, 07, 08, 09, 10, 12, 14, 20, 28, 30 — plus U-AS-09 folds into U-AS-06's spec reconciliation).**

The 12 FORK units do not enter `pipeline-cleared-queue.md`; they route to `pipeline-fork-queue.md` (items 9–15 already there for U-AS-06/07/08/10/12/20/28 — this audit adds U-AS-02, U-AS-09, U-AS-14, U-AS-30 and supplies the systemic §4A resolution that supersedes the per-unit provisional classifications). The 18 CLEARED units flow to the cleared queue. The 3 CONFORM units clear automatically once the single AS-plan revision-pass conforms the units they cite.

---

*Phase-7 pre-implementation review, review-ahead pipeline pass Q1 — plan-wide systemic audit of `Implementation_Plan_Action_Surface_v1.md` (all 33 units). Two systemic attacks: verbatim-claim divergence + undeclared-type/no-carrier. Read-only with respect to all `design-substrate/` artifacts, `CLAUDE.md` files, plans, specs, and source — no repository file modified. Buffer-1 findings folded by reference, not re-derived. Findings classified, not absorbed (X-AL-3). Authored 2026-05-15 per `harness-adversarial-reviewer` SKILL.md Phase-7 pre-implementation review mode; §4A appendix per `systems-architect` SKILL.md §4A tension-resolution mode.*
