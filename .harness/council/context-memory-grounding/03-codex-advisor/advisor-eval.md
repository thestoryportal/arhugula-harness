# advisor() (transcript-aware) evaluation — Stage 3

*The advisor is in-family with the Claude council (its own caveat): concurrence = weak evidence (correlated blind spots); Codex is the genuinely decorrelated voice. Captured verbatim from the Stage-3 advisor() call (full-transcript-aware).*

---

**Calibration (advisor's own framing):** "I'm Claude — in-family with the council. My concurrence is weak evidence (correlated blind spots), so Codex is your only genuinely decorrelated voice in Stage 3. Weight its disagreements heavily; if it merely concurs, log that as 'no new signal,' not 'validated.'" The cross-cutting catch and the not-git-versioned finding earned their keep. Three things the council + adversarial both missed:

**1. (Blocks) The load-bearing justification is a proxy chain that never reaches the operator's actual pain.** The pain is *drift during coding sessions*. The PLAN centers the *cache-detonation cost* mechanism — but C7 already established cache-cost is unobservable in the dev loop, so it fell back to the git-edit-cadence proxy (60/60 commits). Chain: edit-cadence (measurable) → cache-cost (unmeasurable here) → drift (never connected). A 40KB prefix still rots in the middle. The plan is rich on what to *evict* (cost) and thin on what to *keep and how to position it* (drift). **Tag each MVP item cost / drift / governance, and make "the retained ~40KB is the right, attention-positioned content" a first-class WS — not a byproduct of eviction.**

**2. (Blocks) Nothing validates that this reduces drift, or even cost.** "byte-budget ≤ cap" is a proxy, not an outcome. The `[[use-the-product-probe-pattern]]` is the fix: the PLAN must specify a before/after **real coding-session probe** (slimmed vs current CLAUDE.md — does drift/cost measurably improve without losing needed context?). Otherwise "success" is undefined and this is mechanism-reasoning, not evidence.

**3. (Pressure-test) Does "X" (the FM-H race) belong in the MVP at all?** The council elevated consequence to HIGH because the memory store isn't git-versioned → "lost-update unrecoverable." But memory entries are regenerable *hints*, not source of truth — incidence unconfirmed *and* consequence arguably low for a solo dev. This looks like AR-5's proportionality lapse recurring on a finding C3/C9 own and are invested in. (The MEMORY.md over-cap problem is real — that's WS-3 retention; the cross-worktree *race* is the speculative part.) Consider dropping "X" to detect-only.
> **NOTE — superseded by the advisor↔Codex split:** Codex DISAGREED here (its CA-4 / concern #5): detect-only is insufficient because the rollback gap is real *regardless* of races — build minimal recoverability (snapshot/version the store) now; defer only the locking. Resolution adopted: **minimal-recoverability-now in MVP; serialization/locking trigger-gated.**

**Process (doesn't block — right-size):** ~18 agents / ~4M tokens in, DESIGN.md unwritten, 3 stages left, already reconciled-to-zero. Set the Stage-3 bar: **re-run 3b + the Stage-4 gate at full fan-out only if Codex surfaces a plan-changing finding.** If Codex concurs, collapse 3b to a one-paragraph accept and Stage 4 to a confirmation. AR-5 applies to the *process*, not just the plan: a 25-agent loop to de-bloat a solo-dev harness is the irony to avoid.

**Tactical:** point Codex at the single self-contained `round2-reconciled.md` (§C + §D), not the whole tree.
