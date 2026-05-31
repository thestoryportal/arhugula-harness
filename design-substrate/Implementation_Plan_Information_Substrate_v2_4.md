# Implementation Plan — Information Substrate (IS axis) — v2.4

*Revision-pass amendment to v2.3 absorbing IS spec v1.2 → v1.3 NEW §5.1 D-derivative sidecar field + NEW §5.2 resolver contract per `.harness/architect_recommendation_h_t_is_2_artifact_tier_registry_wiring.md` Q-set + apply-pass D1 ratification 2026-05-30 (Q-α=(α-1) content-hash + Q-β=(β-3) direct-compute). Skill: `implementation-planner` SKILL.md §8 revision-pass sub-mode.*

**Status:** Proposed

---

## §0 Change-note (v2.3 → v2.4)

### §0.1 Predecessor

`Implementation_Plan_Information_Substrate_v2_3.md` (v2.3 — R2 materializability conformance; canonical at HEAD `8816ce9` per workspace `CLAUDE.md` §2.4 row IS).

### §0.2 Revision scope (v2.3 → v2.4)

v2.4 absorbs **Phase 7 H_T-IS-2 substitution-retirement apply-pass** — the IS-axis substrate landing for the spec v1.2 → v1.3 amendment (NEW §5.1 + §5.2; §C-IS-02 line 170 canonical-reading patch). Per architect rec §5 + Q-set operator ratification 2026-05-30:

- **Q1 = γ-family + Q1.1 = γ** — sidecar field carrier per ADR-F2 §Consequences (c) D-derivative extension authorization; preserves §C-IS-05 F-layer six-field shape verbatim
- **Q2 = narrow** — intra-IS-axis at apply-pass; cross-axis cascade (~13 producer-site lifts across `harness-as` / `harness-cp` / `harness-runtime`) deferred to follow-on per-axis arcs per workspace `[[substrate-pre-landed-consumer-deferred-multi-arc-lift]]` precedent
- **Q3 = bundled** — single PR co-publishes spec + plan + IS resolver impl + tests + clearance marker per workspace `CLAUDE.md` §11.4 mixed-posture default
- **Q4 = inline** — §C-IS-05 footer MAY/MUST composition declared at the spec amendment
- **Q-α = (α-1) content-hash** — `Identifier = sha256(canonical_join(active_skills_versions ‖ routing_manifest_sha))`; self-describing; immune to registry drift. **Apply-time empirical orientation narrowing at v1.3:** 3-component recipe (skills + prompts + routing-manifest) → 2-component recipe (skills + routing-manifest) per X-AL-3 — `active_prompt_version` field absent at `HarnessContext`; no `PromptManifest` carrier anywhere at HEAD; prompts component deferred to v1.x runtime-binding-extension arc per spec v1.3 §5.2 Deferral footer. 55th application of `[[advisor-before-substantive-work-for-cross-axis-blockers]]` posture at pre-impl orientation
- **Q-β = (β-3) direct-compute** — no separate snapshot-keyed registry persists at H_T; resolver re-computes from current `HarnessContext` at every call; procedural artifacts persist at filesystem+git per §C-IS-02 line 163

| In scope at v2.4 | Out of scope |
|---|---|
| Revised body for U-IS-11 (`procedural_tier_snapshot_ref` sidecar field absorbed at `EntryPayload`); NEW unit U-IS-18 (`resolve_procedural_tier_snapshot` resolver primitive) | The 16 other v2.3 unit bodies — preserved verbatim per §0.4 |
| Coverage-matrix delta at C-IS-05 + C-IS-02 (NEW §5.1 + §5.2 + line 170 patch covered) | Cross-axis producer-site lifts (~13 sites across CP / runtime / AS) — deferred per Q2=narrow |
| Dependency-graph delta: NEW node U-IS-18; NEW within-axis edge U-IS-11 → U-IS-18 (caller-side optional consumption) | Engine-layer composer kw-only-callable parameter binding (CP-axis follow-on per §16.5.7 + §16.5.8 precedent) |
| Enum-byte-drift fix at `harness-is/src/harness_is/artifact_tier_registry.py` (UPPERCASE StrEnum values → lowercase per spec §C-IS-02 line 122-128 canonical) — discretionary doc-hygiene per architect rec §7 (a) | — |

