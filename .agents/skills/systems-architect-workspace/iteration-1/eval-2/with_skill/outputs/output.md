# Phase 7 Tension Resolution — `SecretScope` internal structure under-committed

**Mode:** Tension-resolution (Phase 7), `systems-architect` skill §4A.
**Status:** Resolution recommendation. **The operator decides** — this skill recommends, it does not decide (§4A.4).
**Surfaced by:** AS-axis implementation, Cluster 5 (U-AS-20), against `C-AS-05 §5`.

---

## 1. Tension stated precisely (§4A.2 step 1)

`fetch_secret` takes a `scope` parameter typed `SecretScope`. The contract names the type and assigns it a *semantic role* but never commits its *internal structure*. The implementation of U-AS-20 needs a concrete `SecretScope` and cannot read one off the authority chain.

Divergent / silent sources, quoted verbatim:

**Spec — `Spec_Action_Surface_v1.md` C-AS-05 §5.1** (the type is named and given a role):
> `scope` | `SecretScope` | Credential-dimension session key per ADR-F5 v1.1 §Context; orthogonal to ADR-F1's routing-dimension session key

**Spec — `Spec_Action_Surface_v1.md` C-AS-05 §5.4 "Deferred to implementation discretion"** (the *serialization format* is deferred — and only the serialization format):
> ... specific `SecretScope` serialization format ...

**Plan — `Implementation_Plan_Action_Surface_v1.md` U-AS-20 §Signatures** (the plan itself records the gap):
> `record SecretScope { ... }                        // serialization deferred`

This is not a spec↔plan *contradiction*. The plan faithfully mirrors the spec: both name `SecretScope`, both treat its shape as undefined. The tension is a **single-source under-specification** — C-AS-05 §5.4 defers the *serialization format* but no contract anywhere commits the *field set* (the internal structure). The plan's `{ ... }` placeholder is the gap made visible.

**Distinction that drives the resolution:** "serialization format" (how a value is encoded to bytes/JSON) and "internal structure" (which fields the type carries) are different commitments. §5.4 defers only the former. The latter is *unaddressed*, not *deferred*. An unaddressed type-shape that downstream contracts depend on is a design gap, not an implementation-discretion item.

## 2. Authority-chain placement (§4A.2 step 2)

Chain (`CLAUDE.md` §1.3): ADR (F1–F5 + D1–D6) → ADD v1.3 → PRD v1.1 → per-axis spec v1.x → per-axis plan v2.x + CXA v2.1.

Walking the chain for a commitment on `SecretScope`'s field set:

| Artifact | Speaks to `SecretScope` structure? | Evidence |
|---|---|---|
| ADR-F5 v1.1 | **No.** Names `scope` as "the credential-dimension session key, separate from ADR-F1's routing-dimension session key" (§Context); commits the *role*, not the *fields*. §Decision and §Consequences never enumerate `SecretScope` fields. | `ADR-F5.md` §Context, §Decision |
| ADD v1.3 §2.5 | **No.** Synthesizes F5; no `SecretScope` field commitment. | `Architectural_Design_Document_v1_3.md` (grep: no `SecretScope`) |
| PRD v1.1 | **No.** R-AS-04 is a negative-observation requirement (secrets absent from prompts/logs); says nothing of `scope` shape. | — |
| Spec C-AS-05 | **Partial.** Names the type and role; §5.4 defers only *serialization format*. | §5.1, §5.4 |
| Plan U-AS-20 | **No.** `record SecretScope { ... } // serialization deferred` — explicitly unresolved. | §Signatures |

**Finding:** the highest artifact that speaks to `SecretScope` is ADR-F5 v1.1, and it commits only the *role*. No artifact on the chain commits the *field set*. The chain is genuinely silent on the structure.

## 3. §2-discipline analysis

**Five-axis decomposition (§2.1).** Primary axis: **Action surface** (tool/secret-fetch contract). Secondary: **Operational discipline** — `SecretScope` is load-bearing in three OD-adjacent contracts, which is why "implementation discretion" cannot absorb it:

