# Implementation Plan — Action Surface (v1.1)

## Status block

| Field | Value |
|---|---|
| Artifact | `Implementation_Plan_Action_Surface_v1_1.md` |
| Status | **Proposed** (v1.1 delta over v1; pending P6-CK clearance) |
| Date | 2026-05-15 |
| Phase | 7 sub-phase 7b — revision pass R3 (third of the R1–R5 carrier-map absorption sequence) |
| Skill | `implementation-planner` SKILL.md §8 revision-pass sub-mode |
| Axis | Action Surface (AS) |
| Predecessor | `Implementation_Plan_Action_Surface_v1.md` (v1, 2026-05-14) |
| Source-set (R3) | `.harness/revision_R3_as_plan.md` (operator-ratified R3 revision proposal); `.harness/verbatim_audit_as_plan.md` (Q1 — canonical AS systemic-tension record); `.harness/shared_type_carrier_map.md` (T1); `.harness/xal3_resolution_recommendations.md` (T2); `.harness/revision_R1_harness_core.md` §3.2 + §4; `design-substrate/Implementation_Plan_Harness_Core_v1_0.md` (U-CORE-01); `design-substrate/Implementation_Plan_Action_Surface_v1.md`; `design-substrate/Spec_Action_Surface_v1.md` |
| Plan shape | Axis-led (unchanged from v1) |
| Sub-mode | Revision-pass (v1 → v1.1 delta; predecessor v1 is the verbatim base) |

> **Versioning note.** This artifact is **AS plan v1 → v1.1**. It is distinct from **AS spec v1.1** (`Spec_Action_Surface_v1.md` v1.1), already cited as the v1 plan's source-set. "v1.1" in this document means the plan version unless prefixed `spec`.

---

## §0 Change-note

### §0.1 Trigger and scope

R3 is the third of the five carrier-map absorption passes (R1 `harness-core` / R2 IS / R3 AS / R4 CP / R5 OD). It absorbs into the AS plan three ratified upstream inputs:

- `.harness/verbatim_audit_as_plan.md` (Q1) — the canonical AS systemic-tension record. Verdict tally over all 33 units: **18 CLEARED · 3 CONFORM · 12 FORK.** Two systemic diseases: Pattern A (verbatim-claim divergence, 7 units) and Pattern B (undeclared auxiliary types, ≥11 types).
- `.harness/shared_type_carrier_map.md` (T1) — the ratified carrier triage.
- `.harness/xal3_resolution_recommendations.md` (T2) — 27/27 X-AL-3 candidates resolved FACTOR-OUT, 0 genuine extensions. **No AS Pattern B type requires a design-substrate spec revision.**

v1.1 is a **delta over v1**. Unaffected units are `[preserved verbatim]` — the actual file agrees with the preserved-verbatim list (§0.5). Revised units carry full or partial revised bodies (§5). §3 dependency graph and §4 coverage matrix take deltas (§7, §8). A permanent new §5.4.2 exhaustive auxiliary-type audit replaces the defective v1 §5.4.1.

### §0.2 Operator ratification decisions (2026-05-15)

| ID | Decision applied in v1.1 |
|---|---|
| Q-R3-7 + Q-R3-1 sequencing | **Ship-now + defer-4.** v1.1 ships now with the 9 determinate revised units + 20 preserved-verbatim units. The 4 conditional units (U-AS-06, U-AS-09, U-AS-12, U-AS-20) are **deferred to a follow-on R3.1 micro-pass**; in v1.1 each carries its v1 body verbatim plus a `[DEFERRED to R3.1]` marker. Their conditional revised bodies are **not** applied. |
| Q-R3-1 | The C-AS-02 §2.2/§2.3/§11.1 `sandbox_tier_floor` spec gap routes to a `spec-writer` reconciliation pass. U-AS-06/U-AS-09 stay conditional pending it. R3.1 finalizes them once the spec decision lands. (§9 of the R3 proposal is the finding.) |
| Q-R3-3 | **Option (a):** declare `SecretAllowlistEntry` at U-AS-07; add `U-AS-07 Depends on [U-AS-20]`. U-AS-22 consumes it. U-AS-22's one micro-edit is applied. The `[U-AS-20]` edge **is cleanly applicable** in v1.1 — see §0.4. |
| Q-R3-5 | **Yes** — re-home U-AS-28's local `WorkloadClass` to `harness-core` U-CP-00. Delete the local enum from U-AS-28's revised body; add `[U-CP-00 (cross-axis: core)]` edges to U-AS-28 and U-AS-29. (U-AS-29 is CLEARED — the edge is a graph-only delta, no body revision.) |
| Q-R3-6 | **Explicit per-unit core edges** for every `harness-core` consumer (`[U-CORE-01]` / `[U-CP-00]`) — not transitive resolution through U-AS-04's re-export. The §7.1 edge-delta table enumerates the per-consumer edges. |
| Q-R3-8 | Operator confirms T2 `proposing`-row faithfulness by ratification. No further action; the §5 carrier declarations trace each field set to its cited spec section. |

### §0.3 Units revised in v1.1 (9 determinate units)

Full revised bodies (§5):

- **U-AS-02** — Pattern B carrier (`ToolContext`). Landed unit; A-2 retrospective.
- **U-AS-04** — declaration-site conversion (`DeploymentSurface`/`PersonaTier` → `harness-core` import; `MCPTransport` stays AS-owned). Landed unit; A-1 re-check.
- **U-AS-07** — Pattern B carrier (`RawContractInput`); `SecretAllowlistEntry` carrier-ordering fix (Q-R3-3 option (a)).
- **U-AS-08** — Pattern A1 conformance (`AssignedTierReason` → §15.2 7-value set); Pattern B carriers (`TaintState`, `MCPServer`).
- **U-AS-10** — Pattern A3 conformance (provider-class vocabulary; `PROCESS_FS_OVERLAY` removed).
- **U-AS-28** — Pattern A3 conformance (`AnthropicPrimitive` "kebab-case verbatim" claim re-grounded); Pattern B carrier (`AnchorCitation`); local `WorkloadClass` re-homed to U-CP-00 (Q-R3-5).
- **U-AS-30** — Pattern B carriers (`ExtendedThinkingEffort`, `BatchApiCell`, `WorkloadManifestOverrides`, `Provider`, `ModelClass`); `[U-CP-00]` edge for `WorkloadClass`.

Partial revised bodies (§5):

- **U-AS-14** — dependency-graph edge add only (`Depends on` gains `[U-AS-08]` for the `MCPServer` carrier) + one AC note. No signature/AC-text conformance.
- **U-AS-22** — the single micro-edit: `SecretAllowlistEntry` declaration moves out of U-AS-22's Signatures block to a consumption reference (the carrier now lives at U-AS-07 per Q-R3-3 option (a)). U-AS-22 is **not** in the preserved-verbatim list.

### §0.4 The 4 deferred units (R3.1 micro-pass)

