# Implementation Plan — Action Surface (v1.2)

## Status block

| Field | Value |
|---|---|
| Artifact | `Implementation_Plan_Action_Surface_v1_2.md` |
| Status | **Proposed** (v1.2 delta over v1.1; pending P6-CK clearance) |
| Date | 2026-05-15 |
| Phase | 7 sub-phase 7b — revision pass **R3.1** (the AS micro-pass; finalizes the 4 units R3 deferred) |
| Skill | `implementation-planner` SKILL.md §8 revision-pass sub-mode |
| Axis | Action Surface (AS) |
| Predecessor | `Implementation_Plan_Action_Surface_v1_1.md` (v1.1, 2026-05-15) |
| Source-set (R3.1) | `.harness/revision_R3_as_plan.md` §5 (R3 conditional bodies for U-AS-06/09/12/20); `.harness/s1_c_as_02_reconciliation.md` (operator-ratified C-AS-02 `sandbox_tier_floor` reconciliation recommendation); `design-substrate/Spec_Action_Surface_v1.md` (now spec v1.2 — reconciled 5-arg `sandbox_tier_floor`); `design-substrate/Implementation_Plan_Action_Surface_v1_1.md` (verbatim base for all non-finalized units) |
| Plan shape | Axis-led (unchanged from v1 / v1.1) |
| Sub-mode | Revision-pass (v1.1 → v1.2 delta; predecessor v1.1 is the verbatim base) |

> **Versioning note.** This artifact is **AS plan v1.1 → v1.2**. "AS spec v1.2" (`Spec_Action_Surface_v1.md` v1.2) is the reconciled specification cited below; "v1.2" in this document means the plan version unless prefixed `spec`.

---

## §0 Change-note

### §0.1 Trigger and scope

v1.2 is the **R3.1 micro-pass** — a narrowly-scoped delta over v1.1 that finalizes the **4 units R3 deferred** (U-AS-06, U-AS-09, U-AS-12, U-AS-20). v1.1 carried each of these with its v1 body verbatim plus a `[DEFERRED to R3.1]` marker, because each was conditional on a decision not yet made at R3-application time. All four decisions are now made (operator-ratified 2026-05-15, §0.2). v1.2 removes the deferral markers and applies the ratified bodies.

v1.2 changes **only the 4 finalized units** plus their dependency-graph / coverage-matrix / §5.4.2-audit deltas. **All 29 other units are `[preserved verbatim]` from v1.1** — the 9 R3-revised determinate units and the 20 R3-preserved units. v1.1 is canonical for every non-finalized unit; v1.2 does not restate them.

### §0.2 Operator ratification decisions (2026-05-15)

The four decisions that close the R3.1 conditionals:

| Unit | R3 conditional | Ratified decision applied in v1.2 |
|---|---|---|
| **U-AS-06** | Q-R3-1 — C-AS-02 `sandbox_tier_floor` spec gap (Option G-1 explicit-arg vs G-2 carrier-borne) | **G-1 / 5-arg signature.** The `systems-architect` S1 reconciliation (`.harness/s1_c_as_02_reconciliation.md`) was operator-ratified; `spec-writer` applied it; AS spec is now **v1.2** with the canonical `sandbox_tier_floor(tool, deployment_surface, blast_radius_tier, mcp_transport, mcp_server) -> SandboxTier \| REFUSE` signature (C-AS-02 §2.2/§2.3/§10.2/§11.1/§12.1). The C-AS-02 spec gap is **RESOLVED** — no longer conditional. U-AS-06 conforms its body to the now-canonical 5-arg signature. |
| **U-AS-09** | Q-R3-1 — folds into the same C-AS-02/§11.1 reconciliation | **G-1 / conform to spec §11.1.** `sub_agent_sandbox_tier`'s outer signature is the spec §11.1 6-param form `(parent_sandbox_tier, tool, blast_radius, mcp_transport, deployment_surface, mcp_server)`; its inner `sandbox_tier_floor` call is the canonical 5-arg form. The outer signature gains `tool` and `mcp_server` so it has them to thread through. |
| **U-AS-12** | Q-R3-4 — Reading A (AC-text fix) vs Reading B (signature gains `cell_compliance_status`) | **Reading A.** "Non-compliance cells" = "any cell" for the solo-developer persona. This is an **acceptance-criteria wording fix only** — no signature change, no new input, function body unchanged. AC2 is revised to remove the false-divergence framing. |
| **U-AS-20** | Q-R3-2 — Option R1 (3-param spec form) vs Option R2 (2-param + context object) | **R1 direction.** `fetch_secret` takes the sandbox tier as a **plain third argument** — `fetch_secret(name, scope, tier) -> SecretRef`. NOT a bundled context object. The `SecretScope` ellipsis-body field set (the residual R3 §7.1 / v1.1 §0.4 flagged) is also fixed — explicit field set, serialization still deferred per spec §5.4. |

### §0.3 The 4 finalized units (full bodies in §5.2)

| Unit | What R3.1 finalizes | Signature/body change vs the v1.1-carried v1 body |
|---|---|---|
| **U-AS-06** | `sandbox_tier_floor` lookup table | `sandbox_tier_floor` 5th argument changes from `mcp_trust_level: Optional<MCPTrustLevel>` to `mcp_server: Optional<MCPServer>`; the `MCPTrustLevel` enum is **removed** (trust level is read from `MCPServer`, not threaded as a scalar); `MCPServer` is **re-homed to U-AS-06 as its declaring carrier** (see §0.4); `ToolMetadata` Pattern B carrier declared; `Implements` citation bumped to spec v1.2. |
| **U-AS-09** | `sub_agent_sandbox_tier` monotonic-ascension | Outer signature conformed to spec §11.1 v1.2 6-param form (gains `tool`, `mcp_server`; drops `mcp_trust_level`); inner `sandbox_tier_floor` call conformed to the 5-arg form; `Implements` citation bumped to spec v1.2. |
| **U-AS-12** | `override_scope` per persona-tier | AC2 text re-stated (Reading A) — no signature, input, or body change. `Implements` citation unchanged. |
| **U-AS-20** | `fetch_secret` signature + `SecretRef` + `SecretScope` | `fetch_secret` finalized at the 3-param `(name, scope, tier)` R1 form; `SecretScope` ellipsis body replaced with an explicit field set (serialization deferred per §5.4); AC1 re-stated to drop the internal contradiction. |