### §0.3 Operator ratification decisions folded into v2.4 (decided 2026-05-30)

| ID | Question | Operator decision | Where applied |
|---|---|---|---|
| **Q1** | Reading family selection | (A) γ-family | Spec §5.1 sidecar field |
| **Q1.1** | γ-family sub-selection | (γ) sidecar field carrier | Spec §5.1 |
| **Q2** | Per-axis cascade scope bound | Narrow | This plan; ZERO CP/runtime/AS revision |
| **Q3** | Apply posture | Bundled single-PR | This arc co-publishes spec + plan + impl |
| **Q4** | §C-IS-05 footer reconciliation | Inline at spec amendment | Spec §C-IS-02 line 170 + §5.1 MAY/MUST reconciliation paragraph |
| **Q-α** | `ProceduralTierSnapshotRef` carrier shape | (α-1) content-hash | NEW U-IS-18 ACs |
| **Q-β** | Snapshot registry home + storage contract | (β-3) direct-compute | NEW U-IS-18 ACs (no separate registry; resolver pure function) |

### §0.4 Sections preserved verbatim from v2.3

| Section | Status at v2.4 |
|---|---|
| §0 (v2.3 change-note) | Superseded by this §0 |
| §1 Spec inventory | Preserved verbatim from v2.1 §1 (citation refresh IS spec v1.2 → v1.3 at §1.3 substrate-version citation per delta-only-plan-chain convention; cite-refresh is doc-hygiene, no contract amendment) |
| §2 — U-IS-01..U-IS-10, U-IS-12..U-IS-17 (16 units) | **Preserved verbatim from v2.3 §2** (which preserves the 11 CLEARED units from v2.1 by reference and carries the 6 R2-revised unit bodies) |
| §2 — U-IS-11 | **Revised at v2.4** — body amendment absorbing NEW §5.1 sidecar field at `EntryPayload`; full body in §2 below |
| §2 — U-IS-18 (NEW) | **Authored at v2.4** — new unit decomposing NEW §5.2 resolver primitive; full body in §2 below |
| §3 Dependency graph | Revised at the delta nodes/edges only (§3 below); all other within-axis edges + the acyclicity proof preserved verbatim from v2.1 §3 |
| §4 Coverage matrix | Revised at C-IS-05 + C-IS-02 rows (§4 below); all other rows preserved verbatim from v2.1 §4 |
| §5 Auxiliary-type carrier audit | Preserved verbatim from v2.3 §5 (no new auxiliary type introduced at v2.4 — `Identifier` is the existing U-IS-07 carrier; `HarnessContext` is the runtime-axis-owned cross-package import not subject to IS-axis carrier audit) |

### §0.5 Authority-chain note — no X-AL-3 risk at this arc

The spec v1.2 → v1.3 amendment is itself the authority chain (Phase 7 substantive amendment per workspace `CLAUDE.md` §11.4 mixed-posture; clearance marker filed at `.harness/clearance/Spec_Information_Substrate-v1_3-cleared-2026-05-30.md` per §4.5). v2.4 cites the spec v1.3 §5.1 + §5.2 contracts; it does not extend them. `implementation-planner` SKILL.md §2 consequence 1 (the planner never extends a spec) is satisfied.

### §0.6 Per-axis cascade discipline + transit posture

H_T-IS-2 substitution-retirement transit posture per X-AL-2:

- **STILL-BOUNDED at v2.4 (UNCHANGED).** Spec v1.3 + plan v2.4 land the contract-shape substrate (sidecar field at §5.1 + resolver primitive at §5.2 + canonical-reading patch at §C-IS-02 line 170); resolver impl + EntryPayload extension + tests are **DEFERRED** to a follow-on arc per §0.8 finding 3 of 3 (residence-decision question). Per X-AL-2 second conjunct ("substituted H_E surface no longer invoked at substitution site"), the substrate-without-impl half does NOT advance transit; H_T-IS-2 remains STILL-BOUNDED until the impl arc closes.
- **STILL-BOUNDED → PARTIAL** on a follow-on impl arc once the residence question is operator-ratified (1 of 3 options per arch rec §11) AND the resolver lands at the ratified residence AND the EntryPayload sidecar field landing co-publishes.
- **PARTIAL → RETIRED** gated on full producer-site lift completion across the ~13 sites per X-AL-2 second conjunct (every state-ledger write site supplies the sidecar field via the resolver).