The 4 conditional units carry their **v1 bodies verbatim** in v1.1, each with a `[DEFERRED to R3.1]` marker (§5). Their R3 §5 conditional bodies are **not** applied; no `Implements` citation is bumped.

| Unit | Deferral basis | R3.1 conditional on |
|---|---|---|
| U-AS-06 | Pattern A2 — C-AS-02 §2.2/§2.3/§11.1 `sandbox_tier_floor` spec under-specification | Q-R3-1 `spec-writer` reconciliation (Option G-1 vs G-2) |
| U-AS-09 | Pattern A2 — folds into the U-AS-06 spec reconciliation (§11.1 site) | Q-R3-1 `spec-writer` reconciliation |
| U-AS-12 | Pattern A1 — `override_scope` "any cell" vs spec §9.4 "non-compliance cells" | Q-R3-4 Reading A vs Reading B operator decision |
| U-AS-20 | Pattern A2 — `fetch_secret` 3-param plan vs spec §5.1 2-param | Q-R3-2 Option R1 vs Option R2 direction decision |

**Q-R3-3 / U-AS-20 coupling resolution.** Q-R3-3 option (a) adds `U-AS-07 Depends on [U-AS-20]` so `SecretScope` (the type of `SecretAllowlistEntry.scope`) is in-cone for U-AS-07. U-AS-20 is deferred — but the edge **is cleanly applicable** in v1.1: U-AS-20 carries its v1 body verbatim, in which `record SecretScope` already exists as a declared type (its v1 body declares `record SecretScope { ... }`). The carrier-ordering edge depends only on `SecretScope` *existing as a type at U-AS-20*, which is true in the v1 body. What is deferred at U-AS-20 is the **`SecretScope` field-set fix** (replacing the `{ ... }` ellipsis with the explicit field set) and the `fetch_secret` direction decision — neither blocks the edge. **Resolution: the `[U-AS-20]` edge is applied in v1.1; the only residual flagged for R3.1 is the `SecretScope` ellipsis-body field-set fix at U-AS-20.** No coupling defect; the edge and the deferral are independent.

### §0.5 Sections preserved verbatim (20 units)

The following 20 unit bodies are `[preserved verbatim]` from v1 — no body edit. They are listed in §5 as pointers, not restated.

- **18 CLEARED units:** U-AS-01, U-AS-03, U-AS-05, U-AS-11, U-AS-13, U-AS-15, U-AS-17, U-AS-18, U-AS-19, U-AS-21, U-AS-23, U-AS-24, U-AS-25, U-AS-26, U-AS-27, U-AS-29, U-AS-31, U-AS-32.
- **2 CONFORM units (bodies verbatim; propagation handled at §0.6):** U-AS-16, U-AS-33.

U-AS-29 (CLEARED) takes a graph-only `[U-CP-00]` edge in §7.1 — the edge is recorded in the dependency-graph delta; the unit body is unchanged. U-AS-22, the third CONFORM unit, carries the one micro-edit (§0.3) and is therefore listed under revised units, not here.

### §0.6 CONFORM propagation (3 units)

The 3 CONFORM units are propagation-gated, not independently defective:

- **U-AS-16** — acc #6 cites U-AS-08's `AssignedTierReason`. Once U-AS-08 conforms to the §15.2 7-value set, U-AS-16 acc #6 resolves automatically. Body preserved verbatim; citation unchanged (U-AS-08); referent member set conformed. (Minor optional test addition flagged Q-R3-4 in the R3 proposal; not applied here.)
- **U-AS-22** — the carrier-ordering defect is fixed in U-AS-07's revised body. U-AS-22 now *consumes* `SecretAllowlistEntry` (declared at U-AS-07) rather than declaring it. The single Signatures-block micro-edit is applied (§5).
- **U-AS-33** — manifest carrier-unit citations point at unit IDs (U-AS-08/09/10/28/30) that do not change; only member sets inside those units change. Body preserved verbatim. U-AS-33 takes a graph-only `[U-CORE-01]` edge for `UnitId` (§7.1).

### §0.7 R3-application action items (FLAGGED — deferred mechanical / coding-lane actions; NOT performed in this pass)

| ID | Action | Locus | Status |
|---|---|---|---|
| **A-1** | **U-AS-04 landed-source re-check.** U-AS-04 is landed; the §3 declaration-site conversion requires verifying the landed source deletes the local `DeploymentSurface`/`PersonaTier` definitions and re-points to the `harness-core` import. Landed enum values matched U-CORE-01 byte-exact before deletion (confirmed identical: `local-development | self-hosted-server | managed-cloud`; `solo-developer | team-binding | multi-tenant-compliance`). Source-vs-plan reconciliation, not a re-implementation. | landed `harness-as/` source | FLAGGED — coding-lane |
| **A-2** | **U-AS-02 landed-source retrospective.** U-AS-02 is landed; verify the landed `ToolContext` materialization is field-complete (`computer_use_bound: bool` + `code_execution_beta_invoked: bool`) and shape-consistent with the U-AS-02 §5 carrier. If not, U-AS-02 must be re-visited. §2.7.6 Class 3 (informational) back-flow. | landed `harness-as/` source | FLAGGED — coding-lane |
| **A-3** | **AS→IS edge version re-cite.** Bump the AS plan §3.4 cross-axis IS-plan citation from `Implementation_Plan_Information_Substrate_v1` to `Implementation_Plan_Information_Substrate_v2_3` (latest filed; R2 IS revision, proposed status); verify each cited U-IS-NN still exists with the same export seam. Mechanical re-cite per SKILL.md §9 use-latest-version discipline. A renumbered/removed U-IS-NN would surface as a Class 1 fork (not anticipated). **Not performed in this pass** — §3.4's IS-plan citation is left at the v1 value pending A-3. | AS plan §3.4 | FLAGGED — mechanical |
| **A-4** | **§5.4.1 → §5.4.2 audit replacement.** The defective v1 §5.4.1 auxiliary-type audit is superseded by the new exhaustive §5.4.2 audit (§5.4.2 of this plan). The §5.4.2 table is authored here; running it to zero (U) rows against the landed/revised type set is the deferred verification step. | AS plan §5.4 | FLAGGED — partly authored (§5.4.2 below); zero-(U) verification deferred |

### §0.8 Coverage-matrix and dependency-graph delta summary

- **Coverage matrix:** no contract loses coverage. C-AS-09 §9.1/§9.4 enum-axis marks move to U-CORE-01 (multi-unit cross-plan coverage); C-AS-12 §12.2 and C-AS-02 §2.3 forward-use marks drop off U-AS-04; C-AS-10 §10.1's U-AS-04 mark strengthens from forward-use to declaring. Full delta at §8.
- **Dependency graph:** new edges `U-AS-04→[U-CORE-01]`, `U-AS-14→[U-AS-08]`, `U-AS-07→[U-AS-20]`, `U-AS-30→[U-CP-00]`, `U-AS-33→[U-CORE-01]`, `U-AS-28→[U-CP-00]`, `U-AS-29→[U-CP-00]`, plus the Q-R3-6 explicit per-consumer core edges. Acyclic invariant re-verified (§7.4). Full delta at §7.

