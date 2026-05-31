# Architect recommendation — H_T-IS-2 artifact-tier registry wiring

**Filed:** 2026-05-30
**Parent ledger row:** `harness-is/CLAUDE.md` §4.1 H_T-IS-2 (STILL-BOUNDED; "typed library exists; no bootstrap composer invokes it; cross-tier traceability invariant unenforced at append-time per ledger v2 §3")
**Spec anchor:** `Spec_Information_Substrate_v1.md` §C-IS-02 §"Tier composition contract" line 170:
> Every `durable`-tier ledger entry references the `procedural`-tier artifacts in scope at the entry's write-time via the `action_id` field (per C-IS-05). This composition enables replay of the procedural-tier state at any prior durable-tier entry timestamp.
**Scope classification:** Phase 7 → design-phase Class 1 back-flow (X-AL-3 protected; new design surface needed before impl).
**Status:** RECOMMENDATION-AWAITING-OPERATOR-RATIFICATION

---

## §1 What this resolves

The IS spec mandates a structural composition (line 170) — every `durable`-tier ledger entry must reference the `procedural`-tier artifacts (Skills, prompts, routing manifest) in scope at write-time via `action_id`, with the contract being "replay procedural-tier state at any prior durable-tier entry timestamp."

The composition is unenforced at every state-ledger write site at HEAD `8816ce9`. The typed registry substrate exists (`harness-is/src/harness_is/artifact_tier_registry.py` — populated `ARTIFACT_TIER_REGISTRY`); no consumer reads it; no `action_id` at any production site encodes procedural-tier artifact references.

H_T-IS-2 is the last STILL-BOUNDED row at the IS axis (8/9 RETIRED; only IS-2 open). It is structurally distinct from the sub-species 10 `gate-text-stale-vs-production-landings` audit shape (foreclosed at the batch-39 advisor pre-substantive pass per `harness-is/CLAUDE.md` line 142): line 170 is a substantive runtime gate at append-time, not a categorical-mismatch or H_E-canonical-substrate framing.

This recommendation surfaces three structural readings — (α) encode-in-action_id, (β) canonical-reading narrowing, (γ) sidecar field carrier — plus a γ' sub-variant, with a single decisive discriminator that collapses one of them at empirical orientation.

---

## §2 Empirical state at HEAD `8816ce9`

### §2.1 Registry substrate

`harness-is/src/harness_is/artifact_tier_registry.py` — **fully typed and populated**:

- `ArtifactTier` StrEnum: 5 members (`WORKING` / `EPISODIC` / `SEMANTIC` / `PROCEDURAL` / `DURABLE`).
- `ArtifactTierMetadata` frozen Pydantic v2 BaseModel: per-tier metadata (description, substrate residence, survival scope).
- `ARTIFACT_TIER_REGISTRY: Mapping[ArtifactTier, ArtifactTierMetadata]` — `MappingProxyType`-wrapped immutable mapping populated at module load.
- Exported at `harness-is/src/harness_is/__init__.py` via `ARTIFACT_TIER_REGISTRY`, `ArtifactTier`, `ArtifactTierMetadata`.
- Siblings: `git_tier_sub_role_taxonomy.py`, `path_class_registry.py`.

**No substrate-authoring required** for the consumer-site lift arc. The registry is the lookup surface; the missing piece is a consumer that reads it at state-ledger write time AND a procedural-tier-artifacts-in-scope resolver that the consumer invokes.

### §2.2 `action_id` at production write sites

Survey of `action_id=` construction across `harness-*/src/`:

| Site | Pattern | Encodes procedural-tier refs? |
|---|---|---|
| `harness-as/.../secret_fetch_audit.py:91` | `Identifier(str(uuid.uuid4()))` | No |
| `harness-cp/.../pause_resume_protocol.py:678/796/915` | `Identifier(_PAUSE_RESUME_ACTION_ID)` / `_PAUSE_CAPTURED_ACTION_ID` / `_RESUME_ATTEMPTED_ACTION_ID` (module constants) | No |
| `harness-cp/.../sibling_ledger_entry_composition.py:145` | `Identifier(action_id)` (pass-through) | No |
| `harness-cp/.../per_step_override_evaluator.py:200` | `ActionID(audit_entry.action_id)` (audit-half pass-through) | No |
| `harness-cp/.../per_step_override_evaluator.py:226` | `ActionID(f"{workflow_id}\|\|{step_id}")` (idempotency-key-shape composition) | No |
| `harness-cp/.../per_step_override_evaluator.py:309` | `Identifier(_OVERRIDE_ACTION_ID)` (module constant) | No |
| `harness-cp/.../workload_binding_engine_class_selection.py:343` | `Identifier(_SELECTION_ACTION_ID)` (module constant) | No |
| `harness-cp/.../hitl_as_tool_call_rewriting.py:286` | `Identifier(_HITL_TOOL_CALL_REWRITING_ACTION_ID)` (module constant) | No |
| `harness-cp/.../workflow_driver.py:1344` | `Identifier(str(action_id))` (pass-through) | No |
| `harness-cp/.../parent_fanout_close_entry.py:219` | `parent_action_id` (parent-derived) | No |
| `harness-is/.../shadow_git_rollback.py:115` | `Identifier(f"rollback:{checkpoint_id}")` (prefix-shape class label) | No |
| `harness-cp/.../sub_agent_gate_level_descent.py:200` | `ActionID(f"{parent_action_id}\|\|sub-agent")` (parent-suffix composition) | No |

