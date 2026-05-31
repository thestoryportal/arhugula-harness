# Implementation Plan — Harness Runtime — v2.42

*Delta over v2.41. v2.42 is the Phase 7 H_T-IS-2 substitution-retirement apply-pass impl-half per `.harness/architect_recommendation_h_t_is_2_artifact_tier_registry_wiring.md` §11.4 Q-γ operator-ratified 2026-05-30 as **(γ-2) NEW U-RT-NN at runtime plan v2.42 cascade**. NEW unit U-RT-112 authors the `resolve_procedural_tier_snapshot` resolver primitive per IS spec v1.3 §5.2; residence pinned to `harness-runtime/src/harness_runtime/lifecycle/procedural_tier_snapshot.py` per Q-γ ratification. U-IS-18 retired at IS plan v2.5 sibling delta (residence-ownership transfer to U-RT-112). U-IS-11 sidecar field amendment PRESERVED VERBATIM at IS plan (carrier remains IS-axis owned). Unit count 109 → 110. +1 within-axis-cross-package edge (U-RT-112 → U-IS-11 for sidecar carrier; U-RT-112 → U-IS-07 for `Identifier` alias). ZERO cross-axis cascade at this arc per Q2=narrow ratification (producer-site lifts at ~13 CP / runtime / AS composers deferred per `[[substrate-pre-landed-consumer-deferred-multi-arc-lift]]` precedent; H_T-IS-2 STILL-BOUNDED → PARTIAL on apply per X-AL-2 second conjunct; PARTIAL → RETIRED gated on full producer-site lift). v2.41 + earlier PRESERVED VERBATIM per delta-only-plan-chain convention.*

## §0 Change note (v2.41 → v2.42)

### §0.1 What changed

| Element | v2.41 | v2.42 |
|---|---|---|
| Total unit count | 109 | **110** (+1 NEW U-RT-112) |
| NEW units | (none) | **U-RT-112** — `resolve_procedural_tier_snapshot` resolver primitive at `harness-runtime/.../lifecycle/procedural_tier_snapshot.py` per IS spec v1.3 §5.2 + Q-γ=(γ-2) ratification |
| NEW within-axis-cross-package edges | (none) | **U-RT-112 → U-IS-07** (`Identifier` type alias consumption); **U-RT-112 → U-IS-11** (sidecar field `EntryPayload.procedural_tier_snapshot_ref` consumption at downstream caller sites; not at U-RT-112 unit body itself but declared at edge layer for arc traversal sequencing) |
| H_T-IS-2 transit | STILL-BOUNDED (per v2.41 baseline) | **STILL-BOUNDED → PARTIAL** at apply-pass merge (substrate landed; producer-site lift bounded per Q2=narrow); PARTIAL → RETIRED at follow-on per-axis cascade arcs per X-AL-2 second conjunct |
| §2 unit-body changes | UNCHANGED | **NEW U-RT-112 unit body in §2 below** |
| §3 DAG | UNCHANGED | **+1 node** (U-RT-112); **+2 cross-package edges** (U-RT-112 → U-IS-07 + U-RT-112 → U-IS-11); acyclicity preserved (cross-package edges run runtime → IS direction matching existing `harness-runtime/types.py:88-90` import chain; ZERO new cycle) |
| §4 coverage matrix | UNCHANGED | **NEW row** for IS spec C-IS-05 §5.2 contract (covered at U-RT-112) |
| CXA v2.16 transit | 6 PENDING → 2 LANDED + 4 carry per v2.40 + v2.41 framing | UNCHANGED — v2.42 is IS-substrate consumer-site authoring, not §16.5 CP composer arc; ZERO CXA transit |

### §0.2 Scope discipline

§0 (this change note); §1 NEW U-RT-112 unit-body decomposition; §2 DAG delta (+1 node + 2 cross-package edges); §3 Coverage matrix delta (NEW C-IS-05 §5.2 row); §4 adjacent observations + cross-axis-cascade discipline (deferred per Q2=narrow); §5 filing footer. All v2.41 + ... + v1 lineage PRESERVED VERBATIM per delta-only-plan-chain convention.

### §0.3 Q-γ ratification + empirical reconciliation

**Q-γ — Resolver implementation residence ratified 2026-05-30 as (γ-2)** per `.harness/architect_recommendation_h_t_is_2_artifact_tier_registry_wiring.md` §11.4.1. Three options enumerated at next-session-opener Q-γ AUQ:

