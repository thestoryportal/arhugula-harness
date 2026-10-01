"""Provider-free contract checks for the A7 examples: three local topology manifests and
the offline-embedding Omarchy profile.

Every check loads the SHIPPED file through the loader the CLI uses, and the behaviour
checks drive the real CP driver and Runtime LLM dispatcher with a recording stand-in for
the Ollama client. No model, daemon or network is used; a live run of these examples on
an installed candidate remains a separate, unwitnessed acceptance.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import os
import subprocess
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, cast

import pytest
from harness_core import DeploymentSurface, WorkloadClass
from harness_cp.cp_shared_types import ProviderAgnosticPayload
from harness_cp.per_workload_class_topology import is_topology_permitted_for_workload
from harness_cp.sub_agent_brief import SubAgentBrief, compute_brief_summary_hash
from harness_cp.topology_pattern import TopologyPattern
from harness_cp.workflow_driver import execute_workflow
from harness_cp.workflow_driver_types import RunStatus, StepKind
from harness_cp.workflow_manifest_entry import WorkflowManifestEntry
from harness_is.path_class_registry import PathClass
from harness_is.path_resolver import PathResolver
from harness_runtime.config.path_bindings import build_path_binding
from harness_runtime.config_source import RuntimeConfigSource
from harness_runtime.lifecycle.embedding_resolution import (
    MODEL_FILES,
    EmbeddingModelError,
    routing_corpus,
    verify_local_embedding,
)
from harness_runtime.lifecycle.evaluator_verdict import read_ollama_evaluator_verdict
from harness_runtime.lifecycle.inter_step_output_channel import InterStepOutputChannel
from harness_runtime.lifecycle.llm_dispatch import RuntimeLLMDispatcher
from harness_runtime.lifecycle.post_join_synthesis_dispatch import (
    POST_JOIN_SYNTHESIS_SIBLINGS_PREFIX,
    PostJoinSynthesisStepDispatcher,
    post_join_tool_binding_violations,
)
from harness_runtime.lifecycle.sync_dispatcher_facade import SyncDispatcherFacade
from harness_runtime.lifecycle.workflow_manifest_loader import (
    LoadedWorkflow,
    WorkflowManifestLoader,
)
from harness_runtime.types import RuntimeConfig
from opentelemetry.sdk.trace import TracerProvider

from .test_local_ollama_examples import (
    _EmitterDouble,
    _LedgerDouble,
    _local_only_violations,
    _OllamaAdapter,
)

ROOT = Path(__file__).resolve().parents[2]
README = ROOT / "examples/README.md"
SHARED_CONFIG = "examples/ollama.local.toml.example"
HANDOFF_CONFIG = "examples/ollama.handoff.local.toml.example"
EMBEDDING_CONFIG = "examples/omarchy.offline-embedding.toml.example"

_PLACEHOLDERS = {
    "/absolute/path/to/your/workspace": "workspace",
    "/absolute/path/to/your/state-root": "state-root",
    "/absolute/path/to/your/models": "models",
    "/absolute/path/to/your/embedding-cache": "embedding-cache",
}


@pytest.fixture(autouse=True)
def _no_harness_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in list(os.environ):
        if name.startswith("HARNESS_"):
            monkeypatch.delenv(name)


def _readme_bindings(workload: WorkloadClass) -> str:
    """The README's documented path-binding block for one workload class."""
    for block in README.read_text().split("```toml\n")[1:]:
        body = block.split("```", 1)[0]
        if f'workflow_class = "{workload.value}"' in body:
            return body
    raise AssertionError(f"README documents no {workload.value} path bindings")


def _load_config(example: str, tmp_path: Path, extra: WorkloadClass | None = None) -> RuntimeConfig:
    """Load a shipped config as an operator would: the README block spliced in ahead of
    `[runtime.routing_manifest]` (bindings are array-of-tables), placeholders replaced."""
    text = (ROOT / example).read_text()
    if extra is not None:
        head, tail = text.split("[runtime.routing_manifest]", 1)
        text = head + _readme_bindings(extra) + "\n[runtime.routing_manifest]" + tail
    for placeholder, name in _PLACEHOLDERS.items():
        text = text.replace(placeholder, str(tmp_path / name))
    config_file = tmp_path / "harness.toml"
    config_file.write_text(text)
    return RuntimeConfigSource.load(config_file=config_file)


