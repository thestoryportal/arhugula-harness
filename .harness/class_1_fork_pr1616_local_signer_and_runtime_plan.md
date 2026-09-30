# PR #1616 Class 1 backflow: local signer boundary and Runtime plan coverage

Status: routed for design review, 2026-09-29. Source execution is held at the
audit-signing configuration boundary until the successor artifacts are reviewed.
This is a bundled absorption under root `CLAUDE.md` §11.4: the design correction
and its implementation will land in the same PR only after independent review.

## Fork A — ADR-D8 signing-key residence

The PR #1616 merge-gate spec lens found that `local-ed25519` can be selected
with `RuntimeConfig.persona_tier=MULTI_TENANT_COMPLIANCE`. In that tier, the
file-backed private key is read by the harness process. ADR-D8 §Decision and
§Rationale 3 select delegated AWS KMS signing for the compliance-tier threat
model specifically to keep that key out of process memory. This is a Class 1
ADR/spec conflict, not an implementation choice to absorb silently.

The 2026-09-24 first-release profile decision at
`/home/robbo/Work/arhugula-trial/evaluation/production-readiness-arch/profile-contract-decision-1.md`
§In scope requires a local audit signer and §Explicit first-release exclusions
rules out a paid KMS service for the first self-hosted Omarchy release. The independent design
input at `.../evidence-local-audit-signer-design-opus-1/report.md` recommends a
file-backed Ed25519 backend for a bounded claim and states that survival of
harness-user compromise would require a separate signer user. Neither source
authorizes advertising the file-backed backend as compliance-tier key isolation.

**Routed resolution.** [HIGH] Keep ADR-D8's MTC commitment intact. Scope
`local-ed25519` to `SOLO_DEVELOPER` and `TEAM_BINDING` as an explicit local
opt-in. At MTC, reject the selection as `RT-FAIL-CONFIG` during the pure
configuration validation pass, before private-key I/O, KMS SDK discovery,
record writes, or tracer registration. Do not substitute KMS automatically.
`aws-kms` stays available at MTC. The local key is not protected against a
compromised harness OS user; installed restart/tamper proof remains a separate
release gate. [SPECULATIVE] A later compliance-tier local signer could use a
separate OS principal and a narrow IPC protocol, but that requires a new ADR
and is outside this correction.

Routing chain: ADR-D8 successor plus ADR-D5 §1.4 residence amendment →
Runtime C-RT-03 successor → Runtime plan successor → Phase 7 config guard
+ behavioral witness. The CP SigningBackend
protocol, signature bytes, key IDs, and audit record format are unchanged. ADR-F5
remains the general secret-fetch authority; proposed ADR-F5 v1.2 owns the
bounded lower-tier file-key exception, including no per-access fingerprint and
outside-Git residence. ADR-D5 v1.7 composes with it. Cross-deployment
dual-signature continuity is an unimplemented target. The first-release
operator procedure prohibits an in-place MTC upgrade; source has no general
MTC+KMS-over-local-ledger guard, which a future MTC activation must add.

## Fork B — Runtime plan head trails implemented contracts

The same spec lens found Runtime plan v2.63 ends at Runtime spec v1.121, while
PR #1616 consumes Runtime spec v1.122–v1.132. This is a Class 1 Phase 6 plan
coverage defect. The revised plan must map the later Runtime obligations to
their source witnesses and distinguish built source from unbound or installed
paths. It must not retroactively claim that a cleared spec alone is an
implementation plan or that `just codex-check` proves installed behavior.

Routing chain: Runtime plan v2.64 delta with version-span coverage,
independently reviewed before its clearance marker. External B-104 plans are
supporting provenance, not a substitute canonical plan head. The independent review found the paired CP v1.120–v1.124 plan gap; it
now routes to Control Plane plan v2.55, co-reviewed with Runtime v2.64.

## Gate record

Pass-1 spec lens: `pr1616-pass1-visible-lenses/spec-refined-block-raw.txt`
SHA256 `35192865d5e99c0d8a56b97a27ada3cf5b65206f293fe93a50b47faba0fa6e0d`.
LIT disposition: `arhugula-harness-trial-193`
`cmt-24579abc-f9a0-4760-8dc1-cf1f872648e0`. Both findings remain accepted
until reviewed design, source witness, composite checks and merge-gate passes
close them. No live-device consent or installed-readiness claim is implied.

## Independent packet review hold

The existing Opus 5.5/high independent reviewer returned BLOCK at LIT
`cmt-121cef7f-a806-45e6-bab2-9bb195ece9c4` (raw SHA256
`79052f45d62d853b9d864507af268a37d6aab96018e3e1f74994735b4e5654d6`).
It confirmed ADR-D8 MTC isolation and the central validation site, and found:
(1) first-release MTC has no admissible signer when KMS is excluded — operator
profile scope resolved by the direct user addendum `/home/robbo/Work/arhugula-omarchy/docs/orchestration/review-evidence/buford-continuation-01a0e147/first-release-persona-decision-2026-09-29.md` (solo/team first release; tenant isolation/redaction retained; MTC deferred); (2) ADR-D5 §1.4 rows 1–2 require
a residence amendment; (3) the Runtime plan's witness citations and source
limits need correction; (4) CP v1.120–v1.124 needs a plan successor. No
clearance marker is filed while these hold. The reviewer was read-only and
released with no handles.

The second independent review at LIT `cmt-671239f0-f409-4990-94f9-903000f4bbbe` closed the Runtime plan citation P2 for draft review and narrowed two P2s: foundational F5 exception/cross-deployment continuity and missing nonempty-prefix CP witnesses. These remain open; no design clearance or source admission follows from this draft correction.

The third independent review at LIT `cmt-7a631c7d-206c-4c22-914d-b637b9bbc5b5` closed CP plan U-CP-103 for draft review and held F5/D5 over two unsupported source-MUST claims. This draft now states key-path checkout exclusion as an installed provisioning gate and MTC transition as a deferred, operator-prohibited operation needing a future source guard. The direct user scope decision is at LIT `cmt-477a5afa-3304-4a82-ae20-e0766c7c3310`. Neither review has cleared these revised bytes.
