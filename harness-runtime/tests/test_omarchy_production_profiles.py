"""S4 — the Omarchy production profile examples, judged by the real loader and verifier.

Provider-free and host-free: each profile is materialised into a scratch checkout, loaded
through `RuntimeConfigSource`, and placed by `bootstrap_state_root` with an injected
filesystem type. This proves the shipped files declare a verifiable external placement. It
is NOT installed-host, restore-scope, CLI-output or launch acceptance (S5 and later gates).
"""

from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass
from pathlib import Path

import pytest
from harness_core import DeploymentSurface, WorkloadClass
from harness_is.path_class_registry import PathClass
from harness_runtime.config.path_bindings import build_path_binding
from harness_runtime.config.state_placement import (
    StatePlacementRefusal,
    StateRootPlacementError,
    bootstrap_state_root,
    transient_worktree_base,
)
from harness_runtime.config_source import RuntimeConfigSource
from harness_runtime.types import RuntimeConfig

from .test_state_placement import world  # noqa: F401  (fixture: scratch dir with no .git above)

ROOT = Path(__file__).resolve().parents[2]
WORKSPACE_PLACEHOLDER = "/absolute/path/to/your/workspace"
STATE_ROOT_PLACEHOLDER = "/absolute/path/to/your/state-root"
Refusal = StatePlacementRefusal


@dataclass(frozen=True)
class Profile:
    file: str
    providers: tuple[str, ...]
    cli_kinds: tuple[str, ...]


PROFILES = (
    Profile("examples/omarchy.ollama.toml.example", ("ollama",), ()),
    Profile("examples/omarchy.claude-code.toml.example", ("claude_code",), ("claude-code",)),
    Profile("examples/omarchy.codex.toml.example", ("codex",), ("codex",)),
)
PROFILE_IDS = [Path(p.file).name for p in PROFILES]
LEGACY_EXAMPLES = (
    "examples/ollama.local.toml.example",
    "examples/ollama.handoff.local.toml.example",
)
HOSTED_PROVIDERS = frozenset({"anthropic", "openai", "gemini", "antigravity", "e2b"})


class Site:
    """A fake checkout beside a home whose `state` parent is a safe 0700 directory."""

    def __init__(self, base: Path) -> None:
        self.repo = base / "repo"
        (self.repo / ".git").mkdir(parents=True)
        (self.repo / ".harness").mkdir()
        self.home = base / "home"
        self.home.mkdir(mode=0o755)
        (self.home / "state").mkdir(mode=0o700)
        self.root = self.home / "state" / "root"

    def load(
        self,
        profile: Profile,
        *,
        state_root: Path | str | None = None,
        monkeypatch: pytest.MonkeyPatch,
    ) -> RuntimeConfig:
        for name in list(os.environ):
            if name.startswith("HARNESS_"):
                monkeypatch.delenv(name)
        text = (ROOT / profile.file).read_text()
        text = text.replace(WORKSPACE_PLACEHOLDER, str(self.repo))
        text = text.replace(STATE_ROOT_PLACEHOLDER, str(state_root or self.root))
        config_file = self.repo.parent / "harness.toml"
        config_file.write_text(text)
        return RuntimeConfigSource.load(config_file=config_file)

    def place(self, config: RuntimeConfig, fs: str = "ext4") -> Path:
        assert config.state_placement is not None
        stamp = bootstrap_state_root(
            config.state_placement,
            repository_root=self.repo,
            worktree_base=transient_worktree_base(self.repo),
            path_bindings=config.path_bindings,
            filesystem_type=lambda _p: fs,
        )
        return stamp.realpath


@pytest.fixture
def site(world: Path) -> Site:  # noqa: F811
    return Site(world / "site")


def _ledger_cells(config: RuntimeConfig) -> list[Path]:
    return [
        Path(e.path)
        for e in build_path_binding(config.path_bindings).entries
        if e.path_class is PathClass.STATE_LEDGER
    ]


