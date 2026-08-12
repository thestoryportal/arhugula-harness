# B-141 cascade — `validator.fail.class` OD/D6 venue reconciliation under the B-138 disposition (a)

*Filed 2026-08-12 (loop session, B-141 arc-open). This is the back-flow record for the
cascade the register row B-141 declares OWED at the OD/ADR-D6 venue after B-138 settled
the wire attribute `validator.fail.class` on the C-CP-25→C-CP-28 §25.2
`ValidatorFailClass` domain (CP spec v1.116, operator-ratified disposition (a),
2026-08-09, PR #1278). The cascade direction is forced by that ratification — this is a
ratified bundled-absorption arc per workspace `CLAUDE.md` §11.4, NOT a new fork filing.*

## 1. The defect (register row B-141, surfaced at the B-138 codex round 3 [P1])

One declared surface family still binds the OLD retry-exit domain
(`ValidatorRetryExitClass`: transient-retry / Reflexion-recoverable / HITL-recoverable /
permanent-fail-exit / terminal-fail-exit) to the wire name `validator.fail.class`,
which B-138 (a) settled on the `ValidatorFailClass` domain (schema_violation /
semantic_inconsistency / safety_policy / resource_constraint / external_rejection):

| Surface | Site (pre-amendment anchors, verified 2026-08-12 before this arc's edits; sites this PR itself amends drifted — post-amendment anchors in parentheses) | Out-of-domain binding |
|---|---|---|
| C-OD-14 §14.5.3 escalation table | `design-substrate/Spec_Operational_Discipline_v1_3.md:223` (defining venue, untouched — superseded by the v1.41 delta; head v1.40 carried it verbatim per the delta-only convention) | `validator.fail.class` = `terminal-fail-exit` |
| ADR-D6 v1.2 §1.5.2 escalation table | `design-substrate/ADR-D6_v1_2.md:298` (post-amendment: the row under "Escalation on mismatch" in §1.5.2) | `validator.fail.class` = `terminal-fail-exit` |
| ADR-D6 v1.2 §1.2.2.1 `retry.fail_class` row | `design-substrate/ADR-D6_v1_2.md:120` (post-amendment: the §1.2.2.1 6-attribute table's `retry.fail_class` row) — Definition clause "carries the validator-fail event's classification if validator-fail triggered the retry" | cross-ref implies the validator-fail event's class ∈ the retry-exit domain |
| Carrier defaults | `harness-od/src/harness_od/idempotency_join_dedup.py:347` (post-amendment `:348`) `ReplaySemanticDivergenceError.validator_fail_class = "terminal-fail-exit"` | out-of-domain default |
| Carrier witness | `harness-od/tests/test_idempotency_join_dedup.py:307` (post-amendment `:311`) | asserts `"terminal-fail-exit"` |
| U-CP-41 deferred verifier carrier | `harness-cp/src/harness_cp/both_by_tier_overlay.py:82,:90-91` (post-amendment `:92`) `VerifierResult.validator_fail_class` documented "∈ the C-CP-21 §21.5 5-value set" | as-domain docstring |
| U-CP-41 witness | `harness-cp/tests/test_both_by_tier_overlay.py:42` `_CP_21_5_FAIL_CLASSES = {c.value for c in ValidatorRetryExitClass}` + `:126` membership assert | as-domain test |
| CP plan U-CP-41 acc #5 | `design-substrate/Implementation_Plan_Control_Plane_v2_9.md:683-686` "drawn from the C-CP-21 §21.5 5-value `validator.fail.class` set" | as-domain plan criterion |
| CP plan U-CP-47-era criteria | `design-substrate/Implementation_Plan_Control_Plane_v2_4.md:631-638` (`VALIDATOR_FAIL_NAMESPACE_SCHEMA` retry-exit enumeration; preserved through the delta chain) | as-domain plan criterion (HISTORY — landed unit, not amended) |

**Zero production emission sites** construct `ReplaySemanticDivergenceError` at HEAD
(declaration + `__all__` + one docstring mention + the test file only — verified by
`rg ReplaySemanticDivergenceError harness-*/src harness-*/tests`, 2026-08-12), and
`VerifierResult` has no live producer (U-CP-41 two-agent observer deferred). So no live
wire value violates B-138 (a) — the DECLARED surfaces contradict it. Declared-shape-only
pricing per the register row's own step (3).

## 2. The carried-value decision

**`validator.fail.class = "semantic_inconsistency"`** (a `ValidatorFailClass` member) on
the §14.5.3 replay-semantic-divergence escalation. Grounds:

1. **Semantic fit.** The escalation fires when a `deterministic_replay` span's
   `retry.cause_attribution` diverges from the F2 ledger entry's stored value — the
   replay CONTRADICTS PRIOR RECORDED STEP STATE, which is `SEMANTIC_INCONSISTENCY`'s
   own definition ("Contradicts prior step state",
   `harness-cp/src/harness_cp/validator_framework_types.py:81`).
2. **No new wire attribute is minted**, so the register row's council trigger
   ("convene only if the distinct-attribute route trends AND it would mint a new wire
   attribute") does NOT fire. Adjudicated in venue per the B-125/B-138 precedent.
3. **The terminal/permanent intent survives structurally.** The §14.5.3 halt + HITL
   routing intent is carried by `validator.fail.permanence = "permanent"` (unchanged)
   and the always-sampled rule, which keys on `permanence`, not `class`
   (C-OD-09 §9.2 "validator.fail.permanence=permanent always-sampled";
   `harness-od/src/harness_od/sampling_mode.py` realization). The specific cause stays
   at `validator.fail.cause_attribution = "replay_semantic_divergence"` (unchanged).
   The retry-exit classification (`terminal-fail-exit`) remains what it always was
   per ADR-D5 v1.6 §1.10 — a ROUTING discriminator, demoted from the wire name.

Alternatives considered and rejected: (b) a distinct wire attribute for the retry-exit
classification — mints a new attribute for information the event does not lose (the
routing behaviour is prose-specified at §14.5.3, not attribute-carried), and would
trigger the council clause for no operator-visible gain; (c) dropping
`validator.fail.class` from the escalation's fixed attributes — loses the class signal
OD's C-OD-29.1 family ingests and diverges from the shipped 4-attribute event shape.

## 3. The cascade (what this arc lands)

1. **ADR-D6 v1.2 → v1.3, in place** (the ADR-D5 v1.6 mechanics; filename
   `ADR-D6_v1_2.md` retained — 14 in-repo path references make a rename pure churn;
   the internal Revision line + this record carry the v1.3 identity):
   §1.5.2 escalation-table `validator.fail.class` row → `semantic_inconsistency`
   with the domain citation; §1.2.2.1 `retry.fail_class` Definition clause reworded to
   name the retry-exit value as the C5 routing classification of the triggering
   validator-fail (per ADR-D5 v1.6 §1.10), distinct from the wire attribute's
   `ValidatorFailClass` domain.
2. **OD spec v1.40 → v1.41** (delta-only file): C-OD-14 §14.5.3 escalation-table
   `validator.fail.class` row superseded to `semantic_inconsistency` with the domain
   citation; the §14.5.3 prose, invariance check, catalog-extension paragraph, and the
   other three table rows preserved verbatim.
3. **CP plan v2.51 → v2.52** (plan-note delta): U-CP-41 acceptance criterion #5's
   "C-CP-21 §21.5 5-value set" as-domain framing superseded to the
   `ValidatorFailClass` domain per CP v1.116; the U-CP-47-era
   `VALIDATOR_FAIL_NAMESPACE_SCHEMA` retry-exit enumeration
   (`Implementation_Plan_Control_Plane_v2_4.md:631-638`) marked superseded-as-domain
   AS A NOTE — the landed units are NOT amended (B-97(a)/B-118 new-unit precedent).
4. **OD plan v2.34 → v2.35** (note delta — a FIFTH venue this arc's own cross-spec
   drift grep surfaced; NOT named at registration): the v2.2-era U-OD-20 criteria
   pinning the §14.5.3 invariance-check ESCALATION to `terminal-fail-exit`
   (`Implementation_Plan_Operational_Discipline_v2_2.md:55/:66/:167/:368`, standing
   authority at head v2.34 — no later delta re-states them) superseded AS VALUE as a
   NOTE, same convention as the CP plan sites; leaving them would have put OD spec
   v1.41 and the OD plan in direct disagreement within one axis.
5. **Code + witnesses** (same-PR cascade, the §0.3 shape of OD v1.40's precedent):
   `ReplaySemanticDivergenceError.validator_fail_class` default →
   `"semantic_inconsistency"` + docstring; its test assert follows;
   `VerifierResult.validator_fail_class` docstrings → `ValidatorFailClass` domain;
   `_CP_21_5_FAIL_CLASSES` → the `ValidatorFailClass` value set (renamed to match).
6. **Clearance markers** for all four design-substrate artifacts + pointer bumps
   (root `CLAUDE.md` §2.3 OD row, §2.4 CP+OD rows; `.harness/artifact-pointers/`
   lineage; `.harness/artifact-heads.md` regenerated + `--check` green).
7. **Register**: B-141 → closed.

## 4. Coordination notes (adjacent register rows — none widened here)

- **B-124** (`validator.fail.permanence` never set on any span): this cascade keeps
  `permanence` EXPLICITLY DECLARED on the carrier and does NOT wire any derivation —
  the permanence-derivation sub-decision stays routed to B-124 per CP v1.116 §1.3.
  If B-124's pending Class-2 ratification (rec D on file at #1283) later re-scopes the
  attribute, the carrier's explicit field is unaffected (it is a declared event shape,
  not a derived span write).
- **B-140** (validator.fail span-site/keying divergence): untouched. The §14.5.3
  escalation is an EVENT-shaped declaration; its always-sampled arm keys on
  `permanence`, which this cascade preserves. The span-site gap B-140 owns is
  orthogonal to the class-domain fix.
- **B-139** (`validator.fail.cause_attribution` zero producers): untouched. Related
  pre-existing gap NOTED, not chased: ADR-D6 v1.2 §1.5.2's "Cross-ADR coordination"
  paragraph forward-flagged that ADR-D5's §1.10.1 open-set cause_attribution catalog
  would absorb `replay_semantic_divergence` "at the next D5 revision"; D5 has since
  revised four times (v1.3–v1.6) without absorbing it. That is B-139's family
  (cause_attribution catalog vs producers) and is recorded here for its next grounding
  pass rather than widened into this arc.
- **B-126/B-146** (`retry.*` wire register): `retry.fail_class` KEEPS the retry-exit
  domain — it is a retry-site routing classification, not the validator wire attribute;
  only the §1.2.2.1 cross-reference CLAUSE is reworded.
- **ADD v1.3** (`Architectural_Design_Document_v1_3.md:116`): its Rationale-highlights
  narrative ("At v1.2, D6 … mismatch ESCALATES to terminal-fail-exit with
  `replay_semantic_divergence` cause_attribution") describes ADR-D6 AS OF v1.2 — a
  version-scoped consolidation summary, the same recorded-not-edited class as the CP
  plan v2.4 criteria. RECORDED here so a future ADD revision carries the D6 v1.3 value;
  not edited in this arc (the ADD is a P3d consolidation artifact and B-141's
  registered scope does not name it).

## 5. What would falsify / re-open

A production construction site of `ReplaySemanticDivergenceError` appearing before
this cascade merges (would make the out-of-domain value LIVE — urgency upgrade), or a
B-124 ratification outcome that re-scopes `validator.fail.permanence` off the event
(would require re-visiting the carrier's fixed fields, not the class value).