| Option | Cost | Benefit | Ratification |
|---|---|---|---|
| (γ-1) cross-package impl under U-IS-18 | NEW workspace convention (IS-contract impl outside harness-is package); zero precedent | Smallest move; no new plan unit | Not selected |
| **(γ-2) NEW U-RT-NN at runtime plan v2.42 (recommended)** | Runtime plan cascade owed (this arc) | Preserves "contract resides where impl resides" convention; mirror U-CORE-02 precedent | **RATIFIED** |
| (γ-3) Protocol pattern at harness-core | Protocol-of-Protocol surface OR carrier re-home (multi-arc); pyright strict structural-typing verification | Preserves both Q2=narrow + intra-IS-axis dep-graph | Not selected |

**Empirical reconciliation at apply-pass orientation 2026-05-30 (post-AUQ).** Two checkpoint claims discriminated via empirical grep:

1. **SkillID residence** — checkpoint claimed `SkillID` at `harness-runtime/.../skills.py`; empirical at HEAD `8816ce9` confirms `SkillID = NewType("SkillID", str)` at **`harness-core/src/harness_core/identity.py:76`**. SkillID is reachable from any axis package depending on harness-core. Checkpoint-vs-HEAD divergence catalogued at `[[checkpoint-recall-vs-empirical-HEAD]]` discipline.
2. **RoutingManifest sha derivation surface** — `RoutingManifest` class at `harness-cp/src/harness_cp/routing_manifest_residence.py:118` exposes NO `.sha` / `.hash()` / `.digest()` method at HEAD. Resolver computes the sha via `sha256(routing_manifest.model_dump_json(by_alias=False).encode("utf-8"))` at the U-RT-112 implementation per IS spec v1.3 §5.2 "Deferred to implementation discretion" footer authorization. This is implementer-discretion territory at the resolver site; NOT a halt-shape gap requiring back-flow per `[[advisor-before-substantive-work-for-cross-axis-blockers]]` 56th application (pre-substantive advisor verification 2026-05-30).

**Per-axis residence rationale at (γ-2).** Runtime axis owns the resolver primitive because: (a) `HarnessContext` lives at runtime axis (`harness-runtime/.../types.py`); (b) `Skill` concrete class + `SkillManifest` live at runtime axis (`harness-runtime/.../lifecycle/skills.py`); (c) `RoutingManifest` is imported by `harness-runtime/.../types.py:70` for `HarnessContext.routing_manifest` field; the runtime package already transits all required carrier surfaces. IS spec v1.3 §5.2 contract is consumed at runtime axis via cross-package contract-citation, mirroring U-CORE-02 (harness-core hosts F1 sandbox-decision-policy carrier per AS spec contract). ZERO new dep edge at `harness-runtime/pyproject.toml` (harness-is + harness-cp + harness-core already declared).

### §0.4 IS plan v2.4 → v2.5 sibling delta

Co-published this arc: **IS plan v2.5** retires U-IS-18 (RELOCATED-TO-U-RT-112-per-Q-γ-(γ-2)-ratification). U-IS-18's body at IS plan v2.4 explicitly deferred residence at "Files affected" line ("concrete module residence DEFERRED per spec v1.3 §5.2 Deferred to implementation discretion footer"); v2.5 closes the deferral via supersession. U-IS-11 sidecar field amendment PRESERVED VERBATIM at IS plan v2.5 (sidecar carrier remains IS-axis owned; only the resolver primitive residence transfers to runtime axis).

## §1 NEW U-RT-112 unit-body decomposition

### U-RT-112 — Implement `resolve_procedural_tier_snapshot` resolver primitive  *(v2.42 NEW)*

**Implements:** IS spec v1.3 [C-IS-05 §5.2] resolver contract; supersedes IS plan v2.4 U-IS-18 residence-deferred placeholder per Q-γ=(γ-2) operator ratification 2026-05-30.

**Depends on:**
- [U-IS-07] — `Identifier` type alias (cross-package consumption at signature return type)
- [U-RT-99] — `SkillManifest` with `version_sha: str` field landing (per v1.32 absorption at `harness-runtime/.../lifecycle/skills.py:60`)
- [U-RT-01] — `HarnessContext` (parameter type at signature)

