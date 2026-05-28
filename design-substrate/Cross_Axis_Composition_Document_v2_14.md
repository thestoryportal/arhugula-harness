# Cross-Axis Composition Document (v2.14)

*Delta over v2.13. v2.14 is a fidelity-pure citation-correction patch closing v2.13 §0.5.preserved finding (b) — `schema_violation → policy_override` HIGH semantic stretch (AS §15.10 row 3) — as **CLOSED-as-fork-doc-Reading-B-by-design** 2026-05-27. The v2.13 carry-text suggested "Future ADR-D2 / F4 enum revision arc owed" but the originating fork (`class_1_fork_as_4_f4_enum_taxonomy_mismatch_and_production_bug.md` §3.1) explicitly REJECTED that revision shape (Reading A — adding MCP-shape values to F4 enum) because it "degrades semantic coherence by mixing two abstraction layers in one enum." Operator-ratified Reading B (sibling MCP-shape enum at AS §15.8 + dual-attribute emission at §15.9 + projection-with-acknowledged-stretch at §15.10) is the canonical end-state; the HIGH stretch at §15.10 row 3 is the deliberate by-design artifact of Reading B's "preserve F4 process-shape coherence" framing, NOT a deferred clean-up. v2.14 corrects the carry-text disposition at the canonical-reading layer. NO matrix change, NO new edge, NO per-axis attribution change. All v2.13 + earlier substantive content preserved verbatim by reference.*

## §0 Change note (v2.13 → v2.14)

### §0.1 Revision context — sub-species 3.carry-suggests-foreclosed-reading

Per workflow v1.9 §7.4.7.3 audit at v2.14 amendment-arc opening 2026-05-27 (operator-routed CXA (b) closure arc post-OD-spec v1.24 push at `4e79db8`). Pre-substantive empirical-verification at the originating fork doc identified that v2.13 (b)'s suggestion ("Future ADR-D2 / F4 enum revision arc owed") references a revision shape explicitly REJECTED at the fork doc's own §4 Recommendation. The carry-text appears to have been authored at v2.13 (and at v2.12 inheritance prior) without re-reading the fork doc — specifically the §3.1 Reading A rejection rationale + §4 Reading B ratification as the canonical end-state.

**Sub-species classification.** This is a NEW sub-species of species 3 (resolved-but-carry-stale-inherited) at workflow v1.9 §7.4.7.2 — **3.carry-suggests-foreclosed-reading**: the carry-text remains structurally well-formed (the divergence at §15.10 row 3 IS still present), but the carry's forward-looking suggestion references a revision shape that was foreclosed at the originating fork doc. The carry is not stale-as-described in the prior species 3 sense (where production resolved the defect at downstream code); rather the carry's *suggested resolution path* is foreclosed-as-described while the underlying surface is preserved by-design.

**Distinct from prior sub-species:**
- 3.code-resolution: resolution at production commit (e.g., CXA v2.13 (c)+(d) closures)
- 3.fork-doc-closure: resolution at operator-ratified fork doc disposition (e.g., U-RT-58 patterns)
- 3.workflow-grammar: resolution at upstream workflow-doc canonicalization (e.g., OD spec v1.22 (d)+(i))
- 3.empirical-verification-of-external-authority: resolution at WebFetch against archived external spec (e.g., OD spec v1.23 (e))
- 3.same-session-immediate-sequel: resolution at same-session sequel arc (e.g., OD spec v1.24 (f))
- **3.carry-suggests-foreclosed-reading (NEW at v2.14): resolution at empirical-verification-at-originating-fork-doc that the carry's suggested revision shape is structurally foreclosed by prior operator ratification + the underlying surface is canonical end-state by-design.**

The sub-species set at species 3 now SIX. Workflow v1.9 §7.4.7.2 "Sub-species" column extension candidate strengthens further.

### §0.2 Empirical verification of (b) closure

