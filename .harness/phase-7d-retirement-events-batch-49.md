# Phase 7d retirement events — batch-49

*Filed 2026-05-30 session-continuation arc closing H_T-IS-2 STILL-BOUNDED → PARTIAL via Phase 7 substantive amendment bundled-absorption (spec v1.3 docs-half at PR #89 commit `36ae336` + IS plan v2.5 + runtime plan v2.42 impl-half at this arc + production binding at `procedural_tier_snapshot.py` resolver + `EntryPayload` sidecar lift + `StateLedgerEntry` D-derivative field + `canonicalize` discipline + 22 NEW tests). Q-γ=(γ-2) operator-ratified residence-ownership transfer to runtime axis per `.harness/architect_recommendation_h_t_is_2_artifact_tier_registry_wiring.md` §11.4. ZERO cross-axis cascade at this arc per Q2=narrow; PARTIAL → RETIRED gated on ~13 producer-site lifts at follow-on per-axis cascade arcs per X-AL-2 second conjunct.*

---

## §0 Batch context

**Status type: 1 STILL-BOUNDED → PARTIAL transition (H_T-IS-2).** First substrate-side transit for H_T-IS-2 since Phase 7 launch. Per workflow v1.12 §7.4.7.3.C retirement-tier-transit audit-template, this batch refreshes `harness-is/CLAUDE.md` §4.1 H_T-IS-2 row + cumulative-counts line. Per X-AL-2 second conjunct ("H_E substitution surface no longer invoked at substitution site"), the transit is bounded at PARTIAL — the resolver primitive lands as canonical substrate but the H_E `Bash`-substituted action-id-encoding pattern at producer composer sites is not yet displaced. Producer-site lifts (~13 sites across CP / runtime / AS composers) deferred per Q2=narrow ratification at v2.4 (preserved at v2.5/v2.42).

**Distinct from sub-species 7d/7e/7a.** This is NOT a vacuous-close shape. Spec v1.3 §C-IS-05 §5.1 + §5.2 + §C-IS-02 line 170 amendments are substantive contract additions per ADR-F2 §Consequences (c) D-derivative extension authorization. Production binding lifts a working resolver + sidecar field carrier to displace the convention-substitution at substantive-runtime-gate enforcement points. The closure shape is the **substantive-substrate-lift** pattern (mirror precedent at H_T-CP-12 batch-40 substantive close 2026-05-28 + H_T-IS-5/6/7/8/9 batch-1 substrate-landing closes 2026-05-20).

**Bundled-absorption arc per workspace `CLAUDE.md` §11.4 mixed-posture default.** This batch is bundled with: (a) docs-half PR #89 (already pending operator review at branch tip `36ae336`); (b) impl-half PR (stacked off the same worktree branch) authoring runtime plan v2.42 NEW U-RT-112 + IS plan v2.5 U-IS-18 retirement + production binding + 22 NEW tests. Mirror precedent: CP spec v1.25 + harness-cp impl + tests landed bundled at PR #37 (2026-05-28); CP spec v1.26 + plan v2.29 + impl landed bundled at PR #38 (2026-05-29). The X-AL-3 silent-absorption rule is satisfied via documented back-flow at the architect recommendation (§11) + this retirement event filing + 2 clearance markers (runtime plan v2.42 + IS plan v2.5).

**Conclusion (preview):** **1 STILL-BOUNDED → PARTIAL transit** (H_T-IS-2). IS-axis advances 8/9 RETIRED + 1 STILL-BOUNDED → 8/9 RETIRED + 1 PARTIAL (pipeline-advanced 8/9 → 9/9 = 100% pipeline-advanced; FIRST IS-axis-clean state at pipeline-advanced view). Workspace-aggregate pipeline-advanced 48/54 → 49/54 = 90.7%. RETIRED count UNCHANGED at 45/54 = 83.3% (PARTIAL is not RETIRED per X-AL-2). NEW species candidate `[[is-spec-contract-runtime-axis-impl-cross-package-pattern]]` catalogued at workflow v1.13 §7.4.7.2 — third instance; sub-species addition candidate at next workflow-doc revision.

---

## §1 H_T-IS-2 STILL-BOUNDED → PARTIAL

### §1.1 Pre-transition state (batch-48 close, 2026-05-29)

H_T-IS-2 carried as STILL-BOUNDED across batches 1 → 48 per `harness-is/CLAUDE.md` §4.1:

> H_T-IS-2 (artifact-tier registry) STILL-BOUNDED — Typed library exists; no bootstrap composer invokes it; cross-tier traceability invariant unenforced at append-time per ledger v2 §3 (substantive runtime gate — sub-species 10 reclassification foreclosed per advisor pre-substantive audit at batch-39 arc).

Per `phase-7d-retirement-ledger-v2.md` §3 substantive runtime gate posture: cross-tier traceability MUST flow at `durable`-tier ledger entry write per `Spec_Information_Substrate_v1.md` §C-IS-02 line 170; the H_E `Bash` convention-substitution encoded the procedural-tier reference via `action_id` text-content discipline, NOT via a typed schema-enforced field. The reclassification to sub-species 10 `gate-text-stale-vs-production-landings` was foreclosed at batch-39 advisor pre-substantive audit because the substantive gate at append-time remained unenforced.

### §1.2 Transition trigger (this batch, 2026-05-30)

**Phase 7 substantive amendment bundled-absorption arc.** The closure is a substrate-landing event:

| Component | Landing site | Spec contract | Status |
|---|---|---|---|
| Sidecar field carrier | `harness-is/src/harness_is/state_ledger_write.py` `EntryPayload.procedural_tier_snapshot_ref: Identifier \| None = None` | IS spec v1.3 §C-IS-05 §5.1 (NEW D-derivative sidecar) | **LANDED** at U-IS-11 v2.4 amendment (sidecar) + this arc impl |
| Persisted entry shape extension | `harness-is/src/harness_is/state_ledger_entry_schema.py` `StateLedgerEntry.procedural_tier_snapshot_ref: Identifier \| None = None` | IS spec v1.3 §C-IS-05 §5.1 | **LANDED** at this arc |
| Canonicalize discipline | `harness-is/src/harness_is/entry_hash.py` `canonicalize` includes sidecar when non-None | IS spec v1.3 §C-IS-06 §6.1 NEW D-derivative contribution | **LANDED** at this arc |
| Resolver primitive | `harness-runtime/src/harness_runtime/lifecycle/procedural_tier_snapshot.py` `resolve_procedural_tier_snapshot(ctx)` + `make_procedural_tier_snapshot_resolver(ctx)` factory | IS spec v1.3 §C-IS-05 §5.2 (NEW resolver contract) | **LANDED** at U-RT-112 (runtime plan v2.42 NEW) per Q-γ=(γ-2) ratification |
| Spec amendment | `design-substrate/Spec_Information_Substrate_v1.md` v1.2 → v1.3 (NEW §5.1 + §5.2 + §C-IS-02 line 170 canonical-reading patch) | Phase 7 substantive amendment | **LANDED** at PR #89 commit `36ae336` (docs-half) |
| IS plan amendment | `design-substrate/Implementation_Plan_Information_Substrate_v2_3.md` → `v2_4.md` (U-IS-11 ext + NEW U-IS-18) → `v2_5.md` (U-IS-18 retirement per Q-γ ratification) | Phase 6 plan revision | **LANDED** at PR #89 docs-half (v2.4) + this arc impl-half (v2.5) |
| Runtime plan amendment | `design-substrate/Implementation_Plan_Harness_Runtime_v2_41.md` → `v2_42.md` (NEW U-RT-112) | Phase 6 plan revision | **LANDED** at this arc impl-half |
| Tests | 22 NEW tests (14 at `test_procedural_tier_snapshot.py` covering U-RT-112 ACs #1-#14; 8 at `test_state_ledger_write_sidecar.py` covering U-IS-11 v2.4 ACs #11-#14 + legacy-chain backward-compat) | Coverage of NEW contract surfaces | **LANDED** at this arc; 1458/1458 tests pass + 10 skipped workspace-wide |

### §1.3 X-AL-2 second-conjunct disposition

X-AL-2 second conjunct ("substituted H_E surface no longer invoked at substitution site") is **BOUNDED at PARTIAL**, NOT MET at RETIRED:

- **First conjunct MET:** U-IS-11 sidecar + U-RT-112 resolver landed at canonical-substrate residence per per Phase 7 ratified spec + plan + impl.
- **Second conjunct PARTIAL:** producer-site composer call-sites at ~13 sites across CP / runtime / AS axes (§16.5 CP composers + sub-agent dispatch + cost-attribution composers + per-step override evaluator + tool-dispatcher span emission) have NOT YET been lifted to consume `resolve_procedural_tier_snapshot(ctx)` or the `make_procedural_tier_snapshot_resolver(ctx)` factory at firing time. The H_E convention-substitution (operator authors `action_id` text encoding the procedural-tier reference) remains in scope at unlifted producer sites until full producer-site lift completion at follow-on per-axis cascade arcs.

Per Q2=narrow ratification at v2.4 (preserved at v2.5/v2.42), producer-site lifts deferred per `[[substrate-pre-landed-consumer-deferred-multi-arc-lift]]` precedent. Estimated cascade sizing: 1-2 sessions per axis (CP-axis ~7 sites at §16.5 composers; runtime-axis ~4 sites; AS-axis ~2 sites).

### §1.4 Refresh — `harness-is/CLAUDE.md` §4.1 row

| Component | Before | After (this batch) |
|---|---|---|
| H_T-IS-2 status | STILL-BOUNDED | **PARTIAL** (substrate landed; producer-site lifts deferred per Q2=narrow; full RETIRED gated on lift completion per X-AL-2) |
| IS-axis cumulative counts | 8/9 RETIRED + 1 STILL-BOUNDED (post-batch-39) | 8/9 RETIRED + 1 PARTIAL (post-batch-49); pipeline-advanced 9/9 = 100% (FIRST IS-axis-clean at pipeline-advanced view) |

### §1.5 Workspace ledger v2 §3 row refresh

| Field | Before | After |
|---|---|---|
| H_T-IS-2 transit | STILL-BOUNDED (batches 1-48) | **PARTIAL** (batch-49) |
| Retirement criterion fidelity | substantive-runtime-gate-at-append-time UNENFORCED | substantive-runtime-gate-at-append-time **CARRIER PRESENT** (sidecar field + resolver primitive landed); ENFORCEMENT AT PRODUCER-SITE-LIFT (gated on follow-on per-axis cascade) |

---

## §2 Cross-axis cascade discipline

**ZERO cross-axis cascade at this arc** per Q2=narrow ratification.

- **CP spec / AS spec / OD spec PRESERVED VERBATIM** (verified via grep at `design-substrate/` — no §5.1 / §5.2 / `procedural_tier_snapshot_ref` cite in any non-IS spec file at HEAD).
- **CXA v2.16 PRESERVED VERBATIM** (this arc authors IS-substrate consumer at runtime axis; no §16.5-composer-arc transit; CXA §0.4 PENDING rows 6 → 6 unchanged).
- **ADR / ADD / PRD PRESERVED VERBATIM.**
- **Target_Stack_Commitment_v1 §5.1 PRESERVED VERBATIM** (framework-pull discipline unchanged at runtime axis).

Producer-site cascade scope per spec §5.2 deferral footer + Q2=narrow ratification:

| Axis | Est. sites | Composer surfaces |
|---|---|---|
| CP | ~7 | §16.5 composers (U-CP-14 override; U-CP-27 workload-class-selection; U-CP-30 pause/resume; U-CP-37 HITL; U-CP-49 pause-captured engine-layer; U-CP-50 resume-attempted engine-layer; U-CP-34 sibling-ledger) |
| Runtime | ~4 | Sub-agent dispatch; cost-attribution composers; per-step override evaluator wiring; bootstrap-stage entries |
| AS | ~2 | Tool-dispatcher span emission; managed_agents (deferred per AS-8f INDEFINITE) |

Each producer-site lift is a small canonical-reading amendment at the consumer's plan body + 1-line composer signature kw-only addition + 1-line entry-construction site update consuming the resolver via `resolve_procedural_tier_snapshot(ctx)` or the kw-only-callable factory `make_procedural_tier_snapshot_resolver(ctx)` per CP spec v1.25 §16.5.7 + §16.5.8 `ledger_writer` precedent.

---

## §3 Sub-species catalogue + adjacent observations

### §3.1 NEW species candidate

`[[is-spec-contract-runtime-axis-impl-cross-package-pattern]]` — third instance, awaiting sub-species addition at workflow v1.13 §7.4.7.2 revision.

| Instance | Spec axis | Impl axis | Carrier landing |
|---|---|---|---|
| U-CORE-02 | AS spec v1.3 §15 (later corrected at phantom-cite resolution) | harness-core | `SandboxDecisionPolicy` empty-marker |
| U-RT-99 (skill activation hook) | AS spec v1.7 §14.4 footer | harness-runtime | `Skill` + `SkillManifest` + `SkillActivationHook` |
| **U-RT-112 (this arc)** | IS spec v1.3 §C-IS-05 §5.2 | **harness-runtime** | `resolve_procedural_tier_snapshot` + factory |

Common pattern: a spec axis declares a contract that requires consumer-package-internal substrates (HarnessContext + Skill + RoutingManifest at runtime axis), forcing impl residence at the consumer axis rather than the spec-author axis. Workflow-doc revision candidate at next revision pass.

### §3.2 Empirical findings during apply-pass orientation

Two checkpoint-vs-HEAD residence drifts surfaced at session-resumption empirical orientation 2026-05-30:

| Finding | Checkpoint claim | Empirical HEAD | Discrimination |
|---|---|---|---|
| SkillID residence | `harness-runtime/.../skills.py` | **`harness-core/identity.py:76`** | Empirical grep at advisor 56th application caught checkpoint stale-recall pre-substantive-authoring |
| RoutingManifest sha derivation surface | (implicit assumption: `.sha`/`.hash()` method exists) | NO such method at HEAD | Resolver canonicalizes via `model_dump_json(by_alias=False)` + sha256 per spec §5.2 implementer-discretion footer; NOT halt-shape gap |

Cardinality 1 of NEW sub-species candidate `[[checkpoint-recall-vs-empirical-HEAD]]` at workflow v1.13 §7.4.7.2; awaits second instance.

### §3.3 56th application of `[[advisor-before-substantive-work-for-cross-axis-blockers]]`

Pre-substantive advisor consultation 2026-05-30 caught: (1) SkillID residence stale claim; (2) RoutingManifest sha derivation surface absence; (3) reframed "30-line module" to empirical "~50 LOC + factory function per CP spec v1.25 §16.5.7 precedent"; (4) scope discipline at Q2=narrow holds (do NOT thread `Callable[[], Identifier]` into producer sites at this arc).

### §3.4 PR shape

Stacked-new-PR off `worktree-h-t-is-2-architect-rec` branch. PR #89 (docs-half) carries spec v1.3 + IS plan v2.4 + arch rec §11 (apply-pass session findings) + clearance marker for spec v1.3. New PR (impl-half, this arc) carries IS plan v2.5 + runtime plan v2.42 + production binding (resolver + sidecar field + canonicalize discipline) + 22 NEW tests + arch rec §11.8 closure entry + 2 NEW clearance markers + this retirement event filing + workspace `CLAUDE.md` row bumps. Rebases to main if PR #89 merges first.

---

## §4 Filing footer

| Field | Value |
|---|---|
| Batch | 49 |
| Filed at | 2026-05-30 |
| Filing authority | `.harness/architect_recommendation_h_t_is_2_artifact_tier_registry_wiring.md` §11.4 Q-γ operator-ratified (γ-2) 2026-05-30 + Phase 7 substantive amendment apply-pass arc bundled co-publication |
| Net delta | 1 STILL-BOUNDED → PARTIAL (H_T-IS-2); IS-axis pipeline-advanced 8/9 → 9/9 = 100%; workspace pipeline-advanced 48/54 → 49/54 = 90.7%; RETIRED count UNCHANGED at 45/54 = 83.3% |
| Production binding | Co-published: NEW `harness-runtime/.../lifecycle/procedural_tier_snapshot.py` + NEW `harness-runtime/tests/test_procedural_tier_snapshot.py` + EDIT `harness-is/src/harness_is/{state_ledger_write,state_ledger_entry_schema,entry_hash}.py` sidecar lifts + NEW `harness-is/tests/test_state_ledger_write_sidecar.py` + EDIT `harness-is/tests/test_state_ledger_entry_schema.py` schema completeness reflecting v1.3 D-derivative addition. 1458/1458 tests pass + 10 skipped workspace-wide. |
| Cross-axis cascade | NONE at this arc per Q2=narrow. Producer-site lifts at ~13 sites across CP / runtime / AS deferred per `[[substrate-pre-landed-consumer-deferred-multi-arc-lift]]` precedent. |
| Downstream artifacts owed | workspace `CLAUDE.md` row bumps (IS spec v1.2 → v1.3 + IS plan v2.4 → v2.5 + runtime plan v2.41 → v2.42); `harness-is/CLAUDE.md` §4.1 H_T-IS-2 row refresh per workflow v1.12 §7.4.7.3.C audit-template; arch rec §11.8 Q-γ closure entry; 2 NEW clearance markers (runtime plan v2.42 + IS plan v2.5) — all co-published this arc |
