# Spec: Control Plane — v1.23 (delta over v1.22)

---

## Change-note (v1.22 → v1.23)

**Scope of revision.** Fidelity-pure citation-correction patch closing the long-carried `resumption.kind` ↔ `engine.replay_disposition` attribute-carrier divergence between §5.2 + §8.1 + §8.3 (v1.2 lineage, preserved verbatim through v1.22) and §9.1 v1.3 4-attribute amendment (F2-12 sub-scope (i) closure). The §9.1 v1.3 amendment introduced `engine.replay_disposition` as the canonical 4th `engine.*` attribute supersedes the §5.2/§8.1/§8.3 `resumption.kind` carrier at the at-emission layer, but the original declaration sites in §5.2 + §8.1 + §8.3 were not amended at v1.3 to harmonize the carrier name. Plan U-CP-20 acceptance #2 + U-CP-21 4-attribute namespace conformed to §9.1; production at `harness-cp/src/harness_cp/per_class_attribute_composition.py:140-145` adopted `engine.replay_disposition` as the required attribute set member at `WorkflowEventClass.RESUMPTION`; grep confirms ZERO production sites set the literal string `resumption.kind`. v1.23 canonical-reading amendment harmonizes the §5.2 + §8.1 + §8.3 declaration sites with §9.1 v1.3 production-de-facto.

**Empirical orientation that surfaced the divergence.** This arc opened as the H_T-CP-9 PARTIAL → RETIRE-READY investigation per `harness-cp/CLAUDE.md` §4.1 ("CP-9 on driver emission of 5-class ResumptionKind beyond binary"). Empirical orientation at `workflow_driver.py:649-663` showed production explicitly skips `WorkflowEventClass.RESUMPTION` emission for `EngineClass.PURE_PATTERN_NO_ENGINE` with the comment citing §8.2 row 3 (JOIN/dedup discipline). §8.2 row 3 is the wrong cite — the right cite is §25.5 v1.4 scope carve-out ("workflow.resumption | CONDITIONAL | … At v1.4 scope: emit on re-entry if `manifest_entry.engine_class == 'save-point-checkpoint'`"). That part of the orientation closes as **Reading B canonical** + Class 3 in-code comment cite-fix (co-published this arc at `workflow_driver.py:662-669`).

Independent of the emission-scope question, the orientation surfaced the attribute-carrier divergence: §8.1 declares `resumption.kind` as the carrier on `workflow.resumption` spans; §9.1 v1.3 declares `engine.replay_disposition` as the 4th `engine.*` attribute. Grep across `harness-cp/src/` + `harness-runtime/src/` + `harness-od/src/` finds ZERO literal `"resumption.kind"` set_attribute call sites; `"engine.replay_disposition"` is set across plan-conformant carriers. The original v1.3 4-attribute amendment did not amend §5.2 + §8.1 + §8.3 to harmonize — leaving a 3-version-deep stale carry at the original sites.

**Operator routing 2026-05-27.** AskUserQuestion presented 3 arc shapes: (A) Reading-B + dual fidelity-pure cite-correction (recommended; ~2-3 commits), (B) Reading-A widen production to emit pure-pattern resumption (~5-8 commits; reverses §25.5 v1.4 carve-out), (C) File Class 1 fork doc + full ratification ceremony (~8-15 commits). Operator chose (A). v1.23 IS the spec-layer half of (A); the code-layer half co-published at this arc.

**Authoring lineage.** Sub-species at workflow v1.9 §7.4.7.2: **3.intra-spec-sibling-supersession** — distinct from the 7 prior species 3 sub-species (3.code-resolution / 3.fork-doc-closure / 3.workflow-grammar / 3.empirical-verification-of-external-authority / 3.same-session-immediate-sequel / 3.retirement-event-filing-arc / 3.binding-fix-not-schema-extension). Shared common-ancestor "resolved-but-carry-stale-inherited"; distinct closure-event-class is **a sibling sub-section amendment within the same spec file lineage supersedes an attribute/contract surface, but the original declaration site is not amended at the same arc, leaving stale carry-text in the original section across all subsequent delta-only versions**. The §9.1 v1.3 amendment was the supersession event (F2-12 sub-scope (i) closure); the §5.2 + §8.1 + §8.3 declaration sites carried stale text from v1.3 through v1.22 (20+ delta versions). Sub-species set at species 3 now EIGHT in 6 consecutive arcs.

