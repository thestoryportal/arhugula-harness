"""S2 — external state-root wiring: stage 1 verifier call, context stamp, factory derivation.

Provider-free. Runs the real stage-1 executor and the real persistent-store factories
against a fake checkout under a scratch directory. It proves the carrier wiring only:
nothing here is an installed-host witness, and B-104 claim/recovery, examples and the
installed proof remain later gates.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Any

import pytest
from cryptography.fernet import Fernet
from harness_as.anthropic_graceful_degradation import MemoryToolStorageBackend
from harness_core import DeploymentSurface, WorkloadClass
from harness_cp.topology_pattern import TopologyPattern
from harness_is.path_class_registry import PathClass
from harness_is.state_ledger_entry_schema import Actor, ActorClass
from harness_runtime.bootstrap import stage_1_is
from harness_runtime.bootstrap.factories import (
    memory_tool_registry_factory as memory_factory,
)
from harness_runtime.bootstrap.factories.memory_tool_registry_factory import (
    materialize_memory_tool_registry_stage,
)
from harness_runtime.bootstrap.factories.protected_result_store_factory import (
    materialize_protected_result_store_stage,
)
from harness_runtime.bootstrap.mutable_context import _MutableHarnessContext
from harness_runtime.config import state_placement as sp
from harness_runtime.config.state_placement import (
    StatePlacementRefusal,
    StateRootPlacementError,
    bootstrap_state_root,
    transient_worktree_base,
)
from harness_runtime.lifecycle.memory_tool_types import MemoryToolBackendConfig
from harness_runtime.types import (
    CollectorConfig,
    OTelConfig,
    PathBindingConfig,
    ProviderSecretsConfig,
    RuntimeConfig,
    StatePlacementConfig,
    VerifiedStateRoot,
)

from .test_state_placement import world  # noqa: F401  (fixture: scratch dir with no .git above)

Refusal = StatePlacementRefusal
WORKLOAD = WorkloadClass.SOFTWARE_ENGINEERING


@pytest.fixture(autouse=True)
def _durable_filesystem(monkeypatch: pytest.MonkeyPatch) -> None:
    """Scratch dirs may be tmpfs; the verifier's real resolver is covered in test_state_placement."""
    # raising=False: before S2 stage 1 had no verifier call, so the name may be absent.
    monkeypatch.setattr(stage_1_is, "linux_filesystem_type", lambda _p: "ext4", raising=False)
    monkeypatch.setattr(sp, "linux_filesystem_type", lambda _p: "ext4")


class Site:
    def __init__(self, base: Path) -> None:
        self.base = base
        self.repo = base / "repo"
        (self.repo / ".git").mkdir(parents=True)
        (self.repo / ".harness").mkdir()
        self.home = base / "home"
        self.home.mkdir(mode=0o755)
        (self.home / "state").mkdir(mode=0o700)
        self.root = self.home / "state" / "root"

    def snapshot(self) -> list[str]:
        return sorted(str(p.relative_to(self.base)) for p in self.base.rglob("*"))

    def config(
        self,
        *,
        placement: bool,
        ledger: Path | None = None,
        extra_ledger_cells: dict[WorkloadClass, Path] | None = None,
        **kwargs: Any,
    ) -> RuntimeConfig:
        ledger_path = ledger if ledger is not None else self.root / "state-ledger"
        entries: list[dict[str, object]] = [
            {
                "path_class": pc,
                "workflow_class": WORKLOAD,
                "deployment_surface": DeploymentSurface.LOCAL_DEVELOPMENT,
                "path": str(ledger_path)
                if pc is PathClass.STATE_LEDGER
                else str(self.repo / ".harness" / "onboarding" / pc.value.lower()),
            }
            for pc in PathClass
        ]
        for workload, cell in (extra_ledger_cells or {}).items():
            entries.append(
                {
                    "path_class": PathClass.STATE_LEDGER,
                    "workflow_class": workload,
                    "deployment_surface": DeploymentSurface.LOCAL_DEVELOPMENT,
                    "path": str(cell),
                }
            )
        return RuntimeConfig(
            deployment_surface=DeploymentSurface.LOCAL_DEVELOPMENT,
            repository_root=self.repo,
            path_bindings=PathBindingConfig(raw_entries=tuple(entries)),
            provider_secrets=ProviderSecretsConfig(),
            otel=OTelConfig(otlp_endpoint="http://localhost:4318"),
            collector=CollectorConfig(),
            default_topology=TopologyPattern.SINGLE_THREADED_LINEAR,
            mcp_clients=[],
            state_placement=StatePlacementConfig(state_root=self.root) if placement else None,
            **kwargs,
        )

    def stamp(self, config: RuntimeConfig) -> VerifiedStateRoot:
        assert config.state_placement is not None
        return bootstrap_state_root(
            config.state_placement,
            repository_root=self.repo,
            worktree_base=transient_worktree_base(self.repo),
            path_bindings=config.path_bindings,
            filesystem_type=lambda _p: "ext4",
        )


