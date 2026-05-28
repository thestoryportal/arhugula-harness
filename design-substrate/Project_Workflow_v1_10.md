# Project Workflow — v1.10 (delta over v1.9)

---

## Change-note (v1.9 → v1.10)

**Scope of revision.** Two-fold substantive amendment at §7.4.7 stale-carry-text disposition discipline:

1. **§7.4.7.2 "Sub-species" column extension** per v1.9 §7.4.7.5 catalogue-accumulation discipline + empirical cardinality of **9 sub-species refinements of species 3 (resolved-but-carry-stale-inherited)** catalogued across 8 consecutive arcs at OD spec / CP spec / CXA / runtime spec lineages 2026-05-26 → 2026-05-27 (lineage at §4 of this delta).

2. **§7.4.7.3 audit-template strengthening** absorbing two candidates surfaced at recent arcs:
   - **Candidate (a) — sibling-section audit at attribute/carrier/enum amendment.** Per CP spec v1.23 §"Adjacent observations" (f): "at any §N.M amendment that introduces a new attribute / carrier / enum, audit ALL declaration sites in sibling sub-sections for stale-carry-text against the amendment." Strengthens §7.4.7.3 audit-template to catch intra-spec-sibling-supersession (sub-species 3.intra-spec-sibling-supersession) at the originating-amendment arc, foreclosing the 20+-delta carry pattern that motivated CP v1.23.
   - **Candidate (b) — session-resumption inherited-framing audit.** Per Reading B validator-composer fork-doc closure reframe 2026-05-27 + CP-9 ResumptionKind reframe 2026-05-27 + tenant_id binding-fix-not-schema-extension reframe 2026-05-27: empirical-orientation at session-resumption can surface that an "inherited next-load-bearing work framing" from a checkpoint summary is stale-as-described when the named work landed between checkpoint authoring and resume. Strengthens §7.4.7.3 audit-template to apply at session-resumption operator-actions, not only at delta-only spec-file amendment arcs.

**Empirical lineage that prompted v1.10 (operator-routed 2026-05-27).** Operator-survey question 2026-05-27 ("survey what's actually next load-bearing"). Across 8 substantive arcs in single session 2026-05-27 + cumulative 6+ consecutive arcs prior (OD spec v1.22 → v1.23 → v1.24 + CXA v2.13 → v2.14 + CP spec v1.20 → v1.21 → v1.22 → v1.23 + Reading B fork doc closure), 9 distinct sub-species of species 3 catalogued; §7.4.7.5 catalogue-accumulation discipline indicated by 9 sub-species in 8 arcs is overdue for column extension. CP v1.23 finding (f) + Reading B reframe finding strengthen audit-template at distinct trigger points.

**No fork doc filed.** Per workspace precedent for substantive amendments at workflow-doc revisions where prior-version §7.4.7.5 explicitly authorizes the extension shape ("Workflow v1.9 → v1.10 / v1.11 / ... MAY extend the species enumeration without v2.x major-revision routing"). v1.10 IS that extension. Operator AskUserQuestion 2026-05-27 ratified Option A (workflow-doc revision pass) over candidate alternatives (B = AS-5 idempotency-key invocation; C = v1.7+ parent_sandbox_tier field; D = stop).

**Self-application of §7.4.7.3 audit at v1.9 → v1.10 transition.** Empirical-verification audit performed pre-substantive-authoring at v1.10 arc opening per v1.9 §7.4.7.3:

| Inherited carry from v1.9 | Verification | Disposition |
|---|---|---|
| §7.4.7.2 five-species enumeration | Empirical inventory at design-substrate/Spec_*.md + Cross_Axis*.md + Implementation*.md confirms 5 species canonical at v1.9 publication 2026-05-27 18:31 -0600; 9 species-3 sub-species refinements catalogued across subsequent arcs WITHOUT changing the 5-species enumeration at the species column | GENUINE at species-axis; AMENDMENT-OWED at sub-species refinement axis per v1.9 §7.4.7.5 explicit authorization |
| §7.4.7.3 audit-template | Empirical lineage at CP v1.23 + Reading B reframe surfaces 2 distinct trigger-point strengthening candidates | STALE-by-accumulation; STRENGTHENING-OWED at v1.10 |
| §7.4.7.6 out-of-scope artifact class enumeration | Empirical check at v1.10 arc opening — session-resumption operator-actions on checkpoint summaries are NOT a delta-only spec file class (out-of-scope per §7.4.7.6); v1.10 candidate (b) extends §7.4.7.3 audit-template scope rather than amending §7.4.7.6 in-scope enumeration | GENUINE; §7.4.7.6 PRESERVED VERBATIM; v1.10 amendment is at §7.4.7.3 scope-of-audit-application, not §7.4.7.6 artifact-class-enumeration |