**No fork doc filed.** Per workspace precedent for fidelity-pure citation-correction patches anchored at conclusive empirical state + operator AskUserQuestion routing that foreclosed fork-doc-ratification ceremony (mirrors v1.22 + v1.17/v1.18/v1.19/v1.20/v1.21 precedent).

**Co-publication this session.** Production cite-fix at `harness-cp/src/harness_cp/workflow_driver.py:662-669` (comment narrative refresh: §8.2 row 3 → §25.5 v1.4 scope carve-out + §8.1/§8.3 contract-space note) + carrier-comment harmonization at `harness-cp/src/harness_cp/per_class_attribute_composition.py:140-150` (comment narrative refresh: §5.2 verbatim claim retracted; §9.1 v1.3 supersession cited). ZERO behavior change at production. ZERO test addition or modification. 1799/1799 harness-cp + harness-runtime tests preserved at PASS (pre-arc baseline).

---

## §1 Canonical-reading amendment

### §1.1 Attribute-carrier harmonization at §5.2 + §8.1 + §8.3

The following carrier-name substitutions are the canonical reading at v1.23 onward. v1.2 file body PRESERVED VERBATIM per delta-only-spec-file convention; downstream readers apply the substitutions in-context.

| Site | v1.2 lineage text (preserved verbatim at file body) | v1.23 canonical reading |
|---|---|---|
| §5.2 row "workflow.resumption" (v1.2 line 519) | "workflow.id, engine.class, **resumption.kind** per C-CP-08 §8.1 enum, idempotency_key (root)" | "workflow.id, engine.class, **engine.replay_disposition** per C-CP-09 §9.1 v1.3 amendment (supersedes §8.1 `resumption.kind` carrier), idempotency_key (root)" |
| §8.1 section title (v1.2 line 722) | "§8.1 Per-engine-class resumption-kind enum" | "§8.1 Per-engine-class resumption-kind enum (carrier at `engine.replay_disposition` per §9.1 v1.3)" |
| §8.1 intro sentence (v1.2 line 724) | "The **`resumption.kind`** attribute carried on the `workflow.resumption` span (declared at C-CP-05 §5.2) takes the following values" | "The **`engine.replay_disposition`** attribute (declared at C-CP-09 §9.1 v1.3 — 5-value enum supersedes the v1 `resumption.kind` carrier name) carries on the `workflow.resumption` span the following values" |
| §8.1 enum table column header (v1.2 line 726) | "\| `resumption.kind` \| Engine class \| Observable behavior … \|" | "\| `engine.replay_disposition` \| Engine class \| Observable behavior … \|" |
| §8.1 always-emitted statement (v1.2 line 734) | "The `resumption.kind` attribute is always-emitted on `workflow.resumption` spans (per C-CP-05 §5.4 always-sampled discipline)." | "The `engine.replay_disposition` attribute is always-emitted on `workflow.resumption` spans (per C-CP-05 §5.4 always-sampled discipline)." |
| §8.3 pseudocode line (v1.2 line 755) | "with attrs: workflow.id, engine.class, **resumption.kind** per §8.1" | "with attrs: workflow.id, engine.class, **engine.replay_disposition** per §9.1 v1.3 (supersedes v1 §8.1 `resumption.kind` carrier name)" |

**Conceptual enum identity preserved.** `ResumptionKind` (5-value class at `harness_cp.resumption_kind:ResumptionKind`) and `ReplayDisposition` (5-value class at `harness_cp.engine_namespace:ReplayDisposition`) are TWO ENUMS with distinct member string values mapped 1:1 to `EngineClass`. The carrier-name harmonization at v1.23 does NOT collapse the two enums; it canonicalizes which attribute name is set on the `workflow.resumption` span. The §8.1 5-class taxonomy (semantic — *what is happening at resumption*) and the §9.1 v1.3 `engine.replay_disposition` 5-value enum (observability — *what disposition the replay engine took*) are conceptually distinct dimensions that happen to be 1:1 mapped per ADR-D1 v1.2 §1.1.1. Production carries BOTH classes (`ResumptionKind` exposed at `t_perm_3_composition.py:44+98`; `ReplayDisposition` exposed at `engine_namespace.py:33-46`); only `ReplayDisposition` is set as the span attribute per §9.1 v1.3 amendment.

**Production already conformant.** `harness-cp/src/harness_cp/per_class_attribute_composition.py:140-150` (post co-publication this arc) declares the required-attribute set for `WorkflowEventClass.RESUMPTION` as `{workflow.id, engine.class, engine.replay_disposition, idempotency_key}` per plan U-CP-20 acc #2 + U-CP-21 4-attribute namespace + §9.1 v1.3. The v1.23 canonical-reading amendment is doc-hygiene catch-up to production de-facto; no behavior change, no test change.

