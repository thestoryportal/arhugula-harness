# Cross-Axis Composition Document (v2.15)

*Delta over v2.14. v2.15 lands the long-carried **U-CP-68 → U-AS-03 ToolContract seam** at §2.3.3 row 6 per `.harness/class_3_drift_cxa_v2_5_cp_as_bucket_extension_u_cp_68.md` (filed 2026-05-21 at cluster 10-CP-C close; landed at U-CP-70 commit `2e417e0` in runtime Pattern-P1 enforcement test; CXA enumeration amendment owed since). The CP→AS bucket grows 5 → 6 genuine canonical edges; aggregate matrix CP→AS cell 18 → 19; aggregate 100 → 101; genuine 30 → 31. This amendment was explicitly anticipated at the fork doc §2 + "Next CXA revision pass" routing. v2.15 publishes the CXA-side amendment + workspace CLAUDE.md §1.1 + §2.4 cardinality refresh + harness-cp/CLAUDE.md §2.3 + §1.1 outbound cite refresh in a single bundled arc. All other v2.14 + v2.13 + v2.12 + v2.11 + v2.10 + v2.9 + v2.8 + v2.7 + v2.6 substantive content preserved verbatim by reference.*

## §0 Change note (v2.14 → v2.15)

### §0.1 Revision context — U-CP-68 ToolContract CP→AS Pattern-P1 seam landing

Per `.harness/class_3_drift_cxa_v2_5_cp_as_bucket_extension_u_cp_68.md` (filed 2026-05-21 at cluster 10-CP-C close): the U-CP-68 → U-AS-03 ToolContract seam is the 6th genuine typed seam at the §2.3.3 CP→AS bucket. The edge is a canonical Pattern-P1 symbol-equality import: CP-side consumer `harness_cp.per_server_trust_evaluator` imports the AS-side type `ToolContract` from `harness_as.tool_contract`. Driver: CP spec v1.10 §27.1 — `PerServerTrustEvaluator.evaluate(...)` canonical signature declares `tool_contract: ToolContract | None`. Physical import is spec-mandated.

**Timing context.** The seam landed at runtime Pattern-P1 enforcement test `harness-runtime/tests/integration/test_cxa_pattern_p1.py` at U-CP-70 commit `2e417e0` (`PATTERN_P1_SEAMS` 24 → 25 entries; `test_seam_count_is_25` test rename) — runtime enforcement has been in agreement with the landed code since 2026-05-21. The CXA canonical enumeration document at v2.5/v2.6/v2.7/v2.8/v2.9/v2.10/v2.11/v2.12/v2.13/v2.14 carried 5-in-CP→AS-bucket / 99-then-100 aggregate without absorbing this row. v2.15 publishes the CXA-side amendment.

**Pattern catalogued — same-shape carry as v2.9 cost-attribution row 8.** v2.9 landed the cost-attribution audit-write seam (CP→OD row 8) after carrying the owe across batches 13/14/15/16/17 + CXA v2.7/v2.8 narrow-scope publications that explicitly disclaimed it. v2.15 follows the same pattern at the CP→AS bucket: runtime enforcement landed first; CXA canonical enumeration follows at a later narrow-scope arc. This is a NATURAL CONSEQUENCE of the test-led pattern where the runtime Pattern-P1 enforcement check serves as the de-facto canonical enumeration during the carry window, and the CXA file catches up at the next CXA revision pass.

### §0.2 Sections revised

§0 (this change note); §2.1 (aggregate 4×4 matrix — CP→AS bucket cell 18 → 19; aggregate total 100 → 101); §2.3.3 (CP→AS per-bucket enumeration — 5 → 6 genuine rows; row 6 NEW); §2.4 (per-axis outbound posture summary — CP outbound 62 → 63, CP genuine 21 → 22; aggregate genuine 30 → 31; AS outbound + AS genuine unchanged per v2.6 namespace-ownership convention — ToolContract is AS-axis-owned at namespace layer BUT the edge attribution at §2.4 follows the dependency-direction primary convention applied to vanilla Pattern-P1 symbol-equality imports per the existing 5 CP→AS genuine rows). All other sections preserved verbatim from v2.14 (which preserved verbatim from v2.13 + v2.12 + v2.11 + v2.10 + v2.9 + v2.8 + v2.7 + v2.6).

### §0.3 §2.3.3 row 6 amendment (CP→AS bucket, U-CP-68 consumer + U-AS-03 producer + ToolContract symbol)

The v2.3-retargeted §2.3.3 5-row genuine bucket enumeration (preserved verbatim through v2.4 + v2.5 + v2.6 + v2.7 + v2.8 + v2.9 + v2.10 + v2.11 + v2.12 + v2.13 + v2.14) is amended at v2.15 with one new row appended. Row 6 entry:

