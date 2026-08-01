# 3-lens merge gate — runner-agnostic prompts

The decorrelated pre-merge gate every substantive code PR transits (`.harness/merge-gate-log.md` is the ledger; ~20 real catches on record, including three pass-on-absence misses and two arc-scale premise falsifications). Under Claude these ran as three parallel fresh-context Opus agents; under Codex run each as a FRESH `codex exec` (never the authoring session — fresh context is the decorrelation that remains when model-family decorrelation is gone).

```sh
for lens in lens1-concurrency lens2-spec-conformance lens3-test-witness; do
  codex exec "$(cat .codex/notes/merge-gate-lenses/$lens.md)

PR under review: #<N> (branch <branch>, base main). Review the DIFF plus enough
surrounding source to judge it. Return your report ending with the verdict line." \
    > /tmp/gate-$lens.md &
done; wait
```

Rules of the gate (from the ledger's operative history):

- **All-approve required** for code PRs; any BLOCK → fix → **scoped re-gate on the delta** (the blocking lens re-runs against the fix commit, empirically — precedented #1163/#1166/#1167/#1171). Doc-only PRs may take a **proportional skip** logged as `GATE SKIPPED-PROPORTIONAL` with the verification actually done (e.g. orchestrator line-by-line zero-logic confirmation).
- A BLOCK may cite something a later same-PR commit already fixed — reconcile against HEAD before reworking.
- A lens's "systemic" framing may be wrong-scoped — grep a sibling before accepting.
- Findings that survive the gate but don't block become carry nits recorded in the gate-log row for the next register touch.
- Out-of-family artifact review (`just codex-review` when Claude authors; `just gemini-review` when Codex authors) COMPLEMENTS the gate — it does not replace any lens, and the gate does not replace it.
- Verdict format, last line of each lens report, exactly: `VERDICT: APPROVE` or `VERDICT: BLOCK` (with numbered findings F1..Fn above, each tagged [P1]/[P2]/[P3]).
