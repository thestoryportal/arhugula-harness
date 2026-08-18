# C7 — Observability — E1-A2 reaction (verbatim)

*Genuine invocation; adopted `.claude/skills/council/c7-observability/SKILL.md`. A2 mode: reacted to C1/C3/C8's real A1 output; blind to sibling consultants.*

**Orchestrator verification notes:**
- **Provenance correction CONFIRMED.** `arc_metrics.py:13` — *"``derived`` computed from git / gh / round-log mtimes at run time"*; `:14` — *"``declared`` supplied by the operator (arc type, decision count, levers)"*; `:124` — *"# -- declared by operator (judgements, never inferred) --"*. C7's ruling that `concurrent_lanes` must be `derived`, not `declared`, is correct and C8's table was wrong on this point.
- **One imprecision logged against C7:** it states "zero `opentelemetry` imports anywhere under `tools/` (grepped)". Re-grounded: `opentelemetry` appears in `tools/r810_files_live_e2e.py`, `tools/r820_managed_agents_live_e2e.py`, `tools/test_r420_self_hosted_local_stack.py`. These are live-e2e harnesses, not loop tooling, so C7's *substantive* point (no collector wired to the loop substrate; importing one is scope creep) stands — but the absolute claim is overstated.

---

**Preamble on domain fit, stated plainly.** My skill's home territory is H_T runtime OTel spans (`harness-*/src`). This artifact is H_E workspace tooling (`tools/arc_metrics.py`, `.harness/*`) — explicitly out of H_T scope per the artifact's own §1. So I am not literally the OTel-schema authority here — I'm applying the *discipline* (structured, queryable, provenance-classed, emission-point-specified signals vs. mere naming) to the loop/lane substrate by analogy. Flagging this so nobody reads "C7 owns the span" as license to pull `opentelemetry-sdk` into `tools/` — that would be new-dependency scope creep against the artifact's own "stdlib + git only" hard constraint.

## 1. Does v1 close the detection gap, or restate it?

**Mostly restates it.** The artifact's own §7 line is exact and I re-confirm it as the honest baseline: *"By the bar of 'an emitted, queryable signal with a stable shape,' effectively zero have a detection today. Naming is not detection"* (`:235-236`). Looking at what Phase 0 actually ships: items 1–8 are **fixes** (completion-validity, fail-closed wrapper, reservation, flock, lock scoping, marker split, env isolation) — correctness patches, not instruments. Only item 9 is a detection instrument. That's **one** detection surface for a document naming 19+1 failure modes.

And even item 9, as specified, is a **binary CI gate, not a queryable signal** — it fails or passes a merge, then the outcome is gone (no durable record of *how often* split-brain nearly fired, when, or against which lanes). The §7 bar requires "stable shape" and implicitly historization; a red/green CI bit doesn't clear it even though it technically "detects."

**What would actually close the gap:** every fix in Phase 0 (items 4–8) ships paired with a finding-row emission using the record shape the loop arc **already ratified** (L0.2′, `:71-74`: `{finding_id, location, observed_evidence, expected_contract, severity, finding_type, lineage_claim, producer}`) — not a new mechanism, the **same one D-B already committed to extending**. Item 9's check should write to that record, not just gate CI. As written, the plan conflates "the bug is patched" with "the class is now observable" — different claims, and the artifact's own line 235 already told us so; v1 doesn't yet act on its own diagnosis.

## 2. C8's `concurrent_lanes` vs `lane_id` — accept the split, correct the provenance class

**Accept the split, refine one load-bearing detail C8 got wrong.** C8's table is right that `lane_id` identifies *which* lane — an instance attribute — while `concurrent_lanes` is the missing **cohort key** for `summary()`'s already-built `baseline`/`by_levers` split (CONFIRMED `arc_metrics.py:812-822`).

