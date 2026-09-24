"""R-FS-1 L2 — the light in-process embedding realization + the routing corpus.

Impl-discretion realization (C-CP-02 §2.4 vendor deferral) of the ``EmbeddingFn``
the CP-pure ``make_embedding_classifier`` (``harness_cp.embedding_routing``)
injects. Operator-decided **Option B** (2026-06-16): a **light in-process**
embedding library — ``fastembed`` (Qdrant's ONNX-backed embedder; **torch-free**,
x86-macOS-stable), NOT ``sentence-transformers``/``torch`` and NOT a remote API.
The light form is what delivers the self-sufficiency / portability the operator
chose Option B for (works standalone with no external model server; no heavy
platform wheels) — see ``.harness/r-l2-option-b-light-embedding`` memory.

The embedding is **sync** (the L2-sync determinant — an in-process model), so the
classifier it backs composes inside the sync ``route()`` (no fork, no spec
amendment; the L2-sync path of R-DESIGN §3 D2). ``fastembed`` is a lazy import
(an OPTIONAL ``[embedding]`` extra) so the base runtime install stays light and
the provider-free lanes never pull ``onnxruntime``; importing THIS module does
not require ``fastembed`` — only constructing a real embedding does.

With routing activation, the DECLARATIVE layer can decline to EMBEDDING. A real
classifier therefore requires a locally verified model before FastEmbed is imported.

Authority: ``Spec_Control_Plane_v1_36.md`` §2 C-CP-02 §2.1/§2.2/§2.4; ADR-F1
v1.2; ``.harness/r-fs-1-r-routing-intelligence-design-v1.md`` §3/§6 (D2 L2-sync +
the L2 vendor gate); operator decision 2026-06-16 (Option B).
"""

from __future__ import annotations

import hashlib
import importlib
import os
import re
import stat
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any

from harness_cp.embedding_routing import EmbeddingFn, EmbeddingRoutingCorpus

# The pinned local realization is BAAI/bge-small-en-v1.5. Other model layouts
# need their own file contract before they can pass the verifier.
DEFAULT_EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"
MODEL_FILES = frozenset(
    {
        "config.json",
        "tokenizer.json",
        "tokenizer_config.json",
        "special_tokens_map.json",
        "model_optimized.onnx",
    }
)
MANIFEST_NAME = "SHA256SUMS"


class EmbeddingModelError(ValueError):
    """The explicit local L2 model cannot be admitted at bootstrap."""


@dataclass(frozen=True)
class VerifiedLocalEmbedding:
    model_dir: Path
    cache_dir: Path


def verify_local_embedding(
    model_dir: Path | None, cache_dir: Path | None
) -> VerifiedLocalEmbedding:
    """Admit one complete, hash-matched model and a private, explicit cache."""
    # [LAW:parse-dont-validate] Return paths only after the whole file boundary passes.
    if model_dir is None or cache_dir is None:
        raise EmbeddingModelError(
            "routing activation requires embedding_model_dir and embedding_cache_dir"
        )
    if not model_dir.is_absolute() or not cache_dir.is_absolute():
        raise EmbeddingModelError("embedding model and cache paths must be absolute")
    try:
        if model_dir.resolve(strict=True) != model_dir or not model_dir.is_dir():
            raise EmbeddingModelError("embedding model directory is missing or symlinked")
        manifest = model_dir / MANIFEST_NAME
        metadata = manifest.lstat()
        if not stat.S_ISREG(metadata.st_mode) or metadata.st_size > 65536:
            raise EmbeddingModelError(
                "embedding SHA256SUMS must be a regular file of at most 64 KiB"
            )
        entries: dict[str, str] = {}
        for line in manifest.read_text(encoding="utf-8").splitlines():
            match = re.fullmatch(r"([0-9a-f]{64})  (.+)", line)
            if match is None:
                raise EmbeddingModelError("malformed embedding SHA256SUMS entry")
            expected, raw_name = match.groups()
            name = PurePosixPath(raw_name)
            if (
                name.is_absolute()
                or name.as_posix() != raw_name
                or any(part in {".", ".."} for part in raw_name.split("/"))
                or "\\" in raw_name
                or raw_name == MANIFEST_NAME
                or raw_name in entries
            ):
                raise EmbeddingModelError("unsafe or duplicate embedding SHA256SUMS entry")
            entries[raw_name] = expected
        if not MODEL_FILES.issubset(entries) or len(entries) > 64:
            raise EmbeddingModelError("embedding SHA256SUMS does not cover the pinned model files")
        actual: set[str] = set()
        for path in model_dir.rglob("*"):
            if path.is_symlink():
                raise EmbeddingModelError("embedding model contains a symlink")
            metadata = path.lstat()
            if stat.S_ISDIR(metadata.st_mode):
                continue
            if not stat.S_ISREG(metadata.st_mode):
                raise EmbeddingModelError("embedding model contains a non-regular file")
            actual.add(path.relative_to(model_dir).as_posix())
        if actual != set(entries) | {MANIFEST_NAME}:
            raise EmbeddingModelError("embedding model files differ from SHA256SUMS")
        for name, expected in entries.items():
            sha = hashlib.sha256()
            with (model_dir / name).open("rb") as file:
                for block in iter(lambda: file.read(1024 * 1024), b""):
                    sha.update(block)
            if sha.hexdigest() != expected:
                raise EmbeddingModelError(f"embedding SHA256 mismatch: {name}")
        if (
            cache_dir.is_relative_to(model_dir)
            or cache_dir.parent.resolve(strict=True) != cache_dir.parent
        ):
            raise EmbeddingModelError(
                "embedding cache must be outside the model under a real parent"
            )
        cache_dir.mkdir(mode=0o700, exist_ok=True)
        cache_meta = cache_dir.lstat()
        if (
            not stat.S_ISDIR(cache_meta.st_mode)
            or cache_meta.st_uid != os.geteuid()
            or stat.S_IMODE(cache_meta.st_mode) != 0o700
        ):
            raise EmbeddingModelError("embedding cache must be a private owned directory")
    except (OSError, UnicodeError) as exc:
        raise EmbeddingModelError(f"embedding local model cannot be verified: {exc}") from exc
    return VerifiedLocalEmbedding(model_dir=model_dir, cache_dir=cache_dir)