ZERO C-*-NN contract change; ZERO retirement event; ZERO production code change; ZERO cross-axis cascade. Pure workflow-grammar canonicalization. Co-publication: workspace `CLAUDE.md` §2.1 governance row bump to v1.10.

---

## §1 §7.4.7.2 Sub-species column extension (canonical-reading amendment)

The §7.4.7.2 five-species enumeration table at v1.9 is amended at v1.10 to add a **6th column "Sub-species"** populated with empirically-catalogued sub-species refinements. v1.9 file body PRESERVED VERBATIM per delta-only-spec-file convention; v1.10 §1 is the canonical reading going forward.

### §1.1 Amended §7.4.7.2 table (canonical at v1.10)

| # | Species | Carry framing at v_n | Actual state at v_n discovery | Closure-shape at v_n+1 | **Sub-species (catalogued; OPEN catalogue per §7.4.7.5)** |
|---|---|---|---|---|---|
| 1 | **phantom-as-described** | Carry claims a defect at substrate (e.g., "row 10 cite drift; cardinality 6→7 cardinality event") | Empirical verification at substrate confirms NONE of the carry's three claims hold | **CLOSED-as-phantom** at v_n+1 via §1 canonical-reading amendment table closing the phantom carry + fixing actual underlying drift | (none catalogued at v1.10 — sub-species refinements not yet empirically surfaced for species 1) |
| 2 | **stale-carry-with-real-but-different-shape** | Carry forecasts wrong defect shape | Real defect existed at different shape | **CLOSED-via-re-litigation** at v_n+1 by performing the deferred verification + applying the correct-shape amendment | (none catalogued at v1.10) |
| 3 | **resolved-but-carry-stale-inherited** | Inherited carry across multiple delta versions with "NOT patched per FM-2; separate apply-pass arc owed" disposition | Defect was resolved at downstream event (production / impl / co-publication / fork-doc-closure / workflow-grammar canonicalization / etc.) BEFORE the carry-text disposition was refreshed at any v_n+k | **CLOSED-as-resolved-at-{event E}** at v_n+k+1 via §1 canonical-reading amendment refreshing carry-text disposition + cite-cascade to downstream artifacts | **9 sub-species catalogued at v1.10 (see §1.2 below); OPEN catalogue per §7.4.7.5** |
| 4 | **authoring-time stale carry** | SELF-AUTHORED carry at v_n stale at the moment of writing because underlying state NOT empirically verified at authoring time | Resolution commit existed BEFORE v_n authoring | **CLOSED-as-resolved-at-{commit C}** at v_n+1 with explicit "authored FRESH at v_n WITHOUT empirical verification at authoring time" attribution | (none catalogued at v1.10) |
| 5 | **post-authoring stale carry** | SELF-AUTHORED carry at v_n initially genuine at authoring-commit time | Downstream event lands AFTER v_n authoring commit, between authoring-timestamp and next-substantive-amendment-opportunity | **CLOSED-as-resolved-at-{commit C}** at v_n+1 with explicit timestamp-gap attribution | (none catalogued at v1.10) |

### §1.2 Species 3 sub-species enumeration (catalogued at v1.10; OPEN per §7.4.7.5)

