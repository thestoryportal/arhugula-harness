"""Runtime consumer of the CP prompt-selection surface (R-PM-1 cascade PR #3).

The CP ``PromptSelectionManifest`` resolver (``harness_cp.prompt_selection_manifest``)
yields a selected prompt ``version_sha`` for a ``(role, workload)``; the IS
``PromptManifest.versions`` content-addressed store (IS spec v1.7 §5.3) resolves
that sha to its content; the runtime translate-time injection seam (PR #1,
runtime spec v1.44 §14.5.2) places the content as a system prompt. **This module
is the runtime CONSUMER site that composes the two** — selection (CP) → sha →
store member (IS) → effective active prompt. It is where the PR #2 store gains
its consumer (the CP→IS store consultation is the CXA seam registered at
cascade PR #5; runtime is the consumer endpoint).

**Dimension honesty.** Reconciliation reads the run's REAL ``workload_class``
(threaded into ``run_bootstrap``) and the MVP-default agent role
(``_MVP_DEFAULT_AGENT_ROLE`` — the runtime has no per-step role at MVP; routing's
own ``per_role_bindings`` is likewise role-keyed only at R-300-second-provider).
So per-workload selection (``per_workload_overrides``) is behavior-driving
end-to-end, while per-role bindings are carried faithfully but resolved against
the default role until real per-role dispatch lands. This mirrors the routing
precedent exactly (`[[r-cxa-seam-wiring-is-producer-discovery]]` — don't build
the hollow per-role runtime indexer).

**Hash/injection coherence (the load-bearing correctness property).** The
selected version is reconciled ONTO ``active_prompt_version`` (a ``model_copy``
to the selected store member), NOT merely redirected at the injection reader. So
BOTH the runtime stage-5 injection reader (``active_prompt_version.content``) and
the C-IS-05 §5.2 procedural-tier hash reader (``active_prompt_version.version_sha``)
read the SAME selected version — consistent by construction. (Redirecting only
injection would reintroduce the content↔hash drift that PR #1's
``version_sha == digest(content)`` derive-invariant closed, one layer up.) The
``model_copy`` skips ``PromptManifest``'s ``mode="after"`` store-invariant
validator, but the selected member is already an authored store member satisfying
content↔sha + membership, so the copy is invariant-preserving.

**Cross-axis membership = fail-loud.** A bound sha that is not an authored member
of the store is a CP↔IS check declared runtime-deferred at the CP spec (§29.3,
mirroring ``validate_routing_manifest``'s runtime-deferred per-role
model-presence check); it is enforced HERE, detect-then-refuse
(``PromptSelectionUnauthoredError`` → ``RT-FAIL-PROMPT-SELECTION-UNAUTHORED``).

Authority: CP spec v1.31 §29 (the prompt-selection contract — incl. §29.4 the
runtime-consumer-site obligation + RT-FAIL-PROMPT-SELECTION-UNAUTHORED); runtime
spec v1.44 §14.5.2 (the translate-time injection seam this composes with); IS
spec v1.7 §5.3 (the `versions` store this consumes); R-PM-1 design §4.2.
"""

from __future__ import annotations

from harness_core import WorkloadClass
from harness_cp.cp_shared_types import AgentRole
from harness_cp.prompt_selection_manifest import (
    PromptSelectionManifest,
    resolve_active_prompt_version_sha,
    validate_prompt_selection_manifest,
)
from harness_is.prompt_manifest import PromptManifest

__all__ = [
    "InvalidPromptSelectionManifestError",
    "PromptSelectionUnauthoredError",
    "reconcile_active_prompt_via_selection",
]

# Mirrors ``llm_dispatch._MVP_DEFAULT_AGENT_ROLE`` — the runtime has no per-step
# agent role at MVP, so per-role prompt selection resolves against this default
# until real per-role dispatch (R-300-second-provider). Per-workload selection
# keys on the genuine run workload and is behavior-driving today.
_MVP_DEFAULT_AGENT_ROLE = AgentRole("default")


