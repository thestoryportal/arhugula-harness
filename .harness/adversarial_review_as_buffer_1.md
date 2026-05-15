# Adversarial Review — AS-axis review-ahead buffer 1

## Summary

- Mode: Phase-7 pre-implementation review (review-ahead lane, pipeline pass)
- Artifact reviewed: `design-substrate/Implementation_Plan_Action_Surface_v1.md` (unit blocks U-AS-20, U-AS-28, U-AS-06, U-AS-08, U-AS-10) vs `design-substrate/Spec_Action_Surface_v1.md` (C-AS-02 §2, C-AS-05 §5, C-AS-09 §9, C-AS-13 §13) + ADR-D2 v1.1 / ADR-D3 v1.2 commitments
- Date: 2026-05-15
- Finding count by §4.1 review-severity class: **Class 3: 3 · Class 2: 4 · Class 1: 2**
- Highest-severity finding: F3-01 (U-AS-06 `sandbox_tier_floor` 5th parameter not in spec §2.3 signature)
- Disposition recommendation: **BLOCKED cluster** — 3 of 5 units carry a §2.7.6 Class 1 (halt-execution) fork; 2 of 5 carry §2.7.6 Class 2 (operator-decision) forks only. No unit clears with zero blocking findings. Per-unit verdict at the Pipeline clearance verdict section.

**Two-taxonomy note (SKILL.md §1).** This report uses the §4.1 review-severity scale (Class 1 minor / Class 2 moderate / Class 3 severe). Where a disposition triggers a Phase-7 execution fork, the §2.7.6 fork class (Class 1 halt / Class 2 operator-decision / Class 3 informational) is stated explicitly and labelled. The two scales are not the same; a §4.1 Class 3 finding is not a §2.7.6 Class 3 fork.

---

## Class 3 findings (severe — requires upstream-phase artifact revision)

### F3-01 — U-AS-06 `sandbox_tier_floor` signature carries a 5th parameter absent from the spec §2.3 contract

- **Location:** `Implementation_Plan_Action_Surface_v1.md` U-AS-06 Signatures block, `function sandbox_tier_floor(tool, deployment_surface, blast_radius_tier, mcp_transport, mcp_trust_level)`; vs `Spec_Action_Surface_v1.md` §2.2 composition formula (lines 197–202) `sandbox_tier_floor(tool, call_site_context.deployment_surface, call_site_context.blast_radius_tier, call_site_context.mcp_transport)`.
- **Defect:** The spec's only signature surface for `sandbox_tier_floor` is the §2.2 `max()` formula, which invokes it with **four** arguments — `mcp_trust_level` is not among them. The plan unit's signature declares **five** parameters, adding `mcp_trust_level: Optional<MCPTrustLevel>`. The spec §2.3 lookup *table* does have rows keyed on remote-MCP trust level (L0/L1/L2/L3), so the trust level is semantically required for the lookup — but the spec never threads it into the function signature. The spec under-specifies its own contract: the §2.3 table cannot be evaluated from the §2.2 four-argument call site. The plan unit silently repairs the gap by extending the signature.
- **Discriminator that classifies as Class 3:** (b) — resolving the finding requires revising the C-AS-02 §2.2 / §2.3 contract (a Phase-5 artifact) so the `sandbox_tier_floor` signature and its call site agree on the trust-level argument. The plan cannot be made faithful to the spec as written without the spec changing.
- **Evidence:** Spec §2.2 line 197–202 passes exactly four args; spec §2.3 (lines 213–224) rows 4–6 ("Remote MCP, trust level 0/1/2/3") are inexpressible without a trust-level input the §2.2 call site does not supply.
- **Axis-domain attack engaged:** AS — untyped/under-typed tool I/O; sandbox-tier composition floor signature vs lookup-table key set.
- **Decision-claim label:** *decided* — the text supports a single reading: the spec's signature surface omits a parameter its own lookup table requires.
- **Resolution path:** §2.7.6 **Class 1 (halt-execution)** fork. Route to Phase-5 AS spec revision-pass: reconcile the C-AS-02 §2.2 call site and §2.3 table so the trust-level argument is consistently present (or consistently sourced from `call_site_context`). Until reconciled, U-AS-06 cannot be cleared — its signature is a plan-introduced extension over an under-specified spec contract (X-AL-3 silent-absorption shape).

