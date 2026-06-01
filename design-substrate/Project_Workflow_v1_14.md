# Project Workflow — v1.14 (delta over v1.13)

---

## Change-note (v1.13 → v1.14)

**Scope of revision.** Catalogue-establishing substantive amendment authoring **NEW §7.5 — Process-discipline catalogue** under §7 (Workflow Versioning Discipline), a *sibling to §7.4 fidelity-grammar discipline*. §7.5 catalogues recurring **execution-process disciplines** — how a Phase-7 (or design-phase) arc is *sequenced, verified, and decomposed* — that are empirically load-bearing across the workspace but are **NOT stale-carry-text disposition** (so they do not belong under §7.4.7) and **NOT fidelity-claim grammar** (so they do not belong under §7.4.1–§7.4.6). v1.13 + v1.12 + v1.11 + v1.10 + v1.9 + v1.8 file bodies PRESERVED VERBATIM per delta-only convention.

This delta follows the **v1.9 framework-establishing precedent** (not the v1.10–v1.13 single-focus incremental precedent): v1.9 introduced the *entire* §7.4.7 framework (taxonomy + 5-species catalogue + audit + closure-shape + accumulation discipline) in one delta, seeding 5 species each backed by an independent empirical closure. v1.14 mirrors that shape for §7.5 — scaffold + seed-from-confirmed-lineage + OPEN accumulation clause — rather than artificially narrowing to one entry.

