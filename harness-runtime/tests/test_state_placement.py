"""S1 — external persistent state-root verifier, config carrier and path derivation.

Code-only slice: nothing here is wired into bootstrap, factories, inspect or the B-104
claim gateway, so none of it proves production placement. It proves the pure verifier,
the typed refusals, the identity stamp and the single path derivation that a later
wiring slice consumes.

Every test runs with an injected filesystem-type resolver because pytest's tmp_path is
tmpfs on this host, which the verifier (correctly) refuses as a durable root.
"""

from __future__ import annotations

import os
import shutil
import stat
import tempfile
import tomllib
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pytest
from harness_runtime.config.loader import materialize_runtime_config
from harness_runtime.config.state_placement import (
    StateKind,
    StatePlacementRefusal,
    StateRootPlacementError,
    VerifiedStateRoot,
    bootstrap_state_root,
    filesystem_type_from_mountinfo,
    linux_filesystem_type,
    probe_state_root,
    revalidate_state_root,
    state_path,
)
from harness_runtime.config_source import RuntimeConfigSource
from harness_runtime.types import PathBindingConfig, RuntimeConfig, StatePlacementConfig
from pydantic import ValidationError

Refusal = StatePlacementRefusal


def _ext4(_path: Path) -> str | None:
    return "ext4"


@dataclass
class Layout:
    """A fake checkout, a private state home and helpers, all under tmp_path."""

    base: Path
    repo: Path
    worktree_base: Path
    home: Path

    def bindings(self, *cells: Path) -> PathBindingConfig:
        classes = ("software-engineering", "research", "content-creation", "pipeline-automation")
        return PathBindingConfig(
            raw_entries=tuple(
                {
                    "path_class": "STATE_LEDGER",
                    "workflow_class": classes[i],
                    "deployment_surface": "local-development",
                    "path": str(cell),
                }
                for i, cell in enumerate(cells)
            )
        )

    def snapshot(self) -> list[tuple[str, bool, int, int]]:
        out: list[tuple[str, bool, int, int]] = []
        for p in sorted(self.base.rglob("*")):
            st = p.lstat()
            out.append(
                (str(p.relative_to(self.base)), stat.S_ISDIR(st.st_mode), st.st_size, st.st_mode)
            )
        return out


def _has_git_at_or_above(path: Path) -> bool:
    return any(os.path.lexists(p / ".git") for p in (path, *path.parents))


@pytest.fixture
def world(tmp_path: Path) -> Iterator[Path]:
    """A scratch directory with no `.git` at or above it.

    The verifier (correctly) refuses any root under a checkout, and some hosts keep a
    `.git` in a shared temp dir, so a plain tmp_path is not always usable. Fall back to
    /dev/shm; skip when neither is clear.
    """
    for parent in (tmp_path, Path("/dev/shm")):
        if parent.is_dir() and os.access(parent, os.W_OK) and not _has_git_at_or_above(parent):
            scratch = Path(tempfile.mkdtemp(prefix="state-placement-", dir=parent))
            break
    else:
        pytest.skip("no scratch directory free of a .git ancestor")
    try:
        yield scratch
    finally:
        shutil.rmtree(scratch, ignore_errors=True)


@pytest.fixture
def lay(world: Path) -> Layout:
    base = world / "world"
    repo = base / "repo"
    (repo / ".git").mkdir(parents=True)
    (repo / ".harness").mkdir()
    home = base / "home"
    home.mkdir(mode=0o755)
    (home / "state").mkdir(mode=0o700)
    return Layout(base, repo, repo / ".harness" / "worktrees", home)


def _config(root: Path, *forbidden: Path) -> StatePlacementConfig:
    return StatePlacementConfig(state_root=root, forbidden_roots=tuple(forbidden))


def _bootstrap(
    lay: Layout,
    root: Path | str,
    *,
    forbidden: tuple[Path, ...] = (),
    cells: tuple[Path, ...] | None = None,
    fs: Callable[[Path], str | None] = _ext4,
) -> VerifiedStateRoot:
    placement = StatePlacementConfig(state_root=Path(root), forbidden_roots=forbidden)
    return bootstrap_state_root(
        placement,
        repository_root=lay.repo,
        worktree_base=lay.worktree_base,
        path_bindings=lay.bindings(*(cells if cells is not None else (Path(root) / "ledger",))),
        filesystem_type=fs,
    )


