# Spec: Control Plane — v1.116 (delta over v1.115)

*Delta-only file. v1.115, v1.114, and every earlier C-CP-01 … C-CP-29 body are preserved verbatim
except at the amendment sites named below. This is the operator-ratified B-138 disposition-(a)
apply pass: the span attribute `validator.fail.class` carries the C-CP-25→C-CP-28 §25.2
`ValidatorFailClass` domain; C-CP-21 §21.1/§21.5's contrary gloss is corrected and the
retry-exit taxonomy is demoted from the wire name — never deleted. The pass is BUNDLED with the
ADR-D5 v1.6 amendment (§1.10.1, the upstream canonical declaration site) so the authority chain
(ADR over spec, root `CLAUDE.md` §1.3) is reconciled at the source, not overridden downstream.
No C-CP number is minted and no Runtime, OD, CXA, or implementation artifact is amended.*

**Filed:** 2026-08-09
**Authority:** Register row `B-138` close_out step (2), operator-ratified candidate **(a)**
2026-08-09 (AskUserQuestion), on the grounding pass recorded at the row (all cites re-read by
content at HEAD).
**Predecessor:** `Spec_Control_Plane_v1_115.md`

## §0 Change-note (v1.115 → v1.116)

### §0.1 The defect and the ratified reading

Two cleared surfaces declared one attribute name with disjoint five-value domains.
`Spec_Control_Plane_v1_2.md` §21.5 declares `validator.fail.class` as
`{transient-retry, Reflexion-recoverable, HITL-recoverable, permanent-fail-exit, terminal-fail-exit}`
(the §21.1 retry-exit routing taxonomy, realized as `ValidatorRetryExitClass` at
`harness-cp/src/harness_cp/validator_fail_taxonomy.py:39-62`). `Spec_Control_Plane_v1_10.md`
§25.2 declares `ValidatorFailClass`
(`schema_violation / semantic_inconsistency / safety_policy / resource_constraint / external_rejection`)
and §25.5 declares the `validator.fail` span emitting `validator.fail.class` — the contract
renamed C-CP-25 → C-CP-28 at v1.13. Every live surface agrees with the §25 reading: both
producers (`validator_framework.py:_build_span_attributes` and
`harness-runtime/.../validator_escalation_composer.py`) write `ValidatorFailClass` values; OD's
ingestion schema (`validator_namespace.py`, C-OD-29.1) declares exactly the §25.5 four-attribute
shape; no reader anywhere asserts a `ValidatorRetryExitClass` value on the attribute; no
projection function exists in `harness-{cp,od,runtime}/src`. The operator ratified reading (a):
**the shipped `ValidatorFailClass` domain is authoritative for the wire attribute
`validator.fail.class`.**

### §0.2 What is corrected, what is demoted, what is preserved

The §21.1 five-class routing taxonomy — its classes, routing rows, staircase, palette
restriction, and every recovery path — is **preserved verbatim in substance**: it remains the
canonical *retry-exit classification* (`ValidatorRetryExitClass`). What is corrected is only its
**binding to the wire name**: the §21.1 table's key column and §21.2's staircase guard named
`validator.fail.class` as their carrier, and §21.5 row 1 declared the wire attribute with the
retry-exit domain. Those bindings are re-declared at §1. The taxonomy is demoted from the
attribute name, not deleted — the B-125 disposition-(b) standard.

### §0.3 The CP-3 / OD-4 attribute-set divergence, dispositioned in the same pass

