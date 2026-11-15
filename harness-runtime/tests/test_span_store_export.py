"""Production ingestion into the sqlite span store on the runtime export path.

With `[runtime.collector] span_store_path` set, the spans a real `TracerProvider` finishes
reach the store the operator tools read (OD spec §C-OD-27, §C-OD-19 §19.3) and reach the
OTLP exporter unchanged. A store that cannot be written never fails the export.
"""

from __future__ import annotations

import json
import logging
import sqlite3
from pathlib import Path

import pytest
from harness_core import DeploymentSurface
from harness_cp.topology_pattern import TopologyPattern
from harness_od.sqlite_span_store import initialize_span_store
from harness_od.sqlite_span_store_reader import read_all_spans, read_spans_by_workflow
from harness_runtime.admin.trace_browser import (
    compute_operator_burden_rollups,
    open_readonly_span_store,
)
from harness_runtime.lifecycle.span_processor import (
    SpanProcessorBindError,
    materialize_span_processor_stage,
)
from harness_runtime.lifecycle.span_store_export import SpanStoreMirror
from harness_runtime.types import (
    CollectorConfig,
    OTelConfig,
    PathBindingConfig,
    ProviderSecretsConfig,
    RuntimeConfig,
)
from opentelemetry.sdk.trace import ReadableSpan, TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor, SpanExportResult
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from opentelemetry.trace import SpanKind, Status, StatusCode
from pydantic import ValidationError


def _config(tmp_path: Path, *, span_store_path: Path | None) -> RuntimeConfig:
    return RuntimeConfig(
        deployment_surface=DeploymentSurface.LOCAL_DEVELOPMENT,
        repository_root=tmp_path,
        path_bindings=PathBindingConfig(),
        provider_secrets=ProviderSecretsConfig(),
        otel=OTelConfig(otlp_endpoint="http://localhost:4317"),
        collector=CollectorConfig(span_store_path=span_store_path),
        default_topology=TopologyPattern.SINGLE_THREADED_LINEAR,
    )


def _emit_one_workflow(provider: TracerProvider) -> None:
    """A workflow envelope with one failed client child and one HITL response span."""
    tracer = provider.get_tracer("test")
    with tracer.start_as_current_span("workflow.envelope") as envelope:
        envelope.set_attribute("workflow.id", "wf-1")
        envelope.set_attribute("workflow.run_id", "run-1")
        envelope.set_attribute("workflow.idempotency_key", "idem-1")
        with tracer.start_as_current_span("chat llama3.2:3b", kind=SpanKind.CLIENT) as chat:
            chat.set_attribute("gen_ai.usage.input_tokens", 32)
            chat.set_attribute("gen_ai.response.finish_reasons", ("stop",))
            chat.add_event("retry", {"attempt": 2})
            chat.set_status(Status(StatusCode.ERROR, "upstream refused"))
        with tracer.start_as_current_span("hitl.invocation.responded"):
            pass


def _finished_workflow_spans() -> tuple[ReadableSpan, ...]:
    """The spans of one emitted workflow, as an exporter receives them."""
    recorder = InMemorySpanExporter()
    provider = TracerProvider()
    provider.add_span_processor(SimpleSpanProcessor(recorder))
    _emit_one_workflow(provider)
    return recorder.get_finished_spans()


def test_finished_spans_reach_the_store_and_the_otlp_exporter_unchanged(tmp_path: Path) -> None:
    store_path = tmp_path / "observability" / "spans.sqlite"
    provider = TracerProvider()
    otlp = InMemorySpanExporter()
    stage = materialize_span_processor_stage(
        _config(tmp_path, span_store_path=store_path), provider, exporter=otlp
    )

    _emit_one_workflow(provider)
    assert provider.force_flush()

    assert isinstance(stage.exporter, SpanStoreMirror)
    assert stage.exporter.stored_span_count == 3 and stage.exporter.failed_span_count == 0
    exported = {span.name: span for span in otlp.get_finished_spans()}
    conn = open_readonly_span_store(store_path)
    rows = {row.name: row for row in read_all_spans(conn)}
    assert (
        set(rows)
        == set(exported)
        == {
            "workflow.envelope",
            "chat llama3.2:3b",
            "hitl.invocation.responded",
        }
    )

    envelope, chat = rows["workflow.envelope"], rows["chat llama3.2:3b"]
    assert envelope.parent_span_id is None
    assert chat.parent_span_id == envelope.span_id and chat.trace_id == envelope.trace_id
    assert envelope.span_id == format(exported["workflow.envelope"].context.span_id, "016x")
    assert (envelope.workflow_id, envelope.workflow_run_id, envelope.workflow_idempotency_key) == (
        "wf-1",
        "run-1",
        "idem-1",
    )
    assert (chat.workflow_id, chat.workflow_run_id, chat.workflow_idempotency_key) == (
        None,
        None,
        None,
    )
    # OTLP numbering: INTERNAL = 1, CLIENT = 3; status ERROR = 2 with its description.
    assert (envelope.kind, chat.kind) == (1, 3)
    assert (chat.status_code, chat.status_message) == (2, "upstream refused")
    assert chat.end_time_ns >= chat.start_time_ns > 0
    assert json.loads(chat.attributes_json) == {
        "gen_ai.response.finish_reasons": ["stop"],
        "gen_ai.usage.input_tokens": 32,
    }
    [event] = json.loads(chat.events_json)
    assert (event["name"], event["attributes"]) == ("retry", {"attempt": 2})

    # The operator tools read the same store: the workflow query and the TUI rollup.
    assert [row.name for row in read_spans_by_workflow(conn, "wf-1", "run-1")] == [
        "workflow.envelope"
    ]
    hitl = next(
        rollup
        for rollup in compute_operator_burden_rollups(conn)
        if rollup.declaration.source_span_class == "hitl.invocation.responded"
    )
    assert hitl.matching_span_count == 1
    conn.close()
    provider.shutdown()


