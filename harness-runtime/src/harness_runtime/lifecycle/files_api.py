"""R-810 provider-free Files API contract helpers.

This module opens the runtime-side Files API boundary without constructing a
provider SDK client or making managed-cloud calls. It supplies:

- a small provider-neutral file metadata record,
- a protocol for future Anthropic Files API adapters, and
- a `files.operation` span helper carrying the AS `files.*` namespace.

The live upload/reference e2e remains gated on the R-810 managed-cloud arc.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator, Mapping
from contextlib import asynccontextmanager
from dataclasses import dataclass
from enum import StrEnum
from typing import Any, BinaryIO, Protocol

__all__ = [
    "ANTHROPIC_FILES_API_BETA",
    "FilesApiClientProtocol",
    "FilesApiFile",
    "FilesOperationKind",
    "container_upload_block",
    "files_operation_span",
]


ANTHROPIC_FILES_API_BETA = "files-api-2025-04-14"
"""Anthropic Files API beta header value used by the managed R-810 live path."""


class FilesOperationKind(StrEnum):
    """AS `files.operation.kind` enum values."""

    UPLOAD = "upload"
    LIST = "list"
    METADATA = "metadata"
    DELETE = "delete"
    REFERENCE = "reference"


@dataclass(frozen=True, slots=True)
class FilesApiFile:
    """Provider-neutral metadata for a file stored by a managed Files API."""

    file_id: str
    filename: str
    mime_type: str
    size_bytes: int
    workspace_id: str


class FilesApiClientProtocol(Protocol):
    """Minimal async port for a future provider-backed Files API adapter."""

    async def upload(
        self,
        *,
        file: BinaryIO,
        filename: str,
        mime_type: str,
    ) -> FilesApiFile:
        ...

    async def list_files(self) -> tuple[FilesApiFile, ...]:
        ...

    async def retrieve_metadata(self, *, file_id: str) -> FilesApiFile:
        ...

    async def delete(self, *, file_id: str) -> None:
        ...


def container_upload_block(file_id: str) -> Mapping[str, str]:
    """Return the Anthropic code-execution content block for `file_id`.

    This helper is pure data shaping; it does not validate provider reachability
    or claim that the referenced file exists.
    """

    return {"type": "container_upload", "file_id": file_id}


@asynccontextmanager
async def files_operation_span(
    *,
    tracer: Any,
    kind: FilesOperationKind,
    file: FilesApiFile | None = None,
    file_id: str | None = None,
    filename: str | None = None,
    mime_type: str | None = None,
    size_bytes: int | None = None,
    workspace_id: str | None = None,
    batch_composition: bool | None = None,
    code_execution_composition: bool | None = None,
) -> AsyncGenerator[Any, None]:
    """Open a `files.operation` span with the AS `files.*` attributes.

    The helper accepts either a full `FilesApiFile` or explicit fields. This
    lets future live adapters emit metadata directly after upload/retrieve while
    provider-free tests can exercise reference/delete spans without SDK calls.
    """

    resolved_file_id = file.file_id if file is not None else file_id
    resolved_filename = file.filename if file is not None else filename
    resolved_mime_type = file.mime_type if file is not None else mime_type
    resolved_size_bytes = file.size_bytes if file is not None else size_bytes
    resolved_workspace_id = file.workspace_id if file is not None else workspace_id

    with tracer.start_as_current_span("files.operation") as span:
        span.set_attribute("files.operation.kind", kind.value)
        if resolved_file_id is not None:
            span.set_attribute("files.file_id", resolved_file_id)
        if resolved_filename is not None:
            span.set_attribute("files.filename", resolved_filename)
        if resolved_mime_type is not None:
            span.set_attribute("files.mime_type", resolved_mime_type)
        if resolved_size_bytes is not None:
            span.set_attribute("files.size_bytes", resolved_size_bytes)
        if resolved_workspace_id is not None:
            span.set_attribute("files.workspace_id", resolved_workspace_id)
        if batch_composition is not None:
            span.set_attribute("files.batch_composition", batch_composition)
        if code_execution_composition is not None:
            span.set_attribute("files.code_execution_composition", code_execution_composition)
        yield span