Pattern: `action_id` at HEAD carries **action-class labels** (module constants) and **occasionally** idempotency-key-shape disambiguators or rollback-class prefixes. None reference procedural-tier artifact versions. The line 170 contract is uniformly unenforced.

### §2.3 IS spec §C-IS-05 field definition

Per spec line 264:

> `action_id` | Identifier — unique per action occurrence | Identifies the action this entry records | Unique within the ledger; harness-generated; **MAY encode action class / sub-class metadata**

And the §5 footer:

> **Deferred to implementation discretion.** Specific identifier format for `action_id` (UUID v4 / ULID / monotonic-counter); ... per-workload-class extensions to the six-field shape (D-derivative per ADR-F2 §Consequences (c)).

The spec actively defers `action_id` *format* to implementation discretion and permits (does not mandate) action-class encoding. The §C-IS-02 line 170 contract that `action_id` "references procedural-tier artifacts" is structural at the §2 tier-composition level but unenforced at the §5 field-shape level. **Reading (β) below operates on this gap** — narrow the structural contract to the format-specific level where §5 is silent.

### §2.4 Procedural-tier mutability mid-run (decisive discriminator)

Runtime spec v1.32 §14.17 + C-RT-15 §14.5.1 + `HarnessContext.activate_skill(...)` at `harness-runtime/src/harness_runtime/types.py:1637-1668`: skills activate at **3 hook firing sites** mid-run:

1. per-LLM-dispatch (`SkillActivationMode.TOOL_SEARCH`)
2. per-workflow-init (`SkillActivationMode.FRONTMATTER_ONLY`)
3. operator-explicit `HarnessContext.activate_skill(...)` (`SkillActivationMode.FILESYSTEM_READ`)

Procedural-tier state — specifically, which skills are active — **mutates between durable-tier entries within a single run**. The line 170 contract that procedural-tier state must be replayable at any prior durable-tier entry timestamp therefore requires **per-entry granularity**.

**This forecloses (β-honest) reading at the obvious narrowing target** (run-boundary git HEAD SHA as procedural-tier reference): a run-boundary snapshot cannot replay a per-entry mid-run mutation.

(See §3 for the structural consequence; this is load-bearing for the option-space collapse.)

### §2.5 Enum-byte-drift adjacent sub-finding

| Site | Tier names |
|---|---|
| Spec §C-IS-02 §2 five-tier table | lowercase: `working`, `episodic`, `semantic`, `procedural`, `durable` |
| Registry `ArtifactTier` StrEnum values | UPPERCASE: `"WORKING"`, `"EPISODIC"`, `"SEMANTIC"`, `"PROCEDURAL"`, `"DURABLE"` |

**Drift.** Not blocking for this architect rec, but the spec amendment co-published with the chosen reading should resolve the drift in one of two directions: either (i) spec canonical-reading amendment declaring UPPERCASE is the canonical form per the registry, or (ii) registry refresh to lowercase byte-matching the spec. Surface as adjacent fix in the apply-pass arc; do not bundle into the reading-selection AUQ.

---

## §3 The three readings

### (α) Encode procedural-tier reference IN `action_id`

**Shape.** Repurpose `action_id` from action-class label semantics to procedural-tier-referencing semantics. `action_id` becomes a structured composition `{action_class}:{procedural_tier_artifacts_in_scope_digest}:{occurrence_disambiguator}` — concretely, e.g., `pause:sha256(active_skill_versions || prompt_version || routing_manifest_sha):uuid`.

**Spec amendments owed.**
- §C-IS-05 field-spec footer: replace "MAY encode action class / sub-class metadata" with "MUST encode procedural-tier artifacts in scope per §C-IS-02 line 170."
- §C-IS-05 "Deferred to implementation discretion" footer: remove or narrow the UUID/ULID/monotonic-counter discretion clause for the part that conflicts with the new structural requirement.

