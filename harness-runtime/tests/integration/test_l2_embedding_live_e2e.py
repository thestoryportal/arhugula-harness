"""Live local L2 classifier proof using an explicit release profile.

Set HARNESS_L2_PROFILE_CONFIG to a TOML harness profile with four
embedding_routing_candidates and absolute embedding_model_dir/cache_dir.
Only an absent optional embedding package may skip; invalid profile/model/import fails.
The chosen local + Claude profile has three distinct candidate labels, so the
>=3 assertion proves separation of those labels, not four-way model quality.
"""

from __future__ import annotations

import importlib.util
import os
from pathlib import Path
from typing import Any, cast

import pytest
from harness_core.workload_class import WorkloadClass
from harness_cp.cp_shared_types import ProviderAgnosticPayload
from harness_cp.embedding_routing import make_embedding_classifier
from harness_cp.layered_routing_strategy import LayerDecisionFn
from harness_cp.routing_manifest_residence import RoutingManifest
from harness_runtime.config_source import RuntimeConfigSource
from harness_runtime.lifecycle.embedding_resolution import (
    make_fastembed_embedding,
    routing_corpus,
)

pytestmark = pytest.mark.e2e


def _profile() -> tuple[dict[WorkloadClass, str], Path, Path, set[str]]:
    profile_path = os.environ.get("HARNESS_L2_PROFILE_CONFIG")
    if not profile_path:
        raise ValueError("HARNESS_L2_PROFILE_CONFIG is required for the L2 live witness")
    config = RuntimeConfigSource.load(config_file=Path(profile_path))
    # [LAW:one-source-of-truth] Read the profile through the runtime loader.
    required = {
        "enabled_provider_names",
        "external_cli_providers",
        "embedding_routing_candidates",
        "embedding_model_dir",
        "embedding_cache_dir",
    }
    missing = required - config.model_fields_set
    if missing:
        raise ValueError("L2 live profile must set: " + ", ".join(sorted(missing)))
    candidates = config.embedding_routing_candidates
    model_dir = config.embedding_model_dir
    cache_dir = config.embedding_cache_dir
    if candidates is None or model_dir is None or cache_dir is None:
        raise ValueError("L2 live profile requires candidates and local model/cache paths")
    cli = {item.provider for item in config.external_cli_providers}
    available = set(config.enabled_provider_names) & ({"ollama"} | cli)
    routing_corpus(candidates, available)
    return candidates, model_dir, cache_dir, available


def _require_fastembed() -> None:
    # [LAW:no-silent-failure] Only an absent optional package can skip this witness.
    if importlib.util.find_spec("fastembed") is None:
        pytest.skip("fastembed not installed (optional [embedding] extra)")


def _real_classifier(
    candidates: dict[WorkloadClass, str],
    model_dir: Path,
    cache_dir: Path,
    available: set[str],
) -> LayerDecisionFn:
    _require_fastembed()
    embed = make_fastembed_embedding(model_dir=model_dir, cache_dir=cache_dir)
    return make_embedding_classifier(
        embed=embed,
        corpus=routing_corpus(candidates, available),
        k=3,
    )


def _payload(text: str) -> ProviderAgnosticPayload:
    return ProviderAgnosticPayload(
        messages=({"role": "user", "content": text},), tools=None, params={}
    )


def _empty_manifest() -> RoutingManifest:
    return RoutingManifest(
        manifest_version=1,
        per_role_bindings={},
        per_workload_overrides={},
        fallback_chains=(),
        retry_policies={},
    )


def test_l2_real_embedding_discriminates_across_workload_classes() -> None:
    """Paraphrases route to profile labels, with at least three distinct picks."""
    candidates, model_dir, cache_dir, available = _profile()
    clf = _real_classifier(candidates, model_dir, cache_dir, available)
    manifest = _empty_manifest()
    code = clf(_payload("help me fix a bug in my python script"), manifest)
    creative = clf(_payload("write me a whimsical short tale"), manifest)
    pipeline = clf(_payload("transform this spreadsheet into rows of records"), manifest)
    research = clf(_payload("review and summarize this academic study"), manifest)
    assert code == candidates[WorkloadClass.SOFTWARE_ENGINEERING]
    assert creative == candidates[WorkloadClass.CONTENT_CREATION]
    assert pipeline == candidates[WorkloadClass.PIPELINE_AUTOMATION]
    assert research == candidates[WorkloadClass.RESEARCH]
    assert len({code, creative, pipeline, research}) >= 3


def test_l2_real_embedding_is_deterministic() -> None:
    candidates, model_dir, cache_dir, available = _profile()
    clf = _real_classifier(candidates, model_dir, cache_dir, available)
    manifest = _empty_manifest()
    query = _payload("debug a failing python test")
    first = clf(query, manifest)
    assert first == candidates[WorkloadClass.SOFTWARE_ENGINEERING]
    assert all(clf(query, manifest) == first for _ in range(3))


def test_l2_factory_builds_real_classifier_when_routing_activation_on() -> None:
    candidates, model_dir, cache_dir, available = _profile()
    from harness_runtime.lifecycle.llm_dispatch import materialize_llm_dispatcher_stage

    _require_fastembed()
    dispatcher = materialize_llm_dispatcher_stage(
        cast("Any", {provider: object() for provider in available}),
        cast("Any", object()),
        routing_activation=True,
        embedding_routing_candidates=candidates,
        external_cli_provider_names=tuple(available - {"ollama"}),
        embedding_model_dir=model_dir,
        embedding_cache_dir=cache_dir,
    )
    assert dispatcher.routing_activation is True
    assert dispatcher.embedding_classifier is not None
    candidate = dispatcher.embedding_classifier(
        _payload("help me fix a bug in my python script"), _empty_manifest()
    )
    assert candidate == candidates[WorkloadClass.SOFTWARE_ENGINEERING]