def _probe(
    lay: Layout,
    root: Path,
    *,
    fs: Callable[[Path], str | None] = _ext4,
    cells: tuple[Path, ...] | None = None,
) -> VerifiedStateRoot:
    return probe_state_root(
        _config(root),
        repository_root=lay.repo,
        worktree_base=lay.worktree_base,
        path_bindings=lay.bindings(*(cells if cells is not None else (root / "ledger",))),
        filesystem_type=fs,
    )


def _assert_refused_without_mutation(
    lay: Layout, reason: StatePlacementRefusal, run: Callable[[], Any]
) -> None:
    before = lay.snapshot()
    with pytest.raises(StateRootPlacementError) as excinfo:
        run()
    assert excinfo.value.reason is reason
    assert lay.snapshot() == before


# --- default-None compatibility and the carrier ---------------------------------------


def test_runtime_config_defaults_state_placement_to_none() -> None:
    assert RuntimeConfig.model_fields["state_placement"].default is None


_LEGACY_LITERALS = {
    StateKind.EFFECT_FENCE: ".harness/effect-fence",
    StateKind.ENGINE_RECOVERY_SEGMENTS: ".harness/engine-recovery-segments",
    StateKind.ENGINE_RECOVERY_RECONCILER: ".harness/engine-recovery-reconciler",
    StateKind.PROTECTED_RESULTS: ".harness/protected-results",
    StateKind.MEMORIES: ".harness/memories",
    StateKind.MEMORIES_DB: ".harness/memories.db",
    StateKind.MEMORIES_ENCRYPTED: ".harness/memories-encrypted",
    StateKind.MEMORY: ".harness/memory",
}


def test_state_kinds_are_exactly_the_persistent_recovery_and_memory_paths() -> None:
    # Ledger-adjacent stores (pause-journal, pause-state-audit, engine-output) live under
    # STATE_LEDGER and are deliberately not kinds.
    assert set(StateKind) == set(_LEGACY_LITERALS)


@pytest.mark.parametrize("kind", list(StateKind))
def test_without_a_verified_root_every_kind_keeps_its_exact_legacy_path(
    kind: StateKind, lay: Layout
) -> None:
    assert state_path(kind, None, lay.repo) == lay.repo / _LEGACY_LITERALS[kind]


@pytest.mark.parametrize("kind", list(StateKind))
def test_with_a_verified_root_every_kind_is_derived_under_the_root(
    kind: StateKind, lay: Layout
) -> None:
    stamp = _bootstrap(lay, lay.home / "state" / "root")

    derived = state_path(kind, stamp, lay.repo)

    assert derived == stamp.realpath / Path(_LEGACY_LITERALS[kind]).name
    assert derived.is_relative_to(stamp.realpath)


def test_state_root_file_table_is_parsed_without_expansion(tmp_path: Path) -> None:
    config_file = tmp_path / "harness.toml"
    config_file.write_text(
        '[runtime]\ndeployment_surface = "local-development"\n'
        f'repository_root = "{tmp_path}"\n'
        'default_topology = "single-threaded-linear"\n'
        '[runtime.otel]\notlp_endpoint = "http://127.0.0.1:4317"\n'
        "[runtime.state_placement]\n"
        'state_root = "~/state"\nforbidden_roots = ["/srv/backup"]\n'
    )

    config = RuntimeConfigSource.load(config_file=config_file)

    assert config.state_placement == StatePlacementConfig(
        state_root=Path("~/state"), forbidden_roots=(Path("/srv/backup"),)
    )
    assert tomllib.loads(config_file.read_text())["runtime"]["state_placement"]["state_root"] == (
        "~/state"
    )


def test_kwargs_and_file_agree_on_the_carrier(tmp_path: Path) -> None:
    from_kwargs = materialize_runtime_config(
        env={},
        deployment_surface="local-development",
        repository_root=tmp_path,
        default_topology="single-threaded-linear",
        otel={"otlp_endpoint": "http://127.0.0.1:4317"},
        state_placement={"state_root": "/var/lib/a", "forbidden_roots": ["/x"]},
    )

    assert from_kwargs.state_placement == StatePlacementConfig(
        state_root=Path("/var/lib/a"), forbidden_roots=(Path("/x"),)
    )