# --- the three topology manifests: one contract, each example a value -------------------


@dataclass(frozen=True)
class _Example:
    path: str
    workflow_id: str
    workload: WorkloadClass
    topology: TopologyPattern
    step_kinds: tuple[StepKind, ...]
    config: str
    inter_step_data_flow: bool


_INFER, _SYNTH = StepKind.INFERENCE_STEP, StepKind.POST_JOIN_SYNTHESIS
_EXAMPLES = (
    _Example(
        "examples/ollama-evaluator-optimizer.toml",
        "example-ollama-evaluator-optimizer",
        WorkloadClass.CONTENT_CREATION,
        TopologyPattern.EVALUATOR_OPTIMIZER,
        (_INFER, _INFER),
        HANDOFF_CONFIG,
        True,
    ),
    _Example(
        "examples/ollama-orchestrator-workers.toml",
        "example-ollama-orchestrator-workers",
        WorkloadClass.RESEARCH,
        TopologyPattern.ORCHESTRATOR_WORKERS,
        (_INFER, _INFER, _INFER, _SYNTH),
        SHARED_CONFIG,
        False,
    ),
    _Example(
        "examples/ollama-hierarchical-delegation.toml",
        "example-ollama-hierarchical-delegation",
        WorkloadClass.RESEARCH,
        TopologyPattern.HIERARCHICAL_DELEGATION,
        (_INFER, _INFER, StepKind.SUB_AGENT_DISPATCH, _SYNTH),
        SHARED_CONFIG,
        False,
    ),
)
_IDS = [example.topology.value for example in _EXAMPLES]


def _load(example: _Example) -> LoadedWorkflow:
    return WorkflowManifestLoader.load_workflow(ROOT / example.path)


@pytest.mark.parametrize("example", _EXAMPLES, ids=_IDS)
def test_topology_example_loads_as_an_admissible_local_workflow(example: _Example) -> None:
    workflow = _load(example)

    assert workflow.workflow_id == example.workflow_id
    assert workflow.workload_class is example.workload
    assert workflow.manifest_entry.topology_pattern is example.topology
    assert is_topology_permitted_for_workload(example.topology, example.workload)
    assert tuple(step.step_kind for step in workflow.steps) == example.step_kinds
    assert _local_only_violations(workflow) == []
    for step in workflow.steps:
        if step.step_kind is _INFER:
            payload = ProviderAgnosticPayload.model_validate(step.step_payload)
            assert payload.messages and payload.tools == ()


@pytest.mark.parametrize("example", _EXAMPLES, ids=_IDS)
def test_documented_config_resolves_every_path_for_the_example(
    example: _Example, tmp_path: Path
) -> None:
    config = _load_config(example.config, tmp_path, extra=example.workload)

    assert config.inter_step_data_flow is example.inter_step_data_flow
    resolver = PathResolver(build_path_binding(config.path_bindings))
    for path_class in PathClass:
        path = resolver.resolve_path(
            path_class, example.workload, DeploymentSurface.LOCAL_DEVELOPMENT
        )
        assert path.is_relative_to(tmp_path)


_SYNTHESIZING = [e for e in _EXAMPLES if _SYNTH in e.step_kinds]


@pytest.mark.parametrize("example", _SYNTHESIZING, ids=[e.topology.value for e in _SYNTHESIZING])
def test_the_synthesis_step_is_terminal_and_effect_free(example: _Example) -> None:
    synthesis = _load(example).steps[-1]

    assert synthesis.step_kind is _SYNTH
    payload = synthesis.step_payload
    assert post_join_tool_binding_violations(payload.get("tools"), payload.get("params")) == []
    assert "messages" not in payload["params"]