### §0.4 `MCPServer` carrier re-home (graph decision)

The reconciled 5-arg `sandbox_tier_floor` takes `mcp_server: Optional<MCPServer>`. v1.1 §5.4.2 declared the `MCPServer` carrier at **U-AS-08**. But U-AS-08 `Depends on [..., U-AS-06, ...]` — U-AS-06 is **upstream** of U-AS-08. If `MCPServer` stayed at U-AS-08, U-AS-06 (which now consumes `MCPServer` at its signature) would require a `[U-AS-08]` edge, creating a **cycle** (U-AS-06 → U-AS-08 → U-AS-06).

**Resolution: `MCPServer` is re-homed to U-AS-06 as its declaring carrier.** U-AS-06 is the primary consumer of `MCPServer` (it is the `sandbox_tier_floor` argument carrier). U-AS-08 then consumes `MCPServer` via its **existing** `[U-AS-06]` edge — in-cone, no new edge. U-AS-14 consumes `MCPServer` via its v1.1-added `[U-AS-08]` edge (still valid; `MCPServer` is transitively in-cone through U-AS-06 → U-AS-08 → U-AS-14). The §5.4.2 audit row for `MCPServer` is updated (§5.4 below). No cycle; the graph remains a DAG (§7.4).

> `TaintState` (the other v1.1 §5.4.2 U-AS-08-declared Pattern B carrier) stays at U-AS-08 — it is not consumed by `sandbox_tier_floor` and has no carrier-ordering defect. Only `MCPServer` re-homes.

### §0.5 Sections preserved verbatim (29 units)

Every unit other than the 4 finalized is `[preserved verbatim]` from v1.1. v1.1 is canonical for them; v1.2 lists them as pointers (§5.1), not restated.

- **9 R3-revised determinate units (v1.1 §5.3 canonical):** U-AS-02, U-AS-04, U-AS-07, U-AS-08, U-AS-10, U-AS-14, U-AS-22, U-AS-28, U-AS-30.
- **20 R3-preserved units (v1.1 §5.1 canonical — themselves verbatim from v1 §2):** the 18 CLEARED units U-AS-01, U-AS-03, U-AS-05, U-AS-11, U-AS-13, U-AS-15, U-AS-17, U-AS-18, U-AS-19, U-AS-21, U-AS-23, U-AS-24, U-AS-25, U-AS-26, U-AS-27, U-AS-29, U-AS-31, U-AS-32, plus the 2 verbatim CONFORM units U-AS-16, U-AS-33.

> **U-AS-08 propagation (no body edit).** U-AS-08's v1.1 body declared `MCPServer`. Under §0.4 the `MCPServer` declaration moves to U-AS-06; U-AS-08 now *consumes* `MCPServer` (in-cone via the existing `[U-AS-06]` edge) rather than declaring it. This is a **§5.4.2-audit and §0.4-recorded carrier-home delta**, identical in pattern to the v1.1 `SecretAllowlistEntry` U-AS-22→U-AS-07 carrier-ordering fix: the consuming reference in U-AS-08's `CallSiteContext` / `FloorInterfaces` is unchanged, only the declaring carrier moves. U-AS-08's body remains `[preserved verbatim]` from v1.1 §5.3; the carrier-home change is recorded here and at §5.4, not by editing U-AS-08's body. (Pattern precedent: v1.1 §0.6 / §5.4.2 handled `SecretAllowlistEntry` the same way.)

### §0.6 R3-application action items (carried forward + one new)

v1.1's action items A-1..A-4 are **carried forward unchanged** — they are deferred coding-lane / mechanical actions, not in R3.1 scope. R3.1 adds **A-5**.

| ID | Action | Locus | Status |
|---|---|---|---|
| **A-1** | **U-AS-04 landed-source re-check.** Verify the landed source deletes the local `DeploymentSurface`/`PersonaTier` definitions and re-points to the `harness-core` import. Source-vs-plan reconciliation. | landed `harness-as/` source | FLAGGED — coding-lane (carried from v1.1) |
| **A-2** | **U-AS-02 landed-source retrospective.** Verify the landed `ToolContext` materialization is field-complete (`computer_use_bound` + `code_execution_beta_invoked`) and shape-consistent with the U-AS-02 §5 carrier. §2.7.6 Class 3 (informational). | landed `harness-as/` source | FLAGGED — coding-lane (carried from v1.1) |
| **A-3** | **AS→IS edge version re-cite.** Bump the AS plan §3.4 cross-axis IS-plan citation to the latest filed IS plan; verify each cited U-IS-NN still exists with the same export seam. Mechanical re-cite per SKILL.md §9. | AS plan §3.4 | FLAGGED — mechanical (carried from v1.1) |
| **A-4** | **§5.4.1 → §5.4.2 audit replacement.** The §5.4.2 table is authored (v1.1 + this v1.2 delta); running it to a confirmed zero-(U) state against the landed/revised type set is the deferred verification step. | AS plan §5.4 | FLAGGED — partly authored; zero-(U) verification deferred (carried from v1.1) |
| **A-5** | **C-AS-05 §5.1 spec revision to the 3-param `fetch_secret` form.** The operator ratified the R1 direction (`fetch_secret(name, scope, tier) -> SecretRef`, 2026-05-15). AS spec v1.2 §5.1 still reads the 2-param `fetch_secret(name, scope) -> SecretRef` form (C-AS-05 / §5 is in the spec v1.2 preserved-verbatim set — the C-AS-02 spec-writer pass did not touch C-AS-05). A `spec-writer` pass revising C-AS-05 §5.1 + the C-AS-05 contract title to the 3-param form is **owed** — analogous to the C-AS-02/ADR-D2 reconciliation already landed. U-AS-20's body in v1.2 applies R1 per the operator ratification; its `Implements` citation bumps to the post-fix C-AS-05 version when the spec-writer pass lands. | AS plan U-AS-20 / `design-substrate/Spec_Action_Surface_v1.md` C-AS-05 §5.1 | **NEW — FLAGGED**; spec-writer pass owed, not performed in this pass |