**Files affected (residence pinned at v2.42 per Q-γ ratification):**
- **NEW** `harness-runtime/src/harness_runtime/lifecycle/procedural_tier_snapshot.py` (~50 lines)
- **NEW** `harness-runtime/tests/test_procedural_tier_snapshot.py` (~150 lines covering 14 acceptance criteria)

**Scope.** Pure-function resolver implementing the IS spec v1.3 §5.2 content-hash recipe + direct-compute storage discipline. NO separate registry persistence; NO mutation state; resolver re-computes from current `HarnessContext` state at every call. Mirror unit-body shape to retired IS plan v2.4 U-IS-18; residence pinned to runtime axis.

**Signatures:**

```python
def resolve_procedural_tier_snapshot(harness_context: HarnessContext) -> Identifier: ...

# Internal helper exposed for testing:
def _canonicalize_procedural_tier_payload(
    active_skills_versions: list[str],
    routing_manifest_sha: str,
) -> bytes: ...

# Factory for engine-layer composers without HarnessContext access at firing time
# per CP spec v1.25 §16.5.7 + §16.5.8 `ledger_writer` kw-only-callable precedent.
# Producer-site lift at composers DEFERRED per Q2=narrow; factory authored at v2.42 for
# future cascade arcs.
def make_procedural_tier_snapshot_resolver(
    harness_context: HarnessContext,
) -> Callable[[], Identifier]: ...
```

**Internal logic (v1.3 — 2-component scope; prompts deferred per spec §5.2 deferral footer):**

1. Extract `active_skills_versions: list[str]` from `harness_context.skills` (read `Skill.manifest.version_sha` per each entry in the `dict[SkillID, Skill]` mapping; `Skill.manifest: SkillManifest` per `harness-runtime/.../lifecycle/skills.py:65`).
2. Compute `routing_manifest_sha: str` via `sha256(harness_context.routing_manifest.model_dump_json(by_alias=False).encode("utf-8")).hexdigest()` (RoutingManifest is a frozen Pydantic v2 BaseModel per `harness-cp/.../routing_manifest_residence.py:118`; no `.sha` method at HEAD; canonicalize-at-resolver per IS spec v1.3 §5.2 implementer-discretion footer).
3. Sort + dedup `active_skills_versions` ascending lexicographic order.
4. Build canonical payload dict `{"active_skills_versions": list[str], "routing_manifest_sha": str}` ordered alphabetically by key (2 components at v1.3; prompts component joins at v1.x per spec §5.2 Deferral footer).
5. Serialize via `json.dumps(payload, sort_keys=True, separators=(",", ":"))`; encode UTF-8.
6. Return `sha256(canonical_bytes).hexdigest()` as `Identifier`.

**Acceptance criteria (v1.3 — 2-component scope):**

| # | Property | Criterion | Spec ref |
|---|---|---|---|
| 1 | Pure function | No side effects; no state mutation; same `HarnessContext` input yields identical output across calls | IS §5.2 |
| 2 | Content-hash recipe byte-exact | Output is lowercase hex SHA-256 (64 chars) of canonical-JSON-bytes per §5.2 recipe; canonical-JSON via `sort_keys=True` + `separators=(",", ":")` | IS §5.2 + §6.1 |
| 3 | Alphabetical key ordering | Canonical payload dict ordered alphabetically by key (`active_skills_versions`, `routing_manifest_sha`) — 2 components at v1.3 | IS §5.2 |
| 4 | Skills-versions list canonicalization | `active_skills_versions` sorted ascending lexicographic + dedup'd before JSON serialization | IS §5.2 |
| 5 | Different HarnessContext state ⇒ different hash | Two HarnessContexts differing in any one of the two presently-bound procedural-tier components produce different content-hash outputs | IS §5.2 |
| 6 | Same HarnessContext state ⇒ same hash | Two HarnessContexts with identical procedural-tier components produce byte-identical content-hash outputs (cross-instance determinism) | IS §5.2 |
| 7 | Return type `Identifier` | Output type matches U-IS-07 `Identifier` alias (str) | IS §5.2 + U-IS-07 |
| 8 | Direct-compute discipline | No module-level state; no caching at v2.42 (per-call recompute; same-input memoization deferred to implementation discretion) | IS §5.2 |
| 9 | No HarnessContext mutation | Function does not mutate or assign to `harness_context` or any of its attributes | IS §5.2 (pure) |
| 10 | Empty-skills-set handled | `active_skills_versions=[]` produces valid canonical-JSON serialization (empty JSON array `[]`) and a deterministic hash | IS §5.2 |
| 11 | Prompts-component deferral discipline | Resolver does NOT attempt to read any prompt-version field from `HarnessContext`; canonical payload contains exactly 2 keys at v1.3 (`active_skills_versions` + `routing_manifest_sha`); 3rd key (`active_prompt_version`) absent per spec §5.2 deferral footer | IS §5.2 (Prompts deferred) |
| 12 | RoutingManifest sha derivation | `routing_manifest_sha` derived via `sha256(model_dump_json(by_alias=False).encode("utf-8")).hexdigest()`; deterministic across Pydantic v2 instances with identical field values | IS §5.2 (implementer-discretion footer) |
| 13 | Factory function shape | `make_procedural_tier_snapshot_resolver(ctx)` returns `Callable[[], Identifier]` closure capturing `ctx`; each call re-computes from captured `ctx` state | IS §5.2 + CP spec v1.25 §16.5.7 + §16.5.8 kw-only-callable precedent |
| 14 | No producer-site lift at v2.42 | Resolver module is authored; consumer-site call sites (~13 across CP / runtime / AS composers per Q2=narrow deferral) NOT exercised at v2.42; H_T-IS-2 transit STILL-BOUNDED → PARTIAL on apply, NOT RETIRED | Q2=narrow + X-AL-2 second conjunct |

