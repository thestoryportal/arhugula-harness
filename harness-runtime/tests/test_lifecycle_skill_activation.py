"""Tests for C-RT-27 SkillActivationSpanEmitter + SkillActivationHook.

Per runtime spec v1.32 §14.17 + plan v2.28 L9-quindecies cluster
(U-RT-99/100/101). Closes H_T-AS-8d producer-site absence per
.harness/class_1_fork_as_8d_skill_activation_surface_absence.md Reading B
Q-set ratification.
"""

from __future__ import annotations

import asyncio
import subprocess
from dataclasses import replace
from functools import partial
from pathlib import Path
from typing import Any

import pytest
from harness_core import SkillID
from harness_cp.cp_shared_types import ModelBinding
from harness_cp.cross_family_fallback_chain import ProviderCandidate, ProviderFamily
from harness_cp.topology_pattern import TopologyPattern
from harness_cp.workflow_driver import execute_workflow
from harness_cp.workflow_driver_types import RunStatus
from harness_runtime.lifecycle.llm_dispatch import (
    PromptInjectionConflictError,
    RuntimeLLMDispatcher,
)
from harness_runtime.lifecycle.retry_breaker_fallback import RESERVED_LLM_DISPATCH_KEY
from harness_runtime.lifecycle.skill_activation import (
    SkillActivationEmitterStageMaterializeError,
    SkillActivationHook,
    SkillActivationHookConfig,
    SkillActivationMode,
    SkillActivationSpanEmitter,
    SkillSelectionInvalidError,
    SkillSelectionInvalidReason,
    UnknownSkillError,
    compose_system_prompt_with_skills,
    parse_skill_selection,
)
from harness_runtime.lifecycle.skills import (
    Skill,
    SkillManifest,
    compute_git_blob_sha,
    load_skills_from_dir,
)
from harness_runtime.lifecycle.state_ledger import materialize_state_ledger_reader
from harness_runtime.lifecycle.sync_dispatcher_facade import materialize_sync_dispatcher_facade
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

from .integration.test_b165_driver_through_composer_round_trip import _Ctx, _manifest, _Registry
from .test_lifecycle_llm_dispatch import (
    _AnthropicClient,
    _AnthropicFakeAdapter,
    _binding,
    _prompt_extension_memory_context,
    _step,
    _step_context,
)
from .test_lifecycle_skills import _write_manifest
from .test_post_tool_effect_cell10 import _transitions
from .test_post_tool_effect_replay import _provider_case, _Tools

# --- U-RT-99 carrier substrate tests -----------------------------------------


def test_skill_activation_mode_three_values_byte_exact() -> None:
    """AC #1: 3 enum members preserving AS spec v1.7 §14.4 Claude Code
    taxonomy verbatim."""
    assert SkillActivationMode.FRONTMATTER_ONLY.value == "frontmatter_only"
    assert SkillActivationMode.TOOL_SEARCH.value == "tool_search"
    assert SkillActivationMode.FILESYSTEM_READ.value == "filesystem_read"
    assert len(list(SkillActivationMode)) == 3


def test_skill_activation_hook_protocol_two_methods() -> None:
    """AC #2: Protocol has select_for_workflow_init + select_for_llm_dispatch.

    runtime_checkable Protocol enables isinstance() duck-typing.
    """

    class _Hook:
        def select_for_workflow_init(self, loaded_skills, workflow_id):
            return []

        def select_for_llm_dispatch(self, loaded_skills, workflow_id, step_index):
            return []

    assert isinstance(_Hook(), SkillActivationHook)


def test_skill_activation_hook_config_empty_marker_or_hook_supplied() -> None:
    """AC #3: SkillActivationHookConfig dataclass supports None and operator hook."""
    cfg_empty = SkillActivationHookConfig()
    assert cfg_empty.hook is None

    class _Hook:
        def select_for_workflow_init(self, loaded_skills, workflow_id):
            return []

        def select_for_llm_dispatch(self, loaded_skills, workflow_id, step_index):
            return []

    h = _Hook()
    cfg_with_hook = SkillActivationHookConfig(hook=h)
    assert cfg_with_hook.hook is h

    # Frozen — assignment raises
    with pytest.raises(Exception):
        cfg_empty.hook = h  # type: ignore[misc]


