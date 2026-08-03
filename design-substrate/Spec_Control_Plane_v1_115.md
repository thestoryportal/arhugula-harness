# Spec: Control Plane — v1.115 (delta over v1.114)

*Delta-only file. v1.114, v1.113, and every earlier C-CP-01 … C-CP-29 body are preserved verbatim
except at the amendment sites named below. This is the operator-ratified B-107 Reading A-hybrid
apply pass: scalar classification removal, map construction refusal, and resolver-boundary
enforcement. No C-CP number is minted and no Runtime, CXA, or implementation artifact is amended.*

**Filed:** 2026-08-03
**Authority:** `.harness/class_2_fork_b107_empty_fence_key_resolution_refusal.md` §11,
operator direction “All recommendations approved … Proceed to pass 13.”
**Predecessor:** `Spec_Control_Plane_v1_114.md`

## §0 Change-note (v1.114 → v1.115)

### §0.1 Amendment sites and preservation

This delta carries exactly three substantive contract amendment sites: (1) `Spec_Control_Plane_v1_107.md` §1.1's effect-fence
unaddressed/eligible membership; (2) `ResumeContext.effect_fence_resolutions`, first published at
v1.66 and expressly preserved at v1.112 §0.4; and (3) the resolver boundary governing the same
membership. It also carries one deterministic publication reconciliation: v1.112 §2.1's obsolete
sentence is qualified at §1.4. The four variants,
ten source shapes, seven carriers, v1.112 §2.2's three constraints, and v1.112 §2.4's
one-authority rule are preserved.

### §0.2 Ratified determinations

The scalar channel is clause-(i) removal; the map channel is clause-(ii) ordinary-construction
refusal. The b80 `False → True` consequence is ratified. **B-101(a) is not jointly discharged:**
this delta pays the same field-set compatibility-cost category but does not add B-101(a)'s closed
variant discriminator or change base-schema serialization. B-101 remains separately closed under
(b)-PLUS, its promotion trigger is unchanged, and the rows remain separate.
`AccessorDerivedResumeContext` and every `ResumeContext` subclass inherit the
base field contract. CXA is classification-only: no new §2.3 row. No Runtime §30 failure class or
Runtime spec delta is owed. The §6.1 forged-instance ruling is defence in depth, not closure.

### §0.3 Byte compatibility for the two-axis map amendment

v1.112 §0.4 preserved the response-field names, order, scalar/map roles, and byte-compatible
legacy construction; it did not authorize a mutable, unvalidated address domain forever. This
amendment changes one existing field's admissible key domain (non-empty strings) and its nested
container behaviour (validated immutable **copy**) while preserving its name, optionality, values,
map-over-scalar precedence, serializable logical content for valid maps, and every scalar field.
Existing valid maps retain their bytes and resolution meaning. Callers that supplied `""`, mutated
the field after construction, or mutate a retained caller alias now fail or observe isolation; that
is the ratified, deliberate compatibility cost. The argument reuses the compatibility analysis
category B-101(a) records; paying that cost for this map field is not the same as implementing
B-101(a)'s discriminator, and it does not disturb B-101's separate close or promotion trigger.

### §0.4 Implementation remainder

U-CP-64 owns the implementation. It owes the filtered scalar candidate set, `ResumeContext`
validation plus immutable copied storage, the resolver-boundary guard, the b80 pin update, and the
witness inventory stated in plan v2.49. No capture-side carrier or hash changes are owed.

## §1 AMENDMENT — effect-fence empty-key resolution is unaddressable

### §1.1 `Spec_Control_Plane_v1_107.md` §1.1 membership amendment

For uniform-fallback eligibility, the authoritative unaddressed effect-fence-pause set contains
only locations whose captured `idempotency_key` is **non-empty** and whose key is absent from
`effect_fence_resolutions`. An empty captured key is position-only and is excluded before the
sole-unaddressed-location computation. Thus the scalar uniform fallback cannot nominate `""`.
This is the sole classification amendment; map entries remain map entries only for valid non-empty
keys.

### §1.2 `ResumeContext.effect_fence_resolutions` map-domain amendment

On ordinary construction, each `effect_fence_resolutions` key MUST be non-empty. The field MUST be
a validated immutable **copy** of the supplied mapping: validate keys and values, copy them, then
expose no mutation route. A proxy or view over a caller-retained mapping does not satisfy this
term. The contract applies by inheritance to `AccessorDerivedResumeContext` and any other subclass.

### §1.3 Resolver-boundary contract term

At every resolver consult, an empty `idempotency_key` is unresolvable and yields no directive
before either a map-hit check or uniform-eligibility comparison. The public
`effect_fence_uniform_fallback_eligible_key` parameter remains caller-supplied, but is not a second
classification authority: a caller-supplied `""` cannot make an empty location resolvable. This
consumption-boundary term makes validation-bypassed map content inert and prevents an empty-key
directive from affecting a keyed sibling.

### §1.4 Reconciliation of `Spec_Control_Plane_v1_112.md` §2.1 publication

The v1.112 §2.1 sentence that the authoritative walk includes the empty key and the uniform
fallback computation counts it described the then-current implementation and cannot remain an
unqualified current statement after §1.1. The walk may still publish key-absent position-only
source shapes, but scalar uniform-fallback membership excludes them; only non-empty captured keys
participate in unaddressed/eligible classification. Per v1.112 §2.4, this is publication of the
§1.1 rule, not a second authority.

### §1.5 Forged-instance boundary

A `ResumeContext` made by validation bypass (including `model_construct`) is not an ordinary map
channel construction and is outside B-107's closure criterion. It MUST nevertheless be inert under
§1.3: its empty-key content is neither honoured nor allowed to alter another location's decision.
No diagnostic is required for that forged object.

## §2 What this delta does not do

- It does not change the four variants, ten source shapes, or seven carriers.
- It does not add a Runtime §30 class, Runtime spec delta, capture-side refusal, carrier field, or
  hash change.
- It does not add a CXA §2.3 row: this is a CP-owned type plus CP-internal classification.
- It does not close B-107; the separately owed U-CP-64 implementation and witnesses remain open.

## §3 Filing footer

| Field | Value |
|---|---|
| Artifact | `Spec_Control_Plane_v1_115.md` |
| Amendment sites | THREE contract sites: v1.107 §1.1 membership; `ResumeContext.effect_fence_resolutions`; resolver boundary. ONE publication reconciliation: v1.112 §2.1 |
| Preserved | Four variants / ten shapes / seven carriers; all untouched prior bodies |
| Contract numbers | ZERO new |
| Runtime / CXA | No Runtime delta or class; CXA classification-only, no §2.3 row |
| Plan delta | `Implementation_Plan_Control_Plane_v2_49.md`, U-CP-64 amendment |
| Implementation | Separately owed; not bundled |
