# ADR-HE-2 — Review-gate and completion semantics

**Filed** 2026-08-17 · **Repo at** `17011f89c` · **Axes** operational discipline · action surface ·
**Class** Foundational (F) for the H_E review layer

**Scope.** What makes a verdict *count*. Companion to [ADR-HE-1](ADR-HE-1_loop_lanes_coordination_architecture.md)
(coordination), [ADR-HE-3](ADR-HE-3_record_and_measurement_substrate.md) (record + measurement), and
[ADR-HE-4](ADR-HE-4_defect_mechanization_and_grounding.md) (mechanization + grounding).
Corpus and authority chain: **HE-1 §0**.

---

## 1. Status

**ACCEPTED.** This record does not decide — it records **BUILD-PLAN Arc 1**, operator-ratified
2026-08-17, together with ratified decision **D-C**. One residual is genuinely open (§6).

---

## 2. Context

This is the sharpest instance of the probabilistic/deterministic boundary in the workspace: a
reviewer is an LLM, but **whether its output counts is a deterministic question** — and today that
question is answered by an exit code, which is not an answer at all.

**Two live defects, both found by the council rather than by either out-of-family reviewer, and both
unmet commitments rather than new policy:**

- **X1 / loop-D1 — an absent verdict can read as clean.** A reviewer CLI exits 0 having produced
  nothing. Zero-byte output ~3× in one session. On PR #1386 the log stayed **313 bytes for 130s
  after the process died**, with the real verdict — 4 findings including a P1 — existing only in the
  CLI's own session artifact under `~/.codex/sessions/`. **Re-reading the log is not sufficient.**
  The defect **recurred live during the very review pipeline that catalogued it**, when a reviewer
  CLI exited 0 having produced nothing but an auth error.
- **X2 / loop-D2 — 13.7% of CI runs are CANCELLED** (190/1,390), structurally identical to X1 one
  layer up.

**Asymmetric exposure.** `tools/codex_review.py` **does not exist [V]** while `tools/agy_review.py`
**does [V]** — so the Gemini path is hardened and the Codex path is a bare CLI invocation, which is
exactly backwards relative to which channel is in the mandatory chain.

**The decorrelation exposure, in its corrected form.** `merge-gate/SKILL.md:12-17` **[V]**, verbatim:
the three blocking lenses are *"lens-decorrelated, not vendor-decorrelated. Same model family, same
training-time blind spots."* An earlier claim that `codex-review` is the *only* cross-vendor channel
was overreach (corrected as E13) — `gemini-review` exists (`justfile:607`, `_require-antigravity`
**[V]**). The accurate statement: **for Claude-authored diffs the mandatory cross-vendor check is a
single non-blocking channel with a documented silent-death mode.**

---

## 3. Decision

> **A verdict counts only if it parses to the expected shape. An exit code is never a completion
> signal, a missing or malformed verdict is BLOCK-equivalent and never APPROVE-able, and every
> terminal state — reviewer and CI alike — is explicit rather than inferred from absence.**

**Committed (BUILD-PLAN Arc 1 + D-C):**

| # | Commitment |
|---|---|
| G1 | **Schema-parsed verdict.** A verdict counts only if it parses to the expected shape. **Exit code is never a completion signal** |
| G2 | **Permanent vs transient split.** A permanent failure (auth error) **skips the retry budget entirely** rather than consuming it — retrying an auth failure burns budget on a certainty |
| G3 | **`REVIEWER_UNAVAILABLE` is its own terminal state**, BLOCK-equivalent, **never APPROVE-able.** A dead reviewer must never read as clean |
| G4 | **Failover per D-C.** On primary failure, invoke the second cross-vendor reviewer under the **identical** validity check — **no relaxed bar** — then **block if it also fails** |
| G5 | **CI terminal states are `{SUCCESS, FAILURE, CANCELLED}`; CANCELLED is INCOMPLETE, never green** |
| G6 | **Escalation routes to the existing durable HITL queue**, default **TTL 24h** for a CI-blocking gate (operator may override; not separately ratified) |
| G7 | **Fail-closed wrapper for `codex-review`**, mirroring the hardened `agy_review.py`. Closes X1 and X8, which are the same defect from two directions |

**Standing constraints this decision must not violate** (R1 contradiction checklist):

- **#5** reviewer output fails closed on missing/malformed/truncated/ambiguous results — G1/G3/G7 are
  *enforcement of an existing invariant*, not new policy. Independently live at
  `merge-gate/SKILL.md:127` (*"Parsing — fail closed"*) and `ship-pr/SKILL.md:199` **[V]**
- **#14** a cancelled CI run is never credited as green — G5
- **#11 / #17** no elapsed-time target overrides an unresolved finding
- **#4** three fresh final lens reviews on the exact bound head; **#8** merge pinned with
  `--match-head-commit`; **#13** a re-attestation is never counted as an execution
- **#19** no workflow optimization becomes permanent merely because an evaluator emits GO

---

## 4. Rationale

