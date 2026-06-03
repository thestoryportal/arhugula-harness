---
name: resolve
description: Resolve a reversible, in-repo decision fork autonomously using two decorrelated reviewers — out-of-family Codex (code/diff/design sanity) AND advisor() (full-transcript-aware). Use when loop mode is on and a non-trivial but reversible choice must be made without the operator ("/resolve", "resolve this", "decide and continue", "which approach"). Agreement → auto-decide + record rationale to the loop ledger; disagreement → take the safer/reversible default + log the split for review. Paid-call / secret / destructive / missing-cred forks are NOT resolvable here — they hard-stop and defer. Do NOT use for an irreversible or outward-facing decision.
---

# resolve — Codex+Advisor decision resolver

The autonomy loop's decision substrate (goal #6). When a reversible in-repo fork
appears in loop mode, two **decorrelated** reviewers vote, then the loop proceeds
without a human round-trip — but only for genuinely reversible choices.

## When NOT to resolve (hard-stop → defer, do not auto-decide)

If the decision involves any of these, STOP — log a `DEFERRED-HIL` row to
`.harness/loop_status.md` and continue with other work (the permission guard U-HK-12
already hard-stops the *tool*; this is the *decision-level* mirror):

- a **paid external call** (live LLM inference, metered API),
- **secret / credential** movement,
- a **destructive / irreversible** action (history rewrite, data loss, outward-facing publish),
- a **missing credential / vendor gate**.

These are the operator's to make. Per `[[feedback-background-agent-no-unilateral-paid-calls-or-secret-relocation]]`.

## The resolution flow

```bash
source tools/hooks/lib.sh && source tools/hooks/loop_lib.sh && source tools/hooks/resolve_lib.sh
```

1. **Frame** the decision as a crisp question with the candidate options + the
   reversibility note.
2. **Codex** (out-of-family): `resolve_codex "<question + options + context>"` — runs
   `codex exec` on the ChatGPT subscription ($0). Captures Codex's pick + reasoning.
3. **Advisor** (transcript-aware): call the `advisor()` tool — it sees the full
   session transcript Codex cannot. Capture its pick + reasoning.
4. **Compare:**
   - **Agree** → take that option. `resolve_record "<chosen>" "<one-line why both agreed>"`. Proceed.
   - **Disagree** → take the **safer / more reversible** option (not a coin-flip).
     `resolve_split "<safe default chosen>" "codex=<x> advisor=<y>; took safer"`. Proceed,
     and note the split is in the ledger for the operator's later review.
5. **Continue** the roadmap arc.

## Notes

- Decorrelation is the value: Codex (no transcript, fresh eyes on the artifact) +
  advisor (full context) catch different failure modes. `[[hooks-codex-pilots-decorrelation-validated]]`.
- Every resolution leaves an audit row (`RESOLVE` or `RESOLVE-SPLIT`) so an unattended
  run is fully reviewable afterward.
- This skill decides; it does not bypass the permission guard — a tool the decision
  authorizes still passes through U-HK-12.
