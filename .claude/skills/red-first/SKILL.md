---
name: red-first
description: Red-first implementation ritual for a single atomic unit — an Adversary subagent writes FAILING tests from the unit's acceptance criteria (one `# mutation-probe:` annotation per test), an Implementer then iterates to green without touching the test file, and the unit closes only when every annotation passes under `just mutation-probe`. OPT-IN ONLY — invoke it explicitly ("/red-first", "run U-XX-NN red-first", "have an adversary write the tests first"); it is never auto-invoked from roadmap-continue or ship-pr.
---

# red-first — the adversary-writes-the-tests-first ritual

A test written by the same context that wrote the implementation tends to pin the
implementation it happens to have, not the acceptance criteria it owes. This skill splits the
two: one context writes the tests from the ACs and nothing else, a second makes them pass and
is fenced out of the test file, and the unit closes on a mechanical witness
(`just mutation-probe`, U-WT-06) rather than on green alone.

## Opt-in only

**Opt-in only — never auto-invoked from `roadmap-continue` or `ship-pr`.** Neither of those
flows calls this skill, and neither should be edited to. It fires only when the operator asks
for it by name, or when this session deliberately chooses it for a unit whose ACs are crisp
enough to test blind. Running it on a unit whose ACs are vague produces an Adversary guessing
at the implementation — the exact failure this ritual exists to prevent.

## Phase 1 — Adversary (a plain Agent-tool subagent)

Spawn **one plain `Agent`-tool subagent**. Its prompt is self-contained (a subagent sees no
conversation context) and carries: the unit ID, its acceptance criteria **verbatim from the
plan**, the repo path, the test-file path to write, and the house test conventions. It does
**not** get the implementation sketch, the design you have in mind, or the source file's
current contents beyond what the ACs name.

**The Adversary is NOT the `harness-adversarial-reviewer` skill.** That skill is review-only
by hard rule — it red-teams *completed* artifacts and does not author. Invoking it here would
be a category error and it would refuse. The Adversary is an ordinary subagent given the
authoring prompt below; nothing about this phase routes through the reviewer skill.

The Adversary's contract:

1. Write tests that **FAIL against the current tree** — red is the deliverable, not an
   accident. A test that passes before any implementation exists proves nothing and must be
   rewritten or deleted.
2. Derive every assertion from the acceptance criteria only. No assertion may encode a
   private implementation choice (a helper's name, an internal call order, a log string the
   ACs never mention).
3. Annotate **every** test with exactly one line, immediately above the test, in this form:

   ```
   # mutation-probe: <file>:<lines>
   ```

   `<file>` is the **source** file the test claims to pin (repo-relative) and `<lines>` is
   `A-B` or a single `A` — the lines whose removal that test must turn red. Not the test's own
   lines. This annotation is the completion gate's input; a test without one cannot close.
4. Report the exact command that runs the test file, and the verbatim failing output.

## The handoff fence (sha256)

At the moment the Adversary hands off,
**record the test file's `sha256` and re-compare it at the completion gate**:

```bash
shasum -a 256 <test-file>            # record this digest in the arc's notes and the PR body
```

The Implementer may not edit that file. `git diff --name-only` is **not** an adequate fence:
an Implementer who edits a test and then reverts the edit, or who rewrites it to an
equivalent-looking form, leaves the same clean name list as one who never touched it. Only the
recorded digest distinguishes an untouched adversary test from an edited one. This is a
**recorded-digest fence, not a permission-guard deny** — no hook blocks the write; the gate
below catches it, and a mismatch is a `RED-FIRST: BLOCK`, not something to explain away.

If the ACs genuinely require a test change (the Adversary misread a criterion), that is a
**re-open**: go back to the Adversary with the correction, let it rewrite, and record a NEW
digest. The Implementer never edits the file directly.

## Phase 2 — Implementer (may not edit the adversary's test file)

The Implementer — this session, or a second subagent — iterates on the **source** until the
adversary tests pass. It may add its own tests in other files; it may not touch the adversary
test file, and it may not weaken an assertion by moving it. Every source change traces to a
failing adversary assertion.

## Completion gate

The unit closes only when **all** of these hold:

1. `shasum -a 256 <test-file>` equals the digest recorded at handoff.
2. The adversary test command exits 0.
3. **Every** `# mutation-probe:` annotation in the file has been executed and exited 0:

   ```bash
   just mutation-probe --file F --lines A-B --test "<the command that runs that test>"
   ```

   Exit 0 = the range is pinned. Exit 1 = the test stayed green with those lines removed (the
   test does not pin what it claims — fix the test through the Adversary, not the range). Exit
   2 = refused or indeterminate (dirty target file, already-red suite, syntax-breaking range) —
   that is **not** a pass; resolve it and re-run. Exit 3 = the restore did not complete; stop
   and repair the tree before anything else.

   `mutation_probe.py` refuses a target file with uncommitted changes, so **commit the arc's
   source work before running the gate**.
4. **Red evidence is in the PR body**: paste the failing output verbatim into the PR body,
   alongside the handoff digest and the per-annotation probe results. There is no Claude-side
   red ledger to write — `codex_loop.py` already carries one for the Codex flow, and pasted
   output is the witness here.

## CUT: no Breaker role

**CUT: no Breaker role.** An earlier shape of this ritual had a third agent trying to break
the implementation past the tests. It is deliberately not built: `merge-gate` reviewer 3
(test-witness adequacy) already reasons through a mutation probe on every code PR, and this
skill's completion gate performs the real one. A third role would duplicate both at the cost
of another full context.

## Verdict lines — fail closed

Each phase ends with **exactly one** line as its final non-empty line, mirroring `merge-gate`'s
protocol:

- `RED-FIRST: PASS` — the phase's contract is met in full.
- `RED-FIRST: BLOCK: <one-sentence reason>` — anything else.

Parsing is **fail closed**: missing, malformed, ambiguous, or truncated → treat as
`RED-FIRST: BLOCK: unparseable verdict`. Never read a silent or off-format response as a pass.
A digest mismatch, an unannotated test, a probe that exited anything other than 0, or a probe
that was never run are each a `BLOCK` on their own — they do not average out against the
passing ones.