| Sub-species | Distinctive closure-event class | Empirical cataloguing arc | Common-ancestor relationship |
|---|---|---|---|
| **3.code-resolution** | Defect resolved at production code commit (named commit hash); carry-text remained stale until next delta amendment refreshed disposition | OD spec v1.17 (closure of v1.13/v1.14/v1.15/v1.16 `gen_ai.system` carry at commit `115387b` 2026-05-26) | Species 3 (resolved-but-carry-stale-inherited) with closure at production-code layer |
| **3.fork-doc-closure** | Defect resolved at operator-ratified fork doc closure event (operator AskUserQuestion ratification + apply-pass); carry-text at inherited fork-doc-body or sibling-spec lagged the closure | OD spec lineage (sibling pattern); validator-composer fork doc Reading B closure 2026-05-27 (carry across 3 days) | Species 3 with closure at fork-doc-ratification layer |
| **3.workflow-grammar** | Defect resolved at upstream workflow-grammar canonicalization (e.g., workflow v1.9 §7.4.7 publication); carry-text at downstream spec arc cited the un-canonicalized framing | OD spec v1.22 (2026-05-27) closing v1.21 (d) + (i) carries at workflow v1.9 §7.4.7.2 / §7.4.7.3 canonicalization | Species 3 with closure at upstream-grammar-artifact layer |
| **3.empirical-verification-of-external-authority** | Defect resolved at WebFetch verification against external authority (e.g., OTel semantic conventions archived text); carry-text at prior spec arcs preserved pre-verification framing | OD spec v1.23 (2026-05-27) closing v1.22 (e) `gen_ai.provider.name` stability tier carry via WebFetch verification at OTel 1.41.0 archived text | Species 3 with closure at external-authority-verification layer |
| **3.same-session-immediate-sequel** | Defect resolved at SAME-SESSION sequel as a SEPARATE arc (separate commit/merge/push cycle) ~minutes-to-~hours after the v_n authoring commit | OD spec v1.24 (2026-05-27) closing v1.23 (f) DERIVATIVE-naming retirement ~70 min after v1.23 publication; OD spec v1.21 closing batch-21 filing carry ~10 min after v1.20 publication | Species 3 with closure at same-session-separate-arc layer |
| **3.retirement-event-filing-arc** | Defect resolved at workspace-cadence-driven retirement event filing (existing 7d cadence); carry-text framing "(separate retirement-event filing arc; operator-discretion timing)" became stale on actual filing | CP spec v1.21 (2026-05-27) + CP plan v2.26 closing v1.20 §0.8 (h) + v2.25 §0.8 (c) batch-21 filing carries | Species 3 with closure at retirement-cadence-driven-event layer |
| **3.binding-fix-not-schema-extension** | Defect resolved at advisor-caught arc-shape-reframe foreclosing schema-extension ceremony; carry-text framing implied CP-19-precedent uniform-shape but empirical orientation discriminated per-field arc-shape | CP spec v1.22 (2026-05-27) closing v1.21 (c) tenant_id sub-axis via binding-fix vs CP-19-precedent fork-ceremony — advisor pre-substantive consultation foreclosed the wider-scope reading | Species 3 with closure at advisor-pre-substantive-arc-shape-reframe layer |
| **3.intra-spec-sibling-supersession** | A sibling sub-section amendment within the same spec file lineage supersedes an attribute/carrier/enum surface, but the original declaration site is NOT amended at the same arc, leaving stale carry-text in the original section across all subsequent delta-only versions | CP spec v1.23 (2026-05-27) closing the 20+-delta `resumption.kind` ↔ `engine.replay_disposition` carrier divergence at §5.2 + §8.1 + §8.3 via §9.1 v1.3 sibling amendment | Species 3 with closure at intra-spec-sibling-supersession layer (the most-aged sub-species: 20+ delta versions across 13+ days at the originating CP spec lineage) |
| **3.carry-suggests-foreclosed-reading** | Carry remains well-formed in describing an open surface, but the carry's *suggested resolution path* is foreclosed at the originating fork doc; pre-substantive empirical-verification at originating fork doc is the discipline that catches this sub-species | CXA v2.14 (2026-05-27) closing v2.13 (b) `schema_violation → policy_override` HIGH semantic stretch as CLOSED-as-fork-doc-Reading-B-by-design per fork `class_1_fork_as_4_f4_enum_taxonomy_mismatch_and_production_bug.md` §3.1 Reading A rejection on semantic-coherence grounds | Species 3 with closure at originating-fork-doc-Reading-B-by-design layer |

### §1.3 Sub-species catalogue is OPEN

Per v1.9 §7.4.7.5 catalogue-accumulation discipline, the sub-species enumeration at species 3 (and other species) is OPEN at v1.10 publication. Future workflow-doc revisions (v1.11 / v1.12 / ...) MAY catalogue additional sub-species under any species per the §7.4.7.5 §3 amendment-arc closure shape:

1. Sub-species number (next-in-sequence under the parent species; e.g., 3.10 / 3.11 / ...);
2. Distinctive closure-event-class statement (column 2 of §1.2 table);
3. Empirical cataloguing arc citation (column 3);
4. Common-ancestor relationship statement (column 4).