def test_skill_manifest_has_version_sha_and_body_tokens_fields() -> None:
    """AC #4 + #5: SkillManifest carries version_sha (str) + body_tokens (int)."""
    m = SkillManifest(
        skill_id=SkillID("test-skill"),
        name="Test",
        description="test description",
        version="1.0",
        version_sha="abc123",
        body_tokens=42,
    )
    assert m.version_sha == "abc123"
    assert m.body_tokens == 42


def test_compute_git_blob_sha_byte_exact_to_git_hash_object() -> None:
    """AC #5: compute_git_blob_sha is byte-exact-identical to
    `git hash-object <path>` output."""
    content = b"hello world\n"
    expected_sha = (
        subprocess.run(
            ["git", "hash-object", "--stdin"],
            input=content,
            capture_output=True,
            check=True,
        )
        .stdout.decode("ascii")
        .strip()
    )
    assert compute_git_blob_sha(content) == expected_sha


def test_load_skills_computes_version_sha_and_body_tokens(tmp_path: Path) -> None:
    """AC #5 + #6 at v1.139: version_sha + body_tokens derive from the
    `<stem>.SKILL.md` content bytes, not the manifest."""
    skills_dir = tmp_path / "skills"
    skills_dir.mkdir()
    manifest_file = skills_dir / "my-skill.skill.json"
    raw = '{"skill_id": "my-skill", "name": "test", "description": "hello world", "version": "1.0"}'
    manifest_file.write_text(raw)
    content_file = skills_dir / "my-skill.SKILL.md"
    content_file.write_text("skill body text\n")

    skills = load_skills_from_dir(skills_dir)
    skill = skills[SkillID("my-skill")]
    assert skill.manifest.version_sha == compute_git_blob_sha(content_file.read_bytes())
    # body_tokens = len("skill body text\n") // 4 = 4
    assert skill.manifest.body_tokens == 4


# --- U-RT-100 emitter tests --------------------------------------------------


class _FakeSpan:
    def __init__(self) -> None:
        self.attrs: dict[str, object] = {}

    def set_attribute(self, key, value) -> None:
        self.attrs[key] = value

    def __enter__(self):
        return self

    def __exit__(self, *a) -> None:
        return None


class _FakeTracer:
    def __init__(self) -> None:
        self.spans: list[_FakeSpan] = []

    def start_as_current_span(self, name):
        span = _FakeSpan()
        span.attrs["__span_name__"] = name
        self.spans.append(span)
        return span


class _FakeTracerProvider:
    def __init__(self) -> None:
        self.tracer = _FakeTracer()

    def get_tracer(self, name: str):
        return self.tracer


def _make_skill(skill_id: str = "my-skill", content: str = "body") -> Skill:
    manifest = SkillManifest(
        skill_id=SkillID(skill_id),
        name="My Skill",
        description="testing",
        version="1.0",
        version_sha=compute_git_blob_sha(content.encode()),
        body_tokens=len(content) // 4,
    )
    return Skill(manifest=manifest, source_path=Path("/tmp/fake.skill.json"), content=content)


