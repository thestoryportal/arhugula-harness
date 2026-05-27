# Implementation Plan — Action Surface v1.4

## Change-note (v1.3 → v1.4)

**Trigger.** Class 1 fork resolution Reading B absorption per `.harness/class_1_fork_as_4_f4_enum_taxonomy_mismatch_and_production_bug.md` (operator-ratified 2026-05-25; AS spec v1.5 → v1.6 amendment landed at `bb2474d`). AS spec v1.6 §15.8 + §15.9 + §15.10 author NEW `MCPInvocationFailClass` 4-value StrEnum + `mcp.fail.class` attribute on `sandbox.violation` child span + best-effort projection table MCP-shape → F4-shape. F4 enum at §4.1 PRESERVED VERBATIM; existing §15.1..§15.7 PRESERVED VERBATIM.

**Scope of revision.** Two single-unit-body canonical-reading amendments at delta-only-plan-chain layer (v1.2 + v1.3 plan files preserved byte-exact; v1.4 supplies amendment-overlay):

- **U-AS-03 carrier-extension** — extends `sandbox_fail_class.py` carrier module to additionally declare `MCPInvocationFailClass` 4-value StrEnum (`transport` / `protocol_error` / `schema_violation` / `timeout`) + the §15.10 projection table function `project_mcp_to_sandbox_fail_class(mcp_fail_class) -> SandboxFailClass`. ZERO new atomic unit; ZERO DAG topology change; ZERO cluster reorganization. The carrier-home-extension pattern mirrors the v1.4 §14.3 footer producer-vs-canonical-schema separation discipline (AS-axis owns the canonical enum + projection; runtime-axis dispatcher consumes via import).
- **U-AS-17 AC #3 absorption** — AC #3 attribute-count text REPLACED: `sandbox.violation` carries `1+` → `2+` attributes per §15.9 dual-attribute emission (`sandbox.fail.class` per F4 §4.1 AND `mcp.fail.class` per §15.8). 2 NEW ACs (#9, #10) covering dual-attribute emission discipline + projection-table application. `SANDBOX_VIOLATION_ATTRIBUTES` constant at `sandbox_span_schema.py` extends from `frozenset({"sandbox.fail.class"})` to `frozenset({"sandbox.fail.class", "mcp.fail.class"})`. NEW test names added per §15.9 emission-scenario matrix at spec §15.9 5-row table.

**Spec authority chain.** AS spec v1.6 §15.8 (MCPInvocationFailClass enum) + §15.9 (mcp.fail.class dual-attr emission) + §15.10 (projection table) — operator-ratified Reading B at fork doc §7. F4 enum at C-AS-04 §4.1 PRESERVED VERBATIM — no field change at U-AS-03 SandboxFailClass surface.

**Plan shape preserved.** v1.2's 9-cluster axis-led structure preserved verbatim. No new clusters; no new units. Net AC count: +3 (U-AS-17 AC #3 text-replace + #9 + #10). Net unit count: 33 → 33.

**ZERO cross-axis cascade at v1.4 semantics layer.** Potential cite cascade owed at follow-on OD §C-OD-04/05/06 (D6 §1.2 sandbox.* ingestion at OD axis) + CXA v2.10 §2.3 (AS↔OD edge enumeration) — NOT patched per FM-2 no-extension discipline; tracked at adjacent-defects section below.

**Sections preserved verbatim from v1.3 + v1.2 + v1.1 + v1.** ALL pre-v1.4 content preserved byte-exact at predecessor files. v1.4 supplies canonical-reading amendment-overlay per the delta-only-plan-chain convention applied at runtime plan v2.18 §1 cite-cascade pattern + CP plan v2.19 §1 cluster-10-CP-A pattern.

**Status posture.** Proposed (v1.3) → Proposed (v1.4). v1.4 is an additive substantive amendment absorbing AS spec v1.6 §15.8/§15.9/§15.10; F4 enum surface unchanged; U-AS-03 carrier-extension; U-AS-17 AC dual-attr absorption.

**Downstream absorption owed (post-v1.4).**
- Workspace `CLAUDE.md` §2.4 AS row version bump (v1.2 → v1.4 — note two-version skip absorbs v1.3 documentary annotation pass + v1.4 substantive amendment in one row update).
- `harness-as/CLAUDE.md` §1.2 + §4.1 spec version cite update (v1.3 → v1.6 spec; v1.2 → v1.4 plan); §4.1 AS-4 row PARTIAL → RETIRED at batch-20 close.
- Fork doc §8 OPEN → READING-B-APPLIED at retirement-batch-20 filing.
- Retirement batch-20 ledger entry per `phase-7-substitution-retirement` skill §3.2.

