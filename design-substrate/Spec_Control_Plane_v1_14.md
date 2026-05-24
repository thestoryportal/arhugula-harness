# Specification — Control Plane v1.14

## Change-note (v1.13 → v1.14)

**Scope of revision.** Narrow-scope citation-correction patch — amends the canonical reading of the v1.2-lineage §19.1 "C10 five-tier framework" narrative at 4 cite sites to align with `Spec_Action_Surface_v1.md` C-AS-10 §10.3 enumerating contract, which canonically declares **4 levels** (Level 0 refuse-remote / Level 1 signed-pinned / Level 2 sandbox-all / Level 3 allow-with-audit) — NOT 5. The drift was previously logged as a Class 3 informational item at CP plan v2.8 §0.6 (2026-05-21+, marked "Recorded for a future CP-spec doc-hygiene touch; no plan or code consequence"); v1.14 applies the doc-hygiene touch as FM-2 item (b) from the Reading B close checkpoint. ZERO contract change, ZERO signature change, ZERO field-set change, ZERO acceptance-criterion change, ZERO behavior change, ZERO cross-axis cascade.

**v1.13 substantive content preserved verbatim.** All v1.13 content (the §25 ValidatorFramework → §28 rename per Reading A apply pass) preserved unchanged. The v1.12 §25.2.1 9th-field `workflow_id` amendment preserved. The v1.11 §26.2 `WorkflowPauseReason` rename preserved. The v1.10 NEW §17.4/§26/§27/§28 (renamed) contracts preserved. The v1.6-lineage §25 / C-CP-25 WorkflowDriver contract preserved. The v1.2 §19 4-axis `_hitl_required` composition + `_hitl_required` semantic content preserved verbatim — only the narrative cardinality token "five-tier" is amended to "four-tier" at the 4 cite sites enumerated at §1 below.

**Source of fix.** CP plan v2.8 §0.6 Class 3 informational logging 2026-05-21+ ("CP spec §19.1 narrative 'C10 five-tier framework' vs `Spec_Action_Surface_v1.md` C-AS-10 §10.3 4-level enumeration — a narrative/enumeration count inconsistency. Non-blocking for v2.8 (`MCPTrustTier` factors out of AS §10.3, the enumerating contract). Recorded for a future CP-spec doc-hygiene touch; no plan or code consequence.") + Reading B close checkpoint FM-2 item (b) + operator AskUserQuestion 2026-05-24 selecting all 4 FM-2 items.

**Authority basis for fix direction.** The CP plan v2.8 §0.6 disposition explicitly identifies **AS §10.3 as the enumerating contract**, canonical for the value set. The CP plan v2.8 §2.0c U-CP-00c `MCPTrustTier` factor-out uses 4 values (`{ LEVEL_0_REFUSE_REMOTE, LEVEL_1_SIGNED_PINNED, LEVEL_2_SANDBOX_ALL, LEVEL_3_ALLOW_WITH_AUDIT }`) sourced from `Spec_Action_Surface_v1.md` C-AS-10 §10.3 verbatim. v1.14 amends the CP-spec-side narrative to match the enumerating contract; **the value set itself was always 4, never 5** — the "five-tier" narrative was a v1.2-era authoring drift at the CP-spec-side. The fix direction is therefore *narrative reconciliation to the canonical enumeration*, not a value-set change.

**One amendment site (4 cite cells).**

