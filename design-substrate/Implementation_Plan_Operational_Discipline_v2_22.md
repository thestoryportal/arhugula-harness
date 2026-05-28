# Implementation Plan: Operational Discipline — v2.22 (delta over v2.21)

---

## Change-note (v2.21 → v2.22)

**Scope of revision.** Fidelity-pure citation-correction patch closing v2.21 §"Adjacent observations" finding (c) — `harness_breaker_schema.py:21` docstring drift — as **CLOSED-at-commit-`0709b33`** 2026-05-27. The v2.21 carry-text framing ("AttributeTier enum has no `REQUIRED` / `CONDITIONAL` members" stale post-v2.20 + v2.21) became stale at production-side doc-hygiene commit `0709b33` (`doc-hygiene(harness_breaker_schema.py): drop stale AttributeTier enum-absence claim from STRIKE rationale`) which landed AFTER v2.21 publication. v2.22 corrects the carry-text disposition at the canonical-reading layer.

**Source of closure.** Production doc-hygiene commit `0709b33` updated the docstring at `harness-od/src/harness_od/harness_breaker_schema.py` lines 18-29 — the docstring now correctly cites `REQUIRED_STABLE` + `RECOMMENDED_DEVELOPMENT` + `OPT_IN_CONTENT` + `CONDITIONALLY_REQUIRED` enum members (the v2.21 carry framing claimed the docstring said "no REQUIRED / CONDITIONAL members"; that text is no longer present at HEAD). Empirical verification at worktree HEAD via grep this session confirms the docstring matches the v2.21-expected state.

**Audit lineage.** v2.22 is the SECOND production application of workflow v1.9 §7.4.7.3 across the workspace carry-set sweep 2026-05-27 (operator-routed "run the sweep" arc post-workflow-v1.9 publication). The sweep enumerated 42 carries; OD plan v2.21 (c) surfaced as STALE per species 5 (post-authoring stale carry — v2.21 authored 2026-05-27 with carry framing that became stale at commit `0709b33` landing same day post-authoring).

**Species classification.** Closure via species 5 (post-authoring stale carry) at workflow v1.9 §7.4.7.2. v2.21 was authored at the OD plan revision arc with the (c) carry preserved verbatim from v2.20 (e); the docstring-drift defect was real at v2.21 authoring time, but landed-fixed at commit `0709b33` (2026-05-27) which was sibling-published with workspace ledger-v2 supersession + harness_breaker_schema.py doc-hygiene merge `a0553ec`. The carry-text propagated unrefreshed because v2.21 was a separate-arc absorption (OD spec v1.19 tier redistribution).

**No fork doc filed.** Per workspace precedent for fidelity-pure citation-correction patches anchored at conclusive empirical state (production grep at HEAD verifies the docstring matches the expected state). Commit `0709b33` IS canonical authority anchor.

**Co-publication this session.** Sibling closure deltas at OD spec v1.22 + CXA v2.13 + CP plan v2.24. Workspace `CLAUDE.md` §2.4 OD plan row co-bumped. ZERO contract change; ZERO unit re-decomposition; ZERO AC change; ZERO DAG topology change.

---

## §1 Finding-closure-disposition refresh

### §1.1 v2.21 §"Adjacent observations" finding (c) — CLOSED

**Carry-text at v2.21.** *"(c) v2.20 finding (e) — `harness_breaker_schema.py:21` docstring drift. Preserved verbatim at v2.21. The docstring claim 'AttributeTier enum has no `REQUIRED` / `CONDITIONAL` members' is now stale on TWO dimensions post-v2.20 + v2.21: (i) v2.20 added `CONDITIONALLY_REQUIRED` member (the 'no `CONDITIONAL`' claim is stale); (ii) v2.21 populates the `CONDITIONALLY_REQUIRED` tier with 3 attrs (the docstring's purpose — explaining harness.breaker.* tier vs base-layer tier separability — is now stronger because the Conditionally Required tier is populated). NOT patched per FM-2; surfaced for follow-on doc-hygiene arc."*

**Disposition at v2.22.** **CLOSED-at-commit-`0709b33`** 2026-05-27. Doc-hygiene commit `0709b33` (`doc-hygiene(harness_breaker_schema.py): drop stale AttributeTier enum-absence claim from STRIKE rationale`) updated the docstring at `harness-od/src/harness_od/harness_breaker_schema.py` lines 18-29 to correctly cite all 4 `AttributeTier` enum members. Empirical verification via grep at worktree HEAD: the docstring now reads "the U-OD-04 `AttributeTier` enum has carried `REQUIRED_STABLE` + `RECOMMENDED_DEVELOPMENT` + `OPT_IN_CONTENT` members since v1.2 baseline and gained `CONDITIONALLY_REQUIRED` at OD spec v1.16 §1.2 (populated with 3 attributes at v1.19 §1.1 per-attribute tier redistribution)" — matches the v2.21 expected state. The carry's purpose (surface the docstring drift for follow-on doc-hygiene arc) is fulfilled at the production-side commit.

### §1.2 Disposition summary

