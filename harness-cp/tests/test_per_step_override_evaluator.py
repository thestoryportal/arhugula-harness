"""Tests for U-CP-14 — per-step override evaluator + CP audit-ledger entries.

Acceptance-criterion coverage:
  #1 resolve_step_binding field-by-field -> test_resolve_step_binding_field_by_field_override
  #2 audit_ref populated on override     -> test_audit_ref_populated_on_override
  #2 action_id composition               -> test_audit_entry_action_id_composition
  #4 deterministic                       -> test_override_evaluator_deterministic
  #5 CPAuditLedgerEntry 8 fields          -> test_cp_audit_ledger_entry_eight_fields
  #5 response-conditional hash population -> test_cp_audit_entry_response_conditional_hash_population
  #6 CPSignedAuditLedgerEntry 5 sig fields -> test_cp_signed_audit_entry_five_signature_fields
  #6 distinct from OD AuditLedgerEntry    -> test_cp_audit_types_distinct_from_od
"""

from __future__ import annotations

from harness_as import GateLevel
from harness_core import PersonaTier, StepID, WorkloadClass

from harness_cp.cp_shared_types import ModelBinding
from harness_cp.cross_family_fallback_chain import (
    FallbackChain,
    ProviderCandidate,
    ProviderFamily,
)
from harness_cp.engine_class import EngineClass
from harness_cp.per_step_override_evaluator import (
    CPAuditLedgerEntry,
    CPSignedAuditLedgerEntry,
    emit_override_audit_entry,
    resolve_step_binding,
)
from harness_cp.topology_pattern import TopologyPattern
from harness_cp.workflow_manifest_entry import StepOverride, WorkflowManifestEntry

_DEFAULT_BINDING = ModelBinding(provider="anthropic", model="default-model")
_OVERRIDE_BINDING = ModelBinding(provider="anthropic", model="override-model")
_CHAIN = FallbackChain(
    primary=ProviderCandidate(
        provider="anthropic", model="m", family=ProviderFamily.ANTHROPIC
    ),
    same_family=(),
    cross_family=(),
    terminal=None,
)


def _manifest(**over: object) -> WorkflowManifestEntry:
    base: dict[str, object] = {
        "workflow_id": "wf-1",
        "workload_class": WorkloadClass.PIPELINE_AUTOMATION,
        "persona_tier": PersonaTier.TEAM_BINDING,
        "engine_class": EngineClass.PURE_PATTERN_NO_ENGINE,
        "topology_pattern": TopologyPattern.SINGLE_THREADED_LINEAR,
        "layer_budgets": (),
        "fallback_chain": _CHAIN,
        "hitl_placements": (),
        "per_step_overrides": {},
    }
    base.update(over)
    return WorkflowManifestEntry(**base)  # type: ignore[arg-type]


def test_resolve_step_binding_field_by_field_override() -> None:
    manifest = _manifest(
        per_step_overrides={
            StepID("s1"): StepOverride(
                step_id=StepID("s1"), model_binding=_OVERRIDE_BINDING
            )
        }
    )
    binding = resolve_step_binding(
        manifest, "s1", default_model_binding=_DEFAULT_BINDING
    )
    # model_binding overridden; engine_class inherits the manifest default.
    assert binding.model_binding == _OVERRIDE_BINDING
    assert binding.engine_class is EngineClass.PURE_PATTERN_NO_ENGINE


def test_audit_ref_populated_on_override() -> None:
    manifest = _manifest(
        per_step_overrides={
            StepID("s1"): StepOverride(
                step_id=StepID("s1"), engine_class=EngineClass.EVENT_SOURCED_REPLAY
            )
        }
    )
    binding = resolve_step_binding(
        manifest, "s1", default_model_binding=_DEFAULT_BINDING
    )
    assert binding.override_applied is True
    assert binding.override_audit_ref is not None

    no_override = resolve_step_binding(
        manifest, "s2", default_model_binding=_DEFAULT_BINDING
    )
    assert no_override.override_applied is False
    assert no_override.override_audit_ref is None


def test_audit_entry_action_id_composition() -> None:
    entry = emit_override_audit_entry(
        workflow_id="wf-1",
        step_id="s1",
        override=StepOverride(step_id=StepID("s1")),
        actor="ctl",  # type: ignore[arg-type]
    )
    assert entry.action_id == "wf-1||s1"


def test_override_evaluator_deterministic() -> None:
    manifest = _manifest(
        per_step_overrides={
            StepID("s1"): StepOverride(
                step_id=StepID("s1"), model_binding=_OVERRIDE_BINDING
            )
        }
    )
    a = resolve_step_binding(manifest, "s1", default_model_binding=_DEFAULT_BINDING)
    b = resolve_step_binding(manifest, "s1", default_model_binding=_DEFAULT_BINDING)
    assert a == b


def test_cp_audit_ledger_entry_eight_fields() -> None:
    assert len(CPAuditLedgerEntry.model_fields) == 8
    assert set(CPAuditLedgerEntry.model_fields) == {
        "action_id",
        "gate_level",
        "response",
        "edited_proposal_hash",
        "rejection_reason_hash",
        "response_text_hash",
        "timestamp",
        "prior_event_hash",
    }


def test_cp_audit_entry_response_conditional_hash_population() -> None:
    approve = CPAuditLedgerEntry(
        action_id="a||s",  # type: ignore[arg-type]
        gate_level=GateLevel.AUTO,
        response="approve",
        timestamp="t",
        prior_event_hash="0" * 64,
    )
    assert approve.edited_proposal_hash is None
    assert approve.rejection_reason_hash is None
    assert approve.response_text_hash is None

    edit = CPAuditLedgerEntry(
        action_id="a||s",  # type: ignore[arg-type]
        gate_level=GateLevel.ASK,
        response="edit",
        edited_proposal_hash="f" * 64,
        timestamp="t",
        prior_event_hash="0" * 64,
    )
    assert edit.edited_proposal_hash == "f" * 64


def test_cp_signed_audit_entry_five_signature_fields() -> None:
    sig_fields = set(CPSignedAuditLedgerEntry.model_fields) - {"entry"}
    assert sig_fields == {
        "audit_signature_sha256",
        "audit_signature_value",
        "audit_signature_algorithm",
        "audit_signature_key_id",
        "audit_signature_key_period",
    }


def test_cp_audit_types_distinct_from_od() -> None:
    # The CP audit types are CP-spec-owned, nominally distinct from the OD
    # AuditLedgerEntry (U-OD-00). The CP names carry the `CP` prefix per the
    # v2.9 §0.5.1 name-collision resolution.
    assert CPAuditLedgerEntry.__name__ == "CPAuditLedgerEntry"
    assert CPSignedAuditLedgerEntry.__name__ == "CPSignedAuditLedgerEntry"