def make_fastembed_embedding(
    *,
    model_dir: Path | None = None,
    cache_dir: Path | None = None,
) -> EmbeddingFn:
    """Build a sync ``EmbeddingFn`` backed by ``fastembed`` (the light-form
    realization; mirror of ``make_ollama_router``).

    The model is constructed eagerly from a verified local directory; the
    closure projects text into a dense vector. The numpy ndarray ``fastembed`` returns is
    converted to ``tuple[float, ...]`` HERE so numpy never crosses into the
    CP-pure classifier (the ``EmbeddingFn`` return type is ``Sequence[float]``).

    Raises ``EmbeddingModelError`` for an invalid local model or cache and
    ``ImportError`` (with an install hint) when the extra is absent.

    fastembed is imported **dynamically** (``importlib``) rather than via a static
    ``from fastembed import ...``: the static import would fail the strict pyright
    gate in the provider-free CI lane (where the optional ``[embedding]`` extra is
    NOT installed — ``reportMissingImports`` + unknown-type propagation; Codex
    [P1]). The dynamic import keeps fastembed invisible to the typechecker while
    preserving the fail-loud runtime behavior; ``Any`` confines the untyped
    surface to this realization (numpy never crosses into the CP-pure classifier).
    """
    verified = verify_local_embedding(model_dir, cache_dir)
    try:
        fastembed: Any = importlib.import_module("fastembed")
    except ImportError as exc:  # pragma: no cover - exercised only without the extra
        raise ImportError(
            "fastembed is required for the Layer-2 in-process embedding "
            "realization; install the optional extra: `uv sync --extra embedding` "
            "(harness-runtime[embedding])"
        ) from exc

    # [LAW:single-enforcer] FastEmbed receives only the admitted local path and offline mode.
    model: Any = fastembed.TextEmbedding(
        model_name=DEFAULT_EMBEDDING_MODEL,
        specific_model_path=str(verified.model_dir),
        local_files_only=True,
        cache_dir=str(verified.cache_dir),
    )

    def _embed(text: str) -> tuple[float, ...]:
        # `model.embed([text])` yields one ndarray per input text.
        vector: Any = next(iter(model.embed([text])))
        return tuple(float(x) for x in vector)

    return _embed


def default_routing_corpus() -> EmbeddingRoutingCorpus:
    """A representative trained per-workload-class corpus (C-CP-02 §2.1 — the L2
    authoring deliverable).

    Maps characteristic call-site utterances across the four ``WorkloadClass``
    families to a sensible ``"provider:model"`` candidate (capability-aware,
    cheapest-adequate per the C-CP-02 cost discipline). This is an **illustrative
    default**: the candidates and exemplars are operator-tunable — an operator
    retrains the corpus for their own provider bindings + workload mix; it
    demonstrates + exercises the capability rather than fixing a routing policy.
    """
    # Candidate bindings (illustrative; capability-aware-cheapest-adequate):
    #   hard reasoning / code  → a frontier model
    #   creative / short-form  → a cheaper fast model
    #   deterministic pipeline → a free local model
    #   research / analysis    → a long-context frontier model
    code = "anthropic:claude-opus-4-8"
    creative = "anthropic:claude-haiku-4-5"
    pipeline = "ollama:llama3.2:3b"
    research = "openai:gpt-5.5"
    return EmbeddingRoutingCorpus.from_pairs(
        [
            # software-engineering
            ("write a python function to parse a config file", code, "software-engineering"),
            ("debug this failing unit test and fix the bug", code, "software-engineering"),
            ("refactor this module and add type annotations", code, "software-engineering"),
            ("implement a REST API endpoint with validation", code, "software-engineering"),
            # content-creation
            ("write a short story about a lighthouse keeper", creative, "content-creation"),
            ("compose a poem in the style of haiku", creative, "content-creation"),
            ("draft a friendly marketing email for a launch", creative, "content-creation"),
            ("rewrite this paragraph to sound more engaging", creative, "content-creation"),
            # pipeline-automation
            ("extract the totals from each row of this csv", pipeline, "pipeline-automation"),
            ("convert this json payload into a flat table", pipeline, "pipeline-automation"),
            ("run the nightly etl batch and summarize counts", pipeline, "pipeline-automation"),
            ("validate these records against the schema", pipeline, "pipeline-automation"),
            # research
            ("summarize the key findings of this research paper", research, "research"),
            ("compare these two studies and their methodology", research, "research"),
            ("analyze the trends across these survey results", research, "research"),
            ("synthesize the literature on this topic", research, "research"),
        ]
    )
