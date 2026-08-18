# C3 — State / Memory / Persistence — E1-A1 contribution (verbatim)

*Genuine invocation; adopted `.claude/skills/council/c3-state-memory-persistence/SKILL.md`. A1 mode: independent, blind to sibling primaries.*

---

**Co-primary scan (run per skill discipline).** This topic touches C9 (reclaim/retry posture on the reservation) and C1 (the commit-trigger for reservation state transitions) — flagged inline below, not absorbed. Proceeding as C3-primary on the durability substrate itself, which is unambiguously mine.

## 1. Position on the SPINE-TENSION

**The tension is a false dichotomy for the slice I own, and I resolve it decisively: build Phase 0 now, unconditionally, regardless of how the pilot-count dispute resolves.**

Grounded in code, not the lanes narrative: X4's mechanism (CONFIRMED, `tools/arc_metrics.py:44-45,551-581,697,408-409`) requires only that two *different worktrees* drain the same queue with a PR-merge-latency gap between them. `committed_arc_ids()` (`:551-581`) checks `MERGED_REF`; `local` (`:697`) reads only the calling worktree's own `LEDGER` file; `append()`'s duplicate guard (`:408-409`) reads that same per-worktree file. None of the three sees a row appended-but-uncommitted in a *sibling* worktree. This is already exploitable at **N=2**, which is the already-shipped `two-lane` recipe (`.claude/skills/two-lane/SKILL.md:8`, CONFIRMED: *"Two arcs can be built concurrently. They cannot be landed concurrently"*) — not gated behind any 4-lane authorization question at all.

So the evidence-gate (≥3 pilots, O1) properly applies to Phase 1/2 **machinery** — widening the lease-file protocol, mechanizing defect classes, the lane-count policy itself. It does *not* apply to Phase 0 items 4–9, and the artifact already structures it that way (§5 heading: *"Phase 0 — correctness. Ungated by lane count."*). My domain evidence sharpens why that structure is correct rather than a stall tactic: Phase 0 isn't "evidence before authorizing 4," it's "the durability floor beneath any N≥2," and the floor is already cracked today. Deferring *machinery* honors the mandate; deferring *Phase 0* would park it, because a 4-lane rollout on an unfixed split-brain ledger doesn't produce "4 lanes, slower than hoped" — it produces silently corrupted state (lost arc-metrics rows, a `KEPT QUEUED` print that's actively false per X5/E9). The artifact doesn't make that mistake. Operator open-decision #3 ("does the ≥3-pilot gate apply to a top-down N=4 mandate") is real and outside my authority, but it should not be read as blocking Phase 0 — nothing in Phase 0 depends on its answer.

## 2. Ruling on T3 — does the reservation inherit the hazard?

**Yes, as specified it inherits the hazard, and in one respect worse than X4: X4 produces a recoverable duplicate; the reservation as written can produce a permanent, silent orphan with no sweep to find it.**

Three concrete failure paths, each the same *shape* as a C3 durability defect (a marker written by one process lifetime, consulted by a later one, across an unbounded latency gap):

- **Crash between drain and PR creation** leaves `pr: null` forever. This is a two-phase write across a latency boundary — identical shape to X4's "row exists, merge hasn't happened yet" window, just for a different fact.
- **Abandon-and-rebase** (`.claude/skills/two-lane/SKILL.md` "On merge conflict — abandon and rebase", CONFIRMED) closes the original PR unmerged and opens a *new* branch. If the reservation is keyed on `branch` as fallback, the old key is now permanently dead and nothing in the two-lane recipe's own text writes a forward-pointer — it says explicitly *"leave the branch in place"* (operator-gated deletion). A reader consulting the reservation later has no path from the dead branch to the live one.
- **`pid`/`host` as liveness for an hours-long reservation is a tier mismatch.** `_claim_owner_is_dead()` (`arc_metrics.py:584-598`, CONFIRMED) is correct for the *seconds-to-minutes* claim window it currently guards — a drain call. Reused naively for a reservation that spans PR review (hours), it breaks in the dangerous direction: the reserving session's PID exits the moment the operator's Claude Code session ends, long before the PR itself is resolved, so a strict reuse of this liveness check would read a live, in-review PR's reservation as "owner dead" and let a second lane steal it.

**What closes it — concrete state design, C3 commitments:**

- **C3 assigns durability tier 1 (filesystem)** for the reservation, collocated with `QUEUE_DIR` — reusing the exact substrate and atomic-publish primitive (`publish_exclusive`, `os.link`, `arc_metrics.py:516-538`, CONFIRMED) already proven for the `.taken`/`.json` claim mechanism. Do not invent a new file format or lock.
- **Replace the nullable `pr` field with a three-state enum**: `pending` (no PR yet) → `open` (`pr: N`, verifiable against live state) → `terminal` (`merged` | `abandoned`, carrying a mandatory `superseded_by: <branch>` when abandoned). A nullable `pr` conflates "in progress" with "orphaned forever" — the exact illegal-state-representable gap that produced X4's ambiguity in the first place.
- **C3 specifies concurrent-write semantics for the reservation tier: single-writer-per-record via atomic rename/replace on every state transition**, tombstoning (not deleting) on release for one sweep cycle, so a concurrent reader never hits a bare, un-try/excepted `FileNotFoundError` mid-transition — the precise defect class E9 found in `_claim_arc`'s ABA path (`drain():742-757`, uncaught `os.replace` at `:754` when a peer's cleanup wins the race, CONFIRMED against the settled evidence record).
- **C3 specifies rollback/staleness boundary at ground truth, not process liveness.** `pending` reservations older than the ship-pr completion SLA are provably orphaned (bounded, cheap latency) and reclaimable by anyone without a liveness check. `open` reservations are judged by `gh pr view <N> --json state` — MERGED or CLOSED both release; CLOSED-unmerged without a `superseded_by` is itself a detectable finding, not a silent leak. `pid`/`host` demote to **provenance only** (who reserved it, for a human debugging a stuck queue) — never a program-consulted truth condition, matching how `arc_type`/`decision_count` are already marked `declared` rather than measured (`arc_metrics.py:382-387`).
- **C3 specifies pruning policy for terminal reservations**: age-based, same axis as Tier-5 default, with a grace window past the merge event before deletion so a duplicate-detection sweep has somewhere to look.