@pytest.fixture
def site(world: Path) -> Site:  # noqa: F811
    return Site(world / "site")


def _ctx(config: RuntimeConfig) -> _MutableHarnessContext:
    ctx = _MutableHarnessContext()
    ctx.config = config
    ctx.actor = Actor(actor_class=ActorClass.AGENT, actor_id="state-placement-bootstrap")
    return ctx


def _inside(path: Path, root: Path) -> bool:
    return path.resolve() == root.resolve() or root.resolve() in path.resolve().parents


# --- stage 1: verify once, before the registry -------------------------------------------


@pytest.mark.asyncio
async def test_a_refused_placement_creates_no_registry_ledger_or_store(site: Site) -> None:
    bad_root = site.repo / ".harness" / "state"
    config = site.config(placement=True, ledger=bad_root / "ledger").model_copy(
        update={"state_placement": StatePlacementConfig(state_root=bad_root)}
    )
    ctx = _ctx(config)
    before = site.snapshot()

    with pytest.raises(StateRootPlacementError) as excinfo:
        await stage_1_is.execute(ctx, config, WORKLOAD)

    assert excinfo.value.reason is Refusal.INSIDE_CHECKOUT
    assert site.snapshot() == before
    assert ctx.path_resolver is None
    assert ctx.ledger_writer is None
    assert ctx.verified_state_root is None


@pytest.mark.asyncio
async def test_a_second_workload_state_ledger_cell_outside_the_root_refuses_at_stage_1(
    site: Site,
) -> None:
    config = site.config(
        placement=True,
        extra_ledger_cells={WorkloadClass.RESEARCH: site.home / "elsewhere" / "ledger"},
    )
    ctx = _ctx(config)
    before = site.snapshot()

    with pytest.raises(StateRootPlacementError) as excinfo:
        await stage_1_is.execute(ctx, config, WORKLOAD)

    assert excinfo.value.reason is Refusal.LEDGER_CELL_OUTSIDE
    assert site.snapshot() == before


@pytest.mark.asyncio
async def test_a_configured_stage_1_stamps_the_context_and_keeps_the_ledger_under_the_root(
    site: Site,
) -> None:
    config = site.config(
        placement=True, extra_ledger_cells={WorkloadClass.RESEARCH: site.root / "research-ledger"}
    )
    ctx = _ctx(config)

    await stage_1_is.execute(ctx, config, WORKLOAD)

    assert ctx.verified_state_root is not None
    assert ctx.verified_state_root.realpath == site.root.resolve()
    assert ctx.ledger_writer is not None
    assert _inside(ctx.ledger_writer.handle.canonical_path, site.root)  # pyright: ignore[reportUnknownMemberType]


@pytest.mark.asyncio
async def test_transient_worktrees_index_and_pid_do_not_move_into_the_state_root(
    site: Site,
) -> None:
    config = site.config(placement=True)
    ctx = _ctx(config)

    await stage_1_is.execute(ctx, config, WORKLOAD)

    assert transient_worktree_base(site.repo) == site.repo / ".harness" / "worktrees"
    assert not (site.root / "index.json").exists()
    assert not (site.root / "worktrees").exists()
    assert not (site.root / "runtime.pid").exists()
    assert not _inside(site.repo / ".harness" / "worktrees", site.root)


@pytest.mark.asyncio
async def test_without_placement_stage_1_is_unchanged_and_creates_no_state_root(
    site: Site,
) -> None:
    legacy_ledger = site.repo / ".harness" / "onboarding" / "state-ledger"
    config = site.config(placement=False, ledger=legacy_ledger)
    ctx = _ctx(config)

    await stage_1_is.execute(ctx, config, WORKLOAD)

    assert ctx.verified_state_root is None
    assert not site.root.exists()
    assert ctx.ledger_writer is not None
    assert _inside(ctx.ledger_writer.handle.canonical_path, legacy_ledger)  # pyright: ignore[reportUnknownMemberType]