def test_an_unknown_state_placement_key_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(ValidationError) as excinfo:
        materialize_runtime_config(
            env={},
            deployment_surface="local-development",
            repository_root=tmp_path,
            default_topology="single-threaded-linear",
            otel={"otlp_endpoint": "http://127.0.0.1:4317"},
            state_placement={"state_root": "/a", "surprise": True},
        )

    assert [(e["loc"], e["type"]) for e in excinfo.value.errors()] == [
        (("state_placement", "surprise"), "extra_forbidden")
    ]


# --- typed refusals, each with zero filesystem mutation --------------------------------


@pytest.mark.parametrize("raw", ["relative/root", "~/state", "/abs/../escape", "./x"])
def test_relative_tilde_and_dotdot_roots_are_refused(lay: Layout, raw: str) -> None:
    _assert_refused_without_mutation(lay, Refusal.RELATIVE, lambda: _bootstrap(lay, raw))


def test_a_relative_forbidden_root_is_refused(lay: Layout) -> None:
    _assert_refused_without_mutation(
        lay,
        Refusal.RELATIVE,
        lambda: _bootstrap(lay, lay.home / "state" / "r", forbidden=(Path("rel"),)),
    )


def test_a_root_inside_the_repo_checkout_is_refused(lay: Layout) -> None:
    _assert_refused_without_mutation(
        lay, Refusal.INSIDE_CHECKOUT, lambda: _bootstrap(lay, lay.repo / ".harness" / "state")
    )


def test_a_root_inside_a_linked_worktree_git_file_is_refused(lay: Layout) -> None:
    linked = lay.base / "linked-wt"
    (linked / "sub").mkdir(parents=True)
    (linked / ".git").write_text("gitdir: /elsewhere/.git/worktrees/linked-wt\n")

    _assert_refused_without_mutation(
        lay, Refusal.INSIDE_CHECKOUT, lambda: _bootstrap(lay, linked / "sub" / "state")
    )


def test_a_root_inside_an_unrelated_checkout_is_refused(lay: Layout) -> None:
    other = lay.base / "other-project"
    (other / ".git").mkdir(parents=True)

    _assert_refused_without_mutation(
        lay, Refusal.INSIDE_CHECKOUT, lambda: _bootstrap(lay, other / "state")
    )


def test_a_nonexistent_root_under_a_checkout_ancestor_is_refused_before_anything_else(
    lay: Layout,
) -> None:
    _assert_refused_without_mutation(
        lay, Refusal.INSIDE_CHECKOUT, lambda: _bootstrap(lay, lay.repo / "missing" / "deeper")
    )


def test_a_symlinked_ancestor_resolving_into_the_checkout_is_refused(lay: Layout) -> None:
    link = lay.home / "alias"
    link.symlink_to(lay.repo / ".harness")

    _assert_refused_without_mutation(
        lay, Refusal.INSIDE_CHECKOUT, lambda: _bootstrap(lay, link / "state")
    )


def test_a_symlink_as_the_root_itself_is_refused(lay: Layout) -> None:
    target = lay.home / "state" / "real"
    target.mkdir(mode=0o700)
    link = lay.home / "state" / "link"
    link.symlink_to(target)

    _assert_refused_without_mutation(lay, Refusal.SYMLINK_ROOT, lambda: _bootstrap(lay, link))


@pytest.mark.parametrize("which", ["repo", "worktree_base", "repo_ancestor", "forbidden"])
def test_a_root_equal_to_or_containing_a_protected_tree_is_refused(lay: Layout, which: str) -> None:
    forbidden = lay.home / "state" / "backup"
    forbidden.mkdir(mode=0o700)
    if which == "worktree_base":
        # A worktree base under the checkout would trip INSIDE_CHECKOUT first; use one outside.
        lay.worktree_base = lay.base / "wtbase"
    roots = {
        "repo": lay.repo,
        "worktree_base": lay.worktree_base,
        "repo_ancestor": lay.base,
        "forbidden": lay.home / "state",
    }

    _assert_refused_without_mutation(
        lay,
        Refusal.CONTAINS_CHECKOUT,
        lambda: _bootstrap(lay, roots[which], forbidden=(forbidden,), cells=(roots[which] / "l",)),
    )


def test_a_root_inside_a_declared_forbidden_root_is_refused(lay: Layout) -> None:
    backup = lay.home / "state" / "backup-scope"
    backup.mkdir(mode=0o700)

    _assert_refused_without_mutation(
        lay,
        Refusal.INSIDE_FORBIDDEN,
        lambda: _bootstrap(lay, backup / "state", forbidden=(backup,)),
    )


