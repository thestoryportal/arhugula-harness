# Cross-Axis Composition Document (v2.9)

*Delta over v2.8. v2.9 lands the long-carried **cost-attribution audit-write seam** at §2.3.7 row 8 per `.harness/Remaining_Work_Closure_Arc_Handoff_v1.md` §6 (operator-ratified Option 1; Phase D iteration-2 F2-02 absorption). The CP→OD bucket grows 7 → 8 canonical edges; aggregate 99 → 100; genuine 29 → 30. This amendment was explicitly anticipated at v2.7 §0.NOTE + v2.8 §0.4 critical preservation note and at OD plan v2.16 §0(d) "Sub-arc B sequel". v2.9 publishes the CXA-side amendment alone (per the handoff scope); OD-side CostRecordAuditPayload authoring (OD spec v1.9 → v1.10 NEW §C-OD-NN) + OD plan revision at U-OD-41 remain outstanding as the OD-side sub-arc B sequel. All other v2.8 + v2.7 + v2.6 substantive content preserved verbatim by reference.*

## §0 Change note (v2.8 → v2.9)

### §0.1 Revision context — cost-attribution audit-write seam landing

Per `.harness/Remaining_Work_Closure_Arc_Handoff_v1.md` §6 (operator-ratified Option 1; Phase D iteration-2 F2-02 absorption) + workspace `CLAUDE.md` §2.4 v2.x published-pairing constraint (paired with U-CP-72 implementation): the cost-attribution audit-write seam (U-OD-41 SpanCostRecord composer → cp_audit_to_od_audit converter via `cost:` action_id prefix → U-OD-00 audit-ledger ingestion) is the 8th typed seam at the §2.3.7 CP→OD bucket. The seam shares the `cp_audit_to_od_audit` converter at `harness-cxa/src/harness_cxa/cp_audit_conversion.py` with the 7 existing rows (1-7) per the established CXA shared-converter pattern; the `cost:` action_id prefix is the discriminator at the F2-entry layer.

**Timing context.** U-CP-72 implementation landed at commit `252b04f` per `[[fork-u-cp-72-cost-and-pause-resume-prefix-gap]]` memory with the `cost:` prefix branch **STRUCK** at landing per `[[halt-route-split-AC-pattern]]` discipline — the `cp_audit_to_od_audit` converter at HEAD does not yet route `cost:` because three CXA + OD-side prerequisites were outstanding: (i) CXA v2.9 row 8 publication (this amendment), (ii) OD-side CostRecordAuditPayload class authoring (owed at OD spec v1.9 → v1.10 sub-arc B sequel), (iii) U-OD-41 plan revision absorbing the routing target (owed at OD plan v2.16 → v2.17 sub-arc B sequel per OD plan v2.16 §0(d) operator preference (i) revise-signature noted at session checkpoint). v2.9 publishes (i) — the CXA-side amendment — alone. (ii) + (iii) remain the OD-side sub-arc B sequel routing.

### §0.2 Sections revised

§0 (this change note); §2.1 (aggregate 4×4 matrix — CP→OD bucket cell 7 → 8; aggregate total 99 → 100); §2.3.7 (CP→OD per-bucket enumeration — 7 → 8 rows; row 8 NEW); §2.4 (per-axis outbound posture summary — OD outbound 26 → 27, OD genuine 1 → 2; aggregate genuine 29 → 30; CP outbound + CP genuine unchanged per established v2.6 §2.4 canonical-namespace-ownership attribution convention; row 8 producer is OD-axis (U-OD-41) with OD-axis-owned `cost.*` namespace per harness-od/CLAUDE.md cost-attribution chain ownership). All other sections preserved verbatim from v2.8 (which preserved verbatim from v2.7 + v2.6).

### §0.3 §2.3.7 row 8 amendment (CP→OD bucket, U-OD-41 producer + cost: action_id prefix discriminator)

The v2.6 §2.3.7 7-row bucket enumeration (preserved verbatim through v2.7 + v2.8) is amended at v2.9 with one new row appended. Row 8 entry:

