# `Spec_Operational_Discipline` v1.33 — delta over v1.32

**Filed:** 2026-07-16
**Authoring authority:** Phase 7 — post-Phase-8 forward-register arc **B-47** (`.harness/post-phase-8-forward-register.md` §B-47), bundled-absorption per workspace `CLAUDE.md` §11.4; grounded at ADR-D8 (Accepted 2026-07-16) + ADR-D5 v1.5 §1.4 row 3 + the `C-CP-20 §20.2.1` / `B-22` cleared precedent (CP spec v1.98, clearance `.harness/clearance/spec-control-plane-v1-98-cleared-2026-07-14.md`)
**Predecessor:** `Spec_Operational_Discipline_v1_32.md` (v1.32 — C-OD-07 §7.1 `harness.breaker.cause` + `harness.breaker.cooldown_ms`)
**Revision shape:** Delta-only spec file per workspace `CLAUDE.md` §2.3 OD spec row convention. v1.32 + v1.31 + ... + v1 file bodies PRESERVED VERBATIM. v1.33 carries this change-note + the NEW C-OD-21 §21.2.1 ADDITIVE subsection only.

---

## Change-note (v1.32 → v1.33)

**Adds §21.2.1 — the `SigningBackend` composition-root injection seam on the C-OD-21 §21.2 audit-entry signing surface.** This is the OD-side mirror of the cleared `C-CP-20 §20.2.1` seam (CP spec v1.98, `B-22`): an OPTIONAL `backend` keyword parameter on the U-OD-30 `sign_audit_entry(payload, key_id, algo)` library function.