def test_one_non_bootstrap_state_ledger_cell_outside_the_root_is_refused(lay: Layout) -> None:
    root = lay.home / "state" / "root"
    outside = lay.home / "elsewhere" / "ledger"

    _assert_refused_without_mutation(
        lay,
        Refusal.LEDGER_CELL_OUTSIDE,
        lambda: _bootstrap(lay, root, cells=(root / "ledger", outside)),
    )


def test_a_relative_state_ledger_cell_cannot_be_proven_inside_and_is_refused(lay: Layout) -> None:
    root = lay.home / "state" / "root"

    _assert_refused_without_mutation(
        lay,
        Refusal.LEDGER_CELL_OUTSIDE,
        lambda: _bootstrap(lay, root, cells=(root / "ledger", Path("relative/ledger"))),
    )


def test_every_state_ledger_cell_inside_the_root_is_accepted(lay: Layout) -> None:
    root = lay.home / "state" / "root"

    stamp = _bootstrap(lay, root, cells=(root / "a", root / "b", root / "deep" / "c"))

    assert stamp.realpath == root.resolve()


@pytest.mark.parametrize("mode", [0o770, 0o707, 0o777])
def test_an_existing_group_or_other_writable_root_is_refused(lay: Layout, mode: int) -> None:
    root = lay.home / "state" / "root"
    root.mkdir()
    root.chmod(mode)

    _assert_refused_without_mutation(lay, Refusal.PERMISSIONS, lambda: _bootstrap(lay, root))