# --- factories derive through the one verified stamp -------------------------------------


def _fernet_env(monkeypatch: pytest.MonkeyPatch, config: RuntimeConfig) -> None:
    monkeypatch.setenv(config.protected_result_store_key_env_var, Fernet.generate_key().decode())


def test_protected_result_store_is_rooted_under_the_verified_root(
    site: Site, monkeypatch: pytest.MonkeyPatch
) -> None:
    config = site.config(placement=True)
    _fernet_env(monkeypatch, config)
    stamp = site.stamp(config)

    store = materialize_protected_result_store_stage(config, stamp)

    assert store is not None
    assert store._root == stamp.realpath / "protected-results"  # pyright: ignore[reportPrivateUsage]


def test_a_declared_placement_without_a_stamp_never_falls_back_to_the_checkout(
    site: Site, monkeypatch: pytest.MonkeyPatch
) -> None:
    config = site.config(placement=True)
    _fernet_env(monkeypatch, config)
    before = site.snapshot()

    with pytest.raises(StateRootPlacementError) as excinfo:
        materialize_protected_result_store_stage(config, None)

    assert excinfo.value.reason is Refusal.UNVERIFIED_PLACEMENT
    assert site.snapshot() == before


def test_without_placement_the_protected_result_store_keeps_its_legacy_path(
    site: Site, monkeypatch: pytest.MonkeyPatch
) -> None:
    config = site.config(placement=False)
    _fernet_env(monkeypatch, config)

    store = materialize_protected_result_store_stage(config)

    assert store is not None
    assert store._root == (site.repo / ".harness" / "protected-results").resolve()  # pyright: ignore[reportPrivateUsage]


