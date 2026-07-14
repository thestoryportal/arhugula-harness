---
artifact: design-substrate/Spec_Control_Plane_v1_98.md
version: v1.98
cleared_at: 2026-07-14T00:00:00-06:00
clearance_type: Phase-7-absorbed-via-architect-recommendation
back_reference:
  - .harness/post-phase-8-forward-register.md (B-22 entry — F5 real audit-signature backend)
  - design-substrate/ADR-F5.md (§Deferred D-ADRs — prod-tech secrets-backend selection deferral)
  - design-substrate/ADR-D5.md (§1.4 signing-key residence table, row 3 — F5 prod-tech deferred to D-ADR)
  - design-substrate/Spec_Control_Plane_v1_2.md (§20 C-CP-20 last-substantive-definition; §20.4 "deferred to implementation discretion" list)
merge_commit: pending (pre-merge at filing time)
reviewer_chain:
  - advisor() pre-build grounding (corrected the initial plan 3 ways: dropped a keyring "reference backend" as wrong-tier for an MTC-exclusive module; identified the seam as a spec delta rather than pure impl per the CP v1.36 RouterResolutionFn precedent; confirmed the concrete prod-backend choice is the genuine operator/D-ADR/credential gate, not something to pick unilaterally)
  - operator AskUserQuestion 2026-07-14 (build-the-seam-now vs hold-B-22-fully; operator chose build-the-seam-now)
  - empirical grounding against ADR-F5 + ADR-D5 v1.3 §1.4 + Spec_Control_Plane_v1_2.md §20 (last-substantive-definition version resolved via delta-chain grep before authoring; confirmed the concrete backend really is D-ADR-deferred, not merely under-specified)
  - just codex-review pre-merge (§13.1 out-of-family review), 3 rounds, 7 findings all fixed. Round 1 — [P1] a valid signature could be relabeled onto different `key_id`/`algorithm`/`key_period` metadata and still verify (fixed via a length-prefixed canonical message binding, mirroring the B-23 segment-injectivity fix); [P2] `sign_audit_entry` accepted a backend declaring an algorithm outside the §20.2 closed enum (fixed with an explicit membership check); [P2] `sign_audit_entry` accepted a negative `key_period` (fixed with an explicit non-negative check). Round 2 — [P1] the verifier still returned `VERIFIED` when the caller's `key.key_id` or the backend's declared `algorithm` disagreed with the entry's stored metadata, since nothing checked those two selector fields against what was actually persisted (fixed with explicit equality checks before consulting the backend); [P2] the round-1 `key_period` check ran before the backend-presence check, changing the absent-backend exception type for a negative period — a regression against this delta's own additivity claim (fixed by reordering). Round 3 — [P2] `key_period=True`/`1.0` passes the `int` type hint by Python subtyping but signs a different textual message than the value Pydantic coerces to, self-invalidating the entry (fixed with an exact `type(key_period) is not int` check); [P2] the read path never validated a `signed` entry's OWN stored algorithm/period against the §20.2 contract, so an externally-constructed entry with out-of-contract metadata could verify if a rogue backend agreed with the same invalid value (fixed by repeating the write-path checks at read time). All seven mutation-probed individually (guard/binding/ordering reverted in isolation → exactly the corresponding test(s) fail → restored).
supersedes: null
superseded_by: null
---

# Clearance — `Spec_Control_Plane v1.98`

v1.98 is the `B-22` seam-half arc: `sign_audit_entry` / `verify_audit_entry_signature` (C-CP-20 §20.3.1, U-CP-44) previously had no call shape capable of ever accepting a real signing backend — both raised `AuditSigningBackendUnavailableError` unconditionally (operator-ratified 2026-07-13 fail-loud disposition, since real signing against an opaque `SecretRef` was not reachable from the CP axis). This delta adds a NEW §20.2.1 `SigningBackend` Protocol plus an optional `backend: SigningBackend | None = None` keyword parameter on both functions. Absent (default) the existing raise is preserved byte-for-byte for the zero production callers that exist today; present, both functions perform genuine SHA-256-then-sign / recompute-then-verify per the §20.3.1 `verify_chain` contract.

The concrete prod-tech backend a `multi-tenant-compliance` deployment would inject through this seam remains **explicitly deferred**, not resolved by this delta: ADR-F5 §Deferred D-ADRs names the specific secrets-provider selection (AWS Secrets Manager / HashiCorp Vault / Azure Key Vault / GCP Secret Manager / Doppler / 1Password Connect) as its own future D-ADR; ADR-D5 v1.3 §1.4's signing-key-residence table row 3 independently confirms "F5 prod-tech (deferred to D-ADR ...)" for exactly this module's exclusive persona tier. This module is MULTI_TENANT_COMPLIANCE-exclusive (`resolve_signing_key` returns `SCOPE_UNAUTHORIZED` for any lower tier) and this workspace's operative persona tier is `solo-developer` (the bridging-arc default) — the module has zero production callers and serves a tier not currently deployed. Given this, the seam was surfaced to the operator as a genuine fork (build the small additive plumbing now vs. hold B-22 fully until a real deployment need surfaces) rather than decided unilaterally; the operator chose to build the seam now.

The seam is proven with a TEST-ONLY in-memory Ed25519 `SigningBackend` double (`harness-cp/tests/test_f5_signing_key_resolution.py::_InMemoryEd25519Backend`) — no cloud credentials, no vault/KMS dependency, no production claim about backend residence. Mutation-probed: forcing `verify_audit_entry_signature` to unconditionally return `VERIFIED` was caught by `test_verify_rejects_tampered_entry_content` and `test_verify_rejects_wrong_backend_key` (2 of 10 tests failed under the mutation, confirming the tests pin real cryptographic verification, not a rubber-stamp).

## Notes

- Phase 7 consumers may rely on this version (v1.98) as canonical for the `SigningBackend` §20.2.1 seam.
- The concrete prod-tech backend selection is NOT closed by this marker — a future arc wiring a real backend (e.g., mirroring the already-landed `harness_runtime.config.provider_secrets.GcpSecretManagerResolver` precedent for LLM-provider secrets) still needs its own D-ADR + credential-provisioning decision before `multi-tenant-compliance` deployments can claim real audit-signature tamper-evidence. `harness-cp` must not import `harness_runtime` (axis-layering) — any such composition-root wiring lives at `harness_runtime`, consuming CP's `SigningBackend` Protocol, not the reverse.
- See `.harness/clearance/README.md` for marker discipline.
