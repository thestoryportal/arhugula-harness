# Project Workflow — v1.18 (delta over v1.17)

---

## Change-note (v1.17 -> v1.18)

**Scope of revision.** Narrow additive amendment to §7.5.2, cataloguing one new process discipline: **PD-8 mutation-probe-as-load-bearing-witness**. v1.17's PD-7 disposition-label-is-a-claim, v1.16's PD-6 composed-chain non-vacuity witness, v1.15's PD-5 grounding-first producer/slice discovery, and all v1.14 §7.5 scaffold content are preserved as predecessor body; v1.18 adds exactly one discipline plus adjacent observations and footer. ZERO §7.4 / §7.4.7 amendment; ZERO contract change; ZERO retirement-event filing; ZERO production-code change; ZERO cross-axis cascade.

**Trigger (R-600 cadence-8, 2026-07-14).** `R-600-pattern-bake-in-sweep` reached its next cadence after the cadence-7 survey at post-PR-973. **Merge count (corrected — a 4th round of out-of-family Codex review caught that a hand-enumerated PR list undercounted, the exact failure mode PD-8 itself warns against; the fix is to cite the reproducible command, not hand-list again):** `git log --first-parent --oneline 9cad319e..380ec161 | wc -l` → **23** merged PR commits since cadence-7's close (`9cad319e`) through this arc's own predecessor commit (`380ec161`) — well past the ~10-PR interval either way. Cadence-7 flagged one card-frontier token as "not yet consolidated" rather than promoting or dropping it: the mutation-probe technique (deliberately break the code a regression test is supposed to pin, confirm the test fails, then restore) was recurring across independent arcs but lived only as sub-content inside a reviewer-ladder tooling file (`codex-out-of-family-reviewer.md`), absent from a dedicated, independently-named entry, and cadence-7's own write-up said "re-evaluate at the next R-600 cadence." This is that deferred re-evaluation. **Correction (caught by out-of-family Codex review of this arc's own PR, pre-merge):** `mutation-probe-load-bearing-witness.md`'s mtime is `2026-07-14T00:32:48-06:00` — 17 minutes **before** cadence-7's own close commit (`2026-07-14T00:49:43-06:00`), not a file-delta discovery *since* cadence-7 close. The file already existed when cadence-7's own write-up flagged it (same close-out session, moments before the closing commit). Cadence-8 performs cadence-7's own explicitly-deferred re-evaluation of an already-known candidate; the §7.5.1 gate application below is unaffected by exactly when the file was created, only by what it demonstrates.

