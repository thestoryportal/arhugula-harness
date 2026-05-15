# Adversarial Review — Plan-wide "verbatim"-claim audit, Operational Discipline plan

## Summary

- Mode: Phase-7 pre-implementation review (per `harness-adversarial-reviewer` SKILL.md §"Phase-7 pre-implementation review mode"), scoped to ONE systemic attack: the "verbatim"-claim divergence pattern across all 34 OD-plan atomic units.
- Corpus reviewed:
  - `design-substrate/Implementation_Plan_Operational_Discipline_v2_1.md` §3.1–§3.8 (U-OD-01 – U-OD-34 unit bodies; preserved verbatim into v2.2/v2.3/v2.4 except U-OD-20)
  - `design-substrate/Implementation_Plan_Operational_Discipline_v2_2.md` §3.5.3 (U-OD-20 v2.2 cascade Step 6b revision)
  - `design-substrate/Implementation_Plan_Operational_Discipline_v2_4.md` (revision-pass scope; U-OD-20 dependency amendment only)
  - `design-substrate/Spec_Operational_Discipline_v1_2.md` §1–§23 (§1–§13 preserved verbatim into v1.3; §14.1–§14.4 likewise)
  - `design-substrate/Spec_Operational_Discipline_v1_3.md` §0.1 (preserve-note attestation; §14.5.1–§14.5.4 amendment)
  - `.harness/adversarial_review_phase7_cp_od_preimpl.md` (Tension 002 / 004 / F3-01 reference shape)
- Date: 2026-05-15
- Finding count by §4.1 review-severity class: **Class 3: 9 · Class 2: 0 · Class 1: 0** (plus the already-filed Tension 004 = U-OD-04, a 10th unit of identical shape, not re-filed here).
- Highest-severity finding: **F3-04 / F3-09** (U-OD-32 / U-OD-33) — the bridging-arc transition table and the preservation-dimension set both claim "per §X verbatim" against sets that are wholesale-disjoint from the cited spec sections, with cardinality coincidentally matching.
- Disposition recommendation: **the systemic pattern is confirmed plan-wide.** Nine OD-plan units beyond U-OD-04 carry a "verbatim"-claim divergence of the Tension 002 / 004 shape. Per SKILL.md §6 (≥3 → systemic pattern) the threshold is crossed many times over; resolution scope is a single OD-plan revision-pass, not nine independent fork records.

**Class-taxonomy disambiguation (per SKILL.md title-section).** Findings use the **§4.1 review-severity** scale (Class 1 minor / Class 2 moderate / Class 3 severe — phase re-opening). Every finding below is a §4.1 **Class 3** review finding (discriminator (b) — resolution requires Phase-6 plan revision-pass against the cited Phase-5 spec contract). Each finding's *disposition* triggers a **§2.7.6 Class 1 (halt-execution)** Phase-7 execution fork — the unit cannot land because its acceptance criteria are internally contradictory (each claims "verbatim" against a signature/set/value that is not). This is structurally identical to Tension 002 and Tension 004.

---

## Method

For every unit U-OD-01 through U-OD-34: extracted every acceptance criterion / signature note asserting "verbatim", "per §X", "matches §X", or an exact cardinality ("exactly N ... per §X"); cross-checked each against the cited section in `Spec_Operational_Discipline_v1_2.md` (canonical-verbatim for §1–§13 per v1.3 §0.1; §14.1–§14.4 likewise). A claim is a **DIVERGENCE** when the unit's signature/value/cardinality does not match the cited spec section. A claim that matches is recorded in the clean-list.

A recurring shape: **cardinality-matches-but-set-diverges.** Several units assert "exactly N ... per §X verbatim" where N is correct but the *member set* is not the spec's member set. The cardinality coincidence masks the divergence; the "verbatim" word is false on contents. These are full divergences — the acceptance criterion claims a verbatim match that does not hold.

---

## Fork inventory table