### F3-02 — U-AS-20 `fetch_secret` signature carries a 3rd parameter while AC1 claims verbatim spec match

- **Location:** `Implementation_Plan_Action_Surface_v1.md` U-AS-20 Signatures block, `function fetch_secret(name: string, scope: SecretScope, tier: SandboxTier) -> SecretRef`; U-AS-20 acceptance criterion 1, "`fetch_secret(name, scope)` signature matches §5.1 verbatim; `tier` injected by U-AS-08"; vs `Spec_Action_Surface_v1.md` §5.1 (lines 354–356) `fetch_secret(name: string, scope: SecretScope) -> SecretRef`.
- **Defect:** Spec §5.1 — and the C-AS-05 contract title at spec line 340 — fix the signature at **two** parameters, `(name, scope)`. The plan unit's Signatures block declares **three** parameters, adding `tier: SandboxTier`. AC1 simultaneously asserts the signature "matches §5.1 verbatim" and concedes "`tier` injected by U-AS-08". A signature with a parameter the cited contract does not contain is not a verbatim match; AC1 is an internally contradictory verbatim claim. This is the Tension-002 / Tension-004 verbatim-claim calibration shape exactly: a unit asserts byte-exact transcription of a spec contract while the transcription adds a parameter.
- **Discriminator that classifies as Class 3:** (b) — the divergence is substantive (the public secret-fetch signature is a contract surface consumed by every downstream secret unit U-AS-21–24). Resolving it faithfully requires either the spec §5.1 / C-AS-05 title adopting the three-parameter form (Phase-5 revision) or the plan dropping `tier` from the signature and threading it via a context object. Either way an upstream or current artifact must change; the "verbatim" claim cannot stand.
- **Evidence:** Spec line 340 contract title `C-AS-05 — fetch_secret(name, scope) -> SecretRef signature`; spec §5.1 lines 354–356 two-parameter signature; plan U-AS-20 line 1039 three-parameter signature; plan U-AS-20 AC1 line 1044 verbatim claim.
- **Axis-domain attack engaged:** AS — tool/secret-fetch contract signature precision.
- **Anti-fabrication attack engaged:** A2 (silent scope alteration of the cited contract surface).
- **Decision-claim label:** *decided* — the contradiction between AC1's verbatim claim and the three-parameter Signatures block is unambiguous in the unit's own text.
- **Resolution path:** §2.7.6 **Class 1 (halt-execution)** fork. Operator decides the canonical reading: (R1) spec §5.1 + C-AS-05 title revised to the three-parameter form (Phase-5 spec revision-pass) and AC1's verbatim claim re-scoped; or (R2) plan U-AS-20 signature reverts to two parameters and `tier` is carried in a context object (Phase-6 plan revision-pass). The reviewer does not pick the reading.

### F3-03 — U-AS-06 / U-AS-08 / U-AS-28 consume auxiliary record types declared by no unit in the dependency cone (systemic undeclared-type pattern)

