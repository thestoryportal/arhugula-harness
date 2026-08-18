# C1 — Orchestration & Control Architect — E1-A1 contribution (verbatim)

*Genuine invocation; adopted `.claude/skills/council/c1-orchestration/SKILL.md`. A1 mode: independent, blind to sibling primaries.*

---

**Co-primary scan (per SKILL.md §"Activation discipline"):** This topic touches C9 (retry/backoff on stale reservations, flock semantics) and C11 (HITL primitive mechanics for gate-coalescing) at specific sub-points below. I flag those seams explicitly rather than absorbing them; the SPINE-TENSION and T2 questions themselves are core C1 territory (topology sequencing, pattern naming) and I proceed as primary on them.

## 1. Position on the SPINE-TENSION

**C1 reads this as two different questions the artifact currently answers well but states ambiguously as one.**

Question A — *is the 4-lane topology itself deferred?* No. C1 selects **parallelization-by-sectioning** (four independent worktree-isolated sub-agent-boundary workers, each with its own gates/reviewers — `two-lane/SKILL.md:23-24`, CONFIRMED) fanning into a **manager-pattern serial gather** at the merge door (`two-lane/SKILL.md:8`, CONFIRMED: *"Two arcs can be built concurrently. They cannot be landed concurrently"*). This topology is buildable and, per artifact item 13, is literally *run* at 3–4 lanes in Phase 1 — manually, with zero new machinery, exactly mirroring how N=2 already operates today (no spawner, no coordinator process). **The operator's N=4 mandate is honored operationally in Phase 1, not parked.**

Question B — *is Phase 0 (X3–X8) gated by the mandate?* No, and it isn't gated by the evidence-rule either — it's an unconditional precondition. X4 (duplicate-append, zero temporal overlap, `arc_metrics.py:551-581` `committed_arc_ids()` + `:697/706` `local`/`append` guard, all CONFIRMED as per-worktree/per-branch checks that individually pass while the composite races) is *live at N=2 today*. Running 4 lanes on top of an unfixed X4 doesn't honor the mandate — it manufactures the exact corruption the mandate implicitly assumes won't happen. Phase 0 is not "the evidence gate" in the spine-tension's sense; it's correctness debt that predates and is independent of the lane-count question.

Where the artifact is **genuinely unresolved, and correctly says so**: Open Decision #3 (`§9`, line 268) — *does the ≥3-pilot gate (`two-lane/SKILL.md:140-142`, CONFIRMED) bind against a top-down mandate at all* — is left open. C1 flags an internal tension in the document itself: item 13 is written as if it *resolves* the gate ("satisfies... the counterfactual demand with one experiment," line 163) while §9 lists the same question as *still open*. Those can't both be true. **C1's read: item 13 resolves the operational question (4 lanes get run) but does not resolve the authority question (does a self-referential workspace heuristic get to gate a ratified operator mandate at all) — that authority question should stay open for the operator, not be quietly closed by the "one experiment" framing.** This is a decision C1 will not pick unilaterally (per SKILL.md §"What this skill is not" — not a tradeoff-resolver); it should be asked plainly, not implied-answered.

## 2. Position on T2 — "build-parallel/land-serial": honest architecture or redefinition?

