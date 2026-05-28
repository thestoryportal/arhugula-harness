# Cross-Axis Composition Document (v2.13)

*Delta over v2.12. v2.13 is a fidelity-pure citation-correction patch closing v2.12 §0.5 "Adjacent observations" finding (c) — `gen_ai.system` vs `gen_ai.provider.name` divergence at production — AND finding (d) — `_PROVIDER_OPERATIONS` non-§4.2-enum-conformance at production — both as **CLOSED-via-resolved-at-OD-spec-lineage** 2026-05-27. The v2.12 carry-text framings became stale at OD spec v1.17 production-rename commit `115387b` (closes (c)) and OD spec v1.18 production-conform commit `ca5674b` (closes (d)) — both commits landed 2026-05-26 / 2026-05-27, before v2.12 publication. The carries were inherited from CXA v2.11 + v2.10 without empirical re-verification per the v1.18 §5 / v1.21 / workflow v1.9 §7.4.7.3 discipline. v2.13 corrects at the canonical-reading layer. NO matrix change, NO new edge, NO per-axis attribution change. All v2.12 + v2.11 + v2.10 + v2.9 + v2.8 + v2.7 + v2.6 substantive content preserved verbatim by reference.*

## §0 Change note (v2.12 → v2.13)

### §0.1 Revision context — sweep-driven stale-carry closure

Per workflow v1.9 §7.4.7.3 audit across workspace carry-set sweep 2026-05-27 (operator-routed "run the sweep" arc post-workflow-v1.9 publication). The sweep enumerated 42 carries across 11 design-substrate/ artifacts; CXA v2.12 §0.5 (c) + (d) surfaced as STALE per species 3 (resolved-but-carry-stale-inherited) at workflow v1.9 §7.4.7.2. v2.13 closes both carries at the canonical-reading layer.

**Empirical verification of (c) closure.** OD spec v1.17 §1 canonical-reading amendment closed the `gen_ai.system` vs `gen_ai.provider.name` divergence at OD audit-ingestion semantics layer. Production-side rename at commit `115387b` (2026-05-26 19:40 -0600) renamed `gen_ai.system` → `gen_ai.provider.name` at `harness-runtime/src/harness_runtime/lifecycle/llm_dispatch.py:341` (now at line 350 post-Path-A) + NEW emission of `gen_ai.operation.name` at line 340 (now line 349) + preserved `gen_ai.request.model` at line 342 (now line 358). All 3 §C-OD-04 §4.3 Required (Stable) tier attributes emit on every GenAI span at production. The CXA v2.11/v2.12 carry framing "Unchanged at v2.12; separate apply-pass arc owed" is stale-as-described — the divergence WAS resolved at OD spec v1.17 lineage + production commit `115387b`, BEFORE v2.12 publication 2026-05-26.

**Empirical verification of (d) closure.** OD spec v1.18 §1.1 canonical-reading amendment closed the `_PROVIDER_OPERATIONS` value-space non-conformance. Production-side conform at commit `ca5674b` (2026-05-26 19:45 -0600) refactored `_PROVIDER_OPERATIONS` from `dict[str, str]` (API method-name string values) → `dict[str, GenAiOperation]` (canonical §C-OD-04 §4.2 enum members; all 3 providers map to `GenAiOperation.CHAT`). The CXA v2.11/v2.12 carry framing "Unchanged at v2.12; separate apply-pass arc owed" is stale-as-described — the divergence WAS resolved at OD spec v1.18 lineage + production commit `ca5674b`, BEFORE v2.12 publication 2026-05-26.

**Species classification.** Both (c) + (d) closures via species 3 (resolved-but-carry-stale-inherited) at workflow v1.9 §7.4.7.2 — defects flagged at vN ("Unchanged; separate apply-pass arc owed") got resolved at downstream code at commits `115387b` + `ca5674b` BEFORE the carry-text disposition was refreshed at any v2.11/v2.12/... delta arc. The CXA carry-text propagated verbatim across delta files because cross-artifact cite-cascade discipline at the OD spec closure arcs did NOT include CXA-side carry refresh.