> **U-OD-41 (SpanCostRecord composer)** | **U-OD-00** | **OD spec v1.10 §C-OD-NN (CostRecordAuditPayload — owed at OD spec v1.9 → v1.10 sub-arc B sequel per OD plan v2.16 §0(d); forward-cite per v2.6 §0.5 forward-cite hygiene pattern)** | **G — `AuditLedgerEntry` as converter output type at cost-attribution audit-write; share `cp_audit_to_od_audit` converter via `cost:` action_id prefix discriminator (single converter, distinct audit-trail pattern at OD-side); 1-row audit shape includes `provider` + `model_id` + `usage_input_tokens` + `usage_output_tokens` + `usage_total_cost_usd` + `step_action_id` + `cumulative_cost_usd` (canonical fields per OD spec C-OD-12 + C-OD-13 cost attribution chain ownership; precise field enumeration pinned at OD spec v1.10 sub-arc B sequel). (NEW v2.9)**

**Bucket note amendment (preserved-with-extension).** The v2.6 bucket-note prose at §2.3.7 (preserved verbatim through v2.8) enumerates 7 action_id prefix discriminators per the §0.3 table (`dispatch:` / `hitl:` / `hitl_webhook:` / `operator_burden:` / `validator:` / `pause:` / `resume:` / `mcp_trust:`). v2.9 extends the discriminator enumeration to 8 by appending `cost:`. The §0.3 action_id-prefix discriminator table extension:

| Discriminator | Action_id pattern | Bucket row | Added |
|---|---|---|---|
| `cost:` | `cost:<workflow_id>:<step_action_id>` | **v2.9 §2.3.7 row 8** | v2.9 |

The discriminator is `cost:` (lowercase per existing 8-prefix convention). The pattern body `<workflow_id>:<step_action_id>` follows the established 2-segment pattern used by `pause:` + `resume:` rows (workflow-scoped + step-anchored); precise pattern body pinned at OD spec v1.10 sub-arc B sequel co-publication.

### §0.4 Aggregate matrix delta

**§2.1 4×4 adjacency matrix — REVISED (CP→OD bucket cell 7 → 8):**

| Source ↓ / Target → | IS | AS | CP | OD |
|---|---|---|---|---|
| **IS** | *(self)* | 0 | 0 | 0 |
| **AS** | 11 | *(self)* | 0 | 0 |
| **CP** | 37 | 18 | *(self)* | **8 (v2.9)** |
| **OD** | 4 | 10 | 12 | *(self)* |

**100 canonical cross-axis relationships** (99 at v2.8 + 1 new CP→OD genuine-typed-seam edge at v2.9). Genuine typed seams within that: **30** (29 at v2.8 + 1). Convention-level: **46** (unchanged). Phase-2-runtime: **24** (unchanged). 30 + 46 + 24 = 100.

**§2.4 per-axis outbound posture summary delta (preserved v2.6 namespace-ownership attribution convention):**

| Axis | v2.8 canonical outbound | v2.9 canonical outbound | v2.8 genuine | v2.9 genuine | Attribution rationale |
|---|---|---|---|---|---|
| IS | 0 | 0 | 0 | 0 | unchanged |
| AS | 11 | 11 | 7 | 7 | unchanged |
| CP | 62 | 62 | 21 | 21 | **unchanged — row 8 producer (U-OD-41) is OD-axis; row 8 namespace (`cost.*`) is OD-axis-owned per harness-od/CLAUDE.md cost-attribution chain (C-OD-12 + C-OD-13); per the established v2.6 §2.4 convention "canonical namespace ownership, not source-file location" determines attribution; row 8 attributes to OD outbound, not CP outbound** |
| OD | 26 | **27 (v2.9: +1 row 8 — cost-attribution seam)** | 1 | **2 (v2.9: +1 row 8)** | row 8 is the second OD-axis genuine outbound seam (alongside the existing 1 genuine at v2.6); both OD-axis-owned namespaces |
| **Aggregate** | **99** | **100 (v2.9: +1)** | **29** | **30 (v2.9: +1)** | — |

**Convention preserved-with-application note.** §2.4 attribution at the existing 7 CP→OD bucket rows (rows 1-7) is CP-axis per the v2.6 explicit convention: "they are CP-axis-attributed by virtue of their canonical namespace ownership, not by source-file location". Row 8 applies the SAME convention to a row with OD-axis namespace ownership — yielding OD-axis attribution. This produces a §2.1-vs-§2.4 attribution divergence (§2.1 counts row 8 under CP→OD bucket-membership = 8; §2.4 counts row 8 under OD outbound = 27 per axis-attribution). This divergence is the NATURAL CONSEQUENCE of the established v2.6 convention — not a new exception. The §2.3.7 bucket-membership classification is preserved per handoff §6 (operator-ratified Option 1 places row 8 at §2.3.7 by virtue of shared-converter anchoring at `cp_audit_to_od_audit`); §2.4 attribution preserves the v2.6 namespace-ownership rule per fidelity-core #5 "preserve what the fix does not touch".