**Per-axis cascade scope.** Wide.
- ~13 producer sites across `harness-as` / `harness-cp` / `harness-is` need refactor.
- ~9 module-level `_*_ACTION_ID` constants RETIRED.
- Every producer site needs `HarnessContext` access for procedural-tier resolver lookup (some currently don't have it — e.g., engine-layer pause/resume composers run before context-binding completes).
- Test fixtures + composer signatures change at every CP §16.5 composer.
- CP spec §16.5.4 per-composer disambiguator-note table extends (every row gains a procedural-tier-component clause).

**Bounded sub-variant (α'): registry-keyed prefix only.** Encode only the procedural-tier registry key (e.g., 32-bit digest of active-skills-version-set) as a fixed-width segment, not the full per-artifact list. Resolution at replay queries the registry by digest. Saves bytes; preserves the structural contract; doesn't require unbounded `action_id` length.

**Risk profile.** High. Breaks existing module-constant pattern; conflates two semantic roles in one field; producer-site refactor across 3 axes; engine-layer composers without context-binding need separate resolution path. The (γ) reading exists specifically to avoid this risk.

---

### (β) Canonical-reading narrowing of line 170

**Shape.** Amend §C-IS-02 line 170 at the canonical-reading layer to weaken the per-entry granularity claim. Two sub-variants:

- **(β-1) Run-boundary granularity.** Replace "at any prior durable-tier entry timestamp" with "at the entry's run-boundary snapshot." Procedural-tier reference becomes a run-init recorded git HEAD SHA (single entry per run records the procedural-tier snapshot; subsequent entries inherit).
- **(β-2) Tier-class-only reference.** Replace "references the procedural-tier artifacts in scope" with "references the procedural tier class." `action_id` already prefixes (`pause:`, `rollback:`, etc.) trivially satisfy a tier-class reference; line 170 collapses to documentation of existing behavior.

**Spec amendments owed.**
- §C-IS-02 §"Tier composition contract" line 170 canonical-reading amendment.
- (β-1) NEW per-run procedural-tier-snapshot entry contract at §C-IS-02 OR §C-IS-05 (where does the snapshot land in the ledger).
- (β-2) §C-IS-02 line 170 collapses to a no-op canonical-reading observation; ZERO implementation surface.

**Per-axis cascade scope.** (β-1) Narrow — one new entry-type per run, one producer (bootstrap stage); ZERO refactor at existing sites. (β-2) Zero — pure documentation amendment.

**Mid-run-mutability discriminator (decisive).** (β-1) is **structurally false** for the contract as currently worded: a run-boundary snapshot cannot replay a per-LLM-dispatch skill-activation mutation that occurred between two durable-tier entries within the run. To make (β-1) honest, the contract must additionally be narrowed to "at run-boundary granularity, not at per-entry granularity" — which weakens the replay guarantee to the point where the original contract's purpose (audit-trail of which procedural artifacts informed a given durable entry) is lost.

(β-2) collapses the contract to triviality. The spec's stated purpose ("This composition enables replay of the procedural-tier state at any prior durable-tier entry timestamp") becomes vacuous.

**Honest framing of (β).** It is a **scope-reduction**, not a scope-satisfaction. (β-1) requires admitting "we are not replayable at per-entry granularity"; (β-2) requires admitting "the replay claim is documentation, not contract." Either is a legitimate architectural posture (per §C-IS-05's actively-deferred footer, the spec authors anticipated implementation might not fully realize the line 170 vision) — but it is *operator-decision territory*, not architect recommendation territory. The architect rec recommends (β) only if operator explicitly accepts the scope-reduction.

---

### (γ) Sidecar procedural-tier-snapshot field carrier

**Shape.** Add a 7th field to the state-ledger entry shape: `procedural_tier_snapshot_ref: Identifier | None` — references a separate registry-keyed procedural-tier snapshot (the active skills version set + prompt version + routing manifest SHA at write-time). `action_id` preserves existing action-class label semantics verbatim; the line 170 contract is satisfied by the new sidecar field, NOT by `action_id` encoding.

The sidecar field is authorized per §C-IS-05 footer "per-workload-class extensions to the six-field shape (D-derivative per ADR-F2 §Consequences (c))" — sidecar additions are the documented extension surface.

**Variant (γ'): in-line mutation event in the ledger.** Instead of a sidecar reference field on every entry, emit a **procedural-tier-mutation event** as a distinct durable-tier entry whenever procedural-tier state changes (skill activation, prompt update, routing manifest change). Subsequent durable-tier entries are replayable by reading-back to the most recent procedural-tier-mutation event. `action_id` and the 6-field shape preserve verbatim; line 170 is satisfied by ledger-time-ordering, not by per-entry sidecar.

**Spec amendments owed.**
- **(γ)** §C-IS-05 NEW §5.X sub-section authoring `procedural_tier_snapshot_ref` as a documented D-derivative extension field. NEW §C-IS-NN contract surface for the procedural-tier snapshot registry (separate from `ARTIFACT_TIER_REGISTRY` — the snapshot is per-write-time *instance* of procedural-tier state, not the static tier metadata).
- **(γ')** §C-IS-02 NEW §2.X sub-section authoring procedural-tier-mutation event as a §C-IS-05 entry sub-class. NEW per-axis emission contracts at runtime spec for the 3 skill-activation hook sites + per-deployment-surface for prompt/routing-manifest mutation surfaces.

**Per-axis cascade scope.**
- **(γ)** Medium. ~13 producer sites add one kwarg to the entry payload constructor (resolver lookup); engine-layer composers still need context-binding resolution path. NEW per-run procedural-tier-snapshot registry composer + storage backend. ZERO refactor of existing `action_id` semantics. NEW reader path at replay.
- **(γ')** Narrow at producer sites (existing entries unchanged; only 3-N hook sites NEW-emit a mutation event), wider at replay (replay logic reads-back to most recent mutation event before reconstructing procedural-tier state at any given entry timestamp).

**Risk profile.** Medium. (γ) preserves existing semantics; threads a new field; producer-site touch is uniform additive; replay surface gains a lookup-by-ref dimension. (γ') preserves both existing semantics AND existing entry shape; replay logic gets more complex; mutation-event emission needs guaranteed-before-next-entry ordering (which the ledger's hash-chain ordering already provides).

(γ') is structurally closer to event-sourcing canonical patterns; (γ) is structurally closer to snapshot-keyed audit-log patterns. Both are sound.

---

## §4 The decisive discriminator: mid-run mutability

Empirical state at §2.4 establishes: procedural-tier state mutates between durable-tier entries within a single run (3 skill-activation hook firing sites + operator-explicit method).

**Consequence:**
- **(β-1) is forecloseable** — run-boundary snapshot cannot replay per-entry mid-run mutation. Operator must accept scope-reduction at the replay-guarantee layer to choose (β-1).
- **(β-2) is forecloseable** — collapses the contract to documentation; the audit-trail purpose is lost.
- **(α) and (γ) and (γ') honestly satisfy line 170** at per-entry granularity.

Among (α) / (γ) / (γ'):
- (α) is closest to the literal spec text ("via the `action_id` field") but requires breaking the existing action-class label pattern at ~13 sites and conflicts with §C-IS-05's footer-deferred discretion clause.
- (γ) preserves all existing semantics; threads one new field uniformly; requires NEW per-write procedural-tier resolver but uses ADR-F2 §Consequences (c) D-derivative extension authorization explicitly.
- (γ') preserves all existing semantics AND the 6-field shape; uses ledger-time-ordering as the replay mechanism; structurally aligns with event-sourcing patterns.

---

## §5 Recommendation: **(γ) sidecar field carrier**, with (γ') as second-choice and (β-1) as scope-reduction option

### Decisive structural argument

The §C-IS-05 footer explicitly authorizes D-derivative extensions to the 6-field shape. (γ) IS that extension shape. It preserves `action_id`'s actively-deferred discretion at the format layer + preserves the existing module-constant action-class label pattern at all 13 production sites + adds the line 170 satisfaction at a new field whose semantics are **only** the procedural-tier reference (no conflation with action-class labeling).

(α) requires re-purposing `action_id` away from the §C-IS-05 footer-deferred discretion — a structurally larger ask than authoring a new D-derivative field. The §C-IS-05 footer is the operator-ratified posture; (α) un-ratifies it.

### Workspace-pattern argument

(γ) mirrors the U-OD-40 `CostRecordAuditPayload` (CP spec v1.24 §28.10) + the pause/resume `PauseResumeAuditPayload` (OD spec v1.11 §C-OD-30.4) precedent: **add a typed sidecar carrier when an axis composition requires per-entry metadata distinct from the entry's primary type**. Both precedents preserved the primary entry type verbatim + added the sidecar at the D-derivative extension layer.

(α) has no workspace precedent — every prior cross-axis composition added a sidecar/converter, never re-purposed an existing canonical field's semantics.

### Cost of (γ)

A new resolver primitive owed at IS-axis: `resolve_procedural_tier_snapshot(harness_context) -> ProceduralTierSnapshotRef`. The 13 producer sites add one kwarg + one resolver-lookup call. Engine-layer composers without `HarnessContext` access at firing time receive `resolve_procedural_tier_snapshot: Callable[[], ProceduralTierSnapshotRef]` as a kw-only parameter at the composer function signature, bound at runtime composition time per the §16.5.7 + §16.5.8 `ledger_writer` kw-only-callable-bound-at-runtime-wiring precedent established at CP spec v1.25 (U-CP-78 / U-CP-79 engine-layer free functions adopt this discipline). The composer never needs to thread `HarnessContext`; the callable closure captures whatever resolution-time state is needed.

### Cost of (γ')

Larger replay-layer surface than (γ). Mutation events introduce a new entry sub-class at §C-IS-05; replay logic gains a lookup-back-by-class dimension. Acceptable if the operator prefers event-sourcing canonical patterns at the ledger layer; the workspace has not yet adopted event-sourcing posture explicitly.

### Cost of (β-1)

Honest scope-reduction: documented loss of per-entry replay guarantee. Cheapest implementation; operator must accept the audit-trail-purpose narrowing.

### Why (α) is NOT recommended

Three arguments, in descending strength:

1. **Producer-site refactor cost across 3 axes.** ~13 producer sites + ~9 module-level `_*_ACTION_ID` constants RETIRED + every composer signature changes + CP §16.5.4 per-composer disambiguator-note table extends row-by-row. (γ) is uniform-additive (one kwarg, one resolver call per site) — strictly smaller surface.
2. **No workspace precedent.** Every prior cross-axis composition added a sidecar/converter, never re-purposed an existing canonical field's semantics. (γ) is on-pattern; (α) is off-pattern.
3. **§C-IS-05 footer composition cost.** The §C-IS-05 footer "MAY encode action class / sub-class metadata" is permissive; (α) is a *narrowing* (MUST procedural-tier ref) that composes with the MAY clause (action_id MAY still encode action class AND MUST encode procedural-tier ref — both can hold). (α) does NOT un-ratify the footer; it tightens the structural floor. The footer-narrowing is a legitimate spec amendment; this is the weakest of the three arguments against (α) — it's a cost, not a foreclosure.

---

## §6 Per-axis cascade scope per reading (impl-arc sizing)

| Reading | IS-axis | CP-axis | runtime-axis | OD-axis | Sessions estimate |
|---|---|---|---|---|---|
| (α) | spec amendment + resolver primitive | refactor ~9 `_*_ACTION_ID` constants + ~13 producer site signatures + §16.5.4 disambiguator-note table extension | refactor `cp_is_wiring.py` 7 adapters + bootstrap context-binding for engine-layer | ZERO direct, indirect via audit-ledger reads | 4-6 sessions |
| (β-1) | NEW per-run snapshot contract | ZERO refactor | NEW bootstrap stage emitting run-boundary snapshot entry | ZERO direct | 1-2 sessions |
| (β-2) | spec doc-amendment only | ZERO | ZERO | ZERO | 1 session |
| (γ) | NEW §C-IS-05 §5.X sidecar field + NEW snapshot resolver primitive | thread resolver-lookup at ~13 producer sites + 1 kwarg at every EntryPayload constructor | wire resolver factory at bootstrap stage 5 + sentinel-resolution at runtime wiring layer | ZERO direct | 3-4 sessions |
| (γ') | NEW §C-IS-02 mutation-event sub-class | ZERO direct, indirect via replay logic | NEW emission contracts at 3 skill-activation hook firing sites + per-deployment prompt/routing-manifest mutation emissions | ZERO direct | 3-5 sessions |

---

## §7 Adjacent sub-findings (not patched per FM-2)

- **(a)** Enum-byte-drift at §2.5 — spec lowercase tier names vs registry UPPERCASE StrEnum values. Resolve in apply-pass arc co-published with chosen reading. Not blocking.
- **(b)** §C-IS-05 footer "Deferred to implementation discretion" composes with §C-IS-02 line 170 structural contract at the `action_id` format layer per a MAY/MUST narrowing relationship — (α) narrows the format layer (MAY encode action class AND MUST encode procedural-tier ref); (β) narrows line 170 itself; (γ) preserves both by using D-derivative extension authorization (the new field carries the MUST; `action_id` retains the MAY). Architect rec surfaces this as a spec-amendment-shape observation (not an inconsistency); downstream apply-pass arc resolves the shape per chosen reading.
- **(c)** Engine-layer composers without `HarnessContext` access at firing time (`pause_resume_protocol.py` free functions at line 678/796/915) accept a kw-only callable parameter bound at runtime composition time per the CP spec v1.25 §16.5.7 + §16.5.8 `ledger_writer` precedent. Under (α) the callable returns the procedural-tier-ref-encoded action_id segment; under (γ) the callable returns the procedural-tier-snapshot ref directly. Same pattern; different return type.
- **(d)** `git_tier_sub_role_taxonomy.py` + `path_class_registry.py` sibling registries — not surveyed at this rec; potential candidates for additional consumer-site lifts that compose with the chosen reading. Out of scope for this rec; revisit at apply-pass arc.
- **(e)** Workspace pattern catalogue at this rec: `[[procedural-tier-mutability-as-decisive-discriminator]]` — first instance of mid-run-mutability discriminator being load-bearing for an architect-rec arc; mirrors but distinguishes from `[[substrate-pre-landed-consumer-deferred-multi-arc-lift]]` (substrate ready, mutability ready, only consumer-site lift owed) by surfacing mutability as a contract-shape discriminator BEFORE consumer-site lift planning.

---

## §8 Operator AUQ shape (proposed)

Fired as a two-stage chain to honor the AskUserQuestion 4-option cap (5 readings ÷ 3 families). (β-2) is omitted from the AUQ chain as a scope-collapsing comparator only; surfaced at §9 do-nothing baseline for narrative reference, not as a peer choice.

**Q1 — Reading family selection (4 options).**
- (A) γ-family — sidecar carrier (recommended); choose between (γ) sidecar field vs (γ') mutation event at Q1.1
- (B) α — encode-in-action_id; refactor ~13 producer sites + retire ~9 module constants
- (C) β-1 — run-boundary snapshot narrowing (scope-reduction; accepts loss of per-entry replay guarantee)
- (D) Hold — surface a 4th alternative or change scope before picking

**Q1.1 — γ-family sub-selection (fires only if Q1 = A).**
- (γ) sidecar field carrier (recommended; uniform additive surface)
- (γ') mutation event in ledger (event-sourcing posture; cleaner at entry-shape layer)

**Q2 — Per-axis cascade scope bound.** Narrow (intra-IS-axis only at apply-arc; cross-axis cascade deferred) OR wide (apply-pass cascades to CP + runtime in same arc)?

**Q3 — Apply posture.** Single bundled apply-pass arc (spec amendment + plan revision + consumer-site lift co-published per workspace `CLAUDE.md` §11.4) OR phased (spec first, then plan, then impl per arc)?

**Q4 — Adjacent finding (b) §C-IS-05 footer reconciliation.** Address inline at the spec amendment (declare the MAY/MUST composition shape at the footer/§2-line-170 layer) OR defer to follow-on canonical-reading patch?

Enum-byte-drift adjacent fix per §2.5 is NOT an operator-decision — spec is canonical authority; default direction is registry-refresh-to-spec-lowercase at the apply-pass arc per workspace doc-hygiene precedent. Surfaced as a §7 adjacent-finding apply-pass deliverable, not as an AUQ ratification.

---

## §9 What changes if operator picks differently than recommended

- **If (γ') ratified:** Apply pass authors §C-IS-02 mutation-event sub-class + 3 hook-site emission contracts; the 13 producer sites preserve verbatim. Replay logic at IS-axis gains lookup-back-by-class. Cost analysis at §6 still holds; (γ') is a sibling-shape to (γ) at the cost dimension.
- **If (α) ratified:** Spec amendment at §C-IS-05 footer un-ratifies the discretion clause; §16.5.4 disambiguator-note table extends; ~9 module-constants RETIRED; ~13 producer sites refactored. Cross-axis cascade is wide; sessions estimate 4-6. The α' sub-variant (registry-keyed prefix only) reduces the per-site refactor cost but preserves the footer-un-ratification cost.
- **If (β-1) ratified:** Single-session arc; per-run snapshot entry contract authored; documented scope-reduction at the replay-guarantee layer. H_T-IS-2 transit STILL-BOUNDED → RETIRED at the apply pass (X-AL-2 both conjuncts trivially satisfied by the narrowing).
- **If (β-2) ratified:** Single-session doc-amendment arc; line 170 collapses to canonical-reading observation; H_T-IS-2 transit STILL-BOUNDED → RETIRED-AS-AUTHORING-ONLY via sub-species 10 audit (categorical-mismatch: line 170 was never a substantive runtime gate; the registry exists as documentation of the tier taxonomy, not as a per-entry resolution surface).

---

## §10 Open contract questions for the apply-pass arc

Surfaced at architect-rec ratification close 2026-05-30 per `[[advisor-before-substantive-work-for-cross-axis-blockers]]` discipline; both must be resolved before spec authoring begins or they will produce mid-arc Class 1 forks at impl-time grounding (mirror PR #37 force-push-pre-merge precedent).

### Q-α — `ProceduralTierSnapshotRef` carrier shape

§5 names the resolver signature `resolve_procedural_tier_snapshot(harness_context) -> ProceduralTierSnapshotRef` but punts the return-type shape. Three sub-shapes:

- **(α-1) Content-hash form.** `Identifier = sha256(canonical_join(active_skills_versions || prompt_version || routing_manifest_sha))`. Self-describing; no separate lookup table needed; replay verifies the snapshot by re-hashing the procedural-tier state at replay time. Tight; immune to registry drift.
- **(α-2) Opaque registry key.** Monotonic counter / UUID / ULID with a separate lookup table `snapshot_id → ProceduralTierSnapshot(skills, prompt, manifest)`. Registry holds canonical state; replay queries by key. Allows non-content-addressed snapshots (e.g., named versions); requires separate registry persistence.
- **(α-3) Composite struct.** `frozen Pydantic v2 BaseModel { skills_set: frozenset[SkillVersionRef], prompt_version_ref: PromptRef, routing_manifest_sha: str }`. Self-describing AND queryable by component; richer than content-hash; widest entry-field footprint.

Each sub-shape interacts differently with `(α-2)` storage contract at Q-β below. Decision matrix:

| Shape | Storage need | Replay mechanism | Entry-field bytes |
|---|---|---|---|
| (α-1) hash | None (verifier re-computes) | Re-hash at replay; compare | 64 hex chars |
| (α-2) key | Separate registry table; persistence-required | Lookup by key | 32-64 bytes |
| (α-3) struct | None inline (self-describing) | Read fields directly | ~variable; per-entry inflated |

### Q-β — Snapshot registry home + storage contract

Three sub-shapes, partly dependent on Q-α:

- **(β-1) New `harness-is` file** `procedural_tier_snapshot_registry.py` sibling to `artifact_tier_registry.py`. In-memory mapping populated at bootstrap from active filesystem state; resolver reads at write-time.
- **(β-2) Storage backend Protocol pattern** per U-RT-76 `MemoryToolStorageBackendProtocol` precedent. `ProceduralTierSnapshotStorageBackend` Protocol with `read(snapshot_id) -> ProceduralTierSnapshot | None`, `write(snapshot_id, snapshot)` callbacks; concrete `LocalFilesystemProceduralTierSnapshotBackend` impl at runtime.
- **(β-3) Direct ledger-side computation** — no separate registry; resolver computes the snapshot at every call from current `HarnessContext` state. Forecloses Q-α-2 (no key→snapshot lookup table); compatible with Q-α-1 + Q-α-3.

Storage persistence is non-trivial: `procedural_tier` survival scope per spec §C-IS-02 §2 is "across runs and workflow versions" — implies the snapshot's **referent state** (skills, prompts, routing-manifest) persists across runs, but the **registry of snapshots-keyed-by-ref** is a derived structure whose persistence is not auto-implied. The apply-pass arc must decide whether the snapshot registry itself persists (replay-across-restart needs it; in-run-only doesn't) and whether shadow-git is the canonical persistence substrate (mirror state-ledger persistence pattern) or filesystem-only.

### Note on workspace-precedent calibration

§5 invokes `CostRecordAuditPayload` + `PauseResumeAuditPayload` as precedents for the sidecar shape. Calibration: those two are **per-event-type payloads** attached to specific composer functions (CP-axis cost-attribution composer; CP-axis pause/resume composer). `procedural_tier_snapshot_ref` is **per-entry universal metadata** attached to every state-ledger write across all composers. The precedent generalizes (the pattern is "typed-carrier-additive-not-substitutional") but is not a direct equivalence. The apply-pass spec amendment should acknowledge: γ generalizes the sidecar-payload precedent from per-event-type to per-entry-universal scope. This is the architectural shape the spec amendment introduces, and it should be named explicitly so future reviewers see the generalization rather than mistake it for direct equivalence.

---

*End of original architect recommendation. Operator ratifications captured at PR #89 review comment (Q1 = γ-family, Q1.1 = γ, Q2 = narrow, Q3 = bundled, Q4 = inline). Apply-pass arc owed at next session opener with Q-α + Q-β resolution as first deliverables before spec authoring begins.*

---

## §11 Apply-pass session 2026-05-30 — 3-of-3 findings catalogue + residence-decision AUQ (DEFERRED to next session)

*Appended at apply-pass session 2026-05-30 close. Pre-substantive advisor pass at apply-pass session opening + mid-arc + halt-decision = 3 advisor consultations at single arc (cardinality 55th application of `[[advisor-before-substantive-work-for-cross-axis-blockers]]` posture, single-arc-multi-call shape).*

### §11.1 Apply-pass docs-half LANDED

Spec v1.2 → v1.3 + plan v2.3 → v2.4 + arch rec §10 + this §11 LAND at apply-pass session close 2026-05-30 per Q3=bundled scope ratification (the docs half — spec amendment + plan revision + clearance marker). Impl half (resolver primitive + EntryPayload sidecar field extension + tests) DEFERRED per finding 3 of 3 (residence-decision AUQ owed at next session).

### §11.2 Finding 1 — Replay semantics ambiguity (RESOLVED at AUQ design)

See plan v2.4 §0.8 finding 1. Pre-substantive advisor pass + empirical grep across `replay` mentions discriminated engine-replay (CP/OD layer) from procedural-tier-state-reconstruction; procedural artifacts persist at filesystem+git per §C-IS-02 line 163. All 3 Q-α sub-shapes remained live; Q-α × Q-β coupling collapsed to 4 legal pairs; AUQ authored over 4 legal pairs at single D1. **Resolution:** AUQ design refinement; no spec/plan amendment owed.

### §11.3 Finding 2 — Prompts referent absent (RESOLVED by spec narrowing pre-commit)

See plan v2.4 §0.8 finding 2. Empirical grep at HEAD `8816ce9` surfaced ZERO runtime binding for `active_prompt_version` (no field on `HarnessContext`; no `PromptManifest` carrier at any harness-* package). Per X-AL-3 the spec MUST NOT commit a content-hash recipe to a phantom referent. **Resolution:** Spec v1.3 §5.2 recipe narrowed from 3 components to 2 components pre-commit per `[[impl-time-grounding-pass-pre-merge-revision]]`; prompts component deferred to v1.x runtime-binding-extension arc.

### §11.4 Finding 3 — Resolver residence cycle (HALT — operator-decision territory)

See plan v2.4 §0.8 finding 3. Empirical grep surfaced dep-graph cycle: `harness-runtime/src/harness_runtime/types.py:88-90` imports from harness-is at runtime; harness-is cannot import HarnessContext from harness-runtime per circular-dep constraint. The architect-rec-assumed `harness-is` residence is **structurally foreclosed** at HEAD. The Q3=bundled ratification originally promised "spec + plan + IS resolver impl"; the IS-resolver-impl half is operator-decision territory not covered by Q3.

#### §11.4.1 Residence-decision AUQ (owed at next session)

**Q-γ — Resolver implementation residence.** Three options enumerated; pick one to unblock the impl arc:

- **(γ-1) `harness-runtime/.../procedural_tier_snapshot.py` under U-IS-18.** Cross-package contract-impl pattern: IS-axis spec contract (C-IS-05 §5.2) authored at spec v1.3; impl resides at sibling package per dep-graph constraint. **Cost:** establishes NEW workspace convention (IS-contract impl outside harness-is package); zero workspace precedent at this shape. **Benefit:** preserves Q2=narrow at plan-unit-ownership layer; no new runtime plan unit owed; impl is straightforward (single module ~30 lines).
- **(γ-2) `harness-runtime/.../procedural_tier_snapshot.py` under NEW U-RT-NN.** Runtime plan v2.41 → v2.42 cascade authoring NEW U-RT-NN unit; spec v1.3 §5.2 contract is consumed by runtime plan rather than implemented by IS plan. **Cost:** runtime plan cascade owed at this arc (Q2=narrow scope-extension); plan-unit-ownership moves to runtime-axis. **Benefit:** preserves "contract resides where impl resides" workspace convention; mirror precedent U-CORE-02 (harness-core contract impl).
- **(γ-3) Protocol pattern at `harness-core/src/harness_core/procedural_tier_snapshot.py`.** harness-core declares a `ProceduralTierSnapshotSource` Protocol with structural fields (`skills: Mapping[..., ...]`, `routing_manifest: ...`); harness-is depends on harness-core (existing dep) + consumes the Protocol at U-IS-18 signature; HarnessContext structurally conforms (Python Protocols cross BaseModel + frozen dataclass per duck-typing). **Cost:** larger surface (Protocol declaration + concrete fields at harness-core; needs `SkillID` + `RoutingManifest` carrier reachability from harness-core); structural-typing semantics need pyright strict verification. **Benefit:** preserves both Q2=narrow (resolver lives in IS package per plan-unit-ownership) + intra-IS-axis dep-graph (harness-is → harness-core only); closest to U-CORE-02 precedent. **Caveat:** `SkillID` lives at harness-runtime + `RoutingManifest` at harness-cp; (γ-3) may require carrier-re-home arc OR a Protocol-of-Protocol pattern at harness-core before viable.

**Decisive structural argument owed at next session opener** — (γ-3)'s viability gate: empirical grep at HEAD against carrier residence + dep-graph constraint for `SkillID` + `RoutingManifest` cross-package consumption from harness-core. If carrier-re-home required, (γ-3) becomes a multi-arc proposition; (γ-1) becomes the structurally-smallest path. If carriers can be referenced from harness-core (e.g., via TYPE_CHECKING-only imports or via Protocol-of-Protocol pattern), (γ-3) preserves workspace conventions cleanest.

### §11.5 Sub-species catalogue candidate

`[[architect-rec-assumed-cross-package-binding-fails-impl-time-empirical-orientation]]` — distinct closure-event-class at workflow v1.13 §7.4.7.2; awaits second instance for sub-species addition. Pattern: an architect rec authored before HEAD empirical orientation makes a residence assumption (or a cross-package binding assumption); apply-time empirical orientation finds the assumption is structurally foreclosed at HEAD; arc splits between docs-half (lands) + impl-half (deferred to residence-decision AUQ). Mirror but distinct from U-RT-111 v2.35-v2.39 5-rescope arc (which operated at the plan-revision layer for not-yet-built substrate); this finding 3 operates at the architect-rec-arc layer for cross-package-binding gaps.

### §11.6 Transit posture at apply-pass session close

H_T-IS-2 substitution-retirement transit posture: **STILL-BOUNDED at apply-pass session close 2026-05-30** (UNCHANGED from PR #89 baseline). Docs-half landing alone does NOT advance transit per X-AL-2 second conjunct ("H_E substitution surface no longer invoked at substitution site"); impl-half lands transit STILL-BOUNDED → PARTIAL at follow-on arc.

### §11.7 Next session opener

**First action:** present Q-γ AUQ (3 residence options) with empirical (γ-3)-viability grep as decisive structural argument source. Then author follow-on impl arc per ratified residence: resolver primitive + EntryPayload sidecar field landing + tests + transit STILL-BOUNDED → PARTIAL filing.

*End of §11. Apply-pass session 2026-05-30 closed at docs-half-LANDED + impl-half-DEFERRED + Q-γ-residence-AUQ-owed-at-next-session.*
