"""Runtime v1.135 Codex read boundary: the real Landlock exec launcher, in disposable children.

Every case runs the REAL launcher in a fresh child process, never in pytest itself. The
target the launcher verifies and executes is this test interpreter, pinned by SHA-256; its
own install prefix and system libraries are TEST-ONLY read allowances so it can start
(production allows only the pinned Codex binary). Unrelated "operator" files live in a
simulated HOME inside `tmp_path`; the target reports only errno values, never contents.

Source canaries on this host's Landlock, not installed Codex acceptance.
"""

from __future__ import annotations

import dataclasses
import errno
import hashlib
import json
import os
import shutil
import socket
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

import pytest
from harness_runtime.lifecycle import cli_read_boundary as boundary

INTERPRETER = Path(os.path.realpath(sys.executable))
# The target interpreter's runtime needs (test-only): its install prefix, the system
# loader/libc directory and the loader cache. None contains a canary.
TEST_RUNTIME_READ_ONLY = (str(Path(sys.base_prefix).resolve()), "/usr/lib", "/etc/ld.so.cache")
# The test interpreter is dynamically linked: the kernel must EXECUTE its ELF loader.
TEST_RUNTIME_EXECUTABLE = (
    (os.path.realpath("/lib/ld-linux-aarch64.so.1"),)
    if os.path.exists("/lib/ld-linux-aarch64.so.1")
    else (os.path.realpath("/lib64/ld-linux-x86-64.so.2"),)
)

PROBE = r"""
import errno, json, os, socket, sys
targets = json.loads(sys.argv[1])
out = {}
def attempt(name, fn):
    try:
        fn()
        out[name] = "ok"
    except OSError as exc:
        out[name] = errno.errorcode.get(exc.errno, str(exc.errno))
def opener(path):
    def go():
        os.close(os.open(path, os.O_RDONLY))
    return go
def writer(path):
    def go():
        with open(path, "w") as fh:
            fh.write("x")
        with open(path) as fh:
            fh.read()
    return go
for name, path in targets.get("read", {}).items():
    attempt(name, opener(path))
for name, path in targets.get("write", {}).items():
    attempt(name, writer(path))
for name, path in targets.get("unix", {}).items():
    def go(path=path):
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            s.connect(path if not path.startswith("@") else "\0" + path[1:])
        finally:
            s.close()
    attempt(name, go)
for name, fd in targets.get("fd", {}).items():
    attempt(name, lambda fd=fd: os.fstat(fd))
if "child" in targets:
    pid = os.fork()
    if pid == 0:
        try:
            os.close(os.open(targets["child"], os.O_RDONLY))
            os._exit(0)
        except OSError as exc:
            os._exit(exc.errno)
    _, status = os.waitpid(pid, 0)
    code = os.waitstatus_to_exitcode(status)
    out["descendant"] = "ok" if code == 0 else errno.errorcode.get(code, str(code))
print(json.dumps(out))
"""


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _layout(tmp_path: Path) -> dict[str, Path]:
    home = tmp_path / "operator-home"
    (home / ".codex").mkdir(parents=True)
    (home / "secret-notes.txt").write_text("operator data")
    (home / ".codex" / "history.jsonl").write_text("operator history")
    codex_home, scratch = tmp_path / "harness-codex-home", tmp_path / "scratch"
    for d in (codex_home, scratch):
        d.mkdir(mode=0o700)
    return {"home": home, "codex_home": codex_home, "scratch": scratch}


def _spec(
    paths: dict[str, Path],
    *,
    sha: str | None = None,
    executable: Path = INTERPRETER,
    extra=(),
    read_write: tuple[str, ...] | None = None,
) -> boundary.RulesetSpec:
    return boundary.build_ruleset_spec(
        executable=str(executable),
        executable_sha256=sha if sha is not None else _sha256(INTERPRETER),
        read_write_dirs=read_write or (str(paths["codex_home"]), str(paths["scratch"])),
        read_only_paths=(*TEST_RUNTIME_READ_ONLY, *extra),
        executable_paths=TEST_RUNTIME_EXECUTABLE,
        protected_roots=(str(paths["home"]),),
        sealed_roots=(str(paths["home"] / ".codex"),),
    )


def _launch(
    spec: boundary.RulesetSpec, targets: dict[str, Any], *, pass_fds: tuple[int, ...] = ()
) -> subprocess.CompletedProcess[str]:
    argv = boundary.launcher_argv(
        spec, (str(INTERPRETER), "-I", "-S", "-c", PROBE, json.dumps(targets))
    )
    return subprocess.run(
        argv,
        capture_output=True,
        text=True,
        timeout=60,
        env={"PATH": "/usr/bin:/bin", "LANG": "C.UTF-8"},
        pass_fds=pass_fds,
        check=False,
    )


