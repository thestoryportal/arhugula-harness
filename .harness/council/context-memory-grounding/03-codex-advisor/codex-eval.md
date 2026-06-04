# Codex (out-of-family) evaluation — Stage 3

*gpt-5.5 via ChatGPT subscription ($0), read-only, decorrelated from the Claude council. Prompted FRESH — not told the advisor's findings. Run `bcclbpk51`.*

---

**VERDICT**

The MVP is directionally sound but not fully proportionate for a solo-developer harness. WS-1 plus a minimal WS-2 index is the real core. G1 is useful if it stays cheap and bypassable. X needs a recovery boundary, but not a full locking regime yet. WS-5 and WS-6/D14 feel less MVP than the plan claims unless there is evidence that runtime budget visibility or recovery hooks are current drift drivers.

**TOP CONCERNS**

1. **Metric substitution:** the council mostly turns “DRIFT” into “byte count.” Smaller context may help, but the plan does not define drift incidents, baseline them, or test whether drift falls after the split.

2. **Claude-reviewing-Claude blind spot:** the process is governance-native. It naturally adds ledgers, gates, hooks, dashboards, reconciliation loops, and “home-of-record” artifacts. That is exactly the kind of context bureaucracy that may have caused the original bloat.

3. **Unverified load-bearing assumption:** it assumes §2 provenance is historical ballast. That is probably true, but only after proving no active rule, hook, grep path, recovery process, or “which artifact is canonical?” decision depends on it.

4. **False confidence from “reconciled-to-zero”:** agreement among same-family reviewers is not evidence of correctness. It can mean shared taste, shared blind spots, and shared over-weighting of formal coherence.

5. **Memory durability is misframed as mostly concurrency:** the confirmed problem is not just races. It is that any bad write/delete to the out-of-worktree memory store lacks rollback. That makes minimal snapshot/versioning load-bearing even if no race is observed.

**WS-RISKS**

**WS-1:** Evicting ~277KB of provenance from `CLAUDE.md` is probably safe and likely the biggest cost/noise win, but only if execution first extracts current invariants into a compact live contract and moves historical/version-chain data to a navigable, git-backed archive/index. Do not rely on “git history somewhere” unless the actual target is versioned.

**WS-4 G1:** A byte-budget `--check` is the right shape, but make it a guardrail, not a religion. It should measure effective loaded context, have an explicit override/waiver path, and avoid forcing unreadable compression. Hard-fail CI is okay after a clean baseline; before that, warning mode is more proportionate.

**X:** For a solo dev, build minimal recoverability now: snapshot/version the memory store, atomic writes, and stale-base detection. Full serialization/locking should stay trigger-gated unless concurrent writes are observed. Detect-only is not enough if detection cannot restore the lost entry.

**MVP-SLICE**

Mostly agree, with changes. Keep WS-1, minimal WS-2, G1, and X recovery in MVP. Move MEMORY.md compaction/retention closer to MVP if MEMORY.md is actually session-loaded or frequently consulted. Defer WS-5 mid-session surface unless cheap. Defer WS-6/D14 unless recovery failure is part of observed drift. The full dashboard, HOOKS.md expansion, G2-G4, and archive asymmetry work can stay deferred.

**DRIFT-CONNECTION**

Weak. The plan strongly reduces byte-count, cost, and provenance pollution. It only indirectly addresses drift. To truly connect, it needs a drift metric: stale-rule use, wrong canonical artifact, forgotten task constraints, memory pollution, bad resumptions, or instruction conflicts before/after WS-1. Without that, this is a context slimming plan, not yet a demonstrated drift-reduction plan.