C-CP-21 §21.5 declares THREE attributes (`class`, `cause_attribution`, `permanence`); OD's
C-OD-29.1 ingests FOUR (`class`, `detail_hash`, `next_action`, `escalation_owed`); the live
emission produces OD's four. **This is two contracts declaring disjoint-except-`class` subsets
of one namespace, not one contract violated**: `detail_hash` / `next_action` / `escalation_owed`
are C-CP-28 §25.5 members, not §21.5 members, and §21.5's declared count stays THREE — the
`namespace_map` / export-manifest count gates that pin `validator.fail.* = 3` against C-CP-21
§21.5 remain correct and untouched. Of §21.5's other two rows: `cause_attribution` is declared
and not yet emitted at HEAD (pre-existing, unchanged by this delta);
`validator.fail.permanence`'s former derivation clause is demoted at §1.3 because its base
(the retry-exit domain) is no longer what the `class` attribute carries; the replacement
derivation is deliberately NOT declared here (see §1.3) and routes to register row `B-124`.
`cause_attribution`'s declared-required-vs-zero-producer gap is not absorbed as acceptable:
it is minted as register row `B-139` at this leg.

### §0.4 Zero-surface statement

ZERO contract numbers minted; ZERO code, test, plan, Runtime, OD, or CXA edits; ZERO hash
impact; ZERO change to §21.5's declared attribute count, to §21.6's sampling rows, or to any
routing/recovery semantics. Historical delta files are preserved verbatim per the delta-chain
convention — the stale cross-cites named at §1.4 are superseded by declaration here, not edited
in place.

## §1 AMENDMENT — `validator.fail.class` domain and the §21 binding corrections

### §1.1 Wire-attribute domain (supersedes §21.5 row 1)

The span attribute `validator.fail.class` carries the C-CP-25→C-CP-28 §25.2 `ValidatorFailClass`
domain: enum string ∈
`{schema_violation, semantic_inconsistency, safety_policy, resource_constraint, external_rejection}`,
bounded (5), cardinality LOW, declared at C-CP-28 §25.5 on the `validator.fail` span.
**Span-site realization gap — recorded, not closed:** no production path opens a
`validator.fail` span at HEAD. The attributes ride the `validator.evaluate` span
(`workflow_driver.py:5600`, attach loop at the §C-OD-29.1 envelope) and the runtime composer's
`validator.escalation` span (`validator_escalation_composer.py:141`), while C-OD-29.1 declares
span-site `validator.fail` and OD sampling fixtures match `validator.fail.*`-shaped span NAMES
that production never emits. This declared-vs-shipped divergence is minted as register row
`B-140` and is load-bearing for `B-124`'s sampling half; this amendment settles the attribute
DOMAIN only. The §21.5
row-1 value-set gloss naming the retry-exit values is corrected accordingly; the row's type,
cardinality, and ownership cell are unchanged. The **always-emitted condition is corrected to
match the C-CP-28 §25.2 type**: `ValidatorResult.fail_class` is `ValidatorFailClass | None`, so
the attribute is emitted on every validator-failure event **carrying a populated `fail_class`**
and is ABSENT when `fail_class=None` (a live shape — a non-PASS result may carry `None`); the
runtime escalation composer additionally materializes the sentinel `unspecified` on a `None`
brief — a shipped out-of-domain value under this closed declaration. Its disposition
(absent-on-`None`, matching the framework producer, vs widening the wire alphabet) is NOT
decided here and routes to `B-140` with the span-site gap. The absent case is not a domain
member.

### §1.2 Retry-exit taxonomy binding (governs every §21 occurrence)

Every §21 occurrence of `validator.fail.class` that names or guards on the five routing values
(the §21.1 table key column; the §21.2 staircase guard
`validator.fail.class ∈ {transient-retry, Reflexion-recoverable}`; the §21.3/§21.1 skip-staircase
references) denotes the **retry-exit classification** (`ValidatorRetryExitClass`, C-CP-21 §21.1),
which is NOT carried on the wire attribute of that name. The routing semantics are preserved
byte-for-byte; only the carrier naming is re-declared. No wire attribute for the retry-exit
classification is minted at this delta — if one is ever wired, it takes a distinct name (the
candidate-(c) route), routed through its own arc.

### §1.3 `validator.fail.permanence` derivation clause (demotes §21.5 row 3's derivation base)