---

## §5 Revised unit bodies

CLEARED units (18) and the verbatim-preserved CONFORM units (U-AS-16, U-AS-33) are `[preserved verbatim]` from `Implementation_Plan_Action_Surface_v1.md` — pointer only, not restated. The 4 deferred units carry their v1 body verbatim + an R3.1 marker. The 9 determinate revised units carry full or partial revised bodies.

### §5.1 Preserved-verbatim units (pointers)

The following 18 CLEARED unit bodies are `[preserved verbatim]` from v1 §2 — consult `Implementation_Plan_Action_Surface_v1.md`:

U-AS-01, U-AS-03, U-AS-05, U-AS-11, U-AS-13, U-AS-15, U-AS-17, U-AS-18, U-AS-19, U-AS-21, U-AS-23, U-AS-24, U-AS-25, U-AS-26, U-AS-27, U-AS-29, U-AS-31, U-AS-32.

The 2 verbatim CONFORM unit bodies are `[preserved verbatim]` from v1 §2:

- **U-AS-16** — `[preserved verbatim]`. Propagation: acc #6's `AssignedTierReason` referent is the conformed §15.2 7-value set (U-AS-08, §5.4). Citation unchanged.
- **U-AS-33** — `[preserved verbatim]`. Manifest carrier-unit IDs (U-AS-08/09/10/28/30) unchanged; member sets inside them change. Graph-only `[U-CORE-01]` edge for `UnitId` (§7.1).

### §5.2 Deferred units (v1 body verbatim + R3.1 marker)

The 4 units below carry their **v1 body byte-for-byte**, followed by a delimited deferral marker. Their R3 §5 conditional bodies are **not** applied; `Implements` citations are **not** bumped.

#### U-AS-06 — Implement `sandbox_tier_floor` 10-row lookup table

> **`[DEFERRED to R3.1 — conditional on Q-R3-1 spec reconciliation]`.** The C-AS-02 §2.2/§2.3 + C-AS-11 §11.1 `sandbox_tier_floor` signature is a three-way spec self-contradiction (4-arg / trust-keyed-table / 3-arg). R3 cannot conform U-AS-06 to a spec section that is itself incomplete. The body below is the **v1 body, carried unchanged**; U-AS-06 finalizes at the R3.1 micro-pass once the `spec-writer` C-AS-02/§11.1 reconciliation decides Option G-1 (trust level explicit arg) vs G-2 (trust level carrier-borne). The R3 proposal §5/§9 holds the conditional body; it is not applied here. The Pattern B `ToolMetadata` carrier declaration and the verbatim-claim re-grounding are also deferred to R3.1 (they ride with the §9 decision).

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

#### U-AS-09 — Implement `sub_agent_sandbox_tier` monotonic-ascension function

> **`[DEFERRED to R3.1 — conditional on Q-R3-1 spec reconciliation]`.** U-AS-09's `sub_agent_sandbox_tier` signature folds into the same C-AS-02/§11.1 `sandbox_tier_floor` spec gap as U-AS-06 (the §11.1 sub-agent inner call is the third inconsistent site). The body below is the **v1 body, carried unchanged**; U-AS-09 finalizes at R3.1 once the `spec-writer` reconciliation decides whether `sub_agent_sandbox_tier` threads `mcp_trust_level` (Option G-1, 5-param) or conforms to the §11.1 4-param form (Option G-2). `Implements` citation not bumped.

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

#### U-AS-12 — Operator-policy override scope per persona-tier

> **`[DEFERRED to R3.1 — conditional on Q-R3-4 direction decision]`.** AC2 reads "SOLO_DEVELOPER → PERMITTED_APPEND_ONLY at any cell"; spec §9.4 reads solo-developer permitted "at non-compliance cells". Two readings: **A** "non-compliance cells" = "any cell" for the solo persona (AC-text fix only); **B** the plan over-permits and `override_scope` is under-typed (needs a `cell_compliance_status` input + a small spec reconciliation). The body below is the **v1 body, carried unchanged**; U-AS-12 finalizes at R3.1 once the operator picks Reading A or Reading B. `Implements` citation not bumped.

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

#### U-AS-20 — Declare `fetch_secret` signature + `SecretRef` opaque type + tier-aware resolution mechanism table

> **`[DEFERRED to R3.1 — conditional on Q-R3-2 direction decision]`.** `fetch_secret` is declared with 3 params `(name, scope, tier)`; spec §5.1 + C-AS-05 title fix it at 2 `(name, scope)`. Two directions: **R1** spec adopts the 3-param form (Phase-5 spec revision); **R2** plan reverts to 2 params + context object. The body below is the **v1 body, carried unchanged**; U-AS-20 finalizes at R3.1 once the operator picks R1 or R2. The `SecretScope` ellipsis-body field-set fix (replacing `{ ... }` with the explicit field set) is **also deferred to R3.1** — it is the only Q-R3-3-coupling residual (see §0.4): the carrier-ordering edge `U-AS-07→[U-AS-20]` is applied in v1.1 because `SecretScope` already exists as a declared type here. `Implements` citation not bumped.

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

### §5.3 Determinate revised units

The 9 determinate revised units. Each shows the **changed** elements with a `CHANGE:` annotation; unchanged elements are `[unchanged]` and resolve against the v1 body.

#### U-AS-02 — Implement forced-tier resolution predicates (computer-use + code-execution beta)

`[Pattern B carrier — ToolContext. Landed unit; see §0.7 A-2 retrospective.]`

- **Implements:** `[C-AS-01 §1.3]` `[unchanged]`
- **Depends on:** `[U-AS-01]` `[unchanged]`
- **Inputs:** `CHANGE:` prose no longer describes `ToolContext` as an external type — it is now declared in this unit's Signatures block.
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
- **Status:** Pattern B carrier — **decided**. Landed-source retrospective A-2 (§0.7) is the deferred coding-lane verification.

#### U-AS-04 — Declare `MCPTransport` enum + import cross-cutting discriminator enums from `harness-core`

`[Declaration-site conversion — see §0.3. Landed unit; see §0.7 A-1.]`

