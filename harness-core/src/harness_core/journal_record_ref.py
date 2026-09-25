"""Shared exact identity for one durable workflow pause-journal record."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class JournalRecordRef(BaseModel):
    """The record-count position and raw-line digest pinned at capture time.

    Runtime creates this value under the journal append lock. CP can later carry
    it without importing Runtime or copying its representation.
    """

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    tenant: str | None
    workflow_id: str = Field(min_length=1)
    run_id: str = Field(min_length=1)
    record_count: int = Field(gt=0)
    latest_digest: str = Field(pattern=r"^[0-9a-f]{64}$")
    snapshot_hash: str = Field(pattern=r"^[0-9a-f]{64}$")
