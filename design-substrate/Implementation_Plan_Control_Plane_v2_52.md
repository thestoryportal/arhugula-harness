# Implementation Plan: Control Plane — v2.52 (delta over v2.51)

*v2.52 absorbs the B-141 cascade (B-138 operator-ratified disposition (a), CP spec
v1.116) into the plan's execution authority as SUPERSESSION NOTES on two as-domain
framings that still cite the C5 retry-exit five-value set for the wire attribute
`validator.fail.class`. No new unit, cluster, DAG node, dependency edge, or CXA row is
introduced; NO landed unit's body is amended (the B-97(a)/B-118 new-unit precedent —
supersession rides as a note, the landed criteria stand as HISTORY). Every unit body,
signature block, rollback boundary, and all other plan content are PRESERVED VERBATIM.*

**Status:** Proposed

## §0 Change-note (v2.51 → v2.52)

### §0.1 The two stale as-domain sites

B-138's disposition (a) settled `validator.fail.class` on the C-CP-25→C-CP-28 §25.2
`ValidatorFailClass` domain (CP spec v1.116, operator-ratified 2026-08-09). Two plan
surfaces still frame the attribute as the C-CP-21 §21.5 retry-exit five-value set:

1. **U-CP-41 acceptance criterion #5** (`Implementation_Plan_Control_Plane_v2_9.md:683-686`):
   "`validator_fail_class`, when present, is drawn from the C-CP-21 §21.5 5-value
   `validator.fail.class` set" — the `VerifierResult` record's domain framing, plus the
   §2A record-shape comment block (`:621-630`) carrying the same cite, and the test
   roster's `test_verifier_fail_class_in_cp_21_5_set`.
2. **U-CP-47-era `VALIDATOR_FAIL_NAMESPACE_SCHEMA` criteria**
   (`Implementation_Plan_Control_Plane_v2_4.md:631-638`, preserved through the delta
   chain): "`validator.fail.class` — enum string ∈ `{transient-retry,
   Reflexion-recoverable, HITL-recoverable, permanent-fail-exit, terminal-fail-exit}`;
   bounded (5)" — plus the derived-permanence clause at the same site, whose derivation
   base is routed to register row `B-124` per CP spec v1.116 §1.3.

### §0.2 The supersession notes (landed units NOT amended)

**NOTE on U-CP-41 (as-domain supersession, v2.52).** `VerifierResult.validator_fail_class`,
when present, is drawn from the C-CP-25→C-CP-28 §25.2 `ValidatorFailClass` domain
(`schema_violation` / `semantic_inconsistency` / `safety_policy` / `resource_constraint`
/ `external_rejection`) per CP spec v1.116 (B-138 disposition (a)) — the U-CP-41
criterion #5 / §2A comment-block references to "the C-CP-21 §21.5 5-value set" are
superseded AS DOMAIN. The record shape stays three fields with Optional presence; the
field's declared TYPE is superseded `Optional<str>` → `Optional<ValidatorFailClass>`
(enum-typed so construction itself enforces the wire domain — an out-of-domain value
is a `ValidationError`, not a silent wire value; out-of-family review round 2 at the
B-141 cascade PR).
The as-built witness follows in the B-141 cascade PR: the test roster's
`test_verifier_fail_class_in_cp_21_5_set` is superseded by
`test_verifier_fail_class_in_validator_fail_class_domain` (membership set →
`ValidatorFailClass`, `harness-cp/tests/test_both_by_tier_overlay.py`); the U-CP-47
export-manifest routing ("verifier output emits `validator.fail.*` span attributes")
is unchanged — the audit contract routes to the same wire names, now under the
ratified domain.

**NOTE on U-CP-47-era criteria (as-domain supersession, v2.52).** The
`VALIDATOR_FAIL_NAMESPACE_SCHEMA` v2.4-era enumeration binding the retry-exit five-value
set to `validator.fail.class` is superseded AS DOMAIN by CP spec v1.116: the attribute's
domain is `ValidatorFailClass`; the retry-exit taxonomy remains the §21.1/§21.2 ROUTING
discriminator per ADR-D5 v1.6 §1.10 (demoted from the wire name, not deleted). The
derived-permanence clause at the same v2.4 site is likewise superseded as written — the
derivation base is the routed `B-124` sub-decision per CP spec v1.116 §1.3. The v2.4
criteria stand as HISTORY (landed-unit text is not retroactively edited); any future
re-validation arc reads THIS note as the operative domain authority, per the same
convention the register row B-141 records for
`Implementation_Plan_Control_Plane_v2_4.md:631-638`.

### §0.3 What this delta is NOT

Not a unit re-open: no new fields, no unit-body rewrites, and U-CP-41's
`VerifierResult` remains a deferred carrier (no live producer — the two-agent observer
activates at a future arc); U-CP-47's landed namespace schema code was already
reconciled at the B-138 arc's CP spec v1.116 leg. The ONE code-shape change this
delta's §0.2 note authorizes is the `validator_fail_class` field-type supersession
(`Optional<str>` → `Optional<ValidatorFailClass>`), landing in the same PR. This delta is the plan-authority re-pin owed under register row
`B-141` (back-flow record `.harness/b-141-validator-fail-class-cascade-2026-08-12.md`),
the exact sibling of the v2.50/v2.51 re-pins under B-144/B-153. Sibling venue legs in
the same PR: OD spec v1.41 (C-OD-14 §14.5.3 escalation table) + ADR-D6 v1.3 (§1.5.2 +
§1.2.2.1).

---

*End of v2.52 delta. The v2.51 body and all prior deltas stand unchanged beneath this
file per the delta-only convention.*