- **Implements:** `CHANGE:` from `[C-AS-02 §2.3; C-AS-09 §9.1 (forward use); C-AS-12 §12.2 (forward use); C-AS-10 §10.1 (forward use)]` to **`[C-AS-10 §10.1]`** — U-AS-04 now covers only the `MCPTransport` transport-level set; `DeploymentSurface`/`PersonaTier` coverage moves to U-CORE-01.
- **Depends on:** `CHANGE:` from `(none)` to **`[U-CORE-01 (cross-axis: core)]`** — the import edge for `DeploymentSurface` + `PersonaTier`.
- **Inputs:** None (foundational) `[unchanged]`.
- **Signatures:** `CHANGE:` delete `enum DeploymentSurface { ... }` and `enum PersonaTier { ... }`. Add the import line. Retain `MCPTransport`:
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
- **Acceptance criteria:** `CHANGE:` v1 ACs 1 + 2 (`DeploymentSurface`/`PersonaTier` cardinality + ordering) **deleted** — covered at U-CORE-01. Revised AC set:
  1. `MCPTransport` carries exactly five values matching C-AS-10 §10.1 transport-level labels byte-exact.
  2. Adding a value to `MCPTransport` requires Workflow §4.1.2 Class-2 ADR-D2 revision (cardinality bound: 5).
  3. `MCPTransport` identifier strings byte-exact spec-canonical.
  4. `DeploymentSurface` + `PersonaTier` are imported from `harness-core` (U-CORE-01); U-AS-04 does not redeclare them. A local redeclaration is a defect.
  5. Pure data type: no associated functions, no metadata tables.
- **Tests:** `CHANGE:` `test_deployment_surface_*` / `test_persona_tier_*` deleted (they live at U-CORE-01). Retain `test_mcp_transport_cardinality_five`, `test_enum_identifier_strings_byte_exact` (scoped to `MCPTransport`). Add `test_u_as_04_does_not_redeclare_core_enums`.
- **Rollback boundary:** `CHANGE:` Revert the `MCPTransport` declaration + the `harness-core` import. Downstream composition units lose `MCPTransport`; `DeploymentSurface`/`PersonaTier` remain available from `harness-core` (unaffected by a U-AS-04 revert).
- **Status:** Declaration-site conversion — **decided**. Landed-source re-check A-1 (§0.7) is the deferred coding-lane verification.

#### U-AS-07 — Add `ToolContract.minimum_tier` field + declaration discipline + registration enforcement

`[Pattern B carrier — RawContractInput; carrier-ordering fix for SecretAllowlistEntry (Q-R3-3 option (a)).]`

- **Implements:** `[C-AS-03 §3.1, §3.2, §3.3]` `[unchanged]`.
- **Depends on:** `CHANGE:` from `[U-AS-01]` to **`[U-AS-01, U-AS-20]`** — the `[U-AS-20]` edge is added per Q-R3-3 option (a) so `SecretScope` (the `SecretAllowlistEntry.scope` type, declared at U-AS-20) is in-cone. Acyclic: U-AS-20 `Depends on [U-AS-01]` only; no back-edge. The edge is cleanly applicable even though U-AS-20 is deferred — see §0.4.
- **Signatures:** `CHANGE:` Pattern B fixes (decided):
  - Declare `record RawContractInput` — the pre-validation tool-contract serialization shape (un-validated counterpart of `ToolContract`; the §3 registration-input subject).
  - **Carrier-ordering fix for `SecretAllowlistEntry`:** declare `record SecretAllowlistEntry { name: string; scope: SecretScope }` (spec §6.1 2-field shape) **at U-AS-07** as the `ToolContract.required_secrets` element type. U-AS-22 then *consumes* it (populates the access-control semantics); it no longer *declares* it.
  ```
  record RawContractInput { ... raw serialized ToolContract fields, pre-validation ... }
  record SecretAllowlistEntry { name: string; scope: SecretScope }   // moved up from U-AS-22 (Q-R3-3 option (a))
  record ToolContract { name; description; input_schema: JSONSchema; output_schema: JSONSchema;
                        minimum_tier: SandboxTier; blast_radius_tier: BlastRadiusTier;
                        required_secrets: List<SecretAllowlistEntry> }
  ```
- **Acceptance criteria:** `CHANGE:` add "`RawContractInput` is declared in this unit as the pre-validation registration-input record." Add "`SecretAllowlistEntry` is declared in this unit (carrier-ordering fix per Q-R3-3 option (a)); U-AS-22 consumes it, does not re-declare it." Other ACs `[unchanged]`.
- **Tests:** `CHANGE:` add `test_raw_contract_input_declared`, `test_secret_allowlist_entry_declared_at_u_as_07`.
- **Status:** Pattern B fixes + Q-R3-3 option (a) — **decided** (operator-ratified). Residual: the `SecretScope` field-set fix at U-AS-20 is deferred to R3.1 (§0.4) — it does not block this unit's carrier-ordering fix.

#### U-AS-08 — Implement `sandbox_tier(tool, call_site_context)` composition function

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
    deployment_surface  : DeploymentSurface     // imported from harness-core (via U-AS-04 / per-unit core edge)
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
  `CHANGE:` `COMPUTER_USE_FORCING` and `CODE_EXECUTION_FORCING` are **removed** from `AssignedTierReason` — they are not §15.2 members. Forced-tier results are reported via U-AS-02's `ForcedTierCause` enum (`COMPUTER_USE_BOUND`/`CODE_EXECUTION_BETA`); `SandboxTierCompositionResult` carries the forced-tier cause from there. `enum SandboxTierCompositionResult`, `interface FloorInterfaces`, `function sandbox_tier(...)` — `[unchanged]` except `FloorInterfaces` now references the in-unit `MCPServer` carrier.
- **Acceptance criteria:** `CHANGE:`
  - AC4 — re-state: "`AssignedTierReason` is the spec §15.2 audit-surface enum, exactly seven members `{contract_minimum, blast_radius_floor, mcp_server_trust_floor, operator_policy_floor, sandbox_tier_floor, persona_tier_floor, sub_agent_monotonic_ascension}` (SCREAMING_SNAKE rendering). It identifies the winning `max()` floor. Forced-tier outcomes are reported via the `ForcedTierCause` enum (U-AS-02), not via `AssignedTierReason`."
  - AC2 — re-state to route forced-tier through `ForcedTierResult`/`ForcedTierCause` (U-AS-02) rather than `AssignedTierReason` members.
  - Add: "`TaintState` and `MCPServer` are declared in this unit as the `CallSiteContext` field carriers."
  - ACs 1, 3, 5, 6, 7 `[unchanged]`.
- **Tests:** `CHANGE:` `test_sandbox_tier_composition_assigned_tier_reason_at_tie` re-grounded to the 7-member §15.2 set. Add `test_assigned_tier_reason_members_match_spec_15_2_verbatim`, `test_taint_state_declared`, `test_mcp_server_declared`.
- **Rollback boundary:** `CHANGE:` add — "Revert also removes the `TaintState` + `MCPServer` carriers; U-AS-14's `GateLevelFloorInterfaces` loses its `MCPServer` type."
- **Status:** Pattern A1 conformance + Pattern B carriers — **decided** (authority-chain-determinate).

> **Propagation (decided):** U-AS-16 acc #6 cites this unit's `AssignedTierReason` for `sandbox.policy.assigned_tier_reason`. The conformed 7-member set is what U-AS-16 references — U-AS-16 body preserved verbatim (§0.6).

#### U-AS-10 — Declare 12-cell deployment-matrix + cell-selection lookup function

`[Pattern A3 conformance — provider-class vocabulary. Pattern B — ToolContext consumed via U-AS-02 carrier.]`