def test_emitter_emit_opens_skill_activation_span_with_six_attrs() -> None:
    """AC #1: emit opens span named 'skill.activation' with all 6 attrs."""
    tp = _FakeTracerProvider()
    emitter = SkillActivationSpanEmitter(tracer_provider=tp)
    skill = _make_skill()

    emitter.emit(
        skill_id=skill.manifest.skill_id,
        mode=SkillActivationMode.TOOL_SEARCH,
        workflow_id="wf-1",
        skill=skill,
    )

    assert len(tp.tracer.spans) == 1
    span = tp.tracer.spans[0]
    assert span.attrs["__span_name__"] == "skill.activation"
    assert span.attrs["skill.id"] == "my-skill"
    assert span.attrs["skill.name"] == "My Skill"
    assert span.attrs["skill.version_sha"] == skill.manifest.version_sha
    assert span.attrs["skill.frontmatter.version"] == "1.0"
    assert span.attrs["skill.body_tokens"] == skill.manifest.body_tokens
    assert span.attrs["skill.activation_mode"] == "tool_search"
    assert span.attrs["workflow.id"] == "wf-1"


def test_emitter_accepts_string_literal_for_mode_cross_axis_boundary() -> None:
    """harness-cp passes mode as str literal ("frontmatter_only") to avoid
    importing SkillActivationMode (workspace dep-graph discipline)."""
    tp = _FakeTracerProvider()
    emitter = SkillActivationSpanEmitter(tracer_provider=tp)
    skill = _make_skill()
    emitter.emit(
        skill_id=skill.manifest.skill_id,
        mode="frontmatter_only",
        workflow_id="wf-1",
        skill=skill,
    )
    assert tp.tracer.spans[0].attrs["skill.activation_mode"] == "frontmatter_only"


# --- U-RT-100 factory tests --------------------------------------------------


@pytest.mark.asyncio
async def test_materialize_emitter_returns_none_when_config_none() -> None:
    """AC #2: opt-out short-circuit returns None."""
    from harness_runtime.bootstrap.factories.skill_activation_emitter_factory import (
        materialize_skill_activation_emitter_stage,
    )

    class _Cfg:
        skill_activation_hook_config = None

    class _Ctx:
        tracer_provider = _FakeTracerProvider()

    result = await materialize_skill_activation_emitter_stage(_Cfg(), _Ctx())
    assert result is None


@pytest.mark.asyncio
async def test_materialize_emitter_constructs_when_config_present() -> None:
    """AC #3: opt-in returns a bound emitter."""
    from harness_runtime.bootstrap.factories.skill_activation_emitter_factory import (
        materialize_skill_activation_emitter_stage,
    )

    class _Cfg:
        skill_activation_hook_config = SkillActivationHookConfig()

    class _Ctx:
        tracer_provider = _FakeTracerProvider()

    result = await materialize_skill_activation_emitter_stage(_Cfg(), _Ctx())
    assert isinstance(result, SkillActivationSpanEmitter)


@pytest.mark.asyncio
async def test_materialize_emitter_raises_on_tracer_provider_unbound() -> None:
    """AC #7: factory raises SkillActivationEmitterStageMaterializeError when
    tracer_provider is None."""
    from harness_runtime.bootstrap.factories.skill_activation_emitter_factory import (
        materialize_skill_activation_emitter_stage,
    )

    class _Cfg:
        skill_activation_hook_config = SkillActivationHookConfig()

    class _Ctx:
        tracer_provider = None

    with pytest.raises(SkillActivationEmitterStageMaterializeError):
        await materialize_skill_activation_emitter_stage(_Cfg(), _Ctx())


# --- U-RT-101 hook-3 (operator-explicit) tests -------------------------------


def test_activate_skill_silent_skip_when_emitter_unbound() -> None:
    """AC #4: HarnessContext.activate_skill silent-skips when
    skill_activation_emitter is None (operator opt-out)."""
    # Construct minimal HarnessContext-shaped object via duck-typing for unit
    # test. We don't need a full ctx — just the activate_skill method
    # behavior with None emitter.
    from harness_runtime.types import HarnessContext

    # The method's logic accesses self.skill_activation_emitter, self.skills,
    # raises UnknownSkillError if needed. We can test the silent-skip arm by
    # building a partial duck-typed object.
    class _PartialCtx:
        skill_activation_emitter = None
        skills: dict = {}
        activate_skill = HarnessContext.activate_skill

    # No exception, no side-effect
    _PartialCtx().activate_skill(SkillID("nonexistent"))


