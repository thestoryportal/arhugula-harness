#!/usr/bin/env python3
"""Live E2B hosted-sandbox probe for the R-421 managed-cloud candidate.

This command is intentionally not part of CI. It creates a short-lived E2B
cloud sandbox, runs one deterministic shell command, and tears the sandbox down
through the SDK context manager. It performs no LLM/provider inference.
"""

from __future__ import annotations

import argparse
import importlib
import os
import sys
from collections.abc import Sequence
from typing import Any


class LiveProbeError(RuntimeError):
    """Raised for a failed R-421 E2B live probe."""


def _print_step(message: str) -> None:
    print(f"[r421-e2b-live] {message}", flush=True)


def _load_sandbox_class() -> Any:
    try:
        module = importlib.import_module("e2b")
    except ImportError as exc:
        raise LiveProbeError(
            "Python module 'e2b' is not importable; install it explicitly for "
            "the live probe, e.g. `uv run --with e2b python tools/r421_e2b_live_probe.py`"
        ) from exc
    sandbox_cls = getattr(module, "Sandbox", None)
    if sandbox_cls is None:
        raise LiveProbeError("Python module 'e2b' does not expose Sandbox")
    return sandbox_cls


def _result_stdout(result: Any) -> str:
    stdout = getattr(result, "stdout", None)
    if not isinstance(stdout, str):
        raise LiveProbeError("E2B command result did not expose string stdout")
    return stdout


def run_probe(
    *,
    sandbox_cls: Any,
    command: str,
    sandbox_timeout_seconds: int,
    command_timeout_seconds: int,
) -> str:
    """Create an E2B sandbox, run the command, and return stdout."""
    with sandbox_cls.create(
        timeout=sandbox_timeout_seconds,
        allow_internet_access=False,
        metadata={"roadmap_item": "R-421-managed-cloud-deployment-e2e"},
    ) as sandbox:
        result = sandbox.commands.run(command, timeout=command_timeout_seconds)
    return _result_stdout(result)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--command",
        default="printf r421-e2b-ok",
        help="Deterministic command to run inside the E2B sandbox.",
    )
    parser.add_argument("--sandbox-timeout", type=int, default=60)
    parser.add_argument("--command-timeout", type=int, default=15)
    args = parser.parse_args(argv)

    if not os.environ.get("E2B_API_KEY"):
        print("R-421 E2B live probe failed: E2B_API_KEY is not set", file=sys.stderr)
        return 1

    try:
        sandbox_cls = _load_sandbox_class()
        _print_step("creating hosted E2B sandbox and running deterministic command")
        stdout = run_probe(
            sandbox_cls=sandbox_cls,
            command=args.command,
            sandbox_timeout_seconds=args.sandbox_timeout,
            command_timeout_seconds=args.command_timeout,
        )
    except LiveProbeError as exc:
        print(f"R-421 E2B live probe failed: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:  # pragma: no cover - provider SDK/runtime boundary
        print(f"R-421 E2B live probe failed: {exc}", file=sys.stderr)
        return 1

    if stdout != "r421-e2b-ok":
        print(
            f"R-421 E2B live probe failed: unexpected stdout {stdout!r}; expected 'r421-e2b-ok'",
            file=sys.stderr,
        )
        return 1

    _print_step("completed: stdout=r421-e2b-ok hosted-provider-calls=1 cost=usage-billed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
