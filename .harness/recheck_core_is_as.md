# Re-check RC-A — harness-core / IS / AS conformed plans

*Review-ahead re-check pass RC-A. Phase-7 pre-implementation re-clearance of the
`Proposed`-status R-series-conformed plans. READ-ONLY. Authored 2026-05-15.*

Scope: confirm the R1 / R2 / R3+R3.1 conformance closed every fork its audit
named, and introduced no new undeclared type, dependency cycle, or
signature-vs-spec gap.

- harness-core — `Implementation_Plan_Harness_Core_v1_0.md` (U-CORE-01) — IN PROGRESS
- IS — `Implementation_Plan_Information_Substrate_v2_3.md` — IN PROGRESS
- AS — `Implementation_Plan_Action_Surface_v1_2.md` — IN PROGRESS

---

## Plan 1 — harness-core (U-CORE-01)

`Implementation_Plan_Harness_Core_v1_0.md` — genesis plan, one unit U-CORE-01.
This is a new plan with no audit fork list of its own; the check is
self-consistency + carrier-map fidelity + spec trace.

**12 declared types — trace verification.**

| Type | Cited contract | Verified |
|---|---|---|
| `DeploymentSurface` (enum, card. 3) | C-AS-09 §9.1 | ✅ Spec §9.2 12-cell matrix rows `local-development / self-hosted-server / managed-cloud` confirmed verbatim |
| `PersonaTier` (enum, card. 3) | C-AS-09 §9.4 + ADR-D5 v1.3 §1.5 | ✅ Spec §9.4 ladder `solo-developer / team-binding / multi-tenant-compliance` confirmed verbatim |
| `ActionID` (newtype) | C-IS-05 §5 | ✅ F2 entry-shape identifier field, traced to concept |
| `EntryID` (newtype) | C-IS-05 §5 | ✅ state-ledger entry identifier |
| `WorkflowID` (newtype) | C-CP-05 §5 | ✅ |
| `StepID` (newtype) | C-CP-05 §5 | ✅ |
| `ThreadID` (newtype) | C-CP-05 §5 | ✅ |
| `StageID` (newtype) | C-CP-13 §13.4 | ✅ carrier map line 142 names `StageID` as U-CORE-01 identity alias |
| `ContractID` (newtype) | C-AS-03 §3 / C-CP-01 §1 | ✅ |
| `UnitId` (newtype) | (none — plan-internal) | ✅ Q-R1-5 operator-ratified plan-internal, explicitly declared non-traced |
| `ReferenceToUnit` (newtype) | (none — plan-internal) | ✅ Q-R1-5; carrier map line 144 names it as U-CORE-01 `UnitId`-family alias |
| `WorkflowEvent` (model) + `WorkflowEventClass` (enum, card. 8) | C-CP-05 §5.1, §5.2 | ✅ CP spec §9.1 confirms "the eight events per C-CP-05 §5.1"; 8 values verbatim |

All 12 types trace to a committing contract or are explicitly operator-ratified
plan-internal (Q-R1-5). No type lacks a basis. The carrier map (line 206) named
the 7-alias + 2-enum core; the final plan adds `StageID` + `ReferenceToUnit`
(both individually carrier-map-named, lines 142/144) and `WorkflowEvent` (Q-R1-2
operator-ratified) — all within the ratified R1 scope, not silent additions.

**`Depends on: (none)` — correct.** U-CORE-01 imports nothing; it is a pure
source node (Level 0) beside the landed U-CP-00. The §3 dependency graph is
trivially acyclic — a source node with inbound-only edges cannot form a cycle.

**No new defect.** No undeclared type is consumed at any signature position
(all signatures are self-declared). No dependency cycle. No signature without
spec basis — the two unbased aliases (`UnitId`/`ReferenceToUnit`) are
explicitly flagged plan-internal and operator-ratified, which is the correct
disposition, not a defect.

