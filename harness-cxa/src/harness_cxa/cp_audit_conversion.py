"""CP→OD audit-write converter — production CXA seam (U-RT-59 Fork 2 close).

Production-grade converter materializing the typed CP→OD audit-write seam
declared at `Cross_Axis_Composition_Document_v2_4.md` §2.3.7 + the converter
contract at `Spec_Control_Plane_v1_7.md` §13.5.1 + the OD-side recognition
discipline at `Spec_Operational_Discipline_v1_5.md` C-OD-24.6. Wired at the
sub-agent dispatch composer per `Spec_Harness_Runtime_v1.md` v1.7 §14.7.2
step 8c.

**Home rationale (Q5 ratification, 2026-05-20).** Lives at `harness-cxa/` per
the workspace `CLAUDE.md` §2.5 assignment ("harness-cxa/ hosts CXA seam
instantiation"). `harness-od/` was foreclosed by OD's "0 outbound cross-axis
edges" invariant; `harness-cp/` would have created a new CP→OD outbound
package-import edge. Moved here from the original prototype location at
`harness-runtime/src/harness_runtime/lifecycle/cp_audit_conversion.py` at the
implementation arc landing.

**Ratifications absorbed.**

- **Q1 (chain equivalence)** — CP `prior_event_hash` ≡ OD `prior_entry_hash`
  per C-IS-06 + C-IS-13 §13.5 (same SHA-256 chain). Direct pass-through.
- **Q2(a) (entry_core source semantic)** — caller (the dispatch composer)
  writes an F2 state-ledger entry recording the dispatch action FIRST,
  then passes the resulting `StateLedgerEntryRef` to the converter. The
  audit's `entry_core` therefore preserves the IS-anchor invariant.
- **Q3 (entry_hash canonicalization)** — SHA-256 over `payload.model_dump_json()`
  per ADR-D5 v1.4 §1.4.1 + OD spec v1.5 C-OD-24.5 canonical helper recipe.
  F2-04 absorption (OD spec v1.7, 2026-05-20): the recipe is now materialized
  at `harness_od.audit_ledger_types.compute_entry_hash`; this converter
  imports it (no local inline duplicate).
- **Q4 (namespace prefix)** — CP-sourced fields land under `audit.cp.*`
  within OD `audit_namespace_attrs` per C-OD-24.6 + the 15-namespace
  ingestion map at C-OD-05.
- **NOTE 3 cryptographic-payload-mismatch foreclosure** — converter signs
  the OD `AuditPayload` directly via `sign_audit_entry`; CP-side signatures
  are NOT re-projected (different bytes, different schemas).
"""

from __future__ import annotations

from harness_cp.per_step_override_evaluator import CPAuditLedgerEntry
from harness_od.audit_ledger_types import (
    AuditLedgerEntry,
    AuditPayload,
    SignatureAlgorithm,
    StateLedgerEntryRef,
    compute_entry_hash,
)
from harness_od.multi_tenant_trace_separation_and_audit_ledger import sign_audit_entry

#: Namespace prefix for CP-sourced fields landing in OD `audit_namespace_attrs`.
#: Ratified at OD spec v1.5 C-OD-24.6 (Q4 — `audit.cp.*` sub-namespace
#: extends OD-canonical `audit.*` per C-OD-05 §5.1).
CP_AUDIT_NAMESPACE_PREFIX = "audit.cp"


