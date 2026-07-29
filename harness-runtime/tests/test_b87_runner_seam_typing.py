"""B-87 codex R6 [P2] — the public ``runner=`` seam is a STATIC two-shape seam.

`_run_with_wire_boundary` gives a pre-B-87 runner RUNTIME compatibility (it
withholds the ``on_wire`` keyword from a runner that never declared it). This
module is the matching STATIC witness: a typed legacy runner and a typed
wire-aware runner must BOTH be assignable to the exported
`ExternalCLISubprocessRunner` — the type every public
``construct_*_cli_adapter(runner=...)`` parameter and every adapter ``runner``
field is annotated with.

The witness is pyright, not pytest: the assignments below are checked by
`just typecheck` / `just check`, and the runtime assertions merely keep the
module honest (the classes really do behave as their annotations claim) and
give the file a reason to exist in the test lane.

Diagnostic-rule note: the declared-variable assignments are `reportAssignmentType`,
which — unlike `reportArgumentType` / `reportCallIssue` — is NOT relaxed for
`harness-runtime/tests` at the root `[tool.pyright]` executionEnvironments. So a
regression that re-narrows the public seam to the wire-aware-only shape fails
the typecheck gate here rather than passing silently. Mutation-probed: narrowing
`ExternalCLISubprocessRunner.run` back to the ``on_wire``-bearing signature makes
pyright report exactly one error, at `_LEGACY_SEAM`.
"""

from __future__ import annotations

import asyncio
from collections.abc import Callable

from harness_runtime.lifecycle.external_cli_provider import (
    AsyncioSubprocessRunner,
    CLIProcessResult,
    ExternalCLISubprocessRunner,
    RecordingSubprocessRunner,
    WireAwareExternalCLISubprocessRunner,
    accepts_explicit_on_wire,
)


class _TypedLegacyRunner:
    """A downstream runner written against the documented pre-B-87 seam."""

    async def run(
        self,
        argv: tuple[str, ...],
        *,
        stdin: str,
        timeout_seconds: float,
    ) -> CLIProcessResult:
        del argv, stdin, timeout_seconds
        return CLIProcessResult(exit_code=0, stdout="legacy", stderr="")


class _TypedWireAwareRunner:
    """A downstream runner that opts in to the B-87 wire notification."""

    async def run(
        self,
        argv: tuple[str, ...],
        *,
        stdin: str,
        timeout_seconds: float,
        on_wire: Callable[[], None] | None = None,
    ) -> CLIProcessResult:
        del argv, stdin, timeout_seconds
        if on_wire is not None:
            on_wire()
        return CLIProcessResult(exit_code=0, stdout="wire-aware", stderr="")


# THE STATIC WITNESS. Both shapes must satisfy the public seam type.
_LEGACY_SEAM: ExternalCLISubprocessRunner = _TypedLegacyRunner()
_WIRE_AWARE_SEAM: ExternalCLISubprocessRunner = _TypedWireAwareRunner()

# The wire-aware shape additionally satisfies the narrower opt-in Protocol,
# which is what `_run_with_wire_boundary` narrows to after its runtime check.
_WIRE_AWARE_NARROW: WireAwareExternalCLISubprocessRunner = _TypedWireAwareRunner()

# The two shipped runners stay wire-aware (full-precision tier).
_SHIPPED_PRODUCTION: WireAwareExternalCLISubprocessRunner = AsyncioSubprocessRunner()
_SHIPPED_RECORDING: WireAwareExternalCLISubprocessRunner = RecordingSubprocessRunner(())


def test_public_seam_admits_both_runner_shapes_at_runtime_too() -> None:
    """The static witness above is matched by the runtime capability verdict."""
    assert accepts_explicit_on_wire(_LEGACY_SEAM.run) is False
    assert accepts_explicit_on_wire(_WIRE_AWARE_SEAM.run) is True
    assert accepts_explicit_on_wire(_SHIPPED_PRODUCTION.run) is True
    assert accepts_explicit_on_wire(_SHIPPED_RECORDING.run) is True


def test_seam_typed_runners_actually_run() -> None:
    """The annotations are not decorative — both shapes execute through the seam."""
    fired: list[str] = []

    legacy = asyncio.run(_LEGACY_SEAM.run((), stdin="", timeout_seconds=1.0))
    assert legacy.stdout == "legacy"

    wire_aware = asyncio.run(
        _TypedWireAwareRunner().run(
            (),
            stdin="",
            timeout_seconds=1.0,
            on_wire=lambda: fired.append("wire"),
        )
    )
    assert wire_aware.stdout == "wire-aware"
    assert fired == ["wire"]
