# Project Workflow — v1.16 (delta over v1.15)

---

## Change-note (v1.15 -> v1.16)

**Scope of revision.** Narrow additive amendment to §7.5.2, cataloguing one new process discipline: **PD-6 composed-chain non-vacuity witness**. v1.15's PD-5 grounding-first producer/slice discovery and all v1.14 §7.5 scaffold content are preserved as predecessor body; v1.16 adds exactly one discipline plus adjacent observations and footer. ZERO §7.4 / §7.4.7 amendment; ZERO contract change; ZERO retirement-event filing; ZERO production-code change; ZERO cross-axis cascade.

**Trigger (R-600 cadence-4, 2026-06-30).** `R-600-pattern-bake-in-sweep` reached its next cadence after the cadence-3 survey at post-PR-466. The current memory-store survey counted 114 files, 558 `[[...]]` refs, 101 distinct tokens, and 72 citation-cardinality >=2 tokens. The store is smaller than cadence-3's 199-file snapshot, so raw count deltas are not read as trend. The load-bearing frontier is qualitative: `full-chain-witness-not-half-proofs` now has 20 refs across 15 files, with adjacent non-vacuity/runtime-path tokens (`built-but-vacuous-reground-ledger-asis`, `test-bypass-as-runtime-truth-pattern`, and `verification-shape-sharpened-grep-vs-e2e`) reinforcing the same execution discipline.

**Authority anchor.** v1.14 §7.5.1 inclusion gate + §7.5.3 OPEN accumulation clause + `R-600-pattern-bake-in-sweep.md` cadence-4 survey evidence. This amendment promotes the recurring lesson that producer-side proof plus consumer-side proof is not enough when the composed production chain is the claim.

**§7.5.1 inclusion-gate application.**

| Gate | Finding |
|---|---|
| Instance-cardinality >=2 of independent arcs | PASS. The memory evidence records repeated independent misses and fixes across B-TOOL-GATE, B-HITL-PLACEMENT, B-EDIT-CARRIER, B-FANOUT-PAUSE-SYNTHESIS, B-FANOUT-CRASH-RESUME-MAYBE-RAN-SUBAGENT, B-INTERSTEP-HANDOFF, and B-HITL-PLACEMENT-PER-STEP-LOOSEN. Each instance had a green partial or proxy witness that did not prove the real composed claim. |
| Genuinely §7.5-shaped | PASS. This is an execution/verification sequencing discipline: select the witness shape before claiming a mechanism is production-live or non-vacuous. It is not stale-carry-text disposition (§7.4.7) and not byte-exact claim grammar (§7.4.1-§7.4.6). |
| No canonical home elsewhere | PASS with cite-don't-relocate. PD-3 requires empirically matching verification shape; PD-5 requires grounding the producer/slice before authoring or closing. Neither states the stronger composed-chain rule: two correct half-proofs, a hand-built fixture, or a stubbed recursive child do not prove the real producer -> seam -> consumer path. |

---

## §1 Amendment to §7.5.2

### §7.5.2 Additive entry catalogued at v1.16

| # | Discipline | Statement | Independent-instance anchor | Application shape | Cross-reference |
|---|---|---|---|---|---|
| **PD-6** | **composed-chain non-vacuity witness** | When the claim is that a mechanism works through a production chain, prove the chain through the real producer, real shared surface, and real consumer in one witness. Producer-side tests that stop at the seam plus consumer-side tests fed hand-built or stubbed inputs do not prove the composed behavior. A witness that mocks the recursive child, hand-builds the risky serialized shape, or leaves an overlapping existing mechanism enabled can be green while the new mechanism is inert. | **>=6 independent arcs/families:** B-TOOL-GATE and B-HITL-PLACEMENT exposed producer/consumer half-proof gaps; B-EDIT-CARRIER exposed a consumer-mock gap; B-FANOUT-PAUSE exposed a hand-built-fixture serialization gap; B-FANOUT-CRASH-RESUME-MAYBE-RAN-SUBAGENT exposed a fake recursive-child gap; B-HITL-PLACEMENT-PER-STEP-LOOSEN and B-INTERSTEP-HANDOFF exposed non-vacuity requirements against overlapping/default mechanisms and real sync/async bridge paths. | Before claiming production-live behavior, identify the real chain boundary and choose one non-proxy witness through it. Disable overlapping default relief when proving a new opt-in mechanism. If no real composed witness exists yet, close honestly as buildable substrate/registered remainder rather than claiming the production path. | memory `[[full-chain-witness-not-half-proofs]]`, `[[built-but-vacuous-reground-ledger-asis]]`, `[[test-bypass-as-runtime-truth-pattern]]`, `[[verification-shape-sharpened-grep-vs-e2e]]`. Adjacent to PD-3 and PD-5; cite-don't-relocate rather than replacing them. |