# --- each profile loads and is placed ---------------------------------------------------


@pytest.mark.parametrize("profile", PROFILES, ids=PROFILE_IDS)
def test_a_profile_loads_declares_placement_and_places_its_ledger_under_the_root(
    site: Site, profile: Profile, monkeypatch: pytest.MonkeyPatch
) -> None:
    config = site.load(profile, monkeypatch=monkeypatch)

    assert config.deployment_surface is DeploymentSurface.LOCAL_DEVELOPMENT
    assert config.state_placement is not None
    assert config.state_placement.state_root == site.root
    cells = _ledger_cells(config)
    assert cells
    assert all(c.is_relative_to(site.root) and c != site.root for c in cells)

    placed = site.place(config)

    assert placed == site.root.resolve()
    assert site.root.is_dir()
    assert (site.root.stat().st_mode & 0o077) == 0


@pytest.mark.parametrize("profile", PROFILES, ids=PROFILE_IDS)
def test_a_profile_routes_only_through_its_local_or_subscription_provider(
    site: Site, profile: Profile, monkeypatch: pytest.MonkeyPatch
) -> None:
    config = site.load(profile, monkeypatch=monkeypatch)

    assert config.enabled_provider_names == profile.providers
    assert tuple(p.kind for p in config.external_cli_providers) == profile.cli_kinds
    assert not HOSTED_PROVIDERS & set(config.enabled_provider_names)
    chains = config.routing_manifest.fallback_chains
    assert [c.primary.provider for c in chains] == list(profile.providers)
    assert all(not c.same_family and not c.cross_family for c in chains)
    assert config.mcp_clients == []
    assert config.memory.enabled is False


# --- refusals the profile must inherit from the verifier --------------------------------


@pytest.mark.parametrize("profile", PROFILES, ids=PROFILE_IDS)
def test_a_root_inside_the_checkout_is_refused(
    site: Site, profile: Profile, monkeypatch: pytest.MonkeyPatch
) -> None:
    config = site.load(
        profile, state_root=site.repo / ".harness" / "state", monkeypatch=monkeypatch
    )

    with pytest.raises(StateRootPlacementError) as excinfo:
        site.place(config)

    assert excinfo.value.reason is Refusal.INSIDE_CHECKOUT
    assert not (site.repo / ".harness" / "state").exists()


@pytest.mark.parametrize("profile", PROFILES, ids=PROFILE_IDS)
def test_a_volatile_filesystem_is_refused(
    site: Site, profile: Profile, monkeypatch: pytest.MonkeyPatch
) -> None:
    config = site.load(profile, monkeypatch=monkeypatch)

    with pytest.raises(StateRootPlacementError) as excinfo:
        site.place(config, fs="tmpfs")

    assert excinfo.value.reason is Refusal.NON_DURABLE_FS
    assert not site.root.exists()


@pytest.mark.parametrize("profile", PROFILES, ids=PROFILE_IDS)
def test_non_empty_legacy_checkout_state_is_refused_not_copied(
    site: Site, profile: Profile, monkeypatch: pytest.MonkeyPatch
) -> None:
    legacy = site.repo / ".harness" / "onboarding" / "state-ledger"
    legacy.mkdir(parents=True)
    (legacy / "state.jsonl").write_text("{}\n")
    config = site.load(profile, monkeypatch=monkeypatch)

    with pytest.raises(StateRootPlacementError) as excinfo:
        site.place(config)

    assert excinfo.value.reason is Refusal.LEGACY_STATE_PRESENT
    assert not site.root.exists()
    assert (legacy / "state.jsonl").read_text() == "{}\n"


@pytest.mark.parametrize("profile", PROFILES, ids=PROFILE_IDS)
def test_a_root_whose_parent_is_missing_is_refused_and_creates_nothing(
    site: Site, profile: Profile, monkeypatch: pytest.MonkeyPatch
) -> None:
    missing_parent = site.home / "not-created"
    config = site.load(profile, state_root=missing_parent / "root", monkeypatch=monkeypatch)

    with pytest.raises(StateRootPlacementError) as excinfo:
        site.place(config)

    assert excinfo.value.reason is Refusal.PARENT_MISSING
    assert not missing_parent.exists()