**Trigger (roadmap-driven, operator-authorized 2026-06-01).** `R-600-workflow-v1-14-amendment` (roadmap §5.6, PROPOSED → authorized this arc). Its evidence base is the `R-600-pattern-bake-in-sweep` survey (`.harness/R-600-pattern-bake-in-sweep.md`, PR #196), which enumerated the workspace auto-memory store and surfaced — across three independent surfacings (v1.13 §3(a) → v1.14-deferral 2026-05-29 → the sweep 2026-06-01) — the same structural gap: a set of strong Class-C disciplines that are **all NON-§7.4.7-shape**. §7.4.7 cannot absorb them without degrading taxonomy coherence (the exact failure mode flagged at v1.13 §3(a) + (c)). §7.5 is the correct home.

**Authority anchor.** v1.13 §3(a) explicit forward-routing ("at a future workflow-doc revision (v1.14 / v1.15+), consider authoring a NEW §7.4.7.X plan-revision-authoring-discipline catalogue distinct from §7.4.7 stale-carry-text discipline; OR ... a NEW §plan-revision-discipline section under §7") + `R-600-pattern-bake-in-sweep.md` §2 recommendation ("author a NEW process-discipline catalogue distinct from §7.4.7 — either a new §7.5 process-discipline catalogue or a new §7.4.7.X sibling") + the v1.9 §7.4.7.5 catalogue-accumulation precedent (additive catalogue at NEW workflow-doc revisions, no v2.x major-revision routing). The §7.5 entries' empirical anchors are the workspace memory store + the `.harness/` retirement-event + fork-doc ledger.

**§7.4 ↔ §7.5 boundary (legibility statement).** §7.4 (fidelity-grammar) governs *how you make claims about substrate* — the byte-exact / structural-fidelity / citation-only taxonomy + the stale-carry-text disposition of "Adjacent observations" carries at §7.4.7. §7.5 (process-discipline) governs *how you sequence, verify, and decompose execution* — verification shape, AC decomposition, discovery sequencing, plan-revision authoring. The two are siblings under §7 (which is already the de-facto home for cross-cutting authoring disciplines that stretch the literal "versioning" title — §7.4 fidelity-grammar does the same).

**Self-application of §7.4.7.3 audit at v1.13 → v1.14 transition.** Empirical-verification audit performed pre-substantive-authoring per v1.10 §2.1 §7.4.7.3.A + §2.2 §7.4.7.3.B + v1.12 §2 §7.4.7.3.C:

| Inherited carry from v1.13 | Verification | Disposition |
|---|---|---|
| §7.4.7.2 species 2 sub-species `2.strike-revision-on-refined-second-tier-reason` (v1.13 §1.1) | Empirical inventory at HEAD: genuine; no new species-2 refinement | PRESERVED VERBATIM at v1.14 |
| §7.4.7.2 species 3 (10) / species 5 ({5.1,5.2}) / species 1/4 (EMPTY) | No new sub-species refinements surfaced at the v1.13 → v1.14 transition | PRESERVED VERBATIM at v1.14 |
| v1.13 §3(a) routing — second candidate `plan-revision-...` is NOT-§7.4.7.2-shape; route to a NEW catalogue at v1.14/v1.15 | This delta IS that catalogue (§7.5). v1.13 §3(a) routing CLOSED at v1.14. | AMENDMENT-OWED → APPLIED at v1.14 §7.5 |
| U-RT-111 v2.36 change-note framing of `plan-revision-against-not-yet-built-substrate` as "§7.4.7.2 sub-species cardinality 1→2" | **STALE-AS-FRAMED** — contradicts v1.13 §3(a) which discriminated the pattern NOT-§7.4.7.2-shape; v1.13 §3(a) is the authority (most recent, the actual workflow doc) | SUPERSEDED at v1.14 §7.5.2 + flagged at §3 (a) |

ZERO C-*-NN contract change; ZERO retirement event filing; ZERO production code change; ZERO cross-axis cascade. Pure workflow-grammar canonicalization. Co-publication: workspace `CLAUDE.md` §2.1 governance row bump to v1.14 + clearance marker `.harness/clearance/Project_Workflow-v1_14-cleared-2026-06-01.md`.

---

## §1 NEW sub-section authoring at §7

### §7.5 Process-discipline catalogue

A catalogue of recurring **execution-process disciplines** empirically load-bearing across Phase-7 (and design-phase) arcs. Distinct from §7.4 fidelity-grammar per the boundary statement in the change-note above. §7.5 is a **catalogue** (heterogeneous disciplines, each with its own statement + empirical anchor + application shape + cross-reference) — **NOT a taxonomy** (it does not decompose a single dimension into species the way §7.4.7.2 decomposes stale-carry-text disposition). Do not force an "N species of X" framing onto §7.5; the entries do not share one axis.

#### §7.5.1 Inclusion gate

A discipline is catalogued at §7.5.2 iff **all three** hold (verify per-candidate at each amendment arc; the gate is per-candidate, NOT a count):

1. **Instance-cardinality ≥2 of independent arcs.** Distinct *arcs* (units / PRs / sessions), not repeated citations of one arc and not multiple rescopes of one unit. (Per the `R-600-pattern-bake-in-sweep` §"Metric caveat": `[[...]]` citation-count is a salience proxy, NOT promotion-cardinality; confirm distinct-instance cardinality empirically.) Single-instance / single-unit-multi-rescope disciplines are admissible **only** under the v1.11 / v1.13 single-instance-at-first-cataloguing precedent, and MUST be labelled as such (not as multi-arc-independent).
2. **Genuinely §7.5-shaped.** A process discipline (sequencing / verification / decomposition / discovery), NOT a §7.4.7 stale-carry-text disposition and NOT a §7.4.1–§7.4.6 fidelity-claim grammar.
3. **No canonical home elsewhere.** If a partial or full home exists (e.g., workspace `CLAUDE.md` §13.1 / §10.9, or the `.harness/` retirement-event-pattern catalogue), **cite-don't-relocate**: catalogue with an explicit cross-reference rather than re-homing the discipline.

#### §7.5.2 Seeded disciplines (catalogued at v1.14)

| # | Discipline | Statement | Independent-instance anchor | Application shape | Cross-reference |
|---|---|---|---|---|---|
| **PD-1** | **halt-route-split-AC** | When a Phase-7 atomic unit's acceptance criteria bundle a cleanly materializable surface with an unmaterializable one (a plan signature written as a `… per §X …` placeholder, or a type that transitively needs substrate the unit's package cannot own), do NOT land the whole unit and do NOT silently drop the bad part — **split it**: land the materializable subset, file Class 1 + STRIKE the unmaterializable AC, revise the plan. Silent absorption is the worst failure mode (X-AL-3 / I-2); but holding the whole unit blocks the lane on a part nothing downstream needs. | **≥3 independent arcs**: U-CORE-01 (`.harness/class_1_tension_u_core_01_workflow_event.md`, 2026-05-15); U-OD-41 AC #8 PARTIAL-LANDED (OD plan v2.17); U-OD-51 AC #9 PARTIAL-LANDED (OD plan v2.18). Distinct units, distinct sessions. | (1) verify the materializable subset verbatim against cited specs; (2) check downstream consumes nothing from the blocked surface; (3) HALT + surface readings to operator; (4) on ruling: partial-land + RESOLVED Class-1 record + plan revision striking the AC. | memory `[[halt-route-split-ac-pattern]]`; `[[spec-tension-record-pattern]]`. No prior workflow-doc home. |
| **PD-2** | **use-the-product-probe** | When the workspace has been in closure-ratification mode for an extended run (fork docs, sub-species catalogues, vacuous-second-conjunct bounded-defers), **file an end-to-end product probe before opening more closure arcs**. Drive the simplest meaningful workflow through the operator-facing surface against real providers; observe what is load-bearing vs ceremonially closed. Each defect surfaced is a fork doc with an empirical anchor (information value, not cost). | **≥4 independent probe arcs**: probe v1 (PR #79), v2 (PR #83), v3 (PR #84), v4 (PR #85), all 2026-05-29 — each surfaced ≥1 operator-facing defect the integration suite structurally could not. | Pick the simplest workflow touching LLM + state-ledger + audit + observability; drive it through `harness run`; split findings positive / structural (fork docs) / UX. Triggers: PARTIAL/RR/RETIRED ratio >80%; consecutive vacuous-second-conjunct closures; cumulative advisor applications >40; operator "is this complete?". | memory `[[use-the-product-probe-pattern]]`. Companion to PD-3. No prior workflow-doc home. |
| **PD-3** | **verification-shape: grep-for-presence ≠ verified-working-end-to-end** | Before any operator-opt-in PARTIAL → RETIRE-READY promotion OR RETIRE-READY → RETIRED close, verify all binding-chain stages **empirically**: (1) config field present; (2) bootstrap factory present + its I/O contract matches host/registry expectations; (3) **driver invocation succeeds end-to-end against a real (or in-process-real) substrate** — NOT "driver code references the bound field". Static presence (grep hits, type checks, import resolutions) is necessary but not sufficient for a criterion-B operational-MET claim. | **≥2 independent arcs**: L9-septies / U-RT-86 transport_config key-mismatch (batch-16, 2026-05-24 — grep passed all 3 stages; the e2e caught a 2-day-latent broken production path); H_T-CP-21 batch-15 DOWN-classification (corrective demotion when stage-(3) was grep-only-verified). | At promotion: confirm an e2e exists OR is scoped at the plan; if neither, stay PARTIAL (CP-21 DOWN precedent). At close: confirm the e2e exercised the **production** factory output, not a manual construction / stub. | **Cite-don't-relocate:** partial home at workspace `CLAUDE.md` §13.1 ("Completeness check before claiming sufficient … verify by execution, not unit tests"); memory `[[verification-shape-sharpened-grep-vs-e2e]]`. §7.5 catalogues the retirement-promotion specialization of the §13.1 always-on discipline. |
| **PD-4** | **plan-revision-against-not-yet-built-substrate** | When a plan-revision arc rescopes an atomic unit's ACs against substrate it assumes is LANDED, **empirically verify the substrate exists at HEAD before authoring the revision**. A revision that STRIKEs / reframes an AC against a phantom or not-yet-built downstream substrate is a silent X-AL-3 risk; the correct shape is HALT + Class-1 route + AC STRIKE on the verified gap. | **Single-unit-multi-rescope** (admissible under the v1.11 / v1.13 single-instance-at-first-cataloguing precedent; labelled honestly — NOT multi-arc-independent): U-RT-111 rescope chain v2.35 → v2.36 → v2.37 → v2.38 (2026-05-29), each STRIKE/reframe driven by an empirical-orientation finding that the assumed substrate (carrier fields, firing sites, engine-layer bodies) was absent at HEAD. | Pre-substantive empirical grep of the assumed substrate at HEAD; if absent, STRIKE the AC on the verified gap (do not synthesize the missing substrate — X-AL-3); capture any explicit derivation rule the spec is silent on at the AC body. | memory: none own-file (referenced across U-RT-111 change-notes). **SUPERSEDES** the U-RT-111 **v2.36 → v2.38** change-note framing of this pattern as a "§7.4.7.2 sub-species" — carried at each rescope (v2.36 cardinality 1→2, v2.37 2→3, v2.38 3→4 at workflow doc §7.4.7.2 per workspace `CLAUDE.md` §2.4) — see §3 (a). |

#### §7.5.3 OPEN accumulation discipline + parked candidates

Per the v1.9 §7.4.7.5 catalogue-accumulation precedent, §7.5 is **OPEN** (additive; PD-5+ MAY be surfaced at future workflow-doc revisions without v2.x major-revision routing). Naming convention: `PD-N` numbered form.

**Parked candidates (surfaced at the `R-600-pattern-bake-in-sweep` survey; fail the §7.5.1 gate at v1.14 — held OPEN pending an independent second arc):**

| Candidate | Why parked (gate failure) | Promotion trigger |
|---|---|---|
| `carried-fork-audit-before-cluster` | Instance-cardinality 1 — FF-2 + FF-3 are **both from the OD-7b arc** (one arc, two findings), not two independent arcs. | A second independent cluster-open arc exhibiting the same carried-fork-audit miss. |
| `impl-time-grounding-pass-pre-merge-revision` | Instance-cardinality 1 — PR #37 + PR #38 are the **same CP→IS cascade**. | A second independent pre-merge grounding-revision arc on an unrelated cascade. |
| `carrier-home-defect-pattern` | Clean instance is U-AS-31 (cardinality 1 for the wrong-axis-package→cycle shape specifically; the related U-CORE-01 / U-OD-00 / U-CP-00b forks route via PD-1, not this shape). | A second independent wrong-axis-package carrier-home fork. |
| `test-bypass-as-runtime-truth` | Cardinality not yet confirmed at ≥2 independent arcs. | A second independent instance of an integration test green for a runtime-rejected path. |
| `spec-prose-plan-body-drift` | Has a home at workspace `CLAUDE.md` §10.9 adversarial checklist (cite-don't-relocate; not §7.5-promotable until it needs workflow-grammar formalization beyond the checklist). | Workflow-grammar formalization need beyond the §10.9 checklist entry. |

#### §7.5.4 Cross-catalogue discriminator

Three distinct catalogues now co-exist; route a surfaced pattern to exactly one:

| Catalogue | Home | What it catalogues |
|---|---|---|
| §7.4.7.2 five-species enumeration | this doc | **Stale-carry-text disposition** closure-event-classes (a carry-text describes a defect-shape that no longer matches production/substrate state). |
| §7.5 process-discipline catalogue | this doc (NEW v1.14) | **Execution-process disciplines** (sequencing / verification / decomposition / discovery). |
| retirement-event-pattern catalogue (sub-species 7.*) | `.harness/retirement-event-pattern-catalogue.md` | **Retirement-event closure shapes** (operator-explicit-deferred-close-gate, gate-text-stale, retirement-ID-scoping, deployment-time-opt-in, **LANDED-substrate-pending-upstream-loop** = 7d, etc.). |

The discriminator preserves the v1.11 §1.2 cross-catalogue scope discipline. Example: `landed-substrate-pending-upstream-loop-substrate` is a **retirement-event closure shape** (it operates at the retirement-event closure layer) and was operator-ratified to the `.harness/` catalogue as sub-species 7d — it is therefore **NOT** catalogued at §7.5, even though the survey listed it as a strong Class-C candidate. (Double-homing it would re-litigate a ratified routing.) Its plan-revision-layer sibling — PD-4 `plan-revision-against-not-yet-built-substrate` — IS §7.5-shaped and lives here; the two are distinct by carry-substrate layer (retirement-event closure vs plan-revision authoring), per the `[[landed-substrate-pending-upstream-loop-substrate]]` memory "Distinct from" note.

---

## §2 Sections preserved verbatim at v1.14

Per delta-only convention + FM-2 no-extension discipline, the v1.14 amendment touches ONLY the NEW §1 §7.5 authoring + this §2 + §3 adjacent observations + filing footer. The following are PRESERVED VERBATIM at file-body layer:

- **§7.4.1–§7.4.6** fidelity-grammar (claim taxonomy / byte-exact / structural-fidelity / citation-only / sub-section-resolution / pre-emission audit gate) — unchanged; §7.5 is a sibling, not an amendment to §7.4.
- **§7.4.7.1–§7.4.7.6** stale-carry-text disposition discipline (incl. the v1.10 species-3 catalogue + v1.11 species-5 + v1.12 species-3 10th + v1.13 species-2 first) — unchanged; §7.5 does NOT touch §7.4.7.
- **§7.1 / §7.2 / §7.3** versioning scheme / revision recording / revert discipline — unchanged.
- **v1.13 §1 + §2 + §3 + §4** + **v1.12 / v1.11 / v1.10 / v1.9 / v1.8 lineage sections** — PRESERVED VERBATIM.

---

## §3 Adjacent observations (surfaced as findings; NOT patched per FM-2)

(a) **PD-4 supersedes the U-RT-111 v2.36 → v2.38 §7.4.7.2-sub-species framing.** The U-RT-111 runtime-plan change-notes framed `plan-revision-against-not-yet-built-substrate` as a "§7.4.7.2 sub-species" across **three consecutive rescopes** — v2.36 ("cardinality 1→2"), v2.37 ("2→3"), v2.38 ("3→4"), all "at workflow doc §7.4.7.2" per workspace `CLAUDE.md` §2.4. v1.13 §3(a) — authored later and the actual workflow doc — discriminated the pattern as **NOT-§7.4.7.2-shape** (it is plan-revision authoring discipline, not stale-carry-text disposition) and routed it to a NEW catalogue. v1.14 §7.5.2 PD-4 is that catalogue home. The v2.36 → v2.38 framing is **SUPERSEDED**; downstream readers apply the §7.5 routing. The runtime-plan v2.36 file text is preserved verbatim per delta-only-plan-chain convention (this §3 (a) is the canonical-reading disposition; no plan-file edit owed).

(b) **`landed-substrate-pending-upstream-loop-substrate` is deliberately EXCLUDED from §7.5.** Per §7.5.4 + its operator-ratified routing to the `.harness/` retirement-event-pattern catalogue as sub-species 7d (per the memory routing-refresh note 2026-05-29 + operator AskUserQuestion option 1). The `R-600-pattern-bake-in-sweep` survey §1 listed it as a strong Class-C candidate, but the survey's disposition column did not capture the prior routing; the §7.5.1 gate condition 3 (no canonical home elsewhere) excludes it. Catalogued for observation.

(c) **§7.5 OPEN catalogue at v1.14 publication.** Four disciplines seeded (PD-1 through PD-4); five candidates parked at §7.5.3 pending an independent second arc. Future workflow-doc revisions MAY promote parked candidates (on independence confirmation) or surface new disciplines, per §7.5.3 + the v1.9 §7.4.7.5 accumulation precedent.

(d) **PD-4 cardinality honesty.** PD-4 is the only seeded discipline at single-unit-multi-rescope cardinality (all instances U-RT-111). It is admitted under the v1.11 species-5 / v1.13 species-2 single-instance-at-first-cataloguing precedent and labelled as such at §7.5.2 — NOT as multi-arc-independent. A second independent arc (a different unit exhibiting plan-revision-against-not-yet-built-substrate) would strengthen it; catalogued for observation.

(e) **Cross-catalogue scope discipline preserved.** v1.11 §1.2 + v1.13 §3(e) cross-catalogue discriminators are PRESERVED VERBATIM and extended at §7.5.4 to the three-catalogue case. v1.14 does NOT touch the §7.4.7.2 enumeration or the retirement-event-pattern catalogue.

---

## Filing footer

| Field | Value |
|---|---|
| Version | v1.14 (Catalogue-establishing substantive amendment — NEW §7.5 Process-discipline catalogue under §7, sibling to §7.4; 4 disciplines seeded PD-1..PD-4 + OPEN accumulation clause + 5 parked candidates; follows the v1.9 §7.4.7 framework-establishing precedent; v1.13 + v1.12 + v1.11 + v1.10 + v1.9 + v1.8 file body PRESERVED VERBATIM per delta-only convention) |
| Trigger | `R-600-workflow-v1-14-amendment` (roadmap §5.6) operator-authorized 2026-06-01; evidence base = `R-600-pattern-bake-in-sweep` survey (PR #196) + v1.13 §3(a) forward-routing |
| Supersedes | v1.13 §3(a) forward-routing of the plan-revision pattern (CLOSED at §7.5.2 PD-4) + the U-RT-111 v2.36 "§7.4.7.2 sub-species" framing of PD-4 (per §3 (a)); ALL other v1.13 + v1.12 + v1.11 + v1.10 + v1.9 + v1.8 sections PRESERVED VERBATIM |
| Scope of revision | SUBSTANTIVE: NEW §1 (§7.5 + §7.5.1–§7.5.4) + §2 + §3 + footer. ZERO C-*-NN contract change; ZERO §7.4 / §7.4.7 amendment; ZERO retirement event filing; ZERO production code change; ZERO cross-axis cascade. Pure workflow-grammar canonicalization. Co-publication: workspace `CLAUDE.md` §2.1 governance row bump + clearance marker |
| Cross-axis cascade | ZERO. v1.14 is workflow-grammar canonicalization; no per-axis spec / plan / CXA / production code touch |
| Authority anchor | v1.13 §3(a) forward-routing + `R-600-pattern-bake-in-sweep.md` §2 recommendation + v1.9 §7.4.7.5 catalogue-accumulation precedent + advisor pre-substantive consultation 2026-06-01 (per-candidate inclusion gate; v1.9 framework-precedent over single-focus; PD-4 supersession + single-unit-multi-rescope honesty; two candidates parked for independence; landed-substrate exclusion confirmed) |
| Predecessor | v1.13 (§7.4.7.2 species-2 sub-species `2.strike-revision-on-refined-second-tier-reason`) |
| Successor | (none — current canonical) |
| Date | 2026-06-01 |

---

*End of `Project_Workflow_v1_14.md` (delta over v1.13). v1.8 + v1.9 + v1.10 + v1.11 + v1.12 + v1.13 PRESERVED VERBATIM as historical anchors per delta-only-spec-file convention.*