### §1.2 Emission-scope cite-correction at `workflow_driver.py:662`

Production at `harness-cp/src/harness_cp/workflow_driver.py:649-663` does NOT emit `WorkflowEventClass.RESUMPTION` for `EngineClass.PURE_PATTERN_NO_ENGINE` per CP spec §25.5 v1.4 scope carve-out ("workflow.resumption | CONDITIONAL | … At v1.4 scope: emit on re-entry if `manifest_entry.engine_class == 'save-point-checkpoint'`"). The pre-v1.23 skip-comment at line 662 read "state-ledger native dedup per §8.2 row 3 handles per-step dedup" — §8.2 row 3 is JOIN/dedup discipline, NOT emission-scope discipline. The right cite is §25.5.

Post-co-publication at this arc, the comment reads: "Under pure-pattern-no-engine: no resumption-specific emission per CP spec §25.5 v1.4 scope carve-out (`workflow.resumption` CONDITIONAL row: 'At v1.4 scope: emit on re-entry if manifest_entry.engine_class == save-point-checkpoint'). §8.1 declares the 5-class ResumptionKind enum + universal observable behavior at §8.3 — those are the full contract space; §25.5 carves out the v1.4 implementation scope. §8.2 row 3 governs state-ledger native dedup for the pure-pattern engine class (orthogonal to emission scope; row 3 is JOIN discipline, not emission discipline)."

Class 3 cite-correction; no contract change; no behavior change.

---

## §2 Cross-artifact cite-cascade disposition (v1.23 NEW)

| Artifact | Site | Disposition at v1.23 |
|---|---|---|
| `harness-cp/src/harness_cp/workflow_driver.py:662-669` | Skip-comment narrative refresh — §8.2 row 3 → §25.5 v1.4 + §8.1/§8.3 contract-space note | **CO-PUBLISHED this arc** |
| `harness-cp/src/harness_cp/per_class_attribute_composition.py:140-150` | Required-attribute set comment harmonization — "§5.2 verbatim" claim retracted; §9.1 v1.3 supersession cited | **CO-PUBLISHED this arc** |
| `harness-cp/src/harness_cp/resumption_kind.py:13` docstring "Authority: ... Spec_Control_Plane_v1_3.md §8 C-CP-08 §8.1" | Spec authority cite — `ResumptionKind` 5-class semantic taxonomy at §8.1 unchanged | **NO change owed** — `ResumptionKind` enum semantics preserved (the carrier-name harmonization at §8.1 substitutes `resumption.kind` → `engine.replay_disposition` as the **attribute carrier**, not the enum class identity) |
| `harness-cp/src/harness_cp/engine_namespace.py:1-20` docstring | `ReplayDisposition` 5-value enum + §9.1 v1.3 4-attribute schema | **NO change owed** — already cites §9.1 v1.3 verbatim |
| `harness-cp/src/harness_cp/per_resumption_observable_behavior.py:1-30` docstring | "Authority: CP spec v1.3 §9.1 4-attribute canonical" | **NO change owed** — already cites §9.1 v1.3 |
| Plan U-CP-20 + U-CP-21 (CP plan v2.26) | Required-attribute set at U-CP-20 acc #2 + 4-attribute namespace at U-CP-21 | **NO change owed** — plan-side cites §9.1 v1.3 directly; canonical at U-CP-20/U-CP-21 |
| Workspace `CLAUDE.md` §2.3 CP spec row | v1.22 row narrative | **CO-PUBLISHED this arc** — bumped to v1.23 |
| `harness-cp/CLAUDE.md` §1.2 spec version cite | v1.3 (canonical base contract authority — delta versions tracked at workspace `CLAUDE.md` §2.3 only) | **NO change owed** — `harness-cp/CLAUDE.md` cites the canonical-base contract authority (v1.3) not current-delta. Verified via grep this session (zero `v1.22` / `v1.23` cites at harness-cp/CLAUDE.md). |
| Peer artifacts at design-substrate/ | ZERO `resumption.kind` literal cites at downstream readers (verified via grep this session) | **NO change owed** — verified |
| CXA v2.15 | No cross-axis edge change; `resumption.kind` attribute does not appear in any cross-axis seam declaration | **NO change owed** — verified via grep |
| Retirement events ledger | `harness-cp/CLAUDE.md` §4.1 H_T-CP-9 PARTIAL status — "ResumptionKind 5-class — driver emits binary only" | **NO change owed at v1.23** — H_T-CP-9 PARTIAL status preserved; the v1.4 emission-scope carve-out is canonical at v1.4 scope; H_T-CP-9 PARTIAL → RETIRE-READY gate would be triggered by a future spec revision widening §25.5 to include additional engine classes (separate arc, not this one) |

