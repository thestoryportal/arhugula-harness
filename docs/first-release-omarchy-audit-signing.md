# First self-hosted Omarchy audit-signing procedure

The first release admits `SOLO_DEVELOPER` and `TEAM_BINDING` only. It uses an explicitly selected `local-ed25519` signer for a bounded audit-integrity claim. `MULTI_TENANT_COMPLIANCE` (MTC) is deferred. Buford, the release lead, owns gate **R-AUDIT-TRANSITION-01** and must include this procedure in the release bundle before enabling signing.

## Before enabling the local signer

1. Confirm the installed `RuntimeConfig.persona_tier` is solo or team and `audit_signing.backend` is `local-ed25519`. The configured private PEM must be an absolute path outside every Git checkout, owned by the harness OS user and readable only by that user. Record the actual resolved path and permissions. The source loader checks path shape, owner and mode; it does not detect checkout membership.
2. Keep signing disabled until B1/B2 source and integration gates and an installed restart/tamper witness pass. Record the exact release build and the installed result. A source test or design clearance alone does not enable the signer.
3. Complete tenant-isolation and redaction acceptance for the installed deployment. The shipped lower-tier Runtime composition strips content-bearing span attributes by default; solo alone can opt into session content capture. Test the actual binding because a direct OD library caller below MTC can pass a narrower attribute set. The MTC recoverable token map is outside this release.

If any check is missing, R-AUDIT-TRANSITION-01 fails and signing stays disabled.

## Requests to change to MTC

Do not change an installation or ledger signed with `local-ed25519` to MTC in place, including by selecting `aws-kms`. Do not treat a new MTC deployment as part of this first-release profile. Stop the change and keep the existing solo/team configuration. The current source rejects MTC with a local private signer, but it does **not** detect MTC plus KMS opening a ledger with local-signing history.

A later MTC release needs its own approved migration plan, a source admission guard for mixed ledger history, a chain-continuity design with the required dual-signed transition, and an installed migration/restart/tamper witness. Until those exist, no operator action or documentation change may claim continuity across the tier change.

## Release record

Buford records the installed persona and backend, key residence/permissions, B1/B2 and restart/tamper results, tenant-isolation and redaction results, and the presence of this procedure in the shipped bundle. Any MTC configuration or in-place tier-change request fails R-AUDIT-TRANSITION-01 for this release. This is an operator release gate; it is not a source-level MTC+KMS history guard.
