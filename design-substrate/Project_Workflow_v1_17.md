# Project Workflow — v1.17 (delta over v1.16)

---

## Change-note (v1.16 -> v1.17)

**Scope of revision.** Narrow additive amendment to §7.5.2, cataloguing one new process discipline: **PD-7 disposition-label-is-a-claim**. v1.16's PD-6 composed-chain non-vacuity witness, v1.15's PD-5 grounding-first producer/slice discovery, and all v1.14 §7.5 scaffold content are preserved as predecessor body; v1.17 adds exactly one discipline plus adjacent observations and footer. ZERO §7.4 / §7.4.7 amendment; ZERO contract change; ZERO retirement-event filing; ZERO production-code change; ZERO cross-axis cascade.

**Trigger (R-600 cadence-5, 2026-07-12).** `R-600-pattern-bake-in-sweep` reached its next cadence after the cadence-4 survey at post-PR-848 (~44 merges since, well past the ~10-PR interval). The current memory-store survey counted 119 files, 566 `[[...]]` refs, 99 distinct tokens, and 76 citation-cardinality >=2 tokens. The load-bearing frontier candidate is `disposition-label-is-a-claim-verify-against-spec`: a registered arc's disposition label (fork-first / build / operator-gated / premise-invalid / etc., wherever it is recorded — `arc-ledger.yaml`, the dashboard, the spine ledger, a prior memory, or a precedent's own paraphrase) is someone's earlier conclusion, not ground truth, and must be re-grounded via a gated direct primary-spec read before acting on it.

