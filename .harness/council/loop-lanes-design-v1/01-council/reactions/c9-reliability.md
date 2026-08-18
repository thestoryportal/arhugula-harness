# C9 — Reliability & Recovery — E1-A2 reaction (verbatim)

*Genuine invocation; adopted `.claude/skills/council/c9-reliability-recovery/SKILL.md`. A2 mode: reacted to C1/C3/C8's real A1 output; blind to sibling consultants.*

**Orchestrator verification note:** C9's §4 claim was independently re-grounded at HEAD — `rg -c flock tools/arc_metrics.py` → **0**; `arc_metrics.py:677` *"no lock is needed to say so"*; `:719` *"Same structural fix as the queue itself -- no lock required."* **CONFIRMED.**

---

## 1. Answer to C1 (T-perm-3)

C1, you're right that the artifact states the fix (flock, PR-tagged reservation) without separating the slot's state machine from staleness detection, and right to route it to me rather than absorb it. Here's the mechanism — and it rejects the framing your question assumes.

**"Backoff/heartbeat" is the wrong model for this slot.** My Pillar 1 (full-jitter retry) and Pillar 4 (breaker half-open) both presuppose a *live process periodically renewing or re-attempting* something — that's what a heartbeat or a backoff curve is *for*. But per C3's grounding (§2 of their contribution), the reserving process's PID exits when the Claude Code session ends — typically minutes after `ship-pr` opens the PR — while the reservation must survive PR review, which is hours. There is no heartbeat source to design a curve around. Applying Pillar 1/4 vocabulary here would be FM-A (discipline-vs-surface leak in reverse: importing a mechanism shaped for the wrong failure surface).

**What actually detects staleness — three tiers, event-driven not time-driven where possible:**

