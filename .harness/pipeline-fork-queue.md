# Pipeline — Fork Queue

*Forks awaiting operator decision. The review-ahead lane (and the coding lane,
on its own spec-read) appends here; neither edits canonical artifacts
(`review-pipeline.md` §3). Operator resolves; an applicator skill (`spec-writer`
/ `implementation-planner`) applies; the reviewer re-checks. Updated 2026-05-15.*

## Open forks — operator decision owed

Items 1–8 dispositioned by the pilot review-ahead pass
(`.harness/adversarial_review_cp_od_v25_reclearance.md`, 2026-05-15). The
reviewer classifies and recommends a resolution *shape* — it does not decide.
Item 9 surfaced by the coding lane's own spec-read.

| # | Item | Class (§4.1 / §2.7.6) | Blocks | Resolution shape |
|---|---|---|---|---|
| 1 | **U-CP-43** — 4-axis `GateLevelInput` diverges from CP spec §19.1: `per_tool_gate_level` absent, `deployment_surface` plan-added, `MCP_TRUST`/`DEPLOYMENT_SURFACE` floors spec-silent | Class 3 / **Class 1 halt** | U-CP-43 | spec-silence design gap — operator decision on whether §19.1 extends or the plan conforms; routes to CP spec or CP plan revision |
| 2 | **U-OD-09** — acc #2 Required/Conditional tier split has no OD spec §7.1 basis | Class — / **Class 1 halt** | U-OD-09 | spec-silence — operator decides spec basis or plan conforms |
| 3 | **U-CP-08** — `FallThroughCause` design gap (silent H_T design extension if invented at the unit) | — / **Class 1** | U-CP-08 | back-flow: CP spec/ADR — needs the cause taxonomy committed upstream |
| 4 | **U-CP-23** — single-vs-dual `default_pattern` structural mismatch | Class 2 / **Class 2** (non-halting) | — (U-CP-23 clears) | operator picks the structural reading; non-blocking for landing |
| 5 | **U-CP-11** — LEASE naming call | — / **Class 2** | U-CP-11 | operator naming decision |
| 6 | **U-OD-28** — `CollectorPlacement` / §20.1 surface — conformance target undetermined | — / **Class 2** *(proposing)* | U-OD-28 | operator resolves the §20.1 conformance target |
| 7 | **U-OD-29** — plan `TIER_0..TIER_3` diverges from ADR-D2 §1.7.1 canonical `{tier-1..tier-4}`; the plan's §1.2 citation is also wrong (§1.2 is the provider-class enum) | — / **Class 1** (authority-chain-determinate) | U-OD-29 | conform plan to ADR-D2 §1.7.1 — determinate, like §4A; operator-accept → `implementation-planner` revision |
| 8 | **F1-01** — U-CP-22 v2.5 acc #3 silently SCREAMING_SNAKE_CASE-renders §10.3 workload identifiers without declaring the edit in §0.3 (stem-match preserved) | Class 1 / **Class 3** (informational) | — | inline doc-hygiene fix to CP plan v2.5 §0.3 change-note |
| 9 | **U-AS-07** — §3.1 signature types `ToolContract.required_secrets` as final `List<SecretAllowlistEntry>`, but `SecretAllowlistEntry` is declared by U-AS-22 (which depends on U-AS-07); U-AS-22 line 1125 says it "populates the previously-empty-shape field at U-AS-07" — the plan never specifies U-AS-07's interim materialization shape | — / **Class 2** *(provisional — coding-lane classification; AS not yet under review-ahead)* | U-AS-07 | operator picks U-AS-07's interim `required_secrets` element-type shape (empty-only / placeholder / U-AS-22 redefines model); routes to AS plan clarification |
| 10 | **U-AS-12** — acc #2 says `SOLO_DEVELOPER → PERMITTED_APPEND_ONLY at any cell` and claims "matches spec §9.4 verbatim"; AS spec §9.4 + §12.2 say solo-developer override is permitted "at **non-compliance cells**" — and "compliance cell" is not a function of `(DeploymentSurface, BlastRadiusTier)`, so `override_scope` cannot evaluate it from its declared inputs | — / **Class 2** *(provisional, proposing — two readings)* | U-AS-12 | operator picks the reading: (A) "non-compliance cells" = "any cell" for the solo-developer persona (plan correct, only the "verbatim" claim is loose) vs (B) plan over-permits and the function needs a compliance-status input; routes to AS plan/spec clarification |
| 11 | **U-AS-06** — F3-01: `sandbox_tier_floor` adds a 5th param (`mcp_trust_level`) absent from spec §2.2/§2.3 contract; F3-03: consumes undeclared `ToolMetadata` | Class 3 / **Class 1 halt** | U-AS-06 | covered by Q1 systemic AS-plan audit; conform-or-extend operator decision |
| 12 | **U-AS-08** — F3-03: `CallSiteContext` field types consume undeclared `TaintState`, `MCPServer` | Class 3 / **Class 1 halt** | U-AS-08 | covered by Q1 systemic AS-plan audit |
| 13 | **U-AS-10** — F2-01 + F2-04: materialization preconditions unmet | Class 2 / **Class 2** | U-AS-10 | covered by Q1 systemic AS-plan audit |
| 14 | **U-AS-20** — F3-02: `fetch_secret` declares a 3rd param (`tier`) while AC1 claims §5.1 "verbatim"; spec §5.1 contract is 2-param — internally contradictory verbatim claim | Class 3 / **Class 1 halt** | U-AS-20 | covered by Q1 systemic AS-plan audit |
| 15 | **U-AS-28** — F3-03: consumes undeclared `AnchorCitation`; + F2-02 | Class 3 / **Class 1 halt** | U-AS-28 | covered by Q1 systemic AS-plan audit |
**Items 16/17/18 SUPERSEDED** by the Q2 CP materializability audit
(`.harness/materializability_audit_cp_plan.md`, 2026-05-15) — the canonical CP
materializability systemic-tension record. Q2 verdict: 20 CLEARED · 12 CONFORM
· 24 FORK across all 56 CP units, 3 systemic patterns (C: `AttributeValueType`/
`Cardinality` no-carrier; D: ≥25 undeclared auxiliary types; E: `[U-CP-00]`
edges recorded-not-materialized). U-CP-01/10/47 fold into Patterns C/D. The
items below are kept for traceability; the audit report is canonical.

