# Sub-phase 7c — cross-axis composition: prerequisites report

**Filed:** 2026-05-16, at 7c entry. **Author:** phase-7-cross-axis-composition (orientation pass).
**Status:** ✅ **ALL FOUR PREREQUISITES RESOLVED 2026-05-16** — see §"Resolution" below. 7c bucket wiring is now unblocked.

---

## Resolution (2026-05-16 — 7c prerequisite pass)

All four prerequisites resolved in-CLI. Deliverables:

| Prereq | Outcome | Artifact |
|---|---|---|
| 1 — placeholder carrier IDs | 20 OD-outbound placeholder rows resolved to canonical carriers by contract anchor against producer-plan coverage tables. No Class 1 (every anchor resolved to exactly one carrier). 3 Class 3 hint-imprecision items logged. | `Cross_Axis_Composition_Document_v2_2.md` §2.3.5/§2.3.6; `Implementation_Plan_Operational_Discipline_v2_11.md`; `.harness/cxa_7c_placeholder_resolution.md` |
| 2 — CP `RoleRoutingBinding` Class 1 | **Stale plan text.** The Class 1 was operator-resolved 2026-05-16 (R-2/W-2 schemas; U-CP-04 full-landed; verified in `harness-cp/src/.../routing_manifest_residence.py`). CP plan v2.9 §0.5 never caught up. Reconciled — not a live blocker. | `Implementation_Plan_Control_Plane_v2_10.md` §0.2 |
| 3 — CXA §3 staleness | Re-verified vs landed code. §3.3 breaker Tier column struck (OD v2.8 D-3); §3.4 `audit.signature.*` 4th attr `sha256`→`key_period` (OD v2.7 D-3). Cascade: P1-CXA-1 **resolved by convergence** — OD and IS `audit.signature.*` sets now byte-exact identical. | `Cross_Axis_Composition_Document_v2_2.md` §3.3–§3.7 |
| 4 — CXA-OD-IS-EDGE-DRIFT | Operator decision 2026-05-16: **wire 4** (OD plan v2.4 canonical), not 6. Aggregate edge count 101 → **99**. | `Cross_Axis_Composition_Document_v2_2.md` §2.1/§2.3.4 |

**Net effect:** aggregate cross-axis edges 101 → 99 (OD→IS 6→4). All 99 edges carry canonical carrier IDs. §3 Pattern P1 clear. 7c bucket wiring may open — 6 buckets in axis-topological order (AS→IS 13, CP→IS 36, CP→AS 24, OD→IS 4, OD→AS 10, OD→CP 12).

**Prereq 1 scope catch (during resolution):** U-OD-27's unit body still declared the two
OD→IS edges that OD plan v2.4 §0.4.2 deleted from §4.5.1 — v2.4 revised the enumeration but
did not propagate the deletion into the unit body. OD plan v2.11 §0.5 strikes both terms
(9 unit bodies revised, not 8).

**Known carry (Class 3, non-blocking) — `harness-cp/CLAUDE.md` staleness.** The CP-axis
subdirectory `CLAUDE.md` plan-pointer (line 20) cites `Implementation_Plan_Control_Plane_v2_6.md`
(57 units) — four versions stale (CP is now at v2.10, 58 units) and pre-dating this prerequisite
pass. Root `CLAUDE.md` §2.4 and `harness-od/CLAUDE.md` were updated to the current versions in
this pass; `harness-cp/CLAUDE.md` was left as-is because a correct fix requires reconciling its
v2.6-era cluster tables, not just the version token — out of scope for the 7c prerequisite pass.
Filed here as a known carry for a dedicated `harness-cp/CLAUDE.md` reconciliation.

*Original orientation report (the 4 gates as filed at 7c entry) preserved below for the record.*

---

## Entry-gate (skill §1.3) — PASS

All four axis-streams complete (IS 17/17, AS 33/33, CP 57/57, OD 35/35); all four terminal exporter manifests landed (U-IS-17, U-AS-33, U-CP-54/55, U-OD-34). 7c is entry-eligible.

## The 101 edges (CXA v2.1 §2.3)

| Bucket | Edges | Carrier IDs | Wireable now? |
|---|---|---|---|
| AS → IS (§2.3.1) | 13 | canonical (real `U-IS-NN` resolved) | ✅ yes |
| CP → IS (§2.3.2) | 36 | canonical | ⚠️ yes, except the U-CP-04 edges — see Prereq 2 |
| CP → AS (§2.3.3) | 24 | canonical | ✅ yes |
| OD → IS (§2.3.4) | 6 | **placeholder `U-IS-NN`** | ❌ blocked — Prereq 1 + 4 |
| OD → AS (§2.3.5) | 10 | **placeholder `U-AS-NN`** | ❌ blocked — Prereq 1 |
| OD → CP (§2.3.6) | 12 | **placeholder `U-CP-NN`** | ❌ blocked — Prereq 1 |

73 edges (AS→IS, CP→IS, CP→AS) are largely wireable; 28 OD-outbound edges are placeholder-blocked.

## Prerequisite 1 — placeholder carrier IDs (Class 1, skill §7)

