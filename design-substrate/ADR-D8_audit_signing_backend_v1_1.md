# ADR-D8 v1.1 — local Ed25519 signing for bounded self-hosted personas

**Status:** Proposed for PR #1616 Class 1 backflow; ADR-D8 v1 remains the cleared authority until independent review and a v1.1 clearance marker.

## Decision delta over ADR-D8 v1

[HIGH] ADR-D8 v1 §Decision and §Rationale 3 continue to govern `MULTI_TENANT_COMPLIANCE`: AWS KMS delegated signing keeps the private audit key outside harness-process memory. A deployment in that persona tier MUST NOT select `local-ed25519`. It must reject that configuration before loading a private key, contacting KMS, writing an audit cutover record, or registering the tracer. The rejection is a configuration error; there is no automatic substitution to another backend.

[HIGH] For `SOLO_DEVELOPER` and `TEAM_BINDING`, the composition root MAY explicitly select `local-ed25519` with absolute private PKCS#8 PEM paths mapped to logical key IDs. This is a bounded local audit-integrity option for the first self-hosted Omarchy release: the 2026-09-24 profile decision requires local signing and excludes paid KMS, and the direct operator addendum at `/home/robbo/Work/arhugula-omarchy/docs/orchestration/review-evidence/buford-continuation-01a0e147/first-release-persona-decision-2026-09-29.md` selects solo/team tiers while keeping tenant isolation and redaction in scope and deferring MTC. For this first-release profile, the operator must explicitly select the local signer when making an audit-integrity claim; the general lower-tier default remains unchanged. This amendment does not change the `SigningBackend` protocol, Ed25519 wire signature, audit chain, cutover-record format, or KMS backend. The existing public-only historical verification map remains a read-only inspection surface at every tier; it never supplies a private signing backend.

[HIGH] In the selected solo/team profile, the shipped Runtime composition strips content-bearing span attributes by default. The per-session content-capture override is honored only at solo and ignored at team. A direct OD library caller below MTC can supply a narrower explicit attribute set, so installed redaction must be proven against the actual binding. MTC-only recoverable token mapping is outside this release profile. Tenant isolation remains a separate acceptance obligation; selecting a signing backend does not prove it.

[HIGH] The private key is readable by the harness OS user during backend construction and resides in that process while signing. A compromise of that user can compromise the key, including its retrospective tamper-evidence value. The bounded local claim therefore does **not** include key isolation from the harness principal or the compliance-tier threat model. On-disk permissions, separate record/row keys, historical public-key identity, and installed restart/tamper proof are still required by their respective Runtime contracts and release gates. No signer is enabled merely by this design amendment.

[SPECULATIVE] A later self-hosted compliance profile might delegate local signing to a separate OS principal over a narrow IPC interface. That is a different trust boundary requiring its own ADR, contract, implementation and installed evidence. This v1.1 delta does not authorize it.

## Rationale and provenance

ADR-D8 v1 §Alternatives 1 and 3 rejected local private-key residence **as the primary MTC path** and deferred a persona-spanning hybrid. The first-release operator contract at `/home/robbo/Work/arhugula-trial/evaluation/production-readiness-arch/profile-contract-decision-1.md` §In scope and §Explicit first-release exclusions now supplies the distinct lower-tier deployment case. Independent design input at `/home/robbo/Work/arhugula-trial/evaluation/production-readiness-arch/evidence-local-audit-signer-design-opus-1/report.md` §Recommendation identifies file-backed Ed25519 as a bounded option and names a separate signer user as the missing premise for a compromise-resistant claim. This amendment resolves that case without weakening ADR-D8's MTC choice.

The PR #1616 pass-1 spec lens identified the missing persona restriction in `harness-runtime/src/harness_runtime/types.py` and the stage-4 composition root. The routed fork record is `.harness/class_1_fork_pr1616_local_signer_and_runtime_plan.md`. Proposed ADR-F5 v1.2 owns the bounded file-key exception to the general secret-fetch rule; ADR-D5 v1.7 composes the §1.4 solo/team residence rows with that foundation. F5 remains unchanged for ordinary secrets. The Runtime spec successor owns the error class and validation ordering; the plan successors own the implementation acceptance criteria.

## Preservation

All ADR-D8 v1 KMS decision items, rationale, alternatives and acceptance evidence remain historical and in force for MTC. This delta adds one lower-tier backend option and one MTC exclusion. It makes no installed-runtime, live-device, or production-readiness attestation.