---

## §2 Sections preserved verbatim at v1.16

Per delta-only convention, v1.16 touches ONLY this file's change-note, §1 PD-6 additive entry, §3 adjacent observations, and footer. The following are PRESERVED VERBATIM at predecessor-body layer:

- v1.15 PD-5 grounding-first producer/slice discovery and adjacent observations.
- v1.14 §7.5 scaffold, §7.5.1 inclusion gate, PD-1 through PD-4, §7.5.3 parked candidates, and §7.5.4 cross-catalogue discriminator.
- §7.4.1-§7.4.6 fidelity-grammar and §7.4.7 stale-carry-text disposition discipline.
- v1.13 + v1.12 + v1.11 + v1.10 + v1.9 + v1.8 historical anchors.

---

## §3 Adjacent observations

(a) **PD-6 is narrower than "write better tests."** It applies when a claim crosses a real producer -> seam -> consumer or overlapping-mechanism boundary. Pure helper behavior and single-layer invariants remain governed by PD-3's verification-shape discipline.

(b) **PD-6 complements PD-5.** PD-5 decides whether the lever is already built, buildable, absent, or live-gated before authoring. PD-6 decides whether the verification for a built slice proves the composed runtime claim without proxies or vacuous defaults.

(c) **Other cadence-4 candidates are not promoted here.** `hooks-codex-pilots-decorrelation-validated` / `codex-out-of-family-reviewer` remain owned by the R-600 out-of-family-review pilot and CLAUDE/Codex review tooling. `feedback-gate-only-on-meaningful-architecture-change` is already operator behavioral guidance in session rules. `subagent-landscape-reports-need-regrounding`, `cleared-spec-resolves-it-before-first-principles-fix`, and `built-but-vacuous-reground-ledger-asis` mostly reinforce PD-5/PD-6 and direct-source grounding rather than requiring separate workflow entries this cadence.

(d) **No §7.4.7 absorption owed.** Cadence-4 did not surface a new stale-carry-text disposition species. The promoted rule is process-discipline-shaped and lands under §7.5 only.

---

## Filing footer

| Field | Value |
|---|---|
| Version | v1.16 (narrow additive amendment to §7.5.2 adding PD-6 composed-chain non-vacuity witness; v1.15 PD-5 and v1.14 §7.5 scaffold preserved as predecessor body) |
| Trigger | `R-600-pattern-bake-in-sweep` cadence-4, 2026-06-30 |
| Supersedes | v1.15 as current workflow head only; all v1.15 bodies preserved verbatim as predecessor |
| Scope of revision | SUBSTANTIVE workflow-grammar amendment: NEW PD-6 entry + adjacent observations + footer. ZERO §7.4/§7.4.7 amendment; ZERO C-*-NN contract change; ZERO production-code change; ZERO cross-axis cascade. Co-publication: workspace `CLAUDE.md` governance pointer bump + clearance marker. |
| Cross-axis cascade | ZERO. v1.16 is process-discipline canonicalization; no per-axis spec / plan / CXA / production code touch. |
| Authority anchor | v1.14 §7.5.1 inclusion gate + §7.5.3 OPEN accumulation clause + `R-600-pattern-bake-in-sweep.md` cadence-4 survey |
| Predecessor | v1.15 (§7.5 PD-5 grounding-first producer/slice discovery) |
| Successor | (none — current canonical) |
| Date | 2026-06-30 |

---

*End of `Project_Workflow_v1_16.md` (delta over v1.15). v1.8 + v1.9 + v1.10 + v1.11 + v1.12 + v1.13 + v1.14 + v1.15 PRESERVED VERBATIM as historical anchors per delta-only-spec-file convention.*
