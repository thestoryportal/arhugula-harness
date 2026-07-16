# ADR-D8: Adopt AWS KMS (Ed25519 / ECC_NIST_EDWARDS25519) as the concrete F5 audit-signing backend for MULTI_TENANT_COMPLIANCE

## Status

Accepted.

Date: 2026-07-16

## Context

ADR-D5 v1.5 §1.4 commits the per-persona-tier audit-ledger cryptographic shape: solo-developer has no signature; team-binding has a hash chain; multi-tenant-compliance adds a cryptographic signature over the hash-chained entry, under a signing key resolved through ADR-F5's `fetch_secret(name, scope) -> SecretRef` abstraction. §1.4's signing-key-residence table names candidate prod-tech backends (Vault / AWS Secrets Manager / Azure Key Vault / GCP Secret Manager / Doppler / 1Password Connect) but explicitly defers the concrete selection to a future D-ADR. ADR-F5 §Deferred D-ADRs independently names the same deferral ("D-ADR on specific secrets provider for production deployment ... selection deployment-surface-bound; depends on production-time deployment surface decision").

The composition-root injection seam this decision plugs into already exists: `C-CP-20 §20.2.1` (CP spec v1.98, landed via `B-22`) declares a `SigningBackend` Protocol —

```python
class SigningBackend(Protocol):
    algorithm: str
    def sign(self, *, message: bytes, key_id: str, key_period: int) -> bytes: ...
    def verify(self, *, message: bytes, signature: bytes, key_id: str, key_period: int) -> bool: ...
```

— consumed by `harness_cp.f5_signing_key_resolution.sign_audit_entry` / `verify_audit_entry_signature` via an optional `backend: SigningBackend | None = None` keyword. Absent, both functions raise `AuditSigningBackendUnavailableError` (preserved verbatim); present, they perform genuine signing/verification. `resolve_signing_key` is gated exclusively to `PersonaTier.MULTI_TENANT_COMPLIANCE` and resolves its `SigningKeyHandle.key_secret_ref` at `SandboxTier.TIER_4_FULL_VM` — per AS spec C-AS-05 §5.4 this tier's resolution mechanism is in-sandbox HTTP, not a literal-string env-var read, and `key_secret_ref` is in fact never read downstream of `resolve_signing_key` (confirmed by direct trace: `sign_audit_entry` / `verify_audit_entry_signature` forward only `key.key_id`). The landed code already leans toward "the signing key should never resolve to a raw string in harness process memory."

The operator authorized using a real AWS account for this decision (AWS CLI SSO profile + static credentials both available via the established `.env` / justfile convention, matching the `R830_S3_*` live-e2e precedent). Two facts were empirically verified before this ADR was authored, per the standing "verify before recommending" discipline:

1. **AWS KMS supports Ed25519 natively as of November 2025** (`ECC_NIST_EDWARDS25519` key spec; `ED25519_SHA_512` / `ED25519_PH_SHA_512` signing algorithms; 64-byte raw signatures; all AWS regions including GovCloud). This was previously assumed unavailable (a training-cutoff-era belief); confirmed current via direct AWS documentation lookup before this ADR was drafted. This means AWS KMS can produce ADR-D5 §1.4's own **default** signature algorithm (Ed25519) — there is no forced tradeoff between "delegate signing to a remote HSM/KMS" and "match the spec's default algorithm."
2. **A dyadic council (C10 action-safety/blast-radius ⊥ C11 operator-loop/local-deployment) was convened** on the resulting live tension — not "which algorithm" (resolved by fact 1) but "should the signing key ever resolve into harness process memory at all." C10's position: given the signing key's unusually severe, silent, retroactive blast radius (compromise invalidates the tamper-evidence guarantee of the *entire* ledger, not just one entry) and the already-landed `TIER_4_FULL_VM`/in-sandbox-HTTP tier choice, a backend that never exposes raw key material (KMS-delegated signing) is the correct default; C11 conceded the exposure argument but flagged a real, distinct cost — KMS moves AWS availability onto the per-signature write-time hot path, a new failure class that should be wired through the existing C9 breaker discipline on the signing call itself, not merely at key resolution. The council ranked KMS-delegated signing first, Secrets-Manager-plus-local-signing second, and explicitly deferred a persona-tier-spanning hybrid design as out of B-36's scope.

Empirical verification of the AWS account state: `aws sts get-caller-identity` on the credentials available in `.env` resolved to the account's IAM root user, not a scoped identity. A dedicated least-privilege IAM user (`arhugula-harness-cp-signing`) was subsequently provisioned, scoped by an inline policy to exactly `kms:Sign` / `kms:Verify` / `kms:GetPublicKey` / `kms:DescribeKey` on one specific KMS key ARN — verified end-to-end (real `Sign`/`Verify` round-trip against the provisioned key; tampered-signature rejection; confirmed `AccessDenied` against S3 and `iam:CreateUser` under the same identity).

## Decision