Cluster-boundary call sites at HEAD continue to work without modification at v2.4 (sidecar field as authored at spec §5.1 is `Optional`, default `None`); the v2.4 substrate is contract-only until impl arc lands.

### §0.7 Status posture

`Status: Proposed` — preserved per `implementation-planner` SKILL.md §8 until any P6-CK-analog re-clearance.

### §0.8 Apply-time empirical orientation — 3 of 3 findings catalogue

Apply-pass session 2026-05-30 surfaced **3 structural surprises** at impl-time empirical orientation; the first two narrowed scope within the ratified shape; the third (residence question) is a new operator-decision territory not covered at the original architect rec Q-set.

**Finding 1 — Replay semantics ambiguity (resolved at AUQ design).** Spec §C-IS-02 line 170 phrasing was ambiguous between "verification" (re-hash compares) and "recovery" (reconstruct from entry). Pre-substantive advisor pass + empirical grep across `replay` mentions in IS spec + ADR-F2 discriminated that "replay" in IS scope is engine-replay (CP/OD layer via `idempotency_key` dedup; F2-12 carry-forward), NOT procedural-tier-state-reconstruction. Procedural artifacts persist at filesystem+git per §C-IS-02 line 163; recovery surface lives there, not at the entry. All 3 Q-α sub-shapes remained live; Q-α × Q-β coupling collapsed to 4 legal pairs. AUQ authored over 4 legal pairs at single D1. **Resolution shape:** AUQ design refinement; no spec/plan amendment.

**Finding 2 — Prompts referent absent (resolved by spec narrowing pre-commit).** Architect rec §2.4 named 3 procedural-tier components per spec line 163 (Skills, prompts, routing manifest); apply-time empirical orientation surfaced ZERO runtime binding for `active_prompt_version` (no field on `HarnessContext`; no `PromptManifest` carrier at any harness-* package; only the `prompts/` path-class taxonomy exists at `harness-is/atomic_deploy_event.py:159` PROMPTS classification — operational referent at filesystem layer, runtime-side binding absent). Per X-AL-3 the spec MUST NOT commit a content-hash recipe to a phantom referent. **Resolution shape:** Spec v1.3 §5.2 recipe narrowed from 3 components to 2 components (skills + routing-manifest) pre-commit per `[[impl-time-grounding-pass-pre-merge-revision]]`; prompts component deferred to v1.x runtime-binding-extension arc per spec §5.2 Deferral footer; plan v2.4 U-IS-18 ACs + tests + recipe block softened in lockstep.

**Finding 3 — Resolver residence cycle (HALT — operator-decision territory; ARC SPLIT).** Architect rec §5 + spec v1.3 §5.2 Deferred footer + plan v2.4 §2.3 U-IS-18 Files line assumed resolver residence at `harness-is/src/harness_is/procedural_tier_snapshot.py`. Apply-time empirical orientation surfaced dep-graph cycle: `harness-runtime/src/harness_runtime/types.py:88-90` imports from `harness_is.path_resolver` + `harness_is.workload_manifest_opt_in_schema` + `harness_is.worktree_isolation` at runtime (NOT TYPE_CHECKING-guarded). Resolver signature `resolve_procedural_tier_snapshot(harness_context: HarnessContext) -> Identifier` requires `HarnessContext` import; harness-is importing harness-runtime would create circular dep. The `harness-is` residence is **structurally foreclosed** at HEAD. **Resolution shape:** ARC SPLIT — spec v1.3 + plan v2.4 land at this arc as contract-shape substrate (Q3=bundled ratification preserved for the docs half); resolver impl + EntryPayload sidecar field landing + tests + EntryPayload-field landing all DEFERRED to a follow-on impl arc gated on operator-decision AUQ at next session (3 residence options enumerated at architect rec §11). The Q3=bundled ratification originally promised "spec + plan + IS resolver impl" — the IS-resolver-impl half is operator-decision territory not covered by Q3; halt + ratify per workspace `[[advisor-before-substantive-work-for-cross-axis-blockers]]` discipline (55th application this session at the residence-question framing — same advisor instance, same arc).

