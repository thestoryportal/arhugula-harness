"""Tests for U-AS-04 — foundational discriminator enums (C-AS-02 §2.3)."""

from __future__ import annotations

from harness_as.discriminators import DeploymentSurface, MCPTransport, PersonaTier

_SPEC_DEPLOYMENT_SURFACES = {
    "local-development",
    "self-hosted-server",
    "managed-cloud",
}
_SPEC_PERSONA_TIERS = {"solo-developer", "team-binding", "multi-tenant-compliance"}
_SPEC_MCP_TRANSPORTS = {
    "stdio",
    "streamable_http_l0",
    "streamable_http_l1",
    "streamable_http_l2",
    "streamable_http_l3",
}


def test_deployment_surface_cardinality_three() -> None:
    """Acceptance #1 — DeploymentSurface carries exactly 3 values."""
    assert len(DeploymentSurface) == 3
    assert {d.value for d in DeploymentSurface} == _SPEC_DEPLOYMENT_SURFACES


def test_persona_tier_cardinality_three() -> None:
    """Acceptance #2 — PersonaTier carries exactly 3 values."""
    assert len(PersonaTier) == 3
    assert {p.value for p in PersonaTier} == _SPEC_PERSONA_TIERS


def test_persona_tier_ordering_monotonic() -> None:
    """Acceptance #2 — declaration order SOLO < TEAM < MULTI_TENANT."""
    assert list(PersonaTier) == [
        PersonaTier.SOLO_DEVELOPER,
        PersonaTier.TEAM_BINDING,
        PersonaTier.MULTI_TENANT_COMPLIANCE,
    ]


def test_mcp_transport_cardinality_five() -> None:
    """Acceptance #3 — MCPTransport carries exactly 5 values."""
    assert len(MCPTransport) == 5
    assert {m.value for m in MCPTransport} == _SPEC_MCP_TRANSPORTS


def test_enum_identifier_strings_byte_exact() -> None:
    """Acceptance #5 — identifier strings byte-exact spec-canonical."""
    assert DeploymentSurface.LOCAL_DEVELOPMENT.value == "local-development"
    assert PersonaTier.MULTI_TENANT_COMPLIANCE.value == "multi-tenant-compliance"
    assert MCPTransport.STREAMABLE_HTTP_L0_REFUSE.value == "streamable_http_l0"