- **Location:** Multiple. U-AS-06 Signatures `sandbox_tier_floor(tool: ToolMetadata, ...)` — `ToolMetadata` referenced (also U-AS-06 Inputs line 325); U-AS-08 Signatures `record CallSiteContext { taint_state: TaintState; mcp_server: Optional<MCPServer>; ... }` — `TaintState` and `MCPServer` referenced; U-AS-28 Signatures `const ANTHROPIC_PRIMITIVE_ANCHORS: Map<AnthropicPrimitive, AnchorCitation>` — `AnchorCitation` referenced. None of `ToolMetadata`, `TaintState`, `MCPServer`, `AnchorCitation` appears as a `record`/`enum`/`opaque type` declaration in any unit's Signatures block (verified by full-file grep — these identifiers appear only at *consumption* positions).
- **Defect:** Each of these is a structured type used at a typed signature position with no declaring carrier. Per-unit dependency cones do not resolve them: U-AS-06 Depends-on = [U-AS-01, U-AS-04, U-AS-05] (none declares `ToolMetadata`); U-AS-08 Depends-on = [U-AS-01, U-AS-02, U-AS-04, U-AS-05, U-AS-06, U-AS-07] (none declares `TaintState` or `MCPServer` — U-AS-08's own `CallSiteContext` *uses* them as field types but does not declare them); U-AS-28 Depends-on = [U-AS-04, U-IS-01, U-IS-02] (none declares `AnchorCitation`). This is the Tension-003 / U-AS-07-`required_secrets` fork shape: a type consumed with no carrier in the dependency cone. The pattern recurs across ≥3 units, making it systemic rather than a per-unit slip.
- **Discriminator that classifies as Class 3:** (b) — a unit whose signature references a type with no declaring carrier is not materializable as written; closing the gap requires revising the AS plan (Phase-6 artifact) to add carrier units / carrier declarations, or to declare these as inline-prose-materialized auxiliary types with explicit discipline. The plan's §3.4 dependency table and §3.5 DAG do not account for these carriers.
- **Evidence:** Grep of `Implementation_Plan_Action_Surface_v1.md` for `record ToolMetadata` / `record ToolContext` / `enum TaintState` / `record MCPServer` / `AnchorCitation` returns zero declaration sites; `ToolMetadata` appears at lines 325, 345 (consumption only); `TaintState`/`MCPServer` at lines 425–426, 437, 705 (consumption only); `AnchorCitation` at line 1448 (consumption only).
- **Axis-domain attack engaged:** AS — untyped tool I/O; signature materializability.
- **Decision-claim label:** *decided* for the existence of the gap; *proposing* for whether the intended resolution is carrier-unit addition vs inline-auxiliary-type discipline — both are consistent with the plan's text and the operator picks.
- **Resolution path:** §2.7.6 **Class 1 (halt-execution)** fork for U-AS-06 (`ToolMetadata`), U-AS-08 (`TaintState`, `MCPServer`), and U-AS-28 (`AnchorCitation`). Route to Phase-6 AS plan revision-pass: declare the auxiliary record/enum types with explicit carriers and dependency-graph edges, or document an inline-auxiliary-type materialization discipline. See systemic-pattern note in Disposition.

---

## Class 2 findings (moderate — current-phase plan revision)

### F2-01 — U-AS-10 acceptance criterion 2 references provider-class identifier `PROCESS_FS_OVERLAY` that the landed `SandboxProviderClass` enum does not contain

- **Location:** `Implementation_Plan_Action_Surface_v1.md` U-AS-10 acceptance criterion 2, "local-dev/self-hosted = LANGUAGE_LEVEL / PROCESS_FS_OVERLAY / CONTAINER / MICROVM_FIRECRACKER"; vs U-AS-11 Signatures block (landed), `enum SandboxProviderClass { LANGUAGE_LEVEL, FILESYSTEM_OVERLAY_WORKTREE, PROCESS_ULIMIT_BUBBLEWRAP_SEATBELT, CONTAINER, MICROVM_FIRECRACKER, FULL_VM }`.
- **Defect:** U-AS-10 AC2 names a provider-class value `PROCESS_FS_OVERLAY`. The `SandboxProviderClass` enum is declared by U-AS-11 — a landed unit and U-AS-10's declared predecessor — with six members, none named `PROCESS_FS_OVERLAY`. The closest landed members are `FILESYSTEM_OVERLAY_WORKTREE` and `PROCESS_ULIMIT_BUBBLEWRAP_SEATBELT`; AC2 supplies neither. The plan unit's acceptance criterion references an enum identifier that does not exist in its dependency cone. Distinct from F3-03's undeclared-type shape: here the carrier (U-AS-11) *is* in the cone, but the AC's identifier disagrees with the carrier's declared member set.
- **Discriminator that classifies as Class 2:** (a) — affects substantive content of a current-phase (Phase-6 plan) artifact; resolution is a plan-internal reconciliation of U-AS-10's AC2 identifier set with U-AS-11's landed enum, with no upstream-artifact change required. Escalates to Class 3 only if the reconciliation reveals the spec §9.1 row-label "process-fs-overlay" cannot be mapped onto any of U-AS-11's six members (then the spec §9.2 enumeration itself is the defect locus).
- **Evidence:** U-AS-11 enum at plan lines 570–577 (six members enumerated); U-AS-10 AC2 at plan line 547 names `PROCESS_FS_OVERLAY`.
- **Axis-domain attack engaged:** AS — sandbox provider-class enum identity; cross-unit enum-member consistency.
- **Decision-claim label:** *decided* for the mismatch; the operator-facing question is which landed member the spec §9.1 "process-fs-overlay" cell maps to.
- **Resolution path:** §2.7.6 **Class 2 (operator-decision)** fork — non-halting choice point. Reconcile U-AS-10 AC2's provider-class identifiers with U-AS-11's landed `SandboxProviderClass` member set. Operator selects which landed member the spec §9.1 local-development T2 cell ("process-fs-overlay" label) resolves to; `implementation-planner` applies. If no landed member fits the spec label, escalate to Class 3 against the spec §9.2 enumeration.

### F2-02 — U-AS-28 acceptance criterion 1 claims "kebab-case" and "verbatim per §13.1" but §13.1 declares no machine identifiers

- **Location:** `Implementation_Plan_Action_Surface_v1.md` U-AS-28 acceptance criterion 1, "`AnthropicPrimitive` declares exactly 11 values per §13.1 verbatim kebab-case"; test `test_anthropic_primitive_identifier_strings_byte_exact_per_spec_13_1`; vs `Spec_Action_Surface_v1.md` §13.1 (lines 838–854), a prose table of primitive *names* ("Skills system", "MCP-as-code", …) with no machine-identifier column.
- **Defect:** AC1 makes two claims that the cited spec section cannot support. (1) "kebab-case": the `AnthropicPrimitive` enum in the same unit's Signatures block is declared in SCREAMING_SNAKE_CASE (`SKILLS_SYSTEM`, `MCP_AS_CODE`, …) — the AC contradicts the unit's own signature. (2) "verbatim per §13.1" + the `byte_exact_per_spec_13_1` test: spec §13.1 contains no identifier strings to be byte-exact against; it is a human-readable name table. The acceptance criterion and its test are not materializable as written — there is no spec-side string set for the test to compare to.
- **Discriminator that classifies as Class 2:** (a) — affects substantive content of the Phase-6 plan unit (its acceptance-criterion precision and test specification); resolution is a plan-internal correction of AC1's case claim and the byte-exact test's reference target, no upstream-artifact change required.
- **Evidence:** Spec §13.1 lines 842–854 (name-only table); plan U-AS-28 Signatures lines 1431–1435 (SCREAMING_SNAKE enum); plan U-AS-28 AC1 line 1456; plan U-AS-28 test list line 1465.
- **Axis-domain attack engaged:** AS — Anthropic-primitive enumeration precision.
- **Anti-fabrication attack engaged:** A2 (acceptance criterion asserts a spec property — verbatim machine identifiers — the spec does not contain).
- **Decision-claim label:** *decided* — the contradiction between AC1's "kebab-case" and the SCREAMING_SNAKE Signatures block is plain in the unit's own text.
- **Resolution path:** §2.7.6 **Class 2 (operator-decision)** fork. Reconcile U-AS-28 AC1's case claim with the Signatures block, and re-scope the `byte_exact_per_spec_13_1` test to a determinable reference (e.g., cardinality + enumeration-order against §13.1's row order, since §13.1 has no string identifiers). `implementation-planner` applies after operator confirms intent.