| 16 | **U-CP-10** — `LifecycleEventClassMetadata.parent_relation` is typed `ParentRelation`, a type declared by no CP-plan unit (v2.1 or v2.4), referenced by no acceptance criterion, with no spec §5.1 basis. Undeclared-type fork (Tension-003 / U-AS-07 shape). *Pilot-CLEARED — the pilot's §4A-verbatim mandate did not run a materializability sweep.* | Class 3 / **Class 1 halt** | U-CP-10 | operator decision on `ParentRelation` carrier + value set, or drop the plan-invented field; routes to CP plan revision |
| 17 | **U-CP-01** — `RoutingAttributeSchema` carries `value_type` + `cardinality` fields, but cited spec §1.4 routing.* table has columns {Attribute, Type, Semantic, Source} — **no cardinality column** (sibling §9.1 engine.* table does have one). acc#1 claims "per §1.4 verbatim"; `cardinality` cannot be transcribed. *Pilot-CLEARED.* | Class 2 / **Class 2** *(proposing)* | U-CP-01 | operator picks: (A) `cardinality` is implementer-discretion (land with inferred OTel tokens) vs (B) needs §1.4 spec extension vs (C) drop the field from the schema |
| 18 | **U-CP-47** — `ValidatorFailAttributeSchema` consumes `AttributeValueType` + `Cardinality`, shared CP-axis enums declared by U-CP-01 (and assumed by U-CP-11). U-CP-47 `Depends on: [U-AS-03]` only — no dep-graph edge to any carrier of those types. Shared-type-no-carrier defect (the WorkloadClass→U-CP-00 shape). *Pilot-CLEARED.* | Class 3 / **Class 1 halt** | U-CP-47 | operator decision on the `AttributeValueType`/`Cardinality` carrier unit (candidate: a foundational CP or harness-core unit, like U-CP-00 for `WorkloadClass`) + dep-edge additions at every consuming unit |

**Note on items 1, 2, 3:** the pilot reviewer confirmed these are pre-existing
spec-silence design gaps the plans themselves declared and carried — NOT
defects introduced by the §4A conformance pass. The conformance pass correctly
conformed everything authority-chain-determinate and correctly refused to
silently absorb the spec-silence items (X-AL-3 honoured).

