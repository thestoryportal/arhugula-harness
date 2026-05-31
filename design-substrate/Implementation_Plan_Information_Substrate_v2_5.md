# Implementation Plan — Information Substrate (IS axis) — v2.5

*Delta over v2.4. v2.5 is the IS-axis-side closure of the Phase 7 H_T-IS-2 substitution-retirement apply-pass impl-half per `.harness/architect_recommendation_h_t_is_2_artifact_tier_registry_wiring.md` §11.4 Q-γ operator-ratified 2026-05-30 as **(γ-2) NEW U-RT-NN at runtime plan v2.42 cascade**. Surgical single-unit retirement at U-IS-18 (RELOCATED-TO-U-RT-112-per-Q-γ-(γ-2)-ratification); residence-ownership transfers to runtime axis at runtime plan v2.42 sibling delta co-published this arc. U-IS-11 sidecar field amendment PRESERVED VERBATIM at v2.5 (carrier remains IS-axis owned). ZERO contract change; ZERO spec amendment; ZERO cross-axis cascade beyond the runtime plan v2.42 co-publication. v2.4 + earlier PRESERVED VERBATIM per delta-only-plan-chain convention.*

**Status:** Proposed

---

## §0 Change-note (v2.4 → v2.5)

### §0.1 Predecessor