### F2-03 — U-AS-08 `CallSiteContext.mcp_trust_level` is consumed by `sandbox_tier_floor` but the spec §2.2 call site sources no trust level

- **Location:** `Implementation_Plan_Action_Surface_v1.md` U-AS-08 Signatures `record CallSiteContext { ... mcp_trust_level: Optional<MCPTrustLevel> ... }`; U-AS-08 AC1 cites the C-AS-02 §2.2 five-floor `max()`.
- **Defect:** U-AS-08's `CallSiteContext` carries `mcp_trust_level`, and U-AS-08 must pass `sandbox_tier_floor`'s arguments at the composition site. This is the consumer side of F3-01: the plan threads `mcp_trust_level` through `CallSiteContext` so U-AS-06's five-parameter `sandbox_tier_floor` can be called, but the spec §2.2 formula's `call_site_context` never names a trust-level field. The plan is internally consistent (U-AS-06 and U-AS-08 agree) but jointly diverges from the spec §2.2 call site. Flagged separately from F3-01 because the locus is U-AS-08's `CallSiteContext` schema, an in-scope unit.
- **Discriminator that classifies as Class 2:** (a) — affects substantive content of the U-AS-08 unit; once F3-01's spec reconciliation lands, this resolves consistently. If F3-01 resolves toward the spec keeping a four-argument `sandbox_tier_floor`, then U-AS-08's `mcp_trust_level` field becomes the defect locus and this escalates to Class 3.
- **Evidence:** U-AS-08 `CallSiteContext` plan lines 424–434 (`mcp_trust_level` field at line 430); spec §2.2 lines 192–204 (no trust-level field on `call_site_context`).
- **Axis-domain attack engaged:** AS — call-site-context schema vs spec composition formula.
- **Decision-claim label:** *proposing* — classification is contingent on F3-01's resolution direction; both readings stated.
- **Resolution path:** Resolve jointly with F3-01 at the Phase-5 spec revision-pass. No independent §2.7.6 fork; U-AS-08's clearance is gated on F3-01's clearance.

