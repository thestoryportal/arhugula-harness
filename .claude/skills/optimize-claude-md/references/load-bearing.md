# Load-bearing content — keep the rule; you may tighten the words

The failure mode this skill exists to prevent is **silent governance drift**: an "optimization"
that quietly removes a guardrail the agent runs under. Byte reduction is trivial; reduction
*without* dropping discipline is the actual product. Before removing or relocating anything,
classify it.

## Two classes of content

**Load-bearing (KEEP).** Content that changes what the agent *does* — invariants, boundaries,
authority, protocols. You may tighten wording, dedupe a thrice-stated rule, or shorten an
example. You may **not** remove the rule, weaken its force (an imperative must not become a
suggestion), or relocate it somewhere it won't be loaded when it's needed. When unsure whether
something is load-bearing, treat it as load-bearing and flag the question instead of cutting.

> **Diff before you dedupe.** Two sections that *look* like restatements of each other — a
> "general statement" and an "operative restatement", a summary and its detail — are the trap:
> deduping by keeping the canonical-looking one and dropping the "redundant" one silently deletes
> any clause the dropped section carried *alone*. Before merging near-duplicates, diff them
> line-by-line and confirm every load-bearing clause unique to *either* survives the merge. The
> classic loss is a unique guardrail (a paid-call/secret boundary, an extra invariant) that
> appears only in the section you were about to call redundant. Dedup the genuinely-shared prose;
> never drop a section wholesale until you've verified it adds nothing the keeper already states.

**Relocatable (MOVE / COMPRESS).** *Reference* content — version-history lineage, change-note
chains, redundant restatement, pointer tables that mostly carry provenance, **and verbose worked
examples / walkthroughs** (illustration a fluent session no longer needs spelled out). Provenance
lives in git; a CLAUDE.md does not need to carry the saga, and it does not need every discipline
dramatized at length. This is where the bytes are (`measure.py` shows §2 "Canonical artifact
pointers" ≈ 81% of the root file) and where optimization should concentrate. Relocate via
`relocation-pattern.md` — never just delete a pointer; re-home it and leave a resolving reference.

> **An example can be a rule's only home.** Worked examples are *usually* illustration of a rule
> stated canonically elsewhere — relocate those freely. But an example sometimes carries the **sole
> statement** of a rule (a "here's what happens when a background run reaches a metered call"
> walkthrough may be the *only* place the paid-call/secret boundary is written down). Framing as an
> "example" does not make the rule optional. Before relocating an illustration/example block, check
> each example: is the rule it demonstrates stated as a rule *somewhere that stays loaded*? If yes,
> the example is pure illustration → relocate it. If the example is the only place that rule lives,
> it is load-bearing → keep it (or restate the rule in a section that stays). Relocating a worked
> example that is a rule's sole home drops the rule; `guardrails_preserved` hard-fails it.

The happy coincidence in this repo: the **heavy** content is mostly **relocatable** (pointer
tables + lineage), and the **load-bearing** content is mostly in the **short** sections. So the
highest-byte win and the lowest-risk move are the same move.

## Keep-list for the root `CLAUDE.md`

Derived from the repo's own stated invariants. Removing or weakening any of these is out of
bounds for an "optimization":

- **§1.3 Canonical authority chain** — who outranks whom when artifacts disagree.
- **§3.1 Committed stack** — the frozen technology decisions.
- **§4 Substitution + back-flow discipline** — esp. **§4.3 back-flow routing** and **§4.4 "NO
  silent H_T design extension at Phase 7"**. This is the **X-AL-3 line**; weakening it is the
  exact anti-pattern the skill guards against.
- **§5 Sub-agent boundary** — operative discipline + topology.
- **§8 Execution invariants.**
- **§10.5 Failure modes to actively prevent**, **§10.8 continuity discipline.**
- **§11 Posture declaration** + **§11.5 enforcement layers** — mode auto-detection + enforcement.
- **§12 Roadmap + drift-detection protocol** — §12.1 session-start audit, §12.2 post-PR-merge
  audit, §12.3 halt-and-reconcile. The deterministic next-action machinery.
- **§13.1 Always-on disciplines** — advisor-before-substantive-work, decorrelated review.
- **The paid-call / secret boundary**, wherever stated — never fire a paid provider call or
  relocate secrets unilaterally (operator feedback, load-bearing). An optimization must not
  soften this.

Per-axis `harness-*/CLAUDE.md`: **§4 "Substitution + anti-leakage surface"** is the load-bearing
core — and also the heaviest section. Tighten wording and relocate its *examples / lineage*, but
keep the anti-leakage rules intact. **§1 axis identity + scope boundary** and **§5 back-flow
channels** are load-bearing.

> This keep-list is a starting map, not a substitute for reading. Sections renumber as the file
> evolves — match on the *rule*, not the number. If a section moved, find where the rule went.

## The X-AL-3 hard scope line (the skill's own guardrail)

The skill must never edit `design-substrate/**`, per-axis specs, plans, ADRs, or fork docs —
editing those would *be* a silent H_T design extension. In scope: the tracked CLAUDE.md files +
`MEMORY.md` index hygiene. `measure.py` enforces this mechanically (it only ever reports
`git ls-files` CLAUDE.md paths; gitignored/vendored files never appear). The optimization pass
must touch nothing outside that set.

## Verify you didn't drop a guardrail

After producing the optimized file, diff old→new and confirm every keep-list rule is still
present and still imperative. `scripts/check_pointers.py` covers the cross-reference half
(links/paths/§refs still resolve). The two decorrelated reviewers (Codex + advisor) are the
backstop — but the keep-list is the *first* gate, and you run it yourself before proposing.
