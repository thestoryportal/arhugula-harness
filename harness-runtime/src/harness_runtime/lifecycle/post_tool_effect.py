"""The post-tool-effect terminal carrier (Runtime v1.134 C-RT-38 §14.27 retry fence).

A model tool-loop dispatch that fails AFTER one of its tool effects started must not be
replayed: re-running the dispatch re-asks the model, which can emit the same call under a
new id and run the effect again. Every failure past that point surfaces once as this
carrier, with the original failure chained as ``__cause__``. The C-RT-16 retry wrapper
never retries it and never advances to another candidate.

Replay safety and provider health are separate facts. The carrier also records WHERE the
failure arose, decided structurally by the boundary that observed it (a provider call and
the parsing of that provider's own reply, or anything else: tool host, memory validation
or executor, turn capture, bookkeeping), never by how the
error looks. Only a provider-origin failure is a provider fault for breaker accounting.

Not an audit-signing failure and not a HITL gate decision, so it subclasses neither
family.
"""

from __future__ import annotations

from collections.abc import Generator
from contextlib import contextmanager
from dataclasses import dataclass
from enum import StrEnum

from harness_od.audit_signing_errors import AUDIT_SIGNING_HARD_FAILURES

__all__ = ["PostToolEffectError", "ToolEffectFailureOrigin", "ToolEffectFence"]


class ToolEffectFailureOrigin(StrEnum):
    """Which boundary observed a post-effect failure."""

    PROVIDER = "provider"
    """The model provider call, or parsing that provider's own reply, failed: a provider
    fault (C-RT-16 charges it; §14.6.3 row 2b)."""
    NON_PROVIDER = "non-provider"
    """Tool host, memory validation or executor, turn capture or harness bookkeeping:
    never a provider fault, whatever the error resembles."""


class PostToolEffectError(RuntimeError):
    """A tool-loop dispatch failed after a tool effect started; it must not be replayed."""

    def __init__(self, fault: Exception, *, origin: ToolEffectFailureOrigin) -> None:
        super().__init__(f"tool-loop dispatch failed after a tool effect started: {fault!r}")
        self.fault = fault
        """The failure itself (also the chained `__cause__`)."""
        self.origin = origin


@dataclass(slots=True)
class ToolEffectFence:
    """Whether any tool effect of ONE retried dispatch attempt has started.

    Owned by the dispatch attempt that the C-RT-16 wrapper retries and handed explicitly
    to every tool-loop arm, so its guard covers the whole attempt, including post-tool
    bookkeeping such as turn capture. An effect has started once its executor was
    entered, whatever it then returned or raised: an executor that raised may still have
    acted, so the outcome is ambiguous and is treated as started.
    """

    started: bool = False

    def record(self, *, started: bool) -> None:
        """Fold in an effect a caller observed completing (it never un-starts)."""
        self.started = self.started or started

    @contextmanager
    def entering_effect(self) -> Generator[None]:
        """Mark the effect started BEFORE the executor runs, then fence its failure."""
        self.started = True
        with self.guard():
            yield

    @contextmanager
    def provider_call(self) -> Generator[None]:
        """Fence one model-provider call and the parsing of its reply: a failure there past
        an effect is a provider fault. Tool, memory and capture work never belongs inside."""
        with self.guard(origin=ToolEffectFailureOrigin.PROVIDER):
            yield

    @contextmanager
    def guard(
        self, *, origin: ToolEffectFailureOrigin = ToolEffectFailureOrigin.NON_PROVIDER
    ) -> Generator[None]:
        """Re-raise a failure past a started effect as `PostToolEffectError`.

        Before any effect the failure passes through unchanged, so today's retry and
        fallback classification still applies. `BaseException` signals (cancellation, a
        tripped dispatch fence, a pause request), the audit-signing hard failures and an
        already-fenced carrier (whose origin was decided closer to its source) keep their
        own identity and are never re-wrapped.
        """
        try:
            yield
        except (PostToolEffectError, *AUDIT_SIGNING_HARD_FAILURES):
            raise
        except Exception as exc:
            if not self.started:
                raise
            raise PostToolEffectError(exc, origin=origin) from exc