> **U-CP-68** | **U-AS-03** | **CP spec v1.10 §27.1 (PerServerTrustEvaluator.evaluate signature — `tool_contract: ToolContract | None`)** | **G — Pattern-P1 symbol-equality import; CP-side consumer `harness_cp.per_server_trust_evaluator` imports AS-side type `ToolContract` from `harness_as.tool_contract`; physical import is spec-mandated. Cluster 10-CP-C close (2026-05-21); runtime Pattern-P1 enforcement test at `harness-runtime/tests/integration/test_cxa_pattern_p1.py` PATTERN_P1_SEAMS row added at U-CP-70 commit `2e417e0`. (NEW v2.15; runtime enforcement landed 2026-05-21; CXA canonical enumeration absorbs at v2.15)**

### §0.4 Aggregate matrix delta

**§2.1 4×4 adjacency matrix — REVISED (CP→AS bucket cell 18 → 19):**

| Source ↓ / Target → | IS | AS | CP | OD |
|---|---|---|---|---|
| **IS** | *(self)* | 0 | 0 | 0 |
| **AS** | 11 | *(self)* | 0 | 0 |
| **CP** | 37 | **19 (v2.15)** | *(self)* | 8 |
| **OD** | 4 | 10 | 12 | *(self)* |

**101 canonical cross-axis relationships** (100 at v2.14 + 1 new CP→AS genuine-typed-seam edge at v2.15). Genuine typed seams within that: **31** (30 at v2.14 + 1). Convention-level: **48** (unchanged from v2.12). Phase-2-runtime: **22** (unchanged). 31 + 48 + 22 = 101.

**§2.4 per-axis outbound posture summary delta:**

| Axis | v2.14 canonical outbound | v2.15 canonical outbound | v2.14 genuine | v2.15 genuine | Attribution rationale |
|---|---|---|---|---|---|
| IS | 0 | 0 | 0 | 0 | unchanged |
| AS | 11 | 11 | 7 | 7 | unchanged — row 6 is CP-side consumer; AS-side U-AS-03 is producer-of-symbol but the edge direction in §2.1 + §2.4 is CP→AS (CP outbound = CP depends on AS) per the established v2.3-and-prior CP→AS bucket convention applied to the existing 5 genuine rows |
| CP | 62 | **63 (v2.15: +1 row 6 — ToolContract seam)** | 21 | **22 (v2.15: +1 row 6)** | row 6 is the 22nd CP-axis genuine outbound seam (alongside the 5 existing v2.3-retargeted CP→AS genuine + 16 other CP→IS/CP→OD genuine); standard CP→AS Pattern-P1 symbol-equality attribution |
| OD | 27 | 27 | 2 | 2 | unchanged |
| **Aggregate** | **100** | **101 (v2.15: +1)** | **30** | **31 (v2.15: +1)** | — |

**Convention preserved-with-application note.** §2.4 attribution at the existing 5 CP→AS bucket genuine rows is CP-axis (CP outbound) per the v2.3-retargeted matrix-direction convention applied to Pattern-P1 symbol-equality imports. Row 6 applies the SAME convention to a 6th Pattern-P1 row — no namespace-ownership-vs-matrix-direction tension here (unlike the v2.9 row 8 CP→OD case where the audit-write physical-file lives at OD-side but the namespace was OD-owned). Row 6 is a vanilla CP→AS Pattern-P1 edge: CP-side consumer + AS-side producer + AS-side-owned namespace + dependency-direction CP→AS. All three attributions converge on CP outbound +1; no §2.1-vs-§2.4 divergence.

### §0.5 Status posture

Proposed (v2.14) → **Proposed (v2.15)**. v2.15 is an additive amendment — one new row at §2.3.3 + aggregate matrix update + per-axis outbound posture update. No prior edge classification change; no prior edge spec-version cite change; no acceptance criterion change at any prior row.

### §0.6 Forward-cite acknowledgement

Row 6 cites `CP spec v1.10 §27.1`. CP spec v1.10 + v1.11 + v1.12 + v1.13 + v1.14 + v1.15 + v1.16 + v1.17 + v1.18 + v1.19 (current canonical at HEAD) preserve §27.1 verbatim per the delta-only-spec-file convention. **No spec-extension at v2.15** — the cite resolves byte-exact against the canonical reading at CP spec v1.10-and-later.

### §0.7 Adjacent defects surfaced (not patched per FM-2 no-extension discipline)

(i) **harness-as/CLAUDE.md §1.1 + §2.2 cardinality drift carry preserved.** `harness-as/CLAUDE.md` lines 13 + 69 + 76 cite `Cross_Axis_Composition_Document_v2_1.md` baseline with "24 CP→AS + 10 OD→AS = 34 inbound" — these are v2.1 baseline counts that were superseded at v2.3 reclassification (18 CP→AS at v2.4-and-later per harness-cp/CLAUDE.md). This is a pre-existing carry from the `[[class_3_tension_per_axis_claude_md_v2_1_to_v2_4_count_drift]]` family. v2.15 does NOT patch this carry — refreshing harness-as/CLAUDE.md from v2.1 baseline to v2.15 (skipping intermediate versions) would conflate the v2.1→v2.4 drift absorption with the v2.15 row 6 addition in a single edit. Surfaced; NOT patched at v2.15 per FM-2 (per-axis CLAUDE.md authoring scope is workspace governance pointer-update; the v2.1→v2.4 absorption is a separate arc).

