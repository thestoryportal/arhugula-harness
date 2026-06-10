# Project Workflow — v1.15 (delta over v1.14)

---

## Change-note (v1.14 → v1.15)

**Scope of revision.** Narrow additive amendment to §7.5.2, cataloguing one new process discipline: **PD-5 grounding-first producer/slice discovery**. v1.14's §7.5 scaffold and PD-1..PD-4 entries are preserved as the predecessor body; v1.15 adds exactly one discipline plus adjacent observations and footer. ZERO §7.4 / §7.4.7 amendment; ZERO contract change; ZERO retirement-event filing; ZERO production-code change; ZERO cross-axis cascade.

**Trigger (R-600 cadence-3, operator-authorized 2026-06-10).** `R-600-pattern-bake-in-sweep` reached its next cadence after 248 commits since cadence-2 (`2e60741` → `a7f7d1f4`). The memory-store survey at cadence-3 counted 199 files, 713 `[[...]]` refs, 192 distinct tokens, and 124 citation-cardinality >=2 tokens. Cadence-2 had parked `r-cxa-seam-wiring-is-producer-discovery` because it had citation salience but questionable independent-arc cardinality. By cadence-3 it had grown to 9 refs across 8 files, and its grounding-first sibling `grounding-reveals-claude-closeable-slice-close-honestly` had grown to 8 refs across 8 files. The post-cadence-2 R-CXA, R-830, R-410/R-411/R-412, and roadmap-refresh arcs provide the independent application record needed to promote a broader PD-5 rather than a seam-only rule.

**Authority anchor.** v1.14 §7.5.1 inclusion gate + §7.5.3 OPEN accumulation clause + `R-600-pattern-bake-in-sweep.md` cadence-2 PD-5 parking note + cadence-3 survey evidence. This amendment resolves the cadence-2 open question by consolidating producer-discovery and closeable-slice discovery under one grounding-first discipline instead of creating multiple narrow PDs.

**§7.5.1 inclusion-gate application.**

| Gate | Finding |
|---|---|
| Instance-cardinality >=2 of independent arcs | PASS. R-CXA seam producer discovery supplied the original "do not hollow-wire absent producers" instance; later arcs independently exercised the same discipline in closeable-slice and stale-state forms: R-830 build/close honestly after grounding a declared backend slice, R-410/R-411/R-412 ground infra-provider reality before claiming closure, and post-Phase-8 roadmap refreshes ground stale authored rows before selecting work. |
| Genuinely §7.5-shaped | PASS. This is a sequencing / discovery / verification discipline: ground the producer, contract, source path, and current implementation before authoring, wiring, closing, or deferring. It is not stale-carry-text disposition (§7.4.7) and not fidelity-claim grammar (§7.4.1-§7.4.6). |
| No canonical home elsewhere | PASS with cite-don't-relocate. PD-2 and PD-3 are adjacent, but neither covers the pre-authoring decision tree from "wire/build/close" lever to one of: already-built, build declared slice, defer no producer, or file fork. CLAUDE.md §12 has the operational "do not park" rule; PD-5 supplies the workflow-level grounding discriminator that prevents both overclaiming and manufactured work. |

---

## §1 Amendment to §7.5.2

### §7.5.2 Additive entry catalogued at v1.15

| # | Discipline | Statement | Independent-instance anchor | Application shape | Cross-reference |
|---|---|---|---|---|---|
| **PD-5** | **grounding-first producer/slice discovery** | When a roadmap, plan, or handoff lever is framed as "wire the production caller", "build the missing slice", "close the gate", or "operator/infra owns this", first ground the current implementation and substrate. Verify the real producer/caller, contract source path, field availability, existing tests, and current roadmap state before authoring. The grounded result determines the action: (a) already built -> record and close; (b) declared stdlib/mockable/provider-free slice exists -> build it and close honestly; (c) producer or contract is absent -> defer or file Class 1/back-flow, do not hollow-wire; (d) live credential/paid/provider step remains -> surface the exact gate only after all non-live work is closed. | **>=4 independent arcs / families:** R-CXA seam producer discovery (`r-cxa-seam-wiring-is-producer-discovery`) prevented hollow event wiring when producers or required fields were absent; R-830 memory backend work grounded the production backend boundary and separated provider-free closure from live-cloud gates; R-410/R-411/R-412 sandbox/managed-provider work grounded host/runtime feasibility before declaring closure; post-Phase-8 forward tracking and roadmap refresh arcs repeatedly found authored rows stale-as-written and re-derived the live closeable slice from HEAD. | Before implementing or closing a lever, run a grounding pass: grep/source-inspect the claimed producer and consumer, inspect the canonical contract/version, run the narrow verification that proves existence or absence, and classify the outcome into already-built / buildable-slice / back-flow-defer / live-gate. Document the classification on the tracking surface so future sessions do not re-open stale work or manufacture work to satisfy an old row. | memory `[[r-cxa-seam-wiring-is-producer-discovery]]`, `[[grounding-reveals-claude-closeable-slice-close-honestly]]`, `[[post-phase-8-forward-tracking]]`, `[[feedback-operator-labels-are-claude-driven-no-parking]]`. Adjacent to PD-2 and PD-3; cite-don't-relocate rather than replacing them. |