**Fork doc reference.** `.harness/class_1_fork_as_4_f4_enum_taxonomy_mismatch_and_production_bug.md` (filed 2026-05-25; status: APPLIED 2026-05-26 / Reading B arc 2 landed; AS spec v1.6 → v1.7 + AS plan v1.4 + harness-as v1.4 + harness-runtime dispatcher fix + 22 new tests + retirement batch-19 H_T-AS-4 PARTIAL → RETIRED).

**§3.1 Reading A — Extend F4 enum (REJECTED).** *"Cons: F4 enum doubles in cardinality + mixes process-shape with MCP-shape values; semantic coherence degrades."* The carry-text suggestion "future spec revision MAY add a F4 `contract_violation` value to absorb this projection cleanly" is the same architectural shape as Reading A — adding a value to F4's process-execution-shape enum that originates at a different abstraction layer (contract / I-O schema). Reading A was rejected; therefore the carry's suggested revision shape is foreclosed.

**§3.2 Reading B — sibling MCP-shape enum (RATIFIED + APPLIED).** *"Optional: §15.6 mapping table from MCP-shape to F4-shape (best-effort projection where applicable)."* The mapping table was added as §15.10 with explicit per-row semantic-stretch column. Row 3 (`schema_violation → policy_override`) carries the HIGH stretch acknowledgement as the deliberate by-design artifact: Reading B's "preserve F4 process-shape coherence" framing is precisely what makes the row-3 projection HIGH-stretch rather than 1:1. The stretch IS the architectural design choice.

**Production state at HEAD `4e79db8`.** Both `mcp.fail.class=schema_violation` AND `sandbox.fail.class=policy_override` emit on the `sandbox.violation` child span per §15.9 dual-attribute discipline. Consumers wanting unambiguous MCP-shape read `mcp.fail.class` directly; consumers wanting F4-shape read `sandbox.fail.class` (projected best-effort per §15.10). The HIGH stretch is invisible to consumers reading `mcp.fail.class`; it is the documented best-effort projection cost at the F4-shape consumer.

**No new emission gap, no behavior change, no contract change.** v2.14 closure is documentation-canonicalization at the carry-text disposition layer.

### §0.3 Scope of v2.14 amendment

v2.14 is a **fidelity-pure citation-correction patch**, same shape as v2.13:

- **NEW §0.5.refresh sub-section** — closes (b) at the canonical-reading layer; preserves (a) + (e) verbatim
- **Aggregate matrix at §2.1**: UNCHANGED (100 typed edges; 30 genuine; 24 phase-2-runtime — v2.13 cardinality preserved)
- **Per-axis attribution at §2.4**: UNCHANGED
- **§2.3.x per-bucket enumerations**: UNCHANGED
- **Convention-level sub-total at §2.1**: 48 (v2.13 cardinality preserved; no new convention seam at v2.14)

All other v2.13 + v2.12 + v2.11 + earlier substantive content preserved verbatim by reference.

### §0.4 Sections preserved verbatim at v2.14

- **§0.1 through §0.4** v2.13 revision context + scope + sections-preserved + filing — preserved verbatim
- **§0.5 v2.13 (a) + (e) carries** — preserved verbatim at v2.14 §0.5.preserved
- **§0.5.refresh + §0.5.preserved + §0.5.new (v2.13)** — refreshed at v2.14 §0.5.refresh-2 + §0.5.preserved-2 + §0.5.new-2 below
- **§1 through §6** v2.6 baseline content preserved verbatim by reference

### §0.5.refresh-2 (v2.14 NEW) — finding-closure-disposition refresh

| v2.13 carry | Closure event | Closure commit | Status at v2.14 |
|---|---|---|---|
| §0.5.preserved (b) `schema_violation → policy_override` HIGH semantic stretch | Empirical verification at `class_1_fork_as_4_f4_enum_taxonomy_mismatch_and_production_bug.md` §3.1 (Reading A rejected) + §4 (Reading B operator-ratified as canonical end-state) + §15.10 row 3 HIGH stretch as deliberate by-design artifact of Reading B's "preserve F4 process-shape coherence" framing | Fork-doc applied 2026-05-26; v2.14 amendment-arc this session | **CLOSED-as-fork-doc-Reading-B-by-design** |