(ii) **harness-od/CLAUDE.md §2.2 inbound row count — no change owed.** Row 6 is a CP→AS edge; OD-axis is uninvolved. ZERO refresh owed at `harness-od/CLAUDE.md`.

(iii) **harness-cxa/CLAUDE.md bucket-count refresh — no change at structural layer.** Per v2.6 §0.5 convention, harness-cxa/ hosts the converter modules + CXA seam instantiation; bucket counts are sourced from the CXA file directly. v2.15 amends the source-of-truth; no per-axis CLAUDE.md edit owed at harness-cxa/.

### §0.8 Downstream absorption owed (post-v2.15)

(a) Workspace `CLAUDE.md` §1.1 CXA row cardinality refresh: "100 canonical cross-axis relationships ... per `Cross_Axis_Composition_Document_v2_9.md` §2.3 (30 genuine ...)" → "101 canonical cross-axis relationships ... per `Cross_Axis_Composition_Document_v2_15.md` §2.3 (31 genuine ...)". **Patched at v2.15 co-publication.**
(b) Workspace `CLAUDE.md` §2.4 CXA row version bump (v2.14 → v2.15) + description amendment: cardinality bump (100 → 101 / 30 → 31) + ToolContract row 6 status note. **Patched at v2.15 co-publication.**
(c) `harness-cp/CLAUDE.md` §1.1 CP outbound 62 → 63 + "37 → IS + 18 → AS + 7 → OD" → "37 → IS + 19 → AS + 7 → OD" + CXA cite bump v2.9 → v2.15. **Patched at v2.15 co-publication.**
(d) `harness-cp/CLAUDE.md` §2.3 row "CP → AS (outbound) | 18 | ..." → "CP → AS (outbound) | 19 | ... `Cross_Axis_Composition_Document_v2_15.md` §2.3.3 ...". **Patched at v2.15 co-publication.**
(e) `.harness/class_3_drift_cxa_v2_5_cp_as_bucket_extension_u_cp_68.md` Status line refresh: OPEN → CLOSED-via-v2.15. **Patched at v2.15 co-publication.**
(f) `harness-as/CLAUDE.md` §1.1 + §2.2 v2.1→v2.x drift absorption — STILL OWED per §0.7(i) above (separate arc; not v2.15 scope).

---

## Filing footer

| Field | Value |
|---|---|
| Artifact | `Cross_Axis_Composition_Document_v2_15.md` |
| Version | v2.15 |
| Filing event | U-CP-68 → U-AS-03 ToolContract CP→AS Pattern-P1 seam landing per `.harness/class_3_drift_cxa_v2_5_cp_as_bucket_extension_u_cp_68.md` (filed 2026-05-21 at cluster 10-CP-C close; runtime Pattern-P1 enforcement landed 2026-05-21 at U-CP-70 commit `2e417e0`; CXA canonical enumeration absorbs at v2.15). Carried across CXA v2.7/v2.8/v2.9/v2.10/v2.11/v2.12/v2.13/v2.14 narrow-scope publications that did NOT include the CP→AS bucket extension. 2026-05-27 |
| Predecessor | `Cross_Axis_Composition_Document_v2_14.md` (preserved verbatim outside the §0 + §2.1 + §2.3.3 + §2.4 amendment sites enumerated at §0.2) |
| Successor | (none — current canonical) |
| Aggregate count | **101 canonical cross-axis relationships** (100 at v2.14 + 1 new G CP→AS bucket-membership at v2.15). **31 genuine typed seams** (30 at v2.14 + 1). Convention-level **48** preserved (since v2.12). Phase-2-runtime **22** preserved. 31 + 48 + 22 = 101. |
| CP→AS bucket | **19 canonical edges** (was 18 at v2.14 + 1 v2.15 row 6 ToolContract seam). **6 genuine** (was 5 at v2.4-and-later + 1 v2.15 row 6); 13 convention/phase-2-runtime preserved. |
| Per-axis attribution | CP outbound 62 → 63 (+1 row 6 — standard CP→AS Pattern-P1 symbol-equality attribution); AS outbound preserved 11 (unchanged — row 6 is CP-side consumer per v2.3-and-prior CP→AS bucket convention); OD unchanged; vanilla CP→AS Pattern-P1 edge with all three attributions (dependency-direction + namespace-ownership + producer-axis) converging on CP outbound |
| ToolContract seam status | **LANDED at v2.15** (runtime Pattern-P1 enforcement landed 2026-05-21 at U-CP-70 commit `2e417e0`; CXA canonical enumeration absorbed at v2.15). |
| Operator authority | `.harness/class_3_drift_cxa_v2_5_cp_as_bucket_extension_u_cp_68.md` filing 2026-05-21 + CP spec v1.10 §27.1 PerServerTrustEvaluator canonical signature mandate |
| Related forks | (none — Class 3 drift filing; non-blocking) |
| Related memory | `[[class_3_tension_per_axis_claude_md_v2_1_to_v2_4_count_drift]]` (harness-as/CLAUDE.md still at v2.1 baseline per §0.7(i) carry preservation) |
| Date | 2026-05-27 |