Adopt **AWS KMS asymmetric-key delegated signing**, key spec `ECC_NIST_EDWARDS25519` (Ed25519, matching ADR-D5 §1.4's default `audit_signature_algorithm`), as the concrete `SigningBackend` implementation for `MULTI_TENANT_COMPLIANCE` deployments that provision AWS as their production secrets/crypto surface.

Concretely:

1. A new `harness_cp.aws_kms_signing_backend.AwsKmsSigningBackend` class implements the `C-CP-20 §20.2.1` `SigningBackend` Protocol via `boto3`'s KMS client (`Sign` / `Verify` APIs, `SigningAlgorithm=ED25519_SHA_512`, `MessageType=RAW`).
2. The backend is constructed with an explicit mapping from the CP-axis logical `key_id` (`f"{scope_kind}:{scope_identifier}"` per `resolve_signing_key`) to a physical KMS key ARN, supplied by the deployment-time composition root — not auto-discovered. An unmapped `key_id` fails loud (`KeyError`), never silently signs under the wrong key or a default key.
3. `resolve_signing_key` is **unchanged**. Its `fetch_secret(...)` call still executes (harmlessly — `fetch_secret` is a pure `SecretRef` constructor per AS spec C-AS-05 §5.1 that never resolves literal secret bytes) and `SigningKeyHandle.key_secret_ref` is still populated but remains unread by the KMS-backed signing path, exactly as it is today for the no-backend path. No CP spec amendment is required — the `§20.2.1` seam already accommodates this backend shape without modification.
4. The physical key never leaves the AWS KMS HSM boundary. `sign()` / `verify()` are network calls; no raw private-key bytes are ever resolvable into harness process memory.
5. The signing call — not merely `resolve_signing_key`'s key-resolution step — should be wired through the existing per-`{secret_backend, scope}` C9 breaker discipline (ADR-F5 §Consequences) at the deployment-time composition-root arc that wires this backend into a live `sign_audit_entry` call site, since AWS KMS availability now sits on the audit-write hot path. This composition-root wiring is a separate, deployment-time arc (there are zero production callers of `sign_audit_entry` today) and is not part of this ADR's `SigningBackend` implementation scope.

This decision is scoped to a **single physical KMS key** proof — multi-key / fleet-scoped key routing across different logical `key_id` values (distinct `WORKFLOW_BOUND` / `TENANT_BOUND` / `FLEET_BOUND` scopes each resolving to a distinct physical key) is deliberately out of scope; today's mapping may legitimately contain one entry. Rotation-boundary-aware key-period selection (choosing among *historical* KMS key versions for a given `key_period`) is `B-33`'s scope, which this ADR's backend composes with once B-33 lands.

## Rationale

### 1. The tension is exposure, not algorithm

AWS KMS's November 2025 Ed25519 support dissolves what looked like a forced choice between "match the spec's default algorithm" and "never expose key material." Both are achievable simultaneously via `ECC_NIST_EDWARDS25519`. The remaining, real tension is exposure surface versus operational simplicity — the C10⊥C11 council's actual subject.

### 2. The landed code already signals a no-exposure design intent

`resolve_signing_key` resolves its `SecretRef` at `SandboxTier.TIER_4_FULL_VM` — per AS spec C-AS-05 §5.4 this tier's mechanism is in-sandbox HTTP, not a literal-string env-var read — and `key_secret_ref` is never read by any downstream consumer. Treating the signing key as a fetchable, in-process-resolvable secret (the Secrets-Manager-plus-local-signing alternative) works against the grain of a design that already isolates this specific secret more tightly than other secrets in the codebase.

### 3. Blast-radius asymmetry favors delegation

A compromised harness process that never held the private key cannot leak it via a memory dump, a crash-handler core dump, or a dependency that logs its own arguments. A compromised process that resolved the key locally can. The audit-signing key's compromise is categorically worse than a typical secret's compromise: it silently and retroactively invalidates the tamper-evidence guarantee of the entire ledger, not just the value it directly gates. `MULTI_TENANT_COMPLIANCE` is exactly the tier where this threat model is live (`resolve_signing_key` is unreachable below it).

### 4. The composition-root seam already supports this cleanly

`C-CP-20 §20.2.1`'s `SigningBackend` Protocol is bytes-in/bytes-out with no key-material parameter — it was already shaped for a delegated-signing backend. Wiring `AwsKmsSigningBackend` requires zero Protocol change, zero CP spec amendment, and zero change to `resolve_signing_key` / `sign_audit_entry` / `verify_audit_entry_signature`. The only new surface is the concrete backend class itself.

### 5. The availability cost is real but bounded and monitorable

C11's objection stands on its own terms: KMS availability becomes a new failure class on the signing hot path. This is a named, bounded, breaker-mediated risk (composes with the existing C9 per-`{secret_backend, scope}` breaker pattern already named in the module's own docstring for `secret_unavailable`) — not a reason to prefer local signing, but a real scope item for the deployment-time wiring arc.

## Consequences

### What becomes possible