**Pattern — AS plan v1 carries the verbatim-divergence disease systemically
(items 9–15).** The §4A systemic verbatim audit covered the **CP + OD** plans
only; **AS plan v1 was never verbatim-audited**. Evidence is now decisive:

- Coding lane: 2 of 4 attempted AS units forked (U-AS-07, U-AS-12).
- Review-ahead AS buffer-1 (`adversarial_review_as_buffer_1.md`): **0 of 5
  units cleared** — 3 Class 3, 4 Class 2, 2 Class 1 findings. The reviewer
  surfaced a **systemic pattern** (F3-03 + F2-04): the plan references
  auxiliary record/enum types (`ToolMetadata`, `TaintState`, `MCPServer`,
  `AnchorCitation`, `ToolContext`) at signature positions with **no carrier
  unit and no dependency-graph edge** — the Tension-003 / U-AS-07 shape,
  recurring across ≥4 units.
- Retrospective concern: U-AS-02 (landed, operational-minimum) may have
  declared `ToolContext` against a silently-absorbed type — the Q1 audit
  should check whether the landed U-AS-02 needs revisiting.

**Q1 systemic AS-plan audit COMPLETE** — `.harness/verbatim_audit_as_plan.md`
is the canonical AS systemic-tension record (supersedes the per-unit framing of
items 9–15; no further per-unit AS records filed). Verdict: 18 CLEARED · 3
CONFORM · 12 FORK across all 33 units. Two systemic patterns — Pattern A
(verbatim divergence) + Pattern B (undeclared auxiliary types, ≥11 types).
**Resolution: one `implementation-planner` 2-sub-pass AS-plan revision**
(Pattern A conformance + Pattern B carrier declaration / dep-graph completion)
**plus a `spec-writer` C-AS-02 §2.2/§2.3/§11.1 reconciliation** for the genuine
`sandbox_tier_floor` spec under-specification. Operator-ratified, same as §4A.
**U-AS-02 (landed) carries a retrospective Class-3** — needs an operator-
authorized check that its inline `ToolContext` is field-complete vs the carrier
shape the revision will give it.

**Pattern — the materializability axis spans all four plans (items 16–18).**
The §4A audit checked **verbatim conformance** (does a plan signature transcribe
its cited spec section). It did NOT check **materializability** (is every type
at a signature position declared by a reachable unit; does the unit's signature
have a complete spec basis). The pilot's CLEARED verdicts inherited that narrow
mandate — `CLEARED` meant "no §4A verbatim divergence", NOT "ready to land".
The coding lane's own per-unit spec-read (defense-in-depth) caught 3
materializability forks (U-CP-01/10/47) among 5 pilot-cleared CP units it
checked. Combined with AS (items 9–15) and the in-flight Q1 audit, the
materializability defect class is now confirmed in CP and AS and is plausible
in OD. **Recommended: a materializability re-sweep of the 15 pilot-cleared
CP/OD units** (enumerate every type consumed at signature positions; confirm a
reachable carrier) before the cleared-queue is treated as durable —
operator-scoped decision, see report.

## Resolved forks

| Item | Resolution | Date |
|---|---|---|
| Tension 001 — C-IS-03 §3 "four" vs 5 rows | spec fixed in-CLI; block cleared | 2026-05-15 |
| Tension 002 — TopologyPattern enum 3-way divergence | operator signed off Set 2 (spec C-CP-10 §10.1); conformed at 4 loci | 2026-05-15 |
| Tension 003 — `WorkloadClass` undeclared | declared in `harness-core` via new U-CP-00 | 2026-05-15 |
| Tension 004 — U-OD-04 span schema divergence | subsumed into OD §4A audit; conformed in OD plan v2.5 | 2026-05-15 |
| Class 1 — U-CORE-01 `WorkflowEvent` payload unmaterializable | operator ruled carrier-thin; payload struck; harness-core plan v1.0→v1.1; U-CORE-01 landed | 2026-05-15 |

## Open follow-ups

| Item | Detail | Owed at |
|---|---|---|
| F-2 (from `class_1_tension_u_core_01_workflow_event.md`) | `Implementation_Plan_Control_Plane_v2_6.md` §0 spec-inventory line references "`WorkflowEventClass`/`WorkflowEvent`" as U-CORE-01-declared; the `WorkflowEvent` token is now stale (mechanical back-reference strike). | Next CP plan touch — likely when U-CP-10 lands fresh or the carrier-gated re-point sweep reaches CP-side recheck. |