---

## §1 — U-AS-03 carrier-extension (canonical-reading amendment)

**v1.2 + v1.3 unit body PRESERVED VERBATIM.** SandboxFailClass 7-value enum + C5FailClass + C9RetryPosture + per-class metadata table preserved byte-exact at `harness-as/src/harness_as/sandbox_fail_class.py`.

**v1.4 amendment** — the same carrier module additionally declares the MCPInvocationFailClass surface per AS spec v1.6 §15.8 + §15.10:

| Surface | v1.2 status | v1.4 amendment |
|---|---|---|
| `SandboxFailClass` 7-value StrEnum | landed at U-AS-03 | PRESERVED VERBATIM |
| `C5FailClass` + `C9RetryPosture` enums | landed at U-AS-03 | PRESERVED VERBATIM |
| `SandboxFailClassMetadata` + `_FAIL_CLASS_METADATA` table | landed at U-AS-03 | PRESERVED VERBATIM |
| `MCPInvocationFailClass` 4-value StrEnum (`transport` / `protocol_error` / `schema_violation` / `timeout`) | NOT LANDED | **NEW at v1.4** per §15.8 |
| `project_mcp_to_sandbox_fail_class(mcp_fail_class) -> SandboxFailClass` projection function | NOT LANDED | **NEW at v1.4** per §15.10 |
| `__all__` export — `MCPInvocationFailClass` + `project_mcp_to_sandbox_fail_class` | NOT LANDED | **NEW at v1.4** |

**NEW ACs at U-AS-03 (appended to v1.2 unit body):**

- **AC #N+1** — `MCPInvocationFailClass` enum declared at `sandbox_fail_class.py` (or sibling module `mcp_invocation_fail_class.py` at implementer-discretion; current carrier-home recommended for cohesion with SandboxFailClass sibling per §15.8 authority anchor "sibling to F4 at C-AS-04 §4.1"). 4 string values: `"transport"` / `"protocol_error"` / `"schema_violation"` / `"timeout"` byte-exact per §15.8 row 1 column 1.
- **AC #N+2** — `project_mcp_to_sandbox_fail_class(MCPInvocationFailClass) -> SandboxFailClass` projection function per §15.10 table: `transport → EXIT_NONZERO`; `protocol_error → EXIT_NONZERO`; `schema_violation → POLICY_OVERRIDE`; `timeout → TIMEOUT`. Function is pure + total over the 4-value enum domain.
- **AC #N+3** — `__all__` re-exports `MCPInvocationFailClass` + `project_mcp_to_sandbox_fail_class` from `harness_as.sandbox_fail_class` module (or carrier-home module).

**NEW test names (appended to v1.2 test list):**

- `test_mcp_invocation_fail_class_enum_cardinality_four`
- `test_mcp_invocation_fail_class_identifier_strings_snake_case_byte_exact`
- `test_project_mcp_to_sandbox_transport_returns_exit_nonzero`
- `test_project_mcp_to_sandbox_protocol_error_returns_exit_nonzero`
- `test_project_mcp_to_sandbox_schema_violation_returns_policy_override`
- `test_project_mcp_to_sandbox_timeout_returns_timeout`
- `test_project_mcp_to_sandbox_total_function_over_enum_domain`

**Implementer-discretion at carrier home.** §15.8 authors at C-AS-15 §15 (sandbox.* contract surface) but the enum carrier semantically siblings F4 SandboxFailClass at C-AS-04 §4.1 (also a fail-class enum). Two implementer paths:
- (a) Co-locate in `sandbox_fail_class.py` (recommended — single module owns BOTH fail-class enums; matches §15.8 spec narrative "sibling to F4"; reduces import surface).
- (b) Separate module `mcp_invocation_fail_class.py` (cleaner namespace separation; matches the §15 vs §4 spec authoring boundary).

Recommendation: (a) per cohesion + §15.8 sibling-narrative. Implementer free to pick (b) if cross-module schema-validation tooling prefers per-module enums. Either path satisfies AC #N+1 / #N+2 / #N+3.

---

## §2 — U-AS-17 AC #3 absorption + 2 NEW ACs (canonical-reading amendment)

