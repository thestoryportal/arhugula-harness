from __future__ import annotations

from pathlib import Path

from tools.r430_tail_keep_collector_live_e2e import _tempo_span_names, _trace_id_hex

ROOT = Path(__file__).resolve().parents[1]


def test_trace_id_hex_is_tempo_width() -> None:
    assert _trace_id_hex(0xABC) == "00000000000000000000000000000abc"


def test_tempo_span_names_supports_scope_spans_payload() -> None:
    payload = {
        "resourceSpans": [
            {
                "scopeSpans": [
                    {
                        "spans": [
                            {"name": "r430.trigger.root"},
                            {"name": "sandbox.violation"},
                        ]
                    }
                ]
            }
        ]
    }

    assert _tempo_span_names(payload) == {"r430.trigger.root", "sandbox.violation"}


def test_tempo_span_names_supports_instrumentation_library_payload() -> None:
    payload = {
        "batches": [
            {
                "instrumentationLibrarySpans": [
                    {
                        "spans": [
                            {"name": "r430.plain.root"},
                            {"name": "r430.plain.child"},
                        ]
                    }
                ]
            }
        ]
    }

    assert _tempo_span_names(payload) == {"r430.plain.root", "r430.plain.child"}


def test_justfile_exposes_r430_live_e2e_recipe() -> None:
    justfile = (ROOT / "justfile").read_text(encoding="utf-8")

    assert "r430-tail-keep-live-e2e config:" in justfile
    assert "uv run --package harness-runtime python" in justfile
    assert "tools/r430_tail_keep_collector_live_e2e.py" in justfile


def test_self_hosted_readme_documents_r430_live_e2e() -> None:
    readme = (ROOT / "deploy" / "self-hosted-local" / "README.md").read_text(encoding="utf-8")

    assert "just r430-tail-keep-live-e2e harness.selfhosted.local.toml" in readme
    assert "trigger-trace-preserved=true" in readme