**Cross-plan honesty.** The `WorkflowEvent` ↔ U-CP-10 `LifecycleEventClass`
double-declaration is correctly flagged in the plan body as a hand-off to R4 —
this is the carrier map's intended multi-declaration target, surfaced not
absorbed. R4's reconciliation is out of RC-A scope (CP plan); for harness-core
the flag itself is correct conduct.

**Verdict: CLEARED.** U-CORE-01 is self-consistent, all 12 types trace,
`Depends on: (none)` is correct, no new defect. Clean.

## Plan 2 — IS v2.3

`Implementation_Plan_Information_Substrate_v2_3.md` vs audit fork list
(`materializability_audit_is_plan.md`: 5 FORK U-IS-02/05/06/12/14 + 1 CONFORM
U-IS-17) and revision `revision_R2_is_plan.md`.

**Audit fork list — closure verification.**

| Fork unit | Undeclared type(s) | v2.3 resolution | Carrier reachable? |
|---|---|---|---|
| U-IS-02 | `WorkflowClass`, `DeploymentSurface` | `WorkloadClass` via `[U-CP-00]`; `DeploymentSurface` via `[U-CORE-01]`; spelling unified `WorkflowClass`→`WorkloadClass` | ✅ U-CP-00 landed; U-CORE-01 declares `DeploymentSurface` (verified Plan 1) |
| U-IS-05 | `WorkflowClass`, `DeploymentSurface` | same two `[U-CP-00]` / `[U-CORE-01]` edges added | ✅ |
| U-IS-06 | `ContractID`, `GitRepository`/`CommitRange`/`CommitId` | `ContractID` via `[U-CORE-01]`; git trio declared **IS-internal in-unit** in U-IS-06 Signatures block per Q-R2-1 operator override | ✅ `ContractID` in U-CORE-01 alias module (verified Plan 1); git trio now has an in-unit declaration site |
| U-IS-12 | `WorkloadClass` | `[U-CP-00]` edge added | ✅ |
| U-IS-14 | `WorkflowEvent` | `[U-CORE-01]` edge added (`WorkflowEvent` + `WorkflowEventClass`) | ✅ U-CORE-01 declares `WorkflowEvent` (verified Plan 1) |
| U-IS-17 (CONFORM) | `UnitId` | `[U-CORE-01]` edge added | ✅ U-CORE-01 declares `UnitId` (plan-internal alias, Q-R1-5) |

Every fork the audit named is closed. Each consuming unit declares the edge in
its `Depends on` line, and the §3.1 dependency-graph delta table records all
six. The git trio is the one fork resolved without a carrier edge — correctly:
the trio is declared in U-IS-06's own Signatures block (in-unit), which IS a
reachable carrier (the unit itself), per the Q-R2-1 operator decision.

**Carrier reachability — cross-plan consistency.** v2.3 cites `[U-CORE-01
(cross-axis: core)]` for U-CORE-01-resident types and unannotated `[U-CP-00]`
for `WorkloadClass` — matching the R1 edge-form discipline exactly (§3.1 edge-
form note). The carriers cited (`DeploymentSurface`, `WorkflowEvent`,
`ContractID`, `UnitId` in U-CORE-01; `WorkloadClass` in U-CP-00) all exist in
the harness-core plan / landed U-CP-00. No dangling `[U-CORE-01]` reference.

**No new defect.**
- No new undeclared type: §5 (new permanent Auxiliary-type carrier audit)
  enumerates every consumed type and its carrier; the table is complete and
  every row resolves.
- No dependency cycle: all six new edges are inbound-only to Level-0 source
  nodes (`U-CORE-01`, `U-CP-00`). A source node receiving inbound edges cannot
  form a cycle; the within-axis 17-node DAG is untouched. §3.1 acyclicity
  argument is sound.
- No signature without spec basis: the revised signatures only re-point
  parameter *types* to existing carriers; acceptance criteria and tests are
  preserved verbatim from v2.1. The `WorkflowClass`→`WorkloadClass` change is a
  spelling unification (the field at U-IS-12 already used `WorkloadClass`), not
  a semantic change. T2 confirmed the factor-out is faithful — no IS-spec
  extension.

