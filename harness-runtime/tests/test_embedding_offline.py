"""Provider-free checks for local L2 model admission."""

from __future__ import annotations

import hashlib
import importlib
import os
from pathlib import Path
from types import SimpleNamespace

import pytest
from harness_runtime.lifecycle.embedding_resolution import (
    EmbeddingModelError,
    make_fastembed_embedding,
)
from harness_runtime.lifecycle.llm_dispatch import (
    LLMDispatchBindError,
    materialize_llm_dispatcher_stage,
)

FILES = (
    "config.json",
    "tokenizer.json",
    "tokenizer_config.json",
    "special_tokens_map.json",
    "model_optimized.onnx",
)


def _model(tmp_path: Path) -> tuple[Path, Path]:
    model = tmp_path / "model"
    model.mkdir()
    lines = []
    for name in FILES:
        data = f"fixture:{name}".encode()
        (model / name).write_bytes(data)
        lines.append(f"{hashlib.sha256(data).hexdigest()}  {name}")
    (model / "SHA256SUMS").write_text("\n".join(lines) + "\n")
    return model, tmp_path / "cache"


def _fake(monkeypatch: pytest.MonkeyPatch) -> list[dict[str, object]]:
    calls: list[dict[str, object]] = []

    class FakeTextEmbedding:
        def __init__(self, **kwargs: object) -> None:
            calls.append(kwargs)

        def embed(self, texts: list[str]) -> list[list[float]]:
            assert texts == ["question"]
            return [[1.0, 2.5]]

    real_import = importlib.import_module
    monkeypatch.setattr(
        importlib,
        "import_module",
        lambda name: (
            SimpleNamespace(TextEmbedding=FakeTextEmbedding)
            if name == "fastembed"
            else real_import(name)
        ),
    )
    return calls


