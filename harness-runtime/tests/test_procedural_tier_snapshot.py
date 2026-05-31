"""Tests for U-RT-112 — procedural-tier snapshot resolver primitive.

Implements IS spec v1.3 §C-IS-05 §5.2 resolver contract; residence pinned
at harness-runtime per Q-γ=(γ-2) operator ratification 2026-05-30.

14 tests cover U-RT-112 ACs #1-#14 per Implementation_Plan_Harness_Runtime_v2_42.md
§1 acceptance criteria. Uses minimal duck-typed context fixture; ZERO bootstrap
or full HarnessContext construction (mirror pattern at
test_lifecycle_skill_activation.py _PartialCtx idiom).
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace

from harness_core import SkillID
from harness_cp.routing_manifest_residence import RoutingManifest
from harness_is.state_ledger_entry_schema import Identifier
from harness_runtime.lifecycle.procedural_tier_snapshot import (
    _canonicalize_procedural_tier_payload,
    make_procedural_tier_snapshot_resolver,
    resolve_procedural_tier_snapshot,
)
from harness_runtime.lifecycle.skills import Skill, SkillManifest


def _skill(skill_id: str, version_sha: str = "v-sha-default") -> Skill:
    """Construct a minimal Skill at-rest carrier."""
    manifest = SkillManifest(
        skill_id=SkillID(skill_id),
        name=f"name-{skill_id}",
        description=f"desc-{skill_id}",
        version="1.0",
        version_sha=version_sha,
        body_tokens=1,
    )
    return Skill(manifest=manifest, source_path=Path("/dev/null"))


def _routing_manifest(manifest_version: int = 1) -> RoutingManifest:
    """Minimal RoutingManifest fixture."""
    return RoutingManifest(
        manifest_version=manifest_version,
        per_role_bindings={},
        per_workload_overrides={},
        fallback_chains=(),
        retry_policies={},
    )


def _ctx(
    skills: dict[SkillID, Skill] | None = None,
    routing_manifest: RoutingManifest | None = None,
) -> SimpleNamespace:
    """Build a minimal duck-typed HarnessContext-shape exposing just the
    fields the resolver reads (``skills`` + ``routing_manifest``)."""
    return SimpleNamespace(
        skills=skills if skills is not None else {},
        routing_manifest=routing_manifest if routing_manifest is not None else _routing_manifest(),
    )


# ---------------------------------------------------------------------------
# AC #2 — content-hash recipe byte-exact (64-char lowercase hex SHA-256).
# ---------------------------------------------------------------------------


def test_resolve_returns_64_char_lowercase_hex() -> None:
    """AC #2: Output is 64-char lowercase hex SHA-256."""
    result = resolve_procedural_tier_snapshot(_ctx())  # type: ignore[arg-type]
    assert len(result) == 64
    assert result == result.lower()
    assert all(c in "0123456789abcdef" for c in result)


# ---------------------------------------------------------------------------
# AC #3 — alphabetical key ordering (2 components at v1.3).
# ---------------------------------------------------------------------------


def test_resolve_canonical_payload_alphabetical_keys_2_components_at_v1_3() -> None:
    """AC #3 + #11: Canonical payload has 2 keys alphabetically ordered."""
    payload_bytes = _canonicalize_procedural_tier_payload(
        active_skills_versions=["a"],
        routing_manifest_sha="b" * 64,
    )
    payload = json.loads(payload_bytes.decode("utf-8"))
    assert list(payload.keys()) == ["active_skills_versions", "routing_manifest_sha"]
    assert "active_prompt_version" not in payload


# ---------------------------------------------------------------------------
# AC #4 — skills-versions list canonicalization.
# ---------------------------------------------------------------------------


