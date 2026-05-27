# Project Workflow — v1.9 (delta over v1.8)

---

## Change-note (v1.8 → v1.9)

**Scope of revision.** Narrow-scope discipline strengthening at §7.4 fidelity-grammar — NEW §7.4.7 sub-section canonicalizing **stale-carry-text disposition discipline** at "Adjacent observations" carry sites in delta-only spec-file authoring. Encodes the 5-species catalogue surfaced empirically at OD spec v1.15 / v1.16 / v1.17 / v1.18 / v1.21 fidelity-pure citation-correction patches (5 closures across the lineage 2026-05-26 → 2026-05-27) + the v1.18 §5 / v1.21 strengthened discipline ("re-verify inherited carries against production state AT THE TIME OF EACH NEW AMENDMENT, not only at the time of the originating arc"). §1–§8.6 PRESERVED VERBATIM per workflow-doc revision convention (delta-only authoring path adopted for narrow revisions; sets precedent matching the spec-file delta-only convention already operative in this workspace at OD spec v1.15+ / CP spec v1.13+ / runtime spec v1.16+).

**Trigger.** User-routed "next highest-value arc" 2026-05-27 selecting workflow-grammar discipline strengthening as the meta-fix preventing future stale-carry recurrence. Empirical-motivation: 5 fidelity-pure citation-correction patches landed at OD spec lineage 2026-05-26 → 2026-05-27 (v1.15 phantom-as-described; v1.17 resolved-but-carry-stale-inherited; v1.18 authoring-time stale carry; v1.20 (subsuming finding (d) deferred audit); v1.21 post-authoring stale carry) — each closing carry-text-disposition defects that the upstream workflow discipline did NOT name. v1.9 §7.4.7 closes the discipline-gap vector at the upstream artifact.

**Authority anchor.** OD spec v1.15 §3 origin-of-drift documentation + v1.16 §3 reconciliation-pass-tiebreaker-check precedent + v1.17 §5 pattern catalogue (THIRD species) + v1.18 §5 pattern catalogue (FOURTH species + STRENGTHENED discipline) + v1.21 §"Change-note" final paragraph (FIFTH species + further-strengthened discipline). The 5 catalogued species + the strengthened discipline are abstracted at v1.9 §7.4.7 as workflow-grammar rules applicable across all delta-only spec-file authoring (NOT only OD spec).

**Scope of revision.** ADDITIVE-only at §7.4. §1–§7.3 + §7.4.1–§7.4.6 + §8 PRESERVED VERBATIM. NEW §7.4.7 sub-section authored. NO change to fidelity-claim taxonomy (§7.4.1), byte-exact grammar (§7.4.2), structural-fidelity grammar (§7.4.3), citation-only grammar (§7.4.4), sub-section-resolution discipline (§7.4.5), or pre-emission audit gate (§7.4.6).

**Routing.** Narrow-scope workflow-doc revision per §7.1 v1.x criteria (clarifications / minor structural updates / new sub-section addition without changing existing structure). Delta-only file authoring (NEW workspace precedent for narrow workflow-doc revisions); v1.8 PRESERVED VERBATIM as historical anchor. No fork doc filed (fidelity-pure discipline-strengthening anchored at empirical lineage; routing decision made at "next highest-value arc" framing). Workspace `CLAUDE.md` §2.1 governance row co-published.

**No fork doc filed.** Per workspace precedent for narrow workflow-doc additions anchored at empirical lineage (v1.7 fidelity-grammar authoring at Path δ; v1.8 §4.1.4.6 cascade-closure substrate-driven extension). The 5 empirical closures at OD spec v1.15..v1.21 ARE the canonical authority anchor for §7.4.7; no separate fork doc needed.

---

## §1 NEW sub-section authoring at §7.4

### §7.4.7 Stale-carry-text disposition discipline

*Added in workflow v1.9 (2026-05-27) per empirical lineage at OD spec v1.15 / v1.16 / v1.17 / v1.18 / v1.21 fidelity-pure citation-correction patches. Encodes 5 species of stale-carry-text disposition + strengthened discipline candidate ("re-verify inherited carries at every amendment arc"). Discipline applies to artifacts authored under workflow v1.9 onward; v1.8-and-prior carries are grandfathered at their existing discipline.*

#### §7.4.7.1 Carry-text disposition taxonomy

A "carry" is a finding surfaced at §"Adjacent observations" (or equivalent FM-2 finding-disposition section) in a delta-only spec-file (e.g., `Spec_<axis>_v<n>.md`) with explicit "NOT patched per FM-2" routing to a future apply-pass arc. Carries propagate verbatim across delta-file lineage (v_n → v_n+1 → ...) UNLESS explicitly closed at an apply-pass arc.