### §0.7 Coverage-matrix and dependency-graph delta summary

- **Coverage matrix:** no contract loses coverage. C-AS-02 §2.3's "deferred to R3.1" qualifier is removed — U-AS-06 now fully covers §2.3 against the reconciled spec v1.2. C-AS-11 §11.1–§11.5 — U-AS-09 finalized, coverage unchanged. C-AS-05 §5.1/§5.2/§5.4 — U-AS-20 finalized; §5.1 carries the A-5 caveat. C-AS-09 §9.4 — U-AS-12 finalized (AC-text only; coverage unchanged). Full delta at §8.
- **Dependency graph:** **no edge added or removed.** The only graph-relevant change is the `MCPServer` carrier-home move U-AS-08 → U-AS-06 (§0.4), which is consumed via *existing* edges and introduces no new edge. Acyclic invariant re-verified (§7.4). Full delta at §7.

---

## §5 Revised unit bodies

### §5.1 Preserved-verbatim units (pointers)

The 29 non-finalized unit bodies are `[preserved verbatim]` — **v1.1 is canonical**:

- **9 R3-revised determinate units** — consult `Implementation_Plan_Action_Surface_v1_1.md` §5.3: U-AS-02, U-AS-04, U-AS-07, U-AS-08, U-AS-10, U-AS-14, U-AS-22, U-AS-28, U-AS-30. *(U-AS-08: body verbatim from v1.1 §5.3; the `MCPServer` carrier-home move per §0.4/§0.5/§5.4 is a recorded carrier-home delta, not a body edit.)*
- **20 R3-preserved units** — consult `Implementation_Plan_Action_Surface_v1_1.md` §5.1 (themselves verbatim from `Implementation_Plan_Action_Surface_v1.md` §2): U-AS-01, U-AS-03, U-AS-05, U-AS-11, U-AS-13, U-AS-15, U-AS-16, U-AS-17, U-AS-18, U-AS-19, U-AS-21, U-AS-23, U-AS-24, U-AS-25, U-AS-26, U-AS-27, U-AS-29, U-AS-31, U-AS-32, U-AS-33.

### §5.2 Finalized units (R3.1 — full bodies, deferral markers removed)

The 4 units below carry their **final bodies**. The v1.1 `[DEFERRED to R3.1]` markers are removed; the ratified decisions (§0.2) are applied.

#### U-AS-06 — Implement `sandbox_tier_floor` lookup table

`[FINALIZED at R3.1. Q-R3-1 resolved — G-1 / 5-arg signature; AS spec v1.2 canonical. Pattern B carrier `ToolMetadata` declared; `MCPServer` carrier re-homed here (§0.4).]`

**Implements:** [C-AS-02 §2.3] *(spec v1.2 — the reconciled `sandbox_tier_floor` lookup table; row→argument keying contract note per spec §2.3)*

**Depends on:** [U-AS-01, U-AS-04, U-AS-05]

**Inputs:** `ToolMetadata` (carries `is_deterministic_inhouse`, `forces_computer_use`, `forces_code_execution` — the §2.3 rows 1–2 / 7 discriminators); `DeploymentSurface`; `BlastRadiusTier`; `MCPTransport` (Optional — the §2.3 row 3 discriminator); `MCPServer` (Optional — carries the remote-MCP trust level keying §2.3 rows 4–6).

**Files affected:** AS-axis sandbox-tier-floor lookup module (logical: `sandbox-tier-floor-lookup`); MCP-server identity/trust type declaration (logical: `mcp-server-type-declaration`).

**Signatures:**

```
record ToolMetadata {                            // Pattern B carrier — the §2.3 row-1/2/7 discriminators
  is_deterministic_inhouse : bool
  forces_computer_use      : bool
  forces_code_execution    : bool
}

record MCPServer { ... }                         // MCP-server identity/trust shape (spec §10 MCP transport/trust
                                                 // surface; spec §2.3 rows 4–6 read the remote-MCP trust level
                                                 // from this object — re-homed here per §0.4; carries a 4-valued
                                                 // trust level: Level 0 refuse-remote / 1 signed-pinned /
                                                 // 2 sandbox-all / 3 allow-with-audit, per spec §10.3)

enum SandboxTierFloorResult {
  RESOLVED(SandboxTier),
  REFUSE
}

function sandbox_tier_floor(
  tool: ToolMetadata,
  deployment_surface: DeploymentSurface,
  blast_radius_tier: BlastRadiusTier,
  mcp_transport: Optional<MCPTransport>,
  mcp_server: Optional<MCPServer>
) -> SandboxTierFloorResult
```

