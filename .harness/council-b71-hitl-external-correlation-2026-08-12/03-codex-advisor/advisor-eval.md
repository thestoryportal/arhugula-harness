# E3 — advisor() (in-family, transcript-aware)

*(Genuine advisor invocation with the arc's failure history in view, Sonnet,
2026-08-12. Key content verbatim.)*

**Verdict: PROCEED-WITH-CONDITIONS.**

## (a) Is this attempt different? Yes — with one residual premise of the same class

All three historical falsified premises are closed with direct code cites rather
than restatement. "The self-correcting texture is the more important signal than any
single closed premise": C1 split-falsified its OWN echo claim at S4, C10 conceded a
wrong citation at S3 — **both corrections happened before the design record froze,
which is the discipline the fifth-round-reverted attempt lacked. That attempt's
rounds each discovered a wrongness in what had already shipped, not in what was
still being drafted.**

**The one unexecuted premise:** tree-wide uniqueness of
`(parent_idempotency_key, branch_index, placement.position)`. C1 rates it [HIGH] but
names its own falsifier as a collision-witness test **that is never actually run in
this docket, only argued analytically**. Every collision scenario walked is
two-peers-sharing-a-`child_workflow_id` or one-branch-two-placements; **a nested
fan-out case is never constructed. This is exactly the shape of claim that falsified
premise 3.**

## (b) Non-convergence risk — coherent single arc, IF scoped to the absorbed list

The qualitative difference from the reverted attempt: every touched surface is a
mechanical instance of an already-established codebase pattern, not an independent
judgment call discovered mid-fix — the capture/construction sites mirror an existing
shape, the pass-through sibling mirrors three existing fields, the audit-key widening
mirrors the `branch_path`/U-CP-83 precedent. **The prior failure was rounds correcting
different wrong layers; here the layers were identified up front, in one pass, each
pinned to a precedent, and none contradicts another.** The seam to actively defend:
if drafting pressure folds a registered item in "while we're in there," that is the
thrash pattern reopening.

## (c) Scope discipline — right, and shows real X-AL-3 discipline

The absorb/register discriminator is applied consistently. Item 6's "named companion
leg, not a deferral" status is the correct shape and matches the B-72 multi-leg
precedent.

## (d) The sequencing condition — real, not over-coupling

`resolvability_note`'s promise is a factual claim about system behavior; without item
6 it is **"a lie in the wire payload, not a rough edge."** And it is self-defusing —
C1's stated fallback (soften the wording in the same commit) means it cannot stall
the spec leg.

## (e) What would make this fail a fourth time (ranked)

1. **The unexecuted collision-witness turns out false** — the single highest-probability
   replay of the premise-3 failure mode.
2. The `_execute_parallelization` mirror sites turn out asymmetric with the primary
   capture sites (verified by name-match grep, not by reading both bodies in full).
3. Persist-once precedence not actually enforced in impl → two-mint drift as a live bug.
4. The OD sixth witness is false — some consumer splits the action_id by segment count.
5. Spec-leg drafting stops re-grounding cites at write-time.

## (f) Readiness + highest-risk element

> The tree-wide-uniqueness claim is the one load-bearing property in this entire
> design that is asserted at [HIGH] confidence but **never actually tested** — every
> other major claim was either verified by re-reading code at HEAD or explicitly
> downgraded with a named falsifier. This matters specifically because B-71's third
> failure was exactly a false disambiguation claim that nobody ran to ground before
> it entered a fix. **Sound reasoning about a uniqueness property is precisely the
> failure category this register row exists to distrust.**
