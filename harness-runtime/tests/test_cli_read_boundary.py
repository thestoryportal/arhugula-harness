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
import platform
import re
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
REFUSAL_TOKEN = boundary.new_refusal_token()
# The target interpreter's runtime needs (test-only): its install prefix, the system
# loader/libc directory and the loader cache. None contains a canary.
TEST_RUNTIME_READ_ONLY = (str(Path(sys.base_prefix).resolve()), "/usr/lib", "/etc/ld.so.cache")
# The test interpreter is dynamically linked: the kernel must EXECUTE its ELF loader.
TEST_RUNTIME_EXECUTABLE = (
    (os.path.realpath("/lib/ld-linux-aarch64.so.1"),)
    if os.path.exists("/lib/ld-linux-aarch64.so.1")
    else (os.path.realpath("/lib64/ld-linux-x86-64.so.2"),)
)


def _host_refusal() -> str | None:
    """Why the launcher refuses THIS host (its own step-2 check), or None if it is supported."""
    try:
        boundary.require_supported_abi(platform.machine(), boundary._query_abi)
    except boundary.LauncherRefusalError as refusal:
        return str(refusal)
    return None


HOST_REFUSAL = _host_refusal()
# [LAW:single-enforcer] the launcher's own host check decides which canaries can run here.
# A canary that needs the kernel to enforce (or to pass step 2) is HELD, unproved, on a host
# the launcher refuses; that host instead runs the real-refusal tests marked UNSUPPORTED_HOST.
SUPPORTED_HOST = pytest.mark.skipif(
    HOST_REFUSAL is not None,
    reason=f"HELD (unproved here): needs kernel Landlock ABI >= {boundary.MIN_ABI} on "
    f"aarch64/x86_64; the launcher refuses this host: {HOST_REFUSAL}",
)
UNSUPPORTED_HOST = pytest.mark.skipif(
    HOST_REFUSAL is None, reason="this host is supported: the SUPPORTED_HOST canaries run instead"
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
        refusal_token=REFUSAL_TOKEN,
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


@SUPPORTED_HOST
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


@SUPPORTED_HOST
def test_a_descendant_inherits_the_boundary(tmp_path: Path) -> None:
    paths = _layout(tmp_path)
    seen = _probe(_spec(paths), {"child": str(paths["home"] / "secret-notes.txt")})
    assert seen == {"descendant": "EACCES"}


@SUPPORTED_HOST
def test_an_inherited_descriptor_is_closed_before_the_target_runs(tmp_path: Path) -> None:
    paths = _layout(tmp_path)
    fd = os.open(paths["home"] / "secret-notes.txt", os.O_RDONLY)
    try:
        seen = _probe(_spec(paths), {"fd": {"inherited": fd}}, pass_fds=(fd,))
    finally:
        os.close(fd)
    assert seen == {"inherited": "EBADF"}


@SUPPORTED_HOST
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
    """The launcher's own reason: exit 125 and one marker line carrying this launch's token."""
    assert result.returncode == boundary.REFUSAL_EXIT, (result.returncode, result.stderr)
    [line] = [ln for ln in result.stderr.splitlines() if ln.startswith(boundary.REFUSAL_MARKER)]
    assert result.stdout == "", "the target must never have run"
    reason = boundary.refusal_reason(REFUSAL_TOKEN, result.returncode, result.stderr)
    assert reason is not None and line == f"{boundary.REFUSAL_MARKER} {REFUSAL_TOKEN} {reason}"
    return reason


def test_only_a_line_carrying_this_launchs_token_is_its_refusal() -> None:
    """The target inherits the launcher's stderr: the marker and exit 125 alone prove nothing."""
    marker, mine, other = boundary.REFUSAL_MARKER, REFUSAL_TOKEN, boundary.new_refusal_token()
    assert boundary.refusal_reason(mine, 125, f"noise\n{marker} {mine} pin mismatch\n") == (
        "pin mismatch"
    )
    for forged in (f"{marker} forged", f"{marker} {other} forged", f"x {marker} {mine} forged"):
        assert boundary.refusal_reason(mine, 125, forged) is None, forged
    assert boundary.refusal_reason(mine, 1, f"{marker} {mine} not a refusal exit") is None


@pytest.mark.parametrize("token", ["", "0" * 31, "0" * 33, "g" * 32, "A" * 32])
def test_a_malformed_refusal_token_is_rejected(token: str) -> None:
    assert _bare_spec().refusal_token == REFUSAL_TOKEN  # the well-formed control builds
    with pytest.raises(ValueError, match="refusal_token"):
        _bare_spec(token)


@pytest.mark.parametrize("spec_json", ["not json", "{}"])
def test_an_unparseable_invocation_refuses_without_a_token(spec_json: str) -> None:
    """No spec, no token: the launcher still refuses loudly, and nothing reads it as typed."""
    argv = boundary.launcher_argv(_bare_spec(), (str(INTERPRETER), "-c", "print('ran')"))
    at = argv.index(str(boundary.LAUNCHER_PATH)) + 1
    result = subprocess.run(
        (*argv[:at], spec_json, *argv[at + 1 :]),
        capture_output=True,
        text=True,
        timeout=60,
        env={"PATH": "/usr/bin:/bin", "LANG": "C.UTF-8"},
        check=False,
    )
    assert result.returncode == boundary.REFUSAL_EXIT and result.stdout == ""
    assert result.stderr.startswith(f"{boundary.REFUSAL_MARKER} unusable invocation:")
    assert boundary.refusal_reason(REFUSAL_TOKEN, result.returncode, result.stderr) is None


def _bare_spec(token: str = REFUSAL_TOKEN) -> boundary.RulesetSpec:
    return boundary.build_ruleset_spec(
        executable=str(INTERPRETER),
        executable_sha256=_sha256(INTERPRETER),
        read_write_dirs=(),
        read_only_paths=(),
        refusal_token=token,
    )


@SUPPORTED_HOST
def test_a_pin_mismatch_is_refused_before_the_target_runs(tmp_path: Path) -> None:
    paths = _layout(tmp_path)
    assert "sha256" in _refusal(_launch(_spec(paths, sha="0" * 64), {}))


@SUPPORTED_HOST
def test_a_symlinked_or_missing_executable_is_refused(tmp_path: Path) -> None:
    paths = _layout(tmp_path)
    link = tmp_path / "codex-latest"
    link.symlink_to(INTERPRETER)
    assert "executable" in _refusal(_launch(_spec(paths, executable=link), {}))
    missing = tmp_path / "absent-codex"
    assert "executable" in _refusal(_launch(_spec(paths, executable=missing), {}))


@SUPPORTED_HOST
def test_a_missing_allowed_path_is_refused(tmp_path: Path) -> None:
    paths = _layout(tmp_path)
    assert "path" in _refusal(_launch(_spec(paths, extra=(str(tmp_path / "nope"),)), {}))


@SUPPORTED_HOST
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


# Runs the launcher's real `main` in a disposable child with source-level injections:
# "machine" or "abi" replace the host report, "unhandled" removes rights from the
# handled mask (a control ruleset). `__main__` itself takes no such input.
ENTRY_DRIVER = r"""
import importlib.util, json, sys
spec = importlib.util.spec_from_file_location("read_boundary_launcher", sys.argv[1])
launcher = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = launcher
spec.loader.exec_module(launcher)
inject = json.loads(sys.argv[2])
kw = {}
if "machine" in inject:
    kw["machine"] = lambda: inject["machine"]
if "abi" in inject:
    kw["query_abi"] = lambda: inject["abi"]
if "unhandled" in inject:
    kw["handled"] = lambda abi: launcher.handled_access_fs(abi) & ~inject["unhandled"]
launcher.main(sys.argv[3:], **kw)
"""


def _launch_entry(
    spec: boundary.RulesetSpec, inject: dict[str, Any], probe: str, targets: Any
) -> subprocess.CompletedProcess[str]:
    real = boundary.launcher_argv(
        spec, (str(INTERPRETER), "-I", "-S", "-c", probe, json.dumps(targets))
    )
    at = real.index(str(boundary.LAUNCHER_PATH))  # the driver takes the launcher's place
    argv = (*real[:at], "-c", ENTRY_DRIVER, real[at], json.dumps(inject), *real[at + 1 :])
    return subprocess.run(
        argv,
        capture_output=True,
        text=True,
        timeout=60,
        env={"PATH": "/usr/bin:/bin", "LANG": "C.UTF-8"},
        check=False,
    )


@pytest.mark.parametrize(
    ("inject", "reason"),
    [
        ({"machine": "riscv64"}, "unverified on architecture 'riscv64'"),
        ({"abi": -errno.ENOSYS}, "Landlock unavailable: ENOSYS"),
        ({"abi": -errno.EOPNOTSUPP}, f"Landlock unavailable: {errno.errorcode[errno.EOPNOTSUPP]}"),
        ({"abi": -errno.EINVAL}, "Landlock unavailable: EINVAL"),
        ({"abi": 8}, "Landlock ABI 8 < required 9"),
    ],
    ids=["architecture", "ENOSYS", "EOPNOTSUPP", "EINVAL", "abi8"],
)
def test_an_unsupported_host_is_refused_by_the_launcher_entry_point(
    tmp_path: Path, inject: dict[str, Any], reason: str
) -> None:
    """Spec item 6.2 on the real entry path: exit 125, the marker, and no target run."""
    paths = _layout(tmp_path)
    assert reason in _refusal(_launch_entry(_spec(paths), inject, PROBE, {}))


@SUPPORTED_HOST
def test_the_entry_driver_runs_the_target_on_a_supported_report(tmp_path: Path) -> None:
    """Control for the refusals above: the same driver with a supported report runs."""
    paths = _layout(tmp_path)
    result = _launch_entry(_spec(paths), {"machine": "x86_64", "abi": 9}, PROBE, {})
    assert result.returncode == 0, result.stderr[-2000:]
    assert json.loads(result.stdout) == {}


def test_the_supported_host_handles_the_full_filesystem_mask() -> None:
    assert boundary.handled_access_fs(10) == (1 << 17) - 1


# Each operation below is one Landlock right's witness: [name, op, *args].
RIGHTS_PROBE = r"""
import errno, json, os, signal, stat, subprocess, sys, time
def signal_descendant():
    pid = os.fork()
    if pid == 0:
        time.sleep(60)
        os._exit(0)
    try:
        os.kill(pid, signal.SIGCONT)
    finally:
        os.kill(pid, signal.SIGKILL)
        os.waitpid(pid, 0)
def run(*argv):
    subprocess.run(argv, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                   stderr=subprocess.DEVNULL, check=False)
OPS = {
    "read": lambda p: os.close(os.open(p, os.O_RDONLY)),
    "write": lambda p: os.close(os.open(p, os.O_WRONLY)),
    "list": os.listdir,
    "rmdir": os.rmdir,
    "unlink": os.unlink,
    "mkdir": os.mkdir,
    "mkreg": lambda p: os.mknod(p, stat.S_IFREG | 0o600),
    "mkfifo": os.mkfifo,
    "symlink": lambda p: os.symlink("/dev/null", p),
    "link": os.link,
    "rename": os.rename,
    "truncate": lambda p: os.truncate(p, 0),
    "exec": run,
    "mkchr": lambda p: os.mknod(p, stat.S_IFCHR | 0o600, os.makedev(1, 3)),
    "mkblk": lambda p: os.mknod(p, stat.S_IFBLK | 0o600, os.makedev(7, 0)),
    "signal": lambda pid: os.kill(pid, signal.SIGCONT),
    "signal_descendant": signal_descendant,
}
out = {}
for name, op, *args in json.loads(sys.argv[1]):
    try:
        OPS[op](*args)
        out[name] = "ok"
    except OSError as exc:
        out[name] = errno.errorcode.get(exc.errno, str(exc.errno))
print(json.dumps(out))
"""


def _rights_probe(
    spec: boundary.RulesetSpec, ops: list[list[Any]], inject: dict[str, Any] | None = None
) -> dict[str, str]:
    if inject is None:
        argv = boundary.launcher_argv(
            spec, (str(INTERPRETER), "-I", "-S", "-c", RIGHTS_PROBE, json.dumps(ops))
        )
        result = subprocess.run(
            argv,
            capture_output=True,
            text=True,
            timeout=60,
            env={"PATH": "/usr/bin:/bin", "LANG": "C.UTF-8"},
            check=False,
        )
    else:
        result = _launch_entry(spec, inject, RIGHTS_PROBE, ops)
    assert result.returncode == 0, (result.returncode, result.stderr[-2000:])
    return json.loads(result.stdout.strip().splitlines()[-1])


@SUPPORTED_HOST
def test_a_confined_child_cannot_signal_outside_its_domain(tmp_path: Path) -> None:
    """Item 6.4, the SIGNAL scope: an unconfined same-user sibling is out of reach (EPERM)
    while the child's own confined descendant is not."""
    paths = _layout(tmp_path)
    sibling = subprocess.Popen((str(INTERPRETER), "-I", "-S", "-c", "import time; time.sleep(60)"))
    try:
        seen = _rights_probe(
            _spec(paths),
            [["sibling", "signal", sibling.pid], ["descendant", "signal_descendant"]],
        )
    finally:
        sibling.kill()
        sibling.wait()
    assert seen == {"sibling": "EPERM", "descendant": "ok"}


def _rights_layout(tmp_path: Path) -> tuple[dict[str, Path], Path]:
    paths = _layout(tmp_path)
    public = tmp_path / "public"  # a read-only grant on the same filesystem as scratch
    public.mkdir()
    (public / "shared.txt").write_text("public")
    home, scratch, codex_home = paths["home"], paths["scratch"], paths["codex_home"]
    for root in (home, scratch, codex_home):
        for name in ("file.txt", "doomed.txt", "trunc.txt", "moved.txt"):
            (root / name).write_text("fixture")
        (root / "emptydir").mkdir()
    # Exec opens for read too, so the EXECUTE witness sits in the read-only grant: readable,
    # never executable.
    tool = public / "tool"
    tool.write_text(f"#!{INTERPRETER}\n")
    tool.chmod(0o755)
    return paths, public


@SUPPORTED_HOST
def test_each_exercisable_right_is_denied_outside_the_grants_and_allowed_inside(
    tmp_path: Path,
) -> None:
    """Item 6.4: the applied ruleset handles every right; one witness per right.

    MAKE_FIFO and MAKE_SYM are granted nowhere (the read-write grant creates regular
    files and directories only), so their control is the unconfined call below. REFER
    reports EXDEV, and its discriminating case is the allowed cross-grant rename.
    MAKE_SOCK, IOCTL_DEV and RESOLVE_UNIX stay HELD (plan v2.66, Held elements).
    """
    paths, public = _rights_layout(tmp_path)
    home, scratch, codex_home = paths["home"], paths["scratch"], paths["codex_home"]
    ops: list[list[Any]] = [
        ["EXECUTE denied", "exec", str(public / "tool")],
        ["EXECUTE allowed", "exec", str(INTERPRETER), "-I", "-S", "-c", "pass"],
        ["READ_FILE denied", "read", str(home / "file.txt")],
        ["READ_DIR denied", "list", str(home)],
        ["WRITE_FILE denied", "write", str(home / "file.txt")],
        ["TRUNCATE denied", "truncate", str(home / "trunc.txt")],
        ["REMOVE_FILE denied", "unlink", str(home / "doomed.txt")],
        ["REMOVE_DIR denied", "rmdir", str(home / "emptydir")],
        ["MAKE_DIR denied", "mkdir", str(home / "newdir")],
        ["MAKE_REG denied", "mkreg", str(home / "new.txt")],
        ["MAKE_FIFO denied", "mkfifo", str(home / "fifo")],
        ["MAKE_SYM denied", "symlink", str(home / "link")],
        ["MAKE_FIFO ungranted", "mkfifo", str(scratch / "fifo")],
        ["MAKE_SYM ungranted", "symlink", str(scratch / "link")],
        ["REFER denied", "link", str(public / "shared.txt"), str(scratch / "shared.txt")],
        ["REFER allowed", "rename", str(scratch / "moved.txt"), str(codex_home / "arrived.txt")],
    ]
    for label, root in (("scratch", scratch), ("codex_home", codex_home)):
        ops += [
            [f"READ_FILE allowed {label}", "read", str(root / "file.txt")],
            [f"READ_DIR allowed {label}", "list", str(root)],
            [f"WRITE_FILE allowed {label}", "write", str(root / "file.txt")],
            [f"TRUNCATE allowed {label}", "truncate", str(root / "trunc.txt")],
            [f"REMOVE_FILE allowed {label}", "unlink", str(root / "doomed.txt")],
            [f"REMOVE_DIR allowed {label}", "rmdir", str(root / "emptydir")],
            [f"MAKE_DIR allowed {label}", "mkdir", str(root / "newdir")],
            [f"MAKE_REG allowed {label}", "mkreg", str(root / "new.txt")],
        ]
    seen = _rights_probe(_spec(paths, extra=(str(public),)), ops)

    expected = {name: "ok" if " allowed" in name else "EACCES" for name, *_ in ops}
    expected["REFER denied"] = "EXDEV"
    assert seen == expected
    assert (home / "file.txt").read_text() == "fixture"
    assert (home / "trunc.txt").read_text() == "fixture"
    assert {p.name for p in home.iterdir()} == {
        ".codex",
        "secret-notes.txt",
        "file.txt",
        "doomed.txt",
        "trunc.txt",
        "moved.txt",
        "emptydir",
    }
    # The FIFO and symlink denials come from Landlock: unconfined, the same calls succeed.
    os.mkfifo(scratch / "fifo")
    os.symlink("/dev/null", scratch / "link")


_MAKE_CHAR, _MAKE_BLOCK = 1 << 6, 1 << 11


def _device_node_prerequisites(tmp_path: Path) -> str | None:
    """Why the device-node discriminator is HELD on this host, or None when it can run."""
    cap_eff = next(
        int(line.split()[1], 16)
        for line in Path("/proc/self/status").read_text().splitlines()
        if line.startswith("CapEff:")
    )
    if cap_eff & (1 << 27):
        return "HELD: the fixture holds CAP_MKNOD"
    try:
        os.mknod(tmp_path / "prereq-fifo", 0o600 | 0o010000)  # S_IFIFO
    except OSError as exc:
        return f"HELD: a sandbox refuses mknod before Landlock ({errno.errorcode[exc.errno or 0]})"
    os.unlink(tmp_path / "prereq-fifo")
    return None


@SUPPORTED_HOST
def test_device_node_creation_is_denied_by_landlock_not_by_the_missing_capability(
    tmp_path: Path,
) -> None:
    """Item 6.4 bits 6 and 11: Landlock's EACCES precedes the CAP_MKNOD check, so the
    control ruleset that leaves both rights unhandled gets EPERM instead."""
    held = _device_node_prerequisites(tmp_path)
    if held is not None:
        pytest.skip(held)
    paths = _layout(tmp_path)
    home = paths["home"]
    ops = [["MAKE_CHAR", "mkchr", str(home / "cdev")], ["MAKE_BLOCK", "mkblk", str(home / "bdev")]]

    applied = _rights_probe(_spec(paths), ops)
    control = _rights_probe(_spec(paths), ops, inject={"unhandled": _MAKE_CHAR | _MAKE_BLOCK})

    assert applied == {"MAKE_CHAR": "EACCES", "MAKE_BLOCK": "EACCES"}
    assert control == {"MAKE_CHAR": "EPERM", "MAKE_BLOCK": "EPERM"}
    assert not (home / "cdev").exists() and not (home / "bdev").exists()


@SUPPORTED_HOST
@pytest.mark.parametrize("broad", ["/", "/usr", "/home", "HOME", "HOME_PARENT"])
def test_a_broad_allowance_is_refused_at_launch(tmp_path: Path, broad: str) -> None:
    paths = _layout(tmp_path)
    target = {"HOME": str(paths["home"]), "HOME_PARENT": str(tmp_path)}.get(broad, broad)
    assert "exposes" in _refusal(_launch(_spec(paths, extra=(target,)), {}))


@SUPPORTED_HOST
def test_a_symlinked_allowance_cannot_reach_the_protected_home(tmp_path: Path) -> None:
    """Review P2-1: the check and the grant are the same opened object, not two strings."""
    paths = _layout(tmp_path)
    alias = tmp_path / "public-dns-alias"
    alias.symlink_to(paths["home"], target_is_directory=True)
    assert "canonical" in _refusal(_launch(_spec(paths, extra=(str(alias),)), {}))


@SUPPORTED_HOST
def test_an_ancestor_symlink_on_an_allowance_is_refused(tmp_path: Path) -> None:
    paths = _layout(tmp_path)
    (tmp_path / "public").mkdir()
    (tmp_path / "public" / "hosts").write_text("fixture")
    ancestor = tmp_path / "via-link"
    ancestor.symlink_to(tmp_path / "public", target_is_directory=True)
    assert "canonical" in _refusal(_launch(_spec(paths, extra=(str(ancestor / "hosts"),)), {}))


@SUPPORTED_HOST
@pytest.mark.parametrize("where", ["residence", "inside"])
def test_the_interactive_codex_residence_is_never_granted(tmp_path: Path, where: str) -> None:
    """Review P2-2: the operator's own ``~/.codex`` (or anything in it) is not dedicated."""
    paths = _layout(tmp_path)
    residence = paths["home"] / ".codex"
    granted = residence if where == "residence" else residence / "harness"
    granted.mkdir(mode=0o700, exist_ok=True)
    spec = _spec(paths, read_write=(str(granted), str(paths["scratch"])))
    assert "sealed" in _refusal(_launch(spec, {}))


@SUPPORTED_HOST
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


@UNSUPPORTED_HOST
def test_this_unsupported_host_is_refused_by_the_real_launcher(tmp_path: Path) -> None:
    """Spec item 6.2 with the REAL host report: the refusal every HELD canary names."""
    assert _refusal(_launch(_spec(_layout(tmp_path)), {})) == HOST_REFUSAL


# The launcher's own grant and executable checks, called in-process on any host: they open
# and compare descriptors only, so they need no ruleset. The launch tests above prove the
# same refusals on the real entry path where the kernel supports it.
def _unsafe_allowance(tmp_path: Path, paths: dict[str, Path], case: str) -> str:
    if case == "missing":
        return str(tmp_path / "nope")
    if case == "symlinked":
        (alias := tmp_path / "public-dns-alias").symlink_to(paths["home"], target_is_directory=True)
        return str(alias)
    if case == "ancestor-symlink":
        (tmp_path / "public").mkdir()
        (tmp_path / "public" / "hosts").write_text("fixture")
        (via := tmp_path / "via-link").symlink_to(tmp_path / "public", target_is_directory=True)
        return str(via / "hosts")
    if case in ("residence", "inside-residence"):
        granted = paths["home"] / ".codex" / ("harness" if case == "inside-residence" else "")
        granted.mkdir(mode=0o700, exist_ok=True)
        return str(granted)
    return {"HOME": str(paths["home"]), "HOME_PARENT": str(tmp_path)}.get(case, case)


@pytest.mark.parametrize(
    ("case", "reason"),
    [
        ("missing", "allowed path unusable (ENOENT)"),
        ("symlinked", "allowed path is not canonical"),
        ("ancestor-symlink", "allowed path is not canonical"),
        ("residence", "allowance exposes a protected or sealed root"),
        ("inside-residence", "allowance lies inside a sealed root"),
        *((broad, "allowance exposes") for broad in ("/", "/usr", "/home", "HOME", "HOME_PARENT")),
    ],
)
def test_the_grant_policy_refuses_an_unsafe_allowance_on_any_host(
    tmp_path: Path, case: str, reason: str
) -> None:
    paths = _layout(tmp_path)
    allowance = _unsafe_allowance(tmp_path, paths, case)
    policy = boundary._GrantPolicy.of(_spec(paths))
    with pytest.raises(boundary.LauncherRefusalError, match=re.escape(reason)):
        boundary._grant_descriptor(allowance, os.O_PATH, policy)


@pytest.mark.parametrize("case", ["pin", "symlinked", "missing"])
def test_the_executable_check_refuses_on_any_host(tmp_path: Path, case: str) -> None:
    paths = _layout(tmp_path)
    if case == "symlinked":
        (tmp_path / "codex-latest").symlink_to(INTERPRETER)
    spec = {
        "pin": _spec(paths, sha="0" * 64),
        "symlinked": _spec(paths, executable=tmp_path / "codex-latest"),
        "missing": _spec(paths, executable=tmp_path / "absent-codex"),
    }[case]
    expected = "sha256 does not match" if case == "pin" else "executable allowed path"
    with pytest.raises(boundary.LauncherRefusalError, match=expected):
        boundary._open_verified_executable(spec, boundary._GrantPolicy.of(spec))