**Honest, with one real disclosure gap.** The name states its own shape — sectioning + serial fan-in — and the artifact does its own cost-pre-check correctly for *wall-clock*: "Expected yield: well under 2×, not 4×" (line 53) is exactly the FM-G obligation (surface the ratio, don't let the operator assume linear scaling from lane count).

What's **missing**, and this is a C1 cross-cutting obligation (concern 3, token economy — SKILL.md:171, CONFIRMED cite: *"multi-agent ≈ 15× single-agent tokens"* per research §2.7): the artifact never states the **token/context-cost** dimension of 4 concurrent isolated-context lanes, only wall-clock yield. Each lane is a separate sub-agent-boundary context reloading full governance context independently. The doc is silent on this axis entirely — it should at minimum flag it as a known-but-unquantified cost, the same way it flags "semantic-conflict rate... unmeasured, not zero" (line 162) for the merge-tree question. **This is the one place C1 finds the artifact under-naming what "parallel" costs**, not what it means.

## 3. What's WRONG from C1's domain

- **Reservation lifecycle has no termination criterion for "abandonment."** Item 4 (line 137): *"Release on confirmed merge, reclaim on confirmed abandonment"* — "confirmed abandonment" is never defined (no elapsed-time bound, no liveness signal named). Per C1 self-audit criterion 2 (FM-E), every control-flow slot needs an explicit exit condition; this one doesn't have one yet. This is *C1's* gap to name (the slot must exist and terminate) even though the *mechanism* that detects staleness is C9's (see §5).
- **No stated ceiling on simultaneous HITL escalation.** If L0.1's TTL-24h queue (line 125, CONFIRMED reference) receives correlated escalations from multiple lanes at once (e.g., a shared reviewer-identity outage hits all 4 lanes' `REVIEWER_UNAVAILABLE` in the same window), there's no stated fan-in bound — Open Decision #4 (gate-coalescing) names the *question* but the topology has no default answer even as a placeholder. Per self-audit criterion 4, silence here is FM-F-adjacent; the artifact should at minimum name a provisional default even though the final answer is operator-owned.

## 4. What's MISSING

1. **No handoff-contract vocabulary applied.** The reservation record `{lane_id, branch, pr, reserved_at, pid, host}` (item 4) is a lock record, not a control-transfer contract — it never states what a lane *returns* to signal "ready to merge" versus "still building" in a form the merge-door step consumes. Thin, likely acceptable for a hand-rolled recipe, but C1 flags it as unspecified rather than assuming it's implicit.
2. **Pattern-naming is never made explicit in the artifact itself** (FM-D). The doc *is* sectioning-into-manager-gather; nowhere does it say so. Purely a documentation gap, not a design defect — but per C1's own quality bar this should be named so a future reader doesn't have to re-derive the pattern.
3. **Token-cost disclosure**, per §2 above.

## 5. Named tension with another voice

**C1 ↔ C9 (T-perm-3, permanent).** Item 5 ("flock across the full claim lifetime... closes X5") and the undefined "confirmed abandonment" from §3 both sit exactly on this seam: C1's job is to say a reservation slot exists and has release/reclaim states; C9's job is the liveness-detection mechanics (what backoff, what heartbeat, what counts as "dead" before reclaim fires). The artifact currently states the *fix* (flock, PR-tagged reservation) without separating "the slot's state machine" (C1) from "how staleness is detected" (C9) — worth a co-primary pass before this lands, not a C1-only spec.

**C1 ↔ C11**, secondary. Open Decision #4 (gate-coalescing: batched vs sequential operator prompts) is squarely the C1-placement/C11-primitive seam this skill's boundary table names explicitly (SKILL.md:142, CONFIRMED). C1 can say *where* the coalescing point sits in the topology (at the merge door, since that's the one serialization point all 4 lanes funnel through); C11 owns what the batched prompt actually looks like.

## 6. Verdict on build order (Phase 0 → 1 → 2)

**Correctly sequenced, one sequencing dependency should be made explicit rather than left implicit.** Fixing the substrate a topology depends on before measuring, and measuring before building automation, is the right meta-order — it avoids building Phase 2 fan-out machinery on top of a race-prone Phase 0 reservation layer. The intra-Phase-0 ordering (item 2's `lane_id` pre-registration before items 4–9, which key off it) is already correctly sequenced and explicitly justified (line 130).

The one gap: **item 13's "≥3 manual pilot runs at 3–4 lanes" is the operational vehicle that (per §1) honors the operator's mandate — but the artifact never states that item 13 is conditioned on Phase 0 items 1–9 being fully landed first.** Phase ordering implies it, but doesn't say it. If a pilot run at 4 lanes executes against an unfixed X4/X5, any "recurring pain" or "no pain" signal it produces is contaminated by known bugs, not genuine friction — and the §1 reading ("the mandate is honored via item 13") collapses back into deferral if that gate is silently skipped. **Recommend the artifact state explicitly: item 13 does not fire until Phase 0 items 1–9 are closed.**