def test_the_evaluator_requests_exactly_the_verdict_shape() -> None:
    evaluator = _load(_EXAMPLES[0]).steps[1]
    schema = evaluator.step_payload["params"]["format"]

    assert set(schema["properties"]) == {"accepted", "feedback"}
    assert schema["additionalProperties"] is False
    assert schema["properties"]["accepted"]["type"] == "boolean"


def test_the_delegated_child_is_a_bounded_local_hierarchy_with_a_canonical_brief() -> None:
    workflow = _load(_EXAMPLES[2])
    children = [s for s in workflow.steps[1:] if s.step_kind is not _SYNTH]
    dispatch = next(s for s in workflow.steps if s.step_kind is StepKind.SUB_AGENT_DISPATCH)
    payload = dispatch.step_payload
    child = WorkflowManifestEntry.model_validate(payload["child_manifest_entry"])
    brief = SubAgentBrief.model_validate(payload["brief"])

    assert len(children) <= 3
    assert child.topology_pattern is TopologyPattern.HIERARCHICAL_DELEGATION
    assert is_topology_permitted_for_workload(child.topology_pattern, child.workload_class)
    assert (child.fallback_chain.primary.provider, child.fallback_chain.primary.model) == (
        "ollama",
        "llama3.2:3b",
    )
    assert not child.fallback_chain.same_family and not child.fallback_chain.cross_family
    assert 2 <= len(payload["child_steps"]) <= 4
    for step in payload["child_steps"]:
        assert ProviderAgnosticPayload.model_validate(step["step_payload"]).tools == ()
    assert compute_brief_summary_hash(brief) == brief.summary_hash


# --- provider-free behaviour through the real driver and dispatcher ---------------------


class _Reply:
    """An Ollama `ChatResponse` stand-in: a complete (`done`) assistant reply."""

    def __init__(self, text: str) -> None:
        self._dump = {
            "model": "llama3.2:3b",
            "done": True,
            "done_reason": "stop",
            "message": {"role": "assistant", "content": text},
        }
        self.prompt_eval_count = 1
        self.eval_count = 1

    def model_dump(self) -> dict[str, Any]:
        return self._dump


@dataclass
class _Client:
    """Answers each chat by asking `reply` for the text; records the messages it was sent."""

    reply: Callable[[list[dict[str, Any]]], str]
    calls: list[list[dict[str, Any]]] = field(default_factory=lambda: [])

    async def chat(self, **kwargs: Any) -> _Reply:
        messages = list(kwargs["messages"])
        self.calls.append(messages)
        return _Reply(self.reply(messages))


class _Registry:
    def __init__(self, dispatchers: dict[StepKind, Any]) -> None:
        self._dispatchers = dispatchers

    def lookup(self, step_kind: StepKind) -> Any:
        return self._dispatchers[step_kind]


def _run(example: _Example, client: _Client, tmp_path: Path) -> Any:
    """Run a shipped manifest through the real CP driver and Runtime LLM dispatcher, with
    the inter-step channel exactly as the example's documented config binds it."""
    config = _load_config(example.config, tmp_path, extra=example.workload)
    workflow = _load(example)
    channel = InterStepOutputChannel() if config.inter_step_data_flow else None

    async def _go() -> Any:
        tracer_provider = TracerProvider()
        dispatcher = RuntimeLLMDispatcher(
            providers={"ollama": _OllamaAdapter(client)},
            tracer_provider=tracer_provider,
            inter_step_channel=channel,
        )
        facade = SyncDispatcherFacade(
            inner=dispatcher, loop=asyncio.get_running_loop(), result_timeout_seconds=30.0
        )
        ctx = type("_ExampleCtx", (), {})()
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
        ctx.evaluator_verdict_reader = read_ollama_evaluator_verdict
        registry = _Registry(
            {_INFER: facade, _SYNTH: PostJoinSynthesisStepDispatcher(inner=facade)}
        )
        return await asyncio.to_thread(
            execute_workflow,
            workflow.manifest_entry,
            list(workflow.steps),
            run_id=f"run-{example.workflow_id}",
            ctx=cast(Any, ctx),
            default_model_binding=workflow.default_model_binding,
            step_dispatchers=cast(Any, registry),
        )

    return asyncio.run(_go())


