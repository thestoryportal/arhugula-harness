"""Foundational discriminator enums — U-AS-04.

Implements C-AS-02 §2.3 (and forward use at C-AS-09 §9.1 / C-AS-10 §10.1 /
C-AS-12 §12.2). Declares the call-site discriminator enums consumed by
downstream AS-axis composition units: deployment surface, persona tier,
MCP transport.

Authority: Implementation_Plan_Action_Surface_v1.md §2 U-AS-04;
Spec_Action_Surface_v1.md §2 C-AS-02; ADR-D2 v1.1.

Pure data types — no associated functions, no metadata tables (acceptance
#6). `PersonaTier` ordering for cross-deployment monotonicity is carried by
declaration order (SOLO_DEVELOPER < TEAM_BINDING < MULTI_TENANT_COMPLIANCE).
"""

from __future__ import annotations

from enum import StrEnum


class DeploymentSurface(StrEnum):
    """Deployment surface of a harness binding (C-AS-09 §9.1 row axis)."""

    LOCAL_DEVELOPMENT = "local-development"
    SELF_HOSTED_SERVER = "self-hosted-server"
    MANAGED_CLOUD = "managed-cloud"


class PersonaTier(StrEnum):
    """Persona tier — declaration order is the monotonic ordering."""

    SOLO_DEVELOPER = "solo-developer"
    TEAM_BINDING = "team-binding"
    MULTI_TENANT_COMPLIANCE = "multi-tenant-compliance"


class MCPTransport(StrEnum):
    """MCP transport / remote-trust level (C-AS-10 §10.1)."""

    STDIO = "stdio"
    STREAMABLE_HTTP_L0_REFUSE = "streamable_http_l0"
    STREAMABLE_HTTP_L1_PINNED = "streamable_http_l1"
    STREAMABLE_HTTP_L2_SANDBOX = "streamable_http_l2"
    STREAMABLE_HTTP_L3_AUDIT = "streamable_http_l3"
