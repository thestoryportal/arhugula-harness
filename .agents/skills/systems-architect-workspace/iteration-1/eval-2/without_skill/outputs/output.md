# Architectural Resolution — `SecretScope` Internal Structure (C-AS-05 §5)

**Surfaced at:** Phase 7 sub-phase 7b, IS/AS axis-stream — U-AS-20 (`Implementation_Plan_Action_Surface_v1.md`), implementing C-AS-05 §5.1/§5.2/§5.4.
**Question:** `fetch_secret(name, scope: SecretScope) -> SecretRef` references a `SecretScope` type. Spec §5.4 defers "specific `SecretScope` serialization format" to implementation discretion, and U-AS-20's signature block declares `record SecretScope { ... }` with no fields. The plan unit needs a concrete `SecretScope`. What is the architectural call?

---

## 1. Fork classification

This is **not a Class 1 (halt-execution) fork** — but it is *adjacent* to one, and the boundary must be drawn precisely before any code is written.

| Reading | Classification | Justification |
|---|---|---|
| "The spec under-specifies a *contract* surface — `SecretScope`'s **field set / semantic dimensions**" | **Class 1** — design defect; route to design-phase back-flow | Field set is contract authority. If the implementer invents the dimensions, that is silent H_T design extension (X-AL-3 violation). |
| "The spec deferred only the **serialization format** (wire/byte encoding) of an already-semantically-determined type" | **Class 2** — in-execution operator decision within an explicit deferral envelope | §5.4 names exactly "serialization format" as deferred. Format ≠ field set. |

The resolution turns on whether C-AS-05 (read together with its ADR-F5 anchor) *does* commit `SecretScope`'s semantic dimensions, leaving only the encoding open. **It does.** See §2. Therefore the operative classification is **Class 2** — but with a Class 1 escalation tripwire stated in §5.

## 2. What the canonical chain already commits

`SecretScope` is **not** an undefined type. The authority chain constrains it on three independent axes:

**(a) ADR-F5 v1.1 §Context / §Decision — `scope` is the credential-dimension session key.**
ADR-F5 states `fetch_secret(name, scope) -> SecretRef` and that "F5's `scope` parameter is the credential-dimension session key, separate from ADR-F1's routing-dimension session key." This is a *foundational* commitment (ADR tier, top of the §1.3 authority chain). It fixes `SecretScope`'s **purpose**: it is a session-scoped key that partitions credential resolution so that session-keyed provider credentials "persist across fallback-chain advancement without leaking across sessions" (ADR-F5 §Context, re ADR-F1 §(a) sticky-routing). A `SecretScope` value therefore must carry **enough identity to (i) uniquely partition a credential namespace and (ii) bound a credential's blast radius to one session**.

**(b) C-AS-05 §5.1 — `scope` is orthogonal to the routing-dimension session key.**
The spec contract table row for `scope` says "Credential-dimension session key per ADR-F5 v1.1 §Context; orthogonal to ADR-F1's routing-dimension session key." Orthogonality is a *contract constraint*: `SecretScope` MUST NOT be structurally fused with, or substitutable for, the CP-axis routing session key. They are distinct types.

**(c) C-AS-05 §5.3 + C-AS-07 §7.3 + C-AS-08 §8.1 — three downstream consumers fix `SecretScope`'s observable obligations.**
- C-AS-07 §7.3 / U-AS-24: the per-`(secret_backend, scope)` circuit breaker. `SecretBackendBreakerKey` embeds `scope`, and `construct_breaker_key` must be **deterministic** (U-AS-24 AC 7: identical inputs → identical keys; AC: distinct for different scope). ⇒ `SecretScope` must be **value-equatable and deterministically hashable**.
- C-AS-08 §8.1 / U-AS-25: `outputs_hash = SHA-256(canonicalize_concat(secret.name, secret.scope, secret.last_rotated_at))`. `scope` is fed into the IS-axis canonicalization (C-IS-06 §6.1, U-IS-08). ⇒ `SecretScope` must have a **deterministic canonical byte-serialization** — and *this* is exactly the "serialization format" §5.4 defers.
- C-AS-05 §5.3 (negative-observation): `scope` participates in the audit-ledger fingerprint **as metadata, structure-not-content**. ⇒ `SecretScope` fields MUST be **non-sensitive identifiers only** — no secret material, no credential values, ever, by construction.

**Conclusion of §2.** The chain fixes `SecretScope`'s *role* (session-scoped credential-namespace key), its *type discipline* (distinct from routing key; value-equatable; deterministically hashable; canonically serializable; non-sensitive-by-construction), and its *deferral envelope* (§5.4 defers the **byte/wire serialization format**, not the field set). What it does **not** spell out field-by-field is the concrete attribute list. That gap is the legitimate Class 2 decision.

## 3. The architectural resolution

**Adopt a minimal, closed, two-field `SecretScope` value type, sealed at the AS-axis foundational unit (U-AS-20), with canonical serialization delegated to the IS-axis canonicalizer.**

### 3.1 Field set (the Class 2 decision — minimal closure)

```python
class SecretScope(BaseModel, frozen=True):   # Pydantic v2, frozen ⇒ hashable, value-equatable
    session_id: str   # the credential-dimension session identity (ADR-F5 §Context).
                      # Bounds a fetched credential's blast radius to exactly one harness session.
    realm: str        # the credential namespace partition within a session — the dimension
                      # that lets one session hold multiple non-colliding credential sets
                      # (e.g. distinct provider/tenant credential families). Opaque string;
                      # never the secret name, never secret material.
```