def test_activate_skill_raises_unknown_skill_error() -> None:
    """AC #5: activate_skill raises UnknownSkillError on unknown skill_id."""
    from harness_runtime.types import HarnessContext

    tp = _FakeTracerProvider()
    emitter = SkillActivationSpanEmitter(tracer_provider=tp)

    class _PartialCtx:
        skill_activation_emitter = emitter
        skills: dict = {}
        activate_skill = HarnessContext.activate_skill

    with pytest.raises(UnknownSkillError):
        _PartialCtx().activate_skill(SkillID("unknown"))


def test_activate_skill_emits_filesystem_read_span() -> None:
    """AC #3: HarnessContext.activate_skill emits one skill.activation span
    with activation_mode = filesystem_read."""
    from harness_runtime.types import HarnessContext

    tp = _FakeTracerProvider()
    emitter = SkillActivationSpanEmitter(tracer_provider=tp)
    skill = _make_skill("my-skill")

    class _PartialCtx:
        skill_activation_emitter = emitter
        skills = {SkillID("my-skill"): skill}
        activate_skill = HarnessContext.activate_skill

    _PartialCtx().activate_skill(SkillID("my-skill"), workflow_id="wf-99")
    assert len(tp.tracer.spans) == 1
    assert tp.tracer.spans[0].attrs["skill.activation_mode"] == "filesystem_read"
    assert tp.tracer.spans[0].attrs["workflow.id"] == "wf-99"


# --- U-RT-101 hook-2 (per-LLM-dispatch) tests --------------------------------


def test_dispatcher_emits_tool_search_span_when_hook_returns_skill() -> None:
    """AC #1: per-LLM-dispatch hook emits one span per selected skill with
    activation_mode = tool_search."""
    from harness_runtime.lifecycle.llm_dispatch import RuntimeLLMDispatcher

    tp = _FakeTracerProvider()
    emitter = SkillActivationSpanEmitter(
        tracer_provider=tp,
        hook=_HookSelectingAllForLLM(),
    )
    skill = _make_skill("my-skill")
    skills_map = {SkillID("my-skill"): skill}

    # Build dispatcher with no providers (we'll invoke just the hook block).
    # Hook firing is at start of dispatch() BEFORE provider resolution; we'll
    # raise ProviderUnreachable after the hook fires to short-circuit.
    dispatcher = RuntimeLLMDispatcher(
        providers={},
        tracer_provider=tp,
        skill_activation_emitter=emitter,
        skills=skills_map,
    )

    # Invoke dispatch — provider resolution will fail, but hook fires first.
    import asyncio

    # The hook only needs step_context.workflow_id + step_context.step_index;
    # we use a duck-typed object instead of a full StepExecutionContext.

    class _SC:
        workflow_id = "wf-llm-1"
        step_index = 7

    class _Binding:
        class model_binding:
            provider = "nonexistent"
            model = "x"

    class _Step:
        step_payload = None

    with pytest.raises(Exception):
        asyncio.run(dispatcher.dispatch(_Binding(), _Step(), step_context=_SC()))

    # Hook fired before exception — span should be emitted
    skill_spans = [s for s in tp.tracer.spans if s.attrs.get("__span_name__") == "skill.activation"]
    assert len(skill_spans) == 1
    assert skill_spans[0].attrs["skill.activation_mode"] == "tool_search"


class _HookSelectingAllForLLM:
    def select_for_workflow_init(self, loaded_skills, workflow_id):
        return list(loaded_skills)

    def select_for_llm_dispatch(self, loaded_skills, workflow_id, step_index):
        return list(loaded_skills)