| Site | Amendment shape |
|---|---|
| **v1.2 §19.1 sites — "C10 five-tier framework" → "C10 four-tier framework per AS spec C-AS-10 §10.3 (Level 0 refuse-remote / Level 1 signed-pinned / Level 2 sandbox-all / Level 3 allow-with-audit)"** | The v1.2-lineage CP spec contains the phrase "C10 five-tier framework" at 4 cite sites within §19.1 + §21.3 context (per v1.2 line numbers 1014, 1627, 1667, 1888 — preserved verbatim through v1.3 → v1.13). The canonical reading at v1.14 amends "five-tier" → "four-tier" at these 4 sites + cites the enumerating contract AS spec C-AS-10 §10.3 for the value set. Sites enumerated: (i) v1.2 line 1014 — inline code-comment "`per_mcp_server_trust_floor(mcp_server),   // C10 five-tier framework per C-CP-19 §19.1`" → canonical-read as "`per_mcp_server_trust_floor(mcp_server),   // C10 four-tier framework per AS spec C-AS-10 §10.3`"; (ii) v1.2 line 1627 — inline code-comment "`per_mcp_server_trust_floor(server),   // C10 five-tier framework`" → canonical-read as "`per_mcp_server_trust_floor(server),   // C10 four-tier framework`"; (iii) v1.2 line 1667 — inline code-comment "`per_mcp_server_trust_floor(mcp_server),                 # C10 five-tier`" → canonical-read as "`per_mcp_server_trust_floor(mcp_server),                 # C10 four-tier`"; (iv) v1.2 line 1888 — §21.3 cross-trust-active row prose "`per C10 five-tier framework (Action Surface territory; \`Spec_Action_Surface_v1.md\` C-AS-10 §10.1)`" → canonical-read as "`per C10 four-tier framework (Action Surface territory; \`Spec_Action_Surface_v1.md\` C-AS-10 §10.3 — 4-level enumeration)`" (also corrects the §10.1 → §10.3 cross-cite shape since §10.3 is the enumerating sub-section, not §10.1). | CP plan v2.8 §0.6 + AS spec C-AS-10 §10.3 verbatim enumeration |

**Adjacent harmonization sites.** None — the amendment is at the value-set cardinality narrative only. The `_hitl_required` 4-axis composition body at v1.2 §19.1 is unchanged (the 4-axis count `per_tool_gate_level × per_mcp_server_trust_tier × persona_tier × blast_radius_tier` is a DIFFERENT count — number of axes in the `max()` composition, not number of values in the `MCPTrustTier` enum). The C-CP-19 §19.4 `_hitl_required` runtime evaluation surface unchanged. The C-CP-21 §21.3 cross-trust-active row body unchanged (only the `per C10 five-tier framework` cite cell within row is amended).

**Sections preserved verbatim from v1.13.** All v1.13 content + all v1.12 9th-field amendment + all v1.11 enum rename + all v1.10 NEW contracts + all v1.6-lineage WorkflowDriver + all v1.2-lineage §19 + §21 substantive contracts preserved unchanged outside the 4 cite cells enumerated above. The v1.10 spec file (`Spec_Control_Plane_v1_10.md`) is NOT edited at v1.14 — delta-only spec-chain preservation discipline preserved per v1.13 §1.3 verbatim-layer integrity precedent.

**Status posture.** Proposed (v1.13) → **Proposed (v1.14)**. v1.14 is a fidelity-pure citation-correction patch — single narrative cardinality amendment ("five-tier" → "four-tier") at 4 cite sites. NO v1.13 contract removed; NO v1.13 contract re-decomposition; NO new contract authored. Contract count unchanged at 27. Fail-class count unchanged. Signature change at any Protocol: none. Acceptance criterion change at any contract: none. Behavior change: none.

**Re-count.** v1.13 contract count: 27 contract surfaces / 28 contract IDs. v1.14 contract count: identical to v1.13 (27 / 28). `MCPTrustTier` enum cardinality at U-CP-00c carrier (CP plan v2.8 §2.0c): unchanged at 4 values. AS spec C-AS-10 §10.3 enumeration: unchanged at 4 levels. CP spec §19.1 narrative cardinality: 5 → 4 at canonical reading per v1.14.

**Downstream absorption owed (post-v1.14).**

(a) Workspace `CLAUDE.md` §2.3 CP spec row version bump (v1.13 → v1.14); co-published this arc.

(b) `harness-cp/CLAUDE.md` §1.3 MCP trust framework scope row narrative cardinality token refresh if present at `harness-cp/CLAUDE.md` (operator-discretion timing; per-axis bookkeeping not gating any retirement event).

(c) `harness-as/CLAUDE.md` — no change owed (AS §10.3 is the enumerating canonical and was always 4-level; the drift was CP-spec-side narrative only).