@pytest.mark.parametrize("profile", PROFILES, ids=PROFILE_IDS)
def test_an_unedited_state_root_placeholder_is_refused(
    site: Site, profile: Profile, monkeypatch: pytest.MonkeyPatch
) -> None:
    config = site.load(profile, state_root=STATE_ROOT_PLACEHOLDER, monkeypatch=monkeypatch)

    with pytest.raises(StateRootPlacementError) as excinfo:
        site.place(config)

    assert excinfo.value.reason is Refusal.PARENT_MISSING


# --- what the profile files must not carry ----------------------------------------------


@pytest.mark.parametrize("profile", PROFILES, ids=PROFILE_IDS)
def test_a_profile_ships_no_host_path_expansion_or_durable_resume(profile: Profile) -> None:
    text = (ROOT / profile.file).read_text()
    parsed = tomllib.loads(text)["runtime"]

    assert "/home/" not in text
    assert "~" not in text
    assert "$" not in text
    assert "pause_resume_protocol_config" not in parsed
    assert "durable" not in text.replace("non-durable", "")
    assert parsed["state_placement"]["state_root"] == STATE_ROOT_PLACEHOLDER
    assert parsed["state_placement"]["forbidden_roots"] == []


def test_the_codex_profile_declares_itself_held_for_the_read_exposure_boundary() -> None:
    header = (ROOT / "examples/omarchy.codex.toml.example").read_text().splitlines()[:20]

    assert any("HELD" in line and "read" in line.lower() for line in header)


# --- legacy examples stay non-durable ---------------------------------------------------


@pytest.mark.parametrize("relative", LEGACY_EXAMPLES)
def test_legacy_examples_still_load_without_a_placement(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, relative: str
) -> None:
    for name in list(os.environ):
        if name.startswith("HARNESS_"):
            monkeypatch.delenv(name)
    config_file = tmp_path / "harness.toml"
    config_file.write_text(
        (ROOT / relative).read_text().replace(WORKSPACE_PLACEHOLDER, str(tmp_path))
    )

    assert RuntimeConfigSource.load(config_file=config_file).state_placement is None


def test_the_workload_bound_for_the_ledger_is_the_one_the_profiles_serve() -> None:
    # Guards the ledger-cell assertions above: they only mean something for a workload
    # the profile actually binds.
    for profile in PROFILES:
        entries = tomllib.loads((ROOT / profile.file).read_text())["runtime"]["path_bindings"][
            "raw_entries"
        ]
        ledger = [e for e in entries if e["path_class"] == PathClass.STATE_LEDGER.value]
        assert [e["workflow_class"] for e in ledger] == [WorkloadClass.PIPELINE_AUTOMATION.value]


# --- operator documentation -------------------------------------------------------------


def test_deploy_docs_give_the_operator_setup_and_state_the_limits() -> None:
    doc = (ROOT / "docs/how-to-deploy.md").read_text()

    for required in (
        "External state root (Omarchy production profile)",
        STATE_ROOT_PLACEHOLDER,
        "forbidden_roots",
        "0700",
        "legacy-state-present",
        "candidate, not accepted",
        "/home/robbo/.local/state/arhugula-harness",
        "omarchy.ollama.toml.example",
        "omarchy.claude-code.toml.example",
        "omarchy.codex.toml.example",
        "HELD",
        "durable",
    ):
        assert required in doc, required


def test_examples_readme_and_tutorial_flag_the_onboarding_state_as_non_durable() -> None:
    for relative in ("examples/README.md", "docs/tutorial-first-workflow.md"):
        text = (ROOT / relative).read_text()
        assert "non-durable" in text, relative
        assert "how-to-deploy.md" in text, relative
