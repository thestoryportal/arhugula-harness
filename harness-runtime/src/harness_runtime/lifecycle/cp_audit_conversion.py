"""CP→OD audit-write converter — DISCOVERY-GRADE PROTOTYPE.

**This module is NOT wired into the runtime composer at v1.6.** It is a
discovery prototype filed in response to `[[class_1_tension_u_rt_59_cp_to_od_audit_write_gap]]`
to validate materializability of the field projection from `CPAuditLedgerEntry`
(CP-shape per C-CP-16 §16.2) to `AuditLedgerEntry` (OD-shape per C-OD-14 §14.5).

Full scoping report at `.harness/u_rt_59_fork_2_cp_to_od_audit_discovery.md`. Five
open spec-level sub-questions (Q1–Q5) are documented there; this prototype encodes
provisional answers and marks each with an inline `DISCOVERY_ASSUMPTION` comment.

**Wiring is gated on operator ratification.** Do not import this module from any
composer until the discovery report's sub-questions are resolved and the relevant
spec amendments land (see report §4).

**Home rationale.** The fork file originally proposed homing at `harness-od/`,
but that would create a new OD→CP outbound edge in violation of OD's
"OD outbound (downstream): 0" invariant per `harness-od/CLAUDE.md` §2.2. Runtime
is the existing CP+OD composition substrate (`audit_writer.py` already imports
both `harness_cp.*` indirectly via composer surface and `harness_od.audit_ledger_types`).
Final home is operator decision per discovery report Q5.
"""

from __future__ import annotations

import hashlib

from harness_cp.per_step_override_evaluator import CPAuditLedgerEntry
from harness_od.audit_ledger_types import (
    AuditLedgerEntry,
    AuditPayload,
    SignatureAlgorithm,
    StateLedgerEntryRef,
)
from harness_od.multi_tenant_trace_separation_and_audit_ledger import sign_audit_entry

#: Namespace prefix for CP-sourced fields landing in OD `audit_namespace_attrs`.
#: Provisional per discovery report Q4 — operator may ratify alternative
#: (`audit.source.cp.*`, `cp.*`, semantic grouping). Spec ratification at
#: C-OD-05 §5.1 amendment.
CP_AUDIT_NAMESPACE_PREFIX = "audit.cp"


def _compute_entry_hash(payload: AuditPayload) -> str:
    """Compute `AuditLedgerEntry.entry_hash` per interim convention.

    DISCOVERY_ASSUMPTION (Q3): C-OD-14 §14.5.1 specifies "8-field SHA-256
    composition + field-ordering" but no canonical helper exists at HEAD.
    Interim convention: SHA-256 over Pydantic JSON dump with sorted keys.
    Replaceable when an OD-canonical helper lands (separate follow-up arc).
    """
    canonical = payload.model_dump_json()
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


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

    **DISCOVERY-GRADE.** Not wired to runtime composer. Encodes provisional
    answers to the discovery report's Q1–Q5. See module docstring.

    Parameters:
        cp_entry: the CP-shape unsigned audit entry from the composer.
        key_id: OD `audit.signature.key_id` per C-OD-21 §21.2.
        algo: OD `audit.signature.algorithm`; defaults to Ed25519 per ADR-D5
            v1.3 §1.4.1.
        entry_core: OD `payload.entry_core` IS reference. If None, synthesizes
            `cp-audit:<cp_action_id>` per discovery report Q2 Option (c) (opaque
            marker; no real IS entry). Operator may instead pass a real
            `StateLedgerEntryRef` per Q2 Option (a) or (b).

    Returns:
        a fully-signed `AuditLedgerEntry` ready for `RuntimeAuditLedgerWriter.append`.

    Raises:
        ValueError: from `sign_audit_entry` when `key_id` is empty.
    """
    # DISCOVERY_ASSUMPTION (Q2): synthesize opaque entry_core when caller does
    # not supply a real IS state-ledger entry reference. Option (c) per report.
    resolved_entry_core: StateLedgerEntryRef = (
        entry_core
        if entry_core is not None
        else StateLedgerEntryRef(f"cp-audit:{cp_entry.action_id}")
    )

    # DISCOVERY_ASSUMPTION (Q1): CP `prior_event_hash` and OD `prior_entry_hash`
    # are semantically equivalent (both SHA-256 over prior canonical entry on
    # the same IS-anchored hash chain per C-IS-06 / C-IS-13 §13.5). Direct
    # re-use; operator ratifies at spec amendment.
    payload = AuditPayload(
        entry_core=resolved_entry_core,
        audit_namespace_attrs=_project_namespace_attrs(cp_entry),
        prior_entry_hash=cp_entry.prior_event_hash,
    )

    signature_attrs = sign_audit_entry(payload, key_id=key_id, algo=algo)
    entry_hash = _compute_entry_hash(payload)

    return AuditLedgerEntry(
        payload=payload,
        signature_attrs=signature_attrs,
        entry_hash=entry_hash,
    )
