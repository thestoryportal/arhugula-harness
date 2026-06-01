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