| v2.21 carry | Closure event | Closure commit | Status at v2.22 |
|---|---|---|---|
| §"Adjacent observations" (c) | `harness_breaker_schema.py` doc-hygiene update | `0709b33` (2026-05-27) | **CLOSED** |

Carry (c) removed from v2.22 §"Adjacent observations" carry-set. v2.21 file body PRESERVED VERBATIM per delta-only-plan-file convention; v2.22 §1 is the canonical-reading amendment for the disposition layer.

---

## §2 Cross-artifact cite-cascade disposition (v2.22 NEW)

| Artifact | Site | Disposition at v2.22 |
|---|---|---|
| `harness-od/src/harness_od/harness_breaker_schema.py:18-29` | Docstring at module level | **NO change owed** — production state IS the closure-evidence at commit `0709b33` |
| `Spec_Operational_Discipline_v1_22.md` (sibling sweep delta) | OD spec v1.22 §"Adjacent observations" | NO change owed — OD spec v1.22 + earlier do NOT cite the docstring text |
| Workspace `CLAUDE.md` §2.4 OD plan row narrative | v2.21 row narrative | **CO-PUBLISHED this arc** — bumped to v2.22 with closure narrative |
| Peer artifacts at design-substrate/ | NO citation of `harness_breaker_schema.py` docstring | NO change owed — verified via grep this session |

---

## §3 Sections preserved verbatim at v2.22

Per delta-only-plan-file convention + FM-2 no-extension discipline + fidelity-pure citation-correction scope, the v2.22 amendment touches ONLY §1 + §2 + §"Adjacent observations" refresh. The following sections are PRESERVED VERBATIM from v2.21:

- **U-OD-04 plan body** (authored at `Implementation_Plan_Operational_Discipline_v2_5.md` §3.2.1; v2.21 amendments at AC #4 tier redistribution preserved)
- **All v2.20 + earlier substantive content**
- **DAG topology + dependency edges** (v2.21 preserved verbatim from v2.20)

---

## Adjacent observations (surfaced as findings; NOT patched per FM-2)

(a) **v2.21 finding (c) — CLOSED-at-commit-`0709b33` at v2.22 §1.1.** Removed from "Adjacent observations" carry.

(b) **v2.21 finding (a) — CLOSED at v2.21.** Already closed; preserved as documented closure.

(c) **v2.21 finding (b) — CLOSED at OD spec v1.17 / v1.18.** Already closed; preserved as documented closure.

(d) **v2.21 finding (d) — v1.19 (g)+(h) CLOSED-via-Path-A.** Already closed; preserved as documented closure.

(e) **v2.21 finding (e) — v1.20 (b)+(c)+(d)+(i) carries preserved at OD spec.** Carried verbatim; out of scope at plan-layer single-unit refresh. v2.22 does NOT touch this carry.

(f) **v2.21 finding (f) — AC #5 §4.4 hierarchy claim preserved verbatim.** Carried verbatim; v1.20 §1.1 narrowing unaffected at AC #5 (constant-value-only test). v2.22 does NOT touch this carry.

(g) **NEW at v2.22 — post-authoring-stale-carry-text-disposition pattern observation.** v2.21 (c) is a textbook example of workflow v1.9 §7.4.7.2 species 5 (post-authoring stale carry) at the OD plan layer: carry text genuine at v2.21 authoring; downstream code resolution at commit `0709b33` landed same day post-authoring; carry-text propagated unrefreshed until sweep audit caught it. Class 3 informational; NOT patched per FM-2; validates the v1.9 §7.4.7.3 audit discipline operationally at the plan-layer in addition to the spec-layer.

---

## Filing footer

| Field | Value |
|---|---|
| Version | v2.22 (Fidelity-pure citation-correction patch closing v2.21 §"Adjacent observations" finding (c) — `harness_breaker_schema.py:21` docstring drift — as **CLOSED-at-commit-`0709b33`** 2026-05-27; NEW §1 + §2 + §3; v2.21 + earlier files PRESERVED VERBATIM) |
| Trigger | Workflow v1.9 §7.4.7.3 sweep audit 2026-05-27 (operator-routed "run the sweep") |
| Supersedes | v2.21 §"Adjacent observations" (c) "NOT patched per FM-2; surfaced for follow-on doc-hygiene arc" framing — superseded at v2.22 §1.1 closure |
| Scope of revision | NARROW: §1 finding-closure-disposition refresh + §2 cross-artifact cite-cascade. ZERO contract / signature / AC / DAG change. Co-publication: workspace CLAUDE.md OD plan row bump. |
| Cross-axis cascade | ZERO. |
| Authority anchor | Production doc-hygiene commit `0709b33` (2026-05-27) at `harness-od/src/harness_od/harness_breaker_schema.py` |
| Predecessor | v2.21 (Substantive canonical-reading amendment at U-OD-04 AC #4 absorbing OD spec v1.19 tier redistribution) |
| Successor | v2.23 (next operator-discretion arc) |
| Sweep cohort | 3 of 4 closure deltas in 2026-05-27 sweep batch (siblings: OD spec v1.22 [authored], CXA v2.13 [authored], CP plan v2.24) |