### F2-04 — U-AS-08 / U-AS-10 reference `ToolContext` at typed signature positions with no declaring carrier; U-AS-02 (landed) declared it only as Inputs prose

- **Location:** `Implementation_Plan_Action_Surface_v1.md` U-AS-10 Signatures `lookup_cell_with_forcing(surface, blast_radius, ctx: ToolContext)` and Inputs line 526; U-AS-02 (landed) Signatures `forced_tier(ctx: ToolContext)` line 165 and Inputs line 148.
- **Defect:** `ToolContext` is used as a typed parameter by U-AS-02 (`forced_tier`) and U-AS-10 (`lookup_cell_with_forcing`), but no unit's Signatures block declares a `record ToolContext`. U-AS-02's Inputs prose describes its fields ("carrying `computer_use_bound: bool` and `code_execution_beta_invoked: bool`") but the field set is never given record form. U-AS-10 Depends-on = [U-AS-01, U-AS-02, U-AS-04, U-AS-11]; U-AS-02 is in the cone but does not *declare* the type. This is an undeclared-type instance like F3-03, but isolated here at Class 2 because U-AS-02 has already landed — meaning either the coding lane inline-materialized `ToolContext` or silently absorbed the gap (X-AL-3 risk). The reviewer is READ-ONLY and does not inspect landed source to resolve this; it is surfaced as an open retrospective observation.
- **Discriminator that classifies as Class 2:** (a) — affects substantive content of U-AS-10 (a not-yet-landed in-scope unit); resolution is a plan-internal carrier declaration. The retrospective concern about U-AS-02's landing is an informational observation, not itself a current-phase content defect of an in-scope unit.
- **Evidence:** Grep returns no `record ToolContext` declaration; consumption at plan lines 148, 165, 526, 542.
- **Axis-domain attack engaged:** AS — untyped tool I/O.
- **Decision-claim label:** *open* — whether `ToolContext` is intended as a distinct record or as an alias/subset of U-AS-08's `CallSiteContext` cannot be determined from the plan text; operator intent required.
- **Resolution path:** §2.7.6 **Class 2 (operator-decision)** fork for U-AS-10. Operator confirms `ToolContext`'s intended declaration locus and whether it is distinct from `CallSiteContext`; `implementation-planner` adds the carrier. Separately, log a §2.7.6 **Class 3 (informational)** observation that U-AS-02 landed against an undeclared `ToolContext` — recommend a retrospective check that the landed materialization is not a silent absorption.