def test_dispatcher_no_op_when_emitter_or_hook_none() -> None:
    """AC #4: dispatcher silent-skips when emitter is None OR hook is None."""
    from harness_runtime.lifecycle.llm_dispatch import RuntimeLLMDispatcher

    tp = _FakeTracerProvider()

    # Emitter None
    dispatcher = RuntimeLLMDispatcher(
        providers={},
        tracer_provider=tp,
        skill_activation_emitter=None,
        skills={SkillID("x"): _make_skill("x")},
    )
    assert dispatcher.skill_activation_emitter is None

    # Hook None (emitter present but without hook)
    emitter_no_hook = SkillActivationSpanEmitter(tracer_provider=tp, hook=None)
    dispatcher2 = RuntimeLLMDispatcher(
        providers={},
        tracer_provider=tp,
        skill_activation_emitter=emitter_no_hook,
        skills={SkillID("x"): _make_skill("x")},
    )
    assert dispatcher2.skill_activation_emitter.hook is None


# --- Runtime v1.139 §14.17.8.2: selection checkpoint + rendering --------------


def test_parse_skill_selection_keeps_selection_order() -> None:
    a, b = _make_skill("a", "A body"), _make_skill("b", "B body")
    skills = {SkillID("a"): a, SkillID("b"): b}

    selection = parse_skill_selection([SkillID("b"), SkillID("a")], skills)

    assert list(selection.items()) == [(SkillID("b"), b), (SkillID("a"), a)]


@pytest.mark.parametrize(
    ("selected", "bad_id", "reason"),
    [
        (["a", "ghost", "a"], "ghost", SkillSelectionInvalidReason.UNKNOWN_ID),
        (["a", "a", "ghost"], "a", SkillSelectionInvalidReason.DUPLICATE_ID),
    ],
)
def test_parse_skill_selection_rejects_first_invalid_id_in_order(
    selected: list[str], bad_id: str, reason: SkillSelectionInvalidReason
) -> None:
    with pytest.raises(SkillSelectionInvalidError) as exc_info:
        parse_skill_selection([SkillID(i) for i in selected], {SkillID("a"): _make_skill("a")})
    err = exc_info.value
    assert (err.skill_id, err.reason) == (SkillID(bad_id), reason)
    assert err.rt_fail_class == "RT-FAIL-SKILL-SELECTION-INVALID"
    assert repr(bad_id) in str(err) and reason.value in str(err)


def test_compose_system_prompt_with_skills_renders_base_then_blocks() -> None:
    a, b = _make_skill("a", "A body"), _make_skill("b", "B body")

    prompt = compose_system_prompt_with_skills("BASE", {SkillID("a"): a, SkillID("b"): b})

    assert prompt == (
        "BASE\n\n"
        f'<skill id="a" version="1.0" version_sha="{a.manifest.version_sha}">\nA body\n</skill>'
        "\n\n"
        f'<skill id="b" version="1.0" version_sha="{b.manifest.version_sha}">\nB body\n</skill>'
    )


@pytest.mark.parametrize("base", [None, ""])
def test_compose_system_prompt_with_skills_blocks_alone_without_base(base: str | None) -> None:
    a = _make_skill("a", "A body")

    prompt = compose_system_prompt_with_skills(base, {SkillID("a"): a})

    assert prompt == (
        f'<skill id="a" version="1.0" version_sha="{a.manifest.version_sha}">\nA body\n</skill>'
    )


@pytest.mark.parametrize("base", [None, "", "BASE"])
def test_compose_system_prompt_with_empty_selection_is_identity(base: str | None) -> None:
    assert compose_system_prompt_with_skills(base, {}) is base


# --- Runtime v1.139 §14.17.8.5 W7: bind ------------------------------------


def test_w7_hook_without_skills_mapping_fails_bind() -> None:
    from harness_runtime.lifecycle.llm_dispatch import LLMDispatchBindError, RuntimeLLMDispatcher

    tp = _FakeTracerProvider()
    emitter = SkillActivationSpanEmitter(tracer_provider=tp, hook=_HookSelectingAllForLLM())

    with pytest.raises(LLMDispatchBindError, match="skills mapping"):
        RuntimeLLMDispatcher(providers={}, tracer_provider=tp, skill_activation_emitter=emitter)

    # An empty mapping and an unbound hook both bind.
    RuntimeLLMDispatcher(
        providers={}, tracer_provider=tp, skill_activation_emitter=emitter, skills={}
    )
    RuntimeLLMDispatcher(
        providers={},
        tracer_provider=tp,
        skill_activation_emitter=SkillActivationSpanEmitter(tracer_provider=tp),
    )


