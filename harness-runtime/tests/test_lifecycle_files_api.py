"""R-810 provider-free Files API contract tests."""

from __future__ import annotations

from io import BytesIO
from typing import BinaryIO

import pytest
from harness_runtime.lifecycle.files_api import (
    ANTHROPIC_FILES_API_BETA,
    FilesApiClientProtocol,
    FilesApiFile,
    FilesOperationKind,
    container_upload_block,
    files_operation_span,
)
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import (
    InMemorySpanExporter,
)


class FakeFilesApiClient:
    def __init__(self) -> None:
        self.deleted: list[str] = []

    async def upload(
        self,
        *,
        file: BinaryIO,
        filename: str,
        mime_type: str,
    ) -> FilesApiFile:
        data = file.read()
        return FilesApiFile(
            file_id="file_test",
            filename=filename,
            mime_type=mime_type,
            size_bytes=len(data),
            workspace_id="workspace_test",
        )

    async def list_files(self) -> tuple[FilesApiFile, ...]:
        return (
            FilesApiFile(
                file_id="file_test",
                filename="data.csv",
                mime_type="text/csv",
                size_bytes=11,
                workspace_id="workspace_test",
            ),
        )

    async def retrieve_metadata(self, *, file_id: str) -> FilesApiFile:
        return FilesApiFile(
            file_id=file_id,
            filename="data.csv",
            mime_type="text/csv",
            size_bytes=11,
            workspace_id="workspace_test",
        )

    async def delete(self, *, file_id: str) -> None:
        self.deleted.append(file_id)


@pytest.fixture
def tracer_with_exporter() -> tuple[TracerProvider, InMemorySpanExporter]:
    provider = TracerProvider()
    exporter = InMemorySpanExporter()
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    return provider, exporter


def test_beta_header_constant_tracks_anthropic_files_api() -> None:
    assert ANTHROPIC_FILES_API_BETA == "files-api-2025-04-14"


def test_container_upload_block_shapes_reference_content() -> None:
    assert container_upload_block("file_123") == {
        "type": "container_upload",
        "file_id": "file_123",
    }


@pytest.mark.asyncio
async def test_files_api_protocol_is_provider_free() -> None:
    client: FilesApiClientProtocol = FakeFilesApiClient()

    uploaded = await client.upload(
        file=BytesIO(b"a,b\n1,2\n"),
        filename="data.csv",
        mime_type="text/csv",
    )
    assert uploaded == FilesApiFile(
        file_id="file_test",
        filename="data.csv",
        mime_type="text/csv",
        size_bytes=8,
        workspace_id="workspace_test",
    )

    listed = await client.list_files()
    assert listed[0].file_id == "file_test"
    assert await client.retrieve_metadata(file_id="file_test") == listed[0]
    await client.delete(file_id="file_test")
    assert client.deleted == ["file_test"]


@pytest.mark.asyncio
async def test_files_operation_span_emits_upload_namespace(
    tracer_with_exporter: tuple[TracerProvider, InMemorySpanExporter],
) -> None:
    provider, exporter = tracer_with_exporter
    tracer = provider.get_tracer(__name__)
    uploaded = FilesApiFile(
        file_id="file_test",
        filename="data.csv",
        mime_type="text/csv",
        size_bytes=8,
        workspace_id="workspace_test",
    )

    async with files_operation_span(
        tracer=tracer,
        kind=FilesOperationKind.UPLOAD,
        file=uploaded,
    ):
        pass

    spans = [span for span in exporter.get_finished_spans() if span.name == "files.operation"]
    assert len(spans) == 1
    attrs = spans[0].attributes or {}
    assert attrs["files.operation.kind"] == "upload"
    assert attrs["files.file_id"] == "file_test"
    assert attrs["files.filename"] == "data.csv"
    assert attrs["files.mime_type"] == "text/csv"
    assert attrs["files.size_bytes"] == 8
    assert attrs["files.workspace_id"] == "workspace_test"
    assert "files.batch_composition" not in attrs
    assert "files.code_execution_composition" not in attrs


@pytest.mark.asyncio
async def test_files_operation_span_emits_reference_composition_flags(
    tracer_with_exporter: tuple[TracerProvider, InMemorySpanExporter],
) -> None:
    provider, exporter = tracer_with_exporter
    tracer = provider.get_tracer(__name__)

    async with files_operation_span(
        tracer=tracer,
        kind=FilesOperationKind.REFERENCE,
        file_id="file_test",
        workspace_id="workspace_test",
        batch_composition=True,
        code_execution_composition=True,
    ):
        pass

    spans = [span for span in exporter.get_finished_spans() if span.name == "files.operation"]
    assert len(spans) == 1
    attrs = spans[0].attributes or {}
    assert attrs["files.operation.kind"] == "reference"
    assert attrs["files.file_id"] == "file_test"
    assert attrs["files.workspace_id"] == "workspace_test"
    assert attrs["files.batch_composition"] is True
    assert attrs["files.code_execution_composition"] is True
