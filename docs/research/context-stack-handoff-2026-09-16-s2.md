# Context-stack program — session-2 handoff (2026-09-16, evening)

> **Status, 2026-09-17: closed. Nothing in this file is owed.** Every item of §2 landed or
> was deliberately refused — PRs #1540, #1542, #1544, #1546, #1548, and U-HE-43 merged. §2
> now records what each came to; §3 is still live guidance for any arc in this workspace.
> Item §2 B was closed by *refusal* and is pinned by a test — read it before re-proposing it.

Read this first; it supersedes §4 of `context-stack-handoff-2026-09-16.md` for ordering, and
that file's §5 records the grounding this session did. Everything below is bound to
`main` at `5785338cd` (refresh #1539) unless a sha says otherwise.

## 1. State at handoff

| Fact | Value |
|---|---|
| Landed this session | PR #1538 → `a436658ac` (main run green); terminating refresh #1539 → `5785338cd` |
| Arc | `preflight-finding-intake`, reservation `merged`, lane `Roberts-MacBook-Pro-arhugula-v2-d56be5f6` |
| Roadmap pointer | installed by the door from `.harness/.next-action-draft`; ends "then U-HE-43" |
| Untracked in the root checkout | `docs/research/` (this program's whole record), `docs/diagrams/code-loop/visual-check/` (pre-existing, not ours) |
| Checkpoints | `~/.gstack/projects/arhugula-v2/checkpoints/20260916-165858-preflight-finding-intake-landed-1538.md` (arc close) and the one written after this file |
| Memory touched | `context-stack-program-state-2026-09-16`, `prose-obligation-needs-an-enforcing-venue` (new), `in-place-bg-job-venue-traps`, `bash-concurrency-and-parsing-gotchas` |
| Branch hygiene owed | `feat/preflight-finding-intake` (#1538) and `roadmap-refresh-post-1538` (#1539) — **closed 2026-09-17**; neither branch remains on `origin` |

What #1538 is, in one paragraph, so you can reason about it without reading the diff:
`refresh-classes.py classify` is a pure verb (JSON findings in, `{finding_id: [class names]}`
out). `just review-template-sweep` stamps each outstanding reviewer finding with its classes
and pre-fills `intake: TODO(answer)` under an UNMATCHED one. `just review-attest-sweep`
parses the slot (`class-extended <n> …` | `new-class <name> …` | `instance-only <reason>`),
re-classifies with the class table **as committed at HEAD**, refuses a repair claim the
table does not show, and records `instance-only` ids on the attestation. Class 15 "bound
bytes are not the executed bytes" was opened by this mechanism on its own codex round.
The end-to-end witness is `tools/test_review_loop_gate.py::test_one_finding_flows_into_the_class_table_end_to_end`.

## 2. That work, and what it came to

**All six items are closed; nothing below is owed.** Session 3 (2026-09-16) ran A–E as
five arcs and F merged separately. This section is kept as the record of what was decided
and why — read it before proposing any of it again. Item B was closed by *refusal*, and is
the one most likely to be re-proposed by someone skimming. The live results record is
`context-stack-evals/README.md`, rows E1–E8.

### A. Commit `docs/research/` — done, PR #1540

`docs/research/` is tracked, 49 files. The oversized and regenerable run inputs were left
out, and the exclusion is now enforced rather than remembered:
`context-stack-evals/.gitignore` carries `E2/*.diff`, `E2/prompt_*.txt`, the two `E2b/`
twins, `E6-vault/`, `*.log` and `E7/*.err`, and the README says what each excluded set
was. The scripts' hard-coded `/Users/robertrhu/…` paths were resolved before commit; none
remain.

### B. Class 2 `drift` extension — measured and REFUSED, PR #1542

**Do not re-propose this.** At the 2026-09-16 corpus of 2,103 findings, 35 rows said
"drift" and 30 matched no class-2 term — which is what made the extension look like ten
minutes of free coverage. Read them, though, and they are contract drift, configuration
drift, roadmap drift and the arc-metrics `drift` cohort. Prose decay in the class-2 sense was at most 2
rows under any prose-adjacent form tried, so a bare `\bdrift` would have pulled 30 rows
*out* of the new-class intake pile: the wrong direction under the intake policy.

The refusal is pinned in three places, so it holds without this file:
- the LEFT OUT note at `.claude/skills/defect-class-preflight/scripts/refresh-classes.py:53-62`;
- `tools/test_refresh_classes.py::test_bare_drift_is_not_class_2_vocabulary`, which fails
  if class 2 ever claims those rows;
- class 16, "witness codifies the divergence", which claims the recurring "test codifies
  the drift" shape this item was really pointing at.

The item's cheap second half did land in the same PR: the witness lens's P3 is now
`tools/test_refresh_classes.py::test_report_counts_agree_with_classify`.

### C. E4 with real questions — done as E4b, PR #1544. Verdict: AUGMENT.

Twenty operator-shaped questions, ground truth session id and turn, threshold written
before the run. Session hit@1 9/20, session hit@5 12/20, turn hit@1 7/20, turn hit@5 8/20 —
short of the POINTERS bar. Memory stays the authority; the index answers "where did that
come from". Full run at `context-stack-evals/E4b-results.md`.

### D. E2 on code with callers — done as E2b, PR #1546. Verdict: precision, not recall.

Two PRs whose depth-2 blast radius was non-empty, same four-reviewer design, every finding
verified by reading the cited file at the reviewed commit: 6 reported, 4 verified in full,
2 verified with a qualification, 0 refuted. Supported for precision, not recall, at n=2.
The operating lesson: attach the ~3 KB blast markdown to the out-of-family prompt and judge
by citation accuracy. The run opened two register rows — B-248 (B-162's AST site counter
sees 3 of 11) and B-249 (B-71's token population is wider than CP v1.119's wording, filed
as a fork). Full run at `context-stack-evals/E2b-results.md`.

### E. E3 reconfiguration — done as E3b, PR #1548. Verdict: embeddings add nothing.

Scoring only claimed-identical pairs turned up exactly one real drift out of the whole
governance pack: `docs/governance/project-framing.md:3` claimed a byte-verbatim relocation
of root `CLAUDE.md` §7 into a pack that has never carried a §7
(`context-stack-evals/E3b-results.md:33`). §7 was relocated to
`docs/governance/skills-and-subphases.md`, whose own header correctly claims it. Every
other claimed-identical pair was byte-identical. A normalised diff finds all of it;
embeddings add nothing where the claim is identity.

**Fixed with this supersede — and the fix was four carriers, not one.** E3b scanned
relocation *headers*, so it saw the one at `project-framing.md:3`. The same wrong claim
had been copied into the three pack-routing tables that tell an agent which file to load:
`CONTEXT.md:33`, `docs/governance/README.md:15` and `AGENTS.md:8` all listed §7 — and two
of them described it as "the Phase 7 sub-phase enumeration" — under `project-framing.md`,
so an agent that needed §7 would have loaded a pack that does not contain it. Treat the
E3b count as a floor: it measures headers, not the routing tables that quote them.

Nothing witnessed this until now. `tools/test_governance_router.py` compared pack
FILENAMES across the three venues, never the §-lists beside them, so reinstating the wrong
claim in `project-framing.md:3` and `CONTEXT.md:33` left the module green at 10 passed.
Rows 11 and 12 of that module's mutation table now close it:
`test_pack_sections_match_origin_header` reads each pack's origin header and requires set
equality against the pack's own headings, and
`test_venues_advertise_pack_section_list` requires each of README.md,
CONTEXT.md and AGENTS.md to advertise that same set (resolving `§A–§B` and the `§N.x`
shorthand against the pack's headings, so a venue may abbreviate but not misstate). Both
go red on each of the three defect shapes, verified by mutation probe. The new witness
immediately found a second, older drift: `AGENTS.md` advertised `roadmap-protocol.md` as
`§12.1–§12.3, §12.5.x`, omitting the `§12` the pack carries and both other venues list.
Fixed here too.

### F. U-HE-43 — merged.

## 3. Mechanics a fresh session will hit

- **Venue.** If the session is an in-place background job, `just codex-check` reds exactly
  `tools/test_codex_stop_gate.py::test_stop_gate_emits_valid_stop_hook_json`
  (`ROOT_CHECKOUT_EDIT`). CI's own
  checkout passes; state it in the PR body. `just codex-context-check-ci` on the committed
  range is the authority.
- **Local pyright.** Run `uv sync --all-packages` once; before it `uv run pyright` reported
  11,699 errors from unsynced members (CI shape is 0).
- **`arc_disjoint_check` exit 1 is often not about your arc.** It `git merge-tree`s each
  sibling head against your candidate, so a sibling that is merely STALE against `main`
  reports CONFLICT on the files `main` moved — with your candidate set to an unmodified
  `origin/main`, and again with this arc's commit on top, it named the same four
  `.harness/` paths, none of which either candidate touched. Read the paths before
  re-deriving: if none is yours, the refusal is inherited and no unit choice clears it.
- **Arc ceremony that worked, in order:** `arc_disjoint_check.py check --candidate HEAD` →
  `reservations.py reserve` → commit → `review-template-preflight` / fill / `review-attest-preflight`
  → `review-with-failover-logged .harness/tmp/<arc>-rounds/r1.log` (background, 600 s timeout
  was enough) → adjudicate each finding **as a literal id, one call each** (a zsh `for id in
  $IDS` over newline-joined ids passed all ids as one argument) → absorb, commit →
  `review-template-sweep` / fill / `review-attest-sweep` (your own arc's findings now get the
  intake treatment) → push once → `gh pr create` → `reservations.py update --set pr=…` →
  `merge-gate-binding <lens>` → lens Agent (sonnet) → ask the lens to write its full message
  to `.harness/tmp/merge-gate-lens-<id>.txt` (a stale file from an earlier arc sits at that
  path; check the mtime before emitting) → `merge-gate-emit --lens …` → narrative md row →
  commit gate rows → push by sha → CI green → `reservations.py update --set head_sha base_sha
  attested_merge_tree` → `transition --to open` → `.harness/.next-action-draft` →
  `safe-merge.sh <pr>` (background; it merged, waited main, opened and merged the refresh) →
  `/context-save-lean` → `just arc-close …` → `defer.sh` branch-hygiene row.
- **`DESIGN_IMPL_MIX` does not fire on `docs/**`** — §2 A of this file used to say it did,
  and that was never checked. `DESIGN_RE` at `tools/codex_context_guard.py:25-28` matches
  `design-substrate/`, `.harness/class_[123]_`, `.harness/architect_recommendation_`,
  `Spec_*_v<n>`, `Implementation_Plan_*_v<n>` and `ADR-[FD]<n>` — nothing under `docs/`.
  Bundling `docs/**` with code is a review-scope judgement, not a gate refusal.
- **Doc-only does NOT keep an arc off the gate ledgers.** Skipping the three-lens merge-gate
  is not the same as writing no gate rows: the mandatory codex round publishes a
  `no_finding` / `finding` / `reviewer_unavailable` row through
  `tools/review_wrapper_common.py:454-496` into `.harness/merge-gate-log.jsonl`. This arc
  proved it — it opened believing a doc-only PR could not collide with a sibling lane on
  the ledgers, and its own round-1 row landed in the file two sibling lanes were holding.
  Plan for a hand-resolved ledger conflict on any arc that runs a reviewer at all; never
  `merge=union` on the append-only ledgers (B-255).
- **Lean protocol for tooling and doc arcs** (memory `feedback-b230-lean-protocol-one-codex-round`):
  one codex round, absorb P1/contract findings, single witness lens only when gate mechanics
  change, no round 2.
- **Do not run `graft build` in the shared checkout**; it regenerates four tracked files
  (memory `graft-build-regenerates-tracked-files`).
- **Operator rules in force:** no metered API calls (subscription and local only); no
  unilateral paid calls or secret relocation in a background job; workspace deps stay
  torch-free (the Pixeltable tool env is where torch lives).

## 4. Open questions only the operator can answer

- ~~Whether `E6-vault/` and the ~600 K of E2 prompt files belong in git at all (item A).~~
  **Answered by #1540:** they stay out, enforced by `context-stack-evals/.gitignore`, with
  the README recording what each excluded set was.
- Whether `instance-only` intakes should carry a cap or a review trigger; today the rate is
  recorded on the attestation and nothing acts on it.
