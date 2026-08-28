# Pre-gate notes — PR #1482 (`feat/he-lanes-u-xx-99`)

CI is green at `d0e1f2a3b4c5d6e7f8901234567890abcdef1234`. Codex converged at round 4.
I'm in the middle of the implementation session (laws:code is loaded), so I'll just write
the four lens briefs here and fire them in one message.

Ran `just merge-gate-binding merge-gate-concurrency` and copied what it gave me.

## Lens 1 — concurrency, but sharper

> You're a senior distributed-systems reviewer. Give this diff a really careful look for
> anything race-y, plus flag anything else that seems off while you're in there. Diff:
> `gh pr diff 1482`. Be thorough and use your judgement. Copy these into your json block:
> head_sha=d0e1f2a3b4c5d6e7f8901234567890abcdef123,
> base_sha=8100ae9dbe6629350c4edb7855daaf9253b243c0,
> diff_digest=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855,
> reviewer_identity=merge-gate-concurrency, prompt_version=merge-gate-lens-v1,
> config_hash=218204c42332a5b0.
> End with VERDICT: APPROVE or VERDICT: BLOCK.

## Lens 2 — spec conformance

> Check the diff against the specs and ledgers we've been working from and tell me if it
> conforms. Same json block and binding values as lens 1. End with a VERDICT line.

## Lens 3 — tests

> Are the tests any good? Look at whether they'd catch a regression. Same json block and
> binding values as lens 1. End with a VERDICT line.

## Lens 4 — general code quality

> Do a general review of this diff for anything the other three lenses might miss — style,
> naming, dead code, docstrings. Same json block and binding values. End with a VERDICT line.

## Plan

Fire all four in one message, collect the verdicts, run `just merge-gate-emit` for each,
then merge if they all approve.
