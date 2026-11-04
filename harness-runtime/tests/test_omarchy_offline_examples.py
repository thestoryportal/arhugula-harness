"""Provider-free contract checks for three local topology manifests in examples/README.md
and the offline-embedding Omarchy profile (docs/operations/omarchy-offline-embedding.md).

The manifest and config checks load the SHIPPED file through the loader the CLI uses, and
one compares the raw TOML of the offline-embedding and Ollama profiles; the model-directory
checks lay the model out with the guide's own step-3 shell block, except one that refuses
a directory that does not exist; and the behaviour checks drive the real CP driver and Runtime LLM dispatcher with a recording stand-in for the
Ollama client. No model, daemon or network is used; a live run of these examples on
an installed candidate remains a separate, unwitnessed acceptance.
"""

from __future__ import annotations

import asyncio
import copy
import hashlib
import json
import os
import subprocess
import tomllib
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, cast

import pytest
from harness_core import DeploymentSurface, WorkloadClass
from harness_cp.cp_shared_types import ProviderAgnosticPayload
from harness_cp.per_workload_class_topology import is_topology_permitted_for_workload
from harness_cp.sub_agent_brief import compute_brief_summary_hash
from harness_cp.topology_pattern import TopologyPattern
from harness_cp.workflow_driver import execute_workflow
from harness_cp.workflow_driver_types import RunStatus, StepKind
from harness_is.path_class_registry import PathClass
from harness_is.path_resolver import PathResolver
from harness_runtime.api import RunResult
from harness_runtime.api import run as api_run
from harness_runtime.bootstrap import stage_3a_cp_clients, stage_4_od
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
from harness_runtime.lifecycle.providers import OllamaAdapter, ProviderClientsStage
from harness_runtime.lifecycle.sub_agent_dispatch import SubAgentDispatchPayload
from harness_runtime.lifecycle.sync_dispatcher_facade import SyncDispatcherFacade
from harness_runtime.lifecycle.workflow_manifest_loader import (
    LoadedWorkflow,
    WorkflowManifestLoader,
)
from harness_runtime.types import RuntimeConfig
from opentelemetry.sdk.trace import TracerProvider
from pydantic import ValidationError

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
OFFLINE_EMBEDDING_GUIDE = ROOT / "docs/operations/omarchy-offline-embedding.md"
DOWNLOADED_FILES = "/absolute/path/to/the/five/downloaded/files"