class PromptSelectionUnauthoredError(Exception):
    """Raised when a prompt-selection binding names a ``version_sha`` that is not
    an authored member of the IS ``PromptManifest.versions`` store (R-PM-1 PR #3).

    The store-membership check is a cross-axis (CP selection ↔ IS store) check,
    declared runtime-deferred at the CP spec (§29.3, mirroring
    ``validate_routing_manifest``'s runtime-deferred model-presence check) and
    enforced here at the runtime consumer site: **fail-loud / detect-then-refuse**,
    never silently fall through to the inline active prompt (consistent with the
    arc-#1 ``RT-FAIL-SANDBOX-DRIVER-UNAVAILABLE`` + PR-#1
    ``RT-FAIL-PROMPT-INJECTION-CONFLICT`` postures + ``[[conformance-validator-disciplines]]``).

    Maps to ``RT-FAIL-PROMPT-SELECTION-UNAUTHORED`` per CP spec v1.31 §29.4.
    Raised at bootstrap stage 0 reconciliation (before any procedural-tier
    snapshot is computed + before the dispatcher is constructed) → surfaces as a
    ``BootstrapFailure`` — a config/authoring error the operator must correct (you
    cannot select a version that was never authored), unlike the per-dispatch
    step-level ``RT-FAIL-PROMPT-INJECTION-CONFLICT``.
    """

    def __init__(self, version_sha: str) -> None:
        self.version_sha = version_sha
        super().__init__(
            "RT-FAIL-PROMPT-SELECTION-UNAUTHORED: prompt-selection binding names "
            f"version_sha={version_sha!r} which is not an authored member of the "
            "PromptManifest.versions store; fail-loud (a version must be authored "
            "in the store before it can be selected)"
        )


class InvalidPromptSelectionManifestError(Exception):
    """Raised when the operator-supplied ``PromptSelectionManifest`` fails the CP
    structural validator (``validate_prompt_selection_manifest``) at the runtime
    consumer site (R-PM-1 PR #3).

    Mirrors ``build_routing_manifest``'s ``InvalidRoutingManifestError`` — the CP
    structural manifest contract (e.g. ``manifest_version >= 1``) is enforced at
    bootstrap rather than silently bypassed (Codex P2-2). Raised at stage 0
    reconciliation → surfaces as a ``BootstrapFailure``. Maps to CP spec v1.31
    §29.5 (the ``manifest_version < 1`` row).
    """

    def __init__(self, reason: str) -> None:
        self.reason = reason
        super().__init__(f"invalid prompt-selection manifest: {reason}")


def reconcile_active_prompt_via_selection(
    prompt_manifest: PromptManifest,
    selection_manifest: PromptSelectionManifest | None,
    *,
    workload_class: WorkloadClass,
    role: AgentRole = _MVP_DEFAULT_AGENT_ROLE,
) -> PromptManifest:
    """Return ``prompt_manifest`` with ``active_prompt_version`` reconciled to the
    version the CP selection layer chooses for ``(role, workload)``, or unchanged.

    Fall-through (returns the manifest unchanged → the #496/PR-#1 standing inline
    active prompt, zero behavior change):

    * ``selection_manifest is None`` (no selection configured — the default), or
    * the manifest selects nothing for ``(role, workload)`` (``resolve`` → ``None``).

    Otherwise the selected ``version_sha`` MUST resolve to an authored member of
    ``prompt_manifest.versions``; the manifest is returned with
    ``active_prompt_version`` set to that member (so injection + the §5.2 hash
    both read it). A selected sha with no store member raises
    :class:`PromptSelectionUnauthoredError` (fail-loud). An operator-supplied
    manifest that fails the CP structural validator raises
    :class:`InvalidPromptSelectionManifestError` (fail-loud — parity with
    ``build_routing_manifest``'s bootstrap validation; Codex P2-2)."""
    if selection_manifest is None:
        return prompt_manifest
    validation_error = validate_prompt_selection_manifest(selection_manifest)
    if validation_error is not None:
        raise InvalidPromptSelectionManifestError(validation_error.reason)
    selected_sha = resolve_active_prompt_version_sha(
        selection_manifest, role=role, workload=workload_class
    )
    if selected_sha is None:
        return prompt_manifest
    for version in prompt_manifest.versions:
        if version.version_sha == selected_sha:
            return prompt_manifest.model_copy(update={"active_prompt_version": version})
    raise PromptSelectionUnauthoredError(selected_sha)