---

## Class 1 findings (minor — drift)

### F1-01 — U-AS-06 acceptance criterion 1 enumerates the §2.3 lookup as "ten rows" but expands the remote-MCP rows into four sub-items

- **Location:** `Implementation_Plan_Action_Surface_v1.md` U-AS-06 acceptance criterion 1, "ten rows per C-AS-02 §2.3 table verbatim (… STDIO MCP, remote MCP L0/L1/L2/L3, …)".
- **Defect:** Spec §2.3 has exactly ten rows, but it collapses remote-MCP trust levels 1 and 3 into a single row ("trust level 1 (signed-pinned) OR trust level 3 (allow-with-audit)"). AC1's parenthetical "remote MCP L0/L1/L2/L3" reads as four distinct rows, which would make twelve. The row count claim ("ten") is correct; the parenthetical enumeration is loose and could mislead an implementer into authoring four separate remote rows. The test list does correctly cover L1 and L3 with separate test invocations against the single combined row.
- **Resolution:** Inline fix in the affected plan unit — tighten AC1's parenthetical to reflect the spec §2.3 L1+L3 row collapse. §2.7.6 Class 3 (informational); non-blocking.

### F1-02 — U-AS-28 Signatures `record SecretScope { ... }` placeholder ellipsis carried in U-AS-20

- **Location:** `Implementation_Plan_Action_Surface_v1.md` U-AS-20 Signatures `record SecretScope { ... }  // serialization deferred`.
- **Defect:** `SecretScope` is declared with an ellipsis body and a "serialization deferred" comment. The spec §5.1 (line 363) types `scope` as `SecretScope` and §5.4's deferred-discretion note explicitly defers `SecretScope` serialization format. So the deferral is spec-sanctioned — but the unit declares `SecretScope` as a *carrier* with no field set, and downstream units (U-AS-22, U-AS-24, U-AS-30) consume `SecretScope` as a typed field. The placeholder is acceptable per the spec's deferral, but the unit should state explicitly that the field set (not only serialization) is deferred, so a downstream consumer does not read `{ ... }` as "fields TBD by this unit".
- **Resolution:** Inline fix in U-AS-20 — make the deferral scope explicit (serialization deferred per spec §5.4; field set declared minimally). §2.7.6 Class 3 (informational); non-blocking. The spec sanctions the deferral, so no upstream fork.

---

## Findings considered and rejected (transparency)

