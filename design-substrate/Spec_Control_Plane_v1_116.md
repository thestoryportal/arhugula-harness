# Spec: Control Plane — v1.116 (delta over v1.115)

*Delta-only file. v1.115, v1.114, and every earlier C-CP-01 … C-CP-29 body are preserved verbatim
except at the amendment sites named below. This is the operator-ratified B-138 disposition-(a)
apply pass: the span attribute `validator.fail.class` carries the C-CP-25→C-CP-28 §25.2
`ValidatorFailClass` domain; C-CP-21 §21.1/§21.5's contrary gloss is corrected and the
retry-exit taxonomy is demoted from the wire name — never deleted. No C-CP number is minted and
no Runtime, OD, CXA, or implementation artifact is amended.*

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
`validator.fail.permanence`'s derivation base is re-declared at §1.3 because its former base
(the retry-exit domain) is no longer what the `class` attribute carries. Its emission remains
build-owed at register row `B-124`.

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
bounded (5), cardinality LOW, emitted on the `validator.fail` span per C-CP-28 §25.5. The §21.5
row-1 value-set gloss naming the retry-exit values is corrected accordingly; the row's type,
cardinality, always-emitted condition, and ownership cell are unchanged.

### §1.2 Retry-exit taxonomy binding (governs every §21 occurrence)

Every §21 occurrence of `validator.fail.class` that names or guards on the five routing values
(the §21.1 table key column; the §21.2 staircase guard
`validator.fail.class ∈ {transient-retry, Reflexion-recoverable}`; the §21.3/§21.1 skip-staircase
references) denotes the **retry-exit classification** (`ValidatorRetryExitClass`, C-CP-21 §21.1),
which is NOT carried on the wire attribute of that name. The routing semantics are preserved
byte-for-byte; only the carrier naming is re-declared. No wire attribute for the retry-exit
classification is minted at this delta — if one is ever wired, it takes a distinct name (the
candidate-(c) route), routed through its own arc.

### §1.3 `validator.fail.permanence` derivation base (supersedes §21.5 row 3's derivation clause)

`validator.fail.permanence` remains enum string ∈ `{transient, permanent}`, bounded (2). Its
derivation is re-declared from the validator OUTCOME: `permanent` iff the evaluation's
`ValidatorOutcome` is `PERMANENT_FAIL` (C-CP-28 §25.2), `transient` otherwise. This preserves
§21.5's intent — the former clause's `{permanent-fail-exit, terminal-fail-exit}` classes are
exactly the outcomes that abort — while grounding the derivation in a domain the producer
actually holds. §21.6's sampling rows key on the two permanence VALUES and are unchanged.
Emission is build-owed at `B-124`; `validator_fail_taxonomy.py:169-176`'s
`validator_fail_permanence(ValidatorRetryExitClass)` helper remains a correct derivation over
the retry-exit domain but is not the wire path.

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
  former is `B-124`'s build; the latter stays declared-unwired as at HEAD.
- It does not mint a wire attribute for the retry-exit classification.
- It does not amend OD's C-OD-29.1 declaration, any Runtime surface, or any CXA row.
- It does not touch code or tests: the shipped producers are already conformant to the ratified
  reading.

## §3 Filing footer

| Field | Value |
|---|---|
| Artifact | `Spec_Control_Plane_v1_116.md` |
| Amendment sites | THREE, all within C-CP-21 §21: §21.5 row-1 domain; the §21 retry-exit binding declaration; §21.5 row-3 derivation clause. ONE reconciliation: stale cross-cites (§1.4) |
| Preserved | §21.1 routing table substance; §21.2 staircase; §21.3 palette rule; §21.4; §21.6; §21.7; §21.5 attribute count (3); all untouched prior bodies |
| Contract numbers | ZERO new |
| Register | `B-138` closes at this leg (disposition (a)); `B-124` build unblocked |
| Runtime / OD / CXA | No delta owed |
| Implementation | ZERO code owed by this delta |