**Why now (grounding).** `B-47` registered that `AwsKmsSigningBackend` (ADR-D8, PR #1031) has no production composition-root call site. Grounding the call-site question found that the *actual* production audit-signing path is this OD function — invoked at every production audit write through the CXA-homed `cp_audit_to_od_audit` converter (CXA §2.3.7; runtime callers at `hitl_gate_composer` / `sub_agent_dispatch` / the `cost_attribution_*` family) — and that it produces the deterministic placeholder `"unsigned:{key_id}:{prior_entry_hash}"`, whose own docstring says a composition root "replaces [it] with the live signing call" per ADR-D5 v1.3 §1.4.1. The CP-side `sign_audit_entry` (C-CP-20 §20.3.1) carries the `B-22` seam but has zero production callers. Without this OD-side seam, no composition-root arc can ever deliver §21.2's committed cryptographic signature (`audit.signature.value` "produced under F5-resolved signing key") to the entries that actually land in the ledger — the §20.1/§21.2 MULTI_TENANT_COMPLIANCE commitment would be structurally unreachable.

**What §21.2.1 commits.**

1. `sign_audit_entry` gains an OPTIONAL keyword parameter `backend: SigningBackend | None = None`, where `SigningBackend` is the `C-CP-20 §20.2.1` Protocol (consumed OD→CP as a convention/runtime carrier import per the CXA §2.3.6 inbound direction — bytes-in/bytes-out, no key material; NOT a new Pattern-P1 seam obligation).
2. **Absent (`backend=None`, the default): the existing placeholder attribute set is PRESERVED VERBATIM** — byte-for-byte identical `AuditSignatureAttributes` for every existing caller, including the `"unsigned:{key_id}:{prior_entry_hash}"` value shape, the caller-supplied `algo`/`key_id`, and the `"DEPLOYMENT_BOUND"` key-period token. Zero regression; this delta is purely additive.
3. **Present: a real cryptographic signature is produced.** The signed message binds the entry content hash to its signature metadata — a length-prefixed injective encoding of the four-tuple `(compute_entry_hash(payload), key_id, algo.value, "DEPLOYMENT_BOUND")` — mirroring the `C-CP-20 §20.3.1` canonical-signing-message discipline (metadata relabeling on a signed entry must break verification; the length-prefix shape mirrors the B-23 injectivity fix). The backend call passes `key_period=0`, the fixed integer projection of the `"DEPLOYMENT_BOUND"` single-period token — rotation-boundary-aware key-period selection remains `B-33`'s scope and is NOT changed here.
4. **Representation (B-34 discipline, applied at birth rather than retrofitted):** `audit_signature_value` carries the raw signature bytes as standard base64 text (the 4-attribute carrier's `str` type is UNCHANGED); the backend-returned signature byte-length MUST equal the declared algorithm's fixed width per the `SIGNATURE_LENGTH_BY_ALGORITHM` table (`{ed25519: 64, ecdsa-p256: 64 raw r||s, rsa-pss-2048: 256}`, byte-identical to `C-CP-20 §20.4`'s committed widths) — a wrong-length signature raises rather than landing a malformed attribute set. A `backend.algorithm` that disagrees with the caller-supplied `algo.value` raises rather than persisting a mislabeled algorithm.
5. The 4-attribute `AuditSignatureAttributes` carrier (§21.2 / ADR-D5 §1.4.1) is **shape-unchanged** — no new field, no type change, no new enum value. §21.2's storage/contract table is PRESERVED VERBATIM.
6. Concrete backend selection and construction (which vault/KMS, credential sourcing, `key_id → key ARN` mapping) remain deployment-time composition-root concerns per ADR-D8 §Decision items 2/5 — this seam does not select a backend, construct one, or read configuration. The composition-root wiring arc (RuntimeConfig surface + bootstrap factory + C9 per-`{secret_backend, scope}` breaker on the signing call) is `B-47`'s remaining scope.

**Cross-references.** ADR-D8 (AWS KMS Ed25519 backend; its §Decision item 5 names this exact wiring as "a separate, deployment-time arc"); ADR-D5 v1.5 §1.4 row 3 (signing-key residence + B-36 cross-reference); `C-CP-20 §20.2.1` (the Protocol; CP spec v1.98); `C-CP-20 §20.4` (signature byte-widths; `Spec_Control_Plane_v1_2.md` §20.4 row `audit.signature.value`); CXA v2.9 §2.3.7 (the CP→OD audit-write seam this signing surface serves).

**Verification obligations discharged at the landing PR.** Absent-path byte-identity witness (placeholder attribute set unchanged for existing callers); real-crypto round-trip witness (an injected Ed25519 backend's signature verifies against the reconstructed canonical message); algorithm-mismatch and wrong-length fail-loud witnesses; CXA converter passthrough witness; each mutation-probed per workflow v1.18 PD-8.

---

## NEW §21.2.1 (C-OD-21) — `SigningBackend` composition-root injection seam

*Appended under §21.2 (Per-tenant audit ledger storage). §21.2's own table + prose are PRESERVED VERBATIM.*

| Property | Contract |
|---|---|
| **Seam surface** | `sign_audit_entry(payload, key_id, algo, *, backend: SigningBackend \| None = None)` — `SigningBackend` per `C-CP-20 §20.2.1` |
| **Absent backend** | Placeholder `AuditSignatureAttributes` PRESERVED VERBATIM (`"unsigned:{key_id}:{prior_entry_hash}"` value; `"DEPLOYMENT_BOUND"` key-period token); purely additive, zero caller regression |
| **Present backend** | Real signature over the length-prefixed canonical message binding `(compute_entry_hash(payload), key_id, algo.value, "DEPLOYMENT_BOUND")`; `key_period=0` passed to the backend as the `"DEPLOYMENT_BOUND"` integer projection |
| **Value representation** | `audit_signature_value` = standard base64 of the raw signature bytes; carrier `str` type unchanged |
| **Fail-loud validations** | `backend.algorithm != algo.value` → raise; `len(signature) != SIGNATURE_LENGTH_BY_ALGORITHM[algo.value]` → raise (widths per `C-CP-20 §20.4`) |
| **Out of scope here** | Backend selection/construction/config (composition root, `B-47` remainder); rotation-aware key-period selection (`B-33`); signature *verification* surface (C-OD-21 exposes hash-chain integrity only — unchanged) |