## 3. What's WRONG in the artifact from my domain

- **Phase 0 item 4 names fields, not semantics.** No stated durability tier, no state-transition contract, no concurrent-write contract for the reservation file itself — only for the ledger it's meant to protect. Against my own self-audit criteria this is FM-C (silent tier) + FM-D (silent cadence) + FM-H (silent concurrent-write semantics) on a load-bearing new piece of state.
- **Item 5's "flock … closes X5's exception branch" needs a scope caveat, or it will be misread as closing more than it does.** The artifact's own §4 text says it correctly for X4 — *"flock dies with the process; this race spans two process lifetimes and a PR merge"* — but doesn't carry that caveat forward to item 5's claim about X5. flock closes only the *same-process* retry race inside `_claim_arc`; it cannot close anything that crosses a drain→merge boundary, which is exactly the shape the reservation (item 4) exists to handle. As written, a reader could conclude flock finishes the job on X5; it finishes only the in-process half.
- **Tier mismatch risk if the reservation is implemented as an append to the existing JSONL pattern.** The reservation needs *mutable* state transitions (pending→open→terminal); the ledger's append-only JSONL shape (rightly kept per L-5's sqlite rejection) is the wrong template for it. The existing `.taken`/`.json` rename-based state machine is the correct template and should be named as such.

## 4. What's MISSING

- No CoALA/tier assignment stated for the reservation record (should be named explicitly: Tier 1, `QUEUE_DIR`-adjacent).
- No pruning/GC policy for orphaned `pending` or abandoned `open` reservations — reservation-bloat is the ledger-bloat failure mode's twin and isn't named anywhere in §7's 19 modes.
- No detection for "orphaned reservation" in the 19-failure-mode table — this design *introduces* a 20th mode (or is a variant of the listed "stale lock") and should get the same cheap-CI-sweep treatment E43 proposed for split-brain ledger: any `pending` older than SLA, or `open` with `gh pr view` CLOSED-unmerged and no `superseded_by`, is a finding.
- No recovery-flow statement for a lane resuming after crash mid-reservation — does it re-verify its own `reserved_at`/`pr` against live `gh` state before treating the reservation as still valid, or trust the file blindly?
- No consistency contract between the reservation (item 4) and the arc-metrics queue entry (the existing `_claim` mechanism) it's stated to protect. They're explicitly two independent mechanisms with "different lifetimes" — but nothing states what happens if they go out of sync (e.g., a dead-owner sweep reclaims the queue entry while the reservation still says `open`).

## 5. Tension with another voice

**C9 (reliability/recovery, retry posture).** Item 4's closing clause — *"release on confirmed merge, reclaim on confirmed abandonment"* — bundles a C3 primitive (what's recoverable, the state shape above) with a C9 decision (when to give up and reclaim: the SLA thresholds, whether a stuck `open` reservation warns before reclaim or auto-reclaims, escalation to the existing HITL queue). This is exactly the FM-J boundary the C3 skill names as regression-prone — I'm surfacing it, not resolving the threshold values; C9 should co-own item 4's timing constants.

Secondary, cleaner boundary: **C1** should name the control-flow trigger for the `pending`→`open` transition (does `ship-pr` write `pr: N` at PR-open, or at first-gate-pass?) — C3 owns landing that transition durably once C1 names the event; currently unaddressed either way.

## 6. Verdict

**Not as currently specified.** Two independent blockers:

1. Phase 0 items 4–9 are unbuilt and X3/X4/X5 are live at N=2 today — already flagged by the artifact itself, not new from me.
2. Item 4's reservation, built exactly as written (`{lane_id, branch, pr: null, reserved_at, pid, host}`, two implicit states, pid/host-as-liveness), reintroduces a hazard of the same shape it closes — a seconds-scale liveness primitive misapplied to an hours-scale durability tier. This needs the three-state redesign above before it is safe even at N=2; at N=4 the pairwise lane-interaction surface is 6× N=2's, so an unfixed per-reservation leak compounds combinatorially rather than linearly.

With the T3 fixes applied (three-state enum, ground-truth staleness via `gh pr view` in place of process liveness, reuse of the existing atomic-publish primitive, explicit abandon-time forward-pointer), the design **can** safely support 4 lanes from a persistence-correctness standpoint — this is a scoped, buildable delta on Phase 0 item 4, not a new arc, and it belongs inside Phase 0, not deferred to Phase 2.

**Outside my authority:** lane-count policy itself, reviewer-concurrency/vendor-decorrelation questions, the C9 reclaim-SLA values, Docker/env isolation (C11), and how the detection signal above gets wired into OTel/CI (C7 owns the span; I own that the signal must exist).
