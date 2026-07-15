# R-600-pattern-bake-in-sweep — survey artifact

**Entry:** `R-600-pattern-bake-in-sweep` (roadmap §5.6) — *Sweep workspace memory for pattern candidates ready for workflow-doc promotion.*
**Posture:** mode-agnostic recurring sweep; design-substrate amendment only when a candidate clears the §7.5 gate. **Cadence:** ~every 10 PRs or operator-discretion.
**Latest status:** **ACTIVE-SURVEYED (cadence-8, 2026-07-14)** — cadence-8 survey complete (both `must_pass` met); promoted `mutation-probe-load-bearing-witness` as **PD-8 mutation-probe-as-load-bearing-witness** in `design-substrate/Project_Workflow_v1_18.md`, clearance marker `.harness/clearance/Project_Workflow-v1_18-cleared-2026-07-14.md` — the card-frontier token flagged (not yet promoted) at cadence-7 cleared the §7.5.1 gate once it consolidated into its own named memory entry. Prior: cadence-7 was a legitimate zero-promotion cadence (this line was previously stale here, still reading "cadence-6" even though the cadence-7 section below had already closed — corrected as part of this same cadence-8 arc); cadence-5 promoted `disposition-label-is-a-claim-verify-against-spec` as **PD-7 disposition-label-is-a-claim** in `design-substrate/Project_Workflow_v1_17.md`, clearance marker `.harness/clearance/Project_Workflow-v1_17-cleared-2026-07-12.md`. R-600 remains a recurring lane; next run only after the cadence trips again (~10 PRs) or a concrete new candidate reaches independent instance-cardinality >=2.

**Method.** Read-only enumeration of the auto-memory store at `/Users/robertrhu/.claude/projects/-Users-robertrhu-Projects-arhugula-v2/memory/` (152 files): grep raw `[[wiki-link]]` tokens across all file bodies; count per-token cardinality (total refs + distinct referencing files). 569 total refs / 155 distinct tokens → **104 at cardinality ≥2**, 51 at cardinality 1.

> **Metric caveat (read before using the counts).** The "cardinality" / "card." numbers in this artifact are **`[[...]]` citation-count** — how often a token is *referenced* across the store — which is a **salience proxy**, NOT the workspace's **promotion-cardinality** (the number of *distinct empirical instances*, per §12.5.1 + every change-note's "cardinality 1; awaits second instance"). The two diverge: e.g. `strike-revision-on-refined-second-tier-reason` shows 5 citations here but had **instance-cardinality 1** at its v1.13 promotion. Citation-count over-counts, so the `≥2` filter is *over-inclusive* (it misses no genuine candidate) but the numbers must not be read as instance-cardinality. **True promotion-cardinality must be confirmed per-candidate at the v1.14 absorption arc** (the strong Class-C candidates below independently attest instance-cardinality ≥2 in their own change-notes — that's the gate, not the citation count).

---

## §1 — `must_pass` #1: all cardinality-≥2 `[[pattern]]` entries identified

The 104 cardinality-≥2 tokens, **bucketed by class**. Only **Class C (discipline / closure-event-class)** entries are workflow-doc-promotion candidates; Classes A/B are project-state bookkeeping, not promotable disciplines.

### Class A — project-state records (NOT promotable; retirement/PR/fork/finding bookkeeping)

`phase-7-bootstrap-status` (9), `fork-cp-is-wiring-gaps` (9), `finding-runtime-config-loader-unreachable-sub-configs` (8), `design-substrate-divergence` (8), `fork-u-rt-44-workflow-loop-drain` (7), `fork-price-table-ref-substitution-retirement` (7), `fork-meta-arch-cp-spec-renumbering-drift` (7), `finding-mech-beta-stub-bodies-vs-env-gate` (7), `workflow-v1-12-species-3-extension-and-audit-template-c` (6), `spec-tension-record-pattern` (6), `h-t-rt-35-retired-batch-46` (6), `h-t-cp-16-17-retire-ready-gate-runtime-composer-arcs` (6), `fork-u-rt-68-retry-wrap-and-bootstrap-wiring-gap` (6), `finding-bootstrap-stage-is-1-requires-skills-path-binding` (6), `h-t-rt-35-retire-ready-batch-45` (5), `h-t-od-1-retired-batch-37` (5), `fork-h-t-cp-18-phantom-retirement-cite` (5), `finding-bootstrap-stage-3a-cp-clients-keyring-fallback-absent` (5), `u-rt-111-ac-11-strike-third-disambiguator-gap` (4), `pr-71-pr-68-reading-d-ratification-batch-45` (4), `h-t-od-7-retired-batch-38` (4), `h-t-od-3-retire-ready-batch-36` (4), `h-t-od-3-partial-batch-34` (4), `fork-validator-composer-arc-stage-4-absence` (4), `fork-trace-storage-pathclass-gap` (4), `fork-sandbox-decision-policy-phantom-cite` (4), `fork-provider-construction-allowlist-semantic` (4), `class_1_tension_u_rt_59_cp_to_od_audit_write_gap` (4), `class_1_tension_u_rt_59_async_sync_step_dispatcher` (4), `advisor-43rd-application-reading-b-then-grep-verification` (4), + the full set of `h-t-*-retired/partial/retire-ready-batch-*`, `pr-NN-*`, `fork-*`, `finding-*`, `u-rt-111-ac-*`, `u-od-40-*`, `phase-*-*`, `path-alpha-*`, `tenant-id-binding-lift-cp-v1-22`, `retirement-batch-11-*`, `backlog-steady-state-post-batch-41`, `ac-5-mech-alpha-reframe-precedent`, `mech-beta-ac-bundle-pr-stack`, `checkpoint-20260529-040236` (each 2–3). *(~85 entries — instance/state records; their value is provenance, not reusable discipline.)*

### Class B — already-canonical disciplines (a home already exists; promotion redundant)

| pattern | card. | existing home |
|---|---|---|
| `advisor-before-substantive-work-for-cross-axis-blockers` | **81** | CLAUDE.md §13.1 (always-on) + §10.4. The workspace's dominant meta-discipline; canonical in root CLAUDE.md. Workflow-doc promotion **optional** (cite, don't relocate). |
| `feedback-checkpoint-remaining-work-is-advisory-not-authoritative` | 2 | CLAUDE.md §12.5.2 + §12.5.4 |
| `feedback-background-agent-no-unilateral-paid-calls-or-secret-relocation` | 2 | CLAUDE.md memory + behavioral feedback (honored) |
| `project-roadmap-v1-deterministic-next-action` | (idx) | CLAUDE.md §12 |

### Class C — discipline / closure-event-class candidates (the actual promotion set)