> **Signature note.** This is the AS-spec-v1.2 canonical 5-argument form `sandbox_tier_floor(tool, deployment_surface, blast_radius_tier, mcp_transport, mcp_server) -> SandboxTier | REFUSE` (C-AS-02 §2.2/§2.3/§10.2/§11.1/§12.1, reconciled per the operator-ratified `s1_c_as_02_reconciliation.md`). It supersedes the v1-body 5th argument `mcp_trust_level: Optional<MCPTrustLevel>`: trust level is **read from the `mcp_server` argument**, not threaded as a standalone scalar — G-1 explicit-argument resolution, for parity with the sibling `mcp_server_trust_tier_floor(call_site_context.mcp_server)` floor in the §2.2 `max()` composition. The v1-body `enum MCPTrustLevel { L0_REFUSE_REMOTE, L1_SIGNED_PINNED, L2_SANDBOX_ALL, L3_ALLOW_WITH_AUDIT }` is **removed** from this unit's Signatures block — the four-valued trust level is now an internal field of `MCPServer`, read by the §2.3 rows 4–6 lookup.

**Acceptance criteria:**
1. Lookup implements the ten C-AS-02 §2.3 rows (computer-use force, code-execution force, STDIO MCP, remote MCP L0/L1/L2/L3, read-only deterministic, local-mutation, external-reversible, external-irreversible). Per the spec §2.3 row→argument keying contract note: rows 1–2 are keyed on the `tool` argument; row 3 on `mcp_transport`; rows 4–6 on the remote-MCP trust level read from the `mcp_server` argument; rows 7–10 on `blast_radius_tier`.
2. Row precedence: forcing conditions → MCP-transport / MCP-server-trust rows → blast-radius default rows.
3. REFUSE sentinel (the remote-MCP Level-0 row) is structurally distinct from any `SandboxTier` value — `SandboxTierFloorResult.REFUSE`.
4. The remote-MCP Level-0 row's egress allow-listing requirement is a downstream MCP registration concern.
5. Rows 7–10 reference `blast_radius_floor` from U-AS-05.
6. Alignment between this table and C-AS-10 §10.1 verified by integration test at U-AS-13 (Cluster 3).
7. `ToolMetadata` is declared in this unit carrying `is_deterministic_inhouse` / `forces_computer_use` / `forces_code_execution` — the §2.3 row-1/2/7 discriminators.
8. `MCPServer` is declared in this unit (carrier re-home per §0.4) as the §2.3 rows-4–6 trust-level carrier and the `sandbox_tier_floor` `mcp_server` argument type.

**Tests:** `test_sandbox_tier_floor_computer_use_returns_tier_4`, `test_sandbox_tier_floor_code_execution_returns_tier_4`, `test_sandbox_tier_floor_stdio_with_read_only_returns_tier_3`, `test_sandbox_tier_floor_stdio_with_external_irreversible_returns_tier_4`, `test_sandbox_tier_floor_remote_l0_returns_refuse`, `test_sandbox_tier_floor_remote_l2_returns_tier_4`, `test_sandbox_tier_floor_remote_l1_returns_blast_radius_floor`, `test_sandbox_tier_floor_remote_l3_returns_blast_radius_floor`, `test_sandbox_tier_floor_read_only_deterministic_returns_tier_1`, `test_sandbox_tier_floor_local_mutation_returns_tier_2`, `test_sandbox_tier_floor_external_reversible_returns_tier_3`, `test_sandbox_tier_floor_external_irreversible_returns_tier_4`, `test_sandbox_tier_floor_forcing_precedence_over_blast_radius`, `test_sandbox_tier_floor_refuse_is_distinct_from_tier_values`, `test_tool_metadata_record_three_fields`, `test_mcp_server_declared_at_u_as_06`, `test_sandbox_tier_floor_signature_is_five_arg`.

> Trust-level row tests (`remote_l0/l1/l2/l3`) construct an `MCPServer` carrying the relevant trust level — the argument shape is the 5-arg canonical form, not the removed `mcp_trust_level` scalar.

**Rollback boundary:** Revert the lookup function + `SandboxTierFloorResult` + `ToolMetadata` + `MCPServer`. U-AS-08 + U-AS-09 consume `sandbox_tier_floor`; U-AS-08 consumes `MCPServer` (via the existing `[U-AS-06]` edge); rollback invalidates the D2-introduced `sandbox_tier_floor` axis and removes the `MCPServer` carrier.

#### U-AS-09 — Implement `sub_agent_sandbox_tier` monotonic-ascension function

`[FINALIZED at R3.1. Q-R3-1 resolved — G-1; `sub_agent_sandbox_tier` conformed to AS spec v1.2 §11.1 6-param form.]`

**Implements:** [C-AS-11 §11.1, §11.2, §11.3, §11.4, §11.5] *(spec v1.2 — §11.1 reconciled to the canonical 5-arg inner `sandbox_tier_floor` call + 6-param outer signature)*

**Depends on:** [U-AS-01, U-AS-04, U-AS-06]

**Inputs:** `parent_sandbox_tier`, `tool` (`ToolMetadata`, per U-AS-06), `blast_radius`, `mcp_transport`, `deployment_surface`, `mcp_server` (`MCPServer`, per U-AS-06). Parent tier resolved by U-AS-08 at the parent call site.

**Files affected:** AS-axis sub-agent sandbox-tier resolution module (logical: `sub-agent-sandbox-tier-resolution`); sub-agent boundary violation detector (logical: `sub-agent-tier-downgrade-violation-detector`).

**Signatures:**

```
function sub_agent_sandbox_tier(
  parent_sandbox_tier: SandboxTier,
  tool: ToolMetadata,
  blast_radius: BlastRadiusTier,
  mcp_transport: Optional<MCPTransport>,
  deployment_surface: DeploymentSurface,
  mcp_server: Optional<MCPServer>
) -> SandboxTier
  =
  max(
    parent_sandbox_tier,
    sandbox_tier_floor(tool, deployment_surface, blast_radius, mcp_transport, mcp_server)
  )

enum SubAgentBoundaryViolation {
  TIER_DOWNGRADE_ATTEMPTED(parent: SandboxTier, attempted_child: SandboxTier),
  REGISTRY_OVERRIDE_WITH_TIER_DOWNGRADE(parent: SandboxTier, attempted_child: SandboxTier)
}

function detect_sub_agent_tier_downgrade(
  parent_sandbox_tier: SandboxTier,
  proposed_child_tier: SandboxTier
) -> Optional<SubAgentBoundaryViolation>
```