**Tests (14 cases at `test_procedural_tier_snapshot.py`):**

- `test_resolve_returns_64_char_lowercase_hex`
- `test_resolve_canonical_payload_alphabetical_keys_2_components_at_v1_3`
- `test_resolve_skills_versions_sorted_ascending`
- `test_resolve_skills_versions_dedup_before_serialize`
- `test_resolve_different_skills_set_different_hash`
- `test_resolve_different_routing_manifest_different_hash`
- `test_resolve_same_state_same_hash_across_calls`
- `test_resolve_pure_function_no_side_effects`
- `test_resolve_no_harness_context_mutation`
- `test_resolve_empty_skills_set_handled`
- `test_resolve_return_type_is_identifier_alias`
- `test_resolve_canonical_payload_omits_prompts_key_at_v1_3`
- `test_resolve_routing_manifest_sha_derivation_byte_exact`
- `test_make_resolver_factory_returns_callable_capturing_ctx`

**Producer-site call sites (deferred per Q2=narrow).** Composers with `HarnessContext` access at firing time consume `resolve_procedural_tier_snapshot(ctx)` at entry-construction time. Engine-layer composers without `HarnessContext` access at firing time receive `Callable[[], Identifier]` via `make_procedural_tier_snapshot_resolver(ctx)` as a kw-only parameter bound at runtime composition time per CP spec v1.25 §16.5.7 + §16.5.8 `ledger_writer` precedent. **Producer-site lift NOT at v2.42 scope** — ~13 sites across `harness-as` / `harness-cp` / `harness-runtime` (CP §16.5 composers + state-ledger emission composers + sub-agent dispatch sites) defer to follow-on per-axis arcs per `[[substrate-pre-landed-consumer-deferred-multi-arc-lift]]` precedent. H_T-IS-2 PARTIAL → RETIRED gated on full producer-site lift completion per X-AL-2 second conjunct.

**Rollback boundary:** Revert NEW `procedural_tier_snapshot.py` module + test file. Sidecar field at U-IS-11 `EntryPayload` continues to accept `None` (existing semantics preserved); cross-axis producer-site lifts (when authored at follow-on arcs) lose the resolver source-of-truth and would need either a re-author or a stub returning a sentinel value. NO contract change at harness-is (U-IS-11 sidecar amendment preserved verbatim at IS plan v2.5).

## §2 DAG delta (v2.42)

### §2.1 New node + within-axis-cross-package edges

| Edge | From | To | Direction | Cycle risk |
|---|---|---|---|---|
| NEW node | — | U-RT-112 | (node addition) | N/A |
| NEW edge | U-RT-112 | U-IS-07 (`Identifier` alias) | runtime → IS | None — matches existing `harness-runtime` → `harness-is` dep direction at `pyproject.toml` |
| NEW edge | U-RT-112 | U-IS-11 (sidecar field carrier at `EntryPayload`) | runtime → IS | None — same direction |
| NEW edge (internal) | U-RT-112 | U-RT-01 (`HarnessContext`) | within-runtime | None — same-package |
| NEW edge (internal) | U-RT-112 | U-RT-99 (`SkillManifest.version_sha`) | within-runtime | None — same-package |