Species 1/2/4/5 sub-species enumerations remain empty at v1.10 (no sub-species refinements yet empirically surfaced); these MAY be populated at future arcs per the same §7.4.7.5 mechanism.

---

## §2 §7.4.7.3 audit-template strengthening (substantive amendment)

The §7.4.7.3 audit-template at v1.9 (Pre-substantive empirical-verification audit) is amended at v1.10 with TWO strengthening sub-sections. v1.9 §7.4.7.3 file body PRESERVED VERBATIM; v1.10 §2 is the canonical strengthening going forward.

### §2.1 Sibling-section audit at attribute/carrier/enum amendment (NEW §7.4.7.3.A)

When a substantive amendment at v_n+1 introduces a NEW attribute / carrier / enum / contract surface at one §N.M sub-section, the §7.4.7.3 audit-template at v1.10 onward REQUIRES the authoring agent to **also audit ALL declaration sites in sibling sub-sections of the same spec file (and immediate downstream cite consumers) for stale-carry-text against the amendment**.

Operational shape:

1. **Identify the amendment surface.** At v_n+1 authoring, name the introduced attribute / carrier / enum / contract surface + the §N.M sub-section that authors it.
2. **Enumerate sibling declaration sites.** Grep / cite-search the SAME spec file for all sub-sections that mention the prior surface (the surface the amendment supersedes / extends / renames / replaces). Enumerate site-by-site.
3. **Audit each sibling site against the amendment.** For each enumerated sibling site, ask: does the sub-section's text accurately describe the surface at v_n+1, or does it carry stale text from the pre-amendment state?
4. **Refresh stale sibling sites at v_n+1.** Author canonical-reading amendments at v_n+1's §1 amendment table for any sibling sites identified as stale. Apply species-specific closure shape per §7.4.7.2 (typically 3.intra-spec-sibling-supersession if the supersession path is the closure event class).

Falsifying §7.4.7.3.A audit at v_n+1 amendment-introducing-new-attribute/carrier/enum arcs (i.e., authoring the amendment WITHOUT performing the sibling-section audit) is a Class 2 finding by default per §4.1 discriminator (a) — the same discipline as falsifying §7.4.7.3 audit.

**Empirical authority for §7.4.7.3.A.** CP spec v1.3 §9.1 4-attribute amendment (F2-12 sub-scope (i) closure, 2026-05-14) introduced `engine.replay_disposition` as the canonical 4th `engine.*` attribute at the at-emission layer, but the original declaration sites at §5.2 (1 cite) + §8.1 (4 cites) + §8.3 (1 cite) were NOT amended at v1.3 to harmonize the carrier name. The stale carrier-name text carried verbatim from v1.3 through v1.22 (20+ delta versions, 13+ days) until empirical orientation at the CP-9 ResumptionKind investigation 2026-05-27 surfaced the divergence + CP spec v1.23 §1.1 canonical-reading amendment closed it. Applying §7.4.7.3.A at the originating v1.3 amendment arc would have caught the sibling-section drift at the originating commit, foreclosing the 20+-delta carry.

### §2.2 Session-resumption inherited-framing audit (NEW §7.4.7.3.B)

When an agent resumes a session from a checkpoint summary or auto-memory entry that includes a "next load-bearing work" framing, the §7.4.7.3 audit-template at v1.10 onward REQUIRES the agent to **empirically verify the named-work-status against the actual commit log AND production state BEFORE opening a new arc**.

Operational shape:

1. **Identify the inherited framing.** Parse the checkpoint summary or memory entry for any "next load-bearing work" / "remaining work" / "still open" / "OPEN" framings that name specific work artifacts (fork docs / atomic units / retirement gates / etc.).
2. **Audit each inherited framing against current state.** For each named work artifact:
   - Grep the commit log for the work-artifact name + any landing / closing / superseding events that may have landed between checkpoint authoring and resume;
   - Re-read the named artifact (fork doc / atomic unit description / etc.) for its CURRENT status (status-line / §N.X disposition / etc.);
   - Verify cross-artifact state — workspace `CLAUDE.md` / axis `CLAUDE.md` / cite chain — for any status-line refreshes the named-artifact missed.