1. **U-AS-08 `MCPTrustLevel` carrier check** — `CallSiteContext` and `FloorInterfaces` reference `MCPTrustLevel`. `MCPTrustLevel` is declared by U-AS-06, which is a declared predecessor of U-AS-08 (Depends-on includes U-AS-06). Carrier resolves in-cone. No finding.
2. **U-AS-08 `AssignedTierReason` / `SandboxTierCompositionResult` self-declaration** — both declared in U-AS-08's own Signatures block; consumed downstream (U-AS-16, U-AS-17 cite `AssignedTierReason`). No undeclared-type gap. No finding.
3. **U-AS-28 `FilesystemPathContract` carrier check** — `skills_loads_from_filesystem_path() -> FilesystemPathContract`; `FilesystemPathContract` arrives cross-axis via U-IS-01 / U-IS-02 `FILESYSTEM_PATH_CONTRACT_EXPORT`, and both U-IS-01 and U-IS-02 are in U-AS-28's Depends-on. Carrier in-cone. No finding (contrast `AnchorCitation`, F3-03, which has no carrier).
4. **Dependency-graph acyclicity** — U-AS-06/08/10/20/28 Depends-on lists trace only to lower-or-foundational units (U-AS-01..U-AS-11 / U-IS-01..02); the §3.5 DAG places them at L1–L3; no cycle detectable across the five units. No finding.
5. **U-AS-28 §13.2 44-cell matrix cardinality** — AC5 claims "exactly 44 cells per §13.2"; spec §13.2 is 11 primitives × 4 workload classes = 44. Arithmetic and the per-row population claims (AC6) match the spec table. No finding.
6. **U-AS-28 persona / ADR trace** — C-AS-13 cites ADR-D3 v1.2; §13.2 cells trace to ADR-D3 §1.2; the eleven-primitive count aligns with the spec's documented F-AS-01 closure (nine→eleven). ADR-coverage and persona-trace checks pass. No finding.
7. **U-AS-20 ADR-F5 commitment honoring** — `SecretRef` opacity (AC2–4), `TIER_RESOLUTION_TABLE` four entries (AC5), T-perm-2 pole expression (AC6) all trace to spec §5.2 / §5.4 and ADR-F5 v1.1 §"Permanent tensions engaged". Contract-vs-ADR honoring holds (the signature divergence is F3-02; the rest is faithful). No additional finding.
8. **U-AS-10 12-cell cardinality** — AC1 claims exactly 12 cells (3×4); spec §9.1 matrix is 3 deployment surfaces × 4 blast-radius tiers = 12. Cardinality faithful. No finding (the provider-class *identifier* mismatch is F2-01; the cell count is clean).
9. **U-AS-06 REFUSE sentinel structural distinctness** — AC3 + the `SandboxTierFloorResult` enum (`RESOLVED(SandboxTier)` / `REFUSE`) make REFUSE structurally distinct from any `SandboxTier` value, matching spec §2.3 row 4 ("sentinel"). Domain-precision concern (tier-vs-sentinel conflation) handled cleanly. No finding.
10. **U-AS-08 forced-tier precedence** — AC2 + AC4 thread `forced_tier` from U-AS-02 with `COMPUTER_USE_FORCING` / `CODE_EXECUTION_FORCING` causes ahead of the `max()`; matches spec §2.3 forcing-row precedence and §9.3. No finding.
11. **A8 framing-contamination sweep** — none of the five units commits a persona, stack, or deployment value the workspace `CLAUDE.md` framing leaves uncommitted; deployment surfaces appear as the spec's `DeploymentSurface` enum (a committed AS contract), not as a single-surface assumption. No framing-contamination finding.
12. **U-AS-06 / U-AS-13 alignment claim** — U-AS-06 AC6 defers C-AS-02 §2.3 ↔ C-AS-10 §10.1 alignment verification to an integration test at U-AS-13; the cross-reference is internally consistent with U-AS-13's stated alignment verifier. No finding (out-of-buffer unit, noted for the next buffer).

---

## Disposition

Three §4.1 Class 3 findings are present (F3-01, F3-02, F3-03), so the cluster does **not** clear. Per §4.1, Class 3 findings route to upstream-phase artifact revision; mapped to the §2.7.6 Phase-7 execution-fork scale, each Class 3 finding here is a **Class 1 (halt-execution)** fork — the affected unit cannot land until the design-phase artifact (AS spec C-AS-02 §2 / C-AS-05 §5, or the AS plan §3.4 dependency declarations) is revised and re-cleared. The four Class 2 findings map to §2.7.6 Class 2 (operator-decision) forks; the two Class 1 findings map to §2.7.6 Class 3 (informational) and are non-blocking.