**v1.2 + v1.3 unit body PRESERVED VERBATIM** except for AC #3 text-replace + 2 appended ACs:

**AC #3 text-replace.**

> v1.2 AC #3: "`sandbox.enter` carries 10 attributes (tier, tech, provider, policy.assigned_tier_reason, deployment_surface, blast_radius_tier, mcp_transport, cold_start_ms, pool_acquired, persona_tier); **`sandbox.violation` carries 1+**; `sandbox.tier_escalation` carries 3 (from_tier, to_tier, escalation_cause); `sandbox.exit` carries 5."
>
> v1.4 AC #3 (REPLACED): "`sandbox.enter` carries 10 attributes (tier, tech, provider, policy.assigned_tier_reason, deployment_surface, blast_radius_tier, mcp_transport, cold_start_ms, pool_acquired, persona_tier); **`sandbox.violation` carries 2+ (per §15.9 dual-attribute emission: `sandbox.fail.class` per F4 §4.1 AND `mcp.fail.class` per §15.8 — either MAY be null per §15.9 emission-scenario matrix; both names always-emitted on the event)**; `sandbox.tier_escalation` carries 3 (from_tier, to_tier, escalation_cause); `sandbox.exit` carries 5."

**NEW AC #9** — `SANDBOX_VIOLATION_ATTRIBUTES` constant at `sandbox_span_schema.py` extended from v1.2 baseline `frozenset({"sandbox.fail.class"})` to v1.4 baseline `frozenset({"sandbox.fail.class", "mcp.fail.class"})` per §15.9. The attribute set is the canonical schema; either value MAY be omitted-not-null on a given emission per §15.9 scenario matrix, but both names ride the canonical schema.

**NEW AC #10** — `sandbox_attribute_schema.py` registers `mcp.fail.class` attribute row with `emitted_on = "sandbox.violation"` + `attribute_name = "mcp.fail.class"` per §15.2 row-shape discipline (the existing rows at v1.2 cover the 7 `sandbox.*` attributes; the new `mcp.fail.class` is a NEW row at this schema-registration surface, NOT a member of the original `sandbox.*` 7-attribute namespace — `mcp.fail.class` carries the `mcp.*` namespace prefix but is co-emitted on the `sandbox.violation` event per §15.9 cross-namespace co-emission discipline).

**NEW test names (appended to v1.2 test list):**

- `test_sandbox_violation_attributes_includes_mcp_fail_class`
- `test_sandbox_violation_attributes_cardinality_two` (UPDATES the v1.2 `test_sandbox_violation_attributes_include_fail_class` — extends from `len(...) >= 1` to `len(...) == 2`; v1.2 test name preserved + extended OR replaced at implementer-discretion)
- `test_mcp_fail_class_emitted_on_sandbox_violation_event`
- `test_dual_attribute_emission_scenario_escape_attempt_omits_mcp_fail_class` (per §15.9 row 1)
- `test_dual_attribute_emission_scenario_transport_omits_sandbox_fail_class` (per §15.9 row 2)
- `test_dual_attribute_emission_scenario_schema_violation_omits_sandbox_fail_class` (per §15.9 row 3)
- `test_dual_attribute_emission_scenario_timeout_dual_emission_via_projection` (per §15.9 row 4 + §15.10 projection)
- `test_dual_attribute_emission_scenario_policy_override_omits_mcp_fail_class` (per §15.9 row 5)

**Authority anchor.** AS spec v1.6 §15.9 dual-attribute emission discipline + §15.10 best-effort projection table.

---

## §3 — Adjacent defects surfaced (not patched per FM-2)

**(a) Spec §15.10 row 3 HIGH semantic stretch.** `schema_violation → policy_override` projection is flagged HIGH semantic stretch at §15.10 row 3 itself ("F4 `policy_override` is documented as 'operator-tunable downgrade', not 'contract violation'. The projection acknowledges this stretch; future spec revision MAY add a F4 `contract_violation` value to absorb this projection cleanly."). The plan adopts the spec's recommended-default option (a) projection at impl arc per AC text; the HIGH stretch is acknowledged + filed for future ADR-D2 / F4 enum revision arc. NOT patched per FM-2 — projection is a structural correspondence for audit-ledger continuity, not a semantic-equivalence claim.