- A concrete, empirically-verified `SigningBackend` implementation exists and can be composition-root-wired into `sign_audit_entry` / `verify_audit_entry_signature`, closing the "signing is unavailable, not faked" gap those functions currently raise for.
- `B-33` (rotation-boundary key-period selection) and `B-34` (signature-representation encoding) now have a concrete backend to build against instead of a hypothetical one.
- `B-34`'s originally-registered "DER-vs-64-byte ECDSA-P256 encoding" finding **narrows**: `ED25519_SHA_512` signatures from KMS are always a fixed 64 raw bytes — no DER-wrapping ambiguity exists for this backend. `B-34` should be re-scoped (not closed outright) to whichever encoding concerns remain relevant if a future ECDSA-P256 fallback backend is ever added alongside this one.

### What becomes harder

- Every real audit-entry signature requires a network round-trip to AWS KMS; this must be accounted for in cost, latency, and failure-mode budgets for the deployment-time composition-root arc that eventually wires a live `sign_audit_entry` call site.
- The composition root must manage a `key_id → KMS key ARN` mapping and AWS credential provisioning as an operational concern, not a purely in-repo one.

### Downstream constraints

- `harness-cp` gains a `boto3` dependency (matching the existing direct-SDK-dependency convention already used for `anthropic` / `openai` / `ollama`).
- The deployment-time composition-root arc that eventually invokes `sign_audit_entry(..., backend=AwsKmsSigningBackend(...))` at a real production call site owns wiring the C9 breaker onto the signing call itself — not assumed to exist yet, and not part of this ADR.
- The least-privilege IAM identity provisioned for this proof (`arhugula-harness-cp-signing`, scoped to one KMS key ARN) is the pattern future composition-root wiring should reuse or extend; it must never be broadened to blanket AWS permissions.

## Alternatives considered

### Alternative 1: AWS Secrets Manager + local Ed25519 signing

Rejected as the primary path per the council's exposure-asymmetry argument (Rationale §3). Would have required zero adaptation to `resolve_signing_key`'s `fetch_secret`-shaped premise and avoided the per-signature network dependency, but resolves raw private-key bytes into harness process memory for the resolved handle's lifetime — exactly the exposure the landed `TIER_4_FULL_VM` tier choice appears designed to avoid, at the one tier where the tamper-evidence threat model is meant to be real.

### Alternative 2: ECDSA-P256 via AWS KMS (pre-Ed25519-support assumption)

Moot. This alternative was under consideration only under the (incorrect, training-cutoff-era) assumption that AWS KMS could not sign Ed25519. Verified false — KMS's native Ed25519 support (Nov 2025 GA) means no algorithm compromise is required.

### Alternative 3: Persona-tier-spanning hybrid (KMS at multi-tenant-compliance, local/unsigned at team-binding)

Deferred as out of scope. `resolve_signing_key` is already gated exclusively to `MULTI_TENANT_COMPLIANCE`; a team-binding-tier signing path is a separate, not-yet-built unit outside B-36's registered scope. Naming a persona-spanning hybrid here would expand B-36's scope rather than drive it to a gate.

### Alternative 4: Defer backend selection further, pending a production deployment-surface commitment

Rejected. ADR-F5's own deferred-D-ADR framing anticipated the concrete prod-tech selection would wait for a production deployment-surface decision. B-36 was explicitly operator-authorized to ground this now, using a real AWS account, rather than continue deferring — and the deferred state was already the status quo the composition-root seam (`B-22`) was built to eventually resolve.

## Acceptance

This ADR is satisfied when:

- `AwsKmsSigningBackend` implements the `C-CP-20 §20.2.1` `SigningBackend` Protocol and is unit-tested against a mocked KMS client.
- A live end-to-end proof exists demonstrating a real sign/verify round-trip against a provisioned AWS KMS Ed25519 key, tamper rejection, and confirmation that the backend's IAM identity is scoped to that one key only.
- `.harness/forward-register.yaml`'s `B-36` row reflects this ADR as its resolution and cross-references the `B-33` / `B-34` scope narrowing named above.

## References

- ADR-D5 v1.5 §1.4 / §1.4.1 — per-persona-tier audit-ledger cryptographic shape; signing-key-residence table; `audit_signature_algorithm` default (Ed25519).
- ADR-F5 §Deferred D-ADRs — "D-ADR on specific secrets provider for production deployment."
- `Spec_Control_Plane_v1_100.md` §20.2.1 (`C-CP-20`, landed at spec v1.98 / `B-22`) — `SigningBackend` Protocol + composition-root injection seam.
- `Spec_Action_Surface_v1.md` §5.1 / §5.4 (`C-AS-05`) — `fetch_secret` pure-constructor semantics; `SecretRef` opaque-handle discipline.
- `harness-cp/src/harness_cp/f5_signing_key_resolution.py` — `resolve_signing_key` / `sign_audit_entry` / `verify_audit_entry_signature`.
- `.harness/forward-register.yaml` `B-36`, `B-33`, `B-34`.
- AWS documentation, "AWS KMS now supports Edwards-curve Digital Signature Algorithm (EdDSA)" (Nov 2025 GA) — `ECC_NIST_EDWARDS25519` key spec; `ED25519_SHA_512` / `ED25519_PH_SHA_512` signing algorithms.