`validator.fail.permanence` remains enum string ∈ `{transient, permanent}`, bounded (2), and
§21.6's sampling rows keying on the two permanence VALUES are unchanged. The former derivation
clause (`permanent` if class ∈ `{permanent-fail-exit, terminal-fail-exit}`) is demoted with the
taxonomy: it remains a correct derivation over the retry-exit classification
(`validator_fail_taxonomy.py:169-176`), but the wire producer does not hold that classification.
**A replacement wire derivation is deliberately NOT declared at this delta**, because the only
candidate the producer holds — the validator outcome — is a LOSSY projection: `permanent-fail-exit`
routes to HITL (outcome `ESCALATE`, §21.1 row 4 / C-CP-28 §25.2 mapping), so outcome cannot
discriminate it from `HITL-recoverable`, and an outcome-based rule would silently narrow §21.6's
always-sample-permanent coverage to the abort path. The derivation decision routes to register
row `B-124`'s arc, which must either materialize the retry-exit classification at the emission
site, ratify an outcome-based narrowing WITH §21.6 re-specified, or select another carrier —
and until it does, `validator.fail.permanence` stays declared-unwired. `B-124` is unblocked on
the TAXONOMY question (settled here) and owns this derivation sub-decision explicitly.

### §1.4 Stale cross-cite reconciliation (declaration only)

Two historical cross-cites tangled the taxonomies and are superseded by this delta's reading:
`Spec_Control_Plane_v1_18.md` adjacent-defect item (iii)'s parenthetical *"5-class taxonomy per
C-CP-21 §21.3"* (C-CP-21 §21.3 is the palette-restriction rule; `ValidatorFailClass` is C-CP-28
§25.2's own taxonomy, not C-CP-21's), and `Spec_Control_Plane_v1_10.md` §25.2's parenthetical
*"per substitution H_T-CP-21"*. Neither historical file is edited. The code docstring
`validator_framework_types.py:71` *"NEW at C-CP-25"* (stale vs the v1.13 rename) is a code-side
Class 3 residual riding the next arc that touches that file, not a spec matter.

## §2 What this delta does not do

- It does not change any routing, staircase, palette, summarization-table, sampling, or
  operator-burden semantics at §21.
- It does not change §21.5's declared attribute count (THREE) or the export-manifest /
  namespace-map count gates pinned to it.
- It does not wire `validator.fail.permanence` or `validator.fail.cause_attribution` — the
  former's derivation sub-decision and build are `B-124`'s; the latter's zero-producer gap is
  minted as `B-139`, not absorbed.
- It does not declare a wire derivation for `validator.fail.permanence` (§1.3 states why the
  outcome projection is lossy and routes the decision to `B-124`).
- It does not mint a wire attribute for the retry-exit classification.
- It does not amend OD's C-OD-29.1 declaration, any Runtime surface, or any CXA row.
- It does not touch code or tests: the shipped producers are conformant to the ratified DOMAIN
  reading; the span-site realization gap and the composer sentinel are recorded at `B-140`, not
  silently absorbed as conformance.

## §3 Filing footer

| Field | Value |
|---|---|
| Artifact | `Spec_Control_Plane_v1_116.md` |
| Amendment sites | THREE, all within C-CP-21 §21: §21.5 row-1 domain + emission condition; the §21 retry-exit binding declaration; §21.5 row-3 derivation-clause demotion. ONE reconciliation: stale cross-cites (§1.4). BUNDLED: ADR-D5 v1.5 → v1.6 (§1.10.1, the upstream canonical declaration site — authority-chain reconciliation at the source) |
| Preserved | §21.1 routing table substance; §21.2 staircase; §21.3 palette rule; §21.4; §21.6; §21.7; §21.5 attribute count (3); all untouched prior bodies |
| Contract numbers | ZERO new |
| Register | `B-138` closes at this leg (disposition (a)); `B-139` MINTED (`cause_attribution` declared-required, zero producers); `B-140` MINTED (span-site realization gap + composer sentinel); `B-124` unblocked on the taxonomy question, owns the permanence-derivation sub-decision |
| Runtime / OD / CXA | No delta owed |
| Implementation | ZERO code owed by this delta |
