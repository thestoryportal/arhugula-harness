# Spec: Control Plane — v1.21 (delta over v1.20)

---

## Change-note (v1.20 → v1.21)

**Scope of revision.** Fidelity-pure citation-correction patch closing v1.20 §0.8 (h) — "Retirement event filing — H_T-CP-19 PARTIAL → RETIRE-READY transit at batch-21 (separate retirement-event filing arc; operator-discretion timing per existing 7d cadence)" — AND the filing footer "H_T-CP-19 status" line "PARTIAL → RETIRE-READY transit owed at batch-21 retirement event filing" — both as **CLOSED-as-filed-at-batch-21** 2026-05-27. Batch-21 retirement event filing landed at commit `c5582b6` (2026-05-27 21:14, ~10 min after v1.20 publication commit `f59945b` at 21:03) + merged to main at `79865d6`. v1.20 §0.8 (h) + filing footer were authored as forward-pointing references at v1.20 publication; both became stale at batch-21 filing in the immediately-following session.

**Authoring lineage.** v1.21 is a SAME-SESSION-IMMEDIATE-SEQUEL-VIA-SEPARATE-ARC stale-carry closure — distinct from v1.20's same-session-immediate-sequel sub-species (sub-species 3.same-session-immediate-sequel catalogued at OD spec v1.24 §"Distinctive lineage finding"). Here the closure event is a SEPARATE arc (batch-21 retirement event filing) authored ~10 minutes after v1.20 publication; the carry-text framing "(separate retirement-event filing arc; operator-discretion timing per existing 7d cadence)" was accurate at v1.20 publication but became stale on batch-21 filing. Sub-species refinement candidate: **3.retirement-event-filing-arc** — distinct from prior species 3 sub-species (3.code-resolution / 3.fork-doc-closure / 3.workflow-grammar / 3.empirical-verification-of-external-authority / 3.same-session-immediate-sequel) in that the closure event is a workspace-cadence-driven retirement event filing rather than a code / fork-doc / workflow / external-authority / same-session-sequel event. Sub-species set at species 3 now SIX in 4 consecutive arcs (v1.22 OD / v1.23 OD / v1.24 OD / v1.21 CP).

**Empirical verification.** v1.21 audit at HEAD `79865d6`:
- Batch-21 doc `.harness/phase-7d-retirement-events-batch-21.md` exists; §0 declares PARTIAL → RETIRE-READY transit; §4 Filing footer cumulative 28/49 RETIRED + 1/49 RETIRE-READY + 6/49 PARTIAL = 35/49 pipeline-advanced (71.4%).
- `harness-cp/CLAUDE.md` §4.1 row promotion landed in same commit `c5582b6` (RETIRE-READY row populated with CP-19 NEW; PARTIAL row 6 → 5).
- Fork doc Status line bumped to APPLIED-AND-RETIRE-READY at same commit.

