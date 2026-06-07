from __future__ import annotations

import importlib
from typing import ClassVar

from tools.r421_e2b_live_probe import LiveProbeError, _load_sandbox_class, run_probe


class _Result:
    stdout = "r421-e2b-ok"


class _Commands:
    calls: ClassVar[list[tuple[str, int]]] = []

    def run(self, command: str, *, timeout: int) -> _Result:
        self.calls.append((command, timeout))
        return _Result()


class _Sandbox:
    create_kwargs: ClassVar[dict[str, object]] = {}

    def __init__(self) -> None:
        self.commands = _Commands()

    @classmethod
    def create(cls, **kwargs: object) -> _Sandbox:
        cls.create_kwargs = kwargs
        return cls()

    def __enter__(self) -> _Sandbox:
        return self

    def __exit__(self, *_exc: object) -> None:
        return None


def test_run_probe_disables_internet_and_tags_roadmap_item() -> None:
    stdout = run_probe(
        sandbox_cls=_Sandbox,
        command="printf r421-e2b-ok",
        sandbox_timeout_seconds=60,
        command_timeout_seconds=15,
    )

    assert stdout == "r421-e2b-ok"
    assert _Sandbox.create_kwargs == {
        "timeout": 60,
        "allow_internet_access": False,
        "metadata": {"roadmap_item": "R-421-managed-cloud-deployment-e2e"},
    }


def test_load_sandbox_class_fails_when_sdk_missing(monkeypatch) -> None:
    def missing(_name: str):
        raise ImportError("missing")

    monkeypatch.setattr(importlib, "import_module", missing)

    try:
        _load_sandbox_class()
    except LiveProbeError as exc:
        assert "Python module 'e2b' is not importable" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("expected LiveProbeError")