| Unit | Claimed-verbatim surface | Divergence (plan says X / spec says Y) | §4.1 severity | §2.7.6 fork class |
|---|---|---|---|---|
| **U-OD-04** *(already filed — Tension 004; in inventory, not re-filed)* | acc. #1 span name "§4.1 verbatim"; #2 "6 operations ... verbatim"; #3 "exactly 4 tiers per §4.3 verbatim"; #6 base metric "§4.5 verbatim" | (a) span name `{op} {model}` 2-component / spec §4.1 `{op} {provider} {model}` 3-component; (b) `GenAiOperation` 6 values / spec §4.2 enumerates 7 (`generate_content` omitted); (c) `AttributeTier` 4 tiers incl. `CONDITIONAL` / spec §4.3 table 3 tiers (no Conditional); (d) `BASE_METRIC_NAME` `gen_ai.client.token.usage` / spec §4.5 `gen_ai.client.operation.duration` | Class 3 | Class 1 (halt) — **already filed as Tension 004** |
| **U-OD-02** | acc. #1 "`BackendClass` enumerates exactly 3 values per §2.1 verbatim" | plan `BackendClass` = 3 values (`OTEL_ONLY, DEDICATED_LLM_OBS_SINGLE_NODE, CLOUD_NATIVE_LLM_OBS`) / spec §2.1 line 173 states **"Eight cells; seven distinct classes"** and spec §1.2 backend-class enum lists 7+ classes (incl. `dedicated multi-node`, `OTel-to-vendor`, `self-hosted multi-tenant`, `vendor-managed multi-tenant OR managed agent runtime`). The plan collapses cells 5/7/8 into the 3-value enum. acc. #3 also mis-cites §2.2 (candidate-witness section) for the backend-class-row claim (backend class is §2.1). | Class 3 | Class 1 (halt) |
| **U-OD-09** | acc. #2 "Required vs Conditional tier classification per §7.1: 4 Required / 3 Conditional"; acc. #3 "`BreakerScope` enumerates exactly 4 values" | (a) spec §7.1 seven-attribute schema table declares **no tier classification at all** — no Required/Conditional split; the 4/3 tier split is plan-invented and falsely attributed "per §7.1". (b) plan `BreakerScope` = 4 values (`TOOL_CALL, MODEL_INVOCATION, PROVIDER_FAMILY, PROVIDER_INSTANCE`) / spec §7.1 declares `harness.breaker.scope` enum ∈ `{per_model, per_provider}` = **2 values**, confirmed again at spec §11.2 line 642 ("`harness.breaker.scope` 2"). Value names also fully disjoint. *(acc. #3 cites "D6 v1.1 §1.2"; the unit Implements C-OD-07 §7.1, which is the cited Phase-5 contract and which says 2.)* | Class 3 | Class 1 (halt) |
| **U-OD-11** | acc. #3 "`ALWAYS_SAMPLED_EVENT_CLASSES` has cardinality 18 per §9.2 verbatim" | cardinality 18 holds; **member set wholesale-diverges.** Plan includes `fallback.exhausted, retry.attempt.second_or_later, gen_ai.eval.alignment_floor.drift_detected, engine.replay.started, engine.replay.completed, tool.gate.denied, mcp.server.pin_mismatch, harness.breaker.permanent_fail_chain` — none in spec §9.2. Spec §9.2 has `sandbox.tier_escalation, hitl.gate.evaluated, hitl.invocation.opened, hitl.invocation.timed_out, topology.fanout.opened, mcp.tool.call, managed_agents.runtime, skill.activation` — none in plan. "verbatim" is false on contents. | Class 3 | Class 1 (halt) |
| **U-OD-12** | acc. #1 "`BASE_RATE_SAMPLED_EVENT_CLASSES` has cardinality 13 per §10.1 verbatim" | cardinality 13 holds; **member set diverges.** Plan includes `create_agent, invoke_agent, retry.attempt.first, validator.fail.transient, skill.activated, skill.invocation` — none in spec §10.1. Spec §10.1 has `sandbox.enter, sandbox.exit, retrieval, cache events, lease.acquired, lease.released` — none in plan. "verbatim" is false on contents. | Class 3 | Class 1 (halt) |
| **U-OD-14** | acc. #1 "`CARDINALITY_SAFE_ATTRIBUTES` cardinality 13 per §11.2 verbatim"; acc. #2 "`CARDINALITY_PROHIBITED_ATTRIBUTES` cardinality 6 per §11.3 verbatim" | both cardinalities hold; **both member sets diverge.** Safe set: plan adds `anthropic.cache_creation_input_tokens, anthropic.cache_read_input_tokens, validator.fail.permanence, topology.fanout.pattern`; spec §11.2 has `gen_ai.response.finish_reasons, sandbox.provider, hitl.gate.level, hitl.response.class` instead. Prohibited set: plan has `gen_ai.input.messages, gen_ai.output.messages, audit.signature.value, memory.path`; spec §11.3 has `Session/user/tenant IDs, mcp.primitive.signature.sha256, skill.version_sha, audit.signature.sha256 / audit.signature.prior_hash` instead. "verbatim" false on contents for both sets. | Class 3 | Class 1 (halt) |
| **U-OD-28** | acc. #1 "`CollectorPlacement` enumerates exactly 7 values per §20.1 verbatim" | spec §20.1 is a per-cell **placement matrix**, not a 7-value enum declaration; the cited spec collector-placement vocabulary (spec §1.2) is a **6-value** enum (`in-process, sidecar, vendor-pipeline, sidecar with per-tenant routing, per-tenant collector instance, vendor-managed collector`). The plan's 7-value enum (`IN_PROCESS_LOOPBACK, EXTERNAL_OTLP_LOCALHOST, EXTERNAL_OTLP_VENDOR_INGESTION, EXTERNAL_OTLP_TEAM_SELF_HOSTED_ENDPOINT, EXTERNAL_OTLP_TEAM_MANAGED_CLOUD, EXTERNAL_PER_TENANT_OTLP_SELF_HOSTED, EXTERNAL_PER_TENANT_OTLP_MANAGED_CLOUD`) is a plan-invented per-cell vocabulary; "exactly 7 ... per §20.1 verbatim" does not resolve to any 7-element verbatim surface in §20.1. *Decision-vocabulary label: proposing* — §20.1 admits a reading as a matrix the plan summarized rather than a verbatim enum; both readings make the "verbatim" claim unsupportable, but the operator should confirm which §20.1 surface the claim intended. | Class 3 | Class 1 (halt) |
| **U-OD-30** | acc. #6 "`SignatureAlgorithm` enumerates exactly 3 values per ADR-D5 v1.3 §1.4.1 verbatim" | plan `SignatureAlgorithm` = `{ED25519, ECDSA_P256, HMAC_SHA256}` / the cited Phase-5 contract C-OD-21 §21.2 (the section U-OD-30 Implements) enumerates `audit.signature.algorithm ∈ {ed25519, ecdsa-p256, rsa-pss-2048}`. Third value diverges: plan `HMAC_SHA256` / spec `rsa-pss-2048`. *(acc. #6 cites the ADR; the unit Implements C-OD-21 §21.2, which is the cited spec contract and which says `rsa-pss-2048`.)* | Class 3 | Class 1 (halt) |
| **U-OD-32** | acc. #1 "`BRIDGING_ARC_TRANSITIONS` declares exactly 8 transitions per §22.1 verbatim" | cardinality 8 holds; **transition set wholesale-diverges.** Plan transitions 3/6/7/8 = `solo-cloud→team-cloud`, `solo-local→solo-self`, `solo-self→solo-cloud`, `team-local→team-self` (deployment-surface-ascent within-column). Spec §22.1 transitions 3/6/7/8 = `team-self→mt-self`, `solo-local→team-self`, `team-local→mt-self`, `team-self→mt-cloud` (incl. 3 **diagonal** transitions). Plan invents deployment-surface-ascent transitions the spec does not list; plan omits all 3 spec diagonals. "verbatim" false on the transition membership. | Class 3 | Class 1 (halt) |
| **U-OD-33** | acc. #1 "`PreservationDimension` enumerates exactly 5 values per §22.2 verbatim" | cardinality 5 holds; **dimension set diverges.** Plan = `SAMPLING_DISCIPLINE, CARDINALITY_BUDGET, REDACTION_CLASS, GATE_POLICY, SANDBOX_TIER`. Spec §22.2 5 rows = `Span schema ingestion contract, Sampling discipline, Redaction discipline, Trace storage tier, Gate-level multiplicative tunable`. Plan substitutes `CARDINALITY_BUDGET` + `SANDBOX_TIER` for spec's `Span schema ingestion contract` + `Trace storage tier`. "verbatim" false on dimension membership. | Class 3 | Class 1 (halt) |