A carry's **disposition state** is one of:

| Disposition state | Semantic | Closure shape |
|---|---|---|
| **GENUINE** | Carry-text accurately describes a still-open defect at the production state / cited substrate / cross-artifact state at the current spec version | NO closure owed; carry MAY remain across future delta versions |
| **STALE** | Carry-text describes a defect-shape that does NOT match the actual production state / cited substrate / cross-artifact state at the current spec version | Closure REQUIRED at next opportunity per §7.4.7.4 amendment-arc discipline |

A STALE carry is a fidelity-grammar defect — the carry's content has fallen out of byte-exact / structural-fidelity / citation-only alignment with the substrate state it cites. STALE carries propagate the defect verbatim across delta versions until explicitly closed.

#### §7.4.7.2 Five species of stale-carry-text disposition

Empirical-lineage at OD spec v1.15 / v1.16 / v1.17 / v1.18 / v1.21 catalogues five distinct species of STALE carry, each with a distinct closure shape:

| Species | Carry framing at v_n | Actual state at v_n discovery | Closure-shape at v_n+1 |
|---|---|---|---|
| **1. phantom-as-described** | Carry claims a defect at substrate (e.g., "row 10 cite drift; cardinality 6→7 cardinality event") | Empirical verification at substrate confirms NONE of the carry's three claims hold (row reference, section cite, cardinality event all phantom) | **CLOSED-as-phantom** at v_n+1 via §1 canonical-reading amendment table closing the phantom carry + fixing actual underlying drift (different shape than carry described) |
| **2. stale-carry-with-real-but-different-shape** | Carry forecasts wrong defect shape (e.g., "spec amendment owed at §A/§B/§C") | Real defect existed at different shape (e.g., "perform deferred WebFetch tiebreaker check") | **CLOSED-via-re-litigation** at v_n+1 by performing the deferred verification + applying the correct-shape amendment |
| **3. resolved-but-carry-stale-inherited** | Inherited carry across multiple delta versions (v_n+1, v_n+2, ...) with "NOT patched per FM-2; separate apply-pass arc owed" disposition | Defect was resolved at downstream code (production / impl / co-publication) at commit C BEFORE the carry-text disposition was refreshed at any v_n+k | **CLOSED-as-resolved-at-{commit C}** at v_n+k+1 via §1 canonical-reading amendment refreshing carry-text disposition + cite-cascade to downstream artifacts |
| **4. authoring-time stale carry** | SELF-AUTHORED carry at v_n stale at the moment of writing because underlying production state / fork doc closure / cross-artifact resolution NOT empirically verified at authoring time | Resolution commit existed BEFORE v_n authoring; production self-documents closure at inline comment / commit log | **CLOSED-as-resolved-at-{commit C}** at v_n+1 with explicit "authored FRESH at v_n WITHOUT empirical verification at authoring time" attribution |
| **5. post-authoring stale carry** | SELF-AUTHORED carry at v_n initially genuine at authoring-commit time | Downstream code (production-emission / fork-doc-closure / cross-artifact-resolution) lands AFTER v_n authoring commit, between authoring-timestamp and next-substantive-amendment-opportunity | **CLOSED-as-resolved-at-{commit C}** at v_n+1 with explicit timestamp-gap attribution (authoring-commit vs resolution-commit ordering documented at change-note) |

