"""Runtime-side C-MEM-03 `provider_family` value-domain authority - U-MEM-26.

`Spec_Memory_Substrate_v1.md` C-MEM-03 (v1.1) binds `MemoryScope.provider_family`
to a `ProviderFamily` VALUE - never a provider key, a model identifier, or a
CLI-profile identifier. The split is exactly two dispositions, "no third
posture":

* a REGISTERED provider key is canonicalized to that key's `ProviderFamily`
  value through the workspace's provider-to-family authority
  (`lifecycle/cross_family_cost_tag.provider_family_for_scope_check`), and
* an UNREGISTERED / otherwise out-of-domain identifier is DENIED - the write is
  refused, and the request is refused against every family-scoped record.

`harness-is` cannot reach that authority (the IS axis has zero outbound
cross-axis edges, `harness-is/CLAUDE.md` §1.1), so it declares the rule as an
injectable `ScopeFamilyCanonicalizer` seam and leaves the authority to its
composition root. This module IS that composition root for the runtime axis: it
binds the seam to the real provider-to-family map once, so every runtime memory
surface - the authoring writers and the direct readers alike - resolves
`provider_family` through one implementation rather than each rolling its own.

`None` is deliberately NOT a fallback for an unknown key. Under C-MEM-03's
asymmetric semantics a stored `null` is the UNPARTITIONED WILDCARD that matches
every requested family, so degrading an unknown key to `null` would WIDEN the
record's reach rather than narrow it, against R-MEM-12. Denial is the only
fail-closed disposition.

Each calling surface raises in its OWN deny vocabulary (a promotion candidate
raises a promotion error, a native-adapter write raises the native callback
error, ...), so this module answers "is it in the domain, and what is its
canonical form" and never decides how a refusal is surfaced.
"""

from __future__ import annotations

from harness_is.memory_record_envelope import MemoryScope
from harness_is.memory_scope_value_domain import RequestScopeResolution, resolve_request_scope

from harness_runtime.lifecycle.cross_family_cost_tag import provider_family_for_scope_check

__all__ = [
    "canonical_scope_family",
    "resolve_scope_family",
    "scope_family_out_of_domain_message",
]


def canonical_scope_family(provider_family: str) -> str | None:
    """Return the canonical `ProviderFamily` value, or `None` when out of domain.

    This is the `ScopeFamilyCanonicalizer` the IS read layers accept. It is the
    fail-closed `provider_family_for_scope_check` - NOT the cost-attribution
    `provider_family_for_provider`, whose `LOCAL_OPEN_WEIGHT` fallback would
    silently admit an unregistered key into a real partition (`B-86`).
    """
    family = provider_family_for_scope_check(provider_family)
    return None if family is None else family.value


def resolve_scope_family(scope: MemoryScope) -> RequestScopeResolution:
    """Canonicalize a scope's `provider_family`, or flag it out of domain.

    A `null` `provider_family` passes through untouched: it is the legitimate
    unpartitioned value, not an out-of-domain identifier.
    """
    return resolve_request_scope(scope, canonical_scope_family)


def scope_family_out_of_domain_message(scope: MemoryScope) -> str:
    """Render the shared refusal wording for an out-of-domain `provider_family`."""

    return (
        f"memory scope provider_family {scope.provider_family!r} is neither a "
        "ProviderFamily value nor a registered provider key (C-MEM-03 value domain)"
    )