**Total divergent units: 10** (U-OD-04 + 9). U-OD-04 is already captured by the filed Tension 004. The 9 rows U-OD-02, U-OD-09, U-OD-11, U-OD-12, U-OD-14, U-OD-28, U-OD-30, U-OD-32, U-OD-33 are **newly surfaced forks** of identical shape.

---

## Class 3 findings (severe — phase re-opening)

All nine findings share one discriminator and one resolution shape; per SKILL.md §6 they are presented as a systemic pattern rather than nine isolated fixes. The per-unit defect detail is in the inventory table above. Common fields:

- **Discriminator that classifies as §4.1 Class 3:** discriminator **(b)** — requires upstream-phase artifact revision. Each unit is a Phase-6 plan artifact; resolving the divergence requires a Phase-6 implementation-plan revision-pass conforming the signature/set/value to the cited Phase-5 spec contract. The spec C-OD-* sections are canonical for the plan per `CLAUDE.md` §1.3 authority chain; the plan is the artifact in error.
- **Anti-fabrication attack engaged:** A2 (silent scope narrowing — the plan unit silently substituted a different value set / vocabulary for the contract it claims to implement) plus the §3 calibration-discipline check behind Tension 002 (does the plan unit faithfully implement the cited contract).
- **Axis-domain attack engaged:** OD — "span-attribute schema gaps", "audit-emission contract holes", and (for U-OD-02/U-OD-28) enum-divergence-from-spec; the domain defect's outcome is concretely present in each unit's signature block.
- **Decision-vocabulary label:** *decided* for all except **U-OD-28** (*proposing* — see inventory note; operator confirms which §20.1 surface the "verbatim" claim targeted).
- **Resolution path (shape only — per FM-C, no replacement text supplied):** one OD-plan `implementation-planner` revision-pass conforming each divergent unit's signature/acceptance criteria to the cited C-OD-* spec section. Where a unit's "verbatim" cardinality is correct but the member set is not (U-OD-11, U-OD-12, U-OD-14, U-OD-32, U-OD-33), the revision must conform the *set contents*, not just the count. The operator selects the conformance direction (authority-chain reading per `CLAUDE.md` §1.3 favours the spec, as in Tension 002 / 004); the reviewer does not pick. Cross-unit propagation must be checked — e.g., U-OD-09's `BreakerScope` rename propagates to U-OD-14's `harness.breaker.scope` cardinality reference and any breaker-consuming unit.