**Why exactly these two and no more.** ADR-F5's commitment requires *session identity* (blast-radius bound) and a *partition dimension* (so sticky-routing across a fallback chain resolves the same credential family). Two fields satisfy both. Adding more (deployment surface, persona tier, provider id) would be **silent H_T design extension (X-AL-3)** — those dimensions belong to other axes' types and re-deriving them inside `SecretScope` fuses concerns the chain holds orthogonal. Fewer (a bare `str`) collapses the namespace partition and breaks ADR-F5's multi-credential-family requirement. Minimal-closed is the conservative reading.

**Why frozen / value type.** Directly discharges the U-AS-24 determinism ACs (hashable breaker key) and the U-AS-25 canonicalization requirement. `frozen=True` gives structural equality and `__hash__` for free; no hand-rolled equality.

### 3.2 Serialization format (the §5.4-deferred item — discharge, don't re-defer)

`SecretScope` canonical serialization is **not** invented at the AS axis. Per C-AS-08 §8.1, `scope` is fed to `canonicalize_concat` which is **C-IS-06 §6.1 canonicalization, materialized at U-IS-08** (cross-axis dependency U-AS-25 → U-IS-08 already in the plan graph). The §5.4 "serialization format" deferral is discharged by: serialize `SecretScope` as the deterministic ordered concatenation of its fields (`session_id` then `realm`, each length-prefixed or delimiter-escaped per U-IS-08's canonical rule). No new canonicalization primitive is created — this is reuse of an existing IS-axis seam, which is the correct framework-pull-disciplined move.

### 3.3 Placement

Declare `SecretScope` in U-AS-20 (it is already the unit that owns `record SecretScope { ... }` and is the L1 foundational unit for the secrets subsystem). It is consumed by U-AS-22 (`SecretAllowlistEntry.scope`), U-AS-24 (`SecretBackendBreakerKey.scope`), and U-AS-25 (`outputs_hash`). Sealing it minimally at U-AS-20 is consistent with those three downstream signatures, which all already type their `scope` field as `SecretScope` without adding fields.

## 4. Why this is Class 2, not Class 1 — and the precedent

This mirrors a resolved precedent in the same workspace. The IS spec (C-IS-07, §7.1/§409) deferred "the relationship between the idempotent-write keying tuple and the C-IS-05 six-field entry shape" to a downstream D-ADR — that *was* a contract-shape question and was correctly held as design back-flow. The `SecretScope` case is **weaker than that**: ADR-F5 already commits the type's role and orthogonality, and §5.4 deferred only the *format*. Selecting a minimal field set that is fully entailed by the foundational ADR is an executability decision inside an explicit deferral envelope, not a contract revision. Record it as a **Class 2 in-execution operator decision** in the Phase 7 sub-phase log (and per the workspace memory pattern, a `Class_3_Tension` / decision record), with the field-set rationale above attached.

## 5. Class 1 escalation tripwire

Halt U-AS-20 and route to design-phase back-flow (Class 1) **if any of the following surfaces** while implementing or wiring downstream units:

1. A downstream unit (U-AS-22/24/25, or a CXA edge) requires a `SecretScope` field **not** entailed by ADR-F5 — e.g. it needs `provider_id` or `deployment_surface` *inside* the scope key. That would mean the two-field closure is wrong and the contract genuinely under-specifies the field set ⇒ design defect.
2. A CXA cross-axis edge requires `SecretScope` to be **structurally unified** with the CP-axis routing session key — directly contradicts C-AS-05 §5.1 orthogonality ⇒ contract conflict, route to back-flow.
3. `SecretScope` is found to need to carry any **value-bearing or sensitive** field to satisfy a consumer — contradicts §5.3 structure-not-content ⇒ design defect.

Absent those, proceed with the §3 resolution. Silent absorption of a real field-set defect is the worst failure mode (CLAUDE.md §4.3); the tripwire exists so the minimal-closure decision stays falsifiable.

## 6. Recommendation summary

| Item | Resolution |
|---|---|
| Fork class | Class 2 (in-execution operator decision within §5.4's explicit deferral envelope) — **not** Class 1 |
| `SecretScope` field set | Closed two-field value type: `session_id: str`, `realm: str` — minimal closure entailed by ADR-F5 §Context |
| Type discipline | Pydantic v2 `frozen=True` model: value-equatable, deterministically hashable, non-sensitive-by-construction |
| Serialization (§5.4 deferral) | Discharge via U-IS-08 / C-IS-06 §6.1 canonical concatenation — no new primitive |
| Placement | U-AS-20; consumed unchanged by U-AS-22 / U-AS-24 / U-AS-25 |
| Governance | Record as Class 2 decision in 7b sub-phase log + Class_3 decision record; attach §3.1 rationale |
| Tripwire | Escalate to Class 1 back-flow if §5 conditions 1–3 surface |

---

*Authority chain consulted: ADR-F5 v1.1 §Context/§Decision/§Consequences; `Spec_Action_Surface_v1.md` C-AS-05 §5.1–§5.4, C-AS-06 §6, C-AS-07 §7, C-AS-08 §8; `Implementation_Plan_Action_Surface_v1.md` U-AS-20/22/24/25; `Spec_Information_Substrate_v1.md` C-IS-06 §6.1 / C-IS-07 §409 deferral precedent; CLAUDE.md §1.3 authority chain, §4.3 back-flow routing, §4.4 X-AL-3. The systems-architect role recommends; the operator decides.*