def _project_namespace_attrs(cp_entry: CPAuditLedgerEntry) -> dict[str, str]:
    """Project CP fields → `audit_namespace_attrs` dict per the §3 field table.

    Conditional hash fields (`edited_proposal_hash` / `rejection_reason_hash` /
    `response_text_hash`) are included only when populated per C-CP-16 §16.2's
    response-conditional discipline.
    """
    attrs: dict[str, str] = {
        f"{CP_AUDIT_NAMESPACE_PREFIX}.action_id": str(cp_entry.action_id),
        f"{CP_AUDIT_NAMESPACE_PREFIX}.gate_level": cp_entry.gate_level.value,
        f"{CP_AUDIT_NAMESPACE_PREFIX}.response": cp_entry.response,
        f"{CP_AUDIT_NAMESPACE_PREFIX}.timestamp": cp_entry.timestamp,
    }
    if cp_entry.edited_proposal_hash is not None:
        attrs[f"{CP_AUDIT_NAMESPACE_PREFIX}.edited_proposal_hash"] = (
            cp_entry.edited_proposal_hash
        )
    if cp_entry.rejection_reason_hash is not None:
        attrs[f"{CP_AUDIT_NAMESPACE_PREFIX}.rejection_reason_hash"] = (
            cp_entry.rejection_reason_hash
        )
    if cp_entry.response_text_hash is not None:
        attrs[f"{CP_AUDIT_NAMESPACE_PREFIX}.response_text_hash"] = (
            cp_entry.response_text_hash
        )
    return attrs


def cp_audit_to_od_audit(
    cp_entry: CPAuditLedgerEntry,
    *,
    key_id: str,
    algo: SignatureAlgorithm = SignatureAlgorithm.ED25519,
    entry_core: StateLedgerEntryRef | None = None,
) -> AuditLedgerEntry:
    """Convert a `CPAuditLedgerEntry` to a signed OD `AuditLedgerEntry`.

    Production seam per CP spec v1.7 §13.5.1 + OD spec v1.5 C-OD-24.6.
    Sub-agent dispatch composer (runtime spec v1.7 §14.7.2 step 8c) invokes
    this function on every dispatch on the SUCCESS / DRAINED path; failure
    paths invoke it best-effort.

    Parameters:
        cp_entry: the CP-shape unsigned audit entry from the composer
            (composed at step 8a via `compose_dispatch_audit`).
        key_id: OD `audit.signature.key_id` per C-OD-21 §21.2 + ADR-D5
            v1.4 §1.4.1. Operator surface deferred per spec §14.7.
        algo: OD `audit.signature.algorithm`; defaults to Ed25519 per
            ADR-D5 v1.4 §1.4.1.
        entry_core: OD `payload.entry_core` IS reference per Q2(a) — the
            `StateLedgerEntryRef` for the F2 dispatch-action entry the
            composer wrote at step 8b. If None (legacy compat / unit-test
            convenience), synthesizes `cp-audit:<cp_action_id>` opaque
            marker; the production composer always supplies a real ref.

    Returns:
        a fully-signed `AuditLedgerEntry` ready for `audit_writer.append`.

    Raises:
        ValueError: from `sign_audit_entry` when `key_id` is empty per the
            CP spec v1.7 §13.5.1 converter signature contract.
    """
    # Q2(a) entry_core source semantic: production composer supplies the
    # F2 dispatch-action `StateLedgerEntryRef`. Synthesis fallback retained
    # for unit-test ergonomics + legacy callers (e.g., the round-trip
    # property tests that don't simulate a full composer).
    resolved_entry_core: StateLedgerEntryRef = (
        entry_core
        if entry_core is not None
        else StateLedgerEntryRef(f"cp-audit:{cp_entry.action_id}")
    )

    # Q1 chain-equivalence: CP `prior_event_hash` and OD `prior_entry_hash`
    # are the same SHA-256 hash-chain link per C-IS-06 / C-IS-13 §13.5. Direct
    # re-use; operator ratifies at spec amendment.
    payload = AuditPayload(
        entry_core=resolved_entry_core,
        audit_namespace_attrs=_project_namespace_attrs(cp_entry),
        prior_entry_hash=cp_entry.prior_event_hash,
    )

    signature_attrs = sign_audit_entry(payload, key_id=key_id, algo=algo)
    entry_hash = compute_entry_hash(payload)

    return AuditLedgerEntry(
        payload=payload,
        signature_attrs=signature_attrs,
        entry_hash=entry_hash,
    )
