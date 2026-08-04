---
name: red-first
description: Use only when the operator explicitly asks for a red-first unit — an adversary session writes failing, probe-annotated tests from the acceptance criteria before any implementation, and an implementer session drives them green without editing them.
---

# Red First

Split test authorship from implementation for one atomic unit. One session writes failing
tests from the acceptance criteria alone; a second makes them pass and is fenced out of the
test file; the unit closes on `just mutation-probe` exit 0 for every annotation, not on green.

Read `AGENTS.md` and `.codex/notes/discipline-digest.md` first; those authorities win if this
summary drifts.

## Invocation posture

This skill is opt-in. Never invoke it automatically from roadmap-continue or ship-pr. Neither
flow calls it and neither may be wired to. Use it only on an operator request, and only for a
unit whose acceptance criteria are concrete enough to test without seeing the implementation.

## Adversary phase

Run this in a fresh, separate codex session, not the one that will implement the unit. Give it
the unit ID, the acceptance criteria verbatim from the plan, the target test path, and the
house test conventions — and nothing about the intended implementation.

The adversary must not be the harness-adversarial-reviewer skill. That skill reviews completed
artifacts and does not author tests; routing this phase through it is a category error. This
phase is an ordinary authoring session under the contract below.

1. Every test must FAIL against the current tree. Red is the deliverable. A test that already
   passes proves nothing and is rewritten or removed.
2. Every assertion derives from an acceptance criterion. No assertion encodes an
   implementation choice the criteria never state.
3. Every test carries exactly one annotation line immediately above it:

   ```text
   # mutation-probe: <file>:<lines>
   ```

   `<file>` is the repo-relative SOURCE file the test claims to pin; `<lines>` is `A-B` or a
   single `A`, naming the lines whose removal must turn that test red. It is never the test's
   own line numbers. A test without an annotation cannot close the unit.
4. Report the exact command that runs the test file and its verbatim failing output.

## Handoff fence

Record the sha256 of the adversary test file at handoff and re-compare it at the completion
gate.

```bash
shasum -a 256 <test-file>
```

`git diff --name-only` is not an adequate fence: an edit-then-revert, or a rewrite into an
equivalent-looking form, leaves an identical clean name list. Only the recorded digest
separates an untouched adversary test from an edited one. This is a recorded-digest
comparison, not a permission-guard deny — nothing blocks the write at the tool layer, so the
gate below is what catches it, and a mismatch is a block rather than something to argue away.

A genuine defect in the tests is a re-open: return to the adversary session, have it rewrite,
and record a new digest. The implementer never edits the file directly.

## Implementer phase

Run in a separate session from the adversary. Change source until the adversary tests pass. Do
not edit the adversary test file, and do not relocate or weaken any of its assertions. Extra
tests belong in other files. Every source change traces to a failing adversary assertion.

## Completion gate

All four must hold before the unit closes.

1. `shasum -a 256 <test-file>` matches the digest recorded at handoff.
2. The adversary test command exits 0.
3. Every `# mutation-probe:` annotation has been run and exited 0:

   ```bash
   just mutation-probe --file F --lines A-B --test "<the command that runs that test>"
   ```

   Exit 0 means the range is pinned. Exit 1 means the test stayed green without those lines —
   fix the test through the adversary session, not the range. Exit 2 is refused or
   indeterminate (dirty target, already-red suite, syntax-breaking range) and is not a pass.
   Exit 3 means the restore did not complete; repair the tree before anything else. The probe
   refuses a target carrying uncommitted changes, so commit the arc's source work first.
4. Paste the verbatim failing output into the PR body, with the handoff digest and the
   per-annotation probe results. No separate red ledger is written on the Claude side;
   `codex_loop.py` already keeps one for this flow, and the pasted output is the witness.

## No Breaker role

No Breaker role exists, deliberately. Merge-gate lens 3 already reasons through a mutation
probe on every code PR, and the completion gate above performs the real one. A third session
would duplicate both at the cost of another full context.

## Verdicts

Each phase ends with exactly one permitted line as its final non-empty line, following the
merge-gate fail-closed convention:

```text
RED-FIRST: PASS
RED-FIRST: BLOCK: <one-sentence reason>
```

Missing, malformed, truncated, or ambiguous output is `RED-FIRST: BLOCK`. A digest mismatch,
an unannotated test, a probe exiting anything other than 0, or a probe that was never run is
each independently a block; passing siblings do not offset it.