**Sub-species catalogue candidate.** `[[architect-rec-assumed-cross-package-binding-fails-impl-time-empirical-orientation]]` — distinct closure-event-class at workflow v1.13 §7.4.7.2; awaits second instance for sub-species addition. The pattern: an architect rec authored before HEAD empirical orientation makes a residence assumption (or a cross-package binding assumption); apply-time empirical orientation finds the assumption is structurally foreclosed at HEAD; arc splits between docs-half (lands) + impl-half (deferred to residence-decision AUQ). Mirror precedent: U-RT-111 v2.35-v2.39 5-rescope arc (5 STRIKE events for not-yet-built substrate); v1.3 + v2.4 + this finding 3 is a NEW shape at the architect-rec-arc layer rather than the plan-revision layer.

---

## §1 Spec inventory

[Preserved verbatim from `Implementation_Plan_Information_Substrate_v2_1.md` §1 — C-IS-01 through C-IS-10 mapping; §1.2 cluster decomposition (now 18 units across 6 clusters; U-IS-18 joins Cluster 4 at v2.4 per §3 delta); §1.3 substrate-version citation alignment (IS spec v1.3; ADR latest-version body-citations). v1.3 cite-refresh per delta-only-plan-chain convention.]

---

## §2 Atomic-unit decomposition

### §2.1 Preserved-verbatim units (15)

[`[preserved verbatim from v2.3 §2]` — U-IS-01, U-IS-02, U-IS-03, U-IS-04, U-IS-05, U-IS-06, U-IS-07, U-IS-08, U-IS-09, U-IS-10, U-IS-12, U-IS-13, U-IS-14, U-IS-15, U-IS-16, U-IS-17 — 16 units. v2.3 preserves U-IS-01, U-IS-03, U-IS-04, U-IS-07, U-IS-08, U-IS-09, U-IS-10, U-IS-13, U-IS-15, U-IS-16 from v2.1 verbatim (the 11 CLEARED minus U-IS-11 which v2.4 revises); v2.3 revised bodies for U-IS-02, U-IS-05, U-IS-06, U-IS-12, U-IS-14, U-IS-17 carry forward verbatim at v2.4.]

### §2.2 Revised units (1)

#### U-IS-11 — Implement C3-pole append-only write contract  *(v2.4 revision — §5.1 sidecar field absorbed at `EntryPayload`)*

**Implements:** [C-IS-07 §7.1, §7.3; C-IS-05 §5.1 (v2.4 NEW absorption)]

**Depends on:** [U-IS-05, U-IS-07, U-IS-08, U-IS-09]

**Inputs:** `JsonlLedgerHandle` (U-IS-05); `StateLedgerEntry` + `Actor` + `ALL_ZEROS_SENTINEL` (U-IS-07); `compute_response_hash` (U-IS-08); `construct_prior_event_hash` (U-IS-09); IS spec v1.3 §7.1 + §7.3 + **§5.1 NEW** sidecar field contract; keying tuple `(thread_id, step_id, idempotency_key)` per Stripe-style convention.

**Files affected:** C3-pole write contract (logical name: `state-ledger-write-contract`); idempotent-write deduplication primitive (logical name: `idempotent-write-dedup`). At HEAD: `harness-is/src/harness_is/state_ledger_write.py` (already landed at v2.3-conformant shape; v2.4 extends `EntryPayload` with NEW optional field).

**Scope.** v2.4 absorbs spec v1.3 §5.1 D-derivative sidecar field `procedural_tier_snapshot_ref: Identifier | None` as an additive `EntryPayload` field. Per §7.4 deferral (preserved), relationship between `WriteKey` and persisted entry shape remains caller-supplied. The sidecar field is `Optional` (default `None`) preserving backward compatibility at all existing call sites at HEAD.