### §2.2 Acyclicity preservation

Cross-package edges run **runtime → IS** direction matching existing `harness-runtime/pyproject.toml` dep declaration + `harness-runtime/src/harness_runtime/types.py:88-90` runtime import chain. ZERO new dep edge at `harness-runtime/pyproject.toml` (harness-is + harness-cp + harness-core already declared). ZERO new cycle.

Empirical verification at HEAD `8816ce9`: `grep -n "harness_runtime" harness-is/src/harness_is/*.py` returns ZERO hits (harness-is does not import from harness-runtime); reverse direction is the only existing dep, so adding U-RT-112 → U-IS-07 + U-RT-112 → U-IS-11 edges preserves DAG acyclicity at the cross-package layer.

## §3 Coverage matrix delta (v2.42)

| Spec contract | Atomic unit | Status |
|---|---|---|
| IS spec v1.3 C-IS-05 §5.2 (`resolve_procedural_tier_snapshot` resolver contract) | **U-RT-112 (v2.42 NEW)** | Covered at v2.42 |
| IS spec v1.3 C-IS-05 §5.1 (`procedural_tier_snapshot_ref` sidecar field) | U-IS-11 (revised at IS plan v2.4) | Covered at IS plan v2.4 + preserved at IS plan v2.5 |

NO other coverage row change at v2.42.

## §4 Adjacent observations + carry-forward + cross-axis cascade discipline

(a) **Q-γ=(γ-2) is the third operator-residence-ratification arc in workspace history.** Mirror precedents: U-CORE-02 `SandboxDecisionPolicy` re-home from phantom AS spec v1.3 §15 cite to harness-core empty-marker (2026-05-22 per `harness-core` plan v1.2); U-RT-99 `Skill` type residence absorption at harness-runtime per spec v1.32 NEW §14.17 (2026-05-28). v2.42 establishes the **IS-spec-contract / runtime-axis-impl** workspace convention; mirror precedent U-CORE-02 (AS-spec-contract / harness-core-impl).

(b) **56th application of `[[advisor-before-substantive-work-for-cross-axis-blockers]]` posture** — pre-substantive advisor consultation 2026-05-30 caught: (1) SkillID residence checkpoint claim was empirically wrong (at harness-core not harness-runtime); (2) RoutingManifest sha derivation surface absent at HEAD; (3) reframed initially-conversational "30-line module" claim to empirical "~50 line module + factory function for engine-layer composers per CP spec v1.25 §16.5.7 precedent"; (4) scope discipline at Q2=narrow holds — do NOT thread `Callable[[], Identifier]` into producer sites at this arc.

(c) **Checkpoint-vs-HEAD discipline** — `[[checkpoint-recall-vs-empirical-HEAD]]` candidate sub-species at workflow v1.13 §7.4.7.2; checkpoint authored at session N records residence claims that drift across N+1 sessions as production state evolves. Empirical grep at HEAD pre-substantive is the discipline that closes drift. Cardinality 1 at this arc (SkillID checkpoint claim).

(d) **Producer-site cascade discipline.** ~13 producer-site lifts deferred per Q2=narrow ratification; estimated split: CP-axis ~7 sites at §16.5 composers (U-CP-14 / U-CP-27 / U-CP-30 / U-CP-37 / U-CP-49 / U-CP-50 / U-CP-34) per CP spec v1.25 §16.5 enumeration; runtime-axis ~4 sites at sub-agent dispatch + cost-attribution composers + per-step override evaluator wiring; AS-axis ~2 sites at tool-dispatcher span emission. Each producer-site lift is a small canonical-reading amendment at the consumer's plan body + a 1-line composer signature kw-only addition + a 1-line entry-construction site update. Per-axis cascade arcs sized at ~1-2 sessions per axis per `[[substrate-pre-landed-consumer-deferred-multi-arc-lift]]` precedent. H_T-IS-2 transit PARTIAL → RETIRED gated on full lift completion per X-AL-2 second conjunct.

(e) **ZERO CXA transit at v2.42.** v2.42 authors runtime-axis substrate consumer of IS-axis spec contract; the production-site lifts that would transit CXA v2.16 §0.4 PENDING rows are CP-axis cascade work, not runtime-axis substrate work. CXA v2.16 6 PENDING → 2 LANDED + 4 carry unchanged at v2.42 publication.

