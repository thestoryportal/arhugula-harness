"""Tests for sandbox host readiness probes."""

from __future__ import annotations

import importlib.util
import os
import stat
import sys
from pathlib import Path

import pytest


def _load_module():
    path = Path(__file__).parent / "sandbox_host_readiness.py"
    spec = importlib.util.spec_from_file_location("sandbox_host_readiness", path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _char_device_stat():
    return os.stat_result((stat.S_IFCHR, 0, 0, 0, 0, 0, 0, 0, 0, 0))


def test_firecracker_alias_maps_to_r412_and_requires_linux_kvm_binary():
    readiness = _load_module()
    probe = readiness.HostProbe(
        system=lambda: "Linux",
        machine=lambda: "x86_64",
        which=lambda name: f"/usr/local/bin/{name}",
        exists=lambda _path: True,
        access=lambda _path, _mode: True,
        stat_path=lambda _path: _char_device_stat(),
    )

    report = readiness.check_provider("firecracker", probe=probe)

    assert report.ready is True
    assert report.provider == "r412-firecracker"
    assert report.roadmap_item == "R-412-sandbox-tier-4-full-vm-execution"
    assert report.source_url == "https://github.com/firecracker-microvm/firecracker"


def test_firecracker_fails_cleanly_on_macos_without_kvm():
    readiness = _load_module()
    probe = readiness.HostProbe(
        system=lambda: "Darwin",
        machine=lambda: "x86_64",
        which=lambda _name: None,
        exists=lambda _path: False,
    )

    report = readiness.check_provider("r412-firecracker", probe=probe)

    failed = {check.name for check in report.checks if not check.ok}
    assert report.ready is False
    assert "host-mode" in failed
    assert "binary:firecracker" in failed
    assert "kvm-device-present" in failed


def test_gvisor_probe_does_not_require_kvm():
    readiness = _load_module()
    probe = readiness.HostProbe(
        system=lambda: "Linux",
        machine=lambda: "aarch64",
        which=lambda name: f"/usr/bin/{name}",
        exists=lambda _path: False,
    )

    report = readiness.check_provider("r411-gvisor", probe=probe)

    assert report.ready is True
    assert report.roadmap_item == "R-411-sandbox-tier-3-microvm-execution"
    assert report.source_url == "https://github.com/google/gvisor"
    assert "kvm-device-present" not in {check.name for check in report.checks}


def test_kata_probe_requires_kvm_access():
    readiness = _load_module()
    probe = readiness.HostProbe(
        system=lambda: "Linux",
        machine=lambda: "x86_64",
        which=lambda name: f"/usr/bin/{name}",
        exists=lambda _path: True,
        access=lambda _path, _mode: False,
        stat_path=lambda _path: _char_device_stat(),
    )

    report = readiness.check_provider("r411-kata", probe=probe)

    failed = {check.name for check in report.checks if not check.ok}
    assert report.ready is False
    assert failed == {"kvm-device-access"}


def test_e2b_probe_is_managed_cloud_and_requires_key_and_sdk():
    readiness = _load_module()
    probe = readiness.HostProbe(
        env_present=lambda _name: False,
        find_module=lambda _name: None,
    )

    report = readiness.check_provider("e2b", probe=probe)

    failed = {check.name for check in report.checks if not check.ok}
    assert report.ready is False
    assert report.provider == "r421-e2b"
    assert report.roadmap_item == "R-421-managed-cloud-deployment-e2e"
    assert report.source_url == "https://github.com/e2b-dev/e2b"
    assert failed == {"env:E2B_API_KEY", "python-module:e2b"}


def test_shuru_requires_apple_silicon_on_macos():
    readiness = _load_module()
    probe = readiness.HostProbe(
        system=lambda: "Darwin",
        machine=lambda: "x86_64",
        which=lambda name: f"/opt/homebrew/bin/{name}",
    )

    report = readiness.check_provider("shuru", probe=probe)

    failed = {check.name for check in report.checks if not check.ok}
    assert report.ready is False
    assert report.provider == "r411-shuru"
    assert failed == {"host-mode"}


def test_microsandbox_allows_macos_apple_silicon_without_kvm():
    readiness = _load_module()
    probe = readiness.HostProbe(
        system=lambda: "Darwin",
        machine=lambda: "arm64",
        which=lambda name: f"/opt/homebrew/bin/{name}",
        exists=lambda _path: False,
    )

    report = readiness.check_provider("microsandbox", probe=probe)

    assert report.ready is True
    assert report.provider == "r411-microsandbox"
    assert report.source_url == "https://github.com/superradcompany/microsandbox"


def test_libkrun_allows_macos_apple_silicon_hvf_with_library():
    readiness = _load_module()
    probe = readiness.HostProbe(
        system=lambda: "Darwin",
        machine=lambda: "arm64",
        find_library=lambda name: f"lib{name}.dylib",
        exists=lambda _path: False,
    )

    report = readiness.check_provider("libkrun", probe=probe)

    assert report.ready is True
    assert report.provider == "r411-libkrun"
    assert report.roadmap_item == "R-411-sandbox-tier-3-microvm-execution"
    assert report.source_url == "https://github.com/containers/libkrun"
    assert "kvm-device-present" not in {check.name for check in report.checks}


def test_qemu_microvm_alias_maps_to_r412_and_requires_linux_kvm_binary():
    readiness = _load_module()
    probe = readiness.HostProbe(
        system=lambda: "Linux",
        machine=lambda: "x86_64",
        which=lambda name: f"/usr/bin/{name}",
        exists=lambda _path: True,
        access=lambda _path, _mode: True,
        stat_path=lambda _path: _char_device_stat(),
    )

    report = readiness.check_provider("qemu-microvm", probe=probe)

    assert report.ready is True
    assert report.provider == "r412-qemu-microvm"
    assert report.roadmap_item == "R-412-sandbox-tier-4-full-vm-execution"
    assert (
        report.source_url
        == "https://github.com/bonzini/qemu/blob/master/docs/system/i386/microvm.rst"
    )


def test_mvm_is_not_registered_as_an_isolation_provider():
    readiness = _load_module()

    with pytest.raises(ValueError, match="unknown provider"):
        readiness.check_provider("mvm")