def _probe(spec: boundary.RulesetSpec, targets: dict[str, Any], **kw: Any) -> dict[str, str]:
    result = _launch(spec, targets, **kw)
    assert result.returncode == 0, (result.returncode, result.stderr[-2000:])
    return json.loads(result.stdout.strip().splitlines()[-1])


def test_unrelated_operator_files_are_denied_and_owned_dirs_are_usable(tmp_path: Path) -> None:
    paths = _layout(tmp_path)
    seen = _probe(
        _spec(paths),
        {
            "read": {
                "home_file": str(paths["home"] / "secret-notes.txt"),
                "codex_history": str(paths["home"] / ".codex" / "history.jsonl"),
                "proc_root_escape": f"/proc/self/root{paths['home'] / 'secret-notes.txt'}",
                "parent_environ": f"/proc/{os.getpid()}/environ",
                "etc_passwd": "/etc/passwd",
            },
            "write": {
                "harness_home": str(paths["codex_home"] / "probe.txt"),
                "scratch": str(paths["scratch"] / "probe.txt"),
                "operator_home_write": str(paths["home"] / "planted.txt"),
            },
        },
    )

    assert seen == {
        "home_file": "EACCES",
        "codex_history": "EACCES",
        "proc_root_escape": "EACCES",
        "parent_environ": "EACCES",
        "etc_passwd": "EACCES",
        "harness_home": "ok",
        "scratch": "ok",
        "operator_home_write": "EACCES",
    }
    assert not (paths["home"] / "planted.txt").exists()


def test_a_descendant_inherits_the_boundary(tmp_path: Path) -> None:
    paths = _layout(tmp_path)
    seen = _probe(_spec(paths), {"child": str(paths["home"] / "secret-notes.txt")})
    assert seen == {"descendant": "EACCES"}


def test_an_inherited_descriptor_is_closed_before_the_target_runs(tmp_path: Path) -> None:
    paths = _layout(tmp_path)
    fd = os.open(paths["home"] / "secret-notes.txt", os.O_RDONLY)
    try:
        seen = _probe(_spec(paths), {"fd": {"inherited": fd}}, pass_fds=(fd,))
    finally:
        os.close(fd)
    assert seen == {"inherited": "EBADF"}


def test_unix_sockets_created_outside_the_domain_are_unreachable(tmp_path: Path) -> None:
    paths = _layout(tmp_path)
    # AF_UNIX paths are limited to 108 bytes: a short OWNED directory under TMPDIR serves
    # as the allowed harness home here, removed afterwards.
    short = Path(tempfile.mkdtemp(prefix="a5s-", dir=os.environ.get("TMPDIR")))
    paths["codex_home"] = short
    pathname = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    abstract = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    name = f"arhugula-canary-{os.getpid()}-{os.urandom(4).hex()}"
    sock_path = paths["codex_home"] / "agent.sock"  # inside an ALLOWED dir: still denied
    try:
        pathname.bind(str(sock_path))
        pathname.listen(1)
        abstract.bind("\0" + name)
        abstract.listen(1)
        seen = _probe(_spec(paths), {"unix": {"pathname": str(sock_path), "abstract": "@" + name}})
    finally:
        pathname.close()
        abstract.close()
        shutil.rmtree(short)
    assert seen == {"pathname": "EACCES", "abstract": "EPERM"}


def _refusal(result: subprocess.CompletedProcess[str]) -> str:
    assert result.returncode == boundary.REFUSAL_EXIT, (result.returncode, result.stderr)
    [line] = [ln for ln in result.stderr.splitlines() if ln.startswith(boundary.REFUSAL_MARKER)]
    assert result.stdout == "", "the target must never have run"
    return line


def test_a_pin_mismatch_is_refused_before_the_target_runs(tmp_path: Path) -> None:
    paths = _layout(tmp_path)
    assert "sha256" in _refusal(_launch(_spec(paths, sha="0" * 64), {}))


def test_a_symlinked_or_missing_executable_is_refused(tmp_path: Path) -> None:
    paths = _layout(tmp_path)
    link = tmp_path / "codex-latest"
    link.symlink_to(INTERPRETER)
    assert "executable" in _refusal(_launch(_spec(paths, executable=link), {}))
    missing = tmp_path / "absent-codex"
    assert "executable" in _refusal(_launch(_spec(paths, executable=missing), {}))


def test_a_missing_allowed_path_is_refused(tmp_path: Path) -> None:
    paths = _layout(tmp_path)
    assert "path" in _refusal(_launch(_spec(paths, extra=(str(tmp_path / "nope"),)), {}))