**Provenance note.** The discipline's independent-arc backing was itself corrected during this arc's own out-of-family review (caught pre-merge, applying **PD-7's own discipline to this promotion**: a claimed instance-count is a claim, verify it against the primary source — here, `gh pr view --json mergedAt` and each commit's own `Claude-Session` trailer, not the memory file's self-reported "3 arcs"). PR #927 (merged 2026-07-11T06:51:07Z) and PR #933 (merged 2026-07-11T17:09:22Z) share the identical `Claude-Session` trailer (`session_01VjkgZRnJXJNZYycJ6fb5GK`) — same session, same underlying lesson (the `task.result()` resurface check), applied to two sibling PRs in the CP-axis `B-18-3C-PREWARM` family. Per the cadence-2 producer-discovery same-day/same-session/same-lesson discriminator, these collapse to **one** instance, not two. The corrected, honest count is **2 genuinely independent instances**: the #927/#933 session (one instance) + PR #972 / `B-26` (merged 2026-07-14T06:09:26Z, a wholly separate session, three days later — a **second round of Codex review on this same v1.18 PR** further caught that #972/`B-26` is itself CP-axis, not IS-axis: its commit is `fix(cp)` wiring real IS hash-chain verification into a CP-owned module (`harness_cp/five_axis_composition.py`), a CP→IS seam, not a separate axis; the same review also caught the probe count was overstated at 4 when direct read of the actual test diff shows exactly 2 distinct discriminating-witness mutation-probes in that PR (an empty-ledger probe + a combined hash-chain/downstream-blocking probe — see the corrected gate table below). This is a **newly-consolidated** discipline per the PD-7 provenance-honesty framing: the underlying behavior recurred before this cadence; the named, citable pattern consolidated only within the cadence-6/7 inter-cadence window.

**Authority anchor.** v1.14 §7.5.1 inclusion gate + §7.5.4 cross-catalogue discriminator + §7.5.3 OPEN accumulation clause + `R-600-pattern-bake-in-sweep.md` cadence-7 card-frontier flag + cadence-8 survey evidence. This amendment promotes the recurring lesson that a regression test's green result is not, by itself, proof the test discriminates the fix from its absence — that requires an explicit fault-injection check.

**§7.5.1 inclusion-gate application.**

| Gate | Finding |
|---|---|
| Instance-cardinality >=2 of independent arcs | PASS, with an honesty caveat (mirrors the cadence-2 PD-5 precedent). 2 genuinely independent instances, verified via `gh pr view --json mergedAt,files` + each commit's `Claude-Session` trailer, not the memory file's self-reported count: (1) PR #927 + PR #933 (both 2026-07-11, CP `B-18-3C-PREWARM-CASCADE` / `B-18-PREWARM-OW`) share the identical `Claude-Session` trailer — same session, same lesson (the `task.result()` resurface check applied to two sibling PRs), collapsing to ONE instance per the same-session-same-lesson discriminator; (2) PR #972 / `B-26` (2026-07-14, a wholly separate session, 3 days later — CP-axis, `fix(cp)`, wiring real IS hash-chain verification into `harness_cp/five_axis_composition.py`, a CP→IS seam rather than a separate axis): direct read of the committed test diff shows exactly **2** distinct discriminating-witness mutation-probes, not 4 — `test_empty_ledger_does_not_fake_success` (the empty-ledger gate) and `test_hash_chain_step_broken_chain_fails_rotation` (a single probe whose assertions cover both the hash-chain-succeeded gate AND the downstream-step-blocking behavior in one revert-and-restore). **Live-verified and reproducible (2026-07-14, this arc) — see the reproduction recipe immediately below this table.** 2 instances clears the literal gate but at the thinnest margin of any PD promoted so far — recorded honestly rather than as "3 distinct arcs," and the #972 probe count corrected from an overstated "4" to the actual "2." |
| Genuinely §7.5-shaped | PASS. This is a verification-sequencing discipline: after a regression test is written and green, prove it is load-bearing via fault injection before trusting it. It is not stale-carry-text disposition (§7.4.7) and not byte-exact claim grammar (§7.4.1-§7.4.6). |
| No canonical home elsewhere | PASS with cite-don't-relocate to PD-3 and PD-6. PD-3 requires matching verification *shape* to the claim (grep vs. e2e); PD-6 requires proving a *composed chain* is real, not proxied. Neither states the narrower, sharper rule that a test **as written** must be shown to discriminate the fix from its absence — a test can pass at the right verification depth, through the real composed chain, and still be green for the wrong reason (a fixture that accidentally satisfies both the old and new code paths, or an assertion weaker than the claim). PD-8 is that missing check. |

**Reproduction recipe for the gate-1 live-verification claim above** (a 3rd round of out-of-family Codex review asked for execution evidence, not just historical self-report; a 4th round then asked for the exact runnable commands rather than a `...::test_*` placeholder summary; a 5th round caught this recipe had been placed inside the table itself, which breaks GFM/CommonMark table rendering after the first data row — moved out here as its own subsection so all three gate rows render correctly):

1. Baseline: `uv run --package harness-cp pytest harness-cp/tests/test_five_axis_composition.py::test_hash_chain_step_broken_chain_fails_rotation harness-cp/tests/test_five_axis_composition.py::test_empty_ledger_does_not_fake_success -v` → `2 passed`.
2. Mutate: in `harness-cp/src/harness_cp/five_axis_composition.py`, insert the single line `    hash_chain_succeeded = True` immediately before the `simulated_suffix = (` line that follows the `if not entries: / elif chain_result.failure_type is None: / else:` block inside `verify_rotation_6_steps` (the line directly after the `else:` branch's `hash_chain_detail = (...)` assignment) — this hardcodes the pre-fix behavior, unconditionally overriding whatever the if/elif/else block just computed.
3. Re-run the identical command from step 1 → `2 failed`, both `AssertionError: assert True is False` (the exact expected assertion, not an unrelated crash/import error).
4. Restore: delete the inserted line from step 2.
5. Re-run the identical command from step 1 → `2 passed`; `git diff harness-cp/src/harness_cp/five_axis_composition.py` → empty; full-file re-run (`... test_five_axis_composition.py` with no node filter) → `14 passed`.

This is first-hand proof PD-8 was genuinely performed for this instance, not merely a self-reported historical claim, and is reproducible by anyone against current HEAD using the exact steps above.

---

## §1 Amendment to §7.5.2

### §7.5.2 Additive entry catalogued at v1.18

| # | Discipline | Statement | Independent-instance anchor | Application shape | Cross-reference |
|---|---|---|---|---|---|
| **PD-8** | **mutation-probe-as-load-bearing-witness** | When a fix's correctness rests on "this regression test proves it," don't stop at green: temporarily revert the fix (comment it out, hardcode the old value, or otherwise reintroduce the exact defect), re-run the specific test, confirm it fails with the EXPECTED assertion error (not an unrelated crash), then restore the fix and re-verify green. A test can be green for the wrong reason — it never exercises the branch that would fail under the bug, its fixture accidentally satisfies both the old and new code paths, or it asserts a weaker property than the one actually claimed — and mutation-probing is the cheapest way to prove the test discriminates the fix from its absence rather than merely happening to pass. | **2 independent instances (cardinality-qualified, not overstated):** PR #927 + PR #933 (both 2026-07-11, same `Claude-Session` trailer — collapse to one instance per the same-session-same-lesson discriminator) + PR #972 / `B-26` (2026-07-14, CP-axis, wiring a CP→IS hash-chain-verification seam, a separate session, 2 discriminating-witness probes in one PR). See change-note provenance note above and `R-600-pattern-bake-in-sweep.md` cadence-8 §1-§2 for the per-arc detail. | After writing a regression test for a real bug/gap: (1) temporarily revert just the fix (comment out, hardcode the old value, or otherwise reintroduce the exact defect); (2) re-run the specific test and confirm it fails with the EXPECTED assertion error, not an unrelated crash; (3) restore the fix (via file-copy backup or direct string-replace-back — never `git checkout --`, which wipes all uncommitted work, not just the mutation) and re-verify green. Especially valuable for branch-blocking/gating logic, empty/absent-evidence guards, and any fix a decorrelated reviewer flagged as suspect. Cheapest as a scripted swap-mutate-run-restore, not a manual multi-minute detour. | memory `[[mutation-probe-load-bearing-witness]]`, `[[safe-mutation-probe-no-git-checkout-restore]]` (the git-safety corollary for the restore step). Adjacent to PD-3 (`[[verification-shape-sharpened-grep-vs-e2e]]` — matching verification *depth* to the claim) and PD-6 (`[[full-chain-witness-not-half-proofs]]` — proving the *chain* is real); PD-8 is the narrower, sharper check that the test **as written** actually discriminates the fix from its absence — cite-don't-relocate rather than merging into either. |

---

## §2 Sections preserved verbatim at v1.18

Per delta-only convention, v1.18 touches ONLY this file's change-note, §1 PD-8 additive entry, §3 adjacent observations, and footer. The following are PRESERVED VERBATIM at predecessor-body layer:

- v1.17 PD-7 disposition-label-is-a-claim and adjacent observations.
- v1.16 PD-6 composed-chain non-vacuity witness and adjacent observations.
- v1.15 PD-5 grounding-first producer/slice discovery and adjacent observations.
- v1.14 §7.5 scaffold, §7.5.1 inclusion gate, PD-1 through PD-4, §7.5.3 parked candidates, and §7.5.4 cross-catalogue discriminator.
- §7.4.1-§7.4.6 fidelity-grammar and §7.4.7 stale-carry-text disposition discipline.
- v1.13 + v1.12 + v1.11 + v1.10 + v1.9 + v1.8 historical anchors.

---

## §3 Adjacent observations

(a) **PD-8 is narrower than "write good tests."** It applies specifically to the moment right after a regression test is written for a real bug/gap and goes green — the discipline is proving THAT SPECIFIC test discriminates the fix from its absence, not general test-quality or coverage discussion (which PD-3/PD-6 already partially cover from adjacent angles).

(b) **PD-8 complements PD-3 and PD-6, it does not replace either.** PD-3 answers "does the verification shape (grep vs. e2e) match the depth of the claim being verified?" PD-6 answers "does the witness prove the real producer -> shared-surface -> consumer chain, not a proxy?" PD-8 answers a question that survives both: "even granting the right depth and the right chain, does the test as written actually fail when the fix is absent?" A test can satisfy PD-3 and PD-6 and still be green-by-construction if it never truly exercises the failing branch.

(c) **Cadence-7's other flagged/touched tokens are not promoted here.** `codex-out-of-family-reviewer.md`'s own new content this window (model-upgrade tooling note; the two review-ritual sharpenings that seeded this PD-8 candidacy) remains reviewer-ladder tooling guidance, already homed. `fanout-pause-per-strategy-carrier.md`'s new content (the `B-21` cross-carrier port byte-compat lesson) remains domain-specific CP-axis runtime-implementation mechanics per the cadence-5/cadence-7 "dedicated home, not §7.5" precedent (`new-surface-audit-hash-and-config-not-carrier`).

(d) **No §7.4.7 absorption owed.** Cadence-8 did not surface a new stale-carry-text disposition species (the 8th independent null-result surfacing across cadence-1 through cadence-8). The promoted rule is process-discipline-shaped and lands under §7.5 only.

(e) Evidentiary claims underlying this promotion (arc count, axis attribution, probe count, merge count) were corrected across out-of-family review before merge; the promotion rests on 2 live-verified independent instances, reproducible via the recipe above — see commit history for the correction detail.

---

## Filing footer

| Field | Value |
|---|---|
| Version | v1.18 (narrow additive amendment to §7.5.2 adding PD-8 mutation-probe-as-load-bearing-witness; v1.17 PD-7, v1.16 PD-6, v1.15 PD-5, and v1.14 §7.5 scaffold preserved as predecessor body) |
| Trigger | `R-600-pattern-bake-in-sweep` cadence-8, 2026-07-14 |
| Supersedes | v1.17 as current workflow head only; all v1.17 bodies preserved verbatim as predecessor |
| Scope of revision | SUBSTANTIVE workflow-grammar amendment: NEW PD-8 entry + adjacent observations + footer. ZERO §7.4/§7.4.7 amendment; ZERO C-*-NN contract change; ZERO production-code change; ZERO cross-axis cascade. Co-publication: workspace `CLAUDE.md` governance pointer bump + clearance marker. |
| Cross-axis cascade | ZERO. v1.18 is process-discipline canonicalization; no per-axis spec / plan / CXA / production code touch. |
| Authority anchor | v1.14 §7.5.1 inclusion gate + §7.5.4 cross-catalogue discriminator + §7.5.3 OPEN accumulation clause + `R-600-pattern-bake-in-sweep.md` cadence-7 card-frontier flag + cadence-8 survey |
| Predecessor | v1.17 (§7.5 PD-7 disposition-label-is-a-claim) |
| Successor | (none — current canonical) |
| Date | 2026-07-14 |

---

*End of `Project_Workflow_v1_18.md` (delta over v1.17). v1.8 + v1.9 + v1.10 + v1.11 + v1.12 + v1.13 + v1.14 + v1.15 + v1.16 + v1.17 PRESERVED VERBATIM as historical anchors per delta-only-spec-file convention.*