def test_inspect_derives_the_same_protected_result_root_as_its_factory(
    site: Site, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    from harness_runtime.admin import inspect as inspect_module
    from harness_runtime.lifecycle import protected_result_store as store_module

    config = site.config(placement=True)
    _fernet_env(monkeypatch, config)
    stamp = site.stamp(config)
    factory_store = materialize_protected_result_store_stage(config, stamp)
    assert factory_store is not None
    seen: list[Path] = []
    monkeypatch.setattr(
        store_module, "read_protected_result_store_snapshot", lambda root: seen.append(root)
    )
    monkeypatch.setattr(
        "harness_runtime.config_source.RuntimeConfigSource.load",
        classmethod(lambda cls, **_k: config),
    )

    inspect_module._read_protected_result_store_if_engaged(  # pyright: ignore[reportPrivateUsage]
        argparse.Namespace(runtime_config=None)
    )

    assert [p.resolve() for p in seen] == [factory_store._root]  # pyright: ignore[reportPrivateUsage]


def test_inspect_leaves_the_store_unresolvable_when_the_placement_cannot_be_verified(
    site: Site, monkeypatch: pytest.MonkeyPatch
) -> None:
    from harness_runtime.admin import inspect as inspect_module
    from harness_runtime.lifecycle import protected_result_store as store_module

    config = site.config(placement=True)  # root never bootstrapped: probe must refuse
    seen: list[Path] = []
    monkeypatch.setattr(
        store_module, "read_protected_result_store_snapshot", lambda root: seen.append(root)
    )
    monkeypatch.setattr(
        "harness_runtime.config_source.RuntimeConfigSource.load",
        classmethod(lambda cls, **_k: config),
    )
    before = site.snapshot()

    result = inspect_module._read_protected_result_store_if_engaged(  # pyright: ignore[reportPrivateUsage]
        argparse.Namespace(runtime_config=None)
    )

    assert result is None
    assert seen == []
    assert site.snapshot() == before


# --- memory: derived under the root; conflicting overrides refuse before any write --------


def test_memory_backends_are_derived_under_the_verified_root(site: Site) -> None:
    config = site.config(placement=True)
    stamp = site.stamp(config)

    fs = memory_factory._construct_backend(  # pyright: ignore[reportPrivateUsage]
        MemoryToolStorageBackend.FILESYSTEM, config, stamp
    )

    assert fs._root == stamp.realpath / "memories"  # pyright: ignore[reportPrivateUsage,reportUnknownMemberType,reportAttributeAccessIssue]


def test_the_default_sqlite_memory_path_is_under_the_verified_root(site: Site) -> None:
    config = site.config(
        placement=True,
        memory_tool_backend_config=MemoryToolBackendConfig(
            backend=MemoryToolStorageBackend.DATABASE
        ),
    )
    stamp = site.stamp(config)

    path = memory_factory._resolve_database_connection_path(  # pyright: ignore[reportPrivateUsage]
        config, stamp
    )

    assert path == stamp.realpath / "memories.db"


def test_a_database_connection_string_outside_the_root_refuses_before_any_write(
    site: Site,
) -> None:
    outside = site.home / "elsewhere" / "memories.db"
    config = site.config(
        placement=True,
        memory_tool_backend_config=MemoryToolBackendConfig(
            backend=MemoryToolStorageBackend.DATABASE,
            backend_params={"connection_string": str(outside)},
        ),
    )
    stamp = site.stamp(config)
    before = site.snapshot()

    with pytest.raises(StateRootPlacementError) as excinfo:
        memory_factory._construct_backend(  # pyright: ignore[reportPrivateUsage]
            MemoryToolStorageBackend.DATABASE, config, stamp
        )

    assert excinfo.value.reason is Refusal.PATH_OUTSIDE_ROOT
    assert site.snapshot() == before


@pytest.mark.asyncio
async def test_the_memory_registry_stage_uses_the_context_stamp(site: Site) -> None:
    config = site.config(placement=True)
    ctx = _ctx(config)
    ctx.verified_state_root = site.stamp(config)

    registry = await materialize_memory_tool_registry_stage(config, ctx)

    assert registry is not None
    assert not (site.repo / ".harness" / "memories").exists()


def test_automatic_memory_defaults_under_the_root_and_never_the_checkout(site: Site) -> None:
    from harness_runtime.automatic_memory import LocalAutomaticMemoryRuntime

    config = site.config(placement=True)
    stamp = site.stamp(config)

    LocalAutomaticMemoryRuntime(config=config, state_root=stamp)

    assert (stamp.realpath / "memory").is_dir()
    assert not (site.repo / ".harness" / "memory").exists()


def test_a_memory_root_override_outside_the_root_refuses_and_writes_nothing(site: Site) -> None:
    from harness_runtime.automatic_memory import LocalAutomaticMemoryRuntime
    from harness_runtime.types import RuntimeMemoryConfig

    outside = site.home / "elsewhere" / "mem"
    config = site.config(placement=True, memory=RuntimeMemoryConfig(root_path=outside))
    stamp = site.stamp(config)
    before = site.snapshot()

    with pytest.raises(StateRootPlacementError) as excinfo:
        LocalAutomaticMemoryRuntime(config=config, state_root=stamp)

    assert excinfo.value.reason is Refusal.PATH_OUTSIDE_ROOT
    assert site.snapshot() == before


def test_a_memory_root_override_inside_the_root_is_honoured(site: Site) -> None:
    from harness_runtime.automatic_memory import LocalAutomaticMemoryRuntime
    from harness_runtime.types import RuntimeMemoryConfig

    config = site.config(placement=True)
    stamp = site.stamp(config)
    inside = stamp.realpath / "custom-memory"
    config = site.config(placement=True, memory=RuntimeMemoryConfig(root_path=inside))

    LocalAutomaticMemoryRuntime(config=config, state_root=stamp)

    assert inside.is_dir()


def test_without_placement_a_memory_override_and_the_default_are_unchanged(site: Site) -> None:
    from harness_runtime.automatic_memory import LocalAutomaticMemoryRuntime
    from harness_runtime.types import RuntimeMemoryConfig

    custom = site.home / "anywhere" / "mem"
    LocalAutomaticMemoryRuntime(
        config=site.config(placement=False, memory=RuntimeMemoryConfig(root_path=custom))
    )
    LocalAutomaticMemoryRuntime(config=site.config(placement=False))

    assert custom.is_dir()
    assert (site.repo / ".harness" / "memory").is_dir()


# --- effect fence: both factories share the one derivation --------------------------------


def _spy_fence_dirs(monkeypatch: pytest.MonkeyPatch, *factory_modules: object) -> list[Path]:
    """Record the fence_dir of every `RuntimeEffectFence` the given factories construct."""
    from harness_runtime.lifecycle.effect_fence import RuntimeEffectFence

    made: list[Path] = []

    class _Spy(RuntimeEffectFence):
        def __init__(self, *, fence_dir: Path) -> None:
            made.append(fence_dir)
            super().__init__(fence_dir=fence_dir)

    for module in factory_modules:
        monkeypatch.setattr(module, "RuntimeEffectFence", _Spy)
    return made


@pytest.mark.asyncio
async def test_the_tool_dispatcher_effect_fence_is_under_the_verified_root(
    site: Site, monkeypatch: pytest.MonkeyPatch
) -> None:
    from harness_runtime.bootstrap.factories import runtime_tool_dispatcher_factory as factory
    from harness_runtime.bootstrap.factories.runtime_tool_dispatcher_factory import (
        materialize_runtime_tool_dispatcher_stage,
    )

    from .test_u_rt_75_runtime_tool_dispatcher_factory import _post_stage_3a_builder

    config = site.config(placement=True)
    stamp = site.stamp(config)
    builder = await _post_stage_3a_builder(config)
    builder.verified_state_root = stamp
    made = _spy_fence_dirs(monkeypatch, factory)

    await materialize_runtime_tool_dispatcher_stage(builder, config)

    assert made == [stamp.realpath / "effect-fence"]
    assert not (site.repo / ".harness" / "effect-fence").exists()


@pytest.mark.asyncio
async def test_the_tool_dispatcher_refuses_a_declared_placement_without_a_stamp(
    site: Site,
) -> None:
    from harness_runtime.bootstrap.factories.runtime_tool_dispatcher_factory import (
        materialize_runtime_tool_dispatcher_stage,
    )

    from .test_u_rt_75_runtime_tool_dispatcher_factory import _post_stage_3a_builder

    config = site.config(placement=True)
    builder = await _post_stage_3a_builder(config)

    with pytest.raises(StateRootPlacementError) as excinfo:
        await materialize_runtime_tool_dispatcher_stage(builder, config)

    assert excinfo.value.reason is Refusal.UNVERIFIED_PLACEMENT


@pytest.mark.asyncio
async def test_without_placement_the_tool_dispatcher_fence_keeps_its_legacy_path(
    site: Site, monkeypatch: pytest.MonkeyPatch
) -> None:
    from harness_runtime.bootstrap.factories import runtime_tool_dispatcher_factory as factory
    from harness_runtime.bootstrap.factories.runtime_tool_dispatcher_factory import (
        materialize_runtime_tool_dispatcher_stage,
    )

    from .test_u_rt_75_runtime_tool_dispatcher_factory import _post_stage_3a_builder

    config = site.config(placement=False)
    builder = await _post_stage_3a_builder(config)
    made = _spy_fence_dirs(monkeypatch, factory)

    await materialize_runtime_tool_dispatcher_stage(builder, config)

    assert made == [site.repo / ".harness" / "effect-fence"]


@pytest.mark.asyncio
async def test_the_managed_agents_effect_fence_is_under_the_verified_root(
    site: Site, monkeypatch: pytest.MonkeyPatch
) -> None:
    from harness_runtime.bootstrap.factories import managed_agents_dispatcher_factory as factory
    from harness_runtime.bootstrap.factories.managed_agents_dispatcher_factory import (
        materialize_managed_agents_dispatcher_stage,
    )
    from harness_runtime.types import ManagedAgentsConfig

    from .test_lifecycle_managed_agents_dispatch import _FakeClient, _tracer_provider

    config = site.config(
        placement=True,
        managed_agents_config=ManagedAgentsConfig(client=_FakeClient(retrieve_statuses=[])),
    ).model_copy(update={"deployment_surface": DeploymentSurface.MANAGED_CLOUD})
    ctx = _ctx(config)
    ctx.tracer_provider = _tracer_provider()[0]

    with pytest.raises(StateRootPlacementError) as excinfo:
        await materialize_managed_agents_dispatcher_stage(config, ctx)
    assert excinfo.value.reason is Refusal.UNVERIFIED_PLACEMENT

    ctx.verified_state_root = site.stamp(config)
    made = _spy_fence_dirs(monkeypatch, factory)
    await materialize_managed_agents_dispatcher_stage(config, ctx)

    assert made == [ctx.verified_state_root.realpath / "effect-fence"]


@pytest.mark.parametrize("stamped", [True, False])
def test_engine_recovery_journals_follow_the_placement(
    site: Site, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, stamped: bool
) -> None:
    from harness_runtime.bootstrap.factories import r_cxa_2_producer_loop_factory as factory

    from .test_r_cxa_2_producer_loop_factory import _post_tool_dispatcher_context

    ctx, config, _ask, _tools = _post_tool_dispatcher_context(tmp_path, [])
    config = config.model_copy(
        update={"state_placement": StatePlacementConfig(state_root=site.root)}
    )
    dirs: dict[str, Path] = {}

    def _spy(name: str, real: type) -> type:
        class _Spy(real):  # type: ignore[valid-type,misc]
            def __init__(self, *, journal_dir: Path, **kwargs: Any) -> None:
                dirs[name] = journal_dir
                super().__init__(journal_dir=journal_dir, **kwargs)

        return _Spy

    monkeypatch.setattr(
        factory,
        "WALSegmentEnginePauseResumeSubstrate",
        _spy("wal", factory.WALSegmentEnginePauseResumeSubstrate),
    )
    monkeypatch.setattr(
        factory,
        "ReconcilerEnginePauseResumeSubstrate",
        _spy("reconciler", factory.ReconcilerEnginePauseResumeSubstrate),
    )
    if not stamped:
        with pytest.raises(StateRootPlacementError) as excinfo:
            factory.materialize_r_cxa_2_producer_loop_stage(ctx, config)
        assert excinfo.value.reason is Refusal.UNVERIFIED_PLACEMENT
        assert dirs == {}
        return
    stamp = bootstrap_state_root(
        config.state_placement,  # type: ignore[arg-type]
        repository_root=tmp_path,
        worktree_base=transient_worktree_base(tmp_path),
        path_bindings=PathBindingConfig(),
        filesystem_type=lambda _p: "ext4",
    )
    ctx.verified_state_root = stamp

    factory.materialize_r_cxa_2_producer_loop_stage(ctx, config)

    assert dirs == {
        "wal": stamp.realpath / "engine-recovery-segments",
        "reconciler": stamp.realpath / "engine-recovery-reconciler",
    }


def test_without_placement_engine_recovery_journals_keep_their_legacy_paths(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from harness_runtime.bootstrap.factories import r_cxa_2_producer_loop_factory as factory

    from .test_r_cxa_2_producer_loop_factory import _post_tool_dispatcher_context

    ctx, config, _ask, _tools = _post_tool_dispatcher_context(tmp_path, [])
    dirs: list[Path] = []
    real = factory.WALSegmentEnginePauseResumeSubstrate

    class _Spy(real):
        def __init__(self, *, journal_dir: Path, **kwargs: Any) -> None:
            dirs.append(journal_dir)
            super().__init__(journal_dir=journal_dir, **kwargs)

    monkeypatch.setattr(factory, "WALSegmentEnginePauseResumeSubstrate", _Spy)

    factory.materialize_r_cxa_2_producer_loop_stage(ctx, config)

    assert dirs == [tmp_path / ".harness" / "engine-recovery-segments"]


# --- inventory guard: no persistent store keeps a repo-local literal ----------------------

_SRC = Path(__file__).resolve().parents[1] / "src" / "harness_runtime"
_PERSISTENT_JOIN = re.compile(
    r"repository_root\s*/\s*(\"\.harness\"|'\.harness'|MEMORY_TOOL_\w+|PROTECTED_RESULT_\w+)"
)
# Files allowed to build a checkout-local .harness path: the legacy derivation itself, the
# transient worktree/index stage, and the runtime pidfile (transient, never persistent state).
_ALLOWED_LITERAL_FILES = {
    "config/state_placement.py",
    "bootstrap/stage_1_is.py",
    "admin/pidfile.py",
}


def test_no_persistent_store_factory_keeps_an_old_repo_local_literal() -> None:
    offenders = sorted(
        f"{path.relative_to(_SRC)}:{match.group(0)}"
        for path in _SRC.rglob("*.py")
        if str(path.relative_to(_SRC)) not in _ALLOWED_LITERAL_FILES
        for match in _PERSISTENT_JOIN.finditer(path.read_text())
    )

    assert offenders == []