**No fork doc filed.** Per workspace precedent for fidelity-pure citation-correction patches anchored at conclusive empirical state (OD spec v1.17 + v1.18 lineage IS canonical authority anchor; production state at HEAD verifies the closure). Workflow v1.9 §7.4.7.3 audit is the discipline that surfaced the stale carries; v2.13 is the apply-pass.

**Co-publication this session.** Sibling closure deltas at OD spec v1.22 + OD plan v2.22 + CP plan v2.24. Workspace `CLAUDE.md` §2.4 CXA row + §2.3 OD spec row + §2.4 OD plan row + §2.4 CP plan row co-bumped. ZERO matrix change; ZERO new edge; ZERO per-axis attribution change; ZERO contract change; ZERO behavior change.

### §0.2 Scope of v2.13 amendment

v2.13 is a **fidelity-pure citation-correction patch**, not a convention-declaration amendment or typed-edge amendment:

- **NEW §0.5.refresh sub-section** — closes (c) + (d) at the canonical-reading layer
- **Aggregate matrix at §2.1**: UNCHANGED (100 typed edges; 30 genuine; 24 phase-2-runtime — v2.12 cardinality preserved)
- **Per-axis attribution at §2.4**: UNCHANGED
- **§2.3.x per-bucket enumerations**: UNCHANGED
- **Convention-level sub-total at §2.1**: 48 (v2.12 cardinality preserved; no new convention seam at v2.13)

All other v2.12 + v2.11 + v2.10 + v2.9 + v2.8 + v2.7 + v2.6 substantive content preserved verbatim by reference.

### §0.3 Sections preserved verbatim at v2.13

- **§0.1** v2.12 revision context (AS §15.9 dual-attribute seam) — preserved verbatim
- **§0.2** v2.12 scope of amendment — preserved verbatim
- **§0.3** v2.12 convention-level vs typed-edge rationale — preserved verbatim
- **§0.4** v2.12 NEW spec-level seam declaration — preserved verbatim
- **§0.5 carries (a) + (b)** — preserved verbatim
- **§0.6** Status — preserved verbatim
- **§0.7** Downstream artifacts requiring absorption — preserved verbatim
- **§1 through §6** v2.6 baseline content preserved verbatim by reference

### §0.5.refresh (v2.13 NEW) — finding-closure-disposition refresh

| v2.12 carry | Closure event | Closure commit | Status at v2.13 |
|---|---|---|---|
| §0.5 (c) `gen_ai.system` vs `gen_ai.provider.name` divergence | OD spec v1.17 §1 canonical-reading amendment + production rename | `115387b` (2026-05-26 19:40) | **CLOSED-via-resolved-at-OD-v1.17** |
| §0.5 (d) `_PROVIDER_OPERATIONS` non-§4.2-enum-conformance | OD spec v1.18 §1.1 canonical-reading amendment + production conform | `ca5674b` (2026-05-26 19:45) | **CLOSED-via-resolved-at-OD-v1.18** |

Both carries removed from v2.13 §0.5 carry-set. v2.12 file body PRESERVED VERBATIM per delta-only-spec-file convention; v2.13 §0.5.refresh is the canonical-reading amendment for the disposition layer.

### §0.5.preserved (v2.13) — carries preserved verbatim from v2.12 §0.5

(a) **`mcp.*` namespace cross-emission on non-`mcp.tool.call` spans.** Carried verbatim from v2.12. Future operator-discretion arc MAY surface as namespace ownership ambiguity at §2.3.6 AS↔OD edge enumeration if discrimination becomes load-bearing for downstream runtime behavior. v2.13 does NOT touch this carry. GENUINE per sweep audit.

(b) **`schema_violation → policy_override` HIGH semantic stretch (AS §15.10 row 3).** Carried verbatim from v2.12. Future ADR-D2 / F4 enum revision arc owed; v2.13 does NOT touch the ADR-D2 reference frame per X-AL-3 + FM-2. GENUINE per sweep audit.

