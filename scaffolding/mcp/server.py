"""7a substitution scaffolding — FastMCP server (substitutes H_T-AS-2).

NOT H_T atomic-unit implementation. Bounded 7a substitution scaffolding
per Phase_7a_Substitution_Scaffolding.md §4 + Phase_7_Meta_Architecture_v1.md
§5.3 (H_T-AS-2). Retired wholesale when U-AS-04..U-AS-09 land. The MCP
server *process* is the X-AL-1 substrate boundary (H_E <-> H_T).

The tools below are 7a *representative* tools — schema-faithful stubs that
exercise tool-schema authoring + namespacing + description-as-prompt across
the 4 axes (7a exit-criterion #3: >=3 per axis, >=12 total). They do NOT
implement axis logic — that lands at the atomic-unit consumptions. Per
ledger §4.3, surface 4 covers the tool-authoring surface only. write_file
and run_bash perform their real H_E-equivalent op (pure filesystem/shell,
no axis logic — consistent with read_file); all IS/CP/OD tool bodies are
schema-faithful stubs.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict, Field

mcp = FastMCP("harness-7a-scaffold")


# --- AS axis ---------------------------------------------------------------


class ReadFileOutput(BaseModel):
    """Structured, validated output for the read_file tool (Pydantic v2)."""

    model_config = ConfigDict(extra="forbid")

    path: str = Field(description="Resolved path that was read.")
    content: str = Field(description="UTF-8 text content of the file.")
    byte_count: int = Field(description="Length of the content in UTF-8 bytes.")


@mcp.tool()
def read_file(path: str) -> ReadFileOutput:
    """Read a UTF-8 text file and return its content.

    7a representative tool — AS axis. [substitutes H_T-AS-2]
    """
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    return ReadFileOutput(path=str(p), content=text, byte_count=len(text.encode("utf-8")))


class WriteFileOutput(BaseModel):
    """Structured, validated output for the write_file tool (Pydantic v2)."""

    model_config = ConfigDict(extra="forbid")

    path: str = Field(description="Resolved path that was written.")
    byte_count: int = Field(description="UTF-8 bytes written to the file.")


@mcp.tool()
def write_file(path: str, content: str) -> WriteFileOutput:
    """Write UTF-8 text content to a file, creating or overwriting it.

    7a representative tool — AS axis. [substitutes H_T-AS-2]
    """
    p = Path(path)
    p.write_text(content, encoding="utf-8")
    return WriteFileOutput(path=str(p), byte_count=len(content.encode("utf-8")))


class RunBashOutput(BaseModel):
    """Structured, validated output for the run_bash tool (Pydantic v2)."""

    model_config = ConfigDict(extra="forbid")

    exit_code: int = Field(description="Process exit code.")
    stdout: str = Field(description="Captured standard output.")
    stderr: str = Field(description="Captured standard error.")


@mcp.tool()
def run_bash(command: str, timeout_s: int = 30) -> RunBashOutput:
    """Run a shell command and return its exit code and captured streams.

    7a representative tool — AS axis. [substitutes H_T-AS-2]
    """
    proc = subprocess.run(  # bounded 7a scaffolding shell-out
        command,
        shell=True,
        capture_output=True,
        text=True,
        timeout=timeout_s,
    )
    return RunBashOutput(exit_code=proc.returncode, stdout=proc.stdout, stderr=proc.stderr)


# --- IS axis ---------------------------------------------------------------


class LedgerAppendOutput(BaseModel):
    """Structured, validated output for the append_state_ledger tool."""

    model_config = ConfigDict(extra="forbid")

    entry_index: int = Field(description="Ordinal index of the appended entry.")
    line_bytes: int = Field(description="UTF-8 byte length of the JSONL line.")


@mcp.tool()
def append_state_ledger(
    action_id: str,
    idempotency_key: str,
    actor: str,
    response_hash: str,
    timestamp: str,
    prior_event_hash: str,
) -> LedgerAppendOutput:
    """Append a canonical 6-field entry to the state ledger (C-IS-05 §5).

    7a representative tool — IS axis. Schema-faithful stub: validates the
    6-field shape and reports the JSONL line size; the append shell-out
    itself is surface 2. [substitutes H_T-IS-5]
    """
    line = json.dumps(
        {
            "action_id": action_id,
            "idempotency_key": idempotency_key,
            "actor": actor,
            "response_hash": response_hash,
            "timestamp": timestamp,
            "prior_event_hash": prior_event_hash,
        },
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )
    return LedgerAppendOutput(entry_index=0, line_bytes=len(line.encode("utf-8")))


class LedgerReadOutput(BaseModel):
    """Structured, validated output for the read_state_ledger tool."""

    model_config = ConfigDict(extra="forbid")

    entries: list[str] = Field(description="Raw JSONL lines, oldest first.")
    count: int = Field(description="Number of entries returned.")


@mcp.tool()
def read_state_ledger(limit: int = 10) -> LedgerReadOutput:
    """Read up to `limit` entries from the state ledger.

    7a representative tool — IS axis. Schema-faithful stub. [substitutes H_T-IS-5]
    """
    return LedgerReadOutput(entries=[], count=0)


class HashChainVerifyOutput(BaseModel):
    """Structured, validated output for the verify_hash_chain tool."""

    model_config = ConfigDict(extra="forbid")

    valid: bool = Field(description="True if the chain verifies end-to-end.")
    entries_checked: int = Field(description="Number of entries verified.")
    first_break_index: int = Field(description="Index of the first chain break, or -1 if none.")


@mcp.tool()
def verify_hash_chain() -> HashChainVerifyOutput:
    """Verify the state-ledger hash-chain linkage (C-IS-06 §6).

    7a representative tool — IS axis. Schema-faithful stub. [substitutes H_T-IS-6]
    """
    return HashChainVerifyOutput(valid=True, entries_checked=0, first_break_index=-1)


# --- CP axis ---------------------------------------------------------------


class RouteOutput(BaseModel):
    """Structured, validated output for the route_llm_call tool."""

    model_config = ConfigDict(extra="forbid")

    provider: str = Field(description="Selected LLM provider.")
    model: str = Field(description="Selected model identifier.")
    source: str = Field(description="Origin of the routing decision.")


@mcp.tool()
def route_llm_call(role: str, path_class: str, step: str) -> RouteOutput:
    """Resolve a (role, path_class, step) tuple to a provider/model target.

    7a representative tool — CP axis. Schema-faithful stub: returns the 7a
    single-LLM substitution target. [substitutes H_T-CP-1]
    """
    return RouteOutput(
        provider="anthropic",
        model="claude-sonnet-4-6",
        source="7a-single-llm-substitution",
    )


class RetryOutput(BaseModel):
    """Structured, validated output for the invoke_with_retry tool."""

    model_config = ConfigDict(extra="forbid")

    attempts: int = Field(description="Number of attempts made.")
    succeeded: bool = Field(description="True if the operation succeeded.")
    breaker_state: str = Field(description="Circuit-breaker state after the call.")


@mcp.tool()
def invoke_with_retry(operation_id: str, max_attempts: int = 3) -> RetryOutput:
    """Invoke an operation under retry + circuit-breaker discipline.

    7a representative tool — CP axis. Schema-faithful stub. [substitutes H_T-CP-3]
    """
    return RetryOutput(attempts=1, succeeded=True, breaker_state="CLOSED")


class HitlOutput(BaseModel):
    """Structured, validated output for the hitl_prompt tool."""

    model_config = ConfigDict(extra="forbid")

    response: str = Field(description="Operator response text.")
    response_class: str = Field(
        description="Palette class: APPROVE / APPROVE_WITH_NOTE / DEFER / REJECT."
    )


@mcp.tool()
def hitl_prompt(question: str, palette: list[str]) -> HitlOutput:
    """Surface a human-in-the-loop prompt and return the operator response.

    7a representative tool — CP axis. Schema-faithful stub. [substitutes H_T-CP-20]
    """
    return HitlOutput(response="APPROVE", response_class="APPROVE")


# --- OD axis ---------------------------------------------------------------


class EmitSpanOutput(BaseModel):
    """Structured, validated output for the emit_span tool."""

    model_config = ConfigDict(extra="forbid")

    namespace: str = Field(description="OTel namespace the span was emitted to.")
    span_id: str = Field(description="Identifier of the emitted span.")
    accepted: bool = Field(description="True if the span was accepted for export.")


@mcp.tool()
def emit_span(namespace: str, span_name: str, attributes: dict[str, str]) -> EmitSpanOutput:
    """Emit an OTel span into one of the 12 H_T namespaces.

    7a representative tool — OD axis. Schema-faithful stub. [substitutes H_T-OD-2]
    """
    return EmitSpanOutput(namespace=namespace, span_id="0" * 16, accepted=True)


class RedactSpanOutput(BaseModel):
    """Structured, validated output for the redact_span tool."""

    model_config = ConfigDict(extra="forbid")

    namespace: str = Field(description="OTel namespace of the span.")
    redacted_attributes: dict[str, str] = Field(
        description="Attributes after structure-not-content redaction."
    )
    redaction_count: int = Field(description="Number of attributes redacted.")


@mcp.tool()
def redact_span(namespace: str, span_name: str, attributes: dict[str, str]) -> RedactSpanOutput:
    """Apply structure-not-content redaction to span attributes before export.

    7a representative tool — OD axis. Schema-faithful stub. [substitutes H_T-OD-4]
    """
    redacted = {k: "<redacted>" for k in attributes}
    return RedactSpanOutput(
        namespace=namespace,
        redacted_attributes=redacted,
        redaction_count=len(redacted),
    )


class RecordCostOutput(BaseModel):
    """Structured, validated output for the record_cost tool."""

    model_config = ConfigDict(extra="forbid")

    action_id: str = Field(description="Action the cost was attributed to.")
    cost_recorded: bool = Field(description="True if the cost was recorded.")


@mcp.tool()
def record_cost(action_id: str, provider: str, tokens_in: int, tokens_out: int) -> RecordCostOutput:
    """Record per-attempt token cost attributed to an action.

    7a representative tool — OD axis. Schema-faithful stub. [substitutes H_T-OD-5]
    """
    return RecordCostOutput(action_id=action_id, cost_recorded=True)


if __name__ == "__main__":
    mcp.run()  # stdio transport
