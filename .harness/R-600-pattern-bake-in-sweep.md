# R-600-pattern-bake-in-sweep — survey artifact

**Entry:** `R-600-pattern-bake-in-sweep` (roadmap §5.6) — *Sweep workspace memory for pattern candidates ready for workflow-doc promotion.*
**Posture:** mode-agnostic. **Sweep run:** 2026-06-01 (HEAD `d7574b3`, post-PR-195). **Cadence:** ~every 10 PRs (first execution; entry was ACTIVE-unstarted).
**Status after this run:** **ACTIVE-SURVEYED** — survey complete (both `must_pass` met); absorption into the workflow doc is owed to the **deferred** `R-600-workflow-v1-14-amendment` (PROPOSED, design-phase, operator-discretion timing per `[[workflow-v1-14-deferred-2026-05-29]]`). The sweep does **not** author design-substrate; it produces the candidate evidence base for the next v1.14/v1.15 amendment arc.

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