Species 1–3 operate on **inherited carries** (carries propagated from prior delta versions); species 4–5 operate on **self-authored carries** (carries authored at the same delta version's authoring arc).

#### §7.4.7.3 Pre-substantive empirical-verification audit (load-bearing)

The strengthened discipline candidate from OD spec v1.18 §5 / v1.21 §"Change-note":

> **At EVERY §"Adjacent observations" entry authoring (inherited OR new), AND at EVERY subsequent substantive-amendment opportunity, empirically verify the entry against production state / fork doc closures / cross-artifact resolutions AT THE MOMENT OF WRITING (not only at the time of the originating arc).**

Operational shape:

1. **Inherited carry verification.** At every substantive amendment opportunity (i.e., authoring v_n+1 over v_n), before authoring v_n+1's §"Adjacent observations" section, empirically verify EACH inherited carry from v_n's §"Adjacent observations" against:
   - production state at worktree HEAD (grep / cite verification at named source files);
   - fork doc closure state (re-read named fork docs for ratification / closure events);
   - cross-artifact resolution state (cite verification at downstream artifacts named in carry).
2. **Self-authored carry verification.** Same as inherited carry verification, applied to any NEW carry authored at v_n+1.
3. **Stale-carry disposition.** For each carry identified as STALE per §7.4.7.1 + §7.4.7.2, author a §1 canonical-reading amendment closing the carry per the appropriate species-specific closure shape (§7.4.7.2 column 4).
4. **Genuine-carry preservation.** For carries verified GENUINE, preserve verbatim at v_n+1 §"Adjacent observations".

The audit produces one of three dispositions per carry:

| Disposition | Criteria | Closure action |
|---|---|---|
| **GENUINE — preserve** | Empirical verification confirms carry-text accurately describes still-open defect | Carry preserved verbatim at v_n+1 |
| **STALE — close** | Empirical verification confirms carry-text describes resolved / phantom / different-shape defect | §1 canonical-reading amendment table at v_n+1 closing carry per appropriate species |
| **AMBIGUOUS — route** | Empirical verification cannot conclusively discriminate GENUINE vs STALE | Route to operator AskUserQuestion before authoring v_n+1; do NOT assume disposition |

Falsifying §7.4.7.3 audit discipline (i.e., authoring a v_n+1 §"Adjacent observations" section WITHOUT performing the audit, OR performing the audit without acting on STALE findings) is a Class 2 finding by default per §4.1 discriminator (a).

#### §7.4.7.4 Amendment-arc closure shape

When a carry is identified STALE per §7.4.7.3 audit, the closure shape at v_n+1 follows the species-specific closure column of §7.4.7.2:

1. **Closure header at v_n+1 change-note.** Cite the closed carry by its species (phantom-as-described / stale-carry-with-real-but-different-shape / resolved-but-carry-stale-inherited / authoring-time stale carry / post-authoring stale carry) + the closure commit hash (where applicable) + the authoring-vs-resolution timestamp gap (where applicable).
2. **§1 canonical-reading amendment table.** NEW §1 amendment table at v_n+1 enumerating the closed carry sites + the corrected canonical reading. Per delta-only-spec-file convention: v_n file body PRESERVED VERBATIM; v_n+1 §1 is the canonical interpretation going forward.
3. **§"Adjacent observations" refresh.** Remove the closed carry from v_n+1 §"Adjacent observations" carry-set. Document the closure at v_n+1 §"Adjacent observations" as a closed-finding entry (e.g., "(a) v_n finding (X) — CLOSED-as-{species}-at-{commit-C} at v_n+1 §1.Y. Removed from carry-set.").
4. **Cross-artifact cite-cascade disposition.** NEW §N cross-artifact cite-cascade disposition table at v_n+1 enumerating downstream artifact sites that reference the closed carry. For each site: route to "CO-PUBLISHED this arc" (sites updated at the same commit) OR "NO change owed — {reason}" (sites unaffected by the closure).
5. **Workspace CLAUDE.md row bump.** Workspace `CLAUDE.md` §2.X spec-row narrative updated to v_n+1 with closure narrative; v_n + earlier lineage preserved.

#### §7.4.7.5 Pattern-catalogue accumulation discipline

Each new species of stale-carry-text disposition surfaced at empirical lineage MUST be catalogued at v_n+1 §"Change-note" or §"Adjacent observations" with:

- Species number (next-in-sequence per the closed enumeration at §7.4.7.2; species cardinality 5 at workflow v1.9 publication);
- Distinguishing characteristic from prior species (which closure event triggers the species; which carry-shape distinguishes it from prior species);
- Closure-shape template (column 4 of §7.4.7.2);
- Common-ancestor relationship to prior species (e.g., v1.15 phantom + v1.16 different-shape + v1.17 resolved-but-stale + v1.18 authoring-time + v1.21 post-authoring share common ancestor "stale carry-text disposition").

The pattern catalogue at §7.4.7.2 is OPEN (additive; species 6+ MAY be surfaced at future arcs); closure of new species at NEW workflow-doc revisions is the canonical mechanism for catalogue accumulation. Workflow v1.9 →  v1.10 / v1.11 / ... MAY extend the species enumeration without v2.x major-revision routing.

#### §7.4.7.6 Out-of-scope artifact classes

§7.4.7 discipline applies to delta-only spec-file authoring (per §7.4.6.1 in-scope enumeration: Implementation plan / Axis specification / Architectural Design Document / Product Requirements Document). Out-of-scope artifact classes per §7.4.6.4 remain under their existing filing-time discipline; §7.4.7 does NOT extend audit scope.

Specifically:

| Artifact class | §7.4.7 applicability |
|---|---|
| Delta-only spec files (`Spec_<axis>_v<n>.md`) | **IN-SCOPE** — §7.4.7 audit at every v_n+1 authoring |
| Implementation plan deltas (`Implementation_Plan_<axis>_v<n>.md`) | **IN-SCOPE** — §7.4.7 audit at every v_n+1 authoring |
| ADD revisions (`Architectural_Design_Document_v<n>.md`) | **IN-SCOPE** — §7.4.7 audit at every v_n+1 authoring |
| PRD revisions (`PRD_v<n>.md`) | **IN-SCOPE** — §7.4.7 audit at every v_n+1 authoring |
| ADRs / CXA / IVR / adversarial-review reports / kickoffs / handoffs / revision logs / workflow document | **OUT-OF-SCOPE** per §7.4.6.4 |

Operator may revisit at a future Workflow revision if out-of-scope artifact classes exhibit stale-carry pattern accumulation.

---

## §2 Sections preserved verbatim at v1.9

Per workflow-doc v1.x narrow-scope revision convention + ADDITIVE-only §7.4 amendment + FM-2 no-extension discipline, the v1.9 amendment touches ONLY the NEW §7.4.7 sub-section. The following sections are PRESERVED VERBATIM from v1.8:

- **§0** Visual Summary (incl. §0.0–§0.8 sub-sections)
- **§1** Purpose and Scope
- **§2** Phase Definitions (incl. §2.1–§2.7)
- **§3** Phase Dependencies and Ordering
- **§4** Workflow Forks and Revision Triggers (incl. §4.1–§4.4)
- **§5** Decision Points Where Workflow May Diverge
- **§6** Skill Build Sequencing
- **§7.1** Versioning scheme
- **§7.2** Revision recording
- **§7.3** Revert discipline
- **§7.4.1** Fidelity-claim taxonomy
- **§7.4.2** Byte-exact verification grammar
- **§7.4.3** Structural-fidelity verification grammar
- **§7.4.4** Citation-only grammar
- **§7.4.5** Sub-section-resolution discipline (P1 addressing)
- **§7.4.6** Pre-emission audit gate
- **§8** Open Questions and Known Unknowns (incl. §8.1–§8.6)

---

## §3 Cross-artifact cite-cascade disposition (v1.9 NEW)

| Artifact | Site | Disposition at v1.9 |
|---|---|---|
| Workspace `CLAUDE.md` §2.1 governance row | `Project_Workflow_v1_8.md` cite | **CO-PUBLISHED this arc** — bumped to `Project_Workflow_v1_9.md` |
| `harness-adversarial-reviewer` SKILL.md | §7.4 fidelity-grammar audit anchor | **NO change owed** — adversarial-reviewer skill MAY consult §7.4.7 at P5-CK / P6-CK audit time; skill description does NOT require update |
| `spec-writer` SKILL.md | §12 revision-pass discipline | **NO change owed** — spec-writer skill description names §7.4 generically; §7.4.7 audit shape implicit per generic anchor |
| `implementation-planner` SKILL.md | §8 revision-pass discipline | **NO change owed** — same anchor shape as spec-writer |
| `systems-architect` SKILL.md | Phase 3d ADD authoring + tension-resolution mode | **NO change owed** — §7.4.7 applies to ADD-revision arcs; skill description names §7.4 generically |
| OD spec v1.15..v1.21 + future axis-spec deltas | Source-of-empirical-lineage | **NO change owed** — v1.9 §7.4.7 abstracts the empirical lineage at workflow-grammar layer; spec files cite the workflow grammar generically (e.g., "per workspace `CLAUDE.md` §4.3 + I-1 byte-exact discipline + v1.18 §5 strengthened discipline"); §7.4.7 is now the canonical anchor for "v1.18 §5 strengthened discipline" framing going forward |
| Peer artifacts at design-substrate/ not listed above | No §7.4 cite | **NO change owed** — verified via grep this session |

---

## §4 Empirical lineage table (v1.9 NEW)

Per §7.4.7.5 pattern-catalogue accumulation discipline, the empirical lineage surfacing the 5 species at v1.9 publication:

| Species | First-surfaced at | Closure commit | Closure shape |
|---|---|---|---|
| 1. phantom-as-described | OD spec v1.15 §2 (2026-05-26) | `1ab6e7d` | §1 canonical-reading amendment table closing phantom + fixing underlying drift |
| 2. stale-carry-with-real-but-different-shape | OD spec v1.16 §3 (2026-05-26) | (re-litigation arc; see v1.16 change-note) | §3 Tension 004 §7 reconciliation supersession |
| 3. resolved-but-carry-stale-inherited | OD spec v1.17 §5 (2026-05-26) | `115387b` (production resolution) | §1 canonical-reading amendment closing carry-text disposition + cite-cascade |
| 4. authoring-time stale carry | OD spec v1.18 §5 (2026-05-26) | `ca5674b` (production resolution) | §1 canonical-reading amendment + STRENGTHENED discipline candidate (v1.18 §5) |
| 5. post-authoring stale carry | OD spec v1.21 §"Change-note" (2026-05-27) | `e874a03` (Path A production emission) | §1 finding-closure-disposition refresh + FURTHER-STRENGTHENED discipline candidate (v1.21 §"Change-note") |

Workflow v1.9 §7.4.7.2 catalogues the 5 species; future arcs MAY extend per §7.4.7.5.

---

## Filing footer

| Field | Value |
|---|---|
| Version | v1.9 (Narrow-scope discipline strengthening at §7.4 fidelity-grammar; NEW §7.4.7 stale-carry-text disposition discipline + 5-species catalogue + pre-substantive empirical-verification audit at every amendment arc + amendment-arc closure shape; §1–§7.3 + §7.4.1–§7.4.6 + §8 PRESERVED VERBATIM; delta-only authoring path adopted for narrow workflow-doc revisions, NEW workspace precedent) |
| Trigger | User-routed "next highest-value arc" 2026-05-27 selecting workflow-grammar discipline strengthening as the meta-fix preventing future stale-carry recurrence; empirical-motivation at 5 fidelity-pure citation-correction patches at OD spec lineage 2026-05-26 → 2026-05-27 |
| Supersedes | v1.8 §7.4 fidelity-grammar discipline (extended with §7.4.7; §7.4.1–§7.4.6 PRESERVED VERBATIM) |
| Scope of revision | NARROW: NEW §7.4.7 sub-section authoring + 5-species catalogue + strengthened discipline candidate. ZERO change to fidelity-claim taxonomy + byte-exact grammar + structural-fidelity grammar + citation-only grammar + sub-section-resolution discipline + pre-emission audit gate. Co-publication: workspace CLAUDE.md §2.1 governance row bump. ZERO downstream-skill description change owed. |
| Contract change | None at workflow-grammar layer. Discipline-strengthening additive at §7.4.7. |
| Cross-axis cascade | ZERO at downstream-skill description layer. §3 cross-artifact cite-cascade disposition documents 7 sites — 1 co-published at this arc (workspace CLAUDE.md); 6 NO-change verified. |
| Authority anchor | OD spec v1.15 / v1.16 / v1.17 / v1.18 / v1.21 fidelity-pure citation-correction patches (5 empirical closures 2026-05-26 → 2026-05-27); v1.18 §5 STRENGTHENED discipline; v1.21 §"Change-note" FURTHER-STRENGTHENED discipline. The 5 species + strengthened discipline are abstracted at v1.9 §7.4.7 as workflow-grammar rules applicable across all delta-only spec-file authoring. |
| Predecessor | v1.8 (cascade-closure substrate-driven P6-CK Iter 4 extension at §4.1.4.6) |
| Successor | v1.10 (next operator-discretion arc — candidates: species-6+ catalogue extension; iteration-ceiling default revision per §8.6; phase-abandonment handling per §8.2; council-deliberation-token-budget per §8.3) |
| Pattern catalogue | §7.4.7.2 catalogues 5 species of stale-carry-text disposition; §7.4.7.5 establishes additive-catalogue accumulation discipline. Workflow-doc delta-only authoring precedent set at this revision (matches spec-file delta-only convention already operative at OD spec v1.15+ / CP spec v1.13+ / runtime spec v1.16+). |
| Advisor application | NOT invoked at this arc per workspace precedent for narrow-scope discipline-strengthening additions anchored at conclusive empirical lineage (5 prior closures provide the authority anchor; the workflow-grammar abstraction is straightforward). 22nd application of `[[advisor-before-substantive-work-for-cross-axis-blockers]]` posture observed (advisor pass deemed unnecessary; empirical lineage is the authority). |
| Filing | `design-substrate/Project_Workflow_v1_9.md` (this file). v1.8 PRESERVED VERBATIM as historical anchor at `design-substrate/Project_Workflow_v1_8.md`; no archive move required at workspace convention (workflow-doc archives at `design-substrate/archive/` are historical sub-version log entries, not full-file replacements). |

---

*End of Project Workflow v1.9.*