### §0.5 Status posture

Proposed (v2.8) → **Proposed (v2.9)**. v2.9 is an additive amendment — one new row at §2.3.7 + aggregate matrix update + per-axis outbound posture update. No prior edge classification change; no prior edge spec-version cite change (preserves the v2.8 path-γ cite bumps verbatim); no acceptance criterion change at any prior row.

### §0.6 Forward-cite acknowledgement (per v2.6 §0.5 forward-cite hygiene)

Row 8 cites `OD spec v1.10 §C-OD-NN` as the OD canonical-schema target. OD spec v1.10 has NOT yet been published — the v2.9 cite is a forward-cite per the established v2.6 §0.5 forward-cite hygiene pattern ("Each new edge cites the owed OD spec ... section at the OD canonical schema column. These citations resolve byte-exact when ... lands ... amendments"). When OD spec v1.9 → v1.10 publishes the CostRecordAuditPayload §C-OD-NN (sub-arc B sequel per OD plan v2.16 §0(d)), the cite resolves; if the OD-side authoring pins a different section identifier than C-OD-NN, this v2.9 file requires a follow-on minor amendment (v2.9.1 or v2.10) updating the §2.3.7 row 8 cite cell. **No spec-extension at v2.9 — the forward-cite is bookkeeping for an owed downstream artifact, not a new H_T design commitment.**

### §0.7 Adjacent defects surfaced (not patched per FM-2 no-extension discipline)

(i) **U-CP-72 `cost:` branch STRUCK status preserved.** Per `[[fork-u-cp-72-cost-and-pause-resume-prefix-gap]]` memory: U-CP-72 implementation at commit `252b04f` STRUCK the `cost:` action_id prefix branch from the `cp_audit_to_od_audit` converter (the production converter at HEAD does not route `cost:` — it raises a TypeError fallback with a fork-doc pointer). v2.9 publishes the CXA-side commitment that row 8 is canonical at the bucket; the converter's actual runtime branch un-STRIKE is OWED at sub-arc B sequel (OD spec v1.10 CostRecordAuditPayload landing + U-CP-72 minor revision restoring the `cost:` branch with the routing target referencing the OD-side AuditPayload subclass). Surfaced; NOT patched at v2.9 per FM-2 no-extension (CXA scope is cross-axis composition contract; runtime converter body is CP-side implementation).

(ii) **OD spec v1.9 → v1.10 NEW §C-OD-NN CostRecordAuditPayload authoring owed.** Per OD plan v2.16 §0(d) sub-arc B sequel framing: OD spec v1.10 must author the CostRecordAuditPayload class extending the AuditPayload base with the cost-attribution shape (per OD CLAUDE.md C-OD-12 + C-OD-13 cost-attribution chain ownership). The §C-OD-NN section identifier is operator-discretion at OD-spec-writer scope. Surfaced; NOT patched at v2.9 per FM-2 (OD-spec-authoring scope is OD-side, not CXA-side).

(iii) **U-OD-41 plan revision owed.** Per OD plan v2.16 §0(d) sub-arc B sequel framing + "operator preference (i) revise-signature noted at session checkpoint": U-OD-41 plan-body Signatures line + ACs need amendment to consume the CostRecordAuditPayload routing target (currently U-OD-41 composes a raw SpanCostRecord without the typed AuditPayload subclass wrapping). Surfaced; NOT patched at v2.9 per FM-2 (OD-plan-authoring scope is implementation-planner revision-pass, not CXA-side).

(iv) **`harness-cxa/CLAUDE.md` + `harness-cp/CLAUDE.md` + `harness-od/CLAUDE.md` cross-axis-bucket count refresh owed.** Per existing v2.6 §0.5 downstream-absorption pattern: per-axis CLAUDE.md cross-axis bucket counts may need refresh (harness-cp/CLAUDE.md §2.3 CP→OD outbound 7 → 8; harness-od/CLAUDE.md §2.2 CP-bucket-inbound 7 → 8 + OD self-outbound +1). Surfaced; NOT patched at v2.9 per FM-2 (per-axis CLAUDE.md authoring scope is workspace governance pointer-update, not CXA file edit).

### §0.8 Downstream absorption owed (post-v2.9)