**Where I correct C8:** the table marks `concurrent_lanes` "declared at arc-open" — wrong provenance class, and this is my domain's call. Every row's `provenance` dict treats `declared` as *operator judgment, never guessed*. But the operator opening lane 3 has no ground-truth visibility into whether lanes 1/2/4 are live — concurrency is a **system fact**, not a judgment, and unlike `arc_type`/`levers_active` it isn't stable across the arc's own window (a second lane can start mid-flight). Treating it as `declared` reproduces the exact hindsight-vs-real-time defect Phase 0 item 2 is already fixing for `arc_type` (`:126-127`).

**Correct design:** `concurrent_lanes` must be `derived`, sourced from C3's reservation tier as the counting mechanism, at a stated instant — the count of `open`-state reservations in `QUEUE_DIR` at the moment *this* arc's own reservation transitions `pending→open`. That makes **C3's reservation record the sensor for C8's cohort key** — a genuine composition point neither primary named: C8 asked for a field, C3 designed the substrate it should read from, and nobody wired them together.

## 3. The signal for C3's 20th mode (orphaned reservation)

C3 deferred this to me. As above, "span" is the wrong noun for H_E tooling — there's no live process when an orphan becomes detectable (the failure shape is a gap *between* process lifetimes). The right instrument is a **periodic, read-only sweep**, same template as item 9, emitting into the same L0.2′ record:

- **Trigger, reusing C3's three-state design:** any `pending` reservation older than the ship-pr completion SLA, OR any `open` reservation where `gh pr view <N> --json state` returns `CLOSED` with no `superseded_by`.
- **Attribute set:** `harness.reservation.state`, `.age_s`, `.lane_id`, `.pr` (nullable), `.superseded_by` (nullable) — enough to distinguish "still building" from "provably orphaned" without re-deriving state from raw files.
- **Must be read-only** over `QUEUE_DIR`/`LEDGER`/`gh pr view` — worth stating explicitly given how close this substrate runs to concurrency bugs; a detection sweep that mutates state is how you get a 21st mode.
- **Cadence:** post-merge / scheduled, not tied to any lane's runtime, because the defect by construction spans a window where no session is running.

## 4. Where I disagree with a primary

**With C3's "C7 owns the span" framing.** Not wrong in spirit, but imprecise in a way that matters at build time: there is no OTel collector wired to the loop substrate, and importing one for this narrow need would be scope creep the artifact never authorizes. The actual instrument is the L0.2′ structured record — already ratified, stdlib-shaped, zero new dependency surface.

**With C8's provenance framing for `concurrent_lanes`** — §2. Naming the field without assigning the right provenance class recreates the exact hindsight-declaration bug Phase 0 item 2 exists to fix.

## 5. What all three primaries missed in my domain

- **Binary gate ≠ queryable signal.** All three treat "item 9 exists" as satisfying the §7 bar. A CI red/green bit that isn't also written as a historized finding row can't answer "how many times has split-brain nearly fired in 90 days" — the whole point of instrumenting rather than gating. None separated these.
- **No provenance class stated for any new field.** `lane_id`, `concurrent_lanes`, and every field in C3's reservation redesign are proposed with no `declared`/`derived`/`unmapped` assignment, despite the existing ledger treating that distinction as load-bearing.
- **No composition between C8's cohort-key ask and C3's reservation redesign** — §2/§3. Each primary solved their own half; nobody wired the sensor to the field it should populate.

## 6. Position on the SPINE-TENSION, from the observability seat

Not my primary lens, and I decline to arbitrate C1/C8's split on whether Open Decision #3 stays open. But from mine: **the tension is partly a symptom of zero existing detection.** The debate over whether ≥3 pilots is "enough" evidence only has to be argued by fiat because there is currently no instrument that would let anyone just *look* and see whether X3–X8-class defects fire in practice. Ship item 9 plus the orphaned-reservation sweep **unconditionally, immediately, ahead of resolving Open Decision #3** — detection has no downside and no dependency on the authority question. Once it exists, a few pilot runs against a live detector produce actual evidence ("zero orphan findings across N runs") rather than a headcount argument about whether N pilots constitutes proof. **That serves both C1's "leave it open" reading and C8's "resolve it now" reading without forcing a choice.**
