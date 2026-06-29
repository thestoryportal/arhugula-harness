from __future__ import annotations

import zipfile
from pathlib import Path

from tools.q4_packaging_gate import (
    REQUIREMENTS_LOCK,
    RUNTIME_ENTRY_POINTS,
    WORKSPACE_PACKAGES,
    validate,
)


def _write_wheel(dist: Path, package_name: str, *, entry_points: str = "") -> None:
    canonical = package_name.replace("-", "_")
    dist_info = f"{canonical}-0.0.0.dist-info"
    wheel_path = dist / f"{canonical}-0.0.0-py3-none-any.whl"
    with zipfile.ZipFile(wheel_path, "w") as wheel:
        wheel.writestr(f"{dist_info}/METADATA", f"Name: {package_name}\nVersion: 0.0.0\n")
        wheel.writestr(
            f"{dist_info}/WHEEL",
            "Wheel-Version: 1.0\nGenerator: test\nRoot-Is-Purelib: true\nTag: py3-none-any\n",
        )
        if entry_points:
            wheel.writestr(f"{dist_info}/entry_points.txt", entry_points)


def _runtime_entry_points(*, include_harness: bool = True) -> str:
    lines = ["[console_scripts]"]
    for script, target in RUNTIME_ENTRY_POINTS.items():
        if script == "harness" and not include_harness:
            continue
        lines.append(f"{script} = {target}")
    return "\n".join(lines)


def _write_dist(tmp_path: Path, *, include_harness_entry_point: bool = True) -> Path:
    dist = tmp_path / "dist"
    dist.mkdir()
    for package_name in WORKSPACE_PACKAGES:
        entry_points = (
            _runtime_entry_points(include_harness=include_harness_entry_point)
            if package_name == "harness-runtime"
            else ""
        )
        _write_wheel(dist, package_name, entry_points=entry_points)
    (dist / REQUIREMENTS_LOCK).write_text(
        "pydantic==2.11.0 \\\n"
        "    --hash=sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\n",
        encoding="utf-8",
    )
    return dist


def test_q4_packaging_gate_accepts_complete_dist(tmp_path: Path) -> None:
    report = validate(Path.cwd(), _write_dist(tmp_path))

    assert report.ready is True
    assert {check.name for check in report.checks if not check.ok} == set()


def test_q4_packaging_gate_rejects_missing_workspace_wheel(tmp_path: Path) -> None:
    dist = _write_dist(tmp_path)
    (dist / "harness_cp-0.0.0-py3-none-any.whl").unlink()

    report = validate(Path.cwd(), dist)

    failed = {check.name: check.detail for check in report.checks if not check.ok}
    assert report.ready is False
    assert "wheel-artifacts" in failed
    assert "harness-cp" in failed["wheel-artifacts"]


def test_q4_packaging_gate_rejects_runtime_wheel_without_harness_cli(
    tmp_path: Path,
) -> None:
    report = validate(Path.cwd(), _write_dist(tmp_path, include_harness_entry_point=False))

    failed = {check.name: check.detail for check in report.checks if not check.ok}
    assert report.ready is False
    assert "runtime-entry-points" in failed
    assert "harness=" in failed["runtime-entry-points"]


def test_q4_packaging_gate_rejects_unhashed_requirements_lock(tmp_path: Path) -> None:
    dist = _write_dist(tmp_path)
    (dist / REQUIREMENTS_LOCK).write_text("pydantic==2.11.0\n", encoding="utf-8")

    report = validate(Path.cwd(), dist)

    failed = {check.name: check.detail for check in report.checks if not check.ok}
    assert report.ready is False
    assert "requirements-lock" in failed
    assert "sha256" in failed["requirements-lock"]
