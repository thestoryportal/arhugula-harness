---
artifact: design-substrate/ADR-D8_audit_signing_backend.md
version: v1 (Accepted, 2026-07-16)
cleared_at: 2026-07-16T00:00:00-06:00
clearance_type: Phase-7-absorbed-via-roadmap-continue
back_reference:
  - .harness/forward-register.yaml (B-36 entry, CLOSED)
  - .harness/post-phase-8-forward-register.md (B-36 section)
merge_commit: pending (pre-merge at filing time)
reviewer_chain:
  - "dyadic council convening (C10 action-safety/blast-radius + C11 operator-loop/local-deployment) run per workspace CLAUDE.md §10.9 nameable-tension discriminator, matching the exact council field the B-36 forward-register row itself named ('conditional — C10 blast-radius vs C11 operator-loop/deployment-surface, live once a candidate backend is proposed'); decisive finding: the already-landed `resolve_signing_key` TIER_4_FULL_VM/in-sandbox-HTTP tier choice + MULTI_TENANT_COMPLIANCE-exclusive gate already signal a no-exposure design intent, so AWS KMS delegated signing (key never leaves the HSM boundary) was ranked over Secrets-Manager-plus-local-signing"
  - "empirical verification before the council convened: AWS KMS's native Ed25519 support (Nov 2025 GA, `ECC_NIST_EDWARDS25519`) confirmed via direct documentation lookup, dissolving the assumed algorithm-vs-exposure tradeoff"
  - "operator `AskUserQuestion` confirmations: (1) 2026-07-16 selecting 'AWS KMS delegated signing (Recommended)' for the backend-architecture question; (2) explicit go-ahead confirmation before any live AWS provisioning action, after an auto-mode classifier correctly paused on an ambiguous prior reply"
  - "live AWS proof: a real KMS asymmetric Ed25519 key + a least-privilege IAM user (arhugula-harness-cp-signing, scoped to Sign/Verify/GetPublicKey/DescribeKey on that one key ARN) were provisioned; `harness-cp/tests/integration/test_b36_kms_signing_live_e2e.py` passed twice against the real key (sign/verify round-trip, tamper rejection, wrong-message rejection, unmapped-key_id fail-loud, confirmed AccessDenied against S3 and iam:CreateUser under the same identity)"
  - "unit tests: harness-cp/tests/test_aws_kms_signing_backend.py — 8/8 passed against a mocked KMS client performing real Ed25519 cryptography; mutation-probed (`_resolve_key_arn`'s fail-loud check reverted to a silent default-key fallback, confirmed 2 tests fail, restored, confirmed 8/8 pass); sibling test_f5_signing_key_resolution.py — 23/23 unchanged, zero regressions"
  - ruff format + ruff check clean; pyright 0 errors/0 warnings/0 informations on all touched files
supersedes: null
superseded_by: null
---

# Clearance — `ADR-D8` concrete F5 audit-signing backend selection (AWS KMS, Ed25519)

Records the operational acceptance, for Phase-7 consumption, of `design-substrate/ADR-D8_audit_signing_backend.md`
(v1, Accepted, 2026-07-16). This is a **bundled design+impl absorption arc** (CLAUDE.md §11.4) —
the ADR is authored, the concrete `SigningBackend` implementation lands, and the forward-register
`B-36` row closes, all in the same PR, mirroring the `B-25`/ADR-D2 v1.3 precedent.

`B-36` was `operator_gated` — ADR-F5 §Deferred D-ADRs and ADR-D5 v1.3 §1.4 row 3 both explicitly
deferred the concrete prod-tech signing backend to a future D-ADR requiring real cloud credentials,
which the operator subsequently authorized (AWS account, both CLI-SSO and static-credential access
paths confirmed available via the existing `.env`/justfile convention). This ADR resolves that
deferral for the AWS case, closing the deferred-D-ADR half of both ADR-F5 and ADR-D5 §1.4 row 3 as
they pertain to the audit-signing-key surface specifically (the broader generic-`fetch_secret`
prod-tech D-ADR ADR-F5 also names remains separately deferred — this ADR is scoped to the
`C-CP-20 §20.2.1` `SigningBackend` seam only).

**No CP spec amendment required.** `resolve_signing_key` / `sign_audit_entry` /
`verify_audit_entry_signature` (`harness-cp/src/harness_cp/f5_signing_key_resolution.py`) are
byte-unchanged — the `§20.2.1` composition-root injection seam (landed at `B-22`, spec v1.98) already
accommodated a delegated-signing backend shape without modification. The only new production surface
is `harness_cp.aws_kms_signing_backend.AwsKmsSigningBackend`.

**No `ADR-D5` amendment required.** The `audit_signature_algorithm` default (Ed25519) is honored
exactly, not deviated from — AWS KMS's native Ed25519 support means this ADR's backend choice needs
no `§1.4`/`§1.4.1` text change.

## Notes

- Phase 7 consumers may rely on this version (v1) as canonical for the concrete `SigningBackend`
  implementation available to a `MULTI_TENANT_COMPLIANCE` deployment on AWS.
- `B-36`'s forward-register row (`.harness/forward-register.yaml` + `.harness/post-phase-8-forward-register.md`)
  is marked closed in the same PR, citing this clearance marker. `B-33` and `B-34` are cross-referenced
  and updated (extended / narrowed respectively) in the same PR.
- The deployment-time composition-root arc that wires `AwsKmsSigningBackend` into a real production
  `sign_audit_entry` call site (with the C9 breaker extended onto the signing call itself, per this
  ADR's C11 concession) is explicitly out of scope for this ADR and remains future work — zero
  production callers of `sign_audit_entry` exist today.
- See `.harness/clearance/README.md` for marker discipline.