(a) Workspace `CLAUDE.md` §2.4 CXA row version bump (v2.8 → v2.9).
(b) Workspace `CLAUDE.md` §2.4 CXA row description amendment: cardinality bump (99 → 100 / 29 → 30) + cost-attribution row 8 status note (was "OWED" → now "LANDED at v2.9; OD-side sub-arc B sequel remains outstanding").
(c) Memory entry `[[fork-u-cp-72-cost-and-pause-resume-prefix-gap]]` description amendment: advance status from "OPEN / PARTIAL-RESOLVED at filing arc" to "PARTIALLY-RESOLVED via CXA v2.9 row 8 publication; cost: branch un-STRIKE remains owed at OD spec v1.10 + U-OD-41 plan revision (sub-arc B sequel)".
(d) Sub-arc B sequel (separately-authored): OD spec v1.9 → v1.10 NEW §C-OD-NN CostRecordAuditPayload + U-CP-72 minor revision restoring `cost:` branch + U-OD-41 plan revision (operator-discretion timing per operator preference (i) revise-signature at session checkpoint).
(e) `harness-cxa/CLAUDE.md` + `harness-cp/CLAUDE.md` §2.3 + `harness-od/CLAUDE.md` §2.2 bucket-count refresh per §0.7(iv) — operator-discretion timing.

---

## Filing footer

| Field | Value |
|---|---|
| Artifact | `Cross_Axis_Composition_Document_v2_9.md` |
| Version | v2.9 |
| Filing event | Cost-attribution audit-write seam row 8 publication per `.harness/Remaining_Work_Closure_Arc_Handoff_v1.md` §6 + workspace `CLAUDE.md` §2.4 v2.x amendment owe (operator-ratified Option 1; Phase D iteration-2 F2-02 absorption). Carried across batches 13/14/15/16/17 + CXA v2.7 + v2.8 narrow-scope publications that explicitly disclaimed cost-attribution. 2026-05-24 |
| Predecessor | `Cross_Axis_Composition_Document_v2_8.md` (preserved verbatim outside the §0 + §2.1 + §2.3.7 + §2.4 amendment sites enumerated at §0.2) |
| Successor | (none — current canonical) |
| Aggregate count | **100 canonical cross-axis relationships** (99 at v2.8 + 1 new G CP→OD bucket-membership at v2.9). **30 genuine typed seams** (29 at v2.8 + 1). Convention-level **46** preserved. Phase-2-runtime **24** preserved. 30 + 46 + 24 = 100. |
| CP→OD bucket | **8 canonical edges** (was 7 at v2.8 + 1 v2.9 row 8 cost-attribution audit-write seam). All 8 share the `cp_audit_to_od_audit` converter at `harness-cxa/src/harness_cxa/cp_audit_conversion.py` via convention; F2-action_id-prefix discriminator at OD audit-trace consumers (8 patterns per the §0.3 v2.9-extended discriminator table). |
| Per-axis attribution | CP outbound preserved 62 (no new CP-axis-owned namespace); OD outbound 26 → 27 (+1 OD-axis-owned `cost.*` namespace per harness-od/CLAUDE.md cost-attribution chain ownership); §2.1-vs-§2.4 attribution divergence is the NATURAL CONSEQUENCE of the established v2.6 namespace-ownership convention, not a new exception |
| Cost-attribution row 8 status | **LANDED at v2.9** (was STILL-OWED at v2.7/v2.8). OD-side sub-arc B sequel (CostRecordAuditPayload at OD spec v1.10 + U-CP-72 `cost:` branch un-STRIKE + U-OD-41 plan revision) remains the outstanding downstream gate per §0.7 + §0.8(d). |
| Operator authority | `.harness/Remaining_Work_Closure_Arc_Handoff_v1.md` §6 (operator-ratified Option 1; Phase D iteration-2 F2-02 absorption) + workspace `CLAUDE.md` §2.4 v2.x published-pairing constraint |
| Related forks | `[[fork-u-cp-72-cost-and-pause-resume-prefix-gap]]` (cost: branch STRIKE status preserved; un-STRIKE owed at sub-arc B sequel per §0.7(i)) |
| Related memory | `[[fork-u-cp-72-cost-and-pause-resume-prefix-gap]]` (advance status); `[[halt-route-split-AC-pattern]]` (catalogue at U-CP-72 STRIKE landing per fork doc); `[[h-t-cp-16-17-retire-ready-gate-runtime-composer-arcs]]` (CXA v2.9 publication completes one of the long-carried owes from batch-13 + batch-14 + batch-15 + batch-16 + batch-17 §6/§8/§6(e) carry-forward chain) |
| Date | 2026-05-24 |
