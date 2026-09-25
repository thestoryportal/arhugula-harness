"""Provider-free contract checks for the local Ollama onboarding examples."""

from __future__ import annotations

import asyncio
import os
import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, cast

import pytest
from harness_core import DeploymentSurface, WorkloadClass
from harness_cp.cp_shared_types import ProviderAgnosticPayload
from harness_cp.topology_pattern import TopologyPattern
from harness_cp.workflow_driver import execute_workflow
from harness_cp.workflow_driver_types import RunStatus, StepKind
from harness_is.path_class_registry import PathClass
from harness_is.path_resolver import PathResolver
from harness_is.state_ledger_entry_schema import Actor, ActorClass
from harness_runtime.config.path_bindings import build_path_binding
from harness_runtime.config_source import RuntimeConfigSource
from harness_runtime.lifecycle.inter_step_output_channel import InterStepOutputChannel
from harness_runtime.lifecycle.llm_dispatch import RuntimeLLMDispatcher
from harness_runtime.lifecycle.sync_dispatcher_facade import SyncDispatcherFacade
from harness_runtime.lifecycle.workflow_manifest_loader import (
    LoadedWorkflow,
    WorkflowManifestLoader,
)
from opentelemetry.sdk.trace import TracerProvider

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


def _local_only_violations(workflow: LoadedWorkflow) -> list[str]:
    """Every way a loaded workflow could route a step off local Ollama.

    [LAW:single-enforcer] One predicate for the whole routing surface: the default
    binding, the fallback chain, and the per-step override map (a hosted per-step
    override would otherwise bypass the other two checks).
    """
    found: list[str] = []
    binding = workflow.default_model_binding
    if (binding.provider, binding.model) != ("ollama", "llama3.2:3b"):
        found.append(f"default binding {binding.provider}/{binding.model}")
    chain = workflow.manifest_entry.fallback_chain
    if (chain.primary.provider, chain.primary.model) != ("ollama", "llama3.2:3b"):
        found.append(f"primary {chain.primary.provider}/{chain.primary.model}")
    if chain.same_family or chain.cross_family:
        found.append("nonempty fallback chain")
    if workflow.manifest_entry.per_step_overrides:
        found.append("per_step_overrides")
    return found


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

    assert _local_only_violations(workflow) == []


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

    for name, config in (
        ("ollama-parallelization.toml", "harness.toml"),
        ("ollama-decentralized-handoff.toml", "harness.handoff.toml"),
    ):
        assert f"uv run --no-sync harness run examples/{name} --config {config}" in readme
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


@pytest.mark.parametrize("relative_path", [p.values[0] for p in _TOPOLOGY_EXAMPLES])
def test_a_hosted_per_step_override_is_detected_as_non_local(
    relative_path: str, tmp_path: Path
) -> None:
    text = (ROOT / relative_path).read_text()
    step = "branch-overview" if "parallelization" in relative_path else "stage-review"
    hosted = (
        f'per_step_overrides = {{ "{step}" = {{ step_id = "{step}", '
        'model_binding = { provider = "anthropic", model = "claude-haiku-4-5" } } }'
    )
    mutated = tmp_path / "hosted.toml"
    mutated.write_text(text.replace("per_step_overrides = {}", hosted))

    workflow = WorkflowManifestLoader.load_workflow(mutated)

    assert _local_only_violations(workflow) == ["per_step_overrides"]


_HANDOFF_CONFIG = "examples/ollama.handoff.local.toml.example"


def test_handoff_config_differs_from_the_shared_local_config_only_by_data_flow() -> None:
    # [LAW:one-source-of-truth] The handoff config is the shared config plus one flag;
    # any other divergence is drift this test refuses.
    shared = tomllib.loads((ROOT / "examples/ollama.local.toml.example").read_text())
    handoff = tomllib.loads((ROOT / _HANDOFF_CONFIG).read_text())

    assert handoff["runtime"].pop("inter_step_data_flow") is True
    assert "inter_step_data_flow" not in shared["runtime"]
    assert handoff == shared


class _OllamaReply:
    def __init__(self, text: str) -> None:
        self._dump = {"model": "llama3.2:3b", "message": {"role": "assistant", "content": text}}
        self.prompt_eval_count = 1
        self.eval_count = 1

    def model_dump(self) -> dict[str, Any]:
        return self._dump


@dataclass
class _RecordingOllamaClient:
    """Provider-free stand-in for the Ollama chat client: records what would be sent."""

    replies: list[_OllamaReply]
    calls: list[dict[str, Any]] = field(default_factory=lambda: [])

    async def chat(self, **kwargs: Any) -> _OllamaReply:
        self.calls.append({**kwargs, "messages": list(kwargs["messages"])})
        return self.replies.pop(0)


@dataclass
class _OllamaAdapter:
    client: _RecordingOllamaClient


class _LedgerDouble:
    def __init__(self) -> None:
        self.actor = Actor(actor_class=ActorClass.AGENT, actor_id="local-ollama-example")
        self.appends: list[Any] = []

    def append(self, payload: Any, write_key: Any) -> str:
        self.appends.append((payload, write_key))
        return "appended"

    @property
    def is_genesis(self) -> bool:
        return not self.appends

    @property
    def entry_count(self) -> int:
        return len(self.appends)


class _EmitterDouble:
    def emit(self, event_class: Any) -> None:
        return None