**Spec alignment / X-AL-3.** v2.3 §0.5 correctly records that the audit's
reading (b) (X-AL-3 design extension → IS-spec back-flow) was discharged
upstream by T2 (FACTOR-OUT, decided): the IS spec §1 / C-IS-04 §4 commit the
"workflow class" / "deployment surface" concepts in prose. v2.3 introduces no
IS-spec / CXA / ADD revision — correct, no silent absorption.

**Residual (non-blocking, already declared).** AI-R2-1 (§0.6) — the landed
U-IS-02 source must be inspected and re-pointed to `harness-core` imports
before v2.3 is "fully consumed". This is correctly classified §2.7.6 Class 3
(informational) — a carrier-ordering artifact (the unit landed before its
carrier existed), explicitly flagged and auditable, not silent absorption. It
is a deferred coding-lane action, not a plan defect, and does NOT block plan
re-clearance. Q-R2-3 (U-IS-04 `ContractID` re-point) is likewise a declared,
deferred, non-blocking item.

**Verdict: CLEARED.** All 5 forks + 1 CONFORM closed against reachable
carriers; no new undeclared type, cycle, or unbased signature. AI-R2-1 and
Q-R2-3 are declared deferred coding-lane items (§4.1 Class 1 / §2.7.6 Class 3
informational), not blockers.

## Plan 3 — AS v1.2

`Implementation_Plan_Action_Surface_v1_2.md` (R3.1 micro-pass) over v1.1 (R3),
vs `verbatim_audit_as_plan.md` (12 FORK + Pattern A/B) and revisions
`revision_R3_as_plan.md` + R3.1.

**Two-stage revision.** R3 produced AS v1.1 (closed 8 of the 12 forks +
re-pointed the carrier-map types); R3.1 produced AS v1.2, which finalizes only
the 4 R3-deferred operator-decision units (U-AS-06/09/12/20) and preserves the
other 29 bodies verbatim from v1.1. Verification therefore spans both files.

**Audit fork list — closure verification (12 FORK).**

| Fork unit | Defect | Resolution | Verified |
|---|---|---|---|
| U-AS-02 | `ToolContext` undeclared (Pattern B) | `record ToolContext { computer_use_bound, code_execution_beta_invoked }` declared in-unit (R3) | ✅ v1.1 line 335 — declaration present |
| U-AS-06 | `sandbox_tier_floor` 4-vs-5 arg (Pattern A2); `ToolMetadata` undeclared (B) | 5-arg signature per AS spec v1.2/v1.3 §2.3; `ToolMetadata` declared in-unit; `MCPServer` re-homed here | ✅ v1.2 §5.2 — signature `(tool, deployment_surface, blast_radius_tier, mcp_transport, mcp_server)` matches conformed spec |
| U-AS-07 | `RawContractInput` undeclared; `SecretAllowlistEntry` carrier-ordering | `RawContractInput` declared in-unit; U-AS-07 forward-declares the `SecretAllowlistEntry` field set, `[U-AS-20]` edge | ✅ R3 §1.1; v1.1 |
| U-AS-08 | `AssignedTierReason` member-set diverges §15.2 (A1); `TaintState`/`MCPServer` undeclared (B) | enum conformed to spec §15.2 7-value set; `TaintState` declared in-unit; `MCPServer` re-homed to U-AS-06 (v1.2 §0.4) | ✅ v1.1 lines 420-424 — 7-value set with `PERSONA_TIER_FLOOR`/`SUB_AGENT_MONOTONIC_ASCENSION` |
| U-AS-09 | `sub_agent_sandbox_tier` 4-vs-5 arg (A2) | outer signature conformed to spec §11.1 6-param; inner `sandbox_tier_floor` 5-arg | ✅ v1.2 §5.2 |
| U-AS-10 | `PROCESS_FS_OVERLAY` not in carrier enum (A3) | AC2 re-stated against actual `SandboxProviderClass` §9.2 member set | ✅ R3 §2 |
| U-AS-12 | `override_scope` "any cell" vs §9.4 "non-compliance cells" (A1) | Reading A — AC-text wording fix only, no signature change | ✅ v1.2 §5.2 |
| U-AS-14 | `MCPServer` undeclared (B) | consumes `MCPServer` via `[U-AS-08]`→`[U-AS-06]` in-cone | ✅ R3 §1.1; v1.2 §0.4 |
| U-AS-20 | `fetch_secret` 2-vs-3 param (A2); `SecretScope` ellipsis body | 3-param `(name, scope, tier)` per ratified R1; `SecretScope` explicit field set | ✅ v1.2 §5.2 — matches conformed spec v1.3 §5.1 |
| U-AS-28 | `AnthropicPrimitive` "kebab-case verbatim" (A3); `AnchorCitation` undeclared (B) | AC1 re-stated; `AnchorCitation` declared in-unit | ✅ R3 §2/§1.1 |
| U-AS-30 | `ExtendedThinkingEffort`/`BatchApiCell`/`WorkloadManifestOverrides`/`Provider`/`ModelClass` undeclared (B) | all 5 declared in-unit (T2: all FACTOR-OUT, no design extension) | ✅ R3 §1.1 |