(d) CP plan v2.8 §0.6 Class 3 informational entry — status advance from "Recorded for a future CP-spec doc-hygiene touch; no plan or code consequence" → "RESOLVED at CP spec v1.14 §1 canonical-reading amendment 2026-05-24" (operator-discretion timing at next CP plan revision pass; not gating).

(e) Adjacent fork docs + Adversarial Reviews — no cite retag owed at v1.14 per fidelity-pure single-token narrative amendment (the "five-tier" token does not appear at any fork doc or adversarial review per empirical grep at v1.14 filing).

**Code retag (within-package import + class identifier).** ZERO code change owed by this v1.14 amendment. The Python `MCPTrustTier` enum at `harness-cp/src/harness_cp/u_cp_00c_shared_types.py` (or wherever U-CP-00c carrier landed) already declares 4 members per CP plan v2.8 §2.0c authoring — the canonical 4-value enumeration was already in code at landing time; the narrative-cardinality fix at v1.14 closes the spec-side mismatch retroactively.

**Adjacent defects surfaced (NOT patched per FM-2 no-extension discipline).**

(i) **v1.2 §19.1 narrative "C10" prefix usage.** The "C10" prefix at the 4 cite sites is a v1.2-era shorthand for "Cluster 10" (a Phase-3 architectural-cluster reference) per the v1.2-era cluster-cite convention. Within v1.13 + v1.14 the C10 prefix is preserved verbatim — the v1.14 canonical-reading amendment only touches the cardinality token ("five-tier" → "four-tier"), NOT the C10 prefix. Future v1.x revision MAY normalize the "C10" prefix to a more readable cite shape (e.g., "MCP server trust framework per AS §10.3") IF a doc-hygiene arc opens; not done at v1.14 per fidelity-pure scope discipline.

(ii) **v1.2 §21.3 cross-trust-active row §10.1 → §10.3 cite-cell correction.** The v1.2 line 1888 row prose cites "C-AS-10 §10.1" but the canonical enumerating sub-section is C-AS-10 §10.3 (§10.1 carries the per-transport sandbox-tier table; §10.3 carries the trust-tier framework enumeration). The v1.14 canonical-read at site (iv) above incorporates the §10.1 → §10.3 cite-shape correction as a bundled fix with the "five-tier" → "four-tier" amendment per the same cell scope. This is technically an additive correction (cardinality drift + cite-shape drift) but is bundled per the same cite-cell amendment site — recorded here for adjacent-defect transparency.

(iii) **Other CP-spec-files "five-tier" carry.** Empirical grep at v1.14 filing across `Spec_Control_Plane_v1_3.md` through `Spec_Control_Plane_v1_13.md` confirms the "five-tier" phrase appears ONLY at v1.2 (the substantive carrier). All v1.3 → v1.13 files are delta-only files; none carry the phrase. The v1.14 canonical-reading amendment is therefore localized to v1.2's 4 cite sites at the canonical-reading layer; no further file-chain cite retag owed.

(iv) **AS spec C-AS-10 §10.2 "Floor input" row + §10.3 4-level enumeration internal coherence.** The AS spec C-AS-10 §10 contract body (preserved verbatim through AS spec v1.4 → v1.5) declares §10.3 trust-tier framework as 4 levels canonically. ZERO drift at AS-spec-side. Surfaced; NO patch owed (AS spec is canonical).

---

## §1 — v1.2 §19.1 + §21.3 4-site canonical-reading amendment

The v1.2 file CP spec contains 4 cite sites where the narrative cardinality "C10 five-tier framework" should canonically read "C10 four-tier framework per AS spec C-AS-10 §10.3" per CP plan v2.8 §0.6 Class 3 informational logging. v1.14 publishes the canonical-reading amendment at these 4 sites without editing v1.2 in-place per delta-only spec-chain preservation discipline.

### §1.1 Per-site canonical-reading table