- **Audit fingerprint (C-AS-08 §8.1):** `outputs_hash = sha256(secret.name || secret.scope || secret.last_rotated_at)`. The hash concatenates `secret.scope`. A structure-not-content fingerprint that is byte-deterministic across access events for the same secret version **requires a canonical, stable serialization of `SecretScope`**. This is the load-bearing reason §5.4 defers the *serialization format* — but a serialization cannot be canonicalized without first fixing the field set. Field set is upstream of serialization.
- **Breaker key (C-AS-07 §7.3):** breaker key is `(secret_backend, scope)`. `scope` is half a breaker-cell identity; it must be hashable/comparable for equality.
- **Allowlist intersection (C-AS-06 §6.2):** `fetch_secret(name, scope)` succeeds only if `(name, scope) ∈ tool.contract.required_secrets`. `scope` must support value-equality against `SecretAllowlistEntry.scope`.

So `SecretScope` is consumed at three deterministic gates (audit, breaker, allowlist). Its field set is a **contract-bearing fact**, not a discretion item.

**Probabilistic-deterministic boundary (§2.2).** `SecretScope` sits entirely on the **deterministic side** — it is an identity key feeding a hash, a breaker map, and an allowlist set membership test. Production reliability (audit determinism, breaker correctness, allowlist enforcement) depends on its shape being fixed and stable. A deterministic gate keyed on a type of undefined shape is not a met reliability property.

**Decision ordering (§2.3).** `SecretScope`'s *field set* is a **Foundational (F)-adjacent** commitment within the F5 surface: it constrains the C-AS-06/07/08 contracts downstream and the C-IS-05 audit-ledger composition cross-axis. The *serialization format* (§5.4-deferred) is correctly **Derivative (D)** — it depends on the field set and on the keyring/registry ecosystem choice. The chain conflated the two: it deferred the D-item and never made the F-adjacent one.

**Cross-axis verification (§2.5).** Action surface ↔ Information substrate: C-AS-08 audit entries compose into the C-IS-05 six-field state-ledger via `outputs_hash`. An unstable `SecretScope` serialization breaks hash-chain reproducibility (`Spec_Information_Substrate_v1.md` C-IS-06 re-canonicalization verification). The gap therefore propagates cross-axis to U-IS-07…U-IS-11 (the IS consumers named in the AS plan §1 table for C-AS-08).

## 4. Resolution recommendation (§4A.2 step 4)

**The authority chain is genuinely silent on `SecretScope`'s internal structure.** Per skill §4A.4: *"If the tension cannot be resolved by reading the authority chain — because the chain is genuinely silent — that is a design gap, not a tension; surface it as such (a Class 1 fork) rather than inventing the missing commitment (`CLAUDE.md` I-2 / X-AL-3)."*

The implementation cannot pick a `SecretScope` field set on implementation discretion, because:
- §5.4 defers only the *serialization format*, not the field set — picking the field set is not exercising a granted discretion; it is filling an *un-granted* gap.
- The field set is consumed by three deterministic contracts (C-AS-06/07/08) and one cross-axis contract (C-IS-05 via C-AS-08). Choosing it in `harness-as/` silently extends the H_T design surface — exactly the X-AL-3 / `CLAUDE.md` I-2 anti-pattern ("No H_T design extension at Phase 7 execution-time").

**Recommended reading:** This is a **Class 1 fork** — a design-phase artifact (Spec_Action_Surface_v1.md C-AS-05) is under-specified and requires revision before U-AS-20 can be implemented. Halt U-AS-20 (and its dependents U-AS-21…U-AS-27, per the U-AS-20 rollback boundary) pending the spec revision.

**Recommended revision target and shape:** `Spec_Action_Surface_v1.md` C-AS-05 §5 should be amended to add a new subsection (e.g. §5.5 "`SecretScope` structure") committing the **field set** of `SecretScope`, while leaving §5.4's *serialization format* deferral intact. The architecturally-indicated field set, traced to existing chain commitments:

| Field | Type | Traced to | Why required |
|---|---|---|---|
| (credential-dimension session key) identity field(s) | — | ADR-F5 §Context ("credential-dimension session key … orthogonal to ADR-F1's routing-dimension session key") | The role ADR-F5 already commits; the spec must make it a concrete field rather than a prose role. ADR-F1's routing-dimension session key shape is the precedent to mirror. |
| deployment-context discriminator | — | ADR-F5 §Decision (dev-tech vs prod-tech; "identical across dev and prod deployment surfaces"); §Rationale cross-deployment bridge | `SecretScope` is the cross-deployment bridge dimension; it must discriminate the deployment context. |