- **Implements:** `[C-AS-09 §9.1, §9.3, §9.5]` `[unchanged]`.
- **Depends on:** `[U-AS-01, U-AS-02, U-AS-04, U-AS-11]` `[unchanged]` — `ToolContext` resolves via the existing `[U-AS-02]` edge (U-AS-02 now declares the carrier, §5.3).
- **Signatures:** `[unchanged]` — `lookup_cell_with_forcing(surface, blast_radius, ctx: ToolContext)` now has its `ToolContext` type in-cone via U-AS-02.
- **Acceptance criteria:** `CHANGE:` **AC2 re-stated against the actual `SandboxProviderClass` member set (spec §9.2 / U-AS-11):**
  - OLD (divergent): "...local-dev/self-hosted = LANGUAGE_LEVEL / **PROCESS_FS_OVERLAY** / CONTAINER / MICROVM_FIRECRACKER..."
  - NEW (conformed): "Per-cell `sandbox_tier` + `provider_class` match spec §9.1 row-by-row, naming `provider_class` values from the `SandboxProviderClass` enum (U-AS-11): `LANGUAGE_LEVEL`, `FILESYSTEM_OVERLAY_WORKTREE`, `PROCESS_ULIMIT_BUBBLEWRAP_SEATBELT`, `CONTAINER`, `MICROVM_FIRECRACKER`, `FULL_VM`. The non-existent `PROCESS_FS_OVERLAY` identifier is removed; the §9.1 cell content (tier + provider-class per `(DeploymentSurface, BlastRadiusTier)` cell) transcribes §9.1 using only these six carrier members."
  - Add AC: "`ToolContext` consumed by `lookup_cell_with_forcing` resolves to the U-AS-02 carrier (in-cone via the `[U-AS-02]` dependency)."
  - ACs 1, 3, 4, 5, 6 `[unchanged]`.
- **Tests:** `CHANGE:` the row-per-spec tests stay; any test asserting `PROCESS_FS_OVERLAY` is corrected to the actual member. Add `test_deployment_matrix_provider_classes_all_in_sandbox_provider_class_enum`.
- **Status:** Pattern A3 conformance — **decided**.

#### U-AS-14 — Implement 5-axis gate-level multiplicative tunable composition

`[Pattern B — MCPServer consumed in GateLevelFloorInterfaces; resolved via U-AS-08 carrier. Edge-add only.]`

- **Implements:** `[C-AS-12 §12.1, §12.2 reference, §12.5]` `[unchanged]`.
- **Depends on:** `CHANGE:` from `[U-AS-01, U-AS-04, U-AS-05, U-AS-06]` to **`[U-AS-01, U-AS-04, U-AS-05, U-AS-06, U-AS-08]`** — add the `[U-AS-08]` edge so `MCPServer` (declared at U-AS-08) is in-cone for `GateLevelFloorInterfaces.per_mcp_server_trust_floor : (Optional<MCPServer>) -> GateLevel`. Acyclic: U-AS-08 → {U-AS-01,02,04,05,06,07}; U-AS-14 → {…,U-AS-08}; no back-edge.
- **Signatures:** `[unchanged]` — `GateLevelFloorInterfaces` now has `MCPServer` in-cone. `GateLevel` 3-value enum transcribes §12.1 faithfully (Q1 clean-list — no change).
- **Acceptance criteria:** `CHANGE:` add "`MCPServer` consumed in `GateLevelFloorInterfaces` resolves to the U-AS-08 carrier (in-cone via the new `[U-AS-08]` dependency)." Others `[unchanged]`.
- **Tests:** `[unchanged]`.
- **Rollback boundary:** `[unchanged]`.
- **Status:** Pattern B dependency-graph completion — **decided**. (Edge-add + one AC note; no signature or AC-text conformance.)

#### U-AS-22 — Allowlist-intersection access control + MCP-passthrough prohibition (one micro-edit)

`[CONFORM unit — single Signatures-block micro-edit per Q-R3-3 option (a). All other elements preserved verbatim from v1.]`

- **Implements:** `[preserved verbatim]`.
- **Depends on:** `[preserved verbatim]` (U-AS-22 already `Depends on` both U-AS-07 and U-AS-20).
- **Signatures:** `CHANGE:` the v1 Signatures block declares `record SecretAllowlistEntry { name; scope }`. Under Q-R3-3 option (a) this declaration **moves to U-AS-07**. U-AS-22's block changes the declaration line to a **consumption reference** — `SecretAllowlistEntry` is consumed from U-AS-07, not declared here. The allowlist-intersection function and all other signatures `[preserved verbatim]`.
- **Acceptance criteria:** `CHANGE:` the acceptance criterion text that asserted U-AS-22 declares `SecretAllowlistEntry` is re-grounded to "`SecretAllowlistEntry` is consumed from U-AS-07 (carrier-ordering fix); U-AS-22 populates the access-control semantics against the already-declared shape." All other ACs `[preserved verbatim]`.
- **Tests:** `[preserved verbatim]`.
- **Rollback boundary:** `[preserved verbatim]`.
- **Status:** CONFORM unit, single micro-edit — **decided** (Q-R3-3 option (a) operator-ratified).

#### U-AS-28 — Declare eleven-primitive enumeration + per-primitive × workload-class adoption-depth matrix

`[Pattern A3 conformance — "kebab-case verbatim" claim. Pattern B carrier — AnchorCitation. WorkloadClass re-homed to U-CP-00 per Q-R3-5.]`

- **Implements:** `[C-AS-13 §13.1, §13.2]` `[unchanged]`.
- **Depends on:** `CHANGE:` add **`[U-CP-00 (cross-axis: core)]`** for `WorkloadClass` (Q-R3-5 re-home). The v1 cross-axis IS edges `[U-IS-01 (cross-axis: IS), U-IS-02 (cross-axis: IS)]` and `[U-AS-04]` are `[unchanged]`. Resulting set: `[U-AS-04, U-CP-00 (cross-axis: core), U-IS-01 (cross-axis: IS), U-IS-02 (cross-axis: IS)]`.
- **Signatures — Pattern B fix (decided):** declare the `AnchorCitation` carrier; **delete the local `enum WorkloadClass`** (Q-R3-5 re-home):
  ```
  record AnchorCitation {
    source_identifier : string
    confidence_tag    : ConfidenceTag       // [HIGH] / [MODERATE] / [SPECULATIVE]
  }
  const ANTHROPIC_PRIMITIVE_ANCHORS: Map<AnthropicPrimitive, AnchorCitation>
  ```
  `CHANGE:` the local `enum WorkloadClass { ... }` is **deleted** — `WorkloadClass` is consumed from `harness-core` (U-CP-00) per Q-R3-5. `enum AnthropicPrimitive` (11 members), `enum AdoptionDepth`, `record AdoptionDepthBinding` — `[unchanged]`.