def _text(messages: list[dict[str, Any]]) -> str:
    return "\n".join(str(m["content"]) for m in messages)


def _is_evaluation(messages: list[dict[str, Any]]) -> bool:
    return "Judge the tagline" in _text(messages)


def test_evaluator_optimizer_carries_draft_and_feedback_and_stops_on_accept(
    tmp_path: Path,
) -> None:
    verdicts = iter([False, True])

    def reply(messages: list[dict[str, Any]]) -> str:
        if _is_evaluation(messages):
            accepted = next(verdicts)
            return json.dumps({"accepted": accepted, "feedback": f"VERDICT-{accepted}"})
        return f"DRAFT-{sum(not _is_evaluation(c) for c in client.calls)}"

    client = _Client(reply)
    result = _run(_EXAMPLES[0], client, tmp_path)

    assert result.status is RunStatus.SUCCESS
    assert len(client.calls) == 4  # generate, evaluate (reject), regenerate, evaluate (accept)
    first_eval, regenerate, second_eval = client.calls[1], client.calls[2], client.calls[3]
    assert "DRAFT-1" in _text(first_eval)
    assert "VERDICT-False" in _text(regenerate)
    assert "DRAFT-2" in _text(second_eval)


def test_evaluator_optimizer_reaching_its_cap_completes_without_acceptance(
    tmp_path: Path,
) -> None:
    """`completed` is not `accepted`: at the three-iteration cap the run still succeeds."""

    def reply(messages: list[dict[str, Any]]) -> str:
        if _is_evaluation(messages):
            return json.dumps({"accepted": False, "feedback": "too long"})
        return "a tagline that never satisfies the evaluator"

    client = _Client(reply)
    result = _run(_EXAMPLES[0], client, tmp_path)

    assert result.status is RunStatus.SUCCESS
    assert len(client.calls) == 6
    assert result.final_state is not None and result.final_state["accepted"] is False


def test_orchestrator_workers_synthesis_receives_only_the_worker_outputs(
    tmp_path: Path,
) -> None:
    workflow = _load(_EXAMPLES[1])
    prompts = {
        str(step.step_payload["messages"][0]["content"]): str(step.step_id)
        for step in workflow.steps
    }

    def reply(messages: list[dict[str, Any]]) -> str:
        return f"OUT-{prompts.get(str(messages[0]['content']), 'synthesis')}"

    client = _Client(reply)
    result = _run(_EXAMPLES[1], client, tmp_path)

    assert result.status is RunStatus.SUCCESS
    synthesis = next(c for c in client.calls if POST_JOIN_SYNTHESIS_SIBLINGS_PREFIX in _text(c))
    siblings = json.loads(
        synthesis[-1]["content"].removeprefix(POST_JOIN_SYNTHESIS_SIBLINGS_PREFIX)
    )
    outputs = [json.dumps(entry["output"]) for entry in siblings]
    assert [entry["branch_index"] for entry in siblings] == [0, 1]
    assert "OUT-worker-benefits" in outputs[0] and "OUT-worker-costs" in outputs[1]
    assert "OUT-lead-plan" not in _text(synthesis)
    for worker in ("worker-benefits", "worker-costs"):
        sent = next(c for c in client.calls if prompts.get(str(c[0]["content"])) == worker)
        assert "OUT-lead-plan" not in _text(sent)


# --- the offline-embedding profile and the documented model directory -------------------


def test_offline_embedding_config_activates_l2_over_an_unbound_manifest(tmp_path: Path) -> None:
    config = _load_config(EMBEDDING_CONFIG, tmp_path)

    assert config.routing_activation is True
    assert config.embedding_model_dir == tmp_path / "models/bge-small-en-v1.5"
    assert config.embedding_cache_dir == tmp_path / "embedding-cache"
    assert not config.routing_manifest.per_role_bindings
    assert not config.routing_manifest.per_workload_overrides
    candidates = config.embedding_routing_candidates
    assert candidates is not None and set(candidates) == set(WorkloadClass)
    routing_corpus(candidates, set(config.enabled_provider_names))
    assert len(set(candidates.values())) >= 2