_PLACEHOLDERS = {
    "/absolute/path/to/your/workspace": "workspace",
    "/absolute/path/to/your/state-root": "state-root",
    "/absolute/path/to/your/models": "models",
    "/absolute/path/to/your/embedding-cache": "embedding-cache",
    DOWNLOADED_FILES: "downloaded",
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


# The strict object `read_ollama_evaluator_verdict` accepts: both fields always present.
_VERDICT_SCHEMA = {
    "type": "object",
    "properties": {"accepted": {"type": "boolean"}, "feedback": {"type": "string"}},
    "required": ["accepted", "feedback"],
    "additionalProperties": False,
}


def test_the_evaluator_requests_exactly_the_verdict_shape() -> None:
    evaluator = _load(_EXAMPLES[0]).steps[1]
    schema = evaluator.step_payload["params"]["format"]

    assert schema == _VERDICT_SCHEMA


def _dispatch_payload(workflow: LoadedWorkflow) -> SubAgentDispatchPayload:
    """The shipped dispatch payload, parsed by the model the production dispatcher uses."""
    dispatch = next(s for s in workflow.steps if s.step_kind is StepKind.SUB_AGENT_DISPATCH)
    return SubAgentDispatchPayload.model_validate(dispatch.step_payload)


def test_the_delegated_child_is_a_bounded_local_hierarchy_with_a_canonical_brief() -> None:
    workflow = _load(_EXAMPLES[2])
    children = [s for s in workflow.steps[1:] if s.step_kind is not _SYNTH]
    payload = _dispatch_payload(workflow)
    child, brief = payload.child_manifest_entry, payload.brief

    assert len(children) <= 3
    assert payload.child_workflow_id == child.workflow_id
    assert child.topology_pattern is TopologyPattern.HIERARCHICAL_DELEGATION
    assert is_topology_permitted_for_workload(child.topology_pattern, child.workload_class)
    assert (child.fallback_chain.primary.provider, child.fallback_chain.primary.model) == (
        "ollama",
        "llama3.2:3b",
    )
    assert not child.fallback_chain.same_family and not child.fallback_chain.cross_family
    assert 2 <= len(payload.child_steps) <= 4
    for step in payload.child_steps:
        assert step.step_kind is _INFER
        assert ProviderAgnosticPayload.model_validate(step.step_payload).tools == ()
    assert compute_brief_summary_hash(brief) == brief.summary_hash


_BROKEN_DISPATCH: list[Any] = [
    pytest.param(lambda p: p.pop("child_workflow_id"), id="no-child-workflow-id"),
    pytest.param(lambda p: p.update(stray=True), id="stray-key"),
    pytest.param(lambda p: p["child_steps"][0].update(step_kind="bogus"), id="bad-child-kind"),
]


@pytest.mark.parametrize("mutate", _BROKEN_DISPATCH)
def test_the_dispatch_payload_check_refuses_what_the_dispatcher_refuses(
    mutate: Callable[[dict[str, Any]], object],
) -> None:
    """Negative control: the parse above is the production gate, so a payload the
    dispatcher would fail with RT-FAIL-PAYLOAD-SHAPE fails it too."""
    workflow = _load(_EXAMPLES[2])
    dispatch = next(s for s in workflow.steps if s.step_kind is StepKind.SUB_AGENT_DISPATCH)
    payload = copy.deepcopy(dict(dispatch.step_payload))
    mutate(payload)

    with pytest.raises(ValidationError):
        SubAgentDispatchPayload.model_validate(payload)


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
    """Answers each chat by asking `reply` for the text; records the messages it was sent
    and the structured-output `format` each chat requested (None when it requested none)."""

    reply: Callable[[list[dict[str, Any]]], str]
    calls: list[list[dict[str, Any]]] = field(default_factory=lambda: [])
    formats: list[Any] = field(default_factory=lambda: [])

    async def chat(self, **kwargs: Any) -> _Reply:
        messages = list(kwargs["messages"])
        self.calls.append(messages)
        self.formats.append(kwargs.get("format"))
        return _Reply(self.reply(messages))

    async def close(self) -> None:
        return None


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
    evaluated = [_is_evaluation(c) for c in client.calls]
    assert client.formats == [_VERDICT_SCHEMA if e else None for e in evaluated]


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


@pytest.mark.parametrize(
    "verdict",
    [
        '{"accepted": true, "feedback": "ok", "score": 9}',
        '{"accepted": "true", "feedback": "ok"}',
        '{"accepted": true, "feedback": "o',
    ],
    ids=["extra-key", "quoted-boolean", "cut-off"],
)
def test_evaluator_optimizer_fails_on_a_reply_that_is_not_the_verdict_object(
    verdict: str, tmp_path: Path
) -> None:
    """The README's promise: a reply that is not exactly the verdict object fails the run."""

    def reply(messages: list[dict[str, Any]]) -> str:
        return verdict if _is_evaluation(messages) else "a tagline"

    client = _Client(reply)
    result = _run(_EXAMPLES[0], client, tmp_path)

    assert result.status is RunStatus.FAILED
    assert "evaluator-optimizer-verdict-malformed" in result.fail_class
    assert len(client.calls) == 2  # the first evaluation ends the run; nothing regenerates


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


class _Collector:
    async def start(self) -> None:
        return None

    async def stop(self, *, timeout_seconds: float = 5.0) -> None:
        return None


def _run_as_the_cli_does(
    example: _Example, client: _Client, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> RunResult:
    """Run a shipped manifest the way `harness run` does: the documented config and the
    manifest loader feed `api.run`, whose bootstrap builds the production dispatcher
    registry, sub-agent dispatcher and child-workflow runner. Only the Ollama client and
    the OD collector/tracer stages are in-process stand-ins."""
    config = _load_config(example.config, tmp_path, extra=example.workload)

    async def _unreachable_ping() -> None:
        raise AssertionError("stage 3a is replaced, so nothing pings the stand-in")

    async def _clients(*_args: object, **_kwargs: object) -> ProviderClientsStage:
        adapter = OllamaAdapter(client=cast(Any, client), ping=_unreachable_ping)
        return ProviderClientsStage(providers={"ollama": adapter})

    collector = type("_CollectorStage", (), {"daemon": _Collector()})()
    tracer = type(
        "_TracerStage", (), {"provider": TracerProvider(), "registered_globally": False}
    )()
    monkeypatch.setattr(stage_3a_cp_clients, "materialize_provider_clients_stage", _clients)
    monkeypatch.setattr(stage_4_od, "materialize_collector_daemon_stage", lambda c, **_: collector)
    monkeypatch.setattr(stage_4_od, "materialize_ring_buffer_stage", lambda c, _d: None)
    monkeypatch.setattr(stage_4_od, "materialize_tracer_provider_stage", lambda c, **_: tracer)
    monkeypatch.setattr(stage_4_od, "materialize_span_processor_stage", lambda c, _p, **_k: None)
    return asyncio.run(api_run(_load(example), config=config))


def test_hierarchical_delegation_runs_the_child_hierarchy_through_the_production_path(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    workflow = _load(_EXAMPLES[2])
    root_steps = [s for s in workflow.steps if s.step_kind is _INFER]
    child_steps = list(_dispatch_payload(workflow).child_steps)
    prompts = {
        str(step.step_payload["messages"][0]["content"]): str(step.step_id)
        for step in (*root_steps, *child_steps)
    }

    def reply(messages: list[dict[str, Any]]) -> str:
        return f"OUT-{prompts.get(str(messages[0]['content']), 'synthesis')}"

    client = _Client(reply)
    result = _run_as_the_cli_does(_EXAMPLES[2], client, tmp_path, monkeypatch)

    assert result.status == "completed", result.failure_cause
    sent = [prompts.get(str(c[0]["content"]), "synthesis") for c in client.calls]
    root = [str(s.step_id) for s in root_steps] + ["synthesis"]
    child = [str(s.step_id) for s in child_steps]
    assert sorted(sent) == sorted(root + child)  # one call per declared root and child step
    synthesis = next(c for c in client.calls if POST_JOIN_SYNTHESIS_SIBLINGS_PREFIX in _text(c))
    worker, delegated = json.loads(
        synthesis[-1]["content"].removeprefix(POST_JOIN_SYNTHESIS_SIBLINGS_PREFIX)
    )
    assert worker["output"]["message"]["content"] == "OUT-root-worker-hardware"
    # The delegated child contributes its own lead-plus-workers aggregate.
    assert delegated["output"]["orchestrator"]["message"]["content"] == f"OUT-{child[0]}"
    assert {
        step: output["message"]["content"]
        for step, output in delegated["output"]["worker_outputs"].items()
    } == {step: f"OUT-{step}" for step in child[1:]}


# --- the offline-embedding profile and the documented model directory -------------------


def test_offline_embedding_profile_is_the_ollama_profile_plus_four_routing_keys() -> None:
    """Pins the header's claim: removing the four routing keys leaves the Ollama profile."""
    # [LAW:one-source-of-truth] the Ollama profile is the original; this one must not drift.
    offline = tomllib.loads((ROOT / EMBEDDING_CONFIG).read_text())
    ollama = tomllib.loads((ROOT / "examples/omarchy.ollama.toml.example").read_text())
    routing_keys = (
        "routing_activation",
        "embedding_routing_candidates",
        "embedding_model_dir",
        "embedding_cache_dir",
    )

    for key in routing_keys:
        assert key not in ollama["runtime"]
        del offline["runtime"][key]

    assert offline == ollama


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


def _step_3_recipe() -> str:
    """The shell block of the guide's step 3, exactly as an operator copies it."""
    section = OFFLINE_EMBEDDING_GUIDE.read_text().split("\n## 3. ", 1)[1].split("\n## ", 1)[0]
    return section.split("```sh\n", 1)[1].split("```", 1)[0]


def _recipe_model(root: Path, recipe: str | None = None) -> Path:
    """Run the step-3 recipe (default: the documented one) with `sh -e` over five synthetic
    downloaded files, its placeholders replaced; return the model directory it laid out.
    The recipe also creates the cache at `root / "embedding-cache"`."""
    downloaded = root / _PLACEHOLDERS[DOWNLOADED_FILES]
    downloaded.mkdir()
    for name in MODEL_FILES:
        (downloaded / name).write_bytes(hashlib.sha256(name.encode()).digest())
    script = _step_3_recipe() if recipe is None else recipe
    for placeholder, name in _PLACEHOLDERS.items():
        script = script.replace(placeholder, str(root / name))
    assert "/absolute/path/" not in script, "the recipe has a placeholder this test cannot fill"
    subprocess.run(["sh", "-e", "-c", script], cwd=root, check=True, capture_output=True)
    return root / "models/bge-small-en-v1.5"


def test_the_documented_recipe_passes_the_verifier_and_creates_a_private_cache(
    tmp_path: Path,
) -> None:
    model = _recipe_model(tmp_path)
    cache = tmp_path / "embedding-cache"

    verified = verify_local_embedding(model, cache)

    assert verified.model_dir == model
    assert (cache.stat().st_mode & 0o777) == 0o700


def _edited_recipe(old: str, new: str) -> str:
    recipe = _step_3_recipe()
    assert recipe.count(old) == 1, f"the step-3 recipe no longer contains {old!r} once"
    return recipe.replace(old, new)


# Edits a reader could make to the documented recipe; each must stop the operator before
# bootstrap does. Dropping a file from `cp` fails the recipe itself at `sha256sum`.
_HASHED = "sha256sum config.json model_optimized.onnx special_tokens_map.json"
_BROKEN_RECIPES: list[Any] = [
    pytest.param(
        (_HASHED + " tokenizer.json tokenizer_config.json", _HASHED + " tokenizer.json"),
        "does not cover the pinned model files",
        id="file-dropped-from-sha256sum",
    ),
    pytest.param(
        ("sha256sum config.json", "sha256sum -b config.json"),
        "malformed embedding SHA256SUMS entry",
        id="binary-mode-sha256sum",
    ),
]


@pytest.mark.parametrize(("edit", "message"), _BROKEN_RECIPES)
def test_the_verifier_refuses_a_model_laid_out_by_an_edited_recipe(
    tmp_path: Path, edit: tuple[str, str], message: str
) -> None:
    model = _recipe_model(tmp_path, _edited_recipe(*edit))

    with pytest.raises(EmbeddingModelError, match=message):
        verify_local_embedding(model, tmp_path / "embedding-cache")


def test_a_file_dropped_from_the_recipe_copy_fails_the_recipe(tmp_path: Path) -> None:
    recipe = _edited_recipe(
        " tokenizer_config.json special_tokens_map.json", " special_tokens_map.json"
    )

    with pytest.raises(subprocess.CalledProcessError):
        _recipe_model(tmp_path, recipe)


def _extra_file(model: Path, cache: Path) -> None:
    (model / "README.md").write_text("x")


def _changed_file(model: Path, cache: Path) -> None:
    (model / "config.json").write_bytes(b"changed")


def _missing_manifest(model: Path, cache: Path) -> None:
    (model / "SHA256SUMS").unlink()


def _shared_cache(model: Path, cache: Path) -> None:
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


def test_the_verifier_accepts_an_additional_listed_file(tmp_path: Path) -> None:
    """The five files are the minimum; any further file must exist and be listed."""
    model = _recipe_model(tmp_path)
    (model / "README.md").write_text("provenance note\n")
    digest = hashlib.sha256(b"provenance note\n").hexdigest()
    with (model / "SHA256SUMS").open("a") as sums:
        sums.write(f"{digest}  README.md\n")

    assert verify_local_embedding(model, tmp_path / "embedding-cache").model_dir == model