This skill **does not author the field set** — naming the exact fields and types is a spec-authoring decision (`spec-writer`), made after the operator confirms the Class 1 fork and the architectural shape above. The recommendation is: (1) the gap is real, (2) it routes to a C-AS-05 spec revision, (3) the revision adds a *field-set* commitment distinct from the §5.4 *serialization* deferral, (4) the field set should be anchored to the ADR-F5 §Context "credential-dimension session key" role and the ADR-F1 routing-dimension session-key precedent.

**Downstream artifacts that must absorb the resolution** (named, not edited — §4A.2 step 4):
- `Spec_Action_Surface_v1.md` C-AS-05 (primary revision; `spec-writer`).
- `Implementation_Plan_Action_Surface_v1.md` U-AS-20 — the `record SecretScope { ... }` placeholder becomes concrete (`implementation-planner`, after spec revision).
- C-AS-06 §6.2 and C-AS-07 §7.3 — confirm `(name, scope)` equality and `(secret_backend, scope)` breaker-key behavior against the now-concrete shape.
- C-AS-08 §8.1 — confirm the §5.4 *serialization format* (still deferred) can canonicalize the now-fixed field set deterministically for the `outputs_hash` concatenation.

## 5. Tiebreaker check (§4A.2 step 5)

The single verifiable fact that makes this recommendation determinate: **confirm that no artifact above the spec on the authority chain (ADR-F5 v1.1, ADD v1.3 §2.5, PRD v1.1) commits a `SecretScope` field set.** If such a commitment exists, this is *not* a design gap — it is a spec under-statement of an already-decided structure, and the resolution downgrades to "conform C-AS-05 to the existing upstream commitment" (no Class 1 halt, no new design). Verification performed for this recommendation: grep of ADD v1.3 returns no `SecretScope`; ADR-F5 §Context/§Decision/§Consequences name the *role* only. On that evidence the gap stands. The operator should re-confirm against ADR-F5 §Context full text before sign-off.

**Load-bearing-artifact flag:** the revision touches a Phase-5 canonical spec contract (C-AS-05) and propagates cross-axis to the IS audit-ledger consumers. It **requires explicit operator sign-off** before `spec-writer` applies it.

## 6. Fork classification (§4A.2 step 6)

**Class 1 (halt-execution)** per `Project_Workflow_v1_8.md` §2.7.6 / `CLAUDE.md` §4.3.

- A design-phase artifact (Spec_Action_Surface_v1.md C-AS-05) requires revision: it must commit `SecretScope`'s field set.
- Implication: **halt U-AS-20** and its dependent units (U-AS-21…U-AS-27 per the U-AS-20 rollback boundary; cross-axis C-AS-08 consumers U-IS-07…U-IS-11 are exposed). Implementation does not proceed on an invented field set.
- Per the workspace memory note "design-substrate divergence" (2026-05-15): design-phase back-flow is deprecated; the spec revision is applied **in-CLI** by `spec-writer` against `design-substrate/Spec_Action_Surface_v1.md`, and the tension is tracked as a `Phase_7_Class_3_Tension_NNN` / Class-1 tension record with the operator's clearing decision recorded. (Per `CLAUDE.md` §4.3 the *fork class* is 1; the *application channel* is in-CLI per the 2026-05-15 deprecation.)
- **Silent absorption is the worst failure mode** (`CLAUDE.md` §4.3): picking a `SecretScope` shape inside `harness-as/` without the spec revision would contaminate C-AS-06/07/08 and the C-IS-05 hash-chain against an invalid contract and propagate to every dependent unit. This recommendation exists to prevent that.

---

**Operator decides.** This skill recommends a Class 1 halt and a C-AS-05 spec revision (add a `SecretScope` field-set commitment, distinct from the §5.4 serialization deferral). It does not author the field set and does not edit the spec or plan — that is `spec-writer` / `implementation-planner` work, sequenced after operator sign-off.