| Reservation state | Staleness detector | "Dead" condition | Action |
|---|---|---|---|
| `pending` (no PR yet) | Wall-clock age only, checked opportunistically | Age > SLA (proposed default: reuse no new constant — bound it to the `queue_capture`→`ship-pr` window, which today has no stated ceiling; I'd default this low, e.g. 30 min, since "drained, not yet PR'd" is a single-session action, not a review-latency window) | Silent reclaim, no HITL — matches C3 §2's "provably orphaned... reclaimable by anyone without a liveness check" |
| `open`, `gh pr view` returns MERGED or CLOSED+`superseded_by` | **Ground truth, not elapsed time** — polled, not aged | Instant on observation | Release/reclaim immediately — this isn't a timing constant at all, it's an event |
| `open`, PR genuinely still open (or CLOSED-unmerged with no `superseded_by`) | Wall-clock age of the `open` state itself | Age > threshold | **Warn via existing HITL queue, never auto-reclaim** — see disagreement below |

For the third row: `gh pr view` can't distinguish "taking a long time" from "abandoned" — both look identical on disk (this is C3's own point, restated one level down: swapping pid-liveness for gh-state-liveness doesn't remove the ambiguous middle, it moves it). Stealing a live in-review PR's reservation is the same hazard C3 flagged with naive pid reuse, just relocated. So this case gets a timing constant, but it gates an **escalation**, not a reclaim: route it through the *already-ratified* L0.1 HITL queue (`HARNESS-LOOP-AND-LANES-DESIGN-v1.md:125`, TTL 24h) rather than inventing a second queue — composes with D-B (extend, don't build new) and with your own §3 point about no stated ceiling on multi-lane HITL fan-in. Propose reusing that same 24h TTL rather than minting a fourth timing constant.

**Where "dead" fires before reclaim**: only on positive ground-truth evidence (MERGED / CLOSED+pointer) or a bounded, cheap, no-liveness-needed age window (`pending` only). Never on absence-of-signal — `gh` unreachable resolves to "leave untouched" (the design doc already states this for the claim step at line 138; see §3 below, this needs to extend explicitly to the sweep too).

## 2. Ruling for C3

**You asked me to co-own item 4's timing constants — yes, and the shape is the three-row table above.** I agree with your core architectural call: ground-truth staleness via `gh pr view`, not process liveness, and pid/host demoted out of the state-transition logic.

**One tightening where I'd push past what you wrote.** You said pid/host demote to "provenance only." I'd go further: they must be **fully inert to the mechanism** — never consulted even as a cheap pre-filter ("if pid is alive, skip the `gh` check"). That shortcut is tempting precisely because it's cheap, and it's exactly wrong twice over: a still-alive pid proves nothing (a session can sit idle for hours while review continues elsewhere — the pid isn't doing anything load-bearing to the reservation), and a dead pid proves nothing either (the session legitimately ended the moment it handed off to review, which is the *expected*, not exceptional, path). Any implementer given "provenance only" plus a working `_claim_owner_is_dead()`-style helper already in the file (`tools/arc_metrics.py:584-598`) will be tempted to reuse it as an optimization. It should not be reachable from the state-transition code path at all — display-only, logged at the moment of debugging a stuck queue, never read by the sweep.

**On the constants themselves, concurring with your severity read**: the `pending`-state bound should be small (single-digit minutes to low tens of minutes — a solo action, not a review window) precisely because a large `pending` bound gives X4-shaped duplicate-append exposure more time to fire, and your own §2 already establishes duplicate-append is the primary lanes hazard. The `open`-stuck-warn threshold is a genuine operator-tunable (I'd anchor it to the existing 24h HITL TTL rather than mint new).

## 3. Answer to C8 (item 14)

**Yes, a collision must feed a policy — conditionally, and it's an extension of Pillar 7, not a new mechanism, but the extension is non-trivial.**

Pillar 7's local-first trinity (per-process retry coordinator + Retry-After honor + full jitter) was designed for one process making concurrent model-inference calls. Item 14 is a different topology: **4 separate processes** (one per lane worktree) hitting the **same single-identity subscription login** — `codex-review` (`justfile:591`, `_require-codex-subscription`) and `gemini-review` (`justfile:607`, `_require-antigravity`) are both subscription-auth, one identity per machine. A *per-process* coordinator, taken literally, doesn't see across lanes — each lane's in-memory queue is blind to the other three. So "per-process" under-covers this hazard; the coordinator needs to be **cross-process, collocated at `QUEUE_DIR`** (C3's Tier-1 substrate, reusing the house `fcntl.flock(LOCK_EX | LOCK_NB)` pattern already proven at `tools/mutation_probe.py:502` and `tools/hooks/lib.sh:209,336` — refuse-don't-wait, not block-and-wait, matching the codebase's existing lock discipline).

**Routing, conditioned on the probe's own result** (this is the missing decision rule, matching your §1 finding about O1):
- Probe finds collision at 2 or 4 concurrent → that observation is `rate_limit_storm_detected` (Pillar 7c), scoped to the reviewer-CLI surface instead of the inference surface; enters the existing `rate_limit_storm` degradation mode (Pillar 6 table) with the same exit condition (signals clear for `degradation_exit_window_ms`). New scope, not a new mode.
- Probe finds no collision at either count → report only, no serialization built. Don't build the cross-process lock speculatively against a probe that came back green — that would violate Phase 2's own "only against named, repeated friction" gate (`:167`).

## 4. Where I disagree, stated plainly

- **With the artifact's item 5, not with any one primary** (none of the three flagged this — see §5): "flock across the full claim lifetime... closes X5" proposes introducing `fcntl` advisory locking into a file whose entire design deliberately avoids it. `drain()`'s own docstring: *"no lock is needed to say so"* (queue drain) and *"Same structural fix as the queue itself -- no lock required"* (claim). `publish_exclusive`'s docstring frames atomic hard-link as the reason a lock isn't needed. Grepping `tools/arc_metrics.py` for `flock` returns zero matches — every other flock use in this codebase (`tools/mutation_probe.py:502`, `tools/hooks/lib.sh:209,336`, `tools/hooks/subagent-validate.sh:106`, `tools/hooks/loop-gc.sh:276`) is a *different* subsystem. Landing flock here is a mechanism-family change the artifact doesn't call out as one. Before adopting it, I'd want the X5 ABA branch's actual fix scoped as a targeted hardening of the `os.replace(taken, path)` calls in `drain()`'s exception branches (check-before-replace, or accept that a queue-file restore is idempotent last-write-wins) — consistent with the rest of the file, rather than layering a second locking discipline on top of a design that earned its correctness specifically by not needing one.
- **With C1's framing of "backoff/heartbeat"** (§1 above) — not wrong to ask, but the answer isn't a curve, it's a ground-truth poll plus a bounded age check, and that distinction changes what gets built (no lease-renewal thread).

## 5. What all three primaries missed in my domain

1. **The flock-vs-lockless mechanism-family clash** (§4) — a reliability-mechanism-choice question, squarely C9's, and none of C1/C3/C8 flagged that item 5 contradicts the file's own stated design philosophy.
2. **The staleness *sweep* needs the same "unreachable → leave untouched" rule the artifact already states for the *claim* step.** Line 138 covers `gh` unreachability at reservation-creation time. Nobody stated it extends to the later staleness poll — and an implementer reading only "poll `gh pr view` for staleness" could reasonably default an unreachable `gh` toward "treat as stale" (a read failure feels safe to ignore) which is exactly backwards and reopens the ABA hazard C3 is closing. This needs to be one rule stated once, not assumed to transfer.
3. **Sweep placement.** Nobody names *where* the reservation-staleness check runs. I'd piggyback it on the existing `_recover_dead_claims()` call site inside `drain()` (`tools/arc_metrics.py`, called before `read_queue()`) — the identical "opportunistic sweep on the next arc's drain" pattern already established, composing with L-2 (no daemon) and D-B (extend, don't build). Phase 0 item 9's CI split-brain check is the complementary backstop, not a substitute.

## 6. Position on the SPINE-TENSION (evidence-gate ⊥ operator-mandate), reliability seat

I concur with the convergence C1/C3/C8 independently reach — Phase 0 is unconditional, not gated by the pilot-count dispute — but from a distinct angle none of the three used: **retry/breaker/coordinator mechanisms amplify a race, they don't insulate against one.** Every one of my seven pillars is stateful and designed to *retry harder* under transient failure. Layering Phase 2's mechanized reliability machinery (item 15) on top of an unfixed X4/X5 doesn't add safety — it adds more concurrent, automated retriers hammering the same racy substrate that a human triggers only occasionally today. That's a reliability-domain argument for "fix Phase 0 first" independent of C1's legibility argument, C3's durability-floor argument, and C8's eval-instrument-conflation argument — worth stating as a fourth, convergent line of reasoning rather than assuming the other three already cover it.

On the authority question (does the ≥3-pilot bar gate a top-down N=4 mandate) — that's C1/C8's call, not mine (per my skill's "not a tradeoff-resolver" boundary), and I defer. What I'll flag: whatever that question resolves to, the §1–§2 staleness design above is itself a Phase 0 dependency — AC#2 probe (b) exercises exactly the reservation this design makes safe — so it lands before any pilot run, including a first top-down-mandated one, regardless of how the authority question is answered.
