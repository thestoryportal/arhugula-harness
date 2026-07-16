"""Tests for U-AS-21 — negative-observation invariant enforcement (C-AS-05 §5.3)."""

from __future__ import annotations

from harness_as.secret_negative_observation import (
    NegativeObservationSurface,
    validate_no_secret_in_audit_ledger_entry,
    validate_no_secret_in_span_attributes,
    validate_no_secret_in_static_prefix,
    verify_sole_resolution_path,
)

_MARKERS = frozenset({"sk-live-deadbeef"})


def test_validate_no_secret_in_static_prefix_detects_known_pattern() -> None:
    """Acceptance #1/#2 — a known secret pattern in the prefix is a violation."""
    violation = validate_no_secret_in_static_prefix(
        "system prompt ... sk-live-deadbeef ...", _MARKERS
    )
    assert violation is not None


def test_validate_no_secret_in_static_prefix_passes_clean_prefix() -> None:
    """Acceptance #1 — a clean prefix passes."""
    assert validate_no_secret_in_static_prefix("system prompt only", _MARKERS) is None


def test_validate_no_secret_in_span_attributes_composes_with_u_as_17_exclusions() -> None:
    """Acceptance #3 — an exclusion-set attribute name is a violation."""
    violation = validate_no_secret_in_span_attributes({"secret_value": "x"})
    assert violation is not None


def test_validate_no_secret_in_audit_ledger_entry_detects_value_content() -> None:
    """Acceptance #1 — a secret value in a ledger-entry field is a violation."""
    violation = validate_no_secret_in_audit_ledger_entry(
        {"note": "leaked sk-live-deadbeef"}, _MARKERS
    )
    assert violation is not None


def test_verify_sole_resolution_path_rejects_manifest_arrival() -> None:
    """Acceptance #4 — a secret arriving via the manifest is a violation."""
    violation = verify_sole_resolution_path("workflow_manifest")
    assert violation is not None
    assert violation.surface is NegativeObservationSurface.WORKFLOW_MANIFEST_ENTRY


def test_verify_sole_resolution_path_accepts_fetch_secret_arrival() -> None:
    """Acceptance #4 — a secret arriving via fetch_secret is permitted."""
    assert verify_sole_resolution_path("fetch_secret") is None


def test_verify_sole_resolution_path_dispatches_known_sites_to_matching_surfaces() -> None:
    """B-24 — dispatch reflects the real arrival site, not a hardcoded label."""
    assert (
        verify_sole_resolution_path("prompt_cache_prefix").surface
        is NegativeObservationSurface.STATIC_PROMPT_CACHE_PREFIX
    )
    assert (
        verify_sole_resolution_path("span_attributes").surface
        is NegativeObservationSurface.SPAN_ATTRIBUTES
    )
    assert (
        verify_sole_resolution_path("log_records").surface is NegativeObservationSurface.LOG_RECORDS
    )
    assert (
        verify_sole_resolution_path("audit_ledger_entry").surface
        is NegativeObservationSurface.AUDIT_LEDGER_ENTRY
    )


def test_verify_sole_resolution_path_dispatches_spec_short_form_labels() -> None:
    """B-24 (Codex round 1) — §5.3's own vocabulary (manifest, prompt, log, ledger)
    must dispatch to the matching surface, not fall through to the manifest default."""
    assert (
        verify_sole_resolution_path("manifest").surface
        is NegativeObservationSurface.WORKFLOW_MANIFEST_ENTRY
    )
    assert (
        verify_sole_resolution_path("prompt").surface
        is NegativeObservationSurface.STATIC_PROMPT_CACHE_PREFIX
    )
    assert verify_sole_resolution_path("log").surface is NegativeObservationSurface.LOG_RECORDS
    assert (
        verify_sole_resolution_path("ledger").surface
        is NegativeObservationSurface.AUDIT_LEDGER_ENTRY
    )


def test_verify_sole_resolution_path_unrecognized_site_defaults_to_manifest() -> None:
    """merge-gate test-witness lens — the documented default-fallback branch
    (an arrival site absent from _ARRIVAL_SITE_SURFACES) was previously
    unwitnessed; pins it explicitly against regressing to the pre-fix
    hardcoded STATIC_PROMPT_CACHE_PREFIX bug."""
    violation = verify_sole_resolution_path("some_unlabeled_site")
    assert violation is not None
    assert violation.surface is NegativeObservationSurface.WORKFLOW_MANIFEST_ENTRY
