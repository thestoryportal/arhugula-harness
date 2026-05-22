"""C-CP-27 PerServerTrustEvaluator + MCPClientNamespaceEmitter type carriers.

U-CP-66 — first unit of cluster 10-CP-C. Declares the 3 carrier enums that the
C-CP-27 `PerServerTrustEvaluator.evaluate` (U-CP-68) + the `mcp.trust.evaluate`
span emission (U-CP-70) consume at runtime:

- `MCPPrimitive` — 4-class MCP-primitive taxonomy per C-AS-14 §14.3 enum
  (tool / resource / prompt / sampling).
- `TrustDecisionReason` — 6-class trust-decision-outcome taxonomy per CP spec
  v1.10 §27.2. Includes the two `UNKNOWN_SERVER_*` members per Decision 3.D1
  RATIFIED (ALLOW-with-tier-floor for unknown servers).
- `TierDerivationRule` — 3-class tier-derivation strategy for unknown servers
  (CONSERVATIVE default per §27.7 deferred-to-discretion notes).

Member string values are cited verbatim from CP spec v1.10 §27.2.

U-CP-67 EXTENDS this file with the `TrustPolicy` + `TrustEvaluation` envelope
models that consume these enums.

Authority: CP spec v1.10 §27.2 (NEW C-CP-27); plan unit U-CP-66
(CP plan v2.15 §1 cluster 10-CP-C, preserved at v2.17).
"""

from __future__ import annotations

from enum import StrEnum


# ---------------------------------------------------------------------------
# U-CP-66 enum carriers (3 enums; §27.2 verbatim)
# ---------------------------------------------------------------------------


class MCPPrimitive(StrEnum):
    """4-class MCP primitive taxonomy per C-AS-14 §14.3 + CP spec v1.10 §27.2.

    Member values match the `modelcontextprotocol.io` primitive enumeration
    (tool / resource / prompt / sampling) consumed by the
    `mcp.primitive.kind` span attribute declared at AS §14.3.
    """

    TOOL = "tool"
    RESOURCE = "resource"
    PROMPT = "prompt"
    SAMPLING = "sampling"


class TrustDecisionReason(StrEnum):
    """6-class trust-decision outcome taxonomy per CP spec v1.10 §27.2.

    The two `UNKNOWN_SERVER_*` members reflect Decision 3.D1 RATIFIED:
    unknown-server default = ALLOW-with-tier-floor (was DENY at draft;
    operator-elected ALLOW). UNKNOWN decisions always carry
    `audit_required=true` per §27.6 invariant 4.
    """

    EXPLICIT_ALLOW = "explicit_allow"
    EXPLICIT_DENY = "explicit_deny"
    TIER_FLOOR_PASS = "tier_floor_pass"
    TIER_FLOOR_VIOLATION = "tier_floor_violation"
    UNKNOWN_SERVER_TIER_FLOOR_PASS = "unknown_server_tier_floor_pass"
    UNKNOWN_SERVER_TIER_FLOOR_VIOLATION = "unknown_server_tier_floor_violation"


class TierDerivationRule(StrEnum):
    """3-class tier-derivation strategy for unknown servers per CP spec v1.10
    §27.2.

    - `CONSERVATIVE` — resolved tier = `MIN(MCPTrustTier members)` per §27.7
      deferred-to-discretion notes; the explicit minimum member is
      `LEVEL_0_REFUSE_REMOTE` per `harness_cp.cp_shared_types.MCPTrustTier`
      enum-order convention.
    - `PROTOCOL_VERSION_TABLE` — operator-supplied mapping
      `protocol_version → MCPTrustTier`; lookup at evaluator-resolution time.
    - `OPERATOR_HOOK` — operator-supplied callable
      `Callable[[str, str | None], MCPTrustTier]`; concrete signature owed
      to U-CP-18 implementation arc per §27.7.
    """

    CONSERVATIVE = "conservative"
    PROTOCOL_VERSION_TABLE = "protocol_version_table"
    OPERATOR_HOOK = "operator_hook"
