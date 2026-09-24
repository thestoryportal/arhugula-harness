"""Provider-free contract checks for the local Ollama onboarding examples."""

from __future__ import annotations

import os
import tomllib
from pathlib import Path

import pytest
from harness_core import DeploymentSurface, WorkloadClass
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