def test_a_directory_executable_allowance_is_refused_at_launch(tmp_path: Path) -> None:
    """An `executable_paths` entry must be a regular file: a directory would grant execute
    beneath it, so the launcher refuses before the target runs."""
    paths = _layout(tmp_path)
    tools = tmp_path / "tools"
    tools.mkdir()
    spec = dataclasses.replace(
        _spec(paths), executable_paths=(*TEST_RUNTIME_EXECUTABLE, str(tools))
    )
    assert "executable allowance is not a regular file" in _refusal(_launch(spec, {}))


@pytest.mark.parametrize(
    "outcome",
    [-errno.ENOSYS, -errno.EOPNOTSUPP, -errno.EINVAL, 0, 5, 8],
    ids=["ENOSYS", "EOPNOTSUPP", "EINVAL", "abi0", "abi5", "abi8"],
)
def test_an_unsupported_host_is_refused(outcome: int) -> None:
    with pytest.raises(boundary.LauncherRefusalError, match="Landlock"):
        boundary.require_supported_abi(lambda: outcome)


def test_the_supported_host_handles_the_full_filesystem_mask() -> None:
    assert boundary.require_supported_abi(lambda: 10) == 10
    assert boundary.handled_access_fs(10) == (1 << 17) - 1


@pytest.mark.parametrize("broad", ["/", "/usr", "/home", "HOME", "HOME_PARENT"])
def test_a_broad_allowance_is_refused_at_launch(tmp_path: Path, broad: str) -> None:
    paths = _layout(tmp_path)
    target = {"HOME": str(paths["home"]), "HOME_PARENT": str(tmp_path)}.get(broad, broad)
    assert "exposes" in _refusal(_launch(_spec(paths, extra=(target,)), {}))


def test_a_symlinked_allowance_cannot_reach_the_protected_home(tmp_path: Path) -> None:
    """Review P2-1: the check and the grant are the same opened object, not two strings."""
    paths = _layout(tmp_path)
    alias = tmp_path / "public-dns-alias"
    alias.symlink_to(paths["home"], target_is_directory=True)
    assert "canonical" in _refusal(_launch(_spec(paths, extra=(str(alias),)), {}))


def test_an_ancestor_symlink_on_an_allowance_is_refused(tmp_path: Path) -> None:
    paths = _layout(tmp_path)
    (tmp_path / "public").mkdir()
    (tmp_path / "public" / "hosts").write_text("fixture")
    ancestor = tmp_path / "via-link"
    ancestor.symlink_to(tmp_path / "public", target_is_directory=True)
    assert "canonical" in _refusal(_launch(_spec(paths, extra=(str(ancestor / "hosts"),)), {}))


@pytest.mark.parametrize("where", ["residence", "inside"])
def test_the_interactive_codex_residence_is_never_granted(tmp_path: Path, where: str) -> None:
    """Review P2-2: the operator's own ``~/.codex`` (or anything in it) is not dedicated."""
    paths = _layout(tmp_path)
    residence = paths["home"] / ".codex"
    granted = residence if where == "residence" else residence / "harness"
    granted.mkdir(mode=0o700, exist_ok=True)
    spec = _spec(paths, read_write=(str(granted), str(paths["scratch"])))
    assert "sealed" in _refusal(_launch(spec, {}))


def test_a_descriptor_above_a_lowered_soft_limit_is_closed(tmp_path: Path) -> None:
    """Review P2-3: closure is independent of RLIMIT_NOFILE, not ``[3, SC_OPEN_MAX)``."""
    paths = _layout(tmp_path)
    argv = boundary.launcher_argv(
        _spec(paths), (str(INTERPRETER), "-I", "-S", "-c", PROBE, json.dumps({"fd": {"high": 256}}))
    )
    driver = (
        "import fcntl, json, os, resource, sys\n"
        "fd = os.open(sys.argv[1], os.O_RDONLY)\n"
        "assert fcntl.fcntl(fd, fcntl.F_DUPFD, 256) == 256\n"
        "os.close(fd); os.set_inheritable(256, True)\n"
        "resource.setrlimit(resource.RLIMIT_NOFILE, (64, resource.getrlimit(resource.RLIMIT_NOFILE)[1]))\n"
        "argv = json.loads(sys.argv[2]); os.execve(argv[0], argv, {'PATH': '/usr/bin:/bin'})\n"
    )
    result = subprocess.run(
        (
            str(INTERPRETER),
            "-I",
            "-S",
            "-c",
            driver,
            str(paths["home"] / "secret-notes.txt"),
            json.dumps(argv),
        ),
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    assert result.returncode == 0, result.stderr[-2000:]
    assert json.loads(result.stdout.strip().splitlines()[-1]) == {"high": "EBADF"}