> **Signature note.** The `sub_agent_sandbox_tier` outer signature is the AS-spec-v1.2 §11.1 6-parameter form `(parent_sandbox_tier, tool, blast_radius, mcp_transport, deployment_surface, mcp_server)`. It supersedes the v1-body 5-parameter form `(parent_sandbox_tier, blast_radius, mcp_transport, mcp_trust_level, deployment_surface)`: per the C-AS-02 reconciliation, the outer signature gains `tool` and `mcp_server` (so it has them to thread into the canonical 5-arg `sandbox_tier_floor` inner call) and **drops** `mcp_trust_level` — trust level travels inside `MCPServer`. The inner composition `max(parent_sandbox_tier, sandbox_tier_floor(tool, deployment_surface, blast_radius, mcp_transport, mcp_server))` matches spec §11.1 verbatim.

**Acceptance criteria:**
1. Sub-agent tier always ≥ parent tier (§11.2 row 1).
2. Tier downgrade structurally prohibited (§11.2 row 2); `detect_sub_agent_tier_downgrade` returns Some when proposed < parent.
3. D4 override-clause does not extend to sandbox monotonicity (§11.2 row 3 + §11.3) — even when registry-scoped override is set, downgrade detection returns Some.
4. Composition is `max(parent_tier, sandbox_tier_floor(tool, deployment_surface, blast_radius, mcp_transport, mcp_server))` per spec §11.1 — the `sandbox_tier_floor` argument list is the canonical 5-arg form; other floors do not reset at sub-agent dispatch.
5. Sub-agent tier-escalation surface emits `sandbox.tier_escalation` event (downstream Cluster 4); this unit returns the structured result.
6. Cross-deployment monotonicity composition: persona-tier bridging-arc raises floors per §11.4.
7. Tier downgrade attempt emits `sandbox.fail.class = POLICY_OVERRIDE` per §11.5 row 3.

**Tests:** `test_sub_agent_tier_at_or_above_parent`, `test_sub_agent_tier_max_of_two_floors`, `test_sub_agent_tier_parent_wins_when_floor_lower`, `test_sub_agent_tier_downgrade_detected`, `test_sub_agent_tier_at_or_above_no_violation`, `test_sub_agent_tier_d4_override_does_not_extend`, `test_sub_agent_tier_pure_function`, `test_sub_agent_sandbox_tier_signature_is_six_param_per_spec_11_1`.

**Rollback boundary:** Revert `sub_agent_sandbox_tier` + downgrade detector + `SubAgentBoundaryViolation`. CP plan loses the sandbox-monotonicity contract at sub-agent dispatch; sub-agents could dispatch at weaker isolation than parent.

#### U-AS-12 — Operator-policy override scope per persona-tier

`[FINALIZED at R3.1. Q-R3-4 resolved — Reading A. Acceptance-criteria wording fix only; no signature, input, or body change.]`

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

> **Signature note.** `[unchanged]` from the v1 body — Reading A is an acceptance-criteria wording fix only. `override_scope`'s inputs `(persona_tier, proposed_cell)` are sufficient: for the solo-developer persona every cell is treated as a non-compliance cell (see AC2), so no `cell_compliance_status` input is required and Reading B's signature growth is foreclosed.

**Acceptance criteria:**
1. `override_scope` total over (PersonaTier, (DeploymentSurface, BlastRadiusTier)).
2. Per-persona-tier scope conforms to spec §9.4:
   - SOLO_DEVELOPER → PERMITTED_APPEND_ONLY. Spec §9.4 reads "Permitted at non-compliance cells" for the solo-developer persona. For the solo-developer persona **every cell is treated as a non-compliance cell**, so the override scope is effectively total over `(DeploymentSurface, BlastRadiusTier)` — the §9.4 "non-compliance cells" qualifier and the plan's "any cell" coincide for this persona. *(The earlier "matches §9.4 verbatim" framing is dropped: §9.4 says "non-compliance cells"; AC2 states the persona-specific equivalence explicitly rather than claiming a verbatim string match. This is the Reading A wording fix — no false-divergence remains.)*
   - TEAM_BINDING + EXTERNAL_IRREVERSIBLE → PROHIBITED_BLAST_RADIUS_TIER (spec §9.4: team-binding "Permitted only at non-`external-irreversible` cells").
   - TEAM_BINDING + other → PERMITTED_HASH_CHAINED.
   - MULTI_TENANT_COMPLIANCE → PROHIBITED_STRUCTURAL at any cell (spec §9.4: "Structurally prohibited at any cell").
3. PROHIBITED_STRUCTURAL produces violation-event audit per §12.3, not a tier change.
4. Override-scope consumed downstream by Cluster 4 span unit (POLICY_OVERRIDE emission) and Cluster 6 audit unit.

**Tests:** `test_override_scope_solo_developer_permitted_at_all_cells`, `test_override_scope_team_binding_permitted_at_non_irreversible`, `test_override_scope_team_binding_prohibited_at_external_irreversible`, `test_override_scope_multi_tenant_compliance_prohibited_at_all_cells`, `test_override_scope_total_function`.

**Rollback boundary:** Revert override-scope module + `OverrideScopeResult`. Cluster 4 cannot discriminate POLICY_OVERRIDE emission posture at multi-tenant-compliance; Cluster 6 audit cannot emit per-persona-tier append-only vs hash-chained ledger entry.

