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
    providers = {"test": object()}
    tracer = object()
    with pytest.raises(LLMDispatchBindError, match="embedding_model_dir"):
        materialize_llm_dispatcher_stage(providers, tracer, routing_activation=True)
    off = materialize_llm_dispatcher_stage(providers, tracer)

    def injected(*_args: object) -> None:
        return None

    on = materialize_llm_dispatcher_stage(
        providers, tracer, routing_activation=True, embedding_classifier=injected
    )
    assert not off.routing_activation and off.embedding_classifier is None
    assert on.routing_activation and on.embedding_classifier is injected