class _InferenceRegistry:
    def __init__(self, facade: SyncDispatcherFacade) -> None:
        self._facade = facade

    def lookup(self, step_kind: StepKind) -> Any:
        assert step_kind is StepKind.INFERENCE_STEP
        return self._facade


_UPSTREAM_LABEL = "Upstream step output:"


def _run_handoff_and_record_provider_messages(
    config_path: Path, tmp_path: Path
) -> list[list[dict[str, Any]]]:
    """Run the handoff example through the real loader, CP driver and LLM dispatcher,
    with the inter-step channel exactly as the given config's flag would bind it."""
    config_text = config_path.read_text().replace("/absolute/path/to/your/workspace", str(tmp_path))
    config_file = tmp_path / "harness.toml"
    config_file.write_text(config_text)
    config = RuntimeConfigSource.load(config_file=config_file)
    workflow = WorkflowManifestLoader.load_workflow(
        ROOT / "examples/ollama-decentralized-handoff.toml"
    )
    # Bootstrap binds a channel iff the flag is set; the dispatcher and driver share it.
    channel = InterStepOutputChannel() if config.inter_step_data_flow else None
    client = _RecordingOllamaClient(
        replies=[_OllamaReply(f"OUTPUT_OF_{step.step_id}") for step in workflow.steps]
    )

    async def _run() -> RunStatus:
        tracer_provider = TracerProvider()
        dispatcher = RuntimeLLMDispatcher(
            providers={"ollama": _OllamaAdapter(client)},
            tracer_provider=tracer_provider,
            inter_step_channel=channel,
        )
        facade = SyncDispatcherFacade(
            inner=dispatcher, loop=asyncio.get_running_loop(), result_timeout_seconds=30.0
        )
        ctx = type("_HandoffCtx", (), {})()
        ctx.ledger_writer = _LedgerDouble()
        ctx.lifecycle_emitter = _EmitterDouble()
        ctx.drained_flag = asyncio.Event()
        ctx.pause_requested_flag = asyncio.Event()
        ctx.pause_resume_protocol = None
        ctx.ledger_reader = None
        ctx.tracer_provider = tracer_provider
        ctx.validator_framework = None
        ctx.tenant_id = None
        ctx.inter_step_output_channel = channel
        result = await asyncio.to_thread(
            execute_workflow,
            workflow.manifest_entry,
            list(workflow.steps),
            run_id="run-local-handoff-example",
            ctx=cast(Any, ctx),
            default_model_binding=workflow.default_model_binding,
            step_dispatchers=cast(Any, _InferenceRegistry(facade)),
        )
        return result.status

    assert asyncio.run(_run()) is RunStatus.SUCCESS
    return [call["messages"] for call in client.calls]


def _contents(messages: list[dict[str, Any]]) -> str:
    return "\n".join(m["content"] for m in messages)


def test_documented_handoff_config_carries_prior_stage_output_into_later_stages(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    for name in list(os.environ):
        if name.startswith("HARNESS_"):
            monkeypatch.delenv(name)

    sent = _run_handoff_and_record_provider_messages(ROOT / _HANDOFF_CONFIG, tmp_path)

    assert len(sent) == 3
    assert _UPSTREAM_LABEL not in _contents(sent[0])
    # Each later stage receives exactly the immediately-prior stage's output, and
    # still carries its own prompt after it.
    assert sent[1][0]["content"].startswith(_UPSTREAM_LABEL)
    assert "OUTPUT_OF_stage-draft" in sent[1][0]["content"]
    assert sent[2][0]["content"].startswith(_UPSTREAM_LABEL)
    assert "OUTPUT_OF_stage-review" in sent[2][0]["content"]
    workflow = WorkflowManifestLoader.load_workflow(
        ROOT / "examples/ollama-decentralized-handoff.toml"
    )
    for stage_index in (1, 2):
        own_prompt = workflow.steps[stage_index].step_payload["messages"][0]
        assert own_prompt in sent[stage_index]


def test_shared_local_config_leaves_handoff_stages_without_upstream_output(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Negative control: the shared config's default keeps the channel off, which is
    # why the handoff needs its own documented config.
    for name in list(os.environ):
        if name.startswith("HARNESS_"):
            monkeypatch.delenv(name)

    sent = _run_handoff_and_record_provider_messages(
        ROOT / "examples/ollama.local.toml.example", tmp_path
    )

    assert all(_UPSTREAM_LABEL not in _contents(messages) for messages in sent)


def test_handoff_review_and_finalize_prompts_act_on_the_upstream_output() -> None:
    workflow = WorkflowManifestLoader.load_workflow(
        ROOT / "examples/ollama-decentralized-handoff.toml"
    )
    prompts = {step.step_id: step.step_payload["messages"][0]["content"] for step in workflow.steps}

    assert "upstream output" in prompts["stage-review"]
    assert "upstream output" in prompts["stage-finalize"]
    assert "DONE" not in prompts["stage-finalize"]


def test_parallelization_manifest_keeps_peer_branches_independent_of_upstream_output() -> None:
    # Peers must not read each other's output, so the parallel example keeps using the
    # shared config whose channel is off.
    workflow = WorkflowManifestLoader.load_workflow(ROOT / "examples/ollama-parallelization.toml")

    assert all(
        "upstream" not in step.step_payload["messages"][0]["content"] for step in workflow.steps
    )