All 12 forks closed. Pattern A (verbatim divergence) resolved by conforming
plan to spec verbatim; Pattern B (≥11 undeclared types) resolved by in-place
declaration in each type's first-consuming AS unit — T2 verified every Pattern B
type is a spec-committed FACTOR-OUT (no X-AL-3 design extension, no IS-spec
back-flow). `DeploymentSurface`/`PersonaTier` moved to `harness-core` U-CORE-01;
U-AS-04 converted from declaring to importing (verified v1.1 lines 351-355 —
local enum declarations deleted, `[U-CORE-01]` edge added).

**Carrier reachability — cross-plan consistency.** AS v1.1 §7.1 adds explicit
per-consumer core edges `[U-CORE-01]` (U-AS-04/28/29/33) and `[U-CP-00]`
(U-AS-28/29/30) — every edge points at a declared carrier (verified Plan 1).
AS→IS cross-axis edges cite U-IS-07/08/09/10/11/01/02; R3 §7.3 / A-3 re-cite
the IS edges against revised IS units. Edge-form discipline (`(cross-axis:
core)` for imports, unannotated `[U-CP-00]`) matches R1/R2.

**No new defect.**
- No new undeclared type: the §5.4.2 exhaustive auxiliary-type audit (permanent
  section) enumerates every consumed type; the v1.2 delta closes the two
  former-deferred (C) entries and removes `MCPTrustLevel` (folded into
  `MCPServer`). Zero-(U) target reaffirmed.
- No dependency cycle — and one cycle risk was caught and resolved: v1.2 §0.4
  identifies that homing `MCPServer` at U-AS-08 would force a U-AS-06→U-AS-08→
  U-AS-06 cycle, and re-homes `MCPServer` to U-AS-06 (the upstream consumer).
  v1.2 §7.4 re-verifies the DAG. This is a defect the revision *prevented*, not
  introduced — sound conduct.
- No signature without spec basis: the `sandbox_tier_floor` 5-arg and
  `fetch_secret` 3-arg signatures both trace to the conformed AS spec (S2 →
  ADR-D2 v1.2 + spec v1.2 for `sandbox_tier_floor`; S3 → spec v1.3 §5.1 for
  `fetch_secret`). Confirmed against `Spec_Action_Surface_v1.md` §5.1 line 400
  (3-param) and §2.3 (5-arg row→argument keying).

**Spec alignment.** Verified: AS spec is now v1.3 (S3 landed the `fetch_secret`
2→3-param touch after AS v1.2 was authored). The `sandbox_tier_floor` and
`fetch_secret` signatures in AS v1.2 unit bodies match the conformed spec
v1.3 exactly.