# --- Runtime v1.139 §14.17.8.5: run-level delivery witnesses -------------------
#
# Provider-free: the REAL dispatcher composes the system prompt and the scripted
# Anthropic client records what reached it. W4/W4b additionally run the REAL CP
# driver, sync facade and C-RT-16 wrapper over that dispatcher.


class _Selecting:
    """A hook-2 policy returning a fixed selection, in order."""

    def __init__(self, *ids: str) -> None:
        self.ids = [SkillID(i) for i in ids]

    def select_for_workflow_init(self, loaded_skills, workflow_id):
        return []

    def select_for_llm_dispatch(self, loaded_skills, workflow_id, step_index):
        return list(self.ids)


def _git_hash_object(path: Path) -> str:
    return subprocess.run(
        ["git", "hash-object", str(path)], check=True, capture_output=True, text=True
    ).stdout.strip()


def _skills_on_disk(skills_dir: Path) -> dict[SkillID, Skill]:
    _write_manifest(skills_dir, "a", content="Alpha procedure.\n")
    _write_manifest(skills_dir, "b", content="Beta procedure.\n")
    return load_skills_from_dir(skills_dir)


def _block(skills_dir: Path, skill_id: str) -> str:
    """The §14.17.8.2 item 4 block, built from the file on disk, not from the loader."""
    path = skills_dir / f"{skill_id}.SKILL.md"
    return (
        f'<skill id="{skill_id}" version="1.0" version_sha="{_git_hash_object(path)}">\n'
        f"{path.read_text(encoding='utf-8')}\n</skill>"
    )


def _anthropic_dispatcher(
    skills: dict[SkillID, Skill] | None, hook: Any, *, with_emitter: bool = True
) -> tuple[RuntimeLLMDispatcher, _AnthropicFakeAdapter, InMemorySpanExporter]:
    exporter = InMemorySpanExporter()
    tracer_provider = TracerProvider()
    tracer_provider.add_span_processor(SimpleSpanProcessor(exporter))
    adapter = _AnthropicFakeAdapter(_AnthropicClient())
    emitter = (
        SkillActivationSpanEmitter(tracer_provider=tracer_provider, hook=hook)
        if with_emitter
        else None
    )
    dispatcher = RuntimeLLMDispatcher(
        providers={"anthropic": adapter},
        tracer_provider=tracer_provider,
        active_system_prompt="BASE",
        memory_context=_prompt_extension_memory_context(
            provider="anthropic", family=ProviderFamily.ANTHROPIC
        ),
        skill_activation_emitter=emitter,
        skills=skills,
    )
    return dispatcher, adapter, exporter


def _skill_spans(exporter: InMemorySpanExporter) -> list[tuple[str, str]]:
    """`(skill.id, skill.version_sha)` of every exported `skill.activation` span."""
    return [
        (str(attributes["skill.id"]), str(attributes["skill.version_sha"]))
        for span in exporter.get_finished_spans()
        if span.name == "skill.activation"
        for attributes in [span.attributes or {}]
    ]


async def _dispatch(dispatcher: RuntimeLLMDispatcher, step: Any = None) -> None:
    await dispatcher.dispatch(
        _binding("anthropic"), step if step is not None else _step(), step_context=_step_context()
    )