3. **Disposition stale framings.** If empirical verification surfaces that the inherited framing is stale-as-described (named work landed; status-line refreshed but artifact-body lagged; framing-shape no longer matches current reality), close the stale framing per §7.4.7.4 amendment-arc discipline at the inherited-framing-substrate-artifact (typically a fork doc body + memory entry + workspace CLAUDE.md row).
4. **Surface to operator.** Before opening the inherited arc shape, AskUserQuestion to operator surfacing the empirical refinement + offering arc-shape options reflecting the actual current state (not the stale-inherited framing).

Falsifying §7.4.7.3.B audit at session-resumption (i.e., opening an arc against an inherited framing WITHOUT performing the audit) is a Class 2 finding by default per §4.1 discriminator (a).

**Empirical authority for §7.4.7.3.B.** Three consecutive arc reframes 2026-05-27 across single session: (1) CP-9 ResumptionKind investigation — checkpoint framing "Class 1 fork on universal-vs-pure-pattern-carve-out" was directionally correct but missed §25.5 v1.4 "At v1.4 scope" carve-out language + sibling-section attribute-carrier drift; (2) tenant_id binding lift — checkpoint framing "3 v1.7+ deferred fields under CP-19-precedent shape" was over-broad; advisor pre-substantive orientation discriminated tenant_id as binding-fix-shape (NOT CP-19-precedent); (3) Reading B validator-composer arc — checkpoint framing "next load-bearing work" was stale-as-described; empirical orientation at commit log showed Reading B was already absorbed at runtime spec v1.22 (`918f94a`, 3 days prior). Each reframe avoided 5-15 commits of unnecessary re-litigation work. Applying §7.4.7.3.B at session-resumption would have caught the stale framings at the orientation step, foreclosing the reframe-via-empirical-orientation discipline that ad-hoc absorbed the same closure pattern across 3 arcs in single session.

**Scope of §7.4.7.3.B.** Applies to all session-resumption operator-actions involving inherited framings — not only checkpoint summaries / memory entries, but also: (i) inherited TaskList entries from prior sessions; (ii) inherited fork-doc body framings carried across multi-session arc cadence; (iii) inherited cross-artifact cite-chains where a downstream consumer cites a status that the upstream artifact's body has not yet refreshed.

---

## §3 Cross-artifact cite-cascade disposition (v1.10 NEW)