**Signatures (v2.4 amendment; additive field marked):**
```
append_ledger_entry(
  ledger_handle  : JsonlLedgerHandle,
  entry_payload  : EntryPayload,
  write_key      : WriteKey
) -> WriteResult

record EntryPayload {
  action_id                       : Identifier      // action class label per §5 footer
  idempotency_key                 : Identifier
  actor                           : Actor
  timestamp                       : Timestamp
  procedural_tier_snapshot_ref    : Identifier | None = None  // v2.4 NEW — §5.1 sidecar
  // response_hash + prior_event_hash computed internally; not caller-supplied
}

record WriteKey {
  thread_id        : Identifier
  step_id          : Identifier
  idempotency_key  : Identifier
}

enum WriteResult { APPENDED, IDEMPOTENT_NOOP }
```

**Internal logic (unchanged at v2.4; sidecar field is additive metadata passed through to persisted entry).** Steps 1-8 from v2.3 §2 preserved verbatim. Persisted JSONL entry shape extends to include the sidecar field via §C-IS-07 §7.3 composition format; serialization includes `procedural_tier_snapshot_ref` as a 7th JSON key when non-`None`, omitted from the line when `None` per Pydantic `model_dump(exclude_none=True)` discipline (preserves JSONL line discipline + minimizes per-entry bytes at bootstrap entries).