#### U-AS-20 — Declare `fetch_secret` signature + `SecretRef` opaque type + tier-aware resolution mechanism table

`[FINALIZED at R3.1. Q-R3-2 resolved — R1 direction: `fetch_secret(name, scope, tier)` 3-param, tier as a plain argument. `SecretScope` ellipsis-body field-set fix applied. A-5 spec revision owed (§0.6).]`

**Implements:** [C-AS-05 §5.1, §5.2, §5.4] *(`Implements` citation bumps to the post-fix C-AS-05 version when the A-5 spec-writer pass revises §5.1 to the 3-param form; see §0.6)*

**Depends on:** [U-AS-01]

**Inputs:** Secret identifier (`name`); scope (`SecretScope`); resolved sandbox tier per call site (`tier`, `SandboxTier`, resolved by U-AS-08 at the call site and passed as a plain argument — R1 direction).

**Files affected:** AS-axis secret-fetch type declarations (logical: `secret-fetch-type-declarations`); secret-fetch API surface (logical: `secret-fetch-api-surface`); tier-aware resolution mechanism table (logical: `tier-aware-secret-resolution-table`).

**Signatures:**

```
opaque type SecretRef                            // no value-accessor API per §5.4

record SecretScope {                             // explicit field set — R3.1 fix; replaces the v1-body `{ ... }` ellipsis.
  name              : string                     // the credential-dimension session-key namespace identifier
                                                 // (spec §5.1: `scope` is the "credential-dimension session key
                                                 // per ADR-F5 v1.1 §Context"). Single field — spec §5.1 commits
                                                 // exactly the session-key identity; no further field is spec-committed.
}
// serialization format remains deferred to implementation discretion per spec §5.4; the FIELD SET is no longer `{ ... }`.

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

> **Signature note.** `fetch_secret` is finalized at the **3-parameter R1 form** `fetch_secret(name: string, scope: SecretScope, tier: SandboxTier) -> SecretRef` — the sandbox `tier` is a **plain third argument**, NOT a bundled context object. AS spec v1.2 §5.1 currently reads the 2-param `fetch_secret(name, scope) -> SecretRef`; the operator ratified the R1 direction (2026-05-15) and a C-AS-05 §5.1 spec revision to the 3-param form is owed — action item **A-5** (§0.6). The `SecretScope` `record` body, a `{ ... }` ellipsis in the v1 body, is replaced with an **explicit field set** (R3.1 Pattern B fix): spec §5.4 sanctions deferring the *serialization format*, not the *field set*.

**Acceptance criteria:**
1. `fetch_secret` signature is the 3-parameter form `(name: string, scope: SecretScope, tier: SandboxTier) -> SecretRef` per the operator-ratified R1 direction; the `tier` argument is a plain `SandboxTier`, resolved at the call site by U-AS-08 and passed positionally — not bundled in a context object. *(The v1-body AC1 contradiction — "`fetch_secret(name, scope)` matches §5.1 verbatim" while declaring `(name, scope, tier)` — is removed: R1 finalizes the 3-param form; C-AS-05 §5.1's revision to match is action item A-5.)*
2. `SecretRef` opaque per §5.4 row 1: no value-accessor API.
3. `SecretRef` lifetime bounded by sandbox lifetime per §5.4 row 2; cross-sandbox sharing prohibited.
4. `SecretRef` fresh-on-restart per §5.4 row 3: no in-process cache across restarts.
5. `TIER_RESOLUTION_TABLE` declares four entries per §5.2:
   - TIER_1_PROCESS → ENV_VAR_AT_SANDBOX_STARTUP / C2
   - TIER_2_CONTAINER → CONTAINER_ENV_VAR_WITH_KEYRING_HANDLES / C2
   - TIER_3_MICROVM → IN_SANDBOX_HTTP_BOOTSTRAP_TOKEN / C3
   - TIER_4_FULL_VM → IN_SANDBOX_HTTP_WITH_ROTATION_REFRESH / C3
6. T-perm-2 F5-layer closure: tier choice picks pole; both poles expressed; structural composition with F4.
7. `tier_resolution_mechanism` total over `SandboxTier`.
8. `SecretScope` is declared with an **explicit field set** (not a `{ ... }` ellipsis); the serialization format remains deferred per spec §5.4.

**Tests:** `test_secret_ref_no_value_accessor_api`, `test_secret_ref_lifetime_bounded_to_sandbox`, `test_secret_ref_no_cross_sandbox_sharing`, `test_tier_resolution_table_cardinality_four`, `test_tier_resolution_mechanism_per_spec_row_by_row`, `test_tier_1_process_pole_is_c2_within_turn`, `test_tier_3_microvm_pole_is_c3_across_turn`, `test_fetch_secret_signature_is_three_param`, `test_secret_scope_field_set_explicit_not_ellipsis`.

**Rollback boundary:** Revert `SecretRef` + `SecretScope` + `TIER_RESOLUTION_TABLE` + `fetch_secret` signature. All downstream secret-handling units (U-AS-21, U-AS-22, U-AS-23, U-AS-24, Cluster 6) lose foundational surface; secrets handling subsystem invalidated. *(U-AS-07 consumes `SecretScope` for `SecretAllowlistEntry.scope` via the v1.1 `[U-AS-20]` carrier-ordering edge — that edge is unchanged; the `SecretScope` field-set fix here makes the v1.1-flagged residual fully resolved.)*

---

## §5.4 Auxiliary-type audit

### §5.4.1 (superseded)

> **`[SUPERSEDED — replaced by §5.4.2.]`** Per v1.1 §5.4.1: the defective v1 §5.4.1 audit is superseded by the exhaustive §5.4.2 audit. Carried forward verbatim; v1.1 is canonical.

### §5.4.2 Exhaustive auxiliary-type audit (permanent plan section)

The §5.4.2 audit method (§5.4.2.1 — enumerate / classify (C)/(X)/(S)/(U) / in-cone check / carrier-ordering check) and the standing discipline clause (§5.4.2.3 — re-run at every AS-plan revision pass; any new type without a carrier row fails the coherence pass) are **`[preserved verbatim]` from v1.1 §5.4.2** — consult `Implementation_Plan_Action_Surface_v1_1.md` §5.4.2.1 / §5.4.2.3. This is the permanent structural fix for Pattern B and remains canonical.

#### §5.4.2.2 Audit table — R3.1 delta

The v1.1 §5.4.2.2 audit table is canonical; v1.2 applies the following **three delta rows** (the R3.1-finalized types):

| Type | Class | Carrier unit | Consuming units | In-cone? | R3.1 delta note |
|---|---|---|---|---|---|
| `ToolMetadata` | C | **U-AS-06** | U-AS-06, U-AS-09 | ✓ | v1.1 marked its *declaration* "deferred to R3.1 (rides §9 decision)". **R3.1 declares it** at U-AS-06; U-AS-09 consumes it via the existing `[U-AS-06]` edge. (U) → (C) closed. |
| `MCPServer` | C | **U-AS-06** *(re-homed from U-AS-08)* | U-AS-06, U-AS-08, U-AS-14 | ✓ | v1.1 §5.4.2.2 declared `MCPServer` at U-AS-08. **R3.1 re-homes it to U-AS-06** (§0.4): U-AS-06 consumes `MCPServer` at the `sandbox_tier_floor` signature and U-AS-06 is upstream of U-AS-08, so a U-AS-08-home carrier would force a U-AS-06→U-AS-08 cycle. U-AS-08 now consumes `MCPServer` via the existing `[U-AS-06]` edge; U-AS-14 via `[U-AS-08]`→`[U-AS-06]`. Carrier-ordering check passes — carrier is no longer downstream of a consumer. |
| `MCPTrustLevel` | — *(removed)* | — | — | n/a | v1.1 §5.4.2.2 listed `MCPTrustLevel` (carrier U-AS-06). **R3.1 removes the type** — the C-AS-02 reconciliation reads trust level from the `MCPServer` argument, not a standalone scalar. The `MCPTrustLevel` enum is deleted from U-AS-06's Signatures block; the four-valued trust level is now an internal field of `MCPServer`. No (U) row created — the type ceases to exist. |
| `SecretScope` | C | U-AS-20 | U-AS-07/22/24/26/27/30 | ✓ | v1.1 marked the `SecretScope` *field-set fix* "deferred to R3.1 (type exists; ellipsis body)". **R3.1 applies the fix** — explicit field set, serialization deferred per §5.4. Carrier unit unchanged (U-AS-20); the v1.1 `[U-AS-07]→[U-AS-20]` carrier-ordering edge unchanged. (C) row now fully resolved — no residual. |

All other v1.1 §5.4.2.2 rows are unchanged. The audit's **zero-(U) target** is reaffirmed: R3.1 closes the two former-deferred (C) entries (`ToolMetadata` declaration, `SecretScope` field set) and removes one type (`MCPTrustLevel`). Running the audit to a confirmed zero-(U) state against the landed/revised type set remains action item A-4 (§0.6).

---

## §7 Dependency-graph delta

The v1.1 §7 dependency graph (itself a delta over v1 §3) is canonical. v1.2 applies the following delta.

### §7.1 New / changed edges

**No edge is added or removed.** The 4 finalized units' `Depends on` lists are unchanged from their v1.1-carried bodies:

| Unit | `Depends on` (v1.2 — unchanged) | Note |
|---|---|---|
| U-AS-06 | `[U-AS-01, U-AS-04, U-AS-05]` | The reconciled 5-arg `sandbox_tier_floor` introduces no new dependency — `MCPServer` is declared *in* U-AS-06 (carrier re-home, §0.4), not imported. |
| U-AS-09 | `[U-AS-01, U-AS-04, U-AS-06]` | The 6-param `sub_agent_sandbox_tier` consumes `ToolMetadata` + `MCPServer`, both declared at U-AS-06 — in-cone via the existing `[U-AS-06]` edge. No new edge. |
| U-AS-12 | `[U-AS-04]` | Reading A is AC-text only — no dependency change. |
| U-AS-20 | `[U-AS-01]` | R1 `fetch_secret(name, scope, tier)` — `tier: SandboxTier` is declared at U-AS-01 (in-cone via the existing `[U-AS-01]` edge); R1 introduces no new dependency. The `SecretScope` field-set fix declares a single `name: string` field (a stack primitive — no carrier, no edge). |

> **`SecretScope` field set — no new edge.** The R3.1 `SecretScope` field set is a single `name: string` field — `string` is a `Target_Stack_Commitment` primitive (audit class (S)), requiring no carrier and no `Depends on` edge. U-AS-20's `Depends on` is `[U-AS-01]` unchanged. (Spec §5.1 commits exactly the session-key identity for `scope`; the planner declares only that field set and does not extend the contract with further fields — per SKILL.md §4.4 no-spec-extension discipline.)

### §7.2 `harness-core` import edges

Per v1.1 §7.2 — a `harness-core` import is flagged `(cross-axis: core)` but is an *import* edge, not an outbound CXA edge; it does not affect the AS→IS edge count. **R3.1 adds no `harness-core` import edge** — the v1.1 `harness-core` edge set is unchanged.

### §7.3 Cross-axis AS→IS edge re-cite

`[preserved verbatim]` from v1.1 §7.3 — action item A-3, not performed in this pass.

### §7.4 Acyclic invariant re-verification

R3.1 adds **no edge** — no new unit-to-unit edge and no new `harness-core` import edge. The `MCPServer` carrier re-home U-AS-08 → U-AS-06 (§0.4) moves a *declaration site*; the consuming references resolve through edges that **already exist** (U-AS-08 `[U-AS-06]`; U-AS-14 `[U-AS-08]`). Re-home from a downstream carrier to an upstream carrier strictly *removes* a cycle risk — it does not introduce one. **The graph remains a DAG, unchanged from v1.1.** Kahn verification still consumes all 33 AS units.

---

## §8 Coverage-matrix delta

The v1.1 §8 coverage-matrix delta is canonical. v1.2 applies the following delta — **no contract loses coverage; no coverage gap is introduced.**

| Contract section | v1.1 coverage | v1.2 coverage | Delta reason |
|---|---|---|---|
| C-AS-02 §2.3 | U-AS-06 (deferred to R3.1) | **U-AS-06 (finalized)** | The "deferred to R3.1 — finalization rides the §9 spec decision" qualifier is **removed**. The C-AS-02 spec gap is resolved (AS spec v1.2); U-AS-06 fully covers §2.3 against the reconciled 5-arg `sandbox_tier_floor`. |
| C-AS-11 §11.1–§11.5 | U-AS-09 (deferred to R3.1) | **U-AS-09 (finalized)** | Deferral qualifier removed; U-AS-09's `sub_agent_sandbox_tier` conformed to spec v1.2 §11.1. Coverage unchanged. |
| C-AS-09 §9.4 | U-CORE-01 (persona-tier enum) + U-AS-12 (deferred to R3.1) | U-CORE-01 + **U-AS-12 (finalized)** | Deferral qualifier removed; U-AS-12 covers §9.4 override-scope. Reading A — AC-text only; coverage unchanged. |
| C-AS-05 §5.1 | U-AS-20 (deferred to R3.1) | **U-AS-20 (finalized — A-5 caveat)** | Deferral qualifier removed; U-AS-20 covers §5.1 with the R1 3-param `fetch_secret`. **Caveat:** AS spec v1.2 §5.1 still reads the 2-param form; the C-AS-05 §5.1 spec revision to the 3-param form is owed (action item A-5, §0.6). The contract row stays covered; the body-citation alignment completes when A-5 lands. |
| C-AS-05 §5.2, §5.4 | U-AS-20 (deferred to R3.1) | **U-AS-20 (finalized)** | Deferral qualifier removed. §5.2 (tier-resolution table) and §5.4 (`SecretRef` opacity + `SecretScope` field-set fix) fully covered. No spec mismatch on these sections. |

> **Coverage-matrix note.** All four finalized units retain their v1.1 contract rows; the only change is the removal of the `[deferred to R3.1]` qualifier and, for C-AS-05 §5.1, the addition of the A-5 spec-revision caveat. No row is dropped; no contract is left uncovered.

---

## §9 Filing footer

| Field | Value |
|---|---|
| Artifact | `Implementation_Plan_Action_Surface_v1_2.md` |
| Role | `implementation-planner`, revision-pass sub-mode (SKILL.md §8) |
| Authored | 2026-05-15, Phase 7 sub-phase 7b — revision pass **R3.1** (the AS micro-pass; finalizes the 4 units R3 deferred) |
| Predecessor | `Implementation_Plan_Action_Surface_v1_1.md` (v1.1, 2026-05-15) — verbatim base for all 29 non-finalized units |
| Source | `.harness/revision_R3_as_plan.md` §5 (R3 conditional bodies); `.harness/s1_c_as_02_reconciliation.md` (operator-ratified C-AS-02 reconciliation); `design-substrate/Spec_Action_Surface_v1.md` v1.2 (reconciled 5-arg `sandbox_tier_floor`); the operator ratification decisions at §0.2 |
| Scope | AS plan v1.1 → v1.2 — **R3.1 micro-pass**: finalize the 4 R3-deferred units (U-AS-06, U-AS-09, U-AS-12, U-AS-20). 4 units finalized (full bodies, deferral markers removed); 29 units preserved verbatim (9 R3-revised + 20 R3-preserved). §5.4.2 audit delta (3 rows + 1 type removal); dependency-graph delta (no edge added or removed; 1 carrier-home move only — `MCPServer` U-AS-08 → U-AS-06); coverage-matrix delta (4 deferral qualifiers removed). |
| Decisions applied | U-AS-06/09 — G-1 / reconciled 5-arg `sandbox_tier_floor` per AS spec v1.2 (C-AS-02 gap resolved). U-AS-12 — Reading A (AC-text wording fix only). U-AS-20 — R1 (`fetch_secret(name, scope, tier)` 3-param, plain `tier` arg) + `SecretScope` field-set fix. |
| Action items | A-1..A-4 carried forward verbatim from v1.1 §0.7 (deferred coding-lane / mechanical). **A-5 NEW** — C-AS-05 §5.1 spec revision to the 3-param `fetch_secret` form owed (operator-ratified R1 direction; spec-writer pass owed; §0.6). |
| Status | **Proposed** — pending P6-CK clearance. |
| Successor | P6-CK clearance of v1.2; the A-5 `spec-writer` C-AS-05 §5.1 revision; R4 (CP) / R5 (OD) per the carrier-map ordering. With v1.2 the R3 → R3.1 AS-plan revision arc closes — all 33 AS units carry final (non-conditional) bodies. |
| HARD WALL attested | This pass wrote only `design-substrate/Implementation_Plan_Action_Surface_v1_2.md`. No other `design-substrate/` file, no `CLAUDE.md`, no R3 proposal / S1 recommendation / spec / audit / source edited. No git commit. |

*End of `Implementation_Plan_Action_Surface_v1_2.md` (v1.2). R3.1 micro-pass delta over v1.1; v1.1 is the verbatim base for all 29 `[preserved verbatim]` pointers.*