- **Acceptance criteria:** `CHANGE:` **AC1 conformed (Pattern A3):**
  - OLD (divergent): "`AnthropicPrimitive` declares exactly 11 values per §13.1 verbatim **kebab-case**."
  - NEW (conformed): "`AnthropicPrimitive` declares exactly 11 members, one per the §13.1 prose name-table entry (`Skills system`, `MCP-as-code`, `Managed Agents`, `Per-role model binding`, …), mapped concept-name → SCREAMING_SNAKE member. §13.1 is a prose name table with no machine-identifier column; the member identifiers are a Python-stack naming-convention rendering (FM-D), not a byte-exact transcription of a spec string set. Closed enumeration; adding a 12th requires Class-2 ADR-D3 revision."
  - Add: "`AnchorCitation` is declared in this unit as the `ANTHROPIC_PRIMITIVE_ANCHORS` map value type."
  - Add: "`WorkloadClass` is consumed from `harness-core` (U-CP-00); U-AS-28 does not declare it. A local redeclaration is a defect."
  - ACs 2–8 `[unchanged]`.
- **Tests:** `CHANGE:` **delete `test_anthropic_primitive_identifier_strings_byte_exact_per_spec_13_1`** (no spec-side string set to compare to). Replace with `test_anthropic_primitive_cardinality_eleven_one_per_spec_13_1_concept`. Add `test_anchor_citation_declared`, `test_workload_class_consumed_from_harness_core`. Other tests `[unchanged]`.
- **Status:** Pattern A3 conformance + Pattern B carrier + Q-R3-5 `WorkloadClass` re-home — **decided** (operator-ratified).

#### U-AS-30 — Anthropic-API graceful-degradation per primitive + workload-binding-time selection contract

`[Pattern B carriers — ExtendedThinkingEffort, BatchApiCell, WorkloadManifestOverrides, Provider, ModelClass. WorkloadClass [U-CP-00] edge per R1 §3.2.]`

- **Implements:** `[C-AS-13 §13.5, §13.6]` `[unchanged]`.
- **Depends on:** `CHANGE:` from `[U-AS-04, U-AS-28, U-AS-29, U-IS-01 (cross-axis: IS), U-IS-02 (cross-axis: IS)]` to **`[U-AS-04, U-AS-28, U-AS-29, U-CP-00 (cross-axis: core), U-IS-01 (cross-axis: IS), U-IS-02 (cross-axis: IS)]`** — add the `[U-CP-00]` edge for `WorkloadClass` per `revision_R1_harness_core.md` §3.2.
- **Signatures — Pattern B fixes (decided), all declared in-unit:**
  ```
  enum ExtendedThinkingEffort { ... }        // §13.6 step 6 effort levels
  record BatchApiCell { ... }                // §13.6 step 7 batch-cell binding shape
  record WorkloadManifestOverrides { ... }   // §13.6 workload-manifest operator-override shape
  enum Provider { ANTHROPIC, BEDROCK, VERTEX, OPENAI, OLLAMA }   // §13.5 row-4 fallback families
  enum ModelClass { ... }                    // §13.5 row-4 fallback-pair model-class identifier
  ```
  `WorkloadBindingDecision`, `compose_workload_binding_decision`, `GRACEFUL_DEGRADATION_POLICY`, `MemoryToolStorageBackend` — `[unchanged]`; their `WorkloadClass` field now resolves to the `harness-core` (U-CP-00) type, not a local declaration.
- **Acceptance criteria:** `CHANGE:` add "`ExtendedThinkingEffort`, `BatchApiCell`, `WorkloadManifestOverrides`, `Provider`, `ModelClass` are each declared in this unit (Pattern B carriers — faithful factor-outs of §13.5/§13.6 per T2)." Add "`WorkloadClass` is consumed from `harness-core` (U-CP-00); U-AS-30 does not declare it." AC2 (`C6_CROSS_FAMILY_FALLBACK_CHAIN` 5-step `anthropic→bedrock→vertex→openai→ollama`) re-grounded to the in-unit `Provider` enum. ACs 1, 3–9 `[unchanged]`.
- **Tests:** `CHANGE:` add `test_extended_thinking_effort_declared`, `test_batch_api_cell_declared`, `test_workload_manifest_overrides_declared`, `test_provider_enum_five_families`, `test_model_class_declared`, `test_workload_class_consumed_from_harness_core`.
- **Status:** Pattern B carriers + `[U-CP-00]` edge — **decided**.

---

## §5.4 Auxiliary-type audit

### §5.4.1 (superseded)

> **`[SUPERSEDED — replaced by §5.4.2.]`** The v1 §5.4.1 auxiliary-type audit claimed "47 auxiliary typed entities … each verified as faithful factor-out" and v1 §5.5 reported "Missing dependencies ✅ NOT PRESENT" — yet 11 distinct types consumed at signature positions had no carrier. The self-audit had a blind spot exactly where the systemic Pattern B defect lived. v1 §5.4.1 is superseded by the exhaustive, mechanical §5.4.2 below. Action item A-4 (§0.7) tracks the mechanical replacement and the zero-(U) verification run.

### §5.4.2 Exhaustive auxiliary-type audit (permanent plan section)

This is the structural fix for Pattern B. It enumerates every type appearing at a typed signature position with its declaring carrier and a declaring-vs-consuming position record. A type with no carrier row is a defect, surfaced by the audit, not discovered later by adversarial review.

#### §5.4.2.1 Audit method (mandatory, mechanical)

1. **Enumerate.** For every unit, list every identifier at a typed signature position — record/enum field types, function parameter types, function return types, `const` value types, map key/value types.
2. **Classify each** into exactly one of four classes:
   - **(C) Carrier-declared** — declared by a `record`/`enum`/`opaque type`/`newtype` in some unit's Signatures block.
   - **(X) Cross-axis import** — arrives via a declared `(cross-axis: IS)` or `(cross-axis: core)` edge.
   - **(S) Stack/SDK primitive** — `Target_Stack_Commitment` adoption (`JSONSchema`, OTel-SDK span/attribute primitives, `str`/`int`/`bool`).
   - **(U) Undeclared** — none of the above. **Every (U) is a defect.** The audit must return zero (U) rows.
3. **In-cone check.** For every (C) row, verify the declaring carrier is inside the consuming unit's `Depends on` transitive cone. A carrier out-of-cone is a defect.
4. **Carrier-ordering check.** For every (C) row, verify the carrier unit is not topologically *downstream* of a consumer. A downstream carrier is a defect (the U-AS-07/U-AS-22 `SecretAllowlistEntry` shape).

#### §5.4.2.2 Audit table (post-R3)

