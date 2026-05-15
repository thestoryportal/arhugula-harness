"""7a substitution scaffolding — FastMCP server (substitutes H_T-AS-2).

NOT H_T atomic-unit implementation. Bounded 7a substitution scaffolding
per Phase_7a_Substitution_Scaffolding.md §4 + Phase_7_Meta_Architecture_v1.md
§5.3 (H_T-AS-2). Retired wholesale when U-AS-04..U-AS-09 land. The MCP
server *process* is the X-AL-1 substrate boundary (H_E <-> H_T).
"""

from __future__ import annotations

from pathlib import Path

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict, Field

mcp = FastMCP("harness-7a-scaffold")


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
    return ReadFileOutput(
        path=str(p), content=text, byte_count=len(text.encode("utf-8"))
    )


if __name__ == "__main__":
    mcp.run()  # stdio transport