**Why parse-not-exit-code.** Both CLIs exit 0 on total failure — this is measured, not theorized.
One run *fabricated four findings while executing zero tools*; another asserted a symbol did not
exist that lives in code and two tests. An exit code reports that a process ended, which is
orthogonal to whether a review happened. The only deterministic signal available is the shape of the
output, so that is what the gate must key on.

**Why re-reading the log cannot be the fix.** PR #1386 is the disproof: the log was frozen at 313
bytes for 130s *after* process exit while the real verdict lived in a different artifact entirely. A
retry-and-re-read loop would have read the same truncated 313 bytes and concluded clean. Only a
positive parse of an expected shape distinguishes "reviewed and clean" from "never produced output."

**Why the failover is not a quality downgrade** — the objection that must be answered, since a
failover superficially converts unavailability into a weaker check. It does not, because G4 holds the
fallback to the **identical** validity bar and **blocks if it also fails**. The failure mode a naive
failover would introduce — silently accepting a weaker reviewer's APPROVE when the primary died — is
structurally unreachable: there is no relaxed path, only a second attempt at the same bar followed by
a block. D-C therefore *strengthens* decorrelation rather than trading it away.

**Why CANCELLED needs naming even though no defect instance exists.** The evidence is genuinely
split, and both halves are correct. The loop arc called D2 live (13.7%, violating invariant #14); the
lanes council **struck** the equivalent X2 (R-1), on the grounds that CI cancels superseded runs
*intentionally* (`cancel-in-progress: true`), that cancellation **clusters on superseded pushes
rather than final heads**, and that two independent consumers already fail closed — with a live
sample of 170 success / 21 cancelled / 9 failure containing **no case of an unattended-cancelled
current final head**. Both hold because they answer different questions. **Verified here:**
`ship-pr/SKILL.md:199` **[V]** fails closed by requiring the merge commit's own run to be an exact
`success`, which excludes CANCELLED — but **`CANCELLED` appears nowhere in `ship-pr/SKILL.md` or
`arc_metrics.py` [V]**. The semantics are enforced *implicitly, by whitelist*. G5 makes them
explicit. That is a robustness improvement against a future edit that broadens the accepted set,
**not** the remediation of an observed defect — and this record declines to claim otherwise.

**Why the wrapper asymmetry is the priority.** The hardened path guards the advisory channel; the
bare path guards the mandatory one. G7 inverts nothing and adds no mechanism family — it mirrors an
implementation that already exists and is already trusted.

---

## 5. Consequences

**Becomes possible.** A reviewer's silence becomes a signal rather than an absence. Retry budget
stops being spent on permanent failures. Escalation has a defined destination and a clock.

**Becomes harder.** Every reviewer invocation now needs a declared output schema, which is a real
contract-authoring cost per channel. A transient-vs-permanent classifier must be maintained per CLI
and will drift as vendors change error text — this is the most likely future defect surface in this
record, and it is deliberately accepted because the alternative is treating all failures as transient
and retrying auth errors to the cap.

**Now constrained.** No future speed optimization may relax the validity bar for a fallback path
(#5, and G4's "no relaxed bar"). Mechanizing defect classes (ADR-HE-4) **never** licenses shortening
review generically (#20). No elapsed-time target overrides an unresolved finding (#11/#17).

**Interaction with lane parallelism — flagged, not resolved.** R1 invariant **#16** caps concurrent
preview reviewers at two and forbids a load probe overlapping a reviewer. Four lanes each running
reviewers, and the ratified plan's own reviewer-concurrency probe, both engage that cap. **v1 AC#5
adjudicated invariant #16 `void`** on the ground that its source plan (U-WT-09) was never adopted —
verified: `U-WT-09` has **0 matches** at HEAD **[V]**. Recorded here because the same reasoning
would void #1–#17 generally, yet #5 and #14 are treated throughout the corpus as *already ratified*.
**The reconciliation is that ratification travels by independent live carriage, not by source:** #5
is independently live at `merge-gate/SKILL.md:127` and `ship-pr/SKILL.md:199` **[V]**, so it binds;
#16 has **no independent carrier at HEAD — searched, not assumed [V]**: a sweep of `.claude/`,
`tools/`, `justfile` and `CLAUDE.md` for a concurrent-reviewer cap returned only two false positives
(a merge-gate *lens name*, `SKILL.md:81`, and a council co-primary cap in
`c2-context-engineering/SKILL.md:218` — voices, not reviewers). So v1's `void` adjudication stands
and **the four-lane reviewer-concurrency question is unconstrained by #16.** Any future appeal to a
numbered invariant should cite its live carrier, not the checklist.

---

## 6. Open item — operator-owned

**Which channel is the failover for Claude-authored diffs?** D-C ratifies automatic failover as the
*principle*; it does not name the channel for the common case. R1 invariant **#3** scopes
out-of-family review to **Codex-authored** work (*"Codex-authored work receives OAuth out-of-family
(Gemini/Antigravity) review"*), so today's `gemini-review` is authorship-gated away from exactly the
diffs the mandatory chain covers.

**Recommendation:** extend `gemini-review` to Claude-authored diffs as the D-C failover, holding it
to G4's identical bar. This closes AC#6 (decorrelation), which cannot close while `codex-review` has
no gate contract at all.

**Tiebreaker — RUN, and it resolves in favour of the recommendation. [V]** The question was whether
the authorship gate is implemented or is only R1 checklist prose. **It is prose.** Verified at HEAD:
the recipe is `gemini-review base='main': _require-antigravity` (`justfile:607`) invoking
`/usr/bin/python3 tools/agy_review.py --base {{base}}` (`:608`) — it takes a **base ref and nothing
else**, with no authorship parameter; and `tools/agy_review.py` contains **zero** occurrences of
`author` / `codex-authored` / `claude-authored`. The channel already reviews whatever diff it is
pointed at, irrespective of who wrote it.

**Consequence:** extending it to Claude-authored diffs is a **policy/documentation change, not a code
change** — the mechanism exists and is unrestricted today. What remains genuinely operator-owned is
narrow: whether to make that channel *blocking* (which is what converts it from an advisory lens into
a D-C failover), and whether invariant **#3**'s Codex-authored scoping should be restated rather than
silently outgrown.

---

## 7. Alternatives considered

| Alternative | Why rejected |
|---|---|
| **Exit code as the completion signal** (status quo) | Both CLIs exit 0 on total failure; measured, repeatedly. Reports process termination, not review occurrence |
| **Retry-and-re-read the log** | Falsified by PR #1386 — the log stayed at 313 bytes for 130s post-exit while the true verdict lived in a separate artifact. A re-read returns the same truncated bytes |
| **A flat numeric round cap** to bound review cost | Falsified by this repo's own data: PR #1034 ran 49 rounds with *"rounds 1–48 each fixed-and-mutation-probed or registered"*; PR #1338 produced P1s at rounds 1, 2, 3, 5, 7, 11, 13; a structured sample found round-2 P1-rate (75%) **above** round 1 (62%). A cap of 8 would have truncated #1034 with 40 rounds of genuine findings outstanding. Violates #11/#17 and #20 |
| **Treat CI-green as a review layer** | CI has **zero documented unique catches** of the classes that block merges here — it runs the tests the PR itself ships, so a tautological or falsely-annotated test passes *by construction*. PR #1349: CI 18/18 green, a lens still blocked a false spec claim. CI is a necessary floor, not a review layer |
| **Collapse decorrelated lenses to save wall-clock** | **93.4% of 679 findings across 146 PRs were caught by exactly one tool**; merge-gate BLOCKed 46% of 141 gated PRs with 32 numbered unique catches, several landing *after* 6–18 clean codex rounds on the same diff. Violates #3, #4, #18 |
| **Single-vendor mandatory chain** (no failover) | Contradicts ratified **D-C**. Also weaker than it appears: the objection it rests on (failover as silent downgrade) is answered by G4's identical-bar-plus-block construction. Recommended by this session's earlier review and **withdrawn** — see HE-1 §6 O2 |
| **A model-judge / eval-harness as the governance gate** | Standing workspace refusal, carried at v1 §10 |

---

## 8. References

**Verified at HEAD (`17011f89c`) this session.** `[V]` means exactly this.

- `.claude/skills/merge-gate/SKILL.md` — lens-vs-vendor decorrelation `:12-17` · *"Parsing — fail
  closed"* `:127` · cap → one batched `AskUserQuestion` `:150-153`
- `.claude/skills/ship-pr/SKILL.md` — fail-closed on the merge commit's own post-merge CI `:199` ·
  `state=MERGED` abort `:190-191`
- `CANCELLED` — **zero occurrences** in `ship-pr/SKILL.md` and `tools/arc_metrics.py`
- `tools/codex_review.py` **absent**; `tools/agy_review.py` **present**, containing **zero**
  `author`/`codex-authored`/`claude-authored` occurrences · `justfile:607-608` — `gemini-review
  base='main': _require-antigravity` → `python3 tools/agy_review.py --base {{base}}`, base-ref only
- `U-WT-09` — **0 matches** at HEAD (basis for v1 AC#5's `void` adjudication of invariant #16)
- **Absence searched, not assumed:** no concurrent-reviewer cap carrier in `.claude/`, `tools/`,
  `justfile`, `CLAUDE.md` (only a lens name at `merge-gate/SKILL.md:81` and a council co-primary cap
  at `c2-context-engineering/SKILL.md:218`)

**Ratified / council-recorded, not independently re-verified.** BUILD-PLAN Arc 1 and decision D-C
(`loop-eng-2026-08-16/BUILD-PLAN-operator-ratified-2026-08-17.md`) · R1's 20-item contradiction
checklist (`loop-eng-2026-08-16/R1-uwt09-prior-art.md` §7) · the PR #1386 / #1034 / #1338 / #1349
forensics and the 93.4% single-tool figure (`SYNTHESIS-loop-v2-reconciliation.md` §1, §3;
`STAGE7-FINAL-opus-grounded-findings.md` §3) · R-1's CANCELLED sample
(`HARNESS-LOOP-AND-LANES-DESIGN-v2.md` §10a)

---

## 9. Filing footer

§3 is ratified; §6 is not. Superseding requires a new `ADR-HE-N` citing this one. H_E tooling only —
the H_T authority chain is out of scope by construction (see HE-1's namespace note).