| v1.2 site | v1.2 verbatim text (preserved at file layer) | v1.14 canonical reading (at consumer layer) | Site context |
|---|---|---|---|
| v1.2 line 1014 | `per_mcp_server_trust_floor(mcp_server),   // C10 five-tier framework per C-CP-19 §19.1` | `per_mcp_server_trust_floor(mcp_server),   // C10 four-tier framework per AS spec C-AS-10 §10.3` | C-CP-19 §19.1 `_hitl_required` 4-axis `max()` composition code-block — inline floor-function comment |
| v1.2 line 1627 | `per_mcp_server_trust_floor(server),   // C10 five-tier framework` | `per_mcp_server_trust_floor(server),   // C10 four-tier framework` | C-CP-19 §19.1 alternate code-block (different presentation) — inline floor-function comment |
| v1.2 line 1667 | `per_mcp_server_trust_floor(mcp_server),                 # C10 five-tier` | `per_mcp_server_trust_floor(mcp_server),                 # C10 four-tier` | C-CP-19 §19.1 Python-syntax code-block (`#` comment) — inline floor-function comment |
| v1.2 line 1888 | `Untrusted-MCP active \| Current tool dispatches against an MCP server with `per_mcp_server_trust_floor` ≥ `untrusted-floor` per C10 five-tier framework (Action Surface territory; `Spec_Action_Surface_v1.md` C-AS-10 §10.1)` | `Untrusted-MCP active \| Current tool dispatches against an MCP server with `per_mcp_server_trust_floor` ≥ `untrusted-floor` per C10 four-tier framework (Action Surface territory; `Spec_Action_Surface_v1.md` C-AS-10 §10.3 — 4-level enumeration)` | C-CP-21 §21.3 cross-trust-boundary palette restriction trigger-table row — bundled cardinality fix + §10.1 → §10.3 cite-shape correction per §0 adjacent-defect (ii) |

### §1.2 Authority basis at each site

All 4 sites cite the same authority chain:

1. **AS spec C-AS-10 §10.3** — canonical enumeration of the trust-tier framework: 4 levels (Level 0 refuse-remote / Level 1 signed-pinned / Level 2 sandbox-all / Level 3 allow-with-audit). Preserved verbatim through AS spec v1.4 → v1.5.

2. **CP plan v2.8 §2.0c U-CP-00c `MCPTrustTier` carrier** — concrete factor-out at the CP-axis as a 4-value enum: `{ LEVEL_0_REFUSE_REMOTE, LEVEL_1_SIGNED_PINNED, LEVEL_2_SANDBOX_ALL, LEVEL_3_ALLOW_WITH_AUDIT }`. Sources from AS §10.3 verbatim.

3. **CP plan v2.8 §0.6 Class 3 informational logging** — explicit drift identification + canonical disposition ("AS §10.3 is the enumerating contract"). The v1.14 amendment is the implementation of the v2.8 §0.6 doc-hygiene-touch recommendation.

### §1.3 Verbatim-layer integrity

The v1.2 spec file (`Spec_Control_Plane_v1_2.md`) is itself NOT edited at v1.14 — the delta-only spec-chain preservation discipline keeps v1.2 byte-exact at its filing footer. Consumers reading the delta chain interpret the v1.2 lines 1014/1627/1667/1888 AS canonically amended per §1.1 above at v1.14. This pattern is parallel to the v1.13 §1.3 verbatim-layer-integrity precedent for the §25 → §28 rename.

### §1.4 Cite-cascade scope

ZERO cite-cascade required across downstream artifacts. The cardinality narrative "C10 five-tier framework" appears ONLY at v1.2's 4 sites — empirical grep at v1.14 filing across:
- All `Spec_Control_Plane_v1_*.md` files (delta-only files v1.3 → v1.13: 0 hits)
- All `Implementation_Plan_Control_Plane_v2_*.md` files: 0 hits (plan files use the correct 4-value enum throughout)
- All `Spec_Action_Surface_v1*.md` files: 0 hits (AS-side was always correct)
- All `Spec_Operational_Discipline_*.md` files: 0 hits at the C10-cardinality context
- All `Spec_Harness_Runtime_v1.md`: 0 hits at the C10-cardinality context
- All `Cross_Axis_Composition_Document_v2_*.md` files: 0 hits
- All `harness-{is,as,cp,od,cxa,core,runtime}/CLAUDE.md`: 0 hits at the C10-cardinality context