| pattern | card. | §7.4.7-shape? | disposition |
|---|---|---|---|
| `strike-revision-on-refined-second-tier-reason` | 5 | **YES — §7.4.7.2 species-2** | ✅ **ALREADY PROMOTED** at workflow v1.13 §1.1 (PR #63). No action. |
| `verification-shape-sharpened-grep-vs-e2e` | **34** | NO (verification discipline) | **Strong candidate** — NOT stale-carry-text. Verify each binding-chain stage empirically; e2e (not grep) gates retirement transit. Partially echoed at CLAUDE.md §13.1 "Completeness check by execution." → distinct §7.5/§7.4.7.X home. |
| `halt-route-split-AC-pattern` (+ `…-ac-pattern` casing dup) | **37** (25+12) | NO (AC-decomposition discipline) | **Strong candidate** — bundle materializable + unmaterializable ACs: partial-land the materializable, file Class 1 + STRIKE the rest. → distinct catalogue. Also a **memory-hygiene dup** (see §3). |
| `plan-revision-against-not-yet-built-substrate` | 5 | NO (plan-revision-authoring discipline) | **Strong candidate** — explicitly routed at workflow v1.13 §3(a) as a NON-§7.4.7.2 pattern needing a distinct catalogue. Validated here at cardinality 5 (U-RT-111 v2.35→v2.38 rescope chain). |
| `LANDED-substrate-pending-upstream-loop-substrate` (+ `…-sub-species`) | 6+2 | NO (substrate/consumer-lifecycle) | **Strong candidate** — substrate landed but consumer/loop-substrate pending upstream; 4-in-24h cardinality. → distinct catalogue. |
| `use-the-product-probe` (+ `…-pattern`) | 6+3 | NO (discovery discipline) | **Strong candidate** — file an end-to-end product probe before opening more closure arcs. Named in `[[workflow-v1-14-deferred-2026-05-29]]` as the lead non-§7.4.7.2 candidate. Also a **slug-split dup** (§3). |
| `spec-prose-plan-body-drift-pattern` | 5 | borderline (drift) | Candidate — drift between spec prose and plan body; land against plan body, file Class 1. Already named in CLAUDE.md §10.9 adversarial checklist. → cite or §7.4.7.X. |
| `carrier-home-defect-pattern` | 4 | NO (cross-axis typing) | Candidate — cross-axis type in one axis package = Class 1 cycle; re-home to harness-core. Architectural discipline. |
| `test-bypass-as-runtime-truth` | 4 | NO (test/runtime asymmetry) | Candidate — an integration test green for a runtime-rejected path is a signal, not coverage. |
| `carried-fork-audit-before-cluster` | 3 | NO (pre-cluster audit) | Candidate — audit each axis plan's §0.6/§0.7 carry-forwards before opening a cluster. |
| `impl-time-grounding-pass-pre-merge-revision` | 3 | NO (grounding discipline) | Candidate — verify type field-sets / symbol existence pre-merge; force-push in-flight revision rather than carry stale rows. |
| `multi-arc-convergence-via-bounded-defer-blocker-set-species-candidate` | 3 | NO (convergence) | Candidate (self-labelled "species candidate"). |
| `v2-33-cascade-target-correction-sub-species-candidate` | 3 | NO (cascade-target) | Candidate (self-labelled "sub-species candidate"). |
| `deferred-to-discretion-clauses-pattern` | 2 | borderline | Weak candidate — spec "deferred to implementation discretion" clauses become latent gaps. |

---

## §2 — `must_pass` #2: promotion candidates evaluated against §7.4.7 catalogues

**Result of the evaluation: ZERO new §7.4.7.2 (stale-carry-text disposition) sub-species are owed this sweep.**

This is from an **independent shape-scan of all 104 cardinality-≥2 tokens at current HEAD** (not a deferral to the v1.13 self-audit, which was at PR #62 state ~130 PRs ago): each ≥2 token was classified (Class A project-state record / Class B already-homed / Class C discipline) and the Class-C set evaluated against the §7.4.7.1 carry-text taxonomy. No token — in Class A or Class C — exhibits a NEW stale-carry-text closure-event-class absent from the v1.10–v1.13 catalogue. The v1.13 audit is *corroborated*, not relied upon.

- §7.4.7.2 species 1 / 4 — EMPTY; no stale-carry refinements surfaced at ≥2.
- §7.4.7.2 species 2 — its single sub-species (`strike-revision-on-refined-second-tier-reason`) is **already catalogued at v1.13**. No second species-2 sub-species surfaced.
- §7.4.7.2 species 3 (10 sub-species) / species 5 ({5.1, 5.2}) — no new sub-species surfaced.

**The load-bearing finding** is the inverse: the strong Class-C candidates (`verification-shape-sharpened-grep-vs-e2e` 34, `halt-route-split-AC-pattern` 37, `plan-revision-against-not-yet-built-substrate` 5, `LANDED-substrate-pending-upstream-loop-substrate` 6, `use-the-product-probe` 9) are **all NON-§7.4.7-shape** — they are verification / AC-decomposition / plan-revision / discovery disciplines, **not** stale-carry-text disposition closure-events. §7.4.7 cannot absorb them without degrading taxonomy coherence (the exact failure mode flagged at v1.13 §3(a) + (c) and ratified by the operator at the v1.14 deferral).

**This is the third independent surfacing of the same structural gap** (v1.13 §3(a) → v1.14 deferral 2026-05-29 → this sweep). The catalogue evidence now stands at strong cardinality. **Recommendation for the v1.14/v1.15 amendment arc:** author a **NEW process-discipline catalogue distinct from §7.4.7** — either a new `§7.5 process-discipline catalogue` or a new `§7.4.7.X plan-revision/verification-discipline` sibling — seeded with the 5–8 strong Class-C candidates above. That is a design-phase, operator-discretion, spec-writer + advisor + (conditional council) arc per `R-600-workflow-v1-14-amendment` — **out of scope for this mode-agnostic sweep.**

---

## §3 — Adjacent finding: memory-hygiene (slug/casing duplicates + index cap)

Surfaced incidentally; routes to the owed `MEMORY.md` audit (dashboard line 29 — index over 24.4KB cap), not to the workflow doc:

| canonical file | duplicate token(s) seen | note |
|---|---|---|
| `halt-route-split-ac-pattern.md` | `[[halt-route-split-AC-pattern]]` (25!) vs `[[halt-route-split-ac-pattern]]` (12) | Case split; the high-card token has no own-file. Normalize references to the lowercase slug. |
| `use-the-product-probe-pattern.md` | `[[use-the-product-probe]]` (6, no file) | Slug split. |
| `fork-u-rt-44-workflow-loop-drain.md` | `[[fork-u-rt-44]]` (3, no file) | Slug split. |
| `fork-h-t-cp-19-default-gate-level-spec-extension.md` | `[[h-t-cp-19-default-gate-level-spec-extension]]` (1, no file) | Slug split. |
| `landed-substrate-pending-upstream-loop-substrate-sub-species.md` | `[[LANDED-substrate-pending-upstream-loop-substrate]]` (6, no file) | Case + slug split. |

Plus `class_*_tension_*` / `class_*_drift_*` tokens (cardinality 2–3) that reference `.harness/` fork-doc paths, not memory files — expected (cross-store links), not dups.

---

## §4 — Closure disposition

- **`must_pass` #1** (all cardinality-≥2 identified): ✅ §1.
- **`must_pass` #2** (each promotion candidate evaluated against §7.4.7): ✅ §2 — result is "no §7.4.7 absorption owed; a NEW non-§7.4.7 catalogue is the correct home."
- **Entry status:** **ACTIVE-SURVEYED.** Full closure (`close_shape: substrate-amendment, artifact: Workflow doc revision`) is owed to the deferred `R-600-workflow-v1-14-amendment` and gated on operator scope authorization. This artifact is the durable candidate evidence base that arc consumes.
- **No design-substrate edit, no clearance marker** (mode-agnostic process-substrate only).
- **Next cadence run:** ~10 PRs out, or when a new Class-C discipline crosses cardinality 2.

---
---

# Cadence-2 run — 2026-06-02 (HEAD `2e60741`, post-PR-242)

**Cadence trigger.** 46 commits merged since the cadence-1 sweep (`d7574b3` → `2e60741`) — well past the ~10-PR interval. The bulk were Surface-XI dashboard / ops / roadmap-refresh PRs (R-XI-* + R-IF-roadmap-refresh), not Phase-7 execution arcs, so the new-discipline yield is expected to be low.

**State-shift since cadence-1 (the load-bearing reconciliation).** Cadence-1's closure was "owed to the **deferred** `R-600-workflow-v1-14-amendment`." **That amendment is now RESOLVED** (PR #201, 2026-06-01): `design-substrate/Project_Workflow_v1_14.md` authored a NEW **§7.5 Process-discipline catalogue** that absorbed cadence-1's strong Class-C set:

| cadence-1 strong candidate | v1.14 disposition |
|---|---|
| `halt-route-split-AC-pattern` (card 37) | ✅ **PD-1** |
| `use-the-product-probe` (card 9) | ✅ **PD-2** |
| `verification-shape-sharpened-grep-vs-e2e` (card 34) | ✅ **PD-3** (cite-don't-relocate; specializes CLAUDE.md §13.1) |
| `plan-revision-against-not-yet-built-substrate` (card 5) | ✅ **PD-4** (honestly labelled single-unit-multi-rescope) |
| `LANDED-substrate-pending-upstream-loop-substrate` (card 6) | **Deliberately NOT §7.5** — routed to `.harness/` 7d sub-species per the §7.5.4 carry-substrate-layer discriminator (retirement-event closure ≠ plan-revision authoring). |
| `carrier-home-defect-pattern` (card 4) | **PARKED** at §7.5.3 (instance-cardinality 1: U-AS-31). |
| `spec-prose-plan-body-drift` (card 5) | **PARKED** at §7.5.3 (cite-don't-relocate; home at CLAUDE.md §10.9). |

**→ Cadence-1's recommendation is fully executed; the prior cycle is discharged.** This cadence-2 run is therefore a *fresh* survey at current HEAD, not a re-statement of cadence-1.

**Method (identical to cadence-1).** Read-only `[[wiki-link]]` enumeration of the auto-memory store (**161 files**, was 152): **579 total refs / 166 distinct tokens → 104 at cardinality ≥2** (unchanged count), 62 at cardinality 1. The +9 files / +11 tokens / +10 refs since cadence-1 landed **almost entirely at cardinality 1** — so the card-≥2 promotion frontier barely moved. *(Same metric caveat as cadence-1 applies: these are citation-counts, a salience proxy — NOT instance-cardinality. Confirm promotion-cardinality per-candidate at the v1.15 absorption arc.)*

---

## C2-§1 — `must_pass` #1: cardinality-≥2 frontier delta vs cadence-1

The 104-token card-≥2 set is **substantially unchanged**.

**Residual computation (verified, not eyeballed — the PD-3 grep-presence-≠-verified discipline applied to this survey's own claim).** Cadence-1's Class-A list is abbreviated in the doc ("~85 entries … + the full set of …"), so a byte-exact set-diff is not recoverable; instead the "newly-crossed" claim is backed by a residual filter at current HEAD: take the 104 card-≥2 tokens, drop the obvious bookkeeping prefixes (`fork-` / `h-t-` / `pr-` / `finding-` / `class_` / `u-rt-` / `u-od-` / `phase-` / `checkpoint-` / `advisor-NN-` / `workflow-v1-1{1,2}` / `path-alpha` / `mech-beta` / `ac-5-` / `tenant-id` / `retirement-batch` / `backlog-` / `design-substrate-divergence` / `spec-tension-record`), then subtract every token already in cadence-1's Class-B + Class-C tables and the Class-A infra-recipe tokens (`uv-workspace-members-install`, `secrets-via-just-recipe-not-direct-sourcing`). **Residual = exactly two tokens: `{r-cxa-seam-wiring-is-producer-discovery, bash-cwd-reverts-to-project-root-not-worktree}`.** Of those, `bash-cwd-…` (card 2) is a harness env recipe (Class A — *"Bash commands may run at project root, not the worktree"*), not a promotable discipline. So the only token that **newly crossed into the card-≥2 frontier as a Class-C discipline** is:

| pattern | card. (cite) | §7.4.7-shape? | §7.5-shape? | disposition |
|---|---|---|---|---|
| `r-cxa-seam-wiring-is-producer-discovery` | **3** | NO | **YES (discovery/grounding-sequencing)** | **NEW PD-5 candidate** — see C2-§2. |

**"Newly crossed" is airtight on provenance, not just count:** producer-discovery's lesson originated at **PR #220 (R-CXA-1, 2026-06-01)**, which *postdates* cadence-1's **PR #195 / `d7574b3`** baseline — so the token genuinely did not exist at the cadence-1 sweep; it was not present-and-missed. No cadence-1 Class-C candidate changed bucket except via the v1.14 absorption above.

**A grounding-first discipline FAMILY is consolidating at cardinality 1** (below the ≥2 frontier, surfaced for the v1.15 arc's awareness — *not yet promotion-ready*):

| pattern | card. (cite) | shape |
|---|---|---|
| `grounding-reveals-claude-closeable-slice-close-honestly` | 1 | complement of producer-discovery: ground → real Claude-closeable slice exists → build it but close HONESTLY (literal must_pass met ≠ titled intent met; §10.5 overclaim trap) |
| `wrong-version-read-delta-only-baseline` | 1 | canonical = last full re-table + subsequent cell-amendments, never the delta-only baseline |
| `porting-old-branch-wip-may-be-superseded` | 0–1 | before porting old-branch WIP onto main, check newer parallel main work via directional diff + merge chronology |
| `feedback-verify-observation-layer-before-concluding-defect` | 1 | "no entries found" ≠ defect; check the sink/marker layer first |

These four share a **verify-the-ground-before-you-author/conclude** meta-shape with the PD-5 candidate. Each is individually cardinality-1 (awaits a 2nd instance), but the cluster's coherence is itself a v1.15 design question (consolidate into one "grounding-first" PD vs separate PDs vs cite-under-PD-2/PD-3).

---

## C2-§2 — `must_pass` #2: candidates evaluated against §7.4.7 **AND §7.5**

> **must_pass-text staleness flag (a §7.4.7-style stale-carry observation, fittingly).** The roadmap `must_pass` #2 text reads *"each promotion candidate evaluated against §7.4.7 catalogues"* — authored **pre-v1.14**, when §7.5 did not exist. As of v1.14 the evaluation must span **§7.4.7 (stale-carry-text) AND §7.5 (process-discipline)** — and the sole cadence-2 candidate lands in §7.5, not §7.4.7. The must_pass text should be refreshed to *"…against the §7.4.7 + §7.5 catalogues"* at the next roadmap touch (reconciled in the roadmap §5.6 update co-published with this run).

**§7.4.7 (stale-carry-text):** ZERO new sub-species owed. Consistent with cadence-1 — no card-≥2 token (new or existing) exhibits a stale-carry-text closure-event-class absent from the v1.10–v1.13 catalogue. The cadence-1 finding stands corroborated at a 4th independent surfacing.

**§7.5 (process-discipline) — the one candidate:**

**`r-cxa-seam-wiring-is-producer-discovery` → PD-5 CANDIDATE (recommend; do NOT self-promote).** Statement: a post-Phase-8 roadmap lever phrased *"wire a production caller for `emit_X`"* looks mechanical but is usually **producer-discovery** — grep the seam's real emitter callers + the scoped source path the event was designed for + whether the event's required fields have a production source; if the producer doesn't exist and the fields can't be sourced, **defer (Reading D / don't-wire)** rather than ship a hollow, fingerprint-defeated seam.

Run against the §7.5.1 inclusion gate (all three must hold; verified per-candidate, NOT by citation count):

1. **Instance-cardinality ≥2 — QUALIFIED, with an honesty caveat (mirrors PD-4's labelling).** The memory self-claims "≥3 (R-CXA-1, U-RT-111, R-CXA-4)," but per the cadence-1 metric caveat that must be discounted:
   - **R-CXA-1 + R-CXA-4 are same-day, same-session, same-lesson** (both 2026-06-01 CXA seam grounding) → this is *single-arc-multi-seam*, analogous to PD-4's honestly-labelled "single-unit-multi-rescope … NOT multi-arc-independent."
   - **U-RT-111 is plausibly DOUBLE-COUNTED with PD-4.** PD-4's entire lineage IS the U-RT-111 v2.35→v2.38 "substrate not built" chain; the producer-discovery memory describes U-RT-111 as "firing-site-precedes-wiring / substrate not built" — the *same underlying instance* viewed through the seam-producer lens rather than the plan-revision lens. If shared, producer-discovery's genuinely-*independent* arcs collapse toward **1 distinct arc** (the CXA grounding session).
   - **Honest framing:** present PD-5 as cardinality-qualified (the v1.15 arc confirms a genuine 2nd independent arc before promoting, exactly as the §7.5.1 gate requires), NOT as settled ≥3.
2. **Genuinely §7.5-shaped — YES.** A discovery / pre-authoring-grounding sequencing discipline; not stale-carry-text (§7.4.7) and not fidelity-claim grammar (§7.4.1–6).
3. **No existing workflow-doc home — OPEN QUESTION for v1.15 (do not resolve here).** The discipline cites `[[use-the-product-probe-pattern]]` (PD-2) and `[[test-bypass-as-runtime-truth]]`, and is adjacent to PD-3 (verification-shape: grep-presence ≠ verified-working). The v1.15 arc must decide whether producer-discovery is a **distinct PD-5** (the "wire a production caller" seam-completion lever is a recognizable standalone shape) or a **cite-don't-relocate specialization** that cross-references PD-2/PD-3. The surrounding grounding-first family (C2-§1) bears on this: PD-5 may be authored as the *first concrete instance* of a broader "grounding-before-authoring" discipline that the card-1 siblings later extend.

**Net §7.5 recommendation for the v1.15/v1.16 amendment arc:** one PD-5 candidate (`producer-discovery`), cardinality-qualified pending a 2nd genuinely-independent arc, with the home/consolidation question (standalone vs cite-under-PD-2/3 vs grounding-first-family head) left to that design-phase arc. As with cadence-1, **this mode-agnostic sweep does not author the workflow doc** — promotion is a spec-writer + advisor (+ conditional council) design-phase arc, operator-discretion timing.

---

## C2-§3 — parked-candidate re-check + memory-hygiene (still routed elsewhere)

**Parked §7.5.3 candidates — no promotion trigger fired this cadence:**
- `carrier-home-defect-pattern` (card 4 cite): still instance-cardinality 1 (U-AS-31); no 2nd independent wrong-axis-package carrier-home fork surfaced since v1.14. **Stays parked.**
- `spec-prose-plan-body-drift` (card 5 cite): no workflow-grammar-formalization need beyond the CLAUDE.md §10.9 checklist surfaced. **Stays parked (cite-don't-relocate).**

**Memory-hygiene dups — STILL PRESENT and STILL UN-OWNED (carried unaddressed from cadence-1 §3).** No R-NNN entry owns this; it is routed in cadence-1 §3 to a "MEMORY.md audit" that does not exist as a roadmap action. The case/slug splits persist verbatim:
- `[[halt-route-split-AC-pattern]]` (25) vs `[[halt-route-split-ac-pattern]]` (12) — case split; the high-card token still has no own-file.
- `[[use-the-product-probe]]` (6) vs canonical `use-the-product-probe-pattern.md` (4) — slug split.
- `[[fork-u-rt-44]]` (3) vs `fork-u-rt-44-workflow-loop-drain.md` — slug split.
- `[[LANDED-substrate-pending-upstream-loop-substrate]]` (4) vs `landed-substrate-pending-upstream-loop-substrate-sub-species.md` (2) — case + slug split.

**MEMORY.md index size:** 24,297 bytes (167 lines) — just under the ~24.4 KB cap flagged at cadence-1, but still near-limit and growing.

> **CLOSE-OUT (2026-06-02, operator-approved follow-on — filed as roadmap `R-600-memory-hygiene-normalization`, RESOLVED).** The dup-normalization was *executed* this arc: the 5 dup/case-split tokens above were renamed to their canonical own-file slugs via literal bracketed-token replacement (pre-edit backup taken). Verified: all 5 old tokens → 0; canonicals absorbed every count (`halt-route-split-ac-pattern` 12→37, `use-the-product-probe-pattern` 4→10, `fork-u-rt-44-workflow-loop-drain` 7→10, `landed-…-sub-species` 2→6, `fork-h-t-cp-19-…` 12→13); total `[[..]]` ref-count unchanged at 579 (pure rename, recall improved); 30 files token-only. **NOTE for the next cadence:** post-normalization the store is **161 distinct tokens / 100 at card≥2** (was 166 / 104 — five dup tokens eliminated, four of them card≥2) — the *pre*-normalization 166/104 figures above are the accurate point-in-time snapshot at the cadence-2 sweep HEAD and are preserved as such. Index-cap **pruning** was deliberately left OUT of scope (judgment-heavy; under cap at close) → watch item, not done.

---

## C2-§4 — Closure disposition (cadence-2)

- **`must_pass` #1** (cardinality-≥2 frontier identified + delta vs cadence-1): ✅ C2-§1.
- **`must_pass` #2** (candidates evaluated against §7.4.7 **+ §7.5**): ✅ C2-§2 — result: ZERO new §7.4.7 owed; **one §7.5 PD-5 candidate** (`producer-discovery`, cardinality-qualified). must_pass-text staleness flagged + reconciled in the roadmap update.
- **Entry status:** **ACTIVE-SURVEYED (cadence-2).** Cadence-1's gating dependency (`R-600-workflow-v1-14-amendment`) is RESOLVED, so the *prior* cycle is fully discharged. The cadence-2 candidate (PD-5) is owed to a **future v1.15/v1.16 workflow-doc amendment** — a design-phase, operator-discretion, spec-writer + advisor arc (NOT yet opened; needs a 2nd genuinely-independent producer-discovery arc to clear the §7.5.1 cardinality gate).
- **No design-substrate edit, no clearance marker** (mode-agnostic process-substrate only). The roadmap §5.6 entry resume note is reconciled (stale "owed to DEFERRED amendment" → cadence-2 state) in the same PR.
- **Next cadence run:** ~10 PRs out, or when a 2nd producer-discovery arc (or any grounding-first-family member) crosses instance-cardinality 2.

---
---

# Cadence-3 run — 2026-06-10 (HEAD `a7f7d1f4`, post-PR-466)

**Cadence trigger.** 248 commits merged since the cadence-2 sweep (`2e60741` → `a7f7d1f4`) — well past the ~10-PR interval. The merged interval includes the R-411/R-412 host/runtime and managed sandbox work, R-810/R-820/R-830 managed integration arcs, R-CXA-1/R-CXA-2 implementation/back-flow, R-IF-112 overlay closeout, dashboard currentness discipline, and the post-#447 terminating refresh.

**Method.** Read-only `[[wiki-link]]` enumeration of the auto-memory store at `/Users/robertrhu/.claude/projects/-Users-robertrhu-Projects-arhugula-v2/memory/` (**199 files**): **713 total refs / 192 distinct tokens → 124 at cardinality >=2**. As in cadence-1 and cadence-2, these are citation-counts, not promotion-cardinality; promotion decisions below use per-candidate independence and home checks.

## C3-§1 — `must_pass` #1: cardinality>=2 frontier identified

Top unchanged already-homed signals remain dominant: `advisor-before-substantive-work-for-cross-axis-blockers` (87), `halt-route-split-ac-pattern` (41), and `verification-shape-sharpened-grep-vs-e2e` (40). The frontier change relevant to workflow promotion is the grounding-first family:

| pattern | refs / files | cadence-2 disposition | cadence-3 disposition |
|---|---:|---|---|
| `r-cxa-seam-wiring-is-producer-discovery` | 9 / 8 | PD-5 candidate, parked for independence/home decision | Promoted as part of PD-5 grounding-first producer/slice discovery |
| `grounding-reveals-claude-closeable-slice-close-honestly` | 8 / 8 | card-1 family member below frontier | Promoted into the same PD-5 decision tree |
| `wrong-version-read-delta-only-baseline` | 3 / 3 | card-1 family member below frontier | Cite-under-PD-5; not a standalone PD |
| `post-phase-8-forward-tracking` | 5 / 4 | not a cadence-2 PD candidate | Cite-under-PD-5 for stale-authored-row grounding |

Other high-salience cadence-3 candidates were evaluated but not promoted:

- `hooks-codex-pilots-decorrelation-validated` / `codex-out-of-family-reviewer`: already have a workspace home in CLAUDE.md §13.1 and Codex review tooling; cite-don't-relocate.
- `promptfoo-no-api-skill-eval-loop` / `eval-harness-refused-as-governance-gate`: dev-tool/eval-governance surfaces, not workflow §7.5.
- `gitignored-work-belongs-in-main-not-reapable-worktree` / `bmad-runtime-gitignore-config-gotchas`: operational worktree/config hygiene; not broad enough for workflow-grammar promotion this cadence.

## C3-§2 — `must_pass` #2: candidates evaluated against §7.4.7 and §7.5

**§7.4.7:** ZERO new stale-carry-text disposition species surfaced. The cadence-1 and cadence-2 finding remains corroborated.

**§7.5:** The cadence-2 PD-5 candidate now clears the v1.14 §7.5.1 gate when framed as **grounding-first producer/slice discovery** rather than seam wiring alone:

1. **Instance-cardinality >=2 of independent arcs — PASS.** R-CXA seam producer discovery prevented hollow production-caller wiring; R-830 separated a declared backend slice from live-cloud gates; R-410/R-411/R-412 grounded sandbox/runtime provider feasibility before closure claims; post-Phase-8 roadmap/status refreshes repeatedly re-derived live closeable work from HEAD rather than trusting stale authored rows.
2. **Genuinely §7.5-shaped — PASS.** The rule is sequencing/discovery/verification: ground first, then classify the lever as already-built, buildable-slice, back-flow/defer, or exact live gate.
3. **No canonical home elsewhere — PASS with cite-don't-relocate.** PD-2 and PD-3 are adjacent but do not cover the full pre-authoring decision tree. CLAUDE.md §12 prevents parking; PD-5 prevents overclaiming and manufactured work.

**Promotion applied this arc:** `design-substrate/Project_Workflow_v1_15.md` adds **PD-5 grounding-first producer/slice discovery**. Clearance marker filed at `.harness/clearance/Project_Workflow-v1_15-cleared-2026-06-10.md`. Root `CLAUDE.md` and `.harness/claude-artifact-pointers.md` now point to workflow head v1.15.

## C3-§3 — Closure disposition (cadence-3)

- **`must_pass` #1** (cardinality>=2 frontier identified): ✅ C3-§1.
- **`must_pass` #2** (candidates evaluated against §7.4.7 + §7.5): ✅ C3-§2 — result: ZERO new §7.4.7 owed; one §7.5 PD-5 promoted at workflow v1.15.
- **Entry status:** **ACTIVE-SURVEYED (cadence-3)**. Cadence-2's PD-5 promotion debt is discharged. R-600 remains an ACTIVE recurring lane; next run only after the cadence trips again (~10 PRs) or a concrete new candidate reaches independent instance-cardinality >=2.

---
---

# Cadence-4 run — 2026-06-30 (HEAD `3177fab8`, post-PR-848)

**Cadence trigger.** More than 10 PRs merged since cadence-3 (`a7f7d1f4` / post-PR-466 → `3177fab8` / post-PR-848), including the full R-FS-1 close track, multiple R-FS-1 implementation arcs, Q1-Q4/D1/C1 closure arcs, Codex context-guard hardening, stale R-IF closure, and terminating refreshes. Cadence is therefore due.

**Method.** Read-only `[[wiki-link]]` enumeration of the auto-memory store at `/Users/robertrhu/.claude/projects/-Users-robertrhu-Projects-arhugula-v2/memory/` (**114 files**): **558 total refs / 101 distinct tokens → 72 at cardinality >=2**. The file count is lower than cadence-3's 199-file snapshot, so raw total/cardinality deltas are not interpreted as a trend; this run uses current token salience plus per-candidate independence/home checks.

## C4-§1 — `must_pass` #1: cardinality>=2 frontier identified

Top unchanged/already-homed signals remain dominant: `hooks-codex-pilots-decorrelation-validated` (45), `verification-shape-sharpened-grep-vs-e2e` (36), `grounding-reveals-claude-closeable-slice-close-honestly` (31), `advisor-before-substantive-work-for-cross-axis-blockers` (30), and `r-cxa-seam-wiring-is-producer-discovery` (20). The frontier change relevant to workflow promotion is the composed-chain / non-vacuity family:

| pattern | refs / files | cadence-3 disposition | cadence-4 disposition |
|---|---:|---|---|
| `full-chain-witness-not-half-proofs` | 20 / 15 | not a cadence-3 promoted entry | Promoted as PD-6 composed-chain non-vacuity witness |
| `built-but-vacuous-reground-ledger-asis` | 18 / 17 | reinforcing PD-5 grounding / non-vacuity signal | Cite-under-PD-5/PD-6; not a standalone PD this cadence |
| `test-bypass-as-runtime-truth-pattern` | 13 / 9 | parked/candidate at earlier cadence | Cite-under-PD-6 + PD-3; not standalone |
| `feedback-gate-only-on-meaningful-architecture-change` | 16 / 15 | operator behavioral guidance | Already active in session/AGENTS discipline; no workflow-doc entry |
| `subagent-landscape-reports-need-regrounding` | 15 / 12 | direct-source grounding signal | Reinforces PD-5 and CLAUDE/AGENTS subagent discipline; no standalone |
| `cleared-spec-resolves-it-before-first-principles-fix` | 14 / 11 | direct-source/spec-authority signal | Reinforces PD-5 and direct-source grounding; no standalone |

## C4-§2 — `must_pass` #2: candidates evaluated against §7.4.7 and §7.5

**§7.4.7:** ZERO new stale-carry-text disposition species surfaced. The cadence-1 through cadence-3 finding remains corroborated.

**§7.5:** One candidate clears the v1.14 §7.5.1 gate:

**`full-chain-witness-not-half-proofs` → PD-6 PROMOTED.** Statement: when the claim crosses a real producer → shared surface → consumer chain, two half-proofs do not prove the composed claim. A producer test that stops at the seam plus a consumer test fed a hand-built/stubbed input can both pass while the production path is dead or vacuous. The proof must include one non-proxy witness through the real composed path, or the close must be narrowed honestly.

Run against the §7.5.1 inclusion gate:

1. **Instance-cardinality >=2 — PASS.** The memory records repeated independent applications: B-TOOL-GATE, B-HITL-PLACEMENT, B-EDIT-CARRIER, B-FANOUT-PAUSE-SYNTHESIS, B-FANOUT-CRASH-RESUME-MAYBE-RAN-SUBAGENT, B-INTERSTEP-HANDOFF, and B-HITL-PLACEMENT-PER-STEP-LOOSEN.
2. **Genuinely §7.5-shaped — PASS.** It is an execution/verification sequencing discipline: choose the composed witness shape before claiming production-live or non-vacuous behavior.
3. **No canonical home elsewhere — PASS with cite-don't-relocate.** PD-3 covers matching verification shape and PD-5 covers grounding/classification before authoring or closing, but neither states the stricter composed-chain witness requirement.

**Promotion applied this arc:** `design-substrate/Project_Workflow_v1_16.md` adds **PD-6 composed-chain non-vacuity witness**. Clearance marker filed at `.harness/clearance/Project_Workflow-v1_16-cleared-2026-06-30.md`. Root `CLAUDE.md` and `.harness/claude-artifact-pointers.md` now point to workflow head v1.16.

## C4-§3 — Closure disposition (cadence-4)

- **`must_pass` #1** (cardinality>=2 frontier identified): ✅ C4-§1.
- **`must_pass` #2** (candidates evaluated against §7.4.7 + §7.5): ✅ C4-§2 — result: ZERO new §7.4.7 owed; one §7.5 PD-6 promoted at workflow v1.16.
- **Entry status:** **ACTIVE-SURVEYED (cadence-4)**. Cadence-4's PD-6 promotion debt is discharged. R-600 remains an ACTIVE recurring lane; next run only after the cadence trips again (~10 PRs) or a concrete new candidate reaches independent instance-cardinality >=2.

---
---

# Cadence-5 run — 2026-07-12 (HEAD `a5627fc2`, post-#941)

**Cadence trigger.** ~44 merge commits (50 total commits) since the cadence-4 baseline (`3177fab8` / post-#848 → `a5627fc2` / post-#941) — well past the ~10-PR interval. The interval includes the R-FS-1 close track's tail (Tier-1 manual sign-off), the R-FS-2 Wave-1/Wave-2 opening arcs (B-18 EPOCH-PARTITION, B-18 PREWARM-OW, B-TOOL-SEARCH-RUNTIME, B-OD19-LOCAL-INSPECTION), and the codex-review-pilot closure.

**Method (identical to cadence-1..4).** Read-only `[[wiki-link]]` enumeration of the auto-memory store at `/Users/robertrhu/.claude/projects/-Users-robertrhu-Projects-arhugula-v2/memory/` (**119 files**, was 114 at cadence-4): **566 total refs / 99 distinct tokens → 76 at cardinality >=2** (was 558/101/72). As at every prior cadence, citation-count is a salience proxy, NOT instance-cardinality — promotion decisions below use per-candidate independent-arc counting, not the raw number.

## C5-§1 — `must_pass` #1: cardinality>=2 frontier identified

Top unchanged/already-homed signals remain dominant: `hooks-codex-pilots-decorrelation-validated` (45), `verification-shape-sharpened-grep-vs-e2e` (35), `advisor-before-substantive-work-for-cross-axis-blockers` (32), `grounding-reveals-claude-closeable-slice-close-honestly` (31), `r-cxa-seam-wiring-is-producer-discovery` (20), `full-chain-witness-not-half-proofs` (20, PD-6) — all already dispositioned at cadence-3/4.

The frontier change relevant to workflow promotion:

| pattern | refs/files | cadence-4 disposition | cadence-5 disposition |
|---|---:|---|---|
| `disposition-label-is-a-claim-verify-against-spec` | 5 refs, 8 named independent arcs (#695, #697, #702, #703, #760, #768, #928, #788) | did not exist as a consolidated token | **Promoted as PD-7** (see C5-§2). |
| `new-surface-audit-hash-and-config-not-carrier` | 7 refs, 6 named independent arcs (#616, #625, #635, #651, #657, #728) | did not exist as a consolidated token | **NOT §7.5** — out-of-domain (runtime-implementation mechanics, not SDLC process discipline). Recommended a dedicated home; see C5-§2. |
| `spec-leg-split-on-ratification-boundary` | 4 | did not exist | Cite-under-PD-1 (single named worked instance, #581 — fails §7.5.1 gate 1). Parked. |
| `adr-vs-fork-spec-plan-granularity` | 4 | did not exist | Already-homed reinforcement of CLAUDE.md §4.3 back-flow routing; not a new §7.5 shape. Cite-don't-relocate. |
| `design-substrate-version-identity-hazards` | 4 | did not exist | Reference-type; reinforces `[[wrong-version-read-delta-only-baseline]]` (already cite-under-PD-5). No standalone. |
| `insights-recs-workspace-blind` | 3 | did not exist | Already-homed at the `/optimize-claude-md` skill (a tool, not a workflow-doc discipline). No standalone. |

**Provenance honesty (the cadence-2 producer-discovery precedent applied here).** 7 of PD-7's 8 named arcs (#695–#788) **predate** the cadence-4 baseline (post-#848); only #928 (2026-07-11) postdates it. This is **not** a newly-occurring pattern missed at cadence-4 — it is a **newly-consolidated** one: the individual per-arc lessons existed as scattered feedback across many sessions, and the memory file itself carries mtime 2026-07-11 (this inter-cadence window), meaning the consolidation into one named, citable discipline happened after cadence-4 closed, drawing together 7 historical instances plus 1 new one. The honest framing is "first cadence at which the consolidated discipline crosses the promotion gate as a named pattern," not "first cadence at which the underlying behavior occurred." Same holds for `new-surface-audit-hash-and-config-not-carrier` (arcs #616–#728, all pre-cadence-4; consolidated file mtime within this window).

## C5-§2 — `must_pass` #2: candidates evaluated against §7.4.7 and §7.5

**§7.4.7:** ZERO new stale-carry-text disposition species surfaced. The cadence-1 through cadence-4 finding remains corroborated (5th independent surfacing).

**§7.5.4 cross-catalogue discriminator re-read at source (v1.14 §7.5.4), not from memory of prior cadence write-ups** — per the advisor's flag that this cadence's actual open question ("distinct new PD vs cite-under an existing PD") is adjudicated by that section's body, and PD-7's own memory frames itself as "the 4-disposition classifier [PD-5] this refines." §7.5.4 discriminates **catalogue membership** (§7.4.7.2 stale-carry-text / §7.5 process-discipline / `.harness/` retirement-event-pattern), not within-§7.5 novelty — and §7.5 is explicitly "a catalogue (heterogeneous disciplines, each with its own statement + empirical anchor + application shape + cross-reference) — NOT a taxonomy" (v1.14 §7.5 preamble). The PD-6 precedent (itself explicitly "complements PD-5," cite-don't-relocate, yet catalogued as its own numbered entry) is the controlling analogy: an adjacent-but-distinct discipline gets its own PD entry cross-referencing the sibling, not a merge into it.

**`disposition-label-is-a-claim-verify-against-spec` → PD-7 PROMOTED.** Statement: a disposition label already attached to a registered arc — in `arc-ledger.yaml`, the dashboard next-action, the spine ledger, a prior memory, or a precedent's own paraphrase/docstring — is someone's earlier conclusion, not ground truth. Before committing to build, fork, or gate on that label, re-ground the one load-bearing premise via a gated **direct** read of the primary spec text (never a precedent's paraphrase, a memory summary, or a sibling arc's framing) — the disposition can flip in either direction.

Run against the §7.5.1 inclusion gate:

1. **Instance-cardinality >=2 of independent arcs — PASS, strongly.** 8 distinct arcs across ~3 weeks (#695 bug-vs-ratified; #697 fork-vs-build; #702 type-signature-tiebreaker-over-a-vetted-design's-own-claimed-verification; #703 answers-a-question-vs-overrides-a-floor; #760 code-comments-are-not-the-spec's-invariant; #768 a-deferred-question-is-not-evidence-for-one-answer; #928 an-anticipated-scope-fix-shape-is-not-a-ratified-disposition; #788 a-probe-cited-disposition-is-doubly-a-claim), each a genuinely distinct failure mode, not a rescope of one unit.
2. **Genuinely §7.5-shaped — PASS.** A verification/sequencing discipline: before acting on an inherited claim, ground it directly. Distinct in shape from PD-3 (matching verification depth to the claim being verified) and PD-5 (deciding whether a lever is built/buildable/absent before authoring) — PD-7 is specifically about auditing **inherited labels/claims about a registered arc's disposition**, with its own discriminators (forbidding invariant vs. descriptive prose; does an impl-discretion clause name the strategy; does an operator action answer the surfaced question or override an independently-enforced invariant).
3. **No canonical home elsewhere — PASS with cite-don't-relocate to PD-5.** PD-5 decides whether a lever is already built before authoring; PD-7 decides whether an *already-assigned disposition label* on that lever should be trusted before acting on it — adjacent, not redundant, exactly the PD-6/PD-5 relationship.

**Promotion applied this arc:** `design-substrate/Project_Workflow_v1_17.md` adds **PD-7 disposition-label-is-a-claim**. Clearance marker filed at `.harness/clearance/Project_Workflow-v1_17-cleared-2026-07-12.md`. Root `CLAUDE.md` and `.harness/claude-artifact-pointers.md` now point to workflow head v1.17.

**`new-surface-audit-hash-and-config-not-carrier` → NOT promoted to §7.5; dedicated home recommended.** The pattern (audit-hash coherence for new behavior-driving surfaces; config-vs-carrier field placement; the three `freeze()` hazard sub-modes; the daemon-reuse per-run-isolation hazard; hash-carrier choice; drop-when-None byte-compat for hash-fed carriers) is empirically load-bearing across 6 independent R-FS-1 arcs (#616, #625, #635, #651, #657, #728) — it clears §7.5.1 gate 1 comfortably. It fails the **domain fit** implicit in §7.5.4's catalogue-routing spirit: §7.5 catalogues *SDLC execution-process* disciplines transferable across axes and design-phase work (sequencing, verification depth, AC decomposition, grounding-before-authoring); this pattern is a **runtime-implementation mechanics checklist** specific to `HarnessContext`/procedural-tier-hash/`freeze()` internals in one subsystem — not a cross-project process shape. Recommended home: a dedicated runtime-implementation pattern note, **not** Project_Workflow. Authored this arc at `.harness/harness-context-carrier-and-hash-patterns.md` (mode-agnostic; no `design-substrate/**` touch, no clearance marker owed).

**Parked (fail gate 1 — single named instance, cite-don't-relocate):**
- `spec-leg-split-on-ratification-boundary` (card 4 cite, 1 worked arc — #581): the design-authoring-time analogue of PD-1's build-time AC-split. Stays a PD-1 specialization until a second independent spec-leg-split arc surfaces.
- `adr-vs-fork-spec-plan-granularity` (card 4 cite, 1 worked arc): already substantially covered by CLAUDE.md §4.3's fork-class routing table; this memory sharpens it (the "impl-to-cleared-spec is not a fork at all" corollary) without introducing a new §7.5 shape. Cite-don't-relocate.
- `design-substrate-version-identity-hazards` (card 4 cite, reference-type): reinforces the already-cited `[[wrong-version-read-delta-only-baseline]]`; no standalone promotion.

## C5-§3 — Closure disposition (cadence-5)

- **`must_pass` #1** (cardinality>=2 frontier identified): ✅ C5-§1.
- **`must_pass` #2** (candidates evaluated against §7.4.7 + §7.5): ✅ C5-§2 — result: ZERO new §7.4.7 owed; one §7.5 PD-7 promoted at workflow v1.17; one strong-but-out-of-domain candidate (`new-surface-audit-hash-and-config-not-carrier`) routed to a dedicated non-§7.5 home instead of forced into the workflow doc.
- **Entry status:** **ACTIVE-SURVEYED (cadence-5)**. Cadence-5's PD-7 promotion debt is discharged in the same arc. R-600 remains an ACTIVE recurring lane; next run only after the cadence trips again (~10 PRs) or a concrete new candidate reaches independent instance-cardinality >=2.

---
---

# Cadence-6 run — 2026-07-12 (HEAD `dfe82ab6`, post-#961)

**Cadence trigger.** ~19 merge commits since the cadence-5 baseline (`a5627fc2` / post-#941 → `27b311d3` / post-#960) — past the ~10-PR interval, per the dashboard's own due-flag ("cadence-5 last closed at PR #942; ~18 PRs since"). The interval covers the R-FS-2 Wave 3/4/5 closeout arcs (B-COST-REPLAY-DEDUP-WITNESS, B-GAPD-TOOLONLY-BOOTSTRAP, B-19-BREAKER-AMBIENT-ATTRS, B-HYGIENE-CITE-POINTER-SWEEP) and the R-FS-2 G2 closure report (PR #960).

**Method (identical to cadence-1..5).** Read-only `[[wiki-link]]` enumeration of the auto-memory store at `/Users/robertrhu/.claude/projects/-Users-robertrhu-Projects-arhugula-v2/memory/` (**121 files**, was 119 at cadence-5): **567 total refs / 100 distinct tokens → 76 at cardinality >=2** (was 566/99/76). The card>=2 count is unchanged from cadence-5 — but per the standing metric caveat (citation-count is a salience proxy, not instance-cardinality; a frozen count can still hide a newly-*consolidated* discipline, exactly how PD-7 surfaced last cadence), the count alone is not treated as evidence of "nothing new." The gating check this cadence is the **file-delta since the cadence-5 baseline**, not the token count (flagged by `advisor()` pre-write-up as the correct discriminator).

## C6-§1 — `must_pass` #1: cardinality>=2 frontier identified + file-delta audit

Top unchanged/already-homed signals remain dominant: `hooks-codex-pilots-decorrelation-validated` (45), `verification-shape-sharpened-grep-vs-e2e` (35), `advisor-before-substantive-work-for-cross-axis-blockers` (32), `grounding-reveals-claude-closeable-slice-close-honestly` (31), `r-cxa-seam-wiring-is-producer-discovery` (20), `full-chain-witness-not-half-proofs` (20, PD-6), `disposition-label-is-a-claim-verify-against-spec` (5, PD-7) — all already dispositioned at cadence-3/4/5.

**File-delta audit (the load-bearing check this cadence).** `find memory/ -maxdepth 1 -name "*.md" -newermt "cadence-5 baseline"` → exactly 3 non-index files touched since cadence-5, plus `MEMORY.md` itself:

| file | card. | disposition |
|---|---:|---|
| `regenerate-roadmap-html-after-source-edit.md` | 8 | Class A operational recipe (dashboard regen mechanics); already indexed at MEMORY.md "Operational recipes." Edited (extended), not new. |
| `dashboard-regen-gh-unavailable-determinism.md` | — | Class A operational recipe (CI-parity `gh`-hidden regen); already indexed. |
| `squash-merge-dashboard-conflict.md` | — | Class A operational recipe (branch-from-stale-local-tip → spurious dashboard conflict); already indexed. |

All three are dashboard/git-mechanics recipes, not SDLC process disciplines — none clears the §7.5 domain-fit gate even before checking independence.

**Two card-frontier tokens worth resolving explicitly (grown since being flagged, never closed out in a cadence write-up):**

- **`feedback-verify-observation-layer-before-concluding-defect`** (card 1 at cadence-2 "awaits 2nd instance" → **9** now, 10 distinct referencing files). Checked against root `CLAUDE.md` §6 Verification & Failure Hygiene — **already baked in verbatim**: *"Verify the observation layer before concluding a defect... 'No entries / didn't happen / empty' is not a bug until you've confirmed you're looking at the right sink... Premature escalation on a misread is the symmetric failure to silent scope-narrowing."* **Class B — already-canonical, just never logged as dispositioned in this survey.** Logging it here closes the gap so it stops looking unresolved at the next cadence.
- **`fable5-fallback-reviewer`** (card 6, new since cadence-4/5 — file mtime 2026-07-10). Reviewer-selection/tooling policy (Fable-5-via-`Agent(model:"fable")` as the fallback decorrelated reviewer when advisor + codex are both unavailable) — the same shape as the already-Class-B `codex-out-of-family-reviewer`. **Class B — tooling/reviewer-ladder guidance, not a §7.5 SDLC discipline.** Already surfaced in MEMORY.md ("Reviewer ladder: codex + Fable-5 fallback").

**Spot-checked mid-frontier tokens (4-9 cite range) for Class-C shape — none qualify:** `gate-enforcement-site-and-timing-asymmetry` (harness gate-placement mechanics, domain-specific like `new-surface-audit-hash-and-config-not-carrier` — already has its own dedicated memory home, not cross-project SDLC), `feedback-genuine-skill-invocation-dedicated-agent` (operator behavioral directive, Class B), `shared-is-shape-change-ripples-cross-axis-field-asserts` (Class A operational recipe, already indexed), `skill-creator-eval-harness-caveats` (Class A tooling recipe, already indexed), `deleting-active-worktree-from-within-session` (Class A git-worktree recipe, sibling of `bash-cwd-reverts-to-project-root-not-worktree`).

## C6-§2 — `must_pass` #2: candidates evaluated against §7.4.7 and §7.5

**§7.4.7 (stale-carry-text):** ZERO new sub-species owed. This is the **6th independent surfacing** of the same null result across cadence-1 through cadence-6 — checked fresh at this cadence's card>=2 set (§C6-§1), not inherited from cadence-5.

**§7.5 (process-discipline):** ZERO new candidates clear the gate. The file-delta audit (the correct discriminator per the advisor's flag — citation-count alone would have under-scrutinized a possible silent consolidation, exactly the shape that produced PD-7 last cadence) found only 3 touched files since cadence-5, all Class A operational/dashboard recipes. The two card-frontier tokens worth resolving (`feedback-verify-observation-layer-before-concluding-defect`, `fable5-fallback-reviewer`) both land Class B — already-homed (CLAUDE.md §6; reviewer-ladder tooling guidance respectively) — confirmed by direct content read, not assumed from citation count.

**No promotion this cadence.** `design-substrate/Project_Workflow_v1_17.md` remains the current head; no amendment, no clearance marker.

## C6-§3 — Closure disposition (cadence-6)

- **`must_pass` #1** (cardinality>=2 frontier identified + file-delta audit): ✅ C6-§1.
- **`must_pass` #2** (candidates evaluated against §7.4.7 + §7.5): ✅ C6-§2 — result: ZERO new §7.4.7 owed (6th surfacing); ZERO new §7.5 promotion (file-delta-audited, not just citation-count-audited, per `advisor()` pre-write-up flag).
- **Entry status:** **ACTIVE-SURVEYED (cadence-6)**. A legitimate zero-promotion cadence — verified against the stronger file-delta signal, not the frozen citation count alone. R-600 remains an ACTIVE recurring lane; next run only after the cadence trips again (~10 PRs) or a concrete new candidate reaches independent instance-cardinality >=2.

---
---

# Cadence-7 run — 2026-07-14 (HEAD `a4074653`, post-#973)

**Cadence trigger.** 11 commits since the cadence-6 close commit (`5aa138aa` / PR #962, merged 2026-07-13T02:48:57Z → `a4074653` / post-#973) — spanning PRs #963–#973, past the ~10-PR interval. The window covers `B-23` (cost-attribution F2-write, PR #968) and `B-26` (real IS hash-chain verification wired into the rotation-verification stub, PR #972 — 5 rounds of out-of-family Codex review), plus their terminating refreshes.

**Method (identical to cadence-6 — file-delta is the load-bearing check, not raw citation count).** Read-only `[[wiki-link]]` enumeration of the auto-memory store at `/Users/robertrhu/.claude/projects/-Users-robertrhu-Projects-arhugula-v2/memory/` (**121 files**, unchanged from cadence-6): **568 total refs / 100 distinct tokens → 76 at cardinality >=2** (was 567/100/76 at cadence-6 — a +1 total-ref delta, cardinality-frontier set unchanged). Per the standing caveat (a frozen cardinality count can still hide a newly-consolidated discipline), the gating check is the file-delta since the precise cadence-6 close timestamp, not the near-identical aggregate counts.

## C7-§1 — `must_pass` #1: cardinality>=2 frontier identified + file-delta audit

Top signals unchanged from cadence-6: `hooks-codex-pilots-decorrelation-validated` (45), `verification-shape-sharpened-grep-vs-e2e` (35), `advisor-before-substantive-work-for-cross-axis-blockers` (32), `grounding-reveals-claude-closeable-slice-close-honestly` (31), `full-chain-witness-not-half-proofs` (21, PD-6), `r-cxa-seam-wiring-is-producer-discovery` (20), `disposition-label-is-a-claim-verify-against-spec` (PD-7) — all already dispositioned at cadence-3 through cadence-6.

**File-delta audit (precise cutoff = cadence-6's own merge timestamp, `2026-07-13T02:48:57Z`, not a rounded date — the cadence-6 audit's own 3 already-dispositioned files (`regenerate-roadmap-html-after-source-edit.md`, `dashboard-regen-gh-unavailable-determinism.md`, `squash-merge-dashboard-conflict.md`) have mtimes a few hours BEFORE that exact timestamp and were correctly excluded once the cutoff was tightened from a same-day approximation to the merge instant).** Exactly 2 non-index files touched since cadence-6 close:

| file | disposition |
|---|---|
| `codex-out-of-family-reviewer.md` | Class A/B tooling — reviewer-ladder guidance, already indexed at MEMORY.md ("Reviewer ladder: codex + Fable-5 fallback"). New content this window: (a) an operational model-upgrade note (`gpt-5.5`→`gpt-5.6-sol`, tooling mechanics, not process); (b) two review-ritual sharpenings from arc #933 — pre-build reviews should verify each rationale leg **empirically**, not just hunt missing legs; post-build reviews should **mutation-probe normative lines** (temporarily delete the load-bearing line, confirm the witness fails, restore). |
| `fanout-pause-per-strategy-carrier.md` | Class C, project-type (own `type: project` frontmatter) — CP-axis fan-out pause/resume implementation mechanics. New content this window: item (6), the `B-21` cross-carrier port (PR #970) and its byte-compat-scoping lesson (a shared serialization helper reused for a new field on one carrier must diverge per-carrier-kind when a sibling carrier already has durable instances depending on the old behavior). Same shape as cadence-5's `new-surface-audit-hash-and-config-not-carrier` finding — domain-specific runtime-implementation mechanics, not a cross-project SDLC discipline. Already has a dedicated home; no §7.5 candidacy. |

**One candidate evaluated against §7.5.1 gate 1 and NOT yet cleared — flagged as a card-frontier token for the next cadence, not promoted this one.** The "mutation-probe normative lines" technique (deliberately break the code the witness is supposed to pin, confirm the witness fails, then restore — proving the test is load-bearing rather than green-by-construction) is genuinely valuable and recurring: it originates at arc #933 (named explicitly in `codex-out-of-family-reviewer.md`), a softer precedent exists at #927 ("mutation-probed the normative task.result() resurface" per the `fanout-pause-per-strategy-carrier.md` / `b18-epoch-partition` lineage), and this session's own `B-26` arc (PR #972) independently applied it 4 times (mutation-probing the hash-chain-succeeded gate, the downstream-blocking gate, the empty-ledger gate, each confirmed by reverting the fix and observing the expected test failure before restoring). **Gate-1 read:** despite this real cross-arc recurrence, it does not yet exist as its own **consolidated, independently-named** memory token — it currently lives as sub-content inside `codex-out-of-family-reviewer.md` (a reviewer-ladder tooling file whose primary subject is something else) and is absent from `safe-mutation-probe-no-git-checkout-restore.md` (a git-safety operational recipe, not the verification technique). Per the cadence-5 PD-7 provenance-honesty framing, the *behavior* recurring across arcs is not the same as the *discipline* being promotion-ready — that requires a named, citable consolidation first. **Disposition:** park; if a dedicated `mutation-probe-...` memory entry consolidates with independent-arc citations before the next sweep, it is a strong PD-3-adjacent candidate (verification-shape matching already exists at PD-3/root `CLAUDE.md` §6, but "prove the test itself is load-bearing via fault injection" is a distinct, sharper facet worth its own entry, not a restatement).

## C7-§2 — `must_pass` #2: candidates evaluated against §7.4.7 and §7.5

**§7.4.7 (stale-carry-text):** ZERO new sub-species owed. This is the **7th independent surfacing** of the same null result across cadence-1 through cadence-7, checked fresh against this cadence's card>=2 set and file-delta (not inherited from cadence-6).

**§7.5 (process-discipline):** ZERO new candidates clear the gate this cadence. Both touched files are already-homed (Class A/B tooling and Class C project-type respectively); the one genuinely interesting emerging technique (mutation-probing normative witnesses) fails gate 1 on consolidation, not on merit — flagged forward rather than forced or dropped, per the register's own "register-then-triage, not drop" discipline.

**No promotion this cadence.** `design-substrate/Project_Workflow_v1_17.md` remains the current head; no amendment, no clearance marker.

## C7-§3 — Closure disposition (cadence-7)

- **`must_pass` #1** (cardinality>=2 frontier identified + file-delta audit): ✅ C7-§1.
- **`must_pass` #2** (candidates evaluated against §7.4.7 + §7.5): ✅ C7-§2 — result: ZERO new §7.4.7 owed (7th surfacing); ZERO new §7.5 promotion (one card-frontier token — mutation-probe-as-load-bearing-witness — flagged forward, not yet consolidated as its own citable pattern).
- **Entry status:** **ACTIVE-SURVEYED (cadence-7)**. A legitimate zero-promotion cadence. R-600 remains an ACTIVE recurring lane; next run only after the cadence trips again (~10 PRs) or a concrete new candidate (the flagged mutation-probe token, or another) reaches independent instance-cardinality >=2 as a named, consolidated entry.

---
---

# Cadence-8 run — 2026-07-14 (HEAD `380ec161`, post-#998)

**Cadence trigger.** Cadence-7 closed at commit `9cad319e` (PR #974, merged 2026-07-14T00:49:43-06:00). Since then: 18 merged PRs — #976, #978, #982-988, #990-998 (#989 was closed unmerged) — well past the ~10-PR interval. This run is additionally triggered by cadence-7's own explicit deferral: cadence-7's write-up (C7-§1 above) named `mutation-probe-load-bearing-witness.md` as a card-frontier token and said "re-evaluate at the next R-600 cadence" — this is that re-evaluation. **Correction (caught by out-of-family Codex review of this cadence's own PR, pre-merge):** the memory file's mtime is `2026-07-14T00:32:48-06:00`, 17 minutes **before** cadence-7's own close commit — it is NOT a file-delta discovery since cadence-7 close; it already existed when cadence-7's own write-up flagged it (same close-out session, just before the closing commit). The corrected framing: cadence-8 performs cadence-7's own explicitly-deferred re-evaluation of an already-known candidate, not a fresh file-delta discovery of a new one. This does not change the promotion decision (§7.5.1 gate application in C8-§2 is unaffected by when the file was created, only by what it says) but the original draft of this section conflated the two, and is corrected here.

**Method (identical to cadence-6/7 — file-delta against the precise prior-cadence close timestamp is the load-bearing check, not raw citation count).** Read-only `[[wiki-link]]` enumeration of the auto-memory store (**127 files**, was 121 at cadence-7): **580 total refs / 103 distinct tokens → 76 at cardinality >=2** (was 568/100/76 at cadence-7 — cardinality-frontier set essentially unchanged in count, consistent with cadence-6/7's pattern of a frozen aggregate hiding a real consolidation event underneath).

## C8-§1 — `must_pass` #1: cardinality>=2 frontier identified + file-delta audit

Top signals unchanged from cadence-7: `hooks-codex-pilots-decorrelation-validated` (45), `verification-shape-sharpened-grep-vs-e2e` (35), `advisor-before-substantive-work-for-cross-axis-blockers` (32), `grounding-reveals-claude-closeable-slice-close-honestly` (31), `full-chain-witness-not-half-proofs` (21, PD-6), `r-cxa-seam-wiring-is-producer-discovery` (20), `disposition-label-is-a-claim-verify-against-spec` (PD-7) — all already dispositioned at cadence-3 through cadence-7.

**File-delta audit (precise cutoff = cadence-7's own merge timestamp, `2026-07-14T00:49:43-06:00`) — snapshot taken at the ORIGINAL cadence-8 audit run, before this PR's own review-driven corrections.** Exactly 6 non-index files touched since cadence-7 close as of that original snapshot (plus `MEMORY.md` itself) — `mutation-probe-load-bearing-witness.md` is deliberately NOT in this table; at snapshot time its mtime predated the cutoff (see the correction in the cadence trigger note above), so it was evaluated separately below, not as a file-delta result. **Reproducibility note (caught by a 3rd round of out-of-family Codex review of this cadence's own PR):** this PR's own review-driven corrections subsequently edited `mutation-probe-load-bearing-witness.md` (to fix its provenance paragraph — see the trigger note + C8-§2 below), which naturally bumped that file's mtime past the cutoff. A fresh re-run of this exact `find`/mtime scan against current HEAD would now show 7 files, not 6, because it would pick up that in-flight edit. This is an artifact of the correction process happening within the same PR that the audit is reporting on, not a re-run of the original cadence-8 audit — the 6-file result above is the honest snapshot at the moment the audit was actually performed, and is preserved as such rather than silently re-numbered as corrections landed on top of it:

| file | disposition |
|---|---|
| `gh-pr-merge-fails-in-worktree-but-succeeds.md` | NEW file this session (single-instance operational recipe — `gh pr merge` "main already checked out" is a local-cleanup-only error in a linked worktree; the merge itself already succeeded via the API). Cardinality-1 by session-independence (confirmed 10x within one session, not across independent sessions per the cadence-2 producer-discovery same-session discriminator). Class A operational recipe; parked, awaits a 2nd independent-session occurrence. |
| `wait-for-main-ci-green-before-forward-work.md` | NEW file this session (explicit operator directive: hold for main's own post-merge CI, not just the PR-gate run, rerunning confirmed-flaky failures before any further forward work). Cardinality-1, feedback-type operator guidance — same shape as cadence-4's `feedback-gate-only-on-meaningful-architecture-change` disposition ("operator behavioral guidance... already active in session discipline; no workflow-doc entry"). Class B; not §7.5-shaped at this cardinality. |
| `roadmap-ledger-edits-via-idempotent-script.md` | Edited (not new) — an explicit idempotency requirement added to the existing roadmap/ledger-edit-script discipline. Already Class A/B, already indexed at MEMORY.md, already cross-referenced to CLAUDE.md §12 Editing Conventions. No new §7.5 candidacy. |
| `forward-register-schema-sibling-to-arc-ledger.md` | Edited (not new) — this session's own B-20/fork-doc-filing work referenced it; content unchanged in shape (project-type, tool/schema-specific). Same disposition as cadence-5/7's `new-surface-audit-hash-and-config-not-carrier` / `fanout-pause-per-strategy-carrier`: domain-specific tooling pattern, not cross-project SDLC discipline. No standalone. |
| `bash-cwd-reverts-to-project-root-not-worktree.md` | Edited (not new) — grew a 4th "EXTENDS" section this window (the Stop-gate hook resolving to the main checkout instead of the worktree, recurring 23x in one prior session). Already dispositioned Class A at cadence-2/3 ("harness env recipe... not a promotable discipline") and remains so — the file accumulating more evidence over time does not change its domain-specific-recipe shape into a cross-project SDLC process discipline. |
| `autonomous-loop-terse-status-line-format.md` | Edited (not new) — a correction narrowing the terse-status-line discipline (narration brevity does not license under-responding to a direct user prompt). Class B, already-canonical (cites + sharpens CLAUDE.md §14.7 directly). No standalone §7.5 candidacy. |

All 6 touched files were spot-checked by direct content read, not assumed from filename/cardinality alone (per the cadence-6 `advisor()` flag this methodology still follows). All 6 are Class A/B (already-homed or single-instance operator/session guidance) — none clears the §7.5 domain-fit or cardinality gate. **The actual load-bearing candidate this cadence is the deferred re-evaluation of `mutation-probe-load-bearing-witness.md` (see below), separate from this file-delta table.**

## C8-§2 — `must_pass` #2: candidates evaluated against §7.4.7 and §7.5

**§7.4.7 (stale-carry-text):** ZERO new sub-species owed. This is the **8th independent surfacing** of the same null result across cadence-1 through cadence-8, checked fresh against this cadence's file-delta set (not inherited from cadence-7).

**§7.5 (process-discipline) — one candidate clears the gate:**

**`mutation-probe-load-bearing-witness` → PD-8 PROMOTED.** Statement: when a fix's correctness rests on "this regression test proves it," don't stop at green — temporarily revert the fix, confirm the specific test fails with the expected assertion, then restore and re-verify. A test can be green for the wrong reason (never exercises the failing branch; a fixture that accidentally satisfies both the old and new code path; an assertion weaker than the actual claim); mutation-probing is the cheapest way to prove the test discriminates the fix from its absence.

Run against the §7.5.1 inclusion gate (verified per-candidate, not by citation count):

1. **Instance-cardinality >=2 of independent arcs — PASS, with an honesty caveat (mirrors the cadence-2 PD-5 precedent), corrected across TWO rounds of out-of-family Codex review of this cadence's own PR.** The memory file's own prose lists 3 named PRs (#927, #933, #972). **Round 1** verified against `gh pr view --json mergedAt` + each commit's `Claude-Session` trailer rather than taking the count at face value, per **PD-7's own discipline applied to itself**, and found PR #927 (merged 2026-07-11T06:51:07Z) and PR #933 (merged 2026-07-11T17:09:22Z) share the identical `Claude-Session` trailer (`session_01VjkgZRnJXJNZYycJ6fb5GK`) — same session, same underlying lesson (the `task.result()` resurface check), applied to two sibling PRs in the same CP-axis `B-18-3C-PREWARM` family. Per the cadence-2 producer-discovery same-day/same-session/same-lesson discriminator, **these collapse to ONE instance, not two,** leaving PR #972 / `B-26` as the second instance. **Round 2 caught two further errors in round 1's own correction:** #972/`B-26` was mischaracterized as a separate "IS-axis" arc — direct read of its commit shows `fix(cp)`, wiring real IS hash-chain verification into the CP-owned `harness_cp/five_axis_composition.py`, a CP→IS seam rather than a distinct axis; and its claimed "4 independent probes" (carried forward unverified from the memory file) is actually **2** on direct read of the committed test diff — `test_empty_ledger_does_not_fake_success` (the empty-ledger gate) and `test_hash_chain_step_broken_chain_fails_rotation` (a single probe whose assertions cover both the hash-chain-succeeded gate and the downstream-step-blocking behavior together, not two separate probes). The fully-corrected count is **2 genuinely independent instances**: the #927/#933 session (one instance) + PR #972/`B-26` (2026-07-14, CP-axis, a separate session, 2 discriminating-witness probes). 2 still clears the literal ">=2" gate text, but at the thinnest margin of any PD promoted so far — flagged honestly rather than overstated as "3 distinct arcs" or "4 probes."
2. **Genuinely §7.5-shaped — PASS.** A verification-sequencing discipline: after a regression test is written and passes, prove it is load-bearing via fault injection before trusting it. Distinct from PD-3 (matching verification depth/shape to the claim) and PD-6 (proving the composed chain is real, not proxied) — PD-8 is the narrower check that survives both: even at the right depth through the right chain, a test can still be green for the wrong reason.
3. **No canonical home elsewhere — PASS with cite-don't-relocate to PD-3 and PD-6.** Neither states the fault-injection requirement; PD-8 is the missing sharper facet, cross-referenced rather than merged (mirroring the PD-6/PD-3 and PD-7/PD-5 precedents of adjacent-but-distinct catalogue entries).

**Promotion applied this arc:** `design-substrate/Project_Workflow_v1_18.md` adds **PD-8 mutation-probe-as-load-bearing-witness**. Clearance marker filed at `.harness/clearance/Project_Workflow-v1_18-cleared-2026-07-14.md`. Root `CLAUDE.md` and `.harness/claude-artifact-pointers.md` now point to workflow head v1.18 — this arc also corrected a stale governance-pointer drift discovered while updating them: root `CLAUDE.md` §10.2's Workflow-doc row had never been bumped past v1.16/PD-6 even though the canonical head had already advanced to v1.17/PD-7 at the cadence-5 clearance (`.harness/claude-artifact-pointers.md` WAS current at v1.17; only the root `CLAUDE.md` pointer lagged). Corrected in the same PR as the v1.18 promotion.

**Three rounds of out-of-family Codex review, six corrections, culminating in live re-verification.** Round 1 caught an audit-window misattribution + overstated arc-count (3→2). Round 2 caught round 1's own new errors (PR #972's axis + probe count). Round 3 asked for something neither round had provided: actual execution evidence that the PD-8 technique was performed on PR #972, not just historical self-report (commit message + test docstrings). Closed by literally re-running the mutation-probe against current HEAD — see the `design-substrate/Project_Workflow_v1_18.md` §7.5.1 gate table's "Live re-verification" entry for the exact commands and results (both tests pass at baseline, fail with the expected assertion when the fix is reverted, pass again restored; `git diff` clean afterward). Round 3 also flagged that this PR's own corrections had bumped `mutation-probe-load-bearing-witness.md`'s mtime past the cadence-7 cutoff, meaning a fresh file-delta re-run would no longer reproduce the 6-file result above — clarified in the file-delta audit note as the original snapshot, not something a later re-run should expect to match.

**Other touched-file candidates — not promoted, dispositions above stand:** `gh-pr-merge-fails-in-worktree-but-succeeds` and `wait-for-main-ci-green-before-forward-work` are both single-session-instance (cardinality-1 by the cadence-2 discriminator) and parked pending a 2nd independent-session occurrence; the remaining 3 edited files reinforce already-dispositioned Class A/B homes.

## C8-§3 — Closure disposition (cadence-8)

- **`must_pass` #1** (cardinality>=2 frontier identified + file-delta audit): ✅ C8-§1.
- **`must_pass` #2** (candidates evaluated against §7.4.7 + §7.5): ✅ C8-§2 — result: ZERO new §7.4.7 owed (8th surfacing); **one §7.5 PD-8 promoted at workflow v1.18** — the cadence-7 card-frontier flag closed in the very next cadence, the fastest flag-to-promotion turnaround in the R-600 history to date.
- **Entry status:** **ACTIVE-SURVEYED (cadence-8)**. Cadence-8's PD-8 promotion debt is discharged in the same arc, alongside a stale-governance-pointer correction (root `CLAUDE.md` §10.2) discovered incidentally while publishing it. R-600 remains an ACTIVE recurring lane; next run only after the cadence trips again (~10 PRs) or a concrete new candidate reaches independent instance-cardinality >=2 as a named, consolidated entry.