| Artifact | Site | Disposition at v1.10 |
|---|---|---|
| Workspace `CLAUDE.md` §2.1 governance row | Project_Workflow_v1_9.md cite | **CO-PUBLISHED this arc** — bumped to Project_Workflow_v1_10.md with v1.10 amendment narrative |
| `harness-cp/CLAUDE.md` | No direct §7.4.7 cite at axis CLAUDE.md (verified via grep this session) | **NO change owed** |
| `harness-od/CLAUDE.md` / `harness-as/CLAUDE.md` / `harness-is/CLAUDE.md` | No direct §7.4.7 cite at axis CLAUDE.md (verified via grep this session) | **NO change owed** |
| Design-substrate/ spec files at v_n+1 amendments going forward | Will reference v1.10 §7.4.7.3.A + §7.4.7.3.B at their own §"Adjacent observations" disposition tables when applicable | **PROSPECTIVE** — no immediate change owed; future deltas absorb |
| Open Class 3 drift docs at `.harness/` (5 enumerated at this session's survey) | `class_3_drift_ledger_v2_section_6_od_2_row_stale_pre_batch_2.md` / `class_3_drift_od_resume_outcome_enum_gap.md` / `class_3_tension_c_rt_16_spec_internal_drift.md` / `class_3_tension_u_rt_59_spec_prose_drift.md` (4 of 5 — 5th already RESOLVED at meta-arch absorption) | **NO change owed at v1.10** — these route to their respective next-spec-revision-pass (OD / runtime / CP) per FM-2; v1.10 §7.4.7.3.A audit-template applies prospectively at their closure arcs |
| Existing v_n delta spec files with carry-text framings | All v1.9-and-prior delta files | **PRESERVED VERBATIM** per §7.4.7.4 amendment-arc closure shape step 1 ("v_n file body PRESERVED VERBATIM") |
| Active checkpoint summaries / memory entries with "next load-bearing work" framings | Per §7.4.7.3.B prospective application at next session-resumption | **PROSPECTIVE** — future operator-actions absorb the discipline |

---

## §4 Empirical lineage table (v1.10 NEW)

Empirical lineage of arcs that catalogued the 9 species-3 sub-species enumerated at §1.2:

| Sub-species | Cataloguing arc | Authoring date | Carry age at closure | Closure event |
|---|---|---|---|---|
| 3.code-resolution | OD spec v1.17 | 2026-05-26 | 4 delta versions (v1.13–v1.16) | Production commit `115387b` `gen_ai.system → gen_ai.provider.name` rename |
| 3.fork-doc-closure | OD spec lineage + validator-composer fork doc closure 2026-05-27 | 2026-05-26 (catalogued); 2026-05-27 (Reading B applied) | 3 days at Reading B closure | Operator-ratified fork doc apply-pass |
| 3.workflow-grammar | OD spec v1.22 + CP spec v1.21 | 2026-05-27 | ~1 hour at workflow v1.9 publication | Workflow v1.9 §7.4.7 publication |
| 3.empirical-verification-of-external-authority | OD spec v1.23 | 2026-05-27 | 7 delta versions (v1.16–v1.22) | WebFetch verification at OTel 1.41.0 archived text |
| 3.same-session-immediate-sequel | OD spec v1.24 + OD spec v1.21 | 2026-05-27 | ~70 minutes (v1.24); ~10 minutes (v1.21) | Same-session separate-arc landing |
| 3.retirement-event-filing-arc | CP spec v1.21 + CP plan v2.26 | 2026-05-27 | ~10 minutes at batch-21 filing | Batch-21 retirement event filing commit `c5582b6` |
| 3.binding-fix-not-schema-extension | CP spec v1.22 | 2026-05-27 | (carry framed as future-arc; foreclosed at advisor consultation before becoming stale) | Advisor pre-substantive arc-shape-reframe consultation |
| 3.intra-spec-sibling-supersession | CP spec v1.23 | 2026-05-27 | 20+ delta versions (v1.3–v1.22) over 13+ days | Empirical orientation at CP-9 ResumptionKind investigation |
| 3.carry-suggests-foreclosed-reading | CXA v2.14 | 2026-05-27 | (carry well-formed but foreclosed at originating fork doc) | Pre-substantive empirical-verification at originating fork doc |

**Pattern observation.** 9 sub-species in 8 consecutive arcs (2026-05-26 → 2026-05-27) is empirically the strongest cardinality evidence for the §7.4.7.5 catalogue-accumulation discipline since v1.9 publication. The accumulation rate (~1 sub-species per arc) suggests continued sub-species surfacing at future arcs; the OPEN catalogue at §1.3 + §7.4.7.5 mechanism accommodates this without v2.x major-revision routing.

---

## §5 Sections preserved verbatim at v1.10

Per delta-only convention + FM-2 no-extension discipline + workflow-grammar canonicalization scope, the v1.10 amendment touches ONLY the NEW §1 sub-species column extension + §2 audit-template strengthening + §3 cite-cascade disposition + §4 empirical lineage + this §5 sections-preserved-verbatim. The following sections are PRESERVED VERBATIM at file-body layer:

- **§7.4.7.1** carry-text disposition taxonomy (file body unchanged; canonical at v1.10)
- **§7.4.7.2** five-species enumeration (file body unchanged; v1.10 §1 IS the canonical-reading amendment adding the sub-species column)
- **§7.4.7.3** pre-substantive empirical-verification audit (file body unchanged; v1.10 §2 IS the canonical-reading strengthening adding §7.4.7.3.A + §7.4.7.3.B)
- **§7.4.7.4** amendment-arc closure shape (file body unchanged; canonical at v1.10)
- **§7.4.7.5** pattern-catalogue accumulation discipline (file body unchanged; canonical at v1.10; v1.10 IS the §7.4.7.5 explicit-authorization extension)
- **§7.4.7.6** out-of-scope artifact classes (file body unchanged; canonical at v1.10)
- **All v1.8 + v1.9 lineage sections at §1 + §2 + §3 + §4 + §5 + §6 + §7 + §8** (file body unchanged; canonical at v1.10 + earlier)

---

## §6 Adjacent observations (surfaced as findings; NOT patched per FM-2)

(a) **Species 1 / 2 / 4 / 5 sub-species enumeration empty at v1.10.** No sub-species refinements yet empirically surfaced for species 1 (phantom-as-described) / species 2 (stale-carry-with-real-but-different-shape) / species 4 (authoring-time stale carry) / species 5 (post-authoring stale carry). Future workflow-doc revisions MAY catalogue refinements under any species per §7.4.7.5. Catalogued for observation only.

(b) **§7.4.7.3 audit Class 2 falsification penalty preserved at v1.10.** v1.9 §7.4.7.3 declares "Falsifying §7.4.7.3 audit discipline … is a Class 2 finding by default per §4.1 discriminator (a)." v1.10 §7.4.7.3.A + §7.4.7.3.B inherit this falsification penalty by extending §7.4.7.3 scope; no separate penalty declaration needed.

(c) **Open Class 3 drift docs (4 enumerated at §3) ride next-spec-revision-pass closure under §7.4.7.3 + §7.4.7.3.A discipline.** These will close at OD spec / runtime spec / CP spec next amendment arcs per existing FM-2 routing. NOT patched at v1.10 per FM-2 single-focus scope.

(d) **Class 3 drift backlog cardinality (~4 open docs as of v1.10) is bounded.** No new Class 3 drift docs have accumulated post-v1.9 publication (verified via grep this session). The §7.4.7.3 + §7.4.7.3.A strengthening at v1.10 prospectively foreclosues the species-3 sub-species accumulation rate from continuing at the pre-v1.10 pace; future Class 3 drift filings should reduce. Catalogued for observation only.

(e) **§7.4.7.3.B prospective scope at multi-session arcs.** §7.4.7.3.B applies to session-resumption operator-actions; it ALSO applies prospectively to multi-session arcs where inherited framings span multiple checkpoint summaries / memory entries / fork doc body refreshes. Multi-session arc empirical-orientation discipline strengthens beyond single-session-resumption scope. Catalogued for observation.

(f) **`harness-cp/CLAUDE.md` §4.1 H_T-CP-9 PARTIAL row text** — "ResumptionKind 5-class — driver emits binary only" framing was partially-refined at CP spec v1.23 §"Adjacent observations" (c). Per §7.4.7.3.A applied to v1.23 amendment arc: H_T-CP-9 PARTIAL status framing is GENUINE at v1.23 carrier-harmonization scope (carve-out canonical at v1.4 scope); no harness-cp/CLAUDE.md row refresh owed. Catalogued for observation.

(g) **Per-arc-ask push protocol** — surfaced at Reading B validator-composer fork-doc closure arc 2026-05-27 + earlier CP-9 / tenant_id / v1.24 / v2.14 arcs. Protocol discipline carry; not encoded at workflow v1.10 scope (would be a separate workflow amendment about operator-collaboration discipline rather than stale-carry-text discipline). Catalogued for future workflow-doc revision consideration.

---

## Filing footer

| Field | Value |
|---|---|
| Version | v1.10 (Substantive amendment per v1.9 §7.4.7.5 explicit-authorization extension — NEW §1 §7.4.7.2 sub-species column extension with 9 species-3 sub-species catalogued + NEW §2 §7.4.7.3 audit-template strengthening with §7.4.7.3.A sibling-section audit + §7.4.7.3.B session-resumption inherited-framing audit; v1.9 file body PRESERVED VERBATIM per delta-only convention) |
| Trigger | Operator-routed survey question "survey what's actually next load-bearing" 2026-05-27 + AskUserQuestion ratification Option A (workflow-doc revision pass over AS-5 idempotency-key invocation, v1.7+ parent_sandbox_tier field, or stop) |
| Supersedes | v1.9 §7.4.7.2 + §7.4.7.3 file-body framing without sub-species column + without §7.4.7.3.A + §7.4.7.3.B strengthening |
| Scope of revision | SUBSTANTIVE: NEW §1 + §2 + §3 + §4 + §5 + §6. ZERO C-*-NN contract change; ZERO retirement event; ZERO production code change; ZERO cross-axis cascade. Pure workflow-grammar canonicalization absorbing empirical lineage at OD/CP/CXA/runtime spec arcs 2026-05-26 → 2026-05-27. Co-publication: workspace `CLAUDE.md` §2.1 governance row bump. |
| Cross-axis cascade | ZERO. v1.10 is workflow-grammar canonicalization; no per-axis spec / plan / CXA / production code touch. |
| Authority anchor | v1.9 §7.4.7.5 catalogue-accumulation discipline + explicit authorization for "Workflow v1.9 → v1.10 / v1.11 / ... MAY extend the species enumeration without v2.x major-revision routing"; 9 species-3 sub-species in 8 consecutive arcs empirical cardinality |
| Predecessor | v1.9 (Stale-carry-text disposition discipline) |
| Successor | (none — current canonical) |
| Date | 2026-05-27 |