---

## Findings considered and rejected (transparency) — units whose "verbatim" claims were checked and DO hold

The following units assert "verbatim" / "per §X" / "exactly N" claims that were cross-checked against the cited spec section and **verified to hold** (clean-list):

1. **U-OD-01** — `PersonaTier` 3 / `DeploymentSurface` 3 / `ACTIVE_CELLS` 8 / `EXCLUDED_CELL` singleton — all match spec §1.1 + §1.4. EXCLUDED rationale matches §1.4. Clean.
2. **U-OD-03** — `COMMITTED_AT_D6_SURFACES` "exactly 6 per §3.1" — spec §3.1 commits 6 per-cell surfaces (backend class / sampling / redaction / trace storage tier / collector placement / retention class). Clean. (`DEFERRED_SURFACES` "11+" is correctly stated as an aggregate, not a verbatim claim.)
3. **U-OD-05** — `NAMESPACE_MAP` "exactly 15 per §5.1" + breakdown "1 OD_CANONICAL / 7 AS_SOURCE / 6 CP_SOURCE / 1 SUBSTRATE_ANCHORED" — spec §5.1 has 15 rows; the 1/7/6/1 source-axis partition is consistent with §5.1 row sourcing. Clean.
4. **U-OD-06** — `AS_SOURCE_NAMESPACE_PREFIXES` "cardinality 7" — spec §5.1 AS-source rows = 7 (`anthropic, mcp, skill, managed_agents, sandbox, files, memory`). Cardinality clean. (Per-prefix §-citations in acc. #2 carry minor cross-reference drift — `mcp.*` cited §14.4 vs spec §5.1 §14.3 etc. — but this is Class 1 documentation drift, not a verbatim-cardinality divergence; not escalated.)
5. **U-OD-07** — `CP_SOURCE_NAMESPACE_PREFIXES` "cardinality 6" — spec §5.1 CP-source rows = 6 (`hitl, topology.fanout, subagent, engine, audit, validator.fail`). Cardinality clean. (Plan writes prefix `"topology."` vs spec row `topology.fanout.*` — minor name drift, Class 1, not escalated.)
6. **U-OD-08** — `F3LifecycleEventClass` "exactly 8 per §6.1" — spec §6.1 maps 8 lifecycle event classes. Cardinality clean.
7. **U-OD-10** — `NamespacePrecedenceRule` 2 values; `NAMESPACE_COLLISIONS` canonical example per §8.2; cache-tier subset invariant `cache_creation + cache_read + uncached == input_tokens` per §8.3 — all match spec §8.1–§8.3. Clean.
8. **U-OD-13** — `PER_CELL_CARDINALITY_BUDGET` 8 entries; `PATTERN_P1_DISCIPLINE_ANCHOR` per §11.4 — consistent with spec §11.1 + §11.4. Clean.
9. **U-OD-15** — `STRUCTURE_NOT_CONTENT_INVARIANT` "matches §12.3 verbatim" — text matches spec §12.3 structure-not-content invariant. (`DEFAULT_OFF_CONTENT_ATTRIBUTES` is stated "per §12.1" without a cardinality claim; the plan's 7-element set is a non-verbatim subset but acc. #1 makes no "verbatim"/"exactly N" assertion, so no divergence claim is contradicted.) Clean on the verbatim claim made.
10. **U-OD-16** — `ContentCapturePosture` 3 values; `PER_PERSONA_TIER_REDACTION` "per §13.1 verbatim" — 3-tier posture matrix matches spec §13.1. Clean.
11. **U-OD-17** — `REDACTION_CLASS_ORDER` "strict-ascending per §13.3 verbatim" — matches spec §13.3 monotonic-tightening ordering. Clean.
12. **U-OD-18** — "formula structure matches §14.1 verbatim" — uncached + 1.25× cache-creation + 0.10× cache-read + output contribution matches spec §14.1; `[MODERATE]` extended-thinking note preserved per §14.1. Clean.
13. **U-OD-19** — sandbox-tier overhead additive per §14.2; fan-out rollup `Σ` / `max` per §14.3 — match spec §14.2/§14.3. Clean.
14. **U-OD-20** — fully revised at OD plan v2.2 cascade Step 6b; its v2.1 "verbatim"/cardinality claims (`F2_12_DeferredSurface` 3, `closure_path` 6) were **deliberately updated** to absorb OD spec v1.3 §14.5.1–§14.5.4 (closure-status discriminator; 3-surface structure preserved as historical record; closure_path 9-entry cascade with the 6-step v2.1 structure preserved as record). The v2.4 claims are consistent with the revised spec v1.3. Not a divergence.
15. **U-OD-21** — `RollupAxis` 3 per §15.1; `TokenizerVersionAnchor` 2 options per §15.2; `FallbackChainCostComposition` per §15.3 — match spec §15.1–§15.3. Clean.
16. **U-OD-22** — `DashboardBindingForm` 3 / `AlertingHook` 3 / `PER_CELL_DASHBOARD_BINDINGS` 8; `1.0/base_rate` scaling per §16.2 — match spec §16.1–§16.2. Clean.
17. **U-OD-23** — `OperatorBurdenEvalPrimitive` "exactly 5 per §17.1 verbatim"; cache-hit-rate formula byte-exact — spec §17.1 five-primitive set matches; child-span emission per §17.2. Clean.
18. **U-OD-24** — `EvalDashboardForm` / `AlignmentFloorAlertingPosture` / `HusainLoopBinding` 3 each; `PER_CELL_EVAL_DASHBOARD_BINDINGS` 8 per §17.3 — match spec §17.3. Clean.
19. **U-OD-25** — `AlignmentFloorPrimitive` "exactly 4 per §18.1"; `DriftDetectedEventAttributes` "exactly 4 per §18.2"; `DRIFT_DETECTED_EVENT_NAME` byte-exact — spec §18.1 has 4 alignment-floor primitives, §18.2 has 4 drift attributes + the event name. Clean.
20. **U-OD-26** — `EvalKindDiscriminator` "exactly 2 per §18.3"; `EVAL_KIND_ATTRIBUTE_NAME == "gen_ai.eval.kind"` byte-exact — spec §18.3 has 2 values + the attribute name. Clean.
21. **U-OD-27** — `BATCH_SPAN_PROCESSOR_WINDOW == 5.seconds` / `BATCH_SPAN_PROCESSOR_BATCH_SIZE == 512` "per §19.1 verbatim" — spec §19.1 commits 5s OR 512 spans. `closure_invariant` per §19.2. Clean.
22. **U-OD-31** — `forbidden_surfaces` "5 per §21.5 verbatim"; `enforcement_layer == DASHBOARD_QUERY_CONSTRUCTION_TIME` — spec §21.5 (cross-tenant aggregation prohibition) + §21.4 — consistent. Clean.
23. **U-OD-34** — `exports` "exactly 8 sub-sections per §23.1"; `closure_path_step_count == 6` — spec §23.1 export surface; closure-path 6 is the v2.1 baseline, preserved-as-historical-record per the v2.2 cascade. Clean within the v2.x cascade discipline.

Additional attack-vector checks that did not surface a finding:

- **FM-D self-check (axis-domain mechanical application).** Each cardinality claim was checked for whether the *member-set* divergence outcome actually appears in the unit's signature block, not asserted generically. Where the set matched (clean-list items), no finding was forced. Where it diverged (inventory table), the divergent members are quoted from the unit's own signature block.
- **U-OD-29 — cites ADR, not spec.** `SandboxTier` 4 values `TIER_0..TIER_3` is asserted "per D2 v1.1 §1.2"; `OtlpReachabilityClass` 4 per §20.3. Spec §20.3 itself uses `Tier-1..Tier-4` labels. The Tier-0..3 vs Tier-1..4 label divergence cannot be classified without reading ADR-D2 v1.1 §1.2 (which the unit cites directly). **Decision-vocabulary label: *open*** — operator/reviewer must verify against ADR-D2 §1.2 before classifying; not placed in the divergence inventory because the divergence target is an ADR, not a spec-§ "verbatim" claim of the audited shape.
- **A5 (missing uncertainty signals).** Implementation-plan units are not confidence-tagged artifacts; absence of `[SPECULATIVE]` tags is expected for the artifact type. Not a finding.

---

## Disposition

**The systemic pattern is confirmed plan-wide.** Tension 002, Tension 004, and CP-plan F3-01 established the shape (≥3 → SKILL.md §6 systemic pattern); this audit finds the shape recurs in **nine further OD-plan units** beyond U-OD-04. Every divergent unit's acceptance criteria are internally contradictory — each claims "per §X verbatim" against a signature/set/value that demonstrably is not — so each unit, as written, **cannot be materialized to satisfy its own acceptance criteria**. Each is a §4.1 Class 3 review finding (discriminator (b)) whose disposition is a §2.7.6 Class 1 (halt-execution) Phase-7 fork.

**Recommended operator action:**

1. **Do not file nine independent fork records.** The higher-leverage resolution per SKILL.md §6 is a single OD-plan revision-pass that addresses the source defect (un-audited "verbatim" claims authored against the OD spec) rather than nine symptom fixes. A single Phase-7 Class 1 tension record covering the OD-plan verbatim-divergence cluster is the appropriate filing — it can carry all nine units plus reference the already-filed Tension 004 for U-OD-04.
2. The `implementation-planner` revision-pass conforms each divergent unit's signatures + acceptance criteria to the cited C-OD-* spec section. For the cardinality-matches-set-diverges units (U-OD-11, U-OD-12, U-OD-14, U-OD-32, U-OD-33) the revision must conform the *member set*, not just preserve the count.
3. Verify cross-unit propagation after the rename/re-set passes — notably U-OD-09 `BreakerScope` (2 vs 4) propagating to U-OD-14's `harness.breaker.scope` reference, and U-OD-02 `BackendClass` (3 vs 7) propagating to U-OD-28's per-cell placement matrix and U-OD-22's cell-class dashboard routing.
4. U-OD-28 is *proposing* and U-OD-29 is *open* — the operator confirms (28) which §20.1 surface the "verbatim" claim intended, and (29) whether ADR-D2 v1.1 §1.2 sanctions the `Tier-0..3` labeling before that unit's classification is settled.

**The complete OD-plan verbatim-divergence fork set is: {U-OD-02, U-OD-04, U-OD-09, U-OD-11, U-OD-12, U-OD-14, U-OD-28, U-OD-30, U-OD-32, U-OD-33}** — 10 units. U-OD-04 is already filed as Tension 004; the 9 others (U-OD-02, U-OD-09, U-OD-11, U-OD-12, U-OD-14, U-OD-28, U-OD-30, U-OD-32, U-OD-33) are newly surfaced forks of identical shape, to be resolved in one OD-plan revision-pass.

---

*Phase-7 pre-implementation review, scoped to the "verbatim"-claim divergence pattern. Read-only with respect to all design-substrate and plan artifacts — no repository file modified. Authored 2026-05-15 per `harness-adversarial-reviewer` SKILL.md Phase-7 pre-implementation review mode.*

---

# §4A Resolution Recommendation — OD-plan verbatim-divergence cluster

*Appended 2026-05-15 per `systems-architect` SKILL.md §4A (Phase-7 tension-resolution mode). This audit report is the canonical systemic-tension record for the cluster (per the Phase-7 checkpoint decision: no per-unit Tension 005+ proliferation). The §4A recommendation is **a recommendation** — the operator holds decision authority (§4A.4).*

## §4A.1 — Precise tension statement

Nine Operational Discipline plan units (plus **U-OD-04**, already filed as Tension 004) carry an acceptance criterion asserting a signature is materialized "per §X **verbatim**" / "exactly N per §X" against a `Spec_Operational_Discipline` contract whose value set, cardinality, or vocabulary the signature does not transcribe. The precise per-artifact divergence is in the **Fork inventory table** above; it is not re-summarized here per §4A.2 ("do not summarize"). The nine newly-surfaced: **U-OD-02, U-OD-09, U-OD-11, U-OD-12, U-OD-14, U-OD-28, U-OD-30, U-OD-32, U-OD-33**.

A recurring sub-shape: **cardinality-matches, member-set-diverges** (U-OD-11, U-OD-12, U-OD-14, U-OD-32, U-OD-33). The "exactly N" count is correct; the N members are not the spec's N members. The conformance must fix the **set contents**, not just preserve the count.

Two divergences were spot-verified directly against `design-substrate/` during this §4A pass: OD spec §7.1 (`harness.breaker.scope ∈ {per_model, per_provider}` = 2 values, reconfirmed at §11.2 line 642) and OD spec §2.1 ("Eight cells; seven distinct classes"; §1.2 enumerates the 7-class backend-class enum). Both confirm the audit; the plan is the divergent artifact.

## §4A.2 — Authority-chain placement

`CLAUDE.md` §1.3 chain: ADR → ADD v1.3 → PRD v1.1 → **per-axis spec v1.x** → **per-axis plan v2.x**. The spec is canonical for the plan.

For all nine the divergent surface is a Phase-5 **`Spec_Operational_Discipline`** contract (v1.2 §1–§13 + §14.1–§14.4 preserved-verbatim into v1.3; v1.3 §14.5 amendment) vs. a Phase-6 **`Implementation_Plan_Operational_Discipline_v2.x`** unit body. The spec sits strictly above the plan. **The plan is the artifact in error in every row.**

Two units cite an ADR rather than the spec in their acceptance criteria, but each unit's `Implements:` field names a Phase-5 spec contract — and the chain is checked against the unit's actual Phase-5 contract:
- **U-OD-09** acc #3 cites "D6 v1.1 §1.2"; the unit Implements **C-OD-07 §7.1**, which declares `harness.breaker.scope ∈ {per_model, per_provider}` = 2. The spec governs.
- **U-OD-30** acc #6 cites "ADR-D5 v1.3 §1.4.1 verbatim"; the unit Implements **C-OD-21 §21.2**, which declares `audit.signature.algorithm ∈ {ed25519, ecdsa-p256, rsa-pss-2048}`. **§4A.5 tiebreaker verified ADR-D5 directly** — see below — and the ADR *agrees with the spec*. The chain is unanimous; the plan's `HMAC_SHA256` is contradicted by its own cited authority.

## §4A.3 — §2-discipline analysis

- **Five-axis (§2.1):** all nine are Operational-Discipline-axis surfaces (backend class, breaker scope, sampling event classes, cardinality budgets, collector placement, signature algorithm, bridging-arc transitions, preservation dimensions). Within-axis plan/spec conformance defect; no cross-axis re-decomposition.
- **Probabilistic–deterministic boundary (§2.2):** every divergent surface is a **deterministic-side** primitive — an enum, a sampled-event-class set, a cardinality-safe/-prohibited attribute set, a signature-algorithm enum, a transition table. OD is the axis where observability and audit reliability *live*; a divergent sampling set or a divergent signature-algorithm enum is a direct reliability defect, not cosmetic.
- **Decision ordering (§2.3):** **D-level** (derivative). The foundational decision — that OD commits these enums/sets — is held by the spec and is not in question. The defect is the plan's derivative materialization diverging. `§4A.4` "an artifact simply diverged from the chain", not a re-decision.

## §4A.4 — Recommended reading

**Conform the nine divergent OD-plan units to the cited `Spec_Operational_Discipline` contract**, in a single `implementation-planner` revision-pass, with cross-unit propagation in the same pass. Authority-chain-determinate per §1.3.

- For the **cardinality-matches / set-diverges** units (**U-OD-11, U-OD-12, U-OD-14, U-OD-32, U-OD-33**) the revision must conform the **member set** — the specific event-class names, attribute names, transitions, dimension rows — to the spec's set, not merely preserve the count. A pass that fixes only the count leaves the divergence intact and the "verbatim" claim still false. This is the single highest-risk instruction for the OD revision-pass.
- For the **enum / cardinality-drift** units (**U-OD-02** 3→7 backend classes, **U-OD-09** `BreakerScope` 4→2, **U-OD-30** `SignatureAlgorithm` `HMAC_SHA256`→`rsa-pss-2048`) conform the enum's value set and cardinality to the cited spec section.
- **Cross-unit propagation (mandatory, same pass):** U-OD-09 `BreakerScope` (2 vs 4) → U-OD-14's `harness.breaker.scope` cardinality reference and any breaker-consuming unit. U-OD-02 `BackendClass` (7 vs 3) → U-OD-28's per-cell placement matrix and U-OD-22's cell-class dashboard routing. The pass must conform consumers in the same revision.
- **Downstream artifact that absorbs the resolution:** `Implementation_Plan_Operational_Discipline` (next version bump). No `CLAUDE.md` anti-leakage rule, no ADR edit implicated.

### Items NOT in the conform-to-spec scope — surfaced for separate operator disposition

1. **U-OD-09 acc #2 — the Required/Conditional tier split is a design gap, not a conformance tension.** The `BreakerScope` 4→2 divergence (acc #3) is clean conform-to-spec. But acc #2's "4 Required / 3 Conditional tier classification per §7.1" describes a split that **spec §7.1 does not declare at all** — the §7.1 seven-attribute schema table has no tier classification. There is nothing to conform to. Per `CLAUDE.md` I-2 / X-AL-3 this is a plan-introduced H_T structure with no spec basis: route as a **§2.7.6 Class 1 fork of a distinct shape** — either `spec-writer` extends §7.1 to commit the tier split, or the operator confirms the plan-extension is sanctioned with recorded rationale.
2. **U-OD-28 — *proposing* (§2.7.6 Class 2 operator decision).** "Exactly 7 values per §20.1 verbatim" resolves to no 7-element verbatim surface in §20.1 (§20.1 is a per-cell placement matrix; the spec §1.2 collector-placement enum is 6-valued). The operator confirms **which §20.1 surface the "verbatim" claim intended** before the unit's conformance target is fixed. Both readings make the claim unsupportable, so U-OD-28 stays in the cluster — but its conformance target needs the operator's read.
3. **U-OD-29 — *open*; not in the fork set; needs an ADR-D2 check.** `SandboxTier` `TIER_0..TIER_3` is asserted "per D2 v1.1 §1.2"; spec §20.3 itself uses `Tier-1..Tier-4` labels. The divergence target is an ADR, not a spec-§ verbatim claim of the audited shape. **Recommend the revision-pass (or the operator) verify `ADR-D2.md` §1.2 directly** to confirm whether `Tier-0..3` is ADR-sanctioned before classifying U-OD-29. This §4A pass did not read ADR-D2; flagging it as the one unverified item.

## §4A.5 — Tiebreaker check

The verifiable fact making each conformance recommendation determinate: **no higher-chain artifact re-commits the plan's divergent vocabulary.** Verified — and for **U-OD-30 the tiebreaker was checked directly against the ADR**, because the plan cited an ADR (higher on the chain than the spec) and an ADR that committed `HMAC_SHA256` would invert the recommendation. `design-substrate/ADR-D5.md` §1.4 + §1.4.1 + the v1.2 Change-note all enumerate `audit_signature_algorithm ∈ {ed25519 / ecdsa-p256 / rsa-pss-2048}` — **`rsa-pss-2048`, not `HMAC_SHA256`.** The ADR agrees with spec C-OD-21 §21.2. The chain is unanimous; U-OD-30's recommendation is **determinate** (and the plan's acc #6 "per ADR-D5 §1.4.1 verbatim" is self-contradicting — its cited authority does not contain `HMAC_SHA256`).

For the other eight, the OD spec change-notes (v1.2→v1.3) record only the §14.5 cost-attribution amendment and the §0.1 preserve-attestation — none touching backend class, breaker scope, sampling sets, cardinality sets, collector placement, bridging-arc transitions, or preservation dimensions. **Determinate: spec canonical, plan conforms.**

**Load-bearing-artifact flag:** the resolution touches no `CLAUDE.md` anti-leakage rule and no F-ADR. The cluster needs operator **ratification** of the conformance direction — except items 1 (U-OD-09 tier split, genuine design gap) and 2 (U-OD-28, *proposing*), which require an explicit operator decision, and item 3 (U-OD-29, *open*) which requires an ADR-D2 §1.2 verification.

## §4A.6 — Fork classification

Per `Project_Workflow_v1_8.md` §2.7.6: **Class 1 (halt-execution)** for all nine — a design-phase artifact (the OD plan) requires revision before the affected units land. Under the `design-substrate/`-is-canonical posture, Class 1 means: halt landing, run the `implementation-planner` revision-pass in-CLI, re-clear, land. **U-OD-01 is unaffected** — audit clean-list, already landed (verified). U-OD-04 is the other cluster member in the current operational-minimum set, already filed as Tension 004 — fold its resolution into the same OD revision-pass.

## §4A.7 — Operator decision required

**The operator decides.** This §4A section recommends; it does not decide and does not edit the plan (§4A.4 — plan edits are `implementation-planner` work, after sign-off). Operator actions:

1. **Ratify** the conform-to-spec direction for the 9-unit cluster + U-OD-04 (authority-chain-determinate; recommended). Note explicitly: the revision-pass must conform **member sets**, not just counts, for U-OD-11/12/14/32/33.
2. **Disposition U-OD-09 acc #2** (item §4A.4.1): spec-extension via `spec-writer`, or sanction the plan-introduced tier split with recorded rationale.
3. **Confirm U-OD-28** (item §4A.4.2): which §20.1 surface the "verbatim" claim targeted.
4. **Authorize an ADR-D2 §1.2 verification** for U-OD-29 (item §4A.4.3) before that unit is classified.

On ratification, sequencing is: `implementation-planner` revision-pass on `Implementation_Plan_Operational_Discipline` (conform 9 units + U-OD-04 + propagate to consumers) → version bump → land U-OD-04 against the conformed plan.

*§4A recommendation authored 2026-05-15 under `systems-architect` SKILL.md §4A. Read-only with respect to `design-substrate/` — no spec, plan, or ADR modified by this pass. ADR-D5.md was read for the §4A.5 tiebreaker; not modified.*
