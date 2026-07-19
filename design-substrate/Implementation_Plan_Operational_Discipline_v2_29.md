# Implementation Plan — Operational Discipline (v2.29)

*Delta over v2.28. v2.29 is the OD plan leg of the RATIFIED **B-51 / B-52 / B-54 OD audit-signing amendment arc** (`.harness/class_1_fork_b51_b52_b54_od_signing_amendment_arc.md`, **RATIFIED 2026-07-18 — all ten gate items ratified AS RECOMMENDED**; three dyadic council convenings at the apply leg, **all-CONFIRM, zero deviations**), absorbing **OD spec v1.34** (`Spec_Operational_Discipline_v1_34.md`: AMENDED §21.2.1 + NEW §21.2.2 + NEW §21.2.3). The **U-OD-30** acceptance criteria pinned at v2.6 §3.7.4 (preserved through the v2.28 head) are STALE against v1.34: they pin the tenant-less `sign_audit_entry(payload, key_id, algo)` signature and a `verify_hash_chain_integrity` that never touches `signature_attrs`. v2.29 amends U-OD-30 and authors **ONE NEW atomic unit U-OD-55** (the §21.2.2 backend-aware verification API — no existing unit carries a signature-verification surface; U-OD-55 is the next free OD unit ID after v2.14's U-OD-35..U-OD-54 block, verified by grep across the v2.1..v2.28 chain). All sections except the §0 change note, the §3.7.4 U-OD-30 amendments, the NEW U-OD-55 body, and the §3 coverage/dependency delta below are PRESERVED VERBATIM from v2.28 (which preserved verbatim from v2.27 + ... + the v2.1 baseline).*

## §0 Change note (v2.28 → v2.29)

### §0.1 Revision context — OD spec v1.34 absorption

The B-51/B-52/B-54 arc (fork gate item 10: one bundle — OD v1.33 → v1.34 + CP v1.100 → v1.101 + Runtime v1.100 → v1.101 + the OD/CP/Runtime plan deltas) amends the C-OD-21 signing surface in three ratified legs. The plan-side staleness this delta clears (per the fork's ratification-gate plan-delta clause, filing codex round-11 P2 / round-12 P2):

> §3.7.4 U-OD-30 signature pin (v2.6, preserved through v2.28): `fn sign_audit_entry(payload : AuditPayload, key_id : string, algo : SignatureAlgorithm) -> AuditSignatureAttributes` — tenant-less; no fifth canonical-message segment; no tenant-tag normalization at signing.
> §3.7.4 U-OD-30 `verify_hash_chain_integrity(ledger : AuditLedger) -> Result<(), HashChainBreach>` — content + linkage only; the v1.34 §21.2.2 backend-aware signature-verification API has NO covering unit anywhere in the chain.

Companion deltas in the same arc: CP plan v2.38 (the tenant-bearing `cp_audit_to_od_audit` + the four CP-owned sections) and Runtime plan v2.49 (the `audit_signing_fail_closed` carrier + MTC config validation + prewarm/keepalive disable + tenant threading + §13.5 inspect inputs + B-53 subcommand).

### §0.2 Sections revised

§0 (this change note); §1 (the §3.7.4 U-OD-30 amendment); §2 (NEW unit U-OD-55); §3 (coverage matrix + dependency-graph delta). All other sections — every other unit body, the v2.28 U-OD-21 amendments, and all v2.1-baseline structure — PRESERVED VERBATIM from v2.28.

### §0.3 Scope discipline

ADDITIVE. ONE new atomic unit (U-OD-55). ONE amended unit (U-OD-30). ZERO deletions. The OD-owned witness classes of the v1.34 change-note ((a)–(f), each mutation-probed per Workflow v1.18 PD-8) are transcribed as `Tests:` criteria at their home units below — (a)/(b)/(f) at U-OD-30, (c)/(d) at U-OD-55; witness (e) (flag-validation) is Runtime-owned enforcement and is transcribed at Runtime plan v2.49 U-RT-134, cross-referenced not duplicated here. The `audit_signing_fail_closed` flag CARRIER, env contract, and bootstrap-validation enforcement are Runtime-owned (Runtime plan v2.49 U-RT-134); this delta pins only the OD-owned §21.2.3 policy criteria (typed boundary + redaction posture) at U-OD-30.

---

## §1 §3.7.4 U-OD-30 — acceptance-criteria + signature amendment (OD v1.34 §21.2.1 + §21.2.3)

The v2.6 signature block and acc #1–#16 are amended as follows (everything not restated — `TenantSeparationStrategy`, `PerTenantSeparation`, `PER_TENANT_SEPARATION_BINDINGS`, `SignatureAlgorithm` note, `verify_hash_chain_integrity`, `assert_tenant_id_on_every_span_at_multi_tenant_cells`, acc #1–#16, `Inputs`, `Rollback boundary` — PRESERVED VERBATIM from the v2.6/v2.7 state):

**Implements (amended v2.29):** [C-OD-21 §21.1, §21.2 (incl. AMENDED §21.2.1 + NEW §21.2.3 at OD v1.34), §21.3] — the NEW §21.2.2 verification API is decomposed to U-OD-55, not carried here.

**`sign_audit_entry` signature (amended v2.29):**

```
fn sign_audit_entry(payload : AuditPayload, key_id : string, algo : SignatureAlgorithm,
                    *,
                    backend : SigningBackend | None = None,   // as-built OD v1.33 §21.2.1 composition-root seam
                                                              // (restated descriptively — never plan-absorbed at
                                                              // its own landing; NOT amended here)
                    tenant_id : string | None = None)         // NEW at v2.29 — OD v1.34 §21.2.1 row 3
  -> AuditSignatureAttributes
```

*(Surfaced finding, mirroring CP v1.101's own restatement discipline: the `backend` keyword landed at the B-22 arc spec+impl-together with no plan delta — the annotation above is descriptive restatement so the implementer reads one truthful signature; the v2.29 AMENDMENT is exactly one token: `tenant_id`.)*

**Acceptance criteria (v2.29 additions #17–#23; #1–#16 preserved verbatim):**

17. **(§21.2.1 rows 1, 3.)** `tenant_id` present → the canonical signing message is the FIVE-length-prefixed-segment form `(compute_entry_hash(payload), key_id, algo.value, "DEPLOYMENT_BOUND", tenant_tag)`; the length-prefix encoding keeps the four-tuple/five-tuple pair injective. `tenant_id` absent/`None` → the segment is DROPPED and the existing four-tuple message is PRESERVED VERBATIM byte-for-byte (the B-22 → B-31 byte-compat precedent) — zero regression for every existing caller and for single-tenant deployments.
18. **(§21.2.1 row 2 — dyad-1 pin; normalizer HOMED in `harness_od`, codex rounds 2/14.)** The impl AUTHORS the tenant-tag rule-set as a `harness_od` export with TWO projections (the ONE authority): `signing_token` (`None` → `None`, no segment) and `sidecar_tag` (`None` → `"_single"`, the writer's preserved byte-shape); shared rules: empty string and the reserved `"_single"` literal REFUSED with a raise; any other value passes through unchanged, and for non-`None` tenants both projections return the IDENTICAL tag (`harness-od` cannot import the runtime writer, so the rules live HERE and the writer delegates its `sidecar_tag` half, per the U-RT-137 enforcement criterion). Signing applies this normalizer to its `tenant_id` before composing the fifth segment — the signed segment and the sidecar `tenant_tag` join key are the SAME token by construction (the U-OD-55 verifier applies the identical normalizer to its tenant-scope input).
19. **(§21.2.1 row 4.)** The non-converter redaction-map compose path carries tenant: `compose_redaction_token_audit_entry` accepts and forwards the tenant parameter; the runtime `AuditLedgerRedactionTokenMap` carrier (which already holds tenant scope as its own `_tenant_id`) supplies it.
20. **(§21.2.1 row 6 — cross-referenced.)** At MULTI_TENANT_COMPLIANCE, tenant scope is REQUIRED — the config-validation enforcement site is Runtime-owned (Runtime plan v2.49 U-RT-134); the OD-side behavior criterion is that signing does not silently keep an MTC deployment on the tenant-unbound four-tuple.
21. **(§21.2.1 row 7 — enforcement site, codex round-8 P2.)** `sign_rotation_pair` is PROHIBITED at MULTI_TENANT_COMPLIANCE until `B-33`'s rotation-aware message binding lands (the v1.33 out-of-scope deferral STRENGTHENED to an explicit prohibition); non-MTC tiers unchanged. The function itself takes no tier input and has ZERO production callers on `main` (verified at apply time — its API is NOT amended here; adding a tier parameter would be an unratified contract change), so the enforceable slice at THIS arc is a CALLER-REGRESSION GUARD: a static witness asserting `sign_rotation_pair` has no production caller in `harness-runtime`/`harness-cp`/`harness-cxa` source (a new caller must confront the prohibition and this test), replacing any vacuous no-call runtime test; the tier-aware refusal at the first real call site is `B-33`'s carried obligation (recorded at that row).
22. **(§21.2.3 row 5 — single typed boundary.)** ALL signing and signature-validation failures — including a configured backend advertising a mismatched algorithm or returning a malformed/non-byte/wrong-length signature (today plain `ValueError`/`TypeError`) — route through the typed `AUDIT_SIGNING_HARD_FAILURES` family before any policy catch consults the flag; untyped backend errors MUST NOT escape into generic catches.
23. **(§21.2.3 row 6 — redaction unconditional.)** The redaction-token signing path is NOT flag-gated: fail-closed at every persona tier, always; signing failures on this path route through the acc-#22 typed boundary and PROPAGATE — blind catches (e.g. the `RedactionSpanProcessor.on_end` `(KeyError, TypeError)` catch) must not swallow them; a removal-then-swallow branch is NOT a permitted implementation, AND an ABSENT backend on this path is itself a typed failure (codex round-16: at solo/team defaults `backend=None` returns the placeholder without raising — the redaction path raises instead of placeholder-signing, at every tier; OD v1.34 §21.2.3 row 6); token assignment that did not complete against a signed row leaves NOTHING exportable. Witness extension: `test_redaction_path_absent_backend_raises_typed_every_tier` (mutation probe: letting the placeholder through on the redaction path fails).

**`Tests:` (v2.29 additions — each mutation-probed per Workflow v1.18 PD-8; v2.6-and-earlier tests preserved verbatim):**

> **Witness (a) — five-tuple byte-injectivity:** `test_five_segment_message_tenant_tag_swap_breaks_verification` (a tenant-tag swap on a signed entry breaks verification; message injective across all five segments). **Witness (b) — four-tuple byte-identity:** `test_tenant_absent_message_and_attrs_byte_identical_to_v1_33_path` (with tenant absent, the canonical message and resulting `AuditSignatureAttributes` are byte-identical to the pre-amendment path for every existing caller). **Witness (f) — redaction unconditional fail-closed:** `test_redaction_path_signing_failure_typed_at_every_tier_nothing_exportable` (a signing failure on the redaction-token path surfaces as a typed error at every tier, flag state notwithstanding, and never leaves the raw value exportable). Plus: `test_tenant_tag_normalization_refuses_empty_and_single_literal`, `test_sign_rotation_pair_has_no_production_caller` (static caller-regression guard over harness-runtime/harness-cp/harness-cxa source; mutation probe: introducing a caller fails it).

**Rollback boundary (v2.29 addition):** reverting removes the `tenant_id` parameter + fifth segment; the tenant-unbound-signature exposure (B-51) reopens; U-OD-55 era selection loses the five-tuple arm.

---

## §2 NEW §3.7.6 U-OD-55 — backend-aware audit-signature verification API (OD v1.34 §21.2.2)

**Implements:** [C-OD-21 §21.2.2 (NEW at OD v1.34)]

**Depends on:** [U-OD-00, U-OD-30] — consumes the U-OD-00 audit-ledger composition types (`AuditLedger` entries, `AuditSignatureAttributes`, `SignatureAlgorithm`) and U-OD-30's canonical-message construction (the verifier reconstructs the message signing produced). Acyclic: both are upstream. Cross-axis CONSUMERS (not dependencies): CP plan v2.38's amended U-CP-44/U-CP-45 bind the §20.3.1 audit-walk to this API; Runtime plan v2.49 U-RT-138 carries its operator-facing inputs.

**Files affected (logical):** the OD per-family audit verification surface (extends the B-49 per-family verifier over `Sequence[AuditLedgerEntry]`); the OD typed-error surface (NEW `AuditSignatureInvalid`).

**Signatures:** an OPTIONAL verification-backend RESOLVER parameter on the per-family verifier surface — per-row backend resolution keyed on each entry's STORED `(audit_signature_algorithm, audit_signature_key_id)`; an expected-tenant-scope parameter; an authenticated-cutover-record input (U-OD-55 also OWNS the record carrier per OD v1.34 §21.2.2 row 4's wire contract: the schema-versioned Pydantic model, the `{placeholder_exempt, four_tuple_real, quarantined}` disposition enum, and the length-prefixed canonical record message signed via the §20.2.1 `SigningBackend` protocol under the reserved record-scope key; witnesses `test_record_canonical_message_golden_vectors` (a fixture record's canonical bytes match the pinned golden vector byte-for-byte — mutation probe: any serialization-order/encoding change breaks it) and `test_record_canonical_message_deterministic_and_tamper_evident` — reordering rows yields the same message (sorted canonical quadruple form) while altering ANY field of a row — `source_tag` INCLUDED (codex round-17: a rewritten source_tag must invalidate the signature, or an attacker redirects an exemption/alias to another same-hash tenant row) — or any metadata field breaks record verification; plus `test_record_source_scoped_uniqueness` — two `source_tag="_single"` rows sharing an `entry_hash` are REJECTED (one-to-many alias foreclosed), two rows sharing a full `(source_tag, entry_hash)` are REJECTED (conflicting dispositions), while two ALREADY-TAGGED rows under different source tags legitimately sharing an entry hash are ACCEPTED, and two NON-quarantined rows with COLLIDING destination `(tenant_scope, entry_hash)` identities are REJECTED (codex rounds 15/16/18 — a `_single`→tenant-a migration colliding with an existing tenant-a/H row would duplicate a sidecar identity the writer rejects on fold; mutation probe: global hash-uniqueness rejects the legitimate multi-tenant case and fails; dropping the destination check passes the colliding record and fails)); an OBSERVED-baseline-identities input (codex round-7 P1: `read_full_entries_for_tenant` converts `legacy_baseline` rows into exemptions and OMITS their identities from the returned entries, so the verifier cannot cross-check declared-vs-observed from the entry sequence alone — the sidecar reader exposes the observed `(tenant_tag, entry_hash)` identities — `legacy_baseline` identities AND leftover `"_single"` full-entry identities (codex round-10: full-entry rows omitted from the record are otherwise silently unreachable under tenant-scoped reads) — via a richer read result or a separate accessor, and the verifier reports BOTH a recorded identity missing from the observation AND an observed identity missing from the record; witness `test_declared_vs_observed_baseline_divergence_reported_both_ways`, mutation probe: dropping either direction of the cross-check fails). *(Exact parameter/type names are implementation discretion per §21.2.2; non-binding suggestion: `backend_resolver: Callable[[SignatureAlgorithm, str], SigningBackend]`.)*

**Acceptance criteria:**

1. **(Row 1.)** The verification parameter is a per-row RESOLVER keyed on each entry's stored `(algorithm, key_id)` — NOT a single `SigningBackend | None` parameter (one backend cannot verify mixed multi-algorithm history). Absent resolver → current behavior (hash-chain + content integrity only) PRESERVED VERBATIM. Present → per-entry backend verify over the reconstructed canonical message, with `"DEPLOYMENT_BOUND"` projected to `key_period=0` exactly as signing does.
2. **(Row 2.)** Tenant scope is a verifier INPUT (the fifth segment is unreconstructable from bare `AuditLedgerEntry` rows), normalized by the SAME §21.2.1 row-2 tag normalization as signing (one source of truth at both ends).
3. **(Row 3.)** Message-format cutover: pre-cutover REAL signatures verify against the FOUR-tuple; post-cutover rows verify against the message shape the tenant-scope input implies (five-tuple under non-`None` tenant; preserved four-tuple under `None`). Era membership is decided by the authenticated cutover record — NEVER inferred from the signature value or any mutable row field.
4. **(Rows 4–5.)** Legacy exemption is gated EXCLUSIVELY on the operator-recorded cutover record: AUTHENTICATED (signed or anchored outside the rewritable ledger), CONTENT-BOUND (exact legacy entry hashes or a digest/root — never date/version/row-position), TENANT-BOUND with per-row disposition (signed `(tenant_scope, entry_hash, verification_disposition)` TRIPLES); exemption NEVER keyed on signature-value SHAPE. Legacy tenant bindings require a trusted source (external authoritative mapping, operator attestation, or declared TOFU + quarantine); families whose `entry_hash` already binds tenant transitively (cost family, §21.2.1 row 5) admit content-derived binding.
5. **(Row 6.)** `legacy_baseline` identities are part of the verification INPUT: cross-checked against the cutover record and reported EXPLICITLY (exempt / quarantined / UNVERIFIED with the nonzero outcome), never omitted.
6. **(Row 7.)** Typed failure taxonomy: (a) backend verify-mismatch → NEW typed `AuditSignatureInvalid` (NOT `HashChainBreach`, which stays reserved for content/linkage tampering); (b) backend availability errors — including a `key_id` unknown to the supplied resolver/mapping — surface through a DEDICATED typed `harness_od` availability exception wrapping the underlying cause (codex round-6 P1: the discriminator consumers — incl. the CP adapter — key on the TYPE; a programming `KeyError`/`TypeError` from the resolver propagates UNWRAPPED as a defect), never a verdict; witness: `test_availability_typed_vs_defect_unwrapped` (an unknown key_id surfaces as the typed availability error; an injected resolver raising `TypeError` propagates unwrapped — mutation probe: wrapping everything fails the defect case); (c) malformed signature VALUES against the stored algorithm's `C-CP-20 §20.4` fixed width → `AuditSignatureInvalid` with the malformation named. Branch (c) scoped to what the entry types can represent (pre-parse malformation stays at the reader boundary).
7. **(Row 8.)** The OD API's default posture is NON-BLOCKING (reports; does not gate dispatch). The MTC UNVERIFIED-nonzero inspection disposition is carried at the Runtime-owned inspect surface (Runtime plan v2.49 U-RT-138); the CP-owned §20.3.1 blocking-walk binding is carried at CP plan v2.38 (amended U-CP-44/U-CP-45) — both cross-referenced, not restated.
8. **(Row 9 — dyad-3 pin.)** The runtime breaker wrapper's sign-instrumented / verify-passthrough asymmetry is INTENTIONAL and PRESERVED — this unit MUST NOT breaker-couple the read path.

**Tests (each mutation-probed per Workflow v1.18 PD-8):**

> **Witness (c) — cutover-era verification:** `test_pre_cutover_real_four_tuple_signature_verifies`, `test_post_cutover_tenant_row_verifies_only_against_five_tuple`, `test_unsigned_shaped_value_absent_from_cutover_record_not_exempt` (the downgrade-path witness). **Witness (d) — taxonomy discriminators:** `test_signature_invalid_vs_hash_chain_breach_vs_availability_distinguishable_at_caller` (incl. unknown `key_id` propagating as availability, not a verdict). Plus: `test_absent_resolver_preserves_hash_only_behavior_verbatim`, `test_legacy_baseline_identities_reported_never_omitted`, `test_verify_path_not_breaker_instrumented`.

**Rollback boundary:** revert the verifier extension + `AuditSignatureInvalid`; the B-54 no-committed-verification-path gap reopens; CP plan v2.38's §20.3.1 walk amendment and Runtime plan v2.49 U-RT-138 lose their API substrate.

---

## §3 Coverage matrix + dependency graph delta (v2.28 → v2.29)

| Contract | Units covering (delta) |
|---|---|
| C-OD-21 §21.2.1 (AMENDED at v1.34) | U-OD-30 (amended acc #17–#21) |
| C-OD-21 §21.2.2 (NEW at v1.34) | **U-OD-55 (NEW)** |
| C-OD-21 §21.2.3 (NEW at v1.34) | U-OD-30 (acc #22–#23, OD-owned policy half) + Runtime plan v2.49 U-RT-134/U-RT-135/U-RT-136 (carrier/enforcement/wiring, cross-axis) |

Dependency graph: +U-OD-55 with edges U-OD-55 → U-OD-00, U-OD-55 → U-OD-30 (both upstream; acyclic — Kahn-verifiable, no inbound edge from either). All prior edges preserved verbatim.

**Canonical topology registration (codex round-28):** the inherited §4 node count is AMENDED 55 → **56** and the level decomposition gains **U-OD-55 at L9** — after its U-OD-30 dependency (whose amended criteria land at its existing level) — so topology-driven execution schedules the verifier unit; every other level assignment is preserved verbatim.

---

## §4 Filing footer

| Field | Value |
|---|---|
| Artifact | `Implementation_Plan_Operational_Discipline_v2_29.md` (delta over v2.28) |
| Authored at | Phase 7 — B-51/B-52/B-54 OD audit-signing amendment arc apply leg (2026-07-18) |
| Authoring authority | OD spec v1.34 (`Spec_Operational_Discipline_v1_34.md`) + `.harness/class_1_fork_b51_b52_b54_od_signing_amendment_arc.md` (RATIFIED 2026-07-18, all ten gate items AS RECOMMENDED; dyads 1–3 all-CONFIRM) |
| Predecessor | `Implementation_Plan_Operational_Discipline_v2_28.md` (v2.28 — U-OD-21 §15.1 4-axis reconciliation) |
| Siblings (same arc) | `Implementation_Plan_Control_Plane_v2_38.md` + `Implementation_Plan_Harness_Runtime_v2_49.md` |
| Revision policy | Delta-only per workspace `CLAUDE.md` §2.4; revisions route to design-phase back-flow |
