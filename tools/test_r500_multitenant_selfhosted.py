from __future__ import annotations

from pathlib import Path

from tools.r500_multitenant_selfhosted_live_e2e import (
    CHILD_SPAN,
    ROOT_SPAN,
    STRUCTURE_SENTINEL,
    TENANT_A,
    _assert_tenant_trace_records,
    _tempo_span_records,
    _trace_id_hex,
)

ROOT = Path(__file__).resolve().parents[1]


def test_trace_id_hex_is_tempo_width() -> None:
    assert _trace_id_hex(0xABC) == "00000000000000000000000000000abc"


def test_tempo_span_records_supports_resource_spans_payload() -> None:
    payload = {
        "resourceSpans": [
            {
                "resource": {
                    "attributes": [
                        {"key": "tenant.id", "value": {"stringValue": TENANT_A}},
                    ],
                },
                "scopeSpans": [
                    {
                        "spans": [
                            {
                                "name": ROOT_SPAN,
                                "attributes": [
                                    {
                                        "key": "audit.signature.sha256",
                                        "value": {"stringValue": STRUCTURE_SENTINEL},
                                    }
                                ],
                            },
                        ]
                    }
                ],
            }
        ]
    }

    [record] = _tempo_span_records(payload)
    assert record.name == ROOT_SPAN
    assert record.resource_attributes["tenant.id"] == TENANT_A
    assert record.span_attributes["audit.signature.sha256"] == STRUCTURE_SENTINEL


def test_tempo_span_records_supports_tempo_batches_payload() -> None:
    payload = {
        "batches": [
            {
                "resource": {
                    "attributes": [
                        {"key": "tenant.id", "value": {"stringValue": TENANT_A}},
                    ],
                },
                "instrumentationLibrarySpans": [
                    {
                        "spans": [
                            {
                                "name": CHILD_SPAN,
                                "attributes": [
                                    {
                                        "key": "audit.signature.sha256",
                                        "value": {"stringValue": STRUCTURE_SENTINEL},
                                    }
                                ],
                            },
                        ]
                    }
                ],
            }
        ]
    }

    [record] = _tempo_span_records(payload)
    assert record.name == CHILD_SPAN
    assert record.resource_attributes["tenant.id"] == TENANT_A
    assert record.span_attributes["audit.signature.sha256"] == STRUCTURE_SENTINEL


def test_tenant_trace_assertion_accepts_redacted_structure_only_records() -> None:
    records = [
        _tempo_span_records(
            {
                "resourceSpans": [
                    {
                        "resource": {
                            "attributes": [
                                {"key": "tenant.id", "value": {"stringValue": TENANT_A}},
                            ],
                        },
                        "scopeSpans": [
                            {
                                "spans": [
                                    {
                                        "name": name,
                                        "attributes": [
                                            {
                                                "key": "audit.signature.sha256",
                                                "value": {"stringValue": STRUCTURE_SENTINEL},
                                            }
                                        ],
                                    }
                                ]
                            }
                        ],
                    }
                ]
            }
        )[0]
        for name in (ROOT_SPAN, CHILD_SPAN)
    ]

    _assert_tenant_trace_records(records, tenant_id=TENANT_A)


def test_justfile_exposes_r500_live_e2e_recipe() -> None:
    justfile = (ROOT / "justfile").read_text(encoding="utf-8")

    assert "r500-multitenant-live-e2e config:" in justfile
    assert "uv run --package harness-runtime python" in justfile
    assert "tools/r500_multitenant_selfhosted_live_e2e.py" in justfile


def test_self_hosted_readme_documents_r500_live_e2e() -> None:
    readme = (ROOT / "deploy" / "self-hosted-local" / "README.md").read_text(encoding="utf-8")

    assert "just r500-multitenant-live-e2e harness.selfhosted.local.toml" in readme
    assert "tenant-resource-separated=true" in readme
    assert "audit-ledger-separated=true" in readme