---

## §3 Sections preserved verbatim at v1.23

Per delta-only-spec-file convention + FM-2 no-extension discipline + fidelity-pure citation-correction scope, the v1.23 amendment touches ONLY the NEW §1 canonical-reading amendment + §2 cross-artifact cite-cascade disposition + §3 sections-preserved-verbatim. The following sections are PRESERVED VERBATIM:

- **§5.2 row "workflow.resumption" file body** (v1.2 line 519; canonical reading at v1.23 §1.1 substitutes `resumption.kind` → `engine.replay_disposition`)
- **§8 C-CP-08 + §8.1 + §8.2 + §8.3 + §8.4 file body** (v1.2 lines 708-770; canonical reading at v1.23 §1.1 substitutes carrier name at the 5 enumerated sites)
- **§9 C-CP-09 + §9.1 file body** (v1.3 lineage; canonical at v1.23 — §9.1 v1.3 amendment IS the authority for `engine.replay_disposition` 5-value enum)
- **§25.5 row "workflow.resumption" v1.4 amendment** (v1.4 line 375; v1.4 scope carve-out canonical at v1.23 per Reading B)
- **All v1.2–v1.22 lineage substantive amendments**

---

## Adjacent observations (surfaced as findings; NOT patched per FM-2)

(a) **v1.22 (b)+(c) `parent_sandbox_tier` + `parent_entry_hash` axes — preserved verbatim at v1.23.** Future operator-discretion arcs per CP-19-precedent shape. GENUINE; NO change at v1.23.

(b) **v1.22 (d) Layer-3 multi-deployment e2e fixture — CLOSED at batch-22.** Confirmed still CLOSED at v1.23 (no new event). v1.22 (d) framing remains canonical disposition; v1.23 is single-focus on attribute-carrier harmonization.

(c) **NEW at v1.23 — H_T-CP-9 PARTIAL status disposition refined.** Per `harness-cp/CLAUDE.md` §4.1 the H_T-CP-9 PARTIAL framing reads "ResumptionKind 5-class — driver emits binary only". Reading B canonical at v1.23 + §25.5 v1.4 scope carve-out makes the "driver emits binary only" framing partial-and-correct: the driver emits RESUMPTION for `save-point-checkpoint` only at v1.4 scope per §25.5; the 5-class enum IS reflected at the production carrier `RESUMPTION_KIND_BINDINGS` (5 entries at `resumption_kind.py:60`) + the `ReplayDisposition` 5-value enum + `REPLAY_DISPOSITION_MAPPING` (5 entries at `engine_namespace.py:98`); only the at-span-emission scope is v1.4-carved. H_T-CP-9 PARTIAL → RETIRE-READY gate at the *spec layer* would be a future arc widening §25.5 to add additional engine classes; H_T-CP-9 PARTIAL → RETIRE-READY gate at the *production layer* would be `workflow_driver.py:649-663` adding emission for additional `EngineClass.*` cases. Both are future arcs; v1.23 is canonical-reading harmonization scope-only.

(d) **NEW at v1.23 — sub-species 3.intra-spec-sibling-supersession catalogued.** v1.23 §1.1 closure is the EIGHTH sub-species refinement of species 3 (resolved-but-carry-stale-inherited) at workflow v1.9 §7.4.7.2. Distinct closure-event-class: **a sibling sub-section amendment within the same spec file lineage supersedes an attribute/contract surface, but the original declaration site is not amended at the same arc, leaving stale carry-text in the original section across all subsequent delta-only versions**. The §9.1 v1.3 amendment (F2-12 sub-scope (i) closure) was the supersession event 2026-05-14; the §5.2 + §8.1 + §8.3 declaration sites carried stale text from v1.3 through v1.22 (20+ delta versions, ~13 days). Sub-species set at species 3 now EIGHT in 6 consecutive arcs (v1.22 OD / v1.23 OD / v1.24 OD / v1.21 CP / v1.22 CP / v1.23 CP). **Workflow v1.9 §7.4.7.2 "Sub-species" column extension increasingly warranted** — empirical cardinality of 8 sub-species in 6 consecutive arcs is strong evidence the column extension is overdue. NOT patched per FM-2.