async def test_w3_selected_skills_reach_the_provider_between_base_and_memory(
    tmp_path: Path,
) -> None:
    skills_dir = tmp_path / "skills"
    skills = _skills_on_disk(skills_dir)
    plain, plain_adapter, _ = _anthropic_dispatcher(skills, None)
    selecting, adapter, exporter = _anthropic_dispatcher(skills, _Selecting("a", "b"))

    await _dispatch(plain)
    await _dispatch(selecting)

    # The memory packet is whatever followed BASE without skills; the skills sit between.
    [plain_call], [call] = plain_adapter.client.messages.calls, adapter.client.messages.calls
    memory = plain_call["system"].removeprefix("BASE")
    assert memory and memory != plain_call["system"], "a memory packet follows the base"
    assert call["system"] == (
        f"BASE\n\n{_block(skills_dir, 'a')}\n\n{_block(skills_dir, 'b')}{memory}"
    )
    assert _skill_spans(exporter) == [
        ("a", _git_hash_object(skills_dir / "a.SKILL.md")),
        ("b", _git_hash_object(skills_dir / "b.SKILL.md")),
    ]
    assert {k: v for k, v in call.items() if k != "system"} == {
        k: v for k, v in plain_call.items() if k != "system"
    }, "only the system prompt carries skills"


async def test_w5_opt_out_and_empty_selection_leave_the_payload_byte_identical(
    tmp_path: Path,
) -> None:
    skills = _skills_on_disk(tmp_path / "skills")
    unbound = _anthropic_dispatcher(skills, None, with_emitter=False)
    no_hook = _anthropic_dispatcher(skills, None)
    empty = _anthropic_dispatcher(skills, _Selecting())

    for dispatcher, _adapter, _exporter in (unbound, no_hook, empty):
        await _dispatch(dispatcher)

    [baseline], [opted_out], [selected_nothing] = (
        case[1].client.messages.calls for case in (unbound, no_hook, empty)
    )
    assert repr(opted_out) == repr(baseline) and repr(selected_nothing) == repr(baseline)
    assert [_skill_spans(case[2]) for case in (no_hook, empty)] == [[], []]


def _step_with_own_system() -> Any:
    return _step(
        {
            "messages": [{"role": "user", "content": "hi"}],
            "tools": None,
            "params": {"max_tokens": 100, "system": "the step's own system"},
        }
    )


async def test_w6_skills_with_a_payload_system_source_conflict(tmp_path: Path) -> None:
    skills = _skills_on_disk(tmp_path / "skills")
    # No base and no memory: the selected skills are the only harness system source.
    empty, empty_adapter, _ = _anthropic_dispatcher(skills, _Selecting())
    selecting, adapter, _ = _anthropic_dispatcher(skills, _Selecting("a"))
    empty, selecting = (
        replace(d, active_system_prompt=None, memory_context=None) for d in (empty, selecting)
    )

    await _dispatch(empty, _step_with_own_system())
    with pytest.raises(PromptInjectionConflictError):
        await _dispatch(selecting, _step_with_own_system())

    [call] = empty_adapter.client.messages.calls
    assert call["system"] == "the step's own system", "no skills, no harness system source"
    assert adapter.client.messages.calls == []


async def test_w8_editing_content_after_bootstrap_changes_nothing_delivered(
    tmp_path: Path,
) -> None:
    skills_dir = tmp_path / "skills"
    skills = _skills_on_disk(skills_dir)
    loaded_block, loaded_sha = _block(skills_dir, "a"), _git_hash_object(skills_dir / "a.SKILL.md")
    dispatcher, adapter, exporter = _anthropic_dispatcher(skills, _Selecting("a"))

    await _dispatch(dispatcher)
    (skills_dir / "a.SKILL.md").write_text("Edited after bootstrap.\n", encoding="utf-8")
    await _dispatch(dispatcher)

    first, second = adapter.client.messages.calls
    assert loaded_block in first["system"] and second["system"] == first["system"]
    assert _skill_spans(exporter) == [("a", loaded_sha), ("a", loaded_sha)]
    assert _git_hash_object(skills_dir / "a.SKILL.md") != loaded_sha


