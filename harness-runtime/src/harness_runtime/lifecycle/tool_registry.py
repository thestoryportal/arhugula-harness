"""U-RT-14 — Tool contract registry.

Per `Spec_Harness_Runtime_v1.md` v1.1 §4 (C-RT-04 `tool_contracts` field:
`dict[ToolName, ToolContract]`) and Phase 2 Session 3 plan v2.1 §2 L3 U-RT-14.

Class 1 risk-flag absorption (plan §2 L3 U-RT-14):
- Plan flagged: 'registration *site* may not be specified — Class 1 candidate.'
- Pre-flight reading: AS shipped `ToolContract` (the schema) at U-AS-07 + the
  allowlist-intersection function but NO `register_tool_contract` function and
  NO `ToolRegistry` class. The registration site is genuinely runtime-side.
- Per the L0 Class 2 Tension authorization, the runtime owns the registry
  surface. Registration is operator-driven (or MCP-proxied at U-RT-15);
  this module ships the registry API only.

Scope at L3:
- `ToolRegistry`: runtime composition primitive wrapping the bare
  `dict[ToolName, ToolContract]` declared at C-RT-04. Adds typed register/
  lookup + duplicate-name rejection.
- `materialize_tool_registry(skills)`: builds an empty registry at stage 2
  AS bootstrap. Future hooks (skill-declared tools, MCP-proxied tools) plug
  in later via `register()`; the `skills` parameter is reserved for that
  future use even at L3 (currently a no-op input).
"""

from __future__ import annotations

from collections.abc import Iterable

from harness_as.tool_contract import ToolContract

from harness_runtime.lifecycle.skills import Skill
from harness_runtime.lifecycle.tool_search import SEARCH_TOOLS_TOOL_NAME
from harness_runtime.types import SkillID, ToolName

__all__ = [
    "DuplicateToolNameError",
    "ReservedToolNameError",
    "ToolNameNotRegisteredError",
    "ToolRegistry",
    "materialize_tool_registry",
]


class DuplicateToolNameError(ValueError):
    """Raised when `register` is called with an already-registered tool name."""

    def __init__(self, name: ToolName) -> None:
        super().__init__(f"tool {name!r} already registered")
        self.name = name


class ReservedToolNameError(ValueError):
    """Raised when `register` is called with a name reserved for a synthetic tool.

    B-TOOL-SEARCH-RUNTIME (AS spec v1.13 §13.7): `search_tools` is reserved
    for the synthetic capability-discovery tool the frozen superset appends
    when `defer_names` is non-empty. Without this reservation, a real MCP
    tool named `search_tools` would collide with the synthetic contract —
    `_RuntimeToolDispatcherModelCallAdapter.dispatch` intercepts EVERY call
    named `search_tools` unconditionally, so a real tool of that name would
    silently never be dispatched (its calls answered with synthetic search
    results instead). Fail loud at registration rather than allow the
    silent shadowing, mirroring `DuplicateToolNameError`'s existing
    fail-loud-on-collision precedent in this same class.
    """

    def __init__(self, name: ToolName) -> None:
        super().__init__(
            f"tool name {name!r} is reserved for the synthetic "
            "search_tools capability-discovery contract (AS spec v1.13 §13.7)"
        )
        self.name = name


class ToolNameNotRegisteredError(KeyError):
    """Raised when `get` is called with a name not in the registry."""

    def __init__(self, name: ToolName) -> None:
        super().__init__(f"tool {name!r} not registered")
        self.name = name


class ToolRegistry:
    """Runtime tool-contract registry — name-indexed dispatch surface.

    The 'discriminator dispatch' per plan §2 L3 AC is the per-tool-name
    indexing: a single `name: str` field on `ToolContract` (C-AS-03 §3.1) is
    the dispatch key; `register` rejects duplicates so each name resolves to
    at most one contract.
    """

    def __init__(self) -> None:
        self._by_name: dict[ToolName, ToolContract] = {}

    def register(self, contract: ToolContract) -> None:
        """Register a tool contract; reject if its name already exists.

        Also rejects `SEARCH_TOOLS_TOOL_NAME` — reserved for the synthetic
        capability-discovery tool (see `ReservedToolNameError`).
        """
        name = ToolName(contract.name)
        if name == SEARCH_TOOLS_TOOL_NAME:
            raise ReservedToolNameError(name)
        if name in self._by_name:
            raise DuplicateToolNameError(name)
        self._by_name[name] = contract

    def get(self, name: ToolName) -> ToolContract:
        """Look up a contract by name; raise on miss."""
        if name not in self._by_name:
            raise ToolNameNotRegisteredError(name)
        return self._by_name[name]

    def names(self) -> Iterable[ToolName]:
        """Iterate over registered tool names."""
        return self._by_name.keys()

    def __len__(self) -> int:
        return len(self._by_name)

    def __contains__(self, name: object) -> bool:
        return name in self._by_name


def materialize_tool_registry(skills: dict[SkillID, Skill]) -> ToolRegistry:
    """Build the runtime tool-contract registry for stage 2 AS bootstrap.

    At L3, the registry is empty by default. Population is operator-driven
    (or MCP-proxied at U-RT-15 when MCP servers declare tool contracts).
    The `skills` parameter is reserved: a future SkillManifest extension
    could declare tool contracts, at which point this function will walk
    `skills.values()` and `register()` each declared contract.
    """
    # `skills` consumed to pin the parameter surface for the future hook.
    _ = skills
    return ToolRegistry()