The drift is isolated to v1.2 §19.1 + §21.3 4 cite sites. v1.14 publishes the canonical-reading amendment localized to these sites.

---

## §2 — Preservation guarantees

| Element | Disposition |
|---|---|
| v1.13 §28 ValidatorFramework rename | Preserved verbatim |
| v1.12 §25.2.1 9th-field `workflow_id` amendment | Preserved verbatim |
| v1.11 §26.2 `WorkflowPauseReason` rename + §26 coexistence NOTE | Preserved verbatim |
| v1.10 NEW §17.4 + §26 + §27 + §28 (renamed) contracts | Preserved verbatim |
| v1.6-lineage §25 / C-CP-25 WorkflowDriver | Preserved verbatim |
| v1.2 §19 `_hitl_required` 4-axis `max()` composition body | Preserved verbatim outside the 4 cite cells at §1.1 |
| v1.2 §21 cross-trust-boundary palette restriction body | Preserved verbatim outside the 1 cite cell at §1.1 row 4 |
| All v1.2-lineage substantive contracts (C-CP-01 through C-CP-24) | Preserved verbatim |
| AS spec C-AS-10 §10.3 4-level enumeration | Unchanged at AS-spec-side (canonical from v1.0; v1.14 amendment is CP-spec-side narrative-token reconciliation only) |
| CP plan v2.8 §2.0c U-CP-00c `MCPTrustTier` 4-value carrier | Unchanged at plan-side (carrier was always 4-value per AS §10.3 factor-out) |
| All ADR commitments (F1–F5 + D1–D6) | Unchanged |
| Decision 2.D3 + all other v1.x decisions | Preserved verbatim |

---

## Filing footer

| Field | Value |
|---|---|
| Artifact | `Spec_Control_Plane_v1_14.md` |
| Version | v1.14 |
| Filing event | FM-2 item (b) from Reading B close checkpoint absorption — `MCP_TRUST` cardinality drift CP-axis narrative reconciliation per CP plan v2.8 §0.6 Class 3 informational doc-hygiene-touch recommendation 2026-05-24 |
| Predecessor | `Spec_Control_Plane_v1_13.md` (v1.13 substantive content preserved verbatim; v1.14 is canonical-reading amendment at v1.2 4 cite sites only) |
| Successor | (none — current canonical) |
| Co-published artifacts (this arc) | Workspace `CLAUDE.md` §2.3 CP row bump v1.13 → v1.14 |
| Downstream absorption owed (next arcs) | `harness-cp/CLAUDE.md` §1.3 MCP trust framework scope row narrative cardinality refresh (operator-discretion); CP plan v2.8 §0.6 Class 3 entry status advance to RESOLVED (operator-discretion at next CP plan touch); CXA + adjacent fork docs + adversarial reviews — empirically-grep confirmed ZERO retag owed |
| Operator authority | AskUserQuestion 2026-05-24 selecting all 4 FM-2 items from Reading B close checkpoint; CP plan v2.8 §0.6 Class 3 disposition (AS §10.3 canonical, CP narrative drift to be reconciled at future CP-spec doc-hygiene touch) |
| Contract-count change | None |
| Fail-class-count change | None |
| Signature change at any Protocol | None |
| Field-set change at any field set | None |
| Acceptance criterion change at any contract | None |
| Behavior change | None |
| Cross-axis cascade | ZERO (AS spec C-AS-10 §10.3 canonical 4-level enumeration is unchanged; CP plan v2.8 §2.0c U-CP-00c 4-value carrier is unchanged; the amendment is CP-spec-side narrative-token reconciliation only) |
| Skill discipline | `spec-writer` Phase-7 spec-fix application of operator-ratified FM-2 item (b); fidelity-pure citation-correction patch; NO contract change; NO extension; preservation audit PASSED |
| Date | 2026-05-24 |