`Implementation_Plan_Information_Substrate_v2_4.md` (v2.4 — Phase 7 H_T-IS-2 apply-pass docs-half landed at PR #89 commit `36ae336` 2026-05-30; preserved at branch `worktree-h-t-is-2-architect-rec` pending operator review-and-merge).

### §0.2 Revision scope (v2.4 → v2.5)

v2.5 closes the v2.4 §0.8 **finding 3 of 3 — resolver residence cycle (HALT)** at the operator-decision boundary. v2.4 authored U-IS-18 with "concrete module residence DEFERRED" framing pending Q-γ AUQ ratification. Q-γ ratified 2026-05-30 at session-opener following PR #89 docs-half landing: operator selected **(γ-2) NEW U-RT-NN at runtime plan v2.42 cascade**.

Under (γ-2) per arch rec §11.4.1 ("spec v1.3 §5.2 contract is consumed by runtime plan rather than implemented by IS plan"), U-IS-18 has no IS-axis decomposition role — the spec contract is implemented at runtime axis per the residence-ownership transfer. v2.5 surgically retires U-IS-18 and records the supersession at the canonical-reading layer; runtime plan v2.42 authors NEW U-RT-112 with equivalent body at runtime axis.

| In scope at v2.5 | Out of scope |
|---|---|
| U-IS-18 retirement (RELOCATED-TO-U-RT-112 per Q-γ ratification) | All other v2.4 unit bodies — preserved verbatim per §0.4 |
| §0.8 finding 3 closure note at canonical-reading layer | Spec v1.3 amendment (the spec is the canonical contract; residence is impl-plan territory) |
| DAG delta: -1 node (U-IS-18 retired); -1 within-axis edge (U-IS-11 → U-IS-18 also retired) | Cross-axis producer-site lifts (~13 sites; deferred per Q2=narrow at v2.4) |
| Coverage matrix delta: C-IS-05 §5.2 row supersession ("Covered at U-RT-112 per runtime plan v2.42") | — |

### §0.3 Operator Q-γ ratification 2026-05-30

| ID | Question | Operator decision | Where applied |
|---|---|---|---|
| **Q-γ** | Resolver implementation residence | **(γ-2) NEW U-RT-NN at runtime plan v2.42 cascade** | This v2.5 retirement of U-IS-18 + co-published runtime plan v2.42 NEW U-RT-112 |

**Decisive structural argument at Q-γ AUQ ratification.** Empirical reconciliation at apply-pass orientation 2026-05-30 surfaced (1) `SkillID` lives at `harness-core/identity.py:76` (NOT at harness-runtime as checkpoint claimed); (2) `RoutingManifest` exposes NO `.sha`/`.hash()` method at HEAD (sha derivation is implementer-discretion at resolver site per spec v1.3 §5.2 deferral footer). Empirical findings did not change Q-γ option-set; both findings made (γ-3) Protocol-at-harness-core more viable but still multi-arc-y (Skill + RoutingManifest carrier types still reside at harness-runtime + harness-cp; Protocol-of-Protocol or carrier re-home still owed at γ-3 path). Operator selected (γ-2) per (1) "contract resides where impl resides" workspace convention preservation; (2) U-CORE-02 mirror precedent (harness-core-impl of AS-axis contract); (3) smallest cascade cost (NEW U-RT-112 + runtime plan v2.42 delta + harness-runtime impl module; NO Protocol declaration + NO carrier re-home).

### §0.4 Sections preserved verbatim from v2.4

| Section | Status at v2.5 |
|---|---|
| §0 (v2.4 change-note) | Superseded by this §0 (the v2.4 change-note records the docs-half landing; the v2.5 change-note records the impl-half closure under Q-γ=(γ-2)) |
| §1 Spec inventory | PRESERVED VERBATIM from v2.4 §1 (citation refresh IS spec v1.3 — UNCHANGED since v2.4 publication; v1.3 still canonical at HEAD) |
| §2 — U-IS-01..U-IS-10, U-IS-12..U-IS-17 (16 units) | **PRESERVED VERBATIM from v2.4 §2.1** |
| §2 — U-IS-11 (revised at v2.4 for sidecar field) | **PRESERVED VERBATIM from v2.4 §2.2** — sidecar field amendment carries forward; carrier remains IS-axis owned at `harness-is/.../state_ledger_write.py:EntryPayload` |
| §2 — U-IS-18 (NEW at v2.4) | **RETIRED at v2.5** — RELOCATED-TO-U-RT-112-per-Q-γ-(γ-2)-ratification; canonical-reading note at §2 below |
| §3 Dependency graph | Revised at the U-IS-18-related nodes/edges only (§3 below); all other within-axis edges + the acyclicity proof preserved verbatim from v2.4 §3 |
| §4 Coverage matrix | Revised at C-IS-05 §5.2 row only (§4 below); all other rows preserved verbatim from v2.4 §4 |
| §5 Auxiliary-type carrier audit | PRESERVED VERBATIM from v2.4 §5 |

### §0.5 Authority chain — Q-γ closure path

The v2.4 § 0.8 finding 3 was filed as "HALT — operator-decision territory not covered by Q3 ratification." The Q-γ AUQ ratification 2026-05-30 IS the operator decision; v2.5 absorbs the decision at the IS-axis canonical-reading layer per delta-only-plan-chain convention. ZERO X-AL-3 risk at this arc (the spec v1.3 contract is unchanged; residence transfer at impl-plan layer is implementer-discretion territory authorized at spec §5.2 deferral footer + arch rec §11.4.1 (γ-2) operator ratification).

### §0.6 Per-axis cascade discipline + transit posture

**ZERO cross-axis cascade at v2.5** per Q2=narrow ratification carried from v2.4. ~13 producer-site lifts across `harness-as` / `harness-cp` / `harness-runtime` deferred to follow-on per-axis arcs per workspace `[[substrate-pre-landed-consumer-deferred-multi-arc-lift]]` precedent.

**H_T-IS-2 substitution-retirement transit posture:**

| State | Transit | Trigger |
|---|---|---|
| STILL-BOUNDED at v2.4 docs-half landing | (no transit) | Docs-half does NOT advance transit per X-AL-2 second conjunct |
| **STILL-BOUNDED → PARTIAL at v2.5 + runtime plan v2.42 + impl + tests merge** | **APPLIED** | Substrate landed at IS-axis sidecar carrier + runtime-axis resolver primitive |
| PARTIAL → RETIRED at follow-on per-axis cascade arcs | (deferred) | Full producer-site lift across ~13 sites required per X-AL-2 second conjunct ("H_E surface no longer invoked at substitution site") |

### §0.7 Status posture

`Status: Proposed (v2.5 in-flight Phase 7 substantive amendment per `.harness/architect_recommendation_h_t_is_2_artifact_tier_registry_wiring.md` apply-pass impl-half arc 2026-05-30 sibling co-publication with runtime plan v2.42)`. Clearance marker filed at `.harness/clearance/Implementation_Plan_Information_Substrate-v2_5-cleared-2026-05-30.md` per workspace `CLAUDE.md` §4.5.

### §0.8 Apply-pass impl-half findings catalogue

v2.5 + v2.42 close v2.4 §0.8 finding 3 of 3 at the operator-decision boundary. v2.4 findings 1 (replay semantics ambiguity) + 2 (prompts referent absent) preserved as historical record at v2.4. NEW at v2.5/v2.42 co-publication arc:

**Finding 4 — Checkpoint-vs-HEAD residence drift (RESOLVED at apply-pass orientation).** Session 4 checkpoint claimed `SkillID` at `harness-runtime/.../skills.py`; empirical grep at HEAD `8816ce9` confirmed `SkillID = NewType("SkillID", str)` at `harness-core/identity.py:76`. Cardinality 1 of `[[checkpoint-recall-vs-empirical-HEAD]]` sub-species candidate; awaits second instance for workflow v1.13 §7.4.7.2 sub-species addition. Empirical-grep-before-substantive-authoring is the closing discipline.

**Finding 5 — RoutingManifest sha derivation surface absence (RESOLVED at impl-discretion).** `RoutingManifest` exposes NO `.sha`/`.hash()` method at HEAD. Resolver computes via `sha256(model_dump_json(by_alias=False).encode("utf-8")).hexdigest()` at U-RT-112 per spec §5.2 implementer-discretion footer. NOT halt-shape gap; NO back-flow owed per `[[advisor-before-substantive-work-for-cross-axis-blockers]]` 56th-application discrimination.

---

## §1 Spec inventory

PRESERVED VERBATIM from v2.4 §1. IS spec v1.3 canonical at HEAD; no spec amendment owed at v2.5/v2.42 impl-half arc.

---

## §2 Atomic-unit decomposition

### §2.1 Preserved-verbatim units (16)

U-IS-01 through U-IS-10, U-IS-12 through U-IS-17 — PRESERVED VERBATIM from v2.4 §2.1. See `Implementation_Plan_Information_Substrate_v2_4.md` §2.1 for unit bodies (delta-only-plan-chain convention).

### §2.2 Preserved-verbatim revised unit (1)

U-IS-11 — PRESERVED VERBATIM from v2.4 §2.2. Sidecar field amendment (`procedural_tier_snapshot_ref: Identifier | None = None` at `EntryPayload`) carries forward unchanged at v2.5; carrier remains IS-axis owned at `harness-is/src/harness_is/state_ledger_write.py`.

### §2.3 Retired unit (1)

#### U-IS-18 — RETIRED at v2.5 *(RELOCATED-TO-U-RT-112-per-Q-γ-(γ-2)-ratification)*

**Status at v2.4:** NEW unit authored with "concrete module residence DEFERRED" framing pending Q-γ AUQ ratification.

**Status at v2.5:** **RETIRED.** Operator-ratified Q-γ=(γ-2) at apply-pass session-opener 2026-05-30 transfers residence-ownership to runtime axis. Equivalent unit body at runtime plan v2.42 as **U-RT-112 — `resolve_procedural_tier_snapshot` resolver primitive** at `harness-runtime/src/harness_runtime/lifecycle/procedural_tier_snapshot.py`.

**Supersession authority:** `.harness/architect_recommendation_h_t_is_2_artifact_tier_registry_wiring.md` §11.4.1 Q-γ AUQ + §11.8 closure entry (this arc co-publication); `.harness/architect_recommendation_h_t_is_2_artifact_tier_registry_wiring.md` §11.4 Q-γ=(γ-2) operator ratification 2026-05-30.

**Coverage continuity:** IS spec v1.3 §C-IS-05 §5.2 resolver contract is covered at runtime plan v2.42 U-RT-112 (see runtime plan v2.42 §1 + §3 coverage matrix). ZERO contract-coverage gap at workspace.

**No re-authoring at IS plan:** U-IS-18 supersession is a residence-ownership transfer at the impl-plan layer, NOT a contract-decomposition revision. The spec v1.3 §5.2 contract surface is unchanged; only the plan-unit ownership migrates.

---

## §3 Dependency graph

### §3.1 Dependency-graph delta (v2.5)

| Operation | Detail |
|---|---|
| RETIRE node | U-IS-18 |
| RETIRE within-axis edge | U-IS-11 → U-IS-18 (was authored at v2.4 §3 NEW edge; retired at v2.5) |
| NEW cross-package edge (declared at runtime plan v2.42) | U-RT-112 → U-IS-07 (`Identifier` alias consumption from runtime axis) |
| NEW cross-package edge (declared at runtime plan v2.42) | U-RT-112 → U-IS-11 (sidecar field carrier consumption from runtime axis at downstream caller-site cascade arcs; not at U-RT-112 unit body itself) |

### §3.2 Acyclicity preservation

Cross-package edges (declared at runtime plan v2.42 §2.1) run **runtime → IS** direction matching existing `harness-runtime/pyproject.toml` dep declaration. ZERO new cycle at IS-axis (U-IS-18 retired; no replacement node added at IS-axis; the cross-package edges added at runtime plan v2.42 do not contest IS-axis internal DAG).

IS-axis internal DAG (16 preserved-verbatim units + revised U-IS-11) PRESERVED VERBATIM from v2.4 §3 minus the U-IS-18 retirement + the U-IS-11 → U-IS-18 edge retirement. Acyclicity preserved at IS-axis intra-axis layer.

---

## §4 Coverage matrix

### §4.1 Coverage-matrix delta (v2.5)

| Spec contract | Atomic unit at v2.4 | Atomic unit at v2.5 |
|---|---|---|
| IS spec v1.3 C-IS-05 §5.1 (`procedural_tier_snapshot_ref` sidecar field) | U-IS-11 (revised) | U-IS-11 (preserved verbatim) |
| IS spec v1.3 C-IS-05 §5.2 (`resolve_procedural_tier_snapshot` resolver contract) | U-IS-18 (NEW; residence deferred) | **U-RT-112 at runtime plan v2.42** (per Q-γ=(γ-2) ratification) |
| IS spec v1.3 C-IS-02 line 170 canonical-reading patch (MAY/MUST composition reconciliation) | (preserved verbatim from v2.4) | (preserved verbatim) |

ZERO contract-coverage gap at workspace post-v2.5/v2.42 co-publication.

---

## §5 Auxiliary-type carrier audit

PRESERVED VERBATIM from v2.4 §5. No new auxiliary type introduced at v2.5 (U-IS-18 retirement is structural-residence transfer; no new carrier surfaces); the auxiliary-type carrier audit at v2.4 §5 remains canonical.

---

## §6 Filing footer

| Field | Value |
|---|---|
| Plan version | v2.5 (delta over v2.4) |
| Authored at | 2026-05-30 |
| Authoring authority | `.harness/architect_recommendation_h_t_is_2_artifact_tier_registry_wiring.md` §11.4 Q-γ operator-ratified (γ-2) 2026-05-30 (next-session-opener AUQ post-apply-pass-session close) |
| Net delta | RETIRE U-IS-18 (RELOCATED-TO-U-RT-112); ZERO contract change; ZERO spec amendment; ZERO new unit at IS axis; -1 within-axis edge (U-IS-11 → U-IS-18 retired); +1 coverage row supersession at C-IS-05 §5.2 |
| Sibling co-publications | Runtime plan v2.42 NEW U-RT-112 (authoring residence-pinned resolver primitive at harness-runtime per (γ-2)); harness-runtime impl module + tests; harness-is sidecar field lift at `state_ledger_write.py`; arch rec §11.8 Q-γ closure entry; workspace `CLAUDE.md` row bumps (IS plan v2.4 → v2.5 + runtime plan v2.41 → v2.42); clearance markers; retirement event filing (H_T-IS-2 STILL-BOUNDED → PARTIAL) |
| Cross-axis cascade | NONE at v2.5/v2.42 co-publication arc. Producer-site lifts at ~13 CP / runtime / AS composers deferred per Q2=narrow per `[[substrate-pre-landed-consumer-deferred-multi-arc-lift]]` precedent. |
| H_T-IS-2 transit | **STILL-BOUNDED → PARTIAL** at v2.5 + runtime plan v2.42 + impl + tests merge; PARTIAL → RETIRED gated on full producer-site lift per X-AL-2 second conjunct |