| Type | Class | Carrier unit | Consuming units | In-cone? | Note |
|---|---|---|---|---|---|
| `SandboxTier` | C | U-AS-01 | most AS units | ✓ | foundational L0 |
| `BlastRadiusTier`, `MechanismClass`, `SandboxTierMetadata` | C | U-AS-01 | various | ✓ | |
| `ToolContext` | C | **U-AS-02** | U-AS-02, U-AS-10 | ✓ | R3 Pattern B fix |
| `ForcedTierCause`, `ForcedTierResult` | C | U-AS-02 | U-AS-08 | ✓ | |
| `SandboxFailClass` + metadata enums | C | U-AS-03 | U-AS-16, U-AS-17 | ✓ | |
| `MCPTransport` | C | U-AS-04 | composition units | ✓ | stays AS-owned |
| `DeploymentSurface`, `PersonaTier` | X (core) | U-CORE-01 | U-AS-04/08/10/12/30/… | ✓ | R3 — imported from `harness-core`; explicit per-unit core edges (Q-R3-6) |
| `ToolMetadata` | C | **U-AS-06** | U-AS-06 | ✓ | R3 Pattern B fix — declaration deferred to R3.1 (rides §9 decision) |
| `SandboxTierFloorResult`, `MCPTrustLevel` | C | U-AS-06 | U-AS-08, U-AS-09, U-AS-13 | ✓ | |
| `RawContractInput` | C | **U-AS-07** | U-AS-07 | ✓ | R3 Pattern B fix |
| `ToolContract`, `ContractValidationResult` | C | U-AS-07 | U-AS-08, U-AS-14, U-AS-22 | ✓ | |
| `SecretAllowlistEntry` | C | **U-AS-07** (moved from U-AS-22) | U-AS-07, U-AS-22 | ✓ | R3 carrier-ordering fix (Q-R3-3 option (a)) |
| `TaintState`, `MCPServer` | C | **U-AS-08** | U-AS-08, U-AS-14 | ✓ | R3 Pattern B fix; U-AS-14 gains `[U-AS-08]` edge |
| `CallSiteContext`, `FloorInterfaces`, `SandboxTierCompositionResult`, `AssignedTierReason` | C | U-AS-08 | U-AS-16 | ✓ | `AssignedTierReason` conformed to §15.2 |
| `SandboxProviderClass` | C | U-AS-11 | U-AS-10, U-AS-16 | ✓ | U-AS-10 AC2 conformed to these members |
| `SecretRef`, `SecretScope` | C | U-AS-20 | U-AS-07/22/24/26/27/30 | ✓ | `SecretScope` field-set fix deferred to R3.1 (type exists; ellipsis body) |
| `AnchorCitation` | C | **U-AS-28** | U-AS-28 | ✓ | R3 Pattern B fix |
| `WorkloadClass` | X (core) | U-CP-00 | U-AS-28/29/30 | ✓ | R3 — `[U-CP-00]` edges (Q-R3-5 re-home) |
| `ExtendedThinkingEffort`, `BatchApiCell`, `WorkloadManifestOverrides`, `Provider`, `ModelClass` | C | **U-AS-30** | U-AS-30 | ✓ | R3 Pattern B fix |
| `UnitId` | X (core) | U-CORE-01 | U-AS-33 | ✓ | R3 — `[U-CORE-01]` edge |
| `StateLedgerEntry`, `IdempotencyKey`, `Actor`, `FilesystemPathContract`, … | X (IS) | IS plan U-IS-01/02/07/08/09/10/11/12 | U-AS-19/25/26/27/28/29/30 | ✓ | cross-axis IS edges; A-3 re-cite check |
| `JSONSchema`, `SpanId`, `MonotonicTimestamp`, `AttributeValue`, `AttributeValueType`, `Cardinality` | S | — | various | n/a | stack/OTel-SDK primitives — no carrier needed |
| **(U) rows** | — | — | — | — | **ZERO target — R3 declares a carrier for all 11 former (U) types. `ToolMetadata` is the one carrier whose *declaration* is deferred to R3.1 (it rides the §9 spec decision); its carrier *unit* (U-AS-06) is fixed. Running the audit to a confirmed zero-(U) state is action item A-4 (§0.7).** |

#### §5.4.2.3 Standing discipline clause

The §5.4.2 audit is **re-run at every AS-plan revision pass**. Any new unit or any new typed signature position must appear in the table with a (C)/(X)/(S) class — never (U). A revision pass that adds a type without a carrier row fails its own coherence pass. This converts the Pattern B defect from "found by adversarial review after the fact" to "blocked at authoring".

---

## §7 Dependency-graph delta

The v1 §3 dependency graph takes the following deltas. The acyclic invariant is re-verified at §7.4.

### §7.1 New / changed edges

Per Q-R3-6 (operator-ratified): explicit per-unit `(cross-axis: core)` edges for every `harness-core` consumer, not transitive resolution.

| Unit | Edge change | Reason |
|---|---|---|
| U-AS-04 | `Depends on` `(none)` → `[U-CORE-01 (cross-axis: core)]` | `harness-core` import of `DeploymentSurface`/`PersonaTier` (§5.3) |
| U-AS-07 | `Depends on` `[U-AS-01]` → `[U-AS-01, U-AS-20]` | `SecretScope` in-cone for `SecretAllowlistEntry.scope` (Q-R3-3 option (a), operator-ratified) |
| U-AS-14 | `Depends on` add `[U-AS-08]` → `[U-AS-01, U-AS-04, U-AS-05, U-AS-06, U-AS-08]` | `MCPServer` carrier in-cone for `GateLevelFloorInterfaces` |
| U-AS-30 | `Depends on` add `[U-CP-00 (cross-axis: core)]` | `WorkloadClass` carrier (R1 §3.2 hand-off) |
| U-AS-33 | `Depends on` add `[U-CORE-01 (cross-axis: core)]` | `UnitId` identity alias from `harness-core` |
| U-AS-28 | `Depends on` add `[U-CP-00 (cross-axis: core)]` | `WorkloadClass` re-home (Q-R3-5, operator-ratified) |
| U-AS-29 | `Depends on` add `[U-CP-00 (cross-axis: core)]` | `WorkloadClass` consumer (Q-R3-5); **graph-only delta — U-AS-29 body preserved verbatim** |
| U-AS-08, U-AS-10, U-AS-12 (and any other `DeploymentSurface`/`PersonaTier` consumer) | `Depends on` add `[U-CORE-01 (cross-axis: core)]` | Q-R3-6 explicit per-unit core edge — `DeploymentSurface`/`PersonaTier` consumed via `CallSiteContext` / matrix-key / `override_scope`. Graph-only delta for any unit not otherwise body-revised. |

> **Q-R3-6 explicit-edge note.** v1 resolved `DeploymentSurface`/`PersonaTier`/`WorkloadClass` transitively through U-AS-04's re-export. The operator ratified explicit per-unit core edges for reviewability. Every AS unit that consumes a `harness-core` type carries its own `[U-CORE-01]` or `[U-CP-00]` edge. For body-revised units (U-AS-08) the edge is shown in §5.3 commentary; for preserved-verbatim units (U-AS-12 deferred body, U-AS-29 CLEARED) the edge is a **graph-only delta recorded here** — the unit body is not edited to add the edge line, the §3 dependency-graph section carries it. The minimum enumerated set is U-AS-04/07/08/10/12/14/28/29/30/33; the operator/executor extends per any further `DeploymentSurface`/`PersonaTier` consumer surfaced at the coherence re-run.