(f) **ZERO cross-axis cascade at v2.42 per Q2=narrow.** Runtime spec PRESERVED VERBATIM at v1.39 (no spec extension owed; U-RT-112 implements an IS-spec contract via runtime-residence under Q-γ ratification; cross-package contract-impl is workspace-convention pattern per U-CORE-02 + U-RT-99 precedent). CP spec / AS spec / OD spec / IS spec v1.3 (just published) / CXA / ADR / ADD / PRD PRESERVED VERBATIM. Target_Stack_Commitment_v1 §5.1 PRESERVED VERBATIM.

(g) **PR shape — stacked-new-PR off `worktree-h-t-is-2-architect-rec` branch.** PR #89 (docs-half: spec v1.3 + IS plan v2.4 + arch rec §11 + clearance marker; merged or pending operator review at apply-pass session 2026-05-30 close) preserved as docs-half PR. Impl-half lands as a separate PR off the same worktree branch (or rebase to main if PR #89 merges first). Mirrors docs-half/impl-half split shape established at apply-pass session 2026-05-30.

(h) **NEW species candidate `[[is-spec-contract-runtime-axis-impl-cross-package-pattern]]`** at workflow v1.13 §7.4.7.2 — distinct from prior species 3 (resolved-but-carry-stale-inherited) + species 4 (authoring-time stale carry). Pattern: a spec axis (IS) declares a contract that requires consumer-package-internal substrates (HarnessContext + Skill + RoutingManifest at runtime axis), forcing impl residence at the consumer axis rather than the spec-author axis. Mirror precedent at U-CORE-02 (AS spec contract / harness-core impl). Cardinality 2 instances across 2 axes pre-v2.42; v2.42 adds third instance establishing pattern as workspace convention. Workflow-doc revision candidate at next workflow revision pass.

## §5 Filing footer

| Field | Value |
|---|---|
| Plan version | v2.42 (delta over v2.41) |
| Authored at | 2026-05-30 |
| Authoring authority | `.harness/architect_recommendation_h_t_is_2_artifact_tier_registry_wiring.md` §11.4 Q-γ operator-ratified (γ-2) 2026-05-30 (next-session-opener AUQ post-apply-pass-session close); session continuation 2026-05-30 |
| Net delta | +1 NEW unit (U-RT-112); +1 NEW node + 4 NEW edges (2 cross-package runtime→IS + 2 internal) at DAG; +1 coverage row at C-IS-05 §5.2; ZERO cross-axis cascade per Q2=narrow; ZERO spec amendment; ZERO contract change |
| Production binding | Co-published this arc: NEW `harness-runtime/src/harness_runtime/lifecycle/procedural_tier_snapshot.py` + NEW `harness-runtime/tests/test_procedural_tier_snapshot.py`; IS plan v2.5 sibling delta retiring U-IS-18 (RELOCATED-TO-U-RT-112); harness-is sidecar field lift at `state_ledger_write.py` per U-IS-11 ext ACs (LANDED at IS plan v2.4 carrier surface; impl at v2.42 co-publication arc) |
| Cross-axis cascade | NONE at v2.42. Producer-site lifts at ~13 CP / runtime / AS composers deferred per Q2=narrow per `[[substrate-pre-landed-consumer-deferred-multi-arc-lift]]` precedent. |
| Downstream artifacts owed | workspace `CLAUDE.md` §2.4 runtime plan row bump v2.41 → v2.42 + IS plan row bump v2.4 → v2.5 — co-published this arc; clearance marker at `.harness/clearance/Implementation_Plan_Harness_Runtime-v2_42-cleared-2026-05-30.md` per CLAUDE.md §4.5 — co-published this arc; arch rec §11.8 Q-γ closure entry — co-published this arc; retirement event filing at `.harness/phase-7d-retirement-events-batch-NN.md` (H_T-IS-2 STILL-BOUNDED → PARTIAL) — co-published this arc |
| H_T-IS-2 transit | **STILL-BOUNDED → PARTIAL** at v2.42 + IS plan v2.5 + impl + tests merge (substrate landed at IS-axis sidecar carrier + runtime-axis resolver primitive); PARTIAL → RETIRED gated on full producer-site lift across ~13 CP / runtime / AS sites per X-AL-2 second conjunct |