Carry removed from v2.14 §0.5 carry-set. v2.13 file body PRESERVED VERBATIM per delta-only-spec-file convention; v2.14 §0.5.refresh-2 is the canonical-reading amendment for the disposition layer.

### §0.5.preserved-2 (v2.14) — carries preserved verbatim from v2.13 §0.5

(a) **`mcp.*` namespace cross-emission on non-`mcp.tool.call` spans.** Carried verbatim from v2.13 → v2.12. Future operator-discretion arc MAY surface as namespace ownership ambiguity at §2.3.6 AS↔OD edge enumeration if discrimination becomes load-bearing for downstream runtime behavior. v2.14 does NOT touch this carry. GENUINE per sweep audit at v2.14 amendment-arc opening (empirically re-verified at HEAD `4e79db8`: OD spec v1.14 §C-OD-08 §8.4 parent-span-class primacy rule canonicalizes the ingestion routing; CXA-side edge enumeration extension is the open question — still deferred-monitor).

(e) **Cross-artifact cite-cascade discipline gap surfaced.** Carried verbatim from v2.13. When OD spec closure arcs enumerate cascade targets, they have NOT historically included CXA §0.5 carry-set as a target. Class 3 informational; future closure-arc discipline candidate. v2.14 does NOT patch the upstream OD spec closure-arc-discipline convention. NOT a new fork; carry strengthens with each subsequent OD spec closure arc that does not include CXA §0.5 carry refresh — v1.23 + v1.24 closure arcs this session did not (and per FM-2 single-focus scope at those arcs, were not expected to). Empirical evidence accumulates that a workflow-doc revision candidate at §7.4.7.4 step 4 "Cross-artifact cite-cascade disposition table" template MAY be warranted to canonicalize CXA §0.5 inclusion. Class 3 informational; NOT patched per FM-2 single-focus arc scope at v2.14.

### §0.5.new-2 (v2.14 NEW) — adjacent observations surfaced at v2.14

(h) **NEW at v2.14 — sub-species 3.carry-suggests-foreclosed-reading catalogued.** v2.13 (b)'s suggestion "future spec revision MAY add a F4 `contract_violation` value to absorb this projection cleanly" references a revision shape (additive at F4 §4.1 process-execution-shape enum) that was REJECTED at the originating fork doc §3.1 Reading A on semantic-coherence grounds. The carry remained well-formed because the underlying surface (HIGH stretch at §15.10 row 3) is preserved by Reading B's by-design end-state — but the carry's *suggested resolution path* is foreclosed. Pattern catalogued at v2.14 §0.1: pre-substantive empirical-verification at originating fork doc is the discipline that catches this sub-species. Distinct from species 3.code-resolution + 3.fork-doc-closure + 3.workflow-grammar + 3.empirical-verification-of-external-authority + 3.same-session-immediate-sequel. Sub-species set at species 3 now SIX. Future workflow-doc revision MAY catalogue the refinement at §7.4.7.2 "Sub-species" column extension per v1.23 finding (g) + v1.24 finding (g) candidate (cardinality now 6 sub-species in 4 consecutive arcs is stronger empirical evidence). Class 3 informational; NOT patched per FM-2 single-focus arc scope at v2.14.

(i) **NEW at v2.14 — Reading B end-state preservation discipline.** Reading B at the originating fork is the canonical end-state. The HIGH stretch at §15.10 row 3 is the deliberate by-design artifact of Reading B's "preserve F4 process-shape coherence" framing — NOT a deferred clean-up. Future operator-discretion arcs at the §15.10 projection table layer SHOULD route through Option C of the v2.14 closure stance question (NEW audit-correlate sub-enum at F4 as sibling to process-execution enum) NOT Option A (re-extending F4 — foreclosed). Documentation discipline candidate: when carry-text suggests a resolution path, cite the originating fork doc + verify the suggestion's shape against the fork doc's §4 Recommendation before propagating across delta versions. Class 3 informational; NOT patched per FM-2 single-focus arc scope at v2.14.

### §0.6 Status

