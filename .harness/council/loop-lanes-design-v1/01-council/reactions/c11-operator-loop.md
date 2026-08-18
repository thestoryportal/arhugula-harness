# C11 — Operator Loop / Local Deployment — E1-A2 reaction (verbatim)

*Genuine invocation; adopted `.claude/skills/council/c11-operator-loop-local-deployment/SKILL.md`. A2 mode: reacted to C1/C3/C8's real A1 output; blind to sibling consultants.*

**Orchestrator verification notes — both load-bearing claims CONFIRMED at HEAD.**
- `grep -c 'coalesc\|batched'` on the design doc → **1**, and it is line 269 (Open Decision #4's own description). The finding is **recorded, never enacted** — nothing in Phase 0/1/2 operationalizes it.
- The existing exemplar mechanism is real: `_loop_pending_hil_rows()` at `tools/hooks/loop_lib.sh:165`; `loop_pending_hil_summary` / `loop_cap_list` cap logic at `:191-205`.

---

**Co-primary scan run.** This lands on my C1↔C11 seam (placement vs. primitive) and C10↔C11 (escalation surface implementation) but stays clean — I'm answering "what does the operator see," not "when does it fire" or "what conditions trigger it." Proceeding single-voice.

## 1. Ruling on Open Decision #4 — one batched prompt, and it already has a working shape

**One batched prompt. Not N sequential — CLAUDE.md §12.4.1 forecloses that outright** ("Approval fatigue is the failure mode"), and the operator's non-coding/decorrelated-witness posture makes N separate per-lane prompts strictly worse than useless: four near-identical escalations invite rubber-stamping, which is gate-fatigue's actual failure shape, not just its annoyance shape.

**The shape isn't a design question — it's an extension question.** This workspace already runs a batched-HITL mechanism that does almost exactly what's needed, CONFIRMED at `tools/hooks/loop_lib.sh`:

- `loop_log()` (`:77`) / `loop_defer()` (`:93`) append one row per gated item to `.harness/loop_status.md`, never interrupting synchronously.
- `_loop_pending_hil_rows()` (`:165`) reduces by item-id with last-write-wins semantics (a later `RESOLVED-HIL` clears a prior `DEFERRED-HIL` for the same token) — CONFIRMED the same reduction Phase 0 item 7 (`:144-147`) proposes extending toward cross-lane visibility.
- `loop_cap_list()` (`:209`) / `loop_pending_hil_summary()` (`:225`) render the whole pending set as **one line**, capped at 3 items + "(+N more)", surfaced once at the operator's next touch (SessionStart), not per-event.

So: **the batched prompt is not a synchronous interrupt at all — it's an asynchronous, capped, ledger-reduced summary line the operator sees on next touch**, matching my skill's durable-queue posture. Extend it, don't invent a new primitive.

**What's genuinely new, and what I add beyond a straight extension: correlated-cause collapse.** Item 7's reduction is per-item-id (one row per deferred *thing*). A shared reviewer-identity outage tripping `REVIEWER_UNAVAILABLE` on all 4 lanes is 4 *different* item-ids with **one shared cause** — reduced by item-id alone that is still 4 rows, i.e. drip-fed-in-substance even once drip-fed-in-timing is fixed. The rubric needs a second reduction key: when ≥2 `DEFERRED-HIL` rows share a `cause_signature` within a bounded window, collapse to **one** row naming all affected `lane_id`s, with **one** response resolving all:

```
[Escalation HITL — request {request_id}]

4 lanes blocked on the same cause: gemini-review REVIEWER_UNAVAILABLE
(lanes: B-171, B-173, B-175, B-176; started 14:02–14:09 UTC)

Gate pipeline evaluation:
  reviewer-identity: unreachable (auth/outage, not per-diff)
  Final decision: ask (per L0.1 — REVIEWER_UNAVAILABLE is BLOCK-equivalent,
  never APPROVE-able)

Available responses:
  approve — failover reviewer proceeds for all 4 lanes
  reject  — all 4 halt at this gate (permanent fail-class, per-lane)
  respond — operator text returns to all 4 for replanning
```

`edit` is dropped — the operator isn't editing four diffs in one response. TTL: the artifact's proposed 24h (`:125`) for a CI-blocking gate, not my skill's 7-day default — a stale correlated block is actively holding 4 lanes' progress.

## 2. Answer to C8 — hybrid, and the split matters

**The shape ships now; the tuning constants get measured.** Two different things are bundled in C8's framing:

- *Whether* coalescing exists and *what it looks like* (one batched line, cause-signature reduction, restricted response palette) — a structural commitment, not a preference; §12.4.1 settles it as policy independent of any measured count. Waiting on data has a real cost: item 13's ≥3 pilots are the **evidence-gathering run**. If the coalescing shape isn't built before pilots run, the pilots will surface drip-fed-prompt friction **as if it were a lane-count problem**, when it's an unbuilt operator-UX surface — **contaminating the exact signal the pilot bar exists to collect.** So I disagree with "resolve it as data, not preference" as stated: the shape is a precondition FOR clean pilot data, not an output of it.
- *What TTL, what correlation window, whether 3+N-more is still the right cap at 4 lanes* — genuinely C8's `expected_hitl_invocations_per_session` territory; instrument during item 13's pilots exactly as C8 proposes, then tune.

Concretely: land the coalescing mechanism as a Phase 0 / early-Phase-1 item (a small extension of already-working code — L-2's "no coordinator process" ban doesn't apply, this is a ledger-reduction rule), instrument invocation counts during pilots, tune the three parameters from that data.

## 3. Where I disagree with a primary

**C1's placement claim is topologically wrong for this specific defect.** C1 says coalescing sits "at the merge door, since that's the one serialization point all 4 lanes funnel through." True for **landing** (§2's diagram, depth-1 by construction). **Not true for gate escalation.** Each lane's reviewer gate fires inside that lane's own independent build stream, *before* any lane reaches the merge door — the four gates are not synchronized to a shared topological point; they fire whenever each lane happens to run its gate, minutes or hours apart. A shared reviewer-identity outage is a **temporal** correlation (same cause, overlapping window), not a **topological** one. Coalescing "at the merge door" would mean the operator hears about a lane-2 outage only once lane-2 reaches merge — by which point lane-1's identical outage may already have been answered separately, and lane-4 may not have hit its gate at all. **The actual coalescing point is temporal — the operator's next touch**, which `loop_status.md`'s existing SessionStart-summary already implements. C1 correctly recuses the primitive to me, but the placement framing needs correcting, not just deferring.

## 4. What all three primaries missed in my domain

**The finding is recorded, never enacted.** `grep -n "coalesc\|batched"` on the artifact returns exactly **one** hit — line 269, Open Decision #4's own description. Nothing in Phase 0 (1–9), Phase 1 (10–14), or Phase 2 (15–19) operationalizes it, not even as the placeholder C1 itself argued for elsewhere (C1 applies "name a provisional default" to the HITL fan-in ceiling generally but doesn't apply it to its own handoff of #4 to me). And none of C1/C3/C8 noticed the workspace **already has a working, battle-tested exemplar** of exactly this mechanism in `tools/hooks/loop_lib.sh` — each treated it as green-field design when it is substantially an extension. That's the miss only the local-deployment-implementation lens catches: I own "which library, which schema, which existing surface," and the correct answer is **"the one that's already running."**

## 5. Position on the SPINE-TENSION, from the operator seat

C1 and C8 both frame the spine as a *correctness/evidence* question. From the seat I own — what the operator experiences — there's a third precondition neither names: **the pilots (item 13) are also measuring operator experience** (per the two-lane bar's own words: *"a specific, repeated, described friction"*), and that measurement is **invalid if the operator-experience substrate isn't built yet**. Running ≥3 pilots at 4 lanes with X3–X8 fixed but #4 unresolved doesn't just risk a UX complaint — it risks the pilot data being **uninterpretable**: a "recurring pain" signal from repeated drip-fed correlated escalations would look identical to one from genuine lane-count unsafety, and nothing in the current design distinguishes them after the fact.

**My addition to the spine: Phase 0's completeness gate (C1/C3's territory) is necessary but not sufficient for item 13 to produce clean signal — the coalescing shape from §1 is a third, currently-absent precondition, and it belongs in Phase 0's "ungated by lane count" bucket for the same reason X3–X8 do: it is correctness of the *measurement instrument*, not a lane-count-gated nicety.**