def test_without_a_store_path_the_exporter_is_the_otlp_exporter_and_no_store_exists(
    tmp_path: Path,
) -> None:
    provider = TracerProvider()
    otlp = InMemorySpanExporter()
    stage = materialize_span_processor_stage(
        _config(tmp_path, span_store_path=None), provider, exporter=otlp
    )

    _emit_one_workflow(provider)
    assert provider.force_flush()

    assert stage.exporter is otlp
    assert len(otlp.get_finished_spans()) == 3
    assert list(tmp_path.iterdir()) == []
    provider.shutdown()


def test_a_store_that_cannot_be_written_is_counted_and_never_fails_the_export(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    connection = initialize_span_store(tmp_path / "spans.sqlite")
    connection.execute("DROP TABLE spans")
    otlp = InMemorySpanExporter()
    mirror = SpanStoreMirror(downstream=otlp, connection=connection, retention_days=7)
    spans = _finished_workflow_spans()

    with caplog.at_level(logging.ERROR, logger="harness.runtime.span_store"):
        result = mirror.export(spans)

    assert result is SpanExportResult.SUCCESS
    assert len(otlp.get_finished_spans()) == 3
    assert (mirror.stored_span_count, mirror.failed_span_count) == (0, 3)
    assert "span store write failed for a batch of 3 spans" in caplog.text
    mirror.shutdown()


def test_a_reexported_span_is_stored_once(tmp_path: Path) -> None:
    spans = _finished_workflow_spans()
    store_path = tmp_path / "spans.sqlite"
    mirror = SpanStoreMirror(
        downstream=InMemorySpanExporter(),
        connection=initialize_span_store(store_path),
        retention_days=7,
    )

    mirror.export(spans)
    mirror.export(spans)

    assert mirror.stored_span_count == 3
    conn = sqlite3.connect(store_path)
    assert conn.execute("SELECT COUNT(*) FROM spans").fetchone() == (3,)
    conn.close()
    mirror.shutdown()


def test_spans_past_the_retention_horizon_are_removed_on_the_next_write(tmp_path: Path) -> None:
    spans = _finished_workflow_spans()
    newest_end_ns = max(span.end_time or 0 for span in spans)
    eight_days_ns = 8 * 86_400 * 1_000_000_000
    store_path = tmp_path / "spans.sqlite"
    mirror = SpanStoreMirror(
        downstream=InMemorySpanExporter(),
        connection=initialize_span_store(store_path),
        retention_days=7,
        clock_ns=lambda: newest_end_ns + eight_days_ns,
    )

    mirror.export(spans)

    conn = sqlite3.connect(store_path)
    assert conn.execute("SELECT COUNT(*) FROM spans").fetchone() == (0,)
    conn.close()
    mirror.shutdown()


def test_an_unusable_store_path_fails_bootstrap(tmp_path: Path) -> None:
    blocker = tmp_path / "not-a-directory"
    blocker.write_text("x")

    with pytest.raises(SpanProcessorBindError):
        materialize_span_processor_stage(
            _config(tmp_path, span_store_path=blocker / "spans.sqlite"),
            TracerProvider(),
            exporter=InMemorySpanExporter(),
        )


def test_a_relative_store_path_is_refused_at_config_load() -> None:
    with pytest.raises(ValidationError, match="span_store_path must be an absolute path"):
        CollectorConfig(span_store_path=Path("observability/spans.sqlite"))