**No fork doc filed.** Per workspace precedent for fidelity-pure citation-correction patches anchored at conclusive empirical state — same lineage as OD spec v1.21 + v1.22 + v1.23 + v1.24 narrow closure deltas (this session's sweep batch precedent).

**Co-publication this session.** Sibling closure delta at CP plan v2.26 (same 2 stale carries at §0.8 (c) + filing footer "H_T-CP-19 status" line). Workspace `CLAUDE.md` §2.3 CP spec row + §2.4 CP plan row co-bumped. ZERO cross-axis cascade at production / contract / signature / AC layers (verified via grep this session — batch-21 filing is intra-workspace bookkeeping; no downstream-consumer artifact cites the v1.20 §0.8 (h) framing).

---

## §1 Finding-closure-disposition refresh

### §1.1 v1.20 §0.8 (h) — CLOSED

**Carry-text at v1.20.** *"(h) Retirement event filing — H_T-CP-19 PARTIAL → RETIRE-READY transit at batch-21 (separate retirement-event filing arc; operator-discretion timing per existing 7d cadence)."*

**Disposition at v1.21.** **CLOSED-as-filed-at-batch-21** 2026-05-27. Batch-21 retirement event filed at commit `c5582b6` (2026-05-27 21:14 -0600) merged to main at `79865d6` (2026-05-27 21:15 -0600). v1.20 §0.8 (h) carry-text "(separate retirement-event filing arc; operator-discretion timing)" was accurate at v1.20 publication but became stale on batch-21 filing ~10 min later. Sub-species: 3.retirement-event-filing-arc (NEW sub-species refinement at v1.21).

### §1.2 v1.20 filing footer "H_T-CP-19 status" line — CLOSED

**Text at v1.20.** *"H_T-CP-19 status | Spec-extension layer (layer 1 of 3) **APPLIED at v1.20**; production binding layer (layer 2) **APPLIED at v1.20 co-publication**; multi-deployment e2e layer (layer 3) **DEFERRED to future arc** per fork Q3 ratification. PARTIAL → RETIRE-READY transit owed at batch-21 retirement event filing."*

**Disposition at v1.21.** **CLOSED-via-batch-21-filing** 2026-05-27 — final clause "PARTIAL → RETIRE-READY transit owed at batch-21 retirement event filing" is stale; current state is "PARTIAL → RETIRE-READY transit FILED at batch-21 (`c5582b6`); RETIRE-READY → RETIRED awaits Layer 3 multi-deployment e2e fixture per Q3 ratification". Layers 1+2 status preserved verbatim. Sub-species: 3.retirement-event-filing-arc.

### §1.3 Disposition summary

| v1.20 carry | Closure event | Closure commit | Status at v1.21 |
|---|---|---|---|
| §0.8 (h) | Batch-21 retirement event filing | `c5582b6` (2026-05-27 21:14) | **CLOSED** |
| Filing footer "H_T-CP-19 status" line final clause | Batch-21 retirement event filing | `c5582b6` (2026-05-27 21:14) | **CLOSED** |

Both carries removed from v1.21 §0.8 + filing footer text. v1.20 file body PRESERVED VERBATIM per delta-only-spec-file convention; v1.21 §1 is the canonical-reading amendment for the disposition layer.

---

## §2 Cross-artifact cite-cascade disposition (v1.21 NEW)

| Artifact | Site | Disposition at v1.21 |
|---|---|---|
| `.harness/phase-7d-retirement-events-batch-21.md` | Batch-21 doc IS the closure-evidence | **NO change owed** — batch-21 IS canonical authority anchor for both closures |
| `harness-cp/CLAUDE.md` §4.1 | Row promotion landed at batch-21 commit | **NO change owed** — already current at HEAD |
| `harness-cp/CLAUDE.md` §1.2 spec/plan version cite | "Spec v1.20 + plan v2.25" current | **CO-PUBLISHED this arc** — bumped to "Spec v1.21 + plan v2.26" |
| Workspace `CLAUDE.md` §2.3 CP spec row | v1.20 row narrative | **CO-PUBLISHED this arc** — bumped to v1.21 with closure narrative |
| Workspace `CLAUDE.md` §2.4 CP plan row | v2.25 row narrative | **CO-PUBLISHED this arc** — bumped to v2.26 via sibling CP plan delta |
| Peer artifacts at design-substrate/ | No v1.20 §0.8 (h) cite | **NO change owed** — verified via grep this session |
| Fork doc `class_1_fork_h_t_cp_19_default_gate_level_spec_extension.md` | Status already APPLIED-AND-RETIRE-READY at batch-21 close | **NO change owed** — already current at HEAD |

---

## §3 Sections preserved verbatim at v1.21

Per delta-only-spec-file convention + FM-2 no-extension discipline + fidelity-pure citation-correction scope, the v1.21 amendment touches ONLY the NEW §1 finding-closure-disposition refresh + §2 cross-artifact cite-cascade disposition + §3 sections-preserved-verbatim. The following sections are PRESERVED VERBATIM from their authoring versions:

- **§6.1.Y** (v1.20 `WorkflowManifestEntry.default_gate_level: GateLevel | None = None` field declaration)
- **§0.4** (v1.20 anti-extension invariant scope-narrowing)
- **§0.7 (i) + (ii)** (v1.20 adjacent carries — 3 other deferred fields preserved; Layer 3 e2e deferred)
- **All v1.2–v1.20 lineage substantive amendments**

---

## Adjacent observations (surfaced as findings; NOT patched per FM-2)

(a) **v1.20 §0.8 (h) — CLOSED-as-filed-at-batch-21 at v1.21 §1.1.** Removed from §0.8 carry.

(b) **v1.20 filing footer "H_T-CP-19 status" line final clause — CLOSED-via-batch-21-filing at v1.21 §1.2.** Closure narrative captured at v1.21 §1.2.

(c) **v1.20 §0.7 (i) — 3 other v1.7+ deferred WorkflowManifestEntry fields preserved at anti-extension invariant.** Carried verbatim. `parent_sandbox_tier` + `parent_entry_hash` + `tenant_id` still hardcoded at workflow_driver.py:750/752/754 per empirical grep at HEAD `79865d6`. GENUINE; future operator-discretion arc(s) per Reading D wider scope.

(d) **v1.20 §0.7 (ii) — Layer-3 multi-deployment e2e fixture deferred.** Carried verbatim. Layer 3 e2e composition shape enumerated at batch-21 §3(a). GENUINE; operator-discretion timing per Q3 ratification.

(e) **NEW at v1.21 — sub-species 3.retirement-event-filing-arc catalogued.** v1.21 §1.1 + §1.2 closures via batch-21 filing arc are sub-species refinement of species 3 (resolved-but-carry-stale-inherited) at workflow v1.9 §7.4.7.2. Distinct from species 3.code-resolution + 3.fork-doc-closure + 3.workflow-grammar + 3.empirical-verification-of-external-authority + 3.same-session-immediate-sequel; shared common-ancestor "resolved-but-carry-stale-inherited" with distinct closure-event-class (retirement event filing per existing 7d cadence). Sub-species set at species 3 now SIX in 4 consecutive arcs (v1.22 OD / v1.23 OD / v1.24 OD / v1.21 CP). Workflow v1.9 §7.4.7.2 "Sub-species" column extension increasingly warranted. NOT patched per FM-2.

---

## Filing footer

| Field | Value |
|---|---|
| Version | v1.21 (Fidelity-pure citation-correction patch closing v1.20 §0.8 (h) batch-21 filing carry + filing footer "H_T-CP-19 status" line final clause — both as **CLOSED-as-filed-at-batch-21** 2026-05-27; NEW §1 finding-closure-disposition refresh + §2 cross-artifact cite-cascade + §3 sections-preserved-verbatim; sub-species 3.retirement-event-filing-arc catalogued at §"Adjacent observations" (e); v1.20 + earlier files PRESERVED VERBATIM) |
| Trigger | Same-session sweep arc post-batch-21 filing — empirical-verification audit at HEAD `79865d6` surfaced 2 stale carries at v1.20 §0.8 (h) + filing footer per workflow v1.9 §7.4.7.3 discipline |
| Supersedes | v1.20 §0.8 (h) + filing footer "H_T-CP-19 status" line final clause "PARTIAL → RETIRE-READY transit owed at batch-21 retirement event filing" — both stale post-batch-21 close |
| Scope of revision | NARROW: NEW §1 + §2 + §3. ZERO contract / signature / AC / behavior change. Co-publication: workspace CLAUDE.md CP spec row + harness-cp/CLAUDE.md §1.2 cite + sibling CP plan v2.26 delta. |
| H_T-CP-19 status | Layer 1 + 2 APPLIED at v1.20 (preserved); Layer 3 DEFERRED per Q3 (preserved); PARTIAL → RETIRE-READY transit **FILED at batch-21** (`c5582b6` 2026-05-27 21:14; merged `79865d6` 21:15). |
| Cross-axis cascade | ZERO. Verified via grep at HEAD. |
| Authority anchor | Batch-21 retirement event doc `.harness/phase-7d-retirement-events-batch-21.md` (2026-05-27 21:14, `c5582b6`) |
| Predecessor | v1.20 (Workflow §4.1.2 Class-2 amendment landing `WorkflowManifestEntry.default_gate_level` field) |
| Successor | (none — current canonical) |
| Date | 2026-05-27 |