def test_resolve_skills_versions_sorted_ascending() -> None:
    """AC #4: ``active_skills_versions`` sorted ascending."""
    skill_a = _skill("skill-a", version_sha="v-sha-z")
    skill_b = _skill("skill-b", version_sha="v-sha-a")
    ctx = _ctx(skills={SkillID("a"): skill_a, SkillID("b"): skill_b})
    # Construct an oracle by manually invoking the same recipe in sorted order.
    expected_versions = sorted(["v-sha-z", "v-sha-a"])
    routing_sha = hashlib.sha256(
        ctx.routing_manifest.model_dump_json(by_alias=False).encode("utf-8"),
    ).hexdigest()
    oracle = hashlib.sha256(
        _canonicalize_procedural_tier_payload(expected_versions, routing_sha),
    ).hexdigest()
    assert resolve_procedural_tier_snapshot(ctx) == oracle  # type: ignore[arg-type]


def test_resolve_skills_versions_dedup_before_serialize() -> None:
    """AC #4: duplicate ``version_sha`` values deduplicated before serialization."""
    skill_a = _skill("skill-a", version_sha="v-shared")
    skill_b = _skill("skill-b", version_sha="v-shared")
    ctx_dup = _ctx(skills={SkillID("a"): skill_a, SkillID("b"): skill_b})
    skill_single = _skill("skill-c", version_sha="v-shared")
    ctx_single = _ctx(skills={SkillID("c"): skill_single})
    assert resolve_procedural_tier_snapshot(ctx_dup) == resolve_procedural_tier_snapshot(  # type: ignore[arg-type]
        ctx_single,  # type: ignore[arg-type]
    )


# ---------------------------------------------------------------------------
# AC #5 + #6 — input-differential discipline.
# ---------------------------------------------------------------------------


def test_resolve_different_skills_set_different_hash() -> None:
    """AC #5: differing skills sets produce different hashes."""
    ctx_a = _ctx(skills={SkillID("x"): _skill("x", version_sha="v-1")})
    ctx_b = _ctx(skills={SkillID("y"): _skill("y", version_sha="v-2")})
    assert resolve_procedural_tier_snapshot(ctx_a) != resolve_procedural_tier_snapshot(  # type: ignore[arg-type]
        ctx_b,  # type: ignore[arg-type]
    )


def test_resolve_different_routing_manifest_different_hash() -> None:
    """AC #5: differing routing manifests produce different hashes."""
    ctx_a = _ctx(routing_manifest=_routing_manifest(manifest_version=1))
    ctx_b = _ctx(routing_manifest=_routing_manifest(manifest_version=2))
    assert resolve_procedural_tier_snapshot(ctx_a) != resolve_procedural_tier_snapshot(  # type: ignore[arg-type]
        ctx_b,  # type: ignore[arg-type]
    )


def test_resolve_same_state_same_hash_across_calls() -> None:
    """AC #6: identical state ⇒ identical hash (cross-instance + cross-call determinism)."""
    skill = _skill("k", version_sha="v-determ")
    ctx_a = _ctx(skills={SkillID("k"): skill})
    ctx_b = _ctx(skills={SkillID("k"): skill})
    result_a1 = resolve_procedural_tier_snapshot(ctx_a)  # type: ignore[arg-type]
    result_a2 = resolve_procedural_tier_snapshot(ctx_a)  # type: ignore[arg-type]
    result_b = resolve_procedural_tier_snapshot(ctx_b)  # type: ignore[arg-type]
    assert result_a1 == result_a2 == result_b


# ---------------------------------------------------------------------------
# AC #7 — return type ``Identifier`` (str alias).
# ---------------------------------------------------------------------------


def test_resolve_return_type_is_identifier_alias() -> None:
    """AC #7: return value is an Identifier (str subtype at runtime)."""
    result = resolve_procedural_tier_snapshot(_ctx())  # type: ignore[arg-type]
    assert isinstance(result, str)


# ---------------------------------------------------------------------------
# AC #1 + #8 — pure-function discipline (no side effects; no module state).
# ---------------------------------------------------------------------------