(e) **NEW at v1.23 — `resumption.kind` literal string disposition.** Post-v1.23 canonical reading, the literal string `"resumption.kind"` no longer corresponds to any harness production span attribute name. Documentation references (e.g., the §8.1 section title preserved verbatim per delta-only-spec-file convention) still use the v1.2 lineage spelling; readers apply §1.1 substitution. The `ResumptionKind` Python class identifier at `harness_cp.resumption_kind` remains canonical for the 5-class semantic taxonomy; the carrier-name harmonization does NOT rename the Python class. Catalogued for observation only.

(f) **NEW at v1.23 — pattern catalogued: empirical-orientation-discovers-pre-existing-divergence.** The arc opened as H_T-CP-9 PARTIAL → RETIRE-READY investigation; empirical orientation at the production code site (`workflow_driver.py:649-663` + `per_class_attribute_composition.py:140-145`) surfaced TWO divergences (emission scope + attribute carrier) that pre-dated the arc by 13+ days and 20+ delta versions. Pattern: **substantive-arc empirical orientation can surface stale divergences that the post-authoring-stale-carry strengthened discipline at workflow v1.9 §7.4.7.3 should have caught at earlier amendment arcs but did not** (the §9.1 v1.3 amendment did not include the sibling §5.2 + §8.1 + §8.3 harmonization at the same commit). Pre-substantive empirical-verification audit at every amendment arc per workflow v1.9 §7.4.7 — when applied to §9.1 v1.3 — would have caught the §5.2/§8.1/§8.3 stale-carry at the originating arc. Strengthening candidate for §7.4.7.3 audit-template: **at any §N.M amendment that introduces a new attribute / carrier / enum, audit ALL declaration sites in sibling sub-sections for stale-carry-text against the amendment**. Catalogued for future workflow-doc revision.

---

## Filing footer

| Field | Value |
|---|---|
| Version | v1.23 (Fidelity-pure citation-correction patch closing the long-carried `resumption.kind` ↔ `engine.replay_disposition` attribute-carrier divergence between §5.2 + §8.1 + §8.3 v1.2 lineage and §9.1 v1.3 4-attribute amendment — **CLOSED-as-canonical-reading-harmonization-with-production-de-facto** 2026-05-27; NEW §1 + §2 + §3; sub-species 3.intra-spec-sibling-supersession catalogued at §"Adjacent observations" (d); v1.22 + earlier files PRESERVED VERBATIM) |
| Trigger | Operator-routed H_T-CP-9 ResumptionKind investigation 2026-05-27; empirical orientation surfaced emission-scope cite-correction (Reading B canonical) + attribute-carrier harmonization (§9.1 v1.3 supersedes §5.2/§8.1/§8.3); operator AskUserQuestion ratified Reading-B + dual fidelity-pure cite-correction arc shape over Reading-A widen-production OR Class 1 fork doc + full ratification |
| Supersedes | §5.2 + §8.1 + §8.3 v1.2-lineage `resumption.kind` carrier-name declarations (6 enumerated sites at §1.1); pre-v1.23 `workflow_driver.py:662-663` skip-comment narrative citing §8.2 row 3 |
| Scope of revision | NARROW: NEW §1 + §2 + §3. ZERO contract / signature / AC change at any C-CP-NN. ZERO Workflow §4.1.2 Class-2 amendment. Co-publication: workflow_driver.py:662-669 comment + per_class_attribute_composition.py:140-150 comment + workspace CLAUDE.md row + harness-cp/CLAUDE.md row. ZERO production behavior change. |
| Cross-axis cascade | ZERO. Verified via grep at HEAD. CXA v2.15 unchanged; no inbound/outbound edge changes; no per-axis attribution refresh owed. Peer downstream readers (CXA / runtime spec / OD spec / AS spec) do NOT cite `resumption.kind` at any canonical-reading site. |
| Authority anchor | §9.1 v1.3 4-attribute amendment (F2-12 sub-scope (i) closure) declaring `engine.replay_disposition` as the 4th canonical `engine.*` attribute supersedes the v1 §5.2/§8.1/§8.3 `resumption.kind` carrier — verified via empirical grep at `harness-cp/src/` + `harness-runtime/src/` + `harness-od/src/` (ZERO `"resumption.kind"` literal set sites; production carries `"engine.replay_disposition"` exclusively per `engine_namespace.py:85`) |
| Predecessor | v1.22 (tenant_id binding lift) |
| Successor | (none — current canonical) |
| Date | 2026-05-27 |