**Provenance note.** 7 of the 8 named independent arcs behind this discipline (#695, #697, #702, #703, #760, #768, #788) predate the cadence-4 baseline (post-#848); only #928 postdates it. This is a **newly-consolidated** discipline, not a newly-occurring one — the per-arc lessons existed individually across many sessions and were drawn together into one named, citable pattern within the current inter-cadence window. See `R-600-pattern-bake-in-sweep.md` cadence-5 §1 for the full provenance accounting.

**Authority anchor.** v1.14 §7.5.1 inclusion gate + §7.5.4 cross-catalogue discriminator + §7.5.3 OPEN accumulation clause + `R-600-pattern-bake-in-sweep.md` cadence-5 survey evidence. This amendment promotes the recurring lesson that an inherited disposition label is a claim to re-verify against the primary spec text, not a given to build, fork, or gate on directly.

**§7.5.1 inclusion-gate application.**

| Gate | Finding |
|---|---|
| Instance-cardinality >=2 of independent arcs | PASS, strongly. 8 distinct arcs across ~3 weeks, each a genuinely different failure mode: #695 (bug label vs. ratified+tested behavior), #697 (design-fork-first label vs. a false fork premise), #702 (a type signature overrides a vetted design doc's own claimed verification), #703 (an operator action that answers the primitive's question rather than overriding an invariant), #760 (an impl's code comment is descriptive prose, not the spec's invariant), #768 (a prior arc's deliberate punt is not evidence for one answer), #928 (an `anticipated_scope` fix-shape is registration-time anticipation, not a ratified disposition), #788 (a probe-cited disposition is doubly a claim — the label and the probe's site both need re-verification). |
| Genuinely §7.5-shaped | PASS. This is a verification/sequencing discipline: before acting on an inherited claim about a registered arc, ground it directly against the primary spec text. It is not stale-carry-text disposition (§7.4.7) and not byte-exact claim grammar (§7.4.1-§7.4.6). |
| No canonical home elsewhere | PASS with cite-don't-relocate to PD-5. PD-5 decides whether a lever is already built, buildable, absent, or live-gated before authoring. PD-7 decides whether an *already-assigned disposition label* on that lever should be trusted before building, forking, or gating on it — the PD-5/PD-7 relationship mirrors the existing PD-5/PD-6 relationship (adjacent, cross-referenced, not merged). |

---

## §1 Amendment to §7.5.2

### §7.5.2 Additive entry catalogued at v1.17

| # | Discipline | Statement | Independent-instance anchor | Application shape | Cross-reference |
|---|---|---|---|---|---|
| **PD-7** | **disposition-label-is-a-claim** | A disposition label already attached to a registered arc — in a ledger's `anticipated_scope`, a dashboard next-action, the spine ledger, a prior memory, or a precedent's own paraphrase/docstring — is someone's earlier conclusion, not ground truth. Before committing to build, fork, or gate on that label, re-ground the one load-bearing premise via a **gated direct read of the primary spec text** (never a precedent's paraphrase, a memory summary, or a sibling arc's framing). The disposition can flip in either direction. Discriminators: (a) does the cited text state a forbidding invariant, or only descriptive current-state prose? (b) does an impl-discretion clause NAME the strategy in question (authorizes) or merely defer to discretion generally? (c) for an operator-resolution/HITL/pause arc — does the operator's action ANSWER the question the primitive paused to ask (completes the decision, build-no-gate), or does it OVERRIDE an invariant the primitive enforces independently of that question (gate)? | **8 independent arcs**: #695, #697, #702, #703, #760, #768, #928, #788 (2026-06 through 2026-07-11) — each a distinct failure mode, not a rescope of one unit; see change-note provenance note above and `R-600-pattern-bake-in-sweep.md` cadence-5 §1-§2 for the per-arc detail. | Before building, forking, or gating on any inherited disposition label: (1) identify the ONE load-bearing premise the label rests on; (2) read the PRIMARY spec/plan/ADR text directly at that premise — not a docstring, memory summary, or sibling arc's framing of it; (3) apply discriminators (a)-(c) above; (4) if the direct read contradicts the inherited label, flip the disposition and name the correction in the arc's record (spine ledger, fork doc, or PR), not just in a private judgment. | memory `[[disposition-label-is-a-claim-verify-against-spec]]`. Adjacent to PD-5 (`[[grounding-reveals-claude-closeable-slice-close-honestly]]` — "the 4-disposition classifier this refines"); cite-don't-relocate rather than merging. Composes with `[[advisor-before-substantive-work-for-cross-axis-blockers]]` (the advisor gates the read) and `[[wrong-version-read-delta-only-baseline]]` (the read must hit the canonical version, not a stale one). |

---

## §2 Sections preserved verbatim at v1.17

Per delta-only convention, v1.17 touches ONLY this file's change-note, §1 PD-7 additive entry, §3 adjacent observations, and footer. The following are PRESERVED VERBATIM at predecessor-body layer:

- v1.16 PD-6 composed-chain non-vacuity witness and adjacent observations.
- v1.15 PD-5 grounding-first producer/slice discovery and adjacent observations.
- v1.14 §7.5 scaffold, §7.5.1 inclusion gate, PD-1 through PD-4, §7.5.3 parked candidates, and §7.5.4 cross-catalogue discriminator.
- §7.4.1-§7.4.6 fidelity-grammar and §7.4.7 stale-carry-text disposition discipline.
- v1.13 + v1.12 + v1.11 + v1.10 + v1.9 + v1.8 historical anchors.

---

## §3 Adjacent observations

(a) **PD-7 is narrower than "double-check your work."** It applies specifically to a label that was ALREADY ASSIGNED to a registered arc by an earlier session, ledger row, dashboard render, or precedent artifact — the discipline is about not inheriting that earlier conclusion uncritically, not about general verification depth (that is PD-3) or about whether a lever exists before authoring (that is PD-5).

(b) **PD-7 complements PD-5, it does not replace it.** PD-5 answers "is this lever already built, buildable, absent, or live-gated?" before authoring. PD-7 answers "is the disposition label already assigned to this arc (built it / fork it / gate it) actually correct?" before acting on that label. A single arc can need both: ground whether the lever exists (PD-5), then ground whether the existing label about that lever is right (PD-7).

(c) **`new-surface-audit-hash-and-config-not-carrier` is NOT promoted here.** The cadence-5 survey found this pattern (audit-hash coherence for new behavior-driving surfaces; `HarnessContext` field placement; `freeze()` hazard sub-modes; daemon-reuse isolation; hash-carrier choice; drop-when-None byte-compat) empirically load-bearing across 6 independent arcs, clearing §7.5.1 gate 1 comfortably — but it is a runtime-implementation mechanics checklist specific to one subsystem's internals, not a cross-project SDLC process discipline, so it fails the domain fit implicit in §7.5.4's catalogue-routing spirit. Routed to a dedicated runtime-implementation pattern note (`.harness/harness-context-carrier-and-hash-patterns.md`) instead of §7.5.

(d) **No §7.4.7 absorption owed.** Cadence-5 did not surface a new stale-carry-text disposition species. The promoted rule is process-discipline-shaped and lands under §7.5 only.

---

## Filing footer

| Field | Value |
|---|---|
| Version | v1.17 (narrow additive amendment to §7.5.2 adding PD-7 disposition-label-is-a-claim; v1.16 PD-6, v1.15 PD-5, and v1.14 §7.5 scaffold preserved as predecessor body) |
| Trigger | `R-600-pattern-bake-in-sweep` cadence-5, 2026-07-12 |
| Supersedes | v1.16 as current workflow head only; all v1.16 bodies preserved verbatim as predecessor |
| Scope of revision | SUBSTANTIVE workflow-grammar amendment: NEW PD-7 entry + adjacent observations + footer. ZERO §7.4/§7.4.7 amendment; ZERO C-*-NN contract change; ZERO production-code change; ZERO cross-axis cascade. Co-publication: workspace `CLAUDE.md` governance pointer bump + clearance marker. |
| Cross-axis cascade | ZERO. v1.17 is process-discipline canonicalization; no per-axis spec / plan / CXA / production code touch. |
| Authority anchor | v1.14 §7.5.1 inclusion gate + §7.5.4 cross-catalogue discriminator + §7.5.3 OPEN accumulation clause + `R-600-pattern-bake-in-sweep.md` cadence-5 survey |
| Predecessor | v1.16 (§7.5 PD-6 composed-chain non-vacuity witness) |
| Successor | (none — current canonical) |
| Date | 2026-07-12 |

---

*End of `Project_Workflow_v1_17.md` (delta over v1.16). v1.8 + v1.9 + v1.10 + v1.11 + v1.12 + v1.13 + v1.14 + v1.15 + v1.16 PRESERVED VERBATIM as historical anchors per delta-only-spec-file convention.*