**(b) OD §C-OD-04/05/06 cite-cascade owed.** AS spec v1.6 §15.9 amends `sandbox.violation` event attribute set; OD §C-OD-04 base layer + §C-OD-06 AS-source verification ingest `sandbox.*` namespace. The `mcp.fail.class` attribute is co-emitted on `sandbox.violation` per §15.9 cross-namespace co-emission discipline; OD-axis ingestion path for the `mcp.*` namespace on this event is undocumented at OD spec v1.11. NOT patched per FM-2 — future OD spec revision MAY absorb the dual-attribute ingestion discipline at §C-OD-06; out-of-scope for v1.4 AS plan amendment.

**(c) CXA v2.10 §2.3 AS↔OD edge enumeration.** AS-axis cross-axis edges to OD per CXA v2.10 §2.3.6 enumerate 10 inbound edges (OD→AS). The dual-attribute `sandbox.violation` event surface is consumed by OD audit-ledger via `sandbox.*` namespace pull; whether the `mcp.fail.class` co-emission warrants a NEW edge declaration at CXA §2.3.6 is undocumented. NOT patched per FM-2 — out-of-scope for v1.4 AS plan amendment.

**(d) ADR-D2 reference frame.** Fork doc §6 adjacent finding (iii) notes ADR-D2 v1.2 §1.7 + §1.7.1 reference frame UNCHANGED at v1.6 spec amendment — MCPInvocationFailClass at §15.8 is AS-spec-internal contract additive, NOT an ADR-D2 §1.7.X declaration site extension. Future ADR-D2 revision arcs MAY surface MCP-protocol-layer fail-class as downstream §1.7.X if cross-axis composition demands it. NOT patched per FM-2 + X-AL-3 no-silent-design-extension discipline at later phases.

---

## §4 — Coverage matrix delta (v1.3 → v1.4)

No coverage delta. AS contracts C-AS-01 through C-AS-16 retain their v1.3 unit coverage verbatim. The new §15.8 + §15.9 + §15.10 subsections at C-AS-15 §15 extend the existing C-AS-15 contract surface; U-AS-03 + U-AS-17 already cover C-AS-15 per v1.2 baseline (U-AS-03 covers fail-class enums; U-AS-17 covers span hierarchy + attribute schema). No new coverage row added; existing rows extend in-scope per the unit-body amendment.

---

## §5 — DAG verification (v1.3 → v1.4)

DAG unchanged. v1.4 amendment is in-unit-body (U-AS-03 + U-AS-17); no new units; no new edges. U-AS-17 dependency edge `[U-AS-01, U-AS-03, U-AS-08, U-AS-16]` preserved verbatim — U-AS-17 already depends on U-AS-03 at v1.2, and the v1.4 carrier-extension at U-AS-03 strengthens the existing edge (U-AS-17 now consumes BOTH `SandboxFailClass` + `MCPInvocationFailClass` from U-AS-03; both at same unit; same edge). Topological sort unchanged.

---

## Filing footer

| Field | Value |
|---|---|
| Artifact | `Implementation_Plan_Action_Surface_v1_4.md` |
| Version | v1.4 |
| Filing event | Class 1 fork resolution Reading B absorption per `.harness/class_1_fork_as_4_f4_enum_taxonomy_mismatch_and_production_bug.md` arc 2, 2026-05-26 |
| Predecessor | `Implementation_Plan_Action_Surface_v1_3.md` (v1.3 — Phase A.2 annotation-only); v1.2 substantive baseline preserved byte-exact at `Implementation_Plan_Action_Surface_v1_2.md` |
| Spec authority | `Spec_Action_Surface_v1.md` v1.6 §15.8 + §15.9 + §15.10 (operator-ratified Reading B at fork doc §7; spec amendment landed at `bb2474d`) |
| New units | 0 |
| Amended unit bodies | U-AS-03 (carrier-extension: +MCPInvocationFailClass enum + projection function); U-AS-17 (AC #3 text-replace + NEW ACs #9 + #10) |
| Net AC delta | +3 ACs across U-AS-03 (3 new) + U-AS-17 (1 text-replace + 2 new) |
| DAG verification | Unchanged (no new units; no graph delta; existing U-AS-17 → U-AS-03 edge strengthened in-cone) |
| Coverage verification | Unchanged (C-AS-04 + C-AS-15 contracts already covered at v1.2; v1.4 extends in-unit-body) |
| Cross-axis cascade | ZERO at v1.4 semantics layer; 3 adjacent OD + CXA + ADR-D2 cascades surfaced at §3 NOT patched per FM-2 |
| Date | 2026-05-26 |
