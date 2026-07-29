"""C-MEM-03 scope null-asymmetry and request-side value domain - U-MEM-26.

The three read-boundary enforcement layers (`MemoryRetriever._scope_mismatch`,
`DerivedRetrievalIndexStore` / `_scope_matches`, and
`memory_policy._scope_not_broader`) each enforce the C-MEM-03 scope boundary on
their own terms, per the U-MEM-26 per-layer requirement. This module is the
single implementation of the two rules they share, so the layers cannot drift
apart again:

* the asymmetric-`null` rule for the SCOPE-PARTITION fields, and
* the request-side `provider_family` value domain.

Scope-partition fields (`provider_family`, `tenant`) vs. intersection fields
--------------------------------------------------------------------------
`Spec_Memory_Substrate_v1.md` C-MEM-03 writes the asymmetry for
`provider_family`: a stored `null` is the unpartitioned wildcard and matches any
requested family, while a `null` REQUEST does not widen access past a
family-scoped record ("a request that declines to name a partition is asking for
*broader* reach than a partitioned record permits"). The forward-register row
`B-90` carries the same reading for `tenant`, whose omission left every
tool-captured record tenant-unpartitioned against the threat-model mandate at
`Spec_Memory_Substrate_v1.md:481`.

The asymmetry is therefore applied to exactly those two fields. `project`,
`workflow`, `workload_class`, and `cli_profile` keep the pre-existing
either-side-`null`-skips (intersection) semantics: the contract says nothing
about them, and silently converting them would change behaviour no cleared
artifact asks for (for instance the regression guard asserting that a
`workflow=None` record still matches a concrete-`workflow` query). Widening the
asymmetry to those fields is a spec question, not an implementation one.

Injected value-domain authority
-------------------------------
`provider_family` carries a `ProviderFamily` value, never a provider key. The
provider-to-family authority lives at
`harness-runtime/src/harness_runtime/lifecycle/cross_family_cost_tag.py`
(`provider_family_for_scope_check`), which `harness-is` MUST NOT import: the IS
axis has zero outbound cross-axis edges (`harness-is/CLAUDE.md` §1.1). The
authority is therefore an OPTIONAL injected collaborator - the same
composition-root injection shape the workspace uses for
`SigningBackend`-style seams.

The registered / unregistered split is exactly two dispositions, per C-MEM-03's
"no third posture": a registered key is canonicalized to its family value, and
an out-of-domain identifier REJECTS THE REQUEST. It never reaches a scope
predicate as the raw string it arrived as, and it is not quietly narrowed to
"whatever an unscoped request could see" either - EVERY record is denied,
unpartitioned records included. That is the disposition C-MEM-03 v1.1 states
(out-of-domain is "rejected") and the one every other boundary already applies:
`StandardMemoryToolExecutor._resolved_scope` denies the call, the capture and
promotion write boundaries raise, and the native adapter refuses. Serving the
unpartitioned remainder would be a third posture between canonicalize and
reject - a rejected request answered anyway, just with less.

A `null` REQUEST is a different thing and still reaches unpartitioned records:
naming no partition is the legitimate unscoped ask, not an identifier this
layer failed to resolve. Those are the asymmetric-`null` semantics above; they
are not an out-of-domain outcome.

When it is ABSENT the pre-existing comparison behaviour for non-`null` values is
preserved verbatim (raw string comparison); only the `null` asymmetry above
applies, which needs no value domain. Production composition MUST inject it -
without it the request side is un-enforced and a crafted raw-key request can
still reach a legacy raw-key record (C-MEM-03 request-side paragraph; U-MEM-26
request-boundary acceptance criterion).
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Final, NamedTuple

from harness_is.memory_record_envelope import MemoryScope

ScopeFamilyCanonicalizer = Callable[[str], str | None]
"""Injected provider-to-family authority for request-side `provider_family`.

Given a requested `provider_family` string, returns the canonical
`ProviderFamily` value for a registered provider key (or the value itself when
it is already one), and `None` when the identifier is out of the value domain.
`None` means "unregistered, so its family is UNKNOWN" and MUST fail closed at
the caller - never "assume it matches".
"""

SCOPE_PARTITION_FIELDS: Final[tuple[str, ...]] = ("provider_family", "tenant")
"""Fields carrying the C-MEM-03 asymmetric-`null` semantics (`B-90` for tenant)."""

SCOPE_INTERSECTION_FIELDS: Final[tuple[str, ...]] = (
    "project",
    "workflow",
    "workload_class",
    "cli_profile",
)
"""Fields keeping the pre-existing either-side-`null`-skips semantics."""


class RequestScopeResolution(NamedTuple):
    """A request scope after request-side `provider_family` resolution."""

    scope: MemoryScope
    """The request scope with a registered provider key canonicalized."""

    family_out_of_domain: bool
    """True when the requested `provider_family` is not in the value domain.

    The caller MUST reject the whole request on it - every record, not only the
    partition-scoped ones (see the module docstring).
    """


def resolve_request_scope(
    scope: MemoryScope,
    canonicalizer: ScopeFamilyCanonicalizer | None,
) -> RequestScopeResolution:
    """Canonicalize a request scope's `provider_family`, or flag it out-of-domain.

    A registered provider key is canonicalized to its family value before any
    predicate compares it; an out-of-domain identifier is flagged so the caller
    can reject the request in that layer's own deny vocabulary. With no
    `canonicalizer` injected the scope passes through
    unchanged - the documented un-wired default (see the module docstring).
    """
    requested_family = scope.provider_family
    if canonicalizer is None or requested_family is None:
        return RequestScopeResolution(scope=scope, family_out_of_domain=False)
    canonical = canonicalizer(requested_family)
    if canonical is None:
        return RequestScopeResolution(scope=scope, family_out_of_domain=True)
    if canonical == requested_family:
        return RequestScopeResolution(scope=scope, family_out_of_domain=False)
    return RequestScopeResolution(
        scope=scope.model_copy(update={"provider_family": canonical}),
        family_out_of_domain=False,
    )


def scope_partition_denied(
    record_scope: MemoryScope,
    requested_scope: MemoryScope | None,
) -> bool:
    """True when a partition field denies the request against this record.

    A `null` RECORD value is the unpartitioned wildcard and matches anything. A
    non-`null` record value requires an EQUAL requested value: a `null` request
    (including an entirely absent request scope, passed as `None`) is a broader
    ask than the partitioned record permits and is denied.
    """
    for field_name in SCOPE_PARTITION_FIELDS:
        record_value = getattr(record_scope, field_name)
        if record_value is None:
            continue
        requested_value = None if requested_scope is None else getattr(requested_scope, field_name)
        if requested_value != record_value:
            return True
    return False


def scope_intersection_denied(
    record_scope: MemoryScope,
    requested_scope: MemoryScope,
) -> bool:
    """True when an intersection field denies the request against this record.

    Pre-existing semantics, preserved verbatim: a `null` on EITHER side is
    "unconstrained on this dimension"; only two concrete unequal values deny.
    """
    for field_name in SCOPE_INTERSECTION_FIELDS:
        record_value = getattr(record_scope, field_name)
        requested_value = getattr(requested_scope, field_name)
        if record_value is not None and requested_value is not None:
            if record_value != requested_value:
                return True
    return False


__all__ = [
    "SCOPE_INTERSECTION_FIELDS",
    "SCOPE_PARTITION_FIELDS",
    "RequestScopeResolution",
    "ScopeFamilyCanonicalizer",
    "resolve_request_scope",
    "scope_intersection_denied",
    "scope_partition_denied",
]