### §7.2 `harness-core` import edges (R1-pattern)

Per `revision_R1_harness_core.md` §3, a `harness-core` import is flagged `(cross-axis: core)` but is an *import* edge, not an outbound CXA edge — it does not affect the AS→IS edge count of 13 (CXA v2.1 §2.3.1).

### §7.3 Cross-axis AS→IS edge re-cite (FLAGGED — A-3, not performed here)

The AS plan §3.4 cites IS plan units via `(cross-axis: IS)` edges. The R2 IS revision produced `Implementation_Plan_Information_Substrate_v2_3.md` (proposed). Per SKILL.md §9 use-latest-version discipline, the AS→IS citations should bump from IS plan v1 to v2.3 and each cited U-IS-NN re-verified. **This is action item A-3 (§0.7) — a deferred mechanical re-cite, not performed in this pass.** §3.4's IS-plan citation is left at the v1 value pending A-3.

### §7.4 Acyclic invariant re-verification

All new edges are either (a) inbound to a Level-0 source node (`[U-CORE-01]`, `[U-CP-00]` — both pure source nodes with no outbound deps; inbound-only edges to a source cannot create a cycle), or (b) `[U-AS-08]`→U-AS-14 and `[U-AS-20]`→U-AS-07 — both forward edges in the existing topological order (U-AS-08 < U-AS-14; U-AS-20 at L1 < U-AS-07 at L1, and U-AS-07 does not transitively reach U-AS-20 — U-AS-20 `Depends on [U-AS-01]` only). **No cycle introduced. The graph remains a DAG.** U-AS-04 moves from a pure L0 source to an L0 node with one inbound-from-core import. Kahn verification still consumes all 33 AS units.

---

## §8 Coverage-matrix delta

The v1 §4.1 contract-section → unit coverage matrix takes these deltas. **No contract loses coverage; no coverage gap is introduced.**

| Contract section | v1 coverage | v1.1 coverage | Delta reason |
|---|---|---|---|
| C-AS-09 §9.1 (deployment-surface enum axis) | U-AS-04 (declares `DeploymentSurface`) + U-AS-10 | **U-CORE-01** (enum axis) + U-AS-10 (12-cell matrix) | U-AS-04 no longer declares the enum; U-CORE-01 covers the deployment-surface enum axis. U-AS-04's §9.1 mark moves to U-CORE-01. |
| C-AS-09 §9.4 (persona-tier ladder / override scope) | U-AS-04 (declares `PersonaTier`) + U-AS-12 | **U-CORE-01** (persona-tier enum) + U-AS-12 (override scope) | U-AS-04's `PersonaTier` declaration moves to U-CORE-01; U-AS-12 still covers §9.4 override-scope. |
| C-AS-12 §12.2 (override-scope reference) | U-AS-04 (forward use) + U-AS-12 + U-AS-14 | U-AS-12 + U-AS-14 | U-AS-04's forward-use citation dropped (no longer declares the discriminator enums). §12.2 stays covered — no gap. |
| C-AS-10 §10.1 (MCP transport-level set) | U-AS-04 (forward use) + U-AS-13 | **U-AS-04** (declares `MCPTransport`) + U-AS-13 | U-AS-04's §10.1 citation strengthens from "forward use" to a declaring citation. |
| C-AS-02 §2.3 | U-AS-04 (forward use) + U-AS-06 | U-AS-06 (deferred to R3.1) | U-AS-04's §2.3 forward-use citation dropped. U-AS-06 covers §2.3; finalization rides the §9 spec decision (R3.1). |
| C-AS-13 §13.1 | U-AS-28 | U-AS-28 | No coverage change — only AC text + the `AnthropicPrimitive` claim re-grounded. |
| C-AS-15 §15.2 | U-AS-08 (`AssignedTierReason`) + U-AS-16 | U-AS-08 (conformed enum) + U-AS-16 | No coverage change — U-AS-08's `AssignedTierReason` now transcribes §15.2 verbatim. |

> **Coverage-matrix cross-plan note.** The C-AS-09 §9.1/§9.4 marks moving to U-CORE-01 means the `harness-core` plan's coverage matrix (`Implementation_Plan_Harness_Core_v1_0.md` §4) already carries those rows (R1 filed them). A contract covered by multiple units across plans is permitted (SKILL.md §4.2). The AS plan v1.1 retains the contract row, attributing the enum-axis coverage to U-CORE-01 with this in-plan cross-reference note — it does not silently drop the row.

---

## §9 Filing footer

| Field | Value |
|---|---|
| Artifact | `Implementation_Plan_Action_Surface_v1_1.md` |
| Role | `implementation-planner`, revision-pass sub-mode (SKILL.md §8) |
| Authored | 2026-05-15, Phase 7 sub-phase 7b — revision pass R3 applied (third of the R1–R5 carrier-map absorption sequence) |
| Predecessor | `Implementation_Plan_Action_Surface_v1.md` (v1, 2026-05-14) — verbatim base for the 20 preserved units + the 4 deferred units' carried bodies |
| Source | `.harness/revision_R3_as_plan.md` (operator-ratified R3 revision proposal, 2026-05-15) + the operator ratification decisions at §0.2 |
| Scope | AS plan v1 → v1.1 — Pattern A verbatim conformance + Pattern B carrier declaration + U-AS-04 declaration-site conversion + U-AS-02 retrospective flag + CONFORM propagation + permanent §5.4.2 exhaustive auxiliary-type audit. 9 determinate units revised; 4 conditional units deferred to R3.1; 20 units preserved verbatim. |
| Deferred | U-AS-06, U-AS-09, U-AS-12, U-AS-20 — finalized at a follow-on **R3.1 micro-pass** (U-AS-06/09 on the Q-R3-1 `spec-writer` C-AS-02/§11.1 reconciliation; U-AS-12 on Q-R3-4 Reading A/B; U-AS-20 on Q-R3-2 R1/R2 direction + the `SecretScope` field-set fix). |
| Action items | A-1 (U-AS-04 landed-source re-check), A-2 (U-AS-02 landed-source retrospective), A-3 (AS→IS edge re-cite to IS plan v2.3), A-4 (§5.4.1→§5.4.2 replacement + zero-(U) verification) — all FLAGGED at §0.7; deferred coding-lane / mechanical actions, not performed in this pass. |
| Status | **Proposed** — pending P6-CK clearance. |
| Successor | R3.1 micro-pass (finalizes the 4 deferred units); R4 (CP) / R5 (OD) follow per the carrier-map ordering. |
| HARD WALL attested | This pass wrote only `design-substrate/Implementation_Plan_Action_Surface_v1_1.md`. No other `design-substrate/` file, no `CLAUDE.md`, no R3 proposal / audit / spec / source edited. No git commit. |

*End of `Implementation_Plan_Action_Surface_v1_1.md` (v1.1). Delta over v1; v1 is the verbatim base for all `[preserved verbatim]` pointers.*