def _recipe_model(root: Path, *, sha256sum_args: tuple[str, ...] = ()) -> Path:
    """Lay out a synthetic model directory with the documented `sha256sum` recipe."""
    model = root / "bge-small-en-v1.5"
    model.mkdir(parents=True)
    for name in sorted(MODEL_FILES):
        (model / name).write_bytes(hashlib.sha256(name.encode()).digest())
    sums = subprocess.run(
        ["sha256sum", *sha256sum_args, *sorted(MODEL_FILES)],
        cwd=model,
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    (model / "SHA256SUMS").write_text(sums)
    return model


def test_the_documented_recipe_passes_the_verifier_and_creates_a_private_cache(
    tmp_path: Path,
) -> None:
    model = _recipe_model(tmp_path)
    cache = tmp_path / "embedding-cache"

    verified = verify_local_embedding(model, cache)

    assert verified.model_dir == model
    assert (cache.stat().st_mode & 0o777) == 0o700


def _extra_file(model: Path, cache: Path) -> None:
    (model / "README.md").write_text("x")


def _changed_file(model: Path, cache: Path) -> None:
    (model / "config.json").write_bytes(b"changed")


def _missing_manifest(model: Path, cache: Path) -> None:
    (model / "SHA256SUMS").unlink()


def _shared_cache(model: Path, cache: Path) -> None:
    cache.mkdir(mode=0o755)
    cache.chmod(0o755)


_REFUSALS: list[Any] = [
    pytest.param(_extra_file, "differ from SHA256SUMS", id="extra-file"),
    pytest.param(_changed_file, "SHA256 mismatch: config.json", id="changed-file"),
    pytest.param(_missing_manifest, "cannot be verified", id="missing-sha256sums"),
    pytest.param(_shared_cache, "private owned directory", id="group-readable-cache"),
]


@pytest.mark.parametrize(("mutate", "message"), _REFUSALS)
def test_the_verifier_refuses_a_broken_model_directory(
    tmp_path: Path, mutate: Callable[[Path, Path], None], message: str
) -> None:
    model = _recipe_model(tmp_path)
    cache = tmp_path / "embedding-cache"
    mutate(model, cache)

    with pytest.raises(EmbeddingModelError, match=message):
        verify_local_embedding(model, cache)


def test_the_verifier_refuses_a_missing_cache_parent(tmp_path: Path) -> None:
    model = _recipe_model(tmp_path)

    with pytest.raises(EmbeddingModelError, match="cannot be verified"):
        verify_local_embedding(model, tmp_path / "absent" / "embedding-cache")


def test_the_verifier_refuses_a_missing_model_directory(tmp_path: Path) -> None:
    with pytest.raises(EmbeddingModelError, match="cannot be verified"):
        verify_local_embedding(tmp_path / "absent-model", tmp_path / "embedding-cache")


def test_the_verifier_refuses_binary_mode_sha256sum_entries(tmp_path: Path) -> None:
    model = _recipe_model(tmp_path, sha256sum_args=("-b",))

    with pytest.raises(EmbeddingModelError, match="malformed embedding SHA256SUMS entry"):
        verify_local_embedding(model, tmp_path / "embedding-cache")


def test_the_verifier_accepts_an_additional_listed_file(tmp_path: Path) -> None:
    """The five files are the minimum; any further file must exist and be listed."""
    model = _recipe_model(tmp_path)
    (model / "README.md").write_text("provenance note\n")
    digest = hashlib.sha256(b"provenance note\n").hexdigest()
    with (model / "SHA256SUMS").open("a") as sums:
        sums.write(f"{digest}  README.md\n")

    assert verify_local_embedding(model, tmp_path / "embedding-cache").model_dir == model