def test_verified_local_model_uses_exact_offline_kwargs(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    model, cache = _model(tmp_path)
    calls = _fake(monkeypatch)
    embed = make_fastembed_embedding(model_dir=model, cache_dir=cache)
    assert embed("question") == (1.0, 2.5)
    assert calls == [
        {
            "model_name": "BAAI/bge-small-en-v1.5",
            "specific_model_path": str(model),
            "local_files_only": True,
            "cache_dir": str(cache),
        }
    ]
    assert cache.stat().st_mode & 0o777 == 0o700


@pytest.mark.parametrize(
    "fault",
    [
        "missing-dir",
        "missing-manifest",
        "bad-entry",
        "escape",
        "symlink",
        "missing-file",
        "corrupt",
        "same-size",
        "unlisted",
    ],
)
def test_bad_model_refuses_before_fastembed_construction(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, fault: str
) -> None:
    model, cache = _model(tmp_path)
    if fault == "missing-dir":
        model = tmp_path / "absent"
    elif fault == "missing-manifest":
        (model / "SHA256SUMS").unlink()
    elif fault == "bad-entry":
        (model / "SHA256SUMS").write_text("not-a-sha256-line\n")
    elif fault == "escape":
        (model / "SHA256SUMS").write_text("0" * 64 + "  ../outside\n")
    elif fault == "symlink":
        (model / "tokenizer.json").unlink()
        (model / "tokenizer.json").symlink_to(model / "config.json")
    elif fault == "missing-file":
        (model / "tokenizer.json").unlink()
    elif fault == "corrupt":
        (model / "tokenizer.json").write_bytes(b"changed length")
    elif fault == "same-size":
        data = (model / "tokenizer.json").read_bytes()
        (model / "tokenizer.json").write_bytes(b"X" + data[1:])
    elif fault == "unlisted":
        (model / "extra.bin").write_bytes(b"extra")
    calls = _fake(monkeypatch)
    with pytest.raises(EmbeddingModelError):
        make_fastembed_embedding(model_dir=model, cache_dir=cache)
    assert calls == []


def test_missing_cache_and_relative_model_refuse_before_import(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    model, _ = _model(tmp_path)
    calls = _fake(monkeypatch)
    with pytest.raises(EmbeddingModelError):
        make_fastembed_embedding(model_dir=model, cache_dir=None)
    with pytest.raises(EmbeddingModelError):
        make_fastembed_embedding(
            model_dir=Path(os.path.relpath(model)), cache_dir=tmp_path / "cache"
        )
    assert calls == []


def test_factory_activation_needs_local_model_but_injection_and_default_off_do_not(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    real_import = importlib.import_module

    def no_fastembed(name: str) -> object:
        if name == "fastembed":
            raise AssertionError("factory touched the optional extra")
        return real_import(name)

    monkeypatch.setattr(importlib, "import_module", no_fastembed)
    providers = {"ollama": object(), "claude_code": object()}
    tracer = object()
    with pytest.raises(LLMDispatchBindError, match="embedding_model_dir"):
        materialize_llm_dispatcher_stage(
            providers,
            tracer,
            routing_activation=True,
            embedding_routing_candidates=PROFILE_CANDIDATES,
            external_cli_provider_names=("claude_code",),
        )
    off = materialize_llm_dispatcher_stage(providers, tracer)

    def injected(*_args: object) -> None:
        return None

    on = materialize_llm_dispatcher_stage(
        providers, tracer, routing_activation=True, embedding_classifier=injected
    )
    assert not off.routing_activation and off.embedding_classifier is None
    assert on.routing_activation and on.embedding_classifier is injected


PROFILE_CANDIDATES = {
    "software-engineering": "claude_code:sonnet",
    "content-creation": "claude_code:haiku",
    "pipeline-automation": "ollama:llama3.2:3b",
    "research": "claude_code:sonnet",
}


def test_profile_corpus_requires_all_classes_before_model_import(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from harness_runtime.lifecycle import embedding_resolution

    monkeypatch.setattr(
        embedding_resolution,
        "make_fastembed_embedding",
        lambda **_kwargs: pytest.fail("model imported before corpus admission"),
    )
    providers = {"ollama": object(), "claude_code": object()}
    for candidates in (None, {"software-engineering": "claude_code:sonnet"}):
        with pytest.raises(LLMDispatchBindError, match="embedding routing candidates"):
            materialize_llm_dispatcher_stage(
                providers,
                object(),
                routing_activation=True,
                embedding_routing_candidates=candidates,
                external_cli_provider_names=("claude_code",),
            )


@pytest.mark.parametrize(
    "candidate",
    ("unknown:sonnet", "anthropic:claude", "claude_code:", "ollama:llama3.2:3b"),
)
def test_profile_corpus_refuses_unavailable_candidate_before_model_import(
    monkeypatch: pytest.MonkeyPatch, candidate: str
) -> None:
    from harness_runtime.lifecycle import embedding_resolution

    monkeypatch.setattr(
        embedding_resolution,
        "make_fastembed_embedding",
        lambda **_kwargs: pytest.fail("model imported before corpus admission"),
    )
    candidates = dict(PROFILE_CANDIDATES)
    candidates["research"] = candidate
    providers = {"claude_code": object()}
    with pytest.raises(LLMDispatchBindError, match="embedding routing candidates"):
        materialize_llm_dispatcher_stage(
            providers,
            object(),
            routing_activation=True,
            embedding_routing_candidates=candidates,
            external_cli_provider_names=("claude_code",),
        )


def test_profile_corpus_builds_configured_labels_without_real_model(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from harness_cp import embedding_routing
    from harness_runtime.lifecycle import embedding_resolution

    observed: list[object] = []

    def classifier(*, embed: object, corpus: object) -> object:
        observed.append(corpus)
        return lambda *_args: None

    monkeypatch.setattr(embedding_resolution, "make_fastembed_embedding", lambda **_kw: object())
    monkeypatch.setattr(embedding_routing, "make_embedding_classifier", classifier)
    dispatcher = materialize_llm_dispatcher_stage(
        {"ollama": object(), "claude_code": object()},
        object(),
        routing_activation=True,
        embedding_routing_candidates=PROFILE_CANDIDATES,
        external_cli_provider_names=("claude_code",),
    )
    assert dispatcher.embedding_classifier is not None
    assert len(observed) == 1
    corpus = observed[0]
    assert len(corpus.exemplars) == 16
    assert {item.workload_class for item in corpus.exemplars} == set(PROFILE_CANDIDATES)
    assert all(
        item.candidate == PROFILE_CANDIDATES[item.workload_class] for item in corpus.exemplars
    )


def test_profile_corpus_accepts_membership_only_provider_map(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from harness_cp import embedding_routing
    from harness_runtime.lifecycle import embedding_resolution

    class MembershipOnlyProviders:
        def __init__(self) -> None:
            self._values = {"ollama": object(), "claude_code": object()}

        def __contains__(self, key: object) -> bool:
            return key in self._values

        def __getitem__(self, key: str) -> object:
            return self._values[key]

        def __len__(self) -> int:
            return len(self._values)

    observed: list[object] = []

    def classifier(*, embed: object, corpus: object) -> object:
        observed.append(corpus)
        return lambda *_args: None

    monkeypatch.setattr(embedding_resolution, "make_fastembed_embedding", lambda **_kw: object())
    monkeypatch.setattr(embedding_routing, "make_embedding_classifier", classifier)
    dispatcher = materialize_llm_dispatcher_stage(
        MembershipOnlyProviders(),
        object(),
        routing_activation=True,
        embedding_routing_candidates=PROFILE_CANDIDATES,
        external_cli_provider_names=("claude_code",),
    )
    assert dispatcher.embedding_classifier is not None
    assert len(observed) == 1
    assert len(observed[0].exemplars) == 16


def test_runtime_config_parses_profile_candidate_keys(tmp_path: Path) -> None:
    from harness_core.deployment_surface import DeploymentSurface
    from harness_core.workload_class import WorkloadClass
    from harness_cp.topology_pattern import TopologyPattern
    from harness_runtime.types import (
        CollectorConfig,
        OTelConfig,
        PathBindingConfig,
        ProviderSecretsConfig,
        RuntimeConfig,
    )

    config = RuntimeConfig(
        deployment_surface=DeploymentSurface.LOCAL_DEVELOPMENT,
        repository_root=tmp_path,
        path_bindings=PathBindingConfig(),
        provider_secrets=ProviderSecretsConfig(),
        otel=OTelConfig(otlp_endpoint="http://localhost:4318"),
        collector=CollectorConfig(),
        default_topology=TopologyPattern.SINGLE_THREADED_LINEAR,
        embedding_routing_candidates=PROFILE_CANDIDATES,
    )
    assert config.embedding_routing_candidates is not None
    assert set(config.embedding_routing_candidates) == set(WorkloadClass)
    assert config.embedding_routing_candidates[WorkloadClass.RESEARCH] == "claude_code:sonnet"


def _live_witness_functions() -> dict[str, object]:
    import runpy

    return runpy.run_path(
        str(Path(__file__).parent / "integration" / "test_l2_embedding_live_e2e.py")
    )


def _profile_file(tmp_path: Path) -> Path:
    profile = tmp_path / "harness.toml"
    profile.write_text(
        "[runtime]\n"
        'deployment_surface = "local-development"\n'
        f'repository_root = "{tmp_path}"\n'
        'default_topology = "single-threaded-linear"\n'
        'enabled_provider_names = ["ollama", "claude_code"]\n'
        f'embedding_model_dir = "{tmp_path / "model"}"\n'
        f'embedding_cache_dir = "{tmp_path / "cache"}"\n'
        "\n[runtime.otel]\n"
        'otlp_endpoint = "http://localhost:4318"\n'
        "\n[runtime.embedding_routing_candidates]\n"
        '"software-engineering" = "claude_code:sonnet"\n'
        '"content-creation" = "claude_code:haiku"\n'
        '"pipeline-automation" = "ollama:llama3.2:3b"\n'
        '"research" = "claude_code:sonnet"\n'
        "\n[[runtime.external_cli_providers]]\n"
        'provider = "claude_code"\n'
        'kind = "claude-code"\n',
        encoding="utf-8",
    )
    return profile


def test_live_witness_uses_runtime_config_source(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from harness_runtime.config_source import RuntimeConfigSource

    functions = _live_witness_functions()
    profile = _profile_file(tmp_path)
    monkeypatch.setenv("HARNESS_L2_PROFILE_CONFIG", str(profile))
    calls: list[Path] = []
    original = RuntimeConfigSource.load

    def tracked_load(config_file: Path) -> object:
        calls.append(config_file)
        return original(config_file=config_file)

    monkeypatch.setattr(RuntimeConfigSource, "load", tracked_load)
    candidates, model, cache, available = functions["_profile"]()
    assert calls == [profile]
    assert candidates == PROFILE_CANDIDATES
    assert (model, cache) == (tmp_path / "model", tmp_path / "cache")
    assert available == {"ollama", "claude_code"}


def test_live_witness_refuses_missing_and_invalid_profile_files(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from harness_runtime.config_source import RuntimeConfigLoadError

    profile = _profile_file(tmp_path)
    functions = _live_witness_functions()
    monkeypatch.setenv("HARNESS_L2_PROFILE_CONFIG", str(tmp_path / "missing.toml"))
    with pytest.raises(RuntimeConfigLoadError, match="config file read failed"):
        functions["_profile"]()
    profile.write_text("[runtime\n", encoding="utf-8")
    monkeypatch.setenv("HARNESS_L2_PROFILE_CONFIG", str(profile))
    with pytest.raises(RuntimeConfigLoadError, match="TOML parse error"):
        functions["_profile"]()


@pytest.mark.parametrize(
    ("line", "field"),
    (
        ('enabled_provider_names = ["ollama", "claude_code"]\n', "enabled_provider_names"),
        (
            '[[runtime.external_cli_providers]]\nprovider = "claude_code"\nkind = "claude-code"\n',
            "external_cli_providers",
        ),
    ),
)
def test_live_witness_rejects_implicit_provider_defaults(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, line: str, field: str
) -> None:
    profile = _profile_file(tmp_path)
    profile.write_text(profile.read_text().replace(line, ""), encoding="utf-8")
    monkeypatch.setenv("HARNESS_L2_PROFILE_CONFIG", str(profile))
    with pytest.raises(ValueError, match=field):
        _live_witness_functions()["_profile"]()


def test_live_witness_installed_import_failure_is_not_skipped(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import importlib.util

    functions = _live_witness_functions()
    monkeypatch.setattr(importlib.util, "find_spec", lambda _name: object())
    globals_ = functions["_real_classifier"].__globals__
    monkeypatch.setitem(
        globals_,
        "make_fastembed_embedding",
        lambda **_kwargs: (_ for _ in ()).throw(ImportError("installed ONNX import failed")),
    )
    with pytest.raises(ImportError, match="installed ONNX import failed"):
        functions["_real_classifier"](
            PROFILE_CANDIDATES, Path("/tmp/model"), Path("/tmp/cache"), {"claude_code", "ollama"}
        )


def test_hosted_candidate_rejected_even_if_hosted_provider_constructed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from harness_runtime.lifecycle import embedding_resolution

    monkeypatch.setattr(
        embedding_resolution,
        "make_fastembed_embedding",
        lambda **_kwargs: pytest.fail("model imported before candidate admission"),
    )
    candidates = dict(PROFILE_CANDIDATES)
    candidates["research"] = "anthropic:claude"
    with pytest.raises(LLMDispatchBindError, match="embedding routing candidates"):
        materialize_llm_dispatcher_stage(
            {"ollama": object(), "claude_code": object(), "anthropic": object()},
            object(),
            routing_activation=True,
            embedding_routing_candidates=candidates,
            external_cli_provider_names=("claude_code",),
        )


def test_live_witness_only_absent_extra_skips(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import importlib.util

    functions = _live_witness_functions()
    monkeypatch.setattr(importlib.util, "find_spec", lambda _name: None)
    with pytest.raises(pytest.skip.Exception, match="fastembed not installed"):
        functions["_real_classifier"](
            PROFILE_CANDIDATES, Path("/tmp/model"), Path("/tmp/cache"), {"claude_code", "ollama"}
        )


def test_live_witness_without_profile_is_explicit_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("HARNESS_L2_PROFILE_CONFIG", raising=False)
    with pytest.raises(ValueError, match="HARNESS_L2_PROFILE_CONFIG is required"):
        _live_witness_functions()["_profile"]()


def test_fake_embedding_can_select_four_distinct_labels() -> None:
    from harness_core.workload_class import WorkloadClass
    from harness_cp.cp_shared_types import ProviderAgnosticPayload
    from harness_cp.embedding_routing import make_embedding_classifier
    from harness_cp.routing_manifest_residence import RoutingManifest
    from harness_runtime.lifecycle.embedding_resolution import routing_corpus

    labels = {
        WorkloadClass.SOFTWARE_ENGINEERING: "claude_code:sonnet",
        WorkloadClass.CONTENT_CREATION: "claude_code:haiku",
        WorkloadClass.PIPELINE_AUTOMATION: "ollama:llama3.2:3b",
        WorkloadClass.RESEARCH: "claude_code:opus",
    }
    corpus = routing_corpus(labels, {"ollama", "claude_code"})
    exemplar_classes = {item.text: item.workload_class for item in corpus.exemplars}

    def fake_embed(text: str) -> tuple[float, ...]:
        workload = exemplar_classes.get(text, text.removeprefix("query "))
        return tuple(float(workload == item.value) for item in WorkloadClass)

    classifier = make_embedding_classifier(embed=fake_embed, corpus=corpus)
    manifest = RoutingManifest(
        manifest_version=1,
        per_role_bindings={},
        per_workload_overrides={},
        fallback_chains=(),
        retry_policies={},
    )
    observed = {
        classifier(
            ProviderAgnosticPayload(
                messages=({"role": "user", "content": f"query {workload.value}"},),
                tools=None,
                params={},
            ),
            manifest,
        )
        for workload in WorkloadClass
    }
    assert observed == set(labels.values())