---

## §2 Sections preserved verbatim at v1.15

Per delta-only convention, v1.15 touches ONLY this file's change-note, §1 PD-5 additive entry, §3 adjacent observations, and footer. The following are PRESERVED VERBATIM at predecessor-body layer:

- v1.14 §7.5 scaffold, §7.5.1 inclusion gate, PD-1 through PD-4, §7.5.3 parked candidates, and §7.5.4 cross-catalogue discriminator.
- §7.4.1-§7.4.6 fidelity-grammar and §7.4.7 stale-carry-text disposition discipline.
- v1.13 + v1.12 + v1.11 + v1.10 + v1.9 + v1.8 historical anchors.

---

## §3 Adjacent observations

(a) **PD-5 resolves the cadence-2 PD-5 parking question by widening the title, not the scope.** Cadence-2 parked `r-cxa-seam-wiring-is-producer-discovery` as possibly same-session / same-family. Cadence-3 evidence shows the durable discipline is the broader grounding-first decision tree that includes producer discovery, closeable-slice honesty, and stale authored-row re-grounding. The promoted entry is therefore not "all grounding"; it is the specific pre-authoring/pre-close discriminator used when a lever looks mechanical but may actually be already built, buildable, absent, or live-gated.

(b) **Other cadence-3 candidates are not promoted here.** `hooks-codex-pilots-decorrelation-validated` / `codex-out-of-family-reviewer` have an existing workspace home in CLAUDE.md §13.1 and the Codex review tooling; `promptfoo-no-api-skill-eval-loop` / `eval-harness-refused-as-governance-gate` belong to dev-tool/eval-governance surfaces rather than workflow §7.5; `gitignored-work-belongs-in-main-not-reapable-worktree` / `bmad-runtime-gitignore-config-gotchas` are operational worktree/config hygiene lessons. They remain cite-don't-relocate or parked until a workflow-grammar need distinct from those homes is demonstrated.

(c) **No §7.4.7 absorption owed.** Cadence-3 did not surface a new stale-carry-text disposition species. The promoted rule is process-discipline-shaped and lands under §7.5 only.

---

## Filing footer

| Field | Value |
|---|---|
| Version | v1.15 (narrow additive amendment to §7.5.2 adding PD-5 grounding-first producer/slice discovery; v1.14 §7.5 scaffold and PD-1..PD-4 preserved as predecessor body) |
| Trigger | `R-600-pattern-bake-in-sweep` cadence-3, operator-authorized 2026-06-10 |
| Supersedes | v1.14 as current workflow head only; all v1.14 bodies preserved verbatim as predecessor |
| Scope of revision | SUBSTANTIVE workflow-grammar amendment: NEW PD-5 entry + adjacent observations + footer. ZERO §7.4/§7.4.7 amendment; ZERO C-*-NN contract change; ZERO production-code change; ZERO cross-axis cascade. Co-publication: workspace `CLAUDE.md` governance pointer bump + clearance marker. |
| Cross-axis cascade | ZERO. v1.15 is process-discipline canonicalization; no per-axis spec / plan / CXA / production code touch. |
| Authority anchor | v1.14 §7.5.1 inclusion gate + §7.5.3 OPEN accumulation clause + `R-600-pattern-bake-in-sweep.md` cadence-3 survey |
| Predecessor | v1.14 (§7.5 process-discipline catalogue seeded PD-1..PD-4) |
| Successor | (none — current canonical) |
| Date | 2026-06-10 |

---

*End of `Project_Workflow_v1_15.md` (delta over v1.14). v1.8 + v1.9 + v1.10 + v1.11 + v1.12 + v1.13 + v1.14 PRESERVED VERBATIM as historical anchors per delta-only-spec-file convention.*