CXA v2.1 §2.3.4/§2.3.5/§2.3.6 cite `U-IS-NN` / `U-AS-NN` / `U-CP-NN` placeholders for **all 28 OD-outbound edges** — never resolved to canonical carrier unit IDs. The OD plan bodies carry the same placeholders (U-OD-29 v2.10 still declares `U-AS-NN (cross-axis: AS — C-AS-12 §12.4)`). Per skill §4.2 Pattern P1 verification + §7, a placeholder carrier ID is a verification failure → **Class 1 halt** → Form A citation-precision revision (the F3-02 precedent: OD plan v2.4 resolved exactly one such row, `U-IS-NN → U-IS-12`, leaving the rest).

**Resolution needed:** a citation-resolution pass — for each of the 28 OD-outbound edges, resolve the placeholder to the canonical carrier unit ID by reading the producer-axis plan (find the unit implementing the cited contract section). Lands as a CXA-doc revision (§2.3.4/5/6 tables) + per-unit OD-plan Form A revisions. ~20 distinct placeholders in the CXA doc.

## Prerequisite 2 — CP plan carried Class 1 (`RoleRoutingBinding` / `WorkloadRoutingOverride`)

CP plan v2.9 §0.5 is titled **"Two sub-records left Class 1 — `RoleRoutingBinding`, `WorkloadRoutingOverride`"** (at U-CP-04); root `CLAUDE.md` §2.4 confirms "left Class 1 2026-05-16". But the project memory records the operator resolved them 2026-05-16 (U-CP-04 upgraded to full-land, CP suite 465). **Plan-vs-landed-state divergence.** U-CP-04 is a CP→IS source unit (CXA §2.3.2 — U-CP-04 → U-IS-01/02/06). Before the CP→IS bucket wires the U-CP-04 edges, confirm: are the two sub-records resolved (→ CP plan needs a catch-up note) or genuinely open (→ live Class 1 blocking those edges)?

## Prerequisite 3 — CXA v2.1 is stale vs OD plan v2.7–v2.10

The CXA doc's Pattern P1 verification (§3) was run against pre-v2.7 OD plan state. Two drifts:
- §3.3 shows `harness.breaker.*` attributes with `REQUIRED` / `CONDITIONAL` tiers — OD plan **v2.8 D-3 STRUCK** that tier classification (no spec basis; FF-1).
- §3.4 shows OD U-OD-30 `AuditSignatureAttributes` = `{value, algorithm, key_id, sha256}` — OD plan **v2.7 D-3 corrected** it to `{value, algorithm, key_id, key_period}` (`sha256` was an un-spec'd field; struck).

§3.7 declares "No P1-CXA findings remain open at v2" — true as of v2-era OD plan, but the OD plan has since moved (v2.7/v2.8/v2.9/v2.10). **Pattern P1 byte-exact needs re-verification against the current OD plan v2.10 + OD spec v1.4** before the OD-touching buckets wire.

## Prerequisite 4 — CXA-OD-IS-EDGE-DRIFT (Class 2, skill §7)

CXA v2.1 §2.3.4 enumerates **6** OD→IS edges; OD plan v2.4/v2.6 §4.5.1 enumerates **4** (C3-15 Path (i-refined) deletions). Known Class 3 informational at IS plan §0.9 / OD plan §0.9; skill §7 escalates it to a **Class 2 operator decision** at wiring time — wire 6 (CXA baseline) or 4 (OD plan canonical)?

## Other axes — clean

AS plan chain — no FF-N carried forks. IS plan v2.3 §0.6 carries one deferred non-blocking action-item (AI-R2-1, U-IS-02 landed-source retrospective) — not a fork. CXA §0.5 forward-flagged concerns — F2-12 closure-path + Workflow §7 fidelity-grammar — both carry-forwards, not 7c-bucket blockers.

## Recommended sequencing

7c is a large sub-phase (101 typed seams). The prerequisite-resolution pass is itself substantial — Prereq 1 (28-edge placeholder resolution) is a CXA-doc + OD-plan revision; Prereq 2 (CP Class 1 reconcile) and Prereq 3 (CXA re-verify) are bounded checks; Prereq 4 is one operator decision. Recommended:

1. **Prerequisite pass (a fresh session):** resolve all 28 OD-outbound placeholders; reconcile the CP `RoleRoutingBinding`/`WorkloadRoutingOverride` Class 1 against landed state; re-verify Pattern P1 §3 against OD plan v2.10 / spec v1.4; take the operator's OD→IS edge-count decision (Prereq 4). Output: a CXA v2.2 (placeholders resolved + Pattern P1 re-verified).
2. **Bucket wiring:** then wire the 6 buckets in axis-topological order — AS→IS, CP→IS, CP→AS, OD→IS, OD→AS, OD→CP — each bucket a coherent batch, operator confirmation at bucket close.

The 73 non-OD-source-bucket edges (AS→IS, CP→IS, CP→AS) could be wired ahead of the OD-outbound buckets if the operator wants to parallelize — but CP→IS's U-CP-04 edges still need Prereq 2 cleared first.