**Closure shape**: fidelity-pure citation-correction patch under workflow v1.9 §7.4.7.4 amendment-arc closure shape. ZERO contract change; ZERO signature change; ZERO matrix change; ZERO per-axis attribution change; ZERO cross-axis cascade at runtime layer. ZERO production-code change.

**No fork doc filed.** Per workspace precedent for fidelity-pure citation-correction patches anchored at conclusive empirical state (fork doc `class_1_fork_as_4_f4_enum_taxonomy_mismatch_and_production_bug.md` IS canonical authority anchor; Reading B applied 2026-05-26 IS canonical end-state).

### §0.7 Downstream artifacts requiring absorption

| Artifact | Required change | Owner |
|---|---|---|
| Workspace `CLAUDE.md` §2.4 CXA row | v2.13 → v2.14 row update with v2.14 change-note narrative; carry-set correction (b) removed | This session apply-pass arc |
| `class_1_fork_as_4_f4_enum_taxonomy_mismatch_and_production_bug.md` | NO change owed — fork doc IS canonical authority for the closure; Reading B applied status preserved | n/a |
| `Spec_Action_Surface_v1_7.md` §15.8 / §15.9 / §15.10 | NO change owed — Reading B end-state preserved verbatim; HIGH stretch at row 3 IS the by-design artifact | n/a |
| `harness-as/` + `harness-runtime/` production carriers | NO change owed — production state at HEAD `4e79db8` IS the closure-evidence (dual-attribute emission per §15.9; projection applied per §15.10) | n/a |
| Peer artifacts at design-substrate/ | NO change owed — no downstream artifact cites the closed carry's "future ADR-D2 / F4 revision" suggestion at canonical-reading sites | n/a |

### §0.8 Filing footer

| Field | Value |
|---|---|
| Version | v2.14 (Fidelity-pure citation-correction patch closing v2.13 §0.5.preserved (b) `schema_violation → policy_override` HIGH semantic stretch — as **CLOSED-as-fork-doc-Reading-B-by-design** 2026-05-27; NEW §0.5.refresh-2 + §0.5.preserved-2 + §0.5.new-2; v2.13 + earlier files PRESERVED VERBATIM) |
| Trigger | Operator-routed CXA (b) closure arc 2026-05-27 post-OD-spec v1.24 push (`4e79db8`); pre-substantive empirical-verification at originating fork doc surfaced foreclosed-reading sub-species |
| Supersedes | v2.13 §0.5.preserved (b) "Future ADR-D2 / F4 enum revision arc owed" framing — superseded at v2.14 §0.5.refresh-2 closure as **fork-doc-Reading-B-by-design** |
| Scope of revision | NARROW: §0.5 carry-set refresh only. ZERO matrix change; ZERO new edge; ZERO per-axis attribution change; ZERO production-code change. |
| Cross-axis cascade | ZERO at runtime layer. Co-publication: workspace CLAUDE.md CXA row bump. |
| Authority anchor | `.harness/class_1_fork_as_4_f4_enum_taxonomy_mismatch_and_production_bug.md` §3.1 Reading A rejection + §4 Reading B operator-ratification + Reading B arc 2 APPLIED 2026-05-26 |
| Predecessor | v2.13 (Fidelity-pure citation-correction patch closing v2.12 (c) + (d) gen_ai.system + _PROVIDER_OPERATIONS divergences via OD spec v1.17 + v1.18 closure lineage) |
| Successor | v2.15 (next operator-discretion arc — candidates: v2.14 (a) mcp.* namespace cross-emission still deferred-monitor; (e) cross-artifact cite-cascade discipline gap accumulating empirical evidence; (h) sub-species 3.carry-suggests-foreclosed-reading workflow-doc catalogue refinement; (i) Reading B end-state preservation discipline workflow-doc catalogue refinement) |
| Audit lineage | v2.13 (b) carried verbatim from v2.12 → v2.13 awaiting operator-discretion stance routing. Routed 2026-05-27 (this session, stance: refresh-carry-text-only per AskUserQuestion after advisor-flagged that the carry's suggested resolution path was foreclosed by the originating fork doc's §3.1 Reading A rejection). |
