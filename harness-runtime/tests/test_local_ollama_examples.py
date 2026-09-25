"""Provider-free contract checks for the local Ollama onboarding examples."""

from __future__ import annotations

import os
import tomllib
from pathlib import Path

import pytest
from harness_core import DeploymentSurface, WorkloadClass
from harness_cp.cp_shared_types import ProviderAgnosticPayload
from harness_cp.topology_pattern import TopologyPattern
from harness_cp.workflow_driver_types import StepKind
from harness_is.path_class_registry import PathClass
from harness_is.path_resolver import PathResolver
from harness_runtime.config.path_bindings import build_path_binding
from harness_runtime.config_source import RuntimeConfigSource
from harness_runtime.lifecycle.workflow_manifest_loader import WorkflowManifestLoader

ROOT = Path(__file__).resolve().parents[2]


def test_local_ollama_examples_load_together(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # [LAW:behavior-not-structure] Use the same loaders as the one-shot CLI.
    for name in list(os.environ):
        if name.startswith("HARNESS_"):
            monkeypatch.delenv(name)
    example = (ROOT / "examples/ollama.local.toml.example").read_text()
    config_file = tmp_path / "harness.toml"
    config_file.write_text(example.replace("/absolute/path/to/your/workspace", str(tmp_path)))

    config = RuntimeConfigSource.load(config_file=config_file)
    workflow = WorkflowManifestLoader.load_workflow(ROOT / "examples/ollama-first.toml")

    assert config.repository_root == tmp_path
    assert config.enabled_provider_names == ("ollama",)
    assert config.external_cli_providers == ()
    assert config.ollama_optional is False
    assert config.mcp_clients == []
    assert config.memory.enabled is False
    assert workflow.workflow_id == "example-ollama-first"
    assert workflow.default_model_binding.provider == "ollama"
    assert workflow.default_model_binding.model == "llama3.2:3b"
    assert workflow.manifest_entry.fallback_chain.primary.provider == "ollama"
    assert workflow.manifest_entry.fallback_chain.same_family == ()
    assert workflow.manifest_entry.fallback_chain.cross_family == ()
    assert config.routing_manifest.fallback_chains[0].primary.provider == "ollama"
    assert len(config.routing_manifest.fallback_chains) == 1
    assert len(workflow.steps) == 1

    resolver = PathResolver(build_path_binding(config.path_bindings))
    for path_class in PathClass:
        path = resolver.resolve_path(
            path_class, WorkloadClass.PIPELINE_AUTOMATION, DeploymentSurface.LOCAL_DEVELOPMENT
        )
        assert path.is_relative_to(tmp_path)
        assert path.suffix != ".jsonl"
    ledger_dir = resolver.resolve_path(
        PathClass.STATE_LEDGER,
        WorkloadClass.PIPELINE_AUTOMATION,
        DeploymentSurface.LOCAL_DEVELOPMENT,
    )
    assert ledger_dir / "state.jsonl" == tmp_path / ".harness/onboarding/state-ledger/state.jsonl"


def test_generic_template_binds_state_ledger_directory() -> None:
    # [LAW:one-source-of-truth] The binding names the directory; stage 1 appends state.jsonl.
    data = tomllib.loads((ROOT / "harness.toml.example").read_text())
    entries = data["runtime"]["path_bindings"]["raw_entries"]
    ledger = next(entry for entry in entries if entry["path_class"] == "STATE_LEDGER")
    assert ledger["path"].endswith("/.harness/state-ledger")


# [LAW:one-type-per-behavior] One topology-manifest contract; each example is a value.
_TOPOLOGY_EXAMPLES = (
    pytest.param(
        "examples/ollama-parallelization.toml",
        "example-ollama-parallelization",
        WorkloadClass.RESEARCH,
        TopologyPattern.PARALLELIZATION,
        ("branch-overview", "branch-risks"),
        id="parallelization",
    ),
    pytest.param(
        "examples/ollama-decentralized-handoff.toml",
        "example-ollama-decentralized-handoff",
        WorkloadClass.PIPELINE_AUTOMATION,
        TopologyPattern.DECENTRALIZED_HANDOFF,
        ("stage-draft", "stage-review", "stage-finalize"),
        id="decentralized-handoff",
    ),
)


@pytest.mark.parametrize(
    ("relative_path", "workflow_id", "workload", "topology", "step_ids"), _TOPOLOGY_EXAMPLES
)
def test_topology_example_is_a_real_local_multi_step_workflow(
    relative_path: str,
    workflow_id: str,
    workload: WorkloadClass,
    topology: TopologyPattern,
    step_ids: tuple[str, ...],
) -> None:
    workflow = WorkflowManifestLoader.load_workflow(ROOT / relative_path)

    assert workflow.workflow_id == workflow_id
    assert workflow.workload_class is workload
    assert workflow.manifest_entry.topology_pattern is topology
    assert tuple(step.step_id for step in workflow.steps) == step_ids
    assert len(set(step_ids)) == len(step_ids)
    assert all(step.step_kind is StepKind.INFERENCE_STEP for step in workflow.steps)

    # [LAW:no-silent-failure] Local-only: the one binding is Ollama and nothing hosted can catch a fallback.
    chain = workflow.manifest_entry.fallback_chain
    assert (workflow.default_model_binding.provider, workflow.default_model_binding.model) == (
        "ollama",
        "llama3.2:3b",
    )
    assert (chain.primary.provider, chain.primary.model) == ("ollama", "llama3.2:3b")
    assert chain.same_family == ()
    assert chain.cross_family == ()


@pytest.mark.parametrize("relative_path", [p.values[0] for p in _TOPOLOGY_EXAMPLES])
def test_topology_example_payloads_are_valid_and_small(relative_path: str) -> None:
    workflow = WorkflowManifestLoader.load_workflow(ROOT / relative_path)

    for step in workflow.steps:
        payload = ProviderAgnosticPayload.model_validate(step.step_payload)
        assert payload.messages
        assert all(m["role"] == "user" and m["content"] for m in payload.messages)
        assert payload.tools == ()
        assert 0 < payload.params["options"]["num_predict"] <= 64


def test_readme_documents_topology_examples_and_their_open_witnesses() -> None:
    readme = (ROOT / "examples/README.md").read_text()

    for name in ("ollama-parallelization.toml", "ollama-decentralized-handoff.toml"):
        assert f"uv run --no-sync harness run examples/{name} --config harness.toml" in readme
    assert "not yet witnessed" in readme


def test_readme_research_path_bindings_let_the_local_config_resolve_parallelization(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # The shipped local config binds paths for pipeline-automation only, but
    # parallelization is admissible only for research/content-creation.
    for name in list(os.environ):
        if name.startswith("HARNESS_"):
            monkeypatch.delenv(name)
    readme = (ROOT / "examples/README.md").read_text()
    block = readme.split("```toml\n", 1)[1].split("```", 1)[0]
    base = (ROOT / "examples/ollama.local.toml.example").read_text()
    # Bindings are array-of-tables, so appending after routing tables would nest
    # them; splice them in ahead of [runtime.routing_manifest].
    head, tail = base.split("[runtime.routing_manifest]", 1)
    text = (head + block + "\n[runtime.routing_manifest]" + tail).replace(
        "/absolute/path/to/your/workspace", str(tmp_path)
    )
    config_file = tmp_path / "harness.toml"
    config_file.write_text(text)

    config = RuntimeConfigSource.load(config_file=config_file)
    resolver = PathResolver(build_path_binding(config.path_bindings))
    for path_class in PathClass:
        path = resolver.resolve_path(
            path_class, WorkloadClass.RESEARCH, DeploymentSurface.LOCAL_DEVELOPMENT
        )
        assert path.is_relative_to(tmp_path)