**Acceptance criteria (additive at v2.4; criteria #1-#10 preserved verbatim):**

| # | Property | Criterion | Spec ref |
|---|---|---|---|
| 1-10 | [preserved verbatim from v2.1 §2] | [preserved verbatim] | [preserved verbatim] |
| 11 | Sidecar field optional | `EntryPayload` accepts `procedural_tier_snapshot_ref: Identifier \| None = None`; existing call sites at HEAD continue without modification | §5.1 |
| 12 | Sidecar serialization discipline | When non-`None`, persisted JSONL line includes `procedural_tier_snapshot_ref` as 7th key per §7.3 composition format; when `None`, key omitted (Pydantic `exclude_none=True` shape) | §5.1 + §7.3 |
| 13 | Sidecar round-trip | Persisted entry round-trips through `compute_response_hash` deterministically; the hash includes the sidecar field's value contribution when non-`None` | §5.1 + §6.2 |
| 14 | MAY/MUST composition | `action_id` retains existing action-class-label semantics independently of `procedural_tier_snapshot_ref` per §C-IS-02 line 170 reconciliation; entry with both fields populated is valid | §C-IS-02 line 170 + §5.1 |

**Tests (additive at v2.4; existing tests preserved verbatim):**
- v2.1 tests: [preserved verbatim — 13 tests covering criteria 1-10]
- NEW v2.4: `test_entry_payload_accepts_none_procedural_tier_snapshot_ref_by_default`, `test_entry_payload_accepts_non_none_procedural_tier_snapshot_ref`, `test_append_persists_sidecar_field_when_non_none`, `test_append_omits_sidecar_key_when_none`, `test_response_hash_includes_sidecar_field_contribution`, `test_round_trip_with_sidecar_field_deterministic`, `test_action_id_and_sidecar_compose_without_conflation`.

**Rollback boundary (unchanged at v2.4):** Revert write contract + dedup primitive + sidecar field. Cross-axis writers (D1 engine event history, D5 audit-ledger, D2 sandbox-violation events, D6 cost-attribution) all block.

### §2.3 New units (1)

#### U-IS-18 — Implement `resolve_procedural_tier_snapshot` resolver primitive  *(v2.4 NEW)*

**Implements:** [C-IS-05 §5.2 (v1.3 NEW)]

**Depends on:** [U-IS-07] (for `Identifier` type-alias)

**Inputs:** `HarnessContext` (runtime-axis-owned cross-package import; consumed at signature position; carrier resides at `harness-runtime/src/harness_runtime/types.py:HarnessContext`); `Identifier` (U-IS-07); IS spec v1.3 §5.2 resolver contract.

**Files affected:** Procedural-tier snapshot resolver primitive (logical name: `procedural-tier-snapshot-resolver`); **concrete module residence DEFERRED** per spec v1.3 §5.2 "Deferred to implementation discretion" footer ("whether the resolver lives at `harness-is` or at a sibling package"). Apply-time empirical orientation 2026-05-30 surfaced a dep-graph cycle constraint: `harness-runtime/.../types.py` imports from `harness_is.path_resolver` at runtime (line 88), forecloseing the architect-rec-assumed `harness-is` residence. See §0.8 finding 3 of 3 + `.harness/architect_recommendation_h_t_is_2_artifact_tier_registry_wiring.md` §11 for the 3-residence-option AUQ owed at next session.

**Scope.** Pure-function resolver implementing the spec v1.3 §5.2 content-hash recipe + direct-compute storage discipline. NO separate registry persistence; NO mutation state; resolver re-computes from current `HarnessContext` state at every call.

**Signatures:**
```
resolve_procedural_tier_snapshot(harness_context: HarnessContext) -> Identifier

# Internal helper exposed for testing:
_canonicalize_procedural_tier_payload(
  active_skills_versions: list[str],
  routing_manifest_sha: str,
) -> bytes
```

**Internal logic (v1.3 — 2-component scope; prompts deferred):**
1. Extract `active_skills_versions: list[str]` from `harness_context.skills` (read `SkillManifest.version_sha` per each entry in the `dict[SkillID, Skill]` mapping).
2. Compute `routing_manifest_sha: str` as the SHA-256 hex digest of `harness_context.routing_manifest.model_dump_json(by_alias=False)` byte-encoded (RoutingManifest is a frozen Pydantic v2 BaseModel per `harness-cp/.../routing_manifest_residence.py`).
3. Sort + dedup `active_skills_versions` ascending lexicographic order.
4. Build canonical payload dict: `{"active_skills_versions": list[str], "routing_manifest_sha": str}` ordered alphabetically by key (2 components at v1.3; prompts component joins at v1.x per spec §5.2 deferral footer).
5. Serialize via `json.dumps(payload, sort_keys=True, separators=(",", ":"))`; encode UTF-8.
6. Return `sha256(canonical_bytes).hexdigest()` as `Identifier`.

**Acceptance criteria (v1.3 — 2-component scope):**

| # | Property | Criterion | Spec ref |
|---|---|---|---|
| 1 | Pure function | No side effects; no state mutation; same `HarnessContext` input yields identical output across calls | §5.2 |
| 2 | Content-hash recipe byte-exact | Output is lowercase hex SHA-256 (64 chars) of canonical-JSON-bytes per §5.2 recipe; canonical-JSON via `sort_keys=True` + `separators=(",", ":")` | §5.2 + §6.1 |
| 3 | Alphabetical key ordering | Canonical payload dict ordered alphabetically by key (active_skills_versions, routing_manifest_sha) — 2 components at v1.3 | §5.2 |
| 4 | Skills-versions list canonicalization | `active_skills_versions` sorted ascending lexicographic + dedup'd before JSON serialization | §5.2 |
| 5 | Different HarnessContext state ⇒ different hash | Two HarnessContexts differing in any one of the two presently-bound procedural-tier components produce different content-hash outputs | §5.2 |
| 6 | Same HarnessContext state ⇒ same hash | Two HarnessContexts with identical procedural-tier components produce byte-identical content-hash outputs (cross-instance determinism) | §5.2 |
| 7 | Return type `Identifier` | Output type matches U-IS-07 `Identifier` alias (str) | §5.2 + U-IS-07 |
| 8 | Direct-compute discipline | No module-level state; no caching at v2.4 (per-call recompute; same-input memoization deferred to implementation discretion) | §5.2 |
| 9 | No HarnessContext mutation | Function does not mutate or assign to `harness_context` or any of its attributes | §5.2 (pure) |
| 10 | Empty-skills-set handled | `active_skills_versions=[]` produces a valid canonical-JSON serialization (empty JSON array `[]`) and a deterministic hash | §5.2 |
| 11 | Prompts-component deferral discipline | Resolver does NOT attempt to read any prompt-version field from `HarnessContext`; canonical payload contains exactly 2 keys at v1.3 (`active_skills_versions` + `routing_manifest_sha`); 3rd key (`active_prompt_version`) absent per spec §5.2 deferral footer | §5.2 (Prompts deferred) |

**Tests:**
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
- `test_canonicalize_helper_byte_stable_across_python_versions`

**Cluster-boundary call site discipline (deferred to per-axis follow-on arcs per Q2=narrow).** Composers with `HarnessContext` access at firing time consume `resolve_procedural_tier_snapshot(ctx)` at entry-construction time. Engine-layer composers without `HarnessContext` access at firing time receive a `Callable[[], Identifier]` kw-only parameter bound at runtime composition time per CP spec v1.25 §16.5.7 + §16.5.8 `ledger_writer` precedent. Producer-site lift not at v2.4 scope.

**Rollback boundary:** Revert resolver module. Sidecar field at U-IS-11 `EntryPayload` continues to accept `None` (existing semantics preserved); cross-axis producer-site lifts (when authored at follow-on arcs) lose the resolver source-of-truth and would need either a re-author or a stub returning a sentinel value.

---

## §3 Dependency graph

### §3.1 Dependency-graph delta (v2.4)

NEW node + 1 NEW within-axis edge:

- **NEW node:** U-IS-18 at Cluster 4 (state-ledger contract pair; sibling to U-IS-11 + U-IS-12)
- **NEW edge:** U-IS-11 → U-IS-18 (caller-side optional consumption; U-IS-18 is the source-of-truth for the sidecar field's value when consumer composer threads the resolver — but U-IS-11 itself does NOT require U-IS-18 at the type-graph layer; U-IS-11's `EntryPayload` accepts the `Identifier | None` field independently of resolver impl. Edge declared for caller-composition discipline only; ZERO Kahn-acyclicity impact.)
- **NEW edge:** U-IS-18 → U-IS-07 (existing carrier dependency — `Identifier` type-alias)

Acyclicity preserved at v2.4. All other within-axis edges + topological-sort order preserved verbatim from v2.1 §3.

### §3.2 Cluster decomposition refresh

| Cluster | Units at v2.4 |
|---|---|
| 1 (path + tier) | U-IS-01, U-IS-02, U-IS-03 |
| 2 (git substrate) | U-IS-04, U-IS-05, U-IS-06 |
| 3 (entry primitive) | U-IS-07, U-IS-08, U-IS-09, U-IS-10 |
| **4 (state-ledger contract pair + resolver)** | **U-IS-11, U-IS-12, U-IS-18** (NEW at v2.4 — sidecar field + resolver primitive) |
| 5 (shadow-Git checkpoint) | U-IS-13, U-IS-14 |
| 6 (worktree-isolation) | U-IS-15, U-IS-16, U-IS-17 |

---

## §4 Coverage matrix

### §4.1 Coverage-matrix delta (v2.4)

| Contract | Spec § | Units | Coverage |
|---|---|---|---|
| C-IS-05 (was 1 unit at v2.3) | **§5 + NEW §5.1 + NEW §5.2** | U-IS-07 (entry-shape carrier) + **U-IS-11 (v2.4 sidecar field absorption)** + **U-IS-18 (v2.4 resolver primitive)** | ✅ |
| C-IS-02 (line 170 v1.3 canonical-reading patch) | §2 | U-IS-11 (sidecar field carrier consumed) + U-IS-18 (resolver source-of-truth) | ✅ |

All other coverage-matrix rows preserved verbatim from v2.1 §4.

---

## §5 Auxiliary-type carrier audit

[Preserved verbatim from v2.3 §5. No new auxiliary type introduced at v2.4: `Identifier` is the existing U-IS-07 carrier; `HarnessContext` is the runtime-axis-owned cross-package import not subject to IS-axis carrier audit (per `[[carrier-home-defect-pattern]]` — cross-axis types in one axis package = Class 1 cycle; `HarnessContext` is canonically homed at `harness-runtime` per v1.37 §C-RT-04, consumed at U-IS-18 signature position via type-only import).]

---

## §6 Filing footer

| Field | Value |
|---|---|
| Artifact | `Implementation_Plan_Information_Substrate_v2_4.md` |
| Authored at | Phase 7 H_T-IS-2 substitution-retirement apply-pass session 2026-05-30 |
| Authoring authority | `.harness/architect_recommendation_h_t_is_2_artifact_tier_registry_wiring.md` operator-ratified 2026-05-30 + apply-pass D1 Q-α + Q-β ratification |
| Predecessor | `Implementation_Plan_Information_Substrate_v2_3.md` |
| Successor consumption | Phase 7 7b implementation arcs at IS-axis + follow-on per-axis cascade arcs (CP / runtime / AS) |
| Revision policy | Per delta-only-plan-chain convention; revisions route to spec-amendment-first then plan-revision-pass per workspace `CLAUDE.md` §4.3 |