### §0.5.new (v2.13 NEW) — adjacent observations surfaced at v2.13

(e) **Cross-artifact cite-cascade discipline gap surfaced.** v2.12 (c) + (d) propagated verbatim across CXA v2.11 → v2.12 because OD spec v1.17 + v1.18 closure arcs did not include CXA-side carry refresh in their cross-artifact cite-cascade disposition tables. Workflow v1.9 §7.4.7.4 step 4 names "Cross-artifact cite-cascade disposition table" as the closure-shape mechanism; OD spec v1.17 §3 + v1.18 §3 cite-cascade tables enumerated downstream artifacts but did not extend to CXA's §0.5 carry-set refresh. Future closure-arc discipline candidate: when an OD spec closure cite-cascade enumerates downstream artifacts, include CXA §0.5 carry-set refresh as a candidate cascade target. Class 3 informational; NOT patched per FM-2 single-focus arc scope.

### §0.6 Status

**Closure shape**: fidelity-pure citation-correction patch under workflow v1.9 §7.4.7.4 amendment-arc closure shape. ZERO contract change; ZERO signature change; ZERO matrix change; ZERO per-axis attribution change; ZERO cross-axis cascade at runtime layer.

**Sweep cohort**: 1 of 4 closure deltas in 2026-05-27 sweep batch (siblings: OD spec v1.22, OD plan v2.22, CP plan v2.24).

### §0.7 Downstream artifacts requiring absorption

| Artifact | Required change | Owner |
|---|---|---|
| Workspace `CLAUDE.md` §2.4 CXA row | v2.12 → v2.13 row update with v2.13 change-note narrative; carry-set correction (c)+(d) removed | This session apply-pass arc |
| `harness-runtime/src/harness_runtime/lifecycle/llm_dispatch.py` | NO change owed — production state IS the closure-evidence | n/a |
| `harness-od/src/harness_od/otel_genai_base.py` | NO change owed — carrier consumed at production | n/a |
| Peer artifacts at design-substrate/ | NO change owed — no downstream artifact cites the closed carries | n/a |

### §0.8 Filing footer

| Field | Value |
|---|---|
| Version | v2.13 (Fidelity-pure citation-correction patch closing v2.12 §0.5 (c) `gen_ai.system` vs `gen_ai.provider.name` divergence + (d) `_PROVIDER_OPERATIONS` non-§4.2-enum-conformance — both as **CLOSED-via-resolved-at-OD-spec-lineage** 2026-05-27; NEW §0.5.refresh + §0.5.preserved + §0.5.new; v2.12 + earlier files PRESERVED VERBATIM) |
| Trigger | Workflow v1.9 §7.4.7.3 sweep audit 2026-05-27 (operator-routed "run the sweep") |
| Supersedes | v2.12 §0.5 (c) + (d) "Unchanged at v2.12; separate apply-pass arc owed" framings — superseded at v2.13 §0.5.refresh closure |
| Scope of revision | NARROW: §0.5 carry-set refresh only. ZERO matrix change; ZERO new edge; ZERO per-axis attribution change. |
| Cross-axis cascade | ZERO at runtime layer. Co-publication: workspace CLAUDE.md CXA row bump. |
| Authority anchor | OD spec v1.17 § (`gen_ai.system` divergence closure) + v1.18 § (`_PROVIDER_OPERATIONS` non-conformance closure) + production commits `115387b` + `ca5674b` |
| Predecessor | v2.12 (NEW §0.4 AS §15.9 ↔ OD §C-OD-05 row 10 spec-level seam) |
| Successor | v2.14 (next operator-discretion arc — candidates: v2.13 (a) mcp.* namespace cross-emission; (b) schema_violation → policy_override HIGH stretch; (e) cross-artifact cite-cascade discipline gap) |
| Sweep cohort | 2 of 4 closure deltas in 2026-05-27 sweep batch (siblings: OD spec v1.22 [authored], OD plan v2.22, CP plan v2.24) |