@pytest.mark.parametrize("half_open", [False, True], ids=["closed", "half-open"])
@pytest.mark.parametrize(
    ("selection", "reason"),
    [(("ghost",), "unknown-id"), (("a", "a"), "duplicate-id")],
    ids=["unknown", "duplicate"],
)
async def test_w4_invalid_selection_fails_the_run_without_retry_advance_or_charge(
    tmp_path: Path, selection: tuple[str, ...], reason: str, half_open: bool
) -> None:
    """W4 and, with a half-open primary, W4b: the re-arm is non-charging."""
    skill_exporter = InMemorySpanExporter()
    skill_tracer = TracerProvider()
    skill_tracer.add_span_processor(SimpleSpanProcessor(skill_exporter))
    script: list[Any] = []
    attempts, wrapper, breaker, step = _provider_case(
        tmp_path,
        "anthropic",
        script,
        _Tools(),
        skill_activation_emitter=SkillActivationSpanEmitter(
            tracer_provider=skill_tracer, hook=_Selecting(*selection)
        ),
        skills={SkillID("a"): _make_skill("a")},
    )
    primary = wrapper.fallback_chain.primary
    wrapper.fallback_chain = wrapper.fallback_chain.model_copy(
        update={
            "same_family": (
                ProviderCandidate(provider="anthropic", model="backup", family=primary.family),
            ),
        }
    )
    policy = wrapper.retry_breaker.retry_policies[RESERVED_LLM_DISPATCH_KEY]
    assert policy.max_attempts >= 2, "a retry would be possible if one were allowed"
    if half_open:
        for _ in range(breaker.fail_threshold):
            breaker.record_failure(now=0.0)
    before = (breaker.fail_count, breaker.opened_at)
    exporter = InMemorySpanExporter()
    wrapper.tracer_provider.add_span_processor(SimpleSpanProcessor(exporter))
    ctx = _Ctx()
    ctx.ledger_writer = attempts.inner.hitl_tool_loop.wiring.ledger_writer
    ctx.ledger_reader = materialize_state_ledger_reader(ctx.ledger_writer)

    result = await asyncio.to_thread(
        partial(
            execute_workflow,
            manifest_entry=_manifest().model_copy(
                update={
                    "fallback_chain": wrapper.fallback_chain,
                    "hitl_placements": (),
                    "topology_pattern": TopologyPattern.SINGLE_THREADED_LINEAR,
                }
            ),
            steps=[step],
            run_id="w4-skill-selection",
            ctx=ctx,
            default_model_binding=ModelBinding(provider="anthropic", model="m"),
            step_dispatchers=_Registry(
                materialize_sync_dispatcher_facade(wrapper, result_timeout_seconds=30.0)
            ),
        )
    )

    assert result.status is RunStatus.FAILED
    assert result.fail_class.startswith("step-failure: RT-FAIL-SKILL-SELECTION-INVALID:")
    assert reason in result.fail_class
    assert _skill_spans(skill_exporter) == []
    assert (len(attempts.calls), len(script)) == (1, 0), "one attempt, no advance"
    assert attempts.calls[0].model_binding.model == "m"
    attempt_spans = [
        s for s in exporter.get_finished_spans() if s.name == "harness.runtime.retry_attempt"
    ]
    assert [(s.attributes or {}).get("retry.terminal") for s in attempt_spans] == [
        "skill-selection-invalid"
    ]
    assert not any(
        event.name == "fallback.exhausted"
        for span in exporter.get_finished_spans()
        for event in span.events
    )
    assert breaker.fail_count == before[0], "a selection fault never charges the breaker"
    if half_open:
        assert breaker.state.value == "open"
        assert breaker.opened_at is not None and breaker.opened_at > 0.0, "fresh cooldown"
        assert _transitions(exporter) == [("open", "half_open", 0), ("half_open", "open", 0)]
    else:
        assert (breaker.state.value, breaker.opened_at) == ("closed", before[1])
        assert _transitions(exporter) == []