**Residual (non-blocking, declared) — AS-R1: citation-token lag.** AS v1.2
unit bodies cite the AS spec at **v1.2** (`Implements: [C-AS-05 §5.1 ...]` —
v1.2 §0.6 action item A-5 explicitly notes "its `Implements` citation bumps to
the post-fix C-AS-05 version when the A-5 spec-writer pass lands"). The A-5
spec-writer pass (S3) has since landed — spec is v1.3. The plan's signature
*content* already matches v1.3; only the citation *token* lags. The S3 spec
change-note itself flags this: "AS plan U-AS-20 already applies the 3-parameter
`fetch_secret` body ... a follow-up token bump to v1.3 is owed". Classification:
§4.1 **Class 1 (documentation drift)** / §2.7.6 **Class 3 (informational)** —
the same disposition the IS plan's AI-R2-1 / Q-R2-3 carried. The pipeline doc
(`review-pipeline.md` line 154) already enumerates a "CLAUDE.md-family
version-token refresh" as carried cleanup. This is a stale citation token, not
a signature-vs-spec gap; it does not block coding-lane resume but should be
discharged at the next AS-plan touch.

**Other declared deferred items (non-blocking).** A-1 (U-AS-04 landed-source
re-check), A-2 (U-AS-02 landed-source retrospective), A-3 (AS→IS edge re-cite),
A-4 (§5.4.2 zero-(U) verification) — all carried-forward coding-lane / mechanical
actions, explicitly flagged in v1.2 §0.6, none a plan defect.

**Verdict: CLEARED (with one declared Class-1 residual).** All 12 forks closed
against reachable carriers; no new undeclared type, cycle, or unbased signature
— and the one potential cycle was caught and prevented by the revision. The
AS-R1 citation-token lag is a §4.1 Class 1 / §2.7.6 Class 3 informational
residual, already tracked as carried cleanup; it does not block re-clearance.

---

## Re-clearance verdict

| Plan | Verdict | Residual |
|---|---|---|
| **harness-core** (`Implementation_Plan_Harness_Core_v1_0.md`, U-CORE-01) | **CLEARED-for-coding** | None. Clean re-check — all 12 declared types trace, `Depends on: (none)` correct, no new defect. |
| **IS** (`Implementation_Plan_Information_Substrate_v2_3.md`) | **CLEARED-for-coding** | AI-R2-1 (landed U-IS-02 source re-point) + Q-R2-3 (U-IS-04 `ContractID` re-point) — both §4.1 Class 1 / §2.7.6 Class 3 informational, declared deferred coding-lane items, non-blocking. |
| **AS** (`Implementation_Plan_Action_Surface_v1_2.md` over v1.1) | **CLEARED-for-coding** | AS-R1: `Implements` citation tokens read AS spec v1.2; spec is now v1.3 (S3 landed). Signature content already matches v1.3. §4.1 Class 1 / §2.7.6 Class 3 informational; already tracked as carried version-token cleanup. Non-blocking. Plus A-1..A-4 declared deferred coding-lane / mechanical items. |

**All 3 plans are CLEARED for the coding lane to resume.** No §2.7.6 Class 1
(halt) fork survives in any of the three conformed plans. The R-series
materializability conformance closed every fork its audits named — the ~16
forks across the three plans (1 self-consistency check for core + 5 IS + 12 AS,
fork totals overlapping where audits double-count) all resolve against
reachable carriers (U-CORE-01, U-CP-00, or in-unit declarations). The R-series
introduced **no** new undeclared type, **no** dependency cycle, and **no**
signature without spec basis; the one cycle risk that arose (AS `MCPServer`
carrier home) was detected and prevented by the AS revision. The three residuals
are all §4.1 Class 1 / §2.7.6 Class 3 informational deferred items (landed-source
re-checks + a citation-token refresh) — declared, auditable, non-blocking, and
already tracked in the pipeline doc as carried cleanup. None is silent
absorption; none blocks re-clearance.

---

*Re-check RC-A — review-ahead lane, Phase-7 pre-implementation re-clearance.
READ-ONLY: no `design-substrate/` file, `CLAUDE.md`, plan, spec, audit, or
source modified (HARD WALL / X-AL-3). Findings classified, not absorbed.
Authored 2026-05-15 per `harness-adversarial-reviewer` SKILL.md Phase-7
pre-implementation review mode.*