def test_a_root_not_owned_by_the_effective_user_is_refused(
    lay: Layout, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = lay.home / "state" / "root"
    root.mkdir(mode=0o700)
    real_uid = os.geteuid()
    monkeypatch.setattr(os, "geteuid", lambda: real_uid + 1)

    _assert_refused_without_mutation(lay, Refusal.PERMISSIONS, lambda: _bootstrap(lay, root))


def test_a_root_that_is_a_file_is_refused(lay: Layout) -> None:
    root = lay.home / "state" / "afile"
    root.write_text("x")

    _assert_refused_without_mutation(lay, Refusal.NOT_A_DIRECTORY, lambda: _bootstrap(lay, root))


def test_bootstrap_never_creates_missing_parents(lay: Layout) -> None:
    _assert_refused_without_mutation(
        lay, Refusal.PARENT_MISSING, lambda: _bootstrap(lay, lay.home / "nope" / "root")
    )


def test_a_group_writable_parent_without_sticky_bit_is_unsafe(lay: Layout) -> None:
    parent = lay.home / "shared"
    parent.mkdir()
    parent.chmod(0o775)

    _assert_refused_without_mutation(
        lay, Refusal.PARENT_UNSAFE, lambda: _bootstrap(lay, parent / "root")
    )


@pytest.mark.parametrize("fstype", ["tmpfs", "ramfs"])
def test_volatile_filesystems_are_refused(lay: Layout, fstype: str) -> None:
    _assert_refused_without_mutation(
        lay,
        Refusal.NON_DURABLE_FS,
        lambda: _bootstrap(lay, lay.home / "state" / "root", fs=lambda _p: fstype),
    )


def test_an_undeterminable_filesystem_type_is_refused_rather_than_assumed_durable(
    lay: Layout,
) -> None:
    _assert_refused_without_mutation(
        lay,
        Refusal.FS_UNDETERMINED,
        lambda: _bootstrap(lay, lay.home / "state" / "root", fs=lambda _p: None),
    )


@pytest.mark.parametrize("name", [".harness/effect-fence", ".harness/protected-results"])
def test_a_nonempty_legacy_directory_refuses_placement(lay: Layout, name: str) -> None:
    legacy = lay.repo / name
    legacy.mkdir(parents=True)
    (legacy / "record").write_text("state")

    _assert_refused_without_mutation(
        lay, Refusal.LEGACY_STATE_PRESENT, lambda: _bootstrap(lay, lay.home / "state" / "root")
    )


def test_a_nonempty_legacy_memory_database_file_refuses_placement(lay: Layout) -> None:
    (lay.repo / ".harness" / "memories.db").write_bytes(b"sqlite")

    _assert_refused_without_mutation(
        lay, Refusal.LEGACY_STATE_PRESENT, lambda: _bootstrap(lay, lay.home / "state" / "root")
    )


def test_empty_legacy_directories_do_not_refuse(lay: Layout) -> None:
    (lay.repo / ".harness" / "effect-fence").mkdir()
    (lay.repo / ".harness" / "memories.db").write_bytes(b"")

    stamp = _bootstrap(lay, lay.home / "state" / "root")

    assert stamp.root_id


# --- bootstrap creates safely; probe never creates -------------------------------------


def test_bootstrap_creates_a_private_root_and_an_exclusive_marker(lay: Layout) -> None:
    root = lay.home / "state" / "root"

    stamp = _bootstrap(lay, root)

    assert stat.S_IMODE(root.stat().st_mode) == 0o700
    marker = root / ".arhugula-state-root"
    assert stat.S_IMODE(marker.stat().st_mode) == 0o600
    assert marker.read_text() == stamp.root_id
    assert len(stamp.root_id) == 32
    assert (stamp.st_dev, stamp.st_ino) == (root.stat().st_dev, root.stat().st_ino)
    assert stamp.realpath == root.resolve()


def test_the_marker_is_written_exclusively_and_never_overwrites_an_existing_one(
    lay: Layout,
) -> None:
    from harness_runtime.config import state_placement as sp

    root = lay.home / "state" / "root"
    stamp = _bootstrap(lay, root)

    with pytest.raises(FileExistsError):
        sp._write_marker_exclusively(root)  # pyright: ignore[reportPrivateUsage]

    assert (root / ".arhugula-state-root").read_text() == stamp.root_id


def test_bootstrap_is_idempotent_and_keeps_the_existing_marker(lay: Layout) -> None:
    root = lay.home / "state" / "root"

    first = _bootstrap(lay, root)
    second = _bootstrap(lay, root)

    assert second == first


def test_bootstrap_adopts_an_existing_empty_private_directory(lay: Layout) -> None:
    root = lay.home / "state" / "root"
    root.mkdir(mode=0o700)

    stamp = _bootstrap(lay, root)

    assert (root / ".arhugula-state-root").read_text() == stamp.root_id


def test_bootstrap_will_not_adopt_a_nonempty_directory_without_a_marker(lay: Layout) -> None:
    root = lay.home / "state" / "root"
    root.mkdir(mode=0o700)
    (root / "someone-elses-file").write_text("data")

    _assert_refused_without_mutation(lay, Refusal.MARKER_MISSING, lambda: _bootstrap(lay, root))


def test_probe_on_a_missing_root_refuses_and_creates_nothing(lay: Layout) -> None:
    _assert_refused_without_mutation(
        lay, Refusal.ROOT_MISSING, lambda: _probe(lay, lay.home / "state" / "root")
    )


def test_probe_without_a_marker_refuses_and_does_not_write_one(lay: Layout) -> None:
    root = lay.home / "state" / "root"
    root.mkdir(mode=0o700)

    _assert_refused_without_mutation(lay, Refusal.MARKER_MISSING, lambda: _probe(lay, root))


def test_probe_returns_the_bootstrap_stamp(lay: Layout) -> None:
    root = lay.home / "state" / "root"
    stamp = _bootstrap(lay, root)

    assert _probe(lay, root) == stamp


def test_a_corrupt_marker_is_refused_by_probe(lay: Layout) -> None:
    root = lay.home / "state" / "root"
    _bootstrap(lay, root)
    (root / ".arhugula-state-root").write_text("not-a-root-id")

    _assert_refused_without_mutation(lay, Refusal.MARKER_INVALID, lambda: _probe(lay, root))


# --- revalidation: a replaced root is not the same root --------------------------------


def _revalidate(lay: Layout, stamp: VerifiedStateRoot, root: Path) -> VerifiedStateRoot:
    return revalidate_state_root(
        stamp,
        _config(root),
        repository_root=lay.repo,
        worktree_base=lay.worktree_base,
        path_bindings=lay.bindings(root / "ledger"),
        filesystem_type=_ext4,
    )


def test_revalidating_an_untouched_root_returns_an_equal_stamp(lay: Layout) -> None:
    root = lay.home / "state" / "root"
    stamp = _bootstrap(lay, root)

    assert _revalidate(lay, stamp, root) == stamp


def test_a_replaced_same_path_root_with_a_copied_marker_is_identity_changed(lay: Layout) -> None:
    root = lay.home / "state" / "root"
    stamp = _bootstrap(lay, root)
    marker_text = (root / ".arhugula-state-root").read_text()
    root.rename(lay.home / "state" / "old")
    root.mkdir(mode=0o700)
    (root / ".arhugula-state-root").write_text(marker_text)
    (root / ".arhugula-state-root").chmod(0o600)

    with pytest.raises(StateRootPlacementError) as excinfo:
        _revalidate(lay, stamp, root)

    assert excinfo.value.reason is Refusal.IDENTITY_CHANGED


def test_a_replaced_root_with_a_different_marker_is_identity_changed(lay: Layout) -> None:
    root = lay.home / "state" / "root"
    stamp = _bootstrap(lay, root)
    root.rename(lay.home / "state" / "old")
    _bootstrap(lay, root)

    with pytest.raises(StateRootPlacementError) as excinfo:
        _revalidate(lay, stamp, root)

    assert excinfo.value.reason is Refusal.IDENTITY_CHANGED


def test_a_missing_marker_fails_revalidation(lay: Layout) -> None:
    root = lay.home / "state" / "root"
    stamp = _bootstrap(lay, root)
    (root / ".arhugula-state-root").unlink()

    with pytest.raises(StateRootPlacementError) as excinfo:
        _revalidate(lay, stamp, root)

    assert excinfo.value.reason is Refusal.MARKER_MISSING


def test_retargeting_a_symlinked_ancestor_changes_the_realpath(lay: Layout) -> None:
    real_a = lay.home / "state" / "a"
    real_b = lay.home / "state" / "b"
    real_a.mkdir(mode=0o700)
    real_b.mkdir(mode=0o700)
    alias = lay.home / "state" / "alias"
    alias.symlink_to(real_a)
    root = alias / "root"
    stamp = _bootstrap(lay, root)
    os.rename(real_a / "root", real_b / "root")
    alias.unlink()
    alias.symlink_to(real_b)

    with pytest.raises(StateRootPlacementError) as excinfo:
        _revalidate(lay, stamp, root)

    assert excinfo.value.reason is Refusal.IDENTITY_CHANGED


# --- the real filesystem-type resolver -------------------------------------------------

_MOUNTINFO = (
    "22 1 8:2 / / rw,relatime - ext4 /dev/sda2 rw\n"
    "30 22 0:25 / /tmp rw,nosuid - tmpfs tmpfs rw\n"
    "31 22 0:26 / /home rw - btrfs /dev/sda3 rw\n"
    "32 31 0:27 / /home/user/my\\040data rw - ramfs none rw\n"
)


@pytest.mark.parametrize(
    ("path", "expected"),
    [
        ("/etc/x", "ext4"),
        ("/tmp/pytest/x", "tmpfs"),
        ("/tmpx/y", "ext4"),
        ("/home/user/x", "btrfs"),
        ("/home/user/my data/x", "ramfs"),
    ],
)
def test_mountinfo_parser_picks_the_longest_matching_mount(path: str, expected: str) -> None:
    assert filesystem_type_from_mountinfo(_MOUNTINFO, Path(path)) == expected


def test_mountinfo_without_any_covering_mount_is_undetermined() -> None:
    assert filesystem_type_from_mountinfo("", Path("/x")) is None


@pytest.mark.skipif(
    not Path("/dev/shm").is_dir() or not os.access("/dev/shm", os.W_OK),
    reason="needs a writable /dev/shm",
)
def test_the_real_resolver_identifies_dev_shm_as_volatile(tmp_path: Path) -> None:
    assert linux_filesystem_type(Path("/dev/shm")) in {"tmpfs", "ramfs"}


# --- private-state invariant for EXISTING roots and markers (S1 delta) --------------------


def _private_root(lay: Layout) -> Path:
    root = lay.home / "state" / "root"
    _bootstrap(lay, root)
    return root


@pytest.mark.parametrize("mode", [0o755, 0o750, 0o705, 0o710])
def test_an_existing_root_with_any_group_or_other_access_is_refused_everywhere(
    lay: Layout, mode: int
) -> None:
    root = _private_root(lay)
    stamp = _probe(lay, root)
    root.chmod(mode)

    _assert_refused_without_mutation(lay, Refusal.PERMISSIONS, lambda: _probe(lay, root))
    _assert_refused_without_mutation(lay, Refusal.PERMISSIONS, lambda: _bootstrap(lay, root))
    _assert_refused_without_mutation(
        lay, Refusal.PERMISSIONS, lambda: _revalidate(lay, stamp, root)
    )


@pytest.mark.parametrize("mode", [0o666, 0o644, 0o640, 0o604, 0o660])
def test_an_existing_marker_with_any_group_or_other_access_is_never_a_valid_identity(
    lay: Layout, mode: int
) -> None:
    root = _private_root(lay)
    stamp = _probe(lay, root)
    (root / ".arhugula-state-root").chmod(mode)

    _assert_refused_without_mutation(lay, Refusal.MARKER_UNSAFE, lambda: _probe(lay, root))
    _assert_refused_without_mutation(lay, Refusal.MARKER_UNSAFE, lambda: _bootstrap(lay, root))
    _assert_refused_without_mutation(
        lay, Refusal.MARKER_UNSAFE, lambda: _revalidate(lay, stamp, root)
    )


def test_a_marker_not_owned_by_the_effective_user_is_unsafe(
    lay: Layout, monkeypatch: pytest.MonkeyPatch
) -> None:
    from harness_runtime.config import state_placement as sp

    root = _private_root(lay)
    real_uid = os.geteuid()
    monkeypatch.setattr(os, "geteuid", lambda: real_uid + 1)

    with pytest.raises(StateRootPlacementError) as excinfo:
        sp._read_marker(root)  # pyright: ignore[reportPrivateUsage]

    assert excinfo.value.reason is Refusal.MARKER_UNSAFE


def test_a_symlinked_marker_is_refused(lay: Layout) -> None:
    root = _private_root(lay)
    marker = root / ".arhugula-state-root"
    real = marker.read_text()
    marker.unlink()
    elsewhere = lay.home / "state" / "elsewhere"
    elsewhere.write_text(real)
    elsewhere.chmod(0o600)
    marker.symlink_to(elsewhere)

    _assert_refused_without_mutation(lay, Refusal.MARKER_INVALID, lambda: _probe(lay, root))


def test_a_private_root_and_marker_are_still_accepted(lay: Layout) -> None:
    root = _private_root(lay)

    assert stat.S_IMODE(root.stat().st_mode) == 0o700
    assert _probe(lay, root) == _bootstrap(lay, root)


def test_the_marker_is_opened_close_on_exec(lay: Layout, monkeypatch: pytest.MonkeyPatch) -> None:
    root = _private_root(lay)
    flags_seen: list[int] = []
    real_open = os.open

    def spy(path: Any, flags: int, *args: Any, **kwargs: Any) -> int:
        if str(path).endswith(".arhugula-state-root"):
            flags_seen.append(flags)
        return real_open(path, flags, *args, **kwargs)

    monkeypatch.setattr(os, "open", spy)
    _probe(lay, root)

    assert flags_seen
    assert all(f & os.O_CLOEXEC and f & os.O_NOFOLLOW for f in flags_seen)


# --- the known checkout-local onboarding STATE_LEDGER is legacy state ---------------------

_ONBOARDING_LEDGER = Path(".harness") / "onboarding" / "state-ledger"


@pytest.mark.parametrize("child", ["state.jsonl", "pause-journal/run-1.json", "claims/lease"])
def test_a_nonempty_onboarding_state_ledger_refuses_external_placement(
    lay: Layout, child: str
) -> None:
    target = lay.repo / _ONBOARDING_LEDGER / child
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("x")

    _assert_refused_without_mutation(
        lay, Refusal.LEGACY_STATE_PRESENT, lambda: _bootstrap(lay, lay.home / "state" / "root")
    )


def test_an_empty_onboarding_state_ledger_and_unrelated_harness_files_do_not_refuse(
    lay: Layout,
) -> None:
    (lay.repo / _ONBOARDING_LEDGER).mkdir(parents=True)
    unrelated = lay.repo / ".harness" / "clearance" / "marker.md"
    unrelated.parent.mkdir(parents=True)
    unrelated.write_text("tracked checkout data that is not harness state")

    stamp = _bootstrap(lay, lay.home / "state" / "root")

    assert stamp.root_id
    assert unrelated.read_text() == "tracked checkout data that is not harness state"