def test_resolve_pure_function_no_side_effects() -> None:
    """AC #1 + #8: no global state; deterministic for fixed input."""
    ctx = _ctx()
    snapshot_1 = resolve_procedural_tier_snapshot(ctx)  # type: ignore[arg-type]
    # Invoke an unrelated function that has no shared state.
    _ = resolve_procedural_tier_snapshot(_ctx(skills={SkillID("x"): _skill("x")}))  # type: ignore[arg-type]
    snapshot_2 = resolve_procedural_tier_snapshot(ctx)  # type: ignore[arg-type]
    assert snapshot_1 == snapshot_2


# ---------------------------------------------------------------------------
# AC #9 — no HarnessContext mutation.
# ---------------------------------------------------------------------------


def test_resolve_no_harness_context_mutation() -> None:
    """AC #9: resolver does not mutate ctx.skills or ctx.routing_manifest."""
    skills_before = {SkillID("a"): _skill("a", version_sha="v-1")}
    skills_snapshot = dict(skills_before)
    routing_before = _routing_manifest(manifest_version=42)
    ctx = _ctx(skills=skills_before, routing_manifest=routing_before)
    resolve_procedural_tier_snapshot(ctx)  # type: ignore[arg-type]
    assert ctx.skills == skills_snapshot
    assert ctx.routing_manifest == routing_before


# ---------------------------------------------------------------------------
# AC #10 — empty skills set handled.
# ---------------------------------------------------------------------------


def test_resolve_empty_skills_set_handled() -> None:
    """AC #10: empty ``ctx.skills`` produces a deterministic non-error hash."""
    result_a = resolve_procedural_tier_snapshot(_ctx(skills={}))  # type: ignore[arg-type]
    result_b = resolve_procedural_tier_snapshot(_ctx(skills={}))  # type: ignore[arg-type]
    assert result_a == result_b
    assert len(result_a) == 64


# ---------------------------------------------------------------------------
# AC #11 — prompts component deferral.
# ---------------------------------------------------------------------------


def test_resolve_canonical_payload_omits_prompts_key_at_v1_3() -> None:
    """AC #11: canonical payload contains exactly 2 keys at v1.3; no prompts."""
    payload_bytes = _canonicalize_procedural_tier_payload(
        active_skills_versions=[],
        routing_manifest_sha="0" * 64,
    )
    payload = json.loads(payload_bytes.decode("utf-8"))
    assert set(payload.keys()) == {"active_skills_versions", "routing_manifest_sha"}
    assert len(payload) == 2


# ---------------------------------------------------------------------------
# AC #12 — RoutingManifest sha derivation byte-exact via model_dump_json.
# ---------------------------------------------------------------------------


def test_resolve_routing_manifest_sha_derivation_byte_exact() -> None:
    """AC #12: routing_manifest_sha derivation matches the documented recipe."""
    rm = _routing_manifest(manifest_version=7)
    ctx = _ctx(routing_manifest=rm)
    expected_routing_sha = hashlib.sha256(
        rm.model_dump_json(by_alias=False).encode("utf-8"),
    ).hexdigest()
    expected_payload = _canonicalize_procedural_tier_payload(
        active_skills_versions=[],
        routing_manifest_sha=expected_routing_sha,
    )
    expected_hash = hashlib.sha256(expected_payload).hexdigest()
    assert resolve_procedural_tier_snapshot(ctx) == expected_hash  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# AC #13 — factory function shape.
# ---------------------------------------------------------------------------


def test_make_resolver_factory_returns_callable_capturing_ctx() -> None:
    """AC #13: ``make_procedural_tier_snapshot_resolver`` returns a zero-arg
    callable that re-computes from the captured ctx state at each call."""
    ctx = _ctx(skills={SkillID("a"): _skill("a", version_sha="v-1")})
    closure = make_procedural_tier_snapshot_resolver(ctx)  # type: ignore[arg-type]
    direct = resolve_procedural_tier_snapshot(ctx)  # type: ignore[arg-type]
    assert callable(closure)
    assert closure() == direct
    # Closure is idempotent across calls (re-compute from captured ctx).
    assert closure() == closure()