**Systemic pattern (SKILL.md §6).** F3-03 plus F2-04 establish a recurring finding shape across ≥4 units (U-AS-06 `ToolMetadata`; U-AS-08 `TaintState`, `MCPServer`; U-AS-10 / U-AS-02 `ToolContext`; U-AS-28 `AnchorCitation`): **auxiliary record/enum types referenced at typed signature positions with no declaring carrier unit and no dependency-graph edge.** This is not a per-unit slip; it is a structural gap in the AS plan v1's signature-completeness discipline. Recommended resolution scope is a single Phase-6 AS plan revision-pass that either (a) adds explicit carrier units / carrier declarations for the auxiliary types with dependency-graph edges, or (b) documents an inline-auxiliary-type materialization discipline (the type is materialized inline at first-consuming unit, with the §3.4 table noting it) — rather than five independent inline fixes. This is the higher-leverage path and addresses the source defect. The known prior fork U-AS-07 (`required_secrets` element type, fork-queue item 9) is the same shape; the pattern predates this buffer.

**Severity-distribution self-audit.** 3 Class 3 / 4 Class 2 / 2 Class 1 — not skewed to either extreme. The high block rate (3 of 5 units BLOCKED) is calibrated, not inflated (FM-A check): the AS plan has documented Tension-002/003/004 antecedents, the §4A verbatim-divergence arc, and a known fork-queue; each Class 3 finding here carries explicit byte-level evidence (a spec line number and a plan line number that disagree). The reviewer did not escalate any finding past its discriminator: F2-01, F2-02, F2-03, F2-04 each name discriminator (a) and stay at Class 2; F1-01, F1-02 are genuine drift.

---

## Pipeline clearance verdict

Per-unit verdict for `pipeline-cleared-queue.md` / `pipeline-fork-queue.md`:

| Unit | Verdict | Blocking fork |
|---|---|---|
| **U-AS-06** | **BLOCKED** | §2.7.6 Class 1 (halt) — F3-01 (`sandbox_tier_floor` 5th parameter absent from spec §2.3 contract signature; Phase-5 AS spec revision-pass required) + F3-03 (`ToolMetadata` undeclared, no carrier in cone) |
| **U-AS-08** | **BLOCKED** | §2.7.6 Class 1 (halt) — F3-03 (`TaintState`, `MCPServer` undeclared, no carrier in cone). Also gated transitively on F3-01 via F2-03 (`CallSiteContext.mcp_trust_level`) |
| **U-AS-10** | **BLOCKED** | §2.7.6 Class 2 (operator-decision) — F2-01 (`PROCESS_FS_OVERLAY` not a member of the landed `SandboxProviderClass` enum) + F2-04 (`ToolContext` undeclared carrier). No §2.7.6 Class 1 fork, but two operator decisions are materialization preconditions — does NOT enter the cleared queue until resolved |
| **U-AS-20** | **BLOCKED** | §2.7.6 Class 1 (halt) — F3-02 (`fetch_secret` 3-parameter signature vs spec §5.1 2-parameter contract; AC1 self-contradictory verbatim claim; operator picks spec-revision vs plan-revision reading) |
| **U-AS-28** | **BLOCKED** | §2.7.6 Class 1 (halt) — F3-03 (`AnchorCitation` undeclared, no carrier in cone). Also §2.7.6 Class 2 — F2-02 (AC1 "kebab-case" / "byte-exact per §13.1" not materializable) |

**0 of 5 units CLEARED.** All five route to `pipeline-fork-queue.md`. U-AS-06, U-AS-08, U-AS-20, U-AS-28 carry §2.7.6 Class 1 (halt-execution) forks — design-phase artifact revision required before landing. U-AS-10 carries §2.7.6 Class 2 forks only (no halt fork) but both are materialization preconditions, so it also does not enter the cleared queue until operator-resolved. The systemic undeclared-type pattern (F3-03 / F2-04) is the highest-leverage item: a single Phase-6 AS plan revision-pass clears the F3-03 component of U-AS-06 / U-AS-08 / U-AS-28 and the F2-04 component of U-AS-10 together.

---

*Filed by the review-ahead lane (`harness-adversarial-reviewer`, Phase-7 pre-implementation review mode), 2026-05-15. Read-only with respect to all `design-substrate/` artifacts, `CLAUDE.md` files, plans, specs, and source. No canonical artifact was edited. Findings classified, not absorbed (X-AL-3).*
